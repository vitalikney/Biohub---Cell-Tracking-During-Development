# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~03:50 UTC (curation 32). This updates the curation-31 build of 29 Sep ~02:55Z. That build is committed in a9ac9ee, and a structured copy is in `research/KNOWLEDGE/_curation/31/watch.json`. Older predecessors run from `_curation/30/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** it now has 4,333 lines, and `## 9. Literature` starts at l.4313. There is one new entry since curation 31: l.4294-4312 (**02:53Z, A-M2 FUNCTION + 08:40Z HEADER + ROUND SCHEDULE + CARD POOL L**, R31-A1).
- **`git log`:** **a9ac9ee** (02:53Z) committed round 31, curation 31 and the card v5 pool-L edit.
- **`research/wf_ideas_v4/round32/`:** untracked, written 03:13-03:45Z. Read:
  - `report.json`, which holds **R32-A1..A4**, new_facts (1)-(6), plan_issues (a)-(e), the rejected items, next_focus and report_md_ru;
  - `report.notes.md`;
  - the `scan_*.notes.md` files and `v_plancheck_pc32-05.notes.md` / `v_recheck_r32-rc-b-*.notes.md`.
  - **There is no `REPORT.md`**, because the harness blocked it; the Russian text is in `report.json` report_md_ru.
- **`experiments/lb_poll/poll.log`:** the newest header is **03:34:22Z** (l.27949). In it, 56656147, 56656157 and 56657612 are PENDING, and 56640366 is COMPLETE 0.959.
- **Loops:**
  - `experiments/e10_watch/watch_loop.log`: RUN 39 at 03:42:06Z, signals 0, next 04:41:53Z.
  - `experiments/discussions/feed_loop.log`: 02:28:02Z, 0 new, E10 FLAG none.
  - `experiments/e10_watch/20260929T0341Z.txt` l.272: us #132, 0.959, count 53.
