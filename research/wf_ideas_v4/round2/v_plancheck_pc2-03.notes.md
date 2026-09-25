# PC2-03 notes (2026-09-25T20:22:55Z)
- 20:25 UTC: no prior json; exp60_trainlab has only results_forkblob.* (T9 main score NOT on disk yet; CONTEXT l.1923 "running").
- tools/trainlab.py l.730-745 verified: arms_dc excludes DC_CONTROL (0.25); best = max over non-control SELECTION deltas -> t* can never be 0.25; neigh = grid[k-1],grid[k+1] in range -> t*=0.15 has 1 neighbour (0.20); t*=0.20 neighbours 0.15 & 0.25 (conf_of[0.25]=0.0 < 0.001 -> strict fails always).
- L2 (in force) adds t_star_below_control (t*<0.25) -> 0.30/0.35 fail. decisions(): in_force = strict plateau AND L2. So in-force can pass ONLY at t*=0.15 (single-sided plateau). Finding confirmed.
- Pre-reg text research/wf_ideas_v3/TASK_CLOUD_SESSION.md l.176-181: ">= +0.001 при обоих соседних порогах"; "Если t* = 0.25, сборки нет"; "Дуги, опирающиеся на уверенность сети, дисконтировать до 0". s_plan_moonshot.json l.78 same.
- LB prior: CONTEXT l.699-703 sjlee101 forks: DC safe-div 0.20->0.15 = 0.946 vs 0.947 for 0.20 and 0.25 (old 0.947 stack). The only passable t* is the one with a (weak) negative public signal.
- With len(neigh)==2 + strict + L2(t*<0.25): gate is UNPASSABLE for every t* -> K3b effectively closed until user OK for L1; under L1 + 2-neighbour clause only t*=0.20 (check 0.15 >= +0.001) can pass. Must be stated as such (closure), not hidden as a bug fix.
- Round-1 overlap: rt2 value verdict already said "settle plateau NOW with STRICT reading"; d3 value: K3b ceiling a handful of events, net ~0. scan_plancheck.json item (3) is this finding. Not a repeat of a closed line; it is a gate-code fix.
- Verdict: NOT refuted (code-verified, tightening only, offline lab code => no kernel/byte-identity risk; must land before T9 numbers are read).
