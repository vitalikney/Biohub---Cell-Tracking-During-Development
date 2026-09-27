"""FAKE train_unet_transformer for the exp77 CPU smoke test. It is never uploaded to Kaggle.

It mirrors the module surface that exp71/exp77 touch in the pinned, patched trainer:
  - the globals WEIGHTS_PATH, _cycle, tqdm, DataLoader, UNetNodeTransformer, compute_detection_loss, train_epoch and
    _POS_EMBED_DIM, all looked up at call time the same way;
  - train(..., validate=False) with the same control flow (output_dir, config.json, _load, a seeded DataLoader,
    train_epoch via the module global, save, reload);
  - encode() returns (features (B, W, C, *sp), [W x (B, 1, *sp)]);
  - load_dataset_windows / FrameWindowDataset / detect_and_match / TemporalUNet3D.
The data is tiny synthetic 8^3 volumes. Failure injection (env):
  FAKE_ITER_SLEEP=<s>        sleep per training iteration
  FAKE_FAIL_WORKERS_IN=<lbl> a DataLoader failure when num_workers > 0 and WEIGHTS_PATH contains <lbl>
  FAKE_HANG_IN=<lbl>         hang in _load of the REAL run (not the probe) when WEIGHTS_PATH contains <lbl>
  FAKE_CRASH_PROXY_IN=<lbl>  load_dataset_windows raises when called outside train() (the proxy) for <lbl>
"""
import json
import os
import time
from itertools import cycle as _cycle
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

WEIGHTS_PATH = Path("/nonexistent/weights")
_POS_EMBED_DIM = 8
SPATIAL = (8, 8, 8)
N_NODES = 3
_IN_TRAIN = {"flag": False}


def _conv_block(cin, cout):
    return nn.Sequential(nn.Conv3d(cin, cout, 1), nn.BatchNorm3d(cout), nn.ReLU(), nn.Conv3d(cout, cout, 1),
                         nn.BatchNorm3d(cout), nn.ReLU())


class TemporalUNet3D(nn.Module):
    def __init__(self, in_channels=1, out_channels=4, layers=None):
        super().__init__()
        layers = layers or [4, 8]
        self.encoder_blocks = nn.ModuleList([_conv_block(in_channels, layers[0])])
        self.decoder_blocks = nn.ModuleList([_conv_block(layers[0], layers[0]) for _ in range(len(layers))])
        self.head = nn.Conv3d(layers[0], out_channels, 1)

    def forward(self, x):  # (B, W, 1, *sp)
        B, W = x.shape[:2]
        h = self.encoder_blocks[0](x.flatten(0, 1))
        for block in self.decoder_blocks:
            h = block(h)
        return self.head(h).unflatten(0, (B, W))


class UNetNodeTransformer(nn.Module):
    def __init__(self, unet, unet_out_channels, pos_feat_dim, hidden_dim=8, **_):
        super().__init__()
        self.unet = unet
        self.unet_out_channels = unet_out_channels
        self.detect_head = nn.Conv3d(unet_out_channels, 1, kernel_size=1)
        self.transformer = nn.Linear(unet_out_channels + pos_feat_dim, hidden_dim)

    def encode(self, imgs):
        window = imgs.unsqueeze(2)
        unet_out = self.unet(window)
        W = unet_out.shape[1]
        det_logits = [self.detect_head(unet_out[:, i]) for i in range(W)]
        return unet_out, det_logits


def compute_detection_loss(det_logits, coords, mask, neg_weight=0.1):
    return F.binary_cross_entropy_with_logits(det_logits, torch.zeros_like(det_logits))


def detect_and_match(det_logits, gt_coords, mask, image_shape, det_threshold=0.3, pool_kernel_um=5.0,
                     max_match_distance=5.0, voxel_size=None, frame_index=0, window_size=None):
    B = det_logits.shape[0]
    flat = det_logits.reshape(B, -1)
    det_mask = flat > det_threshold
    matches = [torch.where(torch.arange(int(det_mask[b].sum())) < int(mask[b].sum()), 0, -1) for b in range(B)]
    coords = torch.zeros(B, flat.shape[1], 3)
    pos = torch.zeros(B, flat.shape[1], 4 * _POS_EMBED_DIM)
    return coords, pos, det_mask, matches


class VideoMeta(dict):
    pass


def load_dataset_windows(ds_path, window_size=2, invert_time=False, max_frames=None, downsample=(1, 1, 1)):
    label = os.environ.get("FAKE_CRASH_PROXY_IN")
    if label and not _IN_TRAIN["flag"] and label in str(WEIGHTS_PATH):
        raise OSError("injected proxy failure")
    seed = sum(map(ord, Path(ds_path).name))
    windows = [{"t_start": t, "seed": seed * 100 + t} for t in range(6)]
    return VideoMeta(name=Path(ds_path).name, image_shape=(8, *SPATIAL)), windows


