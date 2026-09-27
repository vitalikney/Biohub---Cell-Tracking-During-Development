# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 19: state as of 2026-09-27 ~18:50 UTC. Git HEAD 22840c5 ('User yes: N2 stronger fine-tune') = origin/main (`git status -sb`). Untracked: `research/wf_ideas_v4/round19/`, `experiments/exp77_secft_n2/`, `research/KNOWLEDGE/_curation/19/`, `experiments/e10_watch/20260927T1731Z.txt`, `20260927T1743Z.txt`, `experiments/ds_secw_corwin_v1/weights/`. The previous curation was 18 (~16:05 UTC, b853642). Hashes older than 26 Sep 10:15 are pre-rewrite (`experiments/git_rewrite_map_2026-09-26.txt`). All times are UTC, and every line cites its source.
Deadline: 29 Sep 23:59. The user ticks finals MANUALLY; our buffer is 20:00 (`WATCHLIST.md` LATER l.104). `CONTEXT.md` gained five entries since curation 18, at l.3011-3074; `## 9. Literature` is now at l.3075. Anchors:
- Rules: PRE-REG v3 l.1576-1736 (R9 hidden-test 'N2' ban l.1673-1676); E10 PORT RULE l.2138-2147; LADDER + L9 l.2407-2424; RULE RECONCILIATION l.2502-2529; user letters (E10 v3, class-C (b), Q1/Q2, FREEZE lifted, aggressive mode) l.2917-2951.
- 27 Sep since c18: round-18 PRE-SCORE CARD 16:08 l.3011-3056; REBASE onto exp70b 16:08 l.3057-3062; exp76d DUMMY CLEAN 16:33 l.3063-3064; exp75 DUMMY COMPLETE 17:21 l.3065-3069; **USER YES TO N2 18:19:11 l.3070-3074**.
- Not yet logged: the R19-A1 amendment, READ TABLE v2 (R19-A2), the R19-A10 corrections, the exp72 gate values and ROUND 14-19 RECORDs. The newest RESUME POINT is still at l.2599 (26 Sep 22:46) (`research/wf_ideas_v4/round19/report.json` R19-A1, A2, A5, A10).

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 K2 exp58 (56563521) = **0.954** and #38 twin exp58n (56563534) = **0.953**. API SELECTED was last read at 07:41:28Z. Sources: `DECISIONS.md` §2 [c19] snapshot l.544; `CONTEXT.md` l.2995-3000.
2. **LB #289 of ~3,953** at 0.954 (18:43Z), 6th of 115 in the 0.954 block, SubmissionCount **46** (was #288 at 17:43Z). This is info only; the private LB (~71%) decides. Sources: `experiments/e10_watch/20260927T1843Z.txt` l.429, l.969; `FACTS.md` F-LB-02 l.216.
3. **Base** = K2 (x138 + safetail + lowrefine + gated DaughterNet insertion). Best public file: exp70b (P42, K2 + forkmid 4.5, 0.954); every 28 Sep file is rebased onto it (`CONTEXT.md` l.3057-3062; `FACTS.md` F-TRN-49 l.388).
4. **Running now:** P45 exp70g (K2 + cap 6, 56606948, 11:15:12Z; 8.0 h mark 19:15:12Z) and P46 exp70q (K2 + cap 6 + thr 0.3 + fm 4.5, 56611472, 14:36:59Z; 8.0 h mark 22:36:59Z) were both still PENDING at the 18:44:52Z header. Sources: `experiments/lb_poll/poll.log` l.16490-16496; `FACTS.md` F-RUN-31 l.265.
5. **Kernels:** exp76d (exp70b + secFT) dummy is clean: 121,061 nodes, 79 forks; exp75 (K2 + CI) dummy is clean after ~3.3 h in the Kaggle queue; exp76a (exp70b + CI, pushed 16:33Z) was still QUEUED at 18:19Z; exp76c/e/g are not built, and exp73m has no dummy. Sources: `CONTEXT.md` l.3063-3069; `FACTS.md` F-RUN-34 l.268, F-MOD-36 l.332; `DECISIONS.md` §1 [c19] table l.339.
6. **N2 approved by the user at 18:19:11Z:** exp77 is one T4x2 training session. n2a continues exp71 for epoch 2; n2b trains fresh from the pilkwang parent at lr 3e-5. Its outputs become exp70b + secswap rungs. It is built but NOT pushed, and no slot rule places those rungs yet. Sources: `CONTEXT.md` l.3070-3074; `experiments/exp77_secft_n2/`; `FACTS.md` F-MOD-37 l.333, C-150 l.544.
7. **28 Sep plan (round 19, not yet in CONTEXT):** W1 goes 00:05Z CI, 00:10Z SEC, 00:50Z DIV by READ TABLE v2 rows A-D (+ 46-PENDING), with per-mechanism fallbacks. W2 comes after the W1 reads or at 12:00Z. The W4 batch runs 29 Sep 00:05-01:45Z. Sources: `research/wf_ideas_v4/round19/report.json` R19-A1, R19-A2; `DECISIONS.md` §2h l.893-894.
8. **Watchers:** The E10 v3 hourly loop has done 7 runs with 0 signals (RUN 7 at 18:45:58Z); the LB poller runs every ~10 min; waiters are Bash PIDs: 45 = 34616, 00:05Z = 18920 (it echoes a stale 'exp72, exp75'), round 20, E10 = 10648. **There is no 46 waiter.** Sources: `experiments/e10_watch/watch_loop.log`; `WATCHLIST.md` I187 l.159, W207 l.61.
9. **Next decision points:** now: R19-A1 into CONTEXT (before 45 is terminal), RESUME POINT, 46 waiter, N2 amendment, exp76c push (by ~19:30Z); ~19:00-19:30Z: 45 read, then the R19-A7 user message; ~22:00-22:40Z: 46 read; 22:30-23:15Z: round 20; 23:30Z: tau answer due; 23:45Z: W1 dummies must PASS; 28 Sep 00:05Z: W1. Sources: `WATCHLIST.md` NEXT 24 H l.72.
10. **Ideas ledger:** 396 ideas (lb-tested 51, lab-tested 21, refuted 193, deferred 44, in-plan 83, open 4). The strict orphan is still I-233. Sources: `IDEAS.md` CHANGES (19) l.94-104, ORPHANS l.624.

