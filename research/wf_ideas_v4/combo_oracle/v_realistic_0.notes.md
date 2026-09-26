# v_realistic_0 notes (skeptic: code & metric parity)
- 2026-09-26 22:0xZ start; v_realistic_0.json did not exist.
- read combo_arms.py: ev() == tools/trainlab.official_eval (same rounding, same counts; only lacks empty-graph guard); F forkmid == tl.forkmid; realistic apply_spec never receives GT path; pooling = official summarise (same as results.md). Agg reproduces: base 0.93988 div 25/31/74; best3 +0.00039; oracle FLD +0.01353.
- cross-check vs results.md: ins35_forkmid45 6bba/ALL 0.9429 vs ins35 0.9427 (+0.0002), div 23/22/65 vs 23/23/65 -> matches F_forkmid_4.5 (+0.00021 6bba, 25/30/74 pooled).
- launched scratchpad/combo/v_real0/vcheck.py (independent L/O rewrite, tl.forkmid, tl.official_eval; 5 workers)
- 22:0xZ vcheck DONE (scratchpad/combo/v_real0/vcheck_out.json): my L/O rewrite + tl.forkmid give IDENTICAL edge sets to apply_spec on all 56 clips x 5 arms; scored with tl.official_eval + summarise: base 0.93988 (44b6 0.9165, 6bba 0.9427 = results.md ins35 rows), div 25/31/74; F45 +0.00017, O10 +0.00020, L8 +0.00002, best3 +0.00039 (44b6 0, 6bba +0.00041, W/L 3/2), mid3 -0.00038 (44b6 -0.00250, W/L 5/9). All match m_realistic exactly.
- vorac.py: oracle_F author rule +0.00629 (W/L 15/5: it sometimes drops the TP child edge); GT-best drop (non-TP child edge) +0.00671 (W/L 20/0). Ceilings slightly conservative; does not change the answer.
- verdict: not refuted.
