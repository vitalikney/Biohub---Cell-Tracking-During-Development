#!/usr/bin/env python3
"""L4_HVETO -- the post-canon fork veto, SHIP FILE for ENG/KER11.

WHAT IT DOES. After the post-canon stages have written the final track graph of ONE film, every
node with out-degree exactly 2 is a proposed division. For each of them this cell cuts a box of
about 15 judge-micrometres over t-2..t+2, builds instance masks from OUR OWN detections inside that
box, asks HOCT (royerlab, arXiv 2607.11754, MIT) for its parental softmax on both legs, and DELETES
the lower-scoring leg when `min(sim_a, sim_b) < TAU`. Nodes are never touched. Nothing else moves.

WHY IT IS HONEST BY CONSTRUCTION. `ctc_v0` is trained on the 16 Cell Tracking Challenge datasets,
zero zebrafish, and has never seen one frame of this competition -- neither the train films nor the
hidden ones. Its opinion is out-of-sample on BOTH sides of our split, which is the one property our
own boosters cannot have.

INTERFACE (KV12's).
    input   the post-canon world of one film as submission rows, plus the film's image zarr
    output  the list of (source_id, target_id) edge rows to DELETE
    ids     integer (t, z, y, x) on the world's own lattice; the join is BY POSITION, never by id
    env     BIOCEL_HVETO        "1" ship / "0" inert (byte-identical passthrough, asserted)
            BIOCEL_HVETO_TAU    default "0.02"   drop when min(sim_a, sim_b) < TAU
            BIOCEL_HVETO_SMAX   default "0.80"   ... AND max(sim_a, sim_b) < SMAX (the guard)
            BIOCEL_HVETO_MAX_FORKS  default "35"   deterministic order, ascending mother node_id
            BIOCEL_HVETO_BUDGET_S   default "20"   per-film wall; forks not reached are KEPT
            BIOCEL_HVETO_WEIGHTS    path to ctc_v0.pt in the aux dataset
    weights ctc_v0.pt  sha256 b9be3d976e2d51ae946128ded99142a81b5ba99fb87a0da67c38de2934944000
            25 505 802 bytes. Verified at load. No download, ever.
    vendor  `hoct_vendor/` in the aux dataset, put at the FRONT of sys.path at import (see the
            bootstrap below). NO pip at run time. `BIOCEL_HVETO_VENDOR` overrides the search.

GT-FREE, AND IT PROVES IT AT IMPORT. The guard below refuses to open anything that smells of the
annotation or of the scorer, and it checks its own body for the imports that could reach them.
Same shape as MITO2's ship guard.

DETERMINISM. The forks are taken in ascending `node_id`; the cap and the wall therefore cut the
same set on every run. `torch` runs in inference mode on a single stream; the ILP is never called
(`solve_tracking` is replaced by a no-op inside `hoct.inference._predict`, exactly as the research
path does), which is why a fork costs 0,27 s and not 40.
"""
from __future__ import annotations

# ======================================================================================
# THE VENDOR BOOTSTRAP -- FIRST, and deliberately BEFORE the GT guard.
# ======================================================================================
# `hoct` and `tracksdata` are in no Kaggle image and the kernel has no internet, so the aux dataset
# carries a flat `hoct_vendor/` directory (pip --target, no pip at run time). It goes at the FRONT
# of sys.path because seven of its packages must SHADOW older copies in the base image --
# `typing_extensions` above all, where the image's 4.9.0 lacks `Sentinel` and tracksdata dies on it.
#
# WHY BEFORE THE GUARD, and it was measured, not assumed: a dataset built from a folder is uploaded
# as ONE archive and Kaggle's expansion is not guaranteed, so this has to be able to unpack
# `hoct_vendor.zip` itself -- and `tracksdata` ships a `metrics.py`, which is one of the guard's
# forbidden tokens. With the guard installed first the unpack raised PermissionError on its own
# dependency and the bootstrap silently found nothing (proved on a pod, 2026-09-12T17:35Z).
# Unpacking the archive the aux dataset ships is not reading ground truth; everything after this
# block runs under the guard.
import os
import sys


