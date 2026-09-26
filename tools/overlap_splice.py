"""Disagreement-component splice of the final graphs of registered overlapping crops (OVERLAP-CONSENSUS line).

Design: research/wf_ideas_v2/r2_research_overlap-consensus.json (refined_change, implementation_notes FUSION) with the
verifiers' repairs (forks skipped, node cap 0.5%, optional owner-gap >= 3 / non-owner-score restriction). Gates G-B/G-D:
CONTEXT.md 2026-09-26 08:58 UTC. Registration: tools/overlap_reg.py (offset = coord_a - coord_b, voxels, frames).

Graph representation (the x138 kernel's and tools/trainlab_io.py's): nodes {node_id: {'t', 'z', 'y', 'x', ...}} with
float voxel coordinates in the video's own crop, edges [{'source_id', 'target_id', ...}]. as_graph() also accepts
(src, dst) tuples; graphs_from_rows()/rows_from_graphs() convert submission.csv rows.

For one accepted pair (A, B) with offset d (B's node p sits at p + d in A's coordinates):
  (i)   overlap nodes = nodes inside both crops; per frame a Hungarian correspondence between A and B overlap nodes
        with cost = distance in um (z 1.625, y/x 0.40625 per voxel), pairs kept only within match_um (2.5);
  (ii)  a matched pair is AGREE iff its predecessor set and its successor set, restricted to overlap nodes, map onto
        each other through the correspondence (edges to nodes outside the overlap are invisible to both copies);
  (iii) the non-agree overlap nodes of both copies are joined by each copy's edges and by same-frame A-B proximity
        <= group_um (7); the connected components are the DISAGREEMENT components;
  (iv)  score s = min(distance to the crop border in um, 1 um x frames to the nearest clip end), averaged over the
        component's node positions (both copies' nodes) in each copy's own crop; B owns iff mean_B > mean_A + margin
        (1 um), else A owns (ties keep A);
  (v)   the receiver's component nodes and their edges are deleted, the owner's are imported; owner edges to AGREE
        nodes are rewired through the correspondence (seams only at agree nodes), owner edges to nodes outside the
        overlap are dropped (outside the receiver's crop);
  (vi)  SKIPPED components: any node that is a fork parent or a fork child in its own copy; a receiver edge from the
        component to a node outside the overlap (would cut a track without an agree seam); the per-video node budget
        (net added nodes <= node_cap_frac x original node count, default 0.5%); optional restrictions min_gap (owner -
        non-owner score, e.g. 3) and max_nonowner (e.g. 8); a third registered copy with a better score (with 3+
        copies the argmax owner decides; that copy's own pairs carry the splice); any in-degree > 1 or new fork after
        the tentative splice (rolled back);
  (vii) imported nodes that would end in a weakly connected component shorter than min_fragment (3) nodes:
        fragment_policy 'rollback' (default) rolls the whole component back (the receiver keeps its version,
        skipped_fragment); 'drop' deletes only those imported nodes and keeps the rest of the splice (the receiver's
        component nodes stay deleted -> pure deletion possible; net-harmful on adversarial synthetic scenes).
Identity: no pair, no overlap node, or no applicable component -> the input objects are returned unchanged.
Pure python + numpy + scipy.optimize.linear_sum_assignment.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

SCALE_UM = (1.625, 0.40625, 0.40625)
MATCH_UM = 2.5
GROUP_UM = 7.0
MARGIN_UM = 1.0
NODE_CAP_FRAC = 0.005
MIN_FRAGMENT = 3
DEFAULTS = {"match_um": MATCH_UM, "group_um": GROUP_UM, "margin_um": MARGIN_UM, "node_cap_frac": NODE_CAP_FRAC,
            "min_fragment": MIN_FRAGMENT, "min_gap": None, "max_nonowner": None, "scale_um": SCALE_UM,
            "mark_key": None, "fragment_policy": "rollback"}
COUNTERS = ("pairs", "overlap_nodes_a", "overlap_nodes_b", "matched", "agree", "components", "owner_a", "owner_b",
            "spliced", "spliced_into_a", "spliced_into_b", "skipped_fork", "skipped_boundary", "skipped_cap",
            "skipped_gap", "skipped_nonowner", "skipped_third", "skipped_invariant", "skipped_fragment", "nodes_removed", "nodes_added",
            "edges_removed", "edges_added", "edges_dropped_outside", "fragments_dropped", "fragment_nodes_dropped")


# ----------------------------------------------------------------------------------------------------------------------
# representation helpers
# ----------------------------------------------------------------------------------------------------------------------
def as_graph(nodes, edges) -> tuple[dict, list]:
    """Normalise to ({id: {'t','z','y','x',...}}, [{'source_id','target_id',...}]); dict edges are kept as objects."""
    out_e = []
    for e in edges:
        if isinstance(e, dict):
            out_e.append(e)
        else:
            s, t = e
            out_e.append({"source_id": int(s), "target_id": int(t)})
    return dict(nodes), out_e


def graphs_from_rows(rows) -> dict:
    """submission.csv rows (dicts with dataset,row_type,node_id,t,z,y,x,source_id,target_id) -> {dataset: graph}."""
    out: dict = {}
    for r in rows:
        g = out.setdefault(str(r["dataset"]), ({}, []))
        if r["row_type"] == "node":
            g[0][int(r["node_id"])] = {"t": int(r["t"]), "z": float(r["z"]), "y": float(r["y"]), "x": float(r["x"])}
        else:
            g[1].append({"source_id": int(r["source_id"]), "target_id": int(r["target_id"])})
    return out


def rows_from_graphs(graphs: dict, order=None) -> list:
    """Inverse of graphs_from_rows (node rows by id with rounded non-negative coords, then edges in order)."""
    rows = []
    for ds in (order or graphs):
        nodes, edges = graphs[ds]
        for nid in sorted(nodes):
            n = nodes[nid]
            rows.append({"dataset": ds, "row_type": "node", "node_id": int(nid), "t": int(n["t"]),
                         "z": max(0, int(round(float(n["z"])))), "y": max(0, int(round(float(n["y"])))),
                         "x": max(0, int(round(float(n["x"])))), "source_id": -1, "target_id": -1})
        for e in edges:
            rows.append({"dataset": ds, "row_type": "edge", "node_id": -1, "t": -1, "z": -1, "y": -1, "x": -1,
                         "source_id": int(e["source_id"]), "target_id": int(e["target_id"])})
    return rows


def _pos(n: dict) -> tuple:
    return (int(round(float(n["t"]))), float(n["z"]), float(n["y"]), float(n["x"]))


def inside(p, shape) -> bool:
    """p = (t, z, y, x) in a crop's voxel coordinates; shape = (T, Z, Y, X)."""
    t, z, y, x = p
    T, Z, Y, X = shape
    return 0 <= t < T and -0.5 <= z <= Z - 0.5 and -0.5 <= y <= Y - 0.5 and -0.5 <= x <= X - 0.5


