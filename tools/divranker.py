"""Division ranker: enumerate candidate forks on prediction graphs, label them with GT divisions, train a classifier.

Candidate = parent p (out-degree 1, child c at t+1) + orphan track start q at t+1 within `parent_um` of p.
Label = 1 if p matches (7 um) a GT node that has >= 2 children and c, q match (7 um) its two children (either order).
Features: geometry (p-c, p-q, c-q distances in um, angle, asymmetry), motion (p velocity, q/c next-step displacement,
grandchild divergence), track context (length of p's track, length of q's and c's forward tracklets), z position.

Usage:
  from tools.divranker import build_dataset, fit_and_eval
  X, y, meta = build_dataset(geff_dir, gt_dir)
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import networkx as nx
import zarr
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import postproc  # noqa: E402

VOX = postproc.VOXEL
FEATURE_NAMES = ["d_pc", "d_pq", "d_cq", "asym", "cos_pc_pq", "speed_p", "len_p_back", "len_c_fwd", "len_q_fwd",
                 "div_next", "d_pq_rank", "n_starts_near", "z_um", "t_frac", "vel_align_q"]


def _load_gt(gt_path: Path):
    z = zarr.open_group(gt_path, mode="r")
    ids = z["nodes/ids"][:]
    t = z["nodes/props/t/values"][:]; zz = z["nodes/props/z/values"][:]; y = z["nodes/props/y/values"][:]; x = z["nodes/props/x/values"][:]
    e = z["edges/ids"][:]
    g = nx.DiGraph()
    for i, n in enumerate(ids):
        g.add_node(int(n), t=int(t[i]), z=float(zz[i]), y=float(y[i]), x=float(x[i]))
    g.add_edges_from((int(a), int(b)) for a, b in e)
    return g


def _match_pred_to_gt(pg: nx.DiGraph, gt: nx.DiGraph, radius: float = 7.0) -> dict:
    """Per-frame one-to-one (greedy nearest) matching of predicted nodes to GT nodes within radius (um)."""
    out = {}
    gt_by_t: dict[int, list] = {}
    for n, d in gt.nodes(data=True):
        gt_by_t.setdefault(d["t"], []).append(n)
    pr_by_t: dict[int, list] = {}
    for n, d in pg.nodes(data=True):
        pr_by_t.setdefault(int(d["t"]), []).append(n)
    for t, gns in gt_by_t.items():
        pns = pr_by_t.get(t, [])
        if not pns:
            continue
        gp = np.stack([postproc._pos(gt.nodes[n]) for n in gns]); pp = np.stack([postproc._pos(pg.nodes[n]) for n in pns])
        d = np.linalg.norm(gp[:, None, :] - pp[None, :, :], axis=-1)
        used_g, used_p = set(), set()
        for gi, pi in zip(*np.unravel_index(np.argsort(d, axis=None), d.shape)):
            if d[gi, pi] > radius:
                break
            if gi in used_g or pi in used_p:
                continue
            used_g.add(gi); used_p.add(pi); out[pns[pi]] = gns[gi]
    return out


def _fwd_len(g: nx.DiGraph, n, cap: int = 30) -> int:
    k = 0; cur = n
    while k < cap:
        s = list(g.successors(cur))
        if len(s) != 1:
            break
        cur = s[0]; k += 1
    return k


def _back_len(g: nx.DiGraph, n, cap: int = 30) -> int:
    k = 0; cur = n
    while k < cap:
        p = list(g.predecessors(cur))
        if len(p) != 1:
            break
        cur = p[0]; k += 1
    return k


def candidates(g: nx.DiGraph, parent_um: float = 8.0, k_starts: int = 3, T: int = 100):
    """Yield (p, c, q, features) for every parent p with one child and up to k_starts nearest orphan starts q."""
    starts: dict[int, list] = {}; parents: dict[int, list] = {}
    for n, d in g.nodes(data=True):
        t = int(d["t"])
        if g.in_degree(n) == 0 and g.out_degree(n) >= 1:
            starts.setdefault(t, []).append(n)
        if g.out_degree(n) == 1:
            parents.setdefault(t, []).append(n)
    for t, p_nodes in sorted(parents.items()):
        s_nodes = starts.get(t + 1, [])
        if not s_nodes:
            continue
        sp = np.stack([postproc._pos(g.nodes[n]) for n in s_nodes]); ts = cKDTree(sp)
        pp = np.stack([postproc._pos(g.nodes[n]) for n in p_nodes])
        dists, idxs = ts.query(pp, k=min(k_starts, len(s_nodes)), distance_upper_bound=parent_um)
        dists = np.asarray(dists).reshape(len(p_nodes), -1); idxs = np.asarray(idxs).reshape(len(p_nodes), -1)
        for pi, p in enumerate(p_nodes):
            c = next(iter(g.successors(p)))
            P, C = postproc._pos(g.nodes[p]), postproc._pos(g.nodes[c])
            vp = postproc._velocity(g, p)
            n_near = int(np.isfinite(dists[pi]).sum())
            for rank, (dist, si) in enumerate(zip(dists[pi], idxs[pi])):
                if not np.isfinite(dist) or si >= len(s_nodes):
                    continue
                q = s_nodes[si]; Q = postproc._pos(g.nodes[q])
                d_pc = float(np.linalg.norm(C - P)); d_pq = float(dist); d_cq = float(np.linalg.norm(C - Q))
                asym = abs(d_pc - d_pq) / max(d_pc + d_pq, 1e-6)
                cos = float(np.dot(C - P, Q - P) / max(np.linalg.norm(C - P) * np.linalg.norm(Q - P), 1e-6))
                # forward divergence of grandchildren
                cs = list(g.successors(c)); qs = list(g.successors(q))
                div_next = -1.0
                if len(cs) == 1 and len(qs) == 1:
                    div_next = float(np.linalg.norm(postproc._pos(g.nodes[cs[0]]) - postproc._pos(g.nodes[qs[0]])) - d_cq)
                vq = postproc._pos(g.nodes[qs[0]]) - Q if len(qs) == 1 else np.zeros(3)
                vel_align = float(np.dot(vq, Q - P) / max(np.linalg.norm(vq) * np.linalg.norm(Q - P), 1e-6))
                feats = [d_pc, d_pq, d_cq, asym, cos, float(np.linalg.norm(vp)), _back_len(g, p), _fwd_len(g, c), _fwd_len(g, q),
                         div_next, rank, n_near, float(P[0]), t / T, vel_align]
                yield p, c, q, feats


def label_candidates(g: nx.DiGraph, gt: nx.DiGraph, cands: list) -> np.ndarray:
    m = _match_pred_to_gt(g, gt)
    gt_children = {n: set(gt.successors(n)) for n in gt.nodes if gt.out_degree(n) >= 2}
    y = np.zeros(len(cands), dtype=int)
    for i, (p, c, q, _) in enumerate(cands):
        gp = m.get(p)
        if gp is None or gp not in gt_children:
            continue
        ch = gt_children[gp]
        if m.get(c) in ch and m.get(q) in ch and m.get(c) != m.get(q):
            y[i] = 1
    return y


def build_dataset(geff_dir: Path, gt_dir: Path, parent_um: float = 8.0):
    X, Y, meta = [], [], []
    n_gt_div = 0
    for p in sorted(Path(geff_dir).glob("*.geff")):
        g = postproc.load(p)
        gt = _load_gt(Path(gt_dir) / p.name)
        n_gt_div += sum(1 for n in gt.nodes if gt.out_degree(n) >= 2)
        cands = list(candidates(g, parent_um=parent_um))
        y = label_candidates(g, gt, cands)
        for (pp, c, q, f), yy in zip(cands, y):
            X.append(f); Y.append(yy); meta.append((p.stem, pp, c, q))
    return np.array(X, float), np.array(Y, int), meta, n_gt_div


def fit_and_eval(X, y, groups, seed: int = 0):
    """Grouped CV (by video) with gradient boosting; returns per-fold AP and the fitted model on all data."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.metrics import average_precision_score
    from sklearn.model_selection import GroupKFold
    aps = []
    oof = np.zeros(len(y))
    for tr, te in GroupKFold(n_splits=min(5, len(set(groups)))).split(X, y, groups):
        clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_depth=4, class_weight="balanced", random_state=seed)
        clf.fit(X[tr], y[tr]); pr = clf.predict_proba(X[te])[:, 1]; oof[te] = pr
        if y[te].sum() > 0:
            aps.append(average_precision_score(y[te], pr))
    clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_depth=4, class_weight="balanced", random_state=seed)
    clf.fit(X, y)
    return clf, oof, aps
