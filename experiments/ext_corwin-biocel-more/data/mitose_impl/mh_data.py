"""MITOSE / mitosis head -- the corpus, read LIVE from zarr + geff.

WHAT THIS IS. The head is a per-candidate classifier: given a node (film, t,
position) it answers "does this cell divide between t and t+1?". Its input is
a small 3D+t crop centred on that node. This module turns the ground truth
(`.geff`) and the images (`.zarr`) into that crop bank, without any
intermediate "cooking" artefact -- amendment A2 of the mandate dropped the
`cuisson.py --cuire` stage because nothing ever read its `bloc_*.npz`.

WHAT IS REUSED, VERBATIM, FROM THE J0 LANE (and therefore not re-proved here):
  * `cuisson.lire_geff` / `evenements_du_film` -- the ground-truth reader and
    the division/continuation split (a division is a node with EXACTLY two
    children; out-degree >= 3 raises).
  * `normalisation.trame_normalisee` -- reading, xy binning by 2 and division
    by the p99 OF THAT IMAGE. This is the mandate's "per-image normalised, NOT
    equalised": the mother's absolute brightness relative to her own frame is
    exactly what the autopsy measured (contrast rise at t-1, AUC 0,68 / 0,69),
    so it must survive normalisation.
  * `normalisation.DECALAGES_DEFAUT = (-2, -1, 0, +1)` -- the four input frames
    of amendment A1, edge-clamped at the film's bounds (never a black frame).
  * `grille.natif_vers_grille` / `natif_vers_um` -- the coordinate frames.

WHAT IS NEW HERE. The crop extractor, the negative classes, and the corpus
assembler. Nothing else.

CENTRING RULE, PUBLISHED BECAUSE THE MANDATE ASKS FOR IT. Every crop -- for a
positive as for a negative -- is centred on the candidate node's OWN voxel at
its OWN frame t, converted to grid coordinates and rounded. Positives are the
MOTHER at t (the last frame where she is one cell); the daughters live at t+1,
inside the +1 channel. No crop is ever centred on a daughter or on a midpoint:
at inference we only ever have the candidate, never her future.

STORED CROP vs FED CROP. The bank stores a MARGIN (2 extra planes in z, 4
extra voxels in xy on each side) so that jitter and z-shift augmentation are a
random sub-crop of a stored crop rather than a second read of the film. The
network is fed the inner (11, 40, 40); the bank holds (15, 48, 48).
"""

from __future__ import annotations

import collections
import hashlib
import json
import pathlib

import numpy as np

import cuisson as CU
import grille as G
import normalisation as N

# --------------------------------------------------------------- geometry

Z_FED, Y_FED, X_FED = 11, 40, 40
"""Fed crop, in GRID voxels: +-5 planes in z (+-8,125 um) and +-20 voxels in
xy (+-16,25 um). Chosen against the measured geometry of the 151: sister-sister
separation median 10,57 um, p90 14,36 um (`mitosis_geometry_151.csv`), so a
+-16,25 um window holds both daughters in p90 of true divisions."""

Z_MARGIN, XY_MARGIN = 2, 4
Z_BANK = Z_FED + 2 * Z_MARGIN
Y_BANK = Y_FED + 2 * XY_MARGIN
X_BANK = X_FED + 2 * XY_MARGIN

OFFSETS = N.DECALAGES_DEFAUT           # (-2, -1, 0, +1)
N_CHANNELS = len(OFFSETS)

BANK_SHAPE = (N_CHANNELS, Z_BANK, Y_BANK, X_BANK)
FED_SHAPE = (N_CHANNELS, Z_FED, Y_FED, X_FED)


class MitosisDataError(ValueError):
    """A named refusal of this module. Never a silent fallback."""


# ----------------------------------------------------------- film access

class FilmReader:
    """Frames of one film, binned and per-image normalised, memoised.

    The memoisation is the one `normalisation.verifier_memoisation` proves
    bit-identical: without augmentation a frame's normalisation depends on no
    other frame."""

    def __init__(self, zarr_dir, film):
        import zarr
        path = pathlib.Path(zarr_dir) / (film + ".zarr")
        if not path.exists():
            raise MitosisDataError("zarr absent: " + str(path))
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
    """The four frames actually read for a candidate at t, edge-clamped."""
    return [int(min(max(int(t) + d, 0), int(n_frames) - 1)) for d in OFFSETS]


