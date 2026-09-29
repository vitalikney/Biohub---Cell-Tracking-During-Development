# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 32: state as of 2026-09-29 ~03:55 UTC (06:55 MSK). Git HEAD a9ac9ee ('Round 31: A-M2 function, 08:40Z header rule, card pool L'), after d6deab5 (`git log`). `CONTEXT.md` has 4,333 lines; newest entry 02:53Z l.4294-4312; `## 9. Literature` l.4313. Uncommitted: `research/KNOWLEDGE/*` curation-32 edits, `experiments/lb_poll/ledger.md`, `poll.log`, E10 logs. Untracked: `research/wf_ideas_v4/round32/` (report.json R32-A1..A4 written 03:45Z, 4 scans, 7 verdicts, NO REPORT.md), `experiments/e10_watch/20260929T0313Z.txt`, `0341Z.txt`, `experiments/lb_poll/_night_subs.csv` / `.err` (`git status`). Previous curation: 31 (~02:55Z). Times are UTC unless marked MSK (= UTC+3).
Deadline 29 Sep 23:59. The user ticks the finals MANUALLY by 20:00 UTC = 23:00 MSK; the session never ticks (`CONTEXT.md` l.3842-3855, l.4092). Rule anchors: PRE-REG v3 l.1576-1736; tie order l.3181; MORNING TABLE v1.1 l.3931-3955; GAP RULE v2 l.4009-4020; RULE v2.1 + exp89l gate l.4104-4126; W4 FREEZE l.4174-4253 (timeouts: (7) l.4226); 02:02Z texts l.4273-4293; 02:53Z A-M2 function / 08:40Z header / card pool L l.4294-4312.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 exp58 = 0.954 + #38 exp58n = 0.953, both below V_pub; only the user's tick changes it (`CONTEXT.md` l.4041-4050; `DECISIONS.md` §2 [c32] l.968-985).
2. **Best = P51 exp87a (K + CI) = 0.959 = V_pub, branch A.** Rank #132 of 3,980 at 03:13Z / 03:42Z, 17th of 21 in the 0.959 block; 115 teams >= 0.960; medal lines unchanged since 02:14Z (silver ~#199 in 0.957, bronze ~#398 in 0.955) (`FACTS.md` F-LB-32 l.259; `experiments/e10_watch/20260929T0341Z.txt`).
3. **No new LB score:** P52 exp89r (56656147), P53 exp75 (56656157), P54 exp89p (56657612) PENDING at the 03:44:23Z header (L > 3.64 / 3.64 / 2.96 h); expected reads exp89p ~07:47-07:58Z, exp75 ~09:03-09:49Z, exp89r ~09:23-09:34Z; 2 submits left on 29 Sep (`experiments/lb_poll/poll.log` l.28010; `DECISIONS.md` §1 l.197-200).
4. **Logged 02:53Z (R31-A1):** A-M2 function (DIS '+' -> exp89s; Rr '+' and DIS '?' -> exp89q iff P '+'/'?'; else UNUSED, incl. d_R = 0.959); 08:40Z header = last header <= 08:40:36Z + one [manual-A-M1] list at 08:40:00Z; round pause NOT adopted; card v5 pool L non-CI <= 9.0 h -> sha8 a134d5e4; R31-A2 push + R31-A3 read-time log (`CONTEXT.md` l.4294-4312; `FACTS.md` F-RUL-28 l.346).
5. **Open, urgent:** the R31-A2 power push (04:13Z, before the user's 05:10Z trip) has NO waiter; the only 04:13Z timer launches a round (`FACTS.md` C-266 l.743; `research/wf_ideas_v4/round32/v_plancheck_pc32-01.json` CONFIRMED).
6. **Round 32 proposals R32-A1..A4, none logged:** push waiter (A1); 0-call UP test from e10 snapshots + 'timeout 180' on any `tools/uptest.py` save (A2); timer texts are pointers (A3); post-deadline division order (A4) (`research/wf_ideas_v4/round32/report.json`; `DECISIONS.md` §2h l.1507-1510).
7. **Timer-text conflicts:** 07:23Z 'build/dummy exp89l' vs no rebuild; 08:30Z 'decide now' vs 08:40Z manual list; 12:03Z names card v4 vs card v5 (`FACTS.md` C-268, C-269; `WATCHLIST.md` W311 l.84).
8. **Card v5 (a134d5e4) still stale:** model numbers for exp85a (l.39, l.46-47; use R31-A4 / I-548), l.114 '+/0u', dead cron ids l.93/138/152, section-4 info lines (I-539) missing (`FACTS.md` C-255, C-263, C-269; `research/wf_ideas_v4/round29/finals_card_v5_ru.md`).
9. **Mode:** user asleep, AUTONOMOUS; submits only by logged rules; E10 null (trigger >= 0.960; HOURLY at ~xx:42Z, next 04:41:53Z, exits 12:00Z; runbook l.66 still says 0.958) (`experiments/e10_watch/watch_loop.log`; `FACTS.md` F-RUL-29 l.347; `WATCHLIST.md` W286 (2)).
10. **Next decision points:** by 04:09Z arm push timer, send 04:10-04:13Z; 04:13Z round 33; 06:07Z post-wake (do not kill a live lb_poll.py within ~11 min of wake); 07:23Z prep only; A-M1 at the 08:40Z header, submit exp89l by 08:45Z iff exp89p >= 0.959; A-M2 at exp89r's terminal header (latest 11:00Z), submit by 11:30Z; 12:03Z card v5 fill; 18:37Z proposal; 20:00Z user tick; 23:59Z deadline (`WATCHLIST.md` NEXT 24 H l.73, LATER l.96). Ideas 556 (in-plan 151, refuted 264, lb-tested 62, lab-tested 28, deferred 49, open 2) (`IDEAS.md` l.202-213).

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` = this page. `CHANGES.md` = per-curation deltas (v4, 2-32). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,32}/` (`*.json` = structured answers, `*.notes.md` = crash-safe logs).
- `IDEAS.md` + `ideas.json` (I-001..I-556): CHANGES (32) l.202, ranking l.215, FINALS l.234, LADDER l.322, BASE l.424, RUN l.467, LOC l.542, DIV l.578, MODEL l.651, NODES l.703, INFER l.741, EF l.763, LINK l.783, VALID l.821, TESTSET l.875, ORPHANS l.893.
- `FACTS.md`: §1 metric l.186, §2 data l.203, §3 LB l.224 (F-LB-32 l.259), §4 runtime l.261 (F-RUN-49 l.313), §5 rules l.315 (F-RUL-28/29 l.346-347), §6 models l.349, §7 lab-to-LB l.405 (F-TRN-64 l.472), CONTRADICTIONS l.474 (C-266..C-272 l.743-749).
- `DECISIONS.md`: probes §1 l.138 (P52-P56 l.197-200; [c32] update l.543); gates §1b l.545; finals §2 l.610 ([c32] snapshot l.968-985); E10 §2f l.1127 ([c32] l.1280); ladder/cards §2h l.1313 (R31-A1..A5 l.1502-1506, R32-A1..A4 l.1507-1510); R1-R10 §3 l.1512.
- `WATCHLIST.md` (curated ~03:53Z): OVERDUE l.61 (W309, W296/W303, W279 (1), W297, W126, W286 (2)), NEXT 24 H l.73 (W309-W311, T192-T194), LATER l.96 (W312), INSIGHTS l.124 (I366-I373).

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows to P46 only); `experiments/lb_poll/poll.log`, `ledger.md`; `experiments/e10_watch/watch_loop.log` + `2026*.txt`; `experiments/discussions/feed_loop.log` + `digest_*.md`.
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `exp58n_x138_safe_lowref/` (#38); V_pub `exp87a_k2cap6_div04_ra094_ci/`; night `exp89r_k2cap6_k_sec_dis225_ci/`, `exp75_k2_coordinject/`, `exp89p_k2cap6_k_sec/`; morning `exp89l_k2cap6_k_sec_ci/` (A-M1), `exp89s_k2cap6_k_dis225/`, `exp89q_k2cap6_k_sec_dis225/` (A-M2); prior best `exp85a_k2cap6_div04_ra094/`; base `exp70g_k2_cap6/`.
- Tools: `tools/build_probe_kernel.py`, `tools/runtime_ledger.py` (admit rule l.197-199), `tools/dummy_gates.py`, `tools/uptest.py` (save l.34-36 has no timeout), `tools/e10_port_gate.py`, `tools/kaggle_feed.py`.
- Round 32 (untracked): `research/wf_ideas_v4/round32/report.json` (R32-A1..A4, new_facts, plan_issues a-e, rejected, next_focus, report_md_ru), `report.notes.md`, `scan_{plancheck,recheck,hyp_external32,browser}.json`, `v_*.json`. Round 31: `round31/report.json` (R31-A4 card numbers, R31-A5). Round 30: `round30/report.json` (R30-A2 morning grid). Round 29: `round29/finals_card_v5_ru.md` (fill source), `night_checklist.md`. No REPORT.md for rounds 29-32. E10 runbook `research/wf_ideas_v4/e10v3/runbook.notes.md` (l.66 stale). Background: `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v3/FINAL_REPORT.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` ORPHANS l.893 ff. and CHANGES (32) l.202)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-546 | R31-A2 Russian power push before the 05:10Z trip; 06:07Z re-push if not on AC + battery-tolerant watchdog | Logged 02:53Z (5) but NO waiter: arm timer by 04:09Z, send 04:10-04:13Z, log '04:1xZ R31-A2 push sent' | `round32/report.json` R32-A1; `FACTS.md` C-266 |
| I-553 | Timer texts are pointers; the logged lines govern at 07:23Z / 08:30Z / 12:03Z | In-plan, at risk (proposed, not logged) | R32-A3; `FACTS.md` C-268, C-269 |
| I-552 | UP test from e10 snapshots (0 API calls); any fresh save only as 'timeout 180 python tools/uptest.py save <tag>' | In-plan, at risk; only needed if exp89p / exp89r display 0.959 | R32-A2; `FACTS.md` C-267, F-RUN-49 |
| I-548 / I-539 | Card fill numbers for V_pub exp87a + two section-4 info lines | At risk: apply at the 12:03Z fill, new sha8 | R31-A4; `FACTS.md` C-263 |
| I-547 | Read-time log: L vs family range (non-CI 6.87-7.81 h, CI 9.27-9.48 h) at each first terminal header | In-plan (logged 02:53Z) | R31-A3; `CONTEXT.md` l.4311-4312 |
| I-556 | Restrict the recheck lens to claims printed on card v5 | In-plan; apply in the round 33 brief | round32 plan_issues (d); `WATCHLIST.md` W313 |
| I-424 / I-121 / I-550 | Post-deadline division order: graph ranker for claimed daughters, parent-vector head (refuted -> deferred), insert-before-short-filter (low) | Deferred; add to the post-deadline agenda (I-252) after 20:00Z | R32-A4; `FACTS.md` F-TRN-64 |
| I-336 / I-233 / I-045 | Hindsight guard pushed before 23:00Z; poller error_description (strict orphan); I-045 WEAKENED-not-overturned note | Carried; one line each | `IDEAS.md` ORPHANS l.893 ff.; R31-A5 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/32/{ideas,facts,watch}.json`)

1. [now] **R32-A1 / W309 power push:** by 04:09Z (07:09 MSK) arm one timer.sh at 04:10:00Z; at 04:10-04:13Z send ONE Russian PushNotification (verbatim text `round32/report.json` R32-A1 (2)); log '04:1xZ R31-A2 push sent'; if read after 04:10Z, push at once, before round 33. Sources: `FACTS.md` C-266; `IDEAS.md` I-546; `WATCHLIST.md` l.65. (All three curators agree [now].)
2. [now] **E10 runbook trigger stale:** `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66 'SC >= 0.958' -> '>= 0.960 (OUR = 0.959)'; fix before the 04:41Z E10 run. Source: `WATCHLIST.md` W286 (2); `CONTEXT.md` l.4159-4160.
3. [today] **Timer texts vs logged lines (R32-A3):** 07:23Z no rebuild / re-push (02:02Z (5)); 08:30Z -> if 56657612 PENDING, one [manual-A-M1] list at 08:40:00Z (02:53Z (2)); 12:03Z fill card v5, not v4. Do not kill or re-arm timers. Sources: `FACTS.md` C-247, C-268, C-269; `IDEAS.md` I-553.
4. [today] **UP tests (R32-A2):** only for a 0.959 display of exp89p / exp89r; use e10 snapshots (count 53 -> 54, `uptest.py compare`); any save as 'timeout 180 ...'; do not edit the tool today. Curator correction: E10 runs HOURLY (~xx:42Z), not every ~30 min, so S1 can lag a header by ~1 h and exp75 + exp89r may land in one window (+2 rule). Sources: `FACTS.md` C-267, F-RUN-49; `experiments/e10_watch/watch_loop.log`.
5. [today] **Morning decisions:** 06:07Z restart only dead loops (T193); A-M1 exp89l iff exp89p COMPLETE >= 0.959 at the 08:40Z header, submit by 08:45Z (11:45 MSK); A-M2 by the 02:53Z (1) function at exp89r's terminal header (latest 11:00Z), submit by 11:30Z (14:30 MSK). Act at the decision header, not the cutoff. Sources: `CONTEXT.md` l.4273-4312; `DECISIONS.md` l.197-200.
6. [today] **Card v5 fill at 12:03Z (15:03 MSK):** R31-A4 numbers for l.39 / l.46-47, I-539 info lines, l.114 '+/0u', optional dead cron ids l.93/138/152, rank + medal-line line from the newest e10_watch file; new sha8; card v4 l.1 still cites aadead83. Sources: `FACTS.md` C-255, C-263, C-269; `IDEAS.md` I-548, I-539. (Settled: facts / watch [before-finals] vs ideas [today] -> [today], hard limit 12:03Z.)
7. [today] **Records missing / unlogged:** `experiments/RESULTS.md` no rows P47-P51 (0.955 / 0.957 / 0.955 / 0.958 / 0.959) or P52-P54; REPORT.md absent for rounds 29-32 (round 32 text in report.json 'report_md_ru'); round 32 uncommitted; W279 (1) DET_THRESHOLD line, W297 'cron defect, not battery', I-510 user message, I-045 note; R30-A3..A5, R31-A4/A5, R32-A1..A4 unlogged. Sources: `FACTS.md` C-118; `WATCHLIST.md` W126, W296/W303, W279, W297, W308. (Settled: ideas / facts [before-finals] vs watch [today] -> [today], after the morning decisions and before the 12:03Z card.)
8. [before-finals] **Finals messages:** 18:37Z proposal, 19:43Z reminder, 20:00Z user tick, 21:05Z last call; 'the pair by the card', never 'рекомендую' / 'не медаль'; the session never ticks. Sources: `CONTEXT.md` l.3848-3855; `DECISIONS.md` §2 l.968-985.
9. [info] **Post-deadline / process:** R32-A4 division agenda (cohort 72, not 85; -LoG splitter refuted) -> I-252 after 20:00Z; W313 drop / restrict the recheck lens in round 33. Sources: `round32/report.json` R32-A4; `WATCHLIST.md` W312, W313.

