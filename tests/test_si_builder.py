"""--base succ in tools/build_probe_kernel.py (E10 v3 (B): a pulled public x138-family successor + our insertion = SI).

    python -m pytest tests/test_si_builder.py

Checks: the x138 notebook used as a pulled successor gives the committed K2 / K1 / exp70b notebooks except the one cell-0
tag line; the metadata is sanitised per E10 P4b(a); probe.json and the tag record the base sha256; the anchor audit
refuses mutants (duplicated anchor, moved cell, missing anchor, a stage after the insertion point, a re-assigned knob,
our own code already in the base, a lowrefine anchor after the V1284 block) with every failing anchor listed and no
output folder; a changed config-cell knob still builds; the real pulled successors apply or refuse as recorded; the
finals and ladder rebuilds stay byte-identical (exp70g / j / k here; the others in tests/test_secswap.py).
"""
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.build_probe_kernel as bpk  # noqa: E402

BUILDER = str(ROOT / "tools" / "build_probe_kernel.py")
E = ROOT / "experiments"
X138_NB = E / "ext_x138" / "biohub-x138.ipynb"
X138_META = E / "ext_x138" / "kernel-metadata.json"
X138_SHA = "6b655e39bbfd2d3d6c762badea69847d3f00f5b548f385cb01b07ee2600fde6d"
HF_NB = E / "ext_biohub-harmonic-fusion-v3" / "biohub-harmonic-fusion-v3.ipynb"
HF_META = E / "ext_biohub-harmonic-fusion-v3" / "kernel-metadata.json"
AM_OLD = (E / "ext_optimized-biohub-max-score" / "optimized-biohub-max-score.ipynb",
          E / "ext_optimized-biohub-max-score" / "kernel-metadata.json")
AM_V10 = (E / "ext_optimized-biohub-max-score" / "v10_2026-09-26" / "optimized-biohub-max-score.ipynb",
          E / "ext_optimized-biohub-max-score" / "v10_2026-09-26" / "kernel-metadata.json")
AM_V6 = (E / "ext_optimized-biohub-max-score" / "v6_2026-09-27" / "optimized-biohub-max-score.ipynb",
         E / "ext_optimized-biohub-max-score" / "v6_2026-09-27" / "kernel-metadata.json")
TMP = "_pytest_si_builder"

K = ["--set", "DIVINS_ENABLE=1", "--set", "DIVINS_STEAL=1", "--set", "DIVINS_CAP=4", "--set", "DIVINS_FRAME_CAP=1",
     "--set", "DIVINS_ALPHA=1", "--set", "DIVINS_THRESH=0.4", "--set", "DIVINS_DUMP=0"]
T = ["--set", "REPAIR_DEADLINE_S=34200", "--set", "DIVINS_DEADLINE_S=28800"]
P = ["--patch", "divinsert", "--patch", "safetail", "--patch", "lowrefine"]
K2 = [*P, *K, *T, "--set", "LOWREFINE_ENABLE=1"]
K1 = [*P, *K, *T, "--set", "LOWREFINE_ENABLE=0"]
REFS = {  # recipe -> committed x138 build it must reproduce (modulo the tag line)
    "k2": (K2, "exp58_x138_safe_lowref", "1f1ddb6d63b47f540ad614232e821ad215f27fce0d901cdbb9f67a8beeb67855"),
    "k1": (K1, "exp58t_x138_safe", "a77bcd6bad527e7bd5c01cbde2147b5169c3c4b51a1507cc0c34276af8dd2b03"),
    "fm": ([*K2, "--patch", "forkmid", "--set", "FORKMID_ENABLE=1"], "exp70b_k2_fm45",
           "b8e7ece1a33cd2a184c2fd199700c1cd8320fde170f28a139265f76babd8b911"),
}
TAG = "probe overrides (tools/build_probe_kernel.py"


@pytest.fixture(scope="module", autouse=True)
def _cleanup():
    yield
    shutil.rmtree(E / TMP, ignore_errors=True)


