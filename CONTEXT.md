# CONTEXT — Biohub Cell Tracking (Kaggle) research project

Living document. Everything needed to continue the work without the chat history. Updated 2026-09-06 02:50.

## 1. Goal and constraints
- Competition: https://www.kaggle.com/competitions/biohub-cell-tracking-during-development — detect nuclei, link them
  across frames, find divisions in 3D+t light-sheet zebrafish embryo videos. Code competition, internet off at scoring.
- Deadline 2026-09-29 (entry 22 Sep). User (Kaggle `vitaliineibauer`) started at rank 611/3140 with public 0.933.
  LB top 0.970, top-20 >= 0.947. Public LB ≈ 29% of test.
- Metric: score = adj_edge_J + 0.1*div_J (see §4). Official code: github.com/royerlab/kaggle-cell-tracking-competition.
- Compute: no local GPU. Kaggle 30 GPU-h/week (2x T4), max 2 concurrent GPU sessions. Experiments run as private
  notebooks via API; **no LB submissions without the user's explicit OK**.

## 2. Data
- `biohub-cell-tracking-during-development/train`: 199 videos (.zarr v3, T=100, Z=64, 256x256 uint16, voxel
  1.625 x 0.40625 x 0.40625 um) + sparse GT tracks (.geff). Two embryos: 44b6 (71 videos, dense, ~1% annotated,
  26 divisions) and 6bba (128 videos, ~9% annotated, 125 divisions). 151 division events in our count (87 videos).
- `test/`: 4 dummy copies of train videos. Real test = 2 other embryos, hidden.
- Known GT quirks: frozen/duplicated frames with GT still moving; boundary cells split into two tracks; a few wrong
  edges; very dim annotated nuclei.

## 3. Repository layout (this folder)
- `biohub-c33-public0933-v19-fallback.ipynb` — user's original public baseline (LB 0.933).
- `experiments/expNN_*/` — one folder per experiment: `kernel-metadata.json` + notebook built by
  `experiments/_lib/build_nb.py out.ipynb cell1.py ...`. Shared cells in `_lib/`: `setup_header.py`,
  `setup_deps_and_repo.py` (offline wheels + repo), `train_patches.py` (fine-tuning/AMP/loss patches to
  `train_unet_transformer.py`), `holdout_split.json` (12-video holdout).
- `experiments/RESULTS.md` — experiment log with numbers. `research/` — literature surveys + discussion digest.
- `tools/repo/` — local copy of the pilkwang support-pack code (metric, io, models, predict/train scripts).
- `tools/score_geffs.py` — official metric on local GT (CPU, ~50 s / 12 videos).
- `tools/postproc.py` — our post-processing (gap closing, direct end->start linking, post-hoc divisions, pruning) on prediction .geff.
- `tools/errdecomp.py` — error decomposition (detection / fragmentation / wrong association) per video.
- `tools/divranker.py` — division candidate enumeration + GBM ranker prototype (weak so far).
- `weights_dataset/` — source of Kaggle dataset `vitaliineibauer/biohub-ft-weights` (subfolder per experiment).
- Kaggle credentials: `kaggle.json` (copied to ~/.kaggle). Push: `python -m kaggle kernels push -p <dir>`;
  status: `kernels status`; outputs: `kernels output` (flaky; keep outputs small, zip predictions).

## 4. Metric facts that drive decisions
- Node match: 7 um bipartite, one-to-one. Edge TP needs both endpoints matched to GT nodes linked in GT. Edge FP only
  when an endpoint matches a GT node linked elsewhere => edges/forks among UNANNOTATED cells are free.
- adj_edge_J per video = J * (1 - 0.1*(N_pred - N_est)/N_est), weighted by GT edge count; fewer nodes than N_est is a
  BONUS (no ceiling). Dense 44b6 videos already get +3..7%.
- Division J = TP/(TP+FP+FN) on genuine parent->2 daughters forks near GT divisions (patched metric). A one-to-one
  linker scores 0 here. On LB a good pipeline has div_J ≈ 0.2 (worth ~0.02).

