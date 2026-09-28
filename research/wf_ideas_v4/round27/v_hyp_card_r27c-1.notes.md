# v_hyp_card_r27c-1 notes
- 2026-09-28T16:04:07Z start: skeptic review of R27C-1 (finals card v4)
- 2026-09-28T16:07:20Z card JSON parses; spec R26-A5(2) (round26/report.json) matched item by item; tie order matches CONTEXT 04:31Z line 3419 ('attributable UP > non-CI > fewer levers > earlier'); SELECTED API read-only proven (CONTEXT l.2132)
- mc26 grids (scratchpad r26/mc26_grid*.txt): {exp85a,#37} bronze 0.680-0.852, silver 0.392-0.632 (base 0.512) -> card P3 'серебро ~0.51' is base only; {exp85a,exp75} bronze 0.734-0.915 all runs (0.77-0.91 over CI mean>=0); ticked 0.475-0.657 / 0.104-0.225
- nightdry (round27/scan_hyp_nightdry.json): E10 copy would take probe 52 and shift list -> 'probe 52: exp89r = ' prefix token fragile; exp83c fallback uses 'probe 54: exp83c = '
- §2 header 'Модель ... выше по бронзе у П1' unconditional; conflicts with fallback rows (exp75 <=0.953/ERROR/NO-OP -> П3; 0.954 + C51 '-' -> П3 first); fill steps do not edit it
- 2026-09-28T16:07:49Z verdict: NOT refuted (bookkeeping, spec-faithful); 4 small fixes; JSON written
