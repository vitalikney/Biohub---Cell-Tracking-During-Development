# R41-RC-C recheck skeptic notes
- 2026-09-29T14:28:04Z start; no prior json
- Beta(5,12) verified (scipy): 90% [0.132,0.484]; P(p<0.114)=0.029, <0.161=0.101, <0.20=0.202, <0.265=0.424. Matches finding.
- CONTEXT l.1305-1308: v1 steal cap4 t0.5, CONF +0.0019 CI[-0.0007,+0.0050], precision 4/15 (TP16->20, FP28->39), gate fail. l.1321 P_min 0.31 = public floor (J_pub 0.36). l.2347 q*=0.161 (ins35 25/31/74), 0.114 pre-insertion. l.2546 cap6 -0.00057, 85 extra 0TP/4FP/81 unann.
- Public reads on SHIPPED config: #35 exp57b 0.954 vs x138 0.953 (l.1801); #37 0.954 vs #38 0.953 (l.2951 "insertion +0.001 twice"). Rounding-level but consistent sign.
- Package break-even (insertion vs none) uses PRE-insertion J -> 0.114 lab-like; 0.161 is the marginal. P(positive) 0.90-0.97 lab-like; finding's 0.8-0.9 is conservative.
- Skeptic angle: both ticked finals carry insertion (correlated private risk). But downside magnitude ~1e-3, rest of stack (K, CI) dominates position vs x138 block; R2 pre-registered; finals ticked; switching to #38 would be post-hoc and lose K. Not a reason to refute.
- Action None -> feasibility trivial (no build/slot).
- 2026-09-29T14:29:19Z verdict NOT refuted; json written
