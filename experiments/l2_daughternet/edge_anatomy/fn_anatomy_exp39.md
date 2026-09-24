# FN anatomy of the final `exp39` graph (199 videos)

Validated: FN 6732 = official edge_fn 6732 in every video; base score 0.914300.

| class | FN all | share | 44b6 | 6bba | GT-division FN | prov ilp/ckpt/none | competitor TP/FP | oracle d all | d 44b6 | d 6bba |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| c_gap_node | 57 | 0.008 | 16 | 41 | 0 | 0/0/57 | 0/110 | +0.00115 | +0.00213 | +0.00097 |
| c_gap_node_off | 14 | 0.002 | 0 | 14 | 0 |  |  |  |  |  |
| a_never | 1907 | 0.283 | 167 | 1740 | 19 |  |  |  |  |  |
| a_tail | 606 | 0.090 | 81 | 525 | 11 |  |  |  |  |  |
| a_linefit | 354 | 0.053 | 28 | 326 | 3 |  |  |  |  |  |
| a_taken | 62 | 0.009 | 16 | 46 | 11 |  |  |  |  |  |
| b_break | 150 | 0.022 | 5 | 145 | 0 | 115/0/35 | 0/0 | +0.00111 | +0.00024 | +0.00127 |
| b_v_taken | 701 | 0.104 | 150 | 551 | 3 | 246/0/455 | 0/701 | +0.00988 | +0.01371 | +0.00918 |
| b_u_diverted | 706 | 0.105 | 156 | 550 | 38 | 288/0/418 | 36/672 | +0.00946 | +0.01399 | +0.00863 |
| b_swap | 2175 | 0.323 | 444 | 1731 | 54 | 558/0/1617 | 53/4301 | +0.04568 | +0.06054 | +0.04297 |

Totals: {'all': 6732, '44b6': 1063, '6bba': 5669}

## End -> start candidate pairs (prediction side only; label under the fixed matching)

| rule | pairs | TP | FP | NE | TP/(TP+FP) |
|---|---:|---:|---:|---:|---:|
| all end->start pairs <= 14 um | 12511 | 120 | 318 | 12073 | 0.274 |
| dist [0,2) | 0 | 0 | 0 | 0 | nan |
| dist [2,3) | 0 | 0 | 0 | 0 | nan |
| dist [3,4) | 0 | 0 | 0 | 0 | nan |
| dist [4,5) | 0 | 0 | 0 | 0 | nan |
| dist [5,6) | 0 | 0 | 0 | 0 | nan |
| dist [6,8) | 2 | 0 | 0 | 2 | nan |
| dist [8,10) | 666 | 34 | 11 | 621 | 0.756 |
| dist [10,12) | 5479 | 59 | 144 | 5276 | 0.291 |
| ILP edge | 1143 | 113 | 5 | 1025 | 0.958 |
| ILP edge & p>=0.7 | 753 | 105 | 3 | 645 | 0.972 |
| ILP edge & mutual NN | 960 | 104 | 4 | 852 | 0.963 |
| no ILP edge & mutual NN | 8898 | 6 | 216 | 8676 | 0.027 |
| no ILP & mutual NN & dist<4 | 0 | 0 | 0 | 0 | nan |
| no ILP & mutual NN & dist<6 | 0 | 0 | 0 | 0 | nan |
| ckpt edge (removed by tail) | 0 | 0 | 0 | 0 | nan |
| e or s synthetic | 0 | 0 | 0 | 0 | nan |

## Stitch rules (tools/build_probe_kernel.py stitch_final_graph on this graph; exact edge counts, division term and node count held fixed)

| rule | added | TP | FP | d all | d sel (6bba) | d conf | d conf 44b6 | d conf 6bba | conf videos gaining 44b6 / 6bba |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| st_all | 1156 | 115 | 5 | +0.00082 | +0.00067 | +0.00093 | +0.00014 | +0.00123 | 0.03 / 0.42 |
| st_p05 | 1107 | 114 | 5 | +0.00081 | +0.00067 | +0.00092 | +0.00014 | +0.00121 | 0.03 / 0.42 |
| st_p06 | 898 | 108 | 4 | +0.00077 | +0.00066 | +0.00086 | +0.00014 | +0.00114 | 0.03 / 0.39 |
| st_p07 | 759 | 107 | 3 | +0.00077 | +0.00067 | +0.00085 | +0.00010 | +0.00114 | 0.03 / 0.39 |
| st_p08 | 612 | 103 | 0 | +0.00076 | +0.00070 | +0.00081 | +0.00005 | +0.00110 | 0.01 / 0.36 |
| st_c1 | 1156 | 115 | 5 | +0.00082 | +0.00067 | +0.00093 | +0.00014 | +0.00123 | 0.03 / 0.42 |
| st_c2 | 1152 | 115 | 5 | +0.00082 | +0.00067 | +0.00093 | +0.00014 | +0.00123 | 0.03 / 0.42 |
| st_max12 | 897 | 88 | 3 | +0.00063 | +0.00047 | +0.00076 | +0.00014 | +0.00099 | 0.03 / 0.38 |
| st_min6 | 1156 | 115 | 5 | +0.00082 | +0.00067 | +0.00093 | +0.00014 | +0.00123 | 0.03 / 0.42 |

Detection-side FN (a_*): 2929; the matched end is a free track end/start in 424; a 1-frame gap bridge (end at t, GT successor matched to a start at t+2, or the mirror) in 28.
