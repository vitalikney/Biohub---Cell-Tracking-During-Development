"""T3: tools/forkmid_dose.py (C04 forkmid dose on a submission.csv).

    python tests/test_forkmid_dose.py      (or pytest tests/test_forkmid_dose.py)
"""
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.forkmid_dose as fd  # noqa: E402

COLS = ["id", "dataset", "row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"]


def _csv(path: Path, nodes: list, edges: list) -> Path:
    rows = [(ds, "node", n, t, z, y, x, -1, -1) for ds, n, t, z, y, x in nodes]
    rows += [(ds, "edge", -1, -1, -1, -1, -1, s, d) for ds, s, d in edges]
    df = pd.DataFrame([(i, *r) for i, r in enumerate(rows)], columns=COLS)
    df.to_csv(path, index=False)
    return path


# video A: fork at node 0 with children offset in x only (mid 0.5 px in x off the parent), plus a chain 3->4
# video B: fork at node 10, midpoint 4 z-slices away (4 * 1.625 = 6.5 um >= 4.5), node ids reused per video
NODES = [("A", 0, 0, 5, 50, 50), ("A", 1, 1, 5, 50, 45), ("A", 2, 1, 5, 50, 56),
         ("A", 3, 0, 1, 1, 1), ("A", 4, 1, 1, 1, 2),
         ("B", 0, 0, 0, 0, 0), ("B", 10, 0, 2, 20, 20), ("B", 11, 1, 6, 10, 20), ("B", 12, 1, 6, 30, 20)]
EDGES = [("A", 0, 1), ("A", 0, 2), ("A", 3, 4), ("B", 10, 11), ("B", 10, 12)]


def test_forks_and_distances(tmp_path):
    f = fd.forks_of(pd.read_csv(_csv(tmp_path / "s.csv", NODES, EDGES))).set_index("dataset")
    assert len(f) == 2 and set(f.node_id) == {0, 10}
    assert f.loc["A", "dist_um"] == pytest.approx(0.5 * 0.40625)
    assert f.loc["B", "dist_um"] == pytest.approx(4 * 1.625)


def test_dose_json_and_rule(tmp_path):
    csv = _csv(tmp_path / "s.csv", NODES, EDGES)
    out = tmp_path / "d.json"
    assert fd.main([str(csv), "--out", str(out)]) == 0
    r = json.loads(out.read_text(encoding="utf-8"))
    assert r["n_forks"] == 2 and r["n_ge_thresh"] == 1 and r["share_ge_thresh"] == 0.5
    assert r["per_video"]["A"]["n_ge_thresh"] == 0 and r["per_video"]["B"]["n_ge_thresh"] == 1
    assert r["verdict"].startswith("C04 STOP")
    assert fd.verdict(0.0).startswith("NO-OP") and fd.verdict(0.15).startswith("OK")


def test_base_split(tmp_path):
    base = _csv(tmp_path / "b.csv", NODES, [e for e in EDGES if e[0] == "A"])  # base has only video A's fork
    csv = _csv(tmp_path / "s.csv", NODES, EDGES)
    r = fd.dose(csv, base)
    assert r["in_base"]["n_forks"] == 1 and r["in_base"]["n_ge_thresh"] == 0
    assert r["new_vs_base"]["n_forks"] == 1 and r["new_vs_base"]["n_ge_thresh"] == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
