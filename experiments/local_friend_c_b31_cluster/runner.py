"""CPU-only, resumable B31 duplicate-node clustering from Friend A's cache.

The cache boundary is deliberately the post-gap checkpoint (``ckpt/*.npz``),
not the raw graph.  The raw-node DeepCenter cache does not contain scores for
synthetic gap points, so replaying raw -> full post-processing without frames
would silently change the control.  Starting at the checkpoint preserves the
exp29 control and still places clustering before safe divisions and the final
prune/short-track/line-fit tail.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.spatial import cKDTree


ROOT = Path(__file__).resolve().parents[2]
PORT_DIR = ROOT / "experiments" / "local_friend_b_exp02_public_port"
TOOLS_DIR = ROOT / "tools"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(PORT_DIR))

import pass2_rank_divisions as p2  # noqa: E402
import postproc  # noqa: E402
import public_local as pl  # noqa: E402


VOXEL_SCALE_UM = np.asarray([1.625, 0.40625, 0.40625], dtype=np.float64)
DEFAULT_RADII_UM = (0.0, 0.5, 1.0, 1.5, 2.0)
REFERENCE_CONTROL = {
    "score": 0.912027502438606,
    "adj_edge_jaccard": 0.9023109032483225,
    "division_tp": 24,
    "division_fp": 96,
    "division_fn": 127,
}


@dataclass
class Config:
    cache_root: Path
    data_dir: Path
    output_dir: Path
    tag: str = "friend_a_b20_exp29"
    radii_um: tuple[float, ...] = field(default_factory=lambda: DEFAULT_RADII_UM)
    stems: tuple[str, ...] = ()
    resume: bool = True
    stop_file: Path | None = None
    expected_videos: int = 199
    force_sweep: bool = False

    @property
    def cache_dir(self) -> Path:
        direct = self.cache_root
        nested = self.cache_root / self.tag
        if (direct / "ckpt").is_dir() and (direct / "raw").is_dir():
            return direct
        return nested

    def serialisable(self) -> dict[str, object]:
        row = asdict(self)
        for key in ("cache_root", "data_dir", "output_dir", "stop_file"):
            value = row[key]
            row[key] = None if value is None else str(value)
        row["radii_um"] = list(self.radii_um)
        row["stems"] = list(self.stems)
        return row


def radius_label(radius_um: float) -> str:
    if radius_um == 0:
        return "control_r0"
    return "cluster_r" + (f"{radius_um:g}".replace(".", "p"))


def config_fingerprint(cfg: Config) -> str:
    payload = json.dumps(cfg.serialisable(), sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _geff_stems(path: Path) -> set[str]:
    return {item.stem for item in path.glob("*.geff") if item.is_dir()}


def selected_stems(cfg: Config) -> list[str]:
    cache = cfg.cache_dir
    sets = {
        "raw": _geff_stems(cache / "raw"),
        "dc": {p.stem for p in (cache / "dc").glob("*.npz")},
        "ckpt": {p.stem for p in (cache / "ckpt").glob("*.npz")},
        "gt": _geff_stems(cfg.data_dir),
    }
    requested = set(cfg.stems) if cfg.stems else sets["ckpt"]
    missing = {name: sorted(requested - values) for name, values in sets.items()}
    missing = {name: values for name, values in missing.items() if values}
    if missing:
        details = "; ".join(f"{name}: {values[:5]}" for name, values in missing.items())
        raise FileNotFoundError(f"Incomplete B31 cache/data ({details})")
    stems = sorted(requested)
    if not stems:
        raise RuntimeError(f"No videos found under {cache}")
    if not cfg.stems and cfg.expected_videos and len(stems) != cfg.expected_videos:
        raise RuntimeError(f"Expected {cfg.expected_videos} cached videos, found {len(stems)}")
    return stems


def preflight(cfg: Config) -> dict[str, object]:
    stems = selected_stems(cfg)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "ok",
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "cache_dir": str(cfg.cache_dir.resolve()),
        "data_dir": str(cfg.data_dir.resolve()),
        "videos": len(stems),
        "radii_um": list(cfg.radii_um),
        "torch_required": False,
        "zarr_images_required": False,
        "weights_required": False,
        "fingerprint": config_fingerprint(cfg),
    }
    (cfg.output_dir / "preflight.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def _load_raw_graph(path: Path):
    import tracksdata as td

    loaded = td.graph.IndexedRXGraph.from_geff(path)
    return loaded[0] if isinstance(loaded, tuple) else loaded


def load_video(cache: Path, stem: str):
    with np.load(cache / "ckpt" / f"{stem}.npz", allow_pickle=False) as ck:
        ids = np.asarray(ck["node_id"], dtype=np.int64)
        rows = np.asarray(ck["tzyx_syn"], dtype=np.float64)
        src = np.asarray(ck["src"], dtype=np.int64)
        dst = np.asarray(ck["dst"], dtype=np.int64)
        prob = np.asarray(ck["edge_prob"], dtype=np.float64)
    with np.load(cache / "dc" / f"{stem}.npz", allow_pickle=False) as dc:
        dc_ids = np.asarray(dc["node_id"], dtype=np.int64)
        dc_values = np.asarray(dc["dc"], dtype=np.float64)
    nodes = {
        int(node_id): {
            "t": int(row[0]),
            "z": float(row[1]),
            "y": float(row[2]),
            "x": float(row[3]),
            "syn": int(row[4]),
        }
        for node_id, row in zip(ids, rows)
    }
    edges = [
        (int(source), int(target), None if np.isnan(value) else float(value))
        for source, target, value in zip(src, dst, prob)
    ]
    dcs = {int(node_id): float(value) for node_id, value in zip(dc_ids, dc_values)}
    graph = _load_raw_graph(cache / "raw" / f"{stem}.geff")
    attrs = graph.node_attrs()
    peak = (
        {int(node_id): float(value) for node_id, value in zip(attrs["node_id"].to_numpy(), attrs["peak_prob"].to_numpy())}
        if "peak_prob" in attrs.columns
        else {}
    )
    return nodes, edges, dcs, peak


def _edge_probability(value: float | None) -> float:
    return -np.inf if value is None or not np.isfinite(value) else float(value)


def cluster_checkpoint(
    nodes: dict[int, dict[str, float | int]],
    edges: list[tuple[int, int, float | None]],
    peak: dict[int, float],
    radius_um: float,
) -> tuple[dict[int, dict[str, float | int]], list[tuple[int, int, float | None]], dict[str, int]]:
    """Greedy score-ordered NMS with edge contraction at the post-gap checkpoint."""
    if radius_um < 0:
        raise ValueError("radius_um must be non-negative")
    if radius_um == 0:
        return dict(nodes), list(edges), {
            "input_nodes": len(nodes), "output_nodes": len(nodes), "removed_nodes": 0,
            "clusters": 0, "input_edges": len(edges), "output_edges": len(edges), "dropped_edges": 0,
        }

    mapping = {node_id: node_id for node_id in nodes}
    by_time: dict[int, list[int]] = {}
    for node_id, node in nodes.items():
        if int(node.get("syn", 0)):
            continue
        by_time.setdefault(int(node["t"]), []).append(node_id)

    clusters = 0
    removed = 0
    for frame_ids in by_time.values():
        if len(frame_ids) < 2:
            continue
        ids = np.asarray(frame_ids, dtype=np.int64)
        points = np.asarray(
            [[nodes[int(i)]["z"], nodes[int(i)]["y"], nodes[int(i)]["x"]] for i in ids],
            dtype=np.float64,
        ) * VOXEL_SCALE_UM
        scores = np.asarray([peak.get(int(i), -np.inf) for i in ids], dtype=np.float64)
        order = np.lexsort((ids, -scores))
        assigned = np.zeros(len(ids), dtype=bool)
        tree = cKDTree(points)
        for index in order:
            index = int(index)
            if assigned[index]:
                continue
            representative = int(ids[index])
            members = [int(i) for i in tree.query_ball_point(points[index], radius_um) if not assigned[int(i)]]
            if len(members) > 1:
                clusters += 1
            for member_index in members:
                assigned[member_index] = True
                node_id = int(ids[member_index])
                mapping[node_id] = representative
                if node_id != representative:
                    removed += 1

    kept_nodes = {node_id: dict(node) for node_id, node in nodes.items() if mapping[node_id] == node_id}

    # Contraction may give a representative several incoming/outgoing arcs.  Preserve
    # unaffected arcs first, then the strongest available redirected arc.  This keeps
    # the pre-division checkpoint a collection of paths (in/out degree <= 1).
    candidates: list[tuple[int, float, int, int, int, int, float | None]] = []
    seen: set[tuple[int, int, int, int]] = set()
    for source, target, probability in edges:
        mapped_source, mapped_target = mapping[source], mapping[target]
        if mapped_source == mapped_target:
            continue
        key = (mapped_source, mapped_target, source, target)
        if key in seen:
            continue
        seen.add(key)
        unchanged = int(source == mapped_source) + int(target == mapped_target)
        candidates.append(
            (unchanged, _edge_probability(probability), mapped_source, mapped_target, source, target, probability)
        )
    candidates.sort(key=lambda row: (-row[0], -row[1], row[2], row[3], row[4], row[5]))
    used_source: set[int] = set()
    used_target: set[int] = set()
    kept_edges: list[tuple[int, int, float | None]] = []
    kept_pairs: set[tuple[int, int]] = set()
    for _, _, source, target, _, _, probability in candidates:
        pair = (source, target)
        if pair in kept_pairs or source in used_source or target in used_target:
            continue
        kept_pairs.add(pair)
        used_source.add(source)
        used_target.add(target)
        kept_edges.append((source, target, probability))
    kept_edges.sort(key=lambda edge: (nodes[edge[0]]["t"], edge[0], edge[1]))
    return kept_nodes, kept_edges, {
        "input_nodes": len(nodes),
        "output_nodes": len(kept_nodes),
        "removed_nodes": removed,
        "clusters": clusters,
        "input_edges": len(edges),
        "output_edges": len(kept_edges),
        "dropped_edges": len(edges) - len(kept_edges),
    }


def _tail_namespace(cfg: Config):
    overrides = {
        "BIOHUB_OUTPUT_SAFE_DIVISIONS": "0",
        "BIOHUB_OUTPUT_MOTION_RELINK": "0",
        "BIOHUB_OUTPUT_GAP_CLOSE": "0",
        "BIOHUB_OUTPUT_GAP2_RECOVERY": "0",
        "BIOHUB_USE_DEEPCENTER_VETO": "0",
        "BIOHUB_REQUIRE_DEEPCENTER_VETO": "0",
    }
    os.environ.update(overrides)
    cells = pl.notebook_cells(pl.DEFAULT_NOTEBOOK)
    return pl.build_cached_postproc_namespace(cells, cfg.output_dir / "work", cfg.data_dir)


def _save_graph_atomic(graph, output: Path) -> None:
    temporary = output.with_name(f".{output.name}.tmp")
    if temporary.exists():
        shutil.rmtree(temporary)
    postproc.save(graph, temporary)
    if output.exists():
        shutil.rmtree(output)
    temporary.replace(output)


def _write_prediction(
    output: Path,
    nodes: dict[int, dict[str, float | int]],
    edges: list[tuple[int, int, float | None]],
    filter_output_graph,
    stem: str,
) -> tuple[int, int]:
    import networkx as nx

    node_records = {
        node_id: {
            "node_id": node_id,
            "t": node["t"], "z": node["z"], "y": node["y"], "x": node["x"],
            **({"gap_synthetic": 1} if node.get("syn") else {}),
        }
        for node_id, node in nodes.items()
    }
    edge_records = [
        {"source_id": source, "target_id": target, "edge_prob": probability}
        for source, target, probability in edges
    ]
    node_records, edge_records, _ = filter_output_graph(
        node_records, edge_records, dataset=stem, deepcenter_bundle=None
    )
    graph = nx.DiGraph()
    for node_id, node in node_records.items():
        graph.add_node(
            int(node_id), t=int(node["t"]),
            z=float(max(0, round(float(node["z"])))),
            y=float(max(0, round(float(node["y"])))),
            x=float(max(0, round(float(node["x"])))),
        )
    for edge in edge_records:
        graph.add_edge(int(edge["source_id"]), int(edge["target_id"]))
    _save_graph_atomic(graph, output)
    return len(node_records), len(edge_records)


def stop_requested(cfg: Config) -> bool:
    return cfg.stop_file is not None and cfg.stop_file.exists()


def run_radius(cfg: Config, stems: list[str], radius_um: float, filter_output_graph) -> dict[str, object]:
    label = radius_label(radius_um)
    output_dir = cfg.output_dir / "predictions" / label
    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = cfg.output_dir / f"progress_{label}.jsonl"
    progress: dict[str, dict[str, object]] = {}
    if progress_path.is_file():
        for line in progress_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                progress[str(row["dataset"])] = row
    started = time.time()
    for index, stem in enumerate(stems, start=1):
        output = output_dir / f"{stem}.geff"
        if cfg.resume and output.is_dir() and stem in progress:
            print(f"[{label} {index}/{len(stems)}] {stem}: cached", flush=True)
            continue
        if stop_requested(cfg):
            raise KeyboardInterrupt(f"Cooperative stop before {stem}; completed GEFFs are reusable")
        nodes, edges, dcs, peak = load_video(cfg.cache_dir, stem)
        nodes, edges, stats = cluster_checkpoint(nodes, edges, peak, radius_um)
        # Exact configuration recorded in control_public.config.json.
        candidates, successors, predecessors = p2.candidates(nodes, edges, dcs, peak, 9.0, 3, "add")
        scores = np.asarray(
            [(-key if (key := p2.public_key(features)) is not None else -np.inf) for *_, features in candidates],
            dtype=np.float64,
        )
        edges, added = p2.apply(
            nodes, edges, candidates, scores, successors, predecessors, "add", min_score=-np.inf
        )
        final_nodes, final_edges = _write_prediction(output, nodes, edges, filter_output_graph, stem)
        row = {
            "dataset": stem, "radius_um": radius_um, **stats,
            "division_candidates": len(candidates), "divisions_added": int(added),
            "final_nodes": final_nodes, "final_edges": final_edges,
        }
        with progress_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row) + "\n")
        progress[stem] = row
        print(
            f"[{label} {index}/{len(stems)}] {stem}: removed={stats['removed_nodes']} "
            f"edges_dropped={stats['dropped_edges']} final={final_nodes}/{final_edges}",
            flush=True,
        )

    missing = [stem for stem in stems if not (output_dir / f"{stem}.geff").is_dir()]
    if missing:
        raise RuntimeError(f"{label} incomplete: {len(missing)} outputs missing")
    missing_progress = [stem for stem in stems if stem not in progress]
    if missing_progress:
        raise RuntimeError(f"{label} has outputs without progress records: {missing_progress[:5]}")
    aggregate_keys = (
        "input_nodes", "output_nodes", "removed_nodes", "clusters",
        "input_edges", "output_edges", "dropped_edges",
        "division_candidates", "divisions_added",
    )
    aggregate = {
        key: sum(int(progress[stem][key]) for stem in stems)
        for key in aggregate_keys
    }
    summary, metric_rows = pl.score_dir(output_dir, cfg.data_dir)
    result = {
        "label": label,
        "radius_um": radius_um,
        "videos": len(stems),
        "summary": summary,
        "aggregate": aggregate,
        "metric_rows": metric_rows,
        "wall_seconds": time.time() - started,
    }
    (cfg.output_dir / f"metrics_{label}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def validate_control(result: dict[str, object], videos: int, expected_videos: int) -> None:
    if videos != expected_videos:
        return
    summary = result["summary"]
    failures = []
    if abs(float(summary["score"]) - REFERENCE_CONTROL["score"]) > 5e-6:
        failures.append(f"score={summary['score']}")
    if abs(float(summary["adj_edge_jaccard"]) - REFERENCE_CONTROL["adj_edge_jaccard"]) > 5e-6:
        failures.append(f"adj_edge={summary['adj_edge_jaccard']}")
    for key in ("division_tp", "division_fp", "division_fn"):
        if int(summary[key]) != int(REFERENCE_CONTROL[key]):
            failures.append(f"{key}={summary[key]}")
    if failures:
        raise RuntimeError("Radius-0 control does not reproduce Friend A: " + ", ".join(failures))


def _nearest_distances(attrs) -> Iterable[np.ndarray]:
    times = np.asarray(attrs["t"].to_numpy(), dtype=np.int64)
    positions = np.column_stack(
        [np.asarray(attrs[name].to_numpy(), dtype=np.float64) for name in ("z", "y", "x")]
    ) * VOXEL_SCALE_UM
    order = np.argsort(times, kind="stable")
    times, positions = times[order], positions[order]
    start = 0
    while start < len(times):
        end = int(np.searchsorted(times, times[start], side="right"))
        points = positions[start:end]
        if len(points) == 1:
            yield np.asarray([np.inf])
        else:
            distances, _ = cKDTree(points).query(points, k=2, workers=1)
            yield np.asarray(distances[:, 1], dtype=np.float64)
        start = end


def run_distance_audit(cfg: Config, stems: list[str]) -> dict[str, object]:
    result_path = cfg.output_dir / "nearest_neighbor_summary.json"
    histogram_path = cfg.output_dir / "nearest_neighbor_histogram.csv"
    if cfg.resume and result_path.is_file() and histogram_path.is_file():
        return json.loads(result_path.read_text(encoding="utf-8"))
    bins = np.linspace(0.0, 10.0, 101)
    groups = {
        "raw": {"nodes": 0, "lt1": 0, "lt2": 0, "lt3": 0, "hist": np.zeros(100, dtype=np.int64), "overflow": 0},
        "gt": {"nodes": 0, "lt1": 0, "lt2": 0, "lt3": 0, "hist": np.zeros(100, dtype=np.int64), "overflow": 0},
    }
    for index, stem in enumerate(stems, start=1):
        sources = {
            "raw": _load_raw_graph(cfg.cache_dir / "raw" / f"{stem}.geff"),
            "gt": _load_raw_graph(cfg.data_dir / f"{stem}.geff"),
        }
        for name, graph in sources.items():
            for distances in _nearest_distances(graph.node_attrs()):
                finite = distances[np.isfinite(distances)]
                groups[name]["nodes"] += len(distances)
                groups[name]["lt1"] += int(np.sum(finite < 1.0))
                groups[name]["lt2"] += int(np.sum(finite < 2.0))
                groups[name]["lt3"] += int(np.sum(finite < 3.0))
                groups[name]["hist"] += np.histogram(finite, bins=bins)[0]
                groups[name]["overflow"] += int(np.sum(finite >= bins[-1])) + int(np.sum(~np.isfinite(distances)))
        if index % 10 == 0 or index == len(stems):
            print(f"[distance audit {index}/{len(stems)}] {stem}", flush=True)
        if stop_requested(cfg):
            raise KeyboardInterrupt("Cooperative stop during distance audit")
    summary: dict[str, object] = {"videos": len(stems), "voxel_scale_um": VOXEL_SCALE_UM.tolist(), "groups": {}}
    for name, values in groups.items():
        total = int(values["nodes"])
        summary["groups"][name] = {
            "nodes": total,
            "fraction_lt_1um": values["lt1"] / total if total else 0.0,
            "fraction_lt_2um": values["lt2"] / total if total else 0.0,
            "fraction_lt_3um": values["lt3"] / total if total else 0.0,
            "overflow_or_singleton": int(values["overflow"]),
        }
    with histogram_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["group", "left_um", "right_um", "count"])
        for name, values in groups.items():
            for left, right, count in zip(bins[:-1], bins[1:], values["hist"]):
                writer.writerow([name, float(left), float(right), int(count)])
            writer.writerow([name, 10.0, "inf", int(values["overflow"])])
    result_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def write_final_report(cfg: Config, audit: dict[str, object], results: list[dict[str, object]]) -> dict[str, object]:
    rows = []
    control = next(result for result in results if float(result["radius_um"]) == 0.0)
    control_summary = control["summary"]
    control_nodes = int(control["aggregate"]["output_nodes"])
    for result in results:
        summary = result["summary"]
        output_nodes = int(result["aggregate"]["output_nodes"])
        delta = float(summary["score"]) - float(control_summary["score"])
        adj_delta = float(summary["adj_edge_jaccard"]) - float(control_summary["adj_edge_jaccard"])
        rows.append({
            "radius_um": result["radius_um"],
            "score": summary["score"],
            "delta": delta,
            "adj_edge_jaccard": summary["adj_edge_jaccard"],
            "adj_edge_delta": adj_delta,
            "division_jaccard": summary["division_jaccard"],
            "division_tp": summary["division_tp"],
            "division_fp": summary["division_fp"],
            "division_fn": summary["division_fn"],
            "checkpoint_node_ratio": output_nodes / control_nodes if control_nodes else 1.0,
            "removed_nodes": result["aggregate"]["removed_nodes"],
            "passes_gate": delta >= 0.005 and adj_delta >= -0.001,
        })
    best = max(rows, key=lambda row: float(row["score"]))
    final = {
        "experiment": "local_friend_c_b31_cluster",
        "status": "complete",
        "fingerprint": config_fingerprint(cfg),
        "cache_boundary": "post-gap checkpoint; before safe divisions and final tail",
        "distance_audit": audit,
        "rows": rows,
        "best": best,
        "decision": "pass" if best["passes_gate"] else ("final2_candidate" if 0.002 <= best["delta"] < 0.005 else "close"),
    }
    (cfg.output_dir / "results.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    lines = [
        "# Friend C B31 — duplicate-node clustering", "",
        "CPU-only cached experiment. Clustering is applied at the post-gap checkpoint, before divisions and the final tail.", "",
        "| radius (um) | score | delta | adj edge | adj delta | node ratio | removed | gate |",
        "|---:|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['radius_um']:g} | {row['score']:.6f} | {row['delta']:+.6f} | "
            f"{row['adj_edge_jaccard']:.6f} | {row['adj_edge_delta']:+.6f} | "
            f"{row['checkpoint_node_ratio']:.6f} | {row['removed_nodes']} | "
            f"{'pass' if row['passes_gate'] else 'fail'} |"
        )
    lines.extend(["", f"Decision: **{final['decision']}**.", ""])
    (cfg.output_dir / "result.md").write_text("\n".join(lines), encoding="utf-8")
    return final


def write_no_lever_report(cfg: Config, audit: dict[str, object]) -> dict[str, object]:
    raw = audit["groups"]["raw"]
    final = {
        "experiment": "local_friend_c_b31_cluster",
        "status": "complete",
        "fingerprint": config_fingerprint(cfg),
        "decision": "close_step1_no_lever",
        "reason": "raw fraction with nearest neighbour below 2 um is below the registered 1% stop gate",
        "distance_audit": audit,
        "sweep_run": False,
    }
    (cfg.output_dir / "results.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    text = (
        "# Friend C B31 — closed at Step 1\n\n"
        f"Raw detections analysed: **{int(raw['nodes']):,}**. "
        f"Fractions with a same-frame nearest neighbour below 1/2/3 um: "
        f"**{raw['fraction_lt_1um']:.8f} / {raw['fraction_lt_2um']:.8f} / "
        f"{raw['fraction_lt_3um']:.8f}**.\n\n"
        "The registered stop rule is `<1% below 2 um => no lever`. The 0.5–2.0 um sweep is therefore skipped: "
        "the public detector's physical NMS already removed every candidate pair in that range.\n"
    )
    (cfg.output_dir / "result.md").write_text(text, encoding="utf-8")
    return final


def run_pipeline(cfg: Config) -> dict[str, object]:
    report = preflight(cfg)
    stems = selected_stems(cfg)
    config_path = cfg.output_dir / "run_config.json"
    current = {"config": cfg.serialisable(), "fingerprint": config_fingerprint(cfg)}
    if config_path.is_file() and json.loads(config_path.read_text(encoding="utf-8")) != current:
        raise RuntimeError(f"Configuration changed for existing output directory: {cfg.output_dir}")
    config_path.write_text(json.dumps(current, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)
    audit = run_distance_audit(cfg, stems)
    raw_close_fraction = float(audit["groups"]["raw"]["fraction_lt_2um"])
    if raw_close_fraction < 0.01 and not cfg.force_sweep:
        print(
            f"B31 STOP GATE: raw fraction below 2 um is {raw_close_fraction:.8f} < 0.01; "
            "the radius sweep cannot change any raw detections and is skipped.",
            flush=True,
        )
        return write_no_lever_report(cfg, audit)
    namespace = _tail_namespace(cfg)
    filter_output_graph = namespace["filter_output_graph"]
    results: list[dict[str, object]] = []
    for radius_um in cfg.radii_um:
        result_path = cfg.output_dir / f"metrics_{radius_label(radius_um)}.json"
        output_dir = cfg.output_dir / "predictions" / radius_label(radius_um)
        complete = all((output_dir / f"{stem}.geff").is_dir() for stem in stems)
        if cfg.resume and complete and result_path.is_file():
            result = json.loads(result_path.read_text(encoding="utf-8"))
            print(f"[{radius_label(radius_um)}] complete result reused", flush=True)
        else:
            result = run_radius(cfg, stems, float(radius_um), filter_output_graph)
        if float(radius_um) == 0.0:
            validate_control(result, len(stems), cfg.expected_videos)
        results.append(result)
    return write_final_report(cfg, audit, results)


def compact_status(cfg: Config) -> dict[str, object]:
    stems = selected_stems(cfg)
    status = {
        radius_label(radius): sum(
            (cfg.output_dir / "predictions" / radius_label(radius) / f"{stem}.geff").is_dir()
            for stem in stems
        )
        for radius in cfg.radii_um
    }
    print(f"videos={len(stems)} completed={status} stop_file={cfg.stop_file}")
    result_path = cfg.output_dir / "results.json"
    return json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else status


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-root", required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--tag", default="friend_a_b20_exp29")
    parser.add_argument("--radii", nargs="*", type=float, default=list(DEFAULT_RADII_UM))
    parser.add_argument("--stems", nargs="*", default=[])
    parser.add_argument("--stop-file", default="")
    parser.add_argument("--expected-videos", type=int, default=199)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--force-sweep", action="store_true", help="run radii despite the registered <1% stop gate")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = Config(
        cache_root=Path(args.cache_root), data_dir=Path(args.data_dir), output_dir=Path(args.output_dir),
        tag=args.tag, radii_um=tuple(args.radii), stems=tuple(args.stems), resume=not args.no_resume,
        stop_file=Path(args.stop_file) if args.stop_file else Path(args.output_dir) / "STOP",
        expected_videos=args.expected_videos, force_sweep=args.force_sweep,
    )
    run_pipeline(cfg)


if __name__ == "__main__":
    main()
