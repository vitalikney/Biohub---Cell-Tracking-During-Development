# Review 0 of the E10 v3 hourly watch loop (lens: correctness)

- 2026-09-27T11:25Z start. Read experiments/lb_poll/e10_watch_loop.py, run_e10_watch_loop.sh, the tools/e10_snapshot.py
  diff (main() -> take_snapshot), tests/test_e10_watch_loop.py, build_watch.notes.md, ladder_watch.poller_wait_s.
  Review 1 (safety lens) was running at the same time and edited the loop and tests at 11:26-11:27Z (signal-before-state
  order). I edited only after its notes were final (11:36Z) and the loop sha matched its JSON (903bbdea...).
- Refactor equivalence: HEAD vs working tools/e10_snapshot.py on the same dry-run cache (built from the 20260927T1101Z
  snapshot) with --now 2026-09-27T12:00Z and the same earlier file: snapshot file identical (except the 'CLI calls
  took N s' timing) and stdout identical (paths normalised). tests/test_e10_snapshot.py 19/19.
- Read-only: the only subprocess path is es.run_cli -> GatedRunner -> assert_read_only -> subprocess.run. The guard
  raises before any subprocess; es.run_cli catches the RuntimeError as a failed attempt (so it is logged in the
  snapshot, not fatal). No submit / push / pull / output is reachable. The LB download may write into any one folder
  given after -p (only e10_snapshot's temp folder in practice).
- Full suite 11:30Z: 437 passed + 1 failure in tests/test_trainlab.py::test_end_to_end_replay_parity (passes alone,
  20/20; other agents were running pytest / editing at the same time). The finals and ladder byte-identity tests
  (test_secswap::test_finals_and_ladder_rebuild_byte_identical: exp58, exp58t, exp58n, exp70a/b/d/e;
  test_si_builder: exp70g/j/k) passed in that run.
- Mutation run 1 (27 mutants of the loop vs its 33 tests): 19 killed, 8 survived: END check in the gate, reappearing
  ref with lastRunTime == oldest, retry sleep after the abort, live bootstrap skipping -dryrun files, prev_above = all
  refs, failed fetch overwriting the good list with None, --once when not due, sleep capped at END, PAUSE poll period.
- BUG FIXED (API burn): a state file that cannot be saved (disk full, locked file, stray watch_loop_state.tmp) made
  run()'s except path call save_state() again, crash, and the restart wrapper re-ran at once. Reproduced: 8 Kaggle calls
  every ~3 min (4 restarts x 8 calls in 9 min). Now the except path's save is best-effort and the process keeps its
  in-memory hourly schedule; same repro: 1 run per hour, no crash. Also say(): a failed watch_loop.log append is echoed
  as a WARN instead of raising (the line itself is already printed), so a log problem cannot hide a signal from stdout
  or crash the loop.
- Tests added to tests/test_e10_watch_loop.py (8): save failure neither crashes nor re-runs; log write failure still
  prints the signal; failed fetch keeps the last good list (heir signals on the next good run); live bootstrap skips
  dry-run snapshots (e10_snapshot's default out-dir is experiments/e10_watch); no call after END while a run is held
  by PAUSE; --once runs now even when not due; the sleep stops at END when the next run is later; a known kernel moving
  above HF v3 without a re-run signals (a). 41 passed.
- 2026-09-27T12:25Z mutation run 2 (30 mutants incl. undoing both fixes and review 1's order fix, vs 41 tests):
  27 killed. 3 survivors are harmless: the retry sleep after an abort and the PAUSE poll period only change timing,
  and a reappearing ref whose lastRunTime equals the list's oldest one is an equality edge case.
- Full suite 12:25Z: 483 passed, 1 skipped (includes the finals / ladder byte-identity tests; re-run alone: 4 passed).
  sha256: loop 36afdc3e..., tests 2b410907..., e10_snapshot 0377cb4c....
- State of git: the main session's commit a6ffbc9 already holds the loop WITH this review's fix (same sha 36afdc3e).
  Still uncommitted: tools/e10_snapshot.py (take_snapshot; HEAD's loop cannot import without it),
  tests/test_e10_watch_loop.py (untracked). run_e10_watch_loop.sh is tracked. Loop not started (no state/log in
  experiments/e10_watch).
- Open (not changed): (1) no single-instance lock: starting the wrapper twice doubles the calls and both write one
  state file (os.kill(pid, 0) would kill the process on Windows, so no quick PID check was added); start it once.
  (2) After a long PAUSE the run's time stays its start time, so the next run can fall due at once (8 extra calls).
  (3) END 29 Sep 12:00Z vs the 23:59Z deadline (same as review 1): --end 2026-09-29T13:30Z keeps the window open for a
  ~9.5 h verbatim copy. (4) Tie jitter at pos 5/6 or around HF v3 would repeat (a)/(b) signals (the order was stable
  in all 8 snapshots so far). Scratch removed; no Kaggle call, submit, push or commit.
