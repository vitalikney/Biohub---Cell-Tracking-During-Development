# Friend A exp38 — public exp29 + AdaBN

Entry point: root-level `friend-a-exp38-public-adabn.ipynb`.

This is the current Friend A task after B20 and B31 were closed.  It ports the
successful B5 per-video BatchNorm recalibration to both public exp29 models:

- primary pilkwang;
- secondary seed314159.

The notebook runs the fixed 12-video 44b6 regression check through the exact
public exp29 port.  These public weights saw the videos, so the result checks
only for regressions, node-count stability, and runtime; it is not an honest
validation score and is not used to tune the recipe.

## Registered recipe

- reload both untouched base checkpoints for every video;
- reset only `BatchNorm3d` running statistics;
- `momentum=None`, batch size 2, non-overlapping windows in chronological order;
- no gradients, optimiser, pseudo-labels, or GEFF access during adaptation;
- run the unmodified exp29 inference/post-processing stack;
- accept adapted output only when `N_adapted / N_base` is in `[0.90, 1.05]`;
- otherwise copy the untouched exp29 output for that video.

The notebook automatically reuses Friend A's B20 exp29 raw cache at
`outputs/local_friend_a_b20_divnet/cache/friend_a_b20_exp29/raw`.  If it is not
available, the unchanged baseline is calculated once and cached locally.

## Stop and resume

The unit of reuse is one completed video.  Use **Interrupt Kernel**, or create:

`C:\Projects\CellTracker\outputs\local_friend_a_exp05_public_adabn\STOP_REQUESTED`

The stop marker is checked between videos and between AdaBN batches.  If a
public inference subprocess is interrupted, only its current video is repeated;
all completed videos and checkpoint pairs remain reusable.  Run All resumes.

Useful environment variables before starting Jupyter:

```powershell
$env:BIOHUB_DATA_DIR = "C:\Projects\CellTracker\train"
$env:BIOHUB_EXP38_MAX_VIDEOS = "1"  # one unfinished video per Run All
$env:BIOHUB_EXP38_RUN = "0"         # preflight only
jupyter lab
```

Outputs go to `outputs/local_friend_a_exp05_public_adabn/`.  The final report is
`result.md`; exact metrics are under `metrics/`.  The copy-ready Kaggle function
cell is `kaggle_adabn_cell.py`.  Nothing is submitted or uploaded automatically.

The completed 12-video regression report is archived in `results/exp38_final.md`
with exact per-video scorer outputs. The registered guarded AdaBN variant scored
0.893524 versus 0.900098 for the unchanged baseline, so it is rejected and no
leaderboard probe is requested.

