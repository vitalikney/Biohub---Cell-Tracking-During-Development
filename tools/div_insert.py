"""Post-tail division insertion (plan L2): add one parent->daughter edge u->v next to u's existing single child c1.

Shared by the Kaggle kernel patch (tools/build_probe_kernel.py --patch divinsert, embedded verbatim in a notebook cell)
and the laptop replay, so both run ONE code path. Pure python + numpy (scipy's cKDTree only as an optional pre-filter
with identical results). Nothing here reads files or images.

    triples = candidate_triples(nodes_by_id, edges, params)          # [(u, c1, v), ...] -> nodes that need p
    edges, stats = insert_divisions(nodes_by_id, edges, node_p, params)

Inputs
  nodes_by_id  {id: {"t", "z", "y", "x", ...}}, t/z/y/x in VOXEL units of the full-resolution frame (as in the notebook,
               the submission CSV and the GT .geff); distances use the notebook's VOXEL_SCALE_UM (1.625, 0.40625, 0.40625).
  edges        list of dicts with source_id, target_id and optional edge_prob (None for gap / gap2 / safe-division
               edges in the notebook), gap_closed, gap2_recovered, safe_division flags.
  node_p       {id: (p_cont, p_par, p_dau)} = tools/daughternet.CLASSES order.
  params       mapping (or attribute object) with the keys of DIVINS_DEFAULT_PARAMS; unknown keys raise.

Rule (fixed in CONTEXT.md before any grid)
  u   has exactly one outgoing edge, to c1 at t+1, and |c1 - u| <= parent_um (10 um).
  v   is a node at t+1, v != c1, |v - u| <= v_um (15 um), and v is not gap-synthetic.
  sister_min <= |c1 - v| <= sister_max (3..20 um); |(c1 + v)/2 - u| <= mid_um (6.5 um);
  cos(c1 - u, v - u) <= cos_max (0.25), cos = dot / (|a| |b| + 1e-9) (a zero-length vector gives cos 0).
  Orphan branch (default): v has no incoming edge.
  Steal branch (steal=1 only): v has exactly one parent w, w is not a fork parent (out-degree 1), edge_prob(w, v) is a
  finite number < steal_prob_max (0.3; None/NaN = gap, gap2 or safe-division edge = never stolen), score >=
  edge_prob(w, v) + steal_margin (0.2), and at most floor(steal_frac * cap_video) steals (half of the cap). The stolen
  edge w->v is removed, so w becomes a track end.
  score = p_par(u) * p_dau(v) * p_dau(c1) ** alpha; only score >= threshold is eligible (a node without p is skipped).
  Greedy by score, ties broken by (t, u, v, c1) ascending. Every node takes part in at most ONE inserted division in any
  role (u, c1, v and the robbed w), which covers "u, v and c1 each used once". Caps: cap_video insertions per call
  (one call = one video) and cap_frame insertions per parent frame t; a cap of 0 inserts nothing.
  Existing forks are never broken (u must have out-degree 1, a robbed w must have out-degree 1) and nodes are never
  added or removed.

Gap-synthetic nodes: the notebook flags single-frame gap nodes with gap_synthetic = 1 (close_single_frame_gaps);
recover_strict_gap2 inserts its two nodes WITHOUT a node flag, so --patch divinsert adds gap2_synthetic = 1 there, and
for graphs without that flag a node whose incoming edge and one outgoing edge are both gap2_recovered is also treated
as synthetic.
"""
from __future__ import annotations

import json
import math
from typing import Any, Mapping, Sequence

import numpy as np

try:
    from scipy.spatial import cKDTree as _DivinsKDTree
except Exception:  # pragma: no cover - the pre-filter is optional, the exact gates below decide
    _DivinsKDTree = None

