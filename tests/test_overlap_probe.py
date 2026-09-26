"""G-P bit-probe (tools/overlap_probe.py): decisions, CSV, zarr v3 + blosc reader, the three outcomes, notebook build.

    python -m pytest tests/test_overlap_probe.py
"""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import overlap_probe as P  # noqa: E402

REC = np.random.default_rng(7).integers(50, 4000, size=(14, 20, 70, 70), dtype=np.uint16)
DUMMY = ROOT.parent.parent.parent / "biohub-cell-tracking-during-development" / "test"
if not DUMMY.is_dir():
    DUMMY = ROOT / "biohub-cell-tracking-during-development" / "test"


def crop(t0, z0, y0, x0, T, Z, Y, X, rec=REC):
    return np.ascontiguousarray(rec[t0:t0 + T, z0:z0 + Z, y0:y0 + Y, x0:x0 + X])


def write_zarr(path: Path, arr: np.ndarray, codec: str = "blosc") -> Path:
    """Competition layout: group zarr.json + array '0' (one chunk per frame, bytes + blosc zstd bitshuffle)."""
    from numcodecs import Blosc
    path.mkdir(parents=True)
    (path / "zarr.json").write_text(json.dumps({"zarr_format": 3, "node_type": "group", "attributes": {}}))
    codecs = [{"name": "bytes", "configuration": {"endian": "little"}}]
    if codec == "blosc":
        codecs.append({"name": "blosc", "configuration": {"typesize": 2, "cname": "zstd", "clevel": 1,
                                                          "shuffle": "bitshuffle", "blocksize": 0}})
    meta = {"shape": list(arr.shape), "data_type": "uint16",
            "chunk_grid": {"name": "regular", "configuration": {"chunk_shape": [1, *arr.shape[1:]]}},
            "chunk_key_encoding": {"name": "default", "configuration": {"separator": "/"}}, "fill_value": 0,
            "codecs": codecs, "attributes": {}, "zarr_format": 3, "node_type": "array", "storage_transformers": []}
    (path / "0").mkdir()
    (path / "0" / "zarr.json").write_text(json.dumps(meta))
    enc = Blosc(cname="zstd", clevel=1, shuffle=Blosc.BITSHUFFLE)
    for t in range(arr.shape[0]):
        d = path / "0" / "c" / str(t) / "0" / "0"
        d.mkdir(parents=True)
        raw = np.ascontiguousarray(arr[t], dtype="<u2").tobytes()
        (d / "0").write_bytes(enc.encode(raw) if codec == "blosc" else raw)
    return path


def make_set(root: Path, n: int, overlap: bool) -> Path:
    rng = np.random.default_rng(11)
    root.mkdir(parents=True)
    for i in range(n):
        arr = rng.integers(50, 4000, size=(8, 16, 40, 40), dtype=np.uint16)
        if overlap and i == 0:
            arr = crop(0, 0, 0, 0, 10, 16, 48, 48)
        if overlap and i == 1:
            arr = crop(3, 2, 10, 12, 9, 16, 50, 52)
        write_zarr(root / f"e1_{i:02d}.zarr", arr)
    return root


