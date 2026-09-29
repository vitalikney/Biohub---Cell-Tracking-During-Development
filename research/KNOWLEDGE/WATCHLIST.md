# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-29 ~04:45 UTC (curation 33). This updates the curation-32 build of 29 Sep ~03:50Z. That build is committed in 6bbbdf0, and a structured copy is in `research/KNOWLEDGE/_curation/32/watch.json`. Older predecessors run from `_curation/31/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there.

**Sources read for this update:**
- **`CONTEXT.md`:** it now has 4,349 lines, and `## 9. Literature` starts at l.4329. There are two new entries since curation 32:
  - l.4313-4324 (**03:56Z, ROUND 32**: external delta null; R32-A1..A3 logged, including the R32-A2 UP-test procedure and the R32-A3 timer-text pointers; no rule change);
  - l.4325-4328 (**04:10Z, R31-A2 POWER PUSH SENT**).
- **`git log`:** **6bbbdf0** (03:56Z) committed round 32 and curation 32. **dd7cf04** (04:10Z) committed the push line.
- **`research/wf_ideas_v4/round33/`:** untracked, written 04:13-04:36Z. Read:
  - `report.json`, which holds **R33-A1..A4**, new_facts (1)-(6), plan_issues (a)-(f), the rejected items and next_focus;
  - `report.notes.md`;
  - every `scan_*.notes.md` and `v_*.notes.md` file.
  - **There is no `REPORT.md`**, because the harness refused it (`report.notes.md` 04:33Z).
- **`experiments/lb_poll/poll.log`:** the newest header is **04:34:31Z** (l.28315). In it, 56656147, 56656157 and 56657612 are PENDING, and 56640366 is COMPLETE 0.959.
- **Loops:**
  - `experiments/e10_watch/watch_loop.log`: RUN 39 at 03:42:06Z, signals 0, next 04:41:53Z. The round's own snapshot is `20260929T0413Z.txt`.
  - `experiments/discussions/feed_loop.log`: 03:58:09Z, 0 new, E10 FLAG none (`digest_20260929T0358Z.md`).
