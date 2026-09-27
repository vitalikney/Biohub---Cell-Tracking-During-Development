# R17-RC-A skeptic notes (2026-09-27T11:14:27Z)
- start; no prior json
- 11:15Z (date -u): R8 cutoff 12:00Z is 45 min away. No build, lab gate, dummy and user OK can fit, so the feasibility side is closed by R8 whatever the value.
- Checked the cited sources: round7/scan_recheck.json R7-NF (668 missed GT nodes, 83% with no presafe node <4 um, 12% removed by the tail, 4.6% merges, 71% with an unclaimed final node at 7-10 um, |dz| ~4.7) matches. R7-RC-C (8.0 h gate, slack >= 0.46 h < 0.58 h spread) matches. round12 R12-NF (0.79% vs 5.20%; readmit -0.0023 vs +0.0008) matches.
- tools/build_probe_kernel.py l.64-67 and l.1407-1416: the DIVINS gate is elapsed since KERNEL_START_TS >= BIOHUB_DIVINS_DEADLINE_S (default 28800). Confirmed.
- v3 DoG value json: net lab -0.001..+0.0005 is ARITHMETIC (a ceiling chain), not a measured run. The clearance of 6.5 um < the 7 um match gate means the same-blob offset peaks get REJECTED by clearance (v3 wording), not added as duplicates. The finding's "becomes a duplicate" is loose but points the same way. v3 also flags FN/FP swap risk in the 4-7 um zone.
- Nit on runtime: L (7.36, 7.54] h is submission->score latency, so it includes queue/scoring overhead. Kernel runtime <= L, so the true slack is >= 0.46 h (a lower bound, which is honest). The "0.88 h vs 0.9 h" K2'' margin of 0.02 h is too thin to carry weight on its own; value and R8 carry the verdict.
- Official metric (memory): nodes over the estimate cost 0.1*dT/T; edges among unannotated cells are free, so added nodes cost only through the node-count term (+1% = -0.0009). That is consistent with the finding.
- Verdict: the finding HOLDS (not refuted); curator line OK, with minor wording fixes.
