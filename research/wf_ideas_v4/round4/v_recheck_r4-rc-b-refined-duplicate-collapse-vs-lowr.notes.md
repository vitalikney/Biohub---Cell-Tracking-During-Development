# v_recheck R4-RC-B (skeptic) notes - started 2026-09-26T00:57:25Z
- no prior json; starting fresh.
- 2026-09-26 ~04:1xZ independent reproduction (scratchpad r4v_dup.py; cKDTree same-frame pairs, voxel 1.625/0.40625/0.40625 um,
  _dl/biohub-exp58t / exp56 / exp58 / exp58n submission.csv; GT = biohub-cell-tracking-during-development/train/<ds>.geff):
  K1 exp58t == exp56 nodes (121,219, identical coords): nodes-in-pairs <1/2/3/4 um = 2/18/58/446; unique pairs <3 um 29, <2 um 9.
  K2 exp58 == twin exp58n nodes (121,252, identical): 4/26/82/465; unique pairs <3 um 41, <2 um 13. -> finding numbers EXACT.
  20 pair keys <3 um in K2 not in K1; nearest GT node to pair midpoint: min 14.7 um (6bba_05db0fb1 t52), 3 at frames with no GT;
  none within 4 um (none within 14 um). K2 vs K1: 2,829 coords only-in-K2, 2,796 only-in-K1 (lowrefine moves ~2.3% nodes, +33 net).
- Skeptic caveats: GT is very sparse on the dummies (44b6 clips 52 and 51 GT nodes over 100 frames; 6bba 861/1229), so
  '0 of 20 near GT' has low power (expected ~0.5-1 by chance at ~3-6% annotation). Verdict rests instead on exposure:
  +12 pairs = +24 nodes max = 0.02% of nodes -> node penalty term 0.1*24/121k ~ 2e-5; edge-side worst case <= ~24/117k edges ~ 2e-4,
  realistic ~1e-5 given sparse GT. Collapse on K2 has ceiling of 41 pairs <3 um -> v2 oracle (+0.0004) is an upper bound, and
  head-free variants were negative. Plus new-mechanism cutoff 27 Sep 12:00 UTC and no build proposed. -> NOT refuted; stays closed.
