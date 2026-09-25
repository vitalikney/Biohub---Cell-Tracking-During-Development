# v_hypotheses_r2s-6 notes

- 2026-09-25 (night round 2) start. No prior json existed. Read scan_hypotheses.json R2S-6 source finding.
- 2026-09-25 ~23:15 UTC (local clock). Sources: CONTEXT.md l.1753-1756 (T6 forkmid rule), l.1860-1874 (Addendum L3/L4), l.1917-1923 (forkblob FAIL); scan_hypotheses.json/.notes.md; scratchpad gtstats.py/gtstats.json, dose_all.py/dose_all.json (session acabaea6 scratchpad).
- Verified: GT divisions all dt=1 (151/151), so mid is not inflated by frame gaps. GT coords are INTEGER voxels (z step 1.625 um -> up to 0.8 um rounding in z); pred coords are float, linefit-smoothed (final graph). GT plain 1-step displacement pct 50/95 = 1.82/5.30 um, 8.1% of GT steps >= 4.5 um.
- Numbers reproduced: GT mid>=4.5 25/151 (16.6%); pred 40/676 (5.9%).
- CONDITIONAL geometry (new): GT mid>=4.5 divisions: cos median -0.03 (10/90 pct -0.61/0.58), sister median 11.75 um; pred mid>=4.5 forks: cos median 0.58 (10/90 0.20/0.85), sister median 6.21. Different populations -> marginal 17% vs 5.9% overstates forkmid TP risk.
- mid>=4.5 AND cos>0.25: GT 5/151 (3.3%) vs pred 34/676 (5.0%) -> ~1.5x enriched only (weak, not 'not enriched', not strong). mid>=4.5 AND cos>0: GT 12 (7.9%) vs pred 39 (5.8%).
- ANTIPAR contains forkmid: 34/40 over 56 clips (85%), not only 14/16 shard A.
- Pred mid pct 50/75/95 = 2.07/3.11/4.69 vs GT 2.33/3.52/6.01 (pred more compact; smoothing?). Step-displacement check pred final vs presafe running in background (r2s6_pred.py).
- Background result (r2s6_pred.py, 56 exp60 clips, plain 1-child edges): FINAL coords step disp pct 5/25/50/75/95/99 = 0.37/0.85/1.41/2.20/3.83/5.25, share>=4.5 = 2.4%; PRESAFE 0.20/1.13/1.88/2.98/5.45/7.89, share>=4.5 = 9.3%; GT raw 8.1%. -> linefit smoothing shrinks displacements ~3-4x at the 4.5 um tail. forkmid measures mid on FINAL coords, GT on raw integer voxels -> the 17% GT rate is not the TP flag rate of the forkmid rule; the comparison is scale-biased.
- Checked: no T9/forkmid results file yet in experiments/exp60_trainlab (only results_forkblob.*), so a coupling clause can still be pre-registered honestly.
- Verdict: refuted (headline confounded by coordinate smoothing + conditional geometry; contingency 'forkmid fails -> K2+ANTIPAR' risks re-admitting forkmid's vetoes under ANTIPAR's looser TP<=1 gate since 34/40 overlap).
