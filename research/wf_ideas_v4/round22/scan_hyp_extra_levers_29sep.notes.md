# scan_hyp_extra_levers_29sep notes (round 22, started 2026-09-28T01:03:00Z)

## 01:05Z context read
- CONTEXT l.3000-3377: W1 submitted 00:06Z probe 47 exp78b (cap12 fc2), 48 exp79a (cap6+CI), ~00:50Z 49 exp78a (cap 8). No reads yet (47 ~07:30Z).
- W2 TABLE v4 / W4 AMEND 2 (CONTEXT l.3347-3377): W3/W4 NEVER knob/thr/N1/fresh-N2/tau/DC rungs; cap 10/16; fc2 on cap 8. v2 (6): 'Never in W3/W4: knob rungs'.
- Round 20 R20ID-6 closed: steal off (-0.002 lab), steal_frac 1.0 (-0.0001), ALPHA (no lab, no read), fc>=3, scaled caps, thr 0.2. IDEAS I-068, I-409, I-410. I-063 (DaughterNet v2 / v1+v2 avg) deferred-after-deadline.
- Lab (scratchpad/r20ins/an2.json): cap6_fc2 vs cap6 = +0.000208 pooled (44b6 0, 6bba +0.00025), 289 vs 286 insertions, 30 swapped-in (0 TP/1 FP/29 ign), div FP 35->34. i.e. fc2 at cap6 = re-ranking at ~equal volume, not 'more cap'.
- DaughterNet ensemble: tools/daughternet.py l.118-129 mean softmax over loaded fold models; kernel loads all /kaggle/input/**/vitalii_daughternet/*.pt. Dumps store ensemble p only -> fold-subset arms NOT replayable from exp60 dumps.

## 01:20Z lab sweep (scratchpad/r22lev/sweep.py = r20ins/sweep2.py with new ARMS; an.py; outputs sweep_raw.json, an.json; tools/ untouched)
- Parity: cap4 = 0.939878, div 25/31/74, identical to r20ins an2 -> replay OK. 56 clips, _dl/exp60_a + exp60_b dumps, in-sample DaughterNet (5-fold mean).
- Pooled delta vs cap6 [clip bootstrap p05, p95] | 44b6 | 6bba | insertions | extra vs cap6 (TP/FP/ign) | lost vs cap6:
  - cap6_fc2   +0.000208 [-0.00019, +0.00081] | 0 | +0.00025 | 289 | 30 (0/1/29) | 27 (0/2/25); 26 clips changed; adj edge +7e-5
  - cap6_a05   0.000000 [-0.00038, +0.00042] | 0 | 0 | 308 | 52 (0/1/51) | 30 (0/1/29); eligible 1994 -> 3653
  - cap6_a0    +0.000588 [-0.00055, +0.00228] | 0 | +0.0007 | 330 | 127 (1/4/122) | 83 (0/4/79); eligible 7620; adj edge -0.000158
  - cap6_a2    -0.001739 [-0.00466, +0.00027] | -0.00503 | -0.00124 | 210 | 21 | 97 (3 TP/4 FP lost)
  - cap6_a3    -0.002153 | -0.00503 | 125 insertions, loses 4 TP
  - cap6_fc2_a2 -0.00189; cap8_a2 -0.00095; cap12_fc2_a2 -0.00064 (44b6 -0.005)
  - cap12_fc2_a05 +0.001335 vs cap6 (vs cap12_fc2 +0.001234 -> +0.0001), 556 vs 462 insertions: alpha<1 = more volume.
  - cap6_sf0.34 (steal cap 2 instead of 3) -0.000068, null.
- Reading: alpha>1 lab-refuted (drops the only 44b6 TP); alpha 0.5 = exact lab null at cap 6; alpha 0 = volume-in-disguise with the one robust-direction adj-edge loss; fc2 at cap6 = the only equal-volume re-rank with a (tiny, CI incl. 0) positive lab.
- Fold subset: not replayable (dumps hold ensemble p); r9h-4 says fold p more extreme (99th pct 0.90 vs 0.83) -> fewer folds = more eligible above 0.4 = volume-in-disguise + noise.
- 2026-09-28T01:13:43Z final JSON written: research/wf_ideas_v4/round22/scan_hyp_extra_levers_29sep.json
