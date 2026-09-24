# feasibility verify notes (fork-midpoint-filter)
- Kernel order (replay.py docs): linefit -> edgefilter -> swapfix -> stitch -> divinsert; forkmid would be last. ef never touches forks; stitch only end->start (no forks).
- div_insert already gates mid=|(c1+v)/2-u|<=6.5 and cos<=0.25 -> audit (exp39 tail) did NOT include divinsert forks of exp48 (local s_c4_t0.5: TP 16->20 / FP 28->39 on confirmation). Checking their mid now (scratchpad/fm_feas.py).
- No saved geffs for divinsert configs in .public_local_cache/l2_replay (predictions dirs empty).
- RESULT fm_feas.py (4.5 min, nice): exp39 tail + div_insert s_c4_t0.5 (exp48-like local) -> 702 inserted forks: 10 TP / 21 FP / 671 free (matches replay +10 TP/+21 FP exactly).
  Inserted TP mid q: min 2.86, med 4.16, max 5.94; >=4.0: 6 TP / 15 FP; >=4.5: 3 TP / 12 FP; >=3.5: 9 TP / 18 FP. Inserted free forks: 381 of 671 >= 4.0.
  => applying forkmid to divinsert forks (as refined_change says) removes 6 of 10 inserted TP at 4.0: public-calibrated 1.36*(-6) - 0.36*(-21) = -0.60 < 0. Must EXEMPT div_inserted forks.
- Kernel exp48 cell 8: add_safe_divisions_postlink edges carry "safe_division": 1 (line ~1163), prob None; divinsert edges carry div_inserted=1. Replay tails keep only NaN prob (gap edges also NaN) -> use rule "prob None/NaN AND not div_inserted" in both for parity.
- Coord-head re-check of the threshold needs coord-head nodes on 199 train videos: lab cache has fixed detector nodes -> not possible without a GPU run of exp51 on train (head moves nodes mean 0.74, max 1.61 um).
- Verdict: as specified (applies to divinsert forks too) REFUTED under feasibility/conflict lens; repair = safe-div-only forkmid, exempt div_inserted, forget stolen-edge restore, and skip/raise threshold if bundled with coordhead.
