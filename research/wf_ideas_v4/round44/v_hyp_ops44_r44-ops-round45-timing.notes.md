# v_hyp_ops44 r44-ops-round45-timing (skeptic), 2026-09-29 17:28-17:35Z
- 17:28Z: no earlier answer file for this task.
- The poll.log headers 15:54:45 .. 17:25:06Z are clean. The 17:25:06Z header lands where R44-PC-03 projected it (17:25:05Z), so the cadence of ~10:02.3 holds. Projected headers: 18:15:17, 18:25:19, 18:35:21Z.
- Win32_Process: timer 30820 exists (scratchpad timer.sh 2026-09-29T18:13:00Z "HOURLY RESEARCH ROUND 45 (21:13 MSK): READS-vs-CARD from local fil..."). The 18:37Z card timer is 29184, the 19:43Z one is 20960, the 21:05Z one is 24260 and the 00:07Z one is 21232.
- timer.sh only notifies the session. It does not launch the workflow by itself, so the fix is purely about how the session behaves. No kill is needed.
- Round 43 ran 16:14-16:43Z (29 min, CONTEXT 16:43Z entry). A round-45 launch at 18:13Z would end at ~18:43Z, with the applying step after the 18:37Z card.
- The READS-vs-CARD lens is already covered by r44dry/readtime.sh (scan_hyp_ops44 r44-ops-readblock). Round 45 adds ~0 before the read.
- Value on private/LB: 0. This is ops only; it protects the timing of the read push and the card before the user's 20:00Z (23:00 MSK) tick.
