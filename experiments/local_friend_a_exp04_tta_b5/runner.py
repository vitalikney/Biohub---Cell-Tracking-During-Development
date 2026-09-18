"""Resumable Friend A B5 test-time-adaptation experiment.

Adaptation is deliberately separated from evaluation: the adaptation functions
open only ``.zarr`` image stores. Competition ``.geff`` labels are read later,
after all predictions for a variant exist, by ``tools/score_geffs.py``.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


EXPERIMENT = "local_friend_a_exp04_tta_b5"
VARIANTS = ("baseline", "adabn", "head_ema")


class StopRequested(RuntimeError):
    """Raised after a resumable checkpoint has been written."""


def _truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"", "0", "false", "no", "off"}


def _atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def _atomic_torch_save(path: Path, payload: Any) -> None:
    import torch

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    torch.save(payload, temporary)
    os.replace(temporary, path)


def _discover_data_dir(repo_root: Path) -> Path:
    candidates: list[Path] = []
    explicit = os.environ.get("BIOHUB_DATA_DIR", "").strip()
    if explicit:
        candidates.append(Path(explicit))
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


@dataclass
class TTAConfig:
    repo_root: Path
    data_dir: Path
    output_dir: Path
    weights_path: Path
    manifest_path: Path
    variants: tuple[str, ...] = VARIANTS
    seed: int = 42
    steps: int = 200
    checkpoint_every: int = 25
    guard_every: int = 25
    probe_windows: int = 8
    batch_size: int = 2
    lr: float = 1e-4
    ema_decay: float = 0.995
    pseudo_threshold: float = 0.985
    background_threshold: float = 0.05
    negative_weight: float = 0.01
    det_threshold: float = 0.965
    pool_kernel_um: float = 5.0
    max_node_growth: float = 0.05
    max_node_drop: float = 0.10
    max_videos_per_run: int = 0
    run_pipeline: bool = True
    use_amp: bool = True
    dataset_ids: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_environment(cls, repo_root: Path) -> "TTAConfig":
        repo_root = repo_root.resolve()
        manifest = repo_root / "experiments" / "_lib" / "loeo_train6bba_val44b6.json"
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        ids = tuple(payload["holdout"])
        variants = tuple(
            item.strip()
            for item in os.environ.get("BIOHUB_TTA_VARIANTS", ",".join(VARIANTS)).split(",")
            if item.strip()
        )
        if variants and "baseline" not in variants:
            variants = ("baseline", *variants)
        output_default = repo_root.parent / "outputs" / EXPERIMENT
        return cls(
            repo_root=repo_root,
            data_dir=_discover_data_dir(repo_root),
            output_dir=Path(os.environ.get("BIOHUB_TTA_OUTPUT_DIR", output_default)).resolve(),
            weights_path=(
                repo_root
                / "weights_dataset"
                / "friend_a_exp02_loeo20"
                / "edge_predictor_best.pth"
            ),
            manifest_path=manifest,
            variants=variants,
            steps=int(os.environ.get("BIOHUB_TTA_STEPS", "200")),
            checkpoint_every=int(os.environ.get("BIOHUB_TTA_CHECKPOINT_EVERY", "25")),
            guard_every=int(os.environ.get("BIOHUB_TTA_GUARD_EVERY", "25")),
            probe_windows=int(os.environ.get("BIOHUB_TTA_PROBE_WINDOWS", "8")),
            batch_size=int(os.environ.get("BIOHUB_TTA_BATCH", "2")),
            lr=float(os.environ.get("BIOHUB_TTA_LR", "1e-4")),
            pseudo_threshold=float(os.environ.get("BIOHUB_TTA_PSEUDO_THRESHOLD", "0.985")),
            max_node_growth=float(os.environ.get("BIOHUB_TTA_MAX_NODE_GROWTH", "0.05")),
            max_node_drop=float(os.environ.get("BIOHUB_TTA_MAX_NODE_DROP", "0.10")),
            max_videos_per_run=int(os.environ.get("BIOHUB_TTA_MAX_VIDEOS", "0")),
            run_pipeline=_truthy(os.environ.get("BIOHUB_TTA_RUN"), True),
            use_amp=_truthy(os.environ.get("BIOHUB_TTA_AMP"), True),
            dataset_ids=ids,
        )

    def serialisable(self) -> dict[str, Any]:
        value = asdict(self)
        for key in ("repo_root", "data_dir", "output_dir", "weights_path", "manifest_path"):
            value[key] = str(value[key])
        value["variants"] = list(self.variants)
        value["dataset_ids"] = list(self.dataset_ids)
        return value

    def recipe_fingerprint(self) -> str:
        value = self.serialisable()
        for key in ("output_dir", "max_videos_per_run", "run_pipeline"):
            value.pop(key, None)
        return hashlib.sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest()


def _log(cfg: TTAConfig, message: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(line, flush=True)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    with (cfg.output_dir / "run.log").open("a", encoding="utf-8") as stream:
        stream.write(line + "\n")


def _state_path(cfg: TTAConfig) -> Path:
    return cfg.output_dir / "state.json"


def load_state(cfg: TTAConfig) -> dict[str, Any]:
    path = _state_path(cfg)
    if not path.exists():
        return {"version": 1, "fingerprint": cfg.recipe_fingerprint(), "records": {}, "metrics": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("fingerprint") != cfg.recipe_fingerprint():
        raise RuntimeError(
            "Existing output was created with another TTA recipe. Use another BIOHUB_TTA_OUTPUT_DIR "
            "or restore the previous settings."
        )
    return state


def save_state(cfg: TTAConfig, state: dict[str, Any]) -> None:
    state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _atomic_json(_state_path(cfg), state)


def stop_path(cfg: TTAConfig) -> Path:
    return cfg.output_dir / "STOP_REQUESTED"


def request_stop(cfg: TTAConfig) -> Path:
    path = stop_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Stop after the next safe checkpoint.\n", encoding="utf-8")
    return path


def clear_stop(cfg: TTAConfig) -> None:
    stop_path(cfg).unlink(missing_ok=True)


def _check_stop(cfg: TTAConfig) -> None:
    if stop_path(cfg).exists():
        raise StopRequested("STOP_REQUESTED marker found")


def _install_import_paths(cfg: TTAConfig) -> Any:
    scripts = cfg.repo_root / "tools" / "repo" / "scripts"
    source = cfg.repo_root / "tools" / "repo" / "src"
    for path in reversed((str(scripts), str(source), str(cfg.repo_root))):
        if path not in sys.path:
            sys.path.insert(0, path)
    os.environ["BIOHUB_DATA_DIR"] = str(cfg.data_dir)
    # The support-pack snapshot has no models/__init__.py, while its training
    # script imports the classes from the package namespace. Populate that
    # namespace without modifying the vendored snapshot.
    import biohub_tracking.models as model_namespace
    from biohub_tracking.models.simple_node_transformer import SimpleNodeTransformer
    from biohub_tracking.models.temporal_unet import TemporalUNet3D

    model_namespace.SimpleNodeTransformer = SimpleNodeTransformer
    model_namespace.TemporalUNet3D = TemporalUNet3D
    import predict_unet_transformer as predictor

    return predictor


def preflight(cfg: TTAConfig, *, gpu_smoke: bool = False) -> dict[str, Any]:
    import torch

    errors: list[str] = []
    if not cfg.weights_path.is_file():
        errors.append(f"missing checkpoint: {cfg.weights_path}")
    if not cfg.weights_path.with_name("config.json").is_file():
        errors.append(f"missing model config: {cfg.weights_path.with_name('config.json')}")
    if len(cfg.dataset_ids) != 12:
        errors.append(f"expected 12 LOEO videos, found {len(cfg.dataset_ids)}")
    unknown = sorted(set(cfg.variants) - set(VARIANTS))
    if unknown:
        errors.append(f"unknown variants: {unknown}")
    for dataset_id in cfg.dataset_ids:
        if not (cfg.data_dir / f"{dataset_id}.zarr").exists():
            errors.append(f"missing image store: {dataset_id}.zarr")
        if not (cfg.data_dir / f"{dataset_id}.geff").exists():
            errors.append(f"missing evaluation GT: {dataset_id}.geff")
    if cfg.steps <= 0 or cfg.checkpoint_every <= 0 or cfg.guard_every <= 0:
        errors.append("steps/checkpoint_every/guard_every must be positive")
    if errors:
        raise RuntimeError("Preflight failed:\n- " + "\n- ".join(errors))

    result: dict[str, Any] = {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "data_dir": str(cfg.data_dir),
        "videos": len(cfg.dataset_ids),
        "variants": list(cfg.variants),
        "output_dir": str(cfg.output_dir),
        "fingerprint": cfg.recipe_fingerprint(),
    }
    if cfg.run_pipeline and not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the requested run")

    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    _atomic_json(cfg.output_dir / "config.json", cfg.serialisable())

    if gpu_smoke:
        predictor = _install_import_paths(cfg)
        device = torch.device("cuda")
        model, window_size, downsample = predictor.load_model(cfg.weights_path, device)
        batch, _, _, _, _ = _load_video_batch(
            predictor, cfg, cfg.dataset_ids[0], [0], downsample, window_size
        )
        with torch.no_grad(), torch.amp.autocast("cuda", enabled=cfg.use_amp):
            _, logits = model.encode(batch.to(device))
        finite = all(torch.isfinite(value).all().item() for value in logits)
        result["gpu_smoke"] = {"finite": bool(finite), "shape": list(logits[0].shape)}
        if not finite:
            raise RuntimeError("GPU smoke produced non-finite logits")
        del model, batch, logits
        torch.cuda.empty_cache()
    _atomic_json(cfg.output_dir / "preflight.json", result)
    return result


def _video_info(predictor: Any, cfg: TTAConfig, dataset_id: str, downsample: tuple[int, ...]):
    import zarr

    ds = predictor.open_dataset(
        cfg.data_dir / dataset_id, normalize=False, load_image=False, downsample=downsample
    )
    if "0.001" not in ds.quantiles or "0.999" not in ds.quantiles:
        raise ValueError(f"{dataset_id}: missing q0.001/q0.999 image statistics")
    array = zarr.open_group(str(ds.zarr_path), mode="r")["0"]
    return ds, array, float(ds.quantiles["0.001"]), float(ds.quantiles["0.999"])


def _load_video_batch(
    predictor: Any,
    cfg: TTAConfig,
    dataset_id: str,
    starts: list[int],
    downsample: tuple[int, ...],
    window_size: int,
):
    import torch

    ds, array, q_low, q_high = _video_info(predictor, cfg, dataset_id, downsample)
    target_shape = list(ds.image_shape[1:])
    windows = []
    for start in starts:
        frames = [
            predictor._load_frame(array, start + offset, target_shape, downsample)
            for offset in range(window_size)
        ]
        windows.append(torch.stack(frames))
    batch = torch.stack(windows).float()
    batch = ((batch - q_low) / (q_high - q_low + 1e-6)).clamp(0.0, 4.0)
    return batch, ds, q_low, q_high, int(ds.image_shape[0])


def _probe_starts(total_frames: int, window_size: int, count: int) -> list[int]:
    last = max(total_frames - window_size, 0)
    return sorted(set(int(value) for value in np.linspace(0, last, max(1, count))))


def _peak_count(logits: list[Any], threshold: float, pool_kernel: tuple[int, ...]) -> int:
    import torch
    import torch.nn.functional as F

    total = 0
    padding = tuple(value // 2 for value in pool_kernel)
    for value in logits:
        pooled = F.max_pool3d(value, pool_kernel, stride=1, padding=padding)
        total += int(((value == pooled) & (torch.sigmoid(value) >= threshold)).sum().item())
    return total


def _probe_model_count(
    predictor: Any,
    cfg: TTAConfig,
    model: Any,
    dataset_id: str,
    downsample: tuple[int, ...],
    window_size: int,
    device: Any,
) -> int:
    batch0, ds, _, _, total_frames = _load_video_batch(
        predictor, cfg, dataset_id, [0], downsample, window_size
    )
    del batch0
    starts = _probe_starts(total_frames, window_size, cfg.probe_windows)
    voxel_size = tuple(scale * stride for scale, stride in zip(ds.scale, downsample))
    pool = predictor.pool_kernel_from_um(cfg.pool_kernel_um, voxel_size)
    total = 0
    model.eval()
    for start in starts:
        batch, _, _, _, _ = _load_video_batch(
            predictor, cfg, dataset_id, [start], downsample, window_size
        )
        with __import__("torch").no_grad(), __import__("torch").amp.autocast(
            "cuda", enabled=cfg.use_amp
        ):
            _, logits = model.encode(batch.to(device))
        total += _peak_count(logits, cfg.det_threshold, pool)
    return total


def _model_dir(cfg: TTAConfig, variant: str, dataset_id: str) -> Path:
    return cfg.output_dir / "adapted_models" / variant / dataset_id


def _save_model(cfg: TTAConfig, model: Any, variant: str, dataset_id: str) -> Path:
    destination = _model_dir(cfg, variant, dataset_id)
    destination.mkdir(parents=True, exist_ok=True)
    weights = destination / "edge_predictor_best.pth"
    _atomic_torch_save(weights, model.state_dict())
    shutil.copy2(cfg.weights_path.with_name("config.json"), destination / "config.json")
    return weights


def _checkpoint_path(cfg: TTAConfig, variant: str, dataset_id: str) -> Path:
    return _model_dir(cfg, variant, dataset_id) / "adaptation_state.pt"


def _mild_photometric(batch: Any, rng: np.random.Generator) -> Any:
    gain = float(rng.uniform(0.90, 1.10))
    offset = float(rng.uniform(-0.05, 0.05))
    gamma = float(rng.uniform(0.90, 1.10))
    return ((batch.clamp(min=0.0) + 1e-6).pow(gamma) * gain + offset).clamp(0.0, 4.0)


def _adapt_adabn(
    predictor: Any, cfg: TTAConfig, dataset_id: str, device: Any
) -> tuple[Path, dict[str, Any]]:
    import torch
    import torch.nn as nn

    model, window_size, downsample = predictor.load_model(cfg.weights_path, device)
    model.eval()
    bn_layers = [module for module in model.unet.modules() if isinstance(module, nn.BatchNorm3d)]
    if not bn_layers:
        raise RuntimeError("No BatchNorm3d layers found")
    for layer in bn_layers:
        layer.reset_running_stats()
        layer.momentum = None
        layer.train()
    _, _, _, _, total_frames = _load_video_batch(
        predictor, cfg, dataset_id, [0], downsample, window_size
    )
    starts = list(range(0, max(total_frames - window_size + 1, 1), window_size))
    with torch.no_grad():
        for offset in range(0, len(starts), cfg.batch_size):
            _check_stop(cfg)
            batch, _, _, _, _ = _load_video_batch(
                predictor,
                cfg,
                dataset_id,
                starts[offset : offset + cfg.batch_size],
                downsample,
                window_size,
            )
            with torch.amp.autocast("cuda", enabled=cfg.use_amp):
                model.unet(batch.to(device).unsqueeze(2))
    model.eval()
    weights = _save_model(cfg, model, "adabn", dataset_id)
    return weights, {"windows": len(starts), "bn_layers": len(bn_layers)}


def _head_loss(student_logits: list[Any], teacher_logits: list[Any], cfg: TTAConfig, pool):
    import torch
    import torch.nn.functional as F

    positive_losses = []
    negative_losses = []
    positive_count = 0
    padding = tuple(value // 2 for value in pool)
    for student, teacher in zip(student_logits, teacher_logits):
        probability = torch.sigmoid(teacher.detach())
        pooled = F.max_pool3d(probability, pool, stride=1, padding=padding)
        positive = (probability == pooled) & (probability >= cfg.pseudo_threshold)
        background = probability <= cfg.background_threshold
        if positive.any():
            positive_losses.append(F.softplus(-student[positive]).mean())
            positive_count += int(positive.sum().item())
        if background.any():
            negative_losses.append(F.softplus(student[background]).mean())
    if not positive_losses:
        return None, 0
    positive_loss = __import__("torch").stack(positive_losses).mean()
    negative_loss = __import__("torch").stack(negative_losses).mean()
    return positive_loss + cfg.negative_weight * negative_loss, positive_count


def _adapt_head_ema(
    predictor: Any, cfg: TTAConfig, dataset_id: str, device: Any
) -> tuple[Path, dict[str, Any]]:
    import torch

    model, window_size, downsample = predictor.load_model(cfg.weights_path, device)
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    for parameter in model.detect_head.parameters():
        parameter.requires_grad_(True)
    model.eval()
    teacher_head = copy.deepcopy(model.detect_head).to(device).eval()
    optimizer = torch.optim.AdamW(model.detect_head.parameters(), lr=cfg.lr)
    checkpoint = _checkpoint_path(cfg, "head_ema", dataset_id)
    start_step = 0
    fingerprint = cfg.recipe_fingerprint()
    rng = np.random.default_rng(
        cfg.seed + int(hashlib.sha256(dataset_id.encode()).hexdigest()[:8], 16)
    )
    if checkpoint.is_file():
        payload = torch.load(checkpoint, map_location=device, weights_only=False)
        if payload.get("fingerprint") != fingerprint:
            raise RuntimeError(f"Checkpoint recipe mismatch: {checkpoint}")
        model.load_state_dict(payload["model_state"])
        teacher_head.load_state_dict(payload["teacher_head_state"])
        optimizer.load_state_dict(payload["optimizer_state"])
        start_step = int(payload["step"])
        np.random.set_state(payload["numpy_state"])
        random.setstate(payload["python_state"])
        torch.set_rng_state(payload["torch_state"].cpu())
        if torch.cuda.is_available() and payload.get("cuda_state") is not None:
            torch.cuda.set_rng_state_all([value.cpu() for value in payload["cuda_state"]])
        if payload.get("generator_state") is not None:
            rng.bit_generator.state = payload["generator_state"]
        _log(cfg, f"{dataset_id} head_ema: resumed at step {start_step}/{cfg.steps}")

    batch0, ds, _, _, total_frames = _load_video_batch(
        predictor, cfg, dataset_id, [0], downsample, window_size
    )
    del batch0
    voxel_size = tuple(scale * stride for scale, stride in zip(ds.scale, downsample))
    pool = predictor.pool_kernel_from_um(cfg.pool_kernel_um, voxel_size)
    baseline_probe_count = _probe_model_count(
        predictor, cfg, model, dataset_id, downsample, window_size, device
    )
    safe_model_state = copy.deepcopy(model.detect_head.state_dict())
    safe_teacher_state = copy.deepcopy(teacher_head.state_dict())
    last_ratio = 1.0
    def save_checkpoint(step: int, reason: str | None = None) -> None:
        _atomic_torch_save(
            checkpoint,
            {
                "fingerprint": fingerprint,
                "dataset_id": dataset_id,
                "variant": "head_ema",
                "step": step,
                "reason": reason,
                "model_state": model.state_dict(),
                "teacher_head_state": teacher_head.state_dict(),
                "optimizer_state": optimizer.state_dict(),
                "numpy_state": np.random.get_state(),
                "python_state": random.getstate(),
                "torch_state": torch.get_rng_state(),
                "cuda_state": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
                "generator_state": rng.bit_generator.state,
            },
        )

    try:
        for step in range(start_step, cfg.steps):
            _check_stop(cfg)
            max_start = max(total_frames - window_size, 0)
            starts = [int(rng.integers(0, max_start + 1)) for _ in range(cfg.batch_size)]
            weak, _, _, _, _ = _load_video_batch(
                predictor, cfg, dataset_id, starts, downsample, window_size
            )
            strong = _mild_photometric(weak, rng)
            weak = weak.to(device)
            strong = strong.to(device)
            optimizer.zero_grad(set_to_none=True)

            with torch.no_grad(), torch.amp.autocast("cuda", enabled=cfg.use_amp):
                weak_features = model.unet(weak.unsqueeze(2))
                teacher_logits = [teacher_head(weak_features[:, index]) for index in range(window_size)]
                strong_features = model.unet(strong.unsqueeze(2))
            with torch.amp.autocast("cuda", enabled=cfg.use_amp):
                student_logits = [
                    model.detect_head(strong_features[:, index]) for index in range(window_size)
                ]
                loss, positives = _head_loss(student_logits, teacher_logits, cfg, pool)
            if loss is None:
                continue
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.detect_head.parameters(), 1.0)
            optimizer.step()
            with torch.no_grad():
                for teacher_parameter, student_parameter in zip(
                    teacher_head.parameters(), model.detect_head.parameters()
                ):
                    teacher_parameter.mul_(cfg.ema_decay).add_(
                        student_parameter, alpha=1.0 - cfg.ema_decay
                    )

            completed_step = step + 1
            if completed_step % cfg.guard_every == 0 or completed_step == cfg.steps:
                student_state = copy.deepcopy(model.detect_head.state_dict())
                model.detect_head.load_state_dict(teacher_head.state_dict())
                probe_count = _probe_model_count(
                    predictor, cfg, model, dataset_id, downsample, window_size, device
                )
                model.detect_head.load_state_dict(student_state)
                last_ratio = probe_count / max(baseline_probe_count, 1)
                _log(
                    cfg,
                    f"{dataset_id} head_ema step {completed_step}/{cfg.steps}: "
                    f"loss={float(loss.detach()):.5f} positives={positives} probe_ratio={last_ratio:.3f}",
                )
                if not (1.0 - cfg.max_node_drop <= last_ratio <= 1.0 + cfg.max_node_growth):
                    model.detect_head.load_state_dict(safe_model_state)
                    teacher_head.load_state_dict(safe_teacher_state)
                    save_checkpoint(completed_step, reason=f"node_guard_{last_ratio:.3f}")
                    break
                safe_model_state = copy.deepcopy(model.detect_head.state_dict())
                safe_teacher_state = copy.deepcopy(teacher_head.state_dict())
            if completed_step % cfg.checkpoint_every == 0:
                save_checkpoint(completed_step)
    except (KeyboardInterrupt, StopRequested):
        save_checkpoint(max(start_step, step if "step" in locals() else 0), reason="interrupted")
        raise

    model.detect_head.load_state_dict(teacher_head.state_dict())
    weights = _save_model(cfg, model, "head_ema", dataset_id)
    checkpoint.unlink(missing_ok=True)
    return weights, {
        "steps_requested": cfg.steps,
        "baseline_probe_count": baseline_probe_count,
        "last_probe_ratio": last_ratio,
    }


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


def _write_graph_atomic(save_graph: Any, graph: Any, destination: Path) -> None:
    temporary = destination.parent / f".{destination.stem}.building.geff"
    if temporary.exists():
        shutil.rmtree(temporary) if temporary.is_dir() else temporary.unlink()
    destination.parent.mkdir(parents=True, exist_ok=True)
    save_graph(graph, temporary)
    if destination.exists():
        shutil.rmtree(destination) if destination.is_dir() else destination.unlink()
    temporary.replace(destination)


def _copy_graph(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination) if destination.is_dir() else destination.unlink()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)


def _predict_graph(
    predictor: Any,
    cfg: TTAConfig,
    dataset_id: str,
    weights_path: Path,
    destination: Path,
    device: Any,
) -> dict[str, int]:
    import tracksdata as td

    from biohub_tracking.io import save_graph

    model, window_size, downsample = predictor.load_model(weights_path, device)
    predict_cfg = predictor.PredictConfig(
        det_threshold=cfg.det_threshold,
        det_tta=True,
        pool_kernel_um=cfg.pool_kernel_um,
        use_ilp=True,
        ilp_edge_weight=-1.0,
        ilp_appearance_weight=0.0,
        ilp_disappearance_weight=2.0,
        ilp_division_weight=1.2,
    )
    coords, edges = predictor.predict_video(
        model,
        cfg.data_dir / dataset_id,
        device,
        predict_cfg,
        window_size=window_size,
        downsample=downsample,
    )
    raw_nodes = int(len(coords))
    graph = predictor.build_graph(coords, edges)
    if graph.num_edges() > 0:
        solver = td.solvers.ILPSolver(
            edge_weight=-1.0 * td.EdgeAttr("edge_prob"),
            appearance_weight=0.0,
            disappearance_weight=2.0,
            division_weight=1.2,
        )
        with predictor.suppress_output():
            graph = solver.solve(graph)
    _write_graph_atomic(save_graph, graph, destination)
    result = {"raw_nodes": raw_nodes, "nodes": int(graph.num_nodes()), "edges": int(graph.num_edges())}
    del model, graph
    __import__("torch").cuda.empty_cache()
    return result


def _record_key(variant: str, dataset_id: str) -> str:
    return f"{variant}/{dataset_id}"


def _prediction_path(cfg: TTAConfig, variant: str, dataset_id: str) -> Path:
    return cfg.output_dir / "predictions" / variant / f"{dataset_id}.geff"


def _candidate_path(cfg: TTAConfig, variant: str, dataset_id: str) -> Path:
    return cfg.output_dir / "candidates" / variant / f"{dataset_id}.geff"


def _run_one(
    predictor: Any,
    cfg: TTAConfig,
    state: dict[str, Any],
    variant: str,
    dataset_id: str,
    device: Any,
) -> None:
    key = _record_key(variant, dataset_id)
    destination = _prediction_path(cfg, variant, dataset_id)
    if state["records"].get(key, {}).get("status") == "complete" and _graph_valid(destination):
        _log(cfg, f"reuse {key}")
        return
    _check_stop(cfg)
    state["records"][key] = {"status": "running", "started_at": time.time()}
    save_state(cfg, state)
    _log(cfg, f"start {key}")

    adaptation: dict[str, Any] = {}
    if variant == "baseline":
        stats = _predict_graph(
            predictor, cfg, dataset_id, cfg.weights_path, destination, device
        )
        selected = "baseline"
    else:
        adapted_weights = _model_dir(cfg, variant, dataset_id) / "edge_predictor_best.pth"
        if adapted_weights.is_file() and adapted_weights.with_name("config.json").is_file():
            adaptation = {"reused_adapted_weights": True}
            _log(cfg, f"reuse adapted weights {variant}/{dataset_id}")
        else:
            if variant == "adabn":
                adapted_weights, adaptation = _adapt_adabn(predictor, cfg, dataset_id, device)
            elif variant == "head_ema":
                adapted_weights, adaptation = _adapt_head_ema(predictor, cfg, dataset_id, device)
            else:
                raise ValueError(variant)
        candidate = _candidate_path(cfg, variant, dataset_id)
        candidate_stats = _predict_graph(
            predictor, cfg, dataset_id, adapted_weights, candidate, device
        )
        baseline_key = _record_key("baseline", dataset_id)
        baseline_stats = state["records"].get(baseline_key, {}).get("stats")
        if not baseline_stats:
            raise RuntimeError(f"Missing baseline statistics for {dataset_id}")
        ratio = candidate_stats["raw_nodes"] / max(int(baseline_stats["raw_nodes"]), 1)
        guard_pass = 1.0 - cfg.max_node_drop <= ratio <= 1.0 + cfg.max_node_growth
        if guard_pass:
            _copy_graph(candidate, destination)
            stats = candidate_stats
            selected = variant
        else:
            _copy_graph(_prediction_path(cfg, "baseline", dataset_id), destination)
            stats = dict(baseline_stats)
            selected = "baseline_fallback"
        adaptation.update({"candidate_stats": candidate_stats, "full_node_ratio": ratio, "guard_pass": guard_pass})

    state["records"][key] = {
        "status": "complete",
        "finished_at": time.time(),
        "selected": selected,
        "stats": stats,
        "adaptation": adaptation,
        "prediction": str(destination),
    }
    save_state(cfg, state)
    _log(cfg, f"complete {key}: selected={selected} nodes={stats['raw_nodes']} edges={stats['edges']}")


def _score_complete_variants(cfg: TTAConfig, state: dict[str, Any]) -> None:
    for variant in cfg.variants:
        directory = cfg.output_dir / "predictions" / variant
        paths = [_prediction_path(cfg, variant, dataset_id) for dataset_id in cfg.dataset_ids]
        if not all(_graph_valid(path) for path in paths):
            continue
        output = cfg.output_dir / "metrics" / f"{variant}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        environment = os.environ.copy()
        environment["BIOHUB_DATA_DIR"] = str(cfg.data_dir)
        command = [
            sys.executable,
            str(cfg.repo_root / "tools" / "score_geffs.py"),
            str(directory),
            "--out",
            str(output),
        ]
        completed = subprocess.run(command, cwd=cfg.repo_root, env=environment, check=True)
        del completed
        metrics = json.loads(output.read_text(encoding="utf-8"))
        state["metrics"][variant] = metrics["summary"]
        save_state(cfg, state)


def _write_result(cfg: TTAConfig, state: dict[str, Any]) -> None:
    baseline = state.get("metrics", {}).get("baseline", {})
    lines = [
        "# Friend A B5 — resumable test-time adaptation",
        "",
        "Adaptation used target images only. GT was opened only by the official scorer after prediction.",
        "",
        "| variant | official score | delta | edge | node recall | division J |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    baseline_score = baseline.get("score")
    for variant in cfg.variants:
        metrics = state.get("metrics", {}).get(variant)
        if not metrics:
            lines.append(f"| {variant} | pending | | | | |")
            continue
        delta = metrics["score"] - baseline_score if baseline_score is not None else float("nan")
        lines.append(
            f"| {variant} | {metrics['score']:.4f} | {delta:+.4f} | "
            f"{metrics['edge_jaccard']:.4f} | {metrics['node_recall']:.4f} | "
            f"{metrics['division_jaccard']:.4f} |"
        )
    lines.extend(
        [
            "",
            "Gate: an adapted variant must beat baseline by at least +0.005 on all 12 LOEO-44b6 videos.",
            "No leaderboard submission is performed by this notebook.",
        ]
    )
    (cfg.output_dir / "result.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pipeline(cfg: TTAConfig) -> dict[str, Any]:
    import torch

    if not cfg.run_pipeline:
        _log(cfg, "BIOHUB_TTA_RUN=0: preflight only")
        return load_state(cfg)
    predictor = _install_import_paths(cfg)
    state = load_state(cfg)
    state["status"] = "running"
    save_state(cfg, state)
    device = torch.device("cuda")
    completed_this_run = 0
    try:
        # Baseline must exist first because every unsupervised node-count guard uses it.
        ordered_variants = [item for item in VARIANTS if item in cfg.variants]
        for variant in ordered_variants:
            for dataset_id in cfg.dataset_ids:
                key = _record_key(variant, dataset_id)
                already_complete = state["records"].get(key, {}).get("status") == "complete"
                if not already_complete and cfg.max_videos_per_run and completed_this_run >= cfg.max_videos_per_run:
                    state["status"] = "paused_by_max_videos"
                    save_state(cfg, state)
                    _write_result(cfg, state)
                    return state
                _run_one(predictor, cfg, state, variant, dataset_id, device)
                if not already_complete:
                    completed_this_run += 1
        _score_complete_variants(cfg, state)
        state["status"] = "complete" if len(state.get("metrics", {})) == len(cfg.variants) else "partial"
        save_state(cfg, state)
    except (KeyboardInterrupt, StopRequested) as error:
        state["status"] = "stopped_safely"
        state["stop_reason"] = str(error)
        save_state(cfg, state)
        _log(cfg, f"stopped safely: {error}")
    finally:
        _write_result(cfg, state)
        torch.cuda.empty_cache()
    return state


def compact_status(cfg: TTAConfig) -> dict[str, Any]:
    state = load_state(cfg)
    complete = sum(1 for row in state.get("records", {}).values() if row.get("status") == "complete")
    total = len(cfg.dataset_ids) * len(cfg.variants)
    return {
        "status": state.get("status", "not_started"),
        "completed_predictions": f"{complete}/{total}",
        "metrics": state.get("metrics", {}),
        "stop_marker": stop_path(cfg).exists(),
        "output_dir": str(cfg.output_dir),
    }
