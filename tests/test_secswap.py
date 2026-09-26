"""--patch secswap on --base x138 (tools/build_probe_kernel.py; spec research/wf_ideas_v4/reach0955/plan.notes.md T4,
r_retrain.json RT-2): swap x138's secondary detector (pilkwang seed314159) for another dataset of the same layout.

    python -m pytest tests/test_secswap.py

Build-time: one exact-once line in x138 code cell 3, the guards in main(), the finals / ladder rebuilds stay
byte-identical, and the K2+secswap notebook differs from K2 only by the two knob lines and the replaced line.
Runtime: x138's own secondary block (patched cell 3, from 'import hashlib as _hashlib' to the integrity receipt) runs
on a synthetic dataset folder, with x138's own remove_path / copy_or_extract_tree.
"""
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.build_probe_kernel as bpk  # noqa: E402

BUILDER = str(ROOT / "tools" / "build_probe_kernel.py")
X138 = bpk.BASES["x138"]
PARENT = bpk.SECSWAP_PARENT_SHA256
NEW_SHA = hashlib.sha256(b"secswap-test-weights").hexdigest()
MANIFEST = "/kaggle/input/datasets/vitaliineibauer/biohub-secft-all-v1/ARTIFACT_MANIFEST.json"
DATASET = "vitaliineibauer/biohub-secft-all-v1"
SECSWAP = ["--patch", "secswap", "--set", f"SECONDARY_EXPECTED_SHA256={NEW_SHA}",
           "--set", f"SECONDARY_ARTIFACT_MANIFEST={MANIFEST}", "--dataset", DATASET]

# the documented builds (CONTEXT 'BUILD COMMANDS FOR 26.09' l.1768-1780; ladder CONTEXT 26 Sep 20:49 UTC) and the
# notebook sha256 of the committed kernels
K = ["--set", "DIVINS_ENABLE=1", "--set", "DIVINS_STEAL=1", "--set", "DIVINS_CAP=4", "--set", "DIVINS_FRAME_CAP=1",
     "--set", "DIVINS_ALPHA=1", "--set", "DIVINS_THRESH=0.4", "--set", "DIVINS_DUMP=0"]
T = ["--set", "REPAIR_DEADLINE_S=34200", "--set", "DIVINS_DEADLINE_S=28800"]
K2_ARGS = ["--base", "x138", "--patch", "divinsert", "--patch", "safetail", "--patch", "lowrefine", *K, *T,
           "--set", "LOWREFINE_ENABLE=1"]
BUILDS = {
    "exp58_x138_safe_lowref": (K2_ARGS, "1f1ddb6d63b47f540ad614232e821ad215f27fce0d901cdbb9f67a8beeb67855"),
    "exp58t_x138_safe": (["--base", "x138", "--patch", "divinsert", "--patch", "safetail", "--patch", "lowrefine", *K,
                          *T, "--set", "LOWREFINE_ENABLE=0"],
                         "a77bcd6bad527e7bd5c01cbde2147b5169c3c4b51a1507cc0c34276af8dd2b03"),
    "exp58n_x138_safe_lowref": (["--base", "x138", "--patch", "safetail", "--patch", "lowrefine",
                                 "--set", "REPAIR_DEADLINE_S=34200", "--set", "LOWREFINE_ENABLE=1"],
                                "55038fd6ac009ad91af4f4f87eb4f3def605f94a84ac6e7eb790e83b525cf4f7"),
    "exp70a_k2_lp30": (["--base", "x138", "--patch", "divinsert", "--patch", "leafprune", "--patch", "safetail",
                        "--patch", "lowrefine", *K, *T, "--set", "LOWREFINE_ENABLE=1",
                        "--set", "LEAF_PRUNE_MIN_EDGE_PROB=0.3"],
                       "132438a9626400e4e652c801f908d898baf2d93481bb6f19b3748842bbb70b61"),
    "exp70d_k2_dc030": ([*K2_ARGS, "--set", "DEEPCENTER_SAFE_DIV_THRESHOLD=0.30"],
                        "e0b8fc0cf87660c3e064b89d07f4af4dcda10beb79454603808fbf5d9c91691f"),
    "exp70e_k2_lp30_dc030": (["--base", "x138", "--patch", "divinsert", "--patch", "leafprune", "--patch", "safetail",
                              "--patch", "lowrefine", *K, *T, "--set", "LOWREFINE_ENABLE=1",
                              "--set", "LEAF_PRUNE_MIN_EDGE_PROB=0.3", "--set", "DEEPCENTER_SAFE_DIV_THRESHOLD=0.30"],
                             "c0f3380c04af3ae6c7b60add9fbaa42929d8a5f467bcea12326ccc827bb04ed8"),
    "exp70b_k2_fm45": ([*K2_ARGS, "--patch", "forkmid", "--set", "FORKMID_ENABLE=1"],
                       "b8e7ece1a33cd2a184c2fd199700c1cd8320fde170f28a139265f76babd8b911"),
}


