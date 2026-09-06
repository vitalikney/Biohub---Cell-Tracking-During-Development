# TEAM.md — roles, onboarding and rules (2026-09-06)

Read `CONTEXT.md` first (goal, metric facts, results, plan). This file says who does what and how we exchange work.

## Roles
| Who | Hardware | Responsibility |
|---|---|---|
| Vitalii (+ Claude) | Kaggle 2xT4 (30 GPU-h/week) | LB probes (4/day, one change each, log in CONTEXT §11), submission notebooks, Kaggle weights dataset, merging results, CONTEXT/RESULTS upkeep |
| Friend A | RTX 5070 Ti 16 GB | **Training.** (1) leak-free validator: train from scratch on 6bba only (split `experiments/_lib/loeo_train6bba_val44b6.json`), 5-10 epochs [running]; (2) then the same recipe from scratch on ALL 199 videos for 30-50 epochs (1-2 days) as a candidate primary/secondary for the public pipeline; (3) model-recipe experiments judged on the validator (sparse-label loss, window 3, augmentation, epochs) |
| Friend B | RTX 5070 12 GB | **Local public pipeline + honest evaluation.** (1) [start now, CPU] port the public 0.941 notebook's post-processing (cell 14: dual-seed blend, motion relink, gap closing, safe divisions, DeepCenter veto, short-track filter; env knobs BIOHUB_*) into a local script that takes prediction .geff + GT so its ~40 knobs can be tuned locally; (2) when Friend A's checkpoint exists: predictions on the 12 44b6 videos (+ 48-video set), official metric, compare pipeline stages and our post-proc findings honestly; (3) only if time remains: dense pseudo-labels feasibility (FOCUS-3D first with stop criteria; Zebrahub only as a one-day fallback) — est. 2-3 days on the 5070 |

## Onboarding (local machine)
1. `pip install kaggle` and put your `kaggle.json` in `~/.kaggle/`. Download the data:
   `kaggle competitions download -c biohub-cell-tracking-during-development` (~88 GB zip) and unzip to
   `biohub-cell-tracking-during-development/` in the repo root (git-ignored).
2. Python 3.12, PyTorch with CUDA 12.8+ (Blackwell), then
   `pip install tracksdata "geff>=1.1.3.1.1" "polars>=1.36" "rustworkx>=0.17.1" "zarr>=3.0.10,<4" scipy scikit-image tqdm dask networkx pandas scikit-learn pyscipopt ilpy blosc2`.
3. Pretrained weights + code: Kaggle dataset `pilkwang/biohub-tracking-support-pack-50ep-v1` (repo/ and weights/);
   the support-pack code is also in `tools/repo/` (scripts + src) without weights.
   **Our weights: private Kaggle dataset `vitaliineibauer/biohub-ft-weights`** — sasyami and gsfatakhov are collaborators
   with edit rights (added 2026-09-06). Layout: one subfolder per experiment (`exp03B/`, `exp08/`, ...) with
   `edge_predictor_best.pth` + `config.json` (written by the training script). To upload a new checkpoint:
   `kaggle datasets download -d vitaliineibauer/biohub-ft-weights --unzip -p ds` -> add your folder -> write
   `ds/dataset-metadata.json` with `{"id": "vitaliineibauer/biohub-ft-weights", "title": "biohub-ft-weights"}` ->
   `kaggle datasets version -p ds --dir-mode zip -m "<exp name>: <recipe>"`. Or just send the two files to Vitalii.
   Every checkpoint gets a row in `experiments/RESULTS.md` (recipe, data split, iterations, seed, and which video
   set it was scored on). Note: local scores on train videos are leaky for pilkwang-initialised models (they saw
   all 199 videos) — our 0.96-0.99 holdout numbers gave 0.899 on the LB; see CONTEXT.md §11.
4. Smoke test: `python tools/score_geffs.py <dir with prediction .geff files>` (needs the train folder) — must print a score.
5. Training locally: `tools/repo/scripts/train_unet_transformer.py` with our patches applied by
   `experiments/_lib/train_patches.py` (`apply_train_patches(path)`), e.g.
   `--init-weights <pth> --amp --no-grad-ckpt --seed 42 --det-loss bce --num-workers 4` (see `experiments/exp03_finetune_ab/finetune_ab.py`
   for the exact command line and `--splits` JSON format). Set `BIOHUB_DATA_DIR` to the train folder; run from the repo copy with `PYTHONPATH=src`.
   16 GB: batch 4-6 without grad checkpointing, or batch 8 with it.
6. Prediction: `scripts/predict_unet_transformer.py --data-dir <train> --splits <json> --split 0 --weights <pth> --det-threshold 0.965 --use-ilp --ilp-appearance-weight 0 --ilp-disappearance-weight 2 --ilp-division-weight 1.2`
   (ensemble option via `experiments/_lib/predict_patches.py`, env `BIOHUB_ENSEMBLE_WEIGHTS`). Post-process with `tools/postproc.py`.

## Rules
- One experiment = one folder `experiments/local_<name>_expNN_<slug>/` with the command line / config and a results JSON; one row in `experiments/RESULTS.md` (state the video set: hold12 / divset36 / 48 / LOEO-44b6 / LB).
- Commit as yourself; no secrets, no data, no prediction graphs in git (zip them elsewhere if needed). Weights go to the Kaggle dataset (subfolder per experiment with `edge_predictor_best.pth` + `config.json`).
- Validation truth: anything initialised from pilkwang weights is leaky on train videos (they trained on all 199). Until the from-scratch 6bba model exists, only the LB is trustworthy for linking/division aggressiveness; model comparisons need >= 48 videos (seed noise ±0.005).
- Do not submit to the LB yourself; send the candidate (kernel or weights) to Vitalii — LB slots are budgeted (4/day).
- Update `CONTEXT.md` §6 (results) and §10/§11 (plan) when you finish something; keep entries short and dated.
