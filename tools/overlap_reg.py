"""GT-free registration of overlapping space-time crops by exact-content anchor hashing (OVERLAP-CONSENSUS line).

Design: research/wf_ideas_v2/r2_research_overlap-consensus.json (implementation_notes, REGISTRATION) with the repairs of
its verifiers (r2_verify_overlap-consensus_{arithmetic,feasibility,transfer}.json): exact voxel equality, >= 5
overlapping frames, >= 5% spatial overlap, saturated buckets skipped, prefix restriction optional (cross-prefix
acceptances are always reported; expected 0). Gate G-A: CONTEXT.md 2026-09-26 08:58 UTC.

Method, per video and frame (raw uint16 volume Z x Y x X):
  anchors = voxels where raw == its 3x7x7 max and raw > the frame's p99.5, >= 1 voxel from the z borders and >= 3 from
            the y/x borders (so the 3x7x7 window and the 3x5x5 patch lie fully inside the crop);
  key     = 64-bit hash of the raw 3x5x5 uint16 patch around the anchor (blake2b, digest_size 8, little endian);
All anchors of all videos go into one table keyed by hash. Every bucket that holds >= 2 videos (and <= max_bucket
entries) votes for (videoA, videoB, dt, dz, dy, dx) with offset = coord_A - coord_B (the convention of
experiments/l2_daughternet/splits.json offset_tzyx_a_minus_b; pair names are ordered a < b). A pair is accepted with its
best candidate offset (candidates tried in vote order) only if
  votes >= 30, the overlap spans >= 5 frames and >= 5% of the smaller crop's volume, and the raw voxels of the 3D
  overlap are exactly equal on >= 99.9% of the voxels in each of 3 frames spread over the overlap.

The API is reader-agnostic: a video is a callable read_frame(t) -> np.ndarray (Z, Y, X) plus its shape (T, Z, Y, X), so
the same code runs on local zarrs and inside a Kaggle notebook. Backends for the 3x7x7 max test: 'auto' = torch
max_pool3d on a GPU when one is available, else 'sparse' (exact: threshold first, then the window max of the ~0.5%
candidates only); 'scipy' = scipy.ndimage.maximum_filter (reference). All give the same anchors, since anchors are
interior and padding never matters (tests/test_overlap_reg.py). Pure numpy/hashlib apart from optional torch/scipy/zarr.

Local use (G-A; 'nice -n 19' on the shared laptop):
    nice -n 19 python tools/overlap_reg.py --data-dir biohub-cell-tracking-during-development/train --workers 4 \
        --cache <dir> --out <file.json> --check-splits experiments/l2_daughternet/splits.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

PCT = 99.5
KERNEL = (3, 7, 7)
BORDER = (1, 3, 3)
PATCH = (3, 5, 5)
MIN_VOTES = 30
MIN_FRAMES = 5
MIN_SPATIAL_FRAC = 0.05
MIN_EQUAL_FRAC = 0.999
N_CHECK_FRAMES = 3
MAX_BUCKET = 10
MAX_CANDIDATES = 3


# ----------------------------------------------------------------------------------------------------------------------
# per frame
# ----------------------------------------------------------------------------------------------------------------------
def frame_threshold(raw: np.ndarray, pct: float = PCT) -> float:
    """np.percentile(raw, pct) ('linear') computed exactly from a histogram (integer frames; ~5x faster)."""
    flat = np.asarray(raw).ravel()
    n = flat.size
    if n == 0:
        return math.inf
    if flat.dtype.kind not in "ui" or flat.dtype.itemsize > 2:
        return float(np.percentile(flat, pct))
    vals = flat.astype(np.int64) if flat.dtype.kind == "i" else flat
    base = int(vals.min()) if flat.dtype.kind == "i" else 0
    counts = np.bincount((vals - base) if base else vals)
    cum = np.cumsum(counts)
    idx = pct / 100.0 * (n - 1)
    lo_k, hi_k = int(math.floor(idx)), int(math.ceil(idx))
    lo = float(np.searchsorted(cum, lo_k, side="right") + base)
    hi = float(np.searchsorted(cum, hi_k, side="right") + base)
    frac = idx - lo_k
    return lo + (hi - lo) * frac


def _torch_device():
    try:
        import torch  # noqa: F401
    except Exception:
        return None
    import torch
    return torch.device("cuda") if torch.cuda.is_available() else None


def local_max_mask(raw: np.ndarray, kernel=KERNEL, backend: str = "auto") -> np.ndarray:
    """Boolean mask raw == max over the kernel window. backend: 'auto' (torch on GPU if present, else scipy),
    'scipy', 'torch' (torch on GPU if present, else torch on CPU; slow)."""
    raw = np.asarray(raw)
    if backend == "auto":
        backend = "torch" if _torch_device() is not None else "scipy"
    if backend == "scipy":
        from scipy.ndimage import maximum_filter
        return raw == maximum_filter(raw, size=tuple(kernel), mode="nearest")
    if backend == "torch":
        import torch
        import torch.nn.functional as F
        dev = _torch_device() or torch.device("cpu")
        x = torch.from_numpy(raw.astype(np.float32, copy=False)).to(dev)[None, None]
        pad = tuple(k // 2 for k in kernel)
        mx = F.max_pool3d(x, kernel_size=tuple(kernel), stride=1, padding=pad)
        return (x == mx)[0, 0].cpu().numpy()
    raise ValueError(f"unknown backend {backend!r}")


def patch_hashes(raw: np.ndarray, zyx: np.ndarray, patch=PATCH) -> np.ndarray:
    """uint64 blake2b(digest_size=8) of the little-endian uint16 patch centred on every (z, y, x) row."""
    raw = np.ascontiguousarray(raw, dtype="<u2")
    zyx = np.asarray(zyx, dtype=np.int64).reshape(-1, 3)
    hz, hy, hx = (p // 2 for p in patch)
    out = np.empty(len(zyx), dtype=np.uint64)
    for i, (z, y, x) in enumerate(zyx.tolist()):
        buf = np.ascontiguousarray(raw[z - hz:z + hz + 1, y - hy:y + hy + 1, x - hx:x + hx + 1]).tobytes()
        out[i] = int.from_bytes(hashlib.blake2b(buf, digest_size=8).digest(), "little")
    return out


def frame_anchors(raw: np.ndarray, pct: float = PCT, kernel=KERNEL, border=BORDER, patch=PATCH,
                  backend: str = "auto", timing: dict | None = None) -> tuple[np.ndarray, np.ndarray]:
    """-> (hashes uint64 (N,), zyx int32 (N, 3)) in C order of the voxels."""
    t0 = time.perf_counter()
    raw = np.asarray(raw)
    if raw.ndim != 3:
        raise ValueError(f"frame must be 3D (Z, Y, X), got shape {raw.shape}")
    thr = frame_threshold(raw, pct)
    bz, by, bx = border
    inner = np.zeros(raw.shape, dtype=bool)
    inner[bz:raw.shape[0] - bz, by:raw.shape[1] - by, bx:raw.shape[2] - bx] = True
    if backend == "auto":
        backend = "torch" if _torch_device() is not None else "sparse"
    if backend == "sparse" and all(b >= k // 2 for b, k in zip(border, kernel)):
        # exact: the threshold keeps ~0.5% of the voxels; test only those against their (interior) window max
        cand = np.argwhere((raw > thr) & inner)
        if len(cand):
            hz, hy, hx = (k // 2 for k in kernel)
            win = np.lib.stride_tricks.sliding_window_view(raw, tuple(kernel))
            wmax = win[cand[:, 0] - hz, cand[:, 1] - hy, cand[:, 2] - hx].max(axis=(1, 2, 3))
            cand = cand[wmax == raw[cand[:, 0], cand[:, 1], cand[:, 2]]]
        zyx = cand.astype(np.int32).reshape(-1, 3)
        t1 = time.perf_counter()
    else:
        mask = local_max_mask(raw, kernel, "scipy" if backend == "sparse" else backend)
        t1 = time.perf_counter()
        mask &= raw > thr
        mask &= inner
        zyx = np.argwhere(mask).astype(np.int32)
    h = patch_hashes(raw, zyx, patch)
    t2 = time.perf_counter()
    if timing is not None:
        timing["filter_s"] = timing.get("filter_s", 0.0) + (t1 - t0)
        timing["hash_s"] = timing.get("hash_s", 0.0) + (t2 - t1)
    return h, zyx


def video_anchors(read_frame, n_frames: int, frames=None, backend: str = "auto", **kw) -> dict:
    """All anchors of one video: {'hash' uint64 (N,), 'tzyx' int32 (N, 4), 'timing' {...}}. read_frame(t) -> (Z,Y,X)."""
    frames = range(int(n_frames)) if frames is None else frames
    hs, cs = [], []
    timing = {"read_s": 0.0, "filter_s": 0.0, "hash_s": 0.0, "frames": 0}
    for t in frames:
        t0 = time.perf_counter()
        raw = np.asarray(read_frame(int(t)))
        timing["read_s"] += time.perf_counter() - t0
        h, zyx = frame_anchors(raw, backend=backend, timing=timing, **kw)
        hs.append(h)
        cs.append(np.concatenate([np.full((len(zyx), 1), int(t), dtype=np.int32), zyx], axis=1))
        timing["frames"] += 1
    h = np.concatenate(hs) if hs else np.zeros(0, dtype=np.uint64)
    c = np.concatenate(cs) if cs else np.zeros((0, 4), dtype=np.int32)
    timing["per_frame_s"] = (timing["read_s"] + timing["filter_s"] + timing["hash_s"]) / max(1, timing["frames"])
    return {"hash": h, "tzyx": c, "timing": timing}


def estimate_seconds(n_videos: int, n_frames: int, per_frame_s: float, workers: int = 1) -> float:
    """Wall-clock estimate of the anchor pass (the voting and the 3-frame checks are small against it)."""
    return float(n_videos) * float(n_frames) * float(per_frame_s) / max(1, int(workers))


# ----------------------------------------------------------------------------------------------------------------------
# voting
# ----------------------------------------------------------------------------------------------------------------------
def prefix_of(name: str) -> str:
    return str(name).split("_", 1)[0]


def vote_offsets(anchor_sets: dict, max_bucket: int = MAX_BUCKET) -> tuple[dict, dict]:
    """anchor_sets {name: {'hash', 'tzyx'}} -> ({(a, b): [((dt, dz, dy, dx), votes), ...] by votes desc}, stats).
    offset = coord_a - coord_b, a < b by name. Buckets with more than max_bucket entries are skipped."""
    names = sorted(anchor_sets)
    hs, vs, cs = [], [], []
    for i, n in enumerate(names):
        h = np.asarray(anchor_sets[n]["hash"], dtype=np.uint64).reshape(-1)
        hs.append(h)
        vs.append(np.full(len(h), i, dtype=np.int32))
        cs.append(np.asarray(anchor_sets[n]["tzyx"], dtype=np.int32).reshape(-1, 4))
    stats = {"videos": len(names), "anchors": 0, "buckets_multi": 0, "buckets_skipped_large": 0, "pair_votes": 0}
    if not names:
        return {}, stats
    h = np.concatenate(hs)
    v = np.concatenate(vs)
    c = np.concatenate(cs)
    stats["anchors"] = int(len(h))
    order = np.argsort(h, kind="stable")
    h, v, c = h[order], v[order], c[order]
    if len(h) == 0:
        return {}, stats
    starts = np.flatnonzero(np.r_[True, h[1:] != h[:-1]])
    lens = np.diff(np.r_[starts, len(h)])
    stats["buckets_multi"] = int(np.count_nonzero(lens >= 2))
    stats["buckets_skipped_large"] = int(np.count_nonzero(lens > max_bucket))
    rows = []
    for k in range(2, int(max_bucket) + 1):
        s = starts[lens == k]
        if len(s) == 0:
            continue
        idx = s[:, None] + np.arange(k)[None, :]
        for i in range(k):
            for j in range(i + 1, k):
                ii, jj = idx[:, i], idx[:, j]
                va, vb = v[ii], v[jj]
                keep = va != vb
                if not keep.any():
                    continue
                ii, jj, va, vb = ii[keep], jj[keep], va[keep], vb[keep]
                swap = va > vb
                a_idx = np.where(swap, jj, ii)
                b_idx = np.where(swap, ii, jj)
                off = c[a_idx].astype(np.int64) - c[b_idx].astype(np.int64)
                rows.append(np.concatenate([np.minimum(va, vb)[:, None].astype(np.int64),
                                            np.maximum(va, vb)[:, None].astype(np.int64), off], axis=1))
    out: dict = {}
    if rows:
        allr = np.concatenate(rows)
        stats["pair_votes"] = int(len(allr))
        uniq, cnt = np.unique(allr, axis=0, return_counts=True)
        for row, n in zip(uniq.tolist(), cnt.tolist()):
            key = (names[row[0]], names[row[1]])
            out.setdefault(key, []).append((tuple(int(x) for x in row[2:]), int(n)))
        for key in out:
            out[key].sort(key=lambda o: (-o[1], o[0]))
    return out, stats


# ----------------------------------------------------------------------------------------------------------------------
# geometry + exact check
# ----------------------------------------------------------------------------------------------------------------------
def overlap_geometry(shape_a, shape_b, offset) -> dict:
    """Overlap of crop A (T, Z, Y, X) and crop B placed at offset = coord_a - coord_b.
    -> {'lo_a', 'hi_a' (A coords, half-open, t z y x), 'n_frames', 'spatial_vox', 'spatial_frac'}."""
    sa = [int(s) for s in shape_a]
    sb = [int(s) for s in shape_b]
    off = [int(o) for o in offset]
    lo = [max(0, d) for d in off]
    hi = [min(a, b + d) for a, b, d in zip(sa, sb, off)]
    ext = [max(0, h - l) for l, h in zip(lo, hi)]
    vox = ext[1] * ext[2] * ext[3]
    denom = min(sa[1] * sa[2] * sa[3], sb[1] * sb[2] * sb[3])
    return {"lo_a": lo, "hi_a": hi, "n_frames": ext[0], "spatial_vox": vox,
            "spatial_frac": (vox / denom) if denom else 0.0}


def check_frames(n_frames: int, k: int = N_CHECK_FRAMES) -> list[int]:
    """k frame indices (0-based within the overlap) spread over it, avoiding the ends when possible."""
    if n_frames <= 0:
        return []
    pos = np.linspace(0, n_frames - 1, k + 2)[1:-1] if n_frames > k else np.arange(n_frames)
    return sorted({int(round(float(p))) for p in pos})


def verify_offset(read_a, read_b, shape_a, shape_b, offset, n_check: int = N_CHECK_FRAMES,
                  min_frames: int = MIN_FRAMES, min_spatial: float = MIN_SPATIAL_FRAC,
                  min_equal: float = MIN_EQUAL_FRAC) -> dict:
    """-> {'ok', 'reason', 'n_frames', 'spatial_frac', 'equal_fracs'}; reads 2 * n_check frames at most."""
    g = overlap_geometry(shape_a, shape_b, offset)
    res = {"ok": False, "reason": "", "n_frames": g["n_frames"], "spatial_frac": round(g["spatial_frac"], 6),
           "equal_fracs": []}
    if g["n_frames"] < min_frames:
        res["reason"] = "frames"
        return res
    if g["spatial_frac"] < min_spatial:
        res["reason"] = "spatial"
        return res
    dt, dz, dy, dx = (int(o) for o in offset)
    lo, hi = g["lo_a"], g["hi_a"]
    for k in check_frames(g["n_frames"], n_check):
        ta = lo[0] + k
        fa = np.asarray(read_a(ta))[lo[1]:hi[1], lo[2]:hi[2], lo[3]:hi[3]]
        fb = np.asarray(read_b(ta - dt))[lo[1] - dz:hi[1] - dz, lo[2] - dy:hi[2] - dy, lo[3] - dx:hi[3] - dx]
        if fa.shape != fb.shape or fa.size == 0:
            res["reason"] = "shape"
            return res
        res["equal_fracs"].append(round(float(np.count_nonzero(fa == fb)) / fa.size, 6))
    if min(res["equal_fracs"]) < min_equal:
        res["reason"] = "voxels"
        return res
    res["ok"] = True
    return res


def register(anchor_sets: dict, readers: dict, shapes: dict, min_votes: int = MIN_VOTES,
             same_prefix: bool = False, max_bucket: int = MAX_BUCKET, max_candidates: int = MAX_CANDIDATES,
             **verify_kw) -> dict:
    """Votes + exact checks -> {'pairs': [accepted], 'rejected': [...], 'stats': {...}}.
    readers {name: read_frame(t)}, shapes {name: (T, Z, Y, X)}. same_prefix=True restricts verification to pairs with
    the same filename prefix (cross-prefix vote winners are still counted in stats)."""
    votes, vstats = vote_offsets(anchor_sets, max_bucket=max_bucket)
    pairs, rejected = [], []
    stats = dict(vstats)
    stats.update({"candidate_pairs": 0, "accepted": 0, "accepted_cross_prefix": 0, "cross_prefix_candidates": 0,
                  "rejected_frames": 0, "rejected_spatial": 0, "rejected_voxels": 0, "rejected_shape": 0,
                  "frames_read": 0, "verify_s": 0.0})
    t0 = time.perf_counter()
    for (a, b) in sorted(votes):
        cands = [(o, n) for o, n in votes[(a, b)] if n >= min_votes][:max_candidates]
        if not cands:
            continue
        cross = prefix_of(a) != prefix_of(b)
        stats["candidate_pairs"] += 1
        stats["cross_prefix_candidates"] += int(cross)
        if cross and same_prefix:
            rejected.append({"a": a, "b": b, "offset": list(cands[0][0]), "votes": cands[0][1], "reason": "prefix"})
            continue
        for off, n in cands:
            r = verify_offset(readers[a], readers[b], shapes[a], shapes[b], off, **verify_kw)
            stats["frames_read"] += 2 * len(r["equal_fracs"])
            rec = {"a": a, "b": b, "offset": list(off), "votes": n, "n_frames": r["n_frames"],
                   "spatial_frac": r["spatial_frac"], "equal_fracs": r["equal_fracs"], "cross_prefix": cross}
            if r["ok"]:
                pairs.append(rec)
                stats["accepted"] += 1
                stats["accepted_cross_prefix"] += int(cross)
                break
            rec["reason"] = r["reason"]
            stats["rejected_" + r["reason"]] += 1
            rejected.append(rec)
    stats["verify_s"] = round(time.perf_counter() - t0, 3)
    return {"pairs": pairs, "rejected": rejected, "stats": stats}


def register_videos(readers: dict, shapes: dict, backend: str = "auto", log=None, **kw) -> dict:
    """One call for the kernel: anchors for every video (sequential; GPU max-pool when available), then register()."""
    anchor_sets, per_frame = {}, []
    t0 = time.perf_counter()
    for name in sorted(readers):
        anchor_sets[name] = video_anchors(readers[name], shapes[name][0], backend=backend)
        per_frame.append(anchor_sets[name]["timing"]["per_frame_s"])
        if log is not None:
            log(f"OVERLAPREG anchors {name}: {len(anchor_sets[name]['hash'])} in "
                f"{anchor_sets[name]['timing']['frames']} frames ({per_frame[-1]:.3f} s/frame)")
    anchor_s = time.perf_counter() - t0
    out = register(anchor_sets, readers, shapes, **kw)
    out["stats"]["anchor_s"] = round(anchor_s, 3)
    out["stats"]["mean_per_frame_s"] = round(float(np.mean(per_frame)), 4) if per_frame else 0.0
    return out


# ----------------------------------------------------------------------------------------------------------------------
# local helpers (zarr, multiprocessing, G-A check)
# ----------------------------------------------------------------------------------------------------------------------
def zarr_video(path) -> tuple:
    """-> (read_frame, shape) for a competition zarr (group with array '0', or a bare array)."""
    import zarr
    z = zarr.open(str(path), mode="r")
    arr = z["0"] if hasattr(z, "keys") and "0" in list(z.keys()) else z
    return (lambda t, _a=arr: np.asarray(_a[int(t)])), tuple(int(s) for s in arr.shape)


def _anchor_job(args) -> tuple:
    path, backend, cache = args
    name = Path(path).name[:-len(".zarr")] if str(path).endswith(".zarr") else Path(path).name
    if cache:
        cp = Path(cache) / f"{name}.npz"
        if cp.exists():
            with np.load(cp, allow_pickle=False) as z:
                return name, {"hash": z["hash"], "tzyx": z["tzyx"], "timing": json.loads(str(z["timing"]))}
    read, shape = zarr_video(path)
    res = video_anchors(read, shape[0], backend=backend)
    if cache:
        Path(cache).mkdir(parents=True, exist_ok=True)
        tmp = Path(cache) / f"{name}.tmp.npz"
        np.savez_compressed(tmp, hash=res["hash"], tzyx=res["tzyx"], timing=np.asarray(json.dumps(res["timing"])))
        os.replace(tmp, Path(cache) / f"{name}.npz")
    return name, res


def anchors_mp(paths, workers: int = 4, backend: str = "sparse", cache=None, log=print) -> dict:
    """Anchors for many zarr paths with a process pool (local runs; spawn-safe: call under __main__)."""
    jobs = [(str(p), backend, str(cache) if cache else None) for p in paths]
    out = {}
    if workers <= 1:
        for j in jobs:
            n, r = _anchor_job(j)
            out[n] = r
            if log:
                log(f"anchors {n}: {len(r['hash'])} ({r['timing']['per_frame_s']:.3f} s/frame)")
        return out
    import multiprocessing as mp
    with mp.get_context("spawn").Pool(int(workers)) as pool:
        for n, r in pool.imap_unordered(_anchor_job, jobs):
            out[n] = r
            if log:
                log(f"anchors {n}: {len(r['hash'])} ({r['timing']['per_frame_s']:.3f} s/frame) [{len(out)}/{len(jobs)}]")
    return out


def check_against_splits(pairs: list, splits_json, tol: int = 1) -> dict:
    """G-A readout: GT-linked pairs (splits.json meta.shared_annotation_links) found at the GT offset (+-tol voxel),
    accepted pairs per embryo, cross-embryo acceptances, extra 44b6 pairs without shared GT."""
    meta = json.loads(Path(splits_json).read_text(encoding="utf-8"))["meta"]
    links = meta["shared_annotation_links"]
    acc = {}
    for p in pairs:
        acc[(p["a"], p["b"])] = [int(x) for x in p["offset"]]
    found, wrong, missing = [], [], []
    gt_keys = set()
    for L in links:
        a, b = L["a"], L["b"]
        off = [int(x) for x in L["offset_tzyx_a_minus_b"]]
        if a > b:
            a, b, off = b, a, [-x for x in off]
        gt_keys.add((a, b))
        got = acc.get((a, b))
        if got is None:
            missing.append({"a": a, "b": b, "gt": off})
        elif all(abs(g - o) <= tol for g, o in zip(got, off)):
            found.append({"a": a, "b": b, "gt": off, "got": got})
        else:
            wrong.append({"a": a, "b": b, "gt": off, "got": got})
    by_emb: dict = {}
    for a, b in acc:
        key = prefix_of(a) if prefix_of(a) == prefix_of(b) else "cross"
        by_emb[key] = by_emb.get(key, 0) + 1
    extra = sorted(f"{a}|{b}" for (a, b) in acc if (a, b) not in gt_keys and prefix_of(a) == prefix_of(b) == "44b6")
    return {"gt_links": len(links), "found_at_gt_offset": len(found), "wrong_offset": wrong, "missing": missing,
            "accepted_by_embryo": by_emb, "extra_44b6_pairs": extra}


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--stems", nargs="*", default=None, help="subset of stems (default: every *.zarr)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--backend", default="sparse", choices=("sparse", "scipy", "torch", "auto"))
    ap.add_argument("--cache", default=None, help="per-video anchor npz cache dir")
    ap.add_argument("--same-prefix", action="store_true")
    ap.add_argument("--min-votes", type=int, default=MIN_VOTES)
    ap.add_argument("--check-splits", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    data = Path(a.data_dir)
    paths = sorted(data.glob("*.zarr"))
    if a.stems:
        want = set(a.stems)
        paths = [p for p in paths if p.name[:-5] in want]
    t0 = time.time()
    anchor_sets = anchors_mp(paths, workers=a.workers, backend=a.backend, cache=a.cache)
    t_anchor = time.time() - t0
    readers, shapes = {}, {}
    for p in paths:
        readers[p.name[:-5]], shapes[p.name[:-5]] = zarr_video(p)
    res = register(anchor_sets, readers, shapes, min_votes=a.min_votes, same_prefix=a.same_prefix)
    per_frame = [r["timing"]["per_frame_s"] for r in anchor_sets.values()]
    res["stats"]["anchor_wall_s"] = round(t_anchor, 1)
    res["stats"]["mean_per_frame_s"] = round(float(np.mean(per_frame)), 4) if per_frame else 0.0
    res["stats"]["workers"] = a.workers
    if a.check_splits:
        res["check"] = check_against_splits(res["pairs"], a.check_splits)
    s = res["stats"]
    print(f"OVERLAPREG videos {s['videos']} anchors {s['anchors']} candidates {s['candidate_pairs']} accepted "
          f"{s['accepted']} (cross-prefix {s['accepted_cross_prefix']}) rejected frames/spatial/voxels "
          f"{s['rejected_frames']}/{s['rejected_spatial']}/{s['rejected_voxels']} anchor wall {s['anchor_wall_s']} s "
          f"({s['mean_per_frame_s']} s/frame/worker) verify {s['verify_s']} s")
    if "check" in res:
        c = res["check"]
        print(f"G-A: {c['found_at_gt_offset']}/{c['gt_links']} GT-linked pairs at the GT offset; wrong offset "
              f"{len(c['wrong_offset'])}; missing {len(c['missing'])}; accepted by embryo {c['accepted_by_embryo']}; "
              f"extra 44b6 pairs {len(c['extra_44b6_pairs'])}")
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
