# PC19-10 verification notes (2026-09-27 ~18:13-18:25Z)
- CONTEXT.md (3090 lines): last RESUME POINT = l.2599 "2026-09-26 22:46 UTC". CONFIRMED stale. It still says E10 v1 >= 0.956 / v2 pending, retrain needs a yes, R8 cap 02:00Z 29 Sep, pair = insertion hedge. All of these are superseded by the 27 Sep entries: 11:08Z E10 v3, 11:09:39Z class-C letter (b), 11:11:40Z exp71 yes, 11:14/11:16Z aggressive mode, 12:01/12:12Z R8 record, 16:08Z card + rebase.
- round18/REPORT.md l.63/79: R18-A2 (RESUME POINT, local-time timers, MEMORY, fb_ins35 copy) marked "now". Not done: there is no RESUME POINT after 22:46Z 26 Sep.
- MEMORY.md (mtime 27 Sep 01:46 local) says "E10 port rule proposed". project-lb-probe-approval.md says "E10 v2 pending", "retraining NOT covered", "R8 cap 02:00Z". CONFIRMED stale.
- CronList (session): 012fa6dd, 328f7392, 18ff4796 (finals checks), bb224de9 (final LB), 2e87e414 (E10 P1, 3-hourly), plus 5b23a3ed/54a8f20d/cdd738f1, one-shots for 27 Sep 04:21-06:31Z that are past but still listed. There is NO cron for the 45/46 reads or for 00:03/00:05Z.
- The actual waiters are Bash background loops (Win32_Process):
  PID 34616/12628 (started 20:31 local = 17:31Z): waits for 56606948 (45) COMPLETE|ERROR in the last poll.log block. There is NO waiter for 56611472 (46).
  PID 18920 (14:37Z): waits for 202609280005, then only echoes "00:05 UTC 28 Sep: submit time (exp72, exp75, ...)". That label is stale vs the 16:08Z card and 17:21Z entry (exp76a/exp76d). It does not submit.
  PID 33896/25052 (17:31Z): round-20 waiter at 20:00Z.
  PID 10648 (12:44Z): waits for E10 SIGNAL in watch_loop.log.
  PID 20052: lb_poll.py; PID 10120: e10_watch_loop.py (RUN 6 17:45Z, 0 signals).
  None of these ids or PIDs appear in CONTEXT (timer entries end at l.2786, 02:29Z; l.2970 mentions 2e87e414 only).
- poll.log header 18:04:40Z: 45 (56606948) and 46 (56611472) are both PENDING. 45's 8.0 h mark is 19:15Z, so a RESUME POINT written now lands before the 45 read.
- Value: continuity only, 0 LB effect. The risk is real: if the session crashes or compacts, the Bash waiters and session crons die, and a fresh session reads a stale MEMORY plus the 22:46Z block. It can still reconstruct the state from the dated entries after it (~490 lines), but it could misapply E10 v1 or the retrain "needs yes" rule. Feasibility: a CONTEXT append plus a memory edit, ~10 min. No mechanism, no R1-R10 impact.
