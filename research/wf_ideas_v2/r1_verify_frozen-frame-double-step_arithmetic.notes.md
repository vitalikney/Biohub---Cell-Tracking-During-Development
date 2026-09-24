# arithmetic verify: frozen-frame-double-step (started 2026-09-24)
- no prior json. test/ folder = 4 train copies -> no info on hidden-embryo freezes.
- parquet (exp39, pre-ef) labels: 6bba sel TP52543 FP3189, conf TP50845 FP2335; 44b6 conf TP18763 FP1322. frozen proxy 909. post class: sel TP2873 FP534, conf TP2718 FP461 (reproduces research).
- per-edge value pooled 199: 1/GT(128883)=7.76e-6; FN->TP x0.95 = 7.4e-6; FP removal ~6.6e-6. Confirmation run GT ~73k (6bba ~53.5k + 44b6 ~19.8k) -> 1.36e-5/edge.
- ceiling after ef (research sim, post frames 6bba all): TP5789 FP546 FN660 GT6449; normal rates FP/TP 5.2%, FN/GT 5.5% -> expected FP301 FN355 -> excess FP245 FN305 -> full-excess ceiling (305*.95+245*.9)/128883 = +0.0040 pooled; confirmation ~+0.0035 (half the edges, 1.36e-5).
- ILP-only conf +73TP -32FP -> (69+29)*1.36e-5 = +0.0013 conf; FILL +87/+18 -> +0.0009. Captures 37% FN excess / 27% FP excess. Pure 6bba-like embryo: +0.0018 max.
- Original hypothesis claim (+0.0015..0.003 via motion model) is refuted: velocity carry +1TP after ef, gate scaling net negative. Remaining gain = trusting in-sample ILP on hardest links (optimism channel). Calibration: relink-off local +0.0014 edge (44b6 12 vids) & per-frame sim ~+0.019 on 6bba normal frames pre-ef -> LB -0.002 (probe 21). Transfer of 'ILP over relink' measured <=0.
- division quantisation: 1 div event ~ 0.1/194 = 0.0005 pooled, ~0.001 on confirmation = same size as claimed gain -> read edge term separately.
- LB rounding 0.001; expected public ~ 0.0013*0.5(P freeze)*0-0.5(optimism haircut) ~ +0.0000..0.0003; max +0.0018. Target gap 0.022 -> <=8% even best case.
