# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 3, state as of 2026-09-25 ~23:15 UTC, git HEAD 1ca747b (+ untracked `research/wf_ideas_v4/round3/`); previous: curation 2 (20:55 UTC, da154cb). All times UTC. Every line cites its source.
Deadline 29 Sep 23:59; finals ticked MANUALLY by the user by 29 Sep 20:00 (`CONTEXT.md` §1; PRE-REG v3 §f l.1707-1736; AMENDMENT f2 l.1887-1895).

## STATE IN 10 LINES

1. Best public **0.954** = P35 exp57b (x138 + ungated insertion). NOT a finals candidate: R5(a) UNPROVEN, L35 in (6.72, 7.73] h - `experiments/lb_poll/ledger.md`; `DECISIONS.md` §1 P35, §2.
2. Base = **x138** (P34 exp56 = 0.953, L34 <= 6.46 h, ADMIT); branch A (the insertion stays in F1) - `CONTEXT.md` l.1797-1805; `experiments/lb_poll/ledger.md`.
3. Rank **#164 of 3,914** at 22:16. We are 18th of 65 teams in the 0.954 block, and the silver line (~196) falls inside that block, 32 ranks below us - `FACTS.md` F-LB-02/03; `research/wf_ideas_v4/round3/report.json` new_facts (1).
4. Every rider is closed: no K3 (forkmid), no K3b (DeepCenter), forkblob FAIL, K4 dropped, ANTIPAR/DNVETO closed. Round 3 adds that the x138 tail is saturated (edge FN = node misses 49% / swaps 43% / dangling 8%) - `CONTEXT.md` l.1918-1951; `DECISIONS.md` §1b G01-G11; `FACTS.md` F-TRN-15.
5. **User OK on AMENDMENT f2 at 22:06**, so F2 = exp58n twin (twin dummy gates PASS at 20:55). Default finals: F1 = K2 = exp58 and F2 = twin, P ~0.85-0.9 - `CONTEXT.md` l.1955-1966; `research/wf_ideas_v4/round3/report.json` R3-A9.
6. Running now: P36 = exp57 v1, PENDING at 23:03Z (L > 6.74 h), INFO ONLY; the LB poller + runtime ledger. K2 and the twin are NOT submitted yet - `experiments/lb_poll/ledger.md`; `DECISIONS.md` §1 P36-P38.
7. Next: at **00:01-00:10 26 Sep**, submit K2 (`probe 37: exp58`) and the twin (`probe 38: exp58n`), both v1 with no re-push. Right after, commit the READ TABLE + a new RESUME POINT. Round 4 runs ~00:45 - `WATCHLIST.md` W16, W39, W40, W10.
8. 26 Sep decision points: the morning OK list before ~06:30; K2 COMPLETE by 08:01 = "clean"; R5(a) proof by 09:31; read the scores by the READ TABLE; closures into CONTEXT by 12:00. K2's latency forecast is F(K2) = 7.87 h, with an R5(b) margin of 1.63 h - `WATCHLIST.md` W19-W21, W31; `FACTS.md` F-RUN-13; `DECISIONS.md` §2b.
9. Cutoffs: R8 (no new mechanisms) 27 Sep 12:00; S12 consolidation 28 Sep 12:00; admission table 28 Sep 22:00; finals tick by 29 Sep 20:00 (reminder at 12:00); R9 refuses retraining - `CONTEXT.md` l.1671-1676; `WATCHLIST.md` T03-T10.
10. Ideas ledger: 223 ideas; refuted 129, lb-tested 37, lab-tested 20, deferred 19, in-plan 18, open-untested 0. At risk: I-035, I-217, I-223 - `IDEAS.md` header l.9, ORPHANS l.354.

## WHERE THINGS ARE

