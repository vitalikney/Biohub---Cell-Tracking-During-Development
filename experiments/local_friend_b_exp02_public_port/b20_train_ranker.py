"""B20: train the division ranker on every video that has pass-1 outputs, with honest cross-validation.

Data: for each video with ckpt/dc/raw in `.public_local_cache/exp29pp/`, the candidate table of
`pass2_rank_divisions.candidates` (mode add or steal) on the CHECKPOINT graph, labelled by GT
(`divranker.label_candidates`: parent within 7 um of a GT divider and both daughters within 7 um of its children).

Negative subsampling (the steal pool is ~35k candidates per video): keep every positive, every candidate whose
daughter lies within 5 um of a positive's daughter (hard negatives), and a random 5% of the rest.

Cross-validation, two ways, both reported:
    by EMBRYO   train on 6bba videos -> score 44b6 videos, and the reverse (the hidden test is other embryos;
                this is the honest estimate of transfer)
    by VIDEO    GroupKFold(5) over videos (more training data per fold; optimistic)
Outputs: OOF probability per candidate (per scheme) saved to `b20_oof_<mode>.npz`, AP / AUC, precision@k, and
a threshold sweep on the OOF scores giving, per threshold, the number of accepted candidates and their precision
- the threshold is then passed to pass 2 as --min-score. Pass 2 uses the OOF scores through --scores-file so no
video is ever ranked by a model that saw it.

    python b20_train_ranker.py --mode steal [--tag exp29pp] [--neg-frac 0.05]
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(Path(__file__).resolve().parent))
import public_local as pl  # noqa: E402
import pass2_rank_divisions as p2  # noqa: E402
import divranker  # noqa: E402
VOX = p2.VOX


def build_tables(cache: Path, stems, parent_um, k, mode, neg_frac, rng):
    import networkx as nx
    from scipy.spatial import cKDTree
    X, Y, G, E, META = [], [], [], [], []
    for s in stems:
        nodes, edges, dcs, peak = p2.load_video(cache, s)
        cands, succ, pred = p2.candidates(nodes, edges, dcs, peak, parent_um, k, mode)
        if not cands:
            continue
        g = nx.DiGraph(); g.add_nodes_from((i, {"t": n["t"], "z": n["z"], "y": n["y"], "x": n["x"]}) for i, n in nodes.items()); g.add_edges_from((e[0], e[1]) for e in edges)
        y = divranker.label_candidates(g, p2.label(cands, s), [(p, c, q, f) for p, c, q, t, f in cands])
        F = np.array([f for *_, f in cands], float)
        keep = y.astype(bool).copy()
        if y.sum():
            qpos = np.stack([np.array([nodes[q]["z"], nodes[q]["y"], nodes[q]["x"]]) * VOX for (p, c, q, t, f), yy in zip(cands, y) if yy])
            tree = cKDTree(qpos)
            qall = np.stack([np.array([nodes[q]["z"], nodes[q]["y"], nodes[q]["x"]]) * VOX for p, c, q, t, f in cands])
            d, _ = tree.query(qall); keep |= d <= 5.0
        keep |= rng.random(len(y)) < neg_frac
        X.append(F[keep]); Y.append(y[keep]); G += [s] * int(keep.sum()); E += [s.split("_")[0]] * int(keep.sum())
        META += [(s, p, c, q) for (p, c, q, t, f), kk in zip(cands, keep) if kk]
        print(f"  {s}: {len(cands)} cands -> kept {int(keep.sum())}, positives {int(y.sum())}", flush=True)
    return np.nan_to_num(np.concatenate(X), nan=-1.0), np.concatenate(Y), np.array(G), np.array(E), META


def cv_oof(X, Y, groups, folds):
    from sklearn.ensemble import HistGradientBoostingClassifier
    oof = np.full(len(Y), np.nan)
    for tr, te in folds:
        if Y[tr].sum() == 0:
            continue
        clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_depth=4, class_weight="balanced", random_state=0)
        clf.fit(X[tr], Y[tr]); oof[te] = clf.predict_proba(X[te])[:, 1]
    return oof


def report(name, Y, oof):
    from sklearn.metrics import average_precision_score, roc_auc_score
    m = ~np.isnan(oof)
    if m.sum() == 0 or Y[m].sum() == 0:
        print(f"{name}: no scored positives"); return
    ap = average_precision_score(Y[m], oof[m]); auc = roc_auc_score(Y[m], oof[m])
    order = np.argsort(-oof[m]); y = Y[m][order]
    pk = " ".join(f"P@{k}={y[:k].mean():.2f}" for k in (10, 25, 50, 100, 200) if k <= len(y))
    print(f"{name}: n={m.sum()} pos={int(Y[m].sum())} AP={ap:.3f} AUC={auc:.3f} | {pk}")
    print(f"  threshold sweep (accepted / precision / recall):")
    for thr in (0.5, 0.7, 0.8, 0.9, 0.95, 0.98):
        acc = oof[m] >= thr
        print(f"    >= {thr:.2f}: {int(acc.sum()):6d} / {Y[m][acc].mean() if acc.sum() else 0:.3f} / {Y[m][acc].sum() / Y[m].sum():.2f}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", default="exp29pp"); ap.add_argument("--mode", choices=["add", "steal"], default="steal")
    ap.add_argument("--parent-um", type=float, default=9.0); ap.add_argument("--k", type=int, default=3); ap.add_argument("--neg-frac", type=float, default=0.05)
    ap.add_argument("--stems", nargs="*", default=[]); a = ap.parse_args()
    cache = pl.DEFAULT_CACHE / a.tag
    stems = a.stems or sorted(p.stem for p in (cache / "ckpt").glob("*.npz") if (cache / "dc" / p.name).is_file() and (cache / "raw" / f"{p.stem}.geff").is_dir())
    rng = np.random.default_rng(0); t0 = time.time()
    X, Y, G, E, META = build_tables(cache, stems, a.parent_um, a.k, a.mode, a.neg_frac, rng)
    print(f"\n{len(stems)} videos ({sorted(set(E))}) | rows {len(Y)} | positives {int(Y.sum())} | build {time.time()-t0:.0f}s")
    from sklearn.model_selection import GroupKFold
    out = {"videos": stems, "mode": a.mode, "n_rows": int(len(Y)), "n_pos": int(Y.sum()), "names": p2.NAMES}
    # by embryo
    embs = sorted(set(E))
    if len(embs) >= 2:
        folds = [(np.where(E != e)[0], np.where(E == e)[0]) for e in embs]
        oof_e = cv_oof(X, Y, E, folds); report("LOO by EMBRYO", Y, oof_e); out["oof_embryo"] = oof_e.tolist()
    else:
        oof_e = None; print("only one embryo present - by-embryo CV not possible yet")
    folds = list(GroupKFold(n_splits=min(5, len(set(G)))).split(X, Y, G))
    oof_v = cv_oof(X, Y, G, folds); report("GroupKFold by VIDEO", Y, oof_v); out["oof_video"] = oof_v.tolist()
    np.savez_compressed(Path(__file__).resolve().parent / "results" / f"b20_oof_{a.mode}.npz",
                        stem=np.array([m[0] for m in META]), p=np.array([m[1] for m in META]), c=np.array([m[2] for m in META]),
                        q=np.array([m[3] for m in META]), y=Y, oof_video=oof_v, oof_embryo=(oof_e if oof_e is not None else np.full(len(Y), np.nan)))
    (Path(__file__).resolve().parent / "results" / f"b20_train_{a.mode}.json").write_text(json.dumps({k: v for k, v in out.items() if not k.startswith("oof")}, indent=2))
    print("wrote results/b20_oof_%s.npz" % a.mode)


if __name__ == "__main__":
    main()
