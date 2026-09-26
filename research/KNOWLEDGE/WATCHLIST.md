# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-26 01:20 UTC (curation 4). This is an incremental update of the curation-3 build from 25 Sep 23:05 UTC.

Sources:
- `CONTEXT.md` §14 up to the 26 Sep 00:02 UTC RESUME POINT (l.2006-2025). Git HEAD b2cb928 == origin/main, pushed 00:02:49Z.
- `experiments/lb_poll/ledger.md` (01:03:05Z) and `poll.log` (last block 01:03:03Z).
- `experiments/RESULTS.md` l.69-71.
- `research/wf_ideas_v4/round3/` (committed in 1017c41).
- `research/wf_ideas_v4/round4/report.json` and `report.notes.md`. Round 4 wrote them at 01:15Z. They are **untracked** and there is no REPORT.md.
- `research/wf_ideas_v3/FINAL_REPORT.md`, `TASK_LOCAL_SESSION.md`, `TASK_CLOUD_SESSION.md`, `TASK_FRIEND_A.md` and `NEXT_RESEARCH.md`.
- `research/wf_ideas_v4/FINAL_REPORT_v4.md`.
- The memory files `MEMORY.md` and `project-lb-probe-approval.md` (both modified 23:13Z).

All times are UTC. The IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, cancelled.

**State in one line.**
- #37 = K2 (`exp58` v1, ref 56563521, submitted 00:02:12Z) and #38 = twin (`exp58n` v1, ref 56563534, submitted 00:02:18Z) are both PENDING at 01:03Z (`CONTEXT.md` 00:02; `ledger.md` 01:03Z).
- P36 = 0.954. It is info only (`CONTEXT.md` l.2010-2011).
- Expected scores: twin ~06:20-07:40Z, K2 ~07:00-08:00Z (`round4/report.json` new_facts).
- The finals default is F1 = K2 and F2 = twin. The scores are read ONLY through the READ TABLE (`CONTEXT.md` 23:12, l.1978-2004).
- **Kaggle currently shows 0/2 finals ticked.** If nothing is ticked, Kaggle auto-fills with P36 and #35, and neither is admissible (`round4/report.json` R4-A5, new_facts).

