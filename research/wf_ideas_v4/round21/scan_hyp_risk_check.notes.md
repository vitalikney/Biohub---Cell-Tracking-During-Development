# scan_hyp_risk_check notes (round 21, 2026-09-27T22:30:45Z)
- 2026-09-27T22:32:11Z dummy CSV sha256 all distinct (18 files incl exp78a/78b/79a/79d/76a/76e/75/72); Secondary artifact path differs between runs: /kaggle/input/<slug> (exp70b,70d,70q) vs /kaggle/input/datasets/<owner>/<slug> (others) -> check secswap/coordinject path resolution
- 22:35Z read CONTEXT tail (to 22:27Z probe-46 read), round20/REPORT.md, IDEAS.md I-370..I-412. Now ~22:45Z 27 Sep.
- Dummy markers (_dl/*/log, parsed by scratchpad logscan.py): 0 Traceback/FAILED/DEADLINE:/FALLING BACK/SKIPPED in exp70g/70q/72/75/76a/76d/76e/78a/78b/79a/79d.
- Dummy runtimes (end s): 70g 1409, 70q 1874, 70b 1740, 72 1437, 75 2288 (>1900), 76a 1896, 76d 1402, 76e 1279, 78a 1486, 78b 1369, 79a 1712, 79d 1305.
  Stage start (DC/lowref/divins/CI): 75 = 101/875/1286/1829 vs 79a = 50/432/791/1258 -> exp75's extra ~550 s is pre-CI machine speed (DC 2x slower), not CI.
  Dummy vs hidden L (ledger.md): 70g 1409 s -> (7.49,7.67]; 70b 1740 s -> (7.41,7.58]; 70q 1874 s -> (7.64,7.81]: dummy length is a weak predictor.
- kaggle kernels status 22:4xZ: exp81, exp80a, exp79a, exp78b COMPLETE. Pulled exp81/exp80a outputs to scratchpad (not repo).
  exp81: 1250 s, Secondary SHA256 7029fe69 at /kaggle/input/datasets/vitaliineibauer/biohub-secft-n2a-v1, nodes 121,085 (-0.14%), edges 116,961, forks 87, 0 error markers, csv sha 8132ef28.
  exp80a: 1388 s, nodes 121,252, edges 117,105, forks 116, 0 error markers, csv sha a109ad02; adds 8/0/21/24 (steals 3/0/3/12).
- Insertion adds per dummy video (eligible/added): cap6 14/6,0/0,33/6,142/6; cap8 7/0/8/8; cap12fc2 8/0/12/12; cap24fc2 8/0/21/24 -> on 44b6_0113 (eligible 14) frame cap binds at 7-8; the cap family differs mainly on high-eligible (6bba-like) videos.
- CSV sha256 (first 12) all distinct across 18 dummies; exp79a vs exp70g: same 238,335 keys, 78,320 rows with changed z/y/x (CI survived to the final CSV).
- Mount layout varies per run: 'Secondary artifact: /kaggle/input/<slug>' in exp70b/70d/70q vs '/kaggle/input/datasets/<owner>/<slug>' elsewhere.
  secswap: explicit manifest path (datasets/ layout) -> 2 pilkwang candidates -> rglob('ARTIFACT_MANIFEST.json') over /kaggle/input (~210 s on the visible run per code comment) matched by weight_sha256; raise FileNotFoundError (module level, NOT fail-soft) only if no manifest with the sha exists.
  coordinject: coordinject_find_dir globs /kaggle/input/*, */*, */*/*, */*/*/* for COORD_INJECT_MANIFEST.json -> layout-robust; sha check; all inside try -> fail-soft (CSV unchanged, 'COORDINJECT FAILED').
- CI deadline logic (exp79a cell 8): deadline_ts = KERNEL_START_TS (cell 0) + 37800 s; skip-all if start > deadline-600; worker skips a video if now + 1.25*max(sec) (first 300 s) > deadline; main kills workers at deadline+900 s (10.75 h); CSV rewrite after (2 streaming passes, ~2 s for 121k nodes on the dummy).
- All videos are 100x64x256x256 uint16 (199 train + 4 test local) -> per-worker memory is size-invariant; main-process RAM on ~100 hidden videos is the one untested CI ERROR mode.
- Own datasets (kaggle datasets list --mine): biohub-ft-weights (attached in K2 #37, COMPLETE on hidden) -> owner-dataset attachment on the rerun is proven; secft-all-v1 13:26Z, secft-n2a-v1 21:25Z.
- 22:46Z kaggle datasets files yuki0731/biohub-coord-inject: 10 files, all created 2026-08-25 09:41Z (unchanged; matches the R18-A7 pre-submit check).
- CI per-video worker s (dets): 75: 120.9(27k) 77.5(9k) 195.4(58k) 238.0(81k); 76a: 117.1/73.5/184.4/220.5; 79a: 111.3/70.9/199.1/230.4 -> t ~ 52 s + 0.00228 s/det, mean ~150-158 s.
  Hidden CI stage = N x mean / 2 workers: N 100-130 x 150-158 s / 2 = 2.1-2.9 h. K2-part kernel time ~7.3-7.7 h -> CI end 9.4-10.6 h; hard bound 10.75 h (+rewrite ~1-2 min +cells 9-14 ~minutes) -> max ~10.9 h < 12 h.
- zarr: 102 files per test video; rglob fallback on the hidden rerun adds ~100 x 102 files to ~199 x 102 train files -> ~+50% of ~210 s at most.
- No memory telemetry in any dummy log (grep RSS/memory/GiB): main-process RAM at ~100 videos + 2 CI workers (each loads one 100x64x256x256 uint16 video, 0.84 GB raw) is untested -> residual CI ERROR mode, judged low.
- 2026-09-27T22:48:41Z final JSON written: research/wf_ideas_v4/round21/scan_hyp_risk_check.json
