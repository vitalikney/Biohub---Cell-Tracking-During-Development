#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ENG/KER13 -- THE MITO3 DIVISION STAGE, v2, as a plain module on the mount (amendment 22).

v2 EXISTS FOR ONE REASON AND IT IS A DEFECT OF MINE. v1 located its data files with a ONE-LEVEL glob
`/kaggle/input/*/<name>`. The second account mounts a dataset at `/kaggle/input/datasets/<owner>/<slug>/`
-- three levels -- so on the A7a DRY under Mathis (08:4xZ) the booster was on the mount, the glob could
not see it, the stage printed `MITO3_DISARMED: s1_NK_... is on no mount`, and the object shipped version
39's csv byte for byte. The disarm path did exactly what it promised; the shot was void. v2 resolves
EVERY data file relative to its OWN location first and falls back to a RECURSIVE walk of the mount, and
proves both layouts at import.

WHAT IT IS. The terminal post-canon stage that applies MITO3's SHIP row -- MITO2's 89 `nod`
columns + the nine collision columns, k = 1, score floor 0,02, pool window [4 ; 17] judge-um,
mother reach 14,0, flow gate 7,0, test (D) OFF -- to the world it receives, and hands the world
back. It adds NO node : it drops and adds EDGES only, and that is asserted on the way out.

    offline, 199-film out-of-fold plate, sealed judge  delta  +0,0006260843
    division tp 59 -> 61, fp 68 -> 70, priced precision 0,50 (bar 0,3199, amendment 23)
    per embryo  44b6 +0,00000000   6bba +0,00075377   node band 0

WHY IT RUNS BEFORE B AND NOT AFTER (ZEUS 07:1xZ). B cannot create a fork : it freezes the forks it
finds and only ever attaches a 0-child source to a 0-parent target. If this stage ran after B, the
daughters it creates would never be seen by B. Division ADD first, B after.

THE TWO PIECES IT DRIVES, both already on the aux dataset and neither rewritten here :
    mito3_ship.py                                  7c16c9f15bb486b6...  the featuriser + scorer
    s1_NK_ship89_plus_collision_deployed.txt       a8afae9da3365def...  the 98-column booster
    ...txt.names.json                              ab5276d4132c0551...  its column order
`mito3_ship` is GT-guarded at import : it replaces `builtins.open` so that any path containing
`.geff`, `vecteurs_gt`, `juge`, `division_metrics` or `scorer_bundle` raises. That is a PROCESS-WIDE
side effect and it is named here rather than discovered later ; none of the kernel's own paths
contain those tokens, and MITO3 proved the passing direction (same candidates, byte-identical edit
list, on a directory holding the zarr and nothing else).

THE EDIT ARITHMETIC IS MITO3's OWN, copied from `code/mito3_deploy.py` -- the script that built the
EDIT worlds the sealed judge scored. For each selected proposal (mother u, daughters d1, d2) :
    * every child of u that is neither d1 nor d2 is DROPPED ;
    * each daughter's in-edge from any parent other than u is DROPPED (the theft undone) ;
    * u -> d1 and u -> d2 are ADDED where absent ;
    * a mother or a daughter already touched in this film is SKIPPED, highest score first.

