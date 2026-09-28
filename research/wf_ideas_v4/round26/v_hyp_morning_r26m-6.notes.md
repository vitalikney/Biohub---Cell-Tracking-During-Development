# v_hyp_morning R26M-6 skeptic (DIS 2.25 old-lab prior) - 2026-09-28
- No prior v_hyp_morning_r26m-6.json; started fresh.
- Arithmetic check: f(S)=f2+b(S-2)+a(S-2)^2 through exp13 1/2/3 = 0.9149/0.9158/0.9110 -> a=-0.00285, b=-0.00195;
  f(2.25)-f(2)=-0.00067, f(1.75)-f(2)=+0.00031. Correct.
- Transfer: CONTEXT l.164 row A9 'ILP div weight 0.6 / disappearance-appearance sweep (exp12/exp13) | v2.1 config; does not transfer (A5)'.
  exp13 ran at ILP div 1.2 (scan_recheck.notes l.4: 'default thr 1.2 > max p -> no ILP forks'); tonight's files use
  ILP_DIVISION_WEIGHT 0.4 (exp89q probe.json l.14) -> fork threshold Div-A differs, different ILP regime.
  Old pipeline output ILP edges directly; current filter_output_graph replaces ALL ILP edges by motion relink
  (knobarms_28sep/v_2.notes.md) -> D acts only via node set + bonus pairs now. Mechanism differs.
- Same exp13 sweep: d2/a0.5 (S=2.5 via appearance) = 0.9216 (+0.0058) -> the S-curve is confounded by forks; the 3-pt
  parabola interpolated at 0.25 step (0.0007) is below 48-video noise; no evidence of negative sign.
- Action infeasible: exp89l (K+SEC+CI) 'not a file' by the 'cap + 2 levers' depth cap (CONTEXT W4 AMEND 4 11:17Z,
  and 11:2xZ 'K + SEC + CI (exp89l) stays excluded'); no experiments/exp89l folder; would need a new dummy (~0.5 GPU-h
  of ~2.5-3 h left). exp89t: no folder/mention. The DIS-free vs DIS question is already covered by the night
  attribution design (stack vs exp89p isolates DIS) and by scan_hyp_finals' exp89s (K+DIS, no SEC) proposal.
- Verdict: refuted (no new value; prior not transferable per the project's own A9 row; action points to an excluded file).
