# v_plancheck_pc33-01 notes
- 2026-09-29T04:24:35Z start; no prior json
- 04:25Z Win32_Process: PID 16292 (parent 13516, created 03:47 MSK = 00:47Z) confirmed: `until last | grep -qE "^(56656147|56656157|56657612),.*(COMPLETE|ERROR)"` -> one-shot on ANY of 3 refs. Only read watcher on the night refs.
- timer.sh due times alive (UTC): 05:13, 06:07, 07:13, 07:23, 08:13, 08:30, 09:13, 10:13, 11:10, 12:03, 13:13..18:13, 18:37, 19:43, 21:05, 30 Sep 00:07. Nothing between 09:13 and 10:13Z.
- Read windows (CONTEXT 00:06Z/00:47Z): exp89p 07:38-08:35Z (first to finish -> fires 16292), exp75 09:05-10:05Z, exp89r ~09:25-09:35Z. So exp89r's header falls in the 09:13-10:13 gap -> A-M2 decided at 10:13Z round or 11:10Z check (up to ~100 min late) unless session re-arms by habit; no logged rule (02:53Z (1) says decide at exp89r's first terminal header; freeze (6) submit at decision header).
- M2 non-CI L 7.0-7.8h: sent 09:40 -> read 16:40-17:30; sent 11:15 -> 18:15-19:03 (vs 18:37Z FINAL proposal, 19:43Z reminder, 20:00Z tick). Finding's arithmetic holds.
- Poll header 04:24:30Z: all 3 refs PENDING. Poll cadence ~10 min.
- DEFECT in proposed command: `cut -c1-220` truncates the exp89r row (266 chars) before 'SubmissionStatus.COMPLETE,<score>' -> the wake message would not show the display. Use the 16292 formatter `awk -F'SubmissionStatus.' '{print substr($1,1,50), $2}'` instead (tested: prints 'ref,submission.csv,time PENDING,,').
- Cost: 0 Kaggle calls, local grep every 120 s; duplicates harmless. No rule change, no R1-R10 conflict. Verdict: not refuted; fix the display.
- 2026-09-29T04:26:15Z wrote json (refuted=false)