DIVINS_VOXEL_SCALE_UM = (1.625, 0.40625, 0.40625)
DIVINS_DEFAULT_PARAMS: dict[str, Any] = {
    "enable": 1,
    "steal": 0,
    "cap_video": 3,
    "cap_frame": 1,
    "alpha": 1.0,
    "threshold": 0.5,
    "parent_um": 10.0,
    "v_um": 15.0,
    "sister_min": 3.0,
    "sister_max": 20.0,
    "mid_um": 6.5,
    "cos_max": 0.25,
    "steal_prob_max": 0.3,
    "steal_margin": 0.2,
    "steal_frac": 0.5,
    "scale_um": DIVINS_VOXEL_SCALE_UM,
}
DIVINS_STAT_KEYS = (
    "divins_enabled", "divins_triples", "divins_triples_orphan", "divins_triples_steal", "divins_missing_p",
    "divins_below_threshold", "divins_steal_margin_rejected", "divins_eligible", "divins_added",
    "divins_added_orphan", "divins_added_steal", "divins_skipped_used", "divins_skipped_cap_frame",
    "divins_skipped_cap_video", "divins_skipped_steal_cap",
)
_DIVINS_KDTREE_MIN = 64
_DIVINS_EDGE_FLAGS = ("gap_closed", "gap2_recovered", "safe_division", "motion_relinked")


def divins_params(params: Mapping[str, Any] | Any | None = None) -> dict[str, Any]:
    """DIVINS_DEFAULT_PARAMS overridden by params (a mapping or an object with attributes); unknown keys raise."""
    merged = dict(DIVINS_DEFAULT_PARAMS)
    if params is None:
        return merged
    items = list(params.items() if isinstance(params, Mapping) else vars(params).items())
    unknown = sorted(str(k) for k, _ in items if k not in DIVINS_DEFAULT_PARAMS)
    if unknown:
        raise ValueError(f"unknown div_insert params: {unknown}")
    merged.update(items)
    return merged


