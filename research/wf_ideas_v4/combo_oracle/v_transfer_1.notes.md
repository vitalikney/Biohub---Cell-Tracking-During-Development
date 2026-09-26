# v_transfer_1 notes (skeptic, INTERPRETATION lens)
- 2026-09-26T18:18:28Z start: v_transfer_1.json absent -> fresh. Read m_transfer_arith.py/.log/_out.json, m_transfer.notes.md, m_joint_oracle/m_realistic notes, IDEAS I-047/I-056/I-164/I-200, scan_hyp_graph.notes.md l.9.
- Re-derived div arithmetic by hand: 25/130=.19231; 25/99=.25253 (+.00602); 32/130=.24615 (+.00538); 32/99=.32323 (+.01309). Matches.
- Superadditivity = 0.1*7*(1/99-1/130) = 0.1*217/12870 = +0.001686 (matches +0.00169). But the stated mechanism "both shrink the same denominator" is WRONG: attach moves FN->TP, T+F+N stays 130; only O_FP shrinks D (130->99), so each attach TP is worth 1/99 instead of 1/130. Number right, explanation wrong.
- I-056 AUC 0.73 = parent-intensity feature for B22 division re-rank; "ranker power never measured"; not measured on fork-removal or orphan-attach pools. Applying it to both classes is borrowed.
- Linking +0.0032 = 136 dangling FN at p=1 pro rata; structurally reachable both-free end->start is 11 FN (~+0.0003, I-164). So the link third is an upper bound; with the reachable link the joint is ~+0.0138, not +0.0168.
- m_joint_oracle full run still in progress (test1.json.partial growing, 3 python procs). Its 1-clip test shows O_FPgt (drop the FP child) keeps the TP edge that O_FP loses -> O_FP understates the fork oracle edge side.
- 2026-09-26T18:20:32Z ran scratchpad/combo/v_transfer_1_check.py -> _out.json: superadd formula 0.1*7*(1/99-1/130)=+0.001686 OK; Wilson90 8/17 .29-.66, 20/25 .64-.90 OK; binormal re-run on 300x300 grid: joint7 at AUC .985 = 69.8%, .99 = 75% (claim 'AUC ~0.99' OK); joint17 reaches +0.012 lab div-only at AUC ~0.97 (the R4 bar in absolute terms needs AUC ~0.97 on the wide pool, ~0.99+ on the gated pool). O_FP edge side approx +0.00027 reproduced; O_FPgt upper ~+0.00068 (so fork oracle ~+0.0067, under-sold by <=0.0004). Reachable link (11 both-free FN) ~+0.00026 -> joint7+reachable link ~+0.0138 vs +0.0168 with the 136-FN ceiling.
- m_realistic partial (7 44b6 clips, test1.json.partial snapshot v_t1_snap.json): oracle_L (end->start <=12um GT pairs) = 0 on 44b6 while the pro-rata link spread assigns 44b6 +0.0048 -> per-embryo 44b6 link number is an assumption, not a measurement.
- waiting for combo_oracle.py combo_out.json (m_joint_oracle, 6 workers) for the measured sequential joint.
- 2026-09-26T18:37:58Z combo_oracle.py (m_joint_oracle) finished 56 clips; copied to scratchpad/combo/v_t1_joint_full.json, aggregated with its agg.py -> v_t1_joint_full_agg.json (official summarise_rows). MEASURED (ALL / 44b6 / 6bba):
  O_FP +0.00629/+0.00695/+0.00577 (reproduces); O_FPgt +0.00671 (edge +0.00068, 20/0 W/L);
  O_ATT_g +0.00541 (32/31/67; 44b6 0); O_ATT_w +0.02039 (51/31/48, 26 kept TP, not 17 -> analytic +0.0135 under-sold);
  O_LINK (GT relabel: remove 25 both-matched non-GT edges, add 151 end->succ, 136 swaps) +0.00734 (44b6 +0.01658, 6bba +0.00655) vs pro-rata +0.00324;
  O_FP+O_ATT_g +0.01339 (analytic +0.01353 OK); O_FP+O_ATT_g+O_LINK +0.02056 (44b6 +0.02354, 6bba +0.02009) vs claimed +0.01677;
  O_FP+O_ATT_w+O_LINK +0.04115 vs claimed +0.02711; O_FPgt+O_ATT_w+O_LINK +0.04157. Info: O_EDGEALL (every FP edge removed) +0.0646.
  Sum of singles (g) .00629+.00541+.00734=.01904 < joint .02056 -> +.0015 superadditive, all on div side.
- Binormal with measured 26-TP wide pool (698 negatives): joint div at AUC .73 +.00055, .90 +.0079, .93 +.0109, .95 +.0136 -> R4 (+0.012 lab) needs AUC ~0.94 on BOTH edit classes with realistic link ~0 (I-164 reachable ~+0.0003). Verdict (not buildable before R8) holds.
- R4 as fraction of oracle: +0.012 = 58% of the gated all-three (+0.0206), 29% of the wide all-three (+0.0412) -> '70% needed' is wrong framing (R4 is absolute).
- 2026-09-26T18:38:27Z wrote v_transfer_1.json (refuted=false; numbers corrected upward, mechanism/framing fixes).
