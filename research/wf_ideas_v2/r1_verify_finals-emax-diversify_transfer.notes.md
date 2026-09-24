# verify transfer: finals-emax-diversify (started Thu Sep 24 16:20:16 UTC 2026)
- No prior verify JSON; fresh. Kaggle CLI 24 Sep: probes 29/30 still PENDING; exp48 0.948 best; current ticked finals exp29+exp39.
- Metric node penalty is LINEAR & symmetric: adj = J*(1 - 0.1*(Tpred-Ttrue)/Ttrue) (tools/official/metrics.md l.40-49) -> node drop dN% gives ~ +0.1*dN*J regardless of over/under count.
- exp51 coordhead: final nodes 122,704 -> 119,174 (-2.9%, mostly one 44b6 video -10.7%) -> multiplier alone ~ +0.1*0.029*0.91 ~ +0.0026 ~ 37% of x138's +0.007. Refined rule applies the J-vs-multiplier screen only to F2, NOT to F1's coordhead -> transfer hole.
- Refined sigma formula: term 0.3*k_eff*|lab| vanishes when k~0 (in-sample-net comps) -> ef sigma = sqrt((1.5*.0017)^2+.0011^2+.0004^2) ~ .0028, contradicts research note 'sd >= 0.3*|lab mu|' (~.0048).
- Embryo heterogeneity from 2 TRAIN embryos (44b6 = one recording, 11 leak groups) = 1-df estimate, networks in-sample on both -> compressed; 95% CI on sigma from 1 df ~0.45x..32x. Sigma is assumed, not measured.
- E[D+] scenarios (ef public +0.004, private mu .003): A = ef in both, F2 adds stitch+cap -> .00107. C = F2 keeps exp48(+coordhead)+cap WITHOUT ef -> .00047 (s_ef .0028), .00106 (s_ef .0048), .00147 (s_ef .006). ef marginal (+0.002 pub): A .00107 vs C .00093/.00161. => 'ef in both finals' flips with the in-sample sigma the refined formula zeroes out.
- Verdict: not refuted (desk rule, lab gains discounted to k~0, public-probe-driven), but 3 transfer repairs needed. Public gain 0.
