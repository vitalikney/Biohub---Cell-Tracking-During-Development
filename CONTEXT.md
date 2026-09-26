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
  the user's browser for it.- 2026-09-23 21:40 UTC L2 DaughterNet v1 TRAINED (kdn-train v2 on Kaggle 2xT4, 17,143 labelled GT samples: 151 parent / 302
  daughter / 16,690 cont incl. 4,801 hard negatives; 5 folds with 44b6 leak groups; ~20 min training, 8 min crop build).
  Honest OOF readout (all 199): parent AUC 0.848 (DivNet in-sample on the same samples 0.829), parent precision top 0.1% =
  6/18 (base 0.9%, LR ~38), top 1% = 38/172 (22%); daughter AUC 0.767, top 0.1% = 11/18, top 1% = 50/172 (29%, base 1.8%).
  Per embryo parent AUC 44b6 0.820 / 6bba 0.862. Contract re-score from raw frames PASS (max |dp| 5e-7). The plan's L2 kill
  criterion (daughter top-1% precision >= 2x base AND parent LR at top 0.1% >= 20) is PASSED -> proceed to K-DN-score of the
  1M exported nodes and the laptop insertion grid on SELECTION, then CONFIRMATION.- 2026-09-23 23:30 UTC L3 FINDING (dorado verifier, tools/register_44b6_dorado.py): the Kaggle 44b6 TRAIN clips are space-time
  crops of the PUBLIC Ultrack "dorado" movie itself (e.g. 44b6_12dfb391 = dorado frames 106-205 at one fixed shift; 654/777
  GT nodes coincide with dorado track points with no search; 63/71 clips placed). Consequences: (a) any model pretrained on
  dorado pseudo-labels is NOT leak-free on 44b6 (39% of dorado samples fall inside 44b6 clip boxes) -> judge L3 on 6bba only
  (125 parents / 250 daughters, fully independent), '44b6_clean' blocks are only partly clean; (b) the hosts state the
  hidden test embryos are different from train, so the public movie should not cover them. POLICY: we do NOT try to match
  hidden test clips against public recordings or use public tracks as test labels - against the spirit of the competition
  and the hosts' statement; dorado is used only as extra training data (allowed external data, Zebrahub/Ultrack public).
  Dorado extraction done: 8 shards, 12,241 usable samples, private dataset vitaliineibauer/biohub-dorado-crops; dorado-only
  training kernel biohub-l3-dorado-train pushed. K-DN-score done: OOF + ensemble p for all 1,012,255 exported nodes, 0 NaN,
  0 leak-excluded. Pool ceiling (tools/label_candidates.py): 62/151 GT parents and 123/302 daughters are present as exact-
  frame candidates (selection 27 / confirmation 35 parents). SELECTION orphan grid (16 configs) running.- 2026-09-23 23:45 UTC L3 CLOSED: dorado-only DaughterNet (12,241 pseudo-labelled crops, 40 epochs on Kaggle T4, 634 s) reaches
  only val AUC parent 0.62 / daughter 0.53 on its own held-out block 417 (vs Kaggle-trained OOF parent 0.85) - the Ultrack
  automatic divisions are too noisy (4.5x the GT division rate) to teach mitosis. Plan kill criterion met; no v3 init.
  L2 SELECTION orphan grid (64 videos, OOF p): best alpha=1 cap=3 -> +0.0038 (TP 7 -> 11, FP 15 -> 23, 90% CI
  [+0.0003, +0.0075], P(d>0) 0.965); thresholds 0.05-0.3 do not bind (cap 3/video binds). Extension with thresholds 0.4-0.7
  and caps 2-6 running before the single CONFIRMATION run.- 2026-09-24 00:15 UTC L2 v1 CONFIRMATION FAILED the pre-registered gate. Selected on SELECTION (64 videos): alpha 1, cap 2 per
  video, threshold 0.6 -> +0.0044 (TP 7 -> 11, FP 15 -> 19, 90% CI [+0.0008, +0.0083]). One run on CONFIRMATION (135 videos):
  +0.0010 (TP 16 -> 18, FP 28 -> 33, CI [-0.0008, +0.0033]); 44b6 +0.0000, 6bba +0.0015. Gate needed >= +0.002, CI > 0,
  net TP >= +3, added-fork precision >= 0.31 (got 2/7). No probe for v1-orphan. Reading: the selection gain was partly
  selection noise; precision on the REAL candidate pool is the weakness (v1 trained on GT-node crops only). Next: (a) steal
  sub-test on SELECTION (running); (b) v2 = v1 + hard examples from the predicted pool labelled by GT matching
  (tools/label_candidates.py) - trainer extension being built (wf_bd752e22-e54). Also noted: the 5-fold ensemble p is less
  extreme than single-fold OOF p (p_par 99th pct 0.83 vs 0.90), so any threshold must be re-calibrated for the ensemble
  before a probe. Parity kernel exp46_divins_parity (ENABLE=0) running on Kaggle.- 2026-09-24 00:40 UTC L2 v1 STEAL sub-test: SELECTION best cap 4, threshold 0.5, steal on -> +0.0058 (TP 7 -> 13, FP 15 -> 25);
  one CONFIRMATION run -> +0.0019 (TP 16 -> 20, FP 28 -> 39, 90% CI [-0.0007, +0.0050]; 44b6 +0.0015, 6bba +0.0021; 124 of
  466 insertions were steals). Fails the gate narrowly (+0.002, CI > 0, added-fork precision 4/15 = 27% < 31%). KEY
  ARITHMETIC for the public board: with J_pub ~0.36 already, an added fork helps only if its precision > J/(1+J) ~ 0.265;
  v1's 27% is break-even, so even a perfect transfer would move the public score by ~0. v2 must lift precision to >= 0.45
  for a visible public gain (+0.002 needs about +5 net public TP at that precision - more than the public test holds).- 2026-09-24 00:30 UTC PARITY PASS: exp46_divins_parity (exp39 + --patch divinsert, DIVINS_ENABLE=0) submission.csv is
  sha256-identical to exp39's (86ba0334...). The patch is an exact no-op when disabled, and the whole pipeline is
  deterministic run to run (so the takaito 0.948 vs our 0.944 gap was not run noise but a different code/version).
  Local edge-error decomposition (exp39, 199 videos): edge TP 122,151 / FP 6,846 / FN 6,732 (J 0.900); errors split ~50/50;
  annotated node recall 0.983.- 2026-09-24 01:30 UTC DaughterNet v2 TRAINED (kdn-train v3: 17,143 GT + 11,117 pool rows at predicted coords; ~25 min).
  Pool block OOF (the one that matters, real candidates): parent-vs-cont AUC 0.875 (v1 on the same rows 0.825; 44b6 0.950,
  6bba 0.859), daughter-vs-cont 0.743 (v1 0.718); gate roles: p_par parent vs cont-as-u 0.84, p_dau daughter vs cont-as-v
  0.68 (weakest link). GT block parent AUC 0.841 (v1 0.848). Rescoring the 1M exported nodes with v2 (kdn-score v2).
  Friend A pushed L5 (b7b7629/1905ac6: full-res DaughterNet-B on his 5070 Ti, 14-22 h, OOF by 25 Sep 20:00 UTC); his edits
  to shared files are backward compatible (tests pass).- 2026-09-24 02:00 UTC PROBE 26 SCORED: exp45 (exp29 with safe divisions OFF, zero forks) = 0.911 public. So our PUBLIC
  division Jaccard J_pub = (0.947 - 0.911) / 0.1 = 0.36 (+-0.04 from 3-decimal rounding), exactly pawanmali's ablation.
  Precision floor for added forks P_min = max(0.15, J/(1+J) + 0.05) = 0.31; break-even precision J/(1+J) = 0.265.- 2026-09-24 02:10 UTC DaughterNet v2 on SELECTION is WORSE for insertion than v1 despite the better pool AUC: best orphan
  +0.0010 (v1 +0.0044), best steal cap 6 t 0.5 +0.0032 (v1 cap 4 t 0.5 +0.0058). All L2 deltas on 64 videos are 1-4
  division events, i.e. inside noise. Running: v1+v2 averaged p grid on SELECTION; L4 weak-leaf pruning port + grid
  (workflow wf_7ffe6fd4-8a4, laptop CPU, selection then one confirmation run).- 2026-09-24 03:10 UTC L4 weak-leaf pruning (seyitkaangunes 035 prune_weak_leaf_nodes, ported verbatim; knob 0.2-0.4 identical
  because tail edge_prob is either 0.0 (relink pairs the network never scored) or >= 0.4): SELECTION +0.0005, CONFIRMATION
  +0.0006 (CI [+0.0004, +0.0009]; 44b6 +0.0010, 6bba +0.0005; NO video worse among 199; node ratio -0.05%). Real but tiny;
  fails the pre-registered +0.002 gate. v1+v2 averaged p: not better than v1 on SELECTION. Ensemble-threshold calibration
  (eligible-count matching on SELECTION): OOF threshold 0.5 ~ ensemble 0.4.
  PROBES PREPARED (decision taken autonomously while the user sleeps; slots are otherwise unused; finals policy unchanged -
  none of these is a final unless it also passes its gate): exp47 = exp39 + leaf prune 0.3; exp48 = exp47 + DaughterNet v1
  insertion with steal (cap 4, alpha 1, ens threshold 0.4, dump on). Both kernels running; submit when complete.- 2026-09-24 09:15 UTC L5 EDGE ANATOMY -> BIGGEST LOCAL WIN OF THE COMPETITION (agent run, d379138). Per-edge TP/FP labels of the
  final exp39 graph on 199 videos match the official totals exactly (122,151 / 6,846). The motion relink REPLACES the ILP
  edge set; 92,952 of its edges join pairs the edge network NEVER scored (edge_prob 0.0), and among evaluable ones they are
  79% FP (584 TP / 2,172 FP); the subset where the ILP linked the source or the target elsewhere is 89-94% FP. Filter
  ef_a3_rl_pr (drop unscored relink edges with ILP evidence elsewhere, re-link to the ILP's free alternative, prune isolated
  nodes, never touch forks): SELECTION +0.0147 [+0.0107, +0.0196]; ONE CONFIRMATION run +0.0162 [+0.0128, +0.0196], 44b6
  +0.0145, 6bba +0.0169, gain on 61% / 80% of videos, edge FP 3,657 -> 2,735, divisions unchanged. GATE PASS.
  RISKS: (1) the linker was trained on all 199 videos, so trusting the ILP's choice is in-sample (relink-off lost 0.002 on
  the LB; the targeted subset is different, but only a probe decides); (2) the lab cache was built with tight gate 6.0, the
  kernel runs 5.5 (9.5% of the drop set differs). PROBES: exp49 = exp39 + ef_a3_rl_pr; exp50 = exp39 + drop-only ef_a0
  (SELECTION +0.0095; depends only on the "never scored" property, a transfer hedge). Kernels pushed.
- 2026-09-24 10:50 UTC RESUME POINT (context compaction by the user; read this first).
  PROBES today (24 Sep UTC; 1 slot left today): #27 exp47 = exp39 + leaf prune 0.3 (id 56510844) = **0.947** (tie with exp29,
  consistent with its tiny +0.0006 local). #28 exp48 = exp47 + DaughterNet v1 insertion with steal (id 56510845) PENDING.
  #29 exp49 = exp39 + edge filter ef_a3_rl_pr (id 56518035) PENDING - THE KEY PROBE (lab confirmation +0.0162). #30 exp50 =
  exp39 + drop-only edge filter ef_a0 (id 56518039) PENDING (transfer hedge). Kernel stats confirmed both filters ran
  (exp49 dropped 389/178/29/1613 edges on the dummy clips and re-linked most; exp50 dropped 407/435/62/2307).
  DECISION TREE when #29/#30 score: exp49 >= ~0.951 -> edge filter is the new base (then bundle with leaf prune, division
  insertion if #28 not worse, re-tune at tight 5.5); exp50 > exp49 -> use drop-only; both <= 0.947 -> filter's local gain
  was in-sample (edge network trained on the 199 videos), close the line.
  RUNNING IN BACKGROUND (notifications will arrive): (a) agent rebuilding the lab cache at MOTION_RELINK_TIGHT_UM 5.5 (the
  kernel's value; friend A's cache was built at 6.0) into data_external/friend_a_cache_t55/ and re-measuring exp39 +
  both filters there; (b) agent doing the FALSE-NEGATIVE anatomy (why 6,732 GT links are missing: detection miss / track
  break / swap / dropped ILP edge) with an optional stitching rule (--patch stitch) under the selection->confirmation
  protocol, files experiments/l2_daughternet/edge_anatomy/fn_anatomy.py; (c) workflow wf_62b09e11-ae9 (3 hypothesis
  generators -> dedupe -> 5 web researchers -> adversarial judge) for more metric ideas toward the user's target
  0.97 +- 0.005; (d) ONE browser agent (the only one allowed to use Chrome) reading all Kaggle discussions/code of this
  competition and external tracking literature -> research/browser_research_2026-09-24.md.
  KEY TOOLS: lab = experiments/l2_daughternet/replay/replay.py (--cache data_external/friend_a_cache/friend_a_b20_exp29_
  friend_c/cache/friend_a_b20_exp29, --split selection|confirmation|all, config keys insert/ins.*, leaf_prune, ef.*);
  kernel builder tools/build_probe_kernel.py with --patch gshift|divinsert|leafprune|edgefilter (all exact no-ops when off);
  edge anatomy experiments/l2_daughternet/edge_anatomy/ (+ parquet .public_local_cache/l2_edge_anatomy/edges_exp39.parquet).
  Friend A: L5 full-res DaughterNet-B running on his 5070 Ti (OOF due 25 Sep 20:00 UTC); told about the edge finding.
  Finals (tick by 29 Sep 20:00 UTC): currently exp29 (56146538) + exp39 (56440312); will change if #29 transfers.
- 2026-09-24 11:20 UTC: probe #28 exp48 (exp47 leaf prune + DaughterNet v1 insertion with steal) = **0.948**, our best
  public score (+0.001 over exp47 0.947 / exp29 0.947; consistent with the lab's +0.0019 for the insertion part). exp48
  replaces exp29 as a finals candidate. #29/#30 still pending. FN-anatomy interim (exp39 + ef graph, 199 videos, FN 6099
  validated against the official scorer): swaps 25% of FN (oracle +0.032), never-detected-link 31%, u-diverted/v-taken
  ~19% (oracle +0.016); a stitch rule (end->start, ILP edge) adds +0.0020 on top of ef on confirmation (44b6 gains on
  only 15% of videos -> fails the per-embryo 55% gate as is).
- 2026-09-24 12:10 UTC, LAPTOP CRASH RECOVERY: the laptop froze at ~11:37 UTC and was power-cycled; all background
  agents died. The ideas workflow wf_62b09e11 had produced NOTHING (2 of 3 generators failed at start with an API 403),
  relaunched as wf_eee39a44-20b from experiments/workflows/biohub-idea-research.js, now CRASH-SAFE: every agent writes
  notes + its final JSON to research/wf_ideas/ and re-uses an existing JSON on restart. The browser agent, the 5.5
  rebuild agent (all 199 ckpts at 5.5 done; DivNet stage pending, reuse 6.0 scores where unchanged) and the FN-anatomy
  agent were resumed with their context, limited to 2 workers. All python processes run at Idle priority (background
  loop) so the user's own work on the laptop keeps priority. OFFLOAD: an agent is porting the replay lab to Kaggle CPU
  kernels (tools/kaggle_lab.py: push-code / run / pull / status; 4 vCPU, 30 GB, no GPU quota) - GPU does not speed up
  the lab (ILP/Hungarian/scoring are CPU-bound) and free Colab gives only 2 vCPU; Colab stays a GPU reserve.
- 2026-09-24 12:30 UTC, BROWSER AGENT RESULT (research/browser_research_2026-09-24.md): public notebook
  anvithpothula/biohub-x138 = **0.953** (gold, 21 Sep; missed by earlier Code-tab scans) = thtennant frontier947-readmit
  (0.946) + ONE change: the "V1284" coordinate-refinement head (MLP 224->32->3 on frozen UNet features at each peak,
  shift <= 2 um; removes the int16 rounding so coords stay sub-voxel; the edge transformer gathers features at the
  refined point by trilinear interpolation). Weights: public CC0 dataset anvithpothula/biohub-v1284-head-s075. 33
  teams sit at exactly 0.953 (x138 copies). Forum: detector retraining gave a top-3 team most of the gain; divisions
  need ~3 um accuracy; stricter min-track-length looked +0.013 offline, -0.004 public (node multiplier). ACTIONS: agent
  porting the head as --patch coordhead -> exp51 = exp48 + coordhead (private GPU kernel; submission needs the user's
  OK). Ideas workflow replaced by a larger crash-safe one, wf_d8ae74be-bcd (9 lenses x 4 hypotheses -> dedupe to <= 14
  -> web research each -> 3 skeptics each (transfer, arithmetic, feasibility) -> completeness critic -> round 2 ->
  synthesis), all outputs in research/wf_ideas_v2/ (FINAL_REPORT.md at the end).
- 2026-09-24 13:10 UTC, BROWSER PASS 2 (research/browser_research_2026-09-24_pass2.md): no public notebook above 0.953;
  41 teams at exactly 0.953 (x138 reproduces). x138 authors privately at 0.959 (thtennant, rank 32) and 0.956. V1284
  head training is not public, but it is reconstructable from x138's own VALIDATOR block: run with V1284_MODE=capture
  on train movies (N per embryo prefix; the author used 20 movies = 4,136 peak<->GT pairs), target = GT - peak in um,
  z-scored 224-d features, ridge/MLP, output norm-bounded < 2 um; V1284_MODE=zero = float coords + trilinear gather with
  no shift (free control). Other teams' datasets: plain detector retrain on 199 stays 0.947 (leonixis); GT-to-detection
  median offset 1.72 um (p90 3.3). Next ideas ranked: (1) exp51 probe; (2) retrain the head on all 199 movies (~10x
  data; hold out by embryo); (3) swap repair where it arises (score unscored relink pairs with the edge net, 2-opt swap
  test on a multi-frame cost; literature: KTH-SE Viterbi re-routing, MAMHT k-best); (5) DaughterNet as a parent/daughter
  constraint for division precision (linajea: -88% FP divisions); (7) short-track-filter guard.
- 2026-09-24 13:25 UTC, BUDGET MODE (user's Claude limits: 5-h window 78% used, resets ~15:25 UTC; weekly 76%, resets
  25 Sep): 5.5 lab-rebuild agent STOPPED (probe 29 answers the transfer question directly; its scripts stay in
  experiments/l2_daughternet/relink55/, the 199 ckpts at 5.5 in data_external/friend_a_cache_t55/). Ideas workflow
  wf_d8ae74be-bcd trimmed: after the 9 hypothesis agents finish it is resumed from the edited script (6 researched
  hypotheses, one adversarial judge-synthesizer, no per-idea skeptics, no critic round). Still running: x138 port
  (exp51 kernel), FN anatomy / swap rule, Kaggle CPU lab port, probe monitor.
- 2026-09-24 13:35 UTC, USER OVERRIDE: research has priority - the ideas workflow wf_d8ae74be-bcd runs at FULL size
  (9 lenses -> <= 14 researched -> 3 skeptics each -> critic round 2 -> synthesis; the trim was never applied to the
  running instance, the script file is restored for crash resume). To free budget the Kaggle-CPU-lab port agent is
  PAUSED (resume via SendMessage later; laptop lab at Idle priority works meanwhile).
