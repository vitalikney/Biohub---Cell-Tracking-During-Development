# v_plancheck PC27-03 (skeptic: value + feasibility) - 2026-09-28
- Re-parsed _dl/<slug>/<slug>.log (JSON 'time'): end / 'mode = candidate' / post-MC:
  exp89p 1313/253/1059; exp89q 1576/519/1057; exp85a 1388/262/1126; exp89s 1566/436/1129;
  exp88a 1894/788/1107; exp88b 1654/501/1153. CI: exp79a 1712/235/1477; exp87a 1870/300/1569; exp89r 1959/486/1473.
- 6bba_05db0fb1 ILP: 89p 76.8 / 89q 76.7; 85a 76.1 / 89s 79.6; 88b 83.9 / 88a 87.0 (+3 s max, noise); 87a 82.9 / 89r 76.2.
- DIS really active: config dump 'ilp_disappearance_weight': 2.25 in 89q/89r/89s/88a, 2.0 in 89p/85a (early in log).
- Cause of the silent gap: in exp89q ipynb the code between 'Low-detection dump applied' (last line before gap, e.g. 66.7 s in 88a)
  and 'V1284 head patched' is `sorted(Path('/kaggle/input').rglob('biohub-v1284-head-s075/v1284_head.pt'))` - a recursive
  walk of all of /kaggle/input incl. the competition zarr chunk trees -> pure I/O noise (205-721 s). Tracking/ILP starts after it.
  DIS cannot act there. Finding is correct.
- Caveat (not DIS-specific): that rglob runs over the hidden test tree on rerun; shared by every K-family file and already inside
  the measured K2 hidden band (6.87-7.81 h). Do NOT patch gated files now (breaks byte identity).
- Caveat: no DIS file has a hidden-scale run in experiments/lb_poll/ledger.md; the 'no hidden cost' claim is an inference from equal
  dummy ILP times (ILP is where DIS acts; timeout 1200 s/dataset bounds it anyway).
- Verdict: NOT refuted. Pure doc correction (I306 + R26 fact 6); zero score gain; frees exp89q/r/s from a false runtime flag.
  Keep the rule-v2 2,100 s gate but read it as pre-stage-noise-dominated (see scan_plancheck notes 16:07Z).
