# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 23: state as of 2026-09-28 ~04:50 UTC. This is a re-run after the round-23 curator agents failed on the weekly limit (`CONTEXT.md` l.3429-3430); the user reset the limit at 04:32Z (l.3431-3432). Git HEAD is 08ceca1 ('Process fix: disclosed knobs are actionable') = origin/main (`git log -1`). Untracked: the nine stack folders `experiments/exp82a-c`, `exp83c-g`, `exp84a`, plus `research/KNOWLEDGE/_curation/23/`, `experiments/e10_watch/20260928T0443Z.txt`, `experiments/ext_succskip/`, `experiments/ext_corwin-biocel-aux/_booster/` and `experiments/ds_secw_corwin_v1/weights/`. The previous curation was 22 (~01:48Z, acbea01). All times are UTC, and every line cites its source.
Deadline: 29 Sep 23:59. The user ticks the finals MANUALLY and picks them on 29 Sep; our buffer is 20:00 (`CONTEXT.md` l.3211-3213). `CONTEXT.md` gained 10 entries at l.3378-3447; `## 9. Literature` is now at l.3448. Anchors:
- Rules: PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147; LADDER + L9 l.2407-2424; user letters (E10 v3, aggressive mode) l.2917-2951; READ TABLE v3 + W1/W2 v3 l.3222-3285; CI-RAN GATE and ERROR rules l.3316-3337; W2 TABLE v4 + S1-S6 l.3347-3365; W4 AMEND 2 l.3366-3377.
- Since c22: **CI-STACK DUMMY GATE** 01:48 l.3378 and its PASS 01:50 l.3411; **PRE-SCORE CLARIFICATIONS** 01:48 l.3387; **RESUME POINT** 01:48 l.3398 (the newest; read it first); **P45 correction** l.3409; **E10 signal checked** 02:46 l.3414; **FINALS CARD + E10 v3 NOW + S7 + SEC-STACK GATE** 04:31 l.3417-3430; **user limit reset** 04:32 l.3431; **discussion 743929 knobs, exp85a/b/c built + W2 AMENDMENT** 04:38 l.3433-3441; **PROCESS FIX** (disclosed knobs are ACTIONABLE; exp85a goes at dummy PASS) 04:39 l.3442-3447.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 K2 exp58 (56563521) = 0.954 and #38 twin exp58n (56563534) = 0.953. The user picks on 29 Sep. The logged card recommends {V_pub, #37} over the ticked pair (`CONTEXT.md` l.3418-3422; `DECISIONS.md` §2 [c23] l.690-700).
2. **Team best: P45 exp70g (K2 + insertion cap 6, 56606948) = 0.956 = V_pub.** P46 exp70q = 0.956, code 0 (`experiments/lb_poll/poll.log` l.20089-20100; `DECISIONS.md` §2 [c23] snapshot l.692).
3. **LB:** #173 at 04:43Z (164 = 1 + teams strictly better), 10th of 58 in the 0.956 block, SubmissionCount 48 (`experiments/e10_watch/20260928T0443Z.txt` l.313, l.1035). John Taylor is #105 at 0.959 (`CONTEXT.md` l.3433). Info only: the private LB (~71%) decides.
4. **Base** = K2 (x138 + safetail + lowrefine + gated DaughterNet insertion) at cap 6 (exp70g). S7: if 47 and 49 are both '+' and disp(exp78a) > disp(exp78b), BASE becomes exp78a (`CONTEXT.md` l.3425-3426; `FACTS.md` C-182).
5. **W1 still PENDING at 04:36:39Z:** P47 exp78b cap 12 + fc2 (56623073), P48 exp79a cap 6 + coordinject (56623105, the first CI file), P49 exp78a cap 8 (56624341) (`experiments/lb_poll/poll.log` l.20089-20096; `FACTS.md` F-LB-17 l.235).
6. **Running now:** exp85a (exp70g + ILP_DIVISION_WEIGHT 0.4 + READMIT_MIN_SCORE 0.94, sha e6337843) and exp85b (ILP 0.4 only) dummies, pushed 04:37Z. The E10 v3 loop did RUN 17 at 04:43:55Z with 0 signals. The LB poller runs every ~10 min (`CONTEXT.md` l.3436-3438; `experiments/e10_watch/watch_loop.log`; `experiments/exp85a_k2cap6_div04_ra094/probe.json`).
7. **Built:** exp80a and exp81 (W3/W4 since the 04:38 amendment); exp83a and exp83b (dummy PASS at 01:50); exp85a/b/c (committed in d14e9a3); the nine stacks exp82a-c, exp83c-g and exp84a: shas match, but no dummies, no CONTEXT line, and untracked. Sources: `CONTEXT.md` l.3411, l.3437-3441; `FACTS.md` F-MOD-42 l.349; `DECISIONS.md` §1 [c23] l.409-424.
8. **Mode:** aggressive mode. Research rounds resume, with round 24 at 07:00Z and then every ~2.5 h. Disclosed x138-family knobs are now ACTIONABLE (`CONTEXT.md` l.3431-3432, l.3442-3447; `FACTS.md` F-RUN-37 l.279).
9. **Next decision points (28 Sep):** ~05:15Z: submit exp85a at its dummy PASS (W2a moved earlier); ~06:58Z: P47 can reach a final status; 07:00Z: round 24; ~07:40-08:45Z: P49; the morning brief by 09:30Z at the latest; ~09:40-10:40Z: P48; 12:00Z W2b: an E10 copy first, else exp85b or exp85c (governed by the '04:5x amendment', which is NOT yet logged); W3 by 23:30Z; last W4 dummy push ~21:00Z. On 29 Sep: W4 00:05-01:45Z; no CI file after 02:00Z; FINALS READ ~19:00Z; ticks by 20:00Z. Sources: `CONTEXT.md` l.3438-3447; `WATCHLIST.md` NEXT 24 H l.63, LATER l.91.
10. **Ideas ledger:** 431 ideas (lb-tested 55, lab-tested 24, in-plan 95, refuted 209, deferred 46, open 2). The only strict orphan is I-233 (`IDEAS.md` CHANGES (23) l.128-137, ORPHANS l.692).

