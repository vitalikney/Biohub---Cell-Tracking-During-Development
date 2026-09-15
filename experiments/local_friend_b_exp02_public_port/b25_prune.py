"""B25 - learned peak pruning as the node-budget lever, on the local port.

WHAT THE METRIC ACTUALLY REWARDS (CONTEXT_FRIEND_B.md §19)
    adj = J * (1 - 0.1 * (N_pred - N_est) / N_est)
Edges between nodes that match no ground-truth node are invisible to J, so removing such nodes moves only the
node-count factor: dropping a fraction X of unmatched nodes is worth about 0.1 * X * N_pred/N_est
(+0.008 at 10%, +0.010 at 13% on the LOEO videos). Removing a MATCHED node costs edges - the NMS sweep showed
blind pruning of 7.9% of nodes at 97.6% recall loses 0.026. So the whole task is selectivity, and the
go/no-go is two numbers: recall on annotated nodes >= 99.0% AND a higher official adj_edge on CLEAN videos.

LABELS ARE POSITIVE-VS-UNKNOWN
    Ground truth covers 0.5-1.7% of predicted nodes. A node within 7 um (the metric's match radius) of a GT node
    is a positive; everything else is unknown, mostly real but unannotated nuclei. The model therefore learns
    "does this detection look like the annotated ones", which is exactly what the metric pays for.

FEATURES (all from the RAW ILP graph with `peak_prob`, no re-inference needed)
    peak_prob               detector confidence at the peak (saturated: min 0.965, median 0.999 - weak alone)
    d_stronger_um           distance to the nearest peak in the same frame with a higher peak_prob (duplicates sit
                            close to a stronger peak)
    d_nn_um, n_within_8um   local crowding in the same frame
    in_deg, out_deg         raw ILP linking (isolated / track-end nodes are the short-track filter's prey)
    comp_len                length of the weakly connected component in the raw graph
    z_um                    depth (light-sheet attenuation makes deep detections less trustworthy)

PROTOCOL
    leave-one-video-out logistic regression; per video, drop the lowest-scored X% of nodes from the RAW graph
    (before post-processing, so motion relink / gap closing can heal around removals) and write a pruned raw
    graph set per X. Then the normal CPU post-processing stage scores each set with the official metric:

        python b25_prune.py --tag exp29pp_4vid --fractions 0.05 0.10 0.13 0.20
        for X in 05 10 13 20; do
            python tools/public_local.py --tag exp29pp_4vid_prune$X --stage pp --stems ...
        done

    Recall on annotated nodes after pruning is printed here (the expensive official recall comes from the pp run).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE = ROOT / ".public_local_cache"
DATA = ROOT / "biohub-cell-tracking-during-development" / "train"
VOXEL = np.array([1.625, 0.40625, 0.40625])
MATCH_UM = 7.0
LEAKY_FOR_FT = {"44b6_12dfb391", "44b6_2a2eff9f", "44b6_a21120c2",
                "44b6_c50204e0", "44b6_d2f34f90", "44b6_d5e7d891"}

sys.path.insert(0, str(ROOT / "tools" / "official" / "src"))
sys.path.insert(0, str(ROOT / "tools"))


def load_raw(path: Path):
    import tracksdata as td
    g = td.graph.IndexedRXGraph.from_geff(path)
    g = g[0] if isinstance(g, tuple) else g
    n = g.node_attrs().sort("node_id")
    e = g.edge_attrs()
    return g, n, e


def gt_nodes(stem: str) -> np.ndarray:
    from tracking_cellmot.io import open_dataset
    ds = open_dataset(DATA / stem, require_tracks=True, load_image=False)
    a = ds.tracks.node_attrs()
    return np.stack([a["t"].to_numpy(), a["z"].to_numpy(), a["y"].to_numpy(), a["x"].to_numpy()], 1).astype(float)


def features_and_labels(stem: str, raw_dir: Path, image_features: bool = False):
    from scipy.spatial import cKDTree
    import networkx as nx

    g, n, e = load_raw(raw_dir / f"{stem}.geff")
    if "peak_prob" not in n.columns:
        raise SystemExit(f"{stem}: raw graph has no peak_prob - re-run inference with --keep-peak-prob")
    ids = n["node_id"].to_numpy()
    t = n["t"].to_numpy().astype(int)
    pos_um = np.stack([n["z"].to_numpy(), n["y"].to_numpy(), n["x"].to_numpy()], 1) * VOXEL
    prob = n["peak_prob"].to_numpy()

    # degrees and component length from the raw ILP graph
    src, dst = e["source_id"].to_numpy(), e["target_id"].to_numpy()
    idx = {int(i): k for k, i in enumerate(ids)}
    in_deg = np.zeros(len(ids)); out_deg = np.zeros(len(ids))
    for s_, d_ in zip(src, dst):
        out_deg[idx[int(s_)]] += 1; in_deg[idx[int(d_)]] += 1
    G = nx.Graph(); G.add_nodes_from(range(len(ids))); G.add_edges_from((idx[int(s_)], idx[int(d_)]) for s_, d_ in zip(src, dst))
    comp_len = np.zeros(len(ids))
    for comp in nx.connected_components(G):
        for k in comp:
            comp_len[k] = len(comp)

    # per-frame geometry
    d_nn = np.full(len(ids), 50.0); d_stronger = np.full(len(ids), 50.0); n8 = np.zeros(len(ids))
    gt = gt_nodes(stem)
    label = np.zeros(len(ids), dtype=bool)
    for frame in np.unique(t):
        m = np.where(t == frame)[0]
        if len(m) == 0:
            continue
        tree = cKDTree(pos_um[m])
        dd, ii = tree.query(pos_um[m], k=min(2, len(m)))
        if len(m) > 1:
            d_nn[m] = dd[:, 1]
        n8[m] = np.array([len(c) - 1 for c in tree.query_ball_point(pos_um[m], 8.0)])
        # nearest STRONGER peak: query several neighbours, take the first with higher prob
        k = min(12, len(m))
        dd, ii = tree.query(pos_um[m], k=k)
        dd = np.atleast_2d(dd); ii = np.atleast_2d(ii)
        for r in range(len(m)):
            for c in range(1, k):
                j = m[ii[r, c]]
                if prob[j] > prob[m[r]]:
                    d_stronger[m[r]] = dd[r, c]; break
        gm = gt[gt[:, 0] == frame]
        if len(gm):
            gtree = cKDTree(gm[:, 1:] * VOXEL)
            dg, _ = gtree.query(pos_um[m])
            label[m] = dg <= MATCH_UM

    cols = [prob, np.log1p(d_stronger), np.log1p(d_nn), n8, in_deg, out_deg, np.log1p(comp_len), pos_um[:, 0]]
    names = ["peak_prob", "log_d_stronger", "log_d_nn", "n_within_8um", "in_deg", "out_deg", "log_comp_len", "z_um"]
    if image_features:
        # size-not-brightness features from b25_image_features.py (zhincez): half-max volume relative to the
        # same-frame control, its temporal profile, and the peak above local background
        f = np.load(Path(__file__).resolve().parent / "results" / "imgfeat" / f"{stem}.npz")
        if not np.array_equal(f["node_id"].astype(int), ids.astype(int)):
            raise SystemExit(f"{stem}: image-feature cache does not match the graph's node ids; re-run b25_image_features.py")
        vol = f["vol_halfmax"]; vrel = f["vol_rel"]
        cols += [np.log1p(vol), np.log(np.clip(vrel, 1e-3, None)),
                 np.log1p(f["vol_prev"]) - np.log1p(vol), np.log1p(f["vol_next"]) - np.log1p(vol),
                 np.log1p(f["peak"])]
        names += ["log_vol_halfmax", "log_vol_rel_frame", "dlog_vol_prev", "dlog_vol_next", "log_peak_above_bg"]
    X = np.stack(cols, 1)
    return ids, X, label, names


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="cache tag whose raw/ graphs carry peak_prob")
    ap.add_argument("--fractions", type=float, nargs="+", default=[0.05, 0.10, 0.13, 0.20])
    ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--image-features", action="store_true",
                    help="add the size-not-brightness image features cached by b25_image_features.py")
    ap.add_argument("--suffix", default="", help="suffix for the pruned-set tags, e.g. _img")
    args = ap.parse_args()

    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline

    raw_dir = CACHE / args.tag / "raw"
    stems = args.stems or sorted(p.stem for p in raw_dir.glob("*.geff"))
    data = {s: features_and_labels(s, raw_dir, args.image_features) for s in stems}
    names = data[stems[0]][3]
    print(f"{len(stems)} videos | features: {names}")
    for s in stems:
        ids, X, y, _ = data[s]
        print(f"  {s}: {len(ids)} nodes, {int(y.sum())} positives ({100 * y.mean():.2f}%)"
              + ("  [LEAKY for exp03B]" if s in LEAKY_FOR_FT else ""))

    # leave-one-video-out scores
    scores = {}
    coefs = []
    for held in stems:
        Xtr = np.concatenate([data[s][1] for s in stems if s != held])
        ytr = np.concatenate([data[s][2] for s in stems if s != held])
        clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced"))
        clf.fit(Xtr, ytr)
        scores[held] = clf.predict_proba(data[held][1])[:, 1]
        coefs.append(clf[-1].coef_[0])
    coef = np.mean(coefs, 0)
    print("mean LOO coefficients (standardised):")
    for nme, c in sorted(zip(names, coef), key=lambda kv: -abs(kv[1])):
        print(f"  {nme:16s} {c:+.3f}")

    # prune and write
    summary = []
    for frac in args.fractions:
        out_tag = f"{args.tag}_prune{int(round(frac * 100)):02d}{args.suffix}"
        out_raw = CACHE / out_tag / "raw"
        if out_raw.exists():
            shutil.rmtree(out_raw)
        out_raw.mkdir(parents=True)
        tot_pos = tot_kept_pos = tot_n = tot_kept = 0
        for s in stems:
            ids, X, y, _ = data[s]
            sc = scores[s]
            n_drop = int(round(frac * len(ids)))
            drop = set(ids[np.argsort(sc)[:n_drop]].tolist())
            keep_mask = np.array([int(i) not in drop for i in ids])
            tot_pos += int(y.sum()); tot_kept_pos += int((y & keep_mask).sum())
            tot_n += len(ids); tot_kept += int(keep_mask.sum())
            write_pruned(raw_dir / f"{s}.geff", out_raw / f"{s}.geff", drop)
        rec = tot_kept_pos / max(tot_pos, 1)
        summary.append({"fraction": frac, "tag": out_tag, "nodes_before": tot_n, "nodes_after": tot_kept,
                        "annotated_recall_after_prune": rec})
        print(f"prune {frac:.0%}: {tot_n} -> {tot_kept} nodes | recall on annotated nodes {rec:.4f}"
              f"  -> {out_tag}/raw")
    (CACHE / args.tag / f"b25_prune_summary{args.suffix}.json").write_text(json.dumps(
        {"features": names, "mean_coef": coef.tolist(), "pruning": summary}, indent=2))
    print("next: run the pp stage on each pruned tag and compare official adj_edge with the unpruned base")


def write_pruned(src: Path, dst: Path, drop: set) -> None:
    import networkx as nx
    import postproc as pp_io
    g = pp_io.load(src)
    g.remove_nodes_from([n for n in g.nodes if int(n) in drop])
    pp_io.save(g, dst)


if __name__ == "__main__":
    os.environ.setdefault("BIOHUB_DATA_DIR", str(DATA))
    main()
