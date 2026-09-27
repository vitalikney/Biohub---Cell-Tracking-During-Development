# R16AP-4 exp71/exp72 cards skeptic notes
- 2026-09-27T08:44:33Z start; no prior JSON
- 08:50Z sources read: CONTEXT.md tail (R13-A3 01:31Z, R15-A1 06:19Z, D2 07:41Z); scan_hyp_answers_prep.json R16AP-4/5/7; reach0955/r_retrain.json + v_retrain.json (model-swap LB record 0/5: exp08 -0.016, friend-A -0.025, exp23 -0.007, exp03B -0.003, soup -0.004; y3uanm FT notebooks were quick saves, never ran).
- K2 knobs in the card == experiments/exp58_x138_safe_lowref/probe.json (DIVINS_* , DUMP 0, REPAIR 34200, DIVINS_DEADLINE 28800, LOWREFINE 1). OK.
- tools/build_probe_kernel.py l.2235-2277/2552-2575: secswap guards (64-hex sha, != parent, manifest inside --dataset, needs both knobs). pytest tests/test_secswap.py: 32 passed (6.3 s), incl. K2+secswap differs from K2 only by knob lines + sha line, finals rebuild byte-identical.
- x138 cell 3 finder: explicit path, then rglob; sha mismatch -> FileNotFoundError/RuntimeError = FAIL-LOUD, not fail-soft (by design; a fallback would be a silent K2 rerun). ERROR can't be a final (eligibility needs COMPLETE), so acceptable.
- copy_or_extract_tree handles weights/ or weights.zip -> --dir-mode zip safe.
- exp71 c05/c06: TRAIN_BUDGET 4.0 h, HARD_STOP 6.0 h -> T+4.5 h central is bounded; 2.7-6 h range means a 09:00Z yes scores ~20:40Z-00:10Z, not surely 27 Sep.
- VALUE: no honest lab gate (G2 not built), dummy node gate in-sample (exp71 trains on all 199 videos incl. dummy), 0/5 swap record -> by R8 text exp72 is a post-deadline item; Q2 = explicit R8 override. E ~0.
- URGENCY: nothing depends on a 27 Sep score (finals tick 29 Sep 20:00Z; real edges 28 Sep 08:00Z / 18:30Z). The 'before 09:00Z' line manufactures urgency; recast as info, recommendation no.
