# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 24: state as of 2026-09-28 ~07:45 UTC. Git HEAD is 19c24b5 ('W1 read: probe 47 exp78b = 0.955 (no UP); cap-12 direction closed') = origin/main (`git log -1`). Untracked: `research/wf_ideas_v4/round24/` (no REPORT.md), `research/KNOWLEDGE/_curation/24/`, `experiments/e10_watch/20260928T0639Z.txt` and `20260928T0722Z.txt`, `experiments/discussions/digest_20260928T0704Z.md` and `0735Z.md`, new `experiments/ext_*` folders (incl. `ext_corwin-biocel-aux/_booster/`) and `experiments/ds_secw_corwin_v1/weights/` (`git status`). The previous curation was 23 (~04:50Z, 08ceca1). All times are UTC, and every line cites its source.
Deadline: 29 Sep 23:59. The user ticks the finals MANUALLY on 29 Sep; our buffer is 20:00 (`CONTEXT.md` l.3211-3213). `CONTEXT.md` gained 7 entries at l.3448-3538; `## 9. Literature` is now at l.3539. Anchors:
- Rules: PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147; LADDER + L9 l.2407-2424; READ TABLE v3 + W1/W2 v3 l.3222-3285; CI-RAN GATE l.3316-3337; W2 TABLE v4 + S1-S6 l.3347-3365; W4 AMEND 2 l.3366-3377; RESUME POINT 01:48 l.3398; FINALS CARD + E10 v3 NOW + S7 + SEC gate 04:31 l.3417-3430; W2 AMENDMENT 04:38 l.3433-3441; PROCESS FIX 04:39 l.3442-3447.
- Since c23: **curation 23 acted on + exp85a pre-submit line** 04:53 l.3448; **P50 submitted + GPU quota read** 05:03 l.3465; **exp85b/c gates + ops restart** 06:26 l.3479; **kaggle_feed tool** 06:35 l.3495; **exp86a/b/c built** 06:37 l.3515; **exp86a/b/c gates PASS** 07:28 l.3522; **P47 read = 0.955 '-'** 07:32 l.3530-3538.

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 K2 exp58 (56563521) = 0.954 and #38 twin exp58n (56563534) = 0.953. The user picks on 29 Sep; the card recommends {V_pub, #37} (`CONTEXT.md` l.3417-3422, l.3474; `DECISIONS.md` §2 [c24] l.730-732).
2. **Team best: P45 exp70g (K2 + cap 6, 56606948) = 0.956 = V_pub**; P46 exp70q = 0.956; **P47 exp78b (cap 12 + FRAME_CAP 2) = 0.955, code '-', no UP** (`CONTEXT.md` l.3530-3538; `experiments/lb_poll/ledger.md` 07:32:50Z).
3. **LB:** #181 of 3,966 at 07:29Z, 10th of 60 in the 0.956 block, 171 teams strictly above (`CONTEXT.md` l.3530-3538; `experiments/lb_poll/_lb/S0_0729Z`). No public notebook scores above 0.953; feed E10 FLAG none at 07:35:25Z; E10 loop RUN 19 07:24Z, 0 signals (`FACTS.md` F-LB-21 l.240; `experiments/discussions/feed_loop.log`; `experiments/e10_watch/watch_loop.log`).
4. **Base** = exp70g. S5: cap > 8 is closed (no exp80a/exp84a; exp86b, exp82b/c, exp83a/d/f/g dead). P49 '+' -> BASE exp78a (S2, stop at cap 8), else BASE stays exp70g (`CONTEXT.md` l.3535-3538).
5. **PENDING at 07:32:48Z:** P48 exp79a CI (56623105), P49 exp78a cap 8 (56624341), **P50 exp85a = exp70g + ILP_DIVISION_WEIGHT 0.4 + READMIT_MIN_SCORE 0.94** (56629533, sent 05:02:30Z) (`experiments/lb_poll/poll.log` l.20760; `CONTEXT.md` l.3465-3474). Expected: 49 ~08:15-08:40Z, 48 ~09:40-10:55Z, 50 ~12:27-12:51Z (`research/wf_ideas_v4/round24/report.json` new_facts).
6. **Budget:** 28 Sep 4 slots used, **1 left (W2b)**. GPU 20:29/30 h used at 04:55Z; ~7.2 h left after the dummies (`CONTEXT.md` l.3474-3478; `round24/report.json` new_facts).
7. **Built/gated:** exp85a/b/c PASS (l.3466-3469, l.3485-3488); exp86a/b/c PASS 07:28 on the old gate85 criteria (l.3522-3529). exp86c has 84 forks vs R24-A4 '>= 85'. No `experiments/exp87*` yet. Poller, E10 loop and feed loop run detached (l.3480-3485, l.3495-3514; `FACTS.md` F-MOD-43 l.355, C-200 l.621).
8. **Round 24 (R24-A1..A11, `research/wf_ideas_v4/round24/report.json` 07:18Z) is not in CONTEXT.** A1-A3 missed the 'before 47 terminal' deadline; Row 1 of TABLE v5 is moot after P47 '-' (`FACTS.md` C-191 l.612).
9. **Next decision points:** now: pre-score blocks + the one user message (R24-A7, by 08:00Z); T1 ~08:45Z; 49 read; 48 read (CI-RAN gate); **W2b** = CI file at 12:00Z or non-CI file at 50's terminal header (latest 14:00Z), else W3 by 23:30Z; 23:30Z W4 freeze; 29 Sep: W4 00:05-01:45Z, no CI after 02:00Z, finals proposal 12:00Z, FINALS READ ~19:00Z, ticks by 20:00Z (`round24/report.json` R24-A1 (T), R24-A2; `WATCHLIST.md` NEXT 24 H l.65, LATER l.97).
10. **Ideas ledger:** 448 ideas (lb-tested 55, lab-tested 24, in-plan 108, refuted 212, deferred 47, open 2). The P47 read is not yet reflected in `IDEAS.md` (curated at 07:31Z). Strict orphan: I-233 (`IDEAS.md` CHANGES (24) l.135-144, ORPHANS l.716).

