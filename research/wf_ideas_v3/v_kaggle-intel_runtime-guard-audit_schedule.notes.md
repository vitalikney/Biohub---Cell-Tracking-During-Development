# notes runtime-guard-audit schedule skeptic — Fri Sep 25 11:10:03 UTC 2026
- 11:1x read BRIEF; x138 nb cell0 l.70-74 (START_TS, DEADLINE 27000, ILP_TIMEOUT 1200), cell5 l.14-45 (_deadline_degrade), l.2114-2116 (check once per dataset in sorted geffs). Numbers in idea match source.
- sibling value verdict (v_ensembles-and-private_x138-budget-aware-deadline_value.json): refuted as standalone probe; free gate: latency(#34/#35) < 7.5 h proves guard did not fire (latency >= runtime).
- FACTUAL ERROR in idea: builder --set ALREADY works with --base x138 (tools/build_probe_kernel.py l.1393-1399, 1522-1528). Verified in scratchpad copy: `build_probe_kernel.py exp58_x138_deadline36k --base x138 --set REPAIR_DEADLINE_S=36000` builds; only cell 0 differs (1 appended env line); datasets/docker/machine identical. Container work = ~10 min, not 1.5 h.
- Public/private come from ONE hidden run per submission -> a scored file's private is fixed; fix only helps files that include it; must be a rider on every future x138-family F1 candidate.
- 11:13 verdict written: not refuted on schedule (P scored ~0.9, earliest 26 Sep ~09-11 UTC); recommend rider + latency gate.
