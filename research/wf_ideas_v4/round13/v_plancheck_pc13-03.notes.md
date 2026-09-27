# PC13-03 notes 2026-09-27T01:14:47Z
- 01:18Z: checked sources. lb_poll.py (35 lines) calls only `competitions submissions`, sleep 600 s -> no LB download (confirmed).
  ladder_wait.py: not tracked in git (git ls-files). R12-A5 (round12/report.json): only the browser agent runs e10_snapshot.
- r_ladder.json L5: POSITIVE = single displays >=0.955, or 0.954 + team moves up inside the 0.954 block; read "at the first COMPLETE poll". No tool, no attribution rule (confirmed).
- Snapshots: our row rank 210 (1620Z, 1701Z) -> 217 (2001Z) -> 229 (2246Z), Score 0.954, SubmissionCount 40, LastSubmissionDate 2026-09-26 00:02:18 in all four.
  => SubmissionCount counts only SCORED subs (stayed 40 at 22:46Z with probes 39-41 pending); LastSubmissionDate = latest SCORED sub (00:02:18 = #38 twin, 0.953), NOT the best one.
  => our own LB row tells which score entered (count +1, date = that ref's submit time) -> attribution and LB-freshness check from the LB alone.
- LB CSV Score is 3 dp (0.954), so only rank order carries the sub-0.001 signal.
- poll.log 01:09:26Z: 39/40/41/42 PENDING. 39 at 21:15:23Z, 40 at 21:17:47Z (144 s). K2 latencies 7.36-7.54 h -> 39 ~04:37-04:48Z, 40 ~04:40-04:50Z, 41 ~05:00-05:11Z, 42 ~07:27-07:38Z. With 10-min polls, P(39 & 40 in same poll) ~0.75.
- Gaps in the finding: CLI needs the competition slug; zip name is fixed (overwritten) -> timestamped folder; LB may lag submission status -> freshness check; later probes move the team only if they beat the RUNNING best (max of K2 and earlier ladder scores), so a no-move is never NEGATIVE and a move is a sufficient (strict) positive.
- Value: only picks the 08:00Z informed combos (L5); finals change only via L9 display >=0.955. Cost ~5-8 LB downloads, a CONTEXT paragraph. Not a mechanism, R8 not touched.
