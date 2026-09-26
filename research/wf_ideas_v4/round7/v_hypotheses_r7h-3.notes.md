# v_hypotheses r7h-3 notes
- 2026-09-26 start: no prior json; reading CONTEXT l.1780-2112, exp60 results, round6 REPORT
- 2026-09-26 verified: CONTEXT 20:35Z (l.1924-1930): forkmid ORIGINAL T9 FAIL + L3 FAIL; "the sign is favourable but the '>= 3 evaluable FP' power clause fails"; l.2021 closure list "K3 forkmid (power)".
- experiments/exp60_trainlab/results.md l.76-150: forkmid_v2 (L3 pooled) only failing check = removed_evaluable_fp_ge_3 (1 FP; 39/40 removals unevaluable); score +0.00013, div_J +0.0010, adj_edge +0.00002.
- lowrefine sensitivity fails removed_tp_eq_0 only because tools/trainlab.py l.651-660 RELABELS readmit-touching rows (metric-ignored) as TP when removed or within 0.7 um of 4.5 -> worst-case proxy, not measured harm.
- ORIGINAL T9 '>=1 FP on 44b6' clause: L3 (CONTEXT 18:20Z) dropped it BECAUSE lambda_44b6 ~0.1-0.4 -> itself a power clause.
- research/KNOWLEDGE/FACTS.md F-TRN-11 and F-TRN-22 record "forkmid power". So "closed-only-for-power set is empty (forkmid included)" contradicts the record. 
- Other audit items verified: forkblob TP1/FP6, div_J 0.1290->0.1271 (20:05Z); ANTIPAR -0.00034, break-even 7.7 (20:55Z); K3b all four fail (20:35Z); b4 SELECTION 0.00000, 7 vs 47 (round3 REPORT l.107); leaf prune closed by P36 rule (19:05Z (b), 01:20Z item 5); insertion +0.001 twice (#34 0.953/#35 0.954; K2 0.954/twin 0.953) - rounded.
- Action conclusion (no power-rescue lab before R8) still right, but for value/cost (r7h-2: P(pass)~0.4, EV ~2-4e-5, builder change, K3 slot, R3 lets F1 show 0.953), not because the set is empty.
- VERDICT: refuted (factual premise wrong on forkmid); fix = reword curator message.
