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
- `weights_dataset/` — the team weights dataset, fully in git (mirror of Kaggle `vitaliineibauer/biohub-ft-weights`); `params.yaml` — paths, slugs, base recipe knobs, LB rules (2026-09-15).
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
- Division J = TP/(TP+FP+FN) on genuine parent->2 daughters forks near GT divisions. OFFICIAL RULE (metrics.md of
  github.com/royerlab/kaggle-cell-tracking-competition, verified 2026-09-11): local parent anchor (the predicted fork
  must be a matched parent-side node or the immediate successor of one), two GT daughter lineages matched to two
  DISTINCT predicted child branches, directed local topology, no merged branches, then a max-cardinality bipartite
  pairing. Literally: "Merely sharing a weakly connected component is not sufficient." A one-to-one
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
| A21 | OUTPUT_MIN_TRACK_LEN 6 -> 8 | LB probe 9 (exp25) | 0.944, -0.001: noise; with A19 (4 -> 0.943) the node-count bonus is not exploitable via track length |
| A22 | secondary := friend A from-scratch all-199 epoch 21 | LB probe 10 (exp27) | **0.920, -0.025**: weaker than pilkwang secondary (4 dummy videos: -0.007, recall/edge FP worse); blend weight 0.8 amplifies it; needs honest raw comparison first |
| A23 | sjlee101 full TTA stack verbatim (B17) | LB probe 14 (exp29) | **0.947 reproduced** -> ADOPTED as base / final candidate 1 |
| A24 | exp03B primary on the sjlee TTA stack (sweep off) | LB probe 11 (exp30) | 0.944, -0.003 vs exp29: no gain; +3.2% nodes at det 0.965 (node-count bonus shrinks); deconfound probe 15 (exp33) pending; next: det threshold re-calibration 0.97/0.975 ; CONFIRMED by probe 15 (exp33, one change: 0.944) - closed |
| A25 | Z-flip views added to both edge-feature TTA loops (on the exp03B/sweep-off base) | LB probe 12 (exp31) | 0.941, -0.003 vs exp30 = tie (noise floor), not a negative; leaky local +0.010; RE-TEST on the clean exp29 base = probe 16 (exp34) ; RE-TEST probe 16 (exp34, clean base) = **0.938, -0.009**: real negative, closed |
| A26 | secondary := exp23 (fine-tuned seed314159) on the TTA stack, with exp03B primary | LB probe 13 (exp32) | **0.937, -0.007**: negative (beyond noise), dropped; +3.9% nodes; untested with the pilkwang primary (queued low) |
| A27 | primary := weight soup 0.5 pilkwang + 0.5 exp03B (`soup03B_50/`) on the exp29 config | LB probe 17 (exp35) | **0.943, -0.004**: no gain, interpolates between 0.947 and 0.944; closed |
| A28 | axis-flip TTA group (8 training-consistent flips instead of rot90/transpose) | friend B local port, 4 videos, 2026-09-15 | +0.025 on pilkwang with flat node count, but +0.0007 on a primary that never saw the videos -> 97% memorised views; closed, no LB probe ; REOPENED 2026-09-15 17:00 on 12 videos: +0.0214 on pilkwang AND +0.0187 on a scratch primary that never saw 44b6 (memorised views = 13-19%, not the mechanism); node count flat -> live candidate, exp37 kernel built ; LB probe 19 (exp37) = 0.946: tie, closed as a gain |
| A29 | detection threshold 0.965 -> 0.99 on the public stack (caassicca v5, public notebook) | public LB 2026-09-15 | **0.942 (-0.005)**: raising the threshold to cut nodes loses; node-budget lever is not a threshold (B19 closed) |
| A20 | GAP_CLOSE_UM 5.0 -> 6.5 | LB probe 8 (exp24) | 0.944, -0.001: noise; gap closing already saturated in the public pipeline |
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
| P1 | B3 (was 17) | dense pseudo-labels (teacher = exp03B + seed314159 ensemble on all 199 videos + GT) used to FINE-TUNE pilkwang primary (friend A) and secondary (friend B) - 1200 it runs, honest check by the exp11 scheme (6bba-only fine-tune -> 44b6 vs sparse fine-tune 0.8825); scratch-on-dense demoted to research (revised 2026-09-10) | friend B: teacher + dense set + secondary; friend A: primary | teacher ~4 h; each fine-tune ~1 h | dense beats sparse fine-tune by >= 0.005 on 44b6 -> all-183 fine-tune -> one LB probe on the TTA base  CAVEAT 2026-09-13 (Lê Quang Cảnh, rank 39, official scorer): dense-label fine-tune of head only = -0.003, of the encoder with the linker frozen = -0.038; only a JOINT fine-tune whose dense set includes teacher EDGES keeps the linker consistent with the moved encoder |
| P2 | B3b | temporal filtering of the teacher labels: keep points where primary and secondary agree within 3-5 um, persist >= 3 frames, fwd/bwd mutual match; keep teacher_score/disagreement; pseudo-edges from stable tracklets only after that (review 2026-09-10) | friend B (after the first dense fine-tune result) | CPU on cached teacher predictions | dense-filtered beats dense-raw on 44b6 |
| CLOSED | B25 | learned peak pruning / "refine" head on the detector output (hengck23: -13.1% peaks at 99.45% recall of annotated nodes, localisation 1.18 -> 0.97 vox). For OUR metric this is the node-budget lever, worth ~+0.012 via the adjusted-Jaccard factor if recall on annotated nodes holds; thresholding alone was flat (probe 4, local 0.93-0.985) so it must be a learned second-stage score (features: peak prob, local contrast, distance to nearest stronger peak, primary/secondary agreement). Validate on hold12 with the official metric: node ratio down, edge TP unchanged | Vitalii (CPU features) / friend A (if a small net) | 2-3 days | official metric, then 1 LB probe  REFERENCE COST of blind pruning (friend B, NMS kernel 6 um = (5,5,5)): -7.9% nodes, recall 0.9936 -> 0.9764, score -0.026; so a learned head must hold recall >= 0.99 on annotated nodes or it is worse than doing nothing  STATUS 2026-09-15 (friend B, 4 videos): peak_prob kept as a node attribute (graph-identical, saturated: min 0.965, median 0.999); LOO logistic pruner on raw-graph features (peak_prob, nearest-stronger-peak distance, crowding, degrees, component length, depth), labels positive-vs-unknown; pruning 5/10/13/20% of the lowest-scored raw nodes -> official score -0.0008/+0.0041/-0.0024/-0.0147 vs 0.9082, recall after post-processing 0.9920 at 10%. Peak +0.004 = half the formula ceiling and = LB noise: promising, not a go. 12-video run queued behind his calibration. The two strong features are ones the pipeline already exploits; beyond ~5-10% needs a feature the pipeline lacks (image-based)  ITERATION 2 (2026-09-15 13:07): zhincez size-not-brightness image features added to the pruner change recall-at-cut by nothing (0.9924/0.9817/0.9709/0.9495 vs 0.9924/0.9827/0.9725/0.9506). Reason, obvious in hindsight: annotated and unannotated nuclei are the same objects, so appearance cannot separate them; the pruner can only remove NON-nuclei, which the graph features already find. CEILING = the detector's false-peak fraction. Size feature moves to B20. 12-video run in progress  CLOSED 2026-09-15 15:00 on 12 videos: negative at every fraction (5% -0.0023 ... 13% -0.0078), recall gate failed; pruned nodes sit inside tracks so the node bonus never beats the edge loss; the free node budget is already taken by prune-isolated + short-track filter |
| DONE (partial) | B26 | FALSIFICATION TEST of the "memorised views" explanation (friend B §13.5): run the public stack on the 12 LOEO-44b6 videos with PRIMARY := friend_a_exp02_loeo20 (never saw 44b6) twice, public TTA vs Z-flip TTA, and compare the delta with the same pair on the pilkwang primary (+0.059 on CLEAN). Delta halves or flips -> confirmed: every local TTA measurement on pilkwang-initialised models is biased upward and local TTA screening is closed for good. ~25 min GPU on friend B's port | friend B | 1 h | local only (that is the point)  RESULT 2026-09-15 (4 videos): Z-flip delta +0.0171 on pilkwang vs +0.0098 on the scratch 6bba-only primary = 43% memorised (short of the pre-registered "halves"); the axis-flip group: +0.0250 vs +0.0007 = 97% memorised. Verdict: local TTA gains on pilkwang models are mostly memorised views; the residual +0.010 on unseen 44b6 for Z-flip still contradicts the LB, so embryo difference is a second cause. Local TTA screening closed |
| P1 | B4 | friend A's all-199 scratch model (dense labels if B3 ready, else sparse with official-metric early stopping every 5 epochs) as SECONDARY in the blend | friend A -> Vitalii | 1-2 days on 5070 Ti + 1 probe | beats pilkwang secondary on LOEO 44b6 |
| CLOSED 2026-09-21 | B5 (was 18) | honest LOEO win (+0.0073 on the 6bba-only scratch model) but on the public stack per-video AdaBN inflates raw nodes 1.1-2.0x on 8/12 videos and the guarded variant loses 0.0066 (exp38 regression, friend A); not probed. Original row: | test-time adaptation of the primary detector on the test embryos (DARTH-style self-training + photometric consistency, EMA teacher, node-count guard) | Vitalii | ~1 day engineering; ~30 min GPU per embryo inside the submission kernel | LOEO: adapt on 44b6 images without labels, score on 44b6 GT >= +0.005 |
| P2 | B6 (was 7) | detector TTA / seed-ensemble as primary with dedup merge (exp03B + exp16 + pilkwang) | Vitalii | check how the public notebook runs inference first; +0.5 h | LOEO |
| DONE | B17 | full TTA stack from sjlee101 -> A23 (0.947 reproduced, adopted as base); its exp03B / Z-flip / exp23 add-ons -> A24-A26 (no gain / negative) | Vitalii | exp33 deconfound pending | - |
| DONE (negative) | B18 | weight soup primary: 0.5*pilkwang + 0.5*exp03B (same init, 1200-it fine-tune -> linear interpolation valid); halves the +3.2% node shift of exp03B; `soup03B_50/` uploaded 2026-09-11 | Vitalii | exp35 kernel pushed 09:55; 1 probe after exp33 scores | LB (one change on exp29)  -> probe 17 = 0.943 |
| P0 (2026-09-23 night) | B35 | DIVISIONS VIA DAUGHTER RECOVERY + STEAL + PAIR MODEL (line 3 of the 0.97 target): the B32 audit located the losses (30/151 second daughters undetected, 39/151 claimed by another parent). Step A: second detector pass (public primary, threshold 0.90, 20 um crop at t+1) around the top-3% DivNet-p parents, recovered nodes enter the graph only through an accepted division; gate reach 121 -> >= 135/151 at <= 0.3% extra nodes. Step B: pool = orphan | claimed | recovered within 15 um, DivNet-p prefilter + <= 8 candidates per parent, pair model (B32 design + current-edge features), 2 folds by embryo, pass 2 with edge replacement; gate +0.005 on 199 and per embryo, adj_edge within 0.002. Step C only if A fails: dense division labels fine-tune used solely in the local second pass. | friend A (GPU) + Vitalii (kernel 27 Sep) | A 24 Sep, B 26 Sep, probe 27 Sep | local OOF, then LB |
| P1 (2026-09-23) | B33 | POST-PROCESSING GRID ON ALL 199 VIDEOS, per-embryo readout (relink radius/bonus/off, linefit weight x window, DeepCenter gap/safe-div thresholds, gap params, short-track len/rescue, safe-div caps and gates, DivNet veto, edge max). Never done at this scale: LB probes 1-9 covered four knobs on the 0.941 base; friend B's 12 videos never swept relink or linefit, the two largest stages. Selection: >= +0.003 on 199 AND >= +0.002 on each embryo, nodes <= control + 0.5%. Forum (hikaggler, Justin CH123): post-proc settings chosen locally transfer. | friend A (CPU from raw cache) + Vitalii (3-5 probes/day via tools/build_probe_kernel.py) | 2 days grid, probes 24-27 Sep | local, then LB |
| P2 (2026-09-23) | B34 | APPEARANCE-AWARE LINKER (giorgosin trainer: real UNet features into SimpleNodeTransformer; the shipped fine-tune used geometry only), 2 folds by embryo through the port with the public detector, plus relink bonus 2.5 so the new probabilities reach the final edges. Gate +0.003 per embryo. Odds low (linker changes did not move hikaggler's LB; relink overrides ILP edges) but it is the only model-side defect found by anyone. | friend A (GPU) | 3-4 days, report 26 Sep | local, then LB |
| CLOSED 2026-09-22 (step 1 reach audit: orphan pool covers 58/151, detection ceiling 121/151, steal pool 97/151 at 16.3M triples) | B32 | DIVISION PAIR MODEL (the line we never ran): parent + both daughters scored together on a wide orphan pool (parent radius 15 um, sister 5-20 um, DeepCenter veto, NO divergence/symmetry gates), 4 image lags + 3 gaussian markers, UNet-GAP initialised from DivNet + geometry head, trained on the 151 GT divisions with 2 folds by embryo (6bba <-> 44b6), OOF p for all 199 videos, pass 2 from friend A's ckpt with tau {0.5,0.7,0.9} x caps {public, 2x, off}; nodes untouched by construction. Gate: score >= control + 0.005 on 199 AND on each embryo, adj_edge within 0.001. Why it can work where B20 failed: B20 scored the parent only (daughter choice unresolved, FP explosion on the 15 um pool); the metric gap to the top 10 is ~+0.02 in div_J alone | friend A (GPU) + Vitalii (kernel) | 4-5 days: report 24 Sep, probe 25-26, freeze 27 | local OOF, then ONE LB probe |
| CLOSED 2026-09-21 | B31 | NODE CLUSTERING instead of pruning - CLOSED AT STEP 1: the public peak extractor is a 3 um max-pool NMS, so no two raw nodes are closer than 3 um (0 of 4,211,780 on 199 videos); radii 0.5-2 um cannot merge anything, and the 6 um kernel was already -0.026 (friend B NMS sweep). Original row kept for the record: (hengck23 "cluster nodes, represent by centroid"; his `cluster_predicted_nodes` = greedy score-ordered duplicate suppression within a radius, keep the best-scored prediction): merges duplicate peaks of one nucleus so the track stays continuous while N_pred falls - the failure mode of B25 (pruned nodes inside tracks) does not apply to true duplicates. Post-processing class, measurable on friend B's port: radius 0.5/1.0/1.5 um per frame on the raw graph, readout node ratio + edge TP, gate +0.005 on 12 videos | friend C (CPU, Mac, from friend A's cache; prompt PROMPT_FRIEND_C.md 2026-09-20) | hours | local, then LB |
| DONE (tie) | B30 | AXIS-FLIP TTA GROUP as ONE probe: exp37 = exp29 config + rot90/transpose views replaced by the 8 axis flips (friend B's apply_axis_flip_tta verbatim). Local: +0.0214 on 12 videos, +0.0187 on an unseen-embryo scratch primary, edge +0.015, node count flat. Risk: embryo difference (sank Z-flip twice); difference from Z-flip: no added views, no node growth, and the removed views are ones training never produced. Kernel pushed 2026-09-15 evening; SUBMITTED 2026-09-15 14:42 UTC as probe 19, id 56256938, exactly once (monitor with duplicate guard); score expected 20:00-22:00 UTC; monitors are OFF at the user's request - read the scores on the next check | Vitalii | 35 min kernel + 1 probe | >= 0.950 adopt; 0.945-0.949 tie; <= 0.944 drop  -> LB 0.946 (-0.001): tie; the inference class does not transfer from the 12-video port even with an unseen-embryo control |
| CLOSED | B28 | LINEFIT SMOOTHING sweep (OUTPUT_LINEFIT_WEIGHT 0.8, WINDOW 2): per-stage table on 12 videos shows it is the LARGEST post-processing stage (+0.0145) and it was never swept nor probed. Post-processing class = locally measurable (port reproduces the LB order, Spearman +0.80). Weight x window grid on friend B's port, then ONE probe if a setting beats the base by >= 0.005 locally AND probe 18's local-vs-LB pair confirmed transfer | friend B (CPU) | hours | local, then LB  CLOSED 2026-09-15 17:30: the public (w0.8, win2) is the unimodal optimum on 12 videos, every deviation loses (off -0.0145 ... win3 -0.0008); the author tuned it, just never exposed it |
| BELOW GATE | B29 | MOTION RELINK OFF (and DeepCenter veto OFF) with the full stack: relink is net -0.0067 on 12 videos and is the stage that collapses 44b6_87bba6c4 (0.636 -> 0.511, FP edges 32 -> 53); veto -0.0035 (one division event). Same class and gate as B28. Caveat: the in-kernel sweep of the public notebook tuned relink radius, never OFF; the public author may have kept it for the hidden embryos | friend B (CPU) | hours | local, then LB  RESULT 2026-09-15 17:30: relink OFF 0.9054 = +0.0053 headline, but +0.0039 is ONE extra division TP and the edge term is +0.0014 (positive on 4/12); it repairs 87bba6c4 (0.535 -> 0.607); veto OFF +0.0024, again one division event. Neither clears +0.005 on the edge term; no probe. Open: the public author kept relink ON for the hidden embryos |
| DONE (tie) | B27 | division FP hygiene, two structurally safe filters bundled as ONE probe: (a) "already divided" - a fork whose ancestor already divided in the video keeps only its nearest child (0 of 151 GT divisions chain within a video, so it cannot remove a true one; local FP 13 -> 11, +0.0009), (b) sister-separation floor 5 um in safe-division (local FP 13 -> 11, +0.0012). Each below LB resolution; together maybe +0.002 and pure expected gain on the private 71%. Needs the user's go because post-proc probes were closed on 2026-09-08 | Vitalii | 1 kernel + 1 probe | LB >= 0.947 -> adopt into final 1; <= 0.944 -> drop  -> user said go 2026-09-15 evening; exp36 SUBMITTED 2026-09-15 13:44 UTC as probe 18, id 56252420, by the monitor; I then re-submitted the same file at 13:50 UTC (id 56252506) because the monitor had written its confirmation to a file instead of emitting an event and expired "with no events" - ONE SLOT WASTED (3 left today). LESSON: a monitor that performs an action must echo the result as an event, and before any manual re-submit check the submissions list first. Score expected 01:00-03:00 MSK; read it on the next check  FRIEND B LOCAL PREDICTION (12 videos, full stack): +0.0011, div FP 7 -> 4, TP unchanged, edge +0.0003 -> predicted LB 0.947-0.948 (tie, adopt); LB <= 0.944 would falsify "post-proc changes are locally measurable"  -> LB 0.946 (-0.001): tie, not adopted |
| DROPPED | B19 | det-threshold re-calibration for a fine-tuned primary on the TTA stack (0.965 -> 0.97/0.975) so N_pred matches pilkwang's; mechanism: adj = J*(1-0.1*(N_pred-N_est)/N_est), +3.2% nodes = -0.003 = exactly exp30's loss | Vitalii | 1 probe, only if exp33 >= 0.946 (weights not worse at equal node count). PRIOR IS WEAK: threshold 0.93-0.985 was flat locally and probe 4 (0.965 -> 0.95) was flat on the LB, so the node-count gain may cancel against lost detections | LB  -> exp33 = 0.944 < 0.946 gate, not run ; CONFIRMED by a public fork: det 0.99 = 0.942 (A29) |
| P1 | B20 | divisions = the only big untapped term. LOCAL SWEEP 2026-09-11, RE-SCORED WITH THE OFFICIAL METRIC (`tools/score_geffs_official.py`; 12 hold-out videos, 14 GT divisions, raw-ILP graphs): gate OFF 0.9469 (0/0/14) -> public tau 0.6 **0.9567** (3/13/11) -> tau 1.0 0.9553 (3/16/11) -> 1.4 0.9523 (3/22/11) -> 2.0 0.9517 (3/25/11). Under the official metric the public setting is the BEST tested and the response is monotone above it, so the gate thresholds are settled; the gate as a whole is worth +0.010 and its ceiling is a 4:1 FP:TP ratio. The lever is a division CLASSIFIER: the binding constraint is the RANKING (`parent_dist + 0.15*sister_dist` ascending picks the tightest pair = duplicate detections, and the ~5-slot per-frame budget is spent before a real division is reached), not the gates. Diagnosis: of 3 missed GT divisions all parents and daughters ARE detected; 1 daughter is an orphan with asymmetric geometry, 2 are claimed by a neighbouring track passing 0.8-1.7 um away | friend A/B (research) | resolve on the FULL 199-video train set (151 GT divisions); then a fork scorer that ranks on evidence | official metric div_J, then LB  IMAGE FEATURE (zhincez notebook, 2026-09-15): dividing nuclei get SMALLER, not dimmer - half-max volume vs paired same-frame controls is -0.27 at +3 frames and already below at -2/-1, while the peak holds; so the ranker feature is a temporal size profile, not mean intensity  CANDIDATE GATE NOTE (Lê, 2026-09-16): both daughter arcs are reachable by a 7 um gate in only 29% of cases, by 12 um in 86%, 15 um in 100% (n=7) - the second-daughter candidate gate must be ~2x the continuation gate; friend B's steal candidates should use up to 12-15 um for the second arc  SHORTCUT 2026-09-18: a PUBLIC trained division detector exists - `giorgosi/biohub-divnet-v2` (3D UNet-GAP on lags -1..+2 + centre marker, 4 folds by movie over all 199 videos / 151 divisions, OOF AUC 0.887, AUC vs confuser forks 0.92, simulated official div_J 0.214 top-1 / 0.226 top-2 vs our 0.11, "lb upside" 0.954-0.956 by the author's own simulation). Inference code vendored in `tools/divnet_infer.py`, dataset added to the fetcher manifest. Use it as the RANKER score for B20 candidates (the only public user, haideptry "0.948+", wastes it as a soft veto p<0.5) |
| P1 | B21 | MINIMUM sister separation in the safe-division gate. Base rates from the training labels (discussion 740573): real divisions have sister separation median 8.85 um (IQR 7.20-10.24), ordinary continuation steps 1.72 um, and duplicate detections sit near zero. The public gate has an UPPER bound (14 um) and NO lower bound, and its ranker `parent_dist + 0.15*sister_dist` ASCENDING actively prefers the close pairs = duplicates. A lower bound near the 25th percentile of real divisions (7.2 um) should cut false positives without touching true ones | Vitalii | offline sweep with `tools/sim_safediv.py --min-sister-um` (FP side has good statistics: 13 FP vs 3 TP on 12 videos), then 1 LB probe | official metric div_J |
| P1 | B22 | re-rank division candidates on EVIDENCE instead of geometry: sister separation (the only separating geometric quantity), parent peak intensity (AUC 0.73 at the split frame, daughters 0.68-0.70 at t+1..t+3; elongation is chance at our z spacing), learned edge score. This is B20's ranker, now with measured signals | friend A/B | needs the 199-video candidate dump | official metric div_J |
| P2 | B23 | ILP division weight 1.2 -> 0.1 or lower. The Ultrack reference zebrafish configs use division/appearance/disappearance penalties of 0.001-0.1, all balanced; our public lineage uses division 1.2, disappearance 2, appearance 0, at which a fork can reportedly never be optimal. Probe 3 only moved it 1.2 -> 0.9 (25%), not the one-to-three orders of magnitude the reference implies | Vitalii | check offline whether the ILP produces any fork at all, then 1 probe | LB |
| P3 | B24 | external Ultrack zebrafish volume at OUR exact voxel scale (1.625, 0.40625, 0.40625), 522 timepoints, public.czbiohub.org/royerlab/ultrack/zebrafish_embryo.ome.zarr - extra division examples and/or pretraining; Ultrack also ships pretrained node detectors unet-daxi.pt / unet-simview.pt. External public data is explicitly allowed | friend A/B | download + upload as a Kaggle dataset (kernels have no internet) | LOEO |
| P2 | B16 | edge-feature TTA (`BIOHUB_EDGE_FEATURE_TTA=1`, from the public 0.946/0.942 forks: average UNet features over the 8 TTA views before edge prediction) | Vitalii / friend B | inference-only patch, exists in `$TMP/pub/biohub-harmonic-fusion` cell 4; unmeasurable on LB at +-0.003 noise -> judge on the honest validator with friend B's port; adopt for the final if >= 0 there | LOEO |
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
- The public forks' in-kernel post-proc sweep (7 candidates selected on 8 leaky train videos, margin 0.001): noise-chasing; the 0.946 vs 0.942 of two identical notebooks proves it.
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
  #8 2026-09-07 10:12 exp24 (exp06 base, GAP_CLOSE_UM 6.5, validator off) = **0.944** (scored ~16:00; -0.001 = noise, dropped;
  gap radius stays 5.0).
  #9 2026-09-07 11:07 exp25 (exp06 base, OUTPUT_MIN_TRACK_LEN 8, validator off) = **0.944** (scored ~18:30; -0.001 = noise,
  dropped; min track len stays 6). POST-PROC PROBES CLOSED: 7 knobs, none >= +0.002; only weights moved the LB. 1 slot left today.
  #10 2026-09-07 23:58 exp27 (exp06 base, SECONDARY := friend_a_full199_ep21, validator off) = pending (id 56084358).
  = **0.920** (scored 2026-09-08 ~05:30; -0.025 vs 0.945, STRONGLY NEGATIVE, dropped).
  Diagnosis (tools/csv2geff.py + tools/score_geffs.py on the 4 dummy test videos = train videos, leaky but same for both):
  exp06 0.8961 vs exp27 0.8889 (-0.007) even on videos friend A's model trained on; on 6bba_05b6850b edge FP 16->26,
  FN 16->31, node recall 0.994->0.985. On unseen test embryos the gap grows to -0.025 => the 21-epoch scratch model is
  weaker than pilkwang's 50-epoch secondary and, blended at SECONDARY_DETECTION_WEIGHT 0.8, drags the blend down. A
  weaker model does not add "diversity", it adds its errors. Rule: a candidate secondary must first beat the pilkwang
  secondary RAW on the honest 6bba->44b6 split (friend A roadmap step 3) before any LB probe.
  #7 2026-09-07 03:08 exp22 (exp06 base, secondary weights := exp08, validator off) = **0.929** (scored ~09:00; -0.016 vs 0.945,
  STRONGLY NEGATIVE, dropped). Lesson: the blend needs a DIFFERENT model as secondary; exp08 is a fine-tune of the same
  pilkwang primary as exp03B (no diversity) and the public post-proc thresholds are tuned for the seed314159 model. 3 slots left today.
  Candidates after: det threshold 0.965->0.95; secondary := fine-tuned too (if #2 positive); SECONDARY_DETECTION_WEIGHT 0.8->0.5.
  #11 2026-09-10 16:28 exp30 (sjlee101 0.947 TTA stack + PRIMARY := exp03B, validator off = base pp config) = **0.944**
  (scored 2026-09-11 ~02:00; -0.003 vs #14, tie by the noise rule but NO gain: the +0.004 of the fine-tuned primary on the
  0.941 base does not carry over to the TTA stack; confounded by the sweep pick, see #15).
  #12 17:08 exp31 (exp30 + Z-flip views in both edge-feature TTA loops) = **0.941** (-0.003 vs exp30 = INSIDE the +-0.003 noise
  floor -> a TIE, not a proven negative; my first write-up said "negative, dropped" - corrected 2026-09-11 after the user's
  challenge. Tested only on top of the exp03B-primary/sweep-off base, never on exp29 itself -> re-test = #16 exp34).
  #13 17:34 exp32 (exp30 + SECONDARY := exp23) = **0.937** (-0.007 vs exp30; NEGATIVE, dropped: third secondary swap in a row
  that hurts - exp08 -0.016, friend A ep21 -0.025, exp23 -0.007; the seed314159 secondary + its tuned thresholds stay).
  #14 17:49 exp29 (sjlee101 verbatim, validator + sweep on -> tight55) = **0.947** (REPRODUCED the public score exactly ->
  the 0.947 is not a lucky run; exp29 = final candidate 1 as of 2026-09-11).
  #15 2026-09-11 09:15 exp33 (exp29 realised config incl. MOTION_RELINK_TIGHT_UM 5.5 + PRIMARY := exp03B, validator off) =
  pending (kernel pushed; submit when COMPLETE). Purpose: probe #11 differed from #14 in TWO things (primary weights AND the
  sweep pick tight55, proxy +0.002); exp33 isolates the weights. exp33 >= 0.949 -> fine-tuned primary composes after all;
  <= 0.947 -> fine-tuned weights do not compose with the TTA stack, final candidate 1 = exp29 as is.
  #16 2026-09-11 09:40 exp34 (exp29 realised config incl. tight55, pilkwang primary, + Z-flip views in both edge-feature TTA
  loops = 12 views) = **0.938** (-0.009 vs exp29: REAL NEGATIVE, beyond noise; Z-flip TTA is dropped for good - the -0.003 of exp31 was the same effect masked by noise). One change vs the submitted exp29. Rule: >= 0.950 real
  gain (adopt); 0.945-0.949 tie (keep the 8-view public group); <= 0.944 negative.
  #15 (exp33, exp29 config + PRIMARY := exp03B, one change) = **0.944** (-0.003 vs exp29 = exactly probe 11's number again:
  the fine-tuned primary does NOT compose with the TTA stack; the lever "fine-tuned weights +0.004" existed only on the
  0.941 pipeline).
  #17 (exp35, exp29 config + PRIMARY := soup03B_50, 0.5 pilkwang + 0.5 exp03B) = **0.943** (-0.004: the soup sits where the
  interpolation predicts, between 0.947 and 0.944 - no free lunch from the node-count mechanism).
  VERDICT 2026-09-12 (scored overnight): all three probes negative or null. exp29 (public sjlee101 stack, 0.947) stays
  the base and FINAL SUBMISSION 1 as is. Fine-tuned-primary family closed on the LB (probes 11, 15, 17); Z-flip closed
  (12, 16); secondary swaps closed (7, 10, 13). 17 probes total; 5 slots/day unused today because nothing mechanism-backed
  is left on the inference side. Slots today: 5.
  RE-EXAMINATION of #11-#13 (2026-09-11, after the user's challenge) with the kernel outputs (run_stats + submission.csv scored
  with tools/csv2geff.py + tools/score_geffs.py on the 4 dummy test videos = train copies, leaky but identical for all):
    exp29 raw nodes 125305, leaky local 0.8932 | exp30 129340 (+3.2%), 0.8936 | exp31 130220 (+3.9%), 0.9034 | exp32 130146 (+3.9%), 0.8969.
    (a) MECHANISM for exp30/32/31 losing on the LB: all three put 3-4% MORE nodes than exp29 through the same det threshold
    0.965 (the fine-tuned models are more confident; the extra TTA views too). The metric's node-count factor rewards fewer
    nodes than the estimate (local ratio on 44b6_0b24845f -0.368 -> -0.245, adj 0.976 -> 0.964 with identical edges), so on
    unseen embryos the surplus nodes eat the bonus. Cheap, mechanism-driven follow-up if exp33 <= 0.947: re-calibrate the det
    threshold for the fine-tuned primary (0.965 -> 0.97/0.975) so its node count matches pilkwang's, ONE probe.
    (b) The leaky local set ranks exp31 first (+0.010 over exp30, edge FP 116 -> 106, FN 86 -> 73 on 6bba_05db0fb1) while the
    LB ranks it last-but-one: the same local-vs-LB contradiction as before (the 4 videos are training videos of exp03B/exp23).
    Local numbers on these videos are NOT evidence for the LB in either direction.
    (c) exp32 stays dropped for now: -0.007 is beyond the noise floor and it is the 4th secondary swap in a row that hurts; but
    it was tested with exp03B as primary (both fine-tuned with the same recipe on the same 183 videos -> correlated errors).
    exp23 as secondary with the PILKWANG primary is untested; queued behind exp34 (only if exp34/exp33 leave slots idle).

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
- NOISE FLOOR (2026-09-08 15:40, from two byte-identical public notebooks scoring 0.946 and 0.942): a single run of
  this pipeline family varies by ~+-0.003 on the public LB (GPU non-determinism through 8-view TTA + ILP). Consequences:
  (1) probe deltas < 0.005 are NOT decisions - this includes exp03B primary (+0.004, kept as base because it is also
  principled, but unproven); (2) a calibration probe = re-run exp06 unchanged (exp28) measures OUR run-to-run variance
  and is worth one slot; (3) never pick finals by the max public score over many runs.
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
<!-- friend-a-exp02-loeo20-result -->
- 2026-09-09 Friend A STEP 1 complete: 20-epoch scratch 6bba->44b6 official best 0.6803 (epoch_020, edge 0.6809, recall 0.8531, N_pred/N_est 0.998); delta20-15 +0.0031; decision `STEP_4_dense_labels_sparse_limit`; weights `friend_a_exp02_loeo20/`, no LB submission.
<!-- friend-a-step1b-result -->
- 2026-09-10 Friend A STEP 1b complete: epoch-20 scored on a fixed seed-42 sample of 12 own 6bba training videos: official score 0.8332, edge 0.8455, node recall 0.9361, N_pred/N_est 1.169 (vs LOEO-44b6 0.6803/0.8531/0.998). Mixed diagnosis: a substantial 6bba->44b6 domain shift plus residual sparse-label/calibration limitations; proceed to the fixed dense STEP 4 without recipe changes. Smoke 2/2 passed; no LB submission.
Pending right now:
- LB probe #4 = kernel `vitaliineibauer/biohub-exp19-pub941-det095` v1 (public pipeline, det 0.95) = 0.940, scored 22:40 MSK
  (neutral, dropped). Check: `python -m kaggle competitions submissions biohub-cell-tracking-during-development`.
