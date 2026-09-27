"""READ-ONLY hourly E10 v3 watch loop (CONTEXT.md 27 Sep 11:08 UTC 'USER INSTRUCTION = E10 v3').

    python experiments/lb_poll/e10_watch_loop.py              # live, from the repo root, as a background process
    python experiments/lb_poll/e10_watch_loop.py --once       # one gated snapshot + signal check, then exit
    python experiments/lb_poll/e10_watch_loop.py --dry-run-from DIR --out-dir SCRATCH   # replay cached CLI outputs
    bash experiments/lb_poll/run_e10_watch_loop.sh            # restart wrapper (main session starts it; not started here)

Every INTERVAL_S (60 min) until END (29 Sep 12:00 UTC) it takes one tools/e10_snapshot.py snapshot in-process
(take_snapshot: the same file, DIFF and read-only CLI calls as `python tools/e10_snapshot.py`) into
experiments/e10_watch/ and compares the parsed kernel lists with the last good lists it saw. The only Kaggle commands
are e10_snapshot's queries(): `kernels list` x5, `kernels status` x2 and `competitions leaderboard --download` into a
temp folder; any other command raises before a subprocess starts. Nothing is pulled, pushed or submitted, and no
kernel imports this file.

SIGNALS ('E10 SIGNAL: <ref> (<kinds>) ...', printed, appended to experiments/e10_watch/watch_loop.log and, as JSON, to
experiments/e10_watch/watch_loop_signals.jsonl):
  (a) a competition kernel sits ABOVE the top ref (TOP_REF = HF v3 raunakdey07/biohub-harmonic-fusion-v3, pos 1 of
      scoreDescending at 0.953 on 27 Sep; x138 is at pos 4) in the scoreDescending top-20 and was not above it (with
      the same lastRunTime) in the last good list; also the top ref's own new lastRunTime (a new version may score
      higher). If the top ref leaves the top-20, the anchor is the highest ref of the current list that was already
      in the last good list (WARN line).
  (b) a ref enters the scoreDescending top-5 (was not in the last good top-5).
  (c) a new lastRunTime of a kernel of anvithpothula (x138 author) or thtennant (any kernel), or of amanatar (only a
      Biohub-related kernel: 'biohub' in ref/title, a ref of a competition list, or a status ref; the rest, e.g. the
      RSNA / S6E9 kernels, is an INFO line). A ref new to a top-10 dateRun list counts when its lastRunTime is newer
      than the oldest one of the last good list (else it only reappeared: INFO).
  The kernel API has no score field: a signal starts a look (its public score on the notebook page / the LB); the
  E10 v3 trigger itself is a public notebook whose own public score is >= 0.955.
INFO lines: status changes of the two status refs, new refs in the competition dateRun top-20, reappearing refs.

API budget. Before every CLI call it waits while experiments/e10_watch/PAUSE or experiments/lb_poll/ladder_watch/PAUSE
exists and while the clock is within +-60 s of lb_poll.py's last or next expected poll (poll.log headers, read only;
ladder_watch.poller_wait_s). A 429 backs off BACKOFF_429_S (60 s) at most MAX_429_PER_RUN (2) times per run; after
that the rest of the run is skipped without calls (the snapshot records FAILED fetches) and the next run is delayed by
EXTRA_429_S (30 min) per consecutive 429-aborted run (at most 2 x). Per run: 8 calls when nothing fails (e10_snapshot
retries a failed call up to 3 x, 10 s apart).

State: experiments/e10_watch/watch_loop_state.json (last run time, the last good kernel lists / statuses, 429 streak);
a restart resumes the hourly schedule from it. Without a state file the comparison baseline is the newest good list of
each key in the snapshots already in the folder (live runs skip -dryrun files). Exit code 0 at END or after --once.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for _p in (str(ROOT), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ladder_watch as lw  # noqa: E402  (poller-phase helpers; poll.log is only read)
import tools.e10_snapshot as es  # noqa: E402

UTC = dt.timezone.utc
END = dt.datetime(2026, 9, 29, 12, 0, tzinfo=UTC)
INTERVAL_S = 3600
TOP_REF = "raunakdey07/biohub-harmonic-fusion-v3"
TOP_N = 5
SCORE_KEY, DATE_KEY = "comp_scoreDescending", "comp_dateRun"
ANY_KERNEL_USERS = ("anvithpothula", "thtennant")      # every new lastRunTime counts
BIOHUB_ONLY_USERS = ("amanatar",)                      # only Biohub-related kernels count (the rest is INFO)
BACKOFF_429_S, MAX_429_PER_RUN, EXTRA_429_S, MAX_429_STREAK = 60, 2, 1800, 2
PAUSE_POLL_S = 60
OUT_DIR = ROOT / "experiments" / "e10_watch"
POLL_LOG = ROOT / "experiments" / "lb_poll" / "poll.log"
PAUSE_PATHS = (OUT_DIR / "PAUSE", ROOT / "experiments" / "lb_poll" / "ladder_watch" / "PAUSE")
RE_429 = re.compile(r"\b429\b|Too Many Requests", re.I)            # stderr, or stdout of a failed call
RE_429_OUT = re.compile(r"429 Client Error|Too Many Requests", re.I)  # stdout of rc 0 (a CSV may hold 429 votes)
LOOK = "look: its public score (notebook page / LB); E10 v3 trigger = own public score >= 0.955"


def stamp(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(s):
    return lw.parse_utc(s)


# ---------------------------------------------------------------- read-only guard
ALLOWED = {tuple(a) for _k, _kind, a, _w in es.queries()}


def assert_read_only(cmd):
    """Only e10_snapshot's queries and its leaderboard download (into one temp folder) may run."""
    args = list(cmd[3:]) if list(cmd[1:3]) == ["-m", "kaggle"] else None
    ok = args is not None and (tuple(args) in ALLOWED or (
        args[:len(es.LB_ARGS)] == es.LB_ARGS and len(args) == len(es.LB_ARGS) + 1))
    if not ok:
        raise RuntimeError(f"e10_watch_loop refuses a non-read-only command: {cmd}")


