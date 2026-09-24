# feasibility verify: clip-boundary-frames (started 2026-09-24)
- predict script L561-566: ILPSolver(edge=-1*p, appearance, disappearance, division); exp39 cell0 sets APPEARANCE 0.0, DISAPPEARANCE 2 -> one-line patch site.
- tracksdata 0.1.0rc9 toy ILP (4-node chain t0..3, p=0.6): default selects 0 nodes; pl.when(t==T_LAST) disappearance 0.05 + appearance -1 at t0 selects 4; NodeAttr comparison form also works. Implementation: trivial.
- friend A cache = cache/<tag>/{raw (ILP solution only), ckpt, dc, divnet}; no pre-ILP candidate graph anywhere -> ILP variant NOT replayable on CPU.
- GPU cost: ~2.5 min/video per pipeline pass (CONTEXT L958) -> SELECTION 64 videos ~2.7 GPU-h, CONFIRMATION 135 ~5.6 GPU-h (research's 0.5-1 GPU-h is low); ~20 GPU-h left, coordhead retraining has priority.
- Structural: ILP-dropped clip-end segments are isolated (a track ending at t96 would be extended by the ILP itself since the end cost is paid either way) and <=3 nodes -> short-track filter (MIN_TRACK_LEN 6, rescue min 4) deletes them; ILP fix alone = no-op on output; needs K_END/K_START <=3 tail rule -> pure node cost (~0.009 TP edge/node).
- Ceiling: +0.0011 local oracle (154 FN), below the +0.002 gate by construction; public 0-0.0003 below LB noise (+-0.003).
- VERDICT: refuted (feasibility/value). Only as free rider on a GPU run that dumps pre-ILP graphs anyway.
