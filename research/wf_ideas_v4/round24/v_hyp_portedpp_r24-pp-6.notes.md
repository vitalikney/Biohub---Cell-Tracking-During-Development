# v_hyp_portedpp R24-PP-6 notes (2026-09-28T07:02:50Z)
- no prior v_*.json; source finding scan_hyp_portedpp.json l.47 (R24-PP-6)
- verified x138 cell 5 (experiments/ext_x138/biohub-x138.ipynb) l.1943-1951: motion_edges = motion_relink_edges(nodes, stats, learned_edge_probs); 'if motion_edges: edges = motion_edges' -> ILP edges replaced; ILP keys only in learned_edge_probs (bonus)
- CONTEXT l.3485-3491 (06:26Z): exp85b (ILP 0.4 on exp70g) +49 nodes (+0.04%), forks 84 vs 81, lowrefine unchanged -> ILP knob near-inert on our base
- IDEAS.md I-049: ILP fork precision at 1.2 = 36/241 = 0.149, at 0.6 = 24/127 = 0.19 (exp12, in-sample, exp03B pipeline, pre-patch metric); break-even q* = 0.161 post-insertion; no replay bed (exp60 edge_cache 0 ILP edges)
- LB reads for the same channel class (division adds): probes 43/44 DC 0.20/0.225 = 0.954 flat; probe 45 cap 6 = 0.956 (the insertion already owns the 'parent with one child + in-degree-0 start' niche); probe 41 DC 0.30 = 0.949
- verdict: refuted as a build for 28-29 Sep. Same output niche as DaughterNet insertion (competes for the same cap 6 / same parents), source precision ~0.15-0.19 vs q* 0.161 = within noise of break-even, no lab, no counter; forks are a tiny share of the metric; EV ~0.
- 2026-09-28T07:03:53Z wrote v_hyp_portedpp_r24-pp-6.json (refuted=true)