## WHERE THINGS ARE

The knowledge base `research/KNOWLEDGE/` is written only by `experiments/workflows/biohub-curator.js`:
- `INDEX.md` is this page. `CHANGES.md` holds the per-curation deltas (v4, 2-19).
- `IDEAS.md` + `ideas.json`: I-001..I-396 in 13 clusters. Sections: FINALS l.125, LADDER l.182, BASE l.228, RUN l.265, LOC l.306, DIV l.339, MODEL l.402, NODES l.452, INFER l.486, EF l.508, LINK l.528, VALID l.559, TESTSET l.606, ORPHANS l.624. The per-ID log is in `ideas.json` meta.curations[n=19].
- `FACTS.md`: §1 metric l.173, §3 LB l.211, §4 runtime l.231 (F-RUN-31..34 l.265-268), §5 rules l.270, §6 models l.293 (F-MOD-34..38 l.330-334), §7 lab-to-LB l.336 (F-TRN-50 l.389), CONTRADICTIONS l.391 (C-150..C-158 l.544-552).
- `DECISIONS.md`: probes §1 l.125 (P45/P46 l.177-178; [c19] built/planned table l.339); gates §1b l.355; finals §2 l.420 ([c19] snapshot l.544); E10 §2f l.688 ([c19] l.815); OC §2g l.817; ladder/cards §2h l.848 ([c19] rows l.891-896); R1-R10 §3 l.898 (proposed R19 rows l.930-932).
- `WATCHLIST.md`: OVERDUE l.55, NEXT 24 H l.72, LATER l.104, INSIGHTS l.139 (I198-I213). Curator logs are in `research/KNOWLEDGE/_curation/{v4,2,...,19}/`.

