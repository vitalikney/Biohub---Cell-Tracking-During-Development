"""K-DN: train DaughterNet (tools/daughternet.py) from scratch with honest video folds and write out-of-fold predictions.

One module shared by the Kaggle kernel (kdn-train.ipynb materialises it with %%writefile next to tools/divnet_infer.py
and tools/daughternet.py) and by the laptop runner run_local.py. Steps (run_all runs them in order):

  step_prepare      locate the data, folds (embedded splits.json, else the inline seed-0 rule), GT labels per video
  step_build_cache  DivNet-contract crops for every labelled node -> one memmap (N, 4, 18, 34, 34) + meta.csv
  step_train        one subprocess per fold (two at once on 2 GPUs): balanced sampler, flips/rot90/jitter/gain,
                    AdamW + cosine, early stopping on the fold's val loss, best.pt/last.pt every epoch, fold OOF
  step_oof          oof.csv + oof_readout.json (+ in-sample DivNet comparison)

Labels (annotated GT nodes only, never unannotated space):
  parent   node with >= 2 GT children (at its own t)
  daughter each child of a parent (at its own, first, frame)
  cont     in-degree 1, out-degree 1, >= cont_min_dist frames (lineage) from every parent AND daughter node,
           random subsample of cont_per_video per video
  hardneg  cont nodes that sit in the L2 insertion gate of an annotated one-child GT node, as u or as v
           (u: exactly one child c1 at t+1 within 10 um; v at t+1, v != c1, within 15 um of u; 3 <= |c1-v| <= 20 um;
           |midpoint(c1, v) - u| <= 6.5 um; cos(c1-u, v-u) <= 0.25), up to hardneg_per_video, label cont
Crops: prepare_sample (DivNet contract) called with an enlarged 18x34x34 crop; the inner 16x32x32 of it equals the
contract sample exactly (asserted on the first nodes of every video), the 1-voxel margin feeds the +-1 voxel jitter.
Node coordinates are voxel indices of the full-resolution (64, 256, 256) frame, exactly as in the GT .geff.
Frame index t+lag is clamped to [0, T-1] (the contract clamps the low end with max(0, .); the high end is clamped here,
as in friend A's FrameReader, so nodes at t >= T-2 get a repeated last frame).
"""
from __future__ import annotations

import copy
import json
import math
import os
import struct
import subprocess
import sys
import threading
import time
import zlib
from pathlib import Path

import numpy as np

try:  # repo layout (laptop) and the Kaggle kernel (tools/ materialised under kdn_src)
    from tools.daughternet import CLASSES, DEFAULT_CFG, build_model, load_daughternet, prepare_sample, score_nodes
    from tools.divnet_infer import _marker, load_divnet_mitosis_model, _checkpoint_candidates
except Exception:  # pragma: no cover - notebook fallback when the cells were executed into globals
    CLASSES = globals()["CLASSES"]
    DEFAULT_CFG = globals()["DEFAULT_CFG"]
    build_model = globals()["build_model"]
    load_daughternet = globals()["load_daughternet"]
    prepare_sample = globals()["prepare_sample"]
    score_nodes = globals()["score_nodes"]
    _marker = globals()["_marker"]
    load_divnet_mitosis_model = globals()["load_divnet_mitosis_model"]
    _checkpoint_candidates = globals().get("_checkpoint_candidates", lambda: [])

COMPETITION = "biohub-cell-tracking-during-development"
VOXEL_SCALE_UM = np.array([1.625, 0.40625, 0.40625], dtype=np.float64)
CLASS_INDEX = {name: i for i, name in enumerate(CLASSES)}
CROP = (16, 32, 32)          # DivNet contract crop (z, y, x) in pooled voxels
MARGIN = 1                   # +-1 voxel jitter margin stored around it
BIG = (CROP[0] + 2 * MARGIN, CROP[1] + 2 * MARGIN, CROP[2] + 2 * MARGIN)
OOF_COLUMNS = ["stem", "t", "z", "y", "x", "label", "fold", "p_cont", "p_par", "p_dau"]


def log(*args) -> None:
    print(time.strftime("%H:%M:%S"), *args, flush=True)