def is_429(p):
    """A throttled call: 429 in stderr (or in stdout when rc != 0); a successful stdout needs the HTTP phrase, since a
    kernel CSV row may hold 429 votes."""
    out, err = p.stdout or "", p.stderr or ""
    if RE_429.search(err) or (p.returncode != 0 and RE_429.search(out)):
        return True
    return bool(RE_429_OUT.search(out))


class Clock:
    def now(self):
        return dt.datetime.now(UTC)

    def sleep(self, s):
        if s > 0:
            time.sleep(s)


class GatedRunner:
    """subprocess.run stand-in for es.take_snapshot: read-only guard, PAUSE files, lb_poll phase guard, 429 rule."""

    def __init__(self, base, clock, say, poll_log=POLL_LOG, pause_paths=PAUSE_PATHS, end=END, poller_guard=True):
        self.base, self.clock, self.say = base, clock, say
        self.poll_log, self.pause_paths, self.end = Path(poll_log), [Path(p) for p in pause_paths], end
        self.poller_guard = poller_guard
        self.calls, self.n429, self.aborted, self.why = 0, 0, False, ""

    def gate(self):
        noted = False
        while True:
            now = self.clock.now()
            if now >= self.end:
                return False
            paused = [p for p in self.pause_paths if p.exists()]
            if paused:
                if not noted:
                    self.say(f"PAUSE file {paused[0]} present: no Kaggle call until it is removed")
                    noted = True
                self.clock.sleep(PAUSE_POLL_S)
                continue
            if self.poller_guard:
                wait, why = lw.poller_wait_s(now, lw.read_poll_headers(self.poll_log))
                if wait > 0:
                    self.say(f"skip: {why}; next call in {wait:.0f} s")
                    self.clock.sleep(wait)
                    continue
            return True

    def sleep(self, s):
        """e10_snapshot's retry sleep; nothing to wait for once the run is aborted."""
        if not self.aborted:
            self.clock.sleep(s)

    def __call__(self, cmd, **kw):
        assert_read_only(cmd)
        if not self.aborted and not self.gate():
            self.aborted, self.why = True, "END reached"
        if self.aborted:
            return subprocess.CompletedProcess(cmd, 1, "", f"e10_watch_loop: call skipped ({self.why})")
        p = self.base(cmd, **kw)
        self.calls += 1
        if is_429(p):
            self.n429 += 1
            if self.n429 <= MAX_429_PER_RUN:
                self.say(f"429 on `kaggle {' '.join(cmd[3:6])}`: backing off {BACKOFF_429_S} s "
                         f"({self.n429}/{MAX_429_PER_RUN})")
                self.clock.sleep(BACKOFF_429_S)
            else:
                self.aborted, self.why = True, f"429 after {MAX_429_PER_RUN} back-offs"
                self.say(f"429 again after {MAX_429_PER_RUN} back-offs: the rest of this run is skipped", log=True)
        return p


