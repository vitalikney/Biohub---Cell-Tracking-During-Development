"""Two targeted adversarial tests of the v2 extra-sample path of kdn_core (complements test_extra_samples.py).

    python experiments/l2_daughternet/kdn_train/run_local.py --out <v2> --extra-samples experiments/l2_daughternet/pool_samples.parquet
    python experiments/l2_daughternet/kdn_train/test_v2_targeted.py --v2 <v2>

Test 1  folds / labels / dedup
  1a synthetic merge_extra_samples: dedup is euclidean in full-resolution VOXELS (dz = 1 voxel = 1.625 um is a duplicate),
     the 1-voxel boundary is inclusive, another t is never a duplicate, a pool row with a conflicting label within 1 voxel is
     dropped and the GT row keeps its label, none / other / unknown labels and rows of unselected videos never enter,
     pool fold = the video's fold, GT rows first and unchanged; load_extra_samples rejects duplicated keys / missing columns
  1b full data (199 videos, 5 folds, embedded splits.json): every row's fold = its splits.json fold, every 44b6 leak group
     sits in one fold, no video is on both sides of any fold's train / OOF split, pool labels = coords_labels roles and
     only parent / daughter / cont (role none / other never used), the GT rows are bit-identical to a run without extra
     samples
Test 2  sampler / pool weight / crop contract
  2a the REAL train_fold sampler (recording RNG, aborted before the first step, 30,000 draws): classes drawn uniformly,
     each drawn row carries the class it was drawn for, the pool share inside each class = the pool share of that
     class's training rows, every drawn row is a training row (never the OOF fold), KDN_POOL_WEIGHT does not change the
     draws
  2b the REAL first training step: KDN_POOL_WEIGHT = 1 -> plain mean cross_entropy (v1 path); KDN_POOL_WEIGHT = 3 ->
     loss == sum(w * CE) / sum(w) with w = 3 on pool rows, 1 on GT rows, targets = the batch's labels
  2c crop_video at adversarial FLOAT coordinates (0.5 rounding boundaries after the 4x XY pooling, z .5, out-of-frame,
     last frame, predicted pool coordinates with fractional parts): every inner crop == prepare_sample (contract) exactly
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import tempfile
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


# ----------------------------------------------------------------------------------------------------------------------
# test 1: folds / labels / dedup
# ----------------------------------------------------------------------------------------------------------------------
def test_merge_synthetic(kdn_core) -> None:
    gt = pd.DataFrame([
        {"stem": "6bba_s1", "node_id": 1000001, "t": 5, "z": 10.0, "y": 100.0, "x": 100.0, "label": "parent", "kind": "parent"},
        {"stem": "6bba_s1", "node_id": 1000002, "t": 5, "z": 20.0, "y": 200.0, "x": 200.0, "label": "cont", "kind": "hardneg_u"},
        {"stem": "44b6_s2", "node_id": 1000003, "t": 3, "z": 5.0, "y": 50.0, "x": 50.0, "label": "daughter", "kind": "daughter"},
    ])
    gt["label_idx"] = gt["label"].map(kdn_core.CLASS_INDEX).astype(int)
    folds = {"6bba_s1": 1, "44b6_s2": 0}
    gt["fold"] = gt["stem"].map(folds).astype(int)
    gt["embryo"] = gt["stem"].str[:4]
    ex = pd.DataFrame([  # (name, stem, node_id, t, z, y, x, label, expected: keep / drop reason)
        ("e1", "6bba_s1", 11, 5, 11.0, 100.0, 100.0, "parent", "dup"),        # dz = 1 voxel (1.625 um) -> duplicate
        ("e2", "6bba_s1", 12, 5, 10.0, 100.0, 101.0, "parent", "dup"),        # dx = 1 voxel exactly -> duplicate
        ("e3", "6bba_s1", 13, 5, 10.0, 100.0, 101.0001, "parent", "keep"),    # just beyond 1 voxel -> kept
        ("e4", "6bba_s1", 14, 6, 10.0, 100.0, 100.0, "parent", "keep"),       # same place, other t -> kept
        ("e5", "6bba_s1", 15, 5, 20.0, 200.0, 200.5, "parent", "dup"),        # conflicting label within 1 voxel
        ("e6", "6bba_s3", 16, 5, 10.0, 100.0, 100.0, "cont", "video"),        # video not selected
        ("e7", "44b6_s2", 17, 3, 5.0, 50.0, 80.0, "none", "label"),           # unannotated space: never a sample
        ("e8", "44b6_s2", 18, 3, 5.0, 50.0, 90.0, "other", "label"),
        ("e9", "44b6_s2", 19, 3, 5.0, 50.0, 58.0, "daughter", "keep"),        # 8 voxels away -> kept
        ("e10", "6bba_s1", 20, 5, 30.0, 30.0, 30.0, "Parent", "label"),       # unknown label spelling
        ("e11", "44b6_s2", 21, 3, 5.0, 50.0, 50.0, "cont", "dup"),            # same xyz, other label than GT daughter
    ], columns=["name", "stem", "node_id", "t", "z", "y", "x", "label", "expect"])
    ex["dist_um"] = 1.0
    ex["gt_id"] = 1000001
    out, info, per_video = kdn_core.merge_extra_samples(gt, ex.drop(columns=["name", "expect"]), folds, 1.0)
    n_gt = len(gt)
    pool = out.iloc[n_gt:]
    kept = set(pool["node_id"])
    want_keep = set(ex.loc[ex["expect"] == "keep", "node_id"])
    check("1a-i synthetic: exactly the expected pool rows survive", kept == want_keep,
          f"kept {sorted(kept)} expected {sorted(want_keep)}")
    check("1a-ii synthetic: drop counters (dup 4, other videos 1, unknown labels 3, conflicting-label dups not same)",
          info["dedup_dropped"] == 4 and info["rows_other_videos"] == 1 and info["rows_unknown_label"] == 3
          and info["dedup_same_label"] == 2, json.dumps({k: info[k] for k in ("dedup_dropped", "rows_other_videos",
                                                                                "rows_unknown_label", "dedup_same_label")}))
    cols = ["stem", "node_id", "t", "z", "y", "x", "label", "kind", "label_idx", "fold", "embryo"]
    check("1a-iii synthetic: GT rows first and unchanged (labels kept on conflicts)",
          out.iloc[:n_gt][cols].reset_index(drop=True).equals(gt[cols]) and (out.iloc[:n_gt]["source"] == "gt").all())
    check("1a-iv synthetic: pool rows carry source=pool, kind pool_<label>, fold = the video's fold, only class labels",
          bool((pool["source"] == "pool").all() and (pool["kind"] == "pool_" + pool["label"]).all()
               and (pool["fold"] == pool["stem"].map(folds)).all() and pool["label"].isin(kdn_core.CLASSES).all()))
    with tempfile.TemporaryDirectory() as td:
        bad = Path(td) / "dup.csv"
        ex.drop(columns=["name", "expect"]).pipe(lambda d: pd.concat([d, d.iloc[:1]])).to_csv(bad, index=False)
        try:
            kdn_core.load_extra_samples(bad)
            dup_raised = False
        except ValueError:
            dup_raised = True
        miss = Path(td) / "miss.csv"
        ex.drop(columns=["name", "expect", "label"]).to_csv(miss, index=False)
        try:
            kdn_core.load_extra_samples(miss)
            miss_raised = False
        except ValueError:
            miss_raised = True
    check("1a-v load_extra_samples rejects duplicated (stem, node_id) and a missing label column",
          dup_raised and miss_raised)


def test_full_data_folds(kdn_core, data_dir: Path, pool_path: Path, labels_path: Path, work: Path) -> None:
    splits_path = ROOT / "experiments" / "l2_daughternet" / "splits.json"
    sp = json.loads(splits_path.read_text(encoding="utf-8"))
    base = {"data_dir": str(data_dir), "cache_dir": str(work / "cache"), "smoke": False, "n_folds": 5,
            "splits_path": str(splits_path), "stems": [], "max_videos": 0}
    st = kdn_core.step_prepare(kdn_core.config_from_env({**base, "work_dir": str(work / "v2"),
                                                         "extra_samples": str(pool_path)}))
    st0 = kdn_core.step_prepare(kdn_core.config_from_env({**base, "work_dir": str(work / "v0"), "extra_samples": ""}))
    meta, meta0 = st["meta"], st0["meta"]
    folds = sp["folds"]
    check("1b-i every row's fold == its video's splits.json fold (gt and pool)",
          bool((meta["fold"] == meta["stem"].map(folds)).all()) and len(st["stems"]) == 199,
          f"{len(meta)} rows, {len(st['stems'])} videos, sources {meta['source'].value_counts().to_dict()}")
    groups = sp["meta"]["leak_groups"]
    groups = groups if isinstance(groups, list) else list(groups.values())
    split_groups = [g for g in groups if len({int(meta.loc[meta["stem"] == s, "fold"].iloc[0]) for s in g
                                              if (meta["stem"] == s).any()}) > 1]
    check("1b-ii every leak group sits in one fold (with the pool rows)", not split_groups,
          f"{len(groups)} groups, split {split_groups}")
    crossed = {}
    for k in sorted(meta["fold"].unique()):
        tr = set(meta.loc[meta["fold"] != k, "stem"])
        oof = set(meta.loc[meta["fold"] == k, "stem"])
        grp_of = {s: i for i, g in enumerate(groups) for s in g}
        tr_groups = {grp_of[s] for s in tr if s in grp_of}
        oof_groups = {grp_of[s] for s in oof if s in grp_of}
        if tr & oof or tr_groups & oof_groups:
            crossed[int(k)] = sorted(tr & oof) + [f"group{g}" for g in sorted(tr_groups & oof_groups)]
    check("1b-iii no video / leak group on both sides of any fold's train vs OOF split", not crossed, str(crossed))
    lab = pd.read_parquet(labels_path)
    pool = meta[meta["source"] == "pool"].merge(lab[["stem", "node_id", "role", "t"]], on=["stem", "node_id"],
                                                how="left", suffixes=("", "_lab"), validate="one_to_one")
    check("1b-iv pool labels == coords_labels role, never none / other, t unchanged",
          bool(pool["role"].notna().all() and (pool["role"] == pool["label"]).all()
               and pool["label"].isin(["parent", "daughter", "cont"]).all() and (pool["t"] == pool["t_lab"]).all()),
          f"{len(pool)} pool rows {pool['label'].value_counts().to_dict()}")
    check("1b-v all labels are DaughterNet classes (gt and pool)", bool(meta["label"].isin(kdn_core.CLASSES).all()))
    n_gt = int((meta["source"] == "gt").sum())
    cols = [c for c in meta0.columns]
    check("1b-vi GT rows (first n_gt) bit-identical to the run without extra samples",
          len(meta0) == n_gt and meta.iloc[:n_gt][cols].reset_index(drop=True).equals(meta0[cols].reset_index(drop=True)),
          f"gt rows {n_gt}, no-extra rows {len(meta0)}")


# ----------------------------------------------------------------------------------------------------------------------
# test 2: sampler / pool weight / crop contract
# ----------------------------------------------------------------------------------------------------------------------
class _Stop(Exception):
    pass


class _RecordingRng:
    """Wraps a numpy Generator; records the sampler's choice / shuffle calls, can abort train_fold right after them."""

    def __init__(self, gen, stop_after_shuffle: bool) -> None:
        self._gen = gen
        self.stop_after_shuffle = stop_after_shuffle
        self.choices: list[np.ndarray] = []
        self.order_before_shuffle = None
        self.order_after_shuffle = None

    def choice(self, *args, **kwargs):
        out = self._gen.choice(*args, **kwargs)
        self.choices.append(np.array(out, copy=True))
        return out

    def shuffle(self, x, *args, **kwargs):
        self.order_before_shuffle = np.array(x, copy=True)
        self._gen.shuffle(x, *args, **kwargs)
        self.order_after_shuffle = np.array(x, copy=True)
        if self.stop_after_shuffle:
            raise _Stop()

    def __getattr__(self, name):
        return getattr(self._gen, name)


