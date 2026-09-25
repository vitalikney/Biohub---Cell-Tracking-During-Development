"""Ideas workflow v3 E2: --patch lowrefine on --base x138 (tools/build_probe_kernel.py; spec in
research/wf_ideas_v3/TASK_CLOUD_SESSION.md T2 and s_merge.json C05).

    python -m pytest tests/test_lowrefine.py

The runtime fragments are taken from the PATCHED x138 cell 4 (its 'lowdet' replacement list, parsed with ast) and
executed on synthetic detector logits / feature maps with x138's real V1284 module (torch CPU, random head weights).
"""
import ast
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.build_probe_kernel as bpk  # noqa: E402

BUILDER = str(ROOT / "tools" / "build_probe_kernel.py")
SCRIPT = ROOT / "tools" / "repo" / "scripts" / "predict_unet_transformer.py"
X138 = bpk.BASES["x138"]
ANCHORS = (bpk.LOWREFINE_GLOBALS_ANCHOR, bpk.LOWREFINE_PEAKS_ANCHOR, bpk.LOWREFINE_CAST_ANCHOR,
           bpk.LOWREFINE_PRINT_ANCHOR)
# the exact T4 knobs of K2 (branch A: x138 + divinsert #35 config + safetail + lowrefine)
K2_ARGS = ["--base", "x138", "--patch", "divinsert", "--patch", "safetail", "--patch", "lowrefine",
           "--set", "DIVINS_ENABLE=1", "--set", "DIVINS_STEAL=1", "--set", "DIVINS_CAP=4", "--set", "DIVINS_FRAME_CAP=1",
           "--set", "DIVINS_ALPHA=1", "--set", "DIVINS_THRESH=0.4", "--set", "DIVINS_DUMP=0",
           "--set", "REPAIR_DEADLINE_S=34200", "--set", "DIVINS_DEADLINE_S=28800", "--set", "LOWREFINE_ENABLE=1"]


def _x138_cells() -> dict:
    nb = json.loads(X138["nb"].read_text(encoding="utf-8"))
    code = [c for c in nb["cells"] if c["cell_type"] == "code"]
    return {k: "".join(c["source"]) for k, c in enumerate(code)}


def _patched(*names: str) -> dict:
    bpk.CELL.clear()
    bpk.CELL.update(X138)
    cells = _x138_cells()
    try:
        for name in names:
            bpk.PATCHES[name](cells)
    finally:  # CELL is module state shared with the other test files (exp39 base by default)
        bpk.CELL.clear()
        bpk.CELL.update(bpk.BASES["exp39"])
    return cells


def _lowdet_list(c4: str) -> list:
    """x138's `for _label, _old, _new in [...]` replacement list (cache + lowdet) as Python values."""
    lists = [n.iter for n in ast.walk(ast.parse(c4)) if isinstance(n, ast.For) and isinstance(n.iter, ast.List)
             and isinstance(n.target, ast.Tuple) and [e.id for e in n.target.elts] == ["_label", "_old", "_new"]]
    assert len(lists) == 1
    return ast.literal_eval(lists[0])


def _fragments(c4: str) -> dict:
    return {label: new for label, _, new in _lowdet_list(c4)}


def _v1284_replacements(c4: str) -> list:
    """x138's four V1284 `_trial_source.replace(old, new)` edits of the predict script, in order."""
    out = []
    for n in ast.walk(ast.parse(c4)):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "replace"
                and isinstance(n.func.value, ast.Name) and n.func.value.id == "_trial_source"):
            out.append((n.lineno, ast.literal_eval(n.args[0]), ast.literal_eval(n.args[1])))
    return [(a, b) for _, a, b in sorted(out)]


def _v1284_module_text(c4: str) -> str:
    for n in ast.walk(ast.parse(c4)):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "write_text" and n.args:
            try:
                text = ast.literal_eval(n.args[0])
            except ValueError:
                continue
            if isinstance(text, str) and text.startswith('"""Frozen-feature coordinate regression'):
                return text
    raise AssertionError("V1284 module text not found")


# ---------------------------------------------------------------- build-time structure

