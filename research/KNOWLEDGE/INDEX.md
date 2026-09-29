# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 38: state as of 2026-09-29 ~10:50 UTC (13:50 MSK). Git HEAD 135788c ('Feed: 0.981 E10 flag is another competition', 10:00Z) after 66f1eeb (09:57Z ROUND 37 APPLIED) (`git log`). `CONTEXT.md` has 4,529 lines; newest entries l.4488-4508 (09:57Z ROUND 37 APPLIED R37-A1..A5; 10:00Z FEED E10 FLAG = FALSE POSITIVE); `## 9. Literature` l.4509. Uncommitted: `research/KNOWLEDGE/*` curation-38 edits, `experiments/lb_poll/ledger.md` / `poll.log`, e10 logs. Untracked: `research/wf_ideas_v4/round38/` (report.json R38-A1..A7, 4 scans, 17 verdicts, NO REPORT.md), `research/KNOWLEDGE/_curation/38/`, `experiments/e10_watch/20260929T1013Z.txt`, `20260929T1041Z.txt` (`git status`). Previous curation: 37 (~10:00Z). Times are UTC unless marked MSK (= UTC+3).
Deadline 29 Sep 23:59. The user ticks the finals MANUALLY by 20:00 UTC = 23:00 MSK; the session never ticks (`CONTEXT.md` l.3842-3855, l.4092). Rule anchors: PRE-REG v3 l.1576-1736 (R8 l.1671); GAP RULE v2 l.4009-4020; RULE v2.1 l.4104-4126; 08:19Z rule (a) l.4404-4414; 08:28Z slot-2 hold l.4433-4440; 08:51Z CLARIFY + SEC exception l.4441-4452; 09:00Z exp89t read rule l.4459-4470; 09:57Z R37 applied (S0 plan, card plan, slot-2 default) l.4488-4501.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged, weaker pair):** #37 exp58 = 0.954 + #38 exp58n = 0.953; recommended П3 {exp87a 56640366, #37 56563521}, П2 {exp87a, exp75} a trade; #38 stays out (R38-RC-C, P(x > 0) ~0.85); user re-ticks by 20:00 UTC (`DECISIONS.md` §2 [c38] l.999-1001; `FACTS.md` F-TRN-73 l.514).
2. **Best = P51 exp87a (K + CI) = 0.959 = V_pub.** Rank #141 of 3,991 at 10:42Z, 17th of 21 in the 0.959 block (125-145) (`experiments/e10_watch/20260929T1041Z.txt` l.1166-1168; `FACTS.md` F-LB-38 l.271).
3. **No new LB score since curation 37.** Last reads: P53 exp75 0.955 clean, P52 exp89r 0.957 (rule (a) not met, exp89s not sent) (`CONTEXT.md` l.4471-4487; `DECISIONS.md` §1 [c38] l.562).
4. **P55 exp89t (K + DIS 2.25 + CI, ref 56669888) still PENDING** at the 10:48:46Z header (L > 1.8 h); read window ~17:53-19:54Z, admit edge 19:45:17Z (22:45 MSK); most likely 0.959 = tie -> V_pub only with an attributable UP (`experiments/lb_poll/poll.log` l.30454-30457; `CONTEXT.md` l.4459-4470; `FACTS.md` F-TRN-72 l.513).
5. **Submits: 4 of 5 used today; slot 2 defaults to UNUSED** at the 11:50Z message / 12:00Z log (logged 09:57Z R37-A5); exp89s only on a new explicit user yes (`CONTEXT.md` l.4488-4501; `DECISIONS.md` §3 l.1787).
6. **Logged since c37:** 09:57Z R37-A1..A5 (user told, timer texts log-only, S0 plan with 17:40Z pre_exp89t job + 11:45Z mk_s0.py fallback, card plan, slot-2 default); 10:00Z feed 0.9812 flag = another competition, 'stacking' excluded in `tools/kaggle_feed.py` (`CONTEXT.md` l.4488-4508).
7. **Round 38 (10:38Z) proposals R38-A1..A7, none logged:** card v3 (A1), one 12:00Z CONTEXT entry (A2), slot-2-yes UP arming (A3), re-arm the 17:40Z save job (A4), exp89t read playbook T0-T8 (A5), 19:44:45Z manual-admit list (A6), KEY FACTS refresh (A7) (`research/wf_ideas_v4/round38/report.json`; `DECISIONS.md` §3 l.1789).
8. **Background:** e10 RUN 46 10:42Z 8/8, signals 0, loop ends 12:00Z (`experiments/e10_watch/watch_loop.log`); poller ~602 s cadence; armed pre_exp89t job pid 18408 (flawed, `FACTS.md` F-RUN-57 l.333); after 12:00Z only `tools/kaggle_feed.py` watches E10 (I-584).
9. **Next decision points (UTC / MSK):** 11:40Z card v3 ready; 11:45Z mk_s0.py; 11:50Z slot-2 message; 12:00Z UNUSED log + R38-A2 entry; 12:03Z/15:03 card v3; 13:13Z round 39; <17:40Z re-arm save job; <17:53Z playbook + 19:44:45Z script; 18:37Z FINAL card; 20:00Z/23:00 user tick; 23:59Z deadline (`WATCHLIST.md` l.61, l.85).
10. **Ideas 587** (lb-tested 65, lab-tested 28, refuted 273, deferred 50, in-plan 169, open 2); at-risk 16, strict orphan I-233 (`IDEAS.md` CHANGES (38) l.228, ORPHANS l.950).

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` = this page. `CHANGES.md` = per-curation deltas (v4, 2-38). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,38}/` (`*.json` answers, `*.notes.md` crash-safe logs).
- `IDEAS.md` + `ideas.json` (I-001..I-587): CHANGES (38) l.228, ranking l.241, FINALS l.260, LADDER l.357, BASE l.473, RUN l.517, LOC l.596, DIV l.632, MODEL l.705, NODES l.758, INFER l.796, EF l.818, LINK l.838, VALID l.876, TESTSET l.931, ORPHANS l.950.
- `FACTS.md`: state l.3; §1 metric l.192, §2 data l.209, §3 LB l.230 (F-LB-38 l.271), §4 runtime l.273 (F-RUN-57 l.333), §5 rules l.335 (F-RUL-38 l.376), §6 models l.378, §7 lab-to-LB l.438 (F-TRN-72/73 l.513-514), CONTRADICTIONS l.516 (C-304..C-314 l.823-833).
- `DECISIONS.md`: probes §1 l.144 (P55 l.207; [c38] l.562); finals §2 l.629 ([c38] snapshot l.1001); E10 §2f l.1268; ladder/cards §2h l.1454; R1-R10 §3 l.1653 ([c38] rows l.1787-1790); changelog [c38] l.2000.
- `WATCHLIST.md` (~10:45Z): DUE NOW l.61 (W346, T209, W347), CONTRADICTIONS l.71 (C10-C13, C7), NEXT 24 H l.85, LATER l.116, INSIGHTS l.141 (I419-I429).

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows to P46 only); `experiments/lb_poll/poll.log`, `ledger.md`; `experiments/e10_watch/watch_loop.log` + `2026*.txt`; `experiments/discussions/feed_loop.log`, `digest_*.md`, `744273.md` (Satwik).
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `exp58n_x138_safe_lowref/` (#38); V_pub `exp87a_k2cap6_div04_ra094_ci/`; pending `exp89t_k2cap6_k_dis225_ci/`; read today `exp75_k2_coordinject/` (0.955), `exp89r_k2cap6_k_sec_dis225_ci/` (0.957), `exp89p_k2cap6_k_sec/` (0.956); not sent `exp89s_k2cap6_k_dis225/`.
- Tools: `tools/uptest.py` (LB save / UP test), `tools/runtime_ledger.py`, `tools/build_probe_kernel.py`, `tools/dummy_gates.py`, `tools/kaggle_feed.py` (E10 watcher after 12:00Z); `experiments/lb_poll/e10_watch_loop.py` (END 12:00Z).
- Rounds: `research/wf_ideas_v4/round38/` (report.json, scan_plancheck / scan_hyp_exp89tread38 / scan_recheck / scan_browser, v_*); rounds 29-35, 37, 38 have no REPORT.md. Card template `research/wf_ideas_v4/round29/finals_card_v5_ru.md` (a134d5e4); filled blocks only in the scratchpad (`card_fill_1203_v2.txt` flawed -> v3). Background: `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v3/FINAL_REPORT.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` CHANGES (38) l.228 and ORPHANS l.950)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-583 | 12:03Z card v3 from v2: R37-A4 Satwik text verbatim (no 'довод'), fresh header/rank, SEC clause after 12:00Z, 22:45-23:00 MSK '?', 'tick now' line | At risk: ready ~11:40Z, send 12:03Z | R38-A1; `FACTS.md` C-304..C-307 |
| I-575 / I-579 / I-584 | 12:00Z entry: slot 2 UNUSED + R37-A6 addendum + timers as pointers + E10 policy after 12:00Z (verify + MSK push) | At risk: 12:00Z | R38-A2; `WATCHLIST.md` W347 |
| I-577 | exp89t S0: 11:45Z mk_s0.py fallback; re-arm the 17:40Z pre_exp89t job (newest non-error block, one retry) | At risk: before 17:40Z | R38-A4; `FACTS.md` C-308 |
| I-580 | exp89t read playbook T0-T8; log 'RECOMMENDED PAIR' before any MSK push after a promotion | At risk: before 17:53Z | R38-A5 |
| I-586 | Self-contained 19:44:45Z manual submissions list at the admit edge | At risk: arm before 17:53Z | R38-A6 |
| I-585 | Slot-2-yes UP-test arming (mid_<token> save, pre-read line) | Conditional: void if slot 2 UNUSED | R38-A3; `FACTS.md` C-309 |
| I-336 / I-252 / I-407 | Hindsight guard, H2/H3 lessons, cap-family private-read line (+ I-582 Satwik) before 23:00-23:59Z | At risk | `IDEAS.md` ORPHANS l.950 |
| I-233 | Poller logs error_description | Strict orphan, no owner | `research/wf_ideas_v4/round4/report.json` R4-A9 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/38/{ideas,facts,watch}.json`)

1. [now] **Card v2 is flawed -> card v3 (R38-A1):** `card_fill_1203_v2.txt` l.54 ends the Satwik line 'Это довод за страховку #37.' (dropped by R37-A4), stale header/rank (09:18Z, #140), slot-2 outcome claimed before 12:00Z, no 22:45-23:00 MSK band. Write v3 by 11:40Z, token checks 'довод' = 0, send 12:03Z (15:03 MSK), log sha8. Sources: `research/wf_ideas_v4/round38/report.json` R38-A1; `v_plancheck_pc38-01.json`; `FACTS.md` C-304..C-307; `WATCHLIST.md` C10.
2. [now] **Slot 2 (R37-A5):** 11:50Z message; no yes -> 12:00Z log 'slot 2 UNUSED (rule (a) not met; 08:28Z hold)'. The 11:10Z timer (pid 17304) is log-only; submit nothing. Sources: `CONTEXT.md` l.4488-4501; `WATCHLIST.md` T209.
3. [today] **One 12:00Z CONTEXT entry (R38-A2):** R37-A6 addendum (exp89r L (9.06, 9.14] h by count jump, k = 0, Satwik null, exp89t prior), timers as pointers + card v3 sha8, Satwik line lock, E10 after 12:00Z = verify biohub + MSK push, never submit without yes (I-584). Commit as the user, no co-author. Sources: `report.json` R38-A2; `scan_plancheck.json` PC38-03, PC38-06. (Settled: watch/ideas [today] vs facts [today]; all agree.)
4. [today] **17:40Z pre_exp89t job pid 18408 is fragile:** reads only the LAST poll.log block, skips on a transient error block, never retries -> S0 falls back ~6 h stale (biases k to 0). 11:45Z run mk_s0.py; before 17:40Z kill 18408/35124 and re-arm per R38-A4 (or save by hand). Sources: `report.json` R38-A4; `research/wf_ideas_v4/round38/report.notes.md` 10:34Z; `FACTS.md` C-308, F-RUN-57.
5. [today] **exp89t read playbook T0-T8 + admit edge (R38-A5, R38-A6):** log before 17:53Z (20:53 MSK); after a promotion first append 'RECOMMENDED PAIR = П3 {exp89t 56669888, #37 56563521}', then push MSK, so 18:37/19:43/21:05Z timers do not revert to exp87a; the 19:47Z re-read misses (19:40:33, 19:45:17] -> self-contained script at 19:44:45Z. Sources: `report.json` R38-A5, R38-A6; `v_hyp_exp89tread38_r38t-h1.json`. (Settled: facts [today] vs watch [today]/[before-finals] -> [today], the logging is due before 17:53Z.)
6. [today] **Stale bookkeeping:** round prompt KEY FACTS say 0.958 = exp85a and E10 >= 0.959 (truth 0.959 = exp87a, E10 >= 0.960) -> refresh before round 39 (13:13Z); round 38 uncommitted and rounds 37/38 lack REPORT.md; `experiments/RESULTS.md` stops at P46. Sources: `report.json` R38-A7; `report.notes.md` 10:38:56Z; `experiments/RESULTS.md` l.79. (Settled: RESULTS / REPORT.md after the 20:00Z tick, as in c37.)
7. [before-finals] **Finals tick:** SELECTED is still {#37 56563521, #38 56563534}; card v3 §5 asks the user to tick the chosen pair now ('сначала снимите, потом отметьте', '2 of 2 selected'); verify SELECTED ~20:00-20:30Z and 21:05Z; push MSK at once on any V_pub change. Sources: `DECISIONS.md` §2 l.999; `CONTEXT.md` l.3844-3855; `WATCHLIST.md` I426.
8. [before-finals] **Post-deadline guards:** push the hindsight-guard prediction (I-336), H2/H3 lessons (I-252) and the I-407 line incl. I-582 before 23:00Z. Source: `IDEAS.md` ORPHANS l.950.
9. [before-finals] **Ready answers:** if the user proposes #38 as 'division-free' partner: P(#37 pair >= #38 pair) = P(x > 0) ~0.85 (I424); exp89t still PENDING at ~18:40Z is anomalous (max CI-family L 9.48 h) -> prepare T7 (I427). Sources: `WATCHLIST.md` l.141; `v_recheck_r38-rc-c-noins-38-partner-stays-out-base-i.notes.md`.
10. [info] **Slot-2 masking conflict:** R37-A3 (3) 'MASKED' vs R26-A4 (b) (strictly lower display does not mask); matters only on a slot-2 yes (no count-57 S0). Sources: `report.json` R38-A3; `FACTS.md` C-309.
11. [info] **E10 after 12:00Z:** only `tools/kaggle_feed.py` watches (not competition-scoped, title blacklist) -> one competition-scoped kernel-list call before telling the user; build nothing. Quote no lab number for exp89t (dummy-lab +0.00089 is not private evidence). Sources: `CONTEXT.md` l.4502-4508; `FACTS.md` F-TRN-72 l.513; `WATCHLIST.md` I419, I420, I429.

**RESOLVED since curation 37:** stale timers 17304 / 33456 handled as pointers, kill rejected (I-576; `CONTEXT.md` l.4488-4492); slot-2 status message sent 09:19Z (R37-A1, W338); S0 plan and card plan logged 09:57Z (I-577, I-578 -> I-583); round 37 committed (66f1eeb); feed 0.9812 flag closed as another competition (135788c); I-548 mc31v card numbers refuted (R38T-G5) (`IDEAS.md` CHANGES (38) l.228-236; `WATCHLIST.md` summary).

## HOW TO USE

- "Score of probe N?" -> `DECISIONS.md` §1 l.144; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log`; `experiments/<exp>/probe.json`.
- "exp89t scored; what now?" -> `CONTEXT.md` l.4459-4470 + l.4488-4501 (A3), R38-A5 T0-T8 in `research/wf_ideas_v4/round38/report.json`; I-577 / I-580 / I-586; `FACTS.md` C-308, F-RUN-57.
- "Use slot 2?" -> `CONTEXT.md` l.4404-4414, l.4433-4440, l.4488-4501 (A5); I-575 / I-585; `DECISIONS.md` l.1777-1779.
- "Which finals pair?" -> card v3 (I-583) + `DECISIONS.md` §2 l.1001; EXP75 PARTNER RULE v2 `DECISIONS.md` l.1738; `FACTS.md` F-TRN-73.
- "Which rule decides this?" -> `DECISIONS.md` §3 l.1653; `FACTS.md` §5 l.335 and CONTRADICTIONS l.516. "Tried?" -> `IDEAS.md`. "True?" -> `FACTS.md`. "Next / overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~10:50Z 29 Sep, read the tail of `CONTEXT.md` §14 (above `## 9.`), the newest `===` header in `poll.log`, and `research/wf_ideas_v4/round39/` or later.
