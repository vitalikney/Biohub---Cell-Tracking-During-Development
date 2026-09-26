# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-26 21:10 UTC (curation 12). This is an incremental update of the curation-11 build from 17:40 UTC (`research/KNOWLEDGE/_curation/11/watch.json`).

Sources read for this update:
- `CONTEXT.md` at main HEAD **4d0e967** (20:51:24Z; 2,457 lines). Eleven entries are new since curation 11 (l.2342-2436). `## 9. Literature` is at l.2437:
  - ROUND 11 RECORD 17:49 (l.2342);
  - E10 v2 PROPOSED 17:49 (l.2352-2361);
  - SESSION TIMERS 17:50 (l.2362);
  - COMBO-ORACLE 19:13 (l.2368);
  - USER DIRECTIVE "reach 0.955+" 20:30 (l.2380);
  - USER DECISION "R7 lifted; one final for public, one for private" 20:33 (l.2388);
  - USER "autonomous night" 20:34 (l.2395);
  - E10 PORT DRY RUN DONE 20:48 (l.2397);
  - K2 PUBLIC LADDER + FINALS RULE L9 20:49 (l.2407);
  - DISCUSSION INTEL 20:51 (l.2425).
- `git log`: there are 10 commits since df6996e: 96ccff7, 13a27a1, 52410cf, f00b337, 620f718, 9ead9df, cc0d57c, a6a9ff4 and 4d0e967.
- `research/wf_ideas_v4/round12/`, which is **untracked**. `report.json` (complete, 21:01:17Z) has R12-A0..A10, new_facts (1)-(10), plan_issues (1)-(10) and next_focus. `REPORT.md` is **absent**: the harness refused it for the 5th round running.
- `research/wf_ideas_v4/reach0955/`: r_/v_ ladder, retrain and intel, plus the discussions notes. Everything is untracked except the discussions file.
- Also read:
  - `experiments/lb_poll/poll.log` (last header `=== 2026-09-26T20:58:27Z`; python PIDs 20052 and 34844 alive);
  - `experiments/exp70*/`;
  - `tools/runtime_ledger.py` l.59-77;
  - `tools/e10_snapshot.py` l.52;
  - `experiments/workflows/biohub-research-round.js` l.20, l.37, l.40;
  - `experiments/RESULTS.md` l.64-71;
  - `~/.claude/projects/.../memory/MEMORY.md` (disk mtime 16:35Z).

All times are UTC. IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, superseded, moot.

