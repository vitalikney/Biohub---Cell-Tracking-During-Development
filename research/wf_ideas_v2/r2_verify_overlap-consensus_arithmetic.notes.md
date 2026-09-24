# r2 verify overlap-consensus ARITHMETIC (started)
- no prior json; fresh run. Read r2_research notes, r2_critic notes, oc_sim.py.
- parquet exp39 44b6: TP 18,763 FP 1,322 (+FN ~1,063) -> D_44b6 ~21.1k (matches 21,148). 44b6 ~26.8k edges/video (~270 nodes/frame), D/video ~298.
- multiplier break-even: 1 FN fix/video = 1/298 = 3.4e-3 J_v; 1 extra node = 0.1*0.95/27k = 3.5e-6 -> ~950 nodes per FN fix. +0.5% node cap worst case = -0.00047 embryo-level; +0.3% = -0.00029.
- forks: 44b6 ~12.5 forks/video, comp_fork edge share 3.2% -> fork-skip removes few components unless percolation.
- MEASURED oc_fp_sim.py (scratchpad; exp39+ef match files, FP attributed to GT node side, owner = max min(border um, frames)): 44b6 TP 18,841 FP 1,074 (+FN 985 -> D 20,900). multi-copy GT node-sides 4,336 holding 255 FP; 203 discordant keys; owner propagation net FP removed = +41 (g0 +38, g3 -5, g2 -1, rest +0..+3).
- Ceiling (perfect splice): FN 89/20,900 = +0.0043; FP 41*0.95/20,900 = +0.0019; total +0.0061 on a 44b6-type embryo; pooled 199 +0.0009. Hypothesis's "+0.013 if FP flip too" is overstated ~2x.
- group 0 holds 75% of FN gain and 93% of FP gain -> conditional gain on a test embryo depends on crop density (overlap pairs ~ n^2).
- final JSON written (refuted=false; ceiling +0.0061, realistic +0.0025-0.004 conditional, ~+0.001 unconditional)
