# PC31-01 verify notes (2026-09-29T02:30:04Z)
- 02:31Z: read round30/report.json actionable[1] (R30-A2): the A-M2 bullet literally says "DIS '?' -> exp89q only if P is '+' or '?'"; the Rr '+' bullet only defines Rr. Confirmed.
- CONTEXT l.3931-3960 MORNING TABLE v1.1 (2) branch A M2: "DIS '+' -> exp89s; else Rr '+' -> exp89q; else UNUSED". Branch-A DIS: dd=(R-P)-(87a-85a=0.001); '+' dd>=0.002 & R>max(0.959,P) => R-P>=0.003; '-' dd<=-0.002 => R-P<=-0.001. Matches the finding's definitions.
- CONTEXT 21:11Z (6) (l.4147): "Rr '+' with DIS '?' -> exp89q; DIS '-' -> UNUSED". 02:02Z (3): same, and (5) points the 07:23Z prep to R30-A2 grid.
- Cell (i) d_R=d_P=0.959: DIS '?' (R-P=0, R not > 0.959), P '+', Rr not '+' (needs >=0.960) -> v1.1 UNUSED, literal bullet exp89q. Real and plausible (87a K+CI 0.959, 85a K 0.958).
- Cells ii-iv also check out. R30-A2 grids (d_R 0.960/0.961) are right, only the bullet is wrong.
- Poll header 02:14:07Z shows all 3 night refs PENDING (round31 scan_plancheck) -> still pre-score. No CONTEXT entry after 02:02Z fixes it.
- P clarification (late COMPLETE read counts at A-M2): consistent with v1.1 code '?' = ERROR or not terminal; pre-score; SEC-conservative. Suggest adding 'GAP RULE v2 still applies to P' (exp89p 10.2 h mark = 10:58:36Z) so the clause does not silently override it.
- Verdict: NOT refuted. Text-only, 0 Kaggle, 0 GPU.
