"""Inference for the public ``giorgosi/biohub-divnet-v2`` checkpoint.

The dataset manifest is the contract: four image channels at lags -1, 0, +1,
+2 plus a Gaussian centre marker, XY mean pooling by four, a 16x32x32 crop,
percentile normalisation, and a small 3-D U-Net followed by global pooling.

``read_test_frame`` is supplied by the caller (the public pipeline notebook or
the local B20 scorer). This module raises on an incompatible checkpoint or
tensor shape; a silent geometric fallback would invalidate B20.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

import numpy as np
import torch


class _DivNetConvBlock(torch.nn.Module):
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.block = torch.nn.Sequential(
            torch.nn.Conv3d(in_channels, out_channels, 3, padding=1, bias=False),
            torch.nn.GroupNorm(min(8, out_channels), out_channels),
            torch.nn.SiLU(inplace=True),
            torch.nn.Conv3d(out_channels, out_channels, 3, padding=1, bias=False),
            torch.nn.GroupNorm(min(8, out_channels), out_channels),
            torch.nn.SiLU(inplace=True),
        )

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        return self.block(value)


class DivNetMitosisClassifier(torch.nn.Module):
    """Architecture reconstructed exactly from the public checkpoint shapes."""

    def __init__(self, in_channels: int = 5, base_channels: int = 16) -> None:
        super().__init__()
        c = int(base_channels)
        self.enc1 = _DivNetConvBlock(in_channels, c)
        self.pool1 = torch.nn.MaxPool3d(2, 2)
        self.enc2 = _DivNetConvBlock(c, c * 2)
        self.pool2 = torch.nn.MaxPool3d(2, 2)
        self.enc3 = _DivNetConvBlock(c * 2, c * 4)
        self.pool3 = torch.nn.MaxPool3d(2, 2)
        self.bottleneck = _DivNetConvBlock(c * 4, c * 8)
        self.up3 = torch.nn.ConvTranspose3d(c * 8, c * 4, 2, 2)
        self.dec3 = _DivNetConvBlock(c * 8, c * 4)
        self.up2 = torch.nn.ConvTranspose3d(c * 4, c * 2, 2, 2)
        self.dec2 = _DivNetConvBlock(c * 4, c * 2)
        self.up1 = torch.nn.ConvTranspose3d(c * 2, c, 2, 2)
        self.dec1 = _DivNetConvBlock(c * 2, c)
        self.gap = torch.nn.AdaptiveAvgPool3d((1, 1, 1))
        self.head = torch.nn.Linear(c, 1)

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        e1 = self.enc1(value)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))
        bottleneck = self.bottleneck(self.pool3(e3))
        d3 = self.dec3(torch.cat([self.up3(bottleneck), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        return self.head(self.gap(d1).flatten(1))


def _checkpoint_candidates() -> list[Path]:
    root = Path(__file__).resolve().parent.parent
    explicit = os.environ.get("BIOHUB_DIVNET_CHECKPOINT", "").strip()
    candidates = [Path(explicit)] if explicit else []
    candidates.extend(
        [
            root / "external" / "giorgosi__biohub-divnet-v2" / "best_overall.pt",
            root / "external" / "giorgosi__biohub-divnet-v2" / "weights" / "divnet" / "best_overall.pt",
            Path("/kaggle/input/biohub-divnet-v2/best_overall.pt"),
            Path("/kaggle/input/biohub-divnet-v2/weights/divnet/best_overall.pt"),
            Path("/kaggle/input/datasets/giorgosi/biohub-divnet-v2/best_overall.pt"),
            Path("/kaggle/input/datasets/giorgosi/biohub-divnet-v2/weights/divnet/best_overall.pt"),
        ]
    )
    return candidates


def load_divnet_mitosis_model(checkpoint: Path | None = None) -> dict[str, object]:
    if not globals().get("DIVNET_VERIFY", True):
        raise RuntimeError("DivNet is disabled by configuration")
    path = Path(checkpoint) if checkpoint is not None else next(
        (item for item in _checkpoint_candidates() if item.is_file()), None
    )
    if path is None:
        checked = "\n".join(str(item) for item in _checkpoint_candidates())
        raise FileNotFoundError(f"DivNet checkpoint not found. Checked:\n{checked}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    payload = torch.load(path, map_location="cpu", weights_only=False)
    state = payload.get("model_state", payload) if isinstance(payload, dict) else payload
    config = payload.get("config", {}) if isinstance(payload, dict) else {}
    model_cfg = config.get("model", {}) if isinstance(config, dict) else {}
    model = DivNetMitosisClassifier(
        in_channels=int(model_cfg.get("in_channels", 5)),
        base_channels=int(model_cfg.get("base_channels", 16)),
    )
    model.load_state_dict(state, strict=True)
    model.to(device).eval()
    return {
        "model": model,
        "device": device,
        "torch": torch,
        "path": path.resolve(),
        "config": config,
        "prepared_frames": {},
    }


def _pool_xy(frame: np.ndarray, factor: int) -> np.ndarray:
    frame = np.asarray(frame)
    if factor <= 1:
        return frame.astype(np.float32, copy=False)
    z, y, x = frame.shape
    y2, x2 = (y // factor) * factor, (x // factor) * factor
    value = frame[:, :y2, :x2].astype(np.float32, copy=False)
    return value.reshape(z, y2 // factor, factor, x2 // factor, factor).mean(axis=(2, 4))


def _normalise(frame: np.ndarray, lo_pct: float, hi_pct: float, clip: tuple[float, float]) -> np.ndarray:
    value = np.asarray(frame, dtype=np.float32)
    lo, hi = np.percentile(value, [lo_pct, hi_pct])
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return np.zeros_like(value)
    return np.clip((value - float(lo)) / (float(hi) - float(lo)), clip[0], clip[1]).astype(np.float32)


def _crop_with_padding(frame: np.ndarray, centre: tuple[int, int, int], shape: tuple[int, int, int]) -> np.ndarray:
    result = np.zeros(shape, dtype=np.float32)
    source_slices: list[slice] = []
    target_slices: list[slice] = []
    for coordinate, size, limit in zip(centre, shape, frame.shape):
        start = coordinate - size // 2
        stop = start + size
        source_start, source_stop = max(0, start), min(limit, stop)
        target_start = source_start - start
        target_stop = target_start + max(0, source_stop - source_start)
        source_slices.append(slice(source_start, source_stop))
        target_slices.append(slice(target_start, target_stop))
    result[tuple(target_slices)] = frame[tuple(source_slices)]
    return result


def _marker(shape: tuple[int, int, int], sigma: tuple[float, float, float]) -> np.ndarray:
    axes = [np.arange(size, dtype=np.float32) - size // 2 for size in shape]
    zz, yy, xx = np.meshgrid(*axes, indexing="ij")
    distance = (zz / sigma[0]) ** 2 + (yy / sigma[1]) ** 2 + (xx / sigma[2]) ** 2
    return np.exp(-0.5 * distance).astype(np.float32)


def prepare_divnet_input(
    dataset: str,
    t: int,
    parent_node: dict[str, object],
    divnet_bundle: dict[str, object],
    frame_cache: dict[object, np.ndarray],
    read_frame: Callable[[str, int, dict], np.ndarray] | None = None,
) -> np.ndarray:
    """Build one ``(5, 16, 32, 32)`` sample from the manifest recipe."""
    cfg = divnet_bundle.get("config", {})
    input_cfg = cfg.get("input", {}) if isinstance(cfg, dict) else {}
    norm_cfg = cfg.get("normalization", {}) if isinstance(cfg, dict) else {}
    lags = tuple(int(value) for value in input_cfg.get("image_lags", (-1, 0, 1, 2)))
    pool_xy = int(input_cfg.get("pool_xy", 4))
    shape = (
        int(input_cfg.get("crop_z", 16)),
        int(input_cfg.get("crop_yx", 32)),
        int(input_cfg.get("crop_yx", 32)),
    )
    sigma = tuple(float(value) for value in input_cfg.get("marker_sigma", (1.5, 2.0, 2.0)))
    clip = tuple(float(value) for value in norm_cfg.get("clip", (-0.5, 6.0)))
    reader = read_frame or globals().get("read_test_frame")
    if reader is None:
        raise RuntimeError("DivNet needs a read_frame callback or a global read_test_frame")
    prepared = divnet_bundle.setdefault("prepared_frames", {})
    channels: list[np.ndarray] = []
    for lag in lags:
        frame_t = max(0, int(t) + lag)
        key = (dataset, frame_t)
        if key not in prepared:
            raw = reader(dataset, frame_t, frame_cache)
            pooled = _pool_xy(raw, pool_xy)
            prepared[key] = _normalise(
                pooled,
                float(norm_cfg.get("lo_pct", 50.0)),
                float(norm_cfg.get("hi_pct", 99.5)),
                clip,
            )
            frame_cache.pop(frame_t, None)
        centre = (
            int(round(float(parent_node["z"]))),
            int(round(float(parent_node["y"]) / pool_xy)),
            int(round(float(parent_node["x"]) / pool_xy)),
        )
        channels.append(_crop_with_padding(prepared[key], centre, shape))
    channels.append(_marker(shape, sigma))
    sample = np.stack(channels, axis=0)
    if sample.shape != (5, *shape) or not np.isfinite(sample).all():
        raise RuntimeError(f"Invalid DivNet input: shape={sample.shape}, finite={np.isfinite(sample).all()}")
    return sample


def divnet_score_division(
    dataset: str,
    t: int,
    parent_node: dict[str, object],
    daughter1: dict[str, object],
    daughter2: dict[str, object],
    divnet_bundle: dict[str, object],
    frame_cache: dict[object, np.ndarray],
    read_frame: Callable[[str, int, dict], np.ndarray] | None = None,
) -> float:
    """Return the parent division probability; daughter arguments preserve the public API."""
    del daughter1, daughter2
    sample = prepare_divnet_input(dataset, t, parent_node, divnet_bundle, frame_cache, read_frame)
    torch_mod = divnet_bundle["torch"]
    tensor = torch_mod.from_numpy(sample).unsqueeze(0).to(
        device=divnet_bundle["device"], dtype=torch_mod.float32
    )
    with torch_mod.inference_mode():
        logit = divnet_bundle["model"](tensor)
        probability = float(torch_mod.sigmoid(logit).item())
    if not np.isfinite(probability):
        raise RuntimeError("DivNet produced a non-finite probability")
    return probability


DIVNET_BUNDLE = None
