# v_hyp_morning30 R30M-1 notes (2026-09-29T01:29:40Z)
- 01:31Z: no prior json. Verified CONTEXT l.3937-3938 (P codes vs exp85a 0.958; '0' already includes MASKED/BLIND), l.4155-4160 (51 = 0.959, row 0.959, count 53).
- experiments/e10_watch/20260929T0113Z.txt l.272: row 132, 0.959, count 53, last sub 2026-09-28 12:14:57 (= exp87a) with 3 night files pending -> count/date = scored only. Row can move only if a new score > exp87a unrounded (>= 0.9585); a 0.958 display (< 0.9585) cannot -> k = 0 by construction. CORRECT.
- Only non-attributable way to get k>=1 at 0.958 = another completion in window (MASKED) -> '0' anyway. Outcome identical under text; finding is clarity, not a rule change.
- DUPLICATE: scan_plancheck.json (round30) finding on '0u unreachable' says the same; scan_hyp_morning30 summary too.
- CAVEAT: last sentence 'k = 0 leaves exp87a first' contradicts R26-A4 (d) (round26/report.json: "attributable UP chains by completion order; 0/MASKED/BLIND are unresolved, never lower"), kept in force by freeze (5) l.4218 -> under (d) k=0 is unresolved -> (2) non-CI -> exp89p. This is open conflict PC30-01 (scan_plancheck.json). The logged line must not settle it implicitly.
- Stale text: freeze (9) l.4247 'on an equal display with code 0 ... V_pub stays exp85a' is pre-51 wording (V_pub = exp87a since 21:45Z); the new line should supersede it.
- V_pub admission for non-CI exp89p also needs L_hi <= 9.0 h (CONTEXT ~l.3183); expected L ~7.0-7.2 h -> fine but state it.
- Count 53->54 valid only if exp89p completes first (expected ~07:46-07:58Z vs exp75 ~09:05Z+, exp89r ~09:25Z); else MASKED unless R26-A4 (b) exemption (lower display) applies.
