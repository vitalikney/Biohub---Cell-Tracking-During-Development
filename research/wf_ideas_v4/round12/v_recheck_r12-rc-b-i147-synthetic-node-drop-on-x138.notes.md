# v_recheck R12-RC-B I-147 synthetic node drop - notes
- 2026-09-26T20:45:40Z start; no prior json present
- 2026-09-26 ~23:50Z read scan_recheck.json/notes (R12-RC-B), scratchpad r12/nodegroups.py, agg.py, agg_out.json (all numbers in the finding reproduce from agg_out.json).
- Method check: arms drop group nodes + incident edges, official_eval (tools/trainlab.py l.432) + official summarise (D-weighted adj J + 0.1 div J). Matching 7 um Hungarian per frame, same as metric. OK.
- Decomposition (my run): all deltas are in adj_edge_jaccard; division term change 0 for gap/synth_all/gapfill/readmit_leaf in both embryos.
- Leave-one-clip-out on gap arm: delta range -0.00207..-0.00242, never flips sign -> not a single-clip artefact.
- Correction: '3-4x less annotated' is partly Simpson pooling (44b6 holds 54% of gap nodes, low base rate). Within embryo: gap 44b6 0.42% vs 0.79% (1.9x), 6bba 1.74% vs 5.20% (3.0x); synth_all 2.5x / 3.2x; readmit ~6x.
- Correction: 44b6 synth_all rate 0.32% sits AT the nominal 0.16-0.3% break-even, yet drop = -0.0100; loss is carried by the ~2 TP edges each annotated gap node bridges (break-even for gap nodes ~half the per-node one), consistent with finding's scan text.
- gapfill +0.00012: 0.09% nodes, below LB 3-decimal resolution, would be a new mechanism past R8 (needs new user OK by 27 Sep 12:00) -> not a lever. readmit_leaf +0.00091 = P36 class (RESULTS.md l.69: #36 0.954 = #35, public 0). Confirmed.
- ideas.json I-147 detail still says 'annotation is spatially uniform' -> curator update is warranted. Verdict: finding holds (refuted=false), info only.
