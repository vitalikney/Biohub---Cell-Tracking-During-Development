# PC19-01 notes
- 2026-09-27T18:12:53Z started; no prior json
- 21:2xZ checked: round18/v_hyp_new_levers_r18nl-1.json refuted=true, fix k=1.5 only if exp72 DISPLAYS >= 0.955 (matches finding).
- round18/REPORT.md l.92: N1 k=2 tonight -> post-deadline list, narrow form (matches).
- CONTEXT l.3052 card (6): "P5 or U4 -> the line stays open, but no N1/N2 build before the deadline" (matches). No CONTEXT entry after 17:21Z; no user OK naming N1 found (grep N1/ExPO/extrapol).
- exp71 c09_exp71_export.py l.43: batchnorm frozen (matches). scan_hyp_n1_prep: exactly 10 keys differ, BN equal; x2/x3 staged under _dl/secft_x{2,3}_ds as NEW dataset ids (not re-versions) - consistent with the finding; x1p5 only in scratchpad.
- CONTEXT l.3032: secFT files public-only while Q3 unanswered -> any N1 file is public-only, private value 0.
- Nits: 'k=2/3' in the focus meant k in {2,3} (n1_prep built x2 and x3), so the WiSE-FT reading is an aside, not a real ambiguity. The narrow-form dummy gate compares deltas to exp72 (K2 base, no fm45), but n1_prep builds N1 on the exp76d template (exp70b base; exp76d delta -191 nodes, 79 vs 74 forks) -> compare to exp76d.
- Verdict: finding upheld (not refuted), with the base-reference fix.
