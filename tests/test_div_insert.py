"""Unit tests for tools/div_insert.py on small synthetic graphs (plain asserts; pytest-compatible).

    python tests/test_div_insert.py        # or: python -m pytest tests/test_div_insert.py
"""
from __future__ import annotations

import copy
import io
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import tools.div_insert as di  # noqa: E402
from tools.div_insert import candidate_triples, insert_divisions  # noqa: E402

S = di.DIVINS_VOXEL_SCALE_UM


def node(t, z_um, y_um, x_um, **flags):
    """Node dict in VOXEL units from a position given in um."""
    return {"t": t, "z": z_um / S[0], "y": y_um / S[1], "x": x_um / S[2], **flags}


def edge(s, t, p=0.9, **flags):
    return {"source_id": s, "target_id": t, "edge_prob": p, **flags}


P_HI = (0.1, 0.8, 0.8)  # (p_cont, p_par, p_dau) -> score 0.8 * 0.8 * 0.8 = 0.512 with alpha = 1


def scene(nodes, edges, base_id, t, y0=0.0, x0=0.0, v_dx=-4.0, c1_dx=4.0):
    """Canonical division scene: u at (0, y0, x0) at t with single child c1 (+c1_dx in x) and an orphan v (+v_dx)."""
    u, c1, v = base_id, base_id + 1, base_id + 2
    nodes[u] = node(t, 0.0, y0, x0)
    nodes[c1] = node(t + 1, 0.0, y0, x0 + c1_dx)
    nodes[v] = node(t + 1, 0.0, y0, x0 + v_dx)
    edges.append(edge(u, c1))
    return u, c1, v


def params(**kw):
    base = {"enable": 1, "steal": 0, "cap_video": 3, "cap_frame": 1, "alpha": 1.0, "threshold": 0.5}
    base.update(kw)
    return base


def all_p(nodes, p=P_HI):
    return {i: p for i in nodes}


def pairs(edges):
    return [(int(e["source_id"]), int(e["target_id"])) for e in edges]


# ---------------------------------------------------------------------------------------------------------------------
def test_orphan_insertion():
    nodes, edges = {}, []
    u, c1, v = scene(nodes, edges, 1, t=5)
    before = copy.deepcopy(edges)
    assert candidate_triples(nodes, edges, params()) == [(u, c1, v)]
    out, st = insert_divisions(nodes, edges, all_p(nodes), params())
    assert pairs(out) == [(u, c1), (u, v)]
    assert st["divins_added"] == 1 and st["divins_added_orphan"] == 1 and st["divins_added_steal"] == 0
    new = out[-1]
    assert new["div_inserted"] == 1 and new["div_c1"] == c1 and new["div_steal_from"] == -1
    assert abs(new["div_score"] - 0.512) < 1e-9 and abs(new["distance_um"] - 4.0) < 1e-9
    assert edges == before and out[0] is edges[0], "input edges must not be mutated or copied"
    assert all(isinstance(v_, (int, float)) for v_ in st.values()), "stats must be scalars"


def test_geometry_gates():
    def one(c1_um, v_um, **v_flags):
        nodes = {1: node(0, 0, 0, 0), 2: node(1, *c1_um), 3: node(1, *v_um, **v_flags)}
        return candidate_triples(nodes, [edge(1, 2)], params())

    assert one((0, 0, 4), (0, 0, -4)) == [(1, 2, 3)]            # positive control
    assert one((0, 0, 4), (0, 0, -16)) == []                    # |v - u| 16 > 15
    assert one((0, 0, 1.4), (0, 0, -1.4)) == []                 # sister 2.8 < 3
    assert one((0, 0, 9.9), (0, 0, -10.5)) == []                # sister 20.4 > 20
    assert one((0, 0, 4), (0, 14, 0)) == []                     # midpoint offset 7.3 > 6.5
    assert one((0, 0, 4), (0, 12, 0)) == [(1, 2, 3)]            # midpoint offset 6.3 <= 6.5
    assert one((0, 0, 4), (0, 3, 3)) == []                      # cos 0.71 > 0.25
    assert one((0, 0, 10.5), (0, 0, -5)) == []                  # |c1 - u| 10.5 > 10
    assert one((0, 0, 4), (0, 0, -4), gap_synthetic=1) == []    # single-gap synthetic v
    assert one((0, 0, 4), (0, 0, -4), gap2_synthetic=1) == []   # gap2 synthetic v (flag added by the patch)
    # c1 not at t + 1 -> u is not a parent candidate
    nodes = {1: node(0, 0, 0, 0), 2: node(2, 0, 0, 4), 3: node(1, 0, 0, -4)}
    assert candidate_triples(nodes, [edge(1, 2)], params()) == []


