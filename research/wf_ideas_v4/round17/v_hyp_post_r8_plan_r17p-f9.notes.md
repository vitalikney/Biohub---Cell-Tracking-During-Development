# R17P-F9 skeptic notes (timer + poller restore card)
- 2026-09-27 11:13Z: no prior JSON. CronCreate schema: "Jobs live only in this Claude session"; `durable` "has no effect"; jobs "only fire while the REPL is idle"; recurring auto-expire 7 d (2e87e414 fine to 4 Oct).
- CronList (11:13Z): 012fa6dd 28 Sep 20:57 local, 328f7392 29 Sep 14:57, 18ff4796 29 Sep 20:57, bb224de9 30 Sep 02:27 (=29 Sep 23:27Z), 2e87e414 recurring hh:04 UTC 27-29 Sep; STALE past one-shots still listed: 5b23a3ed, 54a8f20d, cdd738f1 (27 Sep 04:21/05:21/06:31Z).
- RESUME POINT (CONTEXT l.2618) names stale ids 2f0d1fa1 / c7cd2e6b (replaced by 2e87e414 at l.2747; 65b1b746 deleted 07:41Z). A card fixes this staleness.
- Poller PID 20052 alive (started 26 Sep 02:12 local), last header 11:11:11Z; lb_poll.py = infinite loop sleep 600, no stop time. Restart recipe already at CONTEXT l.2567 (Start-Process -WorkingDirectory). W6 liveness (<15 min) already at l.2064.
- Precedent for session loss: CONTEXT l.1371, 24 Sep 11:37Z laptop freeze + power-cycle.
- Prior coverage: R11-A5 (round11/report.json) raised 'timers die with session' and asked the user for a wake mechanism; no restore card -> finding is new as a card, not as a problem.
- Gate flaw: "CronList shows every id on the card" is trivially true in this session and impossible after a restore (new ids). Use one live job per card row with matching time + action.
- 11:16Z verdict written: not refuted, with gate fix (rows by action/time, not id), deadline column, stale one-shot cleanup, E10 v3 prompt check.
