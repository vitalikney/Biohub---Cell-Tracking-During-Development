# v_recheck R3-RC-B clip-boundary short-track on x138 — notes
- 2026-09-26 start: no prior JSON; reading CONTEXT tail, scan_recheck, round reports.
- 2026-09-26 ~01:50 UTC read CONTEXT.md l.1576-1983 (PRE-REG v3 R1-R10, ADDENDUM L7 closures incl. 'MIN_TRACK_LEN 4 -0.002', exp60 T9 read, twin f2), round3/scan_recheck.notes.md + .json.
- Evidence files exist in session scratchpad (.../acabaea6-.../scratchpad/recheck3b.py, recheck3c.py/.log/_out.json, recheck3d.py/.log/_out.json).
- Re-aggregated recheck3c_out.json myself with tools/trainlab.summarise_rows: b4 pooled +0.000561 (confirmed), w/o 44b6_9be80b04 +0.000334 (confirmed); W/L 7/47; SEL +0.00000, CONF +0.00109; nodes +0.48%; parity 56/56 (log). Edge sums: TP +25, FP -17, FN -25, div 0 -> gain all edge, loss all node multiplier. Per-clip median -0.0003, top clip 9be80b04 (w=236) +0.042.
- Bootstrap (2000, clip resample): CONF 5/50/95% = +0.00006/+0.00104/+0.00229 (P<=0 0.04); ALL -0.00003/+0.00051/+0.00121 (P<=0 0.058).
- recheck3d.log: global L4 ALL +0.00015 (SEL -0.00074, CONF +0.00099); L5 CONF +0.00041, SEL -0.00040 -> CONF half favours EVERY node-adding arm; so CONF CI>0 of the rescue is the same lab bias, not evidence. LB anchor experiments/RESULTS.md l.38 probe 6 (MIN_TRACK_LEN 4) 0.943 vs 0.945 = -0.002; l.41 probe 9 (8) -0.001.
- v2 bar check (research/wf_ideas_v2/r1_research_clip-boundary-frames.json refined_lab_test): tail-only success = >= +0.001 on SELECTION, boundary FN down >= 25%, nodes <= +0.4%; the 55% win-rate is the Step-2 (ILP) gate, not the tail bar -> finding slightly misquotes, verdict unchanged (SEL 0.00000; b5 nodes +0.26% but SEL +0.0001). v2 arithmetic verifier's relaxed criterion (CONF net>0, CI>0) would nominally pass, but it was never pre-registered and CONF is biased (above).
- VERDICT: agree STAYS CLOSED; refuted=false. R4 (+0.002 public) unreachable from a +0.0006 in-sample lab; no build/probe.
- 22:48 UTC final JSON written (refuted=false).
