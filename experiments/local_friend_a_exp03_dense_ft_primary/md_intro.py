# Friend A — resumable dense fine-tune pipeline (revised 2026-09-10)

This single root notebook follows the current `TEAM.md` / `PROMPT_FRIEND_A.md`. Dense pseudo-labels are used to
**fine-tune the pilkwang primary**, not to train a model from scratch. It never submits to the leaderboard.

`Run All` performs:

1. finishes/reuses STEP 1c (`teacher_geff/`, `train_dense/`, `train_dense_geff/`);
2. runs the same-machine sparse primary fine-tune reference (1200 iterations);
3. runs dense primary variants: 1200, 2400, 1200 with `det-neg-weight=0.1`, and 1200 with intensity augmentation;
4. scores every run on the fixed 12-video `44b6` LOEO set with the official metric;
5. if the best dense variant beats the sparse reference by at least 0.005, extends dense labels to all 199 videos,
   fine-tunes the winner on the exp03 183-video split, uploads `friend_a_ft_dense_primary/`, and prints a hand-off message.

Every training command contains `--init-weights` pointing to the verified pilkwang primary checkpoint. The notebook
contains no from-scratch 20/30-epoch or all-199 scratch branch.

Expected time on the RTX 5070 Ti is about 7 hours through STEP 2 (the 2400-iteration run takes roughly twice as long
as a 1200-iteration run). If a dense recipe wins, STEP 3 adds roughly 2–3 hours including the missing teacher graphs,
dense build, two validations, and upload. These are estimates; the notebook prints and saves every subprocess log.

## Stop and resume

- Teacher inference is saved in 6-video chunks and dense GEFFs are saved per video.
- Each completed fine-tune variant and official evaluation is recorded and skipped on rerun.
- If interrupted inside a variant, only that active variant restarts; earlier variants remain complete. This loses at most
  about 1 hour for a 1200-iteration run or about 2 hours for the 2400-iteration run.
- Keep `outputs/local_friend_a_exp03_loeo_dense_20ep/active/` (the existing 138 teacher files),
  `outputs/local_friend_a_exp03_dense_ft_primary/active/`, and `train_dense/`.

Start Jupyter from `C:\Projects\CellTracker`, select the project Python 3.12 kernel, and use **Run All**. For a dry
preflight with no GPU work, uploads, or commits:

```powershell
$env:BIOHUB_DENSE_FT_RUN_PIPELINE = "0"
jupyter lab
```
