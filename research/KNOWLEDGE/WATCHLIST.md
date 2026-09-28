# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-28 ~20:58 UTC (curation 29). This updates the curation-28 build of 28 Sep ~20:15Z (full text in the git history of this file; structured copy `research/KNOWLEDGE/_curation/28/watch.json`). Older predecessors: `_curation/27/watch.json` down to `_curation/18/watch.json`. Rows not repeated here are unchanged there. The TASK_LOCAL_SESSION, TASK_CLOUD_SESSION and v3 FINAL_REPORT rows have not changed since `_curation/20/watch.json`.

**Sources read for this update:**
- `CONTEXT.md`:
  - It now has 4,154 lines, and `## 9. Literature` starts at l.4134.
  - Entries new since curation 28 (l.4094-4133):
    - 20:13Z: SECOND TRIGGER PATH, background timers (l.4094-4103);
    - 20:18Z: RULE v2.1 + exp89l DUMMY GATE + NO-FREEZE FALLBACK (l.4104-4126);
    - 20:18Z: SESSION CRONS NEVER FIRE -> WAITERS (l.4127-4133).
- `git log`: 9bcd86f .. **e42769c** (20:18Z; round 28 is now tracked).
- `research/wf_ideas_v4/round29/`, untracked, written 20:18-20:55Z:
  - `report.json` (**R29-A1..A8**, new_facts 1-12, plan_issues (a)-(q)) and `report.notes.md`;
  - the stored night texts: `night_checklist.md` (sha8 075152c4), `freeze_line_template.md` (c675d7c3), `finals_card_v5_ru.md` (aadead83);
  - `scan_*` and `v_*` notes and JSON.
  - **There is no `REPORT.md`**: the subagent harness blocked the write (`round29/report.json` report_md_ru_note).
- `experiments/lb_poll/poll.log`: newest header **20:53:11Z** (l.25457). 56640366 (probe 51) PENDING.
- Loops:
  - `experiments/e10_watch/watch_loop.log`: RUN 32 20:42Z, signals 0, next run 21:41:53Z.
  - `experiments/discussions/feed_loop.log`: 20:27:27Z, 0 new, E10 FLAG none.