def read_csv(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


# ----------------------------------------------------------------------------------------------------------------------
def test_decide_table():
    assert P.decide(4, 0, False) == "csv"
    assert P.decide(4, 3, False) == "csv"          # the visible dummy commit run always completes
    assert P.decide(4, 0, True) == "csv"
    assert P.decide(10, 1, False) == "csv"         # > 10 videos required
    assert P.decide(11, 1, False) == "raise"
    assert P.decide(120, 0, False) == "csv"
    assert P.decide(120, 5, True) == "nocsv"       # failure never reads as the overlap signal
    assert P.decide(0, 0, True) == "csv"


def test_minimal_rows_match_sample_shape():
    rows = P.minimal_rows([("a_1", (100, 64, 256, 256)), ("b_2", (2, 10, 20, 30)), ("c_3", None)])
    assert rows[:5] == [[0, "a_1", "node", 1, 0, 32, 128, 128, -1, -1], [1, "a_1", "node", 2, 1, 32, 128, 128, -1, -1],
                        [2, "a_1", "node", 3, 2, 32, 128, 128, -1, -1], [3, "a_1", "edge", -1, -1, -1, -1, -1, 1, 2],
                        [4, "a_1", "edge", -1, -1, -1, -1, -1, 2, 3]]
    b = [r for r in rows if r[1] == "b_2"]
    assert [r[2] for r in b] == ["node", "node", "edge"] and b[0][5:8] == [5, 10, 15]
    assert [r[0] for r in rows] == list(range(len(rows)))
    assert len([r for r in rows if r[1] == "c_3"]) == 5


def test_csv_equals_sample_submission_on_dummy(tmp_path):
    sample = DUMMY.parent / "sample_submission.csv"
    if not sample.exists():
        pytest.skip("no local competition data")
    shapes = [(p.name[:-5], P.video_shape(p)) for p in P.list_videos(DUMMY)]
    P.write_csv(tmp_path / "s.csv", P.minimal_rows(shapes))
    assert (tmp_path / "s.csv").read_text().splitlines() == sample.read_text().splitlines()


def test_reader_matches_zarr_and_raw(tmp_path):
    arr = crop(0, 0, 0, 0, 4, 16, 48, 48)
    zp = write_zarr(tmp_path / "v.zarr", arr)
    read, shape, name = P.make_reader(zp)
    assert shape == arr.shape and name in ("blosc2", "numcodecs", "blosc")
    for t in range(4):
        assert np.array_equal(read(t), arr[t])
    zarr = pytest.importorskip("zarr")
    z = zarr.open(str(zp / "0"), mode="r")
    assert np.array_equal(np.asarray(z[2]), arr[2])
    read2, _, name2 = P.make_reader(write_zarr(tmp_path / "raw.zarr", arr, codec="none"))
    assert name2 == "raw" and np.array_equal(read2(3), arr[3])


def test_reader_on_dummy_clip():
    if not DUMMY.is_dir():
        pytest.skip("no local competition data")
    zarr = pytest.importorskip("zarr")
    p = P.list_videos(DUMMY)[0]
    read, shape, name = P.make_reader(p)
    assert name == "blosc2" or name in ("numcodecs", "blosc")
    assert np.array_equal(read(7), np.asarray(zarr.open(str(p / "0"), mode="r")[7]))


def test_outcome_raise_on_large_set_with_overlap(tmp_path):
    d = make_set(tmp_path / "hid", 12, overlap=True)
    with pytest.raises(RuntimeError, match=r"^OVERLAP PROBE: 1 accepted pairs$"):
        P.run_probe(d, tmp_path, workers=1, log=lambda s: None)
    assert not (tmp_path / "submission.csv").exists()


def test_outcome_csv_small_set_and_no_overlap(tmp_path):
    d = make_set(tmp_path / "small", 4, overlap=True)
    s = P.run_probe(d, tmp_path, workers=1, log=lambda s: None)
    assert s["accepted"] == 1 and s["outcome"] == "csv"
    rows = read_csv(tmp_path / "submission.csv")
    assert rows[0] == P.CSV_HEADER and len(rows) == 1 + 4 * 5
    (tmp_path / "submission.csv").unlink()
    d = make_set(tmp_path / "none", 12, overlap=False)
    s = P.run_probe(d, tmp_path, workers=1, log=lambda s: None)
    assert s["accepted"] == 0 and s["outcome"] == "csv" and not s["failed"]
    assert len(read_csv(tmp_path / "submission.csv")) == 1 + 12 * 5


def test_outcome_nocsv_on_failure(tmp_path):
    d = make_set(tmp_path / "bad", 12, overlap=True)
    (d / "e1_05.zarr" / "0" / "c" / "3" / "0" / "0" / "0").write_bytes(b"not blosc")
    lines = []
    s = P.run_probe(d, tmp_path, workers=1, log=lines.append)
    assert s["failed"] and s["outcome"] == "nocsv" and not (tmp_path / "submission.csv").exists()
    assert any(line.startswith("OVERLAP PROBE FAILED") for line in lines)
    s = P.run_probe(None, tmp_path, workers=1, log=lambda s: None)   # no test dir at all (commit-run side)
    assert s["failed"] and s["outcome"] == "csv" and read_csv(tmp_path / "submission.csv") == [P.CSV_HEADER]


def test_find_test_dir(tmp_path):
    assert P.find_test_dir(candidates=(str(tmp_path / "x"),)) is None
    assert P.find_test_dir(candidates=(str(tmp_path / "x"), str(tmp_path))) == tmp_path
    assert P.find_test_dir(candidates=(), override=str(tmp_path)) == tmp_path


def test_notebook_build_embeds_modules_and_runs(tmp_path):
    nbp = P.build_notebook(tmp_path / "kern")
    meta = json.loads((tmp_path / "kern" / "kernel-metadata.json").read_text())
    assert meta["id"] == "vitaliineibauer/biohub-exp65-overlap-probe" and meta["is_private"] is True
    assert meta["enable_gpu"] is False and meta["enable_internet"] is False
    assert meta["competition_sources"] == ["biohub-cell-tracking-during-development"] and meta["dataset_sources"] == []
    assert meta["code_file"] == nbp.name
    code = P.notebook_code(nbp)
    ns = {}
    src = code.split("import overlap_probe\n")[0]
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        exec(compile(src, "nb", "exec"), ns)
    finally:
        os.chdir(cwd)
    mods = tmp_path / "_overlap_mods"
    for m in ("overlap_reg.py", "overlap_probe.py"):   # LF text of the tool files (the checkout may be CRLF)
        assert (mods / m).read_bytes() == (ROOT / "tools" / m).read_text(encoding="utf-8").encode("utf-8")
    # the whole notebook as one script on a 12-video overlapping set (2 spawn workers): must raise
    d = make_set(tmp_path / "hid", 12, overlap=True)
    script = tmp_path / "nb.py"
    script.write_text(code, encoding="utf-8")
    env = dict(os.environ, OVERLAP_PROBE_TEST_DIR=str(d), OVERLAP_PROBE_WORKERS="2")
    # exec'd like a notebook cell (no __main__.__file__, so spawn children do not re-run the script)
    r = subprocess.run([sys.executable, "-c", f"exec(open({str(script)!r}, encoding='utf-8').read())"], cwd=tmp_path,
                       env=env, capture_output=True, text=True, timeout=600)
    assert r.returncode != 0 and "RuntimeError: OVERLAP PROBE: 1 accepted pairs" in r.stderr
