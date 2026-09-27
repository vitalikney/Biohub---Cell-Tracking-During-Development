# v_plancheck_pc19-02 notes (2026-09-27T18:12:54Z)
- 18:13Z: no prior JSON for this task. Sources: CONTEXT.md l.3037-3045 (R18 branch table: rows only for 46 in P5/U4/N4/MASKED/NEG/ERR; no PENDING row), round18/report.json (46-read timer 22:45Z, re-arm 30 min, hard edge 00:00Z, but no action defined if still PENDING).
- poll.log header 18:04:40Z: 45 56606948 PENDING (L > 6.82 h), 46 56611472 PENDING (L > 3.46 h). 46 9.0 h mark 23:36:59Z; 23:45Z cutoff = L 9.13 h.
- Hidden L of K2 family (ledger.md): 37 (7.36,7.54], 42 exp70b (7.41,7.58], 43/44 (7.56/7.57,7.74], 40 exp70a (6.87,7.04], 39 exp70e (7.24,7.42]. Max 7.74 h.
- Dummy runtime is a poor predictor of hidden L: exp70b dummy ~1,740 s (+15% vs K2 1,512 s, CONTEXT l.2624) but hidden L = K2's; exp70e dummy 1,629 s -> 7.24-7.42 h; exp70a 1,464 s -> 6.87-7.04 h; exp76d 1,402 s. So the '+24% dummy' premise is weak; P(46 L > 9.13 h) is small (~5-10%, mostly Kaggle-side delay).
- Still: the gap is real (undefined branch -> post-hoc choice at 23:45Z), and the fix is one pre-score line, no mechanism, no R1-R10 issue. The proposed mapping only reuses existing rows (45 P5/U4 -> exp76e,a,d; else exp76a,d + held slot 3), consistent with the table's conservative default.
- Refinement: the 45 read (cap 6 alone, expected ~18:30-19:00Z) gives a direct runtime check of the insertion-cap change; log it with the line.
- 2026-09-27T18:14:34Z: final JSON written (refuted=false, procedural fix, premise corrected).
