# R41-RC-B verify notes
- 2026-09-29T14:28:03Z start; no prior json
- CONTEXT l.3485-3490: exp85b +49 nodes/+3 forks; exp85c +1,022 nodes (+0.84%), LOWREFINE +3.05% -> K ~ READMIT: confirmed.
- CONTEXT l.3856-3861: probe 50 exp85a 0.958 vs exp70g 0.956 = display +0.002 (unrounded 0.001..0.003).
- Node cost arithmetic -0.1*0.91*0.0084 = -0.00076 ok (metric adj = J*(1-0.1*dN/N), memory project-metric-insights).
- round23/scan_recheck.json R23-RC-A: band [0.94,0.965) 6,696 peaks, 0 near GT; band population 44b6 +1.09% vs 6bba +0.32% (~3x).
  => the zero-recall node cost is embryo-dependent: ~-0.0003..-0.0010 on train-like embryos, scaling with band size; not a fixed floor.
- R23-RC-A: frontier947 read = readmit turned ON at 0.965 (0.947->0.946), not the 0.965->0.94 step. JT 743929 read (+0.001) and our probe 50 are both on the SAME public embryo, and JT picked K by public reads (selection). So no independent private evidence; 'out-of-sample reads split' is one embryo.
- risk_audit/skeptic.md l.30 + answer_ru l.22: harsh = stress scenario (cap6 and K both -0.001), labelled as such; audit rec keeps pair. Finding's action = no change = current plan. Gain 0.
- No exp86c (RA92) public read (dropped from night, l.3896): no second rung to check monotonicity.
- 2026-09-29T14:29:36Z verdict written: refuted=true (floor claim wrong; reads one embryo; no action)