def crop_from_film(reader, t, zyx_grid):
    """(4, Z_BANK, Y_BANK, X_BANK) float32 + a log.

    Out-of-volume is filled by EDGE REPLICATION (`np.pad` mode='edge'), never
    by zeros: a black border would teach the head that the volume's edge is
    dark."""
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
            raise MitosisDataError(
                "empty crop for %s t=%s at %s" % (reader.film, t, (z0, y0, x0)))
        if any(any(q) for q in pad):
            sub = np.pad(sub, pad, mode="edge")
            padded = True
        out[c] = sub
    clamped = [int(int(t) + d) for d in OFFSETS
               if not (0 <= int(t) + d < reader.n_frames)]
    return out, {"frames": frames, "p99": p99, "clamped": clamped,
                 "padded": bool(padded)}


# ------------------------------------------------------ ground truth pools

def read_truth(geff_dir, film):
    gt = CU.lire_geff(pathlib.Path(geff_dir) / (film + ".geff"))
    div, cont = CU.evenements_du_film(gt)
    return {"gt": gt, "divisions": div, "continuations": cont}


def grid_of(gt, node):
    _t, z, y, x = gt["pos"][int(node)]
    return G.natif_vers_grille(np.array([[z, y, x]], np.float64))[0]


def um_of(gt, node):
    _t, z, y, x = gt["pos"][int(node)]
    return G.natif_vers_um(np.array([[z, y, x]], np.float64))[0]


NEG_CLASSES = ("NEG_RANDOM", "NEG_CROWDED", "NEG_MOVING", "NEG_TERMINAL")


def candidates_of_film(geff_dir, film, rng, n_neg_per_class):
    """The labelled candidate list of ONE film. No image is read here.

    Negative classes (the mandate's negatives, minus the two that need a
    predicted world):
      NEG_RANDOM   -- a node with exactly one child.
      NEG_CROWDED  -- a non-dividing node whose nearest neighbour AT THE SAME
                      FRAME is under 6 um (two cells touching or crossing).
      NEG_MOVING   -- a non-dividing node whose step to its child is at or above
                      the film's p90 (the stretching look without the split).
      NEG_TERMINAL -- a node with NO child (a track ends: what a division looks
                      like to a linker that cannot see the daughters).
    Every class is drawn WITHOUT replacement and never contains a true mother."""
    tr = read_truth(geff_dir, film)
    gt, div, cont = tr["gt"], tr["divisions"], tr["continuations"]
    mothers = set(int(u) for u in div)
    all_ids = [int(i) for i in gt["ids"]]
    with_children = set(int(k) for k in gt["enfants"])
    terminal = [u for u in all_ids if u not in with_children]

    rows = []
    for u in sorted(mothers):
        rows.append({"film": film, "node": int(u), "t": int(gt["pos"][u][0]),
                     "label": 1, "klass": "POS_REAL",
                     "zyx_grid": [float(v) for v in grid_of(gt, u)]})

    by_frame = collections.defaultdict(list)
    for u in all_ids:
        by_frame[gt["pos"][u][0]].append(u)
    nearest = {}
    for t, ids in by_frame.items():
        if len(ids) < 2:
            for u in ids:
                nearest[u] = float("inf")
            continue
        pts = np.array([um_of(gt, u) for u in ids])
        d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
        np.fill_diagonal(d, np.inf)
        for u, v in zip(ids, d.min(axis=1)):
            nearest[u] = float(v)

    steps = {}
    for u in cont:
        c = gt["enfants"][u][0]
        steps[u] = float(np.linalg.norm(um_of(gt, c) - um_of(gt, u)))
    step_cut = (float(np.quantile(np.array(list(steps.values())), 0.90))
                if steps else float("inf"))

    # The crowded cut is a PER-FILM DECILE, not an absolute micron threshold.
    # Measured reason (throughput receipt, 2026-09-07T22:0xZ): with an absolute
    # 6 um cut the pool was EMPTY on both dense films -- the ground truth of
    # this competition holds 8 to 17 cells per frame, so "two cells touching"
    # is defined relative to the film's own crowding or it does not exist.
    finite_near = [v for v in nearest.values() if np.isfinite(v)]
    crowd_cut = (float(np.quantile(np.array(finite_near), 0.10))
                 if finite_near else float("inf"))

    pools = {
        "NEG_RANDOM": [u for u in cont if u not in mothers],
        "NEG_CROWDED": [u for u in cont
                        if u not in mothers and nearest.get(u, np.inf)
                        <= crowd_cut],
        "NEG_MOVING": [u for u in cont
                       if u not in mothers and steps.get(u, 0.0) >= step_cut],
        "NEG_TERMINAL": [u for u in terminal if u not in mothers],
    }
    taken = set()
    for klass in NEG_CLASSES:
        want = int(n_neg_per_class.get(klass, 0))
        pool = [u for u in pools.get(klass, []) if u not in taken]
        if not pool or want <= 0:
            continue
        take = min(want, len(pool))
        pick = rng.choice(np.array(sorted(pool), dtype=np.int64), size=take,
                          replace=False)
        for u in pick:
            u = int(u)
            taken.add(u)
            rows.append({"film": film, "node": u, "t": int(gt["pos"][u][0]),
                         "label": 0, "klass": klass,
                         "zyx_grid": [float(v) for v in grid_of(gt, u)]})
    stats = {"n_nodes": len(all_ids), "n_divisions": len(div),
             "n_continuations": len(cont), "n_terminal": len(terminal),
             "pool_sizes": dict((k, len(v)) for k, v in pools.items()),
             "step_p90_um": step_cut, "crowd_p10_um": crowd_cut}
    return rows, stats


