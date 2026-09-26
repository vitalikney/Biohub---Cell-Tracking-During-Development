"""G-B lab driver (tools/overlap_lab.py): units, global frames, once-counted division events, pooling, bootstrap, gate,
CSV sanity, the splice arms on synthetic crops (scenes of tests/test_overlap_splice.py), and eval_clip parity with
tools/trainlab.official_eval on one real exp60 clip (skipped without the local data).

    python -m pytest tests/test_overlap_lab.py
"""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

import overlap_lab as L  # noqa: E402
import test_overlap_splice as TS  # noqa: E402


def row(tp, fp, fn, nodes=100, n_total=100.0, dtp=0, dfp=0, dfn=0):
    j = tp / (tp + fp + fn)
    ratio = (nodes - n_total) / n_total
    return {"edge_tp": tp, "edge_fp": fp, "edge_fn": fn, "division_tp": dtp, "division_fp": dfp, "division_fn": dfn,
            "num_pred_nodes": nodes, "node_recall": 0.9, "total_node_ratio": ratio, "edge_jaccard": j,
            "adj_edge_jaccard": max(0.0, j * (1 - 0.1 * ratio))}


# ------------------------------------------------------------------------------------------------------------------
def test_units_merge_groups_through_pairs_and_keep_singletons_fixed():
    stems = ["e_a", "e_b", "e_c", "e_d", "e_e", "e_f"]
    groups = [["e_a", "e_b", "x_missing"], ["e_c", "e_d"], ["e_z"]]
    units, fixed = L.units_of(stems, groups, [])
    assert units == [["e_a", "e_b"], ["e_c", "e_d"]] and fixed == ["e_e", "e_f"]
    units, fixed = L.units_of(stems, groups, [{"a": "e_b", "b": "e_c"}, {"a": "e_e", "b": "e_f"},
                                              {"a": "e_f", "b": "not_in_lab"}])
    assert units == [["e_a", "e_b", "e_c", "e_d"], ["e_e", "e_f"]] and fixed == []


def test_global_frames_chain_and_inconsistency():
    links = [{"a": "e_a", "b": "e_b", "offset_tzyx_a_minus_b": [1, 0, 2, 3]}]
    pairs = [{"a": "e_b", "b": "e_c", "offset": [0, 1, 0, -5]}]
    fr, bad = L.global_frames(["e_a", "e_b", "e_c", "e_d"], links, pairs)
    assert fr["e_a"] == ("e_a", (0, 0, 0, 0)) and fr["e_b"] == ("e_a", (1, 0, 2, 3))
    assert fr["e_c"] == ("e_a", (1, 1, 2, -2)) and fr["e_d"] == ("e_d", (0, 0, 0, 0)) and bad == 0
    # p_a = p_b + o: the same physical point has equal global coordinates in both clips
    p_b = np.array([4, 5, 6, 7])
    assert list(p_b + np.array([1, 0, 2, 3]) + 0) == list(p_b + np.array(fr["e_b"][1]))
    fr, bad = L.global_frames(["e_a", "e_b", "e_c"], links, pairs + [{"a": "e_a", "b": "e_c", "offset": [9, 9, 9, 9]}])
    assert bad == 1


def test_division_weights_count_each_event_once():
    shapes = {"e_a": (20, 20, 100, 100), "e_b": (20, 20, 100, 100), "e_c": (20, 20, 100, 100)}
    fr, _ = L.global_frames(list(shapes), [], [{"a": "e_a", "b": "e_b", "offset": [0, 0, 0, 40]}])
    ev = {
        # one GT division in the overlap (global x 60): A sees it at x 60 (TP), B at x 20 (FN)
        "e_a": {"gt_div": [[5, 10.0, 50.0, 60.0, 1], [5, 10.0, 50.0, 10.0, 0]], "fp_fork": [[7, 10.0, 20.0, 70.0],
                                                                                          [7, 10.0, 20.0, 5.0]]},
        "e_b": {"gt_div": [[5, 10.0, 50.0, 20.0, 0]], "fp_fork": []},
        "e_c": {"gt_div": [[5, 10.0, 50.0, 60.0, 1]], "fp_fork": [[1, 1.0, 1.0, 1.0]]},  # own frame: no sharing
    }
    w = L.division_weights(ev, fr, shapes)
    assert w["e_a"] == pytest.approx((0.5, 0.5 + 1.0, 1.0))
    assert w["e_b"] == pytest.approx((0.0, 0.0, 0.5))
    assert w["e_c"] == pytest.approx((1.0, 1.0, 0.0))
    tot = [sum(w[s][k] for s in w) for k in range(3)]
    assert tot == pytest.approx([1.5, 2.5, 1.5])  # 3 unique GT divisions: 1.5 TP + 1.5 FN