## WHERE THINGS ARE

The knowledge base `research/KNOWLEDGE/` is written only by `experiments/workflows/biohub-curator.js`:
- `INDEX.md` is this page. `CHANGES.md` holds the per-curation deltas (v4, 2-23).
- `IDEAS.md` + `ideas.json`: I-001..I-431 in 13 clusters. Section lines: FINALS l.158, LADDER l.219, BASE l.278, RUN l.316, LOC l.363, DIV l.397, MODEL l.466, NODES l.517, INFER l.552, EF l.574, LINK l.594, VALID l.625, TESTSET l.674, ORPHANS l.692. The per-ID log is `ideas.json` meta.curations[n=23].
- `FACTS.md`: §1 metric l.177, §2 data l.194, §3 LB l.215 (F-LB-19 l.237), §4 runtime l.239 (F-RUN-37 l.279), §5 rules l.281, §6 models l.304 (F-MOD-42 l.349), §7 lab-to-LB l.351 (F-TRN-55 l.409), CONTRADICTIONS l.411 (C-182..C-189 l.596-603). **Gap:** exp85a/b/c and the 04:38/04:39 entries are not in FACTS.md, DECISIONS.md or WATCHLIST.md yet (`grep -c exp85` = 0); only `IDEAS.md` I-431 covers them.
- `DECISIONS.md`: probes §1 l.129 (P47-P49 l.183-185; [c23] builds l.409-424); gates §1b l.425; finals §2 l.490 ([c23] card l.690, snapshot l.692); E10 §2f l.832 ([c23] l.967); ladder/cards §2h l.1000 ([c23] rows l.1076-1091); R1-R10 §3 l.1093 ([c23] R23 rows l.1144-1150).
- `WATCHLIST.md`: OVERDUE l.48 (W228 first), NEXT 24 H l.63, LATER l.91, INSIGHTS l.121 (I262-I273). Curator logs are in `research/KNOWLEDGE/_curation/{v4,2,...,23}/`.

