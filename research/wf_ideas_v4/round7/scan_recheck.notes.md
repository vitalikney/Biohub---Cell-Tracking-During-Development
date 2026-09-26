# scan_recheck notes (round 7)
- 2026-09-26T08:21:51Z start; scan_recheck.json absent -> fresh run
- 09:1xZ read: CONTEXT.md l.1800-2099 (K2/twin read 07:35Z: #37 0.954 L(7.36,7.54]h clean; #38 0.953 L(6.69,6.87]h; finals #37+#38; 08:21Z user chose full rounds);
  earlier recheck coverage (round2-6 scan_recheck.json): floatout, I-077/78, tempfuse, swapfix, clip-boundary, axis-flip, head-shift scale,
  refined-dup, leaf prune, post-freeze, already-divided, AdaBN, stitch g0, efpost, linefit. Round 1 lens_mine-old: runtime-rejected ideas.
- Candidate pool (research/KNOWLEDGE/IDEAS.md refuted list; v3 FINAL_REPORT §i): not yet rechecked -> I-186 tracklet gap LAP g=1..3,
  I-141 hole-fill sandwich, I-042 zsplit / I-128 under-segmentation, I-139 readmit knobs, I-079 split-aware relink, I-014 speed-ups.
- Pick: RC-A gap closing g=1..3 + sandwich (I-186/I-141) measured on exp60 final graphs; RC-B node-miss anatomy / merge share (I-042/I-128)
  measured on exp60; RC-C headroom-rejected ideas re-read with measured #37/#38 latencies (desk).
- Lab infra: _dl/exp60_{a,b}/trainlab/*.npz (presafe/preshort/final graphs, gap_synthetic/gap2_synthetic flags), tools/score_geffs.py GT loader
  (reused from round-6 scratchpad stitch_reach.py).
- Old evidence read: research/wf_ideas_v3/v_linking-on-x138_tracklet-gap-lap_value.json (refuted: g=0 idle; g=1..3 = ~173 FN reach at exp39,
  +0.0005 lab at 0.6 precision; gap radius 5->6.5 um was LB -0.001 'gap closing saturated'); research/wf_ideas_v2/r1_research_hole-fill-sandwich.json
  (73% of hole nodes at 4-6 um sit on the same blob; sandwich passes 44% holes vs 40% random controls); research/wf_ideas_v3/
  v_localisation-training-free_zsplit-under-segmented-z_value.json (6bba misses not merges: close GT pairs <7um = 1% of misses; net -0.0003..+0.0003).
- RC-C desk: research/wf_ideas_v4/lens_headroom.json H1/H2 (H2 polyphase view +0.38 h at N=106), CONTEXT 07:35Z entry (L(K2) (7.36,7.54] h clean,
  L(twin) (6.69,6.87] h). Key: #37/#38 hidden run is DONE (one run public+private); runtime ideas have 0 value for the ticked finals;
  a new K2-based file has <= 0.46-0.64 h slack to the 8.0 h insertion gate vs 0.58 h GPU run spread (round 6).
- Lab script: scratchpad/r7/r7_gaps.py (exp60 56 clips, final graphs, 7 um Hungarian per frame, same matching as round-6 stitch_reach.py).
- 08:2xZ RC-A RESULT (scratchpad/r7/r7_gaps_out.json; 56 exp60 clips, final graphs): end(t)->start(t+g+1) pairs < 20 um, GT-labelled
  (TP = GT path a->..->b with free intermediates and linear interpolation within 7 um of each GT intermediate; FP = evaluable per the official rule):
  g1: TP 1 / FP 137 (0-10 um: TP 1 / FP 9); g2: TP 2 / FP 149 (+3 path-claimed/far) (0-10 um: TP 1 / FP 25); g3: TP 2 / FP 172 (+5) (0-10 um: 0 / 29).
  All TP in 6bba. Unevaluable pairs ~3.9k in 0-10 um (each adds g interpolated nodes). Precision ~0.03 vs break-even ~0.5 -> gap LAP / sandwich
  closed on x138 by measurement (x138 gap_synthetic 5,647 + gap2_synthetic 2,968 nodes already in the final graphs).
- 08:30Z RC-B RESULT (scratchpad/r7/r7_miss_dist_out.json, r7_miss710_out.json): 668 GT nodes missing (endpoints of FN edges; 44b6 64, 6bba 604;
  1,211 FN edge-ends). Classes: merged (nearest final <= 7 um claimed by another GT) 31 = 4.6% (yx-dominant 30, z-dominant 1; GT-GT <= 4 um: 2);
  pruned by x138 tail (presafe node <= 4 um, none in final <= 7 um) 80 = 12%; absent upstream 557 = 83%. Nearest final node: <4 um 2, 4-7 um 29,
  7-10 um 477 (71%), 10-15 um 123, >= 15 um 37. Of the 477 at 7-10 um, 456 (96%) have an UNCLAIMED nearest node; mean |dz| ~4.7 um, |dyx| ~5.6 um
  (z-dominant 194 / yx 283). Sandwich holes (both GT neighbours matched) 93 (14%), 81 of them absent upstream.
  -> zsplit (I-042) ceiling on x138 ~1 z-merge in 668 missing nodes; closed.
- RC-C desk: #37/#38 already ran on hidden public+private (one run) -> runtime headroom cannot change the ticked finals; for a NEW K2-based file:
  slack to the 8.0 h insertion gate >= 8.0 - 7.54 = 0.46 h vs 0.58 h GPU run spread; cheapest headroom rider H2 = +0.38 h at N=106 -> would need
  K2''-style deadlines (37800/32400), a new build + dummy + R4 +0.002 public read before R8 (27 Sep 12:00Z); detection-map class 0/5 on LB. Closed.
- 08:31Z wrote scan_recheck.json (3 recheck-old + 1 new-fact; no revival, no plan change)
