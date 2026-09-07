# CONTEXT — Biohub Cell Tracking (Kaggle) research project

Living document. Everything needed to continue the work without the chat history. Updated 2026-09-06 18:30.

## 1. Goal and constraints
- Competition: https://www.kaggle.com/competitions/biohub-cell-tracking-during-development — detect nuclei, link them
  across frames, find divisions in 3D+t light-sheet zebrafish embryo videos. Code competition, internet off at scoring.
- Deadline 2026-09-29 (entry 22 Sep). User (Kaggle `vitaliineibauer`) started at rank 611/3140 with public 0.933.
  LB top 0.970, top-20 >= 0.947. Public LB ≈ 29% of test.
- Metric: score = adj_edge_J + 0.1*div_J (see §4). Official code: github.com/royerlab/kaggle-cell-tracking-competition.
- LB rank after probe 2: **46 / 3174** (2026-09-06 17:10).
- Compute: no local GPU. Kaggle 30 GPU-h/week (2x T4), max 2 concurrent GPU sessions. Code requirements: notebook
  rerun <= 12 h (GPU or CPU), internet off, public external data/pretrained models allowed, output `submission.csv`.
  Scoring time observed: clean pipeline ~2 h, public 0.941 pipeline ~6 h (hidden test ≈ 100-130 videos by that ratio). Experiments run as private
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
| local Friend A exp01 | raw **0.6706** (edge 0.6688, div 0/0/15, recall 0.8600); fixed pp v2 **0.6891** (adj edge 0.6869, edge 0.6856, div 1/31/14, recall 0.8649); internal sparse recall best 0.8944 at epoch 4 | from-scratch 6bba -> LOEO-44b6, 5 epochs | leak-free checkpoint; 12/12 videos; det 0.965, TTA, NMS5 from config, ILP app 0 / disapp 2 / div 1.2; validator-aligned diagnostic 0.6603 |
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

## 8. Ideas backlog
Merged into §10a (single prioritised list with tried/queued/parked status). Do not maintain a second list here.

## 10. Next steps (checklist; re-check after every CONTEXT update, run independent items in parallel)
- [x] exp08 full epoch: worse (0.9539). Keep exp03B. Consider shorter (600 it) / lower-LR run and 2-3 seed ensemble later.
- [x] exp09 sweep: gap 5um / div parent 5 sister 12 remain best but small (+0.006 total on divset36); keep config, do not over-tune.
- [x] exp10 submission notebook built (`experiments/exp10_submit_clean`), self-check on hold12 enabled; CSV writer dry-run OK locally (251k nodes / 237k edges on hold12, no dangling refs).
- [x] exp10 ran on Kaggle: hold12 self-check raw 0.9575 / pp 0.9728 (exact), valid submission.csv, ~2.5 h projected for hidden test. Output saved in experiments/exp10_submit_clean/results/.
- [x] LB probe with exp10 (v2.1): 0.899 - clean pipeline does not transfer; see §11.
- [x] LOEO check: exp11 done (A 0.8798 vs B 0.8825 on 44b6); post-proc v2 transfers (+0.023 on unseen embryo, every stage positive). Built (`experiments/exp11_loeo_6bba_to_44b6`, split `_lib/loeo_train6bba_val44b6.json`: 126 6bba train, 12 44b6 val, 15 divisions); push when a GPU slot frees; then local post-proc transfer test on its zipped predictions.
- [x] Division ranker prototype (tools/divranker.py) - weak; candidate recall is the bottleneck.
- [x] Error decomposition on divset36 (tools/errdecomp.py): recovered 93.3% of GT edges; lost to detection 3.6% (missed GT nodes 2.6%), fragmented 3.1%, wrong association ~0. Detection misses concentrate in 2 dim videos (6bba_57b7cc1e 237/1659 nodes missed, 6bba_786893ac 156/1465) = 43% of all detection losses. Fragmentation: 468 src-no-successor, 566 tgt-no-predecessor, 274 both linked elsewhere.
- [x] Residual direct end->start linking (`direct_um`, mutual NN, t->t+1): hold12 0.9619 -> 0.9634/0.9645/0.9654 (4/6/8 um), divset36 0.9002 -> 0.9041/0.9051/0.9056. Works on both sets. 10/12 um worse; with divisions: hold12 0.9780, divset36 0.9117 => pipeline v2 adopted.
- [x] 'Dim' videos are actually LOW-CONTRAST / high-background: 6bba_57b7cc1e q0.1=893 vs q0.999=1993 (ratio 1.7; 6bba median ratio 24), 6bba_786893ac q0.1=750 (ratio 4.5). Quantile normalisation (q0.001..q0.999) compresses the signal. => exp14: fine-tune with intensity augmentation (gain/offset/gamma) for background robustness; evaluate on hold12 + these 4 low-contrast videos.
- [x] exp12 scored: ILP division weight 0.6 + gap5 + direct8 without post-hoc divisions = 0.9271 (48 videos) => config v2.1; exp10 updated (BIOHUB_ILP_DIVISION_WEIGHT=0.6, BIOHUB_PP_DIV_PARENT_UM=0), self-check re-run pushed.
- [x] exp13 scored: no change (see §10b.2).
- [x] exp14 intensity augmentation: worse (0.9345 vs 0.9575) - rejected. If low-contrast robustness is revisited: milder ranges (gain 0.8-1.25, offset ±0.1, no haze) or per-video background subtraction in normalisation (5c).
- [ ] Dense pseudo-labels for the detector (FOCUS-3D or Zebrahub crops) - assigned to friend B (TEAM.md).
- [ ] From-scratch 6bba model (leak-free validator) - assigned to friend A, running on RTX 5070 Ti (branch merged 2026-09-06).
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