def _flag(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in ("", "0", "false", "no", "off")
    return bool(value)


def _int_flag(record: Mapping[str, Any], key: str) -> bool:
    value = record.get(key, 0)
    try:
        return int(value or 0) == 1
    except (TypeError, ValueError):
        return False


def _edge_prob(edge: Mapping[str, Any]) -> float | None:
    value = edge.get("edge_prob")
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _graph_index(nodes_by_id: Mapping[int, Mapping[str, Any]], edges: Sequence[Mapping[str, Any]]):
    out_e: dict[int, list] = {}
    in_e: dict[int, list] = {}
    for edge in edges:
        s, t = int(edge["source_id"]), int(edge["target_id"])
        if s not in nodes_by_id or t not in nodes_by_id:
            continue
        out_e.setdefault(s, []).append(edge)
        in_e.setdefault(t, []).append(edge)
    return out_e, in_e


def is_gap_synthetic(node_id: int, node: Mapping[str, Any], in_e: Mapping[int, list], out_e: Mapping[int, list]) -> bool:
    if _int_flag(node, "gap_synthetic") or _int_flag(node, "gap2_synthetic"):
        return True
    ins = in_e.get(node_id, [])
    outs = out_e.get(node_id, [])
    return any(_int_flag(e, "gap2_recovered") for e in ins) and any(_int_flag(e, "gap2_recovered") for e in outs)


def _candidates(nodes_by_id, P, out_e, in_e) -> list[tuple[int, int, int, Mapping[str, Any] | None]]:
    """[(u, c1, v, stolen_edge_or_None)] in (t, u, v) order; every geometric and structural gate applied."""
    scale = np.asarray(P["scale_um"], dtype=np.float64)

    def pos(node_id: int) -> np.ndarray:
        n = nodes_by_id[node_id]
        return np.array([float(n["z"]), float(n["y"]), float(n["x"])], dtype=np.float64) * scale

    steal = _flag(P["steal"])
    steal_prob_max = float(P["steal_prob_max"])
    parent_um, v_um = float(P["parent_um"]), float(P["v_um"])
    sister_min, sister_max = float(P["sister_min"]), float(P["sister_max"])
    mid_um, cos_max = float(P["mid_um"]), float(P["cos_max"])

    v_by_t: dict[int, list[int]] = {}
    steal_edge: dict[int, Mapping[str, Any]] = {}
    for node_id, node in nodes_by_id.items():
        node_id = int(node_id)
        if is_gap_synthetic(node_id, node, in_e, out_e):
            continue
        ins = in_e.get(node_id, [])
        if ins:
            if not steal or len(ins) != 1:
                continue
            w = int(ins[0]["source_id"])
            if len(out_e.get(w, [])) != 1:
                continue
            ep = _edge_prob(ins[0])
            if ep is None or not ep < steal_prob_max:
                continue
            steal_edge[node_id] = ins[0]
        v_by_t.setdefault(int(node["t"]), []).append(node_id)

    parents_by_t: dict[int, list[tuple[int, int]]] = {}
    for u, outs in out_e.items():
        if len(outs) != 1:
            continue
        c1 = int(outs[0]["target_id"])
        tu = int(nodes_by_id[u]["t"])
        if int(nodes_by_id[c1]["t"]) != tu + 1:
            continue
        parents_by_t.setdefault(tu, []).append((int(u), c1))

    triples: list[tuple[int, int, int, Mapping[str, Any] | None]] = []
    for tu in sorted(parents_by_t):
        vs = sorted(v_by_t.get(tu + 1, []))
        if not vs:
            continue
        V = np.stack([pos(v) for v in vs])
        pairs_uc = sorted(parents_by_t[tu])
        PU = np.stack([pos(u) for u, _ in pairs_uc])
        PC = np.stack([pos(c1) for _, c1 in pairs_uc])
        DC = PC - PU
        NDC = np.sqrt((DC * DC).sum(axis=1))
        keep = np.flatnonzero(NDC <= parent_um)
        if keep.size == 0:
            continue
        # (parent index, v index) pairs in (u, v) order; the KD-tree only pre-filters, the gates below decide
        if _DivinsKDTree is not None and len(vs) > _DIVINS_KDTREE_MIN:
            hits = _DivinsKDTree(V).query_ball_point(PU[keep], v_um + 1e-6)
            lists = [sorted(h) for h in hits]
            lens = np.fromiter((len(h) for h in lists), dtype=np.int64, count=len(lists))
            if int(lens.sum()) == 0:
                continue
            ui = np.repeat(keep, lens)
            vj = np.fromiter((j for h in lists for j in h), dtype=np.int64, count=int(lens.sum()))
        else:
            ui = np.repeat(keep, len(vs))
            vj = np.tile(np.arange(len(vs), dtype=np.int64), keep.size)
        pu, pc, dc, ndc, q = PU[ui], PC[ui], DC[ui], NDC[ui], V[vj]
        dv = q - pu
        ndv = np.sqrt((dv * dv).sum(axis=1))
        ds = q - pc
        sis = np.sqrt((ds * ds).sum(axis=1))
        dm = 0.5 * (q + pc) - pu
        mid = np.sqrt((dm * dm).sum(axis=1))
        cos = (dv * dc).sum(axis=1) / (ndv * ndc + 1e-9)
        ok = (ndv <= v_um) & (sis >= sister_min) & (sis <= sister_max) & (mid <= mid_um) & (cos <= cos_max)
        for i, j in zip(ui[ok].tolist(), vj[ok].tolist()):
            u, c1 = pairs_uc[i]
            v = vs[j]
            if v == c1:
                continue
            triples.append((u, c1, v, steal_edge.get(v)))
    return triples


def candidate_triples(nodes_by_id: Mapping[int, Mapping[str, Any]], edges: Sequence[Mapping[str, Any]],
                      params: Mapping[str, Any] | Any | None = None) -> list[tuple[int, int, int]]:
    """Every gated (u, c1, v) the insertion may consider (orphan v; plus stealable v when params steal=1).
    The kernel scores exactly the union of these nodes; p is not needed for anything else."""
    P = divins_params(params)
    out_e, in_e = _graph_index(nodes_by_id, edges)
    return [(u, c1, v) for u, c1, v, _ in _candidates(nodes_by_id, P, out_e, in_e)]


def insert_divisions(nodes_by_id: Mapping[int, Mapping[str, Any]], edges: list[Mapping[str, Any]],
                     node_p: Mapping[int, Sequence[float]], params: Mapping[str, Any] | Any | None = None):
    """Returns (edges, stats). Unchanged input -> the SAME list object; otherwise a new list = input edges in order
    (minus stolen ones) + one new edge dict per insertion. Input dicts are never mutated. stats values are scalars."""
    P = divins_params(params)
    stats: dict[str, Any] = {key: 0 for key in DIVINS_STAT_KEYS}
    stats["divins_enabled"] = int(_flag(P["enable"]))
    if not stats["divins_enabled"] or not edges or not nodes_by_id:
        return edges, stats

    alpha = float(P["alpha"])
    threshold = float(P["threshold"])
    steal_margin = float(P["steal_margin"])
    cap_video = int(P["cap_video"])
    cap_frame = int(P["cap_frame"])
    steal_cap = int(math.floor(float(P["steal_frac"]) * cap_video + 1e-9)) if _flag(P["steal"]) else 0
    scale = np.asarray(P["scale_um"], dtype=np.float64)

    out_e, in_e = _graph_index(nodes_by_id, edges)
    cands = _candidates(nodes_by_id, P, out_e, in_e)
    stats["divins_triples"] = len(cands)
    stats["divins_triples_steal"] = sum(1 for c in cands if c[3] is not None)
    stats["divins_triples_orphan"] = len(cands) - stats["divins_triples_steal"]

    eligible: list[tuple[float, int, int, int, int, Mapping[str, Any] | None, float | None]] = []
    for u, c1, v, stolen in cands:
        pu, pv, pc = node_p.get(u), node_p.get(v), node_p.get(c1)
        if pu is None or pv is None or pc is None:
            stats["divins_missing_p"] += 1
            continue
        score = float(pu[1]) * float(pv[2]) * (float(pc[2]) ** alpha)
        if not math.isfinite(score):
            stats["divins_missing_p"] += 1
            continue
        if score < threshold:
            stats["divins_below_threshold"] += 1
            continue
        ep = None
        if stolen is not None:
            ep = _edge_prob(stolen)
            if ep is None or score < ep + steal_margin:
                stats["divins_steal_margin_rejected"] += 1
                continue
        eligible.append((score, int(nodes_by_id[u]["t"]), u, v, c1, stolen, ep))
    eligible.sort(key=lambda item: (-item[0], item[1], item[2], item[3], item[4]))
    stats["divins_eligible"] = len(eligible)

    used: set[int] = set()
    per_frame: dict[int, int] = {}
    added: list[dict[str, Any]] = []
    removed: set[int] = set()
    n_steal = 0
    for k, (score, tu, u, v, c1, stolen, ep) in enumerate(eligible):
        if len(added) >= cap_video:
            stats["divins_skipped_cap_video"] = len(eligible) - k
            break
        w = int(stolen["source_id"]) if stolen is not None else None
        if u in used or v in used or c1 in used or (w is not None and w in used):
            stats["divins_skipped_used"] += 1
            continue
        if per_frame.get(tu, 0) >= cap_frame:
            stats["divins_skipped_cap_frame"] += 1
            continue
        if w is not None and n_steal >= steal_cap:
            stats["divins_skipped_steal_cap"] += 1
            continue
        nu, nv = nodes_by_id[u], nodes_by_id[v]
        d = (np.array([float(nv["z"]), float(nv["y"]), float(nv["x"])])
             - np.array([float(nu["z"]), float(nu["y"]), float(nu["x"])])) * scale
        added.append({
            "source_id": u,
            "target_id": v,
            "edge_prob": None,
            "distance_um": float(np.sqrt(d @ d)),
            "div_inserted": 1,
            "div_score": float(score),
            "div_c1": c1,
            "div_steal_from": -1 if w is None else w,
            "div_stolen_edge_prob": float("nan") if ep is None else float(ep),
        })
        used.update((u, v, c1))
        if w is not None:
            used.add(w)
            removed.add(id(stolen))
            n_steal += 1
        per_frame[tu] = per_frame.get(tu, 0) + 1

    stats["divins_added"] = len(added)
    stats["divins_added_steal"] = n_steal
    stats["divins_added_orphan"] = len(added) - n_steal
    if not added:
        return edges, stats
    return [e for e in edges if id(e) not in removed] + added, stats


# ---------------------------------------------------------------------------------------------------------------------
# Parity dump: the kernel (BIOHUB_DIVINS_DUMP=1) writes dump_arrays(...) per dataset with np.savez_compressed; the laptop
# replays it with replay_dump(np.load(path)) and must reproduce the kernel's inserted / removed edges exactly.
# ---------------------------------------------------------------------------------------------------------------------
def dump_arrays(nodes_by_id: Mapping[int, Mapping[str, Any]], edges: Sequence[Mapping[str, Any]],
                node_p: Mapping[int, Sequence[float]], params: Mapping[str, Any] | Any | None = None,
                triples: Sequence[Sequence[int]] | None = None,
                result_edges: Sequence[Mapping[str, Any]] | None = None) -> dict[str, np.ndarray]:
    """Pre-insertion graph + node p (+ triples and the insertion result) as plain numpy arrays."""
    ids = sorted(int(i) for i in nodes_by_id)
    nodes = [nodes_by_id[i] for i in ids]
    out: dict[str, np.ndarray] = {
        "node_id": np.asarray(ids, dtype=np.int64).reshape(-1),
        "node_t": np.asarray([int(n["t"]) for n in nodes], dtype=np.int64).reshape(-1),
        "node_zyx": np.asarray([[float(n["z"]), float(n["y"]), float(n["x"])] for n in nodes],
                               dtype=np.float64).reshape(-1, 3),
        "node_gap_synthetic": np.asarray([_int_flag(n, "gap_synthetic") for n in nodes], dtype=np.int8).reshape(-1),
        "node_gap2_synthetic": np.asarray([_int_flag(n, "gap2_synthetic") for n in nodes], dtype=np.int8).reshape(-1),
        "edge_st": np.asarray([[int(e["source_id"]), int(e["target_id"])] for e in edges], dtype=np.int64).reshape(-1, 2),
        "edge_prob": np.asarray([np.nan if _edge_prob(e) is None else _edge_prob(e) for e in edges],
                                dtype=np.float64).reshape(-1),
        "edge_distance_um": np.asarray([np.nan if e.get("distance_um") is None else float(e["distance_um"])
                                        for e in edges], dtype=np.float64).reshape(-1),
    }
    for flag in _DIVINS_EDGE_FLAGS:
        out["edge_" + flag] = np.asarray([_int_flag(e, flag) for e in edges], dtype=np.int8).reshape(-1)
    p_ids = sorted(int(i) for i in node_p)
    out["p_id"] = np.asarray(p_ids, dtype=np.int64).reshape(-1)
    out["p"] = np.asarray([[float(x) for x in node_p[i]] for i in p_ids], dtype=np.float32).reshape(-1, 3)
    out["params_json"] = np.asarray(json.dumps(divins_params(params), sort_keys=True,
                                               default=lambda o: o.item() if hasattr(o, "item") else list(o)))
    if triples is not None:
        out["triples"] = np.asarray([[int(a) for a in tr[:3]] for tr in triples], dtype=np.int64).reshape(-1, 3)
    if result_edges is not None:
        new = [e for e in result_edges if _int_flag(e, "div_inserted")]
        out["added"] = np.asarray([[int(e["source_id"]), int(e["target_id"]), int(e["div_c1"]),
                                    int(e["div_steal_from"])] for e in new], dtype=np.int64).reshape(-1, 4)
        out["added_score"] = np.asarray([float(e["div_score"]) for e in new], dtype=np.float64).reshape(-1)
        kept = {id(e) for e in result_edges}
        out["removed"] = np.asarray([[int(e["source_id"]), int(e["target_id"])] for e in edges if id(e) not in kept],
                                    dtype=np.int64).reshape(-1, 2)
    return out


def load_dump(arrays: Mapping[str, np.ndarray]) -> dict[str, Any]:
    """Inverse of dump_arrays -> {nodes_by_id, edges, node_p, params, triples?, added?, removed?}."""
    nodes_by_id: dict[int, dict[str, Any]] = {}
    zyx = np.asarray(arrays["node_zyx"], dtype=np.float64)
    g1 = np.asarray(arrays["node_gap_synthetic"])
    g2 = np.asarray(arrays["node_gap2_synthetic"])
    for k, (node_id, t) in enumerate(zip(np.asarray(arrays["node_id"]).tolist(), np.asarray(arrays["node_t"]).tolist())):
        node = {"node_id": int(node_id), "t": int(t), "z": float(zyx[k, 0]), "y": float(zyx[k, 1]), "x": float(zyx[k, 2])}
        if int(g1[k]):
            node["gap_synthetic"] = 1
        if int(g2[k]):
            node["gap2_synthetic"] = 1
        nodes_by_id[int(node_id)] = node
    edges: list[dict[str, Any]] = []
    st = np.asarray(arrays["edge_st"]).reshape(-1, 2)
    prob = np.asarray(arrays["edge_prob"], dtype=np.float64)
    dist = np.asarray(arrays["edge_distance_um"], dtype=np.float64)
    for k in range(len(st)):
        edge: dict[str, Any] = {
            "source_id": int(st[k, 0]),
            "target_id": int(st[k, 1]),
            "edge_prob": None if not np.isfinite(prob[k]) else float(prob[k]),
            "distance_um": float(dist[k]),
        }
        for flag in _DIVINS_EDGE_FLAGS:
            key = "edge_" + flag
            if key in arrays and int(np.asarray(arrays[key])[k]):
                edge[flag] = 1
        edges.append(edge)
    p = np.asarray(arrays["p"], dtype=np.float32).reshape(-1, 3)
    node_p = {int(i): tuple(float(x) for x in p[k]) for k, i in enumerate(np.asarray(arrays["p_id"]).tolist())}
    out: dict[str, Any] = {
        "nodes_by_id": nodes_by_id,
        "edges": edges,
        "node_p": node_p,
        "params": json.loads(str(np.asarray(arrays["params_json"]))),
    }
    for key in ("triples", "added", "added_score", "removed"):
        if key in arrays:
            out[key] = np.asarray(arrays[key])
    return out


def replay_dump(arrays: Mapping[str, np.ndarray], params: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Re-run candidate_triples + insert_divisions on a kernel dump (with the dumped params unless overridden) and
    compare against the kernel's recorded result -> {'match': bool | None, 'triples_match', 'edges', 'stats', ...}."""
    d = load_dump(arrays)
    P = d["params"] if params is None else params
    triples = candidate_triples(d["nodes_by_id"], d["edges"], P)
    edges, stats = insert_divisions(d["nodes_by_id"], d["edges"], d["node_p"], P)
    new = [e for e in edges if _int_flag(e, "div_inserted")]
    added = np.asarray([[int(e["source_id"]), int(e["target_id"]), int(e["div_c1"]), int(e["div_steal_from"])]
                        for e in new], dtype=np.int64).reshape(-1, 4)
    kept = {id(e) for e in edges}
    removed = np.asarray([[int(e["source_id"]), int(e["target_id"])] for e in d["edges"] if id(e) not in kept],
                         dtype=np.int64).reshape(-1, 2)
    res: dict[str, Any] = {"edges": edges, "stats": stats, "added": added, "removed": removed, "triples": triples,
                           "match": None, "triples_match": None}
    if "triples" in d:
        res["triples_match"] = bool(np.array_equal(np.asarray(triples, dtype=np.int64).reshape(-1, 3), d["triples"]))
    if "added" in d and params is None:
        res["match"] = bool(np.array_equal(added, d["added"].reshape(-1, 4))
                            and np.array_equal(removed, d["removed"].reshape(-1, 2)))
    return res