Knowledge base (`research/KNOWLEDGE/`, written only by the curator workflow `experiments/workflows/biohub-curator.js`):
- `research/KNOWLEDGE/INDEX.md` - this page: state, map, top ideas, top alerts.
- `research/KNOWLEDGE/IDEAS.md` + `research/KNOWLEDGE/ideas.json` - 223 ideas I-001..I-223 in 12 clusters, each with status and sources. The ORPHANS section starts at l.354; `ideas.json` `meta.curations` logs every status change.
- `research/KNOWLEDGE/FACTS.md` - verified facts (§1 metric ... §7 lab-to-LB transfer) + CONTRADICTIONS C-01..C-29 (l.140).
- `research/KNOWLEDGE/DECISIONS.md` - probes P01..P38 (§1), lab-gate decisions G01-G11 (§1b), finals table (§2), proposed READ TABLE (§2b), R1-R10 status (§3).
- `research/KNOWLEDGE/WATCHLIST.md` - OVERDUE / NEXT 24 H / LATER / INSIGHTS AT RISK (W, T, I IDs).
- `research/KNOWLEDGE/CHANGES.md` - the delta for each curation. Curator logs and JSON answers: `research/KNOWLEDGE/_curation/v4/`, `research/KNOWLEDGE/_curation/2/`, `research/KNOWLEDGE/_curation/3/`.

