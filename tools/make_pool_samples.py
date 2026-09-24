"""DaughterNet v2 training rows from the REAL candidate pool: exported candidate nodes labelled by GT matching.

Inputs
  --coords  experiments/l2_daughternet/coords_exp39.parquet   stem, node_id, t, z, y, x (float voxel coordinates of the
            PREDICTED nodes, post-linefit, exactly the node dicts the kernel hands to daughternet.score_nodes)
  --labels  data_external/l2/coords_labels.parquet           stem, node_id, t, role, dist_um, gt_id
            (tools/label_candidates.py: role of the nearest annotated GT node within 7 um in the same frame)
Output
  --out     experiments/l2_daughternet/pool_samples.parquet  (+ <out>.json sidecar with counts, inputs, v1 baseline)
            stem, node_id, t, z, y, x, label, dist_um, gt_id, n_triples, n_u, n_c1, n_v
            label = role; coordinates = the PREDICTED node (what the model sees at inference), never the GT node.

Rows kept: role parent / daughter (all of them) and cont (at most --cont-per-video per video). role none (unannotated
space, NEVER a negative: GT is sparse) and other (annotated, but neither a division node nor a clean continuation) are
dropped.

cont subsampling (deterministic): nodes that sit in many div_insert candidate triples are the ones the insertion scores
most often, so they are preferred: weighted sampling without replacement (Efraimidis-Spirakis, key = U^(1/w), top-k)
with w = n_triples, U from numpy default_rng([seed, crc32(stem)]) over the video's cont rows in node_id order.
n_triples / n_u / n_c1 / n_v come from re-running tools/div_insert.candidate_triples on the replay tail graphs the export
was made from (.public_local_cache/l2_replay/friend_a_b20_exp29/tail/<base_key>/<stem>.npz, ~1 s per video) with the
export's candidate_params; the node set and coordinates are checked against the coords file (any mismatch aborts).
Without the tail graphs (--tail-dir none, or not found) the counts are left empty and sampling is uniform (w = 1).

    python tools/make_pool_samples.py                                   # defaults below, 4 workers
    python tools/make_pool_samples.py --cont-per-video 80 --seed 0 --tail-dir none
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COORDS = ROOT / "experiments" / "l2_daughternet" / "coords_exp39.parquet"
DEFAULT_LABELS = ROOT / "data_external" / "l2" / "coords_labels.parquet"
DEFAULT_OUT = ROOT / "experiments" / "l2_daughternet" / "pool_samples.parquet"
DEFAULT_REPLAY = ROOT / ".public_local_cache" / "l2_replay" / "friend_a_b20_exp29" / "tail"
DEFAULT_V1_OOF = ROOT / "data_external" / "l2" / "kds_out" / "node_p_oof.parquet"
SPLITS = ROOT / "experiments" / "l2_daughternet" / "splits.json"
KEEP_ROLES = ("parent", "daughter", "cont")
OUT_COLUMNS = ["stem", "node_id", "t", "z", "y", "x", "label", "dist_um", "gt_id", "n_triples", "n_u", "n_c1", "n_v"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_tail(path: Path) -> tuple[dict, list[dict]]:
    """replay.py load_tail (same npz layout), nodes + edges only."""
    with np.load(path, allow_pickle=False) as z:
        ids, t, zyx, syn, gap2 = z["node_id"], z["t"], z["zyx"], z["syn"], z["gap2"]
        src, dst, prob, dist = z["src"], z["dst"], z["edge_prob"], z["distance_um"]
    nodes = {}
    for i, tt, (zz, yy, xx), s, g2 in zip(ids.tolist(), t.tolist(), zyx.tolist(), syn.tolist(), gap2.tolist()):
        node = {"node_id": i, "t": tt, "z": zz, "y": yy, "x": xx}
        if s:
            node["gap_synthetic"] = 1
        if g2:
            node["gap2_synthetic"] = 1
        nodes[i] = node
    edges = []
    for s, d, p, dd in zip(src.tolist(), dst.tolist(), prob.tolist(), dist.tolist()):
        edge = {"source_id": s, "target_id": d, "edge_prob": None if p != p else p}
        if dd == dd:
            edge["distance_um"] = dd
        edges.append(edge)
    return nodes, edges


def triple_counts(job: tuple) -> dict:
    """Per node of one video: number of candidate triples it takes part in, in total and as u / c1 / v."""
    stem, tail_path, params, node_ids, tzyx = job
    sys.path.insert(0, str(ROOT / "tools"))
    import div_insert

    nodes, edges = load_tail(Path(tail_path))
    triples = div_insert.candidate_triples(nodes, edges, params)
    involved = sorted({int(i) for tr in triples for i in tr})
    if involved != sorted(int(i) for i in node_ids):
        return {"stem": stem, "error": f"node set differs from the coords file ({len(involved)} vs {len(node_ids)})"}
    got = np.asarray([[nodes[i]["t"], nodes[i]["z"], nodes[i]["y"], nodes[i]["x"]] for i in node_ids], dtype=np.float64)
    if not np.array_equal(got.reshape(-1, 4), np.asarray(tzyx, dtype=np.float64).reshape(-1, 4)):
        return {"stem": stem, "error": "node coordinates differ from the coords file"}
    n_u, n_c1, n_v = {}, {}, {}
    for u, c1, v in triples:
        n_u[u] = n_u.get(u, 0) + 1
        n_c1[c1] = n_c1.get(c1, 0) + 1
        n_v[v] = n_v.get(v, 0) + 1
    ids = [int(i) for i in node_ids]
    return {"stem": stem, "error": None, "triples": len(triples), "node_id": np.asarray(ids, np.int64),
            "n_u": np.asarray([n_u.get(i, 0) for i in ids], np.int32),
            "n_c1": np.asarray([n_c1.get(i, 0) for i in ids], np.int32),
            "n_v": np.asarray([n_v.get(i, 0) for i in ids], np.int32)}


def weighted_pick(node_ids: np.ndarray, weights: np.ndarray, k: int, stem: str, seed: int) -> np.ndarray:
    """Efraimidis-Spirakis weighted sampling without replacement; deterministic per (seed, stem); returns positions."""
    order = np.argsort(node_ids, kind="stable")
    rng = np.random.default_rng([int(seed), zlib.crc32(stem.encode("utf-8"))])
    u = rng.random(len(order))
    w = np.maximum(np.asarray(weights, dtype=np.float64)[order], 1e-12)
    key = np.log(np.maximum(u, 1e-300)) / w          # log(U^(1/w)): larger = picked first
    top = np.lexsort((node_ids[order], -key))[:k]    # ties (never in practice) by node_id
    return np.sort(order[top])


def auc(scores, positive) -> float | None:
    s = np.asarray(scores, dtype=np.float64)
    y = np.asarray(positive, dtype=bool)
    n1, n0 = int(y.sum()), int((~y).sum())
    if n1 == 0 or n0 == 0:
        return None
    ranks = pd.Series(s).rank(method="average").to_numpy()
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def v1_baseline(frame: pd.DataFrame) -> dict:
    """AUCs of the v1 OOF p (kdn-score node_p_oof) on labelled pool rows: the number v2's pool block must beat."""
    out = {}
    groups = [(e, g) for e, g in frame.groupby(frame["stem"].str[:4])] + [("all", frame)]
    for emb, g in groups:
        par, dau, cont = g[g.label == "parent"], g[g.label == "daughter"], g[g.label == "cont"]
        out[emb] = {
            "n_parent": int(len(par)), "n_daughter": int(len(dau)), "n_cont": int(len(cont)),
            "auc_p_par_parent_vs_cont": auc(np.r_[par.p_par, cont.p_par], np.r_[np.ones(len(par)), np.zeros(len(cont))]),
            "auc_p_dau_daughter_vs_cont": auc(np.r_[dau.p_dau, cont.p_dau], np.r_[np.ones(len(dau)), np.zeros(len(cont))]),
            "auc_p_par_one_vs_rest": auc(g.p_par, g.label == "parent"),
            "auc_p_dau_one_vs_rest": auc(g.p_dau, g.label == "daughter"),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--coords", default=str(DEFAULT_COORDS))
    ap.add_argument("--labels", default=str(DEFAULT_LABELS))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--cont-per-video", type=int, default=80)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tail-dir", default="auto",
                    help="replay tail graphs of the export base; 'auto' = <replay>/tail/<base_key from coords json>, "
                         "'none' = uniform cont sampling")
    ap.add_argument("--v1-oof", default=str(DEFAULT_V1_OOF), help="v1 OOF node p (kdn-score) for the baseline block; "
                                                                  "'none' to skip")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    t0 = time.time()

    coords_path, labels_path, out_path = Path(a.coords), Path(a.labels), Path(a.out)
    co = pd.read_parquet(coords_path)
    lab = pd.read_parquet(labels_path)
    for name, df in (("coords", co), ("labels", lab)):
        dup = int(df.duplicated(["stem", "node_id"]).sum())
        if dup:
            raise SystemExit(f"{name}: {dup} duplicated (stem, node_id) rows")
    df = co.merge(lab, on=["stem", "node_id"], how="left", suffixes=("", "_lab"), validate="one_to_one")
    if df["role"].isna().any():
        raise SystemExit(f"{int(df['role'].isna().sum())} coords rows have no label row")
    if not (df["t"] == df["t_lab"]).all():
        raise SystemExit("t differs between coords and labels")
    if len(lab) != len(co):
        raise SystemExit(f"labels has {len(lab)} rows, coords {len(co)}")
    role_counts = df["role"].value_counts().to_dict()
    print(f"coords {len(co)} rows / {co['stem'].nunique()} videos; roles {role_counts}", flush=True)

    # ---- triple multiplicity from the replay tail graphs (optional)
    side_json = Path(str(coords_path) + ".json")
    export_meta = json.loads(side_json.read_text(encoding="utf-8")) if side_json.is_file() else {}
    tail_dir = None
    if a.tail_dir.lower() == "auto":
        cand = DEFAULT_REPLAY / str(export_meta.get("base_key", "")) if export_meta.get("base_key") else None
        tail_dir = cand if cand is not None and cand.is_dir() else None
    elif a.tail_dir.lower() != "none":
        tail_dir = Path(a.tail_dir)
        if not tail_dir.is_dir():
            raise SystemExit(f"--tail-dir {tail_dir} not found")
    keep = df[df["role"].isin(KEEP_ROLES)].copy()
    for col in ("n_triples", "n_u", "n_c1", "n_v"):
        keep[col] = np.nan
    triples_info = {"source": "none (uniform cont sampling)", "tail_dir": None}
    if tail_dir is not None:
        params = export_meta["candidate_params"]
        stems = sorted(keep["stem"].unique())
        jobs = []
        for stem in stems:
            sub = co[co["stem"] == stem].sort_values("node_id")
            jobs.append((stem, str(tail_dir / f"{stem}.npz"), params, sub["node_id"].to_numpy(),
                         sub[["t", "z", "y", "x"]].to_numpy(np.float64)))
        print(f"triple counts for {len(jobs)} videos from {tail_dir} ({a.workers} workers) ...", flush=True)
        results, total_triples = {}, 0
        with ProcessPoolExecutor(max_workers=max(1, a.workers)) as pool:
            for k, res in enumerate(pool.map(triple_counts, jobs, chunksize=4), start=1):
                if res["error"]:
                    raise SystemExit(f"{res['stem']}: {res['error']} -> tail graphs do not match the export")
                want = (export_meta.get("per_video") or {}).get(res["stem"], {}).get("triples")
                if want is not None and int(want) != res["triples"]:
                    raise SystemExit(f"{res['stem']}: {res['triples']} triples, export recorded {want}")
                results[res["stem"]] = res
                total_triples += res["triples"]
                if k % 50 == 0:
                    print(f"  {k}/{len(jobs)} videos ({time.time() - t0:.0f} s)", flush=True)
        counts = pd.concat([pd.DataFrame({"stem": s, "node_id": r["node_id"], "n_u": r["n_u"], "n_c1": r["n_c1"],
                                          "n_v": r["n_v"]}) for s, r in results.items()], ignore_index=True)
        counts["n_triples"] = counts["n_u"] + counts["n_c1"] + counts["n_v"]
        keep = keep.drop(columns=["n_triples", "n_u", "n_c1", "n_v"]).merge(
            counts, on=["stem", "node_id"], how="left", validate="one_to_one")
        if keep["n_triples"].isna().any() or (keep["n_triples"] < 1).any():
            raise SystemExit("a kept node has no triple count (every exported node is in >= 1 triple)")
        triples_info = {"source": "div_insert.candidate_triples on the replay tail graphs",
                        "tail_dir": str(tail_dir), "candidate_params": params, "triples_recomputed": total_triples,
                        "div_insert_sha_export": export_meta.get("div_insert_sha"),
                        "div_insert_sha_now": sha256_file(ROOT / "tools" / "div_insert.py")}

    # ---- selection: all parent / daughter rows, cont <= cap per video (triple-weighted)
    parts, per_video = [], {}
    for stem, g in keep.groupby("stem", sort=True):
        pd_rows = g[g["role"] != "cont"]
        cont = g[g["role"] == "cont"]
        if len(cont) > a.cont_per_video:
            w = cont["n_triples"].to_numpy(np.float64) if tail_dir is not None else np.ones(len(cont))
            pos = weighted_pick(cont["node_id"].to_numpy(), w, a.cont_per_video, stem, a.seed)
            cont_sel = cont.iloc[pos]
        else:
            cont_sel = cont
        parts.append(pd.concat([pd_rows, cont_sel]))
        per_video[stem] = {"parent": int((g["role"] == "parent").sum()), "daughter": int((g["role"] == "daughter").sum()),
                           "cont_available": int(len(cont)), "cont": int(len(cont_sel))}
    out = pd.concat(parts, ignore_index=True)
    out["label"] = out["role"].astype(str)
    out = out.sort_values(["stem", "t", "node_id"]).reset_index(drop=True)
    for col in ("n_triples", "n_u", "n_c1", "n_v"):
        out[col] = out[col].astype("float64") if out[col].isna().any() else out[col].astype(np.int32)
    out["gt_id"] = out["gt_id"].astype(np.int64)
    out = out[OUT_COLUMNS]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_path, index=False)

    # ---- sidecar: counts, inputs, fold coverage, v1 baseline on the same rows
    folds = json.loads(SPLITS.read_text(encoding="utf-8"))["folds"] if SPLITS.is_file() else {}
    by_label = out["label"].value_counts().to_dict()
    by_emb = out.groupby([out["stem"].str[:4], "label"]).size().unstack(fill_value=0)
    side = {
        "file": str(out_path.relative_to(ROOT)) if out_path.is_relative_to(ROOT) else str(out_path),
        "rows": int(len(out)), "videos": int(out["stem"].nunique()), "by_label": by_label,
        "by_embryo": {e: {k: int(v) for k, v in r.items()} for e, r in by_emb.iterrows()},
        "by_fold": ({str(f): {k: int(v) for k, v in r.items()}
                     for f, r in out.groupby(out["stem"].map(folds), dropna=False)["label"].value_counts()
                     .unstack(fill_value=0).iterrows()} if folds else None),
        "unique_gt": {lbl: int(out.loc[out.label == lbl, ["stem", "gt_id"]].drop_duplicates().shape[0])
                      for lbl in KEEP_ROLES},
        "roles_in_labels": {k: int(v) for k, v in role_counts.items()},
        "cont_per_video": a.cont_per_video, "seed": a.seed,
        "cont_sampling": ("weighted without replacement, w = n_triples (Efraimidis-Spirakis), rng default_rng([seed, "
                          "crc32(stem)]) over cont rows in node_id order" if tail_dir is not None else
                          "uniform without replacement (same rng)"),
        "triples": triples_info,
        "inputs": {"coords": str(coords_path), "coords_sha256": sha256_file(coords_path),
                   "labels": str(labels_path), "labels_sha256": sha256_file(labels_path),
                   "export_base_key": export_meta.get("base_key")},
        "coordinates": "PREDICTED node coordinates (coords file), float voxel units of the full-resolution frame",
        "per_video": per_video,
        "sha256": sha256_file(out_path),
    }
    if tail_dir is not None:
        cont_all = keep[keep["role"] == "cont"]
        cont_out = out[out["label"] == "cont"]
        side["n_triples_cont"] = {"all_cont_mean": float(cont_all["n_triples"].mean()),
                                  "selected_cont_mean": float(cont_out["n_triples"].mean()),
                                  "selected_cont_median": float(cont_out["n_triples"].median()),
                                  "all_cont_median": float(cont_all["n_triples"].median())}
    v1_path = Path(a.v1_oof) if a.v1_oof.lower() != "none" else None
    if v1_path is not None and v1_path.is_file():
        p = pd.read_parquet(v1_path)
        sel = out.merge(p, on=["stem", "node_id"], how="left", validate="one_to_one")
        full = keep.assign(label=keep["role"]).merge(p, on=["stem", "node_id"], how="left", validate="one_to_one")
        fold_ok = bool(not folds or (sel["fold"].astype(int) == sel["stem"].map(folds).astype(int)).all())
        side["v1_oof_baseline"] = {
            "source": str(v1_path), "fold_matches_splits": fold_ok, "missing_p": int(sel["p_par"].isna().sum()),
            "on_pool_samples": v1_baseline(sel),
            "on_all_labelled_pool_rows": v1_baseline(full),
        }
    Path(str(out_path) + ".json").write_text(json.dumps(side, indent=1, default=str) + "\n", encoding="utf-8")

    print(f"wrote {out_path} ({len(out)} rows, {out['stem'].nunique()} videos) in {time.time() - t0:.0f} s")
    print(by_emb.to_string())
    if "n_triples_cont" in side:
        print("n_triples of cont rows (mean all -> selected):", side["n_triples_cont"])
    if "v1_oof_baseline" in side:
        b = side["v1_oof_baseline"]["on_pool_samples"]["all"]
        print(f"v1 OOF on these rows: parent-vs-cont AUC {b['auc_p_par_parent_vs_cont']}, daughter-vs-cont AUC "
              f"{b['auc_p_dau_daughter_vs_cont']} (fold check {side['v1_oof_baseline']['fold_matches_splits']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
