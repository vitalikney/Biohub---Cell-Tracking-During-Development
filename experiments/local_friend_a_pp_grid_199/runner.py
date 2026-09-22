"""Resumable Friend A B33 post-processing grid on the fixed B20 raw cache.

The expensive unit is one (variant, video) pair.  Every completed GEFF gets an
atomic JSON marker, so Interrupt Kernel or ``STOP_REQUESTED`` loses at most the
current video.  The code executes the public notebook's own post-processing
cell; it does not reimplement its algorithms.
"""

from __future__ import annotations

import csv
import gc
import hashlib
import json
import os
import re
import shutil
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator


EXPERIMENT = "local_friend_a_pp_grid_199"
CACHE_TAG = "friend_a_b20_exp29"
EXPECTED_CONTROL_SCORE = 0.912027502438606
GATE_ALL = 0.003
GATE_EACH_EMBRYO = 0.002
MAX_NODE_RATIO = 1.005

# The realised exp29 submission selected tight55.  It must be explicit because
# exp29's source notebook still contains the pre-sweep 6.0 um default.
BASE_ENV = {"BIOHUB_MOTION_RELINK_TIGHT_UM": "5.5"}


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
    if isinstance(value, Path):
        return str(value)
    try:
        import numpy as np

        if isinstance(value, np.generic):
            return value.item()
    except Exception:
        pass
    return value


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def atomic_json(path: Path, payload: Any) -> None:
    atomic_text(path, json.dumps(jsonable(payload), ensure_ascii=False, indent=2))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def discover_data_dir(repo_root: Path) -> Path:
    explicit = os.environ.get("BIOHUB_DATA_DIR", "").strip()
    candidates = [Path(explicit)] if explicit else []
    candidates.extend(
        [
            repo_root.parent / "train",
            repo_root / "train",
            repo_root / "biohub-cell-tracking-during-development" / "train",
        ]
    )
    for candidate in candidates:
        if candidate.is_dir() and any(candidate.glob("*.zarr")):
            return candidate.resolve()
    raise FileNotFoundError("Set BIOHUB_DATA_DIR to the directory with 199 .zarr/.geff pairs")


@dataclass(frozen=True)
class Variant:
    name: str
    group: str
    overrides: dict[str, str]
    note: str
    use_divnet_notebook: bool = False


