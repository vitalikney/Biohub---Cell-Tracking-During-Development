# feasibility verify ef-anomaly-attribution-finals (started Thu Sep 24 16:22:30 UTC 2026)
- Kernel: tools/build_probe_kernel.py EDGEFILTER_FN l.486-615, EDGEFILTER_CAPTURE l.617 (inserted at _EF_RELINK_ANCHOR, i.e. BEFORE motion relink and linefit -> node coords there are pre-linefit), EDGEFILTER_CALL after linefit (l.631).
- Replay: replay.py run_config_video l.874; load_ilp_probs l.836 already loads raw/<stem>.geff raw_nodes (pre-linefit detector coords) + ILP edges with the kernel's own next-frame/length filter -> per-t median ILP step computable there in ~15 lines.
- ef_anom knob = restrict candidates to flagged t: ~20-30 lines (new param anom_min_step_um + per-t set passed in); default off = no-op; changes _edgefilter_sha -> ef config fingerprints change (re-run ef reference in the same lab job).
- Flag definition mismatch: parquet used median of relink_ilp_tight edges; kernel/replay can only cheaply use median of ALL ILP edges (post length filter). Thresholds must be re-read in the replay itself.
- Frozen-frame exact-zero test breaks under coordhead (float coords; temporal UNet context differs for t vs t+1) -> needs tolerance (e.g. median ILP step < 0.2 um) or volume equality.
- ef validated only on integer-coord cache; replay cannot test ef on top of coordhead (fixed nodes) -> any final = coordhead+ef needs an LB probe (slots: 5/day, 5 days left -> feasible).
- Cost of readout: 2 configs x 135 videos on Kaggle CPU lab (same as ef-a3-conf job, 4 workers). Feasible within a day.
- Verdict: refined change (no ef_anom build; finals policy + optional readout) is feasible, no pipeline conflict (order linefit->ef->swapfix->stitch->divinsert unchanged). Not refuted under feasibility lens.
