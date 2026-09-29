# v_hyp_readscard37 R37-F2 skeptic notes (2026-09-29 ~09:26-09:35Z)
- No prior answer file existed at start (09:26Z).
- CONTEXT.md 09:19Z: probe 52 exp89r = 0.957, rule (a) (08:19Z, >= 0.958) not met -> exp89s not sent; default UNUSED under the 08:28Z hold (decide 11:55-12:00Z; non-CI only).
- Math check: exp85a U(0.9575,0.9585) + DIS N(0,0.0012): need DIS >= 0.001..0.002 for display 0.960 -> P ~0.05-0.2 (avg ~0.1); plancheck PC37 gives 0.03-0.06. Either way EV ~0 and it would swap CI (3/3 LB '+') out of V_pub.
- digest_20260929T0918Z.md: E10 flag none (best public 0.953); 744273 Satwik 09:06Z (public has few divisions; no values), Yassine 09:13Z (no values). https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744273 -> no aggressive-mode build.
- IDEAS I-542 (re-submit for tie order refuted), I-484 / R36H-2 (blind exp89s refuted) confirmed.
- FEASIBILITY defect in the proposed message: 'до 14:55 МСК' is too late for a NEW candidate; scan_plancheck.json (PC37) says a non-CI candidate needs its dummy pushed by ~11:15Z (14:15 MSK; ~35-45 min dummy + R22-A1 gate). After that only exp89s/UNUSED are possible. Fix the wording.
- Verdict: not refuted (default UNUSED correct, consistent with rules); fix the cutoff time in the message.
