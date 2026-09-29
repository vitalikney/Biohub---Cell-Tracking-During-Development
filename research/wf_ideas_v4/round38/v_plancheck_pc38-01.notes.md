# v_plancheck PC38-01 notes (2026-09-29 10:27 UTC)
- No prior v_plancheck_pc38-01.json; fresh run.
- scratchpad card_fill_1203_v2.txt (mtime 13:01 MSK = 10:01Z) section 6, last line: "Satwik в обсуждении 744273 (29 сен): на паблике мало делений; его локальные выигрыши по делениям дали на ЛБ 0 или чуть хуже. Это довод за страховку #37." -> no 'не подтверждено' flag (the 743006 line above carries it).
- mk_card_v2.py: the replace `c + "   Satwik ... Это довод за страховку #37.\n"` adds that line; token asserts (П1, рекомендую, <, [если, П4) pass but do not catch it.
- round37/report.json R37-A4: optional line text = 'Не подтверждено: Satwik (744273, 12:06 МСК) ... оба партнёра (#37 и exp75) их не несут, так что на выбор П3/П2 это не влияет.' + "Drop the scan's 'ещё один довод за страховку #37': exp75 = #37 + CI hedges cap 6 and K just as well."
- CONTEXT 09:57Z (A4): 'optional Satwik (744273) line'. Satwik comment 09:06Z = 12:06 MSK (round37 report l.40/60); URL https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/discussion/744273 ; no values (opinion).
- Logic check: #37 (cap 4 insertion, no cap 6/K/CI) and exp75 (#37 + CI) both lack cap 6 and K -> Satwik claim does not discriminate П3 vs П2; line is a one-sided nudge in the neutral card (card forbids 'рекомендую'; П3/П2 = user choice). Finding holds.
- R37-A4 replacement text: tokens П1/рекомендую/</[если/П4 = 0 (checked by eye). Time now 10:27Z; card due 12:03Z -> ~1.5 h slack. 0 Kaggle calls.
- Verdict: not refuted. Value = 0 LB; it is plan fidelity/neutrality. Feasibility trivial.
