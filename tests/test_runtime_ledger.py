"""A5: tools/runtime_ledger.py on synthetic LB poll logs (lb_poll.py format, including empty-output blocks).

    python -m pytest tests/test_runtime_ledger.py -q
"""
import datetime as dt
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import tools.runtime_ledger as rl  # noqa: E402

HEAD = "ref,fileName,date,description,status,publicScore,privateScore"
P34 = ("56545267", "2026-09-25 08:09:00.723000",
       "probe 34: exp56 = anvithpothula/biohub-x138 verbatim on our account (author public 0.953); same docker pin")
P35 = ("56545786", "2026-09-25 08:33:25.043000",
       '"probe 35: exp57b = x138 verbatim (exp56) + DaughterNet v1 division insertion with steal; +12 forks, nodes"')
P32 = ("56534391", "2026-09-25 00:02:05.877000", "probe 32: exp52 = exp51 (exp48 + x138 head) + float output coords")
K2 = ("56560001", "2026-09-26 00:01:30.100000", '"probe 37: exp58 = K2 x138 + safetail + lowrefine + divinsert, C01"')
K1 = ("56560002", "2026-09-26 00:02:10.000000", "probe 38: exp58t = K1 twin lowrefine off")


def row(sub, status, score=""):
    ref, date, desc = sub
    return f"{ref},submission.csv,{date},{desc},SubmissionStatus.{status},{score},"


def block(ts, rows, note=""):
    """lb_poll.py block: header, then the CLI lines (blank line after the header and between rows); rows=None means
    EMPTY CLI output (the header is followed by one empty line)."""
    lines = [f"=== {ts}{note}"]
    if rows is None:
        lines.append("")
    else:
        lines.append(HEAD)
        for r in rows:
            lines += ["", r]
        lines.append("")
    return "\n".join(lines) + "\n"


def ledger(text, **kw):
    rep = rl.build(rl.parse_log(text), **kw)
    return rep, {e["ref"]: e for e in rep["entries"]}


def trig(rep, tid):
    return [t for t in rep["triggers"] if t["id"] == tid]


# the real 25 Sep sequence (CONTEXT 14:37 / 16:20 UTC): #34 and #35 bounds, five empty polls before #35's score
LOG_2509 = (
    block("2026-09-25T14:16:14Z", [row(P35, "PENDING"), row(P34, "PENDING"), row(P32, "COMPLETE", "0.950")])
    + block("2026-09-25T14:26:33Z", [row(P35, "PENDING"), row(P34, "PENDING"), row(P32, "COMPLETE", "0.950")])
    + block("2026-09-25T14:36:36Z", [row(P35, "PENDING"), row(P34, "COMPLETE", "0.953"), row(P32, "COMPLETE", "0.950")])
    + block("2026-09-25T15:16:44Z", [row(P35, "PENDING"), row(P34, "COMPLETE", "0.953")])
    + "".join(block(f"2026-09-25T{h}Z", None) for h in ("15:26:45", "15:36:49", "15:46:51", "15:56:53", "16:06:54"))
    + block("2026-09-25T16:16:55Z", [row(P35, "COMPLETE", "0.954"), row(P34, "COMPLETE", "0.953")])
)


def test_parse_blocks_and_empty_output():
    polls = rl.parse_log(LOG_2509)
    assert len(polls) == 10
    assert [p.empty for p in polls].count(True) == 5
    assert polls[0].rows["56545786"]["description"].startswith("probe 35: exp57b")   # quoted comma kept
    assert rl.norm_status(polls[-1].rows["56545786"]["status"]) == "COMPLETE"


def test_real_sequence_bounds_and_r5():
    rep, e = ledger(LOG_2509)
    p34, p35, p32 = e["56545267"], e["56545786"], e["56534391"]
    # #34: (6.29, 6.46] -> R5(a) admitted under the 7.5 h x138 deadline
    assert (rl.fmt_lo(p34["lo_h"]), rl.fmt_hi(p34["hi_h"])) == ("6.29", "6.46")
    assert p34["family"] == "x138" and p34["r5"][0] == "ADMIT"
    assert p34["first_result"] == rl.parse_ts("2026-09-25T14:36:36Z") and p34["result_score"] == "0.953"
    assert p34["empty_between"] == [] and p34["invisible_between"] == []
    # #35: (6.72, 7.73] with the five empty polls noted -> R5(a) unproven, ungated insertion
    assert (rl.fmt_lo(p35["lo_h"]), rl.fmt_hi(p35["hi_h"])) == ("6.72", "7.73")
    assert len(p35["empty_between"]) == 5
    assert p35["family"] == "x138_ungated" and p35["r5"][0] == "UNPROVEN" and "no R5(b)" in p35["r5"][1]
    # exp52: no PENDING ever seen, no lower bound, always admissible
    assert p32["lo_h"] is None and p32["family"] == "notimer" and p32["r5"][0] == "ADMIT"
    assert trig(rep, "A5-L(K2)")[0]["state"] == "WATCH"          # no K2 yet
    md = rl.render_md(rep)
    assert "(6.72, 7.73]" in md and "empty at 15:26, 15:36, 15:46, 15:56, 16:06" in md


