# v_hyp_lessons_r14l-6 notes (2026-09-27)
- start: no prior json; read scan_hyp_lessons.json R14L-3/6/7
- ~02:05Z facts:
  - P2 (C2 = #37-#38 > 0, prior 0.55-0.60) is ALREADY pre-registered: CONTEXT l.2288-2300 (26 Sep 16:04Z) and LESSONS_draft l.70; pushed (origin/main == HEAD f24ff72, 2026-09-27T04:54+03:00). Redundant.
  - L1/L2/L4 priors already registered+pushed: CONTEXT l.2711-2721 (commit 3d48d35). READ RULE there: "0 is uninformative; no ratio is estimated". P1 reads 'all three = 0' as 'rules cost ~0' -> contradicts the registered read rule; also private RANK is by unrounded score (LESSONS s3.6) so display-0 != rank-cost-0 in a ~330-team tie block.
  - P1 arithmetic: independent product 0.65*0.50*0.80 = 0.26; comonotone upper bound 0.50; 0.45 is near the upper bound (plausible only with strong #37 correlation) -> 0.3-0.45.
  - P3 / R14L-7: CONTEXT l.2297-2299 (16:04Z) pre-registered "No rank-vs-0.953-block reading (rivals' private = max of their own two files; the block is not all x138 copies)" -> P3 is the forbidden reading. And f_B > f_A is expected mechanically: shrinkage f ~ m^2/(m^2+s^2); B margin +0.007..+0.013 vs A +0.002..+0.004 with per-team embryo-shift s ~0.002 -> f_B > f_A under NO route effect. Group labels ('own-model') unverified. Non-discriminating prediction.
  - Git gate: local commit date is self-attested; origin is GitHub (git@github.com:vitalikney/...), push time is the external stamp -> gate should be 'pushed before first private score'.
  - Rules: not a submission mechanism -> R8 n/a; 0 GPU, 0 slots, finals-neutral; commit as the user without trailer matches memory feedback-git-no-coauthor.
- verdict: core (freeze s3 item 11 + post-private-note-only clause) holds, cheap; P1/P3 as framed defective, P2 redundant.
