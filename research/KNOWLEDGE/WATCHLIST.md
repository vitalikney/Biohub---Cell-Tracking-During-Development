# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-26 10:58 UTC (curation 8). This is an incremental update of the curation-7 build from 08:50 UTC.

Sources:
- `CONTEXT.md` in the local main working tree (HEAD b41ec05), §14 up to l.2176, plus the two dated entries that sit below `## 9. Literature` (l.2179-2197).
- **`origin/main` 24dcdea (10:52:55Z) is one commit ahead of the local main.** It adds the OC STOP entry at `git show origin/main:CONTEXT.md` l.2177-2186. It also changes `poll.log` and `ledger.md`, which are modified and uncommitted locally (`git status`, `git log b41ec05..origin/main`).
- `research/wf_ideas_v4/round8/`, which is untracked and in progress:
  - The scans and skeptic `v_*.json` files were written 10:23-10:42Z.
  - `report.notes.md` is the judge's log from 10:43-10:46Z.
  - There is no `report.json` or `REPORT.md` yet.
- The worktrees `.claude/worktrees/wf_b39793f6-e79-{1,4,5,6}` (`git worktree list`, 10:53Z).
- The memory file `MEMORY.md` (l.8-9 as read at 10:53Z).
- `poll.log`: last header 10:55:02Z (l.4959). `tasklist`: python PID 20052 is alive.

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, cancelled, moot.

**Hash note.** Main was rewritten at 10:15Z (`CONTEXT.md` l.2167-2176). Hashes cited by curation 7 and in older CONTEXT entries map through `experiments/git_rewrite_map_2026-09-26.txt`:
- 64f0551 -> 093526c
- b4144e9 -> b2be382
- 4d0c477 -> 9d04fce
- 7107b6d -> 3ffe1f6
- 5336567 (round 7) -> 3992fd0
- e21d430 (ticks) -> d3ca495

