"""A5 runtime ledger (research/wf_ideas_v4/FINAL_REPORT_v4.md amendment 5, final.json 'A5-runtime-ledger-and-triggers').

Pure file processing: reads the LB poll log written by experiments/lb_poll/lb_poll.py (one block per poll:
'=== <UTC ts>[ notes]' followed by the first lines of `kaggle competitions submissions -v` CSV output; a block with no
rows is an EMPTY poll) and rewrites experiments/lb_poll/ledger.md. No Kaggle calls. Report only: nothing here FAILs.

Per submission: first-seen time of a score or an error, latency bounds (last PENDING seen, first COMPLETE/ERROR seen,
with the empty polls and the polls where the row was not visible in between), R5(a) admission against the deadline of
its build family, and the A5 triggers (K2 latency > 8.0 h -> the deadline-move / D4 OK question; forecast F > 7.9 h;
the A6 K2-error contingency).

Conventions (the same as CONTEXT.md 25 Sep 14:37 / 16:20 UTC):
  - latency L = observation time - submission 'date' column (UTC); runtime <= L;
  - lower bound = last poll that showed PENDING (the header timestamp; the real query ran at or after it, so this is
    conservative); upper bound = the header timestamp of the first poll that showed COMPLETE/ERROR, plus
    RETRY_SLACK_S per failed CLI attempt noted in that header (the retrying poller writes the timestamp before its
    attempts);
  - no PENDING ever seen -> no lower bound; R5(a) needs the upper bound <= the family deadline, R5 says latency counts
    only from our own polls, so a result first seen after a long gap proves nothing.

    python tools/runtime_ledger.py                              # experiments/lb_poll/poll.log -> ledger.md
    python tools/runtime_ledger.py --forecast-h 7.7 --json experiments/lb_poll/ledger.json
    python tools/runtime_ledger.py --family 56555189=x138_ungated --k2 56560000
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG = ROOT / "experiments" / "lb_poll" / "poll.log"
DEFAULT_OUT = ROOT / "experiments" / "lb_poll" / "ledger.md"

DEFAULT_COLUMNS = ["ref", "fileName", "date", "description", "status", "publicScore", "privateScore"]
RETRY_SLACK_S = 210            # lb_poll.py: one failed attempt = <= 180 s timeout + 30 s sleep
GAP_WARN_S = 15 * 60           # the poller runs every ~10 min
K2_TOKEN = "exp58"             # K2 = exp58 (FINAL_REPORT v3 §e build names)
K2_ALT_TOKENS = ("exp58n",)    # K2 without insertion (branch C / R2 'exp58n_...'): used only when no exp58 is in the log
UNKNOWN_WATCH_AFTER = dt.datetime(2026, 9, 25, 18, 0, tzinfo=dt.timezone.utc)   # K-build era: unknown family is loud
K1_NOTE = "K1 = exp58t (vitaliineibauer/biohub-exp58t-x138-safe v1, already gated: sha256 == exp57b dummy)"
DIVINS_GATE_H = 8.0            # DIVINS_DEADLINE_S = 28800
K2PP_DIVINS_GATE_H = 9.0       # K2'' exp58d: DIVINS_DEADLINE_S = 32400 (REPAIR_DEADLINE_S = 37800 = 10.5 h)
A5_L_TRIGGER_H = 8.0           # A5: L(K2) > 8.0 h
A5_F_TRIGGER_H = 7.9           # A5: forecast F > 7.9 h
K2_WATCH_H = (7.0, 8.5)        # A5: keep the poller alive 07:00-08:30 UTC for K2 at 00:01 UTC

# family -> R5 deadline (h), insertion gate (h), ungated insertion (R5(b) not available at L > 7.5 h), label
FAMILIES = {
    "x138": dict(deadline_h=7.5, divins_h=None, ungated=False, label="x138 type, REPAIR_DEADLINE 7.5 h"),
    "x138_ungated": dict(deadline_h=7.5, divins_h=None, ungated=True,
                         label="x138 + ungated insertion (#35/exp57), 7.5 h, no R5(b)"),
    "safetail_ci": dict(deadline_h=10.75, divins_h=10.2, ungated=False, label="safetail + coordinject: admit L_hi <= 10.75 h; insertion gate read on L_hi - CI_lo 2.2 h ('did NOT fire' iff L_hi <= 10.2 h)"),
    "safetail": dict(deadline_h=9.5, divins_h=DIVINS_GATE_H, ungated=False,
                     label="safetail (C01) + gated insertion, 9.5 h (insertion gate 8.0 h)"),
    "safetail_noins": dict(deadline_h=9.5, divins_h=None, ungated=False, label="safetail (C01), no insertion, 9.5 h"),
    "safetail_late": dict(deadline_h=10.5, divins_h=K2PP_DIVINS_GATE_H, ungated=False,
                          label="K2'' exp58d: safetail (C01) + gated insertion, both deadlines moved, 10.5 h "
                                "(insertion gate 9.0 h)"),
    "notimer": dict(deadline_h=None, divins_h=None, ungated=False, label="exp51/exp52, no timer: always admissible"),
    "unknown": dict(deadline_h=None, divins_h=None, ungated=False, label="family unknown (pass --family)"),
}
# first 'exp<N><suffix>' token of the description -> family (first match wins); --family overrides
EXP_RULES = [
    (r"exp56", "x138"),
    (r"exp63[a-z]*", "x138"),             # E10 successor port (CONTEXT 26 Sep P4b): x138 type, 7.5 h, never safetail
    (r"exp57[a-z]*", "x138_ungated"),
    (r"exp58(n|p)[a-z]*", "safetail_noins"),
    (r"exp58d", "safetail_late"),          # K2'' (CONTEXT 26 Sep v3 V3): REPAIR 37800 / DIVINS 32400
    (r"exp(58|59|61|62)[a-z]*", "safetail"),
    (r"exp75[a-z]*", "safetail_ci"),          # coordinject stacks (CONTEXT 27 Sep round 20 R20-A4)
    (r"exp76[acfhi]", "safetail_ci"),
    (r"exp79a[a-z]*", "safetail_ci"),
    (r"exp7[2-9][a-z]*", "safetail"),         # 28 Sep public rungs (K2 family)
    (r"exp8\d[a-z]*", "safetail"),
    (r"exp70[a-z]*", "safetail"),             # K2 public ladder (CONTEXT 26 Sep 20:49 UTC): K2 + knobs, REPAIR 34200 / DIVINS 28800
    (r"exp5[12]", "notimer"),
]
# '_' and '-' are separators: build names are exp58_x138_safe_lowref / exp58n_x138_safe_lowref / biohub-exp58t-x138-safe
EXP_TOKEN = re.compile(r"(?<![A-Za-z0-9])(exp\d+[a-z]*)(?![a-z0-9])", re.IGNORECASE)
HEADER = re.compile(r"^=== (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)(.*)$")
RESULT_STATES = ("COMPLETE", "ERROR")


# ------------------------------------------------------------------------------------------------ parsing
@dataclass
class Poll:
    ts: dt.datetime
    note: str = ""
    rows: dict = field(default_factory=dict)      # ref -> row dict
    bad_rows: int = 0

    @property
    def empty(self) -> bool:
        return not self.rows

    @property
    def failed_attempts(self) -> int:
        return self.note.count("[empty stdout") + self.note.count("[ERROR")


def parse_ts(s: str) -> dt.datetime:
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def parse_submit_date(s: str) -> dt.datetime | None:
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return dt.datetime.strptime(s, fmt).replace(tzinfo=dt.timezone.utc)
        except ValueError:
            pass
    return None


def norm_status(s: str) -> str:
    return s.strip().split(".")[-1].upper()


def parse_log(text: str) -> list[Poll]:
    polls: list[Poll] = []
    cols = list(DEFAULT_COLUMNS)
    for line in text.splitlines():
        m = HEADER.match(line)
        if m:
            polls.append(Poll(parse_ts(m.group(1)), m.group(2).strip()))
            cols = list(DEFAULT_COLUMNS)
            continue
        if not polls or not line.strip():
            continue
        if line.startswith("ref,"):
            cols = next(csv.reader([line]))
            continue
        if not re.match(r"^\d+,", line):
            continue
        vals = next(csv.reader([line]))
        if len(vals) != len(cols):
            polls[-1].bad_rows += 1
            continue
        row = dict(zip(cols, vals))
        polls[-1].rows[row["ref"]] = row
    polls.sort(key=lambda p: p.ts)
    return polls


# ------------------------------------------------------------------------------------------------ per submission
def exp_token(desc: str) -> str:
    m = EXP_TOKEN.search(desc or "")
    return m.group(1).lower() if m else ""


def family_of(ref: str, token: str, overrides: dict) -> str:
    if ref in overrides:
        return overrides[ref]
    if token and token in overrides:
        return overrides[token]
    for pat, fam in EXP_RULES:
        if token and re.fullmatch(pat, token):
            return fam
    return "unknown"


def hours(a: dt.datetime, b: dt.datetime) -> float:
    return (a - b).total_seconds() / 3600.0


def fmt_ts(t: dt.datetime | None) -> str:
    return t.strftime("%Y-%m-%d %H:%M:%SZ") if t else "-"


def fmt_lo(h: float | None) -> str:
    return "?" if h is None else f"{math.floor(h * 100) / 100:.2f}"


def fmt_hi(h: float | None) -> str:
    return "?" if h is None else f"{math.ceil(h * 100) / 100:.2f}"


def ledger_entry(ref: str, polls: list[Poll], overrides: dict) -> dict:
    seen = [p for p in polls if ref in p.rows]
    last_row = seen[-1].rows[ref]
    desc = last_row.get("description", "")
    submitted = parse_submit_date(last_row.get("date", ""))
    token = exp_token(desc)
    fam = family_of(ref, token, overrides)
    e = dict(ref=ref, description=desc, exp=token, family=fam, submitted=submitted,
             status=norm_status(last_row.get("status", "")), public=last_row.get("publicScore", ""),
             first_seen=seen[0].ts, last_pending=None, first_result=None, first_result_upper=None,
             result_status=None, result_score=None, empty_between=[], invisible_between=[], retried_result=0)
    after = [p for p in polls if submitted is None or p.ts >= submitted]
    empties, invisible = [], []
    for p in after:
        row = p.rows.get(ref)
        if row is None:
            (empties if p.empty else invisible).append(p.ts)
            continue
        st = norm_status(row.get("status", ""))
        if st in RESULT_STATES:
            e["first_result"] = p.ts
            e["first_result_upper"] = p.ts + dt.timedelta(seconds=RETRY_SLACK_S * p.failed_attempts)
            e["retried_result"] = p.failed_attempts
            e["result_status"] = st
            e["result_score"] = row.get("publicScore", "")
            break
        e["last_pending"] = p.ts
        empties, invisible = [], []
    else:
        empties, invisible = [], []      # still pending: nothing is "between" yet
    lo_from = e["last_pending"]
    e["empty_between"] = [t for t in empties if lo_from is None or t > lo_from]
    e["invisible_between"] = [t for t in invisible if lo_from is None or t > lo_from]
    if submitted is not None:
        e["lo_h"] = hours(e["last_pending"], submitted) if e["last_pending"] else None
        e["hi_h"] = hours(e["first_result_upper"], submitted) if e["first_result_upper"] else None
    else:
        e["lo_h"] = e["hi_h"] = None
    e["r5"] = r5_admission(e)
    e["divins_gate"] = divins_gate(e)
    return e


def r5_admission(e: dict) -> tuple[str, str]:
    """(code, text). code in ADMIT, NO, UNPROVEN, PENDING, NA."""
    fam = FAMILIES[e["family"]]
    st = e["result_status"]
    if st == "ERROR":
        return "NO", "NO: scored with ERROR"
    if e["family"] == "unknown":
        return "NA", "n/a: family unknown"
    if fam["deadline_h"] is None:
        return ("ADMIT", "ADMIT: no timer (exp51/exp52 always)") if st == "COMPLETE" else ("PENDING", "pending")
    d = fam["deadline_h"]
    lo, hi = e.get("lo_h"), e.get("hi_h")
    no_b = " (ungated insertion: no R5(b))" if fam["ungated"] else "; only R5(b) (step-0 margin >= 1 h) can admit"
    if st is None:
        if lo is not None and lo > d:
            return "NO", f"(a) FAILS already: pending at {fmt_lo(lo)} h > {d} h{no_b}"
        return "PENDING", f"pending (deadline {d} h)"
    if hi is not None and hi <= d:
        return "ADMIT", f"ADMIT (a): L <= {fmt_hi(hi)} h <= {d} h"
    if lo is not None and lo > d:
        return "NO", f"(a) FAILS: L > {fmt_lo(lo)} h > {d} h{no_b}"
    return "UNPROVEN", f"(a) UNPROVEN: L in ({fmt_lo(lo)}, {fmt_hi(hi)}] vs {d} h{no_b}"


def divins_gate(e: dict) -> str:
    g = FAMILIES[e["family"]]["divins_h"]
    if g is None:
        return ""
    lo, hi = e.get("lo_h"), e.get("hi_h")
    if e["result_status"] == "COMPLETE" and hi is not None and hi <= g:
        return f"insertion gate {g} h did NOT fire (L <= {fmt_hi(hi)} h)"
    if lo is not None and lo > g:
        return f"L > {g} h: the insertion gate MAY have fired"
    if e["result_status"] is None:
        return f"insertion gate {g} h: open"
    return f"insertion gate {g} h: UNPROVEN"


# ------------------------------------------------------------------------------------------------ A5 triggers
def pick_k2(entries: list[dict], k2_ref: str | None) -> dict | None:
    if k2_ref:
        return next((e for e in entries if e["ref"] == k2_ref), None)
    cands = [e for e in entries if e["exp"] == K2_TOKEN]
    if not cands:
        cands = [e for e in entries if e["exp"] in K2_ALT_TOKENS]
    return max(cands, key=lambda e: e["submitted"] or e["first_seen"]) if cands else None


def a5_triggers(entries: list[dict], polls: list[Poll], k2_ref: str | None, forecast_h: float | None,
                now: dt.datetime | None = None) -> list[dict]:
    """List of {id, state, text}; state in FIRED, POSSIBLE, CLEAR, WATCH, INFO."""
    out = []
    if now is not None and polls and (now - polls[-1].ts).total_seconds() > GAP_WARN_S:
        out.append(dict(id="poller", state="WATCH",
                        text=f"last poll {fmt_ts(polls[-1].ts)} is {(now - polls[-1].ts).total_seconds() / 60:.0f} "
                             f"min before {fmt_ts(now)}: is experiments/lb_poll/lb_poll.py still running?"))
    for e in entries:
        if e["family"] == "unknown" and (e["submitted"] or e["first_seen"]) >= UNKNOWN_WATCH_AFTER:
            out.append(dict(id="family", state="WATCH",
                            text=f"ref {e['ref']} (submitted {fmt_ts(e['submitted'])}, token {e['exp'] or '-'}) has "
                                 f"family unknown: R5(a) and the insertion gate are NOT evaluated. If it is a K build "
                                 f"pass --family {e['ref']}=FAMILY (and --k2 {e['ref']} if it is K2). "
                                 f"Description: {e['description'][:100]}"))
    k2 = pick_k2(entries, k2_ref)
    if k2 is None:
        out.append(dict(id="A5-L(K2)", state="WATCH", text=f"K2 ({K2_TOKEN}) not in the poll log yet."))
    else:
        lo, hi, sub = k2.get("lo_h"), k2.get("hi_h"), k2["submitted"]
        mark = sub + dt.timedelta(hours=A5_L_TRIGGER_H) if sub else None
        ask = ("-> ask the user's OK: (a) D4 exact two-stage scoring behind DIVINS_TWOSTAGE (sha256 == K2 dummy) "
               "and/or (b) move BOTH deadlines to 32400/37800 (never DIVINS alone).")
        head = f"K2 = ref {k2['ref']} ({k2['exp']}), submitted {fmt_ts(sub)}, 8.0 h mark {fmt_ts(mark)}"
        if lo is not None and lo > A5_L_TRIGGER_H:
            out.append(dict(id="A5-L(K2)", state="FIRED",
                            text=f"{head}: L(K2) > {fmt_lo(lo)} h > {A5_L_TRIGGER_H} h {ask}"))
        elif k2["result_status"] is None:
            last = polls[-1].ts if polls else None
            end = sub + dt.timedelta(hours=K2_WATCH_H[1]) if sub else None
            keep = f" Keep the poller alive until {fmt_ts(end)}." if end and (last is None or last < end) else ""
            out.append(dict(id="A5-L(K2)", state="WATCH",
                            text=f"{head}: still PENDING (L > {fmt_lo(lo)} h so far).{keep}"))
        elif hi is not None and hi <= A5_L_TRIGGER_H:
            out.append(dict(id="A5-L(K2)", state="CLEAR",
                            text=f"{head}: {k2['result_status']} seen by {fmt_ts(k2['first_result_upper'])}, "
                                 f"L(K2) <= {fmt_hi(hi)} h <= {A5_L_TRIGGER_H} h (the 8.0 h insertion gate did not "
                                 f"fire)."))
        else:
            out.append(dict(id="A5-L(K2)", state="POSSIBLE",
                            text=f"{head}: L(K2) in ({fmt_lo(lo)}, {fmt_hi(hi)}] h straddles {A5_L_TRIGGER_H} h "
                                 f"({len(k2['empty_between'])} empty / {len(k2['invisible_between'])} not-visible "
                                 f"polls in between); L > 8.0 h is not excluded {ask}"))
        if sub:
            w0, w1 = sub + dt.timedelta(hours=K2_WATCH_H[0]), sub + dt.timedelta(hours=K2_WATCH_H[1])
            inwin = [p for p in polls if w0 <= p.ts <= w1]
            out.append(dict(id="A5-poller-window", state="INFO",
                            text=f"K2 watch window {fmt_ts(w0)} - {fmt_ts(w1)}: {len(inwin)} polls "
                                 f"({sum(p.empty for p in inwin)} empty)."))
        # A6 contingency (needs OK): K2 error, or L > 9.5 h and R5(a) fails
        if k2["result_status"] == "ERROR":
            out.append(dict(id="A6", state="FIRED",
                            text=f"K2 scored with ERROR (first seen {fmt_ts(k2['first_result'])}) -> A6 [needs OK]: "
                                 f"{K1_NOTE} in the next free 26 Sep slot; rebase K3 on K1."))
        elif k2["r5"][0] == "NO":
            out.append(dict(id="A6", state="FIRED",
                            text=f"K2 R5(a) fails ({k2['r5'][1]}) -> A6 [needs OK] if R5(b) also fails: {K1_NOTE} "
                                 f"in the next free slot; rebase K3 on K1."))
        elif k2["r5"][0] == "UNPROVEN":
            out.append(dict(id="A6", state="POSSIBLE",
                            text=f"K2 {k2['r5'][1]} -> check R5(b); if it fails, A6 [needs OK] ({K1_NOTE})."))
    if forecast_h is None:
        out.append(dict(id="A5-F", state="INFO",
                        text=f"Forecast F not supplied (--forecast-h; from the dummy_gates ledger); trigger F > "
                             f"{A5_F_TRIGGER_H} h not evaluated."))
    elif forecast_h > A5_F_TRIGGER_H:
        out.append(dict(id="A5-F", state="FIRED",
                        text=f"F = {forecast_h:.2f} h > {A5_F_TRIGGER_H} h -> ask the user's OK: D4 and/or move BOTH "
                             f"deadlines to 32400/37800 (never DIVINS alone)."))
    else:
        out.append(dict(id="A5-F", state="CLEAR", text=f"F = {forecast_h:.2f} h <= {A5_F_TRIGGER_H} h."))
    return out


# ------------------------------------------------------------------------------------------------ report
def build(polls: list[Poll], overrides: dict | None = None, k2_ref: str | None = None,
          forecast_h: float | None = None, now: dt.datetime | None = None) -> dict:
    overrides = overrides or {}
    refs = {r for p in polls for r in p.rows}
    entries = [ledger_entry(r, polls, overrides) for r in refs]
    entries.sort(key=lambda e: (e["submitted"] or e["first_seen"], e["ref"]), reverse=True)
    gaps = [(a.ts, b.ts) for a, b in zip(polls, polls[1:]) if (b.ts - a.ts).total_seconds() > GAP_WARN_S]
    return dict(polls=polls, entries=entries, gaps=gaps, triggers=a5_triggers(entries, polls, k2_ref, forecast_h, now), now=now)


def _cell(s: str) -> str:
    return str(s).replace("|", "/").replace("\n", " ")


def _hm(ts_list: list[dt.datetime]) -> str:
    return ", ".join(t.strftime("%H:%M") for t in ts_list)


def render_md(rep: dict, log_name: str = "poll.log") -> str:
    polls, entries = rep["polls"], rep["entries"]
    n_empty = sum(p.empty for p in polls)
    n_retry = sum(p.failed_attempts > 0 for p in polls)
    L = ["# LB runtime ledger (A5)", "",
         f"Generated by `tools/runtime_ledger.py` from `{log_name}`; do not edit by hand (rewritten on every run). "
         "Report only: no gate FAILs here; each triggered change needs the user's OK.", ""]
    if not polls:
        return "\n".join(L + ["No polls in the log.", ""])
    if rep.get("now") is not None:
        L.append(f"- Ledger time: {fmt_ts(rep['now'])}.")
    L += [f"- Polls: {len(polls)} ({fmt_ts(polls[0].ts)} .. {fmt_ts(polls[-1].ts)}); empty: {n_empty}; "
          f"with failed CLI attempts: {n_retry}; gaps > {GAP_WARN_S // 60} min: {len(rep['gaps'])}.",
          "- Latency L = poll time - submission date (UTC); lower bound = last PENDING seen, upper bound = first "
          f"COMPLETE/ERROR seen (+{RETRY_SLACK_S} s per failed CLI attempt in that poll). Runtime <= L. Bounds are "
          "rounded outward to 0.01 h.",
          "- R5(a): admitted if scored without error and L <= deadline of the family (7.5 h x138/exp57b type, 9.5 h "
          "safetail builds, exp51/exp52 always). UNPROVEN = the bounds straddle the deadline -> R5(b) decides.", "",
          "## A5 triggers", ""]
    for t in rep["triggers"]:
        L.append(f"- **{t['state']}** `{t['id']}`: {t['text']}")
    L += ["", "## Submissions (newest first)", "",
          "| ref | exp | family | submitted | status | public | first result seen | last PENDING | "
          "empty / not-visible polls between | L bounds (h) | R5(a) | insertion gate | description |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in entries:
        fam = e["family"]
        dl = FAMILIES[fam]["deadline_h"]
        fam_s = f"{fam} ({dl} h)" if dl is not None else fam
        if e["result_status"]:
            first = f"{e['result_status']} {e['result_score']} @ {fmt_ts(e['first_result'])}"
            if e["retried_result"]:
                first += f" (+{e['retried_result']} failed attempts)"
            bounds = f"({fmt_lo(e['lo_h'])}, {fmt_hi(e['hi_h'])}]"
        else:
            first = "-"
            bounds = f"> {fmt_lo(e['lo_h'])} (pending)"
        between = f"{len(e['empty_between'])} / {len(e['invisible_between'])}"
        if e["empty_between"]:
            between += f" (empty at {_hm(e['empty_between'])})"
        L.append("| " + " | ".join(_cell(x) for x in [
            e["ref"], e["exp"] or "-", fam_s, fmt_ts(e["submitted"]), e["status"], e["public"] or "-", first,
            fmt_ts(e["last_pending"]), between, bounds, e["r5"][1], e["divins_gate"] or "-",
            e["description"][:90]]) + " |")
    L += ["", "## Poll health", ""]
    empties = [p for p in polls if p.empty]
    L.append(f"- Empty polls ({len(empties)}): " + (", ".join(
        fmt_ts(p.ts) + (f" {p.note}" if p.note else "") for p in empties) or "none"))
    L.append(f"- Gaps > {GAP_WARN_S // 60} min: " + (", ".join(
        f"{fmt_ts(a)} -> {fmt_ts(b)}" for a, b in rep["gaps"]) or "none"))
    bad = sum(p.bad_rows for p in polls)
    if bad:
        L.append(f"- Unparsed rows (column count mismatch): {bad}")
    L.append("")
    return "\n".join(L)


def to_json(rep: dict) -> dict:
    def conv(v):
        if isinstance(v, dt.datetime):
            return fmt_ts(v)
        if isinstance(v, (list, tuple)):
            return [conv(x) for x in v]
        return v
    return dict(n_polls=len(rep["polls"]), n_empty=sum(p.empty for p in rep["polls"]),
                last_poll=fmt_ts(rep["polls"][-1].ts) if rep["polls"] else None, now=conv(rep.get("now")),
                gaps=[[fmt_ts(a), fmt_ts(b)] for a, b in rep["gaps"]], triggers=rep["triggers"],
                entries=[{k: conv(v) for k, v in e.items()} for e in rep["entries"]])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--log", type=Path, default=DEFAULT_LOG)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--json", type=Path, default=None, help="also write the ledger as JSON")
    ap.add_argument("--family", action="append", default=[], metavar="REF_OR_EXP=FAMILY",
                    help=f"override the build family; families: {', '.join(FAMILIES)}")
    ap.add_argument("--k2", default=None, help="K2 submission ref (default: newest submission whose exp token is "
                                               f"'{K2_TOKEN}', else '{'/'.join(K2_ALT_TOKENS)}')")
    ap.add_argument("--forecast-h", type=float, default=None, help="A5 forecast F (h) from the dummy ledger")
    ap.add_argument("--now", default=None, help="ledger time, e.g. 2026-09-26T08:05:00Z (default: current UTC time)")
    ap.add_argument("--print", action="store_true", help="also print the ledger to stdout")
    a = ap.parse_args(argv)
    overrides = {}
    for kv in a.family:
        k, _, v = kv.partition("=")
        if v not in FAMILIES:
            ap.error(f"unknown family {v!r} in {kv!r}")
        overrides[k.strip().lower() if not k.strip().isdigit() else k.strip()] = v
    if not a.log.exists():
        print(f"no poll log at {a.log}", file=sys.stderr)
        return 2
    now = parse_ts(a.now) if a.now else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    rep = build(parse_log(a.log.read_text(encoding="utf-8", errors="replace")), overrides, a.k2, a.forecast_h, now)
    md = render_md(rep, a.log.name)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(md, encoding="utf-8")
    if a.json:
        a.json.write_text(json.dumps(to_json(rep), indent=1, ensure_ascii=False), encoding="utf-8")
    if a.print:
        sys.stdout.buffer.write(md.encode("utf-8"))
    for t in rep["triggers"]:
        if t["state"] in ("FIRED", "POSSIBLE", "WATCH"):
            print(f"{t['state']} {t['id']}: {t['text']}")
    print(f"ledger written: {a.out} ({len(rep['entries'])} submissions, {len(rep['polls'])} polls)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
