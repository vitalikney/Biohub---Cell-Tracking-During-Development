## 2026-09-27T23:27:29Z start skeptic r21w-4 holder rule
- 23:27Z now; W1 (exp78b/exp79a/exp78a) not yet submitted -> condition 'log before exp78b terminal header' still satisfiable.
- Sources: CONTEXT.md 21:05Z v3 (1) codes (cap-6-base file >=0.957 -> '+', coded vs its OWN base display, not vs the row);
  21:06Z N2 pre-reg (base exp70g); 22:27Z probe 46 read; e10_watch/20260927T2230Z.txt l.975-996 (0.957 block = 38 teams ranks 119-156;
  0.956 = 52, ours 9th); round21/scan_hyp_w2_w4_plan.notes.md (exp82a ffc00631 / exp82b 7cd1e3ed are SCRATCH builds only, no dummy).
- ARITHMETIC CHECK: exp70g ~0.95634 -> exp81 displays 0.957 at g >= +1.6e-4, and v3 codes that '+' regardless of who holds the row.
  Finding's '+6.6e-4' = gain needed to overtake exp78b on the ROW, which v3 does not require. P(detect) under N(0,8e-4):
  g>1.6e-4 0.42 ; g>2.6e-5 (0.957 block gap ~1e-3/38) 0.49 ; g>6.6e-4 0.205. So real gain in detect prob ~0.42 -> ~0.49, not 0.20 -> 0.45.
- Real (smaller) effect: on a non-holder, a 0.956 exp81 reads '?' not '0' (v3 holder condition) -> SEC cannot CLOSE; on holder it can.
- Value: extra sensitivity is in the 2e-5..1.6e-4 band on the ONE public embryo (29%); v3 itself said the U window holds ~1-3% of CI/SEC mass
  and weight swaps were 0/5 on LB; sub-1e-4 public deltas carry ~no private sign info (edge filter +0.016 lab -> 0 LB; forkmid +5-9e-5 public, private unknown).
- Feasibility: exp82a/82b need repo builds + dummies (~0.4 GPU-h each) that must pass by W2 decision; holder unknown until ~07:30Z (78b) / ~08:35-09:15Z (78a);
  in the main scenario (78b '+' holder) W2a = exp80a by v3, SEC is pushed to W2b behind E10 and a CI '+' stack -> may not be submitted at all 28 Sep.
  Codes for a SEC file on a 0.957 base are undefined in v3 (amendment says 'against its own base' without a table) -> new rule text needed.
  Moving-target: if exp80a (W2a) later becomes holder, exp82b is again a non-holder.
- Verdict: refuted (core arithmetic overstated ~3x; private value ~0; adds branching + 2 dummies). Keep v3 SEC=exp81; optional minimal fix below.
