# v_plancheck_pc11-06 notes (skeptic: value + feasibility)
- 2026-09-26 ~17:40 UTC: no prior JSON; started. Read CONTEXT l.1620-1700 (R1-R10), l.2250-2340 (P4c, private-read priors C1-C4, rank forecast, user OK 17:00), round11/scan_plancheck.json (PC11-03..PC11-12).
- R4 text (CONTEXT l.1650-1652): "Δ к текущему кандидату F1" - F1 = K2 #37 (0.954), NOT x138. R4 as written: S 0.955 vs F1 = +0.001 -> F2 candidate only. PC11-06 "R4 vs S's real base x138, no new rule needed" is a reinterpretation.
- P6 last sentence (CONTEXT ~l.2144, quoted in PC11-03) bars "successor + insertion build (new code after R8, unscored stack)"; R8 consolidation ends 28 Sep 12:00. So E10 v2 IS a new rule and needs a new user OK (PC11-03 says so itself).
- P6 (CONTEXT 09:03 entry) registers the successor threshold as 0.956 "= K2 + 0.002 ... (R4)" and ends "No 'successor + insertion' build ... (new code after R8, unscored stack)". So 0.955 for S+ins is a NEW reading; it has to go in E10 v2 and get the user's OK. It is defensible because S+ins keeps the insertion, so S's own mechanism is measured against x138.
- Toy rank simulation (scratchpad pairsim.py; units = 0.001 private; I~N(0.7,0.9) matches C2 priors; D=X_S-X~N(muD,1); 400 x138 copies at X; 200 S copies (half keep x138 as max); 450 variants X+N(0.8,1.2); 70 top). P(bronze) / P(silver):
  muD -0.3: A{#37,#38} .70/.20, B{S+ins,#37} .77/.31, C{S+ins,#38} .65/.22
  muD  0.2: A .62/.17, B .78/.36, C .73/.31
  muD  0.6: A .53/.17, B .80/.45, C .77/.43
  muD  1.0: A .43/.16, B .80/.55, C .79/.53
  B >= C and B >= A in every case, so the pair choice holds. B loses to A only when I<L and D+I<L (~5-7%), which matches PC11-06.
- Feasibility gap: if runtime(S) + <=0.85 h crosses the 8.0 h DIVINS gate on the hidden run, the insertion is SKIPPED and S+ins degenerates to S+C01 (no tie-break edge). A runtime condition is needed: dummy runtime(S) + 0.85 h <= 7.5 h.
- Unconditional value is small: P(a clean S >= 0.955 appears after the OK and before 29 Sep 00:00) ~0.05-0.15. Every near-top public notebook seen so far (amanatar v10, anhadmahajan06) fails P4c.
- 2026-09-26T17:18:38Z: final JSON written (refuted=false with fixes).
