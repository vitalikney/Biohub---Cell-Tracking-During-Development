# v_recheck R4-RC-A head-shift scale C09 — notes
- 2026-09-26T00:57:16Z started skeptic review
- Read scan_recheck.json/notes (round 4 source of the finding); script scratchpad/r4_headscale.py (uses tools/train_coordhead.py HeadPack.shift_um = bounded(head,(x-mean)/scale), |shift|<2 um).
- Verified kernel equivalence: exp58 notebook cell 4 applies shift = bounded(...)/SPACING with no extra factor, guard >2.00001 um -> RuntimeError. So s=1 in script == x138 production. s>1 would trip the guard for |shift|>2/s um.
- Re-tabulated r4_headscale_out.json (all 8 s values, full and _nox sets):
  44b6_nox mean: 0 1.4903 | .75 1.3117 | 1.0 1.3006 | 1.15 1.3060 | 1.33 1.3233 | 1.5 1.3499 | 2.0 1.4794 ; m4 16086/16134/16117/16107/16093/16086/16050
  6bba_nox mean: 0 1.7328 | .75 1.5769 | 1.0 1.5767 | 1.15 1.5893 | 1.33 1.6175 | 1.5 1.6577 | 2.0 1.8444 ; m4 97205/97324/97271/97244/97220/97181/96782
  Full sets (incl. 20 x138 stems) give the same ordering -> exclusion list guess does not matter.
  Numbers in the finding match the file exactly.
- T12 gate (TASK_CLOUD_SESSION.md l.205-208): s_opt >= 1.25 AND >= 4% on both embryos. s_opt in [0.75,1.0]; s=1.33 is +1.7%/+2.6% WORSE -> gate fails decisively.
- Skeptic angles tried: (a) public head may be in-sample on these videos -> biases optimum TOWARD s=1, so out-of-sample optimum is if anything <=1: reinforces closure of s>1. (b) proxy (mean dist) vs metric: 4 um re-match count m4 also monotonically falls for s>0.75. (c) s=0.75 'shrink' is NOT a revival: +17/16117 (0.1%) m4, mean dist mixed (44b6 worse), would be a knob ladder after 27 Sep 12:00 mechanism cut -> stays closed too.
- Verdict: finding upheld (refuted=false); closure correct; no build.
