# v_recheck R39-RC-B notes (2026-09-29T11:24:28Z)
- started; no prior answer file
- read scan_recheck.json (R39-RC-B source), scratchpad r39/mc39_cprior.txt, r26/mc26.py, card_fill_1203_v3.txt
- mc26: exp79a=b+C+CI, exp85a=b+C+K, exp87a=b+C+K+CI, #37=b, exp75=b+CI; C only via CMODE=norm draw. Structure OK.
- Recount of mc39_cprior.txt (12 runs = 6 configs x 2 seeds; seed spread <=0.006):
  bronze: exp79a below #37 and exp75 12/12; exp85a below #37 12/12, above exp75 1/12 (C+.0004 sd.0012 s39 .832 vs .831)
  silver: exp85a ABOVE #37 12/12 (incl. lab prior C-.0006: .485/.491 vs .474/.490); exp79a above #37 4/12 (+1 tie); exp85a above exp75 2/12
  Eval: exp85a > #37 2/12; exp75 > #37 10/12; silver exp75 > #37 12/12; bronze exp75 > #37 7/12
- => headline '12/12 below both cap-4 partners' and the Russian user line are FALSE on silver (JT neighbour beats #37 on silver in every run). Correct: bronze only; on silver only exp75 dominates.
- Lab prior -0.0006 is in-sample on train clips (memory: lab over-trusts in-sample) -> weak prior. MC is judgmental ('ranks only', I-092).
- Verdict: refuted as written (wrong claim + wrong user-facing sentence); plan outcome (no card change) survives, P2 slightly favoured by this MC.
- 2026-09-29T11:26:00Z final JSON written (refuted=true)
