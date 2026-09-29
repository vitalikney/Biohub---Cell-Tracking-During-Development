# v_plancheck PC43-08 skeptic notes (2026-09-29 16:25Z, 19:25 MSK; 0 Kaggle calls)
- No prior v_plancheck_pc43-08.json; fresh check.
- CONTEXT.md l.4618-4626 (R40-A1, 13:58Z): observed L non-CI 6.69-7.81 h, CI 8.88-9.48 h, verbatim x138 6.29-6.46 h; P4b dummy 35-45 min (queues up to 3-4 h); finish-by-23:59Z (744250, CONTEXT 12:59Z); dummy start edges 14:10Z (L 9.0), 15:50Z (7.5), 16:50Z absolute (verbatim x138). "Default: slot 2 expires unused."
- CONTEXT l.4549 (11:54Z): user holds slot 2 in reserve only for a new public notebook, per-notebook yes (R38-A2 (d)).
- experiments/e10_watch/watch_loop.log: last RUN 47 11:42:05Z (20260929T1141Z.txt), END 12:00:00Z. Confirmed newest e10 file = 20260929T1141Z.
- Feed 15:59Z: 744250 comment only, no E10 flag (scan_recheck.json round43). Feed loop's last run ~17:29Z still pending -> after 16:50Z any flag it raises is info only.
- Nuance: 16:50Z is the last DUMMY start for a NEW file. A re-submit of an already dummy-tested, already-scored version skips the dummy (edge ~17:18Z non-CI / ~17:41Z verbatim x138), but it is a same-code rerun and adds nothing (and no such candidate exists). So "dead for any new file at 16:50Z; effectively dead" holds. The slot does not formally 'expire' until 23:59Z; wording should say "closed: no new file can finish by 23:59Z".
- Value: bookkeeping only, prevents later rounds (17:13Z, 18:13Z) re-opening a submit; zero Kaggle calls, zero risk. Not refuted.
