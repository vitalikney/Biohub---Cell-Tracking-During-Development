# r1 research: oof-edge-scorer-full-candidates (started 2026-09-24)
## Code facts (tools/repo/scripts/predict_unet_transformer.py, train_unet_transformer.py, simple_node_transformer.py, exp39 nb)
- NO kNN candidate graph: transformer scores DENSE n_src x n_tgt per frame pair (pair_mlp over all pairs, chunked).
- probs = softmax(raw, dim=0) = per-TARGET distribution over ALL sources (no null/no-parent column). Loss same (focal BCE on softmax dim0, GT rows/cols only).
- Candidate threshold: BIOHUB_DUAL_SEED_EDGE_THRESHOLD=0.48 (cfg.threshold) -> each target has <=2 (practically 1) candidate parents. So "edge_prob 0" pairs WERE scored; p<0.48 was just not written.
- exp39 blend: secondary seed edge weight 0.15 low_margin_consensus, bidirectional harmonic 0.15, secondary edge feature TTA 0.75. A re-dump must reproduce these.
- relink cost = motion + 0.05*raw - BONUS(1.0 in exp39)*prob; learned_edge_probs built from geff edges (ILP output) in filter_output_graph.
- Training: transformer+UNet trained on GT nodes only (sparse transition matrix among annotated nodes), GT coords; inference on all detections -> train/test set shift.
- OOF pitfall: fine-tuning "from the public init" is NOT OOF (init saw all 199); UNet features also got edge-loss gradient on all 199.
## Web
- tracksdata ILPSolver.solve return_solution=True default -> returns solution SUBGRAPH only (raw.githubusercontent.com/royerlab/tracksdata/main/src/tracksdata/solvers/_ilp_solver.py). So geff = ILP solution; candidates >=0.48 not selected also lost.
- Trackastra (arXiv 2405.15700): parental quiet softmax exp/(1+sum) = null option; keeps associations down to alpha=0.05 for linker; spatial mask d_max. Ours: plain softmax, no null, threshold 0.48.
- Stacking/OOF: in-sample base predictions bias second-level models (Kaggle general/18793; KDnuggets stacking; arXiv 2206.08473).
- anatomy: 'unscored & ILP both none' 33,544 edges, 341 TP/268 FP evaluable, drop = -0.0007.
## Verdict draft
- mixed: plumbing supported (sub-threshold probs exist at inference for free; Trackastra keeps alpha=0.05), kNN premise wrong, OOF retrain weak (UNet leak, public-init leak, probe 29 answers ef transfer directly, exp51 coords will invalidate cache).
- noisyislands/biohub-transformer-finetune: edge transformer fine-tune w/ impostor duplicates, lr 2e-5, 6-8 ep (no LB) - relevant hard-negative idea.
- Pitfall: relink edge 'edge_prob' feeds ef (p==0 test) and short-track rescue (mean prob >=0.88): carry full prob in a separate field.
## Resume 2026-09-24 (session 2)
- Re-verified exp39 nb: relink cost line 1048 `motion + 0.05*raw - BONUS*prob`, BONUS env=1.0 (nb line 86); prob dict from post-ILP edges (nb ~2000-2012), .get(...,0.0).
- Max sub-threshold contribution = BONUS*0.48 = 0.48 um of cost -> only flips near-ties; swaps are node-position errors (CONTEXT 13:45) so plumbing cannot touch the 2.7k swap FN.
- CONTEXT 13:25: probe 29 answers ef transfer directly -> OOF retrain for 'is ef in-sample' is redundant.
- Writing final JSON now.
