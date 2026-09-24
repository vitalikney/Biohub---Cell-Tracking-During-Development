# r2 verify dorado-oos-lab ARITHMETIC notes (2026-09-24)
- parquet edges_exp39: TP step q50 1.39, q99 4.57, q99.9 5.77 um -> 6um tracklet cut removes ~0.06% of true edges (not a blind spot).
- ef set (unscored relink, ILP linked elsewhere): 59,408 edges, median len 2.18 um (q90 3.8), only 2,147 evaluable (1,904 FP / 243 TP) -> 6um cut does NOT hide ef edges.
- CONTEXT 16:55: stitch bundle closed with edge filter; float coords probed on LB 25 Sep; coordhead probe 31 pending.
- 44b6 real GT: 71 videos, 20,085 evaluable edges (1,322 FP); ef set on 44b6 = 17,795 edges, only 348 evaluable (299 FP). 6bba: 108,912 eval, ef 1,799 eval (1,605 FP).
- Pseudo-GT 10% unseen arm -> ~10x more evaluable edges on 44b6 than real GT; ef calibration signal (thousands of affected evaluable edges) is resolvable. Drop break-even precision ~J/(1+J)=0.47.
- Decision pool after closures: stitch (closed with ef; unmeasured on exp48), float (LB probe 25 Sep; judge sign-only), fork-midpoint (division term, unjudgeable), coordhead split (pos noise 1.29um) -> live judgeable: frozen ILP-first +0.0013 (ILP-trusting), stitch-on-exp48 (~+0.002?, ILP-trusting), overlap consensus 0-0.004.
- Observed transfer ratio for ILP-trusting lab gains: 0/0.0162, -0.001/0.0095, -0.002/0.0053 -> mean ~ -0.1. Prior true OOS for stitch/frozen ~0 +- 0.001.
- EV of gate (g~N(0,0.001), judge sd 0.0006, ship if >+0.001): E[g*1(ghat>c)] = sg^2/s*phi(c/s) = 1e-6/0.00117*0.277 = +0.00024/item -> ~+0.0005 for 2 items, +overlap consensus maybe +0.0005 -> realistic +0.0003..+0.001 private, 0 public. Claimed +0.001..+0.003 lower bound not supported.
- Calibration uses 2 LB points each +-0.002-0.003 noisy; criterion B tolerates residual optimism up to +0.004 = 2x the items it would judge.