## WHERE THINGS ARE

The knowledge base `research/KNOWLEDGE/` is written only by `experiments/workflows/biohub-curator.js`:
- `INDEX.md` is this page. `CHANGES.md` holds the per-curation deltas (v4, 2-24). Curator logs are in `research/KNOWLEDGE/_curation/{v4,2,...,24}/`.
- `IDEAS.md` + `ideas.json`: I-001..I-448. Section lines: CHANGES (24) l.135, FINALS l.165, LADDER l.227, BASE l.291, RUN l.331, LOC l.383, DIV l.418, MODEL l.488, NODES l.540, INFER l.576, EF l.598, LINK l.618, VALID l.649, TESTSET l.698, ORPHANS l.716. The per-ID log is `ideas.json` meta.curations[n=24].
- `FACTS.md`: §1 metric l.178, §2 data l.195, §3 LB l.216 (F-LB-20/21 l.239-240), §4 runtime l.242 (F-RUN-38 l.283), §5 rules l.285 (F-RUL-19 l.307), §6 models l.309 (F-MOD-43 l.355), §7 lab-to-LB l.357 (F-TRN-56 l.416), CONTRADICTIONS l.418 (C-190..C-200 l.611-621).
- `DECISIONS.md`: probes §1 l.130 (P47-P50 l.184-187; [c24] builds l.427-429); gates §1b l.446; finals §2 l.511 ([c24] l.730, snapshot l.732); E10 §2f l.872 ([c24] l.1009); ladder/cards §2h l.1042 ([c24] rows l.1134-1147); R1-R10 §3 l.1153 ([c24] rows l.1211-1218).
- `WATCHLIST.md` (curated 07:25Z, before the P47 read): OVERDUE l.48 (W235-W238 first), NEXT 24 H l.65, LATER l.97, INSIGHTS l.124 (I274-I286 l.128-140).