- LB probe #5 = kernel `vitaliineibauer/biohub-exp20-ft03b-secdet05` v1 (exp06 base + SECONDARY_DETECTION_WEIGHT 0.5,
  validator off) = 0.943, scored 2026-09-07 00:15 MSK (negative, dropped). Next slots ~03:00 MSK 2026-09-07.
- LB probe #7 (exp22, secondary := exp08, id 56065255) = 0.929 (-0.016, dropped). Probe #6 (exp21, min track len 4,
  id 56065251) = 0.943 (-0.002, dropped). exp25 = min track len 8 built and pushed ~10:05 as probe #9 candidate. 3 daily slots left.
- exp24 = exp06 base + BIOHUB_GAP_CLOSE_UM 5.0 -> 6.5 (direction probe) kernel `vitaliineibauer/biohub-exp24-ft03b-gap65`
  pushed 2026-09-07 ~09:20 MSK; probe #8 = 0.944 (noise, dropped). exp25 (min len 8) = probe #9 = 0.944 (noise, dropped).
  Post-proc probes are CLOSED (§10a A-list); next LB probes only for model-side changes after a friend-B/LOEO check.
- exp23 (user "запускай" 11:40): kernel `vitaliineibauer/biohub-exp23-ft-secondary` v1 pushed 11:45 MSK = fine-tune the
  pilkwang seed314159 SECONDARY with the exp03B recipe (1200 it, batch 8, lr 5e-5, BCE, seed 42); also measures the raw
  seed314159 model on hold12 (A) vs fine-tuned (B), leaky sanity only. ~50 min. When COMPLETE: `kaggle kernels output
  vitaliineibauer/biohub-exp23-ft-secondary -p <dir>` -> `ft_weights/unet_transformer/split_0/{edge_predictor_best.pth,config.json}`
  -> `weights_dataset/exp23/` -> `kaggle datasets version -p weights_dataset --dir-mode zip -m "exp23"` -> tell friend B
  (TEAM.md, friend B step 2). NO LB probe until friend B's check (>= +0.003 as secondary in the full pipeline).
  DONE 13:00 MSK: exp23 hold12 raw 0.9469 -> fine-tuned 0.9551 (leaky sanity, +0.008 like exp03B); weights uploaded to the
  dataset as `exp23/` (verified). Waiting for friend B's honest check; results in experiments/exp23_ft_secondary/results/.
