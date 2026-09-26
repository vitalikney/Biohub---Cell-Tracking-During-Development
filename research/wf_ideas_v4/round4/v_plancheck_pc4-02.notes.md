# v_plancheck_pc4-02 notes — started 2026-09-26T00:57:33Z
- read CONTEXT.md l.1900-2042 (READ TABLE 23:12, RESUME 00:02); scan_plancheck.notes.md (origin of PC4-02).
- 00:58Z poll.log: #37 K2 56563521 and #38 twin 56563534 still PENDING -> an addendum written now is pre-score.
- CONTEXT l.1993-1994 row 2: F2 = K2 if d1>=-0.001 [OK], else K1 if submitted and scored [OK], else exp52. Rows 1/4/5 are the only ones that submit K1; first-match means row 4 never runs when row 2 matches -> hole confirmed textually.
- Arithmetic: row 2 with d1>=-0.001 needs K2>=0.953 AND twin>=0.955 (d2>=+0.002). So most row-2 worlds (K2 0.952/twin 0.954, K2 0.951/twin 0.953) ARE the hole case -> the hole covers the bulk of row 2, not a corner.
- #35 cannot stand in for K1: R5 admits ungated insertion only if L35<=7.5 h; L35 in (6.72,7.73] h unproven (l.1655-1657, §f item 3).
- K1 = exp58t v1: dummy gates PASS 17:20Z (K1 sha == exp57b dummy ef0eff86..., l.1818-1820); kernel COMPLETE (scan notes 00:55Z). No build/GPU needed; hidden rerun does not use weekly quota (l.1971-1972). 3 slots left 26 Sep.
- Rules: K1 at d1<=-0.002 is not barred ('Never: K1 at d1=-0.001' only); twin vs K1 differ in 2 components -> not identical; R8 n/a (no new mechanism); R7 0.001-pick n/a (hedge, not pick). Consistent with row 4 (d1<=-0.002 -> K1 [OK]) and R3 (lowrefine removed at -0.002 in the insertion stack).
- Minor extra gap: row 2 sets F1 = twin with no >=0.953 floor (e.g. K2 0.950 / twin 0.952); suggest F1 = K1 if twin < 0.953 and K1 >= 0.953.
- Verdict: NOT refuted; cheap, pre-score, OK-gated.
