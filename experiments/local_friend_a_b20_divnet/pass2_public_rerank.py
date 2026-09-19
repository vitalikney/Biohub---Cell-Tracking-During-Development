"""B20 follow-up: re-rank the prompt-defined public orphan candidates.

The first B20 run used a 15 um orphan+steal pool.  This follow-up keeps only
orphan candidates, the public hard gates/caps/veto, parent distance <= 12 um,
and sister separation >= 5 um.  It changes only proposal ordering.  The
optional hybrid uses ``DivNet p * 1 / (1 + public geometry cost in um)``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "experiments" / "local_friend_b_exp02_public_port"))

import pass2_rank_divisions as p2  # noqa: E402
import public_local as pl  # noqa: E402


def stop_requested() -> bool:
    value = os.environ.get("BIOHUB_B20_STOP_FILE", "").strip()
    return bool(value) and Path(value).exists()


def load_parent_scores(path: Path, stem: str) -> dict[int, float]:
    source = path / f"{stem}.npz" if path.is_dir() else path
    with np.load(source, allow_pickle=False) as payload:
        values = np.asarray(payload["score"], dtype=np.float64)
        if path.is_dir() or "stem" not in payload.files:
            return {
                int(parent): float(value)
                for parent, value in zip(payload["p"], values)
            }
        return {
            int(parent): float(value)
            for item_stem, parent, value in zip(payload["stem"], payload["p"], values)
            if str(item_stem) == stem
        }


def source_counts_by_frame(nodes: dict[int, dict], edges: list[tuple]) -> dict[int, int]:
    successors: dict[int, list[int]] = defaultdict(list)
    for source, target, _ in edges:
        successors[int(source)].append(int(target))
    counts: dict[int, int] = defaultdict(int)
    for source, targets in successors.items():
        if len(targets) != 1 or source not in nodes or targets[0] not in nodes:
            continue
        time = int(nodes[source]["t"])
        if int(nodes[targets[0]]["t"]) == time + 1:
            counts[time] += 1
    return counts


def apply_public_caps(
    nodes: dict[int, dict],
    edges: list[tuple[int, int, float | None]],
    candidates: list[tuple],
    scores: np.ndarray,
    predecessors: dict[int, list[int]],
    min_score: float,
) -> tuple[list[tuple[int, int, float | None]], int]:
    """Apply the shipped global/frame caps and DeepCenter veto in score order."""
    frame_sources = source_counts_by_frame(nodes, edges)
    result = list(edges)
    used_sources: set[int] = set()
    used_targets: set[int] = set()
    per_frame: dict[int, int] = defaultdict(int)
    added = 0
    global_cap = max(1, int(round(len(edges) * p2.GLOBAL_CAP)))
    order = sorted(
        range(len(candidates)),
        key=lambda index: (-float(scores[index]), int(candidates[index][0]), int(candidates[index][2])),
    )
    dc_index = p2.NAMES.index("dc_q")
    for index in order:
        score = float(scores[index])
        if not np.isfinite(score) or score < min_score:
            continue
        parent, _, candidate, time, features = candidates[index]
        parent, candidate, time = int(parent), int(candidate), int(time)
        if added >= global_cap:
            break
        frame_cap = max(1, int(round(frame_sources.get(time, 1) * p2.FRAME_CAP)))
        if per_frame[time] >= frame_cap:
            continue
        if parent in used_sources or candidate in used_targets:
            continue
        if predecessors.get(candidate):
            continue
        if float(features[dc_index]) < p2.DC_THR:
            continue
        result.append((parent, candidate, None))
        used_sources.add(parent)
        used_targets.add(candidate)
        per_frame[time] += 1
        added += 1
    return result, added


def proposal_scores(
    candidates: list[tuple],
    parent_scores: dict[int, float],
    ranker: str,
    sister_min_um: float,
) -> tuple[np.ndarray, dict[str, int]]:
    eligible: list[int] = []
    for index, (*_, features) in enumerate(candidates):
        if float(features[2]) < sister_min_um:
            continue
        if p2.public_key(features) is None:
            continue
        eligible.append(index)

    scores = np.full(len(candidates), -np.inf, dtype=np.float64)
    missing_parents: set[int] = set()
    if ranker == "geometry":
        for index in eligible:
            key = p2.public_key(candidates[index][4])
            assert key is not None
            scores[index] = -float(key)
        selected = len(eligible)
    elif ranker == "divnet":
        by_parent: dict[int, list[int]] = defaultdict(list)
        for index in eligible:
            by_parent[int(candidates[index][0])].append(index)
        selected = 0
        for parent, indices in by_parent.items():
            if parent not in parent_scores:
                missing_parents.add(parent)
                continue
            # DivNet scores the parent event.  Resolve its daughter ambiguity
            # exactly as requested: choose the largest sister separation.
            best = max(
                indices,
                key=lambda index: (
                    float(candidates[index][4][2]),
                    -float(candidates[index][4][1]),
                    -int(candidates[index][2]),
                ),
            )
            scores[best] = float(parent_scores[parent])
            selected += 1
    else:
        selected = 0
        for index in eligible:
            parent = int(candidates[index][0])
            if parent not in parent_scores:
                missing_parents.add(parent)
                continue
            key = p2.public_key(candidates[index][4])
            assert key is not None
            geometry_affinity = 1.0 / (1.0 + float(key))
            scores[index] = float(parent_scores[parent]) * geometry_affinity
            selected += 1
    return scores, {
        "candidates": len(candidates),
        "eligible": len(eligible),
        "selected": selected,
        "missing_scored_parents": len(missing_parents),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="friend_a_b20_exp29")
    parser.add_argument("--stems", nargs="*", default=[])
    parser.add_argument("--ranker", choices=["geometry", "divnet", "hybrid"], required=True)
    parser.add_argument("--scores-file", default="")
    parser.add_argument("--parent-um", type=float, default=12.0)
    parser.add_argument("--sister-min-um", type=float, default=5.0)
    parser.add_argument("--min-score", type=float, default=-1.0)
    parser.add_argument("--label", required=True)
    parser.add_argument("--data-dir", default=str(pl.DEFAULT_DATA))
    parser.add_argument("--cache-dir", default=str(pl.DEFAULT_CACHE))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    cache = Path(args.cache_dir) / args.tag
    stems = args.stems or sorted(path.stem for path in (cache / "ckpt").glob("*.npz"))
    if not stems:
        raise RuntimeError(f"No pass-1 checkpoints in {cache / 'ckpt'}")
    score_source = Path(args.scores_file) if args.scores_file else cache / "divnet"
    if args.ranker in {"divnet", "hybrid"} and not score_source.exists():
        raise FileNotFoundError(score_source)

    output_dir = cache / "pp" / args.label
    output_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "tag": args.tag,
        "ranker": args.ranker,
        "candidate_mode": "public_orphans_no_steal",
        "parent_um": args.parent_um,
        "sister_min_um": args.sister_min_um,
        "sister_max_um": p2.SISTER_MAX,
        "min_score": args.min_score,
        "within_parent": {
            "geometry": "public_geometry",
            "divnet": "largest_sister_separation",
            "hybrid": "divnet_probability_times_inverse_public_geometry_cost",
        }[args.ranker],
        "scores_file": str(score_source.resolve()) if args.ranker in {"divnet", "hybrid"} else None,
    }
    config_path = cache / "pp" / f"{args.label}.config.json"
    if config_path.is_file() and json.loads(config_path.read_text(encoding="utf-8")) != config:
        raise RuntimeError(f"Configuration changed for existing label {args.label}; choose another label")
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    os.environ["BIOHUB_OUTPUT_SAFE_DIVISIONS"] = "0"
    os.environ["BIOHUB_OUTPUT_MOTION_RELINK"] = "0"
    os.environ["BIOHUB_OUTPUT_GAP_CLOSE"] = "0"
    os.environ["BIOHUB_OUTPUT_GAP2_RECOVERY"] = "0"
    os.environ["BIOHUB_USE_DEEPCENTER_VETO"] = "0"
    os.environ["BIOHUB_REQUIRE_DEEPCENTER_VETO"] = "0"
    cells = pl.notebook_cells(pl.DEFAULT_NOTEBOOK)
    work = cache / "work"
    work.mkdir(exist_ok=True)
    repo, _ = pl.materialise_repo(Path(pl.DEFAULT_WEIGHTS_ROOT), work, None, None, materialise_code=False)
    namespace = pl.build_namespace(cells, repo, work, Path(args.data_dir))
    pl.load_postproc(cells, namespace)
    filter_output_graph = namespace["filter_output_graph"]

    import networkx as nx
    import postproc

    rows: list[dict[str, object]] = []
    for video_index, stem in enumerate(stems, start=1):
        output = output_dir / f"{stem}.geff"
        if args.resume and output.is_dir():
            rows.append({"dataset": stem, "status": "resumed"})
            print(f"[{video_index}/{len(stems)}] {stem}: output present, skipped", flush=True)
            continue
        nodes, edges, dcs, peak = p2.load_video(cache, stem)
        candidates, _, predecessors = p2.candidates(
            nodes, edges, dcs, peak, args.parent_um, 0, "add"
        )
        parent_scores = (
            load_parent_scores(score_source, stem)
            if args.ranker in {"divnet", "hybrid"}
            else {}
        )
        scores, counts = proposal_scores(
            candidates, parent_scores, args.ranker, args.sister_min_um
        )
        threshold = -np.inf if args.ranker == "geometry" else args.min_score
        new_edges, added = apply_public_caps(
            nodes, edges, candidates, scores, predecessors, threshold
        )

        node_records = {
            node_id: {
                "node_id": node_id,
                "t": node["t"],
                "z": node["z"],
                "y": node["y"],
                "x": node["x"],
                **({"gap_synthetic": 1} if node["syn"] else {}),
            }
            for node_id, node in nodes.items()
        }
        edge_records = [
            {"source_id": source, "target_id": target, "edge_prob": probability}
            for source, target, probability in new_edges
        ]
        node_records, edge_records, _ = filter_output_graph(
            node_records, edge_records, dataset=stem, deepcenter_bundle=None
        )
        graph = nx.DiGraph()
        for node_id, node in node_records.items():
            graph.add_node(
                int(node_id),
                t=int(node["t"]),
                z=float(max(0, round(node["z"]))),
                y=float(max(0, round(node["y"]))),
                x=float(max(0, round(node["x"]))),
            )
        for edge in edge_records:
            graph.add_edge(int(edge["source_id"]), int(edge["target_id"]))
        postproc.save(graph, output)
        row = {"dataset": stem, "status": "written", **counts, "added": int(added)}
        rows.append(row)
        print(
            f"[{video_index}/{len(stems)}] {stem}: eligible={counts['eligible']} "
            f"selected={counts['selected']} added={added}",
            flush=True,
        )
        if stop_requested():
            raise SystemExit(75)

    missing = [stem for stem in stems if not (output_dir / f"{stem}.geff").is_dir()]
    if missing:
        raise RuntimeError(f"Pass 2 incomplete; missing {len(missing)} outputs: {missing[:5]}")
    summary, metric_rows = pl.score_dir(output_dir, Path(args.data_dir))
    result = {
        **config,
        "label": args.label,
        "videos": stems,
        "summary": summary,
        "metric_rows": metric_rows,
        "progress": rows,
    }
    result_path = cache / "pp" / f"{args.label}.json"
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        f"== {args.label} score={summary['score']:.6f} "
        f"adj_edge={summary['adj_edge_jaccard']:.6f} div={summary['division_jaccard']:.6f} "
        f"({int(summary['division_tp'])}/{int(summary['division_fp'])}/{int(summary['division_fn'])})",
        flush=True,
    )


if __name__ == "__main__":
    main()
