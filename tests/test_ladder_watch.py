"""experiments/lb_poll/ladder_watch.py (R13-A2 read-only ladder watcher) on synthetic CLI outputs and leaderboards;
no network: FakeKaggle stands in for the CLI (and, like the real wrapper, refuses anything but the two read-only
commands), FakeClock for time.

    python -m pytest tests/test_ladder_watch.py -q
"""
import datetime as dt
import importlib.util
import json
import sys
import zipfile
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("ladder_watch", ROOT / "experiments" / "lb_poll" / "ladder_watch.py")
lw = importlib.util.module_from_spec(_spec)
sys.modules["ladder_watch"] = lw
_spec.loader.exec_module(lw)

UTC = lw.UTC
E, A, D, B = "56589025", "56589065", "56589423", "56592350"
SCRATCH_LB = Path("C:/Users/vital/AppData/Local/Temp/claude/c--Users-vital-Documents-kAGGLE-Biohub---Cell-Tracking"
                  "-During-Development/acabaea6-42c1-4115-a146-2ddc5bb7e8c8/scratchpad/lb/r13/biohub-cell-tracking"
                  "-during-development-publicleaderboard-2026-09-26T22_46_47.csv")


def T(h, m, s=0):
    return dt.datetime(2026, 9, 27, h, m, s, tzinfo=UTC)


# ---------------------------------------------------------------- synthetic inputs
SUB_TEXT = (
    "ref,fileName,date,description,status,publicScore,privateScore\n\n"
    '56592350,submission.csv,2026-09-27 00:05:50.347000,"probe 42: exp70b = K2 + forkmid 4.5 (ladder L4, class B)",'
    "SubmissionStatus.PENDING,,\n\n"
    '56589423,submission.csv,2026-09-26 21:38:33.837000,"probe 41: exp70d = K2 + DeepCenter safe-div 0.30 (ladder '
    'L2, class B)",SubmissionStatus.COMPLETE,0.955,\n\n'
    '56589065,submission.csv,2026-09-26 21:17:47.170000,"probe 40: exp70a = K2 + leaf prune 0.3 (ladder L1, class A)",'
    "SubmissionStatus.ERROR,,\n\n"
    '56589025,submission.csv,2026-09-26 21:15:23.887000,"probe 39: exp70e = K2 + leaf prune 0.3 + DeepCenter '
    'safe-div 0.30 (ladder L3, R7 lifted by user 26 Sep 20:33Z)",SubmissionStatus.PENDING,,\n\n'
    "56563534,submission.csv,2026-09-26 00:02:18.207000,probe 38: exp58n = K2 twin without the insertion (x138 + "
    "safetail + lowrefine); AMENDMENT f2 F2 candidate; twin gates pass,SubmissionStatus.COMPLETE,0.953,\n\n"
    "56563521,submission.csv,2026-09-26 00:02:12.737000,probe 37: exp58 = K2 (x138 + safetail C01 + lowrefine + "
    "DaughterNet insertion #35 config); dummy gates 18/18,SubmissionStatus.COMPLETE,0.954,\n\n")

LB_HEAD = "Rank,TeamId,TeamName,LastSubmissionDate,Score,SubmissionCount,TeamMemberUserNames"


def lb_text(rows, bom=True):
    body = "\n".join([LB_HEAD] + [",".join(map(str, r)) for r in rows]) + "\n"
    return ("\ufeff" if bom else "") + body


def ours_row(rank, score="0.954", count=40, last="2026-09-26 00:02:18"):
    return (rank, lw.OUR_TEAM_ID, '"D: Discipline"', f'"{last}"', score, count, '"gsfatakhov,sasyami,vitaliineibauer"')


def team(rank, tid, score):
    return (rank, tid, f"Team {tid}", '"2026-09-26 12:00:00"', score, 30, f"user{tid}")


def subs_of(*items):
    """(ref, status, display, date) -> a parsed-submissions dict."""
    return {r: {"ref": r, "date": d, "description": "", "status": st, "public": None if p is None else Decimal(p)}
            for r, st, p, d in items}


