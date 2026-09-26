#!/usr/bin/env python3
"""ENG/KV11 -- physics features for the division ranker, ONE FILM (ZEUS 01:2xZ + HADES 18).

THE ARCHITECTURAL DECISION THAT MAKES THIS AFFORDABLE, and it is the whole trick: every image
quantity lives on a NODE, never on a candidate. A film raises ~2 million candidate pairs; touching
the image once per pair is impossible. Touching it once per NODE is 50 000 reads, and every
pair-level feature -- sister similarity, synchronisation, the continuity alternative -- then reduces
to a dot product between two precomputed descriptors. So the full film can be SCORED, not just a
sample, which is exactly what the pre-registered metric requires.

The zarr is (T, 64, 256, 256) uint16, 8,4 MB a frame: a whole film is under a gigabyte and is held
in RAM. Patches are cut on the DECIMATED lattice (stride 1,4,4) so they are physically isotropic at
1,625 um -- a 7x7x7 patch is an 11,4 um cube, a nucleus and its collar.

FEATURE FAMILIES
  physics      integrated intensity around each node, conservation I(d1)+I(d2) vs I(m), symmetry
               |I1-I2|/(I1+I2), peak-over-integral compactness (newborn nuclei are small and bright)
  geometry     midpoint-to-mother after local motion correction, separation, |v1-v2|, anisotropy of
               the mother's own blob at t and at t-1 (the saddle appears, then was not there)
  history      track length and straightness before t, each daughter's own credible past
  linker       q(m->d1), q(m->d2), q(incumbent->d), the margins -- INVERTED or not, the model learns
               the sign; that is the point of using a learner rather than another hand-written rule
  HADES 18     sister similarity (the two daughters' volumes compared, reflection allowed, no free
               deformation), synchronisation (do their changes happen at the same instant), and the
               continuity alternative (does the image prefer the incumbent parent to the proposal --
               the champion's parent is a COMPETITOR, never the truth used to build the test)

Labels are the judge's own annotated divisions, joined by POSITION. A true family is a true family
whether or not the champion already links it.
"""
from __future__ import annotations

# ======================================================================================
# THE GT GUARD -- this module cannot read ground truth, and proves it at import.
# ======================================================================================
import builtins as _bi
import pathlib as _pl

_FORBIDDEN = (".geff", "vecteurs_gt", "/juge", "juge.py", "division_metrics", "scorer_bundle")
_REAL_OPEN = _bi.open


def _guarded_open(file, *a, **k):
    _p = str(file).replace("\\", "/").lower()
    for _tok in _FORBIDDEN:
        if _tok in _p:
            raise PermissionError(
                "MITO3 SHIP GUARD: this cell is GT-free by construction and refused to open %r"
                % (file,))
    return _REAL_OPEN(file, *a, **k)


_bi.open = _guarded_open
_pl.Path.open = lambda self, *a, **k: _guarded_open(str(self), *a, **k)

with _REAL_OPEN(__file__, "r", encoding="utf-8") as _fh:
    _SELF = _fh.read()
_BODY = _SELF.rsplit("# END OF GUARD", 1)[1]     # the guard never inspects itself
for _tok in ("tracksdata", "from_geff", "geff", "juge", "scorer", "vecteurs_gt"):
    assert _tok not in _BODY, \
        "MITO3 SHIP GUARD: forbidden token %r is present in the shipped source" % _tok
del _SELF, _BODY
# END OF GUARD

import argparse
import csv as _csv
import json
import time
from pathlib import Path

import os as _os
import numpy as np
IMGFREE = _os.environ.get('KV12_IMGFREE', '0') == '1'
FLOWFIRST = float(_os.environ.get('KV12_FLOWFIRST', '0') or 0)
IMGFREE_KEEP = set(['sep_um', 'mid_to_mother_um', 'opposed', 'leg_sym', 'leg1_um', 'leg2_um', 'past_len_mother', 'straight_mother', 'past_len_d1', 'past_len_d2', 'fut_len_d1', 'fut_len_d2', 'q_m_d1', 'q_m_d2', 'q_inc_d1', 'q_inc_d2', 'margin_d1', 'margin_d2', 'local_density', 'FLOW_residual_d1', 'FLOW_residual_d2', 'FLOW_residual_midpoint', 'FLOW_residual_incumbent_d1', 'FLOW_residual_incumbent_d2', 'FLOW_advantage_d1', 'FLOW_advantage_d2', 'FLOW_norm_at_mother', 'AXIS_cos_to_flow', 'AGE_mother', 'AGE_d1', 'AGE_d2', 'd1_is_theft', 'd2_is_theft', 'd1_is_orphan', 'd2_is_orphan', 'already_kept'])


