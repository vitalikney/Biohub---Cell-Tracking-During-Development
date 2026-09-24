#!/usr/bin/env python
"""Retrain x138's V1284 coordinate-refinement head on our own TRAIN-video capture, evaluate it held out, kill-test it.

    nice -n 19 python tools/train_coordhead.py --capture experiments/coordhead_retrain/captures \
        --out experiments/coordhead_retrain/out_full [--loss huber] [--epochs 60] [--export-dataset]

Input: the per-video capture files written by the kernels of experiments/coordhead_retrain/build_capture_kernel.py
(<stem>.npz: coords = x138's integer peaks [t, z, y, x] in the (1,4,4)-downsampled grid, features = x138's 224-d
sample_features at the edge-TTA-averaged primary UNet map, bit-exact to exp51's inference path; all peaks within 10 um
of a same-frame GT node + a 1 % random sample of all peaks + exact all-peak feature moments). --capture is repeatable
and searched recursively; a stem captured twice (pilot + full run) is compared (determinism) and kept once.

Conventions (identical to the head's use in the kernel): peak position in um = grid index * 1.625 on every axis (x138's
SPACING; the zarr is read with ::1, ::4, ::4 strides, so grid index j = full-resolution voxel 4j in y/x and the
pipeline outputs coords * (1, 4, 4)); GT (geff, full-resolution voxels) in um = (z, y, x) * (1.625, 0.40625, 0.40625).
The head outputs a shift in um through bounded() (norm < 2 um), which the kernel divides by SPACING.

Training pairs: per frame, Hungarian one-to-one matching of GT nodes to peaks on the um distance, pairs <= --match-um
(4 um). Target = gt - peak (um), norm clipped to --clip-um (1.99 < 2, the bounded() range), x --target-scale.
Features standardised by --norm (allpeaks: exact mean/std over ALL peaks of the training videos, from the capture's
moments = the distribution the head sees at inference; pairs: over the training pairs). Model = x138's make_head()
(Linear 224->32, SiLU, Linear 32->3, last layer zero-initialised) trained through x138's bounded() with Huber or MSE.

Evaluation (every method on the SAME held-out videos): none (no shift), public (anvithpothula/biohub-v1284-head-s075,
downloaded with `kaggle datasets download` if --public-head is missing), new (the fold's head), ridge (diagnostic only).
  fixed pairs   = the no-shift Hungarian pairs (<= 4 um); per method the distance of the same pairs after the shift:
                  mean / median distance, per-axis bias (gt - shifted peak, um), per-video wins
  re-matching   = per frame Hungarian of GT vs shifted peaks within 4 um and within 7 um: counts, share of GT nodes
  sample shifts = the method's shift on the random all-peak sample (mean |shift|, mean vector: embryo-bias check)
Folds: leak5 = the 5 leak-group folds of experiments/l2_daughternet/splits.json (OOF over all videos); embryo =
train 6bba -> test 44b6 and train 44b6 -> test 6bba. The public head was trained on ~20 of these train videos (x138's
validator: per embryo the first 10 stems, "has a GT division" first, then alphabetical), so every table is also
reported without those 20 (x138_probable_train), where the public head is out-of-sample.

KILL TEST (printed and stored in report.json): ship only if on BOTH embryo-held-out directions the new head's fixed-pair
mean distance <= (1 - 0.03) x the public head's AND its 7 um re-match count >= the public head's.

Output (--out): report.json (all tables), report.txt (the printed summary), v1284_head.pt (final head trained on ALL
captured videos, exactly the public file format: {'state_dict': {0.weight, 0.bias, 2.weight, 2.bias}, 'mean', 'scale'},
float32 CPU tensors, torch.save to a file named v1284_head.pt) + head_meta.json. --export-dataset (only if the kill test
passes, or with --force-export) also writes experiments/coordhead_retrain/dataset_coordhead_199/ (v1284_head.pt,
head_meta.json, dataset-metadata.json for the private Kaggle dataset vitaliineibauer/biohub-coordhead-199).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import time
from collections import OrderedDict, defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # kdn_core imports tools.daughternet
sys.path.insert(0, str(ROOT / "experiments/l2_daughternet/kdn_train"))
import kdn_core  # noqa: E402  (read_gt_geff: numpy/zstd zarr reader, zarr fallback)

GT_SCALE_UM = np.array([1.625, 0.40625, 0.40625], dtype=np.float64)
GRID_UM = 1.625
PUBLIC_HEAD_DATASET = "anvithpothula/biohub-v1284-head-s075"
PUBLIC_HEAD_SHA256 = "625a0d9340f48193f2ec294fc2d81c5bb3c03087eab78ef0ae998a9c4c7da00c"
DATASET_SLUG = "vitaliineibauer/biohub-coordhead-199"
BIG = 1e6


# ---------------------------------------------------------------------------------------------------------------------
# x138's head (v1284_coordinate_refinement.py, verbatim semantics)
# ---------------------------------------------------------------------------------------------------------------------
def make_head():
    import torch
    head = torch.nn.Sequential(torch.nn.Linear(224, 32), torch.nn.SiLU(), torch.nn.Linear(32, 3))
    torch.nn.init.zeros_(head[-1].weight)
    torch.nn.init.zeros_(head[-1].bias)
    return head


def bounded(head, x):
    import torch
    delta = head(x)
    return 2.0 * delta / (1.0 + torch.linalg.vector_norm(delta, dim=-1, keepdim=True))


class HeadPack:
    """A head + its standardisation, applied exactly like x138's refine (float32, (x - mean) / scale)."""

    def __init__(self, state_dict, mean, scale, name: str) -> None:
        import torch
        self.name = name
        self.head = make_head()
        self.head.load_state_dict(state_dict)
        self.head.eval()
        self.mean = torch.as_tensor(mean, dtype=torch.float32)
        self.scale = torch.as_tensor(scale, dtype=torch.float32)

    def shift_um(self, feats: np.ndarray) -> np.ndarray:
        import torch
        out = np.zeros((len(feats), 3), dtype=np.float64)
        with torch.no_grad():
            for i in range(0, len(feats), 65536):
                x = torch.from_numpy(np.ascontiguousarray(feats[i:i + 65536], dtype=np.float32))
                out[i:i + 65536] = bounded(self.head, (x - self.mean) / self.scale).numpy()
        return out

    @staticmethod
    def load(path: Path, name: str) -> "HeadPack":
        import torch
        saved = torch.load(str(path), map_location="cpu", weights_only=True)
        return HeadPack(saved["state_dict"], saved["mean"], saved["scale"], name)


