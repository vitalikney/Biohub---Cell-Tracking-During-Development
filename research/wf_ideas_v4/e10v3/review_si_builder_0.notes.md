# review_si_builder_0 notes (correctness lens on the --base succ SI builder)

- 2026-09-27 11:40 UTC start. Read the build notes and the diff of tools/build_probe_kernel.py (it also carries a parallel
  coordinject hook), and tests/test_si_builder.py.
- 11:45 UTC full pytest (my first run): 453 passed, 1 skipped, 1 FAILED, tests/test_trainlab.py::test_end_to_end_replay_parity
  (StopIteration: experiments/zz_trainlab_test/kernel_a had no .ipynb). This looks like a race with the concurrent reviewer's
  pytest on the shared zz_trainlab_test folder, not the SI code (re-checked below).
- 11:46 UTC independent byte-identity rebuild of the ten builds into experiments/_scratch_e10v3/rev0 (recipes from
  tests/test_secswap.py BUILDS + test_si_builder ladder): nb AND kernel-metadata.json == committed for exp58 1f1ddb6d,
  exp58t a77bcd6b, exp58n 55038fd6, exp70a 132438a9, exp70d e0b8fc0c, exp70e c0f3380c, exp70b b8e7ece1, exp70g 52c182a3,
  exp70j 61a8d3c1, exp70k adef8bcb.
- 11:47 UTC mutant probe of succ_anchor_audit (x138 cells, K2 patches, knob REPAIR_DEADLINE_S). On the DELIVERED code these
  all passed the audit (no FAIL): an aliased environ write (`_env = os.environ; _env["BIOHUB_REPAIR_DEADLINE_S"] = ...`),
  `from os import environ`, `os.environ.__setitem__(...)`, a Python re-binding `REPAIR_DEADLINE_S = 27000.0` after the
  reader or in another cell, and a drift check naming the key in another cell. By 11:48 a concurrent reviewer
  (review_si_builder_1) had already hardened the knob check: one Python binding, no other quoted mention of the key, and
  KERNEL_START_TS guarded under safetail. Re-run on that code: alias / from-import / __setitem__ / rebind / drift-check
  mutants are now refused. STILL PASSING: a computed key (`os.environ["BIOHUB_" + k] = v` fed by `{"REPAIR_DEADLINE_S": ...}`),
  an f-string key, a tuple re-binding (`REPAIR_DEADLINE_S, _x = ...`) and `globals()["REPAIR_DEADLINE_S"] = ...`.
- 11:48 UTC tried a fix: FAIL on any computed-key / aliased / bulk os.environ write after cell 0. REVERTED within a minute:
  x138 itself (so HF v3 and amanatar v6 too) has `os.environ["BIOHUB_" + key] = str(value)` in code cell 10, the validator's
  re-apply of the selected PP config, so the check refused every base. File back to the concurrent reviewer's version
  (grep: no _SUCC_ENV_DYNAMIC left; ast parses). Narrower safe fix, NOT applied because review_si_builder_1 was editing that
  function: also count the quoted BARE name (`["'](BIOHUB_)?NAME["']`) in the "other mention" check. Scan: x138, HF v3 and
  amanatar v6 have no bare quoted REPAIR_DEADLINE_S / KERNEL_START_TS in cells >= 1. Only amanatar v10 has one
  ('KERNEL_START_TS' in cell 10), and v10 is refused anyway. The v10 test asserts exactly 1 FAIL, so that test would need
  updating.
- 11:52 UTC no-push check: the builder's only push path is `if a.push:` at the end of main(), and --base succ refuses --push
  before anything is built. Risk found in the TEST: test_builder_argument_refusals passes --push to a real builder
  subprocess, so if the refusal ever regressed, the test would really run `python -m kaggle kernels push` with the user's
  credentials. Kaggle 2.2.4 reads ~/.kaggle/access_token, kaggle.json, KAGGLE_API_TOKEN and the OAuth creds file.
  FIX APPLIED in tests/test_si_builder.py: _build() now runs with _nokaggle_env(), which puts a shadow `kaggle` package
  (__main__ = SystemExit) first on PYTHONPATH (under the module's _pytest_si_builder tmp dir, removed by the fixture) and
  drops KAGGLE_* env. New test test_builder_subprocesses_cannot_reach_kaggle proves `python -m kaggle kernels push` exits
  blocked under that env. tests/test_si_builder.py: 27 passed (includes the concurrent reviewer's 3 new tests).
- 11:54 UTC real-successor end-to-end K2 SI builds (scratch): HF v3 (raunakdey07, sha 9ab32885) and amanatar v6 (e6c3f729)
  build with 37 checks OK. Only code cells 0/4/5 change, plus the same 2 new cells (ids 8deded8f / fe84a462, as in x138
  K2). Notebook metadata and nbformat are unchanged, and serialisation is compact (a round trip reproduces the pull). The
  kernel-metadata diff is exactly id_no dropped, id, title, code_file, is_private true and + vitaliineibauer/biohub-ft-weights;
  docker, machine and GPU are kept. amanatar v6 INFO: DET_THRESHOLD 0.960, so prefer K1, as delivered.
- Other checks, no issue: the audit runs on the pristine cells before the cell-0 block, and every refusal exits before
  out_dir.mkdir. Name / owner / slug-length / dataset / train-stems / knob whitelist guards work. The cell-1 drift-guard
  rewrite (`"BIOHUB_KEY": value,`) keeps a successor's cell-1 guard consistent with our --set. x138 / exp39 paths are
  unchanged (the ten rebuilds match).
- 12:03 UTC full pytest on the current files (build_probe_kernel.py sha d5ceea0b..., test_si_builder.py 746dfc4b...):
  479 passed, 1 skipped (test_trainlab passes: the 11:45 failure was the shared-folder race).
- 12:05 UTC ten-build byte-identity re-run on the CURRENT builder (after the concurrent reviewer's edits): all ten nb +
  kernel-metadata.json == committed (same shas as above). My scratch (experiments/_scratch_e10v3/rev0) is removed. The other
  folders under _scratch_e10v3/ belong to another agent and were left alone. Nothing was submitted, pushed or committed.
