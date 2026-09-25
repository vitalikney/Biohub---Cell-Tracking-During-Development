# s_critic notes
- 2026-09-25T12:10:06Z start; s_critic.json absent -> fresh run
- 12:25 read BRIEF, browser_intel (all), CONTEXT tail, exp56 cells 0/2/4/5 (deadline + sequential repair loop after all GPU shards), build_probe_kernel divinsert block (no own try/except -> any exception = REPAIR FAILED fallback for the whole clip).
- Fact: cell 4 l.7 calls torch.cuda.get_device_name(0) in the parent -> fork-based repair workers cannot use CUDA; worker must be a fresh subprocess (exec cell 2 config + cell 5 defs; cell 2 is side-effect free).
- Fact: nobody proposed parallel repair, AMP or cudnn speedups (grep h_*/v_*/s_merge).
- Latency evidence (v_ensembles budget-aware schedule): #29/#30 7.0-7.2 h, #28/#31 7.5 h, #32/#33 7.8 h (incl. queue). Same GPU phase as x138.
- 12:45 runtime sim (scratchpad rt_sim.py/rt_sim2.py; inputs = dummy per-clip det+edges 233/246/230/268 s, ILP 32/21/6/90 s, x138 repair 47/59/11/109 s, exp57b repair 80/116/19/276 s, 2 shards, degraded clip = 25% of full repair, lognormal sd 0.25; rho = private repair/ILP density factor; GUESSES):
  mean degraded share / finish p95 (h):
  N=120 rho1.0: x138 verb 0.00/7.0 | x138 C01(34200) 0.00/7.0 | x138 par3+34200 0.00/5.6 | x57b C01gate 0.00/8.2 | x57b par3 0.00/6.4
  N=120 rho1.6: x138 verb 0.24/7.8 | C01 0.00/8.8 | par3 0.00/6.5 | x57b C01gate 0.01/9.6 | x57b par3 0.00/7.8
  N=140 rho1.0: x138 verb 0.14/7.7 | C01 0.00/8.1 | par3 0.00/6.5 | x57b C01gate 0.00/8.9 | x57b par3 0.00/7.5
  N=140 rho1.6: x138 verb 0.58/8.2 | C01 0.05/9.7 | par3 0.00/7.6 | x57b C01gate 0.18/9.8 | x57b par3 0.00/9.2
  N=160 rho1.0: x138 verb 0.55/8.0 | C01 0.00/9.2 | par3 0.00/7.4 | x57b C01gate 0.01/9.5 | x57b par3 0.00/8.6
  N=160 rho1.6: x138 verb 0.84/8.5 | C01 0.35/10.0 | par3 0.00/8.6 | x57b C01gate 0.39/10.0 | x57b par3 0.11/10.2
  N=180 rho1.0: x138 verb 0.86/8.2 | C01 0.19/9.7 | par3 0.00/8.3 | x57b C01gate 0.17/9.7 | x57b par3 0.00/9.6
  N=199 rho1.0: x138 verb 1.00 (=> public degraded => excluded by x138 0.953 unless hidden HW faster) | C01 0.50/10.0
  exp57b VERBATIM N=150 rho1.6: finish p50 12.2 h => #35 could TIME OUT, not just degrade.
- Reading: C01 alone leaves 5-35% of clips degraded when N=140-160 and private clips are ~1.6x denser than the dummies; 3 repair workers remove it up to N~180. x138 verbatim is degraded (private tail, public sorted first) in the N=140-160 world -> the 241-copy block would lose ~0.01-0.03 on private.
- Latency back-calibration idea: exp48/exp51 (same GPU phase, DaughterNet ungated, NO guard) scored within 7.5 h -> their dummy per-clip repair seconds turn L=7.5 h into an N bound; zero slot, needs local session to read exp48/49/51 logs.
