# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-28 ~11:00 UTC (curation 25). This updates the curation-24 build of 28 Sep 07:25Z (full text in the git history of this file, commit a256dcb). Predecessors: `research/KNOWLEDGE/_curation/24/watch.json`, `_curation/23/watch.json`, `_curation/22/watch.json`, `_curation/21/watch.json`, `_curation/20/watch.json`, `_curation/18/watch.json`. Rows not repeated here are unchanged there. The TASK_LOCAL_SESSION, TASK_CLOUD_SESSION and v3 FINAL_REPORT rows are unchanged since `_curation/20/watch.json`.

**Sources read for this update:**
- `CONTEXT.md` has 3,737 lines, and `## 9. Literature` starts at l.3717. New entries since curation 24 (l.3522-3716):
  - 07:28Z exp86a/b/c gates PASS; 07:32Z probe 47 read;
  - 07:43Z ROUND 24 PRE-SCORE 1/3, 2/3 and 3/3, plus the W4 LIFT SPLIT; 07:44Z exp87a/b/i builds and the ledger rule;
  - 07:47Z user answers; 07:54Z probe 49 read; 09:07Z knob arms exp88a/b/c;
  - 09:35Z probe 48 read (0.957) and W2b TABLE v5 AMENDMENT A;
  - 10:16Z exp87a/83c/88a/88b gates PASS, and the private hedge proposal;
  - 10:19Z user answers (3+2 yes; tick by 20:00 UTC = 23:00 MSK);
  - 10:45Z teammate GPU, dataset sharing and the pre-push rule; 10:47Z the user says yes to morning CI files; 10:52Z schedule restored (session cron).
- `git log`: f40d44b, 19c24b5, 031e152, c91ae89, 3c66202, c16215b, 9014628, a599958, b618f7b, 1b5e912, 7f50382, ce23262, a256dcb, 74caff9. The last one is 13:52 local = 10:52Z; git dates are local time (UTC+3). `git log -12 --format=%b | grep -ci co-author` = 0.
- `git status` 10:55Z: `experiments/lb_poll/ledger.md` and `poll.log` modified; `research/wf_ideas_v4/round25/` untracked.
- `research/wf_ideas_v4/round25/report.json` is complete (10:52Z), with actions **R25-A1..A9** and plan_issues 1-15. Also read: `report.notes.md`, `scan_plancheck.notes.md`, `scan_recheck.notes.md`, `scan_hyp_sched29.notes.md`, `scan_hyp_private.notes.md`, `scan_browser.notes.md`, `v_plancheck_pc25-04.notes.md`, `v_hyp_sched29_r25s-7.notes.md`. **Round 25's sources stop at CONTEXT 10:19Z** (`report.notes.md` 10:42Z), so the round missed the 10:45Z, 10:47Z and 10:52Z entries.
- `experiments/lb_poll/poll.log` header **10:53:24Z** (l.21980): probe 50 (56629533) PENDING; 47/48/49 COMPLETE.
- `experiments/e10_watch/watch_loop.log` (RUN 22 at 10:24:33Z, 0 signals); `experiments/discussions/feed_loop.log` (10:36:55Z, E10 FLAG none); `experiments/discussions/digest_20260928T1036Z.md` (top public notebook 0.953; flag level > 0.957).
- Code and file checks:
  - `tools/runtime_ledger.py` l.80-83; `tools/kaggle_feed.py` l.172; `experiments/lb_poll/e10_watch_loop.py` l.78; `experiments/lb_poll/run_feed_loop.sh` l.10; `experiments/RESULTS.md` l.78-79;
  - `ls experiments | grep exp8[6-9]` finds no exp89 folder;
  - `ls tools | grep -E "uptest|gate_dummy"` finds neither file.

All times are UTC. The user thinks in MSK (UTC+3) (`CONTEXT.md` l.3683-3687). IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at 10:58Z, 28 Sep:**
- **Best display 0.957** = exp79a (probe 48, 56623105; exp70g + coordinject ALPHA 0.5; a CI file). UP of 33 teams, code C+ (`CONTEXT.md` l.3639-3645).
- **Rank:** #153 of ~3,966, with 137 teams above; 16th of 42 at 0.957 (l.3644; `round25/report.json` new_facts 5).
- **Probe reads today:**
  - 47 exp78b = 0.955, code '-' (l.3530-3538).
  - 49 exp78a = 0.955, code '-'. S1 fires: the DIV volume is closed, **BASE = exp70g**, and cap 6 is the optimum (l.3615-3624).
  - 48 exp79a = 0.957, code C+ (l.3639).
