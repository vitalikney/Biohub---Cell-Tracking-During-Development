"""Plan L4: --patch leafprune (tools/build_probe_kernel.py) = prune_weak_leaf_nodes from the public notebook
seyitkaangunes/biohub-035-deconfounded-edge-stack, also applied by the replay lab (experiments/l2_daughternet/replay).

    python tests/test_leafprune.py      (or pytest tests/test_leafprune.py)
"""
import difflib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.build_probe_kernel as bpk  # noqa: E402


def _base_code_cells() -> list[str]:
    nb = json.loads(bpk.BASE_NB.read_text(encoding="utf-8"))
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def _pure_insertion(old: str, new: str) -> int:
    """Number of inserted lines; fails if any base line is removed or replaced."""
    ops = difflib.SequenceMatcher(a=old.splitlines(), b=new.splitlines(), autojunk=False).get_opcodes()
    assert all(op in ("equal", "insert") for op, *_ in ops), [o for o in ops if o[0] != "equal"]
    return sum(j2 - j1 for op, _, _, j1, j2 in ops if op == "insert")


def test_patch_only_inserts_lines():
    code = _base_code_cells()
    cells = {k: s for k, s in enumerate(code)}
    bpk.patch_leafprune(cells)
    assert _pure_insertion(code[2], cells[2]) == 4  # blank + comment + knob, CONFIG_DISPLAY entry
    assert _pure_insertion(code[7], cells[7]) == 59 + 2 + 5  # function (+2 blank lines), counters, guarded call
    c7 = cells[7]
    # position: after short-track filtering, before linefit (the 035 notebook's order)
    assert c7.index("filter_short_track_components(nodes_by_id, edges, stats)") < c7.index(
        "prune_weak_leaf_nodes(nodes_by_id, edges, stats)") < c7.index(
        "nodes_by_id = linefit_smooth_output_graph(nodes_by_id, edges, stats)")
    for s in cells.values():
        compile(s, "cell", "exec")


def test_patch_order_with_divinsert():
    code = _base_code_cells()
    a = {k: s for k, s in enumerate(code)}
    b = dict(a)
    bpk.patch_divinsert(a)
    bpk.patch_leafprune(a)
    bpk.patch_leafprune(b)
    bpk.patch_divinsert(b)
    assert {k: v for k, v in a.items() if k != bpk.NEW_CELLS_KEY} == {k: v for k, v in b.items() if k != bpk.NEW_CELLS_KEY}
    # leaf pruning runs before linefit, the division insertion after it
    c7 = a[7]
    assert c7.index("prune_weak_leaf_nodes(nodes_by_id, edges, stats)") < c7.index(
        "nodes_by_id = linefit_smooth_output_graph(nodes_by_id, edges, stats)") < c7.index("# ---- divinsert:")


def _prune(threshold, nodes, edges):
    g = {"np": np, "LEAF_PRUNE_MIN_EDGE_PROB": threshold}
    exec(compile("from __future__ import annotations\n" + bpk.LEAFPRUNE_FN, "leafprune", "exec"), g)
    stats = {}
    kept_nodes, kept_edges = g["prune_weak_leaf_nodes"](dict(nodes), list(edges), stats)
    return set(kept_nodes), [(e["source_id"], e["target_id"]) for e in kept_edges], stats


def test_prune_rules():
    nodes = {i: {"t": t} for i, t in {1: 0, 2: 1, 3: 2, 4: 1, 5: 1, 6: 1, 7: 0, 8: 1, 9: 1, 10: 3, 11: 2}.items()}
    e = [(1, 2, 0.9), (2, 3, 0.95), (3, 11, 0.9), (9, 11, 0.9),  # interior nodes: never leaves
         (1, 4, 0.1),                # weak leaf 4 (t=1 < max_t=3): pruned
         (7, 5, None),               # leaf without probability (safe-division/gap edge): exempt
         (7, 6, float("nan")),       # non-finite probability: exempt
         (7, 8, 0.1), (1, 8, 0.1),   # two incoming edges: never pruned
         (11, 10, 0.05)]             # weak leaf on the last frame (t=3): kept
    edges = [{"source_id": s, "target_id": d, "edge_prob": p} for s, d, p in e]
    kept, kept_edges, stats = _prune(0.3, nodes, edges)
    assert kept == set(nodes) - {4}, kept
    assert (1, 4) not in kept_edges and len(kept_edges) == len(edges) - 1
    assert stats == {"leaf_prune_nodes": 1, "leaf_prune_edges": 1}
    # single pass, no cascade: 1 loses its child 4 but has other children anyway; threshold 0 = inert
    kept0, kept_edges0, stats0 = _prune(0.0, nodes, edges)
    assert kept0 == set(nodes) and len(kept_edges0) == len(edges) and stats0 == {}


def test_knob_needs_patch():
    name = "test_leafprune_guard_probe"
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "build_probe_kernel.py"), name,
                        "--set", "LEAF_PRUNE_MIN_EDGE_PROB=0.3"], capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode != 0 and "leafprune" in (r.stderr + r.stdout), (r.returncode, r.stdout, r.stderr)
    assert not (ROOT / "experiments" / name).exists()


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    for name, fn in tests:
        fn()
        print("ok", name)
    print(f"{len(tests)} tests passed")