**RESOLVED since curation 31:** R31-A1 / W304 logged 02:53Z (A-M2 function, 08:40Z header, card pool L, push + read-time log; round pause NOT adopted, T189 superseded) and committed a9ac9ee with card v5 l.17 / l.124 (sha8 a134d5e4); C-259..C-262 resolved (`CONTEXT.md` l.4294-4312; `FACTS.md` C-259..C-262).

## HOW TO USE

- "Score of probe N, and what changed?" -> `DECISIONS.md` §1; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log` (P47 onward); `experiments/<exp>/probe.json`.
- "exp89p / exp89r / exp75 scored; what now?" -> `CONTEXT.md` l.3931-3955, l.4273-4312; `round32/report.json` R32-A2/A3; `round30/report.json` R30-A2; `tools/runtime_ledger.py` l.197-199.
- "Which morning file, and how do I submit it?" -> `CONTEXT.md` l.4294-4312 (1)(2); `DECISIONS.md` §1 l.197-200, §2h l.1502-1510; `WATCHLIST.md` NEXT 24 H l.73.
- "Which pair do we propose for the finals?" -> `research/wf_ideas_v4/round29/finals_card_v5_ru.md` (a134d5e4) + R31-A4 numbers; `DECISIONS.md` §2 l.968-985; `CONTEXT.md` l.4041-4050.
- "Did a public notebook beat us (>= 0.960)?" -> `experiments/e10_watch/watch_loop.log`; `experiments/discussions/feed_loop.log`; `DECISIONS.md` §2f l.1280.
- "Which rule decides this?" -> `DECISIONS.md` §3 l.1512; `FACTS.md` §5 l.315 and CONTRADICTIONS l.474; `CONTEXT.md` l.1576-1736. "Was idea X tried?" -> `IDEAS.md`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~03:55Z 29 Sep, check the tail of `CONTEXT.md` §14 (above `## 9.`), the newest `===` header in `poll.log`, and `research/wf_ideas_v4/round32/` or later round folders.
