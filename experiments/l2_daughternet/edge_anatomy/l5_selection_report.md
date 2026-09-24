# L2 replay - split `selection` (64 videos), control `exp39`

cache `C:\Users\vital\Documents\kAGGLE\Biohub - Cell Tracking During Development\data_external\friend_a_cache\friend_a_b20_exp29_friend_c\cache\friend_a_b20_exp29`; official metric; paired bootstrap over videos (2000 draws, seed 0).

| config | score | delta | 90% CI | P(d>0) | adj edge | div TP/FP/FN | 44b6 | d44b6 | 6bba | d6bba | node ratio |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| exp39 | 0.897811 | +0.000000 | - | - | 0.888951 | 7/15/57 | - | - | 0.897811 | - | 1.000000 |
| ef_a0 | 0.907279 | +0.009468 | [+0.00654, +0.01302] | 1.000 | 0.898418 | 7/15/57 | - | - | 0.907279 | +0.009468 | 1.000000 |
| ef_a0_rl | 0.911455 | +0.013644 | [+0.00949, +0.01874] | 1.000 | 0.902594 | 7/15/57 | - | - | 0.911455 | +0.013644 | 1.000000 |
| ef_a1_rl | 0.910068 | +0.012257 | [+0.00852, +0.01700] | 1.000 | 0.901208 | 7/15/57 | - | - | 0.910068 | +0.012257 | 1.000000 |
| ef_a2_rl | 0.909839 | +0.012027 | [+0.00835, +0.01658] | 1.000 | 0.900978 | 7/15/57 | - | - | 0.909839 | +0.012027 | 1.000000 |
| ef_a3 | 0.908056 | +0.010244 | [+0.00740, +0.01366] | 1.000 | 0.899195 | 7/15/57 | - | - | 0.908056 | +0.010244 | 1.000000 |
| ef_a3_rl | 0.912220 | +0.014408 | [+0.01035, +0.01939] | 1.000 | 0.903359 | 7/15/57 | - | - | 0.912220 | +0.014408 | 1.000000 |
| ef_a3_rl_pr | 0.912468 | +0.014657 | [+0.01066, +0.01957] | 1.000 | 0.903607 | 7/15/57 | - | - | 0.912468 | +0.014657 | 0.999553 |
| ef_a3_rl_f0 | 0.910176 | +0.012365 | [+0.00668, +0.01834] | 1.000 | 0.903420 | 5/10/59 | - | - | 0.910176 | +0.012365 | 1.000000 |
| ef_a4_rl | 0.904140 | +0.006328 | [+0.00486, +0.00795] | 1.000 | 0.895279 | 7/15/57 | - | - | 0.904140 | +0.006328 | 1.000000 |
| lp030 | 0.898315 | +0.000503 | [+0.00029, +0.00076] | 1.000 | 0.889454 | 7/15/57 | - | - | 0.898315 | +0.000503 | 0.999365 |
| lp_ef_a3_rl | 0.912150 | +0.014339 | [+0.01028, +0.01931] | 1.000 | 0.903290 | 7/15/57 | - | - | 0.912150 | +0.014339 | 0.999365 |
| lp_ef_a3_rl_pr | 0.912395 | +0.014583 | [+0.01057, +0.01946] | 1.000 | 0.903534 | 7/15/57 | - | - | 0.912395 | +0.014583 | 0.998973 |

`lp030`: leaf_prune 0.3 pruned 750 leaf nodes; kernel: tools/build_probe_kernel.py <name> --patch leafprune --set LEAF_PRUNE_MIN_EDGE_PROB=0.3

`lp_ef_a3_rl`: leaf_prune 0.3 pruned 750 leaf nodes; kernel: tools/build_probe_kernel.py <name> --patch leafprune --set LEAF_PRUNE_MIN_EDGE_PROB=0.3

`lp_ef_a3_rl_pr`: leaf_prune 0.3 pruned 750 leaf nodes; kernel: tools/build_probe_kernel.py <name> --patch leafprune --set LEAF_PRUNE_MIN_EDGE_PROB=0.3

`ef_a0`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 0, 'min_len_um': 0.0, 'relink': 0, 'prune': 0, 'skip_forks': 1}: candidates 34334, dropped 34334, re-linked 0+0, pruned nodes 0; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1

`ef_a0_rl`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 0, 'min_len_um': 0.0, 'relink': 1, 'prune': 0, 'skip_forks': 1}: candidates 34334, dropped 34334, re-linked 10293+4837, pruned nodes 0; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_RELINK=1

`ef_a1_rl`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 1, 'min_len_um': 0.0, 'relink': 1, 'prune': 0, 'skip_forks': 1}: candidates 16182, dropped 16182, re-linked 8267+2563, pruned nodes 0; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=1 --set EDGEFILTER_RELINK=1

`ef_a2_rl`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 2, 'min_len_um': 0.0, 'relink': 1, 'prune': 0, 'skip_forks': 1}: candidates 14913, dropped 14913, re-linked 5932+3930, pruned nodes 0; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=2 --set EDGEFILTER_RELINK=1

`ef_a3`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 3, 'min_len_um': 0.0, 'relink': 0, 'prune': 0, 'skip_forks': 1}: candidates 21510, dropped 21510, re-linked 0+0, pruned nodes 0; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=3

`ef_a3_rl`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 3, 'min_len_um': 0.0, 'relink': 1, 'prune': 0, 'skip_forks': 1}: candidates 21510, dropped 21510, re-linked 10293+4837, pruned nodes 0; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=3 --set EDGEFILTER_RELINK=1

`ef_a3_rl_pr`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 3, 'min_len_um': 0.0, 'relink': 1, 'prune': 1, 'skip_forks': 1}: candidates 21510, dropped 21510, re-linked 10293+4837, pruned nodes 528; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=3 --set EDGEFILTER_RELINK=1 --set EDGEFILTER_PRUNE=1

`ef_a3_rl_f0`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 3, 'min_len_um': 0.0, 'relink': 1, 'prune': 0, 'skip_forks': 0}: candidates 21680, dropped 21680, re-linked 10336+4856, pruned nodes 0; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=3 --set EDGEFILTER_RELINK=1 --set EDGEFILTER_SKIP_FORKS=0

`ef_a4_rl`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 4, 'min_len_um': 0.0, 'relink': 1, 'prune': 0, 'skip_forks': 1}: candidates 7132, dropped 7132, re-linked 4244+2888, pruned nodes 0; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=4 --set EDGEFILTER_RELINK=1

`lp_ef_a3_rl`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 3, 'min_len_um': 0.0, 'relink': 1, 'prune': 0, 'skip_forks': 1}: candidates 20853, dropped 20853, re-linked 9856+4497, pruned nodes 0; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=3 --set EDGEFILTER_RELINK=1

`lp_ef_a3_rl_pr`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 3, 'min_len_um': 0.0, 'relink': 1, 'prune': 1, 'skip_forks': 1}: candidates 20853, dropped 20853, re-linked 9856+4497, pruned nodes 464; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=3 --set EDGEFILTER_RELINK=1 --set EDGEFILTER_PRUNE=1

Synthetic-node flag self-check: **OK** (0/64 videos mismatch; totals ckpt_gap_synthetic 5383 vs ckpt_stats_gap_added_nodes 5383; ckpt_gap2_synthetic 2890 vs ckpt_stats_gap2_added_nodes 2890)
