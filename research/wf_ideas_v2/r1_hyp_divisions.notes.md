# r1_hyp_divisions notes (started 2026-09-24)
- CONTEXT 14: local exp39 div 23/43/128 (J 0.119); B32/B35 reach: parent+both daughters detected 121/151 (direct), 136/151 window-rule; orphan pool 58/151; 39 second daughters claimed by other parent.
- L2 DaughterNet v1 steal confirmation +0.0019 (TP16->20, FP28->39), added-fork precision 4/15=27% ~ break-even 0.265. Public probe 28 = 0.948 (+0.001).
- exp36 hygiene (sister floor 5um + already-divided) = 0.946 tie. DivNet veto p>=0.5 +0.0023 local (59 FP removed / 1 TP lost), LB tie.
- Division base rates: parent->daughter step median 5.745um (p90 9.07, p99 12.8); sister sep median 8.85 (IQR 7.2-10.2); continuation 1.72.
- Daughters shrink: half-max volume -0.17..-0.27 at +1..+3 frames.
- OFFICIAL div rule (tools/official/src/tracking_cellmot/division_metrics.py): per-GT-division local 7um matching vs {grandparent, divider, children, grandchildren}; pred fork must be matched-parent-side node or its immediate successor => fork timing tolerance t-1..t+1; children lineages {child, its successors} must hit 2 distinct GT daughter lineages (child or grandchild). FP forks = considered-not-TP | forks matched to GT node with out-degree>=1 | cross-component | malformed (child with >1 pred). Forks on unannotated / GT-leaf nodes are free.
- AUDIT (scratchpad div_audit.py, approx per-division Hungarian 7um, 199 videos, 151 GT div): raw ILP solution has ZERO forks (div weight 1.2) -> ILP-fork transplant dead. Final direct TP 19 (official 23 incl. window).
  Final non-TP 132 by 2nd-daughter status: linked+orphan 36 | claimed by edge p>=0.6 33 | 2nd daughter missing (no gc either) 23 | claimed by unscored relink (p=0) 12 | claimed p<0.6 6 | missing at t+1 but gc at t+2 matched: linked 7 / orphan 5 | other ~10.
  ckpt (safe-div input) vs final: linked+orphan 44 -> 36, missing 13 -> 23 => ~10 orphan 2nd-daughter tracks deleted by tail (short-track filter) after safe-div declined them.
- AUDIT2 (div_audit2.py, final exp39 graph, fork classes reproduce official 23 TP / 43 FP exactly; 1948 free forks):
  TP forks: parent-to-daughter-midpoint 'mid' median 1.58 um; FP forks mid median 3.02 um; sister med 7.6 both; DivNet p median 0.77 vs 0.76 (useless); min daughter track len median 21 vs 12; FP forks near a GT division only 1/43 (FP = forks on annotated continuing cells).
  36 missed divisions with orphan 2nd daughter: parent sits ON c1 (pd_c1 med ~1.5 um), v 7-10 um away, mid ~3.7; safe-div symmetry gate (tau 0.6) rejects ~33/36; v is a LONG track (v_fwd median ~30, min 5).
  54 claimed: claimer w is an unannotated (53/54) established neighbour track (w_back>=5 in 41; indeg 0 in 8), w-mp 9.8 um median, claim edge prob median 0.71 (p=0 in ~25%).
- AUDIT3 (div_audit3.py): 112,975 orphan starts (t>=1) in final graph have a single-child parent u with sister 4-15 um within 12 um; hypothetical fork labels tp 30 / fp 2,537 / free 110k => precision 1.2%; long v (>=20) + interior 3.2%; + DivNet p>=0.7 6-8.5%. "Explain every orphan" is DEAD (way below break-even 0.265). Nearest free track end to orphans median 35 um (ends are rare).
- Missed-orphan geometry: parent sits on one lobe (pd_c1 ~1.5) => hypothesis: division centre is at t-1 (gp); test mid computed at gp.
- AUDIT3b: gp-centred midpoint / mirror / jump features do NOT separate TP from FP in the orphan pool (TP mid 3.4 vs FP 3.5; mirror 7.2 vs 7.1). Geometry is exhausted; precision is bound by image evidence (DivNet>=0.7 & interior & long v: 2/7).
- linefit (weight 0.8, window 2) walks back through single-pred chains: a daughter's fit includes P and GP -> daughters pulled ~0.8 um toward parent track (1D toy calc); small lever since only ~1 FP fork is near a GT division.
- External: Lime1123 divisions need ~3 um accuracy (LB divJ 0.28 at adjJ 0.89); kevin park 39% of division nodes >3 um off; ITEC re-detects missing cells via t->t+2 skip links; Loffler mask re-insertion at interpolated positions (TRA 0.65->0.80 at 10% FN).
- B35 step A (friend A): 0.90 full-frame pass reaches 151/151 GT divisions but +24% nodes -> peak cache exists (tools/recover_daughters.py).
- AUDIT4: claimed daughters: |v - GT b| median 2.9 um, 17/54 > 4 um (true daughter probably undetected), 30/54 within 3 um. TP: 2.3 um.
- AUDIT5: claimer w never has an alternative orphan successor within 3-6 um (0/54) -> not a displaced-neighbour swap; AUDIT6: claimer lineage stays ~8.6 um (median min) from the parent lineage; no over-segmentation twin pattern.
- GT asymmetry (gt_asym.py): 57/151 GT divisions FAIL the safe-div symmetry gate (tau 0.6) on GT coords; sister median 10.6 um, p90 14.4 (> SISTER_MAX 14); max parent step p90 10.0 (> SAFE_DIV_MAX 9).
- AUDIT7 (fork removal, exp39 final forks, official-equivalent labels 23 TP / 43 FP): DaughterNet OOF p exists for only 7 evaluable fork parents (export = single-child parents) -> needs rescoring.
  mid = |P - (c1+c2)/2|: TP max 3.8 um; remove mid>=4.0 -> 11 FP / 0 TP (local J +0.0071 => score +0.0007); mid>=3.5 -> 16 FP / 1 TP (+0.0005 local); mid>=3.0 -> 22 FP/4 TP (local -0.0008, public-calibrated +). minlen<3 -> 3 FP/0 TP.
  Local J 0.119 vs public 0.36 => local lab UNDER-values fork removal (break-even q 0.106 local vs 0.265 public) and OVER-values insertion.
- ILP raw solution: 0 forks on 67 sampled videos (1.46M solution edges) - structural at division weight 1.2; candidate-pair probs are not cached (raw geff = solution edges only).
- Short-track filter min len 6 (+rescue) runs after safe-div; div_insert runs post-linefit => ~10 second daughters lost before insertion sees them.
- Chosen hypotheses: (1) mirror sub-threshold peak daughter recovery; (2) fork midpoint filter; (3) insertion at ckpt stage + post-ef; (4) edge-net second-daughter pair probability in div_insert (conditional on probe 29).
- Scripts (scratchpad, read-only analyses): div_audit.py .. div_audit7.py, gt_asym.py
