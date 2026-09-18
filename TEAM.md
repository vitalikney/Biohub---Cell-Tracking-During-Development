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

**DATA LAYOUT (2026-09-15).** All team weights are in git: `weights_dataset/<name>/edge_predictor_best.pth` + `config.json`
(exp03B, exp08, exp23, soup03B_50, friend_a_*). `git pull` gets them; the Kaggle dataset `vitaliineibauer/biohub-ft-weights`
is the same content for the notebooks. When you add a checkpoint: put it in `weights_dataset/<your_name>/`, commit, push, and
publish the dataset from that folder (`python -m kaggle datasets version -p weights_dataset --dir-mode zip -m "..."`) so both
copies stay identical. The competition data (82 GB of zarr) is NOT in git and will not be: download it once from Kaggle.
Paths, slugs, the base recipe's knobs and the LB rules live in `params.yaml`. The THIRD-PARTY packs the kernels depend on
(pilkwang support pack, seed314159 secondary, DeepCenter; hundreds of MB) are also not in git: run
`python tools/get_kaggle_datasets.py` once and they land in `external/` (git-ignored, fetched only if missing).

**METRIC ALERT (2026-09-11, applies to BOTH friends, read before any local scoring).**
`tools/repo/` is pilkwang's fork and its division metric is the PRE-PATCH one: it credits a ground-truth division to any
predicted fork merely reachable in the same weakly connected component. The organisers removed that rule on 2026-07-17
(metrics.md: "Merely sharing a weakly connected component is not sufficient"). The official package is now vendored at
`tools/official/` and `tools/score_geffs.py` uses it - just `git pull` and re-run. Edge numbers are unaffected (io and
image code are byte-identical); only division TPs change, and score = adj_edge + 0.1*div_J. Concretely, on one of my own
sweeps the fork reported 4 division TPs where the official metric reports 3, which flipped which setting looked best.
If you have ANY local row that reported division TPs, re-score it before drawing a conclusion from it.

**Friend B — order of work (revised 2026-09-10 21:30; supersedes the 18:00 version). Self-contained.**

UPDATE 2026-09-18 (B20 shortcut): a PUBLIC trained division detector exists - `giorgosi/biohub-divnet-v2` (per-node 3D UNet-GAP on lags -1..+2 + centre marker, 4 folds over all 199 videos, OOF AUC 0.887, simulated official div_J 0.21-0.23 vs our 0.11). Loader/scorer in `tools/divnet_infer.py`, dataset in the fetcher manifest (`--only divnet`). Use its p as the ranker score for your B20 candidates (needs the 4 frames around each candidate, so score in pass 1 or a streaming pass); gate unchanged: official div_J on 199 by 22 Sep.

UPDATE 2026-09-15 night (plan after your closures): from tomorrow your main line is B20 (division ranker via your in-kernel
feature table): the only metric term with room, multi-day, must show div_J on all 199 videos with the official metric by
22 Sep. Order: feature table (incl. the size profile) -> ranker -> LOEO div_J. The axis-flip branch (DeepCenter TTA group,
primary-only / secondary-only ablations) only if probe 19 scores >= 0.950; if <= 0.944 the inference class does not
transfer and the port stays a post-processing instrument.

UPDATE 2026-09-15 evening (your calibration, B25 closure, probe-18 prediction and per-stage table are merged - thank you).
Order now: (1) the per-stage follow-ups you queued, in this order: linefit weight x window grid (B28, the largest stage,
never swept), then relink OFF and veto OFF with the full stack (B29); report ALL-12 deltas and per-video swings; (2) B26 and
the axis-flip test on 12 videos with pilkwang and scratch primaries; (3) B20 with the size profile only after (1)-(2).
Gate for asking Vitalii for a probe on (1): >= +0.005 on ALL 12 and probe 18's LB confirms that your local post-processing
delta transferred (its score lands tonight). Your withdrawn "read on CLEAN" rule is withdrawn team-wide too.

