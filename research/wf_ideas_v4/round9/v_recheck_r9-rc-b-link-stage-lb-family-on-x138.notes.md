# v_recheck R9-RC-B notes
- 2026-09-26T12:56:48Z start; no prior json exists.
- Determinism: CONTEXT l.1310-1312 (exp46 parity sha256 == exp39; "deterministic run to run"), l.977 (same file scores identically), curator 25 Sep "19:05" (really ~18:40, l.1917) item (c) l.1909-1910: 0.001 public step between our kernels is real on public; transfer to private open. -> P21-P23 (0.945 vs exp29 0.947) are real negatives on the public embryo; 3-dp rounding means true delta in (0.001, 0.003).
- P21-P23 were on exp29 (plain relink, no flow prior/readmit), not x138 (RESULTS.md l.54-56). P24 exp43 = takaito verbatim whole stack (RESULTS l.57), not a clean association ablation; l.1312 attributes 0.944 vs 0.948 to different code/version.
- exp56 x138 cell 0: LEARNED_BONUS 1.0 (code default 0.75, cell 2), TIGHT 5.5, FLOW_MODE seed, K 12, R 40, GATE 1, FLOW_TIGHT 7.0, RAW_COST 0, READMIT 4 um/0.965, GAPFILL gap 3. Cell 5: 0 hits for gshift/global_shift.
- Cell 5 ~83350: readmit_discarded_detections is called INSIDE `if OUTPUT_MOTION_RELINK:` (relink OFF kills readmit + flow). fill_gaps_from_low_detections called at ~86320 AFTER relink, unconditional -> gapfill survives relink OFF (finding's "inside or after" is accurate).
- Seed mode: seed pass at seed_gate = TIGHT 5.5 um; flow field = K-NN of seed displacements. Measured per-frame global drift 0.5-2.3 um (CONTEXT l.1204-1206) << 5.5 um, so seeds carry the drift -> gshift plausibly subsumed; NOT measured (I-185: flow prior neutral alone on LB 0.947).
- exp60 dumps: tools/trainlab.py l.243 only presafe/preshort (both post-relink); build_probe_kernel.py l.1492-1579 presafe hook. No pre-relink hook -> confirmed. And lab is in-sample for linker anyway.
- Verdict: cannot refute closure; wording tweaks only. No build, R8 deadline 27 Sep 12:00 not relevant.
- 2026-09-26T12:58:48Z final JSON written (refuted=false).
