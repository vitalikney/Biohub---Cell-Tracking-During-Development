"""READ-ONLY ladder watcher (R13-A2; CONTEXT.md 27 Sep 01:31 UTC 'LADDER PRE-SCORE REGISTRATION' (1) L5v2 and
(2) ATTRIBUTION).

    python experiments/lb_poll/ladder_watch.py              # live, from the repo root, as a background process
    python experiments/lb_poll/ladder_watch.py --once       # one ListSubmissions read (+ the S0 baseline if none yet)
    python experiments/lb_poll/ladder_watch.py --dry-run    # synthetic scenario, fake clock, temp folder, no network

It runs only two read-only Kaggle CLI commands (anything else raises before a subprocess starts):
    competitions submissions biohub-cell-tracking-during-development -v                 (ListSubmissions, CSV)
    competitions leaderboard biohub-cell-tracking-during-development -d -p <out>/<YYYYMMDDTHHMMSSZ>/
It never submits, never pushes a kernel and never writes lb_poll.py or poll.log (poll.log is only read, to keep out of
the poller's way). poll.log stays the official L9 record; this watcher only adds evidence for the in-block reading.

Loop. ListSubmissions every FAST_S (120 s) while >= 2 of exp70e/exp70a/exp70d are PENDING and before SOFT_CAP (06:45Z),
else every SLOW_S (300 s), until all four watched refs are terminal (COMPLETE/ERROR) or HARD_CAP (09:40Z). Before every
call it waits while <out>/PAUSE exists (touch it before a planned submit, W6, or on an E10 trigger) and while the
clock is within +-60 s of lb_poll.py's next expected poll (last '=== <UTC>' header of poll.log + k x the median header
spacing, ~603 s). A 429 backs off 60 s at most twice, then pauses 10 min.

Events. When a watched (or any later, ref > BASE_MAX_REF) submission turns COMPLETE/ERROR, the watcher downloads the
public LB into a new folder <out>/<stamp>/ (the zip is kept, its CSV extracted with ':' -> '_') and reads our row
(TeamId 16810638). FRESHNESS: the download is valid iff our SubmissionCount == 40 + the refs COMPLETE in the
ListSubmissions read taken just before it (with an ERROR present, 40 + COMPLETE + ERROR is also accepted until
--error-counts pins the rule; the log says which matched). A stale download is repeated every 2 min (each time after a
fresh ListSubmissions read, whose new status changes join the event) up to 3 times; then the event is AMBIGUOUS.
UP TEST: some TeamId ranked above us in S0 ranks below us in S1. ATTRIBUTION: with exactly one ref COMPLETE between
the two fresh downloads the UP is that ref's; with >= 2 (co-completion) the higher display takes it, equal top displays
make it non-attributable (all NEU). Each fresh S1 becomes the next S0; the first S0 is a baseline download at start
(skipped when a state file or an earlier fresh download already provides one).

Per ref: verdict UP / NEU / NEG / AMBIGUOUS (ERROR for an errored ref), unit status per L5v2: POS = display >= 0.955,
or 0.954 with an attributable UP; NEG = display <= 0.953; NEU = anything else. Output: one line per event appended to
<out>/watch.log and printed (flushed); one JSON line per CLI call in <out>/calls.jsonl; state in <out>/state.json
(a restart resumes from it). Exit code 0 at the normal end (all four terminal, or the hard cap).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
import zipfile
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UTC = dt.timezone.utc
COMP = "biohub-cell-tracking-during-development"
OUR_TEAM_ID, OUR_TEAM = "16810638", "D: Discipline"      # the team name is only the fallback
BASE_COUNT = 40                                         # scored submissions before the ladder (LB 22:46Z)
BASE_MAX_REF = 56563534                                 # probe 38, the last scored submission before the ladder
BASE_LAST = "2026-09-26 00:02:18"                       # its submit time = our LastSubmissionDate before the ladder
WATCHED = {"56589025": "exp70e", "56589065": "exp70a", "56589423": "exp70d", "56592350": "exp70b"}
FAST_REFS = ("56589025", "56589065", "56589423")
TERMINAL = ("COMPLETE", "ERROR")
FAST_S, SLOW_S, RETRY_S, MAX_REDOWNLOADS = 120, 300, 120, 3
SOFT_CAP = dt.datetime(2026, 9, 27, 6, 45, tzinfo=UTC)
HARD_CAP = dt.datetime(2026, 9, 27, 9, 40, tzinfo=UTC)
POLLER_GUARD_S, POLLER_PERIOD_S, POLLER_STALE_S = 60, 603, 1800
BACKOFF_429_S, MAX_429_BACKOFFS, PAUSE_429_S = 60, 2, 600
CLI_TIMEOUT_S = 180
POS_MIN, NEG_MAX = Decimal("0.955"), Decimal("0.953")
OUT_DIR = ROOT / "experiments" / "lb_poll" / "ladder_watch"
POLL_LOG = ROOT / "experiments" / "lb_poll" / "poll.log"
SUB_ARGS = ["competitions", "submissions", COMP, "-v"]
LB_ARGS = ["competitions", "leaderboard", COMP, "-d", "-p"]
HDR_RE = re.compile(r"^=== (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z", re.M)
RE_429 = re.compile(r"\b429\b|Too Many Requests", re.I)


def stamp(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def folder_stamp(t):
    return t.strftime("%Y%m%dT%H%M%SZ")


def parse_utc(s):
    """'2026-09-27T04:10Z' / '2026-09-27T04:10:00Z' / '... 04:10:00' -> aware UTC datetime."""
    s = s.strip().replace(" ", "T").rstrip("Z")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return dt.datetime.strptime(s, fmt).replace(tzinfo=UTC)
        except ValueError:
            pass
    raise ValueError(f"bad UTC time {s!r}")


# ---------------------------------------------------------------- parsers (pure)
def norm_status(s):
    """'SubmissionStatus.COMPLETE' -> 'COMPLETE'."""
    s = (s or "").strip()
    return (s.rsplit(".", 1)[1] if "." in s else s).upper()


def q3(s):
    """Score text -> Decimal rounded to 3 decimals (half up); None when blank / not a number."""
    try:
        d = Decimal(str(s).strip())
    except (InvalidOperation, ValueError):
        return None
    return d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP) if d.is_finite() else None


def fmt_d(d):
    return "-" if d is None else str(d)


def parse_submissions(text):
    """`competitions submissions -v` stdout -> {ref: {ref, date, description, status, public}}; {} for 'No submissions
    found'; None when there is no CSV header (error text, HTML, warnings only). Blank lines (the CLI's \\r\\r\\n on
    Windows) and preamble lines ('Using competition: ...', warnings) are ignored; date is cut to whole seconds."""
    lines = (text or "").lstrip("﻿").splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().startswith("ref,"):
            out = {}
            for r in csv.DictReader(io.StringIO("\n".join(lines[i:]))):
                ref = (r.get("ref") or "").strip()
                if not ref.isdigit():
                    continue
                out[ref] = {"ref": ref, "date": (r.get("date") or "").strip()[:19],
                            "description": (r.get("description") or "").strip(),
                            "status": norm_status(r.get("status")), "public": q3(r.get("publicScore"))}
            return out
    return {} if re.search(r"no submissions found", text or "", re.I) else None


def parse_lb(text):
    """Leaderboard CSV text (BOM ok; columns Rank, TeamId, TeamName, LastSubmissionDate, Score, SubmissionCount,
    TeamMemberUserNames) -> {teams, ranks {TeamId: Rank}, ours, above [TeamIds ranked above us]} or None when a needed
    column is missing. Rank-0 rows (host benchmarks) are not teams and are skipped. ours = {rank, id, name, last,
    score, count} (None when our team is absent)."""
    rdr = csv.DictReader(io.StringIO((text or "").lstrip("﻿"), newline=""))
    col = {f.strip().lower(): f for f in (rdr.fieldnames or [])}
    if any(k not in col for k in ("rank", "teamid", "score", "submissioncount")):
        return None
    teams = []
    for r in rdr:
        def g(k):
            return (r.get(col[k]) or "").strip() if k in col else ""
        rk = g("rank")
        if not rk.isdigit() or int(rk) == 0:
            continue
        cnt = g("submissioncount")
        teams.append({"rank": int(rk), "id": g("teamid"), "name": g("teamname"), "last": g("lastsubmissiondate")[:19],
                      "score": g("score"), "count": int(cnt) if cnt.isdigit() else None})
    ours = next((t for t in teams if t["id"] == OUR_TEAM_ID), None) or next(
        (t for t in teams if t["name"] == OUR_TEAM), None)
    return {"teams": len(teams), "ranks": {t["id"]: t["rank"] for t in teams}, "ours": ours,
            "above": [t["id"] for t in teams if ours is not None and t["rank"] < ours["rank"]]}


def extract_lb(folder):
    """-> path of the leaderboard CSV in folder (extracted from the zip on first use; the member name holds ':' which
    Windows forbids, so ':' and other reserved characters become '_') or None."""
    folder = Path(folder)
    csvs = sorted(folder.glob("*.csv"))
    if csvs:
        return csvs[0]
    for z in sorted(folder.glob("*.zip")):
        with zipfile.ZipFile(z) as zf:
            for n in zf.namelist():
                if n.lower().endswith(".csv"):
                    dst = folder / re.sub(r'[<>:"|?*]', "_", n.replace("\\", "/").rsplit("/", 1)[-1])
                    dst.write_bytes(zf.read(n))
                    return dst
    return None


def read_lb_source(path):
    """Leaderboard CSV text from a download folder, a .zip, a .csv or an e10_watch snapshot .txt (its
    'leaderboard_rows' section); None when nothing is found."""
    path = Path(path)
    if path.is_dir():
        p = extract_lb(path)
        return p.read_bytes().decode("utf-8-sig", errors="replace") if p else None
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            return zf.read(names[0]).decode("utf-8-sig", errors="replace") if names else None
    text = path.read_bytes().decode("utf-8-sig", errors="replace")
    if path.suffix.lower() == ".txt":
        lines, out = text.splitlines(), None
        for ln in lines:
            if out is not None and ln.startswith("======== "):
                break
            if out is not None:
                out.append(ln)
            elif ln.strip() == "======== leaderboard_rows ========":
                out = []
        head = next((i for i, ln in enumerate(out or []) if ln.startswith("Rank,")), None)  # skip the 'kept' note
        return "\n".join(out[head:]) + "\n" if head is not None else None
    return text


def load_lb(folder):
    p = extract_lb(folder)
    return parse_lb(p.read_bytes().decode("utf-8-sig", errors="replace")) if p else None


def tracked(subs):
    """Refs that count toward our SubmissionCount after the baseline: the watched four and any later submission."""
    return [r for r in subs if r in WATCHED or int(r) > BASE_MAX_REF]


def statuses(subs):
    return {r: subs[r]["status"] for r in tracked(subs)}


def changed_refs(before, subs):
    """Tracked refs terminal in subs but not in the status map `before` (a ref missing from `before` counts as new)."""
    before = before or {}
    return [r for r in tracked(subs) if subs[r]["status"] in TERMINAL and before.get(r) not in TERMINAL]


def freshness(count, subs, error_mode=None):
    """FRESHNESS key of CONTEXT (2): our SubmissionCount vs 40 + tracked refs COMPLETE (+ ERROR when errors count).
    error_mode: None (unknown: both accepted when an ERROR exists), 'yes' or 'no'. -> dict fresh, C, E, expected,
    err_counted ('n.a.' without an ERROR, else 'yes' / 'no' / '?')."""
    new = tracked(subs)
    c = sum(subs[r]["status"] == "COMPLETE" for r in new)
    e = sum(subs[r]["status"] == "ERROR" for r in new)
    if e == 0:
        exp, err = [BASE_COUNT + c], "n.a."
    elif error_mode == "yes":
        exp, err = [BASE_COUNT + c + e], "yes"
    elif error_mode == "no":
        exp, err = [BASE_COUNT + c], "no"
    else:
        exp = [BASE_COUNT + c, BASE_COUNT + c + e]
        err = "yes" if count == exp[1] else "no" if count == exp[0] else "?"
    return {"fresh": count is not None and count in exp, "C": c, "E": e, "expected": exp, "err_counted": err,
            "count": count}


def expected_last(subs, error_mode=None):
    """Secondary check: LastSubmissionDate should be the latest submit time among the scored submissions."""
    kinds = ("COMPLETE", "ERROR") if error_mode == "yes" else ("COMPLETE",)
    return max([BASE_LAST] + [subs[r]["date"] for r in tracked(subs) if subs[r]["status"] in kinds])


def up_test(lb0, lb1):
    """TeamIds ranked above us in S0 that rank below us in S1 (public bests never decrease, so any such team proves
    our best rose). None when either side lacks our row."""
    if not lb0 or not lb1 or not lb0.get("ours") or not lb1.get("ours"):
        return None
    r1 = lb1["ours"]["rank"]
    return [t for t in lb0["above"] if lb1["ranks"].get(t, 0) > r1]


def attribute(complete, subs, up):
    """complete: refs that turned COMPLETE between the two fresh downloads. -> (ref taking the UP or None, text)."""
    if not up:
        return None, "no UP"
    if not complete:
        return None, "UP without a COMPLETE ref (anomaly)"
    if len(complete) == 1:
        return complete[0], "single completion (count +1 per COMPLETE): the UP is attributable"
    disp = {r: subs[r]["public"] if subs[r]["public"] is not None else Decimal(-1) for r in complete}
    top = max(disp.values())
    tops = [r for r in complete if disp[r] == top]
    if len(tops) == 1:
        return tops[0], f"co-completion of {len(complete)}: the higher display {tops[0]} takes the UP"
    return None, f"co-completion of {len(complete)}: equal top displays {fmt_d(top)}, UP non-attributable (NEU)"


def unit_status(display, attributable_up):
    """L5v2 unit status: POS = display >= 0.955, or 0.954 with an attributable UP; NEG = display <= 0.953; NEU else."""
    if display is None:
        return "NEU"
    if display >= POS_MIN:
        return "POS"
    if display <= NEG_MAX:
        return "NEG"
    return "POS" if attributable_up else "NEU"


def ref_verdict(ref, subs, evaluable, attributed):
    """-> (verdict, unit). ERROR needs no S1; a display <= 0.953 is NEG without the LB; otherwise the LB decides."""
    st, d = subs[ref]["status"], subs[ref]["public"]
    if st == "ERROR":
        return "ERROR", "NEU"
    if d is not None and d <= NEG_MAX:
        return "NEG", "NEG"
    if not evaluable:
        return "AMBIGUOUS", unit_status(d, False)
    if ref == attributed:
        return "UP", unit_status(d, True)
    return "NEU", unit_status(d, False)


# ---------------------------------------------------------------- poller phase (poll.log is only read)
def read_poll_headers(path, tail_bytes=65536):
    """UTC datetimes of the '=== <UTC>' headers in the tail of poll.log (a header is written after its poll ran)."""
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - tail_bytes))
            text = f.read().decode("utf-8", errors="replace")
    except OSError:
        return []
    return [dt.datetime.strptime(m, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=UTC) for m in HDR_RE.findall(text)]


def poller_period(headers):
    """Median spacing of the last headers (600 s sleep + the poll + the ledger run); POLLER_PERIOD_S by default."""
    d = [(b - a).total_seconds() for a, b in zip(headers[-9:], headers[-8:])]
    d = [x for x in d if 590 <= x <= 900]
    return statistics.median(d) if d else float(POLLER_PERIOD_S)


def poller_wait_s(now, headers, guard=POLLER_GUARD_S):
    """-> (seconds to wait, reason). 0 when now is not within +-guard s of lb_poll's last or next expected poll."""
    headers = [h for h in headers if h <= now]
    if not headers:
        return 0.0, "poll.log has no header (poller phase unknown, no skip)"
    last, period = headers[-1], poller_period(headers)
    age = (now - last).total_seconds()
    if age > POLLER_STALE_S:
        return 0.0, f"last poll.log header {age:.0f} s old (poller phase unknown, no skip)"
    k0 = int(age // period)
    for k in (k0, k0 + 1):
        e = last + dt.timedelta(seconds=k * period)
        d = (now - e).total_seconds()
        if -guard < d < guard:
            return guard - d + 1, f"within {abs(d):.0f} s of lb_poll's {'last' if k == 0 else 'expected'} poll " \
                                  f"{e:%H:%M:%S}Z (period {period:.0f} s)"
    return 0.0, ""


# ---------------------------------------------------------------- CLI and clock
class Clock:
    def now(self):
        return dt.datetime.now(UTC)

    def sleep(self, s):
        if s > 0:
            time.sleep(s)


def assert_read_only(args):
    """Only ListSubmissions and the LB download may ever run."""
    ok = (args[:3] == SUB_ARGS[:3] and args[3:] == SUB_ARGS[3:]) or (
        args[:5] == LB_ARGS and len(args) == 6)
    if not ok:
        raise RuntimeError(f"ladder_watch refuses a non-read-only Kaggle command: {args}")


class KaggleCLI:
    def __init__(self, root=ROOT):
        self.root = Path(root)

    def run(self, args):
        assert_read_only(args)
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        try:
            p = subprocess.run([sys.executable, "-m", "kaggle", *args], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=CLI_TIMEOUT_S, env=env, cwd=str(self.root))
            return p.returncode, p.stdout or "", p.stderr or ""
        except subprocess.TimeoutExpired:
            return None, "", f"timed out after {CLI_TIMEOUT_S} s"
        except Exception as exc:  # CLI missing, OS error
            return None, "", f"{type(exc).__name__}: {exc}"


def one_line(s, n=200):
    return " ".join((s or "").split())[:n]


# ---------------------------------------------------------------- the watcher
def new_state():
    return {"version": 1, "last_statuses": None, "s0": None, "error_mode": None, "events": 0, "verdicts": {},
            "ambiguous": [], "history": []}


class Watcher:
    def __init__(self, out_dir=OUT_DIR, poll_log=POLL_LOG, cli=None, clock=None, soft_cap=SOFT_CAP,
                 hard_cap=HARD_CAP, error_mode=None, echo=None, rel_root=ROOT):
        self.out_dir, self.poll_log = Path(out_dir), Path(poll_log)
        self.cli, self.clock = cli or KaggleCLI(), clock or Clock()
        self.soft_cap, self.hard_cap = soft_cap, hard_cap
        self.pinned_error_mode = error_mode
        self.echo = echo or (lambda s: print(s, flush=True))
        self.rel_root = Path(rel_root)
        self.state_path = self.out_dir / "state.json"
        self.log_path, self.calls_path = self.out_dir / "watch.log", self.out_dir / "calls.jsonl"
        self.pause_path = self.out_dir / "PAUSE"
        self.state, self.calls, self._folder = new_state(), 0, None

    # ---- output and state
    def now(self):
        return self.clock.now()

    def say(self, msg, log=False):
        line = f"{stamp(self.now())} {msg}"
        self.echo(line)
        if log:
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

    def record_call(self, rec):
        with self.calls_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str) + "\n")

    def save_state(self):
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=1, default=str), encoding="utf-8")
        os.replace(tmp, self.state_path)

    def error_mode(self):
        return self.pinned_error_mode or self.state.get("error_mode")

    def load_state(self):
        """state.json if present; else recover S0 from the newest fresh download folder; else a new state."""
        if self.state_path.exists():
            self.state = dict(new_state(), **json.loads(self.state_path.read_text(encoding="utf-8")))
            return "resumed from state.json"
        metas = sorted(p for p in self.out_dir.glob("*/meta.json"))
        for m in reversed(metas):
            meta = json.loads(m.read_text(encoding="utf-8"))
            if meta.get("fresh") and meta.get("ours"):
                self.state["s0"] = {"folder": m.parent.name, "statuses": meta["statuses"], "ours": meta["ours"]}
                self.state["last_statuses"] = dict(meta["statuses"])
                return f"no state.json; S0 recovered from the fresh download {m.parent.name}"
        return "new state" + (" (earlier downloads exist, none fresh)" if metas else "")

    # ---- call gate: PAUSE file, poller phase, hard cap
    def gate(self):
        noted = set()
        while True:
            now = self.now()
            left = (self.hard_cap - now).total_seconds()
            if left <= 0:
                return False
            if self.pause_path.exists():
                if "pause" not in noted:
                    self.say(f"PAUSE file {self.pause_path.name} present: no Kaggle call until it is removed")
                    noted.add("pause")
                self.clock.sleep(min(60, left))
                continue
            wait, why = poller_wait_s(now, read_poll_headers(self.poll_log))
            if wait > 0:
                self.say(f"skip: {why}; next call in {wait:.0f} s")
                self.clock.sleep(min(wait, left))
                continue
            return True

    def call(self, endpoint, make_args):
        """One read-only CLI call through the gate, with the 429 rule. -> (rc, stdout, stderr, t0) or None."""
        n429 = 0
        while True:
            if not self.gate():
                return None
            t0 = self.now()
            args = make_args(t0)
            rc, out, err = self.cli.run(args)
            self.calls += 1
            if RE_429.search(f"{out}\n{err}"):
                n429 += 1
                self.record_call({"utc": stamp(t0), "endpoint": endpoint, "rc": rc, "note": "429"})
                if n429 <= MAX_429_BACKOFFS:
                    self.say(f"429 on {endpoint}: backing off {BACKOFF_429_S} s ({n429}/{MAX_429_BACKOFFS})")
                    self.clock.sleep(BACKOFF_429_S)
                    continue
                self.say(f"429 on {endpoint} after {MAX_429_BACKOFFS} back-offs: pausing {PAUSE_429_S // 60} min",
                         log=True)
                self.clock.sleep(PAUSE_429_S)
                return None
            return rc, out, err, t0

    def read_submissions(self):
        res = self.call("ListSubmissions", lambda t: list(SUB_ARGS))
        if res is None:
            return None
        rc, out, err, t0 = res
        subs = parse_submissions(out)
        rec = {"utc": stamp(t0), "endpoint": "ListSubmissions", "rc": rc}
        if subs is None:
            rec["note"] = f"no CSV: stdout={one_line(out)!r} stderr={one_line(err)!r}"
            self.record_call(rec)
            self.say(f"ListSubmissions failed (rc={rc}): {one_line(err or out)}")
            return None
        rec["statuses"] = {r: [subs[r]["status"], fmt_d(subs[r]["public"])] for r in tracked(subs)}
        self.record_call(rec)
        return {"utc": stamp(t0), "subs": subs}

    def new_folder(self, t):
        name, k = folder_stamp(t), 1
        while (self.out_dir / name).exists():
            k += 1
            name = f"{folder_stamp(t)}-{k}"
        self._folder = self.out_dir / name
        try:
            rel = self._folder.relative_to(self.rel_root)
        except ValueError:
            rel = self._folder
        return rel.as_posix() + "/"

    def download(self, read):
        """One LB download into a new folder + freshness against the ListSubmissions read `read`. -> dict or None."""
        res = self.call("DownloadLeaderboard", lambda t: LB_ARGS + [self.new_folder(t)])
        if res is None:
            return None
        rc, out, err, t0 = res
        folder = self._folder
        folder.mkdir(parents=True, exist_ok=True)
        lb, note = None, ""
        try:
            lb = load_lb(folder)
        except (zipfile.BadZipFile, OSError) as exc:
            note = f"{type(exc).__name__}: {exc}"
        if lb is None and not note:
            note = f"no leaderboard CSV (rc={rc}, stderr={one_line(err)!r})"
        ours = lb["ours"] if lb else None
        subs = read["subs"]
        fr = freshness(ours["count"] if ours else None, subs, self.error_mode())
        last_exp = expected_last(subs, self.error_mode())
        last_ok = None if ours is None else ours["last"] == last_exp
        meta = {"utc": stamp(t0), "rc": rc, "stdout": one_line(out, 400), "stderr": one_line(err, 400), "note": note,
                "teams": lb["teams"] if lb else None, "ours": ours, "fresh": fr["fresh"], "freshness": fr,
                "read_utc": read["utc"], "statuses": statuses(subs), "last_expected": last_exp, "last_ok": last_ok}
        (folder / "meta.json").write_text(json.dumps(meta, indent=1, default=str), encoding="utf-8")
        self.record_call({"utc": stamp(t0), "endpoint": "DownloadLeaderboard", "rc": rc, "folder": folder.name,
                          "our_row": ours, "fresh": fr["fresh"], "expected": fr["expected"], "note": note})
        if fr["err_counted"] == "yes" and self.error_mode() is None and fr["fresh"]:
            self.state["error_mode"] = "yes"
            self.say("learned: an ERROR increments SubmissionCount (count == 40 + COMPLETE + ERROR)", log=True)
        o = (f"rank {ours['rank']} score {ours['score']} count {ours['count']} last {ours['last']}" if ours
             else f"our row missing ({note or 'team not found'})")
        self.say(f"LB download {folder.name}: {o}; {'fresh' if fr['fresh'] else 'STALE'} (expected count "
                 f"{'/'.join(map(str, fr['expected']))}, ERROR counted: {fr['err_counted']})")
        return {"folder": folder.name, "lb": lb, "ours": ours, "fresh": fr["fresh"], "fr": fr, "last_ok": last_ok,
                "last_exp": last_exp}

    def set_s0(self, dl, read):
        self.state["s0"] = {"folder": dl["folder"], "statuses": statuses(read["subs"]), "ours": dl["ours"]}

    # ---- baseline S0
    def take_baseline(self, read):
        self.say("S0 baseline: no fresh ladder_watch S0 yet, downloading the LB")
        for attempt in range(1 + MAX_REDOWNLOADS):
            if attempt:
                self.clock.sleep(RETRY_S)
                r2 = self.read_submissions()
                if r2 is None:
                    continue
                if changed_refs(self.state["last_statuses"], r2["subs"]):
                    self.say("status change during the S0 baseline: S0 left unset (this event is AMBIGUOUS)",
                             log=True)
                    return r2
                read = r2
            dl = self.download(read)
            if dl and dl["fresh"]:
                self.set_s0(dl, read)
                o = dl["ours"]
                self.say(f"S0 {dl['folder']}: rank {o['rank']} score {o['score']} count {o['count']} last "
                         f"{o['last']} ({len(dl['lb']['above'])} TeamIds above us)", log=True)
                return read
            if self.now() >= self.hard_cap:
                break
        self.say(f"S0 baseline NOT fresh after {1 + MAX_REDOWNLOADS} downloads: S0 unset (next event AMBIGUOUS)",
                 log=True)
        return read

    # ---- events
    def resolve_event(self, read, changed):
        event_refs, subs = list(changed), read["subs"]
        error_only = all(subs[r]["status"] == "ERROR" for r in event_refs)
        self.say("status change: " + ", ".join(f"{r} {WATCHED.get(r, 'new')} {subs[r]['status']} "
                                               f"{fmt_d(subs[r]['public'])}" for r in event_refs))
        tries, dl = 0, None
        while True:
            tries += 1
            dl = self.download(read)
            if (dl and dl["fresh"]) or tries >= (1 if error_only else 1 + MAX_REDOWNLOADS):
                break
            if self.now() >= self.hard_cap:
                break
            self.say(f"S1 not fresh: re-download {tries}/{MAX_REDOWNLOADS} in {RETRY_S} s")
            self.clock.sleep(RETRY_S)
            r2 = self.read_submissions()
            if r2 is not None:
                more = changed_refs(statuses(subs), r2["subs"])
                if more:
                    event_refs += more
                    self.say("joins the event: " + ", ".join(f"{r} {WATCHED.get(r, 'new')} "
                                                             f"{r2['subs'][r]['status']}" for r in more))
                    error_only = error_only and all(r2["subs"][r]["status"] == "ERROR" for r in more)
                read, subs = r2, r2["subs"]
        self.state["last_statuses"] = statuses(subs)
        ev = self.evaluate(event_refs, read, dl, tries)
        self.state["events"] = ev["n"]
        self.state["history"].append(ev)
        self.say(format_event(ev), log=True)
        return ev

    def evaluate(self, event_refs, read, dl, tries):
        subs, s0 = read["subs"], self.state["s0"]
        fresh = bool(dl and dl["fresh"])
        lb0 = load_lb(self.out_dir / s0["folder"]) if (fresh and s0) else None
        passed = up_test(lb0, dl["lb"]) if lb0 is not None else None
        carried, attributed, delta = [], None, None
        if passed is not None:
            changed_all = [r for r in tracked(subs) if subs[r]["status"] in TERMINAL
                           and s0["statuses"].get(r) not in TERMINAL]
            complete = [r for r in changed_all if subs[r]["status"] == "COMPLETE"]
            errors = [r for r in changed_all if subs[r]["status"] == "ERROR"]
            attributed, mode = attribute(complete, subs, bool(passed))
            delta = dl["ours"]["count"] - s0["ours"]["count"]
            evaluable = not mode.endswith("(anomaly)")
            if delta not in (len(complete), len(complete) + len(errors)):
                mode += f"; count delta {delta:+d} != {len(complete)} COMPLETE (anomaly)"
                evaluable = False
            carried = [r for r in changed_all if r not in event_refs and r in self.state["ambiguous"]]
            if attributed in carried:
                mode += f"; the UP goes to {attributed}, which stays AMBIGUOUS"
        else:
            evaluable = False
            mode = ("download failed" if dl is None else "S1 stale after "
                    f"{tries} download(s)" if not fresh else "no fresh S0")
        refs = []
        for r in event_refs + carried:
            if r in carried:
                verdict, unit = self.state["verdicts"][r]["verdict"], self.state["verdicts"][r]["unit"]
            else:
                verdict, unit = ref_verdict(r, subs, evaluable, attributed)
                self.state["verdicts"][r] = {"verdict": verdict, "unit": unit, "event": self.state["events"] + 1}
                if verdict == "AMBIGUOUS":
                    self.state["ambiguous"].append(r)
            refs.append({"ref": r, "name": WATCHED.get(r, "new"), "status": subs[r]["status"],
                         "display": fmt_d(subs[r]["public"]), "verdict": verdict, "unit": unit,
                         "carried": r in carried})
        ev = {"n": self.state["events"] + 1, "utc": stamp(self.now()), "refs": refs,
              "s0": s0["folder"] if s0 else None, "s1": dl["folder"] if dl else None, "fresh": fresh,
              "tries": tries, "fr": dl["fr"] if dl else None, "last_ok": dl["last_ok"] if dl else None,
              "ours0": s0["ours"] if s0 else None, "ours1": dl["ours"] if dl else None,
              "passed": None if passed is None else len(passed), "passed_ids": passed or [],
              "up": "n/a" if passed is None else ("PASS" if passed else "FAIL"), "attribution": mode,
              "delta": delta}
        if fresh:
            self.set_s0(dl, read)
        return ev

    # ---- main loop
    def done(self):
        st = self.state["last_statuses"] or {}
        return all(st.get(r) in TERMINAL for r in WATCHED)

    def interval(self):
        st = self.state["last_statuses"] or {}
        pending = sum(st.get(r) not in TERMINAL for r in FAST_REFS)
        return FAST_S if (pending >= 2 and self.now() < self.soft_cap) else SLOW_S

    def stop(self, why):
        self.save_state()
        self.say(f"STOP ({why}); {self.calls} Kaggle calls this run; events {self.state['events']}; verdicts "
                 + (", ".join(f"{r} {WATCHED.get(r, 'new')} {v['verdict']}/{v['unit']}"
                              for r, v in self.state["verdicts"].items()) or "none"), log=True)
        return 0

    def import_s0(self, path):
        """--s0: a leaderboard CSV / zip / download folder, or an e10_watch snapshot .txt (its leaderboard_rows
        section keeps every row >= 0.953, so our row and all teams above us), taken before any ladder score. It is
        fresh iff our SubmissionCount == 40; it is copied to <out>/S0-<name>/ with a meta.json (all refs PENDING)."""
        path = Path(path)
        text = read_lb_source(path)
        lb = parse_lb(text) if text else None
        ours = lb["ours"] if lb else None
        if ours is None or ours["count"] != BASE_COUNT:
            self.say(f"--s0 {path.name} NOT used: " + ("no leaderboard with our row" if ours is None else
                                                        f"our SubmissionCount {ours['count']} != {BASE_COUNT}"),
                     log=True)
            return False
        folder = self.out_dir / ("S0-" + re.sub(r"[^A-Za-z0-9_.-]", "_", path.stem))
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "leaderboard.csv").write_text(text, encoding="utf-8")
        sts = {r: "PENDING" for r in WATCHED}
        meta = {"utc": stamp(self.now()), "source": str(path), "teams": lb["teams"], "ours": ours, "fresh": True,
                "statuses": sts, "note": "imported with --s0"}
        (folder / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        self.state["s0"] = {"folder": folder.name, "statuses": sts, "ours": ours}
        if self.state["last_statuses"] is None:
            self.state["last_statuses"] = dict(sts)
        self.say(f"S0 {folder.name} (from --s0 {path}): rank {ours['rank']} score {ours['score']} count "
                 f"{ours['count']} last {ours['last']} ({len(lb['above'])} TeamIds above us)", log=True)
        return True

    def run(self, once=False, s0_path=None):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        how = self.load_state()
        self.say(f"START ladder watch (read-only; {how}); refs " + ", ".join(f"{r} {n}" for r, n in WATCHED.items())
                 + f"; baseline count {BASE_COUNT}; {FAST_S}/{SLOW_S} s; soft cap {stamp(self.soft_cap)}, hard cap "
                 f"{stamp(self.hard_cap)}; ERROR counted: {self.error_mode() or 'unknown'}", log=True)
        if s0_path:
            if self.state["s0"] is None:
                self.import_s0(s0_path)
            else:
                self.say(f"--s0 ignored: S0 {self.state['s0']['folder']} already set ({how})")
        first = True
        while True:
            if self.now() >= self.hard_cap:
                return self.stop("hard cap reached")
            read = self.read_submissions()
            if read is not None:
                subs = read["subs"]
                if first:
                    first = False
                    if self.state["last_statuses"] is None:     # the ladder refs were PENDING at registration
                        self.state["last_statuses"] = dict(statuses(subs), **{r: "PENDING" for r in WATCHED})
                        pre = changed_refs(self.state["last_statuses"], subs)
                        if pre:
                            self.say("terminal before the first read: " + ", ".join(pre) + " (they form the first "
                                     "event; " + ("S0 from --s0)" if self.state["s0"] else "no S0 -> AMBIGUOUS)"),
                                     log=True)
                    if self.state["s0"] is None and not changed_refs(self.state["last_statuses"], subs):
                        read = self.take_baseline(read)
                        subs = read["subs"]
                changed = changed_refs(self.state["last_statuses"], subs)
                if changed:
                    self.resolve_event(read, changed)
                else:
                    self.state["last_statuses"] = statuses(subs)
                    self.say("ListSubmissions: " + ", ".join(f"{WATCHED[r]} {subs[r]['status'] if r in subs else '?'}"
                                                             for r in WATCHED))
                self.save_state()
                if self.done():
                    return self.stop("all four watched refs terminal")
            if once:
                return self.stop("--once")
            left = (self.hard_cap - self.now()).total_seconds()
            self.clock.sleep(max(0.0, min(self.interval(), left)))


def format_event(ev):
    def ours(o):
        return o or {"rank": "?", "score": "?", "count": "?", "last": "?"}
    o0, o1 = ours(ev["ours0"]), ours(ev["ours1"])
    fr = ev["fr"]
    fr_txt = "no download" if fr is None else (
        f"{'fresh' if ev['fresh'] else 'STALE'} after {ev['tries']} download(s); count {fr['count']} vs expected "
        f"{'/'.join(map(str, fr['expected']))} (40 + {fr['C']} COMPLETE" + (f" + {fr['E']} ERROR" if fr["E"] else "")
        + f"); ERROR counted: {fr['err_counted']}; LastSubmissionDate "
        + ("ok" if ev["last_ok"] else "n/a" if ev["last_ok"] is None else "MISMATCH"))
    changed = ", ".join(f"{r['ref']} {r['name']} {r['status']} {r['display']}" + (" (carried)" if r["carried"] else "")
                        for r in ev["refs"])
    verdicts = "; ".join(f"{r['ref']} {r['name']}: {r['verdict']} unit {r['unit']}" for r in ev["refs"])
    passed = "n/a" if ev["passed"] is None else str(ev["passed"])
    delta = "" if ev["delta"] is None else f" ({ev['delta']:+d})"
    return (f"EVENT {ev['n']} | changed: {changed} | S0 {ev['s0'] or '-'} -> S1 {ev['s1'] or '-'} ({fr_txt}) | ours "
            f"rank {o0['rank']}->{o1['rank']} score {o0['score']}->{o1['score']} count {o0['count']}->{o1['count']}"
            f"{delta} last {o0['last']}->{o1['last']} | passed TeamIds {passed} | UP test {ev['up']}; "
            f"{ev['attribution']} | {verdicts}")


# ---------------------------------------------------------------- synthetic stand-ins (dry run and tests)
class FakeClock:
    def __init__(self, start):
        self.t = start

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += dt.timedelta(seconds=max(0.0, s))


class FakeKaggle:
    """Scripted Kaggle CLI: refs turn terminal at `done` (ListSubmissions shows it at once), the LB shows it lag_s
    later (or the ref's own 'lag'); teams = [(TeamId, name, unrounded score)]; our best = max(our_base, visible
    COMPLETE scores); calls whose 1-based index is in throttle return a 429."""

    BASE_ROWS = [("56563534", "2026-09-26 00:02:18.207000", "probe 38: exp58n", "COMPLETE", "0.953"),
                 ("56563521", "2026-09-26 00:02:12.737000", "probe 37: exp58 = K2", "COMPLETE", "0.954")]

    def __init__(self, clock, refs, teams, our_base, lag_s=150, throttle=(), error_counts=False):
        self.clock, self.refs, self.teams, self.our_base = clock, refs, teams, our_base
        self.lag_s, self.throttle, self.error_counts = lag_s, set(throttle), error_counts
        self.log = []

    def status(self, r, now):
        return r["final"] if r["done"] is not None and now >= r["done"] else "PENDING"

    def run(self, args):
        assert_read_only(args)
        now = self.clock.now()
        self.log.append((now, args[1]))
        if len(self.log) in self.throttle:
            return 1, "", "429 Client Error: Too Many Requests for url: https://api.kaggle.com/v1/..."
        if args[1] == "submissions":
            buf = io.StringIO()
            w = csv.writer(buf, lineterminator="\n\n")        # the CLI's blank lines on Windows
            w.writerow(["ref", "fileName", "date", "description", "status", "publicScore", "privateScore"])
            for r in sorted(self.refs, key=lambda r: r["ref"], reverse=True):
                st = self.status(r, now)
                w.writerow([r["ref"], "submission.csv", r["date"] + ".000000", r["desc"], f"SubmissionStatus.{st}",
                            str(q3(r["score"])) if st == "COMPLETE" else "", ""])
            for ref, date, desc, st, sc in self.BASE_ROWS:
                w.writerow([ref, "submission.csv", date, desc, f"SubmissionStatus.{st}", sc, ""])
            return 0, buf.getvalue(), ""
        path = Path(args[-1])
        if not path.is_absolute():
            path = ROOT / path
        path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path / f"{COMP}.zip", "w") as zf:
            zf.writestr(f"{COMP}-publicleaderboard-{now:%Y-%m-%dT%H:%M:%S}.csv", self.lb_csv(now).encode("utf-8-sig"))
        return 0, f"Downloading {COMP}.zip to {path}\n", ""

    def lb_csv(self, now, members="gsfatakhov,sasyami,vitaliineibauer"):
        vis = [r for r in self.refs if r["done"] is not None
               and now >= r["done"] + dt.timedelta(seconds=r.get("lag", self.lag_s))]
        comp = [r for r in vis if r["final"] == "COMPLETE"]
        counted = comp + ([r for r in vis if r["final"] == "ERROR"] if self.error_counts else [])
        best = max([self.our_base] + [r["score"] for r in comp])
        last = max([BASE_LAST] + [r["date"] for r in counted])
        rows = [(s, tid, name, "2026-09-26 12:00:00", 30) for tid, name, s in self.teams]
        rows.append((best, OUR_TEAM_ID, OUR_TEAM, last, BASE_COUNT + len(counted)))
        rows.sort(key=lambda x: -x[0])
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(["Rank", "TeamId", "TeamName", "LastSubmissionDate", "Score", "SubmissionCount",
                    "TeamMemberUserNames"])
        for i, (s, tid, name, ls, n) in enumerate(rows, 1):
            w.writerow([i, tid, name, ls, str(q3(s)), n, members if tid == OUR_TEAM_ID else name.lower()])
        w.writerow([0, "1", "UNet Baseline", "2026-08-01 00:00:00", "0.900", 1, ""])
        return buf.getvalue()


