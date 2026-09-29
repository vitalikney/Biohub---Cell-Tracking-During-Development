# v_plancheck PC36-06 notes
- 2026-09-29 08:23Z: no prior JSON. Win32_Process 13740 (created 28.09 23:12:18 local) = timer.sh 2026-09-29T08:30:00Z "M1 CI DEADLINE CHECK (11:30 MSK): if MORNING TABLE v1.1 calls for a CI M1 file and it is not yet submitted, decide now ... submit by 08:45 UTC if its dummy PASSED." - generic text confirmed.
- CONTEXT.md l.4396-4406 (07:59Z READ): 56657612 exp89p COMPLETE 0.956 at header 07:58:14Z -> P '-' -> A-M1 UNUSED.
- CONTEXT.md 02:53Z (2): manual 08:40Z waiter only if 56657612 still PENDING at the 08:30Z timer -> not triggered.
- poll.log l.29420/29481/29542: 56657612 COMPLETE 0.956 (repeated headers).
- ledger.md: no exp89l/exp89t submit lines.
- NUANCE: CONTEXT 08:23Z entry: exp89t (K + DIS 2.25 + CI) dummy pushed 08:22:49Z, proposed for the freed slot 1 (cancelled A-M1) on the user's yes, submit ~09:05Z, explicitly breaking the 08:45Z cutoff. The 08:30Z log line should also say exp89t is NOT governed by this timer (not in MORNING TABLE v1.1; user yes + dummy PASS only), so the timer's '08:45Z / dummy PASSED' clause is not read as a deadline or trigger for exp89t either.
