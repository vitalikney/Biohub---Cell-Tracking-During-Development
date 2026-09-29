# R37-RC-B skeptic notes (2026-09-29T09:26:20Z)
- 12:3xZ read: CONTEXT 14:12Z EXP75 PARTNER RULE v2; 09:09Z probe 53 read (0.955 clean); card v5 (round29/finals_card_v5_ru.md) l.38-41 already shows P2 model bronze ~0.75-0.93 / silver ~0.59-0.78 vs P3 ~0.68-0.85 / ~0.39-0.63; step 10 'Числа модели не пересчитывать'.
- R34-RC-B skeptic (round34/v_recheck_r34-rc-b-...json): refuted; allowed an info caption only with standing-prior rows and the user's OK.
- mc26.py structure: CI is ONE shared draw per world (exp75 = b+CI, #37 = b, exp87a = b+C+K+CI) -> P2-P3 = CI + max(C+K,0) - max(C+K+CI,0): pathwise P2>=P3 iff CI>0. Break-even is purely the private CI sign/asymmetry.
- mc37_p2p3.txt grid: 7 of 12 runs use CI_MU 0.0007 (NOT the standing 0.0005): all four sensitivity runs (K_MU, RHO, overfit, qpub0) only at 0.0007. At the standing mean 0.0005: bronze P2-P3 = +.031 (sd .0008), +.008 (sd .0012), -.006 (sd .0015); Eval P3 > P2 at sd .0015 (2.873 vs 2.851e-3).
- 12:4xZ own grid (27 runs, mc26.py unchanged, VPUB=exp87a, standing CI_MU 0.0005): scratchpad r37skep/mc_std_grid.txt.
  bronze P2 vs P3 at CI_MU .0005: sd .0008 P2 ahead 9/9 (+.02..+.05); sd .0012 P2 ahead 8/9 (+.002..+.03; overfit P3 .850 vs .839); sd .0015 P3 ahead 5/9 (overfit, qpub0, seeds 11/23/41), P2 ahead 4/9 by <= .018 -> a tie.
  break-even CI mean: sd .0008 < +.0002 (P2 .762 vs .756 at .0002); sd .0012 ~+.00035-.0004 (.760/.765 at .0003, .776/.774 at .0004); sd .0015 ~+.0006 (.759/.771 at .0004, .773/.779 at .0005).
  silver: P2 ahead in 27/27 and also at CI mean -0.0003 in mc37 (.480 vs .473) -> structural (variance in upper tail), not evidence about CI.
- Text errors in the proposed line: '9 of 12' counts 7 runs at CI_MU .0007 (motivated by reads 2 and 3, incl. exp75's own read) yet is labelled 'стандартный prior'; 'посчитана до чтения exp75' false (runs 09:13-09:35Z after the 09:09Z read; code unchanged, and exp75's display is not a model input); break-even '+0.0003 = треть' is the sd-.0012 low end, ~+0.0004 there and ~+0.0006 (more than half) at sd .0015.
- Verdict: directional claim holds for sd <= .0012 only; action as worded misleading -> refuted (as written), fixed line given.