def _nokaggle_env() -> dict:
    """(review_si_builder_0) the builder subprocess env with a shadow `kaggle` package first on PYTHONPATH and no Kaggle
    token env: if a --push refusal ever regressed, `python -m kaggle kernels push` exits here instead of pushing."""
    shadow = E / TMP / "_nokaggle" / "kaggle"
    if not (shadow / "__main__.py").is_file():
        shadow.mkdir(parents=True, exist_ok=True)
        (shadow / "__init__.py").write_text("", encoding="utf-8")
        (shadow / "__main__.py").write_text('raise SystemExit("kaggle blocked by tests/test_si_builder.py: never push")\n',
                                            encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if not k.startswith("KAGGLE_")}
    env["PYTHONPATH"] = str(shadow.parent) + (os.pathsep + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else "")
    return env


def _build(name: str, out: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, BUILDER, name, "--out-dir", f"{TMP}/{out}", *args], capture_output=True,
                          text=True, cwd=str(ROOT), env=_nokaggle_env())


def _succ(nb: Path, meta: Path) -> list:
    return ["--base", "succ", "--base-ipynb", str(nb), "--base-meta", str(meta)]


def _out(out: str, name: str) -> Path:
    return E / TMP / out / (name.replace("_", "-") + ".ipynb")


def _code(nb) -> list:
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def _x138_cells() -> dict:
    return dict(enumerate(_code(json.loads(X138_NB.read_text(encoding="utf-8")))))


def _audit(cells: dict, patches=("divinsert", "safetail", "lowrefine"), knobs=("REPAIR_DEADLINE_S",)):
    return bpk.succ_anchor_audit(cells, list(patches), list(knobs))