def _x138_cells() -> dict:
    nb = json.loads(X138["nb"].read_text(encoding="utf-8"))
    return {k: "".join(c["source"]) for k, c in enumerate(c for c in nb["cells"] if c["cell_type"] == "code")}


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


def _build(name: str, out_dir: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, BUILDER, name, "--out-dir", out_dir, *args], capture_output=True, text=True,
                          cwd=str(ROOT))


def _code(nb_path: Path) -> list:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


# ---------------------------------------------------------------- build-time structure

def test_patch_is_one_exact_once_line_in_the_secondary_cell():
    base = _x138_cells()
    sec = X138["secondary"]
    assert [k for k, s in base.items() if PARENT in s] == [sec]          # the pin lives in cell 3 only, once
    for names in (("secswap",), ("divinsert", "lowrefine", "secswap", "safetail"),
                  ("divinsert", "leafprune", "lowrefine", "forkmid", "secswap", "overlapcons", "safetail")):
        cells, without = _patched(*names), _patched(*[n for n in names if n != "secswap"])
        assert {k: v for k, v in cells.items() if k != sec} == {k: v for k, v in without.items() if k != sec}
        assert cells[sec] == bpk.secswap_secondary_source(base[sec])     # no other patch touches cell 3
        for k, src in cells.items():
            if isinstance(k, int):
                compile(src, f"cell{k}[{'+'.join(names)}]", "exec")
    a, b = base[sec].splitlines(keepends=True), _patched("secswap")[sec].splitlines(keepends=True)
    diff = [(x, y) for x, y in zip(a, b) if x != y]
    assert len(a) == len(b) and diff == [(bpk.SECSWAP_SHA_ANCHOR, bpk.SECSWAP_SHA_NEW)]
    assert bpk.SECSWAP_SHA_NEW == ('_secondary_expected_sha256 = os.environ.get("BIOHUB_SECONDARY_EXPECTED_SHA256", '
                                   f'"{PARENT}").strip().lower()\n')
    # strict at build time: never a silent partial patch
    c3 = base[sec]
    with pytest.raises(AssertionError, match="already applied"):
        bpk.secswap_secondary_source(bpk.secswap_secondary_source(c3))
    with pytest.raises(AssertionError, match="only in the pinned line"):
        bpk.secswap_secondary_source(c3 + f"\n# {PARENT}\n")
    with pytest.raises(AssertionError, match="no longer reads"):
        bpk.secswap_secondary_source(c3.replace(bpk.SECSWAP_MANIFEST_READ, "_secondary_manifest_explicit = Path((\n"))
    other = dict(base)
    other[5] = other[5] + f"\n# {PARENT}\n"
    bpk.CELL.clear()
    bpk.CELL.update(X138)
    try:
        with pytest.raises(AssertionError, match=r"also pinned in code cells \[5\]"):
            bpk.patch_secswap(other)
    finally:
        bpk.CELL.clear()
        bpk.CELL.update(bpk.BASES["exp39"])


def test_hardset_knob_list_is_exactly_what_x138_resets_after_cell0():
    base = _x138_cells()
    pat = re.compile(r'os\.environ\[\s*"(BIOHUB_(?:SECONDARY|DUAL_SEED)\w*)"\s*\]\s*=(?!=)')
    hardset = {m.group(1) for k, s in base.items() if k >= 1 for m in pat.finditer(s)}
    assert hardset == set(bpk.X138_HARDSET_KNOBS)
    everything = "".join(base.values())
    for knob in bpk.SECSWAP_KNOBS:                                           # read-only knobs, never re-set
        assert not re.search(r'os\.environ\[\s*"%s"\s*\]\s*=(?!=)' % knob, everything)
    assert everything.count('"BIOHUB_SECONDARY_ARTIFACT_MANIFEST"') == 1   # x138's own env read (cell 3)
    assert "BIOHUB_SECONDARY_EXPECTED_SHA256" not in everything


