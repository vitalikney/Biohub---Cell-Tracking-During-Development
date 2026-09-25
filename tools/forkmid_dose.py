"""T3 / C04 dose: how many forks of a submission.csv would the forkmid rider touch?

Fork = node with >= 2 outgoing edges. Distance = |P - mean(children)| in um, scale (z, y, x) = (1.625, 0.40625, 0.40625);
for a plain 2-way fork this is |P - (c1 + c2) / 2|. C04 drops a (non-inserted) safe-division fork when the distance
is >= 4.5 um. The CSV cannot tell safe-division forks from inserted ones, so the dose here is an upper bound over
all forks; --base CSV splits forks into those already present in a base submission and new ones (e.g. insertion).

Rule (FINAL_REPORT §e, T3): share >= 4.5 um == 0%  -> the forkmid patch is a no-op on these clips;
                            share >  15%           -> C04 stop.

    python tools/forkmid_dose.py _dl/biohub-exp56-x138-verbatim/submission.csv --out dose_exp56.json
    python tools/forkmid_dose.py _dl/biohub-exp57b-x138-divins-only/submission.csv \
        --base _dl/biohub-exp56-x138-verbatim/submission.csv --out dose_exp57b.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCALE = np.array([1.625, 0.40625, 0.40625])  # um per voxel, z, y, x
THRESH_UM = 4.5
STOP_SHARE = 0.15
QUANTILES = (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1.0)


def forks_of(df: pd.DataFrame) -> pd.DataFrame:
    """One row per fork: dataset, parent node_id, t, parent z/y/x, n_children, dist_um."""
    nodes = df[df.row_type == "node"].set_index(["dataset", "node_id"])[["t", "z", "y", "x"]].astype(float)
    edges = df[df.row_type == "edge"][["dataset", "source_id", "target_id"]].astype(
        {"source_id": np.int64, "target_id": np.int64})
    outdeg = edges.groupby(["dataset", "source_id"]).size()
    fk = outdeg[outdeg >= 2]
    rows = []
    zyx = ["z", "y", "x"]
    for (ds, src), n in fk.items():
        kids = edges[(edges.dataset == ds) & (edges.source_id == src)].target_id.to_numpy()
        p = nodes.loc[(ds, int(src))]
        c = nodes.loc[[(ds, int(k)) for k in kids], zyx].to_numpy()
        d = float(np.linalg.norm((p[zyx].to_numpy() - c.mean(axis=0)) * SCALE))
        rows.append(dict(dataset=ds, node_id=int(src), t=int(p.t), z=float(p.z), y=float(p.y), x=float(p.x),
                         n_children=int(n), dist_um=d))
    cols = ["dataset", "node_id", "t", "z", "y", "x", "n_children", "dist_um"]
    return pd.DataFrame(rows, columns=cols)


def summarize(dist: np.ndarray, thresh: float = THRESH_UM) -> dict:
    n = int(len(dist))
    out = dict(n_forks=n, n_ge_thresh=int((dist >= thresh).sum()) if n else 0)
    out["share_ge_thresh"] = out["n_ge_thresh"] / n if n else 0.0
    out["quantiles_um"] = {f"q{int(q * 100):02d}": float(np.quantile(dist, q)) for q in QUANTILES} if n else {}
    out["mean_um"] = float(dist.mean()) if n else None
    return out


def verdict(share: float) -> str:
    if share == 0:
        return "NO-OP (0% >= thresh: forkmid does nothing here)"
    if share > STOP_SHARE:
        return "C04 STOP (share > 15%)"
    return "OK (0% < share <= 15%)"


def dose(csv: Path, base: Path | None = None, thresh: float = THRESH_UM) -> dict:
    f = forks_of(pd.read_csv(csv))
    if base is not None:
        # a fork is "in base" if the base submission has a fork at the same dataset/t/parent position
        fb = forks_of(pd.read_csv(base))
        key = ["dataset", "t", "z", "y", "x"]
        f = f.merge(fb[key].drop_duplicates().assign(in_base=True), on=key, how="left")
        f["in_base"] = f["in_base"].fillna(False).astype(bool)
    res = dict(csv=str(csv), thresh_um=thresh, scale_zyx=SCALE.tolist(), **summarize(f.dist_um.to_numpy(), thresh))
    res["n_forks_gt2_children"] = int((f.n_children > 2).sum())
    res["verdict"] = verdict(res["share_ge_thresh"])
    res["per_video"] = {ds: summarize(g.dist_um.to_numpy(), thresh) for ds, g in f.groupby("dataset")}
    if base is not None:
        res["base_csv"] = str(base)
        res["in_base"] = summarize(f[f.in_base].dist_um.to_numpy(), thresh)
        res["new_vs_base"] = summarize(f[~f.in_base].dist_um.to_numpy(), thresh)
    res["forks"] = f.sort_values(["dataset", "t", "node_id"]).to_dict(orient="records")
    return res


def _line(name: str, s: dict) -> str:
    q = s["quantiles_um"]
    qs = " ".join(f"{k}={v:.2f}" for k, v in q.items()) if q else "-"
    return (f"{name:<16} forks={s['n_forks']:>4}  >=thr={s['n_ge_thresh']:>3} "
            f"({100 * s['share_ge_thresh']:5.1f}%)  {qs}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", type=Path)
    ap.add_argument("--base", type=Path, default=None, help="base submission.csv to split forks into base/new")
    ap.add_argument("--thresh", type=float, default=THRESH_UM)
    ap.add_argument("--out", type=Path, default=None, help="output JSON (default: <csv stem>_forkmid_dose.json "
                                                           "next to the CSV)")
    a = ap.parse_args(argv)
    res = dose(a.csv, a.base, a.thresh)
    print(f"forkmid dose: {a.csv}  (thresh {a.thresh} um, scale zyx {SCALE.tolist()})")
    print(_line("ALL", res))
    for ds, s in res["per_video"].items():
        print(_line(ds, s))
    if a.base is not None:
        print(_line("in base", res["in_base"]))
        print(_line("new vs base", res["new_vs_base"]))
    print(f"forks with > 2 children: {res['n_forks_gt2_children']}")
    print(f"VERDICT: {res['verdict']}")
    out = a.out or a.csv.with_name(a.csv.stem + "_forkmid_dose.json")
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
