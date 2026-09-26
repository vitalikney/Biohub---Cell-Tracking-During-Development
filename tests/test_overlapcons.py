"""OVERLAP-CONSENSUS kernel stage: --patch overlapcons on --base x138 (tools/build_probe_kernel.py).

Checks: the embedded module texts are byte-identical to tools/overlap_reg.py / tools/overlap_splice.py; undoing the
writer edit gives the base post-processing cell back; a K2-like build and its overlapcons twin differ only by the patch
block; builder refusals; and an end-to-end run of the EMBEDDED cell + the PATCHED write_test_submission on synthetic
overlapping videos (mocked geff reader / tail), against the UNPATCHED writer: ENABLE=0 -> byte-identical CSV and stats,
no accepted pair -> identical, an accepted pair -> the discordant component is spliced (fresh node ids written),
FORCE_FAIL / budget / stage-time limit -> identical CSV with the matching log line.

    python -m pytest tests/test_overlapcons.py
"""
import copy
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import tools.build_probe_kernel as bpk  # noqa: E402

BUILDER = str(ROOT / "tools" / "build_probe_kernel.py")
NL = "\n"
K2_ARGS = ["--base", "x138", "--patch", "divinsert", "--patch", "safetail", "--patch", "lowrefine",
           "--set", "DIVINS_ENABLE=1", "--set", "DIVINS_STEAL=1", "--set", "DIVINS_CAP=4", "--set", "DIVINS_FRAME_CAP=1",
           "--set", "DIVINS_ALPHA=1", "--set", "DIVINS_THRESH=0.4", "--set", "DIVINS_DUMP=0",
           "--set", "REPAIR_DEADLINE_S=34200", "--set", "DIVINS_DEADLINE_S=28800", "--set", "LOWREFINE_ENABLE=1"]


def _base_cells() -> dict:
    nb = json.loads(bpk.BASES["x138"]["nb"].read_text(encoding="utf-8"))
    code = [c for c in nb["cells"] if c["cell_type"] == "code"]
    return {k: "".join(c["source"]) for k, c in enumerate(code)}


def _patched(*names: str) -> dict:
    bpk.CELL.clear()
    bpk.CELL.update(bpk.BASES["x138"])
    cells = _base_cells()
    try:
        for name in names:
            bpk.PATCHES[name](cells)
    finally:  # CELL is module state shared with the other test files (exp39 base by default)
        bpk.CELL.clear()
        bpk.CELL.update(bpk.BASES["exp39"])
    return cells


def _undo_writer(post: str) -> str:
    """Inverse of overlapcons_writer_source: drop the hold line and the hook, dedent the row block by 4."""
    post = post.replace(bpk._OC_WRITER_HOLD, "")
    i0 = post.index(bpk.OVERLAPCONS_WRITER_HOOK)
    i1 = post.index(bpk._OC_WRITER_END, i0)
    body = post[i0 + len(bpk.OVERLAPCONS_WRITER_HOOK):i1]
    body = "".join(ln[4:] if ln.strip() else ln for ln in body.splitlines(keepends=True))
    return post[:i0] + body + post[i1:]


# ---------------------------------------------------------------------------------------------------------------------
# builder
# ---------------------------------------------------------------------------------------------------------------------
def test_patch_undo_and_embedded_modules_verbatim():
    base = _base_cells()
    cells = _patched("overlapcons")
    new = cells.pop(bpk.NEW_CELLS_KEY)
    post = bpk.BASES["x138"]["post"]
    assert [k for k in base if cells[k] != base[k]] == [post]
    assert _undo_writer(cells[post]) == base[post]
    assert len(new) == 1 and new[0][0] == bpk.BASES["x138"]["predict"]
    cell = new[0][1]
    compile(cell, "overlapcons_cell", "exec")
    compile(cells[post], "post", "exec")
    for var, fname in (("OVERLAP_REG_SRC", "overlap_reg.py"), ("OVERLAP_SPLICE_SRC", "overlap_splice.py")):
        m = re.search(r"^" + var + r" = (r'''.*?''')$", cell, re.M | re.S)
        assert m and eval(m.group(1)) == (ROOT / "tools" / fname).read_text(encoding="utf-8")  # noqa: S307
    # the writer hook sits between the empty-graph assert and the row block; no loop control inside the row block
    assert cells[post].count("overlapcons_final_graphs(_oc_final)") == 1
    assert cells[post].count(bpk._OC_WRITER_HOLD) == 1