def test_finals_and_ladder_rebuild_byte_identical():
    tmp = "_pytest_secswap_rebuild"
    try:
        for name, (args, sha) in BUILDS.items():
            r = _build(name, f"{tmp}/{name}", *args)
            assert r.returncode == 0, (name, r.stderr[-500:])
            nb = ROOT / "experiments" / tmp / name / (name.replace("_", "-") + ".ipynb")
            assert hashlib.sha256(nb.read_bytes()).hexdigest() == sha, name
            committed = ROOT / "experiments" / name
            if committed.is_dir():
                assert nb.read_bytes() == (committed / nb.name).read_bytes(), name
                assert (nb.parent / "kernel-metadata.json").read_bytes() == \
                    (committed / "kernel-metadata.json").read_bytes(), name
    finally:
        shutil.rmtree(ROOT / "experiments" / tmp, ignore_errors=True)


def test_k2_secswap_differs_from_k2_only_by_knob_lines_and_the_sha_line():
    tmp = "_pytest_secswap_k2"
    name = "exp58_x138_safe_lowref"  # same name: the override header is the same line in both
    try:
        r = _build(name, f"{tmp}/k2", *K2_ARGS)
        assert r.returncode == 0, r.stderr[-500:]
        r = _build(name, f"{tmp}/sw", *K2_ARGS, *SECSWAP)
        assert r.returncode == 0, r.stderr[-500:]
        d = ROOT / "experiments" / tmp
        nb_name = name.replace("_", "-") + ".ipynb"
        assert hashlib.sha256((d / "k2" / nb_name).read_bytes()).hexdigest() == BUILDS[name][1]
        nb_k2 = json.loads((d / "k2" / nb_name).read_text(encoding="utf-8"))
        nb_sw = json.loads((d / "sw" / nb_name).read_text(encoding="utf-8"))
        assert nb_k2["metadata"] == nb_sw["metadata"]
        assert [(c.get("id"), c["cell_type"]) for c in nb_k2["cells"]] == [(c.get("id"), c["cell_type"])
                                                                            for c in nb_sw["cells"]]
        a, b = _code(d / "k2" / nb_name), _code(d / "sw" / nb_name)
        assert len(a) == len(b) == 14
        sec = X138["secondary"]  # no new cell is inserted before cell 3 by divinsert / lowrefine / safetail
        assert [i for i in range(len(a)) if a[i] != b[i]] == [0, sec]
        # cell 0: exactly the two knob lines, inserted after the K2 --set lines and before the builder's defaults
        la, lb = a[0].splitlines(), b[0].splitlines()
        knobs = [f'os.environ["BIOHUB_SECONDARY_EXPECTED_SHA256"] = "{NEW_SHA}"',
                 f'os.environ["BIOHUB_SECONDARY_ARTIFACT_MANIFEST"] = "{MANIFEST}"']
        i = lb.index(knobs[0])
        assert lb[i:i + 2] == knobs and lb[:i] + lb[i + 2:] == la
        assert la[i - 1] == 'os.environ["BIOHUB_LOWREFINE_ENABLE"] = "1"'
        # cell 3: the one replaced line
        la, lb = a[sec].splitlines(keepends=True), b[sec].splitlines(keepends=True)
        assert len(la) == len(lb)
        assert [(x, y) for x, y in zip(la, lb) if x != y] == [(bpk.SECSWAP_SHA_ANCHOR, bpk.SECSWAP_SHA_NEW)]
        # metadata: K2's datasets (pilkwang's seed314159 kept, harmless) + ours; probe
        m_k2 = json.loads((d / "k2" / "kernel-metadata.json").read_text(encoding="utf-8"))
        m_sw = json.loads((d / "sw" / "kernel-metadata.json").read_text(encoding="utf-8"))
        assert m_sw["dataset_sources"] == m_k2["dataset_sources"] + [DATASET]
        assert "pilkwang/biohub-temporal-unet3d-seed314159-v1" in m_sw["dataset_sources"]
        assert {k: v for k, v in m_sw.items() if k != "dataset_sources"} == \
            {k: v for k, v in m_k2.items() if k != "dataset_sources"}
        assert m_sw["enable_internet"] is False
        probe = json.loads((d / "sw" / "probe.json").read_text(encoding="utf-8"))
        assert "lab" not in probe and probe["change"]["PATCHES"] == "divinsert+lowrefine+secswap+safetail"
        assert probe["change"]["SECONDARY_EXPECTED_SHA256"] == NEW_SHA
        assert probe["change"]["SECONDARY_ARTIFACT_MANIFEST"] == MANIFEST
    finally:
        shutil.rmtree(ROOT / "experiments" / tmp, ignore_errors=True)