DEC_UM = 1.625
SCALE = np.array([1.625, 0.40625, 0.40625], dtype=np.float64)
STEP = np.array([1, 4, 4], dtype=np.int64)          # full-res voxels per decimated unit
R = 3                                                # patch half-width in decimated units -> 7^3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--film", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--data-dir", default="/workspace/data_raw/competition/train")
    ap.add_argument("--probmat", default="")
    ap.add_argument("--sep-lo-um", type=float, default=4.0)      # SHIP
    ap.add_argument("--sep-hi-um", type=float, default=17.0)     # SHIP
    ap.add_argument("--gate-um", type=float, default=7.0)
    ap.add_argument("--bridge-um", type=float, default=15.0)
    ap.add_argument("--max-daughters", type=int, default=8)
    ap.add_argument("--n-hard", type=int, default=3000)
    ap.add_argument("--n-rand", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--score-model", default="",
                    help="score EVERY candidate with this booster and report the true families' "
                         "EXACT rank in the full distribution -- the pre-registered metric, which "
                         "a sample cannot give")
    ap.add_argument("--score-out", default="")
    ap.add_argument("--flow-cut", type=float, default=0.0)
    ap.add_argument("--top-k", type=int, default=1, help="SHIP: proposals kept per film")
    ap.add_argument("--reach-um", type=float, default=14.0,          # SHIP
                    help="MITO2: mother reach, mother node at t to the orphan/stolen start at t+1")
    ap.add_argument("--parent-past-max", type=int, default=99,
                    help="MITO2: max chain length of the stolen child's incumbent parent")
    ap.add_argument("--flow-gate", type=float, default=7.0,          # SHIP
                    help="MITO2: midpoint-to-flow residual gate on the pool (0 = none)")
    ap.add_argument("--dcrop-rad", type=int, default=9,
                    help="MITO2: (D) crop half-width in DECIMATED pixels (9 = 29,3 judge-um "
                         "half-width = about 1,5 nucleus diameters each side)")
    ap.add_argument("--no-image-tests", action="store_true")
    ap.add_argument("--with-d", action="store_true",
                    help="SHIP: test (D) is OFF by default -- AUC 0,517 and 55 pct of the runtime")
    ap.add_argument("--score-min", type=float, default=0.02,
                    help="SHIP: a proposal below this booster score is not made at all")
    ap.add_argument("--no-d", action="store_true", default=True,
                    help="MITO2: skip test (D) entirely -- measured worthless (AUC 0,517 on the "
                         "1,1,2,2 pattern) and it is the expensive half of the image work")
    ap.add_argument("--keep-all", action="store_true",
                    help="keep EVERY candidate's features (for scoring a held-out film in full)")
    a = ap.parse_args()
    t00 = time.time()

    # ------------------------------------------------------------------ the champion's world
    nid_l, t_l, zyx_l, edges = [], [], [], []
    with open(a.csv, newline="") as fh:
        for r in _csv.DictReader(fh):
            if r["dataset"] != a.film:
                continue
            if r["row_type"] == "node":
                nid_l.append(int(r["node_id"]))
                t_l.append(int(r["t"]))
                zyx_l.append((float(r["z"]), float(r["y"]), float(r["x"])))
            else:
                edges.append((int(r["source_id"]), int(r["target_id"])))
    nid = np.asarray(nid_l, np.int64)
    tt = np.asarray(t_l, np.int64)
    zyx = np.asarray(zyx_l, np.float64)
    n = len(nid)
    row_of = {int(v): i for i, v in enumerate(nid)}
    dec = zyx / STEP
    by_t = {}
    for i, t in enumerate(tt.tolist()):
        by_t.setdefault(int(t), []).append(i)
    kids, par = {}, {}
    for s, d in edges:
        if s in row_of and d in row_of:
            kids.setdefault(row_of[s], []).append(row_of[d])
            par.setdefault(row_of[d], []).append(row_of[s])

    # ------------------------------------------------------------------ the film, in RAM
    import zarr
    z = zarr.open(str(Path(a.data_dir) / (a.film + ".zarr")), mode="r")
    arr = z["0"] if "0" in z else z
    T, Z, Y, X = arr.shape[-4:]
    img = (np.zeros((T, 1, 1, 1), np.float32) if IMGFREE
           else np.asarray(arr[:]).astype(np.float32))
    frame_med = np.array([np.median(img[k]) for k in range(T)], dtype=np.float32)
    frame_std = np.array([img[k].std() for k in range(T)], dtype=np.float32) + 1e-6

    # ------------------------------------------------------------------ per-NODE image features
    # One pass. Every pair-level quantity later is arithmetic on these.
    P = 2 * R + 1
    npatch = P * P * P
    q = np.rint(dec).astype(np.int64)
    qz = np.clip(q[:, 0], R, Z // 1 - R - 1)
    qy = np.clip(q[:, 1], R, Y // 4 - R - 1)
    qx = np.clip(q[:, 2], R, X // 4 - R - 1)

    def patches_at(dt):
        """(n, P^3) decimated-lattice patches at each node's own frame + dt, z-scored per patch."""
        out = np.zeros((n, npatch), dtype=np.float32)
        ok = np.zeros(n, dtype=bool)
        if IMGFREE:
            return out, ok
        for t_, idx in by_t.items():
            k = t_ + dt
            if k < 0 or k >= T:
                continue
            F = img[k]
            ii = np.asarray(idx)
            for j in ii:
                zc, yc, xc = qz[j], qy[j], qx[j]
                sub = F[zc - R:zc + R + 1,
                        (yc - R) * 4:(yc + R) * 4 + 1:4,
                        (xc - R) * 4:(xc + R) * 4 + 1:4]
                if sub.shape != (P, P, P):
                    continue
                v = sub.reshape(-1)
                out[j] = v
                ok[j] = True
        return out, ok

    pat0, ok0 = patches_at(0)
    pat_m1, okm1 = patches_at(-1)
    pat_p1, okp1 = patches_at(+1)

    integ = pat0.sum(1)                                   # integrated intensity, the "volume"
    peak = pat0.max(1)
    compact = peak / (integ / npatch + 1e-6)              # bright and small -> large
    bg = frame_med[np.clip(tt, 0, T - 1)]
    integ_n = integ / (bg * npatch + 1e-6)                # normalised to its own frame
    aniso = np.zeros(n, dtype=np.float32)                 # two-lobe score: the saddle
    C = pat0.reshape(n, P, P, P)
    mid = C[:, R, :, :]
    aniso = (mid.max(1).max(1) - mid[:, R, R]) / (mid.max(1).max(1) + 1e-6)

    def zs(M, ok):
        v = M - M.mean(1, keepdims=True)
        nrm = np.linalg.norm(v, axis=1, keepdims=True) + 1e-6
        v = v / nrm
        v[~ok] = 0.0
        return v

    D0, Dm1, Dp1 = zs(pat0, ok0), zs(pat_m1, okm1), zs(pat_p1, okp1)
    Ddelta = Dp1 - D0                                     # how the volume CHANGES, per node
    nrm = np.linalg.norm(Ddelta, axis=1, keepdims=True) + 1e-6
    Ddelta = Ddelta / nrm
    # reflection through the patch centre, for the bounded-alignment similarity
    D0r = D0.reshape(n, P, P, P)[:, ::-1, ::-1, ::-1].reshape(n, -1).copy()

    print("[feat] %s nodes %d | film in RAM %.0f MB | node features %.1f s"
          % (a.film, n, img.nbytes / 1e6, time.time() - t00), flush=True)

    # ------------------------------------------------------------------ history, from the world
    def up(i):
        p = par.get(i)
        return p[0] if p and len(p) == 1 else None

    def dn(i):
        k = kids.get(i)
        return k[0] if k and len(k) == 1 else None

    past_len = np.zeros(n, np.float32)
    straight = np.zeros(n, np.float32)
    for i in range(n):
        cur, chain = i, [i]
        for _ in range(4):
            nx = up(cur)
            if nx is None:
                break
            cur = nx
            chain.append(cur)
        past_len[i] = len(chain) - 1
        if len(chain) >= 3:
            p0, p1, p2 = dec[chain[-1]], dec[chain[len(chain) // 2]], dec[chain[0]]
            tot = np.linalg.norm(p2 - p0) + 1e-6
            pathl = np.linalg.norm(p1 - p0) + np.linalg.norm(p2 - p1) + 1e-6
            straight[i] = tot / pathl
    fut_len = np.zeros(n, np.float32)
    for i in range(n):
        cur, c = i, 0
        for _ in range(3):
            nx = dn(cur)
            if nx is None:
                break
            cur = nx
            c += 1
        fut_len[i] = c

    # local motion, per frame: the median displacement of the confident continuations
    motion = {}
    for t_ in sorted(by_t):
        v = [dec[k] - dec[i] for i in by_t[t_] for k in (kids.get(i) or [])[:1]
             if len(kids.get(i) or []) == 1]
        motion[t_] = np.median(np.asarray(v), axis=0) if v else np.zeros(3)

    # ================================================================== BIOLOGICAL COHERENCE
    # Guillaume 01:3xZ: these are cells with known behaviour, and most look-alikes are biologically
    # incoherent with the tissue's own observed motion. Every quantity here is derived from the
    # CHAMPION's own tracks and the raw image -- no GT, so it is all usable at inference.
    #
    # LOCAL TISSUE FLOW: for each node, the median t->t+1 displacement of its k nearest confidently
    # tracked neighbours. A true mother->daughter edge RIDES this flow; a theft is a jump against it.
    from scipy.spatial import cKDTree as _KD
    flow = np.zeros((n, 3), np.float64)
    flow_ok = np.zeros(n, bool)
    K_NB, R_NB = 12, 25.0 / DEC_UM
    for t_, idx in by_t.items():
        ii = np.asarray(idx)
        mov, src = [], []
        for i_ in idx:
            kk = kids.get(i_) or []
            if len(kk) == 1:
                mov.append(dec[kk[0]] - dec[i_])
                src.append(i_)
        if len(src) < 3:
            continue
        tr = _KD(dec[np.asarray(src)])
        V = np.asarray(mov)
        dd, jj = tr.query(dec[ii], k=min(K_NB, len(src)), distance_upper_bound=R_NB)
        jj = np.atleast_2d(jj); dd = np.atleast_2d(dd)
        for r_, i_ in enumerate(ii):
            sel = jj[r_][np.isfinite(dd[r_])]
            sel = sel[sel < len(src)]
            if len(sel) >= 3:
                flow[i_] = np.median(V[sel], axis=0)
                flow_ok[i_] = True
    # the neighbourhood's principal motion axis, for the division-axis feature
    flow_dir = flow / (np.linalg.norm(flow, axis=1, keepdims=True) + 1e-9)

    # SIZE RANK within the frame: pre-division mothers are among the larger, newborns among smaller
    size_rank = np.zeros(n, np.float32)
    for t_, idx in by_t.items():
        ii = np.asarray(idx)
        v = integ[ii]
        size_rank[ii] = np.argsort(np.argsort(v)) / max(len(ii) - 1, 1)

    # APPEARANCE DISCONTINUITY against the champion-assigned past: a newborn is smaller and brighter
    # than the node it is linked from; a continuing cell matches it.
    disc_size = np.full(n, np.nan, np.float32)
    disc_bright = np.full(n, np.nan, np.float32)
    for d_, pp_ in par.items():
        if not pp_:
            continue
        p_ = pp_[0]
        disc_size[d_] = (integ[d_] - integ[p_]) / (integ[d_] + integ[p_] + 1e-6)
        disc_bright[d_] = (compact[d_] - compact[p_]) / (compact[d_] + compact[p_] + 1e-6)

    # LINEAGE AGE: frames since the last fork upstream, from the champion's own tracks
    age = np.zeros(n, np.float32)
    for i_ in range(n):
        cur, c_ = i_, 0
        for _ in range(30):
            pp_ = par.get(cur) or []
            if len(pp_) != 1:
                break
            if len(kids.get(pp_[0]) or []) >= 2:
                break
            cur = pp_[0]
            c_ += 1
        age[i_] = c_

    # ------------------------------------------------------------------ the linker's matrix
    qmat = {}
    alt = {}
    if a.probmat and Path(a.probmat).exists():
        Zm = np.load(a.probmat)
        if "pm_src" in Zm.files:
            co = Zm["pm_coords"]
            from scipy.spatial import cKDTree
            tol = a.bridge_um / DEC_UM
            inv, byt = {}, {}
            for r_ in range(len(co)):
                byt.setdefault(int(co[r_][0]), []).append(r_)
            for t_, rows_ in byt.items():
                idx = by_t.get(t_, [])
                if not idx:
                    continue
                tr = cKDTree(dec[np.asarray(idx)])
                Pp = np.asarray([[float(co[r_][1]), float(co[r_][2]), float(co[r_][3])]
                                 for r_ in rows_])
                dd, jj = tr.query(Pp, k=1)
                for r_, d_, j_ in zip(rows_, dd.tolist(), jj.tolist()):
                    if d_ <= tol:
                        inv[r_] = idx[j_]
            pr = Zm["pm_prob"].tolist()
            for k_, (s_, d_) in enumerate(zip(Zm["pm_src"].tolist(), Zm["pm_tgt"].tolist())):
                if s_ in inv and d_ in inv:
                    alt.setdefault(inv[s_], set()).add(inv[d_])
                    qmat[(inv[s_], inv[d_])] = float(pr[k_])

    # ================================================================== THE CANDIDATES (MITO2)
    # KV12 enumerates EVERY unordered pair of a mother's nearest successors -- millions per film.
    # MITO2 does not. The champion's linker is a ONE-TO-ONE two-pass Hungarian (ENG/LINK2), so it
    # CANNOT emit a fork: at a real division the mother keeps exactly one daughter and the other
    # daughter is, structurally,
    #     * a TRACK START at t+1 (in-degree 0)  -- an ORPHAN, or
    #     * a STOLEN child -- it carries the in-edge of another single-child track at t.
    # So the pool is  d2 in {orphans} U {stolen}  x  a mother at t that CONTINUES (out-degree 1),
    # with d1 = THE CHILD THE CHAMPION ALREADY GAVE HER. d1 is never free: the proposal is always
    # "add the second leg", never "re-draw both legs".
    indeg = np.zeros(n, np.int64); outdeg = np.zeros(n, np.int64)
    for i_, kk in kids.items(): outdeg[i_] = len(kk)
    for d_, pp_ in par.items(): indeg[d_] = len(pp_)
    inc_par = np.full(n, -1, np.int64)
    for d_, pp_ in par.items():
        if pp_: inc_par[d_] = pp_[0]
    chain_len = np.zeros(n, np.int64)
    for i_ in range(n):
        cur = i_
        for _ in range(6):
            p_ = inc_par[cur]
            if p_ < 0: break
            cur = int(p_); chain_len[i_] += 1
    _pu, _pc, _po, _pk = [], [], [], []
    for t0 in sorted(by_t):
        nxt = by_t.get(t0 + 1)
        if not nxt: continue
        srcn = by_t[t0]
        moth = [i_ for i_ in srcn if outdeg[i_] == 1]
        if not moth: continue
        cand2, kind2 = [], []
        for j_ in nxt:
            if indeg[j_] == 0:
                cand2.append(j_); kind2.append(0)                     # ORPHAN track start
            else:
                p_ = int(inc_par[j_])
                if outdeg[p_] == 1 and tt[p_] == t0 and chain_len[p_] <= a.parent_past_max:
                    cand2.append(j_); kind2.append(1)                 # STOLEN child
        if not cand2: continue
        M = dec[np.asarray(moth)]
        Dj = dec[np.asarray(cand2)]
        Dm = np.sqrt((((Dj[:, None, :] - M[None, :, :]) * DEC_UM) ** 2).sum(2))
        for r_, j_ in enumerate(cand2):
            for s_ in np.where(Dm[r_] <= a.reach_um)[0]:
                u_ = moth[int(s_)]
                d1_ = kids[u_][0]
                if d1_ == j_: continue
                _pu.append(u_); _pc.append(d1_); _po.append(j_); _pk.append(kind2[r_])
    _pu = np.asarray(_pu, np.int64); _pc = np.asarray(_pc, np.int64)
    _po = np.asarray(_po, np.int64); _pk = np.asarray(_pk, np.int8)
    if len(_pu):
        _sep = np.sqrt((((dec[_pc] - dec[_po]) * DEC_UM) ** 2).sum(1))
        _m = (_sep >= a.sep_lo_um) & (_sep <= a.sep_hi_um)
        U, C1, C2, KIND = _pu[_m], _pc[_m], _po[_m], _pk[_m]
    else:
        U = C1 = C2 = np.zeros(0, np.int64); KIND = np.zeros(0, np.int8)
    if a.flow_gate > 0 and len(U):
        _mid = 0.5 * (dec[C1] + dec[C2])
        _res = np.linalg.norm((_mid - dec[U] - flow[U]) * DEC_UM, axis=1)
        _g = _res <= a.flow_gate
        U, C1, C2, KIND = U[_g], C1[_g], C2[_g], KIND[_g]
    nc = len(U)
    _raised = len(_pu)
    print("[feat] MITO3-POOL : %d of %d raised pairs kept (%.1f pct) | orphan %d, stolen %d | %.1f s"
          % (nc, _raised, 100.0 * nc / max(_raised, 1), int((KIND == 0).sum()),
             int((KIND == 1).sum()), time.time() - t00), flush=True)
    # THE STRUCTURAL ASSERTION that replaces KV12's "the cut kept < 30 pct": this cell can
    # only ever propose "add the mother's SECOND leg", never re-draw a family. If d1 is not
    # already the mother's own child, the generator has been changed and the cell must stop.
    for _j in range(0, nc, max(1, nc // 512 or 1)):
        assert int(C1[_j]) in (kids.get(int(U[_j])) or []), "MITO3: d1 is not the mother's child"
    if nc == 0:
        raise SystemExit("[feat] no candidate on %s" % a.film)

    # ---------------------------------------------------------- NO GROUND TRUTH, BY DESIGN
    # This file is the SHIP path. It does not read, import or infer any ground truth: the
    # research file's whole label section was removed by `mito3_shipgen.py`, and the GT
    # GUARD at the top of this module makes reading one impossible even by accident.
    y = np.zeros(nc, np.int8)
    y3 = np.full(nc, -1, np.int8)
    divisions, want, GN, gk = [], set(), {}, {}
    _HAVE_GT = False

    # ------------------------------------------------------------------ pair features, vectorised
    # The matrix lookup is VECTORISED. A python dict.get per candidate cost 110 s of the first
    # film's 135 s -- on 975 506 candidates times four lookups it is four million dict probes for a
    # quantity that is a sorted-array search.
    if qmat:
        _k = np.fromiter((u_ * n + v_ for (u_, v_) in qmat.keys()), dtype=np.int64,
                         count=len(qmat))
        _v = np.fromiter(qmat.values(), dtype=np.float32, count=len(qmat))
        _o = np.argsort(_k)
        _k, _v = _k[_o], _v[_o]
    else:
        _k = np.zeros(0, np.int64); _v = np.zeros(0, np.float32)

    def qv(src, dst):
        if _k.size == 0:
            return np.full(len(src), np.nan, np.float32)
        key = np.asarray(src, np.int64) * n + np.asarray(dst, np.int64)
        pos = np.searchsorted(_k, key)
        pos = np.clip(pos, 0, len(_k) - 1)
        hit = _k[pos] == key
        out = np.full(len(key), np.nan, np.float32)
        out[hit] = _v[pos[hit]]
        return out

    inc_of = np.full(n, -1, np.int64)
    for _d, _p in par.items():
        if _p:
            inc_of[_d] = _p[0]
    inc1, inc2 = inc_of[C1], inc_of[C2]
    q_m1, q_m2 = qv(U, C1), qv(U, C2)
    q_i1 = np.where(inc1 >= 0, qv(np.maximum(inc1, 0), C1), np.nan).astype(np.float32)
    q_i2 = np.where(inc2 >= 0, qv(np.maximum(inc2, 0), C2), np.nan).astype(np.float32)

    sep = np.sqrt((((dec[C1] - dec[C2]) * DEC_UM) ** 2).sum(1))
    _mot = np.zeros((int(tt.max()) + 2, 3), np.float64)
    for _t, _v3 in motion.items():
        _mot[_t] = _v3
    mot = _mot[tt[U]]
    midp = 0.5 * (dec[C1] + dec[C2])
    mid_to_m = np.sqrt((((midp - dec[U] - mot) * DEC_UM) ** 2).sum(1))
    v1 = (dec[C1] - dec[U] - mot) * DEC_UM
    v2 = (dec[C2] - dec[U] - mot) * DEC_UM
    n1 = np.linalg.norm(v1, axis=1) + 1e-6
    n2 = np.linalg.norm(v2, axis=1) + 1e-6
    opposed = -(v1 * v2).sum(1) / (n1 * n2)            # +1 when they move apart back to back
    leg_sym = np.abs(n1 - n2) / (n1 + n2)

    # KV12: the tissue-flow cut moved AHEAD of the pair features and the GBM. KV11 measured it a
    # SPEED device and not an accuracy one (KV11_GBM.md 4bis: identical top-1e-3, top-1e-4 and
    # precision@2), so cutting here changes the clock and not the answer.
    if FLOWFIRST > 0:
        _res = np.linalg.norm((midp - dec[U] - flow[U]) * DEC_UM, axis=1)
        _k = _res <= FLOWFIRST
        U, C1, C2 = U[_k], C1[_k], C2[_k]
        inc1, inc2 = inc1[_k], inc2[_k]
        q_m1, q_m2, q_i1, q_i2 = q_m1[_k], q_m2[_k], q_i1[_k], q_i2[_k]
        sep, mot, midp, mid_to_m = sep[_k], mot[_k], midp[_k], mid_to_m[_k]
        v1, v2, n1, n2 = v1[_k], v2[_k], n1[_k], n2[_k]
        opposed, leg_sym = opposed[_k], leg_sym[_k]
        y = y[_k]
        nc = int(_k.sum())
        print("[feat] FLOW-CUT-FIRST %.2f um : %d of %d candidates kept (%.1f pct) | %.1f s"
              % (FLOWFIRST, nc, len(_k), 100.0 * nc / max(len(_k), 1), time.time() - t00), flush=True)
    I1, I2, Im = integ_n[C1], integ_n[C2], integ_n[U]
    cons = (I1 + I2) / (Im + 1e-6)
    isym = np.abs(I1 - I2) / (I1 + I2 + 1e-6)
    # HADES 18 -- the three visual families, each a dot product on precomputed descriptors
    def dot(A, ia, B, ib, chunk=200000):
        """sum(A[ia] * B[ib], axis=1) without ever materialising a (nc, 343) fancy index."""
        o = np.empty(len(ia), np.float32)
        for s_ in range(0, len(ia), chunk):
            e_ = min(s_ + chunk, len(ia))
            o[s_:e_] = np.einsum("ij,ij->i", A[ia[s_:e_]], B[ib[s_:e_]])
        return o

    _i1 = np.maximum(inc1, 0); _i2 = np.maximum(inc2, 0)
    if IMGFREE:
        _z = np.zeros(len(C1), np.float32)
        sis = sis_refl = sync = cont_m1 = cont_m2 = _z
        cont_i1 = cont_i2 = np.full(len(C1), np.nan, np.float32)
    else:
        sis = dot(D0, C1, D0, C2)
        sis_refl = np.maximum(sis, dot(D0, C1, D0r, C2))
        sync = dot(Ddelta, C1, Ddelta, C2)
        cont_m1 = dot(D0, C1, D0, U)
        cont_m2 = dot(D0, C2, D0, U)
        cont_i1 = np.where(inc1 >= 0, dot(D0, C1, D0, _i1), np.nan)
        cont_i2 = np.where(inc2 >= 0, dot(D0, C2, D0, _i2), np.nan)
    _cnt = np.zeros(int(tt.max()) + 2, np.float32)
    for _t, _idx in by_t.items():
        _cnt[_t] = len(_idx)
    dens = _cnt[tt[U]]
    # flow residuals: the proposed legs, and the INCUMBENT legs, against the local tissue motion
    fl = flow[U]
    res1 = np.linalg.norm((dec[C1] - dec[U] - fl) * DEC_UM, axis=1)
    res2 = np.linalg.norm((dec[C2] - dec[U] - fl) * DEC_UM, axis=1)
    res_mid = np.linalg.norm((midp - dec[U] - fl) * DEC_UM, axis=1)
    fi1 = np.where((inc1 >= 0)[:, None], flow[_i1], np.nan)
    fi2 = np.where((inc2 >= 0)[:, None], flow[_i2], np.nan)
    resi1 = np.linalg.norm((dec[C1] - dec[_i1] - fi1) * DEC_UM, axis=1)
    resi2 = np.linalg.norm((dec[C2] - dec[_i2] - fi2) * DEC_UM, axis=1)
    # the division axis against the local flow direction
    sepv = (dec[C1] - dec[C2])
    sepv = sepv / (np.linalg.norm(sepv, axis=1, keepdims=True) + 1e-9)
    axis_cos = np.abs((sepv * flow_dir[U]).sum(1))
    # "two ordinary cells": BOTH members are coherent continuations of their own pasts
    both_continuing = ((np.nan_to_num(np.abs(disc_size[C1]), nan=9) < 0.15) &
                       (np.nan_to_num(np.abs(disc_size[C2]), nan=9) < 0.15) &
                       (np.nan_to_num(resi1, nan=99) < 3.0) &
                       (np.nan_to_num(resi2, nan=99) < 3.0))

    # ================================================================== THE FIVE PHYSICAL TESTS
    # All GT-free, all computable on a hidden film. Judge micrometres everywhere: a decimated pixel
    # is 1,625 um in EVERY axis (the lattice is isotropic in the judge's metric); laterally that is
    # 4 full-resolution voxels, so lateral judge-um = physical/4.
    _P3 = P * P * P
    _G = np.stack(np.meshgrid(np.arange(P) - R, np.arange(P) - R, np.arange(P) - R,
                              indexing="ij"), -1).reshape(-1, 3).astype(np.float64)
    _shell = np.zeros((P, P, P), bool)
    _shell[0, :, :] = _shell[-1, :, :] = True
    _shell[:, 0, :] = _shell[:, -1, :] = True
    _shell[:, :, 0] = _shell[:, :, -1] = True
    _shell = _shell.reshape(-1)
    if IMGFREE or a.no_image_tests:
        blob_vol = np.zeros(n, np.float32); ring = np.zeros(n, np.float32)
        elong = np.zeros(n, np.float32); axis3 = np.zeros((n, 3), np.float64)
        elong_m1 = np.zeros(n, np.float32)
    else:
        _bgn = frame_med[np.clip(tt, 0, T - 1)].astype(np.float32)
        _thr = _bgn + 0.5 * (peak - _bgn)
        blob_vol = (pat0 > _thr[:, None]).sum(1).astype(np.float32)      # decimated voxels
        ring = (peak - np.median(pat0[:, _shell], axis=1)) / (frame_std[np.clip(tt, 0, T - 1)])
        def _axes(PAT):
            W = np.clip(PAT - _bgn[:, None], 0, None).astype(np.float64)
            Ws = W.sum(1) + 1e-9
            mu = (W @ _G) / Ws[:, None]
            MM = np.empty((len(W), 3, 3))
            for _i in range(3):
                for _j in range(_i, 3):
                    MM[:, _i, _j] = MM[:, _j, _i] = (W @ (_G[:, _i] * _G[:, _j])) / Ws \
                                                    - mu[:, _i] * mu[:, _j]
            ev, evec = np.linalg.eigh(MM)
            el = (ev[:, 2] + 1e-9) / (ev[:, 1] + 1e-9)
            return el.astype(np.float32), evec[:, :, 2]
        elong, axis3 = _axes(pat0)
        elong_m1, _ = _axes(pat_m1)

    # ---- (E) EMPTINESS AT t : back-project the new start to t along the local tissue flow and
    # read the image there. A nucleus under it at t = a cell the DETECTOR MISSED, not a birth.
    _pb = dec[C2] - flow[U]
    if IMGFREE or a.no_image_tests:
        E_contrast = np.zeros(nc, np.float32); E_ratio = np.zeros(nc, np.float32)
        E_peak_near = np.zeros(nc, np.float32)
    else:
        RB = 2
        _o = np.stack(np.meshgrid(np.arange(-RB, RB + 1), np.arange(-RB, RB + 1),
                                  np.arange(-RB, RB + 1), indexing="ij"), -1).reshape(-1, 3)
        _tb = np.clip(tt[U], 0, T - 1)
        _zc = np.clip(np.rint(_pb[:, 0]).astype(np.int64), RB, Z - RB - 1)
        _yc = np.clip(np.rint(_pb[:, 1]).astype(np.int64), RB, Y // 4 - RB - 1)
        _xc = np.clip(np.rint(_pb[:, 2]).astype(np.int64), RB, X // 4 - RB - 1)
        E_contrast = np.zeros(nc, np.float32)
        for _s in range(0, nc, 100000):
            _e = min(_s + 100000, nc)
            zz = _zc[_s:_e, None] + _o[None, :, 0]
            yy = (_yc[_s:_e, None] + _o[None, :, 1]) * 4
            xx = (_xc[_s:_e, None] + _o[None, :, 2]) * 4
            v = img[_tb[_s:_e, None], zz, yy, xx]
            E_contrast[_s:_e] = (v.max(1) - frame_med[_tb[_s:_e]]) / frame_std[_tb[_s:_e]]
        _own = (peak[C2] - frame_med[np.clip(tt[C2], 0, T - 1)]) / frame_std[np.clip(tt[C2], 0, T - 1)]
        E_ratio = (E_contrast / (_own + 1e-6)).astype(np.float32)
        E_peak_near = _own.astype(np.float32)
    # any DETECTION of the champion at t under the back-projected position (3 decimated voxels)
    from scipy.spatial import cKDTree as _KD2
    E_node_d = np.full(nc, 99.0, np.float32)
    for _t in sorted(by_t):
        _sel = np.where(tt[U] == _t)[0]
        if len(_sel) == 0 or not by_t.get(_t): continue
        _tr = _KD2(dec[np.asarray(by_t[_t])])
        _dd, _ = _tr.query(_pb[_sel], k=1)
        E_node_d[_sel] = (_dd * DEC_UM).astype(np.float32)
    E_node_hit = (E_node_d <= 3.0 * DEC_UM).astype(np.float32)

    # ---- (V) VOLUME BUDGET : the mother's blob at t against the sum of the two daughters' at t+1
    V_m, V_1, V_2 = blob_vol[U], blob_vol[C1], blob_vol[C2]
    V_ratio = (V_1 + V_2) / (V_m + 1e-6)
    V_absdiff = (V_1 + V_2) - V_m
    V_sym = np.abs(V_1 - V_2) / (V_1 + V_2 + 1e-6)

    # ---- (S) SYMMETRY about the mother
    _sv = dec[C1] - dec[C2]
    _sv = _sv / (np.linalg.norm(_sv, axis=1, keepdims=True) + 1e-9)
    S_axis_cos = np.abs((axis3[U] * _sv).sum(1)).astype(np.float32)
    S_elong_mother = elong[U]
    S_elong_change = (elong[U] - elong_m1[U]).astype(np.float32)
    S_peak_sym = (np.abs(peak[C1] - peak[C2]) / (peak[C1] + peak[C2] + 1e-6)).astype(np.float32)
    S_ring_mother = ring[U]; S_ring_d1 = ring[C1]; S_ring_d2 = ring[C2]
    S_mid_resid = np.linalg.norm((0.5 * (dec[C1] + dec[C2]) - dec[U] - flow[U]) * DEC_UM, axis=1)

    # ---- (C) MULTI-FRAME CONVERGENCE : do the two tracks, in the tissue frame, come from ONE point?
    _nxt1 = np.full(n, -1, np.int64)
    for _i, _k in kids.items():
        if len(_k) == 1: _nxt1[_i] = _k[0]
    def _traj(j0):
        """flow-compensated positions of the track starting at j0, over its own t .. t+2."""
        pos = [dec[j0].copy()]; cur = j0.copy(); acc = np.zeros((len(j0), 3))
        alive = np.ones(len(j0), bool)
        for _ in range(2):
            nx = np.where(alive, _nxt1[np.maximum(cur, 0)], -1)
            alive = alive & (nx >= 0)
            acc = acc + np.where(alive[:, None], flow[np.maximum(cur, 0)], 0.0)
            cur = np.where(alive, nx, cur)
            pos.append(np.where(alive[:, None], dec[np.maximum(cur, 0)] - acc, np.nan))
        return np.stack(pos, 1)                     # (nc, 3, 3)
    _T1 = _traj(C1); _T2 = _traj(C2)
    def _extrap(Tr):
        """linear fit on the available flow-compensated points, evaluated one frame EARLIER."""
        ok = ~np.isnan(Tr[:, :, 0])
        k = ok.sum(1)
        x = np.arange(Tr.shape[1], dtype=np.float64)[None, :]
        W = ok.astype(np.float64)
        sx = (W * x).sum(1); sxx = (W * x * x).sum(1); sw = W.sum(1)
        den = sw * sxx - sx * sx
        out = np.empty((len(Tr), 3)); slope = np.empty((len(Tr), 3))
        for _d in range(3):
            yv = np.nan_to_num(Tr[:, :, _d], nan=0.0)
            sy = (W * yv).sum(1); sxy = (W * x * yv).sum(1)
            b = np.where(den > 1e-9, (sw * sxy - sx * sy) / np.where(den > 1e-9, den, 1), 0.0)
            aa = np.where(sw > 0, (sy - b * sx) / np.maximum(sw, 1), 0.0)
            out[:, _d] = aa + b * (-1.0)
            slope[:, _d] = b
        return out, slope, k
    _X1, _V1s, _k1 = _extrap(_T1); _X2, _V2s, _k2 = _extrap(_T2)
    C_conv_dist = np.linalg.norm((_X1 - _X2) * DEC_UM, axis=1).astype(np.float32)
    C_to_mother = (0.5 * (np.linalg.norm((_X1 - dec[U]) * DEC_UM, axis=1)
                          + np.linalg.norm((_X2 - dec[U]) * DEC_UM, axis=1))).astype(np.float32)
    _sepk = np.linalg.norm((_T1 - _T2) * DEC_UM, axis=2)          # (nc, 3), nan where absent
    _ok2 = ~np.isnan(_sepk)
    _kk = _ok2.sum(1)
    _xg = np.arange(3, dtype=np.float64)[None, :]
    _Wg = _ok2.astype(np.float64)
    _syg = (_Wg * np.nan_to_num(_sepk)).sum(1); _sxg = (_Wg * _xg).sum(1)
    _sxxg = (_Wg * _xg * _xg).sum(1); _swg = _Wg.sum(1)
    _sxyg = (_Wg * _xg * np.nan_to_num(_sepk)).sum(1)
    _deng = _swg * _sxxg - _sxg * _sxg
    C_sep_slope = np.where(_deng > 1e-9, (_swg * _sxyg - _sxg * _syg)
                           / np.where(_deng > 1e-9, _deng, 1), 0.0).astype(np.float32)
    C_sep_mono = ((_kk < 2) | (np.nan_to_num(_sepk[:, 1], nan=-1) >= _sepk[:, 0])).astype(np.float32)
    C_minlen = np.minimum(_k1, _k2).astype(np.float32)
    C_speed_sym = (np.abs(np.linalg.norm(_V1s, axis=1) - np.linalg.norm(_V2s, axis=1))
                   / (np.linalg.norm(_V1s, axis=1) + np.linalg.norm(_V2s, axis=1) + 1e-6)
                   ).astype(np.float32)

    # ---- (D) ONE-TO-TWO : count the blobs in a centred wide crop over t-1, t, t+1, t+2.
    # A division reads 1,1,2,2 ; two independent cells read 2 at every frame ; a missed detection
    # reads 2 already at t. Deduplicated on the rounded midpoint so the image is read once per place.
    Dcnt = np.full((nc, 4), -1.0, np.float32)
    if not (IMGFREE or a.no_image_tests or (a.no_d and not a.with_d)) and nc:
        from scipy import ndimage as _nd
        RAD = a.dcrop_rad; ZR = 3
        _mid = 0.5 * (dec[C1] + dec[C2])
        key = np.stack([tt[U],
                        np.clip(np.rint(_mid[:, 0]).astype(np.int64), ZR, Z - ZR - 1),
                        np.clip(np.rint(_mid[:, 1]).astype(np.int64), RAD, Y // 4 - RAD - 1),
                        np.clip(np.rint(_mid[:, 2]).astype(np.int64), RAD, X // 4 - RAD - 1)], 1)
        uk, inv = np.unique(key, axis=0, return_inverse=True)
        W2 = 2 * RAD + 1
        _oz = np.arange(-ZR, ZR + 1); _oy = np.arange(-RAD, RAD + 1) * 4
        _ox = np.arange(-RAD, RAD + 1) * 4
        cnt_u = np.full((len(uk), 4), -1.0, np.float32)
        for _fi, _dt in enumerate((-1, 0, 1, 2)):
            _tf = uk[:, 0] + _dt
            good = np.where((_tf >= 0) & (_tf < T))[0]
            for _s in range(0, len(good), 20000):
                gi = good[_s:_s + 20000]
                zz = uk[gi, 1][:, None, None, None] + _oz[None, :, None, None]
                yy = uk[gi, 2][:, None, None, None] * 4 + _oy[None, None, :, None]
                xx = uk[gi, 3][:, None, None, None] * 4 + _ox[None, None, None, :]
                V = img[_tf[gi][:, None, None, None], zz, yy, xx]      # (m, 2ZR+1, W2, W2)
                MP = V.max(1)
                SM = _nd.uniform_filter(MP, size=(1, 3, 3), mode="nearest")
                MX = _nd.maximum_filter(SM, size=(1, 5, 5), mode="nearest")
                bgf = frame_med[_tf[gi]][:, None, None]
                mxv = SM.reshape(len(gi), -1).max(1)[:, None, None]
                thr = bgf + 0.35 * (mxv - bgf)
                cnt_u[gi, _fi] = ((SM >= MX - 1e-6) & (SM > thr)).reshape(len(gi), -1).sum(1)
        Dcnt = cnt_u[inv]
    D_pattern = ((Dcnt[:, 0] == 1) & (Dcnt[:, 1] == 1)
                 & (Dcnt[:, 2] >= 2) & (Dcnt[:, 3] >= 2)).astype(np.float32)
    D_gain = (Dcnt[:, 2] - Dcnt[:, 1]).astype(np.float32)

    # ---- ENG/MITO3 (ZEUS amendment 2): THE COLLISION COLUMNS. In reversed time a division is a
    # head-on merge: going BACK s frames from t+1 the pair's separation is |r - s*v| with
    # r the separation vector and v the FORWARD relative velocity, minimised at s* = (r.v)/|v|^2.
    # s* ~ +1 means they met at the MOTHER's frame t. b = |r x v|/|v| is the impact parameter.
    # NOTE, stated because it is a fact and not an omission: a RELATIVE velocity is invariant to
    # subtracting the same local flow from both daughters, so the "tissue frame" version of b, t*
    # and the radial fraction is the SAME NUMBER by construction; only p* moves, and there the
    # flow version measures worse (0,580 against 0,684). No flow twin is emitted.
    def _m3_fwd(rows, k):
        out = np.full((len(rows), k + 1, 3), np.nan)
        cur = np.asarray(rows, np.int64).copy(); alive = np.ones(len(rows), bool)
        out[:, 0, :] = dec[cur]
        for s_ in range(1, k + 1):
            nx = np.where(alive, _nxt1[np.maximum(cur, 0)], -1)
            alive = alive & (nx >= 0); cur = np.where(alive, nx, cur)
            out[alive, s_, :] = dec[cur[alive]]
        return out
    _R1 = _m3_fwd(C1, 2); _R2 = _m3_fwd(C2, 2)
    _MU = dec[U] * DEC_UM
    _pa = _R1[:, 0, :] * DEC_UM; _pb = _R2[:, 0, :] * DEC_UM
    _s3 = np.isfinite(_R1[:, 2, 0]) & np.isfinite(_R2[:, 2, 0])
    _s2 = np.isfinite(_R1[:, 1, 0]) & np.isfinite(_R2[:, 1, 0])
    _ua = np.where(_s3[:, None], (_R1[:, 2, :] - _R1[:, 0, :]) / 2.0,
                   _R1[:, 1, :] - _R1[:, 0, :]) * DEC_UM
    _ub = np.where(_s3[:, None], (_R2[:, 2, :] - _R2[:, 0, :]) / 2.0,
                   _R2[:, 1, :] - _R2[:, 0, :]) * DEC_UM
    _rv = _pb - _pa; _vv = _ub - _ua
    _nv2 = (_vv * _vv).sum(1); _nv = np.sqrt(_nv2); _nr = np.linalg.norm(_rv, axis=1)
    K_impact_b = (np.linalg.norm(np.cross(_rv, _vv), axis=1) / (_nv + 1e-9)).astype(np.float32)
    K_tstar = ((_rv * _vv).sum(1) / (_nv2 + 1e-9)).astype(np.float32)
    K_tstar_err = np.abs(K_tstar - 1.0).astype(np.float32)
    K_radial = ((_rv * _vv).sum(1) / (_nr * _nv + 1e-9)).astype(np.float32)
    _scl = np.clip(K_tstar, 0.0, 3.0)
    K_dmin = np.linalg.norm(_rv - _scl[:, None] * _vv, axis=1).astype(np.float32)
    _ps1 = _pa - K_tstar[:, None] * _ua; _ps2 = _pb - K_tstar[:, None] * _ub
    K_pstar_split = np.linalg.norm(_ps1 - _ps2, axis=1).astype(np.float32)
    K_pstar_to_mother = (0.5 * (np.linalg.norm(_ps1 - _MU, axis=1)
                                + np.linalg.norm(_ps2 - _MU, axis=1))).astype(np.float32)
    _SEPK3 = np.linalg.norm((_R1 - _R2) * DEC_UM, axis=2)
    K_sep_vel_t1_t3 = np.where(_s3, (_SEPK3[:, 2] - _SEPK3[:, 0]) / 2.0,
                               np.where(_s2, _SEPK3[:, 1] - _SEPK3[:, 0],
                                        np.nan)).astype(np.float32)
    K_vspan = np.where(_s3, 3.0, np.where(_s2, 2.0, 0.0)).astype(np.float32)

    F = {
        "K_impact_b": K_impact_b, "K_tstar": K_tstar, "K_tstar_err": K_tstar_err,
        "K_radial": K_radial, "K_dmin": K_dmin, "K_pstar_split": K_pstar_split,
        "K_pstar_to_mother": K_pstar_to_mother, "K_sep_vel_t1_t3": K_sep_vel_t1_t3,
        "K_vspan": K_vspan,
        "E_backproj_contrast": E_contrast, "E_contrast_ratio": E_ratio,
        "E_own_contrast": E_peak_near, "E_node_dist_t_um": E_node_d, "E_node_hit": E_node_hit,
        "V_mother": V_m, "V_d1": V_1, "V_d2": V_2, "V_ratio": V_ratio,
        "V_absdiff": V_absdiff, "V_sym": V_sym,
        "S_axis_cos": S_axis_cos, "S_elong_mother": S_elong_mother,
        "S_elong_change": S_elong_change, "S_peak_sym": S_peak_sym,
        "S_ring_mother": S_ring_mother, "S_ring_d1": S_ring_d1, "S_ring_d2": S_ring_d2,
        "S_mid_resid_um": S_mid_resid,
        "C_conv_dist_um": C_conv_dist, "C_to_mother_um": C_to_mother,
        "C_sep_slope": C_sep_slope, "C_sep_mono": C_sep_mono, "C_minlen": C_minlen,
        "C_speed_sym": C_speed_sym,
        "D_n_tm1": Dcnt[:, 0], "D_n_t": Dcnt[:, 1], "D_n_tp1": Dcnt[:, 2], "D_n_tp2": Dcnt[:, 3],
        "D_pattern_1122": D_pattern, "D_gain": D_gain,
        "MITO2_kind_stolen": KIND.astype(np.float32),
        "sep_um": sep, "mid_to_mother_um": mid_to_m, "opposed": opposed, "leg_sym": leg_sym,
        "leg1_um": n1, "leg2_um": n2,
        "I_conservation": cons, "I_symmetry": isym, "I_mother": Im, "I_d1": I1, "I_d2": I2,
        "compact_d1": compact[C1], "compact_d2": compact[C2], "compact_mother": compact[U],
        "aniso_mother_t": aniso[U], "aniso_d1": aniso[C1], "aniso_d2": aniso[C2],
        "past_len_mother": past_len[U], "straight_mother": straight[U],
        "past_len_d1": past_len[C1], "past_len_d2": past_len[C2],
        "fut_len_d1": fut_len[C1], "fut_len_d2": fut_len[C2],
        "q_m_d1": q_m1, "q_m_d2": q_m2, "q_inc_d1": q_i1, "q_inc_d2": q_i2,
        "margin_d1": q_m1 - q_i1, "margin_d2": q_m2 - q_i2,
        "SISTER_similarity": sis, "SISTER_similarity_reflected": sis_refl,
        "SYNCHRONISATION": sync,
        "CONTINUITY_mother_d1": cont_m1, "CONTINUITY_mother_d2": cont_m2,
        "CONTINUITY_incumbent_d1": cont_i1, "CONTINUITY_incumbent_d2": cont_i2,
        "CONTINUITY_advantage": np.fmin(cont_m1 - cont_i1, cont_m2 - cont_i2),
        "local_density": dens,
        "FLOW_residual_d1": res1, "FLOW_residual_d2": res2, "FLOW_residual_midpoint": res_mid,
        "FLOW_residual_incumbent_d1": resi1, "FLOW_residual_incumbent_d2": resi2,
        "FLOW_advantage_d1": resi1 - res1, "FLOW_advantage_d2": resi2 - res2,
        "FLOW_norm_at_mother": np.linalg.norm(fl * DEC_UM, axis=1),
        "AXIS_cos_to_flow": axis_cos,
        "SIZE_rank_mother": size_rank[U], "SIZE_rank_d1": size_rank[C1],
        "SIZE_rank_d2": size_rank[C2],
        "DISC_size_d1": disc_size[C1], "DISC_size_d2": disc_size[C2],
        "DISC_bright_d1": disc_bright[C1], "DISC_bright_d2": disc_bright[C2],
        "AGE_mother": age[U], "AGE_d1": age[C1], "AGE_d2": age[C2],
        "BOTH_continuing": both_continuing,
        "d1_is_theft": (inc1 >= 0) & (inc1 != U), "d2_is_theft": (inc2 >= 0) & (inc2 != U),
        "d1_is_orphan": inc1 < 0, "d2_is_orphan": inc2 < 0,
        "already_kept": (inc1 == U) & (inc2 == U),
    }
    if IMGFREE:
        F = {k_: v_ for k_, v_ in F.items() if k_ in IMGFREE_KEEP}
    names = sorted(F)
    Xm = np.stack([np.asarray(F[k], dtype=np.float32) for k in names], axis=1)

    # ------------------------------------------------------------------ the FULL-FILM reading
    # ZEUS's metric is the true family's rank among ALL of its film's candidates, not among a
    # sample. Scoring happens here, in the process that already holds the matrix, so no 500 MB
    # feature file is ever written.
    if a.score_model:
        import lightgbm as lgb
        bst = lgb.Booster(model_file=a.score_model)
        want_names = json.load(open(a.score_model + ".names.json"))["features"]
        if want_names != names:
            idx = [names.index(w) for w in want_names]
            Xs = Xm[:, idx]
        else:
            Xs = Xm
        sc = np.empty(nc, np.float64)
        CH = 500000
        for s_ in range(0, nc, CH):
            sc[s_:s_ + CH] = bst.predict(Xs[s_:s_ + CH])
        # the same cut at scoring time, or the ranking is measured on a population the model
        # never saw -- a candidate the flow cut excludes is not proposed at all.
        if a.flow_cut > 0:
            excl = np.nan_to_num(F["FLOW_residual_midpoint"], nan=1e9) > a.flow_cut
            sc[excl] = -1.0
        rows_ = []
        for i_ in np.where(y == 1)[0]:
            above = int((sc >= sc[i_]).sum())
            rows_.append({"rank": above, "fraction": above / nc,
                          "u": int(nid[U[i_]]), "d1": int(nid[C1[i_]]), "d2": int(nid[C2[i_]]),
                          "t": int(tt[U[i_]]), "score": float(sc[i_])})
        # MITO2 -- THE STRUCTURAL VARIANT, no GBM at all, thresholds pre-registered in STATE.md
        # before this ran: (E) nothing detected under the back-projected position, (V) the volume
        # budget holds, (C) the sisters separate and come from one place. Survivors are ranked by
        # the flow-symmetry residual, NOT by a learned score.
        _st = ((np.nan_to_num(F["E_node_dist_t_um"], nan=0) >= 1.0)
               & (np.nan_to_num(F["V_ratio"], nan=0) >= 0.5)
               & (np.nan_to_num(F["V_ratio"], nan=9) <= 2.5)
               & (np.nan_to_num(F["C_sep_slope"], nan=-9) > 0.3)
               & (np.nan_to_num(F["C_conv_dist_um"], nan=99) <= 12.0))
        _sr = np.where(_st, -np.nan_to_num(F["S_mid_resid_um"], nan=99), -1e18)
        _stop = np.argsort(-_sr)[:25]
        _stop = [j for j in _stop if _sr[j] > -1e17]
        top = np.argsort(-sc)[:25]
        _sel = [int(j) for j in top[:a.top_k] if float(sc[j]) >= a.score_min]
        _edit = {"drop_edges": [], "add_edges": [], "touched": []}
        _seen = set()
        for _j in _sel:
            _u, _d1, _d2 = int(U[_j]), int(C1[_j]), int(C2[_j])
            if {_u, _d1, _d2} & _seen:
                continue
            _seen |= {_u, _d1, _d2}
            _pos = lambda _i: [int(tt[_i]), int(zyx[_i][0]), int(zyx[_i][1]), int(zyx[_i][2])]
            for _c in (kids.get(_u) or []):
                if _c not in (_d1, _d2):
                    _edit["drop_edges"].append({"source_id": int(nid[_u]), "target_id": int(nid[_c]),
                                                "source_pos": _pos(_u), "target_pos": _pos(_c)})
            for _d in (_d1, _d2):
                _pp = (par.get(_d) or [])
                for _p in _pp:
                    if _p != _u:
                        _edit["drop_edges"].append({"source_id": int(nid[_p]),
                                                    "target_id": int(nid[_d]),
                                                    "source_pos": _pos(_p), "target_pos": _pos(_d)})
                if _d not in (kids.get(_u) or []):
                    _edit["add_edges"].append({"source_id": int(nid[_u]), "target_id": int(nid[_d]),
                                               "source_pos": _pos(_u), "target_pos": _pos(_d)})
            _edit["touched"].append({"u": int(nid[_u]), "d1": int(nid[_d1]), "d2": int(nid[_d2]),
                                     "t": int(tt[_u]), "score": float(sc[_j])})
        out_ = {"film": a.film, "candidates": int(nc), "true_families": len(rows_),
                "selection": {"rule": "TOP-K by booster score, descending; a mother or a daughter "
                                      "touched twice in one film is skipped, highest score wins",
                              "top_k": int(a.top_k), "sep_um": [a.sep_lo_um, a.sep_hi_um],
                              "reach_um": a.reach_um, "flow_gate_um": a.flow_gate,
                              "score_min": a.score_min, "test_D": bool(a.with_d),
                              "model": str(a.score_model)},
                "edit_list": _edit,
                "top_k_selected": [{"u": int(nid[U[j]]), "d1": int(nid[C1[j]]),
                                    "d2": int(nid[C2[j]]), "t": int(tt[U[j]]),
                                    "score": float(sc[j])} for j in _sel],
                "n_structural": int(_st.sum()),
                "top25_struct": [{"u": int(nid[U[j]]), "d1": int(nid[C1[j]]), "d2": int(nid[C2[j]]),
                                  "t": int(tt[U[j]]), "score": float(_sr[j]),
                                  "is_true": bool(y[j] == 1)} for j in _stop],
                "TRUE": rows_,
                "top25": [{"u": int(nid[U[j]]), "d1": int(nid[C1[j]]), "d2": int(nid[C2[j]]),
                           "t": int(tt[U[j]]), "score": float(sc[j]), "is_true": bool(y[j] == 1)}
                          for j in top]}
        Path(a.score_out or (a.out + "/" + a.film + ".score.json")).write_text(
            json.dumps(out_, indent=1))
        print("[feat] SCORED %d candidates | true families at ranks %s (fractions %s)"
              % (nc, [r["rank"] for r in rows_],
                 ["%.2e" % r["fraction"] for r in rows_]), flush=True)
        return 0

    # ------------------------------------------------------------------ the sample
    rng = np.random.default_rng(a.seed)
    pos = np.where(y == 1)[0]
    neg = np.where(y == 0)[0]
    if a.keep_all:
        keep = np.arange(nc)
    else:
        # MITO2: the EVALUABLE FALSE class is kept ENTIRE -- it is the population the judge would
        # price as a false fork, and deliverable (2) compares the tests on judge-true against
        # judge-false. UNKNOWN is sampled: it is unannotated territory and can never be priced.
        evf = np.where(y3 == 0)[0]
        unk = np.where(y3 == -1)[0]
        hard_key = np.nan_to_num(sis_refl, nan=-9) + np.nan_to_num(cons, nan=0) * 0.0
        hard = unk[np.argsort(-hard_key[unk])[:a.n_hard]]
        rest = np.setdiff1d(unk, hard, assume_unique=False)
        rnd = rng.choice(rest, size=min(a.n_rand, len(rest)), replace=False)
        keep = np.concatenate([pos, evf, hard, rnd])
        keep = np.unique(keep)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(str(out / (a.film + ".feat.npz")),
                        X=Xm[keep].astype(np.float32), y=y[keep], y3=y3[keep],
                        names=np.array(names),
                        u=U[keep], c1=C1[keep], c2=C2[keep], kind=KIND[keep],
                        tcand=tt[U[keep]],
                        nid=nid, tt=tt, zyx=zyx,
                        n_candidates_total=np.int64(nc),
                        n_positives_total=np.int64(int(y.sum())),
                        reachable_families=np.int64(len(want)),
                        annotated_divisions=np.int64(len(divisions)),
                        film=np.array(a.film))
    print("[feat] kept %d rows (%d positive) of %d | %d features | %.1f s total"
          % (len(keep), int(y[keep].sum()), nc, len(names), time.time() - t00), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
