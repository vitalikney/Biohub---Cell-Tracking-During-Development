"""E10 PORT RULE P1 watch snapshot (READ-ONLY): public kernels, watched users/notebooks and the public LB histogram.

    python tools/e10_snapshot.py [--out-dir experiments/e10_watch] [--dry-run-from DIR] [--now 2026-09-26T16:05Z]

P1 (CONTEXT.md, 26 Sep 09:03 UTC entry) asks for a light check every ~6 h through 29 Sep 00:00 UTC. One run makes only
read-only Kaggle CLI calls: `kernels list` x5 (competition by dateRun and by scoreDescending, top 20; users
anvithpothula / thtennant / amanatar by dateRun, top 10), `kernels status` x2 (amanatar/optimized-biohub-max-score and
the live x138 slug anvithpothula/biohub-0-953-lb-original) and `competitions leaderboard --download` into a temp folder
that is deleted after parsing. Each command gets up to ATTEMPTS tries (retry on an error, an empty stdout or an
unparseable output; a 404 is final) with a TIMEOUT_S timeout.

It writes <out-dir>/<YYYYMMDDTHHMMZ>.txt (UTC start time) with the raw CLI outputs, the kept leaderboard rows
(Score >= KEEP_MIN), the parsed histogram and, at the end, a DIFF against the newest earlier snapshot in that folder
(the earlier file is re-parsed by the same code, so both sides are read alike). It prints the DIFF section and
'E10-P1 SNAPSHOT <path> CHANGES=<n>'. A change is NOT a port trigger; it only tells the human where to look.
Exit code 0, or 1 when a command still failed after its retries (the snapshot is written anyway).

--dry-run-from DIR replays cached CLI outputs instead of calling the CLI: <key>.out (stdout), optional <key>.err and
<key>.rc (exit code; default 0 when the .out exists) for the keys comp_dateRun, comp_scoreDescending, user_<name>,
status_<owner>__<slug>, and leaderboard.zip or leaderboard.csv (+ optional leaderboard.out/.err/.rc) for the
download. A dry run writes <stamp>-dryrun.txt and makes one attempt per command; a live check never diffs against a
dry-run file.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMP = "biohub-cell-tracking-during-development"
OUT_DIR = ROOT / "experiments" / "e10_watch"
OUR_TEAM, OUR_TEAM_ID = "D: Discipline", "16810638"      # the TeamId is the fallback if the team is renamed
USERS = ("anvithpothula", "thtennant", "amanatar")
X138 = "anvithpothula/biohub-0-953-lb-original"          # live x138 slug; the old anvithpothula/biohub-x138 is a 404
STATUS_REFS = ("amanatar/optimized-biohub-max-score", X138)
WATCH_MIN = Decimal("0.955")                              # histogram bins (P1: teams per public score >= 0.955)
GE_LINES = (Decimal("0.955"), Decimal("0.960"), Decimal("0.970"))
KEEP_MIN = Decimal("0.953")                               # LB rows kept in the file: watch bins, our block, P2 movers
P2_MIN, P2_FROM_MAX, P2_GROUP = Decimal("0.956"), Decimal("0.953"), 5
ATTEMPTS, TIMEOUT_S, RETRY_SLEEP_S = 3, 120, 10
MAX_MOVERS = 25
KERNEL_FIELDS = ("ref", "title", "author", "lastRunTime", "totalVotes")
LB_ARGS = ["competitions", "leaderboard", COMP, "--download", "-p"]
NOTE = "A change is NOT a port trigger; it only tells the human where to look."
SEC_RE = re.compile(r"^======== (.+) ========$")
NAME_RE = re.compile(r"^(?P<stamp>\d{8}T\d{4}Z)(?:-(?P<n>\d+))?(?P<dry>-dryrun)?\.txt$")
STATUS_RE = re.compile(r'has status "([^"]*)"')
TQDM_RE = re.compile(r"^\s*\d+%\|")


def sec(name):
    return f"======== {name} ========"


def queries():
    """(key, kind, CLI args after `kaggle`, what) of the kernel lists and statuses, in file order."""
    q = [(f"comp_{s}", "kernels", ["kernels", "list", "--competition", COMP, "--sort-by", s, "--page-size", "20", "-v"],
          f"public competition kernels, top 20 by {s}") for s in ("dateRun", "scoreDescending")]
    q += [(f"user_{u}", "kernels", ["kernels", "list", "--user", u, "--sort-by", "dateRun", "--page-size", "10", "-v"],
           f"kernels of {u}, top 10 by dateRun") for u in USERS]
    q += [("status_" + r.replace("/", "__"), "status", ["kernels", "status", r], f"kernel status of {r}")
          for r in STATUS_REFS]
    return q


# ---------------------------------------------------------------- parsers (pure)
def parse_kernel_csv(text):
    """`kernels list -v` stdout -> row dicts (ref, title, author, lastRunTime, totalVotes) in CLI order;
    [] for 'No kernels found'; None when there is no CSV header (error text, HTML, warnings only)."""
    lines = (text or "").lstrip("﻿").splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().startswith("ref,"):
            rows = []
            for r in csv.DictReader(io.StringIO("\n".join(lines[i:]))):
                if (r.get("ref") or "").strip():
                    rows.append({k: (r.get(k) or "").strip() for k in KERNEL_FIELDS})
            return rows
    return [] if re.search(r"no kernels found", text or "", re.I) else None


def parse_status(text):
    """`kernels status` stdout -> 'COMPLETE' / 'RUNNING' / 'ERROR' / ... (KernelWorkerStatus. prefix dropped) or None."""
    m = STATUS_RE.search(text or "")
    if not m:
        return None
    s = m.group(1).strip()
    return (s.split(".", 1)[1] if s.startswith("KernelWorkerStatus.") else s).upper()


def q3(s):
    """Public score text -> Decimal rounded to 3 decimals (half up); None when blank or not a number."""
    try:
        d = Decimal(str(s).strip())
    except (InvalidOperation, ValueError):
        return None
    return d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP) if d.is_finite() else None


def parse_lb_csv(text):
    """Leaderboard CSV text -> (fieldnames, rows) or None when there is no Score column."""
    rdr = csv.DictReader(io.StringIO((text or "").lstrip("﻿"), newline=""))
    fields = rdr.fieldnames or []
    if "score" not in {f.strip().lower() for f in fields}:
        return None
    return fields, list(rdr)


def lb_summary(fields, rows, total=None):
    """Histogram of teams per 3-decimal public score. The CSV (Kaggle CLI 2.2.4, checked 26 Sep) has Rank, TeamId,
    TeamName, LastSubmissionDate, Score, SubmissionCount, TeamMemberUserNames; ranks are sequential inside a tied
    score (ties broken by the unrounded score / time) and the host benchmark rows (UNet Baseline, Nearest Neighbor
    Benchmark, Sample Submission) have Rank 0: they are not teams and are left out. Our rank is the CSV Rank (or
    1 + teams with a strictly better score when there is no Rank column). total overrides the team count (the
    snapshot keeps only the rows >= KEEP_MIN)."""
    col = {f.strip().lower(): f for f in fields}

    def g(r, name):
        return (r.get(col[name]) or "").strip() if name in col else ""

    teams, unranked = [], 0
    for r in rows:
        rk = g(r, "rank")
        if rk == "0":
            unranked += 1
            continue
        teams.append({"rank": int(rk) if rk.isdigit() else len(teams) + 1, "id": g(r, "teamid"),
                      "name": g(r, "teamname"), "score": q3(g(r, "score")), "last": g(r, "lastsubmissiondate")})
    scored = [t for t in teams if t["score"] is not None]
    blocks = {}                                              # score -> (first rank, last rank, teams)
    for t in scored:
        lo, hi, n = blocks.get(t["score"], (t["rank"], t["rank"], 0))
        blocks[t["score"]] = (min(lo, t["rank"]), max(hi, t["rank"]), n + 1)
    ours = next((t for t in teams if t["name"] == OUR_TEAM), None) or next(
        (t for t in teams if t["id"] == OUR_TEAM_ID), None)
    if ours is not None:
        better = sum(1 for t in scored if ours["score"] is not None and t["score"] > ours["score"])
        ours = dict(ours, better=better, rank_src="CSV Rank column")
        if "rank" not in col:
            ours.update(rank=better + 1, rank_src="1 + teams with a strictly better score")
    return {"total": len(teams) if total is None else total, "csv_rows": len(rows), "unranked": unranked,
            "hist": {s: b[2] for s, b in blocks.items() if s >= WATCH_MIN},
            "ge": {x: sum(1 for t in scored if t["score"] >= x) for x in GE_LINES},
            "blocks": blocks, "ours": ours,
            "teams": {t["id"] or t["name"]: t for t in scored if t["score"] >= KEEP_MIN}}


def kept_rows_csv(fields, rows):
    """-> (CSV text of the header + rows with Score >= KEEP_MIN, number of kept rows)."""
    col = {f.strip().lower(): f for f in fields}
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(fields)
    k = 0
    for r in rows:
        s = q3(r.get(col["score"]) or "")
        if s is not None and s >= KEEP_MIN:
            w.writerow([r.get(f) or "" for f in fields])
            k += 1
    return buf.getvalue(), k


def read_lb_file(paths):
    """First leaderboard CSV among .zip / .csv paths -> (display name, text) or None."""
    for p in map(Path, paths):
        if p.suffix.lower() == ".zip":
            with zipfile.ZipFile(p) as zf:
                names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
                if names:
                    return f"{p.name}:{names[0]}", zf.read(names[0]).decode("utf-8-sig", errors="replace")
        elif p.suffix.lower() == ".csv":
            return p.name, p.read_bytes().decode("utf-8-sig", errors="replace")
    return None


# ---------------------------------------------------------------- CLI calls
def _classify(out, err, rc, check, need_stdout):
    if rc == 0 and (out.strip() or not need_stdout) and check(out):
        return "OK"
    if rc not in (0, None) and re.search(r"\b404\b", f"{err}\n{out}"):
        return "NOTFOUND"                                   # deterministic: no retry
    return None


def run_cli(key, args, what, check, *, need_stdout=True, before=None, runner=subprocess.run, sleep=time.sleep,
            attempts=ATTEMPTS, timeout=TIMEOUT_S, shown_args=None):
    """`python -m kaggle <args>` with up to `attempts` tries -> fetch dict (state OK / NOTFOUND / FAILED)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    notes, out, err, rc = [], "", "", None
    for i in range(1, attempts + 1):
        if before:
            before()
        try:
            p = runner([sys.executable, "-m", "kaggle", *args], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout, env=env, cwd=str(ROOT))
            out, err, rc = p.stdout or "", p.stderr or "", p.returncode
        except subprocess.TimeoutExpired:
            out, err, rc = "", f"timed out after {timeout} s", None
        except Exception as exc:  # CLI missing, OS error
            out, err, rc = "", f"{type(exc).__name__}: {exc}", None
        state = _classify(out, err, rc, check, need_stdout)
        if state:
            return _fetch(key, what, shown_args or args, out, err, rc, i, state, notes)
        notes.append(f"attempt {i}: rc={rc} stdout={len(out.strip())} chars stderr={' '.join(err.split())[:160]!r}")
        if i < attempts:
            sleep(RETRY_SLEEP_S)
    return _fetch(key, what, shown_args or args, out, err, rc, attempts, "FAILED", notes)


