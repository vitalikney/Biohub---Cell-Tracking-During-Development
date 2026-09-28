- 2026-09-27T23:27:31Z start PC21-06 recheck
- 2026-09-27T23:29Z sources: CONTEXT.md l.3075-3090 (R19-A1 (1): 46 S0 = newest count-47 download; log k), l.3246-3247 (R20-A2: k=10 at 20:02Z already logged), l.3307-3310 (46 read: S0 185549Z, no k logged).
- our row per snapshot (experiments/e10_watch/*.txt 'our team' line): 2002Z pos 11/52 (k=10), 2043Z pos 10/53 (k=9), 2143Z pos 9/53 (k=8, count 47 = newest count-47 download), 2230Z pos 9/52 (k=8, count 48, l.996), 2243Z pos 9/52 (k=8).
- recomputed UP test for 46 vs S1 = experiments/lb_poll/ladder_watch/20260927T222653Z/*.csv (#165, count 48, k=8):
  S0 185549Z (count 47, #162, k=11): 0 passed; S0 e10 2002Z (k=10): 0; 2043Z (k=9): 0; 2143Z (k=8, newest count-47): 0 passed. Code 0 stands under the actual rule.
- the finding's reasoning is backwards: teams only rise, so a NEWER S0 has a SUPERSET of teams above us -> a stale S0 can MISS an UP (false '0', which closes CI/SEC levers). No false UP is possible from either S0. Conclusion right only because verified directly.
- k at the 46 read's own S0 (185549Z) was 11, not 10.
- W1 later reads: S0 = newest download with the count just before that file's completion (49, 50 ... per 'each S1 becomes the next S0'), not always count 48.
- k trend 11 -> 8 in ~3.5 h, flat since 21:43Z; W1 cap reads ~07:30-08:00Z -> BLIND risk real but not imminent.
- 2026-09-27T23:29:29Z wrote v_plancheck_pc21-06.json (refuted=false, corrected reasoning)
