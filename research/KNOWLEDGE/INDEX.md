# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 11: state as of 2026-09-26 ~17:50 UTC, git HEAD df6996e, plus the untracked `research/wf_ideas_v4/round11/` (report.json 17:31Z, R11-A0..A9 NOT yet applied) and `experiments/e10_watch/20260926T1701Z*.txt`. Previous: curation 10 (~15:55 UTC, 6064d85). Hashes from before 26 Sep 10:15 are pre-rewrite: `experiments/git_rewrite_map_2026-09-26.txt`. All times UTC; every line cites its source.
Deadline 29 Sep 23:59; finals ticked MANUALLY by 29 Sep 20:00. `CONTEXT.md` anchors: PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147 (in force), P4b l.2217, P4c l.2257-2279 (+ P4c(3) fix l.2301-2317); RESUME POINT 13:27 l.2205-2212 (current); ROUND 10 RECORD 16:04 l.2230-2256; snapshots + post-R8 check times l.2280-2287; PRIVATE-READ PREDICTIONS l.2288-2300; USER full rounds 16:49 l.2318-2323; PRIVATE RANK FORECAST 16:54 l.2324-2334; USER OK successor PLAN 17:00 l.2335-2341; `## 9. Literature` l.2342.

## STATE IN 10 LINES

