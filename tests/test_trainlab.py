"""exp60 x138 train lab (research/wf_ideas_v3/TASK_CLOUD_SESSION.md T5): builder patch `trainlab`, the kernel-side
snapshot module tools/trainlab_io.py and the CPU replay / scoring tool tools/trainlab.py.

    python -m pytest tests/test_trainlab.py
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import tools.build_probe_kernel as bpk  # noqa: E402
import trainlab as tl  # noqa: E402
import trainlab_io as tio  # noqa: E402

BUILDER = str(ROOT / "tools" / "build_probe_kernel.py")
NL = "\n"
STEM = "6bba_07477033"
LAB_ARGS = ["--base", "x138", "--patch", "divinsert", "--patch", "safetail", "--patch", "trainlab", "--lab",
            "--set", "REPAIR_DEADLINE_S=40000", "--set", "DIVINS_DEADLINE_S=40000", "--set", "DIVINS_ENABLE=1",
            "--set", "DIVINS_STEAL=1", "--set", "DIVINS_CAP=4", "--set", "DIVINS_FRAME_CAP=1", "--set", "DIVINS_ALPHA=1",
            "--set", "DIVINS_THRESH=1.5", "--set", "DIVINS_DUMP=1", "--set", "VALIDATOR_ENABLE=0"]


def _build(name: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, BUILDER, name, *args], capture_output=True, text=True, cwd=ROOT)


@pytest.fixture(scope="module")
def lab_nb():
    out = ROOT / "experiments" / "zz_trainlab_test"
    try:
        r = _build("zz-trainlab-test", *LAB_ARGS, "--train-stems", STEM, "--out-dir", "zz_trainlab_test/kernel_a")
        assert r.returncode == 0, r.stderr[-800:]
        r = _build("zz-trainlab-test-b", *LAB_ARGS, "--train-stems", STEM, "--owner", "sasyami",
                   "--out-dir", "zz_trainlab_test/kernel_b_sasyami")
        assert r.returncode == 0, r.stderr[-800:]
        yield out
    finally:
        shutil.rmtree(out, ignore_errors=True)


def _code(nb_path: Path) -> list[str]:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def test_x138_without_patches_is_exp56():
    name = "zz-trainlab-x138-plain"
    try:
        r = _build(name, "--base", "x138")
        assert r.returncode == 0, r.stderr[-500:]
        built = (ROOT / "experiments" / name / (name + ".ipynb")).read_bytes()
        assert built == bpk.BASES["x138"]["nb"].read_bytes()
    finally:
        shutil.rmtree(ROOT / "experiments" / name, ignore_errors=True)


def test_lab_build_one_stem(lab_nb):
    kdir = lab_nb / "kernel_a"
    nb = next(kdir.glob("*.ipynb"))
    code = _code(nb)
    for i, s in enumerate(code):
        compile(s, f"cell{i}", "exec")
    env = tl.cell_env(code[0])
    assert env["BIOHUB_TRAINLAB_DUMP"] == "1" and env["BIOHUB_REPAIR_DEADLINE_S"] == "40000"
    assert env["BIOHUB_DIVINS_THRESH"] == "1.5" and env["BIOHUB_DIVINS_DUMP"] == "1"
    assert env["BIOHUB_VALIDATOR_ENABLE"] == "0" and env["BIOHUB_DEEPCENTER_SAFE_DIV_THRESHOLD"] == "0.25"
    pred = [s for s in code if "test_stems = list_test_stems()" in s]
    assert len(pred) == 1 and f"    {STEM!r}," in pred[0]
    assert pred[0].index("TEST_DIR = Path(tempfile.gettempdir())") < pred[0].index("test_stems = list_test_stems()")
    assert pred[0].index("test_stems = list_test_stems()") < pred[0].index("predict_cmd = [")
    post = [s for s in code if "def filter_output_graph(" in s]
    assert len(post) == 1
    for stage in ("presafe", "preshort", "final"):
        assert post[0].count(bpk.trainlab_hook_line(stage)) == 1
    assert post[0].count(bpk.TRAINLAB_DC_WRAP) == 1
    # removing the trainlab insertions gives exactly the divinsert + safetail post cell
    undone = post[0].replace(bpk.TRAINLAB_DC_WRAP, "")
    for stage in ("presafe", "preshort", "final"):
        undone = undone.replace(bpk.trainlab_hook_line(stage), "")
    bpk.CELL.clear()
    bpk.CELL.update(bpk.BASES["x138"])
    try:
        x = json.loads(bpk.BASES["x138"]["nb"].read_text(encoding="utf-8"))
        cells = {k: "".join(c["source"]) for k, c in enumerate(c for c in x["cells"] if c["cell_type"] == "code")}
        for p in ("divinsert", "safetail"):
            bpk.PATCHES[p](cells)
    finally:
        bpk.CELL.clear()
        bpk.CELL.update(bpk.BASES["exp39"])
    assert undone == cells[5]
    assert sum("tools/trainlab_io.py" in s for s in code) >= 1 and sum("trainlab summary" in s for s in code) == 1
    meta = json.loads((kdir / "kernel-metadata.json").read_text())
    assert meta["id"] == "vitaliineibauer/biohub-zz-trainlab-test"
    assert meta["dataset_sources"] == ["pilkwang/biohub-deepcenter-unet3d-center-prior-v1",
                                       "pilkwang/biohub-temporal-unet3d-seed314159-v1",
                                       "pilkwang/biohub-tracking-support-pack-50ep-v1",
                                       "anvithpothula/biohub-v1284-head-s075", "vitaliineibauer/biohub-ft-weights"]
    assert meta["competition_sources"] == ["biohub-cell-tracking-during-development"]
    probe = json.loads((kdir / "probe.json").read_text(encoding="utf-8"))
    assert "never submit" in probe["lab"] and probe["train_stems"] == [STEM]
    meta_b = json.loads((lab_nb / "kernel_b_sasyami" / "kernel-metadata.json").read_text())
    assert meta_b["id"] == "sasyami/biohub-zz-trainlab-test-b" and meta_b["dataset_sources"] == meta["dataset_sources"]


def test_builder_refusals():
    base = ["--base", "x138", "--patch", "divinsert", "--patch", "safetail", "--set", "REPAIR_DEADLINE_S=40000",
            "--set", "DIVINS_ENABLE=1"]
    cases = [
        (["--base", "x138", "--patch", "trainlab", "--train-stems", STEM], "needs --lab"),
        (["--base", "x138", "--patch", "trainlab", "--lab"], "--train-stems"),
        (["--base", "x138", "--patch", "trainlab", "--lab", "--train-stems", "6bba_nothere"], "unknown"),
        (["--patch", "divinsert", "--set", "DIVINS_DUMP=1"], "--lab builds only"),
        (["--base", "x138", "--patch", "divinsert", "--set", "DIVINS_DUMP=1"], "--lab builds only"),
        ([*base, "--patch", "trainlab", "--lab", "--train-stems", STEM, "--set", "DIVINS_THRESH=0.4",
          "--set", "DIVINS_DUMP=1"], "dump-only"),
        ([*base, "--patch", "trainlab", "--lab", "--train-stems", STEM, "--set", "DIVINS_THRESH=1.5"], "dump-only"),
        (["--base", "x138", "--patch", "trainlab", "--lab", "--train-stems", STEM, "--set", "VALIDATOR_ENABLE=1"],
         "VALIDATOR_ENABLE=0"),
        (["--base", "x138", "--train-stems", STEM], "needs --patch trainlab"),
        (["--base", "x138", "--set", "TRAINLAB_DUMP=1"], "needs --patch trainlab"),
        (["--patch", "trainlab", "--lab", "--train-stems", STEM], "needs --base x138"),
    ]
    for args, msg in cases:
        r = _build("zz-trainlab-refusal", *args)
        assert r.returncode != 0 and msg in r.stderr, (args, r.stderr[-300:])
    assert not (ROOT / "experiments" / "zz-trainlab-refusal").exists()


def test_stems_from_split():
    stems = bpk.trainlab_parse_stems("@experiments/exp60_trainlab/split.json:A")
    split = json.loads((ROOT / "experiments/exp60_trainlab/split.json").read_text(encoding="utf-8"))
    assert stems == split["shards"]["A"] and len(stems) == 28


def test_split_properties():
    split = json.loads((ROOT / "experiments/exp60_trainlab/split.json").read_text(encoding="utf-8"))
    assert tl.make_split(split["total"], split["seed"]) == split  # reproducible from the committed inputs
    stems = split["stems"]
    assert 50 <= len(stems) <= 60 and len(set(stems)) == len(stems)
    excluded = set(split["excluded"]["x138_probable_train"]) | set(tl.DUMMY_TWINS)
    assert len(split["excluded"]["x138_probable_train"]) == 20 and not excluded & set(stems)
    assert tl.check_leak(stems) == []
    sp = json.loads(tl.SPLITS.read_text(encoding="utf-8"))
    grouped = {s for g in sp["meta"]["leak_groups"] for s in g}
    groups = [set(g) for g in sp["meta"]["leak_groups"]] + [{s} for s in sp["folds"] if s[:4] == "44b6" and s not in grouped]
    avail = [g for g in groups if g - excluded]
    assert sum(s.startswith("44b6") for s in stems) == len(avail)  # one clip per leak group with an eligible clip
    for emb in tl.EMBRYOS:
        n = [sum(s.startswith(emb) for s in split["halves"][h]) for h in ("SELECTION", "CONFIRMATION")]
        assert abs(n[0] - n[1]) <= 1 and min(n) > 0
        assert all(sum(s.startswith(emb) for s in split["shards"][k]) > 0 for k in ("A", "B"))
    assert sorted(split["halves"]["SELECTION"] + split["halves"]["CONFIRMATION"]) == stems
    assert sorted(split["shards"]["A"] + split["shards"]["B"]) == stems


# ---------------------------------------------------------------------------------------------------------------------
# tools/trainlab_io.py
# ---------------------------------------------------------------------------------------------------------------------
def test_io_roundtrip_exact():
    nodes = {7: {"node_id": 7, "t": 0, "z": 1.5, "y": 2.0, "x": 3.25}, 3: {"node_id": 3, "t": 1, "z": 1.0, "y": 2.5,
                                                                         "x": 3.0, "readmitted": 1}}
    edges = [{"source_id": 7, "target_id": 3, "edge_prob": None, "distance_um": 1.0, "safe_division": 1},
             {"source_id": 7, "target_id": 3, "edge_prob": 0.0, "flag": True, "weird": "x"}]
    arr = tio.trainlab_graph_arrays("s_", nodes, edges)
    nodes[7]["z"] = 99.0  # later in-place edits must not leak into the snapshot
    n2, e2 = tio.trainlab_graph_from_arrays(arr, "s_")
    assert list(n2) == [7, 3] and n2[7]["z"] == 1.5 and n2[3] == {"node_id": 3, "t": 1, "z": 1.0, "y": 2.5, "x": 3.0,
                                                                   "readmitted": 1}
    assert isinstance(n2[3]["t"], int) and isinstance(n2[3]["z"], float)
    assert e2[0] == edges[0] and e2[1] == {"source_id": 7, "target_id": 3, "edge_prob": 0.0, "flag": True}


def _io_ns(dump: str, tmp: Path) -> dict:
    ns = {"__name__": "k"}
    old = {k: os.environ.get(k) for k in ("BIOHUB_TRAINLAB_DUMP", "BIOHUB_TRAINLAB_DIR")}
    os.environ["BIOHUB_TRAINLAB_DUMP"], os.environ["BIOHUB_TRAINLAB_DIR"] = dump, str(tmp)
    try:
        exec(compile(bpk.trainlab_cell(), "trainlab_cell", "exec"), ns)
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return ns


def test_hooks_are_noop_when_disabled(tmp_path, capsys):
    ns = _io_ns("0", tmp_path)
    nodes, edges = {1: {"t": 0, "z": 0.0, "y": 0.0, "x": 0.0}}, []
    for stage in tio.TRAINLAB_STAGES:
        assert ns["trainlab_hook"](stage, "d", nodes, edges, {}, None, 0.0) is None
    assert not list(tmp_path.iterdir()) and ns["TRAINLAB_STATE"]["pending"] == {}

    def orig(*a):
        return 0.5
    ns["deepcenter_score_point"] = orig
    exec(bpk.TRAINLAB_DC_WRAP, ns)
    assert ns["deepcenter_score_point"] is orig  # no wrapper without the dump
    assert "TRAINLAB FAILED" not in capsys.readouterr().out


def test_hook_fail_soft(tmp_path, capsys):
    ns = _io_ns("1", tmp_path)
    ns["trainlab_hook"]("final", "d", {}, [], {}, None, 0.0)  # no presafe snapshot
    assert ns["TRAINLAB_STATE"]["failed"] == 1 and "TRAINLAB FAILED at final" in capsys.readouterr().out


# ---------------------------------------------------------------------------------------------------------------------
# end to end on a synthetic graph: the lab notebook's own tail with the real hooks (= the kernel), then the CPU replay
# ---------------------------------------------------------------------------------------------------------------------
DIV_T0 = (3, 7, 11, 15, 19, 23, 27, 31)


def _synthetic_presafe(seed: int = 0) -> tuple[dict, list]:
    """40 frames, 60 straight noisy tracks (edges p 0.9, some 0.0), plus 8 division-like configurations: a parent P at
    t0 with its continuing child c1 and an ORPHAN track q starting at t0+1 on the other side (safe-division candidates,
    DIV_T0 = the t0 values; one per frame, so only the DeepCenter threshold and the global cap decide)."""
    rng = np.random.default_rng(seed)
    nodes, edges, nid = {}, [], 1
    T = 40
    for k in range(60):
        z, y, x = 10.0 + (k % 5) * 6, 40.0 + (k // 5) * 60, 40.0 + (k % 7) * 50
        prev = None
        for t in range(T):
            nodes[nid] = {"node_id": nid, "t": t, "z": z, "y": y + t * 0.5 + rng.normal(0, 3.0), "x": x}
            if prev is not None:
                edges.append({"source_id": prev, "target_id": nid, "edge_prob": 0.0 if (k + t) % 11 == 0 else 0.9})
            prev, nid = nid, nid + 1
    for j, t0 in enumerate(DIV_T0):
        z, y, x = 20.0, 500.0 + j * 60, 500.0
        chain = []
        for t in range(max(0, t0 - 5), t0 + 1):  # parent track up to t0
            nodes[nid] = {"node_id": nid, "t": t, "z": z, "y": y, "x": x}
            chain.append(nid)
            nid += 1
        for side, rest in ((1, "c1"), (-1, "q")):
            prev = chain[-1] if rest == "c1" else None
            for dt in range(1, 11):
                nodes[nid] = {"node_id": nid, "t": t0 + dt, "z": z, "y": y + side * (8 + 12 * (dt - 1)), "x": x}
                if prev is not None:
                    edges.append({"source_id": prev, "target_id": nid, "edge_prob": 0.95})
                prev, nid = nid, nid + 1
        for a, b in zip(chain, chain[1:]):
            edges.append({"source_id": a, "target_id": b, "edge_prob": 0.9})
    for e in edges:
        e["distance_um"] = float(np.linalg.norm(tl._pos_um(nodes[e["target_id"]]) - tl._pos_um(nodes[e["source_id"]])))
    return nodes, edges


def _kernel_function(post: str) -> str:
    lines = post.splitlines(keepends=True)
    first = lines.index(bpk.trainlab_hook_line("presafe"))
    last = lines.index(bpk.trainlab_hook_line("final"))
    return ("def _kernel_tail(nodes_by_id, edges, stats, dataset, deepcenter_bundle, repair_frame_cache,"
            " deepcenter_heatmap_cache, _stage_t0):\n" + "".join(lines[first:last + 1]) + "    return nodes_by_id, edges\n")


def _stats0() -> dict:
    keys = ["safe_division_candidates", "safe_division_geometric_candidates", "safe_divisions_added",
            "safe_division_skipped_cap", "safe_division_mutual_nn_rejected", "safe_division_divergence_rejected",
            "safe_division_symmetry_rejected", "deepcenter_safe_div_checked", "deepcenter_safe_div_accepted",
            "deepcenter_safe_div_rejected", "deepcenter_safe_div_missing", "short_track_components_removed",
            "short_track_nodes_removed", "short_track_edges_removed", "short_track_filter_skipped_all",
            "short_track_rescue_triggered", "short_track_rescue_components", "short_track_rescue_nodes",
            "short_track_rescue_budget", "linefit_smoothed_nodes", "linefit_skipped_nodes", "dropped_division_edges",
            "pruned_isolated_nodes"]
    return {k: 0 for k in keys}


def test_end_to_end_replay_parity(lab_nb, tmp_path):
    nb = next((lab_nb / "kernel_a").glob("*.ipynb"))
    post = [s for s in _code(nb) if "def filter_output_graph(" in s][0]
    # "kernel": a namespace of the lab notebook with the REAL trainlab hooks and a DeepCenter stand-in
    kns = tl.tail_namespace(nb)
    io_ns = _io_ns("1", tmp_path)
    kns.update({k: io_ns[k] for k in ("trainlab_hook", "trainlab_record_dc", "TRAINLAB_STATE", "TRAINLAB_DUMP")})

    scores = dict(zip((t0 + 1 for t0 in DIV_T0), (0.12, 0.17, 0.22, 0.27, 0.32, 0.40, 0.50, 0.60)))

    def fake_dc(dataset, t, point, bundle, fc, hc):
        return scores.get(int(t), 0.9)
    kns["deepcenter_score_point"] = fake_dc
    exec(bpk.TRAINLAB_DC_WRAP, kns)
    assert kns["deepcenter_score_point"] is not fake_dc
    exec(compile(_kernel_function(post), "kernel_tail", "exec"), kns)
    nodes, edges = _synthetic_presafe()
    with contextlib.redirect_stdout(io.StringIO()) as out:
        fn, fe = kns["_kernel_tail"](nodes, edges, _stats0(), "synth_a", object(), {}, {}, time.time())
    assert "TRAINLAB_TIMING" in out.getvalue() and "TRAINLAB FAILED" not in out.getvalue()
    dump_path = tmp_path / "synth_a.npz"
    d = tio.trainlab_load(dump_path)
    assert d["meta"]["n_dc"] > 0 and len(d["dc"]) > 0
    assert tl.writer_digest(*d["final"]) == tl.writer_digest(fn, fe)
    assert d["meta"]["final_stats"]["safe_divisions_added"] > 0

    # laptop: replay from the dump through the notebook's own tail (no scoring)
    res = tl.lab_dataset({"stem": "synth_a", "dump": str(dump_path), "nb": str(nb), "gt": None, "divins": None})
    for start in ("presafe", "preshort"):
        p = res["parity"][start]
        assert p["writer_equal"] and p["float_equal"] and p["node_ids_equal"] and p["edge_pairs_equal"], (start, p)
    assert res["parity"]["presafe"]["dc_miss"] == 0
    arms = res["arms"]
    assert set(arms) >= {"control", "forkmid45", "linefit_w07_win2", "dc0.15", "dc0.20", "dc0.30", "dc0.35"}
    added = {a: arms[a]["safe_divisions_added"] for a in ("dc0.15", "dc0.20", "dc0.30", "dc0.35")}
    ctrl = d["meta"]["final_stats"]["safe_divisions_added"]
    assert (added["dc0.15"], added["dc0.20"], ctrl, added["dc0.30"], added["dc0.35"]) == (7, 6, 5, 4, 3)
    assert arms["forkmid45"]["nodes"] == arms["control"]["nodes"]
    assert all(isinstance(r["readmitted_touch"], bool) for r in res["forkmid_audit"])  # ADDENDUM L3 sensitivity flag
    assert arms["linefit_w07_win2"]["digest"] != arms["control"]["digest"]  # weight 0.7 moves nodes
    assert arms["linefit_w07_win2"]["edges"] == arms["control"]["edges"]


# ---------------------------------------------------------------------------------------------------------------------
# forkmid, insertion variant
# ---------------------------------------------------------------------------------------------------------------------
def _fork(mid_vox_y: float, ilp_prob, inserted: bool = False):
    # parent at y=0; children at t+1: ilp child y = a, added child y = b; midpoint offset = (a + b)/2 voxels in y
    nodes = {1: {"t": 0, "z": 0.0, "y": 100.0, "x": 0.0}, 2: {"t": 1, "z": 0.0, "y": 100.0 + mid_vox_y + 6, "x": 0.0},
             3: {"t": 1, "z": 0.0, "y": 100.0 + mid_vox_y - 6, "x": 0.0}}
    e_ilp = {"source_id": 1, "target_id": 2, "edge_prob": ilp_prob}
    e_add = {"source_id": 1, "target_id": 3, "edge_prob": None, "safe_division": 1}
    if inserted:
        e_add = {"source_id": 1, "target_id": 3, "edge_prob": None, "div_inserted": 1}
    return nodes, [e_ilp, e_add]


def test_forkmid_rules():
    far = 4.5 / 0.40625 + 0.5  # midpoint offset just above 4.5 um
    nodes, edges = _fork(far, 0.0)
    snap = json.dumps(nodes, sort_keys=True)
    out, audit = tl.forkmid(nodes, edges)
    assert out == [edges[1]] and audit[0]["removed"] == "ilp" and audit[0]["mid_um"] >= 4.5
    nodes, edges = _fork(far, 0.9)
    out, audit = tl.forkmid(nodes, edges)
    assert out == [edges[0]] and audit[0]["removed"] == "added"
    nodes, edges = _fork(far, None)  # gap edge (None) is not 0.0 -> the added edge goes
    assert tl.forkmid(nodes, edges)[0] == [edges[0]]
    nodes, edges = _fork(4.5 / 0.40625 - 0.5, 0.0)
    out, audit = tl.forkmid(nodes, edges)
    assert out == edges and audit[0]["removed"] is None
    nodes, edges = _fork(far, 0.0, inserted=True)  # inserted forks are never touched
    out, audit = tl.forkmid(nodes, edges)
    assert out == edges and audit == []
    assert json.dumps(_fork(far, 0.0)[0], sort_keys=True) == snap  # nodes untouched


def test_insert_nosteal0():
    # u(t0) -> c1(t1); w(t0) -> v(t1) with edge_prob 0.0: #35 steals v for u, nosteal0 must not
    nodes = {1: {"t": 0, "z": 10.0, "y": 100.0, "x": 100.0}, 2: {"t": 1, "z": 10.0, "y": 110.0, "x": 100.0},
             3: {"t": 1, "z": 10.0, "y": 90.0, "x": 100.0}, 4: {"t": 0, "z": 10.0, "y": 60.0, "x": 100.0}}
    edges = [{"source_id": 1, "target_id": 2, "edge_prob": 0.9}, {"source_id": 4, "target_id": 3, "edge_prob": 0.0}]
    node_p = {1: (0.0, 0.95, 0.0), 2: (0.0, 0.0, 0.95), 3: (0.0, 0.0, 0.95)}
    e35, st = tl.insert35(nodes, edges, node_p)
    assert st["divins_added_steal"] == 1 and edges[1] not in e35
    e0, st0 = tl.insert35(nodes, edges, node_p, nosteal0=True)
    assert st0["divins_added"] == 0 and e0 is edges
    edges[1]["edge_prob"] = 0.1  # a scored weak edge is still stealable in both
    e1, st1 = tl.insert35(nodes, edges, node_p, nosteal0=True)
    assert st1["divins_added_steal"] == 1 and all(e is edges[0] or e.get("div_inserted") for e in e1)


# ---------------------------------------------------------------------------------------------------------------------
# mock scoring on synthetic graphs (official metric internals, aggregation, gates)
# ---------------------------------------------------------------------------------------------------------------------
def _td_graph(nodes: dict, edges: list):
    import polars as pl
    import tracksdata as td
    g = td.graph.IndexedRXGraph()
    for key in ("z", "y", "x"):
        g.add_node_attr_key(key, pl.Float64, 0.0)
    ids = sorted(nodes)
    g.bulk_add_nodes([{k: nodes[i][k] for k in ("t", "z", "y", "x")} for i in ids], indices=ids)
    g.bulk_add_edges([{"source_id": s, "target_id": t} for s, t in edges])
    return g


def test_official_eval_matches_evaluate(monkeypatch):
    pytest.importorskip("tracksdata")
    import score_geffs as sg
    from tracking_cellmot.metrics import evaluate, per_sample_metrics, node_recall
    gt_nodes, gt_edges, nid = {}, [], 1
    for k in range(6):  # 6 GT tracks, one divides at t=5
        prev = None
        for t in range(12):
            gt_nodes[nid] = {"t": t, "z": 10.0, "y": 50.0 + 40 * k, "x": 50.0 + (3 * t if k == 0 and t > 5 else 0)}
            if prev is not None:
                gt_edges.append((prev, nid))
            prev, nid = nid, nid + 1
    div_parent = 6  # track 0, t=5
    for t in range(6, 12):
        gt_nodes[nid] = {"t": t, "z": 10.0, "y": 50.0, "x": 50.0 - 3 * (t - 5)}
        gt_edges.append((div_parent if t == 6 else nid - 1, nid))
        nid += 1
    scale = (1.625, 0.40625, 0.40625)
    monkeypatch.setattr(sg, "_load_gt_and_scale", lambda p: (_td_graph(gt_nodes, gt_edges), scale))
    monkeypatch.setattr(sg, "_estimated_n_total", lambda p: 100.0)
    # prediction: GT shifted ids, one track broken, a false fork, the division found
    pred = {i + 1000: dict(n, y=n["y"] + 2.0) for i, n in gt_nodes.items()}
    pedges = [{"source_id": s + 1000, "target_id": t + 1000} for s, t in gt_edges if (s, t) != (20, 21)]
    pedges.append({"source_id": 1000 + 30, "target_id": 1000 + 43})
    row, tpf, fpf = tl.official_eval(pred, pedges, Path("unused.geff"))
    g = _td_graph({k: {kk: float(max(0, int(round(float(v[kk]))))) if kk != "t" else v["t"] for kk in v}
                   for k, v in pred.items()}, [(e["source_id"], e["target_id"]) for e in pedges])
    er = evaluate(g, _td_graph(gt_nodes, gt_edges), scale=scale)
    ref = per_sample_metrics(er, 100.0, node_recall(g, _td_graph(gt_nodes, gt_edges)))
    for k in ("edge_tp", "edge_fp", "edge_fn", "division_tp", "division_fp", "division_fn", "num_pred_nodes"):
        assert row[k] == ref[k], k
    assert abs(row["adj_edge_jaccard"] - ref["adj_edge_jaccard"]) < 1e-12
    assert tpf == [1000 + div_parent] and row["division_tp"] == 1


def _fake_result(stem: str, deltas: dict, audit: list) -> dict:
    def row(tp, fp, fn, dtp, dfp, dfn, n=100):
        return {"edge_tp": tp, "edge_fp": fp, "edge_fn": fn, "division_tp": dtp, "division_fp": dfp,
                "division_fn": dfn, "num_pred_nodes": n, "node_recall": 1.0, "total_node_ratio": 0.0,
                "edge_jaccard": tp / (tp + fp + fn), "adj_edge_jaccard": tp / (tp + fp + fn)}
    arms = {}
    for arm in tl.ARMS:
        tp = 90 + deltas.get(arm, 0)
        arms[arm] = {"row": row(tp, 5, 100 - tp, 2, 3, 1), "nodes": 100, "forks": 5, "tp_forks": [1, 2],
                     "fp_forks": [3, 4, 5], "new_forks": [], "gone_forks": [], "inserted_kept": True}
    return {"stem": stem, "embryo": stem[:4], "arms": arms, "forkmid_audit": audit,
            "parity": {"presafe": {"writer_equal": True, "float_equal": True, "dc_miss": 0},
                       "preshort": {"writer_equal": True, "float_equal": True}}}


def test_aggregate_and_gates():
    pytest.importorskip("tracksdata")
    fp = {"mid_um": 5.0, "removed": "added", "label": "FP"}
    tp = {"mid_um": 2.0, "removed": None, "label": "TP"}
    results = [_fake_result("6bba_a", {"dc0.20": 3, "dc0.15": 2, "ins35": 1}, [fp, fp, tp]),
               _fake_result("6bba_b", {"dc0.20": 3, "dc0.15": 2, "ins35": 1}, [tp]),
               _fake_result("44b6_c", {"dc0.20": -1}, [fp]),
               _fake_result("44b6_d", {}, [])]
    half_of = {"6bba_a": "SELECTION", "6bba_b": "CONFIRMATION", "44b6_c": "SELECTION", "44b6_d": "CONFIRMATION"}
    agg = tl.aggregate(results, half_of)
    assert agg["control"]["6bba/ALL"]["clips"] == 2 and agg["control"]["6bba/ALL"]["delta"] == 0.0
    assert agg["dc0.20"]["6bba/CONFIRMATION"]["delta"] > 0.02
    g = tl.gates(results, agg, half_of)
    assert g["parity"]["pass"] and g["forkmid"]["pass"]
    assert g["forkmid"]["6bba"]["removed_fp"] == 2 and g["forkmid"]["44b6"]["removed_fp"] == 1
    dc = g["deepcenter_m1"]
    assert dc["t_star"] == 0.20 and dc["checks"]["conf_ge_+0.002"]
    assert dc["checks"]["plateau_strict_grid_neighbours_ge_+0.001"] is False  # neighbour 0.25 = control
    assert dc["checks"]["plateau_noncontrol_neighbours_ge_+0.001"] is True
    assert g["insertion"]["ok_each_embryo_ge_0"]["ins35"]
    results[0]["forkmid_audit"].append({"mid_um": 4.6, "removed": "added", "label": "TP"})
    assert not tl.gates(results, agg, half_of)["forkmid"]["pass"]
    md = tl.report_md({"generated_utc": "x", "n_clips": 4, "clips_per_embryo": {}, "missing": [], "leak_clashes": [],
                       "aggregate": agg, "gates": g, "clips": [
                           dict(r, meta={"stage_seconds": {}, "kernel_elapsed_s": 1.0}) for r in results]})
    assert "forkmid 4.5 um audit" in md and "| control | 6bba/ALL |" in md


# ---------------------------------------------------------------------------------------------------------------------
# PRE-REGISTRATION v3 ADDENDUM L (CONTEXT.md 25 Sep 18:20 UTC): L1/L2 DeepCenter, L3 forkmid_v2, L5 insertion labels
# ---------------------------------------------------------------------------------------------------------------------
def test_wilson_lower():
    assert tl.wilson_lower(0, 0) is None
    assert tl.wilson_lower(2, 6) < 0.265 < tl.wilson_lower(3, 6)  # at n = 6 the L2 bound needs 3/6
    assert abs(tl.wilson_lower(3, 6) - 0.2682) < 1e-3 and abs(tl.wilson_lower(6, 7) - 0.6223) < 1e-3
    assert tl.wilson_lower(4, 10) < 0.265  # 0.40 point estimate, bound 0.23: fails L2 although >= 0.35
    assert tl.wilson_lower(0, 8) <= 1e-12 and tl.wilson_lower(5, 5) < 1.0
    assert tl.wilson_lower(3, 6, z=0.0) == pytest.approx(0.5)


def test_fork_precision_evaluable_keeps_old_value():
    # 20 new forks: 4 TP, 2 FP, 14 ignored by the metric -> T9 as coded 4/20 = 0.2, ADDENDUM L2 4/6
    a = {"new_forks": list(range(100, 120)), "tp_forks": [100, 101, 102, 103, 1], "fp_forks": [104, 105, 2],
         "gone_forks": [1, 2, 3]}
    c = {"tp_forks": [1], "fp_forks": [2]}
    res = [{"stem": "6bba_x", "embryo": "6bba", "arms": {"control": c, "dc0.20": a}},
           {"stem": "44b6_y", "embryo": "44b6", "arms": {"control": c, "dc0.20": a}}]
    p = tl._fork_precision(res, "dc0.20", "6bba", {"6bba_x"})
    assert (p["new_forks"], p["new_tp"], p["new_precision"], p["gone_forks"], p["gone_tp"]) == (20, 4, 0.2, 3, 1)
    assert (p["new_fp"], p["new_evaluable"], p["gone_fp"], p["gone_evaluable"]) == (2, 6, 1, 2)
    assert p["new_precision_evaluable"] == pytest.approx(4 / 6)
    assert tl._fork_precision(res, "dc0.20", "6bba", set())["new_precision_evaluable"] is None


def _dc_results(new_tp: int, new_fp: int, new_ignored: int, dnodes: int = 0) -> tuple[list, dict]:
    """t* = 0.20 on 6bba (SELECTION +3 edge TP, CONFIRMATION +3); the CONFIRMATION clip's dc0.20 arm adds the given
    new forks. dc0.15 +2 (the non-control neighbour), 0.25 = control."""
    tp = {"mid_um": 2.0, "removed": None, "label": "TP"}
    fp = {"mid_um": 5.0, "removed": "added", "label": "FP"}
    results = [_fake_result("6bba_a", {"dc0.20": 3, "dc0.15": 2}, [fp, fp, tp]),
               _fake_result("6bba_b", {"dc0.20": 3, "dc0.15": 2}, [tp]),
               _fake_result("44b6_c", {}, [fp]),
               _fake_result("44b6_d", {}, [])]
    new = list(range(200, 200 + new_tp + new_fp + new_ignored))
    arm = results[1]["arms"]["dc0.20"]
    arm["new_forks"] = new
    arm["tp_forks"] = [1, 2] + new[:new_tp]
    arm["fp_forks"] = [3, 4, 5] + new[new_tp:new_tp + new_fp]
    arm["new_fork_sister_um"] = {str(u): (3.0 if i % 2 == 0 else 9.0) for i, u in enumerate(new)}
    arm["nodes"] += dnodes
    half_of = {"6bba_a": "SELECTION", "6bba_b": "CONFIRMATION", "44b6_c": "SELECTION", "44b6_d": "CONFIRMATION"}
    return results, half_of


def test_gates_L1_L2_deepcenter():
    pytest.importorskip("tracksdata")
    # the coded T9 bug: 4 TP + 2 FP + 14 ignored -> old precision 0.2 fails, L2 precision 0.67, n 6, Wilson 0.41 passes
    results, half_of = _dc_results(4, 2, 14)
    g = tl.gates(results, tl.aggregate(results, half_of), half_of)
    dc = g["deepcenter_m1"]
    assert dc["t_star"] == 0.20 and dc["new_fork_precision_conf"]["new_precision"] == 0.2
    assert dc["checks"]["new_fork_precision_ge_0.35"] is False and dc["pass_noncontrol_plateau"] is False  # unchanged
    l2 = dc["L2"]
    assert l2["new_evaluable"] == 6 and l2["new_precision_evaluable"] == pytest.approx(4 / 6)
    assert all(l2["checks"].values()), l2["checks"]
    assert l2["pass_noncontrol_plateau_L2"] is True  # L1 + L2
    assert l2["pass_strict_plateau_L2"] is False  # strict reading: neighbour 0.25 = control has delta 0
    info = l2["forkblob_L4_info"]
    assert info["marginal_forks"] == 20 and info["sister_le_5.0um"] == 10 and info["sister_le_5.0um_share"] == 0.5
    assert info["cell_share"] is None
    d = g["decisions"]["deepcenter_K3b"]
    assert (d["original_T9_strict"], d["strict_plateau_plus_L2"], d["addendum_L1_L2"], d["in_force"]) == (
        False, False, True, False)
    # n_evaluable < 6 fails although precision is perfect; the coded gate passes vacuously (no new forks at all)
    results, half_of = _dc_results(5, 0, 0)
    l2 = tl.gates(results, tl.aggregate(results, half_of), half_of)["deepcenter_m1"]["L2"]
    assert l2["checks"]["n_evaluable_added_ge_6"] is False and l2["pass_noncontrol_plateau_L2"] is False
    results, half_of = _dc_results(0, 0, 0)
    dc = tl.gates(results, tl.aggregate(results, half_of), half_of)["deepcenter_m1"]
    assert dc["pass_noncontrol_plateau"] is True and dc["L2"]["pass_noncontrol_plateau_L2"] is False
    assert dc["L2"]["wilson80_lower"] is None
    # Wilson clause: 4/10 (point 0.40 >= 0.35) has a lower bound 0.23 <= 0.265
    results, half_of = _dc_results(4, 6, 0)
    l2 = tl.gates(results, tl.aggregate(results, half_of), half_of)["deepcenter_m1"]["L2"]
    assert l2["checks"]["new_fork_precision_evaluable_ge_0.35"] and not l2["checks"]["wilson80_lower_gt_0.265"]
    # nodes must stay unchanged
    results, half_of = _dc_results(4, 2, 14, dnodes=3)
    l2 = tl.gates(results, tl.aggregate(results, half_of), half_of)["deepcenter_m1"]["L2"]
    assert l2["checks"]["nodes_unchanged"] is False and l2["pass_noncontrol_plateau_L2"] is False


def _fm_row(mid, removed, label, readmitted=False):
    return {"mid_um": mid, "removed": removed, "label": label, "readmitted_touch": readmitted}


def _fm_results(audits: list[list[dict]], fm_delta: int = 0) -> list[dict]:
    return [_fake_result(f"{'6bba' if i % 2 else '44b6'}_{i}", {"forkmid45": fm_delta}, a) for i, a in enumerate(audits)]


def test_forkmid_v2_pooled_rules():
    fp = _fm_row(5.0, "added", "FP")
    res = _fm_results([[fp], [fp, _fm_row(2.0, None, "TP")], [fp, _fm_row(4.0, None, "TP")]])
    v = tl.forkmid_v2(res, 0.0)
    assert v["pass"] and v["removed_fp"] == 3 and v["tp_in_band"] == 1 and v["removed_tp"] == 0
    assert not tl.forkmid_v2(res, -0.0003)["pass"]  # pooled adj_edge floor -0.0002
    assert tl.forkmid_v2(res, -0.0002)["pass"]
    assert not tl.forkmid_v2(res, None)["pass"]
    res2 = _fm_results([[fp], [fp, _fm_row(3.8, None, "TP")], [fp, _fm_row(4.49, None, "TP")]])
    assert tl.forkmid_v2(res2, 0.0)["checks"]["tp_mid_in_[3.8,4.5)_le_1"] is False  # 2 TP in the band
    res3 = _fm_results([[fp], [fp, _fm_row(3.79, None, "TP")], [fp, _fm_row(4.2, None, "TP")]])
    assert tl.forkmid_v2(res3, 0.0)["pass"]  # 3.79 is outside the band
    res4 = _fm_results([[fp], [fp, _fm_row(5.1, "added", "ignored")]])
    v4 = tl.forkmid_v2(res4, 0.0)
    assert v4["removed_fp"] == 2 and v4["removed_ignored"] == 1 and not v4["pass"]  # ignored forks are not FP
    res5 = _fm_results([[fp], [fp, fp, _fm_row(4.6, "added", "TP")]])
    assert tl.forkmid_v2(res5, 0.0)["checks"]["removed_tp_eq_0"] is False
    res6 = _fm_results([[fp], [fp], [fp]])
    res6[0]["arms"]["forkmid45"]["nodes"] += 1
    assert tl.forkmid_v2(res6, 0.0)["checks"]["nodes_unchanged"] is False
    res6 = _fm_results([[fp], [fp], [fp]])
    res6[1]["arms"]["ins35_forkmid45"]["inserted_kept"] = False
    assert tl.forkmid_v2(res6, 0.0)["checks"]["inserted_forks_unchanged"] is False


def test_forkmid_v2_lowrefine_sensitivity():
    fp = _fm_row(5.0, "added", "FP")
    # a removed FP touching a readmitted node counts as a removed TP in the sensitivity variant
    res = _fm_results([[fp], [fp, fp], [_fm_row(6.0, "added", "FP", readmitted=True)]])
    assert tl.forkmid_v2(res, 0.0)["pass"]
    s = tl.forkmid_v2(res, 0.0, lowdet_adverse=True)
    assert not s["pass"] and s["removed_tp"] == 1 and s["removed_fp"] == 3 and s["readmitted_rows_flagged"] == 1
    # an unremoved fork within 0.7 um of 4.5 touching a readmitted node is adverse (lowrefine may move it across)
    res = _fm_results([[fp], [fp, fp], [fp, _fm_row(3.9, None, "ignored", readmitted=True)]])
    assert tl.forkmid_v2(res, 0.0)["pass"]
    assert not tl.forkmid_v2(res, 0.0, lowdet_adverse=True)["pass"]
    # far from 4.5 and not removed: harmless
    res = _fm_results([[fp], [fp, fp], [fp, _fm_row(2.0, None, "TP", readmitted=True)]])
    assert tl.forkmid_v2(res, 0.0, lowdet_adverse=True)["pass"]
    # the input rows are never modified
    rows = [_fm_row(6.0, "added", "FP", readmitted=True)]
    tl.forkmid_v2(_fm_results([rows]), 0.0, lowdet_adverse=True)
    assert rows[0]["label"] == "FP" and rows[0]["removed"] == "added"


def test_gates_L3_L5_and_decisions():
    pytest.importorskip("tracksdata")
    fp = {"mid_um": 5.0, "removed": "added", "label": "FP", "readmitted_touch": False}
    # 3 removed FP, none on 44b6: the original T9 gate fails on its 44b6 clause, ADDENDUM L3 passes
    results = [_fake_result("6bba_a", {"ins35": -1}, [fp, fp]), _fake_result("6bba_b", {}, [fp]),
               _fake_result("44b6_c", {}, []), _fake_result("44b6_d", {}, [])]
    half_of = {"6bba_a": "SELECTION", "6bba_b": "CONFIRMATION", "44b6_c": "SELECTION", "44b6_d": "CONFIRMATION"}
    agg = tl.aggregate(results, half_of)
    g = tl.gates(results, agg, half_of)
    assert g["forkmid"]["pass"] is False and g["forkmid_v2"]["pass"] is True
    assert g["forkmid_v2"]["pooled"]["clips"] == 4 and g["forkmid_v2"]["pooled_adj_edge_delta"] == 0.0
    assert g["forkmid_v2_lowrefine_sensitivity"]["pass"] is True
    d = g["decisions"]["forkmid_K3"]
    assert (d["original_T9"], d["addendum_L3"], d["in_force"]) == (False, True, False)
    assert "original until the user's OK" in d["applies"]
    # pooled adj_edge harm: the forkmid arm loses edge TP on one clip
    results[2]["arms"]["forkmid45"]["row"] = results[2]["arms"]["control"]["row"] | {"edge_tp": 89, "edge_fn": 11,
                                                                                    "adj_edge_jaccard": 89 / 105}
    g2 = tl.gates(results, tl.aggregate(results, half_of), half_of)
    assert g2["forkmid_v2"]["pooled_adj_edge_delta"] < -0.0002 and g2["forkmid_v2"]["pass"] is False
    # L5: ins35 CONFIRMATION delta is 0 here; make SELECTION-only harm irrelevant and CONFIRMATION harm a warning
    results[1]["arms"]["ins35"]["row"] = results[1]["arms"]["control"]["row"] | {"edge_tp": 89, "edge_fn": 11,
                                                                                "adj_edge_jaccard": 89 / 105}
    g3 = tl.gates(results, tl.aggregate(results, half_of), half_of)
    assert g3["insertion"]["ok_each_embryo_ge_0"]["ins35"] is False  # original key and value kept
    l5 = g3["insertion_L5"]
    assert l5["check_is_warning_only"] and l5["labels"]["ins35_forkmid45"].startswith("IN-SAMPLE UPPER BOUND")
    assert any(w.startswith("ins35:") for w in l5["warnings"]) and "CLOSED" in l5["nosteal0"]
    md = tl.report_md({"generated_utc": "x", "n_clips": 4, "clips_per_embryo": {}, "missing": [], "leak_clashes": [],
                       "aggregate": tl.aggregate(results, half_of), "gates": g3, "clips": [
                           dict(r, meta={"stage_seconds": {}, "kernel_elapsed_s": 1.0}) for r in results]})
    assert "ORIGINAL T9 vs PRE-REGISTRATION v3 ADDENDUM L" in md and "IN-SAMPLE UPPER BOUND" in md
    assert "forkmid_v2 (ADDENDUM L3" in md and "forkmid_v2_lowrefine_sensitivity" in md
    assert "original until the user's OK" in md and "IN FORCE" in md


def test_sister_um():
    nodes = {1: {"t": 1, "z": 0.0, "y": 0.0, "x": 0.0}, 2: {"t": 1, "z": 2.0, "y": 0.0, "x": 0.0},
             3: {"t": 1, "z": 0.0, "y": 8.0, "x": 0.0}}
    assert tl.sister_um(nodes, (1, 2)) == pytest.approx(3.25)
    assert tl.sister_um(nodes, (1, 3)) == pytest.approx(3.25)
    assert tl.sister_um(nodes, (1, 2, 3)) is None and tl.sister_um(nodes, (1, 9)) is None
