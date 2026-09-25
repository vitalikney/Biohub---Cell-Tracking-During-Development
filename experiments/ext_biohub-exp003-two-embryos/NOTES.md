# denpugovkin/biohub-exp003-two-embryos (V5 of 5, run 24 Sep 20:37 UTC, public 0.885 = its V1 parent) - what is new vs x138
1. Not an x138 derivative: a clean "no-hub" rebuild of the pilkwang support-pack tracker (TemporalUNet3D + transformer, threshold 0.970, 8-view YX TTA, ILP, one-frame gap close, short-track filter).
2. Negative result reported in its TL;DR: fine-tuning the detector 1 epoch on 4 FOVs lost 0.0046 on one held-out FOV (0.9737 vs 0.9783) - excluded.
3. States that the host's current division metric "requires local directed branches" and that the notebook has "no fake ancestral hub" (i.e. an earlier hub exploit on the division metric was closed).
4. Metric notes in the notebook: no clamp at 1 on the N_pred term, so under-counting nodes can push the adjusted edge term above J.
5. Verdict: useful only as a data point (tiny fine-tunes hurt); nothing to copy. Source: https://www.kaggle.com/code/denpugovkin/biohub-exp003-two-embryos
