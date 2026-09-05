"""Lightweight graph post-processing for prediction .geff files (CPU, local).

Ops (all optional, applied in this order):
  1. gap closing      : link track end at t to track start at t+2 (insert a midpoint node) if within gap_um
  2. prune isolated   : drop nodes with no edges
  3. short components : drop weakly-connected components with fewer than min_len nodes (keep ones with a division if keep_div)

Usage:
  python tools/postproc.py IN_DIR OUT_DIR --min-len 6 --gap-um 5.0
  from tools.postproc import process_dir
"""
from __future__ import annotations
import argparse, math, shutil
from pathlib import Path
import numpy as np
import networkx as nx
import geff
from scipy.spatial import cKDTree

VOXEL = np.array([1.625, 0.40625, 0.40625])  # z, y, x um


def load(path: Path) -> nx.DiGraph:
    g, _meta = geff.read(path, structure_validation=False)
    assert isinstance(g, nx.DiGraph)
    # keep only ILP-solution edges/nodes when the flag is present
    if any("solution" in d for _, d in g.nodes(data=True)):
        g.remove_nodes_from([n for n, d in g.nodes(data=True) if d.get("solution") is False])
    if any("solution" in d for _, _, d in g.edges(data=True)):
        g.remove_edges_from([(u, v) for u, v, d in g.edges(data=True) if d.get("solution") is False])
    return g


