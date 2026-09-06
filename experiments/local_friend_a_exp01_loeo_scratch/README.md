# Friend A experiment 01: scratch LOEO validator

Open the root-level `friend-a-loeo-scratch.ipynb` and run all cells in the Python 3.12 project environment.
The default recipe trains for five full epochs on the fixed 126-video `6bba` manifest and validates internally on
12 `44b6` videos. The two other local `6bba` datasets are dummy-test copies and are intentionally outside the manifest.

The notebook performs a real CUDA allocation before training, rejects any pretrained-weight flags, copies the support
code into a unique `outputs/local_friend_a_exp01_loeo_scratch/<timestamp>/` directory, applies the shared training
patches, streams `train.log`, and produces:

- `artifact/edge_predictor_best.pth`
- `artifact/config.json`
- `artifact/run_config.json`
- `artifact/results.json`
- `artifact/handoff.json`

Send the artifact directory to Friend B/Vitalii. Friend B owns predictions and official evaluation. Do not submit to
the Kaggle leaderboard. Once official metrics are available, copy the final result into this folder's `results.json`,
add a row to `experiments/RESULTS.md`, and update `CONTEXT.md` as required by `TEAM.md`.

Configuration overrides use `BIOHUB_FRIEND_A_*` environment variables; the notebook prints and records the exact
command. `BIOHUB_DATA_DIR` must point to the train directory containing paired `.zarr` and `.geff` directories.
On Windows the notebook defaults to `num_workers=0` to avoid `spawn` duplicating PyTorch/CUDA DLL mappings and
exhausting the pagefile. Set `BIOHUB_FRIEND_A_WORKERS` only after increasing the Windows pagefile and re-running a smoke test.
