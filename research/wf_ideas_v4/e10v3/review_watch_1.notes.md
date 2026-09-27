# Review 1 of the E10 v3 hourly watch loop (lens: safety and rule fit)

- 2026-09-27T11:20Z start. Read experiments/lb_poll/e10_watch_loop.py, run_e10_watch_loop.sh, the tools/e10_snapshot.py
  diff (main() -> take_snapshot), tests/test_e10_watch_loop.py, build_watch.notes.md / .json, CONTEXT 'USER INSTRUCTION =
  E10 v3' (27 Sep 11:08Z) and ladder_watch.poller_wait_s / read_poll_headers.
- Rule fit: the loop only detects. It never builds, pushes or submits, and it cannot reach a final. Signal (a) (any
  ref above HF v3 at 0.953 in the scoreDescending top-20, plus HF v3's own re-run) covers every public notebook that could
  score >= 0.955. Such a notebook must sort above 0.953. Ties at 0.953/0.954 give false positives only (the safe
  direction). The trigger itself (own public score >= 0.955) stays a manual look, since the kernel API has no score. Fine.
- Read-only guard: the args after `-m kaggle` must equal an e10_snapshot query or be LB_ARGS plus one temp folder. submit,
  push, pull, output and other list args raise before a subprocess starts (tested). The e10_snapshot refactor keeps main()
  behaviour (19/19). No kernel or builder file is touched, and no tool reads e10_watch except ladder_watch --s0 (a fixed
  file).
- BUG FIXED: run_once advanced the 'good' kernel lists and saved the state BEFORE writing the signal lines and the jsonl.
  If that write failed (disk error, or a kill between save_state and the write), run() caught it, saved the advanced
  state, and the change never signalled again. A missed (a) signal would silently skip the E10 v3 'verbatim fast' step.
  Now the good lists advance and the state is saved only after the RUN/INFO/SIGNAL lines and the jsonl are written. A
  failure repeats the signal next run, and a duplicate is harmless. New test
  test_a_failed_signal_write_repeats_the_signal_next_run fails on the HEAD (9cdc047) version (checked in the scratchpad)
  and passes now. tests/test_e10_watch_loop.py: 33 passed.
- Full suite: 438 passed plus 1 transient failure (test_si_builder::test_changed_config_knob_still_builds).
  tools/build_probe_kernel.py and tests/test_si_builder.py were being edited by another agent during the run (mtimes
  11:32-11:33Z). A re-run of test_si_builder + test_safetail + test_secswap (the finals-hash tests) gives 66 passed.
- Not changed (open for the main session):
  1. END = 29 Sep 12:00Z, but the deadline is 23:59Z. A verbatim copy with ~9.5 h runtime could still score if it is
     pushed by ~13:30Z. The main session may pass --end 2026-09-29T13:30Z if it wants the extra window. The default is
     conservative.
  2. Detection latency is up to 60 min (up to 120 min after 429-cut runs). This is the API-budget trade-off; `--once` can
     be run by hand at any time.
  3. The commit must include tools/e10_snapshot.py (take_snapshot) together with the loop. HEAD's loop imports it (as the
     builder noted). The loop fix in this review is also uncommitted.
  4. A corrupt watch_loop_state.json makes the wrapper restart every 120 s with no Kaggle calls and no signals. Check
     watch_loop.stdout.log for '=== restart' lines after starting it.