UPDATE 2026-09-15 (read first; your 17 commits are merged into main, thank you - the port, the leak split and the
memorised-views finding are all recorded in CONTEXT §14). Order of work now:
1. B26 - the falsification test you designed in §13.5 (PRIMARY := friend_a_exp02_loeo20 from `weights_dataset/`, public
   TTA vs Z-flip, 12 videos, compare the delta with the pilkwang pair). ~25 min GPU. Report the two deltas and your verdict.
2. The axis-flip variant: measure it, but read it with your asymmetric rule (a local loss closes it; a local gain is
   not evidence). Do not ask for an LB probe on a local gain alone.
3. B25 on your port - the node-budget lever (CONTEXT §10a B25): a learned second-stage score that removes ~10-13% of
   detected peaks while keeping recall on annotated nodes; by your own §14.1 table this is a within-model comparison,
   so it is measurable locally. Cheapest first version: features from the cached raw graphs (peak prob if you can cache
   it, distance to the nearest stronger peak, primary/secondary agreement), a logistic model, LOEO over videos, and the
   official metric's node ratio + edge TP as the readout.
4. STEP 3 (secondary fine-tune) only if disk frees up; it is a final-2 candidate at most (probe 13 was -0.007 on the LB).
Always round node coordinates as the submission writer does before scoring (your §16.1, +0.0006).

UPDATE 2026-09-12 (read first): the alternative division stack was measured on 12 videos with the official metric:
gates open + sister floor 0.9523-0.9543 and a sister-first ranker 0.9475, against 0.9567 for the public setting. Reachable
is not recovered - without a learned ranker the false forks explode and the ~5-per-frame budget is spent on them. So the
division GATE stays public; STEP 4b (199-video sweep) is now low-priority CPU filler only. The task with real value left
on the division side is a learned fork RANKER (score each candidate fork on evidence: sister separation, parent intensity
at the split frame, per-branch motion, detector confidence; 151 positives on all 199 videos, LOEO; go/no-go = div_J on the
official metric before any LB probe). Take it only after your local port and calibration (STEP 4) work. Closed on the LB
meanwhile: fine-tuned primaries (0.944/0.943 vs 0.947) and Z-flip TTA (0.938).


What changed since 18:00: Vitalii already probed the first TTA-stack variants on the LB (probes 11-14: exp30 = 0.947 stack +
exp03B primary; exp31 = + Z-flip TTA; exp32 = + secondary := exp23; exp29 = public 0.947 verbatim), so those are no longer
"first customers" for the local port - they are its CALIBRATION SET. Friend A's dense pipeline (`friend-a-dense-pipeline.ipynb`,
`tools/build_dense_gt.py`) produces the teacher for the 126 6bba + 12 44b6 videos; check the dataset before doing it again.

STEP 1 (only if the dataset `vitaliineibauer/biohub-ft-weights` still has NO `teacher_geff/` and `train_dense_geff/` when you start):
  teacher detections (exp03B + seed314159 ensemble, det 0.965, no ILP, `BIOHUB_ENSEMBLE_WEIGHTS`) for the 138 videos of
  `experiments/_lib/loeo_train6bba_val44b6.json` (126 train + 12 holdout). If Friend A's folders exist: skip, download them.
  The remaining 61 44b6 videos are needed only for the final all-183 fine-tune - do them last (STEP 5).
STEP 2 (CPU): `train_dense/` with `tools/build_dense_gt.py` (teacher UNION GT, dedupe 5 um GT wins, GT edges only, zarr junctions,
  `dense_stats.csv`). Skip if `train_dense_geff/` exists.
STEP 3 (~1 h GPU per run; 12 GB: batch 4 + grad checkpointing): fine-tune the SECONDARY (pilkwang seed314159) on 6bba ONLY, twice:
  (a) sparse (real train dir) and (b) dense (`BIOHUB_DATA_DIR=train_dense`, `--max-detections 0`); both `--init-weights <seed314159 pth>
  --max-iters 1200 --lr 5e-5 --det-loss bce --seed 42`, split `loeo_train6bba_val44b6.json`. Score both raw on the 12 44b6 videos
  (det 0.965 + ILP, `tools/score_geffs.py`): score, edge_jaccard, node_recall, N_pred/N_est. Note: exp23 in the dataset is the
  sparse fine-tune of the same weights on 183 videos INCLUDING 44b6 - it is NOT a valid reference here, do (a) yourself.
  Keep dense only if (b) >= (a) + 0.005. Folder `experiments/local_friend_b_exp01_dense_ft_secondary/`, RESULTS rows.
