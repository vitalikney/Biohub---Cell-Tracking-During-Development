"""Local port of the public 0.947 inference+post-processing pipeline, with cached GPU stages.

WHY THIS EXISTS (Friend B, STEP 4)
----------------------------------
The public notebook (sjlee101 `biohub-lf-dctta-v020`, reproduced by us as `experiments/exp29_*`) is a Kaggle
kernel: it predicts the hidden TEST videos and writes `submission.csv`, so none of its ~40 post-processing knobs
can be tuned locally. This script runs the SAME pipeline on local TRAIN videos with local ground truth, splits it
into a cached GPU stage and a cheap CPU stage, and scores every stage with the OFFICIAL metric.

FIDELITY: the pipeline logic is NOT re-implemented. The notebook's own cells are executed verbatim:
  * cell 2  -> all `BIOHUB_*` knob parsing and the ~90 derived constants
  * cell 4  -> the runtime patches to `predict_unet_transformer.py` (detection TTA, dual-seed blend,
               retention guard, harmonic bidirectional fusion, edge-feature TTA, secondary edge-feature TTA)
  * cell 5  -> the post-processing (motion relink, gap closing, gap2, safe divisions, DeepCenter veto,
               short-track filter, linefit), of which we call `filter_output_graph` directly
Only the I/O boundary is replaced: Kaggle input mounts -> local paths, `submission.csv` -> prediction `.geff`.
Cell 3 (pip install + artifact materialisation + sha256 checks) is replaced by a local equivalent that produces
the same `REPO_DIR` layout and exports the same environment variables.

STAGES
    infer : GPU. Patched support-pack inference -> raw ILP graphs in `--cache-dir/<tag>/raw/*.geff`.
            Skipped when the cache is complete unless `--force-infer`.
    pp    : CPU. Notebook post-processing over the cached raw graphs -> `--out-dir/*.geff`, then official score.

USAGE
    # calibration: reproduce an LB-probed config on the 12 LOEO 44b6 videos
    python tools/public_local.py --notebook experiments/exp29_sjlee947_verbatim/exp29-sjlee947-verbatim.ipynb \
        --tag exp29 --split experiments/_lib/loeo_train6bba_val44b6.json --key holdout

    # CPU-only knob sweep on the cached graphs (no GPU work)
    python tools/public_local.py --tag exp29 --stage pp --env BIOHUB_MOTION_RELINK_TIGHT_UM=5.5 --label tight55

    # weights swap (exp30 = public stack + our fine-tuned primary)
    python tools/public_local.py --notebook <exp29 nb> --tag exp30 --primary exp03B

Requires: local competition videos (see `tools/kaggle_fetch_videos.py`), the third-party packs in `external/`
(`python tools/get_kaggle_datasets.py`) and the team checkpoints in `weights_dataset/` (tracked in git).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS = PROJECT_ROOT / "tools"
DEFAULT_WEIGHTS_ROOT = Path(os.environ.get("BIOHUB_WEIGHTS_ROOT", Path.home() / "biohub_weights"))
DEFAULT_DATA = Path(os.environ.get(
    "BIOHUB_DATA_DIR",
    PROJECT_ROOT / "biohub-cell-tracking-during-development" / "train",
))
DEFAULT_CACHE = Path(os.environ.get("BIOHUB_LOCAL_CACHE", PROJECT_ROOT / ".public_local_cache"))
DEFAULT_NOTEBOOK = PROJECT_ROOT / "experiments/exp29_sjlee947_verbatim/exp29-sjlee947-verbatim.ipynb"

SUPPORT_PACK = "biohub-tracking-support-pack-50ep-v1"
SECONDARY_PACK = "biohub-temporal-unet3d-seed314159-v1"
DEEPCENTER_PACK = "biohub-deepcenter-unet3d-center-prior-v1"
FT_WEIGHTS = "biohub-ft-weights"

# Repo layout as of 2026-09-15 (params.yaml): team checkpoints are tracked in git under weights_dataset/, the
# third-party packs are fetched by tools/get_kaggle_datasets.py into git-ignored external/<owner>__<name>/.
EXTERNAL_DIR = PROJECT_ROOT / "external"
TEAM_WEIGHTS_DIR = PROJECT_ROOT / "weights_dataset"


def find_pack(name: str, weights_root: Path) -> Path:
    """Locate a third-party pack, preferring the repo's external/ layout over a flat download directory."""
    for candidate in (EXTERNAL_DIR / f"pilkwang__{name}", weights_root / name):
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(
        f"{name} not found in {EXTERNAL_DIR} or {weights_root}; "
        f"run `python tools/get_kaggle_datasets.py` to fetch it")