1. **Finals TICKED 2/2**: #37 K2 exp58 (56563521) = **0.954**, #38 twin exp58n (56563534) = **0.953**; API SELECTED last checked 17:09Z. No submission since 00:02:18Z. Sources: `experiments/RESULTS.md` l.70-71; `IDEAS.md` I-258; `FACTS.md` F-LB-10 [c11].
2. **Rank #210 of 3,929** ranked teams at 17:01Z (12th of 97 at 0.954; ~13 below public silver). Info only (R7); private LB (~71%) decides. Sources: `experiments/e10_watch/20260926T1701Z.txt` l.792ff; `FACTS.md` F-LB-02, C-79.
3. **Base** = x138 + safetail + lowrefine + gated DaughterNet insertion (K2); rebuild byte-identical; 275 tests pass after bea9d99. Sources: `CONTEXT.md` l.2220-2229; `IDEAS.md` I-001, I-281.
4. **E10 in force: port only at a successor's own public >= 0.956**, now with P4c and read-only gate `tools/e10_port_gate.py` (72 tests; x138 + exp56 PASS, amanatar v10 FAIL) and `tools/e10_snapshot.py`. **Not met** at 16:20Z / 17:01Z (amanatar v10 ERROR; anhadmahajan06 BioTrack-Omni 0.946 fails P4c(2)). Sources: `CONTEXT.md` l.2257-2317; `IDEAS.md` I-026, I-292; `DECISIONS.md` §2f.
5. **Successor gap (round 11):** a clean 0.954-0.955 x138-family successor is NOT covered but is the larger medal risk. **E10 v2 PORT-ONLY** (>= 0.954, pair {PORT, #37}, <= 2 ports, 3-hourly checks, last submit 29 Sep 02:00) is PROPOSED, needs one user OK before 27 Sep 12:00. The 17:00 "хорошо" covered only the analysis PLAN. Sources: `research/wf_ideas_v4/round11/report.json` R11-A2; `CONTEXT.md` l.2335-2341; `IDEAS.md` I-286; `DECISIONS.md` §2f l.484.
6. **SI (successor + our insertion) is NOT the default:** an early verbatim port is at least as good for bronze (P 0.84/0.89/0.93 vs 0.80/0.83/0.87); SI only on user opt-in by ~09:00 27 Sep. This corrects the earlier chat claim. Sources: `research/wf_ideas_v4/round11/report.json` R11-A3, rejected; `FACTS.md` C-81, F-MOD-24; `IDEAS.md` I-287.
7. **Running now:** poller (last header 17:46:15Z, `experiments/lb_poll/poll.log` l.7460). Nothing scoring. Round 11 ran ~17:05-17:31Z; untracked, REPORT.md refused again (text in R11-A0). No session timers exist yet. Sources: `research/wf_ideas_v4/round11/report.notes.md`; `WATCHLIST.md` W103, W107.
8. **Round-11 closures (lab, no LB):** I-047 refuted by measurement (-0.0129/-0.0273), I-293 raw-maxima arm (ceiling +0.0059), I-294 division-wave prior; nothing reaches the R8 bar. Sources: `DECISIONS.md` G36, G37 (l.213-214); `FACTS.md` F-TRN-37; `IDEAS.md` l.9.
9. **Next decision points:** round 12 ~19:45Z; user message R11-A9 now (E10 v2 OK, wake mechanism, SI); next E10 P1 check by 23:00; HF v3 dry run by 27 Sep 06:00; SI opt-in ~09:00; **R8 cutoff + E10 v2 OK deadline 27 Sep 12:00**; last port submit 29 Sep 02:00; tick checks 28 Sep 18:00, 29 Sep 12:00/18:00; ticks final 20:00. Sources: `WATCHLIST.md` NEXT 24 H l.64, LATER l.94; `research/wf_ideas_v4/round11/report.json` R11-A4, R11-A8.
10. **Ideas ledger:** 294 ideas (lb-tested 41, lab-tested 21, refuted 166, deferred 27, in-plan 38, open 1). Strict orphan I-233; at risk I-229, I-232, I-262, I-282, I-286, I-290. Source: `IDEAS.md` l.11, ORPHANS l.434.

## WHERE THINGS ARE

Knowledge base `research/KNOWLEDGE/` (written only by `experiments/workflows/biohub-curator.js`):
- `INDEX.md` (this page); `CHANGES.md` (per-curation deltas v4, 2-11).
- `IDEAS.md` + `ideas.json`: I-001..I-294 in 12 clusters (FINALS l.45, BASE l.83, RUN l.117, LOC l.154, DIV l.184, MODEL l.239, NODES l.280, INFER l.312, EF l.332, LINK l.352, VALID l.382, TESTSET l.416, ORPHANS l.434); curation delta l.13; per-ID changes in `ideas.json` meta.curations.
- `FACTS.md`: §1 metric l.69 ... §7 lab-to-LB l.199; CONTRADICTIONS l.241 (C-79..C-83 new, l.323-327).
- `DECISIONS.md`: probes §1 l.51; lab gates G01-G37 §1b l.171; finals §2 l.230 (CURRENT snapshot l.289); READ TABLE §2b-§2e; E10 + P4c + E10 v2 PROPOSED §2f l.426; OC CLOSED §2g l.502; R1-R10 §3 l.533.
- `WATCHLIST.md`: OVERDUE l.54, NEXT 24 H l.64 (W103-W112), LATER l.94 (T36-T39), INSIGHTS l.130 (I96-I106).
- Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,11}/`.

Key sources (repo root):
- `CONTEXT.md`: single source of truth; newest §14 entry l.2335-2341 (17:00Z), above `## 9. Literature` l.2342.
- LB: `experiments/RESULTS.md` (every probe); `experiments/lb_poll/poll.log`, `experiments/lb_poll/ledger.md` (both uncommitted); `experiments/e10_watch/<UTC>.txt` (P1 snapshots; `20260926T1701Z-2.txt` is a duplicate to delete).
- Finals kernels: `experiments/exp58_x138_safe_lowref/` (#37), `experiments/exp58n_x138_safe_lowref/` (#38); `experiments/*/probe.json`.
- Tools: `tools/e10_port_gate.py` (read-only port gate), `tools/e10_snapshot.py` (P1 snapshot; P2_MIN 0.956 at l.52), `tools/build_probe_kernel.py`, `tools/runtime_ledger.py` (exp63 -> x138 l.71), `tools/dummy_gates.py`, `tools/official/src/tracking_cellmot/metrics.py`.
- Labs: `experiments/exp60_trainlab/results.md`; `experiments/runtime_step0/`; `experiments/ext_*/NOTES.md`.
- Rounds: `research/wf_ideas_v4/round11/` (untracked: `report.json` R11-A0..A9, `scan_*.json`, `v_*.json`); `round10/`, `round9/` (REPORT.md, `LESSONS_draft.md`), `round8/`; prompt `experiments/workflows/biohub-research-round.js`.
- Background: `research/wf_ideas_v3/FINAL_REPORT.md`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`, `PROMPT_FRIEND_A.md` (stale), `PROMPT_FRIEND_C.md`, `TEAM.md`, `research/discussions_summary.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-286 | E10 v2 PORT-ONLY: >= 0.954, pair {PORT, #37}, <= 2 ports, 3-hourly checks | In-plan, at risk. Append as PROPOSED; one user OK before 27 Sep 12:00 | `IDEAS.md` l.108 |
| I-290 | Precedence for public successors: P6 > f2 > R4 | In-plan, at risk. In ROUND 11 RECORD; superseded by E10 v2 V6 if OK'd | `IDEAS.md` l.112 |
| I-282 | e10_watch snapshots + post-R8 schedule + wake mechanism | Partly done; create R11-A4 timers now, log ids; wake answer pending | `IDEAS.md` l.107 |
| I-262 | E10 dry run on HF v3 (never submit), time trigger-to-submit | In-plan, at risk. Before 27 Sep 06:00 | `IDEAS.md` l.102 |
| I-232 | Save round11/REPORT.md from R11-A0; commit round11/ | At risk. In the R11-A1 commit | `IDEAS.md` l.405 |
| I-229 / I-258 | Tick checklist; API SELECTED re-checks 28 Sep eve, 29 Sep 12:00/18:00 | In-plan; user's own reminders unconfirmed | `IDEAS.md` l.67, l.77 |
| I-287 | SI = successor + our insertion (exp67) | Not adopted; opt-in only by ~09:00 27 Sep | `IDEAS.md` l.109 |
| I-252 / I-233 | LESSONS s4 lines (R11-A7); poller error_description | Deferred, by 27 Sep 12:00 / strict orphan: close with one line | `IDEAS.md` l.407, l.141 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/11/{ideas,facts,watch}.json`)

1. [now] **E10 v2 needs one user OK** (logged with `date -u`, before 27 Sep 12:00 and before any trigger). Append E10_V2_TEXT as PROPOSED, then send R11-A9 once. Without an OK, the 0.954-0.955 risk is accepted by default. Sources: `research/wf_ideas_v4/round11/report.json` R11-A2, R11-A9; `WATCHLIST.md` W105, W112; `FACTS.md` C-80.
2. [now] **Correct the chat claim that SI is stronger** inside R11-A9; build no SI unless the user opts in by ~09:00 27 Sep. Sources: `report.json` R11-A3, rejected; `FACTS.md` C-81; `WATCHLIST.md` W106.
3. [now] **Detection gap under E10 v2:** `tools/e10_snapshot.py` flags only at 0.956 and counts teams, not notebook scores; add a browser score read of every new x138-family kernel to the timer steps and the E10 v2 text. Sources: `tools/e10_snapshot.py` l.52; `WATCHLIST.md` I96.
4. [now] **Session timers (R11-A4)**: 3-hourly P1 checks 27 Sep 12:00 -> 29 Sep 00:00, tick checks 28 Sep 18:00 and 29 Sep 12:00/18:00; log ids in CONTEXT. Wake question asked twice (16:04, 16:49) unanswered; re-ask in R11-A9. Sources: `report.json` R11-A4, R11-A5; `CONTEXT.md` l.2285-2287, l.2321-2323; `FACTS.md` C-82.
5. [now, before round 12] **Hygiene commit R11-A0/A1** as the user, no Co-Authored-By trailer (memory rule `feedback-git-no-coauthor.md`): ROUND 11 RECORD (incl. precedence I-290, closures I-047/I-049/I-122/I-139/I-278/I-293/I-294, RESUME slot fix 3/5/5/5), round11/REPORT.md, poll.log, ledger.md, 20260926T1701Z.txt; delete the -2 duplicate. pytest green, finals sha unchanged, claude grep 0. Sources: `report.json` R11-A0, R11-A1; `WATCHLIST.md` W103, W104.
6. [today, by 27 Sep 06:00] **HF v3 E10 dry run** (private dummy + NEVER_SUBMIT.md), record each step's wall time; any gate FAIL is a procedure finding. Sources: `report.json` R11-A6; `WATCHLIST.md` W109, T37.
7. [today] **Next E10 P1 check by 23:00** (browser agent only, one snapshot per round) and fix round prompt l.37-40 ('~4 h headroom', duplicate snapshot runs). Sources: `report.json` R11-A8; `experiments/workflows/biohub-research-round.js`; `WATCHLIST.md` W111, W71.
8. [before-finals, by 27 Sep 12:00] **Curator records and LESSONS:** R11-A7 lines to LESSONS s4; I69 caveat at `research/wf_ideas_v4/round9/LESSONS_draft.md` l.7; overdue CONTEXT l.22, l.196, out_valid, efpost, 33.1%; friend A card. Sources: `WATCHLIST.md` OVERDUE l.54, W110.
9. [info] 16:54 rank forecast is calibration-only (0.953 block median SubmissionCount 25); DaughterNet weight load is outside the fail-soft, so keep W102 finals-input protection; stale MEMORY index copy (C-75); team count 3,929 (C-79); close I-233. Sources: `CONTEXT.md` l.2324-2334; `WATCHLIST.md` I97-I106; `FACTS.md` C-75, C-79.

## HOW TO USE

- "Score of probe N, what changed, why dropped?" -> `DECISIONS.md` §1, `experiments/RESULTS.md`, `experiments/<exp>/probe.json`.
- "What if a public successor appears (0.954-0.955 or >= 0.956)?" -> `DECISIONS.md` §2f (E10 + E10 v2 PROPOSED), `CONTEXT.md` l.2138-2147, l.2257-2317, l.2335-2341, `research/wf_ideas_v4/round11/report.json` R11-A2/A3, `IDEAS.md` I-286/I-287/I-290.
- "Which lab gate closed a rider?" -> `DECISIONS.md` §1b (G01-G37), `experiments/exp60_trainlab/results.md`.
- "Which rule decides this?" -> `DECISIONS.md` §3; `FACTS.md` §5; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> search its mechanism/alias in `IDEAS.md` or `ideas.json`. "Is claim X true?" -> `FACTS.md` + CONTRADICTIONS.
- "Old hash does not resolve" -> `experiments/git_rewrite_map_2026-09-26.txt`.
- "What is next / overdue?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- Anything newer than ~17:50Z 26 Sep -> tail of `CONTEXT.md` §14 (above `## 9.`), `experiments/lb_poll/poll.log`, `experiments/e10_watch/`, newest `research/wf_ideas_v4/round*/`.