Key sources (repo root):
- `CONTEXT.md` (anchors above). LB: `experiments/RESULTS.md` (rows to P46); `experiments/lb_poll/poll.log`, `ledger.md`, `_lb/S0_0729Z`; `experiments/e10_watch/20260928T0722Z.txt` (newest snapshot), `watch_loop.log`.
- Kernels (each has `probe.json`): finals `experiments/exp58_x138_safe_lowref/` (#37), `exp58n_x138_safe_lowref/` (#38); best `experiments/exp70g_k2_cap6/`; W1 `exp78b_k2_cap12_fc2/`, `exp79a_k2cap6_coordinject/`, `exp78a_k2_cap8/`; knobs `exp85a_k2cap6_div04_ra094/` (P50), `exp85b_k2cap6_div04/`, `exp85c_k2cap6_ra094/`; branches `exp86a_k2cap8_div04_ra094/`, `exp86b_k2cap12fc2_div04_ra094/` (dead), `exp86c_k2cap6_div04_ra092/`; W3/W4 `exp81_k2cap6_secn2a/`, stacks `exp82a_k2cap8_secn2a/` ... `exp84a_k2_cap48_fc2/`.
- Tools: `tools/build_probe_kernel.py`, `tools/coordinject_patch.py`, `tools/runtime_ledger.py` (exp8\d -> safetail rule, I-383), `tools/dummy_gates.py`, `tools/e10_port_gate.py`, `tools/kaggle_feed.py` (discussions + notebook scores, digests in `experiments/discussions/`); `experiments/lb_poll/e10_watch_loop.py`; `research/wf_ideas_v4/e10v3/runbook.notes.md`.
- Rounds: `research/wf_ideas_v4/round24/report.json` (R24-A1..A11), `report.notes.md`, `scan_*.json`, 23 `v_*.json` (rechecks `v_recheck_r24-rc-*.json`); older rounds `round23/`..`round8/` (with REPORT.md). Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-436 | ROUND 24 PRE-SCORE 1/3: W2b timing (CI 12:00Z / non-CI at 50's header, latest 14:00Z) + K LEVER (ILP 0.4 + READMIT 0.94 = one lever, coded by P50) + TABLE v5 | Log now, marked '(written after 47 was terminal)'; Row 1 moot | `IDEAS.md` l.285 |
| I-437 | PRE-SCORE 2/3: W4 AMEND 3 + (4) EXCEPTION (READMIT 0.92/0.90 allowed) | Log before 50 is terminal; without it exp86c is banned | `IDEAS.md` l.286 |
| I-434 / I-445 | PRE-SCORE 3/3: GAP RULE, node-row hash gate `tools/gate_dummy.py`, runtime rule v2 (<= 2,100 s) | Log with the ILP/lowrefine corrections; gate85.py is scratchpad-only | `IDEAS.md` l.377-378 |
| I-435 | exp86a/b/c branch files | exp86b dead (P47 '-'); exp86c needs the R24-A4 check (forks 84) before Row 3 | `IDEAS.md` l.284 |
| I-438 / I-383 | exp87 K-lever CPU builds + ledger rule exp87[abce] -> safetail_ci | Build only exp87a/b/i (c/d/e/j dead after P47); add the rule + test | `IDEAS.md` l.287, l.369 |
| I-425 / I-300 / I-330 | One Russian user message: 02:00Z cap lift (<= 2 non-CI files to ~10:25Z), Q3, E10 after 02:00Z, K disclosure | Send with the 47 read, by 08:00Z; LIFT SPLIT line first | `IDEAS.md` l.221, l.233, l.529 |
| I-447 / I-433 | Dummy push schedule T1-T5 + detached loops / live session at 12:15/12:30/13:30Z | T1 ~08:45Z; wake-ups for W2b | `IDEAS.md` l.379, l.376 |
| I-426 / I-444 | 29 Sep finals proposal message; 'V_pub + one-lever parent' refuted | R23-A10 fixes + knob-file caveat before 29 Sep 12:00Z | `IDEAS.md` l.222, l.224 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/24/{ideas,facts,watch}.json`)

1. [now] **The R24-A1..A3 pre-score blocks are not in CONTEXT, and P47 went terminal at 07:32:48Z.** Log them as one block: quote the last PENDING header for 48/49/50, mark it '(written after 47 was terminal)', and drop Row 1. It must land before 49 (~08:15-08:40Z) and 50 (~12:27Z) are terminal. Sources: `round24/report.json` R24-A1..A3; `FACTS.md` C-191; `WATCHLIST.md` W235-W237.
2. [now] **The R24-A7 user message is due with the 47 read or by 08:00Z.** Log the LIFT SPLIT line first, then send ONE message (lift, Q3, E10 after 02:00Z, a K line, READMIT 0.92/0.90 as our own steps). Take no slot on a presumed yes. Sources: `round24/report.json` R24-A7; `IDEAS.md` I-425; `WATCHLIST.md` W241.
3. [today] **exp86c gate vs R24-A4.** It was logged PASS with 84 forks, but R24-A4 needs >= 85, a node-row hash differing from 30e1c6e46704, per-clip readmits and 0 failed frames. READMIT 0.92 stays banned by W4 AMEND 2 (4) until the R24-A2 exception is logged. Settle both before any Row-3 use by 12:30Z. Sources: `CONTEXT.md` l.3522-3529; `FACTS.md` C-198, C-200; `IDEAS.md` I-435.
4. [today] **Dead files and the exp87 builds after P47.** Remove the cap > 8 files (exp80a, exp84a, exp86b, exp82b/c, exp83a/d/f/g, exp87c/d/e/j) from every push list. Build only exp87a/b/i (CPU, stop on a sha8 mismatch) and add the ledger rule with its test before T1 ~08:45Z. Sources: `CONTEXT.md` l.3535-3538; `round24/report.json` R24-A5; `WATCHLIST.md` W239.
5. [today] **The W2b decision needs a live session.** Log which rule governs (R24-A1 (T) or 06:26 W2 v4 (2) at 12:00Z). The session timers died at 05:07Z (76-min poller gap). The feed loop hit a 429 at 06:34Z. Wake up at 12:15/12:30/13:30Z, check the loops, and pause the feed loop 10 min before the submit. Sources: `FACTS.md` C-191, F-RUN-37; `WATCHLIST.md` W242, W247; `experiments/lb_poll/ledger.md` gaps.
6. [today] **Corrections and one runtime rule.** 'ILP 0.4 near-inert' (06:26) is wrong: it adds +3 safe divisions. 'exp85a changes TWO things' (04:53) is benign. Three runtime criteria are in use (1,920 s / 1,900 s / rule v2), so pick one in the R24-A3 block. Sources: `round24/v_recheck_r24-rc-a-*.json`, `v_recheck_r24-rc-c-*.json`; `FACTS.md` C-192, C-193, C-195.
7. [today] **Before the 48 read and any E10 trigger.** Add the W230 balanced CI caveat and the W231 residue (exp84a gate, 7029fe69). Also add the R24-A9 SI rule: cap-family BASE DIVINS keys only, because the SI gate FAILs on a K base. Sources: `WATCHLIST.md` W230, W231, W243; `WATCHLIST.md` I274 l.128.
8. [before-finals] **Finals texts.** Apply the R23-A10 draft fixes (DIV caveat, pool with E10, conditional SEC, #38 rationale) plus a public-only knob-file caveat. Keep {V_pub, #37}; JT's partner advice is not our rule. Sources: `FACTS.md` C-184, C-197; `WATCHLIST.md` W234.
9. [before-finals] **exp87m (amanatar V6) pre-registration omits round 17's public V6 read of 0.901**, which is confounded. Cite it if exp87m is ever built. Sources: `round24/report.json` R24-A11; `round17/report.json` new_facts; `IDEAS.md` I-442.
10. [before-finals] **Records.** Missing CONTEXT lines: R22-A9, R23-A8, R24-A10 (a)-(f) incl. the synthetic author (José Freitas, not hengck23; C-194), and R20-A13. Render round24 REPORT.md and commit it with the snapshots (named paths only). Add RESULTS rows P47-P50. Orphan I-233 is [info]. Sources: `WATCHLIST.md` W202, W244, W246; `FACTS.md` C-118.

**RESOLVED since curation 23:** R23-A4 runbook SI; R23-A11 template key facts; R23-A5 quota read (20:29/30 h); R23-A7 stacks committed (d015291); RESULTS rows 39-46 (59e14e2); E10 loop text '>= 0.957'; SEC sibling CSVs sha-checked; the exp85a pre-submit line (`CONTEXT.md` l.3448-3494). The c23 alert 'READMIT/lowrefine coupling' is withdrawn as benign (R24-RC-A). exp86a/b/c gates are logged at l.3522, which supersedes the watch curator's 'exp86c has no output' (W238, I282). P47 was read and committed (19c24b5).
**Settled curator disagreements:** exp86c [now] (watch) vs [today] -> [today], since the PASS is logged and only the stricter gate is open. The user message [now]/[today] -> [now] (08:00Z). The pre-score blocks are [now] in all three curators.

## HOW TO USE

- "Score of probe N, and what changed?" -> `DECISIONS.md` §1; `experiments/RESULTS.md` (to P46); `experiments/lb_poll/poll.log` / `ledger.md` (P47 onward); `experiments/<exp>/probe.json`.
- "A W1/P50 file scored; which code applies?" -> `CONTEXT.md` l.3222-3285 (READ TABLE v3), l.3316-3337 (CI-RAN), l.3347-3365 (S1-S6), l.3425-3426 (S7); `round24/report.json` R24-A1 (K lever, TABLE v5), R24-A3 (GAP RULE).
- "What goes out at W2b / W3 / W4?" -> `CONTEXT.md` l.3438-3447, l.3491-3493, l.3535-3538; `round24/report.json` R24-A1, R24-A2, R24-A6; `DECISIONS.md` §2h [c24] l.1134-1147; `IDEAS.md` I-436, I-437.
- "Which pair do we propose for the finals?" -> `CONTEXT.md` l.3417-3422; `DECISIONS.md` §2 [c24] l.730-732; `IDEAS.md` I-426.
- "Did a public notebook beat us (E10 v3)?" -> `experiments/discussions/feed_loop.log` + digests; `experiments/e10_watch/watch_loop.log`; `DECISIONS.md` §2f [c24] l.1009.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~07:45Z 28 Sep, check the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, and the newest `research/wf_ideas_v4/round*/`.
