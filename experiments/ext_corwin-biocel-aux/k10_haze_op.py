#!/usr/bin/env python3
"""ENG/HAZE -- THE OPERATOR: conditional haze flattening.

THE PHYSICS. Light-sheet imaging through tissue adds a smooth SCATTERED background that rises
with depth; the nucleus signal sits on TOP of it. The vendor's normalisation is ONE AFFINE MAP
PER FILM -- `(x - q_low) / (q_high - q_low)` with `q_low`, `q_high` read from the zarr's
`image_statistics` attributes -- so it cannot remove a term that varies INSIDE the film. The
deep nuclei therefore reach the detector with a low peak-over-background contrast and fall under
its bar.

THE OPERATION, and why it is a SUBTRACTION and not a gain or a re-quantisation.
  * ENG/DEPTH: the per-film depth slopes of log(contrast) have OPPOSITE SIGNS on 4 films vs 2 --
    a depth-dependent GAIN is refuted, it would have to change sign per film.
  * ENG/KER10 v17 / v18: a per-frame change of OFFSET and SCALE (quantile re-normalisation)
    made the drifting film's GT recall FALL 0,5686 -> 0,5098. An affine map of whole frames is
    the wrong operation.
  * What is left, and what the physics actually says, is an ADDITIVE, LOW-FREQUENCY,
    SPATIALLY VARYING term. You remove such a term by estimating it and subtracting it --
    clipped at zero so that where it is absent NOTHING changes.

    B    = gauss3d(minpool3d(raw, KMIN), SZ, SYX)     the local background
    E    = clamp(B - floor_film, min=0)               its EXCESS over the film's baseline
    raw' = clamp(raw - E, min=0)                      the flattened frame

THE MIN-POOL IS LOAD-BEARING. A plain Gaussian of a DENSE field estimates
`background + mean nucleus signal`, so it tracks nucleus DENSITY and the operator would suppress
the densest films -- the exact class that carries 1 970 of the champion's 2 199 missed nodes. A
grey erosion at just over one nucleus diameter takes the local minimum, which in a dense field is
still the space BETWEEN nuclei. `--no-minpool` is the declared control arm that shows it.

THE PADDING IS REFLECT on all three axes: a zero-padded blur darkens the first and last planes
and the operator would then invent an excess exactly where the stack ends.
EVERYTHING IS float32 AND CLAMPED AT ZERO: no integer overflow, no negative value reaches the
vendor's normalisation.
"""
from __future__ import annotations

import math

import torch
import torch.nn.functional as F

# ---- the parameters, frozen in STATE.md before any recall was read -----------------------
KMIN = 5          # decimated px (8,1 um) -- grey erosion, just over one nucleus diameter
SZ = 3.0          # decimated px (4,9 um) -- the haze changes plane to plane
SYX = 13.0        # decimated px (21,1 um) -- ~3 nucleus diameters
FLOOR_Q = 0.05    # the film's baseline background = p05 of B
FSTRIDE = 10      # frames used to estimate the film floor
VSTRIDE = 2       # y/x stride inside those frames


def _gauss_kernel(sigma: float, device, dtype) -> torch.Tensor:
    """A truncated Gaussian, radius 3 sigma, normalised to sum 1."""
    r = max(1, int(math.ceil(3.0 * sigma)))
    x = torch.arange(-r, r + 1, device=device, dtype=dtype)
    k = torch.exp(-0.5 * (x / sigma) ** 2)
    return k / k.sum()


def gauss3d(v: torch.Tensor, sz: float = SZ, syx: float = SYX) -> torch.Tensor:
    """Separable 3-D Gaussian on (N, 1, Z, Y, X), REFLECT padding on every axis."""
    kz = _gauss_kernel(sz, v.device, v.dtype)
    kyx = _gauss_kernel(syx, v.device, v.dtype)
    for ax, k in ((2, kz), (3, kyx), (4, kyx)):
        r = (k.numel() - 1) // 2
        shape = [1, 1, 1, 1, 1]
        shape[ax] = k.numel()
        pad = [0, 0, 0, 0, 0, 0]           # (x0, x1, y0, y1, z0, z1) for F.pad on 5-D
        pad[(4 - ax) * 2] = r
        pad[(4 - ax) * 2 + 1] = r
        # reflect padding needs the pad to be strictly smaller than the axis length
        n = v.shape[ax]
        if r >= n:
            r2 = max(0, n - 1)
            if r2 == 0:
                continue
            k = k[r - r2: r + r2 + 1]
            k = k / k.sum()
            shape[ax] = k.numel()
            pad[(4 - ax) * 2] = r2
            pad[(4 - ax) * 2 + 1] = r2
        v = F.pad(v, pad, mode="reflect")
        v = F.conv3d(v, k.reshape(shape))
    return v


