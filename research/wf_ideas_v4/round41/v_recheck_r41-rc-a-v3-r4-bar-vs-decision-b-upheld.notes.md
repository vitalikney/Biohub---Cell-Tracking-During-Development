# v_recheck R41-RC-A (v3 R4 bar vs decision B) notes
- 2026-09-29T14:28:09Z: no prior json -> fresh. Reading CONTEXT tail, v3 FINAL_REPORT R4/(f), lb.csv.
- 14:29Z now; exp89t 56669888 still PENDING (poll.log header 14:19:28Z) -> recheck is pre-read, not post-hoc.
- Verified: CONTEXT l.4607-4617 decision B (13:34Z); l.2502-2505 R4 +0.002 lifted for public slot (26 Sep 21:31Z); v3 FINAL_REPORT (f) F1 = most complete build.
- Metric check: tools/official/src/tracking_cellmot/metrics.py l.29/l.420: J_adj = max(0, J*(1 - alpha*node_ratio)), linear, no upper cap -> node term (fewer nodes = bonus) is embryo-independent in form; 0.1*0.00768*0.91 = +0.00070 (arithmetic ok); dummy measured +0.00048 (R38-A2 INFO).
- Block arithmetic: 17th of 22 -> (16.5/22)*0.001 below top -> ~0.95875 (rounding) or ~0.95925 (truncation); gap to next display ~+0.00075 either way. OK.
- Skeptic points: (1) R38 rejected text already said node multiplier 'already priced into public' -> a 0.960 read implies public J-term >= ~0..+0.0003; private J-term shrinks toward lab prior which is mixed (exp13 parabola net -0.0007 => J ~ -0.0012 on older base; exp89t dummy FP flip +0.0004). Private expectation of the swap after a 0.960 read ~ +0.0002..+0.0006, not +0.0004..+0.0006 (sign still >= 0) -> promotion at 0.960 still right.
  (2) 'keeping exp87a costs at most ~0.0005' overclaims; spread +-0.0007 is symmetric -> 'about 0 on average'. The optional RU line 'в лучшем случае' is wrong wording (means 'at best'); use 'по оценке ~0 (±0.0007), в среднем ничего'.
  (3) T2 late-header prob <= ~1%: CI L 8.88-9.48 h -> finish 17:53-18:29Z vs 19:12Z mark; ok.
- Verdict: not refuted; action none; decision B stands (user decision, pre-registered). No build/slot/runtime involved.
