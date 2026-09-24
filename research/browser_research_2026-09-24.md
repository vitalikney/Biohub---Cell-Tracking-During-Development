# Browser research 2026-09-24: what could move us from 0.948 toward 0.97

Status: written in stages (laptop crash at ~11:37 UTC). Sections are appended as sources are read.
Our base: public LB 0.948 (probe 28 = exp39 + leaf prune + DaughterNet insertion); probes 29/30 (edge filter
ef_a3_rl_pr / drop-only ef_a0) pending. Stack = sjlee101/biohub-lf-dctta-v020 lineage.

---------------------------------------------------------------------------------------------------------
## 0. HEADLINE (read this first)

**A public notebook scores 0.953, well clear of the 0.947 wall, and its one new ingredient is a learned
coordinate-refinement head.** `anvithpothula/biohub-x138` (https://www.kaggle.com/code/anvithpothula/biohub-x138),
public LB **0.953**, GOLD, 148 votes, one version, run 21 Sep. Its weights dataset
`anvithpothula/biohub-v1284-head-s075` (https://www.kaggle.com/datasets/anvithpothula/biohub-v1284-head-s075,
CC0, made public 24 Sep after Justin CH123 asked; before that forks could not reproduce it) is described as "produced
0.953 score". Our previous code-tab scans missed it because it sat in the list with a generic title.

What x138 is (read from the kernel source via the Kaggle kernels-pull endpoint in the browser, cells 0, 4, 5):
1. The Harmonic Fusion / lf-dctta stack (the same one we use), config identical to the public 0.947 family
   (det 0.965, ILP disappear 2, div 1.2, gap 5.0, min track len 6, safe-div 9/14, DeepCenter veto + TTA, tight55).
2. **V1284 coordinate refinement head** (the new piece). Code lives in the notebook; key facts:
   - a 224 -> 32 -> 3 MLP (`Linear(224,32), SiLU, Linear(32,3)`, last layer zero-initialised) on FROZEN UNet
     features sampled at each detected peak: the 32-channel feature at the centre voxel plus the 6 face-neighbour
     differences (7 x 32 = 224), standardised with a stored mean/scale;
   - output is a bounded displacement, `2*delta/(1+|delta|)`, i.e. at most 2 um, converted with spacing 1.625 um;
     the run raises if any shift exceeds 2 um;
   - applied right after peak extraction (`arr = _v1284_refine(...)` before `coord_offset[t] = ...`), and the patch
     **removes `coords = coords.astype(np.int16)`**, so sub-voxel coordinates survive association and output;
   - the edge transformer's feature lookup is replaced by a **trilinear** gather at the float coordinate
     (`UNetNodeTransformer._index_features = _v1284_index`), identical to the native gather at integer coordinates;
   - training (author's comment): "Trained on x107's 20-movie TRAIN capture (4,136 detection<->GT pairs). Held-out BY
     MOVIE it moves centres CLOSER to truth: ridge -10.8% mlp -10.4% POOLED, 16 of 20 movies improve. The 4-movie
     version of this head was +14.9% WORSE, so the null there was volume, not concept." A `capture` mode in the same
     module dumps (coords, features) per frame to build the training set.
3. Four relink/gap add-ons ported from the `thtennant/biohub-frontier947-*` series (agent-generated notebooks):
   - **neighbourhood-flow motion prior in the motion relink** (`BIOHUB_MOTION_RELINK_FLOW_MODE=seed`, K=12, radius
     40 um, exclude 1.5 um, min 4 samples, flow tight gate 7 um): per frame, a tight Hungarian "seed" pass gives
     confident matches; each source's next position is predicted as source + MEDIAN displacement of its 12 nearest
     seed matches (its own match excluded), then all sources are re-assigned on the distance to that predicted
     position, admitting a pair if either raw or motion distance is inside the gate. Comment: "Cells move with their
     neighbours, so a displacement field sampled from confident links predicts a source's next position better than
     its own last step (experiments/motion_model_audit.py)". Cost = motion distance - 1.0 x learned prob (unscored
     pairs still get prob 0).
   - **readmit**: detector peaks the ILP discarded, score >= 0.965, not within 2 um of a kept node, are re-added
     when within 4 um of an open track end (t-1) or start (t+1); then the relink runs again. Log on the 4 dummy
     test movies: +84 / +94 / +497 / +662 nodes (0.4-3.2 %).
   - **gap filler on sub-threshold peaks** (`GAPFILL_MAX_GAP 3, MIN_SCORE 0.5, STEP 5 um/frame, PEAK_RADIUS 3.5 um,
     EXCLUDE 2 um, ALLOW_SYNTHETIC 0, CONTEXT 1, MAX_ADDED_FRAC 0.03`): after the single-frame closer and gap2, bridge
     a track end at t to a start at t+g+1 (g = 1..3) only if a free detector peak with score >= 0.5 lies within
     3.5 um of the straight-line interpolation at EVERY missing frame; direction test rejects bridges that reverse the
     neighbouring steps (cos <= -0.25); pairs assigned by Hungarian on span/(g+1) + mean peak deviation, shorter gaps
     first; capped at 3 % added nodes. Log: +3 to +67 nodes per dummy movie.
   - the low-detection dump (peaks >= 0.3 saved per frame) that feeds readmit and gapfill.
4. Filter order in `filter_output_graph`: edge filter -> motion relink (flow) -> readmit -> relink again -> single-
   parent / single-child repair -> close_single_frame_gaps -> recover_strict_gap2 -> gapfill -> safe divisions ->
   division geometry filter -> prune isolated -> short-track filter -> linefit.

Attribution of the +0.006: thtennant's components alone scored 0.947 (flow2 v1), 0.946 (flow2 det096), 0.947
(gapfill v1, gapfill det096), 0.946 (readmit v1), 0.942 (divprec) - none above the wall. The author's earlier
notebooks: x56 = 0.940, dual-seed harmonic = 0.928. So the step to 0.953 is most plausibly the V1284 refinement
(+ float coordinates + trilinear features), possibly interacting with flow/readmit/gapfill. One public run; public
noise for this family is about +-0.003, so +0.006 is outside noise but not by much.

Why this matters for us: it is a DETECTION-side (localisation) gain that is shippable in 4 days, touches no
model weights, and is consistent with three independent observations below (annotation offset vs detector,
hengck23's "centroid vs cell corner" domain shift, Lime1123's "divisions need ~3 um accuracy").

Caveat on transfer: the head is trained on features of the PUBLIC primary model. If our primary differs (fine-tuned
exp03B etc.), the frozen-feature head is on a different feature space -> retrain the head on our own features
(cheap: 4k pairs, tiny MLP, CPU-trainable).

---------------------------------------------------------------------------------------------------------
## (a) Concrete hints from top / named participants (discussion forum, all 117 topics pulled via the forum API)

Ranks are the `competitionRanking` shown next to names on 24 Sep. Earlier digests (research/discussions_summary.md)
cover most threads up to 24 Sep 10:00; below are the hints with a technical payload, old and new, in one place.

| who (rank) | hint | link |
|---|---|---|
| Sergio Alvarez (1) | Every node/edge removal he made moved public LB/CV; unbounded node multiplier is intended by hosts. Synthetic volumes (PolNet-style) ~2 weeks, no gain, dropped. Public Ultrack embryo 2024_03_22_dorado is a different embryo, same spacing, usable for validation (cut 64x256x256 chunks). | /discussion/739686, /739731, /741386 |
| Tang (3) | Retrain the model instead of using the public ckpt; gains from preprocessing + architecture; the ckpt "hit a wall", post-processing alone won't go further. Order: detection -> linking -> division. "most of the gains come from model improvements." | /discussion/734604, /737543 |
| Ogurtsov (7) | 0.947 -> 0.957 "reachable to some extent but pretty risky" for private; "room for improvement in all directions". Removing random nodes/edges reduces score a lot. | /discussion/741749, /742169, /739686 |
| Masha Mikhisor (7) | Validates on external embryos (public Ultrack zebrafish) - i.e. a third embryo for validation. | /discussion/741386 |
| Soheil Ayati (8) | **Break missed edges into (i) missing endpoint nodes and (ii) incorrect associations; many "linking" issues actually originate in node selection, so improving the edge model won't necessarily help. Validate complete movies with the official scorer and movie-level OOF splits.** | /discussion/737101 |
| Tom (24) | Frozen/duplicated frames list per video; napari "celltrack-studio" viewer to see t->t+1 matching errors. | /discussion/724283, /724130 |
| Antonoof (26) | Deleting 44.7 % of nodes left public LB at 0.954 (later "maybe I was mistaken"). | /discussion/739686 |
| Mark (26) | Any smarter motion linker = exactly +0.001 LB while CV moves 0.01-0.03. | /discussion/739685 |
| TWEAK (26) | Claims a generic "plugin" giving +0.03..0.05 on public models (no details). | /discussion/735352 |
| mige551 (34) | Two-seed blend reduced nodes 1.7 % and helped: model diversity improved detection PRECISION. | /discussion/730924 |
| Michael Hernandez (35) | Node factor has no ceiling; example 44b6_0b24845f: J 0.98 with node ratio -0.29 -> adj 1.0102. | /discussion/739018 |
| Pavel (54) | Edge-weight model +0.02..0.04 on 5 folds incl. cross-embryo, +0.000 LB. "0.850 CV -> 0.914 LB, 0.919 CV -> 0.914 LB". | /discussion/739352, /741651 |
| Quantizr (57) | Many train annotations look wrong (centroids > 7 um off, wrong links, fake divisions). | /discussion/742942 |
| Komil Parmar (74) | Trained from scratch; training is affordable. | /discussion/735352 |
| Justin CH123 (93) | 10 single-knob LB tests: LB loss tracked the change in predicted node count on test, not offline edge J. Final edges come from the Hungarian relink; network prob enters only via bonus (<= ~1 um vs 1.8 um median step). | /discussion/742266 |
| Lê Quang Cảnh / zhincez (116) | Division base rates (continuation median 1.72 um, division step 4.57 um, sister 8.85 um); second daughter arc needs ~2x gate; relink destroys ILP forks; constant offset correction loses 0.0031, "a learned per-node offset is the only version that can pay" (x138 confirms); dense-label encoder fine-tune -0.038; contested links: velocity extrapolation picks the true child 0/381 times. | /discussion/740573, /732103, /738217 |
| Lê / zhincez notebook "The metric pays you to delete nodes" | **Node-deletion trap measured on LB**: min-track-len 6 -> 10 (+det 0.98, per-embryo 44b6=20/6bba=10) = +0.013 offline (validator 0.9368 -> 0.9495), public LB 0.938 -> **0.934**; own pipeline 0.9523 offline -> 0.865 LB. Label coverage 44b6 0.2-1.3 %, 6bba 13-15 %, so deletions look free on 44b6. Advice: always split score into J and node multiplier; distrust gains that are > 70 % multiplier. | https://www.kaggle.com/code/zhincez/the-metric-pays-you-to-delete-nodes |
| Hammad Farooq (118) | In-kernel PP sweep always picks tight55 (proxy 0.9490 -> 0.9511). HOCT veto has a 10 h deadline risk. | /discussion/741242 |
| Civitasmass (120) | Stuck at 0.947 a month; retrained detector, but "not all of the LB gain from the retrain"; check whether local gains are spread across all videos or driven by 1-2 outliers. | /discussion/742266 |
| OmerZalman (122, ~0.95) | "you have to improve all parts"; a 0.969 player told him the same. | /discussion/742266 |
| Arul Prasad (134) | A fork-free submission returns pure adj edge J (summarise drops the division term) - one probe gives the exact edge/division split. HOCT with ball masks over-links, 45 min/movie. | /discussion/734192, /728551 |
| Lime1123 (145) | **Divisions are sensitive to spatial accuracy within ~3 um even though the metric uses 7 um**; LB divJ ~0.28 with adjJ ~0.89. kevin park then found 39 % of his division nodes > 3 um off. | /discussion/737543 |
| sghwr (145) | Local CV pessimistic vs LB by 0.013-0.02; blind human review: ~70 % of their model's FPs could be TPs (annotation noise). | /discussion/739352, /742942 |
| OpPrime (171) | Division links lost at every stage (before ILP, in ILP selection, blocked by relink/validation); GT-centred candidate results collapse on detector outputs; crowded neighbourhoods hardest. | /discussion/742266 |
| hengck23 (1161; researcher, not a leader here) | (1) **"multiple nodes matched to GT node and kaggle metric only consider first 2 - your edge may be linking to other matching node"** -> duplicates near an annotated cell steal links; (2) Kaggle annotation sits on Ultrack-segmentation points, sometimes "cell corners" vs true centres -> localisation domain shift; (3) best way to reduce nodes = cluster and represent by centroid; (4) Ultrack's pretrained segmentation gives fg/boundary probabilities that estimate T_est (the organisers' node estimate); (5) e2e linker: raw edge J 0.902 / 0.896 without / with his ILP (dense focus3d labels + augmented frames); (6) Ultrack selects hypotheses over ALL frames (best trajectory), not one or two; (7) break validation down: T_pred, matched nodes, error distance, misses (gap length) vs FP. | /discussion/740145, /738217, /732103 |

