"""Local acceptance test of the v2 extra-sample path (KDN_EXTRA_SAMPLES) of kdn_core, on finished run_local.py outputs.

    python experiments/l2_daughternet/kdn_train/run_local.py --out <v2> --extra-samples experiments/l2_daughternet/pool_samples.parquet
    python experiments/l2_daughternet/kdn_train/run_local.py --out <v0>          # new code, no extra samples
    <v1 reference run of the committed kdn_core.py with the same smoke settings>   -> <v1>
    python experiments/l2_daughternet/kdn_train/test_extra_samples.py --v2 <v2> --v0 <v0> --v1 <v1>

Checks
  1 labels per source: the pool rows in meta/oof are exactly the pool parquet rows of the selected videos minus the
    GT duplicates (recomputed here independently: same stem and t, <= 1 voxel from a GT sample), labels unchanged
  2 crops: every pool row's cached inner crop == tools.daughternet.prepare_sample at the PREDICTED coordinates of the
    parquet (fresh reader, DEFAULT_CFG), bit-exact; a few GT rows the same way
  3 oof.csv carries source (gt / pool) on every row, all rows predicted, counts equal meta
  4 oof_readout.json has by_source.gt and by_source.pool blocks
  5 fold routing: splits_used.json and the GT rows (index, identity, fold) equal the v1 run; pool fold = its video's
    fold; fold k's oof.csv holds exactly the fold-k rows; fold k trained on exactly the rows of the other folds; the GT
    crops equal v1's bit-exactly
  6 v0 (no KDN_EXTRA_SAMPLES) reproduces v1: meta (minus the new source column), crops, fold oof.csv, best.pt weights,
    merged oof.csv predictions and the per-embryo readout
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in (str(ROOT), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""), flush=True)
    return bool(ok)


def load_meta(run: Path) -> pd.DataFrame:
    return pd.read_csv(run / "cache" / "meta.csv", index_col="row", float_precision="round_trip")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--v2", required=True, help="run_local.py output WITH --extra-samples")
    ap.add_argument("--v0", default="", help="run_local.py output of the new code WITHOUT extra samples")
    ap.add_argument("--v1", default="", help="output of the committed v1 kdn_core with the same settings")
    ap.add_argument("--pool", default=str(ROOT / "experiments" / "l2_daughternet" / "pool_samples.parquet"))
    ap.add_argument("--data-dir", default=str(ROOT / "biohub-cell-tracking-during-development" / "train"))
    ap.add_argument("--dedup-vox", type=float, default=1.0)
    a = ap.parse_args()

    import kdn_core
    from tools.daughternet import DEFAULT_CFG, prepare_sample
    from tools.divnet_infer import _marker

    v2 = Path(a.v2)
    meta = load_meta(v2)
    oof = pd.read_csv(v2 / "oof.csv", float_precision="round_trip")
    readout = json.loads((v2 / "oof_readout.json").read_text())
    splits_used = json.loads((v2 / "splits_used.json").read_text())
    folds = {k: int(v) for k, v in splits_used["folds"].items()}
    pool = pd.read_parquet(a.pool)

    # ---- 1 labels per source
    gt_rows = meta[meta["source"] == "gt"]
    pm = meta[meta["source"] == "pool"]
    sel = pool[pool["stem"].isin(set(folds))].copy()
    pairs = sel.reset_index().merge(gt_rows[["stem", "t", "z", "y", "x"]], on=["stem", "t"], suffixes=("", "_g"))
    d = np.sqrt((pairs.z - pairs.z_g) ** 2 + (pairs.y - pairs.y_g) ** 2 + (pairs.x - pairs.x_g) ** 2)
    dup_idx = set(pairs.loc[d.to_numpy() <= a.dedup_vox, "index"])
    expected = sel.drop(index=list(dup_idx))
    got_keys = set(zip(pm["stem"], pm["node_id"]))
    exp_keys = set(zip(expected["stem"], expected["node_id"]))
    check("1a pool rows = parquet rows of the selected videos minus GT duplicates", got_keys == exp_keys,
          f"meta {len(got_keys)}, expected {len(exp_keys)} ({len(sel)} in the videos, {len(dup_idx)} duplicates)")
    lab = pm.merge(expected[["stem", "node_id", "label", "t"]], on=["stem", "node_id"], suffixes=("", "_p"))
    check("1b pool labels / t unchanged", bool((lab["label"] == lab["label_p"]).all() and (lab["t"] == lab["t_p"]).all()),
          f"{len(lab)} rows")
    counts = meta.groupby(["source", "label"]).size().unstack(fill_value=0)
    print("meta rows by source x label:\n" + counts.to_string())
    exp_counts = expected["label"].value_counts().to_dict()
    check("1c pool label counts", {k: int(v) for k, v in pm["label"].value_counts().items()} == exp_counts,
          str(exp_counts))
    check("1d pool kinds are pool_<label>", bool((pm["kind"] == "pool_" + pm["label"]).all()))

    # ---- 2 crops at predicted coordinates == prepare_sample
    crops = np.load(v2 / "cache" / "crops.npy", mmap_mode="r")
    M = kdn_core.MARGIN
    inner = (slice(None), slice(M, M + kdn_core.CROP[0]), slice(M, M + kdn_core.CROP[1]), slice(M, M + kdn_core.CROP[2]))
    marker = _marker(kdn_core.CROP, tuple(DEFAULT_CFG["input"]["marker_sigma"]))
    coords = pm.reset_index().merge(pool[["stem", "node_id", "t", "z", "y", "x"]], on=["stem", "node_id"],
                                    suffixes=("", "_p"))
    same_xyz = bool(np.array_equal(coords[["z", "y", "x"]].to_numpy(np.float64),
                                   coords[["z_p", "y_p", "x_p"]].to_numpy(np.float64)))
    check("2a meta.csv pool coordinates == parquet predicted coordinates (bit-exact)", same_xyz, f"{len(coords)} rows")
    gt_probe = gt_rows.reset_index().groupby("stem").head(2)
    probe = pd.concat([coords.assign(_src="pool"), gt_probe.assign(z_p=gt_probe.z, y_p=gt_probe.y, x_p=gt_probe.x,
                                                                     _src="gt")], ignore_index=True)
    reader = kdn_core.FrameReader(Path(a.data_dir))
    max_diff = {"pool": 0.0, "gt": 0.0}
    n_eq = {"pool": 0, "gt": 0}
    n_all = {"pool": 0, "gt": 0}
    for stem, g in probe.groupby("stem"):
        bundle = {"config": DEFAULT_CFG, "prepared_frames": {}}
        for _, r in g.sort_values("t").iterrows():
            node = {"t": int(r["t"]), "z": float(r["z_p"]), "y": float(r["y_p"]), "x": float(r["x_p"])}
            ref = prepare_sample(stem, int(r["t"]), node, bundle, {}, reader)
            cached = np.asarray(crops[int(r["row"])], dtype=np.float32)[inner]
            ok = ref.shape == (5, *kdn_core.CROP) and np.array_equal(cached, ref[:4]) and np.array_equal(ref[4], marker)
            max_diff[r["_src"]] = max(max_diff[r["_src"]], float(np.abs(cached - ref[:4]).max()))
            n_eq[r["_src"]] += int(ok)
            n_all[r["_src"]] += 1
    check("2b every pool crop == prepare_sample at the predicted node (bit-exact)", n_eq["pool"] == n_all["pool"] > 0,
          f"{n_eq['pool']}/{n_all['pool']} equal, max |diff| {max_diff['pool']:.3g}")
    check("2c GT probe crops == prepare_sample", n_eq["gt"] == n_all["gt"] > 0,
          f"{n_eq['gt']}/{n_all['gt']} equal, max |diff| {max_diff['gt']:.3g}")
    summ = pd.read_csv(v2 / "labels_summary.csv")
    if "contract_checks_pool" in summ.columns:
        check("2d in-build contract checks ran on pool nodes", int(summ["contract_checks_pool"].fillna(0).sum()) > 0,
              f"gt+pool {int(summ['contract_checks'].fillna(0).sum())}, pool {int(summ['contract_checks_pool'].fillna(0).sum())}")
    cc = json.loads((v2 / "contract_check.json").read_text())
    check("2e end-to-end re-score (score_nodes from raw frames) passes incl. pool rows",
          bool(cc["pass"]) and cc.get("checked_pool", 0) > 0,
          f"checked {cc['checked']} (pool {cc.get('checked_pool')}), max |dp| {cc['max_abs_diff_daughternet']:.2e}")

    # ---- 3 oof.csv carries source
    check("3a oof.csv has a source column on every row", "source" in oof.columns and oof["source"].isin(["gt", "pool"]).all())
    check("3b oof rows by source == meta rows by source",
          oof.groupby("source").size().to_dict() == meta[meta["valid"]].groupby("source").size().to_dict(),
          str(oof.groupby("source").size().to_dict()))
    check("3c every oof row has predictions", bool(oof[["p_cont", "p_par", "p_dau"]].notna().all().all()))
    oof_keys = set(zip(oof.loc[oof.source == "pool", "stem"], oof.loc[oof.source == "pool", "node_id"]))
    check("3d oof pool rows keep node_id (predicted graph id) and the pool columns",
          oof_keys == got_keys and all(c in oof.columns for c in ("gt_id", "dist_um", "n_triples")))

    # ---- 4 readout blocks
    bs = readout.get("by_source", {})
    check("4a oof_readout.json has by_source.gt and by_source.pool", "gt" in bs and "pool" in bs, str(list(bs)))
    if "pool" in bs:
        pb = bs["pool"]
        check("4b pool block: per_embryo (all + embryos), vs_cont, gate_roles",
              "all" in pb["per_embryo"] and "all" in pb["vs_cont"] and "all" in pb.get("gate_roles", {}),
              f"n pool scored {pb['per_embryo']['all']['parent']['n']}")
        check("4c gt block == top-level (v1-style) per_embryo", bs["gt"]["per_embryo"] == readout["per_embryo"])

    # ---- 5 fold routing
    check("5a pool row fold == its video's fold", bool((pm["fold"] == pm["stem"].map(folds)).all()))
    check("5b gt row fold == its video's fold", bool((gt_rows["fold"] == gt_rows["stem"].map(folds)).all()))
    n_gt = len(gt_rows)
    check("5c GT rows first (indices 0..n_gt-1), pool rows appended",
          bool((meta.index[:n_gt] == np.arange(n_gt)).all() and (meta.iloc[:n_gt]["source"] == "gt").all()
               and (meta.iloc[n_gt:]["source"] == "pool").all()))
    for fold in sorted(meta["fold"].unique()):
        fdir = v2 / "folds" / f"fold_{int(fold)}"
        fo = pd.read_csv(fdir / "oof.csv")
        rows_f = set(meta.index[(meta["fold"] == fold) & meta["valid"]])
        sm = json.loads((fdir / "summary.json").read_text())
        n_train = int(((meta["fold"] != fold) & meta["valid"]).sum())
        check(f"5d fold {int(fold)}: oof rows == fold rows; trained on the other folds only",
              set(fo["row"]) == rows_f and sm["n_train"] == n_train,
              f"oof {len(fo)} (pool {int((meta.loc[list(fo['row']), 'source'] == 'pool').sum())}), train {sm['n_train']} "
              f"by source {sm.get('train_counts_by_source')}")
    if a.v1:
        v1 = Path(a.v1)
        m1 = load_meta(v1)
        cols = ["stem", "node_id", "t", "z", "y", "x", "label", "kind", "label_idx", "fold", "embryo", "valid"]
        same = (len(m1) == n_gt and (m1.index == meta.index[:n_gt]).all()
                and m1[cols].equals(meta.iloc[:n_gt][cols]))
        check("5e GT rows of the v2 run == v1 rows (index, identity, coordinates, labels, fold)", bool(same),
              f"v1 {len(m1)} rows, v2 GT {n_gt}")
        s1 = json.loads((v1 / "splits_used.json").read_text())
        check("5f splits_used.json identical to v1", s1 == splits_used, str(splits_used["folds"]))
        c1 = np.load(v1 / "cache" / "crops.npy", mmap_mode="r")
        check("5g GT crops identical to v1 (bit-exact)", bool(np.array_equal(np.asarray(c1), np.asarray(crops[:n_gt]))))

    # ---- 6 v0 reproduces v1
    if a.v0 and a.v1:
        import torch
        v0, v1 = Path(a.v0), Path(a.v1)
        m0, m1 = load_meta(v0), load_meta(v1)
        check("6a v0 meta == v1 meta (+ source=gt column only)",
              m0.drop(columns=["source"]).equals(m1) and (m0["source"] == "gt").all(),
              f"columns v0 {list(m0.columns)}")
        check("6b v0 crops == v1 crops", bool(np.array_equal(np.load(v0 / "cache" / "crops.npy"),
                                                              np.load(v1 / "cache" / "crops.npy"))))
        for fold in sorted(m1["fold"].unique()):
            f0 = pd.read_csv(v0 / "folds" / f"fold_{int(fold)}" / "oof.csv")
            f1 = pd.read_csv(v1 / "folds" / f"fold_{int(fold)}" / "oof.csv")
            dp = float(np.abs(f0[["p_cont", "p_par", "p_dau"]].to_numpy() - f1[["p_cont", "p_par", "p_dau"]].to_numpy()).max())
            b0 = torch.load(v0 / "folds" / f"fold_{int(fold)}" / "best.pt", map_location="cpu", weights_only=False)
            b1 = torch.load(v1 / "folds" / f"fold_{int(fold)}" / "best.pt", map_location="cpu", weights_only=False)
            dw = max(float((b0["model_state"][k].float() - b1["model_state"][k].float()).abs().max())
                     for k in b1["model_state"])
            check(f"6c fold {int(fold)}: v0 == v1 (fold OOF p and best.pt weights)",
                  f0["row"].equals(f1["row"]) and dp == 0.0 and dw == 0.0 and b0["config"] == b1["config"],
                  f"max |dp| {dp:.3g}, max |dw| {dw:.3g}, ckpt config equal {b0['config'] == b1['config']}")
        o0, o1 = pd.read_csv(v0 / "oof.csv"), pd.read_csv(v1 / "oof.csv")
        check("6d v0 oof.csv == v1 oof.csv (+ source column)",
              o0.drop(columns=["source"]).equals(o1) and (o0["source"] == "gt").all(),
              f"columns v0 {list(o0.columns)}")
        r0 = json.loads((v0 / "oof_readout.json").read_text())
        r1 = json.loads((v1 / "oof_readout.json").read_text())
        check("6e v0 readout per_embryo / hardneg == v1", r0["per_embryo"] == r1["per_embryo"]
              and r0["hardneg"] == r1["hardneg"] and "pool" not in r0.get("by_source", {}))

    n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\n{len(RESULTS) - n_fail}/{len(RESULTS)} checks passed")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
