# v_hyp_graph r11g-1 skeptic notes (2026-09-26)
- ~20:15Z no prior v_hyp_graph_r11g-1.json; started fresh.
- Read scratchpad r11_graph_arms.py (orphan_attach mirror/near + oracle_fp), .log, _out.json (56 clips).
- Recomputed from _out.json: div TP/FP/FN base 25/31/74, mirror 32/231/67, near 42/729/57, oracle_fp 25/0/74 -> matches claim exactly.
- Recomputed tools/trainlab.summarise_rows score: all base 0.93988, mirror 0.92702 (-0.01286), near 0.91263 (-0.02725), oracle_fp 0.94617 (+0.0063); 44b6 -0.01215 / 6bba -0.01305 -> matches claim.
- Old closure: research/KNOWLEDGE/IDEAS.md I-047 (honest 1 TP / 31 FP). New number is same direction on x138.
- Skeptic check on "maybe a tighter gate helps": 7-TP mirror pool, perfect precision would give <= +0.0054 lab (scan_hyp_graph (2)), below ~+0.012 lab bar and past R8 anyway. No route to a submittable mechanism. Finding (a negative result, info only) stands.
