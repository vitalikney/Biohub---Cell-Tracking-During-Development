# s_critic notes
- 2026-09-25T12:10:06Z start; s_critic.json absent -> fresh run
- 12:25 read BRIEF, browser_intel (all), CONTEXT tail, exp56 cells 0/2/4/5 (deadline + sequential repair loop after all GPU shards), build_probe_kernel divinsert block (no own try/except -> any exception = REPAIR FAILED fallback for the whole clip).
- Fact: cell 4 l.7 calls torch.cuda.get_device_name(0) in the parent -> fork-based repair workers cannot use CUDA; worker must be a fresh subprocess (exec cell 2 config + cell 5 defs; cell 2 is side-effect free).
- Fact: nobody proposed parallel repair, AMP or cudnn speedups (grep h_*/v_*/s_merge).
- Latency evidence (v_ensembles budget-aware schedule): #29/#30 7.0-7.2 h, #28/#31 7.5 h, #32/#33 7.8 h (incl. queue). Same GPU phase as x138.
