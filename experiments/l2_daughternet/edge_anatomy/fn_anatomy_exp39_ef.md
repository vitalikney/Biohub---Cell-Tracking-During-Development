# FN anatomy of the final `exp39` + ef {'enable': 1, 'max_prob': 0.3, 'alt': 3, 'min_len_um': 0.0, 'relink': 1, 'prune': 1, 'skip_forks': 1} graph (199 videos)

Validated: FN 6099 = official edge_fn 6099 in every video; base score 0.929849.

| class | FN all | share | 44b6 | 6bba | GT-division FN | prov ilp/ckpt/none | competitor TP/FP | oracle d all | d 44b6 | d 6bba |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| c_gap_node | 57 | 0.009 | 16 | 41 | 0 | 0/0/57 | 0/107 | +0.00116 | +0.00214 | +0.00098 |
| c_gap_node_off | 20 | 0.003 | 4 | 16 | 0 |  |  |  |  |  |
| a_never | 1907 | 0.313 | 167 | 1740 | 19 |  |  |  |  |  |
| a_tail | 624 | 0.102 | 86 | 538 | 11 |  |  |  |  |  |
| a_linefit | 353 | 0.058 | 28 | 325 | 3 |  |  |  |  |  |
| a_taken | 62 | 0.010 | 16 | 46 | 11 |  |  |  |  |  |
| b_break | 399 | 0.065 | 41 | 358 | 2 | 281/48/70 | 0/0 | +0.00298 | +0.00198 | +0.00317 |
| b_v_taken | 556 | 0.091 | 142 | 414 | 4 | 23/46/487 | 0/556 | +0.00799 | +0.01324 | +0.00702 |
| b_u_diverted | 593 | 0.097 | 156 | 437 | 37 | 27/116/450 | 36/563 | +0.00804 | +0.01437 | +0.00688 |
| b_swap | 1528 | 0.251 | 329 | 1199 | 54 | 1/12/1515 | 53/3003 | +0.03227 | +0.04501 | +0.02994 |

Totals: {'all': 6099, '44b6': 985, '6bba': 5114}

## End -> start candidate pairs (prediction side only; label under the fixed matching)

| rule | pairs | TP | FP | NE | TP/(TP+FP) |
|---|---:|---:|---:|---:|---:|
| all end->start pairs <= 14 um | 43045 | 353 | 921 | 41771 | 0.277 |
| dist [0,2) | 2769 | 31 | 43 | 2695 | 0.419 |
| dist [2,3) | 1617 | 12 | 33 | 1572 | 0.267 |
| dist [3,4) | 794 | 6 | 9 | 779 | 0.400 |
| dist [4,5) | 477 | 3 | 8 | 466 | 0.273 |
| dist [5,6) | 742 | 4 | 6 | 732 | 0.400 |
| dist [6,8) | 3863 | 49 | 68 | 3746 | 0.419 |
| dist [8,10) | 7260 | 101 | 145 | 7014 | 0.411 |
| dist [10,12) | 12063 | 100 | 278 | 11685 | 0.265 |
| ILP edge | 6956 | 271 | 19 | 6666 | 0.934 |
| ILP edge & p>=0.7 | 4794 | 231 | 8 | 4555 | 0.967 |
| ILP edge & mutual NN | 4662 | 214 | 14 | 4434 | 0.939 |
| no ILP edge & mutual NN | 18236 | 62 | 365 | 17809 | 0.145 |
| no ILP & mutual NN & dist<4 | 5101 | 49 | 84 | 4968 | 0.368 |
| no ILP & mutual NN & dist<6 | 5861 | 50 | 95 | 5716 | 0.345 |
| ckpt edge (removed by tail) | 5258 | 48 | 86 | 5124 | 0.358 |
| e or s synthetic | 0 | 0 | 0 | 0 | nan |

## Stitch rules (tools/build_probe_kernel.py stitch_final_graph on this graph; exact edge counts, division term and node count held fixed)

| rule | added | TP | FP | d all | d sel (6bba) | d conf | d conf 44b6 | d conf 6bba | conf videos gaining 44b6 / 6bba |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| st_all | 7182 | 281 | 19 | +0.00197 | +0.00178 | +0.00211 | +0.00117 | +0.00247 | 0.15 / 0.72 |
| st_p05 | 7010 | 279 | 18 | +0.00196 | +0.00178 | +0.00210 | +0.00117 | +0.00245 | 0.15 / 0.70 |
| st_p06 | 6025 | 259 | 15 | +0.00183 | +0.00170 | +0.00194 | +0.00102 | +0.00229 | 0.15 / 0.67 |
| st_p07 | 4936 | 240 | 8 | +0.00174 | +0.00168 | +0.00179 | +0.00078 | +0.00218 | 0.14 / 0.62 |
| st_p08 | 3736 | 212 | 3 | +0.00157 | +0.00152 | +0.00160 | +0.00073 | +0.00194 | 0.11 / 0.56 |
| st_c1 | 7143 | 281 | 19 | +0.00197 | +0.00178 | +0.00211 | +0.00117 | +0.00247 | 0.15 / 0.72 |
| st_c2 | 6402 | 272 | 19 | +0.00190 | +0.00172 | +0.00205 | +0.00102 | +0.00244 | 0.15 / 0.72 |
| st_max12 | 6228 | 232 | 17 | +0.00162 | +0.00142 | +0.00177 | +0.00097 | +0.00207 | 0.15 / 0.67 |
| st_min6 | 6728 | 275 | 18 | +0.00193 | +0.00177 | +0.00206 | +0.00117 | +0.00240 | 0.15 / 0.70 |

Detection-side FN (a_*): 2946; the matched end is a free track end/start in 519; a 1-frame gap bridge (end at t, GT successor matched to a start at t+2, or the mirror) in 58.