def _pulled(tmp: Path, mutate=None, meta_mutate=None, fname: str = "biohub-x138.ipynb") -> tuple[Path, Path]:
    """A pulled-successor folder made from x138 with its code cells mutated (compact Kaggle JSON, like a pull)."""
    nb = json.loads(X138_NB.read_text(encoding="utf-8"))
    code = [c for c in nb["cells"] if c["cell_type"] == "code"]
    if mutate:
        srcs = mutate({k: c["source"] for k, c in enumerate(code)})
        assert sorted(srcs) == list(range(len(code)))                        # mutators keep the cell count
        for k, c in enumerate(code):
            c["source"] = srcs[k]
    meta = json.loads(X138_META.read_text(encoding="utf-8"))
    meta["code_file"] = fname
    if meta_mutate:
        meta_mutate(meta)
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / fname).write_bytes(json.dumps(nb, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    (tmp / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return tmp / fname, tmp / "kernel-metadata.json"


# ---------------------------------------------------------------- x138 as the successor = the committed builds

@pytest.mark.parametrize("recipe", sorted(REFS))
def test_x138_as_successor_reproduces_committed_build_modulo_tag_line(recipe):
    args, ref, ref_sha = REFS[recipe]
    name = f"exp73_si_anvithpothula_{recipe}"
    r = _build(name, recipe, *_succ(X138_NB, X138_META), *args)
    assert r.returncode == 0, r.stderr[-800:]
    built = json.loads(_out(recipe, name).read_text(encoding="utf-8"))
    ref_path = E / ref / (ref.replace("_", "-") + ".ipynb")
    assert hashlib.sha256(ref_path.read_bytes()).hexdigest() == ref_sha
    ref_nb = json.loads(ref_path.read_text(encoding="utf-8"))
    a, b = _code(built), _code(ref_nb)
    assert len(a) == len(b)
    diff = [(i, x, y) for i, (sa, sb) in enumerate(zip(a, b)) for x, y in zip(sa.splitlines(), sb.splitlines()) if x != y]
    assert [(i, TAG in x, TAG in y) for i, x, y in diff] == [(0, True, True)]      # one line, the cell-0 tag
    assert diff[0][1] == (f"# ---- {name}: probe overrides (tools/build_probe_kernel.py --base succ "
                          f"anvithpothula/biohub-x138 sha256={X138_SHA}) ----")
    assert diff[0][2] == f"# ---- {ref}: probe overrides (tools/build_probe_kernel.py --base x138) ----"
    # swapping that one line back gives the committed file byte for byte (ids, metadata, serialisation)
    c0 = next(c for c in built["cells"] if c["cell_type"] == "code")
    assert c0["source"].count(diff[0][1]) == 1
    c0["source"] = c0["source"].replace(diff[0][1], diff[0][2])
    assert json.dumps(built, separators=(",", ":"), ensure_ascii=False).encode("utf-8") == ref_path.read_bytes()


def test_metadata_sanitised_per_p4b_and_probe_records_base_sha():
    name = "exp73_si_anvithpothula"
    r = _build(name, "meta", *_succ(X138_NB, X138_META), *K1)
    assert r.returncode == 0, r.stderr[-800:]
    d = E / TMP / "meta"
    meta = json.loads((d / "kernel-metadata.json").read_text(encoding="utf-8"))
    pulled = json.loads(X138_META.read_text(encoding="utf-8"))
    assert meta["id"] == "vitaliineibauer/biohub-exp73-si-anvithpothula"
    assert meta["title"] == "biohub-exp73-si-anvithpothula" != pulled["title"]
    assert meta["code_file"] == "exp73-si-anvithpothula.ipynb"
    assert meta["is_private"] is True and meta["enable_internet"] is False and "id_no" not in meta
    assert pulled["is_private"] is False and "id_no" in pulled
    for k in ("docker_image", "machine_shape", "enable_gpu", "kernel_sources", "competition_sources", "model_sources",
              "language", "kernel_type", "keywords", "enable_tpu"):
        assert meta[k] == pulled[k], k
    assert meta["dataset_sources"] == pulled["dataset_sources"] + [bpk.WEIGHTS_DATASET]
    assert list(meta) == [k for k in pulled if k != "id_no"]
    # same fields as the committed K1 metadata except id / title / code_file
    k1 = json.loads((E / "exp58t_x138_safe" / "kernel-metadata.json").read_text(encoding="utf-8"))
    assert list(meta) == list(k1) and sorted(k for k in meta if meta[k] != k1[k]) == ["code_file", "id", "title"]
    probe = json.loads((d / "probe.json").read_text(encoding="utf-8"))
    assert probe["base_sha256"] == X138_SHA == probe["succ"]["ipynb_sha256"]
    assert probe["succ"]["ref"] == "anvithpothula/biohub-x138" and probe["succ"]["serial"] == "compact"
    assert probe["succ"]["meta_sha256"] == hashlib.sha256(X138_META.read_bytes()).hexdigest()
    assert X138_SHA in probe["base"] and "E10 v3 (B)" in probe["rule"]
    assert probe["change"]["PATCHES"] == "divinsert+lowrefine+safetail"
    assert probe["succ"]["anchors"] and all(l.startswith(("OK   ", "INFO ")) for l in probe["succ"]["anchors"])
    assert f"sha256={X138_SHA}" in _code(json.loads(_out("meta", name).read_text(encoding="utf-8")))[0]
    # the pinned sha is accepted, a wrong one refuses
    ok = _build(name, "meta_pin", *_succ(X138_NB, X138_META), "--base-sha256", X138_SHA, *K1)
    assert ok.returncode == 0, ok.stderr[-500:]
    bad = _build(name, "meta_badpin", *_succ(X138_NB, X138_META), "--base-sha256", "0" * 64, *K1)
    assert bad.returncode != 0 and "--base-sha256" in bad.stderr and not (E / TMP / "meta_badpin").exists()


# ---------------------------------------------------------------- anchor audit (in memory)

def test_audit_passes_x138_with_every_supported_patch():
    report, fails = _audit(_x138_cells(), bpk.SUCC_PATCHES)
    assert fails == [] and report
    labels = {bpk.SUCC_ANCHORS[i][3] for i in range(len(bpk.SUCC_ANCHORS))}
    assert len(labels) >= 30


def test_audit_refuses_duplicated_anchor():
    cells = _x138_cells()
    cells[5] = cells[5] + "\n" + bpk.SAFETAIL_DEGRADE_OLD                  # a second copy in the same cell
    _, fails = _audit(cells)
    assert len(fails) == 1 and "x138 deadline-degrade block" in fails[0] and "{5: 2}" in fails[0]
    cells = _x138_cells()
    cells[9] = cells[9] + "\n" + bpk._LP_LINEFIT_CALL                       # a copy in another cell
    _, fails = _audit(cells)
    assert fails and all("{5: 1, 9: 1}" in f for f in fails)
    assert {f.split("] ")[1].split(" (cell")[0] for f in fails} == {"linefit call (insertion point)"}


def test_audit_refuses_moved_cell():
    cells = _x138_cells()
    cells[4], cells[5] = cells[5], cells[4]                                  # predict and post swapped
    _, fails = _audit(cells)
    text = "\n".join(fails)
    assert "found {4: 1}" in text                                             # post anchors now in cell 4
    for label in ("post cell: def filter_output_graph(", "linefit call (insertion point)", "FINAL print",
                  "lowdet globals literal", "x138 deadline-degrade block", "[knob] REPAIR_DEADLINE_S"):
        assert label in text, label
    orig = _x138_cells()                                                     # the post cell moved to the end
    cells = dict(enumerate(orig[k] for k in [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 5]))
    _, fails = _audit(cells)
    assert fails and any("found {11: 1}" in f for f in fails) and not any("lowdet" in f for f in fails)


def test_audit_refuses_missing_anchor():
    for patch, text, label in (("safetail", bpk.SAFETAIL_DEGRADE_OLD, "x138 deadline-degrade block"),
                               ("lowrefine", bpk.LOWREFINE_CAST_ANCHOR, "lowdet int16 cast literal"),
                               ("divinsert", bpk._SUCC_GAP2_ANCHOR, "gap2 node dict end")):
        cells = _x138_cells()
        cell = next(k for k, s in cells.items() if text in s)
        cells[cell] = cells[cell].replace(text, "")
        _, fails = _audit(cells, (patch,), ())
        assert fails and label in fails[0] and "found nowhere" in fails[0], (patch, fails)


def test_audit_refuses_stage_between_insertion_and_final_print():
    cells = _x138_cells()
    stage = "    edges = successor_new_stage(nodes_by_id, edges)\n"
    cells[5] = cells[5].replace(bpk._LP_LINEFIT_CALL, bpk._LP_LINEFIT_CALL + stage)
    _, fails = _audit(cells)
    assert len(fails) == 1 and "no stage after the insertion" in fails[0]


def test_audit_refuses_reassigned_knob_and_our_code_in_base():
    cells = _x138_cells()
    cells[10] += '\nos.environ["BIOHUB_REPAIR_DEADLINE_S"] = "30600"\n'   # amanatar v10's pass-2 pattern
    _, fails = _audit(cells)
    assert len(fails) == 1 and "[knob] REPAIR_DEADLINE_S" in fails[0] and "{10: 1}" in fails[0]
    cells = _x138_cells()
    cells[2] += '\nX = os.environ.get("BIOHUB_DIVINS_ENABLE", "0")\n'
    _, fails = _audit(cells)
    assert len(fails) == 1 and "no BIOHUB_DIVINS_ knob in the base" in fails[0]
    cells = _x138_cells()                                                    # knob check only for knobs we --set
    cells[10] += '\nos.environ["BIOHUB_REPAIR_DEADLINE_S"] = "30600"\n'
    assert _audit(cells, ("divinsert",), ())[1] == []


def test_audit_refuses_lowrefine_anchor_after_v1284_block():
    cells = _x138_cells()
    c = cells[4]
    a = bpk.LOWREFINE_PRINT_ANCHOR
    cells[4] = c.replace(a, "") + "\n# " + a + "\n"
    _, fails = _audit(cells, ("lowrefine",), ())
    assert len(fails) == 1 and "LOWDET per-video print literal" in fails[0] and "V1284" in fails[0]


def test_audit_structure_too_few_cells():
    cells = {k: v for k, v in _x138_cells().items() if k < 4}
    _, fails = _audit(cells)
    assert len(fails) == 1 and "[structure]" in fails[0]


# ---------------------------------------------------------------- refusals end to end (no output folder)

def _refused(r: subprocess.CompletedProcess, out: str, *needles: str) -> str:
    assert r.returncode != 0, r.stdout[-300:]
    for n in needles:
        assert n in r.stderr, (n, r.stderr[-800:])
    assert not (E / TMP / out).exists()
    return r.stderr


def test_builder_refuses_mutants_listing_every_failing_anchor(tmp_path):
    def dup(c):
        c[5] = c[5] + "\n" + bpk.SAFETAIL_DEGRADE_OLD
        return c

    def moved(c):
        c[4], c[5] = c[5], c[4]
        return c

    def missing(c):
        c[4] = c[4].replace(bpk.LOWREFINE_GLOBALS_ANCHOR, "")
        c[5] = c[5].replace(bpk._FM_FINAL_PRINT, "")
        return c

    for tag, fn, needles in (("dup", dup, ["1 anchor check(s) failed", "x138 deadline-degrade block", "{5: 2}"]),
                             ("moved", moved, ["def filter_output_graph(", "found {4: 1}", "[knob] REPAIR_DEADLINE_S"]),
                             ("missing", missing, ["lowdet globals literal", "FINAL print",
                                                   "no stage after the insertion"])):
        nb, meta = _pulled(tmp_path / tag, fn)
        r = _build("exp73_si_anvithpothula", f"mut_{tag}", *_succ(nb, meta), *K2)
        err = _refused(r, f"mut_{tag}", "--base succ REFUSED", *needles)
        assert err.count("\n  FAIL ") + err.startswith("  FAIL ") >= 1


def test_changed_config_knob_still_builds(tmp_path):
    def knob(c):
        old = 'os.environ["BIOHUB_DET_THRESHOLD"] = "0.965"'
        assert c[0].count(old) == 1
        c[0] = c[0].replace(old, 'os.environ["BIOHUB_DET_THRESHOLD"] = "0.960"')
        old = 'OUTPUT_LINEFIT_WINDOW = int(os.environ.get("BIOHUB_OUTPUT_LINEFIT_WINDOW", "2"))'
        assert c[2].count(old) == 1
        c[2] = c[2].replace(old, old.replace('"2"', '"3"'))
        return c

    nb, meta = _pulled(tmp_path / "knob", knob)
    r = _build("exp73_si_anvithpothula_knob", "knob", *_succ(nb, meta), *K1)
    assert r.returncode == 0, r.stderr[-800:]
    probe = json.loads((E / TMP / "knob" / "probe.json").read_text(encoding="utf-8"))
    info = [l for l in probe["succ"]["anchors"] if l.startswith("INFO [lowrefine]")]
    assert len(info) == 1 and "'DET_THRESHOLD': '0.960'" in info[0] and "prefer the K1 recipe" in info[0]
    assert "INFO [validator] cell 0 sets BIOHUB_VALIDATOR_ENABLE='0'" in probe["succ"]["anchors"]


def test_validator_on_is_reported_not_refused():
    cells = _x138_cells()
    old = 'os.environ["BIOHUB_VALIDATOR_ENABLE"] = "0"'
    assert cells[0].count(old) == 1
    cells[0] = cells[0].replace(old, 'os.environ["BIOHUB_VALIDATOR_ENABLE"] = "1"')
    report, fails = _audit(cells)
    assert fails == [] and any(l.startswith("INFO [validator]") and "NOT off" in l for l in report)
    cells = _x138_cells()
    cells[9] += '\nos.environ["BIOHUB_VALIDATOR_ENABLE"] = "1"\n'
    report, fails = _audit(cells)
    assert fails == [] and any("also assigned in code cells [9]" in l for l in report)


def test_builder_argument_refusals(tmp_path):
    nb, meta = _pulled(tmp_path / "ok")
    ok = _succ(nb, meta)
    cases = [
        ("noname", "exp73_si_someoneelse", [*ok, *K1], "the name must give the slug biohub-exp73[x]-si-anvithpothula"),
        ("token", "exp63_si_anvithpothula", [*ok, *K1], "the name must give the slug"),
        ("nodiv", "exp73_si_anvithpothula", [*ok, "--patch", "safetail", "--patch", "lowrefine", *T[:2],
                                             "--set", "LOWREFINE_ENABLE=1"], "--patch divinsert is required"),
        ("ds", "exp73_si_anvithpothula", [*ok, *K1, "--dataset", "a/b"], "no --dataset"),
        ("knob", "exp73_si_anvithpothula", [*ok, *K2, "--set", "DEEPCENTER_SAFE_DIV_THRESHOLD=0.30"],
         "accepts only --set"),
        ("patch", "exp73_si_anvithpothula", [*ok, *K1, "--patch", "secswap"], "supports only --patch"),
        ("rd", "exp73_si_anvithpothula", [*ok, "--patch", "divinsert", *K, "--set", "REPAIR_DEADLINE_S=34200"],
         "only with --patch safetail"),
        ("owner", "exp73_si_anvithpothula", [*ok, *K1, "--owner", "someone"], "--owner someone"),
        ("push", "exp73_si_anvithpothula", [*ok, *K1, "--push"], "no --push"),
        ("nometa", "exp73_si_anvithpothula", ["--base", "succ", "--base-ipynb", str(nb), *K1], "--base-meta"),
        ("x138", "exp58_x138_safe_lowref", ["--base", "x138", "--base-ipynb", str(nb), *K2], "need --base succ"),
        ("deadline", "exp73_si_anvithpothula", [*ok, *P, *K, "--set", "REPAIR_DEADLINE_S=30000"],
         "(REPAIR_DEADLINE_S, DIVINS_DEADLINE_S)"),
    ]
    for out, name, args, needle in cases:
        _refused(_build(name, f"arg_{out}", *args), f"arg_{out}", needle)
    for tag, mm, needle in (("blank", lambda m: m["dataset_sources"].append(""), "blank source"),
                            ("ks", lambda m: m.__setitem__("kernel_sources", ["x/y"]), "kernel_sources"),
                            ("nodocker", lambda m: m.pop("docker_image"), "docker_image"),
                            ("codefile", lambda m: m.__setitem__("code_file", "other.ipynb"), "code_file"),
                            ("ours", lambda m: m.__setitem__("id", "vitaliineibauer/biohub-exp58"), "our own kernels")):
        nb2, meta2 = _pulled(tmp_path / tag, meta_mutate=mm)
        _refused(_build("exp73_si_anvithpothula", f"meta_{tag}", *_succ(nb2, meta2), *K1), f"meta_{tag}", needle)


# ---------------------------------------------------------------- the real pulled successors

def _hunks(base: list, built: list) -> list:
    out = []
    for a, b in zip(base, built):
        la = a.splitlines()
        lb = [l for l in b.splitlines() if TAG not in l]
        out.append([(t, la[i1:i2], lb[j1:j2]) for t, i1, i2, j1, j2 in
                    difflib.SequenceMatcher(None, la, lb, autojunk=False).get_opcodes() if t != "equal"])
    return out


def _by_id(nb) -> dict:
    return {c["id"]: c["source"] for c in nb["cells"] if c["cell_type"] == "code"}


@pytest.mark.parametrize("which", ["hfv3", "amv6"])
def test_real_successor_si_equals_the_x138_to_k1_change(which):
    nbp, metap = {"hfv3": (HF_NB, HF_META), "amv6": AM_V6}[which]
    if not nbp.is_file():
        pytest.skip(f"{nbp} not in this checkout")
    author = json.loads(metap.read_text(encoding="utf-8"))["id"].split("/")[0]
    name = f"exp73_si_{author}"
    r = _build(name, f"real_{which}", *_succ(nbp, metap), *K1)
    assert r.returncode == 0, r.stderr[-800:]
    built = json.loads(_out(f"real_{which}", name).read_text(encoding="utf-8"))
    base = json.loads(nbp.read_text(encoding="utf-8"))
    ref = json.loads((E / "exp58t_x138_safe" / "exp58t-x138-safe.ipynb").read_text(encoding="utf-8"))
    x138 = json.loads(X138_NB.read_text(encoding="utf-8"))
    bb, bi = _by_id(base), _by_id(built)
    xb, xr = _by_id(x138), _by_id(ref)
    got = _hunks(list(bb.values()), [bi[k] for k in bb])
    want = _hunks(list(xb.values()), [xr[k] for k in xb])
    n = len(want)
    assert got[:n] == want and all(h == [] for h in got[n:])                  # hunk for hunk, cells 0 / 4 / 5 only
    assert [i for i, h in enumerate(got) if h] == [0, 4, 5]
    assert [s for k, s in bi.items() if k not in bb] == [s for k, s in xr.items() if k not in xb]  # the 2 new cells
    for i, s in enumerate(_code(built)):
        compile(s, f"cell{i}", "exec")


@pytest.mark.parametrize("pair", [AM_OLD, AM_V10], ids=["amanatar_old", "amanatar_v10"])
def test_amanatar_old_and_v10_refused_for_reassigned_deadline(pair):
    nbp, metap = pair
    if not nbp.is_file():
        pytest.skip(f"{nbp} not in this checkout")
    r = _build("exp73_si_amanatar", "real_am", *_succ(nbp, metap), *K1)
    err = _refused(r, "real_am", "--base succ REFUSED: 1 anchor check(s) failed", "[knob] REPAIR_DEADLINE_S",
                   "re-assigned after cell 0 in code cells {10: 1}")
    assert err.count("FAIL ") == 1


# ---------------------------------------------------------------- the x138 builds are unchanged

@pytest.mark.parametrize("name,extra,sha", [
    ("exp70g_k2_cap6", "cap6", "52c182a36a40faf9"),
    ("exp70j_k2_dc020", "dc020", "61a8d3c1be8a3aa2"),
    ("exp70k_k2_dc0225", "dc0225", "adef8bcbc3cd4f5b"),
])
def test_ladder_rebuilds_not_in_test_secswap_stay_byte_identical(name, extra, sha):
    if extra == "cap6":
        args = [*P, *[x.replace("DIVINS_CAP=4", "DIVINS_CAP=6") for x in K], *T, "--set", "LOWREFINE_ENABLE=1"]
    else:
        args = [*K2, "--set", "DEEPCENTER_SAFE_DIV_THRESHOLD=" + {"dc020": "0.20", "dc0225": "0.225"}[extra]]
    r = _build(name, f"ladder_{name}", "--base", "x138", *args)
    assert r.returncode == 0, r.stderr[-500:]
    got = _out(f"ladder_{name}", name).read_bytes()
    committed = E / name
    assert hashlib.sha256(got).hexdigest().startswith(sha[:16])
    assert got == (committed / (name.replace("_", "-") + ".ipynb")).read_bytes()
    assert (E / TMP / f"ladder_{name}" / "kernel-metadata.json").read_bytes() == \
        (committed / "kernel-metadata.json").read_bytes()


# ---------------------------------------------------------------- review_si_builder_1 hardening (27 Sep)

def test_audit_refuses_python_rebinding_and_indirect_env_write():
    cells = _x138_cells()
    cells[9] += "\nREPAIR_DEADLINE_S = 20000.0\n"                           # Python-level re-binding
    _, fails = _audit(cells)
    assert len(fails) == 1 and "[knob] REPAIR_DEADLINE_S" in fails[0] and "Python binding" in fails[0]
    cells = _x138_cells()
    cells[10] += '\nfor _k in ["BIOHUB_REPAIR_DEADLINE_S"]:\n    os.environ[_k] = "30600"\n'   # write via a variable
    _, fails = _audit(cells)
    assert len(fails) == 1 and "also named in code cells {10: 1}" in fails[0]
    cells = _x138_cells()
    cells[9] += "\nKERNEL_START_TS = _time.time()\n"                         # the insertion gate's clock reset
    _, fails = _audit(cells)
    assert len(fails) == 1 and "[knob] KERNEL_START_TS" in fails[0]
    cells = _x138_cells()
    cells[10] += '\nos.environ["BIOHUB_KERNEL_START_TS"] = str(time.time())\n'
    _, fails = _audit(cells)
    assert len(fails) == 1 and "[knob] KERNEL_START_TS" in fails[0] and "re-assigned after cell 0" in fails[0]
    assert _audit(cells, ("divinsert",), ())[1] == []                        # clock check only under safetail


def test_submission_si_needs_safetail_and_insertion_on(tmp_path):
    nb, meta = _pulled(tmp_path / "ok")
    ok = _succ(nb, meta)
    _refused(_build("exp73_si_anvithpothula", "h_nosafe", *ok, "--patch", "divinsert", *K), "h_nosafe",
             "needs --patch safetail")
    k_off = [x.replace("DIVINS_ENABLE=1", "DIVINS_ENABLE=0") for x in K]
    _refused(_build("exp73_si_anvithpothula", "h_off", *ok, *P, *k_off, *T, "--set", "LOWREFINE_ENABLE=0"), "h_off",
             "DIVINS_ENABLE is off")
    r = _build("exp73_si_anvithpothula_d1", "h_d1", *ok, "--patch", "divinsert", *K, "--lab")   # D1 dummy: lab only
    assert r.returncode == 0, r.stderr[-500:]
    assert "never submit" in json.loads((E / TMP / "h_d1" / "probe.json").read_text(encoding="utf-8"))["lab"]


def test_succ_build_never_overwrites_another_kernels_folder(tmp_path):
    nb, meta = _pulled(tmp_path / "ok")
    fake = E / TMP / "h_final"
    fake.mkdir(parents=True, exist_ok=True)
    km = json.dumps({"id": "vitaliineibauer/biohub-exp58-x138-safe-lowref"})
    (fake / "kernel-metadata.json").write_text(km, encoding="utf-8")
    r = _build("exp73_si_anvithpothula", "h_final", *_succ(nb, meta), *K1)
    assert r.returncode != 0 and "refusing to overwrite another kernel's folder" in r.stderr, r.stderr[-500:]
    assert sorted(p.name for p in fake.iterdir()) == ["kernel-metadata.json"]
    assert (fake / "kernel-metadata.json").read_text(encoding="utf-8") == km
    ok = _build("exp73_si_anvithpothula", "h_again", *_succ(nb, meta), *K1)     # a rebuild of the same kernel is fine
    assert ok.returncode == 0, ok.stderr[-500:]
    again = _build("exp73_si_anvithpothula", "h_again", *_succ(nb, meta), *K1)
    assert again.returncode == 0, again.stderr[-500:]


def test_builder_subprocesses_cannot_reach_kaggle():
    """(review_si_builder_0) every _build() runs with the shadow kaggle package: a regressed --push refusal cannot push."""
    r = subprocess.run([sys.executable, "-m", "kaggle", "kernels", "push", "-p", str(E / TMP)], capture_output=True,
                       text=True, cwd=str(ROOT), env=_nokaggle_env())
    assert r.returncode != 0 and "kaggle blocked by tests/test_si_builder.py" in r.stderr, (r.stdout, r.stderr)