def fref(ref, done, score, final="COMPLETE", date="2026-09-26 21:15:23", lag=None):
    r = {"ref": ref, "date": date, "desc": f"probe {ref}", "final": final, "score": score, "done": done}
    if lag is not None:
        r["lag"] = lag
    return r


TEAMS = [("901", "A1", 0.9600), ("902", "A2", 0.9551), ("903", "B0", 0.95449), ("904", "B1", 0.95440),
         ("905", "B2", 0.95436), ("906", "C0", 0.9534)]
OUR_BASE = 0.95435                                      # rank 6 behind A1, A2, B0, B1, B2


def make(tmp_path, refs, start=T(4, 10), hard_cap=T(9, 40), headers=(), lag_s=150, throttle=(), error_counts=False,
         teams=TEAMS, **kw):
    clock = lw.FakeClock(start)
    tmp_path.mkdir(parents=True, exist_ok=True)
    poll = tmp_path / "poll.log"
    poll.write_text("".join(f"=== {lw.stamp(h)}\nref,fileName\n" for h in headers), encoding="utf-8")
    cli = lw.FakeKaggle(clock, refs, teams, OUR_BASE, lag_s=lag_s, throttle=throttle, error_counts=error_counts)
    lines = []
    w = lw.Watcher(out_dir=tmp_path / "lw", poll_log=poll, cli=cli, clock=clock, hard_cap=hard_cap, echo=lines.append,
                   **kw)
    return w, cli, clock, lines


def events(w):
    return [ln for ln in w.log_path.read_text(encoding="utf-8").splitlines() if " EVENT " in ln]


def verdicts(w):
    return {r: (v["verdict"], v["unit"]) for r, v in w.state["verdicts"].items()}


# ---------------------------------------------------------------- parsers
def test_parse_submissions_cli_csv_with_blank_lines_and_preamble():
    s = lw.parse_submissions("Using competition: x\n" + SUB_TEXT)
    assert list(s)[:4] == [B, D, A, E]
    assert s[D]["status"] == "COMPLETE" and s[D]["public"] == Decimal("0.955")
    assert s[A]["status"] == "ERROR" and s[A]["public"] is None
    assert s[B]["status"] == "PENDING" and s[B]["date"] == "2026-09-27 00:05:50"
    assert "ladder L4, class B" in s[B]["description"]
    assert s["56563534"]["public"] == Decimal("0.953")
    assert lw.tracked(s) == [B, D, A, E]                 # probe 37/38 are part of the baseline 40
    assert lw.statuses(s) == {B: "PENDING", D: "COMPLETE", A: "ERROR", E: "PENDING"}


def test_parse_submissions_failures():
    assert lw.parse_submissions("429 Client Error: Too Many Requests") is None
    assert lw.parse_submissions("") is None
    assert lw.parse_submissions("No submissions found") == {}


def test_parse_submissions_on_the_real_poll_log_block():
    log = ROOT / "experiments" / "lb_poll" / "poll.log"
    if not log.exists():
        pytest.skip("no poll.log")
    text = log.read_text(encoding="utf-8", errors="replace")
    block = text[text.rindex("\n=== ") + 1:].split("\n", 1)[1]
    s = lw.parse_submissions(block)
    if not s:
        pytest.skip("last poll.log block has no CSV (poller error)")
    for r in lw.WATCHED:
        assert r in s and s[r]["status"] in ("PENDING", "COMPLETE", "ERROR")
    assert s["56563534"]["status"] == "COMPLETE" and s["56563534"]["public"] == Decimal("0.953")


