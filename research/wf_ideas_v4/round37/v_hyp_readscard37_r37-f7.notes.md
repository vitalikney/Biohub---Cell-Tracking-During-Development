# v_hyp_readscard37 R37-F7 notes (2026-09-29, skeptic check)
- ledger experiments/lb_poll/ledger.md l.22: 56656157 exp75 safetail_ci, sub 00:05:34Z, last PENDING 08:58:26Z, COMPLETE 0.955 @ 09:08:28Z, 0/0 failed CLI -> L (8.88, 9.05] h (9.048 h rounded outward). ADMIT (a), 10.2 h gate not fired.
- #37 56563521 L (7.36, 7.54] h (ledger l.38). dL = 9.05-7.54 = 1.51 h > 0.5 h; even the conservative L_lo(exp75) - L_hi(#37) = 8.88-7.54 = 1.34 h > 0.5 -> CI-RAN robust.
- L_hi 9.05 < 9.6 -> no ins-tail? footnote (partner rule v2, CONTEXT l.3966-3973; card v5 step 7).
- V_pub = exp87a 56640366 (K+CI, 0.959) -> CI file -> rule v2 (b) = R25: П2 {V_pub, exp75} only as trade; П3 {V_pub, #37} first (card v5 l.38/55/89; CONTEXT 09:09Z line l.4471-4478 matches).
- Robustness: pending exp89t (K+DIS+CI) is also CI, so even if it becomes V_pub (b) still applies. exp89r = 0.957 (SEC, CI) - not V_pub. No non-CI file pending -> branch (a) unreachable today.
- exp75 0.955 < 0.959 -> cannot be V_pub. Verdict: finding correct, info only, no action.
