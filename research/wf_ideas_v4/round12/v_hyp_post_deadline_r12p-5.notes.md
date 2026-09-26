# r12p-5 paired-retrain gate verify (2026-09-26T20:45:11Z)
- Source: scan_hyp_post_deadline.json r12p-5 (same scan's r12p-2 G0 (ii) already contains the paired-retrain gate -> duplicate).
- Premise check: F-MOD-05 (head retrain 6bba->44b6 +12.0%, CONTEXT l.1488-1493) was diagnosed as learning 6bba's annotation z-offset = embryo shift, not leak; public head balanced ~10+10 videos. F-TRN-05: 81-87% of local TTA gain survives on a scratch primary -> LB failure = embryo difference, not memorisation.
- Leak persists via init: CONTEXT l.235-240 'LOEO (fine-tuned on 6bba, but base saw 44b6) are memorised'. Planned items are fine-tunes from pilkwang init (r12p-2: '4 paired fine-tunes x ~1 h') -> arm AND control leak; interaction bias (arms that stay closer to init win on the memorised held-out embryo). Leak-free = scratch per embryo (1.3 GPU-h/epoch x 5+ epochs per model; scratch secondary 0.920 = different operating point).
- Seed noise: CONTEXT l.88/167/252, RESULTS l.78: fine-tune seed variance +-0.005 (seed 7 0.9502 vs seed 42 0.9575). Gate's clip bootstrap ignores training-seed variance; 'same seeds' does not pair GPU trajectories once the loss/target changes. Detect +0.006 at sd 0.005/run: ~9 seeds/arm/direction; +0.002: ~75. Stated +4-8 GPU-h underestimates by ~10x.
- 44b6-train direction: 71 overlapping crops of ONE recording, ~1% annotated, 26 div (F-DAT-01/03) -> weak model, delta sign ~ coin flip; 'both directions' = low power.
- Deployment still needs arm vs public weights (leaky) -> gate answers 'does the change help within our recipe', not 'ship vs public'.
- No private/LB effect before 29 Sep; R8 not applicable (post-deadline curator text).
- 2026-09-26T20:46:38Z final JSON written (refuted=true)