def test_video_cap():
    nodes, edges, trip = {}, [], []
    for k in range(5):
        trip.append(scene(nodes, edges, 10 * (k + 1), t=2 * k, y0=100.0 * k))
    p = all_p(nodes)
    for k, (u, _, _) in enumerate(trip):
        p[u] = (0.1, 0.5 + 0.1 * k, 0.1)  # scene k has score (0.5 + 0.1k) * 0.8 * 0.8 -> best = last scenes
    out, st = insert_divisions(nodes, edges, p, params(cap_video=3, threshold=0.1))
    added = [pr for pr in pairs(out) if pr not in pairs(edges)]
    assert st["divins_added"] == 3 and len(added) == 3
    assert set(added) == {(trip[k][0], trip[k][2]) for k in (2, 3, 4)}
    assert st["divins_skipped_cap_video"] == 2
    out0, st0 = insert_divisions(nodes, edges, p, params(cap_video=0, threshold=0.1))
    assert out0 is edges and st0["divins_added"] == 0


def test_frame_cap():
    nodes, edges, trip = {}, [], []
    for k in range(3):
        trip.append(scene(nodes, edges, 10 * (k + 1), t=4, y0=100.0 * k))
    p = all_p(nodes)
    p[trip[1][0]] = (0.0, 0.95, 0.0)  # scene 1 is the best in the frame
    out, st = insert_divisions(nodes, edges, p, params(cap_video=6, cap_frame=1))
    assert st["divins_added"] == 1 and (trip[1][0], trip[1][2]) in pairs(out)
    assert st["divins_skipped_cap_frame"] == 2
    _, st2 = insert_divisions(nodes, edges, p, params(cap_video=6, cap_frame=2))
    assert st2["divins_added"] == 2
    out0, st0 = insert_divisions(nodes, edges, p, params(cap_video=6, cap_frame=0))
    assert out0 is edges and st0["divins_added"] == 0
    # a second frame gets its own slot
    trip.append(scene(nodes, edges, 100, t=7))
    _, st3 = insert_divisions(nodes, edges, all_p(nodes), params(cap_video=6, cap_frame=1))
    assert st3["divins_added"] == 2


