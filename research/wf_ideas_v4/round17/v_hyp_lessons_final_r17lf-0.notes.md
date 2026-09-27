## 2026-09-27 11:14Z verifier start (R17LF-0 plan-issue: nothing reaches R8)
- 11:15Z: CONTEXT.md tail (2960 lines) has 4 entries AFTER the scan's "last entry 09:15Z": 11:08Z USER INSTRUCTION E10 v3 (supersedes E10 v1/v2, lifts R8 for ports; commit 61e0737), 11:09:39Z class-C letter option (b) (659cef3), 11:11:40Z user YES exp71 push + exp72 submit, R8 lifted for exp72 (5bce47f), 11:12Z exp71 PUSHED 11:11:50Z (d1ccc85).
- So R17LF-0 premises "no user letter since ~07:45Z" and "no build/submit" are stale; action "log 'E10 v2 lapsed' at 12:00Z" is misleading (E10 v2 superseded, not lapsed; E10 v3 is not bound by R8).
- Narrow core still true: no NEW research mechanism (other than the user-named items) reaches R8; I-320 / I-345 confirm (IDEAS.md l.29).
- poll.log headers: 11:01:09Z, 11:11:11Z (43/44 terminal read trigger per R16-A1 (3)).
