"""Ideas workflow v3 E3 = C04: --patch forkmid on --base x138 (tools/build_probe_kernel.py; spec in
research/wf_ideas_v3/TASK_CLOUD_SESSION.md T6).

    python -m pytest tests/test_forkmid.py
"""
import copy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.build_probe_kernel as bpk  # noqa: E402

BUILDER = str(ROOT / "tools" / "build_probe_kernel.py")
NL = "\n"
SCALE = (1.625, 0.40625, 0.40625)


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


def _undo_forkmid(post: str) -> str:
    post = post.replace(NL + bpk.FORKMID_FN + bpk._FM_FILTER_DEF, bpk._FM_FILTER_DEF)
    return post.replace(bpk.FORKMID_CALL + bpk._FM_FINAL_PRINT, bpk._FM_FINAL_PRINT)


def _ns(enable="1", min_um=None, force_fail="0") -> dict:
    env = {"BIOHUB_FORKMID_ENABLE": enable, "BIOHUB_FORKMID_FORCE_FAIL": force_fail}
    if min_um is not None:
        env["BIOHUB_FORKMID_MIN_UM"] = str(min_um)
    old = {k: os.environ.get(k) for k in (*env, "BIOHUB_FORKMID_MIN_UM")}
    os.environ.update(env)
    try:
        ns = {"os": os, "np": np, "VOXEL_SCALE_UM": SCALE}
        exec(bpk.FORKMID_FN, ns)
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return ns


def _node(i, t, z, y, x):
    return {"node_id": i, "t": t, "z": float(z), "y": float(y), "x": float(x)}


def _um(z_um, y_um, x_um):  # micrometres -> voxel coordinates
    return z_um / SCALE[0], y_um / SCALE[1], x_um / SCALE[2]


def _graph():
    """Four forks + a plain track. P at the origin (t=0); sisters at t=1.
    fork A (parent 1): sisters at +-5 um in x -> midpoint 0 um from P: kept.
    fork B (parent 2): both sisters shifted 6 um in y, ILP edge scored (0.8) -> the added edge goes.
    fork C (parent 3): both sisters shifted 6 um in y, ILP edge unscored (edge_prob 0.0) -> the ILP edge goes.
    fork D (parent 4): far, but the extra child is div_inserted (DaughterNet) -> untouched.
    fork E (parent 5): far, ILP edge a gap edge (edge_prob None) -> the added edge goes.
    track (parent 6): one child, no fork."""
    nodes, edges = {}, []
    specs = {1: (0.0, 5.0, 0.8, "safe"), 2: (6.0, 5.0, 0.8, "safe"), 3: (6.0, 5.0, 0.0, "safe"),
             4: (6.0, 5.0, 0.0, "divins"), 5: (6.0, 5.0, None, "safe")}
    nid = 100
    for p, (dy, dx, prob, kind) in specs.items():
        base_x = 100.0 * p
        nodes[p] = _node(p, 0, *_um(10.0, 10.0, base_x))
        c1, c2 = nid, nid + 1
        nid += 2
        nodes[c1] = _node(c1, 1, *_um(10.0, 10.0 + dy, base_x - dx))
        nodes[c2] = _node(c2, 1, *_um(10.0, 10.0 + dy, base_x + dx))
        edges.append({"source_id": p, "target_id": c1, "edge_prob": prob, "distance_um": 1.0})
        extra = {"source_id": p, "target_id": c2, "edge_prob": None, "distance_um": 1.0}
        extra.update({"safe_division": 1} if kind == "safe" else {"div_inserted": 1, "div_steal_from": -1})
        edges.append(extra)
    nodes[6] = _node(6, 0, 1, 1, 1)
    nodes[7] = _node(7, 1, 1, 1, 2)
    edges.append({"source_id": 6, "target_id": 7, "edge_prob": 0.9, "distance_um": 0.4})
    return nodes, edges


def test_synthetic_forks():
    ns = _ns()
    nodes, edges = _graph()
    nodes0, edges0 = copy.deepcopy(nodes), copy.deepcopy(edges)
    kept, counters, removed = ns["forkmid_edges"](nodes, edges, 4.5)
    assert nodes == nodes0 and edges == edges0  # inputs untouched
    pairs = {(e["source_id"], e["target_id"]) for e in kept}
    assert (1, 100) in pairs and (1, 101) in pairs  # fork A kept (midpoint 0 um)
    assert (2, 102) in pairs and (2, 103) not in pairs  # B: added edge dropped
    assert (3, 104) not in pairs and (3, 105) in pairs  # C: unscored ILP edge dropped
    assert (4, 106) in pairs and (4, 107) in pairs  # D: DaughterNet fork untouched
    assert (5, 108) in pairs and (5, 109) not in pairs  # E: gap ILP edge (None) -> added edge dropped
    assert (6, 7) in pairs
    assert len(kept) == len(edges) - 3
    assert counters == {"forkmid_forks_seen": 4, "forkmid_removed": 3, "forkmid_removed_ilp_edge": 1,
                        "forkmid_removed_added_edge": 2, "forkmid_skipped": 0}
    assert [r[:2] for r in removed] == [(2, 103), (3, 104), (5, 109)]
    assert all(abs(r[2] - 6.0) < 1e-6 for r in removed) and [r[3] for r in removed] == ["added", "ilp", "added"]