_MAN = "SECONDARY_ARTIFACT_MANIFEST="
_SHA = "SECONDARY_EXPECTED_SHA256="
_SW = ["--base", "x138", "--patch", "secswap"]


@pytest.mark.parametrize("args,msg", [
    # either knob without the patch: x138 would silently keep pilkwang's secondary
    (["--base", "x138", "--set", _SHA + NEW_SHA], "need --patch secswap"),
    (["--base", "x138", "--set", _MAN + MANIFEST, "--dataset", DATASET], "need --patch secswap"),
    ([*K2_ARGS, "--set", _SHA + NEW_SHA, "--set", _MAN + MANIFEST, "--dataset", DATASET], "need --patch secswap"),
    (["--set", _MAN + MANIFEST], "need --patch secswap"),                                          # exp39 base
    # the patch needs both knobs
    ([*_SW, "--dataset", DATASET], "needs --set SECONDARY_EXPECTED_SHA256=... and --set SECONDARY_ARTIFACT_MANIFEST"),
    ([*_SW, "--set", _MAN + MANIFEST, "--dataset", DATASET], "needs --set SECONDARY_EXPECTED_SHA256=..."),
    ([*_SW, "--set", _SHA + NEW_SHA, "--dataset", DATASET], "needs --set SECONDARY_ARTIFACT_MANIFEST=..."),
    ([*_SW, "--set", _SHA, "--set", _MAN + MANIFEST, "--dataset", DATASET], "needs --set SECONDARY_EXPECTED_SHA256"),
    # sha: 64 lowercase hex, not the parent
    ([*_SW, "--set", _SHA + NEW_SHA[:-1], "--set", _MAN + MANIFEST, "--dataset", DATASET], "64 lowercase hex"),
    ([*_SW, "--set", _SHA + NEW_SHA.upper(), "--set", _MAN + MANIFEST, "--dataset", DATASET], "64 lowercase hex"),
    ([*_SW, "--set", _SHA + "g" * 64, "--set", _MAN + MANIFEST, "--dataset", DATASET], "64 lowercase hex"),
    ([*_SW, "--set", _SHA + PARENT, "--set", _MAN + MANIFEST, "--dataset", DATASET], "parent (pilkwang seed314159)"),
    # manifest: a plain /kaggle/input/.../ARTIFACT_MANIFEST.json path (Git Bash's MSYS rewrite of /kaggle/... too)
    ([*_SW, "--set", _SHA + NEW_SHA, "--set", _MAN + "C:/Program Files/Git" + MANIFEST, "--dataset", DATASET],
     "plain /kaggle/input/"),
    ([*_SW, "--set", _SHA + NEW_SHA, "--set", _MAN + MANIFEST.replace("/input/", "/working/"), "--dataset", DATASET],
     "plain /kaggle/input/"),
    ([*_SW, "--set", _SHA + NEW_SHA, "--set", _MAN + MANIFEST.lstrip("/"), "--dataset", DATASET],
     "plain /kaggle/input/"),
    ([*_SW, "--set", _SHA + NEW_SHA, "--set", _MAN + MANIFEST.replace("datasets/", "datasets/../"),
      "--dataset", DATASET], "plain /kaggle/input/"),
    ([*_SW, "--set", _SHA + NEW_SHA, "--set", _MAN + MANIFEST.replace("ARTIFACT_MANIFEST.json", "manifest.json"),
      "--dataset", DATASET], "plain /kaggle/input/"),
    ([*_SW, "--set", _SHA + NEW_SHA, "--set", _MAN + "/kaggle/input/ARTIFACT_MANIFEST.json", "--dataset", DATASET],
     "plain /kaggle/input/"),
    # at least one --dataset, and the manifest lies inside one of them
    ([*_SW, "--set", _SHA + NEW_SHA, "--set", _MAN + MANIFEST], "needs --dataset"),
    ([*_SW, "--set", _SHA + NEW_SHA, "--set", _MAN + MANIFEST, "--dataset", "vitaliineibauer/biohub-secft-44b6-v1"],
     "is not inside any --dataset"),
    # base: x138 only
    (["--patch", "secswap", "--set", _SHA + NEW_SHA, "--set", _MAN + MANIFEST, "--dataset", DATASET],
     "needs --base x138"),
    # knobs x138 re-sets after the override block: a --set would be silently overwritten
    (["--base", "x138", "--set", "SECONDARY_DETECTION_WEIGHT=0.7"], "silently"),
    ([*K2_ARGS, "--set", "SECONDARY_EDGE_WEIGHT=0.2"], "silently"),
    ([*K2_ARGS, *SECSWAP, "--set", "DUAL_SEED_EDGE_THRESHOLD=0.5"], "silently"),
    (["--base", "x138", "--set", "DUAL_SEED_MIN_CANDIDATE_RETENTION=0.8"], "silently"),
])
def test_builder_refusals(args, msg):
    tmp = "_pytest_secswap_refusal"
    try:
        r = _build("zz_secswap_refusal", tmp, *args)
        assert r.returncode != 0 and msg in r.stderr, (args, r.stderr[-400:])
        assert not (ROOT / "experiments" / tmp).exists()
    finally:
        shutil.rmtree(ROOT / "experiments" / tmp, ignore_errors=True)