AMENDMENT 21 : THIS FUNCTION NEVER RAISES ON DATA. On any exception the world it received is
written out unchanged and `MITO3_DISARMED: <reason>` is printed. A stage that kills a twelve-hour
run because one film surprised it is worth less than no stage at all.
"""
from __future__ import annotations

import collections
import csv as _csv
import glob as _glob
import json
import os
import sys
import time
import traceback
from pathlib import Path

SHIP_TOP_K = 1
SHIP_SCORE_MIN = 0.02
SHIP_SEP_LO_UM = 4.0
SHIP_SEP_HI_UM = 17.0
SHIP_REACH_UM = 14.0
SHIP_FLOW_GATE = 7.0
MODEL_BASENAME = "s1_NK_ship89_plus_collision_deployed.txt"


# Every data file this stage needs, declared ONCE so the manifest and the
# resolution report can be read against each other file by file.
DATA_FILES = (
    "mito3_ship.py",                                     # the featuriser + scorer
    MODEL_BASENAME,                                      # the 98-column booster
    MODEL_BASENAME + ".names.json",                      # its column order
)


def _resolve(basename, roots=None):
    """Find one data file. OWN DIRECTORY FIRST, then the mount, RECURSIVELY.

    WHY v2 EXISTS, in one sentence: v1 globbed `/kaggle/input/*/<name>`, one
    level deep, and the second account mounts its datasets at
    `/kaggle/input/datasets/<owner>/<slug>/` -- three levels -- so the booster
    was on the mount, the glob could not see it, and the stage disarmed on a
    file that was right there (DRY of A7a under Mathis, 08:4xZ).

    The order is deliberate:
      1. `Path(__file__).parent` -- the directory this module was loaded from.
         Every file it needs ships in the SAME dataset, so on any layout,
         present or future, this hits first and no glob runs at all.
      2. a RECURSIVE walk of each mount root, so a layout nobody has seen yet
         still resolves.
    `KER13_MOUNT_ROOTS` (os.pathsep-separated) replaces the roots for the
    offline bench. It is a test seam, never a knob: unset in the kernel.
    """
    here = Path(__file__).resolve().parent
    own = here / basename
    if own.exists():
        return str(own)
    if roots is None:
        raw = os.environ.get("KER13_MOUNT_ROOTS", "").strip()
        roots = [r for r in raw.split(os.pathsep) if r] or ["/kaggle/input"]
    for root in roots:
        hits = sorted(_glob.glob(os.path.join(root, "**", basename),
                                 recursive=True))
        if hits:
            return hits[0]
    return None


def resolve_all(roots=None):
    """Where every declared data file resolves, or None. For the receipt."""
    return {name: _resolve(name, roots) for name in DATA_FILES}


def _resolve_data_dir(explicit=None, film=None):
    """Where the films' `<film>.zarr` live.

    A directory that exists is NOT enough -- v1 would have accepted one holding
    no film at all. When `film` is given, a candidate is kept only if
    `<candidate>/<film>.zarr` is really there ; otherwise the tree is walked for
    that exact name and its parent is used. Same lesson as the mount: assume no
    layout, verify the file.
    """
    cands = []
    if explicit:
        cands.append(str(explicit))
    for key in ("BIOHUB_TEST_DIR", "MITO3_DATA_DIR"):
        v = os.environ.get(key, "").strip()
        if v:
            cands.append(v)
    if film is None:
        for c in cands:
            if Path(c).exists():
                return c
        return None
    target = film + ".zarr"
    for c in cands:
        if (Path(c) / target).exists():
            return c
    for c in cands:                       # the film is somewhere under it
        if not Path(c).exists():
            continue
        hits = sorted(_glob.glob(os.path.join(c, "**", target), recursive=True))
        if hits:
            return os.path.dirname(hits[0])
    return None


def score_one_film(csv_in, film, data_dir, model, out_dir, log=print):
    """Drive `mito3_ship.main()` on ONE film. Returns its score json as a dict."""
    import mito3_ship                                    # noqa: F401  (GT guard at import)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    score_out = out_dir / (film + ".score.json")
    argv = [
        "mito3_ship", "--csv", str(csv_in), "--film", film,
        "--out", str(out_dir), "--data-dir", str(data_dir),
        "--score-model", str(model), "--score-out", str(score_out),
        "--top-k", str(SHIP_TOP_K), "--score-min", str(SHIP_SCORE_MIN),
        "--sep-lo-um", str(SHIP_SEP_LO_UM), "--sep-hi-um", str(SHIP_SEP_HI_UM),
        "--reach-um", str(SHIP_REACH_UM), "--flow-gate", str(SHIP_FLOW_GATE),
    ]
    keep = sys.argv
    try:
        sys.argv = argv
        rc = mito3_ship.main()
    finally:
        sys.argv = keep
    if rc != 0:
        raise RuntimeError("mito3_ship returned %r on %s" % (rc, film))
    return json.loads(score_out.read_text(encoding="utf-8"))


def apply_edits(rows, header, proposals_by_film, log=print):
    """MITO3's own edit arithmetic (mito3_deploy.py), on rows read from the csv.

    `rows` is the body, `header` the column names. Returns (new_rows, report).
    NODES ARE NEVER TOUCHED -- asserted by the caller on the counts.
    """
    ic = {c: i for i, c in enumerate(header)}
    by_film = collections.OrderedDict()
    for r in rows:
        by_film.setdefault(r[ic["dataset"]], []).append(r)
    next_id = max((int(r[ic["id"]]) for r in rows
                   if r[ic["id"]].lstrip("-").isdigit()), default=0)
    out, tot = [], collections.Counter()
    per_film = {}
    for film, body in by_film.items():
        nodes = [r for r in body if r[ic["row_type"]] == "node"]
        edges = [r for r in body if r[ic["row_type"]] == "edge"]
        kids = collections.defaultdict(list)
        par = {}
        for r in edges:
            s, d = int(r[ic["source_id"]]), int(r[ic["target_id"]])
            kids[s].append(d)
            par[d] = s
        drop, add, touched = set(), [], set()
        classes = collections.Counter()
        for p in proposals_by_film.get(film, []):
            u, d1, d2 = int(p["u"]), int(p["d1"]), int(p["d2"])
            if d1 in kids[u] and d2 in kids[u]:
                classes["ALREADY_PRESENT"] += 1
                continue
            if {u, d1, d2} & touched:
                classes["CONFLICT_SKIPPED"] += 1
                continue
            classes["APPLIED"] += 1
            for c in list(kids[u]):
                if c not in (d1, d2):
                    drop.add((u, c))
            for d in (d1, d2):
                if d in par and par[d] != u:
                    drop.add((par[d], d))
            add += [(u, d1), (u, d2)]
            touched |= {u, d1, d2}
        kept = [r for r in edges
                if (int(r[ic["source_id"]]), int(r[ic["target_id"]])) not in drop]
        have = {(int(r[ic["source_id"]]), int(r[ic["target_id"]])) for r in kept}
        new = []
        for (s, d) in add:
            if (s, d) in have:
                continue
            next_id += 1
            rr = ["-1"] * len(header)
            rr[ic["id"]] = str(next_id)
            rr[ic["dataset"]] = film
            rr[ic["row_type"]] = "edge"
            rr[ic["source_id"]] = str(s)
            rr[ic["target_id"]] = str(d)
            new.append(rr)
            have.add((s, d))
        # THE TWO INVARIANTS OF THE WORLD, checked on the FILM that was edited
        after = kept + new
        indeg = collections.Counter(int(r[ic["target_id"]]) for r in after)
        outdeg = collections.Counter(int(r[ic["source_id"]]) for r in after)
        ref_out = collections.Counter(int(r[ic["source_id"]]) for r in edges)
        if indeg and max(indeg.values()) > 1:
            raise RuntimeError("in-degree > 1 on %s after the edit" % film)
        bad = [u for u, v in outdeg.items() if v > max(2, ref_out.get(u, 0))]
        if bad:
            raise RuntimeError("out-degree grew beyond 2 on %s : %s" % (film, bad[:5]))
        out += nodes + after
        per_film[film] = {"nodes": len(nodes), "edges_in": len(edges),
                          "edges_out": len(after), "dropped": len(drop),
                          "added": len(new), "classes": dict(classes),
                          "proposals": len(proposals_by_film.get(film, []))}
        tot.update(classes)
        tot["dropped"] += len(drop)
        tot["added"] += len(new)
        tot["proposals"] += len(proposals_by_film.get(film, []))
    return out, {"per_film": per_film, "totals": dict(tot)}


def run(csv_in, csv_out, data_dir=None, model=None, work_dir=None, films=None,
        log=print):
    """The stage. NEVER raises : on any exception the world comes through unchanged."""
    t0 = time.time()
    csv_in, csv_out = str(csv_in), str(csv_out)
    try:
        # THE RESOLUTION IS REPORTED FILE BY FILE, always, armed or not : the
        # failure of 08:4xZ was invisible until the trace was read, and a stage
        # that cannot say where it looked cannot be debugged from a kernel log.
        found = resolve_all()
        for _n, _p in sorted(found.items()):
            log("MITO3_RESOLVE %-48s %s" % (_n, _p or "NOT FOUND"))
        missing = sorted(n for n, p in found.items() if not p)
        if missing:
            raise FileNotFoundError(
                "not resolved from %s nor under %s : %s"
                % (Path(__file__).resolve().parent,
                   os.environ.get("KER13_MOUNT_ROOTS", "/kaggle/input"), missing))
        model = model or found[MODEL_BASENAME]
        # mito3_ship builds the names path as `score_model + ".names.json"`, so
        # the two MUST sit in one directory. Checked here, with a clear reason,
        # rather than dying inside the featuriser on a bare open().
        if not Path(model + ".names.json").exists():
            raise FileNotFoundError(
                "the booster resolved to %s but its .names.json is not beside it "
                "-- mito3_ship builds that path by concatenation" % model)
        ship = found["mito3_ship.py"]
        sys.path.insert(0, os.path.dirname(ship))
        want_data_dir = data_dir
        work_dir = Path(work_dir or (Path(csv_out).parent / "_mito3"))
        work_dir.mkdir(parents=True, exist_ok=True)

        with open(csv_in, newline="", encoding="utf-8") as fh:
            rows = [r for r in _csv.reader(fh) if r]
        header, body = rows[0], rows[1:]
        ic = {c: i for i, c in enumerate(header)}
        seen = films or sorted({r[ic["dataset"]] for r in body})
        n_nodes_in = sum(1 for r in body if r[ic["row_type"]] == "node")

        # THE ZARR, resolved against the FIRST FILM'S OWN NAME and not against a
        # directory that merely exists -- same lesson as the mount.
        data_dir = _resolve_data_dir(want_data_dir, film=seen[0] if seen else None)
        if not data_dir:
            raise FileNotFoundError(
                "no directory holding %s.zarr (tried %r and BIOHUB_TEST_DIR=%r, "
                "then a recursive walk of each)"
                % (seen[0] if seen else "<no film>", want_data_dir,
                   os.environ.get("BIOHUB_TEST_DIR")))
        log("MITO3_RESOLVE %-48s %s" % ("<film>.zarr directory", data_dir))

        props = {}
        for film in seen:
            sc = score_one_film(csv_in, film, data_dir, model, work_dir, log=log)
            props[film] = sc.get("top_k_selected", [])
            log("MITO3 film=%s candidates=%s selected=%d"
                % (film, sc.get("candidates"), len(props[film])))

        new_body, report = apply_edits(body, header, props, log=log)
        n_nodes_out = sum(1 for r in new_body if r[ic["row_type"]] == "node")
        if n_nodes_out != n_nodes_in:
            raise RuntimeError("the node set moved : %d -> %d"
                               % (n_nodes_in, n_nodes_out))
        with open(csv_out, "w", newline="", encoding="utf-8") as fh:
            w = _csv.writer(fh, lineterminator="\n")
            w.writerow(header)
            w.writerows(new_body)
        report["armed"] = True
        report["wall_s"] = round(time.time() - t0, 2)
        report["model"] = str(model)
        report["resolved"] = found
        report["data_dir"] = str(data_dir)
        report["films"] = list(seen)
        log("MITO3_ARMED films=%d proposals=%d applied=%d dropped=%d added=%d %.1f s"
            % (len(seen), report["totals"].get("proposals", 0),
               report["totals"].get("APPLIED", 0), report["totals"].get("dropped", 0),
               report["totals"].get("added", 0), report["wall_s"]))
        return report
    except BaseException as e:                                    # noqa: BLE001
        reason = "%s: %s" % (type(e).__name__, str(e)[:300])
        try:
            Path(csv_out).write_bytes(Path(csv_in).read_bytes())
        except BaseException:                                     # noqa: BLE001
            pass
        log("MITO3_DISARMED: %s" % reason)
        log("MITO3_TRACE: %s" % traceback.format_exc()[-800:].replace("\n", " | "))
        return {"armed": False, "reason": reason,
                "wall_s": round(time.time() - t0, 2)}


# --- amendment 8 : both directions, proven at import, on the arithmetic ------
_H = ["id", "dataset", "row_type", "node_id", "t", "z", "y", "x",
      "source_id", "target_id"]


def _node(i, f, nid, t):
    return [str(i), f, "node", str(nid), str(t), "0", "0", "0", "-1", "-1"]


def _edge(i, f, s, d):
    return [str(i), f, "edge", "-1", "-1", "-1", "-1", "-1", str(s), str(d)]


# a world where mother 1 has ONE child (2) and node 3 at the same frame is stolen
# by node 9. The proposal (1, 2, 3) must drop 9->3 and add 1->3.
_ROWS = ([_node(0, "F", 1, 0), _node(1, "F", 2, 1), _node(2, "F", 3, 1),
          _node(3, "F", 9, 0)]
         + [_edge(4, "F", 1, 2), _edge(5, "F", 9, 3)])
_OUT, _REP = apply_edits([list(r) for r in _ROWS], _H,
                         {"F": [{"u": 1, "d1": 2, "d2": 3, "t": 0, "score": 0.9}]})
_E = [(int(r[8]), int(r[9])) for r in _OUT if r[2] == "edge"]
if sorted(_E) != [(1, 2), (1, 3)]:
    raise SystemExit("[ker13] the MITO3 edit arithmetic does not undo a theft : %s" % _E)
if _REP["totals"].get("APPLIED") != 1 or _REP["totals"].get("added") != 1 \
        or _REP["totals"].get("dropped") != 1:
    raise SystemExit("[ker13] the MITO3 edit report is wrong : %s" % _REP["totals"])
# and the REFUSING direction : a proposal whose two daughters are already the
# mother's children must change NOTHING.
_OUT2, _REP2 = apply_edits([list(r) for r in _ROWS], _H,
                           {"F": [{"u": 1, "d1": 2, "d2": 2, "t": 0, "score": 0.9}]})
if [(int(r[8]), int(r[9])) for r in _OUT2 if r[2] == "edge"] != [(1, 2), (9, 3)]:
    raise SystemExit("[ker13] a no-op proposal changed the world. STOP.")
if _REP2["totals"].get("ALREADY_PRESENT") != 1:
    raise SystemExit("[ker13] a no-op proposal was not classified ALREADY_PRESENT. STOP.")
del _OUT, _REP, _OUT2, _REP2, _E

# --- amendment 8 on the DEFECT THAT COST THE A7a SHOT : the resolver is proven
# --- at import, on BOTH mount layouts, and proven to REFUSE a file that is absent.
import shutil as _shutil                                            # noqa: E402
import tempfile as _tempfile                                        # noqa: E402

_LAYOUTS = {
    # what v1 assumed, and the only shape it could see
    "classic": ("input", "biocel-aux-4d9e2c17"),
    # what the second account actually mounts -- three levels -- and the layout
    # on which v1 disarmed under Mathis at 08:4xZ with the file right there
    "datasets": ("input", "datasets", "corwin1979", "biocel-aux-4d9e2c17"),
}
# A SENTINEL NAME, never a real one. Probing with a REAL basename would resolve
# from the module's own directory once this file sits on the aux beside the
# booster -- the test would then fail on the very layout it is meant to bless.
# A guard that refuses the legitimate case looks like it works.
_PROBE = "_ker13_resolve_probe.bin"
_tmp = _tempfile.mkdtemp(prefix="ker13_resolve_")
try:
    for _lay, _parts in _LAYOUTS.items():
        _d = Path(_tmp) / _lay
        for _p in _parts:
            _d = _d / _p
        _d.mkdir(parents=True, exist_ok=True)
        (_d / _PROBE).write_text("x", encoding="utf-8")
        _root = str(Path(_tmp) / _lay / "input")
        _hit = _resolve(_PROBE, roots=[_root])
        if not _hit or Path(_hit).resolve() != (_d / _PROBE).resolve():
            raise SystemExit(
                "[ker13] the resolver does NOT find a data file on the %r layout "
                "(%s). This is the exact defect that voided the A7a shot. STOP."
                % (_lay, _hit))
        # the refusing direction : a name on no root must come back None, never
        # a stale hit from elsewhere
        if _resolve("a_file_that_is_on_no_mount_at_all.bin", roots=[_root]) is not None:
            raise SystemExit("[ker13] the resolver invents a file that is absent. STOP.")
    # and the FIRST branch, which is the one that makes the layout irrelevant :
    # the module's own directory must resolve without any root at all.
    _own = _resolve(Path(__file__).name, roots=[str(Path(_tmp) / "empty")])
    if not _own or Path(_own).resolve() != Path(__file__).resolve():
        raise SystemExit("[ker13] the resolver cannot find a file beside itself "
                         "(%s). STOP." % _own)
finally:
    _shutil.rmtree(_tmp, ignore_errors=True)
del _LAYOUTS, _PROBE, _tmp, _lay, _parts, _d, _p, _root, _hit, _own
