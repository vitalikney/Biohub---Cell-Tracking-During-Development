"""Image features for B25 (peak pruning) and B20 (division ranking): SIZE, not brightness.

zhincez (rank 39, 2026-09-15, CPU EDA with paired same-frame controls): a dividing nucleus gets SMALLER, not
dimmer - the half-max volume in a box around the annotated position is -0.27 relative to controls at +3 frames
and already below at -2/-1, while the peak intensity holds; mean intensity falls only because a fixed box around
a smaller object reads more background. So the usable image feature is a size profile over a temporal window,
measured relative to a same-frame control.

Per detection (t, z, y, x) this computes, in a fixed box around the position:
    bg          20th percentile of the box (same local-background estimate the public gap-refine uses)
    peak        max - bg
    vol_halfmax number of voxels above bg + 0.5 * peak            <- the size
    vol_rel     vol_halfmax / median vol_halfmax of all detections in the same frame   <- same-frame control
    vol_prev, vol_next   the same box at t-1 and t+1 (temporal profile, cheap version)
    dz_int      ratio of the box's intensity above bg to the frame's median (a crude "is there an object here")

Results are cached per video as results/imgfeat/<stem>.npz keyed by node_id so b25_prune.py can merge them.

    python b25_image_features.py --tag exp29pp_4vid [--stems ...] [--box 2 6 6]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE = ROOT / ".public_local_cache"
DATA = ROOT / "biohub-cell-tracking-during-development" / "train"
OUT = Path(__file__).resolve().parent / "results" / "imgfeat"


def load_nodes(path: Path):
    import tracksdata as td
    g = td.graph.IndexedRXGraph.from_geff(path)
    g = g[0] if isinstance(g, tuple) else g
    n = g.node_attrs().sort("node_id")
    return (n["node_id"].to_numpy().astype(int), n["t"].to_numpy().astype(int),
            n["z"].to_numpy(), n["y"].to_numpy(), n["x"].to_numpy())


def box_stats(frame: np.ndarray, z: float, y: float, x: float, rz: int, ryx: int):
    Z, Y, X = frame.shape
    zi, yi, xi = int(round(z)), int(round(y)), int(round(x))
    z0, z1 = max(0, zi - rz), min(Z, zi + rz + 1)
    y0, y1 = max(0, yi - ryx), min(Y, yi + ryx + 1)
    x0, x1 = max(0, xi - ryx), min(X, xi + ryx + 1)
    box = frame[z0:z1, y0:y1, x0:x1].astype(np.float32)
    if box.size == 0:
        return 0.0, 0.0, 0.0
    bg = float(np.percentile(box, 20.0))
    peak = float(box.max() - bg)
    if peak <= 0:
        return bg, 0.0, 0.0
    vol = int((box > bg + 0.5 * peak).sum())
    return bg, peak, float(vol)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="cache tag whose raw/ graphs give the node positions")
    ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--box", type=int, nargs=3, default=[2, 6, 6], help="half-sizes in voxels: z y x")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    import zarr

    OUT.mkdir(parents=True, exist_ok=True)
    raw_dir = CACHE / args.tag / "raw"
    stems = args.stems or sorted(p.stem for p in raw_dir.glob("*.geff"))
    rz, ry, rx = args.box
    for stem in stems:
        dst = OUT / f"{stem}.npz"
        if dst.is_file() and not args.force:
            print(f"{stem}: cached"); continue
        ids, t, z, y, x = load_nodes(raw_dir / f"{stem}.geff")
        arr = zarr.open(str(DATA / f"{stem}.zarr" / "0"), mode="r")
        T = arr.shape[0]
        n = len(ids)
        bg = np.zeros(n); peak = np.zeros(n); vol = np.zeros(n); vol_prev = np.zeros(n); vol_next = np.zeros(n)
        frame_cache: dict[int, np.ndarray] = {}

        def frame(k: int) -> np.ndarray:
            if k not in frame_cache:
                if len(frame_cache) > 3:
                    frame_cache.pop(min(frame_cache))
                frame_cache[k] = np.asarray(arr[k])
            return frame_cache[k]

        for k in np.unique(t):
            m = np.where(t == k)[0]
            f0 = frame(int(k))
            fp = frame(int(k) - 1) if k > 0 else None
            fn = frame(int(k) + 1) if k + 1 < T else None
            for i in m:
                bg[i], peak[i], vol[i] = box_stats(f0, z[i], y[i], x[i], rz, ry)
                vol_prev[i] = box_stats(fp, z[i], y[i], x[i], rz, ry)[2] if fp is not None else vol[i]
                vol_next[i] = box_stats(fn, z[i], y[i], x[i], rz, ry)[2] if fn is not None else vol[i]
            med = np.median(vol[m]) if len(m) else 1.0
            if med <= 0:
                med = 1.0
            # same-frame control: size relative to the frame's typical detection
            vol_rel_frame = vol[m] / med
            if k == np.unique(t)[0]:
                vol_rel = np.zeros(n)
            vol_rel[m] = vol_rel_frame
        np.savez(dst, node_id=ids, bg=bg, peak=peak, vol_halfmax=vol, vol_rel=vol_rel,
                 vol_prev=vol_prev, vol_next=vol_next, box=np.array(args.box))
        print(f"{stem}: {n} nodes | vol_halfmax median {np.median(vol):.0f} vox, "
              f"p10 {np.percentile(vol, 10):.0f}, p90 {np.percentile(vol, 90):.0f} | peak median {np.median(peak):.0f}")


if __name__ == "__main__":
    main()
