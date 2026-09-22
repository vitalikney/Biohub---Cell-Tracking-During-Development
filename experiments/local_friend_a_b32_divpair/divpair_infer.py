"""B32 division-pair model and input construction.

The network keeps the published DivNet U-Net/GAP trunk, expands the input from
five to seven channels (four image lags plus parent/daughter markers), and
concatenates standardised geometric features before the final linear head.

The initial state is deliberately equivalent to the parent-only DivNet: the
first five input channels and the original head weights are copied, while the
two new marker channels and geometry weights start at zero.
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Callable

import numpy as np
import torch


class ConvBlock(torch.nn.Module):
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


class DivPairClassifier(torch.nn.Module):
    """DivNet-compatible 3-D U-Net with a pair-aware geometry head."""

    def __init__(self, geometry_dim: int, in_channels: int = 7, base_channels: int = 16) -> None:
        super().__init__()
        c = int(base_channels)
        self.geometry_dim = int(geometry_dim)
        self.enc1 = ConvBlock(in_channels, c)
        self.pool1 = torch.nn.MaxPool3d(2, 2)
        self.enc2 = ConvBlock(c, c * 2)
        self.pool2 = torch.nn.MaxPool3d(2, 2)
        self.enc3 = ConvBlock(c * 2, c * 4)
        self.pool3 = torch.nn.MaxPool3d(2, 2)
        self.bottleneck = ConvBlock(c * 4, c * 8)
        self.up3 = torch.nn.ConvTranspose3d(c * 8, c * 4, 2, 2)
        self.dec3 = ConvBlock(c * 8, c * 4)
        self.up2 = torch.nn.ConvTranspose3d(c * 4, c * 2, 2, 2)
        self.dec2 = ConvBlock(c * 4, c * 2)
        self.up1 = torch.nn.ConvTranspose3d(c * 2, c, 2, 2)
        self.dec1 = ConvBlock(c * 2, c)
        self.gap = torch.nn.AdaptiveAvgPool3d((1, 1, 1))
        self.head = torch.nn.Linear(c + self.geometry_dim, 1)

    def image_features(self, value: torch.Tensor) -> torch.Tensor:
        e1 = self.enc1(value)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))
        bottleneck = self.bottleneck(self.pool3(e3))
        d3 = self.dec3(torch.cat([self.up3(bottleneck), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        return self.gap(d1).flatten(1)

    def forward(self, value: torch.Tensor, geometry: torch.Tensor) -> torch.Tensor:
        if geometry.ndim != 2 or geometry.shape[1] != self.geometry_dim:
            raise ValueError(f"geometry shape {tuple(geometry.shape)} != (*, {self.geometry_dim})")
        return self.head(torch.cat([self.image_features(value), geometry], dim=1))


def load_parent_checkpoint(path: Path) -> tuple[dict[str, torch.Tensor], dict]:
    payload = torch.load(path, map_location="cpu", weights_only=False)
    state = payload.get("model_state", payload) if isinstance(payload, dict) else payload
    config = payload.get("config", {}) if isinstance(payload, dict) else {}
    return dict(state), dict(config)


def initialise_from_divnet(
    model: DivPairClassifier,
    checkpoint: Path,
) -> dict[str, object]:
    """Copy the five-channel DivNet state and zero all new pair inputs."""
    state, config = load_parent_checkpoint(checkpoint)
    target = model.state_dict()
    copied: list[str] = []
    for key, value in state.items():
        if key == "enc1.block.0.weight":
            if value.shape[1] != 5 or target[key].shape[1] != 7:
                raise RuntimeError(f"Unexpected first-convolution shapes: {value.shape} -> {target[key].shape}")
            target[key].zero_()
            target[key][:, :5].copy_(value)
            copied.append(key)
        elif key == "head.weight":
            if value.shape[1] > target[key].shape[1]:
                raise RuntimeError(f"Unexpected head shapes: {value.shape} -> {target[key].shape}")
            target[key].zero_()
            target[key][:, : value.shape[1]].copy_(value)
            copied.append(key)
        elif key in target and target[key].shape == value.shape:
            target[key].copy_(value)
            copied.append(key)
    model.load_state_dict(target, strict=True)
    required = set(state) - {"head.weight"}
    missing = sorted(required - set(copied))
    if missing:
        raise RuntimeError(f"DivNet initialisation missed keys: {missing[:5]}")
    return {
        "checkpoint": str(Path(checkpoint).resolve()),
        "copied_tensors": len(copied),
        "source_config": config,
    }


class FrameReader:
    """Small Zarr reader compatible with ``tools.divnet_infer``."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.arrays: dict[str, object] = {}

    def __call__(self, dataset: str, t: int, frame_cache: dict) -> np.ndarray:
        import zarr

        if dataset not in self.arrays:
            self.arrays[dataset] = zarr.open(str(self.data_dir / f"{dataset}.zarr" / "0"), mode="r")
        array = self.arrays[dataset]
        index = max(0, min(int(t), int(array.shape[0]) - 1))
        if index not in frame_cache:
            frame_cache[index] = np.asarray(array[index])
        return frame_cache[index]


