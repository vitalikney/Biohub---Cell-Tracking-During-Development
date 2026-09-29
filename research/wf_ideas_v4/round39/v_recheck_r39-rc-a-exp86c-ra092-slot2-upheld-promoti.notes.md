# R39-RC-A exp86c RA092 slot2 recheck notes (started 11:24Z)
- 11:25Z: no prior answer file. Checked CONTEXT l.3433-3437 (JT 743929: READMIT 0.965->0.94 +0.001; JT stopped at 0.94), l.3515-3528 (exp86c dummy PASS, CSV 31b1e047587a, nodes +0.32% vs exp85a), l.3885-3898 (12:23Z 28 Sep: READMIT 0.92 excluded as public fitting), l.3931-3936 (MORNING TABLE v1.1 (0)(i) keeps RA 0.92/0.90 out). All match.
- Ledger experiments/lb_poll/ledger.md: exp85a L (7.01,7.19] h, exp89p (7.02,7.20] h -> exp86c sent 12:00Z reads ~19:01-19:12Z. Matches.
- scratchpad r26/dummy_lab_summary.json: exp85a 0.921842 vs exp86c 0.921747 (-0.000095), tp/fp/fn 2049/99/78 identical both -> pure node-multiplier move. Matches.
- scratchpad r39/p86c.txt: P(disp>=0.960) 0.008/0.039/0.079/0.169 for the 4 priors. Matches.
- CONTEXT 11:10Z: slot 2 = last slot of 29 Sep, default UNUSED, user hold to 12:00Z. No later slot exists -> an exp86c read has no information value beyond a promotion decision.
- Refutation attempts: (i) 'send but never promote' -> value exactly 0, still not > UNUSED, adds a pending read + card work near the tick; (ii) '0.960 would be real private signal' -> needs +0.002 over exp85a 0.958 from a knob that moves 0 TP/FP/FN in lab; on 29% public that is fit/noise; (iii) exp86c+CI would read ~21:15Z+, after the tick, and has no dummy. None overturns the verdict. The '-0.0005 private' figure is a rough, unsourced estimate, but the sign argument (swap CI for non-CI on primary) is enough.
- Verdict: finding UPHELD -> refuted=false.