# ---------------------------------------------------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------------------------------------------------
def load_captures(dirs: list[Path]) -> tuple[dict, dict]:
    """stem -> capture arrays; duplicates (same stem in two captures) are compared and the first one is kept."""
    caps: dict[str, dict] = {}
    dup = {}
    for d in dirs:
        for p in sorted(Path(d).rglob("*.npz")):
            with np.load(p) as z:
                if "features" not in z.files or "feat_sum" not in z.files:
                    continue
                rec = {k: z[k] for k in z.files}
            rec["path"] = str(p)
            stem = p.stem
            if stem in caps:
                a, b = caps[stem], rec
                same_coords = a["coords"].shape == b["coords"].shape and bool((a["coords"] == b["coords"]).all())
                diff = float(np.abs(a["features"] - b["features"]).max()) if same_coords else None
                dup[stem] = {"first": a["path"], "second": rec["path"], "coords_identical": same_coords,
                             "max_abs_feature_diff": diff, "n_all": [int(a["n_all"]), int(b["n_all"])]}
                continue
            caps[stem] = rec
    return caps, dup


def hungarian(frames_p: np.ndarray, pos: np.ndarray, gt_t: np.ndarray, gt_um: np.ndarray, radius: float):
    """Per-frame one-to-one matching (min total distance) of GT nodes to peaks within radius.
    Returns (peak_idx, gt_idx, dist) arrays."""
    out_p, out_g, out_d = [], [], []
    order_p = np.argsort(frames_p, kind="stable")
    fp = frames_p[order_p]
    order_g = np.argsort(gt_t, kind="stable")
    fg = gt_t[order_g]
    for t in np.unique(fg):
        gi = order_g[np.searchsorted(fg, t, "left"):np.searchsorted(fg, t, "right")]
        pi = order_p[np.searchsorted(fp, t, "left"):np.searchsorted(fp, t, "right")]
        if not len(pi):
            continue
        d = np.sqrt(((gt_um[gi][:, None, :] - pos[pi][None, :, :]) ** 2).sum(-1))
        cost = np.where(d <= radius, d, BIG)
        r, c = linear_sum_assignment(cost)
        ok = cost[r, c] < BIG
        out_g.append(gi[r[ok]])
        out_p.append(pi[c[ok]])
        out_d.append(d[r[ok], c[ok]])
    if not out_p:
        return np.zeros(0, np.int64), np.zeros(0, np.int64), np.zeros(0)
    return np.concatenate(out_p), np.concatenate(out_g), np.concatenate(out_d)


