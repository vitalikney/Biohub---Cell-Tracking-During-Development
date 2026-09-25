# haideptry/biohub-0-951-sota-deepcenter-fast-ilp-19m (V1 of 1, run 21 Sep 16:30 UTC, public 0.944 despite "0.951" in the title) - what is new vs x138
1. Base is the pre-x138 pilkwang/harmonic stack: NO flow-prior relink, NO readmit, NO sub-threshold gap filler, NO V1284 head (all those env knobs absent).
2. Adds DivNet 3D-CNN soft veto of division candidates (BIOHUB_DIVNET_VERIFY=1, BIOHUB_DIV_MIN_PROB=0.50) from dataset giorgosi/biohub-divnet-v2.
3. UNet batch size 8, CUDNN workspace cap; 4 movies post-processed in parallel threads; runtime 23m 29s (T4 x2) on the visible test.
4. Public 0.944 < 0.947 base: the DivNet veto did not help on the LB (matches our closed "DivNet veto" line).
5. Verdict: nothing to take. Source: https://www.kaggle.com/code/haideptry/biohub-0-951-sota-deepcenter-fast-ilp-19m
