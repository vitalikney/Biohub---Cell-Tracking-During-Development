- 2026-09-27T05:47:37Z started skeptic (value+feasibility) for R15FP-1; no prior JSON.
- 05:48Z read CONTEXT tail (l.2575-2834): L5v2 (01:31Z) banned threshold neighbours / class C rungs; 04:59Z post-hoc rungs exp70j/exp70k 'class C unless the user allows'; 05:28Z submits 56598763/56598765.
- poll.log header 05:40:15Z: 42 exp70b, 43, 44 all PENDING. ledger.md: all three safetail 9.5 h, insertion gate open.
- IDEAS I-298 ({V*, #37}) REFUTED by round-12 judge (insertion-hedge logic), next step 'user may still re-choose'. Option (b) of the table = I-298 re-offered; allowed only as a user choice.
- FACTS F-LB-11: bronze ~395, silver ~197; P(max>X) 0.85-0.9 prior. F-MOD-17: lowrefine 12 same-frame pairs, none near GT, effect ~1e-5. F-TRN-03: d1 = d2 = 0 at 3dp.
- Read scratch finals_arith.py (session scratchpad): eps = +-|N(0,1e-4)|, NO mass at eps == 0; d unconditional (not conditioned on V*_C displaying >= 0.955); entry text says ~1e-5 while script uses 1e-4 (inconsistent, harmless unless eps can be 0).
- 05:55Z SENSITIVITY scratch finals_arith_eps0.py (400k draws, same 12 worlds, eps sd 1e-5, P(eps == 0) = p0; eps == 0 means #38 ties the x138 copies and sits after the earlier copies -> counted as cliff):
  p0 0.0: a lowest cliff 11/12 (reproduces finding). p0 0.5: a 8/12, b 4/12; c cliff 0.10-0.30. p0 1.0: b lowest cliff 12/12 (b 0.056-0.196 vs a 0.100-0.200) AND b highest E[max] 12/12 -> (a) is then dominated by (b) whenever V*_C exists.
  => the finding's '(a) lowest or within 0.01 in 12/12' and 'b vs a coin flip' hinge on the unmodelled P(eps == 0). eps == 0 is plausible: lowrefine moves no node near GT (F-MOD-17), safetail is byte-identical unless the deadline hits, d2 = 0 at 3dp.
- Other checks: mechanics (T0-T3, cutoff, V*_C conditions, tie->44, 'never 0.954') are consistent with L9 (9.0 h, COMPLETE, never byte-identical) and need no submit/build; runtime 0; feasible before ~12:30Z. Honest out-of-public evidence for dc0.20 is the 6bba lab -0.0008 (+6 FP forks) and 'tau is embryo-specific' (round 13 (6)): the 'transfer' world (+0.0006) is not supported by any measurement.
- 2026-09-27T05:51:18Z JSON written (refuted=true: mechanics OK, trade-off REASON not robust to P(eps==0)).
- 2026-09-27T05:51:38Z JSON written (refuted=true: mechanics OK, trade-off REASON not robust to P(eps==0); sensitivity script in session scratchpad finals_arith_eps0.py).
