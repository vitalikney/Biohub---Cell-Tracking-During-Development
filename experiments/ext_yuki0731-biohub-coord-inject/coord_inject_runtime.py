from __future__ import annotations

import json
import math
import shutil
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.spatial import cKDTree
from skimage.feature import peak_local_max


SCALE = np.array([1.625, 0.40625, 0.40625], dtype=np.float64)
POOL = 4
S = 64


def _torch_load(path: Path, map_location="cpu"):
    try:
        return torch.load(path, map_location=map_location, weights_only=False)
    except TypeError:
        return torch.load(path, map_location=map_location)


def _block(ci: int, co: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Conv3d(ci, co, 3, padding=1),
        nn.BatchNorm3d(co),
        nn.ReLU(inplace=True),
        nn.Conv3d(co, co, 3, padding=1),
        nn.BatchNorm3d(co),
        nn.ReLU(inplace=True),
    )


class UNet3D(nn.Module):
    def __init__(self, base: int = 24):
        super().__init__()
        self.e1 = _block(1, base)
        self.e2 = _block(base, base * 2)
        self.e3 = _block(base * 2, base * 4)
        self.pool = nn.MaxPool3d(2)
        self.bott = _block(base * 4, base * 8)
        self.u3 = nn.ConvTranspose3d(base * 8, base * 4, 2, stride=2)
        self.d3 = _block(base * 8, base * 4)
        self.u2 = nn.ConvTranspose3d(base * 4, base * 2, 2, stride=2)
        self.d2 = _block(base * 4, base * 2)
        self.u1 = nn.ConvTranspose3d(base * 2, base, 2, stride=2)
        self.d1 = _block(base * 2, base)
        self.out = nn.Conv3d(base, 1, 1)

    def forward(self, x):
        e1 = self.e1(x)
        e2 = self.e2(self.pool(e1))
        e3 = self.e3(self.pool(e2))
        b = self.bott(self.pool(e3))
        d3 = self.d3(torch.cat([self.u3(b), e3], 1))
        d2 = self.d2(torch.cat([self.u2(d3), e2], 1))
        d1 = self.d1(torch.cat([self.u1(d2), e1], 1))
        return self.out(d1)


def unet_feats(m: UNet3D, x: torch.Tensor):
    e1 = m.e1(x)
    e2 = m.e2(m.pool(e1))
    e3 = m.e3(m.pool(e2))
    b = m.bott(m.pool(e3))
    d3 = m.d3(torch.cat([m.u3(b), e3], 1))
    d2 = m.d2(torch.cat([m.u2(d3), e2], 1))
    d1 = m.d1(torch.cat([m.u1(d2), e1], 1))
    return m.out(d1), (d1, d2, d3)


def _group_norm_channels(ch: int) -> nn.GroupNorm:
    for g in (8, 4, 2, 1):
        if ch % g == 0:
            return nn.GroupNorm(g, ch)
    return nn.GroupNorm(1, ch)


class Dense2(nn.Module):
    def __init__(
        self,
        base: int = 24,
        off_scale: float = 0.5,
        off_head: str = "linear",
        off_hidden: int = 64,
        off_layers: int = 3,
        off_kernel: int = 3,
    ):
        super().__init__()
        self.unet = UNet3D(base=base)
        self.off_scale = float(off_scale)
        self.off_head = str(off_head)
        self.off_hidden = int(off_hidden)
        self.off_layers = int(off_layers)
        self.off_kernel = int(off_kernel)
        if self.off_head == "linear":
            self.off = nn.Conv3d(base, 3, 1)
            nn.init.zeros_(self.off.weight)
            nn.init.zeros_(self.off.bias)
        elif self.off_head in ("tower", "res_tower"):
            tower = self._make_tower(base)
            if self.off_head == "tower":
                self.off = tower
            else:
                base_head = nn.Conv3d(base, 3, 1)
                nn.init.zeros_(base_head.weight)
                nn.init.zeros_(base_head.bias)
                self.off = nn.ModuleDict({"base": base_head, "delta": tower})
        else:
            raise ValueError(f"unknown off_head={self.off_head!r}")

    def _make_tower(self, base: int) -> nn.Sequential:
        pad = self.off_kernel // 2
        layers = []
        cin = base
        for _ in range(self.off_layers):
            layers.append(nn.Conv3d(cin, self.off_hidden, self.off_kernel, padding=pad))
            layers.append(_group_norm_channels(self.off_hidden))
            layers.append(nn.SiLU(inplace=True))
            cin = self.off_hidden
        layers.append(nn.Conv3d(cin, 3, 1))
        nn.init.zeros_(layers[-1].weight)
        nn.init.zeros_(layers[-1].bias)
        return nn.Sequential(*layers)

    def forward(self, x):
        lg, feats = unet_feats(self.unet, x)
        f = feats[0]
        if self.off_head == "res_tower":
            base = torch.tanh(self.off["base"](f)) * 0.5
            delta = torch.tanh(self.off["delta"](f)) * self.off_scale
            return lg, torch.clamp(base + delta, -self.off_scale, self.off_scale)
        return lg, torch.tanh(self.off(f)) * self.off_scale