def _fetch(key, what, args, out, err, rc, attempts, state, notes):
    return {"key": key, "what": what, "cmd": "kaggle " + " ".join(args), "stdout": out, "stderr": err, "rc": rc,
            "attempts": attempts, "state": state, "notes": notes}


def fetch_leaderboard(runner=subprocess.run, sleep=time.sleep, attempts=ATTEMPTS):
    """Full public LB download into a temp folder (deleted here) -> fetch dict + 'lb_file' = (name, CSV text)."""
    got = {}
    with tempfile.TemporaryDirectory(prefix="e10_lb_") as tmp:
        d = Path(tmp)

        def clear():
            got.clear()
            for p in d.iterdir():
                shutil.rmtree(p) if p.is_dir() else p.unlink()

        def check(_out):
            try:
                f = read_lb_file(sorted(d.glob("*.zip")) + sorted(d.glob("*.csv")))
            except (zipfile.BadZipFile, OSError):
                return False
            if f and parse_lb_csv(f[1]):
                got["file"] = f
                return True
            return False

        f = run_cli("leaderboard", LB_ARGS + [tmp], "public leaderboard, full download (rows >= "
                    f"{KEEP_MIN} and the histogram below)", check, need_stdout=False, before=clear, runner=runner,
                    sleep=sleep, attempts=attempts, shown_args=LB_ARGS + ["<tmpdir>"])
    for k in ("stdout", "stderr"):                          # the temp folder is gone; keep the file machine-neutral
        f[k] = f[k].replace(tmp, "<tmpdir>").replace(tmp.replace("\\", "/"), "<tmpdir>")
    f["lb_file"] = got.get("file")
    return f