- 2026-09-24 13:45 UTC, FN ANATOMY FINAL (experiments/l2_daughternet/edge_anatomy/l6_fn_anatomy_report.md): SWAPS ARE NOT
  LINKING ERRORS. In swaps the GT link is normal (median 2.6 um) but its two matched predicted nodes are 9.4 um apart;
  our links there are short and smooth (~1.5 um, p ~0.76; motion prefers ours in 98.6%); swap endpoints match GT at
  4.4/4.7 um vs 1.8 um for correct edges: the annotated nucleus sits BETWEEN two of our tracks and the 7 um matching
  picks track A at t and B at t+1 (u_diverted / v_taken: same, one-sided). A 2x2 re-assignment rule (--patch swapfix,
  sw.*) = -0.00004 on confirmation, FAIL. => the ~2,700 swap/diverted FN (oracle +0.03-0.046) are a NODE-POSITION
  problem: coordinate head (x138), retraining it on 199, near-duplicate track merging. STITCH (--patch stitch, st.*;
  re-add ILP end->start edges after the edge filter): confirmation +0.0021 CI [+0.0016, +0.0026], 44b6 +0.0012, 6bba
  +0.0025, but 44b6 win rate 15.5% (59/71 videos unchanged, 11/12 changed gain) -> fails only the win-rate criterion,
  which cannot be met by an add-only sparse rule; candidate to bundle with the edge filter if probe 29 transfers
  (build: --patch edgefilter --patch stitch --set STITCH_ENABLE=1 ...). Open: linefit moves 354 GT-matched nodes beyond
  7 um (displacement cap untested, needs new tails). The ideas workflow was resumed with this correction in its brief
  for all post-hypothesis stages (9 hypothesis sets cached), script experiments/workflows/biohub-idea-hunt-v2.js.
- 2026-09-24 16:30 UTC, exp51 READY (not submitted): kernel vitaliineibauer/biohub-exp51-coordhead v1 COMPLETE, 1,713 s,
  valid submission = exp48 + --patch coordhead (x138's V1284 head verbatim: 224->32->3 MLP, shift <= 2 um, float coords,
  trilinear gather incl. the secondary model; knobs COORDHEAD_ENABLE, COORDHEAD_MODE=candidate|zero|capture; ENABLE=0
  byte-identical to exp48). Pre-ILP coordinates and raw ILP counts identical to x138's own run. Head moved 143,633
  peaks, mean 0.74 um, max 1.61 um. Final nodes 122,704 -> 119,174 (-2.9%, mostly 44b6_0b24845f -10.7%; x138 shows the
  same drop vs its parent, so part of its +0.007 may be the node multiplier -> private-board risk), forks 58 -> 56.
  x138 vs our base otherwise: flow-prior relink (raw-distance cost 0), readmit, gap filler, DeepCenter 0.25, ILP timeout
  1200 s, runtime guard (each neutral alone on LB). The CSV writer rounds coords (int(round())), also in x138: z
  refinements < 0.81 um are lost at output - float output coordinates are an open idea. Head retraining recipe on 199
  videos: capture mode -> Hungarian match to GT (<= 4 um) -> target (gt-det) um clipped < 2 -> Linear-SiLU-Linear with
  zero-init last layer -> movie/embryo-held-out folds (experiments/ext_x138/DIFF.md).
- 2026-09-24 16:40 UTC: probe #30 exp50 (exp39 + drop-only edge filter ef_a0, lab SELECTION +0.0095) = **0.946**, i.e.
  -0.001 vs exp39 0.947: the "unscored relink edges are 79% FP" pattern does NOT transfer to the test embryo as a
  drop rule (most likely an in-sample artefact: on train the edge network / ILP are near-perfect, so relink edges that
  disagree with them look wrong; on test they are not). Bad omen for #29 (full filter with ILP re-link, still
  pending): if #29 <= 0.948 the edge-filter line is closed and the lab's in-sample optimism is ~+0.01 for anything
  that trusts the ILP/edge network - lab gains of that type must be discounted accordingly.
- 2026-09-24 16:55 UTC: probe #29 exp49 (exp39 + full edge filter ef_a3_rl_pr, lab CONFIRMATION +0.0162, gate PASS)
  = **0.947**, a tie with exp39. EDGE-FILTER LINE CLOSED (and the stitch bundle that depended on it). Lesson, now
  quantified twice: rules that override the relink with the ILP / edge network look +0.01..+0.016 locally and give 0 on
  LB (in-sample network). Lab gains are only trustworthy for changes that do NOT lean on network confidence (e.g. float
  output coordinates, which change no topology). Finals candidates now: exp48 (0.948) and, if it scores, exp51.
- 2026-09-24 17:09 UTC: probe #31 exp51 (exp48 + x138 coordinate head) SUBMITTED with the user's OK, id 56527239
  (5/5 slots used on 24 Sep UTC). Next day (25 Sep, 5 slots): float output coordinates on top of the best (lab +0.0018,
  3/3 skeptics survive; server parser risk = parse error, not silent loss), then the workflow's synthesis picks.
- 2026-09-24 18:00 UTC, IDEAS WORKFLOW v2 DONE (76 agents; research/wf_ideas_v2/FINAL_REPORT.md + final.json): of 36
  hypotheses / 16 researched, KEPT: (1) float output coordinates, "safe" encoding (w = round(v) + frac clipped to
  0.499, 3 decimals; a truncating parser still gets round(v)): lab +0.0019 on 199 videos, both embryos, topology and
  divisions identical -> expected public +0.001 (0..+0.002), P(no harm) ~0.97; (2) finals rule: diversify F2 as a
  private hedge (edge filter + stitch on the best base) - 0 on public by construction; (3) overlap consensus across
  overlapping TEST crops (transductive; needs the USER's rules/spirit approval; ~+0.0005, only if the public embryo
  is 44b6-type); (4) fork-midpoint filter +0.0003..0.0008; (5) head retrain on 199 ~+0.0003 (gated on probe 31 and a
  COORDHEAD_MODE=zero probe). Critic findings: the loss is a DENSITY problem (densest 6bba quartile = 52% of the loss,
  Spearman(J, nodes/frame) = -0.66); a_never FN in 44b6 are mostly under-segmentation (Ultrack has ~44% more
  interior points); linefit displacement cap, neighbour repulsion, border rules, snapping to Ultrack = dead ends.
  HONEST OUTLOOK: expected public ~0.955 (sd 0.002), optimistic ceiling ~0.962; 0.965-0.975 needs +0.017..0.027,
  more than the sum of all post-processing ceilings (+0.014) - the top teams got there by MODEL RETRAINING (detector
  localisation / density). Agent building --patch floatout -> exp52 = exp51 + float(safe), exp53 = exp48 +
  float(safe) (private kernels, for the 25 Sep batch).
