## 2026-09-27T01:16:45Z start GF-4 verification
- 01:18Z recomputed _dl/exp60_a|b/retention_guard_*.jsonl (5,600 unique frames, 56 clips x 100):
  44b6 non-fallback 1137 fr: blended 329,646 vs primary 335,525 (0.982); bgtp 377; excess +2,582, deficit -8,461
  44b6 fallback 563 fr: 136,124 vs 174,321 (0.781); bgtp 0 (!), deficit -38,197
  6bba non-fallback 3748 fr: 803,274 vs 807,232 (0.995); bgtp 1706; excess +7,415, deficit -11,373
  6bba fallback 152 fr: 28,943 vs 34,011 (0.851); bgtp 0
  => finding numbers reproduce. BUT in fallback frames the blend NEVER has more candidates than primary (0/715),
     so union there ~= primary set (x138's current output) + offset duplicates -> no gain there, only FP risk.
  => in non-fallback frames union adds at most the primary-only peaks (deficit 8,461 = 2.5% / 11,373 = 1.4%),
     i.e. peaks the 0.8 secondary blend suppressed (secondary disagrees) -> node lever, ~0.0009-0.001 J per 1% nodes
     => node-factor cost up to ~-0.0023 (44b6) / -0.0013 (6bba) before TP-edge offset (annotation 0.79% / 5.20%).
- IDEAS.md I-222 (retention-guard redesign) refuted/closed: 'would change the node set (R4) and needs a GPU lab';
  I-147/I-148 node levers negative on x138 both embryos. GF-4 = guard redesign + node-add lever -> closed family in disguise.
- Feasibility: no CPU lab (GF-2: no heatmaps/per-model candidates in dumps); GPU lab ~4 GPU-h, ~5 h wall; R8 27 Sep 12:00Z
  needs lab+dummy+NEW user OK; finding itself says 'later'. Post-deadline oracle has no competition value after 29 Sep.
- Verdict: refuted=true.
- 2026-09-27T01:18:24Z wrote v_hyp_gated_fusion_gf-4.json
