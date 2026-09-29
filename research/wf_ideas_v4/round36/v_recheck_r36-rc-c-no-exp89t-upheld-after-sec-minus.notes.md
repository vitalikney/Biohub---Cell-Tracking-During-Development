# v_recheck R36-RC-C (no exp89t upheld) - skeptic notes
- 2026-09-29 08:24Z: no prior answer JSON; started.
- FACT CHANGE: experiments/exp89t_k2cap6_k_dis225_ci/ EXISTS (ipynb + kernel-metadata.json + probe.json, mtime 08:22Z UTC;
  kernel vitaliineibauer/biohub-exp89t-k2cap6-k-dis225-ci; probe.json = exp87a knobs + ILP_DISAPPEARANCE_WEIGHT 2.25 + COORDINJECT).
- CONTEXT.md l.4415-4424 (08:23Z): 'exp89t BUILT + DUMMY PUSHED (user idea "add CI to exp89s"; submit only on the user's yes)';
  slot plan: slot 1 -> exp89t, slot 2 = A-M2 rule (a). Dummy pushed 08:22:49Z; planned submit ~09:05Z at PASS.
- scan_recheck.json written 08:22:19Z = same minute: the finding raced the build. Its evidence 'ls exp89* = a,e,l,p,q,r,s only'
  and verdict 'no build, dummy or question' are overtaken. R26-A6 precondition ('only on the user's yes') is now user-originated.
- Value side of the finding is fair: DIS lab K +0.00048 (89s-85a), K+SEC +0.00039, 70g -0.00079 (scan_recheck.notes l.12);
  prior ~0; 0.960 display odds mostly from exp87a's unrounded position (winner's curse).
- Residual real point (c): 09:05Z submit precedes exp89r's read (L 9.30-9.48 h from 00:05:28Z -> ~09:23-09:34Z), so exp89t
  would enter without any DIS read (conflicts with 12:25Z 'winners only'). Option: gate exp89t on exp89r >= 0.958 (same
  rule (a) as exp89s): submit ~09:40Z -> CI read ~18:58-19:09Z (before the 20:00Z tick; tail to ~10.9 h lands 20:34Z vs 19:59Z
  for a 09:05Z submit). If gated, exp89t and exp89s fire on the same condition: pick one (exp89t = V_pub line, CI) for slot 1,
  keep exp89s for slot 2 only if exp89t's dummy fails.