def _find_vendor():
    import glob
    cands = [os.environ.get("BIOCEL_HVETO_VENDOR", "")]
    cands += sorted(glob.glob("/kaggle/input/*/hoct_vendor"))
    cands += [os.path.join(os.path.dirname(os.path.abspath(__file__)), "hoct_vendor")]
    for c in cands:
        if c and os.path.isdir(c):
            return c, "directory"
    # `.zip.bin` is the SAME zip under a name Kaggle will not try to expand: a dataset of one
    # opaque file is ingested in minutes where 12 979 expanded files took over an hour.
    zips = sorted(glob.glob("/kaggle/input/*/hoct_vendor.zip"))
    zips += sorted(glob.glob("/kaggle/input/*/hoct_vendor.zip.bin"))
    here = os.path.dirname(os.path.abspath(__file__))
    zips += sorted(glob.glob(os.path.join(here, "hoct_vendor.zip")))
    zips += sorted(glob.glob(os.path.join(here, "hoct_vendor.zip.bin")))
    for z in zips:
        import zipfile
        dest = os.environ.get("BIOCEL_HVETO_UNZIP_TO", "/kaggle/working/_hveto_vendor")
        os.makedirs(dest, exist_ok=True)
        d = os.path.join(dest, "hoct_vendor")
        if not os.path.isdir(os.path.join(d, "hoct")):
            with zipfile.ZipFile(z) as zf:
                zf.extractall(dest)
        if os.path.isdir(d):
            return d, "unpacked from " + z
    return "", "NOT FOUND"


VENDOR_DIR, VENDOR_HOW = _find_vendor()
if VENDOR_DIR and VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)

# ======================================================================================
# THE GT GUARD -- this module cannot read ground truth, and proves it at import.
# ======================================================================================
import builtins as _bi
import pathlib as _pl

_FORBIDDEN = (".geff", "vecteurs_gt", "/juge", "juge.py", "division_metrics", "scorer_bundle",
              "tracking_cellmot", "metrics.py")
_REAL_OPEN = _bi.open

# THE GUARD IS SCOPED, NOT TOKEN-ONLY -- and this is a defect that cost two Kaggle runs.
# A substring blacklist is a property of the NAME, and names repeat: `scikit-image` ships
# `skimage/metrics/set_metrics.py`, which matches `metrics.py` exactly. The admission ticket walks
# the 12 979 vendor files to re-hash them and died on that file at t = 18,8 s (KER10, version 32,
# `recus/HVETO_TICKET_V32_RAISED.json`). The vendor directory is code WE shipped in the aux dataset;
# it can never be ground truth, so it is admitted by SCOPE before the blacklist is consulted.
# Everything outside that scope is still judged by the blacklist, and the self-test below proves
# BOTH directions at import -- the register's rule: a guard that only refuses has not been tested.
_VENDOR_SCOPE = ""
if VENDOR_DIR:
    _VENDOR_SCOPE = os.path.abspath(VENDOR_DIR).replace("\\", "/").rstrip("/") + "/"


def _in_vendor(p):
    if not _VENDOR_SCOPE:
        return False
    q = os.path.abspath(str(p)).replace("\\", "/")
    return q.startswith(_VENDOR_SCOPE) or q == _VENDOR_SCOPE[:-1]


def _guarded_open(file, *a, **k):
    if _in_vendor(file):
        return _REAL_OPEN(file, *a, **k)
    _p = str(file).replace("\\", "/").lower()
    for _tok in _FORBIDDEN:
        if _tok in _p:
            raise PermissionError(
                "L4_HVETO GUARD: this cell is GT-free by construction and refused to open %r"
                % (file,))
    return _REAL_OPEN(file, *a, **k)


_bi.open = _guarded_open
_pl.Path.open = lambda self, *a, **k: _guarded_open(str(self), *a, **k)

# ---- THE TWO-DIRECTION SELF-TEST, at import, loud on failure ----------------------------
# (i) it must REFUSE a ground-truth path, and (ii) it must ADMIT a file inside the vendor whose
# name matches the blacklist. If either half is wrong the module refuses to load at all.
_SELFTEST = {"refuses_gt": None, "admits_vendor": None, "vendor_scope": _VENDOR_SCOPE}
try:
    _bi.open("/__l4_hveto_selftest__/does_not_exist.geff", "rb")
    _SELFTEST["refuses_gt"] = False
