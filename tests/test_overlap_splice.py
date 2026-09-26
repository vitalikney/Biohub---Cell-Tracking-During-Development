"""OVERLAP-CONSENSUS splice (tools/overlap_splice.py): synthetic pairs of crops of one global scene.

Crops are (T, Z, Y, X) = (20, 20, 100, 100) voxels (z 1.625 um, y/x 0.40625 um). A covers global x [0, 100), B global
x [40, 140) -> B = global - (0, 0, 0, 40), offset = coord_a - coord_b = (0, 0, 0, 40); the overlap is global x [40, 100).

    python -m pytest tests/test_overlap_splice.py
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import overlap_splice as S  # noqa: E402

SHAPE = (20, 20, 100, 100)
OFF_B = (0, 0, 0, 40)


class G:
    """Tiny builder: tracks in GLOBAL coordinates, stored in the crop's own coordinates."""

    def __init__(self, origin=(0, 0, 0, 0)):
        self.o = origin
        self.nodes, self.edges, self.next = {}, [], 1
        self.ids = {}

    def node(self, key, t, z, y, x):
        nid = self.next
        self.next += 1
        self.nodes[nid] = {"t": t - self.o[0], "z": float(z - self.o[1]), "y": float(y - self.o[2]),
                           "x": float(x - self.o[3]), "score": 0.5}
        self.ids[key] = nid
        return nid

    def edge(self, k1, k2):
        self.edges.append({"source_id": self.ids[k1], "target_id": self.ids[k2], "edge_prob": 0.9})

    def track(self, name, ts, z, y, x, skip_edges=(), moved=None):
        prev = None
        for t in ts:
            yy = y + (moved or {}).get(t, 0.0)
            self.node((name, t), t, z, yy, x)
            if prev is not None and t not in skip_edges:
                self.edge((name, prev), (name, t))
            prev = t
        return self

    def g(self):
        return self.nodes, self.edges


def background(g: G) -> G:
    """Agreeing tracks inside the overlap plus one outside it on each side."""
    g.track("bg1", range(0, 20), 10, 30, 60)
    g.track("bg2", range(2, 18), 8, 70, 75)
    if g.o[3] == 0:
        g.track("onlyA", range(0, 20), 10, 50, 20)   # global x 20: outside B
    else:
        g.track("onlyB", range(0, 20), 10, 50, 120)  # global x 120: outside A
    return g


def chain_ok(nodes, edges, ts, xy):
    """One continuous track over ts at global (y, x) = xy (A coordinates = global)."""
    at = {int(n["t"]): nid for nid, n in nodes.items() if (round(n["y"]), round(n["x"])) == xy}
    assert sorted(at) == list(ts)
    pairs = {(e["source_id"], e["target_id"]) for e in edges}
    return all((at[t], at[t + 1]) in pairs for t in list(ts)[:-1])


def degrees_ok(nodes, edges):
    pred, succ = {}, {}
    for e in edges:
        assert e["source_id"] in nodes and e["target_id"] in nodes
        pred[e["target_id"]] = pred.get(e["target_id"], 0) + 1
        succ[e["source_id"]] = succ.get(e["source_id"], 0) + 1
    return max(pred.values(), default=0) <= 1 and max(succ.values(), default=0) <= 2


def test_border_score_and_inside():
    assert S.border_score((10, 10, 50, 95), SHAPE) == pytest.approx(4 * 0.40625)
    assert S.border_score((1, 10, 50, 50), SHAPE) == pytest.approx(1.0)
    assert S.border_score((10, 0, 50, 50), SHAPE) == 0.0
    assert S.inside((0, -0.4, 0, 99.5), SHAPE) and not S.inside((20, 1, 1, 1), SHAPE)
    assert not S.inside((0, 1, 1, 99.6), SHAPE)


def test_identity_when_copies_agree_and_when_no_pair():
    a = background(G()).track("t", range(3, 17), 10, 50, 95).g()
    b = background(G(OFF_B)).track("t", range(3, 17), 10, 50, 95).g()
    a2, b2, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B)
    assert a2 is a and b2 is b
    assert st["components"] == 0 and st["agree"] == st["matched"] == 14 + 20 + 16
    out, stats = S.splice_all({"e_a": a, "e_b": b}, {"e_a": SHAPE, "e_b": SHAPE}, [])
    assert out["e_a"] is a and out["e_b"] is b and stats["total"]["videos_changed"] == 0
    # a pair whose crops do not overlap at all
    a3, b3, st = S.splice_pair(a, b, SHAPE, SHAPE, (0, 0, 0, 400))
    assert a3 is a and b3 is b and st["overlap_nodes_a"] == 0