class CacheRunner:
    """--dry-run-from stand-in for subprocess.run: replays <key>.out/.err/.rc from a folder; for the leaderboard
    download it copies leaderboard.zip (or .csv) into the -p folder of the call."""

    def __init__(self, cache):
        self.cache = Path(cache)
        self.keys = {tuple(a): k for k, _kind, a, _w in queries()}

    def _read(self, key, ext):
        p = self.cache / f"{key}.{ext}"
        return p.read_text(encoding="utf-8", errors="replace") if p.exists() else None

    def __call__(self, cmd, **_kw):
        args, present = list(cmd[3:]), False
        if args[:len(LB_ARGS)] == LB_ARGS:
            key = "leaderboard"
            for name in ("leaderboard.zip", "leaderboard.csv"):
                if (self.cache / name).exists():
                    shutil.copy(self.cache / name, Path(args[-1]) / name)
                    present = True
                    break
        else:
            key = self.keys.get(tuple(args), "unknown")
        out, err, rc = self._read(key, "out"), self._read(key, "err") or "", self._read(key, "rc")
        if rc is not None and rc.strip().lstrip("-").isdigit():
            code = int(rc.strip())
        else:
            code = 0 if (out is not None or present) else 1
        if out is None and not present:
            err = err or f"dry run: {key}.out not found in {self.cache}"
        return subprocess.CompletedProcess(cmd, code, out or "", err)