## 5. Pipeline we build on ("clean pipeline")
pilkwang support pack: TemporalUNet3D (XY downsample 4x, window 2) + node transformer (parental softmax + focal)
+ ILP (tracksdata) -> .geff. Our additions: fine-tuning patches (`--init-weights`, `--amp --no-grad-ckpt`,
`--det-loss gauss_focal`, `--seed`, workers=0), then `tools/postproc.py`.
Current best config: exp03B weights (1200 it fine-tune, lr 5e-5) -> predict det 0.965, ILP app 0 / disapp 2 / div 1.2
-> gap closing 5 um (1 frame, mutual NN, midpoint node) -> post-hoc divisions (parent<=5 um to orphan start at t+1,
sisters <=12 um, cap 1% nodes). **hold12 official score 0.9728** (raw 0.9575).
**Pipeline v2 (2026-09-06 02:05):** gap closing 5 um -> residual direct end(t)->start(t+1) linking 8 um (mutual NN)
-> post-hoc divisions (5/12 um). hold12 **0.9780** (adj 0.9646, div 6/31/8), divset36 **0.9117** (vs v1 0.9728 / 0.9056).
Radius 10 um slightly worse, 12 um worse. exp10 notebook updated to v2 (BIOHUB_PP_DIRECT_UM=8).

## 6. Results so far (hold12 = 12 held-out train videos, official metric unless noted)
| exp | what | score | note |
|---|---|---|---|
| exp00 | user's baseline re-run | val4 0.9360 | reproduced; 37 min |
| exp01/01b | training speed | - | 3.4 s/it -> 2.05 s/it with AMP+no ckpt; full epoch ~1.3 h |
| exp02 | public 0.941 pipeline | 0.9632 (notebook metric) | node bonus t_pred 232k vs 360k; 44b6_87bba6c4 collapses to 0.53 |
| exp03 A | pretrained raw model | 0.9527 | leaky (weights saw hold12) |
| exp03 B | +1200 it fine-tune | 0.9575 | real gain (+0.005 edge J) |
| exp04 | gauss-focal det loss | 0.9094 | calibration shift, under-detects at 0.965 |
| exp05 | window 3 | 0.9526 | worse than exp03B; 2x slower; not adopted |
| exp06 | public pipeline + ft weights | 0.9615 (notebook metric) | neutral: secondary seed (w 0.8) dilutes |
| exp07 | det threshold sweep | 0.9559/0.9575/0.9582 | flat |
| exp07+pp | + gap closing 5 um | 0.9619 | 2-frame gaps / short-track filter don't help |
| exp07+pp+div | + post-hoc divisions | 0.9728 | 6/14 GT divisions, 35 FP (mostly free) |
| exp08 | full-epoch fine-tune (2265 it) | 0.9539 | worse than 1200 it; over-training under-detects; per-video ±0.03 swings => single-run differences <0.01 are partly noise |
| exp10 | submission notebook self-check | raw 0.9575 / pp 0.9728 | matches local; ready for LB probe |
| exp12 | ILP division weight 0.3/0.6 on 48 videos (hold12+divset36, 106 GT div) | raw 0.9204 (div 36/205/70) / 0.9210 (24/104/82) | ILP now creates forks itself; baseline div 1.2 on the same 48 videos + v2 post-proc being scored locally |
| exp13 | ILP disappearance/appearance sweep (d1/a0, d3/a0, d2/a0.5) on 48 videos | pending | pushed 02:45 |
| exp11 | LOEO: fine-tune on 6bba only (126 videos, 1200 it), eval raw on 12x 44b6 | A pretrained 0.8798 (edge 0.8585) / B 6bba-only 0.8825 (edge 0.8570, recall 0.977->0.987) | fine-tuning on the other embryo does not hurt. **Post-proc transfers to the unseen embryo**: B raw 0.8825 -> gap5 0.8934 -> +direct8 0.9014 -> v2 (+div) 0.9059 (div 3/45/12); A: 0.8798 -> 0.8850 -> 0.8944 -> 0.8963 |
| pp velocity | EMA-velocity projection in gap closing | 0.9621 | neutral |
| pp steal | divisions may steal weakly linked daughters | 0.9710 | worse than 0.9728; off |
| pp direct link | end(t)->start(t+1) residual linking 4/6/8/10/12 um | hold12 0.9634/0.9645/0.9654/0.9652/0.9626; divset36 0.9041/0.9051/0.9056/0.9045/0.9034 | 8 um best on both sets |
| pp v2 | gap5 + direct8 + div 5/12 | hold12 **0.9780**, divset36 **0.9117** | new default (exp10 updated) |
| exp09 | exp03B predictions on 36 division-rich videos (92 GT divisions; 32 are 6bba) | raw 0.8997 (divset36) | harder set. Post-proc on it: gap5 +0.0005 (0.9002), 2-frame gaps hurt, divisions d5s12 0.9056 (17/156/75, divJ 0.069). Gains 5x smaller than on hold12 => model quality is the lever |

## 7. Caveats / validation strategy
- hold12 comes from the same two embryos as training => optimistic. Public LB is reportedly ~10% more optimistic
  than leave-one-embryo-out (LOEO) CV. Plan: LOEO check (train on 6bba, test on 44b6 and vice versa) for the final
  model choice; one LB probe when a clear candidate exists (needs user OK).
