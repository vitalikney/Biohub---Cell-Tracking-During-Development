# PC19-03 verify notes
- 2026-09-27T18:14:48Z: started; no prior json. Folders: only exp76a/exp76d exist; exp73m has no output (no dummy). poll header 18:04:40Z: 45 (56606948) and 46 (56611472) PENDING. Builder sha d46a8b2d, coordinject_patch 78cae2a9 (unchanged vs round 18). Scratch ROOT for rebuild: /c/Users/vital/AppData/Local/Temp/claude/c--Users-vital-Documents-kAGGLE-Biohub---Cell-Tracking-During-Development/acabaea6-42c1-4115-a146-2ddc5bb7e8c8/scratchpad/r19root
- 18:20Z scratch rebuild (ROOT copy of tools/ + exp39/exp56 dirs, repo untouched), round-18 B/K/KQ/FM/CI/SW strings (round18/scan_hyp_slots_28sep.json build_env_git_bash):
  exp70b b8e7ece1 = repo, exp70q 33ab04d1 = repo, exp76a 98a9e647 = repo, exp73m 76c81122 = repo (builder d46a8b2d reproduces all refs).
  Draft names reproduce draft shas: exp76c_k2_maxdiv_ci 1bb648a4, exp76e_k2_fm_cap6 d5c5ff5e, exp76g_k2_maxdiv_secft 17bf5872.
- Diffs: exp76e vs exp70b = cell-0 name + DIVINS_CAP 4->6 only (meta id/title/code_file). exp76g vs exp70q = name + 2 SECONDARY env lines + sha default line; dataset += vitaliineibauer/biohub-secft-all-v1. exp76c vs exp70q = name + 2 COORDINJECT env lines + CI cell (identical text to exp76a's CI cell) + dataset += yuki0731/biohub-coord-inject.
- Queue: exp75 pushed 13:18Z, started ~16:50Z, while later pushes (exp72 13:27Z, exp76d ~15:50Z) ran first -> stalls are per-kernel and unpredictable, not only lane congestion (exp71 training ended 13:25Z). Round 18 already flagged the dummy gaps (v_hyp_slots_28sep_r18s-3 fix (b)); not actioned by 18:13Z.
- Runtime: exp76c = exp70q (dummy +24% vs K2) + CI; CI deadline is KERNEL_START + 37800 s, kill +900 s (tools/coordinject_patch.py l.260-310) -> L <= ~10.75 h, fail-soft, but CI coverage may be partial on this base.
- Quota: ~22 h left at Q1 (CONTEXT l.2729); since then exp71 ~2.3 h + ~6 dummies -> ~16 h; 4 dummies ~2-2.5 h: fine (weekly reset Sat).
- 2026-09-27T18:16:53Z: final JSON written (refuted=false).
