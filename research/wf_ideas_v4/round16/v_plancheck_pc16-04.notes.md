# v_plancheck PC16-04 notes (round 16)
- 2026-09-27 08:45Z: no prior v_plancheck_pc16-04.json; starting.
- Source: CONTEXT.md 06:19Z entry (l.2814-2855) (3) read trigger "first poll.log header with both refs terminal", (4) V*_C needs L_hi <= 9.0 h (first COMPLETE header by 14:28:13Z / 14:28:22Z) and other rung ">= 0.954 or ERROR/unscored". No timeout anywhere; R15-A5 (round15/report.json) same, deadline text "14:28Z for the 9.0 h clause" but no trigger.
- No CONTEXT entry after 07:41Z D2 -> PC16-02 composition line not yet written; still pre-score (ledger 08:40:46Z: 56598763/56598765 PENDING, > 3.20 h).
- poll.log headers every ~10 min, drifting ~+2 s/poll: 07:30:34, ..., 08:40:46Z. Extrapolated header near 14:30 is ~14:31-14:32Z, not "14:30Z" exactly -> wording should be "first header at or after 14:28:22Z".
- Header before 14:28:22 is ~14:21Z; a ref first COMPLETE at the ~14:31 header already has L_hi > 9.0 h, so a 14:28:22Z trigger loses nothing the table would accept.
- "wait with no end" overstated: safetail deadline 9.5 h and Kaggle 12 h limit force a terminal state (COMPLETE/ERROR) by ~17:30Z unless Kaggle itself hangs; still, a fixed trigger removes the post-hoc window where the late rung's score could steer the smoothness clause.
- Residual gap: if the poll.log watcher itself stops, "the header" never comes. Add wall-clock fallback (date -u >= 14:40Z -> one ListSubmissions read, logged).
- Value: procedural only; 0 score effect; no mechanism, not R8-bound, no submit. Byte-identical/fail-soft n/a.
