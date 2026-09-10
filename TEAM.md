# TEAM.md — roles, onboarding and rules (2026-09-06)

Read `CONTEXT.md` first (goal, metric facts, results, plan). This file says who does what and how we exchange work.

## Roles
| Who | Hardware | Responsibility |
|---|---|---|
| Vitalii (+ Claude) | Kaggle 2xT4 (30 GPU-h/week) | LB probes (5/day, one change each, log in CONTEXT §11), submission notebooks, Kaggle weights dataset, merging results, CONTEXT/RESULTS upkeep |
| Friend A (Kaggle: Sasyami) | RTX 5070 Ti 16 GB | **Training.** (1) leak-free validator: train from scratch on 6bba only (split `experiments/_lib/loeo_train6bba_val44b6.json`), 5-10 epochs [running]; (2) then the same recipe from scratch on ALL 199 videos for 30-50 epochs (1-2 days) as a candidate primary/secondary for the public pipeline; (3) model-recipe experiments judged on the validator (sparse-label loss, window 3, augmentation, epochs) |
| Friend B (Kaggle: gsfatakhov) | RTX 5070 12 GB | **Local public pipeline + honest evaluation.** (1) [start now, CPU] port the public 0.941 notebook's post-processing (cell 14: dual-seed blend, motion relink, gap closing, safe divisions, DeepCenter veto, short-track filter; env knobs BIOHUB_*) into a local script that takes prediction .geff + GT so its ~40 knobs can be tuned locally (see 'Friend B start kit' below for the exact steps and the order of work after it); (2) when Friend A's checkpoint exists: predictions on the 12 44b6 videos (+ 48-video set), official metric, compare pipeline stages and our post-proc findings honestly; (3) only if time remains: dense pseudo-labels feasibility (FOCUS-3D first with stop criteria; Zebrahub only as a one-day fallback; synthetic volumes dropped - 1st place found no gain) — est. 2-3 days on the 5070 |

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
   `--init-weights <pth> --amp --no-grad-ckpt --seed 42 --det-loss bce --num-workers 0` on Windows (see `experiments/exp03_finetune_ab/finetune_ab.py`
   for the exact command line and `--splits` JSON format). Set `BIOHUB_DATA_DIR` to the train folder; run from the repo copy with `PYTHONPATH=src`.
   16 GB: batch 4-6 without grad checkpointing, or batch 8 with it. Windows workers use `spawn`; each imports
   PyTorch/CUDA DLLs and may exhaust the pagefile (`WinError 1455`), so keep workers at 0 unless a larger pagefile is verified.
6. Prediction: `scripts/predict_unet_transformer.py --data-dir <train> --splits <json> --split 0 --weights <pth> --det-threshold 0.965 --use-ilp --ilp-appearance-weight 0 --ilp-disappearance-weight 2 --ilp-division-weight 1.2`
   (ensemble option via `experiments/_lib/predict_patches.py`, env `BIOHUB_ENSEMBLE_WEIGHTS`). Post-process with `tools/postproc.py`.

## Friend B start kit (2026-09-07)
Goal: run the public 0.941 pipeline locally on the 12 LOEO 44b6 videos and expose its post-processing knobs.
1. Data: only the 12 videos in `experiments/_lib/loeo_train6bba_val44b6.json` (key `holdout`) are needed first
   (zarr + geff pairs, ~10 GB); the full 80 GB train set can come later.
2. Code: `experiments/exp06_pipeline_ft03B/exp06-pipeline-ft03B.ipynb` = the public notebook + our primary override.
   Cell 0 = env knobs (~40 `BIOHUB_*`), cell 2 = helpers, cell 3 = deps + support-pack import, cell 5 = dual-seed
   inference (TemporalUNet3D primary + secondary) + DeepCenter, cell 6 = post-processing (motion relink, gap closing,
   safe divisions, DeepCenter veto, short-track filter) -> this is the part to port into a script that takes cached
   predictions + GT and prints the official metric per stage.