def find_team_weights(name: str, weights_root: Path) -> Path:
    """Locate a team checkpoint: git copy first, then the Kaggle download, then a flat directory."""
    for candidate in (TEAM_WEIGHTS_DIR / name,
                      EXTERNAL_DIR / f"vitaliineibauer__{FT_WEIGHTS}" / name,
                      weights_root / FT_WEIGHTS / name):
        if (candidate / "edge_predictor_best.pth").is_file():
            return candidate
    raise FileNotFoundError(f"checkpoint {name!r} not found under {TEAM_WEIGHTS_DIR} or {weights_root}")

# The notebook applies its runtime patches, then runs inference. Everything from this marker on is Kaggle-specific
# orchestration (test-stem discovery, 2-GPU sharding, shard merging) that we replace with our own invocation.
CELL4_RUN_MARKER = "def list_test_stems()"
# Cell 5 ends by building the Kaggle submission; we stop before that and call `filter_output_graph` ourselves.
CELL5_STOP_MARKER = 'write_test_submission("base")'


# --------------------------------------------------------------------------------------------------- notebook I/O
def notebook_cells(path: Path) -> list[str]:
    nb = json.loads(Path(path).read_text())
    return ["".join(c["source"]) for c in nb["cells"]]


def find_cell(cells: list[str], *needles: str) -> int:
    """Index of the single cell containing every needle (notebooks differ slightly between experiments)."""
    hits = [i for i, src in enumerate(cells) if all(n in src for n in needles)]
    if len(hits) != 1:
        raise RuntimeError(f"expected exactly one cell matching {needles}, found {hits}")
    return hits[0]


# ------------------------------------------------------------------------------------------- local materialisation
def materialise_repo(weights_root: Path, work: Path, primary_override: str | None,
                     secondary_override: str | None, materialise_code: bool = True) -> tuple[Path, Path]:
    """Recreate the Kaggle `REPO_DIR` layout locally; return (repo_dir, deepcenter_checkpoint).

    `materialise_code=False` only resolves paths and exports the environment variables cell 3 exports -
    used for CPU-only post-processing runs, which never touch the inference code or the model weights.
    """
    support = find_pack(SUPPORT_PACK, weights_root)
    if not (support / "repo" / "scripts").is_dir():
        raise FileNotFoundError(f"support pack at {support} has no repo/scripts")
    repo = work / "tracking_repo"
    if materialise_code:
        if repo.exists():
            shutil.rmtree(repo)
        shutil.copytree(support / "repo", repo)
        shutil.copytree(support / "weights", repo / "weights")

    primary_dir = repo / "weights" / "unet_transformer" / "split_0"
    if primary_override and materialise_code:
        src = find_team_weights(primary_override, weights_root)
        for name in ("edge_predictor_best.pth", "config.json"):
            shutil.copy(src / name, primary_dir / name)
        print(f"PRIMARY OVERRIDE: {primary_override} -> {primary_dir}")

    if secondary_override:
        src = find_team_weights(secondary_override, weights_root)
        secondary = work / "secondary_seed_weights" / "unet_transformer" / "split_0"
        secondary.mkdir(parents=True, exist_ok=True)
        if materialise_code:
            for name in ("edge_predictor_best.pth", "config.json"):
                shutil.copy(src / name, secondary / name)
        secondary_weights = secondary / "edge_predictor_best.pth"
        print(f"SECONDARY OVERRIDE: {secondary_override} -> {secondary_weights}")
    else:
        secondary_weights = (find_pack(SECONDARY_PACK, weights_root) / "weights" / "unet_transformer"
                             / "split_0" / "edge_predictor_best.pth")
    if not secondary_weights.is_file():
        raise FileNotFoundError(f"secondary weights not found: {secondary_weights}")

    deepcenter = find_pack(DEEPCENTER_PACK, weights_root) / "weights" / "full_frame_center" / "best.pt"
    if not deepcenter.is_file():
        raise FileNotFoundError(f"DeepCenter checkpoint not found: {deepcenter}")

    # Cell 3 exports these; the patched predict script and the post-processing read them from the environment.
    os.environ["BIOHUB_SECONDARY_WEIGHTS"] = str(secondary_weights)
    os.environ["BIOHUB_SECONDARY_EDGE_WEIGHT"] = "0.15"
    os.environ["BIOHUB_SECONDARY_DETECTION_WEIGHT"] = "0.80"
    os.environ["BIOHUB_SECONDARY_LINK_MODE"] = "low_margin_consensus"
    os.environ["BIOHUB_SECONDARY_MIX_TEMPERATURE"] = "1"
    os.environ["BIOHUB_SECONDARY_LOW_MARGIN_MAX"] = "0.35"
    os.environ["BIOHUB_DUAL_SEED_EDGE_THRESHOLD"] = "0.48"
    os.environ["BIOHUB_DEEPCENTER_CHECKPOINT"] = str(deepcenter)
    return repo, deepcenter


