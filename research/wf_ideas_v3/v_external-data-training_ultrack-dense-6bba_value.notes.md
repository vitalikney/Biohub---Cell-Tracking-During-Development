# notes value-skeptic ultrack-dense-6bba (2026-09-25)
- 11:1x read BRIEF, h_external-data-training.json, sibling verdicts v_..dense-dorado-secondary_value (refuted, central -0.001) and v_..dense-primary-headrefit_value (refuted, central -0.002). This idea only FEEDS those two.
- fn_anatomy_exp39.md confirmed: a_never 1907 (44b6 167 / 6bba 1740), b_swap 2175 (444/1731); total FN 6732; lab J 0.9143.
- r2_critic.notes.md:15,20: hosts' own Ultrack (dorado, UNet boundaries, full volume) covers GT at 97.2% <=7um, 91.7% <4um; our final nodes match GT <=7um at 0.988 on 44b6 -> teacher recall < student recall on annotated nodes. Union with Ultrack pts 0.988->0.998 but +30-40% nodes.
- curl raw.githubusercontent ultrack_supplementary sparse_zebrafish/config.toml: verified threshold 0.4, min_area 300, max_area 25000, max_distance 10, appear/disappear/division -0.1, window_size 25, postgresql 25 workers (full-embryo run, not 64x256x256 crops).
- RESULTS.md ~l.80-81: friend A exp02 6bba-only scratch -> LOEO-44b6 0.6803 vs own-train12 0.8332 (embryo shift 0.15); model exists (friend_a_exp02_loeo20) -> usable init for an honest A/B.
- discussions_summary.md:216 dense-label detector FT -0.0033 (head) / -0.0377 (head+encoder).
- Ceiling recompute: 6bba a_never 1740 + b_swap 1731 = 3471 FN x 7.37e-6 = +0.0256 lab cap (in-sample). Realistic in-sample 15-25% fixed -> +0.004..0.006 lab; x transfer 0.2-0.3 -> +0.001..0.002; minus harm 0.4 x 0.004 -> central ~0 public. Idea's own marginal +0.001..0.002 < +0.002 bar. Verdict: refuted.
- final JSON written
