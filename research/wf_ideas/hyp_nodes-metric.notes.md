# hyp_nodes-metric notes (lens: NODES + METRIC mechanics)
- 2026-09-24 start: no prior result file; created folder.
- 2026-09-24 metric: adj = J*(1-0.1*(Npred-Nest)/Nest) per video, weighted by D=TP+FP+FN (tools/official/src/tracking_cellmot/metrics.py per_sample_metrics/summarise).
- ef graph (exp39+ef, local 0.9298; ef_a3_rl_pr_per_video.csv): 44b6 Npred 1.98M vs Nest 2.62M (ratio w-mean -0.166, range -0.63..+0.23); 6bba Npred 2.15M vs Nest 2.11M (ratio ~0, range -0.15..+0.50). Node term currently contributes +0.0023 (44b6) +0.0002 (6bba) to adj.
- Marginal: 1% fewer nodes everywhere = +0.00092 adj. Value of one node relative to one TP edge = 0.1*J*D/Nest: median 0.0034 (p10 0.00036, p90 0.014). So dropping a node pays only if P(annotated)*edges_lost < ~0.3%.
- FN anatomy after ef (6099 FN): a_never 1907, a_tail 624 (node removed by tail: short-track/prune), a_linefit 353 (linefit moved ckpt node >7um), a_taken 62, swaps 1528.
- 2026-09-24 node table (scratchpad node_table.py/node_value.py; exp39 tail graph + official match cache): 4.13M pred nodes, 3.17% matched to GT. Matched rate is ~3.2-3.4% almost everywhere (z, xy border, density); only drops to ~1% at z/xy borders (<1-2 um) and in comps <10 frames (0.9%). Full-length comps (99-101 fr) 9.8%.
- First-order value of DROPPING node groups (bonus - TP edges lost + FP removed): every spatial/length group is strongly negative (e.g. bxy<2um -0.045, clen 5-10 -0.016); only max(p_in,p_out)<0.3 is +0.0016 (overlaps ef). => N_pred exploitation by dropping real nuclei is DEAD: annotation is spatially uniform; break-even needs P(annotated)<0.3%.
- Conversely node COST is small: all-node bonus = 0.0875 total, i.e. 1 TP edge (~7.4e-6) = ~350 extra nodes. Adding nodes to recover missed annotated nodes is cheap if targeted.
