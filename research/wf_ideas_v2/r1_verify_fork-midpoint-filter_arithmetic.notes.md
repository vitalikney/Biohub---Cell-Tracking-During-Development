# verify fork-midpoint-filter arithmetic (started)
- Recomputed from scratchpad div_audit8.json (exp39 final, 199 videos): forks TP 23 (44b6 5 / 6bba 18), FP 43 (10/33), free 1948. GT div 151 (26/125).
- mid>=4: 11 FP (44b6 1, 6bba 10), 0 TP, 358 free; >=4.5: 6 FP; >=3.5: 16 FP 1 TP. TP max mid 3.76. 11 videos change FP status (105 with any removed fork).
- Pooled local J 23/194=0.1186 -> 23/183=0.1257 (+0.0071 J, +0.0007 score). 44b6 5/36->5/35 (+0.0004), 6bba 18/158->18/148 (+0.0008). Ceiling (all 43 FP) 23/151 -> +0.0034. Rule captures ~21% of local ceiling.
- Public (assumed 19/13/21, J .358): -1 FP +0.0069 J, -1 TP -0.0189 J. Break-even TP loss rate g = f*FP/D = .256*.245 = 6.3%. Beta posterior from 0/23: P(g>6.5%) ~ 0.2.
- HOLE: ship base is exp48 (divinsert, mid_um 6.5, cos 0.25). Divinsert added ~+10 TP / +21 FP locally (sel 7->13 TP, 15->25 FP; conf 16->20, 28->39). None audited for mid. GT divisions eligible under divinsert gate: 142, of which 25 (17.6%) mid>=4, 18 >=4.5 (GT coords). Expected ~1.8 divinsert TP lost at 4.0; P(0 lost of 10) ~0.06-0.14 -> pre-registered criterion (1) likely fails.
- exp48 local est: TP 33 FP 64 FN 118 (D 215, J .1535). FM40 on all forks: -11 safe-div FP, -~7? divinsert FP, -1.8 TP -> 31.2/197 = .158 (+0.0005) or, if few divinsert FP removed, 31.2/204 = .153 (-0.0001). Each local TP lost = -0.00047 score.
- Fix: restrict forkmid to safe_division forks (exclude div_inserted) -> exp39 audit applies directly; or measure divinsert fork mids first.