def _k2_log(k2_rows):
    """k2_rows: list of (ts, status or None for an empty poll, score)."""
    out = ""
    for ts, st, score in k2_rows:
        out += block(ts, None if st is None else [row(K2, st, score), row(K1, "PENDING")])
    return out


def test_k2_complete_by_8h_clears_trigger():
    text = _k2_log([("2026-09-26T07:51:00Z", "PENDING", ""), ("2026-09-26T08:01:00Z", "COMPLETE", "0.954")])
    rep, e = ledger(text)
    k2 = e["56560001"]
    assert k2["family"] == "safetail" and k2["r5"][0] == "ADMIT"
    assert k2["hi_h"] < 8.0 and "did NOT fire" in k2["divins_gate"]
    t = trig(rep, "A5-L(K2)")[0]
    assert t["state"] == "CLEAR" and "56560001" in t["text"]
    assert not trig(rep, "A6")


def test_k2_pending_past_8h_fires():
    text = _k2_log([("2026-09-26T07:55:00Z", "PENDING", ""), ("2026-09-26T08:05:00Z", "PENDING", "")])
    rep, e = ledger(text)
    t = trig(rep, "A5-L(K2)")[0]
    assert t["state"] == "FIRED" and "BOTH deadlines to 32400/37800" in t["text"] and "never DIVINS alone" in t["text"]
    assert e["56560001"]["r5"][0] == "PENDING"
    assert "MAY have fired" in e["56560001"]["divins_gate"]


def test_k2_pending_before_8h_is_watch_with_keepalive():
    rep, _ = ledger(_k2_log([("2026-09-26T07:00:00Z", "PENDING", "")]))
    t = trig(rep, "A5-L(K2)")[0]
    assert t["state"] == "WATCH" and "Keep the poller alive until 2026-09-26 08:31:30Z" in t["text"]


def test_k2_empty_polls_straddling_8h_is_possible():
    text = _k2_log([("2026-09-26T07:41:00Z", "PENDING", ""), ("2026-09-26T07:51:00Z", None, ""),
                    ("2026-09-26T08:01:00Z", None, ""), ("2026-09-26T08:11:00Z", None, ""),
                    ("2026-09-26T08:21:00Z", "COMPLETE", "0.954")])
    rep, e = ledger(text)
    k2 = e["56560001"]
    assert len(k2["empty_between"]) == 3 and k2["lo_h"] < 8.0 < k2["hi_h"]
    assert k2["r5"][0] == "ADMIT"                                  # still <= 9.5 h
    assert "UNPROVEN" in k2["divins_gate"]
    t = trig(rep, "A5-L(K2)")[0]
    assert t["state"] == "POSSIBLE" and "3 empty" in t["text"]
    win = trig(rep, "A5-poller-window")[0]
    assert "3 empty" in win["text"]


def test_k2_error_fires_a6_and_r5_no():
    rep, e = ledger(_k2_log([("2026-09-26T03:00:00Z", "PENDING", ""), ("2026-09-26T03:10:00Z", "ERROR", "")]))
    assert e["56560001"]["result_status"] == "ERROR" and e["56560001"]["r5"][0] == "NO"
    a6 = trig(rep, "A6")[0]
    assert a6["state"] == "FIRED" and "exp58t" in a6["text"]


def test_k2_over_9_5h_fails_r5a():
    text = _k2_log([("2026-09-26T09:40:00Z", "PENDING", ""), ("2026-09-26T09:50:00Z", "COMPLETE", "0.954")])
    rep, e = ledger(text)
    assert e["56560001"]["r5"][0] == "NO" and "R5(b)" in e["56560001"]["r5"][1]
    assert trig(rep, "A5-L(K2)")[0]["state"] == "FIRED"
    assert trig(rep, "A6")[0]["state"] == "FIRED"


