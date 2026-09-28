# v_hyp_private_r25p-6 notes (started 2026-09-28T10:35:13Z)
- no prior JSON answer; read scan_hyp_private.notes.md (mc25 description)
- 2026-09-28 ~10:45Z read: CONTEXT.md 3560-3708 (09:35Z probe 48 = 0.957 C+, 10:16Z private-hedge proposal exp75, 10:19Z user answers); scan_hyp_private.json R25P-1..10; round23 scan_hyp_finals_29sep.notes.md (mc23 P13 {exp79a,#37} .69/.41 at CI +2e-4); ci_zshift_out.json (clip 44b6_c50204e0: CI a0.5 J 0.86047 -> 0.8576, i.e. lab CI can be negative per clip).
- Code: scratchpad r25/mc25.py imports r21/mc20.py unchanged. B vs A differ ONLY in whether the 2nd file carries CI; rival field does not enter the sign. C term (mc20, written 27 Sep 20:00Z, BEFORE probes 47/49) has mean +0.00041, sd 0.00225, P(C<0)=0.51 -> not updated for the cap ladder reads (cap 8 0.955, cap 12 '-').
- Reproduced base seed 11: A .705/.447, B .762/.511, C .618/.439 (exact match).
- SENSITIVITY (mine, seed 11, base / qpub0), bronze/silver:
  CI N(.0003,.0010): A .691/.427 B .709/.478 | qpub0 A .618/.303 B .646/.376
  CI N(.0002,.0012): A .688/.422 B .681/.468 | qpub0 A .617/.304 B .614/.368   -> bronze flips at mean +.0002 when sd .0012
  CI N(.0001,.0012): A .680/.412 B .661/.449
  CI N(.0005,.0015): A .717/.467 B .720/.532 | qpub0 A .651/.354 B .663/.447  -> bronze edge +.003 only (vs +.057 at sd .0008)
  CI N(0,.0015):     A .679/.411 B .634/.445
  CMODE norm C N(.0003,.0012) CI base: A .754/.446 B .774/.486 C .705/.447 (base); central A .656 B .689 C .627 -> order B>A>C survives a lower cap mean.
- CONCLUSION: the bronze crossover is NOT a single mean threshold: +.0001 at sd .0009 (the finding's own cross run used sd .0009, not the base .0008), ~+.00025 at sd .0012, ~+.0005 at sd .0015. The 7 'scenarios' vary field/q only, never CI; 'B > A > C in all 7' is robustness to non-deciding terms. Silver B-A stays positive in every run incl. CI mean 0 (+.03). Bronze is a coin-flip at honest CI widths.