- **Local read-only checks at ~04:38Z:**
  - Card v5 sha8 = **a134d5e4**.
  - BatteryStatus is 2 (AC).
  - Win32_Process: **the only night-ref read watcher is still 16292/13516** (created 03:47 MSK = 00:47Z). No per-ref watcher exists yet.
  - `grep -c` on CONTEXT.md returns 0 for each of: DET_THRESHOLD, int-casting, "cron defect", I-045, R33-A1, "P LATE THRESHOLD". "battery standby" still returns 1.
  - `experiments/RESULTS.md` probe rows still end at probe 46 (l.79).
  - `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66 is unchanged.
  - The `REPORT.md` files for rounds 29-33 are all absent.

All times are UTC; the user thinks in MSK, which is UTC+3 (`CONTEXT.md` l.3683-3687). IDs are stable: W is an action, T a time-bound reminder, I an insight. Status values are: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~04:40Z, 29 Sep:**
- **Best display: 0.959**, from exp87a (probe 51). V_pub = exp87a (`CONTEXT.md` l.4278-4285).
- **Rank** at 04:13:49Z: #132 of 3,981, 17th of 21 in the 0.959 block, with 115 teams at >= 0.960 (`round33/report.json` new_facts (3)).
- **Medal lines are unchanged:** silver ~#199 (0.957 block, 157-206); bronze ~#398 (0.955 block, 331-440).
- **Night probes 52-54 are all PENDING** at 04:34:31Z. Expected reads:
  - exp89p 07:38-08:35Z (expected 07:47-07:58Z);
  - exp75 09:05-10:05Z;
  - exp89r ~09:23-09:34Z (`round33/report.json` new_facts (6)).
- **Slots:** 2 left on 29 Sep, for A-M1 and A-M2.
- **User:** the push was sent at 04:10Z. The user travels from 05:10Z. The session never ticks.
- **CRITICAL (new): W314 = R33-A1.** Watcher 16292 is one-shot and will exit on exp89p. **exp89r has no watcher**, and it lands in the 09:13-10:13Z timer gap.

**Changes since ~03:50Z (curation 32):**
- **Done:**
  - **W309** (the power push): sent and logged at 04:10Z (`CONTEXT.md` l.4325-4328, dd7cf04).
  - **W310** (the UP-test procedure) and **W311 (a)** (the timer-text pointers): logged in CONTEXT at 03:56Z (l.4316-4324).
  - **Round 32:** committed (6bbbdf0).
  - **T181, round 33:** ran 04:13-04:36Z.
- **Superseded:**
  - **W313** (the recheck lens) is replaced by R33 plan_issue (e): a READS-vs-CARD lens (**W318**).
  - R30-A4 (b)'s sequential re-arm is replaced by per-ref watchers (W314).
- **New:**
  - actions **W314-W318**;
  - reminders **T195-T197**;
  - insights **I374-I381**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W314** (new; = **R33-A1**, supersedes R30-A4 (b)) | **ARM TWO PER-REF NIGHT READ WATCHERS** with run_in_background Bash, 0 Kaggle calls. One `until` loop on `^56656147,.*(COMPLETE\|ERROR)` (exp89r) and one on `^56656157,...` (exp75), each polling the last poll.log block every 120 s. <br>- **Use the 16292 formatter** `awk -F'SubmissionStatus.' '{print substr($1,1,50), $2}'`, **not `cut -c1-220`**. <br>- **Keep 16292** for exp89p. If 16292 fires on a ref other than 56657612, arm one for 56657612 at once. <br>- **On the exp89r fire:** re-read the full header; apply the 02:53Z (1) A-M2 function; nb_try by 11:30Z. <br>- **On the exp75 fire:** code it under partner rule v2. <br>- Log the one-line CONTEXT OPS entry given in R33-A1 | **not started / due now**: at 04:38Z Win32_Process shows only 16292/13516; `grep -c R33-A1 CONTEXT.md` = 0 | **Now.** At the latest before **09:05Z**, when the exp75 window opens. Ideally before the 05:10Z trip | `research/wf_ideas_v4/round33/report.json` R33-A1, plan_issues (a); `round33/v_plancheck_pc33-01.notes.md` |
| W126 (part 2) | Add RESULTS.md rows for probes **47 (0.955), 48 (0.957), 49 (0.955), 50 (0.958) and 51 (0.959, UP 12)**, then the night probes 52-54 and the morning probes | **overdue**: probe rows still end at 46 (l.79); RESULTS.md was last committed 28 Sep 05:03Z | before the finals card (29 Sep 12:03Z) | `experiments/RESULTS.md` l.79; `CONTEXT.md` l.4153-4160, l.4254-4272 |
| W296 + W303 (updated) | Write REPORT.md for **rounds 29-33**. Rounds 30-33 must be copied verbatim from `report.json` report_md_ru, because the harness refused the writes. **Commit round 33** (untracked) with named paths, as the user, with no Co-Authored-By | rounds 29-32 are committed (6bbbdf0 for 32); round 33 is untracked; all 5 REPORT.md files are absent | with the next CONTEXT commit (the W314 OPS line) | `round33/report.json` next_focus NOTE; `round33/report.notes.md` 04:33Z; `git status` (`?? research/wf_ideas_v4/round33/`); `memory/feedback-git-no-coauthor.md` |
| W286 (updated) | **(1)** Add a CONTEXT line: floatout probes 32/33 were no-ops under an int-casting scorer. **(2)** Fix `e10v3/runbook.notes.md` l.66 to "OUR = 0.959 (exp87a), so SC >= 0.960". CONTEXT l.4159-4160 already has the right trigger | (1)(2) **overdue**: `grep int-casting` = 0; l.66 still reads "OUR = 0.957 ... SC >= 0.958" at 04:38Z | (2) before the E10 read at 04:41Z (now passed; next 05:41Z); (1) low | `round28/report.json` R28-A6; `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66 |
| W279 (1) | Log RC-C: "DET_THRESHOLD stays closed for 29 Sep and is never a morning filler" | not started (not in 03:56Z or 04:10Z; `grep -c DET_THRESHOLD CONTEXT.md` = 0) | before **07:23Z**; fold it into the W314 OPS line | `round27/report.json` R27-A9 (1) |
| W297 | CONTEXT still blames "a busy session / battery standby" for the lost rounds. The cause was the cron defect (round 28) | not started (`grep -c "cron defect"` = 0) | with W314; low | `round28/report.json` new_facts 5; `CONTEXT.md` l.4096 |
| W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 | Old info and curator lines; the ROUND RECORD; LESSONS H1; no NEVER_SUBMIT in exp70j/exp70k; old text fixes | overdue, low | H2, 29 Sep 23:00Z | `_curation/24/watch.json`, `_curation/26/watch.json` |

