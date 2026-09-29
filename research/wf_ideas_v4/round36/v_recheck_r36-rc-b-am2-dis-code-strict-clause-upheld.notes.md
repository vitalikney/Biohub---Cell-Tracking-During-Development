# R36-RC-B skeptic notes (2026-09-29T08:23:20Z)
- 08:24Z: no prior JSON for this task. 0 Kaggle calls.
- CONTEXT.md l.4294-4300 (02:53Z A-M2 function: d_R=0.959 -> UNUSED) = the rule the finding upholds.
- CONTEXT.md l.4404-4414 (08:19Z, "A-M2 RULE (a)", USER CHOICE in chat, "supersedes the A-M2 function of 02:53Z (1) now that P='-'"):
  exp89r COMPLETE, display >= 0.958 with L_hi <= 10.2 h (or >= 0.959 with L_hi <= 10.75 h) -> send exp89s; else UNUSED.
  git 2fdf387 (08:19:45Z) "A-M2 rule (a): exp89s if exp89r >= 0.958 (pre-score)".
- CONTEXT.md l.4415-4424 (08:23Z): exp89t (K+DIS+CI) built, dummy pushed; slot plan: slot1 exp89t (pending user yes), slot2 = rule (a).
- scan_recheck.json (written ~08:13-08:22Z) predates / did not see rule (a): its RC-B verdict "keep 0.959 row -> UNUSED" contradicts the user's rule.
- ledger l.22: 56656147 exp89r still PENDING at 08:18:17Z header (pre-score, so no post-hoc issue for the user's rule).
- Lab arithmetic check (scratchpad r36/pool.py numbers quoted in scan): exp89r-exp87a lab -0.00079; exp89p-exp85a -0.00160 -> lab dd = +0.00081 = DIS(+0.00048 on K) + ~+0.0003-0.0004 SEC x CI. Arithmetic OK but
  (i) the lab is 0/2 on CI sign (R36-RC-A) so a SEC x CI term from it has no standing; (ii) 0.0004 << +-0.002 display rounding; (iii) under rule (a) exp89s is itself a clean DIS read vs exp85a, so dd is only a trigger.
- VERDICT: refuted (stale; superseded by user rule (a)). Keep rule (a) unchanged; interaction may be an info note only.
