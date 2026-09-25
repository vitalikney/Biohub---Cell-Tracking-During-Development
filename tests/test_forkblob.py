"""Ideas workflow v4 L1 / PRE-REGISTRATION v3 ADDENDUM L4: --patch forkblob on --base x138
(tools/build_probe_kernel.py FORKBLOB_FN) and the lab arm tools/forkblob_lab.py.

    python -m pytest tests/test_forkblob.py
"""
import copy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.ndimage import gaussian_filter, map_coordinates

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import tools.build_probe_kernel as bpk  # noqa: E402

BUILDER = str(ROOT / "tools" / "build_probe_kernel.py")
NL = "\n"
SCALE = (1.625, 0.40625, 0.40625)
SIGMA = (0.6, 1.5, 1.5)


def _patched(*names: str) -> dict:
    bpk.CELL.clear()
    bpk.CELL.update(bpk.BASES["x138"])
    nb = json.loads(bpk.BASES["x138"]["nb"].read_text(encoding="utf-8"))
    code = [c for c in nb["cells"] if c["cell_type"] == "code"]
    cells = {k: "".join(c["source"]) for k, c in enumerate(code)}
    try:
        for name in names:
            bpk.PATCHES[name](cells)
    finally:  # CELL is module state shared with the other test files (exp39 base by default)
        bpk.CELL.clear()
        bpk.CELL.update(bpk.BASES["exp39"])
    return cells


def _post(cells: dict) -> str:
    return cells[bpk.BASES["x138"]["post"]]


def _undo_forkblob(post: str) -> str:
    post = post.replace(NL + bpk.FORKBLOB_FN + bpk._FM_FILTER_DEF, bpk._FM_FILTER_DEF)
    return post.replace(bpk.FORKBLOB_CALL, "")


def _ns(enable="1", force_fail="0") -> dict:
    env = {"BIOHUB_FORKBLOB_ENABLE": enable, "BIOHUB_FORKBLOB_FORCE_FAIL": force_fail}
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        ns = {"os": os, "np": np, "VOXEL_SCALE_UM": SCALE}
        exec(bpk.FORKBLOB_FN, ns)
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return ns


# ---------------------------------------------------------------------------------------------------------------------
# valley: local crop == full-frame blur
# ---------------------------------------------------------------------------------------------------------------------
def _valley_full(frame, a, b):
    """Reference: blur the WHOLE frame (the prototype research/.../forkvalley2.py recipe), 41 samples, 8:33 / min end."""
    blurred = gaussian_filter(np.asarray(frame, dtype=np.float32), sigma=SIGMA)
    a, b = np.asarray(a, float), np.asarray(b, float)
    s = np.linspace(0, 1, 41)
    prof = map_coordinates(blurred, (a[None] + s[:, None] * (b - a)[None]).T, order=1, mode="nearest")
    return float(prof[8:33].min() / max(min(prof[0], prof[-1]), 1e-6))


def _blob(shape, centre, sig_zyx, amp):
    zz, yy, xx = np.meshgrid(*[np.arange(n, dtype=np.float64) for n in shape], indexing="ij")
    d = sum(((g - c) / s) ** 2 for g, c, s in zip((zz, yy, xx), centre, sig_zyx))
    return amp * np.exp(-0.5 * d)


def _volume(seed=0, shape=(20, 72, 72)):
    rng = np.random.default_rng(seed)
    vol = rng.normal(100.0, 8.0, size=shape)
    for _ in range(12):
        c = rng.uniform([1, 4, 4], [shape[0] - 2, shape[1] - 5, shape[2] - 5])
        vol += _blob(shape, c, (1.2, 5.0, 5.0), rng.uniform(200, 800))
    return np.clip(vol, 0, 65535).astype(np.uint16)