def test_no_fork_breaking():
    # u already divides -> not a parent candidate
    nodes = {1: node(0, 0, 0, 0), 2: node(1, 0, 0, 4), 3: node(1, 0, 4, 0), 4: node(1, 0, 0, -4)}
    edges = [edge(1, 2), edge(1, 3)]
    assert candidate_triples(nodes, edges, params()) == []
    out, st = insert_divisions(nodes, edges, all_p(nodes), params(cap_video=6))
    assert out is edges and st["divins_added"] == 0
    # randomized invariants, orphan mode: every input edge survives, targets were orphans, sources had out-degree 1
    rng = random.Random(7)
    total_added = 0
    for trial in range(20):
        nodes, edges = {}, []
        nid = 0
        for t in range(6):
            for _ in range(25):
                nid += 1
                nodes[nid] = node(t, rng.uniform(0, 20), rng.uniform(0, 40), rng.uniform(0, 40))
        by_t = {}
        for i, n in nodes.items():
            by_t.setdefault(n["t"], []).append(i)
        for t in range(5):
            targets = by_t[t + 1][:]
            rng.shuffle(targets)
            for s in by_t[t]:
                r = rng.random()
                if r < 0.6 and targets:
                    edges.append(edge(s, targets.pop(), p=rng.random()))
                elif r < 0.7 and len(targets) >= 2:
                    edges.append(edge(s, targets.pop(), p=rng.random()))
                    edges.append(edge(s, targets.pop(), p=rng.random()))
        before = copy.deepcopy(edges)
        nodes_before = copy.deepcopy(nodes)
        outdeg = {}
        indeg = {}
        for e in edges:
            outdeg[e["source_id"]] = outdeg.get(e["source_id"], 0) + 1
            indeg[e["target_id"]] = indeg.get(e["target_id"], 0) + 1
        p = {i: (rng.random(), rng.random(), rng.random()) for i in nodes}
        out, st = insert_divisions(nodes, edges, p, params(cap_video=50, cap_frame=50, threshold=0.0))
        assert nodes == nodes_before and edges == before
        assert out[:len(edges)] == edges, "orphan mode must keep every input edge, in order"
        new = out[len(edges):]
        assert len(new) == st["divins_added"]
        seen = set()
        for e in new:
            u, v, c1 = e["source_id"], e["target_id"], e["div_c1"]
            assert outdeg.get(u, 0) == 1 and indeg.get(v, 0) == 0
            assert not ({u, v, c1} & seen), "a node may take part in one inserted division only"
            seen |= {u, v, c1}
        total_added += len(new)
    assert total_added >= 20, total_added


def test_used_once():
    # shared v: two one-child parents next to the same orphan
    nodes = {1: node(0, 0, 0, 0), 2: node(1, 0, 0, 4), 3: node(0, 0, 2, -8), 4: node(1, 0, 2, -12),
             5: node(1, 0, 1, -4)}
    edges = [edge(1, 2), edge(3, 4)]
    tr = candidate_triples(nodes, edges, params())
    assert {t_[2] for t_ in tr} == {5} and len({t_[0] for t_ in tr}) == 2
    out, st = insert_divisions(nodes, edges, all_p(nodes), params(cap_video=6, cap_frame=6))
    assert st["divins_added"] == 1 and st["divins_skipped_used"] == 1
    # shared u: two orphans on the far side of c1
    nodes = {1: node(0, 0, 0, 0), 2: node(1, 0, 0, 4), 3: node(1, 0, 0, -4), 4: node(1, 0, 1.5, -4.5)}
    edges = [edge(1, 2)]
    assert len(candidate_triples(nodes, edges, params())) == 2
    _, st = insert_divisions(nodes, edges, all_p(nodes), params(cap_video=6, cap_frame=6))
    assert st["divins_added"] == 1
    # shared c1 (malformed in-degree 2): u1 -> c1 <- u2, one orphan next to each parent
    nodes = {1: node(0, 0, 0, 0), 2: node(0, 0, 3, 0), 3: node(1, 0, 1.5, 4), 4: node(1, 0, 0, -4),
             5: node(1, 0, 3, -4)}
    edges = [edge(1, 3), edge(2, 3)]
    tr = candidate_triples(nodes, edges, params())
    assert {t_[1] for t_ in tr} == {3} and {t_[0] for t_ in tr} == {1, 2}
    _, st = insert_divisions(nodes, edges, all_p(nodes), params(cap_video=6, cap_frame=6))
    assert st["divins_added"] == 1
    # cross role: v of the division at t is the parent u of a candidate division at t + 1 -> only one is inserted
    nodes = {1: node(0, 0, 0, 0), 2: node(1, 0, 0, 4), 3: node(1, 0, 0, -4),
             4: node(2, 0, 0, -1), 5: node(2, 0, 0, -8)}
    edges = [edge(1, 2), edge(3, 5)]
    tr = candidate_triples(nodes, edges, params())
    assert (1, 2, 3) in tr and (3, 5, 4) in tr
    _, st = insert_divisions(nodes, edges, all_p(nodes), params(cap_video=6, cap_frame=6))
    assert st["divins_added"] == 1


