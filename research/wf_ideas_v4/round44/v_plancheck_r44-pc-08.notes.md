# v_plancheck R44-PC-08 (skeptic, value + feasibility) - 2026-09-29 ~17:28-17:35Z (20:28-20:35 MSK)
- No prior v_plancheck_r44-pc-08.json; started fresh 17:28:01Z. 0 Kaggle API calls.
- Scratchpad <SP>=C:/Users/vital/AppData/Local/Temp/claude/.../acabaea6-.../scratchpad
- sha256[:8] mk_card_1837.py = a19e1bd6 (matches R41-A3). card_1203_sent.txt sha8 = 4fa899f9 (builder assert passes).
- `python <SP>/mk_card_1837.py --dry-all` from repo root: 35/35 "ok" (7 codes x 5 SELECTED sets), exit clean.
- Default --lb e10_20260929T1141Z: experiments/lb_poll/_lb/e10_20260929T1141Z/lb.csv (70 833 B, mtime 11:45:16Z) loaded by tools/uptest.load; truncated csv -> teams falls back to --teams 3994.
- PENDING:a text: "если прочитается >= 0.960, основным станет он (при 0.959 по вашему решению B остаётся exp87a)"; rule (1) line appends decision B; T3KEEP body keeps exp87a at 0.959. Consistent with decision B (13:30Z).
- Stale-line grep '#141|3 994|14:45 МСК|#148|17 из 22' = exactly 1 line in PENDING:a, T1:a_old, T1:a, T3KEEP:a, T5:b, T6:a, T8:a -> the rank line only; confirms R44-PC-01 single-line overwrite suffices.
- Minor: under windows cp1251 console, --show output needs PYTHONIOENCODING=utf-8 to print Cyrillic (the real run writes a utf-8 file, so no effect on the card).
- Verdict: recheck is accurate; nothing to refute; info only.