- Differences < 0.005 on hold12 are noise; divisions on 14 GT events are very noisy.
- Rule-based divisions have hurt LB for others while raising CV: validate division precision under LOEO.

## 8. Ideas backlog (from papers + discussions), ranked
1. Dense pseudo-labels for detection: FOCUS-3D instance segmentation / Zebrahub (allowed) -> train point detector
   with near-100% recall of annotated nodes and N_pred <= N_est; two-head domain shift trick (FOCUS zyx + delta).
2. Longer temporal window (3-6) for the link transformer with dense pseudo-tracks (Trackastra/HOCT); association
   consistency across views for ambiguous parents.
3. Division ranker (small MLP on parent/daughter geometry + features), trained on 151 real + synthetic divisions
   (José Freitas CC0 dataset), time-reversed clips as negatives.
4. Parent-offset / flow head (linajea, ELEPHANT) as motion prior for linking and gap closing.
5. Node-count control: learn to predict N_est-like density; drop low-confidence nodes not on tracks.
6. TTA/SWA/seed ensembles for the detector (merge detections, never union without dedup).

## 10. Next steps (checklist; re-check after every CONTEXT update, run independent items in parallel)
- [x] exp08 full epoch: worse (0.9539). Keep exp03B. Consider shorter (600 it) / lower-LR run and 2-3 seed ensemble later.
- [x] exp09 sweep: gap 5um / div parent 5 sister 12 remain best but small (+0.006 total on divset36); keep config, do not over-tune.
- [x] exp10 submission notebook built (`experiments/exp10_submit_clean`), self-check on hold12 enabled; CSV writer dry-run OK locally (251k nodes / 237k edges on hold12, no dangling refs).
- [x] exp10 ran on Kaggle: hold12 self-check raw 0.9575 / pp 0.9728 (exact), valid submission.csv, ~2.5 h projected for hidden test. Output saved in experiments/exp10_submit_clean/results/.
- [ ] LB probe with exp10 output (user decision 01:35: wait for exp11 + exp12 first); compare with public 0.941 pipeline.
- [x] LOEO check: exp11 done (A 0.8798 vs B 0.8825 on 44b6); post-proc v2 transfers (+0.023 on unseen embryo, every stage positive). Built (`experiments/exp11_loeo_6bba_to_44b6`, split `_lib/loeo_train6bba_val44b6.json`: 126 6bba train, 12 44b6 val, 15 divisions); push when a GPU slot frees; then local post-proc transfer test on its zipped predictions.
- [x] Division ranker prototype (tools/divranker.py) - weak; candidate recall is the bottleneck.
- [x] Error decomposition on divset36 (tools/errdecomp.py): recovered 93.3% of GT edges; lost to detection 3.6% (missed GT nodes 2.6%), fragmented 3.1%, wrong association ~0. Detection misses concentrate in 2 dim videos (6bba_57b7cc1e 237/1659 nodes missed, 6bba_786893ac 156/1465) = 43% of all detection losses. Fragmentation: 468 src-no-successor, 566 tgt-no-predecessor, 274 both linked elsewhere.
- [x] Residual direct end->start linking (`direct_um`, mutual NN, t->t+1): hold12 0.9619 -> 0.9634/0.9645/0.9654 (4/6/8 um), divset36 0.9002 -> 0.9041/0.9051/0.9056. Works on both sets. 10/12 um worse; with divisions: hold12 0.9780, divset36 0.9117 => pipeline v2 adopted.
- [ ] Inspect the two dim videos (intensity stats) -> detector robustness to dim nuclei.
- [ ] exp12 done on Kaggle (div weight 0.3: 36 TP/205 FP; 0.6: 24/104 on 48 videos); local comparison vs 1.2 with pipeline v2 running -> pick ILP division weight.
- [ ] exp13 running: ILP disappearance/appearance sweep on 48 videos -> score locally with v2.
- [ ] Dense pseudo-labels for the detector (FOCUS-3D or Zebrahub crops) - feasibility test first.
Rules: max 2 GPU kernels at once; keep outputs zipped; log every result in RESULTS.md and §6.

