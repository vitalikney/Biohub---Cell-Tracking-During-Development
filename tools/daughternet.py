"""DaughterNet: 3-class node classifier (continuation / parent / daughter) for the L2 division stage.

Shared contract between training (Kaggle K-DN kernels), the submission kernel patch (--patch divinsert) and the laptop
replay. The input sample is EXACTLY the DivNet manifest contract of tools/divnet_infer.prepare_divnet_input: image
channels at lags -1, 0, +1, +2 around the node's frame t, XY mean-pool by 4, a 16x32x32 crop centred on the node,
percentile 50/99.5 normalisation clipped to [-0.5, 6], plus one gaussian centre marker -> (5, 16, 32, 32).
The network is the DivNet UNet-GAP body with a 3-logit head. Class order is fixed: CLASSES = (cont, parent, daughter).
  parent   = GT dividing node at the last frame before the split (label at its own t)
  daughter = GT daughter node at its first frame (label at its own t)
  cont     = annotated node with in-degree = out-degree = 1, >= 2 frames from any GT division
Scoring averages softmax over the loaded fold models (ensemble) or uses one fold model per video (OOF).
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Sequence

import numpy as np
import torch

try:  # repo layout
    from tools.divnet_infer import _DivNetConvBlock, prepare_divnet_input
except Exception:  # embedded in a notebook cell after divnet_infer's code (names already global)
    _DivNetConvBlock = globals().get("_DivNetConvBlock")
    prepare_divnet_input = globals().get("prepare_divnet_input")

CLASSES = ("cont", "parent", "daughter")
DEFAULT_CFG = {
    "input": {"image_lags": [-1, 0, 1, 2], "pool_xy": 4, "crop_z": 16, "crop_yx": 32, "marker_sigma": [1.5, 2.0, 2.0]},
    "normalization": {"lo_pct": 50.0, "hi_pct": 99.5, "clip": [-0.5, 6.0]},
    "model": {"in_channels": 5, "base_channels": 16, "n_classes": 3},
}


class DaughterNet(torch.nn.Module):
    """DivNet UNet-GAP body (same layer names as DivNetMitosisClassifier) with an n_classes head."""

    def __init__(self, in_channels: int = 5, base_channels: int = 16, n_classes: int = 3) -> None:
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
        self.head = torch.nn.Linear(c, int(n_classes))

    def forward(self, value: torch.Tensor) -> torch.Tensor:
        e1 = self.enc1(value)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))
        b = self.bottleneck(self.pool3(e3))
        d3 = self.dec3(torch.cat([self.up3(b), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        return self.head(self.gap(d1).flatten(1))


def build_model(cfg: dict | None = None) -> DaughterNet:
    m = (cfg or DEFAULT_CFG)["model"]
    return DaughterNet(int(m["in_channels"]), int(m["base_channels"]), int(m["n_classes"]))


def load_daughternet(paths: Sequence[Path | str], device: str | None = None) -> dict:
    """Load one or more fold checkpoints ({'model_state', 'config'}) -> bundle usable by prepare_sample/score_nodes."""
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    models, cfg = [], None
    for p in paths:
        payload = torch.load(Path(p), map_location="cpu", weights_only=False)
        cfg = payload.get("config", DEFAULT_CFG) if isinstance(payload, dict) else DEFAULT_CFG
        model = build_model(cfg)
        model.load_state_dict(payload["model_state"] if "model_state" in payload else payload, strict=True)
        models.append(model.to(dev).eval())
    if not models:
        raise FileNotFoundError("no DaughterNet checkpoints given")
    return {"models": models, "device": dev, "torch": torch, "config": cfg, "prepared_frames": {}}


def prepare_sample(dataset: str, t: int, node: dict, bundle: dict, frame_cache: dict,
                   read_frame: Callable[[str, int, dict], np.ndarray] | None = None) -> np.ndarray:
    """(5, 16, 32, 32) float32 sample, identical to the DivNet contract (bundle['config'] carries input/normalization)."""
    return prepare_divnet_input(dataset, int(t), node, bundle, frame_cache, read_frame)


@torch.no_grad()
def score_nodes(dataset: str, nodes: Sequence[dict], bundle: dict, frame_cache: dict,
                read_frame: Callable[[str, int, dict], np.ndarray] | None = None, batch: int = 64,
                model_index: int | None = None) -> np.ndarray:
    """Softmax probabilities (N, 3) in CLASSES order; mean over fold models unless model_index selects one (OOF)."""
    if not nodes:
        return np.zeros((0, 3), dtype=np.float32)
    order = sorted(range(len(nodes)), key=lambda i: int(nodes[i]["t"]))
    out = np.zeros((len(nodes), 3), dtype=np.float32)
    models = bundle["models"] if model_index is None else [bundle["models"][model_index]]
    dev = bundle["device"]
    for s in range(0, len(order), batch):
        idx = order[s:s + batch]
        x = np.stack([prepare_sample(dataset, int(nodes[i]["t"]), nodes[i], bundle, frame_cache, read_frame) for i in idx])
        xt = torch.from_numpy(x).to(dev, dtype=torch.float32)
        p = torch.stack([torch.softmax(m(xt), dim=1) for m in models]).mean(0)
        out[idx] = p.float().cpu().numpy()
    return out
