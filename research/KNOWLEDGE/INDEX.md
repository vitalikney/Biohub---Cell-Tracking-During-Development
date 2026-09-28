# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 22: state as of 2026-09-28 ~01:48 UTC. Git HEAD acbea01 ('Fix W2 table v4 entry formatting') = origin/main (`git log -1`). Untracked: `research/wf_ideas_v4/round22/`, `research/KNOWLEDGE/_curation/22/`, `experiments/ext_succskip/`, `experiments/ext_corwin-biocel-aux/_booster/`, `experiments/ds_secw_corwin_v1/weights/`, `experiments/e10_watch/20260928T0043Z..0143Z.txt`. The previous curation was 21 (~23:56 UTC 27 Sep, 4ac7126). All times are UTC, and every line cites its source.
Deadline: 29 Sep 23:59. The user ticks the finals MANUALLY and picks them on 29 Sep; our buffer is 20:00 (`CONTEXT.md` l.3211-3213). `CONTEXT.md` gained 7 entries since curation 21, at l.3311-3377; `## 9. Literature` is now at l.3378. Anchors:
- Rules: PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147; LADDER + L9 l.2407-2424; RULE RECONCILIATION l.2502-2529; user letters (E10 v3, class-C (b), FREEZE lifted, aggressive mode) l.2917-2951; READ TABLE v3 + W1/W2 v3 l.3222-3285; finals on 29 Sep l.3211; autonomous night l.3217.
- Since c21: **R8 COVERAGE** 00:00 l.3311; **R21-A3 gates** (exp81/exp80a PASS, CI-RAN GATE, 46 addendum, ERROR rules, NO-GO) 00:00 l.3316-3337; **W1 submits** 00:06 l.3338, 00:50 l.3342; **exp83 ledger rule + exp83a/b built** 01:02 l.3344-3346; **W2 TABLE v4 + S1-S6** 01:02 l.3347-3365; **W4 AMEND 2** 01:02 l.3366-3377.
- Not yet logged: all of round 22 (R22-A1..A11; `research/wf_ideas_v4/round22/report.json`, `REPORT.md`). The newest RESUME POINT is still l.2599 (26 Sep 22:46).

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 K2 exp58 (56563521) = 0.954 and #38 twin exp58n (56563534) = 0.953. The user picks on 29 Sep; the rule path is {V_pub = exp70g, #37} (`CONTEXT.md` l.3211-3213; `DECISIONS.md` §2 [c22] snapshot l.656).
2. **Team best: P45 exp70g (K2 + insertion cap 6, 56606948) = 0.956** (~0.95634 unrounded); P46 exp70q = 0.956, code 0 (`DECISIONS.md` §1 l.180-181; `FACTS.md` F-LB-16 l.233).
3. **LB:** rank #169 at 01:43Z (160 = 1 + teams strictly better), 10th of 59 in the 0.956 block, SubmissionCount 48; info only, the private LB (~71%) decides (`experiments/e10_watch/20260928T0143Z.txt` l.309, l.1013).
4. **Base** = K2 (x138 + safetail + lowrefine + gated DaughterNet insertion) on cap 6 (exp70g) = V_pub (`DECISIONS.md` §2 [c22] l.656; `FACTS.md` F-MOD-39).
5. **W1 SUBMITTED, all PENDING at 01:36:09Z:** P47 exp78b cap 12 + fc2 (56623073, 00:06:09Z); P48 exp79a cap 6 + coordinject (56623105, 00:06:33Z; first CI file on the LB); P49 exp78a cap 8 (56624341, 00:50:37Z). 2 slots left on 28 Sep (`experiments/lb_poll/poll.log` l.18991-19000; `CONTEXT.md` l.3338-3342; `FACTS.md` F-LB-17 l.234).
6. **Running now:** exp83a (exp78b + CI) and exp83b (exp78a + CI) dummies pushed 01:01Z, RUNNING at 01:28:54Z, no pass gate logged; E10 v3 loop RUN 14 01:43:54Z, 0 signals; LB poller every ~10 min (`CONTEXT.md` l.3344-3346; `research/wf_ideas_v4/round22/report.notes.md`; `experiments/e10_watch/watch_loop.log`).
7. **Built:** exp80a, exp81, exp83a, exp83b only. The other 9 planned stacks (exp82a-c, exp83c-g, exp84a) exist only as round-21 scratch sha claims (`ls -d experiments/exp8*`; `FACTS.md` F-MOD-41 l.345; `DECISIONS.md` §1 [c22] table l.396).
8. **User mode:** asleep, session autonomous; aggressive mode and E10 v3 in force (`CONTEXT.md` l.3217-3221, l.2917-2951). Round 22 (R22-A1..A11) is PROPOSED, not logged (`research/wf_ideas_v4/round22/report.json`).
9. **Next decision points:** NOW R22-A1 gate before the exp83a/b outputs are read; <= 06:45Z R22-A2/A3/A4 (47 can be terminal from ~06:58Z); ~06:58-10:42Z W1 reads; <= 09:30Z morning brief; 08:45-10:00Z W2a; 11:45Z exp83a/b PASS; 12:00Z W2b; ~21:00Z last W4 dummy; <= 23:30Z W3. 29 Sep: W4 00:05-01:45Z; no CI after 02:00Z; FINALS READ ~19:00Z; ticks by 20:00Z (`WATCHLIST.md` NEXT 24 H l.80, LATER l.111; `FACTS.md` F-RUN-36 l.276).
10. **Ideas ledger:** 425 ideas (lb-tested 55, lab-tested 24, in-plan 91, refuted 207, deferred 46, open 2); strict orphan I-233 (`IDEAS.md` CHANGES (22) l.117-125, ORPHANS l.674).

