# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 37: state as of 2026-09-29 ~10:00 UTC (13:00 MSK). Git HEAD 348b9dc ('Probe 52 exp89r = 0.957; DIS ~ 0; exp89s not sent', 09:19Z) after 782eed2 (09:09Z P53 read), 9693f08 (09:00Z P55 exp89t submitted), 7caa068 (08:51Z round 36 + CLARIFY + timer note) (`git log`). `CONTEXT.md` has 4,508 lines; newest entries l.4441-4487 (08:51Z CLARIFY ... 09:19Z READ P52); `## 9. Literature` l.4488. Uncommitted: `research/KNOWLEDGE/*` curation-37 edits, `experiments/lb_poll/ledger.md` / `poll.log`, e10 logs. Untracked: `research/wf_ideas_v4/round37/` (report.json R37-A1..A8, 4 scans, 8 verdicts, NO REPORT.md), `research/KNOWLEDGE/_curation/37/`, `experiments/e10_watch/20260929T0941Z.txt` (`git status`). Previous curation: 36 (~08:50Z). Times are UTC unless marked MSK (= UTC+3).
Deadline 29 Sep 23:59. The user ticks the finals MANUALLY by 20:00 UTC = 23:00 MSK; the session never ticks (`CONTEXT.md` l.3842-3855, l.4092). Rule anchors: PRE-REG v3 l.1576-1736 (R8 l.1671); no-midday-slot line l.3683-3687; GAP RULE v2 l.4009-4020; RULE v2.1 l.4104-4126; 08:19Z rule (a) l.4404-4414; 08:28Z slot-2 hold l.4433-4440; 08:51Z CLARIFY + SEC exception l.4441-4452; 09:00Z P55 + exp89t read rule l.4459-4470; 09:09Z P53 read l.4471-4478; 09:19Z P52 read l.4479-4487.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 exp58 = 0.954 + #38 exp58n = 0.953; recommended pair П3 {exp87a 56640366, #37 56563521}, П2 {exp87a, exp75} shown as a trade; the user must re-tick by 20:00 UTC (`DECISIONS.md` §2 [c37] l.994-996; `CONTEXT.md` l.4471-4478).
2. **Best = P51 exp87a (K + CI) = 0.959 = V_pub.** Rank #140 of 3,989 at 09:41Z, 16th of 20 in the 0.959 block (125-144) (`experiments/e10_watch/20260929T0941Z.txt` l.280, l.1164; `FACTS.md` F-LB-37 l.269).
3. **NEW P53 exp75 (#37 + CI) = 0.955, clean** (09:08:28Z; L (8.88, 9.05] h; CI-RAN): CI now 3/3 '+' (+0.001 each) on public; EXP75 PARTNER RULE v2 (b) (`CONTEXT.md` l.4471-4478; `FACTS.md` F-TRN-70 l.507).
4. **NEW P52 exp89r (K + SEC + DIS 2.25 + CI) = 0.957** (09:18:30Z; L (9.04, 9.22] h, count-jump refined (9.06, 9.14]): Rr '-', DIS ~0 (dd 0 -> '?'), rule (a) NOT met -> exp89s NOT sent (`CONTEXT.md` l.4479-4487; `FACTS.md` F-RUN-56 l.330).
5. **P55 exp89t (K + DIS 2.25 + CI) SUBMITTED 09:00:17Z (ref 56669888), the only PENDING file** at the 09:48:35Z header; read window ~17:53-19:54Z (admit 10.75 h = 19:45:17Z); most likely 0.959 = tie with exp87a -> V_pub only with an attributable UP (`CONTEXT.md` l.4459-4470; `experiments/lb_poll/poll.log` l.30088-30091; `experiments/exp89t_k2cap6_k_dis225_ci/probe.json`).
6. **Submits: 4 of 5 used today, 1 left. Slot 2 defaults to UNUSED** at the ~11:50-12:00Z decision (rule (a) failed, 08:28Z hold); a new non-CI candidate needs its dummy by ~11:15Z (14:15 MSK); exp89s only on a new explicit user yes (`CONTEXT.md` l.4433-4440, l.4484-4487; `research/wf_ideas_v4/round37/report.json` R37-A1, R37-A5).
7. **Round 37 (09:40Z) proposals R37-A1..A8, none logged:** slot-2 messages, stale timers 17304 / 33456, exp89t S0, 12:03Z card from scratchpad `card_fill_1203.txt` (dd1bdc22), CONTEXT addendum, exp89t read handling, optional П2/П3 caption (`research/wf_ideas_v4/round37/report.json`; `report.notes.md`).
8. **Background loops:** e10 RUN 45 09:42Z 8/8, signals 0, loop ends 12:00Z; feed digest 09:18Z: Satwik (744273) says the public embryo is division-poor; E10 flag none (`experiments/e10_watch/watch_loop.log`; `experiments/discussions/digest_20260929T0918Z.md`).
9. **Next decision points:** 10:13Z round 38 (last scan that can feed slot 2); before 11:10Z kill/re-arm timers; 11:45Z S0 fallback (mk_s0.py); 11:50Z slot-2 message, 12:00Z UNUSED log; 12:03Z card fill; 17:40Z pre_exp89t save; ~17:53Z+ exp89t read; 18:37Z FINAL card; 19:43Z + 19:47Z re-read; 20:00 UTC user tick; 23:59Z deadline (`WATCHLIST.md` l.56, l.80).
10. **Ideas 582** (lb-tested 65, lab-tested 28, refuted 271, deferred 50, in-plan 166, open 2); at-risk 16, strict orphan I-233 (`IDEAS.md` CHANGES (37) l.225, ORPHANS l.942).

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` = this page. `CHANGES.md` = per-curation deltas (v4, 2-37). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,37}/` (`*.json` answers, `*.notes.md` crash-safe logs).
- `IDEAS.md` + `ideas.json` (I-001..I-582): CHANGES (37) l.225, ranking l.238, FINALS l.257, LADDER l.353, BASE l.466, RUN l.509, LOC l.588, DIV l.624, MODEL l.697, NODES l.750, INFER l.788, EF l.810, LINK l.830, VALID l.868, TESTSET l.923, ORPHANS l.942.
- `FACTS.md`: §1 metric l.191, §2 data l.208, §3 LB l.229 (F-LB-37 l.269), §4 runtime l.271 (F-RUN-56 l.330), §5 rules l.332 (F-RUL-37 l.372), §6 models l.374, §7 lab-to-LB l.434 (F-TRN-70/71 l.507-508), CONTRADICTIONS l.510 (C-297..C-303 l.810-816).
- `DECISIONS.md`: probes §1 l.143 (P52-P55 l.202-206; [c37] l.559); finals §2 l.626 ([c37] snapshot l.996); E10 §2f l.1245; ladder/cards §2h l.1431 ([c37] rows l.1759-1763); R1-R10 §3 l.1630; changelog [c37] l.1971.
- `WATCHLIST.md` (~09:45Z): DUE NOW l.56 (W338-W340, W343), CONTRADICTIONS C2/C7/C8/C9 l.69, NEXT 24 H l.80, LATER l.104, INSIGHTS l.125 (I409-I418).

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows to P46 only); `experiments/lb_poll/poll.log`, `ledger.md`; `experiments/e10_watch/watch_loop.log` + `2026*.txt`; `experiments/discussions/feed_loop.log`, `digest_*.md`, `744273.md`.
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `exp58n_x138_safe_lowref/` (#38); V_pub `exp87a_k2cap6_div04_ra094_ci/`; pending `exp89t_k2cap6_k_dis225_ci/`; read today `exp75_k2_coordinject/` (0.955), `exp89r_k2cap6_k_sec_dis225_ci/` (0.957), `exp89p_k2cap6_k_sec/` (0.956); not sent `exp89s_k2cap6_k_dis225/`.
- Tools: `tools/uptest.py` (LB save / UP test), `tools/runtime_ledger.py`, `tools/build_probe_kernel.py`, `tools/dummy_gates.py`, `tools/kaggle_feed.py`; `experiments/lb_poll/e10_watch_loop.py` (END 12:00Z).
- Rounds: `research/wf_ideas_v4/round37/` (report.json with `report_md_ru`, scan_*/v_*); round 36 has REPORT.md; rounds 29-35 and 37 have no REPORT.md. Card: `research/wf_ideas_v4/round29/finals_card_v5_ru.md` (a134d5e4; filled copy only). Background: `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v3/FINAL_REPORT.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` CHANGES (37) l.225 and ORPHANS l.942)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-576 | Kill stale timers 17304 (11:10Z 'submit by 11:30') and 33456 (12:03Z card v4); re-arm pointer-only | At risk: before 11:10Z | R37-A2; `FACTS.md` C-297, C-298 |
| I-575 | Slot-2 closure: MSK status now, 11:50Z message, 12:00Z 'slot 2 UNUSED' log | At risk: now / 11:50Z / 12:00Z | R37-A1, R37-A5; `FACTS.md` C-302 |
| I-577 | S0 for exp89t's UP test: mk_s0.py at 11:45Z + pre_exp89t save at 17:40Z (count 56) | At risk: arm now | R37-A3; `FACTS.md` C-300 |
| I-578 / I-526 | 12:03Z card from `card_fill_1203.txt` + R37-A4 edits (a)-(c) | At risk: pre-fill ~11:40Z | R37-A4; `FACTS.md` C-301 |
| I-580 | exp89t read handling: watch from 17:53Z, immediate MSK push, 19:47Z re-read, 18:37Z rank source | At risk | R37-A7; `FACTS.md` C-299 |
| I-579 | CONTEXT addendum: count-jump timing, k = 0, Satwik null, exp89t prior, timers superseded | At risk: next commit | R37-A6 |
| I-336 / I-252 / I-407 | Hindsight guard, H2/H3 lessons, cap-family private-read line before 23:00-23:59Z | At risk | `IDEAS.md` ORPHANS l.942 ff. |
| I-233 | Poller logs error_description | Strict orphan, no owner | `research/wf_ideas_v4/round4/report.json` R4-A9 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/37/{ideas,facts,watch}.json`)

1. [now] **Stale timers (all three):** pid 17304 fires 11:10Z with 'submit by 11:30 UTC' (vs rule (a) + the 12:00Z hold); pid 33456 fires 12:03Z pointing at card v4. Kill + re-arm pointer-only before 11:10Z; if not, act on the CONTEXT rules, not the timer text; exp89s has no NEVER_SUBMIT guard. Sources: `research/wf_ideas_v4/round37/report.notes.md` 09:36Z; `report.json` R37-A2; `FACTS.md` C-297, C-298.
2. [now] **Slot-2 status message (R37-A1)** in MSK: exp89s not sent under rule (a); the last slot stays empty unless a >= 0.960 notebook / disclosed setting appears by ~11:15Z (14:15 MSK, NOT 14:55 MSK). Sources: `report.json` R37-A1, plan_issues (5); `CONTEXT.md` l.4479-4487.
3. [now] **exp89t has no count-56 S0** (post_exp75 = count 55; watcher saves only post_exp89t at 0.959; e10 ends 12:00Z; naive e10 -> _lb conversion crashes KeyError 'TeamId'). Arm the 17:40Z `timeout 180 python tools/uptest.py save pre_exp89t` job now; 11:45Z mk_s0.py fallback. Sources: `report.json` R37-A3; `research/wf_ideas_v4/round37/scan_plancheck.json` PC37-01; `CONTEXT.md` l.4459-4470. (Settled: facts [today] vs ideas / watch [now] -> [now], the job must be armed while the session is up.)
4. [today] **11:50Z / 12:00Z slot-2 decision (R37-A5):** message at 11:50Z; no answer -> log 'slot 2 UNUSED (rule (a) not met; 08:28Z hold); DIS 1.75 / exp89e not revived'. Sources: `report.json` R37-A5; `CONTEXT.md` l.4433-4440; `research/wf_ideas_v4/round37/scan_recheck.notes.md`.
5. [today] **12:03Z card fill** from scratchpad `card_fill_1203.txt` (sha8 dd1bdc22, already has I-562/I-565/I-573): (a) drop section-3 exp75 fallback lines, (b) add '0u' to the section-5 admit clause, (c) immediate push instead of 22:43-only; refresh header / SELECTED / rank; token checks; never 'рекомендую'. The block lives only in the scratchpad: if lost, rebuild from `research/wf_ideas_v4/round37/scan_hyp_readscard37.json` R37-F4. Sources: `report.json` R37-A4; `FACTS.md` C-301; `WATCHLIST.md` W341, I411.
6. [today] **Round 38 at 10:13Z** = last scan that can still feed slot 2 (browser-only; E10 flag none, best public notebook 0.953). Source: `experiments/discussions/digest_20260929T0918Z.md` l.42; `report.json` next_focus. (Watch only.)
7. [today] **CONTEXT addendum (R37-A6)** with the next commit, no re-log of 09:19Z: count-jump L (9.06, 9.14] h, k = 0, Satwik null, exp89t prior, timers superseded; plus the R8-override line (W336). Sources: `report.json` R37-A6; `WATCHLIST.md` W343. (Settled: watch [now] / facts [today] / ideas [info] -> [today].)
8. [before-finals] **exp89t read:** window ~17:53Z (L 8.88 h) to ~19:54Z, not card step 9's 9.27-9.45 h; admit edge 19:45:17Z is after the 19:43Z reminder -> re-read poll.log ~19:47Z; code at once under the 09:00Z rule, push MSK on any V_pub change (П3 {exp89t, #37}); 18:37Z rank from post/pre_exp89t or one `fill_1837` save. Sources: `report.json` R37-A7; `FACTS.md` C-299; `experiments/lb_poll/ledger.md` 09:38:35Z.
9. [before-finals] **Finals:** SELECTED expected {#37 56563521, #38 56563534}; user ticks by 20:00Z; read-only SELECTED check ~20:00-20:30Z, 21:05Z timer; hindsight guard (I-336), H2/H3 (I-252), I-407 line + I-582 before 23:00Z. Sources: `CONTEXT.md` l.3844-3855, l.4091-4092; `IDEAS.md` ORPHANS l.942.
10. [today] **Power:** laptop on battery at 08:50Z (78%); keep charger in + lid open until 23:00 MSK (I-497, I-517). Source: `CONTEXT.md` l.4453-4458. (Ideas only.)
11. [info] **П2/П3 break-even:** standing-prior MC ranks П2 {exp87a, exp75} ahead on bronze at CI sd <= 0.0012 (break-even private CI mean ~+0.0004..+0.0006); keep 'П3 first' on the card, optional chat caption only (I-581). Sources: `report.json` R37-A8, plan_issues (7); `FACTS.md` C-303.
12. [info] **Records:** `experiments/RESULTS.md` rows stop at P46 (P47-P55 missing); round 37 (and 29-35) no REPORT.md (text in `report.json` 'report_md_ru'); round 37 untracked. Do after the 20:00Z tick. (Settled: ideas / facts [info] vs watch [before-finals] -> after the tick.) Sources: `experiments/RESULTS.md` l.79; `research/wf_ideas_v4/round37/report.notes.md` 09:40Z.

**RESOLVED since curation 36:** R36-A2 CLARIFY + SEC exception and R36-A3 timer note logged 08:51Z (I-570, I-571; C-288..C-290); exp89t submitted 09:00:17Z (I-486); exp75 read 0.955 and exp89r read 0.957 coded (I-465, I-478); round 36 vs the user conflict closed (C1/C4); round 36 committed (7caa068); exp89s refuted (I-484); DIS 1.75 revival upheld closed (I-461) (`CONTEXT.md` l.4441-4487; `IDEAS.md` l.228-234).

## HOW TO USE

- "Score of probe N?" -> `DECISIONS.md` §1 l.143; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log`; `experiments/<exp>/probe.json`.
- "exp89t scored; what now?" -> `CONTEXT.md` l.4459-4470 (read rule, S0/S1), I-577 / I-580, `FACTS.md` C-299, C-300.
- "Use slot 2?" -> `CONTEXT.md` l.4404-4414, l.4433-4440, l.4484-4487; I-575; `DECISIONS.md` l.1754-1756.
- "Which finals pair?" -> card v5 filled copy (I-578) + `DECISIONS.md` §2 l.996; EXP75 PARTNER RULE v2 `DECISIONS.md` l.1715.
- "Which rule decides this?" -> `DECISIONS.md` §3 l.1630; `FACTS.md` §5 l.332 and CONTRADICTIONS l.510. "Tried?" -> `IDEAS.md`. "True?" -> `FACTS.md`. "Next / overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~10:00Z 29 Sep, read the tail of `CONTEXT.md` §14 (above `## 9.`), the newest `===` header in `poll.log`, and `research/wf_ideas_v4/round38/` or later.
