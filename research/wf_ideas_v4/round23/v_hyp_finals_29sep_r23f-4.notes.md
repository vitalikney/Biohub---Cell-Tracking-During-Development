# v_hyp_finals_29sep_r23f-4 notes
- 2026-09-28T04:14:23Z start: skeptic check of R23F-4 (exp70b as partner = info/no change)
- 2026-09-28 ~07:20Z sources: CONTEXT l.2927-2932 (letter (b) 11:09:39Z 27 Sep names #37 as partner, not exp70b); l.3307 probe 46 read (exp70q cap6+thr0.3+forkmid 0.956, code 0); l.2136 forkmid lab = power-limited closure, sign favourable (+0.00013, div_J +0.0010, 1 evaluable FP); l.2388 user 26 Sep 20:33Z 'one public, one private'.
- Re-ran scratchpad r23/mc23b.py base: P1 {exp70g,#37} 0.656/0.370; P3 {exp70g,exp70b} FMU +5e-5 0.680/0.395, FMU 0 0.668/0.389, FMU -1e-4 0.648/0.380. Bronze deltas +0.024/+0.012/-0.008 REPRODUCED. Nuance: silver delta stays positive at all three (+0.025/+0.019/+0.010), so 'flips' holds for bronze only.
- mc23_out.txt 8 scenarios: P3-P1 bronze +0.013..+0.031 (at FMU +5e-5). All inside a judgmental model (I-092: MC never decides).
- Verdict: not refuted. No-change is carried by governance (letter (b) partner #37, private-aimed second final, forkmid public-picked/closed), not by the MC. Wording fix: say the model edge is small and sign depends on an unmeasured forkmid mean; silver edge is positive in the tested range.