# ---------------------------------------------------------------- signal rules (pure)
def _t(s):
    return (s or "")[:19]


def _pos(rows):
    return {r["ref"]: i + 1 for i, r in enumerate(rows)}


def _desc(r):
    return f'lastRunTime {_t(r["lastRunTime"])} "{r["title"]}" by {r["author"]}'


def is_biohub(row, comp_refs):
    return ("biohub" in f"{row['ref']} {row['title']}".lower() or row["ref"] in comp_refs
            or row["ref"] in es.STATUS_REFS)


def compare(prev, cur, top_ref=TOP_REF):
    """prev = {'kernels': {key: rows}, 'status': {key: str}} (last good lists; a key may be missing), cur = es.load_state
    of the new snapshot -> events [{level: SIGNAL / INFO / WARN, kind, ref, text}]."""
    ev = []
    pk, ck = prev.get("kernels", {}), cur.get("kernels", {})

    def add(level, kind, ref, text):
        ev.append({"level": level, "kind": kind, "ref": ref, "text": text})

    # (a) + (b): scoreDescending
    a, b = pk.get(SCORE_KEY), ck.get(SCORE_KEY)
    if b is None:
        add("WARN", "a/b", "", f"{SCORE_KEY} fetch failed: (a)/(b) not evaluated this run")
    elif a is None:
        add("INFO", "a/b", "", f"{SCORE_KEY}: no earlier good list; this run is the baseline")
    else:
        pa, pb = _pos(a), _pos(b)
        rows_a = {r["ref"]: r for r in a}
        if top_ref in pb:
            anchor = top_ref
        else:
            anchor = next((r["ref"] for r in b if r["ref"] in pa), None)
            add("WARN", "a", top_ref, f"top ref {top_ref} not in the scoreDescending top-20; anchor = "
                                      f"{anchor or 'none (no known ref left)'}")
        cut = pb[anchor] if anchor else len(b) + 1
        prev_above = ({r for r, i in pa.items() if i < pa[anchor]} if anchor in pa else set(pa))
        for r in b[:cut - 1]:
            o = rows_a.get(r["ref"])
            if r["ref"] not in prev_above or o is None or o["lastRunTime"] != r["lastRunTime"]:
                was = (f"was pos {pa[r['ref']]}" if r["ref"] in pa else "was not in the top-20")
                if o is not None and o["lastRunTime"] != r["lastRunTime"]:
                    was += f", lastRunTime {_t(o['lastRunTime'])} -> {_t(r['lastRunTime'])}"
                add("SIGNAL", "a", r["ref"], f"pos {pb[r['ref']]} in scoreDescending, ABOVE the top ref {anchor} "
                                             f"(pos {cut}); {was}; {_desc(r)}")
        if anchor == top_ref and top_ref in rows_a:
            o, r = rows_a[top_ref], b[pb[top_ref] - 1]
            if o["lastRunTime"] != r["lastRunTime"]:
                add("SIGNAL", "a", top_ref, f"the top ref re-ran: lastRunTime {_t(o['lastRunTime'])} -> "
                                            f"{_t(r['lastRunTime'])} (pos {pb[top_ref]}); {_desc(r)}")
        top_a = {r["ref"] for r in a[:TOP_N]}
        for r in b[:TOP_N]:
            if r["ref"] not in top_a:
                was = f"was pos {pa[r['ref']]}" if r["ref"] in pa else "was not in the top-20"
                add("SIGNAL", "b", r["ref"], f"entered the scoreDescending top-{TOP_N} at pos {pb[r['ref']]} ({was}); "
                                             f"{_desc(r)}")

    # INFO: new competition kernels by dateRun
    a, b = pk.get(DATE_KEY), ck.get(DATE_KEY)
    if a is not None and b is not None:
        known = {r["ref"] for r in a}
        new = [r for r in b if r["ref"] not in known]
        for r in new[:5]:
            add("INFO", "dateRun", r["ref"], f"new in the competition dateRun top-20; {_desc(r)}")
        if len(new) > 5:
            add("INFO", "dateRun", "", f"... {len(new) - 5} more new refs in the dateRun top-20")

    # (c): watched users
    comp_refs = {r["ref"] for key in (SCORE_KEY, DATE_KEY) for src in (pk, ck) for r in (src.get(key) or [])}
    for u in ANY_KERNEL_USERS + BIOHUB_ONLY_USERS:
        key = f"user_{u}"
        a, b = pk.get(key), ck.get(key)
        if b is None:
            add("WARN", "c", u, f"{key} fetch failed: (c) not evaluated for {u} this run")
            continue
        if a is None:
            add("INFO", "c", u, f"{key}: no earlier good list; this run is the baseline")
            continue
        rows_a = {r["ref"]: r for r in a}
        oldest = min((r["lastRunTime"] for r in a), default="")
        for r in b:
            o = rows_a.get(r["ref"])
            if o is not None and o["lastRunTime"] == r["lastRunTime"]:
                continue
            if o is None and a and r["lastRunTime"] <= oldest:
                add("INFO", "c", r["ref"], f"reappeared in the {u} dateRun top-10 with an older run; {_desc(r)}")
                continue
            what = ("new lastRunTime " + (f"{_t(o['lastRunTime'])} -> {_t(r['lastRunTime'])}" if o else
                                          f"{_t(r['lastRunTime'])} (new in the {u} top-10)"))
            if u in ANY_KERNEL_USERS or is_biohub(r, comp_refs):
                add("SIGNAL", "c", r["ref"], f"watched user {u}: {what}; {_desc(r)}")
            else:
                add("INFO", "c", r["ref"], f"watched user {u}, not Biohub-related: {what}; {_desc(r)}")

    # INFO: statuses
    for key, sb in cur.get("status", {}).items():
        sa = prev.get("status", {}).get(key)
        if sa is not None and sb is not None and sa != sb:
            add("INFO", "status", key[len("status_"):].replace("__", "/"), f"status {sa} -> {sb}")
    return ev