### 10a. Ideas queue — prioritised, with what was already tried (rewritten 2026-09-07 04:40)
Ordering rule (from §11 + discussions 2026-09-07): the only LB gain so far came from WEIGHTS (+0.004); post-processing
and linker knobs are saturated on the public pipeline and local linking gains do not transfer to LB. So: model/detection
ideas first, honest LOEO check before any LB probe, one change per probe, differences < 0.002 = noise.

**A. Already tried (do not repeat without a new angle)**
| # | idea | where | result |
|---|---|---|---|
| A1 | primary weights := our fine-tune exp03B (1200 it, lr 5e-5) | LB probe 2 (exp06) | **+0.004 (0.941 -> 0.945), adopted as base** |
| A2 | ILP division weight 1.2 -> 0.9 | LB probe 3 | 0.941, neutral, dropped |
| A3 | detection threshold 0.965 -> 0.95 | LB probe 4 | 0.940, neutral, dropped |
| A4 | secondary detection weight 0.8 -> 0.5 | LB probe 5 | 0.943, -0.002, dropped |
| A5 | clean pipeline (exp03B + ILP div 0.6 + gap 5 + direct 8, no public post-proc) | LB probe 1 (exp10) | 0.899 vs local 0.990: leaky validation; public heuristics worth +0.046 on unseen embryos |
| A6 | post-hoc divisions + gap closing (item 1 old numbering) | local hold12/divset36 | +0.015 local; on the public pipeline direct linking finds 0 pairs, divisions 1 TP / 31 FP on the honest validator -> keep DIV_PARENT_UM=0 |
| A7 | velocity-projected gap closing (discussion 739570) | local | neutral (0.9619 -> 0.9621) |
| A8 | division ranker on candidate forks (tools/divranker.py) | local divset36 | candidate recall 35% is the bottleneck; GBM top-200 = 8 TP vs rule 12 TP; parked |
| A9 | ILP div weight 0.6 / disappearance-appearance sweep (exp12/exp13) | local 48 videos | v2.1 config; does not transfer (A5) |
| A10 | gauss-focal heatmap loss (exp04) | local | 0.909 vs 0.958: calibration shifts; only worth retrying with a threshold re-sweep |
| A11 | linker window 3 (exp05) | local | 0.953 vs 0.958, worse; revisit only with dense pseudo-tracks |
| A12 | full-epoch fine-tune 2265 it (exp08), 600 it (exp17), seed 7 (exp16) | local | 0.954 / 0.956 / 0.950 vs 0.958: 1200 it seed 42 stays; seed noise +-0.005 |
| A13 | intensity augmentation for low-contrast videos (exp14) | local | 0.935, worse; milder ranges only if revisited |
| A14 | inference ensemble exp03B+exp08 (exp15) | local | 0.971 vs 0.982 raw, worse (both from the same pilkwang primary -> no diversity) |
| A19 | OUTPUT_MIN_TRACK_LEN 6 -> 4 | LB probe 6 (exp21) | 0.943, -0.002: shorter tracks hurt; opposite direction (8) queued as probe 9 |
| A18 | secondary weights := exp08 (fine-tune of the same primary as exp03B) | LB probe 7 (exp22) | **0.929, -0.016**: no diversity + post-proc thresholds tuned for the seed314159 secondary; keep pilkwang secondary |
| A15 | node-count control by dropping short components | local analysis | bonus = loss (0.9610 vs 0.9619); needs a confidence signal, not length; LB direction probe pending (min len 4 / 8) |
| A16 | frozen/duplicated frames | scan | only 6bba, 7% of frames; identical input => identical detections; no rule needed |
| A17 | from-scratch 6bba model, 5 epochs (friend A) | honest LOEO 44b6 | 0.671 raw / 0.689 pp: undertrained; validator not usable yet |

