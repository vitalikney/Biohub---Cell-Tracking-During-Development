"""False-negative anatomy of the FINAL exp39 graph: why is each missed GT edge missing, and which misses are recoverable?

WHAT IT DOES (per video, <= 3 workers)
    graph      the replay's cached post-tail graph of the exp39 base (tail/<base_key>/<stem>.npz, found with anatomy.py's
               tail_dir_for = replay.py's own key recipe); with --ef "<k=v,...>" the edge filter (replay config keys ef.*,
               tools/build_probe_kernel.py edgefilter_final_graph, same call as replay.run_config_video) is applied first,
               so the graph is the exp39 + ef final graph.
    matching   anatomy.official_match: the graph is written like the replay (write_test_submission rounding) and scored by
               the OFFICIAL code (7 um timepoint-aware optimal assignment); cached per video. A GT edge (u, v) is TP iff a
               TP predicted edge maps onto it; FN = every other GT edge. VALIDATION: per-video FN count == the metric's
               edge_fn (and == the replay's per-video csv when given); the script stops if any video differs.
    classes    one primary class per FN edge (priority top-down):
               c_gt_skip        the GT edge spans != 1 frame (a t -> t+1 predicted edge can never match it)
               c_gap_node       both ends matched, p_u or p_v is a synthetic gap node (gap1 / recover_strict_gap2)
               c_gap_node_off   an end is unmatched and our track passes through a synthetic node at that frame (the
                                matched end's neighbour in the graph is synthetic) or the nearest node there is synthetic
               a_<reason>       an end is unmatched (detection side); reason of the (first) unmatched end:
                                  taken   a final node lies within 7 um but the assignment gave it to another GT node
                                  free    a final node lies within 7 um and is unmatched (assignment corner case)
                                  linefit the ckpt node within 7 um is still in the graph but linefit moved it > 7 um
                                  tail    a ckpt node within 7 um was removed by the tail (short tracks / prune / ...)
                                  pass1   a raw ILP node within 7 um is absent from the ckpt (lost before the ckpt)
                                  never   no raw ILP node within 7 um (never detected by the linker's solution)
               b_<topology>     both ends matched to real nodes p_u, p_v, no TP edge p_u -> p_v:
                                  break       p_u is a track END and p_v a track START
                                  v_taken     p_u is an end, p_v is linked from another node
                                  u_diverted  p_u is linked to another node, p_v is a start
                                  swap        both linked elsewhere
                                  present     the edge p_u -> p_v exists but the metric discarded it
               provenance of p_u -> p_v (b / c_gap_node): ilp = the raw ILP solution had the edge (raw/<stem>.geff; this
               cache holds the ILP SOLUTION only - the candidate set with network scores is not available, so "the network
               scored the pair" == "ILP edge" here), ckpt = the post-gap checkpoint had it (relink / gap edge) and the tail
               removed it, none = never proposed.
    candidates every (track end at t, track start at t+1) pair of the final graph within --cand-um, with prediction-side
               features only (distance, velocity-predicted distance, ILP edge + p, ckpt edge, NN ranks, chain lengths,
               synthetic flags) and the official label the added edge would get under the fixed matching (TP/FP/NE) -
               the design table of a GT-free stitching rule. Adding edges between existing nodes leaves the node matching
               unchanged, so edge counts of a stitch rule are exact from this table (the division term is not).
               Detection-side rows also carry other_free (the matched end is a free track end / start) and bridge (a
               1-frame gap: the matched end is an end at t and the unmatched node's GT successor is matched to a start
               at t+2, or the mirror).
    estimates  oracle score change of recovering each linkable class (a recovered FN becomes TP; for v_taken /
               u_diverted / swap the competing edges must go - their labels are counted: removing a TP is a loss) with
               the official summarise() over per-video rows (node count unchanged), and the stitch rules in
               STITCH_RULES evaluated by the SAME function the replay / kernel run (bpk.STITCH_FN, reached through the
               replay's patched notebook namespace) on every video: exact edge TP / FP of the added edges under the
               fixed matching, summarised per split x embryo with the share of videos that gain. The division term is
               held fixed here; the replay (config keys st.*) is exact.

OUTPUTS
    <out>/fn_<tag>.parquet, <out>/cand_<tag>.parquet      FN rows / candidate pairs (git-ignored)
    <out>/match/<tail_key>__ef_<fp>/<stem>.npz            official matches of the --ef graph (exp39 reuses anatomy.py's)
    experiments/l2_daughternet/edge_anatomy/fn_anatomy_<tag>.{md,json}

USAGE
    python experiments/l2_daughternet/edge_anatomy/fn_anatomy.py --workers 3
    python experiments/l2_daughternet/edge_anatomy/fn_anatomy.py --workers 3 --tag exp39_ef --ef alt=3,relink=1,prune=1
    python experiments/l2_daughternet/edge_anatomy/fn_anatomy.py --stems 44b6_0b24845f --workers 1     (smoke)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import anatomy as A  # noqa: E402  (tail location, official match, relink rerun, score arithmetic - one code path)

R = A.R
ROOT = A.ROOT
DEFAULT_OUT = ROOT / ".public_local_cache" / "l2_fn_anatomy"
MATCH_UM = 7.0
REASONS = ("never", "pass1", "tail", "linefit", "taken", "free")
_ST = {"enable": 1, "min_prob": 0.0, "max_um": 0.0, "min_um": 0.0, "min_chain": 0}
STITCH_RULES = {  # evaluated exactly (edge counts) on every video by the kernel function; the replay grid is the judge
    "st_all": dict(_ST), "st_p05": {**_ST, "min_prob": 0.5}, "st_p06": {**_ST, "min_prob": 0.6},
    "st_p07": {**_ST, "min_prob": 0.7}, "st_p08": {**_ST, "min_prob": 0.8}, "st_c1": {**_ST, "min_chain": 1},
    "st_c2": {**_ST, "min_chain": 2}, "st_max12": {**_ST, "max_um": 12.0}, "st_min6": {**_ST, "min_um": 6.0},
}
TOPOLOGIES = ("break", "v_taken", "u_diverted", "swap", "present")


# ------------------------------------------------------------------------------------------------ helpers
def _rounded(nodes: dict, ids: list[int]) -> np.ndarray:
    """write_geff rounding (what the metric sees)."""
    return np.asarray([[max(0.0, float(round(float(nodes[i][k])))) for k in ("z", "y", "x")] for i in ids],
                      dtype=np.float64).reshape(-1, 3)


class FrameIndex:
    """Per-frame KD-trees over scaled (um) coordinates."""

    def __init__(self, ids: np.ndarray, t: np.ndarray, pos_um: np.ndarray):
        from scipy.spatial import cKDTree

        self.ids, self.t, self.pos = ids, t, pos_um
        self.trees, self.rows = {}, {}
        for tt in np.unique(t).tolist():
            rows = np.nonzero(t == tt)[0]
            self.rows[tt] = rows
            self.trees[tt] = cKDTree(pos_um[rows])

    def within(self, tt: int, p: np.ndarray, r: float) -> list[tuple[int, float]]:
        if tt not in self.trees:
            return []
        rows = self.rows[tt][self.trees[tt].query_ball_point(p, r)]
        return sorted(((int(self.ids[k]), float(np.linalg.norm(self.pos[k] - p))) for k in rows), key=lambda x: x[1])


def _chains(n_ids: list[int], tt: dict, succ: dict, pred: dict) -> tuple[dict, dict]:
    """Linear-chain length (edges) above / below every node (stops at forks / merges)."""
    order = sorted(n_ids, key=lambda i: tt[i])
    up = {}
    for i in order:
        p = pred.get(i, [])
        up[i] = up[p[0]] + 1 if len(p) == 1 and len(succ.get(p[0], [])) == 1 else 0
    down = {}
    for i in reversed(order):
        s = succ.get(i, [])
        down[i] = down[s[0]] + 1 if len(s) == 1 and len(pred.get(s[0], [])) == 1 else 0
    return up, down


# ------------------------------------------------------------------------------------------------ per video
def fn_video(stem: str, settings: dict) -> dict:
    A.init_worker(settings["anatomy"])
    started = time.time()
    cache, tail_dir = Path(settings["cache"]), Path(settings["tail_dir"])
    ns, scorer = A._W["ns"], A._W["scorer"]
    nodes, edges, _ = R.load_tail(tail_dir / f"{stem}.npz")
    ilp_probs = R.load_ilp_probs(cache, stem)  # the kernel's capture (raw ILP solution, next-frame / length filter)
    ef_stats: dict = {}
    if settings["ef"]:
        nodes, edges = ns["edgefilter_final_graph"](nodes, [dict(e) for e in edges], ef_stats, dict(settings["ef"]),
                                                    dict(ilp_probs))
        match_out = Path(settings["out"])
    else:
        match_out = Path(settings["anatomy"]["out"])  # anatomy.py's cache (same key => same graph)
    mt = A.official_match(stem, nodes, edges, match_out, settings["match_key"])
    row = json.loads(str(mt["row"]))

    # ---- GT side (its physical scale is what the metric applies to both graphs)
    gt, gt_scale = scorer._load_gt_and_scale(Path(str(scorer.DATA)) / f"{stem}.geff")
    scale = np.asarray(gt_scale, dtype=np.float64)
    gna = gt.node_attrs()
    g_pos = {int(i): np.asarray([z, y, x], dtype=np.float64) * scale for i, z, y, x in
             zip(gna["node_id"].to_list(), gna["z"].to_list(), gna["y"].to_list(), gna["x"].to_list())}
    g_t = {int(i): int(t) for i, t in zip(gna["node_id"].to_list(), gna["t"].to_list())}

    # ---- prediction side: final, ckpt, raw
    f_ids = sorted(nodes)
    f_t = {i: int(nodes[i]["t"]) for i in f_ids}
    f_pos_r = _rounded(nodes, f_ids) * scale                                  # metric coordinates
    f_pos = np.asarray([[nodes[i][k] for k in ("z", "y", "x")] for i in f_ids], dtype=np.float64).reshape(-1, 3) * scale
    f_row = {i: k for k, i in enumerate(f_ids)}
    f_idx = FrameIndex(np.asarray(f_ids, np.int64), np.asarray([f_t[i] for i in f_ids], np.int64), f_pos_r)
    syn = {i for i in f_ids if nodes[i].get("gap_synthetic") or nodes[i].get("gap2_synthetic")}
    succ: dict[int, list[int]] = {}
    pred: dict[int, list[int]] = {}
    for e in edges:
        s, d = int(e["source_id"]), int(e["target_id"])
        succ.setdefault(s, []).append(d)
        pred.setdefault(d, []).append(s)
    edge_set = {(int(e["source_id"]), int(e["target_id"])) for e in edges}

    ck_nodes, ck_edges, _dcs, _exp = R.load_ckpt(cache, stem)
    ck_ids = sorted(ck_nodes)
    ck_pos = _rounded(ck_nodes, ck_ids) * scale
    ck_idx = FrameIndex(np.asarray(ck_ids, np.int64), np.asarray([ck_nodes[i]["t"] for i in ck_ids], np.int64), ck_pos)
    ck_syn = {i for i, n in ck_nodes.items() if n["syn"] or n["gap2"]}
    ck_edge = {(s, d): p for s, d, p in ck_edges}

    raw = R.fc._load_raw_graph(cache / "raw" / f"{stem}.geff").node_attrs()
    raw_nodes = {int(i): {"t": int(t), "z": float(z), "y": float(y), "x": float(x)} for i, t, z, y, x in
                 zip(raw["node_id"].to_list(), raw["t"].to_list(), raw["z"].to_list(), raw["y"].to_list(),
                     raw["x"].to_list())}
    raw_ids = sorted(raw_nodes)
    raw_idx = FrameIndex(np.asarray(raw_ids, np.int64), np.asarray([raw_nodes[i]["t"] for i in raw_ids], np.int64),
                         _rounded(raw_nodes, raw_ids) * scale)


    # ---- official matching and TP GT edges
    match = {int(i): int(m) for i, m in zip(mt["n_id"].tolist(), mt["n_match"].tolist())}
    inv: dict[int, list[int]] = {}
    for p, g in match.items():
        if g != -1:
            inv.setdefault(g, []).append(p)
    multi = sum(len(v) > 1 for v in inv.values())
    gt_edges = list(zip(mt["gt_src"].tolist(), mt["gt_dst"].tolist()))
    gt_edge_set = set(gt_edges)
    gt_out: dict[int, int] = {}
    gt_in: dict[int, int] = {}
    gt_succ: dict[int, list[int]] = {}
    gt_pred: dict[int, list[int]] = {}
    for a, b in gt_edges:
        gt_out[a] = gt_out.get(a, 0) + 1
        gt_in[b] = gt_in.get(b, 0) + 1
        gt_succ.setdefault(a, []).append(b)
        gt_pred.setdefault(b, []).append(a)
    lab = {(int(s), int(d)): (1 if tp else (2 if v else 0)) for s, d, tp, v in
           zip(mt["e_src"].tolist(), mt["e_dst"].tolist(), mt["e_tp"].tolist(), mt["e_valid"].tolist())}
    tp_gt = {(match[s], match[d]) for (s, d), l in lab.items() if l == 1}
    fn_edges = [(a, b) for a, b in gt_edges if (a, b) not in tp_gt]

    def reason(g: int) -> tuple[str, int, bool]:
        """Why GT node g has no predicted match: (reason, nearest node id or -1, that node is synthetic)."""
        t, p = g_t[g], g_pos[g]
        near = f_idx.within(t, p, MATCH_UM)
        if near:
            nid = near[0][0]
            return ("free" if match.get(nid, -1) == -1 else "taken"), nid, nid in syn
        near = ck_idx.within(t, p, MATCH_UM)
        if near:
            nid = near[0][0]
            return ("linefit" if nid in nodes else "tail"), nid, nid in ck_syn
        near = raw_idx.within(t, p, MATCH_UM)
        if near:
            return "pass1", near[0][0], False
        return "never", -1, False

    rows = []
    for a, b in fn_edges:
        pu = inv.get(a, [-1])[0]
        pv = inv.get(b, [-1])[0]
        dt = g_t[b] - g_t[a]
        r = {"stem": stem, "gt_u": a, "gt_v": b, "t": g_t[a], "dt": dt, "gt_u_out": gt_out.get(a, 0),
             "gt_v_in": gt_in.get(b, 0), "gt_div": gt_out.get(a, 0) >= 2, "p_u": pu, "p_v": pv,
             "u_reason": "", "v_reason": "", "u_near": -1, "v_near": -1, "u_near_syn": False, "v_near_syn": False,
             "p_u_syn": pu in syn, "p_v_syn": pv in syn, "topo": "", "prov": "", "ilp_p": np.nan,
             "ckpt_prob": np.nan, "dist_um": np.nan, "comp_fp": 0, "comp_tp": 0, "comp_ne": 0, "nbr_syn": False,
             "pu_out": len(succ.get(pu, [])) if pu != -1 else -1, "pv_in": len(pred.get(pv, [])) if pv != -1 else -1,
             "other_free": False, "bridge": False}
        if pu == -1:
            r["u_reason"], r["u_near"], r["u_near_syn"] = reason(a)
        if pv == -1:
            r["v_reason"], r["v_near"], r["v_near_syn"] = reason(b)
        if pu != -1 and pv != -1:
            r["dist_um"] = float(np.linalg.norm(f_pos[f_row[pv]] - f_pos[f_row[pu]]))
            if (pu, pv) in ilp_probs:
                r["prov"], r["ilp_p"] = "ilp", float(ilp_probs[(pu, pv)])
            elif (pu, pv) in ck_edge:
                r["prov"] = "ckpt"
            else:
                r["prov"] = "none"
            if (pu, pv) in ck_edge and ck_edge[(pu, pv)] is not None:
                r["ckpt_prob"] = float(ck_edge[(pu, pv)])
            su = [x for x in succ.get(pu, []) if x != pv]
            pvv = [x for x in pred.get(pv, []) if x != pu]
            if (pu, pv) in edge_set:
                r["topo"] = "present"
            else:
                r["topo"] = {(False, False): "break", (False, True): "v_taken", (True, False): "u_diverted",
                             (True, True): "swap"}[(bool(su), bool(pvv))]
            comp = [(pu, x) for x in su] + [(x, pv) for x in pvv]
            for e in comp:
                lv = lab.get(e, 0)
                r["comp_tp" if lv == 1 else ("comp_fp" if lv == 2 else "comp_ne")] += 1
        elif pu != -1:
            r["nbr_syn"] = any(x in syn for x in succ.get(pu, []))
            r["other_free"] = not succ.get(pu)
            # 1-frame gap bridge: p_u an end, v's single GT successor w matched to a track start at t+2
            ws = gt_succ.get(b, [])
            pw = inv.get(ws[0], [-1])[0] if len(ws) == 1 else -1
            r["bridge"] = bool(r["other_free"] and pw != -1 and not pred.get(pw) and f_t[pw] == f_t[pu] + 2)
        elif pv != -1:
            r["nbr_syn"] = any(x in syn for x in pred.get(pv, []))
            r["other_free"] = not pred.get(pv)
            us = gt_pred.get(a, [])
            pz = inv.get(us[0], [-1])[0] if len(us) == 1 else -1
            r["bridge"] = bool(r["other_free"] and pz != -1 and not succ.get(pz) and f_t[pz] == f_t[pv] - 2)
        # primary class
        if dt != 1:
            cls = "c_gt_skip"
        elif pu != -1 and pv != -1:
            cls = "c_gap_node" if (r["p_u_syn"] or r["p_v_syn"]) else f"b_{r['topo']}"
        elif r["nbr_syn"] or r["u_near_syn"] or r["v_near_syn"]:
            cls = "c_gap_node_off"
        else:
            cls = f"a_{r['u_reason'] or r['v_reason']}"
        r["cls"] = cls
        r["unmatched"] = "both" if pu == -1 and pv == -1 else ("u" if pu == -1 else ("v" if pv == -1 else ""))
        rows.append(r)

    # ---- candidate end -> start pairs (prediction side only) + labels
    t_max, t_min = max(f_t.values()), min(f_t.values())
    ends = [i for i in f_ids if not succ.get(i) and f_t[i] < t_max]
    starts = [i for i in f_ids if not pred.get(i) and f_t[i] > t_min]
    up, down = _chains(f_ids, f_t, succ, pred)
    cand = []
    starts_by_t: dict[int, list[int]] = {}
    for s in starts:
        starts_by_t.setdefault(f_t[s], []).append(s)
    ends_by_t: dict[int, list[int]] = {}
    for e in ends:
        ends_by_t.setdefault(f_t[e], []).append(e)
    R_C = float(settings["cand_um"])
    for t, es in ends_by_t.items():
        ss = starts_by_t.get(t + 1, [])
        if not ss:
            continue
        pe = f_pos[[f_row[e] for e in es]]
        ps = f_pos[[f_row[s] for s in ss]]
        dmat = np.linalg.norm(pe[:, None, :] - ps[None, :, :], axis=2)
        rank_s = np.argsort(np.argsort(dmat, axis=1), axis=1)   # rank of start j among starts for end i
        rank_e = np.argsort(np.argsort(dmat, axis=0), axis=0)   # rank of end i among ends for start j
        for i, e in enumerate(es):
            # velocity prediction from the end's own predecessor
            pr = pred.get(e, [])
            vel = f_pos[f_row[e]] - f_pos[f_row[pr[0]]] if len(pr) == 1 else None
            for j in np.nonzero(dmat[i] <= R_C)[0].tolist():
                s = ss[j]
                nx = succ.get(s, [])
                cand.append({
                    "stem": stem, "e": e, "s": s, "t": t, "dist_um": float(dmat[i, j]),
                    "pred_um": float(np.linalg.norm(ps[j] - (pe[i] + vel))) if vel is not None else np.nan,
                    "back_um": (float(np.linalg.norm(pe[i] - (ps[j] - (f_pos[f_row[nx[0]]] - ps[j]))))
                                if len(nx) == 1 else np.nan),
                    "ilp_p": float(ilp_probs[(e, s)]) if (e, s) in ilp_probs else np.nan,
                    "in_ckpt": (e, s) in ck_edge,
                    "ckpt_prob": (np.nan if ck_edge.get((e, s)) is None else float(ck_edge[(e, s)])),
                    "rank_s": int(rank_s[i, j]), "rank_e": int(rank_e[i, j]),
                    "n_s": len(ss), "n_e": len(es), "e_up": up[e], "s_down": down[s],
                    "e_syn": e in syn, "s_syn": s in syn, "e_isolated": not pred.get(e), "s_isolated": not succ.get(s),
                    "label": A._label_pair(e, s, match, gt_edge_set, gt_out, gt_in),
                })

    # ---- stitch rules: the replay / kernel function itself (bpk.STITCH_FN in the namespace) on this graph; added edges
    # labelled under the fixed matching (no node is added or removed, so edge TP/FP are exact)
    st_eval = {}
    for name, params in settings["stitch_rules"].items():
        st_stats: dict = {}
        _n, new_edges = ns["stitch_final_graph"](nodes, [dict(e) for e in edges], st_stats, dict(params),
                                                 dict(ilp_probs))
        labs = [A._label_pair(int(e["source_id"]), int(e["target_id"]), match, gt_edge_set, gt_out, gt_in)
                for e in new_edges[len(edges):]]
        st_eval[name] = {"added": len(labs), "tp_add": labs.count(1), "fp_add": labs.count(2)}

    check = {"fn": len(fn_edges), "metric_fn": int(row["edge_fn"]), "metric_tp": int(row["edge_tp"]),
             "label_tp": len(tp_gt), "multi_match_gt": multi, "gt_edges": len(gt_edges),
             "ends": len(ends), "starts": len(starts)}
    return {"stem": stem, "rows": rows, "cand": cand, "check": check, "row": row, "ef_stats": ef_stats,
            "st_eval": st_eval,
            "seconds": round(time.time() - started, 2)}


def _task(stem: str, settings: dict) -> dict:
    for attempt in range(4):  # Windows: antivirus can hold the freshly written GEFF directory (rename -> WinError 5)
        try:
            return fn_video(stem, settings)
        except PermissionError:
            if attempt == 3:
                raise
            import shutil
            import os

            shutil.rmtree(Path(settings["out"]) / "work" / str(os.getpid()), ignore_errors=True)
            time.sleep(2.0 * (attempt + 1))


# ------------------------------------------------------------------------------------------------ estimates
def oracle(fn, base_rows: dict, mask, steal: bool) -> dict:
    """Recover the masked FN edges: each becomes TP; with steal the competing edges (their official labels) are
    dropped first (unique per video)."""
    sub = fn.loc[mask]
    counts: dict[str, dict] = {}
    for stem, g in sub.groupby("stem"):
        c = {"tp_add": int(len(g)), "fp_drop": 0, "tp_drop": 0}
        if steal:
            c["fp_drop"] = int(g["comp_fp"].sum())
            c["tp_drop"] = int(g["comp_tp"].sum())
        counts[stem] = c
    out = {"edges": int(mask.sum())}
    for subset in ("all", "44b6", "6bba"):
        stems = [s for s in base_rows if subset == "all" or s.startswith(subset)]
        b = {s: base_rows[s] for s in stems}
        new = A.video_score_rows(counts, b)
        out[f"d_{subset}"] = A.summarise(new) - A.summarise(list(b.values()))
    return out


# ------------------------------------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", default=str(A.DEFAULT_CACHE))
    ap.add_argument("--replay-out", default=str(A.DEFAULT_REPLAY_OUT))
    ap.add_argument("--anatomy-out", default=str(A.DEFAULT_OUT), help="anatomy.py cache (relink rerun, matches)")
    ap.add_argument("--config", default="exp39")
    ap.add_argument("--ef", default="", help="edge filter params k=v,... applied post-tail (replay ef.* keys)")
    ap.add_argument("--tag", default="exp39")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--report-dir", default=str(HERE))
    ap.add_argument("--data-dir", default=str(R.pl.DEFAULT_DATA))
    ap.add_argument("--splits", default=str(R.DEFAULT_SPLITS))
    ap.add_argument("--validate-csv", default="", help="replay per_video csv[:config] to cross-check TP/FN")
    ap.add_argument("--cand-um", type=float, default=14.0, help="candidate radius (the ILP capture keeps <= 14 um)")
    ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    if a.workers > 3:
        raise SystemExit("at most 3 workers")
    import pandas as pd

    cache, out, replay_out = Path(a.cache).resolve(), Path(a.out).resolve(), Path(a.replay_out).resolve()
    tail_dir, cfg = A.tail_dir_for(a.config, replay_out)
    ef = {}
    match_key = tail_dir.name
    if a.ef:
        raw = {}
        for item in a.ef.split(","):
            k, _, v = item.partition("=")
            raw[k.strip()] = R._parse_value(v)
        ef = R.edgefilter_params("fn_anatomy", raw)
        match_key = f"{tail_dir.name}__ef_{R._fingerprint({'ef': ef, 'sha': R._edgefilter_sha()})[:10]}"
    stems = list(a.stems) or sorted(p.stem for p in (cache / "ckpt").glob("*.npz"))
    missing = [s for s in stems if not (tail_dir / f"{s}.npz").is_file()]
    if missing:
        raise SystemExit(f"{len(missing)} tails missing under {tail_dir}: run the replay for {a.config!r} first")
    anatomy_settings = {"cache": str(cache), "out": str(Path(a.anatomy_out).resolve()), "tail_dir": str(tail_dir),
                        "data_dir": str(Path(a.data_dir)), "ns_out": str(Path(a.anatomy_out).resolve() / "ns")}
    settings = {"cache": str(cache), "out": str(out), "tail_dir": str(tail_dir), "ef": ef, "match_key": match_key,
                "anatomy": anatomy_settings, "cand_um": a.cand_um, "stitch_rules": STITCH_RULES}
    out.mkdir(parents=True, exist_ok=True)
    print(f"tail {tail_dir}\nef {ef or 'off'} match key {match_key}\n{len(stems)} videos, {a.workers} workers", flush=True)

    results: dict[str, dict] = {}
    started = time.time()
    if a.workers <= 1:
        for s in stems:
            results[s] = _task(s, settings)
            print(f"  {s} {results[s]['seconds']} s {results[s]['check']}", flush=True)
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
                    if n % 20 == 0 or n == len(stems):
                        el = time.time() - started
                        print(f"  {n}/{len(stems)}  {el / 60:.1f} min  eta {el / n * (len(stems) - n) / 60:.1f} min",
                              flush=True)

    # ---- validation
    bad = {s: r["check"] for s, r in results.items()
           if r["check"]["fn"] != r["check"]["metric_fn"] or r["check"]["label_tp"] != r["check"]["metric_tp"]}
    csv_bad = {}
    if a.validate_csv:
        path, _, conf = a.validate_csv.partition(":")
        pv = pd.read_csv(path)
        if conf:
            pv = pv[pv["config"] == conf]
        ref = {r["dataset"]: r for r in pv.to_dict("records")}
        csv_bad = {s: (results[s]["check"]["fn"], int(ref[s]["edge_fn"])) for s in stems if s in ref
                   and (results[s]["check"]["fn"] != int(ref[s]["edge_fn"])
                        or int(results[s]["row"]["edge_fp"]) != int(ref[s]["edge_fp"]))}
        print(f"csv cross-check: {sum(s in ref for s in stems)} videos compared, {len(csv_bad)} differ", flush=True)
    tot_fn = sum(r["check"]["fn"] for r in results.values())
    tot_mfn = sum(r["check"]["metric_fn"] for r in results.values())
    multi = sum(r["check"]["multi_match_gt"] for r in results.values())
    print(f"VALIDATION: FN {tot_fn} vs metric edge_fn {tot_mfn}; mismatching videos {len(bad)}; "
          f"GT nodes with >1 match {multi}", flush=True)
    if bad or csv_bad:
        print(json.dumps({"metric": dict(list(bad.items())[:5]), "csv": dict(list(csv_bad.items())[:5])}, indent=1))
        raise SystemExit("FN validation FAILED")

    splits = json.loads(Path(a.splits).read_text(encoding="utf-8"))
    split_of = {s: "selection" for s in splits["selection"]} | {s: "confirmation" for s in splits["confirmation"]}
    fn = pd.DataFrame([r for s in stems for r in results[s]["rows"]])
    cand = pd.DataFrame([r for s in stems for r in results[s]["cand"]])
    for df in (fn, cand):
        df["embryo"] = df["stem"].str.split("_").str[0]
        df["split"] = df["stem"].map(split_of).fillna("none")
    fn.to_parquet(out / f"fn_{a.tag}.parquet", index=False)
    cand.to_parquet(out / f"cand_{a.tag}.parquet", index=False)
    base_rows = {s: {"dataset": s, **results[s]["row"]} for s in stems}
    base_score = A.summarise(list(base_rows.values()))
    print(f"wrote {out / f'fn_{a.tag}.parquet'} ({len(fn)} FN) and cand_{a.tag}.parquet ({len(cand)} pairs); "
          f"base score {base_score:.6f}", flush=True)

    # ---- class table
    def counts(mask) -> dict:
        m = np.asarray(mask, bool)
        return {"all": int(m.sum()), "44b6": int((m & (fn["embryo"] == "44b6")).sum()),
                "6bba": int((m & (fn["embryo"] == "6bba")).sum())}

    order = (["c_gt_skip", "c_gap_node", "c_gap_node_off"] + [f"a_{x}" for x in REASONS]
             + [f"b_{x}" for x in TOPOLOGIES])
    table = []
    for cls in order + sorted(set(fn["cls"]) - set(order)):
        m = (fn["cls"] == cls).to_numpy()
        if not m.any():
            continue
        e = {"class": cls, **counts(m), "gt_div": int((m & fn["gt_div"]).sum())}
        if cls.startswith(("b_", "c_gap_node")) and cls != "c_gap_node_off":
            for p in ("ilp", "ckpt", "none"):
                e[f"prov_{p}"] = int((m & (fn["prov"] == p)).sum())
            steal = cls not in ("b_break", "b_present")
            e["oracle"] = oracle(fn, base_rows, m, steal=steal)
            e["comp_tp"] = int(fn.loc[m, "comp_tp"].sum())
            e["comp_fp"] = int(fn.loc[m, "comp_fp"].sum())
        table.append(e)
    tot = counts(np.ones(len(fn), bool))

    # ---- break detail: distance / ILP bins and whether the pair is in the candidate table
    brk = fn[fn["cls"] == "b_break"].copy()
    brk_key = set(zip(brk["stem"], brk["p_u"], brk["p_v"]))
    cand["is_fn_break"] = [(s, e, t) in brk_key for s, e, t in zip(cand["stem"], cand["e"], cand["s"])]

    # ---- candidate label rates by feature bins (design table)
    def rate_rows(df, name, mask) -> dict:
        m = np.asarray(mask, bool)
        lab = df["label"].to_numpy()[m]
        return {"rule": name, "pairs": int(m.sum()), "TP": int((lab == 1).sum()), "FP": int((lab == 2).sum()),
                "NE": int((lab == 0).sum())}

    c = cand
    design = [rate_rows(c, "all end->start pairs <= %.0f um" % a.cand_um, np.ones(len(c), bool))]
    for lo, hi in ((0, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 8), (8, 10), (10, 12)):
        design.append(rate_rows(c, f"dist [{lo},{hi})", (c["dist_um"] >= lo) & (c["dist_um"] < hi)))
    ilp = c["ilp_p"].notna()
    design += [rate_rows(c, "ILP edge", ilp), rate_rows(c, "ILP edge & p>=0.7", ilp & (c["ilp_p"] >= 0.7)),
               rate_rows(c, "ILP edge & mutual NN", ilp & (c["rank_s"] == 0) & (c["rank_e"] == 0)),
               rate_rows(c, "no ILP edge & mutual NN", ~ilp & (c["rank_s"] == 0) & (c["rank_e"] == 0)),
               rate_rows(c, "no ILP & mutual NN & dist<4", ~ilp & (c["rank_s"] == 0) & (c["rank_e"] == 0)
                         & (c["dist_um"] < 4)),
               rate_rows(c, "no ILP & mutual NN & dist<6", ~ilp & (c["rank_s"] == 0) & (c["rank_e"] == 0)
                         & (c["dist_um"] < 6)),
               rate_rows(c, "ckpt edge (removed by tail)", c["in_ckpt"]),
               rate_rows(c, "e or s synthetic", c["e_syn"] | c["s_syn"])]
    # ---- stitch rules: exact edge counts -> official summarise per split x embryo, per-video gain fractions
    st_table = []
    for name, params in STITCH_RULES.items():
        e = {"rule": name, "params": params}
        counts = {s: results[s]["st_eval"][name] for s in stems}
        e["added"] = sum(c["added"] for c in counts.values())
        e["tp_add"] = sum(c["tp_add"] for c in counts.values())
        e["fp_add"] = sum(c["fp_add"] for c in counts.values())
        for split in ("all", "selection", "confirmation"):
            ss = [s for s in stems if split == "all" or split_of.get(s) == split]
            for emb in ("all", "44b6", "6bba"):
                se = [s for s in ss if emb == "all" or s.startswith(emb)]
                if not se:
                    e[f"d_{split}_{emb}"] = e[f"gain_{split}_{emb}"] = float("nan")
                    continue
                b = {s: base_rows[s] for s in se}
                new = {r["dataset"]: r for r in A.video_score_rows(counts, b)}
                e[f"d_{split}_{emb}"] = A.summarise(list(new.values())) - A.summarise(list(b.values()))
                e[f"gain_{split}_{emb}"] = sum(R._video_score(new[s]) > R._video_score(b[s]) + 1e-12
                                               for s in se) / len(se)
        st_table.append(e)
    summary = {"config": a.config, "ef": ef, "tag": a.tag, "videos": len(stems), "fn_total": tot_fn,
               "metric_fn_total": tot_mfn, "base_score": base_score, "classes": table, "totals": tot,
               "design": design, "stitch_rules": st_table, "ef_stats_total": {k: float(sum(float(r["ef_stats"].get(k, 0) or 0)
                                                                 for r in results.values()))
                                                    for k in {k for r in results.values() for k in r["ef_stats"]}}}
    R._atomic_text(Path(a.report_dir) / f"fn_anatomy_{a.tag}.json", R._dumps(summary, indent=1))

    lines = [f"# FN anatomy of the final `{a.config}`{' + ef ' + str(ef) if ef else ''} graph ({len(stems)} videos)", "",
             f"Validated: FN {tot_fn} = official edge_fn {tot_mfn} in every video; base score {base_score:.6f}.", "",
             "| class | FN all | share | 44b6 | 6bba | GT-division FN | prov ilp/ckpt/none | competitor TP/FP | "
             "oracle d all | d 44b6 | d 6bba |", "|---|---:|---:|---:|---:|---:|---|---|---:|---:|---:|"]
    for e in table:
        o = e.get("oracle") or {}
        prov = f"{e['prov_ilp']}/{e['prov_ckpt']}/{e['prov_none']}" if "prov_ilp" in e else ""
        comp = f"{e['comp_tp']}/{e['comp_fp']}" if "comp_tp" in e else ""
        f6 = (lambda x: f"{x:+.5f}" if x is not None else "")
        lines.append(f"| {e['class']} | {e['all']} | {e['all'] / max(1, tot['all']):.3f} | {e['44b6']} | {e['6bba']} | "
                     f"{e['gt_div']} | {prov} | {comp} | {f6(o.get('d_all'))} | {f6(o.get('d_44b6'))} | "
                     f"{f6(o.get('d_6bba'))} |")
    lines += ["", f"Totals: {tot}", "", "## End -> start candidate pairs (prediction side only; label under the fixed "
              "matching)", "", "| rule | pairs | TP | FP | NE | TP/(TP+FP) |", "|---|---:|---:|---:|---:|---:|"]
    for d in design:
        prec = d["TP"] / (d["TP"] + d["FP"]) if d["TP"] + d["FP"] else float("nan")
        lines.append(f"| {d['rule']} | {d['pairs']} | {d['TP']} | {d['FP']} | {d['NE']} | {prec:.3f} |")
    lines += ["", "## Stitch rules (tools/build_probe_kernel.py stitch_final_graph on this graph; exact edge counts, division "
              "term and node count held fixed)", "", "| rule | added | TP | FP | d all | d sel (6bba) | d conf | d conf 44b6 "
              "| d conf 6bba | conf videos gaining 44b6 / 6bba |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for e in st_table:
        lines.append(f"| {e['rule']} | {e['added']} | {e['tp_add']} | {e['fp_add']} | {e['d_all_all']:+.5f} | "
                     f"{e['d_selection_all']:+.5f} | {e['d_confirmation_all']:+.5f} | {e['d_confirmation_44b6']:+.5f} | "
                     f"{e['d_confirmation_6bba']:+.5f} | {e['gain_confirmation_44b6']:.2f} / "
                     f"{e['gain_confirmation_6bba']:.2f} |")
    det = fn["cls"].str.startswith("a_")
    lines += ["", f"Detection-side FN (a_*): {int(det.sum())}; the matched end is a free track end/start in "
              f"{int((det & fn['other_free']).sum())}; a 1-frame gap bridge (end at t, GT successor matched to a start "
              f"at t+2, or the mirror) in {int((det & fn['bridge']).sum())}."]
    R._atomic_text(Path(a.report_dir) / f"fn_anatomy_{a.tag}.md", "\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)
    print(f"done in {(time.time() - started) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