def test_crop_valley_matches_full_frame():
    ns = _ns()
    vol = _volume()
    rng = np.random.default_rng(1)
    pairs = [((10.0, 36.0, 30.0), (10.4, 36.5, 41.2)),  # interior
             ((0.0, 0.0, 0.0), (1.3, 6.0, 7.5)),  # frame corner (crop edge == frame edge)
             ((19.0, 71.0, 71.0), (17.2, 60.3, 66.0)),  # opposite corner
             ((5.5, 2.0, 70.0), (6.1, 12.0, 69.0))]
    for _ in range(40):
        a = rng.uniform([0, 0, 0], [19, 71, 71])
        pairs.append((tuple(a), tuple(np.clip(a + rng.normal(0, [1.5, 6, 6]), 0, [19, 71, 71]))))
    worst = 0.0
    for a, b in pairs:
        crop = ns["forkblob_valley"](vol, a, b)
        full = _valley_full(vol, a, b)
        worst = max(worst, abs(crop - full))
        assert abs(crop - full) <= 0.005, (a, b, crop, full)
    assert worst < 1e-4  # the margin makes the crop exact up to float rounding


def test_valley_one_blob_vs_two_blobs():
    ns = _ns()
    shape = (16, 64, 64)
    one = (_blob(shape, (8, 32, 32), (1.5, 9.0, 6.0), 1000.0) + 100).astype(np.uint16)  # elongated in y: one blob
    two = (_blob(shape, (8, 26, 32), (1.0, 2.5, 2.5), 1000.0) + _blob(shape, (8, 38, 32), (1.0, 2.5, 2.5), 1000.0)
           + 100).astype(np.uint16)
    a, b = (8.0, 26.0, 32.0), (8.0, 38.0, 32.0)  # 12 vox in y = 4.875 um
    assert ns["forkblob_valley"](one, a, b) >= 0.95
    assert ns["forkblob_valley"](two, a, b) < 0.5


# ---------------------------------------------------------------------------------------------------------------------
# the pure function on synthetic forks
# ---------------------------------------------------------------------------------------------------------------------
def _node(i, t, z, y, x):
    return {"node_id": i, "t": t, "z": float(z), "y": float(y), "x": float(x)}


FRAME_SHAPE = (16, 64, 400)


def _frames():
    """Frame t=1: one blob elongated along y at x = 50, 150 and 350 (forks A/E, B, D); two separate blobs at x = 250
    (fork C)."""
    one = np.full(FRAME_SHAPE, 100.0)
    for xc in (50.0, 150.0, 350.0):  # forks A, B, D and E sit on one elongated blob (along y)
        one += _blob(FRAME_SHAPE, (8, 32, xc), (1.5, 10.0, 3.0), 1000.0)
    for yc in (26.0, 38.0):  # fork C: two separate blobs
        one += _blob(FRAME_SHAPE, (8, yc, 250.0), (1.0, 2.0, 2.0), 1000.0)
    return {1: one.astype(np.uint16)}


def _graph():
    """P at t=0; sisters at t=1, 12 voxels apart in y (4.875 um) unless noted.
    A (1, x=50):  one blob, ILP edge scored 0.8        -> added edge dropped
    B (2, x=150): one blob, ILP edge unscored (0.0)    -> ILP edge dropped
    C (3, x=250): two blobs (valley low)               -> kept
    D (4, x=350): one blob but sisters 13.5 vox (5.48 um) apart -> kept, no frame read needed
    E (5, x=50, t=0 again): DaughterNet-inserted extra child -> untouched
    track (6 -> 7)."""
    nodes, edges = {}, []
    specs = {1: (50.0, 12.0, 0.8, "safe"), 2: (150.0, 12.0, 0.0, "safe"), 3: (250.0, 12.0, 0.8, "safe"),
             4: (350.0, 13.5, 0.8, "safe"), 5: (50.0, 12.0, 0.0, "divins")}
    nid = 100
    for p, (xc, dy, prob, kind) in specs.items():
        nodes[p] = _node(p, 0, 8, 32, xc)
        c1, c2 = nid, nid + 1
        nid += 2
        nodes[c1] = _node(c1, 1, 8, 32 - dy / 2, xc)
        nodes[c2] = _node(c2, 1, 8, 32 + dy / 2, xc)
        edges.append({"source_id": p, "target_id": c1, "edge_prob": prob, "distance_um": 1.0})
        extra = {"source_id": p, "target_id": c2, "edge_prob": None, "distance_um": 1.0}
        extra.update({"safe_division": 1} if kind == "safe" else {"div_inserted": 1, "div_steal_from": -1})
        edges.append(extra)
    nodes[6] = _node(6, 0, 1, 1, 1)
    nodes[7] = _node(7, 1, 1, 1, 2)
    edges.append({"source_id": 6, "target_id": 7, "edge_prob": 0.9, "distance_um": 0.4})
    return nodes, edges


