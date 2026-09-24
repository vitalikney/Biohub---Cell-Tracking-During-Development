"""Edge anatomy of the FINAL exp39 graph: which classes of predicted edges are wrong, and would dropping them pay?

WHAT IT DOES (per video, 4 workers max)
    final graph   the replay's cached post-tail graph of the exp39 base (tail/<base_key>/<stem>.npz under the replay
                  --out dir; exactly what replay.py writes as the exp39 GEFF: post-linefit, pre-insertion). The base key is
                  recomputed with replay.py's own functions, so a changed tail source gives a clear "run the replay" error.
    labels        the graph is written with replay.write_geff (write_test_submission rounding) and scored by the OFFICIAL
                  code (tools/official tracking_cellmot.metrics.evaluate: 7 um timepoint-aware optimal assignment); the
                  per-edge frame is metrics._evaluate_matched_graph on the matched graph, i.e. the very rows the metric
                  counts: TP = matched_edge_mask, FP = pred_valid & ~matched (source matches a GT node with a GT
                  successor OR target matches a GT node with a GT predecessor), NE = everything else, incl. edges the
                  metric discards before counting (merge duplicates, out-degree cap; reason in `ne_reason`).
                  VALIDATION: per-video TP/FP must equal the metric's edge_tp/edge_fp and the replay's per-video csv
                  (exp39 rows); the script stops if any video differs.
    origin        motion relink REPLACES all ILP edges in the exp29 tail, so every ckpt edge with a probability is a
                  relink edge: edge_prob > 0 = the pair was also an ILP (raw/) edge, edge_prob == 0 = pair the network
                  never scored. The relink pass (tight <= 6 um / relaxed <= 10 um) and its motion residual are not in the
                  ckpt: the notebook's own motion_relink_edges is re-run on raw/<stem>.geff (validated per video: same
                  edge set, same probabilities, same tight/relaxed counts as the ckpt's stored stats). Edges without a
                  probability are gap edges: gap1 (touches a gap_synthetic node), gap2 (touches a recover_strict_gap2
                  node), gap1_reuse (single-frame gap through a reused isolated raw node). Final edges absent from the ckpt
                  are safe divisions (divnet_rerank). Short-track rescue: edge in a final component smaller than
                  OUTPUT_MIN_TRACK_LEN without a fork (the only way such a component survives the short-track filter).
    features      edge_prob, length (final float coords, um; scale z 1.625, y/x 0.40625), pre-linefit length, relink
                  motion residual, constant-velocity residual in the final graph, local density (nodes within 10 um in
                  the source / target frame), nearest competing target, endpoint topology (start / end / leaf / fork),
                  segment and component length, ILP (dis)agreement and re-link alternatives (ILP successor of the source
                  that is a track start in the final graph, ILP predecessor of the target that is a track end), and the
                  official label the alternative edge would get.
    estimates     per class, the score change of DROPPING its edges (per-video counts: TP -> FN, FP removed, node count
                  unchanged, division counts unchanged; exact official summarise() over the per-video rows), and of
                  RE-LINKING (drop + add the ILP alternative, labelled by the same matching). The division term is held
                  fixed: classes that contain fork edges say so (the replay run in step B is exact).

OUTPUTS
    <out>/relink/<stem>.npz, <out>/match/<stem>.npz     per-video caches (relink rerun ~50 s, official match ~3 s)
    <out>/edges_<tag>.parquet                             every final edge: labels + features (git-ignored)
    experiments/l2_daughternet/edge_anatomy/anatomy_<tag>.{md,json}, classes_<tag>.csv   summary tables

USAGE
    python experiments/l2_daughternet/edge_anatomy/anatomy.py --workers 4
    python experiments/l2_daughternet/edge_anatomy/anatomy.py --stems 44b6_0b24845f --workers 1     (smoke)
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import shutil
import sys
import time
import warnings
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPLAY_DIR = ROOT / "experiments" / "l2_daughternet" / "replay"
if str(REPLAY_DIR) not in sys.path:
    sys.path.insert(0, str(REPLAY_DIR))

import replay as R  # noqa: E402  (tail I/O, GEFF writer, notebook namespace, scorer import - one code path)

DEFAULT_CACHE = ROOT / "data_external" / "friend_a_cache" / "friend_a_b20_exp29_friend_c" / "cache" / "friend_a_b20_exp29"
DEFAULT_REPLAY_OUT = ROOT / ".public_local_cache" / "l2_replay" / "friend_a_b20_exp29"
DEFAULT_OUT = ROOT / ".public_local_cache" / "l2_edge_anatomy"
SCALE_UM = np.asarray([1.625, 0.40625, 0.40625], dtype=np.float64)
DENSITY_UM = 10.0
MATCH_VERSION = 1
RELINK_VERSION = 1


# ------------------------------------------------------------------------------------------------ base / tail location
def tail_dir_for(spec: str, replay_out: Path) -> tuple[Path, dict]:
    """tail/<base_key> of a replay config spec, with replay.py's own key recipe (so a stale tail is never read)."""
    name, raw = R.parse_config_spec(spec)
    cfg = R.resolve_config(name, raw, {name: raw})
    base = R.base_params(cfg)
    key = f"{cfg['safe_div']}_" + R._fingerprint({
        "base": base, "notebook_sha": R._sha256_file(R.pl.DEFAULT_NOTEBOOK), "tail_version": R.TAIL_VERSION,
        "tail_sources_sha": {p.name: R._sha256_file(p) for p in R.TAIL_SOURCES}})[:12]
    return replay_out / "tail" / key, cfg


# ------------------------------------------------------------------------------------------------ worker context
_W: dict = {}


def init_worker(settings: dict) -> None:
    if _W.get("settings") == settings:
        return
    R.init_context({"cache": settings["cache"], "data_dir": settings["data_dir"], "out": settings["ns_out"],
                    "need_insert": False})
    import tracksdata as td
    from tracking_cellmot import metrics as M

    _W.clear()
    _W.update(settings=settings, ns=R._CTX["namespace"], scorer=R._CTX["scorer"], td=td, M=M)