def registered_variants() -> list[Variant]:
    variants = [
        Variant("control", "control", {}, "realised exp29 control (tight55)"),
        Variant("relink_off", "relink", {"BIOHUB_OUTPUT_MOTION_RELINK": "0"}, "disable motion relink"),
        Variant("relink_tight_4p5", "relink", {"BIOHUB_MOTION_RELINK_TIGHT_UM": "4.5"}, "tight radius 4.5 um"),
        Variant("relink_tight_6p5", "relink", {"BIOHUB_MOTION_RELINK_TIGHT_UM": "6.5"}, "tight radius 6.5 um"),
        Variant("relink_relaxed_7", "relink", {"BIOHUB_MOTION_RELINK_RELAXED_UM": "7"}, "relaxed radius 7 um"),
        Variant("relink_relaxed_9", "relink", {"BIOHUB_MOTION_RELINK_RELAXED_UM": "9"}, "relaxed radius 9 um"),
        Variant("relink_bonus_0p5", "relink", {"BIOHUB_MOTION_RELINK_LEARNED_BONUS": "0.5"}, "learned bonus 0.5"),
        Variant("relink_bonus_1p5", "relink", {"BIOHUB_MOTION_RELINK_LEARNED_BONUS": "1.5"}, "learned bonus 1.5"),
        Variant("relink_bonus_2p5", "relink", {"BIOHUB_MOTION_RELINK_LEARNED_BONUS": "2.5"}, "learned bonus 2.5"),
    ]
    for weight in (0.5, 0.8, 1.0):
        for window in (1, 2, 3):
            if weight == 0.8 and window == 2:
                continue
            variants.append(
                Variant(
                    f"linefit_w{str(weight).replace('.', 'p')}_win{window}",
                    "linefit",
                    {
                        "BIOHUB_OUTPUT_LINEFIT_WEIGHT": str(weight),
                        "BIOHUB_OUTPUT_LINEFIT_WINDOW": str(window),
                    },
                    f"linefit weight {weight}, window {window}",
                )
            )
    variants.extend(
        [
            Variant("dc_gap_0p15", "deepcenter", {"BIOHUB_DEEPCENTER_GAP_THRESHOLD": "0.15"}, "gap DC 0.15"),
            Variant("dc_gap_0p35", "deepcenter", {"BIOHUB_DEEPCENTER_GAP_THRESHOLD": "0.35"}, "gap DC 0.35"),
            Variant("dc_div_0p25", "deepcenter", {"BIOHUB_DEEPCENTER_SAFE_DIV_THRESHOLD": "0.25"}, "division DC 0.25"),
            Variant("dc_div_0p30", "deepcenter", {"BIOHUB_DEEPCENTER_SAFE_DIV_THRESHOLD": "0.30"}, "division DC 0.30"),
            Variant("dc_gap_veto_off", "deepcenter", {"BIOHUB_DEEPCENTER_GAP_VETO": "0"}, "disable DC gap veto"),
            Variant("gap_close_4p5", "gaps", {"BIOHUB_GAP_CLOSE_UM": "4.5"}, "gap radius 4.5 um"),
            Variant("gap_close_5p5", "gaps", {"BIOHUB_GAP_CLOSE_UM": "5.5"}, "gap radius 5.5 um"),
            Variant("gap_max_1", "gaps", {"BIOHUB_GAP_CLOSE_MAX_GAP": "1"}, "one-frame gaps only"),
            Variant("gap2_step_4", "gaps", {"BIOHUB_GAP2_MAX_STEP_UM": "4.0"}, "gap2 max step 4 um"),
            Variant("gap_reuse_2p8", "gaps", {"BIOHUB_GAP_CLOSE_REUSE_UM": "2.8"}, "gap reuse 2.8 um"),
            Variant("gap_density_0", "gaps", {"BIOHUB_GAP_DENSITY_GAIN": "0"}, "disable density gain"),
            Variant("gap_density_0p08", "gaps", {"BIOHUB_GAP_DENSITY_GAIN": "0.08"}, "density gain 0.08"),
            Variant("short_min_5", "short_tracks", {"BIOHUB_OUTPUT_MIN_TRACK_LEN": "5"}, "minimum track 5"),
            Variant("short_min_7", "short_tracks", {"BIOHUB_OUTPUT_MIN_TRACK_LEN": "7"}, "minimum track 7"),
            Variant("short_rescue_off", "short_tracks", {"BIOHUB_ADAPTIVE_SHORT_TRACK_RESCUE": "0"}, "disable rescue"),
            Variant("short_prob_0p85", "short_tracks", {"BIOHUB_SHORT_TRACK_RESCUE_MIN_MEAN_EDGE_PROB": "0.85"}, "rescue p 0.85"),
            Variant("short_prob_0p92", "short_tracks", {"BIOHUB_SHORT_TRACK_RESCUE_MIN_MEAN_EDGE_PROB": "0.92"}, "rescue p 0.92"),
            Variant("div_frame_half", "divisions", {"BIOHUB_SAFE_DIV_FRAME_FRAC_CAP": "0.0038"}, "half frame cap"),
            Variant("div_frame_double", "divisions", {"BIOHUB_SAFE_DIV_FRAME_FRAC_CAP": "0.0152"}, "double frame cap"),
            Variant("div_global_half", "divisions", {"BIOHUB_SAFE_DIV_GLOBAL_FRAC_CAP": "0.001875"}, "half global cap"),
            Variant("div_global_double", "divisions", {"BIOHUB_SAFE_DIV_GLOBAL_FRAC_CAP": "0.0075"}, "double global cap"),
            Variant("div_max_8", "divisions", {"BIOHUB_SAFE_DIV_MAX_UM": "8"}, "division radius 8 um"),
            Variant("div_max_10", "divisions", {"BIOHUB_SAFE_DIV_MAX_UM": "10"}, "division radius 10 um"),
            Variant("div_symmetry_off", "divisions", {"BIOHUB_SAFE_DIV_SISTER_SYMMETRY_TAU": "0"}, "disable symmetry"),
            Variant("div_diverge_off", "divisions", {"BIOHUB_SAFE_DIV_DIVERGE_UM": "0"}, "disable divergence"),
            Variant("divnet_veto_on", "divisions", {"BIOHUB_DIVNET_VERIFY": "1"}, "exp39 DivNet veto", True),
            Variant("edge_max_12", "edge_filter", {"BIOHUB_OUTPUT_EDGE_MAX_UM": "12"}, "edge max 12 um"),
            Variant("edge_max_15", "edge_filter", {"BIOHUB_OUTPUT_EDGE_MAX_UM": "15"}, "edge max 15 um"),
        ]
    )
    return variants


