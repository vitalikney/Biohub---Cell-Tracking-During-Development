# v_browser_r18-cadence-answer notes (2026-09-27 ~15:35Z)
- Oldest file mtime per round (local +0300 -> UTC): r2 25Sep 19:51Z, r3 22:22Z, r4 26Sep 00:53Z, r5 03:20Z, r6 05:49Z, r7 08:27Z, r8 10:23Z, r9 12:51Z, r10 15:20Z, r11 17:04Z, r12 20:03Z, r13 22:49Z, r14 27Sep 01:52Z, r15 05:37Z, r16 08:36Z, r17 11:05Z, r18 15:20Z (scan_browser.json 18:20:36+0300; finding said 15:17Z, 3 min off, immaterial).
- Gaps r2..r18 (h): 2.5,2.5,2.45,2.5,2.6,1.9,2.45,2.5,1.7,3.0,2.75,3.05,3.75,3.0,2.5,4.25. Median ~2.5 h over all rounds; ~3 h over r10-r18. Cadence has drifted longer overnight/today.
- Caveat: mtimes are when first scan agent WROTE output, i.e. a few min after round start; proxy only, but consistent across rounds.
- E10 watch: experiments/lb_poll/e10_watch_loop.py INTERVAL_S=3600, END 29 Sep 12:00Z; watch_loop.log runs 12:43:55Z, 13:43:57Z, 14:44:10Z -> hourly confirmed.
- Verdict: finding confirmed (informational, no pipeline change, no rule R1-R10 impact).
