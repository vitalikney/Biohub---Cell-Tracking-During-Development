# v_hyp_post_deadline r12p-2 notes
- 2026-09-26 23:45 UTC start; no prior json
- Read scan_hyp_post_deadline.json/.notes, round9 LESSONS_draft s4 (8-item list), r9 skeptic on I-222 (weight 0.80; clip-level gap confounded, 'no signal'), RESULTS l.65-80.
- D program cost '4 paired fine-tunes x ~1 h' = fine-tune from pilkwang weights (exp23 recipe 1200 it, RESULTS) which saw BOTH embryos -> G0 not leak-free for it. Scratch alternative: 1.3 GPU-h/epoch (CONTEXT l.244); 6bba-only scratch 5 ep = 0.671 raw / 0.689 pp on LOEO 44b6 (CONTEXT l.90, A17); all-199 scratch ep21 = 0.920 LB (l.268); I-118 ~23 h/run on 5070 Ti; memory: no local GPU (CONTEXT l.12, Kaggle 30 GPU-h/wk, 12 h session).
- Precedents that an honest weak-model LOEO arm-vs-control win does not transfer to the public stack: B5 AdaBN +0.0073 on 6bba-only scratch -> -0.0066 on public stack (CONTEXT l.196); B30 axis-flip +0.0187 on unseen-embryo scratch primary -> LB tie (l.205).
- I-242: FN 120 x 2.4e-5 = 0.0029, FP 152 x 2.4e-5 = 0.0036; fixed-node non-swap link oracle +0.0011 bed-wide bounds the TP-add side; with the >50% TP rule the passing max is ~+0.0022 at oracle -> same bound r12p-1 uses to kill I-122/I-285 (internal inconsistency).
- Late-sub gates on #3/#5/#8 (private >= +0.001) vs r12p-4's own rule 'lab EV < +0.003 cannot be read, stays lab-only' -> contradiction.
- Arithmetic of EV/unit checks out (2.0e-4, 0.9e-4, 0.89e-4, 0.72e-4, 0.6e-4, 0.17e-4).
- Verdict: refuted as written (gate G0 flawed for trained items; ranking/gates internally inconsistent); fix = amend before pre-registering.
- 20:47Z final JSON written (refuted=true)