# ------------------------------------------------------------------------------------------------ relink rerun
def relink_rerun(stem: str, cache: Path, out: Path) -> dict:
    """The notebook's motion_relink_edges on raw/<stem>.geff, preceded by filter_output_graph's own edge filter and
    learned-probability map (verbatim logic); validated against the ckpt. Cached."""
    path = out / "relink" / f"{stem}.npz"
    if path.is_file():
        with np.load(path, allow_pickle=False) as z:
            if int(z["version"]) == RELINK_VERSION:
                return {k: z[k] for k in z.files}
    ns = _W["ns"]
    graph = R.fc._load_raw_graph(cache / "raw" / f"{stem}.geff")
    na, ea = graph.node_attrs(), graph.edge_attrs()
    nodes = {int(i): {"node_id": int(i), "t": int(t), "z": float(z), "y": float(y), "x": float(x)}
             for i, t, z, y, x in zip(na["node_id"].to_list(), na["t"].to_list(), na["z"].to_list(),
                                      na["y"].to_list(), na["x"].to_list())}
    raw_src = np.asarray(ea["source_id"].to_list(), dtype=np.int64)
    raw_dst = np.asarray(ea["target_id"].to_list(), dtype=np.int64)
    raw_p = np.asarray(ea["edge_prob"].to_list(), dtype=np.float64)
    edges = []
    for s, d, p in zip(raw_src.tolist(), raw_dst.tolist(), raw_p.tolist()):
        a, b = nodes.get(s), nodes.get(d)
        if a is None or b is None:
            continue
        if ns["OUTPUT_ENFORCE_NEXT_FRAME"] and int(b["t"]) != int(a["t"]) + 1:
            continue
        if ns["OUTPUT_EDGE_MAX_UM"] > 0 and ns["edge_distance_um"](a, b) > ns["OUTPUT_EDGE_MAX_UM"]:
            continue
        edges.append((s, d, p))
    learned: dict[tuple[int, int], float] = {}
    for s, d, p in edges:
        if p is not None and np.isfinite(p):
            learned[(s, d)] = max(learned.get((s, d), float("-inf")), float(p))
    stats = {k: 0 for k in ("motion_relink_edges", "motion_relink_tight_edges", "motion_relink_relaxed_edges",
                            "motion_relink_frames", "motion_relink_skipped_large_frame")}
    old = ns["OUTPUT_MOTION_RELINK"]
    ns["OUTPUT_MOTION_RELINK"] = True
    try:
        rel = ns["motion_relink_edges"](nodes, stats, learned)
    finally:
        ns["OUTPUT_MOTION_RELINK"] = old
    fallback = not rel
    if fallback:  # notebook falls back to the raw (filtered) edges
        rel = [{"source_id": s, "target_id": d, "edge_prob": p, "distance_um": np.nan, "motion_distance_um": np.nan,
                "motion_pass": "raw"} for s, d, p in edges]
    # validation against the ckpt (edges with a probability = relink output; counters stored by the notebook)
    with np.load(cache / "ckpt" / f"{stem}.npz", allow_pickle=False) as ck:
        cp = np.asarray(ck["edge_prob"], dtype=np.float64)
        keep = ~np.isnan(cp)
        ck_edges = {(int(s), int(d)): float(p) for s, d, p in zip(ck["src"][keep], ck["dst"][keep], cp[keep])}
        ck_stats = json.loads(str(ck["stats"]))
    ours = {(int(e["source_id"]), int(e["target_id"])): float(e["edge_prob"]) for e in rel}
    same_set = set(ours) == set(ck_edges)
    prob_bad = sum(1 for k in set(ours) & set(ck_edges) if abs(ours[k] - ck_edges[k]) > 1e-5)
    counts_ok = all(int(stats[k]) == int(ck_stats.get(k, -1)) for k in
                    ("motion_relink_edges", "motion_relink_tight_edges", "motion_relink_relaxed_edges"))
    arrays = {
        "version": np.asarray(RELINK_VERSION),
        "src": np.asarray([int(e["source_id"]) for e in rel], dtype=np.int64),
        "dst": np.asarray([int(e["target_id"]) for e in rel], dtype=np.int64),
        "prob": np.asarray([float(e["edge_prob"]) for e in rel], dtype=np.float64),
        "pass_code": np.asarray([{"tight": 0, "relaxed": 1}.get(str(e.get("motion_pass")), 2) for e in rel],
                                dtype=np.int8),
        "raw_um": np.asarray([float(e.get("distance_um", np.nan)) for e in rel], dtype=np.float64),
        "motion_um": np.asarray([float(e.get("motion_distance_um", np.nan)) for e in rel], dtype=np.float64),
        "ilp_src": raw_src, "ilp_dst": raw_dst, "ilp_p": raw_p,
        "valid": np.asarray(int(same_set and prob_bad == 0 and (counts_ok or fallback))),
        "check": np.asarray(json.dumps({"same_set": same_set, "prob_mismatch": prob_bad, "counts_ok": counts_ok,
                                        "fallback": fallback, "ours": stats,
                                        "ckpt": {k: ck_stats.get(k) for k in stats}})),
    }
    R._atomic_npz(path, **arrays)
    return arrays