- Team timing (user 13:10 MSK 2026-09-07): friend A's 30-epoch 6bba run is at epoch 13, ~45 min/epoch -> finishes ~02:00
  MSK 2026-09-08 (official scores every 5 epochs expected in his branch). 17:15: friend A (Ваня, Sasyami) sees no gain in
  the last epochs and will stop ~20:00 if no improvement. Stop rule agreed: judge by the OFFICIAL metric on the 12 44b6
  videos at checkpoints 10/15/20/25 (not the training-log recall) + N_pred/N_est per checkpoint; continue only if 25 beats
  20 by >= 0.005; keep the best checkpoint -> dataset `friend_a_exp02/` + RESULTS row. A plateau at 15-20 epochs is the
  expected sparse-GT behaviour: next gain comes from data (dense teacher labels, all 199 videos), not epochs.
- Work split for model experiments (friend A, 18:00): the UNet detector can be trained on ANY GPU and plugged into the joint
  training with `train_unet_transformer.py --unet-weights <pth>` (linker then trained/fine-tuned on top). So detector
  experiments (§10a B3 dense labels, B7 ignore-unlabelled loss, B5 test-time adaptation) run in parallel on Kaggle (Vitalii,
  ~1 h/epoch on T4, a few epochs per run) and on friend A's GPU; only the full 199-video 30+ epoch joint run stays with
  friend A. Every detector result = UNet weights file + official score on the 12 44b6 videos after a linker fine-tune.
- 22:10 friend A pushed (merged into main): `friend-a-full199-scratch-30ep.ipynb` (root) = from-scratch joint training on all
  199 videos, 30 epochs, cosine lr 1e-4 -> 1e-5, batch 4, seed 42, checkpoints every 5 epochs, leaky 12-video monitor;
  shared `experiments/_lib/train_patches.py` now has `--max-detections` (caps local maxima per frame before the O(N^2)
  transformer, GT-near peaks protected; set 0 for dense labels), `--lr-schedule/--min-lr`, `--checkpoint-every`, bounded
  zarr/blosc threads. Verified: 26 patches still apply + compile on the base script (Kaggle kernels unaffected). Waiting
  for the 6bba run's official scores at 10/15/20 before he starts the 199-video run (~70 min/epoch, ~1.5 days).
  CORRECTION 22:50: the run friend A had going all day WAS the all-199 from-scratch run (45 min/epoch); it crashed after
  epoch 21 (host RAM -> the zarr fix). Best-by-leaky-monitor checkpoint uploaded to the dataset as `friend_a_full199_ep21/`
  (config identical to ours: 32/32-64-128, ds 1,4,4, window 2, NMS 5). He resumes 21 -> 30 overnight (root
  `friend-a-full199-resume-ep21-to30.ipynb`, ~7-8 h, cosine 2.85e-5 -> 1e-5, checkpoint every epoch). No honest local
  score is possible for a full-199 model (it saw 44b6); the only test is the LB. Probe folder READY (not pushed):
  `experiments/exp27_ft03B_sec-friendA21` = exp06 base + SECONDARY := friend_a_full199_ep21 (§10a B4). Awaiting the
  user's go: GIVEN 23:15 -> probe #10 = 0.920 (-0.025, dropped). No more blind probes of friend A's all-199 checkpoints (ep30 included)
- 2026-09-10 16:00 NEW PUBLIC BASE CANDIDATE (research/discussions_summary.md "Update 2026-09-10"): sjlee101/biohub-lf-dctta-v020
  = public 0.947 in ONE run: Harmonic Fusion + DeepCenter TTA (8-view averaging of the veto model) + secondary edge-feature TTA
  (weight 0.75) + DC safe-div threshold 0.20. Inference-only, no model change -> composes with exp03B. Kernels pushed 15:50 MSK:
  exp29 = verbatim (validator+sweep on, ~70 min) to reproduce 0.947; exp30 = + PRIMARY_OVERRIDE exp03B, validator off (~30 min).
  Submit both when COMPLETE (probes #11, #12; 5 slots today). Decision: exp30 >= 0.948 -> exp30 becomes the new base for the
  final (all later probes on it); exp30 <= exp29 -> the fine-tuned primary does not compose with the TTA stack, keep whichever
  is higher as final candidate 1. Remember the +-0.003 run-to-run noise: treat < 0.005 differences as ties.
  Other new notebooks: 0.942-0.944 knob combos (nothing new), rayk's harmonic-mean edge fusion 0.915 (rejected).
  LESSON (user question 16:30): we missed the TTA stack ourselves because (1) detection TTA already existed in the base and I
  treated TTA as "done" (queued only seed-ensembles, B6); (2) I lumped inference-compute changes with post-proc knobs when
  closing the knob probes; (3) after the noise-floor finding I parked edge-feature TTA as "unmeasurable" while three stacked
  TTA steps gave +0.006 together. Rule going forward: any inference stage that still sees ONE view (linker features,
  secondary features, DeepCenter, ILP inputs) is a cheap, LB-transferable candidate - check those before any heuristic.
  Hardware is not the reason: TTA runs inside the Kaggle kernel; the 5070/5070 Ti stay on training.
- AUDIT of past conclusions (user 2026-09-10 17:00, "re-examine your results"):
  STILL VALID: (1) post-proc KNOB probes are flat - all 6 single knobs were <= 0 (none positive to stack), and the public
  knob-combo forks (busyaprime/evgendvorkin/hanklin) also sit at 0.942; (2) exp08 as secondary -0.016 and friend A ep21 as
  secondary -0.025 are far outside noise; (3) clean pipeline 0.899 vs public 0.941; (4) linker gains do not transfer (7th
  place confirms). WRONG/INCOMPLETE: (a) I closed "inference" together with "knobs" - TTA is extra compute, not a threshold,
  and it stacks: 3 TTA stages = +0.006 public; (b) queue item 7 (TTA, from the survey, day 1) was never executed because
  the base "already had TTA" - I never enumerated which stages were single-view; (c) "unmeasurable at +-0.003" is not a
  reason to skip a principled step - stack several and measure the stack; (d) exp23 (fine-tuned secondary, the second step
  of the fine-tune stack) has been idle 3 days waiting for a local check that is not coming. NEW STACK CANDIDATES found by
  enumerating single-view stages against the TRAINING augmentation (augmentations.py flips Z, Y and X independently; the
  public TTA uses only in-plane XY views): Z-flip TTA views for primary + secondary edge features (exp31, built);
  exp23 as secondary on the TTA stack (exp32, built). Later: rot90/transpose views are NOT in the training distribution -
  a training-consistent 8-axis-flip TTA group could replace them (exp33 candidate).
  PROBE PLAN 2026-09-10/11 (5 slots/day): #11 exp29, #12 exp30, then #13 exp31 (Z-flip) and #14 exp32 (secondary exp23)
  on whichever of exp29/exp30 is the better base; kernels pushed as GPU slots free (max 2 concurrent).
  #11 SUBMITTED 2026-09-10 16:28 MSK: exp30 (id 56145113, pending). exp31 (Z-flip) kernel pushed 16:30; exp29 still running.
  #12 SUBMITTED 2026-09-10 17:08 MSK: exp31 = exp30 + Z-flip TTA views (id 56145851, pending). exp32 (secondary := exp23)
  kernel pushed 17:08; exp29 (verbatim, validator on) still running. 3 slots left today.
  #13 SUBMITTED 2026-09-10 17:34 MSK: exp32 = exp30 + SECONDARY := exp23 (id 56146281, pending). 2 slots left; exp29 still running.
  #14 SUBMITTED 2026-09-10 17:49 MSK: exp29 = sjlee101 verbatim, validator + sweep on (id 56146538, pending). 1 slot left today.
  Scoring takes 5.5-7 h -> all four expected between 22:00 and 01:00 MSK.
  exp29 kernel output (experiments/exp29_sjlee947_verbatim/results/, big files ignored): the in-kernel sweep on 8 leaky train
  videos scored base proxy 0.9490 and SELECTED `tight55` (MOTION_RELINK_TIGHT_UM 5.5, proxy 0.9511, +0.002); all other
  candidates within +-0.0001 of base, `relaxed9` -0.001. So probe #14's submission = sjlee stack + relink 5.5, whereas
  sjlee's own 0.947 run may have selected something else -> another source of run-to-run spread. Our exp30-32 runs have
  the sweep off (base config).
- 21:30 friend B's tasks re-cut (TEAM.md + PROMPT_FRIEND_B.md): the TTA variants I already probed (exp29-32) become the
  CALIBRATION set for his local port (does local ranking match LB?); his next variants = secondary edge-TTA weight 0.5/1.0,
  DeepCenter threshold 0.15/0.25, Z-flip in DeepCenter TTA, axis-flip TTA group. Teacher/dense set only if friend A's pipeline
  has not uploaded `teacher_geff/`/`train_dense_geff/` (dataset check 21:20: not there yet). exp23 is not a valid sparse
  reference for his LOEO comparison (it saw 44b6); he runs the 6bba-only sparse fine-tune himself.
- 21:35 friend A merged: his dense pipeline is redirected to PRIMARY fine-tunes (step1c teacher -> step2 variants -> step3 winner
  on 183 videos), matching TEAM.md; the teacher is not in the dataset yet.
  Prompts for the friends' assistants now live in the repo: PROMPT_FRIEND_A.md, PROMPT_FRIEND_B.md (keep them current).
- 2026-09-10 23:30 REVIEW of the dense fine-tune (external summary via the user) - checked against the code:
  Linker loss (`compute_loss`): mask = rows with a GT child | columns with a GT parent; softmax over dim 0; BCE-focal on the
  masked block. Targets are mapped from GT nodes onto DETECTIONS via `build_matched_edge_targets` (unmatched detections ->
  target 0). VERDICT: the reviewer's reading of the mask is correct, the conclusion is not. A teacher node has no edges, so
  its row/column is inactive; it only appears as a 0-target column inside a GT parent's row - but the SAME nucleus already
  appears there as an unmatched detection in sparse-GT training (target 0 as well). Dense labels therefore change NOTHING in
  the edge supervision; they only add detection positives. No hidden "linker degradation" mechanism; the running dense
  baseline is a valid A/B and needs no provenance masking for correctness. (Only division daughters that are unannotated are
  wrongly negative - identical in both regimes.)
  Still worth an A/B, as an experiment not a fix: two-stage "dense detector -> sparse linker recalibration". Implemented as
  optional flags in `experiments/_lib/train_patches.py` (defaults unchanged, 33 patches apply + compile): `--edge-loss-weight`
  (0 = detector-only) and `--freeze {linker,detector}` (optimizer over trainable params only). Recipe: stage A
  `--init-weights <pilkwang> --freeze linker --edge-loss-weight 0 --max-iters 1200` on train_dense; stage B
  `--init-weights <stageA> --freeze detector --max-iters 600` on the sparse train dir. Added as friend A variant (e).
  Other review points: temporal filtering of pseudo-labels (primary/secondary agreement 3-5 um, >= 3-frame persistence,
  fwd/bwd mutual match, keep teacher_score) - AGREE, queued as B3b (friend B/A after the first dense result); pseudo-EDGES
  from stable tracklets - only after B3b; nnPU / masked-unknown detection loss = B7 (already queued, after the dense result);
  softer intensity aug / background subtraction for the 6bba->44b6 shift - AGREE, variant (d) already uses `--aug-intensity`
  with the old ranges -> friend A should halve the ranges (gain 0.8-1.25, offset +-0.1, gamma 0.8-1.25, no haze) - note added;
  window-3 was not a Trackastra-style multi-frame LINKER test - AGREE (the transformer still links t->t+1 pairs), but
  error decomposition says detection + fragmentation dominate, wrong association ~0, so a multi-frame linker stays P3;
  parent-offset head for divisions = B8 (queued).
- TEAM PLANS REVISED 18:00 (TEAM.md): dense labels now feed 1-hour FINE-TUNES of pilkwang (A: primary, B: secondary), honest
  check by the exp11 scheme; scratch 30-epoch runs and their LB probes are stopped. Friend B's local port gains priority as the
  place to compare TTA-stack variants without LB slots.
- 2026-09-10 18:30 friend A merged (branch): STEP 1b = the 20-epoch 6bba scratch model scores **0.833** on 12 of its own
  training videos (recall 0.936, N/N_est 1.17) vs 0.680 on unseen 44b6 -> the 6bba->44b6 EMBRYO SHIFT (+0.15) dominates;
  the sparse-label limit is secondary. Consequences: (1) models must see both embryos (fine-tunes on all 183 do; scratch on
  6bba never will) - supports the revised fine-tune route; (2) cross-embryo robustness ideas move up: `--aug-intensity` /
  scale augmentation as a fine-tune variant, and test-time adaptation on the test embryos (§10a B5, Vitalii); (3) the test
  set = two further unseen embryos, so LB gaps between our models are largely shift, not capacity.
  He also delivered a resumable dense pipeline (`friend-a-dense-pipeline.ipynb`, `tools/build_dense_gt.py`, teacher step,
  atomic checkpoints) written for the OLD plan (scratch dense 20 ep -> all-199 scratch if >= 0.70). Asked to redirect its
  STEP 4 to the revised plan: `--init-weights` pilkwang primary, `--max-iters 1200 --lr 5e-5` (keep teacher + builder as is).
- 2026-09-09 16:30 FRIEND A STEP 1 DONE (branch merged; `experiments/local_friend_a_exp02_loeo_scratch_20ep/`, dataset
  `friend_a_exp02_loeo20/`): scratch on 126 6bba -> official metric on 12 unseen 44b6 videos, cosine 1e-4 -> 1e-5:
  ep5 0.6635 (node recall 0.877, N/N_est 0.99) | ep10 0.5547 (recall 0.687, N/N_est 0.82 - mid-run instability) |
  ep15 0.6772 (0.866, 1.01) | ep20 0.6803 (0.853, 1.00). References on the same videos: pilkwang primary 0.8807,
  secondary 0.8691 (both leaky). Divisions 0/15 at every checkpoint. Stop rule hit (20-15 = +0.003).
  READING: the curve is flat from epoch 5; node recall on the unseen embryo caps at ~0.85-0.88 while N_pred matches N_est,
  i.e. the detector finds the right NUMBER of nuclei but not the annotated ones (faint/hard nuclei) -> sparse-GT limit
  and/or 6bba->44b6 shift. Decision (his + ours): STEP 4 dense labels; no more sparse-GT epochs. Validator gate (0.85)
  NOT reached, so the honest validator is still not usable for fine comparisons; it IS usable for the big question
  "dense vs sparse" (delta expected >> 0.02). Also uploaded: `friend_a_full199_ep30/` (resume 21 -> 31 done; leaky
  monitor only; NOT probed per the probe-10 rule).
  Cheap diagnostic asked of friend A (STEP 1b, ~20 min GPU): score the ep20 model with the official metric on 12 of its
  own TRAIN 6bba videos. ~0.9 there => the gap is embryo shift / over-fit to 6bba; ~0.7 there => under-fit / sparse-label
  limit. Either way dense labels are next, but the answer decides whether STEP 4 must also include cross-embryo
  augmentation (intensity/scale) or not.
  CRITICAL PATH = teacher detections (friend B STEP 1). If friend B has not started by tonight, Vitalii runs the teacher
  for the 126 6bba videos on Kaggle (exp03B + seed314159 ensemble, det 0.965, no ILP; ~1.5 GPU-h of the ~5.5 h left).
- 2026-09-08 15:40 discussion/notebook re-read (research/discussions_summary.md "Update 2026-09-08"): public 0.946 is the
  same 0.941 pipeline; two identical copies score 0.946 and 0.942 -> LB noise +-0.003 per run. Plan changes: (1) exp28 =
  exp06 re-run unchanged as a CALIBRATION probe (folder built, not pushed; 25 min + 1 slot, user's go needed); (2) edge-feature
  TTA added to §10a as B16, judged locally, not on LB; (3) FINAL-SUBMISSION RULE: sub 1 = exp06-family config, sub 2 = the
  config that is best on the honest validator (friend A/B), never the max-over-runs public score; public notebooks are LB-tuned
  and a private shake-up against them is likely (Yubo: 0.946 public notebook is 0.015 worse on 5-fold CV than his 0.942).
- 2026-09-08 07:30: TEAM.md now holds self-contained step lists for BOTH friends (A: sparse 6bba validator -> recipe changes;
  B: teacher detections -> dense geff set `train_dense/` -> dense 6bba run on the 5070 -> local port). Split of GPU work: the
  sparse-vs-dense comparison runs in parallel on the two cards; the winner is retrained on all 199 by friend A and probed once
  as secondary (blend weight 0.5 first). Plumbing verified: predict script works without --use-ilp (nodes only), the trainer
  reads GT from `<stem>.geff` next to `<stem>.zarr` (io.py from_geff) so a dense-label dataset is just another data dir.
  until the honest 6bba->44b6 raw comparison exists. Leaky-but-useful local check for any full-pipeline kernel: the kernel's
  interactive run writes submission.csv for the 4 dummy test videos (train copies) -> `python tools/csv2geff.py <csv> <dir>`
  -> `python tools/score_geffs.py <dir>`; exp06 = 0.8961 on them (reference). Friend B joins ~21:00 MSK today -> the local
  port is realistically tomorrow; exp23's check therefore cannot come from him today. Option on the table: exp26 = exp06
  notebook with validator ON + secondary := exp23 on hold12 (~60 min GPU). DECLINED by the user (13:20): wait for friend B's
  local check, do NOT spend GPU on exp26. Nothing else to launch today; remaining work = log probes #8/#9 when scored. After probe #6: if min len 4 is
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
  (4) Schedule (user check 2026-09-09; final deadline 29 Sep 23:59 UTC): recipe experiments until 24 Sep; STEP 5 all-199
  retrain of the winner starts by 24 Sep; second seed by 26 Sep; from 26 Sep only final-submission probes; 28-29 Sep pick
  the two finals = best LB config + one conservative (honest-validator) variant.
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
- 2026-09-11 09:15 MSK PROBES 11-14 SCORED (all COMPLETE ~02:00): exp29 verbatim **0.947** (reproduced), exp30 (+exp03B
  primary) **0.944**, exp31 (+Z-flip) **0.941**, exp32 (+exp23 secondary) **0.937**. Decision per the rule of 2026-09-10 16:00:
  exp30 <= exp29 -> the fine-tuned primary does not compose with the TTA stack; FINAL CANDIDATE 1 = exp29 (sjlee stack as is,
  in-kernel sweep on). Both stack add-ons are negative and dropped. The two proven levers of the 0.941 base (fine-tuned
  primary +0.004, TTA +0.006) are NOT additive: the TTA stack already captures what the fine-tune fixed.
  Caveat on probe 11: exp30 ran with the sweep OFF (base pp config) while exp29's sweep picked tight55 (proxy +0.002), so
  probe 11 = two changes. Deconfound probe #15 = exp33 (`experiments/exp33_sjlee947_tight55_ft03B`: exp29 config +
  MOTION_RELINK_TIGHT_UM 5.5 hard-coded + PRIMARY := exp03B, validator off) - kernel pushed 09:15, ~30 min; SUBMIT WHEN
  COMPLETE -> SUBMITTED 2026-09-11 09:35 MSK as probe #15 (id 56160334, pending; 4 slots left). Rule: >= 0.949 -> weights compose, exp33 becomes candidate 1 and friend A's primary
  fine-tunes stay on track; <= 0.947 -> weights do not compose; the value of friend A's/B's fine-tunes then rests on the
  honest validator + final candidate 2 only, and further LB probes go to inference-side changes on exp29 (friend B's
  variants: secondary edge-TTA weight 0.5/1.0, DC threshold 0.15/0.25, axis-flip group) and to test-time adaptation (B5).
  Slots: 5 available today (11 Sep, reset 03:00 MSK); 1 used by exp33 when submitted. exp28 (exp06 re-run) stays unpushed:
  exp29 reproducing 0.947 exactly already answers the run-to-run question for this base.
  Friend B's calibration set now has LB numbers: exp29 0.947 > exp30 0.944 > exp31 0.941 > exp32 0.937 (spread 0.010,
  ranking is the test of his local port). TEAM.md / PROMPT_FRIEND_B.md updated with the numbers.