def steal_scene(ep, w_fork=False, base=1, t=0, y0=0.0):
    """u -> c1 (+4 um), v (-4 um) already owned by w (-7 um at t) through w -> v with edge_prob ep."""
    u, c1, v, w = base, base + 1, base + 2, base + 3
    nodes = {u: node(t, 0, y0, 0), c1: node(t + 1, 0, y0, 4), v: node(t + 1, 0, y0, -4), w: node(t, 0, y0, -7)}
    edges = [edge(u, c1, p=0.9), edge(w, v, p=ep)]
    if w_fork:
        nodes[base + 4] = node(t + 1, 0, y0 - 30, -7)
        edges.append(edge(w, base + 4, p=0.9))
    return nodes, edges, (u, c1, v, w)


def test_steal_gating():
    P9 = (0.05, 0.9, 0.9)  # score 0.729 with alpha = 1
    nodes, edges, (u, c1, v, w) = steal_scene(0.1)
    out, st = insert_divisions(nodes, edges, all_p(nodes, P9), params(steal=0, cap_video=2))
    assert out is edges and st["divins_triples"] == 0, "steal branch must be off by default"
    out, st = insert_divisions(nodes, edges, all_p(nodes, P9), params(steal=1, cap_video=2))
    assert st["divins_added_steal"] == 1 and pairs(out) == [(u, c1), (u, v)], pairs(out)
    assert out[-1]["div_steal_from"] == w and abs(out[-1]["div_stolen_edge_prob"] - 0.1) < 1e-12
    assert len(edges) == 2, "input list untouched"
    for ep in (0.3, 0.35, None, float("nan")):
        nodes, edges, _ = steal_scene(ep)
        out, st = insert_divisions(nodes, edges, all_p(nodes, P9), params(steal=1, cap_video=2))
        assert out is edges and st["divins_triples"] == 0, ep
    nodes, edges, _ = steal_scene(0.1, w_fork=True)  # w divides -> never robbed
    out, st = insert_divisions(nodes, edges, all_p(nodes, P9), params(steal=1, cap_video=2))
    assert out is edges and st["divins_triples"] == 0
    # score margin: ep 0.25 needs score >= 0.45 (alpha = 0: score = p_par(u) * p_dau(v))
    nodes, edges, (u, c1, v, w) = steal_scene(0.25)
    p = all_p(nodes, (0.3, 0.3, 0.3))
    p[u] = (0.1, 0.8, 0.1)
    p[v] = (0.1, 0.1, 0.5)   # 0.40 < 0.45
    out, st = insert_divisions(nodes, edges, p, params(steal=1, cap_video=2, alpha=0.0, threshold=0.3))
    assert out is edges and st["divins_steal_margin_rejected"] == 1
    p[v] = (0.1, 0.1, 0.5625)  # 0.45 >= 0.45
    out, st = insert_divisions(nodes, edges, p, params(steal=1, cap_video=2, alpha=0.0, threshold=0.3))
    assert st["divins_added_steal"] == 1
    # steals <= floor(cap / 2)
    nodes, edges = {}, []
    for k in range(3):
        n_, e_, _ = steal_scene(0.1, base=10 * (k + 1), t=3 * k, y0=100.0 * k)
        nodes.update(n_)
        edges.extend(e_)
    for cap, want in ((1, 0), (2, 1), (3, 1), (4, 2), (6, 3)):
        _, st = insert_divisions(nodes, edges, all_p(nodes, P9), params(steal=1, cap_video=cap, cap_frame=1))
        assert st["divins_added_steal"] == want, (cap, st)
    _, st = insert_divisions(nodes, edges, all_p(nodes, P9), params(steal=1, cap_video=1))
    assert st["divins_skipped_steal_cap"] == 3
    # orphans still fill the cap next to a limited steal budget
    n_, e_, trip = {}, [], []
    for k in range(2):
        trip.append(scene(n_, e_, 1000 + 10 * k, t=20 + 2 * k, y0=500.0 + 100 * k))
    nodes.update(n_)
    edges.extend(e_)
    _, st = insert_divisions(nodes, edges, all_p(nodes, P9), params(steal=1, cap_video=3, cap_frame=1))
    assert st["divins_added"] == 3 and st["divins_added_steal"] == 1 and st["divins_added_orphan"] == 2


