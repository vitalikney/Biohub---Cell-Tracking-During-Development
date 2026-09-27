# review_gate_verbatim_0 (correctness lens) of build_gate_verbatim (tools/e10_port_gate.py --mode verbatim / si)

- 2026-09-27T11:40Z start. Read the delivered diff of tools/e10_port_gate.py (+302/-14), tests/test_e10_port_gate_modes.py
  (41 tests), build_gate_verbatim.notes.md/.json, CONTEXT E10 v3 (11:08 UTC) + P4/P4b rules. Backup of the delivered gate in
  the session scratchpad (e10_port_gate.delivered.py).
- 11:41Z full `python -m pytest -q tests` (before any edit of mine): 454 passed, 1 skipped (other agents add tests in parallel).
- 11:43Z finals + ladder rebuilt with the CURRENT builder into experiments/_scratch_e10v3/<name> (commands reconstructed from
  each probe.json 'change' + PATCHES): exp58 1f1ddb6d, exp58t a77bcd6b, exp58n 55038fd6, exp70a 132438a9, exp70b b8e7ece1,
  exp70d e0b8fc0c, exp70e c0f3380c, exp70g 52c182a3, exp70j 61a8d3c1, exp70k adef8bcb: all 10 == expected == committed.
- No submit / push path: the gate has no subprocess / network / kaggle call (only help text); the test file's only
  subprocess is the local builder (--out-dir under experiments/_scratch_e10v3, removed in finally).
- 11:45Z FINDING 1 (false PASS, SI): hunk matching drops positions. Synthetic probes: the same insertion moved to another
  line of the same cell -> match; moved into ANOTHER CELL -> match; a replace applied to the other of two identical lines
  -> match. Order swap -> correctly no match. FIX (tools/e10_port_gate.py): diff_hunks_slid() now also returns, per hunk,
  the set of code-cell ordinals of every slid form (code_cell_prefix(); markdown cells not counted, HF v3 interleaves 8);
  check_si_diff() adds, after a content PASS, a PASS/FAIL line 'every SI hunk sits in the same code cell as in the reference
  patch diff' (FAIL names hunk, SI cell set vs reference cell set); INFO 'position check skipped' when the pulled notebook's
  code-cell count differs from the base's. Within-cell position is still NOT checked (context lines differ on successors
  that strip comments, e.g. HF v3) -> residual limitation, mitigated by the builder's succ_anchor_audit (exactly-once anchors).
- 11:49Z NOTE: a parallel agent is editing tools/e10_port_gate.py at the same time (added SI_ID_RX / SI_REF_KNOWN / FAIL on a
  non-x138 reference base). Both sets of edits are present in the file; from then on only exact-string edits.
  Gated the other agent's scratch build experiments/_scratch_e10v3/si_hfv3_k1 (HF v3 + K1 recipe) with the position check:
  PASS, 'every SI hunk sits in the same code cell ... (12 code cells)', 1 slid insertion. The real-builder test
  test_si_real_builder_on_hfv3 now SELF-SKIPS: the current (parallel-edited) builder refuses HF v3 ('FAIL [knob]
  KERNEL_START_TS: computed-key / aliased / bulk os.environ writes after cell 0 in code cells {10: 1}'), so the build's
  claim 'HF v3 SI PASS with the real builder' is not reproducible with today's builder (builder owner's call).
- Tests added (tests/test_e10_port_gate_modes.py, appended): swapped hunk order does not match; slid forms record their
  code cells; the exp58t cell-0 override block moved to the end of cell 1 -> content PASS but position FAIL; position PASS
  on exp58t-as-SI of x138.
- 11:52Z default mode re-checked with the current file (both agents' edits): output byte-identical to HEAD's gate on the 4
  inputs (HF v3 full dry run rc0 PASS; amanatar v10 rc1; x138+exp56 port rc1; x138+exp56 dummy/author rc0).
  Verbatim on the HF v3 dry run: rc 0, 0 [FAIL]/[SKIP] lines, 1 'author version: 3' line (R12-A4 protocol OK).
- 11:54Z FINDING 2 (false PASS, verbatim + si): a pulled folder whose notebook is missing produced 'pulled notebook: ...'
  as FAIL in default mode but source_as_info() downgraded it to INFO in verbatim / si, so a static trigger run (no --port)
  printed RESULT PASS with no notebook at all. FIX: run() appends that FAIL directly; only check_source's findings are
  downgraded. Regression test test_missing_pulled_notebook_fails_in_copy_modes[verbatim|si].
- 11:58-12:15Z mutation run (mutants loaded through a pytest plugin from the scratchpad; the shared gate file never mutated),
  14 mutants on tests/test_e10_port_gate_modes.py: 12 killed first pass; SURVIVED: 'slide_unbounded' (neighbour bounds of
  diff_hunks_slid removed) and 'order_insensitive' (check_si_diff matching hunks in any order; the builder's swapped-order
  test called hunks_match directly, not the gate). Added test_slide_is_bounded_by_the_neighbouring_hunk (brute-force witness
  x y z x y z -> x z: unbounded slide adds the non-equivalent form (y, z, x)) and test_si_diff_same_hunks_in_swapped_order_fails
  (synthetic 4-notebook check_si_diff). Re-run: both KILLED, and reverting FINDING 2's fix is KILLED by its regression test.
- Full `python -m pytest -q tests` after my edits: 483 passed, 1 skipped (the self-skipping real-builder HF v3 test; other
  agents keep adding tests). pyflakes clean on both files. Finals + ladder rebuilt again: all 10 byte-identical (same hashes).
  My scratch rebuild folders deleted; experiments/_scratch_e10v3 removed if empty (other agents' rev0 / si_hfv3_k1 were
  already gone). Nothing committed, pushed or submitted.
- Not changed (design points for the orchestrator): (a) verbatim keeps P4 (4) kernel_sources == [] as FAIL - E10 v3's safety
  list names byte-identity, public/listable sources, runtime evidence, dummy; a public top notebook fed by another notebook's
  output cannot get an (A) copy through this gate (defensible: a kernel source floats to its latest version); (b) runtime
  evidence (<= 12 h) and 'scored version == pulled latest' are not checked by the gate; (c) si mode does not require the
  recipe's own log lines (e.g. 'Low-detection dump applied' / LOWREFINE for a K2-recipe SI), only DIVINS ENABLED and the
  FAILED/SKIPPED lines; (d) within-cell hunk position is unchecked (cell-level only).