def minpool3d(v: torch.Tensor, k: int = KMIN) -> torch.Tensor:
    """Grey erosion. `max_pool3d` pads with -inf, so -maxpool(-x) is a true min over the
    window with the padded entries ignored."""
    if k <= 1:
        return v
    return -F.max_pool3d(-v, kernel_size=k, stride=1, padding=k // 2)


FAST_DS = 4       # the lateral stride the FAST path estimates B on


def background(raw: torch.Tensor, minpool: bool = True,
               sz: float = SZ, syx: float = SYX, kmin: int = KMIN,
               fast: bool = False, ds: int = FAST_DS) -> torch.Tensor:
    """The local background estimate B of a (W, Z, Y, X) float32 stack, same shape.

    THE FAST PATH, and why it is not an approximation anybody has to take on trust. `B` is
    BAND-LIMITED BY CONSTRUCTION -- a Gaussian of sigma 13 px carries nothing above 1/13 px^-1 --
    so estimating it on a grid 4x coarser in y/x and interpolating back loses nothing the
    operator uses. The erosion and the decimation are done by ONE `max_pool3d` with stride
    (1, ds, ds). `code/haze_fastgate.py` measures the exact-vs-fast difference on a named frame
    and the receipt carries it; it is never asserted.
    """
    v = raw[:, None]                                     # (W, 1, Z, Y, X)
    if not fast:
        if minpool:
            v = minpool3d(v, kmin)
        return gauss3d(v, sz, syx)[:, 0]
    if minpool:
        v = -F.max_pool3d(-v, kernel_size=(1, kmin, kmin), stride=(1, ds, ds),
                          padding=(0, kmin // 2, kmin // 2))
    else:
        v = F.avg_pool3d(v, kernel_size=(1, ds, ds), stride=(1, ds, ds))
    v = gauss3d(v, sz, syx / ds)
    v = F.interpolate(v, size=tuple(raw.shape[1:]), mode="trilinear", align_corners=False)
    return v[:, 0]


def flatten(raw: torch.Tensor, floor: float, minpool: bool = True,
            sz: float = SZ, syx: float = SYX, kmin: int = KMIN,
            fast: bool = False, ds: int = FAST_DS):
    """raw' = clamp(raw - clamp(B - floor, 0), 0). Returns (raw', B, E)."""
    b = background(raw, minpool=minpool, sz=sz, syx=syx, kmin=kmin, fast=fast, ds=ds)
    e = (b - floor).clamp(min=0.0)
    return (raw - e).clamp(min=0.0), b, e


def film_floor(z_arr, n_t: int, ds, device, minpool: bool = True,
               sz: float = SZ, syx: float = SYX, kmin: int = KMIN,
               fstride: int = FSTRIDE, vstride: int = VSTRIDE, fast: bool = False):
    """The film's baseline background and its haze ratio, from a strided subsample.

    Returns every quantile of `B` the two declared floors need (p05 and p50), `p95`, the haze
    ratio `R_haze = p95/p05`, and the count of frames and voxels the estimate used -- MEASURED
    counters, never derived ones.
    """
    dz, dy, dx = ds
    ts = list(range(0, n_t, fstride)) or [0]
    vals = []
    for t in ts:
        raw = torch.from_numpy(
            z_arr[t:t + 1, ::dz, ::dy, ::dx].astype("float32")).to(device)
        b = background(raw, minpool=minpool, sz=sz, syx=syx, kmin=kmin, fast=fast)
        vals.append(b[0, :, ::vstride, ::vstride].reshape(-1))
    v = torch.cat(vals)
    qq = torch.tensor([0.05, 0.25, 0.5, 0.95], device=v.device, dtype=torch.float32)
    p05, p25, p50, p95 = (float(x) for x in torch.quantile(v.float(), qq))
    return {"floor": p05, "floor_p05": p05, "floor_p50": p50, "bg_p05": p05, "bg_p25": p25,
            "bg_p50": p50, "bg_p95": p95, "R_haze": p95 / max(p05, 1e-6),
            "n_frames_used": len(ts), "n_voxels_used": int(v.numel()),
            "params": {"KMIN": kmin if minpool else 0, "SZ": sz, "SYX": syx,
                       "FSTRIDE": fstride, "VSTRIDE": vstride, "FAST": fast}}
