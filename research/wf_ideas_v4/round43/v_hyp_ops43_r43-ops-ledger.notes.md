# v_hyp_ops43 r43-ops-ledger notes
- 16:24Z start: verify poll.log error blocks + runtime_ledger L_hi claim
- 16:25Z poll.log grep: error headers 2026-09-29T15:19:43Z / 15:31:24Z / 15:43:04Z, each 3x '[empty stdout, rc=1' SSLEOFError, no rows -> 3 blocks confirmed (poll.log l.32101/32103/32105).
- CONTEXT.md l.4670 (15:59Z entry) names only 15:31:24Z and 15:43:04Z -> wording omission confirmed; cosmetic.
- tools/runtime_ledger.py ledger_entry(): empty polls go to `empties`, reset by any later PENDING row; failed_attempts slack (210 s each) only applied on the first COMPLETE/ERROR header. Error blocks before last_pending cannot affect L_lo/L_hi.
- Re-ran ledger to scratchpad r43v (0 Kaggle calls): exp89t family safetail_ci (auto, also in real ledger.md l.20), last_pending 16:24:52Z, lo_h 7.41, empty_between [], gate 10.2 h open.
- Arithmetic: 16:04:47-09:00:17 = 7.075 h; 18:20:00-09:00:17 = 9.329 h; +420 s = 9.446 h. Matches the finding.
- Residual (not a defect): if a future error streak straddles the result, L_hi inflates conservatively (header of first COMPLETE); T7/10.2 h gate at 19:12:17Z is by design.
- Verdict: finding is correct, action 'none' correct; no value/feasibility claim to refute (ops recheck only).