def test_parse_lb_synthetic_bom_rank0_and_our_row():
    t = lb_text([team(1, "901", "0.978"), team(2, "902", "0.955"), ours_row(3), team(4, "904", "0.954"),
                 (0, "1", "UNet Baseline", '"2026-08-01 00:00:00"', "0.900", 1, "")])
    lb = lw.parse_lb(t)
    assert lb["teams"] == 4                              # the Rank-0 benchmark row is not a team
    assert lb["ours"] == {"rank": 3, "id": lw.OUR_TEAM_ID, "name": "D: Discipline", "last": "2026-09-26 00:02:18",
                          "score": "0.954", "count": 40}
    assert lb["above"] == ["901", "902"] and lb["ranks"]["904"] == 4
    assert lw.parse_lb(lb_text([team(1, "901", "0.978")]))["ours"] is None
    assert lw.parse_lb(lb_text([team(1, "901", "0.978")]))["above"] == []
    assert lw.parse_lb("Rank,TeamId,Score\n1,2,0.9\n") is None          # no SubmissionCount column


def test_extract_lb_zip_with_colon_member(tmp_path):
    member = f"{lw.COMP}-publicleaderboard-2026-09-27T04:39:12.csv"
    with zipfile.ZipFile(tmp_path / f"{lw.COMP}.zip", "w") as zf:
        zf.writestr(member, lb_text([ours_row(1)]).encode("utf-8"))
    p = lw.extract_lb(tmp_path)
    assert p.name == f"{lw.COMP}-publicleaderboard-2026-09-27T04_39_12.csv" and p.exists()
    assert lw.load_lb(tmp_path)["ours"]["rank"] == 1
    assert lw.extract_lb(tmp_path) == p                  # second use reads the extracted CSV


def test_real_lb_2246Z_from_the_e10_snapshot():
    """The 22:46Z LB rows >= 0.953 kept in the tracked e10 snapshot: our row #229 / 40 / 2026-09-26 00:02:18."""
    p = ROOT / "experiments" / "e10_watch" / "20260926T2246Z.txt"
    if not p.exists():
        pytest.skip("no e10 snapshot")
    lb = lw.parse_lb(lw.read_lb_source(p))
    o = lb["ours"]
    assert (o["rank"], o["count"], o["last"], o["score"]) == (229, 40, "2026-09-26 00:02:18", "0.954")
    assert len(lb["above"]) == 228


@pytest.mark.skipif(not SCRATCH_LB.exists(), reason="session scratchpad copy of the 22:46Z LB CSV not present")
def test_real_lb_2246Z_full_csv():
    lb = lw.parse_lb(lw.read_lb_source(SCRATCH_LB))
    assert lb["teams"] == 3935
    assert (lb["ours"]["rank"], lb["ours"]["count"], lb["ours"]["last"]) == (229, 40, "2026-09-26 00:02:18")


# ---------------------------------------------------------------- freshness, UP test, attribution, units
def test_freshness_key():
    pend = subs_of((E, "PENDING", None, "d1"), (A, "PENDING", None, "d2"))
    assert lw.freshness(40, pend)["fresh"] and not lw.freshness(41, pend)["fresh"]
    two = subs_of((E, "COMPLETE", "0.954", "d1"), (A, "COMPLETE", "0.954", "d2"), (D, "PENDING", None, "d3"))
    f = lw.freshness(41, two)
    assert not f["fresh"] and f["expected"] == [42] and f["err_counted"] == "n.a."
    assert lw.freshness(42, two)["fresh"]
    assert not lw.freshness(None, two)["fresh"]           # our row missing
    err = subs_of((E, "COMPLETE", "0.954", "d1"), (A, "ERROR", None, "d2"))
    assert lw.freshness(41, err)["err_counted"] == "no"
    assert lw.freshness(41, err)["fresh"] and lw.freshness(42, err)["fresh"]
    assert lw.freshness(42, err)["err_counted"] == "yes"
    assert not lw.freshness(40, err)["fresh"] and lw.freshness(40, err)["err_counted"] == "?"
    assert lw.freshness(42, err, "yes")["fresh"] and not lw.freshness(41, err, "yes")["fresh"]
    assert lw.freshness(41, err, "no")["fresh"] and not lw.freshness(42, err, "no")["fresh"]
    later = subs_of((E, "COMPLETE", "0.954", "d1"), ("56600000", "COMPLETE", "0.955", "d9"))
    assert lw.freshness(42, later)["fresh"]              # a later non-watched submission counts too