def _run_fold_recording(kdn_core, cfg: dict, fold: int, stop_after_shuffle: bool):
    """train_fold with numpy.random.default_rng and torch.amp.GradScaler / cross_entropy instrumented; aborted either
    right after the epoch's sampler (shuffle) or at the first backward (scaler.scale). Returns the recorder dict."""
    import torch

    rec: dict = {"rng": None, "ce": [], "loss": None}
    real_rng, real_ce, real_scaler = np.random.default_rng, torch.nn.functional.cross_entropy, torch.amp.GradScaler

    def fake_rng(*args, **kwargs):
        r = _RecordingRng(real_rng(*args, **kwargs), stop_after_shuffle)
        if rec["rng"] is None:
            rec["rng"] = r
        return r

    def fake_ce(input, target, *args, **kwargs):
        out = real_ce(input, target, *args, **kwargs)
        rec["ce"].append({"reduction": kwargs.get("reduction", "mean"), "target": target.detach().cpu().numpy().copy(),
                          "out": out.detach().cpu().numpy().copy()})
        return out

    class FakeScaler:
        def __init__(self, *args, **kwargs):
            pass

        def scale(self, loss):
            rec["loss"] = float(loss.detach().cpu())
            raise _Stop()

    np.random.default_rng = fake_rng
    torch.nn.functional.cross_entropy = fake_ce
    torch.amp.GradScaler = FakeScaler
    try:
        kdn_core.train_fold(cfg, fold, "cpu", threads=4)
        raise RuntimeError("train_fold returned without reaching the instrumented stop")
    except _Stop:
        pass
    finally:
        np.random.default_rng = real_rng
        torch.nn.functional.cross_entropy = real_ce
        torch.amp.GradScaler = real_scaler
    return rec


