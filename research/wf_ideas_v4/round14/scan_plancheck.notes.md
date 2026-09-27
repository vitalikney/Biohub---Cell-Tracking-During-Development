# scan_plancheck round 14 notes

- 2026-09-27 01:47 UTC start. No prior scan_plancheck.json. ladder_watch.py exists.
- 01:55 UTC. R13-A1 audit: commit 3d48d35 (author+commit 2026-09-27T01:31:30Z) holds 'LADDER PRE-SCORE REGISTRATION'; its poll.log copy ends at header 01:29:31Z with 56589025/56589065/56589423/56592350 all PENDING; origin/main reflog: pushed 01:31:34Z. Latest poll 01:49:34Z still all PENDING. => registered before any score (external timestamp = GitHub push).
- ladder_watch.py committed f24ff72 (01:54:11Z) with tests/test_ladder_watch.py: 35 passed locally (3.75 s). Dry run (fake clock) OK: 62 fake calls, 3 events, co-completion equal-display -> NEU, single completion -> UP/POS, 0.953 -> NEG.
- Read-only guard: assert_read_only allows only `competitions submissions <comp> -v` and `competitions leaderboard <comp> -d -p <path>`. No submit/push path. OK.
- Parser on the real poll.log block 01:39:32Z: 29 rows, tracked = the 4 ladder refs only, freshness(40) fresh, expected_last 2026-09-26 00:02:18. RE_429 no false hit on real block.
- kaggle 2.2.4 competition_leaderboard_download -> download_file makedirs(outpath): new -p folder is created by the CLI. OK.
- LB CSV generated on demand (member timestamps == snapshot times 16:20:22, 17:01:22, 20:01:38, 22:46:23, 01:47:50).
- --s0 import of experiments/e10_watch/20260927T0147Z.txt works offline: rank 242, score 0.954, count 40, last 2026-09-26 00:02:18, 241 TeamIds above.
- lb_poll.py: header ts taken BEFORE the poll, written after; retries 3x with 30 s sleeps (429 case spans ~70-100 s after ts).
- Watcher robustness: run() catches only KeyboardInterrupt; save_state uses os.replace (Windows PermissionError if a Python reader holds state.json open) -> process dies; A-only extension is DROPPED if the watcher does not run.
- Timing: dummy runtimes e 1,464 / a 1,629 / d 1,320 / K2 1,512 / b 1,740 s (CONTEXT 21:15-21:38Z, 00:06Z). K2 L (7.36,7.54], twin (6.69,6.87]. Scaled: d could score ~04:05-04:30Z (before the 04:10 start), a ~7.9-8.0 h (8.0 h mark 05:17:47Z) -> ledger L_hi from 10-min polls may straddle 8.0 h. exp70b ~08:30-09:30Z vs HARD_CAP 09:40Z.
- E10 P1 snapshot 20260927T0147Z (browser/timer): NOT met. amanatar/optimized-biohub-max-score new run lastRun 01:39:05Z, status ERROR->RUNNING (v11?). x138 v1 COMPLETE, anvithpothula list unchanged; Anvith team 0.956 #131 (last sub 26 Sep 01:08:28). >=0.955: 214 -> 226; we #242 (16/97 in 0.954 block). Largest movers none are public notebooks.
- Inconsistency: ROUND 13 RECORD (4) plans the API SELECTED read at ~05:00Z (main-session API touch) inside the 04:10-06:45 quiet window; R13-A1 (2) names a '03:04Z timer snapshot' that does not exist (timer ran 01:47Z).
- 02:00 UTC final JSON written (10 findings).
