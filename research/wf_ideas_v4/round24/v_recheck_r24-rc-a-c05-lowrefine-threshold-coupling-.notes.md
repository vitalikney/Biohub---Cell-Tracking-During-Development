# notes R24-RC-A skeptic (2026-09-28T07:05:32Z)
- 07:2xZ verified dummy logs: exp70g LOWREFINE refined 26532/33336/7370/76396 (>=0.965) failed 0; exp85c 26694/36487/7497/77342 (>=0.94) failed 0 (+4386); exp85a identical to 85c. readmitted 96/677/84/508=1365 -> 167/1148/105/804=2224 (85a 2223). Numbers in finding CONFIRMED.
- builder l.1652 _LOWREFINE_MIN_SCORE reads BIOHUB_READMIT_MIN_SCORE (coupling real). Refine exception -> grid coords kept (fail-soft).
- scan_recheck.json (round24) item A carries the full evidence; cmp85c.py lives in another session scratchpad.
- independent recompute (scipy KDTree, per dataset/t, new = >0.5 vox from any exp70g node): 2,913 new nodes, 7.96% on 4-px xy grid vs 7.44% all exp70g nodes -> band readmits are refined (unrefined would be ~100% on grid). Confirms the finding's 8.3%/7.3% (its 1 um cut gives 1,857).
- caveats: 0.92 (exp86c) not measured (no _dl/exp86c dummy yet); 'better localisation' unmeasured (no GT for 0.94-0.965 band). Coordinate moves <= ~1.15 um xy vs 7 um match radius -> second-order for matching; can nudge relink/safe-division geometry (e.g. the +1 insertion on 0b24845f), inseparable from volume but tiny.
- verdict: NOT refuted. Action = note amendment + gate logging only; zero build/slot cost; no rule R1-R10 touched.
