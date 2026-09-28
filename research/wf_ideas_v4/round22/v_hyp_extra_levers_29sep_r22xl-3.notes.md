# v_hyp_extra_levers_29sep R22XL-3 (DIVINS_ALPHA close) - skeptic notes, 2026-09-28
- No prior answer file; starting fresh.
- Re-read scratchpad r22lev/an.json (acabaea6 scratchpad). Numbers in the finding match the file:
  cap6_a2 -0.001739 (CI90 -0.00466..+0.00027), cap6_a3 -0.002153 (CI90 -0.00522..+0.0001); 44b6 -0.005028 both; lost TP 3 / 4.
  cap6_a05 = 0.000000 exactly (52 in / 30 out, 1 FP each side). cap6_a0 +0.000588, eligible 1994->7620 (x3.82), 330 vs 286 insertions (+44), adj_vs6 -0.000158.
  cap8 +0.000605 with adj +2e-6 -> a0 is dominated by plain cap8 (same gain, worse adj). cap12_fc2_a05 +0.001335 vs cap12_fc2 +0.001234 with 556 vs 462 insertions = volume.
- Code check tools/div_insert.py l.260-275: score = p_par(u)*p_dau(v)*p_dau(c1)**alpha, caps after scoring -> alpha<1 raises all scores (pc<=1) = more eligible = volume; alpha>1 lowers = fewer. Mechanism consistent with the reading.
- Wording nit: an.py div = [TP, FP, FN]; 44b6 cap6 [2,9,9] -> a2 [1,8,10]. a2 drops ONE OF TWO 44b6 division TPs, not "the only" one. Does not change the action.
- Feasibility: R8 hard line (27 Sep 12:00) is past, and ALPHA is a knob rung banned by v2(6)/W4 AMEND 2. Closing costs nothing. No build, no submit.
- Verdict: not refuted. Info-only close is correct.
