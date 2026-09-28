# v_hyp_freezetext R29F-8 notes
- 2026-09-28T20:38Z start; no prior json
- Parsed _dl/<kernel>/<kernel>.log read-only (grep on "time" JSON fields):
  - exp89r: mode=candidate 485.773193 s, GPU shard 0 485.773239 s (diff 46 us); last time 1959.214 -> compute 1473.4 s both anchors.
  - exp87a: 300.460810 / 300.460862; last 1869.782 -> 1569.3 s.
  - exp89q: 519.466256 / 519.466300; last 1576.199 -> 1056.7 s.
- CONTEXT l.4021-4028 (16:26Z, GPU shard 0 anchor) and l.4104-4110 (20:18Z RULE v2.1, mode=candidate anchor + 're-measure if GPU shard 0 used') -> the re-measure clause is vacuous: same number.
- Duplicate: round29/scan_plancheck.json (same finding, 6 logs incl. exp89p 1,059, exp85a 1,126, exp89s 1,129). Merge, not new.
- Caveat: holds for exp89l only if its cell-4 print order is unchanged (same builder template; SEC/coordinject patches do not touch that print). Check the two timestamps once when reading the exp89l log (1 grep). 0 GPU, 0 API, 0 LB value.
- Verdict: NOT refuted (info only).