def border_score(p, shape, scale_um=SCALE_UM) -> float:
    """min(distance to the crop border in um, 1 um x frames to the nearest clip end), >= 0."""
    t, z, y, x = p
    T, Z, Y, X = shape
    sp = min(min(z, Z - 1 - z) * scale_um[0], min(y, Y - 1 - y) * scale_um[1], min(x, X - 1 - x) * scale_um[2])
    tm = float(min(t, T - 1 - t))
    return max(0.0, min(sp, tm))


class _Work:
    """Mutable copy of one graph with pred/succ maps and an undo log."""

    def __init__(self, nodes: dict, edges: list):
        self.nodes = dict(nodes)
        self.edges = {}
        self.pred = defaultdict(set)
        self.succ = defaultdict(set)
        for e in edges:
            k = (int(e["source_id"]), int(e["target_id"]))
            self.edges[k] = e
            self.succ[k[0]].add(k[1])
            self.pred[k[1]].add(k[0])
        self.fork_parents = {s for s, kids in self.succ.items() if len(kids) >= 2}
        self.fork_nodes = set(self.fork_parents)
        for s in self.fork_parents:
            self.fork_nodes.update(self.succ[s])
        self.next_id = (max(self.nodes) + 1) if self.nodes else 1
        self.changed = False
        self.log = None

    def begin(self):
        self.log = []
        self._next0 = self.next_id

    def rollback(self):
        for op in reversed(self.log):
            kind = op[0]
            if kind == "add_node":
                self.nodes.pop(op[1], None)
            elif kind == "del_node":
                self.nodes[op[1]] = op[2]
            elif kind == "add_edge":
                self._del_edge_raw(op[1])
            elif kind == "del_edge":
                self._add_edge_raw(op[1], op[2])
        self.next_id = self._next0
        self.log = None

    def commit(self):
        self.log = None

    def _add_edge_raw(self, k, e):
        self.edges[k] = e
        self.succ[k[0]].add(k[1])
        self.pred[k[1]].add(k[0])

    def _del_edge_raw(self, k):
        self.edges.pop(k, None)
        self.succ[k[0]].discard(k[1])
        self.pred[k[1]].discard(k[0])

    def add_edge(self, s, t, rec):
        k = (int(s), int(t))
        if k in self.edges:
            return False
        self._add_edge_raw(k, rec)
        self.log.append(("add_edge", k))
        return True

    def del_edge(self, k):
        e = self.edges[k]
        self._del_edge_raw(k)
        self.log.append(("del_edge", k, e))

    def add_node(self, rec) -> int:
        nid = self.next_id
        self.next_id += 1
        self.nodes[nid] = rec
        self.log.append(("add_node", nid))
        return nid

    def del_node(self, nid) -> int:
        n_e = 0
        for p in list(self.pred.get(nid, ())):
            self.del_edge((p, nid))
            n_e += 1
        for c in list(self.succ.get(nid, ())):
            self.del_edge((nid, c))
            n_e += 1
        self.log.append(("del_node", nid, self.nodes.pop(nid)))
        return n_e

    def wcc_size(self, start, cap: int) -> int:
        seen, stack = {start}, [start]
        while stack and len(seen) < cap:
            u = stack.pop()
            for v in list(self.pred.get(u, ())) + list(self.succ.get(u, ())):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        return len(seen)

    def result(self, original):
        """The spliced (nodes, edges); the untouched `original` object itself when nothing changed."""
        if not self.changed:
            return original
        return dict(self.nodes), list(self.edges.values())


