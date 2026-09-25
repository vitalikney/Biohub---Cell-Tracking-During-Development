# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation v4 (first build), state as of 2026-09-25 ~18:30 UTC, git HEAD 14c339e. All times UTC. Every line cites its source.
Deadline 29 Sep 23:59; finals ticked MANUALLY by the user by 29 Sep 20:00 (`CONTEXT.md` §1, 13:38 §f).

## STATE IN 10 LINES

1. Best public **0.954** = P35 exp57b (x138 + DaughterNet insertion); NOT a finals candidate under R5 (L35 in (6.72, 7.73] h, 7.5 h unprovable) - `DECISIONS.md` §1 P35; `CONTEXT.md` l.1801-1810.
2. Base = **x138** (P34 exp56 verbatim = 0.953, L34 <= 6.46 h, rule R1); branch A (R2: insertion stays in F1) - `CONTEXT.md` l.1797-1805.
3. Rank #151 of 3,905 at 18:08; silver ~rank 195 (end of 0.954 block), bronze ~390 (inside 0.953) - `CONTEXT.md` l.1844-1849.
4. Running now: P36 = exp57 v1 diagnostic (PENDING at 18:28:59Z) - `experiments/lb_poll/poll.log` l.315; exp60 lab shards A/B - `research/wf_ideas_v4/final.notes.md` 18:08.
5. Next submit: **K2 = exp58** (x138 + safetail + lowrefine + insertion), 18/18 dummy gates, pre-approved for **00:01 26 Sep** - `CONTEXT.md` l.1817-1836.
6. Finals now: F1 candidate = K2 (after R3/R5); F2 = exp52 (0.950) by §f until the user OKs AMENDMENT f2 (F2 = twin exp58n) - `DECISIONS.md` §2; `CONTEXT.md` l.1887-1895.
7. Decision points: P36 R4 read (~23:48 25 Sep); K2 latency + score 07:00-10:00 26 Sep (R3, R5); user OKs ~09:00 26 Sep; K3 slot S4 10:00-13:00 - `WATCHLIST.md` W14-W25.
8. Cutoffs: R8 no new mechanisms after 27 Sep 12:00; S12 consolidation 28 Sep 12:00; after 29 Sep 02:00 emergency repeat only - `CONTEXT.md` l.1671-1672; `WATCHLIST.md` T03-T08.
9. Retraining is refused until after 29 Sep (R9); only 1 of 10 lab gains transferred to LB - `CONTEXT.md` l.1673-1676; `FACTS.md` §7.
10. 37 submissions so far (36 probes + 1 duplicate) - `research/wf_ideas_v4/FINAL_REPORT_v4.md` §2.

## WHERE THINGS ARE

Knowledge base (`research/KNOWLEDGE/`, written only by `experiments/workflows/biohub-curator.js`):
- `research/KNOWLEDGE/INDEX.md` - this page: state, map, top ideas, top alerts.
- `research/KNOWLEDGE/IDEAS.md` + `research/KNOWLEDGE/ideas.json` - 211 ideas I-001..I-211 in 12 clusters, status + sources; ORPHANS at the end.
- `research/KNOWLEDGE/FACTS.md` - verified facts (metric, data, LB, runtime/N, rules, models, lab->LB transfer) + contradictions C-01..C-18.
- `research/KNOWLEDGE/DECISIONS.md` - all probes P01..P36 with rule used, current finals table, R1-R10 status.
- `research/KNOWLEDGE/WATCHLIST.md` - OVERDUE / NEXT 24 H / LATER / insights at risk (W, T, I IDs).
- `research/KNOWLEDGE/CHANGES.md` - delta per curation. `research/KNOWLEDGE/_curation/v4/` - curator logs and JSON answers.

Key sources (repo root):
- `CONTEXT.md` - single source of truth; newest dated entries at the end of §14 (before "## 9. Literature", l.1896); PRE-REGISTRATION v3 l.1576-1736; ADDENDUM L + AMENDMENT f2 l.1850-1895.
- `experiments/RESULTS.md` - every LB probe with score; `experiments/lb_poll/poll.log` - 10-min submission poll (latency proof for R5).
- `experiments/*/probe.json` - what each kernel changed; `experiments/exp58_x138_safe_lowref/`, `experiments/exp58n_x138_safe_lowref/` - K2 and the f2 twin.
- `experiments/runtime_step0/step0.md` - hidden-N bound and K2 latency forecast; `experiments/exp60_trainlab/` - x138 train lab (T9 readout).
- `tools/dummy_gates.py`, `tools/trainlab.py` - dummy-gate checks and lab gates (ADDENDUM L not yet coded, W01).
- `research/wf_ideas_v4/FINAL_REPORT_v4.md` - research round 1 plan and the morning OK list (§5); `research/wf_ideas_v3/FINAL_REPORT.md` - pre-reg source, slot table.
- `research/wf_ideas_v3/TASK_*.md`, `PROMPT_FRIEND_A.md`, `PROMPT_FRIEND_C.md`, `TEAM.md` - task cards and roles (some stale, WATCHLIST W03, I14).
- `research/browser_research_2026-09-24*.md`, `research/discussions_summary.md`, `research/survey_*.md` - external intel.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-001 | safetail (C01): repair deadline + gated fail-soft insertion (inside K2) | in-plan; read K2 by R3/R5 | `IDEAS.md` RUN; `CONTEXT.md` l.1817-1829 |
| I-071 | forkmid (K3): drop safe forks with midpoint offset >= 4.5 um | in-plan; score exp60 with old gate + L3 | `IDEAS.md` DIV l.127 |
| I-073 | forkblob (L4): drop a safe fork whose daughters sit on one blob | in-plan; patch + trainlab arm NOT built; R3 class needs OK | `IDEAS.md` DIV l.129 |
| I-074 | DeepCenter safe-div threshold on 6bba (K3b) | in-plan; exp60 arc, gates L1+L2; expected "no" | `IDEAS.md` DIV l.130 |
| I-090 | F2 = no-insertion twin exp58n (amendment f2) | built; needs OK, dummy `--insertion 0`, slot S3 | `IDEAS.md` FINALS l.154 |
| I-011 | A6: K1 (exp58t) in next slot if K2 errors | in-plan; needs morning OK | `IDEAS.md` RUN |
| I-158 | tempfuse (K4) | at-risk orphan; build by 26 Sep 12:00 or record "K4 dropped, S6 empty" | `IDEAS.md` INFER l.246 |
| I-081 / I-072 | DaughterNet precision veto on safe forks / float-coord divgate re-audit | strict orphans; free exp60 T9 arms or close in CONTEXT | `IDEAS.md` ORPHANS |