Net from the forum: nobody above 0.95 has disclosed a method. The only public >0.95 evidence is x138
(localisation refinement). Linker-only changes repeatedly give ~+0.001 on LB; node-count-only changes
repeatedly look great offline and lose on LB.

---------------------------------------------------------------------------------------------------------
## (b) Linking-related public notebooks (Code tab, score-sorted + date-sorted lists via the Kaggle internal API)

Public scores (bestPublicScore) as of 24 Sep:

| notebook | LB | what it changes in linking / nodes |
|---|---|---|
| anvithpothula/biohub-x138 | **0.953** | V1284 coordinate refinement + float coords + trilinear features; flow-prior relink; readmit; sub-threshold gapfill (see section 0) |
| amanatar/biohub-geometric-fusion (v4) | 0.948 | Harmonic Fusion + extended in-kernel PP sweep (DeepCenter safe-div 0.15/0.10, wider div windows, diverge 1.5, minlen5, rescue 0.85, vel 0.75) with a per-embryo-prefix guard (reject if any embryo drops > 0.001) + **weak-leaf pruning**: drop a node with out-degree 0, exactly one incoming edge with learned prob < 0.30/0.40, not on the last frame, single pass. Which candidate was selected on the LB run is not in the source. |
| thtennant/biohub-frontier947-flow2-v1 | 0.947 | neighbourhood-flow prior in relink only |
| thtennant/biohub-frontier947-gapfill-v1 / -det096 | 0.947 / 0.947 | sub-threshold peak gap filler |
| thtennant/biohub-frontier947-readmit-v1 | 0.946 | readmit discarded peaks at open ends |
| thtennant/biohub-frontier947-divprec-v1 | 0.942 | division precision variant (lost 0.005) |
| haideptry/biohub-sota-0-948-mutual-best-density-2xt4 | 0.943 | mutual-best association + density-adaptive gates (title inflated) |
| haideptry/biohub-0-951-sota-deepcenter-fast-ilp-19m | 0.944 | density-adaptive relink + DivNet veto (title inflated) |
| yudaiyamauchi/lb-exploration-a..e (hard-negative margin, relative rank, disagreement-adaptive, mutual-best) | 0.944-0.946 | association-score variants; all at or below the wall |
| andnyu/biohub-947-mutual-rank | 0.945 | mutual-rank association |
| seyitkaangunes/biohub-035-deconfounded-edge-stack | 0.946 | edge stack variant |
| pawanmali/biohub-zhincez947-nodiv-ablation-v1 | 0.911 | zhincez 0.947 with divisions OFF: -0.036 => divisions (division term + division edges) are worth ~0.036 on this stack |
| binasalama/...-gap-recovery | 0.887 | learned gap recovery - loses |
| kunaldesale2408/biohub-cell-tracking | 0.942 | confidence-distance edge gate |
| giorgosin/notebook447aed80b2 | unscored | appearance-aware edge predictor work (DivNet author) |

