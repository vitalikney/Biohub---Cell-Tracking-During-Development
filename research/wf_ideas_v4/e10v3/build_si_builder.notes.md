# build_si_builder notes (E10 v3 (B): successor + our insertion builder path)

- 2026-09-27 11:16 UTC start. Read CONTEXT E10 entries (P1-P8, P4b, P4c, gate built, R12-A4, E10 v3 11:08Z), round11 R11-A3 SI_CONDITIONS.
  Baseline: pytest 343 passed; tools/build_probe_kernel.py unmodified in git. Parallel agents touch e10_port_gate.py / e10_snapshot.py:
  the SI path will NOT import e10_port_gate (kept self-contained); only build_probe_kernel.py + new tests/test_si_builder.py change.
- 2026-09-27 11:37 UTC BUILT --base succ in tools/build_probe_kernel.py (new section before main(): SUCC_* constants, SUCC_ANCHORS table,
  succ_anchor_audit(), succ_base(), succ_meta(); main() wiring: --base-ipynb/--base-meta/--base-sha256, audit on the PRISTINE
  cells before cell 0 is touched, patch AssertionError -> refusal, tag line '--base succ <author>/<slug> sha256=<sha>',
  P4b(a) metadata, probe.json base_sha256 + succ provenance + every audit line). safetail/lowrefine/forkmid accept base succ.
  Bug found and fixed during verification: the first version audited AFTER the cell-0 override block was appended, so our own
  BIOHUB_DIVINS_* lines tripped the 'absent' checks on every base.
- Audit rows (K2 recipe = 33 checks + 2 INFO): each 'once' anchor exactly once in the expected cell and in no other code cell
  (duplicate / moved cell caught), linefit call directly followed by the FINAL print (no stage after the insertion), our knob /
  function names absent from the base, lowrefine literals before the V1284 block, REPAIR_DEADLINE_S read once in the post
  cell and never re-assigned after cell 0 (os.environ[...] = / update / putenv). INFO lines (never refuse): validator switch
  in cell 0; DET_THRESHOLD / READMIT_MIN_SCORE vs x138 0.965 for lowrefine.
- Refusals also: missing files, --base-sha256 mismatch, code_file != ipynb name, blank source, kernel_sources != [], no
  docker_image, base owned by us, name not exp73[x]_si_<author>[_suffix], slug > 50, --owner != vitaliineibauer, no
  divinsert, --dataset, --train-stems, --push, --set outside SUCC_KNOBS, REPAIR_DEADLINE_S without safetail.
- VERIFY (scratch experiments/_scratch_e10v3/, since removed): finals + ladder rebuilds byte-identical (nb AND
  kernel-metadata.json == committed): exp58 1f1ddb6d, exp58t a77bcd6b, exp58n 55038fd6, exp70a 132438a9, exp70b b8e7ece1,
  exp70d e0b8fc0c, exp70e c0f3380c, exp70g 52c182a3, exp70j 61a8d3c1, exp70k adef8bcb.
  x138 (ext_x138, sha 6b655e39) as succ: K2 -> exp58, K1 -> exp58t, K2+fm45 -> exp70b notebooks differ ONLY in the cell-0 tag
  line (swapping it back gives the committed bytes); metadata differs only in id/title/code_file.
  HF v3 (ext_ and dry_2026-09-26, same sha 9ab32885): K2, K1, #35-config, K2+fm45, K2+lp30 all APPLY; SI hunks == x138->K2 hunks
  (cells 0/4/5 + the same 2 new cells). amanatar v6 (27 Sep pull, e6c3f729, 13 code cells): all 5 recipes APPLY, hunks equal;
  INFO: DET_THRESHOLD 0.960 -> lowrefine premise shifts, prefer K1. amanatar old (371fc1f9) and v10 (96387e78): every
  safetail recipe REFUSED ([knob] REPAIR_DEADLINE_S re-assigned in code cell 10 = the pass-2 rewrite), K2+lp30 also refused
  (their own leaf pruning); divinsert-only (#35 config) builds, with INFO 'validator ON'.
- TESTS: tests/test_si_builder.py 23 tests (x138 == K2/K1/exp70b modulo tag, P4b metadata + sha records, audit mutants:
  duplicated anchor (same cell / other cell), moved cell (swap 4/5, post to the end), missing anchor (3 patches), stage after
  insertion, re-assigned knob, our code in base, lowrefine after V1284, too few cells; end-to-end refusals with no output
  folder; changed cell-2 knob still builds; argument/metadata refusals; real successors; exp70g/j/k byte-identical).
  python -m pytest -q tests: 440 passed (343 + 23 here + 74 from the parallel gate / watch agents).
- OPEN: token collision - other agents are creating experiments/exp73a..exp73v_k2_* (K2 variants) while this task's spec
  names SI kernels exp73-si-<author>; slugs cannot collide (-si-), but submit-message tokens and a future runtime_ledger
  rule would share 'exp73'. SUCC_TOKEN is one constant; runtime_ledger.py has NO exp73 rule yet (not edited here).
