"""Resumable exp38 regression: public exp29 plus per-video AdaBN.

The expensive public inference is performed one video at a time.  Completed
raw graphs and adapted checkpoint pairs are reused.  Ground truth is touched
only after all twelve baseline/candidate graphs exist, by the official scorer.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .kaggle_adabn_cell import (
    _adabn_video_batch,
    _load_public_predictor,
    adapt_public_pair_for_video,
    adabn_node_guard,
)


EXPERIMENT = "local_friend_a_exp05_public_adabn"
VARIANTS = ("baseline", "candidate_adabn", "guarded_adabn")


class StopRequested(RuntimeError):
    """A cooperative stop at a reusable boundary."""


def _truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"", "0", "false", "no", "off"}


def _atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def _copy_graph(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination) if destination.is_dir() else destination.unlink()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)


def _discover_data_dir(repo_root: Path) -> Path:
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
    raise FileNotFoundError(
        "Training videos were not found. Set BIOHUB_DATA_DIR to the folder containing *.zarr files."
    )


def _baseline_source(repo_root: Path, dataset_ids: tuple[str, ...]) -> Path | None:
    explicit = os.environ.get("BIOHUB_EXP38_BASE_RAW_DIR", "").strip()
    candidates = [Path(explicit)] if explicit else []
    candidates.extend(
        [
            repo_root.parent
            / "outputs"
            / "local_friend_a_b20_divnet"
            / "cache"
            / "friend_a_b20_exp29"
            / "raw",
            repo_root / ".public_local_cache" / "exp29" / "raw",
            repo_root.parent / ".public_local_cache" / "exp29" / "raw",
        ]
    )
    for candidate in candidates:
        if candidate.is_dir() and all((candidate / f"{stem}.geff").exists() for stem in dataset_ids):
            return candidate.resolve()
    return None


@dataclass
class Exp38Config:
    repo_root: Path
    data_dir: Path
    output_dir: Path
    source_notebook: Path
    split_path: Path
    support_repo: Path
    primary_weights: Path
    secondary_weights: Path
    baseline_source_dir: Path | None
    dataset_ids: tuple[str, ...] = field(default_factory=tuple)
    batch_size: int = 2
    use_amp: bool = True
    guard_lower: float = 0.90
    guard_upper: float = 1.05
    max_videos_per_run: int = 0
    run_pipeline: bool = True

    @classmethod
    def from_environment(cls, repo_root: Path) -> "Exp38Config":
        repo_root = repo_root.resolve()
        split_path = repo_root / "experiments" / "_lib" / "loeo_train6bba_val44b6.json"
        payload = json.loads(split_path.read_text(encoding="utf-8"))
        dataset_ids = tuple(payload["holdout"])
        support = repo_root / "external" / "pilkwang__biohub-tracking-support-pack-50ep-v1"
        secondary = repo_root / "external" / "pilkwang__biohub-temporal-unet3d-seed314159-v1"
        output_default = repo_root.parent / "outputs" / EXPERIMENT
        return cls(
            repo_root=repo_root,
            data_dir=_discover_data_dir(repo_root),
            output_dir=Path(os.environ.get("BIOHUB_EXP38_OUTPUT_DIR", output_default)).resolve(),
            source_notebook=(
                repo_root
                / "experiments"
                / "exp29_sjlee947_verbatim"
                / "exp29-sjlee947-verbatim.ipynb"
            ),
            split_path=split_path,
            support_repo=support / "repo",
            primary_weights=(
                support / "weights" / "unet_transformer" / "split_0" / "edge_predictor_best.pth"
            ),
            secondary_weights=(
                secondary / "weights" / "unet_transformer" / "split_0" / "edge_predictor_best.pth"
            ),
            baseline_source_dir=_baseline_source(repo_root, dataset_ids),
            dataset_ids=dataset_ids,
            batch_size=int(os.environ.get("BIOHUB_EXP38_BATCH", "2")),
            use_amp=_truthy(os.environ.get("BIOHUB_EXP38_AMP"), True),
            guard_lower=float(os.environ.get("BIOHUB_EXP38_GUARD_LOWER", "0.90")),
            guard_upper=float(os.environ.get("BIOHUB_EXP38_GUARD_UPPER", "1.05")),
            max_videos_per_run=int(os.environ.get("BIOHUB_EXP38_MAX_VIDEOS", "0")),
            run_pipeline=_truthy(os.environ.get("BIOHUB_EXP38_RUN"), True),
        )

    def serialisable(self) -> dict[str, Any]:
        result = asdict(self)
        for key in (
            "repo_root",
            "data_dir",
            "output_dir",
            "source_notebook",
            "split_path",
            "support_repo",
            "primary_weights",
            "secondary_weights",
        ):
            result[key] = str(result[key])
        result["baseline_source_dir"] = (
            str(self.baseline_source_dir) if self.baseline_source_dir is not None else None
        )
        result["dataset_ids"] = list(self.dataset_ids)
        return result

    def recipe_fingerprint(self) -> str:
        result = self.serialisable()
        for key in ("output_dir", "baseline_source_dir", "max_videos_per_run", "run_pipeline"):
            result.pop(key, None)
        for label, path in (
            ("primary", self.primary_weights),
            ("secondary", self.secondary_weights),
            ("notebook", self.source_notebook),
        ):
            stat = path.stat()
            result[f"{label}_identity"] = [stat.st_size, stat.st_mtime_ns]
        return hashlib.sha256(json.dumps(result, sort_keys=True).encode("utf-8")).hexdigest()


def _log(cfg: Exp38Config, message: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    with (cfg.output_dir / "run.log").open("a", encoding="utf-8") as stream:
        stream.write(line + "\n")


def stop_path(cfg: Exp38Config) -> Path:
    return cfg.output_dir / "STOP_REQUESTED"


def clear_stop(cfg: Exp38Config) -> None:
    stop_path(cfg).unlink(missing_ok=True)


def request_stop(cfg: Exp38Config) -> Path:
    path = stop_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Stop at the next reusable boundary.\n", encoding="utf-8")
    return path


def _check_stop(cfg: Exp38Config) -> None:
    if stop_path(cfg).exists():
        raise StopRequested("STOP_REQUESTED marker found")


def _state_path(cfg: Exp38Config) -> Path:
    return cfg.output_dir / "state.json"


def load_state(cfg: Exp38Config) -> dict[str, Any]:
    path = _state_path(cfg)
    if not path.exists():
        return {
            "version": 1,
            "fingerprint": cfg.recipe_fingerprint(),
            "status": "not_started",
            "records": {},
            "metrics": {},
        }
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("fingerprint") != cfg.recipe_fingerprint():
        raise RuntimeError(
            "Existing exp38 output uses another recipe. Restore the settings or choose another "
            "BIOHUB_EXP38_OUTPUT_DIR."
        )
    return state


def save_state(cfg: Exp38Config, state: dict[str, Any]) -> None:
    state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _atomic_json(_state_path(cfg), state)


def _graph_valid(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        import tracksdata as td

        loaded = td.graph.IndexedRXGraph.from_geff(path)
        graph = loaded[0] if isinstance(loaded, tuple) else loaded
        return graph.num_nodes() >= 0 and graph.num_edges() >= 0
    except Exception:
        return False


def _graph_counts(path: Path) -> dict[str, int]:
    import tracksdata as td

    loaded = td.graph.IndexedRXGraph.from_geff(path)
    graph = loaded[0] if isinstance(loaded, tuple) else loaded
    return {"nodes": int(graph.num_nodes()), "edges": int(graph.num_edges())}


def _raw_path(cfg: Exp38Config, variant: str, stem: str) -> Path:
    return cfg.output_dir / "raw" / variant / f"{stem}.geff"


def _adapted_dir(cfg: Exp38Config, stem: str) -> Path:
    return cfg.output_dir / "adapted_models" / stem


def _pair_ready(cfg: Exp38Config, stem: str) -> bool:
    root = _adapted_dir(cfg, stem)
    return all(
        (root / side / name).is_file()
        for side in ("primary", "secondary")
        for name in ("edge_predictor_best.pth", "config.json")
    ) and (root / "pair_receipt.json").is_file()


def _copy_checkpoint_pair(source_weights: Path, destination_dir: Path) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    for name in ("edge_predictor_best.pth", "config.json"):
        shutil.copy2(source_weights.with_name(name), destination_dir / name)


def _public_local(cfg: Exp38Config):
    tools = cfg.repo_root / "tools"
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    import public_local

    return public_local


def _run_public_raw(
    cfg: Exp38Config,
    stem: str,
    variant: str,
    *,
    primary_weights: Path | None = None,
    secondary_weights: Path | None = None,
) -> float:
    destination = _raw_path(cfg, variant, stem)
    if _graph_valid(destination):
        return 0.0
    public = _public_local(cfg)
    work = cfg.output_dir / "work" / variant / stem
    predictions = work / "predictions"
    if predictions.exists():
        shutil.rmtree(predictions)
    work.mkdir(parents=True, exist_ok=True)
    repo, _ = public.materialise_repo(
        Path.home() / "biohub_weights", work, None, None, materialise_code=True
    )
    if primary_weights is not None:
        _copy_checkpoint_pair(
            primary_weights, repo / "weights" / "unet_transformer" / "split_0"
        )
    if secondary_weights is not None:
        os.environ["BIOHUB_SECONDARY_WEIGHTS"] = str(secondary_weights)

    cells = public.notebook_cells(cfg.source_notebook)
    namespace = public.build_namespace(cells, repo, work, cfg.data_dir)
    public.apply_runtime_patches(cells, namespace, repo, work)
    started = time.perf_counter()
    public.run_inference(
        namespace,
        repo,
        work,
        cfg.data_dir,
        [stem],
        destination.parent,
        None,
    )
    seconds = time.perf_counter() - started
    if not _graph_valid(destination):
        raise RuntimeError(f"public inference did not produce a valid graph: {destination}")
    return seconds


def _ensure_baseline(cfg: Exp38Config, stem: str) -> dict[str, Any]:
    destination = _raw_path(cfg, "baseline", stem)
    source = cfg.baseline_source_dir / f"{stem}.geff" if cfg.baseline_source_dir else None
    reused = False
    seconds = 0.0
    if not _graph_valid(destination):
        if source is not None and _graph_valid(source):
            _copy_graph(source, destination)
            reused = True
            _log(cfg, f"baseline {stem}: reused {source}")
        else:
            _log(cfg, f"baseline {stem}: running public exp29")
            seconds = _run_public_raw(cfg, stem, "baseline")
    return {**_graph_counts(destination), "seconds": seconds, "reused": reused}


def _ensure_candidate(cfg: Exp38Config, stem: str) -> tuple[dict[str, Any], dict[str, Any]]:
    adapted_root = _adapted_dir(cfg, stem)
    if _pair_ready(cfg, stem):
        receipt = json.loads((adapted_root / "pair_receipt.json").read_text(encoding="utf-8"))
        receipt["reused"] = True
        _log(cfg, f"AdaBN {stem}: reused checkpoint pair")
    else:
        _log(cfg, f"AdaBN {stem}: adapting primary + secondary")
        receipt = adapt_public_pair_for_video(
            repo_dir=cfg.support_repo,
            video_path=cfg.data_dir / stem,
            primary_weights=cfg.primary_weights,
            secondary_weights=cfg.secondary_weights,
            output_dir=adapted_root,
            batch_size=cfg.batch_size,
            use_amp=cfg.use_amp,
            stop_check=lambda: _check_stop(cfg),
        )
        receipt["reused"] = False

    destination = _raw_path(cfg, "candidate_adabn", stem)
    infer_seconds = 0.0
    if not _graph_valid(destination):
        _check_stop(cfg)
        _log(cfg, f"AdaBN {stem}: running public exp29 with adapted pair")
        infer_seconds = _run_public_raw(
            cfg,
            stem,
            "candidate_adabn",
            primary_weights=adapted_root / "primary" / "edge_predictor_best.pth",
            secondary_weights=adapted_root / "secondary" / "edge_predictor_best.pth",
        )
    stats = {**_graph_counts(destination), "seconds": infer_seconds}
    return stats, receipt


def _apply_guard(
    cfg: Exp38Config,
    stem: str,
    baseline_stats: dict[str, Any],
    candidate_stats: dict[str, Any],
) -> dict[str, Any]:
    accepted, ratio = adabn_node_guard(
        baseline_stats["nodes"],
        candidate_stats["nodes"],
        cfg.guard_lower,
        cfg.guard_upper,
    )
    selected = "candidate_adabn" if accepted else "baseline_fallback"
    source_variant = "candidate_adabn" if accepted else "baseline"
    destination = _raw_path(cfg, "guarded_adabn", stem)
    if not _graph_valid(destination):
        _copy_graph(_raw_path(cfg, source_variant, stem), destination)
    return {"accepted": accepted, "ratio": ratio, "selected": selected}


def _all_graphs_valid(cfg: Exp38Config, variant: str) -> bool:
    return all(_graph_valid(_raw_path(cfg, variant, stem)) for stem in cfg.dataset_ids)


def _postprocess_and_score(cfg: Exp38Config, state: dict[str, Any]) -> None:
    if not all(_all_graphs_valid(cfg, variant) for variant in VARIANTS):
        return
    public = _public_local(cfg)
    work = cfg.output_dir / "work" / "postprocess"
    repo, _ = public.materialise_repo(
        Path.home() / "biohub_weights", work, None, None, materialise_code=True
    )
    cells = public.notebook_cells(cfg.source_notebook)
    namespace = public.build_namespace(cells, repo, work, cfg.data_dir)
    public.load_postproc(cells, namespace)
    if namespace.get("DEEPCENTER_VETO_DETECTOR") is None:
        namespace["DEEPCENTER_VETO_DETECTOR"] = namespace["load_deepcenter_veto_detector"]()

    for variant in VARIANTS:
        _check_stop(cfg)
        output = cfg.output_dir / "predictions" / variant
        complete = all(_graph_valid(output / f"{stem}.geff") for stem in cfg.dataset_ids)
        if not complete:
            _log(cfg, f"post-processing {variant}")
            public.postprocess_and_write(namespace, cfg.output_dir / "raw" / variant, output)
        summary, rows = public.score_dir(output, cfg.data_dir)
        metrics = {"summary": summary, "rows": rows}
        state["metrics"][variant] = metrics
        _atomic_json(cfg.output_dir / "metrics" / f"{variant}.json", metrics)
        save_state(cfg, state)


def _write_result(cfg: Exp38Config, state: dict[str, Any]) -> None:
    baseline = state.get("metrics", {}).get("baseline", {}).get("summary", {})
    baseline_score = baseline.get("score")
    lines = [
        "# Friend A exp38 — public exp29 + per-video AdaBN",
        "",
        "The regression set is the fixed 12-video 44b6 set. Public weights saw these videos, so this is a "
        "regression/timing check, not an honest model-selection validation.",
        "",
        "| variant | official score | delta | adjusted edge | division J | node recall |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for variant in VARIANTS:
        summary = state.get("metrics", {}).get(variant, {}).get("summary")
        if not summary:
            lines.append(f"| {variant} | pending | | | | |")
            continue
        delta = summary["score"] - baseline_score if baseline_score is not None else float("nan")
        lines.append(
            f"| {variant} | {summary['score']:.6f} | {delta:+.6f} | "
            f"{summary['adj_edge_jaccard']:.6f} | {summary['division_jaccard']:.6f} | "
            f"{summary['node_recall']:.6f} |"
        )

    lines.extend(
        [
            "",
            "| video | base nodes | AdaBN nodes | ratio | decision | adaptation s | inference s |",
            "|---|---:|---:|---:|---|---:|---:|",
        ]
    )
    for stem in cfg.dataset_ids:
        record = state.get("records", {}).get(stem)
        if not record or record.get("status") != "complete":
            lines.append(f"| {stem} | pending | | | | | |")
            continue
        lines.append(
            f"| {stem} | {record['baseline']['nodes']} | {record['candidate']['nodes']} | "
            f"{record['guard']['ratio']:.4f} | {record['guard']['selected']} | "
            f"{record['adaptation'].get('seconds', 0.0):.1f} | "
            f"{record['candidate'].get('seconds', 0.0):.1f} |"
        )
    accepted = sum(
        bool(row.get("guard", {}).get("accepted"))
        for row in state.get("records", {}).values()
        if row.get("status") == "complete"
    )
    lines.extend(
        [
            "",
            f"Guard accepted AdaBN on {accepted}/{len(cfg.dataset_ids)} videos. Bounds: "
            f"[{cfg.guard_lower:.2f}, {cfg.guard_upper:.2f}].",
            "No leaderboard submission is performed by this notebook.",
            "The copy-ready Kaggle cell is `experiments/local_friend_a_exp05_public_adabn/kaggle_adabn_cell.py`.",
        ]
    )
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    (cfg.output_dir / "result.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def preflight(cfg: Exp38Config, *, gpu_smoke: bool = False) -> dict[str, Any]:
    import torch
    import torch.nn as nn

    errors = []
    for path in (
        cfg.source_notebook,
        cfg.split_path,
        cfg.primary_weights,
        cfg.primary_weights.with_name("config.json"),
        cfg.secondary_weights,
        cfg.secondary_weights.with_name("config.json"),
        cfg.support_repo / "scripts" / "predict_unet_transformer.py",
    ):
        if not path.exists():
            errors.append(f"missing: {path}")
    if len(cfg.dataset_ids) != 12:
        errors.append(f"expected 12 regression videos, found {len(cfg.dataset_ids)}")
    for stem in cfg.dataset_ids:
        if not (cfg.data_dir / f"{stem}.zarr").exists():
            errors.append(f"missing image: {stem}.zarr")
        if not (cfg.data_dir / f"{stem}.geff").exists():
            errors.append(f"missing scoring GT: {stem}.geff")
    if cfg.batch_size != 2:
        errors.append("registered B5 recipe requires batch_size=2")
    if (cfg.guard_lower, cfg.guard_upper) != (0.90, 1.05):
        errors.append("registered exp38 recipe requires node guard [0.90, 1.05]")
    if errors:
        raise RuntimeError("Preflight failed:\n- " + "\n- ".join(errors))
    if cfg.run_pipeline and not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for exp38")

    result: dict[str, Any] = {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "videos": len(cfg.dataset_ids),
        "data_dir": str(cfg.data_dir),
        "output_dir": str(cfg.output_dir),
        "baseline_source_dir": (
            str(cfg.baseline_source_dir) if cfg.baseline_source_dir is not None else None
        ),
        "fingerprint": cfg.recipe_fingerprint(),
    }
    if gpu_smoke:
        predictor = _load_public_predictor(cfg.support_repo)
        device = torch.device("cuda")
        smoke = []
        for label, weights in (
            ("primary", cfg.primary_weights),
            ("secondary", cfg.secondary_weights),
        ):
            model, window_size, downsample = predictor.load_model(weights, device)
            bn_layers = [m for m in model.unet.modules() if isinstance(m, nn.BatchNorm3d)]
            batch, _ = _adabn_video_batch(
                predictor, cfg.data_dir / cfg.dataset_ids[0], [0], downsample, window_size
            )
            with torch.no_grad(), torch.amp.autocast("cuda", enabled=cfg.use_amp):
                output = model.unet(batch.to(device).unsqueeze(2))
            finite = bool(torch.isfinite(output).all().item())
            smoke.append({"model": label, "bn_layers": len(bn_layers), "finite": finite})
            del model, batch, output
            torch.cuda.empty_cache()
        if not all(row["bn_layers"] and row["finite"] for row in smoke):
            raise RuntimeError(f"GPU smoke failed: {smoke}")
        result["gpu_smoke"] = smoke

    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(cfg.output_dir / "config.json", cfg.serialisable())
    _atomic_json(cfg.output_dir / "preflight.json", result)
    return result


def run_pipeline(cfg: Exp38Config) -> dict[str, Any]:
    state = load_state(cfg)
    if not cfg.run_pipeline:
        state["status"] = "preflight_only"
        save_state(cfg, state)
        _write_result(cfg, state)
        return state
    state["status"] = "running"
    save_state(cfg, state)
    completed_this_run = 0
    try:
        for stem in cfg.dataset_ids:
            record = state["records"].get(stem, {})
            if record.get("status") == "complete" and _graph_valid(
                _raw_path(cfg, "guarded_adabn", stem)
            ):
                _log(cfg, f"reuse completed {stem}")
                continue
            if cfg.max_videos_per_run and completed_this_run >= cfg.max_videos_per_run:
                state["status"] = "paused_by_max_videos"
                save_state(cfg, state)
                _write_result(cfg, state)
                return state
            _check_stop(cfg)
            state["records"][stem] = {"status": "running", "started_at": time.time()}
            save_state(cfg, state)
            baseline = _ensure_baseline(cfg, stem)
            _check_stop(cfg)
            candidate, adaptation = _ensure_candidate(cfg, stem)
            guard = _apply_guard(cfg, stem, baseline, candidate)
            state["records"][stem] = {
                "status": "complete",
                "finished_at": time.time(),
                "baseline": baseline,
                "candidate": candidate,
                "adaptation": adaptation,
                "guard": guard,
            }
            save_state(cfg, state)
            _log(
                cfg,
                f"complete {stem}: ratio={guard['ratio']:.4f} selected={guard['selected']}",
            )
            completed_this_run += 1

        _postprocess_and_score(cfg, state)
        state["status"] = "complete" if len(state.get("metrics", {})) == 3 else "partial"
        save_state(cfg, state)
    except (KeyboardInterrupt, StopRequested) as error:
        state["status"] = "stopped_safely"
        state["stop_reason"] = str(error)
        save_state(cfg, state)
        _log(cfg, f"stopped safely: {error}")
    except Exception as error:
        state["status"] = "failed"
        state["error"] = repr(error)
        save_state(cfg, state)
        raise
    finally:
        _write_result(cfg, state)
    return state


def compact_status(cfg: Exp38Config) -> dict[str, Any]:
    state = load_state(cfg)
    complete = sum(
        row.get("status") == "complete" for row in state.get("records", {}).values()
    )
    return {
        "status": state.get("status", "not_started"),
        "completed_videos": f"{complete}/{len(cfg.dataset_ids)}",
        "guard_accepts": sum(
            bool(row.get("guard", {}).get("accepted"))
            for row in state.get("records", {}).values()
            if row.get("status") == "complete"
        ),
        "metrics": {
            key: value.get("summary", {})
            for key, value in state.get("metrics", {}).items()
        },
        "stop_marker": stop_path(cfg).exists(),
        "output_dir": str(cfg.output_dir),
        "result": str(cfg.output_dir / "result.md"),
    }