Key sources (repo root):
- `CONTEXT.md` (anchors above).
- LB records: `experiments/RESULTS.md` (rows up to P38 only); `experiments/lb_poll/poll.log` and `ledger.md` (P39 onward); `experiments/e10_watch/20260928T0443Z.txt` (the newest snapshot) and `watch_loop.log`.
- Kernels (each has a `probe.json`): finals: `experiments/exp58_x138_safe_lowref/` (#37) and `experiments/exp58n_x138_safe_lowref/` (#38); best: `experiments/exp70g_k2_cap6/`; W1: `experiments/exp78b_k2_cap12_fc2/`, `exp79a_k2cap6_coordinject/`, `exp78a_k2_cap8/`; JT knobs: `experiments/exp85a_k2cap6_div04_ra094/`, `exp85b_k2cap6_div04/`, `exp85c_k2cap6_ra094/`; W3/W4: `experiments/exp81_k2cap6_secn2a/`, `exp80a_k2_cap24_fc2/`; stacks: `experiments/exp82a_k2cap8_secn2a/` ... `exp84a_k2_cap48_fc2/`, and `exp83a_k2cap12fc2_ci/`, `exp83b_k2cap8_ci/`.
- Tools: `tools/build_probe_kernel.py`, `tools/coordinject_patch.py`, `tools/runtime_ledger.py`, `tools/dummy_gates.py`, `tools/e10_port_gate.py`; `experiments/lb_poll/e10_watch_loop.py` (still says '>= 0.955' at l.28 and l.78); `research/wf_ideas_v4/e10v3/runbook.notes.md` (the SI recipe in §9 is stale at l.206-213).
- Rounds: `research/wf_ideas_v4/round23/report.json` + `REPORT.md` (R23-A1..A12), `scan_plancheck.json`, `scan_hyp_finals_29sep.json` (R23F-3 draft_ru), `scan_hyp_stack_builds.json`, `scan_recheck.json`, `scan_browser.json`, `v_*.json`; older rounds in `round22/`..`round8/`.
- Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-431 / I-412 | exp85a/b/c: John Taylor's two disclosed knobs on exp70g (both / ILP 0.4 / READMIT 0.94) | exp85a is the W2a submit at dummy PASS (~05:15Z); the exp85b/exp85c split is the one-knob read at 12:00Z | `IDEAS.md` l.275, l.313 |
| I-364 / I-287 | E10 v3 NOW (trigger: strictly above our best, now >= 0.957) + SI = BASE's probe.json keys, REF = BASE | The runbook §9 still says cap 4 / REF exp58; fix it before any trigger (R23-A4) | `IDEAS.md` l.312, l.304 |
| I-428 / I-416 | SEC-STACK DUMMY GATE + the nine built stacks | Log the builds and commit them; download the exp81/exp80a sibling CSVs; push only the BASE's member after the 47/49 reads | `IDEAS.md` l.359, l.272 |
| I-414 / I-399 / I-396 | W2 v4 + S1-S7 + the 04:38 W2 AMENDMENT: exp80a/exp81 move to W3/W4 | Log the '04:5x amendment' for 12:00Z/W3/W4 | `IDEAS.md` l.270, l.265, l.513 |
| I-425 | 28 Sep morning brief (Russian) | Send at the first header with 47 AND 49 terminal, <= 09:30Z; Q1 answer needed by ~23:00Z | `IDEAS.md` l.214 |
| I-426 / I-406 | 29 Sep finals proposal message + the logged card | Apply the R23-A10 fixes to the draft before the 29 Sep 12:00Z send | `IDEAS.md` l.215, l.213 |
| I-405 | GPU quota read + dummy priority (5 h / 3 h thresholds) | 4th deferral; read it before the next dummy push | `IDEAS.md` l.355 |
| I-259 | Refresh the stale workflow task template | Before round 24 (07:00Z) | `IDEAS.md` l.651 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/23/{ideas,facts,watch}.json`)

1. [now] **exp85a READMIT 0.94 also lowers lowrefine's threshold on K2.** The file therefore changes two things, not one: `_LOWREFINE_MIN_SCORE` reads `BIOHUB_READMIT_MIN_SCORE`. Round 23 refuted the knob for exactly this reason. ILP 0.4 may do ~nothing, because the x138 relink replaces every ILP edge (R23-RC-B). Before submitting, record the lowrefine refined-count and the node growth vs exp70g from the dummy log (lab band ~+0.60%; flag > +1.5%). State the coupling and the winner's-curse risk in the pre-submit line. Sources: `experiments/exp85c_k2cap6_ra094/exp85c-k2cap6-ra094.ipynb`; `research/wf_ideas_v4/round23/v_recheck_r23-rc-a-readmit-min-score-094-lab-blind.json`; `CONTEXT.md` l.3433-3447.
2. [now] **E10 SI runbook defect (R23-A4).** Runbook §9 builds cap 4 with REF exp58 (`research/wf_ideas_v4/e10v3/runbook.notes.md` l.206-213), but the logged rule is SI = BASE keys, REF = BASE (`CONTEXT.md` l.3423-3425). An SI built from the runbook ships cap 4 or FAILs its own gate. Fix it before the Burhan 0.969 burst (~07-09Z). Sources: `FACTS.md` C-183; `WATCHLIST.md` W232.
3. [now] **Stale workflow task template (R23-A11)** (best 0.954, finals by row 3, E10 >= 0.956, R8 new OK). Refresh it before round 24 at 07:00Z; this curation's own task text repeats the stale facts. Sources: `experiments/workflows/biohub-research-round.js`; `FACTS.md` C-189; `WATCHLIST.md` W228.
4. [today] **Stacks and SEC gate.** The nine stacks are unlogged and uncommitted (R23-A7); The exp81/exp80a dummy CSVs (sha12 8132ef2811d0 / a109ad024ace) are not in _dl; The gate lacks the R23-A3 (a)(5)/(b)/(c)/(d) clauses; Push nothing before the 47/49 reads, then push only the BASE's member (R23-A6). Commit the named paths as the user with no trailer. Sources: `FACTS.md` F-MOD-42, C-170; `WATCHLIST.md` W229, W231, W233.
5. [today] **GPU quota unread, 4th deferral.** The last reading was 07:55/30 h on 26 Sep (`CONTEXT.md` l.2542). The exp85a/b dummies went out at 04:37Z without a reading. The round-23 estimate is inconsistent ('2.5-5 h left' vs 3.5-9.4 h). Read https://www.kaggle.com/settings before the next push. Sources: `FACTS.md` F-RUL-05, C-172; `WATCHLIST.md` W212.
6. [today] **W1 reads.** P47 from ~06:58Z, P49 ~07:40-08:45Z, P48 ~09:40-10:40Z. Use one waiter per ref. S0 = `experiments/e10_watch/20260928T0400Z.txt` (count 48, k = 9); take a manual S1 within 10 min. Apply the CI-RAN gate to 48. The read procedure R23-A12 is PROPOSED only. Sources: `FACTS.md` F-LB-17, F-RUN-36; `WATCHLIST.md` NEXT 24 H.
7. [today] **Plan churn and the morning brief.** W2 changed three times in 4 h (04:31, 04:38, 04:39), and the '04:5x amendment' for 12:00Z/W3/W4 is not in CONTEXT. The brief template still shows exp80a vs exp81 in W2a. Send the brief (R23-A9) when 47 AND 49 are terminal, <= 09:30Z: Q2 threshold 0.957, no absence-insurance line, one line saying exp85a is already submitted. Sources: `CONTEXT.md` l.3438-3447; `IDEAS.md` I-425; `FACTS.md` C-165, C-173.
8. [before-finals] **Finals texts.** The 04:31 card is condensed: no balanced CI caveat (Eric -0.002 vs P31 +0.002). The R23F-3 Russian draft still has the R23-A10 defects: no DIV caveat, the cap-parent line, a narrowed pool, unconditional SEC wording, the wrong #38 rationale and the exp70b wording. Fix it before 29 Sep 12:00Z. Sources: `research/wf_ideas_v4/round23/scan_hyp_finals_29sep.json`; `FACTS.md` C-184, C-188; `WATCHLIST.md` W230, W234.
9. [before-finals] **Missing CONTEXT lines:** R22-A9 info line; R23-A8 curator text (READMIT coupling, ILP reason); R20-A13 private-read addendum (before the first private score); LESSONS H1; the R21-A12 DC-blind lesson. Sources: `research/wf_ideas_v4/round23/report.json` R23-A8; `IDEAS.md` I-407, I-430; `WATCHLIST.md` W202.
10. [info] **Records.** `experiments/RESULTS.md` still ends at P38; add P39-P49 before the FINALS READ; The E10 loop text still says '>= 0.955' (`experiments/lb_poll/e10_watch_loop.py` l.28/l.78); change it only at the next planned edit; FACTS/DECISIONS/WATCHLIST do not cover exp85 yet (next curation). Sources: `FACTS.md` C-118; `WATCHLIST.md` W126.

**RESOLVED since curation 22:**
- R22-A1 CI-STACK DUMMY GATE logged before the outputs were read (`CONTEXT.md` l.3378); PASS at l.3411.
- R22-A2 RESUME POINT + P45 correction + MEMORY (l.3398, l.3409).
- R22-A3 PRE-SCORE CLARIFICATIONS (l.3387).
- R22-A4 finals card + E10 NOW line, logged pre-score (l.3417-3425; condensed, see alert 8).
- R22-A6 nine stacks rebuilt with matching shas (`FACTS.md` F-MOD-42).
- Round 23 committed with REPORT.md (db8ba02).
- The limit outage ended with the 04:32 reset.
- `FACTS.md` C-26, C-159, C-164, C-170 (partial), C-175..C-178 and C-181 are resolved.

**Settled curator disagreements:**
- The task template [today]/[now] -> [now] (07:00Z).
- The stack log/commit [now]/[today] -> [today] (nothing is pushed before the reads).
- The finals draft [before-finals] in all three.
- The RESULTS rows stay [info], due before the FINALS READ.

## HOW TO USE

- "Score of probe N, and what changed?" -> `DECISIONS.md` §1; `experiments/RESULTS.md` (up to P38); `experiments/lb_poll/poll.log` / `ledger.md` (P39 onward); `experiments/<exp>/probe.json`.
- "A W1 file has scored; which code applies?" -> `CONTEXT.md` l.3222-3285 (READ TABLE v3), l.3316-3337 (CI-RAN GATE), l.3387-3397 (CI-? SCOPE), l.3425-3426 (S7); `report.json` R23-A12.
- "What goes out at 12:00Z / W3 / W4?" -> `CONTEXT.md` l.3347-3377 (W2 v4, W4 AMEND 2), l.3438-3447 (04:38 amendment, 04:39 fix); `IDEAS.md` I-431, I-414; `DECISIONS.md` §1 [c23] l.409.
- "Which pair do we propose for the finals?" -> `CONTEXT.md` l.3418-3422; `DECISIONS.md` §2 [c23] l.690; `IDEAS.md` I-426.
- "Did a public notebook beat us (E10 v3)?" -> `CONTEXT.md` l.3423-3425 (trigger > our best, now >= 0.957); `DECISIONS.md` §2f l.967; `experiments/e10_watch/watch_loop.log`.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~04:50Z 28 Sep, check the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, and the newest `research/wf_ideas_v4/round*/`.
