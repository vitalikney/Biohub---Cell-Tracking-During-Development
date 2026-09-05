# Literature survey B: learned linking, division detection, global optimisation

## Metric facts that shape the ranking
- Exact metric (https://github.com/royerlab/kaggle-cell-tracking-competition/blob/main/metrics.md):
  `adjusted_edge_J = max(0, J_edge * (1 - 0.1*(T_pred - T_true)/T_true))`, `score = adjusted_edge_J + 0.1 * J_div`, micro-averaged.
- Edge FP counts only when a predicted edge's endpoints match GT nodes that are connected elsewhere in GT; edges among unmatched (unannotated) detections are free. Recall of annotated edges dominates; over-detection costs 10% per 100% excess nodes.
- Division-Jaccard exploit was patched (discussion 727154): divisions must be genuine parent -> two-daughter forks with all three nodes matched within 7 um.

## Papers

1. **Trackastra** — Gallusser & Weigert, ECCV 2024. https://arxiv.org/abs/2405.15700 , code https://github.com/weigertlab/trackastra
   Transformer over detections in a temporal window s=6 (s=2 "substantially degrades"), shallow features + Fourier PE + RoPE, spatial attention mask by d_max. Loss = parental softmax (per child over candidate parents) + small BCE, division rows x10, dt <= 2. Overlapping windows averaged. Greedy or ILP (motile) linking. Won CTC ISBI-2024 generalizable linking.
   For us: window 4-6 frames, parental softmax instead of row-focal BCE; ~200 lines on SimpleNodeTransformer; <2 GPU-h on T4 with precomputed features. Expected: high.

2. **HOCT: Higher-Order Cell Tracking Transformer** — Bragantini, Theodoro, Royer (competition organisers), arXiv 13 Jul 2026. https://arxiv.org/abs/2607.11754
   Edge-centric transformer: node stage -> edge tokens [z_i || z_j] for candidate edges incl. dt>1 -> edge stage with line-to-line distance attention bias, 3D RoPE. Only 19 shallow features (t,z,y,x, diameter, intensity stats, inertia tensor, border distance), no image encoder. Focal loss gamma=3.5 on parental-softmax, normalised per target node and per temporal gap, division weight 3.5x. Two-pass ILP: dt=1 -> tracklets; tracklets as meta-nodes + long-range edges -> learned gap closing. 262k params. SOTA on CTC linking (CLB 0.926).
   For us: best-matched idea; kNN <= 8 candidates, window 3-4 frames; replaces motion-relink + gap-closing heuristics. Expected: highest.

3. **linajea: whole-embryo lineages from sparse annotations** — Malin-Mayor et al., Nat Biotech 2023. https://www.nature.com/articles/s41587-022-01427-7 , code https://github.com/funkelab/linajea
   4D U-Net (7 frames) predicts cell-indicator heatmap (loss only near annotations) + movement vector to parent centre (daughters point to mother). ILP with node/edge/appear/disappear costs, grid search on validation edge errors. Zebrafish 0.078 errors/edge.
   For us: add 3-channel parent-offset head supervised at annotated nodes; use as edge feature, motion prior, division cue. Expected: medium-high.

4. **Weakly-supervised tracking + graph optimisation for C. elegans** — Hirsch et al., MICCAI 2022. https://arxiv.org/abs/2208.11467 . Structured SVM for ILP weights; learned division detector. For us: optimise ILP costs against the competition metric on CV folds (Optuna, CPU).

5. **Ultrack** — Bragantini et al., Nat Methods 2025. https://www.nature.com/articles/s41592-025-02778-0 , https://github.com/royerlab/ultrack
   Hypothesis-selection + linking ILP, flow-field motion compensation, power-transformed edge weights, near-zero event costs. For us: motion compensation idea, cost parameterisation, alternative ILP backend.

6. **GNN cell tracking** — Ben-Haim & Riklin Raviv, ECCV 2022. https://arxiv.org/abs/2202.04731 . Metric-learning embeddings; superseded by transformers.

7. **Mitosis-aware multi-hypothesis tracker with aleatoric uncertainty** — Kaiser et al., IEEE TMI 2025. https://arxiv.org/abs/2403.15011 . TTA-based probabilistic motion, delayed division decisions. For us: accept fork only if both daughters persist >= k frames.

8. **Contrastive learning for division detection** — Zyss et al., BMC Bioinformatics 2025. https://link.springer.com/article/10.1186/s12859-025-06344-5 . Triplet (mother, d1, d2) classifier with embedding + geometry features. For us: dedicated division MLP on candidate forks; 151 positives + hard negatives from ILP forks.

9. **Mitosis detection from partial annotation via frame-order flipping** — Nishimura et al., MICCAI 2023. https://arxiv.org/abs/2307.04113 . Time-reversed clips = guaranteed negatives; copy-paste of annotated divisions = extra positives.

10. **CELLECT** — Zhou et al., Nat Methods 2025. https://www.nature.com/articles/s41592-025-02886-x . Detection + per-cell embedding from sparse centre annotations; NN linking in embedding space. For us: contrastive embedding head as extra edge feature.

11. **CAP: Cell as Point** — Song et al., Pattern Recognition 2026. https://arxiv.org/abs/2411.14833 . Division-event oversampling during training; rolling-window inference.

12. **Cell-TRACTR** — O'Connor & Dunlop, PLOS CB 2025. Not feasible in budget.

13. **CTC Cell Linking Benchmark** (Jan 2025): Trackastra, PAST-FR (KOFT Kalman + optical flow, https://github.com/raphaelreme/byotrack), RWTH-GE (SAM2 propagation). HOCT above all (0.926).

14. **ELEPHANT** — eLife 2022. https://elifesciences.org/articles/69380 . Flow trained from sparse links.

15. **SynCellFactory** — MICCAI 2024. https://arxiv.org/abs/2404.16421 . Not in budget.

## Top-5 ranking (survey B)
1. Edge-centric windowed transformer (HOCT + Trackastra): 3-6 frame window, candidate edges dt=1..3, parental softmax + focal, division up-weighting.
2. Two-pass ILP with learned long-range edges instead of rule-based gap closing.
3. Learned parent-offset / movement-vector head on the detector (linajea / ELEPHANT).
4. Dedicated triplet division classifier + division augmentation (frame flipping, copy-paste, multi-frame consistency).
5. Metric-aware ILP cost calibration on CV folds.