def demo_teams():
    """214 teams displaying >= 0.955, 100 in the 0.954 block (0.95449 .. 0.95350), 100 at 0.953."""
    t = [(str(9000000 + i), f"Team A{i}", 0.9790 - i * 0.00011) for i in range(214)]
    t += [(str(9100000 + j), f"Team B{j}", 0.95449 - j * 0.00001) for j in range(100)]
    t += [(str(9200000 + j), f"Team C{j}", 0.95349 - j * 0.00001) for j in range(100)]
    return t


def demo_refs(start):
    def at(h, m, s=0):
        return start.replace(hour=h, minute=m, second=s)
    return [
        {"ref": "56589025", "date": "2026-09-26 21:15:23", "desc": "probe 39: exp70e", "final": "COMPLETE",
         "score": 0.954375, "done": at(4, 37, 10)},
        {"ref": "56589065", "date": "2026-09-26 21:17:47", "desc": "probe 40: exp70a", "final": "COMPLETE",
         "score": 0.954375, "done": at(4, 38, 5)},
        {"ref": "56589423", "date": "2026-09-26 21:38:33", "desc": "probe 41: exp70d", "final": "COMPLETE",
         "score": 0.954455, "done": at(5, 6, 0)},
        {"ref": "56592350", "date": "2026-09-27 00:05:50", "desc": "probe 42: exp70b", "final": "COMPLETE",
         "score": 0.95312, "done": at(7, 31, 0)},
    ]


