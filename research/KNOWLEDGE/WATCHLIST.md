# WATCHLIST: overdue, next 24 h, later, insights at risk

Curated 2026-09-26 08:50 UTC (curation 7). This is an incremental update of the curation-6 build from 06:25 UTC.

Sources:
- `CONTEXT.md` §14 up to the 08:27 UTC entry (l.2058-2095). The new entries are:
  - v4 at l.2058-2069 (64f0551, committed 06:31:36Z).
  - The score read at l.2070-2081 (b4144e9).
  - The user's option "b" at l.2082 (7107b6d).
  - The wave check at l.2083-2095 (4d0c477).
- Git HEAD is 4d0c477. `poll.log` and `ledger.md` are modified and uncommitted, and `research/wf_ideas_v4/round7/` is untracked (`git status`, 08:47Z).
- `research/wf_ideas_v4/round7/report.json` (written 08:45:40Z): R7-A1..A8, new_facts, plan_issues, rejected, next_focus and `e10_port_rule_text`.
- `experiments/lb_poll/poll.log` (last header 08:44:25Z, l.4166) and `experiments/RESULTS.md` l.70-71.
- The memory files (`MEMORY.md` mtime 02:13Z; `project-lb-probe-approval.md` mtime 07:36Z).
- `tasklist` at 08:48Z: python PID 20052 (the poller) is alive, and PID 13436 is gone (stopped, `CONTEXT.md` l.2080-2081).

All times are UTC. The IDs are stable: W = action, T = time-bound reminder, I = insight. Status values: done, in progress, overdue, not started, cancelled.

**State in one line.**
- **The finals are decided:** #37 K2 = exp58 (56563521) = **0.954**, L in (7.36, 7.54] h, CLEAN, R5(a); #38 twin = exp58n (56563534) = **0.953**, L in (6.69, 6.87] h, R5(a). By READ TABLE row 3 the pair is {#37, #38} (`CONTEXT.md` l.2070-2081; `RESULTS.md` l.70-71).
- **The finals are NOT TICKED:** the API SELECTED group returned 0 at 08:32Z and 08:37:15Z, and the page showed 0/2 at ~08:34Z (`round7/report.json` new_facts 4, plan_issues 1).
- The user chose option **(b)**: full research rounds every ~2.5 h until R8, 27 Sep 12:00 (`CONTEXT.md` l.2082).
- LB: #183 at 08:22Z, #185 at 08:38Z. The silver line (~196) is 11-13 ranks below us, and we lose ~8 ranks/h (`CONTEXT.md` l.2083-2085; `round7/report.json` new_facts 1).
- E10 is NOT triggered (`CONTEXT.md` l.2093-2095).

**Contradiction to fix in the chat.** The plan table the main session sent at ~08:2x ends the E10 watch at 27 Sep 12:00, gives P(trigger) as ~15-20%, and puts us at "162nd place". The pre-registration keeps the E10 successor watch alive after R8 (S8 on 27 Sep, S14 on 28 Sep, `CONTEXT.md` l.1611, l.1616; C10 "until 29 Sep 07:00", `round7/report.json` plan_issues 2). R8 caps it at the last port submit, 29 Sep 02:00 (`CONTEXT.md` l.1671-1672). Round 7 puts P(trigger) at ~5-10% (new_facts 3), and the rank is now #185. Send the one-line correction with W74.

**Changes since 06:25:**
- Done:
  - W62: v4 (l.2058-2069) was committed at 06:31:36Z, before the first result at 06:54:06Z (l.2071-2072).
  - W47: the mechanical read (l.2070-2081).
  - W64: poll.log and ledger were committed in b4144e9.
  - W61: the user gave no OK on the 04:04 list, so strict text applied (l.2072-2073).
  - W35: RESULTS rows l.70-71 are filled.
  - W60 for round 6: REPORT.md is in 64f0551.
  - W67: round 7 ran (`round7/report.json`).