def test_composes_with_the_k2_patches_in_builder_order():
    cells = _patched("divinsert", "lowrefine", "overlapcons", "safetail")
    ref = _patched("divinsert", "lowrefine", "safetail")
    post = bpk.BASES["x138"]["post"]
    assert _undo_writer(cells[post]) == ref[post]
    new, ref_new = cells.pop(bpk.NEW_CELLS_KEY), ref.pop(bpk.NEW_CELLS_KEY)
    assert new[:len(ref_new)] == ref_new and len(new) == len(ref_new) + 1
    assert {k: v for k, v in cells.items() if k != post} == {k: v for k, v in ref.items() if k != post}


def _build(name: str, out_dir: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, BUILDER, name, "--out-dir", out_dir, *args], capture_output=True,
                          text=True, cwd=str(ROOT))


def test_k2_vs_k6_off_notebooks_differ_only_by_the_patch_block():
    tmp_k2, tmp_off, tmp_on = "_pytest_oc_k2", "_pytest_oc_off", "_pytest_oc_on"
    try:
        r = _build("zz_oc_k2", tmp_k2, *K2_ARGS)
        assert r.returncode == 0, r.stderr
        r = _build("zz_oc_off", tmp_off, *K2_ARGS, "--patch", "overlapcons")
        assert r.returncode == 0, r.stderr
        r = _build("zz_oc_on", tmp_on, *K2_ARGS, "--patch", "overlapcons", "--set", "OVERLAPCONS_ENABLE=1")
        assert r.returncode == 0, r.stderr
        nbs = {}
        for tag, d, n in (("k2", tmp_k2, "zz-oc-k2"), ("off", tmp_off, "zz-oc-off"), ("on", tmp_on, "zz-oc-on")):
            nbs[tag] = json.loads((ROOT / "experiments" / d / f"{n}.ipynb").read_text(encoding="utf-8"))
        k2, off, on = nbs["k2"], nbs["off"], nbs["on"]
        assert k2["metadata"] == off["metadata"]
        ids_k2 = [c["id"] for c in k2["cells"]]
        extra = [c for c in off["cells"] if c["id"] not in ids_k2]
        assert len(extra) == 1 and "OVERLAP_REG_SRC = r'''" in extra[0]["source"]
        post_id = [c["id"] for c in k2["cells"] if "def write_test_submission(" in c["source"]]
        assert len(post_id) == 1
        by_id = {c["id"]: c for c in off["cells"]}
        # order: the new cell right before the post-processing cell
        assert [c["id"] for c in off["cells"]].index(extra[0]["id"]) + 1 == \
            [c["id"] for c in off["cells"]].index(post_id[0])
        for c in k2["cells"]:
            o = by_id[c["id"]]
            if c["id"] == post_id[0]:
                assert _undo_writer(o["source"]) == c["source"]
            elif c["source"] != o["source"]:  # cell 0: only the kernel name of the override block (no knob set)
                d = [ln for ln in o["source"].splitlines() if ln not in c["source"].splitlines()]
                assert d == ["# ---- zz_oc_off: probe overrides (tools/build_probe_kernel.py --base x138) ----"], d
                assert len(o["source"].splitlines()) == len(c["source"].splitlines())
            else:
                assert o == c
        diff_on = [(a["source"], b["source"]) for a, b in zip(off["cells"], on["cells"]) if a != b]
        assert len(diff_on) == 1
        assert 'os.environ["BIOHUB_OVERLAPCONS_ENABLE"] = "1"' in diff_on[0][1]
        probe = json.loads((ROOT / "experiments" / tmp_on / "probe.json").read_text(encoding="utf-8"))
        assert probe["change"]["PATCHES"] == "divinsert+lowrefine+overlapcons+safetail"
        assert probe["change"]["OVERLAPCONS_ENABLE"] == "1" and "lab" not in probe
    finally:
        for d in (tmp_k2, tmp_off, tmp_on):
            shutil.rmtree(ROOT / "experiments" / d, ignore_errors=True)


@pytest.mark.parametrize("args,msg", [
    (["--base", "x138", "--set", "OVERLAPCONS_ENABLE=1"], "need --patch overlapcons"),
    (["--patch", "overlapcons"], "needs --base x138"),
    (["--base", "x138", "--patch", "overlapcons", "--set", "OVERLAPCONS_ENABLE=2"], "must be 0 or 1"),
    (["--base", "x138", "--patch", "overlapcons", "--set", "OVERLAPCONS_FORCE_FAIL=1"], "needs --lab"),
    (["--base", "x138", "--patch", "overlapcons", "--set", "OVERLAPCONS_BUDGET_S=abc"], "must be a number"),
    (["--base", "x138", "--patch", "overlapcons", "--set", "OVERLAPCONS_WORKERS=0"], "integer 1..99"),
    (["--base", "x138", "--patch", "overlapcons", "--set", "OVERLAPCONS_FOO=1"], "unknown overlapcons knobs"),
])
def test_builder_refusals(args, msg):
    r = subprocess.run([sys.executable, BUILDER, "zz_oc_refusal", *args], capture_output=True, text=True,
                       cwd=str(ROOT))
    assert r.returncode != 0 and msg in r.stderr, (r.returncode, r.stderr[-400:])
    assert not (ROOT / "experiments" / "zz_oc_refusal").exists()