def test_retry_note_widens_upper_bound_and_counts_empty_error_polls():
    note = " [empty stdout, rc=1, stderr=''] [ERROR timed out]"
    text = (block("2026-09-26T07:40:00Z", [row(K2, "PENDING")])
            + block("2026-09-26T07:50:00Z", None, note)                 # all attempts failed: empty poll
            + block("2026-09-26T07:57:00Z", [row(K2, "COMPLETE", "0.955")], " [empty stdout, rc=0, stderr='']"))
    rep, e = ledger(text)
    k2 = e["56560001"]
    polls = rep["polls"]
    assert polls[1].empty and polls[1].failed_attempts == 2 and polls[2].failed_attempts == 1
    assert k2["first_result_upper"] == rl.parse_ts("2026-09-26T07:57:00Z") + dt.timedelta(seconds=rl.RETRY_SLACK_S)
    assert k2["retried_result"] == 1 and len(k2["empty_between"]) == 1
    # 07:57 + 210 s = 08:00:30 is before the 8.0 h mark 08:01:30 -> clear
    assert trig(rep, "A5-L(K2)")[0]["state"] == "CLEAR"
    assert "(+1 failed attempts)" in rl.render_md(rep)


def test_row_scrolled_out_of_the_window_counts_as_not_visible():
    text = (block("2026-09-26T05:00:00Z", [row(K1, "PENDING")])
            + block("2026-09-26T05:10:00Z", [row(K2, "PENDING"), row(K1, "PENDING")])
            + block("2026-09-26T05:20:00Z", [row(K2, "PENDING")])         # K1 cut by the 12-line window
            + block("2026-09-26T05:30:00Z", [row(K2, "PENDING"), row(K1, "COMPLETE", "0.954")]))
    _, e = ledger(text)
    k1 = e["56560002"]
    assert k1["invisible_between"] == [rl.parse_ts("2026-09-26T05:20:00Z")]
    assert k1["last_pending"] == rl.parse_ts("2026-09-26T05:10:00Z")
    assert k1["family"] == "safetail"


def test_families_and_overrides():
    assert rl.family_of("1", "exp58n", {}) == "safetail_noins"
    assert rl.family_of("1", "exp58p", {}) == "safetail_noins"
    assert rl.family_of("1", "exp59dc", {}) == "safetail"
    assert rl.family_of("1", "exp57", {}) == "x138_ungated"
    assert rl.family_of("1", "exp51", {}) == "notimer"
    assert rl.family_of("1", "exp53", {}) == "unknown"
    assert rl.family_of("1", "exp63", {"exp63": "safetail"}) == "safetail"
    assert rl.family_of("777", "exp58", {"777": "x138"}) == "x138"
    assert rl.exp_token('"P36 exp57 v1 DIAGNOSTIC (x138+leafprune0.3)"') == "exp57"


def test_exp_token_underscore_and_dash_build_names():
    assert rl.exp_token("probe 37: exp58_x138_safe_lowref = K2") == "exp58"
    assert rl.exp_token("probe 37: exp58n_x138_safe_lowref = K2 no insertion") == "exp58n"
    assert rl.exp_token("vitaliineibauer/biohub-exp58t-x138-safe v1") == "exp58t"
    assert rl.exp_token("EXP58_x138") == "exp58"
    assert rl.exp_token("myexp58 exp58abc1 x") == ""          # embedded / digit-tailed tokens are not builds
    assert rl.family_of("1", rl.exp_token("exp58_x138_safe_lowref"), {}) == "safetail"
    assert rl.family_of("1", rl.exp_token("exp58n_x138_safe_lowref"), {}) == "safetail_noins"


K2U = ("56560003", "2026-09-26 00:01:30.100000", "probe 37: exp58_x138_safe_lowref = K2 x138 + safetail + lowrefine")
K2N = ("56560004", "2026-09-26 00:55:00.000000", "probe 37: exp58n_x138_safe_lowref = K2 (no insertion)")


