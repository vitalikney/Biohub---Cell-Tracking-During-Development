# Friend A STEP 1 — honest 20-epoch LOEO validator

This is the single overnight entry point required by **Friend A — order of work** in `TEAM.md`.

It performs STEP 1 end to end:

1. trains the joint detector + linker **from scratch** on the fixed 126-video `6bba` side;
2. keeps all 12 `44b6` videos outside training and predicts them at checkpoints 5/10/15/20 and training `best`;
3. evaluates each graph set with the official metric and records score, edge Jaccard, node recall and `N_pred/N_est`;
4. evaluates the pilkwang primary and seed314159 secondary references with exactly the same prediction command;
5. selects the Friend A checkpoint by the official LOEO score, uploads it as `friend_a_exp02_loeo20/`, updates
   `experiments/RESULTS.md` and `CONTEXT.md`, commits, and pushes `detector-baseline-v2`.

The recipe is fixed: BCE, window 2, downsample 1,4,4, batch 4, cosine `1e-4 -> 1e-5`, seed 42,
`--max-detections 1024`, 20 full epochs, milestone checkpoints every 5 epochs. No pilkwang or team weight is loaded
for the Friend A model. Reference weights are used only after training for comparison.

## Safe stop and resume

- Press Jupyter's **Interrupt/Stop once**. The notebook terminates the child trainer and keeps
  `training_state_latest.pt`, written atomically after every completed epoch.
- Run all cells again later. Model weights, AdamW, cosine scheduler, AMP scaler, Torch/NumPy/CUDA RNG and the data-loader
  generator resume from the last completed epoch. An interrupted epoch is repeated.
- Completed checkpoint evaluations are also skipped on restart. The current prediction is repeated only if it did not
  finish and produce a valid 12-video metrics JSON.
- Do not delete `outputs/local_friend_a_exp02_loeo_scratch_20ep/active/` until STEP 1 is published.

Expected duration on the local RTX 5070 Ti is about 15 hours for training plus the checkpoint/reference predictions.
Do not submit anything to the leaderboard from this notebook.

Start Jupyter from `C:\Projects\CellTracker`, select the project Python 3.12 environment, and choose **Run All**.
The defaults perform the full run and publication. Useful overrides before Jupyter starts:

```powershell
$env:BIOHUB_DATA_DIR = "C:\Projects\CellTracker\train"
$env:BIOHUB_STEP1_AUTO_UPLOAD = "0"  # keep results local if Kaggle publication should be deferred
$env:BIOHUB_STEP1_AUTO_GIT = "0"     # keep report changes uncommitted if desired
jupyter lab
```
