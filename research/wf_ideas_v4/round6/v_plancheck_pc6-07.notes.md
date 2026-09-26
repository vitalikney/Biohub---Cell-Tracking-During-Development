# v_plancheck PC6-07 notes (2026-09-26 ~06:05 UTC)
- No prior json for this task. poll.log: #37 56563521 / #38 56563534 still PENDING (last lines 3132/3134).
- CONTEXT.md l.2028 C2(d): timeout/compute on K2 only -> ask the user; default row 1 [OK] (= K1). Confirmed.
- CONTEXT.md l.2029 C3 + l.2036 V1 already give the pair {twin #38, exp52} when there is no K1 -> the "no-new-submit option" already exists.
- Key counter-evidence: poll.log l.3138 probe 35 = exp57b = x138 + DaughterNet insertion (exp48 knobs), COMPLETE 0.954, L35 in (6.72, 7.73] h on the SAME hidden run. K1 = exp58t = exp57b + safetail (gates only); K1 dummy CSV sha == exp57b dummy CSV (CONTEXT T1 block). P36 (x138 + ungated insertion + leaf prune) also COMPLETE, L36 <= 7.42 h.
- So K1's code path has already finished on the hidden data once, 4.3 h below the 12 h limit. The shared 8.0/9.5 h timers are irrelevant unless runtime > 8 h.
- Dummy repair sums (round3 scan_plancheck notes): K1 499.8, K2 509.2, twin 218.8, exp57b 491.4 s -> K1/K2 same cost. With a K2-only timeout (twin fine), the only code difference vs #35 is lowrefine(+safetail) -> either lowrefine x insertion interaction (K1 lacks it) or a hardware/platform draw (any resubmit is a fresh draw). In both cases K1 is the evidence-backed retry. Finding's "K1 is not an independent retry" is misleading.
- Parts that stand: no K2'' after a timeout (longer 10.5/9.0 h deadlines = less margin); already implicit since V3 ties K2'' to the runtime trigger + B > 9.0 h. Probability of the event < ~1%.
- Verdict: refuted (premise wrong/misleading; remaining action already covered by C3/V1/V3).