def gaussian_marker(
    shape: tuple[int, int, int],
    centre: tuple[int, int, int],
    sigma: tuple[float, float, float],
) -> np.ndarray:
    axes = [np.arange(size, dtype=np.float32) - float(point) for size, point in zip(shape, centre)]
    zz, yy, xx = np.meshgrid(*axes, indexing="ij")
    distance = (zz / sigma[0]) ** 2 + (yy / sigma[1]) ** 2 + (xx / sigma[2]) ** 2
    return np.exp(-0.5 * distance).astype(np.float32)


class PairInputBuilder:
    """Build seven-channel crops while caching normalised frames per video."""

    def __init__(self, data_dir: Path, parent_checkpoint: Path) -> None:
        from tools import divnet_infer

        _, config = load_parent_checkpoint(parent_checkpoint)
        self.divnet = divnet_infer
        self.config = config
        self.reader = FrameReader(data_dir)
        self.bundle: dict[str, object] = {"config": config, "prepared_frames": {}}
        self.frame_cache: dict[object, np.ndarray] = {}
        input_cfg = config.get("input", {})
        self.pool_xy = int(input_cfg.get("pool_xy", 4))
        self.shape = (
            int(input_cfg.get("crop_z", 16)),
            int(input_cfg.get("crop_yx", 32)),
            int(input_cfg.get("crop_yx", 32)),
        )
        self.sigma = tuple(float(v) for v in input_cfg.get("marker_sigma", (1.5, 2.0, 2.0)))

    def reset_video(self) -> None:
        self.bundle["prepared_frames"] = {}
        self.frame_cache = {}

    def _daughter_marker(self, parent: dict, daughter: dict) -> np.ndarray:
        parent_global = (
            int(round(float(parent["z"]))),
            int(round(float(parent["y"]) / self.pool_xy)),
            int(round(float(parent["x"]) / self.pool_xy)),
        )
        daughter_global = (
            int(round(float(daughter["z"]))),
            int(round(float(daughter["y"]) / self.pool_xy)),
            int(round(float(daughter["x"]) / self.pool_xy)),
        )
        centre = tuple(
            int(size // 2 + child - par)
            for size, child, par in zip(self.shape, daughter_global, parent_global)
        )
        return gaussian_marker(self.shape, centre, self.sigma)

    def build(self, dataset: str, t: int, parent: dict, daughter1: dict, daughter2: dict) -> np.ndarray:
        base = self.divnet.prepare_divnet_input(
            dataset,
            int(t),
            parent,
            self.bundle,
            self.frame_cache,
            self.reader,
        )
        sample = np.concatenate(
            [
                base,
                self._daughter_marker(parent, daughter1)[None],
                self._daughter_marker(parent, daughter2)[None],
            ],
            axis=0,
        )
        if sample.shape != (7, *self.shape) or not np.isfinite(sample).all():
            raise RuntimeError(f"Invalid DivPair sample: {sample.shape}")
        return sample.astype(np.float32, copy=False)


def augment_batch(images: torch.Tensor) -> torch.Tensor:
    """Random member of the eight axis-reflection group plus mild intensity jitter."""
    result = images.clone()
    for dimension in (2, 3, 4):
        mask = torch.rand(result.shape[0], device=result.device) < 0.5
        if bool(mask.any()):
            result[mask] = torch.flip(result[mask], dims=(dimension,))
    gain = torch.empty((result.shape[0], 1, 1, 1, 1), device=result.device).uniform_(0.9, 1.1)
    offset = torch.empty((result.shape[0], 1, 1, 1, 1), device=result.device).uniform_(-0.05, 0.05)
    result[:, :4] = result[:, :4] * gain + offset
    return result


def load_model_checkpoint(path: Path, device: torch.device) -> tuple[DivPairClassifier, dict]:
    payload = torch.load(path, map_location="cpu", weights_only=False)
    geometry_dim = int(payload["geometry_dim"])
    model = DivPairClassifier(geometry_dim=geometry_dim)
    model.load_state_dict(payload["model_state"], strict=True)
    model.to(device).eval()
    return model, payload


def probability_batch(
    model: DivPairClassifier,
    images: np.ndarray,
    geometry: np.ndarray,
    device: torch.device,
    amp: bool = True,
) -> np.ndarray:
    x = torch.from_numpy(np.asarray(images)).to(device=device, dtype=torch.float32)
    g = torch.from_numpy(np.asarray(geometry)).to(device=device, dtype=torch.float32)
    enabled = bool(amp and device.type == "cuda")
    with torch.inference_mode(), torch.autocast(
        device_type=device.type,
        dtype=torch.float16,
        enabled=enabled,
    ):
        values = torch.sigmoid(model(x, g)).flatten()
    return values.float().cpu().numpy()


def lru_put(cache: OrderedDict, key: object, value: object, maximum: int) -> None:
    cache[key] = value
    cache.move_to_end(key)
    while len(cache) > maximum:
        cache.popitem(last=False)
