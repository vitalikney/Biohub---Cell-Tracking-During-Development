# exp77: N2, a stronger distilled fine-tune of the seed314159 secondary (TRAINING ONLY, never submit)

This notebook only trains. It writes no submission file, and it must never be submitted to the competition.

It runs **two recipes in parallel** in one T4 x2 session, as two subprocesses (one per GPU, `num_workers=2` each):

| run | GPU | init | lr | loader seed | length |
|---|---|---|---|---|---|
| **n2a** | `CUDA_VISIBLE_DEVICES=0` | exp71 student `ed8c616b` (private dataset `biohub-secft-all-v1`) | 1e-5 (same as exp71) | 271828 | 1 more epoch (epoch 2) |
| **n2b** | `CUDA_VISIBLE_DEVICES=1` | pilkwang parent `9bac2fa0` | **3e-5** (3x) | 314159 (same as exp71) | 1 epoch |

**Recipe (both runs):** exp71 = y3uanm `notebook0afc5663f6` (v1).
- Teacher: the frozen ORIGINAL pilkwang secondary `9bac2fa0` (also for n2a).
- Trainable: `unet.decoder_blocks[-1]`, `unet.head` and `detect_head`. BatchNorm stays frozen.
- Detection loss: softplus at the GT centres, plus 0.5 x BCE to the teacher on non-GT voxels, plus 0.1 x feature MSE to the teacher.
- AdamW with a fresh optimizer state, batch 1, fp32, all 199 annotated videos, no validation, no augmentations.

**Cells:**
- c01-c03: exp71's cells, byte for byte (setup + trainer patch, read check, splits + parent pin).
- c04: pins the exp71 student.
- The `%%writefile` cell: the worker. It holds exp71's c04-c07 recipe and run control, with the changes marked `[exp77]`.
- c06: the launcher.
- c07: the per-student sanity (hard asserts).
- c08: the per-student export and cleanup.

**Safety, per run (kept from exp71):**
- a 40-iteration timing probe;
- `max_iters` of at most one pass over the loader;
- a 300 s DataLoader timeout, and a retry with `num_workers=0` if the probe's loader fails;
- if the real run's loader fails, the student is saved.

**Time caps:**
- Each run's hard stop is 4.5 h of training. The student is saved.
- All training must end within 5.75 h of c04.
- The launcher watchdog touches a stop file 5 min after a run's deadline, then kills the process group 20 min after it.
- If only one GPU is visible, the runs go one after the other and share the window.

**Output:**
- `/kaggle/working/secft_n2a/` and `/kaggle/working/secft_n2b/`, each with `ARTIFACT_MANIFEST.json` (`model.weight_sha256`, `parent_sha256`, `root_parent_sha256`) and `weights/unet_transformer/split_0/{edge_predictor_best.pth, config.json}`;
- `/kaggle/working/exp77_train_log.json`;
- `/kaggle/working/exp77_logs/`.