# ------------------------------------------------------------------------------------------------- notebook namespace
def build_namespace(cells: list[str], repo: Path, work: Path, data_dir: Path) -> dict:
    """Execute the notebook's env-knob cell and constants cell, then redirect Kaggle paths to local ones."""
    env_cell = find_cell(cells, "BIOHUB_PRESET", "BIOHUB_DET_THRESHOLD")
    const_cell = find_cell(cells, "COMP_DIR_CANDIDATES", "CONFIG_DISPLAY")

    ns: dict = {"__name__": "biohub_local"}
    # Knob cell: only assignments into os.environ that are not already set (our --env overrides win).
    preset_env = dict(os.environ)
    exec(compile(cells[env_cell], "<notebook:env>", "exec"), ns)
    for key, value in preset_env.items():
        if key.startswith("BIOHUB_"):
            os.environ[key] = value  # restore caller overrides clobbered by the notebook defaults

    try:
        from IPython.display import display  # noqa: F401
    except Exception:  # IPython is not needed locally; cell 2 only imports it
        import builtins

        class _Mod:
            @staticmethod
            def display(*a, **k):
                print(*a)

        sys.modules.setdefault("IPython", _Mod())
        sys.modules.setdefault("IPython.display", _Mod())
        builtins.display = _Mod.display

    exec(compile(cells[const_cell], "<notebook:const>", "exec"), ns)

    # Redirect the Kaggle mounts. TEST_DIR is what the pipeline predicts and reads raw frames from.
    ns["COMP_DIR"] = data_dir.parent
    ns["TEST_DIR"] = data_dir
    ns["WORKING_DIR"] = work
    ns["REPO_DIR"] = repo
    ns["SUBMISSION_PATH"] = work / "submission.csv"
    ns["RUN_STATS_PATH"] = work / "run_stats.csv"
    return ns


def build_cached_postproc_namespace(cells: list[str], work: Path, data_dir: Path) -> dict:
    """Load the notebook post-processing code without resolving model packs.

    This is the entry point for CPU-only work from ``ckpt/*.npz`` caches.  Callers
    must disable stages whose inputs are not present in their cache before calling
    this function (in particular inference, motion/gap reconstruction and the live
    DeepCenter model).  Unlike :func:`materialise_repo`, this helper never looks for
    weights and never imports the support-pack inference repository.
    """
    work.mkdir(parents=True, exist_ok=True)
    namespace = build_namespace(cells, PROJECT_ROOT / "tools" / "repo", work, data_dir)
    load_postproc(cells, namespace)
    return namespace


def apply_runtime_patches(cells: list[str], ns: dict, repo: Path, work: Path) -> None:
    """Run the notebook's source patches against the local copy of `predict_unet_transformer.py`."""
    idx = find_cell(cells, "TTA patch applied", CELL4_RUN_MARKER)
    src = cells[idx]
    cut = src.index(CELL4_RUN_MARKER)
    exec(compile(src[:cut], "<notebook:patches>", "exec"), ns)

    # The patches hard-code Kaggle's writable directory for their diagnostic logs.
    predict_script = repo / "scripts" / "predict_unet_transformer.py"
    text = predict_script.read_text()
    if "/kaggle/working" in text:
        text = text.replace('Path("/kaggle/working")', f'Path({str(work)!r})')
        compile(text, str(predict_script), "exec")
        predict_script.write_text(text)
        print("patched diagnostic log paths -> local working dir")