def test_k2_underscore_build_name_fires():
    # the review scenario: PENDING until 08:35Z, COMPLETE at 09:05Z -> L in (8.55, 9.06] -> FIRED, not WATCH
    text = (block("2026-09-26T08:35:00Z", [row(K2U, "PENDING")])
            + block("2026-09-26T09:05:00Z", [row(K2U, "COMPLETE", "0.954")]))
    rep, e = ledger(text)
    k2 = e["56560003"]
    assert k2["exp"] == "exp58" and k2["family"] == "safetail" and k2["r5"][0] == "ADMIT"
    t = trig(rep, "A5-L(K2)")[0]
    assert t["state"] == "FIRED" and "56560003" in t["text"] and "BOTH deadlines to 32400/37800" in t["text"]
    assert not trig(rep, "family")


def test_k2_falls_back_to_exp58n_and_prefers_exp58():
    text = block("2026-09-26T09:00:00Z", [row(K2N, "PENDING")])
    rep, e = ledger(text)
    assert e["56560004"]["family"] == "safetail_noins"
    t = trig(rep, "A5-L(K2)")[0]
    assert t["state"] == "FIRED" and "(exp58n)" in t["text"]
    rep, _ = ledger(block("2026-09-26T09:00:00Z", [row(K2N, "PENDING"), row(K2U, "PENDING")]))
    assert "56560003" in trig(rep, "A5-L(K2)")[0]["text"]


def test_unknown_family_after_1800z_is_loud():
    unk = ("56560005", "2026-09-25 23:00:00.000000", "probe 36: K build without a token")
    old = ("56560006", "2026-09-25 07:00:00.000000", "probe 33: exp53 = something")
    rep, e = ledger(block("2026-09-26T01:00:00Z", [row(unk, "PENDING"), row(old, "COMPLETE", "0.95")]))
    assert e["56560005"]["family"] == "unknown" and e["56560006"]["family"] == "unknown"
    w = trig(rep, "family")
    assert len(w) == 1 and w[0]["state"] == "WATCH" and "56560005" in w[0]["text"] and "--family 56560005=" in w[0]["text"]
    rep, _ = ledger(block("2026-09-26T01:00:00Z", [row(unk, "PENDING")]), overrides={"56560005": "safetail"})
    assert not trig(rep, "family")


def test_forecast_trigger():
    rep, _ = ledger(LOG_2509, forecast_h=7.95)
    assert trig(rep, "A5-F")[0]["state"] == "FIRED"
    rep, _ = ledger(LOG_2509, forecast_h=7.8)
    assert trig(rep, "A5-F")[0]["state"] == "CLEAR"
    rep, _ = ledger(LOG_2509)
    assert trig(rep, "A5-F")[0]["state"] == "INFO"


def test_stale_poller_and_gaps():
    text = block("2026-09-26T01:00:00Z", [row(K2, "PENDING")]) + block("2026-09-26T03:00:00Z", [row(K2, "PENDING")])
    rep, _ = ledger(text, now=rl.parse_ts("2026-09-26T04:00:00Z"))
    assert rep["gaps"] == [(rl.parse_ts("2026-09-26T01:00:00Z"), rl.parse_ts("2026-09-26T03:00:00Z"))]
    assert trig(rep, "poller")[0]["state"] == "WATCH"
    rep, _ = ledger(text, now=rl.parse_ts("2026-09-26T03:05:00Z"))
    assert not trig(rep, "poller")


def test_main_writes_ledger_and_json(tmp_path, capsys):
    log = tmp_path / "poll.log"
    log.write_text(LOG_2509 + _k2_log([("2026-09-26T08:05:00Z", "PENDING", "")]), encoding="utf-8")
    out, js = tmp_path / "ledger.md", tmp_path / "ledger.json"
    rc = rl.main(["--log", str(log), "--out", str(out), "--json", str(js), "--now", "2026-09-26T08:06:00Z",
                  "--family", "exp53=notimer"])
    assert rc == 0
    md = out.read_text(encoding="utf-8")
    assert md.startswith("# LB runtime ledger (A5)") and "**FIRED** `A5-L(K2)`" in md
    d = json.loads(js.read_text(encoding="utf-8"))
    assert d["n_empty"] == 5 and d["now"] == "2026-09-26 08:06:00Z"
    assert {x["ref"] for x in d["entries"]} == {"56545267", "56545786", "56534391", "56560001", "56560002"}
    assert "FIRED A5-L(K2)" in capsys.readouterr().out


def test_main_missing_log(tmp_path):
    assert rl.main(["--log", str(tmp_path / "nope.log"), "--out", str(tmp_path / "l.md")]) == 2


def test_empty_log():
    rep = rl.build(rl.parse_log(""))
    assert rep["entries"] == [] and "No polls" in rl.render_md(rep)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