def _gn(ch: int) -> nn.GroupNorm:
    for g in (8, 4, 2, 1):
        if ch % g == 0:
            return nn.GroupNorm(g, ch)
    return nn.GroupNorm(1, ch)


class ResidualCropNet(nn.Module):
    def __init__(
        self,
        radius=(3, 5, 5),
        data_ch: int = 3,
        scalar_ch: int = 7,
        hidden: int = 48,
        layers: int = 4,
        mlp: int = 192,
        off_scale: float = 2.0,
    ):
        super().__init__()
        self.radius = tuple(int(x) for x in radius)
        self.data_ch = int(data_ch)
        self.scalar_ch = int(scalar_ch)
        self.hidden = int(hidden)
        self.layers = int(layers)
        self.mlp = int(mlp)
        self.off_scale = float(off_scale)
        rz, ry, rx = self.radius
        shape = (2 * rz + 1, 2 * ry + 1, 2 * rx + 1)
        zz = torch.linspace(-1, 1, shape[0]).view(1, shape[0], 1, 1).expand(1, *shape)
        yy = torch.linspace(-1, 1, shape[1]).view(1, 1, shape[1], 1).expand(1, *shape)
        xx = torch.linspace(-1, 1, shape[2]).view(1, 1, 1, shape[2]).expand(1, *shape)
        self.register_buffer("grid", torch.cat([zz, yy, xx], 0), persistent=False)
        convs = []
        cin = self.data_ch + 3
        for _ in range(self.layers):
            convs += [nn.Conv3d(cin, self.hidden, 3, padding=1), _gn(self.hidden), nn.SiLU(inplace=True)]
            cin = self.hidden
        self.trunk = nn.Sequential(*convs)
        flat = self.hidden * shape[0] * shape[1] * shape[2]
        self.head = nn.Sequential(
            nn.Linear(flat + self.scalar_ch, self.mlp),
            nn.SiLU(inplace=True),
            nn.Linear(self.mlp, self.mlp),
            nn.SiLU(inplace=True),
            nn.Linear(self.mlp, 3),
        )
        nn.init.zeros_(self.head[-1].weight)
        nn.init.zeros_(self.head[-1].bias)

    def forward(self, x, scal):
        g = self.grid.to(dtype=x.dtype).unsqueeze(0).expand(x.shape[0], -1, -1, -1, -1)
        y = self.trunk(torch.cat([x, g], 1)).flatten(1)
        return torch.tanh(self.head(torch.cat([y, scal], 1))) * self.off_scale


def _conv2d(cin: int, hidden: int, layers: int) -> nn.Sequential:
    parts = []
    for _ in range(layers):
        parts += [nn.Conv2d(cin, hidden, 3, padding=1), _gn(hidden), nn.SiLU(inplace=True)]
        cin = hidden
    return nn.Sequential(*parts)


class XYProjectionNet(nn.Module):
    def __init__(
        self,
        radius=(3, 5, 5),
        data_ch: int = 3,
        scalar_ch: int = 7,
        hidden: int = 64,
        layers: int = 4,
        mlp: int = 192,
        off_scale: float = 0.5,
    ):
        super().__init__()
        self.radius = tuple(int(x) for x in radius)
        self.data_ch = int(data_ch)
        self.scalar_ch = int(scalar_ch)
        self.hidden = int(hidden)
        self.layers = int(layers)
        self.mlp = int(mlp)
        self.off_scale = float(off_scale)
        rz, ry, rx = self.radius
        h, w = 2 * ry + 1, 2 * rx + 1
        yy = torch.linspace(-1, 1, h).view(1, h, 1).expand(1, h, w)
        xx = torch.linspace(-1, 1, w).view(1, 1, w).expand(1, h, w)
        yv = torch.arange(-ry, ry + 1, dtype=torch.float32).view(1, h, 1).expand(1, h, w)
        xv = torch.arange(-rx, rx + 1, dtype=torch.float32).view(1, 1, w).expand(1, h, w)
        self.register_buffer("grid", torch.cat([yy, xx], 0), persistent=False)
        self.register_buffer("query_vox", torch.cat([yv, xv], 0), persistent=False)
        self.trunk = _conv2d(self.data_ch * 4 + 3, self.hidden, self.layers)
        flat = self.hidden * h * w
        self.head = nn.Sequential(
            nn.Linear(flat + self.scalar_ch, self.mlp),
            nn.SiLU(inplace=True),
            nn.Linear(self.mlp, self.mlp),
            nn.SiLU(inplace=True),
            nn.Linear(self.mlp, 3),
        )
        nn.init.zeros_(self.head[-1].weight)
        nn.init.zeros_(self.head[-1].bias)

    def forward(self, x, scal):
        zc = x.shape[2] // 2
        img = torch.cat([x[:, :, zc], x.mean(2), x.amax(2), x.std(2, unbiased=False)], 1)
        g = self.grid.to(dtype=x.dtype).unsqueeze(0).expand(x.shape[0], -1, -1, -1)
        qv = self.query_vox.to(dtype=x.dtype).unsqueeze(0)
        fy = scal[:, 1].to(dtype=x.dtype).view(-1, 1, 1, 1)
        fx = scal[:, 2].to(dtype=x.dtype).view(-1, 1, 1, 1)
        marker = torch.exp(-0.5 * (((qv[:, 0:1] - fy) / 0.75) ** 2 + ((qv[:, 1:2] - fx) / 0.75) ** 2))
        feat = self.trunk(torch.cat([img, g, marker], 1)).flatten(1)
        return torch.tanh(self.head(torch.cat([feat, scal], 1))) * self.off_scale


