# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 27: state as of 2026-09-28 ~16:40 UTC (19:40 MSK). Git HEAD da5ce54 ('743929 overfitting comment; user agrees with the hedge pair'), after 00e2603 (laptop on AC), 756c513 (round 27 committed, incl. `research/wf_ideas_v4/round27/`), 608d950, 7faa8cf, eea3793, dba59bd. Uncommitted: `research/KNOWLEDGE/*` curation-27 edits, `experiments/lb_poll/ledger.md`, `poll.log` (`git status`). Previous curation: 26 (~14:10Z, 5e5fd1b). Times are UTC unless marked MSK (= UTC+3); every line cites its source.
Deadline: 29 Sep 23:59. Finals are ticked MANUALLY by the user by 20:00 UTC = 23:00 MSK on 29 Sep; the session never ticks (`CONTEXT.md` l.3842-3855). `CONTEXT.md` gained 13 entries at l.3924-4050 (last 16:32Z); `## 9. Literature` is now at l.4051. Anchors:
- Rules: PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147; LADDER + L9 l.2407-2424; FINALS CARD 04:31 l.3417-3430; A2 + P50/P51 read rule 11:17 l.3717; Q3 = YES l.3834; night list confirmed 12:25 l.3899.
- Since c26: **R8 COVERAGE night files** 14:12 l.3924; **MORNING TABLE v1.1** l.3931; **exp89s built + gate** l.3956; **EXP75 PARTNER RULE v2** l.3965; **exp89s PASS** 14:40 l.3974; **OPS outage + user defaults** 15:43 l.3979; **API LOAD CUT** 15:57 l.3988; **standby CORRECTION + power ask** 16:26 l.3999; **GAP RULE v2** l.4009; **DIS runtime = sibling** l.4021; **card v4 stored + R27 facts** l.4029; **laptop ON AC** 16:30 l.4035; **743929 overfitting comment + user agrees with the hedge pair** 16:32 l.4041.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 exp58 (56563521) = 0.954 + #38 exp58n (56563534) = 0.953, both below V_pub; only the user's own tick changes them. Plan agreed by the user 16:32Z: {V_pub, #37 or exp75 if >= 0.955 clean}; the partner carries neither K nor cap 6; the JT-style {best + neighbour} pair is NOT recommended (`CONTEXT.md` l.3851-3855, l.4041-4050; `FACTS.md` F-RUL-22; `DECISIONS.md` §2 [c27] l.842-844).
2. **Team best: P50 exp85a (exp70g + ILP_DIVISION_WEIGHT 0.4 + READMIT 0.94 = 'K', non-CI, 56629533) = 0.958 = V_pub;** rank 138 of 3,968 at 15:43Z (14th of 21 in the 0.958 block; 124 teams >= 0.959); E10 null, trigger >= 0.959 (`CONTEXT.md` l.3856-3862, l.4029-4034; `FACTS.md` F-LB-27 l.249).
3. **PENDING:** P51 exp87a (K + CI, 56640366, sent 12:14:57Z) at the 16:32:08Z header; read earliest ~20:50Z, expected 21:30-22:15Z; '?' threshold 22:26:57Z now softened by GAP RULE v2 ('+'/'0u' late -> UNPROVEN-ins, a normal read) (`experiments/lb_poll/poll.log` l.23871-23874; `CONTEXT.md` l.4009-4020).
4. **Ops:** laptop back ON AC at 16:29Z (51%); watchdog notifies on battery or poll header > 25 min; the 15:00-15:39Z "outage" was lid standby on battery; Kaggle API load cut (feed every 90 min) after a ban report elsewhere (`CONTEXT.md` l.3988-4008, l.4035-4040; `FACTS.md` F-RUN-44, F-RUL-23).
5. **Budget:** 28 Sep slots 5/5 used (no submit before 00:00Z). GPU: API says 9,988.9 of 21,600 s used at 15:44Z (~3.2 h left), disagrees with the Settings page; plan on 2.2-3.2 h (`CONTEXT.md` l.4033; `FACTS.md` C-227).
6. **Night 29 Sep (user-confirmed 12:25, all dummies PASS):** 00:05Z exp89r (K + SEC + DIS 2.25 + CI) if P51 reads '+'/'0u', else exp89q (K + SEC + DIS 2.25); 00:06Z exp75 (#37 + CI, v1); 00:46Z exp89p (K + SEC). No COMPLETE P51 header by 23:30Z -> exp89q (`CONTEXT.md` l.3899-3923; `DECISIONS.md` §1 P52-P54 l.192-194).
7. **Morning 29 Sep:** MORNING TABLE v1.1 logged (branch A: M1 exp89l if P '+'/'0u', M2 exp89s/exp89q; branch B: M1 exp89s on DIS '+'); exp89s (K + DIS 2.25, 8ed72e32) PASS 14:40Z; exp89l built only at P51's read in branch A; user defaults: no exp89t, no exp89u (`CONTEXT.md` l.3931-3987; `DECISIONS.md` §1 P55-P56 l.195).
8. **Unlogged (round 27):** RULE v2.1 compute gate (R27-A3 (2)); 23:30Z freeze line (R27-A4, incl. R26-A4 masking fix); 00:04Z checklist + nb_try exit-3 fix + backup crons (R27-A5); two user questions (R27-A6); decision-header submit + V_pub re-check in 58b6ded3 (R27-A7); card v4 edits + Q3 П1 line (R27-A8); DET-closed line + KEY FACTS (R27-A9 (1)(3)) (`research/wf_ideas_v4/round27/report.json`; `DECISIONS.md` §2h l.1311-1319).
9. **Next decision points:** 17:47Z round 28 (KEY FACTS); 17:57Z tick check; ~20:50-22:30Z P51 read -> branch A/B (+ exp89l build in A); 23:30Z freeze (cron 5ece5d24 23:33Z); 00:04Z night batch (2ab38c73); ~07:00Z night reads; 07:23Z morning prep; 12:03Z card v4; 18:37Z FINAL proposal; 19:43Z reminder; 20:00Z user tick (`WATCHLIST.md` NEXT 24 H l.102, LATER l.126).
10. **Ideas ledger:** 509 ideas (lb-tested 61, lab-tested 26, in-plan 128, refuted 245, deferred 47, open 2); strict orphan I-233; 13 at risk (`IDEAS.md` CHANGES (27) l.181, ORPHANS l.824; `ideas.json` meta.curations[n=27]).

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` = this page. `CHANGES.md` = per-curation deltas (v4, 2-27). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,27}/`.
- `IDEAS.md` + `ideas.json` (I-001..I-509): CHANGES (27) l.181, ranking l.193, FINALS l.212, LADDER l.288, BASE l.378, RUN l.419, LOC l.482, DIV l.518, MODEL l.588, NODES l.640, INFER l.677, EF l.699, LINK l.719, VALID l.755, TESTSET l.806, ORPHANS l.824.
- `FACTS.md`: §1 metric l.181, §2 data l.198, §3 LB l.219 (F-LB-27 l.249), §4 runtime l.251 (F-RUN-42..44 l.296-298), §5 rules l.300 (F-RUL-23 l.326), §6 models l.328 (F-MOD-49/50 l.380-381), §7 lab-to-LB l.383 (F-TRN-59 l.445), CONTRADICTIONS l.447 (C-219..C-228 l.669-678).
- `DECISIONS.md`: probes §1 l.133 (P51-P56 l.191-195; [c27] builds l.490-492); gates §1b l.501; finals §2 l.566 ([c27] l.842, snapshot l.844); E10 §2f l.985 ([c27] l.1128); ladder/cards §2h l.1161 ([c27] rows l.1305-1319); R1-R10 §3 l.1321 ([c27] rows l.1403 ff.).
- `WATCHLIST.md` (curated ~16:25Z): OVERDUE l.85 (W271-W280), NEXT 24 H l.102 (T164-T169), LATER l.126, INSIGHTS l.152 (I315-I326; I306 retired).

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows to P46 only, l.79); `experiments/lb_poll/poll.log`, `ledger.md`, `_lb/`, `dataset_baseline/`; `experiments/e10_watch/watch_loop.log`; `experiments/discussions/feed_loop.log` + `digest_*.md`; `experiments/lb_poll/run_feed_loop.sh`.
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `exp58n_x138_safe_lowref/` (#38); best `exp85a_k2cap6_div04_ra094/`; P51 `exp87a_k2cap6_div04_ra094_ci/`; night `exp89r_k2cap6_k_sec_dis225_ci/`, `exp89q_k2cap6_k_sec_dis225/`, `exp75_k2_coordinject/`, `exp89p_k2cap6_k_sec/`; morning `exp89s_k2cap6_k_dis225/` (built, PASS); base `exp70g_k2_cap6/`. exp89l not built (branch A only).
- Tools: `tools/build_probe_kernel.py`, `tools/runtime_ledger.py` (l.42 RETRY_SLACK_S 210; 't' added), `tools/dummy_gates.py`, `tools/uptest.py`, `tools/e10_port_gate.py`, `tools/kaggle_feed.py`.
- Rounds: `research/wf_ideas_v4/round27/report.json` (R27-A1..A9, 16:20Z; `report_md_ru`), `finals_card_v4_ru.md`, 5 `scan_*.json`, 13 `v_*.json`; no REPORT.md for rounds 24-27. Older: `round26/`..`round8/`, `knobarms_28sep/`. Background: `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v3/FINAL_REPORT.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` ORPHANS l.824 ff.)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-503 | Mechanical 23:30Z W4 freeze line (R27N-2 + LATE rule; GAP RULE v2; exp89p timing; exp75 kept under C51 '-') | Fill and log at 23:30Z, pre-score | ORPHANS; `round27/report.json` R27-A4 |
| I-504 | 00:04Z checklist G0-G5 + nb_try (limit/allowance/daily -> exit 3 STOP) + backup crons 00:20/00:50/01:30Z | Replace cron 2ab38c73 prompt at the freeze | ORPHANS; R27-A5 |
| I-501 | RULE v2.1: dummy gate on compute (CI: exp89r 1,473 s -> <= 1,620 s) | Log before any exp89l dummy (branch A, ~20:50Z+) | ORPHANS; R27-A3 (2) |
| I-490 / I-491 / I-492 | UP masking relaxation; night hygiene; finals pool + PENDING branch | Inside the freeze line (item 5) / checklist / card | ORPHANS; R26-A4 |
| I-485 | exp89l = K + SEC + CI (cad1d47f), branch-A M1 | Build + coverage + v2.1 gate + dummy at P51's read, before 23:30Z | ORPHANS; R26-A3 (3) |
| I-498 / I-499 | User questions: keep-awake process; exp89p at 00:07Z in branch A | Ask (MSK first); defaults no / 00:46Z | ORPHANS; R27-A6 |
| I-507 / I-508 | Submit morning files at the decision header; Q3 conditional line for pair П1 | Log with the freeze line | ORPHANS; R27-A7 (2), R27-A8 |
| I-233 | Poller logs error_description (strict orphan) | Close in one line | ORPHANS |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/27/{ideas,facts,watch}.json`)

1. [today] **Power, partly resolved:** on AC at 16:29Z (BatteryStatus 2) and the watchdog is re-armed; the lid must stay open (lid action hidden in powercfg; session declined to change OS settings); on battery, display-off idle alone enters standby (I315). Re-check at round 28 (17:47Z), 23:25Z and 00:03Z. Sources: `CONTEXT.md` l.3999-4008, l.4035-4040; `FACTS.md` F-RUN-44; `WATCHLIST.md` W271, T168, I315.
2. [today] **P51 read ~20:50-22:30Z decides the 00:05Z file** (exp89r vs exp89q) and whether exp89l is built. GAP RULE v2 is logged; do not restart the poller 21:00-22:30Z unless its header is > 15 min old; tighten L_hi from e10_watch snapshots. Sources: `CONTEXT.md` l.4009-4020; `poll.log` l.23871; `WATCHLIST.md` T165, I316; `IDEAS.md` I-438, I-500.
3. [today] **RULE v2.1 not logged** (gate v2 <= 2,100 s would fail a CI dummy ~30-40% of the time on rglob setup noise). Log before the exp89l dummy. Sources: `CONTEXT.md` l.4021-4028; `FACTS.md` F-RUN-42, C-220; R27-A3 (2); `WATCHLIST.md` W274.
4. [today] **23:30Z freeze + 00:04Z batch not yet written:** R27N-2 line (with R26-A4 (a)-(e), LATE rule, decision-header and Q3 П1 lines), checklist + nb_try, backup crons; no rule for a failed/timed-out submit (list submissions before any retry); session crons lost in standby. Sources: R27-A4, R27-A5, R27-A7, R27-A8; `round27/scan_hyp_nightdry.json` R27N-2/3; `FACTS.md` C-225, F-MOD-50; `WATCHLIST.md` W275, W276, I322.
5. [today] **nb_try 'limit' hole:** its HARD-FAIL regex matches 'limit', so a daily-allowance error sends exp83c in exp89p's place. Map limit/allowance/daily to exit 3 = STOP. Sources: R27-A5; `FACTS.md` F-MOD-50; `WATCHLIST.md` I318, T169.
6. [today] **MASKED coded '0' in MORNING TABLE v1.1:** exp75's read window (~09:00-09:50Z) overlaps exp89r's; log the masking relaxation (I-490) in freeze item (5) before ~07:00Z. Sources: `CONTEXT.md` l.3931-3955, l.3785-3786; `IDEAS.md` I-490.
7. [today] **R27-A6 questions not in CONTEXT** (keep-awake; exp89p 00:07Z in branch A). Ask once; log answers or defaults in freeze item (4). Sources: `CONTEXT.md` l.3999-4008 (charger only); R27-A6; `IDEAS.md` I-498, I-499; `WATCHLIST.md` W272.
8. [today] **Records:** `experiments/RESULTS.md` lacks P47-P50 (0.955 / 0.957 / 0.955 / 0.958); REPORT.md missing for rounds 24-27; KEY FACTS for round 28 not refreshed (rank 138, DIS runtime = sibling, exp89t/u no); 17:57Z tick check and 23:00-23:45Z LB snapshot not in the cron. Sources: `FACTS.md` C-118; R27-A9 (3); `WATCHLIST.md` W126, W280, W270.
9. [before-finals] **Card v4 + finals path:** 4 defects (l.31 opener, l.40 П3 silver range, token keys on probe numbers, exp83c missing) to fix before the 12:03Z fill; Q3 vs П1 conflict (C-223); fold the V_pub re-check into cron 58b6ded3 (19:43Z); morning files submitted at the decision header (C-228); DET-closed line before 07:23Z. Sources: `round27/finals_card_v4_ru.md`; R27-A7, R27-A8, R27-A9 (1); `FACTS.md` C-223, C-224, C-226, C-228.
10. [info] GPU API figure vs Settings page disagree (C-227); no new Kaggle loops (ban report, I317); 0.956 wave of 7 teams, below the P2 trigger of 5 per window (I323); orphan I-233. Sources: `FACTS.md` C-227, F-RUL-23; `WATCHLIST.md` I317, I323; `IDEAS.md` ORPHANS.

**RESOLVED since curation 26:** R26-A6 message sent, defaults applied (no exp89t/u; depth-cap reading stands) (`CONTEXT.md` l.3979-3987); R8 coverage for exp89p/q/r (l.3924); depth cap + MORNING TABLE v1.1 (l.3931); exp89s built + PASS, ledger 't' (l.3956, l.3974); EXP75 PARTNER RULE v2 (l.3965); outage cause corrected (l.3999); GAP RULE v2 (l.4009); 'DIS +15-20%' retracted (l.4021; I-502); card v4 stored (l.4029); laptop on AC (l.4035); round 27 committed (756c513); hedge-pair plan confirmed by the user after the 743929 'overfitting' comment (l.4041-4050).
**Settled curator disagreements:** power [now] (all three, written before 16:29Z) -> [today], since 00e2603 logs AC; night hardening [before-finals] (facts) vs [today] (ideas, watch) -> [today], since it is due at 23:30Z.

## HOW TO USE

- "Score of probe N, and what changed?" -> `DECISIONS.md` §1; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log` (P47 onward); `experiments/<exp>/probe.json`.
- "P51 scored; which file goes at 00:05Z?" -> `CONTEXT.md` l.3717 (A2), l.3899-3907, l.4009-4020 (GAP RULE v2); `DECISIONS.md` §1 l.191-194.
- "What goes out tonight / tomorrow morning?" -> `CONTEXT.md` l.3899-3978; `round27/report.json` R27-A4/A5/A7; `round27/scan_hyp_nightdry.json`; `WATCHLIST.md` NEXT 24 H l.102.
- "Is a dummy gate PASS?" -> `CONTEXT.md` l.3956-3978, l.4021-4028; `FACTS.md` F-RUN-41/42; R27-A3 (RULE v2.1, not yet logged).
- "Which pair do we propose for the finals?" -> `CONTEXT.md` l.3417-3430, l.3834-3862, l.3965-3973, l.4041-4050; `DECISIONS.md` §2 [c27] l.842-844; `round27/finals_card_v4_ru.md`; R27-A8.
- "Did a public notebook beat us (E10 v3, trigger >= 0.959)?" -> `experiments/discussions/feed_loop.log` + digests; `experiments/e10_watch/watch_loop.log`; `DECISIONS.md` §2f l.1128.
- "Is the laptop / poller alive?" -> `experiments/lb_poll/poll.log` newest `===` header; `CONTEXT.md` l.4035-4040; `FACTS.md` F-RUN-43/44.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~16:40Z 28 Sep, check the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, and the newest `research/wf_ideas_v4/round*/`.
