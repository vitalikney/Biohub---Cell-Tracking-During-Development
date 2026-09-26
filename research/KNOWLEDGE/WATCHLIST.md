# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-26 03:58 UTC (curation 5). This is an incremental update of the curation-4 build from 01:20 UTC.

Sources:
- `CONTEXT.md` §14 up to the 01:20 UTC entries (l.2026-2038). Git HEAD f05389e == origin/main (committed 01:20:05Z, pushed; `git status -sb` 03:55Z).
- `experiments/lb_poll/ledger.md` (03:43:33Z) and `poll.log` (last header 03:43:32Z, l.2336).
- `experiments/RESULTS.md` l.69-71.
- `research/wf_ideas_v4/round5/report.json` (written 03:49:02Z) and `report.notes.md`. Both are **untracked**, and there is no REPORT.md.
- `research/wf_ideas_v4/round4/` (now committed in f05389e, with REPORT.md).
- `research/wf_ideas_v3/FINAL_REPORT.md`, `TASK_LOCAL_SESSION.md`, `TASK_CLOUD_SESSION.md`, `TASK_FRIEND_A.md` and `NEXT_RESEARCH.md`; `PROMPT_FRIEND_A.md`.
- The memory files (`MEMORY.md` and `project-lb-probe-approval.md`, both last modified 23:13Z).
- `tasklist` at 03:56Z: the only python process is PID 20052 (the poller).

All times are UTC. The IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, cancelled.

**State in one line.**
- #37 = K2 (`exp58` v1, ref 56563521, 00:02:12Z) and #38 = twin (`exp58n` v1, ref 56563534, 00:02:18Z) are both PENDING at 03:43:32Z, with L > 3.68 h (`ledger.md`).
- Expected scores: twin ~06:15-07:40Z, K2 ~07:50-09:30Z (`round5/report.json` new_facts 5).
- The finals default is F1 = K2 and F2 = twin. The scores are read ONLY through the READ TABLE (`CONTEXT.md` l.1978-2005) + CLARIFICATION v2 (l.2026-2032) + v3 (not written yet, W56).
- **Kaggle still shows 0/2 finals ticked.** The provisional-tick rule is now in CONTEXT (l.2034-2038).
- LB at 03:16Z: #160 of 3,922 at 0.954, 36 ranks above silver (`round5/report.json` new_facts 1).

