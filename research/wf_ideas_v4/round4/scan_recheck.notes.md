# scan_recheck notes (round 4) - started 2026-09-26T00:46Z
- 00:46Z no round4/scan_recheck.json existed; started fresh. Read CONTEXT tail (R1-R10, READ TABLE, RESUME 00:02), round2+round3 scan_recheck.json (covered: floatout, I-077/78, tempfuse, swapfix, clip-boundary, axis-flip).
- 00:5xZ CANDIDATE refined-duplicate-collapse (v2 Dropped: "head does not make pairs converge") re-checked vs lowrefine (NEW in K2):
  same-frame NN pairs (um, voxel 1.625/0.40625/0.40625) on dummy CSVs _dl/biohub-*/submission.csv:
  exp56 = exp58t (K1): nodes-in-pairs <1/<2/<3/<4 um = 2/18/58/446 of 121,219 nodes;
  K2 exp58 = twin exp58n: 4/26/82/465 of 121,252 -> lowrefine adds ~+4 pairs <2um, +12 pairs <3um (0.02% of nodes).
  -> no material duplicate creation; collapse ceiling ~1e-5; stays closed.
- 01:0xZ CANDIDATE I-035 / C09 / E12 head-shift scale s (ORPHAN, never run; v3 FINAL_REPORT §c row 13; TASK_CLOUD_SESSION T12 gate:
  continue only if s_opt >= 1.25 and >= 4% gain on BOTH embryos). RUN NOW on CPU (33 s):
  scratchpad r4_headscale.py / r4_headscale_out.json; inputs experiments/coordhead_retrain/captures (199 videos, 313,205 kept peaks),
  public head experiments/coordhead_retrain/public_head/v1284_head.pt, fixed 4 um Hungarian pairs, tools/train_coordhead.py code.
  mean dist (um) on fixed pairs, excluding 20 probable x138 head-train stems ("_nox"):
    s:      0.00   0.75   1.00   1.15   1.33   1.50   2.00
    44b6: 1.4903 1.3117 1.3006 1.3060 1.3233 1.3499 1.4794
    6bba: 1.7328 1.5769 1.5767 1.5893 1.6175 1.6577 1.8444
  m4 (4 um re-match count): 44b6 max at s=0.75 (16,134 vs 16,117 at 1.0); 6bba max at 0.75 (97,324 vs 97,271).
  z bias on 6bba shrinks with s (0.45 -> 0.32 at 1.33) but y/x bias grows -> net worse. s_opt ~0.75-1.0 on both embryos.
  -> C09 gate FAILS decisively (s_opt < 1.25; s=1.33 is +1.7% / +2.6% WORSE). Close I-035 explicitly.
- 01:1xZ dup-collapse follow-up: unique same-frame pairs < 3 um: K1 29, K2 41 (20 pair keys new in K2 incl. moved coords);
  0 of the 20 new pairs have ANY GT node within 4 um of their midpoint (sparse GT, unannotated regions) -> no evaluable
  harm; node-multiplier exposure <= 12/121,252 = 0.01% nodes -> ~1e-5. Refined-duplicate collapse stays CLOSED on K2.
- 01:1xZ y3uanm secondary fine-tune (experiments/ext_y3uanm-secondary-ft/NOTES.md): weights dataset NOT public, training
  notebook only -> porting is impossible without our own retraining (R9) -> no revival via C10 'successor port'.
- 01:1xZ CANDIDATE leaf prune on x138 (v3 §i: 'returns only if E9 >= +0.002'; CONTEXT l.1808 pre-reg: |#36-#35| <= 0.001 -> closed).
  NEW FACT since round 3: P36 = 0.954 = #35 (delta 0, L36 (7.24, 7.42] h). Running CPU replay on exp60 (scratchpad r4_leafprune.py:
  prune_weak_leaf_nodes verbatim from tools/build_probe_kernel.py LEAFPRUNE_FN, inserted before linefit like exp57; arms 0.3/0.5).
- 01:3xZ FINAL written to scan_recheck.json (leaf prune replay still running; result -> scratchpad r4_leafprune_out.json).
