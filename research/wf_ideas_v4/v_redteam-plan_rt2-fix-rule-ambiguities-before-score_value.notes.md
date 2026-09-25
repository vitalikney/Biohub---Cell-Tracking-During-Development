# RT2 value/transfer notes 2026-09-25T17:47:19Z
- Sources read: FINAL_REPORT.md (v3) §e R3/R4/R5/R7, §f fallback chain; CONTEXT.md 13:38 pre-reg, 14:29 T2-T6, 16:20 #35, 16:45 step0, 17:20/17:45 dummy gates; tools/trainlab.py gates() lines ~594-665; memory project-metric-insights + edge-filter finding.
- Premise check (_dl/biohub-exp58-x138-safe-lowref vs _dl/biohub-exp58t-x138-safe logs): readmits 96/677/84/508 = 1365 vs 94/662/84/497 = 1337; nodes after safe-div +1/+31/0/+8; geometric_candidates 123/141/14/230 vs 121/155/13/222; safe-div added 35/6/5/17 = 63 vs 62 (+1 fork). CONFIRMED: lowrefine is a (tiny) set-changer, not coordinate-only.
- Ceiling of lowrefine on the metric (score = adj edge J*(1-0.1*(Tpred-Ttrue)/Ttrue) + 0.1*div_J):
  edge side: +29 edges / ~120k in dummy -> |dJ| <= ~2.4e-4 even if all were TP in annotated regions; realistic |d| < 1e-4.
  node multiplier: +33 nodes/121.8k -> -0.1*2.7e-4*J ~ -3e-5 (bonus side, tiny).
  division: 151 GT events / 199 train videos ~0.76/clip; ~62 predicted safe-div forks per 4 dummy clips (~15/clip) -> div_J small, one fork ~ 0.1*(1/~450) ~ 2e-5.
  Coordinate part: closed line 'float output coords' = tie on LB (exp52 0.950 = exp51) -> coordinate refinement is LB-neutral.
  => true lowrefine effect |delta| ~ 1e-4; public -0.001 display vs #35 is ~pure rounding of #35's in-bin position; P ~0.05-0.12.
- Value of RT2 item 1: dropping on a display -0.001 decides on noise with ~0 correlation to private (different embryos/clips; effect idiosyncratic). E gain ~ P(drop) * E[-delta_priv | signal] ~ 0.1 * ~0 < 1e-5 (claimed +1e-4 is ~10x too high). Cost: dropping needs a newly scored no-lowrefine file (K1 unscored in branch A), a slot + 7-8 h rerun, and forces K3 rebuild -> confounds K3-vs-K2. R7 explicitly forbids choosing between near-copies on 0.001 - RT2 reverses that on noise.
- Item 2 (delete #34 from §f fallback): value-NEGATIVE. #34 is scored 0.953, L34 <= 6.46 h (admissible). In the world where the K-family fails (K2 hidden-run error, P ~2-5%), the chain would give F1 = exp52 = F2 (duplicate final), losing max(x138_priv, exp52_priv) option. Bottom of 241-team x138 block still beats every team below it; exp52 (public 0.950) must beat x138 on private to do better.
- Item 3: 'noncontrol' plateau is the LOOSER reading for DeepCenter threshold = network-confidence knob judged in-sample (DeepCenter/detector trained on all 199) - edge-filter lesson (+0.016 local -> 0 LB) argues for strict reading or extra margin. Settling before exp60 results is good; the recommended direction is wrong for transfer.
- Item 4: correct and already implied by R5(b) (9.5 - 7.8 = 1.7 h >= 1 h); harmless, no value.
- Verdict (value/transfer lens): REFUTED as proposed. Salvage: pre-commit before scores (procedural) with lowrefine kept unless K2 <= #35 - 0.002; keep #34 in fallback; pick STRICT plateau reading.
- 2026-09-25T17:49:29Z final JSON written
