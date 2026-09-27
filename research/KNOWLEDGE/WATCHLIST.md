# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-27 02:25 UTC (curation 14). This is an incremental update of the curation-13 build from 01:35 UTC (`research/KNOWLEDGE/_curation/13/watch.json`).

Sources read for this update:
- `CONTEXT.md` at main HEAD **f24ff72** (2,770 lines; `## 9. Literature` at l.2750). Entries new since curation 13 (l.2626-2749):
  - ROUND 13 RECORD 01:31 (l.2626-2663);
  - **LADDER PRE-SCORE REGISTRATION** 01:31 (l.2664-2721: L5v2 l.2665, attribution l.2676, A-only extension l.2693, L9 info l.2700, stop and slots l.2704, private-read addendum l.2711);
  - **EXP71/EXP72 GOVERNANCE** 01:31 (l.2722-2746: Q1-Q3 l.2728-2731, G2 l.2736, exp72 dummy gate l.2739);
  - TIMERS UPDATED 01:32 (l.2747-2749).
- `git log` since fc2536c: 3d48d35 (01:31Z, pushed 01:31:34Z per `round14/report.json` new_facts (7)), 5e57346, f2f843e, f24ff72 (01:54Z). All four are authored by Vitaly Neybauer.
- `research/wf_ideas_v4/round14/` (**untracked**): `report.json` (complete, 02:11:57Z; R14-A0..A9, new_facts (1)-(14), plan_issues (1)-(10), rejected, next_focus), `scan_*.json`, 12 `v_*.json`. `REPORT.md` is absent for the 7th round running (`round14/report.notes.md` 02:08Z).
- Other files:
  - `experiments/lb_poll/poll.log`: last header `=== 2026-09-27T02:09:38Z` (l.10451); all four ladder refs PENDING.
  - `experiments/lb_poll/ledger.md` (02:09:40Z) and `experiments/e10_watch/20260927T0147Z.txt` (untracked).
  - `experiments/lb_poll/ladder_watch.py` (l.66 HARD_CAP 09:40Z, l.886 `--hard-cap`) and `experiments/workflows/biohub-research-round.js` (l.35, l.37, l.38, l.44).
  - `tasklist`: only python PID 20052 (the poller) at 02:2xZ.
  - CronList (read-only, 02:1xZ).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, blocked.

