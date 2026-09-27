# review_gate_verbatim_1 (lens: SAFETY AND RULE FIT)

## 2026-09-27 11:42Z
- Read the gate diff (HEAD -> working copy) and tests/test_e10_port_gate_modes.py. Baseline: gate tests 113 passed.
- Verbatim mode: source downgrade covers only validator / deadline / sweep-rewrite (check_source has no other
  FAIL besides "cannot read", which stays FAIL). Metadata + byte identity unchanged. Fits user rule (A).
- Gate is read-only (no file writes); default prefixes (exp63-succ / exp73-si) cannot hit a finals id (exp58*).
- Findings:
  1. SI id: gate required prefix biohub-exp73-si-, but the builder allows biohub-exp73[x]-si-<author>[-suffix]
     (build_probe_kernel.py SUCC_TOKEN regex). An exp73a_si_<author> build (needed when K1 and K2 SI of the same
     author coexist) would FAIL the gate falsely at a trigger. -> fix.
  2. SI hunk match drops positions: a pure insertion in the wrong code cell would match. -> fix (code-cell index).
  3. Reference base not pinned x138 was only INFO; the "our patch diff" is defined on x138 v1. -> make FAIL.
  4. No indication which recipe the --si-ref is. -> INFO line (K2 exp58 / K1 exp58t / other).

## 2026-09-27 11:47Z
- While applying, found tools/e10_port_gate.py modified concurrently by another agent (mtime 11:47:17Z): it added a
  code-cell position check for SI hunks (code_cell_prefix, 4th hunk element, PASS/FAIL line; INFO skip when the
  pulled and base code-cell counts differ). That covers finding 2, so I dropped my own version of it and apply only
  1, 3, 4 with small targeted edits.

## 2026-09-27 11:50Z  applied (small targeted edits, CRLF of the working copy kept; the other agent's code untouched)
- SI_ID_RX = vitaliineibauer/biohub-exp73[a-z0-9]*-si-<rest>; check_metadata(id_rx=) used in --mode si when no
  --id-prefix; suffix INFO accepts <author>-<suffix>. Header shows the regex. Docstring updated.
- check_si_diff: reference base sha256 != pinned x138 v1 -> FAIL (was INFO). New INFO "reference build = K2 final
  exp58 recipe / K1 exp58t recipe / not a pinned final recipe".
- tests/test_e10_port_gate_modes.py: +9 tests (7 id cases incl. ladder id exp73a-k2-dc015 and finals id FAIL, base
  pinned, recipe named). Modes file: 50 tests.
- Real check: rebuilt the K1 recipe on HF v3 with the builder's --base succ into experiments/_scratch_e10v3 and ran
  the CLI --mode si: PASS rc 0 (8 hunks, 1 slid, position check PASS, reference = K1 exp58t recipe). Scratch deleted.

## Open (reported, not changed)
- The concurrent position check reports INFO "hunk position check skipped" when the pulled and base code-cell counts
  differ; under the R12-A4 protocol (no [FAIL]/[SKIP]) that skip does not block. Suggest status SKIP (or FAIL) so a
  human looks; left to its owner to avoid clobbering an in-progress edit.
- SI hunk content matching still ignores surrounding context lines inside a cell (only code-cell index now);
  the builder's succ_anchor_audit (once-only anchors) is the primary placement guard.
- flatten_notebook ignores per-cell metadata / outputs; harmless for execution.
- The optional HF v3 real-builder test skips (not fails) when the builder refuses; a builder regression there would
  go unnoticed by the suite.
- --id-prefix override bypasses the SI regex and allows any prefix; operator-only escape hatch (finals ids use
  exp58*, never reachable by the defaults).
- exp73 token shared by the SI builder and the exp73a..v ladder folders (ids do not collide; ledger/messages do).
