# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 31: state as of 2026-09-29 ~02:55 UTC (05:55 MSK). Git HEAD d6deab5 ('Round 30: morning/finals text resolutions (running champion, A-M1 trigger), card v5 edits'), after afebb5d (night batch) (`git log`). `CONTEXT.md` has 4,314 lines; newest entry 02:02Z l.4273-4293; `## 9. Literature` l.4294. Uncommitted: `research/KNOWLEDGE/*` curation-31 edits, `experiments/lb_poll/ledger.md`, `poll.log`, E10/feed logs. Untracked: `research/wf_ideas_v4/round31/` (report.json R31-A1..A5 written 02:38Z, 4 scans, 7 verdicts, NO REPORT.md), `experiments/e10_watch/20260929T0213Z.txt`, `0241Z.txt`, `experiments/discussions/digest_20260929T0227Z.md`, `experiments/lb_poll/_night_subs.csv` (`git status`). Previous curation: 30 (~02:00Z). Times are UTC unless marked MSK (= UTC+3).
Deadline 29 Sep 23:59. The user ticks the finals MANUALLY by 20:00 UTC = 23:00 MSK; the session never ticks (`CONTEXT.md` l.3842-3855, l.4092). Rule anchors: PRE-REG v3 l.1576-1736; tie order l.3181 (reading fixed 02:02Z (2)); MORNING TABLE v1.1 l.3931-3955; GAP RULE v2 l.4009-4020; RULE v2.1 + exp89l gate l.4104-4126; 21:11Z A-M2 precedence l.4134-4152; W4 FREEZE l.4174-4253; morning/finals texts l.4273-4293.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 exp58 = 0.954 + #38 exp58n = 0.953, both below V_pub; plan {V_pub, #37 or exp75}; only the user's tick changes it (`CONTEXT.md` l.4041-4050; `DECISIONS.md` §2 [c31] l.963-980).
2. **Best = P51 exp87a (K + CI) = 0.959 = V_pub, branch A.** Rank #132 of 3,979 at 02:14Z / 02:42Z, 17th of 21 in the 0.959 block; medal lines moved up one block (bronze ~#398 in 0.955, silver ~#199 in 0.957) (`FACTS.md` F-LB-31 l.257; `experiments/e10_watch/20260929T0213Z.txt`).
3. **No new LB score:** P52 exp89r (56656147), P53 exp75 (56656157), P54 exp89p (56657612) all PENDING at the 02:44:13Z header; 2 submits left on 29 Sep (`experiments/lb_poll/poll.log` l.27644; `DECISIONS.md` §1 l.196-199).
4. **Logged 02:02Z (R30-A1):** A-M1 exp89l only on exp89p >= 0.959 (0.958 = UNUSED, no uptest); running champion, CONSERVATIVE reading (k = 0 tie keeps exp87a); SEC/Rr cell -> UNUSED; no rebuild/re-push at 07:23Z; card v5 -> sha8 aab8801a (`CONTEXT.md` l.4273-4293; `FACTS.md` F-RUL-27 l.342).
5. **Open pre-score bug:** the R30-A2 (a) A-M2 bullet that 02:02Z (5) says to paste drops the Rr '+' condition -> would send exp89q where MORNING TABLE v1.1 says UNUSED (`FACTS.md` C-259 l.730; `research/wf_ideas_v4/round31/v_plancheck_pc31-01.json` CONFIRMED).
6. **Round 31 proposals R31-A1..A5, none logged:** A-M2 function + 08:40Z header + read-only rounds + card pool L (A1); wake push (A2); read-time log (A3); card numbers (A4); I-045 note (A5) (`research/wf_ideas_v4/round31/report.json`; `DECISIONS.md` §2h l.1478-1482).
7. **Latency families:** non-CI 6.87-7.81 h, CI 9.27-9.48 h; poller cadence ~601.7 s puts headers near 08:35:1x / 08:45:1x, not 08:40 (`FACTS.md` F-RUN-48 l.310, C-261 l.732).
8. **Card v5 (aab8801a) still stale:** model numbers for V_pub exp85a (l.37-48), non-CI L_hi 8.0 h at l.17 / l.124 vs logged 9.0 h, l.114 '+/0u' (`FACTS.md` C-260, C-263, F-TRN-63 l.466; `research/wf_ideas_v4/round29/finals_card_v5_ru.md`).
9. **Mode:** user asleep, AUTONOMOUS since 20:07Z; submits only by logged rules; watchdog 10576 one-shot; E10 null (trigger >= 0.960, loop exits 12:00Z), feed digest 02:27Z null (`CONTEXT.md` l.4081-4093; `experiments/discussions/digest_20260929T0227Z.md`; `DECISIONS.md` §2f l.1256).
10. **Next decision points:** now: R31-A1 entry (hard limit = first header with a night ref terminal, earliest ~07:38Z); 04:13Z wake push; 06:07Z post-wake; 07:23Z prep only; A-M1 at exp89p's terminal header (08:40Z header, submit by 08:45Z); A-M2 at exp89r's terminal header (latest 11:00Z, submit by 11:30Z); 12:03Z card; 18:37Z proposal; 20:00Z user tick; 23:59Z deadline (`WATCHLIST.md` NEXT 24 H l.73, LATER l.97). Ideas 549 (in-plan 149, refuted 261, lb-tested 62, lab-tested 28, deferred 47, open 2) (`IDEAS.md` l.200-211).

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` = this page. `CHANGES.md` = per-curation deltas (v4, 2-31). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,31}/` (`*.json` = structured answers, `*.notes.md` = crash-safe logs).
- `IDEAS.md` + `ideas.json` (I-001..I-549): CHANGES (31) l.200, ranking l.213, FINALS l.232, LADDER l.320, BASE l.421, RUN l.463, LOC l.535, DIV l.571, MODEL l.643, NODES l.695, INFER l.732, EF l.754, LINK l.774, VALID l.812, TESTSET l.866, ORPHANS l.884.
- `FACTS.md`: §1 metric l.185, §2 data l.202, §3 LB l.223 (F-LB-31 l.257), §4 runtime l.259 (F-RUN-48 l.310), §5 rules l.312 (F-RUL-27 l.342), §6 models l.344, §7 lab-to-LB l.400 (F-TRN-63 l.466), CONTRADICTIONS l.468 (C-259..C-265 l.730-736).
- `DECISIONS.md`: probes §1 l.137 (P51-P56 l.195-199; [c31] build update l.540); gates §1b l.542; finals §2 l.607 ([c31] snapshot l.963-979); E10 §2f l.1105 ([c31] l.1256); ladder/cards §2h l.1289 (R30-A1..A5 l.1473-1477, R31-A1..A5 l.1478-1482); R1-R10 §3 l.1484.
- `WATCHLIST.md` (curated ~02:50Z): OVERDUE l.61 (W304, W296/W303, W279 (1), W297, W126, W286 (2)), NEXT 24 H l.73 (T187-T191, W305-W308), LATER l.97, INSIGHTS l.127 (I358-I365).

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows to P46 only); `experiments/lb_poll/poll.log`, `ledger.md`; `experiments/e10_watch/watch_loop.log` + `2026*.txt`; `experiments/discussions/feed_loop.log` + `digest_*.md`.
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `exp58n_x138_safe_lowref/` (#38); V_pub `exp87a_k2cap6_div04_ra094_ci/`; night `exp89r_k2cap6_k_sec_dis225_ci/`, `exp75_k2_coordinject/`, `exp89p_k2cap6_k_sec/`; morning `exp89l_k2cap6_k_sec_ci/` (A-M1), `exp89s_k2cap6_k_dis225/`, `exp89q_k2cap6_k_sec_dis225/` (A-M2); prior best `exp85a_k2cap6_div04_ra094/`; base `exp70g_k2_cap6/`.
- Tools: `tools/build_probe_kernel.py`, `tools/runtime_ledger.py` (admit rule l.197-199; `--print` rewrites ledger.md), `tools/dummy_gates.py`, `tools/uptest.py`, `tools/e10_port_gate.py`, `tools/kaggle_feed.py`.
- Round 31 (untracked): `research/wf_ideas_v4/round31/report.json` (R31-A1..A5, new_facts, plan_issues, rejected, next_focus), `report.notes.md`, `scan_{plancheck,recheck,hyp_private31,browser}.json`, `v_*.json`. Round 30: `round30/report.json` (R30-A2 morning grid). Round 29: `round29/finals_card_v5_ru.md` (fill source), `night_checklist.md`. No REPORT.md for rounds 29-31. E10 runbook `research/wf_ideas_v4/e10v3/runbook.notes.md` (l.66 stale). Background: `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v3/FINAL_REPORT.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` ORPHANS l.884 ff. and CHANGES (31) l.200)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-543 | A-M2 decision function restoring Rr '+': DIS '+' -> exp89s; else Rr '+' and DIS '?' and P in {+,?} -> exp89q; else UNUSED | At risk: log pre-score; paste at 07:23Z instead of R30-A2 (a) | `round31/report.json` R31-A1 (1); `v_plancheck_pc31-01.json` |
| I-544 | '08:40Z header' = last poll.log header <= 08:40:36Z; one manual list at 08:40:00Z if 56657612 PENDING at 08:30Z | At risk: log in the R31-A1 entry | R31-A1 (2); `FACTS.md` C-261 |
| I-530 | Rounds 07:13-10:13Z read-only (<= 5 min); next full round at the 11:10Z tail | At risk: never logged | R31-A1 (3); `v_plancheck_pc31-05.json` |
| I-545 / I-539 | Card v5 non-CI pool L_hi <= 9.0 h (l.17, l.124) + two section-4 info lines | At risk: edit, new sha8, same entry | R31-A1 (4); R30-A5 (3); `FACTS.md` C-260 |
| I-546 / I-497 | 04:13Z Russian wake/power push; 06:07Z battery check + battery-tolerant watchdog re-arm | At risk | R31-A2; `FACTS.md` C-262 |
| I-548 | Card fill numbers for V_pub exp87a: П2 0.63-0.85 / 0.43-0.68, П3 0.61-0.83, ticked bronze 0.20-0.58; silver caveat | At risk: use at 12:03Z; never 'не медаль' | R31-A4; `FACTS.md` F-TRN-63 |
| I-547 | Read-time log: L vs family range at each first terminal header | In-plan, info | R31-A3 |
| I-336 / I-233 / I-516 / I-448 / I-045 | Hindsight guard pushed before 23:00Z; poller error_description (strict orphan); truncation line; builder hardening; I-045 WEAKENED-not-overturned note | Carried; one line each | `IDEAS.md` ORPHANS l.884 ff.; R31-A5 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/31/{ideas,facts,watch}.json`)

1. [now] **R31-A1 / W304 pre-score entry:** one CONTEXT entry above `## 9. Literature` (l.4294) quoting a header with all 3 night refs PENDING (02:44:13Z qualifies): (1) A-M2 function (I-543); (2) 08:40Z header definition + manual list (I-544); (3) read-only rounds 07:13-10:13Z (I-530); (4) card l.17/l.124 non-CI L_hi <= 9.0 h + I-539 info lines + new sha8; fold in R30-A3..A5, W279 (1) DET_THRESHOLD and W297 'cron defect, not battery'. Hard limit: first header with a night ref terminal (earliest ~07:38Z), at the latest the 07:23Z prep. Sources: `round31/report.json` R31-A1; `FACTS.md` C-259..C-262; `WATCHLIST.md` l.65. (Settled: facts put (2) at [today], ideas/watch [now] -> [now], one entry.)
2. [now] **E10 runbook trigger stale:** `research/wf_ideas_v4/e10v3/runbook.notes.md` l.66 'SC >= 0.958' -> '>= 0.960 (OUR = 0.959)'; fix before the 03:41Z E10 run. Source: `WATCHLIST.md` W286 (2); `CONTEXT.md` l.4159-4160.
3. [today] **Wake/power (R31-A2):** 04:13Z (07:13 MSK) one Russian push with MSK times (no tick request); 06:07Z if on battery re-push and re-arm a battery-tolerant watchdog (10576 is one-shot). If the laptop sleeps through ~11:30Z, A-M2 and the 12:03Z card are lost. Sources: R31-A2; `FACTS.md` F-RUN-45, F-RUN-46.
4. [today] **Morning (MORNING TABLE v1.1, branch A):** 07:23Z prep only (no rebuild/re-push, nb_try '-v 1'). A-M1 exp89l iff exp89p >= 0.959 at the 08:40Z header, submit by 08:45Z (11:45 MSK). A-M2 by the I-543 function at exp89r's terminal header (~09:25-09:35Z, latest 11:00Z), submit by 11:30Z (14:30 MSK). exp87a stays V_pub unless a later file shows >= 0.960 or an attributable UP at 0.959. Submit at the decision header. Sources: `CONTEXT.md` l.4273-4293; `DECISIONS.md` l.196-199.
5. [today] **Card v5 numbers stale (R31-A4):** l.37-48 computed for exp85a on the 28 Sep 13:18Z field; ticked pair overstated by ~0.1-0.3. At 12:03Z (15:03 MSK) use mc31v numbers + silver caveat + medal-line rank line from the newest e10_watch file; refresh 18:37Z; re-run mc31v.py only if V_pub changes. Sources: `FACTS.md` C-263, F-TRN-63; `WATCHLIST.md` W307. (Settled: facts [before-finals] vs ideas/watch [today] -> [today], hard limit 12:03Z.)
6. [today] **Records missing:** `experiments/RESULTS.md` has no rows P47-P51 (0.955 / 0.957 / 0.955 / 0.958 / 0.959) or P52-P54; REPORT.md absent for rounds 29-31; round 31 uncommitted. Sources: `FACTS.md` C-118; `WATCHLIST.md` W126, W296/W303. (Settled: [today], before the 12:03Z card; after the morning decisions.)
7. [before-finals] **Finals messages:** 12:03Z card, 18:37Z proposal, 19:43Z reminder, 20:00Z user tick, verify SELECTED ~20:00-20:30Z, 21:05Z last call; say 'the pair by the card', never 'рекомендую' / 'не медаль'; choose the partner by bronze and insurance, not silver (silver slightly favours {exp87a, exp85a}). Sources: `CONTEXT.md` l.3851-3855; `WATCHLIST.md` I361; `FACTS.md` C-264.
8. [info] **Orphans / notes:** I-547 read-time log; I-045 'WEAKENED, stays closed' curator line (post-deadline OK); `runtime_ledger.py --print` rewrites ledger.md (harmless). Sources: R31-A3, R31-A5; `WATCHLIST.md` I356, I364.

