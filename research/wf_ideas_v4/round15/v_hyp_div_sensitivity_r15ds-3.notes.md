# v_hyp_div_sensitivity R15DS-3 notes (skeptic, started 2026-09-27T05:47Z)
- read scan_hyp_div_sensitivity.json/notes (R15DS-3 origin)
- CONTEXT l.698-710 (11 Sep 14:20 MSK): sjlee forks: dctta020-sectta1 0.947, dctta025-sectta1 0.947, dctta-v015 0.946. Different pipeline (0.947 stack, no DaughterNet, no x138 linker changes); tie at 3dp = unrounded |d|<0.001, compatible with 1 TP + ~2 FP in the band at public per-event values (+0.0023/-0.0007).
- experiments/exp60_trainlab/results.md dc rows: EDGE side is NOT negligible on 44b6: dc0.30 adj edge 0.9054->0.9042 (-0.0012, nodes -49, 0 TP lost); dc0.35 edge -0.0022 (nodes -88). 6bba edge ~+0.0001/+0.0002. Scanner attributed public -0.005 wholly to div TPs (edge ~4e-5 per lost TP fork only).
- Lab dc arms are x138 control WITHOUT insertion; public exp70d has insertion (cap 4) -> interaction untested (probably mitigating: rejected v's become orphans eligible for insertion).
- poll.log tail at 05:48Z (system clock): probes 43/44 not scored.
- ledger.md l.23: exp70d COMPLETE 0.949, L (7.19,7.36] h, insertion gate did NOT fire -> the -0.005 is not a runtime or deadline artefact.
- research/wf_ideas_v4/round15/v_plancheck_pc15-03.notes.md l.5 already flags that the sjlee forks are a different stack (Harmonic Fusion sjlee, not x138).
- VERDICT: refuted (the weight is overconfident, SHIFT and LAB make the same 43/44 prediction, the private clause is a non sequitur, and the edge channel was left out). Keep the 43/44 read rows R1-R5 unchanged. Only the labels and weights change.