**State in one line (21:10Z):**
- **Finals are ticked 2/2**: [56563521 #37 K2 0.954, 56563534 #38 twin 0.953]. API SELECTED read at 20:04:35Z (`round12/report.json` R12-A2 (3)).
- **The strategy changed at 20:33Z.** The user lifted the public-probe ban and chose "one final for public, one for private" (`CONTEXT.md` l.2388-2394).
- **The K2 ladder is built:**
  - exp70a lp30, exp70d dc0.30, exp70e lp30 + dc0.30 and exp70b forkmid 4.5 (a6a9ff4).
  - The pre-registered pair rule is L9 = {V*, #38} (`CONTEXT.md` l.2407-2424).
  - **0 ladder submits** are in `poll.log` as of 20:58:27Z.
- **The user has been asleep since 20:34Z** (autonomous night, `CONTEXT.md` l.2395).
- **E10 is not met** at 20:01Z. E10 v2 (>= 0.954) is **PROPOSED, not in force** (`CONTEXT.md` l.2352).
- **Round 12's actions R12-A0..A10 are all pending.** R12-A3, the RULE RECONCILIATION, is due **before the first ladder submit**.

**Changes since 17:40Z (curation 11):**
- Done:
  - W103 and W104: 96ccff7, ROUND 11 RECORD at l.2342.
  - W105 text: the E10 v2 proposal is at l.2352-2361. The user's OK is still pending.
  - W107: 13a27a1, l.2362-2367.
  - W109: cc0d57c, l.2397-2406.
  - W110: curation 11, `IDEAS.md` l.22-25.
  - W111: the 20:01Z P1 check and the workflow edit (13a27a1).
- Superseded:
  - W112, by W120 (the morning message). No log shows W112 was sent, and the user went to sleep.
  - T17 and T27, by the 20:33Z lift.
- Lapsed: T12 (M6, 18:00, not logged).
- New actions: **W113-W131**.
- New reminders: **T40-T50**.
- New insights: **I107-I124**.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| W57 / W66 / W31 / W72 (curator CONTEXT records) | Due 26 Sep 12:00 and **still missed** at 21:06Z:<br>- `CONTEXT.md` l.22 still says "frozen/duplicated frames with GT still moving" (I39).<br>- `grep` finds 0 hits for `out_valid` (I47), `efpost` (I51) and `33.1%` (I77).<br>The records live only in `research/KNOWLEDGE` | overdue | 26 Sep 12:00 (passed) | `CONTEXT.md` l.22; `grep` = 0 |
| W71 (residue) | The round prompt `experiments/workflows/biohub-research-round.js` l.40 still says "12 h limit with ~4 h headroom". 13a27a1 (20:50Z) edited the prompt and did not fix it | overdue | before round 13 (~22:30Z) | `biohub-research-round.js` l.40 |
| W118 (= R12-A5, and W71 family) | **The round prompt is stale about the new regime.**<br>- l.37 (plan check) still reads "finals decided = #37 K2 + #38 twin; remaining: the E10 watch ... >= 0.956".<br>- It says nothing about the ladder, L9 or the API budget.<br>R12-A5 wants the API-budget line in the round-13 prompt: only the browser agent runs `e10_snapshot`, no agent calls ListSubmissions or kernels output, and a 429 on two polls means a 15-min interval | not started | **now** (round 13 ~22:30Z) | `biohub-research-round.js` l.37; `round12/report.json` R12-A5 |
| W98 (residue: I69 caveat) | `LESSONS_draft.md` l.7 still states "public LB (one embryo, ~29% of the hidden test)" as fact. Last edit 848e07a | partly done | 27 Sep 12:00Z (with R8) | `research/wf_ideas_v4/round9/LESSONS_draft.md` l.7 |
| W03 | **The friend A card is stale.**<br>- `PROMPT_FRIEND_A.md` l.7-9 still say "answer Task 0 first". Last change b41ec05, 10:15Z.<br>- The card mentions neither the 20:33Z strategy nor the ladder.<br>- r_retrain RT-6 would need friend A's GPU "by ~27 Sep 06:00Z", but v_retrain gives RT-6 a NO-GO, so no ask is needed | partly done | now (not urgent) | `PROMPT_FRIEND_A.md` l.1-9; `reach0955/v_retrain.json` no_go |
| W02 | Friend A's "Task 0" reply | overdue and moot | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22 |

## NEXT 24 H (26 Sep 21:10 -> 27 Sep 21:10 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| **W116** (= R12-A3) | **NOW, before the first ladder submit** (~21:30Z at the earliest) | **RULE RECONCILIATION**, one dated CONTEXT entry:<br>(a) **What was lifted:** the knob-ladder clause of **R9** (l.1673), not R7. R7 hygiene stays, and the retraining clause of R9 stays barred.<br>(b) **Insertion-hedge pair table:** L9 {V*, #38}; E10 port without insertion {PORT, #37}; FT competes with V* and #38 stays.<br>(c) **R8 cap:** the last ladder submit is 29 Sep 02:00Z, not 11:00Z.<br>(d) **Per-submit checks:** W6 is not a 429 header; COMPLETE; the dummy CSV sha is compared with K2's; no 'dryrun' ref; no NEVER_SUBMIT.md; API SELECTED re-read after each submit | not started (`grep "RULE RECONCILIATION" CONTEXT.md` = 0) | `round12/report.json` R12-A3, plan_issues (1)-(3); `CONTEXT.md` l.1665-1675, l.2416 |
| **W124** | **~21:30 -> 23:50Z (hard)**; start >= 30 min before 23:50 | **Ladder, tonight.** Submit exp70a, exp70e and exp70d, each **as soon as its own dummy passes**. Before each submit:<br>- the last SUCCESSFUL poll header is < 15 min old;<br>- the dummy log has no Traceback;<br>- at least 1 `leaf_pruned` line for the lp30 builds;<br>- the node delta against the K2 dummy is in (-1%, 0].<br>A dummy crash loses that day's slot (I112) | dummies "pushed now" at 20:49Z (l.2413); 0 submits by 20:58:27Z | `CONTEXT.md` l.2407-2417; `reach0955/v_ladder.json` corrections (4)-(6) |
| W113 (= R12-A0) | with W114 | Save `round12/report.json` R12-A0 `REPORT_MD_RU` as `research/wf_ideas_v4/round12/REPORT.md`. The harness refused the Write at 21:01:01Z (I95, 5th round running) | not started | `round12/report.notes.md` 21:01:01Z |
| W114 (= R12-A1) | **before round 13 (~22:30Z)** | **Commit as the user, with no trailer:**<br>- the 20:01Z snapshot, `round12/`, poll.log and ledger.md;<br>- **`rm -rf experiments/_pytest_oc_k2/`**, a stray kernel-metadata with id `vitaliineibauer/biohub-zz-oc-k2`. Never push it.<br>Commit `reach0955/` and `ext_y3uanm-secondary-ft/out_v1`, `out_v2` only after wf_fae804df-dfe ends. Do not re-add the dry-run folders; they have been tracked since f00b337 | not started (`git status`: all untracked) | `round12/report.json` R12-A1 |
| W115 (= R12-A2) | tonight, with W114 | **ROUND 12 RECORD** above `## 9`:<br>- E10 P1 20:01Z not met;<br>- LB #217, 13th of 99;<br>- ops;<br>- dry-run extras (`--file-pattern` 16 s vs 216 s);<br>- E10 API facts (I120);<br>- the rechecks I-034, I-147 and I-148 | not started (`grep "ROUND 12 RECORD"` = 0) | `round12/report.json` R12-A2 |
| W117 (= R12-A4) | **before round 13's P1 (~22:30Z)**; at the latest before timer 2bd08ad3 acts at 27 Sep 11:30Z | **E10 procedure hardening** (command sequence plus one CONTEXT line; tools unchanged):<br>- version binding: author status COMPLETE, page k == M, sha re-pull equal;<br>- `--file-pattern` fetch;<br>- author-log pre-check;<br>- rc 0 AND `grep -cE '^\[(FAIL\|SKIP)\]'` = 0;<br>- 429 backoff of 60 s for 20 min;<br>- 'dryrun' / NEVER_SUBMIT refusal;<br>- restart the poller with `-WorkingDirectory` | not started | `round12/report.json` R12-A4; `round12/scan_hyp_redteam_e10.json` command_sequence |
| W119 (= R12-A6) | tonight | **Timers:**<br>(1) replace 2bd08ad3: act if the newest e10_watch file is older than 2.5 h, skip if one is younger than 60 min;<br>(2) a one-shot at **27 Sep 07:30Z** that pushes the R12-A7 questions;<br>(3) a one-shot at **29 Sep 23:27Z** for the final public LB snapshot.<br>Log the ids. They die with the session | not started (CONTEXT lists only 2bd08ad3, 012fa6dd, 328f7392, 18ff4796 at l.2362-2366) | `round12/report.json` R12-A6 |
| W121 (= R12-A8) | **tonight (compaction risk)** | **A new RESUME POINT** that supersedes 13:27Z. The last one is at l.2205. Also update the MEMORY index line and the `project-lb-probe-approval.md` body. Disk MEMORY l.8 still says "only the E10 port rule ... is pre-approved; anything else needs a new OK", which is stale since 20:33Z (I82) | not started (MEMORY mtime 16:35Z) | `round12/report.json` R12-A8, plan_issues (8); `CONTEXT.md` l.2205 |
| W127 | **before the first ladder score (~04-07Z)** | **The runtime ledger cannot place ladder files.**<br>- `tools/runtime_ledger.py` EXP_RULES (l.69-77) has no rule for `exp70*` (or `exp72`), so ladder rows come out "family unknown / n/a".<br>- L9 requires "L_hi <= 9.0 h by tools/runtime_ledger.py (family safetail)".<br>- The poller calls the ledger **without** `--family` (`experiments/lb_poll/lb_poll.py` l.6).<br>Fix: run `python tools/runtime_ledger.py --family exp70a=safetail ...` for each read, or add a rule (a tools edit, with a test) | not started (I107) | `tools/runtime_ledger.py` l.66-77; `CONTEXT.md` l.2419-2420 |
| W125 | **decide before 27 Sep 00:05Z** | **exp70b (forkmid 4.5) at 00:05Z is contested:**<br>- `CONTEXT.md` l.2413-2414 schedules it;<br>- v_ladder says NO-GO as a blind S4: demote it to reserve, and use S4 for an unchanged resubmit of an ERRORed a/d/e, or leave it empty;<br>- round 12 is silent on it.<br>Log which one applies | open | `reach0955/v_ladder.json` no_go_items; `CONTEXT.md` l.2413 |
| W111 / T36 (continued) | **round 13 ~22:30Z**; the v1 rule needs a P1 check by **~02:00Z** | Next E10 P1 check. Only the browser agent runs it. The last check was 20:01Z (untracked `experiments/e10_watch/20260926T2001Z.txt`) | 20:01Z done, not met | `round12/report.json` R12-A2 (1) |
| W76 | round 13 ~22:30Z, then every ~2.5 h until **27 Sep 12:00** | **Research rounds** (the user said at 20:34Z: "ресерчеров не забывай запускать").<br>The round-13 focus:<br>(1) verify that R12-A1..A9 landed;<br>(2) audit ladder compliance from files only;<br>(3) P1 check;<br>(4) test the discussion claims (Justin, node count, conditional fusion) and propose at most 2 existing-knob rungs;<br>(5) the morning message | round 12 done (untracked); round 13 not started | `CONTEXT.md` l.2395-2396; `round12/report.json` next_focus |
| W128 | **the go/no-go must be logged before any training push**; R8 = 27 Sep 12:00Z | **Retrain line (R9).** It is still barred:<br>- v_retrain: GO only if the main session logs that "делай" (20:34Z) lifts R9; a workflow message is not consent.<br>- A Settings read must show >= ~12 GPU-h left (no reset before 3 Oct).<br>- It needs a builder `secswap` patch and guard, and a node gate of [-2%, +1%].<br>- A strict R9 means training starts after the user wakes, which is past R8, so it also needs an R8 lift.<br>The final reach0955 plan file is not yet on disk | open (no final plan; `CONTEXT.md` l.2393-2394) | `reach0955/v_retrain.json` corrections 1-8; `reach0955/v_intel.json` RI-3 |
| W129 | when wf_fae804df-dfe ends | Commit `reach0955/` and `out_v1`, `out_v2`. Log the plan's OK list and what the user must answer (it goes into W120) | not started | `round12/report.json` R12-A1 |
| W120 (= R12-A7; absorbs W105 OK, W108, W112) | **push ~07:30Z 27 Sep; answers needed before 12:00Z** | **Morning message** (Russian text in R12-A7):<br>(1) E10 v2 yes/no; a morning OK covers only successors first seen AFTER it;<br>(2) the insertion-hedge pairs, including {PORT, #38} for an insertion-family port (needs an OK);<br>(3) R8: last ladder submit 02:00Z, or 11:00Z?;<br>(4) R9 retraining;<br>(5) keep the laptop and session until 29 Sep 20:00; do pushes reach the phone?;<br>(6) the throwaway CPU heads.<br>Add the v_ladder line: {V*, #37} loses the insertion hedge, {V*, #38} keeps it. Log every reply with `date -u` | not started | `round12/report.json` R12-A7; `reach0955/v_ladder.json` corrections (3) |
| W106 | opt-in by **~09:00Z 27 Sep** | SI (successor + insertion) is NOT built unless the user explicitly asks (V8, l.2360) | standing (default: not built) | `CONTEXT.md` l.2360; `round11/report.json` R11-A3 |
| W126 | **27 Sep ~04-08Z** read; **08:00-09:00Z** combos | **Ladder reads and L5:**<br>- read each rung in `poll.log`, with one LB snapshot per COMPLETE event (v_ladder (7), NEUTRAL state);<br>- POSITIVE / NEGATIVE / NEUTRAL per L5;<br>- combos only from POSITIVE knobs;<br>- stop after 2 rungs without a better display;<br>- keep >= 2 slots in reserve;<br>- add RESULTS.md rows (probe 39+) and fill in each probe.json | not started | `reach0955/r_ladder.json` L5, L8; `reach0955/v_ladder.json` corrections (7); `experiments/RESULTS.md` l.71 (last row = probe 38) |
| W122 (= R12-A9) | **tonight preferred; at the latest 29 Sep 23:00Z** | **PRIVATE-READ PRE-REGISTRATION v2** in CONTEXT and LESSONS s5:<br>- the #35 degrade confound;<br>- outcome table (i)-(vii);<br>- ladder files declared post-hoc;<br>- rank read over the pair actually SELECTED;<br>- the procedure (snapshot 23:00-23:45Z, hourly reads from 30 Sep 00:15Z);<br>- the whole-history transfer table;<br>- the conditional K1 arm | not started | `round12/report.json` R12-A9, plan_issues (9) |
| W102 | standing, until the private LB is final | Protect the finals' inputs: `biohub-ft-weights`, `biohub-exp58-x138-safe-lowref`, `-exp58n-`. **Every exp70 build also mounts `vitaliineibauer/biohub-ft-weights`** (`experiments/exp70a_k2_lp30/kernel-metadata.json`), so a V* final depends on it too | standing | `CONTEXT.md` l.2249-2252 |
| W93 | standing, until 29 Sep 23:59 | Never push or submit exp65 / exp66. Never push `experiments/_pytest_oc_k2` (`biohub-zz-oc-k2`, W114). Never submit the dry-run kernel `biohub-exp63-succ-dryrun-raunakdey07` | standing | `CONTEXT.md` l.2223-2226, l.2397-2398 |
| W19 / W73 | until **29 Sep 20:00** | ONE poller. Before any submit, the last **successful** header (not a 429 line) must be < 15 min old.<br>- A 21.6-min gap already happened at 20:26:49 -> 20:48:26Z.<br>- **Two python PIDs are alive (20052, 34844). Confirm only one is `lb_poll.py`** | in progress (last header 20:58:27Z) | `experiments/lb_poll/poll.log`; `round12/report.json` new_facts (4) |
| T40 (= W124) | **26 Sep 23:50Z (hard)** | The last submit time for tonight's 3 slots. Unused slots do not carry over | - | `CONTEXT.md` l.2413 |
| T41 | **~22:30Z** | Round 13: P1 check, ladder compliance audit, W113-W122 verification | - | `round12/report.json` next_focus |
| T18 / T42 | **27 Sep 00:00** | Slot reset: 5 slots for 27 Sep. 00:05Z is exp70b or an error resubmit (W125) | - | `CONTEXT.md` l.2351, l.2413 |
| T42b | **~02:00Z** | The latest P1 check the v1 cadence allows (round 12) | - | `round12/report.json` R12-A2 (1) |
| T43 | **27 Sep ~04-08Z** | The first ladder scores arrive (K2-family latency 7.36-7.54 h). The overnight LB burst also lands ~07-09Z (I102) | - | `reach0955/r_ladder.json` L8; `round11/report.json` R11-A8 |
| T44 (= W120) | **27 Sep 07:30Z** | Morning push (needs the W119 timer) | - | `round12/report.json` R12-A6 (2), R12-A7 |
| T45 (= W126) | **27 Sep 08:00-09:00Z** | L5 informed combos, submitted by 09:00Z and scored ~16:30Z | - | `reach0955/r_ladder.json` L5 |
| T38 | **27 Sep ~09:00** | Last moment for an SI opt-in | - | `round11/report.json` R11-A3 |
| T03 | **27 Sep 12:00** | **R8.** No new mechanism after this. Also due now:<br>- the E10 v2 OK deadline (W120);<br>- the wake answer;<br>- lessons (W98);<br>- any retrain go (W128).<br>Ladder rungs are existing mechanisms, so R8 does not stop them (v_ladder (8)) | - | `CONTEXT.md` l.1671-1672, l.2352 |
| T32 / T39 | 27 Sep 12:00, 15:00, 18:00, 21:00 (timer 2bd08ad3 at hh:04) | Post-R8 E10 P1 checks: snapshot, poller header, API SELECTED, Chrome connected | timer set (l.2362) | `CONTEXT.md` l.2362-2367 |

## LATER (27 Sep 21:10 -> 29 Sep 23:59 UTC, and after)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T32 / T39 (cont.) | 28 Sep 00, 03, 06, 09, 12, 15, 18 and 21; **29 Sep 00:00** (the last) | E10 P1 checks (timer 2bd08ad3, to be replaced by W119) | `CONTEXT.md` l.2362-2364 |
| T46 (updates T04) | **28 Sep 12:00** | **F1-final consolidation is due** under R8 (l.1671). Since the ladder, it is no longer "empty by rule": the informed combos must be decided by then (R12-A3 (c)) | `CONTEXT.md` l.1671; `round12/report.json` R12-A3 |
| T28 | 28 Sep | S14: an x138 successor on a late trigger (P7) | `CONTEXT.md` l.1616 |
| T19 / W77 | **28 Sep 17:57** (timer 012fa6dd) | API SELECTED plus the FIRST logged page read of the ticks | `CONTEXT.md` l.2365 |
| T35 | 28 Sep 22:00 | The plan's "final admission table" (`FINAL_REPORT.md` l.178). Now it has real content: the L9 eligibility table for every ladder variant | `research/wf_ideas_v3/FINAL_REPORT.md` l.178; `CONTEXT.md` l.2418-2424 |
| T20 | **29 Sep 00:00** | The last slot reset and the last useful E10 trigger. The dummy must be terminal by 01:45Z (V3) | `CONTEXT.md` l.2355 |
| T29 / T47 | **29 Sep 02:00** | The last E10 port submit, and **the last ladder submit under R8**. L9 / L8 say 11:00Z, which breaks R8 (the hard edge is 10:00; a score would land ~18:30Z) unless the user lifts R8 (W120 (3)) | `CONTEXT.md` l.1671-1672, l.2416; `round12/report.json` plan_issues (2) |
| T09 / W77 | **29 Sep 11:57** (timer 328f7392, push) / **17:57** (18ff4796) | Remind the user to check or re-tick. API SELECTED | `CONTEXT.md` l.2365-2366 |
| T48 (= W131) | **29 Sep ~19:00** | **L9 read.** V* = the highest display >= 0.955 that is COMPLETE, has L_hi <= 9.0 h (W127) and has every single knob >= 0.954. Pair = {V*, #38}, otherwise {#37, #38}. An E10 port uses the reconciliation table (W116). Never two byte-identical files. Tell the user the exact two refs to tick | `CONTEXT.md` l.2418-2424 |
| T10 | **29 Sep 20:00** | Ticks final: exactly 2 files. Without a re-tick, {#37, #38} stays. **Stop the poller** | `CONTEXT.md` l.2356, l.2424 |
| T49 | **29 Sep 23:00 / 23:27** | The latest time to commit W122. Timer (W119 (3)) for the final public LB snapshot to `experiments/private_read/` | `round12/report.json` R12-A9 (d), R12-A6 (3) |
| T11 | 29 Sep 23:59 | Competition deadline | - |
| T30 / T50 | **30 Sep from 00:15Z, hourly** | Private read per W122 (d):<br>- C1-C5;<br>- rank read over the SELECTED pair;<br>- whether the 16:54 forecast was for a different pair;<br>- LESSONS s5 and CONTEXT §11.<br>The conditional K1 late-sub arm needs its own OK | `CONTEXT.md` l.2288-2300, l.2324-2334; `round12/report.json` R12-A9 |
| W123 (= R12-A10) | s5 parts with W122; the rest by 30 Sep | LESSONS/IDEAS curator pass:<br>- the corrected oracle sentence;<br>- G0-FT / G0-SCR plus a seed null;<br>- the I-222 bound ~+0.005;<br>- the I-034 / I-033 / I-147 / I-148 wording | `round12/report.json` R12-A10 |
| W29 | after 29 Sep | Post-deadline list: R10-A5 (g), plus round 11 and round 12 (G0 split, detector program only, I-113 wording) | `round10/report.json` R10-A5 (g); `round12/report.json` R12-A10 (2) |
| W102 (cont.) | until the private LB is final | Keep the finals' inputs intact, including every file a ticked V* mounts | `CONTEXT.md` l.2249-2252 |

**Done, superseded or moot since 17:40Z (for the record):**
- W103 and W104 are done in 96ccff7 (20:50Z):
  - `round11/REPORT.md` is tracked;
  - the ROUND 11 RECORD is at l.2342-2351 and deletes the duplicate 1701Z-2 snapshot;
  - the slot line 3/5/5/5 is at l.2351.
- W105: the proposal is at l.2352-2361 (done). The OK moved to W120.
- W107 is done in 13a27a1 (l.2362-2367): timers 2bd08ad3, 012fa6dd, 328f7392 and 18ff4796.
- W109 is done in cc0d57c (l.2397-2406): full gate PASS, and trigger-to-ready takes ~45-60 min.
- W110 is done by curation 11 (`research/KNOWLEDGE/IDEAS.md` l.22-25).
- W111 is done: the 20:01Z check, and the workflow edit in 13a27a1.
- W112 is superseded by W120.
- T17 is superseded: the 3 slots on 26 Sep go to the ladder (l.2389-2390).
- T27 is superseded: a ladder variant can become a final (L9).
- T12 lapsed at 18:00 (M6) and was never logged.
- Earlier records: `_curation/11/watch.json`, `_curation/10/watch.json`.

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| I107 | The runtime ledger maps only exp56/57/58/59/61/62/63/51/52 (l.69-77). "exp70" and "exp72" match no rule and land in `"unknown": ... "family unknown (pass --family)"`. r_retrain noticed it for exp72 ("token exp72 is unmatched -> pass --family exp72=safetail"); nobody noticed it for the ladder | `tools/runtime_ledger.py` l.66-77; `reach0955/r_retrain.notes.md`; `experiments/lb_poll/lb_poll.py` l.6 | L9 eligibility needs L_hi from this tool. Without `--family`, `ledger.md` shows "n/a" for every rung (W127) |
| I108 | **Name clash:** r_retrain RT-1 names its training kernels "exp70a = all 199 videos ... exp70b = 44b6-only". The ladder already owns `experiments/exp70a_k2_lp30`, `exp70b_k2_fm45` and the Kaggle ids `biohub-exp70a-k2-lp30` / `-exp70b-` | `reach0955/r_retrain.json` RT-1; `experiments/exp70*/kernel-metadata.json` | If the retrain line starts, reuse would collide in folders, ledger tokens ("first exp token") and RESULTS rows. Rename it first (e.g. exp71 / exp73) |
| I109 | v_ladder: "L9 as written: NO-GO. PAIR = {V*, twin #38} ... directly contradicts the user's logged 20:33Z decision (... default #37 K2)". The round-12 judge overruled this: "the user named no file". Both agree the user must see the trade-off in ONE line | `reach0955/v_ladder.json` no_go_items, corrections (3); `round12/report.notes.md` 'JUDGE CHECK' | If W116 is not logged before V* scores, the pair choice looks post-hoc. W120 (2) must carry the trade-off |
| I110 | "exp70a ... the gain over the current team best is ~min(lp, lowrefine effect) ... lowrefine refines exactly x138's readmit/gapfill pool ... lp30 removals are 95% readmitted leaves ... P(display >= 0.955) ~0.05-0.15, not 0.2-0.3" | `reach0955/v_ladder.json` corrections (1) | CONTEXT l.2412 keeps the plan's 0.05-0.15 caveat. The **non-additivity** of lp30 and lowrefine is not in CONTEXT. It matters for reading exp70a/e as a factorial |
| I111 | "dc x insertion interaction unmeasured": `div_insert.py` l.24-32 can RE-INSERT a fork that dc0.30 vetoed. Under dc0.30, 44b6 edge J goes 0.9054 -> 0.9042. The earlier pre-registered T9 gate for dc0.30 FAILED, and 0.35 is a cliff | `reach0955/v_ladder.json` corrections (2); `reach0955/r_ladder.json` L2 | exp70d/e are lab-FAILED knobs reopened only as public rungs (R12-A3 (a)). A 0.955 from them is a public-embryo read with the least lab support. Relevant to T48 |
| I112 | "A kernel version can be submitted only after it has run to COMPLETE and holds submission.csv ... A crash therefore costs the day's slot, and unused slots do not carry over" | `reach0955/v_ladder.json` no_go_items | The plan text "submit anyway if the dummy is not COMPLETE by 23:30Z" is infeasible. Budget ~40-50 min per dummy (v_ladder (4)) |
| I113 | "Our own record on model swaps is 0 of 5: exp08 secondary -0.016; friend A ep21 -0.025; exp23 FT -0.007; exp03B primary -0.003; soup -0.004". "+1% nodes ~ -0.001"; "G1 ratio up to 1.04 would pass the exact failure of exp23". y3uanm's public FT notebooks are QUICK SAVES that never ran | `reach0955/v_retrain.json` no_go_items, corrections 3, 7 | The honest prior for W128. It is not in CONTEXT (`CONTEXT.md` l.2383 still cites "y3uanm's public distilled secondary fine-tune, team 0.949 -> 0.956" as the route) |
| I114 | "x138 cell 1 = configuration guard: BIOHUB_DET_THRESHOLD must equal 0.965 ... else RuntimeError 'Configuration drift detected'" -> a DET_THRESHOLD rung CRASHES. Also: "'Secondary weight:' log line always prints /kaggle/working/... -> useless as a swap check; use 'Secondary artifact:' + 'Secondary SHA256:'" | `reach0955/v_intel.notes.md`; `reach0955/v_intel.json` no_go | CONTEXT l.2416-2417 records only the SECONDARY_* trap. The DET guard and the log-line pitfall are not recorded, so round 13's "at most 2 rungs" could pick a crash |
| I115 | GPU budget: "total ~8-11 GPU-h out of the final week's 30 h ... Read the Settings page first. If < 12 h remain, drop exp70b/G2". Weekly reset "expected 26 Sep 00:00Z" (l.2137), so the next is 3 Oct | `reach0955/v_retrain.json` corrections 8; `CONTEXT.md` l.2137 | Tonight's 4 ladder dummies, the dry run and the labs all draw on the same quota. Nobody has read Settings since the reset |
| I116 | The discussion agent's times labelled "Z" are **local time (UTC+3)**: "2026-09-26 ~23:40Z start", "~00:05Z 27 Sep", "no answer at 00:10Z". The file mtime is 23:50 local, and CONTEXT dates the read at 20:51 UTC | `reach0955/discussions_2026-09-26.notes.md`; `CONTEXT.md` l.2425 | Any later check of "Justin still unanswered" must convert: 00:10 "Z" = ~21:10Z 26 Sep |
| I117 | "'R7' in the 20:30-20:49 entries is the knob-ladder clause of R9 in PRE-REGISTRATION v3, where R7 is hygiene" | `round12/report.json` plan_issues (3); `CONTEXT.md` l.1665-1675 | Until W116 is logged, a reader could take "R7 lifted" to mean hygiene is lifted too (validator/PP sweep off, fail-soft, node-count identity) |
| I118 | "Dummy-CSV equality is NOT proof of hidden-test equality (4 visible clips vs hidden set)"; an identical dummy CSV sha means the knob did nothing on the visible clips, and a public tie is likely | `round12/report.notes.md`; `round12/report.json` R12-A3 (d) | This is the only cheap pre-submit check against the L7-type silent no-op. Record the result for each rung |
| I119 | Kaggle kernel API behaviour:<br>- "pages show the LAST SUCCESSFUL version";<br>- "kernels pull returns the LATEST source";<br>- "current_version_number does not move when a newer version errors";<br>- "kernels output <ref>/<N> ignores N";<br>- "an ERROR session still serves submission.csv" | `round12/report.json` new_facts (5) | The basis of W117's version binding. Without it, a port could take the errored newer source while scoring on the page's older one |
| I120 | "e10_port_gate exits 0 with SKIP lines, and its group summary hides a SKIP next to a PASS" | `round12/report.json` new_facts (7) | rc == 0 is not a pass. The gate grep (W117 (4)) is mandatory |
| I121 | "Our dummy CSV sha256 == author CSV == exp56 dummy (d52a5da2 ...), so x138 is byte-deterministic across accounts" | `CONTEXT.md` l.2404; `round12/report.json` new_facts (6) | A verbatim port ties its author exactly on public and private. That is why a port must be early (tie order by submit time, I98) |
| I122 | "Georgy Mamarin: a public-best improvement wins on private ~3 in 4 in code competitions"; hikaggler: "plain averaging did nothing"; imissher's LOST list includes "secondary weight 0.65" and "own/adapted secondary (0.939)" | `CONTEXT.md` l.2429-2436 | The 3-in-4 heuristic supports the public-aimed slot, but it comes from other competitions, not this metric. imissher's secondary loss matches I113 |
| I123 | "Lab annotation density: 0.79% of predicted nodes match GT on 44b6 vs 5.20% on 6bba" | `round12/report.json` new_facts (10), R12-A2 (6) | Node-count levers read very differently per embryo. Split every node-lever delta by embryo (R12-A10 (4)) |
| I124 | Discussion: "several players: LB moves with the predicted node count, not with local edge J". Justin went 0.953 -> 0.956 with PP/divisions only ("div J ~0.23") | `CONTEXT.md` l.2427-2433 | Round 13 (4) must test this against our node-drop audit (negative on the x138 lab, I105), not adopt it. Any node-cutting rung breaks R7 hygiene's "node-count identity first" unless it is declared |
| I96 | **Detection gap for E10 v2:** P2 flags only at `P2_MIN = Decimal("0.956")` (l.52), and the timer runs only the CLI snapshot | `tools/e10_snapshot.py` l.52; `CONTEXT.md` l.2363-2364 | Partly mitigated: round 12's browser agent read the Code tab by score (HF v3 0.953 first). The post-R8 timer has no page-score read. Relevant only if E10 v2 is OK'd |
| I82 | MEMORY is stale:<br>- disk l.8 says "only the E10 port rule ... is pre-approved; anything else needs a new OK";<br>- this curator's injected context says "(E10 port rule proposed; overlap-consensus line paused)".<br>Both predate the 20:33Z lift | `~/.claude/projects/.../memory/MEMORY.md` l.8 (mtime 16:35Z) | Subagents may refuse ladder work or treat it as unapproved. Fix in W121 |
| I72 | The harness again asks for a "Claude Opus 5.5" Co-Authored-By trailer; the user's rule forbids it | this curator's context; `memory/feedback-git-no-coauthor.md` | The last 12 commits pass (`git log -12 \| grep -ci claude` = 0). Keep that for W114 |
| I95 | **The harness has refused the round-report Write five rounds running** (8-12; round 12 at 21:01:01Z) | `round12/report.notes.md` | Structural. Each REPORT.md exists only if the main session extracts it (W113) |
| I97 / I98 / I102-I104 | The 0.953-block median of 25 submissions; late exact copies sit at the block end (now the **12th** window, ~20 teams #641-660, round 12); the overnight burst lands ~07-09Z; notify-and-wait at 00:00Z misses 02:00; P(successor >= 0.954) ~5-15% | `round11/report.json`; `round12/report.json` new_facts (2) | The basis for tie-order reasoning and W120 (1) |
| I99 / I100 / I101 / I105 / I106 | The builder's `--base` header; HF v3 is a clone; the DaughterNet load raises outside the fail-soft (so #37 **and every exp70 build** fail hard if `biohub-ft-weights` breaks); node-drop bonus 4.5e-6 vs cost 9.5e-5; 6bba misses are peakless | `round11/report.json`; `round11/scan_plancheck.json` PC11-09 | I101 now covers any V* too (W102) |
| I88 / I89 | x138's dormant ADAPTIVE_SHORT_TRACK_RESCUE (fires at >= 10% MIN_TRACK_LEN removal) is not in CONTEXT (`grep` = 0). A primary swap under x138 fails silently | `research/KNOWLEDGE/IDEAS.md` l.293, l.235 | lp30 removes nodes **before** linefit (v_ladder notes: "cell7 prune_weak_leaf_nodes ... after short-track filter"). Check that no rung pushes a clip across the 10% switch (unmeasured) |
| I69 | "public = one embryo" is a participants' guess, not a host fact | `round8/v_hypotheses_r8h-1.json`; `research/discussions_summary.md` l.4-6 | Still stated as fact in LESSONS l.7 (W98), and relied on by L9's 1/6 transfer and the ladder reads |
| I77 / I78 / I79 / I83 / I47 / I51 / I39 / I44 | Blend-switch 33.1% of 44b6 frames; FN/FP division anatomy; delete-node deltas; DeepCenter trained on 44b6 only (**now load-bearing for exp70d**, see r_ladder L2); the edge-FP rule; efpost; the l.22 error; unadapted features | `round9/report.json`; `round6/report.json`; `round5/report.json`; `round9/scan_hypotheses.json` r9h-3 | The W57 family. The DeepCenter-44b6 fact is now cited in `reach0955/r_ladder.json` L2 but is still not in CONTEXT |
| I01-I09, I14-I29, I34, I46, I52-I54, I64-I68, I71, I73, I76 | Older lens and round insights, unchanged since curation 11 | `_curation/11/watch.json`; `research/wf_ideas_v4/lens_*.json`; `round2`-`round8/*.json` | Post-deadline and §11 lessons |

**Resolved since 17:40Z:**
- I85, I90 and I92 were recorded earlier.
- I86 and I87 were resolved earlier.
- I93 is moot.
- Details: `_curation/11/watch.json`.
