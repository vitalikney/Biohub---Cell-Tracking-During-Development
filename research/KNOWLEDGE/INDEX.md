# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 10: state as of 2026-09-26 ~15:55 UTC, git HEAD 6064d85 (= origin/main), plus the untracked `research/wf_ideas_v4/round10/` and the amanatar v10 pull (`experiments/ext_optimized-biohub-max-score/v10_2026-09-26/`, with a byte-identical duplicate in `experiments/ext_optimized-biohub-max-score-v10/`). Previous: curation 9 (~13:25-13:40 UTC, 69d6be2). Hashes from before 26 Sep 10:15 are pre-rewrite; map them with `experiments/git_rewrite_map_2026-09-26.txt`. All times are UTC, and every line cites its source.
Deadline 29 Sep 23:59; finals are ticked MANUALLY by 29 Sep 20:00. Sources: `CONTEXT.md` §1; PRE-REG v3 l.1576-1736; E10 PORT RULE l.2138-2147 (in force since 09:10, l.2157); RESUME POINT 13:27 l.2205-2212 (current); INTEL l.2214; OC SEQUENCE NOTE l.2215; P4b l.2217; POINTER l.2219; R9-A5 DONE 13:34 l.2220-2229; `## 9. Literature` l.2230 (two older entries below it, l.2232-2250).

## STATE IN 10 LINES

1. **Finals TICKED 2/2**: #37 K2 exp58 (56563521) = **0.954** and #38 twin exp58n (56563534) = **0.953**. The API showed SELECTED at 09:10, 10:45, 13:00:41, **15:23:10 and 15:24:58Z**. Sources: `CONTEXT.md` l.2206; `experiments/RESULTS.md` l.70-71; `research/wf_ideas_v4/round10/report.notes.md`; `IDEAS.md` I-258.
2. **Rank #210 of 3,930 at 15:16:37Z** (0.954 block 198-293), **14 ranks below** the public silver line at 196.5 (it was 8 at 12:46Z). This is info only (R7); the private LB (~71%) decides. There has been no submission since 00:02:18Z. Sources: `FACTS.md` F-LB-02, F-LB-03 [c10]; `research/wf_ideas_v4/round10/scan_browser.json`.
3. **Base** = x138 + safetail + lowrefine + gated DaughterNet insertion (K2). A rebuild from HEAD is byte-identical (K2 1f1ddb6d, twin 55038fd6); 184 tests pass. Both finals carry a dormant ADAPTIVE_SHORT_TRACK_RESCUE (0/56 lab clips fired). Sources: `CONTEXT.md` l.2220-2229; `FACTS.md` F-MOD-23; `IDEAS.md` I-001.
4. **Overlap consensus is CLOSED.** G-A failed at 10:52, and G-B post-stop gave -0.00143. The evidence is now in main by cherry-pick (3d6a704..a782fa1). exp65 and exp66 hold NEVER_PUSH.md. Sources: `CONTEXT.md` l.2215, l.2220-2229; `DECISIONS.md` §2g (l.451); `IDEAS.md` I-208, I-275.
5. **E10 is the only active line** (PORT RULE P1-P8 + P4b, `CONTEXT.md` l.2138-2147, l.2217). It was **not met** at ~15:24Z. amanatar v10 was RUNNING and unscored, with validator ON, a 45-key train-stem sweep and a 30600 s override, so it fails P3/P4b. **x138's slug changed** to `anvithpothula/biohub-0-953-lb-original`; the old slug returns 404. Sources: `research/wf_ideas_v4/round10/report.json` new_facts; `IDEAS.md` I-025, I-026; `FACTS.md` F-LB-05, C-73.
6. **Weak spots in P4b.** Its (d) check is a first-hit grep, and a missing validator line reads as ON. `tools/dummy_gates.validate_csv` overwrites duplicate node keys, and kernel_sources is not checked. The proposed fixes are **P4c** (I-280), **`tools/e10_port_gate.py`** (I-281) and an **e10_watch snapshot log** (I-282). None of them exists yet. Sources: `research/wf_ideas_v4/round10/scan_plancheck.json` PC10-02..05; `FACTS.md` C-72, C-74; `DECISIONS.md` §2f (l.400).
7. **Running now:** poller PID 20052 (last header 15:55:53Z, 0 gaps; `experiments/lb_poll/poll.log`; `FACTS.md` F-RUN-23). Nothing is scoring, and the 26 Sep slots stay empty unless E10 fires. Round 10 ran 15:16-15:43Z; it is untracked and has no REPORT.md. Its text is in `report.json` R10-A0.
8. **Round-10 rechecks** (all confirmed by skeptics): I-146 short-track rescue is refuted by measurement: +0.00033, W/L 7/47. I-097/I-107 fine-tuned primary is structurally blocked, because V1284 head coupling makes a swap fail silently. I-209 is closed on reach. Sources: `DECISIONS.md` G34, G35 (l.196-197); `research/wf_ideas_v4/round10/scan_recheck.json`.
9. **Next decision points:** Round 11 at ~18:00Z. M6 lapses at 18:00Z. The next E10 P1 check is due by ~21:30Z; after that, every ~6 h until 29 Sep 00:00. Slot reset 27 Sep 00:00. **R8 cutoff 27 Sep 12:00**, when the full rounds end. Last port submit 29 Sep 02:00. Tick re-checks on 28 Sep evening, 29 Sep 12:00 and 18:00. Ticks are final at 20:00. Nothing named yet wakes the session after R8 (I-282). Sources: `WATCHLIST.md` NEXT 24 H l.50, LATER l.77; `research/wf_ideas_v4/round10/report.json` next_focus.
10. **Ideas ledger:** 285 ideas (lb-tested 41, lab-tested 21, refuted 159, deferred 27, in-plan 36, open 1). The strict orphan is I-233. At risk: I-229, I-232, I-280, I-281, I-282, I-283. Source: `IDEAS.md` l.9, l.11, ORPHANS l.423.