def test_sampler_and_weight(kdn_core, v2: Path, work: Path) -> None:
    cache = v2 / "cache"
    base = json.loads((cache / "kdn_cfg.json").read_text())
    base.update({"_cache_dir": str(cache), "_work_dir": str(work / "tf"), "epochs": 1})
    meta = pd.read_csv(cache / "meta.csv", index_col="row")
    meta = meta[meta["valid"].astype(bool)]
    for fold in sorted(meta["fold"].unique()):
        fold = int(fold)
        tr = meta[meta["fold"] != fold]                       # train_fold's train rows (inner_val off), index order
        y_tr = tr["label_idx"].to_numpy()
        src_tr = tr["source"].to_numpy()
        n_draw = 30000
        recs = {}
        for pw in (1.0, 3.0):
            cfg = {**copy.deepcopy(base), "epoch_samples": n_draw, "pool_weight": pw}
            recs[pw] = _run_fold_recording(kdn_core, cfg, fold, stop_after_shuffle=True)["rng"]
        r = recs[1.0]
        cls = r.choices[0]
        order = r.order_before_shuffle
        present = sorted(set(y_tr.tolist()))
        counts = np.bincount(y_tr[order], minlength=3)
        sd = np.sqrt(n_draw * (1 / len(present)) * (1 - 1 / len(present)))
        balanced = all(abs(counts[c] - n_draw / len(present)) <= 5 * sd for c in present)
        check(f"2a-i fold {fold}: classes drawn uniformly ({n_draw} draws)", balanced,
              f"counts [cont, parent, daughter] {counts.tolist()}, 5 sd = {5 * sd:.0f}")
        check(f"2a-ii fold {fold}: each drawn row carries the class it was drawn for (position by position)",
              len(order) == len(cls) == n_draw and bool(np.array_equal(y_tr[order], cls)))
        shares = []
        ok_share = True
        for c in present:
            drawn = order[y_tr[order] == c]
            p_exp = float((src_tr[y_tr == c] == "pool").mean())
            p_got = float((src_tr[drawn] == "pool").mean())
            tol = 5 * np.sqrt(max(p_exp * (1 - p_exp), 1e-12) / max(len(drawn), 1)) + 1e-9
            ok_share &= abs(p_got - p_exp) <= tol
            shares.append(f"{kdn_core.CLASSES[c]} pool share {p_got:.3f} vs rows {p_exp:.3f}")
        check(f"2a-iii fold {fold}: within each class, pool rows drawn in proportion to their training rows", ok_share,
              "; ".join(shares))
        drawn_stems = set(tr.iloc[np.unique(order)]["stem"])
        oof_stems = set(meta.loc[meta["fold"] == fold, "stem"])
        check(f"2a-iv fold {fold}: every drawn row is a training row (no OOF-fold video)",
              not (drawn_stems & oof_stems) and int(order.max()) < len(tr), f"drawn videos {sorted(drawn_stems)}")
        check(f"2a-v fold {fold}: KDN_POOL_WEIGHT 3 draws exactly the same rows as 1",
              bool(np.array_equal(recs[3.0].order_after_shuffle, r.order_after_shuffle)))

        # 2b first training step: loss formula
        for pw in (1.0, 3.0):
            cfg = {**copy.deepcopy(base), "pool_weight": pw}
            rec = _run_fold_recording(kdn_core, cfg, fold, stop_after_shuffle=False)
            idx = rec["rng"].order_after_shuffle[: int(cfg["batch"])]
            first = rec["ce"][0]
            targets_ok = bool(np.array_equal(first["target"], y_tr[idx]))
            if pw == 1.0:
                ok = first["reduction"] == "mean" and targets_ok and abs(rec["loss"] - float(first["out"])) < 1e-6
                check(f"2b-i fold {fold}: KDN_POOL_WEIGHT 1 -> v1 mean cross_entropy on the batch labels", ok,
                      f"reduction {first['reduction']}, loss {rec['loss']:.6f}")
            else:
                w = np.where(src_tr[idx] == "pool", pw, 1.0)
                want = float((first["out"] * w).sum() / w.sum())
                ok = first["reduction"] == "none" and targets_ok and abs(rec["loss"] - want) < 1e-5
                check(f"2b-ii fold {fold}: KDN_POOL_WEIGHT 3 -> loss == sum(w*CE)/sum(w) (w=3 pool, 1 gt)", ok,
                      f"loss {rec['loss']:.6f} vs {want:.6f}; batch pool rows {int((src_tr[idx] == 'pool').sum())}/"
                      f"{len(idx)}; plain mean would be {float(first['out'].mean()):.6f}")


