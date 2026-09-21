# Friend C B31 — CPU-only duplicate-node clustering

This is the MacBook-safe implementation of B31. It needs no CUDA, model weights, or image Zarrs.

## Why the boundary changed

Friend A's `dc/<stem>.npz` stores DeepCenter scores only at existing raw nodes. The full public post-processing also
queries DeepCenter at synthetic gap points, so replaying `raw -> pp` without images cannot reproduce the control.
B31 therefore starts from `ckpt/<stem>.npz`, the saved graph after motion relinking and gap closing, and applies
clustering before safe divisions and the final prune/short-track/line-fit tail. Radius zero must reproduce Friend A's
199-video control (`0.9120275`, adjusted edge `0.9023109`, divisions `24/96/127`) before any radius is trusted.

## macOS setup

Use an arm64 Python 3.11 environment. Do not follow the CUDA/data-download onboarding in the general section of
`TEAM.md`.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "numpy<3" scipy pandas networkx polars tqdm scikit-image \
  "zarr>=3.0.10,<4" "geff>=1.1.3.1.1" "tracksdata>=0.4.1" \
  "rustworkx>=0.17.1" blosc2 ipython
```

PyTorch, `ilpy`, `pyscipopt`, Kaggle competition images, and all detector weights are intentionally absent.

## Cache layout

Unpack Friend A's package and set:

```bash
export BIOHUB_LOCAL_CACHE="$HOME/biohub_friend_c/cache"
export BIOHUB_DATA_DIR="$HOME/biohub_friend_c/train"
```

The following must exist for the same 199 stems:

```text
cache/friend_a_b20_exp29/raw/<stem>.geff/
cache/friend_a_b20_exp29/dc/<stem>.npz
cache/friend_a_b20_exp29/ckpt/<stem>.npz
train/<stem>.geff/
```

## Run

The easiest entry point is the root notebook `friend-c-b31-cluster.ipynb`. Start Jupyter from the repository root and
run its cells in order. The command-line equivalent is:

```bash
python experiments/local_friend_c_b31_cluster/runner.py \
  --cache-root "$BIOHUB_LOCAL_CACHE" \
  --data-dir "$BIOHUB_DATA_DIR" \
  --output-dir outputs/local_friend_c_b31_cluster
```

The pipeline first writes the raw-vs-GT nearest-neighbour audit. It obeys the registered stop rule: if fewer than 1%
of raw detections have a neighbour below 2 micrometres, B31 is closed without wasting time on an identical sweep.
Otherwise it runs radius `0`, `0.5`, `1.0`, `1.5`, and `2.0` micrometres. Every completed video is reusable. To stop cleanly, create
`outputs/local_friend_c_b31_cluster/STOP`; the current video finishes and the next launch resumes. Removing `STOP`
allows continuation.

`--force-sweep` exists only for implementation diagnostics; it is not the registered experiment recipe.

For a two-video smoke test use a separate output directory and disable the 199-video count check:

```bash
python experiments/local_friend_c_b31_cluster/runner.py \
  --cache-root "$BIOHUB_LOCAL_CACHE" --data-dir "$BIOHUB_DATA_DIR" \
  --output-dir outputs/local_friend_c_b31_smoke --expected-videos 0 \
  --stems 44b6_0113de3b 44b6_0b24845f
```

Results are written to `results.json`, `result.md`, `nearest_neighbor_summary.json`, and one official-metric JSON per
radius. Prediction GEFFs remain under `outputs/` and must not be committed.
