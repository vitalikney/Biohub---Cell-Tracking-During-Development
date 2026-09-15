"""B20 pass 2: the division stage with a learned ranker, run on the pass-1 checkpoints - no frames needed.

Per video: load ckpt/<stem>.npz (the graph the shipped division stage sees), dc/<stem>.npz (DeepCenter score per
raw node, 8-view TTA) and the raw graph (peak_prob). Enumerate candidates on the checkpoint graph:
    parent p with exactly one child c at t+1, candidate daughter q at t+1 within --parent-um of p,
    q != c, q not synthetic;  mode 'add': q must have no predecessor (the shipped pool)
                              mode 'steal': q may have a predecessor; accepting removes that edge
Score with a ranker trained on OTHER videos (leave-one-video-out over the videos given), accept in descending
score under the shipped caps (frame 0.0076 x sources, global 0.00375 x edges) and the shipped DeepCenter veto
(threshold 0.20 on the daughter's cached score), then run the shipped tail (prune-isolated, short-track filter,
linefit) through the notebook's own functions, write the graph and score it with the official metric.
'--ranker public' reproduces the shipped ranking (parent_dist + 0.15*sister_dist ascending, with the shipped
mutual-NN / divergence / symmetry gates) as the control.

    python pass2_rank_divisions.py --tag exp29pp --ranker public|gbm --mode add|steal [--stems ...]
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(Path(__file__).resolve().parent))
VOX = np.array([1.625, 0.40625, 0.40625])
FRAME_CAP, GLOBAL_CAP, EXIST_CHILD_MAX, SISTER_MAX, DC_THR = 0.0076, 0.00375, 10.0, 14.0, 0.20
NAMES = ["d_pc", "d_pq", "d_cq", "asym", "cos", "div_next", "len_p_back", "len_c_fwd", "len_q_fwd", "z_um",
         "peak_p", "peak_c", "peak_q", "dc_q", "dc_c", "q_claimed", "q_in_prob", "q_pred_peak", "q_pred_backlen"]


def load_video(cache: Path, stem: str):
    ck = np.load(cache / "ckpt" / f"{stem}.npz"); dc = np.load(cache / "dc" / f"{stem}.npz")
    nodes = {int(i): {"t": int(r[0]), "z": float(r[1]), "y": float(r[2]), "x": float(r[3]), "syn": int(r[4])} for i, r in zip(ck["node_id"], ck["tzyx_syn"])}
    edges = [(int(s), int(d), (None if np.isnan(p) else float(p))) for s, d, p in zip(ck["src"], ck["dst"], ck["edge_prob"])]
    dcs = {int(i): float(v) for i, v in zip(dc["node_id"], dc["dc"])}
    import tracksdata as td
    g = td.graph.IndexedRXGraph.from_geff(cache / "raw" / f"{stem}.geff"); g = g[0] if isinstance(g, tuple) else g
    na = g.node_attrs(); peak = {int(i): float(p) for i, p in zip(na["node_id"].to_numpy(), na["peak_prob"].to_numpy())} if "peak_prob" in na.columns else {}
    return nodes, edges, dcs, peak


def candidates(nodes, edges, dcs, peak, parent_um, k, mode):
    succ, pred, eprob = {}, {}, {}
    for s, d, p in edges:
        succ.setdefault(s, []).append(d); pred.setdefault(d, []).append(s); eprob[(s, d)] = p
    pos = {i: np.array([n["z"], n["y"], n["x"]]) * VOX for i, n in nodes.items()}
    by_t = {}
    for i, n in nodes.items(): by_t.setdefault(n["t"], []).append(i)
    def back_len(n, cap=30):
        k_ = 0
        while len(pred.get(n, [])) == 1 and k_ < cap: n = pred[n][0]; k_ += 1
        return k_
    def fwd_len(n, cap=30):
        k_ = 0
        while len(succ.get(n, [])) == 1 and k_ < cap: n = succ[n][0]; k_ += 1
        return k_
    out = []
    for t in sorted(by_t):
        nxt = [q for q in by_t.get(t + 1, []) if not nodes[q]["syn"] and (mode == "steal" or not pred.get(q))]
        if not nxt: continue
        tree = cKDTree(np.stack([pos[q] for q in nxt]))
        srcs = [p for p in by_t[t] if len(succ.get(p, [])) == 1]
        for p in srcs:
            c = succ[p][0]
            if nodes[c]["t"] != t + 1: continue
            d_pc = float(np.linalg.norm(pos[c] - pos[p]))
            if d_pc > EXIST_CHILD_MAX: continue
            d, i = tree.query(pos[p], k=min(k + 1, len(nxt)), distance_upper_bound=parent_um)
            for dd, ii in zip(np.atleast_1d(d), np.atleast_1d(i)):
                if not np.isfinite(dd) or ii >= len(nxt): continue
                q = nxt[ii]
                if q == c: continue
                d_pq = float(dd); d_cq = float(np.linalg.norm(pos[c] - pos[q]))
                if d_cq > SISTER_MAX: continue
                asym = abs(d_pc - d_pq) / max((d_pc + d_pq) / 2, 1e-6)
                cos = float(np.dot(pos[c] - pos[p], pos[q] - pos[p]) / max(d_pc * d_pq, 1e-6))
                cs, qs = succ.get(c, []), succ.get(q, [])
                div_next = float(np.linalg.norm(pos[cs[0]] - pos[qs[0]]) - d_cq) if len(cs) == 1 and len(qs) == 1 else -1.0
                pr = pred.get(q, [])
                if pr:
                    r = pr[0]; st = [1.0, float(eprob.get((r, q)) or 0.0), peak.get(r, -1.0), float(back_len(r))]
                else:
                    st = [0.0, -1.0, -1.0, -1.0]
                f = [d_pc, d_pq, d_cq, asym, cos, div_next, float(back_len(p)), float(fwd_len(c)), float(fwd_len(q)), float(pos[p][0]),
                     peak.get(p, -1.0), peak.get(c, -1.0), peak.get(q, -1.0), dcs.get(q, -1.0), dcs.get(c, -1.0)] + st
                out.append((p, c, q, t, f))
    return out, succ, pred


def label(cands, stem):
    import divranker, networkx as nx
    gt = divranker._load_gt(ROOT / "biohub-cell-tracking-during-development" / "train" / f"{stem}.geff")
    return gt


def public_key(f):  # shipped ranking, lower is better; shipped gates as hard filters
    d_pc, d_pq, d_cq, asym, cos, div_next = f[:6]
    if asym > 0.6: return None                       # symmetry tau 0.6
    if div_next < 2.25: return None                  # divergence >= 2.25 um (requires grandchildren)
    return d_pq + 0.15 * d_cq


def apply(nodes, edges, cands, scores, succ, pred, mode, min_score=-np.inf):
    """Accept candidates in score order under the shipped caps and veto; returns new edge list."""
    n_src_by_t = {}
    for p, c, q, t, f in cands: n_src_by_t[t] = n_src_by_t.get(t, 0) + 1
    edges = list(edges); eset = {(s, d) for s, d, _ in edges}
    used_src, used_tgt, per_frame, added = set(), set(), {}, 0
    global_cap = max(1, int(round(len(edges) * GLOBAL_CAP)))
    order = sorted(range(len(cands)), key=lambda i: -scores[i])
    for i in order:
        if scores[i] == -np.inf or scores[i] < min_score: continue   # a learned ranker needs a threshold, not just the caps
        p, c, q, t, f = cands[i]
        if added >= global_cap: break
        cap = max(1, int(round(n_src_by_t.get(t, 1) * FRAME_CAP)))
        if per_frame.get(t, 0) >= cap or p in used_src or q in used_tgt: continue
        if f[NAMES.index("dc_q")] < DC_THR: continue                    # shipped DeepCenter veto on the daughter
        if mode == "add" and pred.get(q): continue
        if mode == "steal" and pred.get(q):
            r = pred[q][0]; edges = [e for e in edges if not (e[0] == r and e[1] == q)]; eset.discard((r, q))
        edges.append((p, q, None)); eset.add((p, q)); used_src.add(p); used_tgt.add(q); per_frame[t] = per_frame.get(t, 0) + 1; added += 1
    return edges, added


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", default="exp29pp"); ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--ranker", choices=["public", "gbm"], default="public"); ap.add_argument("--mode", choices=["add", "steal"], default="add")
    ap.add_argument("--parent-um", type=float, default=9.0); ap.add_argument("--k", type=int, default=3); ap.add_argument("--label", default=None)
    ap.add_argument("--min-score", type=float, default=None, help="gbm only: accept a candidate only if its OOF probability >= this (default: caps only)")
    a = ap.parse_args()
    import public_local as pl, divranker, postproc, networkx as nx
    cache = pl.DEFAULT_CACHE / a.tag
    stems = a.stems or sorted(p.stem for p in (cache / "ckpt").glob("*.npz"))
    label_ = a.label or f"p2_{a.ranker}_{a.mode}" + (f"_t{a.min_score:g}" if (a.ranker == "gbm" and a.min_score is not None) else "")
    out_dir = cache / "pp" / label_; out_dir.mkdir(parents=True, exist_ok=True)
    # notebook tail (prune-isolated, short-track, linefit) through the real functions
    os.environ["BIOHUB_OUTPUT_SAFE_DIVISIONS"] = "0"; os.environ["BIOHUB_OUTPUT_MOTION_RELINK"] = "0"; os.environ["BIOHUB_OUTPUT_GAP_CLOSE"] = "0"; os.environ["BIOHUB_OUTPUT_GAP2_RECOVERY"] = "0"
    os.environ["BIOHUB_USE_DEEPCENTER_VETO"] = "0"; os.environ["BIOHUB_REQUIRE_DEEPCENTER_VETO"] = "0"
    cells = pl.notebook_cells(pl.DEFAULT_NOTEBOOK); work = cache / "work"; work.mkdir(exist_ok=True)
    repo, _ = pl.materialise_repo(Path(pl.DEFAULT_WEIGHTS_ROOT), work, None, None, materialise_code=False)
    ns = pl.build_namespace(cells, repo, work, pl.DEFAULT_DATA); pl.load_postproc(cells, ns); fog = ns["filter_output_graph"]

    data = {s: load_video(cache, s) for s in stems}
    C = {s: candidates(*data[s][:4], a.parent_um, a.k, a.mode) for s in stems}
    Y = {}
    for s in stems:
        cands, succ, pred = C[s]
        g = nx.DiGraph(); g.add_nodes_from((i, {"t": n["t"], "z": n["z"], "y": n["y"], "x": n["x"]}) for i, n in data[s][0].items()); g.add_edges_from((e[0], e[1]) for e in data[s][1])
        Y[s] = divranker.label_candidates(g, label(cands, s), [(p, c, q, f) for p, c, q, t, f in cands])
    tot = sum(len(C[s][0]) for s in stems); pos = sum(int(Y[s].sum()) for s in stems)
    print(f"{len(stems)} videos | mode {a.mode} | candidates {tot} | positives {pos}", flush=True)
    rows = []
    for s in stems:
        cands, succ, pred = C[s]; nodes, edges, dcs, peak = data[s]
        F = np.array([f for *_, f in cands], float) if cands else np.zeros((0, len(NAMES)))
        if a.ranker == "public" or not cands:
            sc = np.array([(-k if (k := public_key(f)) is not None else -np.inf) for *_, f in cands]) if cands else np.zeros(0)
        else:
            from sklearn.ensemble import HistGradientBoostingClassifier
            Xtr = np.concatenate([np.array([f for *_, f in C[o][0]], float) for o in stems if o != s and C[o][0]])
            ytr = np.concatenate([Y[o] for o in stems if o != s and C[o][0]])
            if ytr.sum() == 0: sc = np.array([(-k if (k := public_key(f)) is not None else -np.inf) for *_, f in cands])
            else:
                clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_depth=4, class_weight="balanced", random_state=0).fit(np.nan_to_num(Xtr, nan=-1), ytr)
                sc = clf.predict_proba(np.nan_to_num(F, nan=-1))[:, 1]
        thr = (a.min_score if (a.ranker == "gbm" and a.min_score is not None) else -np.inf)
        new_edges, added = apply(nodes, edges, cands, sc, succ, pred, a.mode, min_score=thr)
        nb = {i: {"node_id": i, "t": n["t"], "z": n["z"], "y": n["y"], "x": n["x"], **({"gap_synthetic": 1} if n["syn"] else {})} for i, n in nodes.items()}
        eb = [{"source_id": s_, "target_id": d_, "edge_prob": p_} for s_, d_, p_ in new_edges]
        nb, eb, stats = fog(nb, eb, dataset=s, deepcenter_bundle=None)
        g = nx.DiGraph()
        for i, n in nb.items(): g.add_node(int(i), t=int(n["t"]), z=float(max(0, round(n["z"]))), y=float(max(0, round(n["y"]))), x=float(max(0, round(n["x"]))))
        for e in eb: g.add_edge(int(e["source_id"]), int(e["target_id"]))
        postproc.save(g, out_dir / f"{s}.geff")
        rows.append((s, len(cands), int(Y[s].sum()), added))
        print(f"  {s}: {len(cands)} cands, {int(Y[s].sum())} pos, added {added}", flush=True)
    summary, mrows = pl.score_dir(out_dir, pl.DEFAULT_DATA)
    print(f"\n== {a.tag}/{label_}  score={summary['score']:.4f} adj_edge={summary['adj_edge_jaccard']:.4f} edge={summary['edge_jaccard']:.4f} "
          f"div={summary['division_jaccard']:.4f} ({int(summary['division_tp'])}/{int(summary['division_fp'])}/{int(summary['division_fn'])}) n={len(stems)}")
    (cache / "pp" / f"{label_}.json").write_text(json.dumps({"tag": a.tag, "label": label_, "ranker": a.ranker, "mode": a.mode, "videos": stems,
                                                              "summary": summary, "metric_rows": mrows, "per_video": [{"dataset": r[0], "cands": r[1], "pos": r[2], "added": r[3]} for r in rows]}, indent=2))


if __name__ == "__main__":
    main()