## NEXT 24 H (29 Sep ~04:40Z -> 23:59Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W314 | **now**, before 05:10Z if possible; hard limit 09:05Z | Per-ref watchers (above) | not started | R33-A1 |
| T181 + T187 + **W318** (new; = R33 plan_issue (e), supersedes **W313**) | **05:13Z** round 34 (may fire late: laptop asleep on the trip); 06:13Z onward, hourly; **07:13Z minimal or skipped** | **Round 34 is light.** It checks that the W314 watchers are alive (Win32_Process grep 56656147 / 56656157) and does a read-only feed / e10 check. Chrome only if something changed; no builds. <br>**From the reads onward, a READS-vs-CARD lens replaces the recheck lens:** codes, running-champion V_pub, UP-test inputs and card v5 numbers at each read. External scans open decisions/ and kaggle_runs/ in any new repo | pending | `round33/report.json` next_focus, plan_issues (e); `CONTEXT.md` l.4305-4308 |
| T100 (updated) | E10 hourly at hh:41Z until **12:00Z** (next 04:41Z, 05:41Z); feed every 90 min (next ~05:28Z) until 23:59Z | The E10 v3 trigger is **>= 0.960**. A copy needs: a >= 0.960 notebook, a PASSED dummy, the user's yes, and a submit by ~10:00Z. It also needs the **R33-A4 (c) pre-pool gate (W317 (c))**. A notebook first seen after ~09:30Z is information only (T192) | live (RUN 39 03:42Z; feed 03:58Z; best public 0.953) | `experiments/e10_watch/watch_loop.log`; `experiments/discussions/digest_20260929T0358Z.md`; `round33/report.json` next_focus |
| T173 | **05:10-06:00Z** (08:10-09:00 MSK) | The user travels and the laptop sleeps. timer.sh fires on wake. Watchdog 25988 is one-shot and exits at the unplug | info | `CONTEXT.md` l.4066-4072; `round33/report.json` new_facts (1) |
| T174 + W301 + T193 | **06:07Z** post-wake (09:07 MSK) | Check AC, poll-header age and loops. **If BatteryStatus != 2, re-push and re-arm a battery-tolerant watchdog.** Confirm that 16292 and the W314 watchers survived the sleep. **Do not kill a live lb_poll.py within ~11 min of the wake** | pending | `CONTEXT.md` l.4309-4312; `round32/v_plancheck_pc32-05.notes.md` |
| W302 (4) | 06:07-07:23Z | First MSK message: "Both morning slots may end UNUSED by rule; that is expected. exp89t/exp89u stay off unless you say yes" | pending | `round30/report.json` R30-A5 (4) |
| **W315** (new; = **R33-A2**, optional) | **before exp89p's first terminal header**; latest at the 07:23Z prep | **P LATE THRESHOLD = 8.0 h** (non-CI safetail), not the CI 10.2 h. If exp89p's terminal header + 210 s x failed attempts > **08:46:36Z**: <br>- P '+' stands (flag v); <br>- P '0'/'-' becomes '?' for A-M2 and for the card SEC line; <br>- a branch-A DIS '+' computed from that d_P becomes '?'. <br>A-M1 is unchanged. Log it pre-score, quoting a header with 56657612 PENDING. **If not logged before the read, the 10.2 h text governs; never settle it after the score** | not started (`grep -c "P LATE THRESHOLD"` = 0) | `round33/report.json` R33-A2, plan_issues (b); `tools/runtime_ledger.py` l.48/l.59-60; `CONTEXT.md` l.3021, l.3249 |
| T151 + W299 + W311 | **07:23Z** prep (10:23 MSK) | Submit `-v 1`, the gated dummy (exp89l cad1d47f). Do NOT rebuild or re-push. Re-run G5. Paste the grid with the 02:53Z (1) A-M2 function. Log the pending L lower bounds (W306) | pending (rule logged 03:56Z) | `CONTEXT.md` l.4322-4324 (R32-A3); l.4291-4301 |
| T159 / T182 + W306 | **exp89p ~07:47-07:58Z** (window 07:38-08:35Z; A-M1 limit 08:40:36Z; 8.0 h mark 08:46:36Z); exp75 09:05-10:05Z; exp89r ~09:23-09:34Z (10.2 h mark 10:17:28Z; admit 10:50:28Z) | **Night reads:** <br>- P = exp89p vs 0.958 (P '+' only at >= 0.959). <br>- Rr = exp89r vs 0.959 (Rr '+' only at >= 0.960). <br>- exp75 vs #37 0.954 (partner rule v2). <br>Log the L interval, KEY FACTS and RESULTS (W126). If two files co-complete in one e10 window, the UP goes to the higher display, and equal displays are both MASKED | pending (all PENDING at 04:34:31Z) | `round33/report.json` new_facts (6); `CONTEXT.md` l.3124-3126, l.4294-4312 |
| **W317 (b)** (new; = **R33-A4 (b)**) | in the post-decision entry after A-M1 (~08:45Z) and after A-M2; **never at the decision header** | **C11 record wording:** <br>- P '+' -> "C11: first positive LB read of a distilled fine-tune (SEC n2a), UNPROVEN (1 public embryo, a 0.001 display step, negative lab prior; no private claim; Q3 unchanged)". <br>- P '-' -> "C11 UPHELD (6th negative secondary change)". <br>- P '0' -> "C11 not overturned (null at display resolution)". <br>- '?' -> "no C11 read". <br>Add Rr as the second n2a point. Write "distillation = post-deadline line" only if both are '+'. **Never "OVERTURNED"** | not started | `round33/report.json` R33-A4 (b), rejected (R33-RC-B); `round33/v_recheck_r33-rc-b-*.notes.md` |
| W310 (updated) | at each terminal header, ~07:47-11:00Z | **UP test, 0 API calls,** only for V_pub at a 0.959 display (exp89p or exp89r). Compare e10 snapshots S0/S1 with `tools/uptest.py compare`. A fresh download only as `timeout 180 python tools/uptest.py save <tag>` | **logged** in `CONTEXT.md` l.4316-4322 (03:56Z) | `round32/report.json` R32-A2 |
| T151 A-M1 / T183 + T190 | first header with 56657612 terminal; **the 08:40Z header**; submit by **08:45Z** (11:45 MSK) | **A-M1:** d_P >= 0.959, COMPLETE -> `nb_try exp89l`; anything else -> UNUSED. If 56657612 is still PENDING at 08:30Z, arm ONE waiter for a single list at 08:40:00Z, tagged `[manual-A-M1]` | pending | `CONTEXT.md` l.4274-4277, l.4302-4305 |
| **T195** (new) | **09:13-10:13Z** | **There is no timer in this gap**, and exp75 and exp89r both land in it. Only the W314 watchers wake the session. If W314 was never armed, A-M2 slips to the 10:13Z round or the 11:10Z check (40-100 min late), and a non-CI M2 read can slide past 18:37Z | info / guarded by W314 | `round33/report.json` new_facts (1), R33-A1 why |
| T151 A-M2 / T184 | first header with 56656147 terminal (expected ~09:23-09:34Z via W314); **latest 11:00Z header, submit by 11:30Z** (14:30 MSK); 11:10Z timer | **The 02:53Z (1) function:** <br>- DIS '+' -> exp89s. <br>- Else, if Rr '+': DIS '-' -> UNUSED; DIS '?' -> exp89q iff P is '+' or '?'. <br>- Everything else -> UNUSED. <br>W315 amends P's late clause if it is logged in time | pending | `CONTEXT.md` l.4295-4301 |
| T180 / W294 + **W316** (new; = **R33-A3**) | at each morning submit (exp89l ~07:55-08:45Z; M2 ~09:30-11:30Z) | **Late-read watcher per morning ref**, ending with `timeout 180 python tools/uptest.py save post_<token>`: 1 call per file, at most 2. The budget is <= 3. <br>Run `uptest.py compare <S0> post_<token>` **only** if the display equals the running champion's. S0 = the last snapshot with our count unchanged (the last e10 file before 12:00Z, or the 12:13Z round). Reads are expected ~16:40-17:30Z | pending | `round33/report.json` R33-A3, plan_issues (c)(d); `experiments/lb_poll/e10_watch_loop.py` l.64 |
| W19 / W73 / W102 / W93 / W165b / W261 | standing | ONE poller; header < 15 min old; never resubmit class C or ERRORed files. SEC may be a final only as V_pub (Q3). Every Kaggle call is wrapped in a timeout | standing | `CONTEXT.md` l.3331-3335, l.3692-3703, l.4112-4114 |
| T186 | **11:41Z** last E10 snapshot; the E10 loop exits at 12:00Z | Take the rank, block position and medal-line ranks for the 12:03Z card. This is also the last free S1 before W316's saves take over | pending | `round30/report.json` R30-A4 (c); `e10_watch_loop.py` l.64 |
| T191 | ~11:10-11:30Z | The first substantive round after A-M2. It uses the READS-vs-CARD lens (W318) | pending | `round32/report.json` next_focus; `round33/report.json` next_focus |
| W266 (2) / T60 / W302 (1)(3) + W307 + W311 (c) | **12:03Z** (15:03 MSK), timer | **Fill card v5** `round29/finals_card_v5_ru.md` (**sha8 a134d5e4**). The timer text still points at v4. <br>Use the W307 numbers. Medal lines: at 04:13Z silver is ~#199 and bronze ~#398; refresh them from 11:41Z. <br>Optional: replace the dead cron ids at card v5 l.93 / l.138 / l.152. **Never "не медаль" or "рекомендую".** Never tick | pending | `CONTEXT.md` l.4322-4324; `round33/report.json` new_facts (3); `round33/v_recheck_r33-rc-a-*.notes.md` |
| W308 | any free slot after the morning decisions; post-deadline is acceptable | Curator note on **I-045**: "WEAKENED on public by CI; stays closed; post-deadline only" | not started (`grep -c I-045 CONTEXT.md` = 0) | `round31/report.json` R31-A5 |