## WHERE THINGS ARE

The knowledge base (`research/KNOWLEDGE/`) is written only by the curator workflow `experiments/workflows/biohub-curator.js`:
- `research/KNOWLEDGE/INDEX.md`: this page. `research/KNOWLEDGE/CHANGES.md`: what changed in each curation (v4, 2-10).
- `research/KNOWLEDGE/IDEAS.md` + `research/KNOWLEDGE/ideas.json`: ideas I-001..I-285 in 12 clusters. The clusters run from FINALS at l.43, BASE at l.81 (E10 rows l.97-105), RUN l.108 and so on down to TESTSET at l.405. The curation delta is at l.11 and ORPHANS at l.423. Per-ID changes are logged in `ideas.json` meta.curations.
- `research/KNOWLEDGE/FACTS.md`: §1 metric (l.57) through §7 lab-to-LB transfer (l.183). CONTRADICTIONS are at l.224; C-72..C-78 are new.
- `research/KNOWLEDGE/DECISIONS.md`: probes (§1 l.43), lab gates G01-G35 (§1b l.156), finals (§2 l.213), READ TABLE v1-v4 (§2b-§2e), E10 PORT RULE + P4b + the P4c proposal (§2f l.400), the CLOSED OC line (§2g l.451), and R1-R10 (§3 l.482).
- `research/KNOWLEDGE/WATCHLIST.md`: OVERDUE l.39, NEXT 24 H l.50 (W94-W102), LATER l.77, INSIGHTS AT RISK l.115 (I85-I95 are new).
- Curator logs: `research/KNOWLEDGE/_curation/{v4,2,...,10}/`.