def test_steal_never_takes_gap_edges():
    # v's parent edge is a gap2 edge and v continues along gap2 -> synthetic v, even with a (fake) low edge_prob
    nodes = {1: node(0, 0, 0, 0), 2: node(1, 0, 0, 4), 3: node(1, 0, 0, -4), 4: node(0, 0, 0, -7), 5: node(2, 0, 0, -5)}
    edges = [edge(1, 2), edge(4, 3, p=0.1, gap2_recovered=1), edge(3, 5, p=None, gap2_recovered=1)]
    assert candidate_triples(nodes, edges, params(steal=1)) == []
    # the real start node of a gap2 bridge (in-edge gap2, out-edge normal) with a None prob is not stealable either
    edges = [edge(1, 2), edge(4, 3, p=None, gap2_recovered=1), edge(3, 5, p=0.9)]
    assert candidate_triples(nodes, edges, params(steal=1)) == []


def test_enable0_identity():
    nodes, edges = {}, []
    scene(nodes, edges, 1, t=0)
    n0, e0 = copy.deepcopy(nodes), copy.deepcopy(edges)
    for flag in (0, "0", False):
        out, st = insert_divisions(nodes, edges, all_p(nodes), params(enable=flag, cap_video=6))
        assert out is edges and st["divins_enabled"] == 0 and st["divins_added"] == 0
    assert nodes == n0 and edges == e0
    out, st = insert_divisions(nodes, [], all_p(nodes), params())
    assert out == [] and st["divins_added"] == 0


def test_threshold_and_missing_p():
    nodes, edges = {}, []
    u, c1, v = scene(nodes, edges, 1, t=0)
    out, st = insert_divisions(nodes, edges, all_p(nodes, (0.5, 0.5, 0.5)), params(threshold=0.2))
    assert out is edges and st["divins_below_threshold"] == 1          # 0.125 < 0.2
    out, st = insert_divisions(nodes, edges, all_p(nodes, (0.5, 0.5, 0.5)), params(threshold=0.2, alpha=0.0))
    assert st["divins_added"] == 1                                      # 0.25 >= 0.2
    p = all_p(nodes)
    del p[c1]
    out, st = insert_divisions(nodes, edges, p, params())
    assert out is edges and st["divins_missing_p"] == 1


def test_params_validation():
    try:
        insert_divisions({}, [], {}, {"cap": 3})
    except ValueError as exc:
        assert "cap" in str(exc)
    else:
        raise AssertionError("unknown params key must raise")
    from types import SimpleNamespace
    nodes, edges = {}, []
    scene(nodes, edges, 1, t=0)
    _, st = insert_divisions(nodes, edges, all_p(nodes), SimpleNamespace(enable=1, steal=0, cap_video=3, cap_frame=1,
                                                                          alpha=1.0, threshold=0.5))
    assert st["divins_added"] == 1