**Changes since 01:20:**
- Done in f05389e (01:20:05Z, before any score): W44 (CLARIFICATION v2, `CONTEXT.md` l.2026-2032), W48 (the rule text, l.2034-2036), W49 (round-4 records, l.2033), the W50 checklist text (l.2036-2038), and W38 for rounds 3 and 4 (REPORT.md committed).
- W33 is closed in CONTEXT (l.2033 (6)). `DECISIONS.md` l.110-113 is aligned ([c4]).
- W46 is superseded by W55 (R5-A1): a background job with three polls, stamped after each call. W18 is absorbed into W59.
- W45 is still not done, and round 5 revised its item list (R5-A3).
- Resolved insights: I31, I32, I33, I35, I37 and I38 (now in `CONTEXT.md` l.2027-2036).
- New: W55-W60 (round 5 R5-A1..A8), T21-T23 and I39-I46.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| W56 | **READ TABLE CLARIFICATION v3 goes into CONTEXT, committed and PUSHED before the first #37/#38 result in poll.log.** Take it verbatim from the end of `plan_issues` and fill in `<hh:mm>`. It holds V1-V7. V1 (pairs, not labels): #34 is barred while the twin is f2-eligible, so C3 and row 4 without K1 give the pair {twin, exp52}. V2: checklist fix. V3: D4 dropped, K2'' = exp58d pre-registered. V4: row-5 runtime read by the bound B. V5: scope. V6: ledger texts superseded. V7: the poller stop rule and the manual-poll job. In the same commit, point the pending-OK line (`CONTEXT.md` l.2023) to the OK REQUEST entry (W45) and save round 5's REPORT.md (W60). Commit as the user, with no Co-Authored-By trailer | **not started** (`grep -c "exp58d\|K2''" CONTEXT.md` = 0) | **now; hard limit ~06:00 26 Sep** (the twin may score from ~06:15Z) | `research/wf_ideas_v4/round5/report.json` R5-A2, plan_issues 3-5, 7 + verbatim block |
| W45 | **ONE consolidated OK request to the user (in Russian), posted before any score, in the chat and as a PushNotification.** Use the round-5 text `ok_message_ru`, items 1-7: (1) K1. (2) The 0.952 twin floor. (3) Row 2, twin above K2. (4) Resubmit K2 on a "Kaggle Error". (5) K2'' = exp58d only if B > 9.0 h. (6) Close floatout, drop L1/L2. (7) The provisional tick. Round 4's item "F1 = twin instead of #34" is dropped as moot (v3 V1), and D4 is dropped. Then append "OK REQUEST posted <UTC>; poll.log last header <ts>; #37/#38 PENDING" to CONTEXT (it can share the W56 commit). When the OK arrives, log its time against the first #37 and #38 result times. An OK given after a visible score is post-hoc | **not started** (`grep -c "OK REQUEST" CONTEXT.md` = 0) | **now; before ~06:00Z** (user local time is UTC+3) | `round5/report.json` R5-A3 (`covered_by_existing_approval: false`), `ok_message_ru`, plan_issues 2 |
| W55 | **Background manual-poll job for the "clean" proof** (supersedes W46). One `run_in_background` script with three one-shots at 07:57:30Z (cap 90 s), 08:00:45Z (cap 75 s) and 08:01:45Z (cap 20 s). The timeout is min(cap, 08:02:10Z - now), the shot is skipped if the timeout is < 5 s, and the header is stamped AFTER the call. Use an absolute poll.log path. **Never import `lb_poll.py`**: its module-level `while True` would start a second poller. Do not touch PID 20052. After 08:02:12Z run `python tools/runtime_ledger.py --print`; only A5-L(K2) CLEAR proves d1 clean. Record the job's start time in CONTEXT (v3 V7) | **not started** (03:56Z tasklist: only PID 20052) | start **well before 07:45Z**; it must be running before 07:57:30Z | `round5/report.json` R5-A1 (script verbatim); `report.notes.md` 03:48Z |
| W38 / W60 | **Round reports.** Rounds 3 and 4 now have REPORT.md (f05389e). Still missing: `round2/REPORT.md` (round2 is tracked, but only as report.json and notes), and **round 5**, which is fully untracked with its REPORT.md refused by the harness. Save `round5/report.json` `report_md_ru` as `round5/REPORT.md` and commit it with W56 (R5-A8). Round 2 is low priority | partial | with the W56 commit | `git ls-files research/wf_ideas_v4` 03:55Z; `round5/report.notes.md` 03:45Z |
| W02 | Friend A "Task 0" reply: availability 26-28 Sep, the 5070 Ti, sasyami GPU hours | overdue: no friend commit since 25 Sep 12:00 (`git log --all`). Practically moot, because no lab or rider work remains | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22 |
| W03 | **The friend A card is stale.** The top block of `PROMPT_FRIEND_A.md` is still the 25 Sep ~14:30 one, which points to `TASK_FRIEND_A.md` (exp60 shard B, tempfuse LOEO). Both are cancelled. Add a "cancelled / nothing to do before 29 Sep" block, as was done for friend C (14c339e) | overdue (unchanged) | now | `PROMPT_FRIEND_A.md` l.1-3; `CONTEXT.md` l.2021 |
| W04 | Admission table in CONTEXT, updated after every score. Columns: file, public, latency, R5, riders, F1/F2 candidate. The ledger and the RESUME POINT LB line cover part of it | overdue (`grep -ci admission CONTEXT.md` = 0) | after each score; final version 28 Sep 22:00 | `TASK_CLOUD_SESSION.md` T13; `FINAL_REPORT.md` §d |
| W05 | Commit `experiments/ext_corwin-biocel-aux/` and `experiments/ext_y3uanm-secondary-ft/` without `__pycache__`. `FINAL_REPORT_v4.md` §2 cites both | overdue (still untracked at 03:55Z) | 25 Sep | `git status` 03:55Z |
| W34 | Memory pointers, residual. `MEMORY.md` l.8 still says "gated riders K3/K3b/K4/N1" (all closed). `project-lb-probe-approval.md` l.14 still says "K2 ... pre-approved ~00:55 UTC" (it was submitted at 00:02:12Z). The refs 56563521 and 56563534 are not listed | mostly done | low; with the next memory touch | memory files (mtime 23:13Z); `CONTEXT.md` l.2006-2008, l.2021 |

