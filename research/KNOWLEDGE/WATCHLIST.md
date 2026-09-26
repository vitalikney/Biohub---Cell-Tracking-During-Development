# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-26 06:25 UTC (curation 6). This is an incremental update of the curation-5 build from 03:58 UTC.

Sources:
- `CONTEXT.md` §14 up to the 04:12 UTC entry (l.2033-2057). Git HEAD is 2f6ec9d, equal to origin/main. The last commits were fc51b75 (04:04:45Z), 801de5a (04:11:11Z) and 2f6ec9d (04:12:15Z), per `git log` at 06:25Z.
- `experiments/lb_poll/ledger.md` (06:14:02Z) and `poll.log` (last header 06:14:00Z, l.3251).
- `experiments/RESULTS.md` l.69-71.
- `research/wf_ideas_v4/round6/report.json` (written 06:17:22Z) and `report.notes.md`. Both are **untracked**, and there is no REPORT.md.
- `research/wf_ideas_v4/round5/` is now committed with REPORT.md (fc51b75).
- `research/wf_ideas_v3/FINAL_REPORT.md`, `TASK_LOCAL_SESSION.md`, `TASK_CLOUD_SESSION.md`, `TASK_FRIEND_A.md` and `NEXT_RESEARCH.md`; `PROMPT_FRIEND_A.md`.
- The memory files (`MEMORY.md` and `project-lb-probe-approval.md`, both unchanged since 23:13Z on 25 Sep).
- `tasklist` at 06:19Z: python PID 20052 (the poller) and PID 13436 (`_dl/clean_proof_polls.py`, per `round6/report.json` new_facts 4).

All times are UTC. The IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, cancelled.

