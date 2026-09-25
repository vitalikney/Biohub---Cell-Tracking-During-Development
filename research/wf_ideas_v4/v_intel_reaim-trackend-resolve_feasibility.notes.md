# v_intel reaim-trackend-resolve feasibility notes
- 2026-09-25T17:41:10Z start; no prior JSON found.
- 2026-09-25T17:42:00Z read ker11_reaim_plugin_v24.py (709 lines): apply_reaim catches BaseException -> shutil.copyfile + REAIM_DISARMED; no wall-time budget inside; flow_field = per-node python loop (O(nodes x sources_in_frame)); resolve needs scipy.linear_sum_assignment; _rewrite reorders rows (nodes then edges per film) and rewrites via polars write_csv; casts t,z,y,x to int. Plan §e rules read (FINAL_REPORT v3 lines 183-275). CONTEXT 17:20-17:55: K2 18/18 gates green, K2 submit 00:01 26 Sep; exp60 lab shard A pushed 17:15, shard B queued.
- 2026-09-25 (local run) selftest of ker11_reaim_plugin_v24.py: 9/9 PASS (python 3.12, polars 1.44.1, scipy 1.18.1).
- BENCH on K2 dummy output _dl/biohub-exp58-x138-safe-lowref/submission.csv (4 clips, 121,252 nodes, 117,077 edges, T=100):
  44b6_0113de3b: 25,729 nodes, 556 track ends, 143 considered, applied 0 (flow 1.7 s, resolve 0.6 s)
  44b6_0b24845f: 19,545 nodes, 1,120 ends, 204 considered, applied 1 move
  6bba_05b6850b: 6,220 nodes, 147 ends, 25 considered, applied 0
  6bba_05db0fb1: 69,758 nodes, 1,516 ends, 725 considered, applied 1 move
  apply_reaim total: REAIM_ARMED films=4 proposals=1097 applied=2, 16.3 s on laptop CPU -> ~100 hidden clips ~7 min (x2 Kaggle CPU ~15 min) < 20 min cap, << ~4 h headroom. Runtime NOT the problem.
- CEILING (abstain=True): margin 2/1/0 um -> 1+1 / 3+2 / 4+4 moves, 0 adds on every clip. Even margin 0 touches 8 of 117,077 edges (0.007%). x138's relink+gapfill+readmit already consumed every free t+1 target near a track end (0 adds). Risk (a) CONFIRMED: RE-AIM is a no-op on x138's world.
- FORMAT BUGS in a verbatim port on our CSV (id,dataset,row_type,node_id,t,z,y,x,source_id,target_id with -1 sentinels): _rewrite copies the proto edge row's `id` -> 2 duplicate ids; new edge rows get node_id/t/z/y/x = null (empty) instead of -1; rows reordered (nodes then edges per film). Fixable (renumber id, fill -1) but a verbatim port could make the submission fail scoring.
- SCHEDULE: exp60 lab arms are CPU replays in tools/trainlab.py on dumped final graphs -> an RE-AIM arm needs no GPU; LB slots exist (S3 held in branch A, S7-S11 on 27 Sep); latency ~8 h fits R8. But the measurable effect (~2 edges / 117k, <=1e-4 even if all correct) cannot reach the lab gate (+0.001 SELECTION) nor R4's +0.002; an LB probe is a guaranteed display tie (R7: no choice between near-copies at 0.001). Verdict: REFUTED (not adjudicable, near-zero effect; skip the arm and the slot).