Take-away: association-rule variants (mutual-best, rank, hard-negative margins) are all 0.943-0.946; gap-filling
and readmit alone are neutral; the only clear winner is the localisation refinement.

---------------------------------------------------------------------------------------------------------
## (c) External literature read so far (numbers)

- **HOCT** (Bragantini, Theodoro, Royer; the organisers), arXiv 2607.11754, https://arxiv.org/html/2607.11754v1 :
  edge weights `w_e = (0.5 - p_e) * exp(-0.5 (dt-1))` (linear in probability, positive cost below p = 0.5), appearance
  0.5(1 - p_orphan), disappearance 0.25, division 0.25, node -10. Parental softmax normalised per target node AND per
  temporal gap. **Two-pass solve**: ILP on dt = 1 edges -> tracklets -> tracklets as meta-nodes, re-solve with all
  (dt > 1) edges. Ablation: long links alone HURT (CLB -3.2 %, BIO -5.5 %), long links + 2-pass solver helped
  (CLB +0.007 to 0.920, BIO +0.023 to 0.858).
- **Trackastra** (Gallusser & Weigert, ECCV 2024), https://arxiv.org/html/2405.15700v1 : greedy vs ILP on bacteria
  AOGM 36 -> 23 (FP edges 10 -> 7, FN 12 -> 8); parental softmax -20 % errors for both linkers (greedy 28.4 -> 23.0,
  ILP 18.8 -> 14.8); window s = 2 degrades, 3-6 all fine; association scores averaged over overlapping windows.