# Anchors inside the already-patched predict script. Each pair brackets the rot90 + transpose + anti-transpose
# views of one TTA loop; the flip list that precedes them is replaced separately.
_AXIS_FLIP_LIST = "for dims in [(-1,), (-2,), (-2, -1), (-3,), (-3, -1), (-3, -2), (-3, -2, -1)]:"
_PUBLIC_FLIP_LIST = "for dims in [(-1,), (-2,), (-2, -1)]:"
_ROT_BLOCKS = [
    ("            for _k in (1, 3):\n                imgs_rot = ",
     "            del imgs_at, det_at, _u_at\n            _nv += 1\n"),
    ("                    for _k in (1, 3):\n                        secondary_imgs_rot = ",
     "                    del secondary_imgs_at, secondary_det_at, _secondary_u_at\n"
     "                    _secondary_nv += 1\n"),
]


def set_pool_kernel_um(repo: Path, value: float) -> None:
    """Override the detection NMS kernel the public stack runs with.

    The support pack ships `pool_kernel_um: float = 3.0` as a plain dataclass default and never reads the
    checkpoint's `config.json`, which says 5.0 - so the public 0.947 stack suppresses peaks with a smaller
    kernel than the model was saved with, i.e. it keeps more detections. Our `tools/repo/` copy has a
    `--pool-kernel-um` flag (we added it), the shipped one does not, so patch the default instead.
    """
    predict_script = repo / "scripts" / "predict_unet_transformer.py"
    text = predict_script.read_text()
    anchor = "    pool_kernel_um: float = 3.0"
    if text.count(anchor) != 1:
        raise RuntimeError(f"expected one pool_kernel_um default, found {text.count(anchor)}")
    text = text.replace(anchor, f"    pool_kernel_um: float = {value}")
    compile(text, str(predict_script), "exec")
    predict_script.write_text(text)
    print(f"POOL KERNEL: detection NMS kernel set to {value} um (public default is 3.0)")