## WHERE THINGS ARE

The knowledge base `research/KNOWLEDGE/` is written only by `experiments/workflows/biohub-curator.js`:
- `INDEX.md` is this page. `CHANGES.md` holds the per-curation deltas (v4, 2-22).
- `IDEAS.md` + `ideas.json`: I-001..I-425 in 13 clusters. FINALS l.146, LADDER l.205, BASE l.263, RUN l.301, LOC l.346, DIV l.380, MODEL l.449, NODES l.500, INFER l.534, EF l.556, LINK l.576, VALID l.607, TESTSET l.656, ORPHANS l.674. Per-ID log: `ideas.json` meta.curations[n=22].
- `FACTS.md`: §1 metric l.176, §2 data l.193, §3 LB l.214 (F-LB-17/18 l.234-235), §4 runtime l.237 (F-RUN-36 l.276), §5 rules l.278, §6 models l.301 (F-MOD-41 l.345), §7 lab-to-LB l.347 (F-TRN-54 l.404), CONTRADICTIONS l.406 (C-175..C-181 l.584-590).
- `DECISIONS.md`: probes §1 l.128 (P47-P49 l.182-184; [c22] table l.396); gates §1b l.408; finals §2 l.473 ([c22] snapshot l.656); E10 §2f l.796 ([c22] l.929); ladder/cards §2h l.962 ([c22] rows l.1029-1037); R1-R10 §3 l.1039.
- `WATCHLIST.md`: OVERDUE l.64 (W224 first), NEXT 24 H l.80, LATER l.111, INSIGHTS l.139 (I249-I261). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,22}/`.

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows up to P38 only); `experiments/lb_poll/poll.log`, `ledger.md` (P39 on); `experiments/e10_watch/20260928T0143Z.txt` (newest snapshot), `watch_loop.log`.
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `experiments/exp58n_x138_safe_lowref/` (#38); best `experiments/exp70g_k2_cap6/`; W1 `experiments/exp78b_k2_cap12_fc2/`, `experiments/exp79a_k2cap6_coordinject/`, `experiments/exp78a_k2_cap8/`; W2 `experiments/exp81_k2cap6_secn2a/`, `experiments/exp80a_k2_cap24_fc2/`; CI stacks `experiments/exp83a_k2cap12fc2_ci/`, `experiments/exp83b_k2cap8_ci/`; trainer `experiments/exp77_secft_n2/` (NEVER_SUBMIT).
- Tools: `tools/build_probe_kernel.py`, `tools/coordinject_patch.py`, `tools/runtime_ledger.py` (exp83* -> safetail_ci l.80), `tools/dummy_gates.py` (no CI mode), `tools/e10_port_gate.py`, `experiments/lb_poll/e10_watch_loop.py` (stale '>= 0.955' l.28, l.78).
- Rounds: `research/wf_ideas_v4/round22/report.json` + `REPORT.md` (R22-A1..A11), `scan_plancheck.json`, `scan_hyp_morning_brief.json`, `scan_hyp_extra_levers_29sep.json`, `scan_recheck.json`, `scan_browser.json`, `v_*.json`; older `round21/`..`round8/`. Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v4/round9/LESSONS_draft.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-420 / I-404 | CI-STACK DUMMY GATE: exp83a/b PASS iff clean log and the 7 columns equal the non-CI sibling, moved fraction 0.60-0.69, runtime <= 2,100 s | Log before reading the outputs; PASS by 11:45Z | `IDEAS.md` l.343, l.254 |
| I-421 / I-414 / I-415 | PRE-SCORE CLARIFICATIONS: CI-? SCOPE (no CI stack after NO-OP/'v'/ERROR); W2a -> exp81 if a DIV ref is not terminal at 10:00Z; 12:00Z consolidation superseded; no CI after 02:00Z | Log quoting a PENDING header; hard stop 06:45Z | `IDEAS.md` l.260, l.256, l.257 |
| I-257 | RESUME POINT + P45 correction (127 passed, exp70g class C) + MEMORY rewrite | 7th deferral; write now, <= 06:45Z | `IDEAS.md` l.177 |
| I-406 / I-393 / I-364 | 29 Sep FINALS CARD + balanced CI caveat + E10 NOW line (trigger >= 0.957, SI = BASE's DIVINS) | 2nd deferral; log before 06:45Z | `IDEAS.md` l.201, l.200, l.297 |
| I-425 | 28 Sep morning brief (Russian; Q1 lift 02:00Z cap default NO, Q2 E10 after 02:00Z) | Send at first header with 47 and 49 terminal, <= 09:30Z | `IDEAS.md` l.202 |
| I-416 / I-400 | Rebuild the 9 missing stacks (exp82a-c, exp83c-g, exp84a) on CPU, check shas, commit named folders | Tonight, no push; exp84a pre-submit line carries the weak cap-48 lab prior | `IDEAS.md` l.258, l.252 |
| I-405 | GPU quota read + dummy priority when short (5 h / 3 h thresholds) | 3rd deferral; before the next dummy push | `IDEAS.md` l.340 |
| I-259 | Refresh the stale workflow task template (E10 >= 0.956, finals by row 3, R8 hard line, 12:00Z consolidation) | Before round 23 (~03:30Z) | `IDEAS.md` l.633 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/22/{ideas,facts,watch}.json`)

