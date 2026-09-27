# PC17-03 verification notes (blanket-yes ambiguity)
- 2026-09-27 11:12Z: no prior v_plancheck_pc17-03.json. Read CONTEXT.md l.2840-2957.
- CONTEXT l.2926-2932: USER LETTER 11:09:39Z verbatim "я бы за вариант б) топил", answering a question whose own text defined (b) as {она, #37}. Logged pre-score (poll.log header 11:01:09Z, both 56598763/56598765 PENDING). Commit 659cef3.
- CONTEXT l.2933-2937: 11:11:40Z "запускай" = Q1/Q2 yes (exp71/exp72); Q3 not answered. Commit 5bce47f.
- No blanket yes arrived; no exp70b-as-final letter logged (grep exp70b: last user-related mention is l.2932 'the user did not name exp70b').
- poll.log header 11:11:11Z: 43/44 still PENDING.
- Premise of the finding (a blanket yes) is overtaken by events: letters arrived specifically. The (b) partner = #37 was chosen by the user in the question text itself, so no 'silent drop' of exp70b (no exp70b yes exists).
- Residual: a later exp70b yes before the read is already covered by R16-A1 (2) (both letters before the read -> one re-tick after the read); an exp70b yes after a V*_C {V*_C,#37} is a collision -> R16-A1 (1) collision clause (push facts, user chooses). No new rule needed; adding one now would be a post-letter rule edit.
- Verdict: refuted (moot). Gain ~0.