def collect(runner=subprocess.run, sleep=time.sleep, attempts=ATTEMPTS):
    """Run every query -> (list of fetch dicts in file order, leaderboard fetch dict)."""
    fetches = []
    for key, kind, args, what in queries():
        if kind == "kernels":
            check = lambda o: parse_kernel_csv(o) is not None  # noqa: E731
        else:
            check = lambda o: parse_status(o) is not None  # noqa: E731
        f = run_cli(key, args, what, check, runner=runner, sleep=sleep, attempts=attempts)
        f["kind"] = kind
        fetches.append(f)
    lb = fetch_leaderboard(runner, sleep, attempts)
    lb["kind"] = "leaderboard"
    return fetches, lb


# ---------------------------------------------------------------- snapshot text
def clean_stderr(s):
    """stderr lines without blank lines; a run of tqdm progress lines collapses to its last line."""
    out = []
    for ln in (s or "").replace("\r", "\n").split("\n"):
        ln = ln.rstrip()
        if not ln.strip():
            continue
        if out and TQDM_RE.match(ln) and TQDM_RE.match(out[-1]):
            out[-1] = ln
        else:
            out.append(ln)
    return out


def render_fetch(f, extra=""):
    """One raw section. Blank stdout lines are dropped: on Windows the CLI's CSV rows end in \\r\\r\\n, which text
    mode reads as a row plus an empty line (the same blank lines as in experiments/lb_poll/poll.log)."""
    L = [sec(f["key"]), f"what: {f['what']}", f"cmd: {f['cmd']}",
         f"fetch: {f['state']} attempts={f['attempts']} rc={f['rc']}{extra}"]
    if f["notes"]:
        L.append("retries: " + " | ".join(f["notes"]))
    L.append("--- stdout ---")
    L += [ln.rstrip() for ln in f["stdout"].splitlines() if ln.strip()]
    err = clean_stderr(f["stderr"])
    if err:
        L += ["--- stderr ---", *err]
    return L + [""]


