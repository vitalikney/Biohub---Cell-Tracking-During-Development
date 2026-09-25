# D3 dc-marginal-precision-gate VALUE skeptic notes
- 2026-09-25T17:42:40Z start
- Existing K3b gate (research/wf_ideas_v3/TASK_CLOUD_SESSION.md T9, ~l.176): 6bba CONF >= ctrl+0.002 at t*, >= +0.001 at both neighbours, 44b6 >= ctrl-0.0005, **precision of added forks >= 0.35**, fork count <= +50%, same nodes, t*=0.25 -> no build. Idea's premise "passes on ~1 event" ignores the 0.35 precision clause.
- FINAL_REPORT v3 l.61: gate already labelled "moonshot"; R4 (l.247): DC threshold is an R4 node/fork changer -> LB >= +0.002 for F1.
- Metric: score = adj_edge + 0.1*div_J; added fork with precision p: dJ = (p(1+J) - J)/D -> break-even J/(1+J) = 0.265 at J_pub 0.36 (CONTEXT l.1308-1321). One fork edge in adj_edge ~1e-5, negligible.
- Wilson 80% (z=1.2816): 3/6 LB .268, 4/8 .294, 4/10 .230, 5/10 .312, 6/12 .327; UB 0/6 .215, 0/8 .170, 0/9 .154, 1/15 .199 -> removal branch (UB<0.167) needs >= 9 evaluable removed forks, all FP.
- Pass probs (binomial; old modelled as point>=0.35 & >=2 TP, ignores plateau/cap so it's an upper bound):
  p=.20: n6 .099/.099, n10 .033/.121, n15 .018/.061; p=.25: n6 .169/.169, n10 .078/.224, n15 .057/.148; p=.45: n6 .56/.56, n10 .50/.73, n15 .55/.74.
  -> at n=6 the rules are IDENTICAL; delta false-pass 0.05-0.15 only at n>=10; power loss ~0.2 at true p=.45. Idea's "P(false pass) 0.25-0.35 under current gate" overstated.
- Downstream: false lab pass -> LB probe (S5, else empty) -> F1 only if public >= +0.002 (R4). P(public >= +0.002 | p <= break-even) ~0.1-0.2. Avoided private loss ~ 0.1 * 0.15 * 0.001-0.002 ~ 2-3e-5; symmetric power loss ~3e-5. Net ~0.
- Transfer: lab biases are UPWARD in precision and a Wilson bound only handles sampling noise: x138 detector saw all 199 (incl. 6bba); DC checkpoint selected on 6bba val (browser_intel.md 6.1 item 2: train = 71 44b6, val = 128 6bba). 44b6 is DC's train set -> even more biased.
- tools/trainlab.py l.20-30: lab control = x138+safetail with insertion DUMP-ONLY; dc0.15..0.35 arms replay from presafe graph WITHOUT insertion. K3b ships = K3 (with insertion, cap 4/video, frame cap 1, orphan+steal) and divinsert runs AFTER safe-division repair (_dl/biohub-exp58-x138-safe-lowref log l.1964-2003). Lowering t consumes orphans that insertion would use -> marginal set in lab != shipped marginal set. Lab already records tp_forks/fp_forks/new_forks/gone_forks per arm (l.536-537) -> fork labelling mostly exists.
- DC veto counts (exp58 dummy log): geometric 123/141/14/230, rejected 86/135/9/210, post-veto 37/6/5/20 (87% vetoed). Control evaluable forks on 6bba whole (exp39): TP 18, D 158.
- VERDICT: refuted under value lens: no measurable private gain (~0..+0.0001), premise overstated, bias uncorrected, removal branch unreachable. Harmless as an ADD-ON clause.
- 2026-09-25T17:45:51Z final JSON written
