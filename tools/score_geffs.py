"""Score prediction .geff graphs with the OFFICIAL competition metric (default scorer).

Uses `tools/official/` - a verbatim copy of the organisers' package
`tracking_cellmot` from github.com/royerlab/kaggle-cell-tracking-competition
(linked from the competition's Evaluation page).

Why this exists: `tools/repo/` is pilkwang's support-pack fork, whose
`division_metrics.py` still credits a GT division to ANY predicted fork
reachable in the same weakly connected component. The official metric
(metrics.md, "Merely sharing a weakly connected component is not sufficient")
requires a local parent anchor and two distinct daughter branches, so the fork
reports a higher division Jaccard than the leaderboard does. Edge-side code
(io.py, img_proc.py) is byte-identical between the two; only the metric differs.

Usage:
    python tools/score_geffs_official.py <geff_dir_or_files...> [--out out.json]
"""
import argparse
import json
import os
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OFFICIAL = ROOT / "official"
sys.path.insert(0, str(OFFICIAL / "src"))
sys.path.insert(0, str(OFFICIAL / "scripts"))
PROJECT_ROOT = ROOT.parent
DATA = Path(
    os.environ.get(
        "BIOHUB_DATA_DIR",
        PROJECT_ROOT / "biohub-cell-tracking-during-development" / "train",
    )
)
os.environ["BIOHUB_DATA_DIR"] = str(DATA)
warnings.filterwarnings("ignore")

import tracksdata as td
from geff import GeffMetadata

from tracking_cellmot.io import open_dataset
from tracking_cellmot.metrics import (
    evaluate as compute_metric,
    node_recall,
    per_sample_metrics,
    summarise,
)


def _estimated_n_total(geff_path: Path) -> float:
    try:
        meta = GeffMetadata.read(geff_path)
    except Exception:
        return float("nan")
    val = (meta.extra or {}).get("estimated_number_of_nodes")
    return float(val) if val is not None else float("nan")


def score(geffs, quiet=False):
    rows = []
    for g in geffs:
        name = g.stem
        ds = open_dataset(DATA / name, require_tracks=True, load_image=False)
        pr = td.graph.IndexedRXGraph.from_geff(g)
        pred = pr[0] if isinstance(pr, tuple) else pr
        er = compute_metric(pred, ds.tracks, scale=ds.scale)
        rec = node_recall(pred, ds.tracks) if pred.num_edges() > 0 and pred.num_nodes() > 0 else 0.0
        row = {"dataset": name, **per_sample_metrics(er, _estimated_n_total(DATA / (name + ".geff")), rec)}
        rows.append(row)
        if not quiet:
            print(
                "%-16s adj=%.4f edge=%.4f tp/fp/fn=%d/%d/%d ratio=%+.3f recall=%.3f div=%d/%d/%d"
                % (
                    name,
                    row["adj_edge_jaccard"],
                    row["edge_jaccard"],
                    row["edge_tp"],
                    row["edge_fp"],
                    row["edge_fn"],
                    row["total_node_ratio"],
                    row["node_recall"],
                    row["division_tp"],
                    row["division_fp"],
                    row["division_fn"],
                ),
                flush=True,
            )
    s = summarise(rows)
    return {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in s.items()}, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    geffs = []
    for p in a.paths:
        path = Path(p)
        # A .geff store is itself a directory, so check the suffix before globbing.
        if path.suffix == ".geff":
            geffs.append(path)
        elif path.is_dir():
            geffs.extend(sorted(path.glob("*.geff")))
        else:
            geffs.append(path)
    s, rows = score(geffs, quiet=a.quiet)
    print(
        "== OFFICIAL score=%.4f adj_edge=%.4f edge=%.4f div=%.4f (%d/%d/%d) node_recall=%.4f n=%d"
        % (
            s["score"],
            s["adj_edge_jaccard"],
            s["edge_jaccard"],
            s["division_jaccard"],
            s["division_tp"],
            s["division_fp"],
            s["division_fn"],
            s["node_recall"],
            len(rows),
        )
    )
    if a.out:
        Path(a.out).write_text(json.dumps({"summary": s, "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
