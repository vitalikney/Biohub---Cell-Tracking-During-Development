"""E10 PORT RULE gate: P4b + P4c as a read-only check (CONTEXT.md, 26 Sep 13:27 UTC P4b entry; P4c text in
research/wf_ideas_v4/round10/report.json, R10-A2; this script is R10-A3).

READ-ONLY: it reads local folders only. It never calls Kaggle, never pushes a kernel and never submits.

    python tools/e10_port_gate.py --pulled experiments/ext_<slug> [--port experiments/<our port folder>] \
        [--dummy _dl/<our dummy output>] [--author _dl/<author output>] [--version N]

Check groups (each prints PASS / FAIL / SKIP lines with reasons; INFO lines never fail):
  metadata        P4b(b)/P4c(4) on the pulled kernel-metadata.json: no blank "" source, kernel_sources == [];
                  P4b(a) on our port's kernel-metadata.json (--port): id prefix, title, is_private true,
                  enable_internet false, no id_no; docker_image / machine_shape / enable_gpu, every non-blank source and
                  every other field equal to the pulled file (only id, id_no, title, is_private, enable_internet and
                  code_file may differ)
  notebook-bytes  P4c(1): the port's code_file is byte-identical (sha256) to the pulled notebook (--port)
  source          P4c(3): grep of the joined code cells of the pulled notebook, every occurrence (needs only --pulled)
  dummy-log       P4c(5): required / forbidden strings in our dummy run's *.log (--dummy)
  csv             P4b(e)/P4c(5): tools/dummy_gates.validate_csv (unchanged) + no duplicate (dataset, node_id) node row +
                  finite x/y/z, on our dummy submission.csv (--dummy) and on the author's output CSV (--author)
  node-counts     per-clip node counts of the two CSVs within 1%; sha256 equality is INFO (--dummy and --author)
Exit code 0 only if no line is FAIL, 1 otherwise.

Source-grep rules (line numbers refer to the code cells joined with a newline, as in round 10's 'l.6583'):
  * BIOHUB_VALIDATOR_ENABLE: every assignment (os.environ[...] =, setdefault, putenv, %env, dict-literal preset,
    keyword argument) must be the literal '0', and one must come before the first reader (os.environ.get, getenv,
    os.environ[...]). A missing assignment counts as ON (x138's reader defaults to '1'); del / pop = ON. Every binding of
    the Python name VALIDATOR_ENABLE must be the env reader or False.
  * BIOHUB_REPAIR_DEADLINE_S: every assignment, preset value and get/getenv fallback must be a literal equal to 27000
    (string, int or float); a reader without a fallback needs an earlier assignment; every binding of the Python name
    REPAIR_DEADLINE_S must be the env reader or 27000; the guard itself must exist.
  * Any other use of either key (in a tuple, passed to a helper, inside a code-like string, in a cell that does not
    parse, ...) cannot be verified and FAILS.
  * Sweep / pass-2 rewrite markers: x138 itself carries a dormant PP sweep + re-write block (PP_SWEEP_KEYS,
    BIOHUB_PPSWEEP_*, 'Re-writing submission.csv', os.environ["BIOHUB_" + key] = ...) that runs only with the validator
    on. A marker hit in code therefore passes only as a whitespace-normalised copy of an x138 v1 code line, counted with
    multiplicity (the x138 notebook is pinned by sha256). Every other code hit FAILS. Hits in comments and in bare string
    statements (docstrings) are INFO.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import math
import re
import sys
import tokenize
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import dummy_gates  # noqa: E402  (validate_csv is used as is; its default behaviour must not change)

GROUPS = ("metadata", "notebook-bytes", "source", "dummy-log", "csv", "node-counts")
PASS, FAIL, SKIP, INFO = "PASS", "FAIL", "SKIP", "INFO"

PORT_ID_PREFIX = "vitaliineibauer/biohub-exp63-succ-"
SOURCE_KEYS = ("dataset_sources", "model_sources", "competition_sources", "kernel_sources")
KEEP_KEYS = ("docker_image", "machine_shape", "enable_gpu")
PORT_MAY_DIFFER = frozenset({"id", "id_no", "title", "is_private", "enable_internet", "code_file"})
_MISSING = object()

KEY_VALIDATOR = "BIOHUB_VALIDATOR_ENABLE"
KEY_DEADLINE = "BIOHUB_REPAIR_DEADLINE_S"
ENV_KEYS = (KEY_VALIDATOR, KEY_DEADLINE)
NAME_VALIDATOR = "VALIDATOR_ENABLE"
NAME_DEADLINE = "REPAIR_DEADLINE_S"
PY_NAMES = {NAME_VALIDATOR: KEY_VALIDATOR, NAME_DEADLINE: KEY_DEADLINE}
DEADLINE_S = 27000
ASSIGN_KINDS = ("assign", "preset", "keyword")

# x138 v1 (anvithpothula/biohub-x138, now biohub-0-953-lb-original v1; md5 97e22a53...) = our exp56 notebook
X138_SHA256 = "6b655e39bbfd2d3d6c762badea69847d3f00f5b548f385cb01b07ee2600fde6d"
X138_REFS = (ROOT / "experiments" / "ext_x138" / "biohub-x138.ipynb",
             ROOT / "experiments" / "exp56_x138_verbatim" / "exp56-x138-verbatim.ipynb")

MARKERS = (
    ("BIOHUB_REWRITE_*", re.compile(r"BIOHUB_REWRITE_\w*")),
    ("BIOHUB_SWEEP_*", re.compile(r"BIOHUB_SWEEP_\w*")),
    ("PPSWEEP", re.compile(r"pp_?sweep", re.I)),
    ("sweep", re.compile(r"sweep", re.I)),
    ("Re-writing submission.csv", re.compile(r"Re-writing submission\.csv")),
    ("rewrite", re.compile(r"re-?writ", re.I)),
    ("pass-2", re.compile(r"\bpass[-_ ]?(?:2|two)\b|\bsecond[-_ ]pass\b", re.I)),
    ("score_validator_config", re.compile(r"\bscore_validator_config\b")),   # in-kernel metric scoring of configs
    ("write_test_submission", re.compile(r"\bwrite_test_submission\b")),     # a second writer call = pass-2 rewrite
    ("selected_config", re.compile(r"\bselected_config\b")),                 # sweep-picked config that triggers it
)
DYNAMIC_ENV = "dynamic os.environ write"

LOG_REQUIRED = ("VALIDATOR: disabled (BIOHUB_VALIDATOR_ENABLE=0).", "enabled=False")
LOG_FORBIDDEN = ("DEADLINE:", "Re-writing submission.csv", "POST-PROCESS SWEEP", "SWEEP TABLE")
CSV_NEED = ("dataset", "row_type", "node_id", "z", "y", "x")
NODE_TOL_PCT = 1

MAGIC_RX = re.compile(r"^\s*(?:%%?[A-Za-z_]|!(?!=))")
ENV_MAGIC_RX = re.compile(r"^\s*%(?:env|set_env)\s+(?P<key>\w+)(?:\s*=\s*|\s+)(?P<val>.*?)\s*$")
CODEY_RX = re.compile(r"environ|getenv|putenv")
DYN_RX = re.compile(r"environ\s*\[(?!\s*(['\"])\w*\1\s*\])[^\]]*\]\s*=(?!=)"
                    r"|environ\s*\.\s*(?:update|clear|popitem|setdefault|pop)\s*\(|(?:put|unset)env\s*\(")


@dataclass
class Line:
    group: str
    status: str
    msg: str
    details: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Val:
    lit: bool
    value: object
    src: str


@dataclass
class Event:
    key: str
    kind: str          # assign | preset | keyword | unset | reader | mention | unresolved
    line: int
    col: int
    form: str
    val: Val | None = None


@dataclass
class Binding:
    name: str
    line: int
    col: int
    val: Val | None    # None = augmented or unpacked assignment (never accepted)
    reads_env: bool    # the right-hand side reads the matching env key


@dataclass
class Hit:
    line: int
    names: tuple[str, ...]
    where: str         # code | comment | bare string
    norm: str          # whitespace-normalised code part (the baseline key)


@dataclass
class Code:
    path: Path
    n_cells: int
    lines: list[str]
    cell_of: list[int]
    events: list[Event]
    bindings: list[Binding]
    hits: list[Hit]
    notes: list[str]


# ---------------------------------------------------------------------------------------------------------- helpers

def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _cut(s: str, limit: int = 160) -> str:
    return s if len(s) <= limit else s[: limit - 3] + "..."


def _src(node: ast.AST | None, limit: int = 100) -> str:
    if node is None:
        return "<none>"
    try:
        return _cut(ast.unparse(node), limit)
    except Exception:  # noqa: BLE001
        return type(node).__name__


def _val(node: ast.AST | None) -> Val | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float, bool)):
        return Val(True, node.value, repr(node.value))
    return Val(False, None, _src(node))


def _is_zero(v: object) -> bool:
    return v == "0" or (type(v) is int and v == 0)


def _is_deadline(v: object) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return v == DEADLINE_S
    try:
        return float(str(v)) == DEADLINE_S
    except ValueError:
        return False


def _func_name(call: ast.Call) -> str | None:
    f = call.func
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None


def _is_environ(node: ast.AST) -> bool:
    return ((isinstance(node, ast.Attribute) and node.attr == "environ")
            or (isinstance(node, ast.Name) and node.id == "environ"))


def _str_const(node: ast.AST | None, value: str | None = None) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str) and (value is None or node.value == value)


def _reads_env(expr: ast.AST, key: str) -> bool:
    for n in ast.walk(expr):
        if isinstance(n, ast.Call) and _func_name(n) in ("get", "getenv") and n.args and _str_const(n.args[0], key):
            return True
        if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Load) and _str_const(n.slice, key):
            return True
    return False


def _pos(x) -> tuple[int, int]:
    return (x.line, x.col)


def load_meta(d: Path) -> tuple[dict | None, str]:
    p = Path(d) / "kernel-metadata.json"
    if not p.is_file():
        return None, f"{p} not found"
    try:
        m = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, f"{p}: {e}"
    return (m, "") if isinstance(m, dict) else (None, f"{p}: not a JSON object")


def find_notebook(d: Path) -> tuple[Path | None, str]:
    d = Path(d)
    if not d.is_dir():
        return None, f"{d} is not a directory"
    meta, _ = load_meta(d)
    cf = meta.get("code_file") if meta else None
    if isinstance(cf, str) and cf:
        p = d / cf
        return (p, "") if p.is_file() else (None, f"code_file {cf!r} not found in {d}")
    nbs = sorted(d.glob("*.ipynb"))
    if len(nbs) == 1:
        return nbs[0], ""
    return None, f"no code_file in kernel-metadata.json and {len(nbs)} *.ipynb files in {d}"


# ------------------------------------------------------------------------------------------------- notebook parsing

def code_cells(nb_path: Path) -> list[str]:
    nb = json.loads(Path(nb_path).read_text(encoding="utf-8"))
    if not isinstance(nb, dict) or not isinstance(nb.get("cells"), list):
        raise ValueError("not an nbformat-4 notebook (no 'cells' list)")
    out = []
    for c in nb["cells"]:
        if isinstance(c, dict) and c.get("cell_type") == "code":
            s = c.get("source", "")
            out.append("".join(s) if isinstance(s, list) else str(s))
    return out


def _neutralize(cell_lines: list[str]) -> tuple[str, list[tuple[int, str]]]:
    """IPython line magics / shell escapes -> 'pass' (same indentation, same line numbers)."""
    out, magic = [], []
    for i, ln in enumerate(cell_lines, 1):
        if MAGIC_RX.match(ln):
            magic.append((i, ln))
            out.append(ln[: len(ln) - len(ln.lstrip())] + "pass")
        else:
            out.append(ln)
    return "\n".join(out), magic


def _comment_cols(src: str) -> dict[int, int] | None:
    cols: dict[int, int] = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                cols[tok.start[0]] = tok.start[1]
    except Exception:  # noqa: BLE001  tokenizer trouble -> treat every line as code (stricter)
        return None
    return cols


def _exact_key_event(c: ast.Constant, key: str, off: int) -> Event:
    p = getattr(c, "_e10_parent", None)
    line, col = off + c.lineno - 1, c.col_offset

    def ev(kind: str, form: str, val: Val | None = None) -> Event:
        return Event(key, kind, line, col, form, val)

    if isinstance(p, ast.Subscript) and p.slice is c:
        obj = _src(p.value, 40)
        if isinstance(p.ctx, ast.Load):
            return ev("reader", f"{obj}[...] read")
        if isinstance(p.ctx, ast.Del):
            return ev("unset", f"del {obj}[...]")
        stmt = getattr(p, "_e10_parent", None)
        if isinstance(stmt, ast.Assign) and any(t is p for t in stmt.targets):
            return ev("assign", f"{obj}[...] =", _val(stmt.value))
        if isinstance(stmt, ast.AnnAssign) and stmt.target is p:
            return ev("assign", f"{obj}[...]: ... =", _val(stmt.value))
        return ev("assign", f"{obj}[...] as the target of a {type(stmt).__name__}", Val(False, None, "<not a plain =>"))
    if isinstance(p, ast.Call) and p.args and p.args[0] is c:
        fn = _func_name(p) or "?"
        second = p.args[1] if len(p.args) > 1 else next(
            (k.value for k in p.keywords if k.arg in ("default", "value")), None)
        head = _src(p.func, 40)
        if fn in ("get", "getenv"):
            return ev("reader", f"{head}(...)", _val(second))
        if fn in ("setdefault", "putenv"):
            return ev("assign", f"{head}(...)", _val(second) or Val(False, None, "<no value>"))
        if fn in ("pop", "unsetenv"):
            return ev("unset", f"{head}(...)")
        return ev("unresolved", f"passed to {fn}(); indirect use cannot be verified")
    if isinstance(p, ast.Dict):
        for k, v in zip(p.keys, p.values):
            if k is c:
                return ev("preset", "dict-literal preset {key: ...}", _val(v))
    if isinstance(p, (ast.Expr, ast.JoinedStr, ast.FormattedValue)):
        return ev("mention", "text of a string")
    where = type(p).__name__ if p is not None else "module"
    return ev("unresolved", f"used inside a {where}; indirect use cannot be verified")


def _bind(target: ast.AST, value: ast.AST | None, off: int, out: list[Binding], plain: bool = True) -> None:
    if isinstance(target, ast.Starred):
        target = target.value
    if isinstance(target, (ast.Tuple, ast.List)):
        for e in target.elts:
            _bind(e, None, off, out, plain=False)
        return
    if isinstance(target, ast.Name):
        name = target.id
    elif isinstance(target, ast.Subscript) and _str_const(target.slice):
        name = target.slice.value            # globals()["REPAIR_DEADLINE_S"] = ...
    else:
        return
    if name not in PY_NAMES:
        return
    line = off + target.lineno - 1
    if not plain or value is None:
        out.append(Binding(name, line, target.col_offset, None, False))
    else:
        out.append(Binding(name, line, target.col_offset, _val(value), _reads_env(value, PY_NAMES[name])))


def _dynamic_env_write(node: ast.AST) -> bool:
    if isinstance(node, ast.Subscript) and _is_environ(node.value) and isinstance(node.ctx, (ast.Store, ast.Del)):
        return not _str_const(node.slice)
    if isinstance(node, (ast.Assign, ast.AugAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        return any(isinstance(t, ast.Attribute) and t.attr == "environ" for t in targets)
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Attribute) and _is_environ(f.value):
            if f.attr == "update":
                static = all(isinstance(a, ast.Dict) and all(k is not None and _str_const(k) for k in a.keys)
                             for a in node.args) and all(k.arg is not None for k in node.keywords)
                return not static
            if f.attr in ("setdefault", "pop"):
                return not (node.args and _str_const(node.args[0]))
            return f.attr in ("clear", "popitem")
        if _func_name(node) in ("putenv", "unsetenv"):
            return not (node.args and _str_const(node.args[0]))
    return False


def _analyze_tree(tree: ast.AST, off: int, events: list[Event], bindings: list[Binding],
                  dyn: set[int], bare: set[int]) -> None:
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child._e10_parent = node  # type: ignore[attr-defined]
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for key in ENV_KEYS:
                if node.value == key:
                    events.append(_exact_key_event(node, key, off))
                elif key in node.value:
                    codey = bool(CODEY_RX.search(node.value))
                    events.append(Event(key, "unresolved" if codey else "mention", off + node.lineno - 1,
                                        node.col_offset, "inside a code-like string (environ/getenv/putenv)"
                                        if codey else "text of a string"))
        elif isinstance(node, ast.keyword) and node.arg in ENV_KEYS:
            events.append(Event(node.arg, "keyword", off + node.lineno - 1, node.col_offset,
                                f"keyword argument {node.arg}=", _val(node.value)))
        elif isinstance(node, (ast.Name, ast.Attribute)):
            name = node.id if isinstance(node, ast.Name) else node.attr
            if name in ENV_KEYS:
                events.append(Event(name, "unresolved", off + node.lineno - 1, node.col_offset,
                                    f"Python name {name}; indirect use cannot be verified"))
        if isinstance(node, ast.Assign):
            for t in node.targets:
                _bind(t, node.value, off, bindings)
        elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)):
            _bind(node.target, node.value, off, bindings)
        elif isinstance(node, ast.AugAssign):
            _bind(node.target, None, off, bindings, plain=False)
        if isinstance(node, ast.Expr) and _str_const(node.value):
            bare.update(range(off + node.lineno - 1, off + (node.end_lineno or node.lineno)))
        if _dynamic_env_write(node):
            dyn.add(off + node.lineno - 1)


def analyze_notebook(nb_path: Path) -> Code:
    cells = code_cells(nb_path)
    lines: list[str] = []
    cell_of: list[int] = []
    events: list[Event] = []
    bindings: list[Binding] = []
    hits: list[Hit] = []
    notes: list[str] = []
    off = 1
    for ci, src in enumerate(cells):
        cl = src.split("\n")
        tree, used, magic = None, src, []
        try:
            tree = ast.parse(src)
        except SyntaxError:
            neutral, magic = _neutralize(cl)
            try:
                tree, used = ast.parse(neutral), neutral
                notes.append(f"cell {ci}: {len(magic)} IPython magic / shell line(s) neutralised before parsing")
            except SyntaxError as e:
                notes.append(f"cell {ci} (L{off}-L{off + len(cl) - 1}) does not parse as Python ({e.msg}, cell line "
                             f"{e.lineno}); regex fallback: every key occurrence there is unverifiable")
                magic = []
        dyn: set[int] = set()
        bare: set[int] = set()
        if tree is not None:
            _analyze_tree(tree, off, events, bindings, dyn, bare)
            for i, text in magic:
                m = ENV_MAGIC_RX.match(text)
                for key in ENV_KEYS:
                    if key not in text:
                        continue
                    if m and m.group("key") == key:
                        events.append(Event(key, "assign", off + i - 1, 0, "%env magic",
                                            Val(True, m.group("val"), repr(m.group("val")))))
                    else:
                        events.append(Event(key, "unresolved", off + i - 1, 0, "IPython magic / shell line"))
            ccols = _comment_cols(used)
        else:
            for i, text in enumerate(cl):
                for key in ENV_KEYS:
                    for m in re.finditer(re.escape(key), text):
                        events.append(Event(key, "unresolved", off + i, m.start(), "in a cell that does not parse"))
                if DYN_RX.search(text):
                    dyn.add(off + i)
            ccols = None
        for i, text in enumerate(cl):
            ln = off + i
            cc = ccols.get(i + 1) if ccols is not None else None
            code_part, comment = (text, "") if cc is None else (text[:cc], text[cc:])
            names = [n for n, rx in MARKERS if rx.search(code_part)]
            if ln in dyn:
                names.append(DYNAMIC_ENV)
            if names:
                hits.append(Hit(ln, tuple(names), "bare string" if ln in bare else "code", " ".join(code_part.split())))
            else:
                cnames = [n for n, rx in MARKERS if rx.search(comment)]
                if cnames:
                    hits.append(Hit(ln, tuple(cnames), "comment", ""))
        lines.extend(cl)
        cell_of.extend([ci] * len(cl))
        off += len(cl)
    events.sort(key=_pos)
    bindings.sort(key=_pos)
    return Code(Path(nb_path), len(cells), lines, cell_of, events, bindings, hits, notes)


@lru_cache(maxsize=None)
def _x138_baseline(ref: Path | None) -> tuple[Counter | None, str]:
    for p in ((Path(ref),) if ref is not None else X138_REFS):
        if p.is_file():
            got = sha256(p)
            if got != X138_SHA256:
                return None, f"{p} has sha256 {got[:16]}..., not the pinned x138 v1 {X138_SHA256[:16]}..."
            return Counter(h.norm for h in analyze_notebook(p).hits if h.where == "code"), str(p)
    return None, "no x138 reference notebook found"


# ------------------------------------------------------------------------------------------------------ source group

def _at(code: Code, line: int) -> str:
    return f"L{line} c{code.cell_of[line - 1]}"


def _text(code: Code, line: int) -> str:
    return _cut(code.lines[line - 1].strip())


def _check_validator(code: Code) -> Line:
    ev = [e for e in code.events if e.key == KEY_VALIDATOR]
    assigns = [e for e in ev if e.kind in ASSIGN_KINDS]
    readers = [e for e in ev if e.kind == "reader"]
    problems, details = [], []
    for e in ev:
        if e.kind in ASSIGN_KINDS:
            ok = e.val is not None and e.val.lit and _is_zero(e.val.value)
            shown = e.val.src if e.val else "<no value>"
            tag = f"ok {e.kind} {shown}" if ok else f"BAD {e.kind} {shown}, must be the literal '0'"
            if not ok:
                problems.append(f"L{e.line} {e.form} {shown} (must be the literal '0')")
        elif e.kind == "reader":
            tag = f"reader, fallback {e.val.src if e.val else '<none>'}"
        elif e.kind == "unset":
            tag = "BAD unset (missing = ON)"
            problems.append(f"L{e.line} {e.form} unsets it (missing = ON)")
        elif e.kind == "unresolved":
            tag = f"BAD {e.form}"
            problems.append(f"L{e.line} {e.form}")
        else:
            tag = "info: text mention"
        details.append(f"{_at(code, e.line)} [{tag}] {_text(code, e.line)}")
    if not assigns:
        problems.append("no assignment at all: a missing assignment counts as ON (x138's reader defaults to '1')")
    elif readers:
        first = min(readers, key=_pos)
        if not any(_pos(a) < _pos(first) for a in assigns):
            problems.append(f"no assignment before the first reader at L{first.line}")
    for b in (b for b in code.bindings if b.name == NAME_VALIDATOR):
        ok = b.val is not None and (b.reads_env or (b.val.lit and b.val.value is False))
        shown = b.val.src if b.val else "<augmented or unpacked>"
        details.append(f"{_at(code, b.line)} [{'ok' if ok else 'BAD'} Python name {b.name}] {_text(code, b.line)}")
        if not ok:
            problems.append(f"L{b.line} binds {b.name} to {shown} (only the env reader or False)")
    if problems:
        return Line("source", FAIL, "validator BIOHUB_VALIDATOR_ENABLE: " + "; ".join(problems), details)
    first_a = min(assigns, key=_pos)
    tail = f", before the first reader at L{min(readers, key=_pos).line}" if readers else ", no reader found"
    return Line("source", PASS, f"validator BIOHUB_VALIDATOR_ENABLE: {len(assigns)} assignment(s), all '0'; "
                                f"first at L{first_a.line}{tail}", details)


def _check_deadline(code: Code) -> Line:
    ev = [e for e in code.events if e.key == KEY_DEADLINE]
    assigns = [e for e in ev if e.kind in ASSIGN_KINDS]
    readers = [e for e in ev if e.kind == "reader"]
    binds = [b for b in code.bindings if b.name == NAME_DEADLINE]
    first_assign = min(assigns, key=_pos) if assigns else None
    problems, details = [], []
    n_values = 0
    for e in ev:
        if e.kind in ASSIGN_KINDS:
            n_values += 1
            ok = e.val is not None and e.val.lit and _is_deadline(e.val.value)
            shown = e.val.src if e.val else "<no value>"
            tag = f"ok {e.kind} {shown}" if ok else f"BAD {e.kind} {shown}, must be a literal {DEADLINE_S}"
            if not ok:
                problems.append(f"L{e.line} {e.form} {shown} (must be a literal {DEADLINE_S})")
        elif e.kind == "reader":
            if e.val is not None:
                n_values += 1
                ok = e.val.lit and _is_deadline(e.val.value)
                tag = f"{'ok' if ok else 'BAD'} reader fallback {e.val.src}"
                if not ok:
                    problems.append(f"L{e.line} reader fallback {e.val.src} (must be a literal {DEADLINE_S})")
            else:
                ok = first_assign is not None and _pos(first_assign) < _pos(e)
                tag = f"{'ok' if ok else 'BAD'} reader without a fallback"
                if not ok:
                    problems.append(f"L{e.line} reader without a fallback and no earlier assignment")
        elif e.kind == "unset":
            tag = "BAD unset"
            problems.append(f"L{e.line} {e.form} unsets it")
        elif e.kind == "unresolved":
            tag = f"BAD {e.form}"
            problems.append(f"L{e.line} {e.form}")
        else:
            tag = "info: text mention"
        details.append(f"{_at(code, e.line)} [{tag}] {_text(code, e.line)}")
    for b in binds:
        ok = b.val is not None and (b.reads_env or (b.val.lit and _is_deadline(b.val.value)))
        shown = b.val.src if b.val else "<augmented or unpacked>"
        details.append(f"{_at(code, b.line)} [{'ok' if ok else 'BAD'} Python name {b.name}] {_text(code, b.line)}")
        if not ok:
            problems.append(f"L{b.line} binds {b.name} to {shown} (only the env reader or {DEADLINE_S})")
    guard = bool(readers) or any(b.val is not None and b.val.lit and _is_deadline(b.val.value) for b in binds)
    if not guard:
        problems.append(f"no reader of {KEY_DEADLINE} and no {NAME_DEADLINE} = {DEADLINE_S}: the x138 7.5 h deadline "
                        f"guard is missing")
    if problems:
        return Line("source", FAIL, "deadline BIOHUB_REPAIR_DEADLINE_S: " + "; ".join(problems), details)
    return Line("source", PASS, f"deadline BIOHUB_REPAIR_DEADLINE_S: all {n_values} assigned / fallback value(s) == "
                                f"{DEADLINE_S}; {len(readers)} reader(s); {len(binds)} {NAME_DEADLINE} binding(s) ok",
                details)


def _check_markers(code: Code, x138_ref: Path | None) -> Line:
    need_base = any(h.where == "code" for h in code.hits)
    base, base_src = _x138_baseline(x138_ref) if need_base else (Counter(), "not needed")
    budget = Counter(base) if base is not None else Counter()
    n_new = n_base = n_info = 0
    details = []
    for h in code.hits:
        if h.where != "code":
            tag, n_info = f"info: {h.where}", n_info + 1
        elif budget[h.norm] > 0:
            budget[h.norm] -= 1
            tag, n_base = "x138 baseline", n_base + 1
        else:
            tag, n_new = "NEW", n_new + 1
        details.append(f"{_at(code, h.line)} [{tag}] {', '.join(h.names)} | {_text(code, h.line)}")
    msg = (f"sweep/rewrite markers: {n_new} NEW code hit(s), {n_base} x138-baseline hit(s) (x138's dormant PP sweep / "
           f"re-write block; it runs only with the validator on), {n_info} in comments or bare strings (info)")
    if base is None:
        msg += f"; x138 baseline unavailable ({base_src}), so every code hit counts as NEW"
    return Line("source", FAIL if n_new else PASS, msg, details)


def check_source(nb_path: Path, x138_ref: Path | None = None) -> list[Line]:
    try:
        code = analyze_notebook(Path(nb_path))
    except Exception as e:  # noqa: BLE001
        return [Line("source", FAIL, f"cannot read the notebook {nb_path}: {type(e).__name__}: {e}")]
    out = [Line("source", INFO, f"{Path(nb_path).name}: {code.n_cells} code cells joined with a newline = "
                                f"{len(code.lines)} lines; below, L<line> c<code cell> refers to that text")]
    out += [Line("source", INFO, n) for n in code.notes]
    out += [_check_validator(code), _check_deadline(code), _check_markers(code, x138_ref)]
    return out


# ------------------------------------------------------------------------------------------ metadata + notebook bytes

def check_metadata(pulled: Path, port: Path | None = None, version: int | None = None) -> list[Line]:
    G = "metadata"
    out: list[Line] = []
    pm, err = load_meta(Path(pulled))
    if pm is None:
        out.append(Line(G, FAIL, f"pulled: {err}"))
    else:
        out.append(Line(G, INFO, f"pulled: id={pm.get('id')!r} id_no={pm.get('id_no')!r} "
                                 f"code_file={pm.get('code_file')!r} enable_gpu={pm.get('enable_gpu')!r} "
                                 f"machine_shape={pm.get('machine_shape')!r} docker_image={pm.get('docker_image')!r}"))
        bad = []
        for k in SOURCE_KEYS:
            v = pm.get(k, [])
            if not isinstance(v, list):
                bad.append(f"{k} is not a list ({v!r})")
                continue
            bad += [f"{k}[{i}] = {s!r}" for i, s in enumerate(v) if not isinstance(s, str) or not s.strip()]
        sizes = ", ".join(f"{k} {len(pm.get(k) or [])}" for k in SOURCE_KEYS)
        out.append(Line(G, FAIL, f"pulled sources: blank or invalid entries {bad} (P4b(b): P3 FAIL)") if bad else
                   Line(G, PASS, f'pulled sources: no blank "" entry ({sizes})'))
        ks = pm.get("kernel_sources", [])
        out.append(Line(G, PASS, "pulled kernel_sources == []") if ks == [] else
                   Line(G, FAIL, f"pulled kernel_sources = {ks!r}: must be [] (P4c(4): a kernel source floats to its "
                                 f"latest version and can carry a cached CSV)"))
        out.append(Line(G, INFO, "not checked (offline): every source public and listable from our account "
                                 "(P4b(b): kaggle datasets files <ref> / kaggle models get <ref>)"))
    out.append(Line(G, INFO, f"author version: {version} (recorded; the scored version on the notebook page must be "
                             f"this pulled version, P4b(c))" if version is not None else
                    "author version: not given (--version); P4b(c) wants it recorded from the notebook page"))
    if port is None:
        out.append(Line(G, SKIP, "port: no --port given"))
        return out
    qm, err = load_meta(Path(port))
    if qm is None:
        out.append(Line(G, FAIL, f"port: {err}"))
        return out
    pid = qm.get("id")
    id_ok = isinstance(pid, str) and pid.startswith(PORT_ID_PREFIX) and len(pid) > len(PORT_ID_PREFIX)
    out.append(Line(G, PASS if id_ok else FAIL, f"port id {pid!r}" + ("" if id_ok else
                                                                     f": must be {PORT_ID_PREFIX}<author>")))
    if id_ok and pm is not None:
        author = str(pm.get("id", "")).split("/")[0].lower()
        if pid[len(PORT_ID_PREFIX):] != author:
            out.append(Line(G, INFO, f"port id suffix {pid[len(PORT_ID_PREFIX):]!r} != pulled author {author!r}"))
    title = qm.get("title")
    t_ok = isinstance(title, str) and bool(title.strip())
    out.append(Line(G, PASS if t_ok else FAIL, f"port title {title!r}" + ("" if t_ok else ": must be non-empty")))
    if t_ok and isinstance(pid, str) and "/" in pid:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        if slug != pid.split("/", 1)[1]:
            out.append(Line(G, INFO, f"title slug {slug!r} != id slug {pid.split('/', 1)[1]!r} (Kaggle warns on push)"))
    out.append(Line(G, PASS if qm.get("is_private") is True else FAIL,
                    f"port is_private = {qm.get('is_private', '<absent>')!r} (must be true)"))
    out.append(Line(G, PASS if qm.get("enable_internet") is False else FAIL,
                    f"port enable_internet = {qm.get('enable_internet', '<absent>')!r} (must be false)"))
    out.append(Line(G, PASS, "port has no id_no") if "id_no" not in qm else
               Line(G, FAIL, f"port has id_no = {qm['id_no']!r} (delete it)"))
    if pm is None:
        out.append(Line(G, FAIL, "port vs pulled: the pulled kernel-metadata.json is unreadable"))
        return out
    for k in KEEP_KEYS:
        a, b = pm.get(k, "<absent>"), qm.get(k, "<absent>")
        out.append(Line(G, PASS, f"port {k} == pulled ({b!r})") if a == b else
                   Line(G, FAIL, f"port {k} {b!r} != pulled {a!r}"))
    for k in SOURCE_KEYS:
        want = [] if k == "kernel_sources" else sorted(
            s for s in (pm.get(k) or []) if isinstance(s, str) and s.strip())
        got = qm.get(k, [])
        same = isinstance(got, list) and all(isinstance(s, str) for s in got) and sorted(got) == want
        out.append(Line(G, PASS, f"port {k} == pulled non-blank ({len(want)})") if same else
                   Line(G, FAIL, f"port {k} {got!r} != {want!r}" +
                        (" (must be [])" if k == "kernel_sources" else " (the pulled non-blank sources)")))
    other = sorted(k for k in (set(pm) | set(qm)) - PORT_MAY_DIFFER - set(SOURCE_KEYS) - set(KEEP_KEYS)
                   if pm.get(k, _MISSING) != qm.get(k, _MISSING))
    same_keys = sorted((set(pm) | set(qm)) - PORT_MAY_DIFFER - set(SOURCE_KEYS) - set(KEEP_KEYS) - set(other))
    out.append(Line(G, FAIL, "port fields that may not differ but do: " + ", ".join(
        f"{k}: {qm.get(k, '<absent>')!r} vs pulled {pm.get(k, '<absent>')!r}" for k in other)) if other else
               Line(G, PASS, f"port other fields equal the pulled file ({', '.join(same_keys) or 'none'})"))
    return out


def check_notebook_bytes(pulled: Path, port: Path | None) -> list[Line]:
    G = "notebook-bytes"
    if port is None:
        return [Line(G, SKIP, "no --port given")]
    pnb, why = find_notebook(Path(pulled))
    if pnb is None:
        return [Line(G, FAIL, f"pulled notebook: {why}")]
    qm, err = load_meta(Path(port))
    if qm is None:
        return [Line(G, FAIL, f"port: {err}")]
    cf = qm.get("code_file")
    if not isinstance(cf, str) or not cf:
        return [Line(G, FAIL, "port kernel-metadata.json has no code_file")]
    qnb = Path(port) / cf
    if not qnb.is_file():
        return [Line(G, FAIL, f"port code_file {cf!r} not found in {port}")]
    hp, hq = sha256(pnb), sha256(qnb)
    sp, sq = pnb.stat().st_size, qnb.stat().st_size
    if hp == hq:
        return [Line(G, PASS, f"port {cf} is byte-identical to pulled {pnb.name}: sha256 {hq[:16]}..., {sq} bytes")]
    return [Line(G, FAIL, f"port {cf} differs from pulled {pnb.name} (P4c(1) byte-for-byte): sha256 {hq[:16]}... "
                          f"({sq} bytes) vs {hp[:16]}... ({sp} bytes)")]


# ------------------------------------------------------------------------------------------------------- dummy log

def read_log_lines(p: Path) -> list[str]:
    """Kaggle kernel log (JSON list of {stream_name, time, data}); each stream is re-joined before splitting lines.
    Falls back to plain text."""
    txt = Path(p).read_text(encoding="utf-8", errors="replace")
    try:
        recs = json.loads(txt)
    except ValueError:
        return txt.splitlines()
    if not isinstance(recs, list):
        return txt.splitlines()
    streams: dict[str, list[str]] = {}
    for r in recs:
        if isinstance(r, dict):
            streams.setdefault(str(r.get("stream_name", "")), []).append(str(r.get("data", "")))
    return [ln for chunks in streams.values() for ln in "".join(chunks).splitlines()]


def check_dummy_log(dummy: Path | None) -> list[Line]:
    G = "dummy-log"
    if dummy is None:
        return [Line(G, SKIP, "no --dummy given")]
    logs = sorted(Path(dummy).glob("*.log"))
    if not logs:
        return [Line(G, FAIL, f"no *.log in {dummy}")]
    lines = [ln for p in logs for ln in read_log_lines(p)]
    out = [Line(G, INFO, f"{len(lines)} log lines from {', '.join(p.name for p in logs)}")]
    for s in LOG_REQUIRED:
        hits = [_cut(ln.strip()) for ln in lines if s in ln]
        out.append(Line(G, PASS, f"has {s!r} ({len(hits)} line(s))", hits[:3]) if hits else
                   Line(G, FAIL, f"missing {s!r}"))
    for s in LOG_FORBIDDEN:
        hits = [_cut(ln.strip()) for ln in lines if s in ln]
        out.append(Line(G, FAIL, f"{len(hits)} line(s) with {s!r}", hits[:5]) if hits else
                   Line(G, PASS, f"no line with {s!r}"))
    bad = [_cut(ln.strip()) for ln in lines if "Validator:" in ln and "enabled=True" in ln]
    out.append(Line(G, FAIL, "validator summary says enabled=True", bad[:3]) if bad else
               Line(G, PASS, "no 'Validator: ... enabled=True' summary line"))
    return out


# ----------------------------------------------------------------------------------------------------- csv + counts

def scan_csv(p: Path) -> dict:
    """One pass over a submission CSV: per-clip unique node counts, duplicate (dataset, node_id) node rows,
    non-integer node_id, non-finite x/y/z, rows with the wrong field count."""
    s = {"path": Path(p), "fatal": "", "counts": Counter(), "nodes": 0, "dups": 0, "dup_ex": [], "bad_id": 0,
         "bad_id_ex": [], "nonfinite": 0, "nonfinite_ex": [], "ragged": 0, "ragged_ex": [], "sha256": sha256(p)}
    with Path(p).open(encoding="utf-8", newline="") as f:
        rd = csv.reader(f)
        header = next(rd, None)
        if not header:
            s["fatal"] = "empty file"
            return s
        idx = {c: i for i, c in enumerate(header)}
        miss = [c for c in CSV_NEED if c not in idx]
        if miss:
            s["fatal"] = f"header {header} lacks {miss}"
            return s
        i_ds, i_rt, i_id, i_z, i_y, i_x = (idx[c] for c in CSV_NEED)
        width = len(header)
        seen: set[tuple[str, int]] = set()
        for n, row in enumerate(rd, start=2):
            if len(row) != width:
                s["ragged"] += 1
                if len(s["ragged_ex"]) < 3:
                    s["ragged_ex"].append(f"row {n}: {len(row)} fields, header has {width}")
                continue
            if row[i_rt] != "node":
                continue
            s["nodes"] += 1
            try:
                nid = int(row[i_id])
            except ValueError:
                s["bad_id"] += 1
                if len(s["bad_id_ex"]) < 3:
                    s["bad_id_ex"].append(f"row {n}: node_id {row[i_id]!r}")
                continue
            key = (row[i_ds], nid)
            if key in seen:
                s["dups"] += 1
                if len(s["dup_ex"]) < 5:
                    s["dup_ex"].append(f"row {n}: ({row[i_ds]}, {nid}) repeated")
            else:
                seen.add(key)
                s["counts"][row[i_ds]] += 1
            for col, i in (("z", i_z), ("y", i_y), ("x", i_x)):
                try:
                    fin = math.isfinite(float(row[i]))
                except ValueError:
                    fin = False
                if not fin:
                    s["nonfinite"] += 1
                    if len(s["nonfinite_ex"]) < 5:
                        s["nonfinite_ex"].append(f"row {n}: ({row[i_ds]}, {row[i_id]}) {col}={row[i]!r}")
                    break
    return s


def _csv_path(p: Path) -> Path:
    p = Path(p)
    return p if p.is_file() else p / "submission.csv"


def _check_one_csv(who: str, p: Path, out: list[Line]) -> dict | None:
    G = "csv"
    if not p.is_file():
        out.append(Line(G, FAIL, f"{who}: {p} not found"))
        return None
    try:
        ok, why, info = dummy_gates.validate_csv(p)
    except Exception as e:  # noqa: BLE001  validate_csv raises on malformed rows
        ok, why, info = False, f"crashed: {type(e).__name__}: {e}", {}
    summ = (f" ({sum(info['nodes'].values())} nodes in {len(info['nodes'])} clips, {info['edges']} edges, "
            f"{sum(info['forks'].values())} forks)") if info else ""
    out.append(Line(G, PASS if ok else FAIL, f"{who}: dummy_gates.validate_csv -> {why}{summ}"))
    s = scan_csv(p)
    if s["fatal"]:
        out.append(Line(G, FAIL, f"{who}: {s['fatal']}"))
        return s
    if s["ragged"]:
        out.append(Line(G, FAIL, f"{who}: {s['ragged']} row(s) with the wrong field count", s["ragged_ex"]))
    if s["bad_id"]:
        out.append(Line(G, FAIL, f"{who}: {s['bad_id']} node row(s) with a non-integer node_id", s["bad_id_ex"]))
    out.append(Line(G, FAIL, f"{who}: {s['dups']} duplicate (dataset, node_id) node row(s)", s["dup_ex"]) if s["dups"]
               else Line(G, PASS, f"{who}: no duplicate (dataset, node_id) among {s['nodes']} node rows"))
    out.append(Line(G, FAIL, f"{who}: {s['nonfinite']} node row(s) with a non-finite x/y/z", s["nonfinite_ex"])
               if s["nonfinite"] else Line(G, PASS, f"{who}: x/y/z finite on all {s['nodes']} node rows"))
    return s


def check_csvs(dummy: Path | None, author: Path | None) -> tuple[list[Line], dict | None, dict | None]:
    out: list[Line] = []
    ours = auth = None
    if dummy is None:
        out.append(Line("csv", SKIP, "ours: no --dummy given"))
    else:
        ours = _check_one_csv("ours", _csv_path(dummy), out)
    if author is None:
        out.append(Line("csv", SKIP, "author: no --author given"))
    else:
        auth = _check_one_csv("author", _csv_path(author), out)
    return out, ours, auth


def check_node_counts(ours: dict | None, auth: dict | None, both_given: bool = True) -> list[Line]:
    G = "node-counts"
    if not both_given:
        return [Line(G, SKIP, "needs --dummy and --author")]
    if ours is None or auth is None or ours["fatal"] or auth["fatal"]:
        return [Line(G, FAIL, "cannot compare: a CSV is missing or unreadable")]
    o, a = ours["counts"], auth["counts"]
    missing, extra = sorted(set(a) - set(o)), sorted(set(o) - set(a))
    common = sorted(set(a) & set(o))
    bad = [(ds, o[ds], a[ds]) for ds in common if abs(o[ds] - a[ds]) * 100 > NODE_TOL_PCT * a[ds]]
    rel = [abs(o[ds] - a[ds]) / a[ds] if a[ds] else (0.0 if o[ds] == 0 else math.inf) for ds in common]
    worst = max(rel, default=0.0)
    details = [f"{ds}: ours {x} vs author {y} ({(x - y) / y:+.3%})" if y else f"{ds}: ours {x} vs author 0"
               for ds, x, y in bad[:20]]
    details += [f"missing in ours: {ds} (author {a[ds]})" for ds in missing[:20]]
    details += [f"extra in ours: {ds} ({o[ds]})" for ds in extra[:20]]
    msg = (f"{len(common)} common clips; total ours {sum(o.values())} vs author {sum(a.values())}; max |ours - author| "
           f"/ author = {worst:.3%}; {len(bad)} clip(s) beyond {NODE_TOL_PCT}%")
    if missing or extra:
        msg += f"; clip sets differ ({len(missing)} missing, {len(extra)} extra)"
    out = [Line(G, FAIL if (bad or missing or extra) else PASS, msg, details)]
    same = ours["sha256"] == auth["sha256"]
    out.append(Line(G, INFO, f"sha256 {'EQUAL' if same else 'differ'}: ours {ours['sha256'][:16]}... author "
                             f"{auth['sha256'][:16]}... (info only)"))
    return out


# ---------------------------------------------------------------------------------------------------------- driver

def run(pulled: Path, port: Path | None = None, dummy: Path | None = None, author: Path | None = None,
        version: int | None = None, x138_ref: Path | None = None) -> list[Line]:
    pulled = Path(pulled)
    port, dummy, author = (Path(x) if x is not None else None for x in (port, dummy, author))
    lines = check_metadata(pulled, port, version)
    lines += check_notebook_bytes(pulled, port)
    nb, why = find_notebook(pulled)
    lines += check_source(nb, x138_ref) if nb is not None else [Line("source", FAIL, f"pulled notebook: {why}")]
    lines += check_dummy_log(dummy)
    csv_lines, ours, auth = check_csvs(dummy, author)
    lines += csv_lines
    lines += check_node_counts(ours, auth, dummy is not None and author is not None)
    return lines


def group_status(lines: list[Line], group: str) -> str:
    st = [ln.status for ln in lines if ln.group == group]
    return FAIL if FAIL in st else PASS if PASS in st else SKIP


def render(lines: list[Line], header: list[str] | None = None) -> str:
    out = list(header or [])
    for g in GROUPS:
        out.append(f"== {g}: {group_status(lines, g)}")
        for ln in (x for x in lines if x.group == g):
            out.append(f"[{ln.status}] {g}: {ln.msg}")
            out.extend(f"        {d}" for d in ln.details)
    n_fail = sum(ln.status == FAIL for ln in lines)
    out.append("== summary: " + " | ".join(f"{g} {group_status(lines, g)}" for g in GROUPS))
    out.append(f"RESULT: {'FAIL' if n_fail else 'PASS'} ({n_fail} FAIL line(s)); exit code {1 if n_fail else 0}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="E10 PORT RULE gate (P4b + P4c), read-only: local files only.")
    ap.add_argument("--pulled", required=True, type=Path,
                    help="folder from `kaggle kernels pull -m` (author notebook + kernel-metadata.json)")
    ap.add_argument("--port", type=Path, help="our port folder (kernel-metadata.json + its code_file)")
    ap.add_argument("--dummy", type=Path, help="our dummy output folder (*.log + submission.csv)")
    ap.add_argument("--author", type=Path, help="the author's output folder (submission.csv) or the CSV itself")
    ap.add_argument("--version", type=int, help="the author's version number of the pulled notebook (info)")
    ap.add_argument("--x138-ref", type=Path,
                    help=f"x138 v1 notebook for the marker baseline (sha256-pinned; default {X138_REFS[0]})")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(errors="backslashreplace")  # notebook lines may not fit the console code page
    except (AttributeError, ValueError):
        pass
    lines = run(a.pulled, a.port, a.dummy, a.author, a.version, a.x138_ref)
    header = ["E10 PORT GATE (read-only: local files only; no Kaggle call, no push, no submit)"]
    header += [f"  --{k:<8} {v if v is not None else '-'}" for k, v in
               (("pulled", a.pulled), ("port", a.port), ("dummy", a.dummy), ("author", a.author),
                ("version", a.version))]
    print(render(lines, header))
    return 1 if any(ln.status == FAIL for ln in lines) else 0


if __name__ == "__main__":
    sys.exit(main())