def test_float_contract(kdn_core, data_dir: Path, pool_path: Path) -> None:
    from tools.daughternet import DEFAULT_CFG, prepare_sample

    pool = pd.read_parquet(pool_path)
    stem = "6bba_48816121"
    zmeta = json.loads((data_dir / f"{stem}.zarr" / "0" / "zarr.json").read_text())
    n_t = int(zmeta["shape"][0])
    nodes = [
        (0, 0.5, 2.0, 6.0),            # y/4 = 0.5 -> 0, x/4 = 1.5 -> 2 (banker's rounding), z .5 -> 0, first frame
        (10, 31.5, 130.0, 126.0),      # y/4 = 32.5 -> 32, x/4 = 31.5 -> 32, z 31.5 -> 32
        (n_t - 1, 63.5, 254.0, 250.0),  # last frame: lags +1/+2 clamp; z beyond the stack half
        (n_t - 2, 62.49, 1.99, 253.99),
        (5, -3.2, -10.0, 300.7),       # outside the frame -> zero padding
        (7, 70.0, 260.0, -6.0),
    ]
    sub = pool[pool["stem"] == stem].sort_values("node_id").head(20)
    rng = np.random.default_rng(7)
    for _, r in sub.iterrows():
        nodes.append((int(r["t"]), float(r["z"]), float(r["y"]), float(r["x"])))
        nodes.append((int(r["t"]), float(r["z"]) + float(rng.uniform(-0.49, 0.49)),
                      float(r["y"]) + float(rng.uniform(-2, 2)), float(r["x"]) + float(rng.uniform(-2, 2))))
    job = {"stem": stem, "data_dir": str(data_dir), "dtype": "float32", "checks": len(nodes),
           "sources": ["pool"] * len(nodes), "nodes": nodes}
    res = kdn_core.crop_video(job)
    check("2c-i crop_video at adversarial float coordinates: every inner crop == contract (in-build check on all)",
          res["error"] is None and res["checked"] == len(nodes) and res["checked_pool"] == len(nodes),
          f"{len(nodes)} nodes, error {res['error']}, checked {res['checked']}")
    if res["error"] is None:
        m = kdn_core.MARGIN
        c = kdn_core.CROP
        reader = kdn_core.FrameReader(data_dir)
        bundle = {"config": copy.deepcopy(DEFAULT_CFG), "prepared_frames": {}}
        n_eq = 0
        for i, (t, z, y, x) in sorted(enumerate(nodes), key=lambda kv: kv[1][0]):
            ref = prepare_sample(stem, int(t), {"t": int(t), "z": z, "y": y, "x": x}, bundle, {}, reader)
            n_eq += int(np.array_equal(res["crops"][i][:, m:m + c[0], m:m + c[1], m:m + c[2]], ref[:4]))
        check("2c-ii independent re-crop (fresh reader, DEFAULT_CFG) equals the cached inner crops bit-exactly",
              n_eq == len(nodes), f"{n_eq}/{len(nodes)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--v2", required=True, help="run_local.py output WITH --extra-samples (cache kept)")
    ap.add_argument("--pool", default=str(ROOT / "experiments" / "l2_daughternet" / "pool_samples.parquet"))
    ap.add_argument("--labels", default=str(ROOT / "data_external" / "l2" / "coords_labels.parquet"))
    ap.add_argument("--data-dir", default=str(ROOT / "biohub-cell-tracking-during-development" / "train"))
    ap.add_argument("--skip-full", action="store_true", help="skip 1b (full-data prepare, ~1.5 min)")
    a = ap.parse_args()

    import kdn_core

    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        test_merge_synthetic(kdn_core)
        if not a.skip_full:
            test_full_data_folds(kdn_core, Path(a.data_dir), Path(a.pool), Path(a.labels), work)
        test_sampler_and_weight(kdn_core, Path(a.v2), work)
        test_float_contract(kdn_core, Path(a.data_dir), Path(a.pool))
    n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\n{len(RESULTS) - n_fail}/{len(RESULTS)} checks passed")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
