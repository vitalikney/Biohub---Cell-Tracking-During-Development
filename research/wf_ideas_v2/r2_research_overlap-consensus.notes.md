# r2 research: overlap-consensus (notes)

- 2026-09-24 start. No prior json.
- Prior measurements live in r2_critic.notes.md lines 5-17 (overlap.py..overlap4.py, sixbba2.py, calib.py in scratchpad). 6bba: MIP phase corr finds no spatial overlap in 645 time-aligned pairs; 44b6 overlaps found at exact offsets (peaks 0.07-0.18).
- make_splits.py: 6bba has a few ONE-FRAME boundary overlaps between consecutive crops (independently annotated) -> registration must require >=2-3 overlapping frames or the pass is not an exact no-op on 6bba (position averaging would touch 1 frame).
- Data for local check: .public_local_cache/l2_fn_anatomy/match/divnet_rerank_fb435c47e6d4__ef_7500fcb4b5/*.npz (e_src,e_dst,e_tp,n_id,n_match) + positions from l2_replay/l5_edgefilter/tail/divnet_rerank_fb435c47e6d4/*.npz
- MEASURED oc_reach.py / oc_reach2.py (scratchpad; exp39+ef match files, 44b6 GT-shared pairs, offset from GT median):
  mapping sanity on 2,012 concordant-TP unique edges: B node -> nearest A node median 0.90 um, 89.7% <=2.5 um, nearest = A's matched node 98.4%.
  200 discordant (FN in X, TP in Y), 25 concordant FN. Of the 200: no X node within 2.5 um of Y's matched node at BOTH ends 97, at v only 27, at u only 21 (=145, 72%),
  one end same node 41, same nodes but edge missing 10 (5%), corr nodes but X matched others 4. Y->X nearest dist median 4.05 um (vs 0.90 concordant).
  => graph-only rules (a)/(b) (edge replacement between MNN-2.5um correspondences) reach at most ~10-14 of 200 discordant; the lever is NODE-level: replace X's nodes by Y's in owner regions (splice), not edge replacement.
- MEASURED oc_hash.py: EXACT-CONTENT ANCHOR HASHING registration (anchor = voxel equal to 3x7x7 max filter and > frame p99.5, hash = blake2b of raw uint16 3x5x5 patch, vote offset = anchor coord difference):
  pair 44b6_12dfb391 / 44b6_3a861e03 (52 shared GT): 3 A frames x 8 B frames -> single offset (dt,dz,dy,dx)=(-86,6,-114,75) with 158 votes = GT offset exactly (note dz=6, nonzero); exact voxel equality on overlap 1.0 (1.49M voxels); nulls vs 6bba_05b6850b and unrelated 44b6_0113de3b: 0 hash hits. ~0.3-0.5 s/frame CPU (max filter) -> do it on GPU (torch max_pool3d) inside detection loop.
  => better than MIP phase correlation (44b6 peaks 0.07-0.18 overlap the 6bba null <=0.12, per critic). Zero FP by construction.
- Dummy test clips 44b6_0113de3b and 44b6_0b24845f are in DIFFERENT leak groups -> interactive kernel run is a negative (no-op) smoke only; need a debug mode on known train pairs for a positive smoke.
- Leak groups: 11 groups sizes [24,11,6,4,3,3,3,3,3,2,2] = 64 of 71 44b6 videos; 7 standalone.
- Sources: linajea (Malin-Mayor et al. Nat Biotech 2023, biorxiv 2021.07.28.454016): blockwise ILP with context >= cell motion, existing neighbour solutions as constraints, appear/disappear cost 0 at block edges. Ultrack: time windows with overlap, only one shared frame used as constraint (stitching).
- MEASURED oc_sim.py: owner-propagation simulation (owner = copy with max min(border_um, 1um*frames_to_end) of the GT edge; every copy takes owner's TP/FN), FN side only: net +89 FN units (fixed-broken) on 44b6, per leak group {g0:+67, g1:+4, g2:+3, g3:+4, g4:+1, g6:+4, g7:+1, g8:+4, g9:+1, g5:0, g10:0}; 9/11 groups positive, 0 negative, but group 0 (24 videos, 2,909 of 4,374 multi-copy instances) = 75% of the gain -> leak-group bootstrap CI will be wide.
  +89 / D_44b6 (~21,148) = +0.0042 on 44b6 ceiling (perfect splice, FN side only); pooled 199 (D ~135.7k) = +0.0007.
- Notebook: submission.csv = flat rows (dataset,row_type,node_id,t,z,y,x,source_id,target_id) written by write_test_submission (exp51 cell 8/13) -> the pass can be ONE standalone final cell: read submission.csv + test zarrs, register, splice, rewrite csv.
- Web: no source (hosts, royerlab repo, forum) says how test clips were cropped; hosts only: 2 embryos, similar size, same protocol. Test layout unknown.
- Idea: optional bit-probe submission (kernel raises if >=1 exact-overlap pair among hidden test videos) answers the structure question for the WHOLE test (public+private) in one submission before engineering; needs user approval.
- final JSON written (valid)
