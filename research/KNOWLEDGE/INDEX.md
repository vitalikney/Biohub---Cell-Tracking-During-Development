# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 21: state as of 2026-09-27 ~23:56 UTC. Git HEAD 4ac7126 ('Probe 46 exp70q = 0.956, no UP') = origin/main (`git log -1`). Untracked: `research/wf_ideas_v4/round21/`, `experiments/ext_succskip/`, `research/KNOWLEDGE/_curation/21/`, `experiments/e10_watch/20260927T2143Z..2343Z.txt`, `experiments/ds_secw_corwin_v1/weights/`. The previous curation was 20 (~21:00 UTC, 771a608). All times are UTC, and every line cites its source.
Deadline: 29 Sep 23:59. The user ticks the finals MANUALLY and picks them on 29 Sep; our buffer is 20:00 (`CONTEXT.md` l.3211-3213). `CONTEXT.md` gained 5 entries since curation 20, at l.3222-3310; `## 9. Literature` is now at l.3311. Anchors:
- Rules: PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147; LADDER + L9 l.2407-2424; RULE RECONCILIATION l.2502-2529; user letters (E10 v3, class-C (b), FREEZE lifted, aggressive mode) l.2917-2951; finals on 29 Sep l.3211; autonomous night l.3217.
- Since c20: **READ TABLE v3 codes + W1/W2 v3** 21:05 l.3222-3285 (logged pre-46); **N2 pre-registration** 21:06 l.3286-3295; ledger + build 21:06 l.3296-3300; N2 done + gates 21:26 l.3301-3306; **PROBE 46 READ** 22:27 l.3307-3310.
- Not yet logged: all of round 21 (R21-A1..A13; `research/wf_ideas_v4/round21/report.json`). The newest RESUME POINT is still l.2599 (26 Sep 22:46).

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 K2 exp58 (56563521) = 0.954 and #38 twin exp58n (56563534) = 0.953. The user picks on 29 Sep; the rule path is {exp70g, #37} (`CONTEXT.md` l.3211-3213; `DECISIONS.md` §2 [c21] snapshot l.620; `FACTS.md` C-160).
2. **Team best: P45 exp70g (K2 + insertion cap 6, 56606948) = 0.956**, still our unrounded best (~0.95634, sub-display). **P46 exp70q (cap 6 + thr 0.3 + forkmid) = 0.956, code 0** (0 TeamIds passed); L (7.64, 7.81] h (`CONTEXT.md` l.3307-3310; `FACTS.md` F-LB-16 l.232; `research/wf_ideas_v4/round21/scan_hyp_w2_w4_plan.json` r21w-9).
3. **LB:** rank #167 of 3,960 at 23:43Z (158 = 1 + teams strictly better), 10th of 56 in the 0.956 block, SubmissionCount 48. Info only; the private LB (~71%) decides (`experiments/e10_watch/20260927T2343Z.txt` l.307, l.1004).
4. **Base** = K2 (x138 + safetail + lowrefine + gated DaughterNet insertion) on cap 6 (exp70g). V_pub = exp70g; exp70q is not V_pub (tie, larger dose) (`DECISIONS.md` §2 [c21] l.618-620; `FACTS.md` F-MOD-39).
5. **Ready dummies (PASS):** exp78b cap 12 + fc2 (d54d810c), exp79a cap 6 + coordinject (5f9b265d; first CI file ever), exp78a cap 8 (8d8d9c28); exp81 (exp70g + N2 student n2a, 7029fe69) and exp80a (cap 24 + fc2) are COMPLETE, PASS not logged. exp77 N2 finished 21:24Z (proxy 0.998/1.010) (`CONTEXT.md` l.3296-3306; `DECISIONS.md` §1 [c21] table l.375).
6. **No 28 Sep submit yet** (`experiments/lb_poll/poll.log` header 23:55:50Z, l.18381). W1 = ~00:05Z exp78b (P47), ~00:06Z exp79a (P48, after the R8 COVERAGE line; fallback <= 03:00Z), 00:50Z exp78a (P49) (`CONTEXT.md` l.3250-3257; `research/wf_ideas_v4/round21/report.json` R21-A1, R21-A2).
7. **User mode:** asleep since 20:30Z; the session runs autonomously. Aggressive mode and E10 v3 stay in force (`CONTEXT.md` l.3217-3221, l.2917-2951).
8. **Watchers:** E10 v3 loop 12 runs, 0 signals (RUN 12 23:43:55Z; next 00:43:42Z); LB poller every ~10 min (`experiments/e10_watch/watch_loop.log`; `experiments/lb_poll/poll.log`).
9. **Next decision points:** 00:05-00:50Z W1 submits; ~00:55Z exp83a/exp83b CI-stack dummies (after the exp83 ledger rule); before ~07:30Z W2 TABLE v4 + S1-S6, W4 AMEND 2, finals card; ~07:30-11:00Z W1 reads; 08:00-09:30Z morning message (2 yes/no); 08:45-10:00Z W2a; 12:00Z W2b; <= 23:30Z W3. 29 Sep: W4 00:05-01:45Z; proposals 12:00Z/18:00Z; FINALS READ ~19:00Z; ticks by 20:00Z (`WATCHLIST.md` NEXT 24 H l.78, LATER l.109).
10. **Ideas ledger:** 419 ideas (lb-tested 55, lab-tested 24, in-plan 88, refuted 206, deferred 44, open 2); strict orphan I-233 (`IDEAS.md` CHANGES (21) l.109-117, ORPHANS l.660).

