# v_hyp_post_deadline_r12p-1 notes
- 2026-09-26 started skeptic check of r12p-1 (recheck-old, post-deadline ceilings)
- No prior v_hyp_post_deadline_r12p-1.json -> fresh run.
- combo_oracle/m_joint_oracle.json: O_FP +0.00629, O_ATT_g +0.00541, O_ATT_w +0.02039 (26 TP), O_LINK +0.00734, gated joint +0.02056, wide joint +0.04115; O_EDGEALL +0.06462 (d_adjEdge +0.0586; 1,676 FP edges removed, 1,651 with one end unmatched); O_FP+O_ATT_w+O_EDGEALL +0.1111 = absolute no-new-node ceiling of the bed.
- v_joint_oracle_0: like-for-like (no-swap) joint +0.01428, no-swap links +0.00106; swap = GT jump/offset detection.
- AUC threshold: v_transfer_1 l.18: +0.012 needs AUC ~0.94 ONLY on the WIDE 26-TP/698-neg pool; on the GATED pool the div joint maxes at +0.0131 and needs AUC ~0.995; v_transfer_1 check: 17-pool needs ~0.97. m_transfer AUC 0.95 -> +0.0061/+0.0092 (7/17 pools) < bar. Finding pairs '84% of gated like-for-like' with 'AUC ~0.94' = mixed pools.
- Pool check (scratchpad/combo/combo_out.json info sums): gated pool 9,852 pairs / 9,185 starts, greedy 9,118 adds -> div FP 231 (200 new), 7 TP; wide 90,729 pairs / 30,045 starts, greedy 29,605 adds -> div FP 729 (698 new), greedy 17 TP, GT-strict 26. The 698 negatives = scored FP only (unscored forks free) -> binormal N is consistent.
- 1/6 applied to oracle in (b) = category error per v_joint_oracle_1 #3 and v_transfer_1 #5.
- IDEAS I-079 already 'closed for the finals; post-deadline as a learned far-daughter slot' (Curation 8) -> geometric-form closure is a repeat. CONTEXT l.2369-2379 already records combo oracle -> I-079. I-252 R11-A7 line 'linking <= +0.003' is the one stale number worth correcting (no-swap +0.00106).
- 2026-09-26T20:47:17Z wrote v_hyp_post_deadline_r12p-1.json (refuted=true as written; fix = corrected curator text)