Key sources (repo root):
- `CONTEXT.md` (anchors above).
- LB: `experiments/RESULTS.md` (rows up to P38 only); `experiments/lb_poll/poll.log`, `ledger.md` (P39 on); `experiments/e10_watch/20260927T1843Z.txt` (newest snapshot), `watch_loop.log`.
- Kernels: finals `experiments/exp58_x138_safe_lowref/` (#37), `experiments/exp58n_x138_safe_lowref/` (#38); rungs `experiments/exp70{b_k2_fm45,g_k2_cap6,q_k2_maxdiv}/probe.json`; 28 Sep `experiments/exp76a_k2fm_coordinject/`, `experiments/exp76d_k2fm_secft/`, `experiments/exp72_k2_secft/`, `experiments/exp75_k2_coordinject/`, `experiments/exp73a_k2_dc015/`..`exp73v_*`; trainers `experiments/exp71_secft_all/`, `experiments/exp77_secft_n2/` (N2).
- Tools: `tools/build_probe_kernel.py`, `tools/coordinject_patch.py`, `tools/runtime_ledger.py` (no exp72-77 family yet), `tools/e10_port_gate.py`, `experiments/lb_poll/e10_watch_loop.py`.
- Rounds: `research/wf_ideas_v4/round19/REPORT.md` (in Russian) and `report.json` (R19-A1..A12); `scan_hyp_reads_table.json`, `scan_plancheck.json`, `scan_recheck.json`, `scan_hyp_n1_prep.json`; older rounds in `round18/`..`round8/`, plus `research/wf_ideas_v4/bigger_levers/`.
- Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v4/round9/LESSONS_draft.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-365 / I-327 / I-390 / I-391 | R19-A1 amendment: UP test by SubmissionCount (S0 = `20260927T1743Z.txt`, count 46), 46-PENDING row, fallbacks per mechanism (the LSD proof I-389 is refuted) | Append it before 56606948 is terminal | `IDEAS.md` l.176, l.201, l.221-222 |
| I-326 / I-361 | P45 exp70g and P46 exp70q reads | Code them P5/U4/N4/NEG/ERR (+ 'v' if L_hi > 8.0 h) | `IDEAS.md` l.200, l.211 |
| I-385 / I-396 | N2 = exp77 (n2a/n2b), then exp70b + secswap rungs | User yes 18:19Z. Push after the GPU check; place the rungs in a logged line | `IDEAS.md` l.447, l.449 |
| I-376 / I-377 / I-363 | exp76c (exp70q + CI), exp76g (exp70q + secFT), exp76e (exp70b + cap 6), exp73m dummy | Build now; push exp76c by ~19:30Z; exp76e only if 45 is P5/U4 | `IDEAS.md` l.213, l.216-217 |
| I-392 / I-381 / I-383 | READ TABLE v2; W1 00:05/00:10/00:50Z; runtime_ledger families (CI 10.75 h) | Before 00:05Z 28 Sep; pass `--family` until then | `IDEAS.md` l.219, l.223, l.303 |
| I-382 / I-374 / I-375 | exp76a CI queue + its own gate vs exp70b; exp76d clean | Never re-push exp76a; exp72/exp75 are fallbacks | `IDEAS.md` l.302, l.335, l.444 |
| I-395 / I-300 / I-330 | tau 0.75 coin rung; 02:00Z cap lift; Q3 (secFT as a final) | One R19-A7 message after the 45 read; each defaults to NO | `IDEAS.md` l.225, l.188, l.443 |
| I-257 / I-229 / I-336 | RESUME POINT + MEMORY; tick checklist; HINDSIGHT GUARD | R19-A5 now; guard pushed before 29 Sep 23:00Z | `IDEAS.md` l.156, l.147, l.595 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/19/{ideas,facts,watch}.json`)

1. [now] **R19-A1 into CONTEXT before 45 is terminal** (8.0 h mark 19:15:12Z). Fill the <> fields from the latest poll header, then read 45 by the count rule with S0 = `experiments/e10_watch/20260927T1743Z.txt`. Choosing S0 by time could code a false N4; the 18:43Z snapshot still shows count 46. Sources: `report.json` R19-A1, plan_issues (1); `FACTS.md` C-156; `WATCHLIST.md` W195.
2. [now] **The user's N2 yes (18:19Z) contradicts three written closures:** card (6) 'no N1/N2 build', round 19's closed list, and R19-A2 (6). Log one amendment for N2 only (call it 'N2-FT (exp77)'); N1 stays out, and R9's hidden-test 'N2' ban stands. The amendment should say the rung takes the SEC slot only if its dummy PASSES by 23:45Z, otherwise it goes to W2, and that it is public-only while Q3 is open. Sources: `CONTEXT.md` l.3052, l.3070-3074; `FACTS.md` C-150; `IDEAS.md` I-396.
3. [now] **N2 weights go to NEW private datasets only.** Re-versioning `biohub-secft-all-v1` would hard-fail the sha check in exp72/exp76d/exp76g, including the 00:10Z SEC submit. Sources: `research/wf_ideas_v4/round19/scan_plancheck.notes.md`; `research/KNOWLEDGE/_curation/19/watch.json` (risk alert).
4. [now] **R19-A5 RESUME POINT, 46 waiter, MEMORY.** Add a waiter for 46 (22:36:59Z), fix the 00:05Z waiter's echo, and record the exp77 push/output state. MEMORY.md is stale, and the last RESUME POINT is l.2599. Sources: `report.json` R19-A5; `WATCHLIST.md` W185, W207; `FACTS.md` C-26.
5. [now] **R19-A3 builds.** Build exp76c/e/g with `MSYS_NO_PATHCONV=1` and the KQ order, and push exp76c first, by ~19:30Z (CI queues ~3.3 h). Then push exp76g and exp73m, and exp76e only after a P5/U4 45 read. Never re-push exp76a; gate it by R19-A4 against exp70b, not exp75. Sources: `report.json` R19-A3, R19-A4; `FACTS.md` F-RUN-34.
6. [now] **GPU quota was last read on 26 Sep.** Tonight needs ~8-9 GPU-h: N2 ~3, R19-A3 ~2-2.5, R19-A9 W2 dummies (need >= 6 h left), the tau rung ~0.5. Read the Settings page before pushing exp77, and log the push order: CI dummies first, exp77 in the next free lane. Sources: `report.json` R19-A3, R19-A9; `experiments/exp77_secft_n2/cells/md_00_intro.py`.
7. [today] **Name clash and ledger.** exp77 is now the N2 trainer, so the tau rung needs another name (e.g. exp78a), and the R19-A6 `exp77[a-z]*` rule must be fixed. Land R19-A6 (safetail_ci 10.75 h, divins 10.2 h, exp72-77 rules, one test) before 00:05Z. Sources: `FACTS.md` C-153, F-RUN-32; `report.json` R19-A6, R19-A8.
8. [today] **R19-A7 user message after the 45 read** (~19:00-19:30Z). Ask 3 yes/no questions: tau (due 23:30Z), the 02:00Z cap (due 29 Sep 00:00Z), Q3 (due 29 Sep 19:00Z). Also cover N2 rung placement and disclose that coordinject runs on the general directive. Quote +0.00215 (in-sample) and L ~9.8-10.45 h. Sources: `report.json` R19-A7; `FACTS.md` C-151, C-155.
9. [today / before-finals] **Corrections and records:** log the R19-A10 (a)-(d) corrections (V6 is not a division read; exp72 gates d78093ac / 121,061 nodes / 80 forks; N1 staging); add RESULTS rows P39-P46; change probe.json 'compare with exp56' to exp70b; write ROUND 14-19 RECORDs, LESSONS H1, NEVER_SUBMIT for exp70j/k; make the R19-A12 commit by named paths with no trailer; do NOT upload `_dl/secft_x2_ds` / `_dl/secft_x3_ds` (N1). Sources: `report.json` R19-A10, R19-A12; `FACTS.md` C-118, F-MOD-38; `WATCHLIST.md` OVERDUE l.55.

**RESOLVED since curation 18:**
- The round-18 pre-score card was logged pre-score at 16:08 (l.3011-3056), while both refs were PENDING at 15:53/16:03Z, and committed in 12d9271.
- exp76a/exp76d were built and rebased onto exp70b (l.3057-3062). The exp76d dummy is clean (l.3063).
- The exp75 queue stall ended and its dummy is clean (l.3065-3069), so R18-A4 (drop CI at 19:00Z / re-push) is withdrawn (`WATCHLIST.md` W187).

## HOW TO USE

- "Score of probe N, what changed?" -> `DECISIONS.md` §1, `experiments/RESULTS.md` (up to P38), `experiments/lb_poll/poll.log` / `ledger.md` (P39 on), `experiments/<exp>/probe.json`.
- "45/46 scored, what now?" -> the 16:08 card (`CONTEXT.md` l.3011-3056) + R19-A1 (in CONTEXT once logged; else `research/wf_ideas_v4/round19/report.json`); `DECISIONS.md` §2h l.893.
- "What goes out on 28 Sep / where does N2 go?" -> `report.json` R19-A2; `DECISIONS.md` §1 [c19] table l.339; `WATCHLIST.md` W196; `IDEAS.md` I-396.
- "Did a public notebook beat us (E10 v3)?" -> `CONTEXT.md` l.2917-2926; `DECISIONS.md` §2f l.815; `experiments/e10_watch/watch_loop.log`.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~18:50Z 27 Sep, check the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, and the newest `research/wf_ideas_v4/round*/`.
