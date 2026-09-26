# v_hyp_post_deadline_r12p-4 notes (skeptic VALUE+FEASIBILITY)
- 2026-09-26T20:45:42Z start; no prior JSON found. grep 'late sub' in CONTEXT.md: 0 hits (novelty claim holds).
- 20:5xZ read scan_hyp_post_deadline.json (r12p-0..8) + CONTEXT tail (to 20:34Z: R7 lifted, finals = one public / one private, autonomous night).
- KEY: r12p-8 (same scan) gives CEILINGS for the inference-only agenda: I-222 <= ~+0.003 pooled, I-242 +0.0063 6bba-only,
  coordhead-v2 <= +0.002, I-079 learned <= +0.004 (and I-079 needs retrain). r12p-1: all rule-based post-proc realistic <= 0.
  => with the r12p-4 eligibility rule "lab EV < +0.003 stays lab-only", the eligible INFERENCE-ONLY set is ~empty
  (EV << ceiling). The only item that can move the score (D program) needs retraining = not 'frozen x138/K2 stack'.
- Rounding: displayed(b) - displayed(a) >= 0.001 implies b > a (rounding monotone) -> sign-sound read; but a true +0.0002
  passes ~20% of the time, and a true +0.0009 shows 0 ~10% of the time; magnitude interval (0, 0.002).
- Internal inconsistency: 'resolution 0.001 ~ +0.006 lab at r=1/6' vs 'EV < +0.003 lab stays lab-only' (+0.003 lab -> +0.0005 private = coin flip).
- GPU quota: CONTEXT l.341 each probe needs a prior commit run (15-40 min, now ~dummy runs) -> late subs do use some quota (hidden rerun does not, CONTEXT l.1972). Claim 'no GPU quota' is only half true (minor).
- Determinism caveat: K2 has wall-clock deadline gates (REPAIR_DEADLINE_S 34200, DIVINS 28800 s); an added stage that pushes the hidden run past them changes output by timing, not mechanism; hidden hardware differs from lab (bit-determinism measured locally only, CONTEXT l.796).
- WebFetch https://www.kaggle.com/docs/competitions returned no body (JS page); relying on general Kaggle behaviour: late subs are scored public+private, not ranked, host-enabled per competition. Not verifiable before 30 Sep either way.
- Overlap with r12p-3 (same scan): after the deadline the private scores of all 39 old subs (incl. #34-#38) are an embryo-held-out table at zero cost -> 'only true bed' is overstated; late subs add only NEW variants.
- Verdict: refuted as a VALUE item (0 effect on our final rank by construction; eligible inference-only set ~empty under its own +0.003 rule; the 15-sub budget sizes a bed with nothing to read). Surviving form = one info line on 30 Sep.