Key sources (repo root):
- `CONTEXT.md` - single source of truth. The newest entries sit at the end of §14, just above "## 9. Literature" (l.1967). PRE-REG v3 l.1576-1736; ADDENDUM L l.1850; AMENDMENT f2 l.1887-1895; exp60 read l.1918-1937; round 2 + ADDENDUM M post-hoc l.1938-1954; f2 OK l.1960-1966. The last RESUME POINT (l.1519, 10:20) is STALE.
- `experiments/RESULTS.md` - every LB probe with its score. `experiments/lb_poll/poll.log` - the 10-min poll (only the 5 newest rows, see `experiments/lb_poll/lb_poll.py` l.28). `experiments/lb_poll/ledger.md` - latency bounds, R5 and the family of each submission.
- `experiments/*/probe.json` - what each kernel changed. `experiments/exp58_x138_safe_lowref/` = K2; `experiments/exp58n_x138_safe_lowref/` = f2 twin; `experiments/exp58t_x138_safe/` = K1 fallback.
- `experiments/exp60_trainlab/results.md`, `experiments/exp60_trainlab/results_forkblob.md` - the x138 train lab (T9 verdicts). `experiments/runtime_step0/` - hidden-N bound and K2 latency forecast.
- `tools/runtime_ledger.py` (A5 ledger; run `--print` after the submits), `tools/dummy_gates.py`, `tools/trainlab.py`, `tools/build_probe_kernel.py` (kernel builder).
- `research/wf_ideas_v4/round3/report.json` - night round 3 (22:59Z; READ TABLE in plan_issues, actions R3-A1..A9, new_facts (1)-(17)). Untracked, and no REPORT.md was written. `research/wf_ideas_v4/round2/report.json` - round 2 (committed 4f5d325, also no REPORT.md). `research/wf_ideas_v4/FINAL_REPORT_v4.md` - round 1 plan (its §5 OK list is stale).
- `experiments/workflows/biohub-research-round.js` - the night-round prompt; l.34/l.54 are stale and still list K3/K3b.
- `research/wf_ideas_v3/FINAL_REPORT.md` - pre-reg source and slot table. `research/wf_ideas_v3/TASK_*.md`, `PROMPT_FRIEND_A.md`, `PROMPT_FRIEND_C.md`, `TEAM.md` - task cards and roles (the friend A card is stale).
- `research/browser_research_2026-09-24*.md`, `research/discussions_summary.md`, `research/survey_*.md` - external intel.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-001 | K2 = exp58: x138 + safetail + lowrefine + insertion | in-plan. Submit at 00:01 with `-m "probe 37: exp58 ..."`, v1, no re-push; read by the READ TABLE | `IDEAS.md` l.42; `WATCHLIST.md` W16 |
| I-090 | F2 = no-insertion twin exp58n (AMENDMENT f2) | in-plan, **user OK 22:06**. Submit right after K2 as `probe 38: exp58n`; F2 if it scores, is R5-admissible and >= 0.953 | `IDEAS.md` l.70; `CONTEXT.md` l.1960-1966 |
| I-217 | K2/twin READ TABLE (d1 = K2 - #35, d2 = twin - #34, clean = L(K2) <= 8.0 h, rows 1-5) | at risk: NOT in CONTEXT. Commit it verbatim before any K2/twin score (~06:00 at the earliest) | `IDEAS.md` l.77; `DECISIONS.md` §2b |
| I-223 | Poller window `[:12]` -> `[:60]` | at risk, not applied. Restart only 23:15-23:55 tonight or after 09:30 on 26 Sep | `IDEAS.md` l.57; `experiments/lb_poll/lb_poll.py` l.28 |
| I-011 | K1 (exp58t) contingency | in-plan, needs the morning OK. Only on READ TABLE rows 1/4/5; never at d1 = -0.001 | `IDEAS.md` l.52; round3 R3-A9 (1) |
| I-219 | Twin floor 0.952 instead of 0.953 (new) | needs the user's OK before the first score is acted on (~06:30) | `IDEAS.md` l.78 |
| I-215 | floatout on x138 as a fail-soft F1 rider | optional (morning OK). Needs a fail-soft check + FORCE_FAIL test by R8; rides only in S12; ~+0.0001 private | `IDEAS.md` l.127; round3 R3-A9 (5) |
| I-035 | Head cascade / V1284 scale pre-gate | at-risk orphan, never run. Close it in one CONTEXT line (or run the CPU desk test) before R8 (27 Sep 12:00) | `IDEAS.md` l.115, ORPHANS |

## TOP ALERTS (deduplicated from the three curators, `research/KNOWLEDGE/_curation/3/*.json`)

1. [now] Submit K2 (exp58 v1, `probe 37: exp58 ...`) then the twin (exp58n v1, `probe 38: exp58n ...`) at 00:01-00:10 26 Sep. List the submissions first; no re-push, and no `--k2/--family` flags are needed. Then run `python tools/runtime_ledger.py --print` and log both refs, the submit times and P36's state in CONTEXT - `WATCHLIST.md` W16; round3 R3-A1; `FACTS.md` C-28.
2. [now] The READ TABLE is not in CONTEXT (`grep 'READ TABLE' CONTEXT.md` = 0). Without it the R3 reference for K2 is undefined: 0.952 passes against #34 and fails against #35. Commit it verbatim before any score reaches `poll.log` - `DECISIONS.md` §2b; `FACTS.md` C-27; `WATCHLIST.md` W39.
3. [now] The live RESUME POINT (`CONTEXT.md` l.1519, 10:20) still says F2 = exp51 and F1 = best of {exp57b, exp56, ...}, against §f + f2. Append a 26 Sep 00:1x RESUME POINT (quote f2 verbatim, point to the READ TABLE) and mark the old block SUPERSEDED. Fix the MEMORY.md "Resume point" line and the approval memory, which gives the f2 OK as ~21:00 while CONTEXT says 22:06 - `WATCHLIST.md` W40, W34; `FACTS.md` C-25, C-26.
4. [now] Workflow prompt drift: `experiments/workflows/biohub-research-round.js` l.34/l.54 still lists K3/K3b, S4-S6 riders and K4/N1 approvals. Edit it before round 4 (~00:45), and add "S4-S6 carry no rider" to CONTEXT - `WATCHLIST.md` W37; `FACTS.md` C-29; round3 R3-A3.
5. [now] The poller keeps only the 5 newest submissions. Change `[:12]` to `[:60]`, restart only in a quiet window (never 06:00-09:30), then check for a block with more than 5 rows. Curators disagree on the line (l.27 in `FACTS.md` F-RUN-14, from round 3); it is **l.28** at 1ca747b - `WATCHLIST.md` W36; `IDEAS.md` I-223.
6. [today] Morning OK list (R3-A9 replaces R2-A8): (1) K1 only via READ TABLE rows 1/4/5; (2) twin floor 0.952; (3) F1 = twin if twin - K2 >= +0.002; (4) F1 = twin instead of #34 when there is no K1; (5) optional S12 floatout; (6) deadline move / D4 / N1 only if the runtime trigger fires. Without the OKs the strict text applies - `WATCHLIST.md` W21; `DECISIONS.md` §2b.
7. [today] Round-3 closures exist only in research files: swapfix I-165/I-166, boundary rescue I-145, axis-flip I-151, dangling-end relink I-173, I-218, I-220-I-222, the lab node-count calibration rule (I-201), I-213 and R2S-6. Add them to CONTEXT by 26 Sep 12:00, and note that the M6 K4 reopen window lapses at 18:00 - `WATCHLIST.md` W31, T12; `IDEAS.md` ORPHANS.
8. [today] Runtime records and quota evidence are not in CONTEXT: F(K2) = 7.87 h, R5(b) margin 1.63 h, and the fact that hidden reruns use no GPU quota (CONTEXT l.1746 still says "unverified"). Add them with the RESUME POINT - `WATCHLIST.md` W41, W06; `FACTS.md` F-RUN-13, F-RUL-05.
9. [today] `research/wf_ideas_v4/round3/` is untracked, and neither round has a REPORT.md, although CONTEXT l.1938 cites `round2/REPORT.md`. Commit round 3, save `report_md_ru` as the REPORT.md files and fix the citation - `WATCHLIST.md` W38.
10. [now] The friend A card is fully stale: it asks for shard B, which finished at 20:05, and for tempfuse, which was dropped. His Task 0 reply is not recorded. Add a "cancelled" top block to `PROMPT_FRIEND_A.md` - `WATCHLIST.md` W02, W03.
11. [before-finals] Close or run I-035 before R8. Still not done: the admission table, committing `experiments/ext_corwin-biocel-aux/` and `experiments/ext_y3uanm-secondary-ft/`, and marking NEXT_RESEARCH superseded. Never tick exp56 or two identical files - `WATCHLIST.md` W04, W05, W26, T09-T10.
12. [info] P36 is still PENDING (L > 6.74 h at 23:03Z). If it is still pending at the submit, L(K2) may include queue time. Compare L(twin) with L(K2) before raising the runtime trigger (I-004) - `experiments/lb_poll/ledger.md`; `WATCHLIST.md` W14. Also: `TEAM.md` l.9 still states "TARGET 0.97" (`FACTS.md` C-04), and DeepCenter t* = 0.30 is a post-deadline idea only (`WATCHLIST.md` I19).

## HOW TO USE

- "What is the score / what did probe N change / why was it dropped?" -> `DECISIONS.md` §1, then `experiments/RESULTS.md` and `experiments/<exp>/probe.json`.
- "How do we read the K2/twin scores and pick F1/F2?" -> `DECISIONS.md` §2b (READ TABLE) + §2, and the rule text in `CONTEXT.md` §f l.1707-1736 and f2 l.1887-1895.
- "Which lab gate closed forkmid / K3b / forkblob / ANTIPAR / swapfix?" -> `DECISIONS.md` §1b, then `experiments/exp60_trainlab/results.md`.
- "Which rule decides this score?" -> `DECISIONS.md` §3 (R1-R10); rule text in `CONTEXT.md` l.1576-1736; latency bounds in `experiments/lb_poll/ledger.md`.
- "Was idea X tried, and what happened?" -> search the alias in `IDEAS.md` / `ideas.json` (aliases column).
- "Is claim X true (metric, N, limits, weights, latency)?" -> `FACTS.md`; for conflicting statements, `FACTS.md` CONTRADICTIONS.
- "What must happen next / what is overdue / what might we forget?" -> `WATCHLIST.md`.
- "What changed since the last curation?" -> `CHANGES.md`. For anything newer than ~23:05 25 Sep, see the tail of `CONTEXT.md` §14 and `experiments/lb_poll/ledger.md`.
