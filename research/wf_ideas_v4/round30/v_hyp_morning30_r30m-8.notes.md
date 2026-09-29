# R30M-8 skeptic notes (2026-09-29T01:29:40Z)
- (a) CONTEXT l.3946 A-M2 row names only Rr '+'; l.3938 defines Rr with a '+' tier only; l.3739 (R25-A1 (4)) '0u counts as + for BEST_CI only'; l.4147-4150 precedence. GAP RULE v2 (5) l.4017 is gap handling only. OK.
- (b) l.4156: 51 L in (9.30, 9.48] h, not UNPROVEN-ins. OK.
- (c) NIT: tools/runtime_ledger.py l.42/l.210: L_hi = header + 210 s x failed attempts - submit. exp89p submit 00:46:36Z (ledger row l.20). Header 08:40:00Z -> 7.890 h; +2 failed attempts -> 8.007 h > 8.0 -> ledger says 'insertion gate 8.0 h: UNPROVEN' ('v' suffix). Headers drift ~2 s/10 min (01:23:59Z latest), so the last header before 08:45Z is ~08:34-08:35Z -> 7.81 h, needs >= 3 fails. Consequence nil: 'v' (l.3021-3023) only affects cap/threshold line, P code (l.3937) has no 'v' clause, and l.3588 'cap-family display >= 0.956 reads as insertion-ran'.
- (d) l.4230-4235 40-min spacing non-CI; M1 exp89l CI. OK. (e) 00:46Z log '2 submissions remaining today'. OK. (f) l.3936, l.4193-4195 KEY = stack submitted. OK.
- (g) NIT: tie order l.3181 'last attributable UP'; a k>=1 read that is MASKED/BLIND (count moves by 2, l.3733-3734) is not attributable -> exp87a stays. Wording 'k >= 1' should be 'attributable UP'. No action change.
- Verdict: not refuted; info only, gain 0.
