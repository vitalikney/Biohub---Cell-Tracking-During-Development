# v_hyp_w2_w4_plan r21w-2-ledger-rule-exp83 (skeptic notes)
- 2026-09-28 ~00:0xZ: no prior JSON answer; started.
- tools/runtime_ledger.py l.69-84 EXP_RULES read: exp79a[a-z]* -> safetail_ci (l.79); exp7[2-9]* -> safetail (l.80); exp8\d[a-z]* -> safetail (l.81). First match wins (family_of, l.158-166).
- Ran family_of(exp_token(name)) locally: exp83a_k2cap12fc2_ci / biohub-exp83c-... / exp83d_... -> 'safetail' (TRAP CONFIRMED); exp82a/b, exp84a, exp81, exp80a -> safetail (correct); exp79a -> safetail_ci; exp79b -> safetail.
- FAMILIES: safetail deadline 9.5 h, divins 8.0 h; safetail_ci deadline 10.75 h, divins 10.2 h (= L_hi - 2.2 h rule, CONTEXT l.3134-3137).
- All exp83a-g builds in scan_hyp_w2_w4_plan.json carry coordinject (CI) -> rule exp83[a-z]* -> safetail_ci has no false positives; exp82* (SEC only) and exp84a (cap 48) correctly stay safetail.
- No CI file scored on LB yet (ledger.md 23:25Z shows only non-CI K2 family at L_hi 7.04-7.81 h); CI latency ~9.7-10.5 h is a model (non-CI ~7.6 h + CI 2.2-3 h). Even the low end > 9.5 h -> safetail family would print NO / 'gate MAY have fired'.
- Mitigation already present: ledger is report-only; --family override works (test l.192/220). Harm = misread card, not a wrong submission. Fix cost ~5 min; tests/test_runtime_ledger.py has the pattern (l.186-220).
- Minor: ledger header R5(a) sentence does not mention the 10.75 h CI family (cosmetic).
- Verdict: not refuted (tooling correctness, no LB/model claim).
