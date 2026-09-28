# v_hyp_card R27C-4 notes (2026-09-28T16:04:07Z)
- No prior v_hyp_card_r27c-4.json existed; fresh verification.
- Independent parser scratchpad/v27c4.py over _dl/biohub-exp{7,8}*/ *.log and _dl/biohub-exp89*/ *.log (local copies, no Kaggle API call).
  Reproduced exactly: exp85a T1388 gpu0 262 T-gpu0 1126 | exp89s 1566/436/1130 | exp89p 1313/253/1060 | exp89q 1576/519/1057 | exp88b 1654/501/1153 | exp88a 1894/788/1106 | exp70g 1409/355/1054 | exp88c(DIS1.75) 1405/296/1109 | exp89r 1959/486/1473 vs exp87a 1870/300/1570.
  ILP sums (both ILP lines per clip): 89p 245.4 = 89q 245.4; 85a 257.0 vs 89s 259.0; 70g 262.0 vs 88a 285.4 (+9%, only DIS pair with a gap; after-setup +5%).
- Setup spread on NON-DIS runs too: exp70q 746, exp85b 640, exp85c 636, exp75 643, exp70a 581 s -> not DIS-specific. (4/4 DIS-2.25 setups are above the non-DIS median ~340 s; p~1/16 by chance, but see mechanism.)
- MECHANISM: the silent gap is 'Low-detection dump applied' (~46 s) -> 'V1284 head patched' print. Code between them (experiments/exp89q_k2cap6_k_sec_dis225/exp89q-k2cap6-k-sec-dis225.ipynb cell 4): write v1284 module + `sorted(Path('/kaggle/input').rglob('biohub-v1284-head-s075/v1284_head.pt'))` = full recursive walk of /kaggle/input (competition zarr trees) -> filesystem I/O noise, reads no config, runs before GPU prediction and before ILP. DIS cannot influence it.
- Correct pairing note: exp88a's parent is exp70g (not exp88b = TAU 0.7); after-setup 1106 vs 1054 (+5%), still within the 1,028-1,170 non-CI band.
- Target line: research/wf_ideas_v4/round26/report.json new_facts item 6 ('DIS 2.25 dummies ran +15-20% vs their siblings'). Not yet corrected in CONTEXT.md (checked l.3956-3998). Same finding as scan_recheck R27-RC-B (duplicate; merge).
- Hidden L of DIS files: no DIS file has ever been read on hidden test -> 'parent family' is an inference, supported by identical ILP time and bounded ILP timeout=1200 s per clip.
- 2026-09-28T16:06:27Z wrote v_hyp_card_r27c-4.json (refuted=false, info-only, merge with R27-RC-B)
