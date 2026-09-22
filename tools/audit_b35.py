"""B35 pre-training audit: actual parent-filter recall and official node matching.

Runs on B20 ckpt/divnet caches, without images, GPU or the raw GEFFs.
The direct-daughter and division-window numbers are diagnostics, NOT scores.
The window diagnostic is a necessary detection condition, not a guarantee of
valid directed topology, branch separation or simultaneous recoverability.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import warnings
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "official" / "src"))
FRACTIONS = (0.01, 0.03, 0.05, 0.10, 0.20, 0.50, 1.0)
VERSION = "b35-parent-audit-v1"


def json_default(item):
    if isinstance(item, np.generic):
        return item.item()
    if isinstance(item, Path):
        return str(item)
    raise TypeError(f"Object of type {type(item).__name__} is not JSON serializable")


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False, default=json_default), encoding="utf-8")
    temporary.replace(path)


def checkpoint_graph(path):
    import polars as pl
    import tracksdata as td
    graph = td.graph.IndexedRXGraph()
    # IndexedRXGraph keeps only registered attributes during bulk insertion.
    # ``t`` is built in; spatial coordinates and the synthetic-node marker are
    # not, so register them before loading the compact checkpoint arrays.
    for key in ("z", "y", "x"):
        graph.add_node_attr_key(key, pl.Float64, -999999.0)
    graph.add_node_attr_key("syn", pl.Int64, 0)
    with np.load(path, allow_pickle=False) as a:
        ids = a["node_id"].astype(np.int64).tolist()
        attrs = [dict(t=int(r[0]), z=float(r[1]), y=float(r[2]), x=float(r[3]),
                      syn=int(r[4])) for r in a["tzyx_syn"]]
        graph.bulk_add_nodes(attrs, indices=ids)
        for src, dst in zip(a["src"], a["dst"], strict=True):
            # tracksdata 0.6 requires the attrs argument even for an
            # attribute-free edge.  The previous two-argument form failed on
            # the pinned project environment before the first video ran.
            graph.add_edge(int(src), int(dst), {})
    return graph


def official_mapping(prediction, truth, scale):
    from tracking_cellmot import division_metrics as dm
    matched = dm._match_full(prediction, truth, tuple(scale), 7.0)
    pairs = dm._matched_node_attrs(matched)
    import tracksdata as td
    return dict(zip(pairs[td.DEFAULT_ATTR_KEYS.NODE_ID].to_list(),
                    pairs[td.DEFAULT_ATTR_KEYS.MATCHED_NODE_ID].to_list(), strict=True))


def ranked_parent_sets(eligible, probabilities):
    """Fixed top fractions of eligible parents per VIDEO; labels never enter."""
    scored = [p for p in eligible if np.isfinite(probabilities.get(p, np.nan))]
    ordered = sorted(scored, key=lambda p: (-probabilities[p], p))
    # Missing cached scores are not silently imputed as high/low confidence.
    return {f"{fraction:.2f}": set(ordered[:math.ceil(len(ordered) * fraction)])
            for fraction in FRACTIONS}


def audit_graph(prediction, truth, scale, probabilities):
    from tracking_cellmot import division_metrics as dm
    attrs = {int(row["node_id"]): row for row in prediction.node_attrs().iter_rows(named=True)}
    eligible = []
    for p in prediction.node_ids():
        children = prediction.successors(p)
        if len(children) == 1 and attrs[children[0]]["t"] == attrs[p]["t"] + 1:
            distance = np.linalg.norm(
                (np.array([attrs[p][k] for k in ("z", "y", "x")]) -
                 np.array([attrs[children[0]][k] for k in ("z", "y", "x")])) * scale)
            if distance <= 10:
                eligible.append(p)
    eligible = set(eligible)
    selected = ranked_parent_sets(eligible, probabilities)
    pred_to_gt = official_mapping(prediction, truth, scale)
    gt_to_pred = {gt: pred for pred, gt in pred_to_gt.items()}
    totals = Counter(nodes=prediction.num_nodes(), eligible_parents=len(eligible),
                     scored_eligible_parents=sum(p in probabilities and np.isfinite(probabilities[p]) for p in eligible))
    events = []
    for gt_parent, window in dm.extract_divisions(truth).items():
        children = truth.successors(gt_parent)
        totals["gt_divisions"] += 1
        p = gt_to_pred.get(gt_parent)
        daughters = [gt_to_pred.get(c) for c in children]
        direct = p is not None and sum(d is not None for d in daughters) >= 2
        totals["direct_parent_detected"] += int(p is not None)
        totals["direct_parent_and_daughters"] += int(direct)
        totals["direct_eligible_parent"] += int(p in eligible)
        # Official division evaluation rematches against each event window.
        # It permits parent/grandparent and child/grandchild evidence.
        window_map = official_mapping(prediction, window, scale)
        parent_gt = {gt_parent, *window.predecessors(gt_parent)}
        parent_ids = {node for node, match in window_map.items() if match in parent_gt}
        daughter_ids = [{node for node, match in window_map.items()
                         if match in {c, *window.successors(c)}} for c in children]
        node_window = bool(parent_ids) and sum(bool(ds) for ds in daughter_ids) >= 2
        local_parents = parent_ids | {s for node in parent_ids for s in prediction.successors(node)}
        local_eligible = local_parents & eligible
        totals["window_detection_necessary"] += int(node_window)
        totals["window_eligible_parent"] += int(bool(local_eligible))
        event = dict(gt_parent=int(gt_parent), direct_parent=p,
                     direct_detection=bool(direct), window_detection_necessary=node_window,
                     eligible_window_parents=sorted(local_eligible), parent_filters={})
        for fraction, parents in selected.items():
            hit = p in parents
            window_hit = bool(local_eligible & parents)
            totals[f"direct_parent_top_{fraction}"] += int(hit)
            totals[f"window_parent_top_{fraction}"] += int(window_hit)
            totals[f"window_detection_and_parent_top_{fraction}"] += int(node_window and window_hit)
            event["parent_filters"][fraction] = dict(direct=hit, window=window_hit)
        events.append(event)
    return dict(counts=dict(totals), selected_parents={f: len(v) for f, v in selected.items()}, events=events)


def fingerprint(paths):
    digest = hashlib.sha256(VERSION.encode())
    for path in paths:
        digest.update(str(path.resolve()).encode())
        if path.is_dir():
            files = sorted(p for p in path.rglob("*") if p.is_file())
        else:
            files = [path]
        for item in files:
            digest.update(str(item.relative_to(path) if path.is_dir() else item.name).encode())
            digest.update(item.read_bytes())
    return digest.hexdigest()


def audit_video(cache, data, stem, output):
    import tracksdata as td
    from geff import GeffMetadata
    ckpt, scores, gt_path = cache / "ckpt" / f"{stem}.npz", cache / "divnet" / f"{stem}.npz", data / f"{stem}.geff"
    sources = [ckpt, scores, gt_path, Path(__file__), ROOT / "tools/official/src/tracking_cellmot/division_metrics.py"]
    signature = fingerprint(sources)
    destination = output / "videos" / f"{stem}.json"
    if destination.is_file():
        previous = json.loads(destination.read_text(encoding="utf-8"))
        if previous.get("fingerprint") == signature:
            print(f"RESUME {stem}", flush=True)
            return previous
    with np.load(scores, allow_pickle=False) as a:
        probabilities = {int(p): float(s) for p, s in zip(a["p"], a["score"], strict=True)}
    prediction = checkpoint_graph(ckpt)
    truth = td.graph.IndexedRXGraph.from_geff(gt_path)
    truth = truth[0] if isinstance(truth, tuple) else truth
    axes = {a.name: a for a in GeffMetadata.read(gt_path).axes}
    scale = np.array([float(axes[k].scale) for k in ("z", "y", "x")])
    row = dict(dataset=stem, embryo=stem.split("_")[0], fingerprint=signature,
               **audit_graph(prediction, truth, scale, probabilities))
    atomic_json(destination, row)
    print(stem, json.dumps(row["counts"], default=json_default), flush=True)
    return row


def summarise(rows, output):
    report = dict(version=VERSION, videos=len(rows), groups={},
                  limitations=["These are detection/filter diagnostics, not leaderboard or official scores.",
                               "Window detection is necessary but not sufficient for a recoverable division.",
                               "Public detector and DivNet checkpoints have training overlap; this is not honest LOEO.",
                               "Parent fractions are fixed without GT; do not tune them on evaluation embryos."])
    for group in ("all", "44b6", "6bba"):
        subset = [r for r in rows if group == "all" or r["embryo"] == group]
        counts = Counter()
        for row in subset:
            counts.update(row["counts"])
        total = counts["gt_divisions"]
        report["groups"][group] = dict(videos=len(subset), counts=dict(counts),
            parent_recall={f: counts[f"direct_parent_top_{f}"] / total if total else None
                           for f in (f"{x:.2f}" for x in FRACTIONS)})
    atomic_json(output / "summary.json", report)
    lines = ["# B35 parent-filter and detection audit", "", f"Videos: {len(rows)}", "",
             "Diagnostic only; no achieved score or trained pair model is claimed.", "",
             "| group | GT divisions | direct detection | window necessary | top 3% direct parents | top 3% window parents |",
             "|---|---:|---:|---:|---:|---:|"]
    for group, row in report["groups"].items():
        c = Counter(row["counts"])
        lines.append(f"| {group} | {c['gt_divisions']} | {c['direct_parent_and_daughters']} | "
                     f"{c['window_detection_necessary']} | {c['direct_parent_top_0.03']} | {c['window_parent_top_0.03']} |")
    lines += ["", *report["limitations"]]
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stems", nargs="*")
    parser.add_argument("--expected-videos", type=int, default=199)
    args = parser.parse_args()
    stems = args.stems or sorted(p.stem for p in (args.cache / "ckpt").glob("*.npz"))
    if len(stems) != args.expected_videos:
        raise RuntimeError(f"Expected {args.expected_videos} videos, found {len(stems)}; use an explicit smoke count")
    for stem in stems:
        for source in (args.cache / "ckpt" / f"{stem}.npz", args.cache / "divnet" / f"{stem}.npz", args.data_dir / f"{stem}.geff"):
            if not source.exists():
                raise FileNotFoundError(source)
    rows = []
    for stem in stems:
        if (args.output / "STOP_REQUESTED").exists():
            raise SystemExit("Cooperative stop; per-video results are resumable")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rows.append(audit_video(args.cache, args.data_dir, stem, args.output))
        summarise(rows, args.output)


if __name__ == "__main__":
    main()
