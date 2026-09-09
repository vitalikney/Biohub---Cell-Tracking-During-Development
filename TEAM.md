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

**Friend B — order of work (updated 2026-09-08 07:30). Self-contained: an assistant given TEAM.md + CONTEXT.md §10a/§14 can execute it.**

Background: the team's main bet is DENSE pseudo-labels (CONTEXT §10a B3): detectors trained on the sparse GT (6% of nuclei
labelled) collapse after 5-10 epochs because unlabelled nuclei act as negatives; the public pipeline's own detections
(node recall 0.98 on GT) are a good dense teacher. Your GPU (5070, 12 GB) produces the teacher and runs the dense-label
run on 6bba while Friend A runs the sparse one, so the sparse-vs-dense comparison exists a day earlier.

STEP 1 (now, ~4 h GPU): teacher detections for all 199 train videos.
  - Code: `tools/repo/` (support-pack scripts + src) with `experiments/_lib/predict_patches.py` applied
    (`apply_predict_patches(Path("scripts/predict_unet_transformer.py"))`) so that `BIOHUB_ENSEMBLE_WEIGHTS` averages models.
  - Weights: primary = `vitaliineibauer/biohub-ft-weights/exp03B`, extra = pilkwang seed314159
    (`pilkwang/biohub-temporal-unet3d-seed314159-v1`, `weights/unet_transformer/split_0/edge_predictor_best.pth` + config.json).
  - Command (from the repo copy, `PYTHONPATH=src`, `BIOHUB_DATA_DIR=<train>`, splits JSON = `[{"split":0,"train":[],"test":[all 199 stems]}]`):
    `BIOHUB_ENSEMBLE_WEIGHTS=<seed314159 pth> python scripts/predict_unet_transformer.py --data-dir <train> --splits <json> --split 0
     --weights <exp03B pth> --det-threshold 0.965 --method teacher` (NO `--use-ilp`; we only need nodes). ~1 min/video on a 5070.
  - Output: `predictions/teacher/split_0/<stem>.geff` (nodes t,z,y,x). Zip -> Kaggle dataset `vitaliineibauer/biohub-ft-weights/teacher_geff/`.

STEP 2 (CPU, same day): build the dense training set `train_dense/` next to the real train folder.
  - For each video: nodes = teacher nodes UNION GT nodes, deduplicated within 5 um (GT node wins, teacher node dropped);
    edges = GT edges only (re-mapped to the kept GT node ids); copy the GT geff metadata (incl. `estimated_number_of_nodes`).
    Write `<stem>.geff` with `tools/repo/src/biohub_tracking/io.py` helpers (tracksdata graph -> `to_geff`).
  - `<stem>.zarr` = directory junction to the real zarr (`mklink /J` on Windows), no copy.
  - Checks per video (write `train_dense/dense_stats.csv`): GT node recall inside the dense set = 1.0 by construction;
    teacher recall of GT within 5 um (expect ~0.98); N_dense / estimated_number_of_nodes (expect 0.9-1.1; flag outliers).
  - Commit the builder script as `tools/build_dense_gt.py` + the stats CSV; the geff files go to the dataset as `train_dense_geff/`.

STEP 3 (~15 h GPU): dense-label validator run on your card.
  - Same recipe as Friend A's STEP 1 (6bba-only split `experiments/_lib/loeo_train6bba_val44b6.json`, BCE, window 2, ds 1,4,4,
    lr 1e-4 cosine -> 1e-5, seed 42, 20 epochs, `--checkpoint-every 5`) but `BIOHUB_DATA_DIR=train_dense` and `--max-detections 0`.
    12 GB: `--batch-size 2` or 3 without grad checkpointing, or batch 4 with it (drop `--no-grad-ckpt`). `--num-workers 0` on Windows.
  - Score every checkpoint on the 12 44b6 videos exactly like Friend A's STEP 1 (raw predict at det 0.965 + ILP, `tools/score_geffs.py`),
    log score / edge_jaccard / node_recall / N_pred/N_est. Folder `experiments/local_friend_b_exp01_loeo_dense_20ep/`, RESULTS row,
    best checkpoint to the dataset as `friend_b_exp01_loeo_dense/`.
  - Decision: dense beats sparse (Friend A STEP 1) by >= 0.02 on 44b6 -> dense becomes the team recipe; Friend A retrains it on
    all 199 (his STEP 5). If not, report the detection numbers (node_recall, N_pred/N_est) - they say whether the teacher was too
    conservative (raise recall: det threshold 0.95 for the teacher) or too noisy.

STEP 4 (CPU, in parallel with STEP 3): local port of the public 0.941 pipeline's post-processing (the 'Friend B start kit'
  above, steps 1-5): cached GPU stages + CPU knob sweeps, stage table on the 12 44b6 videos. Needed to test any new secondary
  locally before an LB slot (probe 7 = -0.016 and probe 10 = -0.025 were both blind). First customer: exp23 as secondary.

STEP 5 (later): knob sweeps on the cached predictions (§10a B9/B10); FOCUS-3D (B11) only if the dense-label bet fails.

**Friend A — order of work (updated 2026-09-08 07:00). Self-contained: an assistant given TEAM.md + CONTEXT.md §10a/§14 can execute it.**

Background: LB probe 10 (your all-199 epoch-21 checkpoint as SECONDARY in the public pipeline) scored 0.920 vs 0.945.
The 21-epoch scratch model is weaker than pilkwang's 50-epoch model, and a weaker model in the blend adds errors, not
diversity. So no model goes to the LB again until it wins on an honest local comparison. Your job now is to build that
comparison and then improve the model on it. The all-199 resume (21 -> 30) is NOT needed; if it is running, let it finish
but do not upload/probe it.

