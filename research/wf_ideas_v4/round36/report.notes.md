- 2026-09-29T08:25:51Z report round36 started; no report.json existed
- 08:27Z CONTEXT read to l.4425 (last entry 08:23Z exp89t built; 08:19Z A-M2 rule (a) user choice supersedes 02:53Z (1)). No CLARIFY / 08:30Z log line yet.
- poll.log headers 08:18:17Z and 08:28:19Z: 56656147 exp89r and 56656157 exp75 PENDING; 56657612 exp89p COMPLETE 0.956.
- ledger 08:18:19Z: exp87a (9.30, 9.48] h; exp85a (7.01, 7.19]; exp89p (7.02, 7.20]; exp70q (7.64, 7.81] (forkmid, non-CI upper edge); exp79a (9.27, 9.45].
- card v5 sha8 a134d5e4 unchanged; it has NO 'exp89t = ' token, no exp89t lever count (step 5), exp89t not in the V_CI list (placeholders l.129); l.59 still says 'при Rr + и DIS ? слот A-M2 не используется' (02:53Z logic, superseded by rule (a)); DIS_READ source l.133 = the old branch-A dd code (superseded).
- experiments/exp89t_k2cap6_k_dis225_ci/probe.json: exp87a knobs + ILP_DISAPPEARANCE_WEIGHT 2.25 (confirmed).
- Skeptic survivors: PC36-01, PC36-02, PC36-06, R36PI-1. Refuted w/ fix: R36RC-1, R36H-3, R36-RC-A (info only), R36-RC-B, R36-RC-C (gated exp89t option). Refuted/drop: PC36-03, R36H-1, R36H-2.
- 08:31Z report MC (scratchpad r36rep/mc_t.py; u85a U(.9575,.9585), CI N(.001,.0008), SEC N(-.001,.0015), conditioned on displays 0.959/0.956; DIS N(0, .0010/.0015); SECxCI noise .0004; per-file noise .0003):
  P(exp89r disp >= .958) .36/.40. exp89t ungated: P(>=.960) .32/.37 (ub incl 0.959+UP .50); E[DIS|switch] +.00076/+.00118.
  | dR>=.958: P(>=.960) .69/.80, E[DIS|sw] +.0010/+.0015; | dR<=.957: P(>=.960) .11/.09, E[DIS|sw] +.00035/+.00041. Gate keeps 62-73% of switches.
  exp89s switch | dR>=.958: .37/.56 (ub).
- Timing: exp89t ungated ~09:00-09:05Z -> read 18:16-18:34Z (tail 10.9 h -> <=19:59Z). Gated at exp89r header 09:23-09:40Z -> 18:41-19:09Z (after 18:37Z card, before 19:43Z); L>10.3-10.6 h misses 20:00Z. Proposed gated cutoff 10:00Z.
- 2026-09-29T08:33:08Z report.json + REPORT.md written (5 actionable: R36-A1..A5)