STEP 4 (CPU + short GPU, in parallel with 3): local port of the public pipeline post-processing ('Friend B start kit' above) with
  cached GPU stages. FIRST use = calibration: reproduce the four LB-probed configs of 2026-09-10 (exp29/exp30/exp31/exp32, folders
  in `experiments/`) on the 12 44b6 videos and report whether the local ranking matches the LB ranking, which is now known
  (scored 2026-09-11): exp29 0.947 > exp30 0.944 > exp31 0.941 > exp32 0.937. A port that reproduces this order (and the
  ~0.010 spread) is calibrated; if it ranks exp30-32 above exp29, tell Vitalii before running any variant.
  THEN the ONE inference variant still unanswered: replace the rot90/transpose views by the training-consistent
  8-axis-flip group. The others are already settled and must NOT be re-run - sjlee101 published his own forks of them and
  every one is a tie with 0.947 (secondary edge-TTA weight 1.0 = 0.947, DC safe-div 0.25 = 0.947, sister radius 16 =
  0.947, DC safe-div 0.15 = 0.946), and Vitalii's exp34 covers the Z-flip idea. Report the axis-flip delta vs exp29 (the
  current base; exp30's fine-tuned primary did not help on the LB) on the 12 videos; Vitalii probes it if it wins.
STEP 4b (CPU, cheap, do it whenever a GPU run is busy): division-gate sweep on ALL 199 videos with `tools/sim_safediv.py`
  (new, 2026-09-11). On 12 videos it is useless - 14 GT divisions quantise the metric, one recovered division = +-0.004 score,
  and the observed threshold spread (symmetry tau, parent radius, divergence) is 2 events wide. On all 199 videos there are
  151 GT divisions, which is the first set that can actually resolve these knobs. Input = the teacher/prediction geffs you
  produce in STEP 1-2. Report: score / div_J / TP-FP-FN per setting, and whether any setting beats the public one by more than
  1.5 recovered divisions. Vitalii probes at most ONE winner on the LB. Known ceiling: the gate adds ~4 FP per TP, so if div_J
  stays near 0.11-0.14 for every setting, say so and stop - the answer is then a division classifier, not a threshold.
STEP 5 (later): teacher for the remaining 61 44b6 videos (for all-183 dense fine-tunes); optional dense scratch run only if 1-4 are done.

**Friend A — order of work (revised 2026-09-10 18:00 after the audit in CONTEXT §14). Self-contained.**

