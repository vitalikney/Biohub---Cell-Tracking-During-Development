# r1_verify hole-fill-sandwich TRANSFER notes (2026-09-24)
- No prior verify json. Inputs: r1_research_hole-fill-sandwich.notes.md (verdict refuted), CONTEXT.md B35 step A (l.1259), x138 lines (l.1381, 1426-1432), ext_x138/DIFF.md (readmit/gapfill knobs l.70-71, 108-121).
- In-sample evidence: 0.90 full-frame pass reaches 151/151 GT divisions (44b6 26/26, 6bba 125/125) vs 136 at 0.965 -> sub-threshold mass at ANNOTATED cells is complete on train; public weights saw all 199 videos; no held-out detector exists (exp11 B was fine-tuned from the public pretrained that saw 44b6).
- Same territory already LB-neutral: readmit (>=0.965, <=4um open end) and gapfill (>=0.5 peaks, <=3% nodes, end->start) each neutral alone on LB.
- Node multiplier: +1.0% nodes -> -0.1*0.01*0.93 = -0.00093 certain on test; forum min-track-len +0.013 offline / -0.004 public; x138 -2.9% nodes may carry part of its +0.007.
- Original rule fills land on 4-6um same-blob holes (valley ~1.0, 95-99%) = second modes at annotation positions (corners) learned in-sample -> local match to GT, on test pure duplicates that steal links. Classic leak signature.
- Refined variant (>7um persistent holes, clearance 6.5, valley<0.85, chains>=3): ceiling +0.015 local, realistic +0.001-0.004 local, public 0-0.001 after haircut; 3-node chains die at min_track_len 6 unless attached.
- VERDICT: refuted under transfer lens. Repair = leakage diagnostic (trigger rate at annotated vs unannotated valley-verified blobs) + embryo-held-out detector; neither fits 2 days cheaply.