class ZProjectionNet(nn.Module):
    def __init__(
        self,
        radius=(3, 5, 5),
        data_ch: int = 3,
        scalar_ch: int = 7,
        hidden: int = 48,
        layers: int = 4,
        mlp: int = 192,
        off_scale: float = 1.0,
    ):
        super().__init__()
        self.radius = tuple(int(x) for x in radius)
        self.data_ch = int(data_ch)
        self.scalar_ch = int(scalar_ch)
        self.hidden = int(hidden)
        self.layers = int(layers)
        self.mlp = int(mlp)
        self.off_scale = float(off_scale)
        rz, ry, rx = self.radius
        d, h, w = 2 * rz + 1, 2 * ry + 1, 2 * rx + 1
        zz_y = torch.linspace(-1, 1, d).view(1, d, 1).expand(1, d, h)
        yy = torch.linspace(-1, 1, h).view(1, 1, h).expand(1, d, h)
        zz_x = torch.linspace(-1, 1, d).view(1, d, 1).expand(1, d, w)
        xx = torch.linspace(-1, 1, w).view(1, 1, w).expand(1, d, w)
        zv_y = torch.arange(-rz, rz + 1, dtype=torch.float32).view(1, d, 1).expand(1, d, h)
        yv = torch.arange(-ry, ry + 1, dtype=torch.float32).view(1, 1, h).expand(1, d, h)
        zv_x = torch.arange(-rz, rz + 1, dtype=torch.float32).view(1, d, 1).expand(1, d, w)
        xv = torch.arange(-rx, rx + 1, dtype=torch.float32).view(1, 1, w).expand(1, d, w)
        self.register_buffer("grid_y", torch.cat([zz_y, yy], 0), persistent=False)
        self.register_buffer("grid_x", torch.cat([zz_x, xx], 0), persistent=False)
        self.register_buffer("query_y", torch.cat([zv_y, yv], 0), persistent=False)
        self.register_buffer("query_x", torch.cat([zv_x, xv], 0), persistent=False)
        cin = self.data_ch * 2 + 3
        self.y_trunk = _conv2d(cin, self.hidden, self.layers)
        self.x_trunk = _conv2d(cin, self.hidden, self.layers)
        profile = self.data_ch * 2 * d
        flat = self.hidden * d * h + self.hidden * d * w + profile
        self.head = nn.Sequential(
            nn.Linear(flat + self.scalar_ch, self.mlp),
            nn.SiLU(inplace=True),
            nn.Linear(self.mlp, self.mlp),
            nn.SiLU(inplace=True),
            nn.Linear(self.mlp, 3),
        )
        nn.init.zeros_(self.head[-1].weight)
        nn.init.zeros_(self.head[-1].bias)

    def forward(self, x, scal):
        yz = torch.cat([x.mean(4), x.amax(4)], 1)
        zx = torch.cat([x.mean(3), x.amax(3)], 1)
        gy = self.grid_y.to(dtype=x.dtype).unsqueeze(0).expand(x.shape[0], -1, -1, -1)
        gx = self.grid_x.to(dtype=x.dtype).unsqueeze(0).expand(x.shape[0], -1, -1, -1)
        qy = self.query_y.to(dtype=x.dtype).unsqueeze(0)
        qx = self.query_x.to(dtype=x.dtype).unsqueeze(0)
        fz = scal[:, 0].to(dtype=x.dtype).view(-1, 1, 1, 1)
        fy0 = scal[:, 1].to(dtype=x.dtype).view(-1, 1, 1, 1)
        fx0 = scal[:, 2].to(dtype=x.dtype).view(-1, 1, 1, 1)
        marker_y = torch.exp(-0.5 * (((qy[:, 0:1] - fz) / 0.75) ** 2 + ((qy[:, 1:2] - fy0) / 0.75) ** 2))
        marker_x = torch.exp(-0.5 * (((qx[:, 0:1] - fz) / 0.75) ** 2 + ((qx[:, 1:2] - fx0) / 0.75) ** 2))
        fy = self.y_trunk(torch.cat([yz, gy, marker_y], 1)).flatten(1)
        fx = self.x_trunk(torch.cat([zx, gx, marker_x], 1)).flatten(1)
        prof = torch.cat([x.mean((3, 4)), x.amax((3, 4))], 1).flatten(1)
        return torch.tanh(self.head(torch.cat([fy, fx, prof, scal], 1))) * self.off_scale