- **Probe 50 exp85a (the K lever) is PENDING** at 10:53:24Z (`poll.log` l.21980). Expected terminal ~11:54-12:50Z (`round25/report.json` new_facts 1).
- **28 Sep slots:** 4 used, **1 left** = probe 51 (W2b) (`round25/report.json` new_facts 1).
- **Dummies PASSED and ready:**
  - exp86a/b/c (l.3522-3529); exp86c only through the R25-A3 (b) waiver;
  - exp87a, exp83c, exp88a, exp88b (l.3659-3668);
  - exp75 (27 Sep dummy; `round25/report.json` new_facts 7).
- **exp88c:** COMPLETE on Kaggle, but no gate line is logged yet (`round25/report.notes.md` 10:46Z).
- **Finals unchanged:** #37 56563521 + #38 56563534 are ticked (l.3474). The user ticks by **20:00 UTC (23:00 MSK) on 29 Sep** (l.3683-3687).
- **User answers today:**
  - cap lift: yes, 2 files after 02:00Z (l.3608);
  - Q3 (SEC file as a final): OPEN (l.3610-3611);
  - E10 copies after 02:00Z: case by case (l.3612-3614);
  - 3 night + 2 morning: yes (l.3681);
  - morning CI files: yes, CI files by 09:30Z and non-CI by 11:30Z (l.3704-3708).
- **GPU:** the user reported ~5 h left at 10:45Z (l.3689). Round 25 estimated ~4.5-4.8 h (`round25/scan_plancheck.notes.md`).
- **Ops:** session cron re-created at 10:52Z (l.3709-3716). The detached poller, E10 loop and feed loop are running.

**Changes since 07:25Z (curation 24):**
- **Done:**
  - W235 (l.3539), W236 (l.3559), W237 (l.3578);
  - W239 (l.3598; live bases only); W241 (l.3592, l.3607);
  - reads T139 (l.3530), T140 (l.3615), T141 (l.3639);
  - W243 (2) (l.3645-3646; `tools/kaggle_feed.py` l.172 default 0.957);
  - W231 (b) (l.3663-3665); W247 main part (l.3709-3716); W238 gate lines (l.3522-3529).
- **Moot:**
  - W231 (a)/(d) and T123: exp80a, exp81-as-W2b and exp84a are dead after 47/49 (l.3619-3622).
  - T118 and T127: answered (l.3608).
- **Superseded:**
  - W242 and T106 -> W248 (R25-A1);
  - W245 (filler) -> W249/W256;
  - W234 and W230 -> W254 (R25-A7);
  - W240 -> W252 (R25-A5).
- **New:** actions **W248-W261**, reminders **T145-T156**, insights **I287-I302**.

---