- Local read-only checks, ~20:55Z:
  - `Win32_Battery` BatteryStatus **2 (AC), 78%**. timer.sh processes are alive; round 29 counted 31 waiters at 20:45Z (`round29/report.json` new_facts 9).
  - The sha8s of the three round-29 texts equal the values R29-A1 calls "now", so **the R29-A1 fixes are not applied yet**.
  - `grep -c "night_checklist\|finals_card_v5" CONTEXT.md` = **0**.
  - The anchored freeze regex `^- 2026-09-2[89] [0-9:]+ UTC, W4 FREEZE: NIGHT 29 Sep` = 0 hits, which is expected before 23:33Z.
  - `round27/finals_card_v4_ru.md` l.1 has no SUPERSEDED banner.
  - `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66 still reads "OUR = 0.957 ... SC >= 0.958".
  - `experiments/RESULTS.md` probe rows still end at probe 46 (l.79).
  - `grep -c DET_THRESHOLD CONTEXT.md` = 0.

All times are UTC. The user thinks in MSK (UTC+3) (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at ~20:58Z, 28 Sep:**
- **Best display 0.958:** exp85a (probe 50, 56629533). V_pub = exp85a.
- **Rank:** #140 of 3,974 at 20:41Z, 13th of 22 in the 0.958 block, 127 teams >= 0.959 (`round29/report.json` new_facts 2).
- **Probe 51 exp87a (56640366):**
  - PENDING at 20:53:11Z.
  - Expected ~21:31-21:42Z (00:31-00:42 MSK).
  - 10.2 h mark = 22:26:57Z; admit edge = 22:59:57Z, with the corrected test "header + 210 s x failed attempts <= 22:59:57Z" (`round29/report.json` R29-A3 (1), plan_issues (e)).
- **Slots:** 28 Sep is 5 of 5 used.
- **Trigger path:** background timer.sh waiters are the PRIMARY path, and the crons are secondary (`CONTEXT.md` l.4094-4103, l.4127-4133).
  - **All waiter message texts are stale** (they point to R27N-2/R27N-3, "00:46", "CI only until 01:45", card v4). They are pointers only, and must not be re-armed (`round29/report.json` plan_issues (c)).
- **User:** asleep, autonomous mode (`CONTEXT.md` l.4081-4093). The session never ticks.
- **CRITICAL (new):**
  - **The stored nb_try dedupe FAILS OPEN** when the kaggle 2.2.4 outdated-version warning is printed to stdout. The idempotent backups would then submit a **duplicate**.
  - **An empty T54 fires exp89p at once.**
  - Both come from `round29/report.json` R29-A1 (a)/(b) and were mock-tested (`round29/report.notes.md` 20:47-20:48Z).
  - Neither is fixed yet.

**Changes since ~20:15Z (curation 28):**
- **Done:**
  - W281 (1) waiters armed (l.4094-4103, l.4127-4133) and W281 (2) OPS line (l.4127-4133);
  - W288 (hourly round timers, l.4097-4099);
  - W282 (a)-(d) (l.4104-4126, quoting the 20:13:02Z PENDING header);
  - W285 content, as a new file `round29/finals_card_v5_ru.md`. It is not yet logged; see W290.
- **Reopened or corrected:**
  - W282 (c): the admit-edge slack sign is inverted (R29F-4). It moves to I345 and W289.
  - W282 (d) / the stored G4: the `-F` form is vacuous (PC29-01). It moves to W290.
  - W281 (3): CONTEXT l.4095-4096 still blames "battery standby" for the lost rounds. This moves to **W297**.
- **New:**
  - actions **W289-W297**;
  - reminders **T177-T180**;
  - insights **I338-I348**.

---

## OVERDUE / DUE NOW

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W289** (new; = **R29-A1**) | **FIX THE TWO STORED NIGHT TEXTS, then recompute their sha8.** <br>**(a)** In `night_checklist.md` l.40, replace the nb_try dedupe with the fail-closed parser (slice from the first `ref,` line; exit 0 found / 10 absent / 2 parse error; rc != 10 -> PARSE FAIL + continue). The exact snippet is stored in `round29/report.notes.md` under "R29-A1 exact snippets". <br>**(b)** Apply the same slice to G2 (l.84-91) and T54 (l.142-149), plus the `[ -n "$T54" ] ||` fallback. <br>**(c)** A superseding banner. <br>**(d)** A PRELUDE note: UTC only from `date -u` / `[DateTime]::UtcNow` / `datetime.now(timezone.utc)`. <br>**(e)** Template l.76: "section P". <br>**(f)** Template item (9): tie wording. <br>**(g)** Item (10): stale timer wording superseded; item (8) counts timer.sh processes, not `WAITER_` tags. <br>**(h)** Item (1): S0/S1 for P. <br>Keep nb_try v3's order. Re-run `bash -n` and the mocks | **not started** (sha8 still 075152c4 / c675d7c3 at ~20:55Z) | **NOW**; before the 23:33Z freeze timer, ideally before 51 reads (~21:30Z) | `round29/report.json` R29-A1, new_facts 5, plan_issues (b); `round29/report.notes.md` 20:47-20:48Z |
| **W290** (new; = **R29-A2**; absorbs the W285 log line and W284 (v)) | **ONE CONTEXT entry above `## 9. Literature`, without the freeze header shape.** It must say: <br>**(1)** Every night step runs `round29/night_checklist.md` (new sha8), and the freeze is written from `freeze_line_template.md`. Timer texts are pointers only. R27N-3's T54 and "Expect Successfully submitted", and R27N-4's nb_try, are superseded. This also corrects l.4054. <br>**(2)** The freeze check is ONLY the anchored `grep -E` form; `-F` is invalid (it already matches via l.4125). <br>**(3)** A success prints "N submissions remaining today."; parsers slice from the first `ref,` line. <br>**(4)** The UTC-source rule. <br>**(5)** A CORRECTION of the 16:26Z entry (l.4029-4032): card v4 never got the R27-A8 edits. The 12:03Z and 18:37Z fills use `finals_card_v5_ru.md` (aadead83). <br>**(6)** The MORNING TABLE v1.1 **A-M2 precedence**, logged pre-score. <br>**Also:** put a SUPERSEDED banner on line 1 of `round27/finals_card_v4_ru.md`, because the 12:03Z waiter opens v4 | **not started** (CONTEXT grep = 0; no banner) | **NOW**, right after W289 and before 23:33Z | `round29/report.json` R29-A2, plan_issues (a)(c)(g)(l); `CONTEXT.md` l.4054, l.4125 |
| **W291** (new; = **R29-A3**; extends T165/W283) | **At 51's read, in branch A, build exp89l at once.** <br>- Build STOP unless sha8 cad1d47f. <br>- Run the PRE-PUSH dataset check and log the R8 line. <br>- Push the dummy. <br>- Gate it with a **RULE v2.1-specific check, NOT scratchpad `gate85.py`** (which checks whole-kernel <= 1,900 s only). <br>- At 07:23Z, only verify the PASS. <br>In branch B, nothing is built | pending (51 PENDING at 20:53:11Z) | at 51's read, ~21:31-21:42Z; the dummy must PASS before the **08:40Z** A-M1 header | `round29/report.json` R29-A3, plan_issues (f)(i); `CONTEXT.md` l.4108-4118 |
| W126 (part 2) | RESULTS.md rows for probes **47 (0.955), 48 (0.957), 49 (0.955), 50 (0.958)**; later 51 and the night probes | **overdue** (probe rows end at 46, `experiments/RESULTS.md` l.79) | before the finals card (29 Sep 12:03Z) | `CONTEXT.md` l.3530, l.3615, l.3639, l.3856 |
| **W296** (new; replaces W280) | Write `research/wf_ideas_v4/round29/REPORT.md` verbatim from `report.json` report_md_ru; the subagent's write was blocked. Commit round 29 (untracked) with named paths, as the user, with no Co-Authored-By. REPORT.md for rounds 24-27 remains optional/low | not started | with the next CONTEXT commit | `round29/report.json` report_md_ru_note; `git status` (`?? research/wf_ideas_v4/round29/`); `memory/feedback-git-no-coauthor.md` |
| **W286** (carried; = R28-A6) | **(1)** CONTEXT line: floatout probes 32/33 were no-ops under an int-casting scorer; lab consistent with 744093; z-shift I-029 stays post-deadline. **(2)** Fix `e10v3/runbook.notes.md` l.66 to "OUR = 0.958 (exp85a), so SC >= 0.959". **(3)** KEY FACTS, now as R29-A8 (1) numbers: #140 / 3,974, 127 >= 0.959 | **overdue** (l.66 still stale ~20:55Z; `grep int-casting CONTEXT.md` = 0) | before the next E10 read; (1)(3) with W290 | `round28/report.json` R28-A6; `round29/report.json` R29-A8 (1) |
| W279 (1) | Log RC-C: "DET_THRESHOLD stays closed for 29 Sep and is never a morning filler" | not started (`grep -c DET_THRESHOLD CONTEXT.md` = 0) | before **07:23Z** 29 Sep | `round27/report.json` R27-A9 (1) |
| **W297** (new; contradiction) | CONTEXT l.4095-4096 says the "15:47, 18:17 and 20:47 MSK rounds were lost to a busy session / battery standby". Round 28 showed that at 20:47 MSK the laptop was on AC and awake, and the cause was the cron defect. W281 (3), the Russian correction message, is unverifiable from the files. Fold a one-line correction into W290 | not started | with W290 | `round28/report.json` new_facts 5, plan_issues 8; `CONTEXT.md` l.4127-4129 |
| W202 + W244 / W176 / W177 / W182 / I208 / W57 / W66 / W31 / W72 / W150 | Old info and curator lines; ROUND RECORD; LESSONS H1; no NEVER_SUBMIT in exp70j/exp70k; old text fixes | overdue, low | H2 29 Sep 23:00Z | `_curation/24/watch.json`, `_curation/26/watch.json` |

