# Round 34 scan_recheck notes (started 2026-09-29 05:15 UTC)
- 05:15Z: no scan_recheck.json in round34 -> fresh run. Read CONTEXT tail (l.4043-4363), all rounds 2-33 recheck summaries (~100 items). R32-PI/R33-PI: lens saturated; suggestion = check card v5 claims against night reads.
- 05:20Z: poll header 05:04:36Z: 56657612 (exp89p), 56656157 (exp75), 56656147 (exp89r) all PENDING. 0 Kaggle calls by me.
- 05:25Z: card v5 (round29/finals_card_v5_ru.md l.47) says the pair model was computed only for V_pub = exp85a ("не пересчитывали"). But scratchpad r26/mc26_grid.txt l.105-219 already has VPUB=exp87a rows (28 Sep): base {exp87a,exp75} bronze 0.821 vs {exp87a,#37} 0.787; #37 ahead only at CI_SD >= 0.0015.
- 05:30Z: mc26 re-run (scratchpad r34/mc34_vpub87a.txt, mc34_exp89u.txt, mc34_allpartners.txt), VPUB=exp87a, CI prior revised per R28-RC-C (mu 0.0002, sd 0.001-0.0015):
  P3 {exp87a,#37} bronze 0.751-0.783; P2 {exp87a,exp75} 0.732-0.797 (P2 > P3 only at CI_MU >= 0.0004 & sd 0.001); {exp87a,exp89u} 0.813-0.838 (best in 9/12 grid runs + 6/6 all-partner runs).
  exp89u loses only when K_MU <= 0 (0.653 vs 0.695) or K_MU 0.0003 + RHO 0.5 (0.669 vs 0.700); ties at K_MU 0.0003 (0.717 vs 0.715). Break-even K private mean ~ +0.0003 (prior N(+0.0009, 0.0012)).
  JT pair {exp87a,exp85a} below P3 on bronze in 6/6 revised-prior runs (0.629-0.754 vs 0.709-0.783) -> rejection upheld (except CMODE=norm where it ties/leads).
  Old exp89u rejection: round26/report.json l.43 'dominated by exp75 as a partner in all 15 mc26 runs' = mc26_grid4 with VPUB exp85a/exp89q/exp89s (non-CI). Since 21:45Z V_pub = exp87a (CI) -> ordering flips.
- exp89u build recipe (round21 build_env_git_bash): B + KB + '--set DIVINS_CAP=4 --set DIVINS_FRAME_CAP=1' + JT ('--set ILP_DIVISION_WEIGHT=0.4 --set READMIT_MIN_SCORE=0.94'); not built yet (no experiments/exp89u*).
- 05:35Z: dummy-clip GT lab (scratchpad r26/dummy_lab_summary.json): exp85a - exp70g (= K) all +0.0013 (44b6 -0.0011, 6bba +0.0014; TP +2, FP -2, FN -2) -> 2 edges, sanity only, does not pin the K private prior that decides exp89u.
- exp89u dummy gate expectations: nodes == exp85a dummy 122,328 (insertion never changes nodes; READMIT 0.94 adds +1,076 over #37's 121,252), forks ~79 (+-3; #37 75 + ~4 from K), edges ~ exp85a 118,137 minus the cap-6-only insertions (~6); no 'Secondary SHA256: 7029fe69', no COORDINJECT; integer z/y/x; RULE v2.1 non-CI reference = #37/exp58 dummy.
- Picked: RC-A exp89u partner (revived conditionally), RC-B R25 rule (b) / card model line (upheld as near-equal, numbers stale), RC-C JT pair {exp87a, exp85a} (upheld).
- 05:22Z: wrote round34/scan_recheck.json (3 rechecks + 1 plan issue).