def test_pooled_equals_official_summarise_without_overlaps():
    rows = [row(90, 5, 5, 101, dtp=2, dfp=1, dfn=1), row(40, 10, 2, 95, dtp=0, dfp=0, dfn=3)]
    recs = [{"row": r, "div_w": (r["division_tp"], r["division_fp"], r["division_fn"])} for r in rows]
    p = L.pooled(recs)
    w = [100, 52]
    adj = (w[0] * rows[0]["adj_edge_jaccard"] + w[1] * rows[1]["adj_edge_jaccard"]) / sum(w)
    assert p["adj_edge_jaccard"] == pytest.approx(adj)
    assert p["division_jaccard"] == pytest.approx(2 / 7) and p["score"] == pytest.approx(adj + 0.1 * 2 / 7)
    assert p["edge_jaccard"] == pytest.approx(130 / 152) and p["nodes"] == 196
    ej = (w[0] * rows[0]["edge_jaccard"] + w[1] * rows[1]["edge_jaccard"]) / sum(w)
    assert p["score_nomult"] == pytest.approx(ej + 0.1 * 2 / 7)
    # deleting nodes raises the multiplier (both signs of the node ratio) but not score_nomult
    fewer = [{"row": row(90, 5, 5, 90, dtp=2, dfp=1, dfn=1), "div_w": (2, 1, 1)}, recs[1]]
    assert L.pooled(fewer)["score"] > p["score"] and L.pooled(fewer)["score_nomult"] == pytest.approx(p["score_nomult"])
    try:
        import trainlab as tl
        s = tl.summarise_rows(rows)
    except Exception:
        return
    assert s["score"] == pytest.approx(p["score"]) and s["adj_edge_jaccard"] == pytest.approx(p["adj_edge_jaccard"])
    # multiplicities = repeated rows
    assert L.pooled(recs, [2, 1])["score"] == pytest.approx(L.pooled([recs[0], recs[0], recs[1]])["score"])
    nodiv = [{"row": rows[0], "div_w": (0, 0, 0)}]
    assert L.pooled(nodiv)["score"] == pytest.approx(rows[0]["adj_edge_jaccard"])


def test_bootstrap_delta():
    old = {s: {"row": row(80, 10, 10), "div_w": (0, 0, 0)} for s in ("a", "b", "c", "d", "f")}
    new = dict(old)
    new["a"] = {"row": row(84, 8, 8), "div_w": (0, 0, 0)}
    new["c"] = {"row": row(82, 9, 9), "div_w": (0, 0, 0)}
    b = L.bootstrap_delta([["a", "b"], ["c", "d"]], ["f"], new, old, b=500)
    assert b["point"] > 0 and b["lower"] > 0 and b["units"] == 2
    assert b == L.bootstrap_delta([["a", "b"], ["c", "d"]], ["f"], new, old, b=500)  # seeded
    new["c"] = {"row": row(76, 12, 12), "div_w": (0, 0, 0)}  # one unit loses
    b = L.bootstrap_delta([["a", "b"], ["c", "d"]], ["f"], new, old, b=500)
    assert b["lower"] < 0 < b["upper"]
    b0 = L.bootstrap_delta([], ["a", "f"], new, old)
    assert b0["units"] == 0 and b0["lower"] == b0["point"]


def test_gate_gb():
    ok = dict(d44=0.003, boot={"lower": 0.0004, "units": 5}, node_frac_clip={"x": 0.004, "y": -0.001},
              node_frac_44=0.001, forks_changed=[], sixbba_changed_edges=0, sixbba_pairs=0, sixbba_clips=0)
    assert L.gate_gb("arm", "base", **ok)["pass"]
    for k, v in (("d44", 0.0019), ("boot", {"lower": 0.0, "units": 5}), ("boot", {"lower": 0.1, "units": 0}),
                 ("node_frac_clip", {"x": 0.0051}), ("node_frac_44", 0.006), ("forks_changed", ["x"]),
                 ("sixbba_changed_edges", 1), ("sixbba_pairs", 1), ("d44", float("nan")), ("boot", None)):
        g = L.gate_gb("arm", "base", **{**ok, k: v})
        assert not g["pass"], (k, v)


