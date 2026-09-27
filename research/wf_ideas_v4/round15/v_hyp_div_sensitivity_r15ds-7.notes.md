# v_hyp_div_sensitivity_r15ds-7 notes (skeptic, value+feasibility), 2026-09-27
- 05:45Z no prior JSON for this task; created notes.
- CONTEXT l.2545-2549 (26 Sep 21:56Z CAP-6 LAB ARM): cap6 vs ins35 pooled -0.00057 (44b6 -0.00079, 6bba -0.00052), W/L 1/4,
  boot90 -0.00125..-0.00011; 85 extra = 0 TP / 4 FP / 81 unannotated; cap5 -0.00015, cap8 +0.00003. Pre-registered gate -> exp70g not submitted. VERIFIED.
- IDEAS I-326 refuted by own gate; I-308 (thresh 0.6/cap 2) refuted NO-GO; I-220 'cap 4 binds nearly everywhere'. VERIFIED (research/KNOWLEDGE/IDEAS.md l.172/177/337).
- F-LB-01: #35 exp57b (x138+ins) 0.954 vs #34 x138 0.953 -> second independent public read of the insertion at +0.001 display, same sign as K2 vs twin.
- K2 vs twin: displays 0.954/0.953 -> unrounded diff in (0, 0.002) under any 3-dec rounding. VERIFIED.
- Soft spots: (a) '1 TP + 1-2 FP' ignores that an inserted parent->daughter link also moves the edge term; decomposition is a guess.
  (b) 'public EV -0.001..-0.002' for cap 6 is not derived from any measurement (lab -0.00057 with 4 evaluable FP; 81/85 unannotated);
  and D1 (CONTEXT 04:58Z) showed the lab mis-signed the DC knob on public, so the lab cannot sign cap 6 on public either. Magnitude unsupported, but irrelevant to the action.
  (c) 'THRESH 0.3 nearly inert' is an inference from I-220 (lab), untested on public dummy clips; again no action depends on it.
- Rules: any cap/thresh rung = post-hoc re-open of a line refuted by its own pre-registered gate + class C (never a final) + needs new user OK by R8 27 Sep 12:00Z; 2 slots left today reserved (E10 port, resubmits). 'None' is the only rule-consistent action. Pending probes 43/44 (DC 0.20/0.225, ~12:30Z) arrive after the R8 line, so they cannot reopen it either.
- Verdict: NOT refuted (keep 0.4/cap 4, no rung); drop the unsupported public-EV number from the record.