def test_kdtree_prefilter_matches_brute_force():
    rng = np.random.default_rng(3)
    nodes, edges = {}, []
    nid = 0
    ids_t = {}
    for t in range(3):
        for _ in range(300):
            nid += 1
            nodes[nid] = node(t, *rng.uniform([0, 0, 0], [40, 80, 80]))
            ids_t.setdefault(t, []).append(nid)
    for t in range(2):
        for s, d in zip(ids_t[t][:150], ids_t[t + 1][:150]):
            edges.append(edge(s, d, p=float(rng.random())))
    for steal in (0, 1):
        with_tree = candidate_triples(nodes, edges, params(steal=steal))
        saved = di._DivinsKDTree
        try:
            di._DivinsKDTree = None
            brute = candidate_triples(nodes, edges, params(steal=steal))
        finally:
            di._DivinsKDTree = saved
        assert with_tree == brute and len(with_tree) > 0, (steal, len(with_tree), len(brute))


def test_dump_roundtrip():
    nodes, edges = {}, []
    scene(nodes, edges, 1, t=0)
    n_, e_, _ = steal_scene(0.1, base=20, t=3)
    nodes.update(n_)
    edges.extend(e_)
    nodes[40] = node(1, 0, 60, 0, gap_synthetic=1)
    nodes[41] = node(1, 0, 90, 0, gap2_synthetic=1)
    edges.append(edge(40, 41, p=None, gap_closed=1))
    P = params(steal=1, cap_video=4)
    triples = candidate_triples(nodes, edges, P)
    p = all_p(nodes, (0.05, 0.9, 0.9))
    out, _ = insert_divisions(nodes, edges, p, P)
    arrays = di.dump_arrays(nodes, edges, p, P, triples, out)
    buf = io.BytesIO()
    np.savez_compressed(buf, **arrays)
    buf.seek(0)
    with np.load(buf) as z:
        res = di.replay_dump(z)
    assert res["match"] is True and res["triples_match"] is True
    assert res["stats"]["divins_added"] == 2 and res["stats"]["divins_added_steal"] == 1
    assert len(arrays["removed"]) == 1


# ---------------------------------------------------------------------------------------------------------------------
# Verifier additions (2026-09-23): units, the kernel glue's frame reader / weight finder, score_nodes row order and
# lag clamping, and the builder's DIVINS-without-patch guard.
# ---------------------------------------------------------------------------------------------------------------------
def test_voxel_units_anisotropy():
    """Gates must use the per-axis voxel scale (z 1.625, y/x 0.40625 um/voxel), not isotropic voxels or um input."""
    def tri(c1_vox, v_vox):
        nodes = {1: {"t": 0, "z": 30.0, "y": 100.0, "x": 100.0},
                 2: {"t": 1, "z": 30.0 + c1_vox[0], "y": 100.0 + c1_vox[1], "x": 100.0 + c1_vox[2]},
                 3: {"t": 1, "z": 30.0 + v_vox[0], "y": 100.0 + v_vox[1], "x": 100.0 + v_vox[2]}}
        return candidate_triples(nodes, [edge(1, 2)], params())

    # 7 z-voxels = 11.4 um > 10 um parent gate (isotropic voxels would call it 2.8 um and accept)
    assert tri((7, 0, 0), (-3, 0, 0)) == []
    # 6 z-voxels = 9.75 um <= 10; v at -3 z-voxels = 4.9 um; sister 14.6 um -> accepted
    assert tri((6, 0, 0), (-3, 0, 0)) == [(1, 2, 3)]
    # 24 x-voxels = 9.75 um -> accepted; 25 x-voxels = 10.2 um -> rejected (anisotropy the other way round)
    assert tri((0, 0, 24), (0, 0, -12)) == [(1, 2, 3)]
    assert tri((0, 0, 25), (0, 0, -12)) == []
    # the inserted edge's distance_um is the notebook's edge_distance_um of (u, v)
    nodes = {1: {"t": 0, "z": 30.0, "y": 100.0, "x": 100.0}, 2: {"t": 1, "z": 36.0, "y": 100.0, "x": 100.0},
             3: {"t": 1, "z": 27.0, "y": 104.0, "x": 97.0}}
    out, st = insert_divisions(nodes, [edge(1, 2)], all_p(nodes), params())
    assert st["divins_added"] == 1
    want = ((3 * 1.625) ** 2 + (4 * 0.40625) ** 2 + (3 * 0.40625) ** 2) ** 0.5
    assert abs(out[-1]["distance_um"] - want) < 1e-12