def _reader(frames, calls):
    def read(t):
        calls.append(int(t))
        return frames[int(t)]
    return read


def test_synthetic_forks():
    ns = _ns()
    nodes, edges = _graph()
    nodes0, edges0 = copy.deepcopy(nodes), copy.deepcopy(edges)
    calls = []
    kept, counters, vetoed = ns["forkblob_edges"](nodes, edges, _reader(_frames(), calls))
    assert nodes == nodes0 and edges == edges0  # inputs untouched
    pairs = {(e["source_id"], e["target_id"]) for e in kept}
    assert (1, 100) in pairs and (1, 101) not in pairs  # A: added edge dropped
    assert (2, 102) not in pairs and (2, 103) in pairs  # B: unscored ILP edge dropped
    assert (3, 104) in pairs and (3, 105) in pairs  # C: two blobs -> kept
    assert (4, 106) in pairs and (4, 107) in pairs  # D: 5.48 um > 5.0 -> kept
    assert (5, 108) in pairs and (5, 109) in pairs  # E: DaughterNet fork untouched
    assert (6, 7) in pairs and len(kept) == len(edges) - 2
    assert counters == {"forkblob_forks_seen": 4, "forkblob_close": 3, "forkblob_removed": 2,
                        "forkblob_removed_ilp_edge": 1, "forkblob_removed_added_edge": 1, "forkblob_skipped": 0}
    assert calls == [1, 1, 1]  # one read per close fork (A, B, C); D is never read
    assert [(v["parent"], v["dropped"], v["side"]) for v in vetoed] == [(1, (1, 101), "added"), (2, (2, 102), "ilp")]
    assert all(v["valley"] >= 0.95 and abs(v["sister_um"] - 4.875) < 1e-6 and v["t"] == 1 for v in vetoed)


def test_thresholds_inclusive_and_skips():
    ns = _ns()
    nodes, edges = _graph()
    frames = _frames()
    # distance threshold inclusive: D at exactly 5.484 um is vetoed with max_um = 5.484375
    _, c, v = ns["forkblob_edges"](nodes, edges, _reader(frames, []), max_um=13.5 * 0.40625)
    assert c["forkblob_close"] == 4 and 4 in [x["parent"] for x in v]
    # valley threshold: nothing passes a valley of 10
    kept, c, v = ns["forkblob_edges"](nodes, edges, _reader(frames, []), min_valley=10.0)
    assert kept is edges and c["forkblob_removed"] == 0 and v == []
    # sisters not both at t + 1, a parent with one child left, a parent with three children: skipped, never read
    nodes, edges = _graph()
    nodes[100]["t"] = 2
    edges = [e for e in edges if (e["source_id"], e["target_id"]) != (2, 102)]
    nodes[99] = _node(99, 1, 8, 40, 250)
    edges.append({"source_id": 3, "target_id": 99, "edge_prob": 0.5})
    calls = []
    kept, c, v = ns["forkblob_edges"](nodes, edges, _reader(frames, calls))
    assert c["forkblob_skipped"] == 3 and c["forkblob_removed"] == 0 and calls == [] and kept is edges


def test_nan_valley_keeps_fork():
    ns = _ns()
    nodes, edges = _graph()
    frames = {1: np.full(FRAME_SHAPE, np.nan, dtype=np.float32)}
    kept, c, v = ns["forkblob_edges"](nodes, edges, _reader(frames, []))
    assert kept is edges and c["forkblob_close"] == 3 and c["forkblob_removed"] == 0


# ---------------------------------------------------------------------------------------------------------------------
# kernel call block: ENABLE=0 identity, fail-soft, frames through read_test_frame
# ---------------------------------------------------------------------------------------------------------------------
def _call_fn(ns):
    src = ("def _f(dataset, edges, nodes_by_id, stats, repair_frame_cache):" + NL + bpk.FORKBLOB_CALL
           + "    return nodes_by_id, edges, stats" + NL)
    exec(src, ns)
    return ns["_f"]


