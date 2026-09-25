# v_hypotheses_r2s-1 notes (skeptic of R2S-1 freeze plan-issue)

## 2026-09-25 20:23 UTC - start; no prior json existed
- 20:24 UTC read: CONTEXT.md l.1640-1940 (R1-R10, Addendum L L1-L7, forkblob FAIL entry 20:05 UTC), scan_hypotheses.json + notes (R2S-1..8).
- Verified: tools/div_insert.py l.22/66 cos_max 0.25 (insertion rule, pre-existing) -> ANTIPAR threshold is borrowed, not tuned.
- experiments/exp60_trainlab/results_forkblob.json (generated 20:04 UTC): control POOLED div TP/FP/FN = 16/25/83, div_J 0.1290; forkblob vetoed 150 (TP 1, FP 6, ignored 143) -> div_J 0.1271, gate FAIL on div_J clause only. Per-fork rows carry parent/ilp_child/added_child ids + labels -> cos of these forks is computable by anyone who reads them (leak channel exists since 20:04).
- Lab veto break-even q* = J/(1+J) = 0.129/1.129 = 0.114 -> 'FP >= 3*TP' is non-binding; div_J clause needs ~FP >= 8 per TP. Evaluable share of vetoed forks ~4.7% (7/150).
- CONTAMINATION STATE: sibling skeptic v_hypotheses_r2s-2 notes 20:24Z: 'Running scratch antipar_lab.py (rule exactly as in R2S-2, cos>0.25 preset) on 56 exp60 dumps with official scoring' -> ANTIPAR labels are being read NOW; window 'before labels' is closing. Freeze proof = scan_hypotheses.json (written 20:25 UTC, file mtime 23:21 local), untracked in git.
- DNVETO skeptic (r2s-3 notes) proposes changing the kernel rule to max-of-5-folds < 0.057 -> any such change must be fixed BEFORE the DNVETO lab is read, else it is a post-hoc variant.
- 0.057 and the cos feature choice used GT of 151 train divisions, which include the 99 lab divisions (split.json) -> 'outside the labels' is overstated: thresholds not tuned on fork labels, but the feature choice saw lab-clip GT geometry. Lab pass = weaker evidence.
- Verdict: not refuted (cheap, R10 ranks pre-registration 2nd, no OK needed for a freeze), with amendments.
- 20:30 UTC final answer written to v_hypotheses_r2s-1.json (refuted=false, with amendments).
