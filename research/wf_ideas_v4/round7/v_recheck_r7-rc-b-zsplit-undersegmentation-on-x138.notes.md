# v_recheck R7-RC-B zsplit (skeptic)
- 2026-09-26 start: no prior json; reading scan_recheck, CONTEXT tail, v3 FINAL_REPORT sec i, round reports
- 08:35Z verified sums: 668=64+604, 1211=121+1090, merges 8+22+1, pruned 12+68, raw 44+513, 7-10: 41+436 (6bba 91%), unclaimed 38+418=456/477, mean dz 4.74 dyx 5.65 (r7_miss710_out.json). 7 um official max_distance (tools/official/src/tracking_cellmot/division_metrics.py:94). np.round(P) matches submission writer (CONTEXT l.812-813).
- annotation fractions: 44b6 ~1%, 6bba ~9% (CONTEXT l.19-20) => nearest-pred 'unclaimed' base rate 91-99%; 96% is not evidence of a class.
- v2 valley test (research/wf_ideas_v2/r1_hyp_detection.notes.md l.8): 4% of 326 7-10um misses show a valley (exp39) -> same object; this, not the claim stat, is what closes the 7-10 um merge reading.
- 08:35Z CONTROL (inline python, exp60 56 clips, same 7 um Hungarian): matched GT nodes whose nearest OTHER final node is at 7-10 um: unclaimed 1611/1703=94.6% (44b6), 11599/11884=97.6% (6bba); z-dominant 27.6% / 24.8%. Missing GT at 7-10: unclaimed 92.7% / 95.9% (= base rate, uninformative); z-dominant 41.5% / 40.6% (excess vs control ~+15 pp -> axial offset signal, consistent with v2 'same object, axial elongation').
- merges within 7 um with an UNannotated neighbour are not misses (Hungarian gives the blob to the lone GT), so the 31 annotated-pair merge count is complete for the <=7 um class; 7-10 um neighbour-peak merges are not separable by this script -> rely on v2 valley test (4%).
- verdict: closure stands (z-split/I-042, I-128 stay closed); FACT wording needs 3 fixes; no build, no probe.
- 08:36Z final JSON written (refuted=false, wording fix).