def _replace_once(text: str, old: str, new: str, what: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{what}: expected one anchor, found {n}: {old[:70]!r}")
    return text.replace(old, new, 1)


def keep_peak_prob(repo: Path) -> None:
    """Store each detection's peak probability as a `peak_prob` node attribute (B25 feature).

    `_detect_cells_pooled` computes sigmoid(logit) for every peak and discards it. This patch captures the
    values at the ONE call site that produces the graph's nodes (the retention guard calls the same function
    twice more per frame just to count candidates, on maps that can differ, so keying by coordinate would be
    wrong) and carries them into `build_graph`, where they become a node attribute. The ILP solver keeps extra
    node attributes and `save_graph` writes them (checked on a real graph). Nothing about detections, edges or
    the ILP changes; with the flag off this function is never called and the script stays byte-identical.
    """
    script = repo / "scripts" / "predict_unet_transformer.py"
    s = script.read_text()

    s = _replace_once(s, "def _detect_cells_pooled(",
                      "_LAST_CALL_PROBS = None\n_LAST_PEAK_PROBS = None\n\n\ndef _detect_cells_pooled(",
                      "peak-prob globals")
    s = _replace_once(s, "    logits = det_logits.unsqueeze(0)  # (1, 1, Z, Y, X)",
                      "    global _LAST_CALL_PROBS\n    logits = det_logits.unsqueeze(0)  # (1, 1, Z, Y, X)",
                      "peak-prob global decl")
    s = _replace_once(s, "        return np.empty((0, 4), dtype=np.int16)",
                      "        _LAST_CALL_PROBS = np.empty((0,), dtype=np.float32)\n"
                      "        return np.empty((0, 4), dtype=np.int16)",
                      "peak-prob empty branch")
    s = _replace_once(s, "    coords = peak_idx.float().cpu().numpy()",
                      "    _LAST_CALL_PROBS = torch.sigmoid(\n"
                      "        logits[0, 0][peak_idx[:, 0], peak_idx[:, 1], peak_idx[:, 2]]\n"
                      "    ).float().cpu().numpy()\n"
                      "    coords = peak_idx.float().cpu().numpy()",
                      "peak-prob capture")
    s = _replace_once(s, "    coord_lists: list[np.ndarray] = []",
                      "    coord_lists: list[np.ndarray] = []\n    prob_lists: list[np.ndarray] = []",
                      "peak-prob list init")
    s = _replace_once(s, "                coord_lists.append(arr)",
                      "                coord_lists.append(arr)\n                prob_lists.append(_LAST_CALL_PROBS)",
                      "peak-prob list append")
    s = _replace_once(s, "    coords = np.concatenate(coord_lists) if coord_lists else np.empty((0, 4), dtype=np.int16)",
                      "    coords = np.concatenate(coord_lists) if coord_lists else np.empty((0, 4), dtype=np.int16)\n"
                      "    global _LAST_PEAK_PROBS\n"
                      "    _LAST_PEAK_PROBS = np.concatenate(prob_lists) if prob_lists else np.empty((0,), dtype=np.float32)\n"
                      "    if len(_LAST_PEAK_PROBS) != len(coords):\n"
                      "        raise RuntimeError('peak-prob bookkeeping out of sync: %d probs vs %d coords'\n"
                      "                           % (len(_LAST_PEAK_PROBS), len(coords)))",
                      "peak-prob assembly")
    s = _replace_once(s, "    edges: list[tuple[int, int, float, float]],\n) -> td.graph.InMemoryGraph:",
                      "    edges: list[tuple[int, int, float, float]],\n    peak_probs=None,\n) -> td.graph.InMemoryGraph:",
                      "peak-prob build_graph signature")
    s = _replace_once(s, "    if edges:\n        graph.add_edge_attr_key(\"edge_prob\", pl.Float64, 0.0)",
                      "    if peak_probs is not None and len(node_ids):\n"
                      "        graph.add_node_attr_key(\"peak_prob\", pl.Float64, -1.0)\n"
                      "        graph.update_node_attrs(node_ids=node_ids,\n"
                      "                                attrs={\"peak_prob\": [float(v) for v in peak_probs]})\n\n"
                      "    if edges:\n        graph.add_edge_attr_key(\"edge_prob\", pl.Float64, 0.0)",
                      "peak-prob build_graph body")
    s = _replace_once(s, "        graph = build_graph(coords, edges)",
                      "        graph = build_graph(coords, edges, peak_probs=_LAST_PEAK_PROBS)",
                      "peak-prob build_graph call")
    compile(s, str(script), "exec")
    script.write_text(s)
    print("PEAK PROB: detection probabilities will be stored as the `peak_prob` node attribute")


def apply_axis_flip_tta(repo: Path) -> None:
    """Swap the in-plane D4 views (rot90 + transpose) for the training-consistent 8 axis flips.

    The training augmentation (`scripts/augmentations.py:flip_augment`) samples uniformly from all 8
    axis-aligned symmetries - Z, Y and X flipped independently - and never rotates or transposes. The public
    stack does the opposite: it averages over rot90 and transpose views the model never saw in training and
    skips the Z flips it did see. This makes the TTA group match the training distribution exactly, keeping the
    view count at 8 so inference cost is unchanged.

    Every edit asserts its anchor count and the result is compiled, so a drift in the upstream patches fails
    loudly instead of silently producing a different variant.
    """
    predict_script = repo / "scripts" / "predict_unet_transformer.py"
    text = predict_script.read_text()

    n_lists = text.count(_PUBLIC_FLIP_LIST)
    if n_lists != 2:
        raise RuntimeError(f"expected 2 public flip lists (primary + secondary), found {n_lists}")
    text = text.replace(_PUBLIC_FLIP_LIST, _AXIS_FLIP_LIST)

    for start, end in _ROT_BLOCKS:
        i = text.find(start)
        j = text.find(end, i + 1) if i >= 0 else -1
        if i < 0 or j < 0:
            raise RuntimeError(f"axis-flip surgery: anchors not found for block starting {start[:60]!r}")
        if text.count(start) != 1:
            raise RuntimeError(f"axis-flip surgery: ambiguous start anchor {start[:60]!r}")
        text = text[:i] + text[j + len(end):]

    if "torch.rot90(imgs" in text or "imgs.transpose(-1, -2)" in text:
        raise RuntimeError("axis-flip surgery: rotation/transpose views survived")
    compile(text, str(predict_script), "exec")
    predict_script.write_text(text)
    print("TTA GROUP: rot90/transpose views replaced by the 8 training-consistent axis flips")


# ------------------------------------------------------------------------------------------------------ GPU stage
def run_inference(ns: dict, repo: Path, work: Path, data_dir: Path, stems: list[str],
                  raw_dir: Path, unet_batch_size: int | None) -> None:
    splits_path = repo / "local_splits.json"
    splits_path.write_text(json.dumps([{"split": 0, "train": [], "test": stems}], indent=2))

    method = ns["METHOD"]
    # The support pack's `dataspec.py` hard-codes PREDICTIONS_PATH = <repo>/predictions (our `tools/repo/`
    # copy is patched to honour BIOHUB_PREDICTIONS_DIR, the shipped one is not), so set the variable for the
    # patched case and locate the output by globbing both roots afterwards.
    predictions_root = work / "predictions"

    cmd = [
        sys.executable, "scripts/predict_unet_transformer.py",
        "--data-dir", str(data_dir),
        "--splits", splits_path.name,
        "--split", "0",
        "--weights", ns["WEIGHTS_RELATIVE"],
        "--unet-batch-size", str(unet_batch_size or ns["UNET_BATCH_SIZE"]),
        "--det-threshold", str(ns["DET_THRESHOLD"]),
        "--ilp-edge-weight", str(ns["ILP_EDGE_WEIGHT"]),
        "--ilp-appearance-weight", str(ns["ILP_APPEARANCE_WEIGHT"]),
        "--ilp-disappearance-weight", str(ns["ILP_DISAPPEARANCE_WEIGHT"]),
        "--ilp-division-weight", str(ns["ILP_DIVISION_WEIGHT"]),
    ]
    if ns["USE_ILP"]:
        cmd.append("--use-ilp")

    env = {**os.environ, "PYTHONPATH": "src", "BIOHUB_PREDICTIONS_DIR": str(predictions_root)}
    print("INFER:", " ".join(cmd), flush=True)
    t0 = time.time()
    subprocess.run(cmd, cwd=repo, env=env, check=True)
    print(f"inference finished in {(time.time() - t0) / 60:.1f} min", flush=True)

    produced = sorted({p for root in (repo, work)
                       for p in root.glob(f"predictions/*/{method}/split_0/*.geff")})
    if len(produced) != len(stems):
        raise RuntimeError(f"expected {len(stems)} prediction graphs, found {len(produced)}: "
                           f"{[str(p) for p in produced[:3]]}")

    raw_dir.mkdir(parents=True, exist_ok=True)
    for geff in produced:
        dst = raw_dir / geff.name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.move(str(geff), str(dst))
    print(f"cached {len(list(raw_dir.glob('*.geff')))} raw graphs in {raw_dir}")


# ------------------------------------------------------------------------------------------------------- CPU stage
def load_postproc(cells: list[str], ns: dict) -> dict:
    """Execute the post-processing cell (stopping before the Kaggle submission writer)."""
    idx = find_cell(cells, "def filter_output_graph", "def add_safe_divisions_postlink")
    src = cells[idx]
    if CELL5_STOP_MARKER in src:
        src = src[: src.rindex(CELL5_STOP_MARKER)]
    exec(compile(src, "<notebook:postproc>", "exec"), ns)
    return ns


def postprocess_and_write(ns: dict, raw_dir: Path, out_dir: Path) -> list[dict]:
    import numpy as np  # noqa: F401  (post-proc namespace already has it)

    geff_read = ns["graph_from_geff"]
    filter_output_graph = ns["filter_output_graph"]
    bundle = ns.get("DEEPCENTER_VETO_DETECTOR")

    out_dir.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(TOOLS))
    import postproc as pp_io  # our geff writer
    import networkx as nx

    rows = []
    for geff_path in sorted(raw_dir.glob("*.geff")):
        dataset = geff_path.stem
        graph = geff_read(geff_path)

        nodes_by_id = {}
        for row in graph.node_attrs().iter_rows(named=True):
            node_id = int(row["node_id"])
            nodes_by_id[node_id] = {
                "node_id": node_id, "t": int(row["t"]),
                "z": float(row["z"]), "y": float(row["y"]), "x": float(row["x"]),
            }
        raw_edges = []
        for row in graph.edge_attrs().iter_rows(named=True):
            edge_prob = row.get("edge_prob") if hasattr(row, "get") else None
            raw_edges.append({
                "source_id": int(row["source_id"]), "target_id": int(row["target_id"]),
                "edge_prob": None if edge_prob is None else float(edge_prob),
            })

        raw_nodes = len(nodes_by_id)
        nodes_by_id, edges, stats = filter_output_graph(
            nodes_by_id, raw_edges, dataset=dataset, deepcenter_bundle=bundle
        )

        # Match what the Kaggle pipeline actually submits: `write_test_submission` rounds every coordinate to a
        # non-negative integer, so the graph the leaderboard scores has integer positions. Keeping floats here
        # would score a slightly different graph than the one the LB number came from (linefit smoothing puts
        # nodes at sub-voxel positions), which is exactly the kind of drift calibration must not have.
        g = nx.DiGraph()
        for node_id, node in nodes_by_id.items():
            g.add_node(int(node_id), t=int(node["t"]),
                       z=float(max(0, round(float(node["z"])))),
                       y=float(max(0, round(float(node["y"])))),
                       x=float(max(0, round(float(node["x"])))))
        for edge in edges:
            g.add_edge(int(edge["source_id"]), int(edge["target_id"]))
        pp_io.save(g, out_dir / f"{dataset}.geff")

        rows.append({"dataset": dataset, "raw_nodes": raw_nodes, "nodes": len(nodes_by_id),
                     "raw_edges": stats["raw_edges"], "edges": len(edges),
                     "safe_divisions_added": stats.get("safe_divisions_added", 0),
                     "gap_added_nodes": stats.get("gap_added_nodes", 0),
                     "short_track_nodes_removed": stats.get("short_track_nodes_removed", 0)})
    return rows


