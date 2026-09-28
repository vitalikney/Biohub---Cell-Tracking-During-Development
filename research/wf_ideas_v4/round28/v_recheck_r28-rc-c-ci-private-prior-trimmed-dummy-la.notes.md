# v_recheck R28-RC-C notes
- 2026-09-28T19:50:41Z start; no prior answer json
- 19:55Z read scan_recheck.json RC-C, scan_recheck.notes.md 20:10Z/20:14Z, bigger_levers/prep_coord_refiner.notes.md l.12 + 12:32Z lab, CONTEXT 14:12Z PARTNER RULE v2, 16:26Z GAP RULE v2.
- Recomputed per clip from scratchpad r28/dummy_lab_exp{79a,87a,75,58}.json + r26/dummy_lab_exp{70g,85a}.json (adj_edge_jaccard):
  exp79a-exp70g: 44b6_0113 0, 44b6_0b24 0, 6bba_05b6 -0.00578 (TP-2 FP+3), 6bba_05db -0.00568 (TP-2 FP+6); clip mean -0.0029; pooled 'all' -0.00549.
  exp87a-exp85a: 0,0,-0.00578,-0.00501; exp75-exp58: identical to 79a-70g. => the 3 pairs are ONE observation (same CI moves on near-identical graphs), not 3/3 replication.
  Pooled score is GT-edge weighted: 6bba ~2030 of ~2130 GT edges; 44b6 dummy clips have 50/49 GT edges -> '44b6 unchanged' is unmeasured, not evidence.
  Whole effect = 13 edge events (TP-4, FP+9) of ~2130 GT edges, 2 clips, in-sample -> noise-level.
- CI bed +0.0032 (alpha 0.5) was SELECTED from 7 arms on the same 4 clips (prep_coord_refiner 12:32Z) -> optimistic; dummy is the only unselected replication. The finding pools them as equal.
- Internal inconsistency: action (3) says dummy lab has the WRONG sign for CI and must never be a sign read, yet the same dummy read is the only new input that lowers the prior 0.65-0.75 -> 0.55-0.65.
- Action (2) (exp75 = 0.954 -> A first) contradicts 'no change to partner rule' AND its own model: central +0.0002 > mc26 break-even (-0.0002..-0.0004) still favours B. Rule v2 already puts A first when probe 51 reads '-'.
- Probe 51 (exp87a K+CI vs exp85a K, 56640366) PENDING, read ~20:50-22:15Z = a 2nd out-of-embryo CI LB read, strictly more informative than the dummy lab; card caveat text must be conditional on it.
- Verdict: refuted (prior revision not supported by independent evidence; action (2) inconsistent); keep only a corrected card caveat and action (3).
- 19:52Z wrote v_recheck_r28-rc-c-ci-private-prior-trimmed-dummy-la.json (refuted=true)