def dry_run(out_dir=None, echo=None):
    """Synthetic ladder on a fake clock from 04:10Z (no network): 39+40 co-complete with equal displays (the first LB
    download is stale), 41 has an attributable UP, 42 displays 0.953; one 429 on the 4th call."""
    start = dt.datetime(2026, 9, 27, 4, 10, 0, tzinfo=UTC)
    out = Path(out_dir or tempfile.mkdtemp(prefix="ladder_watch_dry_"))
    out.mkdir(parents=True, exist_ok=True)
    poll_log = out / "fake_poll.log"
    t0 = start - dt.timedelta(seconds=40)
    poll_log.write_text("".join(f"=== {stamp(t0 + dt.timedelta(seconds=603 * k))}\nref,fileName\n"
                                for k in range(60)), encoding="utf-8")
    clock = FakeClock(start)
    cli = FakeKaggle(clock, demo_refs(start), demo_teams(), our_base=0.95435, throttle={4})
    w = Watcher(out_dir=out / "ladder_watch", poll_log=poll_log, cli=cli, clock=clock, echo=echo)
    rc = w.run()
    (echo or print)(f"[dry run] folder {out}; {len(cli.log)} fake CLI calls; exit code {rc}")
    return rc, w


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--poll-log", default=str(POLL_LOG))
    ap.add_argument("--error-counts", choices=("yes", "no"), help="pin whether an ERROR increments SubmissionCount")
    ap.add_argument("--soft-cap", default=stamp(SOFT_CAP))
    ap.add_argument("--hard-cap", default=stamp(HARD_CAP))
    ap.add_argument("--s0", help="first S0 taken before any ladder score: LB .csv/.zip/folder or an e10_watch .txt")
    ap.add_argument("--once", action="store_true", help="one ListSubmissions read (+ the S0 baseline if none), exit")
    ap.add_argument("--dry-run", action="store_true", help="synthetic scenario on a fake clock (no network)")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    if a.dry_run:
        return dry_run(None if a.out_dir == str(OUT_DIR) else a.out_dir)[0]
    w = Watcher(out_dir=a.out_dir, poll_log=a.poll_log, soft_cap=parse_utc(a.soft_cap),
                hard_cap=parse_utc(a.hard_cap), error_mode=a.error_counts)
    try:
        return w.run(once=a.once, s0_path=a.s0)
    except KeyboardInterrupt:
        w.save_state()
        w.say("interrupted (state saved)", log=True)
        return 130


if __name__ == "__main__":
    sys.exit(main())
