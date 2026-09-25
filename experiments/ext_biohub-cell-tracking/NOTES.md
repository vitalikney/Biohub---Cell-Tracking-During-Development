# kunaldesale2408/biohub-cell-tracking (public 0.953, V10 of 10, run 24 Sep 06:13 UTC) - what is new vs x138
1. Nothing functional: a cell-by-cell diff against `experiments/ext_x138/biohub-x138.ipynb` shows only blank-line changes and one extra empty cell (78 diff lines, all whitespace).
2. Same 4 datasets (pilkwang deepcenter prior v1, temporal-unet3d seed314159 v1, tracking support pack 50ep v1, anvithpothula/biohub-v1284-head-s075), same env knobs, same thtennant chain + V1284 head.
3. Public score 0.953 = x138's 0.953; it sorts above x138 on the Code tab only by votes/tie-break (194 votes vs 176), not a higher score.
4. Visible-test runtime 23m 34s on T4 x2 (x138: 20m 28s) - same pipeline, noise.
5. Verdict: a verbatim re-upload of x138; no new idea to take. Source: https://www.kaggle.com/code/kunaldesale2408/biohub-cell-tracking (read 25 Sep 11:05 UTC).
