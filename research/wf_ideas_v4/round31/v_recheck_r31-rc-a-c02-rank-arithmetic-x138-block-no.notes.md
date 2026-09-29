# v_recheck R31-RC-A (C02 rank arithmetic) skeptic notes
- 2026-09-29T02:30:13Z start; no prior json/notes
- 02:32Z LB facts checked in experiments/e10_watch/20260929T0213Z.txt l.1115-1143 (CSV 2026-09-29T02:14:14): all block counts/ranks match; 3979 teams -> silver floor(5%)=198-199, bronze floor(10%)=397-398; mid (0.955-0.959) 316 vs mc26 244 -> +72/12.9 h = 5.5/h; 0.953 420->406; 0.954 140->136 (so the '0.954 0.7/h observed' rate is not observed, net -0.3/h; negligible, the model halves it).
- Card round29/finals_card_v5_ru.md sha8 aab8801a confirmed; l.37-38 П2 .75-.93/.59-.78, l.39-40 П3 .68-.85/.39-.63, l.46 ticked .48-.66/.10-.23, l.47 'model for V_pub exp85a'.
- Reproduced MC: scratchpad r31v/mc31v.py (imports r26/mc26.py + r21/mc20.py read-only; field 02:14Z minus own row; HOURS 21.75; rates top .95 mid 5.5 b954 .7 b953 0; VPUB exp87a; seed 11). Base: {87a,#37} .741/.540; {87a,75} .779/.571; {87a,85a} .706/.549; ticked .382/.071. 6 scen ranges: {87a,75} .70-.85, {87a,#37} .66-.82, {87a,85a} .61-.76, ticked .20-.57 -> EXACT match with the finding.
- Sensitivity (base): RMID 2.3 -> ticked .433, #37 .765, 75 .799; RMID 9 -> ticked .341, #37 .722, 75 .770; seed 23 within .012; central + RGROW 1.0-1.6 -> ticked .165. Most of the ticked drop comes from the new starting field, not the growth extrapolation. Order robust.
- CAVEAT: R28 CI prior (0.0002/0.0010) base SILVER: {87a,85a} .528 > {87a,75} .520 > {87a,#37} .499 (bronze .687 < .711/.717). So 'exp85a never better' (scan_recheck.json text) is false for silver; ordering claim holds for bronze only. Card must not state silver ordering as settled.
- Not a duplicate of rounds 2-30 (grep straddl/rank arithmetic); same-round scan_hyp_private31 has a parallel public-rank update (compatible).
- Feasibility: card text only, no submit/GPU/API; fits R1-R10; the model remains judgmental (ranks, not decides).
- 02:32Z wrote JSON (refuted=false)
