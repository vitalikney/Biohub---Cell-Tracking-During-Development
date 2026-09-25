# RT2 feasibility notes
- 2026-09-25T17:48:12Z start; no prior json. Reading CONTEXT.md tail, FINAL_REPORT v3 §e/§f, trainlab gates.
- 17:48Z read CONTEXT.md tail (§e R3/R4/R5, §f fallback list, dummy gates 17:20Z, FF 17:45Z, night plan 17:55Z) and tools/trainlab.py 594-665.
- Facts: R3 as written = accept if public >= prev - 0.001 and "a rider that passed lab gates is not removed for -0.001". §f fallback item 4 = #34 (exp56) contradicts §f's own "never tick exp56" line -> item (2) is a pure consistency fix.
- trainlab.gates(): dc.pass_strict vs dc.pass_noncontrol_plateau, note "main session decides" -> ambiguity is real.
- `kaggle kernels status` 17:48Z: exp60 trainlab-a RUNNING (pushed 17:15Z, ~2 h -> output ~19:15Z), trainlab-b RUNNING too. So the deadline for item (3) is ~19:00Z TONIGHT, not 07:00Z tomorrow.
- K2 submit 00:01Z 26 Sep -> insertion gate 8.0 h = 08:01Z; repair deadline 9.5 h = 09:31Z. Step-0 forecast 7.8 h -> R5(b) margin 1.7 h >= 1 h OK for repair; insertion gate margin only 0.2 h, so poller alive 07:00-08:30Z needed (it had 5 empty outputs 15:26-16:06Z today; retry patch added).
- Gap: in branch A, K1 (S3) is HELD -> "compare with its scored twin K1" has no score. K1 sha256 == exp57b dummy, so #35 (0.954) is a proxy unless #35's x138 7.5 h deadline fired (L35 in (6.72,7.73], unproven). If lowrefine is dropped, §f(i) needs a SCORED F1 -> K1 must be submitted (slot S3 at 00:01 or 26 Sep afternoon) and K3 must be rebuilt with LOWREFINE_ENABLE=0 + a new dummy (~30 min GPU). 26 Sep slots: K2,K1,K3,K3b,K4 = 5 exactly; K3b can move to S7.
- Cost: 0 runtime, 0 code, text only; byte-identical/fail-soft N/A. Needs user OK (user asleep; standing OK covers researcher actions, arguably not amending the approved pre-registration) -> write as timestamped amendment before 19:00Z, flag for user veto.
- Verdict: NOT refuted (feasible), with the fixes above.
