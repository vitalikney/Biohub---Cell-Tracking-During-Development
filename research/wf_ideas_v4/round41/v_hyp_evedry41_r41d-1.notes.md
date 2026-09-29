# R41D-1 verifier notes (2026-09-29T14:28:01Z)
- 14:28Z: ps -ef: cygwin 12542 (winpid 36816) = 'bash scratchpad/pre_exp89t.sh', started 13:53:43 MSK (10:53:43Z), live sleep child 35396. ALIVE.
- Script: T=date -u -d 2026-09-29T17:40:00Z (UTC, not MSK) -> fires 17:40Z; skips only if poll.log newest non-error block shows 56669888 COMPLETE/ERROR (exp89t read expected ~18:17-18:29Z, so it will NOT skip); then up to 2x 'python tools/uptest.py save pre_exp89t' (kaggle competitions leaderboard -d), 300 s apart.
- CONTEXT l.4614-4615 (13:34Z decision B): 'the 17:40Z pre_exp89t save job was CANCELLED'. l.4633 (13:58Z R40-A3): 18:37Z card uses --lb post_exp89t else e10_20260929T1141Z '(pre_exp89t was cancelled)'. Log and process table disagree -> finding confirmed.
- Consumers: mk_card_1837.py has argparse default --lb pre_exp89t (l.155) but the CONTEXT recipe always passes --lb explicitly; no other armed script reads _lb/pre_exp89t. Killing loses nothing decision-relevant (decision B: 0.959 keeps exp87a whatever UP says).
- HAZARD: cygwin 12544 (winpid 3028) = manual_admit.sh, started the SAME second 13:53:43 MSK -> must not be killed. Kill only 12542 / Stop-Process 36816.
- Also in round41/scan_plancheck.json (same finding independently).
