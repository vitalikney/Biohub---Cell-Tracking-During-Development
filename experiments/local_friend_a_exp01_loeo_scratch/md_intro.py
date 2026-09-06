# Friend A — leak-free LOEO validator from scratch

This notebook implements the first task assigned to Friend A in `TEAM.md`:

- train **from scratch** on the fixed `6bba` side of
  `experiments/_lib/loeo_train6bba_val44b6.json`;
- use the 12 fixed `44b6` videos only for validation;
- run 5–10 full epochs (default: 5) on a single 16 GB GPU;
- save a self-contained hand-off artifact for Friend B/Vitalii.

The current manifest intentionally contains 126 training videos rather than all 128 local `6bba` videos. The two
excluded IDs are the public dummy-test copies (`6bba_05b6850b` and `6bba_05db0fb1`). The manifest is the source of
truth for this experiment.

Important:

1. Start Jupyter from the repository root and select the Python 3.12 project environment.
2. Run all cells. Training starts automatically and can take several hours.
3. This notebook never loads pilkwang or team checkpoints. The generated command is rejected if it contains
   `--init-weights` or `--unet-weights`.
4. The per-epoch `acc * recall` printed by the training script is only an internal sparse-GT diagnostic. It is **not**
   the official competition score. Friend B performs prediction and official evaluation afterwards.
5. Do not submit anything to the leaderboard from this notebook.

You may override settings before starting Jupyter, for example:

```powershell
$env:BIOHUB_DATA_DIR = "C:\path\to\biohub-cell-tracking-during-development\train"
$env:BIOHUB_FRIEND_A_EPOCHS = "7"
jupyter lab
```