## WHERE THINGS ARE

The knowledge base `research/KNOWLEDGE/` is written only by `experiments/workflows/biohub-curator.js`:
- `INDEX.md` is this page. `CHANGES.md` holds the per-curation deltas (v4, 2-21).
- `IDEAS.md` + `ideas.json`: I-001..I-419 in 13 clusters. FINALS l.138, LADDER l.196, BASE l.253, RUN l.291, LOC l.335, DIV l.369, MODEL l.435, NODES l.486, INFER l.520, EF l.542, LINK l.562, VALID l.593, TESTSET l.642, ORPHANS l.660. Per-ID log: `ideas.json` meta.curations[n=21].
- `FACTS.md`: §1 metric l.175, §2 data l.192, §3 LB l.213 (F-LB-16 l.232), §4 runtime l.234 (F-RUN-35 l.272), §5 rules l.274, §6 models l.297 (F-MOD-40 l.340), §7 lab-to-LB l.342 (F-TRN-53 l.398), CONTRADICTIONS l.400 (C-167..C-174 l.570-577).
- `DECISIONS.md`: probes §1 l.127 (P45/P46 l.179-180; [c21] table l.375); gates §1b l.390; finals §2 l.455 ([c21] snapshot l.620); E10 §2f l.759 ([c21] l.890); ladder/cards §2h l.923 ([c21] rows l.982-989); R1-R10 §3 l.991.
- `WATCHLIST.md`: OVERDUE l.63 (W216 first), NEXT 24 H l.78, LATER l.109, INSIGHTS l.136 (I231-I248). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,21}/`.

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows up to P38 only); `experiments/lb_poll/poll.log`, `ledger.md` (P39 on); `experiments/e10_watch/20260927T2343Z.txt` (newest snapshot), `watch_loop.log`.
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `experiments/exp58n_x138_safe_lowref/` (#38); best `experiments/exp70g_k2_cap6/`; W1 `experiments/exp78b_k2_cap12_fc2/`, `experiments/exp79a_k2cap6_coordinject/`, `experiments/exp78a_k2_cap8/`; W2 `experiments/exp81_k2cap6_secn2a/`, `experiments/exp80a_k2_cap24_fc2/`; trainer `experiments/exp77_secft_n2/` (NEVER_SUBMIT). exp82*/exp83*/exp84a exist only in the session scratchpad (`research/wf_ideas_v4/round21/scan_hyp_w2_w4_plan.json` r21w-1).
- Tools: `tools/build_probe_kernel.py`, `tools/coordinject_patch.py`, `tools/runtime_ledger.py` (safetail_ci l.59, exp79a l.79; no exp83 rule yet), `tools/e10_port_gate.py`, `experiments/lb_poll/e10_watch_loop.py`.
- Rounds: `research/wf_ideas_v4/round21/report.json` (R21-A1..A13; no REPORT.md yet), `scan_plancheck.json`, `scan_hyp_w2_w4_plan.json`, `scan_hyp_risk_check.json`, `scan_recheck.json`, `scan_browser.json`, `v_*.json`; older `round20/`..`round8/`. Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v4/round9/LESSONS_draft.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-324 / I-401 | R8 COVERAGE line for coordinject, then exp79a = exp70g + CI (first CI on the LB) | Log the line before the ~00:06Z submit; hard fallback 03:00Z | `IDEAS.md` l.363, l.366 |
| I-398 / I-397 | exp78b (cap 12 + fc2) P47 ~00:05Z; exp78a (cap 8) P49 00:50Z | Submit `-v 1` from the PASSED dummy, no re-push; descriptions start 'probe 47/49: ...' | `IDEAS.md` l.241, l.240 |
| I-383 / I-404 / I-416 | exp83* -> safetail_ci ledger rule; exp83a/exp83b CI stacks; BASE-lookup stack builds | Rule + test before the ~00:55Z dummies; rebuild from the r21w-1 env block, log sha | `IDEAS.md` l.329, l.245, l.249 |
| I-413 | CI-RAN GATE: dL = L_hi(exp79a) - L_hi(exp78b); <= 0.5 h no-op, >= 1.2 h ran | Log before exp79a's terminal header (~09:40Z) | `IDEAS.md` l.331 |
| I-414 / I-399 / I-396 / I-400 | W2 TABLE v4 + DIV STOP RULES S1-S6: W2a exp80a iff S3 else exp81; W2b; exp84a (cap 48) only under S3 | Log before exp78b's terminal header (~07:30Z) | `IDEAS.md` l.247, l.242, l.482, l.243 |
| I-415 | W4 AMEND 2: <= 4 planned files + 1 held for E10; E10 copy after 02:00Z 29 Sep needs a user yes | Log with I-414; ask in the morning message | `IDEAS.md` l.248 |
| I-406 / I-393 / I-407 | 29 Sep finals card lines (V_pub + INFO lines, partner always #37); private-read addendum | Log before ~07:30Z; addendum before 29 Sep 23:59Z | `IDEAS.md` l.193, l.192, l.638 |
| I-257 / I-418 | RESUME POINT + MEMORY + P45 correction; ERROR / dataset-freeze rules + NO-GO list | Write ~00:10-01:30Z, around the W1 submits | `IDEAS.md` l.169, l.332 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/21/{ideas,facts,watch}.json`)

