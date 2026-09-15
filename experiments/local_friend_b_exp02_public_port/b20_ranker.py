"""B20 division ranker prototype on the local port's raw graphs (CONTEXT_FRIEND_B.md §38.3).

Builds on tools/divranker.py (team, 2026-09-06): its candidate generator = every parent with ONE child plus up to
k nearest orphan track-starts at t+1 within `parent_um` (an open gate: no mutual-NN, divergence or symmetry
filters), its GT labels (parent within 7 um of a GT divider AND both daughters within 7 um of its two children),
and its 15 geometric/track features. Added here:
    peak_p, peak_c, peak_q      detector confidence at parent / existing child / candidate daughter (peak_prob)
    vol_c, vol_q                daughter half-max volume at t+1 relative to the frame's detection median
    vol_c2, vol_q2              same at t+2 for their successors (post-split shrinkage, CONTEXT_FRIEND_B §37)
Evaluation: GroupKFold by video, average precision and precision@k of the out-of-fold score; the pipeline-level
readout (official div_J with the ranker replacing `parent_dist + 0.15*sister_dist`) is a separate step.

    python b20_ranker.py --tag exp29pp [--stems ...] [--no-image]
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent.parent
DATA = ROOT / "biohub-cell-tracking-during-development" / "train"
CACHE = ROOT / ".public_local_cache"
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(Path(__file__).resolve().parent))
import postproc, divranker  # noqa: E402
from b25_image_features import box_stats  # noqa: E402
VOXEL = postproc.VOXEL


def image_feats(stem, g, cands, det_by_t, rz=2, ryx=6):
    import zarr
    arr = zarr.open(str(DATA / f"{stem}.zarr" / "0"), mode="r"); T = arr.shape[0]
    cache = {}
    def frame(k):
        if k not in cache:
            if len(cache) > 4: cache.pop(min(cache))
            cache[k] = np.asarray(arr[k])
        return cache[k]
    med_cache = {}
    def frame_median(t):
        if t not in med_cache:
            pts = det_by_t.get(t, [])
            if len(pts) > 80: pts = [pts[k] for k in np.linspace(0, len(pts) - 1, 80).astype(int)]
            vols = [box_stats(frame(t), z, y, x, rz, ryx)[2] for (z, y, x) in pts]
            med_cache[t] = float(np.median(vols)) if len(vols) >= 5 and np.median(vols) > 0 else None
        return med_cache[t]
    def rel_vol(n):
        d = g.nodes[n]; t = int(d["t"])
        if t < 0 or t >= T: return np.nan
        m = frame_median(t)
        if m is None: return np.nan
        return box_stats(frame(t), d["z"], d["y"], d["x"], rz, ryx)[2] / m
    out = []
    for p, c, q, _ in cands:
        cs = list(g.successors(c)); qs = list(g.successors(q))
        out.append([rel_vol(c), rel_vol(q),
                    rel_vol(cs[0]) if len(cs) == 1 else np.nan, rel_vol(qs[0]) if len(qs) == 1 else np.nan])
    return np.array(out, float)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", default="exp29pp"); ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--parent-um", type=float, default=9.0); ap.add_argument("--k-starts", type=int, default=3)
    ap.add_argument("--no-image", action="store_true"); a = ap.parse_args()
    raw = CACHE / a.tag / "raw"
    stems = a.stems or sorted(p.stem for p in raw.glob("*.geff"))
    X, Y, G, meta = [], [], [], []; n_gt = 0; n_lab = 0
    names = list(divranker.FEATURE_NAMES) + ["peak_p", "peak_c", "peak_q"] + ([] if a.no_image else ["vol_c", "vol_q", "vol_c2", "vol_q2"])
    for stem in stems:
        g = postproc.load(raw / f"{stem}.geff")
        gt = divranker._load_gt(DATA / f"{stem}.geff")
        n_gt += sum(1 for n in gt.nodes if gt.out_degree(n) >= 2)
        cands = list(divranker.candidates(g, parent_um=a.parent_um, k_starts=a.k_starts))
        y = divranker.label_candidates(g, gt, cands)
        if not cands: continue
        pk = lambda n: float(g.nodes[n].get("peak_prob", np.nan))
        F = np.array([f + [pk(p), pk(c), pk(q)] for p, c, q, f in cands], float)
        if not a.no_image:
            det_by_t = {}
            for n, d in g.nodes(data=True): det_by_t.setdefault(int(d["t"]), []).append((d["z"], d["y"], d["x"]))
            F = np.concatenate([F, image_feats(stem, g, cands, det_by_t)], 1)
        X.append(F); Y.append(y); G += [stem] * len(y); meta += [(stem, p, c, q) for p, c, q, _ in cands]
        n_lab += int(y.sum())
        print(f"  {stem}: {len(cands)} candidates, {int(y.sum())} positive (GT divisions {sum(1 for n in gt.nodes if gt.out_degree(n) >= 2)})", flush=True)
    X = np.concatenate(X); Y = np.concatenate(Y); G = np.array(G)
    X = np.nan_to_num(X, nan=-1.0)
    print(f"\n{len(stems)} videos | GT divisions {n_gt} | candidates {len(Y)} | positives {int(Y.sum())} (reach {int(Y.sum())/max(n_gt,1):.0%})")
    from sklearn.metrics import average_precision_score, roc_auc_score
    # baseline: the public ranking key, ascending parent_dist + 0.15*sister_dist  (lower = better)
    d_pq = X[:, names.index("d_pq")]; d_cq = X[:, names.index("d_cq")]
    base = -(d_pq + 0.15 * d_cq)
    print(f"public key       AP={average_precision_score(Y, base):.3f} AUC={roc_auc_score(Y, base):.3f}")
    sis = d_cq; print(f"sister-first key AP={average_precision_score(Y, sis):.3f} AUC={roc_auc_score(Y, sis):.3f}")
    clf, oof, aps = divranker.fit_and_eval(X, Y, G)
    print(f"GBM ranker (LOO-video OOF): AP={average_precision_score(Y, oof):.3f} AUC={roc_auc_score(Y, oof):.3f} | per-fold AP {np.round(aps,3).tolist()}")
    order = np.argsort(-oof)
    for k in (5, 10, 20, 50):
        print(f"  precision@{k}: {Y[order[:k]].mean():.2f} ({int(Y[order[:k]].sum())} of {k}); recall@{k}: {Y[order[:k]].sum()/max(Y.sum(),1):.2f}")
    try:
        from sklearn.inspection import permutation_importance
        imp = permutation_importance(clf, X, Y, scoring="average_precision", n_repeats=5, random_state=0).importances_mean
        print("feature importance (permutation, AP):")
        for n_, v in sorted(zip(names, imp), key=lambda kv: -kv[1])[:10]: print(f"  {n_:14s} {v:+.3f}")
    except Exception as e: print("importance failed:", e)
    out = Path(__file__).resolve().parent / "results" / f"b20_ranker_{a.tag}.json"
    out.write_text(json.dumps({"videos": stems, "n_gt": n_gt, "n_cand": int(len(Y)), "n_pos": int(Y.sum()), "names": names,
                               "ap_public": float(average_precision_score(Y, base)), "ap_gbm_oof": float(average_precision_score(Y, oof))}, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