@dataclass
class B33Config:
    repo_root: Path
    data_dir: Path
    raw_dir: Path
    output_dir: Path
    weights_root: Path
    exp29_notebook: Path
    exp39_notebook: Path
    divnet_checkpoint: Path
    run_pipeline: bool = True
    max_videos: int = 0
    max_variants: int = 0
    requested_variants: tuple[str, ...] = ()

    @classmethod
    def from_environment(cls, repo_root: Path) -> "B33Config":
        repo_root = Path(repo_root).resolve()
        data_dir = discover_data_dir(repo_root)
        base_output = Path(
            os.environ.get("BIOHUB_B33_OUTPUT_DIR", repo_root.parent / "outputs" / EXPERIMENT)
        ).resolve()
        max_videos = int(os.environ.get("BIOHUB_B33_MAX_VIDEOS", "0"))
        if max_videos and "BIOHUB_B33_OUTPUT_DIR" not in os.environ:
            base_output = base_output / f"smoke_{max_videos}"
        cache_root = Path(
            os.environ.get(
                "BIOHUB_B33_B20_CACHE",
                repo_root.parent / "outputs" / "local_friend_a_b20_divnet" / "cache" / CACHE_TAG,
            )
        ).resolve()
        requested = tuple(
            value.strip()
            for value in os.environ.get("BIOHUB_B33_VARIANTS", "").split(",")
            if value.strip()
        )
        return cls(
            repo_root=repo_root,
            data_dir=data_dir,
            raw_dir=cache_root / "raw",
            output_dir=base_output,
            weights_root=Path(
                os.environ.get("BIOHUB_WEIGHTS_ROOT", repo_root.parent / "biohub_weights")
            ).resolve(),
            exp29_notebook=repo_root / "experiments" / "exp29_sjlee947_verbatim" / "exp29-sjlee947-verbatim.ipynb",
            exp39_notebook=repo_root / "experiments" / "exp39_sjlee947_tight55_divnetveto" / "exp39-sjlee947-tight55-divnetveto.ipynb",
            divnet_checkpoint=repo_root / "external" / "giorgosi__biohub-divnet-v2" / "best_overall.pt",
            run_pipeline=truthy(os.environ.get("BIOHUB_B33_RUN"), True),
            max_videos=max_videos,
            max_variants=int(os.environ.get("BIOHUB_B33_MAX_VARIANTS", "0")),
            requested_variants=requested,
        )

    @property
    def all_stems(self) -> list[str]:
        raw = {path.stem for path in self.raw_dir.glob("*.geff")}
        gt = {path.stem for path in self.data_dir.glob("*.geff")}
        images = {path.stem for path in self.data_dir.glob("*.zarr")}
        return sorted(raw & gt & images)

    @property
    def stems(self) -> list[str]:
        stems = self.all_stems
        if not self.max_videos:
            return stems
        each = max(1, self.max_videos // 2)
        selected = [stem for stem in stems if stem.startswith("44b6")][:each]
        selected += [stem for stem in stems if stem.startswith("6bba")][:each]
        return sorted(selected[: self.max_videos])

    @property
    def variants(self) -> list[Variant]:
        variants = registered_variants()
        by_name = {variant.name: variant for variant in variants}
        if self.requested_variants:
            missing = sorted(set(self.requested_variants) - set(by_name))
            if missing:
                raise ValueError(f"Unknown BIOHUB_B33_VARIANTS: {missing}")
            variants = [by_name[name] for name in self.requested_variants]
            if "control" not in self.requested_variants:
                variants.insert(0, by_name["control"])
        if self.max_variants:
            variants = variants[: self.max_variants]
        return variants

    @property
    def stop_file(self) -> Path:
        return self.output_dir / "STOP_REQUESTED"

    def serialisable(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in (
            "repo_root",
            "data_dir",
            "raw_dir",
            "output_dir",
            "weights_root",
            "exp29_notebook",
            "exp39_notebook",
            "divnet_checkpoint",
        ):
            payload[key] = str(payload[key])
        payload["selected_videos"] = len(self.stems)
        payload["selected_variants"] = [variant.name for variant in self.variants]
        return payload


def clear_stop(cfg: B33Config) -> None:
    cfg.stop_file.unlink(missing_ok=True)


def request_stop(cfg: B33Config) -> Path:
    cfg.stop_file.parent.mkdir(parents=True, exist_ok=True)
    cfg.stop_file.write_text("Stop after the current video.\n", encoding="utf-8")
    return cfg.stop_file


def check_stop(cfg: B33Config) -> None:
    if cfg.stop_file.is_file():
        raise StopRequested(f"Stop requested via {cfg.stop_file}")


def install_import_paths(cfg: B33Config) -> None:
    for path in (cfg.repo_root, cfg.repo_root / "tools"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def variant_fingerprint(cfg: B33Config, variant: Variant) -> str:
    notebook = cfg.exp39_notebook if variant.use_divnet_notebook else cfg.exp29_notebook
    payload = {
        "version": 1,
        "variant": asdict(variant),
        "base_env": BASE_ENV,
        "notebook_sha256": sha256_file(notebook),
        "stems": cfg.stems,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def marker_path(cfg: B33Config, variant: Variant, stem: str) -> Path:
    return cfg.output_dir / "completed" / variant.name / f"{stem}.json"


def prediction_path(cfg: B33Config, variant: Variant, stem: str) -> Path:
    return cfg.output_dir / "predictions" / variant.name / f"{stem}.geff"


def marker_valid(cfg: B33Config, variant: Variant, stem: str) -> bool:
    marker = marker_path(cfg, variant, stem)
    prediction = prediction_path(cfg, variant, stem)
    if not marker.is_file() or not prediction.is_dir():
        return False
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
        return payload.get("fingerprint") == variant_fingerprint(cfg, variant)
    except Exception:
        return False


def _remove_inside(path: Path, root: Path) -> None:
    resolved = path.resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    if resolved == root_resolved or root_resolved not in resolved.parents:
        raise RuntimeError(f"Refusing to remove path outside {root_resolved}: {resolved}")
    if resolved.is_dir():
        shutil.rmtree(resolved)
    elif resolved.exists():
        resolved.unlink()


@contextmanager
def isolated_biohub_environment(overrides: dict[str, str]) -> Iterator[None]:
    before = {key: value for key, value in os.environ.items() if key.startswith("BIOHUB_")}
    try:
        # Remove sweep knobs inherited from an earlier notebook session.
        sweep_keys = set(BASE_ENV)
        for variant in registered_variants():
            sweep_keys.update(variant.overrides)
        for key in sweep_keys:
            os.environ.pop(key, None)
        os.environ.update(BASE_ENV)
        os.environ.update(overrides)
        yield
    finally:
        for key in [key for key in os.environ if key.startswith("BIOHUB_")]:
            os.environ.pop(key, None)
        os.environ.update(before)


def prepare_namespace(cfg: B33Config, variant: Variant) -> dict[str, Any]:
    install_import_paths(cfg)
    import public_local as pl

    notebook = cfg.exp39_notebook if variant.use_divnet_notebook else cfg.exp29_notebook
    cells = pl.notebook_cells(notebook)
    work = cfg.output_dir / "work" / variant.name
    work.mkdir(parents=True, exist_ok=True)
    repo, _ = pl.materialise_repo(cfg.weights_root, work, None, None, materialise_code=False)
    if variant.use_divnet_notebook:
        os.environ["BIOHUB_DIVNET_CHECKPOINT"] = str(cfg.divnet_checkpoint)
    namespace = pl.build_namespace(cells, repo, work, cfg.data_dir)
    if variant.use_divnet_notebook:
        divnet_index = pl.find_cell(cells, "exp39: DivNet parent veto", "class DivNetMitosisClassifier")
        exec(compile(cells[divnet_index], "<exp39:divnet>", "exec"), namespace)
    pl.load_postproc(cells, namespace)
    if namespace.get("DEEPCENTER_VETO_DETECTOR") is None:
        namespace["DEEPCENTER_VETO_DETECTOR"] = namespace["load_deepcenter_veto_detector"]()
    return namespace


def process_one(cfg: B33Config, variant: Variant, stem: str, namespace: dict[str, Any]) -> dict[str, Any]:
    install_import_paths(cfg)
    import networkx as nx
    import postproc as pp_io

    raw_path = cfg.raw_dir / f"{stem}.geff"
    output = prediction_path(cfg, variant, stem)
    marker = marker_path(cfg, variant, stem)
    output.parent.mkdir(parents=True, exist_ok=True)
    marker.parent.mkdir(parents=True, exist_ok=True)
    temporary = cfg.output_dir / "temporary" / variant.name / f"{stem}.geff"
    temporary.parent.mkdir(parents=True, exist_ok=True)
    if temporary.exists():
        _remove_inside(temporary, cfg.output_dir)

    graph = namespace["graph_from_geff"](raw_path)
    nodes_by_id: dict[int, dict[str, Any]] = {}
    for row in graph.node_attrs().iter_rows(named=True):
        node_id = int(row["node_id"])
        nodes_by_id[node_id] = {
            "node_id": node_id,
            "t": int(row["t"]),
            "z": float(row["z"]),
            "y": float(row["y"]),
            "x": float(row["x"]),
        }
    raw_edges = []
    for row in graph.edge_attrs().iter_rows(named=True):
        edge_probability = row.get("edge_prob") if hasattr(row, "get") else None
        raw_edges.append(
            {
                "source_id": int(row["source_id"]),
                "target_id": int(row["target_id"]),
                "edge_prob": None if edge_probability is None else float(edge_probability),
            }
        )
    raw_nodes = len(nodes_by_id)
    started = time.time()
    nodes_by_id, edges, stats = namespace["filter_output_graph"](
        nodes_by_id,
        raw_edges,
        dataset=stem,
        deepcenter_bundle=namespace.get("DEEPCENTER_VETO_DETECTOR"),
    )
    prediction = nx.DiGraph()
    for node_id, node in nodes_by_id.items():
        prediction.add_node(
            int(node_id),
            t=int(node["t"]),
            z=float(max(0, round(float(node["z"])))),
            y=float(max(0, round(float(node["y"])))),
            x=float(max(0, round(float(node["x"])))),
        )
    for edge in edges:
        prediction.add_edge(int(edge["source_id"]), int(edge["target_id"]))
    pp_io.save(prediction, temporary)
    # A read-back catches interrupted/corrupt GEFF stores before the completion marker exists.
    import tracksdata as td

    loaded = td.graph.IndexedRXGraph.from_geff(temporary)
    loaded = loaded[0] if isinstance(loaded, tuple) else loaded
    if int(loaded.num_nodes()) != len(nodes_by_id) or int(loaded.num_edges()) != len(edges):
        raise RuntimeError(f"GEFF read-back mismatch for {variant.name}/{stem}")
    if output.exists():
        _remove_inside(output, cfg.output_dir)
    os.replace(temporary, output)
    row = {
        "variant": variant.name,
        "dataset": stem,
        "embryo": stem.split("_", 1)[0],
        "fingerprint": variant_fingerprint(cfg, variant),
        "raw_nodes": raw_nodes,
        "nodes": len(nodes_by_id),
        "raw_edges": int(stats.get("raw_edges", len(raw_edges))),
        "edges": len(edges),
        "safe_divisions_added": int(stats.get("safe_divisions_added", 0)),
        "gap_added_nodes": int(stats.get("gap_added_nodes", 0)),
        "short_track_nodes_removed": int(stats.get("short_track_nodes_removed", 0)),
        "seconds": time.time() - started,
    }
    atomic_json(marker, row)
    return row


def score_paths(cfg: B33Config, paths: list[Path]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    install_import_paths(cfg)
    os.environ["BIOHUB_DATA_DIR"] = str(cfg.data_dir)
    import score_geffs

    score_geffs.DATA = cfg.data_dir
    return score_geffs.score(paths, quiet=True)


def score_variant(cfg: B33Config, variant: Variant) -> dict[str, Any]:
    paths = [prediction_path(cfg, variant, stem) for stem in cfg.stems]
    if not all(path.is_dir() for path in paths):
        raise RuntimeError(f"Cannot score incomplete variant {variant.name}")
    metrics: dict[str, Any] = {}
    metric_rows: dict[str, Any] = {}
    for group in ("all", "44b6", "6bba"):
        subset = paths if group == "all" else [path for path in paths if path.stem.startswith(group)]
        if not subset:
            continue
        metrics[group], metric_rows[group] = score_paths(cfg, subset)
    completion_rows = [
        json.loads(marker_path(cfg, variant, stem).read_text(encoding="utf-8")) for stem in cfg.stems
    ]
    nodes_by_embryo = {
        embryo: sum(int(row["nodes"]) for row in completion_rows if row["embryo"] == embryo)
        for embryo in ("44b6", "6bba")
    }
    result = {
        "variant": variant.name,
        "group": variant.group,
        "note": variant.note,
        "overrides": {**BASE_ENV, **variant.overrides},
        "videos": len(paths),
        "nodes": sum(int(row["nodes"]) for row in completion_rows),
        "nodes_by_embryo": nodes_by_embryo,
        "raw_nodes": sum(int(row["raw_nodes"]) for row in completion_rows),
        "seconds": sum(float(row["seconds"]) for row in completion_rows),
        "metrics": metrics,
        "metric_rows": metric_rows,
    }
    atomic_json(cfg.output_dir / "results" / "variants" / f"{variant.name}.json", result)
    return result


def load_variant_result(cfg: B33Config, variant: Variant) -> dict[str, Any] | None:
    path = cfg.output_dir / "results" / "variants" / f"{variant.name}.json"
    if not path.is_file():
        return None
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
        if int(result.get("videos", 0)) != len(cfg.stems):
            return None
        return result
    except Exception:
        return None


def compact_row(result: dict[str, Any], control: dict[str, Any]) -> dict[str, Any]:
    control_nodes = max(1, int(control["nodes"]))
    row: dict[str, Any] = {
        "variant": result["variant"],
        "group": result["group"],
        "settings": " ".join(f"{key}={value}" for key, value in result["overrides"].items()),
        "videos": result["videos"],
        "nodes": result["nodes"],
        "node_ratio_vs_control": float(result["nodes"] / control_nodes),
        "hours": float(result["seconds"] / 3600.0),
    }
    result_nodes_by_embryo = result.get("nodes_by_embryo", {})
    control_nodes_by_embryo = control.get("nodes_by_embryo", {})
    for embryo in ("44b6", "6bba"):
        denominator = max(1, int(control_nodes_by_embryo.get(embryo, 0)))
        row[f"{embryo}_node_ratio"] = float(
            int(result_nodes_by_embryo.get(embryo, 0)) / denominator
        )
    for group in ("all", "44b6", "6bba"):
        if group not in result["metrics"]:
            continue
        metric = result["metrics"][group]
        baseline = control["metrics"][group]
        row[f"{group}_score"] = metric["score"]
        row[f"{group}_delta"] = metric["score"] - baseline["score"]
        row[f"{group}_adj_edge"] = metric["adj_edge_jaccard"]
        row[f"{group}_div_tp"] = int(metric["division_tp"])
        row[f"{group}_div_fp"] = int(metric["division_fp"])
        row[f"{group}_div_fn"] = int(metric["division_fn"])
    row["passes_gate"] = bool(
        row.get("all_delta", float("-inf")) >= GATE_ALL
        and row.get("44b6_delta", float("-inf")) >= GATE_EACH_EMBRYO
        and row.get("6bba_delta", float("-inf")) >= GATE_EACH_EMBRYO
        and row["node_ratio_vs_control"] <= MAX_NODE_RATIO
    )
    if result["variant"] == "control":
        row["passes_gate"] = False
    return row


def write_grid(cfg: B33Config) -> list[dict[str, Any]]:
    variants = registered_variants()
    results = {variant.name: load_variant_result(cfg, variant) for variant in variants}
    control = results.get("control")
    if control is None:
        return []
    rows = [compact_row(result, control) for result in results.values() if result is not None]
    rows.sort(key=lambda row: (not row["passes_gate"], -float(row.get("all_delta", -999)), row["variant"]))
    fields = [
        "variant", "group", "settings", "videos", "nodes", "node_ratio_vs_control", "hours",
        "all_score", "all_delta", "all_adj_edge", "all_div_tp", "all_div_fp", "all_div_fn",
        "44b6_score", "44b6_delta", "44b6_node_ratio", "44b6_adj_edge", "44b6_div_tp", "44b6_div_fp", "44b6_div_fn",
        "6bba_score", "6bba_delta", "6bba_node_ratio", "6bba_adj_edge", "6bba_div_tp", "6bba_div_fp", "6bba_div_fn",
        "passes_gate",
    ]
    csv_path = cfg.output_dir / "results" / "grid.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = csv_path.with_name(csv_path.name + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, csv_path)
    lines = [
        "# Friend A B33 — post-processing grid",
        "",
        f"Control expected: `{EXPECTED_CONTROL_SCORE:.10f}`. Gates: all +{GATE_ALL:.3f}, each embryo +{GATE_EACH_EMBRYO:.3f}, nodes <= {MAX_NODE_RATIO:.3f}x.",
        "",
        "| variant | all | delta | 44b6 delta | 6bba delta | nodes all/44b6/6bba | divisions TP/FP/FN | gate |",
        "|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in rows:
        lines.append(
            "| {variant} | {all_score:.5f} | {all_delta:+.5f} | {d44:+.5f} | {d6:+.5f} | {ratio:.5f}/{r44:.5f}/{r6:.5f} | {tp}/{fp}/{fn} | {gate} |".format(
                variant=row["variant"],
                all_score=float(row.get("all_score", float("nan"))),
                all_delta=float(row.get("all_delta", float("nan"))),
                d44=float(row.get("44b6_delta", float("nan"))),
                d6=float(row.get("6bba_delta", float("nan"))),
                ratio=float(row["node_ratio_vs_control"]),
                r44=float(row["44b6_node_ratio"]),
                r6=float(row["6bba_node_ratio"]),
                tp=int(row.get("all_div_tp", 0)),
                fp=int(row.get("all_div_fp", 0)),
                fn=int(row.get("all_div_fn", 0)),
                gate="YES" if row["passes_gate"] else "no",
            )
        )
    atomic_text(cfg.output_dir / "results" / "grid.md", "\n".join(lines) + "\n")
    return rows


def preflight(cfg: B33Config) -> dict[str, Any]:
    install_import_paths(cfg)
    errors: list[str] = []
    for path, label in (
        (cfg.raw_dir, "B20 raw cache"),
        (cfg.data_dir, "training data"),
        (cfg.exp29_notebook, "exp29 notebook"),
        (cfg.exp39_notebook, "exp39 notebook"),
    ):
        if not path.exists():
            errors.append(f"missing {label}: {path}")
    if len(cfg.all_stems) != 199:
        errors.append(f"expected 199 raw/image/GT triples, found {len(cfg.all_stems)}")
    if any(variant.use_divnet_notebook for variant in cfg.variants) and not cfg.divnet_checkpoint.is_file():
        errors.append(f"missing DivNet checkpoint: {cfg.divnet_checkpoint}")
    # Guard against the easy no-op: public_local does not add BIOHUB_ itself.
    for variant in registered_variants():
        for key in variant.overrides:
            if not key.startswith("BIOHUB_"):
                errors.append(f"unprefixed override {variant.name}: {key}")
    if errors:
        raise RuntimeError("B33 preflight failed:\n- " + "\n- ".join(errors))
    result = {
        "videos": len(cfg.stems),
        "full_dataset_videos": len(cfg.all_stems),
        "variants": len(cfg.variants),
        "raw_dir": str(cfg.raw_dir),
        "data_dir": str(cfg.data_dir),
        "output_dir": str(cfg.output_dir),
        "first_variants": [variant.name for variant in cfg.variants[:5]],
        "stop_file": str(cfg.stop_file),
    }
    atomic_json(cfg.output_dir / "preflight.json", result)
    return result


def run_pipeline(cfg: B33Config) -> dict[str, Any]:
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    state_path = cfg.output_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {"version": 1}
    state.update({"status": "running", "config": cfg.serialisable(), "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
    atomic_json(state_path, state)
    if not cfg.run_pipeline:
        state["status"] = "preflight_only"
        atomic_json(state_path, state)
        return state
    try:
        for variant_index, variant in enumerate(cfg.variants, start=1):
            check_stop(cfg)
            complete = sum(marker_valid(cfg, variant, stem) for stem in cfg.stems)
            print(f"\nVARIANT [{variant_index}/{len(cfg.variants)}] {variant.name}: {complete}/{len(cfg.stems)} cached", flush=True)
            if complete < len(cfg.stems):
                with isolated_biohub_environment(variant.overrides):
                    namespace = prepare_namespace(cfg, variant)
                    try:
                        for video_index, stem in enumerate(cfg.stems, start=1):
                            if marker_valid(cfg, variant, stem):
                                continue
                            check_stop(cfg)
                            print(f"  [{video_index}/{len(cfg.stems)}] {stem}", flush=True)
                            process_one(cfg, variant, stem, namespace)
                    finally:
                        namespace.clear()
                        gc.collect()
                        try:
                            import torch

                            if torch.cuda.is_available():
                                torch.cuda.empty_cache()
                        except Exception:
                            pass
            result = score_variant(cfg, variant)
            state.setdefault("variants", {})[variant.name] = {
                "status": "complete",
                "score": result["metrics"]["all"]["score"],
                "nodes": result["nodes"],
            }
            state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            atomic_json(state_path, state)
            write_grid(cfg)
        rows = write_grid(cfg)
        state["status"] = "complete"
        state["passing_variants"] = [row["variant"] for row in rows if row["passes_gate"]]
        state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        atomic_json(state_path, state)
        return state
    except (StopRequested, KeyboardInterrupt) as exc:
        state["status"] = "stopped_safely"
        state["message"] = str(exc) or "KeyboardInterrupt"
        state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        atomic_json(state_path, state)
        print("SAFE STOP: completed video markers are reusable.", flush=True)
        return state
    except Exception as exc:
        state["status"] = "failed"
        state["error"] = f"{type(exc).__name__}: {exc}"
        state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        atomic_json(state_path, state)
        raise


def compact_status(cfg: B33Config) -> dict[str, Any]:
    state_path = cfg.output_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
    return {
        "status": state.get("status", "new"),
        "videos": len(cfg.stems),
        "variants": {
            variant.name: sum(marker_valid(cfg, variant, stem) for stem in cfg.stems)
            for variant in cfg.variants
        },
        "grid": str(cfg.output_dir / "results" / "grid.md"),
        "stop_file": str(cfg.stop_file),
    }
