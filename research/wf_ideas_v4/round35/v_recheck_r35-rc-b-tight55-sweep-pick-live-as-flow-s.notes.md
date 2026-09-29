# R35-RC-B tight55 recheck notes
- 2026-09-29T07:24:09Z start; no prior json.
- Verified in scratchpad exp85a_src.py: env l.76 TIGHT 5.5 (comment "ppsweep_selected.json ... tight55"), l.72 VALIDATOR_ENABLE 0, l.78 FLOW_MODE seed, l.86 SEED_GATE 0, l.90 FLOW_TIGHT 7.0, l.91 FLOW_RELAXED 0 -> falls back to RELAXED_UM default 10.0 (l.235). Code l.3286 seed_gate_um = TIGHT_UM when SEED_GATE<=0; l.3305 seed pass uses previous_flow as prior; l.3324-3325 no-field fallback = (TIGHT 5.5, RELAXED 10.0). Finding's code claims all correct.
- RESULTS.md l.43 probe 14 (56146538) = 0.947, sweep picked tight55. CONTEXT l.461 proxy 0.9490->0.9511; l.876 friend-B 12-video lab 0.8993 for exp29/tight55 (reference, not an isolation).
- CONTEXT l.228: relink-radius knobs "saturated, noise-level"; l.1214 haideptry density-adaptive relink radius 5.5-7.25 is a non-x138 stack (probe 23 only ported gshift) -> not an x138-family disclosure, not actionable under aggressive mode.
- Verdict: finding holds (not refuted). No build; deadline today, no lab, block-shared knob.
