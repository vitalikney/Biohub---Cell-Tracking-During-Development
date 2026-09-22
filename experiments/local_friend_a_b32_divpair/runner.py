"""Resumable B32 division-pair experiment for Friend A.

Stages:
1. Enumerate and label the registered wide orphan pool for every video.
2. Cache a fixed, deterministic train subset of seven-channel crops.
3. Train two embryo-held-out folds with per-epoch checkpoints.
4. Score every candidate out of fold, then run the registered threshold/cap grid.
5. Gate on all 199 videos and on each embryo separately; package a final model only for a winner.

Every expensive unit is either one video or one epoch. ``STOP_REQUESTED`` is
checked between those units and inside full-candidate scoring batches.
"""

from __future__ import annotations

import gc
import hashlib
import json
import math
import os
import random
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np


EXPERIMENT = "local_friend_a_b32_divpair"
CACHE_TAG = "friend_a_b20_exp29"
THRESHOLDS = (0.5, 0.7, 0.9)
CAP_MODES = ("public", "double", "none")
FOLDS = (
    ("train6bba_val44b6", "6bba", "44b6"),
    ("train44b6_val6bba", "44b6", "6bba"),
)


class StopRequested(RuntimeError):
    pass


def truthy(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"", "0", "false", "no", "off"}


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(jsonable(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def atomic_npz(path: Path, *, compressed: bool = True, **arrays: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.stem + ".tmp.npz")
    if compressed:
        np.savez_compressed(temporary, **arrays)
    else:
        np.savez(temporary, **arrays)
    for attempt in range(30):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 29:
                raise
            gc.collect()
            time.sleep(min(0.05 * (attempt + 1), 1.0))


def atomic_torch(path: Path, payload: dict[str, Any]) -> None:
    import torch

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    torch.save(payload, temporary)
    for attempt in range(30):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 29:
                raise
            gc.collect()
            time.sleep(min(0.05 * (attempt + 1), 1.0))


def discover_data_dir(repo_root: Path) -> Path:
    choices: list[Path] = []
    explicit = os.environ.get("BIOHUB_DATA_DIR", "").strip()
    if explicit:
        choices.append(Path(explicit))
    choices.extend(
        [
            repo_root.parent / "train",
            repo_root / "train",
            repo_root / "biohub-cell-tracking-during-development" / "train",
        ]
    )
    for choice in choices:
        if choice.is_dir() and any(choice.glob("*.zarr")):
            return choice.resolve()
    raise FileNotFoundError("Set BIOHUB_DATA_DIR to the directory with 199 .zarr/.geff pairs")


@dataclass
class B32Config:
    repo_root: Path
    data_dir: Path
    output_dir: Path
    b20_cache: Path
    parent_checkpoint: Path
    run_pipeline: bool = True
    max_videos: int = 0
    seed: int = 42
    parent_um: float = 15.0
    sister_min_um: float = 5.0
    sister_max_um: float = 20.0
    deepcenter_threshold: float = 0.20
    epochs: int = 25
    batch_size: int = 32
    score_batch_size: int = 64
    learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    negatives_per_positive: int = 32
    minimum_negatives_per_video: int = 16
    maximum_negatives_per_video: int = 192
    use_amp: bool = True

    @classmethod
    def from_environment(cls, repo_root: Path) -> "B32Config":
        repo_root = Path(repo_root).resolve()
        output = Path(
            os.environ.get(
                "BIOHUB_B32_OUTPUT_DIR",
                repo_root.parent / "outputs" / EXPERIMENT,
            )
        ).resolve()
        b20_cache = Path(
            os.environ.get(
                "BIOHUB_B32_B20_CACHE",
                repo_root.parent / "outputs" / "local_friend_a_b20_divnet" / "cache" / CACHE_TAG,
            )
        ).resolve()
        parent_checkpoint = Path(
            os.environ.get(
                "BIOHUB_B32_DIVNET_CHECKPOINT",
                repo_root / "external" / "giorgosi__biohub-divnet-v2" / "best_overall.pt",
            )
        ).resolve()
        return cls(
            repo_root=repo_root,
            data_dir=discover_data_dir(repo_root),
            output_dir=output,
            b20_cache=b20_cache,
            parent_checkpoint=parent_checkpoint,
            run_pipeline=truthy(os.environ.get("BIOHUB_B32_RUN"), True),
            max_videos=int(os.environ.get("BIOHUB_B32_MAX_VIDEOS", "0")),
            seed=int(os.environ.get("BIOHUB_B32_SEED", "42")),
            epochs=int(os.environ.get("BIOHUB_B32_EPOCHS", "25")),
            batch_size=int(os.environ.get("BIOHUB_B32_BATCH_SIZE", "32")),
            score_batch_size=int(os.environ.get("BIOHUB_B32_SCORE_BATCH_SIZE", "64")),
            learning_rate=float(os.environ.get("BIOHUB_B32_LR", "1e-4")),
            weight_decay=float(os.environ.get("BIOHUB_B32_WEIGHT_DECAY", "1e-4")),
            negatives_per_positive=int(os.environ.get("BIOHUB_B32_NEG_PER_POS", "32")),
            minimum_negatives_per_video=int(os.environ.get("BIOHUB_B32_MIN_NEG_PER_VIDEO", "16")),
            maximum_negatives_per_video=int(os.environ.get("BIOHUB_B32_MAX_NEG_PER_VIDEO", "192")),
            use_amp=truthy(os.environ.get("BIOHUB_B32_AMP"), True),
        )

    @property
    def stop_file(self) -> Path:
        return self.output_dir / "STOP_REQUESTED"

    @property
    def all_stems(self) -> list[str]:
        zarr = {path.name.removesuffix(".zarr") for path in self.data_dir.glob("*.zarr")}
        geff = {path.name.removesuffix(".geff") for path in self.data_dir.glob("*.geff")}
        return sorted(zarr & geff)

    @property
    def stems(self) -> list[str]:
        stems = self.all_stems
        if not self.max_videos:
            return stems
        each = max(1, self.max_videos // 2)
        selected = [stem for stem in stems if stem.startswith("44b6")][:each]
        selected += [stem for stem in stems if stem.startswith("6bba")][:each]
        return sorted(selected[: self.max_videos])

    def serialisable(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in ("repo_root", "data_dir", "output_dir", "b20_cache", "parent_checkpoint"):
            payload[key] = str(payload[key])
        payload["videos"] = len(self.stems)
        payload["full_dataset_videos"] = len(self.all_stems)
        payload["thresholds"] = list(THRESHOLDS)
        payload["cap_modes"] = list(CAP_MODES)
        return payload

    def fingerprint(self) -> str:
        payload = self.serialisable()
        for key in ("run_pipeline", "output_dir"):
            payload.pop(key, None)
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def state_path(cfg: B32Config) -> Path:
    return cfg.output_dir / "state.json"


def load_state(cfg: B32Config) -> dict[str, Any]:
    if not state_path(cfg).is_file():
        return {"version": 1, "fingerprint": cfg.fingerprint(), "status": "new", "stages": {}}
    state = json.loads(state_path(cfg).read_text(encoding="utf-8"))
    if state.get("fingerprint") != cfg.fingerprint():
        raise RuntimeError("B32 recipe changed. Restore settings or select another BIOHUB_B32_OUTPUT_DIR")
    return state


def save_state(cfg: B32Config, state: dict[str, Any]) -> None:
    state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    atomic_json(state_path(cfg), state)


def request_stop(cfg: B32Config) -> Path:
    cfg.stop_file.parent.mkdir(parents=True, exist_ok=True)
    cfg.stop_file.write_text("Stop after the next video/epoch/batch checkpoint.\n", encoding="utf-8")
    return cfg.stop_file


def clear_stop(cfg: B32Config) -> None:
    cfg.stop_file.unlink(missing_ok=True)


def check_stop(cfg: B32Config) -> None:
    if cfg.stop_file.is_file():
        raise StopRequested(f"Stop requested via {cfg.stop_file}")


def install_import_paths(cfg: B32Config) -> None:
    paths = [
        cfg.repo_root,
        cfg.repo_root / "tools",
        cfg.repo_root / "experiments" / "local_friend_b_exp02_public_port",
        cfg.repo_root / "experiments" / EXPERIMENT,
    ]
    for path in paths:
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def candidate_dir(cfg: B32Config) -> Path:
    return cfg.output_dir / "candidates"


def candidate_path(cfg: B32Config, stem: str) -> Path:
    return candidate_dir(cfg) / f"{stem}.npz"


def sample_path(cfg: B32Config, stem: str) -> Path:
    return cfg.output_dir / "train_samples" / f"{stem}.npz"


def stable_seed(seed: int, text: str) -> int:
    digest = hashlib.sha256(f"{seed}:{text}".encode()).digest()
    return int.from_bytes(digest[:8], "little") & 0x7FFFFFFF


def enumerate_candidates(cfg: B32Config, stem: str) -> dict[str, np.ndarray]:
    """Create the registered 15 um orphan pool and honest triple labels."""
    install_import_paths(cfg)
    import networkx as nx
    import divranker
    import pass2_rank_divisions as p2

    nodes, edges, dcs, peak = p2.load_video(cfg.b20_cache, stem)
    original_max = p2.SISTER_MAX
    p2.SISTER_MAX = float(cfg.sister_max_um)
    try:
        raw, _, _ = p2.candidates(nodes, edges, dcs, peak, cfg.parent_um, 0, "add")
    finally:
        p2.SISTER_MAX = original_max
    dc_index = p2.NAMES.index("dc_q")
    kept = [
        item
        for item in raw
        if cfg.sister_min_um <= float(item[4][2]) <= cfg.sister_max_um
        and float(item[4][dc_index]) >= cfg.deepcenter_threshold
    ]

    prediction = nx.DiGraph()
    prediction.add_nodes_from(
        (node_id, {"t": node["t"], "z": node["z"], "y": node["y"], "x": node["x"]})
        for node_id, node in nodes.items()
    )
    prediction.add_edges_from((source, target) for source, target, _ in edges)
    truth = divranker._load_gt(cfg.data_dir / f"{stem}.geff")
    matching = divranker._match_pred_to_gt(prediction, truth, radius=7.0)
    truth_children = {node: set(truth.successors(node)) for node in truth if truth.out_degree(node) >= 2}
    labels = np.zeros(len(kept), dtype=np.uint8)
    gt_parent = np.full(len(kept), -1, dtype=np.int64)
    for index, (parent, child, candidate, _, _) in enumerate(kept):
        matched_parent = matching.get(parent)
        if matched_parent is None or matched_parent not in truth_children:
            continue
        children = truth_children[matched_parent]
        matched_child = matching.get(child)
        matched_candidate = matching.get(candidate)
        if (
            matched_child in children
            and matched_candidate in children
            and matched_child != matched_candidate
        ):
            labels[index] = 1
            gt_parent[index] = int(matched_parent)
    features = (
        np.asarray([item[4] for item in kept], dtype=np.float32)
        if kept
        else np.zeros((0, len(p2.NAMES)), dtype=np.float32)
    )
    return {
        "p": np.asarray([item[0] for item in kept], dtype=np.int64),
        "c": np.asarray([item[1] for item in kept], dtype=np.int64),
        "q": np.asarray([item[2] for item in kept], dtype=np.int64),
        "t": np.asarray([item[3] for item in kept], dtype=np.int16),
        "features": features,
        "label": labels,
        "gt_parent": gt_parent,
        "feature_names": np.asarray(p2.NAMES),
        "gt_divisions": np.asarray([len(truth_children)], dtype=np.int32),
        "recipe_fingerprint": np.asarray([cfg.fingerprint()]),
    }


def candidate_file_valid(cfg: B32Config, path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path, allow_pickle=False) as payload:
            return (
                {"p", "c", "q", "t", "features", "label", "gt_parent", "recipe_fingerprint"}
                <= set(payload.files)
                and str(payload["recipe_fingerprint"][0]) == cfg.fingerprint()
                and len(payload["p"]) == len(payload["label"])
            )
    except Exception:
        return False


def candidate_reach_diagnostics(cfg: B32Config) -> dict[str, Any]:
    """Measure the hard reach ceiling stage by stage without enumerating triples.

    This deliberately uses the same 7 um one-to-one node matching as the labels.
    It separates failures caused by missing detections from the orphan/DeepCenter
    restrictions, so increasing a radius cannot hide an impossible candidate gate.
    """
    install_import_paths(cfg)
    import collections
    import networkx as nx
    import divranker
    import pass2_rank_divisions as p2

    stage_names = (
        "gt_divisions",
        "parent_detected",
        "both_daughters_detected",
        "parent_has_one_child",
        "existing_child_valid",
        "existing_child_is_gt_daughter",
        "other_daughter_node_valid",
        "parent_radius",
        "sister_range",
        "deepcenter_veto",
        "orphan_only",
    )
    counters = {
        "all": collections.Counter(),
        "44b6": collections.Counter(),
        "6bba": collections.Counter(),
    }

    def increment(embryo: str, stage: str) -> None:
        counters["all"][stage] += 1
        counters[embryo][stage] += 1

    for stem in cfg.stems:
        nodes, edges, dcs, _ = p2.load_video(cfg.b20_cache, stem)
        embryo = stem.split("_", 1)[0]
        successors: dict[int, list[int]] = {}
        predecessors: dict[int, list[int]] = {}
        for source, target, _ in edges:
            successors.setdefault(source, []).append(target)
            predecessors.setdefault(target, []).append(source)
        positions = {
            node_id: np.asarray([node["z"], node["y"], node["x"]], dtype=np.float64) * p2.VOX
            for node_id, node in nodes.items()
        }
        prediction = nx.DiGraph()
        prediction.add_nodes_from(
            (
                node_id,
                {"t": node["t"], "z": node["z"], "y": node["y"], "x": node["x"]},
            )
            for node_id, node in nodes.items()
        )
        prediction.add_edges_from((source, target) for source, target, _ in edges)
        truth = divranker._load_gt(cfg.data_dir / f"{stem}.geff")
        pred_to_gt = divranker._match_pred_to_gt(prediction, truth, radius=7.0)
        gt_to_pred = {gt_node: pred_node for pred_node, gt_node in pred_to_gt.items()}

        for gt_parent in truth:
            gt_children = list(truth.successors(gt_parent))
            if len(gt_children) < 2:
                continue
            for key in ("all", embryo):
                counters[key]["gt_divisions"] += 1
            parent = gt_to_pred.get(gt_parent)
            if parent is None:
                continue
            increment(embryo, "parent_detected")
            daughter_predictions = [gt_to_pred.get(child) for child in gt_children[:2]]
            if any(daughter is None for daughter in daughter_predictions):
                continue
            increment(embryo, "both_daughters_detected")
            children = successors.get(parent, [])
            if len(children) != 1:
                continue
            increment(embryo, "parent_has_one_child")
            child = children[0]
            if (
                nodes[child]["t"] != nodes[parent]["t"] + 1
                or float(np.linalg.norm(positions[child] - positions[parent])) > p2.EXIST_CHILD_MAX
            ):
                continue
            increment(embryo, "existing_child_valid")
            matched_child = pred_to_gt.get(child)
            if matched_child not in gt_children:
                continue
            increment(embryo, "existing_child_is_gt_daughter")
            other_index = 1 if matched_child == gt_children[0] else 0
            candidate = daughter_predictions[other_index]
            assert candidate is not None
            if (
                candidate == child
                or nodes[candidate]["syn"]
                or nodes[candidate]["t"] != nodes[parent]["t"] + 1
            ):
                continue
            increment(embryo, "other_daughter_node_valid")
            parent_distance = float(np.linalg.norm(positions[candidate] - positions[parent]))
            sister_distance = float(np.linalg.norm(positions[candidate] - positions[child]))
            if parent_distance > cfg.parent_um:
                continue
            increment(embryo, "parent_radius")
            if not cfg.sister_min_um <= sister_distance <= cfg.sister_max_um:
                continue
            increment(embryo, "sister_range")
            if float(dcs.get(candidate, -1.0)) < cfg.deepcenter_threshold:
                continue
            increment(embryo, "deepcenter_veto")
            if predecessors.get(candidate):
                continue
            increment(embryo, "orphan_only")

    report: dict[str, Any] = {"matching_radius_um": 7.0, "groups": {}}
    for group, values in counters.items():
        total = int(values["gt_divisions"])
        report["groups"][group] = {
            stage: {
                "count": int(values[stage]),
                "fraction_of_gt": float(values[stage] / total) if total else float("nan"),
            }
            for stage in stage_names
        }
    atomic_json(cfg.output_dir / "results" / "step1_reach_diagnostic.json", report)
    return report


def build_candidates(cfg: B32Config, state: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for index, stem in enumerate(cfg.stems, start=1):
        path = candidate_path(cfg, stem)
        if not candidate_file_valid(cfg, path):
            print(f"CANDIDATES [{index}/{len(cfg.stems)}] {stem}", flush=True)
            arrays = enumerate_candidates(cfg, stem)
            atomic_npz(path, **arrays)
        with np.load(path, allow_pickle=False) as payload:
            positives = int(np.asarray(payload["label"]).sum())
            covered = len(set(np.asarray(payload["gt_parent"])[np.asarray(payload["gt_parent"]) >= 0].tolist()))
            rows.append(
                {
                    "dataset": stem,
                    "embryo": stem.split("_", 1)[0],
                    "candidates": len(payload["p"]),
                    "positives": positives,
                    "covered_gt_divisions": covered,
                    "gt_divisions": int(payload["gt_divisions"][0]),
                }
            )
        state.setdefault("candidate_videos", {})[stem] = rows[-1]
        save_state(cfg, state)
        check_stop(cfg)

    total_gt = sum(int(row["gt_divisions"]) for row in rows)
    covered_gt = sum(int(row["covered_gt_divisions"]) for row in rows)
    summary = {
        "videos": len(rows),
        "candidates": sum(int(row["candidates"]) for row in rows),
        "positives": sum(int(row["positives"]) for row in rows),
        "gt_divisions": total_gt,
        "covered_gt_divisions": covered_gt,
        "coverage": covered_gt / total_gt if total_gt else float("nan"),
        "by_embryo": {},
        "rows": rows,
    }
    for embryo in ("44b6", "6bba"):
        subset = [row for row in rows if row["embryo"] == embryo]
        gt = sum(int(row["gt_divisions"]) for row in subset)
        covered = sum(int(row["covered_gt_divisions"]) for row in subset)
        summary["by_embryo"][embryo] = {
            "videos": len(subset),
            "candidates": sum(int(row["candidates"]) for row in subset),
            "positives": sum(int(row["positives"]) for row in subset),
            "gt_divisions": gt,
            "covered_gt_divisions": covered,
            "coverage": covered / gt if gt else float("nan"),
        }
    if len(cfg.stems) == 199 and summary["coverage"] < 0.90:
        summary["reach_diagnostic"] = candidate_reach_diagnostics(cfg)
    atomic_json(cfg.output_dir / "results" / "step1_candidates.json", summary)
    state["stages"]["candidates"] = True
    state["candidate_summary"] = summary
    save_state(cfg, state)
    if len(cfg.stems) == 199 and summary["coverage"] < 0.90:
        detector_ceiling = summary["reach_diagnostic"]["groups"]["all"][
            "both_daughters_detected"
        ]["fraction_of_gt"]
        raise RuntimeError(
            f"Registered candidate pool covers only {summary['coverage']:.1%} of GT divisions (<90%). "
            f"Even the detected-parent-and-both-daughters ceiling is {detector_ceiling:.1%}. "
            "Do not train: widening the radius cannot meet the registered gate."
        )
    return summary


def preflight(cfg: B32Config, gpu_smoke: bool = True) -> dict[str, Any]:
    install_import_paths(cfg)
    import torch
    from tools.divnet_infer import DivNetMitosisClassifier
    from divpair_infer import DivPairClassifier, initialise_from_divnet

    errors: list[str] = []
    if len(cfg.all_stems) != 199:
        errors.append(f"expected 199 image/GT pairs, found {len(cfg.all_stems)}")
    for folder, suffix, expected in (("ckpt", ".npz", 199), ("dc", ".npz", 199), ("raw", ".geff", 199)):
        base = cfg.b20_cache / folder
        count = len(list(base.glob(f"*{suffix}")))
        if count != expected:
            errors.append(f"{base}: expected {expected}, found {count}")
    if not cfg.parent_checkpoint.is_file():
        errors.append(f"missing DivNet checkpoint: {cfg.parent_checkpoint}")
    control = cfg.b20_cache / "pp" / "control_public.json"
    if not control.is_file():
        errors.append(f"missing B20 public control: {control}")
    if cfg.epochs < 1 or cfg.batch_size < 1 or cfg.score_batch_size < 1:
        errors.append("epochs and batch sizes must be positive")
    if cfg.run_pipeline and not torch.cuda.is_available():
        errors.append("CUDA is required for B32 training and full-candidate scoring")
    if errors:
        raise RuntimeError("B32 preflight failed:\n- " + "\n- ".join(errors))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    state, _ = __import__("divpair_infer").load_parent_checkpoint(cfg.parent_checkpoint)
    base = DivNetMitosisClassifier(in_channels=5, base_channels=16)
    base.load_state_dict(state, strict=True)
    pair = DivPairClassifier(geometry_dim=19)
    init = initialise_from_divnet(pair, cfg.parent_checkpoint)
    base.to(device).eval()
    pair.to(device).eval()
    generator = torch.Generator(device="cpu").manual_seed(cfg.seed)
    x5 = torch.randn((1, 5, 16, 32, 32), generator=generator).to(device)
    x7 = torch.cat([x5, torch.zeros((1, 2, 16, 32, 32), device=device)], dim=1)
    geometry = torch.zeros((1, 19), device=device)
    with torch.inference_mode():
        equivalence_error = float((base(x5) - pair(x7, geometry)).abs().max().item())
    if equivalence_error > 1e-5:
        raise RuntimeError(f"DivPair initialisation is not DivNet-equivalent: {equivalence_error}")

    smoke: list[dict[str, Any]] = []
    if gpu_smoke:
        for prefix in ("44b6", "6bba"):
            for stem in (item for item in cfg.stems if item.startswith(prefix)):
                arrays = enumerate_candidates(cfg, stem)
                if len(arrays["p"]):
                    smoke.append(
                        {
                            "dataset": stem,
                            "candidates": len(arrays["p"]),
                            "positives": int(arrays["label"].sum()),
                        }
                    )
                    break
    result = {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "cuda": torch.cuda.is_available(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "videos": len(cfg.stems),
        "full_dataset_videos": len(cfg.all_stems),
        "b20_cache": str(cfg.b20_cache),
        "parent_checkpoint": str(cfg.parent_checkpoint),
        "divnet_equivalence_max_abs": equivalence_error,
        "initialisation": init,
        "candidate_smoke": smoke,
    }
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    atomic_json(cfg.output_dir / "config.json", cfg.serialisable())
    atomic_json(cfg.output_dir / "preflight.json", result)
    return result


def choose_train_indices(cfg: B32Config, stem: str, labels: np.ndarray, features: np.ndarray) -> np.ndarray:
    positives = np.flatnonzero(labels > 0)
    negatives = np.flatnonzero(labels == 0)
    requested = max(
        cfg.minimum_negatives_per_video,
        cfg.negatives_per_positive * max(1, len(positives)),
    )
    requested = min(cfg.maximum_negatives_per_video, requested, len(negatives))
    if requested <= 0:
        return positives.astype(np.int64)
    hard_count = requested // 2
    geometry_cost = features[negatives, 1] + 0.15 * features[negatives, 2]
    hard = negatives[np.argsort(geometry_cost, kind="stable")[:hard_count]]
    remaining = np.setdiff1d(negatives, hard, assume_unique=False)
    rng = np.random.default_rng(stable_seed(cfg.seed, stem))
    random_count = requested - len(hard)
    sampled = (
        rng.choice(remaining, size=random_count, replace=False)
        if random_count and len(remaining) >= random_count
        else remaining
    )
    indices = np.concatenate([positives, hard, sampled]).astype(np.int64)
    return indices[np.argsort(indices, kind="stable")]


def sample_file_valid(cfg: B32Config, path: Path, candidate_count: int) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path, allow_pickle=False) as payload:
            return (
                {"image", "geometry", "label", "candidate_index", "recipe_fingerprint"}
                <= set(payload.files)
                and str(payload["recipe_fingerprint"][0]) == cfg.fingerprint()
                and np.all(np.asarray(payload["candidate_index"]) < candidate_count)
            )
    except Exception:
        return False


def build_train_sample_video(cfg: B32Config, stem: str) -> dict[str, Any]:
    install_import_paths(cfg)
    import pass2_rank_divisions as p2
    from divpair_infer import PairInputBuilder

    candidates = candidate_path(cfg, stem)
    with np.load(candidates, allow_pickle=False) as payload:
        labels = np.asarray(payload["label"], dtype=np.uint8)
        features = np.asarray(payload["features"], dtype=np.float32)
        parent = np.asarray(payload["p"], dtype=np.int64)
        child = np.asarray(payload["c"], dtype=np.int64)
        candidate = np.asarray(payload["q"], dtype=np.int64)
        times = np.asarray(payload["t"], dtype=np.int16)
    indices = choose_train_indices(cfg, stem, labels, features)
    output = sample_path(cfg, stem)
    if sample_file_valid(cfg, output, len(labels)):
        with np.load(output, allow_pickle=False) as existing:
            return {
                "dataset": stem,
                "samples": len(existing["label"]),
                "positives": int(np.asarray(existing["label"]).sum()),
                "resumed": True,
            }

    nodes, _, _, _ = p2.load_video(cfg.b20_cache, stem)
    builder = PairInputBuilder(cfg.data_dir, cfg.parent_checkpoint)
    builder.reset_video()
    order = indices[
        np.lexsort(
            (
                indices,
                candidate[indices],
                parent[indices],
                times[indices],
            )
        )
    ]
    images: list[np.ndarray] = []
    for position, candidate_index in enumerate(order, start=1):
        if position % 32 == 0:
            check_stop(cfg)
        p = int(parent[candidate_index])
        c = int(child[candidate_index])
        q = int(candidate[candidate_index])
        images.append(builder.build(stem, int(times[candidate_index]), nodes[p], nodes[c], nodes[q]))
    image = (
        np.stack(images).astype(np.float16)
        if images
        else np.zeros((0, 7, 16, 32, 32), dtype=np.float16)
    )
    atomic_npz(
        output,
        compressed=False,
        image=image,
        geometry=features[order].astype(np.float32),
        label=labels[order].astype(np.uint8),
        candidate_index=order.astype(np.int64),
        recipe_fingerprint=np.asarray([cfg.fingerprint()]),
    )
    return {
        "dataset": stem,
        "samples": len(order),
        "positives": int(labels[order].sum()),
        "resumed": False,
    }


def build_train_samples(cfg: B32Config, state: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for index, stem in enumerate(cfg.stems, start=1):
        print(f"TRAIN CACHE [{index}/{len(cfg.stems)}] {stem}", flush=True)
        row = build_train_sample_video(cfg, stem)
        rows.append(row)
        state.setdefault("sample_videos", {})[stem] = row
        save_state(cfg, state)
        check_stop(cfg)
    summary = {
        "videos": len(rows),
        "samples": sum(int(row["samples"]) for row in rows),
        "positives": sum(int(row["positives"]) for row in rows),
        "rows": rows,
    }
    atomic_json(cfg.output_dir / "results" / "train_sample_cache.json", summary)
    state["stages"]["train_samples"] = True
    save_state(cfg, state)
    return summary


def load_sample_arrays(cfg: B32Config, stems: Iterable[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    images: list[np.ndarray] = []
    geometry: list[np.ndarray] = []
    labels: list[np.ndarray] = []
    for stem in stems:
        path = sample_path(cfg, stem)
        if not path.is_file():
            raise FileNotFoundError(path)
        with np.load(path, allow_pickle=False) as payload:
            images.append(np.asarray(payload["image"]).copy())
            geometry.append(np.asarray(payload["geometry"], dtype=np.float32).copy())
            labels.append(np.asarray(payload["label"], dtype=np.float32).copy())
    if not images or sum(len(item) for item in images) == 0:
        raise RuntimeError("No cached samples for this split")
    return np.concatenate(images), np.concatenate(geometry), np.concatenate(labels)


def binary_metrics(labels: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    from sklearn.metrics import precision_recall_curve, roc_auc_score

    labels = np.asarray(labels, dtype=np.uint8)
    probability = np.asarray(probability, dtype=np.float64)
    result: dict[str, float] = {
        "samples": float(len(labels)),
        "positives": float(labels.sum()),
    }
    if len(labels) == 0:
        result["auc"] = float("nan")
        result["precision_at_recall_0p5"] = float("nan")
        result["precision_at_recall_0p7"] = float("nan")
        return result
    result["auc"] = float(roc_auc_score(labels, probability)) if len(np.unique(labels)) == 2 else float("nan")
    if labels.sum() == 0:
        result["precision_at_recall_0p5"] = float("nan")
        result["precision_at_recall_0p7"] = float("nan")
        return result
    precision, recall, _ = precision_recall_curve(labels, probability)
    for target, key in ((0.5, "precision_at_recall_0p5"), (0.7, "precision_at_recall_0p7")):
        eligible = precision[recall >= target]
        result[key] = float(np.max(eligible)) if len(eligible) else 0.0
    return result


def normalise_geometry(
    train: np.ndarray,
    other: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray | None, np.ndarray, np.ndarray]:
    train_finite = np.nan_to_num(np.asarray(train, dtype=np.float32), nan=-1.0, posinf=10.0, neginf=-10.0)
    mean = train_finite.mean(axis=0, dtype=np.float64).astype(np.float32)
    std = train_finite.std(axis=0, dtype=np.float64).astype(np.float32)
    std = np.where(std < 1e-5, 1.0, std).astype(np.float32)
    train_norm = np.clip((train_finite - mean) / std, -8.0, 8.0).astype(np.float32)
    if other is None:
        return train_norm, None, mean, std
    other_finite = np.nan_to_num(np.asarray(other, dtype=np.float32), nan=-1.0, posinf=10.0, neginf=-10.0)
    other_norm = np.clip((other_finite - mean) / std, -8.0, 8.0).astype(np.float32)
    return train_norm, other_norm, mean, std


def rng_payload() -> dict[str, Any]:
    import torch

    return {
        "python_rng": random.getstate(),
        "numpy_rng": np.random.get_state(),
        "torch_rng": torch.get_rng_state(),
        "cuda_rng": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
    }


def restore_rng(payload: dict[str, Any]) -> None:
    import torch

    if "python_rng" in payload:
        random.setstate(payload["python_rng"])
    if "numpy_rng" in payload:
        np.random.set_state(payload["numpy_rng"])
    if "torch_rng" in payload:
        torch.set_rng_state(payload["torch_rng"])
    if torch.cuda.is_available() and payload.get("cuda_rng") is not None:
        torch.cuda.set_rng_state_all(payload["cuda_rng"])


def evaluate_tensor_set(
    model: Any,
    images: np.ndarray,
    geometry: np.ndarray,
    labels: np.ndarray,
    device: Any,
    batch_size: int,
    amp: bool,
) -> tuple[float, dict[str, float]]:
    import torch

    model.eval()
    probabilities: list[np.ndarray] = []
    losses: list[float] = []
    criterion = torch.nn.BCEWithLogitsLoss()
    with torch.inference_mode():
        for start in range(0, len(labels), batch_size):
            x = torch.from_numpy(images[start : start + batch_size]).to(device=device, dtype=torch.float32)
            g = torch.from_numpy(geometry[start : start + batch_size]).to(device=device, dtype=torch.float32)
            y = torch.from_numpy(labels[start : start + batch_size]).to(device=device, dtype=torch.float32)
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=amp and device.type == "cuda"):
                logits = model(x, g).flatten()
                loss = criterion(logits, y)
            losses.append(float(loss.item()) * len(y))
            probabilities.append(torch.sigmoid(logits).float().cpu().numpy())
    probability = np.concatenate(probabilities)
    return sum(losses) / max(1, len(labels)), binary_metrics(labels, probability)


def train_fold(
    cfg: B32Config,
    fold_name: str,
    train_prefix: str,
    validation_prefix: str,
) -> dict[str, Any]:
    install_import_paths(cfg)
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    from divpair_infer import DivPairClassifier, augment_batch, initialise_from_divnet

    fold_dir = cfg.output_dir / "folds" / fold_name
    last_path = fold_dir / "last.pt"
    best_path = fold_dir / "best.pt"
    history_path = fold_dir / "history.json"
    train_stems = [stem for stem in cfg.stems if stem.startswith(train_prefix)]
    validation_stems = [stem for stem in cfg.stems if stem.startswith(validation_prefix)]
    if not train_stems or not validation_stems:
        raise RuntimeError(f"{fold_name}: both embryo groups are required")
    print(f"Loading {fold_name}: train={len(train_stems)} val={len(validation_stems)}", flush=True)
    train_x, train_geometry, train_y = load_sample_arrays(cfg, train_stems)
    val_x, val_geometry, val_y = load_sample_arrays(cfg, validation_stems)
    train_geometry, val_geometry, geometry_mean, geometry_std = normalise_geometry(train_geometry, val_geometry)
    if train_y.sum() == 0 or val_y.sum() == 0:
        raise RuntimeError(f"{fold_name}: missing positive triples in train or validation")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DivPairClassifier(geometry_dim=train_geometry.shape[1])
    init_report = initialise_from_divnet(model, cfg.parent_checkpoint)
    model.to(device)
    optimiser = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay)
    scaler = torch.amp.GradScaler("cuda", enabled=cfg.use_amp and device.type == "cuda")
    positive_weight = float((len(train_y) - train_y.sum()) / max(1.0, train_y.sum()))
    criterion = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor([positive_weight], device=device))
    dataset = TensorDataset(
        torch.from_numpy(train_x),
        torch.from_numpy(train_geometry),
        torch.from_numpy(train_y),
    )
    start_epoch = 0
    best_auc = -math.inf
    history: list[dict[str, Any]] = []
    if last_path.is_file():
        payload = torch.load(last_path, map_location="cpu", weights_only=False)
        if payload.get("fingerprint") != cfg.fingerprint() or payload.get("fold") != fold_name:
            raise RuntimeError(f"Incompatible checkpoint: {last_path}")
        model.load_state_dict(payload["model_state"], strict=True)
        optimiser.load_state_dict(payload["optimizer_state"])
        scaler.load_state_dict(payload["scaler_state"])
        start_epoch = int(payload["epoch"]) + 1
        best_auc = float(payload.get("best_auc", -math.inf))
        history = list(payload.get("history", []))
        restore_rng(payload)
        print(f"Resuming {fold_name} at epoch {start_epoch + 1}", flush=True)
    else:
        random.seed(cfg.seed)
        np.random.seed(cfg.seed)
        torch.manual_seed(cfg.seed)
        torch.cuda.manual_seed_all(cfg.seed)

    for epoch in range(start_epoch, cfg.epochs):
        check_stop(cfg)
        generator = torch.Generator().manual_seed(cfg.seed + epoch)
        loader = DataLoader(
            dataset,
            batch_size=cfg.batch_size,
            shuffle=True,
            generator=generator,
            num_workers=0,
            pin_memory=device.type == "cuda",
        )
        model.train()
        total_loss = 0.0
        seen = 0
        epoch_started = time.time()
        for images, geometry, labels in loader:
            images = images.to(device=device, dtype=torch.float32, non_blocking=True)
            geometry = geometry.to(device=device, dtype=torch.float32, non_blocking=True)
            labels = labels.to(device=device, dtype=torch.float32, non_blocking=True)
            images = augment_batch(images)
            optimiser.zero_grad(set_to_none=True)
            with torch.autocast(
                device_type=device.type,
                dtype=torch.float16,
                enabled=cfg.use_amp and device.type == "cuda",
            ):
                logits = model(images, geometry).flatten()
                loss = criterion(logits, labels)
            scaler.scale(loss).backward()
            scaler.step(optimiser)
            scaler.update()
            total_loss += float(loss.item()) * len(labels)
            seen += len(labels)
        validation_loss, validation_metrics = evaluate_tensor_set(
            model,
            val_x,
            val_geometry,
            val_y,
            device,
            cfg.score_batch_size,
            cfg.use_amp,
        )
        row = {
            "epoch": epoch + 1,
            "train_loss": total_loss / max(1, seen),
            "validation_loss": validation_loss,
            **validation_metrics,
            "seconds": time.time() - epoch_started,
        }
        history.append(row)
        auc = float(validation_metrics["auc"])
        checkpoint = {
            "version": 1,
            "experiment": EXPERIMENT,
            "fingerprint": cfg.fingerprint(),
            "fold": fold_name,
            "epoch": epoch,
            "epochs_requested": cfg.epochs,
            "model_state": model.state_dict(),
            "optimizer_state": optimiser.state_dict(),
            "scaler_state": scaler.state_dict(),
            "best_auc": max(best_auc, auc),
            "geometry_dim": train_geometry.shape[1],
            "geometry_mean": geometry_mean,
            "geometry_std": geometry_std,
            "history": history,
            "initialisation": init_report,
            "train_prefix": train_prefix,
            "validation_prefix": validation_prefix,
            "positive_weight": positive_weight,
            **rng_payload(),
        }
        atomic_torch(last_path, checkpoint)
        atomic_json(history_path, history)
        if auc > best_auc:
            best_auc = auc
            atomic_torch(best_path, checkpoint)
        print(
            f"{fold_name} epoch {epoch + 1}/{cfg.epochs}: loss={row['train_loss']:.5f} "
            f"val_auc={auc:.5f} p@r50={row['precision_at_recall_0p5']:.4f} "
            f"p@r70={row['precision_at_recall_0p7']:.4f}",
            flush=True,
        )
    del train_x, train_geometry, train_y, val_x, val_geometry, val_y, dataset, model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return {
        "fold": fold_name,
        "train_prefix": train_prefix,
        "validation_prefix": validation_prefix,
        "best_auc": best_auc,
        "best_checkpoint": str(best_path),
        "epochs": cfg.epochs,
    }


def oof_path(cfg: B32Config, stem: str) -> Path:
    return cfg.output_dir / "oof" / f"{stem}.npz"


def score_video_oof(cfg: B32Config, stem: str, checkpoint: Path) -> dict[str, Any]:
    install_import_paths(cfg)
    import torch
    import pass2_rank_divisions as p2
    from divpair_infer import PairInputBuilder, load_model_checkpoint, probability_batch

    with np.load(candidate_path(cfg, stem), allow_pickle=False) as payload:
        parent = np.asarray(payload["p"], dtype=np.int64)
        child = np.asarray(payload["c"], dtype=np.int64)
        candidate = np.asarray(payload["q"], dtype=np.int64)
        times = np.asarray(payload["t"], dtype=np.int16)
        features = np.asarray(payload["features"], dtype=np.float32)
        labels = np.asarray(payload["label"], dtype=np.uint8)
    output = oof_path(cfg, stem)
    if output.is_file():
        with np.load(output, allow_pickle=False) as existing:
            if (
                len(existing["score"]) == len(parent)
                and str(existing["recipe_fingerprint"][0]) == cfg.fingerprint()
            ):
                return {
                    "dataset": stem,
                    "candidates": len(parent),
                    "positives": int(labels.sum()),
                    "resumed": True,
                }

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, model_payload = load_model_checkpoint(checkpoint, device)
    geometry_mean = np.asarray(model_payload["geometry_mean"], dtype=np.float32)
    geometry_std = np.asarray(model_payload["geometry_std"], dtype=np.float32)
    geometry = np.nan_to_num(features, nan=-1.0, posinf=10.0, neginf=-10.0)
    geometry = np.clip((geometry - geometry_mean) / geometry_std, -8.0, 8.0).astype(np.float32)
    nodes, _, _, _ = p2.load_video(cfg.b20_cache, stem)
    builder = PairInputBuilder(cfg.data_dir, cfg.parent_checkpoint)
    builder.reset_video()
    partial = output.with_name(output.stem + ".partial.npz")
    scores = np.full(len(parent), np.nan, dtype=np.float32)
    start_index = 0
    if partial.is_file():
        with np.load(partial, allow_pickle=False) as saved:
            if len(saved["score"]) == len(scores) and str(saved["recipe_fingerprint"][0]) == cfg.fingerprint():
                scores[:] = saved["score"]
                start_index = int(saved["done"][0])
    for start in range(start_index, len(parent), cfg.score_batch_size):
        check_stop(cfg)
        stop = min(start + cfg.score_batch_size, len(parent))
        images = np.stack(
            [
                builder.build(
                    stem,
                    int(times[index]),
                    nodes[int(parent[index])],
                    nodes[int(child[index])],
                    nodes[int(candidate[index])],
                )
                for index in range(start, stop)
            ]
        )
        scores[start:stop] = probability_batch(
            model,
            images,
            geometry[start:stop],
            device,
            cfg.use_amp,
        )
        atomic_npz(
            partial,
            score=scores,
            done=np.asarray([stop], dtype=np.int64),
            recipe_fingerprint=np.asarray([cfg.fingerprint()]),
        )
        if stop % 2048 < cfg.score_batch_size or stop == len(parent):
            print(f"  {stem}: {stop}/{len(parent)} triples", flush=True)
    if not np.isfinite(scores).all():
        raise RuntimeError(f"{stem}: OOF scoring left non-finite values")
    atomic_npz(
        output,
        p=parent,
        c=child,
        q=candidate,
        score=scores,
        label=labels,
        recipe_fingerprint=np.asarray([cfg.fingerprint()]),
        checkpoint=np.asarray([str(checkpoint.resolve())]),
    )
    partial.unlink(missing_ok=True)
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return {
        "dataset": stem,
        "candidates": len(parent),
        "positives": int(labels.sum()),
        "resumed": False,
    }


def divnet_parent_scores(cfg: B32Config, stem: str, parents: np.ndarray) -> np.ndarray:
    source = cfg.b20_cache / "divnet" / f"{stem}.npz"
    with np.load(source, allow_pickle=False) as payload:
        mapping = {int(node): float(score) for node, score in zip(payload["p"], payload["score"])}
    return np.asarray([mapping.get(int(parent), np.nan) for parent in parents], dtype=np.float32)


def build_oof_metrics(cfg: B32Config) -> dict[str, Any]:
    result: dict[str, Any] = {"folds": {}, "all": {}}
    all_labels: list[np.ndarray] = []
    all_pair: list[np.ndarray] = []
    all_parent: list[np.ndarray] = []
    for fold_name, _, validation_prefix in FOLDS:
        fold_labels: list[np.ndarray] = []
        fold_pair: list[np.ndarray] = []
        fold_parent: list[np.ndarray] = []
        for stem in (item for item in cfg.stems if item.startswith(validation_prefix)):
            with np.load(oof_path(cfg, stem), allow_pickle=False) as payload:
                labels = np.asarray(payload["label"], dtype=np.uint8)
                pair_score = np.asarray(payload["score"], dtype=np.float32)
                parents = np.asarray(payload["p"], dtype=np.int64)
            parent_score = divnet_parent_scores(cfg, stem, parents)
            fold_labels.append(labels)
            fold_pair.append(pair_score)
            fold_parent.append(parent_score)
        labels = np.concatenate(fold_labels)
        pair_score = np.concatenate(fold_pair)
        parent_score = np.concatenate(fold_parent)
        parent_finite = np.isfinite(parent_score)
        result["folds"][fold_name] = {
            "validation_prefix": validation_prefix,
            "divpair": binary_metrics(labels, pair_score),
            "divnet_parent_control": {
                **binary_metrics(labels[parent_finite], parent_score[parent_finite]),
                "coverage": float(parent_finite.mean()),
            },
        }
        all_labels.append(labels)
        all_pair.append(pair_score)
        all_parent.append(parent_score)
    labels = np.concatenate(all_labels)
    parent_score = np.concatenate(all_parent)
    parent_finite = np.isfinite(parent_score)
    result["all"] = {
        "divpair": binary_metrics(labels, np.concatenate(all_pair)),
        "divnet_parent_control": {
            **binary_metrics(labels[parent_finite], parent_score[parent_finite]),
            "coverage": float(parent_finite.mean()),
        },
    }
    atomic_json(cfg.output_dir / "results" / "step2_oof_metrics.json", result)
    return result


def run_oof(cfg: B32Config, state: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for fold_name, _, validation_prefix in FOLDS:
        checkpoint = cfg.output_dir / "folds" / fold_name / "best.pt"
        if not checkpoint.is_file():
            raise FileNotFoundError(checkpoint)
        stems = [stem for stem in cfg.stems if stem.startswith(validation_prefix)]
        for index, stem in enumerate(stems, start=1):
            print(f"OOF {fold_name} [{index}/{len(stems)}] {stem}", flush=True)
            row = score_video_oof(cfg, stem, checkpoint)
            rows.append(row)
            state.setdefault("oof_videos", {})[stem] = row
            save_state(cfg, state)
            check_stop(cfg)
    metrics = build_oof_metrics(cfg)
    state["stages"]["oof"] = True
    state["oof_metrics"] = metrics
    save_state(cfg, state)
    return metrics


def source_counts_by_frame(nodes: dict[int, dict], edges: list[tuple]) -> dict[int, int]:
    successors: dict[int, list[int]] = {}
    for source, target, _ in edges:
        successors.setdefault(int(source), []).append(int(target))
    counts: dict[int, int] = {}
    for source, targets in successors.items():
        if len(targets) != 1 or source not in nodes or targets[0] not in nodes:
            continue
        time_value = int(nodes[source]["t"])
        if int(nodes[targets[0]]["t"]) == time_value + 1:
            counts[time_value] = counts.get(time_value, 0) + 1
    return counts


def apply_divpair_edges(
    nodes: dict[int, dict],
    edges: list[tuple[int, int, float | None]],
    parent: np.ndarray,
    candidate: np.ndarray,
    times: np.ndarray,
    scores: np.ndarray,
    threshold: float,
    cap_mode: str,
) -> tuple[list[tuple[int, int, float | None]], int]:
    if cap_mode not in CAP_MODES:
        raise ValueError(cap_mode)
    multiplier = {"public": 1.0, "double": 2.0, "none": math.inf}[cap_mode]
    frame_sources = source_counts_by_frame(nodes, edges)
    result = list(edges)
    used_sources: set[int] = set()
    used_targets: set[int] = set()
    per_frame: dict[int, int] = {}
    global_cap = math.inf if not math.isfinite(multiplier) else max(1, int(round(len(edges) * 0.00375 * multiplier)))
    order = sorted(
        range(len(scores)),
        key=lambda index: (-float(scores[index]), int(parent[index]), int(candidate[index])),
    )
    added = 0
    for index in order:
        if not np.isfinite(scores[index]) or float(scores[index]) < threshold:
            continue
        p = int(parent[index])
        q = int(candidate[index])
        t = int(times[index])
        if added >= global_cap:
            break
        frame_cap = (
            math.inf
            if not math.isfinite(multiplier)
            else max(1, int(round(frame_sources.get(t, 1) * 0.0076 * multiplier)))
        )
        if per_frame.get(t, 0) >= frame_cap or p in used_sources or q in used_targets:
            continue
        result.append((p, q, None))
        used_sources.add(p)
        used_targets.add(q)
        per_frame[t] = per_frame.get(t, 0) + 1
        added += 1
    return result, added


_POSTPROCESS_NAMESPACE: dict[str, Any] | None = None


def postprocess_namespace(cfg: B32Config) -> dict[str, Any]:
    global _POSTPROCESS_NAMESPACE
    if _POSTPROCESS_NAMESPACE is not None:
        return _POSTPROCESS_NAMESPACE
    install_import_paths(cfg)
    import public_local as pl

    os.environ["BIOHUB_OUTPUT_SAFE_DIVISIONS"] = "0"
    os.environ["BIOHUB_OUTPUT_MOTION_RELINK"] = "0"
    os.environ["BIOHUB_OUTPUT_GAP_CLOSE"] = "0"
    os.environ["BIOHUB_OUTPUT_GAP2_RECOVERY"] = "0"
    os.environ["BIOHUB_USE_DEEPCENTER_VETO"] = "0"
    os.environ["BIOHUB_REQUIRE_DEEPCENTER_VETO"] = "0"
    work = cfg.output_dir / "postprocess_work"
    work.mkdir(parents=True, exist_ok=True)
    cells = pl.notebook_cells(pl.DEFAULT_NOTEBOOK)
    _POSTPROCESS_NAMESPACE = pl.build_cached_postproc_namespace(cells, work, cfg.data_dir)
    return _POSTPROCESS_NAMESPACE


def write_pass2_video(
    cfg: B32Config,
    stem: str,
    threshold: float,
    cap_mode: str,
    output: Path,
) -> dict[str, Any]:
    install_import_paths(cfg)
    import networkx as nx
    import pass2_rank_divisions as p2
    import postproc

    marker = output.parent / f"{output.name}.complete"
    if output.is_dir() and marker.is_file():
        return {"dataset": stem, "status": "resumed"}
    nodes, edges, _, _ = p2.load_video(cfg.b20_cache, stem)
    with np.load(candidate_path(cfg, stem), allow_pickle=False) as meta:
        parent = np.asarray(meta["p"], dtype=np.int64)
        candidate = np.asarray(meta["q"], dtype=np.int64)
        times = np.asarray(meta["t"], dtype=np.int16)
    with np.load(oof_path(cfg, stem), allow_pickle=False) as prediction:
        if not (
            np.array_equal(parent, prediction["p"])
            and np.array_equal(candidate, prediction["q"])
        ):
            raise RuntimeError(f"Candidate/OOF alignment mismatch for {stem}")
        scores = np.asarray(prediction["score"], dtype=np.float32)
    new_edges, added = apply_divpair_edges(
        nodes,
        edges,
        parent,
        candidate,
        times,
        scores,
        threshold,
        cap_mode,
    )
    node_records = {
        node_id: {
            "node_id": node_id,
            "t": node["t"],
            "z": node["z"],
            "y": node["y"],
            "x": node["x"],
            **({"gap_synthetic": 1} if node["syn"] else {}),
        }
        for node_id, node in nodes.items()
    }
    edge_records = [
        {"source_id": source, "target_id": target, "edge_prob": probability}
        for source, target, probability in new_edges
    ]
    namespace = postprocess_namespace(cfg)
    node_records, edge_records, _ = namespace["filter_output_graph"](
        node_records,
        edge_records,
        dataset=stem,
        deepcenter_bundle=None,
    )
    graph = nx.DiGraph()
    for node_id, node in node_records.items():
        graph.add_node(
            int(node_id),
            t=int(node["t"]),
            z=float(max(0, round(node["z"]))),
            y=float(max(0, round(node["y"]))),
            x=float(max(0, round(node["x"]))),
        )
    for edge in edge_records:
        graph.add_edge(int(edge["source_id"]), int(edge["target_id"]))
    temporary = output.parent / f"{output.stem}.partial.geff"
    if temporary.exists():
        shutil.rmtree(temporary)
    postproc.save(graph, temporary)
    if output.exists():
        shutil.rmtree(output)
    os.replace(temporary, output)
    marker.write_text("complete\n", encoding="utf-8")
    return {
        "dataset": stem,
        "status": "written",
        "added_division_edges": added,
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
    }


def summarise_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    from score_geffs import summarise

    return jsonable(summarise(rows))


def metric_bundle(summary: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {"all": jsonable(summary), "by_embryo": {}}
    for embryo in ("44b6", "6bba"):
        subset = [row for row in rows if str(row["dataset"]).startswith(embryo)]
        result["by_embryo"][embryo] = summarise_rows(subset)
    result["node_total"] = int(sum(int(row["num_pred_nodes"]) for row in rows))
    return result


def load_control_metrics(cfg: B32Config) -> dict[str, Any]:
    source = cfg.b20_cache / "pp" / "control_public.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    if len(payload.get("metric_rows", [])) != 199:
        raise RuntimeError("B20 public control is incomplete")
    wanted = set(cfg.stems)
    rows = [row for row in payload["metric_rows"] if row["dataset"] in wanted]
    if len(rows) != len(wanted):
        raise RuntimeError(f"B20 public control covers {len(rows)}/{len(wanted)} selected videos")
    summary = payload["summary"] if len(rows) == 199 else summarise_rows(rows)
    return metric_bundle(summary, rows)


def pass2_variant(
    cfg: B32Config,
    state: dict[str, Any],
    threshold: float,
    cap_mode: str,
) -> dict[str, Any]:
    install_import_paths(cfg)
    import public_local as pl

    label = f"divpair_t{threshold:.1f}_{cap_mode}".replace(".", "p")
    output_dir = cfg.output_dir / "pass2" / label
    output_dir.mkdir(parents=True, exist_ok=True)
    progress: list[dict[str, Any]] = []
    for index, stem in enumerate(cfg.stems, start=1):
        print(f"PASS2 {label} [{index}/{len(cfg.stems)}] {stem}", flush=True)
        row = write_pass2_video(cfg, stem, threshold, cap_mode, output_dir / f"{stem}.geff")
        progress.append(row)
        state.setdefault("pass2_videos", {}).setdefault(label, {})[stem] = row
        save_state(cfg, state)
        check_stop(cfg)
    missing = [stem for stem in cfg.stems if not (output_dir / f"{stem}.geff").is_dir()]
    if missing:
        raise RuntimeError(f"{label}: missing {len(missing)} outputs")
    summary, rows = pl.score_dir(output_dir, cfg.data_dir)
    result = {
        "label": label,
        "threshold": threshold,
        "cap_mode": cap_mode,
        "metrics": metric_bundle(summary, rows),
        "progress": progress,
    }
    atomic_json(cfg.output_dir / "results" / f"{label}.json", result)
    state["stages"][label] = True
    save_state(cfg, state)
    return result


def gate_result(control: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    candidate = result["metrics"]
    comparisons: dict[str, Any] = {}
    passed = True
    for key in ("all", "44b6", "6bba"):
        baseline = control["all"] if key == "all" else control["by_embryo"][key]
        current = candidate["all"] if key == "all" else candidate["by_embryo"][key]
        row = {
            "control_score": float(baseline["score"]),
            "score": float(current["score"]),
            "score_delta": float(current["score"] - baseline["score"]),
            "control_adj_edge": float(baseline["adj_edge_jaccard"]),
            "adj_edge": float(current["adj_edge_jaccard"]),
            "adj_edge_delta": float(current["adj_edge_jaccard"] - baseline["adj_edge_jaccard"]),
            "division_jaccard": float(current["division_jaccard"]),
            "division_tp": int(current["division_tp"]),
            "division_fp": int(current["division_fp"]),
            "division_fn": int(current["division_fn"]),
        }
        row["passes"] = bool(row["score_delta"] >= 0.005 and row["adj_edge_delta"] >= -0.001)
        passed = passed and row["passes"]
        comparisons[key] = row
    node_delta = int(candidate["node_total"] - control["node_total"])
    return {
        "label": result["label"],
        "threshold": result["threshold"],
        "cap_mode": result["cap_mode"],
        "comparisons": comparisons,
        "control_nodes": int(control["node_total"]),
        "nodes": int(candidate["node_total"]),
        "node_delta": node_delta,
        "passes_gate": bool(passed and node_delta == 0),
    }


def build_final_report(
    cfg: B32Config,
    control: dict[str, Any],
    results: list[dict[str, Any]],
    oof_metrics: dict[str, Any],
) -> dict[str, Any]:
    rows = [gate_result(control, result) for result in results]
    winners = [row for row in rows if row["passes_gate"]]
    winners.sort(key=lambda row: row["comparisons"]["all"]["score"], reverse=True)
    report = {
        "experiment": EXPERIMENT,
        "videos": len(cfg.stems),
        "gate": "score delta >= +0.005 and adj_edge delta >= -0.001 on all/44b6/6bba, node total unchanged",
        "control": control,
        "oof_metrics": oof_metrics,
        "rows": rows,
        "winner": winners[0] if winners else None,
    }
    atomic_json(cfg.output_dir / "results.json", report)
    lines = [
        "# Friend A B32 DivPair results",
        "",
        f"Videos: {len(cfg.stems)}. Gate: {report['gate']}.",
        "",
        "| variant | all score/delta | 44b6 delta | 6bba delta | adj deltas all/44b6/6bba | div TP/FP/FN | node delta | gate |",
        "|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in rows:
        all_metrics = row["comparisons"]["all"]
        lines.append(
            f"| {row['label']} | {all_metrics['score']:.5f} / {all_metrics['score_delta']:+.5f} | "
            f"{row['comparisons']['44b6']['score_delta']:+.5f} | {row['comparisons']['6bba']['score_delta']:+.5f} | "
            f"{all_metrics['adj_edge_delta']:+.5f} / {row['comparisons']['44b6']['adj_edge_delta']:+.5f} / "
            f"{row['comparisons']['6bba']['adj_edge_delta']:+.5f} | "
            f"{all_metrics['division_tp']}/{all_metrics['division_fp']}/{all_metrics['division_fn']} | "
            f"{row['node_delta']:+d} | {'PASS' if row['passes_gate'] else '-'} |"
        )
    lines.extend(
        [
            "",
            "Winner: " + (winners[0]["label"] if winners else "none"),
            "",
            "No leaderboard submission is performed by this experiment.",
            "",
        ]
    )
    text = "\n".join(lines)
    (cfg.output_dir / "result.md").write_text(text, encoding="utf-8")
    tracked = cfg.repo_root / "experiments" / EXPERIMENT / "results"
    tracked.mkdir(parents=True, exist_ok=True)
    atomic_json(tracked / "b32_final.json", report)
    (tracked / "b32_final.md").write_text(text, encoding="utf-8")
    return report


def train_final_model(cfg: B32Config) -> Path:
    """Train the gated recipe on all 199 videos for the registered epoch count."""
    install_import_paths(cfg)
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    from divpair_infer import DivPairClassifier, augment_batch, initialise_from_divnet

    final_dir = cfg.output_dir / "final_model"
    last_path = final_dir / "last.pt"
    images, geometry, labels = load_sample_arrays(cfg, cfg.stems)
    geometry, _, geometry_mean, geometry_std = normalise_geometry(geometry)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DivPairClassifier(geometry_dim=geometry.shape[1])
    init_report = initialise_from_divnet(model, cfg.parent_checkpoint)
    model.to(device)
    optimiser = torch.optim.AdamW(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay)
    scaler = torch.amp.GradScaler("cuda", enabled=cfg.use_amp and device.type == "cuda")
    positive_weight = float((len(labels) - labels.sum()) / max(1.0, labels.sum()))
    criterion = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor([positive_weight], device=device))
    dataset = TensorDataset(torch.from_numpy(images), torch.from_numpy(geometry), torch.from_numpy(labels))
    start_epoch = 0
    history: list[dict[str, Any]] = []
    if last_path.is_file():
        payload = torch.load(last_path, map_location="cpu", weights_only=False)
        if payload.get("fingerprint") != cfg.fingerprint():
            raise RuntimeError(f"Incompatible final checkpoint: {last_path}")
        model.load_state_dict(payload["model_state"], strict=True)
        optimiser.load_state_dict(payload["optimizer_state"])
        scaler.load_state_dict(payload["scaler_state"])
        start_epoch = int(payload["epoch"]) + 1
        history = list(payload.get("history", []))
        restore_rng(payload)
    for epoch in range(start_epoch, cfg.epochs):
        check_stop(cfg)
        loader = DataLoader(
            dataset,
            batch_size=cfg.batch_size,
            shuffle=True,
            generator=torch.Generator().manual_seed(cfg.seed + 1000 + epoch),
            num_workers=0,
            pin_memory=device.type == "cuda",
        )
        model.train()
        total = 0.0
        seen = 0
        started = time.time()
        for batch_images, batch_geometry, batch_labels in loader:
            batch_images = augment_batch(batch_images.to(device=device, dtype=torch.float32, non_blocking=True))
            batch_geometry = batch_geometry.to(device=device, dtype=torch.float32, non_blocking=True)
            batch_labels = batch_labels.to(device=device, dtype=torch.float32, non_blocking=True)
            optimiser.zero_grad(set_to_none=True)
            with torch.autocast(
                device_type=device.type,
                dtype=torch.float16,
                enabled=cfg.use_amp and device.type == "cuda",
            ):
                logits = model(batch_images, batch_geometry).flatten()
                loss = criterion(logits, batch_labels)
            scaler.scale(loss).backward()
            scaler.step(optimiser)
            scaler.update()
            total += float(loss.item()) * len(batch_labels)
            seen += len(batch_labels)
        row = {"epoch": epoch + 1, "train_loss": total / max(1, seen), "seconds": time.time() - started}
        history.append(row)
        payload = {
            "version": 1,
            "experiment": EXPERIMENT,
            "fingerprint": cfg.fingerprint(),
            "fold": "all199",
            "epoch": epoch,
            "epochs_requested": cfg.epochs,
            "model_state": model.state_dict(),
            "optimizer_state": optimiser.state_dict(),
            "scaler_state": scaler.state_dict(),
            "geometry_dim": geometry.shape[1],
            "geometry_mean": geometry_mean,
            "geometry_std": geometry_std,
            "history": history,
            "initialisation": init_report,
            "positive_weight": positive_weight,
            **rng_payload(),
        }
        atomic_torch(last_path, payload)
        atomic_json(final_dir / "history.json", history)
        print(f"final all199 epoch {epoch + 1}/{cfg.epochs}: loss={row['train_loss']:.5f}", flush=True)
    return last_path


def package_final_model(cfg: B32Config, checkpoint: Path, winner: dict[str, Any]) -> Path:
    package = cfg.repo_root / "weights_dataset" / "friend_a_divpair"
    package.mkdir(parents=True, exist_ok=True)
    shutil.copy2(checkpoint, package / "model.pt")
    shutil.copy2(
        cfg.repo_root / "experiments" / EXPERIMENT / "divpair_infer.py",
        package / "divpair_infer.py",
    )
    params = {
        "experiment": EXPERIMENT,
        "winner": winner,
        "candidate_generator": {
            "parent_um": cfg.parent_um,
            "sister_min_um": cfg.sister_min_um,
            "sister_max_um": cfg.sister_max_um,
            "deepcenter_threshold": cfg.deepcenter_threshold,
            "orphan_only": True,
            "divergence_gate": False,
            "symmetry_gate": False,
        },
        "model": {
            "channels": 7,
            "image_lags": [-1, 0, 1, 2],
            "markers": ["parent", "daughter1", "daughter2"],
            "crop": [16, 32, 32],
            "pool_xy": 4,
            "epochs": cfg.epochs,
            "seed": cfg.seed,
        },
    }
    atomic_json(package / "params.json", params)
    return package


def run_pipeline(cfg: B32Config) -> dict[str, Any]:
    state = load_state(cfg)
    if not cfg.run_pipeline:
        print("BIOHUB_B32_RUN=0: preflight only", flush=True)
        return state
    state["status"] = "running"
    save_state(cfg, state)
    try:
        candidate_summary = build_candidates(cfg, state)
        print(
            f"STEP 1: {candidate_summary['candidates']} candidates, "
            f"{candidate_summary['positives']} positives, coverage={candidate_summary['coverage']:.1%}",
            flush=True,
        )
        build_train_samples(cfg, state)
        fold_reports = []
        for fold_name, train_prefix, validation_prefix in FOLDS:
            fold_reports.append(train_fold(cfg, fold_name, train_prefix, validation_prefix))
            state["stages"][fold_name] = True
            state.setdefault("folds", {})[fold_name] = fold_reports[-1]
            save_state(cfg, state)
            check_stop(cfg)
        oof_metrics = run_oof(cfg, state)
        control = load_control_metrics(cfg)
        results: list[dict[str, Any]] = []
        for threshold in THRESHOLDS:
            for cap_mode in CAP_MODES:
                results.append(pass2_variant(cfg, state, threshold, cap_mode))
                check_stop(cfg)
        report = build_final_report(cfg, control, results, oof_metrics)
        if report["winner"] is not None and len(cfg.stems) == 199:
            checkpoint = train_final_model(cfg)
            package = package_final_model(cfg, checkpoint, report["winner"])
            state["final_package"] = str(package)
        state["status"] = "complete"
        state["stages"]["complete"] = True
        state["report"] = report
        save_state(cfg, state)
        return state
    except StopRequested as exc:
        state["status"] = "stopped_safely"
        state["message"] = str(exc)
        save_state(cfg, state)
        print(f"\nSAFE STOP: {exc}\nRemove STOP_REQUESTED and Run All to resume.", flush=True)
        return state
    except KeyboardInterrupt:
        state["status"] = "stopped_safely"
        state["message"] = "KeyboardInterrupt"
        save_state(cfg, state)
        print("\nSAFE STOP: completed videos and epochs are reusable. Run All to resume.", flush=True)
        return state
    except Exception as exc:
        state["status"] = "failed"
        state["error"] = f"{type(exc).__name__}: {exc}"
        save_state(cfg, state)
        raise


def compact_status(cfg: B32Config) -> dict[str, Any]:
    state = load_state(cfg)
    status = {
        "status": state.get("status", "unknown"),
        "videos": len(cfg.stems),
        "candidates": sum(candidate_file_valid(cfg, candidate_path(cfg, stem)) for stem in cfg.stems),
        "train_samples": sum(sample_path(cfg, stem).is_file() for stem in cfg.stems),
        "oof": sum(oof_path(cfg, stem).is_file() for stem in cfg.stems),
        "folds": {
            fold_name: {
                "last": (cfg.output_dir / "folds" / fold_name / "last.pt").is_file(),
                "best": (cfg.output_dir / "folds" / fold_name / "best.pt").is_file(),
            }
            for fold_name, _, _ in FOLDS
        },
        "pass2_variants": sum(
            (
                cfg.output_dir
                / "results"
                / (f"divpair_t{threshold:.1f}_{cap_mode}".replace(".", "p") + ".json")
            ).is_file()
            for threshold in THRESHOLDS
            for cap_mode in CAP_MODES
        ),
        "stages": state.get("stages", {}),
        "stop_file": str(cfg.stop_file),
        "output_dir": str(cfg.output_dir),
    }
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return status
