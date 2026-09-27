# v_hyp_private_view_r20pv-7-private-read-row (skeptic, round 20)
- 2026-09-27 ~20:30Z start; no prior json.
- Sources: round20/scan_hyp_private_view.json (r20pv-1 MC: C mean +0.0004, sd 0.0017-0.0023, P(C>0) .49 (.32-.59); r20pv-7 text), CONTEXT.md l.2570-2590 (private-read v2: read is over DISPLAYED contrasts in thousandths, l.2573), l.2289 (DISPLAYED 3-decimal private scores), l.2863-2866 (L6/L7 priors with P(=0) .40/.45 = rounding-aware), l.3056 (8) 'Add 56606948 [exp70g], 56611472 and every 28 Sep ref to the private-read list', l.3195 (10) same for 28/29 Sep refs, l.2948 (exp70q = K2 + cap 6 + THRESH 0.3 + forkmid 4.5).
- Redundancy: exp70g 56606948 is ALREADY on the read list (l.3056 (8)); every 28/29 Sep ref too (l.3195). Only the prior + joint-read rule are new.
- Rounding check (scratch sim, base U(0.950,0.960), 4% exact-zero mass, 3-dp display of both files):
  mu +4e-4 sd 2e-3 -> P(<0/=0/>0) .31/.23/.46; sd 1e-3 -> .19/.37/.44; lab-like mu -4e-4 -> .46/.22/.31; public-like mu +1.1e-3 -> .21/.20/.59.
  => registered prior .48/.04/.48 is wrong for the displayed observable (P(=0) ~0.2-0.4, not 0.04) and symmetric although its own MC mean is +0.0004.
- Discriminating power of the sign: P(>0) .59 vs .31, P(<0) .21 vs .46 -> LR ~2 per non-zero read; '=0' (~22%) uninformative. One draw pooled over the private embryos; cannot 'fix' the public-like weight, only nudge it.
- C_q = exp70q - exp70b is a compound (cap6 + THRESH 0.3), not a cap read. Clean: C_fm = exp76e - exp70b (cap 6 on fm45), C_thr = exp70q - exp76e.
- Value to medal: 0 (post-deadline calibration). Feasibility: trivial text; no runtime/R8 issue.
