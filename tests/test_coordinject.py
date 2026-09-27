"""--patch coordinject (tools/coordinject_patch.py): yuki0731/biohub-coord-inject as a post-step on submission.csv.

    python -m pytest tests/test_coordinject.py
    COORDINJECT_WEIGHTS_DIR=<folder with the dataset files> python -m pytest tests/test_coordinject.py   # + CPU e2e
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.build_probe_kernel as bpk  # noqa: E402
import tools.coordinject_patch as cip  # noqa: E402

BUILDER = str(ROOT / "tools" / "build_probe_kernel.py")
K2_NB = ROOT / "experiments/exp58_x138_safe_lowref/exp58-x138-safe-lowref.ipynb"
K2_SHA = "1f1ddb6d63b47f540ad614232e821ad215f27fce0d901cdbb9f67a8beeb67855"
K = ["--set", "DIVINS_ENABLE=1", "--set", "DIVINS_STEAL=1", "--set", "DIVINS_CAP=4", "--set", "DIVINS_FRAME_CAP=1",
     "--set", "DIVINS_ALPHA=1", "--set", "DIVINS_THRESH=0.4", "--set", "DIVINS_DUMP=0", "--set", "REPAIR_DEADLINE_S=34200",
     "--set", "DIVINS_DEADLINE_S=28800", "--set", "LOWREFINE_ENABLE=1"]
K2_PATCHES = ["--patch", "divinsert", "--patch", "safetail", "--patch", "lowrefine"]
SCALE = np.array([1.625, 0.40625, 0.40625])
HEADER = "id,dataset,row_type,node_id,t,z,y,x,source_id,target_id\r\n"


def _build(name, out_dir, *args):
    return subprocess.run([sys.executable, BUILDER, name, "--out-dir", out_dir, "--base", "x138", *args],
                          capture_output=True, text=True, cwd=str(ROOT))


def _code(nb_path):
    nb = json.loads(Path(nb_path).read_text(encoding="utf-8"))
    return ["".join(c["source"]) if isinstance(c["source"], list) else c["source"]
            for c in nb["cells"] if c["cell_type"] == "code"]


def _cell_ns(tmp_path, env, csv_text, stems=("vidA", "vidB"), extra=None):
    """Exec the coordinject cell the way the notebook does (globals of the earlier cells mocked)."""
    sub = tmp_path / "submission.csv"
    sub.write_bytes(csv_text.encode("ascii"))
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    ns = {"os": os, "test_stems": list(stems), "TEST_DIR": tmp_path / "test", "SUBMISSION_PATH": sub,
          "KERNEL_START_TS": __import__("time").time(), "__name__": "__main__", **(extra or {})}
    try:
        exec(compile(cip.CELL_SRC, "coordinject_cell", "exec"), ns)
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return ns, sub


def _csv(rows):
    out = HEADER
    for i, r in enumerate(rows):
        out += f"{i}," + ",".join(str(x) for x in r) + "\r\n"
    return out


def _fake_refined(dets_by_t, T=3, shape=(3, 64, 256, 256)):
    offs, coords = [0], []
    for t in range(T):
        d = dets_by_t.get(t, [])
        coords += d
        offs.append(offs[-1] + len(d))
    return {"raw_ref": np.asarray(coords, dtype=np.float32).reshape(-1, 3), "scores": np.ones(len(coords), np.float32),
            "offsets": np.asarray(offs, np.int64), "T": np.int64(T), "shape": np.asarray(shape, np.int64)}


# ---------------------------------------------------------------- build time

def test_off_build_is_k2_plus_one_cell_and_on_build_attaches_the_dataset(tmp_path):
    assert hashlib.sha256(K2_NB.read_bytes()).hexdigest() == K2_SHA  # the final is untouched
    tmp = "zz_test_coordinject"
    try:
        r = _build("exp58_x138_safe_lowref", f"{tmp}/k2", *K2_PATCHES, *K)
        assert r.returncode == 0, r.stderr
        assert (ROOT / "experiments" / tmp / "k2/exp58-x138-safe-lowref.ipynb").read_bytes() == K2_NB.read_bytes()
        r = _build("exp58_x138_safe_lowref", f"{tmp}/off", *K2_PATCHES, "--patch", "coordinject", *K)
        assert r.returncode == 0, r.stderr
        k2, off = _code(K2_NB), _code(ROOT / "experiments" / tmp / "off/exp58-x138-safe-lowref.ipynb")
        assert len(off) == len(k2) + 1
        post = next(i for i, s in enumerate(k2) if 'write_test_submission("base")' in s)
        assert off[post + 1] == cip.CELL_SRC and off[:post + 1] + off[post + 2:] == k2
        meta = json.loads((ROOT / "experiments" / tmp / "off/kernel-metadata.json").read_text())
        assert cip.DATASET not in meta["dataset_sources"]
        r = _build("exp58_x138_safe_lowref", f"{tmp}/on", *K2_PATCHES, "--patch", "coordinject", *K,
                   "--set", "COORDINJECT_ENABLE=1")
        assert r.returncode == 0, r.stderr
        on = _code(ROOT / "experiments" / tmp / "on/exp58-x138-safe-lowref.ipynb")
        assert on[1:] == off[1:] and 'os.environ["BIOHUB_COORDINJECT_ENABLE"] = "1"' in on[0]
        meta = json.loads((ROOT / "experiments" / tmp / "on/kernel-metadata.json").read_text())
        assert meta["dataset_sources"][-1] == cip.DATASET
        for i, s in enumerate(on):
            compile(s, f"cell{i}", "exec")
    finally:
        shutil.rmtree(ROOT / "experiments" / tmp, ignore_errors=True)


@pytest.mark.parametrize("args,msg", [
    (["--set", "COORDINJECT_ENABLE=1"], "need --patch coordinject"),
    (["--patch", "coordinject", "--set", "COORDINJECT_ENABLE=2"], "must be 0 or 1"),
    (["--patch", "coordinject", "--set", "COORDINJECT_MAX_UM=9"], "(0, 7]"),
    (["--patch", "coordinject", "--set", "COORDINJECT_ALPHA=0"], "(0, 1]"),
    (["--patch", "coordinject", "--set", "COORDINJECT_WORKERS=3"], "1 or 2"),
    (["--patch", "coordinject", "--set", "COORDINJECT_DEADLINE_S=43000"], "submission build"),
    (["--patch", "coordinject", "--set", "COORDINJECT_FORCE_FAIL=1"], "needs --lab"),
    (["--patch", "coordinject", "--set", "COORDINJECT_TYPO=1"], "unknown coordinject knobs"),
])
def test_builder_refusals(args, msg):
    assert msg in (cip.check("x138", [a for i, a in enumerate(args) if i and args[i - 1] == "--patch"],
                             {("BIOHUB_" + a.split("=")[0]): a.split("=", 1)[1]
                              for i, a in enumerate(args) if i and args[i - 1] == "--set"}, lab=False) or "")


def test_builder_refuses_exp39_base():
    assert "needs --base x138" in cip.check("exp39", ["coordinject"], {}, lab=False)
    assert cip.check("x138", ["coordinject"], {"BIOHUB_COORDINJECT_FORCE_FAIL": "1"}, lab=True) is None
    assert "coordinject" in bpk.PATCHES and "coordinject" in bpk.BASES["x138"]["patches"]


# ---------------------------------------------------------------- runtime (the cell exec'd with mocks)

def test_disabled_is_a_no_op(tmp_path, capsys):
    text = _csv([("vidA", "node", 1, 0, 10, 100, 100, -1, -1)])
    ns, sub = _cell_ns(tmp_path, {"BIOHUB_COORDINJECT_ENABLE": "0"}, text)
    assert sub.read_bytes() == text.encode() and ns["COORDINJECT_STATE"]["status"] == "disabled"
    assert "coordinject disabled" in capsys.readouterr().out


def test_force_fail_and_no_gpu_leave_the_csv(tmp_path, capsys):
    text = _csv([("vidA", "node", 1, 0, 10, 100, 100, -1, -1)])
    ns, sub = _cell_ns(tmp_path, {"BIOHUB_COORDINJECT_ENABLE": "1", "BIOHUB_COORDINJECT_FORCE_FAIL": "1"}, text)
    assert sub.read_bytes() == text.encode() and ns["COORDINJECT_STATE"]["status"] == "failed"
    assert "COORDINJECT FAILED" in capsys.readouterr().out
    ns, sub = _cell_ns(tmp_path, {"BIOHUB_COORDINJECT_ENABLE": "1", "BIOHUB_COORDINJECT_FORCE_FAIL": "0",
                                  "BIOHUB_COORDINJECT_DEADLINE_S": "100"}, text)
    assert sub.read_bytes() == text.encode() and ns["COORDINJECT_STATE"]["status"] == "skipped_deadline"


def test_rewrite_moves_only_matched_node_rows(tmp_path):
    rows = [("vidA", "node", 1, 0, 10, 100, 100, -1, -1),     # det 1 um in z away -> moves
            ("vidA", "node", 2, 0, 30, 200, 50, -1, -1),      # nearest det 4 um away -> stays (max_um 3)
            ("vidA", "node", 3, 1, 5, 20, 20, -1, -1),        # frame 1: det at +2 vox y (0.81 um) -> moves
            ("vidA", "node", 4, 2, 63, 255, 255, -1, -1),     # frame 2 has no detections -> stays
            ("vidA", "edge", -1, -1, -1, -1, -1, 1, 3),
            ("vidB", "node", 7, 0, 10, 100, 100, -1, -1),     # no npz for vidB -> untouched
            ("vidB", "edge", -1, -1, -1, -1, -1, 7, 7)]
    sub = tmp_path / "submission.csv"
    sub.write_bytes(_csv(rows).encode())
    ns = {"os": os}
    exec(compile(cip.CELL_SRC.split("\nif COORDINJECT_ENABLE:")[0], "cell", "exec"), ns)
    ref = _fake_refined({0: [[10 + 1 / 1.625, 100.4, 99.6], [30, 200 + 4 / 0.40625, 50]], 1: [[5, 22, 20]]})
    tmp, stats = ns["coordinject_rewrite_csv"](sub, {"vidA": ref}, max_um=3.0, alpha=1.0)
    out = tmp.read_bytes().decode().split("\r\n")
    src = sub.read_bytes().decode().split("\r\n")
    assert len(out) == len(src)
    changed = {i for i, (a, b) in enumerate(zip(src, out)) if a != b}
    assert changed == {1, 3}                                   # lines of node 1 and node 3 (header = line 0)
    assert out[1] == "0,vidA,node,1,0,11,100,100,-1,-1" and out[3] == "2,vidA,node,3,1,5,22,20,-1,-1"
    assert stats["vidA"]["nodes"] == 4 and stats["vidA"]["replaced"] == 2 and stats["vidA"]["moved_cells"] == 2
    # alpha 0.5 -> halfway, rounded like the x138 writer
    tmp, stats = ns["coordinject_rewrite_csv"](sub, {"vidA": ref}, max_um=3.0, alpha=0.5)
    assert tmp.read_bytes().decode().split("\r\n")[3] == "2,vidA,node,3,1,5,21,20,-1,-1"
    # a float CSV (floatout) keeps float cells
    fl = tmp_path / "f.csv"
    fl.write_bytes(_csv([("vidA", "node", 1, 0, "10.000", "100.000", "100.000", -1, -1)]).encode())
    tmp, _ = ns["coordinject_rewrite_csv"](fl, {"vidA": ref}, max_um=3.0, alpha=1.0)
    assert tmp.read_bytes().decode().split("\r\n")[1] == "0,vidA,node,1,0,10.615,100.400,99.600,-1,-1"


def test_positions_match_inject_one_rule():
    ns = {"os": os}
    exec(compile(cip.CELL_SRC.split("\nif COORDINJECT_ENABLE:")[0], "cell", "exec"), ns)
    rng = np.random.default_rng(0)
    old = rng.uniform([0, 0, 0], [63, 255, 255], size=(400, 3))
    times = rng.integers(0, 3, size=400)
    dets = {t: (old[times == t] + rng.normal(0, 2.0, size=((times == t).sum(), 3))).tolist() for t in range(3)}
    ref = _fake_refined(dets)
    new, rep, dist = ns["coordinject_positions"](old, times, ref, 3.0, 1.0)
    for k in range(len(old)):  # brute force, inject_one's loop
        t = times[k]
        c = np.asarray(dets[t])
        d = np.linalg.norm((c - old[k]) * SCALE, axis=1)
        j = int(np.argmin(d))
        assert np.isclose(dist[k], d[j])
        assert rep[k] == (d[j] <= 3.0)
        assert np.allclose(new[k], c[j] if d[j] <= 3.0 else old[k], atol=1e-5)


# ---------------------------------------------------------------- CPU end-to-end (needs the dataset files locally)

@pytest.mark.skipif(not os.environ.get("COORDINJECT_WEIGHTS_DIR"), reason="set COORDINJECT_WEIGHTS_DIR")
def test_end_to_end_cpu_two_frames(tmp_path, monkeypatch):
    """The real worker (dataset module verbatim) on 2-frame copies of two public test videos; torch.cuda.device_count
    is mocked to 1 so the cell launches one worker (it runs on CPU); K2's dummy submission.csv is the input."""
    import torch

    k2_csv = ROOT / "_dl/biohub-exp58-x138-safe-lowref/submission.csv"
    src = ROOT / "biohub-cell-tracking-during-development/test"
    if not k2_csv.exists() or not src.exists():
        pytest.skip("needs the K2 dummy CSV and the local test videos")
    stems = sorted(p.name[:-5] for p in src.glob("*.zarr"))
    for stem in stems[:2]:
        dst = tmp_path / "test" / f"{stem}.zarr"
        for p in (src / f"{stem}.zarr").rglob("zarr.json"):
            (dst / p.relative_to(src / f"{stem}.zarr")).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(p, dst / p.relative_to(src / f"{stem}.zarr"))
        for t in (0, 1):
            shutil.copytree(src / f"{stem}.zarr/0/c/{t}", dst / f"0/c/{t}")
    monkeypatch.setattr(torch.cuda, "device_count", lambda: 1)
    out_dir = tmp_path / "work"
    text = k2_csv.read_bytes().decode("ascii")
    ns, sub = _cell_ns(tmp_path, {"BIOHUB_COORDINJECT_ENABLE": "1", "BIOHUB_COORDINJECT_FORCE_FAIL": "0",
                                  "BIOHUB_COORDINJECT_DEADLINE_S": "37800",
                                  "BIOHUB_COORDINJECT_DIR": os.environ["COORDINJECT_WEIGHTS_DIR"],
                                  "BIOHUB_COORDINJECT_WORK": str(out_dir)},
                       text, stems=stems, extra={})
    ns_out = ns["COORDINJECT_OUT"]
    assert ns["COORDINJECT_STATE"]["status"] == "applied", ns["COORDINJECT_STATE"]
    assert ns["COORDINJECT_STATE"]["videos"] == 2
    a, b = text.split("\r\n"), sub.read_bytes().decode("ascii").split("\r\n")
    assert len(a) == len(b)
    for x, y in zip(a, b):
        if x == y:
            continue
        px, py = x.split(","), y.split(",")
        assert px[:5] == py[:5] and px[8:] == py[8:] and px[2] == "node" and px[1] in stems[:2] and int(px[4]) in (0, 1)
    assert sum(x != y for x, y in zip(a, b)) > 0
    shutil.rmtree(ns_out, ignore_errors=True)