- 2026-09-11 09:40 MSK user challenge "re-examine exp31/exp32, maybe dropped wrongly like the TTA stack was": done, see §11
  #12/#16 and the RE-EXAMINATION block. Corrections: exp31 was a TIE by my own noise rule (I had written "negative");
  the Z-flip is dimensionally right (imgs (B,W,Z,Y,X), -3 = Z; training flip_augment flips Z/Y/X independently) and the
  kernel log confirms 12 views. Probe #16 = exp34 (`experiments/exp34_sjlee947_tight55_zflip`: exp29 config + tight55 +
  Z-flip, pilkwang primary) pushed 09:40, ~35 min; SUBMIT WHEN COMPLETE (monitor bp39sezlx). exp33 submitted (#15). After both: 3 slots left today.
  Mechanism found in the kernel stats: every losing variant put 3-4% more nodes through det 0.965 than exp29 -> node-count
  bonus shrinks; det threshold re-calibration for the fine-tuned primary is the next mechanism-driven probe if exp33 <= 0.947.
  Lesson (again): write "tie" when the delta is inside the noise floor; a tie on a confounded base is not a verdict.
- 2026-09-11 09:55 MSK "what other knobs" pass (user request). Inference/model-side ideas NOT yet tried on the exp29 base, ranked:
  (1) B18 weight soup primary -> exp35 pushed (submit after exp33; both are "one change vs exp29"); (2) B19 det-threshold
  re-calibration for the fine-tuned primary (node-count mechanism, quantified: adj factor 1-0.1*dN/N, exp30's +3.2% nodes
  = -0.003 = its whole loss); (3) friend B's inference variants (secondary edge-TTA weight 0.5/1.0, DC safe-div threshold
  0.15/0.25, Z-flip in DC TTA, axis-flip group) - LB-tuned by the author, low expected value; (4) B20 divisions = the
  only big untapped term but not a knob (diagnosis above). Checked and rejected: linker window TTA (W=2, stride 1: every
  pair is scored exactly once, no alternative context); temporal reversal TTA (not in training aug); the unused env
  switches of the notebook (SINGLE_CHILD_REPAIR, DIVISION_GEOMETRY_FILTER, VELOCITY_WEIGHT, RETENTION 0.90) are
  post-proc knobs = noise-level class, closed. Kernel exp35 runs; exp34 (Z-flip) runs; exp33 scoring (id 56160334).
  Dataset biohub-ft-weights now has 7 weight folders (friend_a_* preserved; local mirror ignored by git).
- 2026-09-11 10:30 MSK DIVISION KNOBS SWEPT LOCALLY AND CLOSED (new tool `tools/sim_safediv.py`: re-implements the
  notebook's safe-division gate offline - existing-child/parent/sister radii, mutual NN, divergence, symmetry, caps,
  ranking - applies it to prediction geffs and scores with the official metric; no DeepCenter veto offline, so it
  over-adds and is only valid for COMPARING settings). Run on the 12 hold-out videos of exp23 (A_pretrained arm, raw
  ILP graphs, 14 GT divisions):
    gate OFF 0.9469 (div 0/0/14) | tau 0.3 0.9515 (1/6/13) | 0.45 0.9550 (2/9/12) | 0.6 (public) 0.9567 (3/13/11) |
    0.8 0.9550 (3/17/11) | 1.0 0.9591 (4/15/10) | 1.4 0.9554 (4/21/10) | 2.0 0.9545 (4/24/10)
    parent radius 7.5 -> 0.9573, 10.5 -> 0.9567 (at tau 0.6); divergence 1.0 -> 0.9577, 3.0 -> 0.9547 (at tau 0.8).
  VERDICT: the response is JAGGED, not unimodal (0.8 sits BELOW 0.6, then 1.0 jumps above it) because 14 GT divisions
  quantise the metric: one recovered division = +-0.004 score / +-0.03 div_J, and the full observed spread is 2 events.
  No division threshold is resolvable on this set -> division knobs join the closed post-proc class; no LB probe.
  What IS solid and new: the gate as a whole is worth +0.010, and its ceiling is the 4:1 FP:TP ratio -> the remaining
  value is a division CLASSIFIER (B20), and any future knob claim must be sweept on all 199 videos (151 GT divisions).
  CORRECTION to my own interim message to the user 10:10: I called the tau response "unimodal with a peak at 1.0" after
  seeing only 5 points; the fuller sweep shows it is single-event noise. Same error class as the exp31 "negative" call:
  state the resolution of the evidence before ranking configurations.
