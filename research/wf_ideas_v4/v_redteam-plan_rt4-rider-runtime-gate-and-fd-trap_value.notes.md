# RT4 value/transfer skeptic notes (2026-09-25)
- 2026-09-25 ~18:10 UTC: no prior JSON. Read step0.md, sibling verdicts D4 value (refuted, EV ~1e-5, fix = re-run step-0 arithmetic per rider), H1 value/feasibility (runtime ledger anchored on L(K2)), CONTEXT l.1810-1853, RESULTS.md probes 21/29.
- tools/dummy_gates.py has NO timing checks today (grep 'detection+edges|repair|SAFETAIL' empty).
- Per-clip GPU 'detection+edges' (s), _dl/*/..log, clips 0113/0b24/05b6/05db:
  exp56 233.2/245.7/229.9/267.5 (mean 244.1); exp57b 211.5/210.8/210.5/233.2 (216.5); K1 exp58t 215.2/215.0/211.5/233.9 (218.9);
  K2 exp58 214.2/213.6/211.6/235.5 (218.7); FD 211.3/210.2/208.5/230.3 (215.1); FF 212.3/224.6/205.3/253.0 (223.8).
  GPU code identical in all six (lowrefine is post-GPU). Session offset vs K2: exp56 +25.4 s/clip, FF +5.1, FD -3.6 -> the 15 s/clip-shard
  GPU threshold would FAIL exp56 (identical GPU code) -> false-fire rate ~1 in 5 dummies, needs ratio/same-session comparison.
- Per-clip repair (s): exp56 46.8/59.3/11.1/109.3 (56.6); FF 47.0/56.0/11.0/105.1 (54.8); exp57b 79.9/116.2/19.4/275.9 (122.9);
  K1 78.9/118.5/20.1/282.3 (125.0); K2 81.7/119.9/20.4/287.2 (127.3); FD 28.1/32.2/6.6/45.7 (28.2). Identical-code repair noise ~2 s/clip -> 8 s tail threshold is above noise (OK).
- Magnitude: worst-case margin 28,800 - 28,071 = 729 s (anchor is an UPPER bound: L35 includes queue time, N<=97 is an upper bound).
  Rider +12 s/clip tail -> +1,164 s -> ~435 s over -> ~3-4 of 97 clips lose insertion (~4%) -> 0.04 x 0.001 = 4e-5 LB.
  Losing 0.0002-0.0005 (idea's claim) needs 20-50% of clips past the gate = 2,700-6,900 s excess -> only in grossly slow worlds that latency shows anyway.
  EV = P(fire | upper-bound anchor, ~0.03-0.1) x 1e-5..1e-4 ~ 1e-6..1e-5. Attribution confound <= lost insertion (~4e-5) << 0.001 LB display step.
- K2 latency L(K2) arrives ~07-08 UTC 26 Sep, BEFORE any rider (K3 S4 ~10-13 UTC) -> real anchor; margin per clip = (28,800 - L(K2))/N; if L(K2) <= 7.3 h the allowance is >= 26 s/clip and the fixed 8 s gate would block/rebuild riders for nothing.
- Remedy DIVINS_DEADLINE_S=32400 rewrites a pre-registered constant (needs user OK per H1 feasibility (4)); D4 value (d): later insertion gate can push clips past the 9.5 h repair deadline in the slow world it insures (insertion +66..185 s/clip x ~28 clips between 8-9 h = ~0.5 h).
- (b) FD trap: correct. Dummies = train copies (CONTEXT l.21, in-sample for detector/edge/head). History: probe 21 relink OFF local +0.0053 (12 LOEO) -> LB -0.002; probe 29 edge filter +0.016 lab -> 0 LB; readmit is what took x138 0.947 -> 0.953. FD 0.9249 vs 0.9180 is one clip (44b6_0113de3b +0.093/4 = +0.023) -> do not act. Already logged in lens_redteam-plan.notes.md l.14; one CONTEXT line is free.
- VERDICT: refuted (value claim ~0, GPU gate within session noise); keep (b) as a one-line record and fold (a) into the H1 ledger anchored on L(K2).
