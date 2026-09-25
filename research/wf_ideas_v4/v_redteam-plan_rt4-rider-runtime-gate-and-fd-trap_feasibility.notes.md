# RT4 rider runtime gate + FD trap — feasibility notes

- 2026-09-25T17:48:38Z started. No prior JSON for this task. Reading tools/dummy_gates.py, step0.md, sibling verdicts (d4, h1, l2).
- tools/dummy_gates.py (151 lines) has no timing gate; the per-dataset lines exist in every dummy log: "[ds] detection+edges X s" (GPU shard) and "  [ds] repair X s | kernel elapsed" + run_stats.csv repair_seconds. Parsing ~20 lines -> part (a) tool is ~0.5 h, offline only, no kernel change.
- Same-GPU-code noise, detection+edges per clip across 6 dummies (exp56, 57b, 58=K2, 58t=K1, 58fd, 58ff):
  44b6_0113de3b 233.2/211.5/214.2/215.2/211.3/212.3; 44b6_0b24845f 245.7/210.8/213.6/215.0/210.2/224.6;
  6bba_05b6850b 229.9/210.5/211.6/211.5/208.5/205.3; 6bba_05db0fb1 267.5/233.2/235.5/233.9/230.3/253.0.
  exp56 vs K2 = +19,+32,+18,+32 (mean +25 s/clip) on IDENTICAL GPU code -> a 15 s/clip-shard FAIL vs a single K2 dummy false-fires (2 of 5 same-code dummies: exp56 mean +25, FF per-clip max +17.5).
- Repair tail noise, same code: K1(58t) vs 57b = -1.0,+2.3,+0.7,+6.4 s (mean +2.1). K2 vs 57b = +1.8,+3.7,+1.0,+11.3 (mean +4.45; lowrefine). An 8 s/clip threshold works only as a MEAN (sum over 4 clips > 32 s); per-clip it would fail K2 itself on 6bba_05db0fb1.
- Planned riders (CONTEXT l.1606-1610): K3 forkmid (graph edit ~0 s), K3b DeepCenter t* (node set == K3), K4 tempfuse (GPU phase, S6 26.09 ~18:00). Only K4 plausibly moves timing, and its cost sits in the noisiest measurement.
- Sim (scratchpad rt4sim.py/rt4sim2.py; step-0 model, repair 61 s + insertion 66 s, degraded 28.2 s; value 1e-5/insertion clip, 1e-4/full-repair clip as in the l2/h1 verdicts): moving DIVINS ALONE to 32400 with REPAIR 34200 is + 1e-4..2.7e-4 at s 1.0-1.2 but -0.0006..-0.0022 at s >= 1.2-1.3 (N 97-106) and negative at every s for N=130: the 0.5 h gap lets insertion eat the repair budget and pushes clips into degraded repair. EV under a guessed s prior (anchor is an upper bound): -2e-5..-5e-5 (9.0/9.5) vs +1e-5..+3e-5 (8.5/9.5) vs +8e-5..+3e-4 (9.0/10.5, needs H1 rule rewrite + user OK). Tmax 10.1-10.4 h (under 12 h).
- This matches v_literature_l2-deadline-retune-12h_value.json ("never move DIVINS alone") and FINAL_REPORT v3 l.57 (8.0 h chosen so K2==#35 while L<=8 h). The rebuild action of RT4 is the harmful half.
- Part (b) FD 0.9249 not yet in CONTEXT (grep); recording it is a zero-cost text edit. Feasible.
- Extra GPU: "median of 2 dummies" when borderline = ~0.5 GPU-h each from the ~11 h quota shared with exp60 lab; with GPU noise ~+-25 s borderline is the NORMAL case for K4.
- final JSON written (refuted=true as specified; reduced form: report-only ledger, no DIVINS-only rebuild, record FD trap).
