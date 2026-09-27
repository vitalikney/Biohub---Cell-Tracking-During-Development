# E10 v3 hourly watch loop (build notes)

- 2026-09-27T11:12Z start. Read CONTEXT 'USER INSTRUCTION = E10 v3' (27 Sep 11:08Z), tools/e10_snapshot.py,
  experiments/lb_poll/ladder_watch.py (+ run_ladder_watch.sh), lb_poll.py. Backtest of the 8 snapshots in
  experiments/e10_watch (26 Sep 16:20Z .. 27 Sep 11:01Z): scoreDescending top-6 order identical in all 8 (HF v3
  raunakdey07/biohub-harmonic-fusion-v3 at pos 1, amanatar/optimized pos 2, kunaldesale pos 3, x138 pos 4), so a
  position-based (a) rule has no tie-jitter noise in this history. User lists: amanatar re-ran optimized-biohub-max-score
  (26 Sep 13:18 -> 27 Sep 01:39) and a non-Biohub kernel (rsna-knee-super-ensemble-0920, 27 Sep 02:12): the second is
  noise for E10, so amanatar kernels count only when Biohub-related; anvithpothula / thtennant count for any kernel.
- 2026-09-27T11:23Z tools/e10_snapshot.py: main() body moved into take_snapshot(out_dir, started, runner, sleep,
  attempts, dry) (same file, DIFF, prints and exit code; tests/test_e10_snapshot.py 19/19). The loop calls it in-process
  with a gated runner, so the only Kaggle commands are e10_snapshot's queries() + its LB download (guard raises on
  anything else before a subprocess starts).
- experiments/lb_poll/e10_watch_loop.py written. Signals (a) above top ref HF v3 in scoreDescending top-20 (+ the top
  ref's own re-run; anchor fallback when HF v3 leaves the list), (b) new ref in top-5, (c) new lastRunTime for
  anvithpothula / thtennant (any kernel) and amanatar (Biohub-related only). Transition-based vs the last good list
  (state file; else newest good list per key in experiments/e10_watch/*.txt), so a signal prints once per change.
  Gate per call: PAUSE files (experiments/e10_watch/PAUSE, experiments/lb_poll/ladder_watch/PAUSE), +-60 s of lb_poll's
  last/next poll (ladder_watch.poller_wait_s on poll.log). 429: 60 s back-off x2, then the run is cut (no more calls)
  and the next run is delayed +30 min per consecutive cut run (cap +60). 429 in stdout of rc 0 needs the HTTP phrase
  (a CSV row can carry 429 votes).
- Backtest on the real snapshots: only 26 Sep 22:46Z -> 27 Sep 01:47Z signals ((c) amanatar/optimized-biohub-max-score
  re-run 26 Sep 13:18 -> 27 Sep 01:39); rsna-knee re-run = INFO; all other pairs silent. Dry run on the 11:01Z snapshot
  outputs (scratchpad) = baseline, 8/8 OK; + a synthetic heir at pos 1 -> one line 'E10 SIGNAL: newbie/biohub-x138-heir
  (a,b) ...'. Scratchpad removed.
- tests/test_e10_watch_loop.py 32 tests (guard, 429 parsing, rules a/b/c, hourly loop to END with one signal, restart
  resume, disk baseline, poller guard, PAUSE, 429 cut + delay, dry-run CLI, restart script, real-history backtest).
  Full suite: 412 passed (343 before + 32 here + other agents' new tests).
- NOTE: the main session's commit 9cdc047 already contains experiments/lb_poll/e10_watch_loop.py (picked up mid-build;
  same bytes as now), but tools/e10_snapshot.py (take_snapshot) is still uncommitted: the loop needs it; commit both.
  Not started (main session starts: bash experiments/lb_poll/run_e10_watch_loop.sh in the background).