3. Weights: Kaggle datasets `pilkwang/biohub-tracking-support-pack-50ep-v1` (primary + code), `pilkwang/biohub-temporal-unet3d-seed314159-v1`
   (secondary), `pilkwang/biohub-deepcenter-unet3d-center-prior-v1` (veto model), ours `vitaliineibauer/biohub-ft-weights/exp03B`.
   `kaggle datasets download -d <ref> --unzip -p <dir>` for each.
4. Deliverable: `tools/public_pp.py` (or similar) with `--pred-dir <cached raw graphs> --gt-dir <train> --env K=V...`,
   caching the GPU stages (inference + DeepCenter scores) once so that knob sweeps are CPU-only. Then one table:
   raw ILP / +relink / +gap / +divisions / +veto / +short-track filter on the 12 videos with exp03B primary.
5. Expected cost on a 5070: GPU stages ~30-40 min for 12 videos (two UNets + DeepCenter + ILP), then each knob sweep
   is minutes on CPU. First check request: exp23 (fine-tuned seed314159 secondary) vs the pilkwang secondary.

**Friend B — order of work (revised 2026-09-10 18:00 after the audit in CONTEXT §14). Self-contained.**

Why the revision: on the LB only two kinds of change have transferred - fine-tuned weights (+0.004) and inference-time TTA
stacks (+0.006, public 0.947). A from-scratch model must beat pilkwang's 50-epoch model to help and is at 0.68 honest; with
the recipe freeze on 24 Sep that is a long shot. So dense pseudo-labels are now used to FINE-TUNE pilkwang, not to train
from scratch. Scratch runs become optional research.

STEP 1 (now, ~4 h GPU): teacher detections for all 199 train videos - unchanged (exp03B + seed314159 ensemble, det 0.965,
  no ILP, `BIOHUB_ENSEMBLE_WEIGHTS`; output `predictions/teacher/split_0/<stem>.geff`; zip -> dataset `teacher_geff/`).
  Coordinate with Friend A: whoever starts first does it; the other skips.
STEP 2 (CPU, same day): dense training set `train_dense/` - unchanged (teacher UNION GT, dedupe 5 um GT wins, GT edges only,
  zarr junctions, `dense_stats.csv`, `tools/build_dense_gt.py`, geff to the dataset as `train_dense_geff/`).
STEP 3 (~1 h GPU per run, 12 GB is enough at batch 4 + grad ckpt): DENSE FINE-TUNE of the SECONDARY (pilkwang seed314159) on
  6bba only: `--init-weights <seed314159 pth>`, `BIOHUB_DATA_DIR=train_dense`, `--max-iters 1200 --lr 5e-5 --det-loss bce
  --max-detections 0 --seed 42`, split `experiments/_lib/loeo_train6bba_val44b6.json`. Score raw on the 12 44b6 videos (det 0.965 +
  ILP, `tools/score_geffs.py`). References on the same videos: sparse fine-tune of the primary = 0.8825 (exp11 B), pretrained
  primary 0.8798, pretrained secondary 0.8691 (rows in RESULTS.md). Also run the SPARSE fine-tune of the secondary on 6bba
  (same command with the real train dir) so the dense-vs-sparse delta is measured on the same model. Keep the dense variant only
  if it beats sparse by >= 0.005 on 44b6. Folder `experiments/local_friend_b_exp01_dense_ft_secondary/`, RESULTS row.
STEP 4 (CPU + short GPU, in parallel with 3): local port of the public pipeline post-processing ('Friend B start kit' above).
  Its value went UP: the TTA stack variants (Z-flip views, secondary edge-TTA weight 0.5/0.75/1.0, DeepCenter threshold,
  replacing rot90/transpose views by the training-consistent axis-flip group) can be compared locally on cached graphs
  instead of one LB slot each. First customers: exp31 (Z-flip) and exp32 (secondary exp23) configs.
