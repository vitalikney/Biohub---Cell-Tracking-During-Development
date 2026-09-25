# CHANGES - delta per curation (newest section at the end)

Each curation appends one dated section. IDs (I-, F-, C-, P, W, T, I) are stable across curations; see `research/KNOWLEDGE/INDEX.md`.

## v4 - 2026-09-25 ~18:30 UTC (first curation; baseline, git HEAD 14c339e)

Previous curation: none. `research/KNOWLEDGE/` did not exist before commit 5ea53f9, so everything below is NEW (baseline),
not a delta. Inputs: `CONTEXT.md` up to the 18:20 UTC entries, `experiments/RESULTS.md`, `experiments/lb_poll/poll.log`
(last poll 18:28:59Z), `research/wf_ideas_v2/`, `research/wf_ideas_v3/`, `research/wf_ideas_v4/FINAL_REPORT_v4.md`
(no `research/wf_ideas_v4/round*/` yet). Curator logs: `research/KNOWLEDGE/_curation/v4/`.

Files created:
- `research/KNOWLEDGE/IDEAS.md` + `ideas.json`: 211 ideas I-001..I-211 in 12 clusters (RUN, BASE, LOC, DIV, FINALS, MODEL,
  NODES, INFER, EF, LINK, VALID, TESTSET). Status: refuted 111, lb-tested 37, in-plan 21, deferred-after-deadline 19,
  lab-tested 18, open-untested 5 - `research/KNOWLEDGE/_curation/v4/ideas.json`.
- `research/KNOWLEDGE/FACTS.md`: 7 fact tables + contradictions C-01..C-18 - `research/KNOWLEDGE/_curation/v4/facts.json`.
- `research/KNOWLEDGE/DECISIONS.md`: probes P01..P36, finals table, R1-R10 status - same source.
- `research/KNOWLEDGE/WATCHLIST.md`: W01-W29, T01-T11, I01-I14 - `research/KNOWLEDGE/_curation/v4/watch.json`.
- `research/KNOWLEDGE/INDEX.md`, `research/KNOWLEDGE/CHANGES.md` (this file).

State recorded at baseline (for the next delta):
- Best public 0.954 (P35 exp57b), base x138 (P34 = 0.953), branch A; R1, R2, R5, R6 applied; R3, R4 pending - `DECISIONS.md` §1, §3.
- P36 (exp57 v1) PENDING; K2 = exp58 scheduled 00:01 26 Sep; exp58n twin built, not submitted - `DECISIONS.md` §1 footer, §2.
- F1 candidate K2; F2 = exp52 until AMENDMENT f2 is OK'd - `DECISIONS.md` §2; `CONTEXT.md` l.1887-1895.
- Orphans: strict I-072, I-081, I-204, I-205, I-207; at-risk I-035, I-158 - `IDEAS.md` ORPHANS.

Alerts opened (13 after dedup; full list in `INDEX.md` TOP ALERTS):
- now: ADDENDUM L code missing in `tools/trainlab.py` (W01); P36 L35 reading undecidable (I10); K2 00:01 submit + poller (W16, W19);
  forkblob patch not built (W11).
- today: morning OK package (W21); twin/K3 dummy-gate code (W12, W13); admission table (W04); untracked ext folders (W05);
  friend A card stale (W02, W03); tempfuse build-or-drop (I-158).
- before-finals: R7 vs exp52 DIVINS_DUMP=1 (C-16); K3b one-blob share (I01); close orphans; manual finals, never exp56 (T10).
- info: stale `experiments/RESULTS.md` l.58 (P25 = 0.946, C-17), `CONTEXT.md` §4 weighting (C-01), §11a noise floor (C-06),
  quota "unverified" (W06), `TEAM.md` 0.97 target (C-04).

Alerts resolved: none (first curation).
