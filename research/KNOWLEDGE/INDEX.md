# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 15: state as of 2026-09-27 ~06:15 UTC. Git HEAD da9766e (= origin/main; probes 43/44 submitted) plus the untracked `research/wf_ideas_v4/round15/`, `experiments/e10_watch/20260927T0531Z.txt` and `experiments/ext_optimized-biohub-max-score/v6_2026-09-27/`. Previous curation: 14 (~02:25 UTC, f24ff72). Hashes older than 26 Sep 10:15 are pre-rewrite (`experiments/git_rewrite_map_2026-09-26.txt`). All times are UTC, and every line cites its source.
Deadline 29 Sep 23:59; the user ticks finals MANUALLY by 29 Sep 20:00. `CONTEXT.md` gained six entries since curation 14 (l.2750-2813); the last is SUBMIT 43/44 (05:28) at l.2809-2813, just above `## 9. Literature` at l.2814. Anchors:
- Rules: PRE-REG v3 l.1576-1736 (R7-R9 at l.1665-1673); E10 PORT RULE l.2138-2147; E10 v2 PROPOSED l.2352-2361; LADDER + L9 l.2407-2424; RULE RECONCILIATION l.2502-2529; E10 HARDENING l.2550-2569.
- 27 Sep: ROUND 13 RECORD l.2626-2663; LADDER PRE-SCORE REGISTRATION (R13-A1) l.2664-2721; EXP71/72 GOVERNANCE l.2722-2746; R14 PRE-SCORE NOTES l.2750-2775; READ SHEET v1 l.2776-2785; WATCH TIMERS l.2786-2788; LADDER READ D1 l.2789-2799; POST-D1 RUNGS l.2800-2808; SUBMIT 43/44 l.2809-2813. Not yet logged: ROUND 14 RECORD, R15-A1, ROUND 15 RECORD (`research/wf_ideas_v4/round15/report.json`).

## STATE IN 10 LINES

