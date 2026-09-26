"""MITOSE / v6 -- the PAIR CROP: what a pair scorer looks at, and the proof that
it looks at the right place.

WHY A SECOND CROP AT ALL. Every head this lane has shipped scores the MOTHER
ALONE, and FRONT A's gate autopsy says that is why it cannot rank the divisions
its poser misses: on A199's 151 divisions the first failing condition is the
POSER's (posed 49, distance envelope 32, symmetry 28, daughter absent 19, both
daughters on one node 15, pass 6), and the separating evidence lives in the PAIR
-- my own trio table says the two probmat edge probabilities separate true trios
by a factor 50. A node head never sees them.

THE PAIR CROP, declared before anything is trained:

  frame       t+1, the daughters' own frame, with the project's usual four-offset
              stack (-2, -1, 0, +1) taken AROUND t+1 -- so the stack spans
              t-1..t+2 and carries t+2, the frame the deployed divergence gate
              reads. The mother crop is unchanged: the same four offsets around
              t, i.e. t-2..t+1.
  centre      the MIDPOINT of the two daughters, in GRID voxels.
  orientation the crop is rotated in xy so that the daughter axis lies along +y.
              The rotation is a per-plane affine with LINEAR interpolation and
              edge replication; z is never resampled. This is a declared part of
              the recipe, not a detail: it is applied identically at training and
              at inference, and the interpolation loss is measured by the
              selftest rather than assumed.
  order       the pair is UNORDERED, so the ordering is made canonical BEFORE the
              angle is computed: the daughter with the lexicographically smaller
              (z, y, x) in grid voxels is the first. Swapping the two arguments
              must therefore return a BIT-IDENTICAL crop, and the selftest proves
              it rather than trusting it.
  refusal     a pair whose xy separation would put a daughter outside the crop is
              REFUSED by name (`PairCropError`), never silently cropped: a
              half-visible pair is exactly the case a pair scorer must not learn
              to score.

THE ALTERNATIVE, declared once and not both: two separate daughter crops merged
by a symmetric (order-invariant) function. It is the arm's ONE variant, it is
chosen before launch, and it is not evaluated afterwards to pick the better
number.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mh_data as D            # noqa: E402

PAIR_OFFSETS = D.OFFSETS
"""The same four offsets, taken around t+1 instead of t."""

MAX_PAIR_SEP_GRID = D.Y_BANK - 8
"""The widest daughter separation a crop of this size can hold with four voxels
of margin on each side. Y_BANK is 48 grid voxels, so 40 -- and one grid voxel is
0,8125 um in xy, so about 32,5 um, well beyond the p90 sister separation of
14,36 um measured on the 151."""


class PairCropError(ValueError):
    """A named refusal of this module. Never a silent fallback."""


def date_u():
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                          capture_output=True, text=True,
                          check=True).stdout.strip()


def canonical_order(d1_grid, d2_grid):
    """The pair is unordered: this makes it ordered in ONE deterministic way, so
    that swapping the caller's arguments cannot change a single voxel."""
    a = tuple(float(v) for v in d1_grid)
    b = tuple(float(v) for v in d2_grid)
    return (a, b) if a <= b else (b, a)


def pair_geometry(d1_grid, d2_grid):
    a, b = canonical_order(d1_grid, d2_grid)
    centre = tuple((a[i] + b[i]) / 2.0 for i in range(3))
    dz = b[0] - a[0]
    dy = b[1] - a[1]
    dx = b[2] - a[2]
    sep_xy = math.hypot(dy, dx)
    theta = math.atan2(dx, dy)        # 0 means the pair already lies along +y
    return {"first": a, "second": b, "centre": centre, "dz": dz,
            "sep_xy_grid": sep_xy, "theta_rad": theta,
            "sep_grid": math.sqrt(dz * dz + dy * dy + dx * dx)}


def _rotate_xy(plane, theta, cy, cx, out_h, out_w):
    """One z-plane, rotated by -theta about (cy, cx) and cropped to
    (out_h, out_w), linear interpolation, edge replication.

    Written with an explicit map_coordinates rather than a library rotate so
    that the centre, the crop and the rotation are ONE resampling and not three.
    """
    from scipy import ndimage
    ys, xs = np.meshgrid(np.arange(out_h, dtype=np.float64) - out_h // 2,
                         np.arange(out_w, dtype=np.float64) - out_w // 2,
                         indexing="ij")
    c, s = math.cos(theta), math.sin(theta)
    src_y = cy + c * ys - s * xs
    src_x = cx + s * ys + c * xs
    return ndimage.map_coordinates(plane, [src_y, src_x], order=1,
                                   mode="nearest").astype(np.float32)


