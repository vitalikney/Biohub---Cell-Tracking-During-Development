# prep_coord_refiner - yuki0731/biohub-coord-inject as a K2 post-step (exp75)

- 2026-09-27 11:20 UTC, start. Read experiments/ext_yuki0731-biohub-coord-inject/ (NOTES, manifest, coord_inject_runtime.py
  874 lines, identical to the dataset copy, sha256 af3d8537...). Dataset downloaded to scratchpad (90.7 MB, 8 .pt).
  GPU sessions: exp71 RUNNING, exp70n QUEUED -> no free session now: build only, no push.
- Prior on public: V1284 head (placement) = +0.002 on our base (probe 31), +0.007 on x138's; float output = 0 (probes 32/33).
  Placement is a real but small lever; coord-inject is an independent 4-seed detector + z/xy refiners that snaps each node
  to its nearest refined detection within 3 um (replaces V1284's placement where a detection exists).
- 11:25 UTC, CPU timing (16 threads, laptop): 1 detector forward on the pooled 64x64x64 volume 0.39 s -> 16 forwards/frame
  (4 seeds x 4 flip views) = 6.5 s/frame; refiners 0.75 s/frame. T4 estimate ~0.5 s + ~0.3 s/frame -> ~1.2-2 min per
  100-frame video per GPU, 2 workers -> ~60-100 min for ~100 hidden clips on top of K2's 7.4-7.6 h (~9.1 h). Checkpoint
  metadata: detectors trained on 'det_data_mix' (train_videos 251, i.e. competition + other data), refiners on 171 of the
  199 train stems -> the public test copies and any train lab are in-sample for coord-inject. Their own trends: detector
  median 3D error 1.71 um (z 1.60, xy 0.77); z refiner med 1.59 um (z 1.13); xy-distilled med 1.65 um (xy 0.58). V1284 public
  head OOF median 1.525 um on our capture (CONTEXT 24 Sep 23:00; raw x138 peaks ~1.72). => coord-inject is NOT more
  accurate than V1284 on paper (different eval sets); it is an independent second localiser.
- 11:35 UTC, 2-frame debug on 6bba_bb9f20c3 (exp60 trainlab final graph, float V1284 coords): every node found a detection
  within 3 um, nn distance median 0.45 um, mean offset (z,y,x) = (-0.14, +0.08, +0.26) voxels -> conventions agree
  (raw = pooled*4 + 1.5 in coord-inject); the two localisers differ by ~0.45 um, well inside the 7 um match radius.
- 11:26 UTC, local CPU lab launched on 4 full train videos (6bba_bb9f20c3, 6bba_784a78c9, 44b6_eb2880fc, 44b6_c50204e0):
  exp60 final graphs, official metric, arms inject(3 um, alpha 1), (3 um, alpha 0.5), (1.5 um, alpha 1) + GT distance.
- 11:40 UTC, PATCH WRITTEN: tools/coordinject_patch.py + 3 small hooks in tools/build_probe_kernel.py (PATCHES /
  META_PATCHES / BASES['x138'] registration after secswap, and one check() call in main()). Design: a NEW code cell right
  after x138's post-processing cell (after write_test_submission('base'), before the guard/validator/manifest cells), so
  the K2 tail and its deadlines are untouched: sha256-checked dataset module + 6 checkpoints; one worker subprocess per GPU
  (<= 2, stems interleaved) running the dataset's coord_inject_runtime.py VERBATIM (detector_cache_for_video +
  apply_axis_refiners; refiners fp32 by default, AMP knob) -> <stem>.npz; per-video deadline guard (no new video once
  now + 1.25 x slowest-so-far passes KERNEL_START_TS + COORDINJECT_DEADLINE_S, default 37800 = 10.5 h; kill at +900 s);
  then a 2-pass streaming rewrite of submission.csv (inject_one's rule on node rows of refined videos, integers like the
  x138 writer, clipped to the volume; all other bytes copied; line-count check; os.replace last). Fail-soft everywhere
  ('COORDINJECT FAILED' / per-video 'COORDINJECT_WORKER FAILED' keep the original rows). ENABLE=0 -> byte-identical CSV.
