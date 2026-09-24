# Browser research 2026-09-24, PASS 2: x138 training recipe, new notebooks/datasets/threads, CTC swap fixes

Status: written in stages (append after every 2-3 sources). First pass: research/browser_research_2026-09-24.md.
Base: our best public 0.948 (exp48); porting the x138 V1284 coordinate head (exp51) now; top teams 0.969-0.975.
Targets: (1) thread 742965 + anvithpothula/thtennant posts on how V1284 was trained; (2) public code >= 0.950 or
published in the last 3 days; (3) datasets from the last 7 days; (4) new discussion topics; (5) CTC swap fixes.

---------------------------------------------------------------------------------------------------------
## 1. Thread 742965 and the V1284 training recipe (12:00 UTC)

- **Thread 742965** (fheizz, rank 1085, 11:35 UTC, "is the 0.953 public notebook accurate?"): still ZERO replies at
  12:01 UTC (checked via the internal GetForumTopicById API; the comments field is absent). No evidence either way.
- **x138 comment thread (742673)**: only 3 posts - URAD "There's one private dataset", Justin CH123 asking to make the
  head public, Anvith Pothula (03:04 UTC 24 Sep) "I have made the dataset public. Sorry about that." Nothing about
  training.
- **Head dataset** anvithpothula/biohub-v1284-head-s075 (CC0, v1): ONE file `v1284_head.pt`, 33,913 bytes, file
  creation date 2026-09-20 14:13 UTC; description only "produced 0.953 score in ...biohub-x138". No training code.
- **Author's kernels** (internal ListKernels, userId 27343392): biohub-v1284-head-s075-notebook (24 Sep, stub), x138,
  divqc, x56 (0.940), two "aisec-*" (another competition). x107 (the "20-movie TRAIN capture") and x122 are PRIVATE.