1. **Finals TICKED 2/2:** #37 K2 exp58 (56563521) = **0.954** and #38 twin exp58n (56563534) = **0.953**. D1 left the pair unchanged (row D1-3). API SELECTED last read 20:04:35Z; next read at the 07:30Z push, 'after probes 39-44'. Sources: `experiments/RESULTS.md` l.70-71; `CONTEXT.md` l.2789-2799; `DECISIONS.md` §2 [c15] l.412, snapshot l.421; `report.json` R15-A3.
2. **LB #256 of 3,938** at 0.954 (05:32Z; was #242), 17th of 102 in the 0.954 block; 239 teams >= 0.955 (+13 in 3.7 h). Info only; private (~71%) decides. Sources: `experiments/e10_watch/20260927T0531Z.txt` l.396; `WATCHLIST.md` I158.
3. **Base** = x138 + safetail + lowrefine + gated DaughterNet insertion (K2). Insertion '+0.006' is in-sample; honest OOF +0.0019. Sources: `CONTEXT.md` l.2407-2409; `FACTS.md` F-TRN-44.
4. **D1 (04:58Z):** P39 exp70e **0.949**, P40 exp70a **0.954** (no attributable UP; rank 242 -> 253), P41 exp70d **0.949**; all within 7.42 h, insertion gate did NOT fire. BASE none -> **no combo**, A-only extension did not fire. Sources: `CONTEXT.md` l.2789-2799; `experiments/lb_poll/ledger.md`; `FACTS.md` F-TRN-46.
5. **Key new fact:** DeepCenter safe-div 0.25 -> 0.30 costs **-0.005 public** while the exp60 lab said +0.0013: the lab sign was wrong for this knob; one public division TP ~0.0015-0.0023. Sources: `CONTEXT.md` l.2795-2798; `FACTS.md` F-TRN-45, F-MOD-31; `IDEAS.md` I-074, I-347.
6. **PENDING at 06:11:39Z:** P42 exp70b fm45 (56592350; D2 ~07:27-08:30Z, 9.0 h clock 09:05:50Z); **P43 exp70j DC 0.20 (56598763), P44 exp70k DC 0.225 (56598765)**, scores ~12:20-13:10Z (9.0 h clocks 14:28:13Z / 14:28:22Z). The watcher exits after exp70b; poll.log is then the only record. Sources: `experiments/lb_poll/ladder_watch/calls.jsonl` 06:11:39Z; `DECISIONS.md` §1 l.139-140; `WATCHLIST.md` T70.
7. **43/44 are class C and a registered-rule breach** (R13-A1 (1)/(5)(a), 5-submit cap, L9; no user OK). Round 15 proposes a DEVIATION RECORD + FREEZE (no further DC rung/combo/ladder submit) and a CLASS-C FINALS TABLE (default (a) no change). Honest prior P(>= 0.955) ~0.08-0.20 per rung, not 0.2-0.3. **None of it is in CONTEXT yet.** Sources: `FACTS.md` C-111, C-113, C-120; `IDEAS.md` I-344, I-345; `report.json` R15-A1.
8. **E10:** v1 (>= 0.956) in force; P1 at 05:31Z NOT met (largest P2 group 2). amanatar V6 is an unscored x138 knob bundle that fails P3: watch-only. v2 (>= 0.954) lapses at 12:00Z without an OK. Sources: `experiments/e10_watch/20260927T0531Z.txt`; `experiments/ext_optimized-biohub-max-score/v6_2026-09-27/NOTES.md`; `DECISIONS.md` §2f l.665; `FACTS.md` C-114.
9. **Next decision points:** now (hard 11:45Z) log+push R15-A1; 07:30Z SELECTED read + R15-A2 push/brief (65b1b746); D2 ~07:27-08:30Z; round 16 ~08:00Z; exp71 yes by ~09:00Z; **12:00Z R8 cutoff, E10 v2 lapse, class-C answer**; 43/44 read ~12:15-13:10Z; 29 Sep 19:00 L9 read, 20:00 ticks. Sources: `WATCHLIST.md` NEXT 24 H l.69, LATER l.107.
10. **Ideas ledger:** 353 ideas (lb-tested 46, lab-tested 21, refuted 182, deferred 41, in-plan 61, open 2). Nothing reaches R8. Strict orphan: I-233. Sources: `IDEAS.md` l.66, CHANGES (15) l.68, ORPHANS l.572.

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` this page; `CHANGES.md` per-curation deltas (v4, 2-15).
- `IDEAS.md` + `ideas.json`: I-001..I-353 in 13 clusters: FINALS l.116, LADDER l.165, BASE l.195, RUN l.230, LOC l.269, DIV l.300, MODEL l.362, NODES l.406, INFER l.440, EF l.462, LINK l.482, VALID l.513, TESTSET l.554, ORPHANS l.572. Per-ID log: `ideas.json` meta.curations[n=15].
- `FACTS.md`: §1 metric l.123, §3 LB l.161, §4 runtime l.181, §5 rules l.214, §6 models l.237, §7 lab-to-LB l.273, CONTRADICTIONS l.324 (C-111..C-120 at l.438-447).
- `DECISIONS.md`: probes §1 l.89 (P43/P44 l.139-140); gates §1b l.259; finals §2 l.324 (c15 snapshot l.421); E10 §2f l.566; OC §2g l.671; ladder/L9 §2h l.702; R1-R10 §3 l.732.
- `WATCHLIST.md`: OVERDUE l.56, NEXT 24 H l.69, LATER l.107, INSIGHTS l.143 (I149-I159). Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,15}/`.

