# notes R13-RC-B (skeptic, 2026-09-27T01:17:07Z)
- 01:17Z: no prior JSON. Probes 39-42 not scored yet (ledger/poll.log). CONTEXT tail read (L9 20:49Z, R12-A3 21:31Z, cap6 21:56Z).
- Re-ran scratchpad r13rc/k2bed_agg.py (7.8 s): numbers reproduce exactly. parity 71/71, divins 71/71; ins35 0.92632, ctl 0.92173.
  lp30 +0.00051 [-0.00043,+0.00142]; fm45 +0.00035 W/L 1/0 (1 fork, 1 clip); lp30+fm45 +0.00086; dc +0.00336 [+0.00117,+0.00613] divFP -9, divTP +0, edgeTP -5;
  dc+lp +0.00387. Sub-splits: dc on 54 non-exp60 clips +0.00593, on 17 exp60 clips +0.00004. Insertion (ctl vs ins35) = W/L 0/2 clips, divTP +2 -> +0.00458 rests on 2 clips.
- Additivity is trivial: 0.00051+0.00035=0.00086 and 0.00336+0.00051=0.00387 EXACTLY -> disjoint edit supports on this bed, not a test of interaction.
- The 9 removed FP forks: 1 per clip in 9 clips; 3 of them in clips with 0 GT divisions (tp=0, fn=0).
- KEY: FACTS F-DAT-12 (research/KNOWLEDGE/FACTS.md l.115): DeepCenter was trained ONLY on the 71 44b6 clips = this exact bed. dc0.30 '0 TP lost' is the model scoring its own training data; the private risk channel (TP forks with lower DC score out-of-sample) is structurally hidden. Honest bed for dc is 6bba (exp60 6bba +0.0010). Both 44b6 reads (exp60 -0.0006, exp64 +0.0034) are in-sample; 'the T9 reason does not reproduce' compares two in-sample reads.
- r13dp-3 notes: GT prior puts 11% of reachable TP divisions in a threshold band; '0 TP lost' in small lab draws is Poisson-likely even when harmful.
- VOI: action itself says L9/L5 unchanged -> no decision uses it; 1/6 transfer puts lab +0.0034 at ~+0.0006 public (below display). Risk: 'no knob negative / additive / lab-best' language leaks into L5 combos and R13-RC-C veto sizing (edge-filter lesson: lab over-trusts in-sample).
- Verdict: refuted as a 'revived' finding (value); feasible as a caveated info line only.
