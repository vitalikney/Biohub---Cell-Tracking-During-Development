"""Self-contained AdaBN cell for the public exp29 primary and secondary.

This file is deliberately valid as a single Kaggle notebook cell.  It reads
only an unlabelled ``.zarr`` video, reloads each untouched checkpoint for every
video, recalibrates ``BatchNorm3d`` running statistics, and writes a checkpoint
pair for that video.  The caller remains responsible for counting public-stack
detections and applying the registered node-ratio guard [0.90, 1.05].
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Callable


def _adabn_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _adabn_atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, path)


def _adabn_atomic_torch_save(path: Path, payload: Any) -> None:
    import torch

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    torch.save(payload, temporary)
    os.replace(temporary, path)


def _load_public_predictor(repo_dir: str | Path):
    """Import the materialised support-pack predictor after its source path."""
    repo_dir = Path(repo_dir).resolve()
    scripts = repo_dir / "scripts"
    source = repo_dir / "src"
    for entry in reversed((str(scripts), str(source))):
        if entry not in sys.path:
            sys.path.insert(0, entry)

    # Some support-pack snapshots omit these re-exports.
    import biohub_tracking.models as model_namespace
    from biohub_tracking.models.simple_node_transformer import SimpleNodeTransformer
    from biohub_tracking.models.temporal_unet import TemporalUNet3D

    model_namespace.SimpleNodeTransformer = SimpleNodeTransformer
    model_namespace.TemporalUNet3D = TemporalUNet3D
    return importlib.import_module("predict_unet_transformer")


def _adabn_video_batch(
    predictor: Any,
    video_path: Path,
    starts: list[int],
    downsample: tuple[int, ...],
    window_size: int,
):
    import torch
    import zarr

    ds = predictor.open_dataset(
        video_path, normalize=False, load_image=False, downsample=downsample
    )
    if "0.001" not in ds.quantiles or "0.999" not in ds.quantiles:
        raise ValueError(f"{video_path}: missing q0.001/q0.999 image statistics")
    array = zarr.open_group(str(ds.zarr_path), mode="r")["0"]
    target_shape = list(ds.image_shape[1:])
    q_low = float(ds.quantiles["0.001"])
    q_high = float(ds.quantiles["0.999"])
    windows = []
    for start in starts:
        frames = [
            predictor._load_frame(array, start + offset, target_shape, downsample)
            for offset in range(window_size)
        ]
        windows.append(torch.stack(frames))
    batch = torch.stack(windows).float()
    # This is byte-for-byte the B5 normalisation recipe.
    batch = ((batch - q_low) / (q_high - q_low + 1e-6)).clamp(0.0, 4.0)
    return batch, int(ds.image_shape[0])


def adapt_adabn_checkpoint(
    *,
    predictor: Any,
    video_path: str | Path,
    source_weights: str | Path,
    output_dir: str | Path,
    batch_size: int = 2,
    use_amp: bool = True,
    stop_check: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Recalibrate one checkpoint on one unlabelled video.

    The registered B5 recipe is preserved: non-overlapping temporal windows in
    increasing order, batch size 2, reset BN statistics, and ``momentum=None``.
    No optimiser, gradients, pseudo-labels, GEFF files, or model parameters are
    used.  The returned checkpoint contains only the newly accumulated BN
    buffers in addition to the original parameters.
    """
    import torch
    import torch.nn as nn

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    video_path = Path(video_path)
    source_weights = Path(source_weights)
    output_dir = Path(output_dir)
    source_config = source_weights.with_name("config.json")
    if not source_weights.is_file() or not source_config.is_file():
        raise FileNotFoundError(f"incomplete checkpoint pair: {source_weights}")
    if not torch.cuda.is_available():
        raise RuntimeError("AdaBN regression run requires CUDA")

    device = torch.device("cuda")
    model, window_size, downsample = predictor.load_model(source_weights, device)
    model.eval()
    bn_layers = [module for module in model.unet.modules() if isinstance(module, nn.BatchNorm3d)]
    if not bn_layers:
        raise RuntimeError(f"no BatchNorm3d layers in {source_weights}")
    for layer in bn_layers:
        layer.reset_running_stats()
        layer.momentum = None
        layer.train()

    first_batch, total_frames = _adabn_video_batch(
        predictor, video_path, [0], downsample, window_size
    )
    del first_batch
    starts = list(range(0, max(total_frames - window_size + 1, 1), window_size))
    started = time.perf_counter()
    with torch.no_grad():
        for offset in range(0, len(starts), batch_size):
            if stop_check is not None:
                stop_check()
            batch, _ = _adabn_video_batch(
                predictor,
                video_path,
                starts[offset : offset + batch_size],
                downsample,
                window_size,
            )
            with torch.amp.autocast("cuda", enabled=use_amp):
                model.unet(batch.to(device).unsqueeze(2))
            del batch

    model.eval()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_weights = output_dir / "edge_predictor_best.pth"
    _adabn_atomic_torch_save(output_weights, model.state_dict())
    shutil.copy2(source_config, output_dir / "config.json")
    result = {
        "source_weights": str(source_weights),
        "source_sha256": _adabn_sha256(source_weights),
        "adapted_weights": str(output_weights),
        "adapted_sha256": _adabn_sha256(output_weights),
        "video": str(video_path),
        "window_size": int(window_size),
        "downsample": list(downsample),
        "windows": len(starts),
        "batch_size": int(batch_size),
        "bn_layers": len(bn_layers),
        "momentum": None,
        "seconds": time.perf_counter() - started,
    }
    _adabn_atomic_json(output_dir / "adabn_receipt.json", result)
    del model
    torch.cuda.empty_cache()
    return result


def adapt_public_pair_for_video(
    *,
    repo_dir: str | Path,
    video_path: str | Path,
    primary_weights: str | Path,
    secondary_weights: str | Path,
    output_dir: str | Path,
    batch_size: int = 2,
    use_amp: bool = True,
    stop_check: Callable[[], None] | None = None,
) -> dict[str, Any]:
    """Return per-video AdaBN weights for both public exp29 models."""
    output_dir = Path(output_dir)
    predictor = _load_public_predictor(repo_dir)
    started = time.perf_counter()
    primary = adapt_adabn_checkpoint(
        predictor=predictor,
        video_path=video_path,
        source_weights=primary_weights,
        output_dir=output_dir / "primary",
        batch_size=batch_size,
        use_amp=use_amp,
        stop_check=stop_check,
    )
    secondary = adapt_adabn_checkpoint(
        predictor=predictor,
        video_path=video_path,
        source_weights=secondary_weights,
        output_dir=output_dir / "secondary",
        batch_size=batch_size,
        use_amp=use_amp,
        stop_check=stop_check,
    )
    receipt = {
        "recipe": "B5 AdaBN: reset BatchNorm3d, momentum=None, ordered non-overlapping windows",
        "labels_used": False,
        "primary": primary,
        "secondary": secondary,
        "seconds": time.perf_counter() - started,
    }
    _adabn_atomic_json(output_dir / "pair_receipt.json", receipt)
    return receipt


def adabn_node_guard(
    baseline_nodes: int,
    adapted_nodes: int,
    lower: float = 0.90,
    upper: float = 1.05,
) -> tuple[bool, float]:
    """Label-free exp38 guard; false means use the untouched exp29 graph."""
    ratio = float(adapted_nodes) / max(int(baseline_nodes), 1)
    return lower <= ratio <= upper, ratio

