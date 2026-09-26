# v_recheck R6-RC-C linefit-after-head (skeptic, value+feasibility) - 2026-09-26
- No prior JSON for this task; started fresh.
- Source: experiments/exp60_trainlab/results.md l.43-48 + results.json gates/linefit_record_only (44b6 SEL -0.00558, CONF +0.00077, ALL -0.00309; 6bba SEL +0.00011, CONF +0.00013, ALL +0.00012). Parity PASS; nodes/forks delta 0.
- Per-clip (results.json clips[].arms.linefit_w07_win2.row vs control.row): 44b6 only 4/17 clips change: 2f31 -1TP (adj -0.0209), c771 -4TP (adj -0.0347, node_recall -0.0044), e35b -1TP (-0.0069), e57f +2TP (+0.0170). Net 44b6 -4 edge TP. c771+2f31 alone = most of the SEL -0.0056.
- 6bba: 15/39 clips change, 9 up / 6 down (4f99 FP only), net +1 edge TP. Total over 56 clips: net -3 TP -> effect is NULL (noise-level), not a real negative; 'premise refuted' overstates it, but closure is still right: no positive signal anywhere.
- 0.6 not measured; B28 (CONTEXT l.206) 12-video grid: w0.8 win2 unimodal optimum, every deviation loses; w0.7 null on head base -> no reason to expect 0.6 to win.
- Feasibility: a weight change is a knob (not a new mechanism, R-rules: no public knob ladders); LB cannot validate a ~1e-4 change at 3 decimals; zero runtime; byte-identical when off trivially. No build justified. Verdict: finding survives (refuted=false) with wording correction.