class FrameWindowDataset(Dataset):
    def __init__(self, video_data, max_nodes=None, augmentations=None):
        self._data = [(w, vm) for vm, ws in video_data for w in ws]

    def __len__(self):
        return len(self._data)

    def __getitem__(self, idx):
        w, vm = self._data[idx]
        g = torch.Generator().manual_seed(w["seed"])
        return {
            "t_start": w["t_start"],
            "n_frames": 2,
            "imgs": torch.rand(2, *SPATIAL, generator=g).half(),
            "coords": torch.randint(0, 8, (2, N_NODES, 3), generator=g).float(),
            "pos_feats": torch.zeros(2, N_NODES, 4 * _POS_EMBED_DIM),
            "masks": torch.ones(2, N_NODES, dtype=torch.bool),
            "targets": torch.zeros(1, N_NODES, N_NODES),
            "image_shape": torch.tensor(vm["image_shape"], dtype=torch.long),
            "voxel_size": torch.tensor([1.0, 1.0, 1.0]),
            "downsample": torch.tensor([1.0, 1.0, 1.0]),
        }


def train_epoch(model, loader, optimizer, device, det_loss_weight=0.1, det_neg_weight=0.1, max_iters=None,
                pool_kernel_um=5.0):
    model.train()
    total_edge, total_det, n = 0.0, 0.0, 0
    if max_iters is not None:
        batch_iter = _cycle(loader)
        pbar = tqdm(range(max_iters), desc="  iters", leave=False, disable=False)
    else:
        batch_iter = iter(loader)
        pbar = tqdm(range(len(loader)), desc="  batches", leave=False, disable=False)
    label = os.environ.get("FAKE_FAIL_WORKERS_IN")
    for _ in pbar:
        if label and label in str(WEIGHTS_PATH) and getattr(loader, "num_workers", 0) > 0:
            raise RuntimeError("DataLoader worker (pid 4242) exited unexpectedly (injected)")
        batch = next(batch_iter)
        imgs = batch["imgs"].to(device, dtype=torch.float32)
        coords = batch["coords"].to(device)
        masks = batch["masks"].to(device)
        B, W = imgs.shape[:2]
        unet_out, det_logits = model.encode(imgs)
        det_loss = sum(compute_detection_loss(det_logits[i], coords[:, i], masks[:, i], det_neg_weight)
                       for i in range(W)) / W
        feats = unet_out[:, 0].mean(dim=(2, 3, 4))
        edge_loss = model.transformer(torch.cat([feats, torch.zeros(B, 4 * _POS_EMBED_DIM, device=device)], -1)).square().mean() * 1e-3
        loss = edge_loss + det_loss_weight * det_loss
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_edge += edge_loss.item() * B
        total_det += det_loss.item() * B
        n += B
        time.sleep(float(os.environ.get("FAKE_ITER_SLEEP", "0")))
    return total_edge / max(n, 1), total_det / max(n, 1)


def _worker_init_fn(worker_id):
    np.random.seed(torch.initial_seed() % 2**32)


def train(data_dir, fold, splits_file, method="unet_transformer", n_epochs=50, lr=1e-3, batch_size=16, num_workers=4,
          unet_out_channels=32, unet_layers=None, unet_weights=None, downsample=(1, 4, 4), det_loss_weight=1e1,
          det_neg_weight=1e-2, max_iters=None, debug_video=None, seed=None, max_frames=None, window_size=2,
          augmentations=None, pool_kernel_um=5.0, data_parallel=True, validate=True):
    folds = json.loads(Path(splits_file).read_text())
    train_files = [Path(data_dir) / name for name in folds[fold]["train"]]
    output_dir = WEIGHTS_PATH / method / f"split_{fold}"
    output_dir.mkdir(parents=True, exist_ok=True)
    model_config = {"unet_out_channels": unet_out_channels, "unet_layers": unet_layers, "downsample": list(downsample),
                    "window_size": window_size, "pool_kernel_um": pool_kernel_um}
    (output_dir / "config.json").write_text(json.dumps(model_config, indent=2))
    hang = os.environ.get("FAKE_HANG_IN")
    if hang and hang in str(WEIGHTS_PATH) and "probe" not in str(WEIGHTS_PATH):
        print("FAKE: hanging in _load", flush=True)
        time.sleep(10**6)
    _IN_TRAIN["flag"] = True
    try:
        data = [load_dataset_windows(f, window_size=window_size, downsample=downsample) for f in train_files]
    finally:
        _IN_TRAIN["flag"] = False
    print(f"  train done: {sum(len(w) for _, w in data)} windows total", flush=True)
    train_ds = FrameWindowDataset(data)
    g = None
    if seed is not None:
        g = torch.Generator()
        g.manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers,
                              prefetch_factor=2 if num_workers > 0 else None, persistent_workers=num_workers > 0,
                              pin_memory=False, generator=g, worker_init_fn=_worker_init_fn)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = UNetNodeTransformer(unet=TemporalUNet3D(in_channels=1, out_channels=unet_out_channels, layers=unet_layers),
                                unet_out_channels=unet_out_channels, pos_feat_dim=4 * _POS_EMBED_DIM).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    save_path = output_dir / "edge_predictor_best.pth"
    for _epoch in range(n_epochs):
        train_epoch(model, train_loader, optimizer, device, det_loss_weight, det_neg_weight, max_iters=max_iters,
                    pool_kernel_um=pool_kernel_um)
        torch.save({k.replace("unet.module.", "unet.", 1): v for k, v in model.state_dict().items()}, save_path)
    model.load_state_dict(torch.load(save_path, map_location=device, weights_only=True))
    return model