def test_enable0_identity():
    ns = _ns(enable="0")
    assert ns["FORKBLOB_ENABLE"] is False
    ns["forkblob_final_graph"] = None  # would raise if called
    ns["read_test_frame"] = None
    nodes, edges = _graph()
    cache = {}
    out_nodes, out_edges, stats = _call_fn(ns)("d", edges, nodes, {}, cache)
    assert out_nodes is nodes and out_edges is edges and stats == {} and cache == {}


def test_call_block_reads_frames_via_notebook_reader(capsys):
    ns = _ns()
    frames = _frames()
    seen = []

    def read_test_frame(dataset, t, frame_cache):
        seen.append((dataset, t, id(frame_cache)))
        frame_cache[t] = frames[t]
        return frames[t]

    ns["read_test_frame"] = read_test_frame
    nodes, edges = _graph()
    nodes0 = copy.deepcopy(nodes)
    cache = {}
    out_nodes, out_edges, stats = _call_fn(ns)("ds1", edges, nodes, {}, cache)
    assert out_nodes is nodes and nodes == nodes0
    assert len(out_edges) == len(edges) - 2 and stats["forkblob_removed"] == 2 and "forkblob_failed" not in stats
    assert seen and all(s == ("ds1", 1, id(cache)) for s in seen) and 1 in cache
    out = capsys.readouterr().out
    assert "[ds1] forkblob: forks=4 close=3 removed=2" in out
    assert "[ds1] forkblob veto: parent=1 t=1 dropped=1->101 (added edge)" in out
    assert "[ds1] forkblob veto: parent=2 t=1 dropped=2->102 (ilp edge)" in out


def test_force_fail_keeps_input_graph(capsys):
    ns = _ns(force_fail="1")
    ns["read_test_frame"] = lambda *a: (_ for _ in ()).throw(AssertionError("no read on FORCE_FAIL"))
    nodes, edges = _graph()
    edges0 = copy.deepcopy(edges)
    stats = {}
    out_nodes, out_edges, stats = _call_fn(ns)("d", edges, nodes, stats, {})
    assert out_edges is edges and edges == edges0 and stats == {"forkblob_failed": 1}
    assert "FORKBLOB FAILED (RuntimeError: BIOHUB_FORKBLOB_FORCE_FAIL=1" in capsys.readouterr().out
    # a reader exception and a missing dataset name fail soft too
    ns = _ns()
    ns["read_test_frame"] = lambda *a: (_ for _ in ()).throw(OSError("chunk gone"))
    stats = {}
    assert ns["forkblob_final_graph"](nodes, edges, stats, "d", {}) is edges and stats == {"forkblob_failed": 1}
    stats = {}
    assert ns["forkblob_final_graph"](nodes, edges, stats, None, {}) is edges and stats == {"forkblob_failed": 1}
    out = capsys.readouterr().out
    assert "FORKBLOB FAILED (OSError: chunk gone)" in out and "FORKBLOB FAILED (ValueError" in out


# ---------------------------------------------------------------------------------------------------------------------
# builder: splice, order, anchors, refusals, builds
# ---------------------------------------------------------------------------------------------------------------------
def test_only_intended_changes_and_order():
    assert _undo_forkblob(_post(_patched("forkblob"))) == _post(_patched())
    for combo in (("forkmid", "forkblob"), ("divinsert", "forkmid", "forkblob", "safetail"),
                  ("divinsert", "lowrefine", "forkmid", "forkblob", "safetail"), ("divinsert", "forkblob", "safetail")):
        post = _post(_patched(*combo))
        others = tuple(n for n in combo if n != "forkblob")
        assert _undo_forkblob(post) == _post(_patched(*others)), combo
        assert post.count(bpk.FORKBLOB_CALL) == 1 and post.count("def forkblob_edges(") == 1
        i_call = post.index(bpk.FORKBLOB_CALL)
        assert post[i_call + len(bpk.FORKBLOB_CALL):].startswith(bpk._FM_FINAL_PRINT)
        if "forkmid" in combo:  # right after the forkmid call; definitions after forkmid's
            assert post[:i_call].endswith(bpk.FORKMID_CALL)
            assert post.index("def forkmid_final_graph(") < post.index("def forkblob_edges(")
        if "divinsert" in combo:
            assert post.index("    # ---- /divinsert ----" + NL) < i_call
            assert bpk.safetail_divins_call() in post
        assert post.index("def forkblob_final_graph(") < post.index("def filter_output_graph(")


