# v_divisions-x138 D2-forkmid-harm-gate — feasibility/schedule skeptic notes
- 2026-09-25T17:41:14Z started; no prior json existed.
- 17:45Z sources read: CONTEXT.md l.1560-1853 (pre-reg v3 §e/§f, 17:20Z dummy gates 16/16, 17:45Z FF PASS, 17:55Z night plan);
  research/wf_ideas_v3/TASK_CLOUD_SESSION.md l.172-183 (T9 gate: 0 TP per embryo, >=3 FP, >=1 on 44b6, TP margin >=0.7 um,
  nodes/inserted unchanged); FINAL_REPORT.md l.112 (C04 P(audit) ~0.6), l.204 (S4), l.244 (R3); s_merge.json C04.
- tools/trainlab.py: forkmid() l.318 = the C04 rule; gates() l.605-622 already uses ALL lab clips (no SELECTION/CONFIRMATION
  split for forkmid) and "0 TP per embryo" == "0 TP pooled" -> the only substantive changes of D2 are dropping ">=3 FP, >=1 on
  44b6" and adding (c) FP>=1 & FP>TP and (d) pooled adj_edge >= -0.0002. aggregate() l.553 has no pooled-across-embryo key ->
  (d) needs ~10 lines (summarise_rows over both embryos' per-clip rows) or a post-hoc script. tests/test_trainlab.py l.446-461
  asserts the old gate -> implement as an ADDITIVE key (g["forkmid_v2"]) so tests stay green.
- exp60 kernel (experiments/exp60_trainlab/kernel_a/probe.json): x138 + safetail(40000) + divinsert dump-only; NO lowrefine;
  kernel writes dumps only (TRAINLAB SUMMARY = written files), forkmid labels/counts appear ONLY at local
  `python tools/trainlab.py score` -> the pre-registration deadline is "before the first local score run" (download is safe).
  No local exp60 outputs exist at 17:45Z (ls experiments/exp60_trainlab, _dl). Shard A pushed 17:15Z (~2 h), shard B after FF.
- Dose re-check (tools/forkmid_dose.py, scratchpad): K2 exp58 dummy: base forks 61, 1 >= 4.5 um (exp56 base had 2 of 62) ->
  lowrefine moves fork geometry; 14 forks new vs exp56 (K1 exp58t: 12 new = inserted). So the lab control (no lowrefine) is
  not K3's coordinate regime: coverage gap, mechanics covered by the K3 dummy gate (§e item 4).
- Power of retained (b): exp39 23 TP forks, max mid 3.76 um. With n~15-25 new lab TP forks from a similar distribution, the
  chance that the new max exceeds the old one is n/(23+n) ~0.4-0.5 -> (b) (TP max <= 3.8) becomes the binding clause;
  P(pass new gate) ~0.35-0.5 by my arithmetic (not 0.6). Still >> old ~0.08.
- Schedule: lab dumps tonight (~19:15-20:30Z), local score (CPU replays, ~several h) -> T9 26.09 ~02:00-09:00; K3 build 1 command
  (CONTEXT l.1790), K3 dummy ~0.5 GPU-h (quota ~5 h left before reset, 30 h after); S4 26.09 10:00-13:00, latency 7-8 h ->
  score ~18:00-21:00 26.09, well before R8 27.09 12:00; fallback S7. Hidden-run cost: < 1 s/clip x ~100 clips < 2 min vs ~4 h headroom.
- Byte-identical off: FORKMID_ENABLE=0 default, tests/test_forkmid.py; fail-soft 'FORKMID FAILED' (T6, CONTEXT l.1753). Gate
  change touches no kernel code.
- Governance: §e/§f are "apply mechanically, do not rewrite"; the T9 gate text is in the task card (not verbatim §e), §e S4 says
  only "аудит E4 пройден". Night standing OK covers researcher actions; amendment must be logged in CONTEXT with UTC time before
  any trainlab score run, and shown to the user in the morning.
- 17:55Z verdict: NOT refuted on feasibility/schedule, with conditions (timing of the log line, additive gate key, EV discounted).
- 2026-09-25T17:45:00Z final JSON written.
