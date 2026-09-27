# v_hyp_node_count_r13nc-3 notes

- 2026-09-27 (round 13 skeptic) start. No prior json. Probe 40 exp70a 56589065 still PENDING in experiments/lb_poll/ledger.md.
- Verified numbers: scratchpad acabaea6.../scratchpad/r13nc/ncarms2_agg.json arm lp30_preins: ALL +0.000962 [0.000574, 0.001386], W/L 52/4, frac 0.507%, dTP +2, dFP -21; 44b6 +0.001386 [-0.00084, +0.00428] (CI crosses 0, 17 clips, 7 matched dropped); 6bba +0.000923. lp50 +0.000930. Numbers match the finding.
- Prune semantics: ncarms2.py lp() == tools/build_probe_kernel.py prune_weak_leaf_nodes (l.454-500) except the isfinite check (irrelevant). OK.
- NOT "exact K2": the exp60 ins35 bed has NO lowrefine (CONTEXT l.1863 "lab base has no lowrefine"; experiments/exp60_trainlab/results.md l.78/118). lowrefine refines readmitted lowdet peaks; round 4: 95% of lp30 drops are readmitted leaves -> same nodes; non-additivity already flagged in research/wf_ideas_v4/reach0955/v_ladder.json.
- NOT new: round 4 (CONTEXT l.2033) exp60 lp30 +0.00083 / lp50 +0.00064 on x138; P36 (x138+lp30+ungated ins, 56555189) = 0.954 = #35, unrounded above #35 (in-block rank 18th -> 6th). exp70a ~= P36 + lowrefine (+ safetail no-op, gated insertion that did not fire on #37).
- P(display 0.955): v_ladder skeptic already corrected r_ladder's 0.2-0.3 to 0.05-0.15, expected +0.0000 (-0.0002..+0.0002) over TEAM BEST (max of P36, K2, #35). R13NC-3's 0.10-0.25 (vs K2 alone) ignores that the P36 anchor already spent the lp30 increment on public. Team best 12-13th of ~99 in the 0.954 block -> probably just below 0.9545 but P36 did not cross it.
- "Close I-312 if 0.954": low-power read (display 0.954 cannot tell +0.0002 from 0); acceptable only as closure-by-exposure ('no display move at the only existing-knob rung'), not as 'node lever has no public effect'.
- Feasibility: nothing to build; exp70a already submitted 21:17:47Z (ledger PENDING at 01:09Z poll), L9 class A. No rule conflict. No action beyond reading probe 40.
- 2026-09-27T01:16:49Z final JSON written: refuted=true (framing/novelty/P overstated; action unchanged).
