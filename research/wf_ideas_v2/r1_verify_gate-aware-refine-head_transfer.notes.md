# verify transfer: gate-aware-refine-head (started 24 Sep)
- No prior verify JSON. Facts: a_never 1907 FN = 44b6 167 / 6bba 1740 (91% one embryo); top-10 videos (all 6bba) hold 41%; per-track persistent offset (dz sign agrees w/ predecessor 82%) -> annotator/track convention, not image (r1_hyp_detection.notes.md l.2-9).
- z-bias 6bba -0.85 vs 44b6 -0.17 um; per-video q10/q90 -1.34/+0.16.
- B26 precedent: local TTA gains on pilkwang-init models 43-97% memorised views -> UNet features on train are in-sample; head GroupKFold does NOT make UNet features OOF.
- x138 head: trained on 20 TRAIN movies (in-sample detector), 4,136 pairs, held-out-by-movie -10.4% centre error; transferred +0.007 LB -> de-quantisation transfers despite in-sample features.
- exp51 on test movies: final nodes 122,704 -> 119,174 (-2.9%, one video -10.7%) -> node-count multiplier alone ~0.1*0.029*0.95 = +0.0028, i.e. up to ~40% of x138's +0.007 may be multiplier, not localisation. The hypothesis' '10% shrink == +0.007' calibration double counts.
- Verdict: refuted under transfer lens (tail = 6bba-dominated annotator/track convention; head-level GroupKFold does not de-leak UNet features; lab Step B freezes node count so misses multiplier). Residual: plain de-quantiser retrain, embryo-fold gated.