## NEXT 24 H (28 Sep ~21:00Z -> 29 Sep ~21:00Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W289, W290 | **now** | Fix the night texts; log the pointer, card v5 and A-M2 precedence entry | not started | R29-A1, R29-A2 |
| T100 | E10 hourly at hh:41Z (next 21:41Z) until 29 Sep 12:00Z; feed every 90 min (next ~21:57Z) until 29 Sep 23:59Z | E10 v3 trigger **>= 0.959** (the runbook l.66 text is stale; see W286 (2)). **Before 02:00Z:** build + dummy an E10 copy per the rule. **After 02:00Z:** the copy needs the user's yes. A PASSED E10 copy displaces exp89p and costs both morning decisions (R29F-7) | live (RUN 32 20:42Z; feed 20:27Z) | `experiments/e10_watch/watch_loop.log`; `CONTEXT.md` l.4089-4091; `round29/report.json` plan_issues (p) |
| **T165 / W283 / W291** | **~21:31-21:42Z expected** (00:31-00:42 MSK); 10.2 h 22:26:57Z; **admit: header + 210 s x f <= 22:59:57Z** | **Read probe 51.** <br>- `uptest.py save S1_51` / `compare S1_1214Z S1_51` (count 53); the backup is the E10 converter (W293). <br>- '+'/'0u' (incl. UNPROVEN-ins) -> branch A (exp89r) + build exp89l (W291). Otherwise -> branch B (exp89q). <br>- Log the read line + KEY FACTS and update RESULTS (W126) | pending (PENDING 20:53:11Z) | `round29/report.json` R29-A3; GAP RULE v2 `CONTEXT.md` l.4009-4020 |
| **T177 / W292** (new; = **R29-A5**; replaces T166) | **22:47Z** round timer (01:47 MSK) | **Skip it**, or do one short in-session step (W289/W290/W291 checks, the 51 read) that **ends by 23:25Z**. No full multi-agent round | pending | `round29/report.json` R29-A5 (1), next_focus |
| **T178** (new) | **23:25Z -> ~00:50Z** (exp89p listed) | Launch no workflow round. Timer notices queue behind a busy foreground | standing | `round29/report.json` R29-A5 (2), plan_issues (j) |
| **T143 + W284** (updated; = R28-A4 + **R29-A4**) | **23:33Z** timer (02:33 MSK) | **W4 FREEZE LINE** from `freeze_line_template.md` (after W289). Paste it as a PLAIN entry: no code fence, real UTC in the header, item (10) carrying the new checklist sha8. Then the anchored regex must = exactly 1. The no-freeze fallback is `CONTEXT.md` l.4119-4124 | not started (pending the timer) | `round29/report.json` R29-A4 (1); `CONTEXT.md` l.4104-4126 |
| T169 | until 29 Sep 00:00Z | 28 Sep is 5 of 5 used: a "limit" error is expected, not a file failure. The daily regex must not match a bare "limit" (R29F-3) | standing | `round28/report.json` new_facts 8; `round29/report.json` plan_issues (d) |
| T126 | 29 Sep 00:00Z | Slot reset (5 new slots) | - | `CONTEXT.md` l.3367 |
| T20 / T107 / T167 (updated) | **00:04Z batch** (timer); T54 = max(00:46Z, exp89q actual + 40 min) (timer 00:44Z); backups **00:20 / 00:50 / 01:30Z** | **Night batch:** it runs `night_checklist.md` only: G0-G5 with the anchored FREEZE check, nb_try with the fail-closed dedupe, the guarded T54 in both branches, exp83c on exit 2, exit 3 = STOP + push. Log the "N submissions remaining today" count. Any missing due file is sent LATE until **01:45Z**; after that, CI by 08:30Z and non-CI by 11:30Z | pending (timers alive) | `round29/report.json` R29-A4 (2), R29-A5 (4); `CONTEXT.md` l.4097-4099 |
| **T171 / T179** (updated) | **01:13Z .. 18:13Z hourly** (04:13-21:13 MSK), timers | The 01:13Z round runs only if all three night files are listed. Every round from 01:13Z to 06:17Z starts with checklist section 5 (G2 list, 1 API call, LATE check). Kaggle calls stay minimal (I317) | pending | `CONTEXT.md` l.4084-4087, l.4097-4099; `round29/report.json` R29-A5 (3)(4) |
| T172 | **02:00Z** (05:00 MSK) | E10 cutoff: after it, an E10 copy needs the user's yes (dummy it and ask) | standing | `CONTEXT.md` l.4089-4091 |
| T173 | **05:10-06:00Z** (08:10-09:00 MSK) | The user is travelling and the laptop is asleep. timer.sh fires on wake (30 s UTC loop) | info | `CONTEXT.md` l.4066-4072, l.4096-4097 |
| T174 + W293 (updated; = **R29-A6**) | **06:07Z** post-wake (timer) | Check AC, poll-header age and the night files; restart stale E10/feed loops; **re-arm only dead waiters** (never re-arm to fix texts). If S1_51 is missing, run `uptest.py save S0_night` | pending | `round29/report.json` R29-A6 (3), rejected (re-arming) |
| **W293** (new; = **R29-A6**) | before exp89p reads (07:38-08:35Z) | **UP test for P:** S0 = S1_51 (count 53); S1 = `uptest.py save S1_P` at the first header with exp89p terminal (count 54). The API-free backup converts an E10 snapshot's `leaderboard_rows` into `_lb/E10_<TS>/lb.csv` (one-liner in `round29/scan_plancheck.json` PC29-05). LastSubmissionDate is never an UP marker | pending | `round29/report.json` R29-A6, new_facts 10 |
| T159 | exp89q ~07:02-07:55Z; **exp89p 07:38-08:35Z**; exp89r ~08:41-11:00Z; exp75 ~09:05-10:05Z | **Night reads**, per MORNING TABLE v1.1 with the W290 (6) precedence | pending | `CONTEXT.md` l.3931-3955; `round29/report.json` R29-A2 (6) |
| T151 + W277 (2) | **07:23Z** prep (timer). **A-M1:** decide by the 08:40Z header, submit by 08:45Z. **B-M1:** by the 10:30Z header, submit by 10:50Z. **M2:** by 11:00Z, submit by 11:30Z | **Morning batch (<= 2 files).** Only PASSED dummies (exp89s; exp89q; exp89l under the v2.1 gate). UNUSED is the default. If our GPU quota runs out, teammates push with --owner; never use their tokens | pending | `CONTEXT.md` l.3931-3955, l.4087-4089, l.4116-4118 |
| **T180 / W294** (new; = **R29-A7**) | at each morning submit; the 18:37Z text | Start a local-only **late-read watcher** per morning ref. If it fires after 18:00Z and V_pub or the pair changes, push ONE Russian MSK line. The 18:37Z proposal lists the pending reads: A-M1 CI ~16:55-17:57Z (tail ~19:39Z); A-M2 ~16:20-17:15Z; B-M1 ~15:25-16:15Z | pending | `round29/report.json` R29-A7, plan_issues (k) |
| W19 / W73 / W102 / W93 / W165b / W261 | standing | ONE poller; header < 15 min old; never resubmit class C or ERRORed files; SEC only as V_pub (Q3). Dataset pre-push check (ft-weights 2026-09-23 23:54:03, n2a 2026-09-27 21:25:35) | standing | `CONTEXT.md` l.3331-3335, l.3692-3703, l.4112-4114 |
| W266 (2) / T60 (updated) | **12:03Z** (15:03 MSK), timer | Fill and send **card v5** (`round29/finals_card_v5_ru.md`, aadead83), **not v4**, whatever the timer text says. Every pair is anchored on V_pub (partner rule v2, user 16:32Z). Send only the ===== block; never tick | pending | `round29/report.json` R29-A2 (5), plan_issues (l)(m); `CONTEXT.md` l.4041 |

