"""Pseudo-labelled DaughterNet crops from the public Ultrack zebrafish embryo ("dorado", plan line L3).

Source (public, no account): the Royer lab stabilized light-sheet movie and its Ultrack tracks.
  image  : public.czbiohub.org/royerlab/ultrack/zebrafish_embryo.ome.zarr, level "0", zarr v2,
           shape (T=522, C=1, Z=505, Y=2217, X=2170) uint16, voxel (1.625, 0.40625, 0.40625) um = the Kaggle scale,
           chunks (1, 1, 128, 2217, 2170) blosc/zstd/bitshuffle, ~340-415 MB compressed each, 4 z-chunks per frame.
  tracks : public.czbiohub.org/royerlab/ultrack/inTRACKtive/Sparse_Embryo_tracks_with_hex_bundle.zarr
           tracks_to_points CSR (458,519 tracks; indices = point index = t * 38068 + slot; data = (z, y, x) in
           0.40625 um units, so z_voxel = z / 4), tracks_to_tracks CSR (row = whole lineage; data = 1-based parent id
           of the column track, -1 = root). Verified: every track covers consecutive frames and a child starts at
           parent end + 1; 186,459 tracks have exactly 2 children.

Every sample follows the DaughterNet / DivNet contract (tools/daughternet.py, tools/divnet_infer.prepare_divnet_input):
image lags -1, 0, +1, +2 around the node frame t, XY mean-pool by 4 (pool grid aligned to multiples of 4 px, like a
Kaggle clip whose origin is a multiple of 4), a 16x32x32 crop centred on (round(z), round(y/4), round(x/4)),
percentile 50/99.5 normalisation clipped to [-0.5, 6], and the gaussian centre marker -> (5, 16, 32, 32).
The percentiles are NOT taken on the whole embryo frame: for each sample one Kaggle-sized 64x256x256 window
(pooled 64x64x64) containing the node is drawn (node position uniform inside the window, like a GT node inside a
Kaggle clip, clamped to the loaded z range and the image), and each lag frame is normalised on that same window.
The stored crop keeps the real surroundings; the window origin is stored so that apply_window_pad() can zero the
voxels outside the window, which is exactly what _crop_with_padding gives for a node near a Kaggle clip border (about
80% of uniformly placed nodes touch a border; use it as a train-time augmentation, or bake it in with --window-pad).
Windows are redrawn until they pass Kaggle-clip bounds (MIN_P50, MAX_ZERO_FRAC below). Window origin, per-lag lo/hi
and the number of tracked cells inside the window are stored per sample.

Labels (class order = daughternet.CLASSES = cont, parent, daughter):
  parent   last point of a track with exactly 2 children; parent and both daughters last >= 10 frames; sister
           separation 5-14 um at the daughters' first frame; parent->daughter step <= 10 um for both daughters;
           no other division among ancestors/descendants within +-15 frames (grandparent split and both daughters'
           own splits are > 15 frames away; sibling/cousin divisions are not checked).
  daughter first point of each child of such a parent.
  cont     point of a track lasting >= 20 frames, >= 5 frames from its own start and end.
  hard     (label cont, meta hard=1) cont point whose position at t+1 has an unrelated track START at t+1 within
           5-14 um (the false-division look-alike of our pipeline).
Per shard: all positives (parents + daughters) in the shard's z range, negatives = 3 x positives, of which up to
--hard-frac are hard negatives and the rest random cont points.

Streaming: per frame block (L consecutive frames) and z-chunk, each level-0 chunk is downloaded into memory (parallel
HTTP range requests), decoded, XY-pooled slab by slab and dropped; only the 4 pooled frames a node needs are kept at
a time, nothing raw is written to disk. Node frames of a block are b0+1 .. b0+L-3 (all four lags inside the block).
Z ownership: shard (b0, k >= 1) takes nodes with round(z) in [128k - 8, 128k + 120): the last 16 pooled slices of
z-chunk k-1 are the halo, kept in memory when z-chunk k-1 was processed just before in the same run, else read
partially from that chunk (blosc block table + only the ~51 MB span of those slices, load_pooled_slices). Consecutive
z-chunks tile z without gaps or duplicates in any run order. With --no-fetch-halo and no in-memory halo the shard
takes [128k + 8, 128k + 120) only (recorded as info.halo = false). info.halo_source = memory / partial / none; the
first in-memory-halo shard of a run also partial-reads its halo and requires it bit-identical to the fully decoded one
(info.halo_verified; --no-verify-halo skips it).
Centre rounding: the global round(y / 4) and the clip-local round of the contract disagree by one pooled voxel on .5
ties when the window origin is odd; the node is then half a voxel off-centre either way and apply_window_pad uses the
same global rounding, so this is jitter with no systematic offset.
One output shard per (frame block, z-chunk): data_external/dorado/shards/b{b0:03d}_z{k}.npz, skipped if present.

Shard keys: x (N,5,16,32,32) float16, y (N,) int8 class index, t, zyx (N,3) node voxel position, track, partner
(daughter: parent track; hard: the unrelated starting track; else -1), hard, block, zchunk, win_origin (pooled z,y,x of
the normalisation window), norm_lohi (N,4,2) raw p50/p99.5 per lag, win_cells (tracked cells in the window), win_ok
(window passed the Kaggle-clip bounds MIN_P50 / MAX_ZERO_FRAC), win_zero_frac, info (json).

Commands (python tools/dorado_crops.py <cmd> -h):
  tracks                      download + cache the tracks bundle (~26 s, ~130 MB)
  density                     per-frame cell counts per Kaggle-sized window, divisions per frame -> density.csv
  blocks [--n 4 --len 8]      choose frame blocks (density closest to Kaggle, spread over development) -> blocks.json
  labels --block B0 [--zchunk K]   label counts for a block without touching the image
  extract [--blocks B0 ...] [--zchunks 1 2] [--window-pad] [--max-frames N --shard-dir D]
                              stream + write shards (resumable; default blocks from blocks.json)
  inspect SHARD.npz           class counts, value ranges, centre-region statistics per lag and class
"""
from __future__ import annotations

import argparse
import json
import math
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data_external" / "dorado"
TRACKS_NPZ = OUT / "tracks" / "tracks.npz"
SHARDS = OUT / "shards"

