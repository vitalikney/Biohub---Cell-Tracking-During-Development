# notes value skeptic fullres-watershed-centroid (2026-09-25)
- read BRIEF.md
- read coordhead report (public head 44b6 held-out 1.296 vs none 1.499; 6bba->44b6 retrain 1.45 worse), DIFF s.4 (head reduced nodes -2.8%: multiplier share), v2 polyphase arithmetic (dose-response), r2_critic (ultrack snap, contract.py <=0.0003 share4), forum lines (Eric -0.002 x2, const offset -0.0031, Lime divisions 3um)
- KEY ANALOGUE (research/wf_ideas_v2/r1_research_float-output-coords.json + FINAL_REPORT l.39-50): float output removes ~0.25 um^2 of independent OUTPUT noise (z rounding 0.47 um RMS); lab +0.0018 adj edge J, clean on both embryos (44b6 +0.0020 CI[-0.0002,+0.0044], 6bba +0.0016), division counts identical; LB exp52 = exp51 = 0.950 (tie). The watershed goes ON TOP of floats (lower base var -> convex -> smaller).
- dose-response (v2 polyphase notes l.7): xy jitter var +0.22/axis -> -0.0021/-0.0013 recall; width 0.81 -> -0.0003/-0.0009 (strongly convex).
- reducible variance: head mean 1.525 um (~2.7 um^2 MSE), GT-fitted in-sample floor 1.21-1.28 (~1.8 um^2); gap ~0.9 um^2 of which ~0.39 um^2 = 6bba bias (convention; 6bba->44b6 retrain worsens 44b6 1.296 -> 1.452). w=0.4 blend: residual 0.36*V_h + 0.16*V_c -> perfect centroid captures <=64% of ~0.5 um^2 = 0.32; realistic V_c 0.5-1 um^2 -> net 0.15-0.25 um^2 <= float-output dose -> lab <= +0.001..+0.0018, LB ~0 (float analogue).
- safe encoding keeps only positive fractional part (w=r+clip(v-r,0,0.499)) -> ~half of z sub-voxel info lost; if server rounds, z shifts <=0.6 um (0.37 voxel) mostly vanish; xy survives.
- verified x138 refine_synthetic_midpoint + GAP_REFINE_* knobs exist in exp56 notebook.
- VERDICT: refuted (public realistic 0..+0.001 < +0.002; LB noise 0.003).
