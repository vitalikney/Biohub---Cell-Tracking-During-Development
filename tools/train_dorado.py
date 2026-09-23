"""Train DaughterNet from scratch on the dorado pseudo-labelled shards (plan line L3); no Kaggle label is used.

Input: shards written by tools/dorado_crops.py extract (data_external/dorado/shards/b<block>_z<k>.npz): x (N,5,16,32,32)
float16 in the DivNet / DaughterNet contract (4 image lags + centre marker, real surroundings), y class index in
tools.daughternet.CLASSES order (cont, parent, daughter), zyx node voxel position, win_origin pooled origin of the
emulated 64x64x64 (pooled) Kaggle clip whose percentiles normalised the crop, block, hard, track, partner, win_ok.
Output: {'model_state', 'config'} loadable by tools.daughternet.load_daughternet (strict), + <out>.history.json.

Recipe: hold out --val-blocks (default 417, the last developmental block) for early stopping; AdamW lr 1e-3 wd 0.01,
3% linear warmup then cosine to 0 over --epochs (<= 40), batch 128, class-balanced sampler (each draw picks a class
uniformly, then a sample of it with replacement; epoch = number of training samples), label smoothing 0.1 (the
pseudo-labels are noisy), per-sample augmentation in this order:
  1. window padding: the image channels outside the sample's emulated Kaggle clip are zeroed (what
     divnet_infer._crop_with_padding gives for a node near a real clip border); bit-identical to
     tools.dorado_crops.apply_window_pad (re-implemented here as a mask from the window offset so the three Colab
     files are self-contained; the equality is tested locally). Applied per sample with probability --pad-prob.
     CHOICE (default --pad-prob auto): measured on the 17,143 Kaggle GT evaluation nodes (eval_daughternet.py build,
     all 199 videos) 60.6% of the contract crops touch a clip border (6bba 70%, 44b6 40%; mean padded fraction 0.314
     given padding); the emulated dorado windows touch the crop for 74.3% (b083_z1) / 77.4% (b083_z2) of the samples
     (0.328 given padding). Padding always would over-pad (~75% vs 61%), and p = 0.74 would under-pad (~0.56); auto
     sets p = min(1, 0.606 / touched fraction of the training split) (~0.8), so the padded fraction matches Kaggle
     while the amount per padded sample already matches. A number (e.g. 1 = always) overrides it. The validation
     set gets a fixed seeded mask with the same probability (deterministic across epochs).
  2. flips on z / y / x and a k*90 degree rotation in yx, applied identically to all 5 channels (marker included);
  3. intensity gain U(0.8, 1.2) on the 4 image channels, clipped back to the contract range [-0.5, 6].
Samples whose window failed the Kaggle-clip bounds (win_ok False) are dropped unless --keep-bad-windows.
KAGGLE 44b6 OVERLAP: the Kaggle 44b6 videos are space-time crops of the dorado recording itself (tools/
register_44b6_dorado.py places them -> data_external/dorado/kaggle44b6_in_dorado.json); 6bba is another embryo.
Default (--exclude-kaggle none): all dorado samples are used and config.train.kaggle44b6_leak_free is False; the
evaluator (tools/eval_daughternet.py eval) then reports '44b6_clean' / 'all_clean' blocks without the 44b6 rows whose
crop + lag frames meet a sample of this model's shards (all 8 shards: 304 of the 4,780 placed 44b6 rows, all cont;
21/26 parents and 42/52 daughters are clean, the rest sit in the 8 clips without a reliable placement), and 6bba in
full. Strict mode (--exclude-kaggle auto | PATH): every dorado sample whose footprint (lag frames t-1..t+2, 16x32x32
pooled crop) meets a placed 44b6 clip box (frames [o, o+99], 64x256x256 voxels, + a small margin) is dropped from train
AND val (39% of the 8 shards, 380 of 1,021 parents); config.train.kaggle44b6_leak_free is True only when every 44b6
clip has a reliable placement (63/71 now).
Validation metric (early stopping, best checkpoint): macro cross-entropy without smoothing (mean over classes of the
per-class mean CE) on the held-out blocks; per-class one-vs-rest AUC and hard-negative AUCs are printed each epoch.
If no shard of the validation blocks is present (smoke tests), a lineage-grouped random --val-frac holdout is used.

    python tools/train_dorado.py --shards data_external/dorado/shards --out data_external/l3/dorado_only.pt
    python -m tools.train_dorado --shards /content/shards --out /content/dorado_only.pt          (Colab, T4)
    python tools/train_dorado.py --shards data_external/dorado/shards/b083_z1.npz --max-per-shard 400 --epochs 1 ...
"""
from __future__ import annotations