def film_negative_classes(geff_dir, film):
    """Per-node hard-negative class membership for one film, plus the two cuts.

    A node can be crowded AND moving: this returns, for every node, the LIST of
    classes it belongs to, never one label. The corpus builder stores that list
    with each row, so the G1 duel needs no second pass over the ground truth."""
    tr = read_truth(geff_dir, film)
    gt, cont = tr["gt"], tr["continuations"]
    mothers = set(int(u) for u in tr["divisions"])
    all_ids = [int(i) for i in gt["ids"]]
    by_frame = collections.defaultdict(list)
    for u in all_ids:
        by_frame[gt["pos"][u][0]].append(u)
    nearest = {}
    for _t, ids in by_frame.items():
        if len(ids) < 2:
            for u in ids:
                nearest[u] = float("inf")
            continue
        pts = np.array([um_of(gt, u) for u in ids])
        d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
        np.fill_diagonal(d, np.inf)
        for u, v in zip(ids, d.min(axis=1)):
            nearest[u] = float(v)
    steps = {}
    for u in cont:
        c = gt["enfants"][u][0]
        steps[u] = float(np.linalg.norm(um_of(gt, c) - um_of(gt, u)))
    step_cut = (float(np.quantile(np.array(list(steps.values())), 0.90))
                if steps else float("inf"))
    finite_near = [v for v in nearest.values() if np.isfinite(v)]
    crowd_cut = (float(np.quantile(np.array(finite_near), 0.10))
                 if finite_near else float("inf"))
    with_children = set(int(k) for k in gt["enfants"])
    classes = {}
    for u in all_ids:
        if u in mothers:
            classes[u] = []
            continue
        cl = []
        if u in with_children:
            cl.append("NEG_RANDOM")
            if nearest.get(u, np.inf) <= crowd_cut:
                cl.append("NEG_CROWDED")
            if steps.get(u, 0.0) >= step_cut:
                cl.append("NEG_MOVING")
        else:
            cl.append("NEG_TERMINAL")
        classes[u] = cl
    return {"gt": gt, "mothers": mothers, "classes": classes,
            "nearest_um": nearest, "step_um": steps,
            "crowd_p10_um": crowd_cut, "step_p90_um": step_cut}


def all_nodes_of_film(geff_dir, film):
    """Every ground-truth node of a film as a scorable candidate (label from
    the truth). This is the SCHOOL population, not the deployable one."""
    tr = read_truth(geff_dir, film)
    gt = tr["gt"]
    mothers = set(int(u) for u in tr["divisions"])
    rows = []
    for u in [int(i) for i in gt["ids"]]:
        rows.append({"film": film, "node": u, "t": int(gt["pos"][u][0]),
                     "label": int(u in mothers),
                     "klass": "POS_REAL" if u in mothers else "ALL_NODE",
                     "zyx_grid": [float(v) for v in grid_of(gt, u)]})
    return rows


# ---------------------------------------------------------------- helpers

def digest(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]


def write_json(path, obj):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, indent=1, ensure_ascii=True, default=str)
    with open(str(p), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return hashlib.sha256((text + "\n").encode("utf-8")).hexdigest()[:16]
