"""E10 v3 (user instruction 27 Sep 11:08 UTC): tools/e10_port_gate.py --mode verbatim / --mode si.

    python -m pytest tests/test_e10_port_gate_modes.py -q

verbatim = (A) a byte copy of a scored public notebook: the P4c(2)/(3) source checks are INFO, the dummy log FAILS only
on Traceback / 'REPAIR FAILED' / 'DEADLINE:'. si = (B) successor + our insertion: the SI notebook may differ from the
pulled successor only by our patch diff (= reference base -> reference build of the same recipe on x138).
Real fixtures: experiments/ext_x138, experiments/exp56_x138_verbatim, experiments/exp58t_x138_safe (K1 recipe on x138),
experiments/ext_optimized-biohub-max-score/v10_2026-09-26, experiments/exp63dry_hfv3 and the git-ignored _dl outputs.
A test whose fixture is absent is skipped. The default mode's own tests stay in tests/test_e10_port_gate.py.
"""
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.e10_port_gate as g  # noqa: E402

X138 = ROOT / "experiments" / "ext_x138"
EXP56 = ROOT / "experiments" / "exp56_x138_verbatim"
EXP58T = ROOT / "experiments" / "exp58t_x138_safe"
V10 = ROOT / "experiments" / "ext_optimized-biohub-max-score" / "v10_2026-09-26"
HFV3_PULLED = ROOT / "_dl" / "ext2_biohub-harmonic-fusion-v3"
HFV3_PORT = ROOT / "experiments" / "exp63dry_hfv3"
HFV3_DUMMY = ROOT / "_dl" / "exp63dry_hfv3_out"
HFV3_AUTHOR = ROOT / "_dl" / "hfv3_author_out"
DUMMY56 = ROOT / "_dl" / "biohub-exp56-x138-verbatim"
DUMMY58T = ROOT / "_dl" / "biohub-exp58t-x138-safe"
SI_ID = "vitaliineibauer/biohub-exp73-si-anvithpothula"
KNOB_OLD = 'OUTPUT_LINEFIT_WEIGHT = float(os.environ.get("BIOHUB_OUTPUT_LINEFIT_WEIGHT", "0.8"))'
KNOB_NEW = 'OUTPUT_LINEFIT_WEIGHT = float(os.environ.get("BIOHUB_OUTPUT_LINEFIT_WEIGHT", "0.7"))'


def need(*paths):
    for p in paths:
        if not p.exists():
            pytest.skip(f"fixture {p.relative_to(ROOT)} not present")


def fails(lines, group=None):
    return [ln for ln in lines if ln.status == g.FAIL and (group is None or ln.group == group)]


def one(lines, prefix):
    got = [ln for ln in lines if ln.msg.startswith(prefix)]
    assert len(got) == 1, [ln.msg for ln in lines]
    return got[0]


