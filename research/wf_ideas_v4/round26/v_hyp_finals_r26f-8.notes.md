# v_hyp_finals_r26f-8 notes
- 2026-09-28T13:37:30Z start; no prior json. Read scan_hyp_finals.json R26F-1..9 + notes.
- Checked facts vs CONTEXT.md l.3700-3930 + poll.log: #37 56563521 0.954, #38 56563534 0.953 (poll.log l.22985) ticked -> draft line OK. Re-tick until 23:59Z = 02:59 MSK (CONTEXT l.3677) OK. Q3 = YES 11:26Z (SEC only in V_pub slot) -> round prompt 'Q3 open' is stale; draft does not contradict it.
- UP semantics (CONTEXT l.3124-3130, 12:16Z probe 50: rank 153->134, '21 TeamIds passed' = WE passed them). Draft tie rule (1) 'файл, после которого нас обогнали команды' = 'after which teams overtook US' -> SIGN ERROR in the Russian text. Must read 'после которого мы обошли команды'.
- R25-A1 (5) (CONTEXT l.3745-3749, pre-registered): pair B {V_pub, exp75} only if exp75 >= 0.955 'as a trade, NEVER as the default'. Draft row 1 makes B the DEFAULT with floor 0.954 -> needs R26F-2's amendment logged pre-score (before exp75 submit 00:06Z / before its read ~09:00Z 29 Sep) with the structural reason (V_pub now non-CI, probe 50 12:16Z). Otherwise violates the pre-registration.
- R25-A1 (5) also: exp75 <= 0.953 or ERROR -> CI-risk flag on any CI V_pub. Draft fallback omits the flag for row 2.
- Row 3 lists {основной, #37+K} = exp89u, which is not built into experiments/ nor scheduled (R26F-7 ranks it below exp89s) -> noise on the card unless submitted.
- exp75 = #37 topology + exp79a CI coords (CONTEXT 11:17Z R25-A4) -> 'exp75 несёт только CI' correct. mc26 ranges match scan notes (.768-.898 etc.), labelled 'оценочная' -> honest.
- No GPU, no slot; text only. Verdict: keep, with 4 fixes.
- 2026-09-28T13:39:01Z JSON written (refuted=false, 4 fixes).
