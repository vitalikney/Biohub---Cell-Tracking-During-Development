# transfer verify: refined-duplicate-collapse
- started 2026-09-24; no prior json
- Read the research notes: oracle survivor post-hoc +0.00043 (44b6) / +0.00196 (6bba); <4um oracle -0.0003/+0.0001; head-free rules -0.002..-0.013.
- From the gate-aware-refine-head transfer json: x138 head shift mean 0.74 um, max 1.61 um; trained on 20 in-sample train movies.
- Arithmetic: to converge under 2.0 um a pair needs d <= 2 + 2*shift; mean shift gives ~3.5 um, max shift gives 5.2 um. The raw NMS floor is 3 um, so merges land almost entirely in the 3-4 um band, where the oracle value is ~0.
- Per-embryo gate: 44b6 oracle +0.0004 < +0.001 gate, so it fails even at the oracle.
- Leakage: the head and detector are in-sample at annotated points, so pulling both peaks toward GT inflates convergence at annotated nuclei locally.
- Divisions: only 23/151 GT divisions are detected forks, so the fork exclusion misses most sister pairs (3-6 um apart); the head could merge sisters on embryos with more divisions.
- DONE: JSON written (refuted=true).