- **What the embedded module (x138 cell, `v1284_coordinate_refinement.py`, docstring "Frozen-feature coordinate
  regression at first-seen fused detector centers") tells us about training**, i.e. the recipe we must reproduce:
  - input x = 224-d: `feature[0,:,z,y,x]` (32 ch of `unet_out[:, f_idx]`, the PRIMARY UNet output for that frame) at
    the integer peak, then the 6 face-neighbour features MINUS the centre (clamped at the border); standardised by
    stored `mean` / `scale` (so training used z-scoring on the train capture);
  - output: `2*delta/(1+||delta||_2)` (vector-norm bound, so |shift| < 2 um in ANY direction), in um, divided by
    SPACING = (1.625, 1.625, 1.625) to voxel units; the head therefore was trained with targets in um;
  - last layer zero-initialised (training starts from "no shift"); `mode='zero'` just casts to float (an ablation mode:
    float coords + trilinear gather with NO shift - useful control for us);
  - label (inferred from the author's note "4,136 detection<->GT pairs", "moves centres CLOSER to truth"): target =
    GT centre - detected peak, in um, for detections matched one-to-one to a GT node (the matching radius is not
    stated); evaluation = mean detection-to-GT distance, pooled and per movie, HELD OUT BY MOVIE; ridge and MLP gave
    the same -10.8 % / -10.4 %; 16/20 movies improve; 4 movies of data made it +14.9 % WORSE.
  - **4,136 pairs over 20 movies = ~207 pairs per movie**, i.e. only the ANNOTATED nodes (sparse labels). Our 199-video
    capture would give ~40k pairs (10x the author's data) - the author's own note says volume was the limiting factor.
  - "s075" is not explained anywhere public; nothing in the module scales by 0.75, so it is either a training-side
    shrinkage of the target (e.g. target x 0.75) or a run name. **Check when the port agent mounts the .pt: print
    `saved.keys()` - any extra metadata key would reveal it.**
  - No augmentation is possible/needed (frozen features, per-peak regression). Loss unknown (ridge => MSE; the MLP
    most likely MSE or Huber on the bounded output).
- **Is x138 overfit to public?** The head never sees test data; the only selection route is across the author's own
  versions (x56 ... x107, x122, x138). The 33-team spike at exactly 0.953 after the head went public (24 Sep 03:04 UTC)
  says the 0.953 REPRODUCES in forks (same public test), but says nothing about private. Private risk is the same as
  any public-selected pipeline; the held-out-by-movie train check is the only generalisation evidence.

## 2. Public Code tab, second pass (12:05 UTC; internal ListKernels, competitionId 136605)

- **Score-sorted (top 100): x138 (0.953) is STILL the ONLY public notebook >= 0.950.** Next: amanatar geometric-fusion
  0.948, then a wall of 0.947 (evgendvorkin LB-proxy, raunakdey07 HF v3, flexonafft HF + lineage-forge, reyhanksatria,
  sjlee101 lf-dctta ...).
- **No public notebook was created on 24 Sep**; the newest is tobimichigan (23 Sep 17 UTC, LB 0.1). The 33 teams at
  0.953 are running PRIVATE forks of x138.
- New since the first pass or not read then (created/run 21-24 Sep): noisyislands/biohub-transformer-finetune
  (unscored), asymortenson/biohub-v5c-final (unscored), crystalbaby/biohub-geometric-fusion (copy of amanatar),
  arnav170/biohub-reid3s (0.947), andnyu/biohub-947-synthetic-edge (0.947), andnyu/biohub-synthetic-conditional-
  third-model (0.946), mthem77/biohub-b0-harmonic-fusion-safety-re-run (0.947), denpugovkin/biohub-0-885-without-the-
  fake-lineage-hub (0.885), y3uanm notebooks (unscored). Reading the potentially relevant ones next.

- Read (12:05-12:10 UTC):
  - **noisyislands/biohub-transformer-finetune** (created 21 Sep, never scored): fine-tunes ONLY the edge transformer +
    pair_mlp of the support-pack model (UNet + detect head frozen) on GT windows AUGMENTED with production-like
    impostors: each GT node duplicated with p = 0.15 at a jitter of z +-2 / y,x +-7 voxels (the duplicate inherits its
    source's target row), plus 2 random noise nodes per frame (forced active, target 0); same masked softmax-BCE-focal
    loss as train_unet_transformer.py; lr 2e-5, 6-8 epochs, 25 windows/movie. Rationale in its docstring: clean GT
    pools lack "the production impostor distribution". No LB number, so no evidence. Relevant to our "edge network never
    scored the relink pairs" finding: a hard-negative fine-tune would let the network score duplicate/impostor pairs.
  - asymortenson/biohub-v5c-final: hard-coded lzma/base85 predictions for the 4 dummy test movies (useless).
  - arnav170/biohub-reid3s (0.947): Harmonic Fusion + appearance re-id descriptor (7x25x25 voxel patch around each node)
    in the relink cost, `BIOHUB_REID_WEIGHT` default 0 ("sweep decides") -> at the wall.
  - andnyu/biohub-947-synthetic-edge (0.947): Harmonic Fusion + bhpepper/biohub-synthetic-5fold-ensemble-v1 edge
    models -> at the wall.

## 3. Datasets updated in the last 7 days (search "biohub", sorted by update; 61 of 160 since 17 Sep)

| dataset | what it is | note |
|---|---|---|
| **georgexue666/biohub-precision-pool2-weights** (20 Sep, 46 MB, 116 downloads) | README: retrained 3D UNet HEATMAP detector, "higher spatial resolution (pool=2) and tighter physical Gaussian sigma 0.8 um", base channels 24, trained on 128 movies / 32 val ("D1.json"), checkpoint selection by Hungarian recall within 4 um at top-330 nodes/frame (best 0.7348 at epoch 22; r2 0.7304, r3 0.7290) + a pool-2 temporal edge predictor | a DETECTOR-side localisation retrain, same direction as V1284 but at the model level. No public LB number. |
| **leonixis/biohub-v5-candidates** (21 Sep, 357 MB, 82 dl) | "Per-epoch checkpoints from the all-train (199 videos, 60 epochs, warm start from v3res) run; LB checkpoint-pick set" + repo scripts | someone retrained the full primary on all 199 videos and picks the epoch on the LB |
| leonixis/biohub-deepcenter-pipeline, leonixis/biohub-p314159-pipeline (19 Sep) | pipeline packs | |
| majidaleissa/biohub-bio122-cross-domain-secondary-v1 (22 Sep, 90 dl) | 3 edge_predictor_best.pth splits (a "cross-domain" secondary) | |
| easonyanyan/biohub-exposure-bias-weights-v1 (20 Sep) | edge_predictor epochs 8/11/12/best ("exposure bias" = trained on predicted, not GT, inputs?) | |
| youyuany123/biohub-finetuned-unet-v2, bigbag1983/biohub-rudi-fold0-weights, fagbolapeter/biohub-trained-4ep | more retrained primaries / edge predictors | |
| bhpepper/biohub-synthetic-5fold-ensemble-v1 (19 Sep, 247 dl) | 5-fold synthetic edge ensemble (used by andnyu 0.947) | at the wall |
| adonis122/biohub-vm-drops (21 Sep, 237 dl) | an agent's notes: AUDIT_v24, DECISIONS x4, HOCT_extraction, PLAN_0918/0919, RECON public scan, PROBE_synth_schema | reading next |
| giorgosi/biohub-zsns00x-relay-leg* (19-20 Sep, 5-17 GB each) | huge relay caches (DivNet author's feature dumps) | |
| anvithpothula/biohub-v1284-head-s075 | the x138 head (file date 20 Sep) | |
| kvswim, rishi150805, serudeeven, fheizz | wheels / classic DoG pipelines | |

- **adonis122/biohub-vm-drops** (an agent team's notes, 83 files, mostly Vietnamese; team is at the 0.947 wall):
  - TASK8_edge_decomposition_REPORT (16 Sep; det@0.30 dump vs GT on all 199 films, per-frame Hungarian at 7 um):
    node recall at deploy threshold 0.965 = 99.63 % (worst film 93.2 %); **GT<->detection offset median 1.72 um,
    p90 3.3 um**; 0.37 % GT nodes unmatched (border 141, division 9, other 349, crowded 0); 99.35 % of GT edges have both
    endpoints kept and are inside the <= 20 um candidate pool; on 4 validator films the kernel's edge FN split:
    fragmented by the short-track filter 16, lost_to_detection 17, wrong_association 6 -> "half of edge FN come from the
    short-track filter (MIN_TRACK_LEN 6)". Their proposed fix: do not cut a short component if it contains a high
    edge_prob edge. (Consistent with our own "never-detected link" + "swap" classes; the 1.72 um median offset is the
    quantity V1284 shrinks by ~10 %.)
  - RESEARCH_model_lever_report (17 Sep): literature synthesis (HOCT, linajea, ultrack, Trackastra, CTC CLB). New
    details not in our pass 1: HOCT trains with focal loss on parental-softmax probabilities, **division-parent edges
    weighted ~3.5x**, augmentation = spatial crops, affine, feature-group dropout; HOCT edge block ablation: plain
    edge-transformer 0.922 CLB -> + line-to-line distance bias 0.926; **incremental correction: a logistic-regression
    head on FROZEN HOCT edge features + ~400 human annotations cut tracking errors 59 %**, beating a LoRA fine-tune (same
    "small head on frozen features" pattern as V1284). No LB evidence of their own.


## 4. Leaderboard + forum re-check (12:10 UTC; internal GetLeaderboard / GetTopicListByForumId APIs)

- **Histogram moved since the first pass**: 0.953 now 40 teams (41 at 12:17 UTC; was 33 at the first pass), 0.948 136 (was 139). x138 copies keep
  landing at exactly 0.953 -> strong evidence it REPRODUCES on public. Examples: Justin CH123 (rank 94, stuck at 0.947
  for days) and PavelLiashkov (bigbag1983, rank 129) are now 0.953.
- **The x138 building-block authors are well above their public notebooks: Teddy Tennant (thtennant) rank 32 = 0.959;
  Anvith Pothula rank 58 = 0.956.** Their private versions gained another +0.003..+0.006 over x138/frontier947. Neither
  has published anything newer (thtennant's latest public kernel is readmit-v1 from 19 Sep; no new datasets).
- **Who owns the new weight datasets, and what they reached** (public LB rank / score):
  - team easonyanyan (georgexue666 + easonyanyan; precision pool-2 sigma-0.8 DETECTOR + "exposure-bias" edge
    predictor) = rank 214, **0.950** (+0.003 over the wall; which part moved it is unknown);
  - bhpepper (synthetic 5-fold edge ensemble) 0.950; Majid Aleissa (cross-domain secondary edge model) 0.950;
  - leonixis (full primary retrained on all 199 videos, 60 epochs, LB-picked epoch) **0.947** - a plain all-train
    retrain did NOT pass the wall;
  - Lê Quang Cảnh / zhincez 0.952; amanatar 0.948; noisyislands (edge transformer hard-negative fine-tune) 0.947;
    adonis122 (vm-drops agent team) 0.947.
- **Top 10 (public):** 1 Sergio Alvarez 0.975, 2 yu4u 0.973, 3 Tang 0.970, 4 ymg_aq 0.970, 5 tatsutaka 0.969,
  6 unicellular 0.969, 7 VOXEL ART (ogurtsov, mikhisor, ...) 0.968, 8 Soheil Ayati 0.968, 9 slime 0.968, 10 Kayla L.
  0.967. None of the top-60 users has posted in the forum since 21 Sep (pavelsavchenkov 65 chars); no top-10 dataset or
  notebook for this competition is public.
- **Forum: 118 topics, 349 messages; nothing new since 742965 (11:35 UTC).** Keyword scan (sigma / heatmap / sub-voxel
  / refine / centroid) found one old hint that x138 later implemented: hengck23, 6 Sep, topic 738217: coordinates
  "could be subpixel and use F.grid_sample to sample feature"; and a riskier one: "refine ground truth to gt+dzxy so
  that it is still within the 7um error limit but drastically improves link probability" (i.e. train on
  tracking-friendly relabelled centres).
- Civitasmass (742266, 22-23 Sep): got past 0.947 after retraining the detector, "but not all of the LB gain from the
  retrain"; "some changes gave big local boosts but barely moved the board". You WeiLin: public notebooks are
  over-engineered, which lowers the ceiling.

## 5. HOW the V1284 training set was almost certainly built (reconstructed from x138's own validator code)

x138 carries a "VALIDATOR" block (cell ~4093-4260, off in the LB run: `BIOHUB_VALIDATOR_ENABLE=0  # in-sample train
proxy, ~11 min of GPU per run`). When on, it runs the SAME `scripts/predict_unet_transformer.py` on TRAIN movies
(`--data-dir train`, same det threshold / ILP flags), choosing per embryo prefix (44b6, 6bba) the first
`BIOHUB_VALIDATOR_N_PER_TYPE` stems, sorted "movies with a GT division first, then alphabetical". Default N = 2 ->
4 movies; N = 10 -> 20 movies. **This matches the author's note exactly: "the 4-movie version of this head was +14.9 %
WORSE" (default N = 2) and "x107's 20-movie TRAIN capture" (N = 10).** So the recipe is:
1. run the kernel with `V1284_MODE=capture`, `V1284_CAPTURE=<dir>`, validator ON with N_PER_TYPE = 10: the patched
   predict script writes, per train movie and frame, `coords` (integer peaks on the fused detector map, after the
   0.965 threshold, BEFORE association) + `features` (224-d);
2. offline: match captured peaks to GT nodes (one-to-one; radius not stated) -> 4,136 pairs (~207/movie = the
   annotated nodes only);
3. target = GT position - peak position (um); z-score features (store mean/scale); fit ridge and the 224-32-3 MLP with
   the bounded output; evaluate mean distance held out BY MOVIE (-10.8 % ridge, -10.4 % MLP, 16/20 movies better).
Implication for us: nothing in the recipe needs the GPU beyond the capture pass; we can capture all 199 train movies
(the validator path, N_PER_TYPE large, or our own lab runner) and train on ~40k pairs on CPU in minutes. Caveat: the
primary UNet was trained on these 199 movies, so train-set features are in-sample (sharper than on test). The public
head has the same caveat and still gave +0.007 on public.

## 6. Outside Kaggle (target 5), part 1

- **CELLECT** (Zhou et al., Nature Methods 22, Nov 2025, https://www.nature.com/articles/s41592-025-02886-x): sparse
  point annotations only (the linajea / C. elegans nih-light-sheet + mskcc-confocal protocol, like our GT). Pieces that
  map onto our failure modes:
  - centre-enhancement network (CEN): the confidence map is trained with FOUR nested label levels around each centre so
    the peak is sharp; with fewer levels "multiple redundant peaks within the same cell" appear and linking gets harder
    (Supp. Fig. 8); a 5x5x3 peak-search mask was the best trade-off (larger -> FN, smaller -> duplicate peaks);
  - an INTRA-frame MLP that learns to remove redundant / overlapping centre predictions of the same cell (a learned
    duplicate suppressor; our analogue: hengck23's "multiple nodes matched to one GT node steal the link");
  - an INTER-frame MLP scoring 5 spatially nearest candidates + a "none" slot + a division flag; spatial-distance
    candidate selection beat feature-distance selection in dense late-stage regions;
  - errors are reported by type (FP edge, FN edge, identity switch, FP/FN division) per 1,000 GT edges; remaining errors
    concentrate in low SNR, poor axial resolution and dense late-stage clusters. Post-processing (track reconnection in a
    temporal window, pruning of redundant branches) was used only for the neuron data set, not for the benchmarks.
  - Take-away for us: no swap-specific post-processing; the gains come from sharper centres + a learned duplicate
    suppressor + a "none" option in association.

- **linajea + cell-state classifier + sSVM** (Hirsch et al., MICCAI 2022, https://arxiv.org/abs/2208.11467), C. elegans,
  sparse point GT, errors per 1,000 GT edges (Tables 1-2, mskcc-confocal 270 frames):
  - a 3D ResNet18 cell-state classifier (parent / daughter / continuation / polar body) enters the ILP as node labels
    with consistency constraints (a selected edge from a "parent" must go to a "daughter" and vice versa; exactly one
    state per selected node); **FP divisions 0.89 -> 0.11 (-88 %) with FN divisions flat (0.26 -> 0.27); division
    errors 1.2 -> 0.38; total 10.3 -> 9.5**; sSVM weight learning ~ equal to a tuned grid; polar-body filter trims FP
    edges 3.7 -> 2.5. nih-ls: FPdiv 1.5 -> 0.20. Identity switches are tiny there (0.03-0.06 / 1,000 edges).
  - Mapping to us: our DaughterNet is used post hoc (insertion with steal); the evidence says the bigger win of a
    division classifier is PRECISION when it constrains the solver (parent->daughter consistency), not insertion.
- **MAMHT / "Cell tracking according to biological needs"** (Kaiser, Schier, Rosenhahn, IEEE TMI 2025,
  https://arxiv.org/abs/2403.15011, code https://github.com/TimoK93/BiologicalNeeds): displacement uncertainty from
  TTA (flips/rotations + spatial shifts of +- the mean cell radius) -> Murty k-best assignments (A_max 7) -> multi-
  hypothesis tracking (H_max 150) with Erlang cell-cycle mitosis costs; ablation (2D sets): k-best off -4.9 % CCA,
  mitosis costs off -1.8..-11.8 %, Kalman instead of learned motion -4.6..-17 %. 2D only; no 3D numbers.

- **KTH-SE / Baxter Algorithms track linking** (Magnusson, Jaldén et al., "Global linking of cell tracks using the
  Viterbi algorithm", IEEE TMI 2015, https://doi.org/10.1109/tmi.2014.2370951 ; CTC page
  https://celltrackingchallenge.net/participants/kth-se/): tracks are added ONE AT A TIME, each the Viterbi-optimal path
  through the WHOLE sequence given the tracks already placed, with "a novel way to alter previously created tracks when
  new tracks are created" (a new track may take over detections of an existing one, which is re-routed). This is the
  classic swap-repair mechanism: the decision is made on whole-track likelihood, not per frame pair. Long-time top-3 on
  the CTC. For us the cheap analogue is a local 2-opt: for two relink edges (a->b, c->d) whose crossed version
  (a->d, c->b) is geometrically admissible, compare the two options on a multi-frame cost (neighbourhood-flow
  residual over t-2..t+2 + edge-network probability where scored) and swap if better.
- CLB leaderboard (celltrackingchallenge.net/latest-clb-results) is published as a 6,145 x 1,635 PNG; per the search
  snippet the Fluo-N3DH-CE linking-only top-3 are LNK 0.984 / 0.977 / 0.960, BIO 0.862 / 0.782 / 0.667 (HOCT / CZB-US is
  the current #1 generalist, already covered in pass 1).
- Other new-data notes: majidaleissa/biohub-bio122-cross-domain-secondary-v1 (team at 0.950): manifest says "Each test
  microscope family uses only the model trained on the other family" (44b6 test movies scored by the 6bba-trained
  secondary and vice versa), "reciprocal real-domain fine-tuning from synthetic SWA initialization"; primary, solver and
  event logic unchanged. Neither thtennant nor anvithpothula has ever posted in the competition forum; thtennant's
  kernels have 0 comments.

---------------------------------------------------------------------------------------------------------
## 7. RANKED IDEAS after pass 2 (what could move 0.948 -> 0.97, each with a test)

Changes to the current plan:
- **No public notebook above 0.953 exists; 41 teams now sit at exactly 0.953** (x138 reproductions). 0.953 is the new
  wall: our exp51 (exp48 + V1284) only keeps pace. Its authors are at 0.959 (thtennant) and 0.956 (anvithpothula)
  privately, so the stack has more headroom than the public version shows.
- The V1284 training recipe is recoverable (section 5): validator capture on TRAIN movies with N_PER_TYPE = 10 ->
  4,136 pairs; we can capture 199 movies (~40k pairs).

1. **Ship V1284 on exp48 (exp51), with a "zero" control** (float coords + trilinear gather, no shift;
   `V1284_MODE=zero`). Evidence: single-variable public step 0.946 -> 0.953; 41 teams reproduce 0.953. Test: lab replay of
   the head on captured features (mean matched distance and 7 um match count per embryo), then probe exp51; the zero
   control, if a slot is spare, tells whether the gain is the shift or the float geometry. Expected +0.004..+0.007.
2. **Retrain the head on all 199 train movies** (the author: volume, not concept, was the limit; 4 movies -> worse, 20
   movies -> -10.4 % distance). Recipe: capture (coords + 224-d features) on all train movies in one Kaggle GPU pass,
   match to GT one-to-one (<= 4 um), target = GT - peak in um, z-score, ridge vs 224-32-3 MLP with the bounded output,
   leave-embryo-out AND leave-movie-out evaluation; try a target shrink (0.75, a guess at "s075") and per-axis output.
   Ship only if held-out distance beats the public head on both embryos AND the lab replay agrees. Expected +0.001..0.004.
3. **Attack the swap class (25 % of our FN, oracle +0.032) where it is born: the motion relink on never-scored pairs.**
   (a) V1284 centres (item 1) reduce the ambiguity; (b) the neighbourhood-flow prior (x138/thtennant flow2, part of
   the 0.953 stack); (c) a 2-opt swap test on relink edges with a multi-frame cost (KTH-SE principle; MAMHT: k-best
   assignments worth 4.9 % CCA on a 2D CTC set); (d) let the edge network score the pairs the relink creates: a hard-negative fine-tune of the
   edge transformer with duplicate/impostor nodes (noisyislands recipe: dup p 0.15 at z+-2 / yx+-7 voxels, 2 noise
   nodes/frame, lr 2e-5, 6-8 epochs), or simply run the existing network on relink pairs at inference. Test: lab replay,
   report the FN-class table (b_swap count) and per-embryo delta. Expected +0.002..+0.008 if (c)/(d) convert even 1/4 of
   the swap oracle.
4. **Edge filter (probes 29/30)** - still the decision point; nothing in pass 2 changes it. Stack with 1-3 if it holds.
5. **Use the division classifier as a solver CONSTRAINT for precision, not only for insertion** (linajea + csc: FP
   divisions -88 %, FN divisions flat, Hirsch et al. 2022). Our public divJ ~0.36 with ~0.1 weight: halving FP forks at
   fixed recall is worth roughly +0.002..+0.004. Test: in the lab, veto ILP/relink forks whose parent is not
   DaughterNet-"parent" and whose children are not "daughter"; score division P/R and the total per embryo.
6. **Detector precision retrain (the top-team route; long shot for 5 days).** Public evidence: team easonyanyan
   (georgexue666 CC0 "precision pool-2, sigma 0.8 um" UNet heatmap detector, recall@4 um 0.735, + an "exposure-bias"
   edge predictor) = 0.950; Civitasmass retrained and passed 0.947; Tang (3rd): "most of the gains come from model
   improvements"; leonixis' plain all-train 60-epoch retrain = 0.947 (no gain). So a retrain only pays when it targets
   localisation (tighter sigma, higher resolution), not just more epochs. Test: only if GPU quota allows - fine-tune the
   primary's detection head with sigma 0.8 um on 199 movies, evaluate matched distance + recall@4 um vs V1284.
7. **Short-track-filter guard** (adonis122 TASK8: on 4 films half of the kernel's edge FN came from MIN_TRACK_LEN 6
   cutting components): keep a short component if it contains an edge with high network probability. Risk: adds nodes
   (the node-count trap), so accept only on J, both embryos. Expected 0..+0.002.

Do NOT spend slots on: plain primary retrain (leonixis 0.947), appearance re-id terms in the relink (arnav170 0.947),
synthetic edge ensembles (0.947-0.950), association-rule variants (0.943-0.946).