**State in one line (02:25Z 27 Sep):**
- **Finals ticked 2/2** = [56563521 #37 K2 0.954, 56563534 #38 twin 0.953]. The last API SELECTED read was at 20:04:35Z 26 Sep. The next one is moved to after 06:45Z (`round14/report.json` R14-A2 (6)).
- **Ladder 39-42: all PENDING** at header 02:09:38Z (`poll.log` l.10451). The latest expected score times (latency ~5 s per dummy second):
  - e ~04:33-04:45Z, d ~04:44-04:56Z, a ~04:49-05:00Z;
  - b ~07:45-08:30Z;
  - source: `round14/report.json` new_facts (10).
- **R13-A1 registration is logged and pushed before any score** (`CONTEXT.md` l.2664; 3d48d35).
- **The watcher code is committed** (f24ff72, 35 tests) but **NOT launched**: `experiments/lb_poll/ladder_watch/` does not exist, and the poller is the only python process. The launch is due at 03:30-03:45Z, hard 04:10Z (R14-A1).
- **E10 P1 at 01:47Z: not met** (`experiments/e10_watch/20260927T0147Z.txt`, untracked). amanatar is RUNNING a new version (`round14/report.json` new_facts (2)).
- **We are #242** (was #229); silver line ~197 (`round14/scan_browser.notes.md` l.3).
- **Round 14's R14-A0..A9 are all pending.**
- **New defect (this curation): the round prompt would make round 15's browser agent call the Kaggle API inside the quiet window.** See W150.
- The user has been asleep since 20:34Z (`CONTEXT.md` l.2395).

**Changes since 01:35Z (curation 13):**
- Done: W132, W133, W135, W137, W139 (see the done record at the end).
- Partly done: W134 (code done, launch pending), W136 (timer recreated as 65b1b746; the push is still due at 07:30Z), W140 (timer 2e87e414 defers inside the window; the round prompt is not fixed).
- Changed: W141's procedure is now the R14-A3 read sheet. The first SELECTED read (W137 (4)) moves from ~05:00Z to after 06:45Z (R14-A2 (6)). The watcher hard cap moves to 11:30Z (R14-A1).
- Resolved insights: I125, I126, I127, I128, I129, I133, I134, I135 (now in CONTEXT l.2626-2746).
- New: actions **W143-W150**, reminders **T62-T67**, insights **I136-I148**.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W150** (new; = W140 residue, absorbs W71 / W118) | **The round prompt will break the API quiet window in round 15.**<br>- The browser scan text (l.37) says "FIRST run `python tools/e10_snapshot.py`" and "If the browser tools are unavailable, use the Kaggle CLI". Round 14's browser agent did exactly that: the 01:47Z snapshot and the 01:48:20Z LB CSV.<br>- `FOCUS_NOTE` (l.35) exists only when `A.lenses` is set, and it is appended **only** to the plancheck scan (l.38). The browser scan (l.37) and the scan launcher (l.44) never receive the main session's focus.<br>- So round 14's next_focus ("round 15 ~04:15-04:45Z ... no Kaggle API or CLI calls by any agent") **cannot reach the browser agent** through `A.focus`.<br>- l.38 is still stale ("finals decided ... E10 >= 0.956", "12 h limit with ~4 h headroom"; last edit 13a27a1, 20:50Z 26 Sep).<br>Fix before launching round 15. Either edit l.37 so that inside 04:10-06:45Z it reads the newest `e10_watch` file and calls no CLI, or launch round 15 only after 06:45Z (or without the browser scan) | overdue (not started) | **before round 15 is launched (planned ~04:15Z)**; the window runs 04:10-06:45Z | `experiments/workflows/biohub-research-round.js` l.35, l.37, l.38, l.44; `round14/scan_browser.notes.md` l.2-3; `round14/report.json` next_focus; `CONTEXT.md` l.2747-2749 |
| W57 / W66 / W31 / W72 (curator CONTEXT records) | Due 26 Sep 12:00 and **still missed** at 02:2xZ:<br>- `CONTEXT.md` l.22 still says "frozen/duplicated frames with GT still moving" (I39);<br>- `grep -c` finds 0 hits for `out_valid` (I47), `efpost` (I51) and `33.1%` (I77) | overdue | 26 Sep 12:00 (passed) | `CONTEXT.md` l.22; `grep -c` = 0 (02:2xZ) |
| W98 (residue: I69 caveat) | `LESSONS_draft.md` l.7 still says "public LB (one embryo, ~29% of the hidden test)" as fact. The last touch is bf07763. R14-A7 now queues further LESSONS edits (by 30 Sep) but not this one | partly done | **27 Sep 12:00Z** (with R8) | `research/wf_ideas_v4/round9/LESSONS_draft.md` l.7; `git log -1` = bf07763 |
| W142 | **exp70g still has no NEVER_SUBMIT.md** (exp71 has one). L5v2 bars cap6 in text (`CONTEXT.md` l.2673), but the folder guard would not catch it | not started | before any 27-28 Sep submit | `ls experiments/exp70g_k2_cap6` = ipynb, kernel-metadata.json, probe.json |
| W03 | The friend A card is stale (`PROMPT_FRIEND_A.md` l.7-9 "answer Task 0 first"; last change b41ec05). No GPU ask is needed | partly done, low priority | now (not urgent) | `git log -1 -- PROMPT_FRIEND_A.md` = b41ec05 |
| W02 | Friend A's "Task 0" reply | overdue and moot | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22 |

## NEXT 24 H (27 Sep 02:25 -> 28 Sep 02:25 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| **W134** (= R13-A2 + **R14-A1**) | **launch 03:30-03:45Z, hard 04:10Z** | **LAUNCH THE LADDER WATCHER** as an independent detached process (not a Claude Code background task), using the restart loop `experiments/lb_poll/run_ladder_watch.sh`:<br>- run it with `--s0 experiments/e10_watch/20260927T0147Z.txt --hard-cap 2026-09-27T11:30Z`;<br>- start it with `Start-Process ... bash.exe ... -WindowStyle Hidden`;<br>- within 5 min check `ladder_watch/watch.log` for "S0 ... rank 242 score 0.954 count 40", one ListSubmissions line in `calls.jsonl`, and no Traceback in stdout;<br>- record the PID.<br>**A dead watcher DROPS the A-only extension** (`CONTEXT.md` l.2693) | in progress (code f24ff72 with 35 tests; not launched: no `ladder_watch/` folder, only PID 20052) | `round14/report.json` R14-A1, plan_issues (1)-(3); `experiments/lb_poll/ladder_watch.py` l.66, l.886 |
| **W143** (new; = R14-A2) | **right after W134; before the first poll.log header that shows a ladder ref COMPLETE; hard 04:25Z** | **ROUND 14 PRE-SCORE NOTES** (one CONTEXT entry, text ready in R14-A2), then commit as the user with **no trailer**, run the claude grep (0) and **push**. The commit holds CONTEXT, `e10_watch/20260927T0147Z.txt`, `run_ladder_watch.sh`, poll.log, ledger.md and `round14/` with REPORT.md. The entry covers:<br>(1) R13-A1 pushed 01:31:34Z;<br>(2) S0 = the 0147Z snapshot (the registered "03:04Z timer snapshot" never existed);<br>(3) watcher launch and liveness checks;<br>(4) literal readings 1-6 (ERRORed single; BLOCKED = combos only; V* ties a > d > b > e; fm45 POS supersedes the R13-A1 (1) NOTE; "UNPROVEN" does not qualify; one re-tick after D2);<br>(5) the D1/D2 sheet = R14-A3;<br>(6) SELECTED is read after 06:45Z | not started (`grep "ROUND 14" CONTEXT.md` = 0) | `round14/report.json` R14-A2, plan_issues (2), (4), (6) |
| W144 (new; = R14-A0) | with W143 | Save `round14/report.json` `report_md_ru` as `research/wf_ideas_v4/round14/REPORT.md` (the harness refused the write, 7th round running) | not started | `round14/report.notes.md` 02:08Z |
| **W150** | before round 15 | See OVERDUE: fix the browser-scan API instruction or delay round 15 | overdue | `experiments/workflows/biohub-research-round.js` l.35-44 |
| **W145** (new; = R14-A5) | **~04:20Z, ~05:20Z, ~06:30Z** | **Watcher liveness checks** (file-only):<br>- the python process and the bash loop are alive;<br>- the newest watch.log / stdout line is < 6 min old in FAST mode (else < 11 min);<br>- `calls.jsonl` grows;<br>- no STOP before all four refs are terminal, and no "=== restart" line.<br>On failure: restart, and log the gap in CONTEXT; an event inside the gap stays AMBIGUOUS. Nobody owns this while the user sleeps: set session timers now, or give it to round 15 | not started (no timer on CronList 02:1xZ) | `round14/report.json` R14-A5, plan_issues (5) |
| W140 (= R13-A8) | window **04:10-06:45Z** | **API QUIET WINDOW**: only the main session (poller + watcher) calls the Kaggle API. Timer 2e87e414 (06:04Z) defers to >= 06:45Z. Round agents read files only (see W150) | timer part done (`CONTEXT.md` l.2747-2749; CronList "R13-A8"); prompt part = W150 | `round13/report.json` R13-A8 |
| **W141** (= R13-A9 + **R14-A3**) | **D1 ~04:45-05:40Z** (39-41 terminal); **D2 after probe 42's first terminal header (~07:45-08:30Z)**; combo submit preferably by ~09:30Z, hard 28 Sep 02:00Z | **Ladder execution with the R14-A3 read sheet:**<br>- STEP 0: the watcher ran, S0 is set; run `tools/runtime_ledger.py`; **no** SELECTED read at D1.<br>- Codes NEG / N4 / U4 / P5 / ERR.<br>- L_hi clock: the first COMPLETE header must come by e 05:15:23Z / a 05:17:47Z / d 05:38:33Z / b 08:05:50Z (8.0 h), or by +1 h (9.0 h).<br>- D1 rows: D1-1 V* {V*, #38}; D1-2 A-only {exp70a, #38}; D1-3 no change.<br>- BASE table; D2 combo only if BASE exists and fm45 is POS. The dummy is mandatory: node identity exp70c 120,719 / exp70h 121,240 / exp70f 120,707.<br>- Re-tick lines R-V* / R-A / R-B / R-C; ONE re-tick after D2.<br>- Otherwise log "ladder ends (L5v2 (5a))" | not started (scores pending) | `round14/report.json` R14-A3; `CONTEXT.md` l.2665-2710 |
| W126 | with D1/D2 | **Ladder records:** one RESULTS.md row per scored probe (39-42), and fill each `experiments/exp70*/probe.json` with the score, the ledger L bounds and the attribution verdict | not started (the last RESULTS row is probe 38, l.71; no score field in any exp70 probe.json) | `experiments/RESULTS.md` l.71 |
| W137 residue | first main-session API touch **after 06:45Z** (with the 07:30Z push) | Log "API SELECTED 2/2 [56563521, 56563534] at hh:mmZ (after probes 39-41/42)". R14-A2 (6) corrects the ROUND 13 RECORD (4) timing (~05:00Z) | not started | `CONTEXT.md` l.2646; `round14/report.json` R14-A2 (6), plan_issues (4) |
| **W146** (new; = R14-A6) | **before 07:30Z** (may go with the D1 entry) | **ROUND 14 RECORD** (text ready):<br>(1) E10 01:47Z not met, amanatar ERROR -> RUNNING;<br>(2) intel: #242, 16th of 97, 226 teams >= 0.955;<br>(3) ops: R13-A1 pushed, watcher f24ff72, combo shas re-verified;<br>(4) nothing reaches R8;<br>(5) **insertion prior corrected**: +0.006 is in-sample, the honest OOF is +0.0019 on the old base, P(<0) 0.10-0.20;<br>(6) retrain evidence 0/4;<br>(7) I-063 reason corrected | not started | `round14/report.json` R14-A6 |
| **W136** (= R13-A4 + **R14-A4**) | **07:30Z** (timer 65b1b746) | **Morning push + brief** (RU, < 200 characters; variant by D1 row: P-A / P-B / P-C). Use the brief template R14D1-6 with **two corrected lines**: the #38 hedge ("+0.006 in-sample upper bound; honest OOF +0.0019; P(<0) 0.10-0.20") and the Q1 evidence line ("0 of 4 on the LB ..."). Q1-Q3, E10 v2 and the R8 cap are questions only. Log "push sent" or the not-sent result | timer recreated (done); push not yet due | `CONTEXT.md` l.2747; CronList 65b1b746; `round14/report.json` R14-A4, plan_issues (7) |
| **W149** (new; = R14-A9) | E10 API P1 **>= 06:45Z** (timer 2e87e414); Chrome view of amanatar **after ~07:00Z** | amanatar/optimized-biohub-max-score is RUNNING ("Version 1 of 6"; its lineage failed P3/P4b on 26 Sep 16:04Z). A new score >= 0.956 is a P2 look signal only: run the full P3/P4b/P4c + R12-A4 hardening. Nothing is pulled while it is RUNNING or scores < 0.954 | not started | `round14/report.json` R14-A9, new_facts (2) |
| W76 | **round 15 ~04:15-04:45Z** (files only; see W150); **round 16 ~07:00Z+**; then every ~2.5 h until **27 Sep 12:00** | **Research rounds** ("ресерчеров не забывай запускать", `CONTEXT.md` l.2395).<br>- Round 15: verify W134/W143 (pushed before the first COMPLETE header), run the W145 check, audit each event against R13-A1 (2), apply the D1 sheet mechanically, draft the D1 line and the push variant.<br>- Round 16: D2 audit, combo gates, SELECTED read, E10 P1, record the user's answers.<br>- No new mechanisms | round 14 done (untracked); round 15 not started | `round14/report.json` next_focus |
| W135 (follow-up) | answers wanted **by ~09:00Z** (Q1/Q2) | exp71/exp72 governance is logged (`CONTEXT.md` l.2722-2746). Still open: the user's Q1-Q3. If Q3 = yes, **G2 needs a second training run with a SECFT_PREFIX cell, landing by 29 Sep 12:00Z** (I130) | governance done; answers awaited | `CONTEXT.md` l.2728-2737 |
| W128 | **user yes needed by ~09:00Z** for a 27 Sep exp72 score | Retrain line exp71 -> exp72. The notebook is ready; the push is BLOCKED by the classifier; do not work around it | blocked (awaiting user) | `CONTEXT.md` l.2539-2544, l.2722-2725 |
| W106 | opt-in by **~09:00Z 27 Sep** | SI (successor + insertion) is NOT built unless the user explicitly asks | standing (default: not built) | `CONTEXT.md` l.2360 |
| W98 | **12:00Z** | LESSONS l.7 caveat (see OVERDUE) | partly done | `research/wf_ideas_v4/round9/LESSONS_draft.md` l.7 |
| W19 / W73 | until **29 Sep 20:00** | ONE poller (PID 20052). Before any submit, the last **successful** header must be < 15 min old and not a 429. Touch `ladder_watch/PAUSE` before any submit while the watcher runs | in progress (last header 02:09:38Z; 221 polls, 0 gaps > 15 min) | `experiments/lb_poll/ledger.md` l.7; `round14/report.json` R14-A1 notes |
| W102 | standing | Protect the finals' inputs (`biohub-ft-weights`, `biohub-exp58-x138-safe-lowref`, `-exp58n-`); every exp70 build and any V* mounts `biohub-ft-weights` | standing | `CONTEXT.md` l.2249-2252 |
| W93 | standing, until 29 Sep 23:59 | Never push or submit exp65 / exp66, exp70g (W142), exp71 (NEVER_SUBMIT.md), or the dry-run kernel `biohub-exp63-succ-dryrun-raunakdey07` | standing | `CONTEXT.md` l.2223-2226, l.2616-2617 |
| T62 | **03:04Z** | Timer 2e87e414 fires, but it acts only if the newest snapshot is > 2 h 30 min old. 0147Z is 1 h 17 min old, so expect a **no-op** | - | `CONTEXT.md` l.2530-2531; CronList (cron `4 0,3,6,...` is local UTC+3) |
| T63 | **03:30-03:45Z** | Watcher launch (W134) | - | `round14/report.json` R14-A1 |
| T52 | **04:10Z** | Hard latest watcher start; quiet window starts (W140 / W150) | - | `round13/report.json` R13-A8 |
| T64 | **04:20Z, 05:20Z, 06:30Z** | Watcher liveness checks (W145) | - | `round14/report.json` R14-A5 |
| T53 | **04:25Z (hard)**; earlier if a ref completes first | W143 logged, committed **and pushed**. After the first COMPLETE header, any reading is post-hoc | - | `round14/report.json` R14-A2 deadline |
| T54 | **~04:33-05:00Z** | Probes 39/41/40 COMPLETE (e ~04:33-04:45, d ~04:44-04:56, a ~04:49-05:00). **8.0 h marks: e 05:15:23, a 05:17:47, d 05:38:33Z** (the A-only extension needs exp70a "did NOT fire") | - | `round14/report.json` new_facts (10), R14-A3 L_hi clock |
| T55 | **06:04Z** | Timer 2e87e414 defers to >= 06:45Z | - | `CONTEXT.md` l.2747-2749 |
| T65 | **06:45Z** | Quiet window ends: SELECTED read at the first API touch after it; E10 API P1 resumes | - | `round14/report.json` R14-A2 (6), R14-A9 |
| T44 (= W136) | **07:30Z** | Morning push (timer 65b1b746) | timer alive | CronList 02:1xZ |
| T57 | **~07:45-08:30Z** | Probe 42 (exp70b) COMPLETE, then D2. 8.0 h mark 08:05:50Z, 9.0 h mark 09:05:50Z. One re-tick after D2 (~08:30Z) | - | `round14/report.json` R14-A3 |
| T58 | **~09:00Z** | Last useful user yes for exp71 (a 27 Sep exp72 score); last SI opt-in | - | `CONTEXT.md` l.2543 |
| T59 | **~09:30Z** (preferred) | L5v2 combo submit, if any (hard edge 28 Sep 02:00Z) | - | `round14/report.json` R14-A3 |
| T56 | **11:30Z** | Watcher hard cap (was 09:40Z; the code default at l.66 is still 09:40Z, so pass `--hard-cap`). A ref still PENDING at the cap is read as not scored | - | `round14/report.json` R14-A1, plan_issues (3) |
| T03 | **27 Sep 12:00** | **R8.** No new mechanism after this. E10 v2 OK lapses. W98 residue. After 12:00Z only an E10 port or exp72 (explicit yes) can add a mechanism; the L5v2 combo is not a new mechanism | - | `CONTEXT.md` l.1671-1672, l.2658-2662 |
| T66 | from **12:00Z** | Curator edits R14-A7 and the R14-A8 hindsight commit may start (W147 / W148) | - | `round14/report.json` next_focus |
| T32 / T39 | 27 Sep 09:04, 12:04, 15:04, 18:04, 21:04 | E10 P1 checks (timer 2e87e414) | timer alive | CronList 02:1xZ |
| T18 / T42 | **28 Sep 00:00** | Slot reset: 5 slots for 28 Sep. Keep 1 per day for a port | - | `CONTEXT.md` l.2704-2710 |
| T67 | standing | **All six timers are session-only and die with the session.** If the session restarts, recreate 65b1b746, 2e87e414, 012fa6dd, 328f7392, 18ff4796 and bb224de9 from CONTEXT | - | `CONTEXT.md` l.2530; CronList "[session-only]" |

## LATER (28 Sep 02:25 -> 29 Sep 23:59 UTC, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T59 (cont.) | **28 Sep 02:00** | Hard edge for the L5v2 combo submit (so it scores before F1) | `round14/report.json` R14-A3 |
| T32 / T39 (cont.) | 28 Sep 00:04 ... 21:04 every 3 h; the last useful one 29 Sep 00:04 | E10 P1 checks (the prompt self-limits at 29 Sep 00:30Z) | `CONTEXT.md` l.2530-2531 |
| T46 | **28 Sep 12:00** | **F1 consolidation** under R8 | `CONTEXT.md` l.1671, l.2708-2709 |
| T28 | 28 Sep | S14: an x138 successor on a late trigger (P7) | `CONTEXT.md` l.1616 |
| T19 / W77 | **28 Sep 17:57** (timer 012fa6dd) | API SELECTED plus the first logged page read of the ticks | CronList; `CONTEXT.md` l.2365 |
| T35 | 28 Sep 22:00 | The plan's "final admission table" = the L9 eligibility table for every ladder variant (+ an exp72 row if Q3 = yes) | `research/wf_ideas_v3/FINAL_REPORT.md` l.178; `CONTEXT.md` l.2607-2610 |
| T20 | **29 Sep 00:00** | The last slot reset and the last useful E10 trigger; the port slot is freed (1 per day kept until then). The dummy must be terminal by 01:45Z | `CONTEXT.md` l.2355, l.2708 |
| T29 / T47 | **29 Sep 02:00** | The last E10 port submit and the last ladder submit under R8 | `CONTEXT.md` l.2709 |
| T60 (= W135 G2) | **29 Sep 12:00** | G2 must have landed (pooled >= -0.0005) for exp72 to be finals-eligible; only if Q3 = yes | `CONTEXT.md` l.2736 |
| T09 / W77 | **29 Sep 11:57** (328f7392, push) / **17:57** (18ff4796) | Remind the user to check or re-tick; API SELECTED | CronList |
| T48 (= W131) | **29 Sep ~19:00** | **L9 read** (re-read on every new score): V* -> {V*, #38}; A-only -> {exp70a, #38}; E10 port without insertion -> {PORT, #37}; exp72 only via Q3. Never two byte-identical files. Tell the user the exact two refs | `CONTEXT.md` l.2510-2518, l.2693-2703; `round14/report.json` R14-A2 (4) |
| T10 | **29 Sep 20:00** | Ticks final: exactly 2 files; without a re-tick {#37, #38} stays. **Stop the poller** | `CONTEXT.md` l.2515-2516, l.2620 |
| **W148** (new; = R14-A8) | **before 29 Sep 23:00Z** (after 12:00Z 27 Sep is fine) | **Hindsight guard:** ONE text-only commit as the user, **pushed**, holding LESSONS s3 item 11 + "do not rewrite after the private LB", with P1 (at least one of L1/L2/L4 non-zero; all zero is uninformative) and P3 dropped. Record the pushed hash in CONTEXT; the GitHub push time is the stamp | `round14/report.json` R14-A8, plan_issues (9) |
| T49 | **29 Sep 23:00-23:45** (timer bb224de9 at 23:27) | Final public LB snapshot to `experiments/private_read/` | `CONTEXT.md` l.2580-2588; CronList |
| T11 | 29 Sep 23:59 | Competition deadline. A submit must **finish** before it to count (safe assumption; participant comment only, no host answer) | `round14/report.json` new_facts (6) |
| T30 / T50 | **30 Sep from 00:15Z, hourly** | Private read per v2 (d) + the ladder addendum L1-L5 (`CONTEXT.md` l.2711-2721); rank over the SELECTED pair | `CONTEXT.md` l.2570-2598, l.2711 |
| **W147** (new; = R14-A7, merged with W138 = R13-A6 and W123 = R12-A10) | s3 item 11 + E-s3.* **before the first private score**; the rest **by 30 Sep** | Curator edits:<br>- IDEAS I-106 (-> untested; 0/4 prior), I-063 (unresolved at noise level), I-069;<br>- v_retrain "0 of 5" annotated;<br>- LESSONS: 12th-16th, quota-reset clause, R14L-9 sentence, 0c descriptive B arm, counterfactual R9 line;<br>- plus R13-A6 (IDEAS nodes line, I-312 closure, post-deadline list, I-051, tau, F-TRN-41) and R12-A10 | `round14/report.json` R14-A7; `round13/report.json` R13-A6; `round12/report.json` R12-A10 |
| W29 | after 29 Sep | Post-deadline list (rounds 10-14: G0 split, detector program, start-leaf prune, component prune, div 2.5, density-aware symmetry gate, I-063 fold-wise v1 vs v2) | `round10/report.json` R10-A5 (g); `round14/report.json` R14-A7 |
| W102 (cont.) | until the private LB is final | Keep every file a ticked final mounts intact | `CONTEXT.md` l.2249-2252 |

**Done, superseded or moot since 01:35Z (for the record):**
- W133 (R13-A1): LADDER PRE-SCORE REGISTRATION at `CONTEXT.md` l.2664-2721; committed in 3d48d35 and pushed 01:31:34Z, before any score (`round14/report.json` new_facts (7)).
- W135 (R13-A3): EXP71/EXP72 GOVERNANCE at `CONTEXT.md` l.2722-2746.
- W137 (R13-A5): ROUND 13 RECORD at `CONTEXT.md` l.2626-2663. Its item (4) timing is superseded by R14-A2 (6) (W137 residue above).
- W132 (R13-A0): `research/wf_ideas_v4/round13/REPORT.md` tracked (3d48d35).
- W139 (R13-A7): 3d48d35 / f2f843e / f24ff72, authored by Vitaly Neybauer (`git log`). The claude grep is not re-verified by this curator.
- W136 part: timer c7cd2e6b -> 65b1b746 with the R13-A4 content (`CONTEXT.md` l.2747; CronList "R12-A7 + R13-A4").
- W140 part: E10 timer 2f0d1fa1 -> 2e87e414 with the quiet-window deferral (`CONTEXT.md` l.2748; CronList "R13-A8").
- W134 part: watcher code + 35 tests + dry run (f24ff72; `round14/report.json` new_facts (7)).
- W111 / T36 / T51: the E10 P1 at 01:47Z ran (via round 14's browser agent), not met (`experiments/e10_watch/20260927T0147Z.txt`).
- W71 / W118 are merged into W150; W138 / W123 are merged into W147.
- Earlier records: `_curation/13/watch.json`, `_curation/12/watch.json`.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| I136 (new) | `const FOCUS_NOTE = A.focus && LENSES ? ... : ''` is interpolated only into the plancheck text. The browser scan says "FIRST run `python tools/e10_snapshot.py` ... If the browser tools are unavailable, use the Kaggle CLI only" | `experiments/workflows/biohub-research-round.js` l.35, l.37, l.38, l.44 | Found by this curator. Round 14's plan puts round 15 inside the quiet window with "no API calls by any agent", but the mechanism cannot tell the browser agent that (W150) |
| I137 (new) | "main() catches only KeyboardInterrupt, and run() has no per-iteration except"; "save_state's os.replace raised PermissionError while another handle held state.json (3,076 of 4,432 replaces failed in a tight-loop test)"; "Every agent reads watch.log and calls.jsonl only, never state.json from Python" | `round14/report.json` new_facts (8), R14-A1 notes | Any round-15 agent that opens `state.json` can kill the watcher, and a dead watcher DROPS the A-only extension. The rule exists only in round14 (untracked) |
| I138 (new) | "Latency scales weakly with dummy runtime ... ~5 s of latency per dummy second"; "P(any ref COMPLETE before 04:10Z) ~5-10%" | `round14/report.json` new_facts (10); rejected (PC14-03 timing) | Sets the score-time table (T54/T57) and why the watcher starts at 03:30-03:45Z. Not in CONTEXT |
| I139 (new) | "The registered S0 source ('03:04Z timer snapshot') never existed"; the 0147Z import gives "rank 242, 0.954, count 40, and 241 TeamIds above. The snapshot keeps every row >= 0.953, which is enough for the UP test" | `round14/report.json` plan_issues (2), new_facts (9) | `CONTEXT.md` l.2677-2679 still names the 03:04Z snapshot. Without W143 (2) the S0 choice becomes post-hoc |
| I140 (new) | Literal reading (4): "fm45 POS = exp70b displays >= 0.955, or 0.954 with an attributable UP, whether or not it beat the base. This supersedes the R13-A1 (1) NOTE, which is inexact when the base displays 0.955" | `round14/report.json` R14-A2 (4)(4) | The CONTEXT NOTE (l.2672-2674) says a POS fm45 "means exp70b beat that base". If W143 is not logged, D2 might wrongly veto a combo |
| I141 (new) | PC14-05: "exp70a's 8.0 h mark is 05:17:4[7]Z"; L_hi comes from 10-min polls, so a completion near the mark reads UNPROVEN and the A-only extension fails. The fix (watcher timestamps) was **rejected**; "the ledger text alone decides; the fallback is {#37, #38}" | `round14/scan_plancheck.json` PC14-05; `round14/report.json` rejected | exp70a is expected ~04:49-05:00Z, so the margin is ~20-30 min. It explains an A-only "miss" at D1 without anyone reopening the rule |
| I142 (new) | "R12-A3's +0.006 is the exp60 IN-SAMPLE number. The honest reference is the v1 single-fold OOF ... +0.0019 ..., added precision 4/15 = 0.27 ... Break-even: 0.125 on the 6bba lab, 0.11-0.20 on private" | `round14/report.json` new_facts (12); `round14/v_recheck_r14-rc-c-...json` | The 07:30Z brief and the 16:54Z forecast cite +0.006 as the insertion driver. It must be corrected in W136/W146 before the user reads it |
| I143 (new; updates I113) | "our FT weights on public stacks are 0/4 on the LB" (exp33 -0.003, exp30 -0.003, soup -0.004, exp32 -0.007); "The exact exp72 setup is untested"; E ~0, P(<0.954) ~25-30% | `round14/report.json` new_facts (13), R14-A4 (2) | The honest prior for the user's Q1-Q3. `reach0955/v_retrain.json` still says "0 of 5" |
| I144 (new) | amanatar: "'Version 1 of 6' (it was v10 before: the history was renumbered or reset)"; the author claims "Kaggle has addressed the historical metric exploit"; there is no host post | `round14/report.json` new_facts (2); `round14/scan_browser.json` r14-amanatar-rerun | A version-number diff check (R12-A4 "Version k of M") can misread a reset history. Its lineage failed P3/P4b, so a >= 0.956 there is not a port trigger by itself |
| I145 (new; updates I135) | Discussion 743765: a participant (not the host) says "It has to finish before the deadline to count." No host answer | `round14/report.json` new_facts (6); https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 | Any submit near 29 Sep 02:00Z or later must finish (not just start) before 23:59Z |
| I146 (new) | "We are #242 (was #229) ... Silver line ~197"; "13 teams passed us" in ~3 h; teams >= 0.955: 226 (was 214) | `round14/scan_browser.notes.md` l.3; `round14/report.json` new_facts (3) | Drift against the 16:54Z medal forecast (`CONTEXT.md` l.2327-2332: silver ~197, P(silver) ~0.10-0.15). Info only; no decision uses rank |
| I147 (new) | "V* ties at equal display: a > d > b > e"; "A ref still PENDING at the watcher hard cap (11:30Z) is read as not scored"; "One re-tick after D2 (~08:30Z). A second only if a combo becomes V*" | `round14/report.json` R14-A2 (4), R14-A3 | Tie and cap rules for a sleepy-hour read. They exist only in round14 until W143 lands |
| I148 (new) | "The Boys ... latency was under 3.3 h ... a short kernel and says nothing about our ~7.4 h runs" | `round14/report.json` new_facts (4) | Guards against reading other teams' fast scoring as queue speed-up for our refs |
| I130 (partly resolved) | "exp71_secft_all trains on all 199 videos; the notebook has no SECFT_PREFIX" | `round13/v_plancheck_pc13-05.json`; `CONTEXT.md` l.2736 | G2 is now defined in CONTEXT, but its second ~4 GPU-h run is still unscheduled (only if Q3 = yes) |
| I131 | "Inside the 0.953 block the order is not by submission time ... the displayed 0.953 hides unrounded differences" | `round13/scan_browser.json` r13-top-movers-and-copies | Round 14 again sees two teams above us "inside the 0.954 block (unrounded order)" (`round14/report.json` new_facts (3)). Not in CONTEXT; it qualifies the v2 (c) tie read |
| I132 | "a 1-sub newcomer at 0.955 means a finished recipe exists somewhere"; E10 P2 counts only >= 0.956 | `round13/scan_browser.json` r13-lb-delta-2246 | Round 14 shows five more teams at 0.955 and a P2 group of 3 at 0.956. Info only |
| I110 / I111 | lp30 x lowrefine are **non-additive**; the dc x insertion interaction is unmeasured on the honest bed | `reach0955/v_ladder.json` corrections (1)-(2) | Now partly echoed in the A-only worst case (`CONTEXT.md` l.2697-2699) and the L3 read rule (l.2716) |
| I114 | "x138 cell 1 = configuration guard: BIOHUB_DET_THRESHOLD must equal 0.965 ... else RuntimeError" | `reach0955/v_intel.notes.md` | Still not in CONTEXT |
| I116 | The reach0955 discussion agent's times labelled "Z" are local (UTC+3) | `reach0955/discussions_2026-09-26.notes.md` | Same trap in CronList: cron hours are local (e.g. 65b1b746 "30 10 27 9" = 07:30Z) |
| I122 / I124 | "a public-best improvement wins on private ~3 in 4"; "LB moves with the predicted node count" (tested in round 13: best pruning +0.0015 lab) | `CONTEXT.md` l.2427-2436, l.2658-2660 | Recorded; the LESSONS part is in W147 |
| I96 | P2 flags only at `P2_MIN = Decimal("0.956")` | `tools/e10_snapshot.py` l.52 | Relevant only if E10 v2 is OK'd (lapses 12:00Z) |
| I72 | The harness again asks for a "Claude Opus 5.5" Co-Authored-By trailer; the user's rule forbids it | this curator's context; `memory/feedback-git-no-coauthor.md` | Keep for W143 / W148. The last 16 commits are authored by Vitaly Neybauer |
| I95 | **The harness has refused the round-report Write seven rounds running** (8-14) | `round14/report.notes.md` 02:08Z | Each REPORT.md exists only if the main session extracts it (W144) |
| I97 / I98 / I102-I104 | 0.953-block median; late exact copies at the block end (**14th** window, #674-688); overnight burst; P(successor >= 0.954) ~5-15% | `round11/report.json`; `round14/report.json` new_facts (4) | See I131 |
| I99 / I100 / I101 / I105 / I106 | Builder `--base` header; HF v3 is a clone; the DaughterNet load raises outside the fail-soft (every exp70 build fails hard if `biohub-ft-weights` breaks); node-drop bonus; 6bba misses are peakless | `round11/report.json` | I101 covers any V* (W102) |
| I88 / I89 | x138's dormant ADAPTIVE_SHORT_TRACK_RESCUE is not in CONTEXT; a primary swap under x138 fails silently | `research/KNOWLEDGE/IDEAS.md` l.293, l.235 | Unmeasured for combos. amanatar's new title "Clean Short-Track Rescue" (I144) touches the same family |
| I69 | "public = one embryo" is a participants' guess, not a host fact | `research/discussions_summary.md` l.4-6 | Still stated as fact in LESSONS l.7 (W98) |
| I77 / I78 / I79 / I83 / I47 / I51 / I39 / I44 | Blend-switch 33.1%; FN/FP division anatomy; delete-node deltas; edge-FP rule; efpost; the l.22 error; unadapted features | `round9/report.json`; `round6/report.json`; `round5/report.json` | The W57 family |
| I01-I09, I14-I29, I34, I46, I52-I54, I64-I68, I71, I73, I76 | Older lens and round insights, unchanged | `_curation/11/watch.json`; `research/wf_ideas_v4/lens_*.json` | Post-deadline and §11 lessons |

**Resolved since 01:35Z (now in CONTEXT):**
- I125 (SubmissionCount counts SCORED only): `CONTEXT.md` l.2635-2636, l.2679-2682.
- I126 (B0 = max(P36, #35, K2)): l.2688-2690.
- I127 (the insertion gate is per clip): l.2663, l.2700-2703.
- I128 (dc0.30 on 44b6 is in-sample): l.2649-2657.
- I129 (dummy node gate is necessary only): l.2724-2726.
- I133 (the x138 author is the likeliest trigger): l.2629-2630.
- I134 (combo condition and P(combo)): l.2672-2675.
- I135 (topic 743765): l.2635-2636; updated by I145.
- Details: `_curation/13/watch.json`.
