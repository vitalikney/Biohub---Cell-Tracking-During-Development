"""experiments/lb_poll/e10_watch_loop.py (READ-ONLY hourly E10 v3 watch) on synthetic CLI outputs with a fake clock;
no network: FakeKaggle stands in for subprocess.run (the loop's guard refuses anything but e10_snapshot's queries).

    python -m pytest tests/test_e10_watch_loop.py -q
"""
import datetime as dt
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location("e10_watch_loop", ROOT / "experiments" / "lb_poll" / "e10_watch_loop.py")
wl = importlib.util.module_from_spec(_spec)
sys.modules["e10_watch_loop"] = wl
_spec.loader.exec_module(wl)
es = wl.es

UTC = dt.timezone.utc
KHEAD = "ref,title,author,lastRunTime,totalVotes"
HF = 'raunakdey07/biohub-harmonic-fusion-v3,Biohub: Harmonic Fusion V3,Raunak Dey,2026-09-25 09:09:04.280000,176'
HF2 = 'raunakdey07/biohub-harmonic-fusion-v3,Biohub: Harmonic Fusion V3,Raunak Dey,2026-09-28 10:00:00.000000,177'
AMAN = "amanatar/optimized-biohub-max-score,optimized-biohub-max-score,Aman Atar,2026-09-27 01:39:05.377000,64"
AMAN2 = "amanatar/optimized-biohub-max-score,optimized-biohub-max-score,Aman Atar,2026-09-28 03:00:00.000000,65"
KUNAL = "kunaldesale2408/biohub-cell-tracking,Biohub Cell Tracking,Kunal Desale,2026-09-24 06:13:53.007000,230"
X138 = "anvithpothula/biohub-0-953-lb-original,Biohub 0.953 LB | ORIGINAL,Anvith Pothula,2026-09-21 09:47:58.620000,213"
X138B = "anvithpothula/biohub-0-953-lb-original,Biohub 0.953 LB | ORIGINAL,Anvith Pothula,2026-09-28 08:00:00.000000,214"
GEO = "amanatar/biohub-geometric-fusion,Biohub Geometric Fusion,Aman Atar,2026-09-21 09:18:35.700000,170"
EVG = "evgendvorkin/biohub-0-947-lb-proxy,Biohub 0.947 LB,Evgen,2026-09-22 15:39:25.977000,137"
SJ = "sjlee101/biohub-lf-dctta,biohub-lf-dctta,Seung Jae Lee,2026-09-09 20:31:52.350000,429"   # 429 votes: not a 429
HEIR = "newbie/biohub-x138-heir,Biohub 0.957 LB | x138 heir,New Bie,2026-09-28 09:00:00.000000,1"
RISER = "riser/biohub-riser,Biohub riser,Ri Ser,2026-09-28 09:30:00.000000,3"
V1284 = "anvithpothula/biohub-v1284-head-s075-notebook,biohub v1284,Anvith Pothula,2026-09-24 03:28:30.973000,1"
TT = "thtennant/biohub-frontier947-readmit-v1,Biohub frontier947 readmit v1,Teddy Tennant,2026-09-19 01:41:22.390000,1"
TT_NEW = "thtennant/misc-notebook,misc notebook,Teddy Tennant,2026-09-28 07:00:00.000000,0"
KNEE = "amanatar/rsna-knee-super-ensemble-0920,RSNA Knee Super Ensemble 0920,Aman Atar,2026-09-28 02:12:58.663000,14"
S6 = "amanatar/s6e9-realmlp,S6E9: RealMLP,Aman Atar,2026-09-23 01:37:06.037000,4"
OLD_AMAN = "amanatar/enveda-casmi-2026,Enveda CASMI 2026,Aman Atar,2026-09-01 10:23:34.017000,1"