def test_discordant_component_spliced_to_owner_b():
    # global x 95 = 4 voxels (1.6 um) from A's x border, 55 voxels inside B: B owns. A misses the 9->10 link and
    # detects t=10 4.1 um off (unmatched at 2.5 um, grouped at 7 um).
    a = background(G()).track("t", range(3, 17), 10, 50, 95, skip_edges={10}, moved={10: 10.0}).g()
    b = background(G(OFF_B)).track("t", range(3, 17), 10, 50, 95).g()
    a2, b2, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B)
    assert b2 is b and a2 is not a
    assert st["components"] == 1 and st["owner_b"] == 1 and st["spliced_into_a"] == 1 and st["spliced"] == 1
    assert st["nodes_removed"] == 3 and st["nodes_added"] == 3
    nodes, edges = a2
    assert len(nodes) == len(a[0]) and chain_ok(nodes, edges, range(3, 17), (50, 95))
    assert degrees_ok(nodes, edges)
    # everything outside the component is untouched, in its original order
    kept = [e for e in a[1] if e["source_id"] in nodes and e["target_id"] in nodes]
    assert edges[:len(kept)] == kept
    assert all(nodes[i] is a[0][i] for i in a[0] if i in nodes)
    # imported nodes carry B's attributes in A's coordinates, with fresh ids
    new = [i for i in nodes if i not in a[0]]
    assert len(new) == 3 and min(new) > max(a[0])
    assert all(nodes[i]["x"] == 95.0 and nodes[i]["y"] == 50.0 and nodes[i]["score"] == 0.5 for i in new)


def test_owner_a_splices_into_b():
    # global x 45: 5 voxels (2.0 um) from B's x border, 45 voxels inside A: A owns and repairs B.
    a = background(G()).track("t", range(3, 17), 10, 50, 45).g()
    b = background(G(OFF_B)).track("t", range(3, 17), 10, 50, 45, skip_edges={8}, moved={8: -10.0}).g()
    a2, b2, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B)
    assert a2 is a and b2 is not b and st["spliced_into_b"] == 1 and st["owner_a"] == 1
    nodes, edges = b2
    at = sorted(int(n["t"]) for n in nodes.values() if (round(n["y"]), round(n["x"])) == (50, 5))
    assert at == list(range(3, 17)) and degrees_ok(nodes, edges)


def test_fork_components_skipped():
    a = background(G()).track("t", range(3, 17), 10, 50, 95, skip_edges={10}, moved={10: 10.0}).g()
    gb = background(G(OFF_B)).track("t", range(3, 17), 10, 50, 95)
    gb.track("d", range(11, 17), 10, 64, 95)
    gb.edge(("t", 10), ("d", 11))  # B divides at t=10
    b = gb.g()
    a2, b2, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B)
    assert a2 is a and b2 is b and st["skipped_fork"] == 1 and st["spliced"] == 0


def test_min_gap_and_max_nonowner_restrictions():
    a = background(G()).track("t", range(3, 17), 10, 50, 95, skip_edges={10}, moved={10: 10.0}).g()
    b = background(G(OFF_B)).track("t", range(3, 17), 10, 50, 95).g()
    a2, _, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B, {"min_gap": 20.0})
    assert a2 is a and st["skipped_gap"] == 1
    a2, _, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B, {"max_nonowner": 1.0})
    assert a2 is a and st["skipped_nonowner"] == 1
    a2, _, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B, {"min_gap": 3.0, "max_nonowner": 8.0})
    assert a2 is not a and st["spliced_into_a"] == 1


