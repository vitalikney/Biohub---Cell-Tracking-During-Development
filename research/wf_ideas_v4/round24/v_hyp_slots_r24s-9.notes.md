# R24S-9 verify notes (2026-09-28T07:04:56Z)
- 07:05Z: file absent at start; writing fresh.
- Source: experiments/discussions/743929.md point 5 (https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/743929). JT: "A decorrelated hedge that sits several thousandths behind loses expected value to a near-twin of the best." His own caveat is "this process reads the public sign exactly and says nothing about the private one". This is finals advice, not a disclosed x138 knob, so the aggressive-mode 'actionable' rule does not cover it.
- CONTEXT l.3179-3194, READ TABLE v2 (9): "The partner is always #37." It is pre-registered. 04:31Z FINALS CARD: {V_pub, #37}.
- The finding's premise ("mc23 compared only pairs with #37/#38/exp70b as partners") is FALSE. scratchpad r23/mc23.py has P7 {exp78a, exp70g}, which is exactly 'stack/rung + its one-lever parent'. r23/mc23b.py has P14 {exp79a, exp70g} (CI stack + its own parent). round23 scan notes l.11: "P14 ... (own parent -0.10)".
- mc23_out.txt, P6 {exp78a,#37} vs P7 {exp78a,exp70g}, bronze/silver per scenario:
  base s7 .668/.414 vs .566/.426; base s23 .671/.414 vs .571/.425; qpub0 .572/.249 vs .410/.248; qpub_hi .716/.497 vs .657/.516;
  overfit .762/.489 vs .615/.475; central .562/.344 vs .512/.370; inspes .595/.378 vs .536/.394; qpub0_pes .484/.221 vs .374/.226.
  The parent partner loses 0.05-0.16 bronze in 8/8 scenarios. Silver moves -0.014..+0.026 (a wash). E-value is lower in 8/8.
- Mechanism: any one-lever parent of a 2-3-lever stack shares at least one public-picked lever (cap > 4: lab 0 TP / 4 FP; READMIT 0.94: lab-blind, R23-RC-A). Its private failure is therefore correlated with V_pub's, and #37 (cap 4, no picked lever) is the hedge. Near-twin logic applies only when the partner's levers are private-proven, and none are.
- The parent 'public read' is one embryo on a 0.001 grid. Parent-vs-#37 gaps of 1-3 thousandths are within the public/private shake-up. Re-running mc23 for READMIT/ILP levers needs new judgmental priors (no measurement), and I-092 says the MC never decides.
- Feasibility: trivial (a message line, 0 runtime, 0 slots). The line would still add a pair the model already ranks lower, which invites a worse pick.