STEP 1 (now, ~15 h GPU): the honest validator = a from-scratch model that never saw embryo 44b6.
  - Recipe: exactly your `local_friend_a_exp01_loeo_scratch` run (126 6bba videos from `experiments/_lib/loeo_train6bba_val44b6.json`,
    BCE, window 2, ds 1,4,4, batch 4, lr 1e-4, seed 42, `--max-detections 1024`) but 20 epochs, `--lr-schedule cosine --min-lr 1e-5`,
    `--checkpoint-every 5`. Output folder: `experiments/local_friend_a_exp02_loeo_scratch_20ep/`.
  - For EACH checkpoint (5/10/15/20 + best): predict the 12 `holdout` videos of that JSON with
    `scripts/predict_unet_transformer.py --det-threshold 0.965 --use-ilp --ilp-appearance-weight 0 --ilp-disappearance-weight 2 --ilp-division-weight 1.2`
    (raw graphs, no post-processing), then `python tools/score_geffs.py <dir> --out <json>`. Record per checkpoint: score,
    edge_jaccard, node_recall, N_pred/N_est (sum of predicted nodes / sum of estimated_number_of_nodes over the 12 videos).
  - Reference on the SAME 12 videos, same predict command: (a) pilkwang PRIMARY `weights/unet_transformer/split_0` from the
    support pack, (b) pilkwang SECONDARY from `pilkwang/biohub-temporal-unet3d-seed314159-v1` (`weights/unet_transformer/split_0`).
    Both are leaky (they trained on 44b6) but they are the bar a candidate secondary must clear on the LB, so log them.
    Known numbers: pilkwang primary raw on these 12 videos = 0.8798 (exp11 A); your 5-epoch model = 0.6706.
  - Deliverables: `results.json` with the table, RESULTS.md row, CONTEXT.md one-line note, best checkpoint to the Kaggle dataset
    as `friend_a_exp02_loeo20/` (edge_predictor_best.pth + config.json). Stop rule: if score(20) - score(15) < 0.005, 20 epochs is enough.

STEP 1 RESULT (2026-09-09): best 0.6803 at epoch 20 (ep5 0.6635, ep10 0.5547, ep15 0.6772); node recall 0.85-0.88,
  N_pred/N_est ~1.0; references pilkwang primary 0.8807 / secondary 0.8691. Sparse-GT limit -> STEP 4 next. Before that:
STEP 1b (~20 min GPU): score the epoch-20 model with the official metric on 12 of its own TRAIN 6bba videos (same predict
  command). Report score + node_recall. ~0.9 = embryo shift / fit to 6bba; ~0.7 = sparse-label under-fit. Add to results.json.
STEP 1c (right after 1b, do NOT wait for anyone): if the dataset has no `teacher_geff/` / `train_dense_geff/` yet, produce
  the teacher yourself - follow "Friend B STEP 1 + STEP 2" below for the 126 6bba training videos + the 12 44b6 holdout
  videos only (138 videos, ~2.5 h on the 5070 Ti; the 44b6 teacher points are needed only for the dense_stats check, never
  for training). Upload `teacher_geff/` and `train_dense_geff/` to the dataset and note it in CONTEXT §14 so Friend B skips it.
STEP 2 (after step 1, and it decides the branch):
  - If the best 6bba-only checkpoint reaches >= 0.85 on 44b6: the validator is usable. Go to step 3.
  - If it stays < 0.80: sparse GT is the limit (unlabelled nuclei become negatives after ~10 epochs). Skip to step 4 (dense labels)
    and do not spend more epochs on sparse GT.

STEP 3 (only with a usable validator): one recipe change at a time, each = a new 6bba-only run scored on 44b6; keep a change only
  if it beats the current best by >= 0.005 (12 videos, seed noise ~0.005). Order: (a) ignore-unlabelled / nnPU detection loss
  (CONTEXT §10a B7), (b) parent-offset head (B8), (c) 40 epochs if the curve is still rising, (d) MAE pretraining (B13).
  Judge DETECTION numbers first (node_recall, N_pred/N_est, edge FN caused by missed nodes); linker-only gains do not transfer to the LB.

STEP 4 (as soon as `train_dense/` exists - from Friend B or from your own STEP 1c): the same
  scratch recipe on DENSE labels (teacher points + GT points, GT wins within 5 um), `--max-detections 0`, 30 epochs, checkpoints
  every 5, scored on 44b6 exactly as in step 1. This is the main bet: dense labels let the detector train 30+ epochs without
  the sparse-GT collapse. Compare against step 1's best.

STEP 4 decision: dense >= sparse + 0.02 on 44b6 (i.e. >= 0.70) -> dense is the team recipe, go to STEP 5 with it;
  dense < sparse + 0.02 -> report node_recall and N_pred/N_est of both; then one cheap sparse-side test while we think:
  `--det-neg-weight 0.001` (10x weaker penalty on unlabelled voxels) on 6bba-only, 10 epochs, scored on 44b6.
STEP 5 (only for a recipe that won on 44b6): retrain it on all 199 videos with the same settings, upload as `friend_a_full199_<recipe>/`,
  and tell Vitalii; he runs ONE LB probe with it as secondary (blend weight will be probed at 0.5 first, not 0.8).

STEP 6 (from ~2026-09-20): freeze recipes; only a second seed of the winning recipe for the final blend.

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
