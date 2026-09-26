"""ENG/PAIR -- the GT-free pair features, as ONE reusable object.

This module is the single definition consumed by `pair_price.py` (the judged arms) and by
`pair_ship.py` (the kernel-side object). It is certified against `pair_build.py`'s stored
matrices at the BIT on three films by `pair_certify.py` before any number is read from it --
two keys on the same lock, per the standing rule.

GT-FREE is asserted, not claimed: this module imports no scorer, opens no `.geff`, and takes
only the champion's own node set and edges.
"""
from __future__ import annotations

import pathlib

import numpy as np

CAND_UM = 15.0
FLOW_K, FLOW_R_UM = 12, 25.0
CHAIN_CAP = 20

COLUMNS = [
    "disp_norm", "disp_dz", "disp_rho",
    "flow_defined", "flow_norm", "res_norm", "res_cos",
    "n_cand_s_10", "n_cand_s_15", "n_cand_d_10", "n_cand_d_15",
    "rank_s", "rank_d", "ratio_s", "ratio_d",
    "back_len_s", "fwd_len_d", "t_frac", "z_s_um", "border_um",
    "pm_prob", "pm_present", "pm_node_prob_s", "pm_node_prob_d",
]


def flow_at(src_pos, src_mov, query_pos):
    """Median motion of the K nearest sources within R um, tie-broken on (distance, index)
    -- ENG/KER11's FLOW_TIEBREAK rule. Returns (flow with NaN where undefined, fallbacks)."""
    from scipy.spatial import cKDTree
    tree = cKDTree(src_pos)
    m = len(query_pos)
    out = np.full((m, 3), np.nan)
    if m == 0:
        return out, 0
    kq = min(FLOW_K + 8, len(src_pos))
    dd, jj = tree.query(query_pos, k=kq, distance_upper_bound=FLOW_R_UM)
    dd = np.atleast_2d(dd)
    jj = np.atleast_2d(jj)
    n_fb = 0
    for r in range(m):
        d_r, j_r = dd[r], jj[r]
        ok = np.isfinite(d_r) & (j_r < len(src_pos))
        d_r, j_r = d_r[ok], j_r[ok]
        if len(d_r) < 3:
            continue
        order = np.lexsort((j_r, d_r))
        d_r, j_r = d_r[order], j_r[order]
        if len(d_r) > FLOW_K and kq < len(src_pos) and d_r[FLOW_K - 1] == d_r[-1]:
            n_fb += 1
            ball = np.asarray(tree.query_ball_point(query_pos[r], FLOW_R_UM), dtype=np.int64)
            db = np.linalg.norm(src_pos[ball] - query_pos[r], axis=1)
            j_r = ball[np.lexsort((ball, db))]
        sel = j_r[:FLOW_K]
        if len(sel) >= 3:
            out[r] = np.median(src_mov[sel], axis=0)
    return out, n_fb


def probmat_join(pm_dir, film, pos_um, t_arr, ech):
    p = pathlib.Path(pm_dir) / f"{film}.npz"
    if not p.exists():
        return None
    z = np.load(p)
    c = np.asarray(z["pm_coords"]).astype(np.float64)
    cat_t = c[:, 0].astype(np.int64)
    cat_pos = np.column_stack([c[:, 1] * ech[0], c[:, 2] * 4.0 * ech[1], c[:, 3] * 4.0 * ech[2]])
    from scipy.spatial import cKDTree
    cat_of_node = np.full(len(pos_um), -1, dtype=np.int64)
    for tt in np.unique(t_arr):
        w = np.flatnonzero(t_arr == tt)
        cw = np.flatnonzero(cat_t == tt)
        if not len(w) or not len(cw):
            continue
        tree = cKDTree(cat_pos[cw])
        d, j = tree.query(pos_um[w], k=1, distance_upper_bound=1.625)
        ok = np.isfinite(d)
        cat_of_node[w[ok]] = cw[j[ok]]
    seen = {}
    for i, c_ in enumerate(cat_of_node):
        if c_ < 0:
            continue
        dd = float(np.linalg.norm(pos_um[i] - cat_pos[c_]))
        if c_ in seen and seen[c_][1] <= dd:
            cat_of_node[i] = -1
        else:
            if c_ in seen:
                cat_of_node[seen[c_][0]] = -1
            seen[c_] = (i, dd)
    return {"cat_of_node": cat_of_node,
            "node_prob": np.asarray(z["pm_node_prob"]).astype(np.float32),
            "pm_src": np.asarray(z["pm_src"]).astype(np.int64),
            "pm_tgt": np.asarray(z["pm_tgt"]).astype(np.int64),
            "pm_prob": np.asarray(z["pm_prob"]).astype(np.float32),
            "join_rate": float(np.mean(cat_of_node >= 0)), "n_cat": int(len(cat_pos))}


