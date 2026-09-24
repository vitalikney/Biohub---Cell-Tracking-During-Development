# arithmetic verify: finals-emax-diversify (started 16:21)
- Probes 29/30 still PENDING (kaggle CLI, ~16:30 UTC); best scored = exp48 0.948.
- Lab per-embryo (GT-edge weighted, l5/l6 CSVs): lp030 44b6 +0.00087 / 6bba +0.00047; ef 44b6 +0.01374 (43/14/14) / 6bba +0.01630 (51/4/9); ef_st_all 44b6 +0.01492 / 6bba +0.01881. W: 44b6 19,826 GT edges, 6bba 53,228.
- Closed form checks: mu .002 s .004 -> E[D+] = .00279 (hypothesis correct). mu=0: E[D+] = 0.399*s -> s .0005 .0002; .00117 .00047; .002 .0008; .003 .0012; .005 .0020.
- Refined sigma formula (k=0.26): ef s=.0029 -> E[D+](mu0)=.00116 (not .0012-.0020); stitch s=.0018 -> .00072; lp s=.0013 -> .00051. At mu=-.0015: ef .00056, stitch .00021.
- The success criterion is tautological: noise floor alone sqrt(.0011^2+.0004^2)=.00117 -> E[D+]=.00047 ~ .0005 threshold; any component heterogeneity pushes it over. Ranking by sigma at mu~0 is fixed by inputs (ef > stitch > lp) under any uniform s scaling.
- Counterfactual: if ef ties (exp49 in 0.947-0.949), Kaggle auto-pick / 'best two public' already = {exp48, exp49} = the diversified pair; incremental premium of the formal rule ~0. Rule adds value mainly in ef-wins case (avoid F1/F2 near-copies like exp49 vs exp49+coordhead variants): ~+0.0005-0.0007.
- Target gap 0.97-0.948 = 0.022; rule caps at ~0.4*sigma <= 0.0012 -> <6% of gap. Zero pipeline cost -> survives as a desk rule, gain overstated at top end.
