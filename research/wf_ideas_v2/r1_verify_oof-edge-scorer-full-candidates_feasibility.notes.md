# feasibility verify notes (started 2026-09-24)
- raw geff (friend A cache) = ILP solution only: 44b6_0113de3b 25,001 edges all solution=1, min edge_prob 0.482 -> NO sub-threshold probs in lab cache; GPU re-dump mandatory
- replay.py starts at ckpt (post-gap); relink lives in raw->ckpt, only replayable via relink55/build_t55_cache.py path with DeepCenter ORACLE (unknown gap points default-accept)
- relink55/build_t55_cache.py DOES give a CPU path for relink changes (raw->ckpt, 199/199 exact 6.0 reproduction, dc_unknown55=0 via local DC model, ~30-50 s/video) -> lab path exists IF sidecar probs exist
- GPU: ~2.5 min/video full inference (friend B stream) -> 64 sel = ~2.7 h, 135 = ~5.6 h T4 of ~20 h left; must reproduce friend A node ids exactly (hardware/determinism risk)
- consumers of edge_prob downstream: ef (p==0 unscored test), short-track rescue (mean prob), leaf prune 0.3 (min edge prob), divinsert steal_prob_max -> sidecar must go in separate field, patch 4-5 places in kernel builder + replay + ckpt format
- effect bounded: bonus 1.0 x p<0.48 -> <=0.48 um cost change; pockets ~450 TP/340 FP; research expected +0.000..+0.001 < +0.002 gate; sparse add-like change also hits 44b6 win-rate wall (stitch precedent 15.5%)
- coordhead (exp51) changes probabilities (trilinear gather at refined coords) -> sidecar on base nodes stale once coordhead adopted
- verdict: refuted (test is buildable but cannot pass gate by construction; cost ~1 day eng + 3-6 GPU h)