- 2026-09-11 14:00 MSK **OUR LOCAL METRIC WAS THE WRONG ONE** (found while reading new public notebooks; verified against
  the organisers' source, not taken on trust). `tools/repo/` is pilkwang's support-pack fork, and its
  `division_metrics.py` credits a GT division to ANY predicted fork merely REACHABLE in the same weakly connected component
  (`div_candidates |= visited & pred_div_nodes`). The official metric, metrics.md at
  github.com/royerlab/kaggle-cell-tracking-competition (linked from the competition's Evaluation page), says in as many
  words "Merely sharing a weakly connected component is not sufficient" and requires a local parent anchor plus two
  distinct daughter branches. Edge-side code is IDENTICAL between the two (io.py and img_proc.py byte-for-byte), so only
  the division term was affected - but score = adj_edge + 0.1*div_J, so every local score with division TPs was inflated.
  MEASURED IMPACT on today's own sweep (same graphs, two metrics): at the public tau 0.6 both agree (3 TP), at tau 1.0 the
  fork says 4 TP / 0.9591 and the official says 3 TP / 0.9553. The fork's extra TP REVERSED the ranking: tau 1.0 looked
  like an improvement over the public setting and is actually worse than it. My 10:30 conclusion ("jagged, unresolvable")
  is superseded: under the official metric the curve is clean and the public 0.6 is the best tested value.
  FIXED: `tools/official/` = verbatim copy of the organisers' package `tracking_cellmot` (metrics, division_metrics, io,
  img_proc, models, scripts/evaluate.py); `tools/score_geffs.py` now scores with it (old behaviour kept as
  `tools/score_geffs_fork.py`, deprecated header); `tools/sim_safediv.py` switched over. ALL LOCAL NUMBERS WITH DIVISION
  TPs PREDATING THIS ARE SUSPECT - in particular friend A's LOEO rows that reported division TPs (e.g. "div 1/31/14").
  Rows where div was 0/0/N are unaffected, which is most of ours.
  Context for the leaderboard: a public notebook (megayak, "The 0.966 Notebooks Used A Patched Metric Bug") reports that
  the July public notebooks scoring 0.963-0.966 - their titles literally say "metric hack" - wired one hub node at
  t=-1000 to every track root plus a chain of fake forks, which satisfied the old weakly-connected-component rule for
  every division at once and drove div_J to ~1.0. Patched 2026-07-17 (commit aa65e90). Their claim about those notebooks
  is THEIRS and unverified by us; what we verified independently is the metric difference above. Today's leaderboard
  leaders (0.970 / 0.966 with submissions hours old) are scoring under the current metric, so their scores are real.
- 2026-09-11 13:35 MSK leaderboard read: we are **160 / 3372** at 0.947 (silver), team D: Discipline. The 0.947 plateau is
  the public-notebook crowd (ranks ~150 to well past 169 all at 0.947), so +0.001 = about 110 places: 0.948 -> ~rank 46,
  0.949 -> ~rank 40, 0.950 -> ~rank 33, 0.953 -> ~rank 19. Top: 0.970, then 0.966, 0.966, 0.964, 0.963. 19 days to go.
  Public LB = 29% of test, so that plateau will scramble on the private split - all the more reason for final submission 2
  to be the honest-validator pick rather than a second public-LB config.
- 2026-09-11 14:20 MSK FRIEND B's INFERENCE VARIANTS ARE ALREADY ANSWERED by the notebook's own author. sjlee101
  published his own single-knob forks of the 0.947 stack and their public scores are visible:
    biohub-lf-dctta020-sectta1 (secondary edge-feature TTA weight 0.75 -> 1.0) = 0.947
    biohub-lf-dctta025-sectta1 (DeepCenter safe-div threshold 0.20 -> 0.25, with sectta1) = 0.947
    biohub-lf-dctta020-sectta1-sister16 (sister radius 14 -> 16) = 0.947
    biohub-lf-dctta-v015 (DeepCenter safe-div threshold 0.20 -> 0.15) = 0.946
  All ties with the 0.947 base. That is 3 of the 4 variants I had queued for friend B (weights 0.5/1.0, thresholds
  0.15/0.25) plus a sister-radius one, settled at zero cost to us. Only the axis-flip TTA group (replacing rot90 and
  transpose by the training-consistent 8 axis flips) remains untested, and our own exp34 already tests the Z-flip half
  of that idea. CONSEQUENCE: friend B's STEP 4 variant list is cut to the axis-flip group only; his calibration step
  (reproduce exp29/30/31/32 locally) and the 199-video division sweep become his main work, and the division RANKER
  becomes the team's highest-value research item. Lesson for probe planning: check whether the notebook's author has
  already forked the knob before spending a slot or a friend's GPU day on it.
- 2026-09-11 15:10 MSK DISCUSSION TAB RE-READ (research/discussions_summary.md "Update 2026-09-11"). The division threads
  are the valuable ones and they independently confirm our own diagnosis with hard base rates measured on the training
  LABELS (no model): division parent-to-daughter step median 4.57 um (IQR 3.30-6.21) sits entirely inside the ordinary
  continuation range (median 1.72, p99 6.91), so any parent-distance gate admits 24-38 continuations per division. The
  ONE separating quantity is sister separation: median 8.85 um for real divisions against 1.72 for continuations.
  => NEW QUEUE ITEMS B21-B24 (above). B21 is the actionable one: the public gate bounds sister separation from ABOVE
  (14 um) and not from below, and its ranker sorts by `parent_dist + 0.15*sister_dist` ASCENDING, which prefers the
  tightest pair - i.e. duplicate detections - over a real division. Offline sweep of a lower bound running now.
  Also logged: a trap (gates tuned on PREDICTED positions calibrate detector error, not motion - labels say max 7.37 um
  where predicted says 13.65 um on the same 7 events); the appearance signal is real but moderate (parent peak intensity
  AUC 0.73, elongation is chance at our z spacing); Ultrack's reference ILP event weights are 0.001-0.1 where ours is
  1.2 (B23); an external Ultrack volume exists at our EXACT voxel scale (B24).
  Two threads confirm our transfer findings from above us on the leaderboard: Mark (10th) "any smarter motion linker
  results in an increase of exactly 0.001" while local CV moves 0.01-0.03, and Yubo WANG measured +0.012 CV -> +0.001 LB
  plus the public 0.946 notebook scoring 0.015 WORSE than his own 0.942 on the same 5-fold CV. Community consensus is a
  large private shake-up (739570); the post-processing plateau thread (740103) has zero answers. Nothing here changes the
  final-submission plan: one best-public-config, one honest-validator config.
  Benchmark for our division term: hikaggler measured div_J ~ 0.22 by ablation at LB 0.929 (confounded, see summary);
  ours is 0.111 on 12 hold-out videos with the official metric, so the term plausibly has room to roughly double.
- 2026-09-11 16:00 MSK **DIVISION BASE RATES AND GATE FUNNEL MEASURED ON OUR OWN 199 TRAINING VIDEOS** (151 GT
  divisions), ground truth only, no model. Two new tools: `tools/division_base_rates.py` and
  `tools/division_gate_funnel.py`. This supersedes the forum numbers (they came from 73 files / 36 divisions).
    continuation step   n=128581  median 1.817  p25 0.908  p75 2.725  p90 4.143  p99 8.367
    division step       n=302     median 5.745  p25 4.001  p75 7.355  p90 9.066  p99 12.842
    sister separation   n=151     median 10.570 p25 8.006  p75 12.682 p90 14.357 p99 17.135
  CUMULATIVE survival of the 151 real divisions through the public safe-division gate stack, best case on GT
  geometry (a model can only do worse):
    start 151 -> existing-child <=10um: 150 -> parent <=9um: 121 -> sister <=14um: 114
    -> divergence (gc_dist - sister >= 2.25): 61 -> symmetry <=0.6: **35 of 151 = 23.2%**
  Individually: divergence rejects 75 (49.7%), symmetry rejects 57 (37.7%), parent radius 30 (19.9%), sister upper
  bound 19 (12.6%). So the shipped gate stack throws away three quarters of all real divisions BEFORE any ranking.
  (This reproduces exactly the "35 reachable" figure claimed in the public metric-bug notebook, which is a useful
  independent check on that source.)
  THE ALTERNATIVE STACK: drop symmetry and divergence, add a LOWER bound on sister separation (the public gate has
  only an upper bound at 14um). Reachable real divisions: min_sister 0 -> 114, 5 -> 109, 6 -> 103, 7 -> 92, i.e.
  about 3x the current ceiling of 35. And the floor is cheap in precision: only 6.2% of ordinary continuation steps
  exceed 5um and 3.5% exceed 6um, so it removes the duplicate-detection pairs that currently eat the per-frame
  budget of ~5 acceptances.
  First empirical check (12 hold-out videos, official metric, public tau 0.6 kept): min_sister 5 gives 0.9579
  (3 TP / 11 FP) against 0.9567 (3 TP / 13 FP) at min_sister 0 - right direction, small because the symmetry gate
  is still discarding most divisions. The decisive runs (gates open + floor, and a ranker that prefers LARGE sister
  separation instead of the public `parent_dist + 0.15*sister_dist` ascending) are running; `tools/sim_safediv.py`
  now has `--no-divergence`, `--min-sister-um` and `--rank-mode public|sister|balanced`.
- 2026-09-12 09:00 MSK PROBES 15-17 SCORED (see §11): exp33 0.944, exp34 0.938, exp35 0.943 -> exp29 stays base and
  final 1; fine-tuned primaries, Z-flip and secondary swaps are all closed on the LB. LOCAL DIVISION SWEEPS FINISHED
  (12 videos, official metric): public gates + sister floor 5um 0.9579 (3 TP/11 FP) vs public 0.9567 (3/13) = one FP,
  inside single-event noise; floors 6/7/8 lose a TP; gates OPEN + floor + public ranker 0.9523/0.9495/0.9543 (27-29 FP);
  sister-first ranker 0.9475 (1 TP). VERDICT: "reachable" (109 of 151 on GT geometry) is not "recovered" - without a
  learned ranker the FP explosion and the ~5-per-frame budget dominate, so the division gate stays at the public
  setting; B20 (learned fork ranker) is the only route left to the division term and is a research project, not a knob.
  Literature/forum sweep (workflow wf_4466359e-bb8) was PAUSED by the user to save tokens - do not resume it; the
  discussion digest of 2026-09-11 and the base-rate tools are what we have. Doc-audit workflow wf_08b2e86f-7e2 died
  with the session; its job (keep TEAM/prompts consistent) was done by hand in this commit.
  PLAN NOW: (1) no more LB probes until something new exists; (2) final 1 = exp29 verbatim (already submitted as
  probe 14, id 56146538); (3) final 2 = best config on the HONEST validator (LOEO, official metric via
  tools/score_geffs.py) - candidates come from friend A's primary fine-tunes and friend B's dense/sparse secondary
  fine-tune; (4) if any friend takes B20, the go/no-go is div_J on all 199 videos with the official metric before
  one LB probe; (5) freeze 24 Sep unchanged.- 2026-09-13 14:30 MSK CODE + DISCUSSION SCAN (browser; details in research/discussions_summary.md "Update 2026-09-13").
  (1) Leaderboard: 355 / 3494 at 0.947 (was 160 / 3372 on the 11th); nothing public above 0.947 (sjlee101 hoctveto-div-b
  0.947, harmonic-fusion v30 0.947; everything above the 0.947 group in the score-sorted list is still the July
  metric-hack set). (2) Lê Quang Cảnh (rank 39) posted controlled official-scorer numbers that RE-CUT friend A's dense
  fine-tune plan: detection head only -0.003, encoder with frozen linker -0.038 => variant (e) two-stage freeze-linker
  is dropped (it is the measured-harmful case), head-only is a sanity check only, and the joint fine-tune is kept ONLY
  with teacher EDGES in the dense set so the linker co-adapts. Annotation bias is real (dz -0.57 um, embryo-dependent)
  but a constant correction loses 0.003; contested links are lost on appearance AND motion (velocity picks the truth
  0/381) => linker work stays closed. (3) hengck23's refine head (-13% peaks at 99.45% recall) is the node-budget lever
  we quantified on the 11th => queued as B25, the most concrete new item. (4) Browser stopped after these reads to save
  the user's tokens; no probes spent (0/5 today).- 2026-09-15 DATA LAYOUT DECISION (user request "store the dataset in the repo, DVC or Hydra").
  What the user downloaded (`archive.zip`, 54 MB) is the TEAM WEIGHTS dataset `vitaliineibauer/biohub-ft-weights`, not the
  competition data; every file in it is byte-identical to `weights_dataset/` in the repo. Done: the whole weights dataset
  is now tracked in git, including friend A's three checkpoints that were git-ignored before (repo +25 MB), so `git pull`
  is the fast way to get all weights; the Kaggle dataset stays as the copy the notebooks read (no internet in kernels).
  Publishing a new version from the same folder keeps every subfolder. `params.yaml` at the repo root is the single
  place for paths, dataset slugs, the base recipe's knobs and the LB rules (plain YAML: DVC- and Hydra-readable).
  COMPETITION DATA STAYS OUT OF GIT: the local copy is 82 GB (199 train + test zarr videos). GitHub refuses files over
  100 MB and repos of a few GB; Git LFS free tier is 1 GB; a DVC remote would need 82 GB of storage plus bandwidth for
  three people (Google Drive free 15 GB, Yandex Disk free 5-10 GB), which is slower and dearer than one Kaggle download
  per person, and inside Kaggle kernels the data is mounted anyway. DVC/Hydra are therefore NOT set up now; the trigger
  for DVC would be a team artefact over ~1 GB that Kaggle cannot hold (e.g. teacher/dense geff sets), and it needs the
  user to choose and authorise a remote first.
  Third-party packs (pilkwang support pack, seed314159, DeepCenter - the ones the user means by "other participants'
  datasets, ~900 MB") stay on Kaggle too: `tools/get_kaggle_datasets.py` is the manifest + fetcher into git-ignored
  `external/` (skip-if-present). Pointers in git, bytes fetched once - DVC's mechanism without needing a remote.- 2026-09-15 FRIEND B MERGED (17 commits, branch `friend-b`, journal `CONTEXT_FRIEND_B.md`, port `tools/public_local.py`,
  driver `experiments/local_friend_b_exp02_public_port/`). What he established, all with the official metric:
  (1) The local port of the 0.947 stack executes the notebook's own cells with only the I/O replaced; it is byte-
  deterministic run-to-run (two independent inference runs identical to 6 decimals), so LOCAL deltas are never run
  noise - the +-0.003 floor is an LB-only phenomenon. Raw edge Jaccard 0.8588 matches exp11's 0.8585 independently.
  (2) The LOEO-44b6 calibration set is HALF-LEAKY for our fine-tunes: exp03B and exp23 were trained on the 183 videos
  of holdout_split.json, which contain 6 of the 12 LOEO-44b6 videos (12dfb391, 2a2eff9f, a21120c2, c50204e0, d2f34f90,
  d5e7d891). Verdicts must be read on the CLEAN 6. Consequence for FINAL SUBMISSION 2: any honest validator for
  exp03B-lineage or friend A's 183-video fine-tunes must exclude those 6 videos (or use a 6bba-only holdout).
  (3) Weight leakage explains exp30/exp32 but NOT exp31: with the same exp03B primary, Z-flip TTA gives +0.059 on CLEAN
  locally vs -0.003 on the LB (and our clean re-test exp34 = -0.009). His explanation: pilkwang trained on all 199
  videos WITH random Z/Y/X flips, so averaging over that group on training embryos averages memorised views (node
  recall 0.9994 vs 0.9936), while on unseen embryos it only blurs the map and adds nodes. => LOEO-44b6 is NOT a valid
  bench for ranking inference variants on pilkwang-initialised models (weights swaps or TTA); it IS valid for
  post-processing knobs and for from-scratch 6bba models. This is the mechanism behind our "linker/TTA gains do not
  transfer" pattern. Falsification test queued as B26 (cheap, decisive).
  (4) Post-processing contributes +0.031 on 4 videos (raw ILP 0.8763 -> 0.9076); the whole TTA stack barely moves the
  raw edge Jaccard - its LB value appears only through post-processing, i.e. through better DETECTIONS feeding motion
  relink. Same conclusion as ours: detections and node budget are the levers, linking is not.
  (5) pool_kernel_um 3/4/5 all map to a (3,3,3) kernel (odd-rounding) - hypothesis refuted, not a knob. Rounding node
  coordinates as the submission writer does is worth +0.0006 locally (scorer inputs must be rounded to match the LB).
  (6) STEP 3 (secondary fine-tune) is blocked by disk on his machine; given probe 13 (exp23 secondary -0.007) it is
  demoted to a final-2 candidate only. His remaining STEP 4 variant (axis-flip TTA group) is measured but read with
  an asymmetric rule: a local loss is believable, a local gain is not (the bias only creates false wins).
  His tools tweak (score_geffs*: a .geff store is a directory, check the suffix before globbing) is merged.
  NEXT FOR HIM (written into TEAM/PROMPT): B26 falsification test; then B25 on his port (learned peak pruning, the
  node-budget lever, comparable locally per his own table); STEP 3 only if disk frees up.
- 2026-09-15 12:30 FRIEND B: B26 DONE, AXIS-FLIP VARIANT CLOSED (4 videos, official metric; details CONTEXT_FRIEND_B.md
  §20-22, rows in RESULTS.md). B26: the Z-flip TTA delta is +0.0171 on the pilkwang primary and +0.0098 on the scratch
  6bba-only primary (never saw 44b6) - a 43% drop, short of his pre-registered 'halves' criterion, so partial support
  only. The decisive test came from the axis-flip variant itself: +0.0250 on pilkwang, **+0.0007 on the scratch
  primary** (recall even drops), i.e. ~97% of the local gain is memorised views. One explanation covers both: Z-flip
  ADDS four views (extra smoothing helps a weak model regardless of which views), axis-flip REPLACES four (no extra
  smoothing, residual zero) -> on unseen data the composition of the TTA group does not matter; it matters locally only
  because the model remembers the frames. Consequences: (a) axis-flip closed, no LB probe; (b) any TTA-group change on
  pilkwang models is unmeasurable on LOEO-44b6 - now shown by direct test, not argument; the only honest local bench
  for such variants is a from-scratch primary, on which the variant must win by itself. Also closed: NMS kernel
  (3.0-5.5 um are one (3,3,3) kernel; 6.0 -> (5,5,5) costs 0.026 at 97.6% recall = the bound for B25's selectivity).
  Next: 12-video calibration running (Kaggle rate limit lifted 12:25), then B25 on the port (design in his §19:
  PU labels, ceiling +0.008..0.010 from the node-count term, recall >= 99% as go/no-go).- 2026-09-15 evening FRIEND B MERGED AGAIN (12 commits): B26 partial (43% of the local Z-flip gain is memorised views,
  residual +0.010 on unseen 44b6 still contradicts the LB -> embryo shift is a second cause); axis-flip group CLOSED
  (97% memorised, A28); B25 first pass: learned pruner peaks at +0.004 for 10% pruning on 4 videos with recall 0.992
  after post-processing - half the formula ceiling, equal to LB noise, 12-video run queued. Team reading: the node-budget
  lever exists but the raw-graph features are already exploited by the pipeline; a bigger cut needs an image feature.
  No LB probe requested or planned from any of this. His own §14 note above is the primary record.- 2026-09-15 evening DISCUSSION + CODE SCAN (research/discussions_summary.md "Update 2026-09-15 evening"): nothing
  public above 0.947. One reusable finding: a dividing nucleus gets SMALLER, not dimmer (half-max volume -0.27 at +3
  frames vs paired controls, peak intensity holds) - the image feature for B20/B25, written into friend B's prompt.
  Zebrahub external data is confirmed allowed; the public Ultrack embryo may be a separate validation embryo (open
  question in thread 741386). HOCT-veto public stack has a 10 h deadline risk - not our stack, no action.- 2026-09-15 late CODE SCAN BY CONTENT (user: "maybe their code improves ours even at equal score"): 13 new notebooks
  pulled and diffed against exp29 (details in research/discussions_summary.md). Outcome: A29 det threshold 0.99 = 0.942
  (B19 closed for good), B27 division-FP hygiene candidate (already-divided filter from pawanmali, GT-proved safe, +0.0009
  local; plus our sister floor +0.0012), a stage-resume mechanism worth copying only if we ever change the kernel, nothing
  else. Awaiting the user's go/no-go on spending one slot on B27.- 2026-09-15 late USER GO on B27: exp36 = exp29 realised config + (a) already-divided fork filter + (b) sister floor 5 um,
  one probe. Kernel pushed; the monitor submits automatically on COMPLETE as probe 18 and wakes on the score (expected
  6-8 h). Reading rule: >= 0.947 -> adopt both filters into final 1 (expected private-LB gain, zero structural risk);
  0.945-0.946 -> tie, keep exp29 verbatim; <= 0.944 -> drop. Slots today after this: 4.- 2026-09-15 night FRIEND B MERGED (6 commits): all 12 LOEO videos local (competition endpoint rate-limits to 0.1 MB/s;
  he bundled the missing six through a private CPU kernel, 3.1 GB in 4 min - reusable trick). exp29 on 12 videos, official
  metric: raw ILP 0.8740 -> post-processed 0.9001 (+0.026); reproduces the 87bba6c4 collapse (0.535, 50 FP); same-set
  cross-check vs exp11: the whole inference stack changes RAW edges by -0.0025, i.e. TTA/dual-seed/fusion do not improve
  linking at all, only the detections that post-processing consumes. B25 iteration 2: image size features add nothing to
  the pruner (annotated and unannotated nuclei are the same objects); ceiling = false-peak fraction; the size feature
  belongs to B20. 12-video calibration and B25 chain running on his machine.
- 2026-09-15 14:30 FRIEND B: 12-VIDEO CALIBRATION DONE (CONTEXT_FRIEND_B.md §28, RESULTS row). ALL 12, official metric:
  exp29 0.9001 > exp31 0.8975 > exp30 0.8867 > exp32 0.8760 vs LB 0.947 > 0.944 > 0.941 > 0.937: Spearman +0.80, the only
  inversion is exp30/exp31 whose LB gap (0.003) is the noise floor; exp29 first and exp32 last as on the LB; stable under
  leave-one-video-out (exp29 first in 10/12); the division term does not change the order; spread 0.024 = 2.4x the LB's.
  PORT CALIBRATED (order yes, magnitude no). CORRECTION to his §10 / our §14 entry of this morning: the CLEAN/LEAKY split
  came out the OPPOSITE of the leakage prediction - exp03B configs beat exp29 on 4 of 6 clean videos and 1 of 6 leaky ones
  - so fine-tune leakage (real as a fact) does NOT drive local rankings; per-video weight-swap swings of -0.037..+0.039
  against a 0.003 LB effect do, and the two heaviest videos (893/773 GT edges) go against exp03B ('worse on dense videos').
  Consequence: the 'honest validator must exclude those 6 videos' rule is withdrawn; weight swaps are unresolvable in
  MAGNITUDE on any 12-video set (>= 48 videos, as we already said), while the ORDER is reproduced. The TTA-memorisation
  finding stands - it rests on the scratch-model tests, not on the split. Next from his chain: B25 on 12 videos, local
  prediction for probe 18 (exp36) before its LB score, per-stage table for the 87bba6c4 collapse.
- 2026-09-15 15:00 FRIEND B: B25 CLOSED on 12 videos (CONTEXT_FRIEND_B.md §29). Learned pruner, official metric, ALL 12:
  every fraction is negative (5% -0.0023, 8% -0.0036, 10% -0.0020, 12% -0.0062, 13% -0.0078) and recall after
  post-processing at 10% is 0.9826, below the 0.99 gate; the 4-video +0.004 was one over-budget video. Mechanism: even a
  5% cut that keeps 99.6% of annotated nodes loses edges (0.8756 -> 0.8702) because pruned nodes sit inside tracks, so
  the node bonus never beats the edge loss. The free part of the node budget is already taken by prune-isolated and the
  short-track filter. Not a threshold, not a probe. Remaining from his chain: local prediction for probe 18 (exp36),
  per-stage table for the 87bba6c4 collapse, then B26 + axis-flip on 12 videos with pilkwang and scratch primaries.
- 2026-09-15 15:05 FRIEND B: LOCAL PREDICTION FOR PROBE 18 (exp36), written before its LB score: on the 12 LOEO videos with
  the full stack (DeepCenter veto on), exp36's post-processing on the exp29 raw graphs scores 0.9004 vs 0.8993 for
  exp29/tight55 = +0.0011, division 1/7/14 -> 1/4/14 (TP unchanged, 3 FP removed), edge +0.0003. Pre-registered as
  +0.001 +-0.0005 and met. Predicted LB: 0.947-0.948 (tie -> adopt). A LB <= 0.944 would falsify the port's claim that
  post-processing changes are locally measurable - that pair is the real test. B25 closed (see 15:00). Remaining: per-stage
  table for 87bba6c4, then B26 + axis-flip on 12 videos with pilkwang and scratch primaries.
- 2026-09-15 15:30 FRIEND B: PER-STAGE TABLE of the public post-processing on 12 videos (CONTEXT_FRIEND_B.md §31, RESULTS
  row, results/stage_table_exp29_12videos.log). Cumulative: edge filter 0.8740 -> +relink 0.8673 (-0.0067) -> +gap 0.8802
  (+0.0130) -> +divisions 0.8886 (+0.0084) -> +veto 0.8851 (-0.0035, one division event) -> +short-track 0.8856 -> +LINEFIT
  0.9001 (+0.0145). Two things we did not know: (1) linefit smoothing (OUTPUT_LINEFIT_WEIGHT 0.8, WINDOW 2) is the single
  largest post-processing stage and is in no sweep key and no probe; (2) motion relink is net NEGATIVE on 12 videos and is
  the stage that collapses 44b6_87bba6c4 (0.636 -> 0.511, FP edges 32 -> 53, never recovered) - the exp02 mystery. Both are
  post-processing-class comparisons, i.e. the locally measurable class. Queued (CPU, behind his GPU chain): relink OFF with
  the full stack, veto OFF, and a linefit weight x window grid. If relink-off or a linefit setting wins on 12 videos, it
  is a candidate in the same class as exp36 - to be read against probe 18's local-vs-LB pair first.
- 2026-09-15 17:00 FRIEND B: B26 + AXIS-FLIP ON 12 VIDEOS - his 4-video closure of the axis-flip group is RETRACTED
  (CONTEXT_FRIEND_B.md §32, RESULTS row). Same TTA change on two primaries: axis-flip +0.0214 on pilkwang (0.9001 ->
  0.9215, edge +0.015, div 1/6/14 -> 2/7/13, raw node count flat) and +0.0187 on the scratch 6bba-only primary that never
  saw a 44b6 video; Z-flip +0.0108 vs +0.0088. So 81-87% of local TTA gains survive on unseen 44b6 videos: memorised views
  are a 13-19% effect, not the mechanism (the 4-video +0.0007 was a small-sample artefact, same error class as the CLEAN
  rule). What sank Z-flip on the LB (exp31 -0.003, exp34 -0.009) must then be embryo difference (+7% nodes for exp31),
  which no local test can see. Axis-flip is therefore a live inference-class candidate (+0.021 on ALL 12, positive on most
  videos, no node growth, same cost) with one untestable risk - the same one that hit exp31/exp34 twice. He does not ask
  for a probe; the class has no confirmed local-vs-LB pair yet (probe 18 gives the first pair, for post-processing).
  Side finding: on both primaries REPLACING rot90/transpose beats ADDING Z-flips, so the rotated views are harmful, not
  neutral. A28 status should read 'reopened on 12 videos'. B28/B29 CPU sweep running next.- 2026-09-15 evening FRIEND B MERGED (3 commits): B26 + axis-flip on 12 videos RETRACT his 4-video closure - 81-87% of local
  TTA gains survive on a scratch primary that never saw the test embryo, memorised views are a 13-19% effect. Axis-flip
  is a live inference candidate (+0.021 local, node count flat, same cost); Z-flip's LB losses must be embryo difference.
  I built and pushed exp37 (B30) so the user can decide on the slot with the kernel already done; friend B himself did
  not ask for a probe (no local-vs-LB pair in the inference class yet). B20 blocked on disk (82 GB for 199 videos), he
  designed an in-kernel feature table instead; B28/B29 CPU sweep running.
  neutral. A28 status should read 'reopened on 12 videos'. B28/B29 CPU sweep running next.
- 2026-09-15 17:30 FRIEND B: B28 CLOSED, B29 BELOW THE GATE (CONTEXT_FRIEND_B.md §34, RESULTS row, results/
  b29_relink_veto_pervideo.txt). Linefit grid on 12 videos: the public (w0.8, win2) is the unimodal optimum, every
  deviation loses (off -0.0145 ... win3 -0.0008) - the author tuned it, just never exposed it. relink OFF with the full
  stack: 0.9054 = +0.0053 on the headline, but +0.0039 of that is ONE extra division TP (2/8/13) and the edge
  term moves +0.0014, positive on 4/12 videos; it does repair 87bba6c4 (0.535 -> 0.607). veto OFF +0.0024,
  again one division event. Neither clears the +0.005 gate on the robust (edge) term; no probe requested. Open question
  no local test answers: the public author kept relink ON for the hidden embryos and swept its radius, never OFF.
- 2026-09-15 18:30 FRIEND B: B20 STEP (b) DONE - size profile on OUR labels (CONTEXT_FRIEND_B.md §37, RESULTS row,
  results/b20_size_profile_12videos.txt). With same-frame DETECTION controls (GT controls unusable in 44b6: 4/15
  divisions had >= 3), zhincez's post-split shrinkage reproduces: daughter half-max volume -0.17/-0.20/-0.20 at lags
  0/+1/+2 with CIs excluding zero (his -0.27 at +3; ours fades by +3). His PRE-split claim (-2/-1) is not seen at n=14
  (fraction below control 0.50). The relative peak (+0.2..+0.4 at every lag) is annotation bias, not a signal. Ranker
  feature for B20 is therefore daughter size at +1/+2 vs the frame's detection median, available at ranking time; its
  power against false forks cannot be measured on 12 videos (~5 reachable positives) - it needs the 199-video in-kernel
  feature table he designed (§33). B28 closed, B29 below the gate, B26/axis-flip done on 12: his queue is empty until
  probes 18 and 19 score; probe 19's kernel was verified to produce the same predict script as his local axisflip run.
  no local test answers: the public author kept relink ON for the hidden embryos and swept its radius, never OFF.- 2026-09-15 22:00 MSK PLAN RE-CUT (user asked whether friend B's plan and the team plan need correcting). 14 days left,
  freeze 24 Sep. Everything knob-shaped is closed on both sides (LB: weights, TTA-add, secondary, post-proc, threshold;
  local: pruner, linefit, relink/veto). What is left is decided by tonight's two probes:
  PROBE 19 (axis-flip) >= 0.950 -> the inference class TRANSFERS and friend B's port is a valid screen for it: he screens
    the same training-consistent group in the DeepCenter TTA and the secondary-only/primary-only ablations (CPU-cheap on
    cached graphs where possible), Vitalii probes at most one follow-up; final 1 = exp29 + axis-flip (+ hygiene if probe
    18 >= 0.947). PROBE 19 <= 0.944 -> the inference class does NOT transfer even with an unseen-embryo local test;
    the port stays a post-processing instrument only; final 1 = exp29 (+ hygiene if probe 18 >= 0.947).
  INDEPENDENT OF THE PROBES, friend B's main line from tomorrow is B20 (division ranker) via his in-kernel feature table:
    it is the only term with room (0.1 x div_J, ours 0.11), it is a multi-day build, and it must show div_J on all 199
    videos with the official metric by 22 Sep to make the freeze. Order for him: B20 feature table -> ranker -> LOEO div_J;
    the probe-19 branch work only if probe 19 wins.
  FRIEND A: silent since 10 Sep, teacher/dense set never delivered, and the dense-fine-tune line is weak on new evidence.
    If he is back, his GPU goes to B5 TEST-TIME ADAPTATION, the one lever aimed at the mechanism that sinks TTA changes on
    the hidden embryos (embryo shift): cheapest form = re-estimate normalisation statistics / a few self-training steps on
    the target video before inference, go/no-go on the LOEO scratch model (0.68 on the unseen embryo) with the official
    metric. Otherwise nothing is assigned to him and the user should ping him.
  FINAL SUBMISSIONS: final 1 = best public config as above. Final 2 = the HEDGE, not a second public config: exp29 +
    axis-flip (+ hygiene) if probe 19 is a tie (strong local evidence on an unseen embryo, LB neutral); if probe 19 wins,
    final 2 = exp29 verbatim as the safe fallback. Both must be selected by hand on the Submissions page by 28 Sep.
  VITALII/ME: merge friends, run at most one follow-up probe per decisive result, prepare the two finals, no sweeps.
- 2026-09-15 19:00 FRIEND B: B20 DECISION POINT (CONTEXT_FRIEND_B.md §38.4, RESULTS row). On the 12 videos' predicted
  graphs the orphan-start candidate set reaches only 4/15 GT divisions (27%) at any radius; the missing daughters are
  not orphans. Per-daughter audit of all 30: 14 already linked to the parent, 6 orphans, 7 CLAIMED BY AN UNMATCHED NODE,
  3 undetected; all 15 parents detected. So a 'steal' from an unmatched predecessor removes an FP edge and adds a TP
  edge - it costs nothing on the edge term - and the ranker's ceiling becomes 13/15 (87%). exp07's steal lost edges
  because it thresholded edge_prob without labels. B20 scope: candidates = orphan OR low-quality-linked node at t+1,
  ranker learns which steals are right; expected ~130 positives on 199 videos. Streaming pass 1 (10-video bundles via
  the private kernel, inference with peak_prob, videos deleted after) is running: first bundle in progress.
- 2026-09-15 18:05 FRIEND B: B20 BUILD - pass 1 and pass 2 in place and validated (CONTEXT_FRIEND_B.md §38.5-38.7).
  Pass 1 (while a bundle's frames are on disk): inference with peak_prob, the post-gap checkpoint graph (the exact
  input of the shipped division stage, prune-isolated deferred) and the 8-view DeepCenter score of every raw node, so
  pass 2 needs no frames. Pass 2 CONTROL on 12 videos - shipped ranking through the checkpoint + cached veto + notebook
  tail - reproduces the shipped stage EXACTLY (0.9001, div 1/6/14). Learned ranker: 5-9 positives on 12 videos are
  untrainable (fills the caps with FPs), but STEAL mode already lifts TP 1 -> 3 with 9 reachable; a probability
  threshold was added so a weak model cannot spend the budget. Streaming over the 187 remaining videos in 10-video
  bundles via the private kernel is starting (first bundle in flight); ~2.5 min/video -> ~8 h unattended, expected
  ~130 positives. Then: LOO ranker, threshold, official div_J on all 199.
- 2026-09-15 18:15 FRIEND B: B20 STREAM RUNNING - 24 bundles x 8 videos via the private kernel, ~25 min/bundle, ~10 h
  unattended (log in experiments/local_friend_b_exp02_public_port/results/stream_bundles.log); nothing else heavy on his
  machine meanwhile (kaggle kernels output buffers the whole zip in RAM). Output per video: raw graph with peak_prob,
  post-gap checkpoint, DeepCenter score per node. Next, on the light CPU: the 199-video ranker trainer (negative
  subsampling, LOO by embryo and by video, probability threshold, OOF scores for pass 2 -> official div_J on all 199).
  ~130 positives. Then: LOO ranker, threshold, official div_J on all 199.- 2026-09-16 PROBE 18 SCORED: exp36 (exp29 + already-divided filter + sister floor 5 um) = **0.946**, -0.001 vs exp29 =
  tie inside the +-0.003 floor. Rule applied: not adopted, final 1 stays exp29 verbatim. Friend B's pre-registered local
  prediction was +0.0011 (0.947-0.948); the LB gave -0.001. Both numbers sit inside the noise floor, so the first
  local-vs-LB pair for the post-processing class is INCONCLUSIVE on magnitude and mildly against on sign - it does not
  falsify "post-processing is locally measurable", but it also gives no licence to promote +0.001-class local gains.
  Possible non-noise contributions: the 5 um sister floor removes 3.3% of real divisions on the labels (a TP on the hidden
  embryos would cost ~0.005 of div_J), and the floor changes which candidates fill the per-frame caps. Probe 19 (axis-flip)
  still pending; the duplicate submission of exp36 will score 0.946 again (deterministic scoring of the same file).- 2026-09-16 PROBE 19 SCORED: exp37 (exp29 + axis-flip TTA group) = **0.946**, -0.001 vs exp29 = tie. Local +0.0214 on
  12 videos (and +0.0187 on a scratch primary that never saw 44b6) did not transfer at all. DECISION: the inference class
  is NOT locally screenable even with an unseen-embryo control - the remaining unseen quantity is the test embryos
  themselves; friend B's port stays a post-processing instrument (and even there +0.001-class gains earn no probes, per
  probe 18). Axis-flip is closed as a gain. The duplicate exp36 submission scored 0.946 = identical: scoring of the same
  file is deterministic, the +-0.003 floor lives between kernel runs. Probes so far: 19 (+1 duplicate); every idea
  on the inference and post-processing side is now closed on the LB. FINALS: final 1 = exp29 verbatim (probe 14).
  Final 2 = reserved for B20's outcome (division ranker, friend B, gate = official div_J on all 199 with a margin that
  survives the 4:1 FP:TP ceiling); if B20 fails its gate by 22 Sep, final 2 = exp29 + axis-flip (0.946, same embryos,
  zero-cost diversification only). No further probes planned until B20 produces a candidate.- 2026-09-16 DISCUSSION RE-READ, hengck23 focus (research/discussions_summary.md "Update 2026-09-16"). Nothing that
  changes tonight's decisions; three items recorded: B31 node clustering (a duplicate-merge, not a prune - the one node-
  budget variant B25 did not test) queued for friend B after B20; B20 gate note (second daughter arc needs ~2x the
  continuation gate, reachability 29% at 7 um -> 100% at 15 um); B24 confirmed by the #1 competitor as a genuine third
  embryo with our spacing. Negative evidence noted: a synthetic-trained division gate cost -0.004 on the LB (Juan Neira).
  hengck23's end-to-end linker (raw edge J ~0.90, trained without Kaggle labels) is recorded as a post-competition idea:
  no LB proof, not integrable in 14 days.- 2026-09-16 CODE SCAN BY CONTENT (user: "look at code regardless of score"): 16 liked/new notebooks pulled and diffed
  (research/discussions_summary.md). New mechanisms found: appearance re-ID association ranker (arnav170, unscored),
  confidence-distance edge gate (kunaldesale2408, 0.940), successor-skip division addition, xiaoleilian's 2-UNet
  top-hat/none blend with public weights. All belong to classes closed on the LB (association +0.001, post-proc ties,
  secondary swaps negative). No probe. Rule kept: a late public notebook with a PUBLISHED score >= 0.950 gets one
  probe as-is without discussion.- 2026-09-18 CODE SCAN (API only, the browser extension is down): 11 new notebooks pulled and diffed. Leaderboard via API:
  3682 teams, top 0.973; plateau 0.947 = 628 teams, 0.948 = 65, 0.949 = 26; we are rank 613 at 0.947 (tie-break by
  date). No mass-adopted public notebook above 0.947. THE FIND: `giorgosi/biohub-divnet-v2` - a public, trained
  per-node division detector (see B20 row) that is essentially the model friend B was going to train, with its own
  OOF numbers on all 199 videos. Vendored the loader/scorer (`tools/divnet_infer.py`, lifted verbatim from
  haideptry's notebook) and added the dataset to `tools/get_kaggle_datasets.py`. Handed to friend B: score his B20
  candidates with DivNet p as the ranker (top-k per parent, threshold from the manifest calibration: p>=0.5 gives
  TPR 0.72 at 3% FPR vs confusers), official div_J on 199 as the gate. Other new code: thtennant "frontier947" forks
  (local flow-field motion relink, gap-fill from a low-confidence detection pool at det 0.96, deadline degradation),
  a per-video denoising-autoencoder prefilter (ghazarosbarseghyan91, test-time adaptation flavour, alpha 0.15),
  arnav170 steal2 (re-ID + steal), newwang12 density-grouped overrides, alfonso1799 "V50 SOTA 0.9605" (2 cells,
  claim unverified; the LB has one team at 0.961 so it is not a public-notebook effect). None probed.
  Scores read later in the browser: haideptry "SOTA 0.948+" (DivNet as a soft veto) = **0.945**, i.e. the veto use costs
  -0.002 on the exp29-class config - consistent with "ranking, not vetoing"; raunakdey07 harmonic-fusion-v3 = 0.947 (tie).- 2026-09-18 FRIEND A IS BACK, FRIEND B IS OUT (user). PROMPT_FRIEND_A.md re-cut with a top block that cancels the dense
  fine-tune line (he had started a notebook for it - stopped) and hands him B20 with DivNet on friend B's port: pass 1
  over all 199 videos locally (no Kaggle bundling, he has the data), DivNet scores per candidate fork while frames are on
  disk, pass 2 with DivNet ranking (top-k, min-score grid), official div_J on 199, gate = score >= control + 0.005 with
  division TP up and adj_edge within 0.001, deadline 22 Sep, then one LB probe by me. Friend B's B20 stream (148/199)
  and scripts stay in the repo as the base; his prompt is unchanged in case he returns.
- 2026-09-19 22:06 FRIEND A: B20 PUBLIC DIVNET CLOSED on all 199 videos with the official metric. Control public ranking:
  score **0.91203**, adj_edge 0.90231, div_J 0.09717, divisions 24/96/127. Best DivNet setting (top-k 2, p>=0.5):
  **0.90007 (-0.01196)**, adj_edge 0.89666 (-0.00565), div_J 0.03404, divisions 16/319/135; thresholds 0.3/0.5/0.7
  are effectively flat, and top-k 1 is worse (~0.8981, 8/~325/143). No setting passes the pre-registered +0.005 score,
  TP-up, edge-within-0.001 gate; no LB probe and no B20 winner. The integration exposes the limitation: the public DivNet
  checkpoint returns one parent-event probability, copied to every candidate fork of that parent, so it cannot rank the
  alternative second daughters; geometry still breaks within-parent ties and false steals explode. Full reproducible report
  is in `experiments/local_friend_a_b20_divnet/results/b20_final.{md,json}`. The Windows-resume failure at 190/199 DivNet
  videos was fixed by explicitly closing NPZ handles and retrying transient `os.replace` locks; all cached work resumed.- 2026-09-19 FRIEND A MERGED (3 commits, one day of work): B20 with DivNet built end to end and RUN ON ALL 199 VIDEOS
  (`experiments/local_friend_a_b20_divnet/`, root notebook `friend-a-b20-divnet.ipynb`, results/b20_final.md). Official
  metric, 199 videos: CONTROL (public ranking through his pass 2) = 0.9120, adj_edge 0.9023, divisions 24/96/127,
  div_J 0.097. DivNet ranking, steal candidates within 15 um: k=1 -> 8 TP / 325 FP, score -0.014; k=2 -> 16 TP / 319 FP,
  score -0.012; adj_edge -0.006 in every variant; thresholds 0.3/0.5/0.7 give IDENTICAL results. FIRST PASS NEGATIVE,
  but not a verdict on DivNet: the implementation computes ONE p PER PARENT (DivNet is a parent-event classifier) and
  attaches it to every admissible second child, so (a) the choice of WHICH candidate is the daughter is unresolved
  (ties -> arbitrary), (b) the 15 um steal pool multiplies candidates and the per-frame caps bind before any threshold
  does (hence threshold-invariance), (c) steals remove true edges (adj_edge -0.006). Two cheap follow-ups from his
  cached per-parent p, written into PROMPT_FRIEND_A.md: (1) AUC of p for parents matched to GT dividers vs the rest on
  all 199 - if ~0.85 the inputs are right and only the design failed, if ~0.5 the input construction is wrong;
  (2) same candidate set and caps as the PUBLIC gate (sister floor 5 um, radius <= 12 um), public ranking replaced by
  p descending, and within a parent the daughter chosen by geometry (largest sister separation) - a pure ranking
  change, no FP explosion possible. Gate unchanged. He also built a resumable B5 test-time adaptation notebook
  (adabn / head-only EMA self-training on the LOEO scratch model) - not run yet, optional after B20.
  His tool changes merged: `tools/divnet_infer.py` rewritten around the manifest (pool-then-crop, percentile
  normalisation, marker), `tools/public_local.py` honours BIOHUB_WEIGHTS_ROOT / BIOHUB_DATA_DIR.
- 2026-09-19 23:35 FRIEND A: B20 CACHED FOLLOW-UPS COMPLETE on all 199 videos, official metric. Parent diagnostic over
  3,821,426 cached p values: 142/151 GT division parents matched within 7 um, **AUC 0.8340**, hits@1/2/3
  0.268/0.352/0.394, close enough to the published 0.887/0.28/0.40/0.46 to validate the input construction. Exact
  public orphan-only pool (parent <=12 um, sister >=5 um, no steal) reproduces control at 0.91205. DivNet order without
  a threshold is 0.91161; p>=0.5 is best at **0.91430 (+0.00227)**, adj_edge 0.90244 (+0.00013), div 23/43/128;
  the final p/(1+public geometry cost) hybrid is 0.91192, div 25/105/126. None passes the registered +0.005 + TP-up +
  edge-within-0.001 gate. **B20 divisions are closed; no LB probe.** Full report and histogram:
  `experiments/local_friend_a_b20_divnet/results/b20_followup.{md,json}` and `b20_followup_diagnostic.svg`.
- 2026-09-20 13:05 FRIEND A: B5 TEST-TIME ADAPTATION COMPLETE on the fixed 12-video 44b6 honest LOEO fold. The
  unchanged 6bba-only scratch checkpoint scores 0.68034. Label-free per-video AdaBN with the registered node-count
  guard scores **0.68761 (+0.00728)**, raw edge J 0.68815 and node recall 0.86535, passing the +0.005 gate; it is used
  on 9/12 videos and falls back to baseline on three videos whose candidate node ratios are outside `[0.90, 1.05]`.
  The guarded result has 6 per-video wins, 3 losses and 3 fallback ties, so the gain is real in the official weighted
  aggregate but heterogeneous. Head-only EMA scores 0.67783 (-0.00251) and is rejected. Nothing was submitted to the
  leaderboard. Full report and exact scorer outputs: `experiments/local_friend_a_exp04_tta_b5/results/b5_final.{md,json}`.- 2026-09-20 RE-CUT AFTER FRIEND A'S TWO COMMITS (771aeb9 B20 closed, 0c9f60c B5 AdaBN win) AND FRIEND C JOINING (user):
  (1) B20 is CLOSED on the pre-registered gate: DivNet inputs validated (AUC 0.834 vs 0.887 published), best variant =
  veto p >= 0.5 on the public candidates, +0.0023 on 199 videos (59 division FP removed, 1 TP lost, edges unchanged),
  below +0.005; consistent with haideptry's LB 0.945 using the same veto. Not probed. (2) B5 AdaBN passed: honest LOEO
  fold (6bba-only scratch model, 12 videos of 44b6) 0.6803 -> 0.6876 (+0.0073) with the label-free node-ratio guard
  [0.90, 1.05] (fallback on 3/12 videos), head-EMA -0.0025 rejected. Per-video spread is wide (-0.051..+0.046) but the
  weighted aggregate passes. The public primary AND secondary use nn.BatchNorm3d (tools/repo/.../temporal_unet.py), so
  AdaBN applies inside the kernel: friend A ports his _adapt_adabn into one kernel-ready cell (per test video, primary +
  secondary, guard), regression check via friend B's port on 12 videos with the public weights (not an honest test,
  just "nothing breaks + time budget"), report 22 Sep -> ONE LB PROBE (exp38 = exp29 + AdaBN), user's go required.
  This is the first local win aimed at the embryo-shift mechanism instead of post-processing; LB transfer is the test.
  (3) Friend C (MacBook Air M4 16 GB, no CUDA, no data): what fits = CPU work from friend A's cached pass 1; what does
  not = the GPU stage of the port, training, the 82 GB download. He takes B31 node clustering (PROMPT_FRIEND_C.md,
  branch friend-c, results in experiments/local_friend_c_b31_cluster/, deadline 23 Sep): step 1 nearest-neighbour
  distance of raw nodes within a frame on 199 videos vs GT (if <1% of peaks closer than 2 um, no lever); step 2 greedy
  score-ordered merge at r = 0.5/1/1.5/2 um on the post-gap `ckpt`, then cached public divisions + final tail on CPU
  with DeepCenter read from dc/<stem>.npz by node_id; gate +0.005 on 199 with adj_edge within 0.001; +0.002..+0.005
  with fewer nodes is reported as a final-2 candidate. This boundary is required because dc has no scores for synthetic
  gap points, so raw -> full pp cannot be replayed without frames. Root notebook `friend-c-b31-cluster.ipynb` is
  resumable and enforces radius-0 control 0.9120275 / 24-96-127. Friend A packages cache/<tag>/{raw,dc,ckpt} + GT geffs.
  Finals unchanged: final 1 = exp29 (probe 14); final 2 = AdaBN probe if it scores >= 0.947, else exp29 + axis-flip.- 2026-09-20 DISCUSSION/CODE CHECK (user asked; browser dropped mid-way, focus3d + shakeup threads not re-read): Eric
  (742064) verified from the shipped manifests that the public 0.947 detectors trained on all 199 train videos, so every
  train hold-out is in-sample for the public stack (his local +0.0078 became -0.002 on the LB); hikaggler (741749) +
  Ogurtsov (5th): no detector/linker change moved the LB, node-count calibration is the LB-predictive readout, local
  ranking of weights does not transfer, only synthetic pretraining helped him and only on his own 0.939 pipeline. Code:
  nothing above 0.947; giorgosin (DivNet author) is now training an appearance-aware edge predictor (linker line, out of
  our window); ghazarosghazaros runs self-distillation arms on 0.946. Details research/discussions_summary.md. Addendum: hengck23 (focus3d, 12 h) is
  himself "trying to find a model that doesn't over estimate num of nodes"; shakeup thread = Mamarin's history of 13
  microscopy boards (8/13 kept >= 5 of the top 10). Plan unchanged: AdaBN probe (exp38) when friend A's cell is ready,
  B31 on friend C.
