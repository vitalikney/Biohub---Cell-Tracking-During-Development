# round45 scan_recheck notes (started 2026-09-29T18:13:44Z)
- 2026-09-29T18:20:39Z started; saturation per R44; candidate pool = ideas_29sep v_0..v_15 (0 recheck hits for IB29/MD/MM), combo_oracle (0 hits).
- 18:2xZ RC-A pick = ideas_29sep/v_10.json (I-175 A/edge weights 'not independent axes: argmin depends only on S=A+Dis and Div-A'). Verified in tracksdata 0.1.0rc9 solvers/_ilp_solver.py l.296-323: in-flow appear+in_edges = node(+merge), out-flow disappear+out_edges = node+division, node_weight default 0 (exp89t cell 4 ILPSolver call sets only edge/app/disapp/div). => #app = n-E, #dis = n-E+#div, cost = (A+Dis)(n-E) + (Dis+Div)#div - sum p. Params: exp70g A0 Dis2 Div1.2 -> S2 T3.2; K (Div0.4) S2 T2.4; K+DIS2.25 (exp89s/exp89t) S2.25 T2.65. Fork-vs-new-start margin = T-S = Div-A (0.4, DIS-invariant); fork-vs-drop-chain margin = T (DIS reverts 0.25/0.8 = 31% of K's T drop).
- ILP -> output channels (exp89t cell 7 filter_output_graph l.1937-1975): ILP forks are NOT output (motion relink replaces raw edges, 1:1 single-parent/child repair l.1978-1998; output forks come from safe divisions l.2017 + DaughterNet insertion). ILP reaches output via node set (+readmit) and learned_edge_probs bonus (l.1954-1966).
- dummy-lab run: scratchpad r45/dis_k.py on _dl exp70g/exp85a/exp89s/exp87a/exp89t (background).
- 18:2xZ dummy-lab (scratchpad r45/dis_k.py; overlap_lab.eval_clip, 4 train clips): nodes/edges/forks/TP/FP/FN
  exp70g 121,252/117,083/81/2047/101/80; exp85a K 122,328/118,137/85/2049/99/78; exp89s K+DIS 121,389/117,246/84/2049/99/78;
  exp87a K+CI 122,328/118,137/85/2045/107/82; exp89t K+DIS+CI 121,389/117,246/84/2045/106/82. Div TP 0 everywhere (3 GT div FN on 6bba_05db).
  => K->K+DIS: annotated TP/FP/FN identical; adj change = node multiplier only (e.g. 44b6_0b24 1.0385 -> 1.04015).
- exp85b/85c decomposition (CONTEXT l.3485-3490): DIV 0.4 alone +49 nodes/+3 forks; READMIT 0.94 alone +1,022 nodes.
- Node identity (r45/dis_overlap2.py, same-frame match <= 1 um): K-new vs exp70g 2,107; K nodes gone in K+DIS 1,812, of which K-new 338 (19%);
  K+DIS new vs K 873; K+DIS vs exp70g +2,524/-2,387. => DIS's -939 net offsets READMIT's +1,076 in COUNT only; not a K-undo by identity.
- GT proximity (r45/dis_gt.py, <= 7 um of a GT node, same frame): DIS-removed 1,812 -> 4 near GT vs 28.3 expected at the K base rate
  (per clip: 44b6_0113 0/0.2, 44b6_0b24 0/2.2, 6bba_05b6 0/4.9, 6bba_05db 4/21.1); DIS-added 873 -> 1 near GT. ~7x depletion.
- Caveats: exp88a (DIS on exp70g) dummy -0.0008 (1 TP, 2 FP) per R26-RC-A; old exp13 48-video lab parabola -0.0007 at S 2.25; 4 dummy clips ~6bba-only (R44-RC-C).
- poll.log: 56669888 still PENDING at 18:15:19Z and 18:25:22Z headers (L > 9.42 h).
- RC-B = ideas_29sep v_8 (I-384 N1 extrapolation): premise 'exp89p reads +' falsified by probe 54 (0.956 vs exp85a 0.958, CONTEXT l.4394).
- RC-C = ideas_29sep v_4 + knobarms_28sep v_1 (FLOW_Z_WEIGHT): only 0.6 / 1.5 judged; v_4's own analysis puts optimum ~0.8-0.88 (never an arm).
- 2026-09-29T18:29:49Z final JSON written (4 findings).
