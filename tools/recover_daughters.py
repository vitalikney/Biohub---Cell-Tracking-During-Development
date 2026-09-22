"""B35 Step A: cache low-threshold public-primary peaks and audit daughter reach.

The detector is the public primary checkpoint with the public runtime detection
TTA, threshold 0.90 and physical NMS 3 um.  It runs once per full video rather
than once per candidate parent.  Peak caches are atomic and reusable.  The
audit adds only peaks that are at least 3 um from an existing node and within
20 um of an eligible one-child parent, then recomputes the B35 official-window
necessary detection condition.  This is a diagnostic, not a competition score.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
VERSION = "b35-step-a-full-frame-primary-v1"
DEFAULT_THRESHOLD = 0.90
DEFAULT_NMS_UM = 3.0
DEFAULT_PARENT_UM = 20.0
DEFAULT_EXISTING_UM = 3.0
REACH_GATE = 144
NODE_RATIO_GATE = 0.003


def json_default(value: Any) -> Any:
    item = getattr(value, "item", None)
    if callable(item):
        converted = item()
        if converted is not value:
            return converted
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=json_default),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def atomic_npz(path: Path, **arrays: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    os.replace(temporary, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def patch_detection_only(repo: Path) -> None:
    """Skip transformer edge work while retaining the public detection path."""
    script = repo / "scripts" / "predict_unet_transformer.py"
    text = script.read_text(encoding="utf-8")
    signature_anchor = "    secondary_low_margin_max: float = 0.2,\n) -> tuple[np.ndarray, list[tuple[int, int, float, float]]]:"
    signature_replacement = (
        "    secondary_low_margin_max: float = 0.2,\n"
        "    detections_only: bool = False,\n"
        ") -> tuple[np.ndarray, list[tuple[int, int, float, float]]]:"
    )
    if text.count(signature_anchor) != 1:
        raise RuntimeError("Detection-only signature anchor drifted in the public runtime patch")
    text = text.replace(signature_anchor, signature_replacement, 1)

    edge_anchor = "        # --- Edge prediction for each consecutive pair in the window ---"
    edge_replacement = (
        "        if detections_only:\n"
        "            del unet_out\n"
        "            continue\n\n"
        + edge_anchor
    )
    if text.count(edge_anchor) != 1:
        raise RuntimeError("Detection-only edge anchor drifted in the public runtime patch")
    text = text.replace(edge_anchor, edge_replacement, 1)
    compile(text, str(script), "exec")
    script.write_text(text, encoding="utf-8")


def prepare_public_primary(args: argparse.Namespace):
    """Materialise and import the exact public primary detection runtime."""
    import torch
    from tools import public_local

    cells = public_local.notebook_cells(args.notebook)
    runtime_work = args.output / "runtime"
    runtime_work.mkdir(parents=True, exist_ok=True)
    repo, _ = public_local.materialise_repo(
        args.weights_root, runtime_work, primary_override=None, secondary_override=None,
        materialise_code=True,
    )
    namespace = public_local.build_namespace(cells, repo, runtime_work, args.data_dir)
    public_local.apply_runtime_patches(cells, namespace, repo, runtime_work)
    public_local.set_pool_kernel_um(repo, args.nms_um)
    public_local.keep_peak_prob(repo)
    patch_detection_only(repo)

    for path in (repo / "src", repo / "scripts"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    spec = importlib.util.spec_from_file_location(
        "b35_public_primary_predict", repo / "scripts" / "predict_unet_transformer.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not import the materialised public prediction script")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    if not torch.cuda.is_available():
        raise RuntimeError("B35 Step A requires CUDA")
    device = torch.device("cuda")
    weights = repo / "weights" / "unet_transformer" / "split_0" / "edge_predictor_best.pth"
    model, window_size, downsample = module.load_model(weights, device)
    config = module.PredictConfig(
        det_threshold=args.det_threshold,
        det_tta=True,
        pool_kernel_um=args.nms_um,
        use_ilp=False,
    )
    identity = {
        "version": VERSION,
        "weights": str(weights),
        "weights_sha256": sha256(weights),
        "det_threshold": args.det_threshold,
        "nms_um": args.nms_um,
        "window_size": int(window_size),
        "downsample": [int(value) for value in downsample],
        "detection_tta": "public_runtime",
        "primary_only": True,
    }
    return module, model, device, config, int(window_size), tuple(downsample), identity


def valid_peak_cache(path: Path, identity: dict[str, Any]) -> bool:
    if not path.is_file():
        return False
    try:
        with np.load(path, allow_pickle=False) as values:
            meta = json.loads(str(values["meta_json"].item()))
            peaks = values["tzyx"]
            probabilities = values["prob"]
        return meta == identity and peaks.ndim == 2 and peaks.shape[1] == 4 and len(peaks) == len(probabilities)
    except Exception:
        return False


def infer_video(
    module: Any,
    model: Any,
    device: Any,
    config: Any,
    window_size: int,
    downsample: tuple[int, ...],
    identity: dict[str, Any],
    args: argparse.Namespace,
    stem: str,
) -> Path:
    destination = args.output / "peaks90" / f"{stem}.npz"
    if valid_peak_cache(destination, identity):
        print(f"PEAK RESUME {stem}", flush=True)
        return destination

    started = time.perf_counter()
    module._LAST_PEAK_PROBS = None
    coords, edges = module.predict_video(
        model,
        args.data_dir / stem,
        device,
        cfg=config,
        window_size=window_size,
        unet_batch_size=args.unet_batch_size,
        downsample=downsample,
        detections_only=True,
    )
    if edges:
        raise RuntimeError(f"Detection-only mode unexpectedly produced {len(edges)} edges")
    probabilities = np.asarray(module._LAST_PEAK_PROBS, dtype=np.float32)
    coords = np.asarray(coords, dtype=np.int16)
    if len(coords) != len(probabilities):
        raise RuntimeError(f"Peak/probability mismatch for {stem}: {len(coords)} vs {len(probabilities)}")
    atomic_npz(
        destination,
        tzyx=coords,
        prob=probabilities,
        meta_json=np.asarray(json.dumps(identity, sort_keys=True)),
    )
    print(
        f"PEAK DONE {stem}: {len(coords)} peaks in {(time.perf_counter() - started) / 60:.1f} min",
        flush=True,
    )
    return destination


def graph_rows(graph: Any) -> tuple[dict[int, dict[str, Any]], dict[int, list[int]]]:
    rows = {
        int(row["node_id"]): {
            "t": int(row["t"]),
            "z": float(row["z"]),
            "y": float(row["y"]),
            "x": float(row["x"]),
        }
        for row in graph.node_attrs().iter_rows(named=True)
    }
    by_time: dict[int, list[int]] = {}
    for node_id, row in rows.items():
        by_time.setdefault(row["t"], []).append(node_id)
    return rows, by_time


def select_candidates(
    graph: Any,
    peaks: np.ndarray,
    probabilities: np.ndarray,
    scale: np.ndarray,
    parent_um: float,
    existing_um: float,
) -> tuple[np.ndarray, np.ndarray]:
    from scipy.spatial import cKDTree

    rows, by_time = graph_rows(graph)
    eligible_by_child_time: dict[int, list[int]] = {}
    for parent in graph.node_ids():
        parent = int(parent)
        children = list(graph.successors(parent))
        if len(children) != 1:
            continue
        child = int(children[0])
        if rows[child]["t"] != rows[parent]["t"] + 1:
            continue
        parent_zyx = np.asarray([rows[parent][key] for key in ("z", "y", "x")])
        child_zyx = np.asarray([rows[child][key] for key in ("z", "y", "x")])
        if float(np.linalg.norm((child_zyx - parent_zyx) * scale)) <= 10.0:
            eligible_by_child_time.setdefault(rows[child]["t"], []).append(parent)

    keep_indices: list[int] = []
    for frame in sorted(set(int(value) for value in peaks[:, 0])):
        frame_indices = np.flatnonzero(peaks[:, 0] == frame)
        if not len(frame_indices) or frame not in eligible_by_child_time:
            continue
        peak_physical = peaks[frame_indices, 1:].astype(np.float64) * scale
        existing_ids = by_time.get(frame, [])
        if existing_ids:
            existing_physical = np.asarray(
                [[rows[node][key] for key in ("z", "y", "x")] for node in existing_ids],
                dtype=np.float64,
            ) * scale
            distances, _ = cKDTree(existing_physical).query(peak_physical, k=1)
            unclaimed = distances >= existing_um
        else:
            unclaimed = np.ones(len(frame_indices), dtype=bool)
        if not np.any(unclaimed):
            continue
        parents = eligible_by_child_time[frame]
        parent_physical = np.asarray(
            [[rows[node][key] for key in ("z", "y", "x")] for node in parents],
            dtype=np.float64,
        ) * scale
        candidate_positions = peak_physical[unclaimed]
        parent_distances, _ = cKDTree(parent_physical).query(candidate_positions, k=1)
        local = frame_indices[unclaimed][parent_distances <= parent_um]
        keep_indices.extend(int(index) for index in local)

    selected = np.asarray(sorted(set(keep_indices)), dtype=np.int64)
    return peaks[selected], probabilities[selected]


def audit_video(args: argparse.Namespace, stem: str, peak_path: Path) -> dict[str, Any]:
    from geff import GeffMetadata
    from tools import audit_b35

    destination = args.output / "videos" / f"{stem}.json"
    with np.load(peak_path, allow_pickle=False) as values:
        peaks = values["tzyx"].astype(np.float32)
        probabilities = values["prob"].astype(np.float32)
        peak_meta = json.loads(str(values["meta_json"].item()))

    checkpoint = args.cache / "ckpt" / f"{stem}.npz"
    truth_path = args.data_dir / f"{stem}.geff"
    signature = hashlib.sha256(
        json.dumps(
            {
                "version": VERSION,
                "peak_meta": peak_meta,
                "peak_size": peak_path.stat().st_size,
                "peak_mtime": peak_path.stat().st_mtime_ns,
                "checkpoint_size": checkpoint.stat().st_size,
                "checkpoint_mtime": checkpoint.stat().st_mtime_ns,
                "truth_mtime": truth_path.stat().st_mtime_ns,
                "parent_um": args.parent_um,
                "existing_um": args.existing_um,
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    if destination.is_file():
        previous = json.loads(destination.read_text(encoding="utf-8"))
        if previous.get("fingerprint") == signature:
            print(f"AUDIT RESUME {stem}", flush=True)
            return previous

    graph = audit_b35.checkpoint_graph(checkpoint)
    baseline_nodes = int(graph.num_nodes())
    axes = {axis.name: axis for axis in GeffMetadata.read(truth_path).axes}
    scale = np.asarray([float(axes[key].scale) for key in ("z", "y", "x")], dtype=np.float64)
    candidates, candidate_probabilities = select_candidates(
        graph, peaks, probabilities, scale, args.parent_um, args.existing_um
    )

    if len(candidates):
        next_id = max((int(node) for node in graph.node_ids()), default=-1) + 1
        graph.bulk_add_nodes(
            [
                {
                    "t": int(row[0]),
                    "z": float(row[1]),
                    "y": float(row[2]),
                    "x": float(row[3]),
                    "syn": 1,
                }
                for row in candidates
            ],
            indices=list(range(next_id, next_id + len(candidates))),
        )

    loaded_truth = __import__("tracksdata").graph.IndexedRXGraph.from_geff(truth_path)
    truth = loaded_truth[0] if isinstance(loaded_truth, tuple) else loaded_truth
    augmented = audit_b35.audit_graph(graph, truth, scale, {})
    baseline_path = args.baseline_audit / "videos" / f"{stem}.json"
    if not baseline_path.is_file():
        raise FileNotFoundError(f"Run B35 A0 first; missing {baseline_path}")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline_counts = baseline["counts"]
    augmented_counts = augmented["counts"]
    ratio = len(candidates) / baseline_nodes if baseline_nodes else 0.0
    row = {
        "dataset": stem,
        "embryo": stem.split("_", 1)[0],
        "fingerprint": signature,
        "low_threshold_peaks": int(len(peaks)),
        "baseline_nodes": baseline_nodes,
        "candidate_nodes": int(len(candidates)),
        "candidate_node_ratio": float(ratio),
        "candidate_ratio_gate_pass": bool(ratio <= NODE_RATIO_GATE),
        "baseline_window_detection_necessary": int(baseline_counts["window_detection_necessary"]),
        "augmented_window_detection_necessary": int(augmented_counts["window_detection_necessary"]),
        "window_gain": int(
            augmented_counts["window_detection_necessary"]
            - baseline_counts["window_detection_necessary"]
        ),
        "gt_divisions": int(augmented_counts["gt_divisions"]),
    }
    atomic_npz(
        args.output / "candidates" / f"{stem}.npz",
        tzyx=candidates.astype(np.int16),
        prob=candidate_probabilities.astype(np.float32),
        meta_json=np.asarray(json.dumps({"fingerprint": signature, "version": VERSION}, sort_keys=True)),
    )
    atomic_json(destination, row)
    print(
        f"AUDIT DONE {stem}: reach {row['baseline_window_detection_necessary']} -> "
        f"{row['augmented_window_detection_necessary']}, candidates={len(candidates)} "
        f"({ratio:.3%})",
        flush=True,
    )
    return row


def summarise(rows: list[dict[str, Any]], output: Path, full: bool) -> dict[str, Any]:
    groups: dict[str, Any] = {}
    for group in ("all", "44b6", "6bba"):
        subset = [row for row in rows if group == "all" or row["embryo"] == group]
        baseline = sum(row["baseline_window_detection_necessary"] for row in subset)
        augmented = sum(row["augmented_window_detection_necessary"] for row in subset)
        candidates = sum(row["candidate_nodes"] for row in subset)
        nodes = sum(row["baseline_nodes"] for row in subset)
        groups[group] = {
            "videos": len(subset),
            "gt_divisions": sum(row["gt_divisions"] for row in subset),
            "baseline_window_detection_necessary": baseline,
            "augmented_window_detection_necessary": augmented,
            "window_gain": augmented - baseline,
            "candidate_nodes": candidates,
            "baseline_nodes": nodes,
            "candidate_node_ratio": candidates / nodes if nodes else 0.0,
            "max_candidate_node_ratio": max(
                (row["candidate_node_ratio"] for row in subset), default=0.0
            ),
            "videos_over_node_ratio_gate": sum(
                not row["candidate_ratio_gate_pass"] for row in subset
            ),
        }
    gate = {
        "required_reach": REACH_GATE,
        "max_candidate_node_ratio_per_video": NODE_RATIO_GATE,
        "reach_pass": groups["all"]["augmented_window_detection_necessary"] >= REACH_GATE,
        "node_ratio_pass": groups["all"]["videos_over_node_ratio_gate"] == 0,
    }
    gate["pass"] = bool(full and gate["reach_pass"] and gate["node_ratio_pass"])
    report = {
        "version": VERSION,
        "status": "complete" if full else "partial",
        "videos": len(rows),
        "groups": groups,
        "gate": gate,
        "decision": "proceed_to_step_B_regardless_of_step_A_gate",
        "step_c": "cancelled_by_2026-09-24_A0_response",
        "limitations": [
            "This is an official-window necessary detection diagnostic, not a competition score.",
            "Recovered peaks remain candidates and enter the final graph only if Step B accepts a division.",
            "The public checkpoints overlap both embryos; this is not honest LOEO model selection.",
        ],
    }
    atomic_json(output / "summary.json", report)
    lines = [
        "# B35 Step A — full-frame primary at threshold 0.90",
        "",
        f"Videos: {len(rows)}. Diagnostic only; this is not a competition score.",
        "",
        "| group | baseline reach | augmented reach | gain | candidate ratio | max/video | videos >0.3% |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for group in ("all", "44b6", "6bba"):
        value = groups[group]
        lines.append(
            f"| {group} | {value['baseline_window_detection_necessary']}/{value['gt_divisions']} | "
            f"{value['augmented_window_detection_necessary']}/{value['gt_divisions']} | "
            f"{value['window_gain']:+d} | {value['candidate_node_ratio']:.3%} | "
            f"{value['max_candidate_node_ratio']:.3%} | {value['videos_over_node_ratio_gate']} |"
        )
    lines += [
        "",
        f"Full-run gate: reach >= {REACH_GATE}/151 and every video <= {NODE_RATIO_GATE:.1%} candidate nodes.",
        f"Gate result: **{'PASS' if gate['pass'] else 'NOT PASSED / PARTIAL'}**.",
        "",
        "Proceed to Step B regardless of this gate. Step C is cancelled by the A0 response.",
        "",
        *report["limitations"],
    ]
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def resolve_stems(args: argparse.Namespace) -> list[str]:
    available = sorted(
        {path.stem for path in (args.cache / "ckpt").glob("*.npz")}
        & {path.stem for path in args.data_dir.glob("*.zarr")}
        & {path.stem for path in args.data_dir.glob("*.geff")}
    )
    stems = list(args.stems) if args.stems else available
    missing = sorted(set(stems) - set(available))
    if missing:
        raise FileNotFoundError(f"Missing complete cache/image/GT inputs: {missing[:5]}")
    return stems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline-audit", type=Path, required=True)
    parser.add_argument(
        "--notebook",
        type=Path,
        default=ROOT / "experiments/exp29_sjlee947_verbatim/exp29-sjlee947-verbatim.ipynb",
    )
    parser.add_argument("--weights-root", type=Path, default=Path.home() / "biohub_weights")
    parser.add_argument("--det-threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--nms-um", type=float, default=DEFAULT_NMS_UM)
    parser.add_argument("--parent-um", type=float, default=DEFAULT_PARENT_UM)
    parser.add_argument("--existing-um", type=float, default=DEFAULT_EXISTING_UM)
    parser.add_argument("--unet-batch-size", type=int, default=4)
    parser.add_argument("--stop-file", type=Path)
    parser.add_argument("--stems", nargs="*", default=[])
    parser.add_argument("--expect-videos", type=int, default=0)
    args = parser.parse_args()
    args.data_dir = args.data_dir.resolve()
    args.cache = args.cache.resolve()
    args.output = args.output.resolve()
    args.baseline_audit = args.baseline_audit.resolve()
    args.notebook = args.notebook.resolve()
    args.weights_root = args.weights_root.resolve()
    args.stop_file = (args.stop_file or args.output / "STOP_REQUESTED").resolve()

    stems = resolve_stems(args)
    if args.expect_videos and len(stems) != args.expect_videos:
        raise RuntimeError(f"Expected {args.expect_videos} videos, found {len(stems)}")
    if not stems:
        raise RuntimeError("No videos selected")
    args.output.mkdir(parents=True, exist_ok=True)
    state_path = args.output / "state.json"
    state = {
        "status": "running",
        "selected_videos": len(stems),
        "completed": 0,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    atomic_json(state_path, state)

    module, model, device, config, window_size, downsample, identity = prepare_public_primary(args)
    atomic_json(args.output / "detector_identity.json", identity)
    rows: list[dict[str, Any]] = []
    try:
        for index, stem in enumerate(stems, start=1):
            if args.stop_file.is_file():
                state.update(status="stopped_safely", completed=len(rows))
                atomic_json(state_path, state)
                print("SAFE STOP before next video; all completed peak caches are reusable.", flush=True)
                return
            print(f"STEP A [{index}/{len(stems)}] {stem}", flush=True)
            peak_path = infer_video(
                module, model, device, config, window_size, downsample, identity, args, stem
            )
            rows.append(audit_video(args, stem, peak_path))
            report = summarise(rows, args.output, full=False)
            state.update(
                completed=len(rows),
                updated_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
                latest=stem,
                current_reach=report["groups"]["all"]["augmented_window_detection_necessary"],
            )
            atomic_json(state_path, state)
    except KeyboardInterrupt:
        state.update(status="stopped_safely", completed=len(rows))
        atomic_json(state_path, state)
        print("SAFE STOP: the current incomplete video will be recomputed; completed videos are reusable.")
        return

    full = len(stems) == 199
    report = summarise(rows, args.output, full=full)
    state.update(status="complete", completed=len(rows), report=report)
    atomic_json(state_path, state)
    if full:
        tracked = ROOT / "experiments/local_friend_a_b32_divpair/results"
        atomic_json(tracked / "b35_step_a.json", report)
        (tracked / "b35_step_a.md").write_text(
            (args.output / "summary.md").read_text(encoding="utf-8"), encoding="utf-8"
        )
    print((args.output / "summary.md").read_text(encoding="utf-8"), flush=True)


if __name__ == "__main__":
    main()