import argparse
import copy
import glob
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:  # `python tools/train_dorado.py` (repo) or /content/tools/train_dorado.py (Colab)
    sys.path.insert(0, str(_ROOT))

from tools.daughternet import CLASSES, DEFAULT_CFG, build_model  # noqa: E402
from tools.divnet_infer import _marker  # noqa: E402

N_IMG = len(DEFAULT_CFG["input"]["image_lags"])                        # 4 image channels
CROP = (int(DEFAULT_CFG["input"]["crop_z"]), int(DEFAULT_CFG["input"]["crop_yx"]), int(DEFAULT_CFG["input"]["crop_yx"]))
POOL = int(DEFAULT_CFG["input"]["pool_xy"])
WIN = (64, 64, 64)                                                     # pooled Kaggle clip (64 x 256/4 x 256/4)
CLIP = tuple(float(v) for v in DEFAULT_CFG["normalization"]["clip"])
KAGGLE_PAD_RATE = 0.606          # Kaggle GT eval nodes whose contract crop touches a clip border (17,143 nodes)
DORADO_PAD_RATE = 0.743          # dorado samples whose emulated window pads the crop (b083_z1)
DEFAULT_PAD_PROB = "auto"        # KAGGLE_PAD_RATE / touched fraction of the training split (~0.8)
LAGS = tuple(int(v) for v in DEFAULT_CFG["input"]["image_lags"])
KAGGLE44_FILE = "kaggle44b6_in_dorado.json"   # tools/register_44b6_dorado.py output
KAGGLE_CLIP_VOX = (64, 256, 256)                # Kaggle clip (z, y, x) in full-resolution voxels
KAGGLE_CLIP_T = 100
KAGGLE_MARGIN_VOX = (2, 8, 8)                   # registration slack (shift is refined to ~0.5 um)
KAGGLE_MARGIN_T = 1


def log(*a) -> None:
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ------------------------------------------------------------------------------------------------------------- shards
def find_shards(specs: list[str]) -> list[Path]:
    """Each spec: a .npz file, a directory (all b*_z*.npz in it) or a glob pattern. Sorted, de-duplicated."""
    out: list[Path] = []
    for s in specs:
        p = Path(s)
        if p.is_dir():
            out += sorted(p.glob("b*_z*.npz"))
        elif p.is_file():
            out.append(p)
        else:
            out += [Path(q) for q in sorted(glob.glob(s))]
    out = [p for p in dict.fromkeys(q.resolve() for q in out) if not p.name.endswith(".tmp.npz")]
    if not out:
        raise FileNotFoundError(f"no shard found for {specs}")
    seen: dict[str, Path] = {}
    for p in out:  # two copies of one (block, z-chunk) shard would double its weight (or repeat val samples)
        if p.name in seen:
            raise RuntimeError(f"shard {p.name} given twice: {seen[p.name]} and {p}")
        seen[p.name] = p
    return out