def test_anchor_counts_strict():
    c4 = _x138_cells()[X138["predict"]]
    v1284_at = c4.index(bpk._LR_V1284_MARK)
    for anchor in ANCHORS:
        assert c4.count(anchor) == 1, anchor
        assert c4.index(anchor) < v1284_at, anchor  # inside the lowdet literals, before the V1284 block
    # strict at build time: a duplicated or missing anchor is an error, never a silent partial patch
    for anchor in ANCHORS:
        with pytest.raises(AssertionError, match="anchor count 2"):
            bpk.lowrefine_predict_source(c4.replace(anchor, anchor + anchor))
        with pytest.raises(AssertionError, match="anchor count 0"):
            bpk.lowrefine_predict_source(c4.replace(anchor, "#"))
    with pytest.raises(AssertionError, match="already applied"):
        bpk.lowrefine_predict_source(bpk.lowrefine_predict_source(c4))


def test_only_lowdet_literals_change_and_cells_compile():
    base = _x138_cells()
    for names in (("lowrefine",), ("divinsert", "lowrefine", "safetail"), ("divinsert", "leafprune", "lowrefine",
                                                                            "safetail")):
        cells = _patched(*names)
        without = _patched(*[n for n in names if n != "lowrefine"])
        p = X138["predict"]
        assert cells[p] == bpk.lowrefine_predict_source(base[p])  # no other x138 patch touches cell 4
        assert {k: v for k, v in cells.items() if k != p} == {k: v for k, v in without.items() if k != p}
        for k, src in cells.items():
            if isinstance(k, int):
                compile(src, f"cell{k}[{'+'.join(names)}]", "exec")
        for _, src in cells.get(bpk.NEW_CELLS_KEY, []):
            compile(src, "new_cell", "exec")
    c4, c4p = base[X138["predict"]], _patched("lowrefine")[X138["predict"]]
    # outside the replacement list nothing changed: V1284 block, its order after the lowdet list, every anchor (_old)
    old_list, new_list = _lowdet_list(c4), _lowdet_list(c4p)
    assert [(lab, old) for lab, old, _ in old_list] == [(lab, old) for lab, old, _ in new_list]
    assert [lab for lab, _, _ in new_list][-3:] == ["lowdet globals", "lowdet peaks", "lowdet write"]
    assert c4p.index("('lowdet peaks'") < c4p.index(bpk._LR_V1284_MARK)
    assert _v1284_replacements(c4p) == _v1284_replacements(c4) and len(_v1284_replacements(c4)) == 4
    assert c4p[c4p.index(bpk._LR_V1284_MARK):] == c4[c4.index(bpk._LR_V1284_MARK):]
    # the new runtime text is exactly the old one with the four edits
    old, new = _fragments(c4), _fragments(c4p)
    assert {k: v for k, v in old.items() if not k.startswith("lowdet")} == \
        {k: v for k, v in new.items() if not k.startswith("lowdet")}
    assert new["lowdet globals"] == old["lowdet globals"] + bpk.LOWREFINE_GLOBALS
    assert new["lowdet peaks"] == old["lowdet peaks"].replace(
        bpk.LOWREFINE_PEAKS_ANCHOR, textwrap.indent(bpk.LOWREFINE_PEAKS, " " * 24).lstrip(" "))
    cast_rt = bpk.LOWREFINE_CAST_ANCHOR.replace("\\n", "\n")
    print_rt = bpk.LOWREFINE_PRINT_ANCHOR.replace("\\n", "\n")
    assert new["lowdet write"] == old["lowdet write"].replace(cast_rt, bpk.LOWREFINE_CAST).replace(
        print_rt, print_rt + bpk.LOWREFINE_PRINT)
    # the patched predict-script text never re-emits an anchor the V1284 patch counts
    for v_old, _ in _v1284_replacements(c4):
        assert sum(frag.count(v_old) for frag in new.values()) == sum(frag.count(v_old) for frag in old.values())


