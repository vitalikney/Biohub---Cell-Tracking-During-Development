# v_recheck R37-RC-A notes
- 2026-09-29T09:26:21Z start; no prior json
- 09:27Z verified: experiments/RESULTS.md l.32 exp13 d1/a0 0.9149, d3/a0 0.9110, ref d2/a0 0.9158; polyfit -> S*=1.658, 1.75 +0.00031, 2.25 -0.00067 (OLD base: div 1.2, pre-x138).
- dummy_lab_summary.json: exp70g 0.92052 (2047/101/80), exp88c 0.92039 (TP 2048) -> lab delta -0.00013 on current-family base; the +0.0002 prior mean is generous.
- MC 400k (exp85a true U[0.9575,0.9585), display>=0.960 <=> true>=0.9595): mu +0.0002 sd 0.0008 -> P 0.063, P(<=0.957) 0.205; mu 0 -> 0.039; mu -0.0001 -> 0.030. Reproduces finding.
- CONTEXT 09:19Z: exp89r = 0.957, DIS dd=0 -> '?', rule (a) not met, slot 2 default UNUSED -> the finding's conditional log line now applies.
- CONTEXT 14:12Z (0)(i) lists DIS 1.75 as 'stay out' (verified l.3935); 12:23Z RISK STACK: values not picked on public board only.
- exp89e folder exists, no dummy entry in CONTEXT (verified).
- Feasibility: a dummy (~25-35 min) would fit before 12:00Z (now 09:27Z), so schedule is not the blocker; value + pre-registration are. Verdict: UPHELD stands, not refuted.
- 2026-09-29T09:28:02Z final JSON written (refuted=false)
