# scan_hypotheses notes (round 2, started 2026-09-25T19:46:16Z)

## 2026-09-25 19:50 UTC - context read
- No round*/REPORT.md existed yet (round2 folder created now); inputs read: CONTEXT.md l.1634-1934, FINAL_REPORT_v4.md, KNOWLEDGE/IDEAS.md (DIV section, orphans I-072/I-081/I-204).
- exp60 dumps ARE on disk (_dl/exp60_a: 28 trainlab npz + 28 divins_dump + edge_cache; _dl/exp60_b: divins_dump + edge_cache, trainlab/ folder MISSING in exp60_b listing at 19:46 UTC). No trainlab score results yet (experiments/exp60_trainlab has no results*).
- DISCIPLINE: I did NOT score / look at fork labels (TP/FP) - only label-free dose statistics, so new arm thresholds can still be pre-registered before labels are seen.
- Fact (tools/div_insert.py candidate_triples, l.225-231 + _candidates): DaughterNet p is computed ONLY for nodes in insertion triples (u with out-degree 1, c1, v). A safe-division fork parent has out-degree 2 in the final graph -> it is never a 'u' -> p(parent) mostly ABSENT in divins_dump. I-081 as "p_par(P)" is not a free CPU arm unless coverage via other roles is high (measured below).
- Fact (lab notebook cell 8, add_safe_divisions_postlink): x138 gates run on the presafe graph whose coords are ALREADY float (head-refined; presafe node z=2.2114..., x=167.69...). So I-072's premise ("recompute with float coords") is moot for the add-time gates; only a re-check on the FINAL (linefit w0.8 smoothed) coords, or a longer horizon (t+3), is new.
- x138 knobs: SAFE_DIV_MAX_UM 4.7, SISTER_MAX 7.2, EXISTING_CHILD_MAX 7.8, DIVERGE_UM 2.25 (1-step, t+2), SYMMETRY_TAU 0.0 (OFF), MUTUAL_NN 1, FRAME_FRAC_CAP 0.008, GLOBAL_FRAC_CAP 0.004, DC veto threshold (lab control) 0.25; ranker score = parent_dist + 0.15*sister_dist.

## 2026-09-25 20:15 UTC - label-free dose on exp60 shard A (28 clips; script in session scratchpad dose.py; NO GT used)
- x138 effective knobs (lab cell 0 env): SAFE_DIV_MAX_UM 9.0, SISTER_MAX 14.0, EXISTING_CHILD_MAX 10.0, SYMMETRY_TAU 0.6 (ON), DIVERGE_UM 2.25 (t+2), FRAME_FRAC_CAP 0.0076, GLOBAL_FRAC_CAP 0.00375, DC 0.25. Cap never binds (safe_division_skipped_cap = 0 on all 28 clips) -> in-stage vetoes do not free slots; post-hoc vetoes = R3-type (nodes untouched).
- 329 safe-division forks (not inserted) on 28 clips (11.8/clip); all clips T = 100 frames; density 48-757 nodes/frame, median 188; 239/329 forks in the dense half; forks per 1000 nodes corr with density -0.22.
- DaughterNet p coverage from divins_dump (triple nodes only): P 60/329 (18%), S-child 74, I-child 72, all three 15/329 (5%) -> I-081 cannot be read from divins_dump; needs OOF p (data_external/l2/kds_out/node_p_oof.parquet, 1.01M exp39 nodes, OOF by fold) matched by position, or a CPU re-score with fold weights (weights_dataset/vitalii_daughternet/fold_0..4.pt; tools/daughternet.score_nodes(model_index=fold) supports OOF).
- Fork geometry on FINAL (linefit) coords, percentiles 5/25/50/75/95: parent->safe 2.15/3.33/4.15/5.07/6.44 um; sister 3.41/5.06/6.78/8.12/9.78; mid 0.75/1.33/1.97/2.99/4.47; cos(children) -0.96/-0.80/-0.50/-0.07/0.55; sym 0.03/0.14/0.27/0.49/0.83; div2 1.58/2.42/2.94/3.49/4.28; div3 2.74/4.20/5.44/6.49/7.57; DC score of safe child 0.25/0.28/0.31/0.37/0.45; ILP edge_prob == 0.0 on 83/329 (25%).
- Doses (share of 329): re-gate on final coords (sym > 0.6 OR div2 < 2.25; x138's OWN thresholds) 99 (30%) [sym 53, div2 63]; div3 < 3.0 29 (9%); cos > 0.25 (insertion rule's cos_max) 50 (15%); young parent (track start <= 3 frames before, not at clip start) 30 (9%); stub branch (either daughter branch ends <= 4 frames, not at clip end) 49 (15%); forkmid (mid >= 4.5) 16 (4.9%); sister <= 5 um 78 (24%, forkblob needs valley too); refractory (parent born by a fork <= 10 frames earlier) 3 (1%) -> refractory idea has no dose, dropped.
- >= 2 of 5 flags {young, stub, cos, regate, div3}: 68 (21%); >= 3: 15 (5%). Flags nearly independent (pairwise overlaps small, e.g. young-stub 5/74, stub-cos 7/92).
- exp60_b: divins_dump + edge_cache on disk, trainlab/ folder MISSING at 19:46 UTC (download incomplete?) -> the main session must check before scoring.