# ---------------------------------------------------------------- runtime: x138's own secondary block

_BLOCK_START = "import hashlib as _hashlib\n"
_BLOCK_END = "_runtime_integrity_receipt = {"
_ENV_WRITTEN = ("BIOHUB_SECONDARY_WEIGHTS", "BIOHUB_SECONDARY_EDGE_WEIGHT", "BIOHUB_SECONDARY_DETECTION_WEIGHT",
                "BIOHUB_SECONDARY_LINK_MODE", "BIOHUB_SECONDARY_MIX_TEMPERATURE", "BIOHUB_SECONDARY_LOW_MARGIN_MAX",
                "BIOHUB_DUAL_SEED_EDGE_THRESHOLD")


def _secondary_block(c3: str) -> str:
    assert c3.count(_BLOCK_START) == 1 and c3.count(_BLOCK_END) == 1
    return c3[c3.index(_BLOCK_START):c3.index(_BLOCK_END)]


def _x138_helpers(c3: str) -> dict:
    """x138's own remove_path + copy_or_extract_tree (cell 3), exec'd with their imports."""
    tree = ast.parse(c3)
    src = "\n\n".join(ast.get_source_segment(c3, n) for n in tree.body
                      if isinstance(n, ast.FunctionDef) and n.name in ("remove_path", "copy_or_extract_tree"))
    ns = {"Path": Path, "shutil": shutil, "zipfile": zipfile}
    exec(compile(src, "x138_cell3_helpers", "exec"), ns)
    assert {"remove_path", "copy_or_extract_tree"} <= set(ns)
    return ns


def _dataset(root: Path, weights: bytes, manifest_sha: str, as_zip: bool = False) -> Path:
    """Our dataset layout: ARTIFACT_MANIFEST.json (model.weight_sha256) + weights/ (or weights.zip)."""
    rel = "unet_transformer/split_0/"
    root.mkdir(parents=True)
    if as_zip:
        with zipfile.ZipFile(root / "weights.zip", "w") as zf:
            zf.writestr(rel + "edge_predictor_best.pth", weights)
            zf.writestr(rel + "config.json", "{}")
    else:
        (root / "weights" / rel).mkdir(parents=True)
        (root / "weights" / rel / "edge_predictor_best.pth").write_bytes(weights)
        (root / "weights" / rel / "config.json").write_text("{}")
    man = root / "ARTIFACT_MANIFEST.json"
    man.write_text(json.dumps({"artifact_name": root.name, "model": {"weight_sha256": manifest_sha}}))
    return man


