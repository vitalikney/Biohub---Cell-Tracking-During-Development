# notes value-skeptic head199-x138-two-arm
- 2026-09-25 ~11:10 UTC start; no prior json found. Read BRIEF.md.
- 11:20 read out_full_P/report.txt, out_full_Q/report.txt, DIFF.md s1/s4, CONTEXT noise/determinism lines.
- Gaussian debias (pooled): leak5 OOF none 1.513 / public 1.427 / P 1.239 / Q 1.264; 6bba->44b6 none 1.478 / public 1.289 / P 1.335 / Q 1.349; 44b6->6bba none 1.501 / public 1.429 / P 1.449 / Q 1.448. Out-of-embryo P worse than public even debiased.
- KEY: per-embryo leak5 (report.json folds[*].eval.per_embryo): on 44b6 P mean dist worse than public in 4/5 folds (1.447/1.374/1.294/1.367/1.318 vs 1.421/1.418/1.234/1.342/1.245) although 44b6 in training. P's 19% gain is 6bba-only (6bba ~1.22 vs ~1.57).
- Per-axis debiased MAE sum (Gaussian per axis): public on 6bba 2.20 vs none 2.14 (public head gives ~0 debiased gain on 6bba); 44b6->6bba P 2.072 vs none 2.079 (0% transfer); 6bba->44b6 P 1.918 vs none 2.039 vs public 1.845.
- Node multiplier: exp51 vs exp48 final nodes -2.9% -> 0.1*0.029*0.91 = +0.0026 ~= whole LB gain +0.002; x138 vs readmit-v1 nodes -2.4% -> +0.0022 of +0.007.
- Pooled per-embryo leak5 OOF (5 folds): 44b6 none 1.499 / public 1.296 / P 1.343 (+3.6% vs public; w/o x138-train 1.338 vs 1.301 +2.9%); 6bba none 1.720 / public 1.567 / P 1.219 (-22%). The headline -19% is 85% 6bba-weighted (106k of 126k pairs) and 6bba-only.
- Sibling verdict v_detector-retrain_coordhead-v2-embryo-robust_value.json also refuted (same debias arithmetic). Consistent.
- Verdict: REFUTE on value (public E ~ 0, below +0.002; private no better). Writing JSON.
