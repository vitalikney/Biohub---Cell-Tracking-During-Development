# r1 research fork-midpoint-filter notes (started 2026-09-24)
- 13:5x recomputed scratchpad/div_audit7.json: 2014 forks (1948 free, 43 fp, 23 tp). TP mid max 3.76, median 1.58; FP median 3.02.
  mid>=4.0: 44b6 1fp/96free, 6bba 10fp/262free, 0tp. >=3.5: 44b6 2fp, 6bba 14fp+1tp. >=4.5: 1+5 fp. TP minlen median 21 vs FP 12.
- tools/div_insert.py ALREADY has mid_um=6.5 and cos_max=0.25 gates (angle gate on c1-u vs v-u). So divinsert is only a tighten.
- Web: no published tracker found that uses an explicit mother-at-midpoint gate as a precision filter; closest = rule "daughter centre points near mother centre" (1906.10886 / generic), Linajea uses a learned cell-state classifier in the ILP (FP div 0.89->0.11, arXiv 2208.11467), Kaiser et al. arXiv 2403.15011 use Erlang cell-cycle age prior instead of geometry.
- CONTEXT 739: public safe-div funnel on GT: symmetry<=0.6 + divergence>=2.25 keep 35/151 real divisions; TP forks we have are pre-selected symmetric.
- Arithmetic public (TP19/FP13/FN21): -1 FP => J +0.0069; -1 TP => J -0.0189 (1 TP = 2.7 FP).
- scratchpad/div_audit8.py (1m44, exp39 tail divnet_rerank_fb435c47e6d4): every TP/FP fork has exactly 1 NaN-prob (added safe-div) child edge.
  FP forks: ILP child correct/added wrong 19, ILP wrong/added correct 15 (ILP-side prob often 0 = unscored relink), both wrong 9.
  mid>=4 FP subset: 4 ilpOK/addX, 5 both wrong, 2 ilpX/addOK -> dropping added edge: edge FP -9, edge TP -2 (smart: drop ILP side if its prob<=0 -> -10/-1).
  cos(c1-P,c2-P): TP max 0.00, FP 10 of 43 >= 0.13. mid/sis>=0.5 == cos>=0 (Thales). mid>=4 OR cos>=0.1: 14 FP (44b6 3, 6bba 11), 0 TP.
  GT divisions (151): mid median 2.33, p90 5.24, 21% >=4 (44b6 12%, 6bba 23%); cos median -0.75 p90 +0.03 -> gate-selected TP forks are the relevant population.
  Split: SELECTION has 7 TP/15 FP forks; mid4 removes 4 FP there; CONFIRMATION 16 TP/28 FP, removes 7 FP. Thresholds were picked on all 199 -> confirmation is contaminated.
  Per-embryo local div-J gain: 44b6 5/36->5/35 (+0.0004 score), 6bba 18/158->18/148 (+0.0008): the +0.002 / +0.001-per-embryo gate is arithmetically unreachable.
  Public EV (gamma/lognorm fit of TP mid): th4.0 P(TP>=4)=2.4-3.8%, dJ +0.009..+0.015 -> +0.0009..+0.0015 score; th4.5 +0.0005..+0.0009.
- Replay: tails store no safe_division flag (NaN prob = safe-div/gap/gap2/divins); run forkmid after divinsert in run_config_video.
- div_audit9: velocity-compensated midpoint (2P-pred) is WORSE (TP max 4.4, 3 TP at >=4); half-velocity ~ same as plain. Keep plain mid. Divins steal inserts must restore the stolen w->v edge when un-forked.
