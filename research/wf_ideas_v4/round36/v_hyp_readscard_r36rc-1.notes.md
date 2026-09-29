# v_hyp_readscard R36RC-1 skeptic notes (2026-09-29 ~08:24Z)
- poll.log l.29356 header 07:48:12Z: 56657612 PENDING; l.29417 07:58:14Z: COMPLETE 0.956. Submit 00:46:36Z -> L in (7.026, 7.194] h. Matches finding.
- Header 08:18:17Z: 56657612 COMPLETE 0.956; 56656147 exp89r, 56656157 exp75 PENDING.
- Coding (a)-(e) re-derived: P '-' (0.956 <= 0.957); L_hi 7.19 < 8.0 (04:51Z) -> no '?'; dd = d_R - 0.957 >= 0.002 & d_R > 0.959 -> d_R >= 0.960; '-' d_R <= 0.955; '?' 0.956..0.959. All correct vs CONTEXT 02:53Z (1), 07:23Z, 07:59Z.
- BUT CONTEXT.md 2026-09-29 08:19 UTC 'A-M2 RULE (a)' (user choice in chat; commit 2fdf387 11:19 MSK) SUPERSEDES the 02:53Z (1) A-M2 function: exp89s iff exp89r COMPLETE, no ERROR, display >= 0.958 with L_hi <= 10.2 h (or >= 0.959 with L_hi <= 10.75 h); else UNUSED. Finding evidence is header 08:08:16Z, i.e. written before 08:19Z -> its action 'exp89s iff d_R >= 0.960 ... <= 10:50:28Z' is STALE and would wrongly veto exp89s at d_R 0.958/0.959.
- Also 08:23Z: exp89t (K+DIS+CI) built, dummy pushed; slot 1 -> exp89t pending user's yes. Finding does not mention it.