def save(g: nx.DiGraph, path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    for n, d in g.nodes(data=True):
        for k in ("t", "z", "y", "x"):
            d[k] = float(d[k]) if k != "t" else int(d["t"])
        d.pop("solution", None)
    for u, v, d in g.edges(data=True):
        d.pop("solution", None)
    geff.write(g, path, axis_names=["t", "z", "y", "x"], axis_types=["time", "space", "space", "space"],
               zarr_format=3, structure_validation=False)


def _pos(d) -> np.ndarray:
    return np.array([d["z"], d["y"], d["x"]], dtype=float) * VOXEL


def gap_close(g: nx.DiGraph, gap_um: float, max_gap: int = 1, min_prob: float | None = None) -> int:
    """Connect track ends (out-degree 0) at t to track starts (in-degree 0) at t+gap+1 by nearest neighbour
    within gap_um (um, per frame step scaled by gap+1), inserting synthetic midpoint nodes. Greedy, mutual-NN."""
    added = 0
    next_id = max(g.nodes) + 1 if g.number_of_nodes() else 0
    ends: dict[int, list] = {}
    starts: dict[int, list] = {}
    for n, d in g.nodes(data=True):
        if g.out_degree(n) == 0:
            ends.setdefault(int(d["t"]), []).append(n)
        if g.in_degree(n) == 0:
            starts.setdefault(int(d["t"]), []).append(n)
    for gap in range(1, max_gap + 1):
        for t, e_nodes in sorted(ends.items()):
            s_nodes = starts.get(t + gap + 1, [])
            e_nodes = [n for n in e_nodes if g.out_degree(n) == 0]
            s_nodes = [n for n in s_nodes if g.in_degree(n) == 0]
            if not e_nodes or not s_nodes:
                continue
            ep = np.stack([_pos(g.nodes[n]) for n in e_nodes]); sp = np.stack([_pos(g.nodes[n]) for n in s_nodes])
            te = cKDTree(ep); ts = cKDTree(sp)
            r = gap_um * (gap + 1)
            d_es, i_es = ts.query(ep, k=1, distance_upper_bound=r)
            d_se, i_se = te.query(sp, k=1, distance_upper_bound=r)
            for ei, (dist, si) in enumerate(zip(d_es, i_es)):
                if not np.isfinite(dist) or si >= len(s_nodes):
                    continue
                if i_se[si] != ei:  # mutual nearest neighbour
                    continue
                a, b = e_nodes[ei], s_nodes[si]
                da, db = g.nodes[a], g.nodes[b]
                prev = a
                for k in range(1, gap + 1):
                    f = k / (gap + 1)
                    nid = next_id; next_id += 1
                    g.add_node(nid, t=int(da["t"]) + k,
                               z=float(da["z"] + f * (db["z"] - da["z"])),
                               y=float(da["y"] + f * (db["y"] - da["y"])),
                               x=float(da["x"] + f * (db["x"] - da["x"])))
                    g.add_edge(prev, nid, edge_prob=0.5); prev = nid
                g.add_edge(prev, b, edge_prob=0.5)
                added += 1
    return added


def add_divisions(g: nx.DiGraph, parent_um: float = 7.0, sister_um: float = 12.0, max_frac: float = 0.01) -> int:
    """Post-hoc divisions: a node p at t with exactly one child c (t+1) gets a second child q if q is a
    track START at t+1 (in-degree 0), q is p's nearest unclaimed start within parent_um, the sisters c,q are within
    sister_um, and p is q's nearest single-child parent. Caps additions to max_frac of nodes. Returns #added."""
    starts: dict[int, list] = {}
    parents: dict[int, list] = {}
    for n, d in g.nodes(data=True):
        t = int(d["t"])
        if g.in_degree(n) == 0 and g.out_degree(n) >= 1:
            starts.setdefault(t, []).append(n)
        if g.out_degree(n) == 1:
            parents.setdefault(t, []).append(n)
    cap = max(1, int(max_frac * g.number_of_nodes()))
    added = 0
    for t, p_nodes in sorted(parents.items()):
        s_nodes = starts.get(t + 1, [])
        if not s_nodes:
            continue
        pp = np.stack([_pos(g.nodes[n]) for n in p_nodes]); sp = np.stack([_pos(g.nodes[n]) for n in s_nodes])
        tp, ts = cKDTree(pp), cKDTree(sp)
        d_ps, i_ps = ts.query(pp, k=1, distance_upper_bound=parent_um)
        d_sp, i_sp = tp.query(sp, k=1, distance_upper_bound=parent_um)
        for pi, (dist, si) in enumerate(zip(d_ps, i_ps)):
            if not np.isfinite(dist) or si >= len(s_nodes) or i_sp[si] != pi:
                continue
            p, q = p_nodes[pi], s_nodes[si]
            if g.in_degree(q) != 0 or g.out_degree(p) != 1:
                continue
            c = next(iter(g.successors(p)))
            if np.linalg.norm(_pos(g.nodes[c]) - _pos(g.nodes[q])) > sister_um:
                continue
            g.add_edge(p, q, edge_prob=0.5); added += 1
            if added >= cap:
                return added
    return added


def prune_isolated(g: nx.DiGraph) -> int:
    iso = [n for n in g.nodes if g.degree(n) == 0]
    g.remove_nodes_from(iso)
    return len(iso)


def filter_short(g: nx.DiGraph, min_len: int, keep_div: bool = True) -> int:
    removed = 0
    for comp in list(nx.weakly_connected_components(g)):
        if len(comp) >= min_len:
            continue
        if keep_div and any(g.out_degree(n) >= 2 for n in comp):
            continue
        g.remove_nodes_from(comp); removed += 1
    return removed


def process(g: nx.DiGraph, min_len: int = 0, gap_um: float = 0.0, max_gap: int = 1, keep_div: bool = True,
            div_parent_um: float = 0.0, div_sister_um: float = 12.0, div_max_frac: float = 0.01) -> dict:
    stats = {}
    if gap_um > 0:
        stats["gaps_closed"] = gap_close(g, gap_um, max_gap)
    if div_parent_um > 0:
        stats["divisions_added"] = add_divisions(g, div_parent_um, div_sister_um, div_max_frac)
    stats["isolated"] = prune_isolated(g)
    if min_len > 1:
        stats["short_removed"] = filter_short(g, min_len, keep_div)
    stats["nodes"] = g.number_of_nodes(); stats["edges"] = g.number_of_edges()
    return stats


def process_dir(in_dir: Path, out_dir: Path, **kw) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    outs = []
    for p in sorted(Path(in_dir).glob("*.geff")):
        g = load(p)
        st = process(g, **kw)
        o = out_dir / p.name
        save(g, o); outs.append(o)
        print(f"  {p.stem}: {st}", flush=True)
    return outs


