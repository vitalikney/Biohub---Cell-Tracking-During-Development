"""ENG/PRIOR -- the crop reader, a DELIBERATE COPY of two functions of mh_data.

WHY A COPY AND NOT AN IMPORT. `10_CHANTIERS/20_MITOSE/impl/mh_data.py` imports
`cuisson`, which opens `.geff` ground truth at module level. This lane must never
pull ground truth into the crop path, and Guillaume's 07/09 directive is
"duplicate rather than share". So `FilmReader` and `crop_from_film` below are
copied VERBATIM (comments translated, behaviour untouched) from mh_data, and the
two constants they depend on are re-stated with their provenance. `grille` and
`normalisation` ARE imported, unchanged, because they are the single definition
of the lattice and of the p99 normalisation in this project and a second copy of
those would be a second truth.

THE LATTICE, because it is the number this lane got wrong once already:
`grille.FACTEUR_XY` = 2, so the crop lives on the MITOSE grid (64, 128, 128) with
a voxel of (1.625, 0.8125, 0.8125) um -- ANISOTROPIC. The fed crop (11, 40, 40)
is therefore z +/- 8.125 um and y/x +/- 16.25 um around the object.
"""

from __future__ import annotations

import pathlib

import numpy as np

import grille as G  # noqa: F401  (re-exported for callers)
import normalisation as N

# --- geometry, provenance mh_data.py lines 55-70 ---------------------------
Z_FED, Y_FED, X_FED = 11, 40, 40
Z_MARGIN, XY_MARGIN = 2, 4
Z_BANK = Z_FED + 2 * Z_MARGIN            # 15
Y_BANK = Y_FED + 2 * XY_MARGIN           # 48
X_BANK = X_FED + 2 * XY_MARGIN           # 48
import os as _os
_fwd = _os.environ.get("FWD_OFFSETS", "").strip()
# ENG/MOTHER, order 34 amendment 10: the temporal window is the ONLY
# variable of the forward-head experiment, so it is read from the
# environment and the value actually used is printed once. Empty means
# the default of record, unchanged.
OFFSETS = (tuple(int(x) for x in _fwd.split(",")) if _fwd
           else N.DECALAGES_DEFAUT)          # default (-2, -1, 0, +1)
if _fwd:
    print("pp_crop: OFFSETS OVERRIDDEN ->", OFFSETS, flush=True)
N_CHANNELS = len(OFFSETS)
BANK_SHAPE = (N_CHANNELS, Z_BANK, Y_BANK, X_BANK)
FED_SHAPE = (N_CHANNELS, Z_FED, Y_FED, X_FED)


class CropError(ValueError):
    """A named refusal of this module. Never a silent fallback."""


class FilmReader:
    """Frames of one film, binned and per-image normalised, memoised."""

    def __init__(self, zarr_dir, film):
        import zarr
        path = pathlib.Path(zarr_dir) / (film + ".zarr")
        if not path.exists():
            raise CropError("zarr absent: " + str(path))
        self.film = film
        self._arr = zarr.open(str(path), mode="r")["0"]
        self.n_frames = int(self._arr.shape[0])
        self._cache = {}
        self.frames_read = 0

    def _raw(self, f):
        self.frames_read += 1
        return np.asarray(self._arr[int(f)])

    def normalised(self, f):
        f = int(f)
        if f not in self._cache:
            self._cache[f] = N.trame_normalisee(self._raw, f)
        return self._cache[f]

    def keep_only(self, keep):
        for f in list(self._cache):
            if f not in keep:
                del self._cache[f]


def clamped_frames(t, n_frames):
    """The four frames actually read for an object at t, edge-clamped."""
    return [int(min(max(int(t) + d, 0), int(n_frames) - 1)) for d in OFFSETS]


def crop_from_film(reader, t, zyx_grid):
    """(4, 15, 48, 48) float32 + a log; out-of-volume filled by edge replication."""
    z0 = int(round(float(zyx_grid[0])))
    y0 = int(round(float(zyx_grid[1])))
    x0 = int(round(float(zyx_grid[2])))
    frames = clamped_frames(t, reader.n_frames)
    hz, hy, hx = Z_BANK // 2, Y_BANK // 2, X_BANK // 2
    out = np.empty(BANK_SHAPE, dtype=np.float32)
    p99 = []
    padded = False
    for c, f in enumerate(frames):
        vol, p = reader.normalised(f)
        p99.append(float(p))
        zs, ys, xs = vol.shape
        za, zb = z0 - hz, z0 - hz + Z_BANK
        ya, yb = y0 - hy, y0 - hy + Y_BANK
        xa, xb = x0 - hx, x0 - hx + X_BANK
        pad = ((max(0, -za), max(0, zb - zs)),
               (max(0, -ya), max(0, yb - ys)),
               (max(0, -xa), max(0, xb - xs)))
        sub = vol[max(0, za):min(zs, zb), max(0, ya):min(ys, yb),
                  max(0, xa):min(xs, xb)]
        if sub.size == 0:
            raise CropError("empty crop for %s t=%s at %s"
                            % (reader.film, t, (z0, y0, x0)))
        if any(any(q) for q in pad):
            sub = np.pad(sub, pad, mode="edge")
            padded = True
        out[c] = sub
    clamped = [int(int(t) + d) for d in OFFSETS
               if not (0 <= int(t) + d < reader.n_frames)]
    return out, {"frames": frames, "p99": p99, "clamped": clamped,
                 "padded": bool(padded)}


def fed_view(bank_crop):
    """The inner (4, 11, 40, 40) the network is fed, from a stored (4, 15, 48, 48)."""
    a = np.asarray(bank_crop)
    if a.shape[-4:] != BANK_SHAPE:
        raise CropError("expected %s, got %s" % (BANK_SHAPE, a.shape))
    return a[..., Z_MARGIN:Z_MARGIN + Z_FED,
             XY_MARGIN:XY_MARGIN + Y_FED,
             XY_MARGIN:XY_MARGIN + X_FED]