### 10a. Ideas from papers + discussions: implementation queue (priority order; cost = GPU-h per experiment)
| # | idea (source) | status | plan / cost |
|---|---|---|---|
| 1 | Post-hoc divisions + gap closing (public notebooks, Kaiser MHT delayed decisions) | done, +0.015 hold12 | robustness check on exp09 (92 div) and LOEO (exp11) |
| 2 | Division ranker on candidate forks (Zyss 2025, Nishimura 2023) | prototype `tools/divranker.py` (15 geometry/track features, grouped-CV GBM) | hold12 too small: 4 positives / 9898 candidates, only 4/14 GT divisions reachable as (parent, child, orphan start) => tried 'steal' of weakly linked daughters (edge_prob<0.6-0.8): no gain (0.971 vs 0.9728); of 14 GT divisions: 7 reachable as orphan-start, 5 second daughter linked elsewhere (prob 0.54-0.65), 1 parent without successors, 1 daughter undetected. On divset36 (92 GT div): only 32 reachable as orphan-start candidates (35% candidate recall) among 30.5k candidates; GBM ranker top-200 holds 8 TP vs geometric rule 12 TP in 5.2k forks. Bottleneck = candidate recall (ILP links the 2nd daughter elsewhere) => exp12: ILP division weight sweep (1.2 -> 0.6 / 0.3) on divset36+hold12 |
| 3 | Velocity-projected gap closing (EMA velocity, discussion 739570; Ultrack flow compensation) | tried: neutral (0.9619 -> 0.9621 on hold12) | implemented in tools/postproc.py (`gap_velocity`); re-check on exp09/LOEO only |
| 4 | Metric-aware ILP cost calibration (appearance/disappearance/division, edge power transform) (Hirsch 2022, Ultrack) | todo | GPU 0.5 h: predict once per setting on hold12; or cache candidate graphs |
| 5 | Detector: nnPU / ignore-unlabelled loss instead of neg_weight BCE (Zhou 2025, Zhao 2023, ELEPHANT); learnable neighbourhood-softmax peak loss (hengck23) | todo | patch train_patches.py; 45 min fine-tune each; early-stop on real metric (overfit after ~10 epochs) |
| 6 | Gaussian/anisotropic heatmap targets + NMS matched to 7 um (PAC-MAP, nnLandmark) | tried (exp04) | failed at fixed threshold; retry with threshold re-sweep on exp04 weights (0.5 h) |
| 7 | Detector TTA (8 flips, in-plane rotations) + seed/SWA ensemble with dedup merge (Moshkov 2020, discussion 733877) | todo | predict-time only; +0.5 h per variant; never union without merge |
| 8 | Dense pseudo-labels: FOCUS-3D centroids / open-source trackers (hengck23), Zebrahub crops+tracks (allowed) | todo, feasibility | Zebrahub bucket public.czbiohub.org/royerlab/zebrahub/imaging/single-objective/: full videos are TB-scale (ZSNS001: 791x448x2174x2423 uint16 ≈ 3.7 TB raw, voxel 1.24x0.439x0.439 um, zarr v2 chunks 1x128x362x362), tracks CSVs 0.2-0.85 GB each. Plan: download tracks.csv + HTTP-read ~50 crops 64x256x256 around tracks, resample to our voxel, measure recall vs our GT |
| 9 | Longer temporal window 3-6 for the linker (Trackastra, HOCT) | tried (exp05 window 3: worse) | revisit only with dense pseudo-tracks (item 8) |
| 10 | Parent-offset / movement-vector head (linajea, ELEPHANT, MPM) as edge feature + gap-closing prior | todo | extra 3-channel head + loss at annotated nodes; 1 h fine-tune |
| 11 | Edge-centric transformer with line-distance attention bias, two-pass ILP with learned long-range edges (HOCT) | todo, large | after 8/10; ~2-3 GPU-h |
| 12 | Node-count control: predict <= N_est (density head or confidence pruning off-track nodes) (hengck23, metric) | analysed: no free lunch | hold12: components of 4-6 nodes = 11.7% of nodes but 1.8% of GT-matched nodes; 7-15 = 29% / 9%. Dropping short components gives bonus ≈ loss (min-len 6: 0.9610 vs 0.9619). Would need a confidence signal, not length |
| 13 | Association consistency: examine ambiguous parent links from multiple views/models, use extra view only where they disagree (FOYSAL 730924) | todo | needs 2 models: exp03B + exp08 -> compare edge_prob disagreement |
| 14 | In-domain 3D-CNN MAE pretraining of the UNet encoder (Wald 2025, CANVAS weighting) | later | 1-2 GPU-h, gain +1-3% expected, after 5/8 |
| 15 | Frozen/duplicated frames (discussion 724283/729082) | scanned: only 6bba, 114/128 videos, ~8 frames each (947 total, 7%) | identical input => identical detections, zero-displacement links; no rule needed. Test embryos may have it too (`$TEMP/frozen_frames.json`) |
| 16 | Synthetic data (Freitas CC0, 18.5 GB) for division model pretraining | later | only if item 2 is data-starved |


## 9. Literature
`research/survey_detection_sparse_labels.md`, `research/survey_linking_divisions.md`, `research/discussions_summary.md`.
