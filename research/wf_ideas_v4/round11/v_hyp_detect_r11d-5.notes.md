# v_hyp_detect r11d-5 notes (2026-09-26)
- 2026-09-26 ~18:xx UTC: no prior answer file; starting.
- Evidence file lives in session scratchpad (not repo): C:/Users/vital/AppData/Local/Temp/claude/.../scratchpad/r11/r11_detect_out.json -> non-durable; curator must copy numbers, not path.
- Numbers (6bba): miss_img_n 595; miss_pk_le5 186 (31%) vs ctl 4444/6388 (70%); BUT miss_val_ge_thr 431/595 = 72% vs ctl 5551/6388 = 87% -> missing nodes are mostly NOT dim, they are peakless in bright regions (crowding / merged maxima). run5+ pk_le5 33/159 = 21%; run2-4 115/310 = 37%.
- 44b6: only 7 missing nodes (of 668 total) -> residual is 6bba-specific; private = other embryos.
- Duplicate check: IDEAS I-113 = "B7 nnPU / ignore-unlabelled detection loss" deferred-after-deadline since 2026-09-06 (CONTEXT l.140, l.216, l.489). I-261 is axial z-localisation (different mechanism). "head retrain" closed pre-deadline (CONTEXT l.1488 kill test FAIL).
- Verdict: refuted as a new hypothesis (dup of I-113, mechanism mismatch dim vs peakless-bright, zero pre-deadline value); the curator note is harmless if refiled under I-113 with corrected wording.