- Cancelled or moot:
  - W65 K2'', T25, T13-T16, T21 and T24, because K2 was clean (l.2074).
  - W55: the clean-proof job was stopped as moot (l.2080-2081).
  - W63: superseded by the score message and the user's reply at 08:21 (l.2082).
  - W04: superseded by the score read.
  - W53: moot, because both files COMPLETE with no error.
- **W54 (the tick) is now OVERDUE**, since the score read at 07:35 asked for the tick "NOW".
- New from round 7: W69-W78, T28-T33 and I56-I63.

---

## OVERDUE

| ID | Item | Status | Deadline | Evidence |
|---|---|---|---|---|
| W54 | **THE USER TICKS EXACTLY TWO FINALS: #37 56563521 'probe 37: exp58' (00:02:12Z) + #38 56563534 'probe 38: exp58n' (00:02:18Z).** With 0/2 ticked, Kaggle auto-selects from the 0.954 tie (#37, #35, P36), which could give P36 + #35, a pair the rule forbids.<br>After the user says "отметил":<br>1. Run the `tick_check_cmd` from `round7/report.json`. It must print `[56563521, 56563534]`.<br>2. The first time, also confirm with a page read or a screenshot. The SELECTED filter has never yet been seen returning a positive.<br>3. Log "FINALS TICKED 2/2: 56563521 + 56563534 (seen hh:mmZ, API+page)" in CONTEXT.<br>Never tick #34, #35, P36, or two files with identical components | **overdue** (API SELECTED = 0 at 08:37:15Z; `grep -c "FINALS TICKED" CONTEXT.md` = 0) | NOW (plan end 29 Sep 20:00) | `CONTEXT.md` l.2079-2080, l.2034-2038; `round7/report.json` R7-A1, plan_issues 1 |
| W74 | **One message to the user (R7-A7, `user_message_ru`), sent once in the chat, plus an optional push.** It carries:<br>1. Tick now (W54).<br>2. **The correction:** the E10 watch runs to 29 Sep 00:00, not 27 Sep 12:00; P(trigger) is ~5-10%, not 15-20%; the rank is now #185.<br>3. The conditional yes for the E10 PORT RULE (W69).<br>4. Public silver will likely slip today; this is expected and needs no action.<br>5. Durable 29 Sep 12:00/18:00 reminders in the user's calendar (W50) | not started | now, with W54 | `round7/report.json` R7-A7, plan_issues 2, 7, new_facts 1, 3 |
| W57 / W66 / W31 / W72 | **Curator records by 26 Sep 12:00**, for rounds 5, 6 and 7. Still open:<br>- `CONTEXT.md` l.22 still says "GT still moving" (I39).<br>- B5 at l.196 still lacks the AdaBN / unadapted-feature blocker (I44).<br>- Round 6: the official edge FP rule, efpost as a neutral FACT, and stitch and linefit CLOSED (I47, I51, I52).<br>- Curation 3: I-151, hysteresis, the calibration rule, "tail saturated", and the M6 lapse.<br>- **Round 7:** paste `records_text` (R7-A5) with the skeptic-corrected wording: ~3.65k unevaluable pairs (not ~3.9k); the node-miss FACT is the z-offset excess, not an "identity class"; the headroom ideas are closed on value, LB and R8 (not on runtime); forkmid is the one power-limited closure | not started (`grep -c` in CONTEXT: I-151 = 0, hysteresis = 0, efpost = 0, out_valid = 0, "ROUND 7" = 0) | **26 Sep 12:00** (3 h left) | `CONTEXT.md` l.22, l.196, l.2048; `round6/report.json` R6-A6; `round7/report.json` R7-A5, rejected 6-8 |
| W60 / W75 | **Save round 7's `report_md_ru` verbatim as `research/wf_ideas_v4/round7/REPORT.md`**, then commit round7/, poll.log and ledger.md with the next CONTEXT entries (R7-A2, A3, A5). Commit as the user with no Co-Authored-By trailer, and push. `round2/REPORT.md` is still missing (low priority) | round6 done (64f0551); round7 not started (untracked; the harness refused the subagent's REPORT.md write) | with the next CONTEXT commit (today) | `round7/report.json` R7-A8, report_md_ru_note; `round7/report.notes.md` 08:45:40Z |
| W03 | **The friend A card is stale.** The top block of `PROMPT_FRIEND_A.md` (25 Sep ~14:30) still points to cancelled tasks. Add a "finals #37 + #38; nothing to do before 29 Sep" block, as was done for friend C | overdue (last change fea74ea, 25 Sep 13:41Z) | now (not urgent) | `PROMPT_FRIEND_A.md` l.1-3; `PROMPT_FRIEND_C.md` l.1-4 |
| W05 | Commit `experiments/ext_corwin-biocel-aux/` and `experiments/ext_y3uanm-secondary-ft/` without `__pycache__`. Also delete the stray `bash.exe.stackdump`, or leave it untracked | overdue (both still `??` at 08:47Z) | 25 Sep | `git status` |
| W02 | Friend A "Task 0" reply | overdue, and moot (no lab or rider work remains) | 25 Sep 18:00 | `research/wf_ideas_v3/TASK_FRIEND_A.md` l.17-22 |