- **Löffler, Scherr, Mikut, PLOS ONE 2021** (KIT-Sch-GE tracker, top-3 several times in CTC),
  https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0249257 : coupled min-cost flow with skip nodes
  (gap <= 3 frames), split/merge nodes for over/under-segmentation; missing masks re-inserted at linearly
  interpolated positions; ablation on simulated 10 % FN: TRA ~0.65 without mask insertion -> ~0.80 with; 10 %
  over-segmentation: ~0.70 -> ~0.82 with untangling.
- **ITEC** (bioRxiv 2026.03.12.711203, https://www.biorxiv.org/content/10.64898/2026.03.12.711203v1.full , code
  github.com/yu-lab-vt/ITEC): iterative tracking + error correction on zebrafish/mouse/Drosophila with sparse
  lineage GT; detects missing cells from t -> t+2 skip links and re-detects them, merges over-segmentation found as
  "one cell in neighbouring frames, two in this one"; first iteration cuts errors 45-56 %, three iterations 52-72 %.
- **Kaggle metric** (github.com/royerlab/kaggle-cell-tracking-competition/blob/main/metrics.md): FP edge only when
  the predicted target matches a GT node whose GT parent is a different node, or the source matches a GT node whose
  GT child is different; everything else is ignored. One-to-one Hungarian node matching within 7 um.

