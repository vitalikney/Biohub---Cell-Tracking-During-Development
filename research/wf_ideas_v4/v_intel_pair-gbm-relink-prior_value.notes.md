# v_intel pair-gbm-relink-prior - VALUE/TRANSFER skeptic notes (25 Sep 2026, ~17:30 UTC)

- 25 Sep: output JSON absent -> fresh run.
- Source: experiments/ext_corwin-biocel-aux/pair_ship.py docstring (Kaggle dataset corwin1979/biocel-aux-4d9e2c17, CC0, 19 Sep).
  Arm A = deployed relink replay WITHOUT gap-close / safe-div / short-track filter; fidelity vs champion dJ -0.015452.
  B_b16 dJ_edge +0.001687 (44b6 +0.0006 / 6bba +0.0019), LOEO +0.001702; vendor-prob control -0.000104.
  +98 TP / -144 FP over 199 films (126k positive pairs) -> ~0.5 TP and ~0.7 FP per film.
- OOF/LOEO is out-of-fold for the BOOSTER only. The node sets and positions it scored come from a detector trained on
  all 199 train films (in-sample world). Same trap as our edge filter (+0.016 local, 0 on LB, probes 29/30;
  memory project-edge-filter-finding). The ambiguity columns n_cand_*, rank_*, ratio_* depend on the density of false nodes,
  and the train world has fewer of them than the hidden test.
- Redundancy with x138: DIFF.md l.69/102: x138 relink already uses a flow predictor (FLOW_MODE seed, K12, R40), and the relink cost
  `motion = |target - predicted|` (cell06_ker11_keep.py:718-723 has the same form) is already the flow residual = the booster's
  strongest column res_norm. The only new information is in the density/rank columns.
- Corwin's own kept cell (cell06_ker11_keep.py, same 19 Sep bundle) has flow relink ON but NO pair scorer wired in
  (grep PAIR_SCORER/pair_edge_probs: only in pair_ship.py/pair_features.py). The owner, a 0.965 team, did not ship it. Weak evidence of no DRY gain.
- RESULTS.md B29 (LOEO-44b6, 12 videos): the whole motion relink is worth about -0.0014 adj_edge (relink OFF +0.0014).
  The mass addressable by reweighting relink costs is therefore ~0.001-0.002 of score.
- Metric ceiling: score = sum_v w_v * J_v * (1 - 0.1*(Tp-Tt)/Tt) + 0.1*divJ. dJ_edge <= +0.0017 (arm A, best case)
  x node multiplier ~1.03-1.07 -> <= +0.0018. The division term is untouched (relink edges are single-child).
  On x138 (readmit + gapfill + linefit already recover ends) expected +0.0000..+0.0008. Node multiplier: relink->readmit
  coupling moves Tp; each 1% of Tp = -0.001*J ~ 0.001 of score, the same size as the whole edge gain, and its sign is unknown.
- Gate: plan v3 §e R4 (FINAL_REPORT.md:247-248) needs +0.002 public to enter F1. The ceiling of +0.0018 is below that bar,
  so the best realistic LB read is 0.954/0.955 (= "F2 candidate" or noise) and a slot is spent for an uninterpretable result.
  The lab (exp60) is in-sample for the booster AND the detector, so it cannot validate the idea.
- Verdict: REFUTED under the value/transfer lens.