BASE_K = {
    "comp_dateRun": [AMAN, HF, KUNAL],
    "comp_scoreDescending": [HF, AMAN, KUNAL, X138, GEO, EVG, SJ],
    "user_anvithpothula": [V1284, X138],
    "user_thtennant": [TT],
    "user_amanatar": [AMAN, S6, GEO],
}
BASE_S = {"amanatar/optimized-biohub-max-score": "COMPLETE", "anvithpothula/biohub-0-953-lb-original": "COMPLETE"}
LB = ("Rank,TeamId,TeamName,LastSubmissionDate,Score,SubmissionCount,TeamMemberUserNames\n"
      '1,101,"Top One","2026-09-25 23:54:29",0.975,101,a\n'
      '2,16810638,"D: Discipline","2026-09-27 00:05:50",0.954,44,"x,y"\n')


def T(d, h, m=0, s=0):
    return dt.datetime(2026, 9, d, h, m, s, tzinfo=UTC)


def rows(lines):
    return es.parse_kernel_csv(KHEAD + "\n" + "\n".join(lines) + "\n")


def st(**over):
    k = dict(BASE_K, **over)
    return {"kernels": {key: (None if v is None else rows(v)) for key, v in k.items()},
            "status": {"status_" + r.replace("/", "__"): s for r, s in BASE_S.items()}}


