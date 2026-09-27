# build_gate_verbatim (E10 v3 tooling: gate modes verbatim / si)

- 2026-09-27T11:14:10Z start. Read CONTEXT E10 entries (P4b, P4c, PORT GATE BUILT, R12-A4, E10 v3 11:08 UTC), round11 R11-A3
  SI_CONDITIONS, tools/e10_port_gate.py (977 lines), tests/test_e10_port_gate.py (72 tests), builder main() (tag line
  '# ---- <name>: probe overrides (tools/build_probe_kernel.py --base <b>) ----', new cells id = sha256(source)[:8],
  modified cells get outputs [] / execution_count None). Baseline: pytest 343 passed. Default gate on the HF v3 dry run
  (pulled _dl/ext2_biohub-harmonic-fusion-v3, port experiments/exp63dry_hfv3, dummy _dl/exp63dry_hfv3_out, author
  _dl/hfv3_author_out) -> RESULT PASS.
- Reference patch diff x138 (exp56) -> exp58t (K1 recipe), flattened cells with a cell marker line, difflib opcodes:
  8 hunks (+14 override block in cell 0, 1 replaced lowrefine literal line, +892 new cells (divnet helpers + DaughterNet),
  safetail degrade replace 2->4 and 1->2, +20 safetail gate, +1 gap2 flag, +42 divinsert call). Clean, anchor-local.
- Plan: only tools/e10_port_gate.py + a NEW test file tests/test_e10_port_gate_modes.py (existing 72 tests untouched);
  builder not touched (another workflow agent may be adding --base succ there).
- 2026-09-27T11:15Z implemented in tools/e10_port_gate.py: MODES default/verbatim/si; check_metadata(prefix, extra_sources)
  (defaults keep old behaviour); check_dummy_log(dummy, mode) + _dummy_log_copy_mode; source_as_info(); flatten_notebook,
  diff_hunks, check_si_diff, si_added_sources; run(..., mode, si_ref, si_ref_base, id_prefix); group_status returns INFO when
  a group has only INFO lines (never happens in default mode); CLI --mode/--si-ref/--si-ref-base/--id-prefix, extra
  header lines only in non-default modes.
- 11:17Z default-mode output byte-identical to HEAD's gate (old copy run with PYTHONPATH=tools) on 4 inputs: HF v3 full dry
  run, amanatar v10 pulled-only, x138 + exp56 port, x138 + exp56 dummy/author.
- 11:18Z verbatim on the HF v3 dry run: PASS, 0 FAIL / 0 SKIP lines, source group INFO. si on exp58t-as-SI of x138: PASS
  (8 hunks, +976/-4, dataset_sources + biohub-ft-weights from ref-vs-base metadata).
- 11:21Z found the parallel SI builder (build_probe_kernel.py --base succ, SUCC_TOKEN exp73, slug biohub-exp73-si-<author>)
  -> SI_ID_PREFIX changed exp67 -> exp73 to match. Built K1 recipe with --base succ on x138 and on HF v3 (scratch).
  x138 SI: PASS. HF v3 SI: FAILED at first: the 892-line new-cell insertion was shown by difflib rotated
  ([marker, source] vs [source, marker]) because HF v3 strips comments, so the surrounding context differs.
  FIX: diff_hunks_slid() records every form of a pure insertion / deletion reachable by sliding it through its own equal
  context (bounded by the neighbouring hunks); hunks_match = the form sets intersect. A rotation that is not a slide does
  not match (unit test). After the fix HF v3 SI: PASS with '1 insertion(s) matched as the same block slid'.
  Sanity: K2 (exp58, LOWREFINE_ENABLE=1) presented as SI against the K1 reference -> FAIL, detail lines name
  os.environ["BIOHUB_LOWREFINE_ENABLE"] = "1" vs "0".
- 11:25Z tests/test_e10_port_gate_modes.py: 41 tests (verbatim 16 incl. parametrised, si 25 incl. slide units and an
  optional real --base succ build on HF v3 that self-skips if the builder lacks the path; it writes under
  experiments/_scratch_e10v3/pytest_si_* and removes it). tests/test_e10_port_gate.py untouched (72 pass).
- 11:30Z full `python -m pytest -q tests`: 438 passed (343 baseline + 41 mine + other workflow agents' new tests).
  pyflakes clean on both files.
- 11:12-11:20Z finals/ladder rebuild check with the CURRENT (parallel-modified) builder into scratch, sha256 vs expected
  and vs committed notebooks: exp58 1f1ddb6d, exp58t a77bcd6b, exp58n 55038fd6, exp70a 132438a9, exp70b b8e7ece1,
  exp70d e0b8fc0c, exp70e c0f3380c, exp70g 52c182a3, exp70j 61a8d3c1, exp70k adef8bcb: all 10 byte-identical.
- Info: amanatar v6 (untracked pull v6_2026-09-27) pulled-only: default PASS, verbatim PASS (source INFO).
- 11:34Z scratch experiments/_scratch_e10v3 deleted. Nothing committed, pushed or submitted.