def _rotate_stack(vol, theta, cz, cy, cx):
    """The whole (Z_BANK, Y_BANK, X_BANK) window in ONE resampling call.

    Identical arithmetic to `_rotate_xy` plane by plane -- z is a passthrough
    coordinate, clamped by the same `mode="nearest"` -- and the selftest asserts
    the two are BIT-IDENTICAL. It exists only because scipy's per-call overhead
    on a 48x48 plane dominated the measured chrono: fifteen calls per channel at
    4,8 rows/s, one call per channel instead."""
    from scipy import ndimage
    zs = np.arange(D.Z_BANK, dtype=np.float64) - D.Z_BANK // 2 + cz
    ys, xs = np.meshgrid(np.arange(D.Y_BANK, dtype=np.float64) - D.Y_BANK // 2,
                         np.arange(D.X_BANK, dtype=np.float64) - D.X_BANK // 2,
                         indexing="ij")
    c, s_ = math.cos(theta), math.sin(theta)
    src_y = cy + c * ys - s_ * xs
    src_x = cx + s_ * ys + c * xs
    Z = np.repeat(zs[:, None, None], D.Y_BANK, axis=1)
    Z = np.repeat(Z, D.X_BANK, axis=2)
    Y = np.broadcast_to(src_y, (D.Z_BANK, D.Y_BANK, D.X_BANK))
    X = np.broadcast_to(src_x, (D.Z_BANK, D.Y_BANK, D.X_BANK))
    return ndimage.map_coordinates(vol, [Z, Y, X], order=1,
                                   mode="nearest").astype(np.float32)


def pair_crop_from_film(reader, t_mother, d1_grid, d2_grid):
    """(4, Z_BANK, Y_BANK, X_BANK) float32 + a log, centred on the daughters'
    midpoint at t+1 and oriented so the daughter axis lies along +y."""
    g = pair_geometry(d1_grid, d2_grid)
    if g["sep_xy_grid"] > MAX_PAIR_SEP_GRID:
        raise PairCropError(
            "pair separation %.2f grid voxels exceeds the crop's reach %d "
            "(film %s, t=%s)" % (g["sep_xy_grid"], MAX_PAIR_SEP_GRID,
                                 getattr(reader, "film", "?"), t_mother))
    tp = int(t_mother) + 1
    frames = [int(min(max(tp + d, 0), int(reader.n_frames) - 1))
              for d in PAIR_OFFSETS]
    cz = int(round(g["centre"][0]))
    cy, cx = g["centre"][1], g["centre"][2]
    out = np.empty(D.BANK_SHAPE, dtype=np.float32)
    p99 = []
    hz = D.Z_BANK // 2
    for c, f in enumerate(frames):
        vol, p = reader.normalised(f)
        p99.append(float(p))
        out[c] = _rotate_stack(vol, g["theta_rad"], cz, cy, cx)
    clamped = [int(tp + d) for d in PAIR_OFFSETS
               if not (0 <= tp + d < reader.n_frames)]
    return out, {"frames": frames, "p99": p99, "clamped": clamped,
                 "theta_rad": g["theta_rad"], "sep_xy_grid": g["sep_xy_grid"],
                 "sep_grid": g["sep_grid"], "dz": g["dz"],
                 "centre_grid": list(g["centre"])}


# ----------------------------------------------------------------- selftest

class FabricatedReader:
    """A film that exists only in memory: a flat background with gaussian blobs
    planted at named GRID positions, so a test can say exactly where a voxel
    should land."""

    def __init__(self, shape=(24, 128, 128), n_frames=6, blobs=None, sigma=1.6):
        self.film = "fab_pair"
        self.n_frames = int(n_frames)
        self._shape = shape
        self._blobs = blobs or {}
        self._sigma = float(sigma)
        self._cache = {}

    def normalised(self, f):
        f = int(f)
        if f in self._cache:
            return self._cache[f]
        vol = np.full(self._shape, 0.05, dtype=np.float32)
        zz, yy, xx = np.ogrid[:self._shape[0], :self._shape[1], :self._shape[2]]
        for (bf, z, y, x, amp) in self._blobs.get(f, []):
            d2 = ((zz - z) ** 2 + (yy - y) ** 2 + (xx - x) ** 2)
            vol = vol + amp * np.exp(-d2 / (2.0 * self._sigma ** 2))
        self._cache[f] = (vol.astype(np.float32), 1.0)
        return self._cache[f]