# ---------------------------------------------------------------------------------------------------------------------
# end to end: embedded cell + patched writer vs the unpatched writer, on synthetic overlapping videos
# ---------------------------------------------------------------------------------------------------------------------
REC = np.random.default_rng(7).integers(50, 4000, size=(14, 20, 70, 70), dtype=np.uint16)
OFF_B = (3, 2, 10, 12)  # e1_b = recording crop at (3, 2, 10, 12): offset = coord_a - coord_b


def _videos(overlap: bool = True) -> dict:
    a = np.ascontiguousarray(REC[0:10, 0:16, 0:48, 0:48])
    b = np.ascontiguousarray(REC[3:12, 2:18, 10:60, 12:64])
    if not overlap:
        b = np.random.default_rng(5).integers(50, 4000, size=b.shape, dtype=np.uint16)
    c = np.random.default_rng(99).integers(50, 4000, size=(10, 16, 48, 48), dtype=np.uint16)
    return {"e1_a": a, "e1_b": b, "e2_c": c}


def _graph(origin, tracks) -> tuple:
    """tracks: [(ts, z, y, x, skip_edge_into, moved {t: dy})] in GLOBAL coordinates -> (nodes, edges) in the crop."""
    nodes, edges, nid = {}, [], 1
    for ts, z, y, x, skip, moved in tracks:
        prev = None
        for t in ts:
            nodes[nid] = {"node_id": nid, "t": t - origin[0], "z": float(z - origin[1]),
                          "y": float(y + moved.get(t, 0.0) - origin[2]), "x": float(x - origin[3])}
            if prev is not None and t not in skip:
                edges.append({"source_id": prev, "target_id": nid, "edge_prob": 0.9})
            prev = nid
            nid += 1
    return nodes, edges


def _final_graphs() -> dict:
    """e1_a misses the global t 5->6 link and detects t=6 4 um off at global x 46 (0.4 um from A's x border, 6.9 um
    inside B); e1_b has the clean track; both carry an agreeing background track; e2_c is unrelated."""
    bg = (range(3, 10), 8, 20, 30, {}, {})
    ga = _graph((0, 0, 0, 0), [bg, (range(3, 10), 8, 30, 46, {6}, {6: 10.0}), (range(0, 10), 6, 5, 5, set(), {})])
    gb = _graph(OFF_B, [bg, (range(3, 10), 8, 30, 46, set(), {}), (range(3, 12), 10, 55, 60, set(), {})])
    gc = _graph((0, 0, 0, 0), [(range(0, 10), 8, 20, 20, set(), {})])
    return {"e1_a": ga, "e1_b": gb, "e2_c": gc}


class _Rows:
    def __init__(self, rows):
        self.rows = rows

    def iter_rows(self, named=True):
        return iter(self.rows)


class _Geff:
    def __init__(self, nodes, edges):
        self.nodes, self.edges = nodes, edges

    def node_attrs(self):
        return _Rows([{"node_id": i, **{k: n[k] for k in ("t", "z", "y", "x")}} for i, n in self.nodes.items()])

    def edge_attrs(self):
        return _Rows([dict(e) for e in self.edges])


def _writer_text(post: str) -> str:
    i0 = post.index("def write_test_submission(")
    i1 = post.index(NL + 'write_test_submission("base")')
    return post[i0:i1]


