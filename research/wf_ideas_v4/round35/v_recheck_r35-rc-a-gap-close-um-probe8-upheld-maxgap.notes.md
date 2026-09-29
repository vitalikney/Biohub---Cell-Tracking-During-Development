# v_recheck R35-RC-A gap-close UM (probe 8) - skeptic notes, 2026-09-29
- No prior json; started fresh.
- experiments/RESULTS.md l.40 (not l.29): LB probe 8 exp24 GAP_CLOSE_UM 5.0->6.5, id 56071497, LB 0.944 vs 0.945 (exp06 base, pre-x138). l.179 A20 same. CONTEXT l.263.
- RESULTS l.17 (not l.6/8): exp07+pp hold12 gap5um/1fr 0.9619; gap 2 frames 0.9583; gap 8um 0.9586 (-0.0033). Quoted correctly.
- exp85a ipynb (experiments/exp85a_k2cap6_div04_ra094) env l.17-23: MAX_GAP 2, UM 5.0, DENSITY_ADAPTIVE 1, ref 6.5, gain 0.040, max delta 0.125, neighbors 3. Defaults l.268-269 (MAX_GAP 1, UM 6.0).
- Code verified: `effective_gap_max = min(GAP_CLOSE_MAX_GAP, 1)`; `threshold_um = GAP_CLOSE_UM * (gap + 1)` = 10 um; adaptive delta clipped +-0.125/step (x2 = +-0.25 um total on the 10 um threshold). Config also has gap_close_effective_max_gap in its printed config (l.375).
- PP_CANDIDATES l.5707 gap45 = GAP_CLOSE_UM 4.5 (a SMALLER radius; the sweep offered it and x138 kept 5.0). So the x138 author tested only downward, weak evidence about upward.
- Side fact NOT new: research/wf_ideas_v4/knobarms_28sep/inventory.notes.md l.11/l.19 already records MAX_GAP 2 -> effective 1.
- Feasibility: GAP_CLOSE_UM is in x138 cell-1 config guard (round13 scan_recheck l.12; knobarms inventory l.5) -> any change needs a builder guard patch; moot as no build proposed.
- Verdict: finding correct; recommends no action; not refuted. Caveat: probe 8 was on exp06 base, not x138; the -0.001 is inside noise, but the lab and LB signs agree (<=0), and no disclosure from other teams for a larger radius was cited.