@pytest.mark.skipif(not SCRIPT.exists(), reason="tools/repo predict script not present")
def test_predict_script_chain_compiles():
    """Replay x138's cell-4 order on our copy of predict_unet_transformer.py: the (patched) lowdet list with its
    exact-once checks, then the four V1284 edits with theirs; the result must compile and the refine calls must sit
    where the head sees the same feature map for the pool and the main peaks."""
    for c4 in (_x138_cells()[X138["predict"]], _patched("lowrefine")[X138["predict"]]):
        s = SCRIPT.read_text(encoding="utf-8")
        for label, old, new in _lowdet_list(c4):
            assert s.count(old) == 1, label
            s = s.replace(old, new, 1)
        compile(s, "predict_after_lowdet", "exec")
        for old, new in _v1284_replacements(c4):
            assert s.count(old) == 1, old[:60]  # 'V1284 patch anchor mismatch' would raise in the kernel
            s = s.replace(old, new)
        compile(s, "predict_after_v1284", "exec")
    pv = s[s.index("def predict_video("):s.index("\ndef ", s.index("def predict_video(") + 1)]
    pool = pv.index("_v1284_refine(ds_path, t, _low[_lhi], unet_out[:, f_idx])")
    main = pv.index("arr = _v1284_refine(ds_path, t, arr, unet_out[:, f_idx])")
    assert pv.index("_lsc = torch.sigmoid(") < pool < main  # score lookup on the integer grid first
    assert "_lc = _lc.astype(np.int16)" in s and "if not _LOWREFINE_ENABLE:" in s
    assert s.count("from v1284_coordinate_refinement import refine as _v1284_refine") == 1


# ---------------------------------------------------------------- runtime fragments on synthetic data

torch = pytest.importorskip("torch")
F = torch.nn.functional

ZYX = (6, 20, 20)
POOL_K = (3, 5, 5)
DOWNSAMPLE = (1, 4, 4)
# (z, y, x, sigmoid score) per frame; 0.99 / 0.975 are readmit-eligible, 0.9 / 0.6 / 0.35 stay on the grid,
# 0.2 is below the 0.3 lowdet threshold
PEAKS = {3: [(1, 2, 2, 0.99), (2, 2, 9, 0.975), (3, 9, 2, 0.9), (4, 9, 9, 0.6), (1, 16, 16, 0.35), (4, 16, 3, 0.2)],
         4: [(2, 3, 3, 0.6), (3, 12, 12, 0.35)],  # no refine-eligible peak in this frame
         5: [(0, 0, 0, 0.98), (5, 19, 19, 0.97), (2, 10, 15, 0.5)]}  # borders: clamped neighbours


def _logit(p: float) -> float:
    return float(np.log(p / (1 - p)))


def _det_logits(t: int):
    lg = torch.full((1, 1) + ZYX, -8.0)
    for z, y, x, p in PEAKS[t]:
        lg[0, 0, z, y, x] = _logit(p)
    return [lg, lg]  # W = 2 window positions; det_logits[f_idx] = (1, 1, Z, Y, X)


