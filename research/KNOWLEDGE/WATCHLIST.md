# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-27 06:10 UTC (curation 15). This is an incremental update of the curation-14 build from 02:25 UTC (`research/KNOWLEDGE/_curation/14/watch.json`).

Sources read for this update:
- `CONTEXT.md` at main HEAD **da9766e** (2,834 lines; `## 9. Literature` at l.2814). Entries new since curation 14 (l.2750-2813):
  - ROUND 14 PRE-SCORE NOTES 02:28 (l.2750-2775);
  - READ SHEET v1 02:28 (l.2776-2785);
  - WATCH TIMERS 02:29 (l.2786-2788);
  - **LADDER READ D1** 04:58 (l.2789-2799);
  - **POST-D1 EXPLORATION RUNGS** 04:59 (l.2800-2808);
  - **SUBMIT probes 43/44** 05:28 (l.2809-2813).
- `git log` since f24ff72: 8155321 (02:28:56Z), a129e5f, 862869f (04:58Z), 477a3bb, da9766e (05:28:44Z). All are authored by Vitaly Neybauer, and none carries a Co-Authored-By trailer (`git log --format=%B -8 | grep -ic co-authored` = 0). `git status -sb` shows `main...origin/main`, so all five are pushed.
- `research/wf_ideas_v4/round15/` (**untracked**): `report.json` (complete, 06:00Z; R15-A0..A8, new_facts (1)-(11), plan_issues (1)-(12), rejected, next_focus), the `scan_*.json` / `*.notes.md` files and `v_hyp_div_sensitivity_r15ds-1.*`. `REPORT.md` is absent for the 8th round running (`round15/report.notes.md` 06:00Z).
- Other files:
  - `experiments/lb_poll/ledger.md` (06:00:21Z);
  - `poll.log` (last header `=== 2026-09-27T06:00:19Z`, l.11854);
  - `ladder_watch/watch.log` (events 04:13:06Z / 04:31:08Z / 04:56:17Z) and `ladder_watch/calls.jsonl` (last 06:01:36Z, rc 0);
  - `experiments/e10_watch/20260927T0531Z.txt` (untracked);
  - `experiments/workflows/biohub-research-round.js` (last commit 13a27a1);
  - `experiments/RESULTS.md` (last probe row l.71 = probe 38);
  - `experiments/exp70*/`.
- CronList (read-only, 06:0xZ).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, blocked.