def ours_line(s):
    o = s["ours"]
    if o is None:
        return f"our team: {OUR_TEAM} (TeamId {OUR_TEAM_ID}) NOT FOUND in the leaderboard CSV"
    blk = s["blocks"].get(o["score"])
    pos = (f"; position {o['rank'] - blk[0] + 1} of {blk[2]} in the {o['score']} block (ranks {blk[0]}-{blk[1]})"
           if blk else "")
    return (f"our team: {o['name']} (TeamId {o['id']}) rank {o['rank']} ({o['rank_src']}), score {o['score']}; "
            f"1 + teams with a strictly better 3-decimal score = {o['better'] + 1}{pos}; "
            f"last submission {o['last']}")


def render_histogram(lbf, s):
    L = [sec("histogram")]
    if s is None:
        return L + [f"leaderboard fetch {lbf['state']}: no histogram in this snapshot", ""]
    L.append(f"public LB {lbf['lb_file'][0]}: teams per 3-decimal public score >= {WATCH_MIN} "
             "(ranks = CSV Rank range of the block)")
    for sc in sorted(s["hist"], reverse=True):
        lo, hi, n = s["blocks"][sc]
        L.append(f"{sc}: {n} (ranks {lo}-{hi})")
    L += [f">= {x}: {s['ge'][x]}" for x in GE_LINES]
    L.append(f"total teams: {s['total']} (CSV rows {s['csv_rows']}; {s['unranked']} unranked host benchmark "
             "rows with Rank 0 left out)")
    below = [sc for sc in sorted(s["blocks"], reverse=True) if KEEP_MIN <= sc < WATCH_MIN]
    if below:
        L.append("info, below the watch line: " + " | ".join(
            f"{sc}: {s['blocks'][sc][2]} (ranks {s['blocks'][sc][0]}-{s['blocks'][sc][1]})" for sc in below))
    return L + [ours_line(s), ""]


def render_body(started, took_s, fetches, lbf, dry):
    parsed = parse_lb_csv(lbf["lb_file"][1]) if lbf.get("lb_file") else None
    s = lb_summary(*parsed) if parsed else None
    states = Counter(f["state"] for f in fetches + [lbf])
    L = [f"E10-P1 WATCH SNAPSHOT {started:%Y%m%dT%H%MZ} ({started:%Y-%m-%d %H:%M} UTC)",
         NOTE,
         "What: E10 PORT RULE P1 light check (CONTEXT.md, 26 Sep 09:03 UTC entry; in force since the user's 09:10 UTC "
         "conditional yes). P1 only gathers; a P2 search signal starts a look, never a port by itself.",
         "Read-only: Kaggle CLI `kernels list`, `kernels status`, `competitions leaderboard --download` (temp folder, "
         "deleted after parsing). Nothing is pulled, pushed or submitted.",
         "The kernel API has no score field: public scores come only from the leaderboard below and the notebook pages.",
         f"x138 = {X138} (live slug). The old slug anvithpothula/biohub-x138 returns 404 since the rename; a 404 there "
         "is NOT a signal, so it is not queried.",
         "Sections: 5 kernel lists (raw CLI CSV), 2 statuses (raw), leaderboard (CLI message), leaderboard_rows (CSV "
         f"rows with Score >= {KEEP_MIN}), histogram (parsed), then the DIFF vs the newest earlier snapshot.",
         f"mode: {'DRY RUN from ' + str(dry) if dry else 'LIVE'} | CLI calls took {took_s:.0f} s | fetch: "
         f"{states['OK']} OK, {states['NOTFOUND']} NOTFOUND, {states['FAILED']} FAILED", ""]
    for f in fetches:
        if f["kind"] == "kernels" and f["state"] == "OK":
            extra = f" rows={len(parse_kernel_csv(f['stdout']))}"
        elif f["kind"] == "status" and f["state"] == "OK":
            extra = f" status={parse_status(f['stdout'])}"
        else:
            extra = ""
        L += render_fetch(f, extra)
    L += render_fetch(lbf, f" file={lbf['lb_file'][0]} csv_rows={s['csv_rows']}" if s else "")
    if s is not None:
        text, k = kept_rows_csv(*parsed)
        L += [sec("leaderboard_rows"),
              f"CSV rows with Score >= {KEEP_MIN}: {k} of {s['csv_rows']} rows kept (the rest omitted); "
              f"total teams {s['total']}; file {lbf['lb_file'][0]}", *text.rstrip("\n").splitlines(), ""]
    L += render_histogram(lbf, s)
    return "\n".join(L) + "\n"