class Video:
    def __init__(self, stem: str, cap: dict, gt: dict, fold: int, match_um: float) -> None:
        self.stem = stem
        self.embryo = stem[:4]
        self.fold = fold
        coords = cap["coords"].astype(np.int64)
        self.frames = coords[:, 0]
        self.det_um = coords[:, 1:].astype(np.float64) * GRID_UM
        self.feats = cap["features"].astype(np.float32, copy=False)
        self.near = cap["near_gt"].astype(bool)
        self.sampled = cap["sampled"].astype(bool)
        self.n_all = int(cap["n_all"])
        self.feat_sum = cap["feat_sum"].astype(np.float64)
        self.feat_sumsq = cap["feat_sumsq"].astype(np.float64)
        captured = set(int(t) for t in cap["frame_t"])
        keep = np.isin(gt["t"], list(captured))
        self.gt_t = gt["t"][keep].astype(np.int64)
        self.gt_um = np.stack([gt["z"], gt["y"], gt["x"]], axis=1)[keep] * GT_SCALE_UM
        self.gt_nodes_total = int(len(gt["t"]))
        self.pair_p, self.pair_g, self.pair_d = hungarian(self.frames, self.det_um, self.gt_t, self.gt_um, match_um)

    def targets(self, clip_um: float, scale: float) -> np.ndarray:
        tgt = self.gt_um[self.pair_g] - self.det_um[self.pair_p]
        n = np.linalg.norm(tgt, axis=1, keepdims=True)
        tgt = np.where(n > clip_um, tgt * (clip_um / np.maximum(n, 1e-12)), tgt)
        return tgt * scale


def x138_probable_train(stems: list[str], divisions: dict) -> list[str]:
    """x138 validator order: per embryo prefix, stems with a GT division first, then alphabetical; first 10 each."""
    out = []
    for emb in ("44b6", "6bba"):
        s = sorted([x for x in stems if x.startswith(emb)], key=lambda x: (int(divisions.get(x, 0)) == 0, x))
        out += s[:10]
    return out


# ---------------------------------------------------------------------------------------------------------------------
# fitting
# ---------------------------------------------------------------------------------------------------------------------
def norm_stats(videos: list[Video], mode: str) -> tuple[np.ndarray, np.ndarray]:
    if mode == "allpeaks":
        n = sum(v.n_all for v in videos)
        s = sum(v.feat_sum for v in videos)
        ss = sum(v.feat_sumsq for v in videos)
        mean = s / n
        var = np.maximum(ss / n - mean * mean, 0.0)
    else:
        x = np.concatenate([v.feats[v.pair_p] for v in videos]).astype(np.float64)
        mean, var = x.mean(0), x.var(0)
    scale = np.sqrt(var)
    scale = np.where(scale > 1e-6, scale, 1.0)
    return mean.astype(np.float32), scale.astype(np.float32)


def train_data(videos: list[Video], args) -> tuple[np.ndarray, np.ndarray]:
    x = np.concatenate([v.feats[v.pair_p] for v in videos]).astype(np.float32)
    ys = [v.targets(args.clip_um, args.target_scale) for v in videos]
    if args.debias == "embryo":
        # remove each embryo's mean offset (annotation convention, e.g. 6bba dz ~ -0.85 um) so the head can only learn
        # what varies within an embryo; the clip stays applied first
        for emb in {v.embryo for v in videos}:
            idx = [i for i, v in enumerate(videos) if v.embryo == emb]
            m = np.concatenate([ys[i] for i in idx]).mean(0) if idx else 0.0
            for i in idx:
                ys[i] = ys[i] - m
    y = np.concatenate(ys).astype(np.float32)
    return x, y


