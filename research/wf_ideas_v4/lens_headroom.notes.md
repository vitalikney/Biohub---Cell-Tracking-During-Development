# lens_headroom notes (started 2026-09-25T17:21:16Z)
- 17:25 Read CONTEXT.md tail (§e/§f v3 rules, dummy gates 18/18 green at 17:45), step0.md, exp56 timing.
- x138 GPU phase facts (experiments/runtime_step0/exp56-x138-verbatim_timing.txt): per clip "detection+edges" 230-268 s on ONE T4 shard,
  nearly independent of node count (7,370 vs 76,396 nodes: 230 vs 268 s) -> encode-bound (fixed volume x T frames x 16 encodes).
  ILP 5.5-89.6 s per clip (timeout 1200 s, far from binding). Repair (CPU, sequential AFTER the whole GPU phase): 11-109 s/clip x138,
  exp57b 19-276 s/clip (insertion ~66 s/clip mean; divins_sec_score 171 s on 6bba_05db0fb1 = the bulk).
- x138 ALREADY runs: primary det D4 8 views + edge-feature TTA 8 views (features averaged), secondary det 8 views + secondary edge-feature TTA
  (w 0.75), DeepCenter 8-view TTA (scratchpad dump of x138 cells, cell 4 lines ~1122-1417, cell 5 ~2125). So "more D4 views" is saturated;
  z-flip / axis-flip closed (probe 19, R9); third detector blend refuted (v3 v_ensembles-and-private_third-detector-heatmap-blend_value.json).
- tools/repo/scripts/predict_unet_transformer.py: W=2, stride 1; frame t (t>=1) detected ONLY from window [t-1,t] pos-1; pos-0 logits of
  window [t,t+1] computed and discarded (= tempfuse E7, already planned, zero GPU). _load_frame = zarr[t, ::1, ::4, ::4] strided, no
  averaging -> 15/16 xy phases never seen. Polyphase for LOCALISATION refuted in v2 (r1_verify_polyphase-*.json: <= +0.0005 on top of head).
- Head cascade (2nd V1284 pass) refuted v3 (v_github-intel_head-cascade_value.json: +0.0005, head calibrated).
- Budget-aware deadline refuted as standalone (v3 v_ensembles-and-private_x138-budget-aware-deadline_*): value only in worlds where the timer fires.
- 17:40 Dummy logs (_dl/biohub-exp58*/ *.log, parsed 'repair Xs' / 'detection+edges' lines):
  K2 (exp58) repair 81.7 / 119.9 / 20.4 / 287.2 s = 127.3 s/clip (exp57b 122.9, exp56 56.6) -> lowrefine +4.4 s/clip.
  K2 GPU 'detection+edges' 211.6-235.5 s per clip per shard (exp56 run: 229.9-267.5 -> run-to-run jitter ~+-12%);
  setup before shard launch 257-636 s across our 6 dummies. DaughterNet on cuda; divinsert 'score' 9.9-185.5 s/clip (mean ~75 s).
  FD (deadline fired at 975 s): degraded repair 28.1 / 32.2 / 6.6 / 45.7 s = 28.2 s/clip (safe-div + linefit kept).
- Forecast K2 <= L35_hi 7.73 h + 106 x 4.4 s = 7.86 h (runtime <= latency; true runtime likely lower).
  Insertion gate 8.0 h = +0.14 h over worst case; repair deadline 9.5 h = +1.64 h; 12 h limit = +4.1 h.
- Per-encode cost: 16 encodes (primary+secondary x 8 D4 views) ~ 215 s/clip/shard -> ~13 s per extra encode per clip per shard
  -> ~6.5 s/clip wall with 2 shards -> +0.19 h per extra encode at N=106.
- Value asymmetry (v3 v_ensembles-and-private_x138-budget-aware-deadline_value.json: degraded ~0.05-0.065 per unit fraction without
  safetail; with safetail keeping safe-div+linefit ~0.015-0.02): 1 degraded clip ~= 15-55 clips of insertion (#35-#34 = +0.001 total).
  => the 8.0 h insertion gate PROTECTS repair time; do not move it later unless REPAIR moves too.
- Slow-world arithmetic (N=106, rerun s x slower than dummy speed): s=1.25 -> GPU ends 5.97 h, full repair 159 s/clip -> 10.65 h
  total; REPAIR 9.5 h -> ~26 clips degraded; REPAIR 10.5 h -> ~3 degraded. Post-deadline tail = R x 28 s x s <= 106 x 28 x 1.5
  = 1.24 h -> 10.5 h deadline still ends <= 11.8 h worst case; for N=199 'fast hardware' world s~0.55 -> 0.85 h. Timeout-safe.
- grep of all research/wf_ideas_v3/v_*_value.json for timer/runtime: NO refuted idea was killed by runtime alone (simview pool
  +0.0002 anyway; optional-nodes ILP value ~0). Headroom unlocks nothing already reviewed.
- LB history of extra views (experiments/RESULTS.md): z-flip probes 12/16 -0.003/-0.009, axis-flip probe 19 -0.001 (local +0.021),
  secondary weight 0.8->0.5 -0.002, 3rd/fine-tuned secondaries -0.007..-0.025. DIVINS_DEADLINE_S is a free --set knob;
  REPAIR_DEADLINE_S whitelisted to 34200 unless --lab (tools/build_probe_kernel.py l.1847-1850).
- 17:50 pilkwang primary/secondary were trained on ALL 199 train videos (CONTEXT.md l.235) -> any detector-map TTA lab on train clips
  is in-sample; only honest pre-LB test = friend A LOEO harness (friend_a_exp02_loeo20, 12 LOEO-44b6 videos), same as tempfuse fix (a).
- Considered and dropped under this lens: more D4 views (saturated: 8+8 det, 8+8 edge-feature, 8 DeepCenter already), z/axis flips
  (closed, R9), 2nd V1284 pass (refuted v3), denser kNN / more ILP candidates (ILP selects nodes only; flow relink rebuilds edges;
  optional-nodes refuted), readmit/gapfill radii (knob ladders, R4/R9), DaughterNet flip-TTA (cost +45-70 s/clip for ~+0.0002;
  eligible-only re-score costs ~0 but changes forks unmeasurably), pipelined repair on idle GPUs (N1-class; not triggered).
- Ideas kept: H1 REPAIR_DEADLINE 9.5 -> 10.5 h for K3+/F1-final with a per-rider runtime ledger (insertion gate stays 8.0 h);
  H2 optional polyphase (2,2) detection view bundled with tempfuse, coupled gate shift, LOEO-gated.
- 17:33 UTC final JSON written to research/wf_ideas_v4/lens_headroom.json (2 ideas + critique)