def split_sections(text):
    secs, cur = {}, None
    for ln in text.splitlines():
        m = SEC_RE.match(ln)
        if m:
            cur = m.group(1)
            secs[cur] = []
        elif cur is not None:
            secs[cur].append(ln)
    return secs


def read_fetch(lines):
    """Section body -> (fetch state, raw stdout text)."""
    state, out, mode = "MISSING", [], None
    for ln in lines:
        if ln == "--- stdout ---":
            mode = "out"
        elif ln == "--- stderr ---":
            mode = "err"
        elif mode == "out":
            out.append(ln)
        elif mode is None and ln.startswith("fetch: "):
            state = (ln.split() + ["MISSING"])[1]
    return state, "\n".join(out)


def load_state(text):
    """Snapshot text -> {'fetch': {key: state}, 'kernels': {key: rows|None}, 'status': {key: str|None},
    'lb': lb_summary|None}. The current check goes through this too (render, then load)."""
    secs = split_sections(text)
    st = {"fetch": {}, "kernels": {}, "status": {}, "lb": None}
    for key, kind, _args, _what in queries():
        state, out = read_fetch(secs[key]) if key in secs else ("MISSING", "")
        st["fetch"][key] = state
        if kind == "kernels":
            st["kernels"][key] = parse_kernel_csv(out) if state == "OK" else None
        else:
            st["status"][key] = (parse_status(out) if state == "OK"
                                 else "NOT FOUND (404)" if state == "NOTFOUND" else None)
    state, _ = read_fetch(secs["leaderboard"]) if "leaderboard" in secs else ("MISSING", "")
    st["fetch"]["leaderboard"] = state
    body = secs.get("leaderboard_rows")
    if state == "OK" and body:
        m = re.search(r"total teams (\d+)", body[0])
        parsed = parse_lb_csv("\n".join(body[1:]))
        if parsed:
            st["lb"] = lb_summary(*parsed, total=int(m.group(1)) if m else None)
    return st


# ---------------------------------------------------------------- diff
def _t(s):
    return s[:19]                                            # drop the microseconds of lastRunTime


def diff_kernels(a, b):
    """Two parsed kernel lists -> change lines (NEW, LASTRUN, TITLE, DROPPED)."""
    pa = {r["ref"]: (i + 1, r) for i, r in enumerate(a)}
    pb = {r["ref"]: (i + 1, r) for i, r in enumerate(b)}
    out = [f'NEW      {ref}  pos {j}  lastRunTime {_t(r["lastRunTime"])}  "{r["title"]}" by {r["author"]}'
           for ref, (j, r) in pb.items() if ref not in pa]
    for ref, (j, r) in pb.items():
        if ref in pa:
            i, o = pa[ref]
            if o["lastRunTime"] != r["lastRunTime"]:
                out.append(f"LASTRUN  {ref}  lastRunTime {_t(o['lastRunTime'])} -> {_t(r['lastRunTime'])}  "
                           f"pos {i} -> {j}")
            if o["title"] != r["title"]:
                out.append(f'TITLE    {ref}  "{o["title"]}" -> "{r["title"]}"')
    out += [f"DROPPED  {ref}  was pos {i}, lastRunTime {_t(o['lastRunTime'])}"
            for ref, (i, o) in pa.items() if ref not in pb]
    return out


def diff_lb(a, b):
    """Two lb_summary dicts -> change lines (histogram bins, >= lines, total, our rank / score)."""
    out = []
    for s in sorted(set(a["hist"]) | set(b["hist"]), reverse=True):
        x, y = a["hist"].get(s, 0), b["hist"].get(s, 0)
        if x != y:
            out.append(f"HIST     {s}: {x} -> {y} ({y - x:+d})")
    for thr in GE_LINES:
        x, y = a["ge"][thr], b["ge"][thr]
        if x != y:
            out.append(f"GE       >= {thr}: {x} -> {y} ({y - x:+d})")
    if a["total"] != b["total"]:
        out.append(f"TOTAL    teams {a['total']} -> {b['total']} ({b['total'] - a['total']:+d})")
    oa, ob = a["ours"], b["ours"]
    if (oa is None) != (ob is None):
        out.append(f"OURS     {OUR_TEAM} not found in the {'current' if ob is None else 'earlier'} leaderboard")
    elif oa is not None:
        if oa["rank"] != ob["rank"]:
            out.append(f"OURS     rank {oa['rank']} -> {ob['rank']} ({ob['rank'] - oa['rank']:+d})")
        if oa["score"] != ob["score"]:
            out.append(f"OURS     score {oa['score']} -> {ob['score']}")
    return out


