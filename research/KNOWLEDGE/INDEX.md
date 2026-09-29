# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 36: state as of 2026-09-29 ~08:50 UTC (11:50 MSK). Git HEAD 785be93 ('Slot 2 held until 15:00 MSK', 08:28Z) after 6a3f778 (08:27Z user yes to exp89t), 096d533 (08:23Z exp89t built), 2fdf387 (08:19Z A-M2 rule (a)), ce88ccf (07:59Z P54 read), 332ace7 (07:46Z round 35 + curation 35) (`git log`). `CONTEXT.md` has 4,461 lines; newest entries l.4381-4440 (07:46Z ROUND 35 ... 08:28Z SLOT 2 HELD); `## 9. Literature` l.4441. Uncommitted: `research/KNOWLEDGE/*` curation-36 edits, `experiments/lb_poll/ledger.md` / `poll.log`, e10 and feed logs. Untracked: `research/wf_ideas_v4/round36/` (REPORT.md + report.json R36-A1..A5, 4 scans, 12 verdicts), `research/KNOWLEDGE/_curation/36/`, `experiments/discussions/744273.md` / `744278.md` / `digest_20260929T0828Z.md`, `experiments/e10_watch/20260929T0841Z.txt` (`git status`). Previous curation: 35 (~07:45Z). Times are UTC unless marked MSK (= UTC+3).
Deadline 29 Sep 23:59. The user ticks the finals MANUALLY by 20:00 UTC = 23:00 MSK; the session never ticks (`CONTEXT.md` l.3842-3855, l.4092). Rule anchors: PRE-REG v3 l.1576-1736 (R8 l.1671); no-midday-slot line l.3683-3687; GAP RULE v2 l.4009-4020; RULE v2.1 l.4104-4126; 03:56Z timer texts = pointers l.4313-4324; 07:46Z R35 procedures l.4381-4393; 07:59Z P54 read l.4394-4403; 08:19Z rule (a) l.4404-4414; 08:23Z exp89t l.4415-4425; 08:27Z yes l.4426-4432; 08:28Z hold l.4433-4440.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 exp58 = 0.954 + #38 exp58n = 0.953; the user must re-tick at 20:00 UTC (`DECISIONS.md` §2 [c36] l.989-991; `CONTEXT.md` l.4041-4050).
2. **Best = P51 exp87a (K + CI) = 0.959 = V_pub.** Rank #139 at 08:42Z, 16th of 20 in the 0.959 block (124-143); 123 teams >= 0.960 (`experiments/e10_watch/20260929T0841Z.txt` l.1160; `FACTS.md` F-LB-36 l.267).
3. **NEW score P54 exp89p (K + SEC) = 0.956** (07:58:14Z; L (7.02, 7.20] h) -> P '-', SEC on K ~-0.002; A-M1 UNUSED, exp89l never sent; SEC removed from all morning files (`CONTEXT.md` l.4394-4403; `FACTS.md` F-TRN-68 l.501).
4. **PENDING at the 08:38:21Z header:** P52 exp89r (56656147, read ~09:23-09:34Z, latest the 11:00Z header) and P53 exp75 (56656157, ~09:05-10:05Z); exp89t not in the list up to the 08:48:23Z header (`experiments/lb_poll/poll.log` l.29661, l.29722; `DECISIONS.md` l.201-205).
5. **exp89t (K + DIS 2.25 + CI) = probe 55, user said 'отправляй' at 08:27Z:** submit at dummy PASS (~08:55-09:05Z; R22-A1 gate vs exp87a dummy CSV db3faf078781), guards G1/G2 (used_today 3)/G3/G5; typical read ~18:25-18:35Z, tail after 20:00Z = display only (`CONTEXT.md` l.4415-4432; `experiments/exp89t_k2cap6_k_dis225_ci/probe.json`; `FACTS.md` F-MOD-55 l.428).
6. **Slot 2 HELD to ~12:00Z (15:00 MSK):** at exp89r's read only CODE rule (a) (>= 0.958 with L_hi <= 10.2 h, or >= 0.959 with L_hi <= 10.75 h) and the DIS estimate d_R - 0.959 + 0.002; ask the user ~11:55Z; no answer -> exp89s if rule (a) held, else UNUSED; non-CI only (`CONTEXT.md` l.4404-4414, l.4433-4440).
7. **Round 36 (08:33Z) read CONTEXT only to l.4425:** R36-A1 (ask about exp89t) is answered; R36-A4 (1) (send exp89s at the read) conflicts with the hold; R36-A2 CLARIFY and R36-A3 08:30Z line NOT logged (`grep -c CLARIFY CONTEXT.md` = 0) (`research/wf_ideas_v4/round36/report.json`; `research/wf_ideas_v4/round36/report.notes.md`).
8. **Background loops:** e10 RUN 44 08:42Z 8/8, signals 0, loop ends 12:00Z; feed 08:28Z 2 new topics (744273 external edge-only null, 744278), E10 flag none (`experiments/e10_watch/watch_loop.log`; `experiments/discussions/feed_loop.log`).
9. **Next decision points:** exp89t submit ~09:05Z; CLARIFY before exp89r's header ~09:23Z; exp75 read (EXP75 PARTNER RULE v2); exp89r read -> rule (a) code; 11:10Z timer = pointer only; ~11:55Z slot-2 ask; 12:03Z card v5 fill; 18:37Z FINAL proposal; 19:43Z reminder; 20:00 UTC user tick; 23:59Z deadline (`WATCHLIST.md` l.59, l.81, l.104).
10. **Ideas 574** (lb-tested 63, lab-tested 28, refuted 270, deferred 49, in-plan 162, open 2); at-risk 13, strict orphan I-233 (`IDEAS.md` CHANGES (36) l.219, ORPHANS l.928).

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` = this page. `CHANGES.md` = per-curation deltas (v4, 2-36). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,36}/` (`*.json` answers, `*.notes.md` crash-safe logs).
- `IDEAS.md` + `ideas.json` (I-001..I-574): CHANGES (36) l.219, ranking l.232, FINALS l.251, LADDER l.345, BASE l.455, RUN l.498, LOC l.576, DIV l.612, MODEL l.685, NODES l.738, INFER l.776, EF l.798, LINK l.818, VALID l.856, TESTSET l.910, ORPHANS l.928.
- `FACTS.md`: §1 metric l.190, §2 data l.207, §3 LB l.228 (F-LB-36 l.267), §4 runtime l.269 (F-RUN-55 l.327), §5 rules l.329 (F-RUL-36 l.368), §6 models l.370 (F-MOD-55 l.428), §7 lab-to-LB l.430 (F-TRN-68/69 l.501-502), CONTRADICTIONS l.504 (C-288..C-296 l.795-803).
- `DECISIONS.md`: probes §1 l.142 (P52-P55 l.201-205; [c36] l.556); finals §2 l.623 ([c36] snapshot l.991); E10 §2f l.1222; ladder/cards §2h l.1408 ([c36] rows l.1730-1735); R1-R10 §3 l.1607; changelog [c36] l.1941.
- `WATCHLIST.md` (~08:40Z): DUE NOW l.59 (W330, W331), CONTRADICTIONS C1-C6 l.70, NEXT 24 H l.81, LATER l.104, INSIGHTS l.136 (I400-I408).

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows to P46 only); `experiments/lb_poll/poll.log`, `ledger.md`; `experiments/e10_watch/watch_loop.log` + `2026*.txt`; `experiments/discussions/feed_loop.log`, `digest_*.md`, `744273.md`.
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `exp58n_x138_safe_lowref/` (#38); V_pub `exp87a_k2cap6_div04_ra094_ci/`; pending `exp89r_k2cap6_k_sec_dis225_ci/`, `exp75_k2_coordinject/`; slot 1 `exp89t_k2cap6_k_dis225_ci/`; slot-2 candidate `exp89s_k2cap6_k_dis225/`; read `exp89p_k2cap6_k_sec/` (0.956); out: `exp89l_*`, `exp89q_*`; neighbour `exp85a_k2cap6_div04_ra094/`.
- Tools: `tools/uptest.py`, `tools/runtime_ledger.py`, `tools/build_probe_kernel.py`, `tools/dummy_gates.py`, `tools/kaggle_feed.py`; `experiments/lb_poll/e10_watch_loop.py` (END 12:00Z).
- Rounds: `research/wf_ideas_v4/round36/` (REPORT.md, report.json, scan_*/v_*); rounds 29-35 have report.json only (no REPORT.md). Card: `research/wf_ideas_v4/round29/finals_card_v5_ru.md` (a134d5e4; l.59 A-M2 text stale, l.129 V_CI list). Background: `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v3/FINAL_REPORT.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` ORPHANS l.928 ff. and CHANGES (36) l.219)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-570 | CLARIFY: SEC files stay in the V_pub pool; rule (a) = 'running champion'; ORDER (1) SEC-tie exception; exp89t 4 levers | At risk: log BEFORE exp89r's first header (~09:23Z, latest 11:00Z) | R36-A2; `FACTS.md` C-288..C-290 |
| I-571 | 08:30Z timer line: A-M1 UNUSED, no 08:40Z list, exp89l not sent, exp89t outside the timer | At risk, overdue, 0 Kaggle calls | R36-A3; PC36-06 |
| I-486 / I-572 | exp89t submit at dummy PASS + post_exp89t watcher + PENDING line; read-time logistics for exp75 / exp89r | In-plan; (1) of I-572 superseded by the hold | `CONTEXT.md` l.4426-4432; R36-A4 |
| I-568 / I-569 | Rule (a) code at exp89r's read; slot-2 ask ~11:55Z, apply at 12:00Z | Logged; execution pending | `CONTEXT.md` l.4404-4414, l.4433-4440 |
| I-573 / I-526 / I-539 / I-548 | Card v5 FILLED copy: 'exp89t = ' token, V_CI list, l.59 actual slot-2 outcome, R35-A2 П1 deletions, rank line | At risk: 12:03Z; re-check 18:37Z / 19:43Z | R36-A5; `FACTS.md` C-294 |
| I-540 | 'Pair by the card' wording, never 'рекомендую' | At risk: 18:37Z message | `IDEAS.md` ORPHANS |
| I-336 / I-252 | Hindsight guard pushed before 23:00Z; lab->LB lessons H2/H3 | At risk | `IDEAS.md` ORPHANS l.928 ff. |
| I-233 | Poller logs error_description | Strict orphan, no owner | `research/wf_ideas_v4/round4/report.json` R4-A9 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/36/{ideas,facts,watch}.json`)

1. [now] **Round 36 vs the user (all three):** do NOT re-ask about exp89t (R36-A1 answered 08:27Z); do NOT send exp89s at exp89r's read (R36-A4 (1) vs the 08:28Z hold); round 37 must read `CONTEXT.md` l.4426-4440. Sources: `research/wf_ideas_v4/round36/report.notes.md`; `FACTS.md` C-291, C-292.
2. [now] **exp89t submit** at dummy PASS (~08:55-09:05Z, not later than ~09:30Z), -m 'probe 55: ...', then watcher + PENDING line; gate fail -> no submit, push the user. Sources: `CONTEXT.md` l.4415-4432; `WATCHLIST.md` T206/W329.
3. [now] **R36-A2 CLARIFY line** (I-570) before exp89r's first terminal header, stamped with the current poll header; after the read it is post-hoc. Sources: `research/wf_ideas_v4/round36/v_plancheck_pc36-01.json`, `v_plancheck_pc36-02.json`.
4. [now] **R36-A3 08:30Z timer line** (I-571) overdue; do not start the 08:40Z waiter. Source: `research/wf_ideas_v4/round36/report.json` R36-A3.
5. [today] **Reads:** exp75 (EXP75 PARTNER RULE v2 + GAP RULE v2 (5)); exp89r -> display, L, DIS estimate, B25 side line (R35-A3), UP test at 0.959 with a count-54 S0 (post_exp75 or 0813Z). Sources: `CONTEXT.md` l.4381-4393; `FACTS.md` F-RUN-53.
6. [today] **Slot-2 ask has no timer** (only 11:10Z and 12:03Z exist); the 11:10Z timer text 'submit by 11:30Z' is a pointer only. Quote I400 (SEC x CI ~+0.0004) and I401 (P(exp89s wins | d_R)). Sources: `research/wf_ideas_v4/round36/scan_plancheck.notes.md`; `WATCHLIST.md` T209/W334, C2. (Watch only.)
7. [today] **Late windows:** exp89s at 12:00Z reads ~19:01-19:49Z (11-59 min before the tick; breaks l.3685); exp89t tail up to ~10.9 h; arm watchers with immediate MSK push; record the user override of R8 in one CONTEXT line. Sources: `CONTEXT.md` l.1671, l.3683-3687; `FACTS.md` C-293.
8. [today] **Card v5 fill 12:03Z:** FILLED copy only (template a134d5e4): I-573 (a)-(e) + R35-A2 + R34-A2; state 'V_pub exp89s and exp75 <= 0.953 -> no CI in the finals' (I405). Sources: `research/wf_ideas_v4/round29/finals_card_v5_ru.md` l.59, l.129; `FACTS.md` C-294.
9. [today] **Records missing:** `experiments/RESULTS.md` rows P47-P51, P54 (0.955 / 0.957 / 0.955 / 0.958 / 0.959 / 0.956), P52/P53/P55 as they read; REPORT.md rounds 29-35; round 36 untracked. (Settled: ideas / facts [before-finals] vs watch [today] -> [today] after the morning decisions, as in c33-c35.)
10. [before-finals] **Finals messages:** 18:37Z (exp89t may still be PENDING -> re-fill at its header), 19:43Z, 20:00 UTC tick, SELECTED check ~20:00-20:30Z; hindsight guard before 23:00Z. Sources: `CONTEXT.md` l.3851-3855, l.4091-4099.
11. [info] **744273 (sghwr):** edge-only post-proc tweak flat twice on public = external null for our edge-filter closure (probes 29/30, I-161); no build. Source: https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744273

**RESOLVED since curation 35:** exp89p read (A-M1 UNUSED, logged 07:59Z); R35-A1/A2/A3/A5 logged 07:46Z (I-564, I-565 off at-risk); C11 record logged (I-559); first MSK brief overtaken by the exp89t yes (I-540); CI-dataset guard moot (I-567); E10 runbook l.66 downgraded (live loop uses >= 0.960, `experiments/lb_poll/e10_watch_loop.py` l.78) (`CONTEXT.md` l.4381-4403; `WATCHLIST.md` W286 (2)).

## HOW TO USE

- "Score of probe N?" -> `DECISIONS.md` §1; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log`; `experiments/<exp>/probe.json`.
- "exp89r / exp75 scored; what now?" -> `CONTEXT.md` l.4404-4414 + l.4433-4440 (rule (a) + hold), l.4381-4393 (UP test, B25), I-570 / I-572.
- "Submit exp89t / exp89s?" -> `CONTEXT.md` l.4415-4440, l.4361-4380 (commands, guards); `DECISIONS.md` l.204-205, l.1732-1733.
- "Which finals pair?" -> card v5 + I-573 / I-548 / I-565; `DECISIONS.md` §2 l.991.
- "Which rule decides this?" -> `DECISIONS.md` §3 l.1607; `FACTS.md` §5 l.329 and CONTRADICTIONS l.504. "Tried?" -> `IDEAS.md`. "True?" -> `FACTS.md`. "Next / overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~08:50Z 29 Sep, read the tail of `CONTEXT.md` §14 (above `## 9.`), the newest `===` header in `poll.log`, and `research/wf_ideas_v4/round37/` or later.
