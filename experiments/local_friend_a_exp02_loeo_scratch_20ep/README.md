# Friend A STEP 1 — 20-epoch honest LOEO validator

Run the root-level `friend-a-step1-loeo-scratch-20ep.ipynb` with **Run All** from the repository workspace.
It is the only execution entry point: training, resumable checkpoints, official evaluation, artifact selection,
Kaggle weights upload, reporting, commit, and branch push are orchestrated by the notebook.

The prepared recipe follows `TEAM.md` Friend A STEP 1 exactly. Results are intentionally absent until the run finishes.
The notebook will write `results.json` here, append/update the `local Friend A exp02` row in `experiments/RESULTS.md`,
add a one-line operational note to `CONTEXT.md §14`, upload the official-best checkpoint as
`vitaliineibauer/biohub-ft-weights/friend_a_exp02_loeo20/`, and push the result commit to `detector-baseline-v2`.

Safe interruption state and all large outputs stay under
`outputs/local_friend_a_exp02_loeo_scratch_20ep/active/` and are git-ignored.
