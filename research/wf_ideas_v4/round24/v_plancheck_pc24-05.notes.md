# v_plancheck_pc24-05 notes (2026-09-28T07:02:45Z)
- 07:05Z CONTEXT l.3516-3520: exp86a/b dummies pushed 06:36Z, gate = scratchpad gate85.py. gate85.py l.44: PASS = csv ok & 0 errs & runtime<=1900 & |dn|<=1.5% (forks, lowrefine, DIVINS only printed).
- 07:08Z _dl/biohub-exp86a-k2cap8-div04-ra094 and _dl/biohub-exp86b-k2cap12fc2-div04-ra094 ALREADY DOWNLOADED (~07:01Z).
- Node-row sha12 (dataset,node_id,t,z,y,x): exp70g = exp78a = exp78b = exp80a = 4cc8927e02a4 (121,252) -> cap/fc never change node rows (confirmed on 4 files).
  exp85a = exp86a = exp86b = 30e1c6e46704 (122,328). exp85b 773a4a6ba5c5 (121,301), exp85c 8b9e6352a0c1 (122,274) -> identity with exp85a proves both ILP 0.4 and READMIT 0.94 are live.
- Edges/forks (source with >=2 targets): exp85a 118,137/85; exp86a 118,141/90 (exp78a 86); exp86b 118,146/99 (exp78b 95) -> cap and fc live.
- gate85 run: exp86a PASS (1460 s, 0 errs, lowrefine 148,020, CSV ddbd6c026e6c); exp86b PASS (1357 s, 0 errs, lowrefine 148,020, CSV 9e41dc0abbcb).
- ERROR in finding: 'DIVINS ENABLED x4' - log has ONE 'DIVINS ENABLED: 5 DaughterNet model(s)' line (also x1 in exp85a). Per-clip evidence = 4 'divinsert: triples=... added=' lines (added 1/7/8/8 in exp86a). As written the item would fail a good file.
- 07:12Z final JSON written (refuted=false, DIVINS x4 item corrected)
