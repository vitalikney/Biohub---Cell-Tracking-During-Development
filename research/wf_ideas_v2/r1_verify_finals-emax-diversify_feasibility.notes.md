# feasibility notes (started)
- no prior feasibility JSON; fresh run 24 Sep ~19:30 UTC.
- Kaggle CLI now: probes 29/30 submitted 09:41 UTC still PENDING (>9.5 h); probe 28 took ~7.5 h (03:45 -> ~11:20). Scoring latency 7.5-10+ h, not 3-6 h.
- build_probe_kernel.py: patches gshift/divinsert/leafprune/edgefilter/stitch/swapfix/coordhead compose in any order (anchors documented); exp48..exp51 folders exist. Stitch is placed after the edgefilter call; lab stitch delta (l6) measured ON TOP of ef only.
- div-cap research (r1_research_div-cap-private-j.json) verdict: do NOT raise cap; marginal beyond cap 4 = 0 TP / 2 FP -> 'DaughterNet cap c*' candidate is effectively dead; leaf prune + DN already in exp48 -> F2 differentiators = {ef toggle, stitch, coordhead toggle}.
- Replay lab cache = fixed integer detector nodes + edge probs -> coordhead cannot be lab-screened; all lab deltas are on a non-coordhead base.
- stitch sigma by refined formula: 1.5*|.0012-.0025|/sqrt2=.0014, + .0011 + .0004 -> s~.0018 (passes s>=.0015 screen marginally); E[D+] at mu 0 = .4*.0018 = .0007 vs near-copy .0002 -> premium ~.0005 = exactly the success threshold.
- Verdict (feasibility): survives; desk rule, <1 min python, <=1-2 extra probes, 20 GPU h ample (exp51 kernel 1,713 s). Caveats: sequencing under 8-10 h latency; off-base screens; thin candidate set.
- JSON written