def cmd_selftest(a):
    """BOTH DIRECTIONS, on voxels fabricated for the purpose."""
    cz, cy, cx = 12, 64, 64
    sep = 12.0                      # grid voxels between the two daughters
    ang = math.radians(37.0)        # a deliberately non-axis-aligned pair
    d1 = (cz, cy - (sep / 2) * math.cos(ang), cx - (sep / 2) * math.sin(ang))
    d2 = (cz, cy + (sep / 2) * math.cos(ang), cx + (sep / 2) * math.sin(ang))
    blobs = {3: [(3, d1[0], d1[1], d1[2], 1.0), (3, d2[0], d2[1], d2[2], 1.0)]}
    reader = FabricatedReader(blobs=blobs)

    crop, log = pair_crop_from_film(reader, 2, d1, d2)
    mid = D.Z_BANK // 2
    plane = crop[2][mid]            # channel 2 = offset 0 = frame t+1 itself
    hy, hx = D.Y_BANK // 2, D.X_BANK // 2
    col = plane[:, hx]
    peaks = np.argsort(-col)[:2]
    peaks = sorted(int(v) for v in peaks)
    want = sorted([hy - int(round(sep / 2)), hy + int(round(sep / 2))])
    on_axis = bool(abs(peaks[0] - want[0]) <= 1 and abs(peaks[1] - want[1]) <= 1)
    # FAR from the pair axis, not merely off the centre COLUMN: a blob has a
    # width, so the neighbouring columns carry nearly the whole peak and a test
    # that calls them "off axis" is a wrong instrument, not a wrong crop. This
    # one asks that the field be BACKGROUND beyond four voxels of the axis.
    far = np.concatenate([plane[:, :hx - 4], plane[:, hx + 5:]], axis=1)
    off_axis_max = float(far.max())
    on_axis_max = float(col.max())

    swapped, _ = pair_crop_from_film(reader, 2, d2, d1)
    identical = bool(np.array_equal(crop, swapped))

    # the fast one-call resampling must be BIT-IDENTICAL to the reference that
    # rotates plane by plane, or the speed-up is a different measurement
    gg = pair_geometry(d1, d2)
    ref = np.empty(D.BANK_SHAPE, dtype=np.float32)
    czr = int(round(gg["centre"][0]))
    hzr = D.Z_BANK // 2
    for c, f in enumerate([int(min(max(3 + d, 0), reader.n_frames - 1))
                           for d in PAIR_OFFSETS]):
        vol, _p = reader.normalised(f)
        for k in range(D.Z_BANK):
            z = int(min(max(czr - hzr + k, 0), vol.shape[0] - 1))
            ref[c, k] = _rotate_xy(vol[z], gg["theta_rad"], gg["centre"][1],
                                   gg["centre"][2], D.Y_BANK, D.X_BANK)
    fast_equals_reference = bool(np.array_equal(crop, ref))

    # the interpolation is measured, not assumed: a rotated blob must keep its
    # peak. A single centred blob is the control.
    single = FabricatedReader(blobs={3: [(3, cz, cy, cx, 1.0)]})
    c1, _ = pair_crop_from_film(single, 2, (cz, cy - 3, cx), (cz, cy + 3, cx))
    peak_axis_aligned = float(c1[2][mid].max())
    c2, _ = pair_crop_from_film(single, 2, (cz, cy - 3 * math.cos(ang),
                                            cx - 3 * math.sin(ang)),
                                (cz, cy + 3 * math.cos(ang),
                                 cx + 3 * math.sin(ang)))
    peak_rotated = float(c2[2][mid].max())
    interp_loss = (peak_axis_aligned - peak_rotated) / max(peak_axis_aligned, 1e-9)

    refused = False
    try:
        pair_crop_from_film(reader, 2, (cz, cy - 40, cx), (cz, cy + 40, cx))
    except PairCropError:
        refused = True

    ok = (on_axis and identical and refused and fast_equals_reference
          and (on_axis_max > 2 * off_axis_max))
    rep = {"schema": "BIOCEL_RECU_V1", "date_u": date_u(), "lane": "MITOSE",
           "question": ("the v6 PAIR CROP proved in both directions on a "
                        "fabricated film"),
           "harnais": "mhv6_pair_crop.py selftest", "assiette": "fabricated",
           "crop_shape": list(D.BANK_SHAPE),
           "pair_offsets_around_t_plus_1": list(PAIR_OFFSETS),
           "passing_path": {
               "planted_separation_grid": sep,
               "planted_angle_deg": 37.0,
               "peaks_on_the_crop_y_axis": peaks,
               "expected": want, "within_one_voxel": on_axis,
               "peak_on_axis": round(on_axis_max, 5),
               "max_beyond_four_voxels_of_the_axis": round(off_axis_max, 5),
               "background_planted": 0.05},
           "order_invariance": {"swapping_the_two_daughters_is_bit_identical":
                                identical},
           "one_call_resampling_is_bit_identical_to_the_plane_by_plane_reference":
               fast_equals_reference,
           "refusing_path": {"separation_80_grid_voxels_raises_PairCropError":
                             refused,
                             "max_separation_grid": MAX_PAIR_SEP_GRID},
           "interpolation_cost_measured": {
               "peak_axis_aligned": round(peak_axis_aligned, 5),
               "peak_rotated_37deg": round(peak_rotated, 5),
               "relative_peak_loss": round(float(interp_loss), 5)},
           "verdict": ("BOTH DIRECTIONS PROVEN" if ok else "REFUSED"),
           "what_this_does_not_establish": (
               "nothing about a real film and nothing about a model: these "
               "voxels were fabricated to have a known answer")}
    D.write_json(a.out, rep)
    print(json.dumps(rep, indent=1))
    if not ok:
        raise SystemExit(2)


