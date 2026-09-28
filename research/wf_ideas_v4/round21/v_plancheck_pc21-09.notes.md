# PC21-09 notes (2026-09-27T23:27:30Z)
- 23:28Z: `kaggle kernels status` (read-only): exp78b, exp79a, exp78a, exp79d, exp81 all COMPLETE.
- KaggleApi.kernels_list(mine) last_run_time: exp78a 2026-09-27 18:56:53Z, exp78b 19:45:12Z, exp79d 20:10:16Z, exp79a 20:32:27Z,
  exp81 21:25:58Z, exp80a 21:26:11Z. current_version_number not exposed (0); kernels_pull -> 403. Local build folders untouched since
  build (exp78a/78b 18:56Z, exp79a 19:05Z local mtime UTC+3) and CONTEXT logs one push per kernel -> v1 is the dummy-gated version
  with high probability; not provable from the API here.
- CONTEXT l.2525 (26 Sep, R12 (d)) already requires 'the kernel version is COMPLETE' + dummy sha compare before every submit -> (a) is
  mostly a restatement; the new part is logging the push time/version.
- tools/runtime_ledger.py l.86 EXP_TOKEN = first exp\d+[a-z]* token; l.158 family_of: ref/token overrides (--family) can fix a
  mis-tokened ref after the fact. Ledger rows 43-46 already use 'probe N: expXX = ...' -> (c) is the existing convention.
  Real risk only for exp79a: a description like 'exp70g + CI' would map to safetail (not safetail_ci) and mis-read the CI gate.
- N2 pre-reg (CONTEXT l.3289, 21:06Z): band '~0.99-1.01'; exp71 in-sample 0.995-1.007 (l.3002) was known when it was written.
  n2a 0.998/1.010 (l.3302) is inside the pre-registered band (inclusive). Switching to <=1.007 now would be a post-hoc gate change
  -> strike that clause. N2 decision is W2a (~08:45Z), not 00:03Z. exp81 dummy is COMPLETE on Kaggle but its node/runtime gate
  is not logged yet.
- 2026-09-27T23:29:41Z: final JSON written (refuted=false, amended: strike <=1.007 clause).