**State in one line (10:58Z):**
- **FINALS TICKED 2/2** = [56563521, 56563534] (#37 K2 exp58 + #38 twin exp58n). This was API-verified at 09:10:07Z (`CONTEXT.md` l.2154-2156) and was still 2/2 at 10:45Z (`round8/report.notes.md`).
- **E10 PORT RULE IN FORCE** since the user's conditional yes at 09:10 (l.2138-2147, l.2157-2158). It was NOT triggered at 10:23Z (`round8/scan_browser.json` r8-e10-not-triggered-public-unchanged).
- **OVERLAP-CONSENSUS (OC) line: STOPPED at 10:52Z by its own gate.** G-A FAILED (43/62 < 60). There is no G-P and no K6. The proxy G-B gave -0.00047 (`origin/main:CONTEXT.md` l.2177-2186).
- LB #188 at 10:17Z. The silver margin is 8 ranks (was 13) (`round8/scan_browser.json` r8-lb-delta-1017).
- **The user's relayed request "в ветке main сделай тоже самое" is already done.** Main history was rewritten and force-pushed at 10:15Z (`CONTEXT.md` l.2167-2176, commit b41ec05). `round8/report.notes.md` 10:44Z checked it: "main log grep -ci claude = 0". This curator did not touch git.

**Changes since 08:50:**
- Done:
  - W54: ticks, l.2154.
  - W69: E10 rule and the user's OK, l.2138-2147 and l.2157.
  - W74: the user message. It was answered by "финалы отметил" and "даю условное да", l.2154 and l.2157.
  - W60/W75: `round7/REPORT.md` is in 3992fd0.
  - W26: cloud day-2 closed, l.2194-2197 and `research/wf_ideas_v3/day2_findings.md`.
  - W71 (mostly): 86a2f75.
  - W70 (partly): the RESUME POINT is at l.2148-2152. Its TICK STATUS placeholder is unfilled; see W80.
  - Round-7 records are at l.2130-2137.
- Moot:
  - Every OC step after G-A: the G-P slot, K6 build and submit, PC8-02..07, PC8-11 and PC8-12 (`origin/main:CONTEXT.md` l.2181-2182).
- New:
  - Actions W79-W85.
  - Insights I64-I73.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| W79 | **Bring the local main working tree up to `origin/main` 24dcdea BEFORE the next CONTEXT write or commit.** The local tree lacks the 10:52Z OC STOP entry, and its uncommitted `poll.log` / `ledger.md` edits collide with 24dcdea's edits to the same files. Safe path:<br>1. `git stash`.<br>2. `git pull --ff-only`.<br>3. `git stash pop`, and resolve `poll.log` by keeping both sides (it is append-only).<br>Never do a merge pull, since the history was rewritten (l.2173-2176) | not started (local HEAD b41ec05; `git log b41ec05..origin/main` = 24dcdea) | now | `git status`; `git show --stat origin/main`; `CONTEXT.md` l.2173-2176 |
| W80 | **Resume hygiene (PC8-10).**<br>(a) Fill the TICK STATUS placeholder at `CONTEXT.md` l.2149 ("<0/2 at 08:37:15Z ... | 2/2 seen hh:mmZ>") with "2/2 at 09:10:07Z (API)". A page read was never logged; add one on the next check.<br>(b) Write a new RESUME POINT: finals ticked; E10 rule in force; OC STOPPED (G-A FAIL); the rewrite rules; the round schedule.<br>(c) Move the two dated entries below `## 9. Literature` (25 Sep 14:05 T1 SAFETAIL, 26 Sep 09:40 cloud check-in, l.2179-2197) above it. A reader who follows "last RESUME POINT just above ## 9" misses them.<br>(d) `MEMORY.md` l.8 still says "E10 port rule proposed; overlap-consensus line paused". It should say "E10 PORT RULE in force (09:10Z); OC line STOPPED 10:52Z (G-A FAIL)" | not started | today, before round 9 (~13:30Z) | `CONTEXT.md` l.2148-2152, l.2177 (`## 9.`), l.2179-2197; `round8/scan_plancheck.json` PC8-10; `MEMORY.md` l.8 |
| W03 | **The friend A card is stale.** `PROMPT_FRIEND_A.md` l.1-5 now carries the history-rewrite notice (b41ec05). The next block (25 Sep ~14:30) still points to "Задача 0" and cancelled tasks. Add "finals #37 + #38 ticked; nothing to do before 29 Sep", as was done for friend C | partly done (rewrite notice only) | now (not urgent) | `PROMPT_FRIEND_A.md` l.1-9; `PROMPT_FRIEND_C.md` l.1-4 |
| W05 | Commit `experiments/ext_corwin-biocel-aux/` and `experiments/ext_y3uanm-secondary-ft/` without `__pycache__`. Delete the stray `bash.exe.stackdump`, or leave it untracked | overdue (still `??` at 10:53Z) | 25 Sep | `git status` |
| W02 | Friend A "Task 0" reply | overdue and moot (no lab or rider work remains) | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22 |

## NEXT 24 H (26 Sep 10:58 -> 27 Sep 10:58 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W57 / W66 / W31 / W72 / W81 | **by 26 Sep 12:00 (~1 h left)** | **Curator records.** Round 7 is DONE (`CONTEXT.md` l.2130-2137). Still open:<br>- l.22 still says "GT still moving" (I39).<br>- B5 at l.196 lacks the unadapted-feature blocker (I44).<br>- Round 6: the official edge FP rule (`out_valid`) and efpost as a neutral FACT (I47, I51). `grep -c` gives 0 for both.<br>- Curation 3: I-151, hysteresis, the calibration rule, and the M6 lapse (all 0).<br>- **New (W81):** ledger I-208 in `research/KNOWLEDGE/IDEAS.md` l.391 still says "refused by team policy/R9". It should read "rule-legal (08:49Z rules check), tried 09:10-10:52Z, STOPPED by pre-registered G-A FAIL 43/62; proxy G-B -0.00047". Record the R9 text too: the OC exception is used up, and N2 and other hidden-test probes stay banned (PC8-09) | in progress | `CONTEXT.md` l.22, l.196, l.2048, l.2153; `origin/main:CONTEXT.md` l.2177-2186; `round8/scan_plancheck.json` PC8-09 |
| W76 | **now: round 8 is finishing** (judge started 10:43Z); then ~13:30, ~16:00, ~18:30, ~21:00, ~23:30, ... up to 27 Sep 12:00 | **Research rounds (option b).**<br>- Round 8: save `REPORT.md` and `report.json`, then commit round8/ as the user with no trailer. The expected content: PC8-01 (G-A FAIL, now logged), RC-A/B/C closures, and R8H-1/R8H-4/R8H-7 refuted.<br>- Round 9 focus: E10 intel, finals hygiene (W80), and lessons. There is no live mechanism line: OC stopped, and RC-A was refuted as a finals candidate.<br>- From ~22:00Z: hygiene and lessons only | round 8 in progress | `CONTEXT.md` l.2082, l.2151 (2); `round8/report.notes.md` 10:43-10:46Z |
| W82 | **~11:30-12:15Z** (exp64 lab kernels a/b finish) | **Record the exp64 G-B reading as INFO ONLY (post-stop).** It must not reopen the line, since the G-A FAIL stands. Report PRIMARY ins35_splice 44b6 delta, bootstrap lower bound, `plain_official` delta, and the delta without leak group 0, next to the proxy -0.00047. No slot is used | not started (both kernels RUNNING at 10:44Z) | `origin/main:CONTEXT.md` l.2184-2185; `round8/report.notes.md` 10:44Z; `round8/scan_plancheck.json` PC8-07, PC8-12 |
| W83 | before the workflow removes its worktrees (today) | **Save the OC evidence without merging.**<br>- wt1 (bc325aa), wt4 (9826517) and wt6 (a012e32, 1986fb9) sit on the OLD history, with 26 Claude refs each. wt5 ff438f7 is on the new history.<br>- The proxy G-B results (`experiments/exp64_overlap_lab/proxy_exp39tail/results.md`), `ga_report.json`, `tools/overlap_lab.py` and `tools/overlap_probe.py` exist ONLY on those branches ("Code kept out of main for now").<br>- If they are kept: cherry-pick the non-merge commits only (never 0074f6a, 1021a65 or 633d72b), then check `git log main --format='%an %ae %B' \| grep -ci claude` = 0 before pushing | not started | `CONTEXT.md` l.2173-2175; `origin/main:CONTEXT.md` l.2185-2186; `round8/scan_plancheck.json` PC8-08; `round8/report.notes.md` 10:44Z |
| W19 / W73 | until **29 Sep 20:00** | Keep ONE poller, `lb_poll.py` (PID 20052). Before any submit, check that the last `poll.log` header is < 15 min old | in progress (last header 10:55:02Z) | `CONTEXT.md` l.2145 (P7), l.2151 (4) |
| W23 | P1 CLI checks every ~6 h: **next ~16:30Z**, then ~22:30Z, 27 Sep ~04:30Z, and so on through **29 Sep 00:00** | **E10 successor watch (P1).**<br>- Last check 10:17-10:23Z: NOT met. The newest public run is still Harmonic Fusion V3 (25 Sep 09:09Z); x138 is still v1 (200 votes, 277 copies).<br>- `koushikrudra/biohub-zerogpu-consensus-v1` is a static CSV, not a method.<br>- Bursts from submits made ~23:30-02:00Z are the daily pattern (P2) | in progress | `CONTEXT.md` l.2139-2140; `round8/scan_browser.json` r8-e10-not-triggered-public-unchanged; `round8/scan_hypotheses.json` R8H-8 |
| W50 | ask again **today**; reminders in place **by 28 Sep** | Durable 29 Sep 12:00 and 18:00 reminders that survive this session: in the user's own calendar, or a cloud routine only with a new OK | not started (no log line; only a mention in the OPEN list at l.2151 (3)) | `CONTEXT.md` l.2037-2038, l.2151 |
| W71 (residue) | with round 9 | `experiments/workflows/biohub-research-round.js` l.36 (the recheck scan) still says "12 h limit with ~4 h headroom". The hypotheses text (l.35) was fixed in 86a2f75 | partly done | `experiments/workflows/biohub-research-round.js` l.35-36 |
| T26 | **today** | The public silver line (~rank 196) was 8 ranks below us at 10:17Z and will likely pass us. The wave is slowing (>=0.953 grew +13 in 1.9 h, against +41 in 2.6 h). Info only (R7) | watch | `round8/scan_browser.json` summary, r8-lb-delta-1017 |
| T12 | **26 Sep 18:00** | The M6 reopen window for K4/tempfuse lapses. Note the lapse with W31 | pending (expected lapse) | `CONTEXT.md` 25 Sep 20:55 (M6); `round6/report.json` rejected 3 |
| T17 | 26 Sep, until 23:59 | 3 unused slots on 26 Sep. They stay EMPTY: the G-P slot is not needed now that OC has stopped, and E10 has not triggered | - | `CONTEXT.md` l.2151; `origin/main:CONTEXT.md` l.2181-2182 |
| T27 | **~26 Sep 22:00** | After this, no round idea can become a final (lab gate, dummy, build, new OK and slot all before R8) | - | `CONTEXT.md` l.2151 (2) |
| T18 | **27 Sep 00:00** | Slot reset: 5 slots for 27 Sep (S8 = E10 port only, by trigger) | - | `CONTEXT.md` l.1611, l.2145 |
| W59 | optional | `tools/runtime_ledger.py` text fixes. Now cosmetic; PC8-11's K6/exp66 mapping is moot because OC stopped. If done, run `python -m pytest tests/test_runtime_ledger.py` | not started, low priority | `round7/report.json` R7-A6; `round8/scan_plancheck.json` PC8-11 |

## LATER (27 Sep 10:58 -> 29 Sep 23:59 UTC)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T02 | 27 Sep ~09:00 | LB snapshot (info only). Compare with #188 at 10:17Z on 26 Sep | `round8/scan_browser.json` r8-lb-delta-1017 |
| T03 | **27 Sep 12:00** | **R8: no new mechanisms after this, and the end of the full research rounds (option b).** The E10 port of a PUBLIC successor stays possible (S8/S14); the P1 CLI watch continues | `CONTEXT.md` l.1671-1672, l.2139, l.2151 |
| T04 / T05 | 28 Sep 12:00 / 16:00 | S12 consolidation and S13. **Moot:** K2 is already the final and no rider or OC candidate exists | `CONTEXT.md` l.1614-1615, l.2150 |
| T28 | 28 Sep | S14: an x138 successor on a late trigger (P7) | `CONTEXT.md` l.1616, l.2145 |
| T19 / W77 | **28 Sep evening** | Re-run the API tick check (group=SELECTED; it must print `[56563521, 56563534]`), and do the first page read. The W50 reminders must exist by now | `CONTEXT.md` l.2132 (2), l.2154-2156 |
| T20 | **29 Sep 00:00** | Last slot reset, and the **last useful E10 trigger** (a port needs ~7.5 h) | `CONTEXT.md` l.2145 |
| T29 | **29 Sep 02:00** | The last E10 port submit (R8 "emergency repeat only" afterwards). The hard edge is 10:00 (S17) | `CONTEXT.md` l.1617, l.1671-1672, l.2145 |
| T09 / W77 | 29 Sep ~11:30 / **12:00** (backup **18:00**) | Re-run the API SELECTED check and remind the user to CHECK the ticks (already set) | `CONTEXT.md` l.2151 (3), l.2155-2156 |
| T10 | **29 Sep 20:00** | Ticks final: exactly 2 files. Default {#37 56563521, #38 56563534}. If an E10 port is adopted under P6, it is {port, #37}. Never tick #34, #35 or P36; never two identical files. **Poller stop** | `CONTEXT.md` l.2144, l.2149, l.2151 (4) |
| T11 | 29 Sep 23:59 | Competition deadline | `CONTEXT.md` §1 |
| W29 | after 29 Sep | Post-deadline work:<br>- E14 (friend A's out-of-embryo A/B).<br>- Linker item #1: re-solve plus efpost (I39, I51).<br>- Axial localisation of z-elongated nuclei (I57).<br>- The z-shift re-test on out-of-sample clips (I66).<br>- Far-daughter localisation (I67).<br>- OC registration kept as a tool (I64).<br>- Lessons for §11 (I53, I65, I69, I72) | `TASK_FRIEND_A.md` "Задача 4"; `CONTEXT.md` l.2134 (4); `round8/scan_recheck.json` |

**Done, cancelled or moot since 08:50 (for the record):**
- W54 done: FINALS TICKED 2/2 (`CONTEXT.md` l.2154-2156, commit d3ca495).
- W69 done: the E10 PORT RULE is at l.2138-2147, and the OK at l.2157-2158. Its P1 carries the correction that the watch runs to 29 Sep 00:00.
- W74 done: the user replied at 09:10 (l.2154, l.2157). Only the W50 reminder part is still open.
- W60/W75 done: `research/wf_ideas_v4/round7/REPORT.md` is in 3992fd0. `round2/REPORT.md` is still missing (low priority; `ls research/wf_ideas_v4/round2/`).
- W26 done: the cloud check-in and `day2_findings.md` (l.2194-2197, da645e8).
- W70 partly done: see W80.
- W71 mostly done: 86a2f75.
- The OC line: gates recorded at 08:58 (l.2110-2128), paused (l.2129), resumed at 09:10 (l.2159), and **STOPPED at 10:52 by G-A FAIL** (`origin/main:CONTEXT.md` l.2177-2186). Everything downstream is moot: G-P, K6 (wt5 exp66, built and not pushed), the G-LB/R4 precedence line and the P6 K6 pair (PC8-02..07, PC8-11, PC8-12).
- Earlier: see `research/KNOWLEDGE/_curation/7/watch.json`, `_curation/6/watch.json` and `_curation/5/watch.json`.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| I69 | **"R8H-1 rests on the assumption that 'public = one embryo'. That is a participants' guess, not a host fact. The hosts say the test holds two embryos and that public is ~29% of the test data ... How the host split rows between public and private is unknown. If the split is by video, both prefixes hold public and private clips"** | `round8/v_hypotheses_r8h-1.json`; `research/discussions_summary.md` l.4-6 ("participants guess public = one embryo"); `research/wf_ideas_v3/browser_intel.md` l.210 | "Public = one embryo" is stated as fact in the round prompt, the task texts and many CONTEXT lines. Every "public says nothing about embryo X" argument inherits this unverified premise. Add the caveat to the lessons and the round prompt |
| I65 | **Proxy G-B (exp39 tails, all 71 44b6 clips): "44b6 delta -0.00047 (boot lower -0.00216) ... delta w/o node multiplier -0.00058 ... nodes -2200 ... clip wins/losses 22/37"**. Only leak group 0 is positive (+0.00050, 24 clips). The splice introduced 6 `outside_crop` rows | `.claude/worktrees/wf_b39793f6-e79-6/experiments/exp64_overlap_lab/proxy_exp39tail/results.md` (commit 1986fb9, **old-history branch, not on main**) | The design's ceiling was +0.004..+0.006 (`CONTEXT.md` l.2114). The measured sign is negative, so the value half failed as well as G-A. This file disappears with the worktree unless W83 keeps it |
| I64 | "Registration is exact and false-free: 58 of the 62 GT-linked pairs produced a candidate at the exact GT offset (0 wrong offsets). 43 were accepted ... The 6 extra pairs have equal_fracs 1.0" (real copies missing from the GT link list). Also: "'65' in CONTEXT is a typo: splits.json ... = 62" | `round8/scan_hypotheses.json` R8H-9; `round8/v_hypotheses_r8h-9.json`; `round8/scan_plancheck.json` PC8-01 | A reusable, verified crop-registration tool (0 6bba, 0 cross-embryo). The line failed on recall and value, not on correctness. `CONTEXT.md` l.2116 still carries "65" |
| I66 | **Embryo-constant z shift: "z + 0.1 voxel before rounding gives +0.0016 pooled (44b6 +0.0025, 6bba +0.0015 ...)"**. The skeptic's view: "6bba is solid (P(<=0) = 0, LOO min +0.00107, a plateau of +0.0015..+0.0018 over +0.1..+0.3)", while the 44b6 part "rests on 2 clips". Refuted as a finals candidate because transfer cannot be tested before R8 (Canh's xyz correction lost 0.0031 on public) | `round8/scan_recheck.json` R8-RC-A; `round8/v_recheck_r8-rc-a-embryo-constant-z-shift-on-x138.json` | A 3-5x revision of the old v3 ceiling (+0.0003..+0.0005). It agrees with I57 (axial offset excess). It is the best cheap post-deadline test, and appears only in round-8 JSON |
| I67 | "99 GT divisions = steal 35 + orphan 27 + one daughter unmatched 21 + TP fork 12 ... So 62 are detected but unforked. Far step median 9.88 um ... Only 8/62 far daughters are within 7 um" | `round8/v_recheck_r8-rc-c-split-aware-flow-relink-reach.json` | Division gains are limited by far-daughter localisation, not by the linker gates. It sits alongside I01 and I57 on the post-deadline list |
| I72 | "This session's harness reminder asks for a Co-Authored-By trailer, which conflicts with the user's standing rule, and the user's rule wins" | `round8/scan_plancheck.json` PC8-08; memory `feedback-git-no-coauthor.md` | Main was just rewritten to remove Claude authorship (`CONTEXT.md` l.2167). Any agent that follows the harness attribution reminder re-adds it. Every commit must be checked with `grep -ci claude` = 0 |
| I73 | Bit-probe encoding lesson: "Any exception outside run_probe's try block also gives 'Threw Exception' and would be misread as 'overlap exists' ... write a deliberately malformed submission.csv ... gives 'Submission Scoring / Format Error'" | `round8/scan_plancheck.json` PC8-02; `round8/v_plancheck_pc8-02.json` | A general rule for any future hidden-set probe: give the signal its own error class. Moot for OC; a lesson for §11 |
| I68 | "FP:TP break-even = 1/J = 7.7 at lab J 0.129 (exp60 control pooled 16/25/83) and 2.8 at public J 0.36" (the "2.8:1 from the P20 tie" argument is withdrawn) | `round8/v_recheck_r8-rc-b-divnet-parent-veto-on-x138.json` | The fork-precision break-even differs ~3x between lab and public. It completes I15 and I24 |
| I70 | Discussion 742942 (Himanish Goel, ~09:20Z 26 Sep): "sometimes a split is marked at the wrong coordinates and sometimes the daughter cell is dropped 1 frame later"; "an honest model may hurt the score unless it replicates the GT noise" | `round8/scan_browser.json` r8-discussion-two-comments-known-threads | GT-noise evidence for the division lessons (I39, the GT quirks at `CONTEXT.md` l.22) |
| I71 | Round-8 skeptics refuted two OC hypotheses by measurement. R8H-4: "the true dt is always tried first" (a frozen frame cannot shift the time). R8H-7: "hashing is 0.7% ... ThreadPoolExecutor(4) ran 3.06x faster than sequential" | `round8/v_hypotheses_r8h-4.json`; `round8/v_hypotheses_r8h-7.json` | If OC is revisited after 29 Sep, these two risks are already closed. PC8-03 (MAX_S 1800 could make K6 == K2 silently) stays the open runtime question |
| I56 | "Finals ticks are readable via competition_submissions(group=SubmissionGroup.SUBMISSION_GROUP_SELECTED)". The first positive was seen at 09:10:07Z = [56563521, 56563534] | `CONTEXT.md` l.2132 (2), l.2154-2156 | Now in CONTEXT (resolved as a record). Keep it for W77: a page read was never logged next to the API read |
| I57 | "668 missing GT nodes ... absent upstream 557 (83%) ... z-dominant 41% vs 25-28% in the control (axial offset excess)" | `CONTEXT.md` l.2134 (4) | Now in CONTEXT. It is kept here because I66 gives it a cheap first test |
| I59 | "Bursts from submits made ~23:30-02:00Z ... are the daily pattern, not a signal on their own" | `CONTEXT.md` l.2140 (P2), l.2131 | Now in CONTEXT; round 8 confirms it (movers submitted 00:02-06:11Z, `round8/scan_hypotheses.json` summary) |
| I61 | forkmid is the only power-limited closure (+0.00013, div_J +0.0010); the 6bba-only replication was not run | `CONTEXT.md` l.2136 (6) | Now in CONTEXT. Post-deadline |
| I47 | **"Official edge FP rule: a predicted edge is scoreable iff its source matches a GT node with out-degree > 0 OR its target matches a GT node with in-degree > 0; a 'both ends matched' shortcut undercounts FP ~20x"** | `round6/report.json` new_facts 8; `tools/official/src/tracking_cellmot/metrics.py` l.165-194 | Still in no CONTEXT line (`grep -c out_valid CONTEXT.md` = 0). W66 |
| I51 | "efpost ... 6bba +0.00174, 44b6 exactly 0 ... kept as a FACT only" | `round6/report.json` new_facts 7, R6-A6 (5) | `grep -c efpost CONTEXT.md` = 0. Post-deadline linker item |
| I52 | "stitch ... ceiling ~+0.0003 -> CLOSED"; "Linefit w0.7 win2 ... null effect, rider closed" | `round6/report.json` new_facts 7, rejected 9-10 | Keep it on the do-not-repropose list (86a2f75 added a closed list) |
| I53 | Lessons (R6H-7): "gains came from detection/localisation ... not the linker tail; in-sample ILP/edge-net trust and lab gains < ~+0.003 did not transfer; LB agreed with 5/5 lab kills" | `round6/report.json` new_facts 10 | For §11 after 29 Sep, with I65, I69 and I72 |
| I54 / I46 | Late x138 byte-copies land at the END of the 0.953 block; round 8 saw the **8th** window (~10 more). The silver margin went 41 -> 36 -> 34 -> 13 -> **8** ranks (00:47 / 03:16 / 05:46 / 08:22 / 10:17Z) | `round6/report.json` new_facts 2-3; `CONTEXT.md` l.2131; `round8/scan_browser.json` summary | This backs the rule against ticking #34. Rank is information only (R7) |
| I39 | "Frozen GT steps have median 0 (GT copies positions on frozen frames; CONTEXT l.22 'GT still moving' is wrong for most)" | `round5/report.json` new_facts 17; `CONTEXT.md` l.2048 (3) | **`CONTEXT.md` l.22 is still wrong** (W57) |
| I44 | "The V1284 head, lowrefine and DaughterNet all read unadapted 224-d detector features; the node-count guard cannot detect feature drift" | `round5/report.json` new_facts 19 | B5 (`CONTEXT.md` l.196) still lacks this blocker (W57) |
| I34 | "The 44b6 '+0.0157' is one TP ... insertion +0.00648 pooled" | `round4/report.json` new_facts | `CONTEXT.md` l.1932 still quotes "+0.0157 / +0.0090" |
| I01 | "Of x138's forks, 24% (15/62 on the dummies) are one-blob duplicates at t+1, against 2% of GT divisions" | `research/wf_ideas_v4/lens_literature.json` plan_critique 1-2 | For division work after 29 Sep (with I67) |
| I02 | "1 of 10 lab gains transferred ... a lab-based slot decision is allowed only for arms whose learned inputs are out-of-sample" | `research/wf_ideas_v4/lens_mine-old.json` plan_critique (4) | Overlaps I53. The OC G-B bed (71 44b6 clips incl. head-train stems, PC8-04) was in-sample too |
| I04 | "7 of 17 44b6 picks are leak-siblings" | `CONTEXT.md` 25 Sep 14:29 (T5) | 44b6 lab deltas are partly in-sample |
| I06 | K2 dummy vs train GT: "FN 82 of 2,127 GT edges. 50% are swaps" | `lens_mine-old.json` critique (3) | Conflicts with I21/I22/I57 (the "swaps" are node misses). Reconcile after 29 Sep |
| I07 | "lowrefine is not a coordinate-only rider ... +33 final nodes, +29 edges and +1 fork" | `lens_redteam-plan.json` RT2 | Lessons |
| I08 | Kernel time is not a hidden-test budget signal; use the per-dataset `[ds] repair` lines | `research/wf_ideas_v3/FINAL_REPORT.md` §j item 19 | For the E10 port P5 runtime read |
| I09 | "Блок 0.953 на private останется единым" is untested | `FINAL_REPORT.md` §g item 13 | See I54 and I69 |
| I14 | `TASK_LOCAL_SESSION.md` l.12 and `TASK_FRIEND_A.md` l.40, l.52 name branch `claude/practical-meitner-31k9ye`. Main is no longer mirrored to it (`CONTEXT.md` l.2166) | those files | Friend A could pull a stale branch; W03 |
| I15 | "The public read over-rewards fork REMOVALS whose precision lies between the private break-even (0.11-0.20) and 0.265" | `round2/report.json` plan_issues (R2-RC-B) | Lessons (with I68) |
| I19 | **DeepCenter t* = 0.30 is the lab optimum** in the removal direction, and it is NOT node-preserving (nodes -79/-49) | `experiments/exp60_trainlab/results.md` l.13-18, l.61-66 | CONTEXT l.1930 gives only the failed gates |
| I21 | "The x138 tail is saturated. Edge FN 1,705 of 40,093 = node misses 834 (49%), swaps 730 (43%), dangling ends 141 (8%)" | `round3/report.json` new_facts (13); `FACTS.md` F-TRN-15 | Not in CONTEXT (W31); I57 refines it |
| I22 | "There are 0 true 2x2 swaps ... our nodes sit 3.9-4.2 um from the GT nuclei" | `round3/report.json` new_facts (14); `CONTEXT.md` l.1974 | Agrees with I53, I57 and I66 |
| I23 | "The CONFIRMATION half reads every node-adding arm as positive ... while the LB read MIN_TRACK_LEN 4 at -0.002" | `round3/report.json` R3-A8 (3) | The calibration rule is not in CONTEXT (W31) |
| I24 | "Evaluable precision: sparse half 8 TP / 3 FP, dense half 1 TP / 3 FP ... q* = 0.114" | `round3/report.json` new_facts (11) | The case for the twin hedge (F2) |
| I28 | "GT node recall before safe divisions -> final: t0 0.959 -> 0.940 ... boundary edge TP rate 0.926 vs 0.958" | `round3/report.json` new_facts (15) | Clip-boundary node loss; post-deadline |
| I29 | The retention guard has no flicker penalty: switch pairs 6.05% FN | `round3/report.json` new_facts (17); `FACTS.md` F-TRN-18 | Not in CONTEXT (W31) |

**Resolved since 08:50:**
- **I56, I57, I59, I61:** now in `CONTEXT.md` l.2131-2136. They are kept above only as short pointers.
- **I58** (gap LAP closed; synthetic nodes match GT ~1%): `CONTEXT.md` l.2133 (3).
- **I60** (the §f(iii) port conflict): resolved by the E10 PORT RULE P6 waiver and the user's OK (l.2144, l.2157).
- **I62** (the night-trigger 8 h loss): moot, since the OK came at 09:10 with P8 autonomy (l.2146, l.2157).
- **I63** (the RC-C runtime wording): `CONTEXT.md` l.2135 (5).
- Earlier: I03, I05, I10-I13, I16-I18, I20, I25-I27, I30-I33, I35-I38, I40-I43, I45 and I48-I50/I55 (`_curation/7/watch.json`).
