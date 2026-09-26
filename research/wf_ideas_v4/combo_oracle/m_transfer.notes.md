# m_transfer notes
- 2026-09-26: started; m_transfer.json absent -> fresh run. Created combo_oracle/ and scratchpad/combo/.
- 18:12Z read r11_graph_arms.py/out.json, scan_hyp_graph notes, v_hyp_graph_r11g-2/-4, LESSONS_draft transfer table (l.11-26), IDEAS I-047/I-056/I-076/I-079/I-164/I-200. Metric: score = w-avg adjEdgeJ (w=TP+FP+FN per clip) + 0.1*micro divJ (pooled counts) -> div term is pooled, edge term weighted. Train embryos: 44b6 142, 6bba 256 geff files. Parallel agent m_joint_oracle is measuring the joint oracle (not duplicated here).
- 18:20Z ran scratchpad/combo/m_transfer_arith.py (re-aggregates r11_graph_arms_out.json per-clip official rows; no graph runs; <1 min, 1 process) -> m_transfer_arith_out.json/.log.
  * base ALL 0.93988, div 25/31/74, edge 38397/1684/1696 (W=41,777; one edge flip ~2.4e-5; one div TP at base ~7.7e-4).
  * O_FP measured +0.00629 = div +0.00602 (25/99 vs 25/130) + edge +0.00027 (31 child edges dropped: 22 FP edges, 9 TP edges). 44b6 +0.00695, 6bba +0.00577 (per-embryo pooled; not additive).
  * attach7 perfect: div +0.00538 exactly (32/130); edge +0 .. +0.00017 (if each recovered div adds 1 GT edge) -> +0.0054..+0.0055; all 7 TP in 6bba (44b6 +0).
  * attach17 perfect: +0.01348 (div +0.01308).
  * link ceiling (136 dangling FN->TP, pro rata): +0.00324.
  * JOINT O_FP+attach7 = +0.01353 (div 32/0/67 = 0.323, +0.01309 div; superadditive by +0.00169 vs the sum 0.00602+0.00538 because both shrink the Jaccard denominator). + link = +0.01677 (44b6 +0.0118, 6bba +0.0170). O_FP+attach17(+link) = +0.02387 (+0.02711).
- 18:22Z classifier model (equal-variance binormal ROC, best threshold, 31 FP/25 TP forks, 7/200 and 17/698 attach pools): AUC 0.73 -> joint +0.00025 lab; 0.80 -> +0.0010..0.0012; 0.90 -> +0.0036..0.0051; 0.95 -> +0.0061..0.0092; 70% of the joint div oracle needs AUC ~0.99. Marginal fork-removal break-even = 84% FP among removed (D/(D+T)=130/155); add break-even q*=0.161. With PERFECT removal, attach needs >=33% precision (<=13 FP for 7 TP) or >=46% (<=19 FP for 17 TP) for 70%. With perfect attach7, removal needs >=18/31 FP forks at 0 TP lost (21 at 1, 25 at 2, 28 at 3).
- 18:24Z m_transfer_vis.py: public = lab x 1/6; 3-dec display, K2 unrounded position uniform in its bin. Joint7+link oracle -> +0.0028 public (P(+0.002 shown)=1.0); 70% -> +0.0020 (0.96); 50% -> +0.0014 (+0.001 sure, +0.002 0.40); 30% -> +0.0008 (+0.001 0.84); 10% -> +0.0003 (0.28). Wilson90: 8/17 -> 0.29-0.66; 20/25 -> 0.64-0.90.
- 18:16Z wrote m_transfer.json (complete) via scratchpad/combo/write_m_transfer.py.
