# Friend A B33 — resumable post-processing grid on 199 videos

Entry point: root-level `friend-a-b33-pp-grid.ipynb`.

This implements line 1 of the 23 September `PROMPT_FRIEND_A.md` block. It
reuses the 199 B20 raw graphs and executes the exp29 notebook's own
post-processing functions. Detector inference is not repeated.

Safety fixes applied by the runner:

- the realised exp29 control explicitly uses tight relink radius 5.5 um;
- every override uses the required `BIOHUB_` prefix;
- the source cache is explicitly
  `outputs/local_friend_a_b20_divnet/cache/friend_a_b20_exp29/raw`;
- the full run discovers exactly 199 raw/image/GT triples instead of silently
  using `public_local.py`'s default 12-video holdout;
- every `(variant, video)` GEFF is read back and receives an atomic completion
  marker; reruns skip it;
- score, adjusted edge, divisions and node ratio are written for all videos and
  separately for 44b6/6bba after every completed variant.

## Stop and resume

Interrupt Kernel is safe between videos. For a cooperative stop, create:

`C:\Projects\CellTracker\outputs\local_friend_a_pp_grid_199\STOP_REQUESTED`

Delete it and Run All to resume. Runtime outputs are outside git.

## Useful overrides

```powershell
$env:BIOHUB_B33_MAX_VIDEOS = "2"              # balanced smoke; separate smoke_2 output
$env:BIOHUB_B33_VARIANTS = "control,relink_off"
$env:BIOHUB_B33_MAX_VARIANTS = "2"
$env:BIOHUB_B33_RUN = "0"                     # preflight only
jupyter lab
```

The full default is the registered one-knob grid. `control` is automatically
prepended whenever a subset is requested because all gates are deltas from it.
Most variants reuse CPU post-processing; the DeepCenter variants and the DivNet
veto can use the GPU. The default full grid contains 45 variants.

## Verification before hand-off

- full preflight found exactly 199 raw/image/GT triples and all 45 variants;
- a balanced two-video smoke completed for `control`, `relink_off` and
  `divnet_veto_on`;
- rerunning that smoke reused all six atomic completion markers and only
  recomputed the reports;
- the smoke scores are implementation checks only and are not B33 results.

## Outputs

- `results/grid.csv` and `results/grid.md`: live ranking and gates;
- `results/variants/<name>.json`: official metrics and per-video rows;
- `predictions/<name>/<stem>.geff`: post-processed graphs;
- `completed/<name>/<stem>.json`: atomic resume markers;
- `state.json`: compact run state.

The notebook never submits to Kaggle and does not modify the B20 cache.
