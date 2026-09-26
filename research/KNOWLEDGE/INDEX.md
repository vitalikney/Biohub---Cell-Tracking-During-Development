# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 9: state as of 2026-09-26 ~13:25 UTC, git HEAD 69d6be2 (local main = origin/main, `git status -sb`), plus the untracked `research/wf_ideas_v4/round9/` and `experiments/exp64_overlap_lab/results_info_post_stop.md`. Previous: curation 8 (~11:10 UTC, 24dcdea). Hashes cited before curation 8 are pre-rewrite; map them with `experiments/git_rewrite_map_2026-09-26.txt`. All times UTC; every line cites its source.
Deadline 29 Sep 23:59; finals are ticked MANUALLY by 29 Sep 20:00. Sources: `CONTEXT.md` §1; PRE-REG v3 l.1576-1736; OC gates l.2110-2128; E10 PORT RULE l.2138-2147; RESUME POINT (stale) l.2148-2152; ticks l.2154-2156; rewrites l.2161-2176; OC STOP l.2177-2186; R9 amendment l.2187-2197; exp64 post-stop l.2198-2204; `## 9. Literature` l.2205.

## STATE IN 10 LINES

1. **Finals TICKED 2/2** = #37 K2 exp58 (56563521) = **0.954** + #38 twin exp58n (56563534) = **0.953**, both R5(a). API SELECTED checks logged at 09:10:07Z, 10:45:26Z and 13:00:41Z. No "11:42" check exists in any log (C-71). Sources: `CONTEXT.md` l.2154-2156; `experiments/RESULTS.md` l.70-71; `research/wf_ideas_v4/round9/report.notes.md`; `FACTS.md` C-71.
2. **Rank #204 of 3,928 at 12:46Z** (0.954 block 192-284). We are now 8 ranks BELOW the ~196 public silver line. Info only (R7); the private LB (~71%) decides. No submission since 00:02:18Z. Sources: `research/wf_ideas_v4/round9/scan_browser.json` r9-lb-delta-1246; `FACTS.md` F-LB-02, F-LB-03.
3. **Base** = x138 + safetail (C01) + lowrefine + gated DaughterNet insertion (K2). Lab-to-public transfer is ~1/6 of the lab size, so R4's +0.002 needs ~+0.012 in the lab. Round 9 found no honest mechanism for the R8 cutoff. Sources: `IDEAS.md` I-001, I-062; `research/wf_ideas_v4/round9/scan_hypotheses.json` r9h-2.
4. **Overlap consensus (OC) is CLOSED.** G-A failed at 10:52 (43/62 pairs). The R9 amendment was recorded at 11:06. The post-stop exp64 G-B on the real K2 stack gave **-0.00143** (bootstrap lower -0.00200): the splice hurts. The idea is post-deadline only, and only with a new design. Sources: `CONTEXT.md` l.2177-2204; `experiments/exp64_overlap_lab/results_info_post_stop.md`; `DECISIONS.md` §2g, G31; `IDEAS.md` I-208, I-270, I-274.
5. **E10 PORT RULE P1-P8 is in force** (since 09:10) and is now the only active line. It was not triggered at 12:47Z or 13:00:51Z. P4b (never push the author's public, internet-on metadata) is proposed but not in CONTEXT. Sources: `CONTEXT.md` l.2138-2147, l.2157-2158; `research/wf_ideas_v4/round9/report.json` R9-A3, R9-A9; `DECISIONS.md` §2f; `IDEAS.md` I-026, I-279.
6. **Running now:** poller PID 20052 (last header 13:15:25Z). No workflow is scoring anything, and no submission is pending; the 26 Sep slots stay empty. Round 9 ran 12:46-13:10Z; it is untracked and has no REPORT.md. Sources: `experiments/lb_poll/poll.log`; `research/wf_ideas_v4/round9/report.json`; `WATCHLIST.md` l.3-10.
7. **Git:** main was rewritten at 10:15. Old-history worktree branches (wf_b39793f6-e79-*) come in by cherry-pick only. The 6 OC commits (9c85782 aa5b834 ff438f7 9826517 a012e32 1986fb9) are NOT in main, yet CONTEXT 13:11 cites `tools/overlap_lab.py`. Sources: `CONTEXT.md` l.2167-2176, l.2200; `research/wf_ideas_v4/round9/scan_plancheck.json` PC9-04; `IDEAS.md` I-275.
8. **Round-9 rechecks:** I-276 (GT-noise mimicry) is refuted. I-222 (retention guard) is deferred: the effective secondary weight is 0.80, and the fallback is embryo-dependent (44b6 33.1% vs 6bba 3.9% of frames). The link family I-177/179/180 are real -0.002 reads. Division loss = missing forks + isolated false forks. Sources: `FACTS.md` F-TRN-33..35, C-68; `DECISIONS.md` G32, G33.
9. **Next decision points:** Resume hygiene and P4b, before round 10 (~15:30Z). E10 P1 check (~15:30Z, at the latest ~19:00Z), then every ~6 h to 29 Sep 00:00. M6 lapses 26 Sep 18:00; after ~22:00Z no idea can become a final. Slot reset 27 Sep 00:00; R8 cutoff 27 Sep 12:00; last port submit 29 Sep 02:00. Tick checks: 28 Sep evening, 29 Sep 12:00 + 18:00. Ticks are final at 29 Sep 20:00. Sources: `WATCHLIST.md` NEXT 24 H l.50, LATER l.74; `research/wf_ideas_v4/round9/report.json` next_focus.
10. **Ideas ledger:** 279 ideas (lb-tested 41, lab-tested 21, refuted 159, deferred 26, in-plan 31, open 1). Strict orphan: I-233. At risk: I-229, I-232, I-243, I-257, I-262, I-275, I-279. Source: `IDEAS.md` l.9, l.11, ORPHANS l.410.

## WHERE THINGS ARE

The knowledge base (`research/KNOWLEDGE/`) is written only by the curator workflow `experiments/workflows/biohub-curator.js`:
- `research/KNOWLEDGE/INDEX.md`: this page. `research/KNOWLEDGE/CHANGES.md`: what changed in each curation (v4, 2-9).
- `research/KNOWLEDGE/IDEAS.md` + `research/KNOWLEDGE/ideas.json`: ideas I-001..I-279 in 12 clusters (FINALS l.36, BASE l.73 ... TESTSET l.392); delta at l.11; ORPHANS at l.410. Per-ID change log: `ideas.json` meta.curations.
- `research/KNOWLEDGE/FACTS.md`: §1 metric (l.48) through §7 lab-to-LB transfer (l.172); CONTRADICTIONS at l.212 (C-68..C-71 are new).
- `research/KNOWLEDGE/DECISIONS.md`: probes P01-P38 (§1 l.35); lab gates G01-G33 (§1b l.142); finals (§2 l.197); READ TABLE v1-v4 (§2b-§2e); E10 PORT RULE + P4b (§2f l.361); OC line, CLOSED (§2g l.398); R1-R10 (§3 l.424).
- `research/KNOWLEDGE/WATCHLIST.md`: OVERDUE l.38, NEXT 24 H l.50, LATER l.74, INSIGHTS AT RISK l.103 (I74-I84 are new).
- Curator logs: `research/KNOWLEDGE/_curation/{v4,2,3,4,5,6,7,8,9}/`.

Key sources (repo root):
- `CONTEXT.md` is the single source of truth. The newest §14 entry ends at l.2204, just above `## 9. Literature` (l.2205). Two dated entries still sit below it (l.2207-2225, C-64). The newest RESUME POINT (l.2148) is stale (C-62).
- LB records: `experiments/RESULTS.md` (every LB probe); `experiments/lb_poll/poll.log` (10-min poll); `experiments/lb_poll/ledger.md` (latency bounds, R5).
- Finals kernels: `experiments/exp58_x138_safe_lowref/` (#37) and `experiments/exp58n_x138_safe_lowref/` (#38). `experiments/*/probe.json` says what each kernel changed.
- Labs: `experiments/exp60_trainlab/results.md` (x138 lab); `experiments/exp64_overlap_lab/` (OC G-B, INFO only); `experiments/runtime_step0/` (bound on the hidden-test N).
- E10 material: `experiments/ext_y3uanm-secondary-ft/` (pulled author metadata, the P4b trap), `experiments/ext_*/NOTES.md`.
- Tools: `tools/build_probe_kernel.py`: builds the probe kernels. `tools/runtime_ledger.py`: runtime forecasts. It has no exp63 rule (l.23, l.69-74). `tools/official/src/tracking_cellmot/metrics.py`: the official metric.
- Research rounds: `research/wf_ideas_v4/round9/` (untracked; `report.json` R9-A0..A9; LESSONS draft in `scan_hypotheses.json` r9h-5). `research/wf_ideas_v4/round8/report.json`. `research/wf_ideas_v4/round{3..7}/REPORT.md`. The round prompt: `experiments/workflows/biohub-research-round.js`.
- Background: `research/wf_ideas_v3/FINAL_REPORT.md` (pre-registration); `research/wf_ideas_v2/r2_research_overlap-consensus.json` (OC design).
- Team and intel: `PROMPT_FRIEND_A.md` (stale tasks), `PROMPT_FRIEND_C.md`, `TEAM.md`; `research/browser_research_2026-09-24*.md`; `research/discussions_summary.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-279 | E10 PORT RULE P4b: private, internet off, no id_no, scored version == pulled version | in-plan, at risk: put the R9-A3 text in CONTEXT before ~15:30Z | `IDEAS.md` l.94 |
| I-243 | runtime_ledger: rule exp63 -> x138, docstring fix, one test | at risk: R9-A4 before any E10 trigger | `IDEAS.md` l.127 |
| I-257 | New RESUME POINT, move the 2 stray entries, MEMORY approval line | at risk: R9-A1 has the ready text | `IDEAS.md` l.67 |
| I-275 | Cherry-pick the 6 OC commits (no merge); grep claude = 0; K2 sha unchanged | at risk: before any worktree is removed | `IDEAS.md` l.389 |
| I-232 | Save round8/ + round9/ REPORT.md from R8-A0/R9-A0; commit round9/ | at risk | `IDEAS.md` l.383 |
| I-229 / I-258 | Tick checklist and API SELECTED re-checks; 29 Sep reminders | in-plan: re-check 28 Sep evening, 29 Sep 12:00 + 18:00; reminders unconfirmed | `IDEAS.md` l.58, l.68 |
| I-265 / I-252 | Light mode vs full rounds; LESSONS draft (r9h-5) | in-plan (a user question) / deferred: save LESSONS_draft.md by 27 Sep 12:00 | `IDEAS.md` l.387, l.385 |
| I-262 / I-233 | E10 dry run (fold into I-279); poller error_description | at risk / strict orphan: close with one line | `IDEAS.md` l.92, l.121 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/9/{ideas,facts,watch}.json`)

1. [now] **Resume hygiene (W80 = R9-A1), flagged twice:** Write a new RESUME POINT: finals 2/2 with the 3 logged API checks, OC stopped, E10 the only active line. Move the 2 entries at l.2207-2225 above `## 9.` Replace the MEMORY.md "LB probe approval" line. Its "Resume point" line is already right (C-26). Never write "11:42". Sources: `CONTEXT.md` l.2148-2152; `research/wf_ideas_v4/round9/report.json` R9-A1; `WATCHLIST.md` W80; `FACTS.md` C-26, C-62, C-64, C-71.
2. [now, before ~15:30Z] **E10 port traps.** Fix both before the next trigger check: Pulled author metadata is public, has internet ON and an id_no. The CLI pulls only the latest version. Fix: put P4b into CONTEXT (R9-A3). `tools/runtime_ledger.py` has no exp63 rule, and its docstring maps exp63 to safetail. A port running 7.5-9.5 h would be wrongly admitted. Fix: R9-A4 plus a test. Sources: `research/wf_ideas_v4/round9/scan_plancheck.json` PC9-02, PC9-03; `WATCHLIST.md` W87, W88, I74, I75.
3. [today] **OC evidence exists only on worktree branches.** Cherry-pick 9c85782 aa5b834 ff438f7 9826517 a012e32 1986fb9 in order and never merge. Check that grep -ci claude = 0, pytest passes and the K2 sha is 1f1ddb6d. Add the line "exp65/exp66 never push or submit". Commit as the user with NO Co-Authored-By trailer (memory rule `feedback-git-no-coauthor.md`). Sources: `research/wf_ideas_v4/round9/report.json` R9-A5; `WATCHLIST.md` W83, W93.
4. [today] **Round artefacts unsaved.** round8/REPORT.md and round9/REPORT.md do not exist (the harness refused both writes). round9/ and the exp64 `results_info_post_stop.md` are untracked. Sources: `research/wf_ideas_v4/round9/report.json` R9-A0; `WATCHLIST.md` W86, W05.
5. [today] **One user message (R9-A8).** Ask about light mode vs full rounds, and ask the user to set their own reminders for 29 Sep 12:00/18:00. The laptop runs ticks, E10 and the poller (sleep = never; restarts not covered). Log the replies with `date -u`. Sources: `research/wf_ideas_v4/round9/report.json` R9-A8; `research/wf_ideas_v4/round9/scan_plancheck.json` PC9-06; `WATCHLIST.md` W92.
6. [today] **Missed curator records (due 12:00):** CONTEXT l.22 still says "GT still moving". B5 at l.196. out_valid / efpost. The R9-A6 facts (weight 0.80, 1/6 transfer, division anatomy). The round prompt still says "241-team block" (l.20; ~330 now) and "~4 h headroom" (l.36). Sources: `WATCHLIST.md` W90, W71; `experiments/workflows/biohub-research-round.js`.
7. [before-finals] **Lessons draft (r9h-5)** exists only in an untracked scan. Save it as `research/wf_ideas_v4/round9/LESSONS_draft.md`, with "241+" changed to "~330" and a caveat that "public = one embryo" is a guess (C-69). Sources: `research/wf_ideas_v4/round9/report.json` R9-A7; `WATCHLIST.md` W91, T30.
8. [before-finals] **Tick re-checks and poller:** Tick re-checks: 28 Sep evening, 29 Sep 12:00 + 18:00. Before any submit, the last poll must be < 15 min old. Keep the poller until 29 Sep 20:00. Sources: `DECISIONS.md` §2; `WATCHLIST.md` LATER l.74.
9. [info] Quote the secondary weight as 0.80, not 0.475, and drop the "47%" figure (C-68). The stale MEMORY index copy injected into subagents still says "25 Sep batch approved": only E10 has a submit OK (I82). Friend A card: W03. Close I-233 with one line. Sources: `FACTS.md` C-68; `WATCHLIST.md` I82, W03; `IDEAS.md` ORPHANS l.410.

## HOW TO USE

- "Score of probe N, what it changed, why it was dropped?" -> `DECISIONS.md` §1, then `experiments/RESULTS.md` and `experiments/<exp>/probe.json`.
- "Which files are the finals, and what if a new public kernel appears?" -> `DECISIONS.md` §2 and §2f, then `CONTEXT.md` l.2138-2158 and `research/wf_ideas_v4/round9/report.json` R9-A3.
- "Why did overlap consensus stop, and is it really dead?" -> `DECISIONS.md` §2g + G31, `FACTS.md` C-59/C-70, then `CONTEXT.md` l.2177-2204.
- "Which lab gate closed a rider?" -> `DECISIONS.md` §1b (G01-G33), then `experiments/exp60_trainlab/results.md`.
- "Which rule decides this, and is it Kaggle's or ours?" -> `DECISIONS.md` §3; `FACTS.md` §5; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> search its alias in `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md` and its CONTRADICTIONS.
- "An old commit hash does not resolve" -> `experiments/git_rewrite_map_2026-09-26.txt`.
- "What is next, overdue or at risk?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`. For anything newer than ~13:25Z 26 Sep -> the tail of `CONTEXT.md` §14 and `experiments/lb_poll/poll.log`.
