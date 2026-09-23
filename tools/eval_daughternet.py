"""Leak-free Kaggle evaluation of DaughterNet checkpoints on ALL Kaggle GT labels (plan line L3 judge).

A model trained without any Kaggle label (tools/train_dorado.py: dorado pseudo-labels only) can be scored on every
labelled Kaggle node of all 199 train videos: there is no fold to hold out. CAVEAT: the 44b6 videos are space-time crops
of the dorado recording itself (tools/register_44b6_dorado.py -> data_external/dorado/kaggle44b6_in_dorado.json), so
for a dorado checkpoint trained without the strict exclusion (train_dorado --exclude-kaggle) the readout adds the
blocks '44b6_clean' and 'all_clean': the 44b6 rows whose image footprint (lag frames t-1..t+2, 16x32x32 pooled crop)
meets no sample of the checkpoint's dorado shards within --overlap-dt frames (rows of clips that could not be registered
are left out as unknown). 6bba is an independent embryo: its rows are always leak-free for a dorado-only model. The label set is EXACTLY the one of the
kdn-train kernel (experiments/l2_daughternet/kdn_train/kdn_core.extract_labels, same defaults and seed), so the
kernel's oof.csv lines up row by row (join on stem + node_id) for a like-for-like comparison.

  build   labels (parent / daughter / cont + hard negatives from the GT .geff, kdn_core.step_prepare) and the
          DivNet-contract crops (kdn_core.crop_video with its exact-contract checks; the inner 16x32x32 of its enlarged
          crop) -> one uncompressed npz, float16: x (N, 4, 16, 32, 32) image channels (the centre marker is re-added
          at scoring time), stem, node_id, t, zyx (N, 3) GT voxel position, label, label_idx, kind, fold
          (splits.json, 44b6 leak groups), embryo, valid, pad_frac (fraction of the crop outside the Kaggle clip =
          zero padding), info (json).
          The npz is written streaming (no 2 GB array in RAM) and read back memory-mapped.
  eval    one or more checkpoints ({'model_state', 'config'}, tools.daughternet.load_daughternet) -> per embryo
          (44b6, 6bba, all) and class (cont, parent, daughter): n_pos, base rate, one-vs-rest AUC, and at the top
          0.1% / 1% / 5% of the class score: precision, lift, likelihood ratio LR+ = TPR / FPR (kdn_core._rank_block,
          the same definitions as the kernel's oof_readout.json); hard-negative AUCs (parent vs hard negatives in the
          u role, daughter vs the v role). Several checkpoints: each one and their softmax mean (the score_nodes
          ensemble). --oof: the kdn-train oof.csv (stem,t,z,y,x,label,fold,p_cont,p_par,p_dau[,node_id,...]) is
          joined and scored on the common rows next to every model, plus a 50/50 probability blend with each model
          and the Spearman correlation of the class scores.

    python tools/eval_daughternet.py build           # all 199 videos -> data_external/l2/kaggle_eval_crops.npz
    python tools/eval_daughternet.py build --stems 6bba_09961292,44b6_a21120c2 --out C:/tmp/eval3.npz
    python tools/eval_daughternet.py eval --ckpt data_external/l3/dorado_only.pt [--oof oof.csv] [--out-csv p.csv]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import struct
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
KDN_DIR = ROOT / "experiments" / "l2_daughternet" / "kdn_train"
for _p in (str(ROOT), str(KDN_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import kdn_core  # noqa: E402  (labels, frame reader, crop_video, _rank_block: the kernel's own code)
from tools.daughternet import CLASSES, DEFAULT_CFG, load_daughternet  # noqa: E402
from tools.divnet_infer import _marker  # noqa: E402

DEFAULT_DATA = ROOT / "biohub-cell-tracking-during-development" / "train"
DORADO_REG = ROOT / "data_external" / "dorado" / "kaggle44b6_in_dorado.json"
DORADO_SHARDS = ROOT / "data_external" / "dorado" / "shards"
VOXEL_UM = np.array([1.625, 0.40625, 0.40625])
CROP_HALF_VOX = np.array([8, 64, 64])                  # half the 16x32x32 pooled crop in full-resolution voxels
OVERLAP_MARGIN_VOX = np.array([2, 8, 8])               # registration slack + pooled-grid rounding
DEFAULT_CACHE = ROOT / "data_external" / "l2" / "kaggle_eval_crops.npz"
CROP = kdn_core.CROP
MARGIN = kdn_core.MARGIN
N_IMG = 4
META_KEYS = ("stem", "node_id", "t", "label", "label_idx", "kind", "fold", "embryo", "valid", "pad_frac")  # + zyx
PROB_COLS = ("p_cont", "p_par", "p_dau")
log = kdn_core.log


# ---------------------------------------------------------------------------------------------------- npz streaming
def _write_npy_member(zf: zipfile.ZipFile, name: str, arr: np.ndarray) -> None:
    with zf.open(name + ".npy", "w", force_zip64=True) as fp:
        np.lib.format.write_array(fp, np.asarray(arr), allow_pickle=False)


def npz_memmap(path: Path, key: str) -> np.ndarray:
    """Memory-map one member of an UNCOMPRESSED npz (np.savez / build); falls back to a full load otherwise."""
    path = Path(path)
    with zipfile.ZipFile(path) as zf:
        info = zf.getinfo(key + ".npy")
    if info.compress_type != zipfile.ZIP_STORED:
        with np.load(path) as d:
            return d[key]
    with open(path, "rb") as f:
        f.seek(info.header_offset)
        local = f.read(30)
        if local[:4] != b"PK\x03\x04":
            raise RuntimeError(f"bad local zip header for {key} in {path}")
        name_len, extra_len = struct.unpack("<HH", local[26:30])
        f.seek(info.header_offset + 30 + name_len + extra_len)
        version = np.lib.format.read_magic(f)
        reader = np.lib.format.read_array_header_1_0 if version == (1, 0) else np.lib.format.read_array_header_2_0
        shape, fortran, dtype = reader(f)
        offset = f.tell()
    return np.memmap(path, dtype=dtype, mode="r", shape=shape, offset=offset, order="F" if fortran else "C")


def load_cache(path: Path):
    """-> (x memmap (N, 4, 16, 32, 32) float16, meta DataFrame, info dict)."""
    import pandas as pd
    path = Path(path)
    x = npz_memmap(path, "x")
    with np.load(path) as d:
        meta = pd.DataFrame({k: d[k] for k in META_KEYS if k in d.files})
        zyx = d["zyx"]
        info = json.loads(str(d["info"]))
    meta.insert(3, "z", zyx[:, 0])
    meta.insert(4, "y", zyx[:, 1])
    meta.insert(5, "x", zyx[:, 2])
    if x.shape != (len(meta), N_IMG, *CROP):
        raise RuntimeError(f"cache x shape {x.shape} does not match {len(meta)} rows")
    return x, meta, info


# ------------------------------------------------------------------------------------------------------------ build
def _pad_frac(z: float, y: float, x: float, frame_shape: tuple[int, int, int], pool: int) -> float:
    """Fraction of the contract crop outside the pooled frame (= zero padding in _crop_with_padding)."""
    dims = np.array([frame_shape[0], frame_shape[1] // pool, frame_shape[2] // pool])
    c = np.array([int(round(float(z))), int(round(float(y) / pool)), int(round(float(x) / pool))])
    lo = c - np.array(CROP) // 2
    ov = np.clip(np.minimum(lo + np.array(CROP), dims) - np.maximum(lo, 0), 0, None)
    return float(1.0 - ov.prod() / np.prod(CROP))


def cmd_build(a) -> None:
    import multiprocessing as mp

    t0 = time.time()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="kdn_eval_build_"))
    try:
        overrides = {"smoke": False, "data_dir": str(a.data_dir), "work_dir": str(work), "cache_dir": str(work / "cache"),
                     "stems": [s.strip() for s in a.stems.split(",") if s.strip()] if a.stems else [],
                     "max_videos": int(a.max_videos), "cont_per_video": int(a.cont_per_video),
                     "hardneg_per_video": int(a.hardneg_per_video), "cont_min_dist": int(a.cont_min_dist),
                     "seed": int(a.seed), "splits_path": a.splits or ""}
        cfg = kdn_core.config_from_env(overrides)
        state = kdn_core.step_prepare(cfg)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    meta = state["meta"].reset_index(drop=True)
    if a.stems and set(overrides["stems"]) - set(meta["stem"]):
        log(f"[build] WARNING stems without labels / data: {sorted(set(overrides['stems']) - set(meta['stem']))}")
    # true folds from splits.json (step_prepare deals small subsets round-robin; the cache keeps the real fold)
    sp = Path(a.splits) if a.splits else kdn_core._default_splits_path()
    splits = kdn_core.load_splits(sp) if sp else None
    if splits:
        meta["fold"] = meta["stem"].map(lambda s: int(splits.get(s, -1))).astype(int)
    data_dir = Path(state["data_dir"])
    pool = int(DEFAULT_CFG["input"]["pool_xy"])
    shapes = {}
    for s in meta["stem"].unique():
        zmeta = json.loads((data_dir / f"{s}.zarr" / "0" / "zarr.json").read_text())
        shapes[s] = tuple(int(v) for v in zmeta["shape"][1:])
    meta["pad_frac"] = [_pad_frac(z, y, x, shapes[s], pool) for s, z, y, x in
                        zip(meta["stem"], meta["z"], meta["y"], meta["x"])]
    n = len(meta)
    log(f"[build] {n} samples in {meta['stem'].nunique()} videos; clip-border padding: "
        f"{float((meta['pad_frac'] > 0).mean()):.3f} of the crops (mean padded fraction "
        f"{float(meta.loc[meta['pad_frac'] > 0, 'pad_frac'].mean()) if (meta['pad_frac'] > 0).any() else 0:.3f})")
    if a.labels_only:
        tab = meta.assign(padded=meta["pad_frac"] > 0).groupby(["embryo", "label"]).agg(
            n=("padded", "size"), padded=("padded", "mean"), pad_frac=("pad_frac", "mean"))
        print(tab.to_string())
        return

    jobs, blocks = [], []
    for stem, grp in meta.groupby("stem", sort=True):
        idx = grp.index.to_numpy()
        if not np.array_equal(idx, np.arange(idx[0], idx[0] + len(idx))):
            raise RuntimeError(f"rows of {stem} are not contiguous")
        blocks.append((stem, int(idx[0]), len(idx)))
        jobs.append({"stem": stem, "data_dir": str(data_dir), "dtype": "float16", "checks": int(a.contract_checks),
                     "nodes": list(zip(grp["t"].tolist(), grp["z"].tolist(), grp["y"].tolist(), grp["x"].tolist()))})
    if [b[1] for b in blocks] != sorted(b[1] for b in blocks) or sum(b[2] for b in blocks) != n:
        raise RuntimeError("video blocks are not in row order")
    n_workers = max(1, min(int(a.workers) or min(8, os.cpu_count() or 1), len(jobs)))
    per_worker_threads = max(1, (os.cpu_count() or 1) // n_workers)
    valid = np.zeros(n, bool)
    video_rows = []
    tmp = out.with_name(out.name + ".tmp")
    inner = (slice(None), slice(None), slice(MARGIN, MARGIN + CROP[0]), slice(MARGIN, MARGIN + CROP[1]),
             slice(MARGIN, MARGIN + CROP[2]))
    header = {"descr": np.lib.format.dtype_to_descr(np.dtype("<f2")), "fortran_order": False,
              "shape": (n, N_IMG, *CROP)}
    log(f"[build] {len(jobs)} videos on {n_workers} workers -> {out} "
        f"({n * N_IMG * int(np.prod(CROP)) * 2 / 2**30:.2f} GiB float16, uncompressed)")
    ctx = mp.get_context("spawn")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as zf:
        with zf.open("x.npy", "w", force_zip64=True) as fp:
            np.lib.format.write_array_header_2_0(fp, header)
            with ctx.Pool(n_workers, initializer=kdn_core._build_worker_init, initargs=(per_worker_threads,)) as pl:
                for k, res in enumerate(pl.imap(kdn_core.crop_video, jobs)):   # ordered: rows stream in sequence
                    stem, start, cnt = blocks[k]
                    if res["stem"] != stem:
                        raise RuntimeError("result order mismatch")
                    if res["error"] is None:
                        crops = np.ascontiguousarray(res["crops"][inner], dtype="<f2")
                        valid[start:start + cnt] = True
                    else:
                        crops = np.zeros((cnt, N_IMG, *CROP), "<f2")
                    fp.write(crops.tobytes())
                    video_rows.append({"stem": stem, "n": cnt, "secs": round(res["secs"], 2),
                                       "frames_read": res["frames_read"], "contract_checks": res["checked"],
                                       "error": res["error"]})
                    log(f"[build] {k + 1}/{len(jobs)} {stem} n={cnt} frames={res['frames_read']} "
                        f"checks={res['checked']} {res['secs']:.1f}s "
                        f"{'ok' if res['error'] is None else 'FAILED ' + res['error']}")
        meta["valid"] = valid
        cols = {"stem": meta["stem"].to_numpy(str), "node_id": meta["node_id"].to_numpy(np.int64),
                "t": meta["t"].to_numpy(np.int32),
                "zyx": meta[["z", "y", "x"]].to_numpy(np.float64),     # GT voxel coordinates ("x" is the crop array)
                "label": meta["label"].to_numpy(str), "label_idx": meta["label_idx"].to_numpy(np.int8),
                "kind": meta["kind"].to_numpy(str), "fold": meta["fold"].to_numpy(np.int8),
                "embryo": meta["embryo"].to_numpy(str), "valid": valid,
                "pad_frac": meta["pad_frac"].to_numpy(np.float32)}
        for k, v in cols.items():
            _write_npy_member(zf, k, v)
        info = {"built": time.strftime("%Y-%m-%d %H:%M:%S"), "data_dir": str(data_dir), "n": int(n),
                "videos": int(len(jobs)), "classes": list(CLASSES), "crop": list(CROP), "image_channels": N_IMG,
                "contract": DEFAULT_CFG, "dtype": "float16", "splits_source": str(sp) if splits else state["splits_source"],
                "label_cfg": {k: cfg[k] for k in ("cont_per_video", "hardneg_per_video", "cont_min_dist", "seed", "gate")},
                "valid": int(valid.sum()), "videos_failed": [r["stem"] for r in video_rows if r["error"]],
                "counts": {e: g.groupby("kind").size().to_dict() for e, g in meta.groupby("embryo")},
                "pad_any_rate": float((meta["pad_frac"] > 0).mean()), "per_video": video_rows,
                "secs": round(time.time() - t0, 1)}
        _write_npy_member(zf, "info", np.array(json.dumps(info, default=kdn_core._json_default)))
    os.replace(tmp, out)
    log(f"[build] wrote {out} ({out.stat().st_size / 2**30:.2f} GiB): {int(valid.sum())}/{n} valid, "
        f"{len(info['videos_failed'])} videos failed, {info['secs']} s")


# ------------------------------------------------------------------------------------------------------------- eval
def score_cache(bundle: dict, x: np.ndarray, valid: np.ndarray, batch: int, chunk: int = 2048) -> np.ndarray:
    """Softmax (N, 3) per model of the bundle -> (n_models, N, 3); rows with valid False stay NaN."""
    import torch
    cfg = bundle["config"] or DEFAULT_CFG
    for sect in ("input", "normalization"):
        if cfg.get(sect) != DEFAULT_CFG[sect]:
            raise RuntimeError(f"checkpoint {sect} {cfg.get(sect)} != cache contract {DEFAULT_CFG[sect]}")
    dev = bundle["device"]
    sigma = tuple(float(v) for v in cfg["input"]["marker_sigma"])
    marker = torch.from_numpy(_marker(CROP, sigma)).view(1, 1, *CROP).to(dev)
    models = bundle["models"]
    out = np.full((len(models), len(x), len(CLASSES)), np.nan, np.float32)
    rows = np.flatnonzero(valid)
    t0 = time.time()
    with torch.no_grad():
        for s in range(0, len(rows), chunk):
            r = rows[s:s + chunk]
            contiguous = r[-1] - r[0] + 1 == len(r)
            block = torch.from_numpy(np.asarray(x[r[0]:r[-1] + 1] if contiguous else x[r], dtype=np.float32))
            for b in range(0, len(r), batch):
                xb = block[b:b + batch].to(dev)
                xin = torch.cat([xb, marker.expand(xb.shape[0], 1, *CROP)], dim=1)
                for mi, m in enumerate(models):
                    out[mi, r[b:b + batch]] = torch.softmax(m(xin).float(), dim=1).cpu().numpy()
            done = min(s + chunk, len(rows))
            if done == len(rows) or (s // chunk) % 4 == 3:
                el = time.time() - t0
                log(f"[eval] scored {done}/{len(rows)} ({done / max(el, 1e-9):.0f} samples/s x {len(models)} models)")
    return out


def readout(meta, probs: np.ndarray, subsets: dict | None = None) -> dict:
    """Per embryo (+ all, + optional named row subsets: bool masks aligned with meta) and class: kdn_core._rank_block,
    plus the hard-negative AUCs of the kernel readout."""
    df = meta.assign(p_cont=probs[:, 0], p_par=probs[:, 1], p_dau=probs[:, 2])
    fin = np.isfinite(df["p_par"].to_numpy())
    extra = [(name, df[np.asarray(m, bool) & fin]) for name, m in (subsets or {}).items()]
    df = df[fin]
    col = {"cont": "p_cont", "parent": "p_par", "daughter": "p_dau"}
    res = {}
    for emb, g in [(e, g) for e, g in df.groupby("embryo")] + [("all", df)] + extra:
        block = {name: kdn_core._rank_block(g[col[name]].to_numpy(np.float64), (g["label"] == name).to_numpy())
                 for name in CLASSES}
        hu = g[g["kind"].str.startswith("hardneg") & g["kind"].str.contains("u")]
        hv = g[g["kind"].str.startswith("hardneg") & g["kind"].str.contains("v")]
        par, dau = g[g["label"] == "parent"], g[g["label"] == "daughter"]
        block["hard"] = {
            "n_hardneg_u": int(len(hu)), "n_hardneg_v": int(len(hv)),
            "auc_parent_vs_hardneg_u": kdn_core.auc_score(np.r_[par["p_par"], hu["p_par"]],
                                                          np.r_[np.ones(len(par)), np.zeros(len(hu))]),
            "auc_daughter_vs_hardneg_v": kdn_core.auc_score(np.r_[dau["p_dau"], hv["p_dau"]],
                                                            np.r_[np.ones(len(dau)), np.zeros(len(hv))]),
        }
        res[emb] = block
    return res


def _fmt(v, nd=3):
    return "   -  " if v is None else f"{v:.{nd}f}"


def print_readout(name: str, ro: dict) -> None:
    print(f"\n== {name}")
    print(f"{'embryo':6s} {'class':8s} {'n':>6s} {'n_pos':>5s} {'base':>6s} {'AUC':>6s} | "
          + " | ".join(f"{k:>7s} P / lift / LR+ (tp/k)" for k, _ in kdn_core.TOP_FRACS))
    for emb, block in ro.items():
        for cname in CLASSES:
            r = block[cname]
            parts = []
            for k, _ in kdn_core.TOP_FRACS:
                c = r.get(k)
                if not c:
                    parts.append(" " * 30)
                    continue
                lr = "inf" if c["lr_plus_infinite"] else _fmt(c["lr_plus"], 1)
                parts.append(f"{c['precision']:.3f} / {_fmt(c['lift'], 1):>5s} / {lr:>5s} ({c['tp']}/{c['k']})")
            print(f"{emb:6s} {cname:8s} {r['n']:6d} {r['n_pos']:5d} {_fmt(r['base_rate'], 4)} {_fmt(r['auc'])} | "
                  + " | ".join(f"{p:>30s}" for p in parts))
        h = block["hard"]
        print(f"{emb:6s} hard-neg AUC: parent vs hardneg_u {_fmt(h['auc_parent_vs_hardneg_u'])} (n_u {h['n_hardneg_u']}), "
              f"daughter vs hardneg_v {_fmt(h['auc_daughter_vs_hardneg_v'])} (n_v {h['n_hardneg_v']})")


def join_oof(meta, oof_path: Path):
    """Row positions in meta and the OOF probabilities aligned to them (join on stem + node_id, else coordinates)."""
    import pandas as pd
    oof = pd.read_csv(oof_path)
    missing = [c for c in ("stem", "t", "z", "y", "x", "label", *PROB_COLS) if c not in oof.columns]
    if missing:
        raise RuntimeError(f"{oof_path}: missing columns {missing}")
    oof = oof[oof["p_par"].notna()]
    left = meta.reset_index(drop=True).assign(_row=np.arange(len(meta)))
    if "node_id" in oof.columns:
        keys = ["stem", "node_id"]
    else:
        keys = ["stem", "t", "z", "y", "x"]
        for c in ("z", "y", "x"):
            left[c] = left[c].round(3)
            oof[c] = oof[c].round(3)
    extra = [c for c in ("fold", "p_divnet") if c in oof.columns]
    m = left.merge(oof[keys + ["label", *PROB_COLS, *extra]].rename(columns={"label": "label_oof", "fold": "fold_oof"}),
                   on=keys, how="inner")
    bad = m["label"] != m["label_oof"]
    info = {"oof_rows": int(len(oof)), "matched": int(len(m)), "label_mismatch": int(bad.sum()), "keys": keys,
            "cache_rows": int(len(meta))}
    m = m[~bad]
    if "fold_oof" in m.columns:
        info["fold_mismatch"] = int((m["fold_oof"] != m["fold"]).sum())
    return m, info


def dorado_overlap(meta, shard_names: list[str], reg_path: Path, shard_dir: Path, dt_max: int = 3) -> tuple:
    """Per eval row: 0 = no shared image content with the dorado shards (or not a 44b6 row), 1 = its footprint (frames
    t-1..t+2, pooled 16x32x32 crop) meets a dorado shard sample's footprint within dt_max frames, -1 = 44b6 clip not
    reliably registered (unknown). Returns (status int8 array, info dict)."""
    from scipy.spatial import cKDTree
    reg = json.loads(Path(reg_path).read_text())["clips"]
    st, sp, missing = [], [], []
    for name in shard_names:
        f = Path(shard_dir) / name
        if not f.is_file():
            missing.append(name)
            continue
        with np.load(f) as d:
            st.append(d["t"].astype(np.int64))
            sp.append(d["zyx"].astype(np.float64))
    status = np.zeros(len(meta), np.int8)
    is44 = (meta["embryo"] == "44b6").to_numpy()
    info = {"shards": shard_names, "missing_shards": missing, "dt_max": int(dt_max), "registration": str(reg_path)}
    if missing:
        status[is44] = -1
        info["note"] = "shards missing locally: every 44b6 row is unknown"
        return status, info
    S_t, S_p = np.concatenate(st), np.concatenate(sp)
    tree = cKDTree(S_p * VOXEL_UM)
    reach = 2 * CROP_HALF_VOX + OVERLAP_MARGIN_VOX
    radius = float(np.linalg.norm(reach * VOXEL_UM))
    stems, ts = meta["stem"].to_numpy(), meta["t"].to_numpy(np.int64)
    zyx = meta[["z", "y", "x"]].to_numpy(np.float64)
    for i in np.flatnonzero(is44):
        c = reg.get(stems[i])
        if not c or not c.get("reliable"):
            status[i] = -1
            continue
        e_t = ts[i] + int(c["o"])
        e_p = zyx[i] + np.asarray(c["shift_vox"], np.float64)
        cand = tree.query_ball_point(e_p * VOXEL_UM, r=radius)
        if cand:
            cand = np.asarray(cand)
            hit = (np.abs(S_t[cand] - e_t) <= dt_max) & np.all(np.abs(S_p[cand] - e_p) < reach, axis=1)
            status[i] = 1 if hit.any() else 0
    info.update({"n_44b6": int(is44.sum()), "overlap": int((status == 1).sum()), "unknown": int((status == -1).sum()),
                 "overlap_by_label": meta.loc[status == 1, "label"].value_counts().to_dict()})
    return status, info


def cmd_eval(a) -> None:
    import pandas as pd
    x, meta, cinfo = load_cache(Path(a.cache))
    valid = meta["valid"].to_numpy(bool).copy() if "valid" in meta else np.ones(len(meta), bool)
    if a.stems:
        want = {s.strip() for s in a.stems.split(",") if s.strip()}
        valid = valid & meta["stem"].isin(want).to_numpy()
    if a.embryo:
        valid = valid & meta["embryo"].isin(a.embryo).to_numpy()
    log(f"[eval] cache {a.cache}: {len(meta)} rows ({int(valid.sum())} scored), videos {meta['stem'].nunique()}, "
        f"built {cinfo.get('built')}; counts {cinfo.get('counts')}")
    ckpts = [Path(p) for p in a.ckpt]
    bundle = load_daughternet(ckpts, device=a.device if a.device != "auto" else None)
    per_model = score_cache(bundle, x, valid, a.batch)
    leak, seen_shards = {}, []
    for p in ckpts:
        tr = _load_cfg(p).get("train") or {}
        if tr.get("source") == "dorado":
            leak[str(p)] = {"kaggle_labels_used": tr.get("kaggle_labels_used"),
                            "kaggle44b6_leak_free": bool(tr.get("kaggle44b6_leak_free", False)),
                            "kaggle44b6_exclusion": tr.get("kaggle44b6_exclusion")}
            if not leak[str(p)]["kaggle44b6_leak_free"]:
                seen_shards += [n for n in tr.get("shards", []) if n not in seen_shards]
    subsets, overlap_info, status = {}, None, None
    if seen_shards:
        if Path(a.dorado_reg).is_file():
            status, overlap_info = dorado_overlap(meta, seen_shards, Path(a.dorado_reg), Path(a.dorado_shards),
                                                  a.overlap_dt)
            clean = valid & (status == 0)
            subsets = {"44b6_clean": clean & (meta["embryo"] == "44b6").to_numpy(), "all_clean": clean}
            log(f"[eval] 44b6 = crops of the dorado recording: {overlap_info.get('overlap')} of "
                f"{overlap_info.get('n_44b6')} 44b6 rows share image content with the dorado shards "
                f"{overlap_info.get('overlap_by_label')}, {overlap_info.get('unknown')} unknown (clip not registered); "
                f"'44b6_clean' / 'all_clean' leave both out. 6bba is independent.")
        else:
            log(f"[eval] WARNING: dorado checkpoint(s) without the 44b6 exclusion and no {a.dorado_reg}: the 44b6 and "
                f"'all' rows include images the model trained on (tools/register_44b6_dorado.py); judge on 6bba.")
    names = [p.stem for p in ckpts]
    if len(names) != len(set(names)):
        names = [f"{i}:{p.parent.name}/{p.stem}" for i, p in enumerate(ckpts)]
    results = {n: per_model[i] for i, n in enumerate(names)}
    if len(ckpts) > 1:
        results["ensemble_mean"] = per_model.mean(axis=0)
    report = {"cache": str(a.cache), "cache_info": {k: cinfo.get(k) for k in ("built", "n", "videos", "splits_source",
                                                                              "label_cfg", "counts", "pad_any_rate")},
              "checkpoints": [str(p) for p in ckpts],
              "checkpoint_train": [_load_cfg(p).get("train") for p in ckpts],
              "dorado_leak_status": leak, "dorado_overlap": overlap_info,
              "definitions": {"base_rate": "fraction of the embryo's labelled samples carrying the class (cont is "
                                           "subsampled: <= 60 random + 40 hard negatives per video)",
                              "precision": "class fraction among the top-k samples ranked by that class probability",
                              "lift": "precision / base_rate", "lr_plus": "TPR / FPR at the cutoff (null when fp = 0)",
                              "auc": "one-vs-rest ROC AUC of the class probability"},
              "models": {}, "oof_comparison": None}
    for n, p in results.items():
        ro = readout(meta[valid].reset_index(drop=True), p[valid], {k: v[valid] for k, v in subsets.items()})
        report["models"][n] = ro
        print_readout(f"{n} (all {int(valid.sum())} Kaggle GT samples, no Kaggle label used in training)", ro)

    if a.oof:
        sub_meta = meta[valid].reset_index(drop=True)
        m, jinfo = join_oof(sub_meta, Path(a.oof))
        rows = m["_row"].to_numpy()
        log(f"[eval] OOF join: {jinfo}")
        p_oof = m[list(PROB_COLS)].to_numpy(np.float32)
        mm = m.drop(columns=[*PROB_COLS]).reset_index(drop=True)
        comp = {"join": jinfo, "models": {}, "spearman": {}}
        sub_sets = {k: v[valid][rows] for k, v in subsets.items()}
        comp["models"]["kdn_oof"] = readout(mm, p_oof, sub_sets)
        print_readout(f"kdn-train OOF on the {len(m)} common rows (honest Kaggle folds)", comp["models"]["kdn_oof"])
        for n, p in results.items():
            pm = p[valid][rows]
            comp["models"][n] = readout(mm, pm, sub_sets)
            print_readout(f"{n} on the same {len(m)} rows", comp["models"][n])
            blend = 0.5 * (pm + p_oof)
            comp["models"][f"blend_{n}_oof"] = readout(mm, blend, sub_sets)
            print_readout(f"50/50 blend {n} + kdn OOF", comp["models"][f"blend_{n}_oof"])
            sp = {}
            for emb, g in [(e, g) for e, g in mm.groupby("embryo")] + [("all", mm)]:
                ix = g.index.to_numpy()
                sp[emb] = {c: float(pd.Series(pm[ix, i]).corr(pd.Series(p_oof[ix, i]), method="spearman"))
                           for i, c in enumerate(CLASSES)}
            comp["spearman"][n] = sp
            print(f"Spearman({n}, kdn OOF): " + "; ".join(
                f"{e}: " + " ".join(f"{c} {v:.3f}" for c, v in d.items()) for e, d in sp.items()))
        if "p_divnet" in mm.columns and mm["p_divnet"].notna().any():
            sub = mm[mm["label"].isin(["parent", "cont"])]
            comp["divnet_in_sample_parent_vs_cont_auc"] = {
                e: kdn_core.auc_score(g["p_divnet"].to_numpy(), (g["label"] == "parent").to_numpy())
                for e, g in [(e, g) for e, g in sub.groupby("embryo")] + [("all", sub)]}
            rounded = {k: None if v is None else round(v, 3)
                       for k, v in comp["divnet_in_sample_parent_vs_cont_auc"].items()}
            print(f"public DivNet (IN-SAMPLE, trained on these videos) parent-vs-cont AUC: {rounded}")
        report["oof_comparison"] = comp

    out_json = Path(a.out_json) if a.out_json else ckpts[0].with_name(ckpts[0].stem + ".kaggle_eval.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=1, default=kdn_core._json_default))
    log(f"[eval] wrote {out_json}")
    if a.out_csv:
        key = "ensemble_mean" if "ensemble_mean" in results else names[0]
        p = results[key]
        df = meta.assign(p_cont=p[:, 0], p_par=p[:, 1], p_dau=p[:, 2])
        if status is not None:
            df["dorado_overlap"] = status
        df = df[valid]
        cols = list(kdn_core.OOF_COLUMNS) + [c for c in ("node_id", "kind", "embryo", "label_idx", "pad_frac",
                                                         "dorado_overlap") if c in df]
        df[cols].to_csv(a.out_csv, index=False)
        log(f"[eval] wrote per-sample probabilities of {key} -> {a.out_csv} ({len(df)} rows, oof.csv layout; the fold "
            f"column is the splits.json fold, the model saw no Kaggle label)")


def _load_cfg(path: Path) -> dict:
    import torch
    payload = torch.load(Path(path), map_location="cpu", weights_only=False)
    return payload.get("config", {}) if isinstance(payload, dict) else {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="labels + DivNet-contract crops -> npz cache")
    b.add_argument("--data-dir", default=str(DEFAULT_DATA))
    b.add_argument("--out", default=str(DEFAULT_CACHE))
    b.add_argument("--stems", default="", help="comma-separated stems (default: all videos)")
    b.add_argument("--max-videos", type=int, default=0)
    b.add_argument("--splits", default="", help="splits.json (default experiments/l2_daughternet/splits.json)")
    b.add_argument("--cont-per-video", type=int, default=60)
    b.add_argument("--hardneg-per-video", type=int, default=40)
    b.add_argument("--cont-min-dist", type=int, default=2)
    b.add_argument("--seed", type=int, default=0)
    b.add_argument("--workers", type=int, default=0, help="crop processes (0 = min(8, cpu count))")
    b.add_argument("--contract-checks", type=int, default=2, help="exact contract checks per video")
    b.add_argument("--labels-only", action="store_true", help="label counts and padding statistics, no crops")
    e = sub.add_parser("eval", help="score checkpoints on the cache")
    e.add_argument("--cache", default=str(DEFAULT_CACHE))
    e.add_argument("--ckpt", nargs="+", required=True)
    e.add_argument("--oof", default="", help="kdn-train oof.csv for a like-for-like comparison")
    e.add_argument("--device", default="auto")
    e.add_argument("--batch", type=int, default=128)
    e.add_argument("--stems", default="", help="restrict to these stems")
    e.add_argument("--embryo", nargs="*", default=None, help="restrict to these embryos (44b6 / 6bba)")
    e.add_argument("--out-json", default="", help="default <first ckpt>.kaggle_eval.json")
    e.add_argument("--out-csv", default="", help="per-sample probabilities (ensemble if several) in oof.csv layout")
    e.add_argument("--dorado-reg", default=str(DORADO_REG), help="44b6 -> dorado registration (register_44b6_dorado.py)")
    e.add_argument("--dorado-shards", default=str(DORADO_SHARDS), help="local copies of the checkpoint's dorado shards")
    e.add_argument("--overlap-dt", type=int, default=3,
                   help="frames between a dorado sample and a 44b6 row that still count as shared image content (3 = "
                        "the lag windows t-1..t+2 intersect; larger = stricter)")
    a = ap.parse_args(argv)
    {"build": cmd_build, "eval": cmd_eval}[a.cmd](a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
