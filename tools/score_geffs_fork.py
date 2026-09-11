"""DEPRECATED: pilkwang fork metric (over-credits divisions). Use tools/score_geffs_official.py.

Kept only to quantify the difference against the official metric; do NOT use it to
rank configurations - its division TP rule is the pre-2026-07-17 weakly-connected-
component rule that the organisers patched out.
"""
"""Score prediction .geff graphs against local GT with the official repo metric (CPU, no image loading).
Usage: python tools/score_geffs.py <geff_dir_or_files...> [--out out.json]
"""
import argparse, json, os, sys, warnings
from pathlib import Path
ROOT = Path(__file__).resolve().parent / "repo"
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "scripts"))
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA = Path(
    os.environ.get(
        "BIOHUB_DATA_DIR",
        PROJECT_ROOT / "biohub-cell-tracking-during-development" / "train",
    )
)
os.environ["BIOHUB_DATA_DIR"] = str(DATA)
warnings.filterwarnings("ignore")
import tracksdata as td
from biohub_tracking.io import open_dataset
from biohub_tracking.metrics import evaluate as compute_metric, node_recall, per_sample_metrics, summarise
from evaluate import _read_estimated_n_total


def score(geffs, quiet=False):
    rows = []
    for g in geffs:
        name = g.stem
        ds = open_dataset(DATA / name, require_tracks=True, load_image=False)
        pr = td.graph.IndexedRXGraph.from_geff(g)
        pred = pr[0] if isinstance(pr, tuple) else pr
        er = compute_metric(pred, ds.tracks, scale=ds.scale)
        rec = node_recall(pred, ds.tracks) if pred.num_edges() > 0 and pred.num_nodes() > 0 else 0.0
        row = {"dataset": name, **per_sample_metrics(er, _read_estimated_n_total(DATA / f"{name}.geff"), rec)}
        rows.append(row)
        if not quiet:
            print(f"{name:16} adj={row['adj_edge_jaccard']:.4f} edge={row['edge_jaccard']:.4f} tp/fp/fn={row['edge_tp']}/{row['edge_fp']}/{row['edge_fn']} "
                  f"ratio={row['total_node_ratio']:+.3f} recall={row['node_recall']:.3f} div={row['division_tp']}/{row['division_fp']}/{row['division_fn']}", flush=True)
    s = summarise(rows)
    return {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in s.items()}, rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("paths", nargs="+"); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    geffs = []
    for p in a.paths:
        p = Path(p)
        geffs += sorted(p.glob("*.geff")) if p.is_dir() else [p]
    s, rows = score(geffs)
    print(f"== score={s['score']:.4f} adj_edge={s['adj_edge_jaccard']:.4f} edge={s['edge_jaccard']:.4f} div={s['division_jaccard']:.4f} "
          f"({int(s['division_tp'])}/{int(s['division_fp'])}/{int(s['division_fn'])}) node_recall={s['node_recall']:.4f} n={int(s['n'])}")
    if a.out:
        Path(a.out).write_text(json.dumps({"summary": s, "rows": rows}, indent=1, default=str))