STEP 5 (optional research, only if 1-4 are done): dense scratch run on 6bba (20 epochs) - the old bet, now low priority.

**Friend A — order of work (revised 2026-09-10 18:00 after the audit in CONTEXT §14). Self-contained.**

Same reasoning as for Friend B above: dense labels now feed FINE-TUNING of pilkwang (proven to transfer), scratch training is
demoted to research. Your 5070 Ti takes the primary side; Friend B takes the secondary side.

STEP 1b (20 min GPU): score the epoch-20 scratch model on 12 of its own TRAIN 6bba videos - unchanged (tells shift vs under-fit).
STEP 1c (if `teacher_geff/` / `train_dense_geff/` are not in the dataset yet): make the teacher + `train_dense/` yourself
  (Friend B STEP 1-2). Coordinate in the chat so it is done once.
STEP 2 (~1 h GPU per run): DENSE FINE-TUNE of the PRIMARY (pilkwang support-pack `weights/unet_transformer/split_0`) on 6bba only:
  `--init-weights <pth>`, `BIOHUB_DATA_DIR=train_dense`, `--max-iters 1200 --lr 5e-5 --det-loss bce --max-detections 0 --seed 42`,
  LOEO split, raw score on the 12 44b6 videos. Reference: the SPARSE fine-tune of the same weights on the same split = 0.8825
  (exp11 B, RESULTS.md); re-run it yourself once so both numbers come from your machine. Variants, one at a time, each ~1 h:
  (a) dense 1200 it; (b) dense 2400 it; (c) dense 1200 it + `--det-neg-weight 0.1` (dense labels make a stronger negative
  weight safe). Keep a variant only if it beats the sparse fine-tune by >= 0.005 on 44b6. Folder
  `experiments/local_friend_a_exp03_dense_ft_primary/`, RESULTS rows.
STEP 3 (only for a winning variant): the same fine-tune on all 183 non-holdout videos (exp03B's split, `experiments/exp03_finetune_ab/config.py`
  holds the list) -> dataset `friend_a_ft_dense_primary/` -> Vitalii probes it as PRIMARY on the TTA base (one LB slot).
  Weights uploaded with config.json; RESULTS row with the 44b6 and hold12 numbers.
STEP 4 (if time remains before 24 Sep): second seed of the winning fine-tune (seed 7) for a 3-model blend; scratch dense run
  (old plan) only as research.
STOP doing: scratch 30-epoch runs on all 199, resumes of them, probes of scratch checkpoints on the LB.


## Rules
- One experiment = one folder `experiments/local_<name>_expNN_<slug>/` with the command line / config and a results JSON; one row in `experiments/RESULTS.md` (state the video set: hold12 / divset36 / 48 / LOEO-44b6 / LB).
- Commit as yourself; no secrets, no data, no prediction graphs in git (zip them elsewhere if needed). Weights go to the Kaggle dataset (subfolder per experiment with `edge_predictor_best.pth` + `config.json`).
- Validation truth: anything initialised from pilkwang weights is leaky on train videos (they trained on all 199). Until the from-scratch 6bba model exists, only the LB is trustworthy for linking/division aggressiveness; model comparisons need >= 48 videos (seed noise ±0.005).
- Do not submit to the LB yourself; send the candidate (kernel or weights) to Vitalii — LB slots are budgeted (5/day for the whole team).
- Kaggle rules (checked 2026-09-06): the 5 submissions/day limit is per Team; submitting from several accounts or sharing
  code outside an official Kaggle Team is a disqualification offence. We are already one Kaggle Team (leader Vitalii,
  members Sasyami + gsfatakhov), so sharing code/weights inside the team is fine. The 5/day limit is shared by the team:
  a submission from your account counts against it, so still leave submissions to Vitalii.
  Running probe-prep kernels under your own account is fine and welcome (each member has their own 30 GPU-h/week).
- Update `CONTEXT.md` §6 (results) and §10/§11 (plan) when you finish something; keep entries short and dated.