except PermissionError:
    _SELFTEST["refuses_gt"] = True
except Exception:
    _SELFTEST["refuses_gt"] = False
assert _SELFTEST["refuses_gt"], \
    "L4_HVETO GUARD SELF-TEST: the guard did not refuse a ground-truth path"

if _VENDOR_SCOPE:
    _probe = None
    for _r, _d, _f in os.walk(VENDOR_DIR):
        for _n in _f:
            if _n.endswith("metrics.py") or _n.endswith("metrics.pyi"):
                _probe = os.path.join(_r, _n)
                break
        if _probe:
            break
    if _probe is None:                      # no blacklisted name in the tree: use any file
        for _r, _d, _f in os.walk(VENDOR_DIR):
            if _f:
                _probe = os.path.join(_r, _f[0])
                break
    try:
        with _bi.open(_probe, "rb") as _fh2:
            _fh2.read(16)
        _SELFTEST["admits_vendor"] = True
        _SELFTEST["probe"] = _probe
    except Exception as _e:
        _SELFTEST["admits_vendor"] = False
        _SELFTEST["probe_error"] = repr(_e)[:200]
    assert _SELFTEST["admits_vendor"], \
        ("L4_HVETO GUARD SELF-TEST: the guard refused a file INSIDE the vendor directory (%r). "
         "The scope rule is broken and the admission ticket cannot pass." % (_probe,))
else:
    _SELFTEST["admits_vendor"] = "no vendor directory resolved -- half of the self-test not run"

with _REAL_OPEN(__file__, "r", encoding="utf-8") as _fh:
    _SELF = _fh.read()
_BODY = _SELF.rsplit("# END OF GUARD", 1)[1]
for _tok in ("from_geff", "geff", "juge", "scorer", "vecteurs_gt", "division_metrics",
             "tracking_cellmot"):
    assert _tok not in _BODY, "L4_HVETO GUARD: forbidden token %r in the body" % _tok
# END OF GUARD
# ======================================================================================

import argparse
import hashlib
import json
import time

import numpy as np

VOXEL_UM = (1.625, 0.40625, 0.40625)     # judge micrometres per lattice step (z, y, x)
RADIUS_UM = 6.0                          # the mask's per-marker radius cap
SIGMA_UM = 0.8                           # the mask's smoothing
BOX_UM = 15.0                            # the fork-local graph box, half-width
MASK_MARGIN_UM = 8.0                     # extra margin so every marker keeps its 4-6 um shell
DT = 2                                   # t-2 .. t+2
WINDOW = 5                               # HOCT's sliding window, in consecutive frames
MAX_DISTANCE = 40.0                      # HOCT's candidate radius, in raw array units
N_NEIGHBORS = 5                          # HOCT's candidate count per node
WEIGHTS_SHA256 = "b9be3d976e2d51ae946128ded99142a81b5ba99fb87a0da67c38de2934944000"
WEIGHTS_BYTES = 25505802


def _env(name, default):
    return os.environ.get(name, default)


