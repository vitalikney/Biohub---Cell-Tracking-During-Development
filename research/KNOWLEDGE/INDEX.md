# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 39: state as of 2026-09-29 ~11:50 UTC (14:50 MSK). Git HEAD c8130a6 (11:39:46Z, '744273 re-read', commits the CONTEXT 11:10Z + 11:39Z entries, digest 1128Z, poll.log) after 75f0efe (10:54Z ROUND 38 APPLIED) (`git log`). `CONTEXT.md` has 4,567 lines; newest entries l.4509-4546 (10:54Z ROUND 38 APPLIED; 11:10Z TIMER 'A-M2 UNUSED'; 11:39Z DISCUSSION 744273 RE-READ); `## 9. Literature` l.4547. Uncommitted: `research/KNOWLEDGE/*` curation-39 edits, `experiments/lb_poll/ledger.md`, e10 logs. Untracked: `research/wf_ideas_v4/round39/` (report.json R39-A1..A9, 4 scans, 7 verdicts, NO REPORT.md), `research/KNOWLEDGE/_curation/39/`, `experiments/e10_watch/20260929T1110Z.txt`, `20260929T1141Z.txt`, `experiments/lb_poll/_lb/e10_20260929T1141Z/lb.csv` (`git status`). Previous curation: 38 (~10:50Z). Times are UTC unless marked MSK (= UTC+3).
Deadline 29 Sep 23:59. The user ticks the finals MANUALLY by 20:00 UTC = 23:00 MSK; the session never ticks (`CONTEXT.md` l.3842-3855, l.4092). Rule anchors: PRE-REG v3 l.1576-1736 (R8 l.1671); GAP RULE v2 l.4009-4020; RULE v2.1 l.4104-4126; 08:19Z rule (a) l.4404-4414; 08:28Z slot-2 hold l.4433-4440; 08:51Z CLARIFY + SEC exception l.4441-4452; 09:00Z exp89t read rule l.4459-4470; 09:57Z R37 applied l.4488-4501; 10:54Z R38 applied (card v3, playbook T0-T8, manual-admit) l.4509-4537.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged, weak pair):** #37 exp58 0.954 + #38 exp58n 0.953 = ~0.49 bronze / ~0.11 silver in every corrected MC run; recommended П3 {exp87a 56640366, #37 56563521}, П2 {exp87a, exp75 56656157} an allowed trade (`DECISIONS.md` §2 [c39] l.1004-1006; `FACTS.md` F-TRN-74 l.519).
2. **Best = P51 exp87a (K + CI) = 0.959 = V_pub.** Rank #141 of 3,994 at 11:41Z, 17th of 22 in the 0.959 block (ranks 125-146) (`experiments/e10_watch/20260929T1141Z.txt` l.1175; `FACTS.md` F-LB-39 l.273).
3. **No new LB score since curation 38** (none since P52/P53 reads at 09:09-09:19Z) (`DECISIONS.md` §1 [c39] l.565; `CONTEXT.md` l.4471-4487).
4. **P55 exp89t (K + DIS 2.25 + CI, ref 56669888) PENDING** at the 11:38:57Z header (L > 2.6 h); typical read ~18:17-18:29Z, T7 if still PENDING at the first header >= 19:12:17Z, admit edge 19:45:17Z (22:45 MSK) (`experiments/lb_poll/poll.log` l.30759-30763; `CONTEXT.md` l.4509-4537 (A5); `FACTS.md` F-RUN-58 l.336).
5. **Submits: 4 of 5 used today; slot 2 -> UNUSED** (11:10Z 'A-M2 UNUSED' logged; 11:50Z message, 12:00Z R39-A1 (2) line still due; any file after ~12:43Z cannot become a final) (`CONTEXT.md` l.4538-4539; `research/wf_ideas_v4/round39/report.json` R39-A1).
6. **Logged since c38:** 10:54Z R38-A1, A2, A4-A7 (card v3 sha8 ae03f566, R37-A6 addendum, E10 policy after 11:30Z, pre_exp89t re-armed, T0-T8 playbook, manual-admit 19:44:45Z, KEY FACTS refresh); 11:39Z 744273 Civitasmass 'local gains negligible or negative on public', no values (`CONTEXT.md` l.4509-4546; `FACTS.md` F-RUL-39 l.380).
7. **Round 39 (11:33Z) proposals R39-A1..A9, only A1/A2 partly acted on:** T7 trigger (A3), SELECTED comparator (A4), S0 validity guard (A5), 0-API Chrome-only rounds + tie wording (A6), mk_card_1837.py (A7), watchdog re-arm (A8), cap-6 answer line (A9) (`research/wf_ideas_v4/round39/report.json`; `DECISIONS.md` §3 l.1817-1818).
8. **Background:** e10 RUN 47 11:41Z (last; loop ends 12:00Z); S0 csv `experiments/lb_poll/_lb/e10_20260929T1141Z/lb.csv` written 11:45Z (tag not yet logged); pre_exp89t 36816 (17:40Z), manual_admit 3028, watcher 30864, one-shot watchdog 22236 (`WATCHLIST.md` l.97-114; `FACTS.md` F-RUN-58).
9. **Next decision points (UTC / MSK):** 11:50/14:50 slot-2 msg; 12:00/15:00 UNUSED log; 12:03/15:03 card v3; <13:13/16:13 round prompt R39-A6; 17:13/20:13 liveness; <17:40/20:40 guard + card builder; <18:13/21:13 T7 trigger; 18:37/21:37 FINAL card; ~19:20/22:20 T7; 19:44:45 admit; 20:00/23:00 tick; 23:59 deadline (`WATCHLIST.md` l.93-118).
10. **Ideas 593** (lb-tested 65, lab-tested 28, refuted 274, deferred 50, in-plan 174, open 2); at-risk 15, strict orphan I-233 (`IDEAS.md` CHANGES (39) l.232, ORPHANS l.960).

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` = this page. `CHANGES.md` = per-curation deltas (v4, 2-39). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,39}/` (`*.json` answers, `*.notes.md` crash-safe logs).
- `IDEAS.md` + `ideas.json` (I-001..I-593): CHANGES (39) l.232, ranking l.245, FINALS l.264, LADDER l.364, BASE l.482, RUN l.526, LOC l.606, DIV l.642, MODEL l.715, NODES l.768, INFER l.806, EF l.828, LINK l.848, VALID l.886, TESTSET l.941, ORPHANS l.960.
- `FACTS.md`: state l.3; §1 metric l.193, §2 data l.210, §3 LB l.231 (F-LB-39 l.273), §4 runtime l.275 (F-RUN-58 l.336), §5 rules l.338 (F-RUL-39 l.380), §6 models l.382, §7 lab-to-LB l.442 (F-TRN-74/75 l.519-520), CONTRADICTIONS l.522 (C-315..C-326 l.840-851).
- `DECISIONS.md`: probes §1 l.145 (P55 l.208; [c39] l.565); finals §2 l.632 ([c39] snapshot l.1006); E10 §2f l.1292; ladder/cards §2h l.1478; R1-R10 §3 l.1677 ([c39] rows l.1815-1818); changelog at the end.
- `WATCHLIST.md` (~11:40Z): DUE NOW l.68 (W355, W354, W346, W359, W363), CONTRADICTIONS l.81 (C14-C16), NEXT 24 H l.93, LATER l.123, INSIGHTS l.150 (I430-I439).

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows to P46 only); `experiments/lb_poll/poll.log`, `ledger.md`; `experiments/e10_watch/watch_loop.log` + `2026*.txt`; `experiments/discussions/feed_loop.log`, `digest_*.md`, `744273.md`, `738833.md`.
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `exp58n_x138_safe_lowref/` (#38); V_pub `exp87a_k2cap6_div04_ra094_ci/`; pending `exp89t_k2cap6_k_dis225_ci/`; П2 partner `exp75_k2_coordinject/` (0.955); read `exp89r_k2cap6_k_sec_dis225_ci/` (0.957), `exp89p_k2cap6_k_sec/` (0.956).
- Tools: `tools/uptest.py` (LB save / UP test), `tools/runtime_ledger.py`, `tools/build_probe_kernel.py`, `tools/dummy_gates.py`, `tools/kaggle_feed.py` (only E10 watcher after 12:00Z), `tools/e10_snapshot.py` (8 calls/run; not after 12:00Z per R39-A6); round prompt `experiments/workflows/biohub-research-round.js` (KEY FACTS l.20, l.37).
- Rounds: `research/wf_ideas_v4/round39/` (report.json, scan_plancheck / scan_hyp_slot2last39 / scan_recheck / scan_browser, v_*); rounds 29-35, 37-39 have no REPORT.md. Card template `research/wf_ideas_v4/round29/finals_card_v5_ru.md`; filled card v3 only in the scratchpad (`card_fill_1203_v3.txt`, ae03f566). Background: `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v3/FINAL_REPORT.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` CHANGES (39) l.232 and ORPHANS l.960)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-575 / I-577 | Slot-2 closure (11:50Z msg, 12:00Z R39-A1 (2) line) + S0 build 1141Z with named fallback 1110Z | At risk: now; S0 tag unlogged | R39-A1, R39-A2 |
| I-591 | 0-API Chrome-only rounds after 12:00Z; 0 agent calls 17:30-20:00Z; fixed tie wording in KEY FACTS | At risk: before 13:13Z | R39-A6; `FACTS.md` C-315, C-320 |
| I-588 | T7 trigger `t7_trigger.sh` (0 calls, fires ~19:20Z) | At risk: arm before 18:13Z | R39-A3; `FACTS.md` C-318 |
| I-589 | SELECTED comparator: П3 or П2 with current V_pub both pass | At risk: log before 18:37Z | R39-A4; `FACTS.md` C-319 |
| I-590 | pre_exp89t S0 validity guard (count 56, LastSubmissionDate 00:46:36) | At risk: log before 17:40Z | R39-A5; `FACTS.md` C-324 |
| I-592 | 18:37Z card builder `mk_card_1837.py` (PENDING/T1..T6), sha8s logged | At risk: before 17:40Z | R39-A7; `FACTS.md` C-326 |
| I-336 / I-252 / I-407 | Hindsight guard, H2/H3 lessons, cap-family private-read line (+ I-582 Satwik, Civitasmass) | At risk: before 23:00Z | `IDEAS.md` ORPHANS l.960 |
| I-233 | Poller logs error_description | Strict orphan, no owner | `research/wf_ideas_v4/round4/report.json` R4-A9 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/39/{ideas,facts,watch}.json`)

1. [now] **S0 build (R39-A2):** `mk_s0.py 20260929T1141Z` (csv present 11:45Z); on StopIteration, missing file or count != 56 use 20260929T1110Z; log the tag. Card l.8 = 17th of 22 (not '17 of 21'). Sources: `report.json` R39-A2; `experiments/e10_watch/20260929T1141Z.txt` l.1175; `WATCHLIST.md` W355.
2. [now] **Slot 2 UNUSED (R39-A1):** 11:50Z (14:50 MSK) message (not citing UP-test hygiene), 12:00Z line 'slot 2 decision = UNUSED ...' incl. 'R38-A3 applies to any slot-2 submit before 12:43Z'. Submit nothing. Sources: `report.json` R39-A1; `CONTEXT.md` l.4538; `WATCHLIST.md` W354.
3. [now] **Card v3 ae03f566 at 12:03Z (15:03 MSK):** header, SELECTED (1 call), rank/block from S0, SEC clause from 12:00Z log; never v4/v2; NO 'Fanch above us on the earlier timestamp' (misattribution; order = unrounded score). Sources: `CONTEXT.md` l.4511-4516; `FACTS.md` C-315, C-317; `WATCHLIST.md` W346, C16.
4. [today] **Round prompt (R39-A6) before 13:13Z (16:13 MSK):** KEY FACTS still say 'ties broken by the EARLIER submission'; browser agent still runs `tools/e10_snapshot.py` (~40 calls over rounds 40-44, overlapping 17:40Z save and 19:44:45Z list; conflicts with the 28 Sep API-load feedback). Fix: Chrome only, 0 agent calls 17:30-20:00Z, 18:13Z round READS-vs-CARD locally. Sources: `experiments/workflows/biohub-research-round.js` l.20, l.37; `FACTS.md` C-316, C-320; I-591. (Settled: ideas [now] vs facts/watch [today] -> [today], hard edge 13:13Z.)
5. [today] **T7 trigger + SELECTED comparator (R39-A3, A4):** nothing fires T7 (user would get ~17 min, not ~40, before 23:00 MSK); 18:37/19:43/21:05Z timer texts compare with 'the recommended pair' and would push a deliberate П2 tick. Arm `t7_trigger.sh` and log the comparator before 18:13Z. Sources: `report.json` R39-A3, R39-A4; `FACTS.md` C-318, C-319; I-588, I-589.
6. [today] **Before 17:40Z (20:40 MSK):** log the S0 validity guard (a completion just before the save turns a real UP into BLIND) and build + dry-run `mk_card_1837.py` (v3 l.3/l.48 go stale; hand edits caused PC38-01). Sources: `report.json` R39-A5, R39-A7; `FACTS.md` C-324, C-326; I-590, I-592.
7. [today] **Watchdog 22236 is one-shot:** re-arm after any ON-BATTERY / POLL-STALE alert; at 17:13Z check 22236, 36816, 3028, 30864, T7 trigger, poller 37016 alive; watcher 30864 reads error blocks too -> read poll.log by hand after ~17:50Z. Sources: `report.json` R39-A8; `FACTS.md` F-RUN-58; `WATCHLIST.md` W361.
8. [before-finals] **Finals tick by 20:00Z:** SELECTED still {#37, #38} (~0.49 / ~0.11); card v3 asks to tick П3 or П2 now; re-check at 18:37, 19:43, 21:05Z with the comparator; push MSK on any V_pub change. Sources: `DECISIONS.md` §2 l.1004; `FACTS.md` F-TRN-74; `CONTEXT.md` l.3844-3855.
9. [before-finals] **Post-deadline guards:** push I-336 prediction, I-252, and the I-407 line citing I-582 (Satwik 744273 + Civitasmass 11:39Z) before 23:00Z. Late-experiment requests: any file after ~12:43Z cannot be a final (I437). Sources: `IDEAS.md` ORPHANS l.960; `CONTEXT.md` l.4540-4546; `WATCHLIST.md` l.150.
10. [info] **Ready answers only if asked:** cap-6 partners 'below cap-4 12/12' is false on silver (exp85a beats #37 12/12) -> use R39-A9 line only; exp86c (READMIT 0.92) closed. Sources: `FACTS.md` C-321, F-TRN-75; `report.json` R39-A9.
11. [today / info] **Bookkeeping:** commit round39/ with the 12:00Z entry (as the user, no co-author); after the tick add `experiments/RESULTS.md` rows P47-P55 and render REPORT.md rounds 37-39 from report.json. Sources: `experiments/RESULTS.md` l.79; `WATCHLIST.md` W363. (Settled: watch [today] for the commit, ideas/facts [info] for RESULTS/REPORT.)

**RESOLVED since curation 38:** card v2 flaw -> v3 ae03f566 logged (C10); R38-A2 single entry incl. R37-A6 addendum and E10-after-11:30Z policy logged; 17:40Z pre_exp89t re-armed (newest non-error block, one retry); T0-T8 playbook + RECOMMENDED PAIR rule + 19:44:45Z manual-admit logged; KEY FACTS 0.959/E10 >= 0.960 refreshed (all `CONTEXT.md` l.4509-4537); 11:10Z A-M2 UNUSED logged (l.4538); round 38 committed (75f0efe); 11:10Z/11:39Z entries committed (c8130a6).

## HOW TO USE

- "Score of probe N?" -> `DECISIONS.md` §1 l.145; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log`; `experiments/<exp>/probe.json`.
- "exp89t scored; what now?" -> `CONTEXT.md` l.4509-4537 (A5 T0-T8, A6), l.4459-4470; R39-A3..A5 in `research/wf_ideas_v4/round39/report.json`; I-588 / I-590; `FACTS.md` F-RUN-58, C-318, C-324.
- "Use slot 2 / one more try?" -> `CONTEXT.md` l.4433-4440, l.4538-4546; R39-A1; I-575 / I-585; `WATCHLIST.md` W354, I437.
- "Which finals pair / is SELECTED ok?" -> card v3 (I-583) + `DECISIONS.md` §2 l.1006; I-589 comparator; `FACTS.md` F-TRN-74; EXP75 PARTNER RULE v2 `DECISIONS.md` l.1762.
- "Which rule decides this?" -> `DECISIONS.md` §3 l.1677; `FACTS.md` §5 l.338 and CONTRADICTIONS l.522. "Tried?" -> `IDEAS.md`. "True?" -> `FACTS.md`. "Next / overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~11:50Z 29 Sep, read the tail of `CONTEXT.md` §14 (above `## 9.`), the newest `===` header in `poll.log`, and `research/wf_ideas_v4/round40/` or later.