def test_patched_cells_compile():
    for names in (("forkblob",), ("forkmid", "forkblob"), ("divinsert", "lowrefine", "forkmid", "forkblob", "safetail")):
        cells = _patched(*names)
        for k, src in cells.items():
            if k != bpk.NEW_CELLS_KEY:
                compile(src, f"cell{k}[{'+'.join(names)}]", "exec")
        for _, src in cells.get(bpk.NEW_CELLS_KEY, []):
            compile(src, "new_cell", "exec")


def test_anchor_strict():
    post = _post(_patched())
    for bad, n in ((post + bpk._FM_FINAL_PRINT, 2), (post.replace(bpk._FM_FINAL_PRINT, ""), 0),
                   (post.replace(bpk._FM_FILTER_DEF, ""), 0)):
        with pytest.raises(AssertionError, match=f"anchor count {n}"):
            bpk.forkblob_postproc_source(bad)


def _run(name, *args):
    return subprocess.run([sys.executable, BUILDER, name, *args], capture_output=True, text=True, cwd=ROOT)


def test_builder_refusals():
    cases = [
        (["--patch", "forkblob"], "needs --base x138"),
        (["--base", "x138", "--set", "FORKBLOB_ENABLE=1"], "need --patch forkblob"),
        (["--base", "x138", "--patch", "forkblob", "--set", "FORKBLOB_ENABLE=2"], "must be 0 or 1"),
        (["--base", "x138", "--patch", "forkblob", "--set", "FORKBLOB_FORCE_FAIL=1"], "needs --lab"),
        (["--base", "x138", "--patch", "forkblob", "--set", "FORKBLOB_MAX_UM=6"], "unknown forkblob knobs"),
    ]
    for args, msg in cases:
        r = _run("zz-forkblob-refusal", *args)
        assert r.returncode != 0 and msg in r.stderr, (args, r.stderr[-300:])
    assert not (ROOT / "experiments" / "zz-forkblob-refusal").exists()


def _code(out: Path) -> list:
    nb = json.loads(next(out.glob("*.ipynb")).read_text(encoding="utf-8"))
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def test_build_k3_and_disabled_build():
    name = "zz-forkblob-build-test"
    out = ROOT / "experiments" / name
    k2 = ["--set", "DIVINS_ENABLE=1", "--set", "DIVINS_STEAL=1", "--set", "DIVINS_CAP=4", "--set", "DIVINS_FRAME_CAP=1",
          "--set", "DIVINS_ALPHA=1", "--set", "DIVINS_THRESH=0.4", "--set", "DIVINS_DUMP=0",
          "--set", "REPAIR_DEADLINE_S=34200", "--set", "DIVINS_DEADLINE_S=28800", "--set", "LOWREFINE_ENABLE=1"]
    try:
        # command-line order does not matter: ... -> forkmid -> forkblob -> safetail
        r = _run(name, "--base", "x138", "--patch", "forkblob", "--patch", "safetail", "--patch", "forkmid",
                 "--patch", "divinsert", "--patch", "lowrefine", *k2, "--set", "FORKMID_ENABLE=1",
                 "--set", "FORKBLOB_ENABLE=1")
        assert r.returncode == 0, r.stderr[-500:]
        code = _code(out)
        assert 'os.environ["BIOHUB_FORKBLOB_ENABLE"] = "1"' in code[0]
        post = [s for s in code if "def filter_output_graph(" in s]
        assert len(post) == 1 and bpk.FORKMID_CALL + bpk.FORKBLOB_CALL + bpk._FM_FINAL_PRINT in post[0]
        for i, s in enumerate(code):
            compile(s, f"cell{i}", "exec")
        probe = json.loads((out / "probe.json").read_text(encoding="utf-8"))
        assert "lab" not in probe and probe["change"]["PATCHES"] == "divinsert+lowrefine+forkmid+forkblob+safetail"
        k3_code = code
        shutil.rmtree(out)
        # the same build with FORKBLOB_ENABLE=0: only cell 0's knob line and the forkblob text differ from K3
        r = _run(name, "--base", "x138", "--patch", "forkblob", "--patch", "safetail", "--patch", "forkmid",
                 "--patch", "divinsert", "--patch", "lowrefine", *k2, "--set", "FORKMID_ENABLE=1",
                 "--set", "FORKBLOB_ENABLE=0")
        assert r.returncode == 0 and "exact no-op" in r.stdout, r.stderr[-500:]
        code = _code(out)
        assert len(code) == len(k3_code)
        assert [a == b for a, b in zip(code, k3_code)].count(False) == 1  # cell 0 only
        assert code[0].replace('FORKBLOB_ENABLE"] = "0"', 'FORKBLOB_ENABLE"] = "1"') == k3_code[0]
        shutil.rmtree(out)
        # ENABLE=0 alone: every cell but the post-processing one is the base's; undoing the text gives the base cell
        r = _run(name, "--base", "x138", "--patch", "forkblob")
        assert r.returncode == 0 and "exact no-op" in r.stdout, r.stderr[-500:]
        code = _code(out)
        base = [s for k, s in sorted(_patched().items()) if k != bpk.NEW_CELLS_KEY]
        post_i = bpk.BASES["x138"]["post"]
        assert len(code) == len(base)
        assert all(code[i] == base[i] for i in range(len(code)) if i != post_i)
        assert _undo_forkblob(code[post_i]) == base[post_i]
    finally:
        shutil.rmtree(out, ignore_errors=True)


