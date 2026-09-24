# transfer skeptic notes: anisotropic-forkaware-rts-smoother (started Thu Sep 24 16:23:44 UTC 2026)
- replay write_geff rounds coords to int voxels exactly like the submission writer (replay.py L626-634) -> no float-vs-rounded scoring artefact. But z output grid 1.625 um => per-axis z smoothing mostly erased at output.
- a_linefit FN (fn_exp39_ef.parquet): 353 total; 44b6 28 FN in 13/71 videos; 6bba 325 in 68/128.
- CEILING if ALL a_linefit FN rescued w/o losses (per ef_a3_rl_pr per-video TP/FP/FN): 44b6 +0.0013 (GT-weighted) / 6bba +0.0027 / all +0.0025. 44b6 ceiling barely above +0.001 per-embryo gate; win-rate >=55% impossible on 44b6 (13/71 videos even have an a_linefit FN).
- LB probes 20-25 all 0.945-0.947 -> public noise floor ~+-0.002 with 0.001 display; a +0.0005-0.002 change is unverifiable on LB.
- L5: ef_a3 (drop only) +0.0102 vs ef_a3_rl (drop + ILP re-link) +0.0144 on selection -> ~30% of the filter gain trusts the in-sample ILP/edge net; rs0 would smooth ALONG those 17,860+8,609 (confirmation) ILP re-links -> in-sample channel. rs2 (cut unscored) and a variant also cutting at ILP re-links are network-free.
- ef confirmation 44b6 +0.0145, 6bba +0.0169 -> topology changes do reach 44b6 annotated nodes; but resmooth gain is conditional on probe 29 (edge filter) transferring; without the filter rs0 ~ no-op.
- exp51 coordhead (float coords) is the likely ship; lab runs on the integer 1.625-um grid -> lambda optimum measured in the wrong regime (pitfall c). In-sample detector -> lower local noise -> local lambda biased toward under-smoothing.
- verdict: refuted=true (unsure it survives: gate unreachable on 44b6 honestly, LB-unverifiable, conditional on 2 pending items). Repairs in JSON.
