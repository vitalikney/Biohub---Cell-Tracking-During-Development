# arithmetic verify hole-fill-sandwich (started)
- sources: research json/notes (hole d1 bins, valley test, sandwich 44% vs 40% control), fn_anatomy_exp39_ef.md b_break 399 -> +0.00298 (7.47e-6/FN), metric memory (node term linear, signed).
- exp39+ef: TP~122,784 FP 5,242 FN 6,099 -> D=134,125; FN->TP = 1/D = 7.46e-6; FP removal = J/D = 0.915*7.46e-6 = 6.83e-6.
- Full-hole ceiling reproduces: 4855*7.46e-6=0.0362 + 3250*6.83e-6=0.0222 = 0.058 (hyp 0.059 OK) - but assumes insertion fixes same-blob holes.
- Break-even error in hyp: avg errors per hole = (4855+3250)/11128 = 0.73, not 2.5. Per 6bba video D~890 -> 8.2e-4 per useful fill vs node cost 0.1*0.93/16.8k=5.5e-6 -> break-even useful rate 0.67% (hyp 0.2%). Not binding; harmful duplicate fills are.
- Reachable (distinct-nucleus AND sandwich-pass) share of hole FN: 4-6um 0.34*0.44*(0.03-0.05) + 6-7um 0.15*0.44*(0.11-0.30) + >7um 0.51*0.015*(0.44-0.59) = 2.1-3.2% -> ~100-155 FN + pro-rata FP -> ceiling +0.0012..0.0019 at perfect capture; realistic x(0.6 peak cov x 0.6 link) -> +0.0004..0.0007.
- Node cost: cap binds (sandwich passes 40% of in-tissue points, +24% candidate peaks) -> +1.5% nodes -> -0.0014 * surviving share (singletons die at min_track_len 6) -> -0.0004..-0.0014.
- Net local -0.001..+0.0003; public <=0. Any bigger local gain = same-blob in-sample position correction (won't transfer).
- FINAL JSON written (refuted).