# ---------------------------------------------------------------------------------------------------------------------
# lab arm
# ---------------------------------------------------------------------------------------------------------------------
def test_lab_clip_on_synthetic_dump(tmp_path):
    zarr = pytest.importorskip("zarr")
    import forkblob_lab as fbl
    import trainlab_io as tio

    nodes, edges = _graph()
    arrays = {}
    for stage in tio.TRAINLAB_STAGES:
        arrays.update(tio.trainlab_graph_arrays(stage + "_", nodes, edges))
    arrays["dc_tzyx"] = np.zeros((0, 4))
    arrays["dc_score"] = np.zeros(0)
    meta = {"dataset": "6bba_synth", "dc_bundle": 0, "presafe_stats": {}, "preshort_stats": {}, "final_stats": {},
            "stage_seconds": {}, "kernel_elapsed_s": 0.0, "n_dc": 0, "format": 1}
    dump = tmp_path / "trainlab" / "6bba_synth.npz"
    dump.parent.mkdir()
    np.savez_compressed(dump, meta_json=np.asarray(json.dumps(meta)), **arrays)
    vol = np.stack([_frames()[1]] * 2)
    z = zarr.open(str(tmp_path / "6bba_synth.zarr" / "0"), mode="w", shape=vol.shape, dtype=vol.dtype,
                  chunks=(1,) + vol.shape[1:])
    z[:] = vol
    r = fbl.lab_clip({"stem": "6bba_synth", "dump": str(dump), "zarr": str(tmp_path / "6bba_synth.zarr"), "gt": None})
    assert r["nodes_unchanged"] and r["counters"]["forkblob_removed"] == 2
    assert [v["parent"] for v in r["vetoed"]] == [1, 2] and r["frames_read"] == 1
    assert r["arms"]["forkblob"]["edges"] == r["arms"]["control"]["edges"] - 2
    assert r["arms"]["forkblob"]["nodes"] == r["arms"]["control"]["nodes"]


def _res(stem, tp, fp, ign, seen, ctrl_row, arm_row):
    vet = [{"div_label": "TP"}] * tp + [{"div_label": "FP"}] * fp + [{"div_label": "ignored"}] * ign
    return {"stem": stem, "embryo": stem[:4], "vetoed": vet, "counters": {"forkblob_forks_seen": seen},
            "nodes_unchanged": True, "arms": {"control": {"row": ctrl_row, "nodes": 10}, "forkblob": {"row": arm_row, "nodes": 10}}}