def test_expected_last_date():
    s = subs_of((E, "COMPLETE", "0.954", "2026-09-26 21:15:23"), (A, "PENDING", None, "2026-09-26 21:17:47"))
    assert lw.expected_last(s) == "2026-09-26 21:15:23"
    assert lw.expected_last(subs_of((E, "PENDING", None, "2026-09-26 21:15:23"))) == lw.BASE_LAST


def test_up_test():
    s0 = lw.parse_lb(lb_text([team(1, "901", "0.955"), team(2, "902", "0.954"), team(3, "903", "0.954"),
                              ours_row(4)]))
    moved = lw.parse_lb(lb_text([team(1, "901", "0.955"), team(2, "902", "0.954"), ours_row(3, count=41),
                                 team(4, "903", "0.954")]))
    assert lw.up_test(s0, moved) == ["903"]
    others_rose = lw.parse_lb(lb_text([team(1, "905", "0.956"), team(2, "901", "0.955"), team(3, "902", "0.954"),
                                       team(4, "903", "0.954"), ours_row(5, count=41)]))
    assert lw.up_test(s0, others_rose) == []            # we fell back: never NEG, just no UP
    gone = lw.parse_lb(lb_text([team(1, "901", "0.955"), team(2, "902", "0.954"), ours_row(3, count=41)]))
    assert lw.up_test(s0, gone) == []                   # a team missing from S1 is not a pass
    assert lw.up_test(s0, lw.parse_lb(lb_text([team(1, "901", "0.955")]))) is None


def test_attribution_rules():
    s = subs_of((E, "COMPLETE", "0.954", "d"), (A, "COMPLETE", "0.955", "d"), (D, "COMPLETE", "0.954", "d"),
                (B, "ERROR", None, "d"))
    assert lw.attribute([E], s, True)[0] == E                               # single
    assert lw.attribute([E], s, False) == (None, "no UP")
    ref, txt = lw.attribute([E, A], s, True)                                 # co-completion, different displays
    assert ref == A and "higher display" in txt
    ref, txt = lw.attribute([E, D], s, True)                                 # co-completion, equal displays
    assert ref is None and "non-attributable" in txt
    assert lw.attribute([E, D, A], s, True)[0] == A
    assert lw.attribute([], s, True)[1].endswith("(anomaly)")


def test_unit_status_and_ref_verdict():
    assert lw.unit_status(Decimal("0.955"), False) == "POS"
    assert lw.unit_status(Decimal("0.954"), True) == "POS"
    assert lw.unit_status(Decimal("0.954"), False) == "NEU"
    assert lw.unit_status(Decimal("0.953"), True) == "NEG"
    assert lw.unit_status(None, False) == "NEU"
    s = subs_of((E, "COMPLETE", "0.954", "d"), (A, "COMPLETE", "0.953", "d"), (B, "ERROR", None, "d"),
                (D, "COMPLETE", "0.956", "d"))
    assert lw.ref_verdict(E, s, True, E) == ("UP", "POS")
    assert lw.ref_verdict(E, s, True, None) == ("NEU", "NEU")
    assert lw.ref_verdict(E, s, False, None) == ("AMBIGUOUS", "NEU")
    assert lw.ref_verdict(A, s, False, None) == ("NEG", "NEG")               # a display <= 0.953 needs no LB
    assert lw.ref_verdict(B, s, True, None) == ("ERROR", "NEU")
    assert lw.ref_verdict(D, s, False, None) == ("AMBIGUOUS", "POS")


# ---------------------------------------------------------------- poller phase, gate, read-only guard, 429
def test_read_poll_headers_and_period(tmp_path):
    p = tmp_path / "poll.log"
    p.write_text("=== 2026-09-27T01:09:26Z\nref,x\n\n=== 2026-09-27T01:19:29Z [empty stdout, rc=1, stderr='429 ...']\n"
                 "=== 2026-09-27T01:29:31Z\nref,x\n", encoding="utf-8")
    h = lw.read_poll_headers(p)
    assert h == [T(1, 9, 26), T(1, 19, 29), T(1, 29, 31)]
    assert lw.poller_period(h) == pytest.approx(602.5)
    assert lw.poller_period(h[:1]) == lw.POLLER_PERIOD_S
    assert lw.read_poll_headers(tmp_path / "missing.log") == []