- 2026-09-24 18:20 UTC, USER APPROVED the 25 Sep batch: P32 = exp52 (exp51 + float output coords, safe encoding),
  P33 = exp53 (exp48 + float safe), P34 = exp54 (exp51 with COORDHEAD_MODE=zero; control: shift vs float geometry) ONLY
  if probe 31 (exp51) >= 0.951. exp52/exp53 are submitted right after 00:00 UTC once their kernels are COMPLETE (both
  go in regardless of #31; order by #31 if it has scored). Remaining 2 slots need a new OK. Detector retrain declined
  on arithmetic (1 run = ~23 h on the 5070 Ti + edge-net + own head; our earlier all-199 retrain = 0.920; others'
  retrains 0.947-0.950). Head retrain on 199 (~1-1.5 days, ~+0.0003..0.002) only if #31 >= 0.951 and exp51 - exp54
  >= 0.002; then prepare friend A's capture script + prompt.
- 2026-09-24 18:40 UTC: user agreed to the V1284 head RETRAIN on all 199 train videos, KAGGLE path, starting now
  (not waiting for #31): agent builds a sharded capture kernel (exp51 stack, COORDHEAD_MODE=capture, train videos),
  tools/train_coordhead.py (Hungarian <= 4 um to GT, target (gt-det) um < 2, 224->32->3 zero-init last layer; eval
  held out by leak group AND by embryo vs the public head; kill test: >= 3% lower matched distance on BOTH embryo
  directions and no loss of 7 um matches), pilot on 6 videos, then the full run (<= ~12 GPU h, 2 sessions), then
  exp55 = exp51 + COORDHEAD_HEAD_PATH (new knob) - build only. Files: experiments/coordhead_retrain/. Colab kept in
  reserve (it would need the competition data + the user's own kaggle.json upload).
- 2026-09-24 22:00 UTC, FLOATOUT READY: --patch floatout (BIOHUB_OUTPUT_FLOAT_COORDS=0|safe|float; mode 0 sha256-identical
  CSV; in-kernel polars re-read check "FLOATOUT CHECK PASSED"); replay key out.coords. Private kernels COMPLETE:
  exp52 = exp51 + float safe (vitaliineibauer/biohub-exp52-coordhead-floatout v1), exp53 = exp48 + float safe
  (vitaliineibauer/biohub-exp53-leafprune-divins-floatout v1): nodes/edges/forks and ids identical to their bases,
  floor(w) == base integer on 100% of nodes (a truncating parser reads exactly the base CSV). Lab SELECTION (64 6bba):
  e48_safe vs e48 = +0.00248 CI90 [+0.00105, +0.00390], 24 wins / 10 losses among 34 changed videos, divisions identical.
  exp54 (exp51 with COORDHEAD_MODE=zero) = CSV BYTE-IDENTICAL to exp48 -> its LB is 0.948 by construction, NO slot
  needed: float geometry + trilinear gather alone change nothing; exp51 - exp48 is entirely the head's shift. The 25 Sep
  batch is therefore exp52 + exp53 at 00:01 UTC (2 slots), 3 slots left for later decisions (need a new OK).
- 2026-09-24 21:05 UTC: user (going to sleep until ~10:00 MSK) approved: submit exp52 + exp53 at 00:01 UTC, and exp55
  (retrained head) at my discretion if its kill test passes; conserve token budget until 07:00 UTC (no workflows).
- 2026-09-24 ~23:00 UTC, HEAD RETRAIN ON 199 = KILL TEST FAIL, exp55 NOT built/submitted. Capture 199/199 (7.2 GPU-h,
  deterministic; public head on our features -10..13% distance = convention OK). Leak-group OOF: new head P 1.238 um
  vs public 1.525 (-18.9%), but mostly bias removal (z residual +0.40 -> +0.02 um). Embryo-held-out: 6bba->44b6 P +12.0%
  WORSE than public (learns 6bba's annotation z-offset), 44b6->6bba +0.2%; debiased Q also worse (+6.3% / +1.3%).
  Public head (balanced ~10+10 videos) transfers better; the hidden test is other embryos -> keep the public head.
  Files: experiments/coordhead_retrain/out_full_P|Q/, tools/train_coordhead.py.
- 2026-09-25 00:02 UTC: probes #32 exp52 (id 56534391) and #33 exp53 (id 56534401) SUBMITTED (3 slots left on 25 Sep).
- 2026-09-25 00:39 UTC: probe #31 exp51 (exp48 + x138 V1284 head) = **0.950**, NEW BEST (+0.002 over exp48 0.948; x138
  gained +0.007 on its own 0.946 base, so the head overlaps with our leaf prune / DaughterNet gains or part of x138's
  gain was its node drop). exp51 becomes finals candidate F1 (with exp48 as the fallback). #32/#33 (float) pending.
- 2026-09-25 07:50 UTC: #32 exp52 (exp51 + float safe) = 0.950 (tie with exp51), #33 exp53 (exp48 + float safe) = 0.948
  (tie with exp48): float output coordinates are harmless but invisible on the public LB (server rounds, or gain < 0.0005).
  WHY exp51 = 0.950 while x138 = 0.953: we never ran x138 itself - exp51 is OUR base (sjlee v020 + tight 5.5 + DivNet
  veto + leaf prune + DaughterNet) + x138's head. x138's base is thtennant's chain (flow-prior relink with raw cost 0
  and a 7 um tight gate, readmit of discarded peaks, sub-threshold gap filler, DeepCenter 0.25, ILP timeout): alone it
  scored 0.946, but those stages all consume node POSITIONS, so the head's refined coordinates make them work (+0.007);
  on our plain relink the head adds only +0.002. Pre-ILP coordinates of exp51 == x138 exactly, so the gap is post-ILP.
  Next: x138 verbatim as the new base (+ our DaughterNet insertion on top).
- 2026-09-25 08:00 UTC: user approved 2 probes: P34 = exp56 = x138 VERBATIM on our account (same docker pin + machine
  shape; pushed, vitaliineibauer/biohub-exp56-x138-verbatim v1) and P35 = exp57 = x138 + DaughterNet insertion (+ leaf
  prune 0.3 if clean), agent building via a --base x138 option in tools/build_probe_kernel.py. Submit each when COMPLETE.
- 2026-09-25 08:15 UTC: tools/build_probe_kernel.py gained --base x138 (base = experiments/exp56_x138_verbatim; only
  divinsert/leafprune allowed; no patches -> byte-identical to exp56; exp39 builds unchanged). exp57 (x138 + divinsert +
  leafprune) runs, but leaf prune on x138 conflicts with READMIT (readmitted peaks are relinked with edge_prob 0.0, so a
  readmitted track end is a leaf < 0.3 and gets pruned) -> P35 will be exp57b = x138 + DaughterNet insertion ONLY
  (vitaliineibauer/biohub-exp57b-x138-divins-only; one change vs exp56). exp57 v1 output kept only as a diagnostic.
- 2026-09-25 08:40 UTC, exp57 DIAGNOSTIC (x138 + leaf prune + insertion; not submitted): runs clean (no REPAIR FAILED,
  repair_fallback 0), pre-tail identical to exp56 (121,777 raw nodes, 1,337 readmitted). Leaf prune removes 513 leaves,
  >= 479 of them READMITTED nodes (36% of readmit) - confirms prune undoes readmit on x138, so exp57b (insertion only)
  is the right P35. Insertion on x138: 12 forks added (5 steals) over 4 test clips, forks 62 -> 74 (0 eligible on
  44b6_0b24845f). Compare script: scratchpad/cmp57.py (out_exp56 downloaded).
- 2026-09-25 10:20 UTC ===== RESUME POINT (user may continue in a NEW CHAT; read this block first) =====
  LB (public): best = 0.950 = exp51 (exp48 + x138 V1284 coordinate head; probe 31) and exp52 (exp51 + float output,
  probe 32). exp48 = 0.948 (exp39 + leaf prune 0.3 + DaughterNet v1 insertion; probe 28). Closed today: edge filter
  (#29 0.947, #30 0.946), float output coords (#32/#33 ties), head retrain on 199 (kill test fail: learns 6bba z offset).
  PENDING on the LB (submitted 25 Sep): #34 = exp56 = anvithpothula/biohub-x138 VERBATIM on our account (id 56545267,
  expect 0.953; author's own score, 41 teams reproduce it) and #35 = exp57b = x138 + DaughterNet v1 insertion only (id
  56545786; +12 forks, nodes/coords identical to exp56). 1 slot left on 25 Sep UTC; 5 per day after. Scoring latency
  7-10 h.
  DECISION RULES when #34/#35 score: #34 == 0.953 -> x138 is the new base; #35 > #34 -> x138 + insertion is F1. If #34 <
  0.953 -> environment difference (like takaito 0.948 -> 0.944): compare the kernel logs with x138's, keep exp51 as F1.
  Do NOT add leaf prune on x138 (it removes readmitted nodes: 479 of 513 pruned leaves were readmit's). Float output is
  harmless (optional in finals). Every new submission needs the user's explicit OK (memory project-lb-probe-approval).
  FINALS (user ticks 2 by 29 Sep 20:00 UTC): F1 = best of {exp57b, exp56, exp51/exp52}; F2 = a structurally different
  hedge (e.g. exp51 if F1 is x138-based, since the post-ILP stages differ) - workflow finals-emax-diversify rule.
  Honest outlook (ideas workflow v2, research/wf_ideas_v2/FINAL_REPORT.md): ~0.955 expected, ceiling ~0.96; 0.97 needs
  model retraining (detector localisation), not realistic before 29 Sep.
  TOOLS: tools/build_probe_kernel.py (exp39 base: --patch leafprune|divinsert|edgefilter|stitch|swapfix|gshift|coordhead|
  floatout; --base x138: only divinsert|leafprune; all patches exact no-ops when off; --push); lab
  experiments/l2_daughternet/replay/replay.py (in-sample! trust only changes that do not lean on the edge network/ILP;
  the division-insertion line did transfer: lab +0.0019 -> LB +0.001); coordinate-head capture/training
  experiments/coordhead_retrain/ + tools/train_coordhead.py; ideas workflow experiments/workflows/biohub-idea-hunt-v2.js
  (crash-safe, outputs research/wf_ideas_v2/); browser reports research/browser_research_2026-09-24*.md.
  KERNELS on Kaggle (private): exp51 biohub-exp51-coordhead, exp52 -floatout, exp53, exp54 (== exp48 bytes), exp56
  biohub-exp56-x138-verbatim, exp57 (x138+prune+ins, diagnostic only), exp57b biohub-exp57b-x138-divins-only.
  FRIEND A: PC rebooted 24 Sep, L5 DaughterNet-B dropped; told to WAIT for #34 and, if 0.953, build a lab cache on the
  x138 stack (experiments/exp56_x138_verbatim) for tuning the division insertion on the new base (PROMPT_FRIEND_A.md top
  block). No commits from him since 24 Sep 04:12 MSK. GPU quota: Kaggle resets 26 Sep 00:00 UTC.
  Paused: tools/kaggle_lab.py (Kaggle CPU lab port, unfinished). Idea needing the user's rules decision: overlap
  consensus across overlapping test crops (transductive; recommended NOT to do).
- 2026-09-25 11:40 UTC, BROWSER INTEL for the cloud session's ideas workflow v3 (branch claude/practical-meitner-31k9ye,
  research/wf_ideas_v3/browser_intel.md, worktree ../biohub-browser): no public notebook > 0.953 (kunaldesale2408 = x138
  copy; "0.951" haideptry = 0.944; seyitkaangunes 0.946). LB 11:27 UTC: 241 teams at 0.953, 0.954: 47, 0.955: 28,
  0.956: 19; we are #460 (0.950). Forum: imissher 743222 (25 Sep) - 8 LB probes all lost, det thresholds 0.960/0.970
  worse; hikaggler 741749 - synthetic pretraining 0.9146 -> 0.9269 hold-out, node count predicts LB better than recall;
  Zebrahub ZSNS001/003 + Ultrack tracks exist as Kaggle datasets (giorgosi relays). RUNTIME RISK (agent's estimate from
  logs): x138 GPU phase ~265 s/clip on 2 shards -> ~7.4 h for ~199 hidden clips, right at x138's 7.5 h repair
  deadline (after it relink/gap/safe-div/linefit are switched off); exp57b's DaughterNet insertion roughly DOUBLES the
  repair time (491 s vs 227 s on the dummy clips) and ignores the deadline flag -> exp57b may degrade or time out on
  the hidden run. If #35 errors or scores < #34, that is the likely cause; any insertion-on-x138 final must respect the
  deadline flag.
- 2026-09-25 13:20 UTC, IDEAS WORKFLOW v3 DONE (user target 0.99 by 29 Sep; cloud session, 11 lenses x 4 ideas, 2
  skeptics each = 44 ideas / 88 verdicts, + browser intel from a local Chrome session, + merge / completeness critic /
  two independent plans / final judge; ~120 agents). Everything in research/wf_ideas_v3/: BRIEF.md, browser_intel.md
  (LB 11:00 UTC: top 0.975, 6 teams >= 0.970, 39 >= 0.960, 401 >= 0.953, 241 exactly 0.953 = x138 copies, we ~456;
  no public notebook > 0.953), h_*.json / v_*.json, s_*.json, FINAL_REPORT.md (Russian), task cards TASK_LOCAL_SESSION /
  TASK_CLOUD_SESSION / TASK_FRIEND_A / TASK_FRIEND_C / TASK_COLAB.md; scripts experiments/workflows/biohub-hunt-v3.js
  and biohub-plan-v3.js. VERDICT: 0.99 and 0.97 are out of reach by 29 Sep (every retraining path refuted for the
  window, 10/10 skeptics); expected public ~0.954 (P>=0.955 ~0.25, P>=0.96 ~0.02). Main new risk: RUNTIME on the hidden
  set (~199 clips per the Data tab): x138 GPU phase ~7.4 h at dummy speed vs REPAIR_DEADLINE_S 27000 s, after which
  relink/readmit/gaps/safe divisions/linefit are switched off for later (alphabetical) clips; exp57b's DaughterNet
  insertion is NOT gated by the deadline and doubles repair time. Plan backbone: K2 = exp58 = x138 + safetail (deadline
  34200 s, insertion gated + fail-soft, DIVINS_DUMP=0) + lowrefine (head coords for readmitted peaks) + insertion per
  rule R2; then forkmid (K3) and a DeepCenter threshold chosen on 6bba (K3b; DeepCenter trained on 44b6 only). F1 must
  not be byte-identical to x138 (241-team tie block spans the medal cutoffs); F2 = exp52 by default. PROPOSED
  PRE-REGISTRATION (branches A-E on #34/#35 score + latency, rules R1-R10, finals rule) = FINAL_REPORT.md sections e/f;
  binding only after the user's OK. Other corrections: metric weights videos by TP+FP+FN; our kernels are deterministic,
  so the 0.003 "LB noise" does not apply to them; swap FN are not reachable by localisation.
- 2026-09-25 13:38 UTC, PRE-REGISTRATION v3 (USER OK in chat "даю да" at ~13:37 UTC, BEFORE any score of #34/#35 was visible; the
  poll log experiments/lb_poll/poll.log shows both still PENDING). User decisions on FINAL_REPORT §h: (1) rules §e/§f
  below are binding; (2) S1 = exp57 v1 diagnostic allowed today AFTER both #34/#35 scores are visible, before 23:30 UTC;
  (3) K2 pre-approved for ~00:55 UTC 26.09 if the dummy gates (§e) are green (K1 only in branches C/D); (4) ~5 GPU-h for
  the exp60 lab on 26.09 approved; (5) standing OK for riders K3 (forkmid), K3b (DeepCenter t*), K4 (tempfuse) and an N1
  build if R6 fires - each only after its gates pass; (6) M3 (dense labels -> secondary detector) = NO (recommendation;
  consistent with 7); (7) refusals confirmed: no detector/edge/head retraining before 29.09, no N2 test-size probe, no
  overlap consensus on test crops, no axis-flip on x138; (8) honest goal accepted: public ~0.954, private above the
  241-team x138 block; (9) user ticks F1/F2 manually by 29.09 20:00 UTC (reminder 12:00). Rules copied verbatim from
  research/wf_ideas_v3/FINAL_REPORT.md (§e, §f) - apply mechanically, do not rewrite:
  ## (e) План слотов (21) с ветками и правилами — ПРЕДРЕГИСТРАЦИЯ

  Слоты: 1 на 25.09 и по 5 на 26–29.09, сброс в 00:00 UTC. Каждый сабмит — только с явного OK пользователя (ночью по
  предодобрению). Ядра детерминированы: повторов не делаем, неиспользованные слоты не сжигаем.

  **Имена сборок** (строит облачная сессия через `tools/build_probe_kernel.py --base x138`):
  - **K2 = exp58**: x138 + safetail (E1) + lowrefine (E2) + [вставка по R2].
  - **K1 = exp58t**: двойник K2 с `LOWREFINE_ENABLE=0`, то есть x138 + safetail + [вставка]. Его дамми — проверка
    sha256; сабмитится только в ветках C/D.
  - **FD = exp58fd**: K1 с `REPAIR_DEADLINE_S=1` (проверка пути деградации). Только дамми, никогда не сабмитится.
  - **FF = exp58ff**: K1 с `DIVINS_FORCE_FAIL=1` (проверка fail-soft вставки). Только дамми; можно отложить до окна
    26.09 ~09:00, сабмит K2 от него не зависит. В ветке без вставки не нужен.
  - **K3 = exp59** = K2 + forkmid. **K3b = exp59dc** = K3 (или K2) + `DEEPCENTER_SAFE_DIV_THRESHOLD=t*`.
  - **K4 = exp61** = текущий стек F1 + tempfuse. **exp60** = лаборатория E4. **exp62** = N1 (parrepair).

  **Слоты**
  | Слот | Когда (UTC) | Что | Условие |
  |---|---|---|---|
  | S1 | 25.09, после появления счетов #34 и #35, до 23:30 | exp57 v1 (готовая версия) — диагностика leaf prune на x138; никогда не финал | по желанию пользователя |
  | S2 | 26.09 ~00:55 | K2 | дамми K2 и K1 прошли ворота (§e «Ворота дамми») |
  | S3 | 26.09 ~00:55 | K1 | только ветки C/D; иначе держим и отдаём под K3b |
  | S4 | 26.09 ~10:00–13:00, после счёта K2 | K3 = K2 + forkmid | аудит E4 пройден; иначе пусто, K3 → S7 |
  | S5 | 26.09 ~11:00–14:00 | K3b (порог DeepCenter t*) | дуга 6bba прошла ворота E5; иначе пусто |
  | S6 | 26.09 ~18:00 | K4 (tempfuse) или сборка с N1 по триггеру | дамми прошёл; иначе пусто |
  | S7 | 27.09 ≤ 12:00 | сдвинувшийся K3/K4, или наездник leaf prune (если E9 дал Δ ≥ +0.002, пересобрать на стеке K с C01) | — |
  | S8 | 27.09 | перенос наследника x138 | только по триггеру E10 |
  | S9 | 27.09 | кандидат F2 на C01, если вариант заработал его по R4 и ещё не оценён с C01 | иначе пусто |
  | S10–S11 | 27.09 | резерв: повтор упавшей сборки K или пересборка с N1, если задержка > 9.5 ч | — |
  | S12 | 28.09 ≤ 12:00 | консолидация F1-final | только если принятые наездники в разных файлах; ворота = объединение ворот их дамми |
  | S13 | 28.09 ≤ 16:00 | повтор S12 при ошибке | — |
  | S14 | 28.09 | наследник x138 по позднему триггеру | — |
  | S15–S16 | 28.09 | не используются | — |
  | S17 | 29.09 ≤ 02:00 (жёсткий край 10:00) | аварийный повтор F1-final | только если сборка 28.09 упала или не прошла R5 |
  | S18–S21 | 29.09 | не используются | — |

  **Ветки по #34/#35** (вероятности — догадки из `s_plan_robust.json`)
  - **A (P ~0.55):** a = 0.953, b ≥ a, L35 ≤ 8.5 ч. K2 с вставкой; S3 держим. (L34 влияет только на R1/R5/R6.)
  - **B (P ~0.2):** a = 0.953, b = a − 0.001. K2 без вставки (отличие от x138 даёт C05, позже C04).
  - **C (P ~0.1):** b ≤ a − 0.002 или #35 с ошибкой.
    - Если L35 > 7.5 ч или ошибка, это конфаунд времени, а не вред DaughterNet. S2 = K2 без вставки, S3 = K1
      (x138 + вставка с гейтом + C01) как чистый перетест. Вставка возвращается со сборки K3, только если K1 ≥ a.
      Если #35 упал или вышел по таймауту, строим N1.
    - Если L35 ≤ 7.5 ч, вставка действительно вредна: убираем её, S3 держим.
  - **D (P ~0.1):** a ≤ 0.952.
    - Если L34 > 7.5 ч, таймер сработал на public в нашем прогоне. S2 = K1' (x138 + C01, без вставки и lowrefine),
      он должен воспроизвести 0.953. S3 = K2. Строим N1.
    - Если L34 ≤ 7.5 ч, отличие окружения. S2 = K1' как проверка воспроизведения, логи сравнить с x138. Запасной F1 =
      exp52, пока сборка семейства x138 не наберёт ≥ 0.953.
  - **E (P ~0.05):** #34 в 20:30 ещё без счёта. Собираем по плану, в 00:55 сабмитим K2 без вставки, о вставке решаем,
    когда появится #35. Строим N1 (R6).

  Шпаргалка по порогам времени: 7.5 ч = #34 до 15:39, #35 до 16:03; 8.0 ч = #34 до 16:09; 8.5 ч = #35 до 17:03 UTC.

  **Правила решений**
  - **R1 база (a).** a = 0.953 и L34 ≤ 7.5 ч: x138 — база, и #34 доказанно не деградирован (время работы ≤ задержке).
    a = 0.953 и 7.5 < L34 ≤ 8.0 ч («жёлтая зона»): база подтверждена, но любой финал семейства x138 — только сборка с
    C01, удовлетворяющая R5, а F2 = exp52 обязательно. a = 0.953 и L34 > 8.0 ч: то же, плюс N1 (R6). a ≤ 0.952: ветка D.
  - **R2 вставка (b).** Вставка входит в стек F1, если b ≥ a и b оценён. Ничья тоже засчитывается «за»: на private
    точка безубыточности 0.11–0.20 против 0.265 на public (`s_merge.json` C03 и assumptions_adjudicated), и вставка отличает F1 от x138.
    b = a − 0.001: без вставки. b ≤ a − 0.002: без вставки, если только чистый перетест K1 ≥ a (ветка C). Используется
    только конфигурация #35; без «лестниц» и сеток порогов.
  - **R3 безвредные наездники** (C01, C05, C04: узлы не меняются, или меняются только координаты). Принимаем, если ворота
    дамми пройдены и public ≥ предыдущий стек − 0.001. При −0.002 и хуже наездник убираем и больше не пробуем. Наездник,
    прошедший лабораторные ворота, не убираем из-за −0.001.
  - **R4 менятели множества узлов или вилок** (порог DeepCenter, tempfuse, leaf prune, наследники, ручки readmit).
    Δ к текущему кандидату F1: +0.002 и выше → в F1; 0 или +0.001 → кандидат F2; −0.001 и ниже → закрыт.
    Никогда не принимаем только по лабораторному приросту.
  - **R5 допуск к финалам по времени.** Файл допускается, если он оценён без ошибки И выполнено одно из двух.
    (а) Задержка ≤ его REPAIR_DEADLINE_S: 7.5 ч для сборок типа x138/exp57b, 9.5 ч для сборок с C01.
    (б) Прогноз шага 0 показывает, что таймер не сработал, с запасом ≥ 1 ч.
    Файлы с вставкой без гейта (#35, exp57) при L > 7.5 ч не допускаются. exp51/exp52 без таймера допускаются всегда.
    Задержка — только по нашему опросу раз в 10 мин; если ночью опроса не было, пункт (а) не доказан и смотрим (б).
  - **R6 триггер N1.** Строим parrepair (E8) раньше E4/E7 и везём его на K3, если выполнено любое из условий:
    - L34 > 8.0 ч;
    - #35 упал или вышел по таймауту;
    - L35 > 8.5 ч, а вставка остаётся в стеке;
    - прогноз шага 0 для F1 > 9.0 ч.

    Иначе N1 не строим.
  - **R7 гигиена.**
    - Валидатор и PP-sweep x138 в сабмите всегда выключены: на скрытом перезапуске они оценивают другие стемы (imissher, 743222).
    - DIVINS_DUMP=1 в сабмите не бывает.
    - Каждая новая стадия fail-soft.
    - Первая проверка любого наездника — тождество числа узлов (для tempfuse допуск ±1%).
    - Между почти-копиями не выбираем по разнице 0.001, кроме как через R3.
  - **R8 сроки.** Новые механизмы — до 27.09 12:00 UTC. Консолидация F1-final — до 28.09 12:00. После 29.09 02:00
    только аварийный повтор (жёсткий край 10:00).
  - **R9 не делаем:** N2 (зонд размера скрытого теста), консенсус по перекрывающимся тестовым кропам (трансдуктивно),
    переобучение детектора/рёбер/головы к 29.09, лестницы ручек на public, axis-flip на x138. N2 — только как последний
    запасной вариант. Условия: N1 провалил дамми к 27.09, задержки оставляют N в 130–170, и пользователь явно разрешил
    зондировать метаданные.
  - **R10 приоритет часов агента:** E1 > предрегистрация > E2 > сборка E4 > E3 > шаг 0 > (N1, если R6) > анализ E4/E5 >
    E7 > E12. Безопасная дорожка (E1, E2) должна быть в git до начала любого кода «лунных» ставок.

  **Ворота дамми** (проверяет локальная сессия перед каждым сабмитом)
  1. K1-двойник: sha256 submission.csv == дамми exp57b (с вставкой) или exp56 (без неё). В логе нет строк `DEADLINE`,
     `DIVINS FAILED`, `REPAIR FAILED`.
  2. K2:
     - в логе есть `Low-detection dump applied`;
     - число пиков в строке `LOWDET <name>: N` по клипам равно exp56;
     - сырых узлов 121 777;
     - возвращено (readmit) 1 337 ± 10%, gapfill ± 10%;
     - жёсткий провал при любой из строк `LOW-DETECTION DUMP SKIPPED`, `gap filler idle`, `invalid V1284 displacement`,
       `REPAIR FAILED`, `LOWREFINE FAILED`;
     - финальных узлов ±0.3% по клипу;
     - по сравнению с K1 меняются только readmit/gapfill-узлы и их рёбра.
  3. FD: `DEADLINE` на датасете 1; вставка пропущена (`DIVINS SKIPPED (deadline)`, 0 вставок); безопасные деления и
     linefit остались (их счётчики в логе > 0); CSV валиден; нет `REPAIR FAILED`.
     FF: `DIVINS FAILED` на каждом клипе, sha256 CSV == дамми exp56 (вставка откатилась, остальное не тронуто).
  4. K3: узлы == K2, вилки сняты только там, где середина ≥ 4.5 мкм.
  5. K3b: множество узлов == K3, меняются только вилки.

  Предварительная арифметика шага 0 (догадка; облако уточнит по логам).
  - Входы: GPU-фаза ~281 с на клип на шард, 2 шарда, то есть ~140 с на клип; старт ~560 с; починка x138 ~57 с/клип,
    exp57b ~123 с/клип (`browser_intel.md` §6.0B, §6.11).
  - exp51 (та же GPU-фаза, хвост тяжелее, без таймера) оценён за ≤ 7.5 ч (`CONTEXT.md`: 24.09 17:09 → 25.09 00:39).
    Если его починка ~100–120 с/клип, то N ≲ 100–110.
  - Тогда x138 заканчивает за ~5.7–6 ч (безопасно), а exp57b — впритык к 27 000 с. Поэтому вставку гейтим, а дедлайн
    поднимаем.
  - Если шаг 0 покажет N ≥ 150 или починку exp51 ≤ 60 с/клип, прогнозы пересчитываются, и R6 может сработать.

  ## (f) Правило выбора финалов F1/F2 (к 29.09 20:00 UTC, отмечает пользователь вручную)

  **F1** — самая полная накопительная сборка семейства x138 (K2 → K3 → K3b/K4 → F1-final), которая одновременно:
  (i) оценена без ошибки; (ii) допущена по времени (R5); (iii) содержит C01; (iv) **не побайтная копия x138**;
  (v) каждый наездник в ней прошёл R3/R4. Более простой файл заменяет её, только если он выше на public на ≥ +0.002.
  Запасной порядок, если выбранная сборка не проходит условия:
  1. предыдущая K в стеке;
  2. K1 (если оценён);
  3. #35 (только если R2 включает вставку и L35 ≤ 7.5 ч);
  4. #34 (только если L34 ≤ 7.5 ч; это копия x138, крайний случай);
  5. exp52.

  **F2 = exp52** (exp51 + дробный выход, public 0.950, `experiments/RESULTS.md` проба 32). Другой хвост после ILP и нет
  таймера, поэтому exp52 страхует и перенос на private, и время. Вместо exp52 берём вариант семейства x138, только если
  выполнено ВСЁ:
  - public(F1) ≥ 0.954;
  - время доказанно комфортное: L34 ≤ 7.5 ч и задержка самой F1 ≤ 9.5 ч;
  - вариант прошёл честные ворота (дуга E4 на 6bba для порога DeepCenter или ворота дамми tempfuse);
  - вариант оценён с public ≥ F1 − 0.001;
  - множество узлов или вилок у варианта отличается от F1.

  Обоснование: итог на private = max(F1, F2), поэтому F2 — бесплатная опция. Премия E[(F2 − F1)+] у exp52 ~+0.0002…+0.0005
  (`v_ensembles-and-private_finals-private-emax-x138-era_value.json`), у вариантного F2 ~+0.0004 (догадка). exp52 плюс к
  этому единственный страхует мир «таймер сработал на private».

  Ветка D (x138 у нас не воспроизводится): F1 = exp52 (или exp51), F2 = лучшая допущенная по времени сборка семейства
  x138 с C01.

  Никогда не отмечать exp56 (x138 без изменений) и два файла с одинаковыми компонентами. Автовыбор Kaggle взял бы две
  лучшие по public почти-копии, поэтому отмечать только вручную.
- 2026-09-25 13:58 UTC, BROWSER CHECKS (TASK_LOCAL_SESSION §4, read-only): (1) TIES: Rules §3.7.b "In the event of a tie, the
  Submission that was entered first to the Competition will be the winner" (https://www.kaggle.com/competitions/
  biohub-cell-tracking-during-development/rules) - so a late byte-copy of x138 ranks at the END of the 0.953 block;
  public-LB tie order officially undocumented. (2) RUNTIME LIMIT = 12 h (Overview -> Code Requirements: "GPU Notebook
  <= 12 hours run-time"), not 9 h. Error classes (https://www.kaggle.com/code-competition-debugging): "Notebook
  Timeout", "Notebook Threw Exception", "Submission CSV Not Found", "Submission Scoring / Format Error", "Notebook
  Exceeded Allowed Compute", "Kaggle Error"; errored submissions count toward the daily limit. #34/#35 showed
  "Notebook Running" (hidden rerun still in progress ~6 h after submission). (3) GPU QUOTA: Settings shows "Kaggle GPU
  18:56 / 30 hrs" (11 h 04 m left); reset weekly, per a 2020 staff post Saturday 00:00 UTC (= 26 Sep 00:00, unconfirmed
  in current docs). Hidden-test reruns reportedly do NOT count against the quota (community answers only, unverified).
- 2026-09-25 14:29 UTC, T2/T3/T5/T6 DONE AND MERGED INTO main (local session; workflow wf_0b307a70-4af: 4 implementers in isolated
  worktrees + 4 independent reviewers, all "ok_to_merge", minor remarks only). Full suite: `python -m pytest tests` = 69
  passed; K2 and K3 render and all cells compile after the merge.
  - T2 --patch lowrefine (x138 only): pool rows with score >= 0.965 get _v1284_refine coords (same features as the main
    peaks), 0.5-0.965 stay on the grid, int16 cast removed (float32), BIOHUB_LOWREFINE_ENABLE (0 = byte-identical
    dump), fail-soft 'LOWREFINE FAILED', log 'LOWREFINE <clip>: refined R of N lowdet peaks'. tests/test_lowrefine.py.
  - T6 --patch forkmid (x138 only): last graph edit; safe-division forks (not div_inserted) removed when |P-(c1+c2)/2|
    >= 4.5 um; drops the ILP-side edge if edge_prob == 0.0 else the added edge; nodes untouched; FORKMID_ENABLE default 0;
    fail-soft 'FORKMID FAILED'; counters forkmid_*. tests/test_forkmid.py.
  - T3 tools/forkmid_dose.py (+test). Dummy dose: exp56 62 forks, 2 >= 4.5 um (3.2%; both in 6bba_05db0fb1); exp57b 74
    forks, 5 >= 4.5 um (the 62 base forks give the same 2; inserted forks 3/12 but C04 excludes them). Verdict per the
    pre-registered T3 rule: neither a no-op (0%) nor a stop (> 15%) -> C04 continues to the exp60 audit.
  - T5 exp60 lab: --patch trainlab (--lab only; DIVINS_DUMP=1 now needs --lab on every base), tools/trainlab.py (split,
    CPU tail-arm replay through the notebook's own code, official scoring, gates), tools/trainlab_io.py. Split written
    BEFORE any run: experiments/exp60_trainlab/split.json = 56 clips (44b6 17 = one per leak group, 11 GT divisions;
    6bba 39, 88 divisions; 20 probable x138 head stems + 4 dummy twins excluded), SELECTION/CONFIRMATION 28/28, shards
    A/B 28/28. Kernels built (NOT pushed): experiments/exp60_trainlab/kernel_a, kernel_b, kernel_b_sasyami. Push after the
    GPU quota reset (26.09 00:00 UTC): `python -m kaggle kernels push -p experiments/exp60_trainlab/kernel_a` (+ kernel_b).
    ~2 h per shard. Known minor gaps (reviewer): DeepCenter score recorder and the TRAINLAB summary cell are not
    fail-soft (a recorder exception sends that clip to the REPAIR FAILED fallback in the LAB only); 7 of 17 44b6 picks
    are leak-siblings of excluded stems.
  BUILD COMMANDS FOR 26.09 (T4; run from the repo root, never --push from the builder):
  # run from the repo root after merging this branch; knob names without BIOHUB_; never --push from here
  K="--set DIVINS_ENABLE=1 --set DIVINS_STEAL=1 --set DIVINS_CAP=4 --set DIVINS_FRAME_CAP=1 --set DIVINS_ALPHA=1 --set DIVINS_THRESH=0.4 --set DIVINS_DUMP=0"

  ## Branch A (insertion per R2; #35 config). K1 = K2 twin with LOWREFINE_ENABLE=0 (notebooks differ in ONE cell-0 line)
  python tools/build_probe_kernel.py exp58_x138_safe_lowref --base x138 --patch divinsert --patch safetail --patch lowrefine $K --set REPAIR_DEADLINE_S=34200 --set DIVINS_DEADLINE_S=28800 --set LOWREFINE_ENABLE=1 --note "K2: x138 + safetail + lowrefine + divinsert (#35 config)"
  python tools/build_probe_kernel.py exp58t_x138_safe --base x138 --patch divinsert --patch safetail --patch lowrefine $K --set REPAIR_DEADLINE_S=34200 --set DIVINS_DEADLINE_S=28800 --set LOWREFINE_ENABLE=0 --note "K1: K2 twin, lowrefine off"
  python tools/build_probe_kernel.py exp58fd_x138_safe --base x138 --patch divinsert --patch safetail --patch lowrefine --lab $K --set REPAIR_DEADLINE_S=1 --set DIVINS_DEADLINE_S=28800 --set LOWREFINE_ENABLE=0 --note "FD dummy only"
  python tools/build_probe_kernel.py exp58ff_x138_safe --base x138 --patch divinsert --patch safetail --patch lowrefine --lab $K --set REPAIR_DEADLINE_S=34200 --set DIVINS_DEADLINE_S=28800 --set LOWREFINE_ENABLE=0 --set DIVINS_FORCE_FAIL=1 --note "FF dummy only"
  # expected probe.json change (A-K2): DIVINS_ENABLE 1, STEAL 1, CAP 4, FRAME_CAP 1, ALPHA 1, THRESH 0.4, DUMP 0, REPAIR_DEADLINE_S 34200, DIVINS_DEADLINE_S 28800, LOWREFINE_ENABLE 1, DEGRADE_KEEP_DIV 1, PATCHES divinsert+lowrefine+safetail; 14 code cells; datasets = x138's 4 + vitaliineibauer/biohub-ft-weights. K1 same with LOWREFINE_ENABLE 0; FD REPAIR_DEADLINE_S 1 + "lab"; FF + DIVINS_FORCE_FAIL 1 + "lab".

  ## No insertion (branch B; C: S2; E: the 00:55 K2; D: S3 when R2 says no insertion). Drop --patch divinsert and all DIVINS_* (DIVINS_DEADLINE_S needs divinsert). FF is not needed.
  python tools/build_probe_kernel.py exp58n_x138_safe_lowref --base x138 --patch safetail --patch lowrefine --set REPAIR_DEADLINE_S=34200 --set LOWREFINE_ENABLE=1 --note "K2 (no insertion): x138 + safetail + lowrefine"
  python tools/build_probe_kernel.py exp58nt_x138_safe --base x138 --patch safetail --patch lowrefine --set REPAIR_DEADLINE_S=34200 --set LOWREFINE_ENABLE=0 --note "K1 (no insertion): twin, lowrefine off"
  python tools/build_probe_kernel.py exp58nfd_x138_safe --base x138 --patch safetail --patch lowrefine --lab --set REPAIR_DEADLINE_S=1 --set LOWREFINE_ENABLE=0 --note "FD (no insertion) dummy only"
  # expected change: REPAIR_DEADLINE_S 34200, LOWREFINE_ENABLE 1|0, DEGRADE_KEEP_DIV 1, PATCHES lowrefine+safetail; 12 code cells, only cells 0/4/5 differ from exp56; datasets = x138's 4.

  ## Branch C (b <= a-0.002 or #35 error): S2 = exp58n_x138_safe_lowref; S3 (only if L35 > 7.5 h or #35 error) = exp58t_x138_safe (branch A's K1: x138 + gated insertion + C01, lowrefine off). If L35 <= 7.5 h: same as B, S3 held.
  ## Branch D (a <= 0.952): S2 = K1' = x138 + C01 only (no insertion, no lowrefine patch):
  python tools/build_probe_kernel.py exp58p_x138_c01 --base x138 --patch safetail --set REPAIR_DEADLINE_S=34200 --note "K1': x138 + C01 only (reproduction check)"
  #   change: REPAIR_DEADLINE_S 34200, DEGRADE_KEEP_DIV 1, PATCHES safetail; only cells 0 and 5 differ from exp56. S3 = K2 by R2 (exp58_... if b >= a else exp58n_...).
  ## Branch E (#34 unscored at 20:30): build both sets; 00:55 submit exp58n_x138_safe_lowref (with OK), insertion decided when #35 appears.
  K3 = K2 + forkmid: add `--patch forkmid --set FORKMID_ENABLE=1` to the K2 line (name exp59_x138_k3).
  K2 DUMMY GATE CORRECTION (reviewer of T2; FINAL_REPORT §e gate 2 read literally would fail a correct K2): keep the
  hard gates 'Low-detection dump applied'; LOWDET N == exp56 per clip; 'LOWREFINE <clip>: refined R of N' with N ==
  LOWDET N, R > 0, failed frames 0; no 'LOWREFINE FAILED' / 'LOW-DETECTION DUMP SKIPPED' / 'REPAIR FAILED'; raw nodes
  121,777; readmit and gapfill counts within +-10%; final nodes within +-0.3% per clip; K1 sha256 check. The "only
  readmit/gapfill nodes and their edges differ from K1" condition becomes a SOFT check (relink/linefit knock-on on main
  nodes is expected).
- 2026-09-25 14:37 UTC: #34 exp56 (x138 verbatim): 0.953, first seen 14:36:36Z (still PENDING at 14:26:33Z), submitted
  08:09:00Z -> L34 in (6.29, 6.46] h <= 7.5 h. R1: x138 is the base AND #34 is proven non-degraded (runtime <= latency
  < REPAIR_DEADLINE 7.5 h). x138 reproduces on our account (unlike takaito). #35 still pending (7.5 h mark = 16:03Z,
  8.5 h = 17:03Z).
- 2026-09-25 16:20 UTC: #35 exp57b (x138 + DaughterNet insertion, #35 config): **0.954** (our best; +0.001 over x138).
  Latency bounds: last seen PENDING 15:16:44Z, first seen COMPLETE 16:16:55Z (the five polls 15:26-16:06Z got EMPTY CLI
  output), submitted 08:33:25Z -> L35 in (6.72, 7.73] h (the 7.5 h mark is NOT provable; poller now retries on empty
  output and logs stderr). BRANCH per §e: a = 0.953, b = 0.954 >= a, L35 <= 8.5 h -> **BRANCH A**: K2 = exp58 WITH the
  insertion (R2), S3 held. R6 (N1): L34 <= 6.46 h (not > 8.0), #35 no error, L35 <= 7.73 h (not > 8.5) -> NOT triggered
  (step-0 forecast pending). R5 note: #35 itself (ungated insertion) is admissible as a final fallback only if L35 <=
  7.5 h, which is unproven -> #35 is not a finals candidate; K2 (gated, C01) is. S1 used: P36 = exp57 v1 diagnostic
  (x138 + leaf prune 0.3 + ungated insertion; id 56555189, submitted 16:18:09Z; never a final); read by R4 with
  delta = #36 - #35 (>= +0.002 -> leaf prune rider on 27.09; |delta| <= 0.001 -> closed; <= -0.002 -> confirms readmit
  must stay); ignore if L36 or L35 > 7.5 h.