**State in one line (06:10Z 27 Sep):**
- **Finals ticked 2/2** = [56563521 #37 K2 0.954, 56563534 #38 twin 0.953]. No re-tick is due: D1 row D1-3 (`CONTEXT.md` l.2789-2795).
- **Ladder D1 is read:** 39 exp70e 0.949 NEG, 40 exp70a 0.954 NEU (no UP), 41 exp70d 0.949 NEG.
  - BASE = none, so no combo is possible, whatever probe 42 shows (l.2789-2793).
  - **DC 0.25 -> 0.30 costs -0.005 public, although the lab said +0.001** (l.2796-2798).
- **Probe 42 exp70b is still PENDING** (L > 5.90 h, `ledger.md`). Its event is expected ~07:27-08:30Z; the 9.0 h clock ends 09:05:50Z.
- **Probes 43 exp70j (DC 0.20, 56598763) and 44 exp70k (DC 0.225, 56598765) were submitted 05:28Z** (l.2809) as class C.
  - They broke R13-A1 (1), R13-A1 (5)(a), the 5-submit ladder cap and L9's no-threshold-neighbours line, with no user OK (`round15/report.json` plan_issues (1)).
  - Their scores are expected **~12:15-13:10Z**.
- **2 slots are left on 27 Sep** (`CONTEXT.md` l.2812).
- **The watcher is alive** (calls.jsonl 06:01:36Z rc 0). It exits once exp70b is terminal, so poll.log is the only record for 43/44 (`round15/report.json` new_facts (5)).
- **Round 15 is complete** (06:00Z). None of R15-A0..A8 is done yet. The most urgent is **R15-A1, the pre-score entry for 43/44 (deviation record + FREEZE + class-C table)**: do it now, hard deadline 11:45Z.
- **We are #256** (was #242), 17th of 102 in the 0.954 block (`round15/report.json` new_facts (3)).
- The user has been asleep since 20:34Z (`CONTEXT.md` l.2395). The morning push is due 07:30Z.

**Changes since 02:25Z (curation 14):**
- Done: W134 (watcher launched 03:35Z, PID 10088), W143 (l.2750), W144 (`round14/REPORT.md` in 8155321), the R14-A3 read sheet logged (l.2776), W141 D1 (l.2789), W145 timers created (l.2786).
- W150 happened as predicted: round 15's browser agent ran `e10_snapshot.py` at 05:31:16Z (8 CLI calls) inside the quiet window. There was no 429 and no harm (`round15/scan_plancheck.notes.md`; plan_issues (9)). The prompt is still unfixed.
- Superseded or corrected:
  - the W136 push variants (R14-A4 -> **R15-A2**);
  - the W137 residue (-> **W153**);
  - the 04:59Z prior 0.2-0.3 (-> 0.08-0.20, plan_issues (5));
  - the 05:28Z line "watcher paused" (false: 0 pause lines, plan_issues (9)).
- Moot: the A-only extension (exp70a = NEU; `CONTEXT.md` l.2791-2793); T54 / T62 / T63 / T52 / T53 have passed.
- New: actions **W151-W157**, reminders **T68-T76**, insights **I149-I160**.
- Resolved insights: I137 (partly), I138, I139, I140, I141, I147.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W151** (new; = R15-A1) | **The pre-score entry for probes 43/44 is not logged.** It is one merged CONTEXT entry (text ready):<br>(1) a DEVIATION RECORD against R13-A1 (1) / (5)(a), the 5-submit cap and L9;<br>(2) a **FREEZE**: no further DC rung, no DC / fm45 combo and no ladder submit through 29 Sep unless the user asks;<br>(3) the descriptive read rule;<br>(4) the CLASS-C FINALS TABLE: default (a) no change, (b) {V*_C, insertion final}, (c) {V*_C, #38} not recommended; a letter counts only if it is logged before the first header that shows 43/44 terminal; ties go to 44;<br>(5) priors of 0.08-0.20 per rung;<br>(6) the NARROW/BROAD reading note;<br>(7) the L6/L7 private-read addendum;<br>(8) the correction of "watcher paused".<br>Then commit and push as the user (no trailer; claude grep 0). **Without it, any class-C choice at ~12:15Z+ is post-hoc** | overdue ("now, before the 07:30Z brief") | **now; before 07:30Z; hard 11:45Z** (earliest 43/44 terminal ~12:15-12:20Z) | `round15/report.json` R15-A1; `grep "PROBES 43/44" CONTEXT.md` = 0 |
| **W126** | **Ladder records for 39-41 are missing:**<br>- no RESULTS.md row for probes 39-42 (the last row is probe 38, l.71);<br>- no score field in any `experiments/exp70*/probe.json`.<br>Also, all exp70* probe.json files carry the builder boilerplate "above exp56 adopt", which contradicts class C (I154) | overdue (D1 was read 04:58Z) | with the D1 entry (passed); now with W151 | `experiments/RESULTS.md` l.71; `round15/scan_plancheck.notes.md` ("probe.json 'rule' field is builder boilerplate") |
| W142 (extended) | No NEVER_SUBMIT.md in **exp70g** (cap6 dropped), **exp70j** or **exp70k** (class C, "never resubmitted" under the R15-A1 (2) FREEZE). exp71 has one | not started | before any further 27-29 Sep submit | `ls experiments/exp70*` (06:0xZ); `round15/scan_plancheck.notes.md` ("No NEVER_SUBMIT.md") |
| W57 / W66 / W31 / W72 (curator CONTEXT records) | Due 26 Sep 12:00 and **still missed**:<br>- `CONTEXT.md` l.22 still says "frozen/duplicated frames with GT still moving" (I39);<br>- `grep -c` finds 0 hits for `out_valid` (I47), `efpost` (I51) and `33.1%` (I77) | overdue | 26 Sep 12:00 (passed) | `CONTEXT.md` l.22; `grep -c` = 0 (06:0xZ) |
| W98 (residue: I69 caveat) | `LESSONS_draft.md` l.7 still says "public LB (one embryo, ~29% of the hidden test)" as fact (last touched in bf07763) | partly done | **27 Sep 12:00Z** (with R8) | `research/wf_ideas_v4/round9/LESSONS_draft.md` l.7 |
| W150 (residue) | **The round prompt is still unfixed** (js last commit 13a27a1):<br>- l.37 makes the browser agent run `e10_snapshot.py` first;<br>- l.38 is stale ("finals decided ...").<br>In round 16 (~08:00-08:45Z) the agent's 8 CLI calls would fall inside the exp70b event window 07:27-08:30Z, which R15-A7 "soft-prefers" to keep clear. Low harm now that the quiet window ends 06:45Z | overdue, low priority | before round 16 | `experiments/workflows/biohub-research-round.js` l.35-38; `round15/report.json` R15-A7 |
| W03 | The friend A card is stale (`PROMPT_FRIEND_A.md` l.7-9; last change b41ec05) | partly done, low priority | not urgent | `git log -1 -- PROMPT_FRIEND_A.md` |
| W02 | Friend A's "Task 0" reply | overdue and moot | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22 |

## NEXT 24 H (27 Sep 06:10 -> 28 Sep 06:10 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| **W151** | **now; hard 11:45Z** | R15-A1 pre-score entry (see OVERDUE) | overdue | `round15/report.json` R15-A1 |
| **W152** (new; = R15-A0) | with W151 | Save the `report_md_ru` field of `round15/report.json` as `research/wf_ideas_v4/round15/REPORT.md`. Commit it with W151 together with `round15/` and `e10_watch/20260927T0531Z.txt` (untracked) | not started | `round15/report.notes.md` 06:00Z; `git status` (`?? research/wf_ideas_v4/round15/`) |
| W145 | **06:31Z** (timer cdd738f1) | Last watcher liveness check (file-only until 06:45Z). The watcher is alive (calls.jsonl 06:01:36Z rc 0), but **no liveness result is logged in CONTEXT**, and CronList still lists **5b23a3ed (04:21Z) and 54a8f20d (05:21Z)** after their times (I159) | in progress | CronList 06:0xZ; `CONTEXT.md` l.2786 |
| W140 | ends **06:45Z** | API quiet window. The round-15 snapshot breach at 05:31Z is logged by W151 (8) | ends | `round15/report.json` plan_issues (9) |
| **W136** (= R13-A4 + **R15-A2**, replaces R14-A4) | **07:30Z** (timer 65b1b746) | **Morning push + brief in the CORRECTED form R15-A2:**<br>- P-A (177 characters) by default; P-B only if probe 42 displays >= 0.955 with L_hi <= 9.0 h;<br>- the brief has 6 sections: the ladder table, 43/44 with the breach disclosed and the freeze, finals, **Question 1 on class C (default (a); answer by 12:00Z)**, Q2 E10 v2, Q3-Q5 exp71/exp72, **Q6 last-submit edge 02:00Z vs 11:00Z**, and slots / E10 / LB.<br>**Do not send the R14-A4 / R14D1-6 variants.** Log "push sent" | timer alive; not due | `round15/report.json` R15-A2, plan_issues (4) |
| **W153** (new; = R15-A3; absorbs the W137 residue) | **07:30Z** (the first main-session API touch after 06:45Z) | Read API SELECTED once and log "API SELECTED 2/2 [56563521, 56563534] at hh:mmZ (after probes 39-44)". Any other value: stop and notify the user. Re-read only after a re-tick | not started | `round15/report.json` R15-A3; `CONTEXT.md` l.2775 |
| **W141** (D2 = **R15-A4**) | **~07:27-08:30Z**; 8.0 h clock 08:05:50Z, **9.0 h clock 09:05:50Z** | D2 read of probe 42 exp70b by READ SHEET v1:<br>- no combo (BASE none);<br>- V* only if COMPLETE, >= 0.955 and L_hi <= 9.0 h (quote the ledger insertion-gate text);<br>- if V*: {exp70b 56592350, #38}, and the re-tick timing follows W151 (4);<br>- ERROR at < 10 h: one unchanged resubmit (R13-A1 (5));<br>- one CONTEXT line + the D2 push.<br>Prior P(>= 0.955) ~0.10-0.15 | not started (PENDING at 06:00:19Z) | `round15/report.json` R15-A4; `CONTEXT.md` l.2776-2785 |
| T70 (new) | when exp70b is terminal | **The watcher exits** (the run_ladder_watch.sh `until` loop ends on rc 0). From then on poll.log (10-min cadence) is the only record for 43/44, with no UP attribution; equal displays are a tie | - | `round15/scan_plancheck.notes.md` ("Watcher code"); plan_issues (10) |
| **W149** (= R14-A9 + **R15-A7**) | E10 P1 **>= 06:45Z** (timer 2e87e414 at 06:04Z defers); preferably once **after the exp70b event (>= ~08:35Z)**; Chrome look at amanatar **after 07:00Z** | amanatar V6 is COMPLETE with no public score (~9 knobs + 2 code blocks). Even at >= 0.956 it **fails E10 P3**; log it as a confounded read on "more safe divisions". **The E10 path is not bound by R8**: P3 is the blocker, not R8 | not started | `round15/report.json` R15-A7, new_facts (2); `experiments/ext_optimized-biohub-max-score/v6_2026-09-27/` (untracked) |
| W146 (= R14-A6) + **W155** (new; = R15-A6) | before 07:30Z (W146); today, after W151 (W155) | **ROUND 14 RECORD** (text in R14-A6; not logged: grep "ROUND 14 RECORD" = 0). **ROUND 15 RECORD** (text in R15-A6):<br>- E10 05:31Z not met;<br>- LB #256;<br>- dummy re-verification;<br>- D1 audit OK;<br>- calibration;<br>- DC semantics;<br>- finals recheck (no change);<br>- insertion knobs;<br>- probe-42 re-price;<br>- nothing reaches R8 | not started | `round14/report.json` R14-A6; `round15/report.json` R15-A6 |
| W76 | **round 16 ~08:00-08:45Z**; **round 17 ~13:00-14:30Z** | Research rounds.<br>- R16: audit W151 (logged, pushed before any 43/44 header), the brief form, the D2 read, user letters and their times, E10 after exp70b; log the 12:00Z lapse.<br>- R17: audit the 43/44 read, L6/L7.<br>- **No mechanism, no DC rung.** Watch W150 (l.37 CLI calls) | round 15 done (untracked) | `round15/report.json` next_focus; `CONTEXT.md` l.2395 |
| W135 / W128 / W106 | answers wanted **by ~09:00Z** (Q1/Q2 for a 27 Sep exp72 score); SI opt-in **by ~09:00Z** | exp71/exp72: the push is BLOCKED until the user says yes. Honest prior: 0/4 FT on the LB, E ~0, P(< 0.954) ~25-30%. G2 needs a second run landing by 29 Sep 12:00Z if Q3 = yes. SI is not built unless asked | blocked (awaiting user) | `CONTEXT.md` l.2722-2746; `round15/report.json` R15-A2 §5 |
| **W154** (new; = the user letter for R15-A1 (4)) | **before the first poll.log header with 56598763 or 56598765 terminal (~12:15Z)**; the brief asks for it by 12:00Z | The user's class-C letter (a) / (b) / (c) must be **logged with `date -u` BEFORE that header** to count as pre-registered. A later letter is logged as USER DECISION AFTER SCORE. No answer = (a) | not started (W151 is not logged) | `round15/report.json` R15-A1 (4), R15-A2 §4 |
| T03 / W157 (new; = R15-A7 lapse line) | **12:00Z** | **R8.** No new mechanism after this. Log "**E10 v2 lapsed; R8 passed; no new mechanism**" if the user has not answered. W98 is due. After 12:00Z only an E10 port (not R8-bound) or exp72 (explicit yes) | not started | `CONTEXT.md` l.1671-1672; `round15/report.json` R15-A7 |
| **W156** (new; = R15-A5) | **~12:15-13:10Z** (first header with both refs terminal). 8.0 h clocks 13:28:13Z / 13:28:22Z; **9.0 h clocks 14:28:13Z / 14:28:22Z** | **Read 43/44 mechanically** against W151 (3)/(4):<br>- both displays and each ledger L_hi with its insertion-gate text;<br>- the table outcome;<br>- whether the letter came before or after the scores;<br>- the pair.<br>Push the result. **No new submit whatever the scores show (FREEZE).** If the pair changes, the user re-ticks by 29 Sep 20:00Z and SELECTED is re-read | not started | `round15/report.json` R15-A5; `experiments/lb_poll/ledger.md` (43/44 rows) |
| W156a / FREEZE (standing once W151 is logged) | until 29 Sep 23:59 | No DC rung (0.175, 0.15, ...), no DC / fm45 / lp30 combo on a DC base, no other ladder submit, no exp70m. Slot order: E10 port > unchanged resubmit of an ERRORed finals-relevant file (never class C) > exp72 (yes only) > empty | pending W151 | `round15/report.json` R15-A1 (2), rejected |
| W19 / W73 | until **29 Sep 20:00** | ONE poller (PID 20052). Before any submit, the last successful header must be < 15 min old and not a 429 (244 polls, 0 gaps > 15 min at 06:00Z) | in progress | `experiments/lb_poll/ledger.md` l.6 |
| W102 / W93 | standing | Protect the finals' inputs. Never push or submit exp65 / exp66, exp70g, exp71, exp70j/k again, or the dry-run kernel | standing | `CONTEXT.md` l.2223-2226, l.2249-2252 |
| T68 | **06:31Z** | Liveness timer cdd738f1 | - | CronList |
| T65 | **06:45Z** | Quiet window ends; SELECTED is read at 07:30Z (W153); E10 P1 resumes | - | `CONTEXT.md` l.2774-2775 |
| T44 | **07:30Z** | Morning push (W136, R15-A2 form) | timer alive | CronList 65b1b746 |
| T57 | **~07:27-08:30Z**; 08:05:50Z / **09:05:50Z** | Probe 42 event, then D2; the watcher exits | - | `round15/report.json` R15-A4 |
| T71 (new) | **~08:00-08:45Z** | Round 16 | - | `round15/report.json` next_focus |
| T58 | **~09:00Z** | Last useful user yes for exp71 (27 Sep exp72 score); last SI opt-in | - | `CONTEXT.md` l.2543 |
| T56 | **11:30Z** | Watcher hard cap (moot if exp70b is terminal earlier) | - | `CONTEXT.md` l.2755-2757 |
| **T72** (new) | **11:45Z** | **Hard deadline for W151** (and W152) | - | `round15/report.json` R15-A1 deadline |
| T03 | **12:00Z** | R8 cutoff, E10 v2 lapse, the class-C answer asked for by then, W98 | - | see W157 |
| **T73** (new) | **~12:15-12:20Z earliest**; ~12:20-13:10Z expected | 43/44 terminal. A letter after the first terminal header is post-hoc | - | `round15/report.json` plan_issues (12) |
| T74 (new) | **~13:00-14:30Z** | Round 17 (audit the 43/44 read) | - | `round15/report.json` next_focus |
| T66 | from **12:00Z** | Curator edits W147 (+ R15-A8) and the W148 hindsight commit may start | - | `round14/report.json` next_focus |
| T32 / T39 | 27 Sep 09:04, 12:04, 15:04, 18:04, 21:04 | E10 P1 checks (timer 2e87e414) | timer alive | CronList |
| T18 / T42 | **28 Sep 00:00** | Slot reset: 5 slots for 28 Sep; 1 kept for a port | - | `CONTEXT.md` l.2704-2710 |
| T67 | standing | **All timers are session-only.** If the session restarts, recreate 65b1b746, 2e87e414, 012fa6dd, 328f7392, 18ff4796, bb224de9 (and cdd738f1 if before 06:31Z) | - | CronList "[session-only]" |

## LATER (28 Sep 06:10 -> 29 Sep 23:59 UTC, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T59 | **28 Sep 02:00** | Hard edge for any combo submit. Moot: BASE = none. It still applies to an ERROR resubmit or exp72 (Q6 asks the user for 02:00Z vs 11:00Z 29 Sep) | `CONTEXT.md` l.2793; `round15/report.json` R15-A2 §5 Q6 |
| T32 / T39 (cont.) | 28 Sep 00:04 ... 21:04 every 3 h; the last useful one 29 Sep 00:04 | E10 P1 checks | `CONTEXT.md` l.2530-2531 |
| T46 | **28 Sep 12:00** | **F1 consolidation** under R8 | `CONTEXT.md` l.1671, l.2708-2709 |
| T28 | 28 Sep | S14: an x138 successor on a late trigger (P7) | `CONTEXT.md` l.1616 |
| T19 / W77 | **28 Sep 17:57** (timer 012fa6dd) | API SELECTED + the first logged page read of the ticks | CronList |
| T35 | 28 Sep 22:00 | The final admission table = the L9 eligibility table for every ladder variant + the class-C rows (43/44) + exp72 if Q3 = yes | `research/wf_ideas_v3/FINAL_REPORT.md` l.178; `round15/report.json` R15-A1 (4) |
| T20 | **29 Sep 00:00** | The last slot reset and the last useful E10 trigger | `CONTEXT.md` l.2355, l.2708 |
| T29 / T47 | **29 Sep 02:00** | The last E10 port submit and the last submit under R8 (unless the user picks 11:00Z in Q6) | `CONTEXT.md` l.2709 |
| T60 (= W135 G2) | **29 Sep 12:00** | G2 must have landed for exp72 to be finals-eligible (Q3 = yes only) | `CONTEXT.md` l.2736 |
| T09 / W77 | **29 Sep 11:57** (328f7392, push) / **17:57** (18ff4796) | Remind the user to check or re-tick; API SELECTED. The brief asks the user to set their own alarms at 12:00Z and 18:00Z (I159) | CronList; `round15/report.json` R15-A2 §6 |
| T48 (= W131) | **29 Sep ~19:00** | **L9 read** (re-read on every new score), including the class-C table if the user allowed (b) / (c). Never two byte-identical files; never a non-COMPLETE file. Tell the user the exact two refs | `CONTEXT.md` l.2510-2518, l.2758-2763; `round15/report.json` R15-A1 (4) |
| T10 | **29 Sep 20:00** | Ticks final: exactly 2 files; without a re-tick {#37, #38} stays. **Stop the poller** | `CONTEXT.md` l.2515-2516, l.2620 |
| **W148** (= R14-A8) | **before 29 Sep 23:00Z** | Hindsight guard: ONE text-only commit as the user, pushed (LESSONS s3 item 11 + "do not rewrite after the private LB") | `round14/report.json` R14-A8 |
| T49 | **29 Sep 23:00-23:45** (timer bb224de9 at 23:27) | Final public LB snapshot to `experiments/private_read/` | `CONTEXT.md` l.2580-2588; CronList |
| T11 | 29 Sep 23:59 | Competition deadline. A submit must **finish** before it to count (participant comment only) | `round14/report.json` new_facts (6) |
| T30 / T50 | **30 Sep from 00:15Z, hourly** | Private read per v2 (d) + the ladder addendum L1-L5 + **L6/L7 and the DC-DOSE read** (added by W151 (7)); rank over the SELECTED pair | `CONTEXT.md` l.2570-2598, l.2711; `round15/report.json` R15-A1 (7) |
| **W147** (= R14-A7 + R13-A6 + R12-A10 + **R15-A8**) | s3 item 11 **before the first private score**; the rest **by 30 Sep**; I-252 after 29 Sep | Curator edits:<br>- IDEAS I-106, I-063, I-069, and **I-297/I-298 (the {V*, #38} shape is dominated for a high-variance knob)**;<br>- **I-252 sentence (fork-removal riders 0 for 6)**;<br>- **"division knobs invisible on public" is WRONG for DC**;<br>- **I-018 DC band**;<br>- the post-deadline "DC sensitivity per embryo" item;<br>- LESSONS 12th-16th, etc. | `round14/report.json` R14-A7; `round15/report.json` R15-A8 |
| W29 | after 29 Sep | Post-deadline list (rounds 10-15, + DC threshold sensitivity per embryo) | `round15/report.json` R15-A8 (4) |

**Done, superseded or moot since 02:25Z (for the record):**
- W134 (R14-A1): watcher launched 03:35Z, PID 10088, S0 = S0-20260927T0147Z, three events (`CONTEXT.md` l.2790; `ladder_watch/watch.log`).
- W143 (R14-A2): ROUND 14 PRE-SCORE NOTES at `CONTEXT.md` l.2750-2775, committed in 8155321 (02:28:56Z) before the first COMPLETE header (04:20:02Z, `ledger.md`). It is pushed (origin/main = da9766e); the exact push time is not verified by this curator.
- W144 (R14-A0): `research/wf_ideas_v4/round14/REPORT.md` is tracked (8155321).
- W141 D1: `CONTEXT.md` l.2789-2799 (row D1-3; no re-tick). The D1 audit is clean (`round15/scan_plancheck.notes.md`).
- W145: timers 5b23a3ed / 54a8f20d / cdd738f1 created (`CONTEXT.md` l.2786).
- Moot:
  - the A-only extension (exp70a NEU);
  - T52 / T53 / T54 / T62 / T63 / T64 (passed);
  - I141 (exp70a L (6.87, 7.04] h, far from 8.0 h).
- W137 residue -> W153. The W136 R14-A4 variants -> R15-A2.
- Earlier records: `_curation/14/watch.json`, `_curation/13/watch.json`.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I149** (new) | "#38 = X + eps, and eps may be exactly 0 on private (lowrefine moves 12 nodes, none near GT, F-MOD-17) ... With eps > 0, #38 hedges an insertion failure; with eps <= 0 it does not". "Above ~380 copies, #38 lands no higher than in half the worlds ... it ties with the copies and loses to them on submission time" | `round15/report.json` R15-A1 (4), R15-A2 §3, new_facts (11); `round15/scan_hyp_finals_public.notes.md` | This undercuts the core reason for #38 in the ticked pair. It is queued only as an IDEAS edit by 30 Sep (R15-A8 (1)). **It should be weighed at the 29 Sep ~19:00Z L9 read, not after the private LB** |
| **I150** (new) | "E[score] favours a DC-diverse F2 iff E[D+] > E[I-] (~0.06e-3) - i.e. almost always when sigma_D is large. But block-step utility P(max > X138): ~0.94 vs ~0.89 => keep #38" | `round15/scan_recheck.notes.md` ("emax recheck") | The finals pair depends on WHICH utility is used (expected score vs clearing the x138 block). CONTEXT never states the utility choice explicitly. The R15-A6 (7) record keeps only the block-step numbers |
| **I151** (new) | Lab: "dc0.35: ... 6bba 10/6/78 -> 6 TP lost -> lab TP cluster sits in [0.30,0.35)"; "SHIFT(-0.05) hypothesis explains all 3 public facts"; "r_ladder L2 already foresaw 'on a shifted embryo 0.30 acts like 0.35'" | `round15/scan_hyp_div_sensitivity.notes.md` | The judge demoted SHIFT to a post-hoc fit (NARROW ~0.6 / BROAD ~0.4). The lab-cluster fact itself appears only here. Relevant to the post-deadline "DC per embryo" item (W29) |
| **I152** (new) | "E10 path is not bound by R8 (round-13 record (6)), so the browser's 'post-deadline because of R8' reason is wrong" | `round15/report.notes.md`; `round15/report.json` plan_issues (11) | After 12:00Z the E10 port is the only mechanism path left. A round agent misread it once; P3 is the real blocker for amanatar V6 |
| **I153** (new) | "tracked() includes refs > 56563534 ... it exits after the 4 WATCHED refs are terminal (exp70b) -> run_ladder_watch.sh 'until' loop ends on rc 0" | `round15/scan_plancheck.notes.md` | After ~08:30Z nothing but poll.log (10-min bins) records 43/44; the L_hi for 43/44 comes from the ledger only (T70) |
| **I154** (new) | "probe.json 'rule' field is builder boilerplate 'above exp56 adopt' in all exp70* (cosmetic; contradicts class C)" | `round15/scan_plancheck.notes.md`; `round15/report.json` R15-A6 (3) | A tired finals read at 29 Sep 19:00Z could read exp70j/k as "adopt". Fix with W126 |
| **I155** (new) | "Cap 4 binds nearly everywhere (I-220) => DIVINS_THRESH 0.4 -> 0.3 nearly inert"; "cap6 adds <= ~6 dummy forks => public <= +0.0009 upper, central ~0" | `round15/scan_hyp_div_sensitivity.notes.md`; `round15/scan_recheck.notes.md` | This closes the insertion-knob family for good (R15-A6 (8)). Guards against a late cap/threshold rung |
| **I156** (new) | "D (and the per-event unit) is prior-driven, not identified by the two displays"; "public ~58 clips -> G ~21-57"; "unit = 1-5 display thousandths per TP (median ~2)" | `round15/v_hyp_div_sensitivity_r15ds-1.notes.md` | The "~0.0015-0.0023 per TP" figure in W151 (3) is a MODEL ESTIMATE. It must never be quoted as a fact in the brief |
| **I157** (new) | "Safe divisions run BEFORE the DaughterNet insertion (l.4607 vs l.4693); insertion uses orphans only (+steal) ... no DeepCenter in the insertion gate" | `round15/scan_hyp_div_sensitivity.notes.md` (exp70j notebook l.4087-4210) | A DC change can change the orphan pool of the insertion. divins_added = 12 in all four dummies (R15-A6 (3)), so there is no dummy effect; the private-side interaction is unmeasured (cf. I110/I111) |
| **I158** (new; updates I146) | "Silver 5% = 197.05"; bronze "~#394 lies inside" the 0.953 block (342-723, 382 teams); we are #256; ">= 0.955: 239 (+13 in 3.7 h)"; "Timass 0.951->0.960 (#725->#66)" with no public source | `round15/scan_browser.notes.md`; `round15/report.json` new_facts (3) | Info only. A private fall into the x138-copy block would put us among ~380 copies around the bronze line (see I149) |
| **I159** (new) | CronList at 06:0xZ still lists the one-shot timers **5b23a3ed (04:21Z) and 54a8f20d (05:21Z)**, and no liveness result is logged in CONTEXT | CronList (this curator); `CONTEXT.md` l.2786 | Either the listing lags, or session-only timers do not fire while the main session is busy. That puts the 07:30Z push and the 29 Sep tick checks at risk. The R15-A2 brief asks the user to set their own alarms for 29 Sep 12:00Z / 18:00Z |
| **I160** (new) | "sjlee forks dctta020-sectta1 0.947, dctta025-sectta1 0.947, v015 0.946 ... flat 0.15-0.25 on the older lf stack; our x138 K2 0.25->0.30 = -0.005. Asymmetric: cliff above 0.25, plateau below" | `round15/scan_recheck.notes.md`; `CONTEXT.md` l.698-710 | It is the evidence behind the lower 43/44 prior. It enters CONTEXT only via W151 (5) |
| I142 (still at risk) | "+0.006 is the exp60 IN-SAMPLE number ... honest ... +0.0019 ... P(<0) 0.10-0.20" | `round14/report.json` new_facts (12) | It is now in the R15-A2 brief §3, but not in CONTEXT until W146 |
| I143 | FT weights on public stacks "0/4 on the LB"; the exp72 setup is untested; E ~0 | `round14/report.json` new_facts (13); `round15/report.json` R15-A2 §5 | The honest prior for Q1-Q3 |
| I136 | FOCUS_NOTE reaches only the plancheck scan; the browser scan runs `e10_snapshot.py` first | `experiments/workflows/biohub-research-round.js` l.35-38 | It materialised at 05:31Z (W150) |
| I144 | amanatar "Version 1 of 6" renumbering; the lineage failed P3/P4b | `round14/report.json` new_facts (2) | Now V6 COMPLETE, ~9 knobs + 2 code blocks (`round15/report.json` new_facts (2)) |
| I145 | "It has to finish before the deadline to count" (participant, no host answer) | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 | Matters for Q6 (an 11:00Z 29 Sep edge still has to finish) |
| I148 | Other teams' < 3.3 h latency says nothing about our ~7.4 h runs | `round14/report.json` new_facts (4) | - |
| I130 | exp71 has no SECFT_PREFIX; G2 needs a second ~4 GPU-h run | `round13/v_plancheck_pc13-05.json`; `CONTEXT.md` l.2736 | Only if Q3 = yes |
| I131 / I132 | Unrounded order inside a display block; a 1-sub newcomer at 0.955 means a finished recipe exists | `round13/scan_browser.json` | Round 15: "Jackson Bom + KHitomi 0.953->0.954 (in-block above us)" (`round15/scan_browser.notes.md`) |
| I110 / I111 | lp30 x lowrefine are non-additive; the dc x insertion interaction is unmeasured | `reach0955/v_ladder.json` | See I157 |
| I114 | "x138 cell 1 = configuration guard: BIOHUB_DET_THRESHOLD must equal 0.965 ... else RuntimeError" | `reach0955/v_intel.notes.md` | Not in CONTEXT; matters for any E10 port of a DET 0.960 fork (amanatar V6) |
| I116 | Agents label local (UTC+3) times as "Z"; cron hours are local | `reach0955/discussions_2026-09-26.notes.md` | CronList "30 10 27 9" = 07:30Z |
| I72 | The harness asks for a Co-Authored-By trailer; the user's rule forbids it | `memory/feedback-git-no-coauthor.md` | Keep for W151 / W148 (the last 8 commits have 0 trailers) |
| I95 | The harness has refused the round-report Write 8 rounds running (8-15) | `round15/report.notes.md` | W152 |
| I96, I97-I106, I88/I89, I69, I77-I83, I47, I51, I39, I44, I01-I76 | Older insights, unchanged | `_curation/14/watch.json`, `_curation/11/watch.json` | See the W57 family, W98 |

**Resolved since 02:25Z (now in CONTEXT):**
- I139 (S0 = 0147Z): `CONTEXT.md` l.2752-2755.
- I140 (fm45 POS reading): l.2765-2766.
- I147 (tie order, cap rule, one re-tick): l.2764, l.2769-2770, l.2779-2780.
- I137 (agents read watch.log / calls.jsonl only): l.2758-2759.
- I138 (latency / timing): overtaken by the actual events (04:13 / 04:31 / 04:56Z).
- Details: `_curation/14/watch.json`.
