# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 8: state as of 2026-09-26 ~11:10 UTC, git HEAD 24dcdea on the REWRITTEN main (local = origin/main at ~11:08Z, `git status -sb`), plus the untracked `research/wf_ideas_v4/round8/`. Previous: curation 7 (~09:05 UTC, 42d1a55 pre-rewrite). Hashes cited before curation 8 are pre-rewrite; map them with `experiments/git_rewrite_map_2026-09-26.txt`. All times UTC; every line cites its source.
Deadline 29 Sep 23:59; finals are ticked MANUALLY by 29 Sep 20:00. Sources: `CONTEXT.md` §1; PRE-REG v3 l.1576-1736; rules check l.2096-2109; OC gates l.2110-2128; E10 PORT RULE l.2138-2147; RESUME POINT l.2148-2152; ticks l.2154-2156; history rewrites l.2161-2176; OC STOP l.2177-2186; `## 9. Literature` l.2187.

## STATE IN 10 LINES

1. **Finals TICKED 2/2** = #37 K2 exp58 (56563521) = **0.954** + #38 twin exp58n (56563534) = **0.953**, both R5(a). API SELECTED check at 09:10:07Z, still 2/2 at 10:45Z. Sources: `CONTEXT.md` l.2154-2156; `experiments/RESULTS.md` l.70-71; `research/wf_ideas_v4/round8/report.notes.md`; `DECISIONS.md` §2.
2. **Rank #188 of 3,924 at 10:17Z.** The silver line (~196) is only 7-8 ranks below us, down from 13. Info only (R7); the private LB (~71%) decides. Sources: `research/wf_ideas_v4/round8/scan_browser.json` r8-lb-delta-1017; `FACTS.md` F-LB-02, F-LB-03.
3. **Base** = x138 + safetail (C01) + lowrefine + gated DaughterNet insertion (K2). Insertion transferred to the LB again (+0.001); lowrefine and C01 do not show at 3 decimals. Sources: `IDEAS.md` I-001, I-062, I-036; `FACTS.md` §7.
4. **Overlap-consensus line (OC, K6) STOPPED at 10:52 by its own gate G-A:** 43 of 62 GT-linked 44b6 pairs found vs >= 60 needed, 0 wrong offsets; proxy lab -0.00047. No G-P bit-probe and no K6 were submitted. Sources: `CONTEXT.md` l.2177-2186; `FACTS.md` F-TRN-30, C-59; `DECISIONS.md` §2g; `IDEAS.md` I-208, I-266..I-273.
5. **E10 PORT RULE P1-P8 IN FORCE** since the user's conditional yes at 09:10. Trigger not met at 10:17-10:23Z; next CLI check ~16:30Z. Sources: `CONTEXT.md` l.2138-2147, l.2157-2158; `DECISIONS.md` §2f; `WATCHLIST.md` W23.
6. **Running now:** exp64 x138 G-B lab kernels a/b (RUNNING at 10:44Z; result = INFO only); the round-8 judge (only `report.notes.md` 10:46Z so far); poller PID 20052 (last header 10:55:02Z). No submission pending; the 3 slots for 26 Sep stay empty. Sources: `research/wf_ideas_v4/round8/report.notes.md`; `experiments/lb_poll/poll.log` l.4959; `WATCHLIST.md` W82, T17.
7. **Git:** main rewritten and force-pushed at 10:15 (Claude authorship removed). Worktree branches wf_b39793f6-e79-* are on the OLD history: cherry-pick only, never merge. Friend A must reset to origin/main. Sources: `CONTEXT.md` l.2167-2176; `FACTS.md` C-63; `IDEAS.md` I-275.
8. **Round-8 rechecks:** constant z shift +0.0016 in-sample, ~+0.0003 expected on new embryos -> deferred (I-029); split-aware relink reaches only 7 of 62 missed divisions -> deferred (I-079); DivNet parent veto stays closed (I-058). Sources: `research/wf_ideas_v4/round8/scan_recheck.json`; `FACTS.md` F-TRN-31/32.
9. **Next decision points:** records by 12:00; exp64 INFO read ~11:30-12:15Z; round 9 ~13:30Z; M6 lapse 18:00; after ~22:00Z no round idea can become a final; slot reset 27 Sep 00:00; R8 cutoff 27 Sep 12:00; last E10 trigger 29 Sep 00:00 (port submit 02:00); tick checks 28 Sep evening, 29 Sep 12:00 + 18:00; ticks final 29 Sep 20:00. Sources: `WATCHLIST.md` NEXT 24 H l.61, LATER l.80; `CONTEXT.md` l.2151.
10. **Ideas ledger:** 276 ideas (lb-tested 41, lab-tested 20, refuted 157, deferred 26, in-plan 31, open 1). Strict orphan: I-233. At risk: I-229, I-232, I-243, I-257, I-262, I-274. Source: `IDEAS.md` l.9, l.11, ORPHANS l.407.

