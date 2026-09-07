# Literature survey A: sparse-label 3D nucleus detection, pretraining, TTA

Setting: T=100, Z=64, 256x256, voxel 1.625 x 0.406 x 0.406 um (4x anisotropy), ~6% of nuclei annotated as point tracks.
Metric = edge Jaccard after 7 um node matching, penalty for over-counting nodes, + 0.1 x division Jaccard.
Baseline detector: TemporalUNet3D, BCE heatmap on GT points (negatives weighted 0.01-0.1), XY downsample 4x, window 2.

## A. Detection with sparse / partial point annotations

1. **Small Object Localization with 90% Annotation Reduction by Positive-Unlabeled Learning** — Zhou et al., Micromachines 16(12):1379, Dec 2025. https://doi.org/10.3390/mi16121379 , PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC12735266/ , code https://github.com/wangshihong/LFE
   Count-map regression; annotated blobs = positive, everything else = unlabeled; non-negative PU risk (Kiryo et al.) `R = pi*Rp+ + max(0, Ru- - pi*Rp-)`, prior pi from expected object density; stage 2 mines pseudo-positives with a beta-mixture model. With 5-10% points annotated: F1 0.74-0.95.
   For us: replace weighted BCE with nnPU on the sigmoid heatmap; pi computed from `estimated_number_of_nodes`; pseudo-positive mining with temporal persistence filter. ~30 lines. Expected: high (+5-15% node recall).

2. **PU learning for cell detection in histopathology with incomplete annotations** — Zhao et al., MELBA 2023. https://arxiv.org/abs/2302.08050 (MICCAI 2021: https://arxiv.org/abs/2106.15918). Heatmap regression with PU reformulation of the negative term. Same recipe as #1 with Gaussian heatmap.

3. **PAC-MAP: Proximity Adjusted Centroid Mapping for nuclei in dense 3D cell systems** — De Vos lab, Comput Biol Med 2024. bioRxiv https://www.biorxiv.org/content/10.1101/2024.07.18.602066v1.full , code https://github.com/DeVosLab/PAC-MAP
   3D U-Net regresses centroid map of anisotropic Gaussians (sigma = nucleus radius adjusted for voxel size), amplitude scaled by distance to nearest neighbour; MSE; spherical max-filter NMS + greedy acceptance by proximity. Weak pretraining on pseudo-labels then fine-tuning on 30 patches: F1 0.793 -> 0.817.
   For us: anisotropic Gaussian targets, proximity-weighted amplitude, ellipsoidal NMS matched to 7 um. Expected: +2-5% detection F1, very cheap.

4. **ELEPHANT: Tracking cell lineages in 3D by incremental deep learning** — Sugawara, Cevrim, Averof, eLife 2022. https://elifesciences.org/articles/69380
   Ellipsoid annotations -> center/periphery/background voxel labels; all unlabeled voxels ignored in the loss; second U-Net predicts 3D flow from sparse links. CTC Fluo-N3DH-CE with ~2% annotations: DET 0.979, TRA 0.975.
   For us: "ignore unlabeled" fallback; negatives only where intensity says background; 3-class head.

5. **nnLandmark: self-configuring 3D landmark detection** — Ertl et al. (MIC-DKFZ), arXiv 2025/2026. https://arxiv.org/abs/2504.06742 , code https://github.com/MIC-DKFZ/nnLandmark
   Distance-transform heatmap target, BCE TopK-20% loss, nnU-Net augmentations, 5-fold ensembling. For us: TopK-BCE / focal loss, richer augmentation. Expected +1-3%.

6. **Weakly supervised nuclei segmentation with point-guided attention and self-supervised pseudo-labeling** — Mo et al., Bioengineering 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC11761557/
   Three-value masks (fg/bg/uncertain), multi-radius Gaussian branches, EMA-teacher pseudo-labels. Engineering details for self-training.

7. **CANVAS: whole-brain light-sheet representations** — Kim et al., CVPR 2026. https://arxiv.org/abs/2603.29842
   Light-sheet centroid benchmark, heatmap + FindMaxima NMS, 3D MAE with content-aware loss weighting (background x1, high-variance patches x10) gives +22.9% F1 on hardest marker.

## B. Self-supervised / foundation pretraining for 3D microscopy

