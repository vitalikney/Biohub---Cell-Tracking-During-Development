# D4 divins-time-insurance — VALUE skeptic notes
- 2026-09-25 ~17:05 UTC: started; no prior json/notes.
- 17:10 UTC evidence read:
  - _dl/biohub-exp58-x138-safe-lowref/...log l.1967-2003: divinsert score sec 37.7/65.1/9.9/185.5 (nodes 3869/6988/661/20770, eligible 14/0/33/142, added 4/0/4/4).
  - experiments/runtime_step0/step0.md: L35 (exp57b = #35, insertion on, NOT gated) <= 7.73 h on the FULL hidden set (public+private in one run); K2 ~= #35 + lowrefine -> <= ~7.8 h.
  - research/wf_ideas_v3/FINAL_REPORT.md l.57: 8.0 h insertion gate chosen deliberately (<9.5 h repair deadline) -> gate protects repair of later clips.
  - tools/div_insert.py l.150-222: U = tracked nodes with 1 out-edge + nearby v; C1 = child of u (itself usually a u at t+1); V = orphans/stealables. U and C1 overlap heavily -> stage-1 set |U| is likely most of nodes_scored; the ">=50% fewer nodes" guess is unverified (no divins_dump npz found locally).
  - tools/daughternet.py l.115-131: score_nodes batches sorted by t; changing the scored set changes batch composition -> cuDNN float drift possible (gate would catch, cost = wasted hours).
- Value arithmetic: insertion LB gain +0.001 (one probe, 3-decimal display: true delta 0..0.002). Division term = 0.1 x div Jaccard.
  Loss if skipped on 5-15% of clips: 0.00005-0.00015; x P(T>8h | hidden fixed, #35 measured <=7.73h) ~0.03-0.1 -> EV ~2e-6..1.5e-5. Not measurable, far below private noise.
- Structural: K2 (00:00 UTC) cannot get D4 (its code is frozen, dummies already passing) -> D4 value on K2 = 0. For K3 the score comes from K3's own single hidden run; its latency is observed before finals are ticked, so "partial insertion" is visible (latency > 8 h) and the 2 final picks already hedge it -> option value further shrinks.
- Part (2) (gate 8.0 -> 9.5 h) can be NET NEGATIVE in exactly the slow world it insures: each insertion adds ~66-185 s, pushing later clips past the 9.5 h repair deadline where they lose relink/gap (repair value per clip >> insertion value ~0.001/clip-level). 8.0 h gate was designed for this.
- Freed runtime (~0.8-1.4 h guess) has ~0 value: ~4 h headroom under 12 h already, no runtime-hungry rider approved (R8/R9).
- Verdict: refuted on the VALUE lens (EV ~1e-5, possibly negative for part 2, zero for K2).