class FakeClock:
    def __init__(self, start, on_sleep=None):
        self.t, self.sleeps, self.on_sleep = start, [], on_sleep

    def now(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += dt.timedelta(seconds=max(0.0, s))
        if self.on_sleep:
            self.on_sleep(self)


class FakeKaggle:
    """subprocess.run stand-in: kernel lists / statuses / LB download by the query args; klists(now) may change them
    over time; calls whose 1-based index is in throttle answer 429."""

    def __init__(self, clock, klists=None, throttle=()):
        self.clock, self.klists, self.throttle = clock, klists or (lambda now: {}), set(throttle)
        self.keys = {tuple(a): k for k, _kind, a, _w in es.queries()}
        self.calls = []

    def __call__(self, cmd, **kw):
        args = list(cmd[3:])
        self.calls.append((self.clock.now(), args))
        if len(self.calls) in self.throttle:
            return subprocess.CompletedProcess(cmd, 1, "", "429 Client Error: Too Many Requests for url: https://x")
        if args[:len(es.LB_ARGS)] == es.LB_ARGS:
            (Path(args[-1]) / "lb.csv").write_text(LB, encoding="utf-8")
            return subprocess.CompletedProcess(cmd, 0, "Downloading lb.zip\n", "")
        key = self.keys[tuple(args)]
        if key.startswith("status_"):
            ref = key[len("status_"):].replace("__", "/")
            return subprocess.CompletedProcess(cmd, 0, f'{ref} has status "KernelWorkerStatus.{BASE_S[ref]}"\n', "")
        lines = dict(BASE_K, **self.klists(self.clock.now()))[key]
        return subprocess.CompletedProcess(cmd, 0, KHEAD + "\r\r\n" + "".join(r + "\r\r\n" for r in lines), "")


def make_loop(tmp_path, clock, fk, end=T(29, 12), poll_log=None, echo=None):
    out = []
    loop = wl.WatchLoop(out_dir=tmp_path / "w", poll_log=poll_log or tmp_path / "no_poll.log", base_runner=fk,
                        clock=clock, end=end, echo=echo or out.append, pause_paths=[tmp_path / "w" / "PAUSE"])
    return loop, out


def sig(events, kind=None):
    return sorted((e["kind"], e["ref"]) for e in events if e["level"] == "SIGNAL" and (kind is None or e["kind"] == kind))


# ---------------------------------------------------------------- read-only guard and 429 parsing
@pytest.mark.parametrize("args", [
    ["competitions", "submit", es.COMP, "-f", "submission.csv", "-m", "x"],
    ["kernels", "push", "-p", "experiments/x"],
    ["kernels", "pull", "amanatar/optimized-biohub-max-score"],
    ["kernels", "output", "anvithpothula/biohub-0-953-lb-original"],
    ["kernels", "list", "--competition", es.COMP, "--sort-by", "hotness", "--page-size", "20", "-v"],
    es.LB_ARGS,                                               # the download needs its one temp folder
])
def test_guard_refuses_anything_but_the_snapshot_queries(tmp_path, args):
    called = []
    gr = wl.GatedRunner(lambda *a, **k: called.append(a), FakeClock(T(28, 1)), lambda *a, **k: None,
                        poll_log=tmp_path / "none", pause_paths=[])
    with pytest.raises(RuntimeError, match="refuses"):
        gr([sys.executable, "-m", "kaggle", *args])
    assert not called and gr.calls == 0


def test_guard_allows_every_snapshot_query(tmp_path):
    fk = FakeKaggle(FakeClock(T(28, 1)))
    gr = wl.GatedRunner(fk, fk.clock, lambda *a, **k: None, poll_log=tmp_path / "none", pause_paths=[])
    for _k, _kind, a, _w in es.queries():
        assert gr([sys.executable, "-m", "kaggle", *a]).returncode == 0
    d = tmp_path / "lbdir"
    d.mkdir()
    assert gr([sys.executable, "-m", "kaggle", *es.LB_ARGS, str(d)]).returncode == 0
    assert gr.calls == len(es.queries()) + 1


def test_is_429():
    cp = subprocess.CompletedProcess
    assert wl.is_429(cp([], 1, "", "429 Client Error: Too Many Requests"))
    assert wl.is_429(cp([], 1, "HTTP 429", ""))
    assert wl.is_429(cp([], 0, "429 Client Error: Too Many Requests for url", ""))
    assert not wl.is_429(cp([], 0, KHEAD + "\n" + SJ + "\n", ""))            # a kernel with 429 votes


# ---------------------------------------------------------------- signal rules
def test_no_change_no_signal():
    assert sig(wl.compare(st(), st())) == []


def test_a_new_kernel_above_the_top_ref_and_b_top5():
    cur = st(comp_scoreDescending=[HEIR, HF, AMAN, KUNAL, X138, GEO, EVG, SJ])
    ev = wl.compare(st(), cur)
    assert sig(ev) == [("a", "newbie/biohub-x138-heir"), ("b", "newbie/biohub-x138-heir")]
    lines = wl.signal_lines(ev, "snap.txt")
    assert len(lines) == 1 and lines[0].startswith("E10 SIGNAL: newbie/biohub-x138-heir (a,b) pos 1")
    assert "ABOVE the top ref raunakdey07/biohub-harmonic-fusion-v3 (pos 2)" in lines[0]
    # the next run sees the same order: no repeat
    assert sig(wl.compare(cur, cur)) == []


def test_a_known_kernel_moving_above_the_top_ref():
    cur = st(comp_scoreDescending=[AMAN2, HF, KUNAL, X138, GEO, EVG, SJ])
    assert sig(wl.compare(st(), cur), "a") == [("a", "amanatar/optimized-biohub-max-score")]


def test_a_kernel_already_above_signals_again_only_on_a_new_run():
    prev = st(comp_scoreDescending=[HEIR, HF, AMAN, KUNAL, X138])
    same = st(comp_scoreDescending=[HEIR, HF, AMAN, KUNAL, X138])
    rerun = st(comp_scoreDescending=[HEIR.replace("2026-09-28 09:00", "2026-09-28 11:00"), HF, AMAN, KUNAL, X138])
    assert sig(wl.compare(prev, same)) == []
    assert sig(wl.compare(prev, rerun)) == [("a", "newbie/biohub-x138-heir")]


def test_a_top_ref_rerun():
    cur = st(comp_scoreDescending=[HF2, AMAN, KUNAL, X138, GEO, EVG, SJ])
    assert sig(wl.compare(st(), cur)) == [("a", "raunakdey07/biohub-harmonic-fusion-v3")]


def test_a_top_ref_missing_uses_the_highest_known_ref_as_anchor():
    cur = st(comp_scoreDescending=[HEIR, AMAN, KUNAL, X138, GEO, EVG, SJ])       # HF v3 gone
    ev = wl.compare(st(), cur)
    assert any(e["level"] == "WARN" and "anchor = amanatar/optimized-biohub-max-score" in e["text"] for e in ev)
    assert sig(ev, "a") == [("a", "newbie/biohub-x138-heir")]
    # HF v3 gone, nothing new: no (a) (amanatar becomes the anchor, nothing above it); EVG moving up to pos 5 is (b)
    assert sig(wl.compare(st(), st(comp_scoreDescending=[AMAN, KUNAL, X138, GEO, EVG, SJ]))) == [
        ("b", "evgendvorkin/biohub-0-947-lb-proxy")]


def test_b_new_ref_in_top5_below_the_top_ref():
    cur = st(comp_scoreDescending=[HF, AMAN, RISER, KUNAL, X138, GEO, EVG, SJ])
    assert sig(wl.compare(st(), cur)) == [("b", "riser/biohub-riser")]
    cur2 = st(comp_scoreDescending=[HF, AMAN, KUNAL, X138, EVG, GEO, SJ])        # EVG from pos 6 to pos 5
    ev = wl.compare(st(), cur2)
    assert sig(ev) == [("b", "evgendvorkin/biohub-0-947-lb-proxy")]
    assert "was pos 6" in [e for e in ev if e["level"] == "SIGNAL"][0]["text"]


def test_c_watched_users():
    ev = wl.compare(st(), st(user_anvithpothula=[X138B, V1284], user_thtennant=[TT_NEW, TT],
                             user_amanatar=[AMAN2, KNEE, S6, GEO]))
    assert sig(ev) == [("c", "amanatar/optimized-biohub-max-score"), ("c", "anvithpothula/biohub-0-953-lb-original"),
                       ("c", "thtennant/misc-notebook")]
    knee = [e for e in ev if e["ref"] == "amanatar/rsna-knee-super-ensemble-0920"]
    assert [e["level"] for e in knee] == ["INFO"] and "not Biohub-related" in knee[0]["text"]


def test_c_reappearing_older_kernel_is_info_only():
    ev = wl.compare(st(), st(user_amanatar=[AMAN, S6, OLD_AMAN]))                  # GEO dropped, an old one back
    assert sig(ev) == []
    assert any(e["level"] == "INFO" and e["ref"] == "amanatar/enveda-casmi-2026" and "reappeared" in e["text"]
               for e in ev)


def test_failed_fetch_is_a_warning_and_the_baseline_is_info():
    ev = wl.compare(st(), st(comp_scoreDescending=None, user_thtennant=None))
    assert sig(ev) == []
    assert {e["kind"] for e in ev if e["level"] == "WARN"} == {"a/b", "c"}
    ev0 = wl.compare({"kernels": {}, "status": {}}, st(comp_scoreDescending=[HEIR, HF]))
    assert sig(ev0) == [] and any("baseline" in e["text"] for e in ev0)


def test_status_change_is_info():
    cur = st()
    cur["status"]["status_amanatar__optimized-biohub-max-score"] = "RUNNING"
    ev = wl.compare(st(), cur)
    assert sig(ev) == [] and any(e["kind"] == "status" and "COMPLETE -> RUNNING" in e["text"] for e in ev)


# ---------------------------------------------------------------- the loop
def test_hourly_loop_until_end_signals_once(tmp_path):
    clock = FakeClock(T(29, 9, 30))
    fk = FakeKaggle(clock, klists=lambda now: (
        {"comp_scoreDescending": [HEIR, HF, AMAN, KUNAL, X138, GEO, EVG, SJ]} if now >= T(29, 10) else {}))
    loop, out = make_loop(tmp_path, clock, fk)
    assert loop.run() == 0
    w = tmp_path / "w"
    snaps = sorted(p.name for p in w.glob("*.txt"))
    assert snaps == ["20260929T0930Z.txt", "20260929T1030Z.txt", "20260929T1130Z.txt"]
    assert sorted({t for t, _ in fk.calls}) == [T(29, 9, 30), T(29, 10, 30), T(29, 11, 30)]
    assert len(fk.calls) == 3 * (len(es.queries()) + 1)                      # 8 calls per run
    log = (w / "watch_loop.log").read_text(encoding="utf-8")
    sigs = [ln for ln in log.splitlines() if ln.startswith("E10 SIGNAL: ")]
    assert len(sigs) == 1 and sigs[0].startswith("E10 SIGNAL: newbie/biohub-x138-heir (a,b)")
    assert "20260929T1030Z.txt" in sigs[0]
    assert "END (2026-09-29T12:00:00Z reached); runs 3, signals 1" in log
    assert log.count(" RUN ") == 3
    js = [json.loads(x) for x in (w / "watch_loop_signals.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {(j["kind"], j["ref"]) for j in js} == {("a", "newbie/biohub-x138-heir"), ("b", "newbie/biohub-x138-heir")}
    state = json.loads((w / "watch_loop_state.json").read_text(encoding="utf-8"))
    assert state["runs"] == 3 and state["last_run_utc"] == "2026-09-29T11:30:00Z"
    assert any(ln.startswith("E10 SIGNAL: ") for ln in out)                  # printed too


def test_restart_resumes_the_hourly_schedule(tmp_path):
    clock = FakeClock(T(28, 9, 30))
    fk = FakeKaggle(clock)
    loop, _ = make_loop(tmp_path, clock, fk)
    assert loop.run(once=True) == 0
    n = len(fk.calls)
    clock.t = T(28, 10, 0)                                                    # crash + restart 30 min later
    loop2, out = make_loop(tmp_path, clock, fk, end=T(28, 10, 45))
    assert loop2.run() == 0
    assert any("resumed from watch_loop_state.json" in x for x in out)
    assert {t for t, _ in fk.calls[n:]} == {T(28, 10, 30)}


def test_first_run_compares_with_the_newest_snapshot_on_disk(tmp_path):
    clock = FakeClock(T(28, 8, 0))
    fk = FakeKaggle(clock, klists=lambda now: (
        {"user_anvithpothula": [X138B, V1284]} if now >= T(28, 9) else {}))
    es.take_snapshot(tmp_path / "w", clock.now(), runner=fk, sleep=lambda s: None)   # a manual P1 snapshot
    clock.t = T(28, 9, 5)
    loop, out = make_loop(tmp_path, clock, fk)
    loop.run(once=True)
    assert any("baseline lists from 20260928T0800Z.txt" in x for x in out)
    assert [x for x in out if x.startswith("E10 SIGNAL: ")][0].startswith(
        "E10 SIGNAL: anvithpothula/biohub-0-953-lb-original (c)")


def test_poller_guard_delays_the_first_call(tmp_path):
    poll = tmp_path / "poll.log"
    poll.write_text("".join(f"=== {(T(28, 9, 0) - dt.timedelta(seconds=603 * k + 20)):%Y-%m-%dT%H:%M:%S}Z\nx\n"
                            for k in (3, 2, 1, 0)), encoding="utf-8")        # last poll 20 s ago
    clock = FakeClock(T(28, 9, 0))
    fk = FakeKaggle(clock)
    loop, out = make_loop(tmp_path, clock, fk, poll_log=poll)
    loop.run(once=True)
    first = fk.calls[0][0]
    assert first >= T(28, 9, 0, 40) and (first - T(28, 8, 59, 40)).total_seconds() >= 60
    assert any("skip: within" in x for x in out)


def test_pause_file_holds_every_call(tmp_path):
    (tmp_path / "w").mkdir()
    pause = tmp_path / "w" / "PAUSE"
    pause.write_text("", encoding="utf-8")

    def lift(c):
        if c.t >= T(28, 9, 3):
            pause.unlink(missing_ok=True)
    clock = FakeClock(T(28, 9, 0), on_sleep=lift)
    fk = FakeKaggle(clock)
    loop, out = make_loop(tmp_path, clock, fk)
    loop.run(once=True)
    assert fk.calls[0][0] >= T(28, 9, 3)
    assert any("PAUSE file" in x for x in out)


def test_429_backs_off_then_cuts_the_run_and_delays_the_next(tmp_path):
    clock = FakeClock(T(28, 9, 0))
    fk = FakeKaggle(clock, throttle=(1, 2, 3))
    loop, out = make_loop(tmp_path, clock, fk)
    loop.run(once=True)
    assert len(fk.calls) == 3                                                 # nothing after the third 429
    assert clock.sleeps.count(60) == 2
    state = json.loads((tmp_path / "w" / "watch_loop_state.json").read_text(encoding="utf-8"))
    assert state["streak_429"] == 1
    assert loop.next_due() == T(28, 9, 0) + dt.timedelta(minutes=90)
    log = (tmp_path / "w" / "watch_loop.log").read_text(encoding="utf-8")
    assert "run cut short" in log and "fetch OK 0/8" in log


def test_one_429_backs_off_and_recovers(tmp_path):
    clock = FakeClock(T(28, 9, 0))
    fk = FakeKaggle(clock, throttle=(1,))
    loop, _ = make_loop(tmp_path, clock, fk)
    loop.run(once=True)
    log = (tmp_path / "w" / "watch_loop.log").read_text(encoding="utf-8")
    assert "fetch OK 8/8" in log and "429s 1" in log
    assert loop.next_due() == T(28, 9, 0) + dt.timedelta(minutes=60)


def test_a_failed_signal_write_repeats_the_signal_next_run(tmp_path):
    """review_watch_1: the good lists advance only after the signals are written, so a disk error (or a kill) between
    the snapshot and the signal write repeats the signal next run instead of losing it."""
    clock = FakeClock(T(28, 9, 0))
    fk = FakeKaggle(clock, klists=lambda now: (
        {"comp_scoreDescending": [HEIR, HF, AMAN, KUNAL, X138, GEO, EVG, SJ]} if now >= T(28, 10) else {}))
    loop, out = make_loop(tmp_path, clock, fk)
    loop.run(once=True)                                                       # baseline
    w = tmp_path / "w"
    (w / "watch_loop_signals.jsonl").mkdir()                                  # the signal write fails
    clock.t = T(28, 10, 0)
    loop.run(once=True)
    assert any("RUN FAILED" in x for x in out)
    (w / "watch_loop_signals.jsonl").rmdir()
    clock.t = T(28, 11, 0)
    out.clear()
    loop.run(once=True)
    sigs = [x for x in out if x.startswith("E10 SIGNAL: ")]
    assert len(sigs) == 1 and sigs[0].startswith("E10 SIGNAL: newbie/biohub-x138-heir (a,b)")
    js = (w / "watch_loop_signals.jsonl").read_text(encoding="utf-8").splitlines()
    assert {json.loads(x)["kind"] for x in js} == {"a", "b"}


def test_past_end_exits_without_calls(tmp_path):
    clock = FakeClock(T(29, 12, 1))
    fk = FakeKaggle(clock)
    loop, out = make_loop(tmp_path, clock, fk)
    assert loop.run() == 0 and fk.calls == [] and any("END" in x for x in out)


def test_cli_dry_run(tmp_path, capsys):
    cache = tmp_path / "cache"
    cache.mkdir()
    for key, lines in BASE_K.items():
        (cache / f"{key}.out").write_text(KHEAD + "\n" + "".join(r + "\n" for r in lines), encoding="utf-8")
    for ref, s in BASE_S.items():
        (cache / f"status_{ref.replace('/', '__')}.out").write_text(
            f'{ref} has status "KernelWorkerStatus.{s}"\n', encoding="utf-8")
    (cache / "leaderboard.csv").write_text(LB, encoding="utf-8")
    assert wl.main(["--dry-run-from", str(cache), "--out-dir", str(tmp_path / "o")]) == 0
    printed = capsys.readouterr().out
    assert "RUN 1 snapshot" in printed and "fetch OK 8/8" in printed
    assert len(list((tmp_path / "o").glob("*-dryrun.txt"))) == 1
    assert wl.main(["--dry-run-from", str(cache)]) == 2                       # never into experiments/e10_watch


def test_restart_script_runs_the_loop():
    sh = (ROOT / "experiments" / "lb_poll" / "run_e10_watch_loop.sh").read_text(encoding="utf-8")
    assert "experiments/lb_poll/e10_watch_loop.py" in sh and sh.lstrip().startswith("#!/usr/bin/env bash")
    assert "until " in sh and "watch_loop.stdout.log" in sh


# ---------------------------------------------------------------- review_watch_0 (correctness lens)
class FlakyKaggle(FakeKaggle):
    """FakeKaggle whose kernel list answers a 500 when klists(now) maps its key to None."""

    def __call__(self, cmd, **kw):
        args = list(cmd[3:])
        key = self.keys.get(tuple(args))
        if key and key.startswith(("comp_", "user_")) and self.klists(self.clock.now()).get(key, 0) is None:
            self.calls.append((self.clock.now(), args))
            return subprocess.CompletedProcess(cmd, 1, "", "500 Server Error: Internal Server Error")
        return super().__call__(cmd, **kw)


def test_state_save_failure_neither_crashes_nor_reruns_at_once(tmp_path):
    """A state file that cannot be saved (disk full, locked file) used to crash run() in its except path; the restart
    wrapper then re-ran at once: 8 calls every ~3 min. Now the process stays up on the in-memory hourly schedule."""
    clock = FakeClock(T(28, 9, 0))
    fk = FakeKaggle(clock)
    loop, _ = make_loop(tmp_path, clock, fk)
    loop.run(once=True)
    (tmp_path / "w" / "watch_loop_state.tmp").mkdir()                          # every later save fails
    clock.t = T(28, 10, 0)
    loop2, out = make_loop(tmp_path, clock, fk, end=T(28, 11, 30))
    assert loop2.run() == 0
    assert sorted({t for t, _ in fk.calls}) == [T(28, 9, 0), T(28, 10, 0), T(28, 11, 0)]
    assert any("RUN FAILED" in x and "state save failed too" in x for x in out)


def test_log_write_failure_still_prints_the_signal(tmp_path):
    clock = FakeClock(T(28, 9, 0))
    fk = FakeKaggle(clock, klists=lambda now: (
        {"comp_scoreDescending": [HEIR, HF, AMAN, KUNAL, X138, GEO, EVG, SJ]} if now >= T(28, 10) else {}))
    loop, out = make_loop(tmp_path, clock, fk)
    loop.run(once=True)
    (tmp_path / "w" / "watch_loop.log").unlink()
    (tmp_path / "w" / "watch_loop.log").mkdir()                                # the log cannot be appended
    clock.t = T(28, 10, 0)
    assert loop.run(once=True) == 0
    assert [x for x in out if x.startswith("E10 SIGNAL: newbie/biohub-x138-heir (a,b)")]
    assert any("watch_loop.log write failed" in x for x in out)


def test_a_failed_fetch_keeps_the_last_good_list(tmp_path):
    """The heir appears while scoreDescending fails: the failed run must not replace the good list (else the next
    run would be a silent 'baseline' and the heir would never signal)."""
    clock = FakeClock(T(28, 9, 0))
    heir = [HEIR, HF, AMAN, KUNAL, X138, GEO, EVG, SJ]
    fk = FlakyKaggle(clock, klists=lambda now: (
        {} if now < T(28, 10) else {"comp_scoreDescending": None} if now < T(28, 11) else
        {"comp_scoreDescending": heir}))
    loop, out = make_loop(tmp_path, clock, fk)
    loop.run(once=True)
    clock.t = T(28, 10, 0)
    loop.run(once=True)
    assert not [x for x in out if x.startswith("E10 SIGNAL: ")]
    assert any("comp_scoreDescending fetch failed" in x for x in out)
    clock.t = T(28, 11, 0)
    loop.run(once=True)
    assert [x for x in out if x.startswith("E10 SIGNAL: newbie/biohub-x138-heir (a,b)")]


def test_live_bootstrap_skips_dry_run_snapshots(tmp_path):
    heir = {"comp_scoreDescending": [HEIR, HF, AMAN, KUNAL, X138, GEO, EVG, SJ]}
    clock = FakeClock(T(28, 8, 0))
    es.take_snapshot(tmp_path / "w", T(28, 8, 0), runner=FakeKaggle(clock), sleep=lambda s: None)
    es.take_snapshot(tmp_path / "w", T(28, 8, 30), runner=FakeKaggle(clock, klists=lambda now: heir),
                     sleep=lambda s: None, dry=tmp_path)                        # a manual dry run (e10_snapshot default dir)
    clock.t = T(28, 9, 0)
    loop, out = make_loop(tmp_path, clock, FakeKaggle(clock, klists=lambda now: heir))
    loop.run(once=True)
    assert any("baseline lists from 20260928T0800Z.txt" in x for x in out)
    assert [x for x in out if x.startswith("E10 SIGNAL: newbie/biohub-x138-heir (a,b)")]


def test_no_call_after_end_while_a_run_is_held(tmp_path):
    (tmp_path / "w").mkdir()
    pause = tmp_path / "w" / "PAUSE"
    pause.write_text("", encoding="utf-8")

    def lift(c):
        if c.t >= T(29, 12, 5):
            pause.unlink(missing_ok=True)
    clock = FakeClock(T(29, 11, 58), on_sleep=lift)
    fk = FakeKaggle(clock)
    loop, _ = make_loop(tmp_path, clock, fk)
    assert loop.run() == 0
    assert fk.calls == []


def test_once_runs_now_even_when_not_due(tmp_path):
    clock = FakeClock(T(28, 9, 0))
    fk = FakeKaggle(clock)
    loop, _ = make_loop(tmp_path, clock, fk)
    loop.run(once=True)
    clock.t = T(28, 9, 10)
    loop2, _ = make_loop(tmp_path, clock, fk)
    loop2.run(once=True)
    assert sorted({t for t, _ in fk.calls}) == [T(28, 9, 0), T(28, 9, 10)]


def test_sleep_stops_at_end_when_the_next_run_is_later(tmp_path):
    clock = FakeClock(T(29, 11, 0))
    fk = FakeKaggle(clock, throttle=(1, 2, 3))                                  # 429-cut run: next due 12:30
    loop, _ = make_loop(tmp_path, clock, fk)
    assert loop.run() == 0
    assert clock.t == T(29, 12, 0)


def test_a_known_kernel_moving_above_the_top_ref_without_a_rerun():
    cur = st(comp_scoreDescending=[AMAN, HF, KUNAL, X138, GEO, EVG, SJ])
    assert sig(wl.compare(st(), cur)) == [("a", "amanatar/optimized-biohub-max-score")]


REAL = ROOT / "experiments" / "e10_watch"
PAIRS = [("20260926T2246Z.txt", "20260927T0147Z.txt", [("c", "amanatar/optimized-biohub-max-score")]),
         ("20260927T0147Z.txt", "20260927T0531Z.txt", []),                   # rsna-knee re-run: INFO only
         ("20260927T0831Z.txt", "20260927T1101Z.txt", [])]


@pytest.mark.parametrize("a,b,want", PAIRS)
def test_real_snapshot_history(a, b, want):
    if not (REAL / a).exists() or not (REAL / b).exists():
        pytest.skip("real snapshots not present")
    load = lambda n: es.load_state((REAL / n).read_text(encoding="utf-8", errors="replace"))  # noqa: E731
    assert sig(wl.compare(load(a), load(b))) == want


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
