# v_hyp_answers_prep R16AP-8 answer-parsing rule (round 16 skeptic)
- 2026-09-27 08:45Z start (date -u 08:44:49Z). No prior JSON. Files only, no API.
- Source finding: round16/scan_hyp_answers_prep.json R16AP-8 (+ R16AP-1..7 cards, R16AP-6 slot table).
- Evidence checked: CONTEXT l.2454-2471 (21:21Z entry (3): 'сделай нам также!' + 'делай' read as retrain yes, R8 lifted for it);
  l.2722-2746 (01:31Z R13-A3: that reading SUSPENDED; MORNING QUESTIONS 'three separate yes/no' Q1-Q3);
  l.2833-2847 (R15-A1 (4): class-C letter counts only if logged with date -u before the first 43/44 terminal header; (a) default/recommended, (b), (c) not recommended).
  Precedent of over-reading is real -> the core of the rule is justified.
- No earlier round proposed an answer-parsing rule (grep 'answer.pars|bare da|echo parsed' over wf_ideas_v4 rounds 5-15: 0 hits). Not a repeat, not a closed line.
- round16/scan_plancheck.json already flags exp70b-yes x class-C (b) partner ambiguity (INS = exp70b or #37).
- FLAWS found:
  (1) the finding reads 'yes to all' as Q1+Q2+Q3 yes. R13-A3 asks for THREE SEPARATE yes/no; Q1 is a head-only FT that also
      overrides the user's own 25 Sep refusal (7) and R9 (plancheck R16 notes this). A blanket yes = the same over-reading pattern
      the rule is meant to stop. Q1/Q2/Q3 must be named explicitly.
  (2) 'yes to all' also hits the exp70b x class-C(b) partner ambiguity (plancheck) - not only (b) vs (c).
  (3) timing trap: asking a clarification can push the class-C letter past the first 43/44 terminal header (~12:15Z) and turn it
      post-hoc. Fix: log the partial letter verbatim at arrival (date -u), mark 'variant pending'; if unresolved at the header,
      the pre-registered part is only 'class C allowed' and the variant is labelled USER DECISION AFTER SCORE.
  (4) cap Q6 is a choice (02:00Z vs 11:00Z), 'yes' does not map -> unchanged (finding agrees).
- Feasibility: procedure only, no kernel, no submit, byte-identical trivially, no R8 issue (not a mechanism), no user OK needed
  as long as it only TIGHTENS interpretation (the Q1-Q3 blanket-yes clause loosens R13-A3 -> drop it).
- Value: 0 direct private score; prevents a wrong re-tick/unauthorized push (tail-risk governance). Keep, with amendments.
- 08:50Z JSON written: refuted=false with amendments (i)-(v).