IMG_URL = "https://public.czbiohub.org/royerlab/ultrack/zebrafish_embryo.ome.zarr/0"
TRK_URL = "https://public.czbiohub.org/royerlab/ultrack/inTRACKtive/Sparse_Embryo_tracks_with_hex_bundle.zarr"
N_T, N_Z, N_Y, N_X = 522, 505, 2217, 2170
ZCHUNK = 128
N_SLOTS = 38068                      # points per frame in the inTRACKtive bundle
UNIT_UM = 0.40625                    # bundle coordinate unit (isotropic)
Z_UNITS_PER_VOX = 4                  # 1.625 / 0.40625
POOL = 4
CROP = (16, 32, 32)
WIN = (64, 64, 64)                   # pooled Kaggle clip: 64 z x (256/4) y x (256/4) x
LAGS = (-1, 0, 1, 2)
LO_PCT, HI_PCT, CLIP = 50.0, 99.5, (-0.5, 6.0)
MARKER_SIGMA = (1.5, 2.0, 2.0)
HALO = 16
# Window acceptance, from the 199 Kaggle train clips (frame 50, pooled): raw p50 min 25 (median 146), exact-zero voxel
# fraction max 0.234 (27 clips have some zero padding). The dorado movie has zero-filled stabilisation margins; a window
# failing either bound is redrawn (up to WIN_TRIES origins), else the best one is kept with win_ok = False.
MIN_P50, MAX_ZERO_FRAC, WIN_TRIES = 25.0, 0.25, 25
KAGGLE_WINDOW_NODES = (200, 700)     # nodes per frame in a 64x256x256 Kaggle clip (detector output)
CLASSES = ("cont", "parent", "daughter")


def log(*a) -> None:
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ----------------------------------------------------------------------------------------------------------------- http
_TLS = threading.local()


def _session():
    import requests
    s = getattr(_TLS, "s", None)
    if s is None:
        s = _TLS.s = requests.Session()
    return s


def http_get(url: str, rng: tuple[int, int] | None = None, retries: int = 5, timeout: int = 300) -> bytes:
    headers = {"Range": f"bytes={rng[0]}-{rng[1] - 1}"} if rng else {}
    for attempt in range(retries):
        try:
            r = _session().get(url, headers=headers, timeout=timeout)
            if r.status_code == 404:
                raise FileNotFoundError(url)
            r.raise_for_status()
            if rng and len(r.content) != rng[1] - rng[0]:
                raise IOError(f"short range read {len(r.content)} != {rng[1] - rng[0]}")
            return r.content
        except FileNotFoundError:
            raise
        except Exception as exc:  # noqa: BLE001 - network errors of any kind are retried
            if attempt == retries - 1:
                raise
            log(f"retry {attempt + 1} {url} {rng}: {exc}")
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable")


def http_size(url: str, retries: int = 5) -> int:
    for attempt in range(retries):
        try:
            r = _session().head(url, timeout=60)
            if r.status_code == 404:
                raise FileNotFoundError(url)
            r.raise_for_status()
            return int(r.headers["Content-Length"])
        except FileNotFoundError:
            raise
        except Exception as exc:  # noqa: BLE001 - a transient HEAD failure must not kill an unattended run
            if attempt == retries - 1:
                raise
            log(f"retry {attempt + 1} HEAD {url}: {exc}")
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable")


def download_parallel(url: str, parts: int = 4, part_mb: int = 16, span: tuple[int, int] | None = None,
                      buf: bytearray | None = None) -> bytearray:
    """Whole object (or bytes [span) into the same offsets of `buf`) with parallel range requests."""
    size = http_size(url) if span is None else None
    a0, a1 = (0, size) if span is None else span
    if buf is None:
        buf = bytearray(size if size is not None else a1)
    step = part_mb << 20
    ranges = [(a, min(a1, a + step)) for a in range(a0, a1, step)]

    def one(r):
        buf[r[0]:r[1]] = http_get(url, r)

    with ThreadPoolExecutor(parts) as ex:
        list(ex.map(one, ranges))
    return buf


def _blosc():
    import numcodecs
    return numcodecs.Blosc()


