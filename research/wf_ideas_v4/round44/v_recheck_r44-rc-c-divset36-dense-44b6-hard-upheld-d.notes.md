# v_recheck R44-RC-C notes (started 2026-09-29T17:28:15Z)
- No prior v_recheck JSON for this id; scan_recheck.json R44-RC-C read.
- Cited lines verified: RESULTS.md l.24 exp09 '(92 GT divisions; 32 are 6bba)' raw 0.8997; l.109 Friend B CALIBRATION on LOEO-44b6 12 videos (ALL ~0.88-0.90); CONTEXT l.4244 SEC dummy all from 6bba_05db0fb1; l.4525 exp89t dummy +0.00089 (node mult + one FP flip on 6bba_05db0fb1).
- Rerun scratchpad r44/vrc_c_tp.py (overlap_lab.eval_clip, exp85a vs exp87a): 44b6_0113 TP 46 FP 3 FN 4; 44b6_0b24 TP 49 FP 0 FN 0 (identical both arms); 6bba_05b6 836/8/9 -> 834/11/11; 6bba_05db 1118/88/65 -> 1116/93/67. TP 46/49 CONFIRMED (scan notes '49-53' is a typo).
- Pooled edge Jaccard 2049/(2049+99+78)=0.92049 -> 2045/(2045+107+82)=0.91540 = -0.0051 = the logged CI dummy delta -> lab is edge-pooled; 44b6 weight = 95/2226 edges ~4%. Caveat 'dummy lab = 6bba read' HOLDS.
- REFUTING FACT: experiments/_lib/divset36.json = 36 videos, 32 x 6bba + 4 x 44b6. The '32 are 6bba' in RESULTS l.24 counts VIDEOS, not divisions. divset36's 'division-rich is harder' (0.8997) is a ~89% 6bba read; it does NOT flag 44b6 as the hard embryo. holdout_split.json hold12 = 6 x 44b6 + 6 x 6bba (0.9575), train 120 6bba / 63 44b6.
- The '44b6 dense/weak' evidence is the exp02/exp03A per-video notes on hold12 and the Friend B LOEO-44b6 set (model never trained on 44b6 there -> out-of-embryo, not intrinsic density). So the finding's chain 'divset36 flags dense 44b6-like as hard' is a misread; the caveat itself is not new (R28-RC-C '44b6 unchanged', CONTEXT l.4244).
- Verdict: refuted=true (framing wrong, no action, no gain). 0 Kaggle calls.
- 17:30:47Z final JSON written