## LATER (29 Sep ~12:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T152 + W302 (2) + W307 (5) | **18:37Z** (21:37 MSK), timer | FINAL proposal from card v5: "the pair by the card", **never "рекомендую"**. If V_pub changed, re-run `scratchpad/r31v/mc31v.py` with the new VPUB. **Optional (R33 rejected RC-A):** check that card l.46 carries the R31-RC-A numbers (0.20-0.58 / 0.02-0.16) | `round31/report.json` R31-A4 (5); `round33/report.json` rejected |
| T161 | **19:43Z** (22:43 MSK), timer | Notify-only reminder + V_pub re-check. The timer already reads SELECTED and pushes on a mismatch. **Any read after ~19:30Z cannot be a final** | `CONTEXT.md` l.3685, l.4054-4056; `round33/v_recheck_r33-rc-a-*.notes.md` |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** The session never ticks. If the user does nothing, #37 + #38 stay (modelled bronze ~0.38 at base) | `CONTEXT.md` l.3851-3855, l.4091-4092 |
| T153 | ~20:00-20:30Z | Verify that API SELECTED = the user's pair | `CONTEXT.md` l.3474 |
| T162 | **21:05Z** (00:05 MSK 30 Sep), timer | Last-call notify on a SELECTED mismatch | `CONTEXT.md` l.4092, l.4099 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; final public LB snapshot | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline: a submit must **finish** before it; re-ticks are allowed until then | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765; `CONTEXT.md` l.3848, l.3855 |
| T155 | 30 Sep 00:07Z, timer (armed) | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715, l.4131; `round33/report.json` new_facts (1) |
| **W317 (a)(c)(d)** (new; = R33-A4) | (a)(d) next curation, post-deadline acceptable; (c) only on an E10 trigger | **(a)** IDEAS I-129 alias: OpenKaggle BH-0005 (MIN_TRACK_LEN 6 -> 4), **NOT RECOMMENDED** (probe 6 -0.002; +2.13% nodes ~ -0.002). **(c)** Any E10 copy must set `BIOHUB_VALIDATOR_ENABLE='0'` explicitly, plus REPAIR 34200 / DIVINS 28800 / DEGRADE_KEEP_DIV 1. Grep the LAST assignment. **(d)** External scans open decisions/ and kaggle_runs/ | `round33/report.json` R33-A4, new_facts (4)(5) |
| W312 | any free slot after the 20:00Z tick | Curator note: the post-deadline division agenda (R32-A4) | `round32/report.json` R32-A4 |
| W295 | next CONTEXT entry / curation pass | The 744093 integer check; an I-320 narrow annotation | `round29/report.json` R29-A8 |
| T133 / T170 | 3 Oct | GPU quota refresh (about 2.7 h left) | `CONTEXT.md` l.4239-4241 |
| W29 / curator / W308 / W312 / W317 (a) | after 29 Sep | Post-deadline list, z-shift I-029, MAX_UM 2.0, I-045 "weakened", the division agenda, the BH-0005 alias | `round25/report.json` R25-A8 (d); `round31/report.json` R31-A5; `round32/report.json` R32-A4; `round33/report.json` R33-A4 |