def signal_lines(events, where):
    """SIGNAL events grouped per ref -> ['E10 SIGNAL: <ref> (<kinds>) <texts> [<where>]', ...]."""
    by = {}
    for e in events:
        if e["level"] == "SIGNAL":
            by.setdefault(e["ref"], []).append(e)
    return [f"E10 SIGNAL: {ref} ({','.join(sorted({e['kind'] for e in es_}))}) "
            + " | ".join(e["text"] for e in es_) + f" | {LOOK} [{where}]" for ref, es_ in by.items()]


# ---------------------------------------------------------------- the loop
def new_state():
    return {"version": 1, "last_run_utc": None, "runs": 0, "signals": 0, "streak_429": 0,
            "good": {"kernels": {}, "status": {}}, "good_from": {}}


def bootstrap_from_snapshots(out_dir, live=True):
    """Newest good kernel list / status per key from the snapshot files already in out_dir."""
    good, src = {"kernels": {}, "status": {}}, {}
    files = sorted(((es.snap_key(p.name), p) for p in Path(out_dir).glob("*.txt") if es.snap_key(p.name)),
                   key=lambda x: x[0][:2], reverse=True)
    keys = [(k, kind) for k, kind, _a, _w in es.queries()]
    for sk, p in files:
        if live and sk[2]:
            continue
        st = es.load_state(p.read_text(encoding="utf-8", errors="replace"))
        for k, kind in keys:
            bucket = "kernels" if kind == "kernels" else "status"
            if k not in good[bucket] and st[bucket].get(k) is not None:
                good[bucket][k], src[k] = st[bucket][k], p.name
        if all(k in good["kernels" if kind == "kernels" else "status"] for k, kind in keys):
            break
    return good, src