**B. Queue, priority order**
| P | # | idea (source) | owner | next step / cost | gate before LB |
|---|---|---|---|---|---|
| P1 | B1 | LB direction probes: OUTPUT_MIN_TRACK_LEN 4 (probe 6, pending) and secondary := exp08 (probe 7, pending); then min len 8 and gap-closing radius as the LAST post-proc probes | Vitalii | 25 min kernel each | none (LB is the test) |
| P1 | B2 | fine-tune the pilkwang seed314159 SECONDARY with the exp03B recipe (exp23) -> probe as secondary (different init than exp03B/exp08). CAUTION after probe 7 (-0.016 with exp08 as secondary): a fine-tuned secondary shifts detection calibration vs the public post-proc thresholds; probe only if the LOEO check is clearly positive | Vitalii | 30 min train + 25 min kernel | LOEO on 44b6 with the full public pipeline (friend B's port) |
| P1 | B3 (was 17) | dense self-distillation: teacher = public pipeline detections on all 199 videos + GT points; student = from-scratch model (Dense Teacher / MUSE) | friend A (+ friend B for teacher predictions) | teacher preds 1.5 GPU-h Kaggle or 3-4 h on a 5070; then the all-199 scratch run | LOEO: 6bba teacher labels -> score on 44b6 >= exp03B raw 0.88 |
| P1 | B4 | friend A's all-199 scratch model (dense labels if B3 ready, else sparse with official-metric early stopping every 5 epochs) as SECONDARY in the blend | friend A -> Vitalii | 1-2 days on 5070 Ti + 1 probe | beats pilkwang secondary on LOEO 44b6 |
| P1 | B5 (was 18) | test-time adaptation of the primary detector on the test embryos (DARTH-style self-training + photometric consistency, EMA teacher, node-count guard) | Vitalii | ~1 day engineering; ~30 min GPU per embryo inside the submission kernel | LOEO: adapt on 44b6 images without labels, score on 44b6 GT >= +0.005 |
| P2 | B6 (was 7) | detector TTA / seed-ensemble as primary with dedup merge (exp03B + exp16 + pilkwang) | Vitalii | check how the public notebook runs inference first; +0.5 h | LOEO |
| P2 | B7 (was 5) | ignore-unlabelled / nnPU detection loss, neighbourhood-softmax peak loss | friend A | patch train_patches.py; 45 min per fine-tune | LOEO |
| P2 | B8 (was 10) | parent-offset / movement-vector head as edge feature + gap-closing prior (linajea, ELEPHANT) | friend A | 1 h fine-tune + linker feature | LOEO |
| P2 | B9 (was 4, 13) | metric-aware ILP cost calibration; association consistency between two models where they disagree | friend B (after the local port) | CPU sweeps on cached candidate graphs | LOEO (linker gains transfer poorly - be strict) |
| P2 | B10 (was 12) | node-count control with a confidence signal (density head or off-track low-confidence pruning) | friend B | CPU on cached predictions | LOEO + LB direction probes (B1) |
| P3 | B11 (was 8) | dense pseudo-labels from FOCUS-3D / Zebrahub (hengck23; no LB proof yet) | friend B | 2-3 days; only if B3 fails or saturates | LOEO |
| P3 | B12 (was 9, 11) | longer linker window 3-6 and HOCT-style edge-centric transformer | friend A | needs dense tracks (B3/B11); 2-3 GPU-h | LOEO |
| P3 | B13 (was 14) | in-domain MAE pretraining of the UNet encoder | friend A | 1-2 GPU-h; +1-3% expected | LOEO |
| P3 | B14 (was 6) | gauss/anisotropic heatmap targets, retry with threshold re-sweep on exp04 weights | anyone | 0.5 h | LOEO |
| P3 | B15 (was 2) | division ranker with more candidates (lower ILP div cost) | parked | data-starved (151 GT divisions) | - |

**C. Dropped**
- Synthetic data (Freitas CC0; item 16): 1st place tried synthetic volumes 2 weeks, no gain (discussion 739731).
- More post-proc knobs beyond B1 (motion-relink radius, DeepCenter veto, etc.): saturated, noise-level.
- Hand labelling of test data: forbidden; SAM2 zero-shot tracking: too heavy/weak for 3D+t here.

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
  #2 = **0.945** (public pipeline + exp03B primary; +0.004 vs public 0.941, +0.012 vs user's 0.933). #3 exp18 (ILP div 0.9) = 0.941 (neutral).
  Both scored in parallel (submitted 28 min apart, completed together at 17:06 MSK; ~6 h each).
  #4 17:10 exp19 (public pipeline, det 0.95, validator off) = **0.940** (scored 22:40; vs 0.941 = neutral/noise, DROPPED;
  det threshold stays 0.965). New base for stacking = exp06 config (0.945).
  #5 17:57 exp20 (exp06 base, SECONDARY_DETECTION_WEIGHT 0.5, validator off) = **0.943** (scored 2026-09-07 00:15; vs base
  0.945 = -0.002, NEGATIVE, dropped; secondary weight stays 0.8). Base for stacking stays exp06 (0.945).
  #6 2026-09-07 03:08 exp21 (exp06 base, OUTPUT_MIN_TRACK_LEN 4, validator off) = **0.943** (scored ~10:00; -0.002, negative:
  more short tracks = more nodes, no gain). Direction => try min len 8 (exp25, probe #9).
  #8 2026-09-07 10:12 exp24 (exp06 base, GAP_CLOSE_UM 6.5, validator off) = pending (id 56071497).
  #9 2026-09-07 11:07 exp25 (exp06 base, OUTPUT_MIN_TRACK_LEN 8, validator off) = pending (id 56072510). 1 slot left today (reserve).
  #7 2026-09-07 03:08 exp22 (exp06 base, secondary weights := exp08, validator off) = **0.929** (scored ~09:00; -0.016 vs 0.945,
  STRONGLY NEGATIVE, dropped). Lesson: the blend needs a DIFFERENT model as secondary; exp08 is a fine-tune of the same
  pilkwang primary as exp03B (no diversity) and the public post-proc thresholds are tuned for the seed314159 model. 3 slots left today.
  Candidates after: det threshold 0.965->0.95; secondary := fine-tuned too (if #2 positive); SECONDARY_DETECTION_WEIGHT 0.8->0.5.

### 11a. LB-probe protocol (agreed 2026-09-06 10:30)
- Cadence: **5 probes/day, no reserve** (user 2026-09-06 18:00, replaces the earlier 4+1). Daily limit per the API counter
  is 5, shared by the whole Kaggle team, resets ~03:00 MSK (00:00 UTC).
  Scoring takes 3-5 h. Whether Kaggle scores two submissions in parallel is to be verified with the next pair
  (exp18 submitted while probe #2 is still pending); if sequential, stagger them.
- Each probe = exactly ONE change vs the public 0.941 pipeline, so the result is interpretable.
- Candidate order (each chosen after the previous results): (1) primary weights := exp03B [DONE: 0.945, adopted];
  (2) ILP division weight 1.2 -> 0.9 [DONE: 0.941, neutral, dropped]; (3) det threshold 0.965 -> 0.95 [DONE: 0.940, neutral, dropped];
  (4) SECONDARY_DETECTION_WEIGHT 0.8 -> 0.5 on the exp06 base [DONE: 0.943, negative, dropped]; (5) secondary := fine-tuned weights (if (1) positive);
  (6) OUTPUT_MIN_TRACK_LEN 6 -> 4.
- Combination rule (user 18:15): as soon as TWO positive single changes (>= +0.002 each) exist on top of the current
  base, the very next probe is their combination; if it holds, it becomes the new base. So far only (1) is positive
  and it is already the base (exp06 = 0.945).
- Rules (user 11:00): do NOT launch new Kaggle kernels or submissions until the first pending probe is scored;
  differences < 0.002 = noise, not adopted; every probe logged in §11 (probe log) with kernel, change, LB;
  from 26 Sep only final-submission probes, no new ideas.
- GPU: each probe needs one prior notebook run (15-40 min) => ~2-2.5 GPU-h/day at 4 probes; ~11 h left this week - enough for ~4 days, then next week's quota.
  Heavy model work (from-scratch model for a leak-free validator) moves to next week's quota.
- Submission limit is per TEAM, not per account (checked on the official rules page 2026-09-06 18:50): 5/day, max team
  size 5, team merger deadline **2026-09-22**, final deadline 2026-09-29. Rules 3.5.a / 3.5.d / 3.6.a: submitting through
  another account acting as a proxy = disqualification; privately sharing code outside a Kaggle Team = disqualification.
  => the "3 accounts = 15 probes/day" idea is REJECTED (user asked, 18:40). We are ALREADY one Kaggle Team
  (confirmed on the Team tab 2026-09-06 19:00: leader Vitalii, members Sasyami + gsfatakhov, 2 free slots), so code and
  weights sharing is legal and the 5/day limit is shared by all three accounts (friends must NOT submit, it eats our
  budget). Gain from the team: 3 GPU quotas — friends can run probe-prep kernels under their own accounts.

## 13. Status summary for the team (2026-09-06 17:30)
What is proven on the LB (the only trustworthy signal):
- Public 0.941 pipeline + our fine-tuned primary weights (exp03B) = **0.945**, rank 46/3174. This is the production base.
- Our clean pipeline (fine-tuned model + ILP + light post-proc) = 0.899: the public pipeline's conservative heuristics
  (dual-seed detection blend, DeepCenter veto, short-track filter, safe divisions) are worth +0.046 on unseen embryos.
- ILP division weight 0.9 = 0.941 (neutral); det threshold 0.95 = 0.940 (neutral). Secondary detection weight 0.5 = 0.943 (negative). Next: min track len 4 (probe 6), secondary := exp08 (probe 7).
What is proven locally but does NOT transfer: everything measured on train videos with pilkwang-initialised models
(hold12 0.99, LOEO 0.906) - leaky. Local numbers are only useful to compare post-proc variants relative to each other.
What this means for the team:
- Friend A: the from-scratch 6bba model is the key enabler - it gives the first honest local validator. First result
  (22:15): 0.671 raw / 0.689 with pp v2 after 5 epochs - undertrained; continue to 30 epochs with official score every 5. Next for A:
  from-scratch on all 199 videos, 30-50 epochs (1-2 days) as a candidate primary/secondary for the public pipeline.
- Friend B (re-prioritised 18:00): FIRST port the public pipeline's post-processing to a local script (CPU, no wait),
  THEN honest evaluation on friend A's checkpoint (12 44b6 videos, pipeline stages vs ours), pseudo-labels last
  (FOCUS-3D ≈ 2-3 days on a 5070, long payoff chain).
- Vitalii: 5 LB probes/day on the public pipeline (one knob each), weights from friend A into the pipeline as soon as
  they beat exp03B on the honest validator.

## 12. Team (2026-09-06)
Three people (Kaggle team: Vitalii = leader, friend A = Sasyami, friend B = gsfatakhov): Vitalii (Kaggle + LB probes + coordination), friend A (RTX 5070 Ti: training, first the from-scratch 6bba
validator), friend B (RTX 5070: inference/evaluation/pseudo-labels). Roles, onboarding and rules in `TEAM.md`.

- 2026-09-06: Friend A root-level `friend-a-loeo-scratch.ipynb` completed five scratch epochs on 126 6bba videos
  in 2 h 33 min; best internal sparse recall 0.8944 at epoch 4. Official LOEO-44b6 evaluation on all 12 videos:
  raw score 0.6706; fixed post-processing v2 score 0.6891 (adjusted edge 0.6869, raw edge 0.6856,
  node recall 0.8649, divisions 1/31/14). Predictor now reads NMS5 from checkpoint config. No LB submission.

## 14. Operational state for session resume (2026-09-06 18:00 MSK) — READ THIS FIRST AFTER A CONTEXT RESET
Pending right now:
- LB probe #4 = kernel `vitaliineibauer/biohub-exp19-pub941-det095` v1 (public pipeline, det 0.95) = 0.940, scored 22:40 MSK
  (neutral, dropped). Check: `python -m kaggle competitions submissions biohub-cell-tracking-during-development`.
- LB probe #5 = kernel `vitaliineibauer/biohub-exp20-ft03b-secdet05` v1 (exp06 base + SECONDARY_DETECTION_WEIGHT 0.5,
  validator off) = 0.943, scored 2026-09-07 00:15 MSK (negative, dropped). Next slots ~03:00 MSK 2026-09-07.
- LB probe #7 (exp22, secondary := exp08, id 56065255) = 0.929 (-0.016, dropped). Probe #6 (exp21, min track len 4,
  id 56065251) = 0.943 (-0.002, dropped). exp25 = min track len 8 built and pushed ~10:05 as probe #9 candidate. 3 daily slots left.
