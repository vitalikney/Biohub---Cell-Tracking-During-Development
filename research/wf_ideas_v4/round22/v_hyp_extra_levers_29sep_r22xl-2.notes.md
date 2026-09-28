# v_hyp_extra_levers_29sep R22XL-2 notes
- 2026-09-28 start: no prior answer file; reading CONTEXT, scan json.
- 2026-09-28 ~04:30Z: scan_hyp_extra_levers_29sep.json read (R22XL-1..5). Lab file scratchpad/r22lev/an.json cap6_fc2: ALL d_cap6 +0.000208, boot CI90 [-0.000194, +0.000809]; 44b6 d 0.0; 6bba +0.000253; adj_vs6 +6.8e-5; extra 30 (0TP/1FP/29ign), lost 27 (0TP/2FP/25ign); 289 insertions vs cap6 ~286.
- Lab cap6 vs cap4 = -0.000572 (from cap6_fc2 d_cap4 -0.000364 minus d_cap6), but public cap6 exp70g 0.956 > K2 0.954: the lab sign was WRONG for the parent lever (cf. CONTEXT l.2798 DC 0.30 sign also wrong). So no sign-transfer evidence for any insertion knob.
- The whole lab gain = 1 FP removed, 0 TP moved; ~1.5 evaluable public changes expected -> below one event; 0.957 display depends on unknown unrounded position of exp70g (0.95634 is an estimate).
- Rules: CONTEXT l.3372-3377 W4 AMEND 2 (4) "Never: knob/thr/... rungs"; W2 TABLE v4 has no fc2-on-cap6 slot; exp76e filler replacement would need a new user OK; exp78b (probe 47, cap 12 + fc2) already carries fc2 -> info-dominated. Public-only knob pick = public-embryo overfit; private ~0.
- Feasibility is fine technically (existing DIVINS_FRAME_CAP knob, default 1 = byte-identical, inside safetail fail-soft, +0 h), but the rule gate fails.
- Verdict: refuted as a value candidate; the finding's own 'DO NOT BUILD' stands.