# ------------------------------------------------------------------------------------------------ official match
def official_match(stem: str, nodes: dict, edges: list[dict], out: Path, tail_key: str) -> dict:
    """Write the final graph exactly like the replay, run the OFFICIAL evaluate, keep the per-edge frame. Cached."""
    path = out / "match" / tail_key / f"{stem}.npz"
    if path.is_file():
        with np.load(path, allow_pickle=False) as z:
            if int(z["version"]) == MATCH_VERSION:
                return {k: z[k] for k in z.files}
    td, M, scorer = _W["td"], _W["M"], _W["scorer"]
    work = out / "work" / str(os.getpid())
    geff = work / f"{stem}.geff"
    R.write_geff(geff, nodes, edges)
    gt_path = Path(str(scorer.DATA)) / f"{stem}.geff"
    gt, scale = scorer._load_gt_and_scale(gt_path)
    loaded = td.graph.IndexedRXGraph.from_geff(geff)
    pred = loaded[0] if isinstance(loaded, tuple) else loaded
    with warnings.catch_warnings(), contextlib.redirect_stdout(io.StringIO()):
        warnings.simplefilter("ignore")
        er = M.evaluate(pred, gt, scale=scale)
        frame = M._evaluate_matched_graph(pred, gt)
        rec = M.node_recall(pred, gt) if pred.num_edges() > 0 and pred.num_nodes() > 0 else 0.0
    row = M.per_sample_metrics(er, scorer._estimated_n_total(gt_path), rec)
    K = td.DEFAULT_ATTR_KEYS
    na = pred.node_attrs(attr_keys=[K.NODE_ID, K.MATCHED_NODE_ID])
    gea = gt.edge_attrs()
    arrays = {
        "version": np.asarray(MATCH_VERSION),
        "e_src": frame[K.EDGE_SOURCE].to_numpy().astype(np.int64),
        "e_dst": frame[K.EDGE_TARGET].to_numpy().astype(np.int64),
        "e_tp": frame[K.MATCHED_EDGE_MASK].to_numpy().astype(bool),
        "e_valid": frame["pred_valid"].to_numpy().astype(bool),
        "n_id": na[K.NODE_ID].to_numpy().astype(np.int64),
        "n_match": na[K.MATCHED_NODE_ID].fill_null(-1).to_numpy().astype(np.int64),
        "gt_src": gea[K.EDGE_SOURCE].to_numpy().astype(np.int64),
        "gt_dst": gea[K.EDGE_TARGET].to_numpy().astype(np.int64),
        "gt_nodes": np.asarray(gt.node_ids(), dtype=np.int64),
        "row": np.asarray(json.dumps({k: (v.item() if hasattr(v, "item") else v) for k, v in row.items()})),
    }
    shutil.rmtree(geff, ignore_errors=True)
    R._atomic_npz(path, **arrays)
    return arrays


# ------------------------------------------------------------------------------------------------ features
def _label_pair(a: int, b: int, match: dict, gt_edges: set, gt_out: dict, gt_in: dict) -> int:
    """Official label of a hypothetical edge a->b (0 NE, 1 TP, 2 FP) under the fixed node matching."""
    ga, gb = match.get(a, -1), match.get(b, -1)
    if ga != -1 and gb != -1 and (ga, gb) in gt_edges:
        return 1
    if (ga != -1 and gt_out.get(ga, 0) > 0) or (gb != -1 and gt_in.get(gb, 0) > 0):
        return 2
    return 0


