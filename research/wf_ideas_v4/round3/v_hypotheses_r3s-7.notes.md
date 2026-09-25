# R3S-7 skeptic notes (2026-09-25T22:46:20Z)
- 22:47Z 25 Sep (K2 not yet submitted; poll.log last 22:43Z, ledger: K2 absent).
- CONTEXT.md l.1601-1619 slot table; l.1650-1652 R3 (-0.001 keeps rider, -0.002 drops); R7 "no choice between near-copies by 0.001 except via R3"; §f "simpler file replaces F1 only at >= +0.002"; §f (i) finals must be scored without error.
- l.1801-1803 (#35 0.954, L35 (6.72,7.73] -> #35 not a finals candidate). Confirms "K1 = only admissible x138+ins without lowrefine".
- Round 1 FINAL_REPORT_v4 §3 item 6: K1 in next 26 Sep slot if K2 ERRORS [needs OK]; §5 OK list item 4. RT1 feasibility fix already proposed trigger "K2 errored or K2 == 0.953 (< #35)". RT1 value verdict: K1 score at -0.001 changes nothing under R3/R7/§f.
- KNOWLEDGE/WATCHLIST W20/W21: K1 on K2 error on morning OK list.
- round3/scan_plancheck.json already proposes: "K2 <= 0.952 or K2 ERROR: submit K1 ... F1 = K1 once scored". So error + <=-0.002 branches are NOT new.
- Only new part of R3S-7 = widening to d1 = -0.001. In that world R3 keeps lowrefine, F1 = K2, K1 (likely 0.954) could replace K2 only via a 0.001 pick -> forbidden by R7/§f. Option value = 0 under the pre-registration; it is a temptation to rewrite R3 post hoc. Private run is the same run as public -> no 'tail insurance' after scoring.
- Residual real value: error / d1<=-0.002 / K2 fails R5 (L(K2) > 9.5 h) worlds, P ~0.05-0.08; gain there ~ insertion private value ~+5e-4 vs falling back to #34 byte copy -> ~+2e-5 to +4e-5, already captured by item 6 + plancheck rule.
- Feasibility: fine (built, gated, free slots S4-S7, no new mechanism, 9.5 h family, L35 <= 7.73 h). Needs user OK.