def test_threshold_edge_and_skips():
    ns = _ns()
    nodes, edges = _graph()
    # threshold is inclusive (>= min_um): midpoint exactly 6 um
    kept, counters, _ = ns["forkmid_edges"](nodes, edges, 6.0)
    assert counters["forkmid_removed"] == 3
    kept, counters, _ = ns["forkmid_edges"](nodes, edges, 6.001)
    assert counters["forkmid_removed"] == 0 and kept is edges
    # a safe-division edge whose parent has lost its ILP child (out-degree 1) or has 3 children: skipped, untouched
    nodes, edges = _graph()
    edges = [e for e in edges if (e["source_id"], e["target_id"]) != (2, 102)]
    nodes[99] = _node(99, 1, *_um(10.0, 40.0, 300.0))
    edges.append({"source_id": 3, "target_id": 99, "edge_prob": 0.5})
    kept, counters, _ = ns["forkmid_edges"](nodes, edges, 4.5)
    assert counters["forkmid_skipped"] == 2 and counters["forkmid_removed"] == 1  # only E (parent 5) goes
    assert {(e["source_id"], e["target_id"]) for e in edges} - {(e["source_id"], e["target_id"]) for e in kept} == {(5, 109)}


def test_node_count_unchanged_via_call_block():
    """The guarded call as it sits in filter_output_graph: nodes_by_id is never reassigned or mutated."""
    ns = _ns()
    src = "def _f(dataset, edges, nodes_by_id, stats):" + NL + bpk.FORKMID_CALL + "    return nodes_by_id, edges, stats" + NL
    exec(src, ns)
    nodes, edges = _graph()
    nodes0 = copy.deepcopy(nodes)
    out_nodes, out_edges, stats = ns["_f"]("d", edges, nodes, {})
    assert out_nodes is nodes and nodes == nodes0 and len(out_nodes) == len(nodes0)
    assert len(out_edges) == len(edges) - 3 and stats["forkmid_removed"] == 3 and "forkmid_failed" not in stats
    # every kept edge still joins existing nodes; no parent keeps more than two children
    assert all(e["source_id"] in out_nodes and e["target_id"] in out_nodes for e in out_edges)


def test_enable0_identity():
    ns = _ns(enable="0")
    assert ns["FORKMID_ENABLE"] is False
    src = "def _f(dataset, edges, nodes_by_id, stats):" + NL + bpk.FORKMID_CALL + "    return nodes_by_id, edges, stats" + NL
    ns["forkmid_final_graph"] = None  # would raise if called
    exec(src, ns)
    nodes, edges = _graph()
    out_nodes, out_edges, stats = ns["_f"]("d", edges, nodes, {})
    assert out_nodes is nodes and out_edges is edges and stats == {}


def test_fail_soft(capsys):
    ns = _ns(force_fail="1")
    nodes, edges = _graph()
    stats = {}
    assert ns["forkmid_final_graph"](nodes, edges, stats, "d") is edges and stats == {"forkmid_failed": 1}
    ns = _ns()
    stats = {}
    nodes, edges = _graph()
    nodes[102] = {"t": 1}  # a node without coordinates -> KeyError inside forkmid_edges
    assert ns["forkmid_final_graph"](nodes, edges, stats, "d") is edges and stats["forkmid_failed"] == 1
    out = capsys.readouterr().out
    assert "FORKMID FAILED (RuntimeError" in out and "FORKMID FAILED (KeyError" in out
    stats = {}
    kept = _ns()["forkmid_final_graph"](*_graph(), stats, "d")
    assert len(kept) == 8 and stats["forkmid_removed"] == 3 and "forkmid: forks=4 removed=3" in capsys.readouterr().out


def test_only_intended_changes_and_last_edit():
    base = _post(_patched())
    assert _undo_forkmid(_post(_patched("forkmid"))) == base
    for combo in (("divinsert", "forkmid", "safetail"), ("forkmid", "divinsert", "safetail"),
                  ("divinsert", "leafprune", "forkmid", "safetail")):
        post = _post(_patched(*combo))
        others = tuple(n for n in combo if n != "forkmid")
        assert _undo_forkmid(post) == _post(_patched(*others)), combo
        assert post.count("forkmid_final_graph(nodes_by_id, edges, stats, dataset)") == 1
        # the call is the last graph edit: after linefit and after the (safetail-wrapped) insertion, before FINAL
        i_lf = post.index("    nodes_by_id = linefit_smooth_output_graph(nodes_by_id, edges, stats)" + NL)
        i_dv = post.index("    # ---- /divinsert ----" + NL)
        i_fm = post.index(bpk.FORKMID_CALL)
        assert i_lf < i_dv < i_fm and post[i_fm + len(bpk.FORKMID_CALL):].startswith(bpk._FM_FINAL_PRINT)
        assert bpk.safetail_divins_call() in post


