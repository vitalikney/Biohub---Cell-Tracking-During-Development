# v_intel notes (skeptic of r_intel: value + feasibility)

- 2026-09-26 20:55Z (date -u) start. v_intel.json did not exist. Read r_intel.json/.notes.md, v_ladder.json, v_retrain.json,
  discussions_2026-09-26.notes.md, CONTEXT.md l.2370-2436 (user 20:30/20:33/20:34Z, ladder+L9 20:49Z, discussion 20:51Z).
- STATE: user lifted R7 at 20:33Z (public probes at the session's discretion; finals = one public-aimed + one private-aimed,
  default private #37). 20:34Z "делай, я спать" (autonomous). Ladder exp70a/b/d/e already built (commit a6a9ff4).
  RI-2's "submit only with the user's explicit OK" and RI-1's "user decides R7" are moot.
- poll.log: last successful header 20:48:26Z; 26 Sep subs = #37 56563521 and #38 56563534 at 00:02Z -> 3 slots left (confirmed).
- LB CSV 20:30Z (scratch reach/...T20_30_20.csv): scores 3 dp; us rank 217, 0.954, 40 subs. 0.954 block = ranks 205-303
  (99 teams) -> we are 13th of 99 in the block, near its top: a small true gain may flip the display to 0.955.
- Our x138-based subs: only 5 of 40 (#34 25 Sep 08:09Z, #35, P36, #37, #38). x138 public 21 Sep (CONTEXT l.1381);
  we found it ~24 Sep. Part of "why not us" = late start on x138, not only R7/R9.
- VERIFIED x138 (experiments/exp56_x138_verbatim, cell 3): l.577 `_secondary_expected_sha256 = "9bac2fa0..."` hard-coded;
  l.609-611 finder accepts a manifest only if model.weight_sha256 == that sha; l.646 raises on mismatch; l.653
  SECONDARY_EDGE_WEIGHT="0.15" and l.659 SECONDARY_DETECTION_WEIGHT="0.80" hard-set AFTER the cell-0 overrides.
  Builder --set lines are appended in cell 0 (exp70d cell 0 l.110-122). => RI-2 (a)(b) and SECONDARY_EDGE_WEIGHT
  0.10/0.20 are silent no-ops (K2 re-run). RI-3's `--set SECONDARY_ARTIFACT_MANIFEST` alone: our manifest is skipped
  (sha mismatch), rglob finds pilkwang's (attached in exp58 kernel-metadata) -> silent K2 duplicate. Needs a builder patch
  (grep: no secswap / SECONDARY_EXPECTED in tools/build_probe_kernel.py yet).
- VERIFIED cell 1 = configuration guard: BIOHUB_DET_THRESHOLD must equal 0.965 (abs_tol 1e-12) else RuntimeError
  "Configuration drift detected". => RI-2's DET_THRESHOLD 0.960/0.970 rungs CRASH at cell 1.
- Valid ladder knobs (read after cell 0, not re-set later): DEEPCENTER_GAP_THRESHOLD (cell 0 l.55 -> cell 2 l.166),
  LOWDET_THRESHOLD (cell 0 l.106 -> cell 4), builder DIVINS_* knobs, LEAF_PRUNE_MIN_EDGE_PROB, DEEPCENTER_SAFE_DIV_THRESHOLD.
- 'Secondary weight:' log line (cell 3 l.655) always prints /kaggle/working/secondary_seed_weights/... -> useless as a swap
  check; use 'Secondary artifact:' (l.654) + 'Secondary SHA256:' (l.656).
- y3uanm v1 (experiments/ext_y3uanm-secondary-ft/notebook0afc5663f6.ipynb cell 6): n_epochs=1, lr=1e-5, num_workers=0,
  validate=False; cell 7 metadata "validation": "public_leaderboard_submission". out_v1 log = 6 nbconvert lines, t=5.6-10.2 s
  -> quick save, never trained publicly. Sources: 3 pilkwang + hftams/zebrahub-zsns003 (+competition). v2 needs
  y3uanm/biohub-synthetic-dataset-jose (not public).
- Did NOT: call Kaggle API (429 risk during tonight's submit window), push, submit, commit, edit tools/ or CONTEXT.md.
- 21:00Z v_intel.json written (RI-1 GO info+corr; RI-2 GO only as built exp70a/d/e, plan rungs a/b no-op, DET_THRESHOLD crash; RI-3 conditional GO with swap-patch need; RI-4 GO).
