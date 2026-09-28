- 2026-09-27T23:27:32Z start R21RK-8 verification (dummy>1900s runtime criterion)
- 23:2xZ 27 Sep: re-parsed _dl/*/<slug>.log (JSON time stamps) first mention DC/LOWREFINE/DIVINS/COORDINJECT/end:
  exp75 101/875/1286/1829/2288; exp79a 50/432/791/1258/1712; exp76a 45/656/983/1472/1896; exp70g 55/564/907/-/1409; exp70q 53/972/1317/-/1874. CONFIRMED.
  CI stage itself: exp75 459 s vs exp79a 454 s -> excess is pre-CI. DC->LOWREFINE interval varies 382-919 s on same code family -> machine variance.
- experiments/lb_poll/ledger.md: exp70g (7.49,7.67], exp70b (7.41,7.58], exp70q (7.64,7.81], 9 safetail rows (58,70a,b,d,e,g,j,k,q) L 6.87..7.81 h, 0 ERR. CONFIRMED.
  dummy 1409->1874 (x1.33) mapped to hidden L_hi 7.67->7.81 (x1.02): dummy length weak predictor.
- grep '1,900|1900' over CONTEXT.md, ledger, research/wf_ideas_v4: no pre-registered '>1,900 s' criterion for cap rungs exists (only exp72 gate and N2 gate '<= 1,920 s', CONTEXT l.2745, l.3290). So 'drop' = no-op; NO-GO list already in RK-1 go_no_go.
- Caveat: no file >1,900 s ever ran hidden (n=3 points all <1,900 s) -> claim about >1,900 s is extrapolation, but moot: cap rungs 78a/78b/80a are 1,369-1,486 s; exp75 not submitted.
- Verdict: not refuted (facts hold), realistic gain 0 (bookkeeping).
