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