## NEXT 24 H (26 Sep 03:58 -> 27 Sep 03:58 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W56 / W45 / W55 | **now -> 06:00** (W55 by ~07:45) | See OVERDUE. These are the only urgent pre-score items | not started | `round5/report.json` next_focus |
| W10 | round 6 ~05:45 (skippable); next useful round **~09:40** | Round 5 finished at 03:49Z. **Round 6** is a short pre-score audit: v3 pushed and the OK REQUEST posted and timestamped before the first result; the manual-poll job and PID 20052 alive; AC power on; at most a 2-minute LB glance. **Cancel it** if the main session confirms all of this by ~05:30Z. The **post-score round** (~09:40Z, or when K2 is terminal) does the mechanical read, L and B, the scope line, the OK-vs-score timing, the tick pair, and K2'' support only if the trigger fired | round 5 done; round 6 optional | `round5/report.json` next_focus |
| W19 / W52 | **now -> both terminal** (at least to the first poll after 09:32:18Z) | Keep the Claude session that owns the poller (PID 20052) open and the machine on AC. **No builds, pushes of code or submits tonight** (R5H-9). New stop rule: do not stop the poller until poll.log shows COMPLETE or ERROR for both 56563521 and 56563534. If either is still PENDING, keep it at least until the first poll after 09:32:18Z (this replaces "~09:30Z") | in progress (poller alive at 03:56Z; 0 gaps > 15 min) | `round5/report.json` R5-A5 (6), plan_issues 7, v3 V7; `ledger.md` Poll health |
| W58 | optional **now** (never inside 07:45-08:35Z); **mandatory before any K2'' build** | **Prepare the K2'' builder change, without building or pushing.** Non-lab safetail builds should accept exactly (34200, 28800) or (37800, 32400), and refuse DIVINS alone. Add tests to `tests/test_safetail.py`, run pytest, rebuild K2 in a scratch copy and confirm sha 1f1ddb6d63b47f54..., and add a 10.5 h ledger family for exp58d (or use --family). exp58d is built and submitted only after the trigger fires AND the user says yes | not started | `round5/report.json` R5-A4; builder check at `tools/build_probe_kernel.py` l.2021-2022 |
| T13 | ~06:15-07:40 | The twin (#38) may score. **Do not act on the twin alone.** Rows 2-5 are read only when both files are terminal. Row 1 (K2 ERROR) may be read on K2 alone | watch | `CONTEXT.md` l.2027 (C1) |
| T21 | ~07:50-09:30 | K2 (#37) is expected. The forecast F = 7.87 h puts the finish at ~07:54Z | watch | `round5/report.json` new_facts 5; R5-A1 why |
| T14 | **08:02:12Z** | The 8.0 h "clean" mark for K2 (the in-kernel insertion deadline). The poller's own polls fall at ~07:54:1x-2xZ and ~08:04:1x-2xZ and straddle the mark, which is why W55 exists | watch | `ledger.md` A5-L(K2); `round5/report.notes.md` 03:36Z |
| W47 | when both are terminal (~07:50-09:40) | **Mechanical score read** (R4-A4 + R5-A5). (1) Run `runtime_ledger.py --print`. (2) Compute k, w, d1, d2, tk and "clean"; first match wins among rows 1-5 + C2-C5 + v3 V1-V4. (3) On a K2 ERROR, read the error class first with the C2 one-liner (verified read-only on kaggle 2.2.4). (4) Record L(K2) and L(twin) and B = min(L(K2)_hi, L(K2)_hi - L(twin)_lo + 6.56 h, L(twin)_hi + 1.95 h). (5) Write the scope line. (6) If the trigger fires (L(K2)_hi > 8.0 h or unproven), raise K2'' with B: <= 8.0 h ~0 value; 8.0-9.0 h optional; > 9.0 h recommend. (7) Log the row, the commit/push times of the table, v2 and v3, and the first-result times. Scores come from poll.log only, never from the LB rank | pending | `round5/report.json` R5-A5; `CONTEXT.md` l.1978-2005, l.2026-2032 |
| T15 | **08:32:12Z** | The A5 watch window ends. The session may be released only under the W19 stop rule | - | `ledger.md` A5-L(K2) |
| T16 | **09:32:12Z** (K2) / 09:32:18Z (twin) | The 9.5 h R5(a) mark. If L <= 9.5 h, R5(a) is proven. If not, R5(b) still admits both unless they ERROR | watch | `CONTEXT.md` l.1968-1970 |
| W54 | right after W47 (~09:30-10:00) | **Provisional tick.** Recommend the pair with refs (default #37 56563521 + #38 56563534). The user ticks EXACTLY two files; check that 2/2 are ticked and record it in CONTEXT. Never leave 0/2 or 1/2 | not started (the rule is in `CONTEXT.md` l.2034-2036) | `round5/report.json` R5-A5 (5); `CONTEXT.md` l.2034-2036 |
| W35 | at the score | RESULTS.md: fill rows l.70-71 (#37/#38 scores and L), plus a one-line exp60 note or a pointer to `experiments/exp60_trainlab/results.md` | partial (`grep -c exp60 RESULTS.md` = 0) | `experiments/RESULTS.md` l.69-71 |
| W57 | next CONTEXT write; curator by **26 Sep 12:00** | **Round-5 records** (R5-A6). (1) Intel line at 03:16Z: #160/3,922, 6th of 73 in the 0.954 block (155-227), silver ~196 (36 ranks margin), 15 more late x138 copies (5th window). (2) FACTS R5H-1, R5H-2, R5H-3/4, R5H-5 and R5H-7. (3) R5-RC-A post-freeze FACT (I39); optionally fix `CONTEXT.md` l.22. (4) R5-RC-B closed; fork-removal riders on x138 are 0 for 5 (I40). (5) R5-RC-C: add the new AdaBN blocker to B5 (l.196) (I44). (6) W44 is done | not started | `round5/report.json` R5-A6 |
| W31 | **by 26 Sep 12:00** | Curation-3 closures still not in CONTEXT: (1) the R2S-6 info-only note. (2) The lab calibration rule for node-adding arms (I23). The lp30 counterpart is now at l.2033 (5), but the rule itself is not. (3) Axis-flip I-151 (`grep -c I-151 CONTEXT.md` = 0). (4) Tail-bug fixes, retention hysteresis (I29; `grep -c hysteresis` = 0) and density-gated insertion. (5) "x138 tail saturated" with the numbers (I21). (6) The M6 lapse note (T12). Merge these with W57 | partial | `CONTEXT.md` l.2033; `round3/report.json` R3-A8 |
| W50 | the durable reminders **by 28 Sep** | The checklist text is in CONTEXT (l.2036-2038). **Missing:** 29 Sep 12:00 and 18:00 reminders that survive this session (a cloud routine or the user's calendar). No evidence yet. Also, the checklist clause "Never tick #34" conflicts with C3/row 4 (see W56, v3 V2) | partial | `CONTEXT.md` l.2037-2038; `round5/report.json` plan_issues 4 |
| W23 | every ~6 h (next ~09:15) until 29 Sep 07:00 | x138 successor watch (E10). The 03:16Z check found nothing: no public run >= 0.954, and x138 is still v1 (189 votes, 266 copies). Track it by slug or author, not by title | in progress | `round5/report.json` new_facts 4 |
| W59 | **after ~09:40Z**, never inside 07:45-08:35Z | Optional `tools/runtime_ledger.py` text fix. A6 becomes "read the error class per CONTEXT C2; K3 closed", the A5 ask offers K2'' only, and the default is F = 7.87 h. Run pytest `tests/test_runtime_ledger.py`. No poller restart is needed. Absorbs W18 ("Forecast F not supplied") | not started | `round5/report.json` R5-A7, new_facts 9; `ledger.md` A5-F |
| W26 | any time 26 Sep | Day-2 cloud research (`NEXT_RESEARCH.md`) was superseded by the night rounds. Record it as "cancelled" in CONTEXT | not started (`grep -c NEXT_RESEARCH CONTEXT.md` = 0) | `research/wf_ideas_v3/NEXT_RESEARCH.md` |
| W53 | after both are terminal, optional | Change the poller to log `error_description` (the API has it, the CLI CSV does not). Deferred, because it needs a poller restart | deferred | `round4/report.json` R4-A9 |
| T12 | **26 Sep 18:00** | The M6 reopen window for K4/tempfuse lapses. Nobody owns it. Note the lapse in CONTEXT (with W31) | pending (expected lapse) | `CONTEXT.md` 20:55 (M6) |
| T17 | 26 Sep, any free slot, **only through the READ TABLE with an OK** | 26 Sep has 3 unused slots. Allowed contents: K1 = exp58t v1, a K2 resubmit (C2a), K2'' = exp58d (v3 V3, trigger + OK), or an S10-S11 retry of a failed K build | - | `CONTEXT.md` l.2012-2013, l.2033 (7); `round5/report.json` R5-A4 |
| T18 | **27 Sep 00:00** | The slot counter resets: 5 slots for 27 Sep. Nothing is planned unless K1, K2'' or a retry is needed | - | `CONTEXT.md` 13:38 (slot plan S7-S11) |
| W15 | - | GPU quota check: optional. Nothing uses the GPU | optional | `round3/report.json` R3-A6 |

## LATER (27 Sep 03:58 -> 29 Sep 23:59 UTC)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T02 | 27 Sep ~09:00 | LB snapshot and rank line (compare with #160 at 03:16Z 26 Sep, 36 ranks above silver) | `FINAL_REPORT_v4.md` §3 item 8; `round5/report.json` new_facts 1 |
| T03 | **27 Sep 12:00** | **R8: no new mechanisms after this.** The search is already over (`CONTEXT.md` l.2021-2022). After the cutoff only K1 / K2'' per the table and S8 for an x138 successor (E10) remain. A post-freeze fix (I39) is explicitly post-deadline | `CONTEXT.md` 13:38 R8; `round5/report.json` rejected 10 |
| T04 | **28 Sep 12:00** | S12 consolidation of F1-final. **Moot:** no rider passed, and floatout is closed (`CONTEXT.md` l.2033 (6)) | `CONTEXT.md` l.1614 |
| T05 | 28 Sep 16:00 | S13: repeat S12 on error (moot) | `CONTEXT.md` l.1615 |
| T19 | **28 Sep evening** | Confirm the F1/F2 refs (checklist step 1). The durable 29 Sep reminders must exist by now (W50) | `CONTEXT.md` l.2037 |
| T06 | 28 Sep 22:00 | Final admission table (W04) | `FINAL_REPORT.md` §d |
| T20 | **29 Sep 00:00** | The last slot reset (5 slots). After 02:00 only S17 (an emergency repeat of F1-final); hard edge 10:00 | `CONTEXT.md` 13:38 R8, S17 |
| T07 | 28-29 Sep | Risk: queue latency above 10 h (other teams' reruns take 7-10 h). If it happens, R5(b) decides | `FINAL_REPORT.md` §g item 6 |
| T09 | 29 Sep ~11:30 / **12:00** (backup **18:00**) | At 11:30, draft the tick check (provisional ticks vs the table). At 12:00, remind the user to CHECK the ticks, which should already be set (W54). Backup reminder at 18:00 | `CONTEXT.md` l.2036-2037 |
| T10 | **29 Sep 20:00** | The USER finishes ticking. Default pair: K2 #37 56563521 + twin #38 56563534 (twin scored without error, R5-admissible, >= 0.953). Otherwise use the table + v2 + v3. By v3 V1, #34 56545267 is tickable only when no eligible non-copy x138-family file exists; then the pair is {#34, exp52 56534391}. Never tick #35, P36, K2 together with K2'', or two files with identical components. Never auto-select | `CONTEXT.md` l.2004-2005, l.2017-2020, l.2036-2038; `round5/report.json` v3 V1-V2 |
| T11 | 29 Sep 23:59 | Competition deadline | `CONTEXT.md` §1 |
| W29 | after 29 Sep | E14: friend A's honest out-of-embryo A/B. Inputs: the error anatomy (I06, I21, I22), post-freeze transitions (I39), DeepCenter t* (I19), the clip-boundary deficit (I28), and the lab calibration (I23 + lp30 at `CONTEXT.md` l.2033 (5)) | `TASK_FRIEND_A.md` "Задача 4" |

**Done or cancelled since 01:20 (for the record):**
- W44 done: CLARIFICATION v2 is at `CONTEXT.md` l.2026-2032, committed in f05389e at 01:20:05Z and pushed before any score (`round5/report.json` new_facts 6). The pending-OK line l.2023 was not changed (moved to W56).
- W48 done (the rule text): `CONTEXT.md` l.2034-2036. The tick itself is W54.
- W49 done: round-4 records (1)-(8) are at `CONTEXT.md` l.2033. The curator took them in [c4] (`research/KNOWLEDGE/DECISIONS.md` G15, l.107-113).
- W33 closed: floatout is closed for the finals (`CONTEXT.md` l.2033 (6)). The user's formal OK is item 6 of W45.
- W22 done for 00:47Z (`CONTEXT.md` l.2033 (1)). The 03:16Z line is in W57.
- W46 superseded by W55. W18 absorbed into W59. W28 recorded (`CONTEXT.md` l.2033 (3)).
- Earlier: W06, W14, W16, W36, W37, W39, W40 and W41 done (curation 4). W01, W08, W09, W11, W12, W17 and W30 done. W07, W13, W24, W27 and T01 cancelled. W20 was superseded by W47, and W21 by W45 (`research/KNOWLEDGE/_curation/4/watch.json`).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| I45 | **"Kaggle scores the best of the two ticked files; F1/F2 are rule labels only. #34 (56545267) is exp56, a byte copy of x138 ... C3 and row 4 without K1 give the PAIR {twin #38, exp52} when the twin is so eligible"** | `round5/report.json` plan_issues 4 + v3 V1; `report.notes.md` 03:40Z | **Contradiction in CONTEXT today:** C3's strict text "[F1 = #34, F2 = twin]" (l.2029) and row 4's "[else §f item 4 = #34]" (l.1999) conflict with the Never line (l.2004-2005), f2 (l.1893-1894) and the checklist "Never tick #34" (l.2038). Only v3 (W56) resolves it |
| I42 | "Our submissions run concurrently (#34 08:09Z and #35 08:33Z both done by 16:17Z) ... L(K2) - L(twin) measures the insertion's runtime cost" | `round5/report.json` new_facts 8, plan_issues 5 | Row 5 (`CONTEXT.md` l.2002-2003) reads "L(twin) >= L(K2) - 0.3 h means queue delay dominates". That is mis-specified, and v3 V4 replaces it with the bound B |
| I43 | "build_probe_kernel.py l.2021-2022 exits on any non-lab build with REPAIR_DEADLINE_S != 34200 ... DIVINS_DEADLINE_S alone is accepted ... D4/DIVINS_TWOSTAGE exists only in the ledger's ask text" | `round5/report.json` new_facts 7; `report.notes.md` 03:37Z | The "deadline move / D4" runtime trigger (row 5; v4 item 5) cannot be built as written, and the only move that builds (DIVINS alone) is harmful. Hence W58. Also, the token `exp58d` maps to the 9.5 h ledger family, which is the wrong column |
| I41 | "Kaggle reruns once over the whole hidden test (public + private) ... CLEAN (L(K2)_hi <= 8.0 h) certifies public AND private; a fired 8.0 h gate turns K2 into the twin on the last-sorted clips only; the 9.5 h degrade is the only large-loss path" | `round5/report.json` new_facts 10, 15 (R5H-1, R5H-6) | Once #37/#38 are COMPLETE, there is no private-only crash risk. That stops the "hunt for private-only crashes" work (rejected 14) and bounds the not-clean cost |
| I39 | "Post-freeze GT edges 2,066: FN 10.3% vs 4.5% normal, FP/TP 13.1% vs 4.8% ... lab ceiling +0.0063 pooled ... Frozen GT steps have median 0 (GT copies positions on frozen frames; CONTEXT l.22 'GT still moving' is wrong for most) ... A post-relink re-solve limited to post-freeze transitions IS CPU-replayable from the exp60 presafe dump" | `round5/report.json` new_facts 17 (R5-RC-A) | The largest identified remaining defect on x138, shared by all finals. `grep -c post-freeze CONTEXT.md` = 0, and `CONTEXT.md` l.22 is factually wrong. Post-deadline linker item #1 (geometric/flow cost only) |
| I40 | "Fork-removal riders on x138: 0 for 5 (4 measured: forkmid power, forkblob, ANTIPAR, already-divided; DNVETO by analogue)"; the already-divided filter is -0.00068 (control) / -0.00055 (ins35), all from 2 clips | `round5/report.json` new_facts 18 | Closes the fork-removal family on x138. Without a CONTEXT line (W57 (4)) it will be re-proposed. Pair with I15 |
| I44 | "The V1284 head (x138's +0.007), lowrefine and DaughterNet all read unadapted 224-d detector features; the node-count guard cannot detect feature drift" | `round5/report.json` new_facts 19 (R5-RC-C) | This is a new blocker for AdaBN (B5, `CONTEXT.md` l.196), which lists only the older reasons. Relevant to any post-deadline test-time adaptation |
| I46 | "Movers ... Ad Space available 0.961->0.965, Nabil Hanif 0.959->0.964, Bio-Pirates 0.950->0.960 (177 subs) ... None has public biohub code or datasets (fits private retrained models, R9-barred for us)"; the silver margin went 41 -> 36 in 2.5 h without any change on our side | `round5/report.json` new_facts 1-2 | Our rank decays through other teams' retrained models. The silver margin (I12/I18) may be gone by 29 Sep. The rank is information, never an input |
| I36 | A poll with one failed attempt proves clean only if its header is <= 07:58:42Z (+210 s). Round 4's one-liner stamped BEFORE the call with a 180 s timeout, so a PENDING returned after 08:02:12Z could fake A5-L FIRED | `round4/report.notes.md` 01:02Z; `round5/report.json` rejected 9, `report.notes.md` 03:48Z | The W55 design (capped timeout, stamp after the call) fixes it. Nothing in CONTEXT fixes it until v3 V7 is written |
| I34 | "The 44b6 '+0.0157' is one TP (SELECTION 0.0000) ... insertion +0.00648 pooled ... the dense half has 2 TP / 4 FP, so a dense private embryo could give K2 ~= twin" | `round4/report.json` new_facts | `CONTEXT.md` l.1932 still quotes "+0.0157 / +0.0090". The evidence is thin, which is the case for the twin as F2 |
| I01 | "Of x138's forks, 24% (15/62 on the dummies) are one-blob duplicates at t+1, against 2% of GT divisions" | `research/wf_ideas_v4/lens_literature.json` plan_critique 1-2 | The main fact for division work after 29 Sep. Every removal rule failed to exploit it (I40) |
| I02 | "1 of 10 lab gains transferred ... a lab-based slot decision is allowed only for arms whose learned inputs are out-of-sample" | `research/wf_ideas_v4/lens_mine-old.json` plan_critique (4) | Not in CONTEXT (`grep "1 of 10"` = 0) |
| I04 | "DeepCenter score recorder and the TRAINLAB summary cell are not fail-soft ... 7 of 17 44b6 picks are leak-siblings" | `CONTEXT.md` 14:29 (T5) | 44b6 lab deltas are partly in-sample |
| I05 | "K2 forecast <= 7.86 h ... the insertion gate at 8.0 h is only +0.14 h above that" (refined to 7.87 h) | `lens_headroom.json` critique (2); `CONTEXT.md` l.1970 | This is why "clean" is not guaranteed and why W55 exists |
| I06 | K2 dummy vs train GT: "FN 82 of 2,127 GT edges. 50% are swaps, 23% one-free-end fragments, 6% end-anchored node misses" | `lens_mine-old.json` critique (3) | It conflicts with I21/I22, where the "swaps" are really node misses. Reconcile the two after 29 Sep |
| I07 | "lowrefine is not a coordinate-only rider ... +33 final nodes, +29 edges and +1 fork" | `lens_redteam-plan.json` RT2 | Why the table needs d2. Compare with R5H-5: shared lowrefine risk <~5e-4 (`round5/report.json` new_facts 14) |
| I08 | Kernel time is not a hidden-test budget signal; use the per-dataset `[ds] repair` lines | `research/wf_ideas_v3/FINAL_REPORT.md` §j item 19 | Start-up noise is 818-1179 s |
| I09 | "Блок 0.953 на private останется единым" is untested | `FINAL_REPORT.md` §g item 13 | Late x138 copies land at the END of the 0.953 block for the 5th window in a row (`round5/report.json` new_facts 3). This backs "never tick a verbatim copy" |
| I12 / I18 | The silver line (~196) sits INSIDE the 0.954 block. The margin went 38 -> 32 -> 41 -> **36** ranks (19:46 / 22:16 / 00:47 / 03:16) | `round2/`-`round5/report.json` new_facts | See I46 |
| I14 | Stale operational text: `TASK_LOCAL_SESSION.md` l.12 and `TASK_FRIEND_A.md` l.40, l.52 name branch `claude/practical-meitner-31k9ye`, but the work lands on `main` | those files | Same risk as W03 |
| I15 | "The public read over-rewards fork REMOVALS whose precision lies between the private break-even (0.11-0.20) and 0.265" | `round2/report.json` plan_issues (R2-RC-B); `CONTEXT.md` l.1644 | Any future removal rule needs a private break-even clause |
| I17 | "FLOATOUT_CHECK (build_probe_kernel.py l.1315-1362) is a bare-assert cell, not fail-soft" | `round2/report.json` new_facts (12) | Moot while floatout stays closed |
| I19 | **DeepCenter t* = 0.30 is the lab optimum** in the removal direction (6bba div 15/11/73 vs control 15/17/73). It is NOT node-preserving (nodes -79/-49) | `experiments/exp60_trainlab/results.md` l.13-18, l.61-66 | CONTEXT l.1930 gives only the failed gates |
| I21 | "The x138 tail is saturated. Edge FN 1,705 of 40,093 = node misses 834 (49%), swaps 730 (43%), dangling ends 141 (8%) ... the remaining error mass needs retraining" | `round3/report.json` new_facts (13); `research/KNOWLEDGE/FACTS.md` F-TRN-15 | In KNOWLEDGE but NOT in CONTEXT (W31 (5)) |
| I22 | "There are 0 true 2x2 swaps ... our nodes sit 3.9-4.2 um from the GT nuclei ... 6bba holds 485 of the 555" | `round3/report.json` new_facts (14); `CONTEXT.md` l.1974 (short form) | "Swaps" are a detection/localization problem |
| I23 | "The CONFIRMATION half reads every node-adding arm as positive (L4 +0.00099, L5 +0.00041, rescue +0.00109), while the LB read MIN_TRACK_LEN 4 at -0.002" | `round3/report.json` R3-A8 (3), new_facts (16) | The calibration rule is still not in CONTEXT (W31 (2)). Its node-removing counterpart, lp30 (no bias), is now there (l.2033 (5)) |
| I24 | "Evaluable precision: sparse half 8 TP / 3 FP, dense half 1 TP / 3 FP ... private harm needs out-of-fold evaluable precision < ~11% (q* = 0.114)" | `round3/report.json` new_facts (11); `FACTS.md` | The quantitative case for the twin hedge |
| I26 | "hidden-rerun latency is 7-10 h with no queue problem" (other teams) | `round3/report.json` new_facts (2); `CONTEXT.md` l.1526 | Makes "not clean" (row 5) a live branch |
| I28 | "GT node recall before safe divisions -> final: t0 0.959 -> 0.940 ... boundary edge TP rate 0.926 vs 0.958" | `round3/report.json` new_facts (15) | The clip-boundary node loss is deferred until after 29 Sep |
| I29 | The retention guard has no flicker penalty: switch pairs 6.05% FN, between blended 3.17% and primary 10.71% | `round3/report.json` new_facts (17); `FACTS.md` F-TRN-18 | Closes hysteresis. Not in CONTEXT (W31 (4)) |

Resolved since 01:20:
- **I31**: auto-selection when 0/2 are ticked is in the PROVISIONAL rule (`CONTEXT.md` l.2034-2036).
- **I32**: "the LB rank is never an input" is in C1 (l.2027).
- **I33**: the error_description one-liner is in C2 (l.2028).
- **I35**: lp30 is in `CONTEXT.md` l.2033 (5).
- **I37**: the x138 rename and "y3uanm has no public weights" are in `CONTEXT.md` l.2033 (8).
- **I38**: the head-shift and refined-duplicate closures are in `CONTEXT.md` l.2033 (3)-(4).
- Earlier: I03, I10, I11, I13, I16, I20, I25, I27 and I30.
