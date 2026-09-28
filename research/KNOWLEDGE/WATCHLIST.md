# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-28 ~20:15 UTC (curation 28). This updates the curation-27 build of 28 Sep ~16:25Z (full text in the git history of this file; structured copy `research/KNOWLEDGE/_curation/27/watch.json`). Older predecessors: `_curation/26/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there. The TASK_LOCAL_SESSION, TASK_CLOUD_SESSION and v3 FINAL_REPORT rows have not changed since `_curation/20/watch.json`.

**Sources read for this update:**
- `CONTEXT.md`:
  - It now has 4,114 lines, and `## 9. Literature` starts at l.4094.
  - Entries new since curation 27 (l.3999-4093):
    - 16:26Z: CORRECTION standby (l.3999); GAP RULE v2 (l.4009); FACT CORRECTION DIS runtime (l.4021); FINALS CARD v4 STORED + facts (l.4029).
    - 16:30Z: laptop ON AC (l.4035).
    - 16:32Z: the user agrees with the hedge pair (l.4041).
    - 16:38Z: ROUND 27 REMAINDER (l.4051).
    - 16:39Z: 744093 (l.4059).
    - 16:43Z: USER TRAVEL 05:10-06:00Z (l.4066).
    - 20:00Z: IDEAS SWEEP, 16 of 16 refuted (l.4073).
    - **20:07Z: USER ASLEEP, AUTONOMOUS MODE (l.4081)**.
- `git log`: 756c513 .. **d150eec** (the 20:07Z entry). Commit bodies still have no Co-Authored-By line (`memory/feedback-git-no-coauthor.md`).
- `research/wf_ideas_v4/round28/`, untracked, written 20:04-20:05Z:
  - `report.json` (**R28-A1..A6**, new_facts 1-8, plan_issues 1-8) and `REPORT.md`;
  - `report.notes.md`;
  - `scan_plancheck.notes.md`, `scan_hyp_prefreeze.notes.md`, `scan_recheck.notes.md`, `scan_browser.notes.md`.
- `research/wf_ideas_v4/ideas_29sep/rank.json`: 0 builds.
- `experiments/lb_poll/poll.log`: newest header **20:03:00Z** (l.25152). 56640366 (probe 51) PENDING (l.25155).
- Loops:
  - `experiments/e10_watch/watch_loop.log`: RUN 31 19:44Z, signals 0, next run 20:41:53Z.
  - `experiments/discussions/feed_loop.log`: 18:57:19Z, 0 new, E10 FLAG none.
