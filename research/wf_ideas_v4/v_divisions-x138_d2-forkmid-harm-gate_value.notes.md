# v_divisions-x138_d2-forkmid-harm-gate_value notes (started 2026-09-25T17:41:18Z)
- JSON did not exist at start -> fresh run.

## 17:43 UTC reading (local files only; no web needed - pure metric/power question)
- Current gate: research/wf_ideas_v3/TASK_CLOUD_SESSION.md T9 (l.~176): 0 TP removed per embryo; >=3 FP removed with >=1 on 44b6; TP mid margin >=0.7 um; nodes + inserted forks unchanged. Coded in tools/trainlab.py l.605-621 (fm["pass"]).
- Slot rule: CONTEXT.md l.1607 S4 "K3 = K2 + forkmid | audit E4 passed"; rules pre-registered 13:38 UTC with the user's OK, "apply mechanically, do not rewrite" -> changing what "audit passed" means needs the user's OK, not only a CONTEXT line.
- exp60: only kernel dirs + split.json in experiments/exp60_trainlab, no _dl/*exp60* -> no results downloaded yet (pre-registration still clean at 17:42 UTC).
- Metric (tools/official/metrics.md l.121-149): score = adj_edge_J + 0.1 * div_J, div J pooled over all videos. Un-forking an evaluable FP: +0.1*J/D; un-forking a TP: -0.1/D. Break-even TP-loss rate q* = k * J * FP/TP (k = fraction of evaluable FP forks removed).
- v3 skeptics (v_metric-math_fork-fp-removal-x138_value.json, v_divisions_fork-precision-geometry-rider_value.json): both refuted; EV public +0.0005..+0.0008, private +0.0003..+0.0008, P(<0) 0.17-0.20; both were computed at k = 14% (exp39 dose at 4.5 um: 6/43 FP).
- r1_research_fork-midpoint-filter.json: the 4.5 um threshold was chosen ON the 23 exp39 TP (max 3.76) -> "0/23 at 4.5" is selection, not evidence; it cannot be pooled into a harm bound. Gamma/lognormal fit on those TP: P(mid>=4)=2.4-3.8%, P(>=4.5)=1.0-2.2% -> P(>=3.8) ~3-4.8%.

## 17:50 UTC arithmetic ($TEMP/fm_mc.py)
- x138 dose is ~half exp39's (2/62 dummy forks >= 4.5 um) -> k ~0.04-0.14 instead of 0.14.
- q* (break-even TP-loss rate at 4.5 um): public 0.07*0.36*0.8 ~0.02; private (J 0.13-0.25, precision 0.25-0.6) median ~0.021. The fitted TP tail at 4.5 um (1.0-2.2% on exp39 coordinates, plus x138 head shift 0.74 um mean, plus unseen-embryo motion) straddles q* -> the private sign is a coin flip-plus.
- MC (G, r, precision, k 0.04-0.14, q 0.005-0.035): public EV +0.00005 (p10 -0.0019, p90 +0.0016, P<0 0.27, P=0 0.27); private EV +0.00007 (p10 -0.0008, p90 +0.0008, P<0 0.32); with q restricted to the fit 1.0-2.2%: private EV +0.00014, P<0 0.27. The idea's +0.0005 rider EV is the k=14% number and does not hold at x138's dose.
- Gate power: P(0 TP removed of n=15/20/25) = 0.74/0.67/0.60 at q=2% (break-even) and 0.54/0.44/0.36 at q=4% -> the "harm test" cannot tell a harmless rider (q~1%) from a break-even one (q~2-4%); it only catches gross harm (q >= 8-15%).
- Gate (b) (TP mid max <= 3.8 um) is a max statistic: P(pass) = (1-p38)^n = 0.29-0.63 for p38 3-4.8%, n 15-25 -> it, not the FP count, binds; the idea's "P(ship) 0.08 -> 0.6" is really ~0.25-0.5.
- Incremental EV of the gate change = dP(ship) ~0.2-0.4 x rider EV ~+0.0001 = ~+0.00003 private (vs the claimed +0.0002..+0.0004). Not measurable, not worth rewriting a pre-registered gate.
- Lab is not out-of-sample: train clips (x138 detector/edge net trained on them), so the lab TP-mid tail is biased low -> a harm gate on it is biased toward passing.
- In favour: nodes untouched (no node-multiplier artefact); not a closed line; dropping ">=1 FP on 44b6" is legitimate (lambda_44b6 0.1-0.4, gate power-dead); pooling 56 clips is legitimate (no parameter selected on the lab).
- VERDICT: refuted under the value/transfer lens. Fix: keep a benefit-conditioned gate (pooled >=3 FP removed, 0 TP removed, no 44b6 clause), drop exp39 0/23 from any bound, replace max-margin (b) with "<= 1 TP fork mid in [3.8, 4.5)", and log it with the user's OK before any exp60 JSON is opened.
- 17:44 UTC: final JSON written (refuted=true).