---------------------------------------------------------------------------------------------------------
## (d) Ranked ideas - DRAFT v1 (written before continuing the browse; will be revised at the end)

1. **Port the x138 localisation stack: V1284 learned coordinate refinement + float coordinates + trilinear feature
   lookup.** Evidence: only public notebook above the wall (0.953); author's held-out-by-movie check: -10.4 % mean
   centre error, 16/20 movies better; Lê: constant offset loses, learned per-node offset "the only version that can
   pay"; Lime1123: divisions need ~3 um accuracy. Test: (i) replay-free sanity: on our lab's 199 videos compute the
   matched-distance distribution and node-match count at 7 um before/after refinement (needs the UNet feature maps
   -> run the capture on Kaggle GPU for ~20 movies, train the MLP on CPU); (ii) full official-metric run with and
   without the head on a movie-held-out split (train head on 20 movies, score the other ~179). Ship as LB probe:
   x138 verbatim first (reproduce 0.953), then x138-style head on our primary. Expected: +0.003..+0.006 LB.
2. **Split every local gain into J vs node multiplier, per embryo (44b6 vs 6bba), before believing it.** zhincez
   measured +0.013 offline -> -0.004 LB when the gain was multiplier-driven. Our edge-filter +0.016: check how much is
   multiplier (dropped edges -> short tracks -> short-track filter removes nodes) and whether it holds on 6bba
   (13-15 % label coverage) as well as 44b6 (0.2-1.3 %). Cheap, CPU, decides probes 29/30 interpretation.
3. **Neighbourhood-flow motion prior in the relink** (x138/thtennant flow2): replace own-velocity prediction with
   the median displacement of the 12 nearest confident matches. Alone = 0.947 (neutral) on LB, but it is in the
   0.953 stack; cheap to replay. Test on our replay: relink FP rate by class with flow on/off, esp. on the relink
   edges that our edge filter keeps.
4. **Readmit + sub-threshold gapfill with peak evidence** (x138): only bridges when a detector peak >= 0.5 exists at
   every missing frame; readmit peaks >= 0.965 within 4 um of open ends. Neutral alone on LB (0.946-0.947). Test by
   replay using the low-detection dump; expected +0.000..0.002.
5. **Weak-leaf pruning** (amanatar 0.948): drop a track-end node whose only incoming edge has p < 0.3-0.4. Our probe
   28 already has "leaf prune" - check it is the same rule.
6. **HOCT-style two-pass tracklet stitching / ILP weights (0.5 - p)**: literature-backed (+0.007..0.023 on CTC), but
   forum evidence says linker gains transfer ~+0.001 on this LB. Lower priority.

### Update 12:xx UTC - x138 ablation chain confirmed from source (single-variable on the public LB)
Pulled `thtennant/biohub-frontier947-readmit-v1` (0.946) and `thtennant/biohub-frontier947-gapfill-v1` (0.947):
- gapfill-v1 = public Harmonic-Fusion config + tight55 + flow-prior relink (`FLOW_MODE=seed`, K 12, R 40 um) + gapfill.
- readmit-v1 = gapfill-v1 + readmit (radius 4 um, score >= 0.965) + low-detection dump (0.3). **No V1284, and the
  `coords.astype(np.int16)` cast is still present.**
- x138 = readmit-v1 + V1284 head + int16 cast removed + trilinear feature gather (the author's own comments say he
  applied his patch "AFTER the readmit dump patch").