def test_poller_wait():
    last = T(4, 9, 20)
    hs = [last - dt.timedelta(seconds=603 * k) for k in (3, 2, 1, 0)]
    w, why = lw.poller_wait_s(last + dt.timedelta(seconds=30), hs)          # 30 s after its last poll
    assert w == pytest.approx(31) and "last poll" in why
    w, why = lw.poller_wait_s(last + dt.timedelta(seconds=603 - 45), hs)    # 45 s before the next one
    assert w == pytest.approx(106) and "expected poll" in why
    assert lw.poller_wait_s(last + dt.timedelta(seconds=603 + 59), hs)[0] > 0
    assert lw.poller_wait_s(last + dt.timedelta(seconds=300), hs)[0] == 0
    assert lw.poller_wait_s(last + dt.timedelta(seconds=603 + 61), hs)[0] == 0
    assert lw.poller_wait_s(last + dt.timedelta(seconds=2 * 603 - 10), hs)[0] > 0
    w, why = lw.poller_wait_s(last + dt.timedelta(seconds=2000), hs)        # poller silent: phase unknown
    assert w == 0 and "unknown" in why
    assert lw.poller_wait_s(last, [])[0] == 0
    future = hs + [last + dt.timedelta(seconds=603)]                         # headers after now are ignored
    assert lw.poller_wait_s(last + dt.timedelta(seconds=300), future)[0] == 0


def test_no_call_within_60s_of_the_poller(tmp_path):
    start = T(4, 10)
    hs = [start - dt.timedelta(seconds=40) + dt.timedelta(seconds=603 * k) for k in range(40)]
    w, cli, clock, lines = make(tmp_path, [fref(E, T(4, 31), 0.95438, lag=0)], headers=hs, hard_cap=T(5, 0))
    assert w.run() == 0
    assert cli.log and all(min(abs((t - h).total_seconds()) for h in hs) >= 60 for t, _ in cli.log)
    assert any("skip: within" in ln for ln in lines)


def test_read_only_guard():
    lw.assert_read_only(list(lw.SUB_ARGS))
    lw.assert_read_only(lw.LB_ARGS + ["experiments/lb_poll/ladder_watch/20260927T041000Z/"])
    for bad in (["competitions", "submit", lw.COMP, "-f", "submission.csv", "-m", "x"],
                ["kernels", "push", "-p", "."], ["competitions", "leaderboard", lw.COMP, "-s"],
                ["competitions", "submissions", "other-comp", "-v"], lw.LB_ARGS + ["a", "b"]):
        with pytest.raises(RuntimeError):
            lw.assert_read_only(bad)
    with pytest.raises(RuntimeError):
        lw.FakeKaggle(lw.FakeClock(T(4, 0)), [], [], 0.95).run(["competitions", "submit", lw.COMP])


def test_429_backs_off_twice_then_pauses_10_min(tmp_path):
    w, cli, clock, lines = make(tmp_path, [], throttle={1, 2, 3})
    w.out_dir.mkdir(parents=True)
    t0 = clock.now()
    assert w.read_submissions() is None
    assert len(cli.log) == 3 and (clock.now() - t0).total_seconds() == 60 + 60 + 600
    assert sum("backing off 60 s" in ln for ln in lines) == 2 and any("pausing 10 min" in ln for ln in lines)
    w2, cli2, clock2, _ = make(tmp_path / "b", [], throttle={1, 2})
    w2.out_dir.mkdir(parents=True)
    assert w2.read_submissions() is not None and len(cli2.log) == 3
    assert (clock2.now() - T(4, 10)).total_seconds() == 120