- 2026-09-25 16:45 UTC, T7 STEP 0 (experiments/runtime_step0/step0.md): hidden N <= ~97-106 clips at dummy speed
  (from L34 <= 6.46 h, L35 <= 7.73 h); the hidden rerun covers public+private in ONE run, so latencies already include
  private. K2 forecast <= ~7.8 h (< 9.5 h repair deadline, < 8.0 h insertion gate at the worst case) -> R6 NOT triggered,
  no N1. #35's own x138 7.5 h deadline may have degraded its last clips if its runtime exceeded 7.5 h (unprovable).
  Dummies K2 (vitaliineibauer/biohub-exp58-x138-safe-lowref) and K1 (biohub-exp58t-x138-safe) pushed at ~16:35 UTC
  (GPU quota 11 h left before the reset), FD/FF queued after them, so K2 can go at 00:00 UTC if the gates pass.
- 2026-09-25 17:20 UTC, DUMMY GATES (tools/dummy_gates.py, FINAL_REPORT §e with the K2 correction): K2 = exp58
  (vitaliineibauer/biohub-exp58-x138-safe-lowref v1), K1 = exp58t, FD = exp58fd: **16/16 PASS**. K1 sha256 == exp57b
  dummy (ef0eff86...) -> safetail is inert while no deadline fires; K2: 'Low-detection dump applied', LOWDET == exp56 per
  clip, LOWREFINE refined 26,532/27,877, 33,336/51,793, 7,370/8,518, 76,396/81,321 peaks with 0 failed frames, no
  hard-fail lines, raw nodes 121,777, readmitted 1,365 vs 1,337 (+2%), gapfill 111 vs 110, final nodes vs K1
  +0.004% / +0.118% / 0 / +0.013%; FD: 'DEADLINE: 975s ... safetail keeps safe divisions + linefit', insertion skipped
  on 4 clips, safe_div 76 and linefit 116,807 kept, CSV valid. FF still running (not required for the K2 submit).
  -> K2 goes at 00:01 UTC 26 Sep (pre-approved). exp60 lab shard A pushed at 17:15 UTC with this week's remaining quota
  (~9 h left before the expected Saturday reset), shard B queued after FF, so the forkmid / DeepCenter-threshold audit
  (T9) can be done tonight instead of 26 Sep morning.
- 2026-09-25 17:45 UTC: FF dummy (exp58ff, DIVINS_FORCE_FAIL=1) 2/2 PASS: 'DIVINS FAILED' on all 4 clips and the CSV is
  byte-identical to exp56 (d52a5da2...) -> the insertion's fail-soft path restores the input graph exactly. All
  dummy gates for K2 are green (18/18).
- 2026-09-25 17:55 UTC, NIGHT PLAN (user asleep; standing OK given in chat: "запускай каждые 2-3 часа ресерчеров ...
  заранее даю добро на их действия"): research rounds every ~2.5 h via experiments/workflows/biohub-research-round.js
  (args round/since/focus; browser delta of the competition page, plan check, new hypotheses on a rotating focus,
  re-check of old closed ideas, one skeptic per idea, REPORT.md), all logged in research/wf_ideas_v4/round<N>/. Round 1 =
  the running v4 workflow (FINAL_REPORT_v4.md). Round 2 at ~19:45 UTC, then ~22:15, ~00:45, ~03:15, ~05:45. Submissions
  at night stay within existing approvals: K2 at 00:01 UTC (18/18 dummy gates green); riders K3/K3b/K4/N1 only after
  their gates pass (exp60 lab running now).
- 2026-09-25 18:05 UTC: KNOWLEDGE CURATOR added (user request): experiments/workflows/biohub-curator.js runs after every
  research round (called from biohub-research-round.js) and can run standalone. It maintains research/KNOWLEDGE/:
  INDEX.md (1-page state + map), IDEAS.md + ideas.json (every idea ever proposed, clustered, with status and sources;
  ORPHANS = proposed but never tested/closed), FACTS.md (+ contradictions), DECISIONS.md (all LB probes, decisions by rule,
  finals candidates, R1-R10 status), WATCHLIST.md (overdue / next 24 h / later / insights at risk of being forgotten),
  CHANGES.md (delta per curation). Writes only there; alerts go to the main session. First standalone curation right
  after the v4 workflow finishes.
- 2026-09-25 18:20 UTC: research round 1 (workflow v4, 52 agents; research/wf_ideas_v4/FINAL_REPORT_v4.md) done. Its lab and finals
  amendments are recorded below VERBATIM before any exp60 output is downloaded or scored (no exp60 output on disk).
  The user is asleep: [OK] items (L1, L3, L4 as R3 class, f2) are COMPUTED alongside but the ORIGINAL rules decide until
  the morning OK. Intel at 18:08 UTC: we are #151 of 3,905 at 0.954; score blocks 0.957 = ranks 66-77, 0.956 = 78-98,
  0.955 = 99-133, 0.954 = 134-195, 0.953 = 196-456 (261 teams); silver ~rank 195 (end of the 0.954 block), bronze ~390
  (inside 0.953); within one displayed score the order follows the unrounded score. No public notebook > 0.953.
- 2026-09-25 18:20 UTC, PRE-REGISTRATION v3 ADDENDUM L (lab reading of exp60; written before any exp60 output was
  downloaded or scored; source research/wf_ideas_v4/FINAL_REPORT_v4.md). Items marked [OK] take effect only with the
  user's morning OK; until then the original T9 text applies. Both versions are computed and reported.
  L1 [OK, clarification] DeepCenter plateau (T9 "M1"): neighbours = non-control grid neighbours of t* (the control 0.25
     has delta 0 by definition); i.e. trainlab 'pass_noncontrol_plateau', ANDed with L2.
  L2 [bug fix + tightening] "precision of added forks >= 0.35" is computed over EVALUABLE new forks only
     (TP/(TP+FP) on 6bba CONFIRMATION; trainlab _fork_precision currently divides by all new forks). Added AND clauses:
     n_evaluable_added >= 6 and one-sided Wilson 80% (z = 1.2816) lower bound > 0.265. Existing checks stay (conf >=
     +0.002 at t*, plateau per L1, 44b6 >= -0.0005, forks <= +50%, nodes unchanged). t* > 0.25: no build (removal
     branch unreachable). Report (info only) the share of marginal forks that fall in the forkblob cell (L4).
  L3 [OK, power fix] forkmid C04 audit, pooled over all 56 clips: 0 TP safe-division forks removed; removed evaluable
     FP >= 3; <= 1 lab TP fork with midpoint in [3.8, 4.5) um (replaces the max-margin clause); pooled adj_edge delta
     >= -0.0002; nodes and inserted forks unchanged. The '>= 1 FP on 44b6' clause is dropped (lambda_44b6 ~0.1-0.4).
     Sensitivity (lab base has no lowrefine): the gate must still pass when fork rows touching a readmitted lowdet node
     are counted as adverse. exp39's 0/23 is never used in any bound (4.5 um was chosen on it).
  L4 [rule frozen now; R3 class needs OK] forkblob: for every 2-child fork with safe_division == 1 and not
     div_inserted, at t+1: sister distance <= 5.0 um AND valley >= 0.95, valley = min of the interior 20-80% of 41
     samples of the gaussian-blurred (sigma zyx 0.6/1.5/1.5 vox, local crop, margin >= 4 sigma) intensity on c1->c2,
     divided by min(I(c1), I(c2)); drop the ILP-side edge if edge_prob == 0.0 else the added edge; runs after
     forkmid; nodes untouched. Lab harm gate (pooled 56 clips): vetoed evaluable TP <= 1 and (TP == 0 or FP >= 3*TP);
     pooled div_J(arm) >= control; >= 10% of control safe-division forks fall in the cell (dose); pooled adj_edge
     delta >= -0.0002; nodes unchanged. Log per vetoed fork: dropped edge, its edge label, the fork's division label.
     Thresholds come from GT sister statistics of all 151 train divisions (no fork labels seen). Prior: on the old
     base (exp39 graphs, 199 clips) the cell holds 3 FP / 0 TP / 65 free; probe 18 (pre-link 5 um floor) tied 0.946 vs
     0.947 -> an LB tie is not a failure, +0.001 is not a confirmation.
  L5 ins35 / ins35_nosteal0 / ins35_forkmid45 arms are 'IN-SAMPLE UPPER BOUND (4/5 DaughterNet v1 folds saw these
     clips)'; the T9 insertion check is a warning only; nosteal0 is CLOSED under R2 whatever the lab shows.
  L6 [conditional] 6bba extension: only if the 39-clip 6bba bed passes the full E5 gate (L1+L2), push the 78 clean
     6bba clips outside exp60 (17 GT divisions; the 10 head-train stems incl. 05db0fb1 excluded; honest pooled bed
     105 divisions) as 2 shards after the K3/twin dummies; veto K3b if the pooled 6bba CONFIRMATION+EXT delta at t* < 0
     or the evaluable new-fork precision < 0.35. Result not in by 10:00 UTC 26 Sep -> decide on the 39-clip bed.
  L7 closures: RE-AIM on x138/K2 = no-op (K2 dummies: 2 of 117,077 edges re-pointed; TP/FP/FN 2,047/101/80 with and
     without it); pair-GBM relink bonus closed (in-sample booster; reopen only on a full-stack public delta >= +0.002
     or an honest OOS check); E13/C08 closed on schedule (R8) plus small ceiling (5/82 end-anchored node misses);
     births/optional nodes stay closed on the LB anchors (gapfill 0, readmit -0.001, det 0.95 flat, MIN_TRACK_LEN 4
     -0.002), not on the anatomy share. FD dummy 0.9249 vs K1 0.9180 locally is an in-sample artefact (one clip
     +0.023; probes 21/29 show this 'trust ILP over relink' pattern gives 0 or less on LB): never act on it.
