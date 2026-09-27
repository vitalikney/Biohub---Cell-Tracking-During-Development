# v_plancheck_pc17-02 notes (skeptic, value + feasibility)
- 2026-09-27 11:12Z: no prior JSON answer existed; started fresh.
- CONTEXT.md l.2903-2905 R16-A1 (4): the letter window is judged against the "last poll.log header" at the time the letter is logged. The gap is real: poll.log headers 10:51:07Z -> 11:01:09Z -> 11:11:11Z (600 s cadence).
- OVERTAKEN BY EVENTS: the class-C letter "я бы за вариант б) топил" is logged at 2026-09-27 11:09:39 UTC (CONTEXT, commit 659cef3, 14:09:39+03:00) and quotes header 11:01:09Z with both refs PENDING.
- poll.log l.13745 header 11:11:11Z: 56598763 and 56598765 both still PENDING (l.13748/13750). So the header BEFORE and the header AFTER the letter both show PENDING, and the letter passes even the proposed tightened bracket rule.
- R16-A1 (5) variant clause: the variant (b) arrived in the same letter, and the partner defaults to #37 (exp70b is not named). Nothing is pending in the gap.
- Value: a label only; no effect on private LB, finals or any file. Residual use: only if the user sends an amended letter (e.g. switches to (c) or names exp70b) before the terminal header. Adding a new rule now, after the letter, is itself a post-letter rule change; a plain factual note is cleaner.