1. [now] **R8 COVERAGE line before exp79a (~00:06Z).** Coordinject was built after the 27 Sep 12:00 R8 cutoff and the user never named it; `grep 'R8 COVERAGE' CONTEXT.md` = none at 23:37Z. If late: submit exp78b/exp78a on time, exp79a after the line, <= 03:00Z. Sources: `research/wf_ideas_v4/round21/report.json` R21-A1; `DECISIONS.md` §2h l.983; `WATCHLIST.md` W216.
2. [now] **W1 submits** 00:05Z exp78b, ~00:06Z exp79a, 00:50Z exp78a: status COMPLETE and live code == local, `-v 1`, never re-push; one waiter per ref; run the ledger and check exp79a prints safetail_ci. Sources: `report.json` R21-A2; `CONTEXT.md` l.3250-3257; `WATCHLIST.md` W203.
3. [now] **exp83 ledger rule before the ~00:55Z exp83a/exp83b dummies.** `tools/runtime_ledger.py` maps exp83* to safetail (9.5 h) via the exp8\d rule, so a normal CI latency (~9.7-10.5 h) would read NO/'v'. Add `exp83[a-z]*` -> safetail_ci above it, with a test; until then pass `--family`. Sources: `report.json` R21-A5, R21-A6; `FACTS.md` C-171; `WATCHLIST.md` W218, W219.
4. [now] **RESUME POINT + P45 correction + MEMORY (R21-A4), 6th deferral.** Last block `CONTEXT.md` l.2599; correction: 127 passed, exp70g class C; MEMORY still says 'E10 port rule proposed'. Write ~00:10-01:30Z. Sources: `FACTS.md` C-26, C-159; `WATCHLIST.md` W185.
5. [today] **One CONTEXT write for R21-A3:** exp81/exp80a dummy PASS lines (W2a needs one); CI-RAN GATE (a fail-soft CI leaves exp70g's CSV byte-identical -> false '0'; before ~09:40Z); 46 S0 addendum (stale S0, k not logged; use the newest download per count); ERROR / dataset-freeze rules; NO-GO list. Sources: `report.json` R21-A3; `FACTS.md` F-RUN-35, C-167; `WATCHLIST.md` W217.
6. [today] **Pre-register before exp78b's terminal header (~07:30Z):** W2 TABLE v4 + S1-S6 (v3 W2b names the already-scored exp79a when BASE = exp70g), W4 AMEND 2 (W4 cannot hold 5 K2-like files at >= 40 min), finals card R21-A9 (partner #37, never the own cap parent). Quote the last PENDING poll header. Sources: `report.json` R21-A7, R21-A8, R21-A9; `FACTS.md` C-168; `WATCHLIST.md` W220, W221, W214.
7. [today] **E10 texts stale + E10 after 02:00Z:** trigger is >= 0.957, not >= 0.955 (`experiments/lb_poll/e10_watch_loop.py` l.28, l.78); SI must use BASE's DIVINS settings, not cap 4; the loop runs to 29 Sep 12:00Z with no rule after 02:00Z. Add the second yes/no question to the 08:00-09:30Z morning message. Sources: `report.json` R21-A9 (v), R21-A10; `FACTS.md` C-163, C-173; `WATCHLIST.md` W222.
8. [today] **GPU quota unread since 26 Sep** (07:55/30 h; estimate ~19.5-21 h); read before the ~08:40Z stack dummies. The scratch-only builds (exp82*/exp83*/exp84a) are lost on a crash: rebuild from r21w-1 and log sha. Sources: `report.json` R21-A11, R21-A6; `FACTS.md` C-172; `WATCHLIST.md` W212.
9. [before-finals] **Records:** write `research/wf_ideas_v4/round21/REPORT.md` from report_md_ru and commit round 21 by named paths as the user, no Co-Authored-By trailer (R21-A13); `experiments/RESULTS.md` still ends at P38 (add P39-P46); round-20 leftovers R20-A10/A13, LESSONS H1. Sources: `FACTS.md` C-118; `WATCHLIST.md` W223, W126.
10. [info] **Reading caveats:** K2 latency drift (L_hi 7.54 -> 7.81 h) can give a cap-rung 'v' with no code cause; a 0.957 on exp70g needs only ~+1.6e-4; the finals MC says the partner choice dominates (#37 vs own cap parent -0.17..-0.34 bronze); the exp60 replay is DC-blind for pre-DC gate relaxations (I-419). Sources: `report.json` R21-A12; `research/wf_ideas_v4/round21/scan_hyp_w2_w4_plan.json` r21w-9; `WATCHLIST.md` I239-I241.

**RESOLVED since curation 20:** R20-A2 READ TABLE v3 + W1/W2 v3 logged 21:05 while 46 was PENDING (commit 9d0820c; `CONTEXT.md` l.3222); R20-A6 N2 pre-registration logged 21:06 before exp77 finished 21:24Z (l.3286); R20-A4 safetail_ci ledger family landed (l.3296; `tools/runtime_ledger.py` l.59); exp79a pushed and PASSED (l.3304); P46 read 22:27 (l.3307); round 20 committed with REPORT.md (9d0820c); the 'CI queues 2-3.3 h' premise refuted (`FACTS.md` C-169).
**Settled curator disagreements:** exp83 ledger rule [now]/[today] -> [now] (dummies ~00:55Z); finals card [today]/[before-finals] -> [today] (must precede ~07:30Z); RESULTS rows [info]/[before-finals] -> [before-finals].

## HOW TO USE

- "Score of probe N, what changed?" -> `DECISIONS.md` §1; `experiments/RESULTS.md` (up to P38); `experiments/lb_poll/poll.log` / `ledger.md` (P39 on); `experiments/<exp>/probe.json`.
- "W1 file scored, what code?" -> `CONTEXT.md` l.3222-3285 (READ TABLE v3); CI-RAN GATE `research/wf_ideas_v4/round21/report.json` R21-A3 (b); `FACTS.md` F-RUN-35.
- "What goes out in W2/W3/W4?" -> `report.json` R21-A7, R21-A8 (until logged in CONTEXT); `DECISIONS.md` §1 [c21] table l.375; `IDEAS.md` I-414, I-415.
- "Which pair do we propose for the finals?" -> `DECISIONS.md` §2 [c21] l.618-620; `report.json` R21-A9; `FACTS.md` C-160, F-TRN-52.
- "Did a public notebook beat us (E10 v3)?" -> `CONTEXT.md` l.2917-2926 (trigger now >= 0.957); `DECISIONS.md` §2f l.890; `experiments/e10_watch/watch_loop.log`.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~23:56Z 27 Sep, check the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, and the newest `research/wf_ideas_v4/round*/`.
