# Friend A — resumable dense pipeline (STEP 1c → STEP 4 → conditional STEP 5)

This is the single local entry point requested on 2026-09-10. It continues after the completed STEP 1/1b run and does
not submit anything to the Kaggle leaderboard.

`Run All` performs, in order:

1. checks `vitaliineibauer/biohub-ft-weights` for `teacher_geff/` and `train_dense_geff/`;
2. if needed, creates the exp03B + seed314159 ensemble teacher for the fixed 126 `6bba` training videos and 12 `44b6`
   diagnostic videos, builds dense GEFF labels with GT winning within 5 µm, and uploads both requested folders;
3. trains the joint detector + linker from scratch on dense `6bba`, evaluates checkpoints 5/10/15/20 on the original
   sparse-GT `44b6` holdout, uploads the official best as `friend_a_exp03_loeo_dense/`, and records STEP 4;
4. if the best score is at least 0.70, extends teacher/dense labels to all 199 videos, retrains from scratch and uploads
   `friend_a_full199_dense/`; otherwise it runs the requested 10-epoch sparse `--det-neg-weight 0.001` fallback.

The user explicitly requested 20 dense-validator epochs in this task. This overrides the 30 epochs currently written in
`TEAM.md`; the difference is recorded in `results.json` and `experiments/RESULTS.md`.

## Safe stop and resume

- Press Jupyter **Interrupt/Stop once**. The active child process is terminated.
- Teacher generation is committed locally in small chunks; only the interrupted chunk repeats.
- Dense GEFF creation is per video and validates/reuses finished outputs.
- Training saves an atomic full state after every completed epoch: model, optimizer, cosine scheduler, AMP scaler and RNG.
  The interrupted epoch repeats; finished epochs do not.
- Completed official checkpoint evaluations and completed uploads are skipped on rerun.
- Keep `outputs/local_friend_a_exp03_loeo_dense_20ep/active/` and `train_dense/` until the pipeline is complete.

Start Jupyter from `C:\Projects\CellTracker`, select the project Python 3.12 kernel, and choose **Run All**. The notebook
defaults to the full pipeline. For a dry preflight only, start Jupyter with:

```powershell
$env:BIOHUB_DENSE_RUN_PIPELINE = "0"
jupyter lab
```
