# notes 2026-09-25T11:13:05Z start: value skeptic for fullres-residual-head
- read BRIEF, sibling v_redteam-past_head199-x138-two-arm_value.json (refuted; LB value ~+0.0007-0.0008 per 1% bias-free cut, head LB gain on ours ~ node multiplier).
- v2 polyphase json: zarr is 1024 px xy, detector ::4; GT coords INTEGER voxels (z grid 1.625 um -> irreducible z sd 0.47 um); quantisation ~20% of xy var, ~10% of 3D var.
- discussions_summary l.354-357: Eric (77th) heuristic sub-voxel peak refinement +0.0078 local -> -0.002 LB TWICE. Constant offset -0.0031 LB. Direct precedent for this idea class.
- coordhead_retrain/out_full_P/report.json leak5 OOF public: mean 1.525, MAE z/y/x 1.076/0.571/0.597, bias 0.399/0.285/0.345; match7 none 132366 / public 132326 / P 132473 (<=0.1% change) -> 7 um matching barely sensitive to sub-2 um shifts.
- public bias by embryo (emb folds): 44b6 z/y/x .131/.050/-.040 ; 6bba .447/.327/.415 -> xy bias embryo-specific; a pooled residual (85% 6bba pairs) learns ~+0.3 um xy 6bba offset.
- Folded-normal debias of public leak5 per-axis: sd z/y/x = 1.288/0.655/0.660 um; bias-free 3D mean 1.431 (matches idea's 1.43). z = 66% of error variance and full-res adds NO z information (detector already reads every z plane).
- MC: xy sd x0.95 -> 3D -2.1%; x0.90 -> -4.2%; x0.85 -> -6.0%; x0.70 -> -11.8%. Idea's target 1.25 um needs xy sd -32% (0.66 -> 0.45) = impossible out of embryo; P in-domain (convention-learned) reached xy MAE 0.44/0.42 only.
- Value: LB response <= ~0.0008 per 1% bias-free cut (x138 one noisy run), ~0 on our stack, float-out lab +0.0018 -> LB tie, Eric -0.002. Realistic xy cut out-of-embryo 5-10% -> 3D -2..-4% -> +0..+0.003 upper, central +0.0005..0.001.
- Verdict: REFUTE on value (<+0.002, below LB noise 0.003). Writing JSON.