def _detect_cells_pooled(det_logits, t, det_threshold=0.5, pool_kernel=(3, 3, 3)):
    """The predict script's function (tools/repo/scripts/predict_unet_transformer.py), verbatim logic."""
    logits = det_logits.unsqueeze(0)
    pad = tuple(k // 2 for k in pool_kernel)
    pooled = F.max_pool3d(logits, pool_kernel, stride=1, padding=pad)
    is_peak = (logits == pooled) & (torch.sigmoid(logits) > det_threshold)
    peak_idx = torch.nonzero(is_peak[0, 0])
    if peak_idx.shape[0] == 0:
        return np.empty((0, 4), dtype=np.int16)
    coords = peak_idx.float().cpu().numpy()
    t_col = np.full((len(coords), 1), t, dtype=np.float32)
    return np.concatenate([t_col, coords], axis=1).astype(np.int16)


@pytest.fixture
def v1284(tmp_path, monkeypatch):
    """x138's own V1284 module (text from cell 4) with a random non-zero head, mode 'candidate'."""
    c4 = _x138_cells()[X138["predict"]]
    path = tmp_path / "v1284_coordinate_refinement.py"
    path.write_text(_v1284_module_text(c4), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"v1284_{tmp_path.name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    torch.manual_seed(0)
    head = mod.make_head()
    torch.nn.init.normal_(head[-1].weight, std=0.5)
    torch.nn.init.normal_(head[-1].bias, std=0.5)
    torch.save({"state_dict": head.state_dict(), "mean": torch.zeros(224), "scale": torch.ones(224)},
               tmp_path / "v1284_head.pt")
    monkeypatch.setenv("V1284_MODE", "candidate")
    monkeypatch.setenv("V1284_HEAD", str(tmp_path / "v1284_head.pt"))
    monkeypatch.setenv("BIOHUB_LOWDET_THRESHOLD", "0.3")
    monkeypatch.setenv("BIOHUB_READMIT_MIN_SCORE", "0.965")
    return mod


def _run_video(c4: str, refine, out_dir: Path, enable, capsys, monkeypatch):
    """globals -> per-frame 'lowdet peaks' -> 'lowdet write' (+ the closing parenthesis of its savez call), as the
    patched predict script runs them for one video; returns (npz arrays, namespace, stdout, refine calls)."""
    if enable is None:
        monkeypatch.delenv("BIOHUB_LOWREFINE_ENABLE", raising=False)
    else:
        monkeypatch.setenv("BIOHUB_LOWREFINE_ENABLE", enable)
    frags = _fragments(c4)
    calls = []

    def spy(ds_path, t, arr, feature):
        calls.append((t, arr.copy(), tuple(feature.shape)))
        return refine(ds_path, t, arr, feature)

    torch.manual_seed(1)
    unet_out = torch.randn((1, 2, 32) + ZYX)  # (1, W, C, Z, Y, X)
    ns = {"os": os, "np": np, "torch": torch, "_detect_cells_pooled": _detect_cells_pooled, "_v1284_refine": spy,
          "cfg": SimpleNamespace(det_threshold=0.965), "pool_k": POOL_K, "ds_path": Path("/x/vid.zarr"),
          "coord_offset": {}, "global_node_count": 0, "unet_out": unet_out}
    exec(frags["lowdet globals"], ns)
    for f_idx, t in enumerate(sorted(PEAKS)):
        ns.update(t=t, f_idx=f_idx % 2, det_logits=_det_logits(t))
        with torch.no_grad():  # predict_video is @torch.no_grad()
            exec(textwrap.dedent(frags["lowdet peaks"]), ns)
    ns.update(name="vid", _cd=out_dir, downsample=DOWNSAMPLE, coords=np.zeros((0, 4), np.float32))
    exec(textwrap.dedent(frags["lowdet write"] + "            )\n"), ns)
    with np.load(out_dir / "vid.npz") as z:
        arrays = {k: z[k] for k in z.files}
    return arrays, ns, capsys.readouterr().out, calls


def _grid_pool() -> np.ndarray:
    """The lowdet pool on the pooled grid (t, z, y, x): every synthetic peak above the 0.3 lowdet threshold."""
    return np.array([(t, z, y, x) for t in sorted(PEAKS) for z, y, x, p in PEAKS[t] if p > 0.3])


def test_refine_call_shape_and_mask(v1284, tmp_path, capsys, monkeypatch):
    c4 = _patched("lowrefine")[X138["predict"]]
    arrays, ns, out, calls = _run_video(c4, v1284.refine, tmp_path, "1", capsys, monkeypatch)
    low, score = arrays["low_coords"], arrays["low_score"]
    assert low.dtype == np.float32 and low.shape == (sum(p > 0.3 for v in PEAKS.values() for *_, p in v), 4)
    assert score.dtype == np.float32
    # one refine call per frame with an eligible peak, on exactly the rows with float64(score) >= READMIT_MIN_SCORE
    assert [c[0] for c in calls] == [3, 5]
    for t, arr, fshape in calls:
        assert arr.dtype == np.int16 and arr.shape[1] == 4 and fshape == (1, 32) + ZYX
        expect = sorted((t, z, y, x) for z, y, x, p in PEAKS[t] if p >= 0.965)
        assert sorted(map(tuple, arr.tolist())) == expect
    grid = _grid_pool()
    hi = np.asarray(score, dtype=np.float64) >= 0.965
    assert int(hi.sum()) == 4 and ns["_LOWREFINE_COUNTS"] == [0, 0, 0]  # reset after the per-video line
    scale = np.array(DOWNSAMPLE, dtype=np.float32)
    grid_full = grid.astype(np.float32)
    grid_full[:, 1:] *= scale
    lo = ~hi
    # rows below 0.965: exactly the grid values x138 writes (int16-exact floats); t column never changes
    by_key = {tuple(r): r for r in grid_full}
    for row, s in zip(low, score):
        if float(s) < 0.965:
            assert tuple(row) in by_key
    assert np.array_equal(np.sort(low[:, 0]), np.sort(grid_full[:, 0]))
    assert lo.sum() == len(low) - 4 and np.all(np.mod(low[lo, 1:], scale) == 0)
    # refined rows: the head's coordinates for the SAME peaks as the main path (main arr at det_threshold 0.965,
    # same unet_out[:, f_idx]), scaled like the main coords; displacement <= 2 um
    for f_idx, t in enumerate(sorted(PEAKS)):
        main = _detect_cells_pooled(_det_logits(t)[0][0], t, 0.965, POOL_K)
        if not len(main):
            continue
        with torch.no_grad():
            ref = v1284.refine(Path("/x/vid.zarr"), t, main, ns["unet_out"][:, f_idx % 2]).astype(np.float32)
        ref[:, 1:] *= scale
        mine = low[(low[:, 0] == t) & hi]
        assert len(mine) == len(main)
        for r in ref:
            assert np.min(np.abs(mine - r).max(axis=1)) < 1e-5
        shift_um = np.linalg.norm((ref[:, 1:] / scale - main[:, 1:]) * 1.625, axis=1)
        assert np.all(shift_um <= 2.00001) and np.any(shift_um > 0.05)
    assert "LOWREFINE vid: refined 4 of 10 lowdet peaks (score >= 0.965), failed frames 0" in out
    assert "LOWDET vid: 10 peaks above 0.3" in out and "LOWREFINE FAILED" not in out
    # cell 5's reader (load_low_detections) takes the dump as float64: the refined fractions survive
    assert np.any(np.mod(np.asarray(low, dtype=np.float64)[hi, 1:], 1.0) != 0)


@pytest.mark.parametrize("enable", ["0", None])
def test_enable0_byte_identical_pool(v1284, tmp_path, capsys, monkeypatch, enable):
    """ENABLE=0 (or unset) runs the original statements: the dump cell 5 reads (and so the CSV) is byte-identical."""
    base_dir, lr_dir = tmp_path / "base", tmp_path / "lr"
    base_dir.mkdir()
    lr_dir.mkdir()
    base, _, out_base, calls_base = _run_video(_x138_cells()[X138["predict"]], v1284.refine, base_dir, enable, capsys, monkeypatch)
    mine, _, out_mine, calls = _run_video(_patched("lowrefine")[X138["predict"]], v1284.refine, lr_dir, enable,
                                          capsys, monkeypatch)
    assert calls == [] and calls_base == []
    assert base.keys() == mine.keys()
    for k in base:
        assert base[k].dtype == mine[k].dtype and base[k].shape == mine[k].shape and \
            base[k].tobytes() == mine[k].tobytes(), k
    assert base["low_coords"].dtype == np.int16
    assert out_base == out_mine and "LOWREFINE" not in out_mine


def test_fail_soft_keeps_grid(v1284, tmp_path, capsys, monkeypatch):
    base_dir, lr_dir = tmp_path / "base", tmp_path / "lr"
    base_dir.mkdir()
    lr_dir.mkdir()
    base, *_ = _run_video(_x138_cells()[X138["predict"]], v1284.refine, base_dir, "0", capsys, monkeypatch)

    def boom(ds_path, t, arr, feature):
        raise RuntimeError("invalid V1284 displacement")
    arrays, ns, out, calls = _run_video(_patched("lowrefine")[X138["predict"]], boom, lr_dir, "1", capsys, monkeypatch)
    assert len(calls) == 2
    assert np.array_equal(arrays["low_coords"], base["low_coords"].astype(np.float32))  # grid coords as in x138
    assert arrays["low_score"].tobytes() == base["low_score"].tobytes()
    assert out.count("LOWREFINE FAILED") == 1  # first failing frame per video, then the counter
    assert "LOWREFINE FAILED (t=3, RuntimeError: invalid V1284 displacement)" in out
    assert "LOWREFINE vid: refined 0 of 10 lowdet peaks (score >= 0.965), failed frames 2" in out

    def bad_shape(ds_path, t, arr, feature):
        return np.zeros((len(arr) + 1, 4), np.float32)
    (tmp_path / "lr2").mkdir()
    arrays, _, out, _ = _run_video(_patched("lowrefine")[X138["predict"]], bad_shape, tmp_path / "lr2", "1", capsys, monkeypatch)
    assert np.array_equal(arrays["low_coords"], base["low_coords"].astype(np.float32))
    assert "LOWREFINE FAILED (t=3, RuntimeError: refine returned shape" in out


# ---------------------------------------------------------------- builder

def _build(name: str, *args: str):
    return subprocess.run([sys.executable, BUILDER, name, *args], capture_output=True, text=True, cwd=ROOT)


def _code(out: Path) -> list:
    nb = json.loads(next(out.glob("*.ipynb")).read_text(encoding="utf-8"))
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def test_builder_refusals():
    cases = [
        (["--patch", "lowrefine"], "needs --base x138"),
        (["--base", "x138", "--set", "LOWREFINE_ENABLE=1"], "needs --patch lowrefine"),
        (["--base", "x138", "--patch", "lowrefine", "--set", "LOWREFINE_ENABLE=2"], "must be 0 or 1"),
    ]
    for args, msg in cases:
        r = _build("zz-lowrefine-refusal", *args)
        assert r.returncode != 0 and msg in r.stderr, (args, r.stderr[-300:])
    assert not (ROOT / "experiments" / "zz-lowrefine-refusal").exists()


def test_build_k2_and_k1_twin():
    """K2 with the exact T4 knobs renders; K1 (= K2 with LOWREFINE_ENABLE=0) differs from it in one cell-0 line."""
    k2, k1 = ROOT / "experiments" / "zz-lowrefine-k2", ROOT / "experiments" / "zz-lowrefine-k1"
    try:
        r = _build(k2.name, *K2_ARGS, "--note", "K2 test render")
        assert r.returncode == 0, r.stderr[-800:]
        k1_args = [a if a != "LOWREFINE_ENABLE=1" else "LOWREFINE_ENABLE=0" for a in K2_ARGS]
        r = _build(k1.name, *k1_args)
        assert r.returncode == 0, r.stderr[-800:]
        c2, c1 = _code(k2), _code(k1)
        base = _x138_cells()
        assert len(c2) == len(base) + 2  # divinsert helper + DaughterNet cells
        assert 'os.environ["BIOHUB_LOWREFINE_ENABLE"] = "1"' in c2[0]
        assert 'os.environ["BIOHUB_REPAIR_DEADLINE_S"] = "34200"' in c2[0]
        assert 'os.environ["BIOHUB_DIVINS_DUMP"] = "0"' in c2[0]
        assert 'os.environ["BIOHUB_DEGRADE_KEEP_DIV"] = "1"' in c2[0]
        assert c2[X138["predict"]] == bpk.lowrefine_predict_source(base[X138["predict"]])
        post = [s for s in c2 if "def filter_output_graph(" in s]
        assert len(post) == 1 and bpk.safetail_divins_call() in post[0]
        for i, s in enumerate(c2):
            compile(s, f"k2cell{i}", "exec")
        diff = [(i, a, b) for i, (a, b) in enumerate(zip(c2, c1)) if a != b]
        assert len(c1) == len(c2) and [i for i, _, _ in diff] == [0]
        l2, l1 = diff[0][1].splitlines(), diff[0][2].splitlines()
        changed = [(a, b) for a, b in zip(l2, l1) if a != b and not a.startswith("# ---- zz-lowrefine-k2:")]
        assert len(l1) == len(l2) and changed == [('os.environ["BIOHUB_LOWREFINE_ENABLE"] = "1"',
                                                   'os.environ["BIOHUB_LOWREFINE_ENABLE"] = "0"')]
        probe = json.loads((k2 / "probe.json").read_text(encoding="utf-8"))
        assert "lab" not in probe and probe["change"]["PATCHES"] == "divinsert+lowrefine+safetail"
        assert probe["change"]["LOWREFINE_ENABLE"] == "1"
        meta = json.loads((k2 / "kernel-metadata.json").read_text(encoding="utf-8"))
        assert "anvithpothula/biohub-v1284-head-s075" in meta["dataset_sources"]
        assert bpk.WEIGHTS_DATASET in meta["dataset_sources"]
    finally:
        shutil.rmtree(k2, ignore_errors=True)
        shutil.rmtree(k1, ignore_errors=True)


def test_build_lowrefine_alone_touches_cell0_and_cell4_only():
    out = ROOT / "experiments" / "zz-lowrefine-alone"
    try:
        r = _build(out.name, "--base", "x138", "--patch", "lowrefine")
        assert r.returncode == 0, r.stderr[-800:]
        code, base = _code(out), _x138_cells()
        assert [i for i in range(len(code)) if code[i] != base[i]] == [0, X138["predict"]]
        assert code[0].endswith('os.environ["BIOHUB_LOWREFINE_ENABLE"] = "1"\n')
    finally:
        shutil.rmtree(out, ignore_errors=True)
