# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 6: state as of 2026-09-26 ~06:30 UTC, git HEAD 2f6ec9d (== origin/main; fc51b75 04:04:45Z, 801de5a/2f6ec9d 04:12Z) plus the untracked `research/wf_ideas_v4/round6/`. Previous: curation 5 (~04:05 UTC, f05389e). All times UTC; every line cites its source.
Deadline 29 Sep 23:59; the user ticks finals MANUALLY by 29 Sep 20:00. Sources: `CONTEXT.md` §1; PRE-REG v3 §f l.1707-1736; READ TABLE l.1978-2005; RESUME POINT l.2006-2025; CLARIFICATION v2 l.2026-2032; tick rule + checklist l.2034-2038; CLARIFICATION v3 l.2039-2046; OK REQUEST l.2049-2051; K2'' builder l.2052-2057.

## STATE IN 10 LINES

1. **Best public 0.954** (P35 exp57b, R5 UNPROVEN; P36 exp57, diagnostic): neither is a final. **Rank #162 of 3,922 at 05:46Z**, 6th of 76 in the 0.954 block, 34 ranks above silver (~#196). Sources: `FACTS.md` F-LB-01/02/03 [c6]; `research/wf_ideas_v4/round6/report.json` new_facts.
2. **Base x138** (P34 exp56 = 0.953, ADMIT, L <= 6.46 h). Sources: `experiments/lb_poll/ledger.md` (06:24:03Z); `DECISIONS.md` §1.
3. **Running:** #37 K2 exp58 (ref 56563521, 00:02:12Z) and #38 twin exp58n (56563534, 00:02:18Z), both **PENDING at 06:24:02Z** (L > 6.36 h, no error). ETA twin ~06:15-07:40Z, K2 ~07:00-09:30Z. Poller PID 20052 + clean-proof job PID 13436 (one-shots 07:57:30/08:00:45/08:01:45Z; 8.0 h mark 08:02:12Z) must stay up. Sources: `experiments/lb_poll/poll.log` l.3312-3317; `WATCHLIST.md` T24; `CONTEXT.md` l.2046 (V7).
4. **Default finals:** the pair {#37, #38}, read by the READ TABLE + CLARIFICATION v2 + **v3 (V1-V7, in CONTEXT since 04:04:45Z, pre-score)**. Sources: `DECISIONS.md` §2, §2b-§2d; `CONTEXT.md` l.2039-2046.
5. **CLARIFICATION v4 (W1-W8, V4b B', R5 line F' = 8.27 h, V3b K2'' gate) is NOT in CONTEXT.** W1 = late-OK rule vs T0 (last poll.log header with both PENDING). Must be committed before the first #37/#38 result, else post-hoc NOTES. Sources: `DECISIONS.md` §2e l.254; `FACTS.md` C-43..C-47; round6 `report.json` R6-A1 v4_text.
6. **OK request posted 04:04Z; no user reply recorded.** Under W1 a score-reading [OK] (twin floor 0.952, row-2 F2 = K2, K1 in rows 4/C4) after T0 is USER DECISION AFTER SCORE. Sources: `CONTEXT.md` l.2049-2051; `IDEAS.md` I-245; `WATCHLIST.md` W61.
7. **Finals ticked: 0 of 2** (auto-select would pick P36 + #35); no durable 29 Sep reminders (W50). Sources: `CONTEXT.md` l.2034-2038; `FACTS.md` F-RUL-12; `WATCHLIST.md` W50, W54.
8. **All riders closed**; round 6 also closed stitch on x138 (G20), linefit (G21, no detectable effect) and K4 = K2 + efpost (G22; efpost kept as a neutral FACT, 6bba +0.00174, 44b6 0). K2'' = exp58d (37800/32400) is the only runtime-trigger build, likeliest user decision today (P(not clean) ~0.3-0.5, a guess). Sources: `DECISIONS.md` §1b G20-G22; `FACTS.md` F-TRN-24..26, F-MOD-20; `IDEAS.md` I-235, I-247.
9. **Next decision points (26 Sep):** v4 commit + morning brief now; clean mark 08:02:12Z; score read with the round-6 cheat sheet (B and B') when both are terminal; commit poll.log + ledger.md at the first result; provisional tick ~09:30-10:00; round 7 ~09:40Z; curator records by 12:00; M6 lapses 18:00. Cutoffs: R8 + last K2'' submit 27 Sep 12:00; finals tick 29 Sep 20:00 (reminders 12:00 + 18:00). Sources: `WATCHLIST.md` NEXT 24 H l.53, LATER l.84; `CONTEXT.md` l.1614-1615.
10. **Ideas ledger:** 255 ideas: lb-tested 38, lab-tested 20, refuted 143, deferred 21, in-plan 32, open-untested 1. Strict orphan I-233; at risk I-229, I-232, I-243, I-244, I-245, I-248, I-249. Source: `IDEAS.md` l.9, l.11, ORPHANS l.386.

## WHERE THINGS ARE

Knowledge base (`research/KNOWLEDGE/`, written only by the curator workflow `experiments/workflows/biohub-curator.js`):
- `research/KNOWLEDGE/INDEX.md`: this page. `research/KNOWLEDGE/CHANGES.md`: delta per curation (v4, 2-6).
- `research/KNOWLEDGE/IDEAS.md` + `research/KNOWLEDGE/ideas.json`: I-001..I-255 in 12 clusters with status and sources; delta l.11, ORPHANS l.386; per-ID change log in `ideas.json` meta.curations.
- `research/KNOWLEDGE/FACTS.md`: facts §1 metric .. §7 lab-to-LB transfer; CONTRADICTIONS l.167 (new C-43..C-47 l.213-217).
- `research/KNOWLEDGE/DECISIONS.md`: probes P01..P38 (§1), lab gates G01-G22 (§1b l.106), finals (§2 l.148), READ TABLE (§2b), v2 (§2c), v3 (§2d, in CONTEXT), proposed v4 + cheat sheet (§2e l.254), R1-R10 (§3 l.288).
- `research/KNOWLEDGE/WATCHLIST.md`: OVERDUE l.39, NEXT 24 H l.53, LATER l.84, INSIGHTS AT RISK l.111 (W, T, I IDs).
- Curator logs: `research/KNOWLEDGE/_curation/{v4,2,3,4,5,6}/`.

Key sources (repo root):
- `CONTEXT.md`: single source of truth; newest entry ends at l.2057, just above "## 9. Literature" (l.2058). PRE-REG v3 l.1576-1736.
- `experiments/RESULTS.md` (every LB probe; P37/P38 PENDING at l.70-71). `experiments/lb_poll/poll.log` (10-min poll). `experiments/lb_poll/ledger.md` (latency bounds, R5, A5 watch; K2-only keep-until text, C-45).
- Kernels: `experiments/exp58_x138_safe_lowref/` (K2), `experiments/exp58n_x138_safe_lowref/` (twin), `experiments/exp58t_x138_safe/` (K1); `experiments/*/probe.json` says what each changed.
- `experiments/exp60_trainlab/results.md` (x138 lab verdicts); `experiments/runtime_step0/` (hidden-N bound, F(K2) = 7.87 h).
- `tools/runtime_ledger.py` (`--print`; 10.5 h exp58d family l.52-73), `tools/build_probe_kernel.py` (accepts only (34200, 28800) or (37800, 32400), l.1478, l.2032), `tools/dummy_gates.py` (`--k2`), `tools/official/src/tracking_cellmot/metrics.py` (edge FP rule l.157-195).
- `research/wf_ideas_v4/round6/report.json` (untracked): R6-A1..A8, `v4_text`, `morning_brief_ru`, `cheat_sheet`, `report_md_ru` (no REPORT.md yet; round2 also missing).
- `research/wf_ideas_v3/FINAL_REPORT.md` (pre-reg source); `PROMPT_FRIEND_A.md` (stale), `PROMPT_FRIEND_C.md`, `TEAM.md`; intel in `research/browser_research_2026-09-24*.md`, `research/discussions_summary.md`, `research/survey_*.md`.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-001 / I-090 | K2 exp58 (#37) / no-insertion twin exp58n (#38) | in-plan: SUBMITTED, PENDING at 06:24Z; read as a pair | `IDEAS.md` l.42, l.83 |
| I-244 / I-245 | CLARIFICATION v4; W1 OK timing vs T0 | at risk: not in CONTEXT; commit before the first result | `IDEAS.md` l.98-99; `DECISIONS.md` §2e |
| I-249 / I-229 | Morning brief (once, chat + push); 29 Sep reminders (W50) | at risk: not sent / not set | `IDEAS.md` l.100, l.95 |
| I-250 / I-246 | Score-read cheat sheet; R5 basis F' = 8.27 h | in-plan: use at the read | `IDEAS.md` l.101, l.67 |
| I-235 / I-237 / I-247 | K2'' = exp58d; bound B + B'; V3b 6-check gate | in-plan: builder merged, not built; only on trigger + user yes | `IDEAS.md` l.61-62, l.68 |
| I-248 | W6 poller scope to every 26 Sep submission (+9.5 h / +10.5 h) | at risk: ledger text is K2-only | `IDEAS.md` l.69 |
| I-011 / I-219 / I-225 | K1 contingency; twin floor 0.952; K2 resubmit on "Kaggle Error" | in-plan; need the OK (W1 timing applies) | `IDEAS.md` l.52, l.91, l.58 |
| I-243 / I-232 / I-233 | ledger text fix; round2/round6 REPORT.md; poller error_description | after ~09:40Z / with v4 commit / close or implement | `IDEAS.md` l.66, l.370, l.60 |

## TOP ALERTS (deduplicated from `research/KNOWLEDGE/_curation/6/{ideas,facts,watch}.json`)

1. [now] **CLARIFICATION v4 not in CONTEXT.** Grep poll.log for COMPLETE/ERROR of 56563521/56563534 first; paste round6 `v4_text` verbatim after l.2057 (label post-hoc NOTES if a result exists); commit as the user with round6/REPORT.md; push. Includes the R5 F' line (C-44) and B' (C-43). Sources: `WATCHLIST.md` W62, W60; `FACTS.md` C-47; `DECISIONS.md` §2e.
2. [now] **Late-OK rule and unanswered OK.** No reply to the 04:04Z request; log any reply with `date -u` against T0; score-reading OKs after T0 = USER DECISION AFTER SCORE. Sources: `WATCHLIST.md` W61; `IDEAS.md` I-245; `CONTEXT.md` l.2049-2051.
3. [now] **Morning brief unsent** (`morning_brief_ru`: status, likely K2'' question, tick exactly 2, W50 reminders). Refresh status from poll.log; send once; do not re-post the OK list. Sources: `WATCHLIST.md` W63; `IDEAS.md` I-249.
4. [today] **Clean-proof window 07:45-08:05Z:** only PIDs 20052 and 13436 poll; no builds, code edits or submits in 07:45-08:35Z; run `tools/runtime_ledger.py --print` after 08:01:45Z and after the ~08:04Z poll. Sources: `WATCHLIST.md` T24; `CONTEXT.md` l.2046.
5. [today] **Score read + tick:** rows 2-5 only when both are terminal; report B and B'; commit poll.log + ledger.md at the first result; user ticks EXACTLY 2 files by ref (default 56563521 + 56563534); verify 2/2. Sources: `WATCHLIST.md` W47, W64, W54; `DECISIONS.md` §2e.
6. [today] **K2'' likeliest decision.** Only on trigger + user yes: build with the l.2055-2057 command, V3b gate (sha-only V3 cannot catch a mis-build), own slug v1, submit by 27 Sep 12:00, poller to +10.5 h. Sources: `WATCHLIST.md` W65, T25; `FACTS.md` F-MOD-20, C-43.
7. [today] **Poller stop rule:** ledger prints K2-only "until 08:32:12Z"; keep PID 20052 until every 26 Sep submission is terminal and past its mark (V7 + W6); ledger code fix only after ~09:40Z. Sources: `FACTS.md` C-45; `IDEAS.md` I-248, I-243.
8. [today/before-finals] **Round-6 records into CONTEXT by 12:00:** intel #162 05:46Z, official edge FP rule, stitch/linefit closed, efpost neutral FACT, 15.4% runtime spread, CONTEXT l.22 fix, B5 l.196 AdaBN blocker, curation-3 closures. Never reword I-161/I-162 to "public has no frozen frames" (C-46). Sources: `WATCHLIST.md` W66, W31; `FACTS.md` F-MET-03, F-RUN-20, C-36, C-46.
9. [before-finals] **Durable 29 Sep reminders** (12:00, 18:00; user's calendar, cloud routine only with a new OK) and the admission table do not exist. Sources: `WATCHLIST.md` W50, W04.
10. [info] Still open: friend A card stale (W03), `experiments/ext_*` untracked (W05), RESULTS.md exp60 line (W35), memory residue (W34), stale A5-F ledger text (C-40), I-233 strict orphan. Sources: `WATCHLIST.md` OVERDUE l.39; `IDEAS.md` ORPHANS l.386.

## HOW TO USE

- "Score of probe N, what it changed, why dropped?" -> `DECISIONS.md` §1, then `experiments/RESULTS.md` and `experiments/<exp>/probe.json`.
- "How do we read K2/twin and pick the pair?" -> `DECISIONS.md` §2b-§2e (cheat sheet in §2e), then `CONTEXT.md` l.1978-2057 and round6 `report.json` cheat_sheet.
- "Which lab gate closed a rider?" -> `DECISIONS.md` §1b (G01-G22), then `experiments/exp60_trainlab/results.md`.
- "Which rule decides this?" -> `DECISIONS.md` §3; rule text `CONTEXT.md` l.1576-1736; latency bounds `experiments/lb_poll/ledger.md`.
- "Was idea X tried?" -> search the alias in `IDEAS.md` / `ideas.json`. "Is claim X true?" -> `FACTS.md` and its CONTRADICTIONS.
- "What is next / overdue / at risk?" -> `WATCHLIST.md`. "What changed?" -> `CHANGES.md`. Anything newer than 06:30Z 26 Sep -> tail of `CONTEXT.md` §14 and `experiments/lb_poll/poll.log`.
