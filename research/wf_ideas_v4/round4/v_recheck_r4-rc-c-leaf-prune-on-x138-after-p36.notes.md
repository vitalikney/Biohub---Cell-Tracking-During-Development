# v_recheck R4-RC-C leaf prune (2026-09-26)
- 2026-09-26 ~01:00Z no prior v_recheck json; started fresh.
- CONTEXT l.1514-1516: exp57 diag: 513 leaves pruned, >=479 readmitted (36% of 1,337 readmit). l.1808-1809: P36 pre-reg |#36-#35|<=0.001 -> closed. l.1905-1907 (19:05 curator): P36 INFO ONLY, no rider even at >= +0.002. l.2010-2011: P36 = 0.954 = #35, L36 (7.24,7.42] h. l.2022 CLOSED list includes leaf prune on x138.
- CONTEXT l.1323-1326 (24 Sep, exp39 base lab): leaf prune +0.0005/+0.0006 CONF, nodes -0.05%; knob 0.2-0.4 identical (edge_prob is 0.0 or >=0.4). Probe 27 exp47 = 0.947 tie.
- R4 literal text (l.1650-1652): delta 0/+0.001 -> "F2 candidate", not closed. Overridden by the P36-specific pre-reg (closed) + 19:05 INFO-ONLY rule + AMENDMENT f2 (F2 = twin, user OK 22:06). Finding's "R4 needs +0.002" is right only for F1 entry.
- CORRECTION: round3 R3-NF-lab-node-count-bias (round3/scan_recheck.json) DID include a node-removing arm: MIN_TRACK_LEN L8 nodes -2.71%, lab -0.00023, LB -0.001 on the OLDER base (probe 9). So "measured on arms that add nodes only" and "first calibration point for a rule that removes nodes" are wrong; correct: first x138-base LB-anchored node-removal point (L8 anchor was pre-x138).
- r4_leafprune.py running (8 python workers seen via tasklist ~00:58Z); output r4_leafprune_out.json not yet present.
- ~01:00Z r4_leafprune_out.json LANDED (scratchpad, 56 clips exp60 lab, official metric). Summary (delta vs control):
  lp30: ALL +0.00083 (SEL +0.00088, CONF +0.00078), 44b6 +0.00165 (SEL +0.00260, CONF +0.00018), 6bba +0.00075; W/L 51/5 clips; nodes -0.507%; pruned 5,703 of which 5,432 (95%) readmitted.
  lp50: ALL +0.00064 (SEL +0.00081, CONF +0.00046; 44b6 CONF -0.00056), W/L 47/9, nodes -0.554%.
  Reading: lab lp30 +0.0008 is CONSISTENT with P36 delta 0 (3-decimal rounding, true |delta| < ~0.001). So this is a concordant point, not evidence of a lab bias for node-removing rules. Below the +0.002 R4 gate both in lab and on LB; no reopen. Stays closed.
- ~01:02Z final JSON written (refuted=false, with corrections).
