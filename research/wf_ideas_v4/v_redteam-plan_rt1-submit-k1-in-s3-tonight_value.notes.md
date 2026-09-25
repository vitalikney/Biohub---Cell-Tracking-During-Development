# RT1 value notes (2026-09-25T17:46:29Z)
- Sources read: CONTEXT.md L1795-1836 (16:20 #35 0.954, L35 (6.72,7.73] h; 16:45 step 0; 17:20 gates 16/16; 17:45 FF),
  research/wf_ideas_v3/FINAL_REPORT.md §e (slots S1-S21, R1-R10) and §f (F1/F2, fallback list), experiments/runtime_step0/step0.md,
  experiments/lb_poll/poll.log (public scores only at 3 decimals: 0.953 / 0.954), memory project-metric-insights (score = adj_edge_J + 0.1*div_J).
- Metric ceiling: K1 vs K2 differ only by lowrefine (final nodes +0.004% / +0.118% / 0 / +0.013% per dummy clip; readmit 1,365 vs 1,337).
  Positions of low-detection readmitted nodes only; edge-J effect bounded well below 0.001; LB rounds to 3 decimals,
  so K2 0.953 vs K1 0.954 can be a true gap of ~0.0001. No private transfer from choosing by it.
- Rule check: if K2 = 0.953, R3 keeps lowrefine (>= stack - 0.001) and §f says a simpler file replaces F1 only at >= +0.002;
  R7 forbids choosing between near-copies by 0.001. So a scored K1 = 0.954 does NOT change finals in that world unless the
  pre-registration is broken. The +0.0001 (0.12 x 0.001) of the claimed EV relies on that break.
- K2-error world (P~0.025): K1 shares everything except lowrefine (fail-soft, 'LOWREFINE FAILED' path). Failure modes
  (12 h limit, insertion crash, env) are shared -> P(K2 error AND K1 ok) ~0.01. And K1 can be submitted reactively on 26 Sep
  after K2's result (~08:00) and scored by ~17:00 26 Sep; slots S10-S11, S15-S16, S18-S21 unused -> the "hole" is covered
  with 3 days of margin. Tonight's submit only moves certainty ~8 h earlier.
- Attribution K1 vs #35: byte-identical unless x138's 7.5 h deadline fired; step0 says at most the last few of ~100 clips;
  their insertion share (~12 forks total for +0.001) -> expected effect <= ~0.0001, invisible at 3 decimals. Power ~0.
- Latency sample (c): K2's own latency is measured anyway and K1 runtime <= K2; adds little.
- Verdict: private gain ~0 (<0.0001); harmless and cheap, but not a value gain. REFUTED on value lens.
