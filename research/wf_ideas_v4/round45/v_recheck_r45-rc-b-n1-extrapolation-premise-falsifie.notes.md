# R45-RC-B recheck (N1 extrapolation, I-384 / IB29-06): notes
- 2026-09-29 18:30Z: no earlier JSON for this task; starting.
- ideas_29sep/v_8.json: IB29-06 refuted. Reason (1) = public-fit: the TRIGGER was exp89p reading '+'. It was a trigger condition, not an assumption of '+'. Reasons (2) (no n2a-delta weights, needs a Kaggle API chain) and (3) (superlinear peak growth x2.9 at k=2, in-sample lab, WiSE-FT) do not depend on the read.
- CONTEXT l.4394-4402: probe 54 exp89p = 0.956 vs exp85a 0.958 -> P '-', SEC out; dummy-lab -0.0008..-0.0020 on 5/5 pairs had the right sign.
- CONTEXT l.4244-4246: those 5/5 pairs all come from ONE in-sample clip (6bba_05db0fb1). The same bed also signed probe 10 (the last secondary swap) correctly, so 'the only lever whose lab sign matched' is an overclaim (secondary swaps are 2/2 on this bed; CONTEXT calls it 'weak negative prior, not a sign').
- CONTEXT l.4482: DIS dd = 0 -> '?' (LB ~0). OK.
- IDEAS.md l.806: I-384 = N1 on the exp71 delta (x2/x3/x1.5 weights local in _dl) plus IB29-06 (n2a delta) folded in by curation 28. The exp71-delta trigger (exp76d/exp72 display >= 0.955) never fired; those files were never submitted (NO-GO). Probe 54 reads the n2a direction only. The finding's 'mark I-384 CLOSED' merges the two.
- Verdict: 'no action tonight' is correct and costs nothing (slot closed, reserve closed ~14:10Z, R9 no retrain). Wording fixes needed.