## NEXT 24 H (26 Sep 08:50 -> 27 Sep 08:50 UTC)

| ID | When (UTC) | Item | Status | Evidence / rule |
|---|---|---|---|---|
| W54 / W74 | **now** | See OVERDUE | overdue | `round7/report.json` R7-A1, R7-A7 |
| W69 | **today, before ~19:00Z and before any trigger** | **E10 PORT RULE:**<br>- Paste `e10_port_rule_text` (P1-P7) as a dated CONTEXT entry.<br>- Ask the user for ONE conditional yes, and log the reply with `date -u`. It counts as pre-registered only if it comes before a trigger.<br>- Content: {port, K2 #37} as the pair, with the twin leaving. §f(iii) (C01 in F1) is waived for the port only [OK]. Adopt iff there is no error, L_hi <= 7.5 h and public >= 0.956. Never {port, twin} and never port + #34.<br>- Without the yes: on a trigger, notify the user and wait | not started (`grep -c "E10 PORT RULE" CONTEXT.md` = 0; `covered_by_existing_approval: false`) | `round7/report.json` R7-A2, plan_issues 3, `e10_port_rule_text` |
| W70 | with W69 (today) | **Post-score RESUME POINT:**<br>- Paste `resume_point_text` into CONTEXT, with the tick status filled in.<br>- Update `MEMORY.md`: l.9 should name the new block, and l.8 should say "finals #37 + #38 decided; no standing submit approval except the E10 PORT RULE if OK'd". It still lists "gated riders K3/K3b/K4/N1", all closed.<br>This absorbs W34 | not started (the newest RESUME POINT is still the pre-score 00:02Z block, `CONTEXT.md` l.2006) | `round7/report.json` R7-A3, plan_issues 4; memory `MEMORY.md` l.8-9 |
| W71 | **before round 8 (~11:00Z)** | **Round-prompt focus text.** Edit `experiments/workflows/biohub-research-round.js`:<br>(a) Add a hard line: a new mechanism must be submittable by 27 Sep 12:00 with an honest lab gate, a dummy and a new OK. After ~26 Sep 22:00Z, rounds cover E10 intel, finals hygiene and lessons only.<br>(b) Append the round-7 closures to the do-not-repropose list.<br>(c) Remove the stale "~4 h headroom", which is still at l.35 and l.36 | not started (grep "4 h headroom" = l.35-36) | `round7/report.json` R7-A4, plan_issues 5 |
| W19 / W73 | **until 29 Sep 20:00** (was "until both terminal") | Keep ONE poller instance, `lb_poll.py` (PID 20052). The v4 W6 stop condition for #37/#38 is met, but a possible E10 port needs coverage to submit + 7.5 h, and the tick period runs to 29 Sep 20:00. Before any submit, check that the last poll.log header is < 15 min old | in progress (alive 08:48Z; last header 08:44:25Z) | `round7/report.json` R7-A6, rejected 9; `CONTEXT.md` l.2064 (W6) |
| W23 | rounds every ~2.5 h until R8; then P1 light CLI checks every ~6 h until **29 Sep 00:00** | **E10 successor watch.**<br>- Last check 08:22-08:38Z: NOT met. No public kernel run since 25 Sep 09:09Z; x138 is still v1; kabirk22/biohub3 is train tensors only.<br>- The `kragglenote2forwork/biohub-sub-cache2` leaked CSVs stay UNUSED.<br>- `amanatar/optimized-biohub-max-score` is rejected under R7.<br>- Use the CLI change detector (P1). The kernel API has no score field, so open the browser only on a change | in progress | `CONTEXT.md` l.2083-2095; `round7/report.json` new_facts 3, `e10_port_rule_text` P1-P2 |
| W76 | **~11:00Z** (round 8), then ~13:30, ~16:00, ~18:30, ~21:00, ~23:30, ... up to 27 Sep 12:00 | **Research rounds (option b).** Round 8 focus, per `next_focus`:<br>1. The tick status by API.<br>2. Check that R7-A2/A3/A5 were committed and REPORT.md saved.<br>3. The E10 CLI delta vs 08:22Z.<br>4. An E10 dry run with no push, on an already pulled notebook (`experiments/ext_biohub-harmonic-fusion-v3` or `ext_optimized-biohub-max-score`): time the P3-P5 steps.<br>5. The curator by 12:00.<br>6. The last call for new mechanisms (new OK, R8).<br>From ~22:00Z, rounds cover E10 intel, hygiene and lessons only | round 8 not started | `CONTEXT.md` l.2082; `round7/report.json` next_focus |
| W50 | ask **now** (in W74); reminders in place **by 28 Sep** | Durable 29 Sep 12:00 and 18:00 reminders that survive this session: in the user's own calendar, or a cloud routine only with a new OK | not started (no evidence in CONTEXT) | `CONTEXT.md` l.2037-2038; `round7/report.json` R7-A7 (5) |
| T26 | **~26 Sep 12:00 onward (today)** | The public silver line (~rank 196) will likely pass us today through others' gains. Info only (R7): nothing reacts to it. Public is one embryo (~29%) | watch | `round7/report.json` new_facts 1, plan_issues 7 |
| T12 | **26 Sep 18:00** | The M6 reopen window for K4/tempfuse lapses (and round 6 refused K4 = K2 + efpost). Note the lapse with W31 | pending (expected lapse) | `CONTEXT.md` 20:55 (M6); `round6/report.json` rejected 3 |
| T17 | 26 Sep, until 23:59 | 3 unused slots on 26 Sep. They stay EMPTY unless E10 triggers and passes P3-P6 with the user's yes | - | `CONTEXT.md` l.2081; `round7/report.json` `e10_port_rule_text` P7 |
| T27 | **~26 Sep 22:00** | After this, no round idea can become a final: an R8 submit by 27 Sep 12:00 needs a lab gate, a dummy, a build, a new OK and a slot | - | `round7/report.json` plan_issues 5 |
| T18 | **27 Sep 00:00** | Slot reset: 5 slots for 27 Sep (S8 = E10 port only by trigger) | - | `CONTEXT.md` l.1611 |
| W59 | optional, any time | `tools/runtime_ledger.py` text fixes (A6, A5 ask, F = 7.87 h, generic keep-until line). Now cosmetic. If done, map the `exp63` token to the x138 7.5 h family, then run `python -m pytest tests/test_runtime_ledger.py`. No poller restart is needed | not started, low priority | `round7/report.json` R7-A6, plan_issues 6 |
| W26 | any time 26 Sep | Record in CONTEXT that day-2 cloud research (`NEXT_RESEARCH.md`) is cancelled; option (b) rounds replace it | not started (`grep -c NEXT_RESEARCH CONTEXT.md` = 0) | `research/wf_ideas_v3/NEXT_RESEARCH.md`; `CONTEXT.md` l.2082 |

## LATER (27 Sep 08:50 -> 29 Sep 23:59 UTC)

| ID | When (UTC) | Item | Evidence |
|---|---|---|---|
| T02 | 27 Sep ~09:00 | LB snapshot and rank line (info only). Compare with #185 at 08:38Z on 26 Sep | `round7/report.json` new_facts 1 |
| T03 | **27 Sep 12:00** | **R8: no new mechanisms after this, and the end of the full research rounds (option b).** The E10 port of a PUBLIC successor stays possible (S8/S14; P1 CLI watch continues) | `CONTEXT.md` l.1671-1672, l.2082; `round7/report.json` plan_issues 2 |
| T04 | 28 Sep 12:00 | S12 consolidation. **Moot:** no rider passed, and K2 is already the final | `CONTEXT.md` l.1614, l.2081 |
| T05 | 28 Sep 16:00 | S13 (moot) | `CONTEXT.md` l.1615 |
| T28 | 28 Sep | S14: an x138 successor on a late trigger (E10 PORT RULE P7) | `CONTEXT.md` l.1616; `round7/report.json` `e10_port_rule_text` P7 |
| T19 / W77 | **28 Sep evening** | Re-run the API tick check (it must print `[56563521, 56563534]`) and confirm the refs (checklist step 1). The W50 reminders must exist by now | `round7/report.json` R7-A1, `tick_check_cmd`; `CONTEXT.md` l.2038 |
| T20 | **29 Sep 00:00** | Last slot reset. It is also the **last useful E10 trigger** (a port needs ~7.5 h) | `round7/report.json` plan_issues 2, `e10_port_rule_text` P7 |
| T29 | **29 Sep 02:00** | The last E10 port submit, and the start of R8's "emergency repeat only". The hard edge is 10:00 (S17) | `CONTEXT.md` l.1617, l.1671-1672 |
| T09 / W77 | 29 Sep ~11:30 / **12:00** (backup **18:00**) | 11:30: draft the tick check. 12:00 and 18:00: re-run the API SELECTED check, and remind the user to CHECK the ticks (these should already be set by W54) | `CONTEXT.md` l.2036-2038; `round7/report.json` R7-A1 |
| T10 | **29 Sep 20:00** | The ticks are final: exactly 2 files, matched by ref and date. Default {#37 56563521, #38 56563534}.<br>- If an E10 port is adopted under P6 (with the user's yes), the pair becomes {port, #37}.<br>- Never tick #34, #35 or P36; never two identical files; never auto-select.<br>This is also the **poller stop** (R7-A6) | `CONTEXT.md` l.2038, l.2079-2080; `round7/report.json` `e10_port_rule_text` P6, R7-A6 |
| T11 | 29 Sep 23:59 | Competition deadline | `CONTEXT.md` §1 |
| W29 | after 29 Sep | Post-deadline work:<br>- E14: friend A's honest out-of-embryo A/B.<br>- Linker item #1: the post-freeze re-solve plus efpost (I39, I51).<br>- Axial localisation of z-elongated nuclei in 6bba (I57).<br>- Lessons for §11 (I53) | `TASK_FRIEND_A.md` "Задача 4"; `CONTEXT.md` l.2048 (3); `round7/report.json` records_text (4) |

**Done or cancelled since 06:25 (for the record):**
- W62 done: v4 is at `CONTEXT.md` l.2058-2069. It was committed in 64f0551 at 06:31:36Z, before the first result at 06:54:06Z (l.2071-2072).
- W47 done: the mechanical read (l.2070-2081).
- W64 done: b4144e9 committed poll.log and ledger.md.
- W61 done: no user OK on the 04:04 list; strict text only (l.2072-2073).
- W35 done: `RESULTS.md` l.70-71. An exp60 one-liner is still absent (`grep -c exp60` = 0; optional).
- W67 done: `round7/report.json`, 08:45:40Z.
- W10 done: round 6, committed in 64f0551.
- Cancelled:
  - W65 (K2''), T25, T13, T14, T15, T16, T21 and T24: K2 was clean at 7.54 h, and the trigger never fired (l.2074, l.2081).
  - W55: the clean-proof job was stopped as moot (l.2080-2081).
  - W63: superseded by the score message and the user's option (b) reply (l.2082).
  - W04: superseded; the 07:35 entry holds file, public, L, R5 and pair.
  - W53: moot (both files COMPLETE with no error).
  - W34: absorbed into W70.
- Earlier: W44-W49, W56, W58, W33, W22, W28, W06, W14, W16, W36-W41, W01, W08, W09, W11, W12, W17 and W30. W07, W13, W24, W27 and T01 were cancelled (`research/KNOWLEDGE/_curation/6/watch.json`, `_curation/5/watch.json`).

## INSIGHTS AT RISK OF BEING FORGOTTEN

| ID | Insight (quoted or close paraphrase) | Where | Why it matters / plan gap |
|---|---|---|---|
| I56 | **"Kaggle API: finals ticks are readable via competition_submissions(group=SubmissionGroup.SUBMISSION_GROUP_SELECTED): 0 at 08:32Z and 08:37:15Z"**. Also: "the filter has not yet been seen returning a positive" | `round7/report.json` new_facts 4, R7-A1, `tick_check_cmd` | The only machine check of the ticks. It is not in CONTEXT yet (it is in `records_text` (2)). The 29 Sep checks (W77) depend on it, and the first positive needs a page read |
| I57 | "668 missing GT nodes (1,211 FN edge-ends): merges 31 (4.6%), pruned by the tail 80 (12%), absent upstream 557 (83%); 71% have a final node at 7-10 um; those are z-dominant 41% vs 25-28% in a matched control (axial offset excess), 91% in 6bba. The '96% unclaimed' figure equals the annotation base rate and carries no information" | `round7/report.json` new_facts 7, rejected 7; `records_text` (4) | The best post-deadline lead: axial localisation of z-elongated nuclei, which agrees with I22 and I53. The warning "do not write 'identity class'" exists only in the skeptic fix |
| I58 | "gap LAP g=1..3 + sandwich: g1..3 TP 5 / FP 458 < 20 um ... ceiling <= ~+0.0003 even at 100% precision (closed). x138's own synthetic gap/gap2/readmitted nodes match GT at ~1% (58/5,647, 29/2,968, 73/13,284)" | `round7/report.json` new_facts 6; `records_text` (3) | I-186/I-141 are closed by measurement. The 1% match rate of x138's synthetic nodes explains why they are "free" (unannotated) under the metric. Not in CONTEXT |
| I59 | "The overnight rise (subs 23:43-01:53Z) follows the 00:00Z quota reset + ~7 h latency (daily pattern, not a signal)"; "Bursts from submits made ~23:30-02:00Z ... are the daily pattern, not a signal on their own" | `round7/report.json` rejected 1, new_facts 2, `e10_port_rule_text` P2 | It stops a false E10 alarm every morning around 07:00-09:00Z. The 08:27 CONTEXT entry (l.2095) reads the burst as "private or Discord x138 variants" |
| I60 | "§f(iii) requires C01 in F1, which a verbatim port cannot carry (tools/build_probe_kernel.py BASES = exp39/x138 l.99; safetail exits unless --base x138 l.2026-2027); runtime_ledger maps an heir to 'unknown'" | `round7/report.json` plan_issues 3 | Without W69, a real E10 trigger would have no legal pair. The finals rule would then block the port as F1, and the pair would be picked after the score (post-hoc) |
| I61 | "forkmid is exactly [the only closure made for power alone] (only the >= 3 evaluable-FP clause failed; the other two clauses are evidence limits)"; "6bba-only replication ... P(pass) ~0.4, EV ~+2-4e-5 ... NOT run" | `round7/report.json` rejected 3-4, new_facts 8 | The one division idea with a favourable sign (+0.00013, div_J +0.0010) to revisit after 29 Sep. Keep F-TRN-11/F-TRN-22 unchanged |
| I62 | "a night trigger (user at UTC+3) can lose up to 8 h" | `round7/report.json` R7-A2 why | This is why the conditional yes must be asked BEFORE the user's evening (~19:00Z) |
| I63 | "RC-C runtime rationale ('8.0 h gate, slack >= 0.46 h < 0.58 h spread'): wrong - it compares a lower bound with a spread, and K2''-style deadlines give a 9.0 h gate" | `round7/report.json` rejected 6 | Use this correct wording in the lessons; the headroom ideas are closed on value, LB and R8 |
| I47 | **"Official edge FP rule: a predicted edge is scoreable iff its source matches a GT node with out-degree > 0 OR its target matches a GT node with in-degree > 0; a 'both ends matched' shortcut undercounts FP ~20x"** | `round6/report.json` new_facts 8; `tools/official/src/tracking_cellmot/metrics.py` l.165-194 | Still in no CONTEXT line (`grep out_valid` = 0). W66 (2) |
| I51 | "efpost ... 6bba +0.00174, 44b6 exactly 0, 32 TP / 107 FP evaluable dropped; kept as a FACT only"; "do NOT reword I-161/I-162/memory to 'public embryo has no frozen frames'" | `round6/report.json` new_facts 7, rejected 3, R6-A6 (5) | A post-deadline linker item (`grep -c efpost CONTEXT.md` = 0) |
| I52 | "stitch ... ceiling ~+0.0003 -> CLOSED"; "Linefit w0.7 win2 ... null effect, rider closed"; wording "'no detectable effect', not 'premise refuted'" | `round6/report.json` new_facts 7, rejected 9-10 | Needs W71 (b) and W66, or rounds 8+ will re-propose it |
| I53 | Lessons (R6H-7): "gains came from detection/localisation (insertion +0.001 twice, head +0.002), not the linker tail; in-sample ILP/edge-net trust and lab gains < ~+0.003 did not transfer; LB agreed with 5/5 lab kills; reproduce public notebooks first; runtime is a first-class risk" | `round6/report.json` new_facts 10 | For CONTEXT §11 after 29 Sep. Round 7 adds I57 (localisation) and I63 |
| I54 / I46 | Late x138 byte-copies land at the END of the 0.953 block (now the 7th window in a row: tie order = earlier submission). The silver margin went 41 -> 36 -> 34 -> **~11-13** ranks (00:47 / 03:16 / 05:46 / 08:22Z) | `round6/report.json` new_facts 2-3; `round7/report.json` new_facts 1-2 | This backs the rule against ticking #34. Rank is information, never an input (R7) |
| I39 | "Frozen GT steps have median 0 (GT copies positions on frozen frames; CONTEXT l.22 'GT still moving' is wrong for most)" | `round5/report.json` new_facts 17; `CONTEXT.md` l.2048 (3) | **`CONTEXT.md` l.22 is still wrong** (W57) |
| I44 | "The V1284 head (x138's +0.007), lowrefine and DaughterNet all read unadapted 224-d detector features; the node-count guard cannot detect feature drift" | `round5/report.json` new_facts 19 | B5 (`CONTEXT.md` l.196) still lacks this blocker (W57) |
| I34 | "The 44b6 '+0.0157' is one TP ... insertion +0.00648 pooled" | `round4/report.json` new_facts | `CONTEXT.md` l.1932 still quotes "+0.0157 / +0.0090" |
| I01 | "Of x138's forks, 24% (15/62 on the dummies) are one-blob duplicates at t+1, against 2% of GT divisions" | `research/wf_ideas_v4/lens_literature.json` plan_critique 1-2 | The main fact for division work after 29 Sep |
| I02 | "1 of 10 lab gains transferred ... a lab-based slot decision is allowed only for arms whose learned inputs are out-of-sample" | `research/wf_ideas_v4/lens_mine-old.json` plan_critique (4) | Not in CONTEXT; overlaps I53 |
| I04 | "7 of 17 44b6 picks are leak-siblings" | `CONTEXT.md` 14:29 (T5) | 44b6 lab deltas are partly in-sample |
| I06 | K2 dummy vs train GT: "FN 82 of 2,127 GT edges. 50% are swaps" | `lens_mine-old.json` critique (3) | Conflicts with I21/I22/I57 (the "swaps" are node misses). Reconcile after 29 Sep |
| I07 | "lowrefine is not a coordinate-only rider ... +33 final nodes, +29 edges and +1 fork" | `lens_redteam-plan.json` RT2 | Relevant to the lessons on d2 |
| I08 | Kernel time is not a hidden-test budget signal; use the per-dataset `[ds] repair` lines | `research/wf_ideas_v3/FINAL_REPORT.md` §j item 19 | For the E10 port P5 runtime read |
| I09 | "Блок 0.953 на private останется единым" is untested | `FINAL_REPORT.md` §g item 13 | See I54 |
| I14 | `TASK_LOCAL_SESSION.md` l.12 and `TASK_FRIEND_A.md` l.40, l.52 name branch `claude/practical-meitner-31k9ye`, but the work lands on `main` | those files | Same risk as W03 |
| I15 | "The public read over-rewards fork REMOVALS whose precision lies between the private break-even (0.11-0.20) and 0.265" | `round2/report.json` plan_issues (R2-RC-B) | Lessons |
| I19 | **DeepCenter t* = 0.30 is the lab optimum** in the removal direction, and it is NOT node-preserving (nodes -79/-49) | `experiments/exp60_trainlab/results.md` l.13-18, l.61-66 | CONTEXT l.1930 gives only the failed gates |
| I21 | "The x138 tail is saturated. Edge FN 1,705 of 40,093 = node misses 834 (49%), swaps 730 (43%), dangling ends 141 (8%)" | `round3/report.json` new_facts (13); `FACTS.md` F-TRN-15 | Not in CONTEXT (W31 (5)). I57 refines it |
| I22 | "There are 0 true 2x2 swaps ... our nodes sit 3.9-4.2 um from the GT nuclei" | `round3/report.json` new_facts (14); `CONTEXT.md` l.1974 | Agrees with I53 and I57 |
| I23 | "The CONFIRMATION half reads every node-adding arm as positive ... while the LB read MIN_TRACK_LEN 4 at -0.002" | `round3/report.json` R3-A8 (3) | Calibration rule not in CONTEXT (W31 (2)) |
| I24 | "Evaluable precision: sparse half 8 TP / 3 FP, dense half 1 TP / 3 FP ... q* = 0.114" | `round3/report.json` new_facts (11) | The case for the twin hedge (now F2) |
| I28 | "GT node recall before safe divisions -> final: t0 0.959 -> 0.940 ... boundary edge TP rate 0.926 vs 0.958" | `round3/report.json` new_facts (15) | Clip-boundary node loss; post-deadline |
| I29 | The retention guard has no flicker penalty: switch pairs 6.05% FN | `round3/report.json` new_facts (17); `FACTS.md` F-TRN-18 | Not in CONTEXT (W31 (4)) |

Resolved since 06:25:
- **I48, I49, I50, I55** (the B/B' runtime bound, the R5 F' line, K2'' as the likeliest decision, the table gaps): all are in v4 (`CONTEXT.md` l.2058-2069) and are moot since K2 was clean (l.2074).
- **I05, I26** (the risk of the insertion gate at 8.0 h, and the 7-10 h latency): answered by the measurement L(K2) in (7.36, 7.54] h (l.2074).
- **I12/I18**: merged into I54/I46.
- Earlier: I03, I10, I11, I13, I16, I17, I20, I25, I27, I30-I33, I35-I38, I40-I43 and I45.
