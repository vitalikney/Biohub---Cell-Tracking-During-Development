# L2 replay - split `confirmation` (135 videos), control `lp030`

cache `C:\Users\vital\Documents\kAGGLE\Biohub - Cell Tracking During Development\data_external\friend_a_cache\friend_a_b20_exp29_friend_c\cache\friend_a_b20_exp29`; official metric; paired bootstrap over videos (2000 draws, seed 0).

| config | score | delta | 90% CI | P(d>0) | adj edge | div TP/FP/FN | 44b6 | d44b6 | 6bba | d6bba | node ratio |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| exp39 | 0.926739 | -0.000620 | [-0.00088, -0.00038] | 0.000 | 0.912826 | 16/28/71 | 0.915693 | -0.000980 | 0.930945 | -0.000481 | 1.000487 |
| lp030 | 0.927359 | +0.000000 | - | - | 0.913446 | 16/28/71 | 0.916673 | - | 0.931426 | - | 1.000000 |
| ef_a3_rl_pr | 0.942980 | +0.015622 | [+0.01223, +0.01895] | 1.000 | 0.929067 | 16/28/71 | 0.930147 | +0.013474 | 0.947869 | +0.016443 | 1.000068 |

`lp030`: leaf_prune 0.3 pruned 1435 leaf nodes; kernel: tools/build_probe_kernel.py <name> --patch leafprune --set LEAF_PRUNE_MIN_EDGE_PROB=0.3

`ef_a3_rl_pr`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 3, 'min_len_um': 0.0, 'relink': 1, 'prune': 1, 'skip_forks': 1}: candidates 36952, dropped 36952, re-linked 17860+8609, pruned nodes 1234; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=3 --set EDGEFILTER_RELINK=1 --set EDGEFILTER_PRUNE=1

Synthetic-node flag self-check: **OK** (0/135 videos mismatch; totals ckpt_gap_synthetic 19963 vs ckpt_stats_gap_added_nodes 19963; ckpt_gap2_synthetic 9602 vs ckpt_stats_gap2_added_nodes 9602)
