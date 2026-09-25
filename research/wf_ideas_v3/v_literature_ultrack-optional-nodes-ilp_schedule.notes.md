# schedule skeptic notes: ultrack-optional-nodes-ilp
- 2026-09-25 start: no prior schedule json; read BRIEF.md
- tracksdata 0.1.0rc9 wheel (pip download; the version cited in wf_ideas_v2 notes as Kaggle site-packages) HAS ILPSolver(node_weight=..., timeout=...) l.134-159; overlap constraints l.330/403. Implementable. Kaggle version still to be confirmed in-kernel.
- x138 (exp56 notebook cell 4): edges are produced INSIDE predict_video (edge transformer) from coords; ILP in predict script subprocess (patched solver block ~l.1314-1351 of extracted src). So hypotheses must be inserted at the `arr = _detect_cells_pooled(...)` line, which is ALSO the anchor of readmit's lowdet patch and the V1284 head patch (known anchor collision incident, notebook l.1610-1616). Fragile.
- _detect_cells_pooled = max_pool3d local max > threshold; low peaks at 0.3 are a superset; free = s<0.965 peaks; separated from standard by pool window. Claim OK.
- No free-pool counts (0.5..0.965) or per-video ILP timings exist in repo; exp56 log lines 'ILP Xs | candidate nodes=' would give them (Kaggle Logs tab -> browser_todo).
- Sibling schedule verdict (byte-lowscore-extension): no x138-on-train lab harness exists; friend A inactive since 24 Sep; vitalii GPU 0 until 26 Sep 00:00; x138 ~3.5-4.5 min/video.