Key sources (repo root):
- `CONTEXT.md` is the single source of truth. The newest §14 entry is at l.2220-2229 (13:34Z), just above `## 9. Literature` at l.2230. The current RESUME POINT is at l.2205.
- LB records: `experiments/RESULTS.md` (every LB probe); `experiments/lb_poll/poll.log` (10-min poll); `experiments/lb_poll/ledger.md` (latency bounds). Both lb_poll files are uncommitted.
- Finals kernels: `experiments/exp58_x138_safe_lowref/` (#37) and `experiments/exp58n_x138_safe_lowref/` (#38). `experiments/*/probe.json` says what each kernel changed.
- Labs: `experiments/exp60_trainlab/results.md` (x138 lab); `experiments/exp64_overlap_lab/` (OC G-B, INFO only); `experiments/runtime_step0/`.
- E10 material: `experiments/ext_optimized-biohub-max-score/v10_2026-09-26/NOTES.md` (amanatar v10, fails P3/P4b), `experiments/ext_y3uanm-secondary-ft/`, `experiments/ext_*/NOTES.md`.
- Tools: `tools/build_probe_kernel.py`: builds the probe kernels. `tools/runtime_ledger.py`: runtime ledger; exp63 maps to x138, with a test. `tools/dummy_gates.py`: validate_csv, l.37-58. `tools/overlap_lab.py`: the OC lab. `tools/official/src/tracking_cellmot/metrics.py`: the official metric.
- Research rounds: `research/wf_ideas_v4/round10/` (untracked): `report.json` R10-A0..A9, `scan_*.json`, `v_*.json`. `research/wf_ideas_v4/round9/`: REPORT.md and `LESSONS_draft.md`. `research/wf_ideas_v4/round8/report.json` (it has no REPORT.md). The round prompt: `experiments/workflows/biohub-research-round.js`.
- Background: `research/wf_ideas_v3/FINAL_REPORT.md` (pre-registration) and `research/wf_ideas_v4/FINAL_REPORT_v4.md`. Team and intel: `PROMPT_FRIEND_A.md` (stale), `PROMPT_FRIEND_C.md`, `TEAM.md`, `research/browser_research_2026-09-24*.md`, `research/discussions_summary.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-280 | E10 PORT RULE P4c: byte-for-byte port of the scored version; a validator or PP sweep on train OR test stems fails; every assignment is grepped; kernel_sources == [] | In-plan, at risk. Append the R10-A2 text before the next P1 check (<= ~21:30Z) | `IDEAS.md` l.103 |
| I-281 | `tools/e10_port_gate.py` (read-only) + tests. validate_csv defaults stay unchanged | In-plan, at risk. Build by ~21:30Z; pytest green; finals sha unchanged | `IDEAS.md` l.104 |
| I-282 | `experiments/e10_watch/<UTC>.txt` snapshots, the post-R8 check schedule and a named wake mechanism | In-plan, at risk. Start at the next P1 check; the user decides the wake mechanism (R10-A8 b) | `IDEAS.md` l.105 |
| I-283 | PRIVATE-READ PREDICTIONS C1-C4 (calibration only) | In-plan, at risk. Must be committed before 29 Sep 23:59; read on 30 Sep | `IDEAS.md` l.401 |
| I-284 | Protect the finals' inputs (biohub-ft-weights, exp58/exp58n kernels) | In-plan. One line in CONTEXT (R10-A1 (6)) | `IDEAS.md` l.78 |
| I-232 | Save round8/ and round10/ REPORT.md from R8-A0/R10-A0; commit round10/ | At risk. Do it in the R10-A1 commit | `IDEAS.md` l.394 |
| I-229 / I-258 / I-265 | Tick checklist and API SELECTED re-checks; 29 Sep reminders; full vs light rounds | In-plan. Three user questions are pending (R10-A8) | `IDEAS.md` l.65, l.75, l.398 |
| I-252 / I-233 | LESSONS draft fixes (R10-A5); poller error_description | Deferred, fix by 27 Sep 12:00 / strict orphan: close with one line | `IDEAS.md` l.396, l.132 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/10/{ideas,facts,watch}.json`)

