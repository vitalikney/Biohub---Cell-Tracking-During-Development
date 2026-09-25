# INDEX - Biohub cell tracking knowledge base (team D: Discipline)

Curation 2, state as of 2026-09-25 ~20:55 UTC, git HEAD da154cb (+ untracked `research/wf_ideas_v4/round2/`); previous: v4 (18:30 UTC, 14c339e). All times UTC. Every line cites its source.
Deadline 29 Sep 23:59; finals ticked MANUALLY by the user by 29 Sep 20:00 (`CONTEXT.md` §1, 13:38 §f l.1707-1736).

## STATE IN 10 LINES

1. Best public **0.954** = P35 exp57b (x138 + ungated DaughterNet insertion). It is NOT a finals candidate under R5 (L35 in (6.72, 7.73] h) - `DECISIONS.md` §1 P35, §2.
2. Base = **x138** (P34 exp56 = 0.953, L34 <= 6.46 h, R1); branch A (R2: the insertion stays in F1) - `CONTEXT.md` l.1797-1805.
3. Rank #157 of 3,908 at 19:46; the silver line (~rank 195) now falls INSIDE the 0.954 block, 38 ranks below us - `research/wf_ideas_v4/round2/report.json` new_facts (1)-(2); `FACTS.md` F-LB-02/03.
4. The exp60 T9 lab read (20:35) gave **no K3** (forkmid: 1 evaluable FP removed, the gate needs >= 3) and **no K3b** (DeepCenter t* = 0.30 fails every gate); forkblob FAILED at 20:05; K4 tempfuse was DROPPED - `CONTEXT.md` l.1918-1937; `DECISIONS.md` §1b G01-G06.
5. So **F1 = K2 = exp58** (x138 + safetail + lowrefine + insertion) is very likely final. It passed 18/18 dummy gates and is pre-approved for **00:00:30-00:05 26 Sep** - `CONTEXT.md` l.1817-1836, l.1934-1937; `WATCHLIST.md` W16.
6. F2 = exp52 (0.950) by §f until the user OKs AMENDMENT f2 (F2 = no-insertion twin exp58n). The twin's dummy was pushed ~20:35 and is not read yet - `CONTEXT.md` l.1887-1895, l.1935-1937; `DECISIONS.md` §2.
7. Running now: P36 = exp57 v1, PENDING at 20:42:40Z (L > 4.40 h) and INFO ONLY; the exp58n twin dummy; the LB poller + runtime ledger - `experiments/lb_poll/ledger.md`; `CONTEXT.md` l.1904-1906.
8. Decision points: twin dummy read ~21:30; P36 7.5 h mark ~23:48; quota check 00:05; K2 COMPLETE by 08:01 and R3/R5 read 06:30-10:00; user OKs ~09:00 26 Sep - `WATCHLIST.md` W12/W17, W14-W21.
9. Cutoffs: R8 (no new mechanisms) 27 Sep 12:00; S12 consolidation 28 Sep 12:00; emergency repeat only after 29 Sep 02:00; retraining refused until after 29 Sep (R9) - `CONTEXT.md` l.1671-1676; `WATCHLIST.md` T03-T08.
10. Ideas ledger: 216 ideas; refuted 124, lb-tested 37, lab-tested 20, deferred 19, in-plan 16, open-untested 0 - `IDEAS.md` header.

## WHERE THINGS ARE

Knowledge base (`research/KNOWLEDGE/`, written only by the curator workflow `experiments/workflows/biohub-curator.js`):
- `research/KNOWLEDGE/INDEX.md` - this page: state, map, top ideas, top alerts.
- `research/KNOWLEDGE/IDEAS.md` + `research/KNOWLEDGE/ideas.json` - 216 ideas I-001..I-216 in 12 clusters, with status and sources; ORPHANS section at the end (l.345); `ideas.json` `meta.curations` logs every status change.
- `research/KNOWLEDGE/FACTS.md` - verified facts (§1 metric ... §7 lab->LB transfer) + CONTRADICTIONS C-01..C-23 (l.126).
- `research/KNOWLEDGE/DECISIONS.md` - probes P01..P36 (§1), lab-gate decisions G01-G06 (§1b), finals table (§2), R1-R10 status (§3).
- `research/KNOWLEDGE/WATCHLIST.md` - OVERDUE / NEXT 24 H / LATER / INSIGHTS AT RISK (W, T, I IDs).
- `research/KNOWLEDGE/CHANGES.md` - delta per curation. `research/KNOWLEDGE/_curation/v4/`, `research/KNOWLEDGE/_curation/2/` - curator logs and JSON answers.