**UPDATE 2026-09-18: friend A's task CHANGED (friend B is out; friend A is back).** The dense/sparse fine-tune line
below is CANCELLED (probes 15/17: fine-tuned primaries 0.944/0.943 vs 0.947; weight swaps unresolvable locally per
friend B's calibration). Friend A takes over B20 with the public DivNet model: pass 1 of friend B's port over all 199
videos on his own GPU (data is local, no Kaggle bundling), DivNet p for every (parent, candidate) fork via
`tools/divnet_infer.py` computed while frames are on disk, pass 2 with DivNet ranking (top-k 1/2, min-score 0.3/0.5/0.7,
shipped caps and veto), official div_J and score on all 199, gate: score >= control + 0.005 with division TP up and
adj_edge down by <= 0.001 -> one LB probe by Vitalii. Deadline 22 Sep. Details in PROMPT_FRIEND_A.md top block.


UPDATE 2026-09-12 (read first): LB probes 15 and 17 are in - a fine-tuned primary on the public 0.947 TTA stack scores
0.944 (exp03B) and 0.943 (weight soup) against 0.947 for the untouched public weights. So NO fine-tuned primary goes into
final submission 1 any more, and there will be no further LB probes of them. Your STEP 2/3 work is still wanted, but its
target changed: it is the candidate for FINAL SUBMISSION 2, chosen on the HONEST validator (leave-one-embryo-out, official
metric via `tools/score_geffs.py` after `git pull`). Report honest-validator numbers only; the LB is not the judge here.
Also closed: Z-flip TTA (probe 16 = 0.938), do not spend time on it.

UPDATE 2026-09-13, dense fine-tune order changed by new evidence (Lê Quang Cảnh, rank 39, official scorer, five held-out
films): fine-tuning the DETECTOR on dense labels costs -0.003 if only the detection head moves and **-0.038 if the encoder
moves while the linker is frozen**, because the linker reads the encoder. Therefore: variant (e) two-stage (freeze linker,
move encoder on train_dense, recalibrate) is DROPPED - it is exactly the harmful case. Run the dense variants (a)/(b) ONLY
as the joint fine-tune (edge loss on) with the teacher's EDGES included in train_dense, so the linker co-adapts; if
train_dense has nodes only, do not run them - do the sparse reference (0) and the softer-augmentation variant (d) instead.
A head-only run (freeze everything but detect_head) is allowed as a 20-minute sanity check and is expected to be ~0.



Same reasoning as for Friend B above: dense labels now feed FINE-TUNING of pilkwang (proven to transfer), scratch training is
demoted to research. Your 5070 Ti takes the primary side; Friend B takes the secondary side.
LB update 2026-09-11: on the new base (sjlee101 TTA stack, 0.947 reproduced) the exp03B primary gave 0.944, i.e. the +0.004 of
the fine-tune on the old base did not carry over (deconfound probe exp33 pending). The bar for a fine-tuned primary is
therefore higher than "beats exp03B on the honest split": it must beat exp03B clearly (>= +0.01 on the honest 12 44b6
videos) to earn an LB probe; otherwise it goes to final candidate 2 (honest-validator pick) only.

STEP 1b (20 min GPU): score the epoch-20 scratch model on 12 of its own TRAIN 6bba videos - unchanged (tells shift vs under-fit).
STEP 1c (if `teacher_geff/` / `train_dense_geff/` are not in the dataset yet): make the teacher + `train_dense/` yourself
  (Friend B STEP 1-2). Coordinate in the chat so it is done once.
STEP 1b RESULT (2026-09-10): own-train 6bba 0.833 vs unseen 44b6 0.680 -> embryo shift dominates. Your dense pipeline
  (`friend-a-dense-pipeline.ipynb`, `tools/build_dense_gt.py`) is merged and is the tool for STEP 1c; its STEP 4 must be
  redirected from scratch to the fine-tune below (add `--init-weights <pilkwang primary pth>`, replace epochs by
  `--max-iters 1200`, lr 5e-5 constant; drop the >= 0.70 scratch branch and the all-199 scratch retrain).
STEP 2 (~1 h GPU per run): DENSE FINE-TUNE of the PRIMARY (pilkwang support-pack `weights/unet_transformer/split_0`) on 6bba only:
  `--init-weights <pth>`, `BIOHUB_DATA_DIR=train_dense`, `--max-iters 1200 --lr 5e-5 --det-loss bce --max-detections 0 --seed 42`,
  LOEO split, raw score on the 12 44b6 videos. Reference: the SPARSE fine-tune of the same weights on the same split = 0.8825
  (exp11 B, RESULTS.md); re-run it yourself once so both numbers come from your machine. Variants, one at a time, each ~1 h:
  (a) dense 1200 it; (b) dense 2400 it; (c) dense 1200 it + `--det-neg-weight 0.1` (dense labels make a stronger negative
  weight safe); (d) dense 1200 it + `--aug-intensity` with HALVED ranges (edit train_patches: gain 0.8-1.25, offset +-0.1,
  gamma 0.8-1.25, no haze; the old ranges were too aggressive); (e) two-stage: stage A `--init-weights <pilkwang primary>
  --freeze linker --edge-loss-weight 0 --max-iters 1200` on train_dense, then stage B `--init-weights <stage A best>
  --freeze detector --max-iters 600 --lr 5e-5` on the sparse train dir (flags exist in `experiments/_lib/train_patches.py`).
  Note (code check 2026-09-10): dense labels do NOT change the linker supervision (teacher nodes have no edges and were already
  0-target detections in sparse training), so (e) is an experiment, not a bug fix.
  Keep a variant only if it beats the sparse fine-tune by >= 0.005 on 44b6. Folder
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
