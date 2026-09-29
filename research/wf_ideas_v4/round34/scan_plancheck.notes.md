# Round 34 plancheck notes (2026-09-29T05:13:49Z)
- 05:20Z: e10 20260929T0441Z + 0513Z: no kernel change; best public notebook 0.953; we #133, count 53, 18/22 of 0.959 block; P2 largest group 0. feed_loop last 03:58Z 0 new. No E10 trigger, nothing disclosed.
- 05:20Z: poll header 05:14:38Z; 3 night refs PENDING; watchers 16292 (any), 1760 (56656147), 17532 (56656157) alive; timers 06:07..00:07 alive; AC 77%. card a134d5e4, checklist 2b442e87 OK.
- Idea: night-ref watchers have no LB save; exp75 (09:05-10:05) and exp89r (09:23-09:34) likely complete inside one e10 hourly gap (09:41Z snapshot) -> +2 -> MASKED UP test for exp89r at 0.959 (champion tie).
- 05:25Z: tools/uptest.py compare prints counts but does not enforce; LB SubmissionCount counts SCORED subs only (53 now with 3 pending). e10 loop hourly xx:41Z until 12:00Z (e10_watch_loop.py l.64-65); round snapshots xx:13Z not guaranteed. exp75 window 09:05-10:05Z, exp89r 09:23-09:34Z -> one gap likely -> +2 -> MASKED if exp89r shows 0.959 (champion tie, 02:02Z (2)). Fix: 0-2 LB saves at terminal headers (conditional), procedure only.
- Sam Barnett #116 (0.957->0.959, last sub 21:12Z) sits ABOVE us in the 0.959 block -> block order = unrounded score, not submit time (consistent with the UP-test design).
- Info: R33-A2 late-P '?' + Rr '+' + DIS '?' -> exp89q (same safetail 8.0 h gate family); card flag only.
- 05:31Z: wrote scan_plancheck.json (PC34-01..04)
