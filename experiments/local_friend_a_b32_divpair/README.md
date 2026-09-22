# Friend A B32 — division pair model

Entry point: root-level `friend-a-b32-divpair.ipynb`.

## Status: stopped honestly at Step 1 (2026-09-22)

The registered 15 um orphan-only pool covers **58/151 = 38.4%** of GT
divisions, far below the required 90%. Increasing the parent radius to its
useful 30 um ceiling changes this to only 59/151. A stage audit shows that the
source graph contains a matched parent and both matched daughters for only
121/151 = 80.1% of divisions, so no radius can meet the gate. Training is
therefore intentionally not started. See
`results/b32_step1_candidate_audit.md` for the complete diagnosis.

This is the 22 September B32 task from `PROMPT_FRIEND_A.md`: replace the
parent-only DivNet decision with a classifier of the complete triple
`(parent, existing daughter, orphan daughter)` while leaving detections,
ordinary links, weights and post-processing unchanged.

## Registered recipe

- source graph: B20 `ckpt/<stem>.npz`, immediately before the public division stage;
- parent has exactly one next-frame child;
- candidate is an unclaimed, non-synthetic next-frame node within 15 um;
- sister separation is 5–20 um and candidate DeepCenter score is at least 0.20;
- the public divergence and symmetry gates are disabled (the model replaces them);
- a positive requires the parent and the two distinct daughters to match one GT
  division locally within 7 um;
- input: lags `[-1, 0, +1, +2]`, parent marker, d1 marker, d2 marker;
- model: published DivNet U-Net/GAP trunk plus standardised B20 geometry features;
- the five public channels/head weights are copied exactly; new marker and
  geometry weights start at zero;
- two honest folds by embryo, 25 epochs by default, AdamW, weighted BCE, batch 32,
  eight axis reflections and mild image-only brightness jitter;
- OOF pass 2 grid: thresholds 0.5/0.7/0.9 times public/double/no caps;
- gate: +0.005 score and adjusted-edge delta >= -0.001 on all 199, 44b6 and
  6bba separately, with exactly the control node total.

To keep 20–30 epochs inside the deadline, the training crop cache contains all
positive triples and a deterministic negative reservoir per video: half the
most plausible geometric confusers and half random negatives (default 32
negatives per positive, 16–192 per video). BCE `pos_weight` is calculated from
that cache. This selection is fixed before either fold is trained. Final OOF
inference scores **every** registered candidate, not just the training reservoir.

## Stop and resume

The following are atomic and reusable:

- one candidate table per video;
- one fixed crop cache per video;
- `last.pt` and `best.pt` after every fold epoch, including optimiser/scaler/RNG;
- one OOF score file per video plus an intra-video partial checkpoint;
- one completed GEFF per pass-2 variant/video;
- one final-model checkpoint per epoch, only if the gate passes.

Use **Interrupt Kernel**, or create:

`C:\Projects\CellTracker\outputs\local_friend_a_b32_divpair\STOP_REQUESTED`

Remove the marker and run all cells again to resume. A cooperative stop can wait
until the current small scoring batch finishes.

## Environment overrides

```powershell
$env:BIOHUB_DATA_DIR = "C:\Projects\CellTracker\train"
$env:BIOHUB_B32_RUN = "0"          # preflight only
$env:BIOHUB_B32_MAX_VIDEOS = "4"   # balanced 44b6/6bba developer run
$env:BIOHUB_B32_EPOCHS = "25"
$env:BIOHUB_B32_BATCH_SIZE = "32"
$env:BIOHUB_B32_SCORE_BATCH_SIZE = "64"
jupyter lab
```

Do not change recipe variables in an existing output directory: the runner
checks a fingerprint and refuses to mix incompatible caches.

## Outputs

Runtime output: `outputs/local_friend_a_b32_divpair/`.

- `results/step1_candidates.json` — coverage and candidate counts;
- `folds/*/{last,best}.pt`, `history.json` — resumable training;
- `results/step2_oof_metrics.json` — per-embryo DivPair vs parent-DivNet;
- `results/divpair_*.json` — official pass-2 metrics;
- `result.md` / `results.json` — registered gate decision.

Only if a full 199-video variant passes, the runner trains all 199 and prepares
`weights_dataset/friend_a_divpair/{model.pt,divpair_infer.py,params.json}`.
It never submits to the leaderboard or publishes a Kaggle dataset automatically.

## Expected order and timing

1. Candidate tables: measured at a few minutes on the local CPU.
2. Fixed crop cache: image I/O, expected roughly 1–3 hours.
3. Two folds: GPU, expected roughly 1–3 hours total after caching.
4. Full OOF scoring: GPU + image I/O, likely the longest stage (several hours).
5. Nine pass-2 variants: CPU, roughly 2–4 hours using the existing B20 cache.

These are planning estimates; the notebook prints measured per-epoch progress.
