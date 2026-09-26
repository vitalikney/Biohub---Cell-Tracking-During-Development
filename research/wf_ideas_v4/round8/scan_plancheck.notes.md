# scan_plancheck notes (round 8, started 2026-09-26T10:16Z)
- 10:22Z read CONTEXT l.1570-2197 (PRE-REG v3 e/f, R1-R10, ADDENDUM L, f2, READ TABLE v1-v4, E10 PORT RULE, overlap gates 08:58, rewrite 10:15).
- 10:25Z G-A RESULT (not yet in CONTEXT): worktree-wf_b39793f6-e79-1 commit e925955 (09:51Z) experiments/overlap_reg_train/ga_train.json:
  found_at_gt_offset 43 / gt_links 62; wrong_offset 0; accepted 49 (all 44b6), accepted_cross_prefix 0, 6bba 0; missing 19 =
  13 rejected by the 5% spatial rule (frac 0.022-0.048) + 4 by the >=5-frame rule (1-4 frames) + 4 never candidates; 6 extra accepted
  44b6 pairs not GT-linked, all equal_fracs 1.0 (exact copies -> GT link list incomplete, not false positives).
  Pre-registered G-A (CONTEXT 08:58): '>= 60 of the 65 GT-linked 44b6 pairs found at the exact GT offset' -> 43/62 FAILS as written
  (even counting rejected-at-GT-offset candidates: 58/62 < 60). Denominator mismatch 65 (CONTEXT) vs 62 (splits.json; CONTEXT l.1267 '0 of 62 links').
  Work continues anyway: wt4 G-P probe (tools/overlap_probe.py, exp65, uncommitted), wt5 K6 builder patch e53b018 (exp66 built, not pushed), wt6 G-B lab tool (uncommitted).
- 10:28Z worktree branches base = old history (merge-base 869ca00); new non-merge commits to cherry-pick: e925955, bc325aa, e53b018; 05e366c already in main as 1953f18. No Co-Authored-By in new commits. wt4/wt6 work uncommitted.
- 10:30Z G-P probe (wt4 tools/overlap_probe.py): overlap -> raise RuntimeError -> 'Notebook Threw Exception'; failure inside try -> no CSV ('CSV Not Found').
  But exceptions OUTSIDE the try (module-writing cell, write_csv on the 'csv' path, OOM/dead kernel) also give 'Threw Exception' -> false 'overlap'.
  CPU notebook (enable_gpu false), spawn process pool; K6 (wt5 e53b018) uses ThreadPoolExecutor + GPU max_pool3d -> G-P latency is not a K6 timing proxy.
- 10:32Z K6 knobs: BUDGET_S 33000, MAX_S 1800 (timeout -> 'OVERLAPCONS SKIPPED (time)' -> K6 == K2 silently). G-A local: 0.1612 s/frame/worker, 199 videos 813 s with 4 procs (~19.9k frames).
  Hidden ~10k-20k frames (step-0 N<=106 clips; Data page 'approximately the same size as the training dataset') -> 1,600-3,200 s if GIL-bound.
- 10:33Z visible test = 44b6_0113de3b, 44b6_0b24845f, 6bba_05b6850b, 6bba_05db0fb1: no pair among them -> dummy exercises only the no-op path.
- 10:34Z tools/dummy_gates.py: no K6 mode; hard-fail list (l.107) lacks 'OVERLAPCONS FAILED'/'SKIPPED'.
- 10:35Z wt6 tools/overlap_lab.py: PRIMARY ins35_splice vs ins35 decides (good); d44 uses a custom 'every event once' division weighting; plain official score reported alongside. Pre-reg says 'official metric'.
- 10:36Z R4 (node-set changers: delta 0/+0.001 -> F2 candidate only) + f2 ('an R4 F2 candidate does not displace the twin') vs G-LB (K6 replaces K2 at public >= 0.954): conflict, no precedence line.
- 10:37Z E10 P6 pair {port, K2 #37} undefined if K6 adopted.
- 10:38Z exp64 lab kernels a/b status RUNNING (kaggle kernels status, read-only) at 10:24Z; pushed 09:12Z.
- 10:38Z poller alive (PID 20052), last header 10:24:52Z.
- 10:39Z PRE-REG v3 user decision (7) (CONTEXT l.1583) + R9 still list overlap consensus as refused and ban N2-type hidden-test probes; no amendment line recorded (08:49/08:58/09:10 entries only).
- 10:40Z MEMORY.md pointer says latest RESUME POINT 25 Sep 10:20 UTC (stale; latest 26 Sep 09:03). 09:03 RESUME POINT has TICK placeholder unfilled and no OC line. Two dated entries sit below '## 9. Literature'.
- 10:41Z runtime_ledger.py token map has no exp66 (K6) -> family 'unknown'.
- 10:30Z scan_plancheck.json written (12 findings, valid JSON)