**Changes since 23:05:**
- Done: W06, W14, W16, W36, W37, W39, W40 and W41 (a)-(c) (commits 1017c41 and b2cb928).
- Mostly done: W34 (memory index fixed at 23:13Z).
- Cancelled or closed: W07 (forkmid closed) and W28 (head-shift scale closed by round 4).
- Recommended close: W33 (floatout).
- Superseded: W20 by W47 and W21 by W45.
- Resolved insights: I03, I11, I25, I27 and I30.
- New: W44-W54 (W44-W52 = round 4 R4-A1..A9), T13-T20 and I31-I38. W42/W43 were never used (curation 3 announced "W36-W43" but used only W36-W41).

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| W44 | **READ TABLE CLARIFICATION v2 goes into CONTEXT, committed and PUSHED before any #37/#38 score reaches poll.log.** It covers: C1 (when to read), C2 (row 1 by error class, with the `error_description` one-liner), C3 (row 1 without K1: F1 = twin [OK] instead of #34), C4 (the row-2 hole: K1 [OK] when twin - K2 >= +0.002 and d1 <= -0.002), C5 (row 5 with d2 undefined: F1 = K2, F2 = exp52) and C6 (extra polls). Take the text verbatim from the end of `plan_issues`. Do not edit the 23:12 rows. Also fix the pending-OK line of the RESUME POINT at `CONTEXT.md` l.2023 | **not started** (`grep CLARIFICATION CONTEXT.md` finds only the 23:12 heading) | **now; hard limit ~06:00 26 Sep** (the twin may score from ~06:15Z) | `research/wf_ideas_v4/round4/report.json` R4-A1, plan_issues items 1 and 7 |
| W45 | **ONE consolidated OK request to the user (in Russian), posted before any score.** (1) The default world needs no OK. (2) Conditional OKs, each with its trigger: (a) K1 exp58t, (b) a 0.952 twin floor, (c) row-2 F1 = twin / F2 = K2 or K1, (d) F1 = twin instead of #34, (e) resubmit K2 after a "Kaggle Error", (f) a deadline move or D4 only if L(K2) > 8.0 h. (3) Floatout: recommend CLOSE. (4) The provisional tick (W48). (5) L1/L2: drop. When the OK arrives, log its UTC time against the first-score times. An OK given after a visible score is post-hoc. This supersedes W21 | **not started** (no CONTEXT record) | **now; before ~06:00 26 Sep** | `round4/report.json` R4-A2 (not covered by the existing approval); `CONTEXT.md` l.2023 (the list there is incomplete) |
| W38 | **Round reports.** round3/ was committed (1017c41), but `round4/` is untracked. REPORT.md is missing for rounds 2, 3 and 4, because the harness blocks the subagent from writing .md files. Save each `report_md_ru` as REPORT.md, commit, and fix the citations at `CONTEXT.md` l.1938 and l.1967 and in the round prompt (= R4-A8, W51) | partial | any quiet moment after round 4; before round 5 is best | `git status` 01:07Z (`?? research/wf_ideas_v4/round4/`); `round4/report.json` R4-A8, report_md_ru_note |
| W02 | Friend A "Task 0" reply: availability 26-28 Sep, the 5070 Ti, sasyami GPU hours | overdue (still no commit and no CONTEXT note). Practically moot: no rider or lab work remains before R8 | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22; `git log -- PROMPT_FRIEND_A.md` (last fea74ea) |
| W03 | **The friend A card is fully stale.** The top block of `PROMPT_FRIEND_A.md` is still the 14:30 one, which points to `TASK_FRIEND_A.md` (exp60 shard B by 08:00 26 Sep, tempfuse LOEO by 06:00 27 Sep). Both are cancelled: exp60 finished at 20:05 and K4 was dropped (M6). Add a "cancelled / nothing to do before 29 Sep" block, as was done for friend C (14c339e) | overdue | now | `PROMPT_FRIEND_A.md` l.1-3; `TASK_FRIEND_A.md` l.31-65; `CONTEXT.md` 20:55 (M6), l.2021 |
| W04 | Admission table in CONTEXT, updated after every score. Columns: file, public, latency, R5, riders, F1/F2 candidate. The ledger and the RESUME POINT LB line cover part of it | overdue (`grep -i admission CONTEXT.md` = 0) | after each score; final version 28 Sep 22:00 | `TASK_CLOUD_SESSION.md` T13; `FINAL_REPORT.md` §d |
| W05 | Commit `experiments/ext_corwin-biocel-aux/` and `experiments/ext_y3uanm-secondary-ft/` without `__pycache__`. FINAL_REPORT_v4 §2 cites both | overdue (still untracked at 01:07Z) | 25 Sep | `git status` 01:07Z |
| W49 | **Records and closures from round 4 into CONTEXT, then to the curator.** (1) Intel at 00:47Z: #155/3,919, 6th of 73 in the 0.954 block (150-222), silver ~196, 41 ranks margin. (2) INFO ONLY: P36's unrounded score is above #35's. (3) CLOSED: head-shift scale I-035/C09/E12 (was W28). (4) Refined-duplicate collapse stays closed. (5) Leaf prune on x138 CLOSED, plus the exp60 lp30 FACT (I35). (6) Floatout closed for the finals; align KNOWLEDGE I-215 and `DECISIONS.md` l.96-98 with `CONTEXT.md` l.2022. (7) S4-S11 carry no new mechanism; list the exceptions. (8) x138 was renamed; y3uanm has no public weights. The **still-open curation-3 closures** also belong here (W31) | not started | next CONTEXT write; curator by **26 Sep 12:00** | `round4/report.json` R4-A6; `grep "#155\|lp30\|C09" CONTEXT.md` = 0 |
| W34 | Memory pointers. Done at 23:13Z: the `MEMORY.md` l.9 "Resume point" line now says "LAST RESUME POINT block + every dated entry after it", and `project-lb-probe-approval.md` has f2 at 22:06. **Residual:** the approval body still says "K2 ... ~00:55 UTC" (it was 00:02). Neither file lists the refs 56563521 and 56563534 (R4-A9 optional line). `MEMORY.md` l.8 still lists "gated riders K3/K3b/K4/N1", which are now all closed | mostly done | low; with the next memory touch | memory files as read at 01:10Z; `CONTEXT.md` l.2021 |