## OVERDUE / DUE NOW (before probe 50 turns terminal, possible from ~11:54Z)

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W248** (new; = **R25-A1**) | **PRE-SCORE 1/2, "W2b AMENDMENT A2 + PROBE 50/51 READ RULE".** Quote the last header that shows 56629533 PENDING. The slot goes at 50's terminal header, **hard latest 13:00Z** (supersedes the 14:00Z of l.3543). R+ -> exp87a; R0/R-/R?, or 50 not terminal at 13:00Z -> **exp75** (replaces amendment A's exp83c, l.3653). Also: the -m text; ledger family safetail_ci; S0/S1 downloads; the '0u' code; the probe-51 REF rule; exp75 CI-RAN (dL = L_hi - 7.54 h); the 'ins-tail?' footnote | not started (`grep "AMENDMENT A2"` = 0) | **now, before ~11:54Z** | `round25/report.json` R25-A1, plan_issues 1, 2, 15 |
| **W249** (new; = **R25-A2**) | **PRE-SCORE 2/2, "W4 AMEND 4".** It supersedes the AMEND 3 (a)-(e) slot lists, the LIFT SPLIT file kinds and the 09:07Z arms slot rule. The night list is keyed on probe 50 alone. **R+:** 00:05 exp86c / 00:06 exp75 (or exp87a) / 00:45 exp89e. **R0/R-/R?:** 00:05 exp88c / 00:06 exp89a / 00:45 exp88b (exp83c on a Q3 yes). **Morning:** M1 is a CI file (exp89h under R+; exp89b/exp89o under R0); M2 is non-CI by 11:30Z. Non-CI files at least 40 min apart (R18-A7); arm code '+' = parent + 0.001; the depth cap kills exp89c/g/i/l | not started (`grep "W4 AMEND 4"` = 0) | **now** (same window as W248) | `round25/report.json` R25-A2, plan_issues 3-7 |
| **W250** (new; = **R25-A3**) | **(a) exp88c gate line**, marked "logged after the kernel completed, before its output was downloaded": nodes +0.4..+1.3% vs 121,252, forks 81 +-5, rule v2. **(b) exp86c WAIVER line:** it fails the literal R24-A4 items (safe 36/7/5/18, forks >= 85) and passes the RA-style gate; the line must say the per-clip readmit check was not applied | not started (`grep WAIVER` = 0; the last exp88c line is l.3668, "pushed 10:07Z") | (a) **now, before the output is downloaded**; (b) before 23:30Z and before any R+ use of exp86c | `round25/report.json` R25-A3; `round25/report.notes.md` 10:46Z-10:47Z |
| **W251** (new; = **R25-A4**) | **exp75 line.** The ipynb ab621c13 equals the Kaggle source; submit the existing v1 and never rebuild or re-push it; dummy CSV d6d9d808303f. It carries the GRANDFATHER clause for the 2,288 s runtime and lifts exp75 from the R21-A3 (e) NO-GO list (`CONTEXT.md` l.3335) | not started (`grep "exp75 re-verified"` = 0) | before the exp75 submit: ~12:00-13:00Z under R0/R-/R?, else 00:06Z | `round25/report.json` R25-A4, new_facts 7 |
| **W253** (new; = **R25-A6**, adjusted) | **ONE Russian message** (MSK first, UTC in brackets): (a) today's slot is exp87a or exp75; (b) the night list is keyed on 50; (c) Q2 is **already answered yes** (10:47Z, l.3704), so only propose the tighter CI cutoff (W260); (d) Q3 is still open; (e) **new question, tick fallback:** if the ticks are unchanged at 00:00 MSK 30 Sep (21:00Z), may the session tick the pair from the 18:00Z proposal?; (f) every file is a public-only, single-embryo read. Log the answers | not started (`grep "tick fallback"` = 0) | now, or with the probe-50 read | `round25/report.json` R25-A6 (covered_by_existing_approval **false**), plan_issues 11 |
| **W260** (new; contradiction) | **Morning CI cutoff.** CONTEXT says CI files by **09:30Z** (12:30 MSK) (l.3685-3686, l.3705-3706). Round 25 says **08:45Z** (11:45 MSK), because the logged CI band reaches 10.9 h: 09:30Z + 10.9 h = 20:24Z, after the 20:00Z tick | open: round 25 did not see the 10:47Z entry | log with W249, before the 29 Sep 07:23Z morning-batch cron | `round25/report.json` plan_issues 5, R25-A2 M1; `round25/scan_hyp_sched29.notes.md` (latency line) |
| **W258** (new; W247 residue) | **Wake-ups missing from the 10:52Z cron.** R25-A1 needs wake-ups at 11:50Z, 12:20Z, 12:50Z and 13:00Z; before 13:00Z the cron has only the 12:47Z research round. Also not re-created: the 28 Sep 17:57Z tick check (012fa6dd), a post-tick SELECTED check on 29 Sep (~20:00-20:30Z) and the 29 Sep ~23:27Z final LB snapshot (bb224de9) | not started | **before 11:50Z** | `CONTEXT.md` l.3709-3716 (cron list), l.2365, l.2619; `round25/report.json` R25-A1 (1) |
| W238 (residue) | Gate lines are done (l.3522-3529). Still missing: `tools/gate_dummy.py` (gate85.py lives only in the scratchpad) | in progress | before the first exp89 gate | `round24/report.json` R24-A4; `ls tools` 10:55Z |
| **W255 (b)** (new; = **R25-A8 (b)**) | Copy `uptest.py` from the session scratchpad to `tools/uptest.py`; keep the S0/S1 zips in `experiments/lb_poll/_lb/` | not started (`ls tools \| grep uptest` = none) | before probe 50's read (the '0u' code needs it) | `round25/report.json` R25-A8 (b); `round25/v_hyp_sched29_r25s-7.notes.md` |
| W126 (part 2) | RESULTS.md rows for probes 47 (0.955), 48 (0.957) and 49 (0.955); later 50 and 51 | overdue for 47-49 (the last RESULTS change is 59e14e2; l.78-79 end at probe 46) | before the finals card (29 Sep 12:00Z) | `experiments/RESULTS.md` l.78-79; `CONTEXT.md` l.3530, l.3615, l.3639 |
| W246 / **W257** (new) | **REPORT.md for rounds 24 and 25 was never rendered.** Subagents are blocked from writing it; round 25's Russian text is in the `report_md_ru` field of `report.json`. The round 25 folder is untracked. Commit named paths only, as the user, with no Co-Authored-By; never `git add -A` | round 24 folder committed (031e152) without REPORT.md; round 25 not started | with the W248/W249 commit | `round25/report.json` next_focus NOTE; `git status` 10:55Z; `ls research/wf_ideas_v4/round2*/REPORT.md` (rounds 20-23 only) |
| W202 + W244 | Info/curator lines: R22-A9 (a)-(h); R24-A10 (a)-(f) (I-412: JT's stage is his own code; the synthetic set is José Freitas's kernel output; radius 2x2 is post-deadline; the amanatar gap is the stitch class; mc23 parent-partner; builder weight-path hardening) | not started (`grep "R22-A9 INFO"` = 0, `grep I-412` = 0) | today | `round23/report.json` R23-A8; `round24/report.json` R24-A10 |
| W176 / W177 / W182 | ROUND 14-25 RECORD; LESSONS H1; no `NEVER_SUBMIT.md` in exp70j/exp70k | overdue, low | H1 now; H2 29 Sep 23:00Z | `_curation/24/watch.json` |
| I208 / W57 / W66 / W31 / W72 / W150 | Old low-priority text fixes | overdue, low | passed | `_curation/20/watch.json` |