def _kernel_glue_namespace(test_dir, read_test_frame):
    """Execute the builder's DIVINS_GLUE the way the notebook cell does (ENABLE=0: no model load)."""
    import json as _json
    import os as _os
    import time as _time

    import tools.build_probe_kernel as bpk
    import tools.daughternet as dn

    g = {"__name__": "__main__", "os": _os, "json": _json, "time": _time, "np": np, "Path": Path,
         "TEST_DIR": Path(test_dir), "read_test_frame": read_test_frame, "load_daughternet": dn.load_daughternet}
    g.update({k: v for k, v in vars(di).items() if not k.startswith("__")})
    saved = {k: _os.environ.pop(k) for k in list(_os.environ) if k.startswith("BIOHUB_DIVINS_")}
    try:
        exec(compile(bpk.DIVINS_GLUE, "divins_glue", "exec"), g)
    finally:
        _os.environ.update(saved)
    assert g["DIVINS_BUNDLE"] is None and g["BIOHUB_DIVINS_ENABLE"] == "0"
    return g


def _fake_video(tmp, dataset, T, shape=(20, 64, 64), seed=0):
    import json as _json
    zdir = Path(tmp) / f"{dataset}.zarr" / "0"
    zdir.mkdir(parents=True)
    (zdir / "zarr.json").write_text(_json.dumps({"shape": [T, *shape], "data_type": "uint16"}))
    rng = np.random.default_rng(seed)
    frames = [(rng.gamma(2.0, 50.0 * (k + 1), size=shape)).astype(np.uint16) for k in range(T)]
    calls = []

    def read_test_frame(ds, t, frame_cache):  # the notebook reader has NO clamp: out of range must fail loudly
        assert ds == dataset
        calls.append(int(t))
        if not 0 <= int(t) < T:
            raise IndexError(f"frame {t} outside [0, {T - 1}]")
        if t in frame_cache:
            return frame_cache[t]
        frame_cache[t] = frames[int(t)]
        return frame_cache[t]

    return frames, read_test_frame, calls


def test_kernel_frame_reader_clamps_and_keeps_cache_clean():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        T = 5
        frames, rtf, calls = _fake_video(tmp, "vid", T)
        g = _kernel_glue_namespace(tmp, rtf)
        reader = g["divins_frame_reader"]("vid")
        cache = {}
        assert reader("vid", -1, cache) is frames[0]
        assert reader("vid", T, cache) is frames[T - 1] and reader("vid", T + 1, cache) is frames[T - 1]
        assert reader("vid", 2, cache) is frames[2]
        assert calls == [0, T - 1, T - 1, 2] and cache == {}, (calls, cache)
        sentinel = np.zeros((20, 64, 64), np.uint16)
        cache = {3: sentinel}
        assert reader("vid", 3, cache) is sentinel and cache == {3: sentinel}  # pre-cached frame reused and kept


