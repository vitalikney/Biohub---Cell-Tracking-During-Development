# v_hyp_successor R11S-2 skeptic notes
- 2026-09-26T17:15:58Z start; no prior json
- 2026-09-26T17:17:02Z read scan_hyp_successor.json/notes, CONTEXT 16:04-17:00 entries, scratchpad/succ_mc.py (seed 11)
- 2026-09-26 ~20:25Z reproduced succ_mc.py in memory (no new files; n=4000): s954 c150 e0.1 P0 .55 / P1 .85 / P2 .81 / P3 .71; s956 P0 .42 / P1 .93 / P2 .86. Matches the finding.
- Stress (in-memory string patches of succ_mc.py):
  g sd 0.5 (less 'second ticket'): P0 .57 P1 .84 P2 .79 (silver P2 .25 vs P1 .13)
  k=0: P0 .62 P1 .80 P2 .76 P3 .54 ; k=0 + g sd 0.5: P0 .69 P1 .76 P2 .75 P3 .55  -> swing only +0.06-0.07
  tie position random (early 0.5) c150: P1 .80 P2 .81 ; c300: P1 .72 P2 .78 ; early .8 c300: P1 .59 P2 .78
  g correlated with our delta (0.6 slope): P0 .57 P1 .79 P2 .77
  30% of variant teams port their own tweak onto the successor (max(d, g+0.5d)): P0 .50 P1 .81 P2 .77, silver P2 .26 vs P1 .10
  -> ORDER robust (action > none; never drop #37; {SI,port} fragile). MAGNITUDE '+0.25-0.45' is NOT robust: low end +0.06-0.14 (k=0 cases).
- LB CSV scratchpad/lb/...2026-09-26T17_05_53.csv: 3,932 rows, 0.953 = 354 teams, Score only 3 decimals -> exact unrounded ties of the x138 block (basis of the submit-time tie order) are NOT verifiable from the CSV; median SubmissionCount in the block 25 (active teams, not one-shot copiers -> many will stack their own tweaks on a successor, modelled above).
- Feasibility: R11S-2 is info only (no code, no submit), R8 not touched. SI rows valid only if R11S-4 tooling + proxy dummies land before 27 Sep 12:00Z; otherwise the table must drop SI rows.
- 2026-09-26T17:19:27Z final JSON written (refuted=false, magnitude caveats)
