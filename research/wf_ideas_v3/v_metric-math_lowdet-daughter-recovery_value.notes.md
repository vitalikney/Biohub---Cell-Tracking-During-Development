# notes: value/transfer skeptic, lowdet-daughter-recovery (2026-09-25)
- read BRIEF.md
- 2026-09-25 read wf_ideas_v2/r1_hyp_divisions.notes.md: missed 132 = linked+orphan 36 | claimed p>=0.6 33 | 2nd daughter missing (no gc) 23 | claimed by unscored relink 12 | ... Relink-claimed 12 HAVE a node at the daughter -> excluded by the patch's own ">2 um from any node" rule. Addressable = 23/132 = 17%, not 27%.
- AUDIT3b (same file): mirror/gp-mid geometry does NOT separate TP from FP in orphan pool (mirror 7.2 vs 7.1 um). Precision rests on DaughterNet p_par only; measured DaughterNet insertion precision 4/15 = 27% ~ break-even 0.265 (CONTEXT; v2 notes). AUDIT3 orphan pool precision 1.2%.
- CONTEXT.md 1255-1262: B35 step A = full-frame public-primary 0.90 pass, 151/151 window reach, +24% nodes (max 73%); IN-SAMPLE detector.
- ext_x138/DIFF.md: lowdet dump = peaks >= 0.3, unrefined int16 coords, feeds readmit (>=0.965, 4 um of open end/start) and gapfill (>=0.5). x138 already consumes part of the pool (readmit/gapfill) -> x138-base addressable pool unmeasured; no x138 lab cache exists (sibling verdict v_metric-math_div-budget-ladder-x138_value.json).
- Sibling verdict: only 15/466 lab insertions evaluable (3.2%); x138 inserts ~3 forks/clip, ~150 public insertions -> ~5 evaluable.
- scratchpad lowdet_val.py (J_pub 0.36 fixed; G=20/40/60 guesses): public FN = 8.8/17.5/26.2 at p=0.5; missing-daughter share 23/132 -> 1.5/3.0/4.6 events. Deltas: +1TP/+2FP = +0.0003..+0.0010; +1/+3 = -0.0001..-0.0003; +0.5/+2 = -0.0002..-0.0008; +2/+3 = +0.0007..+0.0031; 5/0 ceiling +0.004..+0.019 (G=40: +0.006..+0.0095, idea says +0.011).
- Realistic E[TP] public: 1.5-4.6 addressable x cap-limited DaughterNet recall (lab insertion 4/71 = 5.6% of FN; assume 2-3x better) x peak present on unseen (0.5-0.7) = 0.1-0.9. E[eval FP] 100-200 forks x ~3% evaluable x (1-prec) = 2-4. Net -0.001..+0.001, centre ~0.
- 2026-09-25 verdict written: refuted (public ~0, range -0.001..+0.001)