class WatchLoop:
    def __init__(self, out_dir=OUT_DIR, poll_log=POLL_LOG, base_runner=subprocess.run, clock=None, end=END,
                 interval_s=INTERVAL_S, top_ref=TOP_REF, echo=None, dry=None, pause_paths=None):
        self.out_dir, self.poll_log = Path(out_dir), Path(poll_log)
        self.base_runner, self.clock = base_runner, clock or Clock()
        self.end, self.interval_s, self.top_ref, self.dry = end, interval_s, top_ref, dry
        self.pause_paths = list(pause_paths) if pause_paths is not None else (
            [self.out_dir / "PAUSE", PAUSE_PATHS[1]])
        self.echo = echo or (lambda s: print(s, flush=True))
        self.log_path = self.out_dir / "watch_loop.log"
        self.state_path = self.out_dir / "watch_loop_state.json"
        self.signals_path = self.out_dir / "watch_loop_signals.jsonl"
        self.state = new_state()

    def say(self, msg, log=False, raw=False):
        line = msg if raw else f"{stamp(self.clock.now())} {msg}"
        self.echo(line)
        if log:
            try:
                self.out_dir.mkdir(parents=True, exist_ok=True)
                with self.log_path.open("a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except OSError as exc:  # review_watch_0: the line is already printed; a log error must not crash the loop
                self.echo(f"{stamp(self.clock.now())} WARN watch_loop.log write failed ({type(exc).__name__}: {exc})")

    def save_state(self):
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=1), encoding="utf-8")
        os.replace(tmp, self.state_path)

    def load_state(self):
        if self.state_path.exists():
            self.state = dict(new_state(), **json.loads(self.state_path.read_text(encoding="utf-8")))
            return f"resumed from {self.state_path.name} (last run {self.state['last_run_utc']})"
        good, src = bootstrap_from_snapshots(self.out_dir, live=self.dry is None)
        self.state["good"], self.state["good_from"] = good, src
        names = sorted(set(src.values()))
        return ("no state file; baseline lists from " + (", ".join(names) if names else "nothing (first run is the "
                                                                                        "baseline)"))

    def next_due(self):
        last = self.state.get("last_run_utc")
        if not last:
            return self.clock.now()
        extra = EXTRA_429_S * min(self.state.get("streak_429", 0), MAX_429_STREAK)
        return parse_utc(last) + dt.timedelta(seconds=self.interval_s + extra)

    def run_once(self):
        started = self.clock.now()
        gr = GatedRunner(self.base_runner, self.clock, self.say, poll_log=self.poll_log,
                         pause_paths=self.pause_paths, end=self.end, poller_guard=self.dry is None)
        snap = es.take_snapshot(self.out_dir, started, runner=gr, sleep=gr.sleep,
                                attempts=1 if self.dry is not None else es.ATTEMPTS, dry=self.dry)
        cur = snap["state"]
        events = compare(self.state["good"], cur, self.top_ref)
        self.state["runs"] += 1
        self.state["last_run_utc"] = stamp(started)
        self.state["streak_429"] = self.state.get("streak_429", 0) + 1 if gr.aborted and gr.n429 else 0
        sig = signal_lines(events, f"{snap['path'].name}, {stamp(started)}")
        # The good lists advance (and the state is saved) only AFTER the signals are written: a crash / kill / disk
        # error in between repeats a signal on the next run instead of losing it (review_watch_1).
        ok = sum(1 for f in snap["fetches"] + [snap["lb"]] if f["state"] == "OK")
        n = len(snap["fetches"]) + 1
        self.say(f"RUN {self.state['runs']} snapshot {snap['path'].name} CHANGES={snap['changes']} fetch OK {ok}/{n}"
                 + (f" FAILED {','.join(snap['failed'])}" if snap["failed"] else "")
                 + f" | calls {gr.calls} 429s {gr.n429}" + (" (run cut short)" if gr.aborted else "")
                 + f" | signals {len(sig)} | next run {stamp(self.next_due())}", log=True)
        for e in events:
            if e["level"] != "SIGNAL":
                self.say(f"{e['level']} ({e['kind']}) {e['ref']}: {e['text']}".replace(" : ", ": "), log=True)
        if sig:
            with self.signals_path.open("a", encoding="utf-8") as f:
                for e in events:
                    if e["level"] == "SIGNAL":
                        f.write(json.dumps(dict(e, utc=stamp(started), snapshot=snap["path"].name)) + "\n")
        for line in sig:
            self.say(line, log=True, raw=True)
        for bucket in ("kernels", "status"):
            for k, v in cur[bucket].items():
                if v is not None:
                    self.state["good"][bucket][k] = v
                    self.state["good_from"][k] = snap["path"].name
        self.state["signals"] += len(sig)
        self.save_state()
        return sig

    def run(self, once=False):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        how = self.load_state()
        self.say(f"START E10 v3 watch loop (read-only; {how}); every {self.interval_s // 60} min until "
                 f"{stamp(self.end)}; top ref {self.top_ref}; mode "
                 f"{'DRY RUN from ' + str(self.dry) if self.dry else 'LIVE'}", log=True)
        while True:
            now = self.clock.now()
            if now >= self.end:
                self.say(f"END ({stamp(self.end)} reached); runs {self.state['runs']}, signals "
                         f"{self.state['signals']}", log=True)
                return 0
            due = self.next_due()
            if once or now >= due:
                try:
                    self.run_once()
                except Exception as exc:  # disk / parse trouble: log it, keep the hourly schedule
                    self.state["last_run_utc"] = stamp(now)
                    why = f"{type(exc).__name__}: {exc}"
                    try:
                        self.save_state()
                    except Exception as exc2:  # review_watch_0: never crash here; a crash lets the restart wrapper
                        # re-run at once (8 calls every ~3 min while the state cannot be saved); the in-memory
                        # schedule keeps the hourly pace while this process lives
                        why += f"; state save failed too ({type(exc2).__name__}: {exc2})"
                    self.say(f"RUN FAILED {why}; next run {stamp(self.next_due())}", log=True)
                if once:
                    return 0
                continue
            self.clock.sleep(min((due - now).total_seconds(), (self.end - now).total_seconds()))


