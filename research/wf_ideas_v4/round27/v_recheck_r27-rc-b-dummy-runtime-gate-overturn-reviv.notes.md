# R27-RC-B verify notes (2026-09-28T16:04:11Z)
- Source: _dl/biohub-*/biohub-*.log. Columns: whole = last log time; pre-GPU = time of the 'GPU shard 0' line; compute = whole - GPU shard 0 (in s).
  Non-CI: 70g 1407/355/1052; 85a 1386/262/1123; 85b 1719/640/1079; 85c 1734/636/1097; 86a 1458/294/1164; 86b 1355/290/1065; 86c 1558/473/1084;
  88a(DIS) 1892/788/1104; 88b 1652/501/1151; 88c 1403/296/1107; 89p 1311/253/1058; 89q(DIS) 1574/519/1055; 89s(DIS) 1564/436/1128.
  CI: 75 2285/643/1642; 79a 1710/235/1475; 83c 2053/465/1588; 87a 1868/300/1567; 89r(DIS) 1957/486/1471.
- The silent gap: 'Low-detection dump applied' (~46-111 s) -> 'V1284 head patched ... Launching 2 shards' with no output. DIS is only passed as a CLI arg to the GPU subprocess (--ilp-disappearance-weight 2.25), so the pre-GPU phase CANNOT depend on DIS. CONFIRMED.
- Per-clip ILP: 89p 25.0/16.5/4.4/76.8 vs 89q 17.9/24.0/4.1/76.7 (same totals ~123 s); 88a 23.2/26.8/5.7/87.0 vs 88b 21.7/24.1/5.7/83.9 (+4%); 89s 27.2/17.8/4.9/79.6 vs 85a 21.3/23.9/7.2/76.1. DIS has no ILP cost. The claim is CONFIRMED.
- '+15-20%' lives in round26/report.json new_facts 6 and v_hyp_finals_r26f-4.json, not in CONTEXT (grep '15-20' in CONTEXT hits only l.405, unrelated).
- HOLE in the proposed amendment: the exp89l gate parent is exp89p (non-CI, compute 1058). Any CI compute (1471-1642) is 1.39-1.55x that, so 'compute <= 1.10 x parent' fails. The rule would not help the one dummy it targets unless 'parent' means the nearest same-CI-family dummy (exp89r 1471 / exp87a 1567 / exp83c 1588).
- tools/dummy_gates.py (151 lines) has no runtime logic; runtime is read by hand.
- Value: 0 LB. Saves one ~35-min re-run only if the exp89l whole-kernel lands in 2100-2500 (CI whole-kernel 1710-2285; 2 of 5 CI dummies > 2100, so ~30-40%).
- 2026-09-28T16:05:52Z final JSON written: refuted=false with a parent-definition fix.
