"""Offline sweep of the public pipeline's safe-division gate, scored with the official metric.

Re-implements the gate exactly as it runs inside the public inference notebook
(existing-child radius, parent radius, sister radius, mutual-NN, divergence,
symmetry, per-frame and global caps, ranking by parent_dist + 0.15*sister_dist),
applies it to prediction .geff graphs and scores the result against local GT.

The DeepCenter veto is NOT available offline, so this over-adds relative to the
kernel; use it to COMPARE gate settings, not to predict absolute LB scores.

Usage:
    python tools/sim_safediv.py <geff_dir_or_glob> [--tau 0.3 0.6 1.0] [--max-um 9.0]
                                [--sister-um 14.0] [--diverge-um 2.25] [--baseline]

SCORING: uses the OFFICIAL metric package (tools/official, tracking_cellmot). Do not
switch this back to tools/repo - that fork credits a GT division to any predicted fork
merely reachable in the same weakly connected component, which the organisers patched
out on 2026-07-17, and it changed the ranking of this very sweep (tau 1.0 looked like
the best setting under the fork and is worse than the public 0.6 under the official one).

WARNING on statistics: the 12-video hold-out set contains only 14 GT divisions, so a
single recovered division moves the score by ~0.004 and div_J by ~0.03. Differences
below ~0.01 on a set that small are single-event noise - sweep on the full 199-video
train set (151 GT divisions) before believing any ranking.
"""
import argparse
import glob as globmod
import json
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "official" / "src"))
sys.path.insert(0, str(ROOT / "official" / "scripts"))
sys.path.insert(0, str(ROOT))
PROJECT_ROOT = ROOT.parent
DATA = Path(
    os.environ.get(
        "BIOHUB_DATA_DIR",
        PROJECT_ROOT / "biohub-cell-tracking-during-development" / "train",
    )
)
os.environ["BIOHUB_DATA_DIR"] = str(DATA)

import numpy as np
import networkx as nx
import tracksdata as td
from scipy.spatial import cKDTree

import postproc
from tracking_cellmot.io import open_dataset
from tracking_cellmot.metrics import (
    evaluate as compute_metric,
    node_recall,
    per_sample_metrics,
    summarise,
)
from evaluate import _read_estimated_n_total

FRAME_FRAC_CAP = 0.0076
GLOBAL_FRAC_CAP = 0.00375
EXIST_CHILD_MAXU = 10.0


