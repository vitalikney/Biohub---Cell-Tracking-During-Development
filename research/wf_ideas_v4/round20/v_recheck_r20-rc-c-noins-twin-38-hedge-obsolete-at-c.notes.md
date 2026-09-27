# v_recheck R20-RC-C notes (2026-09-27 ~23:30Z)
- No prior answer JSON existed -> fresh verification.
- Algebra re-derived (F1=b+x+y, #37=b+x, #38=b): diff=max(F1,#37)-max(F1,#38): x>0,y>0 ->0; x>0>y -> min(-y,x)>0; x<0<y -> 0 or x+y<0; x,y<0 -> x<0. Algebra CORRECT.
- REDUNDANT: the '#38 always' rule was already superseded before round 20:
  * CONTEXT 27 Sep 11:09:39Z user letter (b) "я бы за вариант б) топил": V*_C -> {V*_C, #37}, #38 leaves.
  * CONTEXT R19 READ TABLE v2 item (9) (18:50Z): "V_pub >= 0.955 and non-CI -> {V_pub, #37 56563521}; #38 leaves" and "The partner is always #37."
  * CONTEXT 19:01Z: options sent to user, A {exp70g,#37} RECOMMENDED.
  * CONTEXT 19:10:58Z: user picks on 29 Sep after all variants; session never re-ticks.
  => finding's action (propose {F1,#37}; mark R14-RC-C superseded) is already the standing rule. Zero decision delta.
- Magnitude inconsistency: uses lab |y| 0.0003-0.0006 (in-sample, ins_cap6.json -0.00079/-0.00052, sign falsified by probe 45) but public |y| in (0.001,0.003) >= public x in (0,0.002). With x,y comparable size and P(x<0)~0.15, E[diff] at cap 6 ~ 0.4*E[min(-y,x)] - 0.15*|x| ~ +/-1e-4 -> sign unresolved; '#37 dominates as cap rises' is not established (a higher public cap read also lowers P(y<0)). Objective is medal/rank not E[score] anyway.
- Verdict: refuted as a NEW finding (redundant confirmation of an existing rule; quantitative 'dominates' claim unsupported). Keep only as a one-clause rationale if wanted.
- 20:30Z wrote final JSON (refuted=true).