def main(argv=None):
    ap = argparse.ArgumentParser(description="READ-ONLY hourly E10 v3 watch loop (module doc).")
    ap.add_argument("--once", action="store_true", help="one run now, then exit")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--poll-log", default=str(POLL_LOG))
    ap.add_argument("--end", default=stamp(END), help="stop time (UTC), default 2026-09-29T12:00:00Z")
    ap.add_argument("--interval-min", type=float, default=INTERVAL_S / 60)
    ap.add_argument("--top-ref", default=TOP_REF)
    ap.add_argument("--dry-run-from", default=None, help="replay cached CLI outputs (tools/e10_snapshot.py format); "
                                                         "needs a non-default --out-dir; implies --once")
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass
    dry = Path(a.dry_run_from) if a.dry_run_from else None
    if dry is not None:
        if not dry.is_dir():
            print(f"e10_watch_loop: --dry-run-from {dry} is not a folder", file=sys.stderr)
            return 2
        if Path(a.out_dir).resolve() == OUT_DIR.resolve():
            print("e10_watch_loop: a dry run needs its own --out-dir (not experiments/e10_watch)", file=sys.stderr)
            return 2
    loop = WatchLoop(out_dir=a.out_dir, poll_log=a.poll_log, end=parse_utc(a.end),
                     interval_s=int(round(a.interval_min * 60)), top_ref=a.top_ref, dry=dry,
                     base_runner=es.CacheRunner(dry) if dry is not None else subprocess.run)
    return loop.run(once=a.once or dry is not None)


if __name__ == "__main__":
    sys.exit(main())
