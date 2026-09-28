# R22XL-4 skeptic notes (2026-09-28, round 22)
- No prior answer file existed; this is the first pass.
- tools/daughternet.py l.116-129: score_nodes = mean softmax over bundle['models'] unless model_index given. Kernel DIVINS_CALL passes no model_index (lens_divisions-x138.notes l.9) -> dumps = 5-fold mean only. Confirmed: subsets not replayable from dumps.
- tools/build_probe_kernel.py l.279/345: DIVINS_WEIGHTS glob env var (default .../vitalii_daughternet/*.pt) -> a subset IS mechanically possible and byte-identical when unset; feasibility is not the blocker.
- CONTEXT.md l.1303-1304 (24 Sep): ensemble p_par 99th pct 0.83 vs single-fold OOF 0.90 -> numbers correct. Attribution nit: source is CONTEXT l.1304 (cited via IDEAS I-066 curation / r9h-4 label), and the 0.90 is OOF single fold, not in-sample single fold.
- Nuance: "volume in disguise" holds only where cap does not bind; where DIVINS_CAP binds it is a re-rank by noisier p. Either way no gain expected.
- No honest gate: DaughterNet v1 trained on all 199 train videos in 5 folds (CONTEXT l.1275); every lab clip is in-sample for 4/5 folds, any k-subset (k>=2) is in-sample on most clips; OOF-only single-fold = the model_index path already tested in the 24 Sep lab (lens_divisions-x138.json plan_critique (4) already removed fold-ensemble variants as untestable -> LB ladder).
- R8 hard line 27 Sep 12:00 UTC has passed; finals #37+#38 fixed; any new build would be post-deadline list anyway. I-063 (v1+v2 average) deferred-after-deadline (CHANGES.md l.778).
- Verdict: finding (do not build, info) stands -> not refuted.
