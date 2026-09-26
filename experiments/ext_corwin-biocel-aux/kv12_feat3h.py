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

import argparse
import csv as _csv
import json
import time
from pathlib import Path

import os as _os
import numpy as np
IMGFREE = _os.environ.get('KV12_IMGFREE', '0') == '1'
# KV12 round 7: the cut ahead of the pair features and the GBM is the DEFAULT, not an env
# opt-in. KER11's kernel exports nothing, so with a 0 default the block was skipped and the
# only cut left was the frozen one at scoring time -- 2,37 M candidates featurised and scored
# to throw the scores away. Set KV12_FLOWFIRST=0 to get the frozen behaviour back for parity.
FLOWFIRST = float(_os.environ.get('KV12_FLOWFIRST', '5.67') or 0)
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
    ap.add_argument("--sep-lo-um", type=float, default=4.0)
    ap.add_argument("--sep-hi-um", type=float, default=15.0)
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

    # ------------------------------------------------------------------ the candidates
    _pu, _pc, _po = [], [], []
    for t0 in sorted(by_t):
        nxt = by_t.get(t0 + 1)
        if not nxt:
            continue
        A = dec[np.asarray(nxt)]
        _src = by_t[t0]
        # KV12: ONE distance matrix per frame instead of one call per mother. Same broadcast, same
        # arithmetic -- row r is bit-for-bit the vector the frozen loop built for mother _src[r].
        _D = np.sqrt((((A[None, :, :] - dec[np.asarray(_src)][:, None, :]) * DEC_UM) ** 2).sum(2))
        _ORD = np.argsort(_D, axis=1)[:, :a.max_daughters]
        for _r, u in enumerate(_src):
            d = _D[_r]
            near = [nxt[j] for j in _ORD[_r] if d[j] <= a.sep_hi_um * 1.6]
            pool = sorted(set(near) | set(alt.get(u, ())))
            _L = len(pool)
            for ii in range(_L):
                for jj in range(ii + 1, _L):
                    _pu.append(u); _pc.append(pool[ii]); _po.append(pool[jj])
    # KV12: the separation window, once, on every pair -- instead of 3 M scalar numpy calls.
    _pu = np.asarray(_pu, np.int64); _pc = np.asarray(_pc, np.int64); _po = np.asarray(_po, np.int64)
    if len(_pu):
        _sep = np.sqrt((((dec[_pc] - dec[_po]) * DEC_UM) ** 2).sum(1))
        _m = (_sep >= a.sep_lo_um) & (_sep <= a.sep_hi_um)
        U, C1, C2 = _pu[_m], _pc[_m], _po[_m]
    else:
        U = C1 = C2 = np.zeros(0, np.int64)
    nc = len(U)
    print("[feat] %d candidates | %.1f s" % (nc, time.time() - t00), flush=True)
    if _os.environ.get("KV12_DUMP_TRIPLETS"):
        np.savez_compressed(_os.environ["KV12_DUMP_TRIPLETS"],
                            u=nid[U], c1=nid[C1], c2=nid[C2])
        print("[feat] triplets dumped to %s" % _os.environ["KV12_DUMP_TRIPLETS"], flush=True)
    if nc == 0:
        raise SystemExit("[feat] no candidate on %s" % a.film)

    # ------------------------------------------------------------------ the truth, by POSITION
    # KV12 GUARD: the SHIP path is GT-free. A hidden film has no .geff; without this the cell dies
    # here, before any feature is computed. y stays all-zero and nothing downstream changes shape.
    _gt = Path(a.data_dir) / (a.film + ".geff")
    if not _gt.exists():
        y = np.zeros(nc, np.int8)
        divisions, want = [], set()
        print("[feat] NO GROUND TRUTH for %s -- inference mode, y is all zero" % a.film, flush=True)
        _HAVE_GT = False
    else:
        _HAVE_GT = True
    if _HAVE_GT:
      import tracksdata as td
      rr = td.graph.IndexedRXGraph.from_geff(str(_gt))
      g = rr[0] if isinstance(rr, tuple) else rr
      nd = g.node_attrs(attr_keys=["node_id", "t", "z", "y", "x"])
      ed = g.edge_attrs(attr_keys=["source_id", "target_id"])
      GN = {int(x["node_id"]): (int(x["t"]), float(x["z"]), float(x["y"]), float(x["x"]))
            for x in nd.iter_rows(named=True)}
      gk = {}
      for x in ed.iter_rows(named=True):
          gk.setdefault(int(x["source_id"]), []).append(int(x["target_id"]))
      divisions = sorted((GN[m][0], m, sorted(v)[:2]) for m, v in gk.items() if len(v) >= 2)

      def near_node(t, q3):
          idx = by_t.get(t, [])
          if not idx:
              return None, 1e9
          Pn = zyx[np.asarray(idx)] * SCALE
          qq = np.asarray(q3) * SCALE
          dd = np.sqrt(((Pn - qq[None, :]) ** 2).sum(1))
          j = int(dd.argmin())
          return idx[j], float(dd[j])

      want = set()
      for (tm, m, ds) in divisions:
          im, dm = near_node(tm, GN[m][1:])
          if im is None or dm > a.gate_um:
              continue
          js = [near_node(GN[d][0], GN[d][1:]) for d in ds]
          if any(j is None or dj > a.gate_um for j, dj in js):
              continue
          if js[0][0] == js[1][0]:
              continue
          want.add((im, frozenset((js[0][0], js[1][0]))))
      y = np.zeros(nc, np.int8)
      for k_ in range(nc):
          if (int(U[k_]), frozenset((int(C1[k_]), int(C2[k_])))) in want:
              y[k_] = 1
      print("[feat] annotated divisions %d | reachable families %d | positives among candidates %d"
            % (len(divisions), len(want), int(y.sum())), flush=True)

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

    F = {
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
        top = np.argsort(-sc)[:25]
        out_ = {"film": a.film, "candidates": int(nc), "true_families": len(rows_),
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
        hard_key = np.nan_to_num(sis_refl, nan=-9) + np.nan_to_num(cons, nan=0) * 0.0
        hard = neg[np.argsort(-hard_key[neg])[:a.n_hard]]
        rest = np.setdiff1d(neg, hard, assume_unique=False)
        rnd = rng.choice(rest, size=min(a.n_rand, len(rest)), replace=False)
        keep = np.concatenate([pos, hard, rnd])
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(str(out / (a.film + ".feat.npz")),
                        X=Xm[keep].astype(np.float32), y=y[keep], names=np.array(names),
                        u=U[keep], c1=C1[keep], c2=C2[keep],
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
