# v_recheck R2-RC-B notes
- 2026-09-25T20:22:59Z started skeptic recheck (value+feasibility)
- 2026-09-25T20:23:36Z read CONTEXT last 300 lines (R2 cites private BE 0.11-0.20; L2 Wilson>0.265; L5 in-sample DaughterNet), v3 mirror/edge/lowdet value verdicts (private mirror +0.0005 [-0.0005,+0.0016]; lowdet private ~0 [-0.0005,+0.001]; edge private 0..+0.001)
- checked in-sample claims: CONTEXT l.1071 public detectors trained on all 199 train videos (h in-sample); l.1350 edge net trained on the 199 videos; Addendum L5 DaughterNet 4/5 folds saw exp60 clips. exp60 split.json excludes only the 20 x138 coord-head stems + 4 dummy twins, which does NOT make detector/edge/DaughterNet out of sample. Claim holds.
- s_merge.json assumptions_adjudicated: public BE 0.265 vs lab ~0.11; loosening had 0 TP/+2 FP lab marginal; ~3% insertions evaluable. IDEAS.md I-066/I-067/I-077/I-078 are all 'refuted', consistent with the finding.
- arithmetic: +1 public TP = +0.0019 < R4 +0.002 bar, so R4 needs >= 2 net TP from ~1-2.5 events -> unreachable (holds even without 0.003 LB noise; the small event count is sampling noise).
- extra support: lowering the L2 Wilson 0.265 bar now would be a post-hoc change after exp60 dumps were downloaded (20:05 UTC) -> it breaks the pre-registration.
- nuance: the public read favours removals. A removal set whose precision lies between the private BE (0.11-0.20) and 0.265 would be public+ and private-. K3 forkmid is protected by its 0-TP-removed audit (L3/T9), so 'fine for K3' holds only because of that gate. Any future removal rider needs the same 0-TP / FP>=3*TP clause.
- verdict: not refuted (stays closed, info only, no build -> feasibility trivially OK).
- 2026-09-25T20:24:33Z final JSON written (refuted=false)
