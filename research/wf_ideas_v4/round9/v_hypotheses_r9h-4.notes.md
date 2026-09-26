# r9h-4 skeptic notes (2026-09-26T12:56:47Z)
- no prior v_hypotheses_r9h-4.json; started fresh.
- (A) 73/13,284 readmitted-final-node GT match confirmed: round7/report.json l.66, round2 v_plancheck_pc2-13 (56-clip exp60 lab). "1,337 of 121,777" is the exp56/K1 dummy count (CONTEXT l.1515), not the lab pool - minor mixing.
- (A) the node-count term is NOT necessarily +-1e-4: 13,284 flagged of ~0.9M lab final nodes (~1.4%) -> removing all gives up to ~+0.1*1.4% ~ +0.001 bonus minus ~73 matched nodes' edges. But the real anchor exists: leaf prune on x138 = 95% readmitted removals (CONTEXT l.1511-1516, l.2033): exp60 lp30 +0.00083 lab, P36 delta 0 on LB -> closed. Readmit knobs are R4 by name (l.1650); LB anchor 'readmit -0.001' (l.1884). So (A) = leaf prune in disguise, closed line.
- (B) R2 'only #35 configuration; no ladders' confirmed CONTEXT l.1643-1646; fold vs ensemble p (0.90 vs 0.83) confirmed CONTEXT ~l.1302.
- (C) V2 checklist CONTEXT l.2041: 'never tick #35 or P36; tick #34 only when no eligible non-copy x138-family file exists' confirmed.
- (D) round8 v_recheck_r8-rc-a refuted=True (z shift, embryo-dependent 44b6 +0.15 vs 6bba +0.45 um; honest size +0.0003..0.0005) confirmed.
- verdict: finding holds (refuted=false); fix: correct A's reasoning to the leaf-prune/LB anchor.
