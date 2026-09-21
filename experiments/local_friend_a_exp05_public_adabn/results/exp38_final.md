# Friend A exp38 — public exp29 + per-video AdaBN

The regression set is the fixed 12-video 44b6 set. Public weights saw these videos, so this is a regression/timing check, not an honest model-selection validation.

| variant | official score | delta | adjusted edge | division J | node recall |
|---|---:|---:|---:|---:|---:|
| baseline | 0.900098 | +0.000000 | 0.895337 | 0.047619 | 0.987257 |
| candidate_adabn | 0.856435 | -0.043663 | 0.851673 | 0.047619 | 0.981254 |
| guarded_adabn | 0.893524 | -0.006575 | 0.887968 | 0.055556 | 0.990621 |

| video | base nodes | AdaBN nodes | ratio | decision | adaptation s | inference s |
|---|---:|---:|---:|---|---:|---:|
| 44b6_12dfb391 | 45357 | 51240 | 1.1297 | baseline_fallback | 6.9 | 74.6 |
| 44b6_1d530831 | 36882 | 37651 | 1.0209 | candidate_adabn | 6.3 | 59.1 |
| 44b6_2a2eff9f | 40941 | 45810 | 1.1189 | baseline_fallback | 6.8 | 67.7 |
| 44b6_74d0c52e | 8968 | 12836 | 1.4313 | baseline_fallback | 6.2 | 44.8 |
| 44b6_7a302da0 | 46264 | 55163 | 1.1924 | baseline_fallback | 6.4 | 67.0 |
| 44b6_87bba6c4 | 30188 | 31026 | 1.0278 | candidate_adabn | 7.1 | 52.5 |
| 44b6_9be80b04 | 27032 | 50299 | 1.8607 | baseline_fallback | 6.4 | 64.9 |
| 44b6_a21120c2 | 22138 | 21901 | 0.9893 | candidate_adabn | 6.1 | 48.9 |
| 44b6_c50204e0 | 39730 | 43998 | 1.1074 | baseline_fallback | 6.8 | 59.5 |
| 44b6_d2f34f90 | 15840 | 17651 | 1.1143 | baseline_fallback | 6.2 | 47.1 |
| 44b6_d5e7d891 | 44385 | 44828 | 1.0100 | candidate_adabn | 6.6 | 58.7 |
| 44b6_e28840c6 | 28431 | 58179 | 2.0463 | baseline_fallback | 6.2 | 72.0 |

Guard accepted AdaBN on 4/12 videos. Bounds: [0.90, 1.05].
No leaderboard submission is performed by this notebook.
The copy-ready Kaggle cell is `experiments/local_friend_a_exp05_public_adabn/kaggle_adabn_cell.py`.

## Decision

The public-stack regression check fails: unguarded AdaBN loses 0.043663 and the registered label-free guard still
loses 0.006575 against the unchanged exp29 baseline. The guard produces two wins, two losses and eight fallback ties;
the two accepted losses outweigh the wins. Node recall rises by 0.003365, but adjusted edge Jaccard falls by 0.007368,
so the extra detections do not translate into better tracking.

AdaBN is therefore rejected for exp38 and no leaderboard probe is requested. The honest B5 improvement remains a
valid result for the scratch LOEO checkpoint, but it does not transfer safely to the already in-sample public stack.
Total wall time was about 34 minutes on the RTX 5070 Ti, including inference, three post-processing passes and official
scoring; adaptation itself took about 78 seconds across all 12 videos.
