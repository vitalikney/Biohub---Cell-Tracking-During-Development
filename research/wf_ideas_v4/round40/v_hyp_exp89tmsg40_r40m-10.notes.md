# R40M-10 skeptic notes (2026-09-29 ~13:30Z)
- No prior v_hyp_exp89tmsg40_r40m-10.json; fresh run.
- Source line: round38/report.json R38-A5 (1) DIS line: 'по округлённым +0.001, истинная разница от 0 до ~+0.0015 на одном эмбрионе'. Origin: round38 v_hyp_exp89tread38_r38t-t1.json reason '(0, ~0.0015)'.
- Arithmetic: half-up display 0.960 => [0.9595,0.9605); 0.959 => [0.9585,0.9595); diff in (0, 0.002). Under truncating display [0.960,0.961)-[0.959,0.960) => same (0, 0.002). Bound holds either way.
- Consistency: CONTEXT l.3941 already states 'four rounded displays carry up to 0.002 of rounding error'; R38-A5 (4) T5 line uses '<d-0.960> to <d-0.958>' (width 0.002). T1 line is the odd one out.
- Rank info (exp87a 17th of 21 in 0.959 block at 10:14Z) puts exp87a low in its interval => larger gaps are if anything MORE likely, so ~0.0015 understates; midpoint of the triangular diff = +0.001.
- exp89t 56669888 still PENDING at ledger 13:19:14Z => T1 remains reachable, so the line can still be printed.
- VALUE: zero private/LB impact (card wording only, no decision rule touched). FEASIBILITY: text edit in the fill copy / mk_card, 0 Kaggle calls; not outcome-dependent (made before the read), so not a post-hoc rule change under R37-F6.