def window_offsets(zyx: np.ndarray, win_origin: np.ndarray) -> np.ndarray:
    """(N, 3) int: start of the sample's normalisation window in crop coordinates (dorado_crops.window_pad_mask's
    rel_lo): window origin minus the crop corner, with the same python round-half-even centre rounding."""
    z = np.asarray(zyx, np.float64)
    centre = np.stack([np.round(z[:, 0]), np.round(z[:, 1] / POOL), np.round(z[:, 2] / POOL)], axis=1).astype(np.int64)
    return np.asarray(win_origin, np.int64) - (centre - np.array(CROP) // 2)


def find_kaggle_exclusion(spec: str, shard_specs: list[str], paths: list[Path]) -> Path | None:
    """'none' -> None; a path -> that file; 'auto' -> KAGGLE44_FILE in a shard directory or its parent (as given and
    resolved), else None."""
    if spec == "none":
        return None
    if spec != "auto":
        p = Path(spec)
        if not p.is_file():
            raise FileNotFoundError(f"--exclude-kaggle {spec}: no such file")
        return p
    dirs: list[Path] = []
    for s in shard_specs:
        d = Path(s) if Path(s).is_dir() else Path(s).parent
        dirs += [d, d.parent]
    for p in paths:
        dirs += [p.parent, p.parent.parent]
    return next((d / KAGGLE44_FILE for d in dict.fromkeys(dirs) if (d / KAGGLE44_FILE).is_file()), None)


def load_kaggle_clips(path: Path) -> tuple[list[dict], list[str]]:
    """44b6 clips to exclude (every PLACED clip, reliable or not: a wrong placement only drops extra dorado data) and
    the names of the clips without a reliable placement (their 44b6 rows cannot be called leak-free)."""
    d = json.loads(Path(path).read_text())
    clips = [{"stem": s, "o": int(c["o"]), "shift_vox": [float(v) for v in c["shift_vox"]]}
             for s, c in sorted(d["clips"].items()) if c.get("placed")]
    bad = sorted(s for s, c in d["clips"].items() if not c.get("reliable"))
    return clips, bad


def kaggle_overlap(t: np.ndarray, zyx: np.ndarray, clips: list[dict]) -> np.ndarray:
    """(N,) bool: the sample's image footprint (frames t+min(lag) .. t+max(lag), its pooled 16x32x32 crop in
    full-resolution voxels) intersects a registered Kaggle clip (frames [o, o+99], voxels [shift, shift + clip)) grown
    by the registration margin."""
    t = np.asarray(t, np.int64)
    z = np.asarray(zyx, np.float64).reshape(-1, 3)
    hit = np.zeros(len(t), bool)
    if not clips or not len(t):
        return hit
    centre = np.stack([np.round(z[:, 0]), np.round(z[:, 1] / POOL), np.round(z[:, 2] / POOL)], axis=1)
    unit = np.array([1, POOL, POOL])
    lo = (centre - np.array(CROP) // 2) * unit
    hi = lo + np.array(CROP) * unit
    t_lo, t_hi = t + min(LAGS), t + max(LAGS)
    margin = np.array(KAGGLE_MARGIN_VOX)
    for c in clips:
        o, sh = c["o"], np.array(c["shift_vox"])
        tin = (t_hi >= o - KAGGLE_MARGIN_T) & (t_lo <= o + KAGGLE_CLIP_T - 1 + KAGGLE_MARGIN_T)
        sin = np.all((hi > sh - margin) & (lo < sh + np.array(KAGGLE_CLIP_VOX) + margin), axis=1)
        hit |= tin & sin
    return hit


def pad_mask(rel_lo: torch.Tensor) -> torch.Tensor:
    """(B, 3) window offsets -> (B, 1, 16, 32, 32) bool, True = inside the emulated clip (kept)."""
    dev = rel_lo.device
    parts = []
    for ax, (size, w) in enumerate(zip(CROP, WIN)):
        i = torch.arange(size, device=dev)[None, :]
        lo = rel_lo[:, ax:ax + 1]
        parts.append((i >= lo) & (i < lo + w))
    return (parts[0][:, None, :, None, None] & parts[1][:, None, None, :, None] & parts[2][:, None, None, None, :])


def load_shards(paths: list[Path], max_per_shard: int = 0, keep_bad_windows: bool = False, seed: int = 0,
                kaggle_clips: list[dict] | None = None) -> dict:
    """Concatenate shards: x (N, 4, 16, 32, 32) float16 image channels (the marker is re-added at batch time), labels
    and the metadata needed for window padding, hold-out and readout."""
    mk = _marker(CROP, tuple(float(v) for v in DEFAULT_CFG["input"]["marker_sigma"]))
    rng = np.random.default_rng(seed)
    cols: dict[str, list] = {k: [] for k in ("x", "y", "rel_lo", "block", "zchunk", "hard", "group", "shard")}
    infos = []
    for si, p in enumerate(paths):
        t0 = time.time()
        with np.load(p) as d:
            info = json.loads(str(d["info"]))
            if tuple(info.get("classes", CLASSES)) != tuple(CLASSES):
                raise RuntimeError(f"{p.name}: class order {info.get('classes')} != {CLASSES}")
            if (tuple(info["crop"]) != CROP or tuple(info["window"]) != WIN or int(info["pool"]) != POOL
                    or len(info["lags"]) != N_IMG or tuple(info["clip"]) != CLIP):
                raise RuntimeError(f"{p.name}: geometry {info['crop']} {info['window']} {info['pool']} {info['lags']} "
                                   f"does not match the DaughterNet contract")
            y = d["y"].astype(np.int64)
            n = len(y)
            keep = np.ones(n, bool) if keep_bad_windows or "win_ok" not in d.files else d["win_ok"].astype(bool)
            n_bad_window = int(n - keep.sum())
            kag = kaggle_overlap(d["t"], d["zyx"], kaggle_clips or []) & keep
            keep &= ~kag
            idx = np.flatnonzero(keep)
            if max_per_shard and len(idx) > max_per_shard:  # stratified subset (smoke tests)
                sel = []
                for c in range(len(CLASSES)):
                    ic = idx[y[idx] == c]
                    k = int(round(max_per_shard * len(ic) / len(idx)))
                    sel.append(rng.choice(ic, min(len(ic), max(k, 1 if len(ic) else 0)), replace=False))
                idx = np.sort(np.concatenate(sel))
            x = d["x"]
            if x.shape[1:] != (N_IMG + 1, *CROP):
                raise RuntimeError(f"{p.name}: x shape {x.shape}")
            if n and float(np.abs(x[0, N_IMG].astype(np.float32) - mk).max()) > 1e-3:
                raise RuntimeError(f"{p.name}: channel {N_IMG} is not the contract centre marker")
            cols["x"].append(np.ascontiguousarray(x[idx, :N_IMG]).astype(np.float16, copy=False))
            del x
            cols["y"].append(y[idx])
            cols["rel_lo"].append(window_offsets(d["zyx"][idx], d["win_origin"][idx]))
            cols["block"].append(np.full(len(idx), int(info["block"]), np.int64))
            cols["zchunk"].append(np.full(len(idx), int(info["zchunk"]), np.int64))
            cols["hard"].append(d["hard"][idx].astype(bool))
            # lineage group for the random fallback hold-out: a daughter joins its parent's track
            track, partner = d["track"][idx].astype(np.int64), d["partner"][idx].astype(np.int64)
            grp = np.where(y[idx] == CLASSES.index("daughter"), partner, track)
            cols["group"].append(grp + (int(info["block"]) << 32))
            cols["shard"].append(np.full(len(idx), si, np.int64))
            info["n_used"] = int(len(idx))
            info["n_dropped_bad_window"] = n_bad_window
            info["n_dropped_kaggle44b6"] = int(kag.sum())
            info["dropped_kaggle44b6_counts"] = np.bincount(y[kag], minlength=len(CLASSES)).tolist()
            info["path"] = str(p)
            if info.get("window_pad"):
                log(f"WARNING {p.name}: window padding is baked in (--window-pad); --pad-prob has no effect on it")
            infos.append(info)
        log(f"shard {p.name}: {len(idx)}/{n} samples {np.bincount(cols['y'][-1], minlength=3).tolist()} "
            f"(dropped: bad windows {infos[-1]['n_dropped_bad_window']}, inside Kaggle 44b6 clips "
            f"{infos[-1]['n_dropped_kaggle44b6']} {infos[-1]['dropped_kaggle44b6_counts']}) in {time.time() - t0:.1f}s")
    data = {k: np.concatenate(v) for k, v in cols.items()}
    data["infos"] = infos
    return data


def split_train_val(data: dict, val_blocks: list[int], val_frac: float,
                    seed: int) -> tuple[np.ndarray, np.ndarray, str]:
    blocks = data["block"]
    val = np.isin(blocks, val_blocks)
    if val.any() and (~val).any():
        return np.flatnonzero(~val), np.flatnonzero(val), f"blocks {sorted(set(blocks[val].tolist()))}"
    # fallback: lineage-grouped random hold-out (parent and its daughters together)
    groups = np.unique(data["group"])
    rng = np.random.default_rng(seed + 17)
    held = set(rng.choice(groups, max(1, int(round(val_frac * len(groups)))), replace=False).tolist())
    val = np.array([g in held for g in data["group"]])
    return (np.flatnonzero(~val), np.flatnonzero(val),
            f"random lineage-grouped {val_frac:.0%} (no shard of blocks {val_blocks} present)")


# ------------------------------------------------------------------------------------------------------------ metrics
def auc_score(scores, positive) -> float | None:
    s = np.asarray(scores, np.float64)
    y = np.asarray(positive, bool)
    n1, n0 = int(y.sum()), int((~y).sum())
    if n1 == 0 or n0 == 0:
        return None
    order = np.argsort(s, kind="mergesort")
    _, inv, cnt = np.unique(s[order], return_inverse=True, return_counts=True)
    avg = np.cumsum(cnt) - (cnt - 1) / 2.0                             # 1-based average rank of each tie group
    ranks = np.empty(len(s))
    ranks[order] = avg[inv]
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def val_metrics(probs: np.ndarray, y: np.ndarray, hard: np.ndarray) -> dict:
    p_true = np.clip(probs[np.arange(len(y)), y], 1e-7, 1.0)
    ce = -np.log(p_true)
    present = [c for c in range(len(CLASSES)) if (y == c).any()]
    nan = float("nan")
    res = {"n": int(len(y)), "macro_ce": float(np.mean([ce[y == c].mean() for c in present])) if present else nan,
           "ce": float(ce.mean()) if len(y) else nan,
           "acc": float((probs.argmax(1) == y).mean()) if len(y) else None}
    for c, name in enumerate(CLASSES):
        res[f"n_{name}"] = int((y == c).sum())
        res[f"auc_{name}"] = auc_score(probs[:, c], y == c)
    hn = hard & (y == 0)
    for c, name in ((1, "parent"), (2, "daughter")):
        m = (y == c) | hn
        res[f"auc_{name}_vs_hard"] = auc_score(probs[m, c], y[m] == c)
    return res


# ------------------------------------------------------------------------------------------------------------- model
def augment(xb: torch.Tensor, rel_lo: torch.Tensor, pad_on: torch.Tensor, marker: torch.Tensor,
            rng: np.random.Generator, gain: tuple[float, float]) -> torch.Tensor:
    """(B, 4, 16, 32, 32) image crops -> (B, 5, 16, 32, 32) float32: window padding (where pad_on), marker, flips
    z/y/x, yx rot90 (all 5 channels identically), gain on the image channels, clip to the contract range."""
    b = xb.shape[0]
    dev = xb.device
    x = xb.float()
    if bool(pad_on.any()):
        keep = pad_mask(rel_lo) | ~pad_on.view(b, 1, 1, 1, 1)
        x = x * keep
    x = torch.cat([x, marker.expand(b, 1, *CROP)], dim=1)
    flips = torch.from_numpy(rng.random((b, 3)) < 0.5).to(dev)
    for axis, dim in enumerate((2, 3, 4)):
        x = torch.where(flips[:, axis].view(b, 1, 1, 1, 1), x.flip(dim), x)
    rot = rng.integers(0, 4, size=b)
    for k in (1, 2, 3):
        sel = np.flatnonzero(rot == k)
        if len(sel):
            idx = torch.from_numpy(sel).to(dev)
            x[idx] = torch.rot90(x[idx], k, dims=(3, 4))
    g = torch.from_numpy(rng.uniform(gain[0], gain[1], size=(b, 1, 1, 1, 1)).astype(np.float32)).to(dev)
    x[:, :N_IMG] = (x[:, :N_IMG] * g).clamp(CLIP[0], CLIP[1])
    return x


@torch.no_grad()
def predict(model, x_img: torch.Tensor, rel_lo: torch.Tensor, pad_on: torch.Tensor, marker: torch.Tensor,
            batch: int, amp: bool) -> np.ndarray:
    model.eval()
    out = []
    for s in range(0, x_img.shape[0], batch):
        xb = x_img[s:s + batch].float()
        po = pad_on[s:s + batch]
        if bool(po.any()):
            xb = xb * (pad_mask(rel_lo[s:s + batch]) | ~po.view(-1, 1, 1, 1, 1))
        x = torch.cat([xb, marker.expand(xb.shape[0], 1, *CROP)], dim=1)
        with torch.autocast(device_type=x.device.type, dtype=torch.float16, enabled=amp):
            logits = model(x)
        out.append(torch.softmax(logits.float(), dim=1).cpu().numpy())
    return np.concatenate(out) if out else np.zeros((0, len(CLASSES)), np.float32)


def _atomic_save(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    torch.save(obj, tmp)
    os.replace(tmp, path)


def train(args) -> dict:
    t_start = time.time()
    device = torch.device(args.device if args.device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu"))
    use_cuda = device.type == "cuda"
    amp = use_cuda and not args.no_amp
    if use_cuda:
        torch.backends.cudnn.benchmark = True
    if args.threads:
        torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    gpu = f" ({torch.cuda.get_device_name(0)})" if use_cuda else ""
    log(f"device {device}{gpu} amp={amp} torch {torch.__version__}")

    paths = find_shards(args.shards)
    kag_path = find_kaggle_exclusion(args.exclude_kaggle, args.shards, paths)
    kag_clips, kag_bad = load_kaggle_clips(kag_path) if kag_path else ([], [])
    leak_free = bool(kag_path) and not kag_bad
    if kag_path is None:
        if args.exclude_kaggle == "auto":
            log(f"WARNING: --exclude-kaggle auto found no {KAGGLE44_FILE}: nothing excluded")
        log("note: Kaggle 44b6 videos are crops of this recording; without --exclude-kaggle the 44b6 metrics must be read "
            "on the evaluator's '44b6_clean' rows (6bba is independent)")
    else:
        log(f"Kaggle 44b6 exclusion: {kag_path} ({len(kag_clips)} registered clips"
            + (f"; no reliable placement: {kag_bad} -> 44b6 only partly leak-free" if kag_bad else "") + ")")
    data = load_shards(paths, args.max_per_shard, args.keep_bad_windows, args.seed, kag_clips)
    tr, va, val_desc = split_train_val(data, args.val_blocks, args.val_frac, args.seed)
    y = data["y"]
    log(f"{len(paths)} shards, {len(y)} samples {np.bincount(y, minlength=3).tolist()} (cont/parent/daughter); "
        f"train {len(tr)} {np.bincount(y[tr], minlength=3).tolist()} | val {len(va)} "
        f"{np.bincount(y[va], minlength=3).tolist()} ({val_desc})")
    if len(tr) == 0 or len(va) == 0:
        raise RuntimeError("empty train or validation split")
    store = torch.float16
    t0 = time.time()
    x_tr = torch.from_numpy(data["x"][tr]).to(device=device, dtype=store)
    x_va = torch.from_numpy(data["x"][va]).to(device=device, dtype=store)
    data["x"] = None                                                   # free the host copy
    rel_tr = torch.from_numpy(data["rel_lo"][tr]).to(device)
    rel_va = torch.from_numpy(data["rel_lo"][va]).to(device)
    y_tr = torch.from_numpy(y[tr]).to(device)
    y_va = y[va]
    hard_va = data["hard"][va]
    log(f"tensors on {device} in {time.time() - t0:.1f}s: train {tuple(x_tr.shape)} {x_tr.dtype}, "
        f"val {tuple(x_va.shape)}")
    # padding: fraction of training samples whose crop pokes out of its window -> pad probability
    rel = data["rel_lo"][tr]
    touched = float(((rel > 0) | (rel + np.array(WIN) < np.array(CROP))).any(1).mean())
    pad_mode = "auto" if str(args.pad_prob) == "auto" else "fixed"
    pad_prob = min(1.0, KAGGLE_PAD_RATE / max(touched, 1e-9)) if pad_mode == "auto" else float(args.pad_prob)
    log(f"window padding: {touched:.3f} of the training samples touch their window border (Kaggle GT nodes "
        f"{KAGGLE_PAD_RATE}); pad prob {pad_prob:.3f} ({pad_mode}) -> expected padded fraction {pad_prob * touched:.3f}")
    val_pad_on = torch.from_numpy(np.random.default_rng(args.seed + 99).random(len(va)) < pad_prob).to(device)
    marker = torch.from_numpy(_marker(CROP, tuple(float(v) for v in DEFAULT_CFG["input"]["marker_sigma"]))).view(
        1, 1, *CROP).to(device)

    cfg = copy.deepcopy(DEFAULT_CFG)
    cfg["classes"] = list(CLASSES)
    cfg["train"] = {"source": "dorado", "script": "tools/train_dorado.py", "shards": [p.name for p in paths],
                    "val": val_desc, "val_blocks": list(args.val_blocks), "epochs": args.epochs, "batch": args.batch,
                    "lr": args.lr, "weight_decay": args.weight_decay, "warmup_frac": args.warmup_frac,
                    "label_smoothing": args.label_smoothing, "pad_prob": pad_prob, "pad_prob_mode": pad_mode,
                    "train_touched_fraction": touched, "kaggle_pad_rate": KAGGLE_PAD_RATE, "gain": list(args.gain),
                    "patience": args.patience, "seed": args.seed, "epoch_samples": args.epoch_samples,
                    "max_per_shard": args.max_per_shard, "keep_bad_windows": args.keep_bad_windows,
                    "n_train": int(len(tr)), "n_val": int(len(va)),
                    "train_counts": np.bincount(y[tr], minlength=3).tolist(),
                    "val_counts": np.bincount(y_va, minlength=3).tolist(), "kaggle_labels_used": False,
                    "kaggle44b6_exclusion": None if kag_path is None else {
                        "file": kag_path.name, "clips": len(kag_clips), "clips_unreliable": kag_bad,
                        "dropped": int(sum(i["n_dropped_kaggle44b6"] for i in data["infos"])),
                        "dropped_counts": np.sum([i["dropped_kaggle44b6_counts"] for i in data["infos"]], 0).tolist()},
                    "kaggle44b6_leak_free": leak_free}
    model = build_model(cfg).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    y_tr_np = y[tr]
    classes_present = [c for c in range(len(CLASSES)) if (y_tr_np == c).any()]
    pools = {c: np.flatnonzero(y_tr_np == c) for c in classes_present}
    epoch_samples = int(args.epoch_samples) or len(tr)
    steps_per_epoch = max(1, math.ceil(epoch_samples / args.batch))
    total_steps = steps_per_epoch * int(args.epochs)
    warmup = max(1, int(args.warmup_frac * total_steps))

    def lr_at(step: int) -> float:
        if step < warmup:
            return args.lr * (step + 1) / warmup
        prog = (step - warmup) / max(1, total_steps - warmup)
        return args.lr * 0.5 * (1.0 + math.cos(math.pi * min(1.0, prog)))

    try:
        scaler = torch.amp.GradScaler("cuda", enabled=amp)
    except Exception:  # older torch
        scaler = torch.cuda.amp.GradScaler(enabled=amp)
    out = Path(args.out)
    hist_path = out.with_name(out.stem + ".history.json")
    best, best_epoch, bad, step = float("inf"), -1, 0, 0
    history = []
    for epoch in range(int(args.epochs)):
        te = time.time()
        model.train()
        cls = rng.choice(classes_present, size=epoch_samples)
        order = np.empty(epoch_samples, np.int64)
        for c in classes_present:
            sel = np.flatnonzero(cls == c)
            order[sel] = rng.choice(pools[c], size=len(sel), replace=True)
        rng.shuffle(order)
        run_loss, seen = torch.zeros((), device=device), 0
        for s in range(0, epoch_samples, args.batch):
            idx = torch.from_numpy(order[s:s + args.batch]).to(device)
            b = len(idx)
            pad_on = torch.from_numpy(rng.random(b) < pad_prob).to(device)
            xb = augment(x_tr[idx], rel_tr[idx], pad_on, marker, rng, tuple(args.gain))
            yb = y_tr[idx]
            for g in opt.param_groups:
                g["lr"] = lr_at(step)
            opt.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=amp):
                logits = model(xb)
            loss = torch.nn.functional.cross_entropy(logits.float(), yb, label_smoothing=args.label_smoothing)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            run_loss += loss.detach() * b
            seen += b
            step += 1
        if use_cuda:
            torch.cuda.synchronize()
        train_loss = float(run_loss) / max(1, seen)
        train_secs = time.time() - te
        probs = predict(model, x_va, rel_va, val_pad_on, marker, args.eval_batch, amp)
        vm = val_metrics(probs, y_va, hard_va)
        val_loss = vm["macro_ce"]
        improved = bool(np.isfinite(val_loss) and val_loss < best)
        if improved:
            best, best_epoch, bad = val_loss, epoch, 0
            cfg["train"].update({"best_epoch": epoch, "best_val_macro_ce": float(val_loss),
                                 "best_val_metrics": {k: v for k, v in vm.items()}})
            _atomic_save({"model_state": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                          "config": copy.deepcopy(cfg)}, out)
        else:
            bad += 1
        if args.save_last:
            _atomic_save({"model_state": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                          "config": copy.deepcopy(cfg), "epoch": epoch}, out.with_name(out.stem + ".last.pt"))
        rec = {"epoch": epoch, "train_loss_smoothed": train_loss, "val_macro_ce": val_loss, "lr": lr_at(step - 1),
               "secs": round(time.time() - te, 1), "train_samples_per_s": round(seen / max(1e-9, train_secs), 1),
               **{f"val_{k}": v for k, v in vm.items()}}
        history.append(rec)
        hist_path.write_text(json.dumps(history, indent=1))
        f = lambda v: "n/a" if v is None else f"{v:.3f}"  # noqa: E731
        log(f"epoch {epoch:2d}: train {train_loss:.4f} | val macro CE {val_loss:.4f}{' *' if improved else '  '} "
            f"AUC cont {f(vm['auc_cont'])} parent {f(vm['auc_parent'])} daughter {f(vm['auc_daughter'])} | "
            f"vs hard: parent {f(vm['auc_parent_vs_hard'])} daughter {f(vm['auc_daughter_vs_hard'])} | "
            f"lr {rec['lr']:.2e} {rec['secs']}s ({rec['train_samples_per_s']} samples/s)")
        if bad >= args.patience:
            log(f"early stop at epoch {epoch} (best epoch {best_epoch}, val macro CE {best:.4f})")
            break
    if best_epoch < 0:
        raise RuntimeError("no finite validation loss: no checkpoint written")
    summary = {"out": str(out), "best_epoch": best_epoch, "best_val_macro_ce": best, "epochs_run": len(history),
               "secs": round(time.time() - t_start, 1), "device": str(device),
               "best_val_metrics": cfg["train"]["best_val_metrics"]}
    log(f"best epoch {best_epoch} val macro CE {best:.4f} -> {out}; history {hist_path}; total {summary['secs']}s")
    return summary


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--shards", nargs="+", default=[str(_ROOT / "data_external" / "dorado" / "shards")],
                    help="shard files, directories (b*_z*.npz inside) or glob patterns")
    ap.add_argument("--out", default=str(_ROOT / "data_external" / "l3" / "dorado_only.pt"))
    ap.add_argument("--val-blocks", type=int, nargs="*", default=[417])
    ap.add_argument("--val-frac", type=float, default=0.15, help="fallback hold-out when no val-block shard exists")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--eval-batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=0.01)
    ap.add_argument("--warmup-frac", type=float, default=0.03)
    ap.add_argument("--label-smoothing", type=float, default=0.1)
    ap.add_argument("--pad-prob", default=DEFAULT_PAD_PROB,
                    help="probability of the Kaggle clip-border padding per sample: 'auto' (match the Kaggle padded "
                         "fraction 0.606) or a number in [0, 1] (1 = always)")
    ap.add_argument("--gain", type=float, nargs=2, default=[0.8, 1.2])
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--epoch-samples", type=int, default=0, help="draws per epoch (0 = number of training samples)")
    ap.add_argument("--max-per-shard", type=int, default=0, help="stratified subset per shard (smoke tests)")
    ap.add_argument("--keep-bad-windows", action="store_true", help="keep samples with win_ok False")
    ap.add_argument("--exclude-kaggle", default="none",
                    help=f"strict mode: drop dorado samples inside the registered Kaggle 44b6 clips: a path, 'auto' "
                         f"({KAGGLE44_FILE} next to the shards or in their parent dir), or 'none' (default: use all "
                         f"samples; the evaluator reports overlap-free 44b6 rows)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="auto", help="auto | cpu | cuda | cuda:N")
    ap.add_argument("--threads", type=int, default=0, help="torch CPU threads (0 = default)")
    ap.add_argument("--no-amp", action="store_true")
    ap.add_argument("--save-last", action="store_true", help="also write <out>.last.pt every epoch")
    a = ap.parse_args(argv)
    if a.pad_prob != "auto":
        try:
            a.pad_prob = float(a.pad_prob)
        except ValueError:
            ap.error("--pad-prob must be 'auto' or a number in [0, 1]")
        if not 0.0 <= a.pad_prob <= 1.0:
            ap.error("--pad-prob must be 'auto' or a number in [0, 1]")
    if a.epochs < 1:
        ap.error("--epochs must be >= 1")
    return a


def main(argv=None) -> int:
    train(parse_args(argv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