def _row(tp, fp, fn, dtp, dfp, dfn, adj):
    return {"edge_tp": tp, "edge_fp": fp, "edge_fn": fn, "division_tp": dtp, "division_fp": dfp, "division_fn": dfn,
            "edge_jaccard": tp / (tp + fp + fn), "adj_edge_jaccard": adj, "node_recall": 1.0, "total_node_ratio": 0.0,
            "num_pred_nodes": 10, "n_total": 10.0}


def test_harm_gate_rules(monkeypatch):
    import forkblob_lab as fbl
    import trainlab as tl

    def fake_summarise(rows):
        s = {k: sum(r[k] for r in rows) for k in ("division_tp", "division_fp", "division_fn")}
        s["division_jaccard"] = s["division_tp"] / max(1, s["division_tp"] + s["division_fp"] + s["division_fn"])
        s["adj_edge_jaccard"] = float(np.mean([r["adj_edge_jaccard"] for r in rows]))
        s["score"] = s["adj_edge_jaccard"] + 0.1 * s["division_jaccard"]
        return s

    monkeypatch.setattr(tl, "summarise_rows", fake_summarise)
    c, a_good = _row(90, 10, 10, 5, 5, 5, 0.8), _row(90, 10, 10, 5, 3, 5, 0.8)
    good = [_res("6bba_a", 0, 2, 3, 40, c, a_good)]
    g = fbl.harm_gate(good, 1, [])
    assert g["pass"] and g["dose"] == 5 / 40 and g["vetoed_fp"] == 2
    # dose below 10%
    assert not fbl.harm_gate([_res("6bba_a", 0, 1, 0, 40, c, a_good)], 1, [])["checks"]["dose_ge_10pct"]
    # one TP needs >= 3 FP; two TP always fail
    assert fbl.harm_gate([_res("6bba_a", 1, 3, 1, 40, c, a_good)], 1, [])["checks"]["tp0_or_fp_ge_3tp"]
    assert not fbl.harm_gate([_res("6bba_a", 1, 2, 2, 40, c, a_good)], 1, [])["checks"]["tp0_or_fp_ge_3tp"]
    assert not fbl.harm_gate([_res("6bba_a", 2, 9, 0, 40, c, a_good)], 1, [])["checks"]["vetoed_evaluable_tp_le_1"]
    # div_J lower, adj_edge drop, missing clips
    worse = _row(90, 10, 10, 4, 5, 6, 0.8)
    assert not fbl.harm_gate([_res("6bba_a", 0, 2, 3, 40, c, worse)], 1, [])["checks"]["div_J_arm_ge_control"]
    drop = _row(90, 10, 10, 5, 3, 5, 0.7997)
    assert not fbl.harm_gate([_res("6bba_a", 0, 2, 3, 40, c, drop)], 1, [])["checks"]["adj_edge_delta_ge_-0.0002"]
    assert not fbl.harm_gate(good, 2, ["6bba_b"])["checks"]["clips_complete"]


# ---------------------------------------------------------------------------------------------------------------------
# exp56 dummy (x138 verbatim on the 4 visible test clips): the report says the rule flags 15 of 62 forks
# ---------------------------------------------------------------------------------------------------------------------
def _find(rel: str):
    for base in (ROOT, *ROOT.parents):
        if (base / rel).exists():
            return base / rel
    return None


def test_exp56_dummy_flag_count():
    csv = _find("_dl/biohub-exp56-x138-verbatim/submission.csv")
    test_dir = _find("biohub-cell-tracking-during-development/test")
    if csv is None or test_dir is None or not (test_dir / "6bba_05db0fb1.zarr").is_dir():
        pytest.skip("exp56 dummy submission.csv or the local test zarrs are not available")
    import forkblob_lab as fbl

    ns = fbl.forkblob_namespace()
    forks = flagged = 0
    per = {}
    for ds, (nodes, edges) in fbl.csv_graphs(csv).items():
        _, c, v = ns["forkblob_edges"](nodes, edges, fbl.ZarrFrames(test_dir / f"{ds}.zarr"))
        forks += c["forkblob_forks_seen"]
        flagged += c["forkblob_removed"]
        per[ds] = c["forkblob_removed"]
    assert (forks, flagged) == (62, 15), per
    assert per["6bba_05db0fb1"] == 5


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