def edit_code(raw: bytes, edit) -> bytes:
    """Edit code-cell sources of a compact (Kaggle-export) notebook and write it back the builder's way."""
    nb = json.loads(raw.decode("utf-8"))
    edit(nb)
    return json.dumps(nb, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def replace_once(old, new):
    def edit(nb):
        hits = [c for c in nb["cells"] if old in c["source"]]
        assert len(hits) == 1 and hits[0]["source"].count(old) == 1, old
        hits[0]["source"] = hits[0]["source"].replace(old, new)
    return edit


# ------------------------------------------------------------------------------------------------------- verbatim

def make_copy_port(tmp_path, pulled, nb_edit=None, meta_edit=None, prefix="vitaliineibauer/biohub-exp63-succ-"):
    meta = json.loads((pulled / "kernel-metadata.json").read_text(encoding="utf-8"))
    author = meta["id"].split("/")[0]
    d = tmp_path / "port"
    d.mkdir()
    raw = (pulled / meta["code_file"]).read_bytes()
    meta.update(id=prefix + author, title=f"port {author}", is_private=True, enable_internet=False)
    meta.pop("id_no", None)
    for k in g.SOURCE_KEYS:
        meta[k] = [s for s in meta.get(k, []) if s.strip()]
    if meta_edit:
        meta_edit(meta)
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (d / meta["code_file"]).write_bytes(nb_edit(raw) if nb_edit else raw)
    return d


def test_verbatim_v10_source_failures_become_info(tmp_path):
    need(V10)
    port = make_copy_port(tmp_path, V10)
    default = g.run(V10, port, version=10)
    assert {ln.group for ln in fails(default)} == {"source"}          # the default gate still refuses amanatar v10
    lines = g.run(V10, port, version=10, mode="verbatim")
    assert not fails(lines), g.render(lines)
    assert g.group_status(lines, "source") == g.INFO
    assert g.group_status(lines, "notebook-bytes") == g.PASS
    v = one(lines, "[verbatim mode: would be FAIL] validator")
    d = one(lines, "[verbatim mode: would be FAIL] deadline")
    m = one(lines, "[verbatim mode: would be FAIL] sweep/rewrite markers")
    assert v.status == d.status == m.status == g.INFO
    assert "L121 " in v.msg and "L6583 " in d.msg and "30600" in d.msg


def test_verbatim_byte_change_still_fails(tmp_path):
    need(V10)
    port = make_copy_port(tmp_path, V10, nb_edit=lambda raw: raw.replace(b"30600", b"27000", 1))
    f = fails(g.run(V10, port, mode="verbatim"))
    assert len(f) == 1 and f[0].group == "notebook-bytes" and "byte-for-byte" in f[0].msg


@pytest.mark.parametrize("meta_edit, needle", [
    (lambda m: m.update(is_private=False), "port is_private"),
    (lambda m: m.update(enable_internet=True), "port enable_internet"),
    (lambda m: m.update(kernel_sources=["someone/cached"]), "port kernel_sources"),
    (lambda m: m.update(id="vitaliineibauer/biohub-exp73-si-amanatar"), "port id"),
])
def test_verbatim_metadata_rules_unchanged(tmp_path, meta_edit, needle):
    need(V10)
    port = make_copy_port(tmp_path, V10, meta_edit=meta_edit)
    f = fails(g.run(V10, port, mode="verbatim"))
    assert len(f) == 1 and f[0].msg.startswith(needle), [x.msg for x in f]


def test_verbatim_pulled_blank_source_or_kernel_source_fails(tmp_path):
    need(X138)
    for i, (key, val) in enumerate((("dataset_sources", [""]), ("kernel_sources", ["a/b"]))):
        d = tmp_path / f"pulled{i}"
        shutil.copytree(X138, d)
        meta = json.loads((d / "kernel-metadata.json").read_text(encoding="utf-8"))
        meta[key] = meta.get(key, []) + val
        (d / "kernel-metadata.json").write_text(json.dumps(meta), encoding="utf-8")
        f = fails(g.run(d, mode="verbatim"))
        assert len(f) == 1 and f[0].group == "metadata" and key in f[0].msg


def test_verbatim_unreadable_notebook_still_fails(tmp_path):
    d = tmp_path / "pulled"
    d.mkdir()
    (d / "kernel-metadata.json").write_text(json.dumps({"id": "a/b", "code_file": "nb.ipynb", "kernel_sources": []}),
                                            encoding="utf-8")
    (d / "nb.ipynb").write_text("{not json", encoding="utf-8")
    src = [ln for ln in g.run(d, mode="verbatim") if ln.group == "source"]
    assert any(ln.status == g.FAIL and ln.msg.startswith("cannot read the notebook") for ln in src)


def test_verbatim_hfv3_dry_run_full_gate(tmp_path):
    need(HFV3_PULLED, HFV3_PORT, HFV3_DUMMY, HFV3_AUTHOR)
    lines = g.run(HFV3_PULLED, HFV3_PORT, HFV3_DUMMY, HFV3_AUTHOR, version=3, mode="verbatim")
    assert not [ln for ln in lines if ln.status in (g.FAIL, g.SKIP)], g.render(lines)
    assert one(lines, "4 common clips").status == g.PASS
    assert one(lines, "sha256 EQUAL").status == g.INFO


def write_log(d, *lines):
    d.mkdir(parents=True, exist_ok=True)
    (d / "run.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d


@pytest.mark.parametrize("bad", ["Traceback (most recent call last):",
                                 "  [44b6_x] REPAIR FAILED (ValueError: x); keeping the base graph",
                                 "  [44b6_x] DEADLINE: 27001s since kernel start"])
def test_verbatim_log_hard_failures(tmp_path, bad):
    lines = g.check_dummy_log(write_log(tmp_path / "d", "start", bad, "done"), mode="verbatim")
    f = fails(lines)
    assert len(f) == 1 and bad.strip() in f[0].details[0]


def test_verbatim_log_validator_and_sweep_lines_are_info(tmp_path):
    log = write_log(tmp_path / "d", "Validator: enabled=True held_out_samples=8", "POST-PROCESS SWEEP 3 configs",
                    "SWEEP TABLE", "Re-writing submission.csv with the selected config")
    assert [ln.status for ln in g.check_dummy_log(log)].count(g.FAIL) == 6        # default mode: unchanged
    lines = g.check_dummy_log(log, mode="verbatim")
    assert not fails(lines) and g.group_status(lines, "dummy-log") == g.PASS
    assert one(lines, "no 'VALIDATOR: disabled").status == g.INFO
    assert one(lines, "1 'Validator: ... enabled=True'").status == g.INFO


def test_verbatim_csv_checks_apply(tmp_path):
    need(X138)
    d = tmp_path / "dummy"
    write_log(d, "ok")
    (d / "submission.csv").write_text(
        "id,dataset,row_type,node_id,t,z,y,x,source_id,target_id\n"
        "0,a,node,0,0,1.0,1.0,1.0,-1,-1\n1,a,node,0,0,1.0,1.0,1.0,-1,-1\n2,a,node,1,1,nan,1.0,1.0,-1,-1\n",
        encoding="utf-8")
    f = [ln.msg for ln in fails(g.run(X138, dummy=d, mode="verbatim"), "csv")]
    assert "ours: 1 duplicate (dataset, node_id) node row(s)" in f
    assert "ours: 1 node row(s) with a non-finite x/y/z" in f


def test_cli_modes(tmp_path, capsys):
    need(V10)
    port = make_copy_port(tmp_path, V10)
    assert g.main(["--pulled", str(V10), "--port", str(port)]) == 1
    out = capsys.readouterr().out
    assert "--mode" not in out and "== source: FAIL" in out            # default header and verdict unchanged
    assert g.main(["--pulled", str(V10), "--port", str(port), "--mode", "verbatim", "--version", "10"]) == 0
    out = capsys.readouterr().out
    assert "--mode        verbatim" in out and "== source: INFO" in out and "RESULT: PASS" in out
    assert "--si-ref" not in out


def test_bad_mode_raises():
    with pytest.raises(ValueError):
        g.run(X138, mode="copy")


# ------------------------------------------------------------------------------------------------------------- si

def make_si(tmp_path, pulled_edit=None, si_edit=None, meta_edit=None):
    """pulled = x138 (optionally edited = a synthetic successor); SI = exp58t (K1 recipe on x138), optionally edited."""
    need(X138, EXP56, EXP58T)
    pulled = tmp_path / "pulled"
    shutil.copytree(X138, pulled)
    if pulled_edit:
        p = pulled / "biohub-x138.ipynb"
        p.write_bytes(edit_code(p.read_bytes(), pulled_edit))
    si = tmp_path / "si"
    si.mkdir()
    meta = json.loads((EXP58T / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta.update(id=SI_ID, title="biohub-exp73-si-anvithpothula", code_file="exp73-si-anvithpothula.ipynb")
    if meta_edit:
        meta_edit(meta)
    (si / "kernel-metadata.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    raw = (EXP58T / "exp58t-x138-safe.ipynb").read_bytes()
    (si / meta["code_file"]).write_bytes(edit_code(raw, si_edit) if si_edit else raw)
    return pulled, si


def si_run(pulled, si, **kw):
    return g.run(pulled, si, mode="si", si_ref=EXP58T, si_ref_base=EXP56, **kw)


def test_si_exp58t_on_x138_passes(tmp_path):
    pulled, si = make_si(tmp_path)
    lines = si_run(pulled, si)
    assert not fails(lines), g.render(lines)
    d = one(lines, "SI vs pulled = our patch diff only")
    assert d.status == g.PASS and "8 hunk(s), +976 / -4 lines" in d.msg
    assert one(lines, "port dataset_sources").msg.endswith("['vitaliineibauer/biohub-ft-weights']")
    assert g.group_status(lines, "source") == g.INFO


def test_si_successor_with_a_changed_knob_passes(tmp_path):
    edit = replace_once(KNOB_OLD, KNOB_NEW)
    pulled, si = make_si(tmp_path, pulled_edit=edit, si_edit=edit)
    lines = si_run(pulled, si)
    assert not fails(lines), g.render(lines)
    scope = one(lines, "successor vs reference base: 1 hunk(s), +1 / -1 lines; 2 changed line(s) mention")
    assert scope.status == g.INFO and "LINEFIT_WEIGHT" in scope.details[0]   # SI_CONDITIONS (e) is shown, not judged


def test_si_reverting_the_successor_change_fails(tmp_path):
    pulled, si = make_si(tmp_path, pulled_edit=replace_once(KNOB_OLD, KNOB_NEW))   # SI built from x138, not S
    f = fails(si_run(pulled, si))
    assert len(f) == 1 and f[0].msg.startswith("SI vs pulled is NOT our patch diff only") and "1 extra" in f[0].msg


@pytest.mark.parametrize("si_edit, needle", [
    (lambda nb: nb["cells"][-1].update(source=nb["cells"][-1]["source"] + "\nx = 1"), "1 extra, 0 missing"),
    (replace_once('                "gap2_synthetic": 1,  # divinsert: node flag (gap2 nodes had none); no downstream '
                  'reader\n', ""), "0 extra, 1 missing"),
    (replace_once('os.environ["BIOHUB_DIVINS_THRESH"] = "0.4"', 'os.environ["BIOHUB_DIVINS_THRESH"] = "0.5"'),
     "1 extra, 1 missing"),
    (lambda nb: nb["cells"].insert(3, {"cell_type": "code", "id": "deadbeef", "metadata": {}, "outputs": [],
                                       "execution_count": None, "source": "print(1)"}), "1 extra"),
    (lambda nb: nb["cells"][0].update(cell_type="markdown"), "extra"),
])
def test_si_extra_or_missing_changes_fail(tmp_path, si_edit, needle):
    pulled, si = make_si(tmp_path, si_edit=si_edit)
    f = fails(si_run(pulled, si))
    assert len(f) == 1 and f[0].group == "notebook-bytes" and needle in f[0].msg, [x.msg for x in f]


def test_si_override_tag_line_is_normalised(tmp_path):
    old = "# ---- exp58t_x138_safe: probe overrides (tools/build_probe_kernel.py --base x138) ----"
    new = "# ---- exp73_si_anvithpothula: probe overrides (tools/build_probe_kernel.py --base succ) ----"
    pulled, si = make_si(tmp_path, si_edit=replace_once(old, new))
    lines = si_run(pulled, si)
    assert not fails(lines), g.render(lines)
    assert "SI 1, reference build 1" in one(lines, "override tag lines normalised").msg


def test_si_notebook_shell_must_match(tmp_path):
    pulled, si = make_si(tmp_path, si_edit=lambda nb: nb["metadata"].update(extra=1))
    f = fails(si_run(pulled, si))
    assert len(f) == 1 and f[0].msg.startswith("SI notebook non-cell keys differ") and "metadata" in f[0].msg


@pytest.mark.parametrize("meta_edit, needle", [
    (lambda m: m["dataset_sources"].remove("vitaliineibauer/biohub-ft-weights"), "port dataset_sources"),
    (lambda m: m["dataset_sources"].append("someone/else"), "port dataset_sources"),
    (lambda m: m.update(id="vitaliineibauer/biohub-exp63-succ-anvithpothula"), "port id"),
    (lambda m: m.update(enable_internet=True), "port enable_internet"),
])
def test_si_metadata(tmp_path, meta_edit, needle):
    pulled, si = make_si(tmp_path, meta_edit=meta_edit)
    f = fails(si_run(pulled, si))
    assert len(f) == 1 and f[0].msg.startswith(needle), [x.msg for x in f]


def test_si_needs_a_reference(tmp_path):
    pulled, si = make_si(tmp_path)
    f = fails(g.run(pulled, si, mode="si"))
    # without the reference the weights dataset is not an allowed addition either
    assert [x.group for x in f] == ["metadata", "notebook-bytes"], [x.msg for x in f]
    assert f[0].msg.startswith("port dataset_sources") and f[1].msg.startswith("--mode si needs --si-ref")


def test_si_dummy_and_author_real(tmp_path):
    need(DUMMY58T, DUMMY56)
    pulled, si = make_si(tmp_path)
    lines = si_run(pulled, si, dummy=DUMMY58T, author=DUMMY56, version=1)
    assert not [ln for ln in lines if ln.status in (g.FAIL, g.SKIP)], g.render(lines)
    assert one(lines, "has 'DIVINS ENABLED:'").status == g.PASS


@pytest.mark.parametrize("log, needle", [
    (("VALIDATOR: disabled (BIOHUB_VALIDATOR_ENABLE=0).",), "missing 'DIVINS ENABLED:'"),
    (("DIVINS ENABLED: 5 DaughterNet model(s)", "  [a] DIVINS FAILED (RuntimeError: x); input edges kept"),
     "1 line(s) with 'DIVINS FAILED'"),
    (("DIVINS ENABLED: 5 DaughterNet model(s)", "  [a] DIVINS SKIPPED (deadline): elapsed 28801s"),
     "1 line(s) with 'DIVINS SKIPPED'"),
    (("DIVINS ENABLED: 5 DaughterNet model(s)", "LOWREFINE FAILED (t=3, ValueError: x); grid coordinates kept"),
     "1 line(s) with 'LOWREFINE FAILED'"),
])
def test_si_dummy_log(tmp_path, log, needle):
    lines = g.check_dummy_log(write_log(tmp_path / "d", *log), mode="si")
    f = fails(lines)
    assert len(f) == 1 and f[0].msg.startswith(needle), [x.msg for x in f]
    ok = g.check_dummy_log(write_log(tmp_path / "ok", "DIVINS ENABLED: 5 DaughterNet model(s)"), mode="si")
    assert not fails(ok)


def test_cli_si(tmp_path, capsys):
    pulled, si = make_si(tmp_path)
    assert g.main(["--pulled", str(pulled), "--port", str(si), "--mode", "si", "--si-ref", str(EXP58T)]) == 0
    out = capsys.readouterr().out
    assert "--si-ref " in out and "(default)" in out and "RESULT: PASS" in out


# ------------------------------------------------------------------------------------- si: slid insertions / deletions

M = g.CELL_MARK + "code"


def test_slid_new_cell_matches():
    # the same new cell [M, x, y] inserted after cell 0; difflib may see it as [M, x, y] before the next marker or as
    # [x, y, M] after it (seen on the HF v3 SI build, whose cell-0 tail differs from x138's)
    base = [M, "a", M, "c"]
    ref = [M, "a", M, "x", "y", M, "c"]
    h = g.diff_hunks_slid(base, ref)
    assert len(h) == 1 and {f[1] for f in h[0][2]} == {(M, "x", "y"), ("x", "y", M)}
    for other in ((M, "x", "y"), ("x", "y", M)):          # either placement, as the other pair's difflib may show it
        assert g.hunks_match(h[0], ((), other, frozenset({((), other)})))


def test_rotation_that_is_not_a_slide_does_not_match():
    base = [M, "a", "b", M, "c"]
    x = g.diff_hunks_slid(base, [M, "a", "p", "q", "r", "b", M, "c"])      # inserts p q r
    y = g.diff_hunks_slid(base, [M, "a", "q", "r", "p", "b", M, "c"])      # inserts q r p: a different text
    assert len(x) == len(y) == 1 and not g.hunks_match(x[0], y[0])


def test_slid_deletion_matches():
    a = ["k", "z", "z", "z", "m"]
    h = g.diff_hunks_slid(a, ["k", "z", "z", "m"])
    assert len(h) == 1 and h[0][2] == frozenset({(("z",), ())})


def test_si_real_builder_on_hfv3(tmp_path):
    """If tools/build_probe_kernel.py has the --base succ path (E10 v3 (B)), build the K1 recipe on the pulled HF v3
    (x138 without comments) and gate it against exp58t: it must pass, with one slid insertion."""
    import subprocess
    need(HFV3_PULLED, EXP58T, EXP56)
    builder = (ROOT / "tools" / "build_probe_kernel.py").read_text(encoding="utf-8")
    if '"succ"' not in builder or "--base-ipynb" not in builder:
        pytest.skip("builder has no --base succ path")
    out_rel = f"_scratch_e10v3/pytest_si_{tmp_path.name}"
    out = ROOT / "experiments" / out_rel
    knobs = ["DIVINS_ENABLE=1", "DIVINS_STEAL=1", "DIVINS_CAP=4", "DIVINS_FRAME_CAP=1", "DIVINS_ALPHA=1",
             "DIVINS_THRESH=0.4", "DIVINS_DUMP=0", "REPAIR_DEADLINE_S=34200", "DIVINS_DEADLINE_S=28800",
             "LOWREFINE_ENABLE=0"]
    cmd = [sys.executable, "tools/build_probe_kernel.py", "exp73_si_raunakdey07", "--base", "succ",
           "--base-ipynb", str(HFV3_PULLED / "biohub-harmonic-fusion-v3.ipynb"),
           "--base-meta", str(HFV3_PULLED / "kernel-metadata.json"),
           "--patch", "divinsert", "--patch", "safetail", "--patch", "lowrefine", "--out-dir", out_rel]
    for k in knobs:
        cmd += ["--set", k]
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            pytest.skip(f"builder refused or failed: {r.stdout[-300:]} {r.stderr[-300:]}")
        lines = g.run(HFV3_PULLED, out, mode="si", si_ref=EXP58T, si_ref_base=EXP56)
        assert not fails(lines), g.render(lines)
        assert "1 insertion(s) matched as the same block slid" in one(lines, "SI vs pulled = our patch diff only").msg
    finally:
        shutil.rmtree(out, ignore_errors=True)
        if out.parent.is_dir() and not any(out.parent.iterdir()):
            out.parent.rmdir()


# ------------------------------------------------------------------ si: hunk order and position (review_gate_verbatim_0)

def test_same_hunks_in_swapped_order_do_not_match():
    base = [M, "a", "b", "c"]
    got = g.diff_hunks_slid(base, [M, "Y", "a", "b", "X", "c"])
    want = g.diff_hunks_slid(base, [M, "X", "a", "b", "Y", "c"])
    assert len(got) == len(want) == 2 and not all(g.hunks_match(h, w) for h, w in zip(got, want))


def test_slid_forms_record_their_code_cells():
    h = g.diff_hunks_slid([M, "a", M, "c"], [M, "a", M, "x", "y", M, "c"])
    assert h[0][3] == frozenset({1, 2})                    # before or after the marker of code cell 2
    assert g.diff_hunks_slid([M, "a", M, "b"], [M, "a", M, "b", "X"])[0][3] == frozenset({2})


def _move_override_block_to_cell1(nb):
    import difflib
    base0 = json.loads((EXP56 / "exp56-x138-verbatim.ipynb").read_text(encoding="utf-8"))["cells"][0]["source"]
    base0 = ("".join(base0) if isinstance(base0, list) else base0).split("\n")
    lines = nb["cells"][0]["source"].split("\n")
    ops = [o for o in difflib.SequenceMatcher(None, base0, lines, autojunk=False).get_opcodes() if o[0] != "equal"]
    assert len(ops) == 1 and ops[0][0] == "insert", ops
    j1, j2 = ops[0][3], ops[0][4]
    nb["cells"][0]["source"] = "\n".join(lines[:j1] + lines[j2:])
    nb["cells"][1]["source"] = nb["cells"][1]["source"] + "\n" + "\n".join(lines[j1:j2])


def test_si_hunk_moved_to_another_cell_fails(tmp_path):
    """Same hunk content and order, but the cell-0 override block sits at the end of cell 1: the content check alone
    passes, the code-cell position check must FAIL."""
    pulled, si = make_si(tmp_path, si_edit=_move_override_block_to_cell1)
    lines = si_run(pulled, si)
    assert one(lines, "SI vs pulled = our patch diff only").status == g.PASS
    f = fails(lines)
    assert len(f) == 1 and f[0].msg.startswith("1 SI hunk(s) sit in a different code cell"), [x.msg for x in f]
    assert "SI code cell [2] vs reference [1]" in f[0].details[0]


def test_si_position_check_passes_on_exp58t(tmp_path):
    pulled, si = make_si(tmp_path)
    assert one(si_run(pulled, si), "every SI hunk sits in the same code cell").status == g.PASS


# ------------------------------------------------------------------ review_gate_verbatim_1 (safety / rule fit) fixes

@pytest.mark.parametrize("pid, ok", [
    ("vitaliineibauer/biohub-exp73-si-anvithpothula", True),
    ("vitaliineibauer/biohub-exp73a-si-anvithpothula", True),          # the builder's exp73[x]_si_<author> names
    ("vitaliineibauer/biohub-exp73-si-anvithpothula-k2", True),        # ... and its [_suffix]
    ("vitaliineibauer/biohub-exp73-si-", False),
    ("vitaliineibauer/biohub-exp73a-k2-dc015", False),                 # a ladder id is not an SI id
    ("vitaliineibauer/biohub-exp58-x138-safe-lowref", False),          # never a finals id
    ("someone/biohub-exp73-si-anvithpothula", False),
])
def test_si_id_follows_the_builder_slug_rule(tmp_path, pid, ok):
    pulled, si = make_si(tmp_path, meta_edit=lambda m: m.update(id=pid))
    idl = one([ln for ln in si_run(pulled, si) if ln.group == "metadata"], "port id ")
    assert idl.status == (g.PASS if ok else g.FAIL), idl.msg


def test_si_reference_base_must_be_pinned_x138(tmp_path):
    pulled, si = make_si(tmp_path)
    f = fails(g.run(pulled, si, mode="si", si_ref=EXP58T, si_ref_base=EXP58T))
    assert any(x.group == "notebook-bytes" and "is not the pinned x138 v1" in x.msg for x in f), [x.msg for x in f]


def test_si_reference_recipe_is_named(tmp_path):
    pulled, si = make_si(tmp_path)
    assert one(si_run(pulled, si), "reference build = ").msg == "reference build = K1 exp58t recipe"


@pytest.mark.parametrize("mode", ["verbatim", "si"])
def test_missing_pulled_notebook_fails_in_copy_modes(tmp_path, mode):
    """review_gate_verbatim_0: a pulled folder without its notebook must FAIL even with no --port (static trigger run);
    source_as_info used to downgrade the 'pulled notebook: ...' line to INFO -> RESULT PASS."""
    d = tmp_path / "pulled"
    d.mkdir()
    (d / "kernel-metadata.json").write_text(json.dumps({"id": "a/b", "code_file": "nb.ipynb", "kernel_sources": [],
                                                        "dataset_sources": []}), encoding="utf-8")
    f = fails(g.run(d, mode=mode))
    assert any(x.group == "source" and x.msg.startswith("pulled notebook: ") for x in f), [x.msg for x in f]


def test_slide_is_bounded_by_the_neighbouring_hunk():
    # a -> b deletes 'y' (line 1) and 'x y z' (lines 3-5); sliding the second deletion left must stop at the first hunk,
    # else the non-equivalent form ('y', 'z', 'x') (it would re-use line 2 next to the first hunk) joins its forms
    h = g.diff_hunks_slid(["x", "y", "z", "x", "y", "z"], ["x", "z"])
    assert len(h) == 2 and h[1][2] == frozenset({(("x", "y", "z"), ()), (("z", "x", "y"), ())})


def _nb_dir(d, *cells):
    d.mkdir(parents=True)
    nb = {"cells": [{"cell_type": "code", "id": f"c{i}", "metadata": {}, "outputs": [], "execution_count": None,
                     "source": "\n".join(c)} for i, c in enumerate(cells)],
          "metadata": {}, "nbformat": 4, "nbformat_minor": 4}
    (d / "nb.ipynb").write_text(json.dumps(nb), encoding="utf-8")
    (d / "kernel-metadata.json").write_text(json.dumps({"id": "a/b", "code_file": "nb.ipynb"}), encoding="utf-8")
    return d


def test_si_diff_same_hunks_in_swapped_order_fails(tmp_path):
    """check_si_diff itself (not only hunks_match) must compare the hunks in order: SI = pulled with the reference's two
    insertions swapped. Synthetic base, so the 'not the pinned x138' line FAILs too; only the diff line is asserted."""
    base = _nb_dir(tmp_path / "base", ["a", "b", "c", "d"])
    ref = _nb_dir(tmp_path / "ref", ["X", "a", "b", "c", "Y", "d"])
    pulled = _nb_dir(tmp_path / "pulled", ["a", "b", "c", "d"])
    si = _nb_dir(tmp_path / "si", ["Y", "a", "b", "c", "X", "d"])
    ok = _nb_dir(tmp_path / "si_ok", ["X", "a", "b", "c", "Y", "d"])
    assert one(g.check_si_diff(pulled, ok, ref, base), "SI vs pulled").status == g.PASS
    d = one(g.check_si_diff(pulled, si, ref, base), "SI vs pulled")
    assert d.status == g.FAIL and "(0 extra, 0 missing)" in d.msg and "the same hunks in a different order" in d.details