- exp24 = exp06 base + BIOHUB_GAP_CLOSE_UM 5.0 -> 6.5 (direction probe) kernel `vitaliineibauer/biohub-exp24-ft03b-gap65`
  pushed 2026-09-07 ~09:20 MSK; SUBMITTED as probe #8 at 10:12 MSK (id 56071497, pending). exp25 (min len 8) SUBMITTED as probe #9 at 11:07 MSK
  (id 56072510, pending). These are the LAST post-proc probes.
- exp23 (user "запускай" 11:40): kernel `vitaliineibauer/biohub-exp23-ft-secondary` v1 pushed 11:45 MSK = fine-tune the
  pilkwang seed314159 SECONDARY with the exp03B recipe (1200 it, batch 8, lr 5e-5, BCE, seed 42); also measures the raw
  seed314159 model on hold12 (A) vs fine-tuned (B), leaky sanity only. ~50 min. When COMPLETE: `kaggle kernels output
  vitaliineibauer/biohub-exp23-ft-secondary -p <dir>` -> `ft_weights/unet_transformer/split_0/{edge_predictor_best.pth,config.json}`
  -> `weights_dataset/exp23/` -> `kaggle datasets version -p weights_dataset --dir-mode zip -m "exp23"` -> tell friend B
  (TEAM.md, friend B step 2). NO LB probe until friend B's check (>= +0.003 as secondary in the full pipeline). After probe #6: if min len 4 is
  negative -> build exp25 with BIOHUB_OUTPUT_MIN_TRACK_LEN=8 (probe #9); if positive -> it becomes part of the base.
  Then post-proc probes STOP (see §10a B1) and the queue moves to B2-B5 (model side). After scoring: both >= +0.002 -> combination
  probe; else next single knobs (gap-closing radius, motion-relink radius, DeepCenter veto threshold) via make_probe.
- CONTINGENCY PLAN if #6/#7 are flat (discussed with the user 2026-09-07 03:30): post-proc knobs are saturated (3 flat
  probes; LB noise +-0.002; the only real gain, +0.004, came from weights). (1) Today's 3 slots: two DIRECTION probes
  only - OUTPUT_MIN_TRACK_LEN 8 (if 4 was negative; fewer nodes = metric bonus) and gap-closing radius; 3rd slot reserve.
  Then STOP single post-proc knobs. (2) Model-side probes only, each expected >= +0.003: exp23 = fine-tune the pilkwang
  seed314159 SECONDARY with the exp03B recipe (1200 it, ~30 min GPU) and probe it as secondary [note: probe #7's exp08 is a
  fine-tune of the same PRIMARY as exp03B -> little diversity, so a negative #7 does not settle this]; seed ensemble
  (exp03B + exp16) as primary if the public notebook's inference can average logits (check first); friend A's all-199
  scratch model as secondary = biggest lever (independent model = diversity in the blend). (3) Escape the 5/day limit:
  friend A's validator at >= 0.85 + friend B's local port of the post-processing -> sweep knobs locally, LB confirms.
  (4) From 26 Sep: two final submissions = best LB config + one conservative variant.
- Discussion re-read 2026-09-07 03:50 (research/discussions_summary.md, "Update 2026-09-07"): no new probe-worthy idea.
  Three signals that CONFIRM the plan: (a) linking gains do not transfer to LB even cross-embryo (Pavel: +0.02-0.04 on
  5 folds, +0.000 LB) -> spend probes on weights/detection, not linker tweaks; (b) 1st place tried synthetic volumes for
  2 weeks with no gain -> synthetic dataset removed from friend B's queue; (c) sparse-GT detectors peak at epoch 5-10 and
  then over-detect -> friend A's 30-epoch run must keep the best official-metric checkpoint and log N_pred/N_est per
  epoch; if the peak is early, go to all-199 data instead of more epochs.
- Literature pass 2026-09-07 04:20 (research/survey_detection_sparse_labels.md, "Update 2026-09-07"): two new ideas added
  to §10a as items 17 (dense self-distillation from our own pipeline -> friend A's all-199 run) and 18 (test-time
  adaptation on the test embryos, DARTH-style). Both get an honest LOEO check before any LB probe.
  Submit template: `python -m kaggle competitions submit biohub-cell-tracking-during-development -k <kernel> -v 1 -f submission.csv -m "probe N: ..."`.
- Rule (user): when a probe-ready kernel is COMPLETE and a daily slot is free, submit immediately, do not wait.
- Background watch (session-local, restart after a session restart): ONLY the LB submissions watch until #4/#5 are
  scored (single event). Repo-branch and weights-dataset watches were switched OFF at the user's request (20:10) to save
  the Fable limit: the user tells us when a friend pushes or uploads weights. On such a message: review the diff and merge
  into main / add a RESULTS row, and if the friend's validator says the weights beat exp03B, one LB probe with them as
  primary (make_probe: edit BIOHUB_PRIMARY_OVERRIDE).
  2026-09-06 22:15: FIRST HONEST NUMBER. Friend A's from-scratch checkpoint (126 6bba videos, 5 epochs, best epoch 4)
  scored with the official metric on the 12 unseen 44b6 videos: raw 0.6706 (edge J 0.669, node recall 0.86, div 0/0/15);
  with our post-proc v2 0.6891 (+0.016 adj edge from gap closing + direct linking; post-hoc divisions 1 TP / 31 FP =
  +0.002 only -> confirms DIV_PARENT_UM=0 as the safe LB setting). Files: `result.md`,
  `experiments/local_friend_a_exp01_loeo_scratch/official_loeo_metrics*.json`. Interpretation: far below the ~0.85 we
  guessed; 5 epochs x 126 videos vs pilkwang's 50 epochs x 199 -> undertrained, not a linker design problem. A 0.69 model
  is a different error regime from the 0.94 LB pipeline, so post-proc conclusions on it do NOT transfer yet. Validator
  becomes useful for relative decisions once the scratch model reaches ~0.85. Weights NOT needed in the dataset yet.
  Next for friend A (asked 22:30): continue the SAME 6bba-only recipe to 30 epochs (~15 h on the 5070 Ti), checkpoint
  every 5 epochs, official score each -> honest learning curve; then the all-199 model for the pipeline.
  Friend A's tool fixes merged: predictor reads pool_kernel_um (NMS 5 um) from config.json (was silently 3 um; identical
  graphs at det 0.965), `--no-det-tta`, BIOHUB_PREDICTIONS_DIR / BIOHUB_DATA_DIR env overrides in dataspec/score_geffs.
  Dataset state 2026-09-06 19:40: exp03B/, exp08/ only. Friend A's branch merged into main at b3786d7 (Windows fixes,
  notebook moved to repo root; full 5-epoch run not started yet).
