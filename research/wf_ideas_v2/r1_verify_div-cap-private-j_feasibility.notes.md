# feasibility skeptic: div-cap-private-J (started)
- tools/div_insert.py knobs exist: cap_video, cap_frame, threshold, steal_frac (steal cap = floor(0.5*cap)); kernel --set DIVINS_CAP/DIVINS_THRESH (tools/build_probe_kernel.py l.200-206). Cap raise = pure --set change; candidate_triples + DaughterNet scoring are cap-independent -> zero Kaggle runtime change.
- Shipped probe 28: cap 4, alpha 1, ENSEMBLE thr 0.4 == OOF thr 0.5 (CONTEXT 03:10 calibration). So refined 'loosen t 0.6->0.5' is ALREADY SHIPPED.
- Saturation (per_video csv, friend_a_b20_exp29): s_c4_t0.5 selection 55/64 videos at cap 4 (median eligible 13.5); confirmation 106/135 at cap 4 (median eligible 14), 466 added, 0 missing p. -> lowering threshold further touches only ~31 unsaturated videos (~<1 evaluable fork): zero power. Raising cap does add insertions (~+3-4 per saturated video, ~450-600 on 199) -> ~13-18 evaluable at 3%, ~half in 44b6.
- s_c6_t0.6 vs s_c4_t0.6 selection: +50 added, 0 TP / +2 FP.
- Lab composition: replay.py run_config_video order ef -> swapfix -> stitch -> insert exists, but NO lab run ever combined ef (or lp030) with insertion. node_p_oof.parquet = 1,012,255 nodes exported from exp39 triples; kernel scores triple nodes on the fly. On ef base, new (u,c1) pairs from ILP re-link can involve c1 without p -> skipped in lab (divins_missing_p counter) but scored in kernel -> lab/kernel mismatch; re-export + kdn-score needed if missing_p is material.
- Lab runtime: ~7 min for 135 videos (l6_stitch log 418 s) -> 199 videos x 5 configs is well within one Kaggle CPU kernel.
- Track-scaled cap: ~10 lines in div_insert + kernel knob; but data refute (Spearman 0.02), skip.
- Original success criterion 'marginal p >= 0.17 on BOTH embryos' unmeasurable: 44b6 had 1 TP/3 FP evaluable at cap 4 on 71 videos.
- Both SELECTION and CONFIRMATION splits already consumed by v1 choice; a cap picked on all 199 has no holdout; public LB cannot arbitrate (marginal p ~ public break-even).
