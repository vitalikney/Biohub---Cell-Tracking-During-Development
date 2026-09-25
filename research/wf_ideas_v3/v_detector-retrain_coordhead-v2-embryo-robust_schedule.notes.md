# notes Fri Sep 25 10:56:39 UTC 2026
2026-09-25 ~11:20 UTC schedule skeptic (coordhead-v2-embryo-robust)
- Read BRIEF.md, experiments/coordhead_retrain/{FRIEND_A_RUN.md,out_full_P.log,out_full_Q.log,out_full_*/report.json}, tools/train_coordhead.py, exp56 notebook/kernel-metadata, CONTEXT.md 1385-1560. No web needed.
- Numbers verified: Q emb 6bba->44b6 1.3781 (none 1.4990, -8.1%), 44b6->6bba 1.5875 (none 1.7199, -7.7%); P 1.4517/1.5699; public 1.2963/1.5668; fits 26-35 s CPU; pairs 125,700 (6bba 106,452); Q args huber 0.5, 120 epochs.
- Per-video win rate vs none (from report.json): Q 68/71 (0.96) and 109/128 (0.85); P 38/71, 112/128.
- m7 margins Q vs none: +4 (20116 vs 20112) and +2 (112256 vs 112254): razor-thin, bagging can flip.
- GATE FLAW: all-peak mean shift of a non-debiased head trained on one embryo: P 6bba->44b6 z +0.567, 44b6->6bba z +0.211; Q -0.123 / +0.039. REF (non-debiased, 10 stems of training embryo) will learn the same convention -> gap vs Q ~0.5-0.7 um > 0.2 in 6bba->44b6 => gate fails by construction. Even vs the public head Q's gap is 0.212 (>0.2).
- Distance criterion 44b6->6bba: Q 1.5875 is WORSE than P 1.5699; needs REF >= 1.637 (P +4.3% from data volume alone, 10 vs 71 stems) -> ~coin flip. 6bba->44b6 likely passes (Q/P = 0.949).
- --balance embryo is a no-op in the single-embryo held-out folds: the gate never tests it.
- Captures = outputs of Kaggle kernels vitaliineibauer/biohub-chcap-* downloaded to experiments/coordhead_retrain/captures on the Windows machine that ran P/Q; train geffs needed via --data-dir. Container has neither.
- Kernel: exp56 cell 4 line 511 rglob('biohub-v1284-head-s075/v1284_head.pt') must match exactly one file; swap dataset_sources + pattern. x138 runtime guard 27,000 s -> hidden-test run ~7.5-10 h.
- GPU: vitaliineibauer 0 GPU-h until 26 Sep 00:00 UTC -> dummy run no earlier than 00:00 26 Sep.
- Conditional on gate pass: scored ~26 Sep 08:00-17:00, 2.5+ days slack -> P~0.9. Unconditional (gate as written): ~0.05-0.1; with repaired gate ~0.35-0.45. < 0.70 -> refute under lens.