def lb_movers(a, b):
    """-> (movers sorted by current rank as (team, earlier score or None), earlier teams gone, P2 groups)."""
    moved = []
    for tid, t in b["teams"].items():
        o = a["teams"].get(tid)
        if o is None or o["score"] != t["score"]:
            moved.append((t, None if o is None else o["score"]))
    moved.sort(key=lambda x: x[0]["rank"])
    gone = [tid for tid in a["teams"] if tid not in b["teams"]]
    groups = Counter(t["score"] for t, o in moved if t["score"] >= P2_MIN and (o is None or o <= P2_FROM_MAX))
    return moved, gone, groups


def lb_info(a, b):
    """Info lines (not counted as changes): teams with a new score and the P2 look-check."""
    moved, gone, groups = lb_movers(a, b)
    L = [f"  info: {len(moved)} team(s) with a new score >= {KEEP_MIN} since the earlier snapshot"
         + (f"; {len(gone)} earlier team(s) no longer in the rows >= {KEEP_MIN}" if gone else "")]
    for t, o in moved[:MAX_MOVERS]:
        was = o if o is not None else f"<{KEEP_MIN} or new"
        L.append(f"    #{t['rank']} {t['name'][:40]}: {was} -> {t['score']} (last submission {t['last']})")
    if len(moved) > MAX_MOVERS:
        L.append(f"    ... {len(moved) - MAX_MOVERS} more")
    big = max(groups.values(), default=0)
    L.append(f"  info: P2 look-check, teams now >= {P2_MIN} that were <= {P2_FROM_MAX} (or not in the earlier rows) "
             "per identical score: " + (", ".join(f"{s}: {k}" for s, k in sorted(groups.items(), reverse=True))
                                        or "none")
             + f"; largest group {big} (P2 search signal: >= {P2_GROUP} in one window; it starts a look, never a "
               "port; the ~23:30-02:00Z submit bursts are the daily pattern)")
    return L


def diff_states(prev, cur):
    """-> (DIFF lines, number of change lines). 'info' lines are not counted."""
    L, n = [], 0

    def section(head, items, sa, sb):
        nonlocal n
        if items is None:
            L.append(f"{head}: NOT COMPARED (fetch earlier {sa}, now {sb})")
        elif not items:
            L.append(f"{head}: no change")
        else:
            L.append(f"{head}: {len(items)} change(s)")
            L.extend("  " + x for x in items)
            n += len(items)

    for key, kind, _args, what in queries():
        if kind == "kernels":
            a, b = prev["kernels"].get(key), cur["kernels"].get(key)
            items = None if a is None or b is None else diff_kernels(a, b)
        else:
            a, b = prev["status"].get(key), cur["status"].get(key)
            items = None if a is None or b is None else ([f"STATUS   {a} -> {b}"] if a != b else [])
        section(f"[{key}] {what}", items, prev["fetch"].get(key, "MISSING"), cur["fetch"].get(key, "MISSING"))
    a, b = prev["lb"], cur["lb"]
    section(f"[leaderboard] teams per score >= {WATCH_MIN}, >= lines, total teams, our rank",
            None if a is None or b is None else diff_lb(a, b),
            prev["fetch"].get("leaderboard", "MISSING"), cur["fetch"].get("leaderboard", "MISSING"))
    if a is not None and b is not None:
        L += lb_info(a, b)
    return L, n


# ---------------------------------------------------------------- files
def snap_key(name):
    """Snapshot file name -> (stamp, n, dry) or None for other files."""
    m = NAME_RE.match(name)
    return None if m is None else (m["stamp"], int(m["n"] or 1), bool(m["dry"]))


def next_path(out_dir, now, dry):
    stamp, suffix, n = f"{now:%Y%m%dT%H%MZ}", "-dryrun" if dry else "", 1
    while True:
        p = out_dir / f"{stamp}{'' if n == 1 else f'-{n}'}{suffix}.txt"
        if not p.exists():
            return p, (stamp, n)
        n += 1