- 2026-09-21 FRIEND C: B31 CLOSED AT STEP 1 on all 199 cached raw graphs. Physical same-frame nearest-neighbour audit:
  4,211,780 raw nodes have **zero** neighbours below 1, 2, or 3 um; sparse GT has 2/133,318 below 3 um and zero below
  2 um. This triggers the registered `<1% below 2 um => no lever` stop rule. Mechanism: the public detector already
  applies 3 um physical NMS, so proposed clustering radii 0.5/1.0/1.5/2.0 cannot merge any raw pair. The radius sweep
  is intentionally skipped and no LB probe is requested. CPU-only radius 0 was still rebuilt on all 199 in 521 s and
  exactly reproduced score 0.9120275, adj_edge 0.9023109, divisions 24/96/127. Mac-safe resumable implementation is in
  `experiments/local_friend_c_b31_cluster/` and `friend-c-b31-cluster.ipynb`; report in `results/b31_step1.{md,json}`.- 2026-09-21 B31 CLOSED (friend A ran "friend C's" step 1 himself on Windows, commit 428e400; nothing ran on the Mac).
  Verdict accepted: 0 of 4,211,780 raw nodes have a same-frame neighbour under 3 um because the public peak extractor
  IS a 3 um max-pool NMS (pool_kernel_um 3.0 -> (3,3,3) kernel on the (1,4,4) grid), so clustering radii 0.5-2 um are a
  no-op by construction, and the next kernel size (6 um) was already measured by friend B at -0.026 (7.9% of nodes,
  recall 0.976). My oversight: B31 was queued without checking that bound; the +3-4% node excess is NOT duplicate
  peaks but single peaks on unannotated/extra nuclei, which no geometric merge can remove (same wall as B25). Node
  budget levers left: none geometric; only detector-side (AdaBN guard keeps the ratio inside [0.90, 1.05]).
  Friend C: no CPU task with a mechanism remains inside the freeze window; on standby (his prompt says so, friend A
  wrote the top block). Friend A: cache package cancelled, straight to the AdaBN kernel cell (item 2 of his 20 Sep block).
