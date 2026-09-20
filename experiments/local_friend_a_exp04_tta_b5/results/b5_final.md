# Friend A B5 — test-time adaptation results

The resumable notebook completed all 36 video/variant records on the fixed 12-video 44b6 validation set. The base
checkpoint was trained only on 6bba. Adaptation read target `.zarr` images without labels; GT `.geff` files were opened
only after prediction by the official scorer.

Gate: an adapted variant must beat the unchanged baseline by at least +0.005 on the official all-12 score.

| variant | official score | delta | raw edge J | node recall | division J | gate |
|---|---:|---:|---:|---:|---:|:---:|
| baseline | 0.680335 | +0.000000 | 0.680886 | 0.853079 | 0.000000 | reference |
| AdaBN | **0.687615** | **+0.007279** | **0.688145** | **0.865347** | 0.000000 | **pass** |
| head-only EMA | 0.677830 | -0.002505 | 0.678461 | 0.851586 | 0.000000 | fail |

AdaBN is the winner. It improves raw edge Jaccard by +0.00726 and node recall by +0.01227. The unsupervised node-count
guard accepted AdaBN on 9/12 videos and reused the unchanged baseline on three unstable videos. Across individual
videos the final guarded AdaBN result has 6 wins, 3 losses and 3 fallback ties; its unweighted median per-video
adjusted-edge delta is +0.00167, while the official micro-aggregated improvement is +0.00728.

Head-only EMA is rejected: it loses 0.00251 overall and is worse on 10/12 videos.

## AdaBN per-video audit

Division Jaccard is zero for every variant, so each per-video score below is its adjusted edge Jaccard.

| dataset | baseline | guarded AdaBN | delta | selected |
|---|---:|---:|---:|---|
| 44b6_12dfb391 | 0.83310 | 0.84325 | +0.01015 | AdaBN |
| 44b6_1d530831 | 0.67582 | 0.62461 | -0.05121 | AdaBN |
| 44b6_2a2eff9f | 0.77764 | 0.82364 | +0.04601 | AdaBN |
| 44b6_74d0c52e | 0.69289 | 0.69289 | +0.00000 | baseline fallback |
| 44b6_7a302da0 | 0.63384 | 0.63384 | +0.00000 | baseline fallback |
| 44b6_87bba6c4 | 0.47062 | 0.47027 | -0.00035 | AdaBN |
| 44b6_9be80b04 | 0.59468 | 0.59802 | +0.00335 | AdaBN |
| 44b6_a21120c2 | 0.68851 | 0.66219 | -0.02632 | AdaBN |
| 44b6_c50204e0 | 0.47664 | 0.50271 | +0.02607 | AdaBN |
| 44b6_d2f34f90 | 0.81047 | 0.84431 | +0.03384 | AdaBN |
| 44b6_d5e7d891 | 0.61993 | 0.64344 | +0.02352 | AdaBN |
| 44b6_e28840c6 | 0.77829 | 0.77829 | +0.00000 | baseline fallback |

The fallback decisions were label-free: candidate node ratios were 1.313, 0.898 and 0.855, outside the configured
range `[0.90, 1.05]`. Total wall time from the first prediction to the final report was about 28 minutes on an RTX
5070 Ti. Nothing was submitted to the leaderboard.

Exact official per-video scorer outputs are stored beside this report as `metrics_baseline.json`, `metrics_adabn.json`
and `metrics_head_ema.json`.
