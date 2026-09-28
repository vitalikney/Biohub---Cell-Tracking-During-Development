## arms_2 notes (28 Sep)
- task: gap/track-filter/safe-div two-direction arms; started 08:11Z; code dumped to scratchpad c*.py
- x138 lab stage stats (56 train clips, _dl/exp60_{a,b}/trainlab meta presafe/final_stats): final 1,124,511 nodes / 1,082,114 edges.
  gap close 5,652 pairs (11,304 edges = 1.04%); DC gap veto checked 1,107 (span >= 8.5), REJECTED 904 (82%), accepted 203; bypassed (span < 8.5) 5,449.
  gap2 candidates 3,330 -> selected 1,484 (45%), gap2_skipped_cap 0 -> per-frame cap (max(1, round(0.006*ends))) = 1/frame binds, not the global cap.
  gapfill 437 pairs / 1,053 nodes; readmitted 14,525 nodes.
  safe div: geometric cands 6,617 -> DC rejected 4,854 (73%) -> symmetry rejected 1,036 -> 727 proposals -> 676 added; caps never bind; divergence rejections 34,918, mutual-NN 3,118.
  short-track filter removes 25,231 nodes (2.2%); rescue never triggered.
- exp29 (sjlee 0.947) PUBLIC 4-clip run_stats: gap pairs 610, DC gap checked 115 / rejected 96; gap2 cand 370 / sel 145; safe div 124 added, DC safe-div rejected 414/730.
- gapstats (56 clips, presafe graphs): accepted gap-1 synthetic spans: <5 3402, [5,6) 585, [6,7) 588, [7,7.5) 288, [7.5,8) 293, [8,8.5) 293, [8.5,9) 66, [9,9.5) 44, [9.5,10) 66, [10,10.5) 27.
  -> CONFIRM_MIN_SPAN 8.5->7.5 exposes 586 accepted pairs to the veto (82% reject rate at >=8.5 -> up to ~-480 pairs); 8.5->9.5 bypasses the [8.5,9.5) band (110 accepted; ~600 checked if rejection uniform -> ~+490 pairs).
  gap2 accepted spans: <5 735, [5,6) 163, [6,7) 161, [7,8) 143, [8,8.5) 64, [8.5,9) 45, [9,9.5) 69, [9.5,10) 76, [10,10.2] 28. gap2 has NO DeepCenter veto.
  ends/frame median 6, p90 20, p99 65; >=84 in 0.8% of frames -> GAP2 frame cap = 1/frame almost always.
- safe-div replay (tools/trainlab replay, 6 clips, DC miss -> reject = lower bound) launched in background (~20 s per replay per clip).
- safe-div/rescue replay DONE (scratchpad sdrep.py; 6 clips 44b6_9be80b04, 6bba_78a7bd97, 44b6_aaf8b0ea, 6bba_d2b9fc0c, 44b6_d754aa59, 6bba_7f87b3d8 = 114,271 final nodes ~ public 121k; DC-unscored candidates REJECTED = lower bound, miss count = DC-blind candidates):
  DIVERGE 3.0: forks -15, nodes 0 | DIVERGE 1.5: forks +2 (lower bound), 435 DC-blind candidates (kernel would DC-veto ~73%)
  TAU 0.8: forks +15, nodes +10 | TAU 0.45: forks -16, nodes -10  (tau sits after the DC veto -> exact replay)
  SAFE_DIV_MAX 10.5: +0 lower bound, 183 DC-blind | 7.5: forks -9, nodes -5
  SISTER_MAX 16: 0 (3 DC-blind) | 11: forks -7  -> sister gate barely binds
  RESCUE trigger 0.0: nodes +380 (+0.33%), edges +294, forks 0 (node-adding; raising the trigger is a no-op; lab-closed G34)
- inert/closed in this group: GAP_CLOSE_REUSE_UM (gap_reused_existing 0 on 56 clips), GAP_REFINE_MAX_SHIFT raise (rejected_shift 0), SAFE_DIV caps (skipped_cap 0), EXISTING_CHILD (never binds), GAP_DENSITY_* (<=0.25 um), GAP_CLOSE_UM + MIN_TRACK_LEN already LB-probed (P08; P06/P09).
- c2 repo defaults: DEEPCENTER_GAP_THRESHOLD 0.10, CONFIRM_MIN_SPAN 0 -> x138 cell0 set 0.25 / 8.5 ('holdout-selected' per BIOHUB_SCORE_AXIS).
- 08:33Z arms_2.json written (5 candidates)