Key sources (repo root): `CONTEXT.md` (source of truth, anchors above). LB: `experiments/RESULTS.md` (rows to P38 only), `experiments/lb_poll/poll.log` + `ledger.md` (39+), `experiments/lb_poll/ladder_watch/` (`watch.log`, `calls.jsonl`; never open `state.json`), `experiments/e10_watch/20260927T0531Z.txt` (newest E10/LB snapshot). Kernels: finals `experiments/exp58_x138_safe_lowref/` (#37), `experiments/exp58n_x138_safe_lowref/` (#38); ladder `experiments/exp70{a_k2_lp30,d_k2_dc030,e_k2_lp30_dc030,b_k2_fm45,g_k2_cap6,j_k2_dc020,k_k2_dc0225}/probe.json`; retrain `experiments/exp71_secft_all/` (NEVER_SUBMIT.md). Tools: `tools/build_probe_kernel.py`, `tools/runtime_ledger.py`, `tools/e10_port_gate.py`, `tools/e10_snapshot.py`. Rounds: `research/wf_ideas_v4/round15/` (UNTRACKED; `report.json` R15-A0..A8, `scan_*.json`, no REPORT.md yet), `round14/`..`round8/`, `reach0955/`; round prompt `experiments/workflows/biohub-research-round.js` (l.37 still sends the browser agent to the API). Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v4/round9/LESSONS_draft.md`, `PROMPT_FRIEND_C.md`, `TEAM.md`, `research/discussions_summary.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-345 / I-344 | Deviation record + DC FREEZE; class-C finals table for 43/44 | In-plan, at risk: text in R15-A1, not in CONTEXT; log+push before 11:45Z; class-C letter only counts if logged before the first 43/44 terminal header | `IDEAS.md` l.191, l.160 |
| I-306 | exp70b (K2 + fm45), probe 42 | D2 by READ SHEET v1: V* only if COMPLETE, >= 0.955, L_hi <= 9.0 h -> {exp70b, #38}; else pair stays | `IDEAS.md` l.176 |
| I-341 / I-342 / I-346 | exp70j DC 0.20, exp70k DC 0.225; NARROW/BROAD reading note | Read mechanically ~12:15-13:10Z; no new submit whatever they show | `IDEAS.md` l.188-189, l.356 |
| I-315 / I-258 | 07:30Z push + brief (R15-A2 form); API SELECTED read | P-A by default (P-B only if 42 is V*); disclose the breach; SELECTED 'after probes 39-44' | `IDEAS.md` l.157, l.148 |
| I-286 / I-299 | E10 v2; E10 insertion-hedge pair rows | Answer by 12:00Z or lapse line; pair rows are missing from the brief | `IDEAS.md` l.220, l.156 |
| I-119 / I-330 / I-106 | exp71 -> exp72 FT secondary; G2 veto; exp23 w/ public primary | Blocked until Q1-Q3; a yes is needed by ~09:00Z | `IDEAS.md` l.390, l.403, l.377 |
| I-336 / I-252 / I-348 | HINDSIGHT GUARD; LESSONS; per-embryo DC study | Guard PUSHED before 29 Sep 23:00Z; R14-A7/R15-A8 edits by 30 Sep; DC study post-deadline | `IDEAS.md` l.549, l.538, l.358 |
| I-229 / I-283 / I-233 | Tick checklist; private-read v2 + L6/L7; poller error_description | L9 read 29 Sep 19:00Z; L6/L7 ride in R15-A1; close I-233 by name at R8 | `IDEAS.md` l.138, l.543, l.254 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/15/{ideas,facts,watch}.json`)

1. [now] **Log R15-A1 in CONTEXT** (date -u): deviation record, FREEZE, class-C finals table, honest priors, NARROW/BROAD note, L6/L7 + DC-DOSE, 'watcher paused' correction. Save `round15/REPORT.md` from `report_md_ru` (R15-A0); commit as the user (no trailer) with `round15/`, the 0531Z snapshot and ext v6; push; log the hash. Hard 11:45Z; after the first 43/44 terminal header every class-C read is post-hoc. Sources: `report.json` R15-A0, R15-A1; `WATCHLIST.md` W151, W152; `FACTS.md` C-111, C-112.
2. [now] **Disclose the 43/44 breach** in the brief (R15-A2 §2); after scoring, no further DC rung, no DC combo, no ladder submit unless the user asks (I-343, I-349 rejected). Sources: `CONTEXT.md` l.2800-2813; `IDEAS.md` I-345; `FACTS.md` C-111.
3. [now] **07:30Z (65b1b746): SELECTED read, then R15-A2 push (P-A, or P-B only if 42 is V*) + brief**, not the stale R14-A4 variants. Questions: class C (by 12:00Z), E10 v2, Q1-Q3, R8 cap; **add the E10 pair-row line (I-299)**. Log each answer with date -u. Sources: `report.json` R15-A2, R15-A3; `WATCHLIST.md` W136, W153.
4. [today] **D2 read of P42** at the first header with 56592350 terminal: READ SHEET v1 mechanically, quote the ledger insertion-gate text, one CONTEXT line; ERROR at < 10 h allows one unchanged resubmit. Sources: `report.json` R15-A4; `WATCHLIST.md` W141.
5. [today] **Records are stale:** RESULTS.md has no rows for P39-P44 (add 39-41 now: 0.949/0.954/0.949); ROUND 14 RECORD (R14-A6) and ROUND 15 RECORD (R15-A6) not logged; exp70g/j/k lack NEVER_SUBMIT.md; exp70* probe.json say 'above exp56 adopt'. Sources: `experiments/RESULTS.md` l.71; `FACTS.md` C-115, C-118; `WATCHLIST.md` W126, W142, W146, W155.
6. [today] **12:00Z R8 / E10 v2 lapse:** log 'E10 v2 lapsed; R8 passed; no new mechanism' (or the answers), close I-323/I-324/I-233 by name. E10 is exempt from R8 (the V6 NOTES reason is wrong; verdict watch-only stands). Next E10 P1 >= 06:45Z, ideally after exp70b's event. Sources: `report.json` R15-A7; `FACTS.md` C-114; `WATCHLIST.md` W149, W157.
7. [today] **Round 16 (~08:00Z) prompt still sends the browser agent to the API** (l.37; l.38 stale); fix or pass a focus before round 16. Timers are session-only and one-shot timers 5b23a3ed/54a8f20d still show on CronList; confirm 65b1b746 fires. Sources: `experiments/workflows/biohub-research-round.js` l.35-38; `WATCHLIST.md` W150, I159, T67.
8. [before-finals] **Any pair change is the user's manual re-tick by 29 Sep 20:00Z**, exactly 2 by ref; re-read SELECTED after each. Carry I149 (#38 hedge void if eps = 0) and I150 (E[score] vs block-step utility) into the 29 Sep 19:00Z L9 read. Push the HINDSIGHT GUARD before 29 Sep 23:00Z; W57 family and LESSONS l.7 still overdue; MEMORY index line stale. Sources: `DECISIONS.md` §2 [c15]; `WATCHLIST.md` I149, I150, W57, W98; `FACTS.md` C-75.
9. [info] **Public DC chase on one embryo:** the lab got this knob's sign wrong; the only out-of-public evidence (6bba dc0.20 -0.0008, 0 TP / +6 FP) leans against transfer. Keep default (a) unless a pre-score letter exists. Sources: `FACTS.md` F-TRN-45, C-113; `IDEAS.md` I-346..I-348.

**RESOLVED since curation 14:** watcher launched 03:35Z (PID 10088, 3 fresh events; I-327 done); R14-A2 pre-score notes + READ SHEET v1 + round14/REPORT.md pushed before any score (8155321, 02:29:01Z); timers logged (a129e5f); D1 read applied (862869f); SELECTED timing settled (07:30Z); W150's feared quiet-window API call happened at 05:31Z with no 429 (`CONTEXT.md` l.2750-2799; `FACTS.md` C-104, C-106, C-108 resolved).

## HOW TO USE

- "Score of probe N, what changed?" -> `DECISIONS.md` §1, `experiments/RESULTS.md` (to P38), `experiments/lb_poll/poll.log` / `ledger.md` (39+), `experiments/<exp>/probe.json`.
- "Probe 42/43/44 scored, what are the finals?" -> READ SHEET v1 (`CONTEXT.md` l.2776-2785), class-C table (`report.json` R15-A1 (4); `IDEAS.md` I-344), `DECISIONS.md` §2 l.421, L9 `CONTEXT.md` l.2407-2424.
- "Is the watcher alive? Who passed us?" -> `experiments/lb_poll/ladder_watch/watch.log`, `calls.jsonl`; `experiments/e10_watch/` newest snapshot.
- "Can exp72 be submitted?" -> `CONTEXT.md` l.2722-2746; `IDEAS.md` I-119/I-330/I-106. "Public successor appeared?" -> `DECISIONS.md` §2f, `CONTEXT.md` l.2138-2147, l.2550-2569; `IDEAS.md` I-286.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736, l.2664-2721.
- "Was idea X tried?" -> search its mechanism in `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~06:15Z 27 Sep: tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, `ladder_watch/`, newest `research/wf_ideas_v4/round*/`.