def add_safe_divisions(nodes, edges, scale, tau=0.6, max_um=9.0, sister_um=14.0, diverge_um=2.25, min_sister_um=0.0):
    """Return (added_edges, stats) for the gate applied to one prediction graph."""
    pos = {int(i): np.array([r.z, r.y, r.x]) * scale for i, r in nodes.iterrows()}
    tt = {int(i): int(r.t) for i, r in nodes.iterrows()}
    out, inc = {}, {}
    for s, d in edges:
        out.setdefault(s, []).append(d)
        inc.setdefault(d, []).append(s)

    def dist(a, b):
        return float(np.linalg.norm(pos[a] - pos[b]))

    by_t = {}
    for n, t in tt.items():
        by_t.setdefault(t, []).append(n)
    added, used_src, used_tgt = [], set(), set()
    global_cap = max(1, int(round(len(nodes) * GLOBAL_FRAC_CAP)))
    stats = dict(mutual_rejected=0, divergence_rejected=0, symmetry_rejected=0, geometric=0, min_sister_rejected=0)
    for t in sorted(by_t):
        child_ids = by_t.get(t + 1, [])
        if not child_ids:
            continue
        src_ids = [n for n in by_t[t] if len(out.get(n, [])) == 1]
        cand_ids = [n for n in child_ids if n not in inc and n not in used_tgt]
        if not src_ids or not cand_ids:
            continue
        ctree = cKDTree(np.stack([pos[c] for c in cand_ids]))
        frame_cap = max(1, int(round(len(src_ids) * FRAME_FRAC_CAP)))
        props = []
        for s in src_ids:
            ec = out[s][0]
            if tt.get(ec) != t + 1:
                continue
            child_dist = dist(s, ec)
            if child_dist > EXIST_CHILD_MAXU:
                continue
            _, ni = ctree.query(pos[ec])
            mutual = cand_ids[int(ni)]
            for q in cand_ids:
                parent_dist = dist(s, q)
                if parent_dist > max_um:
                    continue
                sister_dist = dist(ec, q)
                if sister_dist > sister_um:
                    continue
                if sister_dist < min_sister_um:
                    stats["min_sister_rejected"] += 1
                    continue
                if q != mutual:
                    stats["mutual_rejected"] += 1
                    continue
                c1s, qs = out.get(ec, []), out.get(q, [])
                if len(c1s) != 1 or len(qs) != 1:
                    stats["divergence_rejected"] += 1
                    continue
                g1, g2 = c1s[0], qs[0]
                if tt.get(g1) != t + 2 or tt.get(g2) != t + 2:
                    stats["divergence_rejected"] += 1
                    continue
                if dist(g1, g2) - sister_dist < diverge_um:
                    stats["divergence_rejected"] += 1
                    continue
                stats["geometric"] += 1
                denom = max((child_dist + parent_dist) / 2.0, 1e-6)
                if tau > 0.0 and abs(child_dist - parent_dist) / denom > tau:
                    stats["symmetry_rejected"] += 1
                    continue
                props.append((parent_dist + 0.15 * sister_dist, s, q))
        props.sort()
        n_frame = 0
        for _, s, q in props:
            if len(added) >= global_cap or n_frame >= frame_cap:
                break
            if q in used_tgt or q in inc or s in used_src:
                continue
            added.append((s, q))
            used_src.add(s)
            used_tgt.add(q)
            n_frame += 1
    return added, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("geffs", help="directory containing <video>.geff, or a glob")
    ap.add_argument("--tau", type=float, nargs="*", default=[0.6])
    ap.add_argument("--max-um", type=float, default=9.0)
    ap.add_argument("--sister-um", type=float, default=14.0)
    ap.add_argument("--diverge-um", type=float, default=2.25)
    ap.add_argument("--min-sister-um", type=float, nargs="*", default=[0.0],
                    help="lower bound on sister separation; real divisions have median 8.85 um, duplicate detections have near-zero")
    ap.add_argument("--baseline", action="store_true", help="also score the graphs unchanged")
    ap.add_argument("--out")
    a = ap.parse_args()
    wild = any(c in a.geffs for c in "*?")
    paths = sorted(globmod.glob(a.geffs)) if wild else sorted(str(p) for p in Path(a.geffs).glob("*.geff"))
    if not paths:
        sys.exit("no .geff found under " + a.geffs)
    cache, dss = {}, {}
    for g in paths:
        name = Path(g).stem
        pr = td.graph.IndexedRXGraph.from_geff(g)
        pred = pr[0] if isinstance(pr, tuple) else pr
        na = pred.node_attrs().to_pandas().set_index("node_id")
        ea = pred.edge_attrs().to_pandas()
        cache[name] = (
            na[["t", "z", "y", "x"]],
            list(zip(ea.source_id.astype(int), ea.target_id.astype(int))),
        )
        dss[name] = open_dataset(DATA / name, require_tracks=True, load_image=False)
    n_div = sum(len(d.tracks.dividing_nodes()) for d in dss.values())
    print(str(len(cache)) + " videos, " + str(n_div) + " GT divisions")
    tmp = Path(os.environ.get("TEMP", ".")) / "sim_safediv_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    results = []
    combos = [(t, m) for t in (([None] if a.baseline else []) + list(a.tau)) for m in a.min_sister_um]
    for tau, min_sis in combos:
        rows, tot = [], 0
        for name, (n, e) in cache.items():
            ds = dss[name]
            sc = np.array(ds.scale)
            extra = [] if tau is None else add_safe_divisions(
                n, e, sc, tau, a.max_um, a.sister_um, a.diverge_um, min_sis
            )[0]
            tot += len(extra)
            g2 = nx.DiGraph()
            for i, r in n.iterrows():
                g2.add_node(int(i), t=int(r.t), z=float(r.z), y=float(r.y), x=float(r.x))
            g2.add_edges_from(e)
            g2.add_edges_from(extra)
            postproc.save(g2, tmp / (name + ".geff"))
            pr = td.graph.IndexedRXGraph.from_geff(tmp / (name + ".geff"))
            p = pr[0] if isinstance(pr, tuple) else pr
            er = compute_metric(p, ds.tracks, scale=ds.scale)
            rows.append(
                {
                    "dataset": name,
                    **per_sample_metrics(
                        er, _read_estimated_n_total(DATA / (name + ".geff")), node_recall(p, ds.tracks)
                    ),
                }
            )
        s = summarise(rows)
        print(
            "tau=%s min_sister=%s: score=%.4f adj_edge=%.4f div_J=%.4f tp/fp/fn=%d/%d/%d added=%d"
            % (
                tau,
                min_sis,
                s["score"],
                s["adj_edge_jaccard"],
                s["division_jaccard"],
                s["division_tp"],
                s["division_fp"],
                s["division_fn"],
                tot,
            ),
            flush=True,
        )
        results.append(
            {
                "tau": tau,
                "min_sister_um": min_sis,
                "added": tot,
                **{k: (float(v) if isinstance(v, (int, float)) else v) for k, v in s.items()},
            }
        )
    if a.out:
        Path(a.out).write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
