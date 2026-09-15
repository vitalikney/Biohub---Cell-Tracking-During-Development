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

Requires: local competition videos (see `tools/kaggle_fetch_videos.py`) and the Kaggle weight datasets
downloaded to `--weights-root` (default ~/biohub_weights).
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
DEFAULT_WEIGHTS_ROOT = Path.home() / "biohub_weights"
DEFAULT_DATA = PROJECT_ROOT / "biohub-cell-tracking-during-development" / "train"
DEFAULT_CACHE = Path(os.environ.get("BIOHUB_LOCAL_CACHE", PROJECT_ROOT / ".public_local_cache"))
DEFAULT_NOTEBOOK = PROJECT_ROOT / "experiments/exp29_sjlee947_verbatim/exp29-sjlee947-verbatim.ipynb"

SUPPORT_PACK = "biohub-tracking-support-pack-50ep-v1"
SECONDARY_PACK = "biohub-temporal-unet3d-seed314159-v1"
DEEPCENTER_PACK = "biohub-deepcenter-unet3d-center-prior-v1"
FT_WEIGHTS = "biohub-ft-weights"

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
    support = weights_root / SUPPORT_PACK
    if not (support / "repo" / "scripts").is_dir():
        raise FileNotFoundError(f"support pack not found under {support}")
    repo = work / "tracking_repo"
    if materialise_code:
        if repo.exists():
            shutil.rmtree(repo)
        shutil.copytree(support / "repo", repo)
        shutil.copytree(support / "weights", repo / "weights")

    primary_dir = repo / "weights" / "unet_transformer" / "split_0"
    if primary_override and materialise_code:
        src = weights_root / FT_WEIGHTS / primary_override
        if not (src / "edge_predictor_best.pth").is_file():
            raise FileNotFoundError(f"primary override weights not found: {src}")
        for name in ("edge_predictor_best.pth", "config.json"):
            shutil.copy(src / name, primary_dir / name)
        print(f"PRIMARY OVERRIDE: {primary_override} -> {primary_dir}")

    if secondary_override:
        src = weights_root / FT_WEIGHTS / secondary_override
        if not (src / "edge_predictor_best.pth").is_file():
            raise FileNotFoundError(f"secondary override weights not found: {src}")
        secondary = work / "secondary_seed_weights" / "unet_transformer" / "split_0"
        secondary.mkdir(parents=True, exist_ok=True)
        if materialise_code:
            for name in ("edge_predictor_best.pth", "config.json"):
                shutil.copy(src / name, secondary / name)
        secondary_weights = secondary / "edge_predictor_best.pth"
        print(f"SECONDARY OVERRIDE: {secondary_override} -> {secondary_weights}")
    else:
        secondary_weights = (weights_root / SECONDARY_PACK / "weights" / "unet_transformer" / "split_0"
                             / "edge_predictor_best.pth")
    if not secondary_weights.is_file():
        raise FileNotFoundError(f"secondary weights not found: {secondary_weights}")

    deepcenter = weights_root / DEEPCENTER_PACK / "weights" / "full_frame_center" / "best.pt"
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

        g = nx.DiGraph()
        for node_id, node in nodes_by_id.items():
            g.add_node(int(node_id), t=int(node["t"]),
                       z=float(node["z"]), y=float(node["y"]), x=float(node["x"]))
        for edge in edges:
            g.add_edge(int(edge["source_id"]), int(edge["target_id"]))
        pp_io.save(g, out_dir / f"{dataset}.geff")

        rows.append({"dataset": dataset, "raw_nodes": raw_nodes, "nodes": len(nodes_by_id),
                     "raw_edges": stats["raw_edges"], "edges": len(edges),
                     "safe_divisions_added": stats.get("safe_divisions_added", 0),
                     "gap_added_nodes": stats.get("gap_added_nodes", 0),
                     "short_track_nodes_removed": stats.get("short_track_nodes_removed", 0)})
    return rows


def score_dir(out_dir: Path, data_dir: Path) -> dict:
    os.environ["BIOHUB_DATA_DIR"] = str(data_dir)
    sys.path.insert(0, str(TOOLS))
    import importlib
    scorer = importlib.import_module("score_geffs")
    summary, _rows = scorer.score(sorted(out_dir.glob("*.geff")), quiet=False)
    return summary


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
    ap.add_argument("--primary", default=None, help="folder in biohub-ft-weights to use as PRIMARY")
    ap.add_argument("--secondary", default=None, help="folder in biohub-ft-weights to use as SECONDARY")
    ap.add_argument("--stage", choices=["all", "infer", "pp"], default="all")
    ap.add_argument("--force-infer", action="store_true")
    ap.add_argument("--unet-batch-size", type=int, default=None)
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
    summary = score_dir(out_dir, data_dir)

    print("\n== %s/%s  score=%.4f adj_edge=%.4f edge=%.4f div=%.4f (%d/%d/%d) recall=%.4f n=%d"
          % (args.tag, args.label, summary["score"], summary["adj_edge_jaccard"], summary["edge_jaccard"],
             summary["division_jaccard"], summary["division_tp"], summary["division_fp"],
             summary["division_fn"], summary["node_recall"], len(rows)))

    result = {
        "tag": args.tag, "label": args.label, "notebook": args.notebook,
        "primary": args.primary, "secondary": args.secondary,
        "env_overrides": args.env, "videos": stems, "summary": summary, "per_video": rows,
    }
    result_path = cache / "pp" / f"{args.label}.json"
    result_path.write_text(json.dumps(result, indent=2))
    print("wrote", result_path)


if __name__ == "__main__":
    main()