def video_frame(stem: str, settings: dict) -> dict:
    init_worker(settings)
    started = time.time()
    cache, out, tail_dir = Path(settings["cache"]), Path(settings["out"]), Path(settings["tail_dir"])
    nodes, edges, tail_stats = R.load_tail(tail_dir / f"{stem}.npz")
    rel = relink_rerun(stem, cache, out)
    mt = official_match(stem, nodes, edges, out, tail_dir.name)
    ck_nodes, ck_edges, _dcs, _exp = R.load_ckpt(cache, stem)
    ns = _W["ns"]
    min_len = int(ns["OUTPUT_MIN_TRACK_LEN"])

    n_ids = np.asarray(sorted(nodes), dtype=np.int64)
    index = {int(i): k for k, i in enumerate(n_ids.tolist())}
    pos = np.asarray([[nodes[i]["z"], nodes[i]["y"], nodes[i]["x"]] for i in n_ids.tolist()], dtype=np.float64)
    pos_um = pos * SCALE_UM
    tt = np.asarray([int(nodes[i]["t"]) for i in n_ids.tolist()], dtype=np.int64)
    ck_pos_um = {i: np.asarray([n["z"], n["y"], n["x"]], dtype=np.float64) * SCALE_UM for i, n in ck_nodes.items()}

    src = np.asarray([int(e["source_id"]) for e in edges], dtype=np.int64)
    dst = np.asarray([int(e["target_id"]) for e in edges], dtype=np.int64)
    prob = np.asarray([np.nan if e.get("edge_prob") is None else float(e["edge_prob"]) for e in edges])
    dist_pre = np.asarray([float(e.get("distance_um", np.nan)) for e in edges])
    si = np.asarray([index[int(s)] for s in src.tolist()], dtype=np.int64)
    di = np.asarray([index[int(d)] for d in dst.tolist()], dtype=np.int64)
    n_e = len(edges)

    # ---- topology of the final graph
    indeg = np.bincount(di, minlength=len(n_ids))
    outdeg = np.bincount(si, minlength=len(n_ids))
    pred_of = np.full(len(n_ids), -1, dtype=np.int64)
    succ_of = np.full(len(n_ids), -1, dtype=np.int64)
    pred_of[di] = si  # meaningful only where indeg == 1
    for s_, d_ in zip(si.tolist(), di.tolist()):
        if outdeg[s_] == 1:
            succ_of[s_] = d_
    order = np.argsort(tt, kind="stable")
    up = np.zeros(len(n_ids), dtype=np.int64)    # edges of the linear chain above a node
    for k in order.tolist():
        if indeg[k] == 1 and outdeg[pred_of[k]] == 1:
            up[k] = up[pred_of[k]] + 1
    down = np.zeros(len(n_ids), dtype=np.int64)  # edges of the linear chain below a node
    for k in order[::-1].tolist():
        if outdeg[k] == 1 and indeg[succ_of[k]] == 1:
            down[k] = down[succ_of[k]] + 1
    parent = np.arange(len(n_ids))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for s_, d_ in zip(si.tolist(), di.tolist()):
        ra, rb = find(s_), find(d_)
        if ra != rb:
            parent[ra] = rb
    roots = np.asarray([find(k) for k in range(len(n_ids))], dtype=np.int64)
    comp_size = np.bincount(roots, minlength=len(n_ids))
    comp_tmin = np.full(len(n_ids), 10**9, dtype=np.int64)
    comp_tmax = np.full(len(n_ids), -1, dtype=np.int64)
    np.minimum.at(comp_tmin, roots, tt)
    np.maximum.at(comp_tmax, roots, tt)
    comp_fork = np.zeros(len(n_ids), dtype=bool)
    comp_fork[roots[outdeg >= 2]] = True

    # ---- density and competitors (final float coordinates)
    from scipy.spatial import cKDTree

    trees = {}
    frame_idx = {}
    for t in np.unique(tt).tolist():
        ks = np.nonzero(tt == t)[0]
        frame_idx[t] = ks
        trees[t] = cKDTree(pos_um[ks])
    n10_src = np.zeros(n_e, dtype=np.int32)
    n10_dst = np.zeros(n_e, dtype=np.int32)
    alt_tgt_um = np.full(n_e, np.inf)
    alt_src_um = np.full(n_e, np.inf)
    t_src = tt[si]
    for t in np.unique(t_src).tolist():
        rows = np.nonzero(t_src == t)[0]
        if t in trees:
            n10_src[rows] = np.asarray([len(x) - 1 for x in trees[t].query_ball_point(pos_um[si[rows]], DENSITY_UM)])
        if t + 1 in trees:
            n10_dst[rows] = np.asarray([len(x) - 1 for x in
                                        trees[t + 1].query_ball_point(pos_um[di[rows]], DENSITY_UM)])
            k = min(2, len(frame_idx[t + 1]))
            dd, jj = trees[t + 1].query(pos_um[si[rows]], k=k)
            dd, jj = np.atleast_2d(dd.T).T if k == 1 else dd, np.atleast_2d(jj.T).T if k == 1 else jj
            ids1 = frame_idx[t + 1][np.minimum(jj, len(frame_idx[t + 1]) - 1)]
            first_is_dst = ids1[:, 0] == di[rows]
            alt_tgt_um[rows] = np.where(first_is_dst, dd[:, 1] if k > 1 else np.inf, dd[:, 0])
        if t in trees:
            k = min(2, len(frame_idx[t]))
            dd, jj = trees[t].query(pos_um[di[rows]], k=k)
            dd, jj = np.atleast_2d(dd.T).T if k == 1 else dd, np.atleast_2d(jj.T).T if k == 1 else jj
            ids0 = frame_idx[t][np.minimum(jj, len(frame_idx[t]) - 1)]
            first_is_src = ids0[:, 0] == si[rows]
            alt_src_um[rows] = np.where(first_is_src, dd[:, 1] if k > 1 else np.inf, dd[:, 0])

    length_um = np.linalg.norm(pos_um[di] - pos_um[si], axis=1)
    # constant-velocity residual in the final graph (source with exactly one predecessor)
    has_prev = indeg[si] == 1
    pv = np.where(has_prev, pred_of[si], si)
    predicted = 2 * pos_um[si] - pos_um[pv]
    cv_resid = np.where(has_prev, np.linalg.norm(pos_um[di] - predicted, axis=1), np.nan)
    v1 = pos_um[si] - pos_um[pv]
    v2 = pos_um[di] - pos_um[si]
    with np.errstate(invalid="ignore", divide="ignore"):
        turn_cos = np.where(has_prev, np.sum(v1 * v2, axis=1) /
                            (np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1) + 1e-9), np.nan)
    has_next = outdeg[di] == 1
    nx_ = np.where(has_next, succ_of[di], di)
    back_pred = 2 * pos_um[di] - pos_um[nx_]
    cv_resid_next = np.where(has_next, np.linalg.norm(pos_um[si] - back_pred, axis=1), np.nan)

    # ---- origin
    ck_set = {(s, d): p for s, d, p in ck_edges}
    rel_map = {(int(s), int(d)): (int(pc), float(ru), float(mu)) for s, d, pc, ru, mu in
               zip(rel["src"].tolist(), rel["dst"].tolist(), rel["pass_code"].tolist(), rel["raw_um"].tolist(),
                   rel["motion_um"].tolist())}
    syn = {i for i, n in ck_nodes.items() if n["syn"]}
    gap2n = {i for i, n in ck_nodes.items() if n["gap2"]}
    origin = np.empty(n_e, dtype=object)
    rpass = np.full(n_e, -1, dtype=np.int8)
    rel_raw = np.full(n_e, np.nan)
    rel_motion = np.full(n_e, np.nan)
    ck_prob = np.full(n_e, np.nan)
    for k, (s, d) in enumerate(zip(src.tolist(), dst.tolist())):
        if (s, d) not in ck_set:
            origin[k] = "safe_div"
            continue
        p = ck_set[(s, d)]
        if p is None:
            origin[k] = "gap1" if (s in syn or d in syn) else ("gap2" if (s in gap2n or d in gap2n) else "gap1_reuse")
            continue
        ck_prob[k] = p
        info = rel_map.get((s, d))
        if info is not None:
            rpass[k], rel_raw[k], rel_motion[k] = info
        base = "ilp" if p > 0 else "new"
        origin[k] = f"relink_{base}_" + {0: "tight", 1: "relaxed", 2: "raw"}.get(int(rpass[k]), "unknown")

    # gap span: distance between the observed end and start that a gap chain connects (ckpt coordinates)
    ck_pred: dict[int, list[int]] = {}
    ck_succ: dict[int, list[int]] = {}
    for s, d, _p in ck_edges:
        ck_succ.setdefault(s, []).append(d)
        ck_pred.setdefault(d, []).append(s)
    flagged = syn | gap2n
    gap_span = np.full(n_e, np.nan)
    for k in np.nonzero(np.isin(origin, ["gap1", "gap2"]))[0].tolist():
        a, b = int(src[k]), int(dst[k])
        steps = 0
        while a in flagged and len(ck_pred.get(a, [])) == 1 and steps < 4:
            a, steps = ck_pred[a][0], steps + 1
        steps = 0
        while b in flagged and len(ck_succ.get(b, [])) == 1 and steps < 4:
            b, steps = ck_succ[b][0], steps + 1
        if a in ck_pos_um and b in ck_pos_um:
            gap_span[k] = float(np.linalg.norm(ck_pos_um[b] - ck_pos_um[a]))

    # ---- ILP agreement / re-link alternatives
    ilp_succ: dict[int, list[tuple[int, float]]] = {}
    ilp_pred: dict[int, list[tuple[int, float]]] = {}
    for s, d, p in zip(rel["ilp_src"].tolist(), rel["ilp_dst"].tolist(), rel["ilp_p"].tolist()):
        ilp_succ.setdefault(int(s), []).append((int(d), float(p)))
        ilp_pred.setdefault(int(d), []).append((int(s), float(p)))
    ilp_src_other = np.zeros(n_e, dtype=bool)
    ilp_dst_other = np.zeros(n_e, dtype=bool)
    ilp_src_none = np.zeros(n_e, dtype=bool)
    ilp_dst_none = np.zeros(n_e, dtype=bool)
    alt_fwd = np.full(n_e, -1, dtype=np.int64)
    alt_fwd_p = np.full(n_e, np.nan)
    alt_bwd = np.full(n_e, -1, dtype=np.int64)
    alt_bwd_p = np.full(n_e, np.nan)
    for k, (s, d) in enumerate(zip(src.tolist(), dst.tolist())):
        succs = [x for x in ilp_succ.get(s, []) if x[0] != d]
        preds = [x for x in ilp_pred.get(d, []) if x[0] != s]
        ilp_src_none[k] = s not in ilp_succ
        ilp_dst_none[k] = d not in ilp_pred
        ilp_src_other[k] = bool(succs)
        ilp_dst_other[k] = bool(preds)
        free_f = [(c, p) for c, p in succs if c in index and indeg[index[c]] == 0 and tt[index[c]] == tt[index[s]] + 1]
        if free_f:
            c, p = max(free_f, key=lambda x: x[1])
            alt_fwd[k], alt_fwd_p[k] = c, p
        free_b = [(c, p) for c, p in preds if c in index and outdeg[index[c]] == 0 and tt[index[c]] + 1 == tt[index[d]]]
        if free_b:
            c, p = max(free_b, key=lambda x: x[1])
            alt_bwd[k], alt_bwd_p[k] = c, p

    # ---- official labels
    match = {int(i): int(m) for i, m in zip(mt["n_id"].tolist(), mt["n_match"].tolist())}
    gt_edges = set(zip(mt["gt_src"].tolist(), mt["gt_dst"].tolist()))
    gt_out: dict[int, int] = {}
    gt_in: dict[int, int] = {}
    for a, b in gt_edges:
        gt_out[a] = gt_out.get(a, 0) + 1
        gt_in[b] = gt_in.get(b, 0) + 1
    lab_map = {(int(s), int(d)): (1 if tp else (2 if v else 0)) for s, d, tp, v in
               zip(mt["e_src"].tolist(), mt["e_dst"].tolist(), mt["e_tp"].tolist(), mt["e_valid"].tolist())}
    label = np.zeros(n_e, dtype=np.int8)
    counted = np.zeros(n_e, dtype=bool)
    for k, (s, d) in enumerate(zip(src.tolist(), dst.tolist())):
        if (s, d) in lab_map:
            label[k] = lab_map[(s, d)]
            counted[k] = True
    gsrc = np.asarray([match.get(int(s), -1) for s in src.tolist()], dtype=np.int64)
    gdst = np.asarray([match.get(int(d), -1) for d in dst.tolist()], dtype=np.int64)
    alt_fwd_label = np.asarray([_label_pair(int(s), int(c), match, gt_edges, gt_out, gt_in) if c >= 0 else -1
                                for s, c in zip(src.tolist(), alt_fwd.tolist())], dtype=np.int8)
    alt_bwd_label = np.asarray([_label_pair(int(c), int(d), match, gt_edges, gt_out, gt_in) if c >= 0 else -1
                                for c, d in zip(alt_bwd.tolist(), dst.tolist())], dtype=np.int8)
    # label of the would-be edge had the metric seen it (sanity: equals `label` for counted edges)
    label_pair = np.asarray([_label_pair(int(s), int(d), match, gt_edges, gt_out, gt_in)
                             for s, d in zip(src.tolist(), dst.tolist())], dtype=np.int8)

    row = json.loads(str(mt["row"]))
    tp_n, fp_n = int(np.sum(label == 1)), int(np.sum(label == 2))
    check = {"tp": tp_n, "fp": fp_n, "metric_tp": int(row["edge_tp"]), "metric_fp": int(row["edge_fp"]),
             "pair_label_mismatch": int(np.sum((label_pair != label) & counted)),
             "relink": json.loads(str(rel["check"])), "relink_valid": int(rel["valid"])}
    cols = {
        "stem": np.full(n_e, stem, dtype=object), "src": src, "dst": dst, "t": tt[si],
        "label": label, "counted": counted, "gt_src": gsrc, "gt_dst": gdst,
        "origin": origin.astype(str), "relink_pass": rpass, "edge_prob": prob, "ckpt_prob": ck_prob,
        "len_um": length_um, "len_pre_um": dist_pre, "relink_raw_um": rel_raw, "relink_motion_um": rel_motion,
        "cv_resid_um": cv_resid, "cv_resid_next_um": cv_resid_next, "turn_cos": turn_cos, "gap_span_um": gap_span,
        "n10_src": n10_src, "n10_dst": n10_dst, "alt_tgt_um": alt_tgt_um, "alt_src_um": alt_src_um,
        "src_indeg": indeg[si].astype(np.int8), "src_outdeg": outdeg[si].astype(np.int8),
        "dst_indeg": indeg[di].astype(np.int8), "dst_outdeg": outdeg[di].astype(np.int8),
        "chain_up": up[si].astype(np.int32), "chain_down": down[di].astype(np.int32),
        "comp_nodes": comp_size[roots[si]].astype(np.int32),
        "comp_tspan": (comp_tmax[roots[si]] - comp_tmin[roots[si]] + 1).astype(np.int32),
        "comp_fork": comp_fork[roots[si]],
        "short_rescue": (comp_size[roots[si]] < min_len) & ~comp_fork[roots[si]],
        "src_syn": np.isin(src, list(syn)), "dst_syn": np.isin(dst, list(syn)),
        "src_gap2": np.isin(src, list(gap2n)), "dst_gap2": np.isin(dst, list(gap2n)),
        "ilp_src_other": ilp_src_other, "ilp_dst_other": ilp_dst_other,
        "ilp_src_none": ilp_src_none, "ilp_dst_none": ilp_dst_none,
        "alt_fwd": alt_fwd, "alt_fwd_p": alt_fwd_p, "alt_fwd_label": alt_fwd_label,
        "alt_bwd": alt_bwd, "alt_bwd_p": alt_bwd_p, "alt_bwd_label": alt_bwd_label,
        "last_frame": tt[di] >= tt.max(),
    }
    return {"stem": stem, "cols": cols, "check": check, "row": row, "tail_stats": tail_stats,
            "seconds": round(time.time() - started, 2)}


