# v_hyp_detect_r11d-4 skeptic notes (round 11, 2026-09-26 ~20:20Z)
- No prior v_hyp_detect_r11d-4.json -> fresh run.
- Recomputed from scratchpad/r11/r11_detect_out.json: missing nodes 44b6 1+28+29+4+2=64, 6bba 42+316+159+62+25=604 -> 668 OK.
  FN edge-ends 44b6 1+51+57+8+4=121, 6bba 45+567+304+124+50=1090 -> 1,211 OK. sandwich_through 25+2=27 nodes, 50+4=54 fnends OK.
- exp60 totals: TP 38,388 + FP 1,681 + FN 1,705 = 41,774 OK; 1,211/41,774 = 0.0290; 0.012*41,774 = 501 -> 41% of 1,211 OK.
  Edge-ends double-count edges between two consecutive missing nodes (runs are 80% of misses), so distinct recoverable edges < 1,211
  and the metric's adjusted-Jaccard factor <= 1 -> +0.029 is an UPPER bound; real bar share is > 41%. Conservative in the finding's favour.
- 54/41,774 = 0.0013 OK.
- R4 bar (+0.002 public, ~+0.012 lab by ~1/6 transfer) and R8 (27 Sep 12:00 UTC) confirmed: CONTEXT.md 16:49 UTC entry (l.2318-2321).
- User OK for successor-scenario analysis: CONTEXT.md 17:00 UTC entry (l.2335-2341); commit df6996e.
- Refutation attempts: (a) a DC-map / UNet-map recall arm is not CPU-measured, but it is bounded by the same pool and is x138's own
  LOWDET/GAPFILL/READMIT knob class (I-139 closed; readmit GT-match 0.5%); detection-map class 0/5 on LB (CONTEXT l.2135).
  (b) public embryo could be dimmer (more misses) - unmeasurable before R8, no gate possible, and any arm would still need GPU lab + dummy + OK in ~16 h.
  (c) z re-centring = I-040/I-046 (closed, LB -0.002 twice). Nothing survives.
- Only caveat: 'nothing reaches R8' is a ceiling argument, not a measurement of every arm; the ceiling suffices.
- Verdict: NOT refuted.
