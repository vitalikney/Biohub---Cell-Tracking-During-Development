# feasibility notes (stitch-tie-aware-gate)
- started Thu Sep 24 16:16:30 UTC 2026
- code: tools/build_probe_kernel.py L669-830 stitch_final_graph exists; replay.py st.* keys, order ef->sw->st->divinsert; lp030 tails already cached (l5_confirmation_vs_lp030.md), so e48 tails NOT new
- in-memory compose (scratch script, nothing written to repo): leafprune+divinsert+edgefilter+stitch+coordhead compile in 2 patch orders; tail order always leafprune -> linefit -> edgefilter -> stitch -> divinsert; ILP capture before relink.
- writer after filter_output_graph uses only source_id/target_id -> extra 'stitched' key harmless. Kernel divinsert scores nodes LIVE with DaughterNet (score_nodes) -> no missing-p in kernel.
- cand_exp39_ef.parquet ILP stitch cands 6956 (38/video), ilp_p min 0.480, median 0.81; p<0.3 share 0 -> steal (steal_prob_max 0.3) can NEVER take a stitched edge; research pitfall (3) moot.
- lab node_p (l2_replay_v2/node_p/21c278c1358028a9) covers only 46% of stitch sources u and 91% of targets v -> lab under-represents new single-child parents created by the stitch (kernel scores them). 62% of cands have dist <= parent_um 10.
- evaluable by p: <0.6 22TP/4FP, 0.6-0.7 18/7, >=0.7 231/8.
- leaf-prune tails already cached (.public_local_cache/l2_replay/l4_leafprune/tail) -> e48 base may need no new tail pass if run in that out dir.
- verdict: feasible (not refuted); caveats: coordhead base untestable in lab, depends on probe 29, kernel ENABLE=1 never run on Kaggle yet.