- 2026-09-21 FRIEND A EXP38 PUBLIC-STACK ADABN REGRESSION COMPLETE on the fixed 12 44b6 videos. This is not honest
  validation because both public checkpoints saw these videos. Unchanged exp29 scores **0.90010**; raw per-video AdaBN
  scores 0.85644 (-0.04366); the registered label-free node-ratio guard `[0.90, 1.05]` accepts 4/12 and scores
  **0.89352 (-0.00657)**. Guarded node recall rises 0.98726 -> 0.99062, but adjusted edge falls 0.89534 -> 0.88797;
  among accepted videos there are two wins and two losses, with the losses dominating. End-to-end runtime was ~34 min
  on RTX 5070 Ti; adaptation itself was ~78 s. **AdaBN is rejected for the public stack and no exp38 LB probe is
  requested.** Honest B5 remains valid for its scratch LOEO model, but the effect does not transfer safely to the
  already in-sample public weights. Full report: `experiments/local_friend_a_exp05_public_adabn/results/exp38_final.md`.- 2026-09-21 EXP38 (public exp29 + per-video AdaBN) REJECTED BEFORE THE LB, verdict accepted. Friend A's regression on
  the fixed 12 44b6 videos with the public weights: unchanged exp29 0.9001; raw AdaBN 0.8564 (-0.044), guarded [0.90,
  1.05] 0.8935 (-0.0066), guard fell back on 8/12 videos because BN recalibration inflates raw nodes 1.1-2.0x; the 4
  accepted videos split 2 wins / 2 losses with losses dominating; node recall +0.003, adj_edge -0.007. Reading: the
  public detector's 0.965 threshold is calibrated to its train-time BN statistics (all 199 videos, augmented); per-video
  statistics shift the logits and the threshold no longer means the same thing, so the effect is a calibration change,
  not domain adaptation. On the scratch LOEO model the same shift happened to help (0.68 -> 0.69), which says nothing
  about the 0.947 stack. Tuning the guard bounds or a partial-momentum blend on these in-sample videos would be exactly
  the in-sample knob fitting Eric's post warns about, so no second attempt. B5 closed for the public stack.
  STATE OF THE PLAN, 3 days before the freeze: every queued line is closed (B20 divisions +0.0023 < gate, B31 no-op by
  the NMS bound, B5 calibration blow-up). Final 1 = exp29 (probe 14, id 56146538). Final 2 = exp37 (exp29 + axis-flip,
  0.946, probe 19) unless the user approves ONE last probe: exp29 + DivNet veto p >= 0.5 on safe divisions (the only
  local positive left, +0.0023 on all 199 with edges untouched, 59 division FP removed / 1 TP lost; haideptry's public
  0.945 uses the same veto on his stack). Friends A and C on standby; friend B out.- 2026-09-21 EVENING SITE CHECK (user): haideptry's new "0.951" notebook = his density-adaptive stack + DivNet veto +
  DeepCenter safe-div 0.25; his team is at 0.947 on the LB, title not backed. LB snapshot: 104 teams >= 0.951, 714 at
  0.947 (we are rank 733). Third independent confirmation (Justin CH123) that LB movement tracks the test node count,
  not offline edge J. Nothing to adopt; exp39 probe (exp29 + DivNet veto p >= 0.5, kernel pushed 21 Sep) still running.
  Details in research/discussions_summary.md.- 2026-09-22 B32 OPENED (user: "8 days left"). Post-mortem first: the plateau is the public stack's ceiling (714 teams
  at 0.947); the top 10 (0.966-0.974) built their own detectors and division models over months; ~+0.02 of the gap is
  the division term alone (their div_J ~0.3 vs our 0.11). The one line we never ran with our own training is a division
  PAIR model on a wide candidate pool (public funnel reaches 35/151; DivNet scores the parent only). Friend A gets it
  as B32 (PROMPT_FRIEND_A.md top block): pool = parent with one child + orphan within 15 um, sister 5-20 um, DeepCenter
  veto, no divergence/symmetry gates; labels = parent and both daughters within 7 um of a GT division; model = DivNet
  UNet-GAP initialised from best_overall.pt with 4 image lags + 3 markers (parent, d1, d2) + geometry head; 2 folds
  by embryo -> OOF p on all 199; pass 2 from his checkpoints with tau x caps sweep; gate score >= control + 0.005 on
  199 and on each embryo, adj_edge within 0.001; final model on all 199 -> weights_dataset/friend_a_divpair/ ->
  I build the kernel (division stage replaced) -> one probe 25-26 Sep. FREEZE for this line moves to 27 Sep; finals
  ticked 28 Sep. Odds stated to the user: about 1 in 4. Rejected alternatives: HOCT veto notebook (public, not above
  0.947, 1 in 10), synthetic pretraining (3-4 GPU days, lands below the public stack).- 2026-09-21 20:50 PROBE 20 SUBMITTED (id 56440312, PENDING): exp39 = exp29 realised config + DivNet parent veto p >= 0.5
  inside add_safe_divisions_postlink (kernel vitaliineibauer/biohub-exp39-sjlee947-tight55-divnetveto v1, folder
  experiments/exp39_sjlee947_tight55_divnetveto/, probe.json has base/change/local/risk/rule). Kernel ran ~100 min on
  2xT4 (DivNet frame reads); on the 4 dummy test clips the veto was live: checked 64/32/10/43 candidates per clip,
  vetoed 36/26/6/34, divisions added 26/6/4/9. Rule: >= 0.948 -> final 2; 0.945-0.947 tie (prefer exp39 over exp37
  only if equal, strictly fewer false divisions); <= 0.944 drop. 4 submissions left today.- 2026-09-22 PROBE 20 SCORED: exp39 (exp29 + DivNet veto p >= 0.5) = **0.947**, a tie with exp29 (probe 14, 0.947) and
  +0.001 over exp37 (0.946). The public share of the division term is too small to show a +0.002 local effect, as
  expected. FINALS DECISION (recommended, user ticks by 28 Sep): final 1 = exp29 (id 56146538) unchanged; final 2 =
  **exp39 (id 56440312)** instead of exp37: same public score as final 1, differs only in the division stage, with local
  evidence on both embryos (all 199 videos: 59 division FP removed, 1 TP lost, edges and nodes untouched), whereas exp37
  changes inference views with in-sample-only local evidence and is 0.001 lower on the board. B20/DivNet line fully
  closed on the LB now (veto = tie). 4 slots left today, none planned until B32 delivers.
- 2026-09-22 B32 STEP 1 STOP: the registered 15 um orphan-only pool on all 199 B20 checkpoints covers only 58/151
  GT divisions (38.4%; 44b6 6/26, 6bba 52/125), not the required >90%. A cumulative reach audit finds the matched
  parent and both matched daughters for only 121/151 (80.1%), so the gate is impossible even before candidate rules;
  117 have the correct existing child, 116 pass geometry, 97 pass DeepCenter, and 58 remain after orphan-only. Parent
  radius 30 um adds only one (59/151); removing sister/DC constraints within the orphan pool reaches 63/151; allowing
  claimed daughters reaches 97/151 but creates 16.3M triples and still misses the gate. No crop cache, GPU training,
  or LB probe was run. B32 needs a newly registered upstream detection/edge-replacement redesign, not a radius tweak.
  Reproducible notebook/code and full report: `experiments/local_friend_a_b32_divpair/`.
