# verify arithmetic: gate-aware-refine-head (started 24 Sep)
- no prior json; reading r1_hyp_detection.notes.md + research notes
- per-FN value check: 1/(TP+FP+FN)=1/135,729=7.37e-6 (exp39 totals) ~ b_break 0.00298/399=7.5e-6 OK. Per-embryo: 44b6 0.00198/41=4.8e-5/FN, 6bba 0.00317/358=8.9e-6/FN.
- hypothesis ceiling arithmetic reproduces (1143x1.22=1394 FN x7.5e-6=0.0105; x1.6e-5=0.018) BUT assumes independent per-node recovery converts FN edges: a_never nodes lie in 721 runs (1567 nodes) -> 846 FN edges are INTERNAL to runs (need both ends rescued, ~p^2), ~1061 boundary.
- recovered node lands at 6-7 um = swap zone, 28.5% link-error rate -> conversion <=~0.72.
- measured learnable tail net rescue 43/798=5.4% (ridge), 37/798 HGB. Global: 0.054x1143=62 nodes; FN: 1061x0.054+846x0.003=~60 x0.72=~43 FN -> +0.0003. Ridge 4-7 zone +9.6% -> ~760 nodes x ~0.15 extra error rate ~ -115 involvements ~ -0.0008 -> net <=0.
- deq.py sim (scratch TMP; gaussian-mixture offsets + uniform 1.625um grid quantisation, 133k nodes): PERFECT de-quantiser median -9.3%, >=7 count -1.9% only (4021->3945; cross in 365 / out 289), 4-7 zone -7.7%. => de-quant acts on the 4-7 swap zone, almost nothing on the 7-10 tail. Scaled to real: >=7 -40 nodes, 4-7 -600 nodes -> ~+0.0004 + ~+0.0007 = ~+0.001 local for a PERFECT de-quantiser from scratch.
- public head already reaches -10.4% of theoretical -11.7% (~89%); residual for a 199-video retrain ~11% -> +0.0001..0.0003 lab, or ~0.11x0.007=+0.0008 if the whole x138 LB step scales. Below +0.002 gate. 44b6 tail lever: 167 a_never FN x5% x4.8e-5 = +0.0004 < +0.001 per-embryo gate.
- VERDICT: refuted (arithmetic). Writing JSON.