## NEXT 24 H (28 Sep 10:58Z -> 29 Sep 10:58Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W248-W251, W253, W258 | **now, before ~11:54Z** | Pre-score lines, exp88c gate, exp75 line, user message, wake-ups (see above) | not started | R25-A1..A4, A6 |
| **T145** (new) | **~11:54-12:50Z** | **Read probe 50** (exp85a). R+ = display >= 0.957 (l.3650-3651); '0u' = 0.957 with an attributable UP (info only). S0 = a fresh LB download within ~10 min of the terminal header; S1 = the first download with count 53. k = 0 or a +2 move = BLIND/MASKED '?' | pending | `round25/report.json` R25-A1 (2)(3); `CONTEXT.md` l.3649-3658 |
| **T146** (new) | **at 50's terminal header, hard latest 13:00Z** (was 14:00Z) | **Probe 51 submit:** exp87a under R+, exp75 otherwise. Pre-submit checks: header < 15 min old and not a 429; pause the feed and watch loops ~10 min before; no duplicate; "1 submission remaining"; R8 COVERAGE (exp75 in the 00:00Z line, exp87a l.3604); dataset pre-push/list check (W261). Then re-run `tools/runtime_ledger.py`; the family must read safetail_ci | pending | `round25/report.json` R25-A1 (1); `CONTEXT.md` l.3543-3544 |
| **T147** (new) | **12:47Z** | The round 26 cron fires inside the 50-read / 51-submit window; the submit must not wait for it. Round 26 checks: W248/W249 were pre-score with the header quoted; the exp88c gate came before its output; 50's code; 51's -m text and family; exp89 builds and the ledger test; GPU quota; the user's answers | scheduled | `CONTEXT.md` l.3711-3712; `round25/report.json` next_focus |
| **W252** (new; = **R25-A5**) | The ledger rule **before any exp89 dummy**; builds and push at 50's read; hard latest push **19:00Z**; morning dummies ~21:00-22:00Z | **(a) Ledger:** `(r"exp89[abcghilmno][a-z]*", "safetail_ci")` above `exp8\d`, plus test_round25_exp89_families; R8 COVERAGE for exp89a/b/h/o. **(b) Builds**, stop on any sha8 mismatch. R+: exp89e 61b59191 (morning: exp89h 39c0452f, exp89k 59e181b4, exp89j e5dc89f4, exp89f 2092cf43). R0/R-/R?: exp89a ddd97ed3 (morning: exp89b 4f2f4ee9, exp89o with a new sha). **(c)** Read the GPU quota first, else at most 3 dummies. **(d)** Log gates before outputs (exp89a topology = exp88a CSV 482dbda1d1a0, etc.). **Q2 is now yes (l.3704), so exp89b/o (R0) and exp89h (R+, after 51 reads '+' or '0u') are live** | not started (`tools/runtime_ledger.py` l.80-83 has no exp89 rule; no exp89 folders) | `round25/report.json` R25-A5, new_facts 8-9 |
| T100 | hourly at hh:22Z until 29 Sep 12:00Z; feed every 30 min until 29 Sep 23:59Z | E10 v3 watch; the trigger is now **>= 0.958** (l.3645-3646). Watch for a JT reply to Justin CH123 on 743929 -> a one-knob arm on the current best (R25-A8 (e)) | live (RUN 22 10:24Z, feed 10:36Z) | `experiments/e10_watch/watch_loop.log`; `experiments/discussions/feed_loop.log` |
| **W255** (a)(c)(d)(e) (new; = **R25-A8**) | (a) before round 26 (12:47Z); (c)(d) today; (e) standing | **(a)** Refresh the round-prompt KEY FACTS: best 0.957 exp79a; 47/49 read 0.955; 50 pending; E10 >= 0.958; the 3+2 yes; tick 20:00Z; Q3 open. **(c)** Info line: the 0822Z P2 look-signal (5 teams moved to 0.956); the crowd-source hypothesis is refuted, so do not cite it in 50's read. **(d)** Curator items. **(e)** After any read >= 0.958, restart the feed and watch loops with the new --our-best; the watch loop running since 06:22Z still holds its old LOOK text | not started | `round25/report.json` R25-A8 |
| **W256** (new; = **R25-A9**) | build any time today; use decided at 23:30Z | Spare exp90a (exp79a + MAX_UM 2.0). Dummy only if a lane is idle and >= 2 GPU-h remain. It fills only an otherwise empty slot. Pre-registered read: >= 0.958 = candidate; 0.957 = no action; <= 0.956 closes the CI knob line | not started | `round25/report.json` R25-A9 |
| **T148** (new) | **~21:45-22:30Z** (the CI band tail reaches ~23:54Z) | **Read probe 51:** exp87a against REF, or exp75 by R25-A1 (5). It must never block the 23:30Z freeze; the night list is keyed on 50 alone | pending | `round25/report.json` R25-A1 (4)(5), plan_issues 4 |
| **T149** (new) | **~21:00-22:00Z** | Push the morning-file dummies (queue risk: CI dummies queued 3-4 h on 27 Sep). Under R+: exp89f at ~22:00Z; exp89h only after 51 reads '+' or '0u' | pending | `round25/report.json` R25-A5 (c) |
| T135 | 28 Sep: 12:47, 15:17, 17:47, 20:17Z; 29 Sep: 22:47 (28th), 01:17, 03:47, 06:17, 08:47, 11:17, 13:47, 16:17Z | Research rounds (session cron; session-only) | scheduled | `CONTEXT.md` l.3711-3713 |
| T19 / W77 | 17:57Z | Tick check: API SELECTED is still #37 + #38. Timer 012fa6dd is dead and the check is not in the 10:52Z cron | at risk (W258) | `CONTEXT.md` l.2365 |
| T143 | **23:30Z** (cron 23:33Z) | **W4 freeze.** Log R, the frozen list with slot times, each file's dummy status (all PASS by 23:30Z), the exp75 grandfather line under R+ (W251) and the spare exp90a decision | pending | `round25/report.json` R25-A2 FREEZE; `CONTEXT.md` l.3713 |
| T126 | 29 Sep 00:00Z | Slot reset (5 new slots) | - | `CONTEXT.md` l.3367 |
| T20 / T107 | **29 Sep: 00:04Z cron; slots 00:05, 00:06, 00:45Z** (spare 01:25Z) | **Night batch (3 files)** per W249 (AMEND 4). Non-CI files >= 40 min apart. Two night arms that complete in one poll window are MASKED | pending | `CONTEXT.md` l.3713; `round25/report.json` R25-A2; I297 |
| **T150** (new) | 29 Sep **~07:05-08:15Z** (non-CI night reads); **~09:25-09:35Z** (the 00:06Z CI file) | Night reads; arm code '+' = parent + 0.001 | pending | `round25/scan_hyp_sched29.notes.md` (latency line) |
| **T151** (new) | 29 Sep **07:23Z** cron. M1 CI by **08:45Z** (round 25) or **09:30Z** (CONTEXT); see W260. M2 non-CI by **11:30Z** (14:30 MSK) | **Morning batch (2 files).** Only PASSED dummies go. After 02:00Z, E10 copies need the user's yes per notebook (l.3612-3614) | pending | `CONTEXT.md` l.3704-3708, l.3713; `round25/report.json` R25-A2 MORNING |
| W19 / W73 / W102 / W93 / W165b | standing | ONE poller; header < 15 min old; never resubmit class C or ERRORed files; SEC files stay probes while Q3 is open (l.3610-3611) | standing | `CONTEXT.md` l.3331-3335, l.3480-3484 |
| **W261** (new; standing) | before every push | **Dataset pre-push rule.** `kaggle datasets list --mine` must show biohub-ft-weights lastUpdated 2026-09-23 23:54:03 and biohub-secft-n2a-v1 lastUpdated 2026-09-27 21:25:35; a change -> stop, diff the file list, tell the user. Never authenticate as a teammate; the user runs teammate pushes/submits with a separate KAGGLE_CONFIG_DIR | standing | `CONTEXT.md` l.3692-3703 |

