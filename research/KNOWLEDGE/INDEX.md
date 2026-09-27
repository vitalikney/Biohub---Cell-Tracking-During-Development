# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 18: state as of 2026-09-27 ~16:05 UTC. Git HEAD b853642 (probe 46 = exp70q submitted) = origin/main (`git status -sb`). Untracked: `research/wf_ideas_v4/round18/`, `research/KNOWLEDGE/_curation/18/`, `experiments/e10_watch/20260927T1343Z..1543Z.txt`, `experiments/ds_secw_corwin_v1/weights/`. Previous curation: 17 (~12:05 UTC, a6ffbc9). Hashes older than 26 Sep 10:15 are pre-rewrite (`experiments/git_rewrite_map_2026-09-26.txt`). All times are UTC, and every line cites its source.
Deadline 29 Sep 23:59; the user ticks finals MANUALLY (our buffer 20:00; Kaggle accepts re-ticks until 23:59, `WATCHLIST.md` LATER). `CONTEXT.md` gained seven entries since curation 17, at l.2952-3010; `## 9. Literature` is at l.3011. Anchors:
- Rules: PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147; LADDER + L9 l.2407-2424; RULE RECONCILIATION l.2502-2529; 43/44 PRE-SCORE ENTRY l.2814-2871; user letters (E10 v3, class-C (b), Q1/Q2, FREEZE lifted, aggressive mode) l.2917-2951.
- 27 Sep since c17: l.2952-2954 12:00 line; l.2955-2971 R8 FULL RECORD; l.2972-2982 last-slot pre-score line; l.2983-2994 bigger levers ready; l.2995-3000 P43/P44 READ; l.3001-3006 exp71 done + exp72 built; l.3007-3010 P46 exp70q submitted.
- Not yet logged: the round-18 pre-score card (R18-A1), ROUND 14-18 RECORDs, the exp72 dummy gate values. The newest RESUME POINT (l.2599, 26 Sep 22:46) is stale (`research/wf_ideas_v4/round18/report.json` R18-A1, R18-A2).

## STATE IN 10 LINES

