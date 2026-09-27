# review_si_builder_1 (lens: SAFETY AND RULE FIT) - 27 Sep 2026

- 11:50 UTC start. Read the CONTEXT E10 v3 entry (11:08Z), P4b, round11 R11-A3 SI_CONDITIONS, the --base succ diff in
  tools/build_probe_kernel.py, tests/test_si_builder.py, and build_si_builder.notes.md.
- RULE FIT OK: (A) verbatim is deliberately NOT a builder path (succ refuses without divinsert: "a verbatim copy is a
  port, pushed from the pulled folder"), so the builder cannot produce a non-byte-identical "verbatim". (B) SI only when
  the audit passes on the pristine cells, and every patch keeps its _rep1 count==1 asserts (AssertionError -> refusal,
  no output folder). Finals: x138 / exp39 code paths are unchanged (tag, serial, metadata branches keyed on succ).
  Metadata follows P4b(a); no --push or --dataset. probe.json["lab"] ("never submit") is not overwritten by the succ rule.
- GAPS FOUND AND FIXED (tools/build_probe_kernel.py):
  1. Knob audit caught only os.environ["KEY"] = / update / putenv. A Python re-binding (`REPAIR_DEADLINE_S = 20000`) or a
     loop write through a variable key (`for k in ["BIOHUB_REPAIR_DEADLINE_S"]: os.environ[k] = ...`) passed silently.
     Now the name must be bound exactly once (the reader in cell 5), and the quoted env key must not appear in cells >= 1
     except the reader and a cell-1 guard entry '"KEY": <num>,' (which the builder rewrites).
  2. safetail's insertion deadline gate reads KERNEL_START_TS, which the audit only required to be present. A successor
     that resets the clock later would let the insertion run past the 8 h gate. It now gets the same bound-once /
     never-rewritten check under safetail (new 'once' anchor for its binding in the post cell).
  3. A non-lab SI could be built with divinsert only, which has no deadline gate and no fail-soft (a crash in the
     insertion kills the submission). R11-A3 (b) fixes the recipe as K1 with safetail. A submission succ build now needs
     --patch safetail; divinsert-only remains available with --lab (the D1 dummy).
  4. A non-lab succ build with DIVINS_ENABLE off gave "successor + dead code" labelled SI. Now refused unless --lab.
  5. --out-dir could point a succ build at an existing final's folder (mkdir exist_ok + overwrite). Now refused when the
     target folder already holds a kernel-metadata.json with a different id. Rebuilding the same kernel still works.
  Docstring updated. tests/test_si_builder.py +3 tests (rebinding / indirect write / clock reset; safetail and insertion-on
  required, lab D1 allowed; no overwrite of another kernel's folder, using a fake final under the test tmp folder).
- CONCURRENCY: review_si_builder_0 edited succ_anchor_audit at the same time (its `dyn` computed-key check is now in the
  same loop, after my checks). One test run hit its half-written state (NameError) and one subset run hit 2 transient
  failures from another agent's pytest sharing experiments/_pytest_si_builder (the module fixture rmtree's it). Both
  reruns were green.
- VERIFY 12:09 UTC: python -m pytest -q tests -> 469 passed, 1 skipped (coordinject weights env, not ours); later
  tests/test_si_builder.py 27 passed; test_secswap + test_si_builder 59 passed. The finals and ladder rebuilds are
  byte-checked in those tests (nb + kernel-metadata.json == committed): exp58 1f1ddb6d, exp58t a77bcd6b, exp58n 55038fd6,
  exp70a/b/d/e (test_secswap), exp70g/j/k (test_si_builder); all green.
- OPEN (not fixed, for the main session):
  a. Token: SI slugs use exp73, but experiments/exp73a..v are K2 variants. R11-A3 (c) had proposed exp67 (unused). A
     ledger rule exp73[a-z]* -> safetail would match both (the same family, so harmless), but submit messages are
     ambiguous (exp73a_si_x vs exp73a_k2_dc015). Pick SUCC_TOKEN before any trigger.
  b. There is no runtime_ledger rule for the SI token yet.
  c. The builder does not check P4b(b) source listability, P4b(c) latest-version score, the validator (INFO only), or
     R11-A3 (e)/(f) (mechanism scope, D0 runtime <= 7.5 h). These belong to the E10 gate and procedure, which must run before any SI submit.
  d. Tests write into experiments/_pytest_si_builder and delete it; parallel pytest runs collide there.
  e. No SI dummy has run on Kaggle yet (D0 / D2 / DFF + dummy_gates).
- Nothing was submitted, pushed or committed. I created no scratch folders; experiments/_scratch_e10v3 belongs to
  other agents and was left alone.