So on the public LB: flow2 0.947 -> +gapfill 0.947 -> +readmit 0.946 -> **+V1284 refinement 0.953 (+0.007)**. That is
a clean single-variable step and the strongest evidence of any idea in this report. The relink/gap add-ons are
neutral on their own.

### Update - more on x138 and the board (browser, after the crash)
- The author's profile (internal ListKernels, userId 27343392) lists `biohub-v1284-head-s075-notebook` (24 Sep) - it is an
  empty stub; the head's TRAINING code is not public. What is public: the architecture, the capture mode
  (`V1284_MODE=capture` writes per-frame `coords` + 224-d `features` npz), the saved head (`state_dict`, `mean`,
  `scale`), and the author's note (20 train movies, 4,136 detection<->GT pairs, held-out-by-movie -10.4 % centre
  error, 16/20 movies improve; a 4-movie head was worse). "s075" in the name is unexplained (maybe a 0.75 scale).
- New thread 742965 (fheizz, rank 1084, 11:35 UTC): "is the 0.953 public notebook accurate or does it overfit the
  public test set?" - no answers yet. The head never sees test data; the only overfit route is selection over the
  author's many versions (x56 ... x107, x122, x138). The held-out-by-movie check argues against pure luck.
- Public LB histogram now (3,872 teams, internal leaderboard API): 0.975 x1, 0.973 x1, 0.970 x2, 0.969 x2, 0.968 x3,
  0.967 x2, 0.966 x1, 0.965 x3, 0.964 x3, 0.963 x2, 0.962 x3, 0.961 x3, 0.960 x3, 0.959 x5, 0.958 x11, 0.957 x7,
  0.956 x12, 0.955 x14, 0.954 x15, **0.953 x33**, 0.952 x23, 0.951 x31, 0.950 x34, 0.949 x44, 0.948 x139, 0.947 x716.
  The spike of 33 teams at exactly 0.953 is what a wave of x138 reproductions would look like (its head became
  public today) - indirect evidence that 0.953 reproduces. Anyone still at 0.948 will be passed by ~150 teams.
- `anvithpothula/divqc-ground-truth-free-division-qc`: on 50 train movies his pipeline had div TP 17 / FP 19 /
  FN 56 (div J 0.185); interior orphan starts (track starts away from the boundary) are the only label-free signal
  of missed divisions; conservation counts are blind. Not actionable for us beyond confirming divisions are hard.