def _run_writer(tmp: Path, post: str, cell: str | None, env: dict, videos: dict, graphs: dict,
                start_offset_s: float = 0.0, hook=None) -> tuple[bytes, bytes, str, dict]:
    """Exec (the overlapcons cell and) the writer in one namespace with mocks; -> (csv, stats csv, log, namespace)."""
    import pandas as pd
    work = tmp / "work"
    shutil.rmtree(work, ignore_errors=True)
    (work / "repo" / "predictions" / "e" / "m" / "split_0").mkdir(parents=True)
    test_dir = work / "test"
    for name, arr in videos.items():
        (work / "repo" / "predictions" / "e" / "m" / "split_0" / f"{name}.geff").write_text("")
        (test_dir / f"{name}.zarr" / "0").mkdir(parents=True)
        (test_dir / f"{name}.zarr" / "0" / "zarr.json").write_text(json.dumps({"shape": list(arr.shape)}))
    log = []

    def _print(*a, **k):
        log.append(" ".join(str(x) for x in a))

    def _filter(nodes_by_id, edges, dataset=None, deepcenter_bundle=None):
        n, e = copy.deepcopy(graphs[dataset])
        return n, e, {"raw_edges": len(edges), "gap_added_nodes": 0}

    ns = {"os": os, "json": json, "np": np, "csv": csv, "pd": pd, "Path": Path, "print": _print,
          "display": lambda *a, **k: None, "_time": time, "_traceback": traceback,
          "TEST_DIR": test_dir, "REPO_DIR": work / "repo", "METHOD": "m", "test_stems": sorted(videos),
          "SUBMISSION_PATH": work / "submission.csv", "RUN_STATS_PATH": work / "run_stats.csv",
          "CSV_COLUMNS": ["id", "dataset", "row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"],
          "graph_from_geff": lambda p: _Geff(*graphs[Path(p).stem]),
          "filter_output_graph": _filter, "fallback_output_graph": None, "DEEPCENTER_VETO_DETECTOR": None,
          "KERNEL_START_TS": time.time() - start_offset_s, "REPAIR_DEADLINE_S": 1e9, "_deadline_degraded": False,
          "_deadline_degrade": None, "predict_seconds": 1.0, "EXPERIMENT_TAG": "t",
          "read_test_frame": lambda ds, t, cache: videos[ds][int(t)]}
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        if cell is not None:
            exec(compile(cell, "overlapcons_cell", "exec"), ns)
        if hook is not None:
            hook(ns)
        exec(compile(_writer_text(post), "writer", "exec"), ns)
        ns["write_test_submission"]("base")
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return (work / "submission.csv").read_bytes(), (work / "run_stats.csv").read_bytes(), NL.join(log), ns


@pytest.fixture(scope="module")
def sources():
    base_post = _base_cells()[bpk.BASES["x138"]["post"]]
    cells = _patched("overlapcons")
    return base_post, cells[bpk.BASES["x138"]["post"]], cells[bpk.NEW_CELLS_KEY][0][1]


@pytest.fixture(scope="module")
def reference(sources, tmp_path_factory):
    base_post, _, _ = sources
    tmp = tmp_path_factory.mktemp("ref")
    csv_ref, stats_ref, _, _ = _run_writer(tmp, base_post, None, {}, _videos(), _final_graphs())
    return csv_ref, stats_ref


def _rows(data: bytes) -> list[dict]:
    return list(csv.DictReader(data.decode("utf-8").splitlines()))


TIMING_COLUMNS = ("repair_seconds", "kernel_elapsed_seconds")


def _same_stats(a: bytes, b: bytes) -> bool:
    """run_stats.csv equal apart from the wall-clock columns."""
    ra = [{k: v for k, v in r.items() if k not in TIMING_COLUMNS} for r in _rows(a)]
    rb = [{k: v for k, v in r.items() if k not in TIMING_COLUMNS} for r in _rows(b)]
    return ra == rb and a.splitlines()[0] == b.splitlines()[0]


def test_disabled_is_byte_identical(sources, reference, tmp_path):
    _, post, cell = sources
    csv_ref, stats_ref = reference
    out, stats, log, _ = _run_writer(tmp_path, post, cell, {"BIOHUB_OVERLAPCONS_ENABLE": "0"}, _videos(),
                                     _final_graphs())
    assert out == csv_ref and _same_stats(stats, stats_ref)
    assert "OVERLAPCONS: enable=0" in log and "OVERLAPCONS registration" not in log


def test_no_accepted_pair_is_byte_identical(sources, reference, tmp_path):
    _, post, cell = sources
    out, stats, log, _ = _run_writer(tmp_path, post, cell, {"BIOHUB_OVERLAPCONS_ENABLE": "1"},
                                     _videos(overlap=False), _final_graphs())
    assert out == reference[0] and _same_stats(stats, reference[1])
    assert "accepted 0" in log and "OVERLAPCONS: no accepted pair" in log


