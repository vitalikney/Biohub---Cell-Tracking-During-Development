# Friend A B20 — DivNet division ranking

Entry point: root-level `friend-a-b20-divnet.ipynb`.

This is the current Friend A task from the 2026-09-18 top block of `PROMPT_FRIEND_A.md`. The old dense fine-tune and
B5 TTA queues are cancelled. The notebook performs, in order:

1. dependency and CUDA preflight;
2. one-video end-to-end smoke test;
3. resumable public-pipeline pass 1 over all 199 local train videos, including peak probabilities, post-gap
   checkpoints and DeepCenter scores;
4. resumable DivNet scoring of every admissible orphan/steal second-child candidate within 15 microns;
5. resumable pass 2 for the exact public control and the six pre-registered `top-k x min-score` variants;
6. official all-199 metric table and the team gate.

## Stop and resume

- Interrupt the Jupyter kernel. The active subprocess is terminated and completed videos/batches remain reusable.
- Or create `C:\Projects\CellTracker\outputs\local_friend_a_b20_divnet\STOP_REQUESTED`. Inference stops after the
  current video; DivNet stops after the current batch; pass 2 stops after the current video.
- Run All again. Existing raw GEFFs, pass-1 NPZs, per-video DivNet files and pass-2 GEFFs are skipped.
- Use `BIOHUB_B20_MAX_VIDEOS=1` for a development run or `BIOHUB_B20_RUN=0` for preflight only.

Nothing is submitted to the leaderboard and no Git push is performed automatically. Compact final results are copied
to `results/b20_final.{json,md}` for review and commit.
