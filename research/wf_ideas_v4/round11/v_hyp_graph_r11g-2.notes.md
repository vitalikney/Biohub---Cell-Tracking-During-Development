# v_hyp_graph r11g-2 notes (2026-09-26T17:16:00Z)
- 17:5xZ read scan_hyp_graph.json r11g-1/r11g-2; IDEAS.md I-056 (AUC 0.73 single feature, old base, ranker power never measured), I-076 (prec 4-15%), I-079 (post-deadline item 6).
- Re-aggregated scratchpad r11_graph_arms_out.json (56 clips, arms[*]['row']): base div 25/31/74 (J 0.1923); orph_mirror 32/231/67; orph_near 42/729/57; oracle_fp 25/0/74 (J 0.2525). Matches the scan.
- Ceiling arithmetic (score = adjEdgeJ + 0.1*divJ, pooled div counts; edge side ignored, ~17 extra TP edges of 40k = negligible):
  gated pool 7 TP: perfect +0.0054; 50% prec +0.0041. CONFIRMED below bar at oracle.
  wide pool 17 TP: perfect +0.0131; 90% +0.0126; 80% +0.0121; 70% +0.0114; 50% +0.0093; 30% +0.0055; 15% -0.0007.
  => CLAIM ERROR: '+0.012 needs precision >= ~50%' is wrong. Needs >= ~79% at full recall (17/17), >= ~93% at 16/17, impossible at <= 15 TP kept. From a 2.4% base that is ~33x precision / ~150x odds enrichment; AUC 0.73 cues cannot do it.
- Pool is 6bba-dominated (44b6 clips add ~0 TP in orph_near); hidden embryos unknown -> value even lower.
- Feasibility: R8 27 Sep 12:00Z; needs raw zarr crops, half-day code, dummy, new user OK -> no. Conclusion 'do not build, post-deadline via learned model' stands.
- 2026-09-26T17:17:43Z wrote v_hyp_graph_r11g-2.json (refuted=false, precision-threshold correction)