def test_accepted_pair_is_spliced_end_to_end(sources, reference, tmp_path):
    _, post, cell = sources
    out, stats, log, ns = _run_writer(tmp_path, post, cell, {"BIOHUB_OVERLAPCONS_ENABLE": "1"}, _videos(),
                                      _final_graphs())
    assert "OVERLAPCONS accepted e1_a e1_b offset_tzyx_a_minus_b [3, 2, 10, 12]" in log
    assert "OVERLAPCONS pair e1_a e1_b" in log and "OVERLAPCONS DONE" in log and "spliced 1" in log
    ref = _rows(reference[0])
    got = _rows(out)
    # e1_b and e2_c rows unchanged; ids renumbered only because e1_a comes first and keeps its row count
    strip = [{k: v for k, v in r.items() if k != "id"} for r in got]
    strip_ref = [{k: v for k, v in r.items() if k != "id"} for r in ref]
    assert [r for r in strip if r["dataset"] != "e1_a"] == [r for r in strip_ref if r["dataset"] != "e1_a"]
    assert [int(r["id"]) for r in got] == list(range(len(got)))
    a_nodes = {int(r["node_id"]): r for r in got if r["dataset"] == "e1_a" and r["row_type"] == "node"}
    a_edges = {(int(r["source_id"]), int(r["target_id"])) for r in got if r["dataset"] == "e1_a" and r["row_type"] == "edge"}
    ref_nodes = {int(r["node_id"]) for r in ref if r["dataset"] == "e1_a" and r["row_type"] == "node"}
    assert len(a_nodes) == len(ref_nodes)  # 3 nodes replaced by 3 imported ones
    new_ids = set(a_nodes) - ref_nodes
    assert len(new_ids) == 3 and min(new_ids) > max(ref_nodes)
    # the damaged track (global y 30, x 46 -> A voxels) is now one continuous chain over global t 3..9
    track = {int(r["t"]): i for i, r in a_nodes.items() if (int(r["y"]), int(r["x"])) == (30, 46)}
    assert sorted(track) == list(range(3, 10))
    assert all((track[t], track[t + 1]) in a_edges for t in range(3, 9))
    assert all(e[0] in a_nodes and e[1] in a_nodes for e in a_edges)
    assert len(_rows(stats)) == 3


@pytest.mark.parametrize("env,offset_s,line", [
    ({"BIOHUB_OVERLAPCONS_ENABLE": "1", "BIOHUB_OVERLAPCONS_FORCE_FAIL": "1"}, 0.0, "OVERLAPCONS FAILED"),
    ({"BIOHUB_OVERLAPCONS_ENABLE": "1"}, 40000.0, "OVERLAPCONS SKIPPED (budget)"),
    ({"BIOHUB_OVERLAPCONS_ENABLE": "1", "BIOHUB_OVERLAPCONS_MAX_S": "0"}, 0.0, "OVERLAPCONS SKIPPED (time)"),
])
def test_fail_soft_paths_keep_the_csv(sources, reference, tmp_path, env, offset_s, line):
    _, post, cell = sources
    out, stats, log, _ = _run_writer(tmp_path, post, cell, env, _videos(), _final_graphs(), start_offset_s=offset_s)
    assert out == reference[0] and _same_stats(stats, reference[1])
    assert line in log


@pytest.mark.parametrize("mode", ["raise", "dangling"])
def test_splice_exception_or_bad_result_falls_back(sources, reference, tmp_path, mode):
    """splice_all raising, or returning a graph that fails overlapcons_check -> 'OVERLAPCONS FAILED', CSV unchanged."""
    _, post, cell = sources

    def hook(ns):
        orig = ns["_OC_SPLICE"].splice_all

        def broken(graphs, shapes, pairs, cfg=None, log=None):
            if mode == "raise":
                raise ValueError("synthetic splice failure")
            out, st = orig(graphs, shapes, pairs, cfg, log)
            nodes, edges = out["e1_a"]
            out["e1_a"] = (nodes, edges + [{"source_id": 10 ** 6, "target_id": min(nodes)}])
            return out, st
        ns["_OC_SPLICE"].splice_all = broken

    out, stats, log, _ = _run_writer(tmp_path, post, cell, {"BIOHUB_OVERLAPCONS_ENABLE": "1"}, _videos(),
                                     _final_graphs(), hook=hook)
    assert out == reference[0] and _same_stats(stats, reference[1])
    assert "OVERLAPCONS FAILED" in log and ("synthetic splice failure" in log or "dangling edge" in log)


def test_overlapcons_video_reads_zarr_json(sources, tmp_path):
    _, post, cell = sources
    _, _, _, ns = _run_writer(tmp_path, post, cell, {"BIOHUB_OVERLAPCONS_ENABLE": "0"}, _videos(), _final_graphs())
    read, shape = ns["overlapcons_video"]("e1_b")
    assert shape == (9, 16, 50, 52) and np.array_equal(read(4), _videos()["e1_b"][4])