## WHERE THINGS ARE

Knowledge base (`research/KNOWLEDGE/`, written only by the curator workflow `experiments/workflows/biohub-curator.js`):
- `research/KNOWLEDGE/INDEX.md`: this page. `research/KNOWLEDGE/CHANGES.md`: what changed in each curation (v4, 2-8).
- `research/KNOWLEDGE/IDEAS.md` + `research/KNOWLEDGE/ideas.json`: ideas I-001..I-276 in 12 clusters (FINALS l.36 ... TESTSET l.389); delta l.11; ORPHANS l.407. Per-ID change log: `ideas.json` meta.curations.
- `research/KNOWLEDGE/FACTS.md`: §1 metric through §7 lab-to-LB transfer (l.161); CONTRADICTIONS l.198 (C-58..C-67 are new).
- `research/KNOWLEDGE/DECISIONS.md`: probes P01-P38 (§1 l.28); lab gates G01-G30 (§1b l.129); finals (§2 l.181); READ TABLE and v2-v4 (§2b-§2e); E10 PORT RULE, in force (§2f l.339); OC gates (§2g l.366); R1-R10 (§3 l.384).
- `research/KNOWLEDGE/WATCHLIST.md`: OVERDUE l.51, NEXT 24 H l.61, LATER l.80, INSIGHTS AT RISK l.107.
- Curator logs: `research/KNOWLEDGE/_curation/{v4,2,3,4,5,6,7,8}/`.