- PLAN APPROVED by the user (2026-09-06 23:50, "stick to it; submit probes 6 and 7 without me"):
  1. When probe #5 is scored: log it (§11, §14, RESULTS), push.
  2. Probe #5 >= 0.947 -> SECONDARY_DETECTION_WEIGHT=0.5 becomes the base (add `--env BIOHUB_SECONDARY_DETECTION_WEIGHT=0.5`
     to every later build); < 0.947 -> base stays exp06 (0.945). Either way build exp21 = base + `BIOHUB_OUTPUT_MIN_TRACK_LEN=4`
     and exp22 = base + `--secondary-override exp08` with make_probe, push both kernels (2 GPU slots, ~25 min each,
     validator off), and at the ~03:00 MSK reset submit them as probes #6 and #7 (no user confirmation needed).
  3. Remaining 3 daily slots: if #6 and #7 are both >= +0.002 -> their combination; else next single knobs on the
     public pipeline: gap-closing radius, motion-relink radius, DeepCenter veto threshold (one knob per probe).
  4. GPU: a probe kernel costs ~25 min (the ~5.5 h is Kaggle's scoring time), so 5 probes/day ~ 2 GPU-h; ~10 h left this week.
  5. Team in parallel: friend A continues the 6bba scratch recipe to 30 epochs with an official score every 5 epochs
     (validator usable from ~0.85; the all-199 model goes into a probe as primary once it beats exp03B there);
     friend B ports the public pipeline's post-processing locally.
- Decision tree after probes #4 (det 0.95) and #5 (secdet 0.5) are scored (user 18:20: do not pre-build, combine
  positives): both >= 0.947 -> next probe = combination `exp23_ft03B_det095_secdet05`; exactly one positive -> it becomes
  the base (add its env to every later build) and the next single knobs go on top; none -> next knobs on the exp06 base.
  Next single knobs: `--env BIOHUB_OUTPUT_MIN_TRACK_LEN=4` (exp21), `--secondary-override exp08` (exp22).
  Build any variant with `python experiments/_lib/make_probe.py --name <expNN_slug> [--env K=V ...] [--secondary-override exp08]`
  (writes experiments/<name>/ with notebook + kernel-metadata.json + probe.json; tested against the hand-made exp19/exp20
  diffs), then `python -m kaggle kernels push -p experiments/<name>`, wait COMPLETE (~25 min, validator off), submit.