def _task(stem: str, settings: dict) -> dict:
    return video_frame(stem, settings)


# ------------------------------------------------------------------------------------------------ score arithmetic
def video_score_rows(counts: "pd.DataFrame", base_rows: dict) -> list[dict]:  # noqa: F821
    """Per-video metric rows after removing tp_drop TP edges (-> FN) and fp_drop FP edges, plus tp_add/fp_add new edges
    (re-link); node count and division counts unchanged (adjusted Jaccard recomputed with the official formula)."""
    rows = []
    for stem, base in base_rows.items():
        c = counts.get(stem, {})
        tp = int(base["edge_tp"]) - int(c.get("tp_drop", 0)) + int(c.get("tp_add", 0))
        fp = int(base["edge_fp"]) - int(c.get("fp_drop", 0)) + int(c.get("fp_add", 0))
        fn = int(base["edge_fn"]) + int(c.get("tp_drop", 0)) - int(c.get("tp_add", 0))
        denom = tp + fp + fn
        j = tp / denom if denom > 0 else float("nan")
        r = float(base["total_node_ratio"])
        adj = max(0.0, j * (1 - 0.1 * r)) if j == j and r == r else float("nan")
        rows.append({**base, "edge_tp": tp, "edge_fp": fp, "edge_fn": fn, "edge_jaccard": j, "adj_edge_jaccard": adj})
    return rows