def build_features(pos, t_arr, nid, esrc, etgt, film=None, pm_dir=None, ech=None):
    """Returns (si, di, F, info). `si`/`di` are INDICES into the node arrays."""
    from scipy.spatial import cKDTree
    n = len(nid)
    n_out = np.bincount(esrc, minlength=n)
    n_in = np.bincount(etgt, minlength=n)
    child_idx = np.full(n, -1, dtype=np.int64)
    parent_idx = np.full(n, -1, dtype=np.int64)
    only_out = n_out[esrc] == 1
    child_idx[esrc[only_out]] = etgt[only_out]
    only_in = n_in[etgt] == 1
    parent_idx[etgt[only_in]] = esrc[only_in]

    frames = {}
    for i, tt in enumerate(t_arr):
        frames.setdefault(int(tt), []).append(i)
    frames = {k: np.asarray(v, dtype=np.int64) for k, v in sorted(frames.items())}
    ts = sorted(frames)
    T = (max(ts) - min(ts) + 1) if ts else 1

    back_len = np.zeros(n, dtype=np.int32)
    for tt in ts:
        w = frames[tt]
        p_ = parent_idx[w]
        has = p_ >= 0
        back_len[w[has]] = np.minimum(back_len[p_[has]] + 1, CHAIN_CAP)
    fwd_len = np.zeros(n, dtype=np.int32)
    for tt in reversed(ts):
        w = frames[tt]
        c_ = child_idx[w]
        has = c_ >= 0
        fwd_len[w[has]] = np.minimum(fwd_len[c_[has]] + 1, CHAIN_CAP)

    lo, hi = pos.min(axis=0), pos.max(axis=0)
    border_all = np.minimum(pos - lo, hi - pos).min(axis=1)

    flow = np.full((n, 3), np.nan)
    n_fb_tot = 0
    for tt in ts:
        idx = frames[tt]
        sel = idx[n_out[idx] == 1]
        if len(sel) < 3:
            continue
        f, nfb = flow_at(pos[sel], pos[child_idx[sel]] - pos[sel], pos[idx])
        flow[idx] = f
        n_fb_tot += nfb

    S_all, D_all = [], []
    for tt in ts:
        if (tt + 1) not in frames:
            continue
        S, D = frames[tt], frames[tt + 1]
        tree = cKDTree(pos[D])
        nb = tree.query_ball_point(pos[S], r=CAND_UM)
        cnt = np.fromiter((len(x) for x in nb), dtype=np.int64, count=len(nb))
        if cnt.sum() == 0:
            continue
        flat = np.concatenate([np.asarray(x, dtype=np.int64) for x in nb if len(x)])
        S_all.append(np.repeat(S, cnt))
        D_all.append(D[flat])
    if not S_all:
        return (np.zeros(0, np.int64), np.zeros(0, np.int64),
                np.zeros((0, len(COLUMNS)), np.float32), {"flow_defined_frac": 0.0})
    si = np.concatenate(S_all)
    di = np.concatenate(D_all)
    m = len(si)
    disp = pos[di] - pos[si]
    dn = np.linalg.norm(disp, axis=1)
    fl = flow[si]
    fdef = np.isfinite(fl[:, 0])
    fl0 = np.where(fdef[:, None], fl, 0.0)
    res_norm = np.linalg.norm(disp - fl0, axis=1)
    flow_norm = np.linalg.norm(fl0, axis=1)
    denom = flow_norm * dn
    res_cos = np.where(denom > 0, np.einsum("ij,ij->i", disp, fl0) / np.maximum(denom, 1e-12), 0.0)

    def group_stats(key, other_nid):
        order = np.lexsort((other_nid, dn, key))
        k_s = key[order]
        new = np.empty(m, dtype=bool)
        new[0] = True
        new[1:] = k_s[1:] != k_s[:-1]
        starts = np.flatnonzero(new)
        gid = np.cumsum(new) - 1
        rank = np.arange(m) - starts[gid] + 1
        size = np.diff(np.append(starts, m))[gid]
        dmin = dn[order][starts][gid]
        c10 = np.cumsum(dn[order] <= 10.0)
        end = np.append(starts[1:], m) - 1
        base = np.where(starts > 0, c10[starts - 1], 0)
        n10 = (c10[end] - base)[gid]
        inv = np.empty(m, dtype=np.int64)
        inv[order] = np.arange(m)
        return rank[inv], size[inv], dmin[inv], n10[inv]

    rank_s, n15_s, dmin_s, n10_s = group_stats(si, nid[di])
    rank_d, n15_d, dmin_d, n10_d = group_stats(di, nid[si])

    F = np.empty((m, len(COLUMNS)), dtype=np.float32)
    F[:, 0] = dn
    F[:, 1] = disp[:, 0]
    F[:, 2] = np.linalg.norm(disp[:, 1:], axis=1)
    F[:, 3] = fdef
    F[:, 4] = flow_norm
    F[:, 5] = np.where(fdef, res_norm, dn)
    F[:, 6] = res_cos
    F[:, 7] = n10_s
    F[:, 8] = n15_s
    F[:, 9] = n10_d
    F[:, 10] = n15_d
    F[:, 11] = rank_s
    F[:, 12] = rank_d
    F[:, 13] = dn / np.maximum(dmin_s, 1e-9)
    F[:, 14] = dn / np.maximum(dmin_d, 1e-9)
    F[:, 15] = back_len[si]
    F[:, 16] = fwd_len[di]
    F[:, 17] = t_arr[si] / max(T - 1, 1)
    F[:, 18] = pos[si, 0]
    F[:, 19] = border_all[si]
    F[:, 20:24] = 0.0

    info = {"flow_defined_frac": float(np.mean(np.isfinite(flow[:, 0]))),
            "flow_ball_fallbacks": int(n_fb_tot), "n_pairs": int(m),
            "join_rate": None, "pair_cover": None}
    if pm_dir and film is not None and ech is not None:
        pm = probmat_join(pm_dir, film, pos, t_arr, ech)
        if pm is not None:
            con = pm["cat_of_node"]
            cs, cd = con[si], con[di]
            both = (cs >= 0) & (cd >= 0)
            key_pairs = pm["pm_src"] * np.int64(1 << 32) + pm["pm_tgt"]
            o = np.argsort(key_pairs)
            kp, vp = key_pairs[o], pm["pm_prob"][o]
            if len(kp):
                q = (np.where(both, cs, 0).astype(np.int64) * np.int64(1 << 32)
                     + np.where(both, cd, 0))
                loc = np.clip(np.searchsorted(kp, q), 0, len(kp) - 1)
                hit = both & (kp[loc] == q)
                F[hit, 20] = vp[loc[hit]]
            else:
                hit = np.zeros(m, dtype=bool)
            F[:, 21] = hit
            F[cs >= 0, 22] = pm["node_prob"][cs[cs >= 0]]
            F[cd >= 0, 23] = pm["node_prob"][cd[cd >= 0]]
            info["join_rate"] = round(pm["join_rate"], 6)
            info["pair_cover"] = round(float(hit.mean()), 6)
    return si, di, F, info


def world_from_csv(film, world_csv, juge_module):
    """Champion world -> arrays. `juge_module` is passed in so this file imports no scorer."""
    W = juge_module.charger_csv(pathlib.Path(world_csv))[film]
    ech = np.asarray(juge_module.echelle_du_film(film), dtype=np.float64)
    pos = W.zyx * ech
    t_arr = W.t.astype(np.int64)
    nid = W.node_id.astype(np.int64)
    idx_of = {int(v): i for i, v in enumerate(nid)}
    e = W.edges
    esrc = np.fromiter((idx_of[int(s)] for s in e[:, 0]), dtype=np.int64, count=len(e))
    etgt = np.fromiter((idx_of[int(d)] for d in e[:, 1]), dtype=np.int64, count=len(e))
    return W, ech, pos, t_arr, nid, esrc, etgt
