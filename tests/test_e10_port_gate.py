"""R10-A3: tools/e10_port_gate.py (E10 PORT RULE P4b/P4c gate, read-only) on the real fixtures and synthetic cases.

    python -m pytest tests/test_e10_port_gate.py -q

Real fixtures: experiments/ext_x138 (x138 v1 = the exp56 notebook byte for byte), experiments/exp56_x138_verbatim,
experiments/ext_optimized-biohub-max-score/v10_2026-09-26 and the git-ignored exp56 dummy output
_dl/biohub-exp56-x138-verbatim. A test whose fixture is absent is skipped.
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
V10 = ROOT / "experiments" / "ext_optimized-biohub-max-score" / "v10_2026-09-26"
DUMMY56 = ROOT / "_dl" / "biohub-exp56-x138-verbatim"
PORT_ID = "vitaliineibauer/biohub-exp63-succ-anvithpothula"


def need(*paths):
    for p in paths:
        if not p.exists():
            pytest.skip(f"fixture {p.relative_to(ROOT)} not present")


def status(lines, group):
    return g.group_status(lines, group)


def fails(lines, group=None):
    return [ln for ln in lines if ln.status == g.FAIL and (group is None or ln.group == group)]


def one(lines, prefix):
    got = [ln for ln in lines if ln.msg.startswith(prefix)]
    assert len(got) == 1, [ln.msg for ln in lines]
    return got[0]


# ------------------------------------------------------------------------------------------------ real fixtures

def test_x138_source_passes():
    need(X138)
    lines = g.check_source(X138 / "biohub-x138.ipynb")
    assert status(lines, "source") == g.PASS, g.render(lines)
    v, d, m = one(lines, "validator"), one(lines, "deadline"), one(lines, "sweep/rewrite markers")
    assert "1 assignment(s), all '0'; first at L72, before the first reader at L4096" in v.msg
    assert any(x.startswith("L74 ") for x in d.details) and any(x.startswith("L1705 ") for x in d.details)
    # x138's own dormant sweep / re-write block is the baseline; its comment hit is info only
    assert m.msg.startswith("sweep/rewrite markers: 0 NEW")
    assert any(x.startswith("L4831 ") and "[x138 baseline] Re-writing submission.csv" in x for x in m.details)
    assert any(x.startswith("L76 ") and "[info: comment]" in x for x in m.details)


def test_x138_pulled_only_groups():
    need(X138)
    lines = g.run(X138)
    assert one(lines, "pulled kernel_sources").status == g.PASS
    assert one(lines, "pulled sources").status == g.PASS
    got = {grp: status(lines, grp) for grp in g.GROUPS}
    assert got == {"metadata": g.PASS, "notebook-bytes": g.SKIP, "source": g.PASS, "dummy-log": g.SKIP,
                   "csv": g.SKIP, "node-counts": g.SKIP}


def test_v10_source_fails_on_validator_and_deadline_override():
    need(V10)
    lines = g.check_source(V10 / "optimized-biohub-max-score.ipynb")
    assert status(lines, "source") == g.FAIL
    v, d, m = one(lines, "validator"), one(lines, "deadline"), one(lines, "sweep/rewrite markers")
    assert v.status == g.FAIL and "L121 " in v.msg and "'1'" in v.msg
    # the first hit (L123 = '27000') is fine; the later pass-2 override is not
    assert d.status == g.FAIL and "L6583 " in d.msg and "30600" in d.msg and "L123 " not in d.msg
    new = [x for x in m.details if "[NEW]" in x]
    assert m.status == g.FAIL and len(new) > 50
    assert any(x.startswith("L184 ") and "BIOHUB_REWRITE_*" in x for x in new)
    assert any(x.startswith("L6583 ") for x in new)


def test_cli_exit_codes(capsys):
    need(X138, V10)
    assert g.main(["--pulled", str(X138)]) == 0
    assert "RESULT: PASS" in capsys.readouterr().out
    assert g.main(["--pulled", str(V10), "--version", "10"]) == 1
    out = capsys.readouterr().out
    assert "== source: FAIL" in out and "RESULT: FAIL" in out and "author version: 10" in out


def test_exp56_dummy_log_and_csv_pass():
    need(X138, DUMMY56)
    lines = g.run(X138, dummy=DUMMY56, author=DUMMY56)   # our dummy vs itself as the 'author' output
    for grp in ("metadata", "source", "dummy-log", "csv", "node-counts"):
        assert status(lines, grp) == g.PASS, g.render(lines)
    assert status(lines, "notebook-bytes") == g.SKIP
    assert one(lines, "has 'VALIDATOR: disabled (BIOHUB_VALIDATOR_ENABLE=0).'").details == [
        "VALIDATOR: disabled (BIOHUB_VALIDATOR_ENABLE=0)."]
    assert one(lines, "has 'enabled=False'").details[0].startswith("Validator:")
    assert one(lines, "sha256 EQUAL").status == g.INFO


def test_exp56_folder_fails_only_on_the_port_id_prefix():
    need(X138, EXP56)
    lines = g.check_metadata(X138, EXP56) + g.check_notebook_bytes(X138, EXP56)
    f = fails(lines)
    assert len(f) == 1 and f[0].msg.startswith("port id 'vitaliineibauer/biohub-exp56-x138-verbatim'"), f
    assert status(lines, "notebook-bytes") == g.PASS   # exp56 is x138 byte for byte


# ------------------------------------------------------------------------------- metadata + notebook bytes (synthetic)

def make_pulled(tmp_path, edit=None):
    need(X138)
    d = tmp_path / "pulled"
    d.mkdir()
    shutil.copy(X138 / "biohub-x138.ipynb", d / "biohub-x138.ipynb")
    meta = json.loads((X138 / "kernel-metadata.json").read_text(encoding="utf-8"))
    if edit:
        edit(meta)
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return d


def make_port(tmp_path, pulled, edit=None, nb=None):
    d = tmp_path / "port"
    d.mkdir()
    meta = json.loads((pulled / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta.update(id=PORT_ID, title="biohub exp63 succ anvithpothula", is_private=True, enable_internet=False,
                code_file="exp63-succ-anvithpothula.ipynb")
    meta.pop("id_no", None)
    for k in g.SOURCE_KEYS:
        meta[k] = [s for s in meta.get(k, []) if s.strip()]
    if edit:
        edit(meta)
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    raw = (pulled / "biohub-x138.ipynb").read_bytes()
    (d / meta["code_file"]).write_bytes(nb(raw) if nb else raw)
    return d


def test_synthetic_port_passes(tmp_path):
    pulled = make_pulled(tmp_path)
    port = make_port(tmp_path, pulled)
    lines = g.check_metadata(pulled, port) + g.check_notebook_bytes(pulled, port)
    assert not fails(lines), g.render(lines)
    assert status(lines, "metadata") == g.PASS and status(lines, "notebook-bytes") == g.PASS


def test_port_may_drop_a_blank_pulled_source_but_the_pulled_file_still_fails(tmp_path):
    pulled = make_pulled(tmp_path, lambda m: m["dataset_sources"].append(""))
    port = make_port(tmp_path, pulled)
    f = fails(g.check_metadata(pulled, port))
    assert len(f) == 1 and f[0].msg.startswith("pulled sources: blank")


@pytest.mark.parametrize("edit, needle", [
    (lambda m: m.update(is_private=False), "port is_private = False"),
    (lambda m: m.update(is_private="true"), "port is_private = 'true'"),          # JSON boolean only
    (lambda m: m.pop("is_private"), "port is_private = '<absent>'"),
    (lambda m: m.update(enable_internet=True), "port enable_internet = True"),
    (lambda m: m.update(id_no=135218473), "port has id_no"),
    (lambda m: m.update(docker_image="gcr.io/kaggle-gpu-images/python:latest"), "port docker_image"),
    (lambda m: m.update(machine_shape="NvidiaTeslaP100"), "port machine_shape"),
    (lambda m: m.update(enable_gpu=False), "port enable_gpu"),
    (lambda m: m.update(id="vitaliineibauer/biohub-exp64-anvithpothula"), "port id"),
    (lambda m: m.update(id=g.PORT_ID_PREFIX), "port id"),
    (lambda m: m.update(title=" "), "port title"),
    (lambda m: m["dataset_sources"].append("vitaliineibauer/biohub-ft-weights"), "port dataset_sources"),
    (lambda m: m["dataset_sources"].pop(), "port dataset_sources"),
    (lambda m: m.update(kernel_sources=["anvithpothula/biohub-x138"]), "port kernel_sources"),
    (lambda m: m.update(enable_tpu=True), "port fields that may not differ"),
])
def test_port_metadata_violation_fails(tmp_path, edit, needle):
    pulled = make_pulled(tmp_path)
    port = make_port(tmp_path, pulled, edit)
    f = fails(g.check_metadata(pulled, port))
    assert len(f) == 1 and f[0].msg.startswith(needle), [x.msg for x in f]


@pytest.mark.parametrize("key", ["dataset_sources", "model_sources", "competition_sources"])
def test_pulled_blank_source_fails(tmp_path, key):
    pulled = make_pulled(tmp_path, lambda m: m.setdefault(key, []).append(""))
    f = fails(g.check_metadata(pulled))
    assert len(f) == 1 and f"{key}[" in f[0].msg and "= ''" in f[0].msg


def test_pulled_kernel_sources_non_empty_fails(tmp_path):
    pulled = make_pulled(tmp_path, lambda m: m.update(kernel_sources=["someone/cached-submission"]))
    f = fails(g.check_metadata(pulled))
    assert len(f) == 1 and f[0].msg.startswith("pulled kernel_sources = ['someone/cached-submission']")


def test_notebook_bytes_differ_fails(tmp_path):
    pulled = make_pulled(tmp_path)
    port = make_port(tmp_path, pulled, nb=lambda raw: raw + b"\n")
    lines = g.check_metadata(pulled, port) + g.check_notebook_bytes(pulled, port)
    assert status(lines, "metadata") == g.PASS
    f = fails(lines)
    assert len(f) == 1 and f[0].group == "notebook-bytes" and "byte-for-byte" in f[0].msg


# ------------------------------------------------------------------------------------------- source grep (synthetic)

def write_nb(d, *cells, markdown=()):
    d.mkdir(parents=True, exist_ok=True)
    cs = [{"cell_type": "markdown", "metadata": {}, "source": m} for m in markdown]
    cs += [{"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": c.splitlines(keepends=True)} for c in cells]
    p = d / "nb.ipynb"
    p.write_text(json.dumps({"cells": cs, "metadata": {}, "nbformat": 4, "nbformat_minor": 4}), encoding="utf-8")
    return p


def source(tmp_path, *cells, **kw):
    return g.check_source(write_nb(tmp_path / "nb", *cells, **kw))


TOP = ('import os\n'
       'os.environ["BIOHUB_VALIDATOR_ENABLE"] = "0"\n'
       'os.environ["BIOHUB_REPAIR_DEADLINE_S"] = "27000"\n')
READERS = ('REPAIR_DEADLINE_S = float(os.environ.get("BIOHUB_REPAIR_DEADLINE_S", "27000"))\n'
           'VALIDATOR_ENABLE = os.environ.get("BIOHUB_VALIDATOR_ENABLE", "1") != "0"\n'
           'if not VALIDATOR_ENABLE:\n'
           '    print("VALIDATOR: disabled (BIOHUB_VALIDATOR_ENABLE=0).")\n')


def test_synthetic_good_notebook_passes(tmp_path):
    lines = source(tmp_path, TOP, READERS, markdown=["os.environ['BIOHUB_VALIDATOR_ENABLE'] = '1'; PP sweep"])
    assert status(lines, "source") == g.PASS, g.render(lines)
    assert "first at L2, before the first reader at L6" in one(lines, "validator").msg


def test_validator_assignment_after_the_reader_fails(tmp_path):
    lines = source(tmp_path, "import os\n" + READERS, TOP)
    v = one(lines, "validator")
    assert v.status == g.FAIL and "no assignment before the first reader at L3" in v.msg
    assert one(lines, "deadline").status == g.PASS   # its reader carries the 27000 fallback


def test_missing_validator_assignment_fails(tmp_path):
    lines = source(tmp_path, 'import os\nos.environ["BIOHUB_REPAIR_DEADLINE_S"] = "27000"\n', READERS)
    v = one(lines, "validator")
    assert v.status == g.FAIL and "missing assignment counts as ON" in v.msg


def test_missing_deadline_guard_fails(tmp_path):
    lines = source(tmp_path, 'import os\nos.environ["BIOHUB_VALIDATOR_ENABLE"] = "0"\n',
                   'VALIDATOR_ENABLE = os.environ.get("BIOHUB_VALIDATOR_ENABLE", "1") != "0"\n')
    d = one(lines, "deadline")
    assert d.status == g.FAIL and "deadline guard is missing" in d.msg


@pytest.mark.parametrize("extra, check, needle", [
    ('os.environ["BIOHUB_VALIDATOR_ENABLE"] = "1"\n', "validator", "'1'"),       # every assignment, not the first hit
    ("os.environ['BIOHUB_VALIDATOR_ENABLE']='0 '\n", "validator", "'0 '"),
    ('os.environ.setdefault("BIOHUB_VALIDATOR_ENABLE", "1")\n', "validator", "'1'"),
    ('PRESET = {"BIOHUB_VALIDATOR_ENABLE": "1"}\n', "validator", "preset"),
    ('os.environ.update({"BIOHUB_VALIDATOR_ENABLE": "1"})\n', "validator", "'1'"),
    ('os.environ.update(BIOHUB_VALIDATOR_ENABLE="1")\n', "validator", "keyword"),
    ('os.environ["BIOHUB_VALIDATOR_ENABLE"] = os.environ.get("MY_FLAG", "0")\n', "validator", "MY_FLAG"),
    ('os.environ["BIOHUB_VALIDATOR_ENABLE"] = False\n', "validator", "False"),
    ('del os.environ["BIOHUB_VALIDATOR_ENABLE"]\n', "validator", "unsets"),
    ('VALIDATOR_ENABLE = True\n', "validator", "binds VALIDATOR_ENABLE to True"),
    ('for k in ("BIOHUB_VALIDATOR_ENABLE",):\n    os.environ[k] = "1"\n', "validator", "indirect"),
    ('os.environ["BIOHUB_REPAIR_DEADLINE_S"] = os.environ.get("BIOHUB_REWRITE_DEADLINE_S", "30600")\n',
     "deadline", "30600"),
    ('x = os.getenv("BIOHUB_REPAIR_DEADLINE_S", "30600")\n', "deadline", "reader fallback '30600'"),
    ('CFG = {"BIOHUB_REPAIR_DEADLINE_S": "30600"}\n', "deadline", "'30600'"),
    ('REPAIR_DEADLINE_S = 30600\n', "deadline", "binds REPAIR_DEADLINE_S to 30600"),
    ('REPAIR_DEADLINE_S += 3600\n', "deadline", "augmented"),
])
def test_every_occurrence_is_checked(tmp_path, extra, check, needle):
    lines = source(tmp_path, TOP, READERS, "import os\n" + extra)
    ln = one(lines, check)
    assert ln.status == g.FAIL and needle in ln.msg, ln.msg


@pytest.mark.parametrize("extra", [
    'os.environ.setdefault("BIOHUB_VALIDATOR_ENABLE", "0")\n',
    'PRESET = {"BIOHUB_VALIDATOR_ENABLE": "0", "BIOHUB_REPAIR_DEADLINE_S": 27000}\n',   # int 27000 is fine
    'os.environ.update({"BIOHUB_REPAIR_DEADLINE_S": "27000"})\n',
    'VALIDATOR_ENABLE = False\nREPAIR_DEADLINE_S = 27000\n',
    '# a comment about a PP sweep and a pass-2 rewrite is not code\nx = 1\n',
    '"""A docstring may mention a sweep or BIOHUB_REWRITE_DEADLINE_S."""\n',
    '%env BIOHUB_VALIDATOR_ENABLE=0\n!ls /kaggle/input\n',
])
def test_accepted_forms_pass(tmp_path, extra):
    lines = source(tmp_path, TOP, READERS, "import os\n" + extra)
    assert status(lines, "source") == g.PASS, g.render(lines)


def test_unparseable_cell_with_a_key_fails(tmp_path):
    lines = source(tmp_path, TOP, READERS, "%%bash\nexport BIOHUB_VALIDATOR_ENABLE=1\n")
    v = one(lines, "validator")
    assert v.status == g.FAIL and "does not parse" in v.msg


def test_new_marker_in_code_fails(tmp_path):
    lines = source(tmp_path, TOP, READERS, 'import os\nos.environ["BIOHUB_REWRITE_LATEST_START_S"] = "27600"\n')
    m = one(lines, "sweep/rewrite markers")
    assert m.status == g.FAIL and m.msg.startswith("sweep/rewrite markers: 1 NEW")
    assert any("[NEW] BIOHUB_REWRITE_*" in x for x in m.details)


def test_x138_baseline_line_is_allowed_once_per_x138_occurrence(tmp_path):
    need(X138)
    base = 'print("SWEEP: validator unavailable -- keeping the base configuration.")\n'
    assert one(source(tmp_path / "a", TOP, READERS, base), "sweep/rewrite markers").status == g.PASS
    m = one(source(tmp_path / "b", TOP, READERS, base + base), "sweep/rewrite markers")
    assert m.status == g.FAIL and m.msg.startswith("sweep/rewrite markers: 1 NEW code hit(s), 1 x138-baseline")


# ----------------------------------------------------------------------------------------------- csv + node counts

HEADER = "id,dataset,row_type,node_id,t,z,y,x,source_id,target_id\n"
NODES = [("44b6_a", 0, 0, 1.0, 2.0, 3.0), ("44b6_a", 1, 1, 1.0, 2.5, 3.0), ("44b6_a", 2, 2, 1.0, 3.0, 3.5),
         ("6bba_b", 0, 0, 4.0, 5.0, 6.0)]
EDGES = [("44b6_a", 0, 1), ("44b6_a", 1, 2)]


def write_csv(d, nodes, edges=()):
    d.mkdir(parents=True, exist_ok=True)
    rows = [HEADER]
    for ds, nid, t, z, y, x in nodes:
        rows.append(f"{len(rows) - 1},{ds},node,{nid},{t},{z},{y},{x},-1,-1\n")
    for ds, s, t in edges:
        rows.append(f"{len(rows) - 1},{ds},edge,-1,-1,-1,-1,-1,{s},{t}\n")
    (d / "submission.csv").write_text("".join(rows), encoding="utf-8")
    return d


def test_synthetic_csv_passes(tmp_path):
    lines, ours, _ = g.check_csvs(write_csv(tmp_path / "d", NODES, EDGES), None)
    assert status(lines, "csv") == g.PASS, g.render(lines)
    assert ours["counts"] == {"44b6_a": 3, "6bba_b": 1}


def test_duplicate_node_row_fails_although_validate_csv_passes(tmp_path):
    lines, _, _ = g.check_csvs(write_csv(tmp_path / "d", NODES + [("44b6_a", 1, 1, 9.0, 9.0, 9.0)], EDGES), None)
    assert one(lines, "ours: dummy_gates.validate_csv").status == g.PASS   # validate_csv keeps the last copy silently
    f = fails(lines, "csv")
    assert len(f) == 1 and f[0].msg == "ours: 1 duplicate (dataset, node_id) node row(s)"


@pytest.mark.parametrize("bad", ["nan", "NaN", "inf", "-inf", ""])
def test_non_finite_coordinate_fails(tmp_path, bad):
    lines, _, _ = g.check_csvs(write_csv(tmp_path / "d", NODES[:3] + [("6bba_b", 0, 0, 4.0, bad, 6.0)], EDGES), None)
    f = fails(lines, "csv")
    assert len(f) == 1 and f[0].msg == "ours: 1 node row(s) with a non-finite x/y/z"


def test_author_csv_is_checked_too(tmp_path):
    lines, _, _ = g.check_csvs(write_csv(tmp_path / "o", NODES, EDGES),
                               write_csv(tmp_path / "a", NODES[:3] + [("6bba_b", 0, 0, 4.0, "nan", 6.0)], EDGES))
    f = fails(lines, "csv")
    assert len(f) == 1 and f[0].msg.startswith("author: 1 node row(s) with a non-finite")


def counts_dir(d, counts):
    return write_csv(d, [(ds, i, 0, 1.0, 1.0, 1.0) for ds, n in counts.items() for i in range(n)])


@pytest.mark.parametrize("ours, ok", [
    ({"a": 1000, "b": 500}, True),
    ({"a": 1010, "b": 495}, True),                # exactly 1% above and 1% below
    ({"a": 1011, "b": 500}, False),               # 1.1%
    ({"a": 1000, "b": 494}, False),               # 1.2%
    ({"a": 1000}, False),                         # a clip missing
    ({"a": 1000, "b": 500, "c": 1}, False),       # an extra clip
])
def test_node_counts_within_one_percent(tmp_path, ours, ok):
    lines, o, a = g.check_csvs(counts_dir(tmp_path / "ours", ours), counts_dir(tmp_path / "author", {"a": 1000, "b": 500}))
    assert status(lines, "csv") == g.PASS
    nc = g.check_node_counts(o, a)
    assert status(nc, "node-counts") == (g.PASS if ok else g.FAIL), nc[0].msg
    assert one(nc, "sha256").status == g.INFO
