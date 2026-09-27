# v_plancheck PC20-05 notes (2026-09-27 ~20:40Z)
- No prior v_plancheck_pc20-05.json -> fresh run.
- CONTEXT.md 3237 lines; last RESUME POINT = l.2599 (26 Sep 22:46Z). Confirmed. It says "E10: v1 IN FORCE (>= 0.956)", L9 pair rule, exp70g dropped, retrain blocked -> all superseded (11:08Z E10 v3, 11:09:39Z class-C letter (b), 11:11:40Z Q1/Q2 yes, 11:14/11:16Z aggressive mode, 18:19Z N2 yes, 18:56Z 45 = 0.956, 19:10:58Z user picks finals on 29 Sep).
- No "R8 coverage" string in CONTEXT.md (grep 0). PC19-11 action text: research/wf_ideas_v4/round19/report.json l.50.
- Recurrence: RESUME POINT refresh was an action in R16-A6, R17-A7, R18-A2, R19-A5 (REPORT.md tables) - never executed (4 rounds).
- MEMORY project-lb-probe-approval.md: modified 25 Sep; description "E10 v1 in force; retrain needs explicit yes"; body ends "E10 v2 pending until 27 Sep 12:00". Stale on E10 v3, Q1/Q2/N2 yes, class-C letter, user-picks-finals-29-Sep.
- Mitigation that exists: MEMORY pointer says read last RESUME POINT + every dated entry after it -> a new session still reaches l.2600-3237, so info is not lost, only scattered and self-contradictory (E10 thresholds 0.955/0.956/0.957 in different lines).
- Precision checks on the proposed text:
  * "E10 v3 until 29 Sep 12:00Z" = END of experiments/lb_poll/e10_watch_loop.py (l.8), NOT a user-set expiry (11:08Z instruction has none). RESUME POINT must word it as "watch loop runs until 29 Sep 12:00Z", not as a rule end.
  * Trigger >= 0.957 = "better than ours" applied to our best 0.956 (scan_plancheck PC20 E10 item); the 11:08Z text says >= 0.955 -> RP should state the derivation, not a new threshold.
  * Rank: #162 at 18:55Z (CONTEXT l.3196), #163 at 20:02Z (e10_watch/20260927T2002Z.txt per round-20 scan). 18:56Z entry's "113 TeamIds" corrected by round 20 to 127 with the pre-registered S0 -> use the corrected count or omit.
  * One slot held for E10 v3 "until 12:00Z" in read table v2 (l.3148) = 28 Sep 12:00Z.
- No Kaggle call, no mechanism, no rule change -> R1-R10 not engaged; feasibility trivial (text append + MEMORY edit by main session).
