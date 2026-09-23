"""Label exported candidate nodes (coords parquet from replay.py --export-coords) by nearest GT node in the same frame.

For each exported node (stem, node_id, t, z, y, x in voxels) find the nearest annotated GT node at the same t within 7 um
(the metric's matching radius) and copy its role: parent (>= 2 GT children), daughter (a child of a parent),
cont (in = out = 1 and >= 2 frames from any division node of its lineage), other (annotated, none of the above),
none (no annotated node within 7 um -> unlabelled; NEVER a negative, GT is sparse).
Output parquet: stem, node_id, t, role, dist_um, gt_id. Used for (a) the pool's positive rate and (b) DaughterNet v2
hard negatives drawn from the real candidate distribution.

    python tools/label_candidates.py --coords experiments/l2_daughternet/coords_exp39.parquet --out data_external/l2/coords_labels.parquet
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/l2_daughternet/kdn_train"))
import kdn_core  # noqa: E402

SCALE = np.array([1.625, 0.40625, 0.40625])
ROLES = ["none", "cont", "parent", "daughter", "other"]


def gt_roles(g: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ids = np.asarray(g["ids"])
    t = np.asarray(g["t"]).astype(int)
    zyx = np.stack([np.asarray(g["z"]), np.asarray(g["y"]), np.asarray(g["x"])], 1).astype(float)
    e = np.asarray(g["edges"]).reshape(-1, 2)
    src, dst = e[:, 0], e[:, 1]
    idx = {int(n): i for i, n in enumerate(ids)}
    outdeg = np.zeros(len(ids), int); indeg = np.zeros(len(ids), int)
    children = {}
    parent_of = {}
    for s, d in zip(src, dst):
        si, di = idx.get(int(s)), idx.get(int(d))
        if si is None or di is None:
            continue
        outdeg[si] += 1; indeg[di] += 1
        children.setdefault(si, []).append(di); parent_of[di] = si
    role = np.full(len(ids), 4, int)  # other
    div = set(np.flatnonzero(outdeg >= 2).tolist())
    dau = set(c for p in div for c in children.get(p, []))
    near = set()
    for p in div:  # nodes within 2 frames of a division along the lineage are not clean cont
        stack = [(p, 0)]
        for node, k in stack:
            near.add(node)
            if k < 2:
                for c in children.get(node, []):
                    stack.append((c, k + 1))
                if node in parent_of:
                    stack.append((parent_of[node], k + 1))
    for i in range(len(ids)):
        if i in div:
            role[i] = 2
        elif i in dau:
            role[i] = 3
        elif indeg[i] == 1 and outdeg[i] == 1 and i not in near:
            role[i] = 1
    return t, zyx, role, ids


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coords", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--data-dir", default=str(ROOT / "biohub-cell-tracking-during-development/train"))
    ap.add_argument("--radius-um", type=float, default=7.0)
    a = ap.parse_args()
    co = pd.read_parquet(a.coords)
    parts = []
    for stem, df in co.groupby("stem", sort=True):
        g = kdn_core.read_gt_geff(Path(a.data_dir) / f"{stem}.geff")
        t_gt, zyx_gt, role, ids = gt_roles(g)
        out_role = np.zeros(len(df), int); out_d = np.full(len(df), np.nan); out_id = np.full(len(df), -1, np.int64)
        for t, sub in df.groupby("t"):
            m = t_gt == int(t)
            if not m.any():
                continue
            tree = cKDTree(zyx_gt[m] * SCALE)
            d, j = tree.query(sub[["z", "y", "x"]].to_numpy(float) * SCALE, distance_upper_bound=a.radius_um)
            ok = np.isfinite(d)
            sel = df.index.get_indexer(sub.index)
            gi = np.flatnonzero(m)
            out_role[sel[ok]] = role[gi[j[ok]]]
            out_d[sel[ok]] = d[ok]
            out_id[sel[ok]] = np.asarray(ids)[gi[j[ok]]]
        parts.append(pd.DataFrame({"stem": stem, "node_id": df["node_id"].to_numpy(), "t": df["t"].to_numpy(),
                                   "role": [ROLES[r] for r in out_role], "dist_um": out_d, "gt_id": out_id}))
    res = pd.concat(parts, ignore_index=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    res.to_parquet(a.out, index=False)
    print(res["role"].value_counts().to_string())
    print("unique GT parents matched:", res.loc[res.role == "parent", ["stem", "gt_id"]].drop_duplicates().shape[0],
          "| unique GT daughters matched:", res.loc[res.role == "daughter", ["stem", "gt_id"]].drop_duplicates().shape[0])


if __name__ == "__main__":
    main()
