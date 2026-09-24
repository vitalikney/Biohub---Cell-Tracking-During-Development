# feasibility notes (anisotropic-forkaware-rts-smoother) started Thu Sep 24 16:23:56 UTC 2026
- linefit code (exp39 cell 7): per-node polyfit, original_pos local; call is last line of filter_output_graph before FINAL print; divinsert/edgefilter/stitch anchor after it
- replay.run_config_video: tail -> ef -> sw -> st -> insert(div_insert returns edges only; nodes unchanged) -> geff -> score. post-tail hook for rs.* is ~same pattern as st/sw
- replay write_geff and kernel CSV both round coords to int voxels (z step 1.625 um, xy 0.406 um): lab is faithful to LB; sub-0.81um z moves vanish.
- div_insert adds edges only (no nodes) -> resmooth after insert keeps node set; stitch/edgefilter add no nodes (ef prune only removes).
- pre-check (scratchpad pre.py, 6bba_05db0fb1, tail divnet_rerank_fb435c47e6d4): linefit on ckpt raw coords + tail topology reproduces tail zyx max err 0.0. 70,257 nodes, 68,145 edges, 2,308 edge_prob==0, 809 NaN. Re-linefit WITHOUT the prob0 edges: 11.1% nodes move >0.5 um, 7.7% >1 um, 11.6% change rounded output coords -> pre-check (>1%) passes, measurable signal.
- Kaggle CPU lab port agent PAUSED (CONTEXT 13:35 UTC); lab runs at idle on laptop -> compute-availability risk, not a code risk.
- 6bba_085bf656 (8,293 nodes): only 25 prob0 edges -> 0.9% nodes >0.5um, 1.05% rounded coords change; 2 linefit passes + load ~8 s wall at nice. Signal is concentrated in big dense videos.
- pitfall: edgefilter treats edge_prob None as gap/safe-div (exempt); rs cut must use prob==0 (never-scored relink), NOT None, else it cuts every gap-closed track.
- verdict: feasible (post-tail, topology-identical, ~0.5-1 day code incl. no-op test); risk = gain below gate and lab-compute availability; lambda_z configs likely inert because z output rounds to 1.625 um.