**RESOLVED since curation 30:** R30-A1 / W298 logged 02:02Z (A-M1 trigger, conservative tie reading, SEC/Rr -> UNUSED, '0u' unreachable, no rebuild) and committed d6deab5; card v5 l.21/l.59/l.106 edits (sha8 aab8801a) (`CONTEXT.md` l.4273-4293; `FACTS.md` C-245, C-247, C-250..C-252).

## HOW TO USE

- "Score of probe N, and what changed?" -> `DECISIONS.md` §1; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log` (P47 onward); `experiments/<exp>/probe.json`.
- "exp89p / exp89r / exp75 scored; what now?" -> `CONTEXT.md` l.3931-3955, l.4273-4293 + the R31-A1 entry once logged; `round31/report.json` R31-A1; `round30/report.json` R30-A2/A3; `tools/runtime_ledger.py` l.197-199.
- "Which morning file, and how do I submit it?" -> `round31/report.json` R31-A1 (1)(2) + `round30/report.json` R30-A2; `DECISIONS.md` §1 l.196-199, §2h l.1473-1482; `WATCHLIST.md` NEXT 24 H l.73.
- "Which pair do we propose for the finals?" -> `research/wf_ideas_v4/round29/finals_card_v5_ru.md` (after R31-A1 (4) edits) + R31-A4 numbers; `DECISIONS.md` §2 l.963-980; `CONTEXT.md` l.4041-4050.
- "Did a public notebook beat us (>= 0.960)?" -> `experiments/e10_watch/watch_loop.log`; `experiments/discussions/feed_loop.log`; `DECISIONS.md` §2f l.1256.
- "Which rule decides this?" -> `DECISIONS.md` §3 l.1484; `FACTS.md` §5 l.312 and CONTRADICTIONS l.468; `CONTEXT.md` l.1576-1736. "Was idea X tried?" -> `IDEAS.md`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~02:55Z 29 Sep, check the tail of `CONTEXT.md` §14 (above `## 9.`), the newest `===` header in `poll.log`, and `research/wf_ideas_v4/round31/` or later round folders.
