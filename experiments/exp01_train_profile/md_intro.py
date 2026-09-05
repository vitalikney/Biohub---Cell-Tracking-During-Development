# exp01 — training-cost profiling on Kaggle (2x T4)

Goal: measure seconds/iteration, epoch cost and GPU memory for the support-pack
`train_unet_transformer.py` recipe (window=2, downsample 1,4,4, batch 8), on a 20-video subset,
1 epoch capped at 150 iterations. No submission is produced.