# --------------------------------------------------------------------------------------------------------------- tracks
def _fetch_zarr_v2(path: str, threads: int = 16) -> np.ndarray:
    meta = json.loads(http_get(f"{TRK_URL}/{path}/.zarray"))
    shape, chunks, dt = meta["shape"], meta["chunks"], np.dtype(meta["dtype"])
    sep = meta.get("dimension_separator", ".")
    grid = [-(-s // c) for s, c in zip(shape, chunks)]
    out = np.full(shape, meta.get("fill_value") or 0, dt)
    codec = _blosc()

    def one(idx):
        try:
            raw = http_get(f"{TRK_URL}/{path}/{sep.join(map(str, idx))}")
        except FileNotFoundError:
            return idx, None
        return idx, np.frombuffer(codec.decode(raw), dt).reshape(chunks)

    with ThreadPoolExecutor(threads) as ex:
        for idx, val in ex.map(one, list(np.ndindex(*grid))):
            if val is None:
                continue
            sl = tuple(slice(i * c, min((i + 1) * c, s)) for i, c, s in zip(idx, chunks, shape))
            out[sl] = val[tuple(slice(0, x.stop - x.start) for x in sl)]
    return out


def fetch_tracks(force: bool = False) -> Path:
    if TRACKS_NPZ.exists() and not force:
        log(f"tracks cached: {TRACKS_NPZ}")
        return TRACKS_NPZ
    TRACKS_NPZ.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    ip = _fetch_zarr_v2("tracks_to_points/indptr").astype(np.int64)
    ind = _fetch_zarr_v2("tracks_to_points/indices").astype(np.int64)
    tin = _fetch_zarr_v2("tracks_to_tracks/indices")
    tda = _fetch_zarr_v2("tracks_to_tracks/data")
    tip = _fetch_zarr_v2("tracks_to_tracks/indptr")
    pts = _fetch_zarr_v2("points").reshape(N_T, N_SLOTS, 3)
    log(f"bundle downloaded in {time.time() - t0:.0f}s")
    n_tracks = len(ip) - 1
    t, slot = np.divmod(ind, N_SLOTS)
    zyx = pts[t, slot]
    if not np.all(zyx == np.round(zyx)) or zyx.min() < 0:
        raise RuntimeError("unexpected non-integral / missing coordinates")
    tr = np.repeat(np.arange(n_tracks), np.diff(ip))
    same = tr[1:] == tr[:-1]
    if not np.all(np.diff(t)[same] == 1):
        raise RuntimeError("tracks with time gaps: the extractor assumes consecutive frames")
    # parent: data of the column entry (consistent over rows); 1-based ids, -1 = root, absent = root
    parent = np.full(n_tracks, -1, np.int64)
    parent[tin] = tda
    parent = np.where(parent > 0, parent - 1, -1)
    start, end = t[ip[:-1]], t[ip[1:] - 1]
    has = parent >= 0
    if not np.all(start[has] == end[parent[has]] + 1):
        raise RuntimeError("child start != parent end + 1")
    np.savez(TRACKS_NPZ, ptr=ip, pt_t=t.astype(np.int16), pt_zyx=zyx.astype(np.int16),
             start=start.astype(np.int16), end=end.astype(np.int16), parent=parent.astype(np.int32))
    log(f"tracks: {n_tracks} tracks, {len(ind)} points -> {TRACKS_NPZ} ({TRACKS_NPZ.stat().st_size / 1e6:.0f} MB)")
    return TRACKS_NPZ


class Tracks:
    """Point and track tables; coordinates in voxels (z, y, x) of the level-0 image."""

    def __init__(self, path: Path = TRACKS_NPZ) -> None:
        if not path.exists():
            fetch_tracks()
        d = np.load(path)
        self.ptr = d["ptr"]
        self.pt_t = d["pt_t"].astype(np.int32)
        units = d["pt_zyx"].astype(np.float32)
        self.pt_um = units * UNIT_UM                                   # isotropic um, for distances
        self.pt_vox = units / np.array([Z_UNITS_PER_VOX, 1, 1], np.float32)
        self.start = d["start"].astype(np.int32)
        self.end = d["end"].astype(np.int32)
        self.parent = d["parent"].astype(np.int64)
        self.n_tracks = len(self.ptr) - 1
        self.pt_track = np.repeat(np.arange(self.n_tracks), np.diff(self.ptr))
        self.length = self.end - self.start + 1
        self.n_children = np.bincount(self.parent[self.parent >= 0], minlength=self.n_tracks)
        kids = np.flatnonzero(self.parent >= 0)
        kids = kids[np.argsort(self.parent[kids], kind="stable")]
        self.kid_ptr = np.concatenate([[0], np.cumsum(self.n_children)])
        self.kids = kids
        order = np.argsort(self.pt_t, kind="stable")
        self.frame_order = order
        self.frame_ptr = np.searchsorted(self.pt_t[order], np.arange(N_T + 1))

    def frame_points(self, t: int) -> np.ndarray:
        return self.frame_order[self.frame_ptr[t]:self.frame_ptr[t + 1]]

    def children(self, k: int) -> np.ndarray:
        return self.kids[self.kid_ptr[k]:self.kid_ptr[k + 1]]

    def first_pt(self, k):
        return self.ptr[k]

    def last_pt(self, k):
        return self.ptr[np.asarray(k) + 1] - 1


# ------------------------------------------------------------------------------------------------------------ labelling
def division_table(tr: Tracks) -> dict[str, np.ndarray]:
    """All 2-child parents with the qualification flags of the label rules."""
    p = np.flatnonzero(tr.n_children == 2)
    c1, c2 = tr.kids[tr.kid_ptr[p]], tr.kids[tr.kid_ptr[p] + 1]
    lp = tr.last_pt(p)
    f1, f2 = tr.first_pt(c1), tr.first_pt(c2)
    sep = np.linalg.norm(tr.pt_um[f1] - tr.pt_um[f2], axis=1)
    step = np.maximum(np.linalg.norm(tr.pt_um[lp] - tr.pt_um[f1], axis=1),
                      np.linalg.norm(tr.pt_um[lp] - tr.pt_um[f2], axis=1))
    tdiv = tr.end[p]
    gp = tr.parent[p]
    up_ok = (gp < 0) | (tdiv - np.where(gp >= 0, tr.end[np.maximum(gp, 0)], -10**6) > 15)
    down_ok = np.ones(len(p), bool)
    for c in (c1, c2):
        down_ok &= (tr.n_children[c] != 2) | (tr.end[c] - tdiv > 15)
    len_ok = (tr.length[p] >= 10) & (tr.length[c1] >= 10) & (tr.length[c2] >= 10)
    sep_ok = (sep >= 5) & (sep <= 14)
    step_ok = step <= 10
    ok = len_ok & sep_ok & step_ok & up_ok & down_ok
    return dict(parent=p, c1=c1, c2=c2, tdiv=tdiv, sep=sep, step=step, len_ok=len_ok, sep_ok=sep_ok,
                step_ok=step_ok, lineage_ok=up_ok & down_ok, ok=ok)


def cont_eligible(tr: Tracks, idx: np.ndarray) -> np.ndarray:
    k = tr.pt_track[idx]
    t = tr.pt_t[idx]
    return (tr.length[k] >= 20) & (t - tr.start[k] >= 5) & (tr.end[k] - t >= 5)


def hard_negative_mask(tr: Tracks, idx: np.ndarray, t: int) -> tuple[np.ndarray, np.ndarray]:
    """For cont-eligible points idx at frame t: True where an unrelated track starts at t+1 within 5-14 um of the
    point's own t+1 position. Returns (mask, partner track id or -1)."""
    from scipy.spatial import cKDTree
    starts = tr.frame_points(t + 1)
    starts = starts[tr.pt_t[starts] == tr.start[tr.pt_track[starts]]]
    mask = np.zeros(len(idx), bool)
    partner = np.full(len(idx), -1, np.int64)
    if len(starts) == 0 or len(idx) == 0:
        return mask, partner
    tree = cKDTree(tr.pt_um[starts])
    nxt = tr.pt_um[idx + 1]                                             # same track, frame t+1 (contiguous CSR)
    hits = tree.query_ball_point(nxt, r=14.0)
    own = tr.pt_track[idx]
    for i, h in enumerate(hits):
        if not h:
            continue
        h = np.asarray(h)
        d = np.linalg.norm(tr.pt_um[starts[h]] - nxt[i], axis=1)
        cand = starts[h][(d >= 5.0) & (tr.parent[tr.pt_track[starts[h]]] != own[i])]
        if len(cand):
            mask[i] = True
            partner[i] = tr.pt_track[cand[0]]
    return mask, partner


def node_frames(b0: int, length: int) -> range:
    return range(b0 - min(LAGS), b0 + length - max(LAGS))


def z_owned(zchunk: int, halo: bool) -> tuple[int, int]:
    lo = ZCHUNK * zchunk + (-CROP[0] // 2 if halo else CROP[0] // 2)
    hi = min(ZCHUNK * (zchunk + 1), N_Z) - CROP[0] // 2
    return lo, hi


def block_candidates(tr: Tracks, divs: dict, b0: int, length: int) -> dict[str, np.ndarray]:
    """Candidate point indices per class over the node frames of the block (no z filter, no sampling)."""
    frames = node_frames(b0, length)
    ok = divs["ok"]
    par_pts = tr.last_pt(divs["parent"][ok])
    dau_pts = np.concatenate([tr.first_pt(divs["c1"][ok]), tr.first_pt(divs["c2"][ok])])
    dau_par = np.concatenate([divs["parent"][ok], divs["parent"][ok]])
    in_f = lambda idx: (tr.pt_t[idx] >= frames.start) & (tr.pt_t[idx] < frames.stop)  # noqa: E731
    par_sel = in_f(par_pts)
    dau_sel = in_f(dau_pts)
    cont, hard, hard_partner = [], [], []
    for t in frames:
        idx = tr.frame_points(t)
        idx = idx[cont_eligible(tr, idx)]
        m, prt = hard_negative_mask(tr, idx, t)
        hard.append(idx[m]); hard_partner.append(prt[m]); cont.append(idx[~m])
    return dict(parent=par_pts[par_sel], daughter=dau_pts[dau_sel], daughter_parent=dau_par[dau_sel],
                cont=np.concatenate(cont), hard=np.concatenate(hard), hard_partner=np.concatenate(hard_partner))


def select_samples(tr: Tracks, cand: dict, zchunk: int, halo: bool, seed: int, neg_ratio: float = 3.0,
                   hard_frac: float = 0.5) -> dict[str, np.ndarray]:
    """Shard sample list: all positives in the owned z range, negatives = neg_ratio x positives."""
    zlo, zhi = z_owned(zchunk, halo)
    zr = lambda idx: np.array([round(float(v)) for v in tr.pt_vox[idx, 0]], np.int64)  # noqa: E731 - python round
    inz = lambda idx: (zr(idx) >= zlo) & (zr(idx) < zhi) if len(idx) else np.zeros(0, bool)  # noqa: E731
    rng = np.random.default_rng(seed)
    par = cand["parent"][inz(cand["parent"])]
    dm = inz(cand["daughter"])
    dau, dau_par = cand["daughter"][dm], cand["daughter_parent"][dm]
    hm = inz(cand["hard"])
    hard, hard_prt = cand["hard"][hm], cand["hard_partner"][hm]
    cont = cand["cont"][inz(cand["cont"])]
    n_pos = len(par) + len(dau)
    n_neg = int(round(neg_ratio * n_pos))
    n_hard = min(len(hard), int(round(hard_frac * n_neg)))
    n_cont = min(len(cont), n_neg - n_hard)
    hsel = rng.choice(len(hard), n_hard, replace=False) if n_hard else np.zeros(0, np.int64)
    csel = rng.choice(len(cont), n_cont, replace=False) if n_cont else np.zeros(0, np.int64)
    idx = np.concatenate([par, dau, hard[hsel], cont[csel]]).astype(np.int64)
    y = np.concatenate([np.full(len(par), 1), np.full(len(dau), 2), np.zeros(n_hard + n_cont)]).astype(np.int8)
    hard_flag = np.concatenate([np.zeros(n_pos, bool), np.ones(n_hard, bool), np.zeros(n_cont, bool)])
    partner = np.concatenate([np.full(len(par), -1), dau_par, hard_prt[hsel], np.full(n_cont, -1)]).astype(np.int64)
    return dict(idx=idx, y=y, hard=hard_flag, partner=partner, z_owned=np.array([zlo, zhi]),
                avail=np.array([len(par), len(dau), len(hard), len(cont)]))


# ------------------------------------------------------------------------------------------------------------- density
def window_counts(pts_units: np.ndarray, bin_units: int = 16, win_units: int = 256) -> np.ndarray:
    """For each point: number of points inside the Kaggle-sized window (64x256x256 voxels = 256^3 units) centred on
    it, via a summed-area table on 16-unit bins (approximate to one bin)."""
    b = (pts_units // bin_units).astype(np.int64)
    shape = b.max(0) + 1
    h = np.zeros(shape, np.int32)
    np.add.at(h, tuple(b.T), 1)
    s = np.zeros(tuple(shape + 1), np.int64)
    s[1:, 1:, 1:] = h.cumsum(0).cumsum(1).cumsum(2)
    half = win_units // bin_units // 2
    lo = np.clip(b - half, 0, shape)
    hi = np.clip(b + half, 0, shape)
    z0, y0, x0 = lo.T
    z1, y1, x1 = hi.T
    return (s[z1, y1, x1] - s[z0, y1, x1] - s[z1, y0, x1] - s[z1, y1, x0]
            + s[z0, y0, x1] + s[z0, y1, x0] + s[z1, y0, x0] - s[z0, y0, x0])


def density_table(tr: Tracks, divs: dict) -> list[dict]:
    units = tr.pt_um / UNIT_UM
    ok_t = np.bincount(divs["tdiv"][divs["ok"]], minlength=N_T)
    all_t = np.bincount(divs["tdiv"], minlength=N_T)
    rows = []
    for t in range(N_T):
        idx = tr.frame_points(t)
        wc = window_counts(units[idx])
        zv = tr.pt_vox[idx, 0]
        in12 = (zv >= 136) & (zv < 376)
        rows.append(dict(t=t, cells=len(idx), win_p25=float(np.percentile(wc, 25)), win_med=float(np.median(wc)),
                         win_p75=float(np.percentile(wc, 75)), frac_in_kaggle_range=float(np.mean(
                             (wc >= KAGGLE_WINDOW_NODES[0]) & (wc <= KAGGLE_WINDOW_NODES[1]))),
                         cells_z1z2=int(in12.sum()), divisions=int(all_t[t]), div_ok=int(ok_t[t])))
    return rows


def choose_blocks(rows: list[dict], n: int = 4, length: int = 8, target: float | None = None,
                  spread: float = 0.5, tol: float = 0.25) -> list[dict]:
    """One block per developmental segment (n equal segments of the movie), searched only in the central `spread`
    fraction of each segment so the blocks stay apart. Key: distance of the block's median cell-centric window count
    to the Kaggle range centre (geometric mean of KAGGLE_WINDOW_NODES) in log units, binned by `tol` (every frame of
    this movie is inside the Kaggle 200-700 range, so near-ties are the rule), then the number of qualifying
    divisions whose parent frame is a node frame."""
    target = target or math.sqrt(KAGGLE_WINDOW_NODES[0] * KAGGLE_WINDOW_NODES[1])
    med = np.array([r["win_med"] for r in rows])
    dok = np.array([r["div_ok"] for r in rows]).astype(int)
    starts = np.arange(1, N_T - length)
    edges = np.linspace(starts[0], starts[-1] + 1, n + 1).astype(int)
    out = []
    for q in range(n):
        best = None
        seg = edges[q + 1] - edges[q]
        s0 = edges[q] + int(round(seg * (1 - spread) / 2))
        s1 = edges[q + 1] - int(round(seg * (1 - spread) / 2))
        for b0 in range(s0, s1 - length + 1):
            m = float(np.median(med[b0:b0 + length]))
            nf = node_frames(b0, length)
            # divisions whose parent frame is a node frame
            d = int(dok[nf.start:nf.stop].sum())
            key = (round(abs(math.log(m / target)) / tol), -d)
            if best is None or key < best[0]:
                best = (key, dict(b0=int(b0), t_range=[int(b0), int(b0 + length - 1)],
                                  node_frames=[nf.start, nf.stop - 1], win_med=m, div_ok_node_frames=d,
                                  quarter=[int(edges[q]), int(edges[q + 1] - 1)]))
        out.append(best[1])
    return out


# ----------------------------------------------------------------------------------------------------------- imaging
def pool_chunk(raw: np.ndarray, slab: int = 8) -> np.ndarray:
    """XY mean-pool by 4 exactly like divnet_infer._pool_xy (float32 reshape-mean), slab by slab to bound memory."""
    z = raw.shape[0]
    y2, x2 = (raw.shape[1] // POOL) * POOL, (raw.shape[2] // POOL) * POOL
    out = np.empty((z, y2 // POOL, x2 // POOL), np.float32)
    for s in range(0, z, slab):
        v = raw[s:s + slab, :y2, :x2].astype(np.float32)
        out[s:s + slab] = v.reshape(v.shape[0], y2 // POOL, POOL, x2 // POOL, POOL).mean(axis=(2, 4))
    return out


def load_pooled(t: int, zchunk: int) -> np.ndarray:
    t0 = time.time()
    buf = download_parallel(f"{IMG_URL}/{t}/0/{zchunk}/0/0")
    t1 = time.time()
    raw = np.frombuffer(_blosc().decode(buf), dtype="<u2")
    mb = len(buf) / 1e6
    del buf
    t2 = time.time()
    raw = raw.reshape(ZCHUNK, N_Y, N_X)[: min(ZCHUNK, N_Z - ZCHUNK * zchunk)]
    pooled = pool_chunk(raw)
    del raw
    log(f"  chunk t={t} z{zchunk}: {mb:.0f} MB download {t1 - t0:.0f}s ({mb / max(t1 - t0, 1e-3):.1f} MB/s), "
        f"decode {t2 - t1:.1f}s, pool {time.time() - t2:.1f}s")
    return pooled


def load_pooled_slices(t: int, zchunk: int, z0: int, z1: int) -> np.ndarray:
    """Pooled slices [z0, z1) of one level-0 chunk without downloading the whole chunk: read the blosc1 header and
    block-start table, fetch only the compressed span of the blocks covering those slices into a zero-filled buffer of
    the full compressed size, and blosc_getitem them (numcodecs decompress_partial). The block table is not
    monotonic (multi-threaded writer), so each block's end is the next larger block start. ~51 MB for 16 slices."""
    import warnings
    from numcodecs import blosc
    url = f"{IMG_URL}/{t}/0/{zchunk}/0/0"
    head = http_get(url, (0, 16))
    nbytes, bs, cb = (int(v) for v in np.frombuffer(head[4:16], "<u4"))
    if head[3] != 2 or nbytes != ZCHUNK * N_Y * N_X * 2:        # getitem start/nitems below are in uint16 items
        raise RuntimeError(f"unexpected blosc header typesize={head[3]} nbytes={nbytes} for {url}")
    slice_b = N_Y * N_X * 2
    s_b, e_b = z0 * slice_b, z1 * slice_b
    if head[2] & 0x02:                                                  # memcpyed chunk: raw bytes after the header
        raw = np.frombuffer(http_get(url, (16 + s_b, 16 + e_b)), "<u2")
    else:
        nb = -(-nbytes // bs)
        table = http_get(url, (16, 16 + 4 * nb))
        bst = np.frombuffer(table, "<i4").astype(np.int64)
        need = bst[s_b // bs:-(-e_b // bs)]
        srt = np.sort(bst)
        pos = np.searchsorted(srt, need, side="right")
        ends = np.where(pos < nb, srt[np.minimum(pos, nb - 1)], cb)
        lo, hi = int(need.min()), int(ends.max())
        buf = bytearray(cb)
        buf[:16] = head
        buf[16:16 + 4 * nb] = table
        download_parallel(url, span=(lo, hi), buf=buf)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            raw = np.frombuffer(blosc.decompress_partial(buf, s_b // 2, (e_b - s_b) // 2), "<u2")
        del buf
    return pool_chunk(raw.reshape(z1 - z0, N_Y, N_X))


def marker(shape=CROP, sigma=MARKER_SIGMA) -> np.ndarray:
    axes = [np.arange(size, dtype=np.float32) - size // 2 for size in shape]
    zz, yy, xx = np.meshgrid(*axes, indexing="ij")
    d = (zz / sigma[0]) ** 2 + (yy / sigma[1]) ** 2 + (xx / sigma[2]) ** 2
    return np.exp(-0.5 * d).astype(np.float32)


def window_origin(centre: tuple[int, int, int], lo: tuple[int, int, int], hi: tuple[int, int, int],
                  rng: np.random.Generator) -> tuple[int, int, int]:
    """Kaggle-clip-like window: node offset uniform in [0, W) per axis, window clamped inside [lo, hi)."""
    o = []
    for c, w, a, b in zip(centre, WIN, lo, hi):
        start = c - int(rng.integers(0, w))
        o.append(int(min(max(start, a), b - w)))
    return tuple(o)


def pick_window(frame0: np.ndarray, zoff: int, centre: tuple[int, int, int], lo: tuple[int, int, int],
                hi: tuple[int, int, int], rng: np.random.Generator) -> tuple[tuple[int, int, int], bool, float]:
    """Draw window origins until the lag-0 window looks like a Kaggle clip (MIN_P50, MAX_ZERO_FRAC)."""
    best = None
    for _ in range(WIN_TRIES):
        o = window_origin(centre, lo, hi, rng)
        w = frame0[o[0] - zoff:o[0] - zoff + WIN[0], o[1]:o[1] + WIN[1], o[2]:o[2] + WIN[2]]
        zero = float(np.count_nonzero(w == 0)) / w.size
        p50 = float(np.percentile(w, LO_PCT))
        if zero <= MAX_ZERO_FRAC and p50 >= MIN_P50:
            return o, True, zero
        score = (zero <= MAX_ZERO_FRAC, p50, -zero)
        if best is None or score > best[0]:
            best = (score, o, zero)
    return best[1], False, best[2]


def cut_sample(frames: list[np.ndarray], zoff: int, centre: tuple[int, int, int], origin: tuple[int, int, int],
               pad: bool, mk: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """frames: pooled arrays (z from zoff) of the 4 lags. centre/origin in pooled global coords (z raw)."""
    x = np.zeros((len(frames) + 1, *CROP), np.float32)
    lohi = np.zeros((len(frames), 2), np.float32)
    c0 = [c - s // 2 for c, s in zip(centre, CROP)]
    # crop box in global coords, intersected with the window if padding like a Kaggle clip
    lo = [max(a, o) if pad else a for a, o in zip(c0, origin)]
    hi = [min(a + s, o + w) if pad else a + s for a, s, o, w in zip(c0, CROP, origin, WIN)]
    for i, f in enumerate(frames):
        shape_g = (f.shape[0] + zoff, f.shape[1], f.shape[2])
        lo_i = [max(l, m) for l, m in zip(lo, (zoff, 0, 0))]
        hi_i = [min(h, s) for h, s in zip(hi, shape_g)]
        wz, wy, wx = origin
        win = f[wz - zoff:wz - zoff + WIN[0], wy:wy + WIN[1], wx:wx + WIN[2]]
        if win.shape != WIN:
            raise RuntimeError(f"window {origin} out of range: {win.shape}")
        a, b = np.percentile(win, [LO_PCT, HI_PCT])
        lohi[i] = (a, b)
        if not (np.isfinite(a) and np.isfinite(b) and b > a) or any(h <= l for l, h in zip(lo_i, hi_i)):
            continue
        src = f[lo_i[0] - zoff:hi_i[0] - zoff, lo_i[1]:hi_i[1], lo_i[2]:hi_i[2]]
        dst = tuple(slice(l - c, h - c) for l, h, c in zip(lo_i, hi_i, c0))
        x[i][dst] = np.clip((src - a) / (b - a), CLIP[0], CLIP[1])
    x[-1] = mk
    return x, lohi


def shard_path(b0: int, zchunk: int, shard_dir: Path | None = None) -> Path:
    return Path(shard_dir or SHARDS) / f"b{b0:03d}_z{zchunk}.npz"


def window_pad_mask(zyx: np.ndarray, win_origin: np.ndarray) -> np.ndarray:
    """(N, 16, 32, 32) bool: crop voxels inside the sample's normalisation window (= inside its emulated Kaggle clip).
    zyx: (N, 3) node voxel positions (shard key zyx); win_origin: (N, 3) pooled window origins (shard key win_origin)."""
    zyx = np.asarray(zyx, np.float64)
    centre = np.array([[round(float(z)), round(float(y) / POOL), round(float(x) / POOL)] for z, y, x in zyx],
                      np.int64).reshape(-1, 3)
    c0 = centre - np.array(CROP) // 2
    rel_lo = np.asarray(win_origin, np.int64) - c0                         # window start in crop coordinates
    masks = []
    for ax, (size, w) in enumerate(zip(CROP, WIN)):
        i = np.arange(size)[None, :]
        masks.append((i >= rel_lo[:, ax:ax + 1]) & (i < rel_lo[:, ax:ax + 1] + w))
    return masks[0][:, :, None, None] & masks[1][:, None, :, None] & masks[2][:, None, None, :]


def apply_window_pad(x: np.ndarray, zyx: np.ndarray, win_origin: np.ndarray) -> np.ndarray:
    """Kaggle-exact version of stored crops: image channels zeroed outside the window, marker channel untouched."""
    out = np.array(x, copy=True)
    m = window_pad_mask(zyx, win_origin)
    out[:, :len(LAGS)] *= m[:, None].astype(out.dtype)
    return out


def extract_shard(tr: Tracks, divs: dict, b0: int, length: int, zchunk: int, halo_in: dict | None, pad: bool,
                  hard_frac: float, neg_ratio: float, max_frames: int | None = None,
                  shard_dir: Path | None = None, fetch_halo: bool = True, verify_halo: bool = False) -> dict | None:
    """Stream the block's frames of one z-chunk, write the shard, return the halo for z-chunk + 1 (None when nothing
    was streamed). The halo (last HALO slices of z-chunk - 1) comes from the previous shard of the same run, else from
    a partial read of that chunk (fetch_halo, ~51 MB per frame), so every shard k >= 1 owns [128k - 8, 128k + 120)
    whatever the run order. verify_halo (in-memory halo only): partial-read the first frame's halo too and require it
    to be bit-identical to the one cut from the fully decoded chunk (level-0 check of load_pooled_slices, ~51 MB)."""
    t_start = time.time()
    need_fetch = halo_in is None and fetch_halo and zchunk >= 1
    halo = halo_in is not None or need_fetch
    halo_source = "memory" if halo_in is not None else ("partial" if need_fetch else "none")
    halo_verified = None
    if verify_halo and halo_in is not None:
        tv = min(halo_in)
        t0 = time.time()
        h = load_pooled_slices(tv, zchunk - 1, ZCHUNK - HALO, ZCHUNK)
        halo_verified = bool(h.shape == halo_in[tv].shape and np.array_equal(h, halo_in[tv]))
        log(f"halo check t={tv} z{zchunk - 1}: partial read == full decode: {halo_verified} ({time.time() - t0:.0f}s)")
        if not halo_verified:
            raise RuntimeError("load_pooled_slices differs from the full decode on level 0: delete every shard whose "
                               "info.halo_source is 'partial' and rerun with --no-fetch-halo")
    cand = block_candidates(tr, divs, b0, length)
    sel = select_samples(tr, cand, zchunk, halo, seed=b0 * 10 + zchunk, neg_ratio=neg_ratio, hard_frac=hard_frac)
    idx = sel["idx"]
    frames_all = list(range(b0, b0 + length))
    if max_frames:
        frames_all = frames_all[:max_frames]
    usable = [t for t in node_frames(b0, length) if t + max(LAGS) in frames_all]
    keep = np.isin(tr.pt_t[idx], usable)
    for k in ("idx", "y", "hard", "partner"):
        sel[k] = sel[k][keep]
    idx = sel["idx"]
    log(f"shard b{b0} z{zchunk} halo={halo}: owned z {sel['z_owned'].tolist()}, available par/dau/hard/cont "
        f"{sel['avail'].tolist()}, selected {np.bincount(sel['y'], minlength=3).tolist()} "
        f"(hard {int(sel['hard'].sum())}) over node frames {usable}")
    zoff = ZCHUNK * zchunk - (HALO if halo else 0)
    rng = np.random.default_rng(b0 * 1000 + zchunk)
    mk = marker()
    n = len(idx)
    X = np.zeros((n, len(LAGS) + 1, *CROP), np.float16)
    LOHI = np.zeros((n, len(LAGS), 2), np.float32)
    ORIG = np.zeros((n, 3), np.int16)
    WOK = np.zeros(n, bool)
    WZERO = np.zeros(n, np.float32)
    WCELLS = np.zeros(n, np.int32)
    vox = tr.pt_vox[idx]
    centres = np.array([[round(float(z)), round(float(y) / POOL), round(float(x) / POOL)] for z, y, x in vox],
                       np.int64).reshape(-1, 3)
    pooled: dict[int, np.ndarray] = {}
    new_halo: dict[int, np.ndarray] = {}
    timing = dict(download_decode_pool=0.0, cut=0.0)
    if n == 0:                                   # nothing to cut: write the empty shard without streaming the chunks
        frames_all = []

    def fetch(t):
        arr = load_pooled(t, zchunk)
        if need_fetch:
            t0 = time.time()
            h = load_pooled_slices(t, zchunk - 1, ZCHUNK - HALO, ZCHUNK)
            log(f"  halo t={t} from z{zchunk - 1}: {h.shape} in {time.time() - t0:.0f}s")
            return t, arr, h
        return t, arr, None

    with ThreadPoolExecutor(1) as ex:
        fut = ex.submit(fetch, frames_all[0]) if frames_all else None
        for i, t in enumerate(frames_all):
            t0 = time.time()
            _, arr, fetched_halo = fut.result()
            if i + 1 < len(frames_all):
                fut = ex.submit(fetch, frames_all[i + 1])
            timing["download_decode_pool"] += time.time() - t0
            new_halo[t] = arr[-HALO:].copy()
            if halo:
                arr = np.concatenate([halo_in[t] if halo_in is not None else fetched_halo, arr], axis=0)
            pooled[t] = arr
            log(f"  frame {t} z{zchunk}: pooled {arr.shape} (wait {time.time() - t0:.0f}s)")
            tn = t - max(LAGS)                                         # node frame whose last lag just arrived
            if tn in usable:
                t1 = time.time()
                frames = [pooled[tn + lag] for lag in LAGS]
                lo = (zoff, 0, 0)
                hi = (zoff + frames[0].shape[0], frames[0].shape[1], frames[0].shape[2])
                fp = tr.frame_points(tn)
                fp_c = tr.pt_vox[fp] / np.array([1, POOL, POOL], np.float32)
                for j in np.flatnonzero(tr.pt_t[idx] == tn):
                    c = tuple(int(v) for v in centres[j])
                    o, WOK[j], WZERO[j] = pick_window(frames[LAGS.index(0)], zoff, c, lo, hi, rng)
                    X[j], LOHI[j] = cut_sample(frames, zoff, c, o, pad, mk)
                    ORIG[j] = o
                    inside = np.all((fp_c >= np.array(o) - 0.5) & (fp_c < np.array(o) + np.array(WIN) - 0.5), axis=1)
                    WCELLS[j] = int(inside.sum())
                timing["cut"] += time.time() - t1
            for old in [k for k in pooled if k <= t - (max(LAGS) - min(LAGS))]:
                del pooled[old]
    tr_id = tr.pt_track[idx]
    # node position (z, y, x) in level-0 voxels as one array: the keys x / y are the crops and the labels
    meta = dict(t=tr.pt_t[idx].astype(np.int16), zyx=vox.astype(np.float32), track=tr_id.astype(np.int32),
                partner=sel["partner"].astype(np.int32), hard=sel["hard"], win_origin=ORIG, norm_lohi=LOHI,
                win_cells=WCELLS, win_ok=WOK, win_zero_frac=WZERO)
    path = shard_path(b0, zchunk, shard_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    info = dict(block=b0, length=length, zchunk=zchunk, halo=halo, halo_source=halo_source,
                halo_verified=halo_verified, z_owned=sel["z_owned"].tolist(),
                available_par_dau_hard_cont=sel["avail"].tolist(), classes=list(CLASSES), lags=list(LAGS), pool=POOL,
                crop=list(CROP), window=list(WIN), pct=[LO_PCT, HI_PCT], clip=list(CLIP), window_pad=pad,
                hard_frac=hard_frac, neg_ratio=neg_ratio, frames=frames_all, node_frames=usable,
                source=IMG_URL, tracks=TRK_URL)
    np.savez_compressed(tmp, x=X, y=sel["y"], block=np.full(n, b0, np.int16), zchunk=np.full(n, zchunk, np.int8),
                        info=np.array(json.dumps(info)), **meta)
    os.replace(tmp, path)
    timing["total"] = time.time() - t_start
    log(f"windows: {int(WOK.sum())}/{n} accepted, {int((~WOK).sum())} kept with win_ok=False")
    log(f"wrote {path} n={n} ({path.stat().st_size / 1e6:.0f} MB); timing {json.dumps({k: round(v, 1) for k, v in timing.items()})}")
    return new_halo or None                      # an empty shard streams nothing: the next z-chunk must fetch its halo


# ---------------------------------------------------------------------------------------------------------------- CLI
def cmd_density(a) -> None:
    tr = Tracks()
    divs = division_table(tr)
    log("divisions: 2-child parents", len(divs["ok"]), "len_ok", int(divs["len_ok"].sum()), "sep_ok",
        int(divs["sep_ok"].sum()), "step_ok", int(divs["step_ok"].sum()), "lineage_ok", int(divs["lineage_ok"].sum()),
        "ALL", int(divs["ok"].sum()))
    rows = density_table(tr, divs)
    OUT.mkdir(parents=True, exist_ok=True)
    import csv
    with open(OUT / "density.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows[::a.every]:
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
    log(f"-> {OUT / 'density.csv'}")


def _load_density() -> list[dict]:
    import csv
    p = OUT / "density.csv"
    if not p.exists():
        raise SystemExit("run `density` first")
    with open(p) as fh:
        return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(fh)]


def cmd_blocks(a) -> None:
    rows = _load_density()
    blocks = choose_blocks(rows, a.n, a.len)
    (OUT / "blocks.json").write_text(json.dumps(blocks, indent=1))
    for b in blocks:
        print(b)
    log(f"-> {OUT / 'blocks.json'}")


def cmd_labels(a) -> None:
    tr = Tracks()
    divs = division_table(tr)
    cand = block_candidates(tr, divs, a.block, a.len)
    print("block", a.block, "candidates:", {k: len(v) for k, v in cand.items() if k in CLASSES + ("hard",)})
    for zc in a.zchunks:
        for halo in (False, True):
            s = select_samples(tr, cand, zc, halo, seed=0)
            print(f" z{zc} halo={halo} owned {s['z_owned'].tolist()} available par/dau/hard/cont {s['avail'].tolist()}"
                  f" selected per class {np.bincount(s['y'], minlength=3).tolist()} hard {int(s['hard'].sum())}")


def cmd_extract(a) -> None:
    tr = Tracks()
    divs = division_table(tr)
    if a.blocks:
        blocks = a.blocks
    else:
        p = OUT / "blocks.json"
        if not p.exists():
            raise SystemExit("no --blocks and no blocks.json (run `blocks`)")
        blocks = [b["b0"] for b in json.loads(p.read_text())]
    shard_dir = Path(a.shard_dir) if a.shard_dir else None
    if a.max_frames and shard_dir is None:
        raise SystemExit("--max-frames writes partial shards: give --shard-dir outside data_external/dorado/shards")
    verified = bool(getattr(a, "no_verify_halo", False))      # one level-0 partial-read check per run is enough
    for b0 in blocks:
        halo, prev = None, None
        for zc in sorted(a.zchunks):
            if shard_path(b0, zc, shard_dir).exists():
                log(f"skip existing {shard_path(b0, zc, shard_dir)}")
                halo, prev = None, zc
                continue
            use_halo = halo if (prev == zc - 1 and halo is not None) else None
            want_halo = (zc + 1) in a.zchunks
            check = use_halo is not None and not verified
            h = extract_shard(tr, divs, b0, a.len, zc, use_halo, a.window_pad, a.hard_frac, a.neg_ratio,
                              a.max_frames, shard_dir, fetch_halo=not a.no_fetch_halo, verify_halo=check)
            verified |= check
            halo, prev = (h if want_halo else None), zc


def cmd_inspect(a) -> None:
    d = np.load(a.shard)
    info = json.loads(str(d["info"]))
    x, y = d["x"].astype(np.float32), d["y"]
    print("info", info)
    print("n", len(y), "class counts", {c: int((y == i).sum()) for i, c in enumerate(CLASSES)}, "hard",
          int(d["hard"].sum()))
    print("x", x.shape, x.dtype, "min", float(x[:, :4].min()), "max", float(x[:, :4].max()), "mean",
          round(float(x[:, :4].mean()), 3), "finite", bool(np.isfinite(x).all()))
    print("norm lo (raw p50) median", float(np.median(d["norm_lohi"][..., 0])), "hi (raw p99.5) median",
          float(np.median(d["norm_lohi"][..., 1])), "hi/lo median",
          round(float(np.median(d["norm_lohi"][..., 1] / np.maximum(d["norm_lohi"][..., 0], 1e-6))), 2))
    if "win_ok" in d.files:
        print("windows accepted (Kaggle-like bounds):", int(d["win_ok"].sum()), "/", len(y))
    print("cells per window (tracked, node frame): median", int(np.median(d["win_cells"])), "p10/p90",
          np.percentile(d["win_cells"], [10, 90]).astype(int).tolist())
    zc, yc, xc = CROP[0] // 2, CROP[1] // 2, CROP[2] // 2
    ctr = x[:, :4, zc - 2:zc + 2, yc - 3:yc + 3, xc - 3:xc + 3]
    ring = x[:, :4, zc - 4:zc + 4, yc - 8:yc + 8, xc - 8:xc + 8]
    groups = {"cont": (y == 0) & ~d["hard"], "hard": (y == 0) & d["hard"], "parent": y == 1, "daughter": y == 2}
    cmean = ctr.mean(axis=(2, 3, 4))                                   # (N, 4) per-sample centre mean per lag
    cstd = ctr.std(axis=(2, 3, 4))
    cmax = ctr.max(axis=(2, 3, 4))
    print("per lag (-1, 0, +1, +2): centre = 4x6x6 pooled voxels at the crop centre, region = 8x16x16")
    for g, m in groups.items():
        if m.sum() == 0:
            continue
        print(f"  {g:9s} n={int(m.sum()):5d} centre mean {np.round(cmean[m].mean(0), 3).tolist()} "
              f"centre std {np.round(cstd[m].mean(0), 3).tolist()} centre max {np.round(cmax[m].mean(0), 3).tolist()} "
              f"region mean {np.round(ring[m].mean(axis=(0, 2, 3, 4)), 3).tolist()}")
    ref = groups["cont"]
    for g in ("parent", "daughter", "hard"):
        m = groups[g]
        if m.sum() < 2 or ref.sum() < 2:
            continue

        def eff(v, m=m):
            return (v[m].mean(0) - v[ref].mean(0)) / np.sqrt(0.5 * (v[m].var(0) + v[ref].var(0)) + 1e-12)

        print(f"  Cohen d {g} vs cont per lag: centre mean {np.round(eff(cmean), 2).tolist()} "
              f"centre std {np.round(eff(cstd), 2).tolist()} centre max {np.round(eff(cmax), 2).tolist()}")
    if a.png:
        _save_png(x, y, d["hard"], Path(a.png))


def _save_png(x: np.ndarray, y: np.ndarray, hard: np.ndarray, path: Path, per: int = 6, zoom: int = 4,
              vmax: float = 2.5) -> None:
    """Grid (Pillow): rows = samples grouped parent / daughter / hard / cont, columns = lags -1..+2, each tile the
    max projection over the central 6 z-slices of the crop, grey range [-0.5, vmax]."""
    from PIL import Image, ImageDraw
    rng = np.random.default_rng(0)
    rows = []
    for name, m in (("parent", y == 1), ("daughter", y == 2), ("hard", (y == 0) & hard), ("cont", (y == 0) & ~hard)):
        ids = np.flatnonzero(m)
        rows += [(name, i) for i in rng.choice(ids, min(per, len(ids)), replace=False)]
    zc = CROP[0] // 2
    tile, gap, left, top = CROP[1] * zoom, 4, 70, 18
    img = Image.new("L", (left + 4 * (tile + gap), top + len(rows) * (tile + gap)), 255)
    draw = ImageDraw.Draw(img)
    for c in range(4):
        draw.text((left + c * (tile + gap) + tile // 3, 3), f"lag {LAGS[c]:+d}", fill=0)
    for r, (name, i) in enumerate(rows):
        draw.text((4, top + r * (tile + gap) + tile // 2 - 5), name, fill=0)
        for c in range(4):
            v = x[i, c, zc - 3:zc + 3].max(0)
            g = np.clip((v + 0.5) / (vmax + 0.5) * 255, 0, 255).astype(np.uint8)
            t = Image.fromarray(g).resize((tile, tile), Image.NEAREST)
            img.paste(t, (left + c * (tile + gap), top + r * (tile + gap)))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print("png ->", path)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("tracks"); s.add_argument("--force", action="store_true")
    s = sub.add_parser("density"); s.add_argument("--every", type=int, default=25)
    s = sub.add_parser("blocks"); s.add_argument("--n", type=int, default=4); s.add_argument("--len", type=int, default=8)
    s = sub.add_parser("labels"); s.add_argument("--block", type=int, required=True)
    s.add_argument("--len", type=int, default=8); s.add_argument("--zchunks", type=int, nargs="+", default=[1, 2])
    s = sub.add_parser("extract")
    s.add_argument("--blocks", type=int, nargs="*")
    s.add_argument("--zchunks", type=int, nargs="+", default=[1, 2])
    s.add_argument("--len", type=int, default=8)
    s.add_argument("--hard-frac", type=float, default=0.5)
    s.add_argument("--neg-ratio", type=float, default=3.0)
    s.add_argument("--window-pad", action="store_true",
                   help="bake the Kaggle clip-border zero padding into x (default: store real surroundings)")
    s.add_argument("--max-frames", type=int, default=None, help="debug: stream only the first N frames of a block")
    s.add_argument("--shard-dir", default=None, help="output directory (default data_external/dorado/shards)")
    s.add_argument("--no-fetch-halo", action="store_true",
                   help="do not partial-read the previous z-chunk when its halo is not in memory (shard then owns "
                        "[128k + 8, 128k + 120) only)")
    s.add_argument("--no-verify-halo", action="store_true",
                   help="skip the one-per-run bit-exact check of the partial halo read against a fully decoded chunk")
    s = sub.add_parser("inspect"); s.add_argument("shard"); s.add_argument("--png", default=None)
    a = ap.parse_args(argv)
    {"tracks": lambda a: fetch_tracks(a.force), "density": cmd_density, "blocks": cmd_blocks, "labels": cmd_labels,
     "extract": cmd_extract, "inspect": cmd_inspect}[a.cmd](a)


if __name__ == "__main__":
    main()