## LATER (29 Sep ~11:00Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| **W254** (new; = **R25-A7**; supersedes W234, W230 and the T120 content) | draft today; **send 29 Sep 12:00Z (15:00 MSK)** (cron 12:03Z); re-check 18:00Z and ~19:00Z | **FINALS CARD v3** as a neutral table. Pairs: A {V_pub, #37}; B {V_pub, exp75}, only if exp75 is COMPLETE at >= 0.955; C {V_pub, exp70g}; ticked {#37, #38} last. Contents: mc25 ranges; the deciding beliefs (CI transfer; cap 6 public vs lab); the exact JT quote; the RC-C CI caveat; a risk column; branches (exp75 pending, V_pub = E10, tick fallback); times as MSK (UTC). Delete "if JT, then exp75" and "partner still exp75" | `round25/report.json` R25-A7; `CONTEXT.md` l.3713-3714 |
| T60 | 12:00Z | Q3 is still open -> SEC files are excluded from the card | `CONTEXT.md` l.3610-3611 |
| T152 (new) | **18:37Z** cron | FINAL proposal. Without a tick-fallback yes, warn that the ticks are still #37/#38 | `CONTEXT.md` l.3714; `round25/report.json` R25-A7 (7) |
| T115 / T48 | **~19:00-19:30Z** | FINALS READ. Every file that may become a final must have read by ~19:30Z; never a non-COMPLETE file | `CONTEXT.md` l.3685-3687 |
| T10 | **20:00Z (23:00 MSK)** | **The user ticks the finals.** 20:00 UTC is our hard limit; Kaggle allows re-ticks until 23:59Z | `CONTEXT.md` l.3683-3685 |
| **T153** (new) | ~20:00-20:30Z | Verify that API SELECTED = the user's pair. There is no cron for this (W258) | `CONTEXT.md` l.3474 (SELECTED check pattern) |
| **T154** (new) | 21:00Z (00:00 MSK 30 Sep) | Tick-fallback moment, only if the user said yes (W253 (e)) | `round25/report.json` R25-A6 (e) |
| W177 H2 | 23:00Z | LESSONS H2 | `_curation/20/watch.json` |
| T49 | 23:00-23:45Z | Final public LB snapshot. Timer bb224de9 is dead and the snapshot is not in the cron (W258) | `CONTEXT.md` l.2619 |
| T11 | **29 Sep 23:59Z** | Deadline; a submit must **finish** before it | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 |
| T155 (new) | 30 Sep 00:07Z cron | POST-DEADLINE job: private read v2 + L1-L7 (T30/T50) | `CONTEXT.md` l.3714-3715, l.2570-2598 |
| T133 | after the deadline | GPU weekly reset (per the user, only after the deadline) | `CONTEXT.md` l.3689-3690 |
| W29 / curator | after 29 Sep | Post-deadline list, plus: z-shift +0.1 after CI (J -0.00085); the MAX_UM 2.0 float-path note | `round25/report.json` R25-A8 (d); `_curation/24/watch.json` |

