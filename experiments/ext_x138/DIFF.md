# x138 vs readmit-v1 vs our exp48: full diff (2026-09-24)

Sources (pulled with `python -m kaggle kernels pull ... -m`):
- `experiments/ext_x138/biohub-x138.ipynb` = anvithpothula/biohub-x138, public LB **0.953** (one version).
- `experiments/ext_frontier947_readmit/biohub-frontier947-readmit-v1.ipynb` = thtennant/biohub-frontier947-readmit-v1, public **0.946**.
- ours: `experiments/exp48_leafprune_divins/exp48-leafprune-divins.ipynb` (probe 28, public **0.948**) = exp39 notebook +
  `--patch leafprune --patch divinsert` from `tools/build_probe_kernel.py` (the current builder rebuilds it byte-identically,
  apart from the preset name).

Cells were compared as code text (all cells are code cells). x138 and readmit-v1 have 12 cells; exp48 has 15
(x138 cell k = exp48 cell k for k = 0..3; x138 cell 4 = exp48 cell 5; x138 cell 5 = exp48 cell 8; x138 cells 6..11 =
exp48 cells 9..14; exp48 cells 4, 6, 7 have no x138 counterpart).

## 1. x138 vs readmit-v1: the head patch is the ONLY difference

11 of 12 cells are byte-identical. Cell 4 (the predict-script patch cell) gets 34 inserted lines (x138 cell 4, lines
501-534), placed after readmit's low-detection-dump patch and before `start_time = time.time()` (the prediction launch):

| x138 cell-4 lines | what |
|---|---|
| 502-510 | comment: x122 failed silently because the V1284 patch ran before readmit's lowdet patch, which anchors on the same `coord_offset[t] = ...` line; ordering it after fixes it |
| 511 | `(_ps.parent/'v1284_coordinate_refinement.py').write_text('...')` - writes the head module next to `scripts/predict_unet_transformer.py` (module text below) |
| 512-514 | head lookup: `sorted(Path('/kaggle/input').rglob('biohub-v1284-head-s075/v1284_head.pt'))`, must find exactly 1 |
| 515-518 | comment: trained on x107's 20-movie TRAIN capture (4,136 detection<->GT pairs); held-out by movie ridge -10.8 %, MLP -10.4 % centre error, 16/20 movies improve; a 4-movie head was +14.9 % worse |
| 519-520 | `os.environ['V1284_MODE']='candidate'`, `os.environ['V1284_HEAD']=str(_myhead[0])` (inherited by the two GPU-shard subprocesses) |
| 522-530 | four anchored replacements in the predict script, each asserted to match exactly once: |
| | (a) `import tracksdata as td\n` -> + `from v1284_coordinate_refinement import refine as _v1284_refine, index_features as _v1284_index` |
| | (b) `coord_offset[t] = (global_node_count, ...)` -> preceded by `arr = _v1284_refine(ds_path, t, arr, unet_out[:, f_idx])` (right after `_detect_cells_pooled`, per new frame; `unet_out` is already the edge-TTA-averaged primary feature map at that point) |
| | (c) `    coords = coords.astype(np.int16)\n` (end of predict_video) -> a comment line, i.e. the cast is REMOVED |
| | (d) `model, window_size, downsample = load_model(...)` -> + `UNetNodeTransformer._index_features = _v1284_index` (class-wide: primary AND secondary model gather trilinearly) |
| 532-533 | write the patched script, print |

Module `v1284_coordinate_refinement.py` (decoded from line 511):
- `SPACING = [1.625]*3` (the (1,4,4)-downsampled grid is isotropic 1.625 um); `OFFSETS` = centre + 6 face neighbours.
- `make_head()`: `Linear(224,32) -> SiLU -> Linear(32,3)`, last layer zero-initialised.
- `sample_features(feature, arr)`: gathers the 32-ch feature at the peak voxel and its 6 neighbours (clamped), returns
  `[centre, n1-centre, ..., n6-centre]` = 224-d.
- `bounded(head, x) = 2*d/(1+|d|)` -> displacement < 2 um.
- `refine(ds_path, t, arr, feature)`: mode `zero` -> float copy, no shift; mode `capture` -> saves `coords` + 224-d
  `features` per frame to `$V1284_CAPTURE/<movie>/<t>.npz` and returns arr unchanged; otherwise loads the head once
  (`state_dict`, `mean`, `scale`), shift_vox = bounded(head, (x-mean)/scale) / SPACING, adds it to z,y,x (downsampled
  voxels), clips to the grid, raises if any shift > 2 um or non-finite. Returns float32.
- `index_features(self, maps, coords, mask)`: trilinear gather (8 corners, clamped); at integer coordinates it equals
  the native `coords.long()` gather exactly (verified locally: `torch.equal` on random maps).

Head file `v1284_head.pt` (dataset anvithpothula/biohub-v1284-head-s075, CC0, 33,913 bytes, created 2026-09-20,
sha256 625a0d9340f48193...): `state_dict` (0.weight 32x224, 0.bias, 2.weight 3x32, 2.bias), `mean` (224), `scale` (224).