## LATER (29 Sep ~12:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T152 | **18:37Z** (21:37 MSK), timer | FINAL proposal from card v5. Show any still-PENDING file with its MSK window and pre-agreed swap (T180) | `CONTEXT.md` l.3714; `round29/report.json` R29-A7 (2) |
| T161 | **19:43Z** (22:43 MSK), timer | Notify-only reminder + V_pub re-check | `CONTEXT.md` l.4054-4056, l.4092 |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** The session never ticks by any route. If the user does nothing, #37 + #38 stay | `CONTEXT.md` l.3851-3855, l.4091-4092 |
| T153 | ~20:00-20:30Z | Verify API SELECTED = the user's pair | `CONTEXT.md` l.3474 |
| T162 | **21:05Z** (00:05 MSK 30 Sep), timer | Last-call notify: if SELECTED is not the proposed pair, push the exact pair | `CONTEXT.md` l.4092, l.4099 |
| W177 H2 / T49 | 23:00Z / 23:00-23:45Z | LESSONS H2; final public LB snapshot | `_curation/20/watch.json`; `CONTEXT.md` l.2619 |
| T11 / T163 | **29 Sep 23:59Z** (02:59 MSK 30 Sep) | Deadline: a submit must **finish** before it; re-ticks are allowed until then | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765; `CONTEXT.md` l.3848, l.3855 |
| T155 | 30 Sep 00:07Z, timer | POST-DEADLINE job: private read v2 + L1-L7 | `CONTEXT.md` l.3714-3715, l.4131 |
| **W295** (new; = **R29-A8**) | next CONTEXT entry / curation pass | KEY FACTS 20:41Z; the 744093 integer check covers every finals candidate (13 CSVs, int64 z/y/x); an I-320 narrow annotation: "~1/6 comes from one lever, not a transfer law". Do not publish the "5/14" class table | `round29/report.json` R29-A8, new_facts 8, rejected |
| T133 / T170 | 3 Oct | GPU quota refresh | `round27/scan_hyp_nightdry.notes.md` |
| W29 / curator | after 29 Sep | Post-deadline list, plus z-shift I-029 and the MAX_UM 2.0 note | `round25/report.json` R25-A8 (d); `round28/report.json` R28-A6 (1) |

