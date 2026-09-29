# v_hyp_readscard_r36h-1 notes (round 36)
- 2026-09-29T08:23Z start; no prior json.
- CONTEXT.md l.4404-4415 '2026-09-29 08:19 UTC, A-M2 RULE (a) (user choice in chat, 08:1xZ)': exp89s is sent iff exp89r COMPLETE, no ERROR, display >= 0.958 with L_hi <= 10.2 h (or >= 0.959 with L_hi <= 10.75 h, GAP RULE v2), latest the 11:00Z header, cutoff 11:30Z; else UNUSED. Commit 2fdf387 (11:19 MSK) 'A-M2 rule (a): exp89s if exp89r >= 0.958 (pre-score)'.
- => R36H-1's proposed amendment (d_R in {0.958, 0.959} -> exp89s) is ALREADY the logged rule, by the user's own choice, before exp89r's header (08:18:17Z header shows 56656147 PENDING). The question it wants to ask is already answered; asking again = noise to the user and a risk of a second, conflicting log line.
- Differences vs logged rule (the logged one governs): admit window is 'latest the 11:00Z header' + L_hi gates (10.2 h for 0.958, 10.75 h for 0.959), not '<= 10:50:28Z'; R36H-1's 'd_R >= 0.960 already sends it under 02:53Z (1)' is stale (02:53Z (1) superseded by 08:19Z).
- CONTEXT 08:23Z: exp89t (K + DIS + CI) built, dummy pushed 08:22:49Z; slot plan pending user yes: slot 1 -> exp89t, slot 2 -> A-M2 rule (a). exp89t removes R36H-1's own CAVEAT (no CI in finals) if the user takes it; with exp89t in play exp89s's marginal value is lower still (DIS already read on the CI base).
- Value: EV claimed +0.00005 private (0-3 ranks); DIS inferred from four rounded displays (+-0.002), so the gain is within rounding noise; not a reason to re-ask anyway.
- 08:26Z final JSON written (refuted: superseded by 08:19Z rule (a)).
