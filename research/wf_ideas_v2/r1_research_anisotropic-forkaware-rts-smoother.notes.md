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
- ckpt coords: z AND y/x on a 1.625-um grid (xy multiples of 4 voxels) -> quantisation sd 0.47 um per axis, isotropic in um.
- Label-free noise from 2nd differences of raw ckpt linear chains (len>=7), 12 vids/embryo (scratchpad noise.py, 6 s):
  r(-lag1/4) um^2: 44b6 z .55 y .42 x .40 ; 6bba z .80 y .51 x .56. r(lag2): 44b6 z .24 y .18 x .15 ; 6bba z .20 y .16 x .10
  lag2 << -lag1/4 => model mismatch: lag-1 excess = step jumps/ID switches (a jump gives lag1 -J^2, lag2 0). White noise part ~ quantisation (0.22 um^2).
  q (var-6r, lag1-based) 44b6 z .70 y .57 x .55; 6bba z 1.24 y .76 x 1.05 um^2/frame^4. Per-video r varies 2-3x (0.28..1.16).
  => z temporal noise only ~1.3-1.6x xy (variance), not 2.5x; the GT-residual z excess is mostly persistent (bias/annotation), which smoothing cannot remove.
- linefit symmetric window: fit at 0 = mean of 5 -> FIR [.16 .16 .36 .16 .16].
- Edge filter (L5) runs AFTER linefit: ~21.5k edges dropped / 15k relinked on 64 sel vids -> linefit smoothed along dropped (79% FP) edges. Pre-linefit coords = ckpt coords by node_id (tail adds no nodes) -> post-tail re-smoothing possible without new base key.
- RTS equivalent kernels (scratchpad kern.py): linefit interior FIR noise gain sum w^2=0.232 == RTS CV at q/r~0.5-0.7 (0.220-0.259). Label-free q/r estimates are 1.3 (lag1) to ~10 (lag2) -> an MMSE-tuned RTS would smooth LESS than the B28 optimum (w1.0/win3 lose, w0.5/win1 lose more). => don't trust per-video q/r in absolute terms; calibrate a global q/r on the lab.
- a_linefit analysis (scratchpad alf.py, tail divnet_rerank_fb435c47e6d4 vs ckpt raw): 371 a_linefit nodes: linefit displacement median 1.33 um (p90 2.41) -> they sit at the 7-um boundary; displacement cap would rescue few. 22% have an unscored (p=0) edge in the +-2 window vs 13.3% of all nodes. All nodes (656k sample, 1/8 videos): disp median .85, p99 3.18; of nodes displaced >2 um, 51% have a p=0 edge in window. Window crosses a fork: only 0.14% of nodes (0.27% of a_linefit) -> fork defect negligible for edges.
- VERIFIED: linefit recomputed from ckpt coords on the tail topology reproduces tail zyx to 3e-14 (6bba_fe670320); all tail nodes are in ckpt -> any re-smoother can be a POST-TAIL replay stage (no new base key).
- edgefilter (min_len 0) uses no positions; stitch uses length gate; divinsert uses positions -> put resmooth AFTER divinsert for identical topology.
- Whittaker (2nd-diff penalised LS) lam=2 == linefit interior noise gain (0.231 vs 0.232); ends: whittaker 0.61 vs linefit 0.84.
- Per-axis lambda=r/q ratio z/xy from label-free stats ~1.07 (44b6) / 1.09 (6bba): z has both more noise AND more process variance -> anisotropic smoothing strength NOT supported.
- Sources: Jaqaman 2008 u-track (github DanuserLab/u-track); TrackMate Kalman tracker doc (CV model, isotropic, no splits); Roudot 2023 u-track3D Cell Rep Methods; Vestergaard 2014 PRE 89:022726 (CVE: lag covariances -> localisation noise); Aravkin et al robust Kalman smoothing (Huber/Student-t, arXiv 1111.2730, 1303.5588); Odelson-Rajamani-Rawlings 2006 ALS noise estimation.
- Verdict drafted: MIXED. Final JSON next.