def raw_to_pooled(p):
    r = np.asarray(p, np.float64).copy().reshape(-1, 3)
    r[:, 1] = (r[:, 1] - (POOL - 1) / 2) / POOL
    r[:, 2] = (r[:, 2] - (POOL - 1) / 2) / POOL
    return r


def pooled_to_raw(p):
    r = np.asarray(p, np.float64).copy().reshape(-1, 3)
    r[:, 1] = r[:, 1] * POOL + (POOL - 1) / 2
    r[:, 2] = r[:, 2] * POOL + (POOL - 1) / 2
    return r


def view_vol(x, i: int):
    if i & 1:
        x = np.flip(x, -2)
    if i & 2:
        x = np.flip(x, -1)
    return x


def view8(x, i: int):
    if i & 4:
        x = np.flip(x, -3)
    return view_vol(x, i & 3)


def read_array_meta(zp: Path) -> dict:
    with open(Path(zp) / "0" / "zarr.json") as f:
        m = json.load(f)
    return {"shape": tuple(m["shape"]), "dtype": np.dtype(m["data_type"])}


_ZC = {}


def load_volume(zp: Path, t: int, meta: dict | None = None):
    try:
        import zarr

        k = str(zp)
        if k not in _ZC:
            _ZC[k] = zarr.open(k, mode="r")["0"]
        return np.asarray(_ZC[k][t])
    except Exception:
        import blosc2

        if meta is None:
            meta = read_array_meta(zp)
        chunk = Path(zp) / "0" / "c" / str(t) / "0" / "0" / "0"
        buf = blosc2.decompress(chunk.read_bytes())
        return np.frombuffer(buf, dtype=meta["dtype"]).reshape(meta["shape"][1:])


def avail_T(zp: Path) -> int:
    meta = read_array_meta(zp)
    present = [t for t in range(meta["shape"][0]) if (Path(zp) / "0" / "c" / str(t) / "0" / "0" / "0").exists()]
    return max(present) + 1 if present else int(meta["shape"][0])