- 2026-09-25 18:20 UTC, PRE-REGISTRATION v3 AMENDMENT f2 [needs the user's OK]: F2 = exp58n (x138 + safetail + lowrefine = K2 minus the
  DaughterNet insertion; no fork riders) if scored without error, R5-admissible and public >= 0.953; its dummy gate:
  tools/dummy_gates.py --insertion 0, node rows (id column stripped) == K2 dummy, edges differ from K2 only at K2's
  inserted/steal forks, no DIVINS/DEADLINE/REPAIR FAILED/LOWREFINE FAILED lines. exp52 only if the twin is unscored,
  failed, or in branch D. A DeepCenter/tempfuse variant that R4 makes an 'F2 candidate' does not displace the twin.
  The twin's score never reopens R2 unless twin - K2 >= +0.002 (R7). The S12 consolidated file joins the candidate
  set; earlier scored K files stay candidates. §f fallback item 4 (#34) stays as the last resort before exp52 ('never
  tick exp56' applies while any admissible non-copy x138-family file exists). Never tick two files with identical
  components. The finals objective is P(private > raw x138) first, silver second.
- 2026-09-25 19:05 UTC, v4 AMENDMENT CODE MERGED (workflow wf_9606c7ef-11e; 3 implementers + 3 reviewers; full suite 112
  passed): tools/trainlab.py ADDENDUM L gates (additive; results.md prints "Decisions: ORIGINAL T9 vs ADDENDUM L"; in
  force now: forkmid = ORIGINAL T9 until the user's OK for L3; DeepCenter K3b = strict plateau AND L2; insertion = L5
  warning-only), tools/forkblob_lab.py + --patch forkblob (x138 only; FORKBLOB_ENABLE default 0; fail-soft), and
  tools/runtime_ledger.py (A5; the poller now refreshes experiments/lb_poll/ledger.md each cycle; poller restarted).
  Reviewer minors kept as known limits: Wilson z = 1.2816 is the ADDENDUM's constant (one-sided 90% quantile, labelled
  "80%" in the text) - applied as written; the new gate code is not wrapped fail-soft (a crash stops the lab report, not a
  kernel); vacuous passes when an aggregate row is NaN are flagged in the report.
- 2026-09-25 19:05 UTC, CURATOR (research/KNOWLEDGE/, first run "v4") ALERTS HANDLED: (a) RESULTS.md probe 25 fixed to
  0.946; (b) P36 READING RULE (recorded BEFORE P36 scores): L35 is only bounded to (6.72, 7.73] h, so "L35 > 7.5 h" is
  unprovable; conservative reading = P36 is INFO ONLY and cannot trigger a leaf-prune rider (no rider from P36 even if
  delta >= +0.002; leaf prune on x138 stays closed); (c) metric notes: adjusted edge J is weighted per video by TP+FP+FN
  (official code; s_merge brief_corrections) and the node multiplier is linear without a kink - the older §4 wording is
  superseded; the "+-0.003 LB noise" of §11a does not apply to our deterministic kernels (a 0.001 public step between our
  kernels is real on the public embryo; transfer to private is the open question); (d) R7 "DIVINS_DUMP=1 never in a
  submission" applies to NEW builds; exp48/51/52/57b were scored with dumps (they only write files) and stay admissible;
  (e) closed explicitly: tools/kaggle_lab.py (paused, superseded by the exp60 x138 lab), stage-resume idea (safetail
  covers the failure modes); (f) K4 tempfuse has no owner: default = DROPPED (S6 empty) unless a night research round
  finds a strong reason before 26 Sep 12:00 UTC; (g) orphans I-081 (DaughterNet as a precision veto on safe-division
  forks) and I-072 (divergence/symmetry gates with float coords) and the density-quartile report column -> handed to the
  night research rounds as candidate free CPU arms on the exp60 dumps.
- 2026-09-25 18:41 UTC: TIMESTAMP CORRECTION - the two entries above stamped "2026-09-25 19:05 UTC" were written at ~18:40 UTC (manual stamp error). exp60 lab shards A and B still RUNNING.
- 2026-09-25 20:05 UTC, exp60 LAB DUMPS: both shards COMPLETE (A 6,959 s, B 5,599 s kernel time; 28 + 28 clips written, missing [],
  failed_hooks 0), downloaded to _dl/exp60_a, _dl/exp60_b (not in git). FORKBLOB (ADDENDUM L4) LAB GATE = FAIL
  (tools/forkblob_lab.py score -> experiments/exp60_trainlab/results_forkblob.json): vetoed 150 forks (evaluable TP 1,
  FP 6, ignored 143), dose 22% of 676 control safe-division forks, pooled div_J 0.1290 -> 0.1271 (check
  div_J(arm) >= control FAILS), adj_edge +0.00006, score delta -0.00013, nodes unchanged. -> forkblob CLOSED (not in K3);
  no user OK needed. Main T9 score (forkmid, DeepCenter threshold arc, insertion arms) is running.
- 2026-09-25 20:35 UTC, exp60 T9 LAB READ (python tools/trainlab.py score, 56 clips, official metric; experiments/exp60_trainlab/
  results.md / results.json). DECISIONS (pre-registered; original and ADDENDUM L both computed):
  - forkmid (K3): ORIGINAL T9 = FAIL, ADDENDUM L3 = FAIL -> NO K3. Pooled: 676 eligible safe-division forks, 40 removed,
    removed TP 0, removed evaluable FP 1 (39 unevaluable), TP mid max 3.65 um (6bba); pooled score delta +0.00013,
    division Jaccard +0.0010, adj_edge +0.00002 -> the sign is favourable but the ">= 3 evaluable FP" power clause fails.
    forkmid stays closed for the LB (no ladder on public).
  - DeepCenter safe-division threshold (K3b): t* = 0.30; conf >= +0.002 FALSE, plateau (strict and non-control) FALSE,
    44b6 >= -0.0005 FALSE, precision FALSE -> NO K3b (S5 empty).
  - insertion (#35 config): lab 44b6 +0.0157, 6bba +0.0090 (ins35_nosteal0: 0.0000 / +0.0071) - IN-SAMPLE UPPER BOUND
    (L5, warning-only), consistent with R2 keeping the insertion in K2.
  - forkblob: FAIL (see the entry above).
  CONSEQUENCE: F1 stack = K2 (x138 + safetail + lowrefine + insertion) unless a later mechanism passes; S4/S5 on 26 Sep
  have no rider. The exp58n twin dummy (AMENDMENT f2 candidate) was pushed now (GPU free) so the morning OK can be
  acted on at once.
- 2026-09-25 20:55 UTC, NIGHT RESEARCH ROUND 2 DONE (research/wf_ideas_v4/round2/REPORT.md, report.json; 24 agents; curator ran).
  HONEST SEQUENCE NOTE: round 2 proposed PRE-REGISTRATION v3 ADDENDUM M (text in round2/report.json plan_issues, items
  M1-M6) to be written BEFORE the exp60 T9 DeepCenter section is opened, but the main session had already read and
  recorded the T9 decisions at 20:35 UTC (entry above). M is therefore NOT a pre-registration; it is recorded as
  post-hoc NOTES. It changes nothing: M1/M2 only TIGHTEN the K3b gate (t* incl. control, two neighbours, parity, dc_miss,
  node digest; L2's evaluable-precision half reclassified as needing the user's OK) and K3b already FAILS under every
  reading; M3 (forkmid variant skipping readmitted-touching forks) is moot because forkmid FAILS the original gate.
  Recorded as facts: M4 ANTIPAR (same-side safe fork, cos > 0.25, final coords) was evaluated ONCE by the round-2
  skeptic on the 56 lab clips: vetoed 113/676 (TP 1, FP 4, ignored 108), div_J 0.1290 -> 0.1250, score -0.00034 ->
  FAIL, CLOSED (no reruns); DNVETO (DaughterNet veto on safe forks, orphan I-081) CLOSED without a run (same mechanism
  class); lab veto break-even at J_div 0.129 is FP:TP >= 7.7. M5: the 4 dummy clips hold GT divisions 0/0/0/3 and every
  dummy fork is metric-ignored -> dummies are plumbing evidence only. M6: K4/tempfuse DROPPED (no code, no owner, no
  honest lab); reopen only with a new honest bed. I-072 (float-coordinate divergence/symmetry gates) CLOSED (premise
  false: presafe gates already use float coords). Density-quartile column computed (orphan I-204), no rule attached.
  LB at 19:46 UTC: we are #157/3,908; 0.954 block = ranks 139-201 (silver ~195 inside it, 38 ranks below us); 0.953 block
  = 202-469; ten late 0.953 risers sit at the END of the block (consistent with the earlier-submission tie rule for
  byte-copies). No new public notebook > 0.953, no new discussions.
- 2026-09-25 20:55 UTC, TWIN DUMMY exp58n (vitaliineibauer/biohub-exp58n-x138-safe-lowref v1; AMENDMENT f2 candidate) GATES PASS:
  node rows identical to the K2 dummy (121,252); K2 = twin + 12 inserted edges - 5 stolen edges (all 12 added edges are
  fork edges = exactly #35's 12 forks / 5 steals); LOWDET and 'LOWREFINE ... refined R of N' lines identical to K2; no
  DIVINS lines; no DEADLINE:/REPAIR FAILED/LOWREFINE FAILED; kernel end 1,038 s vs K2 1,512 s, repair 219 s vs 509 s.
  Its SUBMIT still needs the user's OK on AMENDMENT f2 (morning).
- 2026-09-25 22:06 UTC, USER OK on AMENDMENT f2 (chat: "мне нравится твоя идея с двойником", after the comparison twin exp58n vs
  exp52): F2 = exp58n (x138 + safetail + lowrefine = K2 without the DaughterNet insertion) under the f2 conditions
  (scored without error, R5-admissible, public >= 0.953; otherwise exp52 per §f). Its submission is approved; twin dummy
  gates already PASS (entry 20:55 UTC). Plan: submit K2 and the twin at ~00:01 UTC 26 Sep (5 slots that day), both with
  the first exp token naming the build (exp58 / exp58n) so tools/runtime_ledger.py assigns the safetail families.
  User's stated principle: the two finals must not be the same file; they hedge different risks (F2 hedges the least
  proven component of F1, the insertion). L1/L2 OKs still pending but moot (K3b fails under every reading).
- 2026-09-25 23:12 UTC, NIGHT RESEARCH ROUND 3 DONE (research/wf_ideas_v4/round3/REPORT.md). Recorded (no OK needed):
  S4-S6 on 26 Sep carry NO rider (forkmid / K3b / forkblob FAIL at the T9 read, K4 dropped): no exp59/exp59dc build and no
  GPU dummy; unused slots are not burned. Exceptions needing the user's OK: K1 per the READ TABLE below, or a deadline
  move / D4 build if the runtime trigger (L(K2) > 8.0 h) fires. Runtime: forecast F(K2) = 7.73 + 97*4.45*1.15/3600 =
  7.87 h (1.63 h margin to the 9.5 h repair deadline -> R5(b) admits K2 and the twin unless they ERROR). Hidden reruns
  do not consume the weekly GPU quota (usage +2.28 h 13:58->18:12 matched our dummies + lab only). LB 22:16-22:23 UTC:
  3,914 teams, we are #164 at 0.954 (18th of the 0.954 block, ranks 147-211); silver (~rank 196) is 32 ranks below us.
  Closures (round 3): swapfix on x138 (0 of 555 true 2x2 swaps; detection/localisation problem, post-deadline);
  clip-boundary rescue b4 (+0.00056 pooled but 0.00000 on SELECTION - no honest gain). Poller widened to 60 lines so
  pending builds do not drop out of the log (PC3-05). The 25 Sep 10:20 UTC RESUME POINT's finals line (F2 = exp51,
  F1 = best of exp57b/exp56/...) is SUPERSEDED by PRE-REG v3 §f + AMENDMENT f2 + the user's OK (22:06 UTC) + the READ TABLE.
