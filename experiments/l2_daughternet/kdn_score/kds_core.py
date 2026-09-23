"""K-DS: score every exported L2 candidate node with the K-DN DaughterNet fold models (OOF or 5-fold ensemble).

One module shared by the Kaggle kernel kdn-score.ipynb (materialised with %%writefile under /kaggle/working/kds_src next
to kdn_core.py, tools/divnet_infer.py, tools/daughternet.py and splits.json) and by the laptop test test_local.py.

Modes (env KDS_ENSEMBLE)
  0    (default) oof   every row of coords_exp39.parquet is scored by the model of its video's fold, i.e. the fold model
                       that never trained on that video                        -> node_p_oof.parquet
  1              ens   softmax averaged over all fold models (what the submission kernel does) -> node_p_ens.parquet
  both           one joint pass: every fold model runs once per sample; oof = the video's fold model's softmax, ens
                 = their mean (the frames are read and prepared once for both outputs)
Output: columns stem, node_id, fold, p_cont, p_par, p_dau (softmax in tools.daughternet.CLASSES order), one row per
selected input row IN INPUT ORDER (all 1,012,255 rows unless a smoke/debug selection is set), NaN where a video has no
model or failed, plus node_p_<mode>_summary.json (rows per fold, NaN count, timing, checks, verification).
In ens mode `fold` is still the video's split fold (for reference); p averages all fold models, including the ones that
trained on that video.

Pipeline (run)
  discover  fold_k/best.pt under /kaggle/input (pruned walk that never enters *.zarr / *.geff; only best.pt files whose
            path has a fold_k directory), the coords parquet (dataset vitaliineibauer/biohub-l2-coords), the trainer's
            splits_used.json (falls back to the embedded experiments/l2_daughternet/splits.json per video); the same
            file seen under two mounts (/kaggle/input/<slug>/ and /kaggle/input/notebooks/<owner>/<slug>/) counts once;
            fold models must come from one trainer run whose n_folds matches the routing splits
  audit     OOF honesty, independent of the routing: a video whose fold model trained on it or on a video of its leak
            group (splits.json meta.leak_groups) gets no OOF prediction (NaN, listed in the summary)
  plan      videos -> worker processes (one per GPU, CUDA_VISIBLE_DEVICES 0 / 1), greedy on rows x models + frames;
            a video is scheduled for the modes whose part is missing (a partial rerun redoes only what is missing)
  worker    per video: each needed frame is read once (kdn_core.FrameReader) and prepared exactly like the DivNet contract
            (_pool_xy + _normalise with the checkpoint config) by a thread pool that also prefetches the next video;
            samples are cropped from the prepared frames with the contract's own _crop_with_padding and _marker; batches
            of KDS_BATCH go to the GPU (fp32 unless KDS_AMP=1) and the CPU crop of batch k+1 overlaps the GPU pass of
            batch k; the result is written to parts/<mode>/<stem>.parquet (atomic; a rerun skips valid parts, parts
            are wiped when the checkpoints / coords / folds / amp signature changes)
  merge     parts -> node_p_<mode>.parquet aligned to the input rows on (stem, node_id)
  verify    a few rows per fold re-scored from raw frames through tools.daughternet.score_nodes on CPU -> max |dp|
Contract guard: in every video KDS_CHECKS_FRESH samples are rebuilt by tools.daughternet.prepare_sample from raw frames
and KDS_CHECKS_CACHED from the shared prepared frames; any difference from the fast-path sample aborts the worker.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np


def _bootstrap_paths() -> list[str]:
    """Make tools/ (divnet_infer, daughternet) and kdn_core importable in the repo layout and in the kernel layout."""
    here = Path(__file__).resolve().parent
    paths = [here]
    for base in (here, *here.parents):
        if (base / "tools" / "daughternet.py").is_file():
            paths.append(base)
            break
    for cand in (here / "kdn_core.py", here.parent / "kdn_train" / "kdn_core.py"):
        if cand.is_file():
            paths.append(cand.parent)
            break
    out = list(dict.fromkeys(str(p) for p in paths))
    for p in reversed(out):
        if p not in sys.path:
            sys.path.insert(0, p)
    return out


SRC_PATHS = _bootstrap_paths()

import kdn_core  # noqa: E402
from kdn_core import FrameReader, decoder_names, load_splits, log, resolve_data_dir  # noqa: E402
from tools.daughternet import CLASSES, load_daughternet, prepare_sample, score_nodes  # noqa: E402
from tools.divnet_infer import _crop_with_padding, _marker, _normalise, _pool_xy  # noqa: E402

KERNEL = "biohub-l2-kdn-score"
P_COLUMNS = ["p_cont", "p_par", "p_dau"]
OUT_COLUMNS = ["stem", "node_id", "fold", *P_COLUMNS]
OUTPUTS = {"oof": "node_p_oof.parquet", "ens": "node_p_ens.parquet"}
PRUNE_SUFFIXES = (".zarr", ".geff")
FOLD_DIR_RE = re.compile(r"fold_(\d+)")
FRAME_COST_ROWS = 100      # planning weight: one prepared frame ~ the GPU time of 100 samples
if tuple(CLASSES) != ("cont", "parent", "daughter"):
    raise RuntimeError(f"tools.daughternet.CLASSES changed to {CLASSES}: update P_COLUMNS")


class ContractError(RuntimeError):
    """Fast-path sample differs from tools.daughternet.prepare_sample: never write predictions from it."""


# ----------------------------------------------------------------------------------------------------------------------
# configuration
# ----------------------------------------------------------------------------------------------------------------------
def _env_flag(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip() not in ("", "0", "false", "False", "no")


def parse_modes(value: str) -> list[str]:
    v = str(value).strip().lower()
    if v in ("", "0", "false", "no", "oof"):
        return ["oof"]
    if v in ("1", "true", "yes", "ens", "ensemble"):
        return ["ens"]
    if v in ("both", "2", "oof+ens", "all"):
        return ["oof", "ens"]
    raise ValueError(f"KDS_ENSEMBLE={value!r}: use 0 (oof), 1 (ensemble) or both")


def config_from_env(overrides: dict | None = None) -> dict:
    env = os.environ.get
    smoke = _env_flag("KDS_SMOKE")
    on_kaggle = Path("/kaggle/working").exists()
    cfg = {
        "smoke": smoke,
        "modes": parse_modes(env("KDS_ENSEMBLE", "0")),
        "data_dir": env("KDS_DATA_DIR", ""),                   # competition train dir (default: kdn_core rule)
        "work_dir": env("KDS_WORK_DIR", "/kaggle/working" if on_kaggle else str(Path.cwd() / "kds_out")),
        "input_root": env("KDS_INPUT_ROOT", "/kaggle/input"),
        "ckpt_root": env("KDS_CKPT_ROOT", ""),                 # where to look for fold_k/best.pt (default input_root)
        "ckpt_name": env("KDS_CKPT_NAME", "best.pt"),
        "train_slug": env("KDS_TRAIN_SLUG", "biohub-l2-kdn-train"),
        "coords": env("KDS_COORDS", ""),                       # explicit parquet path
        "coords_name": env("KDS_COORDS_NAME", "coords_exp39.parquet"),
        "coords_slug": env("KDS_COORDS_SLUG", "biohub-l2-coords"),
        "splits": env("KDS_SPLITS", ""),                       # explicit splits file (else trainer splits_used.json)
        "stems": [s.strip() for s in env("KDS_STEMS", "").split(",") if s.strip()],
        "max_videos": int(env("KDS_MAX_VIDEOS", "3" if smoke else "0") or 0),
        "rows_per_video": int(env("KDS_ROWS_PER_VIDEO", "300" if smoke else "0") or 0),
        "seed": int(env("KDS_SEED", "0")),
        "batch": int(env("KDS_BATCH", "512")),
        "pad_to": int(env("KDS_PAD_TO", "64")),                # last batch of a video padded -> few cuDNN shapes
        "amp": _env_flag("KDS_AMP", "0"),                      # fp16 autocast (faster, |dp| ~1e-3 vs score_nodes)
        "gpus": int(env("KDS_GPUS", "-1")),                    # -1 = all visible, 0 = CPU
        "workers": int(env("KDS_WORKERS", "0")),               # 0 = one per GPU (max 2), 1 on CPU
        "max_gpu_workers": int(env("KDS_MAX_GPU_WORKERS", "2")),
        "frame_threads": int(env("KDS_FRAME_THREADS", "2")),   # per worker; 0 = prepare frames inline
        "checks_fresh": int(env("KDS_CHECKS_FRESH", "1")),     # per video, contract sample rebuilt from raw frames
        "checks_cached": int(env("KDS_CHECKS_CACHED", "2")),   # per video, contract sample from the shared frames
        "verify_per_fold": int(env("KDS_VERIFY_PER_FOLD", "3")),
        "verify_tol": float(env("KDS_VERIFY_TOL", "0") or 0),  # 0 = auto: 1e-4 fp32 (GPU vs CPU), 2e-2 amp
        "expect_folds": int(env("KDS_EXPECT_FOLDS", "5")),
        "retries": int(env("KDS_RETRIES", "1")),
        "resume": _env_flag("KDS_RESUME", "1"),
    }
    if overrides:
        cfg.update(overrides)
    if isinstance(cfg.get("modes"), str):
        cfg["modes"] = parse_modes(cfg["modes"])
    return cfg


# ----------------------------------------------------------------------------------------------------------------------
# discovery
# ----------------------------------------------------------------------------------------------------------------------
def pruned_walk(root: Path, max_depth: int = 8):
    """os.walk that never descends into *.zarr / *.geff (the competition chunk trees), hidden dirs or __pycache__."""
    root = Path(root)
    if not root.exists():
        return
    for dirpath, dirnames, filenames in os.walk(root, followlinks=True):
        depth = len(Path(dirpath).relative_to(root).parts)
        if depth >= max_depth:
            dirnames[:] = []
        else:
            dirnames[:] = sorted(d for d in dirnames if not d.endswith(PRUNE_SUFFIXES) and not d.startswith(".")
                                 and d != "__pycache__")
        yield Path(dirpath), filenames


def find_files(root: Path, name: str, max_depth: int = 8) -> list[Path]:
    return [d / name for d, files in pruned_walk(root, max_depth) if name in files]


def _file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def code_shas() -> dict[str, str]:
    """sha256 of the code that determines the scores (part signature: a code change never reuses stale parts)."""
    import tools.daughternet as _dn
    import tools.divnet_infer as _dv

    out = {}
    for name, f in (("kds_core.py", __file__), ("daughternet.py", _dn.__file__), ("divnet_infer.py", _dv.__file__),
                    ("kdn_core.py", kdn_core.__file__)):
        try:
            out[name] = _file_sha(Path(f))
        except Exception:
            out[name] = "?"
    return out


def fold_of_path(path: Path) -> int | None:
    """k of the innermost fold_k directory of the path (the file name itself is ignored)."""
    ks = [int(m.group(1)) for part in Path(path).parts[:-1] for m in [FOLD_DIR_RE.fullmatch(part)] if m]
    return ks[-1] if ks else None


def dedupe_same_file(paths) -> list[Path]:
    """One path per distinct file. The same attached output can be visible under two mount points (legacy
    /kaggle/input/<slug>/... and /kaggle/input/notebooks/<owner>/<slug>/..., or a symlink between them): paths with the
    same real path or the same content collapse to the shortest (then lexicographically first) one, so every fold picks
    its file from the same mount."""
    ordered = sorted((Path(p) for p in paths), key=lambda q: (len(q.parts), str(q)))
    by_real: dict[str, Path] = {}
    for p in ordered:
        by_real.setdefault(os.path.realpath(p), p)
    out = list(by_real.values())
    if len(out) > 1:
        by_sha: dict[str, Path] = {}
        for p in out:
            by_sha.setdefault(_file_sha(p), p)
        out = list(by_sha.values())
    return out


def discover_checkpoints(root: Path, name: str = "best.pt", prefer: str = "") -> dict[int, Path]:
    root = Path(root)
    by_fold: dict[int, list[Path]] = {}
    for p in find_files(root, name):
        k = fold_of_path(p.relative_to(root))
        if k is not None:
            by_fold.setdefault(k, []).append(p)
    ckpts = {}
    for k, paths in sorted(by_fold.items()):
        paths = dedupe_same_file(paths)
        if len(paths) > 1 and prefer:
            paths = [p for p in paths if prefer in str(p)] or paths
        if len(paths) > 1:
            raise RuntimeError(f"fold {k}: {len(paths)} different checkpoints {[str(p) for p in paths]}; set "
                               "KDS_CKPT_ROOT to the one trainer output to use")
        ckpts[k] = paths[0]
    # the fold models must come from ONE trainer run (folds/ dir): mixing runs breaks the video -> fold routing
    runs = sorted({str(p.parent.parent) for p in ckpts.values()})
    if len(runs) > 1:
        raise RuntimeError(f"fold checkpoints come from {len(runs)} different trainer outputs {runs}; set "
                           "KDS_CKPT_ROOT to the one trainer output to use")
    return ckpts


def inspect_checkpoints(ckpts: dict[int, Path]) -> dict[int, dict]:
    """Validate every fold checkpoint (fold id, classes, identical input contract) and record provenance."""
    import torch

    info, contracts = {}, {}
    for k, p in sorted(ckpts.items()):
        payload = torch.load(Path(p), map_location="cpu", weights_only=False)
        if not isinstance(payload, dict) or "model_state" not in payload:
            raise RuntimeError(f"{p}: not a K-DN checkpoint (dict with model_state)")
        cfg = payload.get("config") or {}
        if "fold" in payload and int(payload["fold"]) != int(k):
            raise RuntimeError(f"{p}: payload fold {payload['fold']} != directory fold_{k}")
        if cfg.get("classes") is not None and list(cfg["classes"]) != list(CLASSES):
            raise RuntimeError(f"{p}: classes {cfg['classes']} != {list(CLASSES)}")
        contracts[k] = json.dumps({key: cfg.get(key) for key in ("input", "normalization", "model")}, sort_keys=True)
        train = cfg.get("train") or {}
        if train.get("fold") is not None and int(train["fold"]) != int(k):
            raise RuntimeError(f"{p}: config.train.fold {train['fold']} != directory fold_{k}")
        info[k] = {"path": str(p), "fold": int(k), "epoch": payload.get("epoch"), "val_loss": payload.get("val_loss"),
                   "sha256": _file_sha(Path(p)), "bytes": Path(p).stat().st_size,
                   "early_stop_fold": train.get("early_stop_fold"), "n_folds": train.get("n_folds"),
                   "inner_val": train.get("inner_val")}
    if len(set(contracts.values())) > 1:
        raise RuntimeError(f"fold checkpoints disagree on the input contract: {contracts}")
    return info


def _embedded_splits_path() -> Path | None:
    here = Path(__file__).resolve().parent
    for p in (here / "splits.json", here.parent / "splits.json"):
        if p.is_file():
            return p
    return None


def resolve_splits(cfg: dict, ckpt_paths: list[Path], input_root: Path, return_sources: bool = False):
    """Video -> fold: the trainer's splits_used.json wins (it is what the fold models were trained with); videos it does
    not list fall back to the embedded splits.json. return_sources=True also returns the (primary, fallback) maps."""
    primary_path = None
    if cfg.get("splits"):
        primary_path = Path(cfg["splits"])
        if not primary_path.is_file():
            raise FileNotFoundError(f"KDS_SPLITS={primary_path} does not exist")
    else:
        cands = []
        for p in ckpt_paths:  # trainer layout: <work>/folds/fold_k/best.pt and <work>/splits_used.json
            for up in list(Path(p).parents)[:4]:
                if (up / "splits_used.json").is_file():
                    cands.append(up / "splits_used.json")
                    break
        cands = dedupe_same_file(dict.fromkeys(cands)) or dedupe_same_file(find_files(input_root, "splits_used.json"))
        if len(cands) > 1:
            cands = [c for c in cands if cfg["train_slug"] in str(c)] or cands
        if len(cands) > 1:
            raise RuntimeError(f"several different splits_used.json {[str(c) for c in cands]}; set KDS_SPLITS")
        primary_path = cands[0] if cands else None
    primary = load_splits(primary_path) if primary_path else None
    emb_path = _embedded_splits_path()
    fallback = load_splits(emb_path) if emb_path else None
    folds: dict[str, int] = dict(fallback or {})
    folds.update(primary or {})
    if not folds:
        raise RuntimeError("no splits: neither a trainer splits_used.json nor the embedded splits.json")
    disagree = sorted(s for s in (primary or {}) if fallback and s in fallback and fallback[s] != primary[s])
    info = {"primary": str(primary_path) if primary_path else None, "n_primary": len(primary or {}),
            "fallback": str(emb_path) if emb_path else None, "n_fallback": len(fallback or {}),
            "fallback_only": sorted(set(fallback or {}) - set(primary or {})) if primary else [],
            "disagreements_primary_vs_fallback": disagree}
    if primary_path:
        try:
            meta = json.loads(Path(primary_path).read_text())
            info["primary_source"] = meta.get("source") if isinstance(meta, dict) else None
            info["primary_n_folds"] = meta.get("n_folds") if isinstance(meta, dict) else None
        except Exception:
            pass
    if return_sources:
        return folds, info, primary, fallback
    return folds, info


def leak_groups(path: Path | None) -> list[list[str]]:
    """splits.json meta.leak_groups: videos that share GT annotations (overlapping space-time crops of 44b6)."""
    try:
        meta = json.loads(Path(path).read_text()).get("meta") or {}
        return [[str(s) for s in g] for g in (meta.get("leak_groups") or [])]
    except Exception:
        return []


def audit_oof_routing(video_fold: dict[str, int], ckpt_info: dict[int, dict], primary: dict[str, int] | None,
                      fallback: dict[str, int] | None, groups: list[list[str]]) -> dict:
    """Honest-OOF audit, independent of the routing itself. Fold model k trained on every video of the trainer's splits
    (splits_used.json; the embedded splits.json if the trainer's file is missing) whose fold is not k. A video v routed
    to model k = video_fold[v] is EXCLUDED (no OOF prediction, NaN) when model k trained on v or on any video of v's
    leak group (videos sharing GT annotations). Also flags folds whose best.pt epoch was selected on the OOF fold's own
    labels (trainer KDN_INNER_VAL=0: early_stop_fold == fold), a mild optimism the scorer cannot remove."""
    basis = dict(primary) if primary else dict(fallback or {})
    sib: dict[str, set] = {}
    for g in groups:
        for s in g:
            sib.setdefault(s, set()).update(g)
    excluded, n_checked = {}, 0
    for v, k in video_fold.items():
        if k not in ckpt_info:
            continue
        n_checked += 1
        seen = sorted(s for s in sib.get(v, set()) | {v} if s in basis and int(basis[s]) != int(k))
        if seen:
            excluded[v] = {"fold": int(k), "model_trained_on": seen}
    return {"basis": "splits_used.json" if primary else "embedded splits.json (trainer splits_used.json not found)",
            "videos_checked": n_checked, "leak_groups": len(groups),
            "videos_in_leak_groups": int(sum(1 for v in video_fold if v in sib)),
            "excluded": excluded,
            "early_stop_on_oof_fold": sorted(int(k) for k, v in ckpt_info.items()
                                             if v.get("early_stop_fold") is not None
                                             and int(v["early_stop_fold"]) == int(k))}


def find_coords(cfg: dict, input_root: Path) -> Path:
    if cfg.get("coords"):
        p = Path(cfg["coords"])
        if not p.is_file():
            raise FileNotFoundError(f"KDS_COORDS={p} does not exist")
        return p
    cands = find_files(input_root, cfg["coords_name"])
    if len(cands) > 1:
        cands = [c for c in cands if cfg["coords_slug"] in str(c)] or cands
    if len(cands) > 1 and len({_file_sha(c) for c in cands}) > 1:
        raise RuntimeError(f"several different {cfg['coords_name']}: {[str(c) for c in cands]}; set KDS_COORDS")
    if cands:
        return cands[0]
    local = Path(__file__).resolve().parent.parent / cfg["coords_name"]  # repo: experiments/l2_daughternet/
    if local.is_file():
        return local
    raise FileNotFoundError(f"{cfg['coords_name']} not found under {input_root} (attach vitaliineibauer/biohub-l2-coords)")


def read_coords(path: Path):
    import pandas as pd

    df = pd.read_parquet(path, columns=["stem", "node_id", "t", "z", "y", "x"])
    df["stem"] = df["stem"].astype(str)
    if df.duplicated(["stem", "node_id"]).any():
        raise RuntimeError(f"{path}: (stem, node_id) is not unique")
    return df


def select_rows(coords, cfg: dict):
    """Rows to score, in input order (index = input position). Default: every row. KDS_STEMS / KDS_MAX_VIDEOS /
    KDS_ROWS_PER_VIDEO (seeded per video) are for smoke runs and tests; workers call this with the same cfg."""
    stems_all = list(dict.fromkeys(coords["stem"].tolist()))
    stems = stems_all
    if cfg.get("stems"):
        wanted = set(cfg["stems"])
        stems = [s for s in stems_all if s in wanted]
    elif cfg.get("max_videos") and cfg["max_videos"] < len(stems_all):
        srt = sorted(stems_all)
        step = len(srt) / cfg["max_videos"]
        pick = {srt[int(i * step)] for i in range(cfg["max_videos"])}
        stems = [s for s in stems_all if s in pick]
    sel = coords if len(stems) == len(stems_all) else coords[coords["stem"].isin(stems)]
    rpv = int(cfg.get("rows_per_video") or 0)
    if rpv > 0:
        keep = []
        for stem, pos in sel.groupby("stem", sort=False).indices.items():
            if len(pos) > rpv:
                rng = np.random.default_rng([int(cfg.get("seed", 0)), zlib.crc32(str(stem).encode("utf-8"))])
                pos = np.sort(rng.choice(pos, size=rpv, replace=False))
            keep.append(pos)
        sel = sel.iloc[np.sort(np.concatenate(keep))] if keep else sel.iloc[:0]
    return sel


# ----------------------------------------------------------------------------------------------------------------------
# the DivNet sample contract (tools.divnet_infer.prepare_divnet_input) split into frame preparation + crop
# ----------------------------------------------------------------------------------------------------------------------
def contract_params(config: dict | None) -> dict:
    """The exact parameter parsing of prepare_divnet_input for a bundle config."""
    cfg = config if isinstance(config, dict) else {}
    input_cfg = cfg.get("input", {}) if isinstance(cfg, dict) else {}
    norm_cfg = cfg.get("normalization", {}) if isinstance(cfg, dict) else {}
    return {
        "lags": tuple(int(v) for v in input_cfg.get("image_lags", (-1, 0, 1, 2))),
        "pool_xy": int(input_cfg.get("pool_xy", 4)),
        "shape": (int(input_cfg.get("crop_z", 16)), int(input_cfg.get("crop_yx", 32)), int(input_cfg.get("crop_yx", 32))),
        "sigma": tuple(float(v) for v in input_cfg.get("marker_sigma", (1.5, 2.0, 2.0))),
        "clip": tuple(float(v) for v in norm_cfg.get("clip", (-0.5, 6.0))),
        "lo": float(norm_cfg.get("lo_pct", 50.0)),
        "hi": float(norm_cfg.get("hi_pct", 99.5)),
    }


def prepare_frame(reader, stem: str, frame_t: int, params: dict) -> np.ndarray:
    """prepared_frames[(stem, frame_t)] of the contract: raw frame (FrameReader clamps t to [0, T-1]) -> pool -> norm."""
    raw = reader(stem, int(frame_t), {})
    return _normalise(_pool_xy(raw, params["pool_xy"]), params["lo"], params["hi"], params["clip"])


def frame_keys(t_values, lags) -> list[int]:
    return sorted({max(0, int(tt) + int(lag)) for tt in np.unique(np.asarray(t_values)) for lag in lags})


class SyncFrames:
    """Frames prepared inline (no threads)."""

    def __init__(self, reader, params: dict) -> None:
        self.reader, self.params = reader, params

    def request(self, stem: str, keys) -> None:
        pass

    def get(self, stem: str, frame_t: int) -> np.ndarray:
        return prepare_frame(self.reader, stem, frame_t, self.params)

    def drop(self, stem: str) -> None:
        pass

    def close(self) -> None:
        pass


class FramePrefetcher(SyncFrames):
    """Thread pool preparing frames in request order (FIFO), so the next video's frames are ready when it starts."""

    def __init__(self, reader, params: dict, threads: int = 2) -> None:
        super().__init__(reader, params)
        self.pool = ThreadPoolExecutor(max(1, int(threads)), thread_name_prefix="kds-frame")
        self.futures: dict[tuple, object] = {}
        self.lock = threading.Lock()
        self.busy_s = 0.0

    def _task(self, stem: str, frame_t: int) -> np.ndarray:
        t0 = time.time()
        out = prepare_frame(self.reader, stem, frame_t, self.params)
        with self.lock:
            self.busy_s += time.time() - t0
        return out

    def request(self, stem: str, keys) -> None:
        for ft in keys:
            key = (stem, int(ft))
            if key not in self.futures:
                self.futures[key] = self.pool.submit(self._task, stem, int(ft))

    def get(self, stem: str, frame_t: int) -> np.ndarray:
        fut = self.futures.pop((stem, int(frame_t)), None)
        return fut.result() if fut is not None else prepare_frame(self.reader, stem, frame_t, self.params)

    def drop(self, stem: str) -> None:
        for key in [k for k in self.futures if k[0] == stem]:
            self.futures.pop(key).cancel()

    def close(self) -> None:
        for fut in self.futures.values():
            fut.cancel()
        self.futures.clear()
        self.pool.shutdown(wait=True)


def score_video(stem: str, t, z, y, x, bundle: dict, reader, model_indices=None, **kw) -> tuple[np.ndarray, dict]:
    """Softmax (N, 3) in CLASSES order for the N nodes of one video (arrays in any order; the result is aligned to them).

    model_indices selects bundle['models'] (OOF: the one fold model of the video); None = mean over all (ensemble), the
    same reduction as tools.daughternet.score_nodes. Samples equal prepare_sample's exactly (checked per video).
    Keyword options: see score_video_members."""
    _, mean, stats = score_video_members(stem, t, z, y, x, bundle, reader, model_indices, **kw)
    return mean, stats


def score_video_members(stem: str, t, z, y, x, bundle: dict, reader, model_indices=None, *, batch: int = 512,
                        amp: bool = False, frames: SyncFrames | None = None, checks_fresh: int = 1,
                        checks_cached: int = 2, seed: int = 0,
                        pad_to: int = 64) -> tuple[np.ndarray, np.ndarray, dict]:
    """(members (M, N, 3), mean (N, 3), stats): the softmax of each selected model and their mean (score_nodes'
    torch.stack(...).mean(0), computed on the device), from ONE pass over the frames. With a single selected model the
    mean equals that model's softmax exactly; with all models, members[k] is fold model k's OOF-able output."""
    import torch

    t = np.asarray(t, dtype=np.int64)
    z, y, x = (np.asarray(v, dtype=np.float64) for v in (z, y, x))
    n = len(t)
    stats = {"rows": int(n), "frames": 0, "frame_wait_s": 0.0, "build_s": 0.0, "model_s": 0.0, "gpu_wait_s": 0.0,
             "checks_fresh": 0, "checks_cached": 0, "batches": 0}
    n_models = len(bundle["models"]) if model_indices is None else len(model_indices)
    out = np.full((n, len(CLASSES)), np.nan, dtype=np.float32)
    members = np.full((n_models, n, len(CLASSES)), np.nan, dtype=np.float32)
    if n == 0:
        return members, out, stats
    t_start = time.time()
    params = contract_params(bundle.get("config"))
    lags, shape, pool = params["lags"], params["shape"], params["pool_xy"]
    min_lag = min(lags)
    marker = _marker(shape, params["sigma"])
    models = list(bundle["models"]) if model_indices is None else [bundle["models"][int(i)] for i in model_indices]
    if not models:
        raise RuntimeError(f"{stem}: no model selected")
    dev = bundle["device"]
    use_amp = bool(amp) and dev.type == "cuda"
    frames = frames if frames is not None else SyncFrames(reader, params)
    frames.request(stem, frame_keys(t, lags))
    order = np.argsort(t, kind="stable")
    rng = np.random.default_rng([int(seed), zlib.crc32(stem.encode("utf-8"))])
    n_fresh, n_cached = min(max(0, checks_fresh), n), max(0, checks_cached)
    picks = rng.choice(n, size=min(n, n_fresh + n_cached), replace=False).tolist()
    fresh, cached = set(picks[:n_fresh]), set(picks[n_fresh:])
    prepared: dict[tuple, np.ndarray] = {}  # (stem, frame_t) -> prepared frame, the contract's prepared_frames layout
    cur_t = None
    pending = None

    def collect(item) -> None:
        idx, pm, p = item
        tw = time.time()
        arr = p.float().cpu().numpy()
        arr_m = pm.float().cpu().numpy()
        stats["gpu_wait_s"] += time.time() - tw
        stats["model_s"] += time.time() - tw
        out[idx] = arr[:len(idx)]
        members[:, idx] = arr_m[:, :len(idx)]

    for s in range(0, n, batch):
        tb = time.time()
        idx = order[s:s + batch]
        nb = len(idx)
        nb_pad = min(max(batch, nb), -(-nb // pad_to) * pad_to) if pad_to else nb
        xb = np.zeros((nb_pad, len(lags) + 1, *shape), dtype=np.float32)
        xb[:nb, len(lags)] = marker
        wait0 = stats["frame_wait_s"]
        for j, i in enumerate(idx):
            tt = int(t[i])
            if tt != cur_t:  # nodes are visited by t: frames below tt + min_lag are never needed again
                for key in [k for k in prepared if k[1] < tt + min_lag]:
                    del prepared[key]
                cur_t = tt
            centre = (int(round(float(z[i]))), int(round(float(y[i]) / pool)), int(round(float(x[i]) / pool)))
            for c, lag in enumerate(lags):
                key = (stem, max(0, tt + lag))
                frame = prepared.get(key)
                if frame is None:
                    tw = time.time()
                    frame = frames.get(stem, key[1])
                    stats["frame_wait_s"] += time.time() - tw
                    stats["frames"] += 1
                    prepared[key] = frame
                xb[j, c] = _crop_with_padding(frame, centre, shape)
            pos = s + j
            if pos in fresh or pos in cached:
                node = {"t": tt, "z": float(z[i]), "y": float(y[i]), "x": float(x[i])}
                ref_bundle = {"config": bundle.get("config"), "prepared_frames": {} if pos in fresh else prepared}
                ref = prepare_sample(stem, tt, node, ref_bundle, {}, reader)
                if ref.shape != xb[j].shape or not np.array_equal(ref, xb[j]):
                    diff = float(np.abs(ref - xb[j]).max()) if ref.shape == xb[j].shape else float("nan")
                    raise ContractError(f"{stem} node t={tt} z={z[i]} y={y[i]} x={x[i]}: fast-path sample != "
                                        f"prepare_sample ({'fresh' if pos in fresh else 'cached'} frames, max |d| {diff})")
                stats["checks_fresh" if pos in fresh else "checks_cached"] += 1
        if not np.isfinite(xb[:nb]).all():
            raise RuntimeError(f"{stem}: non-finite DaughterNet input in batch starting at sorted row {s}")
        stats["build_s"] += time.time() - tb - (stats["frame_wait_s"] - wait0)
        tf = time.time()  # on CUDA this is H2D + kernel launch (async); on CPU it is the whole forward pass
        xt = torch.from_numpy(xb).to(dev)
        with torch.no_grad(), torch.autocast(device_type=dev.type, dtype=torch.float16, enabled=use_amp):
            pm = torch.stack([torch.softmax(m(xt).float(), dim=1) for m in models])
            p = pm.mean(0)
        stats["model_s"] += time.time() - tf
        if pending is not None:
            collect(pending)
        pending = (idx, pm, p)
        stats["batches"] += 1
    collect(pending)
    prepared.clear()
    stats["secs"] = time.time() - t_start
    stats["models"] = len(models)
    return members, out, stats


# ----------------------------------------------------------------------------------------------------------------------
# parts (per-video results, resumable)
# ----------------------------------------------------------------------------------------------------------------------
def part_path(parts_dir: Path, stem: str) -> Path:
    return Path(parts_dir) / f"{stem}.parquet"


def write_part(df, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    df.to_parquet(tmp, index=False)
    os.replace(tmp, path)


def part_valid(path: Path, node_ids: np.ndarray) -> bool:
    import pandas as pd

    if not path.is_file():
        return False
    try:
        df = pd.read_parquet(path)
    except Exception:
        return False
    if list(df.columns) != OUT_COLUMNS or len(df) != len(node_ids):
        return False
    if not np.array_equal(df["node_id"].to_numpy(np.int64), np.asarray(node_ids, dtype=np.int64)):
        return False
    return bool(np.isfinite(df[P_COLUMNS].to_numpy(np.float64)).all())


# ----------------------------------------------------------------------------------------------------------------------
# worker process (one per GPU)
# ----------------------------------------------------------------------------------------------------------------------
def worker_main(argv: list[str]) -> int:
    """Score the videos assigned to this worker for the modes the job lists per video. A video that needs 'ens' runs all
    fold models once; its 'oof' part (if also requested) is fold model k's softmax from the same pass."""
    import argparse

    import pandas as pd
    import torch

    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--worker", type=int, required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=0)
    a = ap.parse_args(argv)
    job = json.loads(Path(a.job).read_text())
    cfg = job["cfg"]
    stems = job["workers"][str(a.worker)]
    stem_modes = job["stem_modes"]
    parts_dirs = {m: Path(d) for m, d in job["parts_dirs"].items()}
    if a.threads:
        torch.set_num_threads(int(a.threads))
    try:
        import blosc2
        blosc2.set_nthreads(max(1, int(job.get("blosc_threads", 1))))
    except Exception:
        pass
    device = torch.device(a.device)
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
    t0 = time.time()
    sel = select_rows(read_coords(Path(job["coords"])), cfg)
    sel = sel[sel["stem"].isin(set(stems))]
    groups = {s: g for s, g in sel.groupby("stem", sort=False)}
    ckpts = {int(k): v for k, v in job["ckpts"].items()}
    model_folds = sorted(ckpts)
    bundle = load_daughternet([ckpts[f] for f in model_folds], device=str(device))
    fold_index = {f: i for i, f in enumerate(model_folds)}
    reader = FrameReader(Path(job["data_dir"]))
    params = contract_params(bundle["config"])
    frames = (FramePrefetcher(reader, params, cfg["frame_threads"]) if int(cfg["frame_threads"]) > 0
              else SyncFrames(reader, params))
    run_dir = Path(job["run_dir"])
    name = torch.cuda.get_device_name(0) if device.type == "cuda" else "cpu"
    log(f"[w{a.worker}] {len(stems)} videos, {len(sel)} rows, modes {sorted({m for s in stems for m in stem_modes[s]})}, "
        f"models {model_folds} on {device} ({name}), batch {cfg['batch']}, amp {cfg['amp']}, frame threads "
        f"{cfg['frame_threads']}; setup {time.time() - t0:.1f} s")
    records, rc = [], 0
    try:
        for vi, stem in enumerate(stems):
            g = groups.get(stem)
            modes_s = list(stem_modes[stem])
            if g is None or g.empty:
                records.append({"stem": stem, "rows": 0, "modes": modes_s, "error": "no rows"})
                continue
            frames.request(stem, frame_keys(g["t"].to_numpy(), params["lags"]))
            if vi + 1 < len(stems) and stems[vi + 1] in groups:
                frames.request(stems[vi + 1], frame_keys(groups[stems[vi + 1]]["t"].to_numpy(), params["lags"]))
            fold = int(job["folds"][stem])
            joint = "ens" in modes_s
            model_idx = None if joint else [fold_index[fold]]
            try:
                members, mean, st = score_video_members(
                    stem, g["t"].to_numpy(), g["z"].to_numpy(), g["y"].to_numpy(), g["x"].to_numpy(), bundle, reader,
                    model_idx, batch=int(cfg["batch"]), amp=bool(cfg["amp"]), frames=frames,
                    checks_fresh=int(cfg["checks_fresh"]), checks_cached=int(cfg["checks_cached"]),
                    seed=int(cfg["seed"]), pad_to=int(cfg["pad_to"]))
            except ContractError as exc:
                log(f"[w{a.worker}] CONTRACT FAILURE {exc}")
                records.append({"stem": stem, "rows": int(len(g)), "modes": modes_s, "error": f"ContractError: {exc}"})
                rc = 3
                break
            except Exception as exc:
                frames.drop(stem)
                log(f"[w{a.worker}] {stem} FAILED {type(exc).__name__}: {exc}")
                records.append({"stem": stem, "rows": int(len(g)), "modes": modes_s,
                                "error": f"{type(exc).__name__}: {exc}"})
                rc = rc or 1
                continue
            for mode in modes_s:
                p = mean if (mode == "ens" or not joint) else members[fold_index[fold]]
                part = pd.DataFrame({"stem": stem, "node_id": g["node_id"].to_numpy(np.int64),
                                     "fold": np.full(len(g), fold, dtype=np.int16),
                                     "p_cont": p[:, 0], "p_par": p[:, 1], "p_dau": p[:, 2]})[OUT_COLUMNS]
                write_part(part, part_path(parts_dirs[mode], stem))
            frames.drop(stem)
            records.append({"stem": stem, "fold": fold, "modes": modes_s,
                            **{k: (round(v, 3) if isinstance(v, float) else v) for k, v in st.items()}, "error": None})
            log(f"[w{a.worker}] {vi + 1}/{len(stems)} {stem} fold {fold} {'+'.join(modes_s)} rows {st['rows']} x "
                f"{st['models']} models, frames {st['frames']} {st['secs']:.1f}s (build {st['build_s']:.1f} frame-wait "
                f"{st['frame_wait_s']:.1f} model {st['model_s']:.1f} of which gpu-wait {st['gpu_wait_s']:.1f}) "
                f"{st['rows'] / max(st['secs'], 1e-9):.0f} rows/s checks {st['checks_fresh']}+{st['checks_cached']}")
    finally:
        busy = getattr(frames, "busy_s", None)
        frames.close()
        secs = time.time() - t0
        rows_done = sum(r.get("rows", 0) for r in records if not r.get("error"))
        summary = {"worker": a.worker, "device": str(device), "device_name": name, "attempt": job.get("attempt", 0),
                   "videos": len(stems), "rows": int(rows_done), "secs": round(secs, 1),
                   "rows_per_s": round(rows_done / max(secs, 1e-9), 1), "frame_thread_busy_s": busy,
                   "decoders": decoder_names(), "records": records}
        (run_dir / f"_worker_{a.worker}_attempt{job.get('attempt', 0)}.json").write_text(
            json.dumps(summary, indent=1, default=_json_default))
    log(f"[w{a.worker}] done: {summary['rows']} rows in {secs:.0f} s ({summary['rows_per_s']} rows/s) rc={rc}")
    return rc


# ----------------------------------------------------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------------------------------------------------
def _json_default(value):
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    return str(value)


def _slots(cfg: dict) -> list[str]:
    import torch

    n_gpu = torch.cuda.device_count() if cfg["gpus"] != 0 else 0
    if cfg["gpus"] > 0:
        n_gpu = min(n_gpu, cfg["gpus"])
    if n_gpu:
        n = cfg["workers"] or min(n_gpu, max(1, cfg["max_gpu_workers"]))
        return [str(i % n_gpu) for i in range(n)]
    return ["cpu"] * max(1, cfg["workers"] or 1)


def plan_workers(sel, stems: list[str], n_workers: int, lags, n_models: dict[str, int] | None = None
                 ) -> dict[int, list[str]]:
    """Greedy longest-first on rows x models + FRAME_COST_ROWS x prepared frames."""
    t_by_stem = {s: g for s, g in sel.groupby("stem", sort=False)["t"]}
    n_models = n_models or {}
    cost = {s: len(t_by_stem[s]) * n_models.get(s, 1) + FRAME_COST_ROWS * len(frame_keys(t_by_stem[s].to_numpy(), lags))
            for s in stems}
    load = [0.0] * n_workers
    out: dict[int, list[str]] = {w: [] for w in range(n_workers)}
    for s in sorted(stems, key=lambda k: (-cost[k], k)):
        w = min(range(n_workers), key=lambda k: (load[k], k))
        out[w].append(s)
        load[w] += cost[s]
    return out


def _launch(job_path: Path, assignment: dict[int, list[str]], slots: list[str], log_dir: Path) -> dict[int, int]:
    env_base = os.environ.copy()
    env_base["PYTHONPATH"] = os.pathsep.join(SRC_PATHS + [p for p in env_base.get("PYTHONPATH", "").split(os.pathsep) if p])
    env_base["PYTHONUNBUFFERED"] = "1"
    threads = max(1, (os.cpu_count() or 1) // max(1, len(slots)))
    running = {}
    for wid, slot in enumerate(slots):
        if not assignment.get(wid):
            continue
        env = dict(env_base)
        env["CUDA_VISIBLE_DEVICES"] = slot if slot != "cpu" else ""
        device = "cuda:0" if slot != "cpu" else "cpu"
        cmd = [sys.executable, str(Path(__file__).resolve()), "worker", "--job", str(job_path), "--worker", str(wid),
               "--device", device, "--threads", str(threads)]
        sink = open(log_dir / f"worker_{wid}.log", "a", encoding="utf-8")
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", errors="replace")
        th = threading.Thread(target=kdn_core._pump, args=(proc.stdout, f"[w{wid}@{slot}] ", sink), daemon=True)
        th.start()
        running[wid] = (proc, th, sink)
        log(f"[score] worker {wid} on {slot}: {len(assignment[wid])} videos (pid {proc.pid})")
    rcs = {}
    for wid, (proc, th, sink) in running.items():
        rcs[wid] = proc.wait()
        th.join(timeout=10)
        sink.close()
    return rcs


def _check_signature(parts_dir: Path, signature: dict, resume: bool) -> str:
    sig_path = parts_dir / "_signature.json"
    old = json.loads(sig_path.read_text()) if sig_path.is_file() else None
    stale = [p for p in parts_dir.glob("*.parquet")]
    status = "fresh"
    if stale and (not resume or old != signature):
        for p in stale:
            p.unlink()
        status = "cleared (resume off)" if not resume else "cleared (signature changed)"
    elif stale:
        status = "resume"
    sig_path.write_text(json.dumps(signature, indent=1))
    return status


def verify_rows(out, sel, ckpts: dict[int, Path], mode: str, data_dir: Path, per_fold: int, seed: int) -> dict:
    """Re-score a few rows per fold from raw frames through tools.daughternet.score_nodes (CPU, batch 1)."""
    reader = FrameReader(Path(data_dir))
    rng = np.random.default_rng(seed)
    both = out.join(sel[["t", "z", "y", "x"]])
    both = both[np.isfinite(both[P_COLUMNS].to_numpy(np.float64)).all(axis=1)]
    picks = []
    for fold, g in both.groupby("fold"):
        cand = [g["p_par"].idxmax(), g["p_dau"].idxmax()] + rng.choice(g.index.to_numpy(), size=min(len(g), per_fold),
                                                                       replace=False).tolist()
        picks += list(dict.fromkeys(cand))[:max(0, per_fold)]
    bundles, rows, max_diff = {}, [], 0.0
    for i in picks:
        r = both.loc[i]
        folds = (int(r["fold"]),) if mode == "oof" else tuple(sorted(ckpts))
        if folds not in bundles:
            bundles[folds] = load_daughternet([ckpts[f] for f in folds], device="cpu")
        bundle = bundles[folds]
        bundle["prepared_frames"] = {}
        node = {"t": int(r["t"]), "z": float(r["z"]), "y": float(r["y"]), "x": float(r["x"])}
        p = score_nodes(str(r["stem"]), [node], bundle, {}, reader, batch=1)[0]
        diff = float(np.abs(p.astype(np.float64) - r[P_COLUMNS].to_numpy(np.float64)).max())
        max_diff = max(max_diff, diff)
        rows.append({"row": int(i), "stem": str(r["stem"]), "node_id": int(r["node_id"]), "fold": int(r["fold"]),
                     "models": list(folds), "p_par": float(r["p_par"]), "diff": diff})
    return {"checked": len(rows), "max_abs_diff": max_diff, "rows": rows}


def _worker_stats(run_dir: Path) -> list[dict]:
    workers = []
    for p in sorted(run_dir.glob("_worker_*.json")):
        try:
            w = json.loads(p.read_text())
        except Exception:
            continue
        recs = [r for r in w.get("records", []) if not r.get("error")]
        workers.append({k: w.get(k) for k in ("worker", "attempt", "device", "device_name", "videos", "rows", "secs",
                                              "rows_per_s", "frame_thread_busy_s", "decoders")}
                       | {f"sum_{k}": round(sum(float(r.get(k, 0) or 0) for r in recs), 1)
                          for k in ("frame_wait_s", "build_s", "model_s", "gpu_wait_s", "frames", "checks_fresh",
                                    "checks_cached")}
                       | {"failed": [r for r in w.get("records", []) if r.get("error")]})
    return workers


def score_modes(cfg: dict, modes: list[str], ctx: dict) -> dict:
    """One worker pass for all requested modes (a video needing oof + ens runs every fold model once and yields both).
    Returns per-mode bookkeeping for finish_mode."""
    work, sel, ckpts = ctx["work"], ctx["sel"], ctx["ckpts"]
    run_dir = work / "parts" / "_run"
    run_dir.mkdir(parents=True, exist_ok=True)
    for old in list(run_dir.glob("_worker_*.json")) + list(run_dir.glob("_job_*.json")):
        old.unlink()  # per-run bookkeeping; the summaries describe this run's workers only
    node_ids, video_fold = ctx["node_ids"], ctx["video_fold"]
    book = {}
    for mode in modes:
        parts_dir = work / "parts" / mode
        parts_dir.mkdir(parents=True, exist_ok=True)
        signature = {"mode": mode, "classes": list(CLASSES), "coords_sha256": ctx["coords_sha"], "amp": bool(cfg["amp"]),
                     "ckpt_sha256": {str(k): v["sha256"] for k, v in ctx["ckpt_info"].items()},
                     "code_sha256": ctx.get("code_sha", {}),
                     "folds": {s: video_fold[s] for s in ctx["stems"]}}
        status = _check_signature(parts_dir, signature, cfg["resume"])
        no_model = [s for s in ctx["stems"] if (video_fold[s] not in ckpts if mode == "oof" else not ckpts)]
        # honest OOF: a video whose fold model trained on it or on a leak-group sibling gets no OOF prediction
        leak_excluded = [s for s in ctx["stems"] if mode == "oof" and s in ctx["routing"]["excluded"]
                         and s not in set(no_model)]
        skip = set(no_model) | set(leak_excluded)
        candidates = [s for s in ctx["stems"] if s not in skip]
        if leak_excluded:  # a part from an earlier run must never be merged for an excluded video
            for s in leak_excluded:
                part_path(parts_dir, s).unlink(missing_ok=True)
        todo = [s for s in candidates if not part_valid(part_path(parts_dir, s), node_ids[s])]
        book[mode] = {"parts_dir": parts_dir, "status": status, "no_model": no_model, "leak_excluded": leak_excluded,
                      "candidates": candidates, "todo_start": list(todo), "todo": list(todo),
                      "resumed": len(candidates) - len(todo)}
        log(f"[score:{mode}] parts {status}: {book[mode]['resumed']} videos resumed, {len(todo)} to score, "
            f"{len(no_model)} without a model {no_model[:5]}, {len(leak_excluded)} excluded by the leak audit "
            f"{leak_excluded[:5]}")
    slots = ctx["slots"]
    rcs_all = []
    t0 = time.time()
    for attempt in range(1 + max(0, int(cfg["retries"]))):
        stem_modes: dict[str, list[str]] = {}
        for mode in modes:
            for s in book[mode]["todo"]:
                stem_modes.setdefault(s, []).append(mode)
        if not stem_modes:
            break
        todo = [s for s in ctx["stems"] if s in stem_modes]
        assignment = plan_workers(sel, todo, len(slots), ctx["lags"],
                                  {s: (len(ckpts) if "ens" in m else 1) for s, m in stem_modes.items()})
        job = {"cfg": dict(cfg), "attempt": attempt, "coords": str(ctx["coords"]), "data_dir": str(ctx["data_dir"]),
               "run_dir": str(run_dir), "parts_dirs": {m: str(book[m]["parts_dir"]) for m in modes},
               "ckpts": {str(k): str(p) for k, p in ckpts.items()}, "folds": {s: video_fold[s] for s in todo},
               "stem_modes": stem_modes, "workers": {str(w): v for w, v in assignment.items()},
               "blosc_threads": max(1, (os.cpu_count() or 1) // max(1, len(slots) * max(1, cfg["frame_threads"])))}
        job_path = run_dir / f"_job_attempt{attempt}.json"
        job_path.write_text(json.dumps(job, indent=1))
        combos: dict[str, int] = {}
        for m in stem_modes.values():
            combos["+".join(m)] = combos.get("+".join(m), 0) + 1
        log(f"[score] attempt {attempt}: {len(todo)} videos (modes per video {combos}), {len(slots)} workers")
        rcs = _launch(job_path, assignment, slots, run_dir)
        rcs_all.append({str(k): v for k, v in rcs.items()})
        if any(rc == 3 for rc in rcs.values()):
            raise ContractError(f"a worker hit a contract failure (see its log in {run_dir}); no merged output written")
        for mode in modes:
            book[mode]["todo"] = [s for s in book[mode]["todo"]
                                  if not part_valid(part_path(book[mode]["parts_dir"], s), node_ids[s])]
        log(f"[score] attempt {attempt}: worker rc {rcs}; videos still missing "
            f"{ {m: len(book[m]['todo']) for m in modes} }")
    score_s = time.time() - t0
    workers = _worker_stats(run_dir)
    for mode in modes:
        book[mode].update({"score_s": score_s, "worker_rc": rcs_all, "workers": workers, "joint_modes": list(modes)})
    return book


def finish_mode(cfg: dict, mode: str, ctx: dict, bk: dict) -> dict:
    """Merge the parts of one mode into node_p_<mode>.parquet (input order), verify, write the summary json."""
    import pandas as pd

    t0 = time.time()
    work, sel, ckpts = ctx["work"], ctx["sel"], ctx["ckpts"]
    node_ids, video_fold = ctx["node_ids"], ctx["video_fold"]
    parts_dir, todo = bk["parts_dir"], set(bk["todo"])
    parts = [pd.read_parquet(part_path(parts_dir, s)) for s in bk["candidates"] if s not in todo]
    res = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=OUT_COLUMNS)
    res = res.drop(columns=["fold"])
    out = (sel[["stem", "node_id"]].rename_axis("_row").reset_index()
           .merge(res, on=["stem", "node_id"], how="left", validate="one_to_one").set_index("_row"))
    out.index.name = None
    out["fold"] = out["stem"].map(video_fold).astype(np.int16)
    out = out[OUT_COLUMNS]
    for c in P_COLUMNS:
        out[c] = out[c].astype(np.float32)
    if len(out) != len(sel) or not (out.index == sel.index).all() or not (out["node_id"].to_numpy() ==
                                                                         sel["node_id"].to_numpy()).all():
        raise RuntimeError("merged output is not aligned to the input rows")
    out_path = work / OUTPUTS[mode]
    tmp = out_path.with_name(out_path.name + ".tmp")
    out.reset_index(drop=True).to_parquet(tmp, index=False)
    os.replace(tmp, out_path)
    merge_s = time.time() - t0

    tv = time.time()
    tol = cfg["verify_tol"] or (2e-2 if cfg["amp"] else 1e-4)
    try:
        verify = verify_rows(out, sel, ckpts, mode, ctx["data_dir"], cfg["verify_per_fold"], cfg["seed"])
        verify["tolerance"] = tol
        verify["pass"] = bool(verify["checked"] > 0 and verify["max_abs_diff"] <= tol)
    except Exception as exc:
        verify = {"checked": 0, "error": f"{type(exc).__name__}: {exc}", "pass": False, "tolerance": tol}
    verify_s = time.time() - tv

    scored_now = [s for s in bk["todo_start"] if s not in todo]
    rows_now = int(sum(len(node_ids[s]) for s in scored_now))
    p = out[P_COLUMNS].to_numpy(np.float64)
    finite = np.isfinite(p).all(axis=1)
    nan_rows = int((~finite).sum())
    score_s = bk["score_s"]
    summary = {
        "kernel": KERNEL, "mode": mode, "output": str(out_path), "columns": OUT_COLUMNS, "classes": list(CLASSES),
        "rows_input_parquet": int(ctx["n_coords"]), "rows_selected": int(len(sel)), "rows_out": int(len(out)),
        "row_count_matches_input": bool(len(out) == ctx["n_coords"]), "selection": ctx["selection"],
        "nan_rows": nan_rows,
        "nan_rows_per_fold": {str(k): int(v) for k, v in out.loc[~finite, "fold"].value_counts().sort_index().items()},
        "rows_per_fold": {str(k): int(v) for k, v in out["fold"].value_counts().sort_index().items()},
        "videos_per_fold": {str(k): int(v) for k, v in
                            pd.Series([video_fold[s] for s in ctx["stems"]]).value_counts().sort_index().items()},
        "models_per_row": 1 if mode == "oof" else len(ckpts),
        "fold_column": ("split fold of the video = the fold model that scored the row (never trained on the video)"
                        if mode == "oof" else "split fold of the video, for reference; p averages all fold models"),
        "videos": {"total": len(ctx["stems"]), "resumed": bk["resumed"], "scored_this_run": len(scored_now),
                   "rows_scored_this_run": rows_now, "missing_after_retries": sorted(todo), "no_model": bk["no_model"],
                   "leak_excluded": bk.get("leak_excluded", [])},
        "worker_rc": bk["worker_rc"], "parts_status": bk["status"],
        "checkpoints": {str(k): v for k, v in ctx["ckpt_info"].items()}, "splits": ctx["splits_info"],
        "oof_routing_audit": ctx["routing"] if mode == "oof" else None,
        "prob": {"max_abs_sum_minus_1": float(np.abs(p[finite].sum(axis=1) - 1).max()) if finite.any() else None,
                 "mean": {c: float(np.nanmean(p[:, i])) if finite.any() else None for i, c in enumerate(CLASSES)},
                 "p_par_quantiles": {q: float(np.quantile(p[finite, 1], float(q))) for q in ("0.5", "0.9", "0.99", "0.999")}
                 if finite.any() else None},
        "verify": verify,
        "timing": {"discover_s": ctx["discover_s"], "score_wall_s": round(score_s, 1), "merge_s": round(merge_s, 1),
                   "verify_s": round(verify_s, 1), "finish_s": round(time.time() - t0, 1),
                   "rows_per_s_wall": round(rows_now / max(score_s, 1e-9), 1) if rows_now else None,
                   "joint_pass_modes": bk["joint_modes"], "workers": bk["workers"]},
        "slots": ctx["slots"], "config": cfg,
    }
    sum_path = work / f"node_p_{mode}_summary.json"
    sum_path.write_text(json.dumps(summary, indent=1, default=_json_default))
    log(f"[score:{mode}] wrote {out_path} ({len(out)} rows, NaN rows {nan_rows}) and {sum_path}; rows per fold "
        f"{summary['rows_per_fold']}; merge {merge_s:.1f} s; verify {verify.get('checked')} rows "
        f"max |dp| {verify.get('max_abs_diff')} tol {tol} -> {'PASS' if verify['pass'] else 'FAIL'}")
    return summary


def run(cfg: dict | None = None) -> dict:
    cfg = cfg or config_from_env()
    t0 = time.time()
    work = Path(cfg["work_dir"])
    work.mkdir(parents=True, exist_ok=True)
    input_root = Path(cfg["input_root"])
    data_dir = resolve_data_dir({"data_dir": cfg["data_dir"]})
    ckpt_root = Path(cfg["ckpt_root"]) if cfg.get("ckpt_root") else input_root
    ckpts = discover_checkpoints(ckpt_root, cfg["ckpt_name"], cfg["train_slug"])
    if not ckpts:
        raise FileNotFoundError(f"no fold_k/{cfg['ckpt_name']} under {ckpt_root} (attach the K-DN trainer output)")
    ckpt_info = inspect_checkpoints(ckpts)
    log("[discover] checkpoints: " + "; ".join(f"fold {k}: {v['path']} epoch {v['epoch']} val {v['val_loss']}"
                                              for k, v in ckpt_info.items()))
    if cfg["expect_folds"] and len(ckpts) != cfg["expect_folds"]:
        log(f"[discover] WARNING {len(ckpts)} fold checkpoints found, expected {cfg['expect_folds']}")
    folds, splits_info, primary, fallback = resolve_splits(cfg, list(ckpts.values()), input_root, return_sources=True)
    basis = primary or fallback or {}
    basis_nf = int(splits_info.get("primary_n_folds") or 0) if primary else 0
    basis_nf = basis_nf or len(set(basis.values()))
    ck_nf = sorted({int(v["n_folds"]) for v in ckpt_info.values() if v.get("n_folds") is not None})
    if ck_nf and ck_nf != [basis_nf]:
        raise RuntimeError(f"fold checkpoints were trained with n_folds {ck_nf} but the splits used for routing "
                           f"({splits_info['primary'] or splits_info['fallback']}) have {basis_nf} folds: the "
                           "video -> fold model routing would not be out-of-fold; set KDS_SPLITS to the trainer's "
                           "splits_used.json")
    if not primary:
        log("[discover] WARNING no trainer splits_used.json found: routing assumes the trainer used the embedded "
            "splits.json (fold counts agree)")
    elif splits_info["fallback_only"]:
        log(f"[discover] WARNING {len(splits_info['fallback_only'])} videos are not in the trainer's splits_used.json "
            "and are routed by the embedded splits.json (no fold model trained on them)")
    coords_path = find_coords(cfg, input_root)
    coords = read_coords(coords_path)
    sel = select_rows(coords, cfg)
    stems = list(dict.fromkeys(sel["stem"].tolist()))
    no_data = [s for s in stems if not (data_dir / f"{s}.zarr").exists()]
    if no_data:
        log(f"[discover] WARNING {len(no_data)} videos have no {data_dir}/<stem>.zarr: {no_data[:5]}")
    import torch
    bundle_cfg = torch.load(ckpts[min(ckpts)], map_location="cpu", weights_only=False).get("config")
    lags = contract_params(bundle_cfg)["lags"]
    slots = _slots(cfg)
    selection = {"stems": cfg["stems"] or None, "max_videos": cfg["max_videos"], "rows_per_video": cfg["rows_per_video"],
                 "seed": cfg["seed"], "videos": len(stems)}
    log(f"[discover] coords {coords_path}: {len(coords)} rows / {coords['stem'].nunique()} videos; selected {len(sel)} "
        f"rows / {len(stems)} videos; data {data_dir}; splits primary {splits_info['primary']} "
        f"(fallback-only {len(splits_info['fallback_only'])}, disagreements "
        f"{len(splits_info['disagreements_primary_vs_fallback'])}); worker slots {slots}")
    video_fold = {s: int(folds.get(s, -1)) for s in stems}
    routing = audit_oof_routing(video_fold, ckpt_info, primary, fallback, leak_groups(_embedded_splits_path()))
    if routing["excluded"]:
        log(f"[discover] WARNING OOF leak audit: {len(routing['excluded'])} videos would be scored by a fold model that "
            f"trained on them or on a leak-group sibling -> NaN in node_p_oof: {dict(list(routing['excluded'].items())[:3])}")
    if routing["early_stop_on_oof_fold"]:
        log(f"[discover] note: folds {routing['early_stop_on_oof_fold']} selected best.pt on their own OOF fold "
            "(trainer KDN_INNER_VAL=0), so OOF p is mildly optimistic")
    ctx = {"work": work, "sel": sel, "folds": folds, "ckpts": ckpts, "ckpt_info": ckpt_info, "stems": stems,
           "coords": coords_path, "coords_sha": _file_sha(coords_path), "n_coords": len(coords), "data_dir": data_dir,
           "splits_info": splits_info, "slots": slots, "lags": lags, "selection": selection,
           "node_ids": {s: g.to_numpy(np.int64) for s, g in sel.groupby("stem", sort=False)["node_id"]},
           "video_fold": video_fold, "routing": routing, "code_sha": code_shas(),
           "discover_s": round(time.time() - t0, 1)}
    modes = list(dict.fromkeys(cfg["modes"]))
    book = score_modes(cfg, modes, ctx)
    state = {"summaries": {}, "work_dir": str(work)}
    for mode in modes:
        state["summaries"][mode] = finish_mode(cfg, mode, ctx, book[mode])
    state["total_s"] = round(time.time() - t0, 1)
    log(f"[kds] done in {state['total_s']} s")
    return state


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        sys.exit(worker_main(sys.argv[2:]))
    run(config_from_env())
