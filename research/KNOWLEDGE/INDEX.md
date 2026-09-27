# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 17: state as of 2026-09-27 ~12:05 UTC. Git HEAD a6ffbc9 (the 12:00 UTC line; = origin/main, `git status -sb`) on top of 9cdc047 (aggressive mode). Untracked: `research/wf_ideas_v4/round17/`, `research/wf_ideas_v4/bigger_levers/`, `research/wf_ideas_v4/e10v3/`, `experiments/exp73a..exp73v/`, `experiments/exp74_k2_secw_corwin/`, `experiments/ds_secw_corwin_v1/`, `experiments/e10_watch/20260927T1101Z.txt`. Also uncommitted: `tools/e10_snapshot.py`, `tools/e10_port_gate.py` and `tools/build_probe_kernel.py`. Previous curation: 16 (~09:15 UTC, 0bd1408). Hashes older than 26 Sep 10:15 are pre-rewrite (`experiments/git_rewrite_map_2026-09-26.txt`). All times are UTC, and every line cites its source.
Deadline 29 Sep 23:59; the user ticks finals MANUALLY (our buffer 20:00; Kaggle accepts re-ticks until 23:59, `WATCHLIST.md` I181). `CONTEXT.md` gained nine entries since curation 16, at l.2880-2954; `## 9. Literature` is at l.2955. Anchors:
- Rules: PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147; LADDER + L9 l.2407-2424; RULE RECONCILIATION l.2502-2529; E10 HARDENING l.2550-2569; 43/44 PRE-SCORE ENTRY (class-C table) l.2814-2871.
- 27 Sep since c16: l.2880-2913 R16-A1 read addendum; l.2914-2916 R16-A2 sent + forecast; l.2917-2926 USER E10 v3; l.2927-2932 USER class-C letter (b), pre-registered; l.2933-2936 USER Q1/Q2 yes; l.2937-2939 exp71 pushed; l.2940-2945 USER FREEZE lifted; l.2946-2951 aggressive mode (P45 exp70g); l.2952-2954 12:00 line.
- Not yet logged: ROUND 14-17 RECORDs, R17-A2..A11 (`research/wf_ideas_v4/round17/report.json`). The newest RESUME POINT (l.2599, 26 Sep 22:46) is stale.

## STATE IN 10 LINES

