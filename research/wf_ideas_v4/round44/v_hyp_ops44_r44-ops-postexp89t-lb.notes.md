# v_hyp_ops44 r44-ops-postexp89t-lb notes (2026-09-29T17:28:10Z)
- 17:29Z checks (0 Kaggle calls):
  - <SP>/mk_card_1837.py (186 lines): a.lb used only at l.69 uptest.load(a.lb), l.72-74 folder mtime + label suffix, l.76 the 'Мы на ЛБ (' line (and teams count on it). Default --lb e10_20260929T1141Z, --teams 3994 (l.167-168).
  - R43-A5 (round43/report.json l.32-36): overwrite 'Мы на ЛБ (' line after build in ANY code; readtime.sh cardfix() -> r44dry/cardfix44.py replaces the full line, asserts one 'Мы на ЛБ (Chrome' and no '#141|3 994|14:45 МСК'. readtime.sh cardcmd already hard-passes --lb e10 --teams 3994.
  - experiments/lb_poll/_lb/post_exp89t: does not exist -> uptest.load glob empty -> sorted([])[-1] IndexError (crash); l.73 max() over empty listdir would also crash. Plus a race if watcher saves mid-build.
  - Win32_Process 30864 cmdline confirmed: saves 'uptest.py save post_exp89t' only if last block matches '^56669888,.*COMPLETE,0[.]959,' (T3KEEP under decision B -> no promo -> no suffix; rank line overwritten by cardfix anyway).
  - e10 folder: lb.csv 70 833 B (truncated, so --teams 3994 path). --dry-all 35/35 ok now.
  - Supersedes R43-A2 (b) ('pass --lb post_exp89t only if bud7lhxmi.output has rank with count 57'): no card effect; bud7lhxmi.output remains info only.
- Verdict: not refuted; info-level ops simplification, no score value, strictly reduces crash risk.
