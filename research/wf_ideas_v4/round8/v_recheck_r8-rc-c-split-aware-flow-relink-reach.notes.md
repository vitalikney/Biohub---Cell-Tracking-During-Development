# v_recheck R8-RC-C split-aware flow relink reach - notes
- 2026-09-26T10:36:15Z start; no prior json found
- Recomputed from scratchpad r8_divreach_out.json (56 exp60 clips): 99 GT divisions = steal 35 + orphan 27 + one-daughter-unmatched 21 + TP_fork 12 + neither 2 + parent_unmatched 2. 62 detected-unforked confirmed. Far step median 9.88 um, q75 11.12; near median 1.82 um. Far <= 7 um: 8/62; far 8-12 um: 33/62.
- Gate proxy in r8_divreach.py = sister 5-14 um AND max step <= 7 um -> steal 2 + orphan 5 = 7 (no 2 um min-step, no cos <= -0.25 gate, so 7 is an UPPER bound on reach).
- 88/99 GT divisions are 6bba (44b6: 11) -> reach stats are basically one embryo.
- exp60 results.json: control 6bba TP/FP/FN 15/17/73, ins35 23/23/65 (claim OK); 44b6 1/8/10 -> 2/8/9. Pooled control J = 16/(16+25+83) = 0.129 -> break-even J/(1+J) = 0.114 (claim OK). Old premise 0.265 at CONTEXT l.1321.
- Old verdict: research/wf_ideas_v3/v_linking-on-x138_split-aware-flow-relink_value.json (refuted; also flow-compensated midpoints worse in div_audit9; velocity picks true child 0/381 on contested links, forum 740573). These refutation reasons do not depend on the 0.265 premise and still stand.
- Verdict: finding CONFIRMED (not refuted). Closure for finals is right (R8 deadline 27 Sep 12:00, no code, no gate bed, needs NEW OK, would compete with K2 insertion for the same pool). Minor caveats only.
