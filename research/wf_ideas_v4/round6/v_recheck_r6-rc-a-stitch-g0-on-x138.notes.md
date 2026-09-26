# v_recheck R6-RC-A stitch g0 on x138 — notes
- 2026-09-26T06:03:22Z started skeptic review; no prior json
- reviewed scratchpad stitch_reach.py: per-frame Hungarian 7 um on round(P)*scale, FN classes by pred out/in-degree, end->start t->t+1 pairs labelled TP / FP_eval (official rule: ga in GT sources OR gb in GT targets) / unevaluable. Logic correct.
- RERAN stitch_reach.py (16 s): output byte-identical to the stored JSON (FN 1,705; both-free 11, all 6bba; pairs 7-9 0/0/8, 9-12 6/13/906, 12-15 4/26/2018). Reproduced.
- cosmetic bug: per_embryo 'ends'/'starts' = 0 (only totals updated); does not affect any claim.
- break-even check: J=TP/(TP+FP+FN); +TP => +1/D, +FP => -J/D -> p* = J/(1+J) = 0.93/1.93 = 0.48. Geometric precision 10/49 = 0.20 << 0.48. Ceiling 11/~41.8k ~ +0.00026.
- 0 pairs < 7 um is expected: x138 flow-prior Hungarian relink + gapfill already consume every close end->start pair, so the old exp39 stitch reach (repairing ef breaks) does not exist on x138.
- Private transfer: an unseen embryo may have more breaks, but the bottleneck is precision at 9-15 um (0.20), not reach; ILP-backed variant not replayable, but lab reach is bounded by the same 11 FN; it is an old mechanism (R-rule: new mechanisms only until 27 Sep 12:00) and its gate (P29) already failed. Verdict holds: not refuted.
- 2026-09-26T06:04:39Z final JSON written (refuted=false)
