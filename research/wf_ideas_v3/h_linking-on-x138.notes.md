# h_linking-on-x138 notes
- 2026-09-25 ~11:00 UTC: started; no prior json. Read BRIEF.md.
- 11:15 read DIFF.md, edge_anatomy (anatomy_exp39.md, fn_anatomy_exp39.md, l6_fn_anatomy_report.md), v2 FINAL_REPORT, survey_linking_divisions.md, x138 cell 5 (motion_relink_edges L519-742, filter_output_graph L1843-2066, linefit L1769).
- FACT: in x138 the ILP edge set is REPLACED by the per-frame flow-prior Hungarian (cell5 L1947-1952 `edges = motion_edges`); ILP only chooses nodes + supplies prob bonus (bonus 1.0, only for ILP-solution edges; others prob 0). No no-link cost: any pair inside the gate is forced. One-to-one => forks only from safe divisions.
- FACT: low-detection pool (readmit + gapfill) is dumped UNREFINED at the (1,4,4) grid (cell4 'lowdet peaks' patch: `_detect_cells_pooled(..., 0.3)` -> int16), i.e. readmitted/gap-filled nodes miss the V1284 head. exp57 diag: 1,337 readmitted nodes on 4 dummy clips (CONTEXT.md L1515).
- FACT: linefit weight 0.8, window 2 (cell2 defaults) - tuned on the int-grid base; a_linefit 354 FN on exp39 (l6 report).
- Ceilings (exp39 lab, fn_anatomy_exp39.md): b_break +0.0011, b_v_taken +0.0099, b_u_diverted +0.0095, b_swap +0.0457 (but swaps = localisation per l6 sec.3; swapfix gate FAIL).
