"""Friend A L5 DaughterNet-B: resumable local training and OOF scoring on an RTX 5070 Ti.

The label definitions, real-pool hard examples, leak-safe folds, optimiser and readout are inherited from L2 v2.
L5 changes only the registered input view: full XY resolution, 16x64x64 crops, lags -2..+3, and therefore six
image channels plus one centre marker.  Crop tensors stay in a float16 memmap and are streamed to the GPU so a
single 16 GB card never has to hold the roughly 25 GiB v2 cache.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.l2_daughternet.kdn_train import kdn_core as K  # noqa: E402
from tools.daughternet import load_daughternet, prepare_sample  # noqa: E402

EXPERIMENT = "local_friend_a_l5_daughternet_b"
PROFILE = "friend_a_l5_fullres"
REQUIRED_COORD_COLUMNS = ("stem", "node_id", "t", "z", "y", "x")
OUTPUT_COLUMNS = ("stem", "node_id", "fold", "p_cont", "p_par", "p_dau")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    os.replace(temporary, path)


def _discover_data_dir(repo_root: Path) -> Path:
    explicit = os.environ.get("BIOHUB_DATA_DIR", "").strip()
    candidates = [Path(explicit)] if explicit else []
    candidates.extend((repo_root.parent / "train", repo_root / "train"))
    for candidate in candidates:
        if candidate.is_dir() and next(candidate.glob("*.zarr"), None) and next(candidate.glob("*.geff"), None):
            return candidate.resolve()
    raise FileNotFoundError("Set BIOHUB_DATA_DIR to the Biohub train directory")


@dataclass
class L5Config:
    repo_root: Path
    data_dir: Path
    work_dir: Path
    splits_path: Path
    coords_path: Path
    pool_samples_path: Path
    final_oof_path: Path
    epochs: int = 30
    patience: int = 6
    batch: int = 4
    eval_batch: int = 64
    lr: float = 1e-3
    build_workers: int = 2
    score_batch: int = 64

    @classmethod
    def from_environment(cls, repo_root: Path) -> "L5Config":
        repo_root = Path(repo_root).resolve()
        default_work = repo_root.parent / "outputs" / EXPERIMENT / "active_v2_pool"
        experiment_dir = repo_root / "experiments" / EXPERIMENT
        return cls(
            repo_root=repo_root,
            data_dir=_discover_data_dir(repo_root),
            work_dir=Path(os.environ.get("BIOHUB_L5_OUTPUT_DIR", default_work)).resolve(),
            splits_path=repo_root / "experiments" / "l2_daughternet" / "splits.json",
            coords_path=repo_root / "experiments" / "l2_daughternet" / "coords_exp39.parquet",
            pool_samples_path=repo_root / "experiments" / "l2_daughternet" / "pool_samples.parquet",
            final_oof_path=experiment_dir / "oof_nodes.parquet",
            epochs=int(os.environ.get("BIOHUB_L5_EPOCHS", "30")),
            patience=int(os.environ.get("BIOHUB_L5_PATIENCE", "6")),
            batch=int(os.environ.get("BIOHUB_L5_BATCH", "4")),
            eval_batch=int(os.environ.get("BIOHUB_L5_EVAL_BATCH", "64")),
            lr=float(os.environ.get("BIOHUB_L5_LR", "1e-3")),
            build_workers=int(os.environ.get("BIOHUB_L5_BUILD_WORKERS", "2")),
            score_batch=int(os.environ.get("BIOHUB_L5_SCORE_BATCH", "64")),
        )

    @property
    def cache_dir(self) -> Path:
        return self.work_dir / "cache"

    @property
    def stop_file(self) -> Path:
        return self.work_dir / "STOP_REQUESTED"

    @property
    def score_stop_file(self) -> Path:
        return self.work_dir / "STOP_SCORING"

    @property
    def predictions_dir(self) -> Path:
        return self.work_dir / "node_predictions"

    def serialisable(self) -> dict[str, Any]:
        return {key: str(value) if isinstance(value, Path) else value for key, value in asdict(self).items()}


def _fold_map(path: Path) -> dict[str, int]:
    value = K.load_splits(path)
    if value is None:
        raise RuntimeError(f"Unsupported splits format: {path}")
    return value


def preflight(cfg: L5Config) -> dict[str, Any]:
    import pandas as pd
    import torch

    K.configure_profile({"profile": PROFILE})
    missing = [path for path in (cfg.splits_path, cfg.coords_path, cfg.pool_samples_path) if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing registered L5 inputs: {missing}")
    splits = _fold_map(cfg.splits_path)
    if len(splits) != 199 or sorted(set(splits.values())) != list(range(5)):
        raise RuntimeError(f"Expected 199 stems in five registered folds, got {len(splits)} / {sorted(set(splits.values()))}")
    coords = pd.read_parquet(cfg.coords_path, columns=list(REQUIRED_COORD_COLUMNS))
    absent = sorted(set(REQUIRED_COORD_COLUMNS) - set(coords.columns))
    if absent or len(coords) != 1_012_255:
        raise RuntimeError(f"Coordinate export mismatch: rows={len(coords)}, missing={absent}")
    coord_stems = set(coords["stem"].astype(str).unique())
    if coord_stems != set(splits):
        raise RuntimeError(f"Coordinate/split stems differ: only coords={sorted(coord_stems - set(splits))[:3]}, "
                           f"only splits={sorted(set(splits) - coord_stems)[:3]}")
    duplicate_keys = int(coords.duplicated(["stem", "node_id"]).sum())
    if duplicate_keys:
        raise RuntimeError(f"Coordinate export contains {duplicate_keys} duplicate (stem,node_id) keys")
    pool = pd.read_parquet(cfg.pool_samples_path)
    pool_required = {"stem", "t", "z", "y", "x", "label"}
    if not pool_required.issubset(pool.columns) or len(pool) != 11_238:
        raise RuntimeError(f"L2 v2 pool-sample mismatch: rows={len(pool)}, columns={sorted(pool.columns)}")
    if not torch.cuda.is_available():
        raise RuntimeError("L5 full run requires CUDA")
    model = K.build_model(K.DEFAULT_CFG).cuda().eval()
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.float16):
        probe = model(torch.zeros((1, 7, 16, 64, 64), device="cuda"))
    del model, probe
    torch.cuda.empty_cache()
    cfg.work_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "ready",
        "gpu": torch.cuda.get_device_name(0),
        "cuda_gib": round(torch.cuda.get_device_properties(0).total_memory / 2**30, 2),
        "videos": len(splits),
        "fold_counts": {str(f): sum(v == f for v in splits.values()) for f in range(5)},
        "coordinate_rows": len(coords),
        "splits_sha256": _sha256(cfg.splits_path),
        "coords_sha256": _sha256(cfg.coords_path),
        "pool_samples": len(pool),
        "pool_samples_sha256": _sha256(cfg.pool_samples_path),
        "profile": PROFILE,
        "input": K.DEFAULT_CFG["input"],
        "model": K.DEFAULT_CFG["model"],
        "work_dir": str(cfg.work_dir),
        "final_oof_path": str(cfg.final_oof_path),
        "stop_file": str(cfg.stop_file),
        "score_stop_file": str(cfg.score_stop_file),
    }
    _atomic_json(cfg.work_dir / "preflight.json", result)
    return result


def _kdn_config(cfg: L5Config, *, smoke: bool) -> dict[str, Any]:
    work = cfg.work_dir / "smoke" if smoke else cfg.work_dir
    cache = work / "cache"
    result = K.config_from_env(
        {
            "profile": PROFILE,
            "run_name": "biohub-friend-a-l5-daughternet-b",
            "smoke": smoke,
            "data_dir": str(cfg.data_dir),
            "work_dir": str(work),
            "cache_dir": str(cache),
            "splits_path": str(cfg.splits_path),
            "extra_samples": str(cfg.pool_samples_path),
            "pool_weight": 1.0,
            "dedup_vox": 1.0,
            "es_source": "all",
            "stems": [],
            "max_videos": 0,
            "smoke_videos": 6,
            "n_folds": 2 if smoke else 5,
            "epochs": 1 if smoke else cfg.epochs,
            "patience": 2 if smoke else cfg.patience,
            "batch": min(2, cfg.batch) if smoke else cfg.batch,
            "eval_batch": min(4, cfg.eval_batch) if smoke else cfg.eval_batch,
            "lr": cfg.lr,
            "epoch_samples": 24 if smoke else 0,
            "build_workers": 1 if smoke else cfg.build_workers,
            "contract_checks": 2,
            "cache_dtype": "float16",
            "amp": True,
            "gpus": 1,
            "inner_val": False,
            "divnet_compare": False,
            "keep_cache": True,
            "stream_crops": True,
            "resume": True,
            "stop_file": str(work / "STOP_REQUESTED"),
        }
    )
    K.configure_profile(result)
    return result


def _run_training(cfg: L5Config, *, smoke: bool) -> dict[str, Any]:
    run_cfg = _kdn_config(cfg, smoke=smoke)
    work = Path(run_cfg["work_dir"])
    work.mkdir(parents=True, exist_ok=True)
    contract = {
        "profile": PROFILE,
        "splits_sha256": _sha256(cfg.splits_path),
        "pool_samples_sha256": _sha256(cfg.pool_samples_path),
        "epochs": run_cfg["epochs"],
        "patience": run_cfg["patience"],
        "batch": run_cfg["batch"],
        "eval_batch": run_cfg["eval_batch"],
        "lr": run_cfg["lr"],
        "epoch_samples": run_cfg["epoch_samples"],
        "pool_weight": run_cfg["pool_weight"],
        "dedup_vox": run_cfg["dedup_vox"],
        "es_source": run_cfg["es_source"],
        "n_folds": run_cfg["n_folds"],
    }
    contract_path = work / "run_contract.json"
    if contract_path.is_file():
        previous_contract = json.loads(contract_path.read_text(encoding="utf-8"))
        if previous_contract != contract:
            raise RuntimeError(
                f"Resume contract changed in {work}; keep the old run intact and set BIOHUB_L5_OUTPUT_DIR "
                "to a new directory"
            )
    else:
        existing_artifacts = (work / "cache" / "crops.npy").is_file() or (work / "folds").is_dir()
        if existing_artifacts:
            raise RuntimeError(f"Unversioned L5 artifacts exist in {work}; use a new BIOHUB_L5_OUTPUT_DIR")
        _atomic_json(contract_path, contract)
    state = K.step_prepare(run_cfg)
    if "error" in state["stats"]:
        graph_failures = state["stats"][state["stats"]["error"].notna()]
        if len(graph_failures):
            raise RuntimeError(f"GT parsing failed for {len(graph_failures)} videos; refusing an incomplete L5 run")
    state = K.step_build_cache(run_cfg, state)
    valid = state["meta"].get("valid")
    if valid is None or not bool(valid.astype(bool).all()):
        missing = state["meta"].loc[~valid.astype(bool), "stem"].drop_duplicates().tolist() if valid is not None else []
        raise RuntimeError(f"L5 crop cache is incomplete; failed videos: {missing[:10]}")
    if Path(run_cfg["stop_file"]).is_file():
        return compact_training_status(cfg, smoke=smoke)
    state = K.step_train(run_cfg, state)
    expected = set(range(int(run_cfg["n_folds"])))
    complete = {
        fold for fold in expected
        if all((work / "folds" / f"fold_{fold}" / name).is_file() for name in ("best.pt", "oof.csv", "summary.json"))
    }
    if complete != expected:
        _atomic_json(work / "state.json", {"status": "stopped_or_incomplete", "complete_folds": sorted(complete)})
        return compact_training_status(cfg, smoke=smoke)
    state = K.step_oof(run_cfg, state)
    state = K.step_verify(run_cfg, state)
    _atomic_json(work / "state.json", {
        "status": "complete" if state["verify"]["pass"] else "contract_failed",
        "complete_folds": sorted(complete),
        "timing": state.get("timing", {}),
        "contract": state.get("verify", {}),
    })
    return compact_training_status(cfg, smoke=smoke)


def run_smoke(cfg: L5Config) -> dict[str, Any]:
    return _run_training(cfg, smoke=True)


def run_training(cfg: L5Config) -> dict[str, Any]:
    return _run_training(cfg, smoke=False)


def compact_training_status(cfg: L5Config, *, smoke: bool = False) -> dict[str, Any]:
    work = cfg.work_dir / "smoke" if smoke else cfg.work_dir
    state_path = work / "state.json"
    readout_path = work / "oof_readout.json"
    state = json.loads(state_path.read_text()) if state_path.is_file() else {}
    readout = json.loads(readout_path.read_text()) if readout_path.is_file() else {}
    folds = {}
    for fold in range(2 if smoke else 5):
        summary = work / "folds" / f"fold_{fold}" / "summary.json"
        last = work / "folds" / f"fold_{fold}" / "last.pt"
        if summary.is_file():
            folds[str(fold)] = json.loads(summary.read_text())
        elif last.is_file():
            folds[str(fold)] = {"status": "resumable_checkpoint", "path": str(last)}
    return {
        "state": state,
        "folds": folds,
        "readout": readout.get("per_embryo"),
        "contract": state.get("contract"),
        "stop_file": str(work / "STOP_REQUESTED"),
    }


def request_training_stop(cfg: L5Config, *, smoke: bool = False) -> Path:
    path = (cfg.work_dir / "smoke" if smoke else cfg.work_dir) / "STOP_REQUESTED"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Stop after the current epoch; last.pt is resumable.\n", encoding="utf-8")
    return path


def clear_training_stop(cfg: L5Config, *, smoke: bool = False) -> None:
    ((cfg.work_dir / "smoke" if smoke else cfg.work_dir) / "STOP_REQUESTED").unlink(missing_ok=True)


def _score_video(cfg: L5Config, rows, fold: int, bundle, reader, torch) -> Any:
    import pandas as pd

    model = bundle["models"][fold]
    device = bundle["device"]
    prepared: dict[Any, np.ndarray] = {}
    frame_cache: dict[Any, np.ndarray] = {}
    local_bundle = {"config": bundle["config"], "prepared_frames": prepared}
    probabilities = np.empty((len(rows), 3), dtype=np.float32)
    ordered = rows.sort_values(["t", "node_id"], kind="stable")
    for frame, group in ordered.groupby("t", sort=True):
        indices = group.index.to_numpy()
        records = group[list(REQUIRED_COORD_COLUMNS)].to_dict("records")
        for start in range(0, len(records), cfg.score_batch):
            recs = records[start:start + cfg.score_batch]
            samples = np.stack([
                prepare_sample(str(node["stem"]), int(node["t"]), node, local_bundle, frame_cache, reader)
                for node in recs
            ])
            tensor = torch.from_numpy(samples).to(device=device, dtype=torch.float32)
            with torch.inference_mode(), torch.autocast(device_type=device.type, dtype=torch.float16,
                                                         enabled=device.type == "cuda"):
                values = torch.softmax(model(tensor), dim=1).float().cpu().numpy()
            probabilities[indices[start:start + len(recs)]] = values
        # For the next frame, lag -2 needs frame t-1. Older normalised volumes can be released.
        for key in [key for key in prepared if key[0] == str(group.iloc[0]["stem"]) and key[1] < int(frame) - 1]:
            prepared.pop(key, None)
    result = pd.DataFrame({
        "stem": rows["stem"].astype(str).to_numpy(),
        "node_id": rows["node_id"].to_numpy(dtype=np.int64),
        "fold": np.full(len(rows), int(fold), dtype=np.int8),
        "p_cont": probabilities[:, 0],
        "p_par": probabilities[:, 1],
        "p_dau": probabilities[:, 2],
    })
    return result


def run_node_scoring(cfg: L5Config) -> dict[str, Any]:
    import pandas as pd
    import torch

    K.configure_profile({"profile": PROFILE})
    folds = _fold_map(cfg.splits_path)
    checkpoints = [cfg.work_dir / "folds" / f"fold_{fold}" / "best.pt" for fold in range(5)]
    missing = [path for path in checkpoints if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Finish all five L5 folds first; missing {missing}")
    coords = pd.read_parquet(cfg.coords_path, columns=list(REQUIRED_COORD_COLUMNS))
    cfg.predictions_dir.mkdir(parents=True, exist_ok=True)
    bundle = load_daughternet(checkpoints, device="cuda" if torch.cuda.is_available() else "cpu")
    reader = K.FrameReader(cfg.data_dir)
    state_path = cfg.work_dir / "scoring_state.json"
    completed = []
    started = time.time()
    for index, stem in enumerate(sorted(coords["stem"].astype(str).unique()), start=1):
        if cfg.score_stop_file.is_file():
            _atomic_json(state_path, {"status": "stopped_safely", "completed_videos": len(completed),
                                      "last_complete": completed[-1] if completed else None})
            return compact_scoring_status(cfg)
        fold = int(folds[stem])
        destination = cfg.predictions_dir / f"{stem}.parquet"
        group = coords[coords["stem"] == stem].reset_index(drop=True)
        if destination.is_file():
            previous = pd.read_parquet(destination, columns=list(OUTPUT_COLUMNS))
            valid = len(previous) == len(group) and set(previous["node_id"]) == set(group["node_id"])
            if valid and int(previous["fold"].iloc[0]) == fold:
                completed.append(stem)
                print(f"L5 SCORE [{index}/199] {stem}: resume {len(group)} nodes", flush=True)
                continue
        print(f"L5 SCORE [{index}/199] {stem}: fold {fold}, {len(group)} nodes", flush=True)
        result = _score_video(cfg, group, fold, bundle, reader, torch)
        temporary = destination.with_suffix(".parquet.tmp")
        result.to_parquet(temporary, index=False)
        os.replace(temporary, destination)
        completed.append(stem)
        _atomic_json(state_path, {"status": "running", "completed_videos": len(completed),
                                  "last_complete": stem, "elapsed_s": round(time.time() - started, 1)})

    parts = [pd.read_parquet(cfg.predictions_dir / f"{stem}.parquet") for stem in sorted(folds)]
    final = pd.concat(parts, ignore_index=True)[list(OUTPUT_COLUMNS)]
    if len(final) != len(coords) or final.duplicated(["stem", "node_id"]).any():
        raise RuntimeError(f"Final OOF coverage mismatch: predictions={len(final)}, coordinates={len(coords)}")
    values = final[["p_cont", "p_par", "p_dau"]].to_numpy(dtype=np.float64)
    if not np.isfinite(values).all() or not np.allclose(values.sum(axis=1), 1.0, atol=2e-4):
        raise RuntimeError("Final OOF probabilities are non-finite or do not sum to one")
    cfg.final_oof_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = cfg.final_oof_path.with_suffix(".parquet.tmp")
    final.to_parquet(temporary, index=False)
    os.replace(temporary, cfg.final_oof_path)
    report = {
        "status": "complete",
        "rows": len(final),
        "videos": int(final["stem"].nunique()),
        "fold_counts": {str(k): int(v) for k, v in final.groupby("fold").size().items()},
        "sha256": _sha256(cfg.final_oof_path),
        "path": str(cfg.final_oof_path),
        "elapsed_s": round(time.time() - started, 1),
    }
    _atomic_json(state_path, report)
    return report


def compact_scoring_status(cfg: L5Config) -> dict[str, Any]:
    path = cfg.work_dir / "scoring_state.json"
    state = json.loads(path.read_text()) if path.is_file() else {}
    state["cached_videos"] = len(list(cfg.predictions_dir.glob("*.parquet"))) if cfg.predictions_dir.is_dir() else 0
    state["stop_file"] = str(cfg.score_stop_file)
    state["final_oof"] = str(cfg.final_oof_path)
    return state


def request_scoring_stop(cfg: L5Config) -> Path:
    cfg.score_stop_file.parent.mkdir(parents=True, exist_ok=True)
    cfg.score_stop_file.write_text("Stop after the current video; completed files are reusable.\n", encoding="utf-8")
    return cfg.score_stop_file


def clear_scoring_stop(cfg: L5Config) -> None:
    cfg.score_stop_file.unlink(missing_ok=True)
