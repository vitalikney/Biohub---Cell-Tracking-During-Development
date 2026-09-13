# Kaggle discussion digest (read 2026-09-06 via browser; sorted by votes)

## Facts from the hosts (Thibgolds, Jordão Bragantini)
- Test set: ~similar size to train, **two different embryos, no embryo overlap with train**; same instrument, protocol and
  developmental stage; each embryo = separate imaging session. Public LB ≈ 29% of test, private 71% (participants
  guess public = one embryo, private = the other + rest). Test folder's 4 clips are dummy copies of train clips. (716793, 724386, 716062)
- Images: multi-view fused, views linearly scaled to a reference; custom light-sheet (Tomer 2012 design). (724582)
- Division-metric exploit (far-away hub + fake forks) patched 17 Jul; divisions now need genuine parent->2 daughters
  within 7 um; edges spanning >1 frame are dropped; duplicate edges collapsed. All submissions re-scored. (727154, 733877)
- Zebrahub imaging + tracking data explicitly ALLOWED as external data (no overlap with test). Hand labelling not
  answered by hosts; community view: allowed except test data. (734330, 737103)
- HOCT (host's higher-order tracking transformer): inference code + weights at github.com/royerlab/hoct; needs
  segmentation masks; a participant fed synthetic balls -> over-linked, 45 min/movie, not viable as-is. (726521, 728551)
- GT annotations are sparse and likely produced by an open-source tracker (ultrack) + manual correction; "sparse
  annotations are not random tracks, they are difficult tracks" (hengck23). Some GT edges wrong (rare); GT jumps
  when frames are duplicated/dropped (frozen frames exist: identical consecutive volumes, yet GT moves up to 8.9 um);
  boundary cells annotated as two tracks with a gap. (724283, 729053, 729082, 726381)

## Metric behaviour (confirmed by several people, matches our findings)
- score = adj_edge_J + 0.1*div_J; adj factor = 1 - 0.1*(N_pred-N_est)/N_est, **no ceiling** -> fewer nodes than
  estimate is a bonus; scores > 1 possible. Over-detection is "almost free": 10% more nodes costs 1%. Node matching
  is one-to-one, so duplicated detections cost ~9% and gain nothing. (728300, 739018, 733877)
- A one-to-one (Hungarian) linker gets division_J = 0 by construction: 0.1 of score left on the table. (733877)
- One participant measured LB division_J ≈ 0.22 by switching divisions off: LB 0.929 -> 0.907. So divisions ARE worth
  ~0.02 on LB for a good pipeline. (739516)
- Rule-based author: detection gains transfer CV->LB ~1:1; graph add-ons (his division edges) raised CV but LOWERED LB
  (0.784 -> 0.778); gap closing neutral on LB. (716952)

## Validation / generalisation warnings
- Public pilkwang checkpoints were trained on ALL 199 videos (split_manifest lists 199 train). Validating them on
  train videos is leakage; corrective post-processing stages look harmful locally but help on LB (one person measured
  +0.018 locally, -0.003 on LB for the same change). (730160)
- Top-30 participant (Mendrika, 28th): public LB is ~10% more optimistic than leave-one-embryo-out CV; per-movie
  variability huge (0.46..0.98, CV 18%). Uses **leave-one-embryo-out for model selection**. (730160, 739570)
- Embryo heterogeneity: 44b6 ~1% annotated, 26 divisions; 6bba ~9% annotated, 125 divisions. (732103 comments)
- Detector trained on sparse GT overfits after ~5-10 epochs: unlabelled nuclei turn into negatives, peaks/frame
  climb, node-count penalty kicks in. Early-stop on the real metric. (738773)
- "Very dim nodes" in GT cause detection misses (hengck23 screenshots). (738773)

## What top / active participants say works
- Tang (5th): retrain instead of using the public checkpoint; gains from preprocessing and architecture; the public
  ckpt "hit a wall", post-processing alone won't go further. (734604)
- Mendrika (28th): decompose errors: node recall within 7 um, N_pred vs N_est, conditional linking accuracy where both
  endpoints detected, oracle-linker ceiling, division candidate recall@K. Keep detector fixed when comparing linkers.
  Edge recall ≈ node_recall^2 x linking accuracy => detector misses are the most expensive. (734604)
- FOYSAL (138th): beyond the two-seed blend plateau (~0.91), gains came from association consistency: examine ambiguous
  parent links from several temporal/model views, use the extra view only where models disagree. (730924)
- hengck23 (109th, very active): (a) dense pseudo-labels: run FOCUS-3D (3D instance segmentation, HF space
  Qinghua-thu/FOCUS-3D) to get dense centroids, train a small UNet3D point detector on them (6 s/volume on T4,
  notebook hengck23/cell-point-detector), then a two-head trick: predict FOCUS3D-zyx + delta to Kaggle-zyx;
  (b) generate dense short tracks with open-source trackers (ultrack, HOCT, trackastra, byotrack) for training a
  link transformer with window 5-8 instead of heuristics; (c) elastic/affine augmentation of frame pairs = free dense
  link supervision; (d) learnable peak loss (softmax over neighbourhood, unlabelled pixels ignored) instead of BCE;
  (e) temporal affinity/flow field as link prior; (f) treat divisions as tracklet association after good tracking;
  (g) "detect just enough nodes (<= N_est) with ~100% recall of annotated ones". (723655, 738217, 739018)
- Velocity-projected gap closing (EMA velocity * gap) helps fast-motion occlusions (Rishavendra). (739570)
- Free CC0 synthetic dataset (José Freitas): 18.5 GB, 2,174 sequences, 165k labelled divisions, physical model,
  same XY stride-4 downsampling as the pipeline; division rate inflated 15.7x; for pretraining division models.
  Kaggle: josefreitasalvesneto/biohub-synthetic-dataset. Also Biohub virtual embryo zoo. (732103)
- Public-notebook meta: most 0.94 notebooks post-process the same pilkwang detections -> expected private shake-up;
  "trust local CV". (739570)

## Implications for our plan
1. Our hold12 (same embryos) over-estimates; add a leave-one-embryo-out check for the final model choice.
2. Post-hoc divisions: worth ~+0.02 on LB if precise, but rule-based divisions have hurt LB for others -> validate
   division precision on LOEO, keep the mutual-NN + sister-distance gates, consider a learned division ranker.
3. Detection is the biggest lever and transfers to LB: dense pseudo-labels (FOCUS-3D / Zebrahub), early stopping,
   node-count control (predict <= N_est).
4. Linking: longer temporal window with dense pseudo-tracks; association consistency across views.

## Update 2026-09-07 03:50 (threads with new comments since the first read)
- **Linking gains do not transfer to LB, even cross-embryo** (739352): Pavel's edge-weight model gives +0.02..0.04 on each
  of 5 folds *including train-on-one-embryo/test-on-the-other*, yet +0.000 on LB. sghwr (38th): his local CV is
  pessimistic vs LB by 0.013-0.02 (edge J only). hengck23: always break CV down (edge J, adj factor, node recall,
  N_pred vs estimate, divisions, breaks vs wrong links) instead of quoting one number. => Even an honest LOEO validator
  may over-reward linker tweaks; LB is dominated by detection quality + node count. Our post-proc knob probes (3 flat)
  fit this picture.
- **Synthetic volumes: negative from the leader** (739731): Sergio Alvarez (1st) spent ~2 weeks on synthetic volumes
  (PolNet-style, as in CZII) with no clear gain and dropped it. hengck23 keeps exploring (PSF generators, DaXi paper,
  differentiable rendering deltaMic, NISNet3D). => drop the José Freitas synthetic dataset from friend B's queue.
- **"Metric problem"** (739686, Antonoof 6th): two submissions differing only by deleting 45% of nodes/edges scored the
  same 0.954; Sergio (1st) says every node/edge removal he made did move the LB; Antonoof later retracted ("maybe I was
  mistaken"). Hosts confirmed elsewhere that the unbounded node factor is intended. Not actionable; our min-track-len
  direction probes (4 vs 8) will show whether the node bonus is real on the LB.
- **Detector overfits past ~epoch 5-10 on sparse GT** (738773, nusrati + hengck23): loss keeps falling, node recall
  stays 0.98-0.99, but peaks/frame climb (1800 -> 2100+) and adj edge J collapses (0.40 -> 0.07 by epoch 120); cause:
  unlabelled nuclei become negatives; faint nuclei in the GT are the hardest. => For friend A's 30-epoch run: official
  score every 5 epochs and keep the best; track N_pred/N_est per epoch; if the peak is <= 10 epochs, more DATA (all 199
  videos), not more epochs, is the way up. His 5-epoch curve (best at epoch 4, worse at 5) already hints at this.
- **hengck23's FOCUS-3D line** (738217, still 222nd - no LB proof): dense FOCUS-3D labels + augmented frame pairs let a
  SuperGlue-style link transformer train 200 epochs without overfitting; on unseen 6bba_337b1b3a with Kaggle GT: node
  recall 1.0, edge recall given nodes 0.964 (divisions excluded). Extra tricks: two-head domain calibration (FOCUS zyx +
  dzyx in um), refining GT by +dzyx within the 7 um tolerance to sharpen link targets, sub-voxel coords via grid_sample.
  He admits it "does not help if the gap is more than one missing frame". Rishabh Roy's claim that the LB is scored on
  dense labels is unsupported (hosts: sparse, same as train).
- **">0.94 line" thread** (738276): no one above 0.94 answered; the only advice (hengck23) is the ultrack toolchain +
  manual annotation rounds. PROXY_SCORE of the public notebook is sparse-GT and barely penalises over-detection.

## Update 2026-09-08 15:40 (discussion + public notebooks re-read)
- **Public 0.946 = 0.941 pipeline + run-to-run luck.** `flexonafft/biohub-harmonic-fusion` (0.946, version 29) and
  `redoctopusk/biohub-942tta` (0.942) are byte-identical in config AND code (same env values, same inference cell with an
  "edge-feature TTA" patch, same in-kernel post-proc sweep, deterministic validator stems). So identical notebooks differ by
  0.004 on the public LB: GPU non-determinism through 8-view TTA + ILP + a leaky-validator sweep that selects among 7 knob
  candidates with a 0.001 margin. The 0.946 is the max over 29 versions. => the public-LB resolution for a SINGLE run of
  this pipeline family is about +-0.003; our probe deltas below 0.005 (incl. exp03B primary +0.004) are not proven.
- What the forks add vs 0.941: (a) `BIOHUB_EDGE_FEATURE_TTA=1` - averages the UNet feature maps over the 8 TTA views
  before edge prediction (base only averaged detection logits); principled, inference-only, effect unmeasurable on LB at
  this noise; (b) PP sweep on 8 leaky train videos (gap 4.5, tight relink 5.5, relaxed 9, learned bonus 1.25, gap2 step 4,
  reuse 2.8, DeepCenter gap 0.35) with margin 0.001 - noise-chasing, do not adopt; (c) VALIDATOR_N_PER_TYPE 2 -> 4.
- **Linker gains still do not transfer** (739685): Mark (7th place) - any smarter motion linker = exactly +0.001 LB while CV
  moves 0.01-0.03; Yubo WANG - +0.012 on 5-fold CV -> +0.001 LB, and the public 0.946 notebook is 0.015 WORSE than his
  0.942 one on the same 5-fold CV => public notebooks are tuned to the public LB; expect a private shake-up against them.
  hengck23 suggests online test-time training and "smart encoding" of submissions to probe the test distribution (the
  encoding part is a grey area we will not use; test-time adaptation itself is legal and is our §10a B5).
- Mark (7th) asks "why train the UNet for >100 epochs?" - a hint that top teams train long (only possible with dense labels).
- Division thread (739516): nearest-parent candidate graph covers 88% of the 151 GT forks vs 99.7% of continuation edges;
  candidate recall is the division bottleneck (matches our divranker finding).
- "Post-processing plateau at 0.942" (740103), no answers: everyone hits the same wall.

## Update 2026-09-10 (Code tab: all new notebooks pulled via API and diffed against the 0.941 base)
Public scores read from the notebook pages (single-run notebooks unless noted):
| notebook | LB | what it is |
|---|---|---|
| sjlee101/biohub-lf-dctta-v020 | **0.947** (v1) | Harmonic Fusion + `BIOHUB_DEEPCENTER_TTA=1` (8-view D4 averaging of the DeepCenter veto logits, the last single-view stage) + `SECONDARY_EDGE_FEATURE_TTA=1` weight 0.75 (secondary model's UNet features also TTA-averaged and blended into edge features) + DeepCenter safe-div threshold 0.25 -> 0.20 |
| sjlee101/biohub-lf-sectta-w1 | 0.946 (v1) | Harmonic Fusion + secondary edge-feature TTA weight 1.0 only |
| flexonafft/biohub-harmonic-fusion | 0.946 (v29) | 0.941 + primary edge-feature TTA + leaky PP sweep (max over 29 runs) |
| reyhanksatria/"0.946 LB" | 0.944 | same lineage; title overstates |
| analyticaobscura/biohub-lb-942 | 0.942 (v1) | byte-identical to Harmonic Fusion -> run-to-run noise ~0.004 |
| busyaprime/"one knob" | 0.942 (v2) | 0.941 with det threshold 0.96; author reports a "0.948"-titled notebook scored 0.935 when re-run |
| evgendvorkin, hanklin | 0.942 (titles) | knob combos (gap 5.8, relink 5.5, secondary edge weight 0.20-0.25) |
| raykkretzschmar/harmonic-bidirectional-association | 0.915 | harmonic-mean fusion of forward/backward edge probabilities + many knob changes: clearly worse |
Take-aways: every gain since 0.941 is inference-time TTA at more stages (edge features, secondary features, DeepCenter);
knob combos stay at 0.942; a fusion-rule change lost 0.03. The sjlee101 stack is a principled, single-run 0.947 and does not
touch the model -> it composes with our fine-tuned primary. Chosen to run: exp29 = sjlee101 lf-dctta-v020 verbatim
(reproduce 0.947, validator + sweep on) and exp30 = the same + PRIMARY := exp03B, validator off (our candidate base).

## Update 2026-09-11 (discussion tab re-read; the division threads are the useful ones)

**740573 "Division steps are not long steps" (Lê Quang Cảnh, base rates measured on the TRAINING LABELS, no model).**
73 label files, 36 divisions, 25,661 continuation edges, every labelled edge spans exactly one timepoint.

| quantity | n | median | IQR | p90 | p99 |
|---|---|---|---|---|---|
| continuation step | 25,661 | 1.724 um | 0.908-2.188 | 3.350 | 6.906 |
| division (parent->daughter) step | 72 | 4.569 um | 3.300-6.214 | 7.081 | 10.619 |
| sister separation | 36 | 8.849 um | 7.196-10.235 | 11.866 | 13.896 |

Continuations sitting above a distance gate, per division admitted: 5 um 24:1, 7 um 30:1, 9 um 27:1, 10 um 38:1.
=> The division IQR lies entirely inside the ordinary continuation range. A parent-distance gate wide enough for the
median division admits ~30 continuations for each division it catches. **This is a base rate, not an overlap you can
tune away** - independent confirmation of our own conclusion that the safe-division RANKER, not its gates, is the
problem. The author's caveat: labels cover segments, not whole lineages (351 of 572 tracks start after frame 0), so
the 36 divisions are a labelled subset and the short displacement is partly selection.

**The one quantity that does separate is sister separation: median 8.85 um vs 1.72 um for continuations.** It is a
property of a candidate PAIR, so it can only be used after the pair is proposed. DIRECT CONSEQUENCE FOR US: the public
ranker sorts candidates by `parent_dist + 0.15 * sister_dist` ASCENDING, i.e. it prefers pairs whose two children are
CLOSE together - the opposite of a real division, and exactly the signature of a duplicate detection. The gate has an
upper bound on sister separation (14 um) and no lower bound. A minimum sister separation around the 25th percentile of
real divisions (7.2 um) is a new, base-rate-backed knob that nobody has tried.

**Trap flagged by the same author:** he first measured these steps between his own PREDICTED nodes. On seven divisions
the longest parent-to-daughter step reads median 6.36 / max 7.37 um on labels but median 8.47 / max 13.65 um between
the matched predicted nodes. A predicted node may sit up to 7 um from the label it matches and two such errors compound
across one edge, so tuning a division gate on predicted positions calibrates your DETECTOR ERROR, not cell motion.
Our `tools/sim_safediv.py` works on predicted positions - remember this when reading its absolute thresholds.

**Appearance signal (hengck23 claim, measured by the topic author).** hengck23: "bright thin lines at time t are new
cell divisions that happened a few frames before; very good clue". Measured on 5 films (8 parents, 16 daughters per
offset, 299 ordinary nodes), patch ~5 x 3.7 x 3.7 um: peak intensity AUC 0.73 at the parent's split frame, 0.68/0.70/0.70
for daughters at t+1..t+3; local contrast 0.55/0.65/0.69/0.64; intensity-weighted elongation 0.34/0.48/0.58/0.56 =
chance. So brightness is a real but moderate signal and "thin" is not measurable at 1.625 um z spacing. Labelled
divisions do NOT cluster in time (median spread 32 of 100 frames), contradicting "when you find one you find many".

**ILP event weights vs the Ultrack reference.** Both zebrafish configs in royerlab/ultrack_supplementary use
max_distance 10.0, max_neighbors 5 and small balanced event penalties (large_zebrafish: appear 0.002, disappear 0.001,
division 0.001; sparse_zebrafish: all three 0.1). The public lineage we fork runs division 1.2, disappearance 1.5-2,
appearance 0; the author computes that a fork can never be optimal at those values. Our probe 3 moved division weight
1.2 -> 0.9 (neutral) - a 25% move, where the reference suggests one to three ORDERS OF MAGNITUDE.

**External data with the Kaggle voxel scale.** hengck23 posted that
`https://public.czbiohub.org/royerlab/ultrack/zebrafish_embryo.ome.zarr/` reports scale (1.625, 0.40625, 0.40625) -
exactly ours - 522 timepoints, 505 x 2217 x 2170. The single-objective Zebrahub files are 1.24 x 0.439 x 0.439 and do
NOT match. Ultrack also ships pretrained node detectors (`unet-daxi.pt`, `unet-simview.pt`). Freely and publicly
available external data is explicitly allowed by the rules.

**739516 "I measured my own division_jaccard (0.22)".** hikaggler ran the same pipeline with division creation off:
LB 0.929 -> 0.907, so 0.022 = 0.1 x div_J => div_J ~ 0.22. A commenter correctly notes the ablation is confounded
(parent->daughter edges count as edges too, so the delta splits between the edge and division terms) and points at
the official `evaluate_datasets()` for an exact local split. His illustration is the useful part: two teams both at
0.948 can need opposite work - div_J 0.30 needs adj_edge 0.918, div_J 0.15 needs 0.933. Our own official-metric div_J
on 12 hold-out videos with the gate on is 0.111, so there is plausibly room to roughly double the division term.
Same thread: a nearest-parent candidate graph (R ~ 9.9 um, K <= 10) covers only ~88% of the 151 GT division forks
against ~99.7% of continuation edges - a candidate-recall ceiling before any classifier runs.

**739685 "Problems with edge connection" - independent confirmation that linker gains do not transfer.**
Mark (10th place): any smarter motion linker gives "an increase of exactly 0.001" while local CV moves 0.01-0.03.
Yubo WANG: +0.012 on 5-fold CV -> +0.001 LB, and the public 0.946 notebook scored 0.015 WORSE than his own private
0.942 notebook on the same 5-fold CV. This is exactly our finding, reported by people above us on the leaderboard.

**739570 "Meta Trap, Private LB Shake-ups" and 740103 "Post-Processing Plateau?".** Community consensus: most of the
leaderboard is post-processing the same public detections, so a large private shake-up is expected; "trust your local
CV" (Mendrika Ramarlina, 146th). The plateau thread reports the same 0.942 wall with zero answers. Supports our plan
of one public-config submission and one honest-validator submission.

**What we take from this read (queued in CONTEXT §10a):**
1. minimum sister separation in the safe-division gate (base rate 7.2-10.2 um vs ~0 for duplicates) - testable offline;
2. re-rank division candidates on evidence (sister separation, parent brightness) instead of `parent_dist + 0.15*sister_dist`;
3. ILP division weight 1.2 -> 0.1 or lower, i.e. the Ultrack scale, not our earlier 25% move;
4. external Ultrack zebrafish volume at our exact voxel scale as extra division examples / pretraining.

## Update 2026-09-13 (discussion + code tab re-read; browser)

**738217 "focus3d" thread, new comment by Lê Quang Cảnh (rank 39, official scorer, five held-out films, one variable
each).** The most useful controlled numbers anyone has posted:
- Dense-label fine-tuning of the DETECTOR: detection head only (33 params) = -0.0033; head + encoder = **-0.0377**, with the
  edge transformer frozen and reading that encoder. Quote of the mechanism: extra detections are nearly free, moving the
  representation underneath the linker is what hurts. => any dense fine-tune must either leave the encoder alone or
  co-train the linker on top of the moved encoder. Our two-stage variant (e) (freeze linker, move encoder on dense
  labels, then recalibrate) is exactly the harmful configuration and is dropped; see TEAM/PROMPT_FRIEND_A.
- Annotation bias vs a detector: mean residual dz -0.57, dy -0.24, dx -0.20 um over 15,693 matched pairs (48/31/26
  standard errors), median match distance 1.50 um; correcting with a CONSTANT loses 0.0031 because matching is an
  assignment on relative distance; the bias is embryo-dependent (dz ~0 for one embryo, -0.61 for the other). A learned
  per-node offset is the only version that can pay.
- Refining annotations inside the 7 um tolerance (hengck23's trick): the link model already puts a median 0.9968 on the
  true link at the annotated position; only 3% sit below 0.90. Low value.
- Contested links (both endpoints detected and matched, link went elsewhere; 381 cases / 15 films): velocity
  extrapolation over 4 frames picks the true child in 0 of them; the link model prefers the true child in 44 of 290
  (15%). Both parents sit ~1.5 um from the node they linked (= their 1.16 um/frame step) while the truth asks for a ~9 um
  jump. So the true assignment loses on appearance AND on trajectory consistency; a structured loss can recover about
  +0.005 edge Jaccard; the rest needs the node and link models to move. Consistent with our "linker gains do not
  transfer" finding.
- Elastic augmentation: their own test was mis-targeted (fine-tuned the secondary), correct run queued; paired top-1
  92.90 (primary) vs 92.46 (elastic-from-secondary), p = 0.0028 / 0.2342 - unresolved.

**740145 "magic or overfitting?" (hengck23, rank 495).** A "refine_prob" head at threshold 0.0888 removes 13.13% of
peak detections while keeping 99.45% recall of Kaggle-annotated nodes; localisation error 1.18 -> 0.97 canonical
voxels. He uses it only to build better dense training samples, but for OUR metric it is the node-budget lever: the
adjusted-Jaccard factor is 1 - 0.1*(N_pred - N_est)/N_est, so -13% nodes at ~no recall loss is worth about +0.012.
Queued as B25. Also: many "false positive" detections sit very close to a true node (localisation, not existence),
and Ultrack's pretrained UNet weights are public (public.czbiohub.org/royerlab/ultrack/unet_weights/unet-daxi.pt,
unet-simview.pt) - allowed as external pretrained models if uploaded as a dataset; unverified against Kaggle points.

**Later hengck23 comments (2-4 days ago):** he now argues the right frame is hypothesis generation + scoring over a
long window (ultrack-style multiple hypotheses, differentiable ILP over T=5-10), and that "instead of learning perfect
predictors, generate hypotheses and test". Research direction, not a 16-day item. Ultrack over-segmentation did not
work for him; Satwik: Ultrack segmentation worse than own detector, useful only to generate dense tracks.

**Code tab (API list sorted by score + spot checks in the browser):** nothing public above 0.947. Newcomers checked:
sjlee101/biohub-lf-hoctveto-div-b 0.947 (v1, 21 votes), flexonafft/biohub-harmonic-fusion v30 0.947 (207 votes).
Everything listed above the 0.947 group is still the July metric-hack set. Leaderboard: we are 355 / 3494 at 0.947
(160 / 3372 two days ago); the top is 0.970 / 0.968 / 0.966 / 0.966; rank 49 = 0.949; ranks 50-344 are collapsed, so
about 200 teams moved to 0.948-0.949 or ahead of us on tie-break in two days. Whatever they did is not a visible
public notebook.
