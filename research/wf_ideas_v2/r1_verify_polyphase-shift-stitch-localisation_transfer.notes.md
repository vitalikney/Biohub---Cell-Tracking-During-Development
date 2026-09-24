# r1 verify polyphase-shift-stitch-localisation — TRANSFER lens (started 2026-09-24)
- No prior verify JSON; research notes read (dose-response: +1 xy quantisation costs -0.0021/-0.0013 edge recall; offsets 6bba z +0.90 vs 44b6 +0.20 um => embryo-specific).
- Eric (discussions_summary l.354-358): public detectors trained on all 199; his sub-voxel peak refinement +0.0078 on 12 videos, -0.002 LB twice -> same class as this idea, same lab.
- CONTEXT l.1425-1429: our coordhead port moved 143,633 peaks mean 0.74 um -> FINAL nodes 122,704 -> 119,174 (-2.9%; 44b6_0b24845f -10.7%). So moving coordinates with a fixed raw node set DOES change final N_pred via post-proc; "N_pred identical" claim is false; part of x138 +0.007 may be multiplier (0.1*0.029*J ~ +0.0027).
- Embryo-specific GT-pred offsets (6bba z +0.90 vs 44b6 +0.20 um) -> arm C (+1.5px constant de-bias) is a constant offset; Le Quang Canh constant offset -0.0031 LB. Drop arm C.
- Embryo shift magnitude: scratch 6bba model own-train 0.833 vs unseen 44b6 0.680 (CONTEXT l.382) -> in-sample localisation is far better than on unseen embryos; quantisation share of error on private is smaller than the local 10-20%.
- Repair: out-of-sample test with friend A's LOEO scratch 6bba model on 44b6 (never saw 44b6), N-matched readout (edge J vs multiplier decomposed).
- VERDICT: refuted under transfer lens (signal <= +0.002 below gate and LB resolution; lab in-sample; multiplier not neutral).