1. **Finals TICKED 2/2 (unchanged):** #37 K2 exp58 (56563521) = **0.954** and #38 twin exp58n (56563534) = **0.953**; API SELECTED last read 07:41:28Z. Sources: `CONTEXT.md` l.2995-3000; `DECISIONS.md` §2 [c18] snapshot l.523.
2. **LB #283 of 3,952** at 0.954 (15:43Z), 6th of 113 in the 0.954 block; 277 teams are >= 0.955 (was 276). Info only; the private LB (~71%) decides. Sources: `experiments/e10_watch/20260927T1543Z.txt` l.950-956.
3. **Base** = K2 (x138 + safetail + lowrefine + gated DaughterNet insertion). Public 0.954 files: #37, P40 exp70a, P42 exp70b, P43 exp70j, P44 exp70k. exp70b sits ~5e-5 below the 0.9545 display edge, K2 files ~1.0-1.3e-4. Sources: `experiments/lb_poll/poll.log` 16:03:10Z header; `FACTS.md` F-TRN-49 l.383.
4. **P43/P44 read 13:14Z:** both 0.954, 0 TeamIds passed. No V*_C, so class-C letter (b) did not fire; DC closed on this side; exp70r not submitted. Sources: `CONTEXT.md` l.2995-3000; `DECISIONS.md` §2h l.863.
5. **Running now (PENDING at 16:03:10Z):** P45 exp70g K2 + cap 6 (56606948, 11:15:12Z): window ~17:56-18:59Z, 8.0 h mark 19:15Z. P46 exp70q K2 + cap 6 + thr 0.3 + fm 4.5 (56611472, 14:36:59Z): ~21:18-22:21Z, 8.0 h mark 22:37Z. Latency is drifting up. Sources: `experiments/lb_poll/poll.log` l.15514-15520; `FACTS.md` F-RUN-31 l.264.
6. **GPU / builds:** exp71 COMPLETE 13:25Z; exp72 (K2 + secFT, f3d23bcd) dummy clean (121,061 nodes -0.158%, 80 forks, 0 errors). exp75 (K2 + coordinject) dummy QUEUED since 13:18Z. No `experiments/exp76*` folder yet. Sources: `CONTEXT.md` l.3001-3010; `research/wf_ideas_v4/round18/report.json` R18-A3, R18-A4.
7. **Slots:** 27 Sep 5/5 used. **28 Sep plan (round 18):** W1 = exp76a (exp70b + coordinject, sha 1bc05bc9) and exp76d (exp70b + secFT, sha 87d257ba) at 00:05/00:25/00:45Z; exp72/exp75 are fallbacks; one slot held for E10 v3 until 12:00Z. This supersedes the chat line 'exp72 at 00:05Z, exp75 best chance'. Sources: `research/wf_ideas_v4/round18/report.json` R18-A3, R18-A7; `DECISIONS.md` §2h l.865; `FACTS.md` C-144.
8. **Watchers:** E10 v3 hourly loop LIVE since 12:43:42Z, 4 runs, 0 signals (until 29 Sep 12:00Z); LB poller every ~10 min. Research rounds are NOT on a fixed timer: mean gap 2.72 h, median 2.52 h, range 1.73-4.25 h; no job for rounds 19/20. Sources: `experiments/e10_watch/watch_loop.log`; `FACTS.md` F-RUN-33 l.266, C-148 l.536.
9. **Next decision points:** now: R18-A0 user reply, R18-A2 RESUME POINT + local-time timers, exp76a/d build + dummies; before 17:50Z: pre-score card R18-A1 + commit; ~17:56-19:15Z: P45 read; 19:00Z: CI queue-stall decision; ~21:18-22:40Z: P46 read + R18-A6 brief (02:00Z cap?, exp74?); 23:45Z: W1 dummies PASS; 28 Sep 00:05Z: W1. Sources: `WATCHLIST.md` NEXT 24 H l.79; `report.json` R18-A0..A7.
10. **Ideas ledger:** 388 ideas (lb-tested 51, lab-tested 21, refuted 192, deferred 45, in-plan 76, open 3). Strict orphan: I-233. Sources: `IDEAS.md` CHANGES (18) l.88-99, ORPHANS l.610.

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` is this page. `CHANGES.md` holds the per-curation deltas (v4, 2-18).
- `IDEAS.md` + `ideas.json`: I-001..I-388 in 13 clusters. FINALS l.119, LADDER l.175, BASE l.215, RUN l.252, LOC l.293, DIV l.326, MODEL l.389, NODES l.438, INFER l.472, EF l.494, LINK l.514, VALID l.545, TESTSET l.592, ORPHANS l.610. Per-ID log: `ideas.json` meta.curations[n=18].
- `FACTS.md`: §1 metric l.172, §3 LB l.210, §4 runtime l.230 (F-RUN-31..33 l.264-266), §5 rules l.268, §6 models l.291 (F-MOD-34/35 l.328-329), §7 lab-to-LB l.331, CONTRADICTIONS l.385 (C-144..C-149 from l.532).
- `DECISIONS.md`: probes §1 l.124 (P43-P46 l.174-177; built/planned table l.319); gates §1b l.336; finals §2 l.401 (c18 snapshot l.523); E10 §2f l.666 (v3 l.786); OC §2g l.793; ladder/L9 + round-18 card §2h l.824 (l.861-866); R1-R10 §3 l.868.
- `WATCHLIST.md`: OVERDUE l.65, NEXT 24 H l.79, LATER l.110, INSIGHTS l.143 (I187-I197). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,18}/`.

