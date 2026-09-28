# R27-RC-C skeptic notes (2026-09-28 ~16:10 UTC)
- No prior answer file existed; started fresh.
- experiments/RESULTS.md l.36: probe 4 exp19 det 0.95 = 0.940 vs 0.941 (old public/exp06 family, NOT x138/K). Confirmed.
- knobarms_28sep/v_6.json: refuted DET 0.96/0.97 on slot value; clause 'Revisit only if both READMIT arms are spent and a slot is left over' present. Confirmed.
- v_5.json: READMIT 0.99 dropped as dominated. Confirmed. 0.92/0.90 closed by 12:23-12:25Z user rule (CONTEXT). Confirmed.
- inventory.json l.448-460: readmit keep = d <= READMIT_RADIUS_UM (default 4, closed) & score >= READMIT_MIN_SCORE -> '4 um of an open end' claim correct.
- CONTEXT 12:25Z: morning = stack of the night winners; MORNING TABLE v1.1 (14:12Z) whitelists only {K, SEC n2a, DIS 2.25, CI}; UNUSED is the honest default. DET is not in the whitelist -> closed by user rule independently of mechanism args.
- Weak spots (do not flip verdict): anchors det 0.95 -0.001 / MIN_TRACK_LEN 4 -0.002 are old-family reads within noise; DET 0.97 removes [0.965,0.97) main peaks that readmit 0.94 could partly re-add near open ends (net effect smaller than -1.0% candidates). DET also couples into dual-seed retention guard (nonlinear). None supports a build.
- Verdict: finding holds (info, nothing to build). Not refuted.
