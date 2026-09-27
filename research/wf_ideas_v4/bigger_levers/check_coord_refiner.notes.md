# check_coord_refiner - skeptic check of exp75_k2_coordinject (K2 + yuki0731 coord-inject, alpha 0.5)

- 2026-09-27 12:36 UTC, start. Read tools/coordinject_patch.py, prep notes, exp75 metadata/probe.json.
- 2026-09-27 12:40 UTC, REBUILD: build command -> experiments/_scratch_chk75/a notebook sha256 ab621c13... (== exp75, metadata identical);
  K2 rebuilt -> 1f1ddb6d... (== exp58 final, byte-identical). Cell diff exp75 vs exp58: cell 0 header name + 2 env lines
  (COORDINJECT_ENABLE=1, ALPHA=0.5); one inserted code cell (index 8) after the post cell (7, write_test_submission) and
  before the retention guard (9). Nothing else changed. dataset_sources = K2's + yuki0731/biohub-coord-inject.
- Globals the new cell uses exist before it: KERNEL_START_TS (cell 7, from env set in cell 0), test_stems (cell 4),
  TEST_DIR (cell 2), SUBMISSION_PATH (cell 2). Runtime module = dataset's (sha af3d8537 matches the local copy).
- LAB PATH MISMATCH: the prep lab (scratchpad ci_lab2.py) blended FLOAT V1284 coords with the target and rounded once;
  the kernel blends the CSV's INTEGER coords and rounds again. Re-ran with the kernel's own coordinject_positions +
  coordinject_cell on rounded exp60 final nodes (scratchpad chk75_lab.py, cached refined npz, official metric):
    a0.5 3um (the build): -0.0029 / +0.0125 / 0 / +0.0029  pooled +0.0022 (was +0.0032) -- edge TP -1/+2/0/+2
    a1.0 3um           : -0.0608 / 0 / 0 / -0.0009       pooled -0.0050
    a0.3 3um           : 0 / 0 / 0 / -0.0029             pooled -0.0013 (was +0.0011: SIGN FLIP -> noise)
    a0.5 2um           : 0 / +0.0125 / 0 / +0.0079       pooled +0.0045
  Reading: alpha 0.5 still the best 3-um arm and positive on the real code path, but it is a handful of edges on 2 clips;
  the a0.3 sign flip under a rounding-only change shows the noise floor is ~ the effect size.
- 2026-09-27 12:40 UTC, TESTS: tests/test_coordinject.py 14 passed 1 skipped; full suite with COORDINJECT_WEIGHTS_DIR set (CPU
  e2e included) 484 passed, 0 failed (the count has grown since the prep run). exp58 sha 1f1ddb6d unchanged; the finals are untouched.
- RUNTIME: every train/test clip is 100 x 64 x 256 x 256 (pooled 64^3). The lab CPU per clip was 3430-3900 s with 4 clips
  running in parallel, consistent with the 6.5 + 0.75 s/frame figure. T4 by FLOP count: roughly 0.3-1 s/frame, so 40-100 s/video, and
  ~50-65 videos per worker comes to 35-110 min. K2 hidden ~7.5 h, so the total is ~8.1-9.3 h. The K2 tail may run to 9.5 h (REPAIR_DEADLINE_S),
  which leaves partial coverage but is still safe. VALIDATOR_ENABLE=0 in K2, so only the guard and manifest cells run after coordinject, and those are cheap.
  Worst case: workers are killed at 10.75 h, then the CSV rewrite (~3M node rows, a few minutes) runs, all under the 12 h limit. skimage 0.25 is in the docker (K2 log);
  zarr is installed by cell 3 from offline dirs, and if the worker cannot see it, load_volume falls back to blosc2 (the docker has blosc2).
  Dataset attach = latest version at push. If yuki0731 updates it, the sha check fails and the step does nothing (fail-soft, the slot is wasted).
- DUMMY GATE ARITHMETIC: the dummy has 4 videos on 2 workers (2 each). Hidden is 100-130 videos, so up to 65 per worker. For full coverage
  inside the 10.5 h guard with K2 at ~7.5 h, per-video worker time must be <= ~165 s. PASS if the mean is <= 130 s; 130-165 s is acceptable but risks
  partial coverage; > 165 s means partial coverage is likely (still no timeout).
- GPU at 12:45Z: exp71 RUNNING, exp70n RUNNING (pushed 12:24Z, a K2 dummy of ~30 min, so free around 12:55Z). NOT pushed.
- DISPLAY: LB blocks 26 Sep: 0.955 = ranks ~144-198 (silver edge ~197), 0.954 = 199-295. A +0.001 display step is worth
  ~60-100 ranks. Kernel-path lab central +0.002 (in-sample, 4 clips, per-clip sd ~0.007); shrink for out-of-sample and
  noise: central ~+0.001, range -0.003..+0.004. Rough P(display >= 0.955) ~0.35, P(<= 0.953) ~0.2. That is a real chance
  of moving the display, and the downside is limited to the probe slot (it is not a finals candidate).
- VERDICT: GO as a risk probe once the dummy passes. The build is verified and reproducible. The only substantive correction is that
  the expected gain is +0.002, not +0.003 (the kernel's integer path). Optional variant: MAX_UM 2.0 (kernel path +0.0045; c502 0 instead of -0.003),
  but in the float path it did not help c502 (-0.018), so it is noise and not required.
