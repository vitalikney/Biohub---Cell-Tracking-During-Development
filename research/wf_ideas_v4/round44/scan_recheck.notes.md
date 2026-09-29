# round44 scan_recheck notes (started 2026-09-29T17:14:07Z)
- 17:14Z: no round44 folder existed -> fresh. exp89t 56669888 PENDING at 17:15:03Z header (L > 8.24 h; ledger.md row 20).
- Coverage grep over round*/scan_recheck.json + v_recheck_*: 0 hits for exp09/divset36, exp17, exp20, B31/duplicate-node, pool-kernel, EMA-velocity, per-stage, B20 step (b). v3 FINAL_REPORT (i) all covered (R43 statement).
- RC-A (B31 duplicate-node closure, RESULTS 'local Friend C / B31': raw NN <1/<2/<3 um = 0/0/0, 'public 3 um NMS already excludes every pair ... clustering cannot change a graph'):
  measured same-frame NN on dummy CSVs (_dl/*/submission.csv, scale z,y,x = 1.625/0.40625/0.40625 um from tools/coordinject_patch.py l.113), script scratchpad/nn_dup.py:
  exp56 x138: nodes 121219, NN<1/2/3 um = 2/18/58 (node counts, pairs x2), min 0.81
  exp70g: 4/26/82; exp58 (#37): 4/26/82; exp85a (K): 6/34/100
  exp87a (K+CI): 24/134/210; exp79a/exp75 (CI): 20/124/192
  -> premise false on final outputs; CI adds ~100 near-dup nodes (<2 um) on 4 clips.
  scratchpad/nn_pairs.py: 67 pairs <2 um after CI in exp87a; 52 were >= 2 um pre-CI (exp85a), 41 >= 3 um; pre-CI dist q10/50/90 = 1.68/3.37/5.03 um; all 67 pairs both nodes in tracks; per clip 44b6_0113 4, 44b6_0b24 18, 6bba_05b6 2, 6bba_05db 43. Mechanism: many-to-one snap to one refined detection (alpha 0.5).
  scratchpad/r44/ci_dup_lab.py (overlap_lab.eval_clip, dummy lab, 4 train clips): exp85a vs exp87a = 6bba_05b6 TP 836->834 FP 8->11; 6bba_05db TP 1118->1116 FP 88->93; 44b6 unchanged (= R28-RC-C). Hybrid (exp87a with converged pairs reverted to exp85a coords, thr 2 um: 104 nodes; thr 3 um: 134 nodes) = IDENTICAL to exp87a on all 4 clips -> converged pairs are not on annotated nodes; CI's dummy loss is not from convergence.
- RC-B (RESULTS exp03B '+0.0048 vs A ... => real gain' vs exp16 seed 7 0.9502 'seed variance ±0.005', exp17 600 it 0.9556, exp08 full epoch 0.9539): seed spread 0.9575-0.9502 = 0.0073 > the 0.0048 gain; exp03B was the best of 2 seeds. LB: probe 2 +0.004 (0.941 pipeline), probes 11/15 -0.003 (TTA stack), probe 13 -0.007 (as secondary). Finals carry pilkwang primary + v1284 head (experiments/exp87a*/kernel-metadata.json, exp58*/kernel-metadata.json; biohub-ft-weights = DaughterNet only).
- RC-C (RESULTS exp09 divset36: raw 0.8997 vs hold12 0.9575, div 0/92, 32 of 92 GT divisions 6bba): dummy-lab clips (R28-RC-C, this round's lab run) have 44b6 edges 49-53 TP each vs 6bba 836-1118 -> every dummy-lab sign on K-base knobs is a 6bba read; divset/hold12 say 44b6-like dense clips are where linking errors live.
- 17:25Z: final JSON written (scan_recheck.json), 3 rechecks + NF, all info.
