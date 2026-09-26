# round5 scan_hypotheses notes (started 2026-09-26T03:16:08Z)
- 06:20Z: no round5 json existed -> fresh run. Read CONTEXT tail (l.1750-2055), round3/round4 REPORT.md.
- Lab logs _dl/exp60_a (6,988 s) / _dl/exp60_b (5,624 s): 0 'REPAIR FAILED', 0 Traceback, 0 'DEADLINE' fires, failed_hooks 0, missing [] on 56 clips.
  Retention guard fallback_frames: shard A 621/2800 frames (44b6_9be80b04 and 44b6_e28840c6 100/100, 6bba_ab78413d 93/100) - x138 own guard, deterministic.
- Notebooks extracted: K2 exp58 = 14 code cells (cell 7 = 101 KB repair), twin exp58n = 12 cells (cell 5 = 98 KB repair).
- 03:20Z: poll.log 03:13:26Z: #37 K2 56563521 and #38 twin 56563534 both PENDING.
- K2 vs #35 (exp57b) notebook diff (scratchpad r5hyp/e57b.py vs k2.py): ONLY cell 0 knobs, the lowdet patch (lowrefine lines) and cell 7 safetail
  (degrade keep_div, safetail_divins_allowed, try/except around the insertion). NOTE: in #35/P36 the insertion was NOT locally fail-soft:
  any insertion exception went to the per-dataset except -> 'REPAIR FAILED' -> fallback_output_graph for the whole clip. K2 reverts
  only the insertion. insert_divisions never mutates its inputs (docstring + code: new list, id()-based removal), so the revert is exact.
- v1284 refine module (extracted to r5hyp/v1284.py): stateless except _CACHE = the head weights; clips to the feature grid; raises only on
  non-finite or >2 um displacement (bounded() makes |shift| < 2 um by construction) -> lowrefine cannot pollute the main refine and
  cannot raise outside its per-frame try. Order: lowdet refine runs BEFORE the main refine in the same frame; no shared state.
- run_stats counters, 56 lab clips (exp60 a+b): repair_fallback 0, deadline_degraded 0, motion_relink_fallback_raw 0,
  motion_relink_skipped_large_frame 0, deepcenter_*_missing 0, short_track_filter_skipped_all 0, gap_refine_failed 14 (one clip
  44b6_0db75fae, benign midpoint fallback), linefit_skipped 92. K2 dummy: same zeros; divins_skipped_cap_video 172 (cap 4 binds).
- ILP time: lab max 67.5 s at 98,233 candidate nodes (6bba_57b7cc1e); dummy max 79.4 s at 76,396 -> 15x below the 1,200 s ILP timeout.
  Repair max 417 s/clip (lab), mean 91 s; raw nodes/clip 4,609-75,544 (46-755 per frame).
- Lab insertion ran at threshold 1.5 (dump-only): eligible 0 / added 0 on all 56 -> the in-kernel added>0 path was exercised only on
  the 4 dummies (12 forks) and on the hidden test in #35/P36.
- SMOKE TEST (r5hyp/smoke.py; K2 cell-7 functions exec'd via ast): readmit + gap filler on the 56 lab ILP geffs with the lab int16 pool vs
  a float pool (score>=0.965 peaks moved <=1.9 um, like lowrefine): 0 exceptions, 0 non-fatal/idle in both arms; readmit 18,178 -> 18,888.
- DaughterNet scoring time (in-kernel, lab 56 clips, dump-only): 2,907 s total = 52 s/clip, max 290 s (6bba_57b7cc1e, 34,794 nodes
  scored); K2 dummy 298 s / 4 clips. ~100 hidden clips -> ~1.4 h, consistent with L35 - L34 ~ 1.3 h. Lab triples min 81 (no clip
  had 0 candidates; the empty path is covered only by code reading: _dv_ids empty -> zeros((0,3)) -> insert_divisions returns the
  same list object).
- experiments/runtime_step0/step0.md l.19-20: "the hidden rerun processes public AND private clips in ONE run ... no separate denser
  private run" -> any kernel-level crash on a private clip would have made #34/#35/P36 ERROR. They are COMPLETE, so the x138 core +
  insertion code has no crash path on any hidden clip; #37/#38 COMPLETE will prove the same for lowrefine + safetail.
- Guard cells (K2 cell 8 retention guard + cell 12 asserts) turn any topology anomaly on any clip into a whole-kernel ERROR (not a
  per-clip fallback). The writer loop (NaN coords -> int(round(nan)) ValueError) is also outside the per-dataset try. Invariants the
  insertion keeps: u has exactly 1 out-edge before, v orphan or its only in-edge stolen, used-set, v at t+1 -> in<=1, out<=2, dt=1.
- Smoke script: C:/Users/vital/AppData/Local/Temp/claude/.../scratchpad/r5hyp/smoke.py (output smoke_out.txt).
- Verdict: no real bug found in any K2/twin path; no rebuild justified; nothing to submit.
- 03:31Z: final JSON written (9 findings, R5H-1..R5H-9).