def summarise(rows: list[dict]) -> float:
    return float(R.summarise_rows(rows)["score"]) if rows else float("nan")


def estimate(df, mask, base_rows: dict, relink: str = "") -> dict:
    """Score deltas (all / 44b6 / 6bba) of dropping the masked edges, or re-linking them (relink='fwd'|'bwd'|'any')."""
    import pandas as pd

    sub = df.loc[mask, ["stem", "label", "alt_fwd", "alt_fwd_label", "alt_bwd", "alt_bwd_label"]]
    g = pd.DataFrame({"stem": sub["stem"], "tp_drop": (sub["label"] == 1).astype(int),
                      "fp_drop": (sub["label"] == 2).astype(int)})
    if relink:
        use_f = sub["alt_fwd"].to_numpy() >= 0 if relink in ("fwd", "any") else np.zeros(len(sub), bool)
        use_b = (sub["alt_bwd"].to_numpy() >= 0) & ~use_f if relink in ("bwd", "any") else np.zeros(len(sub), bool)
        lab = np.where(use_f, sub["alt_fwd_label"].to_numpy(), np.where(use_b, sub["alt_bwd_label"].to_numpy(), -1))
        g["tp_add"] = (lab == 1).astype(int)
        g["fp_add"] = (lab == 2).astype(int)
        # an alternative end point can be claimed by two masked edges: keep the first claim only
        fwd_key = sub["stem"] + ":" + sub["alt_fwd"].astype(str)
        bwd_key = sub["stem"] + ":" + sub["alt_bwd"].astype(str)
        dup = (use_f & fwd_key.duplicated().to_numpy()) | (use_b & bwd_key.duplicated().to_numpy())
        g.loc[dup, ["tp_add", "fp_add"]] = 0
    counts = g.groupby("stem").sum().to_dict("index")
    out = {"edges": int(mask.sum()), "tp": int(g["tp_drop"].sum()), "fp": int(g["fp_drop"].sum())}
    if relink:
        out.update(tp_add=int(g["tp_add"].sum()), fp_add=int(g["fp_add"].sum()))
    for subset in ("all", "44b6", "6bba"):
        stems = [s for s in base_rows if subset == "all" or s.startswith(subset)]
        b = {s: base_rows[s] for s in stems}
        new_rows = video_score_rows(counts, b)
        out[f"d_{subset}"] = summarise(new_rows) - summarise(list(b.values()))
        vs_new = {r["dataset"]: R._video_score(r) for r in new_rows}
        vs_old = {s: R._video_score(b[s]) for s in stems}
        out[f"gain_{subset}"] = int(sum(vs_new[s] > vs_old[s] + 1e-12 for s in stems))
        out[f"loss_{subset}"] = int(sum(vs_new[s] < vs_old[s] - 1e-12 for s in stems))
    return out


