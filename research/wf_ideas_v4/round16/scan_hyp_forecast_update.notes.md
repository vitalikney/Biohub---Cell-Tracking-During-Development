# round 16 scan_hyp_forecast_update notes (files only, no API)

- 2026-09-27 08:31Z start. round16/ folder did not exist -> no cached answer; created.
- Read: CONTEXT.md l.2324-2334 (16:54Z PRIVATE RANK FORECAST), l.2599-2880 (22:46 RESUME .. D2 read 07:41Z), round15/REPORT.md,
  round15 v_recheck_r15-rc-c (E[max] / P(above block) MC: {#37,#38} 0.92-0.94 vs {#37,exp70d} 0.84-0.89; I~N(0.7e-3,0.7e-3)),
  round14 v_recheck_r14-rc-c (insertion honest OOF +0.0019 old base, precision 4/15, P(I<0) 0.10-0.20),
  reach0955/r_intel.json (band median subs 41-70; selection over ~50 variants ~+0.002-0.003 public with no true gain;
  variant jitter ~0.001-0.0015), research/KNOWLEDGE/IDEAS.md header (353 ideas; I-094 rank watch; I-283 private read).
- LB field from the watcher's fresh downloads (experiments/lb_poll/ladder_watch/<ts>/*.csv, local files):
  | snapshot | teams | >=0.960 | 0.955-0.959 | 0.954 | 0.953 | ours |
  | 26 Sep 16:20Z (CONTEXT) | 3,929 | 67 | 131 | 95 | 353 | #210 |
  | 27 Sep 04:13Z | 3,941 | 70 | 166 | 100 | 383 | #253 |
  | 27 Sep 04:56Z | 3,941 | 71 | 167 | 101 | 384 | #255 |
  | 27 Sep 07:37Z | 3,945 | 76 | 171 | 111 | 381 | #255 (8th of 111 in 0.954 block 248-358, after the exp70b UP) |
  rates 16:20Z->07:37Z (15.3 h): >=0.954 293->358 = 4.25/h (25->26 Sep was 4.4/h: steady); teams +1.0/h.
  0.953 block 359-739; below: 0.952 19, 0.951 12, 0.950 5, 0.949 21, 0.948 59, 0.947 473 (sjlee family), 0.946 136.
- Medal lines (Kaggle 1000+ teams: gold 10+0.2%N, silver 5%, bronze 10%): N_final ~3,990-4,030 -> bronze ~#399-403, silver ~#200, gold ~#18.
- 43/44 (DC 0.20/0.225) still PENDING at 08:31Z (poll.log l.12772-12774); scores expected ~12:20-13:10Z.

## 2026-09-27 ~08:40-09:10Z  model (MC, judgmental inputs; illustration, not a decision input per I-092)
- Scripts (scratchpad, session-only): <scratchpad>/r16/forecast_mc.py, forecast_mc2.py (correlated finals + copy-as-2nd-final),
  forecast_mc3.py (F/d sd params), diag.py, diag2.py, final_runs.py -> final_runs.txt.
- World: growth for 64.4 h at r x current rates (>=0.960 0.59/h, 0.955-0.959 2.6/h, 0.954 1.05/h, 0.953 1.8/h, teams 1.0/h);
  bronze = floor(0.10 N), silver = floor(0.05 N). x138 unrounded ~U(0.9526, 0.9534).
  Rival private delta D vs X: >=0.960 N(0.5 m, 0.002); 0.955-0.959: genuine share g -> N(0.6 m, 0.0012), rest selection =
  max of two finals N(beta m, s) with corr rho and prob k that the 2nd final is an exact copy (D = max(0, v)); 0.954 selection
  as above; 0.953 block: share c exact copies (D = 0, tie; tie order vs ours U(0.35,0.65)), rest max(0, N(-0.0003, s));
  0.948-0.952 N(0.7 m, 0.0015); 0.946-0.947 N(-0.004, 0.0015).
  Fields: overfit (r .4-.8, g .10-.25, beta 0-.10, s .5-1.0e-3, rho .6-.9, k .3-.6), mid (r .6-1.0, g .15-.35, beta .10-.25,
  rho .4-.8, k .2-.4), central (r .7-1.0, g .2-.4, beta .2-.35, independent finals), easy/hard (independent finals).
  Ours: eps (lowrefine) in {-1e-5, 0, +1e-5} w.p. .375/.25/.375 (F-MOD-17: ~1e-5, coin-flip sign, may be exactly 0);
  I (insertion, private) N(0.9,0.7)/N(0.6,0.8)/N(0.4,0.9) e-3 (P(I<0) .10/.23/.33; round 14 RC-C OOF +0.0019 old base,
  public +0.001 display x3); F (fm45) N(0.05e-3, 0.3 or 0.6e-3); d (DC 0.20/0.225 | display >= 0.955) mixture
  .35 N(+0.8e-3, sd) / .35 N(0, sd) / .30 N(-1.0e-3, sd), sd 1.2e-3 or 2.5e-3 (dc0.30 moved public -0.005; round 15 RC-C wide sigma 3-4e-3);
  lab-anchored sensitivity d ~ N(-0.8, 1.2)e-3 (6bba dc0.20 -0.0008, +6 FP forks, 0 TP).
- KEY DIAGNOSTIC: private rank of a file just above X (X+1e-9) at the deadline: overfit median 415 (10-90% 375-455;
  P(<= bronze) 0.32); mid 524 (480-570; 0.00); easy 504; central 602; hard 707. => X's own private rank is modelled at or
  below the bronze line (~#400) in every field; the 16:54Z premise 'bronze falls inside the x138 block, P(above block) ~ P(medal)'
  no longer holds once the >= 0.954 public group (358 at 07:37Z) grows to ~520-690 by the deadline.
- Hedge arithmetic (model-light): #38 pays only if I < 0 (0.10-0.33) AND eps > 0 (~0.35-0.5) AND rank(X+) <= bronze (0.0-0.35)
  -> <= 0.10 x ... central ~0.23 x 0.375 x 0.15 ~ 0.013; upper ~0.33 x 0.5 x 0.35 ~ 0.06.
- Scenario-weighted (fields overfit .30/mid .45/central .25; I opt .25/cen .5/pes .25; F/d sd sets 50/50), P(bronze+)/P(silver+):
  A {#37,#38} 0.57/0.18 (ranges 0.27-0.89 / 0.04-0.47); B {exp70b,#38} 0.59/0.23 (0.30-0.88 / 0.06-0.51);
  B2 {exp70b,#37} (I-298 shape, info) 0.64/0.26 (0.33-0.91 / 0.06-0.59);
  C1 {V*_C,#37} 0.72/0.41 (0.47-0.93 / 0.19-0.67); C1b {V*_C,exp70b} 0.74/0.44 (0.49-0.92 / 0.20-0.70); C2 {V*_C,#38} 0.54/0.34 (0.37-0.73 / 0.17-0.48).
  Lab-anchored d: overfit A .78/.32 C1 .79/.40 C2 .50/.21; mid A .55/.14 C1 .61/.21 C2 .31/.12 -> (b) never worse than (a) by > ~0.01; (c) can lose ~0.25.
  P(gold) ~0 for every option (gold ~#18, all 0.966+ public teams are far above).
- Runtime: every candidate is COMPLETE (#37 L 7.36-7.54 h, #38 6.69-6.87 h, exp70b 7.41-7.58 h; 43/44 pending) and the
  private score is computed in the same scored run, so no option carries a hidden-rerun runtime risk; the 8.0 h insertion
  gate did NOT fire for #37/exp70b. The runtime family is irrelevant to the pair choice.
- 2026-09-27 09:15Z final JSON written: research/wf_ideas_v4/round16/scan_hyp_forecast_update.json (7 findings r16fc-1..7). Round-16 browser 08:32Z (scan_browser.json) agrees with the 07:37Z field numbers.
