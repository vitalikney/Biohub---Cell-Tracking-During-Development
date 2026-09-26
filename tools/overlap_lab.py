"""Gate G-B of the OVERLAP-CONSENSUS line: the disagreement-component splice on the lab's final graphs, official metric.

    nice -n 19 python tools/overlap_lab.py score --dumps _dl/exp64_a _dl/exp64_b \
        --out experiments/exp64_overlap_lab/results.json [--workers 3] [--reg-json <registration.json>] [--reg-cache <dir>]

Pre-registered gate (CONTEXT.md 2026-09-26 08:58 UTC, G-B): on the x138/K2 tails of the 44b6 train clips, the 44b6
per-embryo delta (spliced - unspliced) >= +0.002 with a leak-group bootstrap one-sided 95% lower bound > 0; 6bba: zero
changed edges; node count <= +0.5%; forks untouched; a per-leak-group table. FAIL -> the line stops.
Design: research/wf_ideas_v2/r2_research_overlap-consensus.json + its three verifiers; registration tools/overlap_reg.py
(GT-free, exact voxels), splice tools/overlap_splice.py (defaults = the design: margin 1 um, forks skipped, cap 0.5%).

Inputs: the lab kernels' dumps (tools/trainlab_io.py format; <dump>/trainlab/<stem>.npz final graph + <dump>/divins_dump/
<stem>.npz DaughterNet p). Only the FINAL graph is read (no notebook replay; tools/trainlab.py score is the parity tool).
Arms (graphs per clip):
  control            the kernel's final graph (exp64: x138 + safetail + lowrefine, insertion dump-only)
  control_splice     overlap splice on control
  ins35              #35 insertion replayed on control (tools/trainlab.insert35) = K2's graph (on exp64)
  ins35_splice       PRIMARY: overlap splice on ins35 = K6 = K2 + overlapcons
  ins35_splice_gap3  the transfer verifier's restriction (owner - non-owner >= 3, non-owner score < 8); info + own gate
  ins35_splice_csv   the splice run on the ins35 CSV rows (rounded coords; what a last-cell kernel pass sees)
The splice of every arm runs on ALL lab clips jointly with the registration pairs (overlap_reg on the local train zarrs
of the lab clips, or --reg-json). Scoring: tools/trainlab.py's official_eval (same calls) extended to return the division
events; per clip rows; pooled per embryo = official summarise for the edge part (adj edge J weighted by TP+FP+FN), and a
division Jaccard where every event is counted once: a GT division present in k lab clips (same global position through
the leak-group offsets) weighs 1/k per copy; a predicted FP fork weighs 1/(number of lab clips whose crop covers it).
Without overlaps this equals the official summarise exactly. The plain official summarise is reported next to it.
Bootstrap units = connected components of (splits.json leak groups U accepted registration pairs) over the lab clips
with >= 2 clips; clips alone in their component are a fixed stratum present in every replicate.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import overlap_splice as osp  # noqa: E402

SPLITS = ROOT / "experiments/l2_daughternet/splits.json"
GA_JSON = ROOT / "experiments/overlap_reg_train/ga_train.json"
TRAIN_DIR = ROOT / "biohub-cell-tracking-during-development/train"
if not TRAIN_DIR.is_dir() and (ROOT.parents[2] / "biohub-cell-tracking-during-development/train").is_dir():
    TRAIN_DIR = ROOT.parents[2] / "biohub-cell-tracking-during-development/train"  # run from a .claude/worktrees copy
EMBRYOS = ("44b6", "6bba")
BASE_ARMS = ("control", "ins35")
CFG_PRIMARY: dict = {}
CFG_GAP3 = {"min_gap": 3.0, "max_nonowner": 8.0}
SPLICE_ARMS = {"control_splice": ("control", CFG_PRIMARY, False), "ins35_splice": ("ins35", CFG_PRIMARY, False),
               "ins35_splice_gap3": ("ins35", CFG_GAP3, False), "ins35_splice_csv": ("ins35", CFG_PRIMARY, True)}
ARMS = ("control", "control_splice", "ins35", "ins35_splice", "ins35_splice_gap3", "ins35_splice_csv")
COMPARE = {"ins35_splice": "ins35", "ins35_splice_gap3": "ins35", "ins35_splice_csv": "ins35",
           "control_splice": "control", "ins35": "control"}
GATED = ("ins35_splice", "ins35_splice_gap3", "ins35_splice_csv", "control_splice")
PRIMARY = "ins35_splice"
DIV_WEIGHT = 0.1
ADJ_ALPHA = 0.1
GATE_DELTA = 0.002
GATE_NODE_FRAC = 0.005
BOOT_B = 10000
BOOT_SEED = 20260926
BOOT_Q = 0.05


# ----------------------------------------------------------------------------------------------------------------------
# graphs
# ----------------------------------------------------------------------------------------------------------------------
def slim(nodes: dict, edges: list) -> tuple[dict, list]:
    """Only what the writer, the splice and the metric use: nodes {id: t z y x} (dict order kept), edges (src, dst)."""
    return ({int(k): {"t": int(n["t"]), "z": float(n["z"]), "y": float(n["y"]), "x": float(n["x"])}
             for k, n in nodes.items()},
            [{"source_id": int(e["source_id"]), "target_id": int(e["target_id"])} for e in edges])


def load_clip(dump: Path, divins: Path | None) -> dict:
    """-> {'control', 'ins35' (slim graphs), 'ins35_stats', 'divins' bool, 'meta'} from the lab dumps of one clip."""
    import trainlab as tl
    import trainlab_io as tio
    with np.load(dump, allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files if k.startswith("final_") or k == "meta_json"}
    meta = json.loads(str(arrays["meta_json"]))
    nodes, edges = tio.trainlab_graph_from_arrays(arrays, "final_")
    out = {"control": slim(nodes, edges), "divins": False, "ins35_stats": None,
           "meta": {k: meta.get(k) for k in ("kernel_elapsed_s", "stage_seconds")}}
    node_p, _ = tl.node_p_from_divins(divins)
    if node_p is not None:
        e2, st = tl.insert35(nodes, edges, node_p)
        out["ins35"] = slim(nodes, e2)
        out["divins"] = True
        out["ins35_stats"] = {k: int(st.get(k, 0)) for k in ("divins_added", "divins_added_steal", "divins_triples",
                                                              "divins_missing_p")}
    else:
        out["ins35"] = out["control"]
    return out


def load_tail(path: Path) -> dict:
    """PROXY input: a local replay tail npz (.public_local_cache/l2_replay/<exp>/tail/<cfg>/<stem>.npz: node_id, t, zyx,
    src, dst) -> the same record as load_clip, with ins35 = control (no DaughterNet dump for these tails)."""
    with np.load(path, allow_pickle=False) as z:
        ids = np.asarray(z["node_id"]).reshape(-1).tolist()
        ts = np.asarray(z["t"]).reshape(-1).tolist()
        zyx = np.asarray(z["zyx"], dtype=np.float64).reshape(-1, 3).tolist()
        src = np.asarray(z["src"]).reshape(-1).tolist()
        dst = np.asarray(z["dst"]).reshape(-1).tolist()
    nodes = {int(i): {"t": int(t), "z": p[0], "y": p[1], "x": p[2]} for i, t, p in zip(ids, ts, zyx)}
    g = (nodes, [{"source_id": int(s), "target_id": int(d)} for s, d in zip(src, dst)])
    return {"control": g, "ins35": g, "divins": False, "ins35_stats": None, "meta": {"tail": str(path)}}


def writer_digest(g: tuple[dict, list]) -> str:
    import trainlab as tl
    return tl.writer_digest(*g)


def forks_of(edges: list) -> dict:
    kids: dict = defaultdict(list)
    for e in edges:
        kids[int(e["source_id"])].append(int(e["target_id"]))
    return {u: tuple(sorted(v)) for u, v in kids.items() if len(v) >= 2}


def edge_set(g) -> set:
    return {(int(e["source_id"]), int(e["target_id"])) for e in g[1]}


def csv_roundtrip(graphs: dict) -> dict:
    """The graphs as a last kernel cell would read them back from submission.csv (rounded non-negative voxels)."""
    rows = osp.rows_from_graphs(graphs)
    back = osp.graphs_from_rows(rows)
    return {k: back.get(k, ({}, [])) for k in graphs}


def splice_arm(graphs: dict, shapes: dict, pairs: list, cfg: dict, via_csv: bool = False) -> tuple[dict, dict, float]:
    """-> (spliced graphs, splice stats, seconds). via_csv: the input graphs go through the CSV writer first; then
    untouched clips keep their ORIGINAL float graph object (the kernel would rewrite nothing for them)."""
    t0 = time.perf_counter()
    src = csv_roundtrip(graphs) if via_csv else graphs
    out, st = osp.splice_all(src, shapes, pairs, cfg)
    if via_csv:
        out = {k: (out[k] if out[k] is not src[k] else graphs[k]) for k in graphs}
    return out, st, time.perf_counter() - t0


# ----------------------------------------------------------------------------------------------------------------------
# registration, units, global frames
# ----------------------------------------------------------------------------------------------------------------------
class _UF:
    def __init__(self, items=()):
        self.p = {x: x for x in items}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            if rb < ra:
                ra, rb = rb, ra
            self.p[rb] = ra


def units_of(stems: list, leak_groups: list, pairs: list) -> tuple[list, list]:
    """Connected components of (leak groups U registration pairs) restricted to `stems`.
    -> (units with >= 2 stems, sorted lists sorted by first stem; fixed = stems alone in their component)."""
    have = set(stems)
    uf = _UF(sorted(have))
    for g in leak_groups:
        members = sorted(set(g) & have)
        for s in members[1:]:
            uf.union(members[0], s)
    for p in pairs:
        if p["a"] in have and p["b"] in have:
            uf.union(p["a"], p["b"])
    comp: dict = defaultdict(list)
    for s in sorted(have):
        comp[uf.find(s)].append(s)
    units = sorted((sorted(v) for v in comp.values() if len(v) >= 2), key=lambda v: v[0])
    fixed = sorted(v[0] for v in comp.values() if len(v) == 1)
    return units, fixed


def global_frames(stems: list, links: list, pairs: list) -> tuple[dict, int]:
    """Origin of every clip in its component's frame: point p in clip c sits at p + g[c]. Sources: GT links of
    splits.json (offset_tzyx_a_minus_b) first, then registration pairs (offset = coord_a - coord_b); with p_a = p_b + o
    -> g[b] = g[a] + o. -> ({stem: (root, (dt, dz, dy, dx))}, number of inconsistent redundant offsets)."""
    have = set(stems)
    adj: dict = defaultdict(list)
    for L in links:
        a, b, o = L["a"], L["b"], [int(x) for x in L["offset_tzyx_a_minus_b"]]
        if a in have and b in have:
            adj[a].append((b, o))
            adj[b].append((a, [-x for x in o]))
    for p in pairs:
        a, b, o = p["a"], p["b"], [int(x) for x in p["offset"]]
        if a in have and b in have:
            adj[a].append((b, o))
            adj[b].append((a, [-x for x in o]))
    out: dict = {}
    bad = 0
    for s in sorted(have):
        if s in out:
            continue
        out[s] = (s, (0, 0, 0, 0))
        stack = [s]
        while stack:
            u = stack.pop()
            gu = out[u][1]
            for v, o in adj[u]:
                gv = tuple(gu[k] + o[k] for k in range(4))
                if v in out:
                    bad += int(out[v][1] != gv)
                else:
                    out[v] = (s, gv)
                    stack.append(v)
    return out, bad // 2


def run_registration(stems: list, train_dir: Path, workers: int, cache: str | None, log=print) -> dict:
    """overlap_reg on the local train zarrs of the lab clips (GT-free; cross-prefix pairs allowed and reported)."""
    import overlap_reg as reg
    paths = [Path(train_dir) / f"{s}.zarr" for s in stems]
    t0 = time.time()
    anchors = reg.anchors_mp(paths, workers=workers, backend="sparse", cache=cache, log=None)
    readers, shapes = {}, {}
    for p in paths:
        readers[p.name[:-5]], shapes[p.name[:-5]] = reg.zarr_video(p)
    res = reg.register(anchors, readers, shapes)
    res["stats"]["anchor_wall_s"] = round(time.time() - t0, 1)
    res["source"] = f"overlap_reg on {len(stems)} lab clips ({train_dir})"
    log(f"REGISTRATION accepted {res['stats']['accepted']} pairs (cross-prefix {res['stats']['accepted_cross_prefix']})"
        f" in {res['stats']['anchor_wall_s']} s")
    return res


# ----------------------------------------------------------------------------------------------------------------------
# official metric with division events
# ----------------------------------------------------------------------------------------------------------------------
def eval_clip(nodes: dict, edges: list, gt_geff) -> dict:
    """tools/trainlab.official_eval (same calls, same order) plus the division events:
    -> {'row', 'gt_div': [[t, z, y, x, tp]], 'fp_fork': [[t, z, y, x]], 'tp_fork_n'} (GT positions from the geff,
    fork positions = the writer's rounded pred node)."""
    import polars as pl
    import score_geffs as sg  # puts tools/official on sys.path
    import tracksdata as td
    from tracking_cellmot import division_metrics as D
    from tracking_cellmot import metrics as M

    gt, scale = sg._load_gt_and_scale(Path(gt_geff))
    n_total = sg._estimated_n_total(Path(gt_geff))
    g = td.graph.IndexedRXGraph()
    for key in ("z", "y", "x"):
        g.add_node_attr_key(key, pl.Float64, 0.0)
    ids = sorted(int(i) for i in nodes)
    wpos = {i: (int(nodes[i]["t"]), float(max(0, int(round(float(nodes[i]["z"]))))),
                float(max(0, int(round(float(nodes[i]["y"]))))), float(max(0, int(round(float(nodes[i]["x"]))))))
            for i in ids}
    if ids:
        g.bulk_add_nodes([{"t": wpos[i][0], "z": wpos[i][1], "y": wpos[i][2], "x": wpos[i][3]} for i in ids],
                         indices=ids)
    if edges:
        g.bulk_add_edges([{"source_id": int(e["source_id"]), "target_id": int(e["target_id"])} for e in edges])
    M._evaluate(g, gt, "jaccard", scale, 7.0)
    if g.num_edges() == 0:
        tp, fp, fn = 0, 0, gt.num_edges()
    else:
        ea = M._evaluate_matched_graph(g, gt)
        tp = int(ea[td.DEFAULT_ATTR_KEYS.MATCHED_EDGE_MASK].sum())
        fp = int(ea["pred_valid"].sum()) - tp
        fn = gt.num_edges() - tp
    div = D.score_divisions(g, gt, scale=scale, max_distance=7.0)
    dtp = sum(div.scores.values())
    er = M.EvaluationResult(edge_tp=tp, edge_fp=fp, edge_fn=fn, division_tp=dtp, division_fn=len(div.scores) - dtp,
                            division_fp=len(div.fp_forks), num_pred_nodes=g.num_nodes())
    rec = M.node_recall(g, gt) if g.num_edges() > 0 and g.num_nodes() > 0 else 0.0
    row = M.per_sample_metrics(er, n_total, rec)
    gt_div = []
    if div.scores:
        nid = td.DEFAULT_ATTR_KEYS.NODE_ID
        df = gt.node_attrs(attr_keys=[nid, "t", "z", "y", "x"])
        gpos = {int(r[nid]): (int(r["t"]), float(r["z"]), float(r["y"]), float(r["x"])) for r in df.iter_rows(named=True)}
        gt_div = [[*gpos[int(d)], int(s)] for d, s in sorted(div.scores.items())]
    fp_fork = [list(wpos[int(u)]) for u in sorted(div.fp_forks)]
    return {"row": row, "gt_div": gt_div, "fp_fork": fp_fork, "tp_fork_n": len(div.tp_forks)}


def _eval_task(task: dict) -> dict:
    t0 = time.time()
    r = eval_clip(task["nodes"], task["edges"], task["gt"])
    r["stem"], r["digest"], r["seconds"] = task["stem"], task["digest"], round(time.time() - t0, 1)
    return r


# ----------------------------------------------------------------------------------------------------------------------
# division weights (every event once), pooling, bootstrap
# ----------------------------------------------------------------------------------------------------------------------
def _gkey(p, g) -> tuple:
    return (int(p[0]) + g[0], round(float(p[1]) + g[1], 3), round(float(p[2]) + g[2], 3), round(float(p[3]) + g[3], 3))


def division_weights(ev: dict, frames: dict, shapes: dict) -> dict:
    """ev {stem: {'gt_div': [[t,z,y,x,tp]], 'fp_fork': [[t,z,y,x]]}} of ONE arm -> {stem: (w_tp, w_fp, w_fn)}.
    A GT division at the same global position in k clips weighs 1/k per copy; an FP fork weighs 1/(clips of its
    component whose crop covers its global position, >= 1)."""
    count: dict = defaultdict(int)
    members: dict = defaultdict(list)
    for s in ev:
        root, g = frames.get(s, (s, (0, 0, 0, 0)))
        members[root].append(s)
        for key in {_gkey(d[:4], g) for d in ev[s]["gt_div"]}:
            count[(root, key)] += 1
    out = {}
    for s in ev:
        root, g = frames.get(s, (s, (0, 0, 0, 0)))
        wtp = wfn = wfp = 0.0
        for d in ev[s]["gt_div"]:
            w = 1.0 / max(1, count[(root, _gkey(d[:4], g))])
            if int(d[4]):
                wtp += w
            else:
                wfn += w
        for f in ev[s]["fp_fork"]:
            gp = (f[0] + g[0], f[1] + g[1], f[2] + g[2], f[3] + g[3])
            k = 0
            for c in members[root]:
                gc = frames.get(c, (c, (0, 0, 0, 0)))[1]
                if c == s or (c in shapes and osp.inside((gp[0] - gc[0], gp[1] - gc[1], gp[2] - gc[2], gp[3] - gc[3]),
                                                         shapes[c])):
                    k += 1
            wfp += 1.0 / max(1, k)
        out[s] = (wtp, wfp, wfn)
    return out


def _jac(tp, fp, fn):
    d = tp + fp + fn
    return tp / d if d > 0 else float("nan")


def pooled(recs: list, mult=None) -> dict:
    """recs [{'row': per_sample_metrics row, 'div_w': (tp, fp, fn)}], mult = per-rec multiplicities (bootstrap).
    adj edge J = official weighting (TP+FP+FN per clip, NaN rows skipped); division J from the weighted events;
    score = adj + 0.1 div J (div J NaN -> adj, as the official summarise). score_nomult: the same with every clip's
    node-count multiplier removed (edge J instead of adj edge J, same weights): fewer nodes ALWAYS raise the
    multiplier (adj = J (1 - 0.1 (N - N_total) / N_total)), so a net-deleting splice gains there without fixing edges."""
    mult = [1] * len(recs) if mult is None else list(mult)
    sw = swa = swj = 0.0
    tp = fp = fn = 0.0
    dtp = dfp = dfn = 0.0
    nodes = 0.0
    for r, m in zip(recs, mult):
        if not m:
            continue
        row = r["row"]
        if row["edge_tp"] != row["edge_tp"]:
            continue
        w = row["edge_tp"] + row["edge_fp"] + row["edge_fn"]
        tp, fp, fn = tp + m * row["edge_tp"], fp + m * row["edge_fp"], fn + m * row["edge_fn"]
        nodes += m * row["num_pred_nodes"]
        if row["adj_edge_jaccard"] == row["adj_edge_jaccard"]:
            sw += m * w
            swa += m * w * row["adj_edge_jaccard"]
            swj += m * w * row["edge_jaccard"]
        a, b, c = r["div_w"]
        dtp, dfp, dfn = dtp + m * a, dfp + m * b, dfn + m * c
    adj = swa / sw if sw > 0 else float("nan")
    dj = _jac(dtp, dfp, dfn)
    score = adj + DIV_WEIGHT * dj if dj == dj else adj
    ej = swj / sw if sw > 0 else float("nan")
    return {"score": score, "score_nomult": ej + DIV_WEIGHT * dj if dj == dj else ej, "adj_edge_jaccard": adj, "edge_jaccard": _jac(tp, fp, fn), "division_jaccard": dj,
            "edge_tp": tp, "edge_fp": fp, "edge_fn": fn, "div_tp_w": dtp, "div_fp_w": dfp, "div_fn_w": dfn,
            "nodes": nodes}


def bootstrap_delta(units: list, fixed: list, recs_new: dict, recs_old: dict, b: int = BOOT_B, seed: int = BOOT_SEED,
                    q: float = BOOT_Q) -> dict:
    """Unit bootstrap of the pooled delta score(new) - score(old): units resampled with replacement, the fixed
    stratum in every replicate. -> {'lower', 'upper' (one-sided q quantiles), 'mean', 'b', 'units'}."""
    order = [s for u in units for s in u] + list(fixed)
    idx_of_unit = []
    pos = 0
    for u in units:
        idx_of_unit.append(list(range(pos, pos + len(u))))
        pos += len(u)
    rn = [recs_new[s] for s in order]
    ro = [recs_old[s] for s in order]
    base = pooled(rn)["score"] - pooled(ro)["score"]
    if not units:
        return {"point": base, "lower": base, "upper": base, "mean": base, "b": 0, "units": 0}
    rng = np.random.default_rng(seed)
    n_fixed = len(fixed)
    vals = np.empty(b)
    for k in range(b):
        pick = rng.integers(0, len(units), size=len(units))
        cnt = np.bincount(pick, minlength=len(units))
        mult = []
        for ui, c in enumerate(cnt):
            mult += [int(c)] * len(idx_of_unit[ui])
        mult += [1] * n_fixed
        vals[k] = pooled(rn, mult)["score"] - pooled(ro, mult)["score"]
    return {"point": base, "lower": float(np.quantile(vals, q)), "upper": float(np.quantile(vals, 1 - q)),
            "mean": float(vals.mean()), "b": b, "units": len(units), "q": q}


# ----------------------------------------------------------------------------------------------------------------------
# CSV-level sanity
# ----------------------------------------------------------------------------------------------------------------------
def graph_checks(g: tuple[dict, list], shape=None) -> dict:
    """Validity of one dataset's rows as the writer emits them."""
    nodes, edges = g
    pairs = [(int(e["source_id"]), int(e["target_id"])) for e in edges]
    indeg: dict = defaultdict(int)
    outdeg: dict = defaultdict(int)
    for s, t in pairs:
        indeg[t] += 1
        outdeg[s] += 1
    dangling = sum(1 for s, t in pairs if s not in nodes or t not in nodes)
    bad_dt = sum(1 for s, t in pairs if s in nodes and t in nodes and int(nodes[t]["t"]) != int(nodes[s]["t"]) + 1)
    outside = 0
    if shape is not None:
        for n in nodes.values():
            p = (int(n["t"]), max(0, int(round(float(n["z"])))), max(0, int(round(float(n["y"])))),
                 max(0, int(round(float(n["x"])))))
            outside += int(not all(0 <= v < s for v, s in zip(p, shape)))
    return {"nodes": len(nodes), "edges": len(pairs), "dup_edges": len(pairs) - len(set(pairs)),
            "self_loops": sum(1 for s, t in pairs if s == t), "dangling": dangling, "dt_not_1": bad_dt,
            "indeg_gt1": sum(1 for v in indeg.values() if v > 1), "outdeg_gt2": sum(1 for v in outdeg.values() if v > 2),
            "outside_crop": outside}


def csv_sanity(old: dict, new: dict, shapes: dict) -> dict:
    """old/new {stem: graph}: validity of the new rows, row-level diff, 6bba byte identity."""
    import trainlab as tl
    per = {}
    tot = defaultdict(int)
    for s in sorted(old):
        ro, rn = tl.writer_rows(*old[s]), tl.writer_rows(*new[s])
        chk = graph_checks(new[s], shapes.get(s))
        lo, ln = set(ro.decode().splitlines()), set(rn.decode().splitlines())
        rec = {"identical": ro == rn, "rows_removed": len(lo - ln), "rows_added": len(ln - lo), **chk}
        per[s] = rec
        for k in ("dup_edges", "self_loops", "dangling", "dt_not_1", "indeg_gt1", "outdeg_gt2", "outside_crop",
                  "rows_removed", "rows_added"):
            tot[k] += rec[k]
        tot["changed_datasets"] += int(not rec["identical"])
    bad_new = {s: {k: v for k, v in r.items() if k in ("dup_edges", "self_loops", "dangling", "indeg_gt1",
                                                         "outdeg_gt2") and v}
               for s, r in per.items()}
    bad_new = {s: v for s, v in bad_new.items() if v}
    old_bad = {s: graph_checks(old[s]) for s in old}
    introduced = {s: v for s, v in bad_new.items()
                  if any(v[k] > old_bad[s].get(k, 0) for k in v)}
    return {"totals": dict(tot), "invalid_introduced": introduced,
            "6bba_changed": sorted(s for s, r in per.items() if s.startswith("6bba") and not r["identical"]),
            "per_clip": per}


def read_kernel_csv(path: Path, stems: set) -> dict:
    """The lab kernel's own submission.csv -> {dataset: (node rows set, edge rows sorted)} for `stems`."""
    out: dict = defaultdict(lambda: (set(), []))
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ds = r["dataset"]
            if ds not in stems:
                continue
            if r["row_type"] == "node":
                out[ds][0].add((int(r["node_id"]), int(r["t"]), int(float(r["z"])), int(float(r["y"])),
                                int(float(r["x"]))))
            else:
                out[ds][1].append((int(r["source_id"]), int(r["target_id"])))
    return dict(out)


def kernel_csv_parity(graph: tuple[dict, list], rows) -> bool:
    nodes, edges = graph
    mine = {(int(i), int(n["t"]), max(0, int(round(float(n["z"])))), max(0, int(round(float(n["y"])))),
             max(0, int(round(float(n["x"]))))) for i, n in nodes.items()}
    return mine == rows[0] and sorted((int(e["source_id"]), int(e["target_id"])) for e in edges) == sorted(rows[1])


# ----------------------------------------------------------------------------------------------------------------------
# gate
# ----------------------------------------------------------------------------------------------------------------------
def gate_gb(arm: str, base: str, d44: float | None, boot: dict | None, node_frac_clip: dict, node_frac_44: float | None,
            forks_changed: list, sixbba_changed_edges: int, sixbba_pairs: int, sixbba_clips: int) -> dict:
    """The pre-registered G-B checks (CONTEXT.md 2026-09-26 08:58 UTC) for `arm` vs `base`."""
    worst = max(node_frac_clip.values()) if node_frac_clip else 0.0
    checks = {
        f"44b6_delta_ge_+{GATE_DELTA}": d44 is not None and d44 == d44 and d44 >= GATE_DELTA,
        "bootstrap_one_sided_95_lower_gt_0": boot is not None and boot.get("units", 0) > 0 and boot["lower"] > 0,
        "6bba_zero_changed_edges": sixbba_changed_edges == 0 and sixbba_pairs == 0,
        f"node_count_le_+{GATE_NODE_FRAC:.1%}_each_clip_and_pooled": worst <= GATE_NODE_FRAC + 1e-12
        and (node_frac_44 is None or node_frac_44 <= GATE_NODE_FRAC + 1e-12),
        "forks_untouched": not forks_changed,
    }
    return {"arm": arm, "base": base, "checks": checks, "pass": all(checks.values()), "44b6_delta": d44,
            "bootstrap": boot, "worst_clip_node_frac": worst, "pooled_44b6_node_frac": node_frac_44,
            "forks_changed_clips": forks_changed, "6bba_changed_edges": sixbba_changed_edges,
            "6bba_accepted_pairs": sixbba_pairs, "6bba_clips_in_lab": sixbba_clips,
            "note": ("6bba check = no accepted 6bba registration pair (lab clips and the G-A train-wide file) and no "
                     "changed edge on any 6bba lab clip; with no 6bba clip in the dumps only the registration half is "
                     "measured here")}


# ----------------------------------------------------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------------------------------------------------
def find_dump(roots: list, sub: str, stem: str) -> Path | None:
    for root in roots:
        for cand in (root / sub / f"{stem}.npz", root / f"{stem}.npz" if root.name == sub else None):
            if cand is not None and cand.is_file():
                return cand
    return None


def lab_stems(roots: list) -> list:
    out = set()
    for root in roots:
        for d in (root / "trainlab", root):
            if d.is_dir():
                out.update(p.stem for p in d.glob("*.npz") if p.stem[:4] in EMBRYOS)
    return sorted(out)


def _fmt(x, nd=4, sign=False):
    if x is None or (isinstance(x, float) and x != x):
        return "-"
    if isinstance(x, (int, np.integer)) and not isinstance(x, bool):
        return f"{x:+d}" if sign else str(x)
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def cmd_score(a) -> dict:
    t_start = time.time()
    roots = [Path(p) for p in (a.dumps or [])]
    tails = Path(a.tails) if a.tails else None
    if (tails is None) == (not roots):
        raise SystemExit("give exactly one of --dumps (lab kernel output) or --tails (local replay tails, PROXY)")
    stems = lab_stems(roots) if roots else sorted(p.stem for p in tails.glob("*.npz") if p.stem[:4] in EMBRYOS)
    if a.only:
        stems = [s for s in stems if s in set(a.only.split(","))]
    if a.embryo != "all":
        stems = [s for s in stems if s.startswith(a.embryo)]
    if not stems:
        raise SystemExit(f"no trainlab dumps under {roots}")
    splits = json.loads(Path(a.splits).read_text(encoding="utf-8"))["meta"]
    leak_groups, links = splits["leak_groups"], splits["shared_annotation_links"]
    group_of = {s: gi for gi, g in enumerate(leak_groups) for s in g}
    print(f"{len(stems)} lab clips ({', '.join(f'{e} {sum(s.startswith(e) for s in stems)}' for e in EMBRYOS)})",
          flush=True)

    # graphs
    clips: dict = {}
    for s in stems:
        clips[s] = load_clip(find_dump(roots, "trainlab", s), find_dump(roots, "divins_dump", s)) if roots \
            else load_tail(tails / f"{s}.npz")
    no_divins = [s for s in stems if not clips[s]["divins"]]
    shapes = {}
    import overlap_reg as reg
    for s in stems:
        shapes[s] = reg.zarr_video(Path(a.train_dir) / f"{s}.zarr")[1]

    # registration
    if a.reg_json:
        regres = json.loads(Path(a.reg_json).read_text(encoding="utf-8"))
        regres["source"] = f"--reg-json {a.reg_json}"
    else:
        regres = run_registration(stems, Path(a.train_dir), a.reg_workers, a.reg_cache)
    pairs = [p for p in regres["pairs"] if p["a"] in clips and p["b"] in clips]
    six_pairs = [p for p in pairs if p["a"].startswith("6bba") or p["b"].startswith("6bba")]
    ga_six = None
    if a.ga_json and Path(a.ga_json).is_file():
        ga = json.loads(Path(a.ga_json).read_text(encoding="utf-8"))
        ga_six = sum(1 for p in ga["pairs"] if p["a"].startswith("6bba") or p["b"].startswith("6bba"))
    units, fixed = units_of(stems, leak_groups, pairs)
    frames, frame_bad = global_frames(stems, links, pairs)
    print(f"{len(pairs)} accepted pairs among lab clips; {len(units)} bootstrap units, {len(fixed)} fixed clips",
          flush=True)

    # arms
    graphs = {arm: {s: clips[s][arm] for s in stems} for arm in BASE_ARMS}
    splice_info = {}
    for arm, (base, cfg, via_csv) in SPLICE_ARMS.items():
        out, st, sec = splice_arm(graphs[base], shapes, pairs, cfg, via_csv)
        graphs[arm] = out
        splice_info[arm] = {"base": base, "cfg": cfg, "via_csv": via_csv, "seconds": round(sec, 2),
                            "total": st["total"], "per_pair": st["per_pair"]}
        print(f"  {arm}: videos changed {st['total']['videos_changed']}, spliced {st['total']['spliced']}, "
              f"nodes +{st['total']['nodes_added']}/-{st['total']['nodes_removed']} ({sec:.1f} s)", flush=True)

    # scoring (identical writer rows are scored once per clip)
    digests = {arm: {s: writer_digest(graphs[arm][s]) for s in stems} for arm in graphs}
    evals: dict = {}
    if not a.no_score:
        tasks, seen = [], set()
        for s in stems:
            for arm in ARMS:
                d = digests[arm][s]
                if (s, d) in seen:
                    continue
                seen.add((s, d))
                nodes, edges = graphs[arm][s]
                tasks.append({"stem": s, "digest": d, "nodes": nodes, "edges": edges,
                              "gt": str(Path(a.train_dir) / f"{s}.geff")})
        print(f"scoring {len(tasks)} (clip, graph) pairs with {a.workers} worker(s)", flush=True)
        t0 = time.time()
        if a.workers > 1:
            from multiprocessing import get_context
            with get_context("spawn").Pool(a.workers) as pool:
                for k, r in enumerate(pool.imap_unordered(_eval_task, tasks, chunksize=1)):
                    evals[(r["stem"], r["digest"])] = r
                    if (k + 1) % 20 == 0:
                        print(f"  {k + 1}/{len(tasks)} ({time.time() - t0:.0f} s)", flush=True)
        else:
            for k, t in enumerate(tasks):
                r = _eval_task(t)
                evals[(r["stem"], r["digest"])] = r
                if (k + 1) % 20 == 0:
                    print(f"  {k + 1}/{len(tasks)} ({time.time() - t0:.0f} s)", flush=True)

    # per clip
    per_clip = []
    recs: dict = {arm: {} for arm in ARMS}
    forks0 = {arm: {s: forks_of(graphs[arm][s][1]) for s in stems} for arm in ARMS}
    for arm in ARMS:
        if a.no_score:
            break
        ev = {s: evals[(s, digests[arm][s])] for s in stems}
        w = division_weights(ev, frames, shapes)
        for s in stems:
            recs[arm][s] = {"row": ev[s]["row"], "div_w": w[s]}
    for s in stems:
        rec = {"stem": s, "embryo": s[:4], "leak_group": group_of.get(s), "divins": clips[s]["divins"],
               "ins35_stats": clips[s]["ins35_stats"], "shape": list(shapes[s]),
               "unit": next((u[0] for u in units if s in u), None), "arms": {}}
        for arm in ARMS:
            g = graphs[arm][s]
            ar = {"digest": digests[arm][s][:16], "nodes": len(g[0]), "edges": len(g[1]), "forks": len(forks0[arm][s])}
            if not a.no_score:
                e = evals[(s, digests[arm][s])]
                one = pooled([{"row": e["row"], "div_w": (sum(d[4] for d in e["gt_div"]), len(e["fp_fork"]),
                                                          sum(1 - d[4] for d in e["gt_div"]))}])
                ar.update({"row": e["row"], "score": one["score"], "div_w": list(recs[arm][s]["div_w"]),
                           "gt_div_n": len(e["gt_div"]), "fp_fork_n": len(e["fp_fork"]), "tp_fork_n": e["tp_fork_n"]})
            base = COMPARE.get(arm)
            if base:
                ar["changed"] = digests[arm][s] != digests[base][s]
                gb = graphs[base][s]
                es, eb = edge_set(g), edge_set(gb)
                ar["edges_changed"] = len(es ^ eb)
                ar["node_delta"] = len(g[0]) - len(gb[0])
                ar["node_frac"] = (len(g[0]) - len(gb[0])) / max(1, len(gb[0]))
                ar["forks_changed"] = forks0[arm][s] != forks0[base][s]
                if not a.no_score and "score" in rec["arms"].get(base, {}):
                    ar["delta"] = ar["score"] - rec["arms"][base]["score"]
            rec["arms"][arm] = ar
        per_clip.append(rec)

    res: dict = {"generated_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime()),
                 "dumps": [str(r) for r in roots] or [f"PROXY tails {tails} (ins35 arms = control arms)"],
                 "n_clips": len(stems), "clips_per_embryo": {e: sum(s.startswith(e) for s in stems) for e in EMBRYOS},
                 "no_divins_dump": no_divins,
                 "registration": {"source": regres.get("source"), "stats": regres.get("stats"),
                                  "pairs_in_lab": [{k: p[k] for k in ("a", "b", "offset", "votes", "n_frames",
                                                                      "spatial_frac")} for p in pairs],
                                  "6bba_pairs_in_lab": len(six_pairs), "6bba_pairs_ga_train": ga_six},
                 "units": units, "fixed_clips": fixed, "frame_inconsistencies": frame_bad,
                 "config": {"primary": {**osp.DEFAULTS, **CFG_PRIMARY}, "gap3": {**osp.DEFAULTS, **CFG_GAP3}},
                 "splice": {k: {kk: vv for kk, vv in v.items() if kk != "per_pair"} for k, v in splice_info.items()},
                 "splice_per_pair": {k: v["per_pair"] for k, v in splice_info.items()}}

    # pooled + gates
    if not a.no_score:
        import trainlab as tl
        pool_res: dict = {}
        for arm in ARMS:
            pool_res[arm] = {}
            for emb in EMBRYOS:
                ss = [s for s in stems if s.startswith(emb)]
                if not ss:
                    continue
                p = pooled([recs[arm][s] for s in ss])
                plain = tl.summarise_rows([recs[arm][s]["row"] for s in ss])
                p["plain_official"] = {k: plain.get(k) for k in ("score", "adj_edge_jaccard", "division_jaccard",
                                                                 "division_tp", "division_fp", "division_fn")}
                p["clips"] = len(ss)
                pool_res[arm][emb] = p
        deltas: dict = {}
        for arm, base in COMPARE.items():
            deltas[f"{arm}-{base}"] = {}
            for emb in pool_res[arm]:
                n, o = pool_res[arm][emb], pool_res[base][emb]
                ss = [s for s in stems if s.startswith(emb)]
                deltas[f"{arm}-{base}"][emb] = {
                    "score": n["score"] - o["score"], "adj_edge_jaccard": n["adj_edge_jaccard"] - o["adj_edge_jaccard"],
                    "edge_jaccard": n["edge_jaccard"] - o["edge_jaccard"],
                    "multiplier_term": (n["adj_edge_jaccard"] - o["adj_edge_jaccard"])
                    - (n["edge_jaccard"] - o["edge_jaccard"]),
                    "division_jaccard": (n["division_jaccard"] - o["division_jaccard"])
                    if n["division_jaccard"] == n["division_jaccard"] else None,
                    "plain_official_score": n["plain_official"]["score"] - o["plain_official"]["score"],
                    "score_nomult": n["score_nomult"] - o["score_nomult"],
                    "edge_tp": n["edge_tp"] - o["edge_tp"], "edge_fp": n["edge_fp"] - o["edge_fp"],
                    "edge_fn": n["edge_fn"] - o["edge_fn"], "nodes": n["nodes"] - o["nodes"],
                    "node_frac": (n["nodes"] - o["nodes"]) / o["nodes"] if o["nodes"] else None,
                    "div_tp_w": n["div_tp_w"] - o["div_tp_w"], "div_fp_w": n["div_fp_w"] - o["div_fp_w"],
                    "clips_changed": sum(1 for r in per_clip if r["embryo"] == emb and r["arms"][arm]["changed"]),
                    "wins": sum(1 for r in per_clip if r["embryo"] == emb and (r["arms"][arm].get("delta") or 0) > 0),
                    "losses": sum(1 for r in per_clip if r["embryo"] == emb and (r["arms"][arm].get("delta") or 0) < 0),
                    "clips": len(ss)}
        # per leak group / unit table (44b6)
        g0 = next((u for u in units if set(u) & set(leak_groups[0])), None) if leak_groups else None
        tables: dict = {}
        boots: dict = {}
        gates: dict = {}
        s44 = [s for s in stems if s.startswith("44b6")]
        units44 = [u for u in units if u[0].startswith("44b6")]
        fixed44 = [s for s in fixed if s.startswith("44b6")]
        for arm in GATED:
            base = COMPARE[arm]
            rows = []
            for u in units44 + [[s] for s in fixed44]:
                pn, po = pooled([recs[arm][s] for s in u]), pooled([recs[base][s] for s in u])
                rows.append({"unit": u[0], "clips": len(u), "leak_groups": sorted({group_of[s] for s in u
                                                                                   if s in group_of}),
                             "pairs": sum(1 for p in pairs if p["a"] in u and p["b"] in u),
                             "spliced": sum(pp["spliced"] for pp in splice_info[arm]["per_pair"]
                                            if pp["a"] in u and pp["b"] in u),
                             "delta": pn["score"] - po["score"], "edge_tp": pn["edge_tp"] - po["edge_tp"],
                             "edge_fp": pn["edge_fp"] - po["edge_fp"], "edge_fn": pn["edge_fn"] - po["edge_fn"],
                             "nodes": pn["nodes"] - po["nodes"],
                             "clip_wins": sum(1 for r in per_clip if r["stem"] in u and (r["arms"][arm].get("delta") or 0) > 0),
                             "clip_losses": sum(1 for r in per_clip if r["stem"] in u and (r["arms"][arm].get("delta") or 0) < 0)})
            tables[arm] = [r for r in rows if r["clips"] > 1 or r["pairs"] or abs(r["delta"]) > 0]
            boot = bootstrap_delta(units44, fixed44, recs[arm], recs[base], b=a.boot) if s44 else None
            ex0 = None
            if g0 is not None and s44:
                keep = [s for s in s44 if s not in g0]
                ex0 = pooled([recs[arm][s] for s in keep])["score"] - pooled([recs[base][s] for s in keep])["score"] \
                    if keep else None
            nz = [r for r in rows if r["clips"] > 1 and r["delta"] != 0]
            boots[arm] = {"bootstrap": boot, "delta_without_leak_group_0_unit": ex0,
                          "units_positive": sum(1 for r in nz if r["delta"] > 0), "units_nonzero": len(nz)}
            d44 = deltas[f"{arm}-{base}"].get("44b6", {}).get("score")
            nf44 = deltas[f"{arm}-{base}"].get("44b6", {}).get("node_frac")
            six_changed = sum(r["arms"][arm]["edges_changed"] for r in per_clip if r["embryo"] == "6bba")
            gates[arm] = gate_gb(arm, base, d44, boot,
                                 {r["stem"]: r["arms"][arm]["node_frac"] for r in per_clip},
                                 nf44, [r["stem"] for r in per_clip if r["arms"][arm]["forks_changed"]],
                                 six_changed, len(six_pairs) + int(ga_six or 0),
                                 res["clips_per_embryo"]["6bba"])
            dd = deltas[f"{arm}-{base}"].get("44b6", {})
            gates[arm].update({"delta_without_leak_group_0_unit": ex0, "units_positive": boots[arm]["units_positive"],
                               "units_nonzero": boots[arm]["units_nonzero"],
                               "info_44b6_delta_without_node_multiplier": dd.get("score_nomult"),
                               "info_44b6_multiplier_term": dd.get("multiplier_term"),
                               "info_44b6_node_delta": dd.get("nodes"),
                               "info_most_negative_clip_node_frac": min((r["arms"][arm]["node_frac"] for r in per_clip),
                                                                        default=0.0)})
        res.update({"pooled": pool_res, "deltas": deltas, "unit_tables": tables, "gates": gates,
                    "G-B": {"arm": PRIMARY, "pass": gates[PRIMARY]["pass"],
                            "rule": ("pre-registered G-B (CONTEXT.md 2026-09-26 08:58 UTC) on the PRIMARY arm "
                                     "ins35_splice vs ins35 (K6 vs K2); ins35_splice_gap3 / ins35_splice_csv / "
                                     "control_splice are gated the same way for information")}})
    # CSV-level sanity (old = ins35 rows, new = ins35_splice rows; kernel CSV parity of the control rows)
    csv_res = {"primary": csv_sanity(graphs["ins35"], graphs[PRIMARY], shapes)}
    agree = []
    for s in stems:
        ch_f = edge_set(graphs[PRIMARY][s]) ^ edge_set(graphs["ins35"][s])
        ch_c = edge_set(graphs["ins35_splice_csv"][s]) ^ edge_set(graphs["ins35"][s])
        if ch_f or ch_c:
            agree.append({"stem": s, "float_path_changed_edges": len(ch_f), "csv_path_changed_edges": len(ch_c),
                          "writer_rows_equal": digests[PRIMARY][s] == digests["ins35_splice_csv"][s]})
    csv_res["float_vs_csv_path"] = agree
    kp = {}
    for root in roots:
        sub = root / "submission.csv"
        if sub.is_file():
            here = {s for s in stems if find_dump([root], "trainlab", s) is not None}
            rows = read_kernel_csv(sub, here)
            for s in sorted(here):
                kp[s] = kernel_csv_parity(clips[s]["control"], rows[s]) if s in rows else None
    csv_res["kernel_csv_parity_control"] = {"checked": len(kp), "equal": sum(1 for v in kp.values() if v),
                                            "mismatch": sorted(s for s, v in kp.items() if v is False),
                                            "absent": sorted(s for s, v in kp.items() if v is None)}
    res["csv_sanity"] = {k: v for k, v in csv_res.items()}
    res["csv_sanity"]["primary"] = {k: v for k, v in csv_res["primary"].items() if k != "per_clip"}
    res["csv_sanity"]["primary"]["changed_clips"] = {s: r for s, r in csv_res["primary"]["per_clip"].items()
                                                     if not r["identical"]}
    res["clips"] = per_clip
    res["seconds"] = round(time.time() - t_start, 1)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    if not a.reg_json:
        out.with_name(out.stem + "_registration.json").write_text(json.dumps(regres, indent=1, default=str),
                                                                   encoding="utf-8")
    out.with_suffix(".md").write_text(report_md(res), encoding="utf-8")
    if "G-B" in res:
        g = res["gates"][PRIMARY]
        print(f"G-B ({PRIMARY} vs ins35): pass = {g['pass']} | 44b6 delta {_fmt(g['44b6_delta'], 5, True)} | "
              f"bootstrap lower {_fmt((g['bootstrap'] or {}).get('lower'), 5, True)} | checks {g['checks']}", flush=True)
    print("wrote", out.with_suffix(".json"), flush=True)
    return res


def report_md(res: dict) -> str:
    L = ["# G-B overlap-consensus lab (official metric)", "",
         f"Generated by `tools/overlap_lab.py score` at {res['generated_utc']} UTC from {res['n_clips']} clips "
         f"({', '.join(f'{k} {v}' for k, v in res['clips_per_embryo'].items())}); dumps {res['dumps']}.", "",
         f"Registration: {res['registration']['source']}; accepted pairs among lab clips "
         f"{len(res['registration']['pairs_in_lab'])} (6bba {res['registration']['6bba_pairs_in_lab']}; G-A train file "
         f"6bba pairs {res['registration']['6bba_pairs_ga_train']}). Bootstrap units {len(res['units'])}, fixed clips "
         f"{len(res['fixed_clips'])}; offset inconsistencies {res['frame_inconsistencies']}.", "",
         "## Splice", "", "| arm | base | videos changed | spliced | skipped fork/bnd/cap/frag/inv/gap/nonowner/third | "
         "nodes +/- | edges +/- | s |", "|---|---|---|---|---|---|---|---|"]
    for arm, v in res["splice"].items():
        t = v["total"]
        L.append(f"| {arm} | {v['base']} | {t['videos_changed']} | {t['spliced']} | {t['skipped_fork']}/"
                 f"{t['skipped_boundary']}/{t['skipped_cap']}/{t['skipped_fragment']}/{t['skipped_invariant']}/"
                 f"{t['skipped_gap']}/{t['skipped_nonowner']}/{t['skipped_third']} | +{t['nodes_added']}/"
                 f"-{t['nodes_removed']} | +{t['edges_added']}/-{t['edges_removed']} | {v['seconds']} |")
    if "gates" in res:
        L += ["", "## Gate G-B (pre-registered, CONTEXT.md 2026-09-26 08:58 UTC)", "",
              f"PRIMARY {res['G-B']['arm']}: pass = **{res['G-B']['pass']}**", "",
              "| arm | base | 44b6 delta | boot lower (95% 1-sided) | units | ex-group-0 | node frac (worst clip) | "
              "forks changed | 6bba edges / pairs | pass | info: delta w/o node multiplier | info: nodes (min clip frac) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for arm, g in res["gates"].items():
            b = g["bootstrap"] or {}
            L.append(f"| {arm} | {g['base']} | {_fmt(g['44b6_delta'], 5, True)} | {_fmt(b.get('lower'), 5, True)} | "
                     f"{b.get('units')} | {_fmt(g['delta_without_leak_group_0_unit'], 5, True)} | "
                     f"{_fmt(g['worst_clip_node_frac'], 5, True)} | {len(g['forks_changed_clips'])} | "
                     f"{g['6bba_changed_edges']} / {g['6bba_accepted_pairs']} | **{g['pass']}** | "
                     f"{_fmt(g.get('info_44b6_delta_without_node_multiplier'), 5, True)} | "
                     f"{_fmt(g.get('info_44b6_node_delta'), 0, True)} "
                     f"({_fmt(g.get('info_most_negative_clip_node_frac'), 4, True)}) |")
        L += ["", "Info columns are not gate terms (the pre-registered gate bounds node GROWTH only): a delta that "
              "vanishes without the node multiplier comes from deleted nodes, not from fixed edges."]
        L += ["", "## Pooled per embryo (division events counted once)", "",
              "| arm | embryo | clips | score | adj edge J | edge J | div J | div TP/FP/FN (weighted) | plain official score |"
              " nodes |", "|---|---|---|---|---|---|---|---|---|---|"]
        for arm, d in res["pooled"].items():
            for emb, p in d.items():
                L.append(f"| {arm} | {emb} | {p['clips']} | {_fmt(p['score'], 5)} | {_fmt(p['adj_edge_jaccard'], 5)} | "
                         f"{_fmt(p['edge_jaccard'], 5)} | {_fmt(p['division_jaccard'], 4)} | {p['div_tp_w']:.2f}/"
                         f"{p['div_fp_w']:.2f}/{p['div_fn_w']:.2f} | {_fmt(p['plain_official']['score'], 5)} | "
                         f"{int(p['nodes'])} |")
        L += ["", "## Deltas", "", "| comparison | embryo | score | adj | edge J | multiplier | div J | TP/FP/FN | nodes |"
              " changed clips | wins/losses |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for k, d in res["deltas"].items():
            for emb, x in d.items():
                L.append(f"| {k} | {emb} | {_fmt(x['score'], 5, True)} | {_fmt(x['adj_edge_jaccard'], 5, True)} | "
                         f"{_fmt(x['edge_jaccard'], 5, True)} | {_fmt(x['multiplier_term'], 5, True)} | "
                         f"{_fmt(x['division_jaccard'], 4, True)} | {x['edge_tp']:+.0f}/{x['edge_fp']:+.0f}/"
                         f"{x['edge_fn']:+.0f} | {x['nodes']:+.0f} | {x['clips_changed']}/{x['clips']} | "
                         f"{x['wins']}/{x['losses']} |")
        L += ["", "## Per leak-group unit (44b6, PRIMARY)", "",
              "| unit | clips | leak groups | pairs | spliced | delta | TP/FP/FN | nodes | clip wins/losses |",
              "|---|---|---|---|---|---|---|---|---|"]
        for r in res["unit_tables"].get(PRIMARY, []):
            L.append(f"| {r['unit']} | {r['clips']} | {r['leak_groups']} | {r['pairs']} | {r['spliced']} | "
                     f"{_fmt(r['delta'], 5, True)} | {r['edge_tp']:+.0f}/{r['edge_fp']:+.0f}/{r['edge_fn']:+.0f} | "
                     f"{r['nodes']:+.0f} | {r['clip_wins']}/{r['clip_losses']} |")
    cs = res["csv_sanity"]
    L += ["", "## CSV-level sanity", "",
          f"- old = ins35 rows, new = ins35_splice rows: {json.dumps(cs['primary']['totals'])}; invalid rows introduced: "
          f"{cs['primary']['invalid_introduced'] or 'none'}; 6bba datasets changed: {cs['primary']['6bba_changed'] or 'none'}",
          f"- kernel submission.csv == our control rows: {cs['kernel_csv_parity_control']}",
          f"- float-path vs CSV-path splice (clips touched by either): {len(cs['float_vs_csv_path'])}; writer rows equal "
          f"on {sum(1 for r in cs['float_vs_csv_path'] if r['writer_rows_equal'])}"]
    return "\n".join(L) + "\n"


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("score")
    c.add_argument("--dumps", nargs="+", default=None, help="downloaded lab kernel output folder(s)")
    c.add_argument("--tails", default=None, help="PROXY: a local replay tail folder instead of lab dumps (no insertion)")
    c.add_argument("--out", default=str(ROOT / "experiments/exp64_overlap_lab/results.json"))
    c.add_argument("--train-dir", default=str(TRAIN_DIR))
    c.add_argument("--splits", default=str(SPLITS))
    c.add_argument("--ga-json", default=str(GA_JSON), help="train-wide G-A registration (6bba pair count); '' = none")
    c.add_argument("--reg-json", default=None, help="reuse a registration json (overlap_reg --out) instead of running it")
    c.add_argument("--reg-cache", default=None, help="anchor npz cache dir for the registration run")
    c.add_argument("--reg-workers", type=int, default=3)
    c.add_argument("--workers", type=int, default=3)
    c.add_argument("--boot", type=int, default=BOOT_B)
    c.add_argument("--embryo", default="all", choices=("all",) + EMBRYOS)
    c.add_argument("--only", default="", help="comma-separated stems")
    c.add_argument("--no-score", action="store_true", help="registration + splice + CSV sanity only (no GT scoring)")
    a = ap.parse_args(argv)
    if a.cmd == "score":
        cmd_score(a)


if __name__ == "__main__":
    main()
