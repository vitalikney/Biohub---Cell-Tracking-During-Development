- 2026-09-25 start: read BRIEF.md
- 2026-09-25 ~11:30 UTC. Checked x138 notebook: cell 0 REPAIR_DEADLINE_S=27000 from KERNEL_START_TS; cell 5 _deadline_degrade
  switches off relink(+readmit inside it), gap close, gap2, safe divisions, linefit; check is PER MOVIE at repair start
  (l.2115), so once fired every remaining movie is fast -> a fixed 36000 cannot by itself push past 12 h unless the GPU
  phase does. Validator off -> cell 10 does not re-run write_test_submission. Guard is inherited from readmit-v1 (DIFF.md s.1:
  11/12 cells identical), not added by x138.
- Metric (tools/official/metrics.md l.140-146): edge J weight-averaged by TP+FP+FN per video; division J pooled over videos.
  Safe divisions are the ONLY fork source (probe 26: zero forks, 0.947->0.911). Pooled-J calc (TP/FP/FN 0.36/0.30/0.34):
  degrading f of GT divisions costs 0.1*dJ = 0.0013 (f=.05), 0.0026 (.1), 0.0083 (.3). Full L per degraded weight ~0.045-0.055.
- Timing: exp51 dummy 1,713 s / 4 clips (CONTEXT l.1424); hidden latency 17:09->00:39 = 7.5 h incl. queue+scoring.
  Model T_x138 ~ N(mu, s), fire if T>7.5 h, f = (T-7.5)/R (R = repair-phase length). mu 6.5-7.0 -> E[private gain]
  +0.0001..+0.007; mu 7.3 -> +0.003..+0.013. Very sensitive to mu, which we do not know (no hidden-run logs).
- PUBLIC: 41 teams reproduce 0.953 to 3 decimals. A guard firing inside the public embryo would make the start movie
  depend on wall-clock jitter (tens of minutes over 7.5 h) -> visible spread of ~0.001/movie. None seen -> public movies
  are (almost surely) not degraded. #34 (our exp56) is a 42nd data point. Realistic public gain ~0 (<= +0.0005).
- Verdict under value lens: REFUTED as an LB probe (public gain < +0.002, a tie is uninformative); KEEP as a zero-slot rider
  on whichever x138-family file is submitted as a final (budget-aware, keep safe divisions+linefit in degraded mode).
- 2026-09-25 wrote final JSON (refuted=true as standalone probe; rider fix)