**Passed or finished time-bound items:**
- **Earlier deadlines:**
  - The R8 new-mechanism cutoff (27 Sep 12:00Z) has passed.
  - The 28 Sep 12:00Z consolidation is superseded (T46).
  - The E10 02:00Z cutoff (T172) has passed.
- **Overnight 28-29 Sep:** the slot reset (00:00Z), the night batch (00:05-00:46Z), R30-A1 (02:02Z), R31-A1 (02:53Z), the round-32 log (03:56Z) and **the W309 power push (04:10Z, l.4325-4328)**.
- **Friend replies:** none awaited (l.2175-2176).
- **T156:** the tick deadline is 20:00 UTC = 23:00 MSK. Never write "20:00" without "UTC".
- **T192:** ~09:30Z is the latest first sighting of a >= 0.960 notebook that can still become a finals candidate.
- **T194:** the free S1 snapshots are the e10 files at hh:13Z / hh:41Z until 12:00Z. After that, W316 covers it.
- **T196** (new, info): `tools/uptest.py save` has no internal timeout. **Always use `timeout 180`** (W310, W316).
- **T197** (new, info): the timer.sh schedule is 05:13, 06:07, 07:13, 07:23, 08:13, 08:30, 09:13, 10:13, 11:10, 12:03, hourly 13:13-18:13, 18:37, 19:43, 21:05, and 30 Sep 00:07Z (`round33/report.json` new_facts (1); `round33/v_plancheck_pc33-01.notes.md`).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I374** (new) | "only read watcher = PID 16292/13516 (created 00:47Z) ... exits at the FIRST terminal ref (expected exp89p ~07:47Z). No logged rule re-arms it"; "Nothing between 09:13 and 10:13Z" | `round33/scan_plancheck.notes.md`; `round33/v_plancheck_pc33-01.notes.md` | Without W314, A-M2 is decided up to ~100 min late, and the M2 read can slide past 18:37Z. R30-A4 (b)'s re-arm exists only in `round30/report.json`. |
| **I375** (new) | "DEFECT in proposed command: `cut -c1-220` truncates the exp89r row (266 chars) before 'SubmissionStatus.COMPLETE,<score>'" | `round33/v_plancheck_pc33-01.notes.md` | A watcher built with cut would wake the session without the display. Use the awk formatter. |
| **I376** (new) | "R31-A1 ... 'a 0/- read with L_hi > 10.2 h ... is ?' -> CI threshold applied to a non-CI file = category error"; safetail gate is 8.0 h (`tools/runtime_ledger.py` l.48/l.60) | `round33/report.notes.md` (PC33-02 self-check) | A late, depressed P can fake a DIS '+' and send exp89s. W315 must be logged **before** exp89p's read, or never. |
| **I377** (new) | "e10_watch_loop.py l.64 END = 2026-09-29 12:00 UTC ... exp89l ... and M2 ... may complete within one hourly gap -> +2 with equal displays = MASKED -> champion stays by default" | `round33/scan_plancheck.notes.md`; `round33/report.notes.md` | This is the reason for W316's immediate `uptest.py save`. Nothing in CONTEXT covers timing after 12:00Z. |
| **I378** (new) | "exp85a l.5068 VALIDATOR_ENABLE = env.get(...,'1')!='0' -> DEFAULT ON if unset (E10 copies must set it)"; "REPAIR_DEADLINE_S 27000 then re-set 34200 later in c0 (last wins)" | `round33/v_recheck_r33-rc-c-*.notes.md` | A late E10 copy of a public x138-type notebook could ship the imissher PP sweep ON (train-stem-dependent selection on the hidden rerun). A naive grep can also read the wrong deadline. W317 (c). |
| **I379** (new) | "OpenKaggle/biohub-cell-tracking-research ... decisions/BH-0005 discloses BIOHUB_OUTPUT_MIN_TRACK_LEN 6 -> 4, unsubmitted"; the scan's "no disclosed value" was wrong | `round33/report.json` new_facts (4), rejected; `round33/scan_hyp_external33.notes.md` | This value was missed by a README-only scan. It maps to closed I-129 (NOT RECOMMENDED), so it should not be re-proposed as new. W317 (a)(d). |
| **I380** (new) | "EMAX calc ... central (g .005, rho .5, s .0025) +0.21e-3, P .16. Versus the do-nothing SELECTED {#37,#38}: loses ... 5-15x the whole partner premium" | `round33/scan_recheck.notes.md` | The partner choice matters little. **What matters is that the user re-ticks away from the stale {#37,#38}.** This is the argument for the 18:37Z / 19:43Z pushes. |
| **I381** (new) | "browser_intel.md l.123 (743222 imissher): two unmodified runs of his stack read 0.948 / 0.946 -> single public reads can move 0.001-0.002 without any change" | `round33/v_recheck_r33-rc-b-*.notes.md`; `research/wf_ideas_v3/browser_intel.md` l.123 | This supports the "UNPROVEN" wording for a 0.959 P read (W317 (b)). A 1-ULP public step is not evidence for SEC on private. |
| I366 / I369 / I370 / I372 | The power push lives only in CONTEXT; no poller kill within ~11 min of wake; card v4 vs v5 and the dead cron ids; recheck-lens yield | `_curation/32/watch.json` | **I366 resolved** (push sent 04:10Z, l.4325-4328). **I372 resolved** by W318. I369 and I370 are still open (T193, W311 (c)). |
| I367 / I368 / I371 / I373 | The uptest save has no timeout; the co-completion window; the orphan pool is used up at cap ~24; the merged-daughter class 8/85 | `_curation/32/watch.json`; `round32/*` | I367 is now logged (`CONTEXT.md` l.4322). The others are unchanged. |
| I356 (repeated) | `tools/runtime_ledger.py --print` also rewrites `experiments/lb_poll/ledger.md` | `round32/scan_plancheck.notes.md` | `M experiments/lb_poll/ledger.md` is still in `git status` at 04:38Z. |
| I352-I365, I338-I348, I329/I330, I334-I337, I316-I326, I303-I313, I287-I302, I278, I72, I116, I145 | Unchanged older insights | `_curation/31/watch.json`, `_curation/30/watch.json`, `_curation/29/watch.json`, `_curation/27/watch.json` | - |