def test_pause_file_blocks_every_call(tmp_path):
    w, cli, clock, lines = make(tmp_path, [fref(E, T(4, 20), 0.95438)], hard_cap=T(4, 30))
    w.out_dir.mkdir(parents=True)
    (w.out_dir / "PAUSE").write_text("", encoding="utf-8")
    assert w.run() == 0
    assert cli.log == [] and clock.now() >= T(4, 30) and any("PAUSE file" in ln for ln in lines)


def test_cadence_fast_then_slow():
    w = lw.Watcher(clock=lw.FakeClock(T(6, 44)), cli=object())
    w.state["last_statuses"] = {r: "PENDING" for r in lw.WATCHED}
    assert w.interval() == 120
    w.clock = lw.FakeClock(T(6, 46))
    assert w.interval() == 300                                              # soft cap 06:45Z
    w.clock = lw.FakeClock(T(5, 0))
    w.state["last_statuses"].update({E: "COMPLETE", A: "ERROR"})
    assert w.interval() == 300                                              # < 2 of 39-41 pending
    w.state["last_statuses"] = None
    assert w.interval() == 120


# ---------------------------------------------------------------- whole-loop scenarios (fake clock + fake CLI)
def test_dry_run_scenario(tmp_path):
    lines = []
    rc, w = lw.dry_run(tmp_path, echo=lines.append)
    assert rc == 0
    assert verdicts(w) == {A: ("NEU", "NEU"), E: ("NEU", "NEU"), D: ("UP", "POS"), B: ("NEG", "NEG")}
    ev = events(w)
    assert len(ev) == 3
    assert "co-completion of 2: equal top displays 0.954" in ev[0] and "fresh after 3 download(s)" in ev[0]
    assert "single completion" in ev[1] and "count 42->43 (+1)" in ev[1] and "passed TeamIds 8" in ev[1]
    assert "UP test FAIL" in ev[2]
    assert any("429 on ListSubmissions: backing off 60 s" in ln for ln in lines)
    assert any("STOP (all four watched refs terminal)" in ln for ln in lines)
    st = json.loads(w.state_path.read_text(encoding="utf-8"))
    assert st["s0"]["ours"]["count"] == 44 and st["events"] == 3


def test_single_completion_attributable_up(tmp_path):
    w, cli, clock, _ = make(tmp_path, [fref(E, T(4, 31), 0.95438, lag=0)], hard_cap=T(5, 0))
    assert w.run() == 0
    assert verdicts(w) == {E: ("UP", "POS")}
    (ev,) = events(w)
    assert "rank 6->5" in ev and "count 40->41 (+1)" in ev and "passed TeamIds 1" in ev
    assert "LastSubmissionDate ok" in ev
    assert sum(a == "leaderboard" for _, a in cli.log) == 2                 # S0 + one fresh S1


def test_co_completion_higher_display_takes_the_up(tmp_path):
    refs = [fref(E, T(4, 31), 0.95438, lag=0), fref(A, T(4, 31), 0.95510, date="2026-09-26 21:17:47", lag=0)]
    w, *_ = make(tmp_path, refs, hard_cap=T(5, 0))
    assert w.run() == 0
    assert verdicts(w) == {A: ("UP", "POS"), E: ("NEU", "NEU")}
    assert "higher display 56589065 takes the UP" in events(w)[0]


def test_co_completion_equal_displays_both_neu(tmp_path):
    refs = [fref(E, T(4, 31), 0.95438, lag=0), fref(A, T(4, 31), 0.95437, date="2026-09-26 21:17:47", lag=0)]
    w, *_ = make(tmp_path, refs, hard_cap=T(5, 0))
    w.run()
    assert verdicts(w) == {E: ("NEU", "NEU"), A: ("NEU", "NEU")}
    assert "UP test PASS" in events(w)[0] and "non-attributable" in events(w)[0]


def test_no_move_is_neu_and_low_display_is_neg(tmp_path):
    refs = [fref(E, T(4, 31), 0.95430, lag=0), fref(A, T(4, 51), 0.95290, date="2026-09-26 21:17:47", lag=0)]
    w, *_ = make(tmp_path, refs, hard_cap=T(5, 30))
    w.run()
    assert verdicts(w) == {E: ("NEU", "NEU"), A: ("NEG", "NEG")}
    assert all("UP test FAIL" in ev for ev in events(w))


