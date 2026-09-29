# R38T-G3 skeptic notes (2026-09-29 ~10:30 UTC)
- No prior JSON; started fresh.
- Card: session scratchpad card_fill_1203_v2.txt l.48: "в пул входит, если завершится до 22:12 МСК, а чтение >= 0.960 или 0.959 с приписываемым UP — до 22:45 МСК с пометкой UNPROVEN-ins; после 23:00 МСК — не финал".
- exp89t 56669888 submitted 09:00:17Z (CONTEXT 09:00Z entry). 10.2 h -> 19:12:17Z = 22:12:17 MSK; 10.75 h -> 19:45:17Z = 22:45:17 MSK; 11.0 h -> 23:00:17 MSK (= tick deadline).
- Rule: CONTEXT freeze (1) l.~4187-4191: L_hi = first COMPLETE header + 210 s x failed attempts - submit; 10.2-10.75 h '+'/'0u' stand UNPROVEN-ins; > 10.75 h '?'. 08:51Z R36-A2 (i) applies it to V_pub admission.
- So gap 22:45:17-23:00 MSK is real and unstated in the card; the user could read it as admissible.
- Part (i) (22:12 keyed on completion) is near-cosmetic: in 22:12-22:45 a '+' / 0.959+UP read is still admitted (flag only); '0'/'-' reads never make exp89t V_pub anyway.
- Observed CI-family L (ledger in CONTEXT): max 9.48 h over 5 CI reads; the 10.9 h tail is modeled, never observed. Joint P(L in 10.75-11.0 h AND display >= 0.960) small (<~2%; exp89t expected ~0.959, DIS ~ 0 per probe 52).
- Mitigation already present: session sends one line after the exp89t read and checks at 22:43 MSK, so the ambiguity would be resolved by a message too.
- Verdict: valid, wording-only, zero submission/runtime risk; small value. Suggest a tighter phrasing that removes the confusing 22:12 clause from the V_pub test.