# ------------------------------------------------------------------------------------------------ classes
def class_masks(df) -> list[tuple[str, "np.ndarray"]]:
    o = df["origin"]
    p = df["edge_prob"]
    L = df["len_um"]
    unscored = p == 0.0
    leaf = df["dst_outdeg"] == 0
    start = df["src_indeg"] == 0
    relink = o.str.startswith("relink_")
    classes = [("ALL", np.ones(len(df), bool))]
    for name in sorted(o.unique()):
        classes.append((f"origin={name}", (o == name).to_numpy()))
    classes += [
        ("relink tight", (df["relink_pass"] == 0).to_numpy()),
        ("relink relaxed", (df["relink_pass"] == 1).to_numpy()),
        ("prob==0 (unscored relink)", unscored.to_numpy()),
        ("prob in (0,0.6)", ((p > 0) & (p < 0.6)).to_numpy()),
        ("prob in [0.6,0.8)", ((p >= 0.6) & (p < 0.8)).to_numpy()),
        ("prob >= 0.8", (p >= 0.8).to_numpy()),
        ("prob None (gap/safe-div)", p.isna().to_numpy()),
        ("short_rescue", df["short_rescue"].to_numpy()),
        ("fork edge (src outdeg 2)", (df["src_outdeg"] >= 2).to_numpy()),
        ("leaf edge (dst end)", (leaf & ~df["last_frame"]).to_numpy()),
        ("start edge (src start)", (start & (df["t"] > 0)).to_numpy()),
        ("len > 6 um", (L > 6).to_numpy()),
        ("len > 8 um", (L > 8).to_numpy()),
        ("len > 10 um", (L > 10).to_numpy()),
        ("cv_resid > 6 um", (df["cv_resid_um"] > 6).to_numpy()),
        ("cv_resid > 8 um", (df["cv_resid_um"] > 8).to_numpy()),
        ("turn_cos < 0", (df["turn_cos"] < 0).to_numpy()),
        ("dense n10_dst >= 4", (df["n10_dst"] >= 4).to_numpy()),
        ("alt target closer (alt_tgt < len)", (df["alt_tgt_um"] < L).to_numpy()),
        ("comp_nodes < 10", (df["comp_nodes"] < 10).to_numpy()),
        ("chain seg <= 3 edges", ((df["chain_up"] + df["chain_down"] + 1) <= 3).to_numpy()),
        ("ILP src->other", (relink & df["ilp_src_other"]).to_numpy()),
        ("ILP other->dst", (relink & df["ilp_dst_other"]).to_numpy()),
        ("ILP disagree both ends", (relink & df["ilp_src_other"] & df["ilp_dst_other"]).to_numpy()),
        ("unscored & ILP src->other", (unscored & df["ilp_src_other"]).to_numpy()),
        ("unscored & ILP other->dst", (unscored & df["ilp_dst_other"]).to_numpy()),
        ("unscored & ILP both none", (unscored & df["ilp_src_none"] & df["ilp_dst_none"]).to_numpy()),
        ("unscored & alt_fwd free", (unscored & (df["alt_fwd"] >= 0)).to_numpy()),
        ("unscored & alt_bwd free", (unscored & (df["alt_bwd"] >= 0)).to_numpy()),
        ("unscored & relaxed", (unscored & (df["relink_pass"] == 1)).to_numpy()),
        ("unscored & len > 6", (unscored & (L > 6)).to_numpy()),
        ("unscored & len > 8", (unscored & (L > 8)).to_numpy()),
        ("unscored & leaf", (unscored & leaf & ~df["last_frame"]).to_numpy()),
        ("unscored & start", (unscored & start).to_numpy()),
        ("unscored & leaf|start", (unscored & ((leaf & ~df["last_frame"]) | (start & (df["t"] > 0)))).to_numpy()),
        ("unscored & cv_resid > 6", (unscored & (df["cv_resid_um"] > 6)).to_numpy()),
        ("unscored & turn_cos < 0", (unscored & (df["turn_cos"] < 0)).to_numpy()),
        ("unscored & alt_tgt < len", (unscored & (df["alt_tgt_um"] < L)).to_numpy()),
        ("unscored & comp < 10", (unscored & (df["comp_nodes"] < 10)).to_numpy()),
        ("relaxed & len > 8", ((df["relink_pass"] == 1) & (L > 8)).to_numpy()),
        ("relaxed & cv_resid > 6", ((df["relink_pass"] == 1) & (df["cv_resid_um"] > 6)).to_numpy()),
        ("gap1 & span > 8", ((o == "gap1") & (df["gap_span_um"] > 8)).to_numpy()),
        ("gap2 & span > 12", ((o == "gap2") & (df["gap_span_um"] > 12)).to_numpy()),
        ("gap edge & leaf|start", (o.str.startswith("gap") & ((leaf & ~df["last_frame"]) | start)).to_numpy()),
        ("safe_div & len > 8", ((o == "safe_div") & (L > 8)).to_numpy()),
        ("cv_resid > 8 & scored<0.6", ((df["cv_resid_um"] > 8) & (p < 0.6)).to_numpy()),
    ]
    return classes


def class_table(df, base_rows: dict) -> list[dict]:
    rows = []
    for name, mask in class_masks(df):
        mask = np.asarray(mask, dtype=bool)
        entry = {"class": name}
        for subset in ("all", "44b6", "6bba"):
            m = mask if subset == "all" else mask & df["stem"].str.startswith(subset).to_numpy()
            lab = df["label"].to_numpy()[m]
            ev = int(np.sum(lab > 0))
            fp = int(np.sum(lab == 2))
            entry.update({f"n_{subset}": int(m.sum()), f"eval_{subset}": ev, f"tp_{subset}": int(np.sum(lab == 1)),
                          f"fp_{subset}": fp, f"fp_rate_{subset}": fp / ev if ev else float("nan")})
        entry["fork_edges"] = int(np.sum(mask & (df["src_outdeg"].to_numpy() >= 2)))
        if name != "ALL":
            est = estimate(df, mask, base_rows)
            entry.update({f"drop_{k}": v for k, v in est.items() if k.startswith(("d_", "gain_", "loss_"))})
            if "unscored" in name or name.startswith(("origin=relink_new", "prob==0")):
                for mode in ("fwd", "bwd", "any"):
                    est = estimate(df, mask, base_rows, relink=mode)
                    entry[f"relink_{mode}_d_all"] = est["d_all"]
                    entry[f"relink_{mode}_add"] = f"{est['tp_add']}/{est['fp_add']}"
        rows.append(entry)
    return rows


