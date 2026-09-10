"""Build dense GEFF labels from teacher detections and sparse competition GT.

The sparse GT graph is the authority: every GT node and edge is preserved. Teacher
nodes within ``--dedup-radius-um`` of a GT node in the same frame are discarded;
the remaining teacher nodes are added without edges. GEFF metadata, including
``estimated_number_of_nodes``, is copied from GT. On Windows, matching Zarr data
is exposed through directory junctions rather than copied.

The command is resumable. A completed dense GEFF is validated and reused unless
``--overwrite`` is passed; ``dense_stats.csv`` is regenerated atomically.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import tracksdata as td
from geff import GeffMetadata
from scipy.spatial import cKDTree


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_SRC = PROJECT_ROOT / "tools" / "repo" / "src"
if str(REPO_SRC) not in sys.path:
    sys.path.insert(0, str(REPO_SRC))

from biohub_tracking.io import open_dataset  # noqa: E402


COORD_COLUMNS = ("z", "y", "x")


def read_graph(path: Path) -> tuple[td.graph.IndexedRXGraph, GeffMetadata]:
    loaded = td.graph.IndexedRXGraph.from_geff(path)
    if not isinstance(loaded, tuple) or len(loaded) < 2:
        raise RuntimeError(f"GEFF reader did not return graph metadata for {path}")
    graph, metadata = loaded[0], loaded[1]
    if not isinstance(metadata, GeffMetadata):
        raise TypeError(f"Unexpected metadata type for {path}: {type(metadata)!r}")
    return graph, metadata


def manifest_ids(path: Path, keys: tuple[str, ...]) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Dense-label manifest must be a dictionary")
    selected: list[str] = []
    for key in keys:
        values = payload.get(key)
        if not isinstance(values, list):
            raise KeyError(f"Manifest key {key!r} is missing or is not a list")
        selected.extend(str(value) for value in values)
    if len(selected) != len(set(selected)):
        raise RuntimeError("Selected manifest IDs contain duplicates")
    return selected


def points_by_frame(graph: td.graph.BaseGraph) -> dict[int, np.ndarray]:
    frame = graph.node_attrs(attr_keys=["t", *COORD_COLUMNS])
    result: dict[int, np.ndarray] = {}
    if frame.is_empty():
        return result
    for time_value in frame["t"].unique().sort().to_list():
        points = (
            frame.filter(frame["t"] == time_value)
            .select(COORD_COLUMNS)
            .to_numpy()
            .astype(np.float64, copy=False)
        )
        result[int(time_value)] = points
    return result


def teacher_gt_diagnostics(
    teacher: td.graph.BaseGraph,
    gt: td.graph.BaseGraph,
    scale_zyx: tuple[float, float, float],
    radius_um: float,
) -> tuple[np.ndarray, float]:
    teacher_attrs = teacher.node_attrs(attr_keys=["t", *COORD_COLUMNS])
    teacher_times = teacher_attrs["t"].to_numpy()
    teacher_xyz = teacher_attrs.select(COORD_COLUMNS).to_numpy().astype(np.float64, copy=False)
    keep = np.ones(teacher_attrs.height, dtype=bool)
    matched_gt = 0
    gt_total = gt.num_nodes()
    scale = np.asarray(scale_zyx, dtype=np.float64)
    gt_frames = points_by_frame(gt)

    for time_value in sorted(set(teacher_attrs["t"].to_list()) | set(gt_frames)):
        teacher_indices = np.flatnonzero(teacher_times == time_value)
        teacher_points = (
            teacher_xyz[teacher_indices]
            if teacher_indices.size
            else np.empty((0, 3), dtype=np.float64)
        )
        gt_points = gt_frames.get(int(time_value), np.empty((0, 3), dtype=np.float64))
        if not len(gt_points) or not len(teacher_points):
            continue
        tree_gt = cKDTree(gt_points * scale)
        teacher_distances, _ = tree_gt.query(teacher_points * scale, k=1)
        keep[teacher_indices] = teacher_distances > radius_um

        tree_teacher = cKDTree(teacher_points * scale)
        gt_distances, _ = tree_teacher.query(gt_points * scale, k=1)
        matched_gt += int(np.count_nonzero(gt_distances <= radius_um))

    teacher_recall = matched_gt / gt_total if gt_total else float("nan")
    return keep, teacher_recall


def validate_bounds(graph: td.graph.BaseGraph, image_shape: tuple[int, ...], dataset_id: str) -> None:
    attrs = graph.node_attrs(attr_keys=["t", *COORD_COLUMNS])
    limits = dict(zip(("t", *COORD_COLUMNS), image_shape))
    for column, upper in limits.items():
        values = attrs[column].to_numpy()
        if values.size and (np.any(values < 0) or np.any(values >= upper)):
            raise RuntimeError(f"{dataset_id}: teacher {column} coordinates are outside [0, {upper})")


def metadata_with_dense_bounds(
    metadata: GeffMetadata,
    graph: td.graph.BaseGraph,
    provenance: dict,
) -> GeffMetadata:
    attrs = graph.node_attrs(attr_keys=["t", *COORD_COLUMNS])
    bounds = {
        name: (float(attrs[name].min()), float(attrs[name].max()))
        for name in ("t", *COORD_COLUMNS)
        if attrs.height
    }
    axes = [
        axis.model_copy(update={"min": bounds[axis.name][0], "max": bounds[axis.name][1]})
        if axis.name in bounds
        else axis.model_copy()
        for axis in metadata.axes
    ]
    extra = copy.deepcopy(metadata.extra or {})
    extra["dense_label_provenance"] = provenance
    return metadata.model_copy(update={"axes": axes, "extra": extra}, deep=True)


def add_teacher_nodes(
    graph: td.graph.IndexedRXGraph,
    teacher: td.graph.BaseGraph,
    keep_mask: np.ndarray,
) -> int:
    teacher_attrs = teacher.node_attrs(attr_keys=["t", *COORD_COLUMNS])
    kept = teacher_attrs.filter(keep_mask.tolist())
    if kept.is_empty():
        return 0
    records: list[dict[str, int]] = []
    for row in kept.iter_rows(named=True):
        record = {"t": int(row["t"])}
        for coordinate in COORD_COLUMNS:
            value = float(row[coordinate])
            rounded = round(value)
            if not math.isclose(value, rounded, abs_tol=1e-6):
                raise RuntimeError(f"Teacher coordinate is not on the source voxel grid: {coordinate}={value}")
            record[coordinate] = int(rounded)
        records.append(record)
    existing_ids = graph.node_ids()
    first_id = max(existing_ids) + 1 if existing_ids else 0
    graph.bulk_add_nodes(records, indices=list(range(first_id, first_id + len(records))))
    return len(records)


def create_junction(link: Path, target: Path) -> None:
    target = target.resolve()
    if link.exists():
        try:
            if os.path.samefile(link, target):
                return
        except OSError:
            pass
        raise FileExistsError(f"Existing Zarr path is not the expected junction: {link}")
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        completed = subprocess.run(
            ["cmd.exe", "/c", "mklink", "/J", str(link), str(target)],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"Failed to create junction {link} -> {target}:\n{completed.stdout}{completed.stderr}")
    else:
        link.symlink_to(target, target_is_directory=True)


def validate_dense_graph(
    dense: td.graph.BaseGraph,
    gt: td.graph.BaseGraph,
    teacher: td.graph.BaseGraph,
    teacher_keep_mask: np.ndarray,
    expected_dense_nodes: int,
    dataset_id: str,
) -> None:
    if dense.num_nodes() != expected_dense_nodes:
        raise RuntimeError(
            f"{dataset_id}: dense node count {dense.num_nodes()} != expected {expected_dense_nodes}"
        )
    dense_edges = {tuple(edge) for edge in dense.edge_list()}
    gt_edges = {tuple(edge) for edge in gt.edge_list()}
    if dense.num_edges() != gt.num_edges() or dense_edges != gt_edges:
        raise RuntimeError(f"{dataset_id}: dense graph does not preserve the GT edge set exactly")
    dense_ids = set(dense.node_ids())
    if not set(gt.node_ids()).issubset(dense_ids):
        raise RuntimeError(f"{dataset_id}: one or more GT node IDs are absent from the dense graph")
    dense_attrs = dense.node_attrs(attr_keys=["node_id", "t", *COORD_COLUMNS])
    dense_teacher_rows = dense_attrs.filter(~dense_attrs["node_id"].is_in(gt.node_ids())).select(
        ["t", *COORD_COLUMNS]
    )
    teacher_rows = teacher.node_attrs(attr_keys=["t", *COORD_COLUMNS]).filter(
        teacher_keep_mask.tolist()
    )
    dense_teacher_points = Counter(tuple(int(round(float(value))) for value in row) for row in dense_teacher_rows.iter_rows())
    expected_teacher_points = Counter(tuple(int(round(float(value))) for value in row) for row in teacher_rows.iter_rows())
    if dense_teacher_points != expected_teacher_points:
        raise RuntimeError(f"{dataset_id}: reused dense graph does not contain the expected teacher nodes")


def build_one(
    dataset_id: str,
    data_dir: Path,
    teacher_dir: Path,
    output_dir: Path,
    radius_um: float,
    overwrite: bool,
) -> dict:
    gt_path = data_dir / f"{dataset_id}.geff"
    teacher_path = teacher_dir / f"{dataset_id}.geff"
    source_zarr = data_dir / f"{dataset_id}.zarr"
    dense_path = output_dir / f"{dataset_id}.geff"
    dense_zarr = output_dir / f"{dataset_id}.zarr"
    for required in (gt_path, teacher_path, source_zarr):
        if not required.exists():
            raise FileNotFoundError(required)

    gt, gt_metadata = read_graph(gt_path)
    teacher, _ = read_graph(teacher_path)
    dataset = open_dataset(data_dir / dataset_id, require_tracks=False, load_image=False)
    if dataset.image_shape is None:
        raise RuntimeError(f"{dataset_id}: image shape is unavailable")
    scale = tuple(float(value) for value in dataset.scale)
    validate_bounds(teacher, dataset.image_shape, dataset_id)
    keep_mask, teacher_recall = teacher_gt_diagnostics(teacher, gt, scale, radius_um)
    n_kept = int(np.count_nonzero(keep_mask))
    expected_dense_nodes = gt.num_nodes() + n_kept

    if overwrite and dense_path.exists():
        if not dense_path.resolve().is_relative_to(output_dir.resolve()):
            raise RuntimeError(f"Refusing to remove an unexpected dense path: {dense_path}")
        shutil.rmtree(dense_path) if dense_path.is_dir() else dense_path.unlink()

    if not dense_path.exists():
        # Keep ``gt`` immutable for the checks below.  ``bulk_add_nodes`` mutates
        # an IndexedRXGraph in place, so build on a fresh graph instance.
        dense_graph, _ = read_graph(gt_path)
        added = add_teacher_nodes(dense_graph, teacher, keep_mask)
        if added != n_kept:
            raise RuntimeError(f"{dataset_id}: added {added} teacher nodes, expected {n_kept}")
        provenance = {
            "builder": "tools/build_dense_gt.py",
            "teacher": "exp03B + pilkwang seed314159 ensemble, det_threshold=0.965",
            "dedup_radius_um": radius_um,
            "gt_wins": True,
            "edges": "competition GT only",
        }
        dense_metadata = metadata_with_dense_bounds(gt_metadata, dense_graph, provenance)
        temporary = output_dir / f".{dataset_id}.geff.building"
        if temporary.exists():
            if not temporary.resolve().is_relative_to(output_dir.resolve()):
                raise RuntimeError(f"Refusing to remove unexpected temporary path: {temporary}")
            shutil.rmtree(temporary) if temporary.is_dir() else temporary.unlink()
        dense_graph.to_geff(temporary, geff_metadata=dense_metadata, overwrite=True)
        temporary.replace(dense_path)

    dense, dense_metadata = read_graph(dense_path)
    validate_dense_graph(dense, gt, teacher, keep_mask, expected_dense_nodes, dataset_id)
    create_junction(dense_zarr, source_zarr)

    gt_attrs = (
        gt.node_attrs(attr_keys=["node_id", "t", *COORD_COLUMNS])
        .sort("node_id")
        .select(["t", *COORD_COLUMNS])
    )
    dense_attrs = dense.node_attrs(attr_keys=["node_id", "t", *COORD_COLUMNS])
    dense_gt_attrs = (
        dense_attrs.filter(dense_attrs["node_id"].is_in(gt.node_ids()))
        .sort("node_id")
        .select(["t", *COORD_COLUMNS])
    )
    gt_recall = 1.0 if gt_attrs.equals(dense_gt_attrs) else 0.0
    estimated = float((gt_metadata.extra or {}).get("estimated_number_of_nodes", float("nan")))
    if not math.isfinite(estimated) or estimated <= 0:
        raise RuntimeError(f"{dataset_id}: GT metadata has no valid estimated_number_of_nodes")
    dense_estimated = float((dense_metadata.extra or {}).get("estimated_number_of_nodes", float("nan")))
    if dense_estimated != estimated:
        raise RuntimeError(f"{dataset_id}: estimated_number_of_nodes was not preserved")
    ratio = dense.num_nodes() / estimated
    return {
        "dataset": dataset_id,
        "n_gt": gt.num_nodes(),
        "n_gt_edges": gt.num_edges(),
        "n_teacher": teacher.num_nodes(),
        "n_teacher_kept": n_kept,
        "n_teacher_dropped_near_gt": teacher.num_nodes() - n_kept,
        "n_dense": dense.num_nodes(),
        "estimated_number_of_nodes": estimated,
        "n_dense_over_estimated": ratio,
        "gt_node_recall_in_dense": gt_recall,
        "teacher_recall_of_gt_5um": teacher_recall,
        "ratio_outside_0.9_1.1": not 0.9 <= ratio <= 1.1,
        "scale_z_um": scale[0],
        "scale_y_um": scale[1],
        "scale_x_um": scale[2],
    }


def atomic_write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError("No dense rows were produced")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--teacher-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--manifest-keys", default="train,holdout")
    parser.add_argument("--dedup-radius-um", type=float, default=5.0)
    parser.add_argument("--stats-out", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=0, help="Smoke-test limit; 0 means all selected videos")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    data_dir = args.data_dir.resolve()
    teacher_dir = args.teacher_dir.resolve()
    output_dir = args.output_dir.resolve()
    manifest = args.manifest.resolve()
    keys = tuple(key.strip() for key in args.manifest_keys.split(",") if key.strip())
    ids = manifest_ids(manifest, keys)
    if args.limit:
        ids = ids[: args.limit]
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for index, dataset_id in enumerate(ids, start=1):
        row = build_one(
            dataset_id,
            data_dir,
            teacher_dir,
            output_dir,
            args.dedup_radius_um,
            args.overwrite,
        )
        rows.append(row)
        print(
            f"[{index}/{len(ids)}] {dataset_id}: GT={row['n_gt']} teacher={row['n_teacher']} "
            f"dense={row['n_dense']} dense/est={row['n_dense_over_estimated']:.3f} "
            f"teacher-recall@5um={row['teacher_recall_of_gt_5um']:.3f}",
            flush=True,
        )

    if any(row["gt_node_recall_in_dense"] != 1.0 for row in rows):
        raise RuntimeError("GT recall inside dense output is not 1.0")
    atomic_write_csv(args.stats_out.resolve(), rows)
    print(f"Wrote {len(rows)} verified rows to {args.stats_out.resolve()}")


if __name__ == "__main__":
    main()
