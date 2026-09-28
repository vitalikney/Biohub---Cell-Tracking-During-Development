# v_hyp_risk_check R21RK-1 notes
- 2026-09-27T23:27:36Z start; read scan_hyp_risk_check.json/notes (source of finding)
- 23:30Z sha256[:12] of _dl CSVs re-hashed: 78b 34a5fa19227c, 79a 4280044276fc, 78a 4a375a3b5f17, 70g 62d832697d3b, 70q ca35552ffbf6 -> match the finding.
- 23:31Z kaggle kernels status: 78b/79a/78a COMPLETE. kaggle kernels pull -m (scratchpad r21rk1/): code cells IDENTICAL to experiments/<k>/*.ipynb (78b f101d6a9414a, 79a 715230734614, 78a 14a0b50ae594); remote metadata enable_internet=false, T4 machine, same dataset_sources (79a adds yuki0731/biohub-coord-inject). No re-push after the dummies.
- Log grep (Traceback|FAILED|DEADLINE:|FALLING BACK|SKIPPED|Error|error): 0 hits each. End times 1368.5 / 1711.5 / 1485.8 s. divinsert adds 78b 8/0/12/12, 79a 6/0/6/6, 78a 7/0/8/8.
- probe.json: 78b DIVINS_CAP 12 FRAME_CAP 2; 78a CAP 8 FRAME_CAP 1; 79a CAP 6 + COORDINJECT alpha 0.5 -> matches R20-A2 (2).
- Authority: CONTEXT l.3217 user 20:30Z autonomous night incl. 28 Sep W1 at 00:05Z (3 submits); R20-A2 (2) W1 order; 5/day team limit (CONTEXT l.343) -> W1 3 + W2a 1 + W2b 1 = 5.
- Skeptic caveats (not refuting): cap rungs have no lab support (CONTEXT 12:12Z: cap>4 = 0 TP/4 FP/81 unannotated), public reads on 1 embryo at 0.001 display; 79a main-process RAM at hidden scale untested (R21RK-5). GO is a readiness verdict, not a value claim.
- 2026-09-27T23:29:55Z final JSON written