def fit_head(videos: list[Video], args, seed: int, name: str) -> tuple[HeadPack, dict]:
    import torch
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    mean, scale = norm_stats(videos, args.norm)
    x, y = train_data(videos, args)
    xs = torch.from_numpy((x - mean) / scale)
    yt = torch.from_numpy(y)
    head = make_head()
    opt = torch.optim.AdamW(head.parameters(), lr=args.lr, weight_decay=args.wd)
    steps_per_epoch = max(1, math.ceil(len(xs) / args.batch))
    total_steps = args.epochs * steps_per_epoch
    if total_steps >= 50:
        sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=args.lr, total_steps=total_steps, pct_start=0.1)
    else:  # tiny plumbing runs: OneCycle needs a few steps per phase
        sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda step: 1.0)
    if args.loss == "huber":
        loss_fn = torch.nn.HuberLoss(delta=args.huber_delta)
    else:
        loss_fn = torch.nn.MSELoss()
    hist = []
    t0 = time.time()
    for ep in range(args.epochs):
        perm = torch.from_numpy(rng.permutation(len(xs)))
        tot = 0.0
        for i in range(0, len(xs), args.batch):
            idx = perm[i:i + args.batch]
            pred = bounded(head, xs[idx])
            loss = loss_fn(pred, yt[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
            sched.step()
            tot += float(loss.detach()) * len(idx)
        hist.append(tot / len(xs))
    head.eval()
    sd = OrderedDict((k, v.detach().cpu().contiguous().float()) for k, v in head.state_dict().items())
    info = {"n_pairs": int(len(xs)), "n_videos": len(videos), "train_loss_first": hist[0], "train_loss_last": hist[-1],
            "seconds": round(time.time() - t0, 1)}
    return HeadPack(sd, mean, scale, name), info


class Ridge:
    """Diagnostic comparator (x138's author reported ridge ~ MLP): closed-form ridge on standardised features,
    output norm-clipped to < 2 um. Not shippable in the head format."""

    def __init__(self, videos: list[Video], args) -> None:
        self.name = "ridge"
        self.mean, self.scale = norm_stats(videos, args.norm)
        x, y = train_data(videos, args)
        xs = np.concatenate([(x - self.mean) / self.scale, np.ones((len(x), 1), np.float32)], 1).astype(np.float64)
        reg = args.ridge_lambda * len(xs) * np.eye(xs.shape[1])
        reg[-1, -1] = 0.0
        self.w = np.linalg.solve(xs.T @ xs + reg, xs.T @ y.astype(np.float64))

    def shift_um(self, feats: np.ndarray) -> np.ndarray:
        xs = np.concatenate([(feats - self.mean) / self.scale, np.ones((len(feats), 1), np.float32)], 1)
        r = xs.astype(np.float64) @ self.w
        n = np.linalg.norm(r, axis=1, keepdims=True)
        return np.where(n > 1.99, r * (1.99 / np.maximum(n, 1e-12)), r)


class NoShift:
    name = "none"

    @staticmethod
    def shift_um(feats: np.ndarray) -> np.ndarray:
        return np.zeros((len(feats), 3))


# ---------------------------------------------------------------------------------------------------------------------
# evaluation
# ---------------------------------------------------------------------------------------------------------------------
def eval_video(v: Video, method) -> dict:
    shift = method.shift_um(v.feats)
    pos = v.det_um + shift
    r = {"n_gt": int(len(v.gt_t)), "n_pairs": int(len(v.pair_p))}
    res = v.gt_um[v.pair_g] - pos[v.pair_p]
    d = np.linalg.norm(res, axis=1)
    r["sum_d"] = float(d.sum())
    r["d"] = d
    r["sum_res"] = res.sum(0)
    r["sum_absres"] = np.abs(res).sum(0)
    for rad in (4.0, 7.0):
        _, _, dm = hungarian(v.frames, pos, v.gt_t, v.gt_um, rad)
        r[f"m{int(rad)}"] = int(len(dm))
        r[f"m{int(rad)}_sum_d"] = float(dm.sum())
    s = shift[v.sampled]
    r["n_sample"] = int(len(s))
    r["sample_sum_norm"] = float(np.linalg.norm(s, axis=1).sum())
    r["sample_ge1"] = int((np.linalg.norm(s, axis=1) >= 1.0).sum())
    r["sample_sum_vec"] = s.sum(0)
    return r


def aggregate(rows: list[dict]) -> dict:
    if not rows:
        return {}
    n_pairs = sum(r["n_pairs"] for r in rows)
    n_gt = sum(r["n_gt"] for r in rows)
    d = np.concatenate([r["d"] for r in rows]) if n_pairs else np.zeros(0)
    ns = max(sum(r["n_sample"] for r in rows), 1)
    out = {
        "videos": len(rows), "n_gt": n_gt, "fixed_pairs": n_pairs,
        "fixed_mean_um": float(d.mean()) if n_pairs else float("nan"),
        "fixed_median_um": float(np.median(d)) if n_pairs else float("nan"),
        "fixed_share_le1um": float((d <= 1.0).mean()) if n_pairs else float("nan"),
        "bias_zyx_um": [float(x) for x in sum(r["sum_res"] for r in rows) / max(n_pairs, 1)],
        "mae_zyx_um": [float(x) for x in sum(r["sum_absres"] for r in rows) / max(n_pairs, 1)],
        "match4": sum(r["m4"] for r in rows), "match7": sum(r["m7"] for r in rows),
        "share4": sum(r["m4"] for r in rows) / max(n_gt, 1), "share7": sum(r["m7"] for r in rows) / max(n_gt, 1),
        "match4_mean_um": sum(r["m4_sum_d"] for r in rows) / max(sum(r["m4"] for r in rows), 1),
        "sample_mean_shift_um": sum(r["sample_sum_norm"] for r in rows) / ns,
        "sample_share_ge1um": sum(r["sample_ge1"] for r in rows) / ns,
        "sample_mean_vec_zyx_um": [float(x) for x in sum(r["sample_sum_vec"] for r in rows) / ns],
    }
    return out


def evaluate(videos: list[Video], methods: list) -> dict:
    per_video = {m.name: {v.stem: eval_video(v, m) for v in videos} for m in methods}
    res = {"all": {}, "per_embryo": {}, "per_video_fixed_mean": {}}
    for m in methods:
        res["all"][m.name] = aggregate(list(per_video[m.name].values()))
        for emb in ("44b6", "6bba"):
            rows = [per_video[m.name][v.stem] for v in videos if v.embryo == emb]
            if rows:
                res["per_embryo"].setdefault(emb, {})[m.name] = aggregate(rows)
        res["per_video_fixed_mean"][m.name] = {
            s: (r["sum_d"] / r["n_pairs"] if r["n_pairs"] else None) for s, r in per_video[m.name].items()}
    names = [m.name for m in methods]
    if "new" in names and "public" in names:
        pv_new, pv_pub = res["per_video_fixed_mean"]["new"], res["per_video_fixed_mean"]["public"]
        common = [s for s in pv_new if pv_new[s] is not None and pv_pub[s] is not None]
        res["new_beats_public_videos"] = f"{sum(pv_new[s] < pv_pub[s] for s in common)}/{len(common)}"
    return res


def fmt_table(title: str, table: dict) -> str:
    lines = [title, f"  {'method':8s} {'videos':>6s} {'pairs':>7s} {'mean_um':>8s} {'med_um':>7s} {'<=1um':>6s} "
                    f"{'bias z/y/x um':>22s} {'m4':>7s} {'share4':>7s} {'m7':>7s} {'shift_um':>8s} {'>=1um':>6s}"]
    for name, a in table.items():
        if not a:
            continue
        b = a["bias_zyx_um"]
        lines.append(f"  {name:8s} {a['videos']:6d} {a['fixed_pairs']:7d} {a['fixed_mean_um']:8.4f} "
                     f"{a['fixed_median_um']:7.4f} {a['fixed_share_le1um']:6.3f} {b[0]:+7.3f}/{b[1]:+6.3f}/{b[2]:+6.3f} "
                     f"{a['match4']:7d} {a['share4']:7.4f} {a['match7']:7d} {a['sample_mean_shift_um']:8.4f} "
                     f"{a['sample_share_ge1um']:6.3f}")
    return "\n".join(lines)


def strip_arrays(obj):
    if isinstance(obj, dict):
        return {k: strip_arrays(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [strip_arrays(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    return obj


# ---------------------------------------------------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------------------------------------------------
def ensure_public_head(path: Path) -> Path:
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading {PUBLIC_HEAD_DATASET} -> {path.parent}", flush=True)
        subprocess.run([sys.executable, "-m", "kaggle", "datasets", "download", PUBLIC_HEAD_DATASET, "-p",
                        str(path.parent), "--unzip", "--force"], check=True)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != PUBLIC_HEAD_SHA256:
        raise SystemExit(f"public head sha256 {sha} != {PUBLIC_HEAD_SHA256}")
    return path


def save_head(pack: HeadPack, out_dir: Path) -> Path:
    """Exactly the public head's format: torch.save({'state_dict', 'mean', 'scale'}) to a file named v1284_head.pt."""
    import torch
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "v1284_head.pt"
    sd = OrderedDict((k, v.detach().cpu().contiguous().float().clone()) for k, v in pack.head.state_dict().items())
    torch.save({"state_dict": sd, "mean": pack.mean.detach().cpu().contiguous().float().clone(),
                "scale": pack.scale.detach().cpu().contiguous().float().clone()}, str(path))
    # re-load exactly like the kernel module (weights_only, make_head, load_state_dict) and check the file format
    saved = torch.load(str(path), map_location="cpu", weights_only=True)
    assert list(saved.keys()) == ["state_dict", "mean", "scale"], list(saved.keys())
    assert list(saved["state_dict"].keys()) == ["0.weight", "0.bias", "2.weight", "2.bias"]
    assert tuple(saved["state_dict"]["0.weight"].shape) == (32, 224) and tuple(saved["mean"].shape) == (224,)
    assert all(t.dtype == torch.float32 for t in [*saved["state_dict"].values(), saved["mean"], saved["scale"]])
    head = make_head()
    head.load_state_dict(saved["state_dict"])
    head.eval()
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--capture", action="append", required=True, help="capture folder (recursive), repeatable")
    ap.add_argument("--out", required=True)
    ap.add_argument("--data-dir", default=str(ROOT / "biohub-cell-tracking-during-development/train"))
    ap.add_argument("--splits", default=str(ROOT / "experiments/l2_daughternet/splits.json"))
    ap.add_argument("--public-head", default=str(ROOT / "experiments/coordhead_retrain/public_head/v1284_head.pt"))
    ap.add_argument("--match-um", type=float, default=4.0)
    ap.add_argument("--clip-um", type=float, default=1.99)
    ap.add_argument("--target-scale", type=float, default=1.0, help="shrink targets (x138's 's075' may be 0.75)")
    ap.add_argument("--norm", choices=["allpeaks", "pairs"], default="allpeaks")
    ap.add_argument("--debias", choices=["none", "embryo"], default="none",
                    help="embryo: subtract each embryo's mean target (no annotation-convention learning)")
    ap.add_argument("--loss", choices=["huber", "mse"], default="huber")
    ap.add_argument("--huber-delta", type=float, default=1.0)
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--batch", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--wd", type=float, default=1e-4)
    ap.add_argument("--ridge-lambda", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=20260924)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--kill-margin", type=float, default=0.03)
    ap.add_argument("--skip-leak5", action="store_true")
    ap.add_argument("--skip-embryo", action="store_true",
                    help="leak5 folds only (hyper-parameter selection without touching the kill-test folds; the kill "
                         "test then reports FAIL for lack of embryo folds)")
    ap.add_argument("--no-final", action="store_true", help="skip the all-video head (selection runs)")
    ap.add_argument("--export-dataset", action="store_true")
    ap.add_argument("--force-export", action="store_true")
    a = ap.parse_args()

    import torch
    torch.set_num_threads(a.threads)
    t_start = time.time()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    report_lines: list[str] = []

    def say(msg: str = "") -> None:
        print(msg, flush=True)
        report_lines.append(msg)

    caps, dup = load_captures([Path(c) for c in a.capture])
    if not caps:
        raise SystemExit("no capture files found")
    splits = json.loads(Path(a.splits).read_text())
    folds = splits["folds"]
    divisions = splits.get("divisions_per_video", {})
    videos = []
    for stem in sorted(caps):
        gt = kdn_core.read_gt_geff(Path(a.data_dir) / f"{stem}.geff")
        videos.append(Video(stem, caps[stem], gt, int(folds[stem]), a.match_um))
    x138_train = set(x138_probable_train(sorted(folds), divisions))
    say(f"capture: {len(videos)} videos ({sum(v.embryo == '44b6' for v in videos)} 44b6 / "
        f"{sum(v.embryo == '6bba' for v in videos)} 6bba), kept peaks {sum(len(v.frames) for v in videos)}, "
        f"all peaks {sum(v.n_all for v in videos)}, GT nodes {sum(len(v.gt_t) for v in videos)}, "
        f"pairs <= {a.match_um} um {sum(len(v.pair_p) for v in videos)} "
        f"(share {sum(len(v.pair_p) for v in videos) / max(sum(len(v.gt_t) for v in videos), 1):.4f})")
    if dup:
        worst = max((d["max_abs_feature_diff"] or 0.0) for d in dup.values())
        same = sum(d["coords_identical"] for d in dup.values())
        say(f"duplicate captures (determinism check): {len(dup)} stems, coords identical {same}/{len(dup)}, "
            f"max |feature diff| {worst:.3g}")
    missing = sorted(set(folds) - set(caps))
    if missing:
        say(f"NOTE: {len(missing)} of {len(folds)} train videos not captured")

    public = HeadPack.load(ensure_public_head(Path(a.public_head)), "public")
    # which standardisation did x138 use? compare its stored mean/scale with ours (all peaks vs pairs)
    m_all, s_all = norm_stats(videos, "allpeaks")
    m_pair, s_pair = norm_stats(videos, "pairs")
    pm, ps = public.mean.numpy(), public.scale.numpy()
    say(f"x138 mean/scale vs ours: |mean - allpeaks| {np.abs(pm - m_all).mean():.4f}, |mean - pairs| "
        f"{np.abs(pm - m_pair).mean():.4f}; scale ratio x138/allpeaks median {np.median(ps / s_all):.3f}, "
        f"x138/pairs median {np.median(ps / s_pair):.3f}")

    report = {"args": vars(a), "videos": [v.stem for v in videos], "duplicates": dup,
              "x138_probable_train": sorted(x138_train), "folds": {}}
    fold_defs = []
    if not a.skip_leak5:
        for f in range(5):
            fold_defs.append((f"leak5_f{f}", [v for v in videos if v.fold != f], [v for v in videos if v.fold == f]))
    if not a.skip_embryo:
        fold_defs.append(("emb_6bba_to_44b6", [v for v in videos if v.embryo == "6bba"],
                          [v for v in videos if v.embryo == "44b6"]))
        fold_defs.append(("emb_44b6_to_6bba", [v for v in videos if v.embryo == "44b6"],
                          [v for v in videos if v.embryo == "6bba"]))

    oof_rows = defaultdict(list)
    oof_rows_nox = defaultdict(list)
    for name, tr, te in fold_defs:
        if not tr or not te or not sum(len(v.pair_p) for v in tr):
            say(f"[{name}] skipped (train {len(tr)} / test {len(te)} videos)")
            continue
        new, info = fit_head(tr, a, a.seed, "new")
        methods = [NoShift(), public, new, Ridge(tr, a)]
        ev = evaluate(te, methods)
        te_nox = [v for v in te if v.stem not in x138_train]
        ev_nox = evaluate(te_nox, methods) if te_nox else None
        report["folds"][name] = {"train_videos": [v.stem for v in tr], "test_videos": [v.stem for v in te],
                                 "fit": info, "eval": strip_arrays(ev),
                                 "eval_without_x138_train": strip_arrays(ev_nox) if ev_nox else None}
        say()
        say(fmt_table(f"[{name}] train {len(tr)} videos / {info['n_pairs']} pairs (loss {info['train_loss_first']:.4f}"
                      f" -> {info['train_loss_last']:.4f}, {info['seconds']} s); held out {len(te)} videos; "
                      f"new beats public on {ev.get('new_beats_public_videos')} videos", ev["all"]))
        if ev_nox and len(te_nox) != len(te):
            say(fmt_table(f"  ... without the {len(te) - len(te_nox)} probable x138 training videos", ev_nox["all"]))
        if name.startswith("leak5"):
            for m in methods:
                oof_rows[m.name] += [eval_video(v, m) for v in te]
                oof_rows_nox[m.name] += [eval_video(v, m) for v in te_nox]
    if oof_rows:
        report["leak5_oof"] = strip_arrays({m: aggregate(r) for m, r in oof_rows.items()})
        report["leak5_oof_without_x138_train"] = strip_arrays({m: aggregate(r) for m, r in oof_rows_nox.items()})
        say()
        say(fmt_table("[leak5 OOF, all videos]", report["leak5_oof"]))
        say(fmt_table("[leak5 OOF, without probable x138 training videos]", report["leak5_oof_without_x138_train"]))

    # ---- kill test ----
    verdict = {"rule": f"on BOTH embryo-held-out directions: new fixed-pair mean distance <= (1 - {a.kill_margin}) x "
                       f"public AND new 7 um re-match count >= public", "directions": {}}
    ok_all = True
    for name in ("emb_6bba_to_44b6", "emb_44b6_to_6bba"):
        f = report["folds"].get(name)
        if not f:
            verdict["directions"][name] = {"pass": False, "reason": "fold not evaluated"}
            ok_all = False
            continue
        n, p = f["eval"]["all"]["new"], f["eval"]["all"]["public"]
        rel = n["fixed_mean_um"] / p["fixed_mean_um"] - 1.0
        d_pass = rel <= -a.kill_margin and n["match7"] >= p["match7"]
        f_nox = f.get("eval_without_x138_train")
        rel_nox = (f_nox["all"]["new"]["fixed_mean_um"] / f_nox["all"]["public"]["fixed_mean_um"] - 1.0) if f_nox else None
        verdict["directions"][name] = {
            "pass": bool(d_pass), "new_mean_um": n["fixed_mean_um"], "public_mean_um": p["fixed_mean_um"],
            "none_mean_um": f["eval"]["all"]["none"]["fixed_mean_um"], "rel_vs_public": rel,
            "match7_new": n["match7"], "match7_public": p["match7"], "match7_none": f["eval"]["all"]["none"]["match7"],
            "match4_new": n["match4"], "match4_public": p["match4"],
            "rel_vs_public_without_x138_train": rel_nox}
        ok_all &= bool(d_pass)
    verdict["pass"] = bool(ok_all)
    report["kill_test"] = verdict
    say()
    say("KILL TEST: " + verdict["rule"])
    for name, d in verdict["directions"].items():
        if "new_mean_um" in d:
            say(f"  {name}: new {d['new_mean_um']:.4f} vs public {d['public_mean_um']:.4f} um "
                f"({100 * d['rel_vs_public']:+.2f} %; none {d['none_mean_um']:.4f}); match7 new {d['match7_new']} vs "
                f"public {d['match7_public']} (none {d['match7_none']}) -> {'PASS' if d['pass'] else 'FAIL'}"
                + (f"; without x138 train {100 * d['rel_vs_public_without_x138_train']:+.2f} %"
                   if d["rel_vs_public_without_x138_train"] is not None else ""))
        else:
            say(f"  {name}: FAIL ({d['reason']})")
    for name in ("emb_6bba_to_44b6", "emb_44b6_to_6bba"):
        f = report["folds"].get(name)
        if f:
            vn = f["eval"]["all"]["new"]["sample_mean_vec_zyx_um"]
            vp = f["eval"]["all"]["public"]["sample_mean_vec_zyx_um"]
            gap = max(abs(x - y) for x, y in zip(vn, vp))
            verdict["directions"][name]["sample_mean_shift_new_zyx"] = vn
            verdict["directions"][name]["sample_mean_shift_public_zyx"] = vp
            say(f"  embryo-bias check {name}: mean shift on all-peak sample new "
                f"{'/'.join(f'{x:+.3f}' for x in vn)} vs public {'/'.join(f'{x:+.3f}' for x in vp)} um (z/y/x), "
                f"max gap {gap:.3f} um ({'ok' if gap <= 0.2 else 'WARN > 0.2 um: learns an embryo convention?'})")
    say(f"KILL TEST VERDICT: {'PASS - ship candidate' if verdict['pass'] else 'FAIL - do not ship'}")

    if a.no_final:
        report["seconds"] = round(time.time() - t_start, 1)
        (out / "report.json").write_text(json.dumps(strip_arrays(report), indent=1))
        (out / "report.txt").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        print(f"done (no final head) in {report['seconds']} s -> {out}", flush=True)
        return

    # ---- final head on all videos ----
    final, info = fit_head(videos, a, a.seed, "final")
    head_path = save_head(final, out)
    sha = hashlib.sha256(head_path.read_bytes()).hexdigest()
    ev_final_in = evaluate(videos, [NoShift(), public, final])
    meta = {"sha256": sha, "file": "v1284_head.pt", "format": "x138 V1284 (state_dict 0/2 Linear, mean, scale)",
            "trained_on": [v.stem for v in videos], "fit": info, "kill_test_pass": verdict["pass"],
            "args": vars(a), "in_sample_eval_all": strip_arrays(ev_final_in["all"]),
            "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tool": "tools/train_coordhead.py"}
    (out / "head_meta.json").write_text(json.dumps(meta, indent=1))
    report["final_head"] = {"path": str(head_path), "sha256": sha, "fit": info}
    say()
    say(f"final head (all {len(videos)} videos, {info['n_pairs']} pairs): {head_path} sha256 {sha[:16]}; "
        f"in-sample mean shift on the all-peak sample {ev_final_in['all']['final']['sample_mean_shift_um']:.3f} um "
        f"(public {ev_final_in['all']['public']['sample_mean_shift_um']:.3f} um)")
    if a.export_dataset:
        if verdict["pass"] or a.force_export:
            ds_dir = ROOT / "experiments/coordhead_retrain/dataset_coordhead_199"
            ds_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(head_path, ds_dir / "v1284_head.pt")
            shutil.copy(out / "head_meta.json", ds_dir / "head_meta.json")
            (ds_dir / "dataset-metadata.json").write_text(json.dumps(
                {"title": "biohub-coordhead-199", "id": DATASET_SLUG, "licenses": [{"name": "CC0-1.0"}]}, indent=1))
            say(f"dataset folder written: {ds_dir} (python -m kaggle datasets create -p {ds_dir} ; private by default)")
        else:
            say("dataset NOT exported: kill test failed (use --force-export to override)")
    report["seconds"] = round(time.time() - t_start, 1)
    (out / "report.json").write_text(json.dumps(strip_arrays(report), indent=1))
    (out / "report.txt").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"done in {report['seconds']} s -> {out}", flush=True)


if __name__ == "__main__":
    main()
