# Friend A L5 — DaughterNet-B full-resolution OOF

This experiment implements the current top block of `PROMPT_FRIEND_A.md`:

- the verified 199-video / 5-fold split from `experiments/l2_daughternet/splits.json`;
- the current L2 v2 labels, real-pool hard examples, optimiser, balanced sampling, and per-source readout;
- a new image view only: full XY resolution, `16x64x64` crops, lags `-2..+3`, random initialisation;
- held-out-fold probabilities for every row of `experiments/l2_daughternet/coords_exp39.parquet`;
- exact final columns `stem,node_id,fold,p_cont,p_par,p_dau` in `oof_nodes.parquet`.

## Run

Start Jupyter from `C:\Projects\CellTracker`, select the project Python 3.12 environment, and open
`friend-a-l5-daughternet-b.ipynb` from that directory. Run cells in order. The notebook performs a GPU preflight and a
small end-to-end smoke test before the full five-fold run.

The full v2 crop cache is about 25 GiB under
`outputs/local_friend_a_l5_daughternet_b/active_v2_pool/cache`. It is deliberately outside Git. GPU training streams those
crops from the memmap so the 16 GB RTX card does not have to hold the whole training set.

The practical estimate for the complete v2 job is **14–22 hours**: roughly 1–2 hours for the cache, 12–18 hours for
five folds (less if early stopping fires), and 1–2 hours for the 1,012,255-node OOF scoring pass.
This is an estimate, not a deadline guarantee; the notebook status shows the actual per-epoch times.

## Stop and resume

- During cache construction, interrupting the notebook keeps every completed video. Rerunning the training cell
  continues the unfinished videos.
- During training, the end of every epoch is saved to `folds/fold_k/last.pt`. Interrupting the notebook keeps the last
  completed epoch; rerun the same cell to continue it.
- For a graceful training stop after the current epoch, create the file printed as `stop_file` in the notebook status.
  The notebook also contains a helper cell for use from a second kernel.
- Node scoring writes one parquet per video. An interrupt or `STOP_SCORING` preserves completed videos; rerun the cell
  to continue.

Do not delete the `active_v2_pool` output directory between resumes. `best.pt`, `last.pt`, caches and per-video score files are
run artifacts and must not be committed. Only the final `oof_nodes.parquet` belongs in this experiment folder.