1. **Finals TICKED 2/2:** #37 K2 exp58 (56563521) = **0.954** and #38 twin exp58n (56563534) = **0.953**. API SELECTED was last read at 07:41:28Z. Sources: `CONTEXT.md` l.2872-2879; `DECISIONS.md` §2 [c17] l.475, snapshot l.482.
2. **LB #260 of 3,945** at 0.954 (11:01Z), 6th of 115 in the 0.954 block (ranks 255-369). Info only; the private LB (~71%) decides. amanatar V6 now shows 0.901. Sources: `experiments/e10_watch/20260927T1101Z.txt` l.930; `FACTS.md` F-LB-01/F-LB-04 [c17].
3. **Base** = x138 + safetail + lowrefine + gated DaughterNet insertion (K2). Best public files: #37, P40 exp70a and P42 exp70b (K2 + forkmid 4.5), all at 0.954. Sources: `experiments/lb_poll/poll.log` 12:01:34Z header; `FACTS.md` F-TRN-47.
4. **User decisions 11:08-11:16Z:** E10 v3: copy any public notebook >= 0.955 (verbatim, +SI, or port; autonomous submit); Class-C letter (b): a V*_C gives {V*_C, #37}, and #38 leaves; Q1/Q2 yes; Q3 (exp72 as a final) is open; FREEZE lifted; aggressive mode; Sources: `CONTEXT.md` l.2917-2951.
5. **Running now:** PENDING at the 12:01:34Z header: P43 exp70j DC 0.20 (56598763), P44 exp70k DC 0.225 (56598765) and P45 exp70g K2 + cap 6 (56606948, submitted 11:15:12Z); 43/44 are expected ~12:21-13:11Z (hard trigger 14:28:22Z, fallback 14:40Z). P45 is expected from ~17:56Z (9.0 h clock 20:15:12Z); Sources: `experiments/lb_poll/poll.log` l.14050; `FACTS.md` F-RUN-29 [c17]; `DECISIONS.md` §1 l.165-167.
6. **GPU:** exp71 (secondary fine-tune) has been RUNNING since 11:11:50Z; done ~15:15-15:45Z. exp72 is set for 28 Sep 00:05Z (public-only); exp70n (thr 0.3) dummy started 11:15Z. exp70q/r have NO dummy; GPU quota not re-read since 26 Sep ~21:5x; Sources: `CONTEXT.md` l.2937-2939, l.2946-2951; `FACTS.md` F-RUN-30; `WATCHLIST.md` I185.
7. **Slots 27 Sep:** 4 used, 1 left. It goes to exp70r (cap 6 + thr 0.3 + fm 4.5 + DC 0.20) if P43 reads >= 0.955 by ~13:00Z, else exp70q (same without the DC change). Lab and public evidence against it: cap-6 lab -0.00057 with 0 TP; thr 0.3 near-inert; V6 0.901. Sources: `CONTEXT.md` l.2946-2951; `FACTS.md` C-138, C-139, C-140, F-MOD-33, F-TRN-48.
8. **E10 v3 watcher NOT running:** there is no `experiments/e10_watch/watch_loop*.log`. `experiments/lb_poll/e10_watch_loop.py` (committed a6ffbc9) imports `take_snapshot`, which exists only in the uncommitted `tools/e10_snapshot.py`. Sources: `research/wf_ideas_v4/e10v3/build_watch.notes.md`; `WATCHLIST.md` W174.
9. **Next decision points:** Before the first 43/44 terminal header: R17-A3 last-slot line; ~12:21-14:40Z: 43/44 read (R17-A2) and one user line (re-tick text, R17-A3 facts, R17-A4 ask, Q3); ~13:00Z: last-slot submit. ~15:00Z: RESUME POINT (R17-A7); Before 17:50Z: P45 pre-score card (R17-A5); 28 Sep 00:05Z: exp72. 29 Sep 02:00Z: E10 v3 target. ~19:00Z: last read. 23:59Z: deadline; Sources: `WATCHLIST.md` NEXT 24 H l.73, LATER l.107.
10. **Ideas ledger:** 372 ideas (lb-tested 48, lab-tested 21, refuted 186, deferred 42, in-plan 73, open 2). The strict orphan is I-233. Sources: `IDEAS.md` CHANGES (17) l.80-89, ORPHANS l.585.

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` is this page. `CHANGES.md` holds the per-curation deltas (v4, 2-17).
- `IDEAS.md` + `ideas.json`: I-001..I-372 in 13 clusters. Line numbers: FINALS l.110, LADDER l.166, BASE l.201, RUN l.238, LOC l.277, DIV l.308, MODEL l.370, NODES l.414, INFER l.448, EF l.470, LINK l.490, VALID l.521, TESTSET l.567, ORPHANS l.585. The per-ID log is `ideas.json` meta.curations[n=17].
- `FACTS.md`: §1 metric l.155, §3 LB l.193, §4 runtime l.213, §5 rules l.248, §6 models l.271, §7 lab-to-LB l.309, CONTRADICTIONS l.362 (C-132..C-143 at l.497-508).
- `DECISIONS.md`: probes §1 l.115 (P43-P45 at l.165-167; built/planned table l.292); gates §1b l.303; finals §2 l.368 (c17 snapshot l.482); E10 §2f l.625 (v3 at l.736); OC §2g l.745; ladder/L9 §2h l.776; R1-R10 §3 l.814.
- `WATCHLIST.md`: OVERDUE l.61, NEXT 24 H l.73, LATER l.107, INSIGHTS l.140 (I172-I186). Curator logs are in `research/KNOWLEDGE/_curation/{v4,2,...,17}/`.

Key sources (repo root):
- `CONTEXT.md` is the source of truth; the anchors are listed above.
- LB: `experiments/RESULTS.md` (rows up to P38 only); `experiments/lb_poll/poll.log` and `ledger.md` (P39 onward); `experiments/e10_watch/20260927T1101Z.txt` (newest LB/E10 snapshot).
- Kernels: Finals: `experiments/exp58_x138_safe_lowref/` (#37), `experiments/exp58n_x138_safe_lowref/` (#38); Public rungs: `experiments/exp70{b_k2_fm45,g_k2_cap6,j_k2_dc020,k_k2_dc0225,n_k2_thr03,q_k2_maxdiv,r_k2_maxdiv_dc020}/probe.json`; 28 Sep levers: `experiments/exp73a_k2_dc015/` .. `experiments/exp73v_k2_i4_fm_dc015/`, `experiments/exp74_k2_secw_corwin/`, `experiments/exp75_k2_coordinject/`; Retrain: `experiments/exp71_secft_all/`.
- Tools: `tools/build_probe_kernel.py`, `tools/e10_port_gate.py`, `tools/e10_snapshot.py`, `tools/coordinject_patch.py`, `experiments/lb_poll/run_e10_watch_loop.sh`.
- Rounds: `research/wf_ideas_v4/round17/report.json` (R17-A0..A11; no REPORT.md yet); `research/wf_ideas_v4/bigger_levers/` (prep_div_combos, prep_corwin_secondary, prep_coord_refiner); `research/wf_ideas_v4/e10v3/` (build_watch, build_gate_verbatim, build_si_builder); `round16/`..`round8/`.
- Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `research/wf_ideas_v4/round9/LESSONS_draft.md`, `TEAM.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-344 / I-341 / I-342 | 43/44 read under letter (b) | V*_C -> re-tick text "untick 56563534, tick V*_C, keep 56563521" (the user re-ticks); else no change | `IDEAS.md` l.154, l.189-190 |
| I-361 / I-362 / I-360 | exp70q / exp70r last 27 Sep slot; exp70n thr 0.3 alone | Needs a dummy and the R17-A3 line first; exp70n has no slot | `IDEAS.md` l.194-196 |
| I-326 / I-365 | P45 exp70g (cap 6) scoring; pre-score card for 45/q/r/exp72/E10 v3 | Card before 17:50Z; >= 0.955 -> finals proposal with #37 | `IDEAS.md` l.184, l.161 |
| I-364 / I-287 / I-366 | E10 v3 (verbatim / +SI / port); slot-collision default | Commit tooling, start the loop; R17-A4 default needs the user's OK | `IDEAS.md` l.235, l.227, l.162 |
| I-119 / I-330 | exp71 -> exp72 FT secondary (28 Sep 00:05Z) | Public-only until Q3 = yes; G2 not running | `IDEAS.md` l.398 |
| I-363 / I-323 / I-324 | 28 Sep levers: 20 exp73 rungs, exp74 Corwin's secondary, exp75 coord-inject | Built, untracked, no CONTEXT entry; decision table + user row choice | `IDEAS.md` l.197, l.410, l.305 |
| I-354 | exp70b as the public-aimed final | User letter only; letter (b) did not name it; expiry ~18:00Z 29 Sep | `IDEAS.md` l.157 |
| I-336 / I-229 / I-367 | HINDSIGHT GUARD; tick checklist; override-budget lesson | Push the guard before 29 Sep 23:00Z; L9 read ~19:00Z | `IDEAS.md` l.557, l.132, l.561 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/17/{ideas,facts,watch}.json`)

1. [now] **The 12:00Z line is logged but incomplete.** It is at `CONTEXT.md` l.2952-2954 (a6ffbc9) and uses the corrected wording, not the R16-A3 template. It still lacks: the slot count (4 used, 1 left), the bracket check, the push status and the DEVIATION RECORD for exp71 and the post-FREEZE rungs. Add them to the next CONTEXT entry and save `round17/REPORT.md` (R17-A0). Sources: `research/wf_ideas_v4/round17/report.json` R17-A0, R17-A1; `FACTS.md` C-135; `WATCHLIST.md` W168, W169.
2. [now] **R17-A3 last-slot line before the first 43/44 terminal header** (the earliest is the 12:11Z header). It must give the mapping: exp70r if P43 >= 0.955, else exp70q. It must also state the facts: V6 = 0.901, cap-6 lab -0.00057 with 0 TP / 4 FP, thr 0.3 inert because the cap binds, exp70q stacks on the unread P45. Sources: `report.json` R17-A3; `FACTS.md` F-TRN-48, C-138, C-139; `IDEAS.md` I-361, I-362.
3. [now] **exp70q/r have no dummy, and both GPU lanes are busy.** exp71 is RUNNING and the exp70n dummy is queued, although exp70n has no slot today. A dummy takes ~25-29 min, so start one or cancel exp70n by ~12:15-12:30Z. Do not submit without a COMPLETE dummy; tell the user if it slips. Sources: `FACTS.md` F-RUN-30; `WATCHLIST.md` W171; `CONTEXT.md` l.2946-2951.
4. [today] **Read 43/44 with the pruned card** (R17-A2). Under letter (b), a V*_C gives the re-tick text from API SELECTED; if max <= 0.953, record it as a public read against more safe-division forks. Send one user line with: the read, the R17-A3 facts, the R17-A4 slot-collision ask, whether exp70n gets a slot, and Q3 for exp72. Sources: `report.json` R17-A2, R17-A4; `CONTEXT.md` l.2927-2932; `DECISIONS.md` §2 l.475.
5. [today] **Commit and start E10 v3.** Commit `tools/e10_snapshot.py`, the gate modes, the SI builder and `tests/test_e10_*.py` / `tests/test_si_builder.py`. Then start `experiments/lb_poll/run_e10_watch_loop.sh` in the background and confirm 2 good runs before 15:00Z. The SI token `exp73` collides with the exp73a..v folders. Sources: `research/wf_ideas_v4/e10v3/build_watch.json`, `build_si_builder.json`; `report.json` R17-A6; `IDEAS.md` I-364, I-288.
6. [today] **Log the untracked 28 Sep levers.** exp73a..v, exp74 (dataset upload not done; Corwin's own note gives -0.006 vs pilkwang) and exp75 need a CONTEXT decision table and pre-score lines (extend R17-A5). Present the row choice to the user with the V6 and cap-6 facts. I4 'ultra' is a cliff risk. Re-read the GPU quota before queueing dummies. Sources: `research/wf_ideas_v4/bigger_levers/prep_div_combos.notes.md`, `prep_corwin_secondary.notes.md`; `FACTS.md` F-MOD-32, C-142; `WATCHLIST.md` W181, I185.
7. [today] **Pre-score card and records.** Log the R17-A5 card for P45, exp70q/r, exp72 and E10 v3 copies before 17:50Z; By ~15:00Z, write the RESUME POINT plus restore card (R17-A7) and fix MEMORY.md; In the R17-A8 hygiene commit: ROUND 14-17 RECORDs, RESULTS rows P39-P45, NEVER_SUBMIT.md for exp70j/k, the v6 NOTES item 4 fix, and copying `fb_ins35.py` out of the scratchpad; Sources: `report.json` R17-A5, R17-A7, R17-A8; `FACTS.md` C-26, C-118; `WATCHLIST.md` W126, W173, W175, W176.
8. [before-finals / info] **Finals wording and corrected readings:** The partner of any new >= 0.955 file is #37, not #38 (C-137); 29 Sep 20:00Z is our own buffer, so read SELECTED after 23:59Z and never write 'FINALS FROZEN' (I-371); Session timers fire only while the REPL is idle; Cite exp70n with its knob, 'thr 0.3', because I-333 used the name for a different knob; The round prompt `experiments/workflows/biohub-research-round.js` is stale (W150); Sources: `FACTS.md` C-137; `WATCHLIST.md` I179, I181; `IDEAS.md` I-333, I-360.

**RESOLVED since curation 16:**
- R16-A1 addendum logged, with R16-A2 sent at 09:15Z (289bd52, 06f1a02).
- User letters, all at `CONTEXT.md` l.2917-2951: E10 v2 superseded by v3; class-C letter (b) pre-registered; Q1/Q2 answered; FREEZE lifted.
- exp71 pushed 11:11:50Z; P45 submitted.
- 12:00Z line logged (a6ffbc9, partial, see alert 1).

## HOW TO USE

- "Score of probe N, what changed?" -> `DECISIONS.md` §1, `experiments/RESULTS.md` (up to P38), `experiments/lb_poll/poll.log` / `ledger.md` (P39 onward), `experiments/<exp>/probe.json`.
- "43/44/45 scored, what are the finals?" -> `CONTEXT.md` l.2927-2932 (letter (b)), l.2940-2945 (new >= 0.955 file -> proposal with #37), l.2814-2871; `DECISIONS.md` §2 l.482; R17-A2/A5 in `research/wf_ideas_v4/round17/report.json`.
- "What goes in the next slot?" -> `CONTEXT.md` l.2946-2951; `DECISIONS.md` §1 built/planned table l.292; `research/wf_ideas_v4/bigger_levers/prep_div_combos.json`.
- "Did a public notebook beat us (E10 v3)?" -> `CONTEXT.md` l.2917-2926; `DECISIONS.md` §2f l.736; newest `experiments/e10_watch/` snapshot; `research/wf_ideas_v4/e10v3/`.
- "Can exp72 be submitted or be a final?" -> `CONTEXT.md` l.2933-2939, l.2722-2746; `IDEAS.md` I-119/I-330.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5 and CONTRADICTIONS; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md`. "What is next or overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~12:05Z 27 Sep: the tail of `CONTEXT.md` §14 (above `## 9.`), `poll.log`, and the newest `research/wf_ideas_v4/round*/`.
