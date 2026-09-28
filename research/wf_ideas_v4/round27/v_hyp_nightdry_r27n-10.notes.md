# R27N-10 skeptic notes (2026-09-28, round 27)
- Recomputed from _dl/biohub-exp*/ *.log (json stream, 'time' field). pre = 'ILP timeout patch applied', gpu0 = 'GPU shard 0', ILP/repair = per-clip '[clip] ILP x s' / '[clip] repair x s' (dedup by clip).
  70g gap 293 end-gpu0 1054 ILP 131.0 REP 485.9 | 85a 201 / 1126 / 128.5 / 565.2 | 87a(CI) 236 / 1569 / 135.9 / 548.6
  88a(DIS) 721 / 1107 / 142.7 / 525.6 | 88b(TAU, non-DIS) 428 / 1153 / 135.4 / 547.2 | 88c(DIS1.75) 235 / 1109 / 123.7 / 536.8
  89p 207 / 1059 / 122.7 / 491.6 | 89q(DIS) 474 / 1057 / 122.7 / 493.3 | 89r(DIS+CI) 436 / 1473 / 124.1 / 488.3 | 89s(DIS) 376 / 1130 / 129.5 / 525.7
- Per-clip ILP 89q vs 89p: 24.0/17.9/4.1/76.7 vs 25.0/16.5/4.4/76.8 -> identical. Claim numbers reproduce.
- The excess is between 'Low-detection dump applied' (~46 s) and 'V1284 head patched' (253-788 s), code cell 4: contains Path('/kaggle/input').rglob('biohub-v1284-head-s075/v1284_head.pt') = recursive walk of the whole input mount (IO-bound -> machine noise). Non-DIS exp88b also had 428 s there, so not DIS-linked.
- Notebook diff exp89q vs exp89p: only the DIS env line (2.25 vs 2) + guard dict + header comment. DIS is consumed only as --ilp-disappearance-weight in predict_cmd (post-GPU). No pre-GPU code path reads it.
- R26 source of the '+15-20%' claim: round26/v_hyp_finals_r26f-4.notes.md l.7 (totals only, "Possible +15-20% (ILP)") -> retired.
- Caveats: dummy = 4 public clips; hidden ILP could scale differently but ILP ~10% of wall time and capped 1200 s/dataset; even +10% ILP = ~+1% L. Rule v2 (<= 2,100 s total) still includes the setup noise: exp89r 1,959 s margin is eaten by setup, not DIS -> a re-run rule already exists (2,100-2,500 re-run once).