Key sources (repo root):
- `CONTEXT.md` - single source of truth; newest entries at the end of §14, just above "## 9. Literature" (l.1938). PRE-REGISTRATION v3 l.1576-1736; ADDENDUM L l.1850; AMENDMENT f2 l.1887-1895; exp60 read l.1918-1937.
- `experiments/RESULTS.md` - every LB probe with score (rows l.33-69). `experiments/lb_poll/poll.log` - 10-min poll; `experiments/lb_poll/ledger.md` - latency bounds, R5 and the family of each submission.
- `experiments/*/probe.json` - what each kernel changed. `experiments/exp58_x138_safe_lowref/` = K2; `experiments/exp58n_x138_safe_lowref/` = f2 twin; `experiments/exp58t_x138_safe/` = K1 fallback.
- `experiments/exp60_trainlab/results.md`, `experiments/exp60_trainlab/results_forkblob.md` - x138 train lab (T9 verdicts). `experiments/runtime_step0/` - hidden-N bound and K2 latency forecast.
- `tools/trainlab.py` (lab gates + ADDENDUM L), `tools/forkblob_lab.py`, `tools/dummy_gates.py` (no `--twin` mode yet), `tools/runtime_ledger.py` (A5 ledger), `tools/build_probe_kernel.py` (kernel builder, FLOATOUT_CHECK l.1315-1362).
- `research/wf_ideas_v4/FINAL_REPORT_v4.md` - round 1 plan; its §5 morning OK list is STALE. `research/wf_ideas_v4/round2/report.json` - round 2 (ADDENDUM M proposal, closures R2-A7; untracked, REPORT.md never written).
- `research/wf_ideas_v3/FINAL_REPORT.md` - pre-reg source and slot table; `research/wf_ideas_v3/TASK_*.md`, `PROMPT_FRIEND_A.md`, `PROMPT_FRIEND_C.md`, `TEAM.md` - task cards and roles (friend A card stale, `WATCHLIST.md` W03).
- `research/browser_research_2026-09-24*.md`, `research/discussions_summary.md`, `research/survey_*.md` - external intel.

## TOP OPEN IDEAS (from `research/KNOWLEDGE/IDEAS.md`)

| ID | Idea | Status / next step | Source |
|---|---|---|---|
| I-001 | safetail (C01) inside K2: repair deadline + gated fail-soft insertion | in-plan; submit 00:00:30 with `-m "probe 37: exp58 ..."`, then read by R3/R5 | `IDEAS.md` l.40; `WATCHLIST.md` W16 |
| I-090 | F2 = no-insertion twin exp58n (AMENDMENT f2) | dummy pushed; add `dummy_gates.py --twin` (a)-(f), read, ask the f2 OK ~09:00, S3 submit | `IDEAS.md` l.66; `round2/report.json` R2-A3 |
| I-011 | A6: K1 (exp58t) in the next slot if K2 errors | in-plan; needs the morning OK | `IDEAS.md` l.50 |
| I-215 | floatout ported to x138 as a fail-soft F1 rider (new) | proposed for the morning OK; fail-soft check + FORCE_FAIL test by R8; S12 only; ~+0.0001 private | `IDEAS.md` l.121; `WATCHLIST.md` W33 |
| I-216 | ADDENDUM M (M1-M6) from round 2 (new) | at risk: not in CONTEXT; record M4-M6 as closures, M1-M3 as moot/post-hoc | `IDEAS.md` l.331, ORPHANS |
| I-089 / I-091 | Rank-aware finals rule; exp52 as F2 fallback | in-plan; the user ticks F1/F2 by 29 Sep 20:00 | `IDEAS.md` l.65, l.67 |
| I-136 | P36 = exp57 v1 (leaf prune + ungated insertion) | PENDING; info only, no rider | `IDEAS.md` l.227; `CONTEXT.md` l.1904-1906 |
| I-035 | Head cascade / scale pre-gate (C09) | at-risk orphan; run only if the cloud session is idle before R8, else close in CONTEXT | `IDEAS.md` l.109, ORPHANS |

## TOP ALERTS (deduplicated from the three curators, `research/KNOWLEDGE/_curation/2/*.json`)