def _run_block(c3: str, tmp: Path, monkeypatch, env: dict) -> dict:
    for k in _ENV_WRITTEN:  # monkeypatch restores every key the block writes
        monkeypatch.setenv(k, "unset-by-test")
    for k in bpk.SECSWAP_KNOBS:
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    ns = {"Path": Path, "os": os, "json": json, "WORKING_DIR": tmp / "working", **_x138_helpers(c3)}
    (tmp / "working").mkdir(exist_ok=True)
    exec(compile(_secondary_block(c3), "x138_cell3_secondary", "exec"), ns)
    return ns


pytestmark_runtime = pytest.mark.skipif(Path("/kaggle/input").exists(),
                                        reason="a real /kaggle/input would trigger x138's rglob walk")


@pytestmark_runtime
@pytest.mark.parametrize("as_zip", [False, True])
def test_runtime_swap_loads_our_secondary_and_logs_it(tmp_path, monkeypatch, capsys, as_zip):
    weights = b"secswap-test-weights"
    sha = hashlib.sha256(weights).hexdigest()
    man = _dataset(tmp_path / "biohub-secft-all-v1", weights, sha, as_zip=as_zip)
    c3 = _patched("secswap")[X138["secondary"]]
    # the knob tolerates stray whitespace / upper case (the builder only ever writes 64 lowercase hex)
    ns = _run_block(c3, tmp_path, monkeypatch, {"BIOHUB_SECONDARY_EXPECTED_SHA256": f" {sha.upper()} ",
                                                "BIOHUB_SECONDARY_ARTIFACT_MANIFEST": str(man)})
    out = capsys.readouterr().out
    assert f"Secondary artifact: {man.parent}\n" in out
    assert f"Secondary SHA256: {sha}\n" in out
    assert PARENT not in out
    assert ns["_secondary_expected_sha256"] == sha and ns["_secondary_actual_sha256"] == sha
    assert ns["SECONDARY_ARTIFACTS"] == man.parent
    w = tmp_path / "working" / "secondary_seed_weights" / "unet_transformer" / "split_0" / "edge_predictor_best.pth"
    assert os.environ["BIOHUB_SECONDARY_WEIGHTS"] == str(w) and w.read_bytes() == weights
    # the fusion knobs stay x138's (hard-set right after the load)
    assert os.environ["BIOHUB_SECONDARY_EDGE_WEIGHT"] == "0.15"
    assert os.environ["BIOHUB_SECONDARY_DETECTION_WEIGHT"] == "0.80"


@pytestmark_runtime
def test_runtime_fails_loud_never_silent(tmp_path, monkeypatch):
    weights = b"secswap-test-weights"
    sha = hashlib.sha256(weights).hexdigest()
    base_c3 = _x138_cells()[X138["secondary"]]
    c3 = _patched("secswap")[X138["secondary"]]
    man = _dataset(tmp_path / "ok", weights, sha)
    # knob unset -> the default is the parent sha: our manifest is skipped exactly as in x138
    with pytest.raises(FileNotFoundError, match=PARENT):
        _run_block(c3, tmp_path, monkeypatch, {"BIOHUB_SECONDARY_ARTIFACT_MANIFEST": str(man)})
    # unpatched x138 with only the manifest knob: skipped too (on Kaggle the rglob then finds pilkwang's = silent K2)
    with pytest.raises(FileNotFoundError, match=PARENT):
        _run_block(base_c3, tmp_path, monkeypatch, {"BIOHUB_SECONDARY_ARTIFACT_MANIFEST": str(man)})
    # a manifest for other weights is never accepted
    man_other = _dataset(tmp_path / "other", weights, hashlib.sha256(b"x").hexdigest())
    with pytest.raises(FileNotFoundError, match=sha):
        _run_block(c3, tmp_path, monkeypatch, {"BIOHUB_SECONDARY_EXPECTED_SHA256": sha,
                                               "BIOHUB_SECONDARY_ARTIFACT_MANIFEST": str(man_other)})
    # manifest claims the sha but the weights file differs -> x138's checksum RuntimeError
    man_bad = _dataset(tmp_path / "bad", b"corrupted", sha)
    with pytest.raises(RuntimeError, match="Secondary model checksum mismatch"):
        _run_block(c3, tmp_path, monkeypatch, {"BIOHUB_SECONDARY_EXPECTED_SHA256": sha,
                                               "BIOHUB_SECONDARY_ARTIFACT_MANIFEST": str(man_bad)})
