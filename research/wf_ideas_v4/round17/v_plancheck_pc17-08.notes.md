# v_plancheck_pc17-08 notes (2026-09-27T11:12:27Z)
- 11:13Z (date -u) read CONTEXT l.2780-2940; poll.log headers 11:01:09Z and 11:11:11Z both show 56598763/56598765 PENDING, 56592350 COMPLETE 0.954.
- Slot count checks out: 42 submitted 00:05:50Z, 43 05:28:13Z, 44 05:28:22Z -> 3 used on 27 Sep, 2 left (5/day).
- scan_plancheck.json mtime 14:06 local = 11:06Z, so PC17-08 was written BEFORE three user messages:
  CONTEXT 11:08 (E10 v3: supersedes E10 v1/v2, lifts R8 for that item, A verbatim + B copy+SI or C port, i.e. up to 2 submits per trigger),
  11:09:39 (class-C letter (b), pre-registered; the 11:01:09Z header was quoted),
  11:11:40 (Q1 yes exp71 pushed 11:11:50Z; Q2 yes exp72 submit, R8 lifted for it; expected score 22:30-23:30Z 27 Sep).
- Stale points in PC17-08: (1) R16-A3 text 'R8 passed, E10 v2 expired' (round16/REPORT.md l.60) is now wrong or misleading, because v2 is superseded by v3 and R8 is lifted for E10 v3 and exp72.
  (2) 'FREEZE holds' is true for DC rungs, but its slot order (R15-A1 (2) l.2825) now faces live demand: exp72 (1 slot, submit ~16-17Z after exp71 ends ~15:15-15:45Z) plus E10 v3 (2 slots per trigger) against 2 slots left on 27 Sep.
  (3) The E10 v1 window (to 29 Sep 00:00Z) and the 02:00Z edge are superseded; v3 states no latest-submit edge. With 12 h runtime and ticks by 20:00Z the hard edge is ~29 Sep 08:00Z; the K2-family latency of 7.4-7.6 h allows ~12:00Z, but that leaves no ERROR retry.
  (4) R16-A7 (E10 P1 every 3 h, E10 v1) is replaced by the e10v3 hourly watch (research/wf_ideas_v4/e10v3/build_watch.notes.md, 11:12Z).
  (5) The exp71 retrain runs against the team rule 'no retraining before 29 Sep'. The user OK'd it explicitly, so it is not a re-proposal, but no deviation line is logged the way R15-A1 (1) did.
- E10 v3 trigger status: none confirmed. amanatar v6 has no public score (experiments/ext_optimized-biohub-max-score/v6_2026-09-27/NOTES.md). HF v3 = x138 clone 0.953.