1. [now] Submit K2 at 00:00:30-00:05 26 Sep: v1, no re-push. The `-m` message must START with `probe 37: exp58` (with exp56/exp57b first, the ledger would class it as x138, 7.5 h). Then run `tools/runtime_ledger.py --k2 <ref> --family <ref>=safetail` and check for "safetail (9.5 h)" - `WATCHLIST.md` W16; `round2/report.json` R2-A4.
2. [now] The twin dummy returns ~21:20-21:40, but `tools/dummy_gates.py` has no `--twin` mode. Add checks (a)-(f) before reading it - `WATCHLIST.md` W12/W17; `round2/report.json` R2-A3.
3. [today] ADDENDUM M is not in CONTEXT, and T9 was read first (20:35 vs round 2 at 20:42). Record M4-M6 as closures (ANTIPAR, DNVETO, break-even FP:TP >= 7.7, dummies prove plumbing only, K4 reopen clause) and M1-M3 as moot/post-hoc. Commit the untracked `research/wf_ideas_v4/round2/` and save its REPORT.md from report.json - `WATCHLIST.md` W30, W31; `FACTS.md` C-21; `IDEAS.md` I-216.
4. [today] Closures due in CONTEXT by 26 Sep 12:00: I-072, I-081, I-212, I-213 (they exist only in round2/report.json R2-A7) - `IDEAS.md` ORPHANS; `WATCHLIST.md` W31.
5. [today] Rewrite the morning OK list: f2 + S3 twin submit; optional floatout (I-215); K1 fallback (I-011). Drop L3 and forkblob, and drop L1/L2 too (moot: t* = 0.30 fails under every reading; the ideas curator still listed a K3b re-read at P ~0.1). `research/wf_ideas_v4/FINAL_REPORT_v4.md` §5 is stale - `WATCHLIST.md` W21; `experiments/exp60_trainlab/results.md` l.76-80.
6. [now] Friend A card still asks for exp60 shard B (done at 20:05) and a tempfuse test (K4 dropped); his Task 0 reply is overdue. Add a cancellation block to `PROMPT_FRIEND_A.md` - `WATCHLIST.md` W02, W03.
7. [today] At 00:05 check the GPU quota reset (unconfirmed; ~5 GPU-h left otherwise) and record that hidden reruns do not use quota (CONTEXT l.1746 says "unverified") - `WATCHLIST.md` W06, W15.
8. [today] Admission table not started; `experiments/ext_corwin-biocel-aux/` and `experiments/ext_y3uanm-secondary-ft/` untracked; `experiments/RESULTS.md` has no exp60 lab row - `WATCHLIST.md` W04, W05, W35.
9. [today] Stale pointers: memory `project-lb-probe-approval` still says the exp52/53/54 batch (point it to PRE-REG v3 + ADDENDUM L/M + f2); `TEAM.md` still has the 0.97 target; the CONTEXT rank line still says #151 at 18:08 - `WATCHLIST.md` W34, W22; `FACTS.md` C-04.
10. [before-finals] FLOATOUT_CHECK is a bare assert (violates R7 fail-soft). Any floatout build needs the user's OK, a fail-soft wrapper and a FORCE_FAIL test, and rides only in S12 - `WATCHLIST.md` W33, I17; `IDEAS.md` I-215.
11. [before-finals] Close I-035 in CONTEXT before R8 (27 Sep 12:00) unless it is run; never tick exp56 or two files with identical components; remind the user at 29 Sep 12:00 - `IDEAS.md` ORPHANS; `WATCHLIST.md` T09-T10.
12. [info] P36 reaches 7.5 h ~23:48: log the score and latency as info; no leaf-prune rider - `WATCHLIST.md` W14; `FACTS.md` C-20. DeepCenter t* = 0.30 (8 FP forks removed, 0 TP lost, but nodes change) is post-hoc: do not act before 29 Sep - `WATCHLIST.md` I19.

## HOW TO USE

- "What is the score / what did probe N change / why was it dropped?" -> `DECISIONS.md` §1 (then `experiments/RESULTS.md`, `experiments/<exp>/probe.json`).
- "Which lab gate closed forkmid / K3b / forkblob / ANTIPAR?" -> `DECISIONS.md` §1b, then `experiments/exp60_trainlab/results.md`.
- "Which file do we tick as F1/F2, is it admissible?" -> `DECISIONS.md` §2 + `CONTEXT.md` §f l.1707-1736 and f2 l.1887-1895.
- "Which rule decides this score?" -> `DECISIONS.md` §3 (R1-R10); text in `CONTEXT.md` l.1576-1736; latency bounds in `experiments/lb_poll/ledger.md`.
- "Was idea X tried? What happened?" -> search the alias in `IDEAS.md` / `ideas.json` (aliases column).
- "Is claim X true (metric, N, limits, weights)?" -> `FACTS.md`; conflicting statements -> `FACTS.md` CONTRADICTIONS.
- "What must happen next / what is overdue / what might we forget?" -> `WATCHLIST.md`.
- "What changed since the last curation?" -> `CHANGES.md`. Anything newer than 20:55 25 Sep -> the tail of `CONTEXT.md` §14 and `experiments/lb_poll/ledger.md`.