**State in one line.**
- #37 = K2 (`exp58` v1, ref 56563521, 00:02:12Z) and #38 = twin (`exp58n` v1, ref 56563534, 00:02:18Z) were both still PENDING at 06:14:00Z, with L > 6.19 h (`ledger.md`).
- The twin can score from about 06:15-06:30Z, and K2 from about 07:00-09:30Z (`round6/report.json` R6-A1 deadline, R6-A3; `round5/report.json` new_facts 5).
- The finals default is still the pair {K2 #37, twin #38}. Scores are read ONLY through the READ TABLE (`CONTEXT.md` l.1978-2005) with CLARIFICATION v2 (l.2026-2032) and v3 (l.2039-2046), plus v4 once it is committed (W62).
- **Kaggle still shows 0/2 finals ticked** (`round6/report.json` R6-A2 why).
- The OK REQUEST was posted at 04:04Z (`CONTEXT.md` l.2049-2051). **No user reply is recorded yet** (`round6/report.notes.md` 06:11Z).
- LB at 05:46Z: #162 of 3,922 at 0.954, 34 ranks above silver (`round6/report.json` new_facts 1).

**Changes since 03:58:**
- Done in fc51b75 (04:04:45Z, before any score):
  - W56: CLARIFICATION v3 (`CONTEXT.md` l.2039-2046).
  - W45: the OK request was posted (l.2049-2051). Logging the user's reply is now W61.
  - W57: the round-5 records are listed (l.2047-2048). Two edits in it are still open.
  - W60 for round 5: REPORT.md is committed.
- W58 done: builder change 801de5a and merge 2f6ec9d (l.2052-2057; 116 tests pass).
- W55 running: the job started at 04:04Z (l.2046 V7), and PID 13436 was alive at 06:19Z.
- W10 done: round 6 ran as a pre-score round at 06:17Z.
- New from round 6 (R6-A1..A8): W62-W66. W67 is round 7. W59 absorbs R6-A7, W60 absorbs R6-A8, and W47 now uses the cheat sheet. New reminders T24-T27; new insights I47-I55.
- Resolved insights: I36, I40, I41, I42, I43 and I45 (now in `CONTEXT.md` l.2039-2048, l.2052).

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| W62 | **READ TABLE CLARIFICATION v4 goes into CONTEXT, committed and PUSHED.** Take it verbatim from the `v4_text` field of `round6/report.json` and fill in `<hh:mm>`. It holds:<br>- W1: one OK-timing reference T0 = the last poll.log header with both files PENDING. An OK given later is logged as "USER DECISION AFTER SCORE".<br>- W2-W8: the table gaps.<br>- The precedence v4 > v3 > v2 > table > f2 > §f.<br>- V4b: B' next to B.<br>- The R5 line: basis F' = 8.27 h.<br>- V3b: the 6-check K2'' gate.<br>Right before the commit, grep poll.log for a COMPLETE or ERROR line of 56563521 or 56563534. If one exists, label the entry "post-hoc NOTES (written after <header>)". Save round 6's REPORT.md in the same commit (W60). Commit as the user, with no Co-Authored-By trailer. Do not touch PIDs 20052 or 13436 | **not started** (`grep -c "CLARIFICATION v4" CONTEXT.md` = 0 at 06:25Z; HEAD 2f6ec9d) | **NOW: before the ~06:24Z poll, at the latest ~06:34Z** | `round6/report.json` R6-A1, plan_issues 1-6, `v4_text` |
| W63 | **Morning brief to the user, in Russian, sent ONCE in the chat and as a PushNotification** (`morning_brief_ru`, R6H-6 with fixes a-d). First refresh its status line from poll.log/ledger.md. Do NOT re-post the 04:04Z OK list. The brief includes the W50 reminder ask (point 4). If the user has already replied, drop point 1 and log the reply time (W61) | not started | right after W62, before the first #37/#38 result if possible | `round6/report.json` R6-A2, R6-A5 |
| W61 | **Log the user's OK reply time against T0** (the v4 W1 gate). An OK after T0 counts only for event items: the C2(a) resubmit, the row-1/C2(c) K1, a twin Kaggle Error, and K2'' after the trigger. Score-reading items (the 0.952 floor, row 2 with F2 = K2, and K1 in rows 4/C4) are then logged as USER DECISION AFTER SCORE | **awaiting the user** (no reply in CONTEXT after l.2051) | when the reply arrives (`date -u`) | `round6/report.json` plan_issues 1, next_focus (1); `CONTEXT.md` l.2049-2051 |
| W60 | **Round reports.** Save `report_md_ru` from `round6/report.json` verbatim as `round6/REPORT.md` and commit it with W62 (R6-A8). `round2/REPORT.md` is still missing (only report.json and notes are tracked); low priority | partial (rounds 3-5 done) | with the W62 commit | `git ls-files research/wf_ideas_v4` 06:22Z; `round6/report.json` report_md_ru_note |
| W02 | Friend A "Task 0" reply: availability 26-28 Sep, the 5070 Ti, sasyami GPU hours | overdue, and in practice moot: no lab or rider work remains | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22 |
| W03 | **The friend A card is stale.** The top block of `PROMPT_FRIEND_A.md` is still the 25 Sep ~14:30 one, which points to cancelled tasks. Add a "cancelled / nothing to do before 29 Sep" block, as was done for friend C (14c339e) | overdue (last change 25 Sep 13:41Z per `git log -- PROMPT_FRIEND_A.md`) | now (not urgent) | `PROMPT_FRIEND_A.md` l.1-3 |
| W04 | Admission table in CONTEXT, updated after each score. Columns: file, public, latency, R5, riders, F1/F2 candidate | overdue (`grep -ci admission CONTEXT.md` = 0) | after each score; final version 28 Sep 22:00 | `TASK_CLOUD_SESSION.md` T13; `FINAL_REPORT.md` §d |
| W05 | Commit `experiments/ext_corwin-biocel-aux/` and `experiments/ext_y3uanm-secondary-ft/` without `__pycache__` | overdue (still `??` in `git status` at 06:20Z) | 25 Sep | `git status` |
| W34 | Memory pointers, residual:<br>- `MEMORY.md` l.8 still says "gated riders K3/K3b/K4/N1" (all closed).<br>- `project-lb-probe-approval.md` l.14 says "K2 ... ~00:55 UTC", but K2 went in at 00:02:12Z.<br>- Refs 56563521 and 56563534 and the 04:04Z OK request are missing.<br>- `MEMORY.md` l.9 does not say that v3 and v4 exist | mostly done | low; at the next memory touch | memory files (mtime 23:13Z 25 Sep) |

## NEXT 24 H (26 Sep 06:25 -> 27 Sep 06:25 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W62 / W63 | **now -> ~06:34** | See OVERDUE | not started | `round6/report.json` next_focus |
| W19 / W52 | **now -> both terminal**, and at least to the first poll after 09:32:18Z | Keep the Claude session that owns the poller (PID 20052) open, and keep the machine on AC power. **Stop rule:** stop the poller only once poll.log shows COMPLETE or ERROR for both 56563521 and 56563534. If a K2'' or K2 resubmit is made, keep it running until submit + that file's deadline (v4 W6). Before each submit, check that the newest poll is < 15 min old | in progress (0 gaps > 15 min, per `ledger.md` Poll health) | `CONTEXT.md` l.2046 (V7); `round6/report.json` plan_issues 6 |
| W55 | job already running; one-shots at **07:57:30 / 08:00:45 / 08:01:45Z** | Clean-proof background job, PID 13436. **Do not touch it.** After 08:02:12Z run `python tools/runtime_ledger.py --print`, once after the 08:01:45Z one-shot and again after the ~08:04Z poll | in progress (started 04:04Z) | `CONTEXT.md` l.2046; `round6/report.json` new_facts 4, cheat_sheet |
| T13 | ~06:15-07:40 | The twin (#38) may score. **Do not act on the twin alone.** Rows 2-5 are read only when both files are terminal. Row 1 (K2 ERROR) may be read on K2 alone. If the twin alone gets a Kaggle Error, that is an event question (default F2 = exp52), per v4 W7 | watch | `CONTEXT.md` l.2027 (C1); `round6/report.json` plan_issues 2 |
| W64 | **at the first #37/#38 result** | Commit poll.log + ledger.md in the same step, as git evidence of the timing. Then check that the v4 commit time is before the first result header, or else v4 stands as post-hoc NOTES | not started | `round6/report.json` R6-A3, cheat_sheet (last lines) |
| T21 | ~07:00-09:30 | K2 (#37) is expected. Forecast F = 7.87 h gives a finish around 07:54Z. P(not clean) is ~0.3-0.5 (a guess) | watch | `round6/report.json` R6-A3, new_facts 9; `round5/report.json` new_facts 5 |
| T24 | **07:45-08:05** | **Poll hygiene.** Only the poller (PID 20052) and `_dl/clean_proof_polls.py` (PID 13436) poll in this window. **Never run `_dl/oneshot_poll.py`**, which stamps before the call. No builds, pushes or ledger code edits during 07:45-08:35Z | watch | `round6/report.json` cheat_sheet, rejected 1; R6-A7 |
| T14 | **08:02:12Z** | The 8.0 h "clean" mark for K2. The poller's headers drift about +2 s per cycle, landing near 07:54:2x and 08:04:2x, clear of the one-shots. For the CLEAN read, accept only a poller header with no failed-attempt note, or a "[manual one-shot, stamped after call]" header stamped before 08:02:12Z | watch | `ledger.md` A5-L(K2); `round6/report.json` new_facts 4, cheat_sheet |
| W47 | when both are terminal (~07:50-09:40) | **Mechanical score read, using the round-6 cheat sheet** (R6H-3 with fixes a-e):<br>1. Compute k, w, d1 and d2, and read error classes via C2.<br>2. Compute "clean".<br>3. Report L(K2), L(twin), B, and **B'** = min(L(K2)_hi, L(K2)_hi - L(twin)_lo + 7.31 h, L(twin)_hi + 2.66 h).<br>4. Write the R5 line (basis F' = 8.27 h). If a file's own L_hi > 9.5 h, R5 is UNPROVEN for it: ask the user.<br>5. Record the OK time against T0.<br>6. Give the user the pair to tick, with refs.<br>7. If the trigger fires (L(K2)_hi > 8.0 h or unproven, and the pair contains K2), raise K2'' in every row:<br>- B <= 8.0: not needed.<br>- 8.0 < B <= 9.0: optional; ask.<br>- B > 9.0: act under OK item 5 if it was given.<br>- B <= 9.0 < B': ask with both numbers.<br>Scores come from poll.log only | pending | `round6/report.json` R6-A3, cheat_sheet, `v4_text`; `CONTEXT.md` l.1978-2005, l.2026-2046 |
| T15 | **08:32:12Z** | The ledger's K2-only watch window ends. This is a minimum only, and W19 governs the stop | - | `ledger.md` A5-L(K2); `round6/report.json` plan_issues 6 |
| T16 | **09:32:12Z** (K2) / 09:32:18Z (twin) | The 9.5 h R5(a) mark | watch | `CONTEXT.md` l.1968-1970; v4 R5 line |
| W54 | right after W47 (~09:30-10:00) | **Provisional tick.** The user ticks EXACTLY two files (default #37 56563521 + #38 56563534, or the cheat-sheet pair). Check that 2/2 are ticked and record it in CONTEXT. Never leave 0/2 or 1/2: auto-selection would pick P36 and #35 | not started | `CONTEXT.md` l.2034-2036; `round6/report.json` R6-A2 why |
| W65 | only if the trigger fires **AND the user says yes**; submit on 26 Sep (3 slots), at the latest **27 Sep 12:00** (R8) | **K2'' = exp58d.** Build with the 04:12Z command (`CONTEXT.md` l.2055-2057) and run its dummy. Then apply the **V3b gate**, all 6 checks:<br>1. The dummy CSV sha256 equals the K2 dummy's.<br>2. The log has "SAFETAIL: repair deadline 37800s, divins deadline 32400s".<br>3. probe.json values match, and the notebook diff is 2 lines plus the name comment.<br>4. `tools/dummy_gates.py --k2 <dir>` passes.<br>5. It has its OWN slug, `biohub-exp58d-x138-safe-lowref` v1, never v2 of the K2 slug.<br>6. The message's first exp token is `exp58d`.<br>No build or submit work during 07:45-08:35Z | conditional; not started | `round6/report.json` R6-A4 (`covered_by_existing_approval: false`); `CONTEXT.md` l.2042, l.2052-2057 |
| W35 | at the score | RESULTS.md: fill rows l.70-71 (#37/#38 scores and L), plus a one-line exp60 note or a pointer to `experiments/exp60_trainlab/results.md` | partial (`grep -c exp60 experiments/RESULTS.md` = 0) | `experiments/RESULTS.md` l.69-71 |
| W67 | **after both are terminal (~09:40Z)**; skip any other pre-score round | **Round 7:**<br>1. Check the v4 commit time and the OK time against T0.<br>2. Do the mechanical read (W47).<br>3. Remind the user about the pair and the 2/2 tick.<br>4. K2'' decision support, only if the trigger fired (the build/dummy/slot plan for 26-27 Sep, the V3b gate, 10.5 h poller coverage).<br>5. Check W59 and the curator handoff.<br>6. A short browser delta (info only, R7) | not started | `round6/report.json` next_focus |
| W57 | curator by **26 Sep 12:00** | Round-5 records. The list is in CONTEXT (l.2047-2048), and the KNOWLEDGE facts are partly in (`FACTS.md` has post-freeze and R5H-1). Still open:<br>- (3): fix `CONTEXT.md` l.22, which still says "GT still moving" (I39).<br>- (5): add the new AdaBN blocker to B5 at l.196, which still lists only the old reasons (I44) | partial | `CONTEXT.md` l.22, l.196, l.2048 |
| W66 | next CONTEXT write; curator by **26 Sep 12:00** (lessons after 29 Sep) | **Round-6 records** (R6-A6):<br>1. The intel line for 05:46-05:48Z.<br>2. FACT: the official edge FP rule (I47).<br>3. Stitch recheck CLOSED (I52).<br>4. Linefit I-184 CLOSED as "no detectable effect" (I52).<br>5. efpost as a FACT, NEUTRAL wording only (I51).<br>6. The x138 prediction spread of 15.4% and the dummy insertion cost of 9.6-181.9 s per clip (I48).<br>7. The W57 and W31 records.<br>8. The R6H-7 lessons for §11 after 29 Sep (I53) | not started (`grep -c efpost research/KNOWLEDGE/FACTS.md` = 0; `grep -c "out_valid" CONTEXT.md` = 0) | `round6/report.json` R6-A6 |
| W31 | **by 26 Sep 12:00** | Curation-3 closures still not in CONTEXT:<br>1. R2S-6 info-only.<br>2. The lab calibration rule for node-adding arms (I23).<br>3. Axis-flip I-151 (`grep -c I-151 CONTEXT.md` = 0).<br>4. Tail-bug fixes and retention hysteresis (`grep -c hysteresis CONTEXT.md` = 0).<br>5. "x138 tail saturated" with its numbers (I21).<br>6. The M6 lapse note (T12).<br>Merge these with W66 | partial | `round3/report.json` R3-A8; `DECISIONS.md` has I-151 and hysteresis |
| W50 | ask **today** (in W63); reminders in place **by 28 Sep** | Durable 29 Sep 12:00 and 18:00 reminders that survive this session: in the user's own calendar, or a cloud routine only with a new OK. This is the only open item from the round-6 readiness check | not started (no evidence) | `CONTEXT.md` l.2037; `round6/report.json` R6-A5, plan_issues 8 |
| W23 | every ~6 h (next ~11:45) until 29 Sep 07:00 | x138 successor watch (E10). The 05:46Z check found nothing: x138 is still v1 (192 votes, 269 copies), and no public notebook scores >= 0.954. New dataset `koushikrudra/biohub-zerogpu-consensus-v1` holds a cached CSV and cannot score. Track x138 by slug or author | in progress | `round6/report.json` new_facts 5 |
| W59 | **after ~09:40Z**, never inside 07:45-08:35Z | Text fixes in `tools/runtime_ledger.py`:<br>- A6: "read the error class per C2".<br>- The A5 ask offers K2'' only.<br>- Default F = 7.87 h.<br>- **Plus R6-A7:** replace the K2-only "Keep the poller alive until ..." line (K2_WATCH_H) with a generic "keep until submit + deadline_h" line for every PENDING safetail, safetail_noins or safetail_late entry.<br>Add a test and run pytest. No poller restart is needed | not started | `round6/report.json` R6-A7; `round5/report.json` R5-A7 |
| W26 | any time 26 Sep | Record in CONTEXT that day-2 cloud research (`NEXT_RESEARCH.md`) is cancelled | not started (`grep -c NEXT_RESEARCH CONTEXT.md` = 0) | `research/wf_ideas_v3/NEXT_RESEARCH.md` |
| W53 | after both are terminal, optional | Poller logs `error_description`. Deferred: needs a restart | deferred | `round4/report.json` R4-A9 |
| T12 | **26 Sep 18:00** | The M6 reopen window for K4/tempfuse lapses. Round 6 also refused K4 = K2 + efpost (I51). Note the lapse with W31 | pending (expected lapse) | `CONTEXT.md` 20:55 (M6); `round6/report.json` rejected 3 |
| T17 | 26 Sep, any free slot, **only through the table, with an OK or event item** | 26 Sep has 3 unused slots. Allowed: K1 = exp58t v1, a K2 resubmit (C2a), K2'' = exp58d (W65), or an S10-S11 retry | - | `CONTEXT.md` l.2033 (7), l.2042 |
| T18 | **27 Sep 00:00** | Slot reset: 5 slots for 27 Sep. K2'' may still go in before 12:00 | - | `CONTEXT.md` 13:38 (S7-S11) |

## LATER (27 Sep 06:25 -> 29 Sep 23:59 UTC)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T02 | 27 Sep ~09:00 | LB snapshot and rank line. Compare with #162 at 05:46Z on 26 Sep, 34 ranks above silver | `round6/report.json` new_facts 1 |
| T03 | **27 Sep 12:00** | **R8: no new mechanisms after this, and the last time for a K2'' submit.** After it, only K1 per the table and S8 (an x138 successor) remain | `CONTEXT.md` 13:38 R8; `round6/report.json` R6-A4 deadline |
| T25 | K2'' submit + 10.5 h | If K2'' is submitted, keep the poller up to its 10.5 h deadline (`safetail_late` family) and read it per V3: it replaces K2 iff it scores without error, L_hi <= 10.5 h, and public >= K2 - 0.001 | `CONTEXT.md` l.2042, l.2052-2054; `round6/report.json` plan_issues 6 |
| T04 | 28 Sep 12:00 | S12 consolidation. **Moot:** no rider passed | `CONTEXT.md` l.1614, l.2033 (6) |
| T05 | 28 Sep 16:00 | S13 (moot) | `CONTEXT.md` l.1615 |
| T19 | **28 Sep evening** | Confirm the F1/F2 refs (checklist step 1). The durable reminders (W50) must exist by now | `CONTEXT.md` l.2037 |
| T06 | 28 Sep 22:00 | Final admission table (W04) | `FINAL_REPORT.md` §d |
| T20 | **29 Sep 00:00** | Last slot reset. After 02:00 only S17; hard edge 10:00 | `CONTEXT.md` 13:38 R8, S17 |
| T07 | 28-29 Sep | Risk: queue latency above 10 h. R5(b) decides | `FINAL_REPORT.md` §g item 6 |
| T09 | 29 Sep ~11:30 / **12:00** (backup **18:00**) | 11:30: draft the tick check. 12:00: remind the user to CHECK the ticks, which should already be set by W54. 18:00: backup reminder | `CONTEXT.md` l.2036-2037 |
| T10 | **29 Sep 20:00** | The USER finishes ticking: exactly 2 files, matched by ref and date. Default {#37 56563521, #38 56563534}; otherwise the table plus v2, v3 and v4.<br>- Never tick #35 or P36.<br>- Tick #34 56545267 only when no eligible non-copy x138-family file exists, as the pair {#34, exp52 56534391} (V2).<br>- Never tick K2 together with K2'', nor two files with identical components.<br>- Never auto-select | `CONTEXT.md` l.2036-2041 |
| T11 | 29 Sep 23:59 | Competition deadline | `CONTEXT.md` §1 |
| W29 | after 29 Sep | E14: friend A's honest out-of-embryo A/B. Also post-deadline linker item #1, the post-freeze re-solve with a geometric/flow cost only, together with efpost (I39, I51), and the lessons (I53) | `TASK_FRIEND_A.md` "Задача 4"; `CONTEXT.md` l.2048 (3) |

**Done or cancelled since 03:58 (for the record):**
- W56 done: CLARIFICATION v3 is at `CONTEXT.md` l.2039-2046. It was committed in fc51b75 at 04:04:45Z, before any score (poll.log 04:04Z, both PENDING, l.2051).
- W45 done (posted): `CONTEXT.md` l.2049-2051. The reply is now tracked as W61.
- W58 done: 801de5a and 2f6ec9d (`CONTEXT.md` l.2052-2057). The builder accepts exactly (34200, 28800) or (37800, 32400), the `safetail_late` family has a 10.5 h deadline, the K2 sha is unchanged, and 116 tests pass.
- W55 is running (PID 13436). The contradictions from curation 5 are resolved by v3: #34 is handled by V1/V2, and the row-5 runtime read by V4.
- W10 done: round 6 (`round6/report.json`, 06:17:22Z).
- W60 done for round 5 (REPORT.md tracked in fc51b75).
- Earlier: W44, W48, W49, W33, W22, W28 (curation 5); W06, W14, W16, W36-W41 (curation 4); W01, W08, W09, W11, W12, W17, W30. W46 was superseded by W55, and W18 absorbed into W59. W07, W13, W24, W27 and T01 were cancelled (`research/KNOWLEDGE/_curation/5/watch.json`).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| I47 | **"Official edge FP rule (metrics.py l.157-195): a predicted edge is scoreable iff its source matches a GT node with out-degree > 0 OR its target matches a GT node with in-degree > 0; a 'both ends matched' shortcut undercounts FP ~20x"** | `round6/report.json` new_facts 8; code at `tools/official/src/tracking_cellmot/metrics.py` l.165-194 (`pred_valid = out_valid \| in_valid`) | Any hand-rolled lab matcher that uses "both ends matched" overstates the precision of edge-adding rules by about 20x. Today it is in no CONTEXT line and no KNOWLEDGE file (`grep out_valid` = 0). W66 (2) |
| I48 | "B is anti-conservative by ~0.7 h: GPU prediction spread 15.4% (~0.58 h), setup 0.13 h, lowrefine 0.14 h, insertion term is a mean ... dummy insertion cost per clip 36.2/62.7/9.6/181.9 s (72.5 s is a mean, not a max)" | `round6/report.json` plan_issues 3, new_facts 6; `report.notes.md` 06:12Z | V4 (`CONTEXT.md` l.2043) uses B alone. Unless v4 (W62) lands, a K2'' decision made at B <= 9.0 < B' would be made without asking the user |
| I49 | "The 23:12 'R5(b) admits K2 and the twin unless they ERROR' (F = 7.87 h) fails R5(b)'s 1 h margin once run variance is added to L35_hi (8.58 h) ... F' = 8.27 h (margin 1.23 h, passes)" | `round6/report.json` plan_issues 4 | The admission sentence in CONTEXT is technically wrong until v4 lands. The expected case is unchanged, but a file with its own L_hi > 9.5 h becomes UNPROVEN, and then the user must be asked |
| I50 | "The most likely user decision today is K2'' (P(not clean) ~0.3-0.5, a guess ...), not K1 (P ~0.05-0.08)"; "pushing K2'' as v2 of the K2 slug would make the C2(a) resubmit ambiguous"; "The V3 sha gate alone cannot detect a K2 rebuilt by mistake (no deadline fires on 4 dummy clips)" | `round6/report.json` new_facts 9, R6-A4 why | Prepare the W65 path, not K1. Its own slug and the SAFETAIL log check are needed. The V3 text in CONTEXT (l.2042) has only the sha gate |
| I51 | "efpost (drop relinked edges with edge_prob == 0 and non-fork source only on the transition after a raw frozen frame) - 6bba +0.00174 (both halves positive), 44b6 exactly 0 (no freezes), 32 TP / 107 FP evaluable dropped; kept as a FACT only"; K4 = K2 + efpost refuted; "do NOT reword I-161/I-162/memory to 'public embryo has no frozen frames'" | `round6/report.json` new_facts 7, rejected 3, R6-A6 (5) | This is a post-deadline linker item paired with post-freeze (I39). The warning against overclaiming exists only in round 6 (`grep efpost research/KNOWLEDGE/*.md` = 0) |
| I52 | "stitch (end->start re-add) - 11 of 1,705 FN have both ends free ... precision 0.20 vs break-even ~0.48, ceiling ~+0.0003 -> CLOSED"; "Linefit w0.7 win2 - 44b6 ALL -0.0031 ... 6bba +0.0001 -> null effect, rider closed"; wording "'no detectable effect', not 'premise refuted'" | `round6/report.json` new_facts 7, rejected 9-10 | Two more closed lines on x138. Without W66 they will be re-proposed |
| I53 | Lessons (R6H-7): "gains came from detection/localisation (insertion +0.001 twice, head +0.002), not the linker tail; in-sample ILP/edge-net trust and lab gains < ~+0.003 did not transfer; LB agreed with 5/5 lab kills; reproduce public notebooks first; runtime is a first-class risk" | `round6/report.json` new_facts 10, R6-A6 (8) | These are for CONTEXT §11 after 29 Sep. Nobody owns them after the deadline |
| I54 | "Latest sub showing a new score is 00:04:20Z -> subs after ~00:00Z are mostly not on the board yet (fits the 6-8 h hidden rerun)"; "Ten more late x138 byte-copies ... landed at the END of the 0.953 block (ranks 514-523), 6th window in a row: tie order = earlier submission" | `round6/report.json` new_facts 2-3 | Rank moves before about 08:00Z carry no signal. The copy-at-block-end pattern now holds for 6 windows, which backs the V1/V2 rule against ticking #34 |
| I55 | "~6 of 96 table cells have no defined pair (K1 fails in row 4, C5 with K1, K2'' scope, B without twin, poller scope, twin Kaggle Error)"; "at k = w = 0.952 the clean flag flips the pair between {#34, exp52} and {#37, exp52}"; "row 5 'kept' always has F1 = K2 at <= 0.952" | `round6/report.json` plan_issues 2, 7 | These are covered only by v4 W2-W8 (W62). If v4 is not committed, these cells need an ad-hoc question to the user |
| I39 | "Post-freeze GT edges 2,066: FN 10.3% vs 4.5% normal ... Frozen GT steps have median 0 (GT copies positions on frozen frames; CONTEXT l.22 'GT still moving' is wrong for most) ... CPU-replayable from the exp60 presafe dump" | `round5/report.json` new_facts 17; `CONTEXT.md` l.2048 (3) | It is now in the CONTEXT records, but **`CONTEXT.md` l.22 is still wrong** (W57) |
| I44 | "The V1284 head (x138's +0.007), lowrefine and DaughterNet all read unadapted 224-d detector features; the node-count guard cannot detect feature drift" | `round5/report.json` new_facts 19; `CONTEXT.md` l.2048 (5) | B5 (`CONTEXT.md` l.196) still lacks this blocker (W57) |
| I46 | Movers with private retrained models; the silver margin went 41 -> 36 -> **34** ranks (00:47 / 03:16 / 05:46Z) with no change on our side | `round5/report.json` new_facts 1-2; `round6/report.json` new_facts 1-2 | Our rank decays through other teams' retrained models. Silver may be lost by 29 Sep. The rank is information, never an input |
| I34 | "The 44b6 '+0.0157' is one TP ... insertion +0.00648 pooled ... a dense private embryo could give K2 ~= twin" | `round4/report.json` new_facts | `CONTEXT.md` l.1932 still quotes "+0.0157 / +0.0090" |
| I01 | "Of x138's forks, 24% (15/62 on the dummies) are one-blob duplicates at t+1, against 2% of GT divisions" | `research/wf_ideas_v4/lens_literature.json` plan_critique 1-2 | The main fact for division work after 29 Sep. Every removal rule failed (fork removal went 0 for 5, `CONTEXT.md` l.2048 (4)) |
| I02 | "1 of 10 lab gains transferred ... a lab-based slot decision is allowed only for arms whose learned inputs are out-of-sample" | `research/wf_ideas_v4/lens_mine-old.json` plan_critique (4) | Not in CONTEXT (`grep "1 of 10"` = 0). It overlaps with I53 |
| I04 | "DeepCenter score recorder and the TRAINLAB summary cell are not fail-soft ... 7 of 17 44b6 picks are leak-siblings" | `CONTEXT.md` 14:29 (T5) | 44b6 lab deltas are partly in-sample |
| I05 | "K2 forecast <= 7.86 h ... the insertion gate at 8.0 h is only +0.14 h above that" (refined to 7.87 h) | `lens_headroom.json` critique (2); `CONTEXT.md` l.1970 | This is why "clean" is not guaranteed (see I50) |
| I06 | K2 dummy vs train GT: "FN 82 of 2,127 GT edges. 50% are swaps ..." | `lens_mine-old.json` critique (3) | It conflicts with I21/I22 (the "swaps" are node misses). Reconcile after 29 Sep |
| I07 | "lowrefine is not a coordinate-only rider ... +33 final nodes, +29 edges and +1 fork" | `lens_redteam-plan.json` RT2 | Why the table needs d2. Shared risk <~5e-4 (R5H-5) |
| I08 | Kernel time is not a hidden-test budget signal; use the per-dataset `[ds] repair` lines | `research/wf_ideas_v3/FINAL_REPORT.md` §j item 19 | Start-up noise is 818-1179 s |
| I09 | "Блок 0.953 на private останется единым" is untested | `FINAL_REPORT.md` §g item 13 | See I54 |
| I12 / I18 | The silver line (~196) sits INSIDE the 0.954 block, and the margin keeps shrinking (see I46) | `round2/`-`round6/report.json` new_facts | - |
| I14 | Stale operational text: `TASK_LOCAL_SESSION.md` l.12 and `TASK_FRIEND_A.md` l.40, l.52 name branch `claude/practical-meitner-31k9ye`, but the work lands on `main` | those files | Same risk as W03 |
| I15 | "The public read over-rewards fork REMOVALS whose precision lies between the private break-even (0.11-0.20) and 0.265" | `round2/report.json` plan_issues (R2-RC-B); `CONTEXT.md` l.1644 | Any future removal rule needs a private break-even clause |
| I17 | "FLOATOUT_CHECK (build_probe_kernel.py l.1315-1362) is a bare-assert cell, not fail-soft" | `round2/report.json` new_facts (12) | Moot while floatout stays closed |
| I19 | **DeepCenter t* = 0.30 is the lab optimum** in the removal direction. It is NOT node-preserving (nodes -79/-49) | `experiments/exp60_trainlab/results.md` l.13-18, l.61-66 | CONTEXT l.1930 gives only the failed gates |
| I21 | "The x138 tail is saturated. Edge FN 1,705 of 40,093 = node misses 834 (49%), swaps 730 (43%), dangling ends 141 (8%)" | `round3/report.json` new_facts (13); `FACTS.md` F-TRN-15 | In KNOWLEDGE but NOT in CONTEXT (W31 (5)) |
| I22 | "There are 0 true 2x2 swaps ... our nodes sit 3.9-4.2 um from the GT nuclei" | `round3/report.json` new_facts (14); `CONTEXT.md` l.1974 | "Swaps" are a detection/localization problem, which agrees with I53 |
| I23 | "The CONFIRMATION half reads every node-adding arm as positive ... while the LB read MIN_TRACK_LEN 4 at -0.002" | `round3/report.json` R3-A8 (3), new_facts (16) | The calibration rule is still not in CONTEXT (W31 (2)) |
| I24 | "Evaluable precision: sparse half 8 TP / 3 FP, dense half 1 TP / 3 FP ... q* = 0.114" | `round3/report.json` new_facts (11) | The quantitative case for the twin hedge |
| I26 | "hidden-rerun latency is 7-10 h with no queue problem" (other teams) | `round3/report.json` new_facts (2); `CONTEXT.md` l.1526 | Makes "not clean" a live branch (I50) |
| I28 | "GT node recall before safe divisions -> final: t0 0.959 -> 0.940 ... boundary edge TP rate 0.926 vs 0.958" | `round3/report.json` new_facts (15) | Clip-boundary node loss; deferred |
| I29 | The retention guard has no flicker penalty: switch pairs 6.05% FN | `round3/report.json` new_facts (17); `FACTS.md` F-TRN-18 | Closes hysteresis. Not in CONTEXT (W31 (4)) |

Resolved since 03:58:
- **I36**: the clean-proof stamping is fixed in V7 (`CONTEXT.md` l.2046) and runs as PID 13436.
- **I40**: fork removal 0 for 5 is at `CONTEXT.md` l.2048 (4).
- **I41**: one hidden run, and CLEAN covers public and private: V5 (l.2044) and R5H-1 (l.2048 (2)).
- **I42**: concurrent runs are handled by V4 (l.2043); I48 refines it.
- **I43**: the builder check is resolved by V3 (l.2042) and the builder change (l.2052-2054).
- **I45**: "pairs, not labels" is in V1 and V2 (l.2040-2041).
- Earlier: I03, I10, I11, I13, I16, I20, I25, I27, I30, I31, I32, I33, I35, I37 and I38.