def test_stale_three_times_is_ambiguous_and_carried(tmp_path):
    refs = [fref(E, T(4, 31), 0.95438, lag=5000),                           # LB shows it only at ~05:54
            fref(A, T(6, 0), 0.95445, date="2026-09-26 21:17:47", lag=0)]
    w, cli, clock, _ = make(tmp_path, refs, hard_cap=T(6, 30))
    assert w.run() == 0
    ev1, ev2 = events(w)
    assert "STALE after 4 download(s)" in ev1 and "S1 stale after 4 download(s)" in ev1
    lb_times = [t for t, a in cli.log if a == "leaderboard"]
    assert len(lb_times) == 1 + 4 + 1                                       # S0, 1 + 3 re-downloads, event 2
    assert all((b - a).total_seconds() >= 120 for a, b in zip(lb_times[1:5], lb_times[2:5]))
    assert "S0 20260927T041000Z -> S1" in ev2 and "(carried)" in ev2      # S0 stayed the pre-ladder one
    assert "co-completion of 2: the higher display" not in ev2              # equal displays 0.954 -> NEU
    assert verdicts(w) == {E: ("AMBIGUOUS", "NEU"), A: ("NEU", "NEU")}


def test_carried_ambiguous_ref_keeps_its_verdict_when_it_takes_the_up(tmp_path):
    refs = [fref(E, T(4, 31), 0.95510, lag=5000),                           # 0.955 display, stale window
            fref(A, T(6, 0), 0.95438, date="2026-09-26 21:17:47", lag=0)]
    w, *_ = make(tmp_path, refs, hard_cap=T(6, 30))
    w.run()
    ev2 = events(w)[1]
    assert "the UP goes to 56589025, which stays AMBIGUOUS" in ev2
    assert verdicts(w) == {E: ("AMBIGUOUS", "POS"), A: ("NEU", "NEU")}


def test_error_only_event_one_download_learns_the_count_rule(tmp_path):
    refs = [fref(A, T(4, 31), None, final="ERROR", date="2026-09-26 21:17:47", lag=0),
            fref(E, T(4, 51), 0.95438, lag=0)]
    w, cli, clock, lines = make(tmp_path, refs, hard_cap=T(5, 30), error_counts=True)
    w.run()
    assert verdicts(w) == {A: ("ERROR", "NEU"), E: ("UP", "POS")}           # a COMPLETE next to an ERROR stays attributable
    assert w.state["error_mode"] == "yes" and any("learned: an ERROR increments" in ln for ln in lines)
    ev1, ev2 = events(w)
    assert "fresh after 1 download(s)" in ev1 and "ERROR counted: yes" in ev1
    assert "count 41->42 (+1)" in ev2 and "40 + 1 COMPLETE + 1 ERROR" in ev2


def test_error_not_counted(tmp_path):
    refs = [fref(A, T(4, 31), None, final="ERROR", date="2026-09-26 21:17:47", lag=0),
            fref(E, T(4, 51), 0.95438, lag=0)]
    w, *_ = make(tmp_path, refs, hard_cap=T(5, 30), error_counts=False)
    w.run()
    assert verdicts(w) == {A: ("ERROR", "NEU"), E: ("UP", "POS")}
    assert w.state["error_mode"] is None and "ERROR counted: no" in events(w)[1]


def test_ref_terminal_before_the_first_read_without_s0_is_ambiguous(tmp_path):
    w, cli, *_ = make(tmp_path, [fref(E, T(3, 50), 0.95438, lag=0)], hard_cap=T(4, 30))
    w.run()
    assert verdicts(w) == {E: ("AMBIGUOUS", "NEU")}
    assert "no fresh S0" in events(w)[0]
    assert sum(a == "leaderboard" for _, a in cli.log) == 1                 # no separate baseline download
    assert w.state["s0"]["ours"]["count"] == 41                             # that S1 became the next S0


