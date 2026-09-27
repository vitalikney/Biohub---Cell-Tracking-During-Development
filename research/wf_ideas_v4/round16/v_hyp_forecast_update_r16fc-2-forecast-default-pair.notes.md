# v_hyp_forecast_update r16fc-2 skeptic notes
- 2026-09-27T08:45Z start; no cached json existed. Source: round16/scan_hyp_forecast_update.json + notes.
- Read CONTEXT l.2324-2334 (26 Sep 16:54Z forecast): it ALREADY said '~250-400 teams end above us (central rank ~320)' and listed
  'the bronze line lands inside the x138-variant crowd above us' as a no-medal path. So the premise 'P(above block) ~ P(medal)'
  is NOT from 16:54Z; it is round15/v_recheck_r15-rc-c (3) ('bronze ~#394 falls inside the 0.953 x138 block (#342-723)... P(above
  block) is close to P(medal)'), which mixes PUBLIC block ranks with the PRIVATE rank of X. The r16 correction is valid arithmetic:
  exact copies share X on private, so X's private rank = 1 + #teams whose better final > X.
- Sanity (my own, no MC): at deadline 110 (>=0.960) + 0.5-0.8 x 410-580 (0.954-0.959) + ~20-100 non-copy 0.953 + ~30 (0.948-0.952)
  -> X+ rank ~365-700 vs bronze ~400. Qualitative claim robust.
- Scratchpad r16/final_runs.txt reproduces the quoted A numbers (overfit .70-.89, mid .46-.70, central .27-.49 P(bronze)).
- GAP: forecast_mc2.py fields have beta >= 0 (overfit 0-0.10) and genuine share g >= 0.10 -> no world where public-selected
  x138 tweaks are net NEGATIVE on private (true-effect prior mean < 0 on an already tuned pipeline; classic shake-up). That world
  puts X+ rank ~250-350 and P(bronze | #37 > X) high -> the 0.55 central and 0.85 upper bound are biased LOW; range skewed.
- Calibration target caveat: private LB shows 3-dp scores; 'rank of the first exact-copy team' is not directly readable when
  variants share the bin. Use X from our own exact-x138 submission's private score (submissions page post-deadline) and count
  teams strictly above it; state the within-bin ambiguity.
- Feasibility: info-only CONTEXT line + read-list item; no build, no submit, no rule change; R1-R10/R8 untouched; I-092 respected
  if labelled illustrative.
- 08:46Z final JSON written (refuted=false with fixes).