def test_score_nodes_row_order_and_lag_frames():
    """Kernel path (tools/daughternet.score_nodes + the glue's clamped reader): rows come back in INPUT order, and a node
    at t uses frames clamp(t-1, t, t+1, t+2) -> t=0 uses [0,0,1,2] and t=T-1 uses [T-2,T-1,T-1,T-1]."""
    import tempfile

    import torch

    import tools.daughternet as dn
    import tools.divnet_infer as dv
    with tempfile.TemporaryDirectory() as tmp:
        T = 5
        frames, rtf, _ = _fake_video(tmp, "vid", T, seed=1)
        g = _kernel_glue_namespace(tmp, rtf)
        reader = g["divins_frame_reader"]("vid")
        torch.manual_seed(0)
        model = dn.build_model(dn.DEFAULT_CFG)
        ckpt = Path(tmp) / "f0.pt"
        torch.save({"model_state": model.state_dict(), "config": dn.DEFAULT_CFG}, ckpt)
        bundle = dn.load_daughternet([ckpt], device="cpu")
        nodes = [{"t": T - 1, "z": 10.0, "y": 30.0, "x": 34.0}, {"t": 0, "z": 9.0, "y": 20.0, "x": 40.0},
                 {"t": 2, "z": 11.0, "y": 44.0, "x": 22.0}]
        cfg = dn.DEFAULT_CFG
        for n in nodes:
            got = dn.prepare_sample("vid", n["t"], n, bundle, {}, reader)
            used = [min(max(n["t"] + lag, 0), T - 1) for lag in cfg["input"]["image_lags"]]
            chans = []
            for ft in used:
                pooled = dv._normalise(dv._pool_xy(frames[ft], 4), 50.0, 99.5, (-0.5, 6.0))
                centre = (int(round(n["z"])), int(round(n["y"] / 4)), int(round(n["x"] / 4)))
                chans.append(dv._crop_with_padding(pooled, centre, (16, 32, 32)))
            chans.append(dv._marker((16, 32, 32), (1.5, 2.0, 2.0)))
            assert np.array_equal(got, np.stack(chans)), (n, used)
        bundle["prepared_frames"].clear()
        p_all = dn.score_nodes("vid", nodes, bundle, {}, reader, batch=2)
        p_one = np.concatenate([dn.score_nodes("vid", [n], bundle, {}, reader) for n in nodes])
        assert p_all.shape == (3, 3) and np.allclose(p_all, p_one, atol=1e-6), (p_all, p_one)
        assert np.allclose(p_all.sum(1), 1.0, atol=1e-5)
        assert not np.allclose(p_all[0], p_all[1], atol=1e-6), "degenerate test: rows must differ"


def test_kernel_weight_finder():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        g = _kernel_glue_namespace(tmp, lambda *a: None)
        root = Path(tmp) / "input"
        good = [root / "ds1" / "vitalii_daughternet" / "fold0.pt",
                root / "datasets" / "owner" / "biohub-ft-weights" / "vitalii_daughternet" / "fold1.pt"]
        bad = [root / "comp" / "train" / "x.zarr" / "vitalii_daughternet" / "d.pt",   # inside a zarr tree
               root / ".cache" / "vitalii_daughternet" / "h.pt",                      # hidden
               root / "a" / "b" / "c" / "d" / "e" / "f" / "g" / "vitalii_daughternet" / "deep.pt",  # depth > 6
               root / "ds1" / "other" / "fold9.pt"]                                   # wrong folder name
        for p in good + bad:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"x")
        found = g["divins_find_weights"](str(root) + "/**/vitalii_daughternet/*.pt")
        assert sorted(Path(p).resolve() for p in found) == sorted(p.resolve() for p in good), found
        # comma-separated, a plain (non-**) glob and a pattern matching nothing
        found2 = g["divins_find_weights"](f"{root}/ds1/other/*.pt, {root}/nothing/**/*.pt")
        assert [Path(p).name for p in found2] == ["fold9.pt"], found2


def test_builder_refuses_divins_knobs_without_patch():
    import subprocess
    root = Path(__file__).resolve().parent.parent
    name = "test_divins_guard_probe"
    r = subprocess.run([sys.executable, str(root / "tools" / "build_probe_kernel.py"), name, "--set", "DIVINS_ENABLE=1"],
                       capture_output=True, text=True, cwd=str(root))
    assert r.returncode != 0 and "divinsert" in (r.stderr + r.stdout), (r.returncode, r.stdout, r.stderr)
    assert not (root / "experiments" / name).exists()


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    for name, fn in tests:
        fn()
        print("ok", name)
    print(f"{len(tests)} tests passed")
