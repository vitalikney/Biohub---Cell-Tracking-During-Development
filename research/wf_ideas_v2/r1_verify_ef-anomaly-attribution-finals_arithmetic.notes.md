# arithmetic verify notes (ef-anomaly-attribution-finals)
- Existing efattr.out (research scratchpad) reused. est formula check: 0.95/128883 = 1/135,666 ~= 1/(TP+FP+FN)=1/135,729 -> per FP dropped +0.9/D, per TP lost -1/D; break-even drop precision = 1/1.9 = 0.526. OK.
- all-199 split of est: drops (0.9*1890-234)=+0.0108, adds (495 TP-0.9*152 FP)=+0.0026; total ~0.0136. Normal class +0.00064 (4.7%).
- rel1.8 (med_pre_rel) normal carries +0.00299/0.0136 = 22% (conf 0.00135/0.00787 = 17%); hyp's ">=90% kept" false for its own proposed relative flag.
- CONTEXT l.1336: confirmation ef 44b6 +0.0145, 6bba +0.0169 -> research's '44b6-like ~+0.0015' is a denominator error (used global GT, 44b6 has only ~15% of GT edges).
- parquet per-embryo TP/FP: 44b6 conf 18,763/1,322 (71 vids); 6bba conf 50,845/2,335, sel 52,543/3,189. D_44b6 ~21k, D_6bba ~114k.
- Within-embryo rescale of efattr abs3.5: 44b6 anom 0.00179*135.7k=243 units -> +0.0115, normal -> +0.0006 (total ~+0.012 vs replay +0.0145). 6bba anom 1515 units -> +0.0133, normal +0.0006 (vs replay +0.0169). Anomaly share ~95% in BOTH embryos although 44b6 flags only 6% of transitions (0 frozen): gain density ~+0.002 per 1% anomalous transitions.
- => a flat probe 29 (+-0.002) needs a public embryo with <~1% anomalous transitions (unlike both train embryos) OR non-transfer of the ILP-based rule; the latter is the likelier reading, so 'flat -> private upside 0.3-0.6x' is optimistic.
- Branch (c) worst-case ordinary harm: 6bba-like -(195 drops+0.9*112 adds)/114k = -0.0026 (realistic 0.2 precision drop: -0.001); 44b6-like -(95+0.9*48)/21k = -0.0066 (realistic -0.002). So '<= -0.003 cannot come from ordinary transitions' holds for 6bba-like, marginal for sparse-annotation embryos.
