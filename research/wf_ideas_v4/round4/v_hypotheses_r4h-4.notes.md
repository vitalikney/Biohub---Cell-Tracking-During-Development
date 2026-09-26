# R4H-4 skeptic notes (value + feasibility), 2026-09-26 ~01:00 UTC
- 00:57Z: no prior v_hypotheses_r4h-4.json; K2 56563521 / twin 56563534 PENDING (scan_hypotheses.notes l.13, poll 00:43Z). Pre-score.
- READ TABLE = CONTEXT.md l.1978-2005 (commit 1017c41). Rows checked one by one:
  row1 K2 ERROR; row2 twin-K2>=+0.002; row3 d1>=-0.001 (covers twin ERROR -> exp52); row4 d1<=-0.002 clean (covers twin<0.953 -> exp52);
  row5 d1<=-0.002 not clean -> branches only on d2. Twin ERROR/unscored => d2 undefined => NO row matches. (a) is a REAL gap.
  P(joint) ~ P(K2<=0.952) 0.05-0.1 x P(not clean) ~0.3 x P(twin ERROR) ~0.02-0.05 => ~0.0005-0.0015.
- (a) proposed text F1=K2, F2=exp52: consistent with row 5 logic (no clean d1, no d2 => no evidence to remove lowrefine; default stack kept),
  and F2=exp52 is the f2 fallback. Note it is a table-internal default, not literal R3 (R3 alone would drop lowrefine at -0.002;
  the 'clean' clause is the table's). A scored K2 has its private already computed -> no runtime risk to F1.
  Missing piece: K1 [OK] should stay available as in row 4/5 (K1 = scored proxy of #35, 0.954) - the user may prefer it.
- (b) DUPLICATE: row-2 OK and 0.952 floor OK are already R3-A9 items (2) and (3) (round3/report.json) and KNOWLEDGE/WATCHLIST.md W21.
  Only nit: CONTEXT RESUME POINT l.2023 'Pending user OKs' lists L1/L2, K1, floor 0.952 but not the row-2 F2=K2 OK -> add 3 words.
- (c) true but near-moot: K2/twin submitted 6 s apart, twin runs ~0.5 h shorter (dummy 1,038 s vs 1,512 s), so twin normally scores first.
  Nothing irreversible happens before 29 Sep except a K1 submit, which needs the user's OK anyway. Harmless procedural line.
- Companion gap found (not in finding): row 1 without OK -> §f fallback: K1 not submitted, #35 barred (L35 unprovable), -> F1 = #34 byte copy
  even if the twin is scored >= 0.953. R3-A9 item (4) (F1 = twin instead of #34) covers only 'lowrefine leaves F1', not K2 ERROR.
- Value on private: ~0 expected score; it is rule hygiene that prevents an ad-hoc post-score choice (R7/pre-reg integrity). Feasibility: one CONTEXT line, pre-score, no build.