def test_patched_cells_compile():
    for names in (("forkmid",), ("divinsert", "forkmid", "safetail"), ("divinsert", "leafprune", "forkmid", "safetail"),
                  ("forkmid", "divinsert", "leafprune", "safetail")):
        cells = _patched(*names)
        for k, src in cells.items():
            if k != bpk.NEW_CELLS_KEY:
                compile(src, f"cell{k}[{'+'.join(names)}]", "exec")
        for _, src in cells.get(bpk.NEW_CELLS_KEY, []):
            compile(src, "new_cell", "exec")


def test_anchor_strict():
    post = _post(_patched())
    try:
        bpk.forkmid_postproc_source(post + bpk._FM_FINAL_PRINT)
    except AssertionError as e:
        assert "anchor count 2" in str(e)
    else:
        raise AssertionError("duplicate anchor accepted")
    try:
        bpk.forkmid_postproc_source(post.replace(bpk._FM_FINAL_PRINT, ""))
    except AssertionError as e:
        assert "anchor count 0" in str(e)
    else:
        raise AssertionError("missing anchor accepted")


def _run(name, *args):
    return subprocess.run([sys.executable, BUILDER, name, *args], capture_output=True, text=True, cwd=ROOT)


def test_builder_refusals():
    cases = [
        (["--patch", "forkmid"], "needs --base x138"),
        (["--base", "x138", "--set", "FORKMID_ENABLE=1"], "need --patch forkmid"),
        (["--base", "x138", "--patch", "forkmid", "--set", "FORKMID_ENABLE=2"], "must be 0 or 1"),
        (["--base", "x138", "--patch", "forkmid", "--set", "FORKMID_MIN_UM=nan"], "finite and > 0"),
        (["--base", "x138", "--patch", "forkmid", "--set", "FORKMID_MIN_UM=0"], "finite and > 0"),
        (["--base", "x138", "--patch", "forkmid", "--set", "FORKMID_FORCE_FAIL=1"], "needs --lab"),
        (["--base", "x138", "--patch", "forkmid", "--set", "FORKMID_COS=1"], "unknown forkmid knobs"),
    ]
    for args, msg in cases:
        r = _run("zz-forkmid-refusal", *args)
        assert r.returncode != 0 and msg in r.stderr, (args, r.stderr[-300:])
    assert not (ROOT / "experiments" / "zz-forkmid-refusal").exists()


def test_build_k3_like_and_disabled_build():
    name = "zz-forkmid-build-test"
    out = ROOT / "experiments" / name
    try:
        # patch order on the command line does not matter: forkmid goes after divinsert, safetail stays last
        r = _run(name, "--base", "x138", "--patch", "forkmid", "--patch", "safetail", "--patch", "divinsert",
                 "--set", "REPAIR_DEADLINE_S=34200", "--set", "DIVINS_ENABLE=1", "--set", "FORKMID_ENABLE=1")
        assert r.returncode == 0, r.stderr[-500:]
        nb = json.loads(next(out.glob("*.ipynb")).read_text(encoding="utf-8"))
        code = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
        assert 'os.environ["BIOHUB_FORKMID_ENABLE"] = "1"' in code[0]
        post = [s for s in code if "def filter_output_graph(" in s]
        assert len(post) == 1 and bpk.FORKMID_CALL + bpk._FM_FINAL_PRINT in post[0]
        assert bpk.safetail_divins_call() in post[0]
        for i, s in enumerate(code):
            compile(s, f"cell{i}", "exec")
        probe = json.loads((out / "probe.json").read_text(encoding="utf-8"))
        assert "lab" not in probe and probe["change"]["PATCHES"] == "divinsert+forkmid+safetail"
        shutil.rmtree(out)
        # ENABLE=0 (default): the cell text changes but the run is the base's (the call is guarded); NOTE printed
        r = _run(name, "--base", "x138", "--patch", "forkmid")
        assert r.returncode == 0 and "exact no-op" in r.stdout, r.stderr[-500:]
        nb = json.loads(next(out.glob("*.ipynb")).read_text(encoding="utf-8"))
        post = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code" and "def filter_output_graph("
                in "".join(c["source"])][0]
        assert _undo_forkmid(post) == _post(_patched())
    finally:
        shutil.rmtree(out, ignore_errors=True)


def test_x138_unpatched_still_verbatim():
    name = "zz-forkmid-verbatim-test"
    out = ROOT / "experiments" / name
    try:
        r = _run(name, "--base", "x138")
        assert r.returncode == 0, r.stderr[-500:]
        assert next(out.glob("*.ipynb")).read_bytes() == bpk.BASES["x138"]["nb"].read_bytes()
    finally:
        shutil.rmtree(out, ignore_errors=True)


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
