# v_plancheck PC6-01 notes
- 06:03Z start; no prior json
- 06:04Z verified: CONTEXT.md (2074 lines) has no OK-timing clause (grep 'late ok|ok timing|OK.*post-hoc|user decision after' = 0 hits; 'post-hoc' only in old lines). OK REQUEST entry l.2049-2051 has no timing consequence.
- poll.log last header 05:53:56Z: 56563521 / 56563534 both PENDING -> the clause can still be written pre-score. HEAD 2f6ec9d == origin/main.
- round5/report.json l.19 ok_message_ru already asked the user to answer 'ДО первого счёта' -> the rule is consistent with what the user was told; only the consequence of a late answer is missing.
- WATCHLIST W45: 'When the OK arrives, log its time against the first #37 and #38 result times. An OK given after a visible score is post-hoc' -> not in CONTEXT.
- Duplicate inside round 6: scan_hypotheses R6H-2 W1 proposes the same rule, but gates floor/row2/C4 on 'the LATER of K2 and twin' -> anti-conservative (twin=0.952 alone already reveals the floor outcome). PC6-01's 'first score of any file the item reads' is the right gate.
- Refinements: (1) poll.log header lags the Kaggle page by up to ~10 min (+210 s on a failed CLI) -> compare OK time with the LAST header where the item's files were all still PENDING, not with the first scored header. (2) A rule cannot void the user's authority: a late OK is logged 'user decision after score (post-hoc)', the strict text stays the recommendation.
- Value: score EV ~<=1e-4 (floor case needs row 3 AND twin exactly 0.952 AND a late OK); main value = no unrecorded post-hoc choice. Cost ~5 min text, 0 kernel. Deadline: first twin result ~06:15-06:30Z.
