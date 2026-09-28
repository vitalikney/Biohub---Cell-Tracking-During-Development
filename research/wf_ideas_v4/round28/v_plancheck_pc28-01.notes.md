# v_plancheck PC28-01 notes
- 2026-09-28T19:50:27Z start; no prior answer file. Verifying claim 'session crons never fired'.
- 2026-09-28T19:51:14Z VERIFIED: transcript has 0 prompts/enqueues with cron text for keys 'Scheduled E10 P1' (recurring 8x/day 27-29 Sep, would have fired ~15x), WATCHER LIVENESS (27 Sep 04:21/05:21/06:31Z), MORNING MESSAGE (27 Sep 07:30Z), SCHEDULED RESEARCH ROUND (12:47/15:17/17:47Z 28 Sep), PROBE 51 HARD LATEST; only CronCreate tool_use + tool_result echoes. 37 Cron calls (31 create+6 delete).
- 19:5xZ 12:47Z window: session IDLE 12:40:37Z..13:13:21Z (next event = task-notification), no cron enqueue -> cron 'aac566de 47 15,20 28 9' did not fire while idle+awake. 17:35-18:00Z: zero events at all.
- Kernel-Power (Get-WinEvent, MSK): 506 enter MS 19:51:43, 507 exit 20:40:20, 105 source change 21:07:28 (to battery), 506/507 21:18:34/21:19:06, 105 21:21:19 (AC). So 20:47 MSK = awake on AC; the 'lost to battery' message is wrong. BatteryStatus now 2 (AC).
- Workflow calls return 'launched in background' in ~1.5 s (13:18, 15:42, 19:36, 19:42Z) -> a waiter notification is not blocked by a running round.
- Entry point claude-vscode; version bump 2.1.282 -> 2.1.283 at 28 Sep 06:04:12Z = session process restart. CronList 15:40Z lists only crons created 28 Sep 10:51Z+; ~13 older crons vanished with only 6 CronDeletes -> restart wipes session-only crons, and would equally kill run_in_background waiters (children of the extension host). Live watchers all started after 06:24Z, consistent.
- Waiter list omits ddc5884d (21:05Z 29 Sep last-call notify) and 7c8c80dd (00:07Z 30 Sep post-deadline) and the 29 Sep round crons e77a3d87/1f0c4670.
- 2026-09-28T19:52:57Z final JSON written (refuted=false)
