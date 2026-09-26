# reach0955 plan agent notes (append-only)

- 2026-09-26 21:00:48Z (date -u): plan.json absent -> writing a new plan.
- Sources read: CONTEXT l.2380-2436 (20:30 directive, 20:33 R7 lift + "one for public, one for private", 20:34 "делай/autonomous",
  20:48 E10 dry run, 20:49 ladder + L9 {V*, #38}, 20:51 discussion intel); r_/v_ intel, retrain, ladder (task text);
  research/wf_ideas_v4/round12/report.json (written 21:01:17Z: R12-A3 keeps L9 {V*,#38}; ladder last submit 29 Sep 02:00Z per R8;
  retraining clause of R9 still needs an explicit yes; R12-A5 API budget; R12-A7 morning message 07:30Z).
- CONTEXT l.1671-1673 (PRE-REG v3): R8 = new mechanisms by 27 Sep 12:00Z; F1-final consolidation by 28 Sep 12:00Z; after
  29 Sep 02:00Z only an emergency repeat (hard edge 10:00Z). R9 bans retraining detector/edges/head, public knob ladders, axis-flip.
- Compute: max 2 concurrent GPU sessions (CONTEXT l.12); weekly 30 GPU-h, reset 26 Sep 00:00Z, next 3 Oct (after the deadline).
- 21:02Z kernels status: biohub-exp70a-k2-lp30 RUNNING, biohub-exp70e-k2-lp30-dc030 RUNNING, exp70d-k2-dc030 and exp70b-k2-fm45
  404 (not pushed yet; the 2-GPU cap). Builds dated 20:48Z (local 23:48).
- poll.log last header 20:58:27Z OK (no new subs since #37/#38); 20:36:50Z was a 429.
- K2 dummy reference: _dl/biohub-exp58-x138-safe-lowref/submission.csv sha256 b6de85c1f3c66e3b..., validate_csv ok,
  nodes 121,252 (44b6_0113de3b 25,729; 44b6_0b24845f 19,545; 6bba_05b6850b 6,220; 6bba_05db0fb1 69,758), edges 117,077,
  forks 75 (39/6/9/21). Node gate for exp72: total in [118,827, 122,465] = [-2%, +1%].
- x138/K2 cell 3 (exp58 notebook): l.573-576 env BIOHUB_SECONDARY_ARTIFACT_MANIFEST; l.577 hard-coded
  _secondary_expected_sha256 = "9bac2fa0..."; finder accepts only model.weight_sha256 == expected (l.609-611); l.646 raises on
  mismatch; l.654/656 print 'Secondary artifact:' / 'Secondary SHA256:'; l.659-663 hard-set SECONDARY_* knobs. '9bac2fa0' occurs
  only at l.577 in all cells -> secswap = one-line anchor replace.
- y3uanm v1 (experiments/ext_y3uanm-secondary-ft/notebook0afc5663f6.ipynb): cell 2 setup (no-index wheels from support pack),
  cell 4 asserts parent sha 9bac2fa0, cell 5 SecondaryFineTune (teacher copy, trainable decoder_blocks[-1]+unet.head+detect_head,
  train() forced eval), cell 6 trainer.train(n_epochs=1, lr=1e-5, batch 1, num_workers=0, max_iters=None, validate=False,
  data_parallel=False), cell 7 artifact with TOP-LEVEL "sha256" (x138 needs model.weight_sha256) + repo + wheels (large).
  Metadata: internet ON, docker gcr.io/kaggle-images/python@sha256:dafd4ce5..., T4. Never actually run publicly (quick saves).
