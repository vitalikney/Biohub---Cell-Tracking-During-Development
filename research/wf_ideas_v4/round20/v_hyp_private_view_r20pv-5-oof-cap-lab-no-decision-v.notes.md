# r20pv-5 oof-cap-lab-no-decision-value skeptic notes (2026-09-27T20:27:39Z)
- 2026-09-27 ~20:3xZ: checked; no prior JSON for this task.
- Existing in-sample cap lab: research/wf_ideas_v4/reach0955/ins_cap6.json (CONTEXT l.2545-2549): cap6 vs ins35 pooled -0.00057 (44b6 -0.00079, 6bba -0.00052), cap5 -0.00015, cap8 +0.00003; 85 extra insertions = 0 TP / 4 FP / 81 unannotated. So only 4 scorable marginal forks -> precision CI ~[0, 0.5] (Wilson n=4). Finding's "4-8 scorable, +-0.3" matches.
- LB: probe 45 exp70g (cap 6) = 0.956 (CONTEXT l.3196) vs K2 0.954 -> the in-sample lab sign was already WRONG vs public for this very knob; lab cannot arbitrate cap.
- node_p_oof.parquet = L2 KDN node classifier OOF (biohub-l2-kdn-score, 5 folds, 199 videos; kds_out/node_p_oof_summary.json), NOT DaughterNet. Replaying caps with it re-ranks candidates with a different model than the deployed one; scorability is set by GT sparsity (81/85 unannotated), unchanged by OOF.
- divins_dump: _dl/exp60_a/divins_dump has 28 npz (44b6 + 6bba clips) - feasible on CPU, but no decision it can move.
- Decision path: cap direction decided by LB rungs exp78a (cap 8) / exp78b (cap 12+fc2) on 28 Sep (CONTEXT l.3201-3210); finals picked by user on 29 Sep after all variants (l.3228ff). R19 READ TABLE v2 already carries the DIV caveat 'lab cap > 4 = 0 TP / 4 FP / 81 unannotated' (round19/report.json). An OOF number would at most restate that caveat.
- Verdict: finding stands (not refuted). Curator note to I-069 is fine.
