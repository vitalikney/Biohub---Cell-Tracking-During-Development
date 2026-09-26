# ins_cap6 notes (started 2026-09-26T21:48Z)
- Task: exp60 x138 lab (56 clips; dumps _dl/exp60_a + _dl/exp60_b), DaughterNet insertion cap 6 vs ins35 (cap 4); context caps 5, 8. Pre-registered: exp70g (cap 6) at 00:05Z iff pooled delta >= 0 AND neither embryo < -0.0005; else exp70b.
- exp70g notebook checked: BIOHUB_DIVINS_ENABLE 1, STEAL 1, CAP 6, FRAME_CAP 1, ALPHA 1, THRESH 0.4 (exp70b: same with CAP 4 + forkmid 4.5).
- Scratch (tools/ not edited): scratchpad/cap6/cap_sweep.py imports tools/trainlab.py + tools/div_insert.py unchanged; params = dict(trainlab.INS35) with only cap_video changed. div_insert derives steal_cap = floor(0.5 * cap_video), as the kernel does from BIOHUB_DIVINS_CAP: cap 4 -> 2 steals, cap 5 -> 2, cap 6 -> 3, cap 8 -> 4.
- 21:50Z smoke test 6bba_55b7eebe: trainlab.insert35 == cap-4 override (writer digest + stats); divins dump graph == final graph.
- 21:50Z full run started, 6 workers.
- 21:54Z run done (177 s wall, 6 workers; scratchpad/cap6/cap_sweep_raw.json). analyse.py -> cap_sweep_agg.json.
- PARITY: cap-4 replay ALL 0.9398779 (= recorded 0.93988), div 25/31/74; per-clip official rows AND writer digests identical to experiments/exp60_trainlab/results.json (ins35 and control) on all 56 clips; trainlab.insert35 == cap-4 override on all clips; divins dump graph == final graph everywhere. Control reproduces too (ALL 0.93340, div 16/25/83).
- RESULT vs ins35 (pooled official summarise; score = adj edge J + 0.1 div J):
  cap 5: ALL -0.00015 | 44b6 0.00000 | 6bba -0.00019 | div 25/32/74 | edge 38397/1684/1696 | W/L 1/1 | boot90 -0.00049..+0.00005
  cap 6: ALL -0.00057 | 44b6 -0.00079 | 6bba -0.00052 | div 25/35/74 | edge 38398/1685/1695 | W/L 1/4 | boot90 -0.00125..-0.00011 (P<0 0.98)
  cap 8: ALL +0.00003 | 44b6 -0.00079 | 6bba +0.00018 | div 26/36/73 | edge 38399/1686/1694 | W/L 2/5 | boot90 -0.00123..+0.00170
  (ins35 itself: ALL 0.93988, 44b6 0.91647 div 2/8/9, 6bba 0.94267 div 23/23/65; edge 38397/1684/1696.)
- cap 6 anatomy: 85 extra insertions (30 steals; superset of cap 4), parent-fork labels 0 TP / 4 FP / 81 metric-ignored. FP clips 44b6_e29f0176, 6bba_268e1230, 6bba_6ca87370, 6bba_7d3058ae (-0.00017 / -0.00010 each); the one win 6bba_786893ac +0.00002 (edge only). 44b6 -0.00079 = div term -0.00053 + adj edge -0.00027 (one FP fork on a 17-clip, 2/8/9 embryo).
- Cap binding: cap 4 -> 45/56 clips insert exactly 4 (45 have eligible candidates cut by the cap; 46 would insert more uncapped, 44b6_2f31fc2f is steal-cap-limited at 3). cap 6 -> 39/56 insert exactly 6 (38 cut; 34 would insert more). Uncapped total 525 insertions vs 201 at cap 4, 286 at cap 6.
- Extra-insertion DaughterNet scores: median 0.505 vs 0.587 for the cap-4 set (all >= 0.4 threshold).
- DECISION (pre-registered): pooled -0.00057 < 0 AND 44b6 -0.00079 < -0.0005 (6bba -0.00052 also < -0.0005) -> branch = exp70b at 00:05Z, not exp70g.
- Caveat: in-sample for DaughterNet (sign check only), and it is negative even in-sample. Small n: 4 evaluable marginal forks, 0 TP; at the ~0.16 break-even, 0/4 has P ~0.5, so this is not proof that cap 6 hurts out of sample, only that the lab shows no gain.
- 21:56Z ins_cap6.json written (complete). No repo file other than these two touched; nothing committed; Kaggle not touched.