# ----------------------------------------------------------------------------------------------------------------------
# configuration
# ----------------------------------------------------------------------------------------------------------------------
def _env_flag(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip() not in ("", "0", "false", "False", "no")


def config_from_env(overrides: dict | None = None) -> dict:
    env = os.environ.get
    smoke = _env_flag("KDN_SMOKE")
    on_kaggle = Path("/kaggle/working").exists()
    cfg = {
        "smoke": smoke,
        "data_dir": env("KDN_DATA_DIR", ""),
        "work_dir": env("KDN_WORK_DIR", "/kaggle/working" if on_kaggle else str(Path.cwd() / "kdn_out")),
        "cache_dir": env("KDN_CACHE_DIR", ""),
        "splits_path": env("KDN_SPLITS", ""),
        "stems": [s.strip() for s in env("KDN_STEMS", "").split(",") if s.strip()],
        "max_videos": int(env("KDN_MAX_VIDEOS", "0") or 0),
        "smoke_videos": int(env("KDN_SMOKE_VIDEOS", "5")),
        "n_folds": int(env("KDN_FOLDS", "2" if smoke else "5")),
        "epochs": int(env("KDN_EPOCHS", "1" if smoke else "30")),
        "patience": int(env("KDN_PATIENCE", "6")),
        "batch": int(env("KDN_BATCH", "64")),
        "lr": float(env("KDN_LR", "1e-3")),
        "weight_decay": float(env("KDN_WD", "0.01")),
        "warmup_frac": float(env("KDN_WARMUP_FRAC", "0.03")),
        "epoch_samples": int(env("KDN_EPOCH_SAMPLES", "0")),   # 0 = number of training samples
        "eval_batch": int(env("KDN_EVAL_BATCH", "256")),
        "cont_per_video": int(env("KDN_CONT_PER_VIDEO", "60")),
        "hardneg_per_video": int(env("KDN_HARDNEG_PER_VIDEO", "40")),
        "cont_min_dist": int(env("KDN_CONT_MIN_DIST", "2")),
        "seed": int(env("KDN_SEED", "0")),
        "build_workers": int(env("KDN_BUILD_WORKERS", "0")),  # 0 = min(4, cpu count)
        "contract_checks": int(env("KDN_CONTRACT_CHECKS", "2")),  # exact contract checks per video
        "cache_dtype": env("KDN_CACHE_DTYPE", "float32"),
        "jitter": int(env("KDN_JITTER", "1")),
        "gain": [float(env("KDN_GAIN_LO", "0.8")), float(env("KDN_GAIN_HI", "1.2"))],
        "amp": _env_flag("KDN_AMP", "1"),
        "gpus": int(env("KDN_GPUS", "-1")),                   # -1 = all visible, 0 = CPU
        "inner_val": _env_flag("KDN_INNER_VAL"),              # 1 = early-stop on fold k+1, train on the other K-2
        "divnet_compare": _env_flag("KDN_DIVNET", "1"),
        "divnet_checkpoint": env("KDN_DIVNET_CKPT", ""),
        "keep_cache": _env_flag("KDN_KEEP_CACHE", "1"),
        "gate": {"child_um": 10.0, "v_um": 15.0, "sister_min_um": 3.0, "sister_max_um": 20.0,
                 "mid_um": 6.5, "cos_max": 0.25},
    }
    if overrides:
        cfg.update(overrides)
    return cfg


def resolve_data_dir(cfg: dict) -> Path:
    if cfg.get("data_dir"):
        return Path(cfg["data_dir"])
    candidates = [Path(f"/kaggle/input/competitions/{COMPETITION}"), Path(f"/kaggle/input/{COMPETITION}")]
    comp_dir = next((p for p in candidates if p.exists()), candidates[0])
    return comp_dir / "train"


def resolve_cache_dir(cfg: dict) -> Path:
    if cfg.get("cache_dir"):
        return Path(cfg["cache_dir"])
    for base in (Path("/kaggle/temp"), Path("/tmp")):
        if base.exists() and os.access(base, os.W_OK):
            return base / "kdn_cache"
    return Path(cfg["work_dir"]) / "_kdn_cache"


# ----------------------------------------------------------------------------------------------------------------------
# codecs: zstd (GT .geff arrays) and blosc (image chunks); several decoders so the kernel needs no extra wheels
# ----------------------------------------------------------------------------------------------------------------------
_ZSTD_FN = None


def _zstd_candidates():
    def via_zstandard(buf, size):
        import zstandard
        return zstandard.ZstdDecompressor().decompress(buf, max_output_size=max(size, 1))

    def via_numcodecs(buf, size):
        from numcodecs import Zstd
        return bytes(Zstd().decode(buf))

    def via_pyarrow(buf, size):
        import pyarrow as pa
        return pa.Codec("zstd").decompress(buf, decompressed_size=size, asbytes=True)

    def via_imagecodecs(buf, size):
        import imagecodecs
        return bytes(imagecodecs.zstd_decode(buf))

    return [via_zstandard, via_numcodecs, via_pyarrow, via_imagecodecs]


def zstd_decompress(buf: bytes, size: int) -> bytes:
    global _ZSTD_FN
    if _ZSTD_FN is not None:
        return _ZSTD_FN(buf, size)
    errors = []
    for fn in _zstd_candidates():
        try:
            out = fn(buf, size)
            if len(out) != size:
                raise ValueError(f"size {len(out)} != {size}")
            _ZSTD_FN = fn
            return out
        except Exception as exc:  # try the next decoder
            errors.append(f"{fn.__name__}: {type(exc).__name__}: {exc}")
    raise RuntimeError("no zstd decoder works: " + " | ".join(errors))


def _bitunshuffle(block: bytes, typesize: int) -> bytes:
    n = len(block) // typesize
    n8 = n - (n % 8)
    if n8 == 0:
        return block
    head = np.frombuffer(block, dtype=np.uint8, count=n8 * typesize).reshape(typesize * 8, n8 // 8)
    bits = np.unpackbits(head, axis=1, bitorder="little").reshape(typesize, 8, n8)
    elems = np.packbits(bits, axis=1, bitorder="little").reshape(typesize, n8)
    return elems.T.tobytes() + block[n8 * typesize:]


def blosc1_decompress_pure(raw: bytes) -> bytes:
    """Blosc-1 frame decoder (numpy + a zstd decoder); last-resort fallback, tested against blosc2 locally."""
    flags, typesize = raw[2], raw[3]
    nbytes, blocksize, _cbytes = struct.unpack("<iii", raw[4:16])
    if flags & 0x2:  # memcpyed
        return bytes(raw[16:16 + nbytes])
    compcode = flags >> 5
    if compcode != 4:
        raise RuntimeError(f"pure blosc decoder supports zstd only (compcode {compcode})")
    nblocks = (nbytes + blocksize - 1) // blocksize
    bstarts = struct.unpack(f"<{nblocks}i", raw[16:16 + 4 * nblocks])
    out = bytearray(nbytes)
    dont_split = bool(flags & 0x10)
    for i, start in enumerate(bstarts):
        bsize = min(blocksize, nbytes - i * blocksize)
        nstreams = 1 if (dont_split or typesize <= 1 or bsize < typesize) else typesize
        neb = bsize // nstreams
        pos, parts = start, []
        for _ in range(nstreams):
            csize = struct.unpack("<i", raw[pos:pos + 4])[0]
            pos += 4
            chunk = raw[pos:pos + csize]
            pos += csize
            parts.append(bytes(chunk) if csize == neb else zstd_decompress(bytes(chunk), neb))
        block = b"".join(parts)
        if flags & 0x4:
            block = _bitunshuffle(block, typesize)
        elif (flags & 0x1) and typesize > 1:
            n = bsize // typesize
            block = np.frombuffer(block, np.uint8, count=n * typesize).reshape(typesize, n).T.tobytes() + block[n * typesize:]
        out[i * blocksize:i * blocksize + bsize] = block
    return bytes(out)


_BLOSC_FN = None


def _blosc_candidates():
    def via_blosc2(raw):
        import blosc2
        return blosc2.decompress(raw)

    def via_numcodecs(raw):
        from numcodecs import Blosc
        return bytes(Blosc().decode(raw))

    def via_blosc(raw):
        import blosc
        return blosc.decompress(raw)

    return [via_blosc2, via_numcodecs, via_blosc, blosc1_decompress_pure]


def blosc_decompress(raw: bytes) -> bytes:
    global _BLOSC_FN
    nbytes = struct.unpack("<i", raw[4:8])[0]
    if _BLOSC_FN is not None:
        return _BLOSC_FN(raw)
    errors = []
    for fn in _blosc_candidates():
        try:
            out = fn(raw)
            if len(out) != nbytes:
                raise ValueError(f"size {len(out)} != {nbytes}")
            _BLOSC_FN = fn
            return out
        except Exception as exc:
            errors.append(f"{fn.__name__}: {type(exc).__name__}: {exc}")
    raise RuntimeError("no blosc decoder works: " + " | ".join(errors))


def decoder_names() -> dict:
    return {"zstd": getattr(_ZSTD_FN, "__name__", None), "blosc": getattr(_BLOSC_FN, "__name__", None)}


def _zarr_dtype(meta: dict) -> np.dtype:
    dtype = np.dtype(meta["data_type"])
    for codec in meta.get("codecs", []):
        if codec.get("name") == "bytes":
            endian = (codec.get("configuration") or {}).get("endian", "little")
            dtype = dtype.newbyteorder("<" if endian == "little" else ">")
    return dtype


def _decode_chunk(raw: bytes, meta: dict, chunk_shape: tuple) -> np.ndarray:
    dtype = _zarr_dtype(meta)
    size = int(np.prod(chunk_shape)) * dtype.itemsize
    data = raw
    codecs = meta.get("codecs", [])
    for codec in reversed(codecs):
        name = codec.get("name")
        if name == "bytes":
            continue
        if name == "zstd":
            data = zstd_decompress(data, size)
        elif name == "blosc":
            data = blosc_decompress(data)
        elif name == "gzip":
            data = zlib.decompress(data, 16 + zlib.MAX_WBITS)
        else:
            raise RuntimeError(f"unsupported zarr codec {name}")
    return np.frombuffer(data, dtype=dtype, count=int(np.prod(chunk_shape))).reshape(chunk_shape)


def read_zarr_array(path: Path) -> np.ndarray:
    """Whole zarr v3 array with a regular chunk grid, decoded with numpy (+ zstd/blosc); zarr is the fallback."""
    path = Path(path)
    try:
        meta = json.loads((path / "zarr.json").read_text())
        shape = tuple(int(v) for v in meta["shape"])
        chunks = tuple(int(v) for v in meta["chunk_grid"]["configuration"]["chunk_shape"])
        sep = ((meta.get("chunk_key_encoding") or {}).get("configuration") or {}).get("separator", "/")
        dtype = _zarr_dtype(meta)
        out = np.full(shape, meta.get("fill_value", 0) or 0, dtype=dtype.newbyteorder("="))
        grid = [range(math.ceil(s / c)) if s else range(0) for s, c in zip(shape, chunks)]
        for idx in np.ndindex(*[len(g) for g in grid]):
            key = sep.join(str(i) for i in idx)
            chunk_path = path / "c" / key if sep == "/" else path / f"c{sep}{key}"
            if not chunk_path.exists():
                continue
            chunk = _decode_chunk(chunk_path.read_bytes(), meta, chunks)
            sl = tuple(slice(i * c, min((i + 1) * c, s)) for i, c, s in zip(idx, chunks, shape))
            out[sl] = chunk[tuple(slice(0, x.stop - x.start) for x in sl)]
        return out
    except Exception as first:
        try:
            import zarr
            return np.asarray(zarr.open(str(path), mode="r")[...])
        except Exception:
            raise first


def read_gt_geff(path: Path) -> dict:
    """GT graph arrays: ids, t, z, y, x (voxel units of the full-resolution frame) and edges (E, 2) source->target."""
    path = Path(path)
    ids = read_zarr_array(path / "nodes" / "ids").astype(np.int64)
    props = path / "nodes" / "props"
    cols = {k: read_zarr_array(props / k / "values") for k in ("t", "z", "y", "x")}
    edges_path = path / "edges" / "ids"
    edges = read_zarr_array(edges_path).astype(np.int64).reshape(-1, 2) if edges_path.exists() else np.zeros((0, 2), np.int64)
    return {"ids": ids, "t": cols["t"].astype(np.int64), "z": cols["z"].astype(np.float64),
            "y": cols["y"].astype(np.float64), "x": cols["x"].astype(np.float64), "edges": edges}


class FrameReader:
    """read_test_frame of the exp39 notebook, parameterised by directory: one blosc chunk per frame, zarr fallback.

    Callable as read_frame(dataset, t, frame_cache); t is clamped to [0, T-1]; the frame is cached under the requested
    t so prepare_divnet_input's frame_cache.pop(frame_t) releases it."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.meta: dict[str, tuple] = {}
        self.frames_read = 0

    def _meta(self, dataset: str) -> tuple:
        if dataset not in self.meta:
            meta = json.loads((self.data_dir / f"{dataset}.zarr" / "0" / "zarr.json").read_text())
            shape = tuple(int(v) for v in meta["shape"])
            chunks = tuple(int(v) for v in meta["chunk_grid"]["configuration"]["chunk_shape"])
            self.meta[dataset] = (meta, shape, chunks)
        return self.meta[dataset]

    def __call__(self, dataset: str, t: int, frame_cache: dict) -> np.ndarray:
        if t in frame_cache:
            return frame_cache[t]
        meta, shape, chunks = self._meta(dataset)
        index = max(0, min(int(t), shape[0] - 1))
        zarr_path = self.data_dir / f"{dataset}.zarr"
        frame = None
        if chunks[0] == 1 and tuple(chunks[1:]) == tuple(shape[1:]):
            try:
                raw = (zarr_path / "0" / "c" / str(index) / "0" / "0" / "0").read_bytes()
                frame = _decode_chunk(raw, meta, (1, *shape[1:]))[0].copy()
            except Exception:
                frame = None
        if frame is None:
            import zarr
            frame = np.asarray(zarr.open(str(zarr_path / "0"), mode="r")[index])
        self.frames_read += 1
        frame_cache[t] = frame
        return frame


# ----------------------------------------------------------------------------------------------------------------------
# labels
# ----------------------------------------------------------------------------------------------------------------------
def _stem_seed(stem: str, seed: int) -> list[int]:
    return [int(seed), zlib.crc32(stem.encode("utf-8"))]


def extract_labels(stem: str, geff_path: Path, cfg: dict) -> tuple[list[dict], dict]:
    g = read_gt_geff(geff_path)
    ids = g["ids"]
    n = len(ids)
    pos_of = {int(v): i for i, v in enumerate(ids)}
    t = g["t"]
    pts_um = np.stack([g["z"], g["y"], g["x"]], axis=1) * VOXEL_SCALE_UM
    children: list[list[int]] = [[] for _ in range(n)]
    parents: list[list[int]] = [[] for _ in range(n)]
    dropped_edges = 0
    for s, d in g["edges"]:
        a, b = pos_of.get(int(s)), pos_of.get(int(d))
        if a is None or b is None:
            dropped_edges += 1
            continue
        children[a].append(b)
        parents[b].append(a)
    outdeg = np.array([len(c) for c in children])
    indeg = np.array([len(p) for p in parents])
    is_parent = outdeg >= 2
    is_daughter = np.zeros(n, bool)
    for i in np.flatnonzero(is_parent):
        is_daughter[children[i]] = True
    ambiguous = is_parent & is_daughter
    division_node = is_parent | is_daughter

    # lineage distance (frames) to the nearest parent or daughter node among ancestors and descendants
    order = np.argsort(t, kind="stable")
    up = np.full(n, -np.inf)
    for i in order:
        if division_node[i]:
            up[i] = t[i]
        elif parents[i]:
            up[i] = max(up[p] for p in parents[i])
    down = np.full(n, np.inf)
    for i in order[::-1]:
        if division_node[i]:
            down[i] = t[i]
        elif children[i]:
            down[i] = min(down[c] for c in children[i])
    dist = np.minimum(t - up, down - t)
    cont_ok = (indeg == 1) & (outdeg == 1) & ~division_node & (dist >= int(cfg["cont_min_dist"]))

    # hard negatives: cont nodes in the insertion gate of an annotated one-child node (as u or as v)
    gate = cfg["gate"]
    by_t: dict[int, np.ndarray] = {}
    for tt in np.unique(t):
        by_t[int(tt)] = np.flatnonzero(t == tt)
    hard_role: dict[int, set] = {}
    gate_triples = 0
    for u in np.flatnonzero(outdeg == 1):
        c1 = children[u][0]
        if t[c1] != t[u] + 1:
            continue
        vec_c = pts_um[c1] - pts_um[u]
        n_c = float(np.linalg.norm(vec_c))
        if n_c > gate["child_um"]:
            continue
        cand = by_t.get(int(t[u]) + 1)
        if cand is None:
            continue
        cand = cand[cand != c1]
        vec_v = pts_um[cand] - pts_um[u]
        n_v = np.linalg.norm(vec_v, axis=1)
        sister = np.linalg.norm(pts_um[cand] - pts_um[c1], axis=1)
        mid = np.linalg.norm(0.5 * (pts_um[cand] + pts_um[c1]) - pts_um[u], axis=1)
        cos = (vec_v @ vec_c) / np.maximum(n_c * n_v, 1e-9)  # zero-length vector -> cos 0 (passes)
        ok = ((n_v <= gate["v_um"]) & (sister >= gate["sister_min_um"]) & (sister <= gate["sister_max_um"])
              & (mid <= gate["mid_um"]) & (cos <= gate["cos_max"]))
        for v in cand[ok]:
            gate_triples += 1
            if cont_ok[u]:
                hard_role.setdefault(int(u), set()).add("u")
            if cont_ok[v]:
                hard_role.setdefault(int(v), set()).add("v")

    rng = np.random.default_rng(_stem_seed(stem, cfg["seed"]))
    hard_nodes = sorted(hard_role)
    if len(hard_nodes) > cfg["hardneg_per_video"]:
        hard_nodes = sorted(rng.choice(hard_nodes, size=cfg["hardneg_per_video"], replace=False).tolist())
    hard_set = set(hard_nodes)
    cont_pool = [i for i in np.flatnonzero(cont_ok) if int(i) not in hard_set]
    if len(cont_pool) > cfg["cont_per_video"]:
        cont_pool = sorted(rng.choice(cont_pool, size=cfg["cont_per_video"], replace=False).tolist())

    rows: list[dict] = []

    def add(i: int, label: str, kind: str) -> None:
        rows.append({"stem": stem, "node_id": int(ids[i]), "t": int(t[i]), "z": float(g["z"][i]),
                     "y": float(g["y"][i]), "x": float(g["x"][i]), "label": label, "kind": kind})

    for i in np.flatnonzero(is_parent & ~ambiguous):
        add(int(i), "parent", "parent")
    for i in np.flatnonzero(is_daughter & ~ambiguous):
        add(int(i), "daughter", "daughter")
    for i in cont_pool:
        add(int(i), "cont", "cont")
    for i in hard_nodes:
        add(int(i), "cont", "hardneg_" + "".join(sorted(hard_role[i])))
    stats = {
        "stem": stem, "embryo": stem[:4], "gt_nodes": int(n), "gt_edges": int(len(g["edges"])),
        "dropped_edges": int(dropped_edges), "divisions": int(is_parent.sum()),
        "parent": int((is_parent & ~ambiguous).sum()), "daughter": int((is_daughter & ~ambiguous).sum()),
        "ambiguous_dropped": int(ambiguous.sum()), "cont_eligible": int(cont_ok.sum()),
        "cont": len(cont_pool), "gate_triples": int(gate_triples), "hardneg_candidates": len(hard_role),
        "hardneg": len(hard_nodes),
        "hardneg_u": sum(1 for i in hard_nodes if "u" in hard_role[i]),
        "hardneg_v": sum(1 for i in hard_nodes if "v" in hard_role[i]),
        "edge_dt_not_1": int(sum(1 for a in range(n) for b in children[a] if t[b] - t[a] != 1)),
    }
    return rows, stats


# ----------------------------------------------------------------------------------------------------------------------
# folds
# ----------------------------------------------------------------------------------------------------------------------
def make_splits_inline(n_div: dict[str, int], n_folds: int = 5, seed: int = 0) -> dict[str, int]:
    """Fallback only (used when no splits.json is available): 5 folds grouped by video, stratified by embryo prefix
    and division count, seed 0. Per embryo: videos in seeded random order, stable-sorted by division count (desc);
    division videos go greedily to the fold with the fewest divisions (then fewest videos), zero-division videos to
    the fold with the fewest videos of that embryo."""
    rng = np.random.default_rng(seed)
    folds: dict[str, int] = {}
    for emb in sorted({s[:4] for s in n_div}):
        vids = sorted(s for s in n_div if s[:4] == emb)
        vids = [vids[i] for i in rng.permutation(len(vids))]
        vids.sort(key=lambda s: -n_div[s])
        div_sum, cnt = [0] * n_folds, [0] * n_folds
        for s in vids:
            if n_div[s] > 0:
                f = min(range(n_folds), key=lambda k: (div_sum[k], cnt[k], k))
            else:
                f = min(range(n_folds), key=lambda k: (cnt[k], k))
            folds[s] = f
            div_sum[f] += n_div[s]
            cnt[f] += 1
    return folds


def load_splits(path: Path) -> dict[str, int] | None:
    if not path or not Path(path).is_file():
        return None
    d = json.loads(Path(path).read_text())
    if isinstance(d, dict) and isinstance(d.get("folds"), dict):
        return {str(k): int(v) for k, v in d["folds"].items()}
    if isinstance(d, dict) and isinstance(d.get("folds"), list):
        return {str(s): i for i, group in enumerate(d["folds"]) for s in group}
    if isinstance(d, dict) and all(isinstance(v, int) for v in d.values()):
        return {str(k): int(v) for k, v in d.items()}
    if isinstance(d, list):
        return {str(r["stem"]): int(r["fold"]) for r in d}
    raise ValueError(f"unrecognised splits format in {path}")


def _default_splits_path() -> Path | None:
    here = Path(__file__).resolve().parent
    for p in (here / "splits.json", here.parent / "splits.json"):
        if p.is_file():
            return p
    return None


# ----------------------------------------------------------------------------------------------------------------------
# step 1: prepare
# ----------------------------------------------------------------------------------------------------------------------
def step_prepare(cfg: dict) -> dict:
    import pandas as pd

    t0 = time.time()
    data_dir = resolve_data_dir(cfg)
    work = Path(cfg["work_dir"])
    work.mkdir(parents=True, exist_ok=True)
    cache = resolve_cache_dir(cfg)
    cache.mkdir(parents=True, exist_ok=True)
    all_stems = sorted(p.name[:-5] for p in data_dir.iterdir() if p.name.endswith(".geff")
                       and (data_dir / f"{p.name[:-5]}.zarr").exists())
    log(f"[prepare] data_dir={data_dir} videos with .zarr+.geff: {len(all_stems)}; cache={cache}; work={work}")
    if not all_stems:
        raise FileNotFoundError(f"no <stem>.zarr + <stem>.geff pairs under {data_dir}")

    # GT labels for every video (cheap: the .geff files are tiny); per-video try/except
    label_rows, stats_rows, n_div = [], [], {}
    for i, stem in enumerate(all_stems):
        ts = time.time()
        try:
            rows, st = extract_labels(stem, data_dir / f"{stem}.geff", cfg)
            st["label_secs"] = round(time.time() - ts, 3)
            label_rows.append(rows)
            stats_rows.append(st)
            n_div[stem] = st["divisions"]
        except Exception as exc:
            log(f"[prepare] {stem}: label extraction FAILED {type(exc).__name__}: {exc}")
            stats_rows.append({"stem": stem, "embryo": stem[:4], "error": f"{type(exc).__name__}: {exc}"})
            label_rows.append([])
            n_div[stem] = 0
    log(f"[prepare] GT parsed for {len(all_stems)} videos in {time.time() - t0:.1f} s; "
        f"divisions {sum(n_div.values())} in {sum(1 for v in n_div.values() if v)} videos; zstd decoder {decoder_names()['zstd']}")

    # folds
    splits_path = Path(cfg["splits_path"]) if cfg.get("splits_path") else _default_splits_path()
    splits = load_splits(splits_path) if splits_path else None
    splits_source = str(splits_path) if splits else "inline make_splits_inline(seed=0)"
    if splits is None:
        splits = make_splits_inline(n_div, 5, 0)
    missing = [s for s in all_stems if s not in splits]
    if missing:
        log(f"[prepare] WARNING {len(missing)} stems missing from splits -> inline fold rule for them")
        extra = make_splits_inline({s: n_div[s] for s in missing}, 5, 0)
        splits.update(extra)

    # video selection
    if cfg["stems"]:
        stems = [s for s in cfg["stems"] if s in set(all_stems)]
    else:
        limit = cfg["max_videos"] or 0
        if cfg["smoke"]:
            limit = min(limit, cfg["smoke_videos"]) if limit else cfg["smoke_videos"]
        if limit and limit < len(all_stems):
            by_emb = {e: sorted((s for s in all_stems if s[:4] == e), key=lambda s: (-n_div[s], s))
                      for e in sorted({s[:4] for s in all_stems})}
            stems, k = [], 0
            while len(stems) < limit:  # alternate embryos, division-rich videos first
                emb = sorted(by_emb, reverse=True)[k % len(by_emb)]
                if by_emb[emb]:
                    stems.append(by_emb[emb].pop(0))
                k += 1
                if not any(by_emb.values()):
                    break
            stems = sorted(stems)
        else:
            stems = list(all_stems)
    n_folds = int(cfg["n_folds"])
    orig_folds = sorted({splits[s] for s in splits})
    if n_folds == len(orig_folds) and len(stems) == len(all_stems):
        folds = {s: int(splits[s]) for s in stems}
    else:
        folds = {s: int(splits[s]) % n_folds for s in stems}
        if len({folds[s] for s in stems}) < min(n_folds, len(stems)):  # small subsets: deal round-robin
            ordered = sorted(stems, key=lambda s: (splits[s], s))
            folds = {s: i % n_folds for i, s in enumerate(ordered)}

    chosen = set(stems)
    rows = [r for stem, rs in zip(all_stems, label_rows) if stem in chosen for r in rs]
    meta = pd.DataFrame(rows, columns=["stem", "node_id", "t", "z", "y", "x", "label", "kind"])
    meta["label_idx"] = meta["label"].map(CLASS_INDEX).astype(int)
    meta["fold"] = meta["stem"].map(folds).astype(int)
    meta["embryo"] = meta["stem"].str[:4]
    meta = meta.sort_values(["stem", "t", "node_id", "kind"]).reset_index(drop=True)
    stats = pd.DataFrame(stats_rows)
    stats["selected"] = stats["stem"].isin(stems)
    stats["fold"] = stats["stem"].map(folds)
    (work / "splits_used.json").write_text(json.dumps(
        {"source": splits_source, "n_folds": n_folds, "folds": {s: folds[s] for s in stems}}, indent=1))
    log(f"[prepare] folds from {splits_source}; selected {len(stems)} videos, {len(meta)} samples; "
        f"per fold videos {dict(sorted(pd.Series(folds).value_counts().items()))}")
    _print_label_counts(meta)
    return {"data_dir": str(data_dir), "cache_dir": str(cache), "work_dir": str(work), "stems": stems,
            "folds": folds, "meta": meta, "stats": stats, "splits_source": splits_source,
            "timing": {"prepare_s": round(time.time() - t0, 1)}}


def _print_label_counts(meta) -> None:
    if meta.empty:
        log("[prepare] no labelled samples")
        return
    tab = meta.groupby(["embryo", "kind"]).size().unstack(fill_value=0)
    log("[prepare] samples by embryo x kind:\n" + tab.to_string())
    tab = meta.groupby(["fold", "label"]).size().unstack(fill_value=0)
    log("[prepare] samples by fold x label:\n" + tab.to_string())


# ----------------------------------------------------------------------------------------------------------------------
# step 2: crops
# ----------------------------------------------------------------------------------------------------------------------
def _big_cfg() -> dict:
    cfg = copy.deepcopy(DEFAULT_CFG)
    cfg["input"]["crop_z"] = BIG[0]
    cfg["input"]["crop_yx"] = BIG[1]
    return cfg


def _build_worker_init(n_threads: int) -> None:
    try:
        import blosc2
        blosc2.set_nthreads(max(1, n_threads))
    except Exception:
        pass
    try:
        import torch
        torch.set_num_threads(1)
    except Exception:
        pass


def crop_video(job: dict) -> dict:
    """All crops of one video: frames are read once (sorted by t), prepared frames kept for lags -1..+2 only."""
    t0 = time.time()
    stem = job["stem"]
    try:
        reader = FrameReader(Path(job["data_dir"]))
        prepared: dict = {}
        bundle = {"config": _big_cfg(), "prepared_frames": prepared}
        ref_bundle = {"config": copy.deepcopy(DEFAULT_CFG), "prepared_frames": prepared}
        frame_cache: dict = {}
        nodes = job["nodes"]
        out = np.empty((len(nodes), 4, *BIG), dtype=np.dtype(job["dtype"]))
        checked = 0
        inner = (slice(None), slice(MARGIN, MARGIN + CROP[0]), slice(MARGIN, MARGIN + CROP[1]),
                 slice(MARGIN, MARGIN + CROP[2]))
        for i in sorted(range(len(nodes)), key=lambda k: nodes[k][0]):
            tt, z, y, x = nodes[i]
            node = {"t": int(tt), "z": float(z), "y": float(y), "x": float(x)}
            sample = prepare_sample(stem, int(tt), node, bundle, frame_cache, reader)
            if sample.shape != (5, *BIG):
                raise RuntimeError(f"unexpected enlarged sample shape {sample.shape}")
            out[i] = sample[:4]
            if checked < job["checks"]:
                ref = prepare_sample(stem, int(tt), node, ref_bundle, frame_cache, reader)
                if ref.shape != (5, *CROP) or not np.array_equal(sample[inner], ref):
                    raise RuntimeError("inner crop != DivNet-contract sample (contract drift)")
                checked += 1
            for key in [k for k in prepared if k[1] < int(tt) - 1]:
                prepared.pop(key)
        prepared.clear()
        frame_cache.clear()
        return {"stem": stem, "crops": out, "secs": time.time() - t0, "error": None, "checked": checked,
                "frames_read": reader.frames_read, "decoders": decoder_names()}
    except Exception as exc:
        return {"stem": stem, "crops": None, "secs": time.time() - t0, "error": f"{type(exc).__name__}: {exc}",
                "checked": 0, "frames_read": 0, "decoders": decoder_names()}


def step_build_cache(cfg: dict, state: dict) -> dict:
    import multiprocessing as mp

    t0 = time.time()
    meta = state["meta"]
    cache = Path(state["cache_dir"])
    crops_path = cache / "crops.npy"
    dtype = np.dtype(cfg["cache_dtype"])
    n = len(meta)
    need = n * 4 * int(np.prod(BIG)) * dtype.itemsize
    try:
        import shutil
        free = shutil.disk_usage(cache).free
        log(f"[build] cache disk free {free / 2**30:.1f} GiB, needed {need / 2**30:.2f} GiB")
        if free < 1.2 * need and dtype == np.float32:
            dtype = np.dtype(np.float16)
            log("[build] WARNING not enough disk for float32 -> caching float16 (OOF inputs rounded to fp16)")
    except Exception:
        pass
    state["cache_dtype"] = dtype.name
    log(f"[build] {n} samples -> {crops_path} ({n * 4 * int(np.prod(BIG)) * dtype.itemsize / 2**30:.2f} GiB {dtype})")
    crops = np.lib.format.open_memmap(crops_path, mode="w+", dtype=dtype, shape=(max(n, 1), 4, *BIG))
    jobs = []
    for stem, grp in meta.groupby("stem", sort=True):
        jobs.append({"stem": stem, "data_dir": state["data_dir"], "dtype": dtype.name, "checks": cfg["contract_checks"],
                     "index": grp.index.to_numpy(),
                     "nodes": list(zip(grp["t"].tolist(), grp["z"].tolist(), grp["y"].tolist(), grp["x"].tolist()))})
    n_workers = cfg["build_workers"] or min(4, os.cpu_count() or 1)
    n_workers = max(1, min(n_workers, len(jobs) or 1))
    per_worker_threads = max(1, (os.cpu_count() or 1) // n_workers)
    valid = np.zeros(n, bool)
    video_rows = []
    lite = [{k: v for k, v in j.items() if k != "index"} for j in jobs]
    index_of = {j["stem"]: j["index"] for j in jobs}
    done = 0
    ctx = mp.get_context("spawn")
    with ctx.Pool(n_workers, initializer=_build_worker_init, initargs=(per_worker_threads,)) as pool:
        for res in pool.imap_unordered(crop_video, lite):
            done += 1
            stem = res["stem"]
            idx = index_of[stem]
            grp = meta.loc[idx]
            counts = grp["kind"].value_counts().to_dict()
            if res["error"] is None:
                crops[idx] = res["crops"]
                valid[idx] = True
                status = "ok"
            else:
                status = "FAILED " + res["error"]
            video_rows.append({"stem": stem, "crop_secs": round(res["secs"], 2), "frames_read": res["frames_read"],
                               "contract_checks": res["checked"], "crop_error": res["error"], "n_samples": len(idx)})
            log(f"[build] {done}/{len(jobs)} {stem} n={len(idx)} "
                + " ".join(f"{k}={v}" for k, v in sorted(counts.items()))
                + f" frames={res['frames_read']} {res['secs']:.1f}s decoders={res['decoders']} {status}")
    crops.flush()
    del crops
    meta = meta.copy()
    meta["valid"] = valid
    meta.to_csv(cache / "meta.csv", index_label="row")
    import pandas as pd
    vid = pd.DataFrame(video_rows)
    stats = state["stats"].merge(vid, on="stem", how="left") if not vid.empty else state["stats"]
    stats.to_csv(Path(state["work_dir"]) / "labels_summary.csv", index=False)
    state["meta"] = meta
    state["stats"] = stats
    secs = time.time() - t0
    state["timing"]["build_s"] = round(secs, 1)
    ok = vid[vid["crop_error"].isna()] if not vid.empty else vid
    per_video = float(ok["crop_secs"].mean()) if len(ok) else float("nan")
    state["timing"]["crop_s_per_video_mean"] = round(per_video, 2)
    log(f"[build] done in {secs:.1f} s with {n_workers} workers; valid samples {int(valid.sum())}/{n}; "
        f"videos failed {int(vid['crop_error'].notna().sum()) if not vid.empty else 0}; mean crop time per video "
        f"{per_video:.2f} s (single worker)")
    return state


# ----------------------------------------------------------------------------------------------------------------------
# step 3: training (subprocess per fold)
# ----------------------------------------------------------------------------------------------------------------------
def _src_paths() -> list[str]:
    import tools.daughternet as dn  # noqa: F401  (the tools package the kernel materialised or the repo copy)
    paths = [str(Path(__file__).resolve().parent), str(Path(dn.__file__).resolve().parent.parent)]
    return list(dict.fromkeys(paths))


def _fold_dir(work: Path, fold: int) -> Path:
    return work / "folds" / f"fold_{fold}"


def _pump(stream, prefix: str, sink) -> None:
    for line in iter(stream.readline, ""):
        print(prefix + line.rstrip(), flush=True)
        sink.write(line)
        sink.flush()
    stream.close()


def step_train(cfg: dict, state: dict) -> dict:
    import torch

    t0 = time.time()
    work = Path(state["work_dir"])
    cache = Path(state["cache_dir"])
    meta = state["meta"]
    folds = sorted(int(f) for f in meta.loc[meta["valid"], "fold"].unique())
    (work / "folds").mkdir(parents=True, exist_ok=True)
    cfg_path = cache / "kdn_cfg.json"
    cfg_path.write_text(json.dumps({**cfg, "_cache_dir": str(cache), "_work_dir": str(work)}, indent=1))
    n_gpu = torch.cuda.device_count() if cfg["gpus"] != 0 else 0
    if cfg["gpus"] > 0:
        n_gpu = min(n_gpu, cfg["gpus"])
    slots = [str(i) for i in range(n_gpu)] or ["cpu"]
    log(f"[train] folds {folds} on slots {slots} (subprocess per fold)")
    env_base = os.environ.copy()
    env_base["PYTHONPATH"] = os.pathsep.join(_src_paths() + [p for p in env_base.get("PYTHONPATH", "").split(os.pathsep) if p])
    env_base["PYTHONUNBUFFERED"] = "1"
    queue = list(folds)
    running: dict[str, tuple] = {}
    results: dict[int, int] = {}
    while queue or running:
        for slot in slots:
            if slot not in running and queue:
                fold = queue.pop(0)
                fdir = _fold_dir(work, fold)
                fdir.mkdir(parents=True, exist_ok=True)
                # a rerun into the same work dir must never pick up a previous run's fold model / OOF rows
                # (a fold that fails or never saves best.pt would otherwise load or merge stale files silently)
                for stale in ("best.pt", "last.pt", "oof.csv", "summary.json", "history.json", "train.log"):
                    (fdir / stale).unlink(missing_ok=True)
                env = dict(env_base)
                if slot != "cpu":
                    env["CUDA_VISIBLE_DEVICES"] = slot
                device = "cuda:0" if slot != "cpu" else "cpu"
                cmd = [sys.executable, str(Path(__file__).resolve()), "worker", "--cfg", str(cfg_path),
                       "--fold", str(fold), "--device", device, "--threads",
                       str(max(1, (os.cpu_count() or 1) // len(slots)))]
                sink = open(fdir / "train.log", "a", encoding="utf-8")
                proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                        encoding="utf-8", errors="replace")
                th = threading.Thread(target=_pump, args=(proc.stdout, f"[fold {fold}@{slot}] ", sink), daemon=True)
                th.start()
                running[slot] = (fold, proc, th, sink, time.time())
                log(f"[train] started fold {fold} on {slot} (pid {proc.pid})")
        time.sleep(1.0)
        for slot in list(running):
            fold, proc, th, sink, ts = running[slot]
            if proc.poll() is not None:
                th.join(timeout=10)
                sink.close()
                results[fold] = proc.returncode
                log(f"[train] fold {fold} finished rc={proc.returncode} in {time.time() - ts:.0f} s")
                del running[slot]
    state["train_rc"] = results
    state["timing"]["train_s"] = round(time.time() - t0, 1)
    failed = [f for f, rc in results.items() if rc != 0]
    if failed:
        log(f"[train] WARNING folds failed: {failed} (their videos get no OOF prediction)")
    return state


def _load_split(crops, rows: np.ndarray, inner_only: bool, dtype, device, torch, chunk: int = 1024):
    """Rows of the memmap -> one tensor on device; inner_only keeps the contract 16x32x32 crop."""
    if len(rows) == 0:
        shape = (0, 4, *CROP) if inner_only else (0, 4, *BIG)
        return torch.zeros(shape, dtype=dtype, device=device)
    parts = []
    for s in range(0, len(rows), chunk):
        block = np.asarray(crops[rows[s:s + chunk]], dtype=np.float32)
        if inner_only:
            block = block[:, :, MARGIN:MARGIN + CROP[0], MARGIN:MARGIN + CROP[1], MARGIN:MARGIN + CROP[2]]
        parts.append(torch.from_numpy(np.ascontiguousarray(block)).to(device=device, dtype=dtype))
    return torch.cat(parts)


def augment_batch(xb, rng: np.random.Generator, cfg: dict, marker, torch):
    """(B, 4, 18, 34, 34) image crops -> (B, 5, 16, 32, 32): +-jitter crop (image shifts, marker stays centred), then
    random flips on z/y/x and a random k*90 degree rotation in yx applied to all 5 channels, then a per-sample
    intensity gain on the 4 image channels (clipped back to the contract range [-0.5, 6])."""
    b = xb.shape[0]
    dev = xb.device
    j = int(cfg["jitter"])
    offs = torch.from_numpy(rng.integers(MARGIN - j, MARGIN + j + 1, size=(b, 3))).to(dev)
    zi = offs[:, 0, None] + torch.arange(CROP[0], device=dev)
    yi = offs[:, 1, None] + torch.arange(CROP[1], device=dev)
    xi = offs[:, 2, None] + torch.arange(CROP[2], device=dev)
    bi = torch.arange(b, device=dev)[:, None, None, None]
    img = xb[bi, :, zi[:, :, None, None], yi[:, None, :, None], xi[:, None, None, :]]  # (B, 16, 32, 32, 4)
    img = img.permute(0, 4, 1, 2, 3).float()
    x = torch.cat([img, marker.to(dev).expand(b, 1, *CROP)], dim=1)
    flips = torch.from_numpy(rng.random((b, 3)) < 0.5).to(dev)
    for axis, dim in enumerate((2, 3, 4)):
        m = flips[:, axis].view(b, 1, 1, 1, 1)
        x = torch.where(m, x.flip(dim), x)
    rot = rng.integers(0, 4, size=b)
    for k in (1, 2, 3):
        sel = np.flatnonzero(rot == k)
        if len(sel):
            idx = torch.from_numpy(sel).to(dev)
            x[idx] = torch.rot90(x[idx], k, dims=(3, 4))
    gain = torch.from_numpy(rng.uniform(cfg["gain"][0], cfg["gain"][1], size=(b, 1, 1, 1, 1)).astype(np.float32)).to(dev)
    x[:, :4] = (x[:, :4] * gain).clamp(-0.5, 6.0)
    return x


def contract_marker(torch):
    sigma = tuple(float(v) for v in DEFAULT_CFG["input"]["marker_sigma"])
    return torch.from_numpy(_marker(CROP, sigma)).view(1, 1, *CROP)


def predict_inner(model, x_inner, marker, batch: int, torch) -> np.ndarray:
    """Softmax (N, 3) for contract samples (image inner crops + centred marker), fp32 like score_nodes."""
    out = []
    model.eval()
    with torch.no_grad():
        for s in range(0, x_inner.shape[0], batch):
            xb = x_inner[s:s + batch].float()
            x = torch.cat([xb, marker.to(xb.device).expand(xb.shape[0], 1, *CROP)], dim=1)
            out.append(torch.softmax(model(x).float(), dim=1).cpu().numpy())
    return np.concatenate(out) if out else np.zeros((0, len(CLASSES)), np.float32)


def auc_score(scores, positive) -> float | None:
    import pandas as pd
    s = np.asarray(scores, dtype=np.float64)
    y = np.asarray(positive, dtype=bool)
    n1, n0 = int(y.sum()), int((~y).sum())
    if n1 == 0 or n0 == 0:
        return None
    ranks = pd.Series(s).rank(method="average").to_numpy()
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def _val_metrics(probs: np.ndarray, y: np.ndarray) -> dict:
    if len(y) == 0:
        return {"n": 0}
    p_true = np.clip(probs[np.arange(len(y)), y], 1e-7, 1.0)
    ce = -np.log(p_true)
    present = [c for c in range(len(CLASSES)) if (y == c).any()]
    macro = float(np.mean([ce[y == c].mean() for c in present]))
    res = {"n": int(len(y)), "macro_ce": macro, "ce": float(ce.mean()),
           "acc": float((probs.argmax(1) == y).mean())}
    for c, name in enumerate(CLASSES):
        res[f"n_{name}"] = int((y == c).sum())
        res[f"ce_{name}"] = float(ce[y == c].mean()) if (y == c).any() else None
        res[f"auc_{name}"] = auc_score(probs[:, c], y == c)
    return res


def _atomic_save(obj, path: Path, torch) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    torch.save(obj, tmp)
    os.replace(tmp, path)


def train_fold(cfg: dict, fold: int, device_str: str, threads: int = 0) -> dict:
    import pandas as pd
    import torch

    t_start = time.time()
    if threads:
        torch.set_num_threads(int(threads))
    cache = Path(cfg["_cache_dir"])
    work = Path(cfg["_work_dir"])
    fdir = _fold_dir(work, fold)
    fdir.mkdir(parents=True, exist_ok=True)
    device = torch.device(device_str)
    use_cuda = device.type == "cuda"
    if use_cuda:
        torch.backends.cudnn.benchmark = True
    seed = int(cfg["seed"]) * 1000 + int(fold)
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    meta = pd.read_csv(cache / "meta.csv", index_col="row")
    crops = np.load(cache / "crops.npy", mmap_mode="r")
    meta = meta[meta["valid"].astype(bool)]
    n_folds = int(cfg["n_folds"])
    if cfg.get("inner_val") and n_folds < 3:
        log(f"fold {fold}: KDN_INNER_VAL needs >= 3 folds (have {n_folds}) -> early stopping on the OOF fold")
        cfg = {**cfg, "inner_val": False}
    if cfg.get("inner_val"):
        es_fold = (fold + 1) % n_folds
        train_mask = ~meta["fold"].isin([fold, es_fold])
        es_mask = meta["fold"] == es_fold
    else:
        es_fold = fold
        train_mask = meta["fold"] != fold
        es_mask = meta["fold"] == fold
    oof_mask = meta["fold"] == fold
    tr_rows = meta.index[train_mask].to_numpy()
    es_rows = meta.index[es_mask].to_numpy()
    oof_rows = meta.index[oof_mask].to_numpy()
    y_tr = meta.loc[tr_rows, "label_idx"].to_numpy().astype(np.int64)
    y_es = meta.loc[es_rows, "label_idx"].to_numpy().astype(np.int64)
    log(f"fold {fold}: device {device} train {len(tr_rows)} {np.bincount(y_tr, minlength=3).tolist()} | "
        f"early-stop fold {es_fold}: {len(es_rows)} {np.bincount(y_es, minlength=3).tolist()} | oof {len(oof_rows)}")
    if len(tr_rows) == 0:
        raise RuntimeError("no training samples")
    store_dtype = torch.float16 if use_cuda else torch.float32
    t_load = time.time()
    x_tr = _load_split(crops, tr_rows, False, store_dtype, device, torch)
    x_es = _load_split(crops, es_rows, True, torch.float32, device, torch)
    y_tr_t = torch.from_numpy(y_tr).to(device)
    log(f"fold {fold}: loaded crops in {time.time() - t_load:.1f} s (train {tuple(x_tr.shape)} {x_tr.dtype})")
    marker = contract_marker(torch).to(device)

    ckpt_cfg = copy.deepcopy(DEFAULT_CFG)
    ckpt_cfg["classes"] = list(CLASSES)
    ckpt_cfg["train"] = {k: cfg[k] for k in ("epochs", "patience", "batch", "lr", "weight_decay", "warmup_frac",
                                               "epoch_samples", "jitter", "gain", "seed", "cont_per_video",
                                               "hardneg_per_video", "cont_min_dist", "inner_val", "n_folds")}
    ckpt_cfg["train"].update({"fold": fold, "early_stop_fold": es_fold, "kernel": "biohub-l2-kdn-train"})
    model = build_model(ckpt_cfg).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=cfg["weight_decay"])
    classes_present = [c for c in range(len(CLASSES)) if (y_tr == c).any()]
    pools = {c: np.flatnonzero(y_tr == c) for c in classes_present}
    epoch_samples = int(cfg["epoch_samples"]) or len(tr_rows)
    steps_per_epoch = max(1, math.ceil(epoch_samples / cfg["batch"]))
    total_steps = steps_per_epoch * int(cfg["epochs"])
    warmup = max(1, int(cfg["warmup_frac"] * total_steps))

    def lr_at(step: int) -> float:
        if step < warmup:
            return cfg["lr"] * (step + 1) / warmup
        prog = (step - warmup) / max(1, total_steps - warmup)
        return cfg["lr"] * 0.5 * (1.0 + math.cos(math.pi * min(1.0, prog)))

    use_amp = bool(cfg["amp"]) and use_cuda
    try:
        scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    except Exception:  # older torch
        scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    best, best_epoch, bad, step = float("inf"), -1, 0, 0
    history = []
    for epoch in range(int(cfg["epochs"])):
        te = time.time()
        model.train()
        cls = rng.choice(classes_present, size=epoch_samples)
        order = np.empty(epoch_samples, dtype=np.int64)
        for c in classes_present:
            sel = np.flatnonzero(cls == c)
            order[sel] = rng.choice(pools[c], size=len(sel), replace=True)
        rng.shuffle(order)
        run_loss, seen = torch.zeros((), device=device), 0
        for s in range(0, epoch_samples, cfg["batch"]):
            idx = order[s:s + cfg["batch"]]
            idx_t = torch.from_numpy(idx).to(device)
            xb = augment_batch(x_tr[idx_t], rng, cfg, marker, torch)
            yb = y_tr_t[idx_t]
            for group in opt.param_groups:
                group["lr"] = lr_at(step)
            opt.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, dtype=torch.float16, enabled=use_amp):
                logits = model(xb)
            loss = torch.nn.functional.cross_entropy(logits.float(), yb)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            run_loss += loss.detach() * len(idx)
            seen += len(idx)
            step += 1
        train_loss = float(run_loss) / max(1, seen)
        if use_cuda:
            torch.cuda.synchronize()
        train_secs = time.time() - te
        probs = predict_inner(model, x_es, marker, cfg["eval_batch"], torch)
        vm = _val_metrics(probs, y_es)
        val_loss = vm.get("macro_ce", float("nan")) if vm["n"] else float("nan")
        improved = vm["n"] > 0 and val_loss < best
        state_cpu = {k: v.detach().cpu() for k, v in model.state_dict().items()}
        payload = {"model_state": state_cpu, "config": ckpt_cfg, "fold": int(fold), "epoch": int(epoch),
                   "val_loss": float(val_loss)}
        _atomic_save(payload, fdir / "last.pt", torch)
        if improved or (vm["n"] == 0):
            best, best_epoch, bad = (val_loss if vm["n"] else best), epoch, 0
            _atomic_save(payload, fdir / "best.pt", torch)
        else:
            bad += 1
        rec = {"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss, "lr": lr_at(step - 1),
               "secs": round(time.time() - te, 1), "train_secs": round(train_secs, 1),
               "samples_per_s": round(seen / max(1e-9, train_secs), 1),
               **{f"val_{k}": v for k, v in vm.items()}}
        history.append(rec)
        (fdir / "history.json").write_text(json.dumps(history, indent=1))
        auc_txt = " ".join(f"auc_{n}={vm.get('auc_' + n) if vm.get('auc_' + n) is None else round(vm['auc_' + n], 3)}"
                           for n in CLASSES)
        log(f"fold {fold} epoch {epoch}: train {train_loss:.4f} val(macro CE) {val_loss:.4f} "
            f"{'*' if improved else ' '} {auc_txt} {rec['secs']}s (train {rec['samples_per_s']} samples/s)")
        if vm["n"] and bad >= int(cfg["patience"]):
            log(f"fold {fold}: early stop at epoch {epoch} (best {best_epoch}, val {best:.4f})")
            break
    del x_tr
    if not (fdir / "best.pt").is_file():
        raise RuntimeError(f"fold {fold}: no best.pt written in this run (epochs={cfg['epochs']}, history "
                           f"{[h['val_loss'] for h in history]}) -> no OOF for this fold")
    # OOF prediction with best.pt through the shared loader (same path the submission patch uses)
    bundle = load_daughternet([fdir / "best.pt"], device=str(device))
    x_oof = _load_split(crops, oof_rows, True, torch.float32, device, torch)
    p_oof = predict_inner(bundle["models"][0], x_oof, marker, cfg["eval_batch"], torch)
    oof = pd.DataFrame({"row": oof_rows, "p_cont": p_oof[:, 0], "p_par": p_oof[:, 1], "p_dau": p_oof[:, 2]})
    oof.to_csv(fdir / "oof.csv", index=False)
    y_oof = meta.loc[oof_rows, "label_idx"].to_numpy().astype(np.int64)
    om = _val_metrics(p_oof, y_oof)
    summary = {"fold": fold, "best_epoch": best_epoch, "best_val_loss": best, "epochs_run": len(history),
               "early_stop_fold": es_fold, "n_train": int(len(tr_rows)), "n_oof": int(len(oof_rows)),
               "train_counts": np.bincount(y_tr, minlength=3).tolist(), "oof_metrics": om,
               "secs": round(time.time() - t_start, 1), "device": str(device)}
    (fdir / "summary.json").write_text(json.dumps(summary, indent=1))
    log(f"fold {fold}: OOF {len(oof_rows)} samples macro CE {om.get('macro_ce')} "
        f"auc_parent {om.get('auc_parent')} auc_daughter {om.get('auc_daughter')}; total {summary['secs']} s")
    return summary


def worker_main(argv: list[str]) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", required=True)
    ap.add_argument("--fold", type=int, required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=0)
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.cfg).read_text())
    train_fold(cfg, a.fold, a.device, a.threads)
    return 0


# ----------------------------------------------------------------------------------------------------------------------
# step 4: OOF merge, readout, DivNet comparison
# ----------------------------------------------------------------------------------------------------------------------
TOP_FRACS = (("top0.1%", 0.001), ("top1%", 0.01), ("top5%", 0.05))


def _rank_block(scores: np.ndarray, positive: np.ndarray) -> dict:
    n = len(scores)
    n_pos = int(positive.sum())
    base = n_pos / n if n else None
    out = {"n": int(n), "n_pos": n_pos, "base_rate": base, "auc": auc_score(scores, positive)}
    order = np.argsort(-scores, kind="stable")
    for name, frac in TOP_FRACS:
        if n == 0:
            out[name] = None
            continue
        k = max(1, int(math.ceil(frac * n)))
        tp = int(positive[order[:k]].sum())
        fp = k - tp
        prec = tp / k
        tpr = tp / n_pos if n_pos else None
        fpr = fp / (n - n_pos) if n - n_pos else None
        lr_plus = (tpr / fpr) if (tpr is not None and fpr) else None
        out[name] = {"k": k, "tp": tp, "precision": prec, "lift": (prec / base) if base else None,
                     "lr_plus": lr_plus, "lr_plus_infinite": bool(fpr == 0 and tp > 0)}
    return out


def _find_divnet_checkpoint(cfg: dict) -> Path | None:
    if cfg.get("divnet_checkpoint"):
        p = Path(cfg["divnet_checkpoint"])
        return p if p.is_file() else None
    for p in _checkpoint_candidates():
        if Path(p).is_file():
            return Path(p)
    root = Path("/kaggle/input")
    if root.exists():  # pruned walk: a plain rglob would descend into every competition .zarr chunk tree
        found = []
        for dirpath, dirnames, files in os.walk(root, followlinks=True):
            depth = Path(dirpath).relative_to(root).parts
            dirnames[:] = [] if len(depth) >= 6 else sorted(
                d for d in dirnames if not d.endswith((".zarr", ".geff")) and not d.startswith("."))
            if "best_overall.pt" in files and "divnet" in dirpath.lower():
                found.append(Path(dirpath) / "best_overall.pt")
        if found:
            return sorted(found)[0]
    return None


def step_oof(cfg: dict, state: dict) -> dict:
    import pandas as pd
    import torch

    t0 = time.time()
    work = Path(state["work_dir"])
    cache = Path(state["cache_dir"])
    meta = pd.read_csv(cache / "meta.csv", index_col="row")
    meta = meta[meta["valid"].astype(bool)].copy()
    for col in ("p_cont", "p_par", "p_dau"):
        meta[col] = np.nan
    fold_summaries = {}
    for fold in sorted(meta["fold"].unique()):
        fdir = _fold_dir(work, int(fold))
        f_oof = fdir / "oof.csv"
        if f_oof.is_file():
            o = pd.read_csv(f_oof).set_index("row")
            meta.loc[o.index, ["p_cont", "p_par", "p_dau"]] = o[["p_cont", "p_par", "p_dau"]].to_numpy()
        if (fdir / "summary.json").is_file():
            fold_summaries[int(fold)] = json.loads((fdir / "summary.json").read_text())
    has_p = meta["p_par"].notna()
    log(f"[oof] predictions for {int(has_p.sum())}/{len(meta)} samples")

    divnet_info = {"enabled": bool(cfg["divnet_compare"])}
    if cfg["divnet_compare"]:
        try:
            ckpt = _find_divnet_checkpoint(cfg)
            if ckpt is None:
                raise FileNotFoundError("best_overall.pt not found")
            bundle = load_divnet_mitosis_model(ckpt)
            dev = bundle["device"]
            crops = np.load(cache / "crops.npy", mmap_mode="r")
            marker = contract_marker(torch).to(dev)
            rows = meta.index.to_numpy()
            ps = []
            for s in range(0, len(rows), 1024):
                x_in = _load_split(crops, rows[s:s + 1024], True, torch.float32, dev, torch)
                with torch.no_grad():
                    for b in range(0, x_in.shape[0], cfg["eval_batch"]):
                        xb = x_in[b:b + cfg["eval_batch"]]
                        x = torch.cat([xb, marker.expand(xb.shape[0], 1, *CROP)], dim=1)
                        ps.append(torch.sigmoid(bundle["model"](x)).flatten().float().cpu().numpy())
            meta["p_divnet"] = np.concatenate(ps) if ps else np.zeros(0)
            del crops, bundle
            divnet_info.update({"checkpoint": str(ckpt), "in_sample": True,
                                "note": "public giorgosi DivNet best_overall.pt was trained on these 199 train videos "
                                        "(4 folds, best fold model): its numbers are IN-SAMPLE, DaughterNet's are OOF"})
            log(f"[oof] DivNet scored {len(meta)} samples with {ckpt}")
        except Exception as exc:
            divnet_info["error"] = f"{type(exc).__name__}: {exc}"
            log(f"[oof] DivNet comparison skipped: {divnet_info['error']}")

    out = meta.reset_index(drop=True)
    extra = [c for c in ("node_id", "kind", "embryo", "label_idx", "p_divnet") if c in out.columns]
    out[OOF_COLUMNS + extra].to_csv(work / "oof.csv", index=False)

    readout = {
        "kernel": "biohub-l2-kdn-train", "classes": list(CLASSES), "n_samples": int(len(out)),
        "n_with_oof": int(out["p_par"].notna().sum()), "splits_source": state.get("splits_source"),
        "definitions": {
            "base_rate": "fraction of the embryo's labelled samples that carry the class (sampling-dependent: cont is "
                         "subsampled to <= cont_per_video + hardneg_per_video per video)",
            "precision": "fraction of the class among the top-k samples ranked by that class probability",
            "lift": "precision / base_rate",
            "lr_plus": "likelihood ratio at the cutoff = TPR / FPR = (tp/P) / (fp/N); null when fp = 0",
            "auc": "one-vs-rest ROC AUC of the class probability",
        },
        "counts": {e: g.groupby("kind").size().to_dict() for e, g in out.groupby("embryo")},
        "per_embryo": {}, "hardneg": {}, "folds": fold_summaries, "divnet_comparison": divnet_info,
        "timing": state.get("timing", {}), "train_rc": state.get("train_rc"),
        "config": {k: v for k, v in cfg.items() if not k.startswith("_")},
    }
    scored = out[out["p_par"].notna()]
    groups = [(e, g) for e, g in scored.groupby("embryo")] + [("all", scored)]
    prob_col = {"cont": "p_cont", "parent": "p_par", "daughter": "p_dau"}
    for emb, g in groups:
        readout["per_embryo"][emb] = {
            name: _rank_block(g[prob_col[name]].to_numpy(), (g["label"] == name).to_numpy()) for name in CLASSES}
        hu = g[g["kind"].str.startswith("hardneg") & g["kind"].str.contains("u")]
        hv = g[g["kind"].str.startswith("hardneg") & g["kind"].str.contains("v")]
        par, dau = g[g["label"] == "parent"], g[g["label"] == "daughter"]
        readout["hardneg"][emb] = {
            "n_hardneg_u": int(len(hu)), "n_hardneg_v": int(len(hv)),
            "auc_p_par_parent_vs_hardneg_u": auc_score(np.r_[par["p_par"], hu["p_par"]],
                                                       np.r_[np.ones(len(par)), np.zeros(len(hu))]),
            "auc_p_dau_daughter_vs_hardneg_v": auc_score(np.r_[dau["p_dau"], hv["p_dau"]],
                                                         np.r_[np.ones(len(dau)), np.zeros(len(hv))]),
        }
        if "p_divnet" in g.columns and divnet_info.get("in_sample"):
            sub = g[g["label"].isin(["parent", "cont"])]
            sub_rand = g[g["kind"].isin(["parent", "cont"])]
            y = (sub["label"] == "parent").to_numpy()
            y_r = (sub_rand["kind"] == "parent").to_numpy()
            divnet_info.setdefault("per_embryo", {})[emb] = {
                "subset": "parent vs cont (random cont + hard negatives)",
                "divnet_in_sample": _rank_block(sub["p_divnet"].to_numpy(), y),
                "daughternet_oof_p_par": _rank_block(sub["p_par"].to_numpy(), y),
                "random_cont_only": {"divnet_in_sample_auc": auc_score(sub_rand["p_divnet"].to_numpy(), y_r),
                                     "daughternet_oof_auc": auc_score(sub_rand["p_par"].to_numpy(), y_r)},
            }
    state["timing"]["oof_s"] = round(time.time() - t0, 1)
    readout["timing"] = state["timing"]
    (work / "oof_readout.json").write_text(json.dumps(readout, indent=1, default=_json_default))
    log(f"[oof] wrote {work / 'oof.csv'} ({len(out)} rows) and {work / 'oof_readout.json'}")
    _print_readout(readout)
    if not cfg.get("keep_cache"):
        import shutil
        shutil.rmtree(cache, ignore_errors=True)
    state["readout"] = readout
    return state


def _json_default(value):
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    return str(value)


def _print_readout(readout: dict) -> None:
    for emb, block in readout["per_embryo"].items():
        for name, r in block.items():
            tops = " ".join(f"{k}:{r[k]['tp']}/{r[k]['k']}" for k, _ in TOP_FRACS if r.get(k))
            auc = None if r["auc"] is None else round(r["auc"], 4)
            base = "n/a" if r["base_rate"] is None else f"{r['base_rate']:.4f}"
            log(f"[readout] {emb:5s} {name:8s} n_pos={r['n_pos']:5d} base={base} AUC={auc} {tops}")
    for emb, r in readout.get("divnet_comparison", {}).get("per_embryo", {}).items():
        a, b = r["divnet_in_sample"]["auc"], r["daughternet_oof_p_par"]["auc"]
        log(f"[readout] {emb:5s} parent-vs-cont AUC DivNet(in-sample)={a} DaughterNet(OOF)={b}")


def step_verify(cfg: dict, state: dict, per_fold: int = 2) -> dict:
    """End-to-end contract check on a few OOF samples per fold: raw frames -> tools.daughternet.score_nodes with the
    fold's best.pt (the submission-patch path) must reproduce oof.csv, and DivNet's divnet_score_division must
    reproduce p_divnet. Differences are only fp rounding (float32 cache) or fp16 rounding (float16 cache)."""
    import pandas as pd
    import torch
    from tools.divnet_infer import divnet_score_division

    work = Path(state["work_dir"])
    oof = pd.read_csv(work / "oof.csv")
    oof = oof[oof["p_par"].notna()]
    reader = FrameReader(Path(state["data_dir"]))
    report = {"checked": 0, "max_abs_diff_daughternet": 0.0, "max_abs_diff_divnet": None, "rows": []}
    divnet_bundle = None
    if "p_divnet" in oof.columns and oof["p_divnet"].notna().any():
        ckpt = _find_divnet_checkpoint(cfg)
        divnet_bundle = load_divnet_mitosis_model(ckpt) if ckpt else None
        report["max_abs_diff_divnet"] = 0.0
    for fold, g in oof.groupby("fold"):
        best = _fold_dir(work, int(fold)) / "best.pt"
        if not best.is_file():
            continue
        bundle = load_daughternet([best], device="cpu")
        # prefer parents/daughters so the check covers the classes that matter
        pick = pd.concat([g[g["label"] != "cont"].head(per_fold), g[g["label"] == "cont"].head(1)])
        for _, r in pick.iterrows():
            node = {"t": int(r["t"]), "z": float(r["z"]), "y": float(r["y"]), "x": float(r["x"])}
            bundle["prepared_frames"] = {}
            p = score_nodes(r["stem"], [node], bundle, {}, reader, batch=1)[0]
            diff = float(np.abs(p - r[["p_cont", "p_par", "p_dau"]].to_numpy(dtype=np.float64)).max())
            report["max_abs_diff_daughternet"] = max(report["max_abs_diff_daughternet"], diff)
            row = {"fold": int(fold), "stem": r["stem"], "t": int(r["t"]), "label": r["label"], "diff": diff}
            if divnet_bundle is not None:
                divnet_bundle["prepared_frames"] = {}
                q = divnet_score_division(r["stem"], int(r["t"]), node, None, None, divnet_bundle, {}, reader)
                d2 = abs(q - float(r["p_divnet"]))
                report["max_abs_diff_divnet"] = max(report["max_abs_diff_divnet"], d2)
                row["diff_divnet"] = d2
            report["rows"].append(row)
            report["checked"] += 1
    # OOF p come from the fold worker (cuDNN on GPU, batch 256); the re-score runs on CPU one node at a time, so
    # only fp rounding separates them; a contract drift (crop shift, normalisation) moves p far more than this.
    tol = 1e-3 if state.get("cache_dtype", cfg["cache_dtype"]) == "float32" else 2e-2
    report["tolerance"] = tol
    report["pass"] = bool(report["checked"] > 0 and report["max_abs_diff_daughternet"] <= tol
                          and (report["max_abs_diff_divnet"] is None or report["max_abs_diff_divnet"] <= tol))
    (work / "contract_check.json").write_text(json.dumps(report, indent=1, default=_json_default))
    log(f"[verify] {report['checked']} samples re-scored from raw frames via score_nodes: max |dp| DaughterNet "
        f"{report['max_abs_diff_daughternet']:.2e}, DivNet {report['max_abs_diff_divnet']} -> "
        f"{'PASS' if report['pass'] else 'FAIL'} (tol {tol})")
    state["verify"] = report
    return state


def run_all(cfg: dict) -> dict:
    state = step_prepare(cfg)
    state = step_build_cache(cfg, state)
    state = step_train(cfg, state)
    state = step_oof(cfg, state)
    state = step_verify(cfg, state)
    return state


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        sys.exit(worker_main(sys.argv[2:]))
    run_all(config_from_env())
