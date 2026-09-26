"""Ideas workflow v3 E1: --patch safetail on --base x138 (tools/build_probe_kernel.py; spec in
research/wf_ideas_v3/TASK_CLOUD_SESSION.md T1).

    python -m pytest tests/test_safetail.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.build_probe_kernel as bpk  # noqa: E402

BUILDER = str(ROOT / "tools" / "build_probe_kernel.py")
NL = "\n"


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


def _undo_safetail(post: str) -> str:
    post = post.replace(bpk.safetail_divins_call(), bpk.DIVINS_CALL)
    post = post.replace(bpk.SAFETAIL_DEGRADE_NEW, bpk.SAFETAIL_DEGRADE_OLD)
    return post.replace(bpk.SAFETAIL_GATE + NL + NL + "def fallback_output_graph(", NL * 3 + "def fallback_output_graph(")


def test_only_intended_changes():
    # with and without divinsert, safetail changes exactly the gate block, _deadline_degrade and the insertion call
    assert _undo_safetail(_post(_patched("safetail"))) == _post(_patched())
    with_div = _post(_patched("divinsert", "safetail"))
    assert _undo_safetail(with_div) == _post(_patched("divinsert"))
    assert with_div.count(" and safetail_divins_allowed(dataset, stats):") == 1
    assert "DIVINS FAILED" in with_div and "DIVINS SKIPPED (deadline)" in with_div
    assert "DIVINS FAILED" not in _post(_patched("safetail"))


def test_patched_cells_compile():
    for names in (("safetail",), ("divinsert", "safetail"), ("divinsert", "leafprune", "safetail")):
        cells = _patched(*names)
        compile(_post(cells), f"post[{'+'.join(names)}]", "exec")
        for _, src in cells.get(bpk.NEW_CELLS_KEY, []):
            compile(src, "new_cell", "exec")


def _gate_ns(start_ago: float, degraded: bool) -> dict:
    ns = {"os": os, "_time": time, "KERNEL_START_TS": time.time() - start_ago, "REPAIR_DEADLINE_S": 34200.0,
          "_deadline_degraded": degraded}
    exec(bpk.SAFETAIL_GATE, ns)
    return ns


def test_gate(monkeypatch, capsys):
    monkeypatch.setenv("BIOHUB_DIVINS_DEADLINE_S", "100")
    stats = {}
    assert _gate_ns(0, False)["safetail_divins_allowed"]("d", stats) is True and stats == {}
    assert _gate_ns(200, False)["safetail_divins_allowed"]("d", stats) is False
    assert stats == {"divins_skipped_deadline": 1}
    stats = {}
    assert _gate_ns(0, True)["safetail_divins_allowed"]("d", stats) is False and stats["divins_skipped_deadline"] == 1
    assert "DIVINS SKIPPED (deadline)" in capsys.readouterr().out


def _call_fn(**ns_extra):
    src = "def _f(dataset, edges, nodes_by_id, stats):" + NL + bpk.safetail_divins_call() + "    return edges, stats" + NL
    ns = {"BIOHUB_DIVINS_ENABLE": "1", "safetail_divins_allowed": lambda d, s: True,
          "SAFETAIL_DIVINS_FORCE_FAIL": False, "DIVINS_BUNDLE": {"prepared_frames": {1: 2}}, "time": time,
          "DIVINS_PARAMS": {}, "DIVINS_DUMP": False, "DIVINS_BATCH": 8, "repair_frame_cache": {}}
    ns.update(ns_extra)
    exec(src, ns)
    return ns["_f"], ns


def test_insertion_fail_soft(capsys):
    edges_in = [{"source_id": 1, "target_id": 2}]
    nodes = {1: {}, 2: {}}
    f, ns = _call_fn(SAFETAIL_DIVINS_FORCE_FAIL=True)
    edges, stats = f("d", edges_in, nodes, {})
    assert edges is edges_in and stats["divins_failed"] == 1 and ns["DIVINS_BUNDLE"]["prepared_frames"] == {}

    def boom(*_):
        raise ValueError("x")
    f, _ = _call_fn(candidate_triples=boom)
    edges, stats = f("d", edges_in, nodes, {})
    assert edges is edges_in and stats["divins_failed"] == 1
    assert "DIVINS FAILED (ValueError: x)" in capsys.readouterr().out


def test_insertion_gate_skips_and_success_path():
    edges_in = [{"source_id": 1, "target_id": 2}]
    nodes = {1: {}, 2: {}}
    f, _ = _call_fn(safetail_divins_allowed=lambda d, s: False, candidate_triples=None)
    edges, stats = f("d", edges_in, nodes, {})
    assert edges is edges_in and stats == {}

    import numpy as np
    new_edges = edges_in + [{"source_id": 1, "target_id": 3}]
    ins_stats = {k: 0 for k in ("divins_triples", "divins_triples_orphan", "divins_triples_steal", "divins_eligible",
                                "divins_added_orphan", "divins_added_steal")}
    ins_stats["divins_added"] = 1
    f, _ = _call_fn(np=np, candidate_triples=lambda *a: [], insert_divisions=lambda *a: (new_edges, dict(ins_stats)))
    edges, stats = f("d", edges_in, nodes, {})
    assert edges is new_edges and stats["divins_added"] == 1 and "divins_failed" not in stats


def _degrade_fn(post: str) -> str:
    start = post.index("def _deadline_degrade()")
    return post[start:post.index(NL * 3, start)]


def test_degrade_keep_div(monkeypatch):
    src = _degrade_fn(_post(_patched("safetail")))
    for keep, expect in (("1", True), ("0", False)):
        monkeypatch.setenv("BIOHUB_DEGRADE_KEEP_DIV", keep)
        ns = {"os": os, "_time": time, "KERNEL_START_TS": time.time(), "REPAIR_DEADLINE_S": 1.0,
              "_deadline_degraded": False}
        ns.update({k: True for k in ("OUTPUT_MOTION_RELINK", "OUTPUT_GAP_CLOSE", "OUTPUT_GAP2_RECOVERY",
                                     "OUTPUT_SAFE_DIVISIONS", "OUTPUT_LINEFIT_SMOOTH")})
        exec(src, ns)
        ns["_deadline_degrade"]()
        assert ns["_deadline_degraded"] is True
        assert not (ns["OUTPUT_MOTION_RELINK"] or ns["OUTPUT_GAP_CLOSE"] or ns["OUTPUT_GAP2_RECOVERY"])
        assert ns["OUTPUT_SAFE_DIVISIONS"] is expect and ns["OUTPUT_LINEFIT_SMOOTH"] is expect


def _run(*args):
    return subprocess.run([sys.executable, BUILDER, "zz-safetail-refusal", *args], capture_output=True, text=True,
                          cwd=ROOT)


def test_builder_refusals():
    cases = [
        (["--base", "x138", "--patch", "safetail"], "needs --set REPAIR_DEADLINE_S=34200"),
        (["--patch", "safetail", "--set", "REPAIR_DEADLINE_S=34200"], "needs --base x138"),
        (["--base", "x138", "--patch", "safetail", "--set", "REPAIR_DEADLINE_S=1"], "need --lab"),
        (["--base", "x138", "--patch", "divinsert", "--patch", "safetail", "--set", "REPAIR_DEADLINE_S=34200",
          "--set", "DIVINS_DUMP=1"], "--lab builds only"),
        (["--base", "x138", "--patch", "divinsert", "--set", "DIVINS_FORCE_FAIL=1"], "needs --patch safetail"),
        (["--base", "x138", "--patch", "divinsert", "--patch", "safetail", "--set", "REPAIR_DEADLINE_S=34200",
          "--set", "DIVINS_FORCE_FAIL=1"], "needs --lab"),
    ]
    for args, msg in cases:
        r = _run(*args)
        assert r.returncode != 0 and msg in r.stderr, (args, r.stderr[-300:])
    assert not (ROOT / "experiments" / "zz-safetail-refusal").exists()


def test_builder_deadline_pairs_refused():
    # non-lab safetail builds accept exactly (34200, 28800 default) or (37800, 32400) (CONTEXT 26 Sep v3 V3, R5-A4)
    ins = ["--base", "x138", "--patch", "divinsert", "--patch", "safetail", "--set", "DIVINS_ENABLE=1"]
    noins = ["--base", "x138", "--patch", "safetail"]
    cases = [
        (ins + ["--set", "REPAIR_DEADLINE_S=34200", "--set", "DIVINS_DEADLINE_S=32400"], "got (34200, 32400)"),  # DIVINS alone
        (ins + ["--set", "REPAIR_DEADLINE_S=34200", "--set", "DIVINS_DEADLINE_S=36000"], "got (34200, 36000)"),
        (ins + ["--set", "REPAIR_DEADLINE_S=37800"], "got (37800, 28800 default)"),                         # REPAIR alone
        (noins + ["--set", "REPAIR_DEADLINE_S=37800"], "got (37800, 28800 default)"),
        (ins + ["--set", "REPAIR_DEADLINE_S=37800", "--set", "DIVINS_DEADLINE_S=28800"], "got (37800, 28800)"),
        (ins + ["--set", "REPAIR_DEADLINE_S=37800", "--set", "DIVINS_DEADLINE_S=36000"], "got (37800, 36000)"),
        (ins + ["--set", "REPAIR_DEADLINE_S=41400", "--set", "DIVINS_DEADLINE_S=32400"], "got (41400, 32400)"),
        (ins + ["--set", "REPAIR_DEADLINE_S=27000", "--set", "DIVINS_DEADLINE_S=28800"], "got (27000, 28800)"),
    ]
    for args, msg in cases:
        r = _run(*args)
        assert r.returncode != 0 and msg in r.stderr, (args, r.stderr[-300:])
        assert "never DIVINS_DEADLINE_S alone" in r.stderr and "need --lab" in r.stderr
    assert not (ROOT / "experiments" / "zz-safetail-refusal").exists()


def _build(name: str, out_dir: str, *args: str) -> Path:
    r = subprocess.run([sys.executable, BUILDER, name, "--out-dir", out_dir, *args], capture_output=True, text=True,
                       cwd=ROOT)
    assert r.returncode == 0, r.stderr[-500:]
    return ROOT / "experiments" / out_dir


def _code_cells(nb_path: Path) -> list:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


# the documented branch-A K2 line (CONTEXT 25 Sep, BUILD COMMANDS FOR 26.09) and the committed K2 notebook (#37)
K2_KNOBS = ["--set", "DIVINS_ENABLE=1", "--set", "DIVINS_STEAL=1", "--set", "DIVINS_CAP=4", "--set", "DIVINS_FRAME_CAP=1",
            "--set", "DIVINS_ALPHA=1", "--set", "DIVINS_THRESH=0.4", "--set", "DIVINS_DUMP=0"]
K2_PATCHES = ["--base", "x138", "--patch", "divinsert", "--patch", "safetail", "--patch", "lowrefine"]
K2_NB = ROOT / "experiments" / "exp58_x138_safe_lowref" / "exp58-x138-safe-lowref.ipynb"
K2_SHA = "1f1ddb6d63b47f540ad614232e821ad215f27fce0d901cdbb9f67a8beeb67855"


def test_build_k2pp_pair_and_k2_sha_unchanged():
    tmp = "zz-safetail-k2pp-test"
    try:
        k2 = _build("exp58_x138_safe_lowref", f"{tmp}/k2", *K2_PATCHES, *K2_KNOBS, "--set", "REPAIR_DEADLINE_S=34200",
                    "--set", "DIVINS_DEADLINE_S=28800", "--set", "LOWREFINE_ENABLE=1",
                    "--note", "K2: x138 + safetail + lowrefine + divinsert (#35 config)")
        k2_nb = k2 / "exp58-x138-safe-lowref.ipynb"
        assert hashlib.sha256(k2_nb.read_bytes()).hexdigest() == K2_SHA          # the builder change is inert for K2
        if K2_NB.exists():
            assert k2_nb.read_bytes() == K2_NB.read_bytes()
        k2pp = _build("exp58d_x138_safe_lowref", f"{tmp}/k2pp", *K2_PATCHES, *K2_KNOBS, "--set",
                      "REPAIR_DEADLINE_S=37800", "--set", "DIVINS_DEADLINE_S=32400", "--set", "LOWREFINE_ENABLE=1",
                      "--note", "K2'': K2 with both deadlines moved")
        a, b = _code_cells(k2_nb), _code_cells(k2pp / "exp58d-x138-safe-lowref.ipynb")
        assert len(a) == len(b) and a[1:] == b[1:]                                 # only cell 0 differs
        la, lb = a[0].splitlines(), b[0].splitlines()
        diff = [(x, y) for x, y in zip(la, lb) if x != y]
        assert len(la) == len(lb) and diff == [
            ("# ---- exp58_x138_safe_lowref: probe overrides (tools/build_probe_kernel.py --base x138) ----",
             "# ---- exp58d_x138_safe_lowref: probe overrides (tools/build_probe_kernel.py --base x138) ----"),
            ('os.environ["BIOHUB_REPAIR_DEADLINE_S"] = "34200"', 'os.environ["BIOHUB_REPAIR_DEADLINE_S"] = "37800"'),
            ('os.environ["BIOHUB_DIVINS_DEADLINE_S"] = "28800"', 'os.environ["BIOHUB_DIVINS_DEADLINE_S"] = "32400"'),
        ], diff
        probe = json.loads((k2pp / "probe.json").read_text(encoding="utf-8"))
        assert "lab" not in probe
        assert probe["change"]["REPAIR_DEADLINE_S"] == "37800" and probe["change"]["DIVINS_DEADLINE_S"] == "32400"
        assert probe["change"]["PATCHES"] == "divinsert+lowrefine+safetail"
    finally:
        shutil.rmtree(ROOT / "experiments" / tmp, ignore_errors=True)


def test_lab_build_keeps_any_deadline_pair():
    # --lab rules unchanged: a DIVINS-only move (refused above without --lab) builds, marked as a lab build
    tmp = "zz-safetail-lab-pair-test"
    try:
        out = _build("zz-safetail-lab-pair", tmp, "--base", "x138", "--patch", "divinsert", "--patch", "safetail",
                     "--lab", "--set", "DIVINS_ENABLE=1", "--set", "REPAIR_DEADLINE_S=34200",
                     "--set", "DIVINS_DEADLINE_S=32400")
        probe = json.loads((out / "probe.json").read_text(encoding="utf-8"))
        assert "lab" in probe and probe["change"]["DIVINS_DEADLINE_S"] == "32400"
    finally:
        shutil.rmtree(ROOT / "experiments" / tmp, ignore_errors=True)


def test_build_k1_like():
    name = "zz-safetail-build-test"
    out = ROOT / "experiments" / name
    try:
        r = subprocess.run([sys.executable, BUILDER, name, "--base", "x138", "--patch", "safetail", "--patch",
                            "divinsert", "--set", "REPAIR_DEADLINE_S=34200", "--set", "DIVINS_ENABLE=1"],
                           capture_output=True, text=True, cwd=ROOT)
        assert r.returncode == 0, r.stderr[-500:]
        nb = json.loads(next(out.glob("*.ipynb")).read_text(encoding="utf-8"))
        code = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
        assert 'os.environ["BIOHUB_REPAIR_DEADLINE_S"] = "34200"' in code[0]
        assert 'os.environ["BIOHUB_DEGRADE_KEEP_DIV"] = "1"' in code[0]
        post = [s for s in code if "def filter_output_graph(" in s]
        assert len(post) == 1 and bpk.safetail_divins_call() in post[0]  # safetail applied after divinsert
        probe = json.loads((out / "probe.json").read_text(encoding="utf-8"))
        assert "lab" not in probe and probe["change"]["PATCHES"] == "divinsert+safetail"
    finally:
        shutil.rmtree(out, ignore_errors=True)