Key sources (repo root):
- `CONTEXT.md` (source of truth; anchors above). LB: `experiments/RESULTS.md` (rows up to P38 only); `experiments/lb_poll/poll.log`, `ledger.md` (P39 on); `experiments/e10_watch/20260927T1543Z.txt` (newest snapshot), `watch_loop.log`.
- Kernels: finals `experiments/exp58_x138_safe_lowref/` (#37), `experiments/exp58n_x138_safe_lowref/` (#38); public rungs `experiments/exp70{b_k2_fm45,g_k2_cap6,j_k2_dc020,k_k2_dc0225,q_k2_maxdiv}/probe.json`; 28 Sep `experiments/exp72_k2_secft/`, `experiments/exp75_k2_coordinject/`, `experiments/exp73a_k2_dc015/`..`exp73v_*`, `experiments/exp74_k2_secw_corwin/`; retrain `experiments/exp71_secft_all/`.
- Tools: `tools/build_probe_kernel.py`, `tools/coordinject_patch.py`, `tools/runtime_ledger.py` (no exp72-76 family yet), `tools/e10_port_gate.py`, `tools/e10_snapshot.py`, `experiments/lb_poll/e10_watch_loop.py`.
- Rounds: `research/wf_ideas_v4/round18/REPORT.md` + `report.json` (R18-A0..A10, next_focus), `scan_hyp_slots_28sep.json` (exp76a-i), `scan_plancheck.json`; `round17/`..`round8/`; `research/wf_ideas_v4/bigger_levers/`, `e10v3/`.
- Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v4/round9/LESSONS_draft.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-365 / I-298 | Pre-score card for P45/P46/W1 files (codes P5/U4/N4/NEG/ERR, MASKED, 'v' suffix); pair {V*, #37} | Log R18-A1 before 17:50Z; >= 0.955 + L_hi <= 9.0 h -> finals proposal with #37 | `IDEAS.md` l.170, l.158 |
| I-326 / I-361 | P45 exp70g, P46 exp70q scoring | Read with the card; 'v' if L_hi > 8.0 h | `IDEAS.md` l.193, l.204 |
| I-373 / I-374 / I-375 | Rebase 28 Sep on exp70b: W1 = exp76a (+CI), exp76d (+secFT) | Build + dummy now; exp72/exp75 fallbacks | `IDEAS.md` l.208, l.322, l.431 |
| I-376 / I-377 / I-379 | Conditional stacks exp76c/g/h (exp70q base), exp76e/i (cap 6), exp76f | Only by the 45/46 codes | `IDEAS.md` l.209-210, l.432 |
| I-382 / I-324 | Coordinject silent no-op + queue-stall guard; exp75 sign probe (P ~0.35-0.45) | Re-push once if stuck; drop CI from W1 at 19:00Z if still stuck | `IDEAS.md` l.289, l.321 |
| I-381 / I-383 | Slot budget + stagger; runtime_ledger families (safetail_ci) | Ledger edit before 00:05Z 28 Sep; `--family` until then | `IDEAS.md` l.212, l.290 |
| I-323 / I-119 | exp74 Corwin secondary (default no); exp72 as a final (Q3 open) | R18-A6 yes/no questions after the P46 read | `IDEAS.md` l.429, l.417 |
| I-257 / I-229 / I-336 | RESUME POINT + MEMORY; tick checklist; HINDSIGHT GUARD | R18-A2 now; guard pushed before 29 Sep 23:00Z | `IDEAS.md` ORPHANS l.610, l.141, l.581 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/18/{ideas,facts,watch}.json`)

1. [now] **Answer the user's cadence question with R18-A0, with the three plan corrections.** Rounds run about every 2.5-3 h on average, launched back to back by session timers, with no fixed cron (the ~2.5 h mandate ended 27 Sep 12:00Z). The corrections: W1 = exp76a/exp76d, not exp72 first; exp75 is a sign probe, not 'the best chance'; exp75 has been stuck QUEUED. Offer a fixed timer only if asked (I-388). Sources: `FACTS.md` F-RUN-33, C-144, C-148; `report.json` R18-A0.
2. [now] **Pre-score card R18-A1 into CONTEXT before 17:50Z** (P45 can score from ~17:56Z). Fill the <> fields from the latest poll header, then commit with `round18/` by named paths, as the user, with no trailer (R18-A10). Sources: `report.json` R18-A1, R18-A10; `DECISIONS.md` §2h l.864.
3. [now] **RESUME POINT, timers, MEMORY (R18-A2).** Create one-shot timers with LOCAL (UTC+3) cron fields `5 22 27 9 *`, `45 1 28 9 *`, `3 3 28 9 *`, `30 9 28 9 *`, and delete the fired timers 5b23a3ed/54a8f20d/cdd738f1. Fix MEMORY l.8-9 and copy `fb_ins35.py` out of the scratchpad. Sources: `report.json` R18-A2; `WATCHLIST.md` W185; `FACTS.md` C-26.
4. [today] **Build exp76a (1bc05bc9) and exp76d (87d257ba) and push both dummies now.** Export `MSYS_NO_PATHCONV=1`, keep the KQ knob order and check the sha before the push. exp76a shares the stalled coord-inject dataset: re-push once if QUEUED >= 30 min, drop CI from W1 at 19:00Z if still stuck, and tell the user. Sources: `report.json` R18-A3, R18-A4; `WATCHLIST.md` W186, W187, I191.
5. [today] **`tools/runtime_ledger.py` family for exp72-76** (safetail_ci, 10.75 h) plus one test before 00:05Z 28 Sep. Otherwise CI latency reads as 'insertion gate MAY have fired'. Sources: `FACTS.md` F-RUN-32; `report.json` R18-A5.
6. [today] **Reads P45/P46 with the 'v' check** (L_hi vs 8.0 h; grep 'DIVINS SKIPPED (deadline)'). After P46: slot table + one brief with 2 yes/no questions (lift the 29 Sep 02:00Z cap? exp74?; default no, treat 02:00Z as binding). W1 dummies PASS by 23:45Z. Sources: `report.json` R18-A6, R18-A7, R18-A8; `FACTS.md` F-RUN-31, C-86.
7. [today] **Records:** log the exp72 dummy gates (121,061 nodes, CSV d78093ac, 80 forks) and fix the 'compare with exp56' text in `experiments/exp72_k2_secft/probe.json` and exp75; add RESULTS rows P39-P46; NEVER_SUBMIT.md for exp70j/k; mark exp70n not planned. Sources: `report.json` R18-A3 (5); `WATCHLIST.md` W126, W182; `FACTS.md` C-118.
8. [before-finals / info] **Records and lessons:** ROUND 14-18 RECORDs and LESSONS H1 after the 46 read. Post-deadline ideas I-384..I-387 and I-368 go into LESSONS s4 by 30 Sep. Name E10 v3 SI copies explicitly, because the `exp73` token collides with exp73a..v. x138's per-frame alignment cancels exp71's bias shift, so do not oversell exp76d. Sources: `report.json` R18-A9; `WATCHLIST.md` W176, I189, I190.

**RESOLVED since curation 17:**
- 12:00Z line completed by the 12:12 R8 FULL RECORD, with slot count, bracket check and deviation record (`CONTEXT.md` l.2955-2971).
- R17-A3 last-slot line logged before any 43/44 score (l.2972-2982). P43/P44 read (l.2995-3000). Last 27 Sep slot used (P46 exp70q, l.3007-3010).
- E10 v3 tooling committed (c86fd5a); loop live. Bigger levers logged (l.2983-2994); exp71 done, exp72 built (l.3001-3006). Round 17 committed (ac08c5e).

## HOW TO USE

- "Score of probe N, what changed?" -> `DECISIONS.md` §1, `experiments/RESULTS.md` (up to P38), `experiments/lb_poll/poll.log` / `ledger.md` (P39 on), `experiments/<exp>/probe.json`.
- "45/46 scored, what now?" -> R18-A1 card (in CONTEXT once logged; else `research/wf_ideas_v4/round18/report.json`); `DECISIONS.md` §2h l.864-865, §2 l.523; `FACTS.md` F-RUN-31.
- "What goes out on 28 Sep?" -> `research/wf_ideas_v4/round18/scan_hyp_slots_28sep.json`; `DECISIONS.md` §1 built/planned table l.319; `WATCHLIST.md` W186-W190.
- "Did a public notebook beat us (E10 v3)?" -> `CONTEXT.md` l.2917-2926; `DECISIONS.md` §2f l.786; `experiments/e10_watch/watch_loop.log` and the newest snapshot.
- "How often do the agents run?" -> `FACTS.md` F-RUN-33; `experiments/e10_watch/watch_loop.log`; `research/wf_ideas_v4/round18/report.json` R18-A0.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~16:05Z 27 Sep: the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, and the newest `research/wf_ideas_v4/round*/`.
