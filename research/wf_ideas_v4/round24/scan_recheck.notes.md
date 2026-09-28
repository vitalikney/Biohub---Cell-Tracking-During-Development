# Round 24 scan_recheck notes (started 2026-09-28 06:40 UTC)

- 06:40Z no round24/scan_recheck.json existed -> doing the task. Bash tool classifier failing; using Read/Grep/PowerShell.
- Already rechecked (skip): 66 RC ids in rounds 2-23 (R2..R23 scan_recheck.json), incl. R23 READMIT 0.94 / ILP div 0.4 / low-score node premise.
- State from CONTEXT l.3448-3521: probe 50 exp85a (cap6 + ILP div 0.4 + READMIT 0.94) submitted 05:02Z; exp85b/c dummies PASS
  (85b +49 nodes, near-inert; 85c +1,022 nodes, LOWREFINE +3.05%); exp86a/b/c branch builds (06:37Z); 47/48/49/50 PENDING at 06:22Z.
- 06:55Z PICK A = v3 s_merge C05 lowrefine '>= 0.965 only (head in distribution); 0.5-0.965 stay on grid'. tools/build_probe_kernel.py l.1652:
  _LOWREFINE_MIN_SCORE = float(os.environ.get('BIOHUB_READMIT_MIN_SCORE','0.965')) -> READMIT 0.94 silently extends refinement.
  Pool coords are on the pooled grid x downsample (l.'_lc[:, 1:] *= downsample', xy 4 px = 1.625 um) when not refined.
  Dummy logs: LOWREFINE refined exp70g 26532/33336/7370/76396 vs exp85c 26694/36487/7497/77342 (of 27877/51793/8518/81321; failed frames 0);
  readmitted exp70g 96/677/84/508 = 1,365 vs exp85c 167/1148/105/804 = 2,224 (+859).
  scratchpad r24rc/cmp85c.py (dummy CSVs _dl/biohub-exp70g-k2-cap6 vs _dl/biohub-exp85c-k2cap6-ra094): new nodes >1um 112/1041/23/681 = 1,857,
  lost >1um 31/434/6/364 = 835, moved <=1um 81/574/22/379 = 1,056; new nodes on the 4-px xy grid 9/75/2/68 = 154/1,857 = 8.3% (all exp70g nodes 7.3%,
  random 6.25%) -> band readmits carry head coords, not grid coords. Churn 2.9k nodes for +1,022 net.
- 07:00Z PICK B = I-183 readmit radius (v3 x138-tail-recalibration; closed as 'readmit/gapfill peaks unrefined int16 -> premise n/a; radius = node
  multiplier artefact', v_redteam-past_x138-tail-recalibration-refined-coords_value.notes.md l.5, l.11). K2 lowrefine now refines the pool -> that
  reason is void. scratchpad r24rc/radius_band.py (exp60 a+b, 56 clips, score >= 0.965, 2 um exclusion vs presafe nodes, distance to nearest open
  end/start anchor): (0,4] 4,325 (17 within 4 um of GT); (4,5] 3,078 (+0.27% of 1,124,511 final nodes; 13 near GT); (5,6] 3,812 (+0.34%; 27 near GT);
  44b6 1,174/1,471, 6bba 1,904/2,341. Lab blind (R23-RC-C) -> node cost only.
- 07:05Z PICK C = ILP_DIVISION_WEIGHT (RESULTS probe 3 0.9 neutral; R11-RC-B; R23-RC-B 'no output channel'; CONTEXT 06:26Z 'exp85b near-inert,
  near-duplicate of exp70g'). run_stats.csv diffs (_dl dummies): safe_divisions_added exp70g 35/6/5/17 (63) -> exp85b 36/7/5/18 (66); exp85c 63 ->
  exp85a 66; divins_added exp70g 6/0/6/6 = exp85b; exp85c 6/1/6/6 = exp85a (readmit adds 1 insertion on 44b6_0b24845f). raw_nodes +7/+30/0/+47;
  motion_relink_replaced_raw_edges +154/+127/+25/+526; division_like_sources +1/+1/0/+1. Forks: 81 = 63 safe + 18 ins; 85b 84 = 66+18; 85c 82 = 63+19;
  85a 85 = 66+19 -> exactly additive. scratchpad r24rc/cmp2.py: exp70g->exp85b nodes same 120,945 / moved<=1um 83 / new 273 / lost 224;
  exp85c->exp85a same numbers (83/271/217). add_safe_divisions_postlink (exp70g cell 7 l.1498-1636) is purely geometric on the post-relink graph
  (orphan candidates = nodes with no incoming edge) -> channel = ILP keeps more daughter nodes (raw nodes +84) that the 1:1 relink leaves as orphans.
- 06:42:35Z poll header: 47/48/49/50 all PENDING.
- kaggle_feed digest 0630Z: 732103 Jose Freitas 'it works! I'm at 0.960' with hengck23 synthetic 18.5 GB (165k labelled divisions).
- 07:12Z final JSON written (research/wf_ideas_v4/round24/scan_recheck.json): picks C (ILP safe-division channel, urgency now), A (lowrefine coupling benign), B (readmit radius stays closed) + NF probe-50 anatomy.
