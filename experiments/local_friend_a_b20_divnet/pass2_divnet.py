"""Streaming/resumable B20 pass 2 for public control or DivNet scores."""

from __future__ import annotations

import argparse
import json
import os
import sys
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


def load_parent_scores(path: Path, key: str, stem: str) -> dict[int, float]:
    source = path / f"{stem}.npz" if path.is_dir() else path
    with np.load(source, allow_pickle=False) as payload:
        values = payload[key]
        if path.is_dir():
            return {int(parent): float(value) for parent, value in zip(payload["p"], values)}
        if "stem" not in payload.files:
            return {int(parent): float(value) for parent, value in zip(payload["p"], values)}
        return {
            int(parent): float(value)
            for item_stem, parent, value in zip(payload["stem"], payload["p"], values)
            if str(item_stem) == stem
        }


def retain_top_k(candidates: list[tuple], scores: np.ndarray, top_k: int) -> np.ndarray:
    if top_k <= 0:
        return scores
    by_parent: dict[int, list[int]] = {}
    for index, row in enumerate(candidates):
        by_parent.setdefault(int(row[0]), []).append(index)
    keep: set[int] = set()
    for indices in by_parent.values():
        ordered = sorted(
            indices,
            key=lambda index: (
                -float(scores[index]),
                float(candidates[index][4][0]) + 0.15 * float(candidates[index][4][2]),
            ),
        )
        keep.update(ordered[:top_k])
    return np.array([value if index in keep else -np.inf for index, value in enumerate(scores)])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="friend_a_b20_exp29")
    parser.add_argument("--stems", nargs="*", default=[])
    parser.add_argument("--ranker", choices=["public", "divnet"], required=True)
    parser.add_argument("--scores-file", default="")
    parser.add_argument("--scores-key", default="score")
    parser.add_argument("--mode", choices=["add", "steal"], default="steal")
    parser.add_argument("--parent-um", type=float, default=15.0)
    parser.add_argument("--candidate-k", type=int, default=64)
    parser.add_argument("--score-top-k", type=int, default=1)
    parser.add_argument("--min-score", type=float, default=0.5)
    parser.add_argument("--label", required=True)
    parser.add_argument("--data-dir", default=str(pl.DEFAULT_DATA))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    cache = pl.DEFAULT_CACHE / args.tag
    stems = args.stems or sorted(path.stem for path in (cache / "ckpt").glob("*.npz"))
    output_dir = cache / "pp" / args.label
    output_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "tag": args.tag,
        "ranker": args.ranker,
        "mode": args.mode,
        "parent_um": args.parent_um,
        "candidate_k": args.candidate_k,
        "score_top_k": args.score_top_k,
        "min_score": args.min_score,
        "scores_file": str(Path(args.scores_file).resolve()) if args.scores_file else None,
    }
    config_path = cache / "pp" / f"{args.label}.config.json"
    if config_path.is_file() and json.loads(config_path.read_text(encoding="utf-8")) != config:
        raise RuntimeError(f"Configuration changed for existing label {args.label}; choose a new label")
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    score_source = None
    if args.ranker == "divnet":
        if not args.scores_file:
            raise ValueError("--scores-file is required for --ranker divnet")
        score_source = Path(args.scores_file)
        if not score_source.exists():
            raise FileNotFoundError(score_source)

    os.environ["BIOHUB_OUTPUT_SAFE_DIVISIONS"] = "0"
    os.environ["BIOHUB_OUTPUT_MOTION_RELINK"] = "0"
    os.environ["BIOHUB_OUTPUT_GAP_CLOSE"] = "0"
    os.environ["BIOHUB_OUTPUT_GAP2_RECOVERY"] = "0"
    os.environ["BIOHUB_USE_DEEPCENTER_VETO"] = "0"
    os.environ["BIOHUB_REQUIRE_DEEPCENTER_VETO"] = "0"
    cells = pl.notebook_cells(pl.DEFAULT_NOTEBOOK)
    work = cache / "work"
    work.mkdir(exist_ok=True)
    namespace = pl.build_cached_postproc_namespace(cells, work, Path(args.data_dir))
    filter_output_graph = namespace["filter_output_graph"]

    import networkx as nx
    import postproc

    rows: list[dict[str, object]] = []
    for index, stem in enumerate(stems, start=1):
        output = output_dir / f"{stem}.geff"
        if args.resume and output.is_dir():
            print(f"[{index}/{len(stems)}] {stem}: output present, skipped", flush=True)
            rows.append({"dataset": stem, "status": "resumed"})
            continue
        nodes, edges, dcs, peak = p2.load_video(cache, stem)
        candidates, successors, predecessors = p2.candidates(
            nodes, edges, dcs, peak, args.parent_um, args.candidate_k, args.mode
        )
        if args.ranker == "public":
            scores = np.array(
                [
                    (-key if (key := p2.public_key(features)) is not None else -np.inf)
                    for *_, features in candidates
                ],
                dtype=float,
            )
            threshold = -np.inf
        else:
            parent_scores = load_parent_scores(score_source, args.scores_key, stem)
            scores = np.array(
                [
                    parent_scores.get(int(parent), -np.inf)
                    for parent, child, candidate, _, _ in candidates
                ],
                dtype=float,
            )
            scores = retain_top_k(candidates, scores, args.score_top_k)
            threshold = args.min_score
        new_edges, added = p2.apply(
            nodes,
            edges,
            candidates,
            scores,
            successors,
            predecessors,
            args.mode,
            min_score=threshold,
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
        rows.append(
            {
                "dataset": stem,
                "status": "written",
                "candidates": len(candidates),
                "finite_scores": int(np.isfinite(scores).sum()),
                "added": int(added),
            }
        )
        print(
            f"[{index}/{len(stems)}] {stem}: {len(candidates)} candidates, "
            f"{int(np.isfinite(scores).sum())} retained, {added} divisions added",
            flush=True,
        )
        if stop_requested():
            raise SystemExit(75)

    missing = [stem for stem in stems if not (output_dir / f"{stem}.geff").is_dir()]
    if missing:
        raise RuntimeError(f"Pass 2 is incomplete; missing {len(missing)} outputs: {missing[:5]}")
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
        f"== {args.tag}/{args.label} score={summary['score']:.4f} "
        f"adj_edge={summary['adj_edge_jaccard']:.4f} div={summary['division_jaccard']:.4f} "
        f"({int(summary['division_tp'])}/{int(summary['division_fp'])}/{int(summary['division_fn'])}) "
        f"n={len(stems)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
