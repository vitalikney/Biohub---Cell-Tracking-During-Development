# notes value-skeptic refined-lowdet-pool  2026-09-25T11:03:11Z
- no prior json; read BRIEF.md
- 2026-09-25 ~11:30Z verified CONTEXT.md L1511-1517 (1,337 readmitted / 121,777 raw nodes; leaf prune removed 513 leaves, >=479 readmitted) and L1324-1328 (leaf prune +0.0006 lab on exp39, prob 0.0 on relink pairs).
- coordhead report: public head GT dist none 1.73 -> public 1.60 um (held-out folds), BUT share within 4 um unchanged (0.9390 vs 0.9387): the head does not change 7 um matching; its value is only via post-ILP geometry (relink gate/flow).
- exp56 notebook cell 0: BIOHUB_READMIT_MIN_SCORE=0.965 (= det threshold), READMIT_RADIUS_UM=4, GAPFILL_MIN_SCORE=0.5, GAPFILL_EXCLUDE_UM=2.0, LOWDET 0.3, LEARNED_BONUS 1.0.
  => readmitted nodes are NOT sub-threshold peaks: they are above-threshold peaks the ILP discarded; the head already refined them pre-ILP, readmit re-adds an unrefined int16 copy. Idea's framing half wrong. Gapfill peaks (0.5-0.965) are sub-threshold and out of distribution for the V1284 head (trained on kept peaks).
- cell 5 L1931-1948: learned_edge_probs built from post-ILP edges only; readmitted nodes get new ids -> prob 0 in relink cost (motion + raw_cost*raw - 1.0*prob). Confirmed.
- ceiling: 1.1% readmit nodes x head effect on x138 (+0.007 total) ~ +0.0001 (x2-3 at track breaks -> +0.0003). Idea's own central +0.0003 << +0.002 gate and << LB noise 0.003. REFUTED under value lens.
- no gapfill realised-count found in repo (would need exp56 log -> browser_todo).