Consequences of the cast removal: coordinates stay float32 from peak refinement through edge prediction (`p_coords_*`,
positional features, edge `dist`), `build_graph` (already Float64 attrs), the ILP, the geff and the whole post-processing
tail (which already reads nodes as float and already moves nodes off-grid in linefit / gap midpoints). The CSV writer
is unchanged in x138: `int(round(float(node["z"])))` etc., so the OUTPUT is rounded to full-resolution voxels (z 1.625 um,
y/x 0.406 um). Before the patch the int16 cast was a no-op (integer peaks x (1,4,4)); with refined floats it would have
TRUNCATED (a systematic -0.5 voxel bias), which is why x138 removes it. Note the z refinement reaches the output only
when it moves a node by >= half a z-plane (0.81 um); in the tail (relink, gaps, divisions) it is used at full precision.

Nothing else is retrained or shipped: x138 attaches only the three pilkwang datasets + the head dataset.

## 2. x138 vs our exp48: every other difference

Cell 1 and cells 6-11 (x138) = cells 1, 9-14 (exp48): identical.

### Cell 0 (env knobs)
| knob | x138 | exp48 |
|---|---|---|
| `BIOHUB_DEEPCENTER_SAFE_DIV_THRESHOLD` | **0.25** | **0.20** (kept for exp51) |
| `BIOHUB_MOTION_RELINK_TIGHT_UM` | 5.5 | 5.5 (same) |
| `BIOHUB_VALIDATOR_ENABLE` | 0 | 0 (same) |
| `BIOHUB_MOTION_RELINK_FLOW_*` | MODE seed, K 12, RADIUS 40, EXCLUDE 1.5, MIN_SAMPLES 4, GATE 1, ITER 1, SEED_GATE 0 (= tight 5.5), RAW_ADMIT 1, Z_WEIGHT 1.0, **RAW_COST 0**, **FLOW_TIGHT_UM 7.0**, RELAXED 0 (= 10) | not present (no flow prior) |
| `BIOHUB_READMIT_*` | RADIUS 4, MIN_SCORE 0.965 | not present |
| `BIOHUB_GAPFILL_*` | MAX_GAP 3, MIN_SCORE 0.5, STEP 5.0, PEAK_RADIUS 3.5, EXCLUDE 2.0, ALLOW_SYNTHETIC 0, CONTEXT 1, MAX_ADDED_FRAC 0.03 | not present |
| `BIOHUB_CACHE_DIR`, `CACHE_EDGE_THRESHOLD`, `LOWDET_THRESHOLD` | /kaggle/working/edge_cache, 1.0 (= no edges cached), 0.3 | not present |
| runtime | `KERNEL_START_TS`, `ILP_TIMEOUT_S 1200`, `REPAIR_DEADLINE_S 27000`, `FRAME_CACHE_MAX_FRAMES 48` | not present |
| ours | - | `DIVNET_VERIFY 1`, `DIVNET_MIN_PROB 0.50`, `PRIMARY_OVERRIDE` popped (pilkwang primary, same as x138), leaf prune 0.3, `DIVINS_*` (enable, steal, cap 4, frame cap 1, alpha 1, thresh 0.4, dump) |
All other knobs (det 0.965, ILP app 0 / disapp 2 / div 1.2, relink bonus 1.0, gap close, density-adaptive gaps, min track
len 6, safe-div 9/14/0.6/2.25/10/0.0076/0.00375, short-track rescue, DeepCenter veto + gap veto 0.25 + TTA,
bidirectional 0.15 harmonic, retention guard 0.90) are identical.

### Cell 2 (config constants)
x138 adds the constants for the FLOW / READMIT / GAPFILL knobs above; exp48 adds `LEAF_PRUNE_MIN_EDGE_PROB` (+ display).

### Cell 3 (setup)
x138 walks `/kaggle/input` for the secondary model's manifest only when the explicit paths miss (runtime only, same result).

### Cell 4 / our cell 5 (predict-script patches)
Common: D4 detection TTA, dual-seed ensemble, retention guard, bidirectional harmonic fusion, pre-ILP coordinate
manifest (it hashes `coords.astype("<i2")` - harmless with floats), edge-feature TTA, secondary edge-feature TTA 0.75.
x138 only: (1) ILP timeout patch (`timeout=1200 s` per dataset; SCIP keeps its incumbent at the limit, so on a slow
hidden-test movie x138 could get a non-optimal ILP where we run to optimality) + ILP timing print; (2) per-dataset
detection timing print; (3) edge cache + low-detection dump (sub-threshold peaks >= 0.3 per frame, unrefined int16,
feeds readmit/gapfill); (4) the V1284 head (section 1).
Ours only: cell 4 primary-weights override (inactive: `PRIMARY_OVERRIDE` popped), cell 6 DivNet cell, cell 7 divinsert
(DaughterNet) cell.

