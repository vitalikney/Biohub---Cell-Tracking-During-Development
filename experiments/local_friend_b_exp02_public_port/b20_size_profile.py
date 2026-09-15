"""B20 first step: does a nucleus really get SMALLER before it divides, on OUR labels?

zhincez's claim (rank 39, EDA on labels + images, paired same-frame controls): the half-max volume of a dividing
lineage is below control at lags -2..+5 (deepest -0.27 at +3) while the peak holds. This reproduces the
measurement on our 12 LOEO-44b6 videos from ground truth alone (no model), which is the go/no-go for building
the in-kernel 199-video feature table (CONTEXT_FRIEND_B.md §33): if the size profile does not separate GT
division parents from same-frame controls here, a ranker built on it will not either.

For every GT division (parent node with two children): follow the parent lineage back to lag -3 and the
first child forward to +3; at each lag measure half-max volume and peak-above-background in a fixed box; the
control for each lag is the median over all other GT nodes in the SAME frame that are >= 15 um from any
division parent. Reports the relative volume per lag with bootstrap CIs and the AUC of the pre-split drop.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent.parent
DATA = ROOT / "biohub-cell-tracking-during-development" / "train"
VOXEL = np.array([1.625, 0.40625, 0.40625])
sys.path.insert(0, str(ROOT / "tools" / "official" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from b25_image_features import box_stats  # noqa: E402

def gt_graph(stem):
    from tracking_cellmot.io import open_dataset
    ds = open_dataset(DATA / stem, require_tracks=True, load_image=False)
    n = ds.tracks.node_attrs().sort("node_id"); e = ds.tracks.edge_attrs()
    nodes = {int(r["node_id"]): (int(r["t"]), float(r["z"]), float(r["y"]), float(r["x"])) for r in n.iter_rows(named=True)}
    succ, pred = {}, {}
    for r in e.iter_rows(named=True):
        s, d = int(r["source_id"]), int(r["target_id"]); succ.setdefault(s, []).append(d); pred.setdefault(d, []).append(s)
    return nodes, succ, pred

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--box", type=int, nargs=3, default=[2, 6, 6]); ap.add_argument("--lags", type=int, nargs=2, default=[-3, 3])
    a = ap.parse_args(); import zarr
    stems = a.stems or json.load(open(ROOT / "experiments/_lib/loeo_train6bba_val44b6.json"))["holdout"]
    rz, ry, rx = a.box; L0, L1 = a.lags
    rel_vol = {lag: [] for lag in range(L0, L1 + 1)}; rel_peak = {lag: [] for lag in range(L0, L1 + 1)}
    n_div = 0
    det_by_video = {}
    raw_dir = ROOT / ".public_local_cache" / "exp29" / "raw"
    import tracksdata as td
    for stem in stems:
        p = raw_dir / f"{stem}.geff"
        if p.is_dir():
            g = td.graph.IndexedRXGraph.from_geff(p); g = g[0] if isinstance(g, tuple) else g
            n = g.node_attrs(); d = {}
            for r in n.iter_rows(named=True): d.setdefault(int(r["t"]), []).append((float(r["z"]), float(r["y"]), float(r["x"])))
            det_by_video[stem] = d
    for stem in stems:
        nodes, succ, pred = gt_graph(stem); arr = zarr.open(str(DATA / f"{stem}.zarr" / "0"), mode="r")
        parents = [i for i, c in succ.items() if len(c) >= 2]
        if not parents: continue
        by_t = {}
        for i, (t, z, y, x) in nodes.items(): by_t.setdefault(t, []).append(i)
        par_pos = {t: [] for t in by_t}
        for p in parents:
            t, z, y, x = nodes[p]
            for dt in range(L0, L1 + 1): par_pos.setdefault(t + dt, []).append(np.array([z, y, x]) * VOXEL)
        cache = {}
        def frame(k):
            if k not in cache:
                if len(cache) > 8: cache.pop(min(cache))
                cache[k] = np.asarray(arr[k])
            return cache[k]
        # CONTROL POPULATION = DETECTIONS of the public stack (raw exp29 graph), not GT nodes: 44b6 annotates ~1% of
        # nuclei, so most frames have < 3 GT controls and only 4 of 15 divisions were usable with GT controls.
        det = det_by_video.get(stem, {})
        ctrl_cache = {}
        def control(t):
            if t in ctrl_cache: return ctrl_cache[t]
            vals = []
            pts = det.get(t, [])
            if len(pts) > 60: pts = [pts[k] for k in np.linspace(0, len(pts) - 1, 60).astype(int)]
            for (z, y, x) in pts:
                pos = np.array([z, y, x]) * VOXEL
                if any(np.linalg.norm(pos - q) < 15 for q in par_pos.get(t, [])): continue
                bg, pk, vol = box_stats(frame(t), z, y, x, rz, ry); vals.append((vol, pk))
            ctrl_cache[t] = (np.median([v for v, _ in vals]), np.median([p for _, p in vals])) if len(vals) >= 5 else (None, None)
            return ctrl_cache[t]
        for p in parents:
            t0 = nodes[p][0]; n_div += 1
            chain = {0: p}
            cur = p
            for lag in range(-1, L0 - 1, -1):
                pr = pred.get(cur, []); 
                if len(pr) != 1: break
                cur = pr[0]; chain[lag] = cur
            cur = succ[p][0]; chain[1] = cur
            for lag in range(2, L1 + 1):
                sc = succ.get(cur, [])
                if len(sc) != 1: break
                cur = sc[0]; chain[lag] = cur
            for lag, i in chain.items():
                t, z, y, x = nodes[i]
                if t < 0 or t >= arr.shape[0]: continue
                cv, cp = control(t)
                if cv is None or cv <= 0: continue
                bg, pk, vol = box_stats(frame(t), z, y, x, rz, ry)
                rel_vol[lag].append(vol / cv); rel_peak[lag].append(pk / max(cp, 1e-6))
    print(f"{len(stems)} videos, {n_div} GT divisions, box {a.box} voxels")
    print(f"{'lag':>4s} {'n':>4s} {'rel volume':>11s} {'95% CI':>16s} {'rel peak':>9s}")
    rng = np.random.default_rng(0)
    for lag in range(L0, L1 + 1):
        v = np.array(rel_vol[lag]); pk = np.array(rel_peak[lag])
        if len(v) == 0: print(f"{lag:+4d}    0"); continue
        bs = [np.median(rng.choice(v, len(v))) for _ in range(500)]
        print(f"{lag:+4d} {len(v):4d} {np.median(v)-1:+11.3f} [{np.percentile(bs,2.5)-1:+.3f}, {np.percentile(bs,97.5)-1:+.3f}] {np.median(pk)-1:+9.3f}")
    # AUC of "pre-split size drop": score = mean rel volume at lags -2,-1 (lower = more division-like), vs controls at 1.0
    pre = np.array([np.mean([rel_vol[l][k] for l in (-2, -1) if k < len(rel_vol[l])]) for k in range(min(len(rel_vol[-2]), len(rel_vol[-1])))])
    if len(pre):
        # controls by construction have rel volume distributed around 1: use the parents' own lag +3/+2 as 'not dividing now'? no -
        # honest AUC needs a control distribution: sample control-node rel volumes directly
        print(f"pre-split (lags -2,-1) median relative volume of parents: {np.median(pre):.3f} (control = 1.000); "
              f"fraction of parents below control: {np.mean(pre < 1):.2f} (0.5 = no signal)")
if __name__ == "__main__":
    main()