## TOP ALERTS (deduplicated from the three curators, `research/KNOWLEDGE/_curation/v4/*.json`)

1. [now] ADDENDUM L2/L3/L4 gates are not in `tools/trainlab.py` (l.578-617); code them before the first exp60 `score` - `WATCHLIST.md` W01.
2. [now] P36 R4 rule "ignore if L35 > 7.5 h" is undecidable (L35 in (6.72, 7.73]); write the reading before P36 scores - `WATCHLIST.md` I10; `DECISIONS.md` §3 R4.
3. [now] K2 goes at 00:01 26 Sep with no scheduled-submit script in git; keep the poller alive 07:00-08:30 (COMPLETE by 08:01 = insertion gate did not fire; R5 by 09:31) - `WATCHLIST.md` W16, W19.
4. [now] forkblob patch + trainlab arm not built; must pass its lab gate before R8 or be recorded as dropped - `WATCHLIST.md` W11; `IDEAS.md` I-073.
5. [today] Morning OK package ~09:00 26 Sep: f2, L1/L3, forkblob as R3, A6 K1 fallback, time trigger; original rules decide until then - `research/wf_ideas_v4/FINAL_REPORT_v4.md` §5; `WATCHLIST.md` W21.
6. [today] Dummy-gate code missing for the twin (`--twin`) and K3/K3b gates 4-5 - `WATCHLIST.md` W12, W13.
7. [today] Admission table not started; untracked `experiments/ext_corwin-biocel-aux/`, `experiments/ext_y3uanm-secondary-ft/`; friend A card stale, Task 0 reply overdue - `WATCHLIST.md` W02-W05.
8. [before-finals] R7 forbids DIVINS_DUMP=1 in submissions, but default F2 exp52 carries it; note R7 = new builds only - `FACTS.md` C-16.
9. [before-finals] Do not submit K3b without the one-blob share of added forks (24% of x138 forks are one-blob) - `WATCHLIST.md` I01.
10. [before-finals] Close or run orphans I-204 (density quartiles), I-205 (kaggle_lab.py), I-207 (stage resume), I-035 (C09 scale gate) - `IDEAS.md` ORPHANS.
11. [before-finals] Never tick exp56 or two identical-component files; reminder 29 Sep 12:00 - `WATCHLIST.md` T09-T10; `CONTEXT.md` l.1735-1736.
12. [info] Stale lines: `experiments/RESULTS.md` l.58 P25 PENDING (= 0.946); `CONTEXT.md` §4 l.45 edge-J weighting; §11a noise +-0.003; quota "unverified" l.1746; `TEAM.md` 0.97 - `FACTS.md` C-01, C-06, C-04, C-17; `WATCHLIST.md` W06.

## HOW TO USE

- "What is the score / what did probe N change / why was it dropped?" -> `DECISIONS.md` §1 (then `experiments/RESULTS.md`, `experiments/<exp>/probe.json`).
- "Which file do we tick as F1/F2, is it admissible?" -> `DECISIONS.md` §2 + `CONTEXT.md` §f l.1707-1736 and f2 l.1887-1895.
- "Which rule decides this score?" -> `DECISIONS.md` §3 (R1-R10), text in `CONTEXT.md` l.1576-1736.
- "Was idea X tried? What happened?" -> search the alias in `IDEAS.md` / `ideas.json` (aliases column).
- "Is claim X true (metric, N, limits, weights)?" -> `FACTS.md`; conflicting statements -> `FACTS.md` CONTRADICTIONS.
- "What must happen next / what is overdue / what might we forget?" -> `WATCHLIST.md`.
- "What changed since the last curation?" -> `CHANGES.md`. Anything newer than 18:30 25 Sep -> tail of `CONTEXT.md` §14 and `experiments/lb_poll/poll.log`.
