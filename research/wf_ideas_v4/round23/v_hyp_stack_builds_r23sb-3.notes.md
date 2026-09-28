- 2026-09-28T04:14:22Z start verify r23sb-3 (dummy gate line for exp82a-c / exp83c-g)
- CONTEXT.md 3378-3384 (R22-A1, exp83a/b only), 3347-3365 (W2 v4 (2)(v), (4) lookup), 3366 (W4 AMEND 2 (1): PASSED dummy by 00:00Z), 3283-3290 (N2 pre-reg: nodes -2%/+1% of 121,252, <=1,920 s), 3322 (R21-A3 (a) exp81/exp80a numbers; (e) cap rungs = 0 errors only). grep: no gate line for exp82*/exp83c-g -> finding's premise TRUE.
- scan_hyp_stack_builds.json (04:15Z): all 9 built, "dummy NOT yet run" -> gate can still be written before any output exists.
- kernel-metadata: exp82a-c, exp83c/d/e/g attach biohub-secft-n2a-v1; exp83c-g attach coord-inject. OK.
- _dl sibling CSVs (local): nodes 121,252 for exp58/70g/78a/78b/70b/83a; 121,061 for ed8c616b SEC files exp72/79d/76d regardless of cap/fm.
  pandas: node rows (dataset,node_id,t,z,y,x) IDENTICAL exp72 vs exp79d (K2 vs cap6, SEC) and exp70g vs exp78b (cap6 vs cap12fc2). => cap/fc knobs never touch nodes on the dummy.
  => a much sharper (a) check: exp82x node rows == exp81 node rows exactly (121,085), not a -0.5/+0.2% band vs the non-SEC sibling.
- exp81 and exp80a dummy CSVs are NOT in _dl/ -> main session must `kaggle kernels output` them and match CSV sha12 8132ef2811d0 / a109ad024ace before gating exp82x/exp83c/exp83f/exp82c.
- Defect in proposal (b): lists R22-A1 (1)-(3),(5),(6) but OMITS (4) (the 7-column topology identity) while saying 'SEC-only dummy as the topology sibling' -> (4) must be included, restated generically.
- 2026-09-28T04:17:05Z verdict: NOT refuted, with amendments (include R22-A1 (4); exact node-row identity vs exp81; download exp81/exp80a CSVs). JSON written.
