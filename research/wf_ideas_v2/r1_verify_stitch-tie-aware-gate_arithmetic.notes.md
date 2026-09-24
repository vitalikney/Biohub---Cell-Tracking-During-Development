# arithmetic verify: stitch-tie-aware-gate (started)
- sources: l6_fn_anatomy_report.md, l6_confirmation_vs_ef.md, l6_per_video_confirmation_vs_ef.csv, splits.json leak_groups, CONTEXT 00:40/02:00 notes (div arithmetic), metrics.py (div J micro-pooled).
- confirmation ef_st_all vs ef: 44b6 dTP +27 dFP +3 (GT edges 19,826; evaluable 1.4% of 2,100 added), 6bba +141/+6 (GT 53,228; 5.7% of 2,575). dnodes 0, ddiv 0 in all 135.
- per-edge value check: 44b6 (27-3*0.93)/~20.5k = 0.00118 = GT-weighted delta 0.00118; 6bba 135.4/~55k = 0.0025 = 0.00251. Metric arithmetic consistent.
- 44b6 leak groups: 18 groups, 5 non-tied, 5/0; group-mean-of-means 0.00097 (<0.001 gate!); per-video 0.00106. Group 4 = 49% of 44b6 gain.
- class ceiling: b_break on ef graph 399 FN, oracle +0.0030; st_all +0.0020 on 199 (281TP/19FP) = 67% of oracle; remaining 118 breaks lack ILP edge, non-ILP pairs precision 0.08-0.17 << break-even 0.48 -> unreachable.
- net per evaluable added edge = p(1+J)-J: p=0.937 ->0.878; 0.8 ->0.614 (70%); 0.7 ->0.421 (48%); 0.6 ->0.228 (26%).
- without ef: +0.0008 exact / +0.0007 replay (115 TP/5 FP).
- division: confirmation exp48-like 20/39/67; one div TP = ~0.0008 score = 40% of stitch gain. Stitch can consume a true orphan daughter only through an FP edge on a GT node (<=9 evaluable FP on conf) or steal of p<0.3 stitched edges -> expected cost <0.0001, variance 1 event.