8. **Multimodal 3D foundation model for light-sheet microscopy** — Scheinfeld et al., arXiv May 2026. https://arxiv.org/abs/2605.26026 , weights https://github.com/AdinaScheinfeld/lsm_fm_public_repo . Masked reconstruction on 1023 LSFM volumes; few-shot nuclei Dice 0.78 vs 0.75. Modest gain.
9. **3D MAE for volumetric cellular representations** — Kardoost et al., arXiv June 2026. https://arxiv.org/abs/2606.23964 . Frequency-domain regularisation keeps fine detail.
10. **Revisiting MAE pre-training for 3D medical image segmentation** — Wald et al., CVPR 2025. https://arxiv.org/abs/2410.23132 . MAE works for 3D CNN U-Nets; block masking; +3 Dice. Most compatible recipe for TemporalUNet3D: 1-2 GPU-h on all frames.
11. **Cellpose-SAM** (bioRxiv 2025, https://www.biorxiv.org/content/10.1101/2025.04.28.651001v1) / **micro-SAM** (Nat Methods 2024, https://www.nature.com/articles/s41592-024-02580-4). Use only as offline pseudo-label / count-estimate source.
12. **CellSeg3D / WNet3D** — Achard et al., eLife 2025. https://elifesciences.org/articles/99848 . Label-free 3D nuclei; source of background masks.
13. **SELMA3D challenge** — arXiv Jan 2025. https://arxiv.org/abs/2501.03880 . In-domain SSL on light-sheet data helps.

## C. Linking (cross-reference with survey B)

14. **HOCT: Higher-Order Cell Tracking Transformer** — Bragantini, Theodoro, Royer (CZ Biohub, competition host), arXiv 13 Jul 2026. https://arxiv.org/abs/2607.11754
15. **Trackastra** — Gallusser & Weigert, ECCV 2024. https://arxiv.org/abs/2405.15700 , https://github.com/weigertlab/trackastra
16. **Ultrack** — Bragantini et al., Nat Methods 2025. https://www.nature.com/articles/s41592-025-02778-0 , https://github.com/royerlab/ultrack

## D. TTA / ensembling

17. **Test-time augmentation for cell segmentation** — Moshkov et al., Sci Rep 2020. https://www.nature.com/articles/s41598-020-61808-3 . Average heatmaps over 8 flips (+ 4 in-plane rotations; never rotate Z into XY), SWA, seed ensembles. Reliable +1-3%.

## Top-5 ranking (survey A)
1. nnPU loss + temporally-filtered pseudo-positive self-training (#1, #2, #4, #6).
2. Heatmap target / NMS / count calibration redesign (#3, #5, #7): anisotropic Gaussian sigma, TopK-BCE or focal, ellipsoidal NMS, threshold chosen so predicted count ~ estimated true count.
3. HOCT-style linking (#14, #15).
4. TTA + SWA + small ensemble on heatmaps (#17, #5).
5. In-domain 3D-CNN MAE self-pretraining (#10, #7, #9).

## Update 2026-09-07 04:20 — second literature pass (only what is NOT already in the queue)
Searched: transformer/GNN linking 2025-26, sparse-point detection losses, division detection, test-time adaptation,
foundation models for video tracking, dense pseudo-labels / distillation. Most hits are already covered (Trackastra,
HOCT, linajea, Ultrack, ELEPHANT, PU-learning, MAE pretraining, SAM-family). Two ideas are new and cheap enough:

**N1. Dense self-distillation from our own pipeline ("Dense Teacher" / noisy-student).**
Dense Teacher (Zhou et al., ECCV 2022, https://dl.acm.org/doi/abs/10.1007/978-3-031-20077-9_3) and DTG-SSOD (NeurIPS 2022)
show that dense pseudo-labels from a teacher beat sparse thresholded ones for semi-supervised detection; MUSE (arXiv
2511.05170) applies dense self-distillation to nucleus detection. For us: the public pipeline already detects ~98% of
GT nuclei; its NMS'd detections on all 199 train videos are dense point labels (plus GT points, GT wins on conflicts).
Training a from-scratch student on dense labels removes the "unlabelled nucleus = negative" failure that makes sparse-GT
detectors peak at epoch 5-10 (discussion 738773; hengck23 trains 200 epochs on dense FOCUS-3D labels without
overfitting). Cheaper than queue item 8 (no FOCUS-3D/Zebrahub): predictions for 199 videos = ~1.5 GPU-h on Kaggle 2xT4
or ~3-4 h on a 5070. Variant: distil the teacher's soft heatmap instead of points (needs the teacher on the fly).
Honest check: LOEO (teacher pseudo-labels on 6bba only -> student -> score on 44b6). Risk: the student inherits the
teacher's misses on faint nuclei; mitigate by keeping GT points and by using the dual-seed blend as teacher.

**N2. Test-time adaptation on the hidden test embryos (DARTH-style).**
DARTH (Segu et al., ICCV 2023, https://arxiv.org/abs/2310.01926): adapt a detector on unlabelled target video with a
detection-consistency loss under photometric augmentation, teacher = EMA of the student; +association via patch
contrastive loss. Zero labels, so it is legal under the "no hand labelling of test data" rule. For us: a few hundred
fine-tune iterations of the primary detector on each test embryo inside the submission kernel (~30 min per embryo on
2xT4, fits the 12 h limit), with the node-count guard (stop if N_pred grows > x%). This is the only idea that attacks
the actual failure mode (weights that generalise poorly to unseen embryos, 0.99 local vs 0.899 LB). Honest check: LOEO
(adapt the 6bba-trained model on 44b6 images without labels, score on 44b6 GT). Simplest first version: self-training
with the model's own confident detections (pseudo-labels) + photometric aug, no contrastive head.

Seen and rejected / already covered:
- SAM2 zero-shot cell tracking (arXiv 2509.09943): unsupervised, competitive on CTC, but heavy for 3D+t at Kaggle
  time budget and far below a trained detector here; at most a diversity source later.
- NuDetect conformal thresholding (2025): principled per-dataset threshold, but needs a labelled calibration set
  from the target domain; our threshold is already LB-tuned (0.965 vs 0.95 = neutral).
- CTransformer (arXiv 2512.14472): membrane tracking, not nuclei.
- 3D nnU-Net cardiomyocyte tracking (2026): segmentation-first pipeline, no new linking idea.