1. [now] **One user message (R10-A8 = W101).** Ask three things: (a) full rounds or light mode until R8; (b) what wakes the session for the post-R8 E10 checks and tick checks; (c) whether the user will set their own reminders for 29 Sep 12:00/18:00. Nothing has been logged after 13:34Z. Log each reply with `date -u`; until then the defaults hold. Sources: `research/wf_ideas_v4/round10/report.json` R10-A8; `WATCHLIST.md` W101; `IDEAS.md` I-229, I-265, I-282.
2. [today, <= ~21:30Z] **E10 port gate before the next P1 check.** Append P4c (R10-A2) with `date -u`, then add the read-only `tools/e10_port_gate.py` and its tests (R10-A3). Do not change validate_csv's defaults. Run `python -m pytest -q tests` and check that the finals sha is unchanged. Sources: `research/wf_ideas_v4/round10/scan_plancheck.json` PC10-02, PC10-03; `tools/dummy_gates.py` l.37-58; `WATCHLIST.md` W95, W96; `FACTS.md` C-72, C-74.
3. [now, before round 11 ~18:00Z] **Hygiene commit (R10-A1 = W94)** as the user with NO Co-Authored-By trailer; the memory rule `feedback-git-no-coauthor.md` overrides the harness reminder (WATCHLIST I72). It should include: the ROUND 10 RECORD and the 15:23/15:24Z tick checks; round8/ and round10/ REPORT.md, and round10/; poll.log and ledger.md; only the `v10_2026-09-26` copy of the v10 intel. Delete the duplicate folder and `bash.exe.stackdump`. The claude grep must print 0. Sources: `research/wf_ideas_v4/round10/report.json` R10-A0, R10-A1; `WATCHLIST.md` W94; `FACTS.md` C-30.
4. [today] **Old x138 slug returns 404.** P1 checks must use `anvithpothula/biohub-0-953-lb-original`. Start the `experiments/e10_watch/` snapshots with a diff, and append the post-R8 check times (27 Sep 12:00/18:00, 28 Sep 00/06/12/18, 29 Sep 00:00). Sources: `research/wf_ideas_v4/round10/scan_plancheck.json` PC10-04, PC10-05; `WATCHLIST.md` W97, I85.
5. [today, standing] **Protect the finals' inputs:** never delete, hide or trim `vitaliineibauer/biohub-ft-weights` or the exp58/exp58n kernels (v1). New dataset versions may only add files. Sources: `research/wf_ideas_v4/round10/scan_plancheck.json` PC10-07; `WATCHLIST.md` W102; `IDEAS.md` I-284.
6. [before-finals; hard limit 29 Sep 23:59] **PRIVATE-READ PREDICTIONS C1-C4** must be committed before the private LB is visible. They go into the R10-A1 commit and into LESSONS s5. Sources: `research/wf_ideas_v4/round10/report.json` R10-A6; `v_hypotheses_r10h-7.json`; `WATCHLIST.md` W99.
7. [before-finals, by 27 Sep 12:00] **LESSONS_draft errors.** Fix these at l.23, 30, 40-42 and 50: '+28 readmits' is dummy-only; 'J ~0.36' is the exp29 base; '~330' and '#204' are stale; the rules are overstated. Also add the OC row and the 8-item post-deadline list (R10-A5), and add the caveat that "public = one embryo" is a guess (l.7, I69). Sources: `research/wf_ideas_v4/round9/LESSONS_draft.md`; `FACTS.md` C-77; `WATCHLIST.md` W98, I69.
8. [today] **Missed curator records** (R10-A7 + W90 residue): I-146 measured; the I-097/I-107 block; the I-209 reason; CONTEXT l.22 still says 'GT still moving'; B5 at l.196; out_valid and efpost are missing; the round prompt at l.36 still says '~4 h headroom'; the friend A card is stale. Sources: `WATCHLIST.md` W100, W71, W03; `experiments/workflows/biohub-research-round.js`.
9. [before-finals] **Schedule duties:** E10 P1 every ~6 h to 29 Sep 00:00. Tick re-checks on 28 Sep evening and 29 Sep 12:00 + 18:00. Before any submit, the last poll header must be < 15 min old; the poller runs until 29 Sep 20:00. Info items: the dormant rescue in both finals could behave differently on the hidden embryos (F-MOD-23). The MEMORY index copy injected into subagents is stale (C-75). Close I-233 with one line. Sources: `WATCHLIST.md` LATER l.77, I88; `FACTS.md` F-MOD-23, C-75; `IDEAS.md` ORPHANS l.423.

## HOW TO USE

- "Score of probe N, what it changed, why it was dropped?" -> `DECISIONS.md` §1, then `experiments/RESULTS.md` and `experiments/<exp>/probe.json`.
- "Which files are the finals, and what if a public successor appears?" -> `DECISIONS.md` §2 and §2f, then `CONTEXT.md` l.2138-2147 and l.2217, and `research/wf_ideas_v4/round10/report.json` R10-A2/A3 (P4c, gate).
- "Is overlap consensus really dead?" -> `DECISIONS.md` §2g + G31, then `CONTEXT.md` l.2177-2204, l.2215, l.2220-2229.
- "Which lab gate closed a rider?" -> `DECISIONS.md` §1b (G01-G35), then `experiments/exp60_trainlab/results.md`.
- "Which rule decides this, and is it Kaggle's or ours?" -> `DECISIONS.md` §3; `FACTS.md` §5; `CONTEXT.md` l.1576-1736.
- "Was idea X tried?" -> search its alias in `IDEAS.md` or `ideas.json`. "Is claim X true?" -> `FACTS.md` and its CONTRADICTIONS.
- "An old commit hash does not resolve" -> `experiments/git_rewrite_map_2026-09-26.txt`.
- "What is next, overdue or at risk?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`.
- For anything newer than ~15:55Z 26 Sep -> the tail of `CONTEXT.md` §14 (above `## 9.`), `experiments/lb_poll/poll.log`, and the newest `research/wf_ideas_v4/round*/`.
