# verify transfer: div-cap-private-J (started)
- confirmation per-video s_c4_t0.5 vs exp39: node count delta 0 on all videos (no node-multiplier effect); edge TP/FP/FN +5/+7/-5; 44b6 gain = ONE TP (44b6_d754aa59, dS +0.126), 3 FP on 3 other videos; 6bba +3TP/+8FP (14 changed videos total). 466 insertions, 124 steals.
- CONTEXT: DaughterNet OOF = 5 folds by 44b6 LEAK GROUP (not by embryo) -> every held-out video's model saw other videos of the SAME embryo; no embryo-held-out precision estimate exists (B32 planned 2 folds by embryo; L2 did not).
- Shipped exp48 = cap 4, alpha 1, ENS threshold 0.4 ~ OOF 0.5 (calibration note 03:10) -> s_c4_t0.5 is already the shipped config; refined 'threshold -0.1' = OOF 0.4 is untested.
- Transfer chain for this exact stage: selection +0.0058 -> confirmation +0.0019 (33%) -> LB +0.001 (+-0.001 rounding of two 3-dec scores).
- Selection cap 4->6 (t0.6): +50 insertions, 0 TP/+2 FP, -0.00034. Precision decreasing in rank, measured in-sample graph.
- Edge side of insertion on confirmation: +5 TP/+7 FP (steals + 2nd daughter edges) -> already net-negative in-sample; steal gate uses in-sample edge_prob <= 0.3.
- 44b6: 1 TP total = one event on one video (d754aa59); crops overlap one recording -> per-embryo marginal precision on 44b6 is n~1-4, not estimable.
- Node count unchanged by insertion (0 on all 135 videos) -> no node-multiplier artefact (only positive transfer point).
- FINAL JSON written (refuted=true)