def cmd_chrono(a):
    """The MEASURED cost of the two crops, on real films, so the bank's size and
    fill time are read and not guessed."""
    import polars as pl
    import mh_data as MD
    import grille as G
    films = sorted(p.name[:-8] for p in
                   (pathlib.Path(a.trio_dir) / "films").glob("*.parquet"))[:a.n_films]
    n = 0
    t0 = time.time()
    per_film = []
    for film in films:
        df = pl.read_parquet(str(pathlib.Path(a.trio_dir) / "films"
                                 / (film + ".parquet")))
        if df.height == 0:
            continue
        rng = np.random.default_rng(20260908)
        take = rng.choice(df.height, size=min(a.per_film, df.height),
                          replace=False)
        if a.sort_by_frame:
            # The reader memoises ONE frame at a time. Rows drawn at random walk
            # the film back and forth and pay a full normalisation per row; rows
            # visited in frame order pay it once per frame. The bank writer must
            # do this, so the chrono must measure it.
            tt = df["t"].to_numpy()
            take = take[np.argsort(tt[take], kind="mergesort")]
        reader = MD.FilmReader(a.zarr_dir, film)
        tf = time.time()
        k = 0
        for i in take:
            r = df[int(i)]
            t = int(r["t"][0])
            g = G.natif_vers_grille(np.array([
                [r["m_z"][0], r["m_y"][0], r["m_x"][0]],
                [r["d1_z"][0], r["d1_y"][0], r["d1_x"][0]],
                [r["d2_z"][0], r["d2_y"][0], r["d2_x"][0]]], dtype=np.float64))
            try:
                MD.crop_from_film(reader, t, g[0])
                pair_crop_from_film(reader, t, g[1], g[2])
            except (PairCropError, MD.MitosisDataError):
                continue
            k += 1
        n += k
        per_film.append({"film": film, "pairs": k,
                         "seconds": round(time.time() - tf, 2)})
        del reader
    secs = time.time() - t0
    rate = n / max(secs, 1e-9)
    row_bytes = int(np.prod(D.BANK_SHAPE)) * 2 * 2      # mother + pair, fp16
    rep = {"schema": "BIOCEL_RECU_V1", "date_u": date_u(), "lane": "MITOSE",
           "question": "the MEASURED cost of a v6 row: two crops, read live",
           "harnais": "mhv6_pair_crop.py chrono on MIT_GPU_2 (CPU)",
           "assiette": {"trio_dir": a.trio_dir, "n_films": len(per_film),
                        "per_film": a.per_film,
                        "rows_visited_in_frame_order": bool(a.sort_by_frame)},
           "n_rows_measured": n, "seconds": round(secs, 2),
           "rows_per_second_one_process": round(rate, 3),
           "row_bytes_two_crops_fp16": row_bytes,
           "per_film": per_film,
           "what_this_does_not_establish": (
               "nothing about a bank: this reads crops and throws them away")}
    D.write_json(a.out, rep)
    print(json.dumps({"n_rows": n, "seconds": round(secs, 2),
                      "rows_per_second": round(rate, 3),
                      "row_bytes": row_bytes}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("selftest")
    p.add_argument("--out", required=True)
    p.set_defaults(f=cmd_selftest)
    p = sub.add_parser("chrono")
    p.add_argument("--trio-dir", required=True)
    p.add_argument("--zarr-dir", required=True)
    p.add_argument("--n-films", type=int, default=10)
    p.add_argument("--per-film", type=int, default=40)
    p.add_argument("--sort-by-frame", action="store_true")
    p.add_argument("--out", required=True)
    p.set_defaults(f=cmd_chrono)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