def pool_xy(vol, f: int = POOL):
    z, y, x = vol.shape
    y2, x2 = (y // f) * f, (x // f) * f
    v = vol[:, :y2, :x2].astype(np.float32, copy=False)
    return v.reshape(z, y2 // f, f, x2 // f, f).mean(axis=(2, 4))


def pool_norm(vol, preproc: str = ""):
    p = pool_xy(vol)
    if preproc == "tophat":
        from scipy.ndimage import grey_opening

        p = np.clip(p - grey_opening(p, size=(1, 7, 7)), 0.0, None)
    lo = float(np.percentile(p, 50))
    hi = float(np.percentile(p, 99.5))
    return np.clip((p - lo) / (hi - lo + 1e-6), -0.5, 6.0).astype(np.float32)


def extract_patches(row, t: int, centres_pooled, radius, ctx: int, use_heatmap: bool = False):
    rz, ry, rx = radius
    shape = (2 * rz + 1, 2 * ry + 1, 2 * rx + 1)
    chans = []
    T = row["T"]
    for d in range(-ctx, ctx + 1):
        tt = min(max(t + d, 0), T - 1)
        chans.append(row["vol"][tt].astype(np.float32))
    if use_heatmap:
        for d in range(-ctx, ctx + 1):
            tt = min(max(t + d, 0), T - 1)
            chans.append(row["hm"][tt].astype(np.float32))
    pad = ((rz, rz), (ry, ry), (rx, rx))
    chans = [np.pad(v, pad) for v in chans]
    q = np.rint(centres_pooled).astype(np.int64)
    q[:, 0] = np.clip(q[:, 0], 0, row["vol"].shape[1] - 1)
    q[:, 1] = np.clip(q[:, 1], 0, row["vol"].shape[2] - 1)
    q[:, 2] = np.clip(q[:, 2], 0, row["vol"].shape[3] - 1)
    out = np.empty((len(q), len(chans), *shape), np.float32)
    for n, p in enumerate(q):
        z, y, x = int(p[0]) + rz, int(p[1]) + ry, int(p[2]) + rx
        for c, v in enumerate(chans):
            out[n, c] = v[z - rz : z + rz + 1, y - ry : y + ry + 1, x - rx : x + rx + 1]
    return out


def scalars(P, score):
    q = np.rint(P).astype(np.float32)
    frac = P.astype(np.float32) - q
    pos = P.astype(np.float32) / np.array([63.0, 63.0, 63.0], np.float32)[None]
    return np.concatenate([frac, pos, score.reshape(-1, 1).astype(np.float32)], 1)


@torch.no_grad()
def predict_delta(model, patches, scal, batch: int, amp: bool, device):
    outs = []
    model.eval()
    for i in range(0, len(patches), batch):
        xb = torch.from_numpy(np.ascontiguousarray(patches[i : i + batch])).to(device)
        sb = torch.from_numpy(np.ascontiguousarray(scal[i : i + batch])).to(device)
        with torch.amp.autocast("cuda", dtype=torch.bfloat16, enabled=amp and device.type == "cuda"):
            y = model(xb, sb)
        outs.append(y.float().cpu().numpy())
    return np.concatenate(outs) if outs else np.zeros((0, 3), np.float32)


def _flip_array(a, view: int):
    if view & 1:
        a = np.flip(a, -3)
    if view & 2:
        a = np.flip(a, -2)
    if view & 4:
        a = np.flip(a, -1)
    return a


def _flip_pts(p, view: int, shape):
    q = np.asarray(p, np.float32).copy().reshape(-1, 3)
    lim = np.asarray(shape, np.float32) - 1.0
    if view & 1:
        q[:, 0] = lim[0] - q[:, 0]
    if view & 2:
        q[:, 1] = lim[1] - q[:, 1]
    if view & 4:
        q[:, 2] = lim[2] - q[:, 2]
    return q


def _rotxy_array(a, rot: int):
    rot = int(rot) % 4
    return np.rot90(a, rot, axes=(-2, -1)) if rot else a


def _rotxy_pts(p, rot: int, shape):
    rot = int(rot) % 4
    q = np.asarray(p, np.float32).copy().reshape(-1, 3)
    if rot == 0:
        return q
    y = q[:, 1].copy()
    x = q[:, 2].copy()
    y_lim = float(shape[1] - 1)
    x_lim = float(shape[2] - 1)
    if rot == 1:
        q[:, 1] = x_lim - x
        q[:, 2] = y
    elif rot == 2:
        q[:, 1] = y_lim - y
        q[:, 2] = x_lim - x
    elif rot == 3:
        q[:, 1] = x
        q[:, 2] = y_lim - y
    return q


def _transform_array(a, view: int, rot: int):
    return _rotxy_array(_flip_array(a, view), rot)


def _transform_pts(p, view: int, rot: int, shape):
    return _rotxy_pts(_flip_pts(p, view, shape), rot, shape)


def _inverse_pts(p, view: int, rot: int, shape):
    q = _rotxy_pts(p, (-int(rot)) % 4, shape)
    return _flip_pts(q, view, shape)


def _view_row(row, view: int, rot: int):
    if view == 0 and int(rot) % 4 == 0:
        return row
    out = dict(row)
    out["vol"] = _transform_array(row["vol"], view, rot)
    if "hm" in row:
        out["hm"] = _transform_array(row["hm"], view, rot)
    return out


def _predict_one(spec, row, t: int, pooled, scores, batch: int, amp: bool, device):
    if not len(pooled):
        return np.zeros((0, 3), np.float32)
    patches = extract_patches(row, t, pooled.astype(np.float32), spec["radius"], spec["ctx"], spec.get("use_heatmap", False))
    return predict_delta(spec["model"], patches, scalars(pooled, scores), batch, amp, device)


def _predict_points(spec, row, t: int, pooled, scores, batch: int, amp: bool, device, views, rots):
    if not len(pooled):
        return np.zeros((0, 3), np.float32)
    shape = row["vol"].shape[1:]
    preds = []
    for view in views:
        for rot in rots:
            rv = _view_row(row, int(view), int(rot))
            pv = _transform_pts(pooled, int(view), int(rot), shape)
            dv = _predict_one(spec, rv, t, pv, scores, batch, amp, device)
            preds.append(_inverse_pts(pv + dv, int(view), int(rot), shape))
    return np.mean(np.stack(preds, 0), axis=0).astype(np.float32)


def load_detector(path: Path, device):
    ck = _torch_load(path, map_location="cpu")
    cfg = ck.get("cfg", {})
    m = Dense2(
        base=int(ck.get("base", 24)),
        off_scale=float(ck.get("off_scale", cfg.get("off_scale", 0.5))),
        off_head=ck.get("off_head", cfg.get("off_head", "linear")),
        off_hidden=int(ck.get("off_hidden", cfg.get("off_hidden", 64))),
        off_layers=int(ck.get("off_layers", cfg.get("off_layers", 3))),
        off_kernel=int(ck.get("off_kernel", cfg.get("off_kernel", 3))),
    ).to(device)
    m.load_state_dict(ck["state_dict"])
    m.eval()
    return m


def load_refiner(path: Path, device):
    ck = _torch_load(path, map_location="cpu")
    cfg = ck.get("cfg", {})
    radius = ck.get("radius", cfg.get("radius", (3, 5, 5)))
    if isinstance(radius, str):
        radius = tuple(int(x) for x in radius.split(","))
    else:
        radius = tuple(int(x) for x in radius)
    ctx = int(cfg.get("ctx", 1))
    use_heatmap = bool(cfg.get("heatmap_tag", ""))
    data_ch = int(cfg.get("data_ch", (2 * ctx + 1) * (2 if use_heatmap else 1)))
    proj = ck.get("proj_mode", cfg.get("proj", ""))
    if proj == "xy":
        net = XYProjectionNet(
            radius=radius,
            data_ch=data_ch,
            hidden=int(cfg.get("hidden", 64)),
            layers=int(cfg.get("layers", 4)),
            mlp=int(cfg.get("mlp", 192)),
            off_scale=float(cfg.get("off_scale", 0.5)),
        ).to(device)
    elif proj == "z":
        net = ZProjectionNet(
            radius=radius,
            data_ch=data_ch,
            hidden=int(cfg.get("hidden", 48)),
            layers=int(cfg.get("layers", 4)),
            mlp=int(cfg.get("mlp", 192)),
            off_scale=float(cfg.get("off_scale", 1.0)),
        ).to(device)
    else:
        net = ResidualCropNet(
            radius=radius,
            data_ch=data_ch,
            hidden=int(cfg.get("hidden", 48)),
            layers=int(cfg.get("layers", 4)),
            mlp=int(cfg.get("mlp", 192)),
            off_scale=float(cfg.get("off_scale", 2.0)),
        ).to(device)
    net.load_state_dict(ck["state_dict"])
    net.eval()
    return {"model": net, "radius": radius, "ctx": ctx, "proj": proj, "use_heatmap": use_heatmap}


def build_volumes(zarr_path: Path):
    meta = read_array_meta(zarr_path)
    T = avail_T(zarr_path)
    vols = []
    for t in range(T):
        vols.append(pool_norm(load_volume(zarr_path, t, meta), "").astype(np.float16))
    return np.stack(vols), T


@torch.no_grad()
def detector_cache_for_video(stem: str, zarr_path: Path, models, device, floor: float = 0.02, max_per_frame: int = 4000):
    vols, T = build_volumes(zarr_path)
    views = [0, 1, 2, 3]
    pooled_frames = []
    score_frames = []
    offsets = [0]
    for t in range(T):
        accl = 0.0
        acco = 0.0
        ns = 0
        no = 0
        x = vols[t].astype(np.float32)
        for m in models:
            for i in views:
                xv = view8(x, i)
                xt = torch.from_numpy(np.ascontiguousarray(xv))[None, None].to(device)
                lg, offd = m(xt)
                accl = accl + view8(lg[0, 0].float().cpu().numpy(), i)
                o = view8(offd[0].float().cpu().numpy(), i).copy()
                if i & 1:
                    o[1] = -o[1]
                if i & 2:
                    o[2] = -o[2]
                if i & 4:
                    o[0] = -o[0]
                acco = acco + o
                ns += 1
                no += 1
        h = 1.0 / (1.0 + np.exp(-(accl / ns)))
        om = acco / no
        pk = peak_local_max(h, min_distance=1, threshold_abs=floor, exclude_border=False)
        if len(pk):
            d = om[:, pk[:, 0], pk[:, 1], pk[:, 2]].T
            P = pk.astype(np.float64) + d
            sc = h[pk[:, 0], pk[:, 1], pk[:, 2]].astype(np.float64)
        else:
            P, sc = np.zeros((0, 3), np.float64), np.zeros(0, np.float64)
        if len(P) > max_per_frame:
            k = np.argsort(-sc)[:max_per_frame]
            P, sc = P[k], sc[k]
        pooled_frames.append(P.astype(np.float32))
        score_frames.append(sc.astype(np.float32))
        offsets.append(offsets[-1] + len(P))
    pooled = np.concatenate(pooled_frames) if pooled_frames else np.zeros((0, 3), np.float32)
    scores = np.concatenate(score_frames) if score_frames else np.zeros(0, np.float32)
    return {"stem": stem, "vol": vols, "T": T, "pooled": pooled, "scores": scores, "offsets": np.array(offsets, np.int64)}


@torch.no_grad()
def apply_axis_refiners(cache, z_spec, xy_spec, device, batch: int = 1024, amp: bool = True):
    pooled = cache["pooled"].astype(np.float32)
    scores = cache["scores"].astype(np.float32)
    offsets = cache["offsets"].astype(np.int64)
    row = {"vol": cache["vol"], "T": int(cache["T"])}
    out = pooled.copy()
    dz_abs = []
    dxy_abs = []
    for t in range(int(cache["T"])):
        lo, hi = int(offsets[t]), int(offsets[t + 1])
        if hi <= lo:
            continue
        P = pooled[lo:hi]
        sc = scores[lo:hi]
        if z_spec is not None:
            zp = _predict_points(z_spec, row, t, P, sc, batch, amp, device, views=[0, 3], rots=[0])
            out[lo:hi, 0] = zp[:, 0]
            dz_abs.append(np.abs(zp[:, 0] - P[:, 0]))
        if xy_spec is not None:
            xyp = _predict_points(xy_spec, row, t, P, sc, batch, amp, device, views=[0], rots=[0, 2])
            out[lo:hi, 1:3] = xyp[:, 1:3]
            dxy_abs.append(np.linalg.norm(xyp[:, 1:3] - P[:, 1:3], axis=1))
    raw_ref = pooled_to_raw(out).astype(np.float32)
    return {
        "pooled": out.astype(np.float32),
        "raw_ref": raw_ref,
        "scores": scores.astype(np.float32),
        "offsets": offsets,
        "T": np.int64(cache["T"]),
        "median_abs_dz": float(np.median(np.concatenate(dz_abs))) if dz_abs else 0.0,
        "median_abs_dxy": float(np.median(np.concatenate(dxy_abs))) if dxy_abs else 0.0,
    }


def _load_graph(path: Path):
    import tracksdata as td

    graph = td.graph.IndexedRXGraph.from_geff(path)
    return graph[0] if isinstance(graph, tuple) else graph


def inject_one(geff_path: Path, out_dir: Path, refined: dict, max_um: float = 3.0, alpha: float = 1.0, score_min: float = -math.inf):
    import tracksdata as td

    graph = _load_graph(geff_path)
    node_key = td.DEFAULT_ATTR_KEYS.NODE_ID
    attrs = graph.node_attrs().select([node_key, "t", "z", "y", "x"])
    rows = attrs.to_dicts()
    node_ids = [int(r[node_key]) for r in rows]
    old = np.array([[float(r["z"]), float(r["y"]), float(r["x"])] for r in rows], dtype=np.float64)
    times = np.array([int(r["t"]) for r in rows], dtype=np.int64)
    new = old.copy()

    coords = refined["raw_ref"].astype(np.float64)
    scores = refined["scores"].astype(np.float64)
    offsets = refined["offsets"].astype(np.int64)
    trees = {}
    for t in np.unique(times):
        if t < 0 or t + 1 >= len(offsets):
            continue
        lo, hi = int(offsets[t]), int(offsets[t + 1])
        cand = coords[lo:hi]
        sc = scores[lo:hi]
        if score_min > -math.inf:
            cand = cand[sc >= score_min]
        if len(cand):
            trees[int(t)] = (cKDTree(cand * SCALE), cand)

    replaced = 0
    nn_dists = []
    shifts = []
    for i, (t, p) in enumerate(zip(times, old)):
        item = trees.get(int(t))
        if item is None:
            continue
        tree, cand = item
        dist, idx = tree.query(p * SCALE, k=1)
        dist = float(dist)
        nn_dists.append(dist)
        if dist <= max_um:
            target = cand[int(idx)]
            mixed = (1.0 - alpha) * p + alpha * target
            new[i] = mixed
            replaced += 1
            shifts.append(float(np.linalg.norm((mixed - p) * SCALE)))

    graph.update_node_attrs(
        attrs={"z": new[:, 0].tolist(), "y": new[:, 1].tolist(), "x": new[:, 2].tolist()},
        node_ids=node_ids,
    )
    out_path = out_dir / geff_path.name
    if out_path.exists():
        if out_path.is_dir():
            shutil.rmtree(out_path)
        else:
            out_path.unlink()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    graph.to_geff(out_path)
    return {
        "stem": geff_path.stem,
        "nodes": len(rows),
        "replaced": replaced,
        "replace_frac": replaced / max(len(rows), 1),
        "median_nn_um": float(np.median(nn_dists)) if nn_dists else float("nan"),
        "p95_nn_um": float(np.percentile(nn_dists, 95)) if nn_dists else float("nan"),
        "median_shift_um": float(np.median(shifts)) if shifts else 0.0,
        "p95_shift_um": float(np.percentile(shifts, 95)) if shifts else 0.0,
    }


def _prediction_dir(repo_dir: Path, method: str) -> Path:
    matches = sorted((repo_dir / "predictions").glob(f"*/{method}/split_0"))
    if len(matches) != 1:
        raise RuntimeError(f"expected one prediction dir for {method}, found {matches}")
    return matches[0]


def run_coord_injection(
    test_dir: Path,
    repo_dir: Path,
    method: str,
    test_stems: list[str],
    weights_dir: Path,
    working_dir: Path,
    max_um: float = 3.0,
    alpha: float = 1.0,
) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    det_names = [
        "D_mix_offpeak_mix_s0_ep0.pt",
        "M_seed1_offpeak_mix_s1_ep0.pt",
        "M_seed2_offpeak_mix_s2_ep0.pt",
        "M_seed3_offpeak_mix_s3_ep0.pt",
    ]
    print(f"[coord-inject] loading {len(det_names)} detector checkpoints on {device}", flush=True)
    models = [load_detector(weights_dir / name, device) for name in det_names]
    z_spec = load_refiner(weights_dir / "R_ens4off_tr171_z_s0_ep6.pt", device)
    xy_spec = load_refiner(weights_dir / "RprojQ_ens4off_tr171_xy_s0_ep1.pt", device)

    pred_dir = _prediction_dir(repo_dir, method)
    out_dir = pred_dir.parent / "split_0_coordinject"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = working_dir / "coord_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    t0_all = time.time()
    for index, stem in enumerate(test_stems, 1):
        t0 = time.time()
        zarr_path = test_dir / f"{stem}.zarr"
        geff_path = pred_dir / f"{stem}.geff"
        if not geff_path.exists():
            raise FileNotFoundError(geff_path)
        cache = detector_cache_for_video(stem, zarr_path, models, device)
        refined = apply_axis_refiners(cache, z_spec, xy_spec, device)
        np.savez(
            cache_dir / f"rz3d6ztta_zy_xyq1r180_{stem}.npz",
            pooled=refined["pooled"],
            raw_ref=refined["raw_ref"],
            scores=refined["scores"],
            offsets=refined["offsets"],
            T=refined["T"],
        )
        row = inject_one(geff_path, out_dir, refined, max_um=max_um, alpha=alpha)
        row.update(
            detections=int(len(refined["scores"])),
            median_abs_dz=refined["median_abs_dz"],
            median_abs_dxy=refined["median_abs_dxy"],
            seconds=float(time.time() - t0),
        )
        rows.append(row)
        print(
            f"[coord-inject] [{index}/{len(test_stems)}] {stem}: "
            f"dets={row['detections']} replaced={row['replaced']}/{row['nodes']} "
            f"shift_med={row['median_shift_um']:.3f}um "
            f"dz={row['median_abs_dz']:.3f} dxy={row['median_abs_dxy']:.3f} "
            f"{row['seconds']:.1f}s",
            flush=True,
        )

    backup_dir = pred_dir.parent / "split_0_public_original"
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    pred_dir.rename(backup_dir)
    out_dir.rename(pred_dir)

    total_nodes = sum(int(r["nodes"]) for r in rows)
    total_replaced = sum(int(r["replaced"]) for r in rows)
    summary = {
        "mode": "rock0926_plus_coord_injection",
        "detectors": det_names,
        "z_refiner": "R_ens4off_tr171_z_s0_ep6.pt",
        "xy_refiner": "RprojQ_ens4off_tr171_xy_s0_ep1.pt",
        "source_pred_dir_backup": str(backup_dir),
        "active_pred_dir": str(pred_dir),
        "max_um": max_um,
        "alpha": alpha,
        "videos": len(rows),
        "nodes": total_nodes,
        "replaced": total_replaced,
        "replace_frac": total_replaced / max(total_nodes, 1),
        "median_video_shift_um": float(np.median([r["median_shift_um"] for r in rows])) if rows else 0.0,
        "seconds": float(time.time() - t0_all),
        "per_video": rows,
    }
    out_json = working_dir / "coord_injection_summary.json"
    out_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("[coord-inject] wrote", out_json, flush=True)
    print(json.dumps({k: summary[k] for k in ["videos", "nodes", "replaced", "replace_frac", "seconds"]}, indent=2), flush=True)
    return summary
