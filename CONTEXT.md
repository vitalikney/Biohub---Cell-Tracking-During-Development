# CONTEXT — Biohub Cell Tracking (Kaggle) research project

Living document. Everything needed to continue the work without the chat history. Updated 2026-09-06 11:10.

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
**Pipeline v2.1 (2026-09-06 03:05):** ILP division weight 0.6 (was 1.2), gap closing 5 um, direct linking 8 um, post-hoc
divisions OFF: 48 videos 0.9271 (v2 0.9229). exp10 self-check on hold12: raw **0.9820** (div 8/19/6), pp **0.9902**
(adj 0.9660, edge 0.9554). Kernel biohub-exp10-submit-clean version 2 = the LB-probe candidate.
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
| exp10 v1 | submission notebook self-check (v2 config, ILP div 1.2) | raw 0.9575 / pp 0.9728 | matches local |
| exp10 v2 | self-check with config v2.1 (ILP div 0.6, gap5, direct8) | raw **0.9820** / pp **0.9902** (div 8/19/6) | LB-probe candidate (kernel version 2) |
| exp12 | ILP division weight sweep on 48 videos (hold12+divset36, 106 GT div), scored locally | div1.2: raw 0.9096 / v2 0.9229 / v2-nodiv 0.9158; div0.6: 0.9210 / 0.9249 / **0.9271**; div0.3: 0.9204 / 0.9248 / 0.9266 | ILP div 0.6 + gap5 + direct8, NO post-hoc divisions = config v2.1 (ILP forks: 24 TP/103 FP vs heuristic 23/172) |
| exp14 | fine-tune + intensity augmentation (gain/offset/gamma/haze) | 0.9345 | WORSE than exp03B 0.9575 (det loss 0.0022 -> 0.017; per-video -0.02..-0.09); augmentation too aggressive; not adopted |
| exp13 | ILP disappearance/appearance sweep on 48 videos, v2.1 post-proc | d1/a0 0.9149, d3/a0 0.9110, d2/a0.5 0.9216 (div 12/42) | reference d2/a0: 0.9158 (div1.2) / 0.9271 (div0.6); keep d2/a0 |
| exp16 | seed-7 fine-tune, exp03B recipe | 0.9502 (recall 0.972) | worse than exp03B 0.9575 and pretrained 0.9527: seed variance ±0.005 ≈ fine-tune gain. No ensemble retry |
| exp17 | 600-it fine-tune | 0.9556 | = exp03B within noise (per-video -0.08..+0.06); fine-tune length 600-2265 is not a lever |
| exp15 | ensemble exp03B+exp08 (avg det + edge logits), hold12, div 0.6 | raw 0.9708 (edge 0.9454, div 5/24/9) | WORSE than single exp03B 0.9820: averaging with the weaker exp08 hurts; 2x inference time. Re-test only with an equal-strength seed (exp16) |
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
- [x] 'Dim' videos are actually LOW-CONTRAST / high-background: 6bba_57b7cc1e q0.1=893 vs q0.999=1993 (ratio 1.7; 6bba median ratio 24), 6bba_786893ac q0.1=750 (ratio 4.5). Quantile normalisation (q0.001..q0.999) compresses the signal. => exp14: fine-tune with intensity augmentation (gain/offset/gamma) for background robustness; evaluate on hold12 + these 4 low-contrast videos.
- [x] exp12 scored: ILP division weight 0.6 + gap5 + direct8 without post-hoc divisions = 0.9271 (48 videos) => config v2.1; exp10 updated (BIOHUB_ILP_DIVISION_WEIGHT=0.6, BIOHUB_PP_DIV_PARENT_UM=0), self-check re-run pushed.
- [ ] exp13 running: ILP disappearance/appearance sweep on 48 videos -> score locally with v2.
- [x] exp14 intensity augmentation: worse (0.9345 vs 0.9575) - rejected. If low-contrast robustness is revisited: milder ranges (gain 0.8-1.25, offset ±0.1, no haze) or per-video background subtraction in normalisation (5c).
- [ ] Dense pseudo-labels for the detector (FOCUS-3D or Zebrahub crops) - feasibility test first.
Rules: max 2 GPU kernels at once; keep outputs zipped; log every result in RESULTS.md and §6.

### 10b. Plan agreed with the user (2026-09-06 02:55; revised 03:25)
Order of execution (GPU queue: max 2 kernels; CPU work in parallel):
1. [done] exp10 v2 = config v2.1 self-check on hold12: raw 0.9820 / pp 0.9902 (kernel version 2).
2. [done] exp13 ILP costs on 48 videos with v2.1 post-proc: d1/a0 0.9149, d3/a0 0.9110, d2/a0.5 0.9216 (div via appearance)
   vs reference d2/a0 0.9158 (div 1.2) / 0.9271 (div 0.6). No change to v2.1 (d2/a0/div0.6).
3. [done: rejected] **exp14** = fine-tune with intensity augmentation (item 3c: low-contrast/high-background videos).
   Evaluate: hold12 raw vs exp03B (0.9575), then the 4 low-contrast 6bba videos (57b7cc1e, 786893ac, 78a7bd97,
   ab78413d) raw and with v2.1; adopt if hold12 >= exp03B - 0.003 and low-contrast videos improve.
4. [DONE 06:30] **LB probe = 0.899** (kernel biohub-exp10-submit-clean v2, config v2.1, submission 56044199) vs the user's
   0.933 (public pipeline) and hold12 0.9902. **Local validation does not transfer** (see §11).