- Local read-only checks, ~20:08Z:
  - `Win32_Battery` BatteryStatus **2 (AC), 78%**.
  - Win32_Process shows **0 processes tagged `WAITER_`**. Only two `until [` bash loops are alive, started 06:24Z and 17:28Z.
  - `finals_card_v4_ru.md` contains 0 hits for `exp83c = 3` and 0 for `0.39`.
  - `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66 still reads "OUR = 0.957 ... SC >= 0.958".
  - `experiments/RESULTS.md` probe rows still end at probe 46 (l.79).
  - `ls tools | grep gate` shows no `gate_dummy.py`.
  - `grep "RULE v2.1\|1,620\|W4 FREEZE: NIGHT"` in CONTEXT finds one hit: l.4057, where RULE v2.1 appears as a name only.

All times are UTC. The user thinks in MSK (UTC+3) (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at 20:15Z, 28 Sep:**
- **Best display 0.958:** exp85a (probe 50, 56629533). V_pub = exp85a.
- **Rank:** #139 of 3,973 at 19:36Z, 14th of 23 in the 0.958 block, 125 teams >= 0.959 (`round28/report.json` new_facts 2).
- **Probe 51 exp87a (56640366):**
  - PENDING at 20:03:00Z.
  - Expected **~21:31-21:42Z** (00:31-00:42 MSK). CI tail ~23:09Z.
  - **10.2 h mark = 22:26:57Z; 10.75 h admit edge = 22:59:57Z** (`round28/report.json` new_facts 1).
- **Slots:** 28 Sep is 5 of 5 used (`round28/report.json` new_facts 8).
- **Night, 29 Sep (unchanged):**
  - 00:05Z exp89r (branch A) or exp89q (branch B);
  - 00:06Z exp75;
  - **00:46Z exp89p in both branches** (R27-A6 (ii) unanswered, so the default applies; l.4057-4058);
  - fallback exp83c.
- **Morning:** MORNING TABLE v1.1 (l.3931-3955) is unchanged after the ideas sweep (l.4073-4080).
- **User:** **asleep, autonomous mode** (l.4081-4093). GPU is no longer binding for testing a strong public notebook or idea. If the quota runs out, teammates push the morning files; the session never uses their tokens. Submits still follow the logged rules. After 02:00Z an E10 copy needs the user's yes. The session never ticks.
- **Power:** on AC since 16:27Z. There was a battery excursion 18:07-18:21Z (21:07-21:21 MSK), and Modern Standby on AC 16:51-17:40Z with the poller unbroken (`round28/report.json` new_facts 5).
- **CRITICAL (new):**
  - **Session crons have never fired in this session: 0 of 31 CronCreate since 26 Sep 17:50Z** (`round28/scan_plancheck.notes.md` 19:45Z; `round28/report.json` plan_issues 1).
  - Every scheduled step from the freeze to the post-deadline job sits on crons.
  - The 20:07Z entry puts the new hourly rounds on "session cron" too (l.4085-4086).
  - No replacement wall-clock waiter is alive as of ~20:08Z.

**Changes since ~16:25Z (curation 27):**
- **Done:**
  - W271 (a) message sent, (b) CONTEXT correction at l.3999-4008, (c) watchdog at l.4007-4008 and l.4035-4040;
  - W273 (GAP RULE v2, l.4009-4020);
  - W274 (1) (l.4021-4028);
  - W278 (1) (l.4029-4034);
  - W279 (2) (l.4033-4034) and (3) (l.4056-4057);
  - W277 (1) (cron 64b9bb56, l.4054-4056);
  - W276 part (backup crons 00:20/00:50/01:30Z, l.4051-4054);
  - T164: round 28 ran 19:36-20:05Z by hand, not by its 17:47Z cron (`round28/scan_plancheck.notes.md` 19:45Z).
- **Moot:**
  - T168 (the battery-empty risk), since the laptop is on AC.
  - W272, answered by default: (i) no, (ii) 00:46Z (l.4057-4058). The user is asleep (l.4081).
- **Reopened or corrected:**
  - W278 (1)'s claim that the card was stored "with the R27-A8 edits" is **false**. It moves to **W285**.
  - W276 / W277 (1) / W270: those crons will not fire. They move to **W281**.
  - The previous chat message blamed the battery for the lost 20:47 MSK round. **That is wrong**: the laptop was on AC and awake then (`round28/report.json` new_facts 5, plan_issues 8). It moves to W281 (3).
- **New:**
  - actions **W281-W288**;
  - reminders **T171-T176**;
  - insights **I327-I337**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W281** (new; = **R28-A1**; supersedes W270, and the cron parts of W276/W277/T166) | **WALL-CLOCK WAITERS replace the session crons.** **(1)** One `run_in_background` Bash until-loop per due time, local clock only, tagged `: WAITER_<LABEL>_<cronid>`. Due times, all UTC: <br>- FREEZE 202609282330; <br>- BATCH 202609290004; <br>- BACKUPS 0020 / 0050 / 0130; <br>- POST-WAKE 0607; <br>- MORNING PREP 0723; <br>- FINALS 1203 and 1837; <br>- TICK REMINDER + V_pub re-check 1943; <br>- LAST-CALL 2105; <br>- POST-DEADLINE 202609300007; <br>- optional research rounds. <br>The freeze waiter must point to R27-A4 + R28-A4, **not** to the stale "W4 AMEND 3" prompt of cron 5ece5d24. **(2)** A CONTEXT OPS line: crons never fired (0/31), and waiters die with a VS Code / Claude Code restart. **(3)** ONE Russian message, MSK first, correcting the battery claim (text in `round28/report.json` R28-A1) | **not started** (0 `WAITER_` processes ~20:08Z; no CONTEXT OPS line) | **NOW**; all waiters armed before 23:00Z | `round28/report.json` R28-A1, new_facts 5, plan_issues 1, 8; `round28/scan_plancheck.notes.md` 19:45Z, 19:55Z |
| **W288** (new; contradiction) | The 20:07Z AUTONOMOUS entry schedules "one pre-night round at 22:47 UTC and HOURLY rounds 01:13-18:13 UTC ... (session cron)". By W281's evidence these will not fire. Add hourly research waiters: 22:47Z, and 01:13Z .. 18:13Z at hh:13. Alternatively, launch each round from the post-batch / read notifications. Amend the CONTEXT line | not started | before 22:47Z | `CONTEXT.md` l.4085-4087; `round28/report.json` R28-A1 (optional research-round waiters) |
| **W282** (new; = **R28-A2**; absorbs W274 (2) and W238 residue) | **ONE pre-score CONTEXT entry, quoting a PENDING header (20:03:00Z or later).** <br>**(a) RULE v2.1**, with ONE compute anchor. The 1,473 s reference was measured from "V1284 head patched ... mode = candidate", not from "GPU shard 0". PASS if whole-kernel <= 2,100 s OR compute <= 1,620 s; log setup, compute and GPU model separately. <br>**(b) exp89l dummy gate:** <br>- branch A only; build STOP unless sha8 cad1d47f; <br>- compare vs the exp89p dummy (CSV 629fc20b4815): topology 122,110 / 117,957 / 88; COORDINJECT 4/4, replaced 0.90-0.93; integer-coordinate change 0.60-0.69; all coordinates integers; <br>- pass by the **A-M1 decision header, 08:40Z**, not 23:30Z. <br>**(c) NO-FREEZE FALLBACK**, written without the freeze literal. <br>**(d) G4 grep** hardened to `^- 2026-09-2[89] [0-9:]+ UTC, W4 FREEZE: NIGHT 29 Sep` | **overdue risk**: not started (`grep 1,620` = 0; RULE v2.1 only named at l.4057) | **before 51's first COMPLETE header (earliest ~21:30Z)** | `round28/report.json` R28-A2, plan_issues 2-3; `round28/scan_plancheck.notes.md` (RULE v2.1 line) |
| W126 (part 2) | RESULTS.md rows for probes **47 (0.955), 48 (0.957), 49 (0.955), 50 (0.958)**; later 51 and the night probes | **overdue** (probe rows end at 46, `experiments/RESULTS.md` l.79) | before the finals card (29 Sep 12:03Z) | `CONTEXT.md` l.3530, l.3615, l.3639, l.3856 |
| **W280** (carried) | Write REPORT.md for rounds 24-27 (only report.json exists; round 28 now has one). Commit rounds 27 and 28 plus `ideas_29sep` with named paths, as the user, with no Co-Authored-By | round 27 is tracked; round 28 is untracked; REPORT.md is missing for rounds 24-27 (optional, low per `round28/report.json` plan_issues 7) | with the next CONTEXT commit | `git status`; `round28/report.json` plan_issues 7 |
| W279 (1) | Log RC-C: "DET_THRESHOLD stays closed for 29 Sep and is never a morning filler" | not started | before **07:23Z** 29 Sep | `round27/report.json` R27-A9 (1) |
| W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 | Old info and curator lines; ROUND RECORD; LESSONS H1; no NEVER_SUBMIT in exp70j/exp70k; old text fixes | overdue, low | H2 29 Sep 23:00Z | `_curation/24/watch.json`, `_curation/26/watch.json` |

## NEXT 24 H (28 Sep 20:15Z -> 29 Sep 20:15Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W281, W288, W282 | **now** | Waiters, round waiters, pre-score RULE v2.1 + exp89l gate + no-freeze fallback | not started | R28-A1, R28-A2; l.4085 |
| **W286** (new; = **R28-A6**) | before **23:30Z** | **(1)** A softened CONTEXT line: floatout probes 32/33 were no-ops under an int-casting scorer; the exp60 lab is consistent with 744093 (ALL -0.0050); z-shift I-029 stays post-deadline. **(2)** Fix `e10v3/runbook.notes.md` l.66 to "OUR = 0.958 (exp85a), so SC >= 0.959". **(3)** KEY FACTS: rank 139 of 3,973, 125 teams >= 0.959, best public notebook 0.953, whitelist exhausted | not started (l.66 still stale ~20:08Z) | `round28/report.json` R28-A6 |
| T100 | E10 hourly at hh:41Z (next 20:41Z) until 29 Sep 12:00Z; feed every 90 min (next ~20:27Z) until 29 Sep 23:59Z | E10 v3 trigger **>= 0.959**. **Before 02:00Z:** build + dummy an E10 copy per the rule. **After 02:00Z:** the copy needs the user's yes; dummy it and ask (l.4089-4091). Autonomous mode lets GPU be spent on a strong public notebook (l.4087-4089) | live (RUN 31 19:44Z; feed 18:57Z) | `experiments/e10_watch/watch_loop.log`; `CONTEXT.md` l.3993-3996, l.4081-4093 |
| **T165 / W283** (= **R28-A3**) | **~21:31-21:42Z expected** (00:31-00:42 MSK); **10.2 h 22:26:57Z**; **admit edge 22:59:57Z**; tail ~23:09Z | **Read probe 51.** <br>- **Rules:** R25-A1 (4) + GAP RULE v2 (l.4009-4020) + the 10.75 h admit edge. <br>- **UP test:** `python tools/uptest.py save S1_51` / `compare S1_1214Z S1_51`; count 53; backup = the e10 snapshots (52 -> 53). <br>- **Branching:** '+'/'0u' (incl. UNPROVEN-ins) -> branch A (exp89r). In branch A, build exp89l (cad1d47f) and push its dummy under the W282 gate. Otherwise -> branch B (exp89q). <br>- **Logging:** the 51 read line + KEY FACTS; launch round 29 by hand; update RESULTS (W126). <br>- **Poller:** no restart 21:00-22:30Z unless the header is > 15 min old | pending (PENDING 20:03:00Z) | `round28/report.json` R28-A3, new_facts 1 |
| T166 (updated) | 22:47Z pre-night round | Per l.4085, but on a cron -> needs a W288 waiter or a hand launch | at risk | `CONTEXT.md` l.4085-4086 |
| **T143 + W284** (new; = **R28-A4**; extends W275/W278 Q3) | **23:30Z** (02:30 MSK), driven by the FREEZE waiter | **W4 FREEZE LINE** = R27N-2 + R27-A4 amendments. **Add R28 amendments:** <br>**(i)** admit edge 10.75 h; <br>**(ii)** item (5): GAP RULE v2 overrides the R26-A4 (a)/(d) 10.2 h clauses; <br>**(iii)** guarded **T54**. R27N-3's version raises IndexError in branch A. Print 00:46Z if there is no exp89q row, and run it as a background until-loop in both branches; <br>**(iv)** **nb_try**: a daily/allowance/limit error -> `return 3` = STOP + push, never the exp83c fallback; delete "limit" from the HARD FAIL regex; <br>**(v)** store ONE checklist text that the batch, backup and post-wake waiters read; <br>**(vi)** SEC and CI info lines; <br>**(vii)** item (8): waiters alive, G5 re-run, BatteryStatus 2, GPU. <br>**Also:** the Q3 conditional line, and "morning files are submitted at their decision header" (W277 (2)) | not started | `round28/report.json` R28-A4, plan_issues 4; `round27/report.json` R27-A4 |
| T169 | until 29 Sep 00:00Z | 28 Sep is 5 of 5 used: a "limit" error is expected, not a file failure | standing | `round28/report.json` new_facts 8 |
| T126 | 29 Sep 00:00Z | Slot reset (5 new slots) | - | `CONTEXT.md` l.3367 |
| T20 / T107 / T167 | **00:04Z batch** (waiter, W281); **00:05 / 00:06 / 00:46Z**; backups **00:20 / 00:50 / 01:30Z** | **Night batch:** stack exp89r or exp89q; exp75 (v1, never re-push); exp89p through the guarded T54; exp83c only on an exp89p file-specific failure, never on a limit error. -m starts with the file token. Backups list first and send only a missing due file | pending; **crons will not fire, so this needs W281** | `CONTEXT.md` l.3899-3907, l.4051-4054; `round28/report.json` R28-A1, R28-A4 |
| **T171** (new) | **01:13Z .. 18:13Z hourly** (04:13-21:13 MSK) | Autonomous research rounds. A round is skipped while the previous one runs or a submit window executes; Kaggle API calls are kept minimal | at risk (cron-based; W288) | `CONTEXT.md` l.4084-4087 |
| **T172** (new) | **02:00Z** (05:00 MSK) | E10 cutoff: after it, an E10 copy needs the user's yes (dummy it and ask) | standing | `CONTEXT.md` l.4089-4091 |
| **T173** (new) | **05:10-06:00Z** (08:10-09:00 MSK) | The user is travelling and the laptop is asleep. Nothing is scheduled in the window. Standby may hang loops and kill background waiters | info | `CONTEXT.md` l.4066-4072 |
| **T174** (new; POST-WAKE) | **06:07Z** (09:07 MSK), waiter 37cd3141 | Check AC and poll-header age; restart stale E10/feed loops; **re-arm any dead waiter from the W281 list**; confirm the night files; notify if on battery | pending (cron -> needs waiter) | `CONTEXT.md` l.4070-4072; `round28/report.json` R28-A1 (1) |
| T159 | exp89q ~07:02-07:55Z; **exp89p 07:38-08:35Z (both branches)**; exp89r ~08:41-11:00Z; exp75 ~09:05-10:05Z | **Night reads**, coded per MORNING TABLE v1.1 (1) and R26-A4 (a)/(b) as amended by W284 (ii); DIS files use parent-family windows | pending | `round28/report.json` next_focus; `CONTEXT.md` l.4021-4028 |
| T151 + W277 (2) | **07:23Z** prep (waiter 0f7afe09). **A-M1:** decide by the 08:40Z header, submit by 08:45Z. **B-M1:** by the 10:30Z header, submit by 10:50Z. **M2:** by 11:00Z, submit by 11:30Z | **Morning batch (<= 2 files)** from MORNING TABLE v1.1. Submit at the decision header. UNUSED is the default. Only PASSED dummies (exp89s l.3974; exp89q l.3915; exp89l only under W282 (b)). If our GPU quota runs out, teammates push; prepare folders with --owner and exact commands; never use their tokens | pending | `CONTEXT.md` l.3931-3955, l.4087-4089; `ideas_29sep/rank.json` |
| **W285** (new; = **R28-A5**; reopens W266 (2) / W278 (2)) | edits before **12:03Z** (best tonight after the freeze) | **FINALS CARD v4 still lacks R27-A8 (1)-(5).** Needed: <br>(1) conditional opener at l.31; <br>(2) П3 silver "~0.39–0.63 (база 0.51)"; <br>(3) token_refs keyed on file names, plus an E10 token and the night/morning exp89q split at ~06:00Z; <br>(4) "exp83c = 3"; <br>(5) pool per GAP RULE v2, up to 10.75 h. <br>Also: section 5 reminder at 22:43 MSK, not 22:30; the CI caveat = R28-A4 (vi); the SEC info line. **Log a CONTEXT correction of l.4029-4032** | not started (0 hits for `exp83c = 3` / `0.39`, ~20:08Z) | `round28/report.json` R28-A5, plan_issues 5; `round28/scan_plancheck.notes.md` |
| W19 / W73 / W102 / W93 / W165b / W261 | standing | ONE poller; header < 15 min old; never resubmit class C or ERRORed files; a SEC file only as V_pub (Q3). Dataset pre-push check on ref,size,lastUpdated only (baseline ft-weights 2026-09-23 23:54:03, n2a 2026-09-27 21:25:35; re-verified by full-slug search ~19:50Z) | standing | `CONTEXT.md` l.3331-3335, l.3692-3703, l.3834-3836; `round28/report.json` new_facts 8 |
| W266 (2) / T60 | **12:03Z** (15:03 MSK), FINALS waiter 2e9ce42e | Send card v4 (after W285). SEC files only as V_pub. Send only the ===== block; never tick | pending | `CONTEXT.md` l.3713, l.3834, l.4091-4092 |

## LATER (29 Sep ~12:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T152 | **18:37Z** (21:37 MSK), waiter ec670938 | FINAL proposal. Show any still-PENDING file with its pre-agreed swap | `CONTEXT.md` l.3714; `round26/report.json` R26-A4 (d) |
| T161 + W277 (1) | **19:43Z** (22:43 MSK), waiter for cron 64b9bb56 | Notify-only reminder + V_pub re-check (re-read poll.log; push if V_pub changed or a PENDING file turned terminal since 18:37Z) | `CONTEXT.md` l.4054-4056, l.4092 |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** The session never ticks by any route. If the user does nothing, #37 + #38 stay | `CONTEXT.md` l.3851-3855, l.4091-4092 |
| T153 | ~20:00-20:30Z | Verify API SELECTED = the user's pair | `CONTEXT.md` l.3474 |
| T162 | **21:05Z** (00:05 MSK 30 Sep), waiter ddc5884d | Last-call notify: if SELECTED is not the proposed pair, push the exact pair | `CONTEXT.md` l.4092; `round28/report.json` R28-A1 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; final public LB snapshot | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline: a submit must **finish** before it; re-ticks are allowed until then | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765; `CONTEXT.md` l.3848, l.3855 |
| T155 | 30 Sep 00:07Z, waiter 7c8c80dd | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715, l.2570-2598 |
| T133 / T170 | 3 Oct | GPU quota refresh | `round27/scan_hyp_nightdry.notes.md` |
| W29 / curator | after 29 Sep | Post-deadline list, plus z-shift I-029 (refutation reason (4) void, still post-deadline) and the MAX_UM 2.0 note | `round25/report.json` R25-A8 (d); `round28/report.json` R28-A6 (1) |

**Passed or finished time-bound items:**
- R8 new-mechanism cutoff (27 Sep 12:00Z) passed; the 28 Sep 12:00Z consolidation is superseded (T46; l.3392-3394).
- Round 28 was lost at 17:47Z (cron defect, not battery) and ran by hand 19:36-20:05Z (`round28/report.notes.md`).
- The ideas sweep ran at 20:00Z (l.4073).
- Friend replies: none awaited (last friend instruction 26 Sep, l.2175-2176).
- Teammates are a GPU / submit reserve only, and they now cover the morning if our quota runs out (l.4087-4089).
- T156: the tick deadline is 20:00 UTC = 23:00 MSK; never write "20:00" without "UTC".

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I327** (new) | "31 CronCreate calls (26 Sep 17:50Z .. 28 Sep 16:43Z) and ZERO prompts carrying any cron prompt text afterwards ... Background tasks DO wake the session" | `round28/scan_plancheck.notes.md` 19:45Z | Not yet in CONTEXT. The 20:07Z entry (l.4086) still relies on crons. Every night step fails silently without W281. |
| **I328** (new) | "probes 47 (00:06:04Z), 49 (00:50:26Z), 50 (05:02:26Z), 51 (12:14:52Z) were each submitted in a turn triggered by a task-notification from a background until-loop" | `round28/scan_plancheck.notes.md` 19:55Z | This is the proven wake path; use the same pattern for W281. |
| **I329** (new) | "The VS Code extension restart at 06:04Z (2.1.282 -> 2.1.283) wiped ~13 crons, and waiters would die the same way" | `round28/report.json` new_facts 5 | An overnight auto-update kills every waiter. The post-wake step must re-arm them (T174), and the message should tell the user not to restart or update VS Code. |
| **I330** (new) | "Modern Standby on AC 19:51:43-20:40:20 MSK with the poller unbroken; battery 21:07:28-21:21:19 MSK" | `round28/report.json` new_facts 5; `round28/scan_plancheck.notes.md` (Power) | The laptop still goes to standby on AC (Idle Timeout), and it briefly ran on battery after the "on AC" line (l.4035). The watchdog is the only guard. |
| **I331** (new) | "R27N-3 T54 code r[0] on exp89q rows -> IndexError in branch A"; "R27N-4 HARD FAIL regex contains 'limit'" | `round28/report.notes.md` 19:58Z | Supersedes I318. Both are still unfixed in every stored text; they must be fixed inside the freeze line (W284 (iii)(iv)). |
| **I332** (new) | "round27 PC27-03 measured from 'V1284 head patched ... mode = candidate', CONTEXT l.4025 says 'GPU shard 0 line' -> name one anchor" | `round28/report.notes.md` 19:58Z | With the wrong anchor, the exp89l gate could fail spuriously and cost ~0.5 GPU-h to re-run (W282 (a)). |
| **I333** (new) | "exp89l dummy deadline ambiguous (AMEND 4 keeps 23:30Z deadline)" | `round28/scan_hyp_prefreeze.notes.md` 19:50Z | If this is read literally, a branch-A exp89l built after 51's read (~21:40Z plus a ~35 min dummy) could be voided. W282 (b) scopes it to 08:40Z. |
| **I334** (new) | Truncation emulation: "floor(z,y,x) vs round: ALL 0.93340 -> 0.92842 (-0.00498) ... 44b6 -0.01310; 6bba -0.00425"; the float probes 32/33 "equal the int CSV under ANY int-casting scorer" | `round28/scan_recheck.notes.md` 20:05Z, 20:15Z | This voids the float anchor used by the v3 s_merge "lab gains do not transfer" verdict. The magnitude reference is for I-029 only (W286 (1)). |
| **I335** (new) | DUMMY LAB: "SEC n2a pairs ... all on 6bba_05db0fb1 (TP -1, FP +4..+6)"; "CI pairs ... -0.00549 ... LB: CI +0.001 -> dummy lab has the wrong sign for CI"; "Refiners (coordinject) saw 171/199 train stems -> dummy clips likely in-sample for CI too" | `round28/scan_recheck.notes.md` 20:10Z | This is a weak negative prior for SEC, which has never been read on LB; the first read is exp89p vs exp85a tonight. The dummy lab must never be read as a sign for coordinate changes (W284 (vi)). |
| **I336** (new) | "CI lowers error on 3/4 dummy clips incl. both 6bba clips where it LOSES 2 TP edges each -> error cut does not convert to edges monotonically" | `round28/scan_recheck.notes.md` 20:14Z | This is only in a scan note. It is the reason the CI prior must stay LB-driven (the R28-RC-C prior cut was refuted). |
| **I337** (new) | "The best rejected 'if the user insists' fallbacks would be IB29-02 (FLOW_Z_WEIGHT 0.6) or MD-1 (LEARNED_BONUS 0.75) ... both have expected value about 0 and sign <= 0" | `research/wf_ideas_v4/ideas_29sep/rank.json` | In autonomous mode with GPU not binding (l.4087), these are the tempting spends. They are pre-refuted, so do not build them. |
| I315 | "VIDEOIDLE ... 300 s (display-off idle -> Modern Standby entry 'Idle Timeout')" | `round27/scan_plancheck.notes.md` 15:48Z | Confirmed again on AC by I330. |
| I316 | "RETRY_SLACK_S = 210" per failed attempt inflates L_hi | `tools/runtime_ledger.py` l.42 | Now built into the admit edge (22:59:57Z + 210 s per failed attempt, W284 (i)). |
| I317 | API load: feed ~900 calls/day was the largest share; another account was banned for "Resource abuse" | `CONTEXT.md` l.3988-3997 | The hourly rounds (T171) must keep Kaggle calls minimal (l.4087). |
| I319 | exp89p at 00:46Z reads 07:38-08:35Z vs the A-M1 decision "latest 08:40Z" (thin) | `round27/scan_hyp_nightdry.notes.md` | 00:46Z is now final in both branches (l.4057-4058), so A-M1 may be UNUSED ('?'). |
| I320 / I321 / I322 / I323 / I324 / I325 / I326 | A-M1 CI tail reads 19:39Z > 19:30Z; dataset diff on ref,size,lastUpdated only; standby-lost crons (now: all crons); P2 look-check near threshold (19:36Z max 4/h); per-run GPU/I/O variance; J_adj linear node term; Q3 ambiguity | `_curation/27/watch.json`; `round28/scan_browser.notes.md` | Unchanged; I322 is subsumed by I327. |
| I303 / I304 / I305 / I307 / I308 / I309 / I310 / I311 / I313 | DIS readable only as abs(dd) >= 0.002; UP '0' = not higher; dummy lab never a sign read; K READMIT -0.0008; Georgy Mamarin 8/10; {exp85a, exp75} first on bronze; the user's tick is the only path; empty exp12/13 dirs; SEC 0/5 | `_curation/27/watch.json` | Unchanged. I305 is reinforced by I335. |
| I287 / I290 / I294 / I297 / I301 / I302 / I278 / I72 / I116 / I145 | Unchanged older insights | `_curation/26/watch.json` | - |

**Resolved since ~16:25Z (curation 27):**
- I306: stays retired (logged at l.4021-4028).
- I318: superseded by I331.
- I314: handled by W277 (2).