def test_graph_checks_and_csv_sanity():
    nodes = {1: {"t": 0, "z": 1.0, "y": 1.0, "x": 1.0}, 2: {"t": 1, "z": 1.0, "y": 1.0, "x": 1.0},
             3: {"t": 1, "z": 1.0, "y": 5.0, "x": 1.0}, 4: {"t": 3, "z": 1.0, "y": 5.0, "x": 1.0}}
    good = (nodes, [{"source_id": 1, "target_id": 2}])
    bad = (nodes, [{"source_id": 1, "target_id": 2}, {"source_id": 3, "target_id": 2}, {"source_id": 3,
                                                                                         "target_id": 9},
                   {"source_id": 3, "target_id": 4}])
    c = L.graph_checks(bad, (4, 4, 4, 4))
    assert c["indeg_gt1"] == 1 and c["dangling"] == 1 and c["dt_not_1"] == 2 and c["outside_crop"] == 2  # 3->2, 3->4
    assert L.graph_checks(good)["indeg_gt1"] == 0
    shapes = {"44b6_x": (4, 4, 8, 8), "6bba_y": (4, 4, 8, 8)}
    res = L.csv_sanity({"44b6_x": good, "6bba_y": good}, {"44b6_x": bad, "6bba_y": good}, shapes)
    assert res["totals"]["changed_datasets"] == 1 and res["6bba_changed"] == []
    assert set(res["invalid_introduced"]["44b6_x"]) == {"indeg_gt1", "dangling", "outdeg_gt2"}
    res = L.csv_sanity({"6bba_y": good}, {"6bba_y": bad}, shapes)
    assert res["6bba_changed"] == ["6bba_y"]


def test_kernel_csv_parity(tmp_path):
    g = ({5: {"t": 0, "z": 1.4, "y": 2.6, "x": -0.2}, 6: {"t": 1, "z": 1.0, "y": 3.0, "x": 0.0}},
         [{"source_id": 5, "target_id": 6}])
    p = tmp_path / "submission.csv"
    p.write_text("id,dataset,row_type,node_id,t,z,y,x,source_id,target_id\n"
                 "0,d1,node,5,0,1,3,0,-1,-1\n1,d1,node,6,1,1,3,0,-1,-1\n2,d1,edge,-1,-1,-1,-1,-1,5,6\n"
                 "3,d2,node,1,0,0,0,0,-1,-1\n", encoding="utf-8")
    rows = L.read_kernel_csv(p, {"d1"})
    assert set(rows) == {"d1"} and L.kernel_csv_parity(g, rows["d1"])
    g2 = (g[0], [])
    assert not L.kernel_csv_parity(g2, rows["d1"])


def _scene():
    """A misses a link near its x border (B owns and repairs it); B is fine. Crops are 44b6-named clips."""
    a = TS.background(TS.G()).track("t", range(3, 17), 10, 50, 95, skip_edges={10}, moved={10: 10.0}).g()
    b = TS.background(TS.G(TS.OFF_B)).track("t", range(3, 17), 10, 50, 95).g()
    six = TS.background(TS.G()).g()
    graphs = {"44b6_a": a, "44b6_b": b, "6bba_c": six}
    shapes = {k: TS.SHAPE for k in graphs}
    pairs = [{"a": "44b6_a", "b": "44b6_b", "offset": list(TS.OFF_B)}]
    return graphs, shapes, pairs


def test_splice_arms_float_and_csv_paths():
    graphs, shapes, pairs = _scene()
    out, st, _ = L.splice_arm(graphs, shapes, pairs, {"node_cap_frac": 1.0})
    assert st["total"]["spliced"] == 1 and out["44b6_b"] is graphs["44b6_b"] and out["6bba_c"] is graphs["6bba_c"]
    assert TS.chain_ok(*out["44b6_a"], range(3, 17), (50, 95))
    out_c, st_c, _ = L.splice_arm(graphs, shapes, pairs, {"node_cap_frac": 1.0}, via_csv=True)
    assert st_c["total"]["spliced"] == 1
    assert out_c["44b6_b"] is graphs["44b6_b"] and out_c["6bba_c"] is graphs["6bba_c"]  # untouched: original objects
    assert L.writer_digest(out_c["44b6_a"]) == L.writer_digest(out["44b6_a"])  # integer scene: paths agree
    # no pair -> every arm is the identity
    out0, st0, _ = L.splice_arm(graphs, shapes, [], {})
    assert all(out0[k] is graphs[k] for k in graphs) and st0["total"]["videos_changed"] == 0
    # CSV sanity of the spliced arm: valid rows, 6bba untouched, forks untouched
    cs = L.csv_sanity(graphs, out, shapes)
    assert cs["invalid_introduced"] == {} and cs["6bba_changed"] == [] and cs["totals"]["changed_datasets"] == 1
    assert L.forks_of(out["44b6_a"][1]) == L.forks_of(graphs["44b6_a"][1]) == {}