### Cell 5 / our cell 8 (post-processing, `filter_output_graph` and the writer)
x138 only:
- runtime guard: after 27,000 s the remaining movies get relink / gap close / gap2 / safe divisions / linefit switched
  off; a movie whose repair raises is written from its ILP graph by `fallback_output_graph` (never triggers on a normal
  run); frame-cache trimming to 48 frames (memory only);
- DeepCenter checkpoint lookup skips the /kaggle/input walk when the explicit path exists (runtime only); DeepCenter
  TTA comment lines blanked (code identical);
- **flow-prior motion relink** (`_flow_predictor`, seed mode): per frame a tight Hungarian seed pass (gate 5.5, itself
  predicted with the previous frame's field), a displacement field = median of the 12 nearest seed matches within
  40 um (own match excluded if closer than 1.5 um), every source re-assigned against source + field; a pair is admitted
  if raw OR motion distance is inside the gate; tight gate 7.0 um when a field exists (5.5 otherwise), relaxed 10;
  **cost = motion + 0.0 x raw - bonus x prob** (the base hard-codes 0.05 x raw; x138 sets RAW_COST 0, which applies to
  every frame, with or without a field);
- **readmit** after the first relink: peaks >= 0.965 the ILP discarded, > 2 um from any node, within 4 um of an open
  end (t-1) or start (t+1) are added as nodes, then the relink runs again;
- **gap filler** after close_single_frame_gaps + recover_strict_gap2: bridges end(t) -> start(t+g+1), g <= 3, only
  through free sub-threshold peaks (>= 0.5, within 3.5 um of the straight line at every missing frame), direction test,
  Hungarian per (t, g), <= 3 % added nodes;
- stage timing prints.
Ours only: DivNet parent veto inside `add_safe_divisions_postlink` (p < 0.50 -> candidate skipped), leaf prune
(035 notebook, 0.3) between short-track filtering and linefit, divinsert (DaughterNet v1 insertion with steal) after
linefit.

Tail order, x138: ILP edges -> next-frame/length filter -> flow relink -> readmit -> relink -> single-parent/child repair
-> single-frame gaps -> gap2 -> gapfill -> safe divisions (DeepCenter veto) -> division geometry filter -> prune isolated
-> short-track filter (+ rescue) -> linefit -> write.
exp48: same without flow/readmit/gapfill, with the DivNet veto in safe divisions, leaf prune before linefit and
divinsert after it.

### Metadata
x138: pilkwang deepcenter / temporal seed314159 / support pack 50ep + anvithpothula/biohub-v1284-head-s075.
exp48: the same three pilkwang datasets + giorgosi/biohub-divnet-v2 + vitaliineibauer/biohub-ft-weights. Same docker
image, T4 x2.

## 3. What exp51 takes from x138
Only section 1 (the head), via `tools/build_probe_kernel.py --patch coordhead` with x138's lines verbatim (module write,
four anchored replacements, V1284_MODE candidate), inserted at the same place in the predict-patch cell (after all other
predict-script patches, before the prediction launch). Differences from x138's block, none of which touches the numbers:
guard `BIOHUB_COORDHEAD_ENABLE` (0 = predict script untouched; verified: the patched script is byte-identical to
exp48's with 0); head lookup tries the two mount paths before x138's rglob; a stats wrapper around x138's refine
(per-movie peaks / moved / mean / max / mean dz,dy,dx shift -> `COORDHEAD_STATS` log lines,
`coordhead_stats_<shard>.jsonl`, `COORDHEAD SUMMARY` after prediction, run fails if the head did not run on every movie).
Not taken: DeepCenter 0.25, flow relink, raw-cost 0, readmit, gapfill, ILP timeout, runtime guard.

## 4. exp51 run (vitaliineibauer/biohub-exp51-coordhead v1, COMPLETE, 1,713 s; not submitted)
- Head ran on 4/4 test movies: 143,634 peaks refined, mean shift 0.739 um, max 1.610 um (per movie mean/max:
  44b6_0113de3b 0.765/1.422, 44b6_0b24845f 0.707/1.312, 6bba_05b6850b 0.838/1.610, 6bba_05db0fb1 0.734/1.394 um;
  mean dz +0.14 / -0.16 / +0.46 / -0.23 um). No traceback, submission.csv valid (unique ids, no dangling edges, dt = 1,
  in-degree <= 1, out-degree <= 2).
- Reproduction check: exp51's pre-ILP coordinate manifest hashes and its raw ILP node/edge counts (121,777 / 114,927)
  are identical to x138's own run, and exp48's are identical to readmit-v1's: the transplant reproduces x138's
  prediction stage exactly.
- vs exp48: ILP nodes 125,305 -> 121,777 (-2.8 %), final nodes 122,704 -> 119,174 (-2.9 %), edges 118,381 -> 114,952,
  forks 58 -> 56; most of the drop is on 44b6_0b24845f (-10.7 % nodes). x138 shows the same drop vs readmit-v1
  (124,246 -> 121,219), so part of x138's +0.007 may be node-multiplier, not localisation.