- **Local read-only checks at ~03:45Z:**
  - Card v5 sha8 = **a134d5e4**, which equals `CONTEXT.md` l.4309.
  - Armed timers due 04:00-05:59Z: only 04:13Z ("HOURLY RESEARCH ROUND ... launch the next research round") and 05:13Z. **There is no 04:10Z push timer.** BatteryStatus is 2 (AC).
  - `grep -c` on CONTEXT.md returns 0 for each of: DET_THRESHOLD, int-casting, "cron defect", I-045. "battery standby" still returns 1.
  - `experiments/RESULTS.md` probe rows still end at probe 46 (l.79).
  - `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66 still reads "OUR = 0.957 ... SC >= 0.958".
  - The `REPORT.md` files for rounds 29, 30, 31 and 32 are all absent.

All times are UTC; the user thinks in MSK, which is UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W is an action, T a time-bound reminder, I an insight. Status values are: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~03:45Z, 29 Sep:**
- **Best display: 0.959**, from exp87a (probe 51, 56640366). V_pub = exp87a, the running champion under the conservative reading (`CONTEXT.md` l.4278-4285).
- **Rank** at 03:13Z: #132 of 3,980, 17th of 21 in the 0.959 block, with 115 teams at >= 0.960 (`round32/report.json` new_facts (3)).
- **Medal lines**, in the same blocks as at 02:14Z:
  - silver is at about #199, inside the 0.957 block (157-206);
  - bronze is at about #398, inside the 0.955 block (328-435).
- **Night submissions, all PENDING at 03:34:22Z.** Revised expected reads (`round32/report.json` new_facts (4)):
  - 54 exp89p ~07:47-07:58Z;
  - 53 exp75 ~09:03-09:49Z;
  - 52 exp89r ~09:23-09:34Z.
- **Slots:** 2 left on 29 Sep, for A-M1 (exp89l) and A-M2 (exp89s / exp89q).
- **User:** asleep, autonomous mode. The session never ticks.
- **CRITICAL (new):** the R31-A2 power push has **no waiter** (W309 = R32-A1). It must be armed **by 04:09Z** and sent at 04:10-04:13Z, before the user's 05:10Z trip.

**Changes since ~02:55Z (curation 31):**
- **Done:** **W304 = R31-A1**, logged at 02:53Z (`CONTEXT.md` l.4294-4312) with pre-score header 02:44:13Z:
  - (1) the A-M2 function, with grid rows d_R = 0.959 / <= 0.958 -> UNUSED;
  - (2) the 08:40Z header = the last header <= 08:40:36Z, plus the 08:30Z manual-A-M1 waiter;
  - (4) card pool L <= 9.0 h, with the new card sha8 **a134d5e4**;
  - (5) the R31-A2 push and the R31-A3 read-time L logging.
- **Not adopted:** **W304 (3), the round pause.** Hourly rounds continue as background workflows (l.4305-4308). T189 is therefore **superseded**.
- **Not folded in:** W279 (1) DET_THRESHOLD and W297 "battery standby", which remain open.
- **W303:** round 31 is committed (a9ac9ee). Round 32 is untracked.
- **Resolved insights:**
  - I358: the A-M2 bullet, fixed by l.4295-4301.
  - I359: the 08:40Z header, defined in l.4302-4305.
- **New:**
  - actions **W309-W313** (R32-A1..A4 and R32 plan_issue (d));
  - reminders **T192-T194**;
  - insights **I366-I373**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W309** (new; = **R32-A1**, supersedes the delivery part of T188 / W305) | **ARM THE R31-A2 POWER PUSH.** <br>(1) By 04:09Z: one run_in_background timer.sh at **2026-09-29T04:10:00Z** with the text "SEND R31-A2 POWER PUSH NOW ... THEN launch round 33". <br>(2) At 04:10-04:13Z: ONE PushNotification with the verbatim Russian text of R32-A1 (2): results from ~10:38 MSK; A-M1 by 11:45; A-M2 by 14:30; card at 15:03; charger + lid open; "if offline by ~11:40, A-M1 simply unused". <br>(3) Log "04:1xZ R31-A2 push sent" in CONTEXT, then launch round 33. **If read after 04:10Z, push at once, before round 33.** Do not ask the user to tick | **not started / due now**: at ~03:45Z the only armed timers before 06:00Z are 04:13Z (round only) and 05:13Z; CONTEXT has no push line | **Arm by 04:09Z (07:09 MSK). Send by 04:13Z**, and in any case before the 05:10Z trip | `research/wf_ideas_v4/round32/report.json` R32-A1, plan_issues (a); `round32/scan_plancheck.notes.md` 04:13Z line; `CONTEXT.md` l.4309-4311 |
| W126 (part 2) | Add RESULTS.md rows for probes **47 (0.955), 48 (0.957), 49 (0.955), 50 (0.958) and 51 (0.959, UP 12)**, then the night probes 52-54 and the morning probes | **overdue**: probe rows still end at 46 (l.79) | before the finals card (29 Sep 12:03Z) | `experiments/RESULTS.md` l.79; `CONTEXT.md` l.4153-4160, l.4255-4272 |
| W296 + W303 (updated) | Write REPORT.md for **rounds 29, 30, 31 and 32**. Rounds 30-32 must be copied verbatim from `report.json` (report_md_ru / next_focus), because the harness blocked the writes. **Commit round 32** (untracked) with named paths, as the user, with no Co-Authored-By | rounds 29-31 are committed (a9ac9ee for 31); all 4 REPORT.md files are absent; round 32 is untracked | with the next CONTEXT commit (the W309 push line) | `round32/report.json` next_focus NOTE; `git status` (`?? research/wf_ideas_v4/round32/`); `memory/feedback-git-no-coauthor.md` |
| W286 (updated) | **(1)** Add a CONTEXT line: floatout probes 32/33 were no-ops under an int-casting scorer. **(2)** Fix `e10v3/runbook.notes.md` l.66 to "OUR = 0.959 (exp87a), so SC >= 0.960". CONTEXT l.4159-4160 already has the right trigger | (1)(2) **overdue**: `grep int-casting` = 0; l.66 unchanged at ~03:45Z; the E10 03:41Z read has passed | (2) before the next E10 read (04:41Z); (1) low | `round28/report.json` R28-A6; `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66 |
| W279 (1) | Log RC-C: "DET_THRESHOLD stays closed for 29 Sep and is never a morning filler" | not started (not in 02:02Z or 02:53Z; `grep -c DET_THRESHOLD CONTEXT.md` = 0) | before **07:23Z**; fold it into the W309 CONTEXT line | `round27/report.json` R27-A9 (1) |
| W297 | CONTEXT still blames "a busy session / battery standby" for the lost rounds. The cause was the cron defect (round 28). Fold a one-line correction into the next entry | not started (`grep -c "cron defect"` = 0) | with W309; low | `round28/report.json` new_facts 5; `CONTEXT.md` l.4096 |
| W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 | Old info and curator lines; the ROUND RECORD; LESSONS H1; no NEVER_SUBMIT in exp70j/exp70k; old text fixes | overdue, low | H2, 29 Sep 23:00Z | `_curation/24/watch.json`, `_curation/26/watch.json` |

