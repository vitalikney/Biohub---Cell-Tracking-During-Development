# r1 research clip-boundary-frames notes (started)
## Code facts (tools/repo/scripts/predict_unet_transformer.py, temporal_unet.py)
- window_size=2 (all weights config.json). Windows [ws, ws+1], stride 1, NO padding. seen_frames dedup: frame 0 detected in slot0 of [0,1]; frames 1..T-1 in slot1 of [t-1,t].
- TemporalUNet3D temporal mixing = _TemporalAttention (per-voxel MHA over T), NO positional encoding -> permutation-equivariant; slot0/slot1 identical function. Frame 0 sees frame 1 (future), others see past. No padded frames at any clip edge.
- => detector-padding part (a) of hypothesis REFUTED by code; last frames are detected exactly like interior frames.
- (resume 2) re-verified predict loop in tools/repo/scripts/predict_unet_transformer.py L348-403: stride=W-1=1, window_starts 0..T-2, no padding. exp39 notebook patches this script (dual-seed blend + retention guard) but keeps loop.
- next: check linefit ends, gap-close at t=0/T-1, parquet boundary breakdown.
- MEASURED (fn_exp39.parquet + edges_exp39 TP, T=100 all videos): FN rate per GT edge slot s0 7.8% s1 8.1% s2 8.1% | mid 5.1% | e2 6.0% e1 6.3% e0 9.0%. Both embryos similar.
  per-1000 GT edges: a_never s0 40.7 s1 31.8 s2 19.4 e2 28.3 e1 32.6 e0 42.3 vs mid 13.9; a_tail s0 28.5 s1 26.0 s2 20.4 e2 13.3 e1 19.9 e0 20.7 vs mid 3.8.
  excess FN over mid rate: a_tail ~111 edges, a_never ~118 edges; total excess all classes ~154 (swaps lower at boundary). Oracle ~ 154*7.4e-6 = +0.0011 max.
- ckpt (pre-tail) component analysis of a_tail FN (fn_exp39): boundary-frame a_tail FN in clip-touching comps: size1-2 12, size3 20, size4 38, size5 39 (not touching: 12). Non-boundary a_tail FN inside touching comps: size4 14, size5 30.
  => (b) MIN-2 (keep touching comps n>=4): ~121 FN edges reachable (upper, before FP), adds 2579 comps / 11,612 nodes (+0.55% of 2.11M ckpt nodes). MIN-1 (n>=5): ~69 FN, 1296 comps / 6,480 nodes (+0.31%).
  rough: MIN-2 +0.0009 edges - ~0.0005 node multiplier -> ~+0.0003-0.0004 net (guess, FP edges ignored). Below +0.002 gate.
- KEY: per-frame REAL ckpt node count / clip mean (199 videos): t0 0.926 t1 0.974 t2 1.027 plateau t3-10 ~1.08; t94-96 ~0.92 t97 0.878 t98 0.834 t99 0.786. => 3-frame node-density ramp at both ends already in the ILP-selected node set (ckpt real nodes = raw ILP nodes; pruned_isolated 0).
  synthetic gap nodes summed over videos: t0 0, t1 9, t2 27, t3 58 ... t96 5, t97 4, t98 4, t99 0 vs mid 275/frame -> gap closing effectively off near both clip ends.
- ROOT CAUSE FOUND (guess->strong): exp39 ILP uses BIOHUB_ILP_APPEARANCE_WEIGHT 0.0, DISAPPEARANCE_WEIGHT 2, edge weight -1*p, division 1.0 (notebook config). tracksdata ILPSolver (site-packages/tracksdata/solvers/_ilp_solver.py L285-320) forces disappear==node for nodes with no out-edges, uniformly for all t (no clip-end exemption). => every track must collect sum(p) > 2 (>= 3 edges) to be selected. Tracks STARTING at t>=97 (new starts after breaks, daughters) can never pay -> end ramp 0.88/0.83/0.79; fragments ENDING at t<=2 (break right after clip start) also dropped -> start ramp. Detector is permutation-equivariant 2-frame window (no pos enc), cannot cause it.
- raw geff in friend A cache = ILP solution only (solution frac 1.0) -> ILP change needs GPU rerun or candidate-graph dump.
- CONFIRMED in raw ILP solution (199 videos): track-start fraction per frame = 5.3% mid, 0 at t=97,98,99; track-end fraction 5.4% mid, 0 at t=0,1,2. Mid-clip 15.8% of nodes are in segments aged<=2 (0 at t=99, 5.4% t=98, 10.5% t=97) -> exactly the density ramp. Same for remaining<=2 at the start.
- GT divisions near ends: parent t<=2: 3, t>=96: 2 (of 151).
- WEB: ultrack mip_solver.add_nodes: appear_weight = not(is_first_t|is_border)*appear; disappear_weight = not(is_last_t|is_border)*disappear (https://raw.githubusercontent.com/royerlab/ultrack/main/ultrack/core/solve/solver/mip_solver.py). tracksdata ILPSolver has no such exemption; ExprInput accepts polars Expr.
- (b) all 199 videos, ckpt comps touching start (t0==0) / end (t1==99), size k..5: start k4 -> 66 FN edges reachable, +11.8k nodes; end k4 -> 55 FN, +11.3k nodes; k5: 41/6.5k and 28/6.2k. prob gate 0.5/0.7 barely separates. Edge gain 60*7.4e-6=+0.00045 vs node cost 0.59%*0.1*0.93=-0.00055 per side => (b) ~break-even/negative.
- Node value: average final node carries ~0.061 TP edges; tail-removed touching comps 0.005/node; ILP-dropped boundary nodes ~0.009/node (118 excess a_never / ~12.6k missing nodes) -> ILP waiver upper bound ~+0.0003.
- VERDICT leaning: mixed (phenomenon real, cause = ILP d2/a0 without clip-end exemption, not padding; gains ~0). Writing JSON next.
- JSON written (verdict mixed).