1. [now] **R22-A1 CI-STACK DUMMY GATE** not in CONTEXT (`grep` = 0); exp83a/b dummies were RUNNING at 01:28:54Z, due ~01:30-01:40Z; `tools/dummy_gates.py` has no CI mode. Log first; if an output was already listed, add the '(written after the output was listed ...)' clause; then the pandas sibling compare. Sources: `research/wf_ideas_v4/round22/report.json` R22-A1; `FACTS.md` F-MOD-41, C-178; `WATCHLIST.md` W224.
2. [now] **R22-A2 RESUME POINT + P45 correction + MEMORY**, 7th deferral: last block `CONTEXT.md` l.2599; MEMORY still says 'E10 v1 in force'. Write between polls; hard stop 06:45Z. Sources: `report.json` R22-A2; `FACTS.md` C-26, C-159; `WATCHLIST.md` W185.
3. [now] **R22-A3 contradiction:** W2 TABLE v4 (2)(iv) and W4 AMEND 2 (1)-2 (l.3353-3354, l.3368) stack CI after any CI '?', but the CI-RAN GATE and R21-A3 (d) (l.3322-3332) forbid it after NO-OP/'v'/ERROR. Also: no W2a rule for an unread 47/49 at 10:00Z; R13-A1 (5) 12:00Z consolidation (l.2709-2710) not superseded; P49 record lacks ref. Log PRE-SCORE CLARIFICATIONS quoting a PENDING header, <= 06:45Z. Sources: `FACTS.md` C-175, C-176, C-181; `WATCHLIST.md` W225.
4. [now] **R22-A4 FINALS CARD** (2nd deferral) with the balanced CI caveat (Eric -0.002 vs P31 +0.002) and the E10 NOW line (>= 0.957, SI = BASE's DIVINS, no 0.955 floor); fix `experiments/lb_poll/e10_watch_loop.py` l.28/l.78 only at its next planned edit. <= 06:45Z. Sources: `report.json` R22-A4; `FACTS.md` C-163, C-164, C-180; `WATCHLIST.md` W214.
5. [now] **Stale workflow task template** (R22-A10): would make round-23 agents raise false violations; update before ~03:30Z. Sources: `report.json` R22-A10; `research/wf_ideas_v4/round22/scan_plancheck.json` PC22-11; `WATCHLIST.md` W228.
6. [today] **W1 reads from ~06:58Z** (safetail floor 6.69 h, not ~07:30Z): one waiter per ref (56623073, 56623105, 56624341); S0 = newest download at count 48 (0103Z qualifies, k = 9) + fresh S1; 48 via the CI-RAN GATE vs 47. Sources: `report.json` R22-A7; `FACTS.md` F-RUN-36, C-177; `WATCHLIST.md` W227, T129.
7. [today] **9 of 11 stack builds missing** (exp82a-c, exp83c-g, exp84a): rebuild on CPU with MSYS_NO_PATHCONV=1, check sha prefixes, commit named paths (R22-A6, R22-A11); W4 dummies must PASS by 00:00Z 29 Sep. Sources: `FACTS.md` F-MOD-41, C-170; `WATCHLIST.md` W226, W229.
8. [today] **GPU quota unread** (3rd deferral; last 07:55/30 h on 26 Sep, `CONTEXT.md` l.2542): ~20.6-22 h used at 1x, ~25-26.5 h if T4x2 bills 2x. Read https://www.kaggle.com/settings before the next dummy push; apply 5 h / 3 h thresholds. Sources: `report.json` R22-A5; `FACTS.md` F-RUL-05, C-172; `WATCHLIST.md` W212.
9. [today] **Morning brief** (R22-A8) at the first header with 47 AND 49 terminal, <= 09:30Z, never wait for 48; Q1 (lift 02:00Z cap, default NO) must be answered by ~23:00Z to change W4; log 'MORNING BRIEF SENT'. Sources: `report.json` R22-A8; `IDEAS.md` I-425; `FACTS.md` C-165, C-173; `WATCHLIST.md` W222.
10. [info] **Records and orphans:** `experiments/RESULTS.md` still ends at P38 (add P39-P49 before the 29 Sep FINALS READ); round-22 closures (I-410 ALPHA, I-422, I-423, I-082 MITO3 NaN probmat, I-424 theft-aware ranker, John Taylor knobs) are only in research files -> R22-A9 info line; exp84a pre-submit must quote 'cap48fc2 vs cap24fc2 = 0 TP / +4 FP, weak prior'. Sources: `FACTS.md` C-118, C-179, F-TRN-54; `research/wf_ideas_v4/round22/scan_recheck.json`; `WATCHLIST.md` W126, I252-I255.

**RESOLVED since curation 21:** R21-A1 R8 COVERAGE logged before the CI submit (`CONTEXT.md` l.3311; git d36a4b2); R21-A2 W1 submitted on time (l.3338, l.3342); R21-A3 gates logged (l.3316); R21-A5/A6 exp83 ledger rule + exp83a/b built and dummies pushed (l.3344; `tools/runtime_ledger.py` l.80); R21-A7/A8 W2 TABLE v4 + S1-S6 and W4 AMEND 2 logged pre-score (l.3347, l.3366); round 21 committed with REPORT.md (d36a4b2). `FACTS.md` C-167, C-168, C-171 resolved.
**Settled curator disagreements:** R22-A3 [now]/[today] -> [now] (hard stop 06:45Z); R22-A4 [now]/[today] -> [now]; task template [today]/[now] -> [now] (round 23 ~03:30Z); RESULTS rows [info]/[before-finals] -> [info] here, deadline before the FINALS READ.

## HOW TO USE

- "Score of probe N, what changed?" -> `DECISIONS.md` §1; `experiments/RESULTS.md` (up to P38); `experiments/lb_poll/poll.log` / `ledger.md` (P39 on); `experiments/<exp>/probe.json`.
- "W1 file scored, what code?" -> `CONTEXT.md` l.3222-3285 (READ TABLE v3), l.3316-3337 (CI-RAN GATE, ERROR rules); `report.json` R22-A7 (read procedure); `FACTS.md` F-RUN-35, F-RUN-36.
- "What goes out in W2/W3/W4?" -> `CONTEXT.md` l.3347-3377 (W2 TABLE v4, W4 AMEND 2) + R22-A3 clarifications (until logged); `DECISIONS.md` §1 [c22] table l.396; `IDEAS.md` I-414, I-415, I-421.
- "Which pair do we propose for the finals?" -> `DECISIONS.md` §2 [c22] l.656; `report.json` R22-A4; `FACTS.md` C-160, C-164.
- "Did a public notebook beat us (E10 v3)?" -> `CONTEXT.md` l.2917-2926 (trigger now >= 0.957); `DECISIONS.md` §2f l.929; `experiments/e10_watch/watch_loop.log`.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~01:48Z 28 Sep, check the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, and the newest `research/wf_ideas_v4/round*/`.