# ------------------------------------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", default=str(DEFAULT_CACHE))
    ap.add_argument("--replay-out", default=str(DEFAULT_REPLAY_OUT), help="replay --out dir holding tail/<base_key>")
    ap.add_argument("--config", default="exp39", help="replay config spec whose final graph is dissected")
    ap.add_argument("--tag", default="exp39")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--report-dir", default=str(HERE))
    ap.add_argument("--data-dir", default=str(R.pl.DEFAULT_DATA))
    ap.add_argument("--splits", default=str(R.DEFAULT_SPLITS))
    ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.workers > 4:
        raise SystemExit("at most 4 workers (keep the laptop responsive)")
    import pandas as pd

    cache, out, replay_out = Path(a.cache).resolve(), Path(a.out).resolve(), Path(a.replay_out).resolve()
    tail_dir, cfg = tail_dir_for(a.config, replay_out)
    if cfg["insert"]:
        raise SystemExit("anatomy reads the post-tail graph; insertion configs are not supported")
    stems = list(a.stems) or sorted(p.stem for p in (cache / "ckpt").glob("*.npz"))
    missing = [s for s in stems if not (tail_dir / f"{s}.npz").is_file()]
    if missing:
        raise SystemExit(f"{len(missing)} tails missing under {tail_dir} (e.g. {missing[:3]}): run the replay for "
                         f"config {a.config!r} with --out {replay_out} first")
    settings = {"cache": str(cache), "out": str(out), "tail_dir": str(tail_dir), "data_dir": str(Path(a.data_dir)),
                "ns_out": str(out / "ns")}
    out.mkdir(parents=True, exist_ok=True)
    print(f"tail {tail_dir}\nout  {out}\n{len(stems)} videos, {a.workers} workers", flush=True)

    results: dict[str, dict] = {}
    started = time.time()
    if a.workers <= 1:
        for s in stems:
            results[s] = _task(s, settings)
            print(f"  {s} {results[s]['seconds']} s", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=a.workers) as pool:
            pending = list(reversed(stems))
            running = set()
            while pending or running:
                while pending and len(running) < 2 * a.workers:
                    running.add(pool.submit(_task, pending.pop(), settings))
                done, running = wait(running, return_when=FIRST_COMPLETED)
                for fut in done:
                    r = fut.result()
                    results[r["stem"]] = r
                    n = len(results)
                    if n % 10 == 0 or n == len(stems):
                        el = time.time() - started
                        print(f"  {n}/{len(stems)}  {el / 60:.1f} min  eta {el / n * (len(stems) - n) / 60:.1f} min",
                              flush=True)

    # ---- validation (per video): labels vs metric, and vs the replay's per-video csv for this config
    bad = {s: r["check"] for s, r in results.items()
           if r["check"]["tp"] != r["check"]["metric_tp"] or r["check"]["fp"] != r["check"]["metric_fp"]
           or r["check"]["pair_label_mismatch"]}
    relink_bad = {s: r["check"]["relink"] for s, r in results.items() if not r["check"]["relink_valid"]}
    replay_rows = {}
    csv_path = replay_out / "per_video_all.csv"
    if csv_path.is_file():
        pv = pd.read_csv(csv_path)
        pv = pv[pv["config"] == a.config]
        replay_rows = {r["dataset"]: r for r in pv.to_dict("records")}
    replay_bad = {s: (results[s]["check"]["tp"], results[s]["check"]["fp"], int(replay_rows[s]["edge_tp"]),
                      int(replay_rows[s]["edge_fp"])) for s in stems if s in replay_rows
                  and (results[s]["check"]["tp"] != int(replay_rows[s]["edge_tp"])
                       or results[s]["check"]["fp"] != int(replay_rows[s]["edge_fp"]))}
    tot_tp = sum(r["check"]["tp"] for r in results.values())
    tot_fp = sum(r["check"]["fp"] for r in results.values())
    print(f"VALIDATION: labels TP {tot_tp} FP {tot_fp}; metric mismatch {len(bad)} videos; replay csv mismatch "
          f"{len(replay_bad)} of {sum(s in replay_rows for s in stems)} videos; relink rerun invalid {len(relink_bad)}",
          flush=True)
    if bad or replay_bad:
        print(json.dumps({"metric": dict(list(bad.items())[:5]), "replay": dict(list(replay_bad.items())[:5])},
                         indent=1))
        raise SystemExit("label validation FAILED - not writing the anatomy")
    if relink_bad:
        print("WARNING relink rerun differs from the ckpt in", len(relink_bad), "videos:",
              json.dumps(dict(list(relink_bad.items())[:3])))

    # ---- edge table
    splits = json.loads(Path(a.splits).read_text(encoding="utf-8"))
    split_of = {s: "selection" for s in splits["selection"]} | {s: "confirmation" for s in splits["confirmation"]}
    frames = []
    for s in stems:
        f = pd.DataFrame(results[s]["cols"])
        frames.append(f)
    df = pd.concat(frames, ignore_index=True)
    df["embryo"] = df["stem"].str.split("_").str[0]
    df["split"] = df["stem"].map(split_of).fillna("none")
    for c in ("stem", "origin", "embryo", "split"):
        df[c] = df[c].astype("category")
    edges_path = out / f"edges_{a.tag}.parquet"
    df.to_parquet(edges_path, index=False)
    df["stem"] = df["stem"].astype(str)
    df["origin"] = df["origin"].astype(str)
    print(f"wrote {edges_path} ({len(df)} edges, {edges_path.stat().st_size / 1e6:.1f} MB)", flush=True)

    # ---- class tables and drop estimates
    base_rows = {s: {"dataset": s, **results[s]["row"]} for s in stems}
    base_score = summarise(list(base_rows.values()))
    table = class_table(df, base_rows)
    report_dir = Path(a.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(table).to_csv(report_dir / f"classes_{a.tag}.csv", index=False)
    j_all = tot_tp / (tot_tp + tot_fp + sum(int(r["row"]["edge_fn"]) for r in results.values()))
    lines = [f"# Edge anatomy of the final `{a.config}` graph ({len(stems)} videos)", "",
             f"tail `{tail_dir}`; labels = official metric per-edge frame (validated: TP {tot_tp}, FP {tot_fp}, "
             f"= metric and replay per-video csv in every video); base score {base_score:.6f}.",
             f"Relink rerun (pass / motion residual) invalid in {len(relink_bad)} videos.",
             f"Dropping a class pays only if FP/(TP) > 1/J, i.e. FP rate among evaluable > J/(1+J) ~ "
             f"{j_all / (1 + j_all):.3f}.", "",
             "| class | edges | eval | TP | FP | FP rate | FP rate 44b6 | FP rate 6bba | fork edges | d drop all | "
             "d 44b6 | d 6bba | videos +/- | d relink any (add TP/FP) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]

    def f6(x):
        return "-" if x is None or (isinstance(x, float) and x != x) else f"{x:+.6f}"

    for e in table:
        rl = (f"{f6(e['relink_any_d_all'])} ({e['relink_any_add']})" if "relink_any_d_all" in e else "")
        lines.append(
            f"| {e['class']} | {e['n_all']} | {e['eval_all']} | {e['tp_all']} | {e['fp_all']} | "
            f"{e['fp_rate_all']:.3f} | {e['fp_rate_44b6']:.3f} | {e['fp_rate_6bba']:.3f} | {e['fork_edges']} | "
            f"{f6(e.get('drop_d_all'))} | {f6(e.get('drop_d_44b6'))} | {f6(e.get('drop_d_6bba'))} | "
            f"{e.get('drop_gain_all', '-')}/{e.get('drop_loss_all', '-')} | {rl} |")
    summary = {"config": a.config, "tail_dir": str(tail_dir), "videos": len(stems), "edges": len(df),
               "label_tp": tot_tp, "label_fp": tot_fp, "base_score": base_score,
               "relink_invalid_videos": sorted(relink_bad), "classes": table,
               "tail_stats_total": {k: float(sum(float(r["tail_stats"].get(k, 0) or 0) for r in results.values()))
                                    for k in R.TAIL_STAT_KEYS}}
    R._atomic_text(report_dir / f"anatomy_{a.tag}.json", R._dumps(summary, indent=1))
    R._atomic_text(report_dir / f"anatomy_{a.tag}.md", "\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)
    print(f"done in {(time.time() - started) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
