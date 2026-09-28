# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-28 ~07:30 UTC (curation 24). This updates the curation-23 build of 28 Sep 04:45Z (full text in git history of this file; predecessors `research/KNOWLEDGE/_curation/23/watch.json`, `_curation/22/watch.json`, `_curation/21/watch.json`, `_curation/20/watch.json`, `_curation/18/watch.json`). Rows not repeated here are unchanged there.

**Sources read for this update:**
- `CONTEXT.md` (3,542 lines; `## 9. Literature` starts at l.3522). New entries since curation 23:
  - 04:38Z DISCUSSION 743929 + exp85a/b/c builds + W2 AMENDMENT (l.3433-3441);
  - 04:39Z PROCESS MISS + FIX (l.3442-3447);
  - 04:53Z CURATION 23 ACTED ON + exp85a PRE-SUBMIT LINE (l.3448-3464);
  - 05:03Z PROBE 50 SUBMITTED (exp85a 56629533) + GPU QUOTA READ (l.3465-3478);
  - 06:26Z exp85b/c DUMMY GATES + OPS RESTART + SEC siblings (l.3479-3494);
  - 06:35Z kaggle_feed tool + first discussions read (l.3495-3514);
  - 06:37Z BRANCH CANDIDATES exp86a/b/c (l.3515-3521).
- `git log`: 08ceca1, d14e9a3, d015291, 59e14e2, 048c518, a240ba1, ebadfa3, af035e7 (last, 09:38 local = 06:38Z). Git dates are local time (UTC+3). `git log -8 --format=%b | grep -ci co-author` = 0.
- `git status` 07:22Z: untracked `research/wf_ideas_v4/round24/` (no REPORT.md), `experiments/e10_watch/20260928T0639Z.txt`, `experiments/discussions/digest_20260928T0704Z.md`, eleven `experiments/ext_*` folders, `ds_secw_corwin_v1/weights/`, `ext_corwin-biocel-aux/_booster/`.
- `research/wf_ideas_v4/round24/report.json` (complete, written 07:18Z, actions **R24-A1..A11**), `round24/report.notes.md`, `scan_plancheck.notes.md`, `scan_hyp_slots.notes.md`, `scan_recheck.notes.md`.
- `experiments/lb_poll/poll.log` header **07:22:46Z** (l.20699): 47/48/49/50 all PENDING; `experiments/lb_poll/ledger.md` (07:12:46Z).
- `experiments/e10_watch/watch_loop.log` (RUN 18 06:23:45Z, 0 signals, next 07:22:29Z); `experiments/discussions/feed_loop.log` (07:05:10Z, E10 FLAG none).
- `experiments/lb_poll/e10_watch_loop.py` l.78; `experiments/RESULTS.md` l.78-79; scratchpad listing (`gate85.py`).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot, awaiting user.

**State at 07:25Z, 28 Sep:**
- **Best display 0.956** = exp70g (probe 45, 56606948), L (7.49, 7.67] h (`experiments/lb_poll/ledger.md`).
- **Rank:** #179 (was #172), 9th of 56 in the 0.956 block, k = 8, 170 teams strictly above (`round24/report.json` new_facts; `experiments/e10_watch/20260928T0639Z.txt`).
- **Four probes PENDING at 07:22:46Z** (`poll.log` l.20699): 47 exp78b 56623073, 48 exp79a CI 56623105, 49 exp78a 56624341, **50 exp85a 56629533** (exp70g + ILP_DIVISION_WEIGHT 0.4 + READMIT_MIN_SCORE 0.94, submitted 05:02:30Z; `CONTEXT.md` l.3465-3474). Expected reads: 47 ~07:30-08:00Z, 49 ~08:15-08:40Z, 48 ~09:40-10:55Z, 50 ~12:27-12:51Z (`round24/report.json` new_facts).
- **28 Sep slots:** 4 used (47, 48, 49 at 00:06-00:50Z; 50 at 05:02Z); **1 left**, for W2b (`CONTEXT.md` l.3474-3478).
- **GPU quota read:** 20:29/30 h at 04:55Z (`CONTEXT.md` l.3476-3477); ~7.2 h left after ~2.2 h of dummies (`round24/report.json` new_facts).
- **Dummies:** exp85a/b/c PASS (l.3466-3469, l.3485-3488); exp86a/b outputs in `_dl/` but **gate not logged**; **exp86c has no output** (`round24/report.notes.md` 07:15Z).
- **Finals unchanged:** #37 56563521 + #38 56563534 ticked; the user picks on 29 Sep (`CONTEXT.md` l.3398-3400, l.3474).
- **Ops:** the previous session died ~05:07Z; poller and E10 loop restarted 06:22Z as detached processes (`CONTEXT.md` l.3480-3485). Session-only timers were not re-created (see W247).

