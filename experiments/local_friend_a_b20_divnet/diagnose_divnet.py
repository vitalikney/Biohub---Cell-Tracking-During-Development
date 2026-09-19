"""Diagnose cached DivNet parent probabilities against all 199 GT videos."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "experiments" / "local_friend_b_exp02_public_port"))

import pass2_rank_divisions as p2  # noqa: E402
import public_local as pl  # noqa: E402


def load_graph(path: Path):
    import tracksdata as td

    graph = td.graph.IndexedRXGraph.from_geff(path)
    return graph[0] if isinstance(graph, tuple) else graph


def gt_division_parents(path: Path) -> list[dict[str, float | int]]:
    graph = load_graph(path)
    attrs = {
        int(row["node_id"]): row
        for row in graph.node_attrs().iter_rows(named=True)
    }
    out_degree = Counter(
        int(row["source_id"])
        for row in graph.edge_attrs().iter_rows(named=True)
    )
    return [
        {
            "node_id": node_id,
            "t": int(attrs[node_id]["t"]),
            "z": float(attrs[node_id]["z"]),
            "y": float(attrs[node_id]["y"]),
            "x": float(attrs[node_id]["x"]),
        }
        for node_id, degree in out_degree.items()
        if degree >= 2 and node_id in attrs
    ]


def match_divisions(
    scored: list[dict[str, float | int]],
    divisions: list[dict[str, float | int]],
    radius_um: float,
) -> tuple[set[int], list[float]]:
    by_time_scored: dict[int, list[int]] = defaultdict(list)
    by_time_gt: dict[int, list[int]] = defaultdict(list)
    for index, row in enumerate(scored):
        by_time_scored[int(row["t"])].append(index)
    for index, row in enumerate(divisions):
        by_time_gt[int(row["t"])].append(index)

    positives: set[int] = set()
    distances: list[float] = []
    for time, gt_indices in by_time_gt.items():
        pred_indices = by_time_scored.get(time, [])
        if not pred_indices:
            continue
        pred_xyz = np.array(
            [[scored[i]["z"], scored[i]["y"], scored[i]["x"]] for i in pred_indices],
            dtype=np.float64,
        ) * p2.VOX
        gt_xyz = np.array(
            [[divisions[i]["z"], divisions[i]["y"], divisions[i]["x"]] for i in gt_indices],
            dtype=np.float64,
        ) * p2.VOX
        distance = np.linalg.norm(gt_xyz[:, None, :] - pred_xyz[None, :, :], axis=2)
        gt_rows, pred_cols = linear_sum_assignment(distance)
        for gt_row, pred_col in zip(gt_rows, pred_cols):
            value = float(distance[gt_row, pred_col])
            if value <= radius_um:
                positives.add(pred_indices[int(pred_col)])
                distances.append(value)
    return positives, distances


def quantiles(values: np.ndarray) -> dict[str, float]:
    return {
        str(q): float(np.quantile(values, q))
        for q in (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0)
    }


def write_histogram_svg(
    path: Path,
    bins: np.ndarray,
    positive_counts: np.ndarray,
    negative_counts: np.ndarray,
    *,
    auc: float,
) -> None:
    """Write a dependency-free density histogram beside the JSON report."""
    width, height = 900, 500
    left, right, top, bottom = 70, 25, 55, 60
    plot_width = width - left - right
    plot_height = height - top - bottom
    positive_density = positive_counts / max(1, int(positive_counts.sum()))
    negative_density = negative_counts / max(1, int(negative_counts.sum()))
    maximum = max(float(positive_density.max()), float(negative_density.max()), 1e-12)
    bar_width = plot_width / len(positive_counts)
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width / 2}" y="30" text-anchor="middle" font-family="sans-serif" font-size="20">DivNet parent diagnostic: AUC={auc:.4f}</text>',
        f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#222"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#222"/>',
    ]
    for index, (positive, negative) in enumerate(zip(positive_density, negative_density)):
        x = left + index * bar_width
        negative_height = float(negative) / maximum * plot_height
        positive_height = float(positive) / maximum * plot_height
        elements.append(
            f'<rect x="{x:.2f}" y="{top + plot_height - negative_height:.2f}" width="{bar_width:.2f}" height="{negative_height:.2f}" fill="#4c78a8" fill-opacity="0.55"/>'
        )
        elements.append(
            f'<rect x="{x + bar_width * 0.2:.2f}" y="{top + plot_height - positive_height:.2f}" width="{bar_width * 0.6:.2f}" height="{positive_height:.2f}" fill="#f58518" fill-opacity="0.75"/>'
        )
    for value in np.linspace(0.0, 1.0, 6):
        x = left + value * plot_width
        elements.extend(
            [
                f'<line x1="{x:.2f}" y1="{top + plot_height}" x2="{x:.2f}" y2="{top + plot_height + 5}" stroke="#222"/>',
                f'<text x="{x:.2f}" y="{top + plot_height + 23}" text-anchor="middle" font-family="sans-serif" font-size="13">{value:.1f}</text>',
            ]
        )
    elements.extend(
        [
            f'<text x="{left + plot_width / 2}" y="{height - 12}" text-anchor="middle" font-family="sans-serif" font-size="15">DivNet probability</text>',
            f'<rect x="{left + 12}" y="{top + 12}" width="18" height="12" fill="#4c78a8" fill-opacity="0.55"/>',
            f'<text x="{left + 37}" y="{top + 23}" font-family="sans-serif" font-size="13">other parents</text>',
            f'<rect x="{left + 145}" y="{top + 12}" width="18" height="12" fill="#f58518" fill-opacity="0.75"/>',
            f'<text x="{left + 170}" y="{top + 23}" font-family="sans-serif" font-size="13">GT division parents</text>',
            '</svg>',
        ]
    )
    path.write_text("\n".join(elements), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="friend_a_b20_exp29")
    parser.add_argument("--data-dir", default=str(pl.DEFAULT_DATA))
    parser.add_argument("--cache-dir", default=str(pl.DEFAULT_CACHE))
    parser.add_argument("--radius-um", type=float, default=7.0)
    parser.add_argument("--stems", nargs="*", default=[])
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    cache = Path(args.cache_dir) / args.tag
    score_dir = cache / "divnet"
    stems = args.stems or sorted(path.stem for path in score_dir.glob("*.npz"))
    if not stems:
        raise RuntimeError(f"No DivNet score files in {score_dir}")

    score_chunks: list[np.ndarray] = []
    label_chunks: list[np.ndarray] = []
    positive_ranks: list[int] = []
    per_video: list[dict[str, object]] = []
    total_gt = 0
    matched_gt = 0
    match_distances: list[float] = []

    for index, stem in enumerate(stems, start=1):
        nodes, _, _, _ = p2.load_video(cache, stem)
        with np.load(score_dir / f"{stem}.npz", allow_pickle=False) as payload:
            parents = np.asarray(payload["p"], dtype=np.int64)
            probabilities = np.asarray(payload["score"], dtype=np.float64)
        scored = [
            {
                "node_id": int(parent),
                "t": int(nodes[int(parent)]["t"]),
                "z": float(nodes[int(parent)]["z"]),
                "y": float(nodes[int(parent)]["y"]),
                "x": float(nodes[int(parent)]["x"]),
                "score": float(probability),
            }
            for parent, probability in zip(parents, probabilities)
            if int(parent) in nodes
        ]
        divisions = gt_division_parents(Path(args.data_dir) / f"{stem}.geff")
        positives, distances = match_divisions(scored, divisions, args.radius_um)
        labels = np.zeros(len(scored), dtype=np.int8)
        if positives:
            labels[np.fromiter(sorted(positives), dtype=np.int64)] = 1
        video_scores = np.asarray([float(row["score"]) for row in scored], dtype=np.float64)
        video_times = np.asarray([int(row["t"]) for row in scored], dtype=np.int16)
        score_chunks.append(video_scores)
        label_chunks.append(labels)
        for time in np.unique(video_times[labels == 1]):
            frame_mask = video_times == time
            frame_values = video_scores[frame_mask]
            positive_values = video_scores[frame_mask & (labels == 1)]
            positive_ranks.extend(
                1 + int(np.sum(frame_values > value))
                for value in positive_values
            )
        total_gt += len(divisions)
        matched_gt += len(positives)
        match_distances.extend(distances)
        per_video.append(
            {
                "dataset": stem,
                "scored_parents": len(scored),
                "gt_divisions": len(divisions),
                "matched_positive_parents": len(positives),
            }
        )
        if index % 20 == 0 or index == len(stems):
            n_scored = sum(len(chunk) for chunk in score_chunks)
            print(f"[{index}/{len(stems)}] parents={n_scored:,} matched={matched_gt}/{total_gt}", flush=True)

    scores = np.concatenate(score_chunks)
    labels = np.concatenate(label_chunks)
    if labels.sum() == 0 or labels.sum() == len(labels):
        raise RuntimeError("AUC requires both positive and negative scored parents")
    n_positive = int(labels.sum())
    n_negative = int(len(labels) - n_positive)
    ranks = rankdata(scores, method="average")
    auc = float(
        (float(ranks[labels == 1].sum()) - n_positive * (n_positive + 1) / 2)
        / (n_positive * n_negative)
    )

    hit_counts = {1: 0, 2: 0, 3: 0}
    for rank in positive_ranks:
        for k in hit_counts:
            hit_counts[k] += int(rank <= k)

    positive = scores[labels == 1]
    negative = scores[labels == 0]
    bins = np.linspace(0.0, 1.0, 21)
    positive_hist, _ = np.histogram(positive, bins=bins)
    negative_hist, _ = np.histogram(negative, bins=bins)
    result = {
        "tag": args.tag,
        "videos": len(stems),
        "match_radius_um": args.radius_um,
        "scored_parents": int(len(scores)),
        "gt_divisions": int(total_gt),
        "matched_positive_parents": int(labels.sum()),
        "gt_coverage": float(labels.sum() / total_gt) if total_gt else 0.0,
        "auc": auc,
        "hits_at_k": {
            str(k): float(value / len(positive_ranks)) if positive_ranks else 0.0
            for k, value in hit_counts.items()
        },
        "hits_definition": "rank among scored parents in the same dataset/frame; ties use the best rank",
        "positive_score_quantiles": quantiles(positive),
        "negative_score_quantiles": quantiles(negative),
        "match_distance_um_quantiles": quantiles(np.asarray(match_distances, dtype=np.float64)),
        "histogram": {
            "bin_edges": bins.tolist(),
            "positive_counts": positive_hist.tolist(),
            "negative_counts": negative_hist.tolist(),
        },
        "per_video": per_video,
    }
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_histogram_svg(
        output.with_suffix(".svg"),
        bins,
        positive_hist,
        negative_hist,
        auc=auc,
    )

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        figure, axis = plt.subplots(figsize=(8, 4.5))
        axis.hist(negative, bins=bins, density=True, alpha=0.55, label=f"other parents (n={len(negative):,})")
        axis.hist(positive, bins=bins, density=True, alpha=0.70, label=f"GT division parents (n={len(positive)})")
        axis.set_xlabel("DivNet probability")
        axis.set_ylabel("density")
        axis.set_title(f"DivNet parent diagnostic: AUC={auc:.4f}")
        axis.legend()
        figure.tight_layout()
        figure.savefig(output.with_suffix(".png"), dpi=160)
        plt.close(figure)
    except ImportError:
        pass

    print(json.dumps({key: result[key] for key in ("videos", "scored_parents", "gt_divisions", "matched_positive_parents", "auc", "hits_at_k")}, indent=2))


if __name__ == "__main__":
    main()