def find_previous(out_dir, cur_key, live):
    """Newest snapshot in out_dir with a (stamp, n) key before cur_key; a live check skips dry-run files."""
    best = None
    for p in Path(out_dir).glob("*.txt"):
        k = snap_key(p.name)
        if k is None or (live and k[2]) or k[:2] >= cur_key:
            continue
        if best is None or k[:2] > best[0]:
            best = (k[:2], p)
    return None if best is None else best[1]


def stamp_dt(stamp):
    return dt.datetime.strptime(stamp, "%Y%m%dT%H%MZ").replace(tzinfo=dt.timezone.utc)


def parse_now(s):
    s = s.strip()
    d = dt.datetime.fromisoformat(s[:-1] + "+00:00" if s.endswith("Z") else s)
    return (d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)).astimezone(dt.timezone.utc)


def display(p):
    p = Path(p).resolve()
    try:
        return p.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def take_snapshot(out_dir, started, runner=subprocess.run, sleep=time.sleep, attempts=ATTEMPTS, dry=None):
    """One snapshot: run the queries through `runner`, write <out_dir>/<stamp>[-n][-dryrun].txt with the DIFF against
    the newest earlier snapshot -> {path, state (load_state of the body), diff (lines), changes, fetches, lb, failed}.
    main() and experiments/lb_poll/e10_watch_loop.py (hourly E10 v3 watch, which passes a gated runner) use this."""
    t0 = time.monotonic()
    fetches, lbf = collect(runner=runner, sleep=sleep, attempts=attempts)
    body = render_body(started, time.monotonic() - t0, fetches, lbf, dry)
    cur = load_state(body)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path, key = next_path(out_dir, started, dry is not None)
    prev = find_previous(out_dir, key, live=dry is None)
    if prev is None:
        diff, n = [sec("DIFF: baseline (no earlier snapshot)")], 0
    else:
        lines, n = diff_states(load_state(prev.read_text(encoding="utf-8", errors="replace")), cur)
        pk = snap_key(prev.name)
        h = (started - stamp_dt(pk[0])).total_seconds() / 3600
        diff = [sec(f"DIFF vs {prev.name}"),
                f"window: {stamp_dt(pk[0]):%Y-%m-%d %H:%M}Z -> {started:%Y-%m-%d %H:%M}Z ({h:.1f} h)"
                + ("; the earlier snapshot is a DRY RUN" if pk[2] else "")] + lines
    diff.append(f"CHANGES: {n}. {NOTE}")
    path.write_text(body + "\n".join(diff) + "\n", encoding="utf-8", newline="\n")
    return {"path": path, "state": cur, "diff": diff, "changes": n, "fetches": fetches, "lb": lbf,
            "failed": [f["key"] for f in fetches + [lbf] if f["state"] == "FAILED"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="E10 PORT RULE P1 watch snapshot (read-only Kaggle CLI calls). " + NOTE)
    ap.add_argument("--out-dir", default=str(OUT_DIR), help="snapshot folder (default: experiments/e10_watch)")
    ap.add_argument("--dry-run-from", default=None, help="replay cached CLI outputs from this folder (module doc)")
    ap.add_argument("--now", default=None, help="UTC time for the file name (tests / replays), e.g. 2026-09-26T16:05Z")
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")               # titles and team names are not always cp1252
        except Exception:
            pass
    dry = Path(a.dry_run_from) if a.dry_run_from else None
    if dry is not None and not dry.is_dir():
        print(f"e10_snapshot: --dry-run-from {dry} is not a folder", file=sys.stderr)
        return 2
    started = parse_now(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    if dry is not None:
        snap = take_snapshot(a.out_dir, started, runner=CacheRunner(dry), sleep=lambda _s: None, attempts=1, dry=dry)
    else:
        snap = take_snapshot(a.out_dir, started)
    path, n, failed = snap["path"], snap["changes"], snap["failed"]
    print("\n".join(snap["diff"]))
    if failed:
        print("CLI FAILED after retries (see the snapshot): " + ", ".join(failed))
    print(f"E10-P1 SNAPSHOT {display(path)} CHANGES={n}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
