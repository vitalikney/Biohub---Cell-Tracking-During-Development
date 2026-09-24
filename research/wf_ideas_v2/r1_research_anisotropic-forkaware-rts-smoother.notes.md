# r1 research: anisotropic-forkaware-rts-smoother (started 2026-09-24)
## Code read (exp39 cell 7, lines 1299-1370 of cell source; call at 1582 = LAST tail stage)
- linefit per node: walk back while len(predecessor[cur])==1 (up to WINDOW=2), walk fwd while len(successor[cur])==1; need >=3 pts; np.polyfit deg1 per axis in VOXEL coords, eval at dt=0; new = 0.2*orig + 0.8*fit. Only t->t+1 edges used.
- CORRECTION to hypothesis (ii): forks are NOT skipped. Track ends / parents with >=2 linear predecessors get ONE-SIDED fit (-2,-1,0). Daughters: backward walk checks only predecessor count of the daughter (=1: the parent), NOT successor count of the parent -> daughter window CROSSES the fork and includes parent+grandparent => daughters pulled toward parent line (toward sister). Example lateral: PP=0,P=0,D=4.5,D1=5,D2=5.5 -> fit 3.0, new 3.3 (1.2 um toward sister). D1 (t+2) also includes P.
- Per-axis polyfit is scale invariant -> "isotropic" = same weight for z and xy, not unit mixing.
- tail npz (l2_replay/l4_leafprune/tail/<cfg>/*.npz) holds POST-linefit zyx (float), topology src/dst, syn flags. Pre-linefit coords could be recovered by inverting the linear operator (check: recovered z near-integer).
## Session 2 (resumed after crash)
- Re-verified code: parent node (2 succ) gets one-sided (-2..0) fit; daughter window crosses fork (pred(D)=[P] len 1). Units voxel, polyfit per axis.
- B28 grid (12 vids, friend B): w0.8 win2 0.9001; off 0.8856; w0.5 0.8948; w1.0 0.8955; win1 0.8907; win3 0.8993; win4/w1.0 0.8939 -> unimodal around w0.8/win2.
- a_linefit 353 FN (28 44b6 / 325 6bba; 3 GT-division FN).
- discussions: annotation bias dz -0.57 dy -0.24 dx -0.20 um (Le Quang Canh), embryo dependent; constant correction -0.0031.
