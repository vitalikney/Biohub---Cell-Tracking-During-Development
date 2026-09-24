# arithmetic verify: oof-edge-scorer-full-candidates (started)
- Marginal values (pooled exp39): D=TP+FP+FN=135,729; FN->TP +1/D=7.37e-6; drop FP +J/D=6.63e-6 (J=0.900). Swap FP->TP pair = 1.40e-5.
- Hypothesis ceiling (225 TP x 7.4e-6 + 170 FP x 6.6e-6 = +0.0028) DOUBLE-COUNTS: the 341 TP (ILP-both-none) and 116 TP (u_diverted in-edges) are already TP; fixing them gains 0. Errors in pockets = 268 + 73 = 341 FP.
- Correct oracle: drop all 341 pocket FP with no TP loss = +0.0023; convert every one to its true TP too = +0.0048 (but FN partners are node-position errors, 2x2 reassign measured 0.0000/-0.00004).
- Relink cost (exp39 nb line 1048) = motion + 0.05*raw - BONUS*prob, in um; sidecar p<0.48 -> max shift 0.48 um (0.72 at BONUS 1.5). Hungarian, no null option; node count unchanged -> multiplier/div terms ~0.
- Parquet near-tie proxy (min(alt_tgt_um, alt_src_um) - len_um): ILP-both-none evaluable 609 -> margin median 5.0 um; margin<0.48: 13 evaluable (4 TP/9 FP); <0.72: 15 (5/10).
- All 128,997 evaluable edges: margin<0.48 -> 332 (199 TP/133 FP); <0.72 -> 450 (288/162). Perfect-oracle flip of all near-tie FP = 133 x 1.4e-5 = +0.0019 (<gate 0.002); BONUS1.5: 162 x 1.4e-5 = +0.0023, only with zero TP losses.
- u_diverted/swap: our link ~1.4 um vs GT-pair geometry 4-9 um -> motion margins of several um >> 0.48; unreachable.
- Realistic: sidecar AUC ~0.85 on near-ties that are 60% TP -> net ~ +0.0000..+0.0003 local.