# ----------------------------------------------------------------------------------------------------------------------
# correspondence, agreement, components
# ----------------------------------------------------------------------------------------------------------------------
def _hungarian(pa: np.ndarray, pb: np.ndarray, gate: float) -> list[tuple[int, int]]:
    from scipy.optimize import linear_sum_assignment
    if len(pa) == 0 or len(pb) == 0:
        return []
    d = np.sqrt(((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1))
    big = gate * 1e3 + 1e6
    cost = np.where(d <= gate, d, big)
    r, c = linear_sum_assignment(cost)
    return [(int(i), int(j)) for i, j in zip(r, c) if d[i, j] <= gate]


class _UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        root = x
        while self.p[root] != root:
            root = self.p[root]
        while self.p[x] != root:
            self.p[x], x = root, self.p[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            if rb < ra:
                ra, rb = rb, ra
            self.p[rb] = ra


def _components(wa: _Work, wb: _Work, shape_a, shape_b, off, cfg) -> dict:
    """Correspondence, agreement and disagreement components of one pair (positions in A's coordinates)."""
    scale = np.asarray(cfg["scale_um"], dtype=np.float64)
    dt, dz, dy, dx = off
    pos_a = {nid: _pos(n) for nid, n in wa.nodes.items()}
    pos_b = {}
    for nid, n in wb.nodes.items():
        t, z, y, x = _pos(n)
        pos_b[nid] = (t + dt, z + dz, y + dy, x + dx)
    ov_a = {nid for nid, p in pos_a.items() if inside((p[0] - dt, p[1] - dz, p[2] - dy, p[3] - dx), shape_b)}
    ov_b = {nid for nid, p in pos_b.items() if inside(p, shape_a)}
    by_t_a, by_t_b = defaultdict(list), defaultdict(list)
    for nid in sorted(ov_a):
        by_t_a[pos_a[nid][0]].append(nid)
    for nid in sorted(ov_b):
        by_t_b[pos_b[nid][0]].append(nid)

    def um(ids, pos):
        return np.asarray([pos[i][1:] for i in ids], dtype=np.float64).reshape(-1, 3) * scale

    corr_ab, corr_ba = {}, {}
    for t in sorted(set(by_t_a) & set(by_t_b)):
        ia, ib = by_t_a[t], by_t_b[t]
        for i, j in _hungarian(um(ia, pos_a), um(ib, pos_b), cfg["match_um"]):
            corr_ab[ia[i]] = ib[j]
            corr_ba[ib[j]] = ia[i]

    def agree(a, b):
        for ga, gb in ((wa.pred, wb.pred), (wa.succ, wb.succ)):
            na = {v for v in ga.get(a, ()) if v in ov_a}
            nb = {v for v in gb.get(b, ()) if v in ov_b}
            if len(na) != len(nb) or any(corr_ab.get(v) not in nb for v in na):
                return False
        return True

    agree_a = {a for a, b in corr_ab.items() if agree(a, b)}
    agree_b = {corr_ab[a] for a in agree_a}
    na_a, na_b = ov_a - agree_a, ov_b - agree_b
    uf = _UF()
    for a in na_a:
        uf.find(("A", a))
        for c in wa.succ.get(a, ()):
            if c in na_a:
                uf.union(("A", a), ("A", c))
    for b in na_b:
        uf.find(("B", b))
        for c in wb.succ.get(b, ()):
            if c in na_b:
                uf.union(("B", b), ("B", c))
    g2 = cfg["group_um"] ** 2
    ta, tb = defaultdict(list), defaultdict(list)
    for a in sorted(na_a):
        ta[pos_a[a][0]].append(a)
    for b in sorted(na_b):
        tb[pos_b[b][0]].append(b)
    for t in set(ta) & set(tb):
        pa, pb = um(ta[t], pos_a), um(tb[t], pos_b)
        d2 = ((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1)
        for i, j in zip(*np.nonzero(d2 <= g2)):
            uf.union(("A", ta[t][int(i)]), ("B", tb[t][int(j)]))
    comps = defaultdict(list)
    for key in list(uf.p):
        comps[uf.find(key)].append(key)
    ordered = [sorted(v) for _, v in sorted(comps.items())]
    return {"pos_a": pos_a, "pos_b": pos_b, "ov_a": ov_a, "ov_b": ov_b, "corr_ab": corr_ab, "corr_ba": corr_ba,
            "agree_a": agree_a, "agree_b": agree_b, "components": ordered}


# ----------------------------------------------------------------------------------------------------------------------
# splice
# ----------------------------------------------------------------------------------------------------------------------
def _splice_component(comp, owner: str, info, W: dict, off, cfg, budget: dict, names: dict, st: dict) -> None:
    """Apply one component owned by `owner` ('A'|'B') to the other copy (receiver) with undo on invariant failure."""
    recv = "B" if owner == "A" else "A"
    wo, wr = W[owner], W[recv]
    on = [nid for side, nid in comp if side == owner]
    rn = [nid for side, nid in comp if side == recv]
    ov_o = info["ov_a"] if owner == "A" else info["ov_b"]
    ov_r = info["ov_b"] if owner == "A" else info["ov_a"]
    agree_o = info["agree_a"] if owner == "A" else info["agree_b"]
    corr = info["corr_ab"] if owner == "A" else info["corr_ba"]
    rn_set, on_set = set(rn), set(on)
    # receiver edges leaving the component to nodes outside the overlap -> no agree seam available
    for u in rn:
        for v in list(wr.pred.get(u, ())) + list(wr.succ.get(u, ())):
            if v not in rn_set and v not in ov_r:
                st["skipped_boundary"] += 1
                return
    net = len(on) - len(rn)
    rname = names[recv]
    if net > 0 and budget["used"][rname] + net > budget["cap"][rname]:
        st["skipped_cap"] += 1
        return
    dt, dz, dy, dx = off
    sgn = 1 if recv == "A" else -1  # owner B -> receiver A: +d ; owner A -> receiver B: -d
    wr.begin()
    removed_e = 0
    for u in rn:
        removed_e += wr.del_node(u)
    new_id = {}
    for u in on:
        rec = dict(wo.nodes[u])
        t, z, y, x = _pos(wo.nodes[u])
        rec["t"], rec["z"], rec["y"], rec["x"] = (t + sgn * dt, z + sgn * dz, y + sgn * dy, x + sgn * dx)
        if cfg.get("mark_key"):
            rec[cfg["mark_key"]] = 1
        new_id[u] = wr.add_node(rec)

    def m(v):
        if v in on_set:
            return new_id[v]
        if v in agree_o:
            return corr[v]
        return None

    added_e, dropped = 0, 0
    for u in on:
        for s, t in [(p, u) for p in wo.pred.get(u, ())] + [(u, c) for c in wo.succ.get(u, ())]:
            ms, mt = m(s), m(t)
            if ms is None or mt is None:
                if (s not in ov_o) or (t not in ov_o):
                    dropped += 1
                continue
            e = dict(wo.edges[(s, t)])
            e["source_id"], e["target_id"] = ms, mt
            if wr.add_edge(ms, mt, e):
                added_e += 1
    touched = set(new_id.values())
    for op in wr.log:
        if op[0] in ("add_edge", "del_edge"):
            touched.update(op[1])
    touched &= set(wr.nodes)
    for v in touched:
        if len(wr.pred.get(v, ())) > 1 or (len(wr.succ.get(v, ())) > 1 and v not in wr.fork_parents) \
                or len(wr.succ.get(v, ())) > 2:
            wr.rollback()
            st["skipped_invariant"] += 1
            return
    # (vii) imported nodes left in weakly connected components shorter than min_fragment
    frag_nodes = 0
    new_ids = set(new_id.values())
    if cfg["fragment_policy"] == "rollback":
        if any(wr.wcc_size(nid, cfg["min_fragment"]) < cfg["min_fragment"] for nid in sorted(new_ids)):
            wr.rollback()
            st["skipped_fragment"] += 1
            return
    for nid in sorted(new_ids):
        if nid in wr.nodes and wr.wcc_size(nid, cfg["min_fragment"]) < cfg["min_fragment"]:
            seen, stack = {nid}, [nid]
            while stack:
                u = stack.pop()
                for v in list(wr.pred.get(u, ())) + list(wr.succ.get(u, ())):
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            dropped_here = sorted(v for v in seen if v in new_ids)
            for v in dropped_here:
                wr.del_node(v)
            frag_nodes += len(dropped_here)
            st["fragments_dropped"] += 1
    added_n = len(on) - frag_nodes
    if not rn and added_n == 0:  # everything imported was a short fragment: no change at all
        wr.rollback()
        st["fragment_nodes_dropped"] += frag_nodes
        return
    net = added_n - len(rn)
    if net > 0 and budget["used"][rname] + net > budget["cap"][rname]:
        wr.rollback()
        st["skipped_cap"] += 1
        return
    wr.commit()
    wr.changed = True
    budget["used"][rname] += net
    st["spliced"] += 1
    st["spliced_into_" + recv.lower()] += 1
    st["nodes_removed"] += len(rn)
    st["nodes_added"] += added_n
    st["edges_removed"] += removed_e
    st["edges_added"] += added_e
    st["edges_dropped_outside"] += dropped
    st["fragment_nodes_dropped"] += frag_nodes


def splice_pair(ga, gb, shape_a, shape_b, offset, cfg: dict | None = None, budget: dict | None = None,
                names=("A", "B"), third=None) -> tuple:
    """Splice one registered pair. ga/gb = (nodes, edges) in their own crops; offset = coord_a - coord_b.
    budget {'cap': {name: max net added nodes}, 'used': {name: int}} (default: node_cap_frac of each graph).
    third(comp_positions_in_A_coords) -> best mean score of any OTHER registered copy covering them, or None.
    -> (ga', gb', stats); unchanged inputs are returned as the same objects."""
    cfg = {**DEFAULTS, **(cfg or {})}
    if cfg["fragment_policy"] not in ("rollback", "drop"):
        raise ValueError(f"fragment_policy {cfg['fragment_policy']!r} not in ('rollback', 'drop')")
    st = {k: 0 for k in COUNTERS}
    st["pairs"] = 1
    na, nb = names
    if budget is None:
        budget = {"cap": {na: int(math.floor(cfg["node_cap_frac"] * len(ga[0]))),
                          nb: int(math.floor(cfg["node_cap_frac"] * len(gb[0])))}, "used": {na: 0, nb: 0}}
    ga_in, gb_in = ga, gb
    W = {"A": _Work(*as_graph(*ga)), "B": _Work(*as_graph(*gb))}
    off = tuple(int(o) for o in offset)
    info = _components(W["A"], W["B"], tuple(shape_a), tuple(shape_b), off, cfg)
    st["overlap_nodes_a"], st["overlap_nodes_b"] = len(info["ov_a"]), len(info["ov_b"])
    st["matched"], st["agree"] = len(info["corr_ab"]), len(info["agree_a"])
    st["components"] = len(info["components"])
    dt, dz, dy, dx = off
    for comp in info["components"]:
        pts = [info["pos_a"][nid] if side == "A" else info["pos_b"][nid] for side, nid in comp]
        sa = float(np.mean([border_score(p, shape_a, cfg["scale_um"]) for p in pts]))
        sb = float(np.mean([border_score((p[0] - dt, p[1] - dz, p[2] - dy, p[3] - dx), shape_b, cfg["scale_um"])
                            for p in pts]))
        owner = "B" if sb > sa + cfg["margin_um"] else "A"
        st["owner_" + owner.lower()] += 1
        s_own, s_non = (sb, sa) if owner == "B" else (sa, sb)
        if any(nid in W[side].fork_nodes for side, nid in comp):
            st["skipped_fork"] += 1
            continue
        if cfg["min_gap"] is not None and s_own - s_non < cfg["min_gap"]:
            st["skipped_gap"] += 1
            continue
        if cfg["max_nonowner"] is not None and s_non >= cfg["max_nonowner"]:
            st["skipped_nonowner"] += 1
            continue
        if third is not None:
            s3 = third(pts)
            if s3 is not None and s3 > s_own:
                st["skipped_third"] += 1
                continue
        _splice_component(comp, owner, info, W, off, cfg, budget, {"A": na, "B": nb}, st)
    return W["A"].result(ga_in), W["B"].result(gb_in), st


def splice_all(graphs: dict, shapes: dict, pairs: list, cfg: dict | None = None, log=None) -> tuple[dict, dict]:
    """Splice every accepted pair (tools/overlap_reg.register()['pairs']) in (a, b) order on the evolving graphs.
    graphs {name: (nodes, edges)}, shapes {name: (T, Z, Y, X)}. The node budget (node_cap_frac of each video's
    ORIGINAL node count) is shared over all pairs of a video. With 3+ copies a component is left to the pair of the
    copy with the best score (skipped_third). -> (graphs', stats with 'total' and 'per_pair')."""
    cfg = {**DEFAULTS, **(cfg or {})}
    out = dict(graphs)
    budget = {"cap": {n: int(math.floor(cfg["node_cap_frac"] * len(g[0]))) for n, g in graphs.items()},
              "used": {n: 0 for n in graphs}}
    offs: dict = defaultdict(dict)  # offs[a][c] = coord_a - coord_c
    for p in pairs:
        a, b, o = p["a"], p["b"], tuple(int(x) for x in p["offset"])
        if a in graphs and b in graphs:
            offs[a][b] = o
            offs[b][a] = tuple(-x for x in o)
    total = {k: 0 for k in COUNTERS}
    per_pair = []
    for p in sorted(pairs, key=lambda q: (q["a"], q["b"])):
        a, b = p["a"], p["b"]
        if a not in graphs or b not in graphs:
            continue
        off = tuple(int(x) for x in p["offset"])

        def third(pts, _a=a, _b=b):
            best = None
            for c, oac in offs[_a].items():
                if c in (_a, _b):
                    continue
                q = [(t - oac[0], z - oac[1], y - oac[2], x - oac[3]) for t, z, y, x in pts]
                if not all(inside(r, shapes[c]) for r in q):
                    continue
                s = float(np.mean([border_score(r, shapes[c], cfg["scale_um"]) for r in q]))
                best = s if best is None else max(best, s)
            return best

        ga2, gb2, st = splice_pair(out[a], out[b], shapes[a], shapes[b], off, cfg, budget, (a, b), third)
        out[a], out[b] = ga2, gb2
        per_pair.append({"a": a, "b": b, **st})
        for k in COUNTERS:
            total[k] += st[k]
        if log is not None:
            log(f"OVERLAPCONS pair {a} {b} off {list(off)}: comps {st['components']} spliced {st['spliced']} "
                f"(fork {st['skipped_fork']} bnd {st['skipped_boundary']} cap {st['skipped_cap']} "
                f"frag {st['skipped_fragment']}) "
                f"nodes +{st['nodes_added']}/-{st['nodes_removed']}")
    total["videos_changed"] = sum(1 for n in graphs if out[n] is not graphs[n])
    total["net_nodes"] = {n: budget["used"][n] for n in graphs if budget["used"][n]}
    return out, {"total": total, "per_pair": per_pair}
