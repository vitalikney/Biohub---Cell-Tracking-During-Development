# v_hypotheses_r2s-2 notes (skeptic VALUE+FEASIBILITY)
- 2026-09-25T20:23:02Z start; no prior json found.
- 20:24Z context read: CONTEXT l.1600-1940, scan_hypotheses.notes.md, results_forkblob.md (forkblob FAIL: control div TP/FP/FN 16/25/83, J 0.129 -> break-even FP:TP ~ 1/J ~ 7.7 in lab, not 3). Running scratch antipar_lab.py (rule exactly as in R2S-2, cos>0.25 preset) on 56 exp60 dumps with official scoring.
- 23:30Z RESULT (scratch antipar_lab.py in the session scratchpad; the R2S-2 rule copied from trainlab.forkmid with cos>0.25 on the FINAL coords and forkmid's drop convention; official scoring via tl.official_eval; 56/56 exp60 clips; 293 s on 8 workers; no threshold tuning):
  - eligible safe forks 676, flagged 113 (16.7%, matches the finding's dose); flagged division labels: TP 1, FP 4, ignored 108; dropped sides: added 96, ilp 17; nodes unchanged on every clip.
  - POOLED: div TP/FP/FN 16/25/83 -> 15/21/84; div_J 0.1290 -> 0.1250 (-0.0040); adj_edge +0.000064; score -0.00034.
    44b6 +0.00056 (div_J +0.0029); 6bba -0.00051 (div_J -0.0056); SELECTION -0.00123; CONFIRMATION +0.00058.
  - forkmid45 + antipar25 == antipar25 exactly (forkmid's only removed evaluable fork, an FP at 6bba_cdcfe533 mid 4.96, is inside the cos cell). forkmid45 alone: div 16/24/83, score +0.00013.
  - Proposed gate: TP<=1 ok; FP>=3TP ok (4>=3); FP>=2 ok; pooled div_J>=control FAILS (0.1250 < 0.1290) -> gate FAIL, same failure mode as forkblob (L4) at 20:04Z.
  - The vetoed TP: 6bba_7f87b3d8 parent 4406 (SELECTION), cos 0.976, mid 3.65, sister 4.64 -> removed the added edge 4406->4504. Any cos threshold in (0.08, 0.976) vetoes it -> no threshold of this rule avoids the TP; the failure is not a knob choice.
  - Lab evaluable cos: TP 16 forks -> 2 with cos>0 (12.5%), 1 with cos>0.25 (6.3%); FP 25 -> 5 with cos>0 (20%), 4 with cos>0.25 (16%). Enrichment FP/TP ~2.6x, far below what is needed.
  - Break-even arithmetic: removing a TP fork turns it into an FN (J drops by 1/N), removing an FP gains J/N -> break-even FP:TP = 1/J = 7.75 at lab J 0.129 (3.0 at the assumed public J 0.33). The finding's gate clause 'FP >= 3*TP' and its value arithmetic use the public J; on the lab the needed purity is q_break = J/(1+J) = 0.114, and even on the finding's own public assumption 4:1 is only 0.2 vs 0.25 break-even q -> marginal at best.
- 20:30Z verdict REFUTED written to v_hypotheses_r2s-2.json
