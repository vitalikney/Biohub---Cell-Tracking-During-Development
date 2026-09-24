# L2 replay - split `confirmation` (135 videos), control `ef_a3_rl_pr`

cache `C:\Users\vital\Documents\kAGGLE\Biohub - Cell Tracking During Development\data_external\friend_a_cache\friend_a_b20_exp29_friend_c\cache\friend_a_b20_exp29`; official metric; paired bootstrap over videos (2000 draws, seed 0).

| config | score | delta | 90% CI | P(d>0) | adj edge | div TP/FP/FN | 44b6 | d44b6 | 6bba | d6bba | node ratio |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| exp39 | 0.926739 | -0.016241 | [-0.01957, -0.01276] | 0.000 | 0.912826 | 16/28/71 | 0.915693 | -0.014454 | 0.930945 | -0.016923 | 1.000419 |
| ef_a3_rl_pr | 0.942980 | +0.000000 | - | - | 0.929067 | 16/28/71 | 0.930147 | - | 0.947869 | - | 1.000000 |
| ef_st_all | 0.945094 | +0.002114 | [+0.00161, +0.00262] | 1.000 | 0.931181 | 16/28/71 | 0.931314 | +0.001167 | 0.950343 | +0.002474 | 1.000000 |
| ef_sw_t3_g4 | 0.942943 | -0.000038 | [-0.00011, +0.00000] | 0.000 | 0.929030 | 16/28/71 | 0.930147 | +0.000000 | 0.947816 | -0.000052 | 1.000000 |

`ef_a3_rl_pr`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 3, 'min_len_um': 0.0, 'relink': 1, 'prune': 1, 'skip_forks': 1}: candidates 36952, dropped 36952, re-linked 17860+8609, pruned nodes 1234; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=3 --set EDGEFILTER_RELINK=1 --set EDGEFILTER_PRUNE=1

`ef_st_all`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 3, 'min_len_um': 0.0, 'relink': 1, 'prune': 1, 'skip_forks': 1}: candidates 36952, dropped 36952, re-linked 17860+8609, pruned nodes 1234; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=3 --set EDGEFILTER_RELINK=1 --set EDGEFILTER_PRUNE=1

`ef_sw_t3_g4`: edgefilter {'enable': 1, 'max_prob': 0.3, 'alt': 3, 'min_len_um': 0.0, 'relink': 1, 'prune': 1, 'skip_forks': 1}: candidates 36952, dropped 36952, re-linked 17860+8609, pruned nodes 1234; kernel: tools/build_probe_kernel.py <name> --patch edgefilter --set EDGEFILTER_ENABLE=1 --set EDGEFILTER_ALT=3 --set EDGEFILTER_RELINK=1 --set EDGEFILTER_PRUNE=1

`ef_sw_t3_g4`: swapfix {'enable': 1, 'min_gain_um': 4.0, 'min_ratio': 0.0, 'max_prob': 1.01, 'src_um': 10.0, 'max_len_um': 14.0, 'min_terms': 3}: candidates 79, swaps 79; kernel: tools/build_probe_kernel.py <name> --patch swapfix --set SWAPFIX_ENABLE=1 --set SWAPFIX_MIN_GAIN_UM=4.0 --set SWAPFIX_MIN_TERMS=3

`ef_st_all`: stitch {'enable': 1, 'min_prob': 0.0, 'max_um': 0.0, 'min_um': 0.0, 'min_chain': 0}: candidates 4675, added 4675; kernel: tools/build_probe_kernel.py <name> --patch stitch --set STITCH_ENABLE=1

Synthetic-node flag self-check: **OK** (0/135 videos mismatch; totals ckpt_gap_synthetic 19963 vs ckpt_stats_gap_added_nodes 19963; ckpt_gap2_synthetic 9602 vs ckpt_stats_gap2_added_nodes 9602)
