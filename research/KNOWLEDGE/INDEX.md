# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 26: state as of 2026-09-28 ~14:10 UTC (17:10 MSK). Git HEAD 5e5fd1b ('Risk stack gates: exp89q and exp89r PASS') = origin/main. Untracked: `research/wf_ideas_v4/round26/` (no REPORT.md), `research/KNOWLEDGE/_curation/26/`, `experiments/discussions/digest_20260928T1338Z.md` (`git status`). Previous curation: 25 (~11:10Z, 74caff9). Times are UTC unless marked MSK (= UTC+3); every line cites its source.
Deadline: 29 Sep 23:59. Finals are ticked MANUALLY by the user by 20:00 UTC = 23:00 MSK on 29 Sep; the session never ticks (`CONTEXT.md` l.3842-3855). `CONTEXT.md` gained 15 entries at l.3717-3923 (last 13:14Z); `## 9. Literature` is now at l.3924. Anchors:
- Rules: PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147; LADDER + L9 l.2407-2424; R8 COVERAGE 00:00 l.3311-3315; FINALS CARD 04:31 l.3417-3430.
- Since c25: **A2 + P50/P51 read rule** 11:17 l.3717; **W4 AMEND 4** 11:17 l.3753; **exp88c gate + exp86c waiver** l.3794; **exp75 line** l.3810; **exp88c PASS, exp89a/e, ledger, uptest** 11:19 l.3824; **Q3 = YES** 11:26 l.3834; **fallback tick allowed / blocked** 11:27-11:28 l.3842-3855; **P50 read 0.958** 12:16 l.3856; **P51 submitted** l.3863; **R+ night list** 12:17 l.3871; **RISK STACK** 12:23 l.3885; **user confirmed night + standing override** 12:25 l.3899; **exp89p PASS** 12:40 l.3908; **exp89q/r PASS** 13:14 l.3915.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 exp58 (56563521) = 0.954 + #38 exp58n (56563534) = 0.953, both below V_pub; only the user's own tick changes them (`CONTEXT.md` l.3851-3855; `FACTS.md` F-RUL-22; `DECISIONS.md` §2 [c26] l.809).
2. **Team best: P50 exp85a (exp70g + ILP_DIVISION_WEIGHT 0.4 + READMIT 0.94 = 'K', non-CI, 56629533) = 0.958, R+, UP 21 teams, rank 134 of 3,969 = V_pub.** E10 trigger now >= 0.959 (`CONTEXT.md` l.3856-3862; `FACTS.md` F-LB-25).
3. **PENDING:** P51 exp87a (K + CI, 56640366, sent 12:14:57Z) at the 14:04:10Z header; read expected ~21:30-22:15Z (`experiments/lb_poll/poll.log` l.23139-23142; `CONTEXT.md` l.3863-3870).
4. **Budget:** 28 Sep: 5/5 slots used. GPU unmeasured since 04:55Z; estimates 2.2-3.6 h (~2.5-3 h in CONTEXT) (`CONTEXT.md` l.3921-3923; `FACTS.md` C-206; `WATCHLIST.md` W269).
5. **Night 29 Sep (user-confirmed 12:25, all dummies PASS):** 00:05Z exp89r (K + SEC + DIS 2.25 + CI) if P51 reads '+'/'0u', else exp89q (K + SEC + DIS 2.25); 00:06Z exp75 (#37 + CI, v1); 00:46Z exp89p (K + SEC). P51 not terminal by 23:30Z -> exp89q (`CONTEXT.md` l.3899-3923; `DECISIONS.md` §1 P52-P54 l.191-193).
6. **Q3 = YES:** a SEC file may be a final only in the V_pub slot. Standing override: a public notebook >= 0.959 or a new disclosed knob is built + dummied at once and a swap proposed (after 02:00Z an E10 copy needs the user's yes) (`CONTEXT.md` l.3834-3841, l.3904-3907; `DECISIONS.md` §2h l.1261).
7. **Unlogged (round 26, R26-A1..A7):** R8 coverage for exp89p/q/r; MORNING TABLE v1.1 + depth-cap supersede; exp89s build + ledger 't'; freeze-line codes; exp75 PARTNER RULE v2 + card v4; user message; KEY FACTS (`research/wf_ideas_v4/round26/report.json`; `DECISIONS.md` §2h l.1263-1269).
8. **Morning 29 Sep:** no valid pre-score rule; the 12:17 clause (exp89h / RA90 / TAU) conflicts with the user's 'not public fitting' condition (`CONTEXT.md` l.3880-3891; `FACTS.md` C-212).
9. **Next decision points:** now: user reply + R26-A1 + exp89s; 15:17Z round 27; 17:57Z tick check; ~21:30Z v1.1 logged, P51 read; 23:30Z freeze; 00:04Z night batch; 07:23Z morning prep; 29 Sep 12:03Z card v4; 18:37Z FINAL proposal; 20:00Z user tick (`WATCHLIST.md` NEXT 24 H l.66, LATER l.88).
10. **Ideas ledger:** 496 ideas (lb-tested 61, lab-tested 26, in-plan 120, refuted 240, deferred 47, open 2); strict orphan I-233; 15 at risk (`IDEAS.md` CHANGES (26) l.169-179, ORPHANS l.799).

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` = this page. `CHANGES.md` = per-curation deltas (v4, 2-26). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,26}/`.
- `IDEAS.md` + `ideas.json` (I-001..I-496): CHANGES (26) l.169, ranking l.181, FINALS l.200, LADDER l.274, BASE l.360, RUN l.401, LOC l.458, DIV l.494, MODEL l.564, NODES l.616, INFER l.652, EF l.674, LINK l.694, VALID l.730, TESTSET l.781, ORPHANS l.799; per-ID log `ideas.json` meta.curations[n=26].
- `FACTS.md`: §1 metric l.180, §2 data l.197, §3 LB l.218 (F-LB-25/26 l.246-247), §4 runtime l.249 (F-RUN-41 l.293), §5 rules l.295 (F-RUL-22 l.320), §6 models l.322 (F-MOD-47/48 l.372-373), §7 lab-to-LB l.375 (F-TRN-58 l.436), CONTRADICTIONS l.438 (C-210..C-218 l.651-659).
- `DECISIONS.md`: probes §1 l.132 (P50-P54 l.189-193; [c26] builds l.472); gates §1b l.488; finals §2 l.553 ([c26] l.809, snapshot l.811); E10 §2f l.952 ([c26] l.1093); ladder/cards §2h l.1126 ([c26] rows l.1256-1269); R1-R10 §3 l.1271.
- `WATCHLIST.md` (curated ~14:05Z): OVERDUE l.50 (W262-W269), NEXT 24 H l.66 (T148, T157-T159), LATER l.88, INSIGHTS l.113 (I303-I308 l.117-122).

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows to P46 only); `experiments/lb_poll/poll.log`, `ledger.md`, `_lb/S1_1214Z`, `dataset_baseline/`; `experiments/e10_watch/watch_loop.log`; `experiments/discussions/feed_loop.log` + `digest_*.md`.
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `exp58n_x138_safe_lowref/` (#38); best `exp85a_k2cap6_div04_ra094/`; P51 `exp87a_k2cap6_div04_ra094_ci/`; night `exp89r_k2cap6_k_sec_dis225_ci/`, `exp89q_k2cap6_k_sec_dis225/`, `exp75_k2_coordinject/`, `exp89p_k2cap6_k_sec/`; base `exp70g_k2_cap6/`; prior best `exp79a_k2cap6_coordinject/`. Not built: exp89s/l/t/u (round-26 scratch only).
- Tools: `tools/build_probe_kernel.py`, `tools/coordinject_patch.py`, `tools/runtime_ledger.py` (l.82 regex lacks 't'), `tools/dummy_gates.py`, `tools/uptest.py`, `tools/e10_port_gate.py`, `tools/kaggle_feed.py` (default 0.958); `experiments/lb_poll/e10_watch_loop.py` (docstring l.28 stale).
- Rounds: `research/wf_ideas_v4/round26/report.json` (R26-A1..A7, 13:50Z), `report.notes.md`, 5 `scan_*.json`, 13 `v_*.json`; `round25/`, `knobarms_28sep/`, older `round24/`..`round8/`. Background: `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v3/FINAL_REPORT.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md` ORPHANS l.799 ff.)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-488 | User message (Russian, MSK first): researchers active; Q-M1 exp89t (default NO), Q-M2 exp89u (default NO), depth-cap reading | Send NOW; log answers | `IDEAS.md` ORPHANS; `round26/report.json` R26-A6 |
| I-480 | R8 COVERAGE line naming exp89p/q/r; supersede 'Q3 open' | Log NOW, before the 00:04Z check | ORPHANS; R26-A1 |
| I-481 / I-483 | MORNING TABLE v1.1 + depth-cap supersede for {K, SEC n2a, DIS 2.25, CI} only | Log before P51 reads (~21:30Z) | ORPHANS; R26-A2 |
| I-484 | exp89s = exp85a + DIS 2.25 (sha8 8ed72e32), usable in both morning branches | GPU read + dataset check, build, gate, dummy | ORPHANS; R26-A3 (1) |
| I-485 | exp89l = K + SEC + CI (cad1d47f), branch A M1 | Build at P51's read, branch A only | ORPHANS; R26-A3 (3) |
| I-489 / I-490 / I-491 | Freeze-line read codes, UP masking relaxation, night hygiene | In the 23:30Z freeze line | ORPHANS; R26-A4 (a)-(c) |
| I-494 / I-495 | EXP75 PARTNER RULE v2; finals card v4 | Rule before 00:06Z; card before 07:23Z, send 12:03Z 29 Sep | ORPHANS; R26-A5 |
| I-492 | Finals pool + PENDING branch + notify-only 19:30Z job | In the freeze line / card v4 | ORPHANS; R26-A4 (d) |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/26/{ideas,facts,watch}.json`)

1. [now] **Answer 'ресерчеры активны?' (R26-A6):** yes; LB poller last header 14:04:10Z, E10 watch RUN 25 13:22Z (0 signals), feed 13:38Z (nothing new), round 26 done 13:50Z, next rounds 15:17 / 17:47 / 20:17Z (18:17 / 20:47 / 23:17 MSK). Also ask Q-M1, Q-M2 and the depth-cap reading. Sources: `experiments/lb_poll/poll.log` l.23139; `experiments/e10_watch/watch_loop.log`; `experiments/discussions/feed_loop.log`; `round26/report.json` R26-A6; `WATCHLIST.md` W267.
2. [now] **R8 COVERAGE gap:** the 00:00 line names none of exp89p/q/r and says 'Q3 open'; the 00:04Z pre-submit check would fail for all three night files. Log R26-A1. Sources: `CONTEXT.md` l.3311-3315, l.3834; `FACTS.md` C-213; `WATCHLIST.md` W262.
3. [now] **exp89s not built, GPU unmeasured, ledger regex:** read Settings quota (else budget 2.2 h) and the dataset baseline, build exp89s (STOP unless 8ed72e32), log the gate before the output; add 't' + test to `tools/runtime_ledger.py` l.82 (exp89t would be filed safetail 9.5 h). Sources: R26-A3; `FACTS.md` F-MOD-45 [c26], C-206; `WATCHLIST.md` W264, W269.
4. [today] **Depth cap vs exp89r + void morning rule:** 'cap + 2 levers' (l.3753-3757, l.3841, l.3884) contradicts the confirmed 4-lever exp89r (l.3899-3907); the 12:17 MORNING clause breaks 'not public fitting' (l.3880-3891). Log the supersede + MORNING TABLE v1.1 pre-score by ~21:30Z. Sources: `FACTS.md` C-211, C-212; R26-A2; `WATCHLIST.md` W263.
5. [today] **P51 read decides the 00:05Z file:** '+'/'0u' -> exp89r (+ exp89l build in branch A), else exp89q; not terminal by 23:30Z -> exp89q. In branch A, DIS reads only as a double difference (|dd| >= 0.002) and the MASKED rule would lose an exp89r '0u' to exp75's overlap. Log R26-A4 (a)-(e) in the 23:30Z freeze line. Sources: `CONTEXT.md` l.3785-3786, l.3899-3904; `FACTS.md` C-214; `WATCHLIST.md` T148, W265, I303.
6. [today] **exp75 PARTNER RULE v2** (>= 0.955 -> B model-favoured; 0.954 near-equal trade; verifiers disagreed on 0.954) must be logged before the 00:06Z submit, or A2 (5) kept explicitly. Sources: `CONTEXT.md` l.3744-3748; R26-A5 (1); `FACTS.md` C-216; `WATCHLIST.md` W266.
7. [today] **Records and cron:** `experiments/RESULTS.md` lacks rows 47-50 (0.955 / 0.957 / 0.955 / 0.958); refresh KEY FACTS before round 27 (task text still said best 0.957); add the missing 17:57Z tick check, 19:30Z notify job and 23:00-23:45Z final LB snapshot. Sources: `FACTS.md` C-118, C-218; R26-A7; `WATCHLIST.md` W126, W268, W270.
8. [before-finals] **Finals card v4** before 07:23Z, sent 12:03Z 29 Sep; FINAL proposal 18:37Z; each text says the user's tick by 20:00 UTC is the only path; every night/morning file is a single-embryo public read chosen after P50; add the host's no-embryo-overlap note (743006). Sources: R26-A5; `FACTS.md` F-RUL-22, C-215; `WATCHLIST.md` W266, I308.
9. [info] Orphan I-233 (close in one line); DIS 2.25 dummies run +15-20% slower, so flag exp89l/t gates above 2,000 s; UP code '0' is unresolved, never 'lower'; dummy-clip GT lab (I-496) only in scratch; round26/ untracked, REPORT.md missing for rounds 24-26. Sources: `IDEAS.md` ORPHANS; `WATCHLIST.md` I304, I306, W246/W257.

**RESOLVED since curation 25:** R25-A1/A2 pre-score lines, exp88c gate + exp86c waiver and the exp75 line logged 11:17 (`CONTEXT.md` l.3717-3823); exp88c PASS, exp89 ledger rule, `tools/uptest.py` 11:19 (l.3824); Q3 answered YES and the tick fallback answered (then blocked) (l.3834-3855); P50 read + P51 submitted (l.3856-3870); night files built and gated (l.3908-3923); E10 trigger >= 0.959 (l.3862). Moot: exp86c night slot, exp88a/b/c, exp89a/e, card v3 (`IDEAS.md` CHANGES (26)).
**Settled curator disagreements:** the depth cap [today] (ideas, watch) vs [before-finals] (facts) -> [today], since exp89l may be built at P51's read. The R26-A1 coverage line [today]/[now] -> [now].

## HOW TO USE

- "Score of probe N, and what changed?" -> `DECISIONS.md` §1; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/ledger.md` / `poll.log` (P47 onward); `experiments/<exp>/probe.json`.
- "P51 scored; which file goes at 00:05Z?" -> `CONTEXT.md` l.3863-3870, l.3899-3907; `round26/report.json` R26-A4 (proposed codes); `DECISIONS.md` §1 l.190-193.
- "What goes out tonight / tomorrow morning?" -> `CONTEXT.md` l.3871-3923; `round26/report.json` R26-A2, R26-A3; `IDEAS.md` I-481, I-484, I-485; `WATCHLIST.md` NEXT 24 H l.66.
- "Which pair do we propose for the finals?" -> `CONTEXT.md` l.3417-3430, l.3834-3862; `DECISIONS.md` §2 [c26] l.809-811; R26-A5; `IDEAS.md` I-494, I-495, I-492.
- "Did a public notebook beat us (E10 v3, trigger >= 0.959)?" -> `experiments/discussions/feed_loop.log` + digests; `experiments/e10_watch/watch_loop.log`; `DECISIONS.md` §2f l.1093.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~14:10Z 28 Sep, check the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, and the newest `research/wf_ideas_v4/round*/`.