### Update - x138 base = our base
x138 sets `BIOHUB_EDGE_FEATURE_TTA=1`, `BIOHUB_SECONDARY_EDGE_FEATURE_TTA=1` weight 0.75, `BIOHUB_DEEPCENTER_TTA=1`,
tight 5.5, i.e. the sjlee101 lf-dctta-v020 stack we run as exp29/exp39 (only the DeepCenter safe-div threshold, 0.25 vs
our 0.20, differs). The V1284 patch hooks three anchors in `scripts/predict_unet_transformer.py`
(`coord_offset[t] = (global_node_count, ...)`, `coords = coords.astype(np.int16)`, `model, window_size, downsample =
load_model(...)`) and reads `unet_out[:, f_idx]` (the primary's per-frame features). Our probe kernels patch the same
script, so the port is a copy of one cell block plus the CC0 dataset `anvithpothula/biohub-v1284-head-s075`, as long as
the anchors match and any other patch on the same lines is applied first (the author lost a run, x122, to an anchor
collision that silently disabled the gap filler).

---------------------------------------------------------------------------------------------------------
## (e) FINAL ranked ideas (supersedes the DRAFT v1 list above)

Context from our lab (CONTEXT.md 24 Sep): exp39 on 199 videos: edge TP 122,151 / FP 6,846 / FN 6,732 (J 0.900),
annotated-node recall 0.983. FN anatomy (exp39 + edge filter): swaps 25 % of FN (oracle +0.032), never-detected
link 31 %, u-diverted / v-taken ~19 % (oracle +0.016). Public divJ ~0.36.

### 1. Port the x138 localisation refinement onto exp48 (V1284 head + float coords + trilinear feature gather)
- Mechanism: a tiny MLP on frozen UNet features (centre + 6 neighbour differences) predicts a bounded (<= 2 um)
  sub-voxel shift of each detected peak. Coordinates stay float through association and output (no int16 rounding;
  the z voxel is 1.625 um, so rounding alone adds up to 0.81 um of z error). The edge transformer reads features
  trilinearly at the refined point. Better centres win more contested Hungarian matches at the scorer (one-to-one,
  7 um) and in our own relink, gap and division gates (divisions need about 3 um, per Lime1123). That attacks the
  swap and diverted FN classes (44 % of our FN) without adding nodes.
- Evidence: public LB single-variable step 0.946 -> 0.953 (thtennant readmit-v1 -> anvithpothula x138, otherwise
  identical); author's held-out-by-movie centre error -10.4 %, 16/20 movies improve; Le Quang Canh: a constant
  offset loses 0.0031, only a learned per-node offset can pay; 33 teams now sit at exactly 0.953.
- Lab test (fits in 4 days): (a) one Kaggle GPU run with `V1284_MODE=capture` on our stack over all 199 train videos
  (features + coords per frame; about the cost of a normal pass); (b) on CPU, match captured detections to GT
  (Hungarian, <= 4 um), apply the PUBLIC head, measure mean matched distance and the 7 um match count per embryo;
  (c) post-hoc replay: shift the final exp48 output nodes that come straight from detector peaks by the head's
  offset, rescore with the official metric on 199 videos, and report dJ and the node multiplier separately (node count
  cannot change here, so any gain is J); (d) probe exp48 + V1284 patch, plus x138 verbatim as a reproducibility
  control if a slot is spare.
- Expected: +0.004..+0.007 public (the public step was +0.007 on the same base).
- Risk: anchor mismatch, or a TTA feature path that still gathers at integer coordinates. Assert the patch counts
  the way the author does, and keep the 2 um bound check.

### 2. Retrain the refinement head on more data and on our exact features
- Mechanism: same head, trained on all 199 videos with a movie- or embryo-held-out split. The author found 4 movies
  made it worse and 20 movies gave -10 % error: "the null there was volume, not concept". Options: add 3x3x3 context
  or per-axis outputs, since the known annotation bias is mostly z (dz -0.57 um, and it depends on the embryo).
- Test: the capture from idea 1 gives the training set (~40k pairs over 199 movies). Fit ridge or an MLP on CPU in
  minutes, then compare held-out distance and the post-hoc replay score against the public head. Ship only if it
  beats the public head on BOTH embryos.
- Expected: +0.000..+0.003 over idea 1. Caveat: the public detector saw all 199 videos, so train features are
  in-sample and the head may learn in-sample residuals. The public head has the same issue and still transferred.

### 3. Before trusting the edge filter (probes 29/30), split its +0.016 into J and node multiplier, per embryo
- Evidence: zhincez, "The metric pays you to delete nodes": +0.013 offline (validator 0.9368 -> 0.9495) became -0.004
  on the LB when the gain came from the multiplier. 44b6 has 0.2-1.3 % label coverage, so deleting there looks free.
  Justin CH123: LB loss tracked the node-count change.
- Test (CPU, minutes, uses existing replay outputs): for exp39 vs exp39+ef on 199 videos, report dJ, dMultiplier,
  N_pred change and the per-embryo (44b6 / 6bba) score deltas. Flag it if > 70 % of the gain is multiplier or if 6bba
  does not improve. If the gain is J on both embryos, keep it and stack it with idea 1.
- Expected: tells us whether probe 29's result can be trusted on the private LB.

### 4. Neighbourhood-flow motion prior inside the motion relink (x138 / thtennant flow2)
- Mechanism: per frame, take seed matches from a tight pass. Each source's predicted position = source + the median
  displacement of its 12 nearest seed matches within 40 um (its own match excluded). Assign on distance to the
  prediction, admitting a pair if the raw OR motion distance is <= 7 um. It targets cells that move with their
  neighbourhood and lose their target to slower cells in the tight pass: our "diverted / taken" FN class.
- Evidence: part of the 0.953 stack; alone it scored 0.947 on the LB (neutral, within noise). Le Quang Canh:
  own-velocity extrapolation picks the true child in 0 of 381 contested cases. The neighbourhood field is the
  alternative that does not depend on the cell's own history.
- Test: replay the relink on cached exp39 graphs with flow on and off (the code is ~150 lines in x138 cell 5,
  `motion_relink_edges`) and score by FN class. It must be combined with our edge filter, because unscored pairs
  still get prob 0 in its cost.
- Expected: 0..+0.002.

### 5. Readmit discarded peaks + evidence-gated gap filler (x138 / thtennant)
- Mechanism: readmit detector peaks the ILP discarded (score >= 0.965, > 2 um from kept nodes) that lie within 4 um of
  an open track end or start, then relink. Bridge gaps of 1-3 frames only if a sub-threshold peak (>= 0.5) lies within
  3.5 um of the interpolation at every missing frame (no synthetic nodes, <= 3 % added nodes). It targets our
  "never-detected link" class (31 % of FN) with evidence instead of blind interpolation.
- Evidence: neutral on the LB alone (0.946-0.947). Literature: ITEC's missing-cell re-detection from t -> t+2 skips
  cut zebrafish errors 45-50 % in its first iteration; Loeffler et al.: re-inserting missed objects raised TRA from
  0.65 to 0.80 at 10 % simulated FN.
- Test: needs the low-detection peak dump (capture it in the same GPU pass as idea 1). Replay on 199 videos and report
  added nodes and dJ per embryo.
- Expected: 0..+0.002 (worth it only if the lab shows J gains on both embryos).

### 6. HOCT-style scoring in the relink/ILP: cost (0.5 - p), parental softmax per target, two-pass tracklet stitching
- Evidence: HOCT ablation: long links alone -3.2 % CLB, with the two-pass solve +0.007 CLB / +0.023 BIO. Trackastra
  parental softmax: -20 % errors. Our own stitch rule: +0.0020 locally but it fails the per-embryo gate. Forum: linker
  gains transfer at about +0.001 (Mark, Pavel, Yubo, Justin).
- Expected: 0..+0.002; lowest priority for a 4-day window.

### Do NOT spend slots on
- node-count-only levers (min track length, detection threshold, blind pruning): zhincez -0.004, caassicca det 0.99
  -0.005, and all ten of Justin CH123's knob changes lost;
- association-rule variants (mutual-best, relative rank, hard-negative margins): 0.943-0.946 on the LB;
- synthetic-data division classifiers (Juan Neira 0.910 -> 0.906) and HOCT as a black box (over-links, slow).

### Realistic path toward 0.96+
0.948 (exp48) + idea 1 (~+0.005) + the edge filter if it transfers (probe 29) + idea 2 -> ~0.955-0.960. The
0.965-0.975 teams have not disclosed anything. Tang (3rd) says most of his gain came from retraining the model
(detector first); Sergio (1st) says every node/edge change moved his LB. Beyond ~0.96 the evidence points at detector
retraining, which does not fit in a 4-day window.

---------------------------------------------------------------------------------------------------------
## Sources
- x138 notebook: https://www.kaggle.com/code/anvithpothula/biohub-x138 ; head dataset (CC0):
  https://www.kaggle.com/datasets/anvithpothula/biohub-v1284-head-s075 ; comments: discussion 742673 (Justin CH123,
  Anvith Pothula), 742965 (fheizz)