**Passed or finished time-bound items:**
- R8 new-mechanism cutoff (27 Sep 12:00Z) passed; the 28 Sep 12:00Z consolidation is superseded (T46; l.3392-3394). No new lever reaches R8 (`round29/report.json` new_facts 12).
- Round 29 ran 20:18-20:55Z from the 20:17Z timer (`CONTEXT.md` l.4097; `round29/report.notes.md`).
- W288 / T166: the round timers exist (l.4097-4099).
- Friend replies: none awaited (last friend instruction 26 Sep, l.2175-2176).
- T156: the tick deadline is 20:00 UTC = 23:00 MSK; never write "20:00" without "UTC".

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I338** (new) | "kaggle 2.2.4 _check_response_version prints the 'outdated kaggle version' warning with print() -> STDOUT ... Old nb_try dedupe ... on warning-first list -> rc 1 = would SUBMIT a duplicate (mock test)" | `round29/report.notes.md` 20:47Z | This is the top overnight risk: a duplicate submit burns morning slots. Not yet fixed in the checklist (W289). |
| **I339** (new) | "`date -u -d \"\"` = 2026-09-28T00:00:00Z (fires at once)" | `round29/report.notes.md` 20:48Z | An empty T54 sends exp89p immediately, breaking the 40-min spacing. The fallback line in W289 (b) is required. |
| **I340** (new) | "'Successfully submitted' appears in 0 of 44 real submit outputs"; success prints "N submissions remaining today." | `round29/report.json` new_facts 4 | Any check waiting for "Successfully submitted" (R27N-3) never passes. Superseded only once W290 (3) is logged. |
| **I341** (new) | "PowerShell Get-Date -Format u prints local MSK with a 'Z' suffix (23:38:48Z at 20:38:48Z)" | `round29/report.json` new_facts 6 | A 3 h error in a hand-typed header or deadline test. Scripted paths are safe; ad-hoc session commands are not (W289 (d), W290 (4)). |
| **I342** (new) | "grep -cF 'W4 FREEZE: NIGHT 29 Sep' CONTEXT.md = 1 already (CONTEXT l.4125 ...)" | `round29/scan_plancheck.notes.md` 20:25Z | A missed freeze would pass the stored G4 and skip the no-freeze fallback. Only the anchored `-E` form is valid (W290 (2)). |
| **I343** (new) | "'mode = candidate' == 'GPU shard 0' timestamps ... CI adds 416-443 s -> exp89l compute ~1,475-1,502 s"; "scratchpad gate85.py: whole-kernel <= 1900 only" | `round29/scan_plancheck.notes.md` | This retires I332 (the anchors coincide). Using gate85.py for exp89l could FAIL a good file (W291). |
| **I344** (new) | "LB CSV LastSubmissionDate = newest SCORED submission (S1_0934Z: 00:50:37 = probe 49 0.955 while best was 48 0.957) -> not a best marker" | `round29/scan_plancheck.notes.md` | This could mis-code an UP test at the P read (W293 (4)). |
| **I345** (new) | R29F-4: "the admit-edge slack sign is inverted in R28-A4 (i) and the 20:18Z (c) text"; the correct test is "header + 210 s x f <= 22:59:57Z" | `round29/report.json` plan_issues (e); `CONTEXT.md` l.4122-4123 | The logged fallback (l.4122-4123) still carries the wrong sign. It matters only with failed poll attempts near 22:59Z. Fix it in the freeze item (1) and W290. |
| **I346** (new) | MORNING TABLE v1.1: "(1) 'Only DIS + keeps DIS 2.25 in a morning file' vs (2) A-M2 'else Rr + -> exp89q'" | `round29/scan_plancheck.notes.md`; `CONTEXT.md` l.3931-3955 | This must be resolved pre-score (W290 (6)), or the A-M2 choice becomes post-hoc. |
| **I347** (new) | Lab embryo consistency: "division fork-set 11 arms same 4 / opp 3 / one-zero 4, Spearman 0.27 ... geometry+node-set 3 arms same 3/3 (Pearson 0.996)" | `round29/scan_recheck.notes.md` (B) | Only in a scan note. Division-lever lab signs barely transfer between embryos, but geometry levers do. This supports keeping the finals choice LB-driven. No plan change (`round29/report.json` rejected RC-C). |
| **I348** (new) | "nothing checks for LATE night files between 01:30Z and 06:07Z"; "01:30Z waiter text 'CI only until 01:45 UTC' vs R27N-2 (7) LATE cutoffs CI 08:30Z / non-CI 11:30Z" | `round29/scan_plancheck.notes.md`; `round29/report.json` plan_issues (j) | Covered only if the 01:13-06:17Z rounds start with checklist section 5 (T179). |
| I329 | "The VS Code extension restart at 06:04Z ... wiped ~13 crons, and waiters would die the same way" | `round28/report.json` new_facts 5; `CONTEXT.md` l.4131-4133 | Still the residual risk: timer.sh waiters die with a restart. The detached poll/e10/feed loops survive, and the user can say "продолжи". |
| I330 / I315 | Modern Standby on AC (Idle Timeout 300 s); battery excursion 18:07-18:21Z | `round28/report.json` new_facts 5; `round27/scan_plancheck.notes.md` 15:48Z | timer.sh loops every 30 s on the UTC clock and fires on wake (l.4096-4097). A standby still delays it. |
| I334 / I335 / I336 | Truncation emulation -0.00498 (floatout no-ops); dummy lab wrong sign for CI; CI error cut does not convert to edges monotonically | `round28/scan_recheck.notes.md` 20:05-20:15Z | Still not in CONTEXT (W286 (1)). Every finals CSV is integer (`round29/report.json` new_facts 8). |
| I337 | IB29-02 / MD-1 "if the user insists" fallbacks have expected value about 0 and sign <= 0 | `research/wf_ideas_v4/ideas_29sep/rank.json` | Autonomous mode (l.4087) makes these tempting. Do not build them. |
| I316 / I317 / I319 | RETRY_SLACK_S = 210; API load and the "Resource abuse" ban; exp89p at 00:46Z reads 07:38-08:35Z vs A-M1 at 08:40Z (thin) | `tools/runtime_ledger.py` l.42; `CONTEXT.md` l.3988-3997; `round27/scan_hyp_nightdry.notes.md` | Unchanged. |
| I320-I326, I303-I313, I287-I302, I278, I72, I116, I145 | Unchanged older insights | `_curation/27/watch.json`, `_curation/26/watch.json` | - |

**Resolved since ~20:15Z (curation 28):**
- I327 and I328: logged at `CONTEXT.md` l.4127-4133; timers are the primary path.
- I332: the anchors coincide (I343), and RULE v2.1 is logged (l.4105-4107).
- I333: the exp89l gate deadline is scoped to 08:40Z (l.4116-4118).
- I331: nb_try v3 order and the guarded T54 are in `night_checklist.md` (`round29/report.json` plan_issues (d)(q)). The remaining parser defect is I338/I339.