def test_s0_import_lets_an_early_completion_be_read(tmp_path):
    refs = [fref(E, T(3, 50), 0.95438, lag=0)]
    w, cli, *_ = make(tmp_path, refs, hard_cap=T(4, 30))
    s0 = tmp_path / "timer_0304Z.csv"
    s0.write_text("\ufeff" + cli.lb_csv(T(3, 4)), encoding="utf-8")
    assert w.run(s0_path=s0) == 0
    assert verdicts(w) == {E: ("UP", "POS")}
    assert "S0 S0-timer_0304Z -> S1" in events(w)[0]


def test_s0_import_from_the_e10_snapshot_and_rejects_a_stale_one(tmp_path):
    p = ROOT / "experiments" / "e10_watch" / "20260926T2246Z.txt"
    if not p.exists():
        pytest.skip("no e10 snapshot")
    w, *_ = make(tmp_path, [])
    w.out_dir.mkdir(parents=True)
    assert w.import_s0(p)
    assert w.state["s0"]["folder"] == "S0-20260926T2246Z" and w.state["s0"]["ours"]["rank"] == 229
    assert len(lw.load_lb(w.out_dir / "S0-20260926T2246Z")["above"]) == 228
    bad = tmp_path / "late.csv"
    bad.write_text(lb_text([ours_row(1, count=41)]), encoding="utf-8")
    w2, *_ = make(tmp_path / "b", [])
    w2.out_dir.mkdir(parents=True)
    assert not w2.import_s0(bad) and w2.state["s0"] is None


def test_restart_resumes_from_state_and_recovers_s0_from_folders(tmp_path):
    refs = [fref(E, T(4, 31), 0.95438, lag=0)]
    w, cli, clock, _ = make(tmp_path, refs, hard_cap=T(4, 20))              # stops before the completion
    assert w.run() == 0 and w.state["s0"] is not None
    s0_folder = w.state["s0"]["folder"]
    lines = []
    w2 = lw.Watcher(out_dir=w.out_dir, poll_log=w.poll_log, cli=cli, clock=clock, hard_cap=T(5, 0), echo=lines.append)
    assert w2.run() == 0
    assert "resumed from state.json" in lines[0]
    assert verdicts(w2) == {E: ("UP", "POS")} and f"S0 {s0_folder} -> S1" in events(w2)[0]
    w.state_path.unlink()                                                    # no state: newest fresh folder is S0
    w3 = lw.Watcher(out_dir=w.out_dir, poll_log=w.poll_log, cli=cli, clock=clock, hard_cap=T(5, 30), echo=lines.append)
    assert "recovered from the fresh download" in w3.load_state()
    assert w3.state["s0"]["folder"] != s0_folder and w3.state["last_statuses"][E] == "COMPLETE"


def test_recovery_prefers_the_newest_fresh_download_over_an_imported_s0(tmp_path):
    refs = [fref(E, T(4, 31), 0.95438, lag=0)]
    w, cli, clock, _ = make(tmp_path, refs, start=T(4, 0), hard_cap=T(5, 0))
    s0 = tmp_path / "timer.csv"
    s0.write_text(cli.lb_csv(T(3, 4)), encoding="utf-8")
    assert w.run(s0_path=s0) == 0 and verdicts(w) == {E: ("UP", "POS")}
    newest = w.state["s0"]["folder"]
    assert newest.startswith("2026")                                         # the fresh S1 became S0
    w.state_path.unlink()
    w2 = lw.Watcher(out_dir=w.out_dir, poll_log=w.poll_log, cli=cli, clock=clock, echo=lambda s: None)
    w2.load_state()
    assert w2.state["s0"]["folder"] == newest


def test_hard_cap_stops_with_exit_0(tmp_path):
    w, cli, clock, lines = make(tmp_path, [], start=T(9, 35))
    assert w.run() == 0
    assert clock.now() >= T(9, 40) and "STOP (hard cap reached)" in lines[-1]


def test_main_dry_run_cli(tmp_path, capsys):
    assert lw.main(["--dry-run", "--out-dir", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "EVENT 3" in out and "[dry run]" in out