- Next probe candidates (one knob each, on the exp06 base 0.945): secondary := fine-tuned weights (exp08 or exp16 in the
  dataset); OUTPUT_MIN_TRACK_LEN 6 -> 4; combination of positives per §11a rule. Build them like exp18-exp20: copy
  `experiments/exp06_pipeline_ft03B/exp06-pipeline-ft03B.ipynb`, edit the env line in the config/setup cell (mind that the
  setup cell overrides some env vars, e.g. SECONDARY_DETECTION_WEIGHT), set BIOHUB_VALIDATOR_ENABLE=0, push with a new
  kernel id, wait COMPLETE (~25 min), then submit that kernel version.
- Friend A is training the from-scratch 6bba validator on his RTX 5070 Ti (branch merged; folder
  `experiments/local_friend_a_exp01_loeo_scratch/`); friend B ports the public pipeline locally (TEAM.md).
How-tos:
- Kernel status: `python -m kaggle kernels status <id>`; outputs: `python -m kaggle kernels output <id> -p <dir>` (retry on
  timeouts; large outputs are slow — keep notebooks' outputs small).
- Local scoring: `python tools/score_geffs.py <dir of .geff>`; post-proc: `tools/postproc.py`; error split: `tools/errdecomp.py`.
- Weights dataset upload: see TEAM.md §Onboarding 3. Commit as the user (no Claude co-author), push to origin main.
- GPU quota this week: ≈20/30 h used (resets in ~5 days); only probe-prep kernels (15-40 min each) from now on.
Numbers to remember: LB probes 0.899 (clean v2.1) / 0.945 (public + exp03B primary, rank 46) / 0.941 (ILP div 0.9);
the user's original 0.933; public notebook 0.941; LB top 0.970.

## 9. Literature
`research/survey_detection_sparse_labels.md`, `research/survey_linking_divisions.md`, `research/discussions_summary.md`.
