# r1 research finals-emax-diversify notes (started Thu Sep 24 12:38:51 UTC 2026)
- No prior JSON existed; started fresh.
- Clark 1961 (Oper. Res. 9(2):145-162): E[max(X1,X2)] = mu1*Phi(a)+mu2*Phi(-a)+theta*phi(a), a=(mu1-mu2)/theta, theta^2=s1^2+s2^2-2rho s1 s2. Equivalent to E[X1]+E[D+], D=X2-X1~N(mu,theta): mu*Phi(mu/theta)+theta*phi(mu/theta). Hypothesis arithmetic checks: mu .002 sd .004 -> +.00279. Sources: emunix.emich.edu/~aross15/q/papers/bounds_Emax.pdf; arxiv 0910.0115
- Kaggle rule: 2 selected finals, best private counts; default = 2 best public if none selected (kaggle discussions/general/394588, 432319; medium Kaggle Handbook shake-up)
- Metric aggregation (tools/official/metrics.md): adj edge J weight-averaged by w_i=TP+FP+FN; division J pooled.
- Lab cluster bootstrap (scratchpad emax_boot.py; confirmation 135 videos; 44b6 18 units = 11 leak groups + 7 singles; 6bba 64 videos):
  44b6: lp030-exp39 +0.00096 sd .00025; ef-exp39 +0.01468 sd .00366; stitch-ef +0.00117 sd .00040. 6bba: lp +.00048 sd .00015; ef +.01693 sd .00245; stitch-ef +.00248 sd .00040. P(D<0)=0 for all.
  => within-embryo resampling variance of D is tiny vs mu: proposed lab test is DEGENERATE (premium ~0, P(F2<F1)~0 always). Real sigma is transfer (lab->LB) + GPU run noise + embryo effect; must be calibrated from LB history.
- Closed form premium table: mu=0: 0.4*s; mu .002 s .004 -> +.00079; mu .005 s .004 -> +.0002; mu >= 2.5 s -> ~0.
- [resume 2] session resumed after interruption; notes above reused. CONTEXT facts: parity pass (exp46 sha256 == exp39) => our pipeline is DETERMINISTIC run to run; duplicate submission scored identical (exp36). The '+-0.003 identical notebooks' noise was other people's forks/code versions, not our rerun noise. => sigma of D is epistemic (lab->private transfer), not run noise.
- Lab->LB pairs (lab delta, public delta): DivNet veto +0.0022 -> 0.000; leaf prune +0.0006 -> 0.000; DN insertion +0.0019 -> +0.001; hygiene(port12) +0.0011 -> -0.001; relink-off(port12) +0.0053 -> -0.002; axis flip(port12) +0.0214 -> -0.001; gshift ? -> -0.002. Public printed at 3 decimals (rounding sd ~0.0003 per score, 0.0004 per delta).