## 2026-09-25 20:40 UTC - GT geometry of the 151 train divisions (tools/official tracksdata, GT geffs only; NO predicted-fork labels) vs x138 safe forks (shard A, 329)
- Share with flag, GT (151) vs predicted safe forks (329):
  cos(children) > 0.25: GT 7 (4.6%) vs pred 50 (15.2%)  [cos>0: 10.6% vs 21.3%; cos>0.5: 3.3% vs 5.8%]  -> ENRICHED 3.3x in predictions
  sister <= 5 um: GT 5 (3.3%) vs pred 78 (24%) -> enriched 7x (supports forkblob / B21 line; GT sister 5/50/95 pct 5.4/10.6/15.3 vs pred 3.4/6.8/9.8)
  mid >= 4.5 um (forkmid): GT 25 (17%) vs pred 16 (4.9%) -> NOT enriched; forkmid's TP risk by geometry is real (lab gate 'removed TP = 0' is essential)
  sym > 0.6: GT 57 (38%) vs pred 16%; div2 < 2.25: GT 71 (47%) vs pred 19%; div3 < 3: GT 52/124 vs pred 9% -> re-gating on final coords (I-072) targets geometry that real divisions HAVE -> TP-hostile; close.
  young parent (track start <= 3 fr before): GT 31 (21%) vs pred 9% -> TP-hostile (annotators start tracks near divisions) -> close.
  stub daughter branch <= 4 frames: GT 66 (44%, sparse annotation truncates GT tracks) -> GT cannot calibrate it; low priority.
  refractory (parent born by a fork <= 10 frames): GT 0, pred 1% -> no dose, close.
- cos > 0.25 AND sister > 5 AND mid < 4.5 (the part not covered by forkblob/forkmid): pred 13/329, GT 0/151.
- forkmid subset: 14 of the 16 mid >= 4.5 forks also have cos > 0.25 -> an antiparallel veto nearly contains forkmid.
- Bayes arithmetic for the cos veto: if TP forks follow GT geometry (4.6% flagged) and evaluable precision p = 0.25, the flagged share 15.2% implies FP flag rate r = (0.152 - 0.25*0.046)/0.75 = 0.187 and vetoed precision q = 0.0115/0.152 = 0.076 << break-even 0.265. With position noise doubling the TP flag rate (9%) q ~ 0.15, still < 0.265.
- DaughterNet OOF p (data_external/l2/kds_out/node_p_oof.parquet via coords_exp39.parquet, nearest node same t): only 76/676 forks have all three roles within 1.5 um (P 184, S 222, I 311 of 676) -> not usable as is; needs CPU re-score with the fold weights (weights_dataset/vitalii_daughternet/fold_k.pt; tools/daughternet.score_nodes(model_index=fold)). Matched p_par(P) pct 5/25/50/75/95 = 0.011/0.068/0.262/0.541/0.924 (n=184).
- exp60_b/trainlab arrived (28 npz) by ~20:30 UTC; full 56-clip dose re-run started.
- Literature: TGMM (Amat 2014, https://github.com/haohaibo/tgmm) uses temporal lineage logic rules incl. short-lived-daughter deletion (I could not verify the exact function name online; treat as unverified).

## 2026-09-25 20:12 UTC (real clock via `date -u`; the two headers above stamped 20:15 / 20:40 were written at ~19:58 / ~20:05 - manual stamp error)
- GT-calibrated DaughterNet thresholds (OOF: each GT crop of data_external/l2/kaggle_eval_crops.npz scored ONLY by the fold model that did not train on its video; weights_dataset/vitalii_daughternet/fold_0..4.pt; 453 crops = 151 parents + 302 daughters, all valid): GT parent p_par pct 5/10/25/50 = 0.057/0.080/0.392/0.750; GT daughter p_dau 0.077/0.104/0.243/0.515; GT triple score p_par*p_dau*p_dau (daughters paired by stem+frame, approx.) 0.0011/0.0029/0.0203/0.1247.
- Predicted x138 safe forks (position-matched OOF p, 76 full triples / 184 parents): triple pct 5/25/50/75/95 = 0.0000/0.0011/0.0118/0.0291/0.1195 (median 10x below GT); p_par(P) 0.011/0.068/0.262/0.541/0.924 -> a veto p_par(P) < 0.057 (GT 5th pct) would hit ~20-25% of forks vs 5% of real divisions (enrichment ~4x; the position-matched p is approximate).
- Main session: experiments/exp60_trainlab/results_forkblob.md generated 20:04 UTC: "Harm gate: pass = **False**" (headline only read; I deliberately did not read per-fork rows so my arm thresholds stay uncontaminated).

## 2026-09-25 20:22 UTC - full 56-clip dose (dose_all.py; label-free) + density quartiles
- 676 safe forks on 56 clips; cos > 0.25: 113 (16.7%); sister <= 5: 160 (23.7%); mid >= 4.5: 40 (5.9%); cos > 0.25 AND sister > 5 AND mid < 4.5: 25. SELECTION 345 forks / 59 flagged; CONFIRMATION 331 / 54; 44b6 235 / 32; 6bba 441 / 81.
- Density quartiles (nodes/frame of the control final graph; edges 83.7 / 160.7 / 258.8; 14 clips each): GT divisions 25 / 24 / 23 / 27 (flat); safe forks 55 / 149 / 209 / 263 (forks per GT division 2.2 / 6.2 / 9.1 / 9.7); cos-flagged 5 / 31 / 37 / 40; sister<=5 14 / 37 / 44 / 65; mid>=4.5 1 / 12 / 10 / 17. -> fork supply scales with density, GT events do not: FP-fork mass sits in Q1-Q3.

## 20:22 UTC - final answer written to scan_hypotheses.json (8 findings: R2S-1..R2S-8)
