# schedule-lens notes: harvest-x138-successors (2026-09-25T11:13:38Z)
- Started. No prior schedule JSON. Reading sibling v_github-intel_successor-port_schedule.json, browser_intel.md, kaggle-intel_runtime-guard-audit_schedule.json.
- Sibling verdicts v_github-intel_successor-port_{value,schedule}.json: near-identical idea, both refuted (P scored ~0.2-0.25, E[pub] ~+0.0005).
- NEW evidence: browser_intel.md (local session, Kaggle CLI + Chrome, 25 Sep 11:00-11:15 UTC). The browser pass the idea asks for "tonight" has ALREADY been done: "no public notebook scores above 0.953". Only x138 and a verbatim re-upload (kunaldesale2408) are >= 0.950. amanatar/optimized-biohub-max-score (x138 + in-sample PP sweep) best 0.953, current version ERRORED, last good run 0.910. raunakdey07 V5 = x138 with comments stripped.
- LB 25 Sep 11:00: 401 teams >= 0.953, 240 at exactly 0.953, 39 >= 0.960 -> ~122 teams at 0.954-0.959, all private. Teddy Tennant now rank 45 = 0.959 (last sub 24 Sep 23:55); his public kernels unchanged.
- Checked here: tools/build_probe_kernel.py --base choices = sorted(BASES) = {exp39, x138} (l.79-82, 1373). A successor needs a new BASES entry for the rider path; a verbatim fork needs no builder.
- Checked here: curl https://www.kaggle.com/api/v1/kernels/list -> 000 (proxy blocks). A pasted Kaggle key would not help this container; the laptop session already has the Kaggle CLI.
- x138 visible-test runtime 20m28s on T4 x2 (browser_intel 2a) -> dummy run ~0.4-0.7 GPU-h after the 26 Sep 00:00 reset.
- Verdict: refuted on schedule (P scored ~0.15-0.2 unconditional; ~0.8 conditional on a qualifying release). Keep as zero-cost triggered watch on the laptop CLI.
- 2026-09-25T11:14:35Z final JSON written.
