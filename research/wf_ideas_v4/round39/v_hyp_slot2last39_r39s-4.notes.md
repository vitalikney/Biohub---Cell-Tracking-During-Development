# v_hyp_slot2last39 R39S-4 skeptic notes
- 2026-09-29 11:24Z start; no prior json. 0 Kaggle calls (local files only).
- round38/report.json R38-A3: 'ONLY IF THE USER SAYS YES TO A SLOT-2 FILE at 11:50-12:00Z ... void if slot 2 stays UNUSED (the logged default)'. Confirmed.
- CONTEXT 10:54Z entry (l.4509-4533): '(A3) Only on a slot-2 yes (void otherwise)'; A5 T3 = count S0 + 1 with exp89t the only newly scored ref. 11:10Z timer log: A-M2 UNUSED, 12:00Z hold governs slot 2. No slot-2 submit in _night_subs.csv / poll.log as of 11:24Z.
- Timing check: non-CI L (7.03, 7.19] h -> 12:00Z submit completes 19:02-19:11Z (+queue) ; exp89t T0 09:00:17Z, 10.2 h = 19:12:17Z, 10.75 h = 19:45:17Z. Claim arithmetically right.
- Residual gap: A3 is keyed only on a yes at 11:50-12:00Z. R38-A2(d) E10-after-11:30Z path could send a slot-2 file later; a non-CI file submitted before ~12:42Z (19:45:17Z - 7.03 h) could still complete inside exp89t's tail window. Needs a flag (P small; no genuine biohub notebook > 0.953, e10_watch 1110Z no change) + dummy 35-45 min -> realistically submit >= ~12:15Z. Tiny-probability edge; fix = one-line: A3 arming applies to ANY slot-2 submit before 12:42Z.
- Value: zero score impact; bookkeeping. Must not be cited as a reason for UNUSED (decision rests on exp89s DIS ~0 / no gated candidate).