- 2026-09-22 B32 CLOSED AT STEP 1, verdict accepted (friend A, commit d9383d9, CPU audit only, no training, no probe).
  Reach of GT divisions through the PREDICTED graph on all 199 videos: parent detected 149/151, parent AND both
  daughters detected 121/151 (80%) - the first ceiling is the detector, which misses one daughter in a fifth of the
  divisions (dividing nuclei shrink); existing child correct 117; within 15 um 116; DeepCenter >= 0.20 97; ORPHAN-ONLY
  58/151 (38%): in 39 cases the second daughter is already linked to another parent, so a division needs an edge
  replacement (steal), and the steal pool reaches 97/151 only at 16.3M triples. Radius 30 um adds one. My registered
  ">90% reach" gate came from GT geometry ("29% at 7 um -> 100% at 15 um"), not from the predicted graph, so the plan
  was mis-specified by me, and the audit is the useful result: to lift div_J from 0.10 to 0.21 (= +0.005 score) we need
  ~+21 true divisions at no extra FP; the orphan pool offers 34 more at a 1:5800 prior (needs FPR ~3e-4 at TPR 0.6, i.e.
  AUC ~0.99, vs DivNet 0.83 on an easier pool), the steal pool 73 more at 1:170k. Neither is a five-day model. The
  division term inside this stack is bounded by the detector and the linker, which is exactly what the top teams
  replaced. B32 closed; friend A on standby; freeze back to the plan (nothing running); finals as decided on 22 Sep
  (final 1 exp29 id 56146538, final 2 exp39 id 56440312).- 2026-09-23 USER DECISION: TARGET 0.950 ON THE PUBLIC LB BY 29 SEP, ALL RESOURCES IN (his words: "мне нужен 0.95, у нас 7 дней,
  у нас 5070ti, ты это выполнишь"). Consequences recorded: (1) the 8 Sep "post-proc probes closed" rule is LIFTED; up to 5
  probes/day, 30 slots to the deadline; (2) selection risk stated to the user: with +-0.003 noise, 30 near-tie
  submissions will likely produce a 0.949-0.950 on the public board by chance that need not hold on the private 71%;
  finals still need local support, so every candidate carries its per-embryo numbers; (3) programme = B33 post-proc
  grid on 199 videos (friend A, CPU, candidates nightly, per-embryo gate) + B34 appearance-aware linker (friend A, GPU,
  report 26 Sep) + LB probes by me via tools/build_probe_kernel.py (exp29 + env overrides, DivNet veto on/off, guard
  patched). Node-budget math recorded for the record: the node term is linear and unbounded (0.001 per 1% of nodes)
  but 20x weaker than the edge term, so pruning only pays if the pruned nodes carry < 5% of the average annotated-edge
  load (B25: even 5% at 99.6% recall lost 0.002); hengck23's refine head (-13% at 99.45%) is a wash by the same math.
  Freeze: none; last results push 27 Sep evening; finals ticked 28 Sep = best public among candidates with local
  per-embryo support (final 1 stays exp29 unless a candidate beats it on both embryos locally AND on the board).- 2026-09-23 FRIEND C TASK (user asked): line 1 split. Friend C = the CPU tail of the post-processing grid from friend A's
  ckpt/dc package via the B31 runner's radius-0 path (linefit weight x window - the largest stage, never swept -, short-
  track filter and rescue, safe-division gates/caps, DeepCenter safe-div threshold, edge max), all 199 videos, per-embryo
  readout, node ratio; friend A = stages that need frames (relink, gap closing, DeepCenter gap threshold) + GPU line 2;
  friend A publishes the package today with tools/package_friend_c_b31_cache.py. Both feed candidates nightly; I probe.- 2026-09-23 FRIEND A 73648e8: B33 grid runner ready (45 one-knob variants from the 199 raw graphs, exp29 notebook's own
  post-processing functions, resumable, per-embryo readout + node ratio, control forced to tight55). B34 audit: giorgosin's
  trainer needs the public checkpoint (trained on both embryos), validates on a fixed 6bba+44b6 pair, mixes ZSNS relay
  data, trains on GT-node pairs, no per-epoch resume, Kaggle-only paths -> not an honest LOEO. DECISION: B34 only as an
  explicitly in-sample public-checkpoint regression (author init, 12-video port check like exp38, LB probe decides),
  capped at one day of porting, after B33 and the friend C package; else closed and the GPU goes to B33's GPU variants.- 2026-09-23 PROBES 21 AND 22 SUBMITTED (PENDING): exp40 = exp29 + motion relink OFF (id 56459135; kernel stats confirm 0
  relink edges, nodes -0.8%..+0.04% on the dummy clips, safe divisions 49/29/10/46 vs exp39's 26/6/4/9 because the veto is
  off), exp41 = exp29 + MOTION_RELINK_LEARNED_BONUS 1.0 -> 2.5 (id 56459139; relink edge counts shift by a few per clip).
  Both built by tools/build_probe_kernel.py. 3 slots left today.- 2026-09-23 NIGHT, USER RAISED THE TARGET TO 0.97 BY 29 SEP AND REAFFIRMED IT ("ты должен добиться 0.97 за 6 дней"). Stated once
  to the user and recorded: +0.023 needed; only the division term has that size (ours 0.10, top-3 ~0.3); inside our
  stack the B32 audit bounds reach by the detector (121/151) and the orphan rule (58/151); a division-level rebuild of
  the detector is months of work for the top teams; my expectation for this programme is 0.948-0.950 public, with
  line 3 the only line whose ceiling is ~+0.01. Decision taken: B34 dropped (GPU to line 3), B35 opened (daughter
  recovery + steal pool + pair model, PROMPT_FRIEND_A.md top block), B33 CPU grid continues, friend C adds pairwise
  combinations and a per-video win-rate criterion (>= 55% of videos per embryo) to his tail grid, I keep 5 probes/day.
  Site check 23 Sep: takaito's "gshift" (per-frame global shift before relink, MNN 12 um) ported as exp42 (running);
  his team is 0.946 after 28 submissions; new threads are two more "stuck at 0.947" posts and no answers from the top.- 2026-09-23 NIGHT, USER'S PRE-CHECK OF B35 (tools/audit_b35.py, written on his side, committed here): (1) the top-3%
  DivNet-p prefilter was an assumption; the script measures GT-parent recall vs fraction (1..100%) per video, and the
  prefilter threshold must come from that curve; (2) the B32 reach audit used greedy matching and direct t+1 daughters
  only, while the official scorer matches optimally (_match_full, 7 um) and credits daughter branches within a frame
  window, so 121/151 is not yet a strict ceiling; the script recomputes it by the scorer's rules. Friend A runs it as
  step A0 before any training; the friend C package gains the divnet/ folder so the audit can run without him.- 2026-09-24 B35 STEP A0 (friend A, f6610f9): official window matching reaches 136/151 (44b6 24/26, 6bba 112/125), direct
  parent+both daughters 123/151; DivNet-p prefilter refuted (top 3% -> 42% recall, top 50% -> 83%). Decisions: step A =
  one full-frame primary pass at threshold 0.90 per frame with a peak cache and spatial matching (his proposal,
  confirmed), gate reach >= 144/151 at <= 0.3% candidate nodes (not his 150/151); step B proceeds regardless because
  the dominant loss is now the orphan rule (136 reachable vs 58 orphan pool); step B prefilter = embryo-fold geometric
  ranker with a recall-vs-fraction curve (DivNet p as one feature), pair model only on the retained fraction.- 2026-09-24 PROBE 23 SUBMITTED: exp42 = exp29 + takaito's per-frame global-shift correction inside the motion relink
  (median of mutual-NN shifts, 12 um; ported line for line via tools/build_probe_kernel.py --patch gshift). Kernel stats
  on the dummy clips: shift computed on 99/99 frame pairs per clip, summed |shift| 225 / 118 / 48 / 89 um per clip, i.e.
  a mean per-frame global displacement of 0.5-2.3 um - comparable to the 1.8 um median true step, so the uncorrected
  relink cost is biased on drifting videos. Node counts within +-0.5% of exp29. Probes 21/22 still pending.- 2026-09-24 PROBES 21 AND 22 SCORED: exp40 (motion relink OFF) = 0.945, exp41 (relink learned bonus 2.5) = 0.945; both
  -0.002 vs exp29, i.e. ties at the noise floor, slightly negative. The relink stage as shipped stays; friend B's local
  +0.0053 for relink-off (one division TP + 0.0014 edges on 12 videos) did not transfer. Probe 23 (exp42 gshift) pending.
  Friend A 31f3212: resumable B35 step A (tools/recover_daughters.py, full-frame 0.90 pass + peak cache) committed, run pending.- 2026-09-24 DISCUSSION CHECK: OmerZalman (0.95) says the top gains came from improving ALL stages together (a 0.969 team
  told him the same); OpPrime traced 0.947-stack division losses across pre-ILP, ILP selection and relink - the same
  multi-stage loss as our A0 audit, consistent with B35 inserting divisions after the tail with edge replacement;
  Pavel (43rd) shows CV/LB decoupling at the top. No code or recipe shared. Details research/discussions_summary.md.- 2026-09-24 PROBE 23 SCORED: exp42 (exp29 + takaito's gshift patch only) = 0.945, -0.002 vs exp29, same as probes 21/22.
  It was NOT his notebook verbatim: his base is haideptry's density-adaptive stack (relink radius 5.5-7.25 um by
  density group, DivNet veto, DeepCenter safe-div 0.25, UNet batch 8) + gshift; I transplanted one piece onto exp29.
  Three relink-stage changes on exp29 (off, bonus 2.5, gshift) all landed at 0.945: the relink stage of exp29 is at its
  local optimum for the hidden embryo. Next check if slots allow: his notebook verbatim as one probe.- 2026-09-22 20:10 UTC (DATE CORRECTION: the notes above headed 2026-09-23 and 2026-09-24 were all written on 22 Sep UTC;
  the session clock ran ahead; real deadline math: today 22 Sep, 7 days left). Two slots left today (5/day, UTC).
  exp43 = takaito/biohub-a951-gshift VERBATIM (user "да"; his stack also carries a relative-rank/mutual-best association
  patch, beta 0.12, which I had missed when porting gshift alone) - kernel running. exp44 = exp43 + friend B's axis-flip
  TTA cell (exp37 verbatim) = a BUNDLE with a change in every stage vs exp29 (detector TTA, association, relink density
  + gshift, divisions DivNet + DC 0.25), per the user's "bundles, not single knobs"; read against exp43 the same day.
  Both kernels pushed; submit both when complete.- 2026-09-22 ~20:40 UTC: exp44 REBUILT as a real bundle after the user pointed out that axis-flip alone is one knob vs exp43:
  takaito base + axis-flip TTA (detector) + exp36 division hygiene (sister floor 5 um + already-divided filter). The v2
  push first failed on the 2-concurrent-GPU-session limit (commit f247b24 says "pushed" - it was not); the user stopped
  v1 on the site and v2 is now running (submit with -v 2). exp43 still running. Both go out before 00:00 UTC.- 2026-09-22 ~20:45 UTC PROBES 24 AND 25 SUBMITTED (pending): exp43 = takaito a951-gshift verbatim; exp44 v2 = exp43 +
  axis-flip TTA + division hygiene (bundle). Kernel log of exp44 confirms both changes ran (TTA GROUP replaced;
  already-divided filter dropped 0-1 edges per clip); submission files differ. 5/5 slots used today.- 2026-09-23 18:40 UTC PROBES 24/25 SCORED + SITE/CODE CHECK. exp43 (takaito a951-gshift VERBATIM) = 0.944 vs his published
  0.948: the SAME notebook lands 0.004 apart across two runs, so the public "0.948" notebooks are favourable draws from a
  ~0.945 +- 0.003 distribution and exp29's 0.947 sits in the same distribution. exp44 bundle (exp43 + axis-flip +
  division hygiene) = 0.946, +0.002 over exp43 on the same day, -0.001 vs exp29. Six probes in a row (20-25) landed
  0.944-0.947. DECISION: no more probes of public-notebook variants; slots go only to B35 and the grid tables (with
  per-embryo support). Finals unchanged: exp29 + exp39. LB 23 Sep: 3851 teams, 136 >= 0.951, 724 at 0.947 (us rank 834);
  OmerZalman now 0.952; sjlee101's team 0.949 after 82 submissions. Discussion: nothing actionable (Civitasmass stuck at
  0.947 for a month; "today" was the merge deadline, submissions open to 29 Sep). Code: 6 new notebooks, all the same
  family (mutual-best beta 0.20/0.25, gshift, DivNet veto); two new knobs taken into the grids: weak-leaf pruning
  (BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB, e.g. 0.30; node-count lever) -> friend C tail grid; relink velocity weight 0.25 ->
  friend A B33 grid. Main: friend A pushed two Step A fixes (import path, videos without divisions), no results yet;
  friend C has not pushed a branch.- 2026-09-23 TEAM CLARIFICATION (user): "friend C" is friend A himself on his MacBook (same person, Kaggle Sasyami, a team
  member), not a separate participant; no private-sharing issue (rules: no private sharing of code/data outside teams;
  team merger deadline passed 22 Sep 23:59 UTC; team = gsfatakhov, sasyami, vitaliineibauer). Consequence for planning:
  friend A's attention is split across both machines. Extra legitimate GPU: each team member's own Kaggle quota
  (sasyami, gsfatakhov ~30 h/week each). Colab free T4 is connected in the user's browser (1 account; a second Google
  account for extra free quota was advised against).- 2026-09-23 20:30 UTC RESEARCH+PLAN WORKFLOW DONE (wf_161da8ae-7e5, 9 agents; full JSON in the session scratchpad
  plan970.json). Key facts: (1) pawanmali removed every fork from our config family: public 0.947 -> 0.911, so our PUBLIC
  division Jaccard is ~0.36 already (local 0.10); the teams >= 0.951 lead on EDGES/detection (our public adj_edge ~0.91).
  (2) Proven division recipes are small: pawanmali's 3-class node classifier (cont/parent/daughter) inserted after the
  tail, <= 6 per video, +0.003 on a 0.926 base; Le +0.002 per division step (0.946 -> 0.950). (3) HOCT/Trackastra add
  nothing (HOCT veto variants all 0.947); Freitas synthetic has no mitotic phenotype (LB -0.004 for a user); the public
  Ultrack dorado embryo (our scale and frame rate, 80k noisy pseudo-divisions) is the only large external division
  source. (4) The notebook's built-in validator scores divisions with the OLD weakly-connected rule. (5) Compute: 26.7 h
  Kaggle GPU now + 30 h after reset 2026-09-26 00:00 UTC; teammates' own quotas; CPU kernels free. PLAN (critics'
  estimate): P(public >= 0.955) ~2-5%, P(0.97) < 0.5%, expected true gain ~+0.001; lines L0 (exp45 measures J_pub, sets
  the precision floor), L1 (laptop lab on friend A's image-free cache + tools/div_insert.py + --patch divinsert with
  parity checks), L2 (DaughterNet from scratch on Kaggle T4, honest 5 folds, orphan insertion first, steal gated
  separately), L5 (friend A DaughterNet-B full-res, ensemble partner), L4 (B33 + laptop leaf-prune grid), L3 optional
  (dorado pseudo-divisions, needs user OK for ~40 GB public download), L7 bundle and finals. Gates on a pre-registered
  SELECTION (6bba odd) / CONFIRMATION (6bba even + all 44b6) split. Finals: exp29 anchor + best confirmed stage (else
  exp39). Build workflow wf_d710f2f6-6f3 launched (splits, K-DN trainer, div_insert + kernel patch, cache replay).- 2026-09-23 B35 STEP A RESULT (friend A 3bb04e1, pushed before he saw the new order): a full-frame public-primary pass at
  threshold 0.90 reaches ALL 151/151 GT divisions under the window rule (136 -> 151; 44b6 26/26, 6bba 125/125) but at
  +24% candidate nodes (max 73% in one video), far over the 0.3% budget -> gate not passed. Consistent with the new plan:
  recovered daughters stay out of the submission path (a second detector pass per video and a huge candidate pool);
  L2 inserts divisions only on existing nodes.- 2026-09-23 21:30 UTC NIGHT LOG (user asleep until ~05:00 UTC, autonomous run). (1) Build workflow wf_d710f2f6-6f3 done, all
  4 artifacts verified and committed (b73bba2): splits.json, tools/div_insert.py (+18 tests), --patch divinsert, DaughterNet
  trainer kdn_train, replay lab. MAJOR catch by the splits verifier: the 44b6 videos are overlapping space-time crops of ONE
  recording (global GT node ids; 62 video pairs share 2,429 GT nodes and 2 divisions), so video-level folds leak; now 11
  leak groups kept whole per fold (0 of 62 links cross folds). 6bba has only 1-frame boundary overlaps between consecutive
  crops (independently annotated). Unique GT divisions = 149 (2 counted twice in 44b6). (2) L1 lab on friend A's cache
  (sasyami/biohub-friend-a-b20-cache, 125 MB, downloaded to data_external/friend_a_cache): controls reproduced EXACTLY
  (exp29 0.912028 / 24-96-127; exp39 0.914300 / 23-43-128; exp39_veto 0.914543). (3) Coordinate export: 1,012,255
  candidate nodes from 649,808 triples (incl. steal pool) -> experiments/l2_daughternet/coords_exp39.parquet (92d1c05) and
  private dataset vitaliineibauer/biohub-l2-coords; friend A told to return OOF p with a fold column for L5. (4) Kaggle:
  kdn-train smoke v1 passed end to end (contract re-score max |dp| 4e-8); full run v2 pushed (5 folds, 199 videos). K-DN-score
  kernel being built (wf_d6a27850-e77). (5) Dorado extractor workflow wf_7bfc39d2-ba0 still running; Colab T4 connected in
  the user's browser for it.
## 9. Literature
`research/survey_detection_sparse_labels.md`, `research/survey_linking_divisions.md`, `research/discussions_summary.md`.