## NEXT 24 H (29 Sep ~03:45Z -> 23:59Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W309 | **04:09Z arm / 04:10-04:13Z send** | The power push (above) | not started | R32-A1 |
| T181 + T187 (updated) + **W313** (new; = R32 plan_issue (d)) | **04:13Z** round 33; 05:13Z (may fire late: laptop asleep on the trip); 06:13Z onward, hourly | Rounds stay **light, with no new mechanisms** (R8; both slots reserved). They run as background workflows (l.4305-4308). **Round 33 first checks that the W309 push went out.** Read-only LB / E10 / feed. Only a disclosure with values from a team at >= 0.959, or a public notebook >= 0.960, is actionable, and then only dummy + the user's yes + submit by ~10:00Z. **W313:** drop the recheck lens, or restrict it to claims printed on card v5 (94 items rechecked; the last one that changed a submit was R20-RC-A). Pre-stage the 12:03Z card values (W307) | pending | `round32/report.json` next_focus, plan_issues (d); `CONTEXT.md` l.1671 (R8), l.4305-4308 |
| T189 | 07:13-10:13Z timers | "Read-only rounds of <= 5 min" | **superseded**: R31-A1 (3) NOT ADOPTED; full rounds continue, but decision steps take precedence and a report that lands during a decision step is read after it | `CONTEXT.md` l.4305-4308 |
| T100 (updated) | E10 hourly at hh:41Z until **12:00Z** (next 04:41Z); feed every 90 min (next ~03:58Z) until 23:59Z | The E10 v3 trigger is **>= 0.960** (l.4159-4160). **After 02:00Z, a copy needs:** a >= 0.960 notebook, a PASSED dummy, the user's yes, and a submit by ~10:00Z. Non-CI T_last is ~10:25-10:30Z; CI T_last is ~08:05Z. A notebook first seen after ~09:30Z is information only (T192) | live (RUN 39 03:42Z; feed 02:28Z) | `experiments/e10_watch/watch_loop.log`; `round32/report.json` new_facts (5) |
| T173 | **05:10-06:00Z** (08:10-09:00 MSK) | The user travels and the laptop sleeps. timer.sh fires on wake. The watchdog 10576 and the read watchers are one-shot | info | `CONTEXT.md` l.4066-4072 |
| T174 + W301 + **T193** (new) | **06:07Z** post-wake (09:07 MSK) | Check AC, poll-header age and loops. **If BatteryStatus != 2, re-push and re-arm a battery-tolerant watchdog** (notifies only on a header > 25 min old). Chain read watchers on the remaining refs, plus one per morning submit ref (W294). **T193:** a header can be written up to ~630 s after its own timestamp, so **do not kill a live lb_poll.py within ~11 min of the wake**; restart at once only if no lb_poll.py is alive. PC32-05's "post-wake lag" was refuted | pending | `CONTEXT.md` l.4309-4312; `round32/report.json` rejected (PC32-05); `round32/v_plancheck_pc32-05.notes.md` |
| W302 (4) | 06:07-07:23Z | First MSK message: "Both morning slots may end UNUSED by rule; that is expected. exp89t/exp89u stay off unless you say yes" | pending | `round30/report.json` R30-A5 (4) |
| T151 + W299 + **W311** (new; = **R32-A3** (a)) | **07:23Z** prep (10:23 MSK) | **The timer text "build/dummy exp89l ... P +/0u" is only a pointer.** Do NOT rebuild or re-push exp89l / exp89s / exp89q: submit `-v 1`, the gated dummy (exp89l cad1d47f, CSV 2c1868375972). Re-run G5. Paste the grid + commands from R30-A2 **with the A-M2 bullets replaced by the 02:53Z (1) function**. Log the pending L lower bounds (W306) | pending | `round32/report.json` R32-A3 (a); `CONTEXT.md` l.4291-4301 |
| T159 / T182 + W306 (updated) | **exp89p ~07:47-07:58Z** (A-M1 limit 08:40:36Z, margin ~0.7 h); exp75 ~09:03-09:49Z; exp89r ~09:23-09:34Z | **Night reads:** P = exp89p vs exp85a 0.958 (P '+' only at >= 0.959). Rr = exp89r vs exp87a 0.959 (Rr '+' only at >= 0.960). exp75 vs #37 0.954 (partner rule v2). DIS per R26-A2 (1). At each first terminal header, log the L interval next to the family range (non-CI 6.87-7.81 h, CI 9.27-9.48 h). Log KEY FACTS + RESULTS (W126). **exp75 and exp89r may land in one 30-min e10 window: the +2 rule gives the UP to the higher display, and equal displays are both MASKED** | pending (all PENDING at 03:34:22Z) | `round32/report.json` new_facts (4); `CONTEXT.md` l.3124-3126, l.4294-4312 |
| W300 + **W310** (new; = **R32-A2**) | at each terminal header, ~07:47-11:00Z, and before the 12:03Z card | **UP test, 0 API calls.** <br>- **A-M1 needs none**: P comes from exp89p's display alone. <br>- **An UP test is needed only for V_pub at a 0.959 display** (exp89p or exp89r). exp89r >= 0.960 wins on display; exp75 < 0.959 needs no test. <br>- **Method:** S0 = the newest `experiments/e10_watch/<TS>.txt` before the terminal header with count 53; S1 = the first one after it with count +1. Extract `leaderboard_rows` with awk into `experiments/lb_poll/_lb/<TS>/lb.csv`, then run `python tools/uptest.py compare <TS0> <TS1>`. <br>- **A fresh download** is allowed only when no suitable snapshot exists (after 12:00Z, or stale > 75 min), and only as `timeout 180 python tools/uptest.py save <tag>`. **Never run it bare.** Do not edit uptest.py today. <br>- **Budget:** <= 3 LB calls | pending; the procedure is **not yet in CONTEXT** (report only) | `round32/report.json` R32-A2, plan_issues (b); `tools/uptest.py` l.34-36; `round30/report.json` R30-A3 |
| T151 A-M1 / T183 + T190 (updated) + W311 (b) | first header with 56657612 terminal; **the 08:40Z header** (last header <= 08:40:36Z); submit by **08:45Z** (11:45 MSK) | **A-M1:** d_P >= 0.959, COMPLETE -> `nb_try exp89l $KL "$M55L"`; anything else -> UNUSED. **The 08:30Z timer text "decide now ... missing read = UNUSED" is overridden:** if 56657612 is still PENDING, arm ONE background waiter for a single list at 08:40:00Z inside a timeout, tagged `=== <UTC> [manual-A-M1]` in poll.log. If exp89p is COMPLETE at >= 0.959 there, submit exp89l at once. **If exp89p is still PENDING at 08:10Z, expect this path** | pending (rule logged l.4302-4305) | `CONTEXT.md` l.4274-4277, l.4302-4305; `round32/report.json` R32-A3 (b), new_facts (4) |
| T151 A-M2 / T184 (updated) | first header with 56656147 terminal; **latest 11:00Z header, submit by 11:30Z** (14:30 MSK); 11:10Z timer | **Use the 02:53Z (1) function:** <br>- DIS '+' -> exp89s. <br>- Else, if Rr '+' (d_R >= 0.960, COMPLETE, terminal + 210 s x f <= 10:50:28Z): DIS '-' -> UNUSED; DIS '?' -> exp89q iff P is '+' or '?'. <br>- Everything else -> UNUSED, including d_R = 0.959. <br>P is read at the A-M2 header, and GAP RULE v2 applies | pending | `CONTEXT.md` l.4295-4301 |
| T180 / W294 | at each morning submit | Start a late-read watcher per morning ref. exp89l sent at 08:45Z reads ~18:03-18:15Z; an M2 non-CI file sent at 11:30Z reads by ~19:20Z | pending | `round29/report.json` R29-A7 |
| W19 / W73 / W102 / W93 / W165b / W261 | standing | ONE poller; header < 15 min old; never resubmit class C or ERRORed files. SEC may be a final only as V_pub (Q3). Dataset pre-push check. Every Kaggle call is wrapped in a timeout (freeze (7); see W310) | standing | `CONTEXT.md` l.3331-3335, l.3692-3703, l.4112-4114 |
| T186 | **11:41Z** last E10 snapshot; the E10 loop exits at 12:00Z | Take RANK, block position and medal-line ranks (W307 (3)) for the 12:03Z card from the 11:41Z snapshot. That snapshot is also the last free S1 for W310 | pending | `round30/report.json` R30-A4 (c) |
| T191 | ~11:10-11:30Z, the tail of the 11:10Z timer | The first substantive round runs after A-M2 is submitted or logged UNUSED. It checks the card fill against P / Rr / DIS / exp75 partner rule v2 and the running-champion V_pub | pending | `round32/report.json` next_focus |
| W266 (2) / T60 / W302 (1)(3) + W307 + W311 (c) | **12:03Z** (15:03 MSK), timer | **The timer names card v4; fill card v5** `research/wf_ideas_v4/round29/finals_card_v5_ru.md` (**sha8 a134d5e4**). <br>**W307 numbers (V_pub exp87a):** <br>- П2 {exp87a, exp75}: bronze ~0.63-0.85 / silver ~0.43-0.68; <br>- П3 {exp87a, #37}: ~0.61-0.83 / ~0.39-0.64; <br>- the ticked {#37, #38}: bronze 0.20-0.58 (base 0.38) / silver 0.02-0.16; <br>- the silver caveat for {V_pub, exp85a}; <br>- medal-line ranks (03:13Z pre-stage: S ~#199 in 0.957, B ~#398 in 0.955; refresh from 11:41Z). <br>**Optional (W311 (c)):** replace the dead cron ids 2e9ce42e / ec670938 / 64b9bb56 / ddc5884d at card v5 l.93 / l.138 / l.152 with "timer.sh 12:03Z / 18:37Z / 19:43Z / 21:05Z", and record the new sha8. **Never "не медаль" or "рекомендую".** Send only the ===== block; never tick | pending | `round32/report.json` R32-A3 (c), new_facts (3); `round31/report.json` R31-A4; `CONTEXT.md` l.4308-4309 |
| W308 | any free slot after the morning decisions; post-deadline is acceptable | Curator note on **I-045**: "WEAKENED on public by CI; stays closed; post-deadline only". Never write "overturned" | not started (`grep -c I-045 CONTEXT.md` = 0) | `round31/report.json` R31-A5 |

## LATER (29 Sep ~12:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T152 + W302 (2) + W307 (5) | **18:37Z** (21:37 MSK), timer | FINAL proposal from card v5: "the pair by the card", **never "рекомендую"**. **If V_pub changed** (a later file at >= 0.960, or with an attributable UP at 0.959 per W310), re-run `scratchpad/r31v/mc31v.py` with the new VPUB. Pre-stage the command for each possible V_pub (exp87a / exp89r / exp89p). List the still-PENDING files with MSK windows | `round31/report.json` R31-A4 (5); `round32/report.json` next_focus (3) |
| T161 | **19:43Z** (22:43 MSK), timer | Notify-only reminder + V_pub re-check. **Any read after ~19:30Z cannot be a final** | `CONTEXT.md` l.3685, l.4054-4056 |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** The session never ticks. If the user does nothing, #37 + #38 stay; the ticked pair's modelled bronze is only ~0.38 at base (W307) | `CONTEXT.md` l.3851-3855, l.4091-4092 |
| T153 | ~20:00-20:30Z | Verify that API SELECTED = the user's pair | `CONTEXT.md` l.3474 |
| T162 | **21:05Z** (00:05 MSK 30 Sep), timer | Last-call notify: if SELECTED is not the proposed pair, push the exact pair | `CONTEXT.md` l.4092, l.4099 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; final public LB snapshot | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline: a submit must **finish** before it; re-ticks are allowed until then | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765; `CONTEXT.md` l.3848, l.3855 |
| T155 | 30 Sep 00:07Z, timer (armed) | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715, l.4131 |
| **W312** (new; = **R32-A4**) | any free slot after the 20:00Z tick; post-deadline is acceptable | **Curator note: post-deadline division agenda** (idea base, not a CONTEXT rule). <br>- Lab exp60 control: 85 FN of 97 two-daughter GT divisions. 72 of these have the parent + both daughters matched: claimed 34-35 / orphan 27 / merged 8 / other 2. <br>- Order: (a) a theft-aware relink-stage ranker on graph features for claimed daughters; (b) a linajea-style parent-vector head only as a secondary variant (DaughterNet scores 3/35); (c) the merged class under detector retraining (the splitter = closed mirror/lowdet); (d) insert-before-short-filter, ceiling <= +0.0023 lab, low priority. <br>No build, no slot | `round32/report.json` R32-A4, rejected (RC-B, RC-C wording) |
| W295 | next CONTEXT entry / curation pass | The 744093 integer check covers every finals candidate; an I-320 narrow annotation; do not publish the "5/14" class table | `round29/report.json` R29-A8 |
| T133 / T170 | 3 Oct | GPU quota refresh (about 2.7 h left) | `CONTEXT.md` l.4239-4241 |
| W29 / curator / W308 / W312 | after 29 Sep | Post-deadline list, plus z-shift I-029, the MAX_UM 2.0 note, the I-045 "weakened" note and the division agenda | `round25/report.json` R25-A8 (d); `round28/report.json` R28-A6 (1); `round31/report.json` R31-A5; `round32/report.json` R32-A4 |

**Passed or finished time-bound items:**
- **Earlier deadlines:**
  - The R8 new-mechanism cutoff (27 Sep 12:00Z) has passed.
  - The 28 Sep 12:00Z consolidation is superseded (T46; l.3392-3394).
  - The E10 02:00Z cutoff (T172) has passed: any E10 copy now needs the user's yes (`round32/report.json` new_facts (5)).
- **Overnight 28-29 Sep:** the 51 read (21:43Z), the freeze (23:34Z), the slot reset (00:00Z), the night batch (00:05-00:46Z), W298 / R30-A1 (02:02Z) and **W304 / R31-A1 (02:53Z, l.4294-4312)**.
- **Friend replies:** none awaited. The last friend instruction was on 26 Sep (l.2175-2176).
- **T156:** the tick deadline is 20:00 UTC = 23:00 MSK. Never write "20:00" without "UTC".
- **T192** (new, info): **~09:30Z** is the latest first sighting of a >= 0.960 public notebook that can still become a finals candidate. After that it is information for the user only (`round32/report.json` new_facts (5); `CONTEXT.md` l.3171-3176).
- **T194** (new, info): the next free S1 snapshots for W310 are the e10 files at hh:13Z / hh:41Z. The loop stops at 12:00Z (`experiments/e10_watch/watch_loop.log`; `round32/report.json` R32-A2).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I366** (new) | "04:13Z timer text = 'launch the next research round' only; R31-A2 power push lives only in CONTEXT 02:53Z (5) -> risk it is skipped before the 05:10Z trip" | `round32/scan_plancheck.notes.md`; `round32/report.json` plan_issues (a) | If the session acts on the timer text alone, the push is lost. A laptop asleep on battery then costs A-M1 (after ~08:40Z), A-M2 (after ~11:30Z) and a timely card (W309). |
| **I367** (new) | "tools/uptest.py save: subprocess.run without timeout (l.34-36) -> can hang a decision step (freeze (7) says every Kaggle call in timeout)" | `round32/scan_plancheck.notes.md`; `tools/uptest.py` l.34-36 | A hang after standby would block A-M1 / A-M2. The fix is W310: an e10-snapshot compare, or `timeout 180`. It is not yet in CONTEXT. |
| **I368** (new) | "exp79a SEC+CI (9.27,9.45] vs exp87a CI (9.30,9.48] -> SEC ~0 runtime; exp89p expected ~ exp85a (7.01,7.19] -> first COMPLETE ~07:47-07:58Z ... exp75 ... and exp89r ... may co-complete within one 30-min e10 window" | `round32/scan_plancheck.notes.md`; `round32/report.json` new_facts (4) | Read windows are ~10 min later than the 07:38Z earliest in W306. With a co-completion, the UP goes to the higher display only, and equal displays are both MASKED (`CONTEXT.md` l.3124-3126). |
| **I369** (new) | "lb_poll.py: ts taken BEFORE poll() ... header can be written up to ~630 s after its own ts"; "the sleep counted standby time for this exact process" (28 Sep 15:15:31Z) | `round32/v_plancheck_pc32-05.notes.md` | The 06:07Z post-wake step must not kill a live poller within ~11 min of the wake (T193). The "post-wake lag" theory is refuted. |
| **I370** (new) | "Card v4 l.1 carries a SUPERSEDED marker, but it cites the old v5 sha8 aadead83"; "card v5 l.93 / l.138 / l.152 still cite dead cron ids 2e9ce42e / ec670938 / 64b9bb56 / ddc5884d" | `round32/report.notes.md` 03:38Z; `round32/report.json` R32-A3 (c) | The 12:03Z timer names card v4. Filling the wrong card, or showing the user dead waiter ids, is a real risk (W311 (c)). |
| **I371** (new) | "the orphan pool is used up at cap ~24 in-lab, which matches the flat public dose above cap 6 (cap 6 0.956, cap 8 0.955, cap 12+fc2 0.955)" | `round32/scan_recheck.notes.md` 03:40-03:58Z | This is the only mechanistic explanation of the DaughterNet cap plateau. It appears only in scan notes, and R32-A4 compresses it to "plateaued on public". Keep it for the post-deadline lessons (W312). |
| **I372** (new) | "Recheck-lens yield: rounds 25-31 = 21 recheck items, 0 builds/submits ... last recheck that changed a submit = R20-RC-A" | `round32/scan_recheck.notes.md`; `round32/report.json` plan_issues (d) | Rounds 33+ should drop the lens or restrict it to card v5 claims (W313). No CONTEXT line records this. |
| **I373** (new) | "On a 1.625 um detection grid ... GT sister distance median 5.97 um ... = daughters just after cytokinesis inside one blob"; one-to-one re-match "Class = 8/85 (9.4%), not 9" | `round32/scan_recheck.notes.md`; `round32/v_recheck_r32-rc-b-*.notes.md` | This prevents a "merged-daughter splitter" from being re-proposed post-deadline. It is the closed mirror/lowdet line, with FP:TP ~6 against a break-even of 2.8. |
| I356 (repeated) | "tools/runtime_ledger.py --print ... also rewrites experiments/lb_poll/ledger.md" happened again in round 32 | `round32/scan_plancheck.notes.md` | This keeps `M experiments/lb_poll/ledger.md` in `git status`. It is harmless, but it is not read-only. |
| I358 / I359 | The A-M2 bullet without Rr '+'; the 08:40Z header may not exist | `round31/*` | **Resolved** by `CONTEXT.md` l.4295-4305 (02:53Z). |
| I360-I365 | The medal-line shift and stale card numbers; the silver-order caveat; the exp89p margin to the family max; the family L range; I-045 "weakened"; the uptest missing-TeamId safety | `_curation/31/watch.json`; `round31/*` | Still open, via W307, W306, W308 and W310. The I360 medal lines were re-confirmed at 03:13Z (`round32/report.json` new_facts (3)). |
| I352-I357, I338-I348, I329/I330, I334-I337, I316-I326, I303-I313, I287-I302, I278, I72, I116, I145 | Unchanged older insights | `_curation/30/watch.json`, `_curation/29/watch.json`, `_curation/27/watch.json` | - |