**Passed or finished time-bound items:**
- The R8 new-mechanism cutoff (27 Sep 12:00Z) has passed, and the user lifted R8/no-retrain for the rounds (`CONTEXT.md` l.3459-3460).
- The 28 Sep 12:00Z consolidation is superseded (T46; l.3392-3394). The curation task template still names both as examples.
- W2a is gone: exp85a went as probe 50 at 05:02Z (l.3465).
- Friend replies: none awaited (the last friend instruction is from 26 Sep, l.2175-2176).
- Teammates gsfatakhov and sasyami are a GPU reserve only; nothing is awaited from them (l.3688-3698).
- **T156** (new): the tick deadline is 20:00 UTC = 23:00 MSK. Never tell the user "20:00" without "UTC" (l.3683-3687).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I287** (new) | "The CI_lo 2.2 h model is contradicted: the measured dL is 1.60-2.18 h" | `round25/report.json` R25-A1 (6), new_facts 10; the model is at `CONTEXT.md` l.3135 | The old model is still in CONTEXT. A CI read with L_hi in 9.6-10.2 h needs the 'ins-tail?' footnote (W248). |
| **I288** (new) | "Morning CI 09:30Z -> 18:46-18:57Z at 9.27-9.45 h (20:24Z at 10.9 h)" | `round25/scan_hyp_sched29.notes.md` | A CI file sent at CONTEXT's 09:30Z cutoff can read after the 20:00Z tick (W260). |
| **I289** (new) | "If the user does nothing, the ticks stay #37 (0.954) + #38 (0.953), below exp79a and exp70g" | `round25/report.json` plan_issues 11 | No fallback is authorised; W253 (e) asks for one. |
| **I290** (new) | "exp75 = exp79a node positions + #37 edges, deterministic"; "Its read is not an independent CI read" | `round25/scan_hyp_private.notes.md` 10:25Z; `round25/report.json` R25-A1 (5) | exp75's display must not count as a second CI confirmation on the finals card. |
| **I291** (new) | The scan says "exp75 rebuild ab621c13 vs repo 4653611e"; the judge found that "the repo holds ab621c13" and ruled "never rebuild/re-push exp75" | `round25/scan_hyp_sched29.notes.md`; `round25/report.notes.md` 10:44Z | A rebuild would change the bytes and void the 27 Sep dummy. Submit Kaggle v1 as is (W251). |
| **I292** (new) | "uptest.py (session scratchpad ..., NOT in repo)" | `round25/v_hyp_sched29_r25s-7.notes.md` | Same failure class as gate85.py (I275): the '0u' code needs it at night even if the session dies (W255 (b)). |
| **I293** (new) | "exp88c ... = COMPLETE (read-only) -> its gate line must be logged BEFORE its output is downloaded/read" | `round25/report.notes.md` 10:46Z | The pre-registration of a night R0 file is at risk (W250 (a)). |
| **I294** (new) | "CI lab per clip a0.5 3um: -0.0209/+0.0125/0/+0.0083 (44b6_c50204e0 negative)"; "the refiner is ALSO z-biased"; "part of the 6bba gain is a learned offset" | `round25/scan_plancheck.notes.md`; `round25/scan_recheck.notes.md`; `round25/report.json` new_facts 11 | CI now drives V_pub, so the finals card caveat must carry this (W254 (5)). |
| **I295** (new) | GPU "~5 h left" (user, 10:45Z) vs "~4.5-4.8 h left" (estimate); "Chrome disconnected at 06:35Z; API has no quota" | `CONTEXT.md` l.3689; `round25/v_plancheck_pc25-04.notes.md` | Unless the Settings page is read, cap at 3 dummies before 23:30Z (W252 (c)). |
| **I296** (new) | "0822Z (P2 largest group 5 at 0.956 ...) = P2 look-signal (not seen in CONTEXT)"; the crowd-source hypothesis was REFUTED | `round25/scan_browser.notes.md`; `round25/report.json` rejected | It must not be cited when reading probe 50 (W255 (c)). |
| **I297** (new) | "night arms 00:05/00:25Z share the 7.0-7.8 h latency band -> can complete in one snapshot window -> MASKED" | `round25/v_hyp_sched29_r25s-7.notes.md` | Night UP tests may be unreadable, so arm codes must rest on displays (R25-A2 ARM CODES). |
| **I298** (new) | "exp88b fork total 86 = the same as exp78a (cap 8), which read 0.955 '-'"; "a tie is the most likely outcome" | `round25/v_plancheck_pc25-04.notes.md` | The prior for TAU 0.7 is a tie or '-'; do not overrate the 00:45Z R0 arm. |
| **I299** (new) | exp88a "raw nodes 44b6_0b24845f 19,383 vs 20,206 (-4%) ... Effect concentrated in one public clip (noisy read)" | `round25/v_plancheck_pc25-04.notes.md` | exp89a (exp79a + DIS 2.25) inherits a one-clip effect, so its read is noisy. |
| **I300** (new) | `run_feed_loop.sh` calls `tools/kaggle_feed.py` without `--our-best` (default 0.957, l.172); the watch-loop process started at 06:22Z holds the old LOOK text | `experiments/lb_poll/run_feed_loop.sh` l.10; `round25/report.json` R25-A8 (e) | After a >= 0.958 read, bump the default or restart the loops, or E10 flags stale copies. |
| **I301** (new) | "an accidental new version of biohub-ft-weights would be picked up silently by new pushes (the DaughterNet glob has no sha pin)"; the teammates briefly had EDIT rights | `CONTEXT.md` l.3697-3703 | Run the W261 pre-push check before every push. |
| **I302** (new) | "A file is submitted from the account that ran its kernel version; the team keeps 5 submits/day in total" | `CONTEXT.md` l.3692-3693 | Kernels run by teammates use the same 5 daily slots. |
| I274 | The SI gate fails if BASE becomes a K file | `round24/scan_plancheck.notes.md` 06:47Z | Live again under R+ (arms re-cut off exp85a/exp86c, l.3637-3638); W243 (1) is still open. |
| I275 | gate85.py lives only in the scratchpad and does not check node rows | `round24/scan_plancheck.notes.md` | W238 residue. |
| I278 | The synthetic set is José Freitas's kernel output, not hengck23's | `round24/report.json` R24-A10 (b) | CONTEXT l.3509-3510 still says hengck23 (W244 (b)). |
| I280 | Feed loop 429 at 06:34Z on a second run within 2 min | `round24/scan_plancheck.notes.md` | Pause the loops before the probe-51 submit (T146). |
| I265 | "readmitted nodes are 3.5-6x depleted near GT" | `round23/report.json` new_facts | Probe 50 raises readmits; only the LB read can sign READMIT. |
| I284 | "No public notebook has best_public_score > 0.953"; JT's stage is his own code | `round24/report.json`; `digest_20260928T1036Z.md` | Still true at 10:36Z, so E10 at >= 0.958 is unlikely to fire (W244 (a)). |
| I72 / I116 / I145 | No Co-Authored-By; timers die with the session; a submit must finish before the deadline | `memory/feedback-git-no-coauthor.md`; `CONTEXT.md` l.3715-3716 | The 10:52Z cron is session-only again. The last 12 commit bodies comply with I72. |
| Older I-rows | Unchanged | `_curation/24/watch.json`, `_curation/23/watch.json` | - |

**Resolved since 07:25Z (curation 24):**
- I276 (the ledger misfiled exp87): the rule is in (`tools/runtime_ledger.py` l.81; `CONTEXT.md` l.3603-3604). The same problem recurs for exp89 as W252 (a).
- I277 (ILP 0.4 is not inert): logged (l.3579-3582).
- I279 (gap rule): logged (l.3587-3589).
- I283 (runtime rule v2): logged (l.3584-3587).
- I281 / W247 (dead timers): the cron was re-created (l.3709-3716); the residue is W258.
- I282 (exp86c had no output): PASS logged (l.3526-3528); waiver in W250 (b).
- I285 (anvithpothula at 0.957): moot; our best is now 0.957 and the trigger is 0.958.
- I286 (ask the user now): asked and answered (l.3607-3614, l.3680-3687, l.3704-3708).
- I267 / I268 / I273: superseded by the neutral card v3 (W254).