def score_dir(out_dir: Path, data_dir: Path) -> tuple[dict, list[dict]]:
    """Official metric over a directory of prediction graphs.

    The per-video rows are returned as well as the summary: the metric is weighted by GT edge count, so a
    subset score (e.g. only the videos a fine-tuned checkpoint never trained on) has to be re-summarised from
    the rows rather than averaged from the totals.
    """
    os.environ["BIOHUB_DATA_DIR"] = str(data_dir)
    sys.path.insert(0, str(TOOLS))
    import importlib
    scorer = importlib.import_module("score_geffs")
    summary, rows = scorer.score(sorted(out_dir.glob("*.geff")), quiet=False)
    return summary, rows


# ------------------------------------------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--notebook", default=str(DEFAULT_NOTEBOOK), help="source of the pipeline cells")
    ap.add_argument("--tag", required=True, help="cache key for the GPU stage (one per model/TTA combination)")
    ap.add_argument("--label", default="base", help="name of this post-processing run inside the tag")
    ap.add_argument("--split", default=str(PROJECT_ROOT / "experiments/_lib/loeo_train6bba_val44b6.json"))
    ap.add_argument("--key", default="holdout")
    ap.add_argument("--stems", nargs="*", default=[], help="explicit video list (overrides --split)")
    ap.add_argument("--limit", type=int, default=0, help="use only the first N videos (smoke tests)")
    ap.add_argument("--data-dir", default=str(DEFAULT_DATA))
    ap.add_argument("--weights-root", default=str(DEFAULT_WEIGHTS_ROOT))
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    ap.add_argument("--primary", default=None, help="checkpoint name under weights_dataset/ to use as PRIMARY")
    ap.add_argument("--secondary", default=None, help="checkpoint name under weights_dataset/ to use as SECONDARY")
    ap.add_argument("--stage", choices=["all", "infer", "pp"], default="all")
    ap.add_argument("--force-infer", action="store_true")
    ap.add_argument("--unet-batch-size", type=int, default=None)
    ap.add_argument("--pool-kernel-um", type=float, default=None,
                    help="detection NMS kernel in um; the public stack hard-codes 3.0 while the checkpoint's "
                         "config.json says 5.0")
    ap.add_argument("--keep-peak-prob", action="store_true",
                    help="store each detection's peak probability as a `peak_prob` node attribute (B25 feature); "
                         "detections, edges and ILP are unchanged")
    ap.add_argument("--tta-group", choices=["public", "axisflip"], default="public",
                    help="'axisflip' replaces the rot90/transpose TTA views by the 8 training-consistent "
                         "axis flips (same view count, matches scripts/augmentations.py)")
    ap.add_argument("--env", nargs="*", default=[], metavar="K=V",
                    help="BIOHUB_* overrides applied on top of the notebook preset")
    args = ap.parse_args()

    for item in args.env:
        key, _, value = item.partition("=")
        os.environ[key] = value
        print(f"ENV OVERRIDE {key}={value}")

    data_dir = Path(args.data_dir)
    cache = Path(args.cache_dir) / args.tag
    work = cache / "work"
    raw_dir = cache / "raw"
    out_dir = cache / "pp" / args.label
    work.mkdir(parents=True, exist_ok=True)

    stems = list(args.stems) or list(json.load(open(args.split))[args.key])
    if args.limit:
        stems = stems[: args.limit]
    missing = [s for s in stems if not (data_dir / f"{s}.zarr").is_dir()]
    if missing:
        raise SystemExit(f"missing local videos ({len(missing)}): {missing[:5]}"
                         f"\nfetch them with tools/kaggle_fetch_videos.py")
    print(f"{len(stems)} videos | tag={args.tag} label={args.label} | cache={cache}")

    cells = notebook_cells(Path(args.notebook))
    have_raw = {p.stem for p in raw_dir.glob("*.geff")} if raw_dir.is_dir() else set()
    need_infer = args.stage in ("all", "infer") and (args.force_infer or not set(stems) <= have_raw)

    repo, _ = materialise_repo(Path(args.weights_root), work, args.primary, args.secondary,
                               materialise_code=need_infer)
    ns = build_namespace(cells, repo, work, data_dir)

    if need_infer:
        apply_runtime_patches(cells, ns, repo, work)
        if args.pool_kernel_um is not None:
            set_pool_kernel_um(repo, args.pool_kernel_um)
        if args.keep_peak_prob:
            keep_peak_prob(repo)
        if args.tta_group == "axisflip":
            apply_axis_flip_tta(repo)
        run_inference(ns, repo, work, data_dir, stems, raw_dir, args.unet_batch_size)
    elif args.stage != "pp":
        print(f"GPU stage cached ({len(have_raw)} graphs in {raw_dir}); skipping inference")

    if args.stage == "infer":
        return

    load_postproc(cells, ns)
    # The post-processing cell already loads the veto model at module level; only load it again if it did not.
    if ns.get("DEEPCENTER_VETO_DETECTOR") is None:
        ns["DEEPCENTER_VETO_DETECTOR"] = ns["load_deepcenter_veto_detector"]()
    rows = postprocess_and_write(ns, raw_dir, out_dir)
    summary, metric_rows = score_dir(out_dir, data_dir)

    print("\n== %s/%s  score=%.4f adj_edge=%.4f edge=%.4f div=%.4f (%d/%d/%d) recall=%.4f n=%d"
          % (args.tag, args.label, summary["score"], summary["adj_edge_jaccard"], summary["edge_jaccard"],
             summary["division_jaccard"], summary["division_tp"], summary["division_fp"],
             summary["division_fn"], summary["node_recall"], len(rows)))

    result = {
        "tag": args.tag, "label": args.label, "notebook": args.notebook,
        "primary": args.primary, "secondary": args.secondary, "tta_group": args.tta_group,
        "pool_kernel_um": args.pool_kernel_um, "keep_peak_prob": args.keep_peak_prob,
        "env_overrides": args.env, "videos": stems, "summary": summary,
        "per_video": rows, "metric_rows": metric_rows,
    }
    result_path = cache / "pp" / f"{args.label}.json"
    result_path.write_text(json.dumps(result, indent=2))
    print("wrote", result_path)


if __name__ == "__main__":
    main()