5. Model improvements, in priority (each through the ladder hold12 -> 48 videos -> LOEO -> exp10):
   a. Ensemble of 2-3 fine-tuned models (exp03B + exp08 + exp14/seed): average detection heatmaps + edge logits
      (predict-script patch, ~1 GPU-h per experiment).
   b. Detector loss for sparse labels (nnPU / ignore-unlabelled voxels, early stopping): 45 min fine-tune.
   c. Low-contrast robustness beyond augmentation if exp14 is not enough: per-video contrast normalisation
      (q0.1 background subtraction) applied consistently in train and predict.
   d. Dense pseudo-labels (FOCUS-3D / Zebrahub): compatibility check on ~50 crops first; biggest but costliest.
6. Keep CONTEXT.md/RESULTS.md/GitHub updated after every result.
7. Model-selection noise: fine-tune seeds span 0.950-0.958 on hold12; hold12 cannot resolve < 0.01 model effects.
   Use divset36+hold12 (48 videos) for model comparisons; post-proc/ILP effects are robust (confirmed on LOEO).

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


## 11. LB probe post-mortem (2026-09-06 06:40) and revised strategy — APPROVED by the user 07:00
- Clean pipeline v2.1: hold12 0.9902, LOEO 0.906, **LB 0.899**. The public 0.941 pipeline scores 0.933-0.941 on LB.
  Raw UNet+ILP reproductions on LB are ~0.89-0.90 (discussion), so our LB is consistent with "raw model + light post-proc".
- Why the local numbers lied: every model we evaluate is initialised from pilkwang weights trained on ALL 199 videos,
  so hold12 and even LOEO (fine-tuned on 6bba, but base saw 44b6) are memorised. On memorised videos aggressive
  linking (ILP div 0.6, direct 8 um) adds almost only correct edges; on unseen embryos it adds errors.
- Structural diff on the 4 dummy test videos (mine vs public 0.941): divisions 63/92/12/180 vs 51/10/6/27 (5-7x more
  forks), short components (<=5 nodes) 51/539/50/276 vs 0/28/0/0, nodes on 44b6_0b24845f 25.0k vs 18.5k, track ends
  795/2090/242/2720 vs 772/1234/204/2154. The public pipeline is far more conservative: fewer forks, no short tracks,
  fewer nodes (node-count bonus) and fewer fragments.
- Conclusions: (1) hold12/LOEO with pilkwang-initialised weights cannot validate linking/division aggressiveness;
  (2) the LB (2-4 probes/day) is the only trustworthy signal for post-processing; (3) a leak-free local validator
  would need a model trained from scratch on one embryo (≈1.3 GPU-h/epoch, 5+ epochs) - possible next week.
- Revised plan (approved; probes 1-2/day):
  a. Base = public 0.941 pipeline (exp02 notebook, kernel-validated). Keep our infrastructure (API runs, local metric).
  b. Change ONE thing per LB probe, 1-2 probes/day: (i) primary weights := exp03B (exp06 config; local neutral,
     LB unknown), (ii) add our direct end->start linking stage (conservative radius 5-6 um) after its post-proc,
     (iii) its ILP division weight 1.2 -> 0.9, (iv) DeepCenter/safe-division thresholds untouched.
  c. In parallel (GPU, next week's quota): from-scratch 6bba-only model for a leak-free LOEO validator; then
     pseudo-label / loss experiments can be judged locally.
  d. Stop spending GPU on fine-tune variants (seed noise ±0.005 > effects).
- LB probe log: #1 06:30 clean v2.1 = 0.899. #2 07:06 exp06 (public pipeline + exp03B primary) = pending (id 56049333).
  Direct linking on top of the public pipeline is useless (its motion-relink leaves 0 end->start pairs within 5 um).
  #3 10:35 exp18 (public pipeline, ILP div 0.9, validator off) = pending (id 56049863), submitted while #2 pending -> parallel-scoring check.
  Candidates after: det threshold 0.965->0.95; secondary := fine-tuned too (if #2 positive); SECONDARY_DETECTION_WEIGHT 0.8->0.5.

### 11a. LB-probe protocol (agreed 2026-09-06 10:30)
- Cadence: **4 probes/day + 1 in reserve** (user 11:10). Daily limit per the API counter is 5, resets ~03:00 MSK.
  Scoring takes 3-5 h. Whether Kaggle scores two submissions in parallel is to be verified with the next pair
  (exp18 submitted while probe #2 is still pending); if sequential, stagger them.
- Each probe = exactly ONE change vs the public 0.941 pipeline, so the result is interpretable.
- Candidate order (each chosen after the previous results): (1) primary weights := exp03B [running, probe #2];
  (2) ILP division weight 1.2 -> 0.9 [exp18, today as soon as its run finishes]; (3) det threshold 0.965 -> 0.95 [exp19, kernel running];
  (4) SECONDARY_DETECTION_WEIGHT 0.8 -> 0.5; (5) secondary := fine-tuned weights (if (1) positive);
  (6) OUTPUT_MIN_TRACK_LEN 6 -> 4. Positive changes are then combined into one notebook and verified by a joint probe
  (effects may not add up).
- Rules (user 11:00): do NOT launch new Kaggle kernels or submissions until the first pending probe is scored;
  differences < 0.002 = noise, not adopted; every probe logged in §11 (probe log) with kernel, change, LB;
  from 26 Sep only final-submission probes, no new ideas.
- GPU: each probe needs one prior notebook run (15-40 min) => ~2-2.5 GPU-h/day at 4 probes; ~11 h left this week - enough for ~4 days, then next week's quota.
  Heavy model work (from-scratch model for a leak-free validator) moves to next week's quota.

## 9. Literature
`research/survey_detection_sparse_labels.md`, `research/survey_linking_divisions.md`, `research/discussions_summary.md`.