- 11:41 UTC, builds: K2 rebuilt from the builder reproduces exp58 byte-for-byte modulo its name (with DIVINS_DUMP=0);
  --patch coordinject ENABLE=0 = K2 + exactly one extra cell; exp75_k2_coordinject built (ENABLE=1; +dataset
  yuki0731/biohub-coord-inject in dataset_sources), notebook sha256 476dda99c036ddcd9bd4666c6536245bc60fc8944b75418b3035e77e70f00773.
  Build command:
    K="--set DIVINS_ENABLE=1 --set DIVINS_STEAL=1 --set DIVINS_CAP=4 --set DIVINS_FRAME_CAP=1 --set DIVINS_ALPHA=1 --set DIVINS_THRESH=0.4 --set DIVINS_DUMP=0"
    python tools/build_probe_kernel.py exp75_k2_coordinject --base x138 --patch divinsert --patch safetail --patch lowrefine --patch coordinject $K --set REPAIR_DEADLINE_S=34200 --set DIVINS_DEADLINE_S=28800 --set LOWREFINE_ENABLE=1 --set COORDINJECT_ENABLE=1 --note "..."
- 11:44 UTC, tests/test_coordinject.py 14 pass + CPU e2e pass (COORDINJECT_WEIGHTS_DIR set): the real worker on 2-frame
  copies of the 4 public test videos with K2's dummy submission.csv as input (2 copies present, 2 missing -> per-video
  FAILED, kept): only node rows of frames 0-1 of the 2 refined videos changed (ids/t/edges identical); 44b6_0113de3b
  replaced 388 (of ~514 nodes in 2 frames), shift median 0.83 um; 44b6_0b24845f shift median 1.23 um (shift measured from
  the CSV's INTEGER coords, so z rounding (<= 0.8 um) is part of it). CPU 60 s per 2-frame video.
- 11:47 UTC, full suite: python -m pytest -q tests -> 454 passed, 1 skipped (the CPU e2e needs COORDINJECT_WEIGHTS_DIR).
  exp58 (K2 final) notebook sha256 still 1f1ddb6d... (untouched).
- 12:32 UTC, LOCAL CPU LAB DONE (4 full train clips, exp60 final graphs = x138 + insertion with V1284 float coords; official
  metric; coord-inject IN-SAMPLE: refiners saw 171/199 train stems, detectors 'det_data_mix'). ~1 h CPU per clip.
  GT distance (rounded writer coords): median 1.68 -> 0.81-1.82 um, share <= 2 um +4..+13 pp (placement clearly better
  in-sample). Adjusted edge Jaccard, delta vs base per clip (c502 / eb28 / 784a / bb9f) and pooled by GT edges:
    alpha 1.0, 3 um (the verbatim rule) : -0.0651 / 0 / 0 / -0.0019   pooled -0.0057  (c502: edge FP +15)
    alpha 1.0 + unique detection        : -0.0408 / 0 / 0 / +0.0005   pooled -0.0029  (collisions are not the cause)
    alpha 0.7                           : -0.0312 / +0.0125 / 0 / +0.0015  pooled -0.0006
    alpha 0.5, 3 um                     : -0.0209 / +0.0125 / 0 / +0.0083  pooled +0.0032
    alpha 0.5, 2 um, unique             : -0.0181 / +0.0125 / 0 / +0.0088  pooled +0.0036
    alpha 0.3                           : -0.0029 / 0 / 0 / +0.0030   pooled +0.0011
    alpha 1.0, 1.5 um                   : -0.0255 / 0 / 0 / -0.0009   pooled -0.0051
  Divisions: no TP change on any arm. Moves are a handful of annotated edges per clip (one edge ~0.003 on 44b6 clips):
  NOISY, and in-sample for coord-inject. Reading: the verbatim alpha-1 snap HURTS (better node placement does not turn
  into better edges: the linker's edges were built on V1284 positions); a 50/50 blend of the two localisers is the only
  arm with a positive pooled delta (+0.003, 2 clips up, 1 down, 1 flat).
- 12:34 UTC, exp75 REBUILT with COORDINJECT_ALPHA=0.5 (alpha 1 rejected by the lab): experiments/exp75_k2_coordinject,
  notebook sha256 ab621c13654e0a530d8468fa242cce59cdbde643b7fb4547adb8264d29c80535; kernel-metadata = K2's + yuki0731/biohub-coord-inject.
  GPU sessions: exp71 RUNNING + exp70n RUNNING = 2 -> NOT pushed (no dummy yet). NEXT when a session frees: push exp75
  as the dummy (python -m kaggle kernels push -p experiments/exp75_k2_coordinject); dummy gates: 'COORDINJECT SUMMARY:
  videos=4/4', no 'COORDINJECT FAILED', per-video COORDINJECT_WORKER seconds (x ~25 for the hidden-set cost, must keep
  the projected total <= ~9.5 h), node/edge rows and ids identical to K2's dummy CSV (only z/y/x of node rows differ).
  VERDICT: feasible and built; expected public effect small (lab +0.003 in-sample, noisy, one clip -0.02); a risk rung,
  not a finals candidate without its own public score.