- 2026-09-25 23:12 UTC, K2/TWIN READ TABLE (pre-score clarification of R3/R5/§f/f2; written before any K2 or twin score is
  in poll.log; source research/wf_ideas_v4/round3/report.json). The strict reading applies now. Rows tagged [OK] need the
  user's OK; without it the strict text in [brackets] applies. Displayed scores only; K2's rank inside its score block is
  info, never a decision input (R7).
  REFS: d1 = K2 - #35 (0.954). #35 is the scored proxy of K1 (K1 dummy sha == exp57b dummy; C01 is inert unless a deadline
  fires), so d1 reads lowrefine in the insertion stack. d2 = twin - #34 (0.953): no insertion and no insertion gate, so d2
  reads lowrefine alone. The probe.json line 'compare with exp56 ... ties recorded' is builder boilerplate
  (tools/build_probe_kernel.py l.2310), not a rule.
  CLEAN: d1 is clean iff ledger.md shows L(K2) upper bound <= 8.0 h (COMPLETE seen at a poll <= submit + 8.0 h, ~08:01Z).
  Then the in-kernel insertion deadline (28,800 s from kernel start) never fired; a per-clip 'DIVINS FAILED' stays
  unobservable. L > 8.0 h or no proof = not clean (L includes queue time; P36 still PENDING at the submit makes that likelier).
  R5: F(K2) = 7.87 h leaves 1.63 h to the 9.5 h repair deadline, so R5(b) admits K2 and the twin unless they ERROR.
  First matching row wins:
  1. K2 ERROR: K1 = exp58t v1 in the next 26 Sep slot [OK] (v4 item 6); F1 = K1 once scored, R5-admissible and >= 0.953;
     F2 = twin by f2, else exp52. [Without the OK: §f fallback order.]
  2. twin - K2 >= +0.002: R2 reopens (f2 / R7). F1 = twin. F2 = K2 if d1 >= -0.001 [OK], else K1 if submitted and
     scored [OK], [else exp52].
  3. d1 >= -0.001: lowrefine kept. F1 = K2. F2 = twin if >= 0.953; twin = 0.952 -> twin with a 0.952 floor [OK]
     [else exp52]; twin <= 0.951 or ERROR -> exp52. d2 alone never removes lowrefine from F1.
  4. d1 <= -0.002 and clean: R3 removes lowrefine from the F1 stack (no new lowrefine build). K1 [OK]; F1 = K1 once
     scored, R5-admissible and >= 0.953. F2 = twin if >= 0.953 (f2 as written; R3's 'never try again' bars new builds,
     not an already scored f2 file), else exp52. No K1: F1 = twin if >= 0.953 [OK] [else §f item 4 = #34]; F2 = exp52.
  5. d1 <= -0.002 and not clean: timing confound (branch-C logic); d2 is the lowrefine read. d2 <= -0.002 -> as row 4
     (note: K1 carries the same 8.0 h insertion gate). d2 >= -0.001 -> lowrefine kept; F1 = K2; F2 = twin if >= 0.953
     (0.952 with the floor OK) else exp52; raise the v4 item-5 runtime trigger (deadline move / D4) to the user after
     comparing L(twin): L(twin) >= L(K2) - 0.3 h means queue delay dominates.
  Never: K1 at d1 = -0.001 (R3 keeps lowrefine; a 0.001 K1-vs-K2 pick is barred by R7 and §f); exp56 while an admissible
  non-copy x138-family file exists; two files with identical components.
- 2026-09-26 00:02 UTC ===== RESUME POINT (supersedes the 25 Sep 10:20 UTC block; read this and every dated entry after it) =====
  SUBMITTED 26 Sep: #37 = K2 = exp58 (vitaliineibauer/biohub-exp58-x138-safe-lowref v1; x138 + safetail C01 + lowrefine
  + DaughterNet insertion #35 config), ref 56563521, 00:02:12Z, under pre-approval (PRE-REG v3 §h.3) with 18/18 dummy
  gates; #38 = TWIN = exp58n (vitaliineibauer/biohub-exp58n-x138-safe-lowref v1; K2 without the insertion), ref
  56563534, 00:02:18Z, under the user's f2 OK (22:06 UTC) with twin gates PASS. P36 (exp57 v1 diagnostic, x138 + leaf
  prune + ungated insertion) = 0.954 (L36 in (7.24, 7.42] h) - INFO ONLY by the 18:4x rule; leaf prune on x138 stays
  closed. 3 slots left on 26 Sep; no rider exists (all T9 gates FAILED), so they stay empty unless the READ TABLE
  (entry 23:12 UTC) calls for K1 with the user's OK.
  LB: #34 x138 verbatim 0.953 (L34 <= 6.46 h); #35 x138 + insertion 0.954 (L35 in (6.72, 7.73] h); best = 0.954.
  Branch A. Read K2 and the twin ONLY by the K2/TWIN READ TABLE (23:12 UTC); expected scores ~06:30-08:30 UTC; keep the
  10-min poller (experiments/lb_poll/lb_poll.py, 60-line window) and tools/runtime_ledger.py (ledger.md) running.
  FINALS: PRE-REG v3 §f (13:38) + AMENDMENT f2 (18:20; user OK 22:06) + READ TABLE. Default: F1 = K2, F2 = twin exp58n
  (if scored without error, R5-admissible, public >= 0.953; else exp52). f2 verbatim keeps §f fallback item 4 (#34) as
  the last resort before exp52; never tick two files with identical components; the user ticks both manually by
  29 Sep 20:00 UTC (reminder 12:00 UTC).
  CLOSED: K3 forkmid (power), K3b DeepCenter t*, forkblob, ANTIPAR, DNVETO, K4 tempfuse, I-072, swapfix on x138,
  clip-boundary rescue, edge filter, float output, head retrain, leaf prune on x138. New mechanisms only until 27 Sep
  12:00 UTC (R8). Pending user OKs (moot unless a READ TABLE row needs them): L1/L2, K1 by the table, twin floor 0.952.
  Night research rounds: experiments/workflows/biohub-research-round.js (+ curator research/KNOWLEDGE/, start there:
  INDEX.md); round reports in research/wf_ideas_v4/round<N>/REPORT.md.
- 2026-09-26 01:20 UTC, READ TABLE CLARIFICATION v2 (pre-score; written before any #37/#38 score is in poll.log; source research/wf_ideas_v4/round4/report.json). Adds to the 23:12 UTC READ TABLE (commit 1017c41, pushed 23:13:16Z); the table rows themselves are unchanged. Rows tagged [OK] need the user's OK; without it the [bracketed] strict text applies.
  C1 WHEN TO READ: row 1 may be read on K2 alone. Rows 2-5 are read only when K2 and the twin are both terminal (COMPLETE or ERROR). P36 was COMPLETE at 23:42:50Z, before the submits, so there is no own-queue confound for L(K2). L(twin) is the paired queue control (submitted 6 s apart). Displayed scores in poll.log only; the LB rank is never an input (P36 moved us 164 -> 155 at the same 0.954; info only).
  C2 ROW 1 BY ERROR CLASS: on a K2 ERROR, first read the class with python -c "from kaggle.api.kaggle_api_extended import KaggleApi as K; a=K(); a.authenticate(); [print(s.ref, s.status, repr(s.error_description)) for s in a.competition_submissions('biohub-cell-tracking-during-development')[:4]]"; if error_description is empty, read the Submissions page (read-only). First match wins: (a) 'Kaggle Error' on K2, twin not also 'Kaggle Error' -> resubmit K2 v1 unchanged in the next 26 Sep slot [OK] (message 'probe NN: exp58 ...'); it counts as K2 for this table; a second Kaggle Error -> (d). (b) 'Notebook Timeout' or 'Exceeded Allowed Compute' on BOTH K2 and the twin -> no K1; ask the user; [§f fallback order]. (c) 'Threw Exception', 'Submission CSV Not Found' or 'Scoring / Format Error' on K2 only -> row 1 as written (K1 [OK]). (d) anything else (timeout/compute on K2 only, Kaggle Error on both, mixed or unreadable class) -> no automatic action; ask the user; default row 1 [OK].
  C3 ROW 1 WITHOUT K1 (no OK, or K1 fails): F1 = twin if scored without error, R5-admissible and >= 0.953 [OK]; F2 = exp52. [Without the OK: §f order -> F1 = #34, F2 = twin by f2.]
  C4 ROW 2 HOLE (twin - K2 >= +0.002 AND d1 <= -0.002): submit K1 = exp58t v1 (vitaliineibauer/biohub-exp58t-x138-safe, no rebuild) in the next 26 Sep slot [OK], message starting 'probe NN: exp58t'. F1 = twin; F2 = K1 once scored without error, R5-admissible (9.5 h C01 deadline or step-0 margin >= 1 h) and >= 0.953, else exp52. If the twin itself is < 0.953 here: F1 = K1 (same conditions), F2 = exp52. [Without the OK: F2 = exp52.]
  C5 ROW 5 WITH d2 UNDEFINED (twin ERROR or unscored): lowrefine kept; F1 = K2; F2 = exp52; K1 [OK] stays optional as in row 4; raise the runtime trigger to the user.
  C6 CLEAN PROOF (measurement only): the poller will poll at ~07:54:2xZ and ~08:04:3xZ; the 8.0 h mark is 08:02:12Z; a poll with a failed CLI attempt adds 210 s to the upper bound. If K2 is still PENDING at 07:45Z, run one-shot polls in the poll.log format at ~07:57:30Z and ~08:00:45Z; do not restart the poller.
- 2026-09-26 01:20 UTC, NIGHT RESEARCH ROUND 4 DONE (research/wf_ideas_v4/round4/). Records: Record in CONTEXT (with the next write) and hand to the curator (by 26 Sep 12:00Z): (1) the intel line: 00:47Z #155/3,919, 6th of 73 in the 0.954 block (150-222), silver ~196 (41 ranks margin), 0.953 block 223-511, 16 more late x138 copies at the block end. (2) INFO ONLY: P36 unrounded > #35 unrounded (in-block rank), no rider, no table criterion. (3) CLOSED I-035/C09/E12 head-shift scale (s_opt 0.75-1.0 on both embryos; s = 1.33 worse by 1.7%/2.6%; T12 gate fails; s > 1 trips the 2 um refine guard; no s < 1 variant). (4) Refined-duplicate collapse stays closed (lowrefine adds 12 pairs < 3 um in 121,252 nodes, ~1e-5; the GT-proximity test has low power, and the verdict rests on exposure). (5) Leaf prune on x138 CLOSED (P36 delta 0, P36 rule, f2). FACT: exp60 lp30 +0.00083 (51/56 clips win; 95% of pruned nodes readmitted), lp50 +0.00064. This is the first x138-base, LB-anchored point for a node-removing rule, and it agrees with the LB (no bias). The round-3 node-count bias already had a node-removal arm (L8). (6) Floatout on x138 closed for the finals, with KNOWLEDGE I-215 / DECISIONS.md l.96-98 aligned to CONTEXT l.2022. (7) S4-S11: no new mechanism. Exceptions: K1 per rows 1/4/C4 [OK], a K2 resubmit per C2(a) [OK], an S10-S11 retry of a failed K build, and a deadline move / D4 if the runtime trigger fires [OK]. (8) x138 renamed ('Biohub 0.953 LB | ORIGINAL', still v1; we use a local copy); y3uanm has no public weights (C10 cannot fire).
- 2026-09-26 01:20 UTC, PROVISIONAL FINALS TICK RULE (round 4, PC4-01): the Submissions page shows 0/2 selected; if fewer than 2 are
  ticked, Kaggle auto-selects from the best public scores - today that would be P36 (diagnostic, never a final) and #35
  (R5-unproven). So as soon as the READ TABLE resolves on 26 Sep the user ticks EXACTLY TWO files (default F1 = K2 #37
  56563521, F2 = twin #38 56563534); re-tick only if a later table row / K1 score changes F1/F2. Ticks are reversible
  until the deadline; the 29 Sep 12:00 UTC reminder becomes a check. FINALS-TICK CHECKLIST: Copy the 29 Sep FINALS-TICK CHECKLIST into CONTEXT. (1) 28 Sep evening: confirm the refs. (2) 29 Sep 12:00 UTC reminder, backup 18:00 UTC: F1 'probe 37: exp58' 56563521 (00:02:12Z) and F2 'probe 38: exp58n' 56563534 (00:02:18Z), or the table's replacements (K1 exp58t, exp52 56534391). (3) Exactly 2 ticked, matched by ref and date, not by score; everything else unticked. (4) Reload, screenshot, log in CONTEXT, commit. Never tick #34, #35, P36, or two files with identical components. Set the reminders in a way that survives this session (cloud routine or the user's own calendar). Hard end: 29 Sep 20:00 UTC for ticks (plan), Kaggle deadline 23:59 UTC.
- 2026-09-26 04:04 UTC, READ TABLE CLARIFICATION v3 (pre-score; written before any #37/#38 score is in poll.log; source research/wf_ideas_v4/round5/report.json). Adds to the 23:12 UTC READ TABLE and CLARIFICATION v2 (f05389e, 01:20:05Z); the table rows are unchanged. Rows tagged [OK] need the user's OK; without it the [bracketed] strict text applies.
  V1 PAIRS, NOT LABELS: Kaggle scores the best of the two ticked files; F1/F2 are rule labels only. #34 (56545267) is exp56, a byte copy of x138. The table's Never line ('exp56 while an admissible non-copy x138-family file exists') and f2's parenthetical bar it while any non-copy x138-family file (K2, K1, K2'', twin) is scored without error, R5-admissible and >= 0.953 (twin: or 0.952 with the floor OK). So C3 and row 4 without K1 give the PAIR {twin #38, exp52 56534391} when the twin is so eligible, with or without the OK, and {#34, exp52} otherwise. The OK item 'F1 = twin instead of #34' is moot.
  V2 CHECKLIST (replaces the 01:20 'Never tick #34, #35, P36' clause): never tick #35 or P36; tick #34 only when no eligible non-copy x138-family file exists (pair {#34, exp52}). Replacement refs: twin 56563534 (also as F1), K1 exp58t, K2'' exp58d (refs when submitted), #34 56545267, exp52 56534391.
  V3 RUNTIME TRIGGER OFFER: the trigger is unchanged (L(K2)_hi > 8.0 h or unproven -> raise to the user). D4 (DIVINS_TWOSTAGE) has no code and is DROPPED (EV ~1e-5, v4). The only offer is K2'' = exp58d = K2 with REPAIR_DEADLINE_S=37800 and DIVINS_DEADLINE_S=32400 (never DIVINS alone). It is built only after the trigger fires and on the user's OK, after a builder change (non-lab safetail builds accept exactly (34200, 28800) or (37800, 32400); tests; a K2 rebuild keeps sha 1f1ddb6d...) and a K2'' dummy whose CSV sha256 equals the K2 dummy CSV; message token 'exp58d' (the ledger maps it to the 9.5 h safetail family: use a 10.5 h family or --family). K2'' replaces K2 as F1 iff it scores without error, L(K2'')_hi <= 10.5 h (its own repair deadline) and public >= K2 - 0.001; otherwise K2 stays. K2 and K2'' are never ticked together.
  V4 ROW 5 / C5 RUNTIME READ (replaces 'L(twin) >= L(K2) - 0.3 h means queue delay dominates'): our submissions run concurrently (#34/#35 overlapped), so L(K2) - L(twin) measures the insertion's runtime, not queue. Report B = min(L(K2)_hi, L(K2)_hi - L(twin)_lo + 6.56 h, L(twin)_hi + 1.95 h) (twin runtime <= L34_hi 6.46 h + 0.1 h jitter; insertion cost <= 97 clips x 72.5 s). For the user's K2'' question: B <= 8.0 h -> the insertion gate very likely never fired, K2'' has ~0 value; 8.0 < B <= 9.0 h -> at most the insertion on the last-sorted clips is lost (<~1e-4), K2'' optional; B > 9.0 h -> recommend K2'' (guards the 9.5 h degrade). CLEAN stays L(K2)_hi <= 8.0 h; B never makes d1 clean. Never use a point value for the insertion cost.
  V5 SCOPE (info): CLEAN covers public AND private (one hidden run, clips in sorted stem order). Not clean costs at most K2 -> twin on the last-sorted clips (8.0 h gate), plus a relink degrade only if runtime(K2) > 9.5 h.
  V6 LEDGER: ledger.md's A6 text ('K1 ... rebase K3 on K1'), its A5 ask text (D4) and A5-F ('Forecast F not supplied') are superseded by C2, V3 and F = 7.87 h; ledger.md is report-only.
  V7 POLLING: the C6 one-shots run from a background job started 04:04Z (07:57:30 / 08:00:45 / 08:01:45Z, stamped after the call, every stamp < 08:02:12Z). Do not stop the poller (PID 20052) until poll.log shows COMPLETE or ERROR for both 56563521 and 56563534; if either is still PENDING, keep it at least until the first poll after 09:32:18Z.
- 2026-09-26 04:04 UTC, NIGHT RESEARCH ROUND 5 DONE (research/wf_ideas_v4/round5/; focus: private-only failure modes of the finals).
  Records: With the next CONTEXT write, and for the curator by 12:00Z: (1) intel line: 03:16Z #160/3,922 at 0.954, 6th of 73 in the 0.954 block (155-227), silver ~196 (36 ranks margin), 0.953 block 228-529, 15 more late x138 copies at its end (5th window). (2) FACTS R5H-1 (no private-only crash is possible once #37/#38 COMPLETE: one hidden run), R5H-2 (K2's insertion fail-soft is finer than #35/P36's), R5H-3/R5H-4 (lowrefine audit + smoke 0 exceptions; exp60 failure counters 0), R5H-5 (shared lowrefine risk <~5e-4), R5H-7 (guards and CSV writer outside the per-dataset try: design property). (3) R5-RC-A as a FACT with the skeptic's wording: x138 post-freeze excess ~0.0068 per 6bba GT vs exp39 ~0.012 before / ~0.0055 after the edge filter (roughly halved; ~2x normal FN and FP/TP rates remain); a post-relink re-solve limited to post-freeze transitions is CPU-replayable from the exp60 presafe dump; post-deadline linker item #1 (geometric/flow cost only, never ILP or edge-net trust); private-risk note; optionally fix CONTEXT l.22 ('GT positions copied on frozen frames, step median 0'). (4) R5-RC-B closed: 'no lab gain (-0.0007 control / -0.0006 ins35, all from 2 clips)'; FACTS 'fork-removal riders on x138: 0 for 5 (4 measured: forkmid power, forkblob, ANTIPAR, already-divided; DNVETO by analogue)'. (5) R5-RC-C: add to B5 (l.196) the new blocker (the V1284 head, lowrefine and DaughterNet depend on unadapted detector features); its point (3) is weak. (6) WATCHLIST W44 is DONE (f05389e, 01:20:05Z).
- 2026-09-26 04:04 UTC, OK REQUEST posted in chat (updated list per round 5: K1 by the table; twin floor 0.952; row-2 pairs;
  K2 "Kaggle Error" -> one resubmit; K2'' = exp58d only if the runtime trigger fires with B > 9.0 h; floatout closed,
  L1/L2 dropped; tick exactly two files as soon as the table resolves). poll.log: #37/#38 still PENDING at 04:04Z.
- 2026-09-26 04:12 UTC: K2'' builder change merged (round 5 R5-A4; no kernel built or pushed): non-lab safetail builds accept only
  (REPAIR_DEADLINE_S, DIVINS_DEADLINE_S) = (34200, 28800) or (37800, 32400); everything else (incl. DIVINS alone) is
  refused; runtime_ledger family 'safetail_late' (10.5 h deadline, 9.0 h insertion gate) for token exp58d. K2 rebuild
  sha256 unchanged (1f1ddb6d...). 116 tests pass. K2'' is built only if the V3 runtime trigger fires AND the user says yes:
  python tools/build_probe_kernel.py exp58d_x138_safe_lowref --base x138 --patch divinsert --patch safetail --patch
  lowrefine <K2 DIVINS knobs> --set REPAIR_DEADLINE_S=37800 --set DIVINS_DEADLINE_S=32400 --set LOWREFINE_ENABLE=1.
- 2026-09-26 06:31 UTC, READ TABLE CLARIFICATION v4 (pre-score; written before any #37/#38 result is in poll.log; source research/wf_ideas_v4/round6/report.json). Gap fill and runtime reading only; no table row and no v2/v3 pair changes, except the R5 line below, which replaces the 23:12 blanket sentence and changes nothing when both files COMPLETE with L_hi <= 9.5 h. Precedence: v4 > v3 > v2 > READ TABLE (23:12) > f2 > §f.
  W1 OK TIMING: T0 = the last poll.log header in which 56563521 and 56563534 are both PENDING. On receipt of the user's reply the main session runs `date -u` and logs the time here. A score-reading [OK] item (twin floor 0.952; row-2 F2 = K2; K1 in rows 4/C4) counts as pre-registered only if the reply time is <= T0. Otherwise the [bracketed] strict text is the rule's answer, and if the user still picks the [OK] option it is logged as USER DECISION AFTER SCORE (post-hoc), never as pre-registered. Event items read an error class or a runtime, not a score, and may be OK'd after their event: C2(a) K2 resubmit, row-1/C2(c) K1, W7, K2'' after the V3 trigger.
  W2 K1 FAILS: in row 4 and row 5->4 a K1 that ERRORs, is not R5-admissible or is < 0.953 counts as 'No K1' -> V1 pair {twin, exp52} if the twin is eligible, else {#34, exp52}.
  W3 C5 WITH K1: a K1 submitted under C5 replaces K2 only if it is eligible and K1 - K2 >= +0.002 (§f simpler-file rule); F2 stays exp52.
  W4 K2'' SCOPE: raise the V3 question (report B and B', see V4b) whenever L(K2)_hi > 8.0 h or unproven AND the resolved pair contains K2 (row 3, row 5 kept, C5, row 2 with F2 = K2). K2'' takes K2's place in the pair (F1 or F2). Never in row 1, row 4, row 5->4, row 2 without K2, or after a timeout (C2(d)).
  W5 B WITHOUT TWIN: twin ERROR -> B = B' = L(K2)_hi.
  W6 POLLER (extends V7; ledger.md's 'keep until 08:32:12Z' is only a minimum): keep experiments/lb_poll/lb_poll.py running (one instance; never import it) until every submission made on or after 26 Sep is COMPLETE/ERROR in poll.log, and for any still PENDING at least until the first poll after submit + 9.5 h (K2 resubmit, K1, twin resubmit) or + 10.5 h (exp58d). Before each new submission check that the last poll.log header is < 15 min old; if not, restart the poller first. If the poller dies across a mark, log the gap; that file's R5 is then read from the ledger bounds or R5(b) (K2'' has no R5(b) route).
  W7 TWIN 'Kaggle Error' ALONE (event item): ask the user then (one unchanged resubmit of exp58n v1 in the next slot); default F2 = exp52 by f2.
  W8 INFO: row 5 'kept' always has F1 = K2 at <= 0.952, by design (V5 timing confound); tell the user and offer K2'' under W4.
  V4b RUNTIME BOUND (report-only addition to V4; the bands stay on B as approved): also report B' = min(L(K2)_hi, L(K2)_hi - L(twin)_lo + 7.31 h, L(twin)_hi + 2.66 h) (twin runtime <= 6.46 + 0.58 GPU run variance + 0.13 setup + 0.14 lowrefine; +0.71 h K2-vs-twin run variance; the 1.95 h insertion term is a mean). OK item 5 acts on B; if B <= 9.0 h < B', do not act: ask the user with both numbers.
  R5 FOR #37/#38 (replaces the 23:12 sentence 'F(K2) = 7.87 h ... R5(b) admits K2 and the twin unless they ERROR'): R5(b) basis F' = min(L35_hi 7.73, L36_hi 7.42) + 0.14 lowrefine + 0.71 run variance = 8.27 h (margin 1.23 h -> passes). If a file's own L_hi > 9.5 h, R5(b) needs its runtime bound <= 8.5 h (K2: B'; twin: L(twin)_hi - L(K2)_lo + B'); else R5 is UNPROVEN for that file -> ask the user; strict default = the V1 pair without that file.
  V3b K2'' GATE (only after the V3 trigger AND the user's yes): (1) dummy CSV sha256 == K2 dummy CSV; (2) the log has 'SAFETAIL: repair deadline 37800s, divins deadline 32400s'; (3) probe.json REPAIR_DEADLINE_S 37800 / DIVINS_DEADLINE_S 32400 and the notebook diff vs K2 = those lines + the name comment; (4) tools/dummy_gates.py with --k2 <K2'' dummy dir> passes; (5) its own slug biohub-exp58d-x138-safe-lowref v1, never v2 of the K2 slug (keeps C2(a) 'K2 v1 unchanged' unambiguous); (6) the message's first exp token is 'exp58d'.
- 2026-09-26 07:35 UTC, K2/TWIN SCORE READ (mechanical, by the READ TABLE 23:12 UTC [commit 1017c41, pushed 23:13:16Z] +
  CLARIFICATION v2 [f05389e, 01:20Z] + v3 [fc51b75, 04:04Z] + v4 [64f0551, 06:31Z]; first result seen in poll.log at
  06:54:06Z = twin; K2 first seen COMPLETE at 07:34:12Z; the user gave no OK on the 04:04 list, so only strict text applies
  and none was needed):
  #37 K2 = exp58 (56563521) = **0.954**, L in (7.36, 7.54] h -> CLEAN (<= 8.0 h: the insertion gate never fired),
  R5(a) ADMIT (<= 9.5 h). #38 TWIN = exp58n (56563534) = **0.953**, L in (6.69, 6.87] h, R5(a) ADMIT.
  k = 954, w = 953; d1 = K2 - #35 = 0; d2 = twin - #34 = 0; twin - K2 = -1 (thousandths). Row 1 (error): no. Row 2
  (twin - K2 >= +2): no. Row 3 (d1 >= -1): YES -> lowrefine kept; F1 = K2 #37; F2 = twin #38 (>= 0.953, f2 conditions
  met). No K1, no K2'' (clean), no new submission needed. Insertion runtime cost on the hidden run <= L(K2)_hi -
  L(twin)_lo = 0.85 h. FINALS PAIR TO TICK NOW (provisional-tick rule, reversible until the deadline): **#37 (56563521,
  'probe 37: exp58') + #38 (56563534, 'probe 38: exp58n')**. Never tick #35, P36, #34. The clean-proof one-shot job was
  stopped (moot). 26 Sep: 3 slots left, no rider exists -> slots stay empty (R8 cutoff 27 Sep 12:00 UTC).
- 2026-09-26 08:21 UTC: user chose FULL research rounds every ~2.5 h until the R8 cutoff (27 Sep 12:00 UTC) (option "b"); round prompt updated with the scored finals #37 + #38.
- 2026-09-26 08:27 UTC, 0.955/0.956 WAVE CHECK (user alert; CLI by the main session + round-7 browser agent, notes
  research/wf_ideas_v4/round7/scan_browser.notes.md): LB 08:22-08:24Z: 3,923 teams; 0.953: 325, 0.954: 87, 0.955: 46
  (was 28 on 25 Sep 11:27), 0.956: 26 (was 19), 0.957: 17, >=0.960: 62. We are #183 at 0.954 (#162 at 05:46Z; 12th in
  the 0.954 block); public silver line ~rank 196 is 13 ranks below us. 26 teams rose into >=0.954 with submissions made
  23:43-01:53Z (scored overnight), 15 of them to >=0.955. SOURCE: NOT public - no new public notebook (newest run is
  Harmonic Fusion V3, 0.953), no new discussion topic/comment, no host announcement. Datasets: kragglenote2forwork/
  biohub-sub-cache2 = cached submission CSVs "recovered from the checkmyacckraggle repo", incl. "RANK1-0.961-V8-x138-
  s3forks (gwey1025/biohub-ends77-s3forks)" = a PRIVATE kernel (403) of team "Abnormal Guys" (#47, 0.961) and a
  "metric-hack" file -> leaked material, not a method; static CSVs cannot score in a code competition; NOT used.
  amanatar/optimized-biohub-max-score (votes 15 -> 53) = x138 + in-kernel validator + metric-aligned PP sweep under a 9 h
  governor: conflicts with R7 (validator/sweep never on in our submissions; the hidden rerun sweeps other stems) and no
  public score >= 0.954 is shown -> not ported. E10 trigger (public x138 heir >= 0.956): NOT met. Interpretation: private
  or Discord x138 variants / own work; public-tuned knobs may not transfer to private. Plan unchanged: finals #37 + #38.
- 2026-09-26 08:49 UTC, RULES CHECK (user question "official rule or our principle?"; browser, read-only, Rules/Data/Overview):
  (1) Leaked private submission CSVs: rules 3.5.d "Privately sharing code or data outside of Teams is not permitted";
  3.6.a sharing Competition Code between teams "may result in disqualification"; using leaked files is not named
  explicitly but conflicts with 3.14.a "your Submission is your own original work" and 3.8.d (cheating/unfair
  practices) -> NOT allowed in practice (and useless: static CSVs cannot score in the hidden rerun). (2) In-kernel
  validator/PP sweep on the hidden rerun: NOT prohibited by the rules -> R7 is our methodological rule only.
  (3) Test-set structure / overlap consensus: the only test-data prohibition is 3.4.b "submissions may not use or
  incorporate information from hand labeling or human prediction of the validation dataset or test data records";
  automated test-time use of test clips, leaks, test-set structure and LB probing are NOT MENTIONED -> not prohibited
  by the rules (earlier caution was ours). Data page: hidden test "approximately the same size as the training dataset",
  "Train and test sets are embryo-disjoint", "Multiple samples may share the same embryo"; overlap of test crops NOT
  MENTIONED. External data/models allowed if "publicly available and equally accessible" (2.6.a, Code Requirements).
  Recommendation to the user: overlap consensus is rule-legal but small (+0.0005 expected), conditional on overlapping
  hidden crops, and too tight for R8 (27 Sep 12:00 UTC) -> not recommended; user decides.
- 2026-09-26 08:58 UTC, USER DECISION: build the OVERLAP-CONSENSUS line (rules check 08:49 UTC: not prohibited) as a CANDIDATE only;
  it never displaces the finals #37 + #38 unless every gate below passes. Design = research/wf_ideas_v2/
  r2_research_overlap-consensus.json (exact-content anchor hashing registration; disagreement-component splice with the
  border-distance owner rule; forks skipped; node cap 0.5%) with its three skeptic verdicts (not refuted; ceiling
  +0.004..+0.006 on a 44b6-type embryo, exactly 0 on a 6bba-type one, harm ~0 by construction).
  PRE-REGISTERED GATES (written before any result):
  G-A REGISTRATION on the 199 train videos (GT-free): >= 60 of the 65 GT-linked 44b6 pairs found at the exact GT offset
      (+-1 voxel); 0 accepted 6bba pairs (with the >= 5-frame and >= 5% spatial rules); 0 cross-embryo pairs. FAIL -> stop.
  G-P BIT-PROBE (1 slot, user-approved as part of this line): a registration-only kernel on the hidden test raises an
      exception if >= 1 pair is accepted (ERROR = overlapping crops exist) and otherwise writes a trivial valid CSV
      (COMPLETE = none -> the line has no possible effect on public or private -> stop). Never a final.
  G-B LAB SPLICE on x138/K2 tails of all 71 44b6 train clips (Kaggle GPU lab, trainlab dumps), official metric:
      44b6 delta >= +0.002 with leak-group bootstrap CI lower bound > 0; 6bba: zero changed edges; node count <= +0.5%;
      forks untouched; report per leak group. FAIL -> stop.
  G-D DUMMY: candidate K6 = K2 + --patch overlapcons; with no accepted pair the CSV is byte-identical to the K2 dummy;
      fail-soft 'OVERLAPCONS FAILED'; registration + splice time <= 30 min.
  G-LB: K6 submitted once (before the R8 cutoff 27 Sep 12:00 UTC). K6 replaces K2 as F1 iff G-A, G-P(ERROR), G-B, G-D
      pass AND K6 scores without error, R5-admissible (9.5 h) and public >= 0.954; F2 stays the twin #38. Otherwise
      the finals stay #37 + #38. The E10 successor watch keeps priority if it triggers.
- 2026-09-26 08:58 UTC: OVERLAP-CONSENSUS line PAUSED by the user ("стой, дождёмся куратора") right after its gates were recorded; nothing built, pushed or submitted. Resume only on the user's word after the round-7 curator report.
- 2026-09-26 09:03 UTC, NIGHT RESEARCH ROUND 7 DONE (research/wf_ideas_v4/round7/; 8 skeptics: 5 confirmed with fixes, 3 refuted). Records (curator by 26 Sep 12:00Z):
  (1) INTEL: 08:22Z 3,923 teams, #183 at 0.954 (12th of 87 in 172-258); 08:38Z CLI #185; blocks 0.957 = 83-99, 0.956 = 100-125, 0.955 = 126-171, 0.953 = 259-582; silver ~196. The overnight rise (subs 23:43-01:53Z) follows the 00:00Z quota reset + ~7 h latency (daily pattern, not a signal). 7th window of late x138 copies at the 0.953 block end. E10 NOT met: no public kernel run since 25 Sep 09:09Z, x138 still v1; kabirk22/biohub3 = normalized train tensors, no method (not pulled). No new topic, comment or announcement.
  (2) API FACT: finals ticks ARE readable: KaggleApi.competition_submissions(..., group=SubmissionGroup.SUBMISSION_GROUP_SELECTED) (0 at 08:32Z and 08:37Z; page 0/2 at ~08:34Z). The kernel list has no score field (change detector only).
  (3) CLOSED BY MEASUREMENT (exp60, 56 clips): I-186/I-141 gap LAP g=1..3 + sandwich: g1..3 TP 5 / FP 458 < 20 um; 2 TP / 63 FP < 10 um (mutual NN 2 / 60); ~3.65k unevaluable pairs; all TP in 6bba; ceiling <= ~+0.0003 at 100% precision. FACT: x138 synthetic gap / gap2 / readmitted nodes match GT at ~1% (58/5,647, 29/2,968, 73/13,284).
  (4) I-042/I-128 z-split stays closed (reachable: 1 z-merge, 2 FN edges). FACT (node-miss anatomy, official 7 um match): 668 missing GT nodes / 1,211 FN edge-ends; merges with an annotated neighbour 31 (4.6%; 30 yx, 1 z); pruned by the x138 tail 80 (12%); absent upstream 557 (83%); nearest final node at 7-10 um 477 (71%; 6bba 436). Their unclaimed rate equals the annotation base rate (control 94.6% / 97.6%), so it carries no information; they are z-dominant 41% vs 25-28% in the control (axial offset excess); the v2 valley test (4% valley, exp39) puts the GT point and the peak on one object. Post-deadline (R9): axial localisation of z-elongated nuclei in 6bba -> detector/head list.
  (5) HEADROOM FAMILY: I-007/I-008/I-009/I-235 moot (the finals already ran on the hidden set; K2 clean, V3/W4 trigger not fired). I-038/I-144/I-156: runtime is no longer the binding objection; closed on value (H2 ~+0.0003, I-144 +0.0002, I-156 4/4 negative on LB; detection-map class 0/5 on LB), on the R4 +0.002 read, on missing tempfuse code and dummy gates, and on R8.
  (6) POWER-LIMITED CLOSURES: exactly one, forkmid (sign favourable: +0.00013, div_J +0.0010; 1 evaluable FP; the 44b6 and lowrefine-sensitivity clauses are evidence-limit clauses, not measured harm). A 6bba-only replication was costed (P(pass) ~0.4, EV ~+2-4e-5; needs a lowrefine lab build, 4-5 GPU-h, a K3 slot and a 7.5 h run before R8) and NOT run. F-TRN-11/F-TRN-22 unchanged. All other closures fail on sign or a harm clause.
  (7) GPU quota not binding (weekly reset expected 26 Sep 00:00Z; readable only on the Settings page).
- 2026-09-26 09:03 UTC, E10 PORT RULE (pre-trigger: written before any qualifying successor is seen; source research/wf_ideas_v4/round7/report.json; merges round-7 PC7-01, PC7-02 and r7h-4 with the skeptics' fixes). It applies only to a PUBLIC x138 successor and adds no mechanism of ours. Items tagged [OK] need ONE conditional user OK, logged with `date -u` BEFORE any trigger; without it the strict text applies: on a trigger, notify the user and wait.
  P1 WATCH (no OK needed): light CLI checks every ~6 h through 29 Sep 00:00 UTC (not only until R8): `kaggle kernels list --competition biohub-cell-tracking-during-development` with --sort-by scoreDescending and with --sort-by dateRun (diff the top-10 refs and lastRunTime against the previous check), `--user anvithpothula` and `--user thtennant` by dateRun, and the LB histogram (teams per score >= 0.955). The kernel API has no score field, so open the browser only when something changed. The full research rounds (the user's option b, 08:21) still end at the R8 cutoff, 27 Sep 12:00 UTC.
  P2 SEARCH SIGNAL (starts a look, never a port by itself): a new or re-run public competition kernel with lastRunTime inside the window, or >= 5 teams moving from <= 0.953 to one identical score >= 0.956 inside one window (C10's >= 10-team spike is the strong form). Bursts from submits made ~23:30-02:00Z (00:00Z quota reset + ~7 h hidden run) are the daily pattern, not a signal on their own.
  P3 PORT CONDITIONS (all): the notebook's own displayed public score >= 0.956; every dataset/model source public; its diff vs experiments/exp56_x138_verbatim = 1-2 explainable mechanisms; no knob sweep, no in-kernel PP sweep or validator scoring test stems (R7), no cached CSV or test-derived dataset.
  P4 BUILD: `kaggle kernels pull -m` into experiments/ext_<slug>/; change only id and title (vitaliineibauer/biohub-exp63-succ-<author>), keep docker_image and machine_shape; no C01 (the builder has no successor base; adding one is new code after R8); one dummy run whose final node count is within 1% of the author's own log; message 'probe NN: exp63 = <author>/<slug> verbatim'.
  P5 R5: run tools/runtime_ledger.py with --family <ref>=x138 only if the port keeps x138's REPAIR_DEADLINE_S = 27000 guard (7.5 h); otherwise R5 is UNPROVEN -> ask the user; not adopted by default.
  P6 ADOPT iff the port scores without error, R5(a) L_hi <= 7.5 h, and public >= 0.956 (= K2 + 0.002 = max(#34, #35) + 0.002; R4). Then the PAIR = {port, K2 #37 56563521}: the twin #38 leaves, and §f(iii) (C01 in F1) is waived for the port only [OK]. Otherwise the pair stays {#37, #38}. Never {port, twin}, never port + #34, never two byte-identical files. No 'successor + insertion' build and no C10 rider path (new code after R8, unscored stack).
  P7 SLOTS AND TIME: S8 (27 Sep) or S14 (28 Sep); the last port submit is 29 Sep 02:00 UTC (R8), so the last useful trigger is ~29 Sep 00:00. Before the submit the last poll.log header must be < 15 min old (W6); keep the poller until the port is terminal and at least until submit + 7.5 h.
  P8 [OK] AUTONOMY: with the user's conditional yes, the session may pull, dummy and submit ONE port that meets P3-P5 without waking the user, and sends a PushNotification at the trigger and at the submit. The user re-ticks {port, #37} only after P6 is met (ticks by 29 Sep 20:00 UTC). Without the yes: notify and wait.
  STATUS: PROPOSED - pending the user's conditional yes (asked in chat at 09:03 UTC); not in force until then.
- 2026-09-26 09:03 UTC ===== RESUME POINT (post-score; supersedes the 26 Sep 00:02 UTC block; read this and every dated entry after it) =====
  FINALS: #37 K2 = exp58 (56563521, 'probe 37: exp58', 0.954, L (7.36, 7.54] h, clean, R5(a)) + #38 twin = exp58n (56563534, 'probe 38: exp58n', 0.953, L (6.69, 6.87] h, R5(a)), by READ TABLE row 3 (07:35 UTC entry). TICK STATUS: <0/2 at 08:37:15Z (API group=SELECTED) | 2/2 seen hh:mmZ (API + page)>. Never tick #34, #35, P36, or two files with identical components.
  MOOT: K1, K2'' (K2 clean), the 0.952 twin floor, L1/L2, every rider (T9 FAIL 25 Sep 20:35), READ TABLE rows 1/2/4/5 and C2-C5.
  OPEN: (1) E10 by the E10 PORT RULE (09:03 entry): CLI checks every ~6 h through 29 Sep 00:00 UTC; last port submit 29 Sep 02:00. (2) Research rounds every ~2.5 h (user's option b, 08:21) until 27 Sep 12:00 UTC (R8); after ~26 Sep 22:00Z they cannot yield a final -> E10 intel, finals hygiene, lessons. (3) Tick checks (API SELECTED + page) on 28 Sep evening, 29 Sep 12:00 and 18:00 UTC; the user's own durable reminders (W50). (4) Poller lb_poll.py (PID 20052) until 29 Sep 20:00 UTC; any submit needs a poll < 15 min old. (5) Curator records of rounds 5-7. Slots: 3 left on 26 Sep, empty unless E10; 5 on 27 Sep (S8); S14 on 28 Sep.
  LB (info only, R7): 08:38Z #185/3,920 at 0.954; the public silver line (~196) will likely pass us today through others' gains; private (~71%, other embryos) decides.
- 2026-09-26 09:03 UTC: curator 7 notes the overlap-consensus line (PAUSED at 08:58Z) was not assessed by the curators; ledger I-208 still says "refused by team policy/R9" - superseded by the 08:49Z rules check (rule-legal) and the user's 08:58Z decision; the line awaits the user's resume/stop.
- 2026-09-26 09:10 UTC: FINALS TICKED 2/2 = [56563521, 56563534] (#37 K2 exp58 + #38 twin exp58n), verified with the Kaggle API
  (SUBMISSION_GROUP_SELECTED) at 09:10:07Z after the user's "финалы отметил". Re-check on 28 Sep evening and 29 Sep
  12:00 / 18:00 UTC.
- 2026-09-26 09:10 UTC: USER CONDITIONAL YES on the E10 PORT RULE (chat: "даю условное да") -> the rule recorded at 09:03 UTC is IN FORCE
  from now (given before any trigger; P2/P3 not met at this time).
- 2026-09-26 09:10 UTC: USER: resume the OVERLAP-CONSENSUS line ("запускай сверку кропов") under the gates G-A/G-P/G-B/G-D/G-LB
  recorded at 08:58 UTC; candidate only; finals stay #37 + #38 unless G-LB is met.
- 2026-09-26 10:09 UTC: BRANCH claude/practical-meitner-31k9ye REWRITTEN at the user's request: commits authored/committed by
  "Claude <noreply@anthropic.com>" (5) now authored by Vitaly Neybauer <pedrosemyonson@gmail.com>; "Co-Authored-By:
  Claude ..." and "Claude-Session: ..." trailer lines (8 each) removed; 111 commits from b8ab8da onward rewritten
  (git filter-branch in a temp clone); final tree identical, 480 commits; force-pushed with lease (a153fc5 -> 4e760fb).
  Local backup ref: backup/claude-branch-before-rewrite (a153fc5, not pushed). main is NOT rewritten and still contains
  the original commits (via PR #1 and the merges). From now on main is NOT mirrored to that branch any more.
- 2026-09-26 10:15 UTC: MAIN HISTORY REWRITTEN at the user's request (same filter as the cloud branch): Claude authorship (5 commits)
  -> Vitaly Neybauer; Co-Authored-By/Claude-Session trailers (8+8) removed; 112 commits from b8ab8da onward rewritten;
  tree identical; force-pushed with lease (fa8db4b -> fd23e0a); main and claude/practical-meitner-31k9ye share the
  rewritten history again (4e760fb). OLD HASHES cited in CONTEXT (e.g. READ TABLE 1017c41 -> 581277b, v2 f05389e ->
  85a7ca8, v3 fc51b75 -> 708861e, v4 64f0551 -> 093526c) map via experiments/git_rewrite_map_2026-09-26.txt; commit dates
  are unchanged, so every "written before the score" timestamp still holds. Local backup refs (not pushed):
  backup/main-before-rewrite (fa8db4b), backup/claude-branch-before-rewrite (a153fc5). RULES FROM NOW: (1) the running
  overlap-consensus workflow branches (worktree-wf_b39793f6-e79-*) are based on the OLD history - bring their work in by
  cherry-pick / rebase --onto, NEVER by merge (a merge would re-import the Claude commits); (2) friend A (and any other
  clone) must `git fetch && git reset --hard origin/main` before committing again (PROMPT_FRIEND_A.md notified).
- 2026-09-26 10:52 UTC, OVERLAP-CONSENSUS LINE STOPPED BY ITS PRE-REGISTERED GATE (workflow wf_b39793f6-e79, 10 agents):
  G-A FAIL: registration on all 199 train videos found 43 of the 62 GT-linked 44b6 pairs at the exact offset (the
  gate said ">= 60 of 65"; splits.json holds 62 links), 0 wrong offsets, 0 accepted 6bba pairs, 0 cross-embryo pairs,
  49 accepted pairs (all 44b6, all bit-exact). Misses: 11 with 2.2-4.8% spatial overlap (< 5%), 4 with 1-4 overlapping
  frames (< 5), 4 with < 30 votes. By the 08:58 UTC text ("G-A FAIL -> stop") the line stops: NO bit-probe (G-P), NO K6
  submission. Supporting evidence (info): the lab-GB proxy on exp39 tails of all 71 44b6 clips gave splice delta
  -0.00047 (bootstrap lower -0.00216; clip wins/losses 22/37). The algo reviewer found and fixed a harmful fragment-drop
  in the splice (now rollback). The exp64 x138 lab kernels finish anyway (no slots used); their G-B reading will be
  recorded as INFO ONLY (post-stop). Code kept out of main for now (branches worktree-wf_b39793f6-e79-* are on the
  pre-rewrite history except the patch-K6 branch, rebased to the new history at ff438f7). Finals unchanged: #37 + #38.
- 2026-09-26 11:06 UTC, R9 / PRE-REG v3 DECISION (7) AMENDED BY THE USER (record of the 08:58 and 09:10 UTC decisions; no new
  decision): overlap consensus was allowed as a CANDIDATE under gates G-A/G-P/G-B/G-D/G-LB, with exactly ONE hidden-test
  probe (G-P, registration only, never a final) as part of that line; N2 and every other hidden-test probe stay banned.
  G-A FAILED (entry 10:52 UTC; written before any exp64/G-B number was read - no exp64 output was on disk). Round 8
  (research/wf_ideas_v4/round8/) confirms: count clause 43/62 fails ("65" in the 08:58 text was a typo for the 62
  splits.json links; this does not change the verdict; even counting candidates rejected by our own floors gives 58/62);
  precision clauses pass (0 wrong offsets, 0 6bba, 0 cross-embryo). Default = STOP; the user may only reopen it as a
  logged post-hoc decision before any G-B number is read. Other round-8 facts: E10 not triggered (no public heir);
  public rank #188-189 of 3,924 at 0.954, silver line ~196 (7-8 ranks margin) - falling below it is not a trigger
  (private decides); the +0.1 voxel z-shift idea (+0.0015 on 6bba in-sample, ~+0.0003 expected out-of-sample) goes to
  the post-deadline list. Curator: ledger I-208 -> "allowed as a candidate by the user 08:58/09:10Z; G-A FAILED 10:52Z".
- 2026-09-26 13:11 UTC, OVERLAP-CONSENSUS POST-STOP INFO (no decision; the line was stopped by G-A at 10:52 UTC): exp64 lab kernels
  (x138 + lowrefine + insertion dump-only replayed on CPU, all 71 44b6 train clips, 2 shards, 0 missing, 0 failed hooks)
  scored with tools/overlap_lab.py (worktree branch worktree-wf_b39793f6-e79-6): registration accepted 49 pairs (0
  cross-prefix), 59 clips changed, 5,556 components spliced (nodes +18,390 / -20,928). G-B (ins35_splice vs ins35):
  44b6 delta **-0.00143**, bootstrap lower -0.00200 -> the splice HURTS on the real K2 stack (proxy on exp39 tails was
  -0.00047). This confirms the stop; the idea goes to the post-deadline list only with a new design (not the owner rule).
  Output: experiments/exp64_overlap_lab/results_info_post_stop.json.
- 2026-09-26 13:27 UTC ===== RESUME POINT (supersedes the 26 Sep 09:03 UTC block; read this and every dated entry after it) =====
  FINALS TICKED 2/2 = [56563521 #37 K2 exp58 0.954, 56563534 #38 twin exp58n 0.953] (READ TABLE row 3, 07:35 UTC entry). API SELECTED seen at 09:10:07Z, 10:45:26Z (round 8) and 13:00:41Z (round 9). Re-check (API SELECTED + page) on 28 Sep evening and 29 Sep 12:00 / 18:00 UTC; ticks by 29 Sep 20:00 UTC (plan; Kaggle deadline 23:59 UTC). Never tick #34, #35, P36, or two files with identical components.
  OVERLAP CONSENSUS: STOPPED by its pre-registered gate (G-A 43/62 < 60; 10:52 UTC entry). No user answer to the round-8 STOP/continue question is logged, so the default STOP stands. Never push or submit exp65 (G-P) or exp66 (K6). Any exp64 G-B reading is 'post-FAIL info, no decision, in-sample'.
  ACTIVE LINE: only E10, under the E10 PORT RULE (in force since 09:10 UTC; P1-P8 + P4b). CLI checks in every research round and at least every ~6 h through 29 Sep 00:00 UTC; last port submit 29 Sep 02:00 UTC; the ledger family for exp63 is x138 (7.5 h), never safetail.
  SLOTS: 3 left on 26 Sep, 5 on 27 Sep, 5 on 28 Sep; all stay empty unless E10 fires. S12/S13 (28 Sep consolidation) are empty by rule (no rider passed); no F1-final consolidation build. R8: no new mechanism after 27 Sep 12:00 UTC; round 9 found no candidate that could pass an honest gate before it.
  POLLER: experiments/lb_poll/lb_poll.py (PID 20052; last header 12:55:21Z; gaps > 15 min: 0) runs until 29 Sep 20:00 UTC; before any submit the last poll.log header must be < 15 min old (W6). Windows sleep-after-idle is 'never' on AC and battery (checked ~13:03 UTC).
  GIT: main was rewritten at 10:15 UTC; old-based worktree branches come in only by cherry-pick / rebase --onto, never by merge; before any push `git log main --format='%an%n%cn%n%b' | grep -ci claude` must print 0.
  RESEARCH: rounds every ~2.5 h until 27 Sep 12:00 UTC (user's option b, 08:21 UTC) unless the user switches to light mode (E10 checks + tick checks + lessons). Reports: research/wf_ideas_v4/round<N>/.
  LB (info only, R7): 12:46Z #204/3,928 at 0.954, 8 ranks below the public silver line (~196). Private (~71%, other embryos) decides.
- 2026-09-26 13:27 UTC, INTEL (round 9, info only, R7): LB 12:46Z 3,928 teams; we are #204 at 0.954 (13th of 93 in the 0.954 block, ranks 192-284); public silver ~196, so we are 8 ranks below it (not a trigger, as said in round 7). Blocks: 0.957 87-106, 0.956 107-136, 0.955 137-191, 0.953 285-619 (335); >=0.960 67; >=0.970 7. 47 teams changed score from subs made 00:08-06:30Z (top mover 'Bioinformatics is not solution' 0.959 -> 0.966). 4 later subs were placed above us inside 0.954 by unrounded score (known since 25 Sep 17:20Z). 9th window of late x138 copies (17 at #586-602). E10 NOT met at 12:47Z and 13:00Z: the newest run, sarveshchhetri/robust-3d-cell-tracking, is a classical baseline (0.432); kssrikar4/biohub-model holds the UNETR++ weights of a 0.758 team; no public notebook > 0.953; x138 still v1. No new topic; one comment on 743006 asks whether the prefixes 44b6/6bba identify embryos (no host answer). Overview unchanged ('3 DAYS TO GO', 12 h limit).
- 2026-09-26 13:27 UTC, OC SEQUENCE NOTE (no decision): G-A 43/62 was committed at 09:51:54Z (e925955 = 9c85782 on the rewritten history). The exp39-tail proxy (-0.00047, bootstrap lower -0.00216) is not G-B as pre-registered, which uses x138/K2 tails. It was committed at 10:45:32Z (wt6 1986fb9) and disclosed in the 10:52 stop entry. The 11:06 wording 'before any exp64/G-B number' refers to exp64 (first dump 12:05Z). R8-A2 (STOP/continue): no user answer is logged, so the default STOP stands. Any exp64 G-B reading = info only, no decision.
Do not declare the user's post-hoc reopen option void, and add nothing to the post-deadline list from this item.
- 2026-09-26 13:27 UTC, E10 PORT RULE P4b (mechanical clarification of P3/P4 within the user's 09:10 UTC conditional yes; no new mechanism; written before any trigger): `kaggle kernels pull -m` returns the AUTHOR's metadata. Pulled files have shown is_private false, enable_internet true, an id_no and blank "" dataset sources, so pulled metadata is never pushed as-is. (a) Set id = vitaliineibauer/biohub-exp63-succ-<author>, a new title, is_private = true, enable_internet = false; delete id_no; keep docker_image, machine_shape, enable_gpu and every non-blank source unchanged. (b) P3 FAILS if any source is "" or cannot be listed from our account (`kaggle datasets files <ref>`; models: `kaggle models get <ref>`). (c) The CLI pulls and outputs the LATEST version only. The port is valid only if the notebook page shows the >= 0.956 score on that same latest version; record the version number. A newer unscored version = no port. (d) grep the notebook. BIOHUB_VALIDATOR_ENABLE must be '0' and REPAIR_DEADLINE_S must be 27000, else R5 is UNPROVEN (P5). There must be no PP sweep or validator that scores test stems, and no cached CSV or test-derived dataset (R7/P3). (e) Dummy gate: tools/dummy_gates.validate_csv passes on our dummy submission.csv and on the author's output CSV of that version (`kaggle kernels output <author>/<slug>`), and the per-clip node counts agree within 1% (sha256 equality recorded as info). The ledger family for exp63 is x138, never safetail.
Mention it to the user in one line (R9-A8 item 6).
- 2026-09-26 13:27 UTC, POINTER (append-only instead of moving text): two dated entries sit BELOW "## 9. Literature" at the end of this file (25 Sep 14:05 UTC "T1 SAFETAIL DONE" and 26 Sep 09:40 UTC cloud check-in); read them as part of section 14.
- 2026-09-26 13:34 UTC, R9-A5 DONE (overlap-consensus evidence into main by cherry-pick, no merge): 9c85782 aa5b834 ff438f7
  9826517 a012e32 1986fb9 -> 3d6a704 b104355 c98242b 58a8452 09233dc a782fa1 (no conflicts; authors unchanged). Checks: a rebuild
  from HEAD with the documented commands ("BUILD COMMANDS FOR 26.09", l.1768-1780) gives byte-identical K2 exp58 (1f1ddb6d...), K1
  exp58t (a77bcd6b...) and twin exp58n (55038fd6...), so the new --patch overlapcons code leaves the finals unchanged; pytest
  184 passed; claude grep on main = 0. experiments/exp65_overlap_probe/ and experiments/exp66_k6_overlapcons/ now hold
  NEVER_PUSH.md (never push, never submit). The worktree branches worktree-wf_b39793f6-e79-{1,4,5,6} are no longer needed as
  evidence; never merge them (e79-1 sits on the pre-rewrite history). Also committed (4a44a83): curation 9 (research/KNOWLEDGE;
  it already records the R9-A6 items: I-276 refuted by measurement, I-222 with weight 0.80, I-177..I-181 notes, exp64 bed),
  intel pulls experiments/ext_corwin-biocel-aux, ext_y3uanm-secondary-ft, ext_robust-3d-cell-tracking, and the exp64 post-stop
  md/registration files. Round-9 status: A0-A7 done, A8 (user brief) in chat at the end of this turn, A9 (E10 check) in round 10.
- 2026-09-26 16:04 UTC, ROUND 10 RECORD (research/wf_ideas_v4/round10/; info and hygiene, no decision):
  (1) E10 P1 ~15:24Z (re-checked 15:33Z): P2 signal = amanatar/optimized-biohub-max-score v10 run started 13:18:11Z, status
  RUNNING, unscored. P3 FAIL (in-kernel 45-key PP sweep + pass-2 rewrite, validator ON on held-out TRAIN stems, 5 new
  default-OFF levers >> 1-2 mechanisms, no page score >= 0.956). P4b(c)/(d) FAIL (BIOHUB_VALIDATOR_ENABLE='1';
  BIOHUB_REPAIR_DEADLINE_S overridden to 30600 in pass 2). No port. scoreDescending top-1 unchanged (Harmonic Fusion V3
  0.953; amanatar 2nd, x138 4th). Crowd clause: 2 teams went from <= 0.953 to 0.956 (< 5). anvithpothula and thtennant
  unchanged. E10 NOT met. Next P1 check <= ~21:30Z (round 11 at ~17:45Z does it).
  (2) FINALS: API SELECTED 2/2 = [56563521, 56563534] at 15:23:10Z and 15:24:58Z.
  (3) INTEL (R7, info only): LB 15:16:37Z, 3,930 teams. We are #210 at 0.954, 13th of 96 in the 0.954 block (198-293).
  Public silver 196.5, so we are 14 ranks below it. Blocks: 0.957 90-107, 0.956 108-140, 0.955 141-197, 0.953 294-638
  (345); >= 0.960 67; >= 0.970 7. 10th window of late x138 copies (17 at #608-624). No mover has a public source.
  (4) x138 SLUG: the live slug is anvithpothula/biohub-0-953-lb-original (v1; lastRunTime 21 Sep 09:47:58Z; ipynb md5
  97e22a53... = experiments/ext_x138/biohub-x138.ipynb). The old anvithpothula/biohub-x138 returns 404 on pull/status:
  renamed, NOT deleted or changed. A version-pinned pull of another user's kernel returns 403 (CLI 2.2.4), so only the
  latest version can be pulled (confirms P4b(c)).
  (5) R9 ACTIONS VERIFIED (round 10, ~15:25Z): RESUME POINT 13:27, P4b, ledger rule exp63 -> x138 (+ test), OC
  cherry-picks, NEVER_PUSH in exp65/exp66, finals notebooks sha unchanged (exp58 1f1ddb6d, exp58t a77bcd6b, exp58n
  55038fd6). No exp65/exp66 push or submit. Test command = `python -m pytest -q tests` (184 passed). A bare `pytest` at the
  repo root errors on experiments/l2_daughternet/kdn_score/test_adversarial.py; that is not a regression.
  (6) FINALS INPUTS PROTECTION (until the private LB is final): never delete or make inaccessible
  vitaliineibauer/biohub-ft-weights or the kernels vitaliineibauer/biohub-exp58-x138-safe-lowref and
  vitaliineibauer/biohub-exp58n-x138-safe-lowref; never remove files from a biohub-ft-weights version (new versions only
  add files).
  (7) OPS: poller PID 20052 alive, last header 15:35:50Z, 0 gaps > 15 min. Windows Update NoAutoRebootWithLoggedOnUsers=1,
  no pending reboot. Hygiene: round8/REPORT.md and round10/REPORT.md saved from the report JSON (the harness blocks .md
  writes by subagents); one copy of the amanatar v10 intel kept (experiments/ext_optimized-biohub-max-score/v10_2026-09-26/,
  ipynb md5 24ecb611...); the byte-identical duplicate folder and bash.exe.stackdump deleted.
- 2026-09-26 16:04 UTC, E10 PORT RULE P4c (mechanical clarification of P3/P4/P4b within the user's 09:10 UTC conditional yes; no new
  mechanism; written before any trigger; source research/wf_ideas_v4/round10/report.json R10-A2):
  (1) BYTE-FOR-BYTE: a port is the scored version byte-for-byte, except the P4b(a) metadata fields. Any change to an env
  default, flag, lever or source = no port. Flipping BIOHUB_VALIDATOR_ENABLE to '0', or hard-coding the levers a sweep
  picked, is our own modification of an unscored configuration, not a port.
  (2) VALIDATOR SCOPE: P3's 'no PP sweep or validator scoring test stems' covers a validator or PP sweep on TRAIN or TEST
  stems. Either one fails P3.
  (3) GREP = EVERY ASSIGNMENT, not the first hit. Every os.environ assignment of BIOHUB_VALIDATOR_ENABLE sets '0', and one
  comes before the reader. A missing line counts as ON (x138's reader is os.environ.get('BIOHUB_VALIDATOR_ENABLE', '1') !=
  '0'). Every os.environ assignment, os.environ.get fallback and preset-dict value of BIOHUB_REPAIR_DEADLINE_S equals
  27000; a later override such as amanatar v10's os.environ['BIOHUB_REPAIR_DEADLINE_S'] =
  os.environ.get('BIOHUB_REWRITE_DEADLINE_S', '30600') fails. There is no pass-2 rewrite, REWRITE/PPSWEEP/SWEEP gate or
  in-kernel metric sweep.
  (4) SOURCES: kernel_sources must be []. Any kernel source = P3 FAIL (it floats to the source's latest version and can
  carry a cached CSV).
  (5) DUMMY: the dummy log shows 'VALIDATOR: disabled (BIOHUB_VALIDATOR_ENABLE=0).' and 'enabled=False', and has no
  'DEADLINE:' and no 'Re-writing submission.csv' line. Both CSVs (ours and the author's output of that version) pass
  validate_csv, have no duplicate (dataset, node_id) rows and have finite x/y/z. Per-clip node counts agree within 1%
  (sha256 equality recorded as info).
  (6) TOOL: (1)-(5) are run by tools/e10_port_gate.py (read-only; it never touches a kernel; being written now, its commit
  follows). Any FAIL = no port.
  (7) BROWSER: the kernel API has no score field, so P3's score read needs the browser. If Claude in Chrome is not
  connected at a trigger: notify the user and wait (strict P8 default).
- 2026-09-26 16:04 UTC, E10 P1 SNAPSHOTS AND CHECK TIMES AFTER R8 (R10-A4): from the next check on, every P1 check writes
  experiments/e10_watch/<YYYYMMDDTHHMMZ>.txt (tools/e10_snapshot.py, read-only CLI: dateRun and scoreDescending top-20,
  --user anvithpothula / thtennant / amanatar, kernels status of amanatar/optimized-biohub-max-score and of the NEW x138
  slug anvithpothula/biohub-0-953-lb-original, LB block counts) with a diff against the newest earlier file; a 404 on the
  old x138 slug is not a signal. CHECK TIMES after R8: 27 Sep 12:00/18:00, 28 Sep 00:00/06:00/12:00/18:00, 29 Sep 00:00
  UTC (plus the tick checks 28 Sep evening, 29 Sep 12:00/18:00 UTC). Wake mechanism: PENDING the user's answer (asked in
  chat with the round-10 brief); until then this session's own timers. At each check confirm Claude in Chrome is
  connected; a trigger with Chrome disconnected = notify the user and wait.
- 2026-09-26 16:04 UTC, PRIVATE-READ PREDICTIONS (pre-registered, calibration only, NEVER a finals input; the finals are fixed at #37 +
  #38): read on 30 Sep from the DISPLAYED 3-decimal private scores of #34 56545267 (x138 verbatim), #35 56545786 (x138 +
  insertion), P36 56555189 (x138 + leaf prune + insertion), #37 56563521 (K2) and #38 56563534 (twin). Contrasts in
  thousandths, with priors P(<0) / P(=0) / P(>0):
  C1 insertion on plain x138 = #35 - #34: 0.10-0.15 / ~0.30 / 0.55-0.60.
  C2 insertion on the K2 stack = #37 - #38: 0.10-0.15 / ~0.30 / 0.55-0.60.
  C3 lowrefine + safetail = #38 - #34: ~0.10 / ~0.80 / ~0.10.
  C4 leaf prune = P36 - #35: ~0.15 / ~0.70 / ~0.15 (lab +0.0008, public 0).
  Reading: C1 and C2 with the same non-zero sign = the insertion transfers to the private embryos. One embryo split can
  only fail to contradict the ~1/6 lab->LB rule, never confirm it. Our private result = max(#37, #38). No
  rank-vs-0.953-block reading (rivals' private = max of their own two files; the block is not all x138 copies); if one
  is reported anyway, compare only with the identifiable late x138-copy windows and label it confounded. Copied into
  research/wf_ideas_v4/round9/LESSONS_draft.md s5 (with the R10-A5 text fixes a-g).
## 9. Literature
`research/survey_detection_sparse_labels.md`, `research/survey_linking_divisions.md`, `research/discussions_summary.md`.
- 2026-09-25 14:05 UTC, T1 SAFETAIL DONE (cloud session; its only task - everything else moves to the local chat, prompt
  research/wf_ideas_v3/PROMPT_LOCAL_CHAT.md). tools/build_probe_kernel.py --patch safetail (x138 base only, applied after
  all other patches): requires --set REPAIR_DEADLINE_S=34200 (other values need --lab); gate + fail-soft around the
  DaughterNet insertion (BIOHUB_DIVINS_DEADLINE_S default 28800, 'DIVINS SKIPPED (deadline)', 'DIVINS FAILED'); sets
  BIOHUB_DEGRADE_KEEP_DIV=1 (safe divisions + linefit survive the deadline); DIVINS_DUMP=1 / DIVINS_FORCE_FAIL need --lab
  (probe.json then says "LAB/DUMMY BUILD: never submit"). tests/test_safetail.py 8/8 pass (exact-diff undo check vs the
  unpatched cell, compile, exec'd gate / fail-soft / degrade mocks, builder refusals, a K1-like build). NOT done here:
  pyflakes pass, lowrefine (T2) - the local chat builds K2 = K1 + lowrefine. Build commands (x138 exp57b insertion knobs):
    K="--set DIVINS_ENABLE=1 --set DIVINS_STEAL=1 --set DIVINS_CAP=4 --set DIVINS_FRAME_CAP=1 --set DIVINS_ALPHA=1 --set DIVINS_THRESH=0.4"
    K1: python tools/build_probe_kernel.py exp58t_x138_safe --base x138 --patch divinsert --patch safetail --set REPAIR_DEADLINE_S=34200 $K
    FD: python tools/build_probe_kernel.py exp58fd_x138_safe --base x138 --patch divinsert --patch safetail --lab --set REPAIR_DEADLINE_S=1 $K
    FF: python tools/build_probe_kernel.py exp58ff_x138_safe --base x138 --patch divinsert --patch safetail --lab --set REPAIR_DEADLINE_S=34200 --set DIVINS_FORCE_FAIL=1 $K
    branch B (no insertion): drop --patch divinsert and $K.
  Dummy gates as in FINAL_REPORT.md section e (K1 sha256 == exp57b dummy CSV; FD: 'DEADLINE' on dataset 1, insertion skipped,
  safe divisions + linefit counters > 0; FF: 'DIVINS FAILED' on every clip, CSV == exp56 dummy).
- 2026-09-26 09:40 UTC, cloud check-in (scheduled research day 2): all five NEXT_RESEARCH.md questions were already answered
  by the local chat overnight (runtime clean, branch A, exp60 riders closed, K2 #37 = 0.954 above the x138 block, finals
  ticked); cloud recorded them in research/wf_ideas_v3/day2_findings.md and schedules no further check-in (budget); open
  lines stay with the local chat.
