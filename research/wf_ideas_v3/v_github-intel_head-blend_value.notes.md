# notes head-blend value skeptic
- 2026-09-25 start; read BRIEF.md
- read coordhead_retrain/out_full_P.log, out_full_Q.log: numbers in idea verified (P 6bba->44b6 +11.99%, 44b6->6bba +0.19%; Q +6.31/+1.32; leak5 OOF none 1.6861 / public 1.5254 / P 1.2375 / Q 1.4278; m7 none 132366 public 132326 P 132473 Q 132444)
- NOTE: 'none' z bias is embryo-specific: 44b6 +0.177, 6bba +0.824 um -> the leak5 gain of P is mostly learning 6bba z offset
- Q out-of-embryo vs none: 44b6 1.3781/1.4990 = -8.1%; 6bba 1.5875/1.7199 = -7.7%. Public in-embryo vs none: -13.5% (44b6), -8.9% (6bba)
- read ext_x138/DIFF.md: x138 notes 20-movie head held-out-by-movie -10.4% (in-embryo), 4-movie head +14.9% worse; exp51 head cut final nodes -2.9% (node-multiplier ~+0.0027 of x138's +0.007 possible, DIFF §4); head on our base +0.002 only (BRIEF)
- read tools/train_coordhead.py: Q = --debias embryo (per-embryo mean target removed), huber 0.5, 120 ep
- computed from out_full_{P,Q}/report.json per_embryo leak5 (pair-weighted over folds):
  44b6: none 1.4990 public 1.2963 Q 1.3624 (+5.1% vs public IN-EMBRYO) P 1.3973 (+7.8%)
  6bba: none 1.7199 public 1.5668 Q 1.5150 (-3.3%) P 1.3942 (-11.0%)
  => the -6.4% leak5 'Q gain' is a 6bba-weighted composite (106k of 126k pairs); on 44b6 Q loses to public even in-embryo
- bias-removed error proxy sqrt(mean^2-|bias|^2) (metric ignores uniform offsets): 44b6 none 1.475 pub 1.288 Q 1.327 (+3.0%); 6bba none 1.466 pub 1.406 Q 1.336 (-5.0%); Q out-of-embryo 44b6 1.344 (+4.3% vs pub-in), 6bba 1.424 (+1.3%): Q's 6bba edge collapses out-of-embryo (1.336 -> 1.424)
- public head vs none on 6bba (dense, where the loss is): only -4.1% bias-removed
- gate (b) (blend <= 0.95 x public on each embryo) needs shift decorrelation cos <= ~0.3 on 44b6 by the convexity bound -> very likely FAIL; P(pass) ~0.1-0.15
- value: blend vs public on unseen embryo ~ -1.3% +- 1.5% distance; slope 0.0005-0.001 LB per 1% => ~+0.001 (range -0.001..+0.003) < +0.002 and < LB noise 0.003 -> REFUTE
- no web needed (all evidence local); no blocked domains tried