def sha256_of(path):
    h = hashlib.sha256()
    with _REAL_OPEN(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------- the masks
def build_labels(img, markers_zyx, vox=VOXEL_UM):
    """Instance masks from OUR OWN detections, on an arbitrary sub-volume.

    Marker-controlled watershed with a threshold LOCAL to each detection (the mean of the smoothed
    image on that detection's own 4-6 um Voronoi shell), and a hard per-label radius cap. A
    per-frame threshold would turn 27-35 pct of the deep detections into one-voxel labels because
    the sheet dims with depth; this rule takes that to 1,4-3,6 pct.
    """
    from scipy import ndimage as ndi
    from skimage.segmentation import watershed

    img = img.astype(np.float32)
    shape = img.shape
    n = len(markers_zyx)
    marker = np.zeros(shape, dtype=np.int32)
    if n:
        marker[markers_zyx[:, 0], markers_zyx[:, 1], markers_zyx[:, 2]] = \
            np.arange(1, n + 1, dtype=np.int32)
    sig = tuple(SIGMA_UM / np.asarray(vox))
    sm = ndi.gaussian_filter(img, sigma=sig, mode="nearest")
    edt, inds = ndi.distance_transform_edt(marker == 0, sampling=vox, return_indices=True)
    within = edt <= RADIUS_UM
    nearest = marker[inds[0], inds[1], inds[2]]
    if not n:
        return np.zeros(shape, np.uint16)
    peak_i = sm[markers_zyx[:, 0], markers_zyx[:, 1], markers_zyx[:, 2]].astype(np.float64)
    shell = within & (edt > 4.0)
    bg = float(np.median(sm[shell])) if shell.any() else 0.0
    ssum = np.bincount(nearest[shell], weights=sm[shell], minlength=n + 1)
    scnt = np.bincount(nearest[shell], minlength=n + 1).astype(np.float64)
    bg_i = np.where(scnt > 0, ssum / np.maximum(scnt, 1), bg)[1:]
    thr_i = 0.5 * (peak_i + bg_i)
    thr_map = np.zeros(n + 1, dtype=np.float32)
    thr_map[1:] = thr_i
    fg = within & (sm >= thr_map[nearest])
    fg |= marker > 0
    lab = watershed(-sm, markers=marker, mask=fg).astype(np.uint16)
    sel = lab > 0
    if sel.any():
        vz, vy, vx = np.nonzero(sel)
        own = lab[vz, vy, vx].astype(np.int64) - 1
        d2 = (((vz - markers_zyx[own, 0]) * vox[0]) ** 2
              + ((vy - markers_zyx[own, 1]) * vox[1]) ** 2
              + ((vx - markers_zyx[own, 2]) * vox[2]) ** 2)
        far = d2 > RADIUS_UM ** 2
        lab[vz[far], vy[far], vx[far]] = 0
    lab[markers_zyx[:, 0], markers_zyx[:, 1], markers_zyx[:, 2]] = \
        np.arange(1, n + 1, dtype=np.uint16)
    return lab


# ---------------------------------------------------------------------------- the cell
class L4Hveto:
    def __init__(self, weights=None, device="cuda", box_um=BOX_UM,
                 mask_margin_um=MASK_MARGIN_UM, verify_sha=True):
        import torch
        weights = weights or _env("BIOCEL_HVETO_WEIGHTS", "/kaggle/input/hoct-ctc-v0/ctc_v0.pt")
        size = os.path.getsize(weights)
        assert size == WEIGHTS_BYTES, ("L4_HVETO: wrong checkpoint size", size, WEIGHTS_BYTES)
        if verify_sha:
            got = sha256_of(weights)
            assert got == WEIGHTS_SHA256, ("L4_HVETO: wrong checkpoint sha256", got)
        self.weights = weights
        self.box_um = box_um
        self.mask_margin_um = mask_margin_um
        self.device = device if torch.cuda.is_available() else "cpu"
        self.model = torch.jit.load(weights, map_location=self.device).to(self.device)
        self.model.eval()

    # ---- the world, as rows -------------------------------------------------
    @staticmethod
    def parse_world(lines):
        """lines: the film's rows of a submission CSV, header first. Returns
        (pos[node_id] = (t,z,y,x), by_t[t] = (ids, zyx), children[source] = [targets])."""
        import collections
        head = lines[0].split(",")
        ic = dict((c, i) for i, c in enumerate(head))
        pos, byt, kids = {}, collections.defaultdict(list), collections.defaultdict(list)
        for ln in lines[1:]:
            q = ln.split(",")
            if q[ic["row_type"]] == "node":
                nid = int(q[ic["node_id"]])
                t = int(q[ic["t"]])
                p = (t, int(q[ic["z"]]), int(q[ic["y"]]), int(q[ic["x"]]))
                pos[nid] = p
                byt[t].append((nid, p[1], p[2], p[3]))
            elif q[ic["row_type"]] == "edge":
                kids[int(q[ic["source_id"]])].append(int(q[ic["target_id"]]))
        byt = dict((t, (np.asarray([r[0] for r in v], np.int64),
                        np.asarray([[r[1], r[2], r[3]] for r in v], np.int64)))
                   for t, v in byt.items())
        return pos, byt, kids

    # ---- one fork -----------------------------------------------------------
    def score_fork(self, img, pos, byt, mother, d1, d2):
        import dask.array as da
        import tracksdata as td
        import hoct.inference._predict as _pred
        from hoct._api import _create_dataset
        from hoct.features import create_graph
        from hoct.inference import model_predict
        from hoct.tracking import ILPSolverConfig

        P = np.asarray([pos[mother], pos[d1], pos[d2]], dtype=np.int64)
        tm = int(P[0, 0])
        T = img.shape[0]
        t_lo, t_hi = max(0, tm - DT), min(T - 1, tm + DT)
        vox = np.asarray(VOXEL_UM)
        rad_g = np.ceil(self.box_um / vox).astype(int)
        rad_m = np.ceil((self.box_um + self.mask_margin_um) / vox).astype(int)
        shp = np.asarray(img.shape[1:], dtype=np.int64)
        lo_g = np.maximum(P[:, 1:].min(0) - rad_g, 0)
        hi_g = np.minimum(P[:, 1:].max(0) + rad_g, shp - 1)
        lo_m = np.maximum(P[:, 1:].min(0) - rad_m, 0)
        hi_m = np.minimum(P[:, 1:].max(0) + rad_m, shp - 1)

        frames, labs, maps = [], [], []
        for t in range(t_lo, t_hi + 1):
            sub = np.asarray(img[t, lo_m[0]:hi_m[0] + 1, lo_m[1]:hi_m[1] + 1,
                                 lo_m[2]:hi_m[2] + 1])
            nid, zyx = byt.get(t, (np.zeros(0, np.int64), np.zeros((0, 3), np.int64)))
            inm = np.ones(len(zyx), bool)
            for k in range(3):
                inm &= (zyx[:, k] >= lo_m[k]) & (zyx[:, k] <= hi_m[k])
            mk = zyx[inm] - lo_m
            ids = nid[inm]
            lab = build_labels(sub, mk, vox)
            ing = np.ones(len(ids), bool)
            for k in range(3):
                ing &= (zyx[inm][:, k] >= lo_g[k]) & (zyx[inm][:, k] <= hi_g[k])
            dropl = np.nonzero(~ing)[0] + 1
            if len(dropl):
                lab[np.isin(lab, dropl)] = 0
            frames.append(sub)
            labs.append(lab)
            maps.append((t, ids, mk))

        images = da.from_array(np.stack(frames), chunks=(1,) + frames[0].shape)
        labels = da.from_array(np.stack(labs), chunks=(1,) + labs[0].shape)
        graph = create_graph(labels=labels, images=images, distance_threshold=MAX_DISTANCE,
                             n_neighbors=N_NEIGHBORS, delta_t=1, scale=None)

        na = graph.node_attrs(attr_keys=[td.DEFAULT_ATTR_KEYS.NODE_ID,
                                         td.DEFAULT_ATTR_KEYS.T, "z", "y", "x"])
        gid = np.asarray(na[td.DEFAULT_ATTR_KEYS.NODE_ID].to_list(), dtype=np.int64)
        gt_ = np.asarray(na[td.DEFAULT_ATTR_KEYS.T].to_list(), dtype=np.int64)
        gzyx = np.column_stack([np.asarray(na["z"].to_list(), float),
                                np.asarray(na["y"].to_list(), float),
                                np.asarray(na["x"].to_list(), float)])
        world2h = {}
        for fi, (t, ids, mk) in enumerate(maps):
            sel = np.nonzero(gt_ == fi)[0]
            if not len(sel) or not len(ids):
                continue
            for j, cid in enumerate(ids):
                d = np.linalg.norm((gzyx[sel] - mk[j]) * vox, axis=1)
                k = int(np.argmin(d))
                if d[k] <= 4.0:
                    world2h[int(cid)] = int(gid[sel[k]])

        have = set()
        ea = graph.edge_attrs(attr_keys=[])
        for a, b in zip(ea[td.DEFAULT_ATTR_KEYS.EDGE_SOURCE].to_list(),
                        ea[td.DEFAULT_ATTR_KEYS.EDGE_TARGET].to_list()):
            have.add((int(a), int(b)))
        hu = world2h.get(mother)
        legs = []
        for v in (d1, d2):
            hv = world2h.get(v)
            if hu is None or hv is None:
                legs.append((v, None, None))
                continue
            inp = (hu, hv) in have
            if not inp:
                graph.add_edge(hu, hv, attrs={"delta_t": 1.0, "distance": 0.0})
            legs.append((v, hv, inp))

        _real = _pred.solve_tracking
        _pred.solve_tracking = lambda **kw: None
        try:
            ds = _create_dataset(graph, None, WINDOW, 0)
            model_predict(self.model, ds, solver_config=ILPSolverConfig.default(),
                          return_solution=False)
        finally:
            _pred.solve_tracking = _real

        sim = {}
        sea = graph.edge_attrs(attr_keys=["similarity"])
        for a, b, s in zip(sea[td.DEFAULT_ATTR_KEYS.EDGE_SOURCE].to_list(),
                           sea[td.DEFAULT_ATTR_KEYS.EDGE_TARGET].to_list(),
                           sea["similarity"].to_list()):
            sim[(int(a), int(b))] = float(s)
        out = {"mother": int(mother), "t": tm, "graph_nodes": int(graph.num_nodes())}
        for name, (v, hv, inp) in zip(("a", "b"), legs):
            out["leg_" + name] = int(v)
            out["sim_" + name] = (sim.get((hu, hv), float("nan"))
                                  if (hu is not None and hv is not None) else None)
            out["in_pool_" + name] = inp
        sa, sb = out["sim_a"], out["sim_b"]
        out["sim_min"] = min(sa, sb) if (sa is not None and sb is not None) else None
        return out

    # ---- one film -----------------------------------------------------------
    def drops_for_film(self, lines, image_zarr_path, tau=None, smax=None, max_forks=None,
                       budget_s=None, trace=None):
        """THE ENTRY POINT KER11 CALLS. `lines` = the film's submission rows, header first.
        Returns the list of (source_id, target_id) to DELETE."""
        import zarr
        tau = float(_env("BIOCEL_HVETO_TAU", "0.02")) if tau is None else float(tau)
        smax = float(_env("BIOCEL_HVETO_SMAX", "0.80")) if smax is None else float(smax)
        max_forks = int(_env("BIOCEL_HVETO_MAX_FORKS", "35")) if max_forks is None else int(max_forks)
        budget_s = float(_env("BIOCEL_HVETO_BUDGET_S", "20")) if budget_s is None else float(budget_s)
        t0 = time.time()
        pos, byt, kids = self.parse_world(lines)
        forks = sorted((u, sorted(v)[0], sorted(v)[1]) for u, v in kids.items() if len(v) == 2)
        n_forks = len(forks)
        img = zarr.open(image_zarr_path, mode="r")
        drops, scored, skipped_budget, unmappable, guarded = [], 0, 0, 0, 0
        for (u, d1, d2) in forks[:max_forks]:
            if time.time() - t0 > budget_s:
                skipped_budget = n_forks - scored
                break
            r = self.score_fork(img, pos, byt, u, d1, d2)
            scored += 1
            if trace is not None:
                trace.append(r)
            if r["sim_min"] is None:
                unmappable += 1
                continue                                  # UNKNOWN is not false: KEEP
            # THE GUARD. A fork whose KEPT leg HOCT is very sure about (sim_max >= SMAX) while it
            # doubts the other is the signature of a REAL division with a long second leg -- the
            # ledger's P1 population -- not of a false fork. Measured on the 199-film plate: the
            # guard at 0,80 saves BOTH true divisions the ungated rule destroys and gives up two
            # false ones, taking the removed evaluable set from 9 fp / 2 tp to 7 fp / 0 tp.
            if r["sim_min"] < tau and max(r["sim_a"], r["sim_b"]) < smax:
                weak = r["leg_a"] if r["sim_a"] <= r["sim_b"] else r["leg_b"]
                drops.append((int(u), int(weak)))
            elif r["sim_min"] < tau:
                guarded += 1
        secs = time.time() - t0
        self.last = dict(forks=n_forks, scored=scored, capped=max(0, n_forks - max_forks),
                         skipped_budget=skipped_budget, unmappable=unmappable,
                         guarded=guarded,
                         dropped=len(drops), seconds=round(secs, 3), tau=tau, smax=smax,
                         max_forks=max_forks, budget_s=budget_s, device=self.device)
        return drops


def apply_drops(lines, drops):
    """Delete those edge rows and renumber the leading counter, exactly as the exporter writes it.
    The node rows are copied byte for byte and the count is asserted."""
    head = lines[0]
    ic = dict((c, i) for i, c in enumerate(head.split(",")))
    dset = set((int(a), int(b)) for a, b in drops)
    nin = nout = 0
    out = [head]
    i = 0
    for ln in lines[1:]:
        q = ln.split(",")
        if q[ic["row_type"]] == "node":
            nin += 1
        if q[ic["row_type"]] == "edge" and (int(q[ic["source_id"]]),
                                            int(q[ic["target_id"]])) in dset:
            continue
        if q[ic["row_type"]] == "node":
            nout += 1
        q[ic["id"]] = str(i)
        i += 1
        out.append(",".join(q))
    assert nin == nout, ("L4_HVETO: NODE BAND IS NOT ZERO", nin, nout)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", required=True, help="one film's CSV (header + rows)")
    ap.add_argument("--film", required=True)
    ap.add_argument("--images", default="/workspace/data_raw/competition/train")
    ap.add_argument("--weights", default=None)
    ap.add_argument("--out-world", default="")
    ap.add_argument("--out-drops", required=True)
    ap.add_argument("--tau", type=float, default=None)
    ap.add_argument("--smax", type=float, default=None)
    ap.add_argument("--max-forks", type=int, default=None)
    ap.add_argument("--budget-s", type=float, default=None)
    ap.add_argument("--trace", default="")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()

    if _env("BIOCEL_HVETO", "1") != "1":
        lines = _REAL_OPEN(a.world).read().splitlines()
        if a.out_world:
            with _REAL_OPEN(a.out_world, "w", newline="\n") as fo:
                fo.write("\n".join(lines) + "\n")
            assert _REAL_OPEN(a.out_world).read().splitlines() == lines, \
                "L4_HVETO: inert mode must be byte-identical"
        _REAL_OPEN(a.out_drops, "w").write("[]")
        print("HVETO film=%s INERT" % a.film)
        return

    lines = _REAL_OPEN(a.world).read().splitlines()
    cell = L4Hveto(weights=a.weights, device=a.device)
    trace = [] if a.trace else None
    drops = cell.drops_for_film(lines, "%s/%s.zarr/0" % (a.images, a.film),
                                tau=a.tau, smax=a.smax, max_forks=a.max_forks,
                                budget_s=a.budget_s, trace=trace)
    _REAL_OPEN(a.out_drops, "w").write(json.dumps([[int(x), int(y)] for x, y in drops]))
    if a.trace:
        _REAL_OPEN(a.trace, "w").write(json.dumps(trace))
    if a.out_world:
        with _REAL_OPEN(a.out_world, "w", newline="\n") as fo:
            fo.write("\n".join(apply_drops(lines, drops)) + "\n")
    print("HVETO film=%s forks=%d scored=%d dropped=%d guarded=%d unmappable=%d capped=%d "
          "skipped_budget=%d seconds=%.3f tau=%s smax=%s device=%s"
          % (a.film, cell.last["forks"], cell.last["scored"], cell.last["dropped"],
             cell.last["guarded"], cell.last["unmappable"], cell.last["capped"],
             cell.last["skipped_budget"], cell.last["seconds"], cell.last["tau"],
             cell.last["smax"], cell.last["device"]), flush=True)


if __name__ == "__main__":
    main()