def test_node_cap_and_imported_nodes():
    # A never detected t = 9..11: the splice imports B's nodes (net +3), which the 0.5% cap blocks on a small video
    a = background(G()).track("t", [t for t in range(3, 17) if t not in (9, 10, 11)], 10, 50, 95,
                               skip_edges={12}).g()
    b = background(G(OFF_B)).track("t", range(3, 17), 10, 50, 95).g()
    a2, _, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B)
    assert a2 is a and st["skipped_cap"] == 1
    a2, _, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B, {"node_cap_frac": 1.0})
    assert st["spliced_into_a"] == 1 and len(a2[0]) == len(a[0]) + 3
    assert chain_ok(*a2, range(3, 17), (50, 95)) and degrees_ok(*a2)
    # an explicit shared budget: 2 net nodes allowed -> blocked, 3 -> allowed and used up
    bud = {"cap": {"A": 2, "B": 2}, "used": {"A": 0, "B": 0}}
    a2, _, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B, budget=bud)
    assert a2 is a and st["skipped_cap"] == 1
    bud = {"cap": {"A": 3, "B": 0}, "used": {"A": 0, "B": 0}}
    a2, _, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B, budget=bud)
    assert st["spliced"] == 1 and bud["used"]["A"] == 3


def test_short_fragments_dropped_without_change():
    a = background(G()).g()
    b = background(G(OFF_B)).track("f", (5, 6), 10, 80, 95).g()  # a 2-node track only B has
    a2, b2, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B, {"node_cap_frac": 1.0})
    assert a2 is a and b2 is b and st["fragment_nodes_dropped"] == 2 and st["spliced"] == 0


def test_receiver_edges_leaving_the_overlap_block_the_splice():
    # A's track leaves the overlap (global x 45 -> 30); force B as owner through a huge negative margin
    ga = background(G())
    ga.track("t", range(3, 9), 10, 50, 45)
    ga.track("u", range(9, 15), 10, 50, 30)
    ga.edge(("t", 8), ("u", 9))
    a = ga.g()
    b = background(G(OFF_B)).g()
    a2, b2, st = S.splice_pair(a, b, SHAPE, SHAPE, OFF_B, {"margin_um": -1000.0, "node_cap_frac": 1.0})
    assert a2 is a and b2 is b and st["skipped_boundary"] == 1


def test_three_copies_argmax_owner():
    # A: global; B: global - (2, 0, 0, 40); C: global - (0, 0, 0, 60). The component (t 9..11, x 95) scores 1.6 in A,
    # 8.0 in B (time-limited), 8.7 in C -> pair (A, B) leaves it to C, pair (A, C) splices C's version into A.
    a = background(G()).track("t", range(3, 17), 10, 50, 95, skip_edges={10}, moved={10: 10.0}).g()
    b = G((2, 0, 0, 40)).track("t", range(3, 17), 10, 50, 95).track("bg1", range(3, 20), 10, 30, 60).g()
    c = G((0, 0, 0, 60)).track("t", range(3, 17), 10, 50, 95).g()
    graphs = {"e_a": a, "e_b": b, "e_c": c}
    shapes = {k: SHAPE for k in graphs}
    pairs = [{"a": "e_a", "b": "e_b", "offset": [2, 0, 0, 40]}, {"a": "e_a", "b": "e_c", "offset": [0, 0, 0, 60]},
             {"a": "e_b", "b": "e_c", "offset": [-2, 0, 0, 20]}]
    lines = []
    out, stats = S.splice_all(graphs, shapes, pairs, log=lines.append)
    pp = {(p["a"], p["b"]): p for p in stats["per_pair"]}
    assert pp[("e_a", "e_b")]["skipped_third"] == 1 and pp[("e_a", "e_b")]["spliced"] == 0
    assert pp[("e_a", "e_c")]["spliced_into_a"] == 1
    assert out["e_b"] is b and out["e_c"] is c and stats["total"]["videos_changed"] == 1
    assert chain_ok(*out["e_a"], range(3, 17), (50, 95)) and len(lines) == 3


def test_rows_roundtrip_and_tuple_edges():
    a = background(G()).g()
    rows = S.rows_from_graphs({"e_a": a})
    back = S.graphs_from_rows(rows)["e_a"]
    assert sorted(back[0]) == sorted(a[0])
    assert [(e["source_id"], e["target_id"]) for e in back[1]] == [(e["source_id"], e["target_id"]) for e in a[1]]
    nodes, edges = S.as_graph(a[0], [(e["source_id"], e["target_id"]) for e in a[1]])
    b = background(G(OFF_B)).g()
    a2, b2, st = S.splice_pair((nodes, [(e["source_id"], e["target_id"]) for e in edges]), b, SHAPE, SHAPE, OFF_B)
    assert st["components"] == 0
