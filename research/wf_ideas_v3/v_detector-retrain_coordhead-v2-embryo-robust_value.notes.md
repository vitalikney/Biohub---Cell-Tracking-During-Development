- 2026-09-25T10:55:33Z start: read BRIEF
- 2026-09-25 read experiments/coordhead_retrain/out_full_P.log, out_full_Q.log, tools/train_coordhead.py (debias=embryo subtracts per-embryo mean target), FRIEND_A_RUN.md, experiments/ext_x138/DIFF.md sec.4.
- Idea's numbers check: Q vs none out-of-embryo 1.3781/1.4990 = -8.1 %, 1.5875/1.7199 = -7.7 % (correct). Public in-embryo 1.2963 / 1.5668.
- Metric point: constant (annotation-convention) offsets only enter the score via 7 um GT matching; m7 re-match counts move <= 50/112k (0.04 %) for every head -> bias part is worth ~0. Downstream stages use pred-pred RELATIVE positions -> only the zero-mean random error matters.
- Isotropic-Gaussian decomposition (scratchpad bias.py): bias-free sigma change vs none:
  leak5 OOF (in-embryo): public -6.2 %, P -18.2 %, Q -16.5 %
  6bba->44b6: public(in-emb, 44b6 = crops of one movie) -12.8 %, P -9.6 %, Q -8.8 %
  44b6->6bba: public(in-emb) -4.8 %, P -3.4 %, Q -3.5 %
  => debias changes only the mean; Q ~= P on random part. Most of Q's '8 %' on 6bba is bias reduction (z 0.82 -> 0.43), score-irrelevant.
- x138 DIFF sec.4: head cut final nodes 2.9 % on dummy test, mostly one movie (44b6_0b24845f -10.7 %) -> ~+0.0026 of the +0.007 is node multiplier, per-movie volatile.
- Value estimate: ~+0.0044 non-node value for ~5-6 % random-error cut -> ~+0.0007 per 1 %. v2 vs public on unseen embryo: -3..+3 % -> -0.002..+0.002, central ~+0.0005; node drift +-0.001. Below +0.002 and below LB noise 0.003 -> REFUTE.
