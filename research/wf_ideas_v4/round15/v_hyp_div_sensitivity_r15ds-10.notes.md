# R15DS-10 skeptic notes (2026-09-27 ~05:45 UTC)
- No prior json for r15ds-10. Source: round15/scan_hyp_div_sensitivity.json l.79-81.
- experiments/exp60_trainlab/results.md: control 6bba/ALL div TP/FP/FN 15/17/73 -> TP+FP+FN = 105 (D=105 checks out; GT div = 88). 44b6/ALL 1/8/10.
- dc0.30 6bba/ALL 15/11/73: 0 TP moved, 6 FP removed -> +0.0010 (M1 json: sel +0.0006, conf +0.0015). 44b6/ALL dc0.30 = -0.0006 (in-sample, CONTEXT l.2652). TP per band on 6bba: 0.15-0.30 = 0 changes, 0.30->0.35 = -5.
- CONTEXT 04:58Z D1 FACT already says: "the lab sign was wrong for this knob; the public division term is far more sensitive than the lab suggested".
- round9/LESSONS_draft.md l.26 (transfer 0..1/6), l.31 (fork-removal riders 0 for 5; low-J embryo break-evens 2-3x stricter for removing forks), l.32 (lab low power), l.38 (power clauses) -> dc0.30 is the 6th fork-removal rider; the lesson is mostly already present.
- Causal claim "governed by Poisson event counts" competes with the same scan's LEADING hypothesis SHIFT(-0.05) (44b6-trained center prior). One public read cannot separate them -> overclaim.
- Sharper, correct form: the lab arm had 0 TP events in the moved band; 0/15 bounds TP loss only at <= ~3/15 (rule of three) ~ up to ~3 public TP x 0.0023 = -0.007, which contains the observed -0.005. The ">= ~20 TP events" threshold has no derivation.
- Feasibility: text only, after 29 Sep, no runtime/submission; trivially fine.
- Verdict: refuted as stated (duplicate + overclaimed mechanism); fold one sentence into the existing LESSONS s2 Divisions bullet.