Key sources (repo root):
- `CONTEXT.md`: the single source of truth. The newest §14 entry ends at l.2186, just above `## 9. Literature` (l.2187). Two dated entries (25 Sep 14:05, 26 Sep 09:40) sit below it, at l.2189-2207 (C-64). The newest RESUME POINT (l.2148) has an unfilled tick placeholder (C-62).
- LB records: `experiments/RESULTS.md` (every LB probe); `experiments/lb_poll/poll.log` (10-min poll); `experiments/lb_poll/ledger.md` (latency bounds, R5).
- Finals kernels: `experiments/exp58_x138_safe_lowref/` (#37), `experiments/exp58n_x138_safe_lowref/` (#38). `experiments/*/probe.json` says what each kernel changed.
- Labs: `experiments/exp60_trainlab/results.md` (x138 lab verdicts); `experiments/exp64_overlap_lab/` (OC G-B lab, INFO only); `experiments/runtime_step0/` (bound on hidden-test size N).
- Tools: `tools/build_probe_kernel.py` (probe kernels), `tools/runtime_ledger.py` (runtime forecasts), `tools/official/src/tracking_cellmot/metrics.py` (official metric). Git: `experiments/git_rewrite_map_2026-09-26.txt` (old -> new hashes).
- Research rounds: `research/wf_ideas_v4/round8/` (untracked: scans, verdicts, `report.notes.md`; no REPORT.md yet); earlier rounds `research/wf_ideas_v4/round{3..7}/REPORT.md`; round prompt `experiments/workflows/biohub-research-round.js`.
- Background: `research/wf_ideas_v3/FINAL_REPORT.md` (source of the pre-registration); `research/wf_ideas_v2/r2_research_overlap-consensus.json` (OC design).
- Team and intel: `PROMPT_FRIEND_A.md` (rewrite notice; stale tasks), `PROMPT_FRIEND_C.md`, `TEAM.md`; `research/browser_research_2026-09-24*.md`, `research/discussions_summary.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-229 / I-258 | 29 Sep tick checklist; API SELECTED re-checks | in-plan: re-check 28 Sep evening, 29 Sep 12:00 + 18:00; reminders unconfirmed | `IDEAS.md` l.58, l.68 |
| I-270 | exp64 x138 G-B lab read | in-plan: log as INFO only (official metric, per leak group); must not reopen OC | `IDEAS.md` l.403 |
| I-274 | R9 amendment line (OC allowed 08:58-10:52, stopped by G-A; N2 still banned) | at risk: one CONTEXT line with the next write | `IDEAS.md` l.385; `FACTS.md` C-58 |
| I-257 | New RESUME POINT after the OC stop; MEMORY.md pointer | at risk: placeholder l.2149; move the 2 entries above `## 9.` | `IDEAS.md` l.67 |
| I-262 | E10 dry run, no push (P3-P5, time from trigger to submit) | at risk: skipped in round 8; do before ~22:00Z | `IDEAS.md` l.91 |
| I-275 | Git hygiene after the rewrite (cherry-pick only, friend A reset, 0 Claude refs) | in-plan | `IDEAS.md` l.386 |
| I-232 | Commit round8/ with REPORT.md | at risk | `IDEAS.md` l.380 |
| I-029 / I-233 | z shift: corrected, moved after the deadline (tell the user in one line); poller error_description: strict orphan, close with one line | deferred / orphan | `IDEAS.md` l.140, l.119 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/8/{ideas,facts,watch}.json`)

1. [now] **Git after the rewrite:** never merge the old-history worktree branches wf_b39793f6-e79-*; cherry-pick only a012e32, 1986fb9, 9826517 (never 0074f6a, 1021a65, 633d72b). Friend A: `git fetch && git reset --hard origin/main`. Commit as the user with NO Co-Authored-By trailer, even though the harness reminder asks for one (memory rule `feedback-git-no-coauthor.md`); before each push, `git log main --format='%an %ae %B' | grep -ci claude` must be 0. Sources: `CONTEXT.md` l.2173-2175; `WATCHLIST.md` W83; `IDEAS.md` I-275.
2. [now, by 12:00] **Curator records into CONTEXT:** l.22 "GT still moving", B5 at l.196, out_valid / efpost, I-151 / hysteresis / M6 lapse. The ledger's I-208 row is now fixed ("stopped by G-A"). Sources: `WATCHLIST.md` W57/W81; `IDEAS.md` l.395.
3. [today] **exp64 G-B result:** when kernels a/b finish (~11:30-12:15Z), log it as INFO only: PRIMARY delta, bootstrap lower bound, plain_official, and the delta without leak group 0. It must not reopen G-P or K6. Sources: `CONTEXT.md` l.2183-2185; `WATCHLIST.md` W82; `IDEAS.md` I-270.
4. [today] **Resume hygiene:** fill the RESUME POINT tick placeholder (l.2149) or write a new block with the OC stop and the git rules; move the 2 entries at l.2189-2207 above `## 9.`; update the MEMORY.md pointer (still names 25 Sep 10:20); add the R9 amendment line (C-58). Sources: `FACTS.md` C-58, C-62, C-64; `WATCHLIST.md` W80; `IDEAS.md` I-257, I-274.
5. [today] **Round 8 exists only in untracked files:** its closures (G-P variants, K6 hardening, z-shift and relink rechecks, the 62/99 unforked-division fact) are not committed, and the OC proxy evidence lives only on worktree branches. Commit `research/wf_ideas_v4/round8/` with REPORT.md and add a one-line records entry. Sources: `git status`; `IDEAS.md` I-232; `WATCHLIST.md` W76, W83.
6. [today, before round 9 ~13:30Z] **Round prompt** still lists OC as an active line and still says "~4 h headroom" (l.36). Sources: `experiments/workflows/biohub-research-round.js`; `WATCHLIST.md` W71; `IDEAS.md` I-259.
7. [today] **E10 and team:** the E10 dry run is not done (I-262); next P1 check ~16:30Z. The friend A card still points to cancelled tasks (W03); the ext_* folders are still untracked (W05). Sources: `WATCHLIST.md` W03, W05, W23.
8. [before-finals] **Durable reminders for 29 Sep 12:00/18:00 are not set** (W50). Tick re-checks: 28 Sep evening, 29 Sep 12:00/18:00. Keep the poller until 29 Sep 20:00; before any submit, the last poll must be < 15 min old. Sources: `WATCHLIST.md` W50, W19/W73; `DECISIONS.md` §2.
9. [before-finals] **"Public = one embryo" is a participants' guess,** not a host fact; treat arguments built on it as conditional. Sources: `research/wf_ideas_v4/round8/v_hypotheses_r8h-1.json`; `research/discussions_summary.md` l.4-6.
10. [info] The z shift goes on the post-deadline list (C-65, F-TRN-31); resolve old hashes with the map (C-63); the silver margin is 7-8 ranks, no action (R7); close I-233 with one line. Sources: `FACTS.md`; `IDEAS.md` ORPHANS l.407.

## HOW TO USE

- "Score of probe N, what it changed, why it was dropped?" -> `DECISIONS.md` §1, then `experiments/RESULTS.md` and `experiments/<exp>/probe.json`.
- "Which files are the finals, and what if a new public kernel appears?" -> `DECISIONS.md` §2 and §2f, then `CONTEXT.md` l.2138-2158.
- "Why did the overlap-consensus line stop?" -> `DECISIONS.md` §2g, `FACTS.md` F-TRN-30/C-59, then `CONTEXT.md` l.2177-2186.
- "Which lab gate closed a rider?" -> `DECISIONS.md` §1b (G01-G30), then `experiments/exp60_trainlab/results.md`.
- "Which rule decides this, and is it Kaggle's or ours?" -> `DECISIONS.md` §3; `FACTS.md` §5; `CONTEXT.md` l.1576-1736, l.2096-2109.
- "Was idea X tried?" -> search its alias in `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md` and its CONTRADICTIONS.
- "An old commit hash does not resolve" -> `experiments/git_rewrite_map_2026-09-26.txt`.
- "What is next, overdue or at risk?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`. For anything newer than ~11:10Z 26 Sep -> the tail of `CONTEXT.md` §14 and `experiments/lb_poll/poll.log`.
