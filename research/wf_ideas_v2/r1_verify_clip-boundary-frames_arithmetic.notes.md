# verify clip-boundary-frames arithmetic (started)
- final exp39 graph (edges_exp39.parquet): 3,971,995 edges, 4,131,185 unique nodes in edges (median 17.7k/video); research used 2.11M ckpt nodes as base -> check
- per_video_all.csv exp39: Npred 4.131M, Nest 4.725M (ratio wmean -0.025; 44b6 -0.164, 6bba +0.001). G=128,883.
  gain per recovered FN (FN-weighted, incl. multiplier) 7.05e-6; node cost per added node 2.13e-8 (6bba 3.55e-8, 44b6 0.58e-8); +1% nodes everywhere = -0.00088.
  break-even precision: 0.003 TP edges per added node overall (0.005 on 6bba).
- FINAL graph per-frame node count / mid mean: t0 .784 t1 .825 t2 .873 t3 .926 t4 .969 | t93 .91 t95 .876 t97 .798 t98 .754 t99 .706 (mid plateau 42.2k/frame, slow decline toward end). Deficit vs local plateau ~26k (start) + ~24k (end) = ~50k nodes (1.2%).
  => all 50k restored at zero TP value costs 50k*2.13e-8 = -0.0011 = exactly the +0.0011 oracle edge ceiling (154 FN). Missing nodes carry ~0.003 TP/node = break-even.
- fn_exp39.parquet recheck: FN at edge slots t0/1/2 = 77/84/88 (7.8-8.1%), t96/97/98 = 68/70/96 (6.0/6.4/9.0%), mid 5.1%. Excess over mid = 156.6 FN edges (of 483 FN, 6,398 GT edges in those slots). Oracle +0.0011. Even ALL 483 boundary FN -> +0.0034 < claimed +0.004.
- verdict: refuted (claim 4x too high; oracle ceiling below +0.002 gate). Writing JSON.
