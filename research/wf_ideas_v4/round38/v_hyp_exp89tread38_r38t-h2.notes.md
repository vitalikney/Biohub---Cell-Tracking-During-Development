# v_hyp_exp89tread38 R38T-H2 (S1 re-saves until 19:50Z) - skeptic notes
- 2026-09-29 10:28Z: no prior JSON. Sources: CONTEXT.md l.4381-4393 (R35-A1 one lag re-save), l.4490-4497 (R37-A3 S0/S1 for exp89t),
  l.3076-3090 (R19-A1 of 27 Sep already allowed 'up to 3 re-downloads at 2 min', later narrowed to one by R35-A1), tools/uptest.py
  (save has no internal timeout; compare = TeamIds above us in S0 and below us in S1; missing team = not passed).
- Empirical LB freshness: ~11 S1 events 27-29 Sep (l.2791 x3 fresh first try, 2873, 3197, 3308, 3617, 3641, 3858, 4155, post_exp75 l.4478)
  -> 0 lags, 0 download failures outside the 05:30-05:57Z trip outage. P(lag after 1 re-save or fail) ~1-5%, not 5-10%.
- Monotonic claim: true for a single-completion window (bests never fall; ties by earlier submit are stable). HOLE: if slot 2 is used
  (exp89s non-CI at ~12:00Z reads ~19:05-19:15Z) a lagging LB that shows count 57 after BOTH completed may reflect exp89s, not exp89t ->
  misattributed UP. Longer re-save window (to 19:50Z) overlaps exactly that completion window. Needs 'no other ref of ours terminal
  between S0 and S1'.
- Edge conflict: card section 5 / T-rows promise swaps only 'до 22:45 МСК' (19:45:17Z admit edge); a V_pub change decided at 19:50Z
  leaves the user <10 min before the 20:00Z tick and contradicts the card text.
- Private value: the decision is exp89t vs exp87a at the SAME 0.959 display; they differ only by DIS 2.25, whose indirect LB estimate is
  0.000 +-0.002 (09:19Z read). A sub-rounding public UP on one embryo (29% of test) carries ~no private signal; exp89t adds a 4th lever.
  Expected private gain of resolving the rare BLIND case ~0.
- Verdict: refuted (value ~0, overstated probability, slot-2 hole, 19:50Z edge); narrow fail-soft variant given as fix.