## NEXT 24 H (26 Sep 01:20 -> 27 Sep 01:20 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W44 / W45 | **now -> 06:00** | See OVERDUE. These are the only urgent pre-score items. Round 5 checks them first | not started | `round4/report.json` next_focus |
| W10 | ~03:15 (round 5), ~05:45 (round 6) | Round 4 finished at 01:15Z. **Round 5** is monitoring plus a pre-score audit: check that W44 is pushed and W45 is posted, that W46 is scheduled, and that the poller, the session and AC power are up; a light LB delta; no mining. **Round 6** is optional: cancel it if round 5 finds everything in place | round 4 done; round 5 and 6 pending | `round4/report.json` next_focus; `round4/report.notes.md` 01:06Z |
| W48 | rule text **now**; the tick as soon as the READ TABLE resolves (~08:00-09:00) | **PROVISIONAL FINALS TICK.** Add the rule to CONTEXT and to the morning brief. The user ticks EXACTLY two files in the Submissions UI: by default F1 = #37 56563521 and F2 = #38 56563534, or whatever the table gives. Never leave 0/2 or 1/2. Re-tick only if a later row, a K1 score or S12 changes the pair. Ticks can be changed until the deadline | not started (`grep -i provisional CONTEXT.md` = 0) | `round4/report.json` R4-A5 (needs the user's OK), new_facts ("0/2 finals selected" at 00:57Z) |
| W46 | schedule **before 07:45**; polls at **~07:57:30Z and ~08:00:45Z**, only if #37 is still PENDING at 07:45Z | **Extra one-shot polls for the "clean" proof.** Use the exact one-liner in R4-A3 (poller header format), then `python tools/runtime_ledger.py --print`. Avoid the poller's own minutes (~07:54:2x and ~08:04:3x). A poll proves "clean" only if its header is <= 08:02:12Z, or <= 07:58:42Z when it had a failed attempt (+210 s). Do NOT restart the poller | not started | `round4/report.json` R4-A3, `report.notes.md` 01:02Z; `ledger.md` A5-L(K2) |
| W19 / W52 | **now -> 08:32:12Z** | Keep the Claude session that owns the poller (PID 20052, alive since 23:12:45Z) open and the machine on AC. **No builds, pushes or submits tonight.** Never restart the poller between 06:00 and 09:30Z | in progress (last poll 01:03:03Z, 0 gaps > 15 min) | `round4/report.json` R4-A9; `ledger.md` Poll health |
| T13 | ~06:15-07:40 | The twin (#38) may score. **Do not act on the twin alone.** Rows 2-5 are read only when both files are terminal. Row 1 (K2 ERROR) may be read on K2 alone (clarification C1, once W44 is in) | watch | `round4/report.json` plan_issues C1 |
| W47 | when both are terminal (~06:20-08:30) | **Mechanical score read** (R4-A4, which supersedes W20). (1) Run `runtime_ledger.py --print`. (2) Compute k, w, d1 = k - 954, d2 = w - 953, tk = w - k and "clean". (3) First match wins: R1 K2 ERROR (by error class, C2); R2 tk >= 2 (C4 if d1 <= -2); R3 d1 >= -1; R4 d1 <= -2 and clean; R5 d1 <= -2 and not clean (C5 if d2 is undefined). (4) Log k, w, d1, d2, tk, clean, L(K2), L(twin), L(K2) - L(twin) (= the old W41 (d)), the row, and the commit/push times ("table 1017c41 pushed 23:13:16Z; clarification <sha> <ts>; first result <ts>"). Scores come from poll.log only, never from the LB rank (I32). Likely outcome: R3, giving F1 = K2 and F2 = twin | pending | `round4/report.json` R4-A4; `CONTEXT.md` l.1978-2004 |
| T14 | **08:02:12Z** | The 8.0 h "clean" mark for K2 (the in-kernel insertion deadline). COMPLETE seen by then means clean | watch | `ledger.md` A5-L(K2) |
| T15 | **08:32:12Z** | The A5 watch window ends; the session may be released after this | - | `ledger.md` A5-L(K2); R4-A9 |
| T16 | **09:32:12Z** (K2) / 09:32:18Z (twin) | The 9.5 h R5(a) mark. If L <= 9.5 h, R5(a) is proven. If not, R5(b) still admits both unless they ERROR (1.63 h forecast margin) | watch | `CONTEXT.md` 23:12 (R5 line), l.1968-1970 |
| W35 | at the score | RESULTS.md: fill in rows l.70-71 (#37/#38 scores and L), plus a one-line exp60 lab note or a pointer to `experiments/exp60_trainlab/results.md` | partial: the #37/#38 rows exist (PENDING) and P36 is filled at l.69; no exp60 line (`grep exp60 RESULTS.md` = 0) | `experiments/RESULTS.md` l.69-71 |
| W54 | right after W47 | Ask the user for the provisional tick (W48) and check that exactly 2 files are ticked. Record it in CONTEXT | not started | `round4/report.json` R4-A5 |
| W22 | with W49; ~09:00 | Intel line. The 22:16 line (#164) is in CONTEXT at 23:12. The **00:47Z line (#155, 6th of 73, silver 41 ranks below) is not** | partial | `round4/report.json` new_facts; `CONTEXT.md` l.1971-1973 |
| W23 | every ~6 h (next ~06:45) until 29 Sep 07:00 | x138 successor watch (E10): a public notebook >= 0.956, or a spike of >= 10 teams at one score >= 0.956. The 00:46-01:05 check found nothing: no notebook has run since 25 Sep 09:09Z, and x138 is still v1 but was renamed "Biohub 0.953 LB \| ORIGINAL" | in progress | `round4/scan_browser.json`; `round4/report.json` new_facts |
| W31 | **by 26 Sep 12:00** | Closures into CONTEXT and the curator. Done at 23:12: swapfix and clip-boundary rescue. **Still open:** (1) the R2S-6 info-only note. (2) The lab calibration rule for node-adding arms (I23). (3) Axis-flip I-151 (base-dependent sign, R9). (4) Tail-bug fixes, retention hysteresis (I29) and density-gated insertion. (5) "x138 tail saturated" with the numbers (I21); it is in `FACTS.md` F-TRN-15 but not in CONTEXT. (6) The M6 lapse note (T12). Merge these with W49 | partial | `CONTEXT.md` l.1974-1975; `round3/report.json` R3-A8 |
| W50 | checklist **today**; the durable reminders **by 28 Sep** | **The 29 Sep FINALS-TICK CHECKLIST goes into CONTEXT.** (1) 28 Sep evening: confirm the refs. (2) 29 Sep 12:00 reminder, backup 18:00. (3) Exactly 2 ticked, matched by ref and date, not by score. (4) Reload, screenshot, log, commit. Never tick #34, #35, P36, or two files with identical components. The reminders must **survive this session** (a cloud routine or the user's calendar) | not started | `round4/report.json` R4-A7 |
| W26 | any time 26 Sep | Day-2 cloud research (`NEXT_RESEARCH.md`, ~$10-12). It is superseded by the night rounds. Record it as "cancelled" in CONTEXT | not started (`grep NEXT_RESEARCH CONTEXT.md` = 0) | `research/wf_ideas_v3/NEXT_RESEARCH.md` |
| W18 | low | The ledger still prints "Forecast F not supplied (--forecast-h)". F = 7.87 h is in CONTEXT at 23:12, so this matters only if a rider dummy appears | partial / low | `ledger.md` A5-F |
| W53 | after 09:30Z, optional | Change the poller to log `error_description`. Only the API exposes it, not the CLI CSV. Deferred: it needs a restart, which is forbidden in the watch window | deferred | `round4/report.json` rejected, R4-A9 |
| W15 | - | GPU quota check: optional. Nothing uses the GPU tonight | optional | `round3/report.json` R3-A6 |
| T12 | **26 Sep 18:00** | The M6 reopen window for K4/tempfuse lapses. Nobody owns it. Note the lapse in CONTEXT (with W31) | pending (expected lapse) | `CONTEXT.md` 20:55 (M6) |
| T17 | 26 Sep, any free slot, **only through the READ TABLE with an OK** | 26 Sep has 3 unused slots. The only allowed contents: K1 = exp58t v1 (rows 1/4/C4), a K2 resubmit (C2a), or an S10-S11 retry of a failed K build. Unused slots are not burned | - | `CONTEXT.md` l.2012-2013; `round4/report.json` R4-A6 (7) |
| T18 | **27 Sep 00:00** | The slot counter resets: 5 slots for 27 Sep. Nothing is planned for them unless K1 or a retry is needed | - | `CONTEXT.md` 13:38 (slot plan S7-S11) |

## LATER (27 Sep 01:20 -> 29 Sep 23:59 UTC)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T02 | 27 Sep ~09:00 | LB snapshot and rank line (compare with #155 at 00:47Z 26 Sep) | `FINAL_REPORT_v4.md` §3 item 8; `round4/report.json` new_facts |
| T03 | **27 Sep 12:00** | **R8: no new mechanisms after this.** In practice the search is already over (`CONTEXT.md` l.2021-2022). After the cutoff only K1 per the READ TABLE and S8 for an x138 successor (E10) remain | `CONTEXT.md` 13:38 R8, l.2023 |
| W33 | (was: code by 27 Sep 12:00) | Floatout on x138 as S12: **recommended CLOSE** (R4-A2 item 3; the user decides). It is not ported to x138, the check is a bare assert, E ~+0.0001, and §e says S12 only consolidates riders that have already scored. **Contradiction:** `CONTEXT.md` l.2022 lists "float output" as CLOSED, but `research/KNOWLEDGE/DECISIONS.md` l.96-98 still says "an OK'd S12 floatout" | `round4/report.json` rejected, plan_issues 4 |
| T04 | **28 Sep 12:00** | S12 consolidation of F1-final, only if accepted riders sit in different files. **Currently moot:** no rider passed, and floatout is recommended closed | `CONTEXT.md` l.1614 (S12); `round4/report.json` R4-A6 (6) |
| T05 | 28 Sep 16:00 | S13: repeat S12 on error (moot if S12 is moot) | `CONTEXT.md` l.1615 |
| T19 | **28 Sep evening** | Confirm the F1/F2 refs (checklist step 1). The durable 29 Sep reminders must exist by now (W50) | `round4/report.json` R4-A7 |
| T06 | 28 Sep 22:00 | Final admission table (W04) | `FINAL_REPORT.md` §d; `TASK_CLOUD_SESSION.md` T13 |
| T20 | **29 Sep 00:00** | The last slot reset (5 slots). After 02:00 only S17 (an emergency repeat of F1-final); hard edge 10:00 | `CONTEXT.md` 13:38 R8, S17 |
| T07 | 28-29 Sep | Risk: queue latency above 10 h. Other teams' reruns take 7-10 h (I26). If it happens, R5(b) decides | `FINAL_REPORT.md` §g item 6 |
| T09 | 29 Sep ~11:30 / **12:00** (backup **18:00**) | Draft the finals-tick check at 11:30 (compare the provisional ticks with the READ TABLE rows). At 12:00, remind the user to CHECK the ticks: they should already be set (W48), so this is a verification, not a first selection. Backup reminder at 18:00 | `round4/report.json` R4-A5, R4-A7; `CONTEXT.md` l.2019-2020 |
| T10 | **29 Sep 20:00** | The USER finishes ticking the finals. Default: F1 = K2 #37 56563521, F2 = twin #38 56563534, provided the twin scored without error, is R5-admissible and is >= 0.953 (f2 OK 22:06). Otherwise follow the READ TABLE (+ CLARIFICATION v2), then exp52 (56534391). #34 is the last resort before exp52. Never tick exp56 while an admissible non-copy x138-family file exists, never tick two files with identical components, never tick P36 or #35, and never auto-select | `CONTEXT.md` l.2017-2020, l.1978-2004; `round4/report.json` R4-A7 |
| T11 | 29 Sep 23:59 | Competition deadline | `CONTEXT.md` §1 |
| W29 | after 29 Sep | E14: friend A's honest out-of-embryo A/B. Inputs: the error anatomy (I06, I21, I22), DeepCenter t* (I19), the clip-boundary deficit (I28) and the lab calibration (I23, I35) | `TASK_FRIEND_A.md` "Задача 4" |

**Done or cancelled since 23:05 (for the record):**
- W16 done: #37 was submitted at 00:02:12Z (ref 56563521) and #38 at 00:02:18Z (ref 56563534), with the right families (`CONTEXT.md` l.2007-2010; `ledger.md` 01:03Z).
- W39 done: the READ TABLE is in `CONTEXT.md` 23:12 (l.1978-2004). Commit 1017c41 was pushed at 23:13:16Z, before any score (`round4/report.json` new_facts).
- W40 done: RESUME POINT 26 Sep 00:02 (`CONTEXT.md` l.2006). The 10:20 finals line is declared SUPERSEDED at l.1976-1977. Residual (low): §10 at l.109 still has no "STALE (6 Sep)" marker.
- W36 done: `lb_poll.py` l.28 now keeps `[:60]` (1017c41). The poller restarted at 23:12:45Z (`round4/report.json` new_facts).
- W37 done: the workflow prompt was updated (`biohub-research-round.js` l.34, 1017c41), and the S4-S6-empty line is in `CONTEXT.md` 23:12 (l.1967-1970).
- W06 done: hidden reruns do not use the GPU quota (`CONTEXT.md` l.1971-1972).
- W41 (a)-(c) done (`CONTEXT.md` l.1970-1972). (d) moved to W47.
- W14 done: P36 = 0.954, L36 in (7.24, 7.42] h (`CONTEXT.md` l.2010-2011; `RESULTS.md` l.69).
- W25 resolved (`CONTEXT.md` l.2012).
- W07 cancelled: forkmid is CLOSED (`CONTEXT.md` l.2021).
- W28 closed by round 4: head-shift s_opt is 0.75-1.0 and the T12 gate fails (`round4/report.json` R4-A6 (3)). It still has to be recorded (W49).
- W20 is superseded by W47, and W21 by W45.
- Earlier: W01, W08, W09, W11, W12, W17 and W30 done; W13, W24, W27 and T01 cancelled (`research/KNOWLEDGE/_curation/3/watch.json`).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| I31 | **"Submissions page at 00:57Z: 0/2 finals selected ... 'If less than 2 are selected, Kaggle will automatically select from your best scoring submissions' (today that would be P36 and #35)"** | `research/wf_ideas_v4/round4/report.json` new_facts, R4-A5 (untracked) | Nobody watches the default auto-selection. P36 is "never a final", and #35's R5 is UNPROVEN (`ledger.md`). A missed tick on 29 Sep fails silently. Hence W48 |
| I32 | "Our LB row shows only the best entry ... in-block order follows the unrounded score, so P36's unrounded public score is above #35's" | `round4/report.json` new_facts; `round4/scan_browser.json` summary | The rank will not move if K2 or the twin score 0.954 below P36. Read K2/twin only from the displayed scores in poll.log. The rank is never an input (R7) |
| I33 | "The Kaggle API exposes error_description; the CLI CSV does not" | `round4/report.json` new_facts, plan_issues C2 | Row 1 of the READ TABLE needs the error class (C2). The poller cannot see it, so the one-liner is required |
| I34 | "The 44b6 '+0.0157' is one TP (SELECTION 0.0000) ... insertion +0.00648 pooled, from 9 clips with +1 TP and 6 with +1 FP ... the dense half has 2 TP / 4 FP, so a dense private embryo could give K2 ~= twin" | `round4/report.json` new_facts | `CONTEXT.md` l.1932 still quotes "+0.0157 / +0.0090" as the insertion lab result. The real evidence is thin (I02, I24), and that is the case for keeping the twin as F2 |
| I35 | "Leaf-prune replay on exp60: lp30 +0.00083 (51/56 clips win; 95% of pruned nodes were readmitted) ... agrees with P36 delta 0 ... the first x138-base, LB-anchored point for a node-removing rule (no lab bias)" | `round4/report.json` new_facts, R4-A6 (5) | This is the counterpart of I23 (node-ADDING arms read positive in the lab but -0.002 on the LB). It is not in CONTEXT or KNOWLEDGE (`grep lp30` = 0). Needed for any post-29 Sep lab calibration |
| I36 | "R4H-2's '08:00:30-08:01:30 keeps the +210 s slack inside the mark' is wrong: a poll with one failed attempt proves clean only if its header <= 07:58:42Z" | `round4/report.notes.md` 01:02Z; `round4/report.json` rejected | A poll timed naively could "prove" clean with a bound past 08:02:12Z. Use W46's timings |
| I37 | "y3uanm's 0.956 route has no public weights, so C10 cannot fire (R9). x138 was renamed 'Biohub 0.953 LB \| ORIGINAL' (still Version 1)" | `round4/report.json` new_facts | The E10 successor watch (W23) must track x138 by its slug or author, not by the old title. C10 can be dropped from the watch |
| I38 | "Lowrefine adds +12 same-frame pairs under 3 um (29 -> 41) in 121,252 nodes, none near GT, effect ~1e-5 ... head-shift s_opt 0.75-1.0 on both embryos; s > 1 trips the 2 um refine guard" | `round4/report.json` new_facts, R4-A6 (3)-(4) | Closes two recurring ideas (refined-duplicate collapse, head-shift scale). Without a CONTEXT line (W49) later rounds will propose them again |
| I01 | "Of x138's forks, 24% (15/62 on the dummies) are one-blob duplicates at t+1, against 2% of GT divisions" | `research/wf_ideas_v4/lens_literature.json` plan_critique 1-2 | The main fact for division work after 29 Sep. Forkblob, ANTIPAR and forkmid all failed to exploit it |
| I02 | "1 of 10 lab gains transferred ... a lab-based slot decision is allowed only for arms whose learned inputs are out-of-sample" | `research/wf_ideas_v4/lens_mine-old.json` plan_critique (4) | Recorded neither in CONTEXT nor in KNOWLEDGE (`grep "1 of 10"` = 0) |
| I04 | "DeepCenter score recorder and the TRAINLAB summary cell are not fail-soft ... 7 of 17 44b6 picks are leak-siblings" | `CONTEXT.md` 14:29 (T5) | 44b6 lab deltas are partly in-sample |
| I05 | "K2 forecast <= 7.86 h ... the insertion gate at 8.0 h is only +0.14 h above that" (refined to 7.87 h) | `lens_headroom.json` critique (2); `CONTEXT.md` l.1970 | This is why "clean" is not guaranteed and why W46 exists |
| I06 | K2 dummy vs train GT: "FN 82 of 2,127 GT edges. 50% are swaps, 23% one-free-end fragments, 6% end-anchored node misses" | `lens_mine-old.json` critique (3) | Not in CONTEXT or KNOWLEDGE. It conflicts with I21/I22, where the "swaps" are really node misses. Reconcile the two before any work after 29 Sep |
| I07 | "lowrefine is not a coordinate-only rider ... +33 final nodes, +29 edges and +1 fork" | `lens_redteam-plan.json` RT2 | This is why the READ TABLE needs d2 |
| I08 | Kernel time is not a hidden-test budget signal; use the per-dataset `[ds] repair` lines | `research/wf_ideas_v3/FINAL_REPORT.md` §j item 19 | Start-up noise is 818-1179 s |
| I09 | "Блок 0.953 на private останется единым" is untested | `FINAL_REPORT.md` §g item 13 | For the 4th window in a row, late x138 copies land at the END of the 0.953 block (16 more at 00:47Z; `round4/report.json` new_facts). This backs "never tick a verbatim copy" (T10) |
| I12 / I18 | The silver line (~196) sits INSIDE the 0.954 block. The margin went 38 -> 32 -> **41** ranks (19:46 / 22:16 / 00:47); the last gain came only from P36 | `round2/`, `round3/`, `round4/report.json` new_facts | Rank moves are dominated by other teams and by our best-entry display (I32). A slide below silver is possible within a day without any change on our side |
| I14 | Stale operational text: `TASK_LOCAL_SESSION.md` l.12 and `TASK_FRIEND_A.md` l.40, l.52 name branch `claude/practical-meitner-31k9ye`, but the work lands on `main` | those files | Same risk as W03 |
| I15 | "The public read over-rewards fork REMOVALS whose precision lies between the private break-even (0.11-0.20) and 0.265" | `round2/report.json` plan_issues (R2-RC-B); `CONTEXT.md` l.1644 (PRE-REG table only) | Any future removal rule needs a private break-even clause |
| I17 | "FLOATOUT_CHECK (build_probe_kernel.py l.1315-1362) is a bare-assert cell, not fail-soft" | `round2/report.json` new_facts (12) | Moot if floatout is closed (W33); otherwise it breaks R7 |
| I19 | **DeepCenter t* = 0.30 is the lab optimum** in the removal direction (6bba div 15/11/73 vs control 15/17/73; 8 evaluable FP removed, 0 TP lost). It is NOT node-preserving (nodes -79/-49) | `experiments/exp60_trainlab/results.md` l.13-18, l.61-66 | CONTEXT l.1930 gives only the failed gates. Keep it for after 29 Sep |
| I21 | "The x138 tail is saturated. Edge FN 1,705 of 40,093 = node misses 834 (49%), swaps 730 (43%), dangling ends 141 (8%) ... the remaining error mass needs retraining" | `round3/report.json` new_facts (13); `research/KNOWLEDGE/FACTS.md` F-TRN-15 | It is in KNOWLEDGE but NOT in CONTEXT (W31 (5)), and it is the reason to stop mining post-processing |
| I22 | "There are 0 true 2x2 swaps ... our nodes sit 3.9-4.2 um from the GT nuclei ... 6bba holds 485 of the 555" | `round3/report.json` new_facts (14); `CONTEXT.md` l.1974 (short form) | "Swaps" are a detection/localization problem |
| I23 | "The CONFIRMATION half reads every node-adding arm as positive (L4 +0.00099, L5 +0.00041, rescue +0.00109), while the LB read MIN_TRACK_LEN 4 at -0.002" | `round3/report.json` R3-A8 (3), new_facts (16) | The lab calibration rule is not in CONTEXT (W31 (2)). Pair it with I35 |
| I24 | "Evaluable precision: sparse half 8 TP / 3 FP, dense half 1 TP / 3 FP ... private harm needs out-of-fold evaluable precision < ~11% (q* = 0.114)" | `round3/report.json` new_facts (11); `FACTS.md` | The quantitative case for the twin hedge (see I34) |
| I26 | "hidden-rerun latency is 7-10 h with no queue problem" (other teams) | `round3/report.json` new_facts (2); `CONTEXT.md` l.1526 | Makes "not clean" (READ TABLE row 5) a live branch |
| I28 | "GT node recall before safe divisions -> final: t0 0.959 -> 0.940 ... boundary edge TP rate 0.926 vs 0.958" | `round3/report.json` new_facts (15) | The clip-boundary node loss (~2 pp) is real and deferred until after 29 Sep |
| I29 | The retention guard has no flicker penalty: switch pairs 6.05% FN, between blended 3.17% and primary 10.71% | `round3/report.json` new_facts (17); `FACTS.md` F-TRN-18 | Closes hysteresis for good. Not in CONTEXT (W31 (4)) |

Resolved since 23:05:
- **I03**: the GPU quota point is in CONTEXT at l.1971.
- **I11**: the R5(b) margin of 1.63 h is in CONTEXT at l.1970.
- **I25**: the poller window is now 60 lines (1017c41).
- **I27**: the probe.json boilerplate is named in the READ TABLE at l.1982-1983.
- **I30**: the stale 10:20 finals line is marked SUPERSEDED at l.1976-1977, and the 00:02 RESUME POINT replaces it.
- **I16, I20, I10, I13**: resolved earlier.
