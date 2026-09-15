# local_friend_b_exp02_public_port — STEP 4: local port of the public 0.947 pipeline + calibration

Friend B (gsfatakhov), RTX 5070 12 GB, Linux, started 2026-09-15.
Reasoning log and findings: `../../CONTEXT_FRIEND_B.md`.

## What this is

`tools/public_local.py` runs the public 0.947 stack (sjlee101 `biohub-lf-dctta-v020`, our `exp29`) on local
train videos with local ground truth, splitting it into a cached GPU stage and a cheap CPU stage, and scores
every configuration with the OFFICIAL metric (`tools/score_geffs.py`).

The pipeline is not re-implemented. The notebook's own cells are executed verbatim - the knob cell, the
constants cell, the runtime patches to `predict_unet_transformer.py`, and the post-processing cell - with only
the I/O boundary replaced. Measured before building it: the post-processing cell is byte-identical across
exp29/30/31/32 and the patch cell differs only for exp31, so the whole calibration is four GPU runs plus
arbitrarily many CPU-only post-processing runs.

## Reproduce

```bash
# 1. data (12 LOEO 44b6 videos, ~6.2 GB; keep --workers low, Kaggle rate-limits hard)
python tools/kaggle_fetch_videos.py --split experiments/_lib/loeo_train6bba_val44b6.json --key holdout

# 2. weights
for d in pilkwang/biohub-tracking-support-pack-50ep-v1 \
         pilkwang/biohub-temporal-unet3d-seed314159-v1 \
         pilkwang/biohub-deepcenter-unet3d-center-prior-v1 \
         vitaliineibauer/biohub-ft-weights; do
  kaggle datasets download -d "$d" --unzip -p ~/biohub_weights/$(basename "$d")
done

# 3. smoke test on one video, then the calibration
python tools/public_local.py --tag smoke --stems 44b6_12dfb391
bash experiments/local_friend_b_exp02_public_port/run_calibration.sh

# 4. read the verdict (three video sets, see "Leakage" below)
python experiments/local_friend_b_exp02_public_port/summarise.py
```

A CPU-only knob sweep reuses the cached raw graphs and touches no GPU:

```bash
python tools/public_local.py --tag exp29 --stage pp --label gap45 --env BIOHUB_GAP_CLOSE_UM=4.5
```

## Configurations

| tag | notebook (patches) | PRIMARY | SECONDARY | LB (probes 11-14, scored 2026-09-11) |
|---|---|---|---|---|
| exp29 | exp29 | pilkwang | pilkwang seed314159 | 0.947 |
| exp30 | exp29 | exp03B | pilkwang seed314159 | 0.944 |
| exp31 | exp31 (Z-flip, 12 views) | exp03B | pilkwang seed314159 | 0.941 |
| exp32 | exp29 | exp03B | exp23 | 0.937 |

## Leakage split — diagnostic only (corrected after the 12-video run)

`exp03B` (primary of exp30/31/32) and `exp23` (secondary of exp32) were fine-tuned on the 183 videos of
`experiments/_lib/holdout_split.json`, which contains six of the twelve LOEO 44b6 videos:
`12dfb391, 2a2eff9f, a21120c2, c50204e0, d2f34f90, d5e7d891`. The morning hypothesis - that this inflates the
exp03B configurations on those six - was **refuted by the 12-video run**: exp03B configurations beat exp29 on
4 of 6 CLEAN videos and 1 of 6 LEAKY ones, the opposite sign. Local rankings are driven by the per-video swing of
a weight swap (−0.037…+0.039) against a 0.003 LB effect.

**The verdict is read on ALL 12 videos** with the leave-one-video-out check (`results/calibration_12videos_pervideo.txt`).
`summarise.py` still prints the CLEAN/LEAKY blocks as a diagnostic. Result: order reproduced up to the exp30/exp31
pair (LB gap 0.003 = noise), exp29 first and exp32 last, spread 2.4× the LB's. See `CONTEXT_FRIEND_B.md` §28.

The pilkwang base weights saw all 199 videos; that leak is identical across configurations and is a separate,
confirmed mechanism for TTA variants (scratch-model tests, §13/§20/§22).

## Files

- `run_calibration.sh` — the four configurations, plus a tight-5.5 post-processing re-run for exp29 (the only
  one submitted with the in-kernel sweep's pick).
- `summarise.py` — per-set tables, Spearman rank correlation against the leaderboard, ranking inversions.
- `rescore.py` — backfills per-video metric rows into results produced before they were stored; reads the
  post-processed graphs already on disk, so it costs seconds.
- `collect_results.py` — copies every run's summary + per-video metric rows out of the git-ignored cache into
  `results/<tag>__<label>.json` and builds `results/all_runs.md`. Run it after every batch of runs; the graphs
  stay out of git, the numbers go in.
- `run_stage_table.sh` — cumulative post-processing ablation (raw / +relink / +gap / +divisions / +veto /
  +short-track / +linefit), CPU-only off the cached raw graphs.
- `run_tta_bias_test.sh` — B26: the Z-flip TTA delta on a scratch-trained primary vs on pilkwang.
- `stream_bundles.py` — B20 pass 1: streams all 199 videos through the port in 8-video bundles fetched by the
  private kernel (`kernel_fetch_missing/`), keeps raw graphs with `peak_prob`, deletes the videos after.
- `pass1_extras.py` — per video while frames are on disk: post-gap checkpoint graph (the shipped division stage's
  exact input) and the 8-view DeepCenter score of every raw node, so pass 2 needs no frames.
- `pass2_rank_divisions.py` — the division stage re-run from checkpoints with the shipped or a learned ranker,
  shipped caps/veto, notebook tail, official score. Control reproduces the shipped stage exactly (0.9001, 1/6/14).
- `b20_ranker.py`, `b20_size_profile.py`, `b25_*.py` — prototypes and feature studies (see CONTEXT_FRIEND_B.md).
- `results/` — one JSON per run plus `all_runs.md`; the numbers behind every RESULTS.md row of this folder.