def test_splice_arm_leaves_forks_and_default_cap_blocks_growth():
    graphs, shapes, pairs = _scene()
    gb = TS.background(TS.G(TS.OFF_B)).track("t", range(3, 17), 10, 50, 95)
    gb.track("d", range(11, 17), 10, 64, 95)
    gb.edge(("t", 10), ("d", 11))
    graphs["44b6_b"] = gb.g()
    out, st, _ = L.splice_arm(graphs, shapes, pairs, {"node_cap_frac": 1.0})
    assert st["total"]["skipped_fork"] >= 1 and L.forks_of(out["44b6_b"][1]) == L.forks_of(graphs["44b6_b"][1])
    # node-importing splice on a tiny video: the default 0.5% cap blocks it
    a = TS.background(TS.G()).track("t", [t for t in range(3, 17) if t not in (9, 10, 11)], 10, 50, 95,
                                    skip_edges={12}).g()
    graphs, shapes, pairs = _scene()
    graphs["44b6_a"] = a
    out, st, _ = L.splice_arm(graphs, shapes, pairs, {})
    assert out["44b6_a"] is a and st["total"]["skipped_cap"] == 1


def test_load_tail(tmp_path):
    p = tmp_path / "44b6_x.npz"
    np.savez(p, node_id=np.array([4, 9]), t=np.array([0, 1]), zyx=np.array([[1.0, 2.0, 3.0], [1.5, 2.5, 3.5]]),
             src=np.array([4]), dst=np.array([9]), edge_prob=np.array([0.9]))
    r = L.load_tail(p)
    assert r["control"] is r["ins35"] and not r["divins"]
    assert r["control"][0] == {4: {"t": 0, "z": 1.0, "y": 2.0, "x": 3.0}, 9: {"t": 1, "z": 1.5, "y": 2.5, "x": 3.5}}
    assert r["control"][1] == [{"source_id": 4, "target_id": 9}]


def test_slim_keeps_order_and_positions():
    nodes = {7: {"t": 1, "z": 1.5, "y": 2.0, "x": 3.0, "score": 0.3, "node_id": 7}, 3: {"t": 0, "z": 0, "y": 0, "x": 0}}
    edges = [{"source_id": 3, "target_id": 7, "edge_prob": 0.5}]
    n, e = L.slim(nodes, edges)
    assert list(n) == [7, 3] and n[7] == {"t": 1, "z": 1.5, "y": 2.0, "x": 3.0} and e == [{"source_id": 3,
                                                                                           "target_id": 7}]


EXP60 = ROOT.parent.parent.parent / "_dl" / "exp60_a"
if not EXP60.is_dir():
    EXP60 = ROOT / "_dl" / "exp60_a"
TRAIN = ROOT.parent.parent.parent / "biohub-cell-tracking-during-development" / "train"
if not TRAIN.is_dir():
    TRAIN = ROOT / "biohub-cell-tracking-during-development" / "train"
STEM = "44b6_2f31fc2f"


@pytest.mark.skipif(not (EXP60 / "trainlab" / f"{STEM}.npz").is_file() or not (TRAIN / f"{STEM}.geff").exists(),
                    reason="local exp60 dump / train GT not available")
def test_eval_clip_matches_trainlab_official_eval():
    import trainlab as tl
    clip = L.load_clip(EXP60 / "trainlab" / f"{STEM}.npz", EXP60 / "divins_dump" / f"{STEM}.npz")
    nodes, edges = clip["ins35"]
    r = L.eval_clip(nodes, edges, TRAIN / f"{STEM}.geff")
    ref, tpf, fpf = tl.official_eval(nodes, edges, TRAIN / f"{STEM}.geff")
    for k, v in ref.items():
        assert (v != v and r["row"][k] != r["row"][k]) or r["row"][k] == v, k
    assert len(r["fp_fork"]) == len(fpf) == r["row"]["division_fp"] and r["tp_fork_n"] == len(tpf)
    assert len(r["gt_div"]) == r["row"]["division_tp"] + r["row"]["division_fn"]
    assert sum(d[4] for d in r["gt_div"]) == r["row"]["division_tp"]
    assert all(len(d) == 5 and not math.isnan(d[1]) for d in r["gt_div"])
