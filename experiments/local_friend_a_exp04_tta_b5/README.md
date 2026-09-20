# Friend A B5 — resumable test-time adaptation

Entry point: root-level `friend-a-test-time-adaptation.ipynb`.

This is the Friend A task assigned in the latest operational note in `CONTEXT.md` (2026-09-15), which supersedes the
older dense-fine-tune prompt. It evaluates three controlled modes on the honest 6bba-to-44b6 setup:

1. unchanged `friend_a_exp02_loeo20` baseline;
2. per-video BatchNorm statistics recalibration (`adabn`);
3. per-video detection-head-only EMA self-training under mild photometric consistency (`head_ema`).

Adaptation sees image Zarr stores only. The competition GEFF is opened only after all predictions for a variant exist,
by the official scorer. Each target video starts from the same untouched base checkpoint.

## Stop and resume

- Every completed video is skipped on rerun.
- `head_ema` writes a full adaptation checkpoint every 25 steps.
- Jupyter's Interrupt button is caught and saved; rerunning resumes the interrupted video.
- For a cooperative stop from another PowerShell window, create
  `C:\Projects\CellTracker\outputs\local_friend_a_exp04_tta_b5\STOP_REQUESTED`.
- `BIOHUB_TTA_MAX_VIDEOS=1` limits one invocation to one unfinished variant/video pair.

No leaderboard submission, Git commit, or dataset upload is performed automatically.

## Completed run — 2026-09-20

The full 12-video run completed on an RTX 5070 Ti in about 28 minutes. Official score:

- unchanged baseline: `0.680335`;
- guarded per-video AdaBN: `0.687615` (`+0.007279`, passes the pre-registered `+0.005` gate);
- head-only EMA: `0.677830` (`-0.002505`, rejected).

AdaBN was applied on 9 videos and fell back to the unchanged baseline on 3 videos using only the configured node-count
guard. The compact decision report and exact official per-video metrics are in `results/`.

