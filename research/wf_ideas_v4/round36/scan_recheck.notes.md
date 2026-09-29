# round36 scan_recheck notes (started 2026-09-29T08:13:44Z)

## 08:13-08:40Z 29 Sep (0 Kaggle calls, no browser, local files only)
- round36 folder was missing -> no earlier answer; created.
- Audit: 34 earlier scan_recheck.json (rounds 2-35), 131 items; R32-PI..R35-PI say the lens is saturated. Items picked here are ones that probe 54 (exp89p = 0.956, SEC '-', CONTEXT 07:59Z) touches and that are not yet read: exp89r (56656147) and exp75 (56656157) PENDING at poll header 2026-09-29T08:18:17Z (poll.log l.29539). Everything below is pre-score for both.
- Excluded as already done: exp86c/READMIT 0.92 on M2 (R26-RC-B -> refuted in round26/report.json 'rejected'); exp89u partner (R34-RC-A refuted); JT pair (R34-RC-C); secondary-swap family (R18-RC-B, R28-RC-B).
- Dummy-clip GT lab recomputed (scratchpad r36/pool.py using tools/overlap_lab.pooled over r26/ + r28/ dummy_lab_exp*.json):
  K on 70g (85a-70g) +0.00132 (44b6 -0.00106, 6bba +0.00143)  LB probe 50 +0.002  RIGHT
  SEC on K (89p-85a) -0.00160 (44b6 +0.00063, 6bba -0.00171)  LB probe 54 -0.002  RIGHT (new today)
  SEC on 70g -0.00204; SEC on CI (83c-79a) -0.00121; SEC on K+DIS (89q-89s) -0.00169
  SEC+DIS on K+CI (89r-87a) -0.00079 (44b6 +0.00137, 6bba -0.00089)
  DIS on K (89s-85a) +0.00048; DIS on K+SEC (89q-89p) +0.00039; DIS on 70g (88a-70g) -0.00079
  CI on 70g -0.00549 vs LB probe 48 +0.001 WRONG; CI on K (87a-85a) -0.00509 vs LB probe 51 +0.001 WRONG; CI on #37 (75-58) -0.00549
  RA92 (86c-85a) -0.00009; exp89r-exp89p -0.00428 (CI inside -> not usable)
  Older: probe 10 secondary swap dummy -0.007 vs LB -0.025 RIGHT (CONTEXT freeze (9)).
  => sign record: non-coordinate levers 3/3 right (magnitude LB/lab 1.25-1.5x for K and SEC); coordinate lever CI 0/2.
- Prediction for exp89r (non-CI part only): SEC+DIS on the CI base = -0.0008 lab -> -0.0010..-0.0012 LB -> d_R central 0.958 (0.957-0.959). DIS '+' / Rr '+' need d_R >= 0.960 -> P ~0.05. exp89s (K+DIS) lab +0.0005 -> exp85a true [0.9575,0.9585) + 0.0006-0.0007 -> display 0.958/0.959, cannot beat 0.959 without DIS >= +0.0015 true.
- SEC x CI interaction in the lab: SEC costs -0.0016 on K but -0.0012 on the CI base (and the pair 89r-87a -0.0008 incl DIS +0.0004). So branch-A dd = (d_R-d_P)-(d_87a-d_85a) is biased UP by ~+0.0004 of SEC-CI interaction -> the 'exp89r > max(exp87a, exp89p)' clause (d_R >= 0.960) is the right strictness after d_P = 0.956; a d_R = 0.959 (dd +0.002) is explainable by interaction + rounding, not DIS.
- exp89t (exp87a + DIS 2.25) never built in experiments/ (only scratch mirror 76b898dd, round26/report.json new_facts 5); default 'no exp89t' (CONTEXT 15:43Z 28 Sep). CI L 9.30-9.48 h -> must be submitted by ~09:30Z to read by ~19:00Z; build+dummy 35-40 min.
- 08:22Z scan_recheck.json written (3 recheck-old + 1 new-fact); helper _w.py from a failed heredoc removed.
