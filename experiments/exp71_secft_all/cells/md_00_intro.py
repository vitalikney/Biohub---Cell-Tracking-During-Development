# exp71: distilled fine-tune of the seed314159 secondary on all 199 videos (TRAINING ONLY, never submit)

This notebook only trains. It writes no submission file, and it must never be submitted to the competition.

**Recipe:** team y3uanm's public notebook `y3uanm/notebook0afc5663f6` (v1), kept verbatim where possible.
- Teacher and init: the pilkwang seed314159 secondary (sha256 `9bac2fa0...`).
- Trainable: `unet.decoder_blocks[-1]`, `unet.head` and `detect_head`. BatchNorm stays frozen because `train()` is forced to eval mode.
- Detection loss: softplus at the GT centres, plus 0.5 x BCE to the frozen teacher on non-GT voxels, plus 0.1 x feature MSE to the teacher.
- Settings: AdamW lr 1e-5, batch 1, fp32, seed 314159, no validation, no augmentations, all 199 annotated train videos.

**What exp71 adds (the recipe cells are unchanged):**
- A pin on the trainer sha (`c4f63177...`, the file x138 pins).
- A 40-iteration timing probe. After it, the real run uses `max_iters = min(19701, int(4.0*3600 / s_per_it))`, capped at one pass over the loader (18,707 windows), so it is never more than v1's single epoch.
- `num_workers=4`. The sample order is unchanged.
- A non-caching replacement for `itertools.cycle`, so host RAM does not fill up.
- A tqdm refresh interval of 60 s.
- A hard stop at 6 h of training wall time, which saves the student.
- A 300 s DataLoader timeout. If the probe's loader fails, it is retried with `num_workers=0`. If the real run's loader fails, the student is saved and the stop is flagged in the log and the manifest.
- A sanity cell.
- An export cell that writes the x138 secondary layout and a manifest with `model.weight_sha256`.

**Output:** `/kaggle/working/secft/{ARTIFACT_MANIFEST.json, weights/unet_transformer/split_0/{edge_predictor_best.pth, config.json}}` and `/kaggle/working/exp71_train_log.json`.
