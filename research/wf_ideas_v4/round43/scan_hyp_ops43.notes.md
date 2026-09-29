# scan_hyp_ops43 notes (started 16:13Z)
- 16:13Z: round43 folder created; no prior scan_hyp_ops43.json.
- (1) scratchpad mk_card_1837.py sha256[:8] = a19e1bd6; `PYTHONIOENCODING=utf-8 python <SP>/mk_card_1837.py --dry-all` from repo root: rc 0, 35 lines 'ok'.
  Extra: 'T1 --disp 0.959' and 'T2 --disp 0.959 --lhi 10.30' both AssertionError ('code/disp mismatch' -> T3KEEP). A T3KEEP test run
  wrote <SP>/card_1837_T3KEEP.txt (simulated hdr 18:20Z) - DELETED by this agent at ~16:16Z so the 18:37Z step cannot mistake it. No card_1837_* file exists now.
- (2) Win32_Process: no process command line contains pre_exp89t (excluding the query itself).
- (3) Alive (creation times are local MSK): poller python lb_poll.py w37016 (28 Sep 15:41Z); manual_admit ONE chain 29032->13708->3028 (10:53:43Z; waits for 19:44:30Z);
  old exp89t watcher 29636->30864 (09:00:54Z; post_exp89t save on 0.959 only); feed stop job 24584->32220 (13:58Z; stops 20892/10924 at first feed run >= 17:20Z or 17:35Z);
  feed loop 10924/20892 alive (last run 15:59:14Z rc=0, next ~17:29Z); new-session jobs: exp89t-terminal waiter 9016 (lastok), t7_trigger 16748 (one), timers 17:13/18:13/18:37/19:43/21:05/00:07Z, feed-signal waiter 13072, power/stale watchdog 22680 (16:09Z).
  Poller newest header 2026-09-29T16:04:47Z at 16:14:12Z = 9.4 min (< 15). Note: 3 of the 'timer' processes match 'manual_admit' only because the 17:13Z timer text names it.
- (4) Win32_Battery BatteryStatus = 2 (AC), 65% at ~16:14Z (was battery 67% at 15:57Z per CONTEXT 15:59Z entry).
- (5) CONTEXT l.4607-4677 (13:34Z decision B, 13:58Z R40, 14:59Z R41, 15:59Z ops): every 0.959 mention maps to T3KEEP / exp87a stays / post_exp89t info save. No text promotes exp89t on 0.959.
- (6) poll.log error blocks: 15:19:43Z, 15:31:24Z, 15:43:04Z (3, not 2; the 15:59Z entry lists only 15:31/15:43) - each header has 3 '[empty stdout' notes and no rows.
  tools/runtime_ledger.py (run with --out/--json to scratchpad, ledger.md NOT rewritten): exp89t family safetail_ci, last_pending 16:04:47Z, lo 7.07 h, empty_between [] (reset by later PENDING polls).
  Simulated COMPLETE at 18:20Z: clean header -> L_hi 9.33 h; header with 2 failed attempts -> 9.45 h (+2x210 s). Error blocks only enter empty lists; slack applies only to the terminal header. No defect.
- Hypotheses: 16:17Z, reserve slot closed (R40-A1: absolute last dummy start 16:50Z, any file reads after the 20:00Z tick); IDEAS.md I-593..I-608 cover finals pairs; nothing new reaches R8.
