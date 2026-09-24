# arithmetic verify: polyphase-shift-stitch-localisation
- started 2026-09-24; no prior json
- exp39 lab: D = TP+FP+FN = 122151+6846+6732 = 135729; J_edge = 0.900; one FN->TP = +7.37e-6; one FP removed = +6.6e-6; GT edges/D = 0.95. Div J = 23/194 = 0.119; one div FN->TP = +0.1/194 = +0.0005.
- N_pred fixed by construction -> multiplier term 0. Break-even: refinement flips matches both ways; only variance reduction gives expected gain.
- Dose-response (research notes, 24 videos): +0.22 um^2/axis xy var costs recall -0.0021 (44b6) / -0.0013 (6bba), pre-linefit, TP-only count. Convex -> removal <= this. With FP twin (flipped match -> our edge becomes FP) factor 1-2x, x0.95 -> pre-linefit J ceiling +0.0012..+0.004.
- Linefit (w0.8 win2, var factor ~0.23 for iid) = +0.0145 on 12 LOEO-44b6 (RESULTS l.99). Relink/gap see pre-linefit coords, final matching sees post-linefit -> retain 0.25-0.5 of pre-linefit ceiling -> +0.0003..+0.002 standalone ceiling (perfect de-quantisation).
- Realistic capture 50-80% (non-shift-equivariant phases, guards skip peaks, recentring) -> +0.0002..+0.0016 standalone.
- x138 +0.007 is not a de-quantisation dose: it includes learned bias correction (6bba z mean offset 0.90 um => bias^2 0.81 um^2, larger than the whole xy quant var 0.44 um^2), float z output, trilinear features in edge scorer. Polyphase w/ recentring removes xy quant only -> can't reproduce it proportionally.
- On top of head: overlap >=70% of same xy grid error -> residual <= +0.0005. Gate +0.002 fails in expectation. Swap/diverted oracle +0.048: offsets 4.4 um vs max quant error 0.81 um/axis -> unreachable (<3%).
- Verdict: refuted under arithmetic lens (original claim), refined claim plausible but below gate.