- thtennant chain: https://www.kaggle.com/code/thtennant/biohub-frontier947-flow2-v1 ,
  https://www.kaggle.com/code/thtennant/biohub-frontier947-gapfill-v1 ,
  https://www.kaggle.com/code/thtennant/biohub-frontier947-readmit-v1
- amanatar weak-leaf pruning + prefix-guarded sweep: https://www.kaggle.com/code/amanatar/biohub-geometric-fusion
- zhincez node-deletion trap: https://www.kaggle.com/code/zhincez/the-metric-pays-you-to-delete-nodes
- pawanmali divisions-off ablation 0.911: https://www.kaggle.com/code/pawanmali/biohub-zhincez947-nodiv-ablation-v1
- divqc: https://www.kaggle.com/code/anvithpothula/divqc-ground-truth-free-division-qc
- Forum threads (prefix https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/):
  737101 (Soheil Ayati), 737543 (Tang, Lime1123), 734604 (Tang), 741749 (Ogurtsov, hikaggler), 742169 (OmerZalman,
  Ogurtsov), 742266 (Justin, OmerZalman, OpPrime, Civitasmass), 739686 (Antonoof, Sergio, Ogurtsov), 739685 (Mark),
  739352 (Pavel, sghwr), 742942 (Quantizr, sghwr), 740573 / 732103 / 738217 / 740145 (Le Quang Canh, hengck23),
  741386 (Masha, Sergio), 741242 (Hammad Farooq), 739018 (Michael Hernandez), 734192 / 728551 (Arul Prasad),
  730924 (mige551)
- Metric: https://github.com/royerlab/kaggle-cell-tracking-competition/blob/main/metrics.md
- HOCT: https://arxiv.org/html/2607.11754v1 ; Trackastra: https://arxiv.org/html/2405.15700v1 ;
  Loeffler et al. 2021: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0249257 ;
  ITEC: https://www.biorxiv.org/content/10.64898/2026.03.12.711203v1.full ;
  linajea (movement vectors, no ablation): https://www.biorxiv.org/content/10.1101/2021.07.28.454016v1.full