**Changes since 04:45Z (curation 23):**
- **Done:**
  - W228 (R23-A11): round key facts refreshed (`CONTEXT.md` l.3459-3460).
  - W232 (R23-A4): runbook section 9 builds the SI from the BASE's probe.json, REF = BASE (l.3456-3458). New residue: W243.
  - W212 (R23-A5): GPU quota read, 20:29/30 h (l.3476-3477).
  - W229 (R23-A7): nine stack notebooks logged and committed (l.3460-3463; commit d015291).
  - W126 part 1: RESULTS.md rows 39-46 (commit 59e14e2; `experiments/RESULTS.md` l.78-79 for 45/46).
  - W174: loop LOOK text now reads "> our best (0.956 on 28 Sep, so >= 0.957)" (`experiments/lb_poll/e10_watch_loop.py` l.78; loop restarted 06:22Z).
  - W231 (c): exp81/exp80a sibling CSVs downloaded, sha12 match (l.3493-3494).
  - W233 principle "dummies pushed by the current BASE only (R23-A6)" logged (l.3462-3463).
- **Superseded:** T117 W2a 08:45-10:00Z (exp85a took the slot at 05:02Z, l.3446-3447, l.3465); W199/W222 morning brief (R23-A9) -> the R24-A7 message (W241).
- **New:** actions **W235-W247**, reminders **T139-T144**, insights **I274-I286**.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| **W235** (new; = **R24-A1**) | **Pre-score block 1/3: W2b TIMING + K LEVER + W2b TABLE v5.** Quote the last PENDING header (07:22:46Z or newer). (T) CI file at 12:00Z; non-CI file at the first header with 56629533 terminal, latest 14:00Z. (K) K = ILP 0.4 + READMIT 0.94 as ONE bundled lever read by probe 50 (R+ / R0 / R- / R?); lookup JT(b), JT+CI(b), RA92(b). TABLE rows 0-4: E10 copy; D12 (S3) -> exp80a; D8 + C+ -> exp83b; wait for 50: R+ -> exp86c (D0) / exp86a (D8), else exp81; Row 4 fallback exp81, exp85b. If 47 is already terminal, write "(written after 47 was terminal)" | **overdue / imminent**: `grep "TABLE v5"` in CONTEXT = 0; last entry 06:37Z | **before probe 47 is terminal (~07:30Z)** | `round24/report.json` R24-A1, plan_issues (1)(2)(4)(13); `poll.log` l.20699 |
| **W236** (new; = **R24-A2**) | **Pre-score block 2/3: W4 AMEND 3 + (4) EXCEPTION.** Dummies PASS by **23:30Z** (supersedes 00:00Z); the 23:30Z freeze line (row, b, R, C, codes, frozen list); rows (a)-(e); stack depth <= cap + 2 levers; READMIT 0.92 only under R+, 0.90 only if RA92 reads strictly above JT(b); no RA98 | not started (`grep "W4 AMEND 3"` = 0) | **now (same block as W235)**; at the latest before 50 is terminal (~12:25Z) | `round24/report.json` R24-A2 |
| **W237** (new; = **R24-A3**) | **Pre-score block 3/3.** (1) Correction to 06:26Z: ILP 0.4 is not inert, +3 safe divisions (63 -> 66) via relink orphans; (2) amend 04:53Z: the lowrefine part is benign, no decoupling build; (3) runtime rule v2 (PASS <= 2,100 s; 2,100-2,500 s re-run; > 2,500 s FAIL); (4) GAP RULE: L_hi > 8.0 h only from a > 15 min poll gap = UNPROVEN, not 'v'; (5) **S0 = `e10_watch/20260928T0639Z.txt` (count 48, #179, k = 8)** | not started | now (same window as W235) | `round24/report.json` R24-A3; `CONTEXT.md` l.3489-3491 (the "near-inert" text) |
| **W238** (new; = **R24-A4**) | **exp86a/b gate lines + gate tool + exp86c.** Log exp86a/b PASS with "(written after the outputs were listed ...)"; copy scratchpad `gate85.py` to `tools/gate_dummy.py` with a node-row hash and a test; **confirm/push the exp86c dummy** and gate it vs exp85a (node rows differ, readmits and LOWREFINE up < +5%, failed frames 0) | not started: no `tools/gate_dummy.py`; exp86c has no `_dl` output (07:15Z) | exp86c push **now**; gate lines ~08:00Z; **exp86c PASS by 12:30Z** | `round24/report.json` R24-A4; `round24/report.notes.md` 07:15Z; `ls tools/gate_dummy.py` 07:22Z = missing |
| W230 (R23-A1 residue) | Balanced CI caveat (R22-A4 (A): a0.5 pooled +0.0022, sign flips with alpha, Eric lab +0.0078 -> LB -0.002 twice, V1284 probe 31 LB +0.002); replaces the Eric-only v2 (9) line (`CONTEXT.md` l.3187). Russian draft (iv) with R23-A10 fixes | not started (`grep "a0.5 pooled"` = 0) | **before 48's terminal header (~09:40Z)** | `round22/report.json` R22-A4 (A); `round23/report.json` R23-A1 |
| W231 (R23-A3 residue) | (c) done (l.3493-3494). Still missing: (a)(5) CSV must differ from the non-SEC sibling and exp81; (b) SEC+CI files show Secondary 7029fe69; (d) **exp84a gate** (R21-A3 (e) cap-rung rules + node rows identical to exp70g) | in progress | before any exp82*/83c-g/84a dummy is gated (T1 ~08:45Z for exp84a under S3) | `round23/report.json` R23-A3; `CONTEXT.md` l.3426-3428 |
| **W246** (new) | **Round 24 REPORT.md + commit.** `round24/REPORT.md` was blocked by the harness; the main session renders it from report.json (round-23 layout). Commit named paths only: round24 folder, `e10_watch/20260928T0639Z.txt` (the S0 file; snapshots stay tracked per R22-A11 amended), digests, as the user, no Co-Authored-By. Never `git add -A` (weights, `_booster/`) | not started | with the W235-W237 commit | `round24/report.json` next_focus NOTE; `round24/report.notes.md` 07:18Z; `git status` 07:22Z |
| **W247** (new) | **Re-create the session timers.** They die with the session (I116), and the session died ~05:07Z. The 06:22Z restart covered only the poller and the E10 loop. Lost timers: 012fa6dd (tick check 28 Sep 17:57Z), 328f7392 (29 Sep 11:57Z push), 18ff4796 (29 Sep 17:57Z), bb224de9 (29 Sep ~23:27Z LB snapshot) | not started (no CONTEXT line re-creates them) | **before 12:00Z today** (W2b wake-ups 12:15/12:30/13:30Z, R24-A8) | `CONTEXT.md` l.2532, l.2601-2602, l.3480-3485; `round18/report.json` R18-A2 (2) |
| W126 (part 2) | RESULTS.md rows for probes 47-50 after their reads (rows 39-46 done, 59e14e2) | not started (by design) | before the finals read (29 Sep ~19:00Z) | `experiments/RESULTS.md` l.78-79 |
| W202 + **W244** (= R23-A8 + **R24-A10**) | Info/curator lines: R22-A9 (a)-(h); READMIT/ILP rows; softened lab caveat (I265); plus R24-A10 (a) I-412 JT stage own code, stop manual 0.947-family scans; (b) synthetic set is José Freitas's kernel output; (c) I-183 radius closed, post-deadline 2x2 test; (d) amanatar gap continuation = stitch class; (e) mc23 parent-partner pairs lose 0.05-0.16 bronze; (f) builder weight-path hardening | not started (`grep "R22-A9 INFO"` = 0) | today | `round23/report.json` R23-A8; `round24/report.json` R24-A10 |
| W176 / W177 / W182 | ROUND 14-24 RECORD; LESSONS H1; no `NEVER_SUBMIT.md` in exp70j/exp70k | overdue, low | H1 now; H2 29 Sep 23:00Z | `ls experiments/exp70j_k2_dc020 experiments/exp70k_k2_dc0225` 07:22Z |
| I208 / W57 / W66 / W31 / W72 / W150 | Old low-priority text fixes (amanatar V6 misattribution l.2976-2977) | overdue, low | passed | `_curation/20/watch.json` |

## NEXT 24 H (28 Sep 07:25Z -> 29 Sep 07:25Z)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W235-W237 | **now, before 47 terminal (~07:30Z)** | The three pre-score blocks (see OVERDUE) | overdue | R24-A1..A3 |
| **T139** (new) | **~07:30-08:00Z** | **Read 47** (exp78b). S1 = manual `kaggle competitions leaderboard -d` within ~10 min of the terminal header; S0 = 0639Z snapshot (W237 (5)); log k; k = 0 -> BLIND '?' | - | `round24/report.json` R24-A3 (5), new_facts; `CONTEXT.md` l.3320-3331 |
| **W241** (new; = **R24-A7**) | **with the 47 read, or at 08:00Z** (whichever first); never re-send at 09:30Z | **ONE short Russian message**: (a) up to 2 non-CI files after 29 Sep 02:00Z until ~10:25Z? (b) Q3: may a SEC file be a final? (c) confirm E10 copies after 02:00Z; one line on K (50 reads ~12:30Z); one line that READMIT 0.92/0.90 are our own steps, only if 50 reads '+'. **Before sending**, append the "W4 LIFT SPLIT (R24)" pre-score line | not started; replaces W199/W222 (R23-A9) | `round24/report.json` R24-A7 (covered_by_existing_approval false: user answers needed) |
| **W239** (new; = **R24-A5**) | **before ~08:45Z** | **Build exp87a/b/c/d/e/i/j** (CPU, no push); expected sha8 87a 2e40c57f, 87b ec9c2860, 87c f29dc7d9, 87d 06f120c7, 87e 53eb54c7, 87i 4042f00f, 87j 97413dfc; STOP on mismatch; diff vs the listed refs; **no RA98**. Add `exp87[abce]` -> safetail_ci above `exp8\d` in `tools/runtime_ledger.py` with a test; extend R8 COVERAGE to exp87a/b/c/e; commit as the user | not started (`ls experiments | grep exp87` = none) | `round24/report.json` R24-A5, plan_issues (6) |
| T100 | hourly at hh:22Z until 29 Sep 12:00Z; feed loop every 30 min until 29 Sep 23:59Z | E10 v3 watch (RUN 18 06:23Z, 0 signals) + feed digests (07:05Z, E10 FLAG none). Watch: a new anvithpothula notebook (author now 0.957), a JT reply to Justin CH123 on 743929 (R24-A9 (3)). Trigger = public notebook strictly above our best display | live | `experiments/e10_watch/watch_loop.log`; `experiments/discussions/feed_loop.log`; `CONTEXT.md` l.3495-3514 |
| **T140** (new) | **~08:15-08:40Z** | **Read 49** (exp78a cap 8); D0/D8/D12 and S1-S7 (S7 now decides BASE only; W2a is gone) | - | `round24/report.json` new_facts; `CONTEXT.md` l.3425-3426 |
| **W240** (new; = **R24-A6**) | T1 ~08:45Z; T2 48 read; T3 ~12:30-13:00Z; T4 ~19:45Z; all PASS by 23:30Z | **Dummy push schedule**, realized branch only: T1 exp84a only under S3; T2 nothing JT-related, never a CI stack; T3 R+ and b != exp70g -> RA92(b) (exp87i/j), R+ and C+/testable C? -> JT+CI(b) (exp87a/b/c); T4 exp87d (+exp87e if C+) under S3-up and R+; T5 SEC(b) only after exp81 reads '+'; RA90(b) only if RA92 reads above JT(b) | not started (by design) | `round24/report.json` R24-A6 |
| W231 (d) | before T1 (~08:45Z) | exp84a gate line (see OVERDUE) | in progress | R23-A3 (d) |
| W230 | **before 48 terminal (~09:40Z)** | Balanced CI caveat (see OVERDUE) | not started | R23-A1 |
| **T141** (new) | **~09:40-10:55Z** | **Read 48** (CI): CI-RAN gate (dL >= 1.2 h, L_hi <= 10.2 h = C+), CI-? SCOPE, GAP RULE (W237 (4)) | - | `CONTEXT.md` l.3388-3391; `round24/report.json` R24-A1 row 2, R24-A3 (4) |
| T135 | **~09:30-10:30Z** round 25; ~12:00-13:30Z round 26; ~20:00-23:00Z round 27 | Round 25: verify W235-W237 were pre-score with the header quoted; 47/49 codes; T1 push; exp87 shas + ledger test; exp86c gate; user answers. Round 26: 48 code, W2b, T3 pushes. Round 27: W2b read, exp80a/exp81 codes, 23:30Z freeze + filler | - | `round24/report.json` next_focus |
| **W242** (new; = **R24-A8**) | **12:00Z (CI file)**, or the first header with 50 terminal (**~12:27-12:51Z, latest 14:00Z**) for a non-CI file | **W2b by TABLE v5.** Pre-submit: dummy PASS logged; header < 10 min, no 429 (**pause the feed loop ~10 min before**); no duplicate; R8 COVERAGE for CI/SEC; "1 submission remaining today"; -m names the table row. OPS: a live session or wake-ups at ~12:15Z, 12:30Z, 13:30Z; check the detached loops at 08:05Z and 12:15Z. If no session is live at 14:00Z, the choice goes as W3 by 23:30Z | not started | `round24/report.json` R24-A8; `CONTEXT.md` l.3480-3485 (session died 05:07Z) |
| W238 | **exp86c PASS by 12:30Z** | exp86c is the only D0/R+ W2b file | not started | R24-A4 |
| T106 | 12:00Z | ~~W2b by TABLE v4~~ -> TABLE v5 (W235/W242) | superseded when W235 lands | `CONTEXT.md` l.3351; R24-A1 |
| **T142** (new) | **~12:27-12:51Z** (13:0xZ if 'v') | **Read 50** (exp85a): R+ = display >= 0.957 or an attributable sub-rounding UP; 0.956 = R0; <= 0.955 = R-. A 0.957 from a two-change file is a public-only read on the finals card (winner's curse) | - | `CONTEXT.md` l.3453-3455; `round24/report.json` R24-A1 (K) |
| W243 (new; = **R24-A9**) | (1) before any E10 trigger; (2) at the first 0.957+ read of ours | (1) Runbook + E10 v3 line: SI = copy + the DIVINS keys of the **cap-family** BASE only; ILP/READMIT never enter an SI. (2) After a 0.957+ read: restart the feed loop with `--our-best` and update the loop LOOK threshold (both hardcoded 0.956: `tools/kaggle_feed.py` l.172, `e10_watch_loop.py` l.78); apply the strict trigger by hand until then | not started | `round24/report.json` R24-A9; `round24/scan_plancheck.notes.md` 06:47Z (SI FAIL with --si-ref exp85a) |
| W234 | draft fixes can start now; send by 29 Sep 11:57Z | Finals draft_ru defects (R23-A10) | not started (`CONTEXT.md` l.3464 "Still open") | `round23/report.json` R23-A10 |
| T123 | ~16:15-17:45Z | The exp80a read if exp80a was submitted (now only via TABLE v5 Row 1 under S3) | - | `round24/report.json` R24-A1 row 1 |
| T19 / W77 | 17:57Z | Tick check (timer 012fa6dd probably dead, W247): API SELECTED + a page read | at risk | `CONTEXT.md` l.2601-2602 |
| **W245** (new; = **R24-A11**) | build by ~21:00Z; dummy ~22:00Z only if needed; decide at 23:30Z | **Filler exp87m** = b + SAFE_DIV_MAX_UM 10.5 / SISTER 15.0 / DIVERGE 1.50 (amanatar V6). Only if the frozen W4 list has < 4 planned files; last free K2 slot <= 01:25Z; pre-registered "EV ~0" | not started | `round24/report.json` R24-A11 |
| T132 | ~21:00Z | Last sensible dummy push for any W4 stack | - | `round22/report.json` R22-A6 |
| T118 | ~23:00Z | Latest useful user answer on the cap lift (W241 (a)) | awaiting user | R24-A7 |
| **T143** (new) | **23:30Z** | **W4 freeze**: every W4 file has a PASSED dummy; log the evaluated row, b, R, C, codes of exp80a/exp81/exp86c, the frozen list with slot times, before any 29 Sep submit. W3 (if W2b moved) submits <= 23:30Z | - | `round24/report.json` R24-A2; `CONTEXT.md` l.3354-3356 |
| T126 | 29 Sep 00:00Z | Slot reset (5 new slots) | - | `CONTEXT.md` l.3367 |
| T20 / T107 | **29 Sep 00:05-01:45Z** | **W4** by AMEND 3 rows (a)-(e): <= 4 planned + 1 held for E10; K2-like 00:05/00:45/01:25Z, CI 00:06Z; no CI file after 02:00Z; no DIV-only file after 01:45Z (S6) | - | `round24/report.json` R24-A2; `CONTEXT.md` l.3366-3373 |
| T127 | 29 Sep 02:00-~10:25Z | Only with the user's yes (W241 (a)): <= 2 non-CI files; E10 copies need W241 (c) | awaiting user | `CONTEXT.md` l.3374-3377; R24-A7 |
| W19 / W73 / W102 / W93 / W165b | standing | ONE poller, header < 15 min (now detached, 07:22:46Z); never resubmit class C / ERRORed / exp79a; SEC datasets untouched; Q3 open, SEC excluded from V_pub | standing | `CONTEXT.md` l.3331-3335, l.3419-3420, l.3480-3484 |

## LATER (29 Sep 07:25Z -> 23:59Z, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T119 | ~07:40-09:30Z | W4 reads land | `round22/report.json` R22-A8 (1) |
| T09 / W77 / **W247** | 11:57Z / 17:57Z | Tick checks + user reminder; **the timers 328f7392 / 18ff4796 died with the 05:07Z session end** unless re-created | `CONTEXT.md` l.2601-2602, l.3480-3485 |
| W234 | by 11:57Z | Finals draft_ru fixes (1)-(7) incl. the corrected #38 bullet (I267) and the full 5 tick steps in the push | `round23/report.json` R23-A10 |
| T120 | **12:00Z** (refresh 18:00Z only on a change) | **Finals proposal**: {V_pub, #37} vs ticked {#37, #38}, card ranges, W230 CI caveat; a knob file's display is public-only, single embryo (R24-A2). The user ticks | `CONTEXT.md` l.3417-3422; R24-A2 |
| T60 | 12:00Z | G2 must have landed for a SEC file to be finals-eligible | `CONTEXT.md` l.2736 |
| T121 | 17-18Z | Log N954 (for sizing ranges only) | R20-A9 (f) |
| T115 / T48 | **~19:00Z** | FINALS READ + L9; Q3 deadline; never a non-COMPLETE file; insertion gate "did NOT fire" | `CONTEXT.md` l.3194, l.2510-2518, l.3421 |
| T10 | **20:00Z** | Our buffer for the ticks; re-ticks allowed until 23:59Z | R20-A3 (a) |
| W177 H2 | 23:00Z | LESSONS H2 | `_curation/20/watch.json` |
| W178 / W215 | before 23:00Z; hourly 30 Sep | Private-read addenda (priors C/C8/C_thr) | R20-A13; `CONTEXT.md` l.3056, l.3195 |
| T49 | 23:00-23:45Z | Final public LB snapshot (timer bb224de9 probably dead, W247) | `CONTEXT.md` l.2532 |
| T11 | **29 Sep 23:59Z** | Deadline; a submit must **finish** before it | https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743765 |
| T30 / T50 | 30 Sep from 00:15Z | Private read v2 + L1-L7 | `CONTEXT.md` l.2570-2598 |
| T136 | 2 Oct | Weekly agent limit reset (moot while the 04:32Z user reset holds) | `CONTEXT.md` l.3428-3432 |
| T133 | 3 Oct | GPU quota reset: after the deadline | `round22/report.json` R22-A5 |
| W29 / curator | after 29 Sep | Post-deadline list: N1 k 1.5; DaughterNet v2 at high cap; synthetic pretraining (SYN-DN rejected for now, R24SY-3); theft-aware ranker; MITO3 after an adapter; READMIT 0.94 lab test with lowrefine decoupled (I264); **new: RADIUS {4,5} x READMIT {0.965, 0.94} 2x2 test (R24-A10 (c))** | R20-A6; R23-A8; `round24/report.json` R24-A10, rejected |

**Passed or finished time-bound items:**
- R8 new-mechanism cutoff 27 Sep 12:00Z has passed, and the user lifted R8/no-retrain for the rounds (`CONTEXT.md` l.3459-3460). The curation task template still names it (and "consolidation 28 Sep 12:00") as examples; the research-round template was fixed (W228 done).
- The 28 Sep 12:00Z consolidation is superseded (T46; `CONTEXT.md` l.3392-3394).
- W2a (08:45-10:00Z) is superseded: exp85a went as probe 50 at 05:02Z (`CONTEXT.md` l.3446-3447, l.3465).
- Friend replies: none awaited; the last friend mention in CONTEXT is the 26 Sep git-reset instruction to friend A (`CONTEXT.md` l.2175-2176, `grep -n -i friend CONTEXT.md` 07:25Z).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| **I274** (new) | "e10_port_gate.py --mode si ... --si-ref exp85a_k2cap6_div04_ra094 -> notebook-bytes FAIL ... => if BASE becomes a knob file (exp85a/86a/86b) the runbook SI (DIVINS_* only, REF=BASE) fails its own gate" | `round24/scan_plancheck.notes.md` 06:47Z | The only copy route to beat our best breaks again if a K file becomes BASE. Not in CONTEXT (W243 (1)). |
| **I275** (new) | "gate85.py lives only in session scratchpad ... Does not check node rows = exp85a"; "gate85.py (\|dn\| <= 1.5%) would pass a dead knob, and 'DIVINS ENABLED x4' would have failed good files" | `round24/scan_plancheck.notes.md`; `round24/report.json` R24-A4 why | Every exp85/86 gate used a tool that dies with this session and cannot catch a dead knob. W238 moves it to `tools/gate_dummy.py`. |
| **I276** (new) | "tools/runtime_ledger.py EXP_RULES: exp8\d -> safetail catches exp87 CI stacks" | `round24/report.notes.md` 07:16Z | A CI stack would get the 9.5 h / 8.0 h gate instead of 10.75 h / 10.2 h and be misread as 'v'. W239. |
| **I277** (new) | "ILP_DIVISION_WEIGHT 0.4 is not output-inert. It adds +3 geometric safe divisions (63->66; 36/7/5/18) through orphan daughters left by the 1:1 relink" | `round24/report.json` R24-A3 (1), new_facts | Contradicts CONTEXT l.3489-3491 ("near-inert on our base"). Dummy forks are metric-ignored, so no sign either way. W237 (1). |
| **I278** (new) | "Synthetic set = KERNEL OUTPUT josefreitasalvesneto/biohub-synthetic-dataset ... by José Freitas, not hengck23" | `round24/report.json` new_facts, R24-A10 (b) | Contradicts CONTEXT l.3509-3510 ("hengck23's synthetic 18.5 GB dataset"). W244 (b). |
| **I279** (new) | "A 76-min poller gap (05:06-06:22Z) is logged"; "if L_hi > 8.0 h comes only from a poll gap > 15 min ... code it UNPROVEN, not 'v'" | `round24/report.json` new_facts, R24-A3 (4) | A dead session can fake a 'v' near 8.0 h and drop a good cap file. W237 (4). |
| **I280** (new) | "feed loop got a 429 on GetTopic at 06:34Z (2nd run within 2 min)" | `round24/scan_plancheck.notes.md`; `experiments/discussions/feed_loop.log` | The submit guard needs "no 429"; pause the feed loop ~10 min before a submit (W242). |
| **I281** (new) | "the previous Claude session ended ~05:07Z and took its background shells with it" | `CONTEXT.md` l.3480-3481 | Same mechanism kills session timers (I116). Only the poller/E10 loop were restarted; the 29 Sep tick-check timers are likely gone (W247). |
| **I282** (new) | "exp86c: no _dl output yet (dummy status unknown)" | `round24/report.notes.md` 07:15Z | exp86c is the only D0/R+ W2b file; CONTEXT l.3519 says it "follows when a lane frees", with no confirmation (W238). |
| **I283** (new) | "Dummy runtime spread is noise, not concurrency: 1,357-1,882 s in parallel; exp75 took 2,288 s solo" | `round24/report.json` new_facts | The 1,900-1,920 s limits in gate85.py and the SEC gate (l.3427-3428) would FAIL a normal CI dummy. Runtime rule v2 (W237 (3)). |
| **I284** (new) | "No public notebook has best_public_score > 0.953"; "John Taylor's 0.953->0.957 stage ... most likely his own code" | `round24/report.json` new_facts, R24-A10 (a) | Stops manual 0.947-family scans; E10 stays the only copy route. W244 (a). |
| **I285** (new) | "Movers above us ... at 0.957 Anvith Pothula (the x138 author, submitted 00:03Z)"; 0.957 count 36 -> 41; rank #172 -> #179 | `round24/report.json` new_facts | The x138 author at 0.957 may publish a notebook: an E10 candidate (R24-A9 (3)). Context for the W241 message. |
| **I286** (new) | "user active 04:32-04:39Z ... open questions (02:00Z cap lift, Q3) can be asked now, not only in the post-47/49 brief" | `round24/scan_plancheck.notes.md` | Without the lift, all five 29 Sep slots go blind at 00:05-01:45Z (plan_issues (11)). W241. |
| I267 | "#38's 'bronze 0' comes from the field-retention prior be >= 0, not from a copy-block tie" | `round23/report.json` new_facts | The finals draft rationale is still wrong (W234 (6); l.3464 "still open"). |
| I273 | The 04:31Z card's CI note is shorter than the R22-A4 (A) caveat; v2 (9) still has the Eric-only line | `CONTEXT.md` l.3187, l.3420-3421 | W230, before 48 is read. |
| I265 | "readmitted nodes are 3.5-6x depleted near GT"; lab gains from dropping readmits are optimistic | `round23/report.json` new_facts | Now directly relevant: probe 50 raises readmits (1,365 -> 2,223). The lab cannot sign READMIT; only the LB read can. Not in CONTEXT (W202). |
| I268 | "{exp70g,exp70b} bronze: +0.024 / +0.012 / -0.008 at forkmid mean +5e-5 / 0 / -1e-4" | `round23/report.json` new_facts | Keep the neutral exp70b wording (W234 (5)). |
| I269 | "Dummy forks: x138 62, K2 75, exp70g 81, exp78a 86, exp78b 95" (now also exp85a 85, 86a 90, 86b 99) | `round23/report.json`; `round24/report.json` new_facts | The runbook forks check must use the BASE delta; l.3456-3458 does not say it was changed. |
| I270 | "outputs downloaded 01:49/01:50Z, after the 01:48Z gate line" | `round23/scan_plancheck.notes.md` 04:19Z | Proof the exp83a/b gate was pre-registered. |
| I236 / I237 | exp70g ~0.95634 unrounded (a 0.957 needs ~+1.6e-4); K2 L_hi drift 7.54 -> 7.81 h | `round21/report.json`; `round21/scan_plancheck.notes.md` | A '+' may be tiny; a 'v' may have no code cause (see I279). |
| I240 / I241 / I247 / I248 | exp60 replay DC-blind; OUTPUT_SINGLE_CHILD_REPAIR no-op; exp79a row changes; k fell to 8 | `round21/*.notes.md`; `round24/report.json` new_facts (k = 8) | k -> 0 makes every UP test BLIND '?'. |
| I206 / I209 / I218 / I219 / I227 | No coordinject/secswap gate mode; N1 staging folders; FRAME_CAP <= 2; JT "best + closest one-line neighbour" | `round22/scan_plancheck.notes.md`; `round19/`, `round20/` notes | Unchanged; I227 now also in CONTEXT l.3435-3436, l.3507 (rejected as a finals line by R24S-9). |
| I72 / I116 / I145 | No Co-Authored-By; cron fields local, timers die with the session; a submit must finish before the deadline | `memory/feedback-git-no-coauthor.md`; `round18/report.json` R18-A2 (2) | I116 is now live (W247). The last 8 commit bodies comply with I72. |
| Older I-rows | Unchanged | `_curation/23/watch.json`, `_curation/21/watch.json` | - |

**Resolved since 04:45Z (curation 23):**
- I262: runbook SI rebuilt from the BASE, REF = BASE (`CONTEXT.md` l.3456-3458); continues as I274 for K bases.
- I263: sibling CSVs downloaded, sha12 match (l.3493-3494).
- I264: the READMIT/lowrefine coupling is logged (l.3449-3451) and measured (+3.05%, l.3469).
- I266: push-by-BASE is logged (l.3462-3463). Note: exp86a and exp86b (mutually exclusive BASE branches) were both pushed at 06:36Z (l.3519-3520), under the 743929 "build during the re-run" process; with ~7.2 h GPU left this is a deliberate exception, not a violation to undo.
- I272 / W174: the loop text now uses the strict trigger (`e10_watch_loop.py` l.78).
- I250 / I251 / I256: superseded by the measured quota and the round-24 read times.
