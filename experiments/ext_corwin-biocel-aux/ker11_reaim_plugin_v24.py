#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ENG/KER11 -- the RE-AIM post-canon plugin, and its FLOW, defined ONCE.

ZEUS ruling KER11-NIGHT-2 (2026-09-12T22:02:14Z), clause (b), on HADES n°4.

THE CONTRACT THIS FILE EXISTS TO HONOUR. There are two things called "the K = 12
flow" in this project and they are NOT the same object:

  * ENG/DEFORM's EXPORT (`field199`, column `fl_*`), which is what the 199-film
    measurement of tonight was run on: a SOURCE is a node of the champion's own
    world at `t` with EXACTLY ONE child; its vector is `child - node`;
    `flow(t, p)` is the **MEDIAN** vector of the **K = 12 nearest sources within
    R = 25 um** of `p`, and it is **UNDEFINED with fewer than 3**.
  * the kernel's `ker11_tissue_flow_field` in `build_kernel_linker.py`: a **MEAN**
    over a spatial tree with **no temporal separation inside the function**, fed
    by **ILP links**.

Same name, three differences: period, estimator, source graph. `DF_m2` was
measured on the FIRST. This plugin therefore implements the FIRST, and
`flow_identity_onefilm()` PROVES producer = consumer before anything is pushed:
the function below, run on the champion's world of one film, against the export's
`fl` column at the same positions, joined by (t, z, y, x) and never by id.

WHAT THE PLUGIN DOES, AND WHAT IT REFUSES TO DO. For every track end (a node with
zero children, before the film's last frame) it proposes the local re-solve of
ZEUS's amendment: candidates at t+1 within 7 um of `p + flow(p)` INCLUDING those
already assigned, their current parents brought into a local bipartite, Hungarian
on the field-compensated distance, applied only when the local total cost falls
by more than the margin. It NEVER moves, adds or deletes a node -- the node band
is zero by construction and asserted. On ANY exception it writes the world it
received, unchanged, and prints `REAIM_DISARMED: <reason>`.
"""
from __future__ import annotations

import json
import math
import sys
import time

import numpy as np

SCALE = (1.625, 0.40625, 0.40625)      # microns per integer index
FLOW_K = 12
FLOW_R_UM = 25.0
FLOW_MIN_SOURCES = 3
GATE_UM = 7.0
MARGIN_UM = 2.0
UNMATCHED_COST_UM = GATE_UM


def _um(d):
    s = np.asarray(SCALE, dtype=np.float64)
    return np.sqrt(((np.asarray(d, dtype=np.float64) * s) ** 2).sum(-1))


def flow_field(nodes, edges):
    """THE EXPORT'S DEFINITION, and nothing else.

    nodes : dict node_id -> (t, z, y, x) integer indices
    edges : iterable (source_id, target_id)
    Returns {node_id: (fz, fy, fx) in MICRONS} for every node, plus a
    `defined` set. A node with fewer than FLOW_MIN_SOURCES sources inside
    R is UNDEFINED and its vector is zero -- undefined is not zero, and the
    two are reported separately, which is why `defined` comes back.
    """
    nchild = {}
    child_of = {}
    for s_, t_ in edges:
        nchild[s_] = nchild.get(s_, 0) + 1
        child_of.setdefault(s_, []).append(t_)

    # a SOURCE : exactly one child. Its vector is child - node, in microns.
    src_by_t = {}
    for nid, k in nchild.items():
        if k != 1:
            continue
        p = nodes.get(nid)
        q = nodes.get(child_of[nid][0])
        if p is None or q is None:
            continue
        v = ((q[1] - p[1]) * SCALE[0], (q[2] - p[2]) * SCALE[1],
             (q[3] - p[3]) * SCALE[2])
        src_by_t.setdefault(p[0], []).append((p[1], p[2], p[3], v[0], v[1], v[2]))

    out, defined = {}, set()
    by_t = {}
    for nid, (t_, z_, y_, x_) in nodes.items():
        by_t.setdefault(t_, []).append((nid, z_, y_, x_))

    for t_, members in by_t.items():
        S = src_by_t.get(t_)
        if not S:
            for nid, *_ in members:
                out[nid] = (0.0, 0.0, 0.0)
            continue
        A = np.asarray(S, dtype=np.float64)
        sp = A[:, :3] * np.asarray(SCALE)          # source positions in um
        sv = A[:, 3:]                              # source vectors in um
        P = np.asarray([[z_, y_, x_] for _, z_, y_, x_ in members],
                       dtype=np.float64) * np.asarray(SCALE)
        for i, (nid, *_rest) in enumerate(members):
            d = np.sqrt(((sp - P[i]) ** 2).sum(1))
            inr = np.nonzero(d <= FLOW_R_UM)[0]
            if len(inr) < FLOW_MIN_SOURCES:
                out[nid] = (0.0, 0.0, 0.0)
                continue
            if len(inr) > FLOW_K:
                inr = inr[np.argsort(d[inr], kind="stable")[:FLOW_K]]
            m = np.median(sv[inr], axis=0)
            out[nid] = (float(m[0]), float(m[1]), float(m[2]))
            defined.add(nid)
    return out, defined


def flow_identity_onefilm(world_csv, field_parquet, film, tol_um=1e-6):
    """PRODUCER = CONSUMER, or no push. Joined by (t, z, y, x), never by id."""
    import polars as pl
    d = pl.read_csv(world_csv)
    n = d.filter(pl.col("row_type") == "node")
    e = d.filter(pl.col("row_type") == "edge")
    nodes = {int(i): (int(t), int(z), int(y), int(x)) for i, t, z, y, x in
             zip(n["node_id"], n["t"], n["z"], n["y"], n["x"])}
    edges = [(int(s), int(t)) for s, t in zip(e["source_id"], e["target_id"])]
    t0 = time.time()
    mine, defined = flow_field(nodes, edges)
    secs = time.time() - t0

    f = pl.read_parquet(field_parquet)
    key = {}
    for t_, z_, y_, x_, a, b, c, fd in zip(f["t"], f["z"], f["y"], f["x"],
                                           f["fl_z"], f["fl_y"], f["fl_x"],
                                           f["flow_defined"]):
        key[(int(t_), int(z_), int(y_), int(x_))] = (a, b, c, bool(fd))

    joined = miss = 0
    dz = []
    both_def = agree_def = 0
    for nid, (t_, z_, y_, x_) in nodes.items():
        k = key.get((t_, z_, y_, x_))
        if k is None:
            miss += 1
            continue
        joined += 1
        mv = mine[nid]
        dz.append(max(abs(mv[0] - k[0]), abs(mv[1] - k[1]), abs(mv[2] - k[2])))
        if k[3] == (nid in defined):
            agree_def += 1
        both_def += 1
    dz = np.asarray(dz) if dz else np.zeros(0)
    rep = {
        "schema": "ker11-flow-identity-1.0", "lane": "ENG/KER11",
        "order": "ZEUS KER11-NIGHT-2 clause (b)",
        "date_u": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "film": film, "world_csv": str(world_csv), "field": str(field_parquet),
        "_join": "by INTEGER POSITION (t,z,y,x). Never by id : ids are local to a world.",
        "_definition": ("source = a node of the world with EXACTLY ONE child ; its "
                        "vector is child - node ; flow(t,p) = MEDIAN of the K = 12 "
                        "nearest sources within R = 25 um ; UNDEFINED under 3."),
        "nodes": len(nodes), "joined": joined, "not_in_field": miss,
        "max_abs_delta_um": float(dz.max()) if len(dz) else None,
        "p99_abs_delta_um": float(np.percentile(dz, 99)) if len(dz) else None,
        "median_abs_delta_um": float(np.median(dz)) if len(dz) else None,
        "tolerance_um": tol_um,
        "within_tolerance": int((dz <= tol_um).sum()) if len(dz) else 0,
        "within_tolerance_frac": float((dz <= tol_um).mean()) if len(dz) else 0.0,
        "defined_flag_agrees": agree_def, "defined_flag_checked": both_def,
        "seconds_for_the_whole_film": round(secs, 3),
    }
    rep["IDENTITY"] = ("PASS" if (len(dz) and rep["within_tolerance_frac"] >= 0.999
                                  and agree_def == both_def) else "FAIL")
    return rep


def opposite_motion_test():
    """THE TEST THAT A MEAN WOULD FAIL AND A MEDIAN MUST PASS.

    Two transitions at one place with OPPOSITE motions must keep opposite
    predictions, not collapse to a near-zero average. Built at two SEPARATE
    frames, because the export's flow is per-frame -- which is precisely the
    'no temporal separation' difference that makes the kernel's function a
    different object.
    """
    nodes, edges = {}, []
    nid = 0

    def add(t, z, y, x):
        nonlocal nid
        nid += 1
        nodes[nid] = (t, z, y, x)
        return nid

    for t, dx in ((0, +10), (2, -10)):
        for j in range(6):
            a = add(t, 10, 100 + j, 100)
            b = add(t + 1, 10, 100 + j, 100 + dx)
            edges.append((a, b))
        probe = add(t, 10, 103, 100 + 1)          # a childless probe at the spot
        nodes[probe] = (t, 10, 103, 101)
    f, _d = flow_field(nodes, edges)
    v0 = [v for k, v in f.items() if nodes[k][0] == 0 and k not in
          [s for s, _t in edges]]
    v2 = [v for k, v in f.items() if nodes[k][0] == 2 and k not in
          [s for s, _t in edges]]
    x0 = np.median([v[2] for v in v0]) if v0 else 0.0
    x2 = np.median([v[2] for v in v2]) if v2 else 0.0
    return {"frame0_median_x_um": float(x0), "frame2_median_x_um": float(x2),
            "opposite": bool(x0 > 1.0 and x2 < -1.0),
            "_what_a_mean_over_both_frames_would_give": 0.0,
            "_why": ("the export's flow is computed PER FRAME. A function with no "
                     "temporal separation would average these two into zero and "
                     "predict no motion where the tissue moves fastest.")}


# =========================================================================
# THE KERNEL SIDE. One entry point, one contract, one fallback.
# =========================================================================
def apply_reaim(csv_in, csv_out, films=None, gate_um=GATE_UM, margin_um=MARGIN_UM,
                abstain=False, log=print):
    """v31's world in, v31 + DF_m2 out. NEVER raises.

    ZEUS KER11-NIGHT-2 (a) : on ANY exception the world received is written
    UNCHANGED and `REAIM_DISARMED: <reason>` is printed. On success the line
    `REAIM_ARMED films=N proposals=P applied=M` is printed -- bar 4 reads the
    disarm sentence as VOID, so the sentence has to be the truth.

    The node set is NEVER touched : no node is added, moved or deleted. That is
    asserted here and re-asserted by the caller, because "the counting term is
    zero by construction" is exactly the kind of claim that stops being true
    the day someone edits this function.
    """
    import polars as pl
    t0 = time.time()
    try:
        d = pl.read_csv(csv_in)
        n_nodes_in = d.filter(pl.col("row_type") == "node").height
        out_frames, tot_prop, tot_app, n_films = [], 0, 0, 0
        tot_over = 0
        for film in (films or sorted(d["dataset"].unique().to_list())):
            sub = d.filter(pl.col("dataset") == film)
            nodes_df = sub.filter(pl.col("row_type") == "node")
            edges_df = sub.filter(pl.col("row_type") == "edge")
            nodes = {int(i): (int(t), int(z), int(y), int(x)) for i, t, z, y, x in
                     zip(nodes_df["node_id"], nodes_df["t"], nodes_df["z"],
                         nodes_df["y"], nodes_df["x"])}
            edges = [(int(a), int(b)) for a, b in
                     zip(edges_df["source_id"], edges_df["target_id"])]
            fl, _def = flow_field(nodes, edges)
            added, moved, prop = resolve(nodes, edges, fl, gate_um,
                                         margin_um, abstain=abstain)
            _st = assert_property(nodes, edges, added, moved, fl, gate_um)
            tot_over += _st["beyond_own_gate"]
            tot_prop += prop
            tot_app += len(added) + len(moved)
            n_films += 1
            out_frames.append(_rewrite(sub, added, moved))
        w = pl.concat(out_frames, how="vertical_relaxed")
        n_nodes_out = w.filter(pl.col("row_type") == "node").height
        if n_nodes_out != n_nodes_in:
            raise AssertionError("node band is not zero : %d -> %d"
                                 % (n_nodes_in, n_nodes_out))
        w.write_csv(csv_out)
        log("REAIM_ARMED films=%d proposals=%d applied=%d nodes=%d "
            "beyond_own_gate=%d abstain=%s seconds=%.1f"
            % (n_films, tot_prop, tot_app, n_nodes_out, tot_over,
               abstain, time.time() - t0))
        return True
    except BaseException as e:                       # noqa: BLE001 -- deliberate
        try:
            import shutil
            shutil.copyfile(csv_in, csv_out)
            log("REAIM_DISARMED: %s: %s -- the world of v31 was written UNCHANGED"
                % (type(e).__name__, str(e)[:300]))
        except BaseException as e2:                  # noqa: BLE001
            log("REAIM_DISARMED: %s during the fallback copy (%s). The caller "
                "must ship csv_in itself." % (type(e2).__name__, str(e2)[:200]))
        return False


def resolve(nodes, edges, fl, gate_um=GATE_UM, margin_um=MARGIN_UM,
            abstain=False):
    """The local re-solve. ONE implementation, used by the kernel plugin and by
    the reference engine, so the thing judged and the thing shipped cannot drift.

    Returns (added, moved, considered) where `added` and `moved` are the FINAL
    TRANSACTION against the graph received -- never the history of intermediate
    re-attributions.

    ================= THE TWO DEFECTS THIS SHAPE EXISTS TO PREVENT =============
    Found by ENG/HADES (n5), verified by ZEUS, in the first version of this
    function. Both were silent: the world was written, the judge scored it, and
    the numbers looked fine.

    (1) TWO PARENTS WRITTEN. The old code appended every re-attribution to a
        `moved` list and the writer removed only edges present in the ORIGINAL
        graph. A target re-attributed twice -- P to A in one local problem, then
        A to B in a later one -- produced moved = [(P,A,q),(A,B,q)]: (P,q) was
        removed, (A,q) had never existed so nothing was removed for it, and BOTH
        (A,q) and (B,q) were written. The node then had two parents. The margin
        was no protection: each step can gain more than it on its own.
        THE FIX is not a patch on the writer, it is a change of what we record.
        We keep `parent0`, the map as received, mutate a live `parent` map, and
        at the end emit ONE row per touched target: nothing if it came back to
        where it started, an ADD if it had no parent, a MOVE otherwise. One
        parent per target BY CONSTRUCTION, not by vigilance.

    (2) A FORK DESTROYED FROM OUTSIDE THE NEIGHBOURHOOD. The old check counted a
        source's children only among the candidates Q. A mother with one daughter
        inside the gate and one outside passed it, and could lose the inside
        daughter -- a true division destroyed by a rule that is only supposed to
        CONTINUE tracks. Symmetrically a source with a child outside Q could take
        a q and end with two: a division INVENTED by a continuation rule. That is
        the measured d div_fp +3 and +2 at margins 0,5 and 1,0.
        THE FIX is to count children on the FULL graph, live: any candidate whose
        current parent does not have EXACTLY ONE child freezes the whole local
        problem. A source that enters the comparison therefore has exactly one
        child and it is inside Q, so the Hungarian's single slot per source
        conserves its count, and the track end can only go from zero to one.
    ==========================================================================
    """
    from scipy.optimize import linear_sum_assignment
    nchild, parent0 = {}, {}
    for s_, t_ in edges:
        nchild[s_] = nchild.get(s_, 0) + 1
        parent0[t_] = s_
    parent = dict(parent0)
    nchild_now = dict(nchild)

    by_t = {}
    for nid, (t_, _z, _y, _x) in nodes.items():
        by_t.setdefault(t_, []).append(nid)
    tmax = max(t for t, _z, _y, _x in nodes.values())

    def aim(nid):
        _t, z_, y_, x_ = nodes[nid]
        f = fl.get(nid, (0.0, 0.0, 0.0))
        return (z_ + f[0] / SCALE[0], y_ + f[1] / SCALE[1], x_ + f[2] / SCALE[2])

    considered = 0
    frozen = 0
    unbalanced = 0
    touched = set()
    ends = sorted(n for n in nodes
                  if nchild.get(n, 0) == 0 and nodes[n][0] < tmax)
    for i in ends:
        if nchild_now.get(i, 0) != 0:
            continue                      # it already received a child: at most one
        cand = by_t.get(nodes[i][0] + 1)
        if not cand:
            continue
        a = np.asarray(aim(i), dtype=np.float64)
        C = np.asarray([nodes[q][1:] for q in cand], dtype=np.float64)
        dd = _um(C - a)
        Q = [cand[j] for j in np.nonzero(dd <= gate_um)[0]]
        if not Q:
            continue
        considered += 1
        S, par_of_q, freeze = [i], {}, False
        for q in Q:
            ps = parent.get(q)
            if ps is None:
                continue
            if ps not in nodes or nchild_now.get(ps, 0) != 1:
                freeze = True             # a fork, or a source we cannot balance
                break
            par_of_q[q] = ps
            if ps not in S:
                S.append(ps)
        if freeze:
            frozen += 1
            continue
        QP = np.asarray([nodes[q][1:] for q in Q], dtype=np.float64)
        M = np.zeros((len(S), len(Q)), dtype=np.float64)
        for r, s_ in enumerate(S):
            M[r, :] = _um(QP - np.asarray(aim(s_), dtype=np.float64))
        cur = sum(M[S.index(ps), Q.index(q)] for q, ps in par_of_q.items())
        cur += UNMATCHED_COST_UM * (len(S) - len(par_of_q))
        # --- HADES n8, verified by ZEUS and REPRODUCED (a 23,97 um edge on a
        # four-node case ; 17 of the 1 359 edges of the shipped world lie beyond
        # the 7 um gate). With `pad = max(0, |S| - |Q|)` the abstention column
        # exists ONLY when there are more sources than targets, so with enough
        # targets EVERY source is forced onto one -- at any distance, because the
        # gate is measured from the TRACK END's position and not from theirs.
        # `abstain=True` gives each source its own abstention column, always.
        pad = len(S) if abstain else max(0, len(S) - len(Q))
        M2 = (np.concatenate([M, np.full((len(S), pad), UNMATCHED_COST_UM)], axis=1)
              if pad else M)
        r_, c_ = linear_sum_assignment(M2)
        if cur - float(M2[r_, c_].sum()) <= margin_um:
            continue
        want = {S[rr]: Q[cc] for rr, cc in zip(r_, c_) if cc < len(Q)}
        # --- defect (3), found by assert_graph_legal on film 6bba_74686d6a, node
        # 8095 : "source gained a child, 1 to 2". A source whose child is in Q but
        # which the assignment leaves UNMATCHED would have its child released and
        # taken by nobody. The release was then dropped from the final transaction
        # (an unclaimed target has no edge to write), so the OLD edge survived in
        # the world while the source's new edge was added -- two children.
        # The rule is a CONTINUATION rule: it must never delete an edge. So the
        # only coherent resolution is to refuse the whole local problem when a
        # target would be RELEASED and claimed by nobody. A source losing its
        # child to another source is fine -- the edge moves, it is not deleted,
        # and the source simply becomes a track end itself.
        # A microcase would not have produced this: it needs |Q| < |S|, i.e. more
        # competing sources than targets inside the gate, which is a dense frame.
        _taken = set(want.values())
        if any(q not in _taken and want.get(ps) != q
               for q, ps in par_of_q.items()):
            unbalanced += 1
            continue
        for s_ in want:                   # release first, then take
            for q, ps in list(par_of_q.items()):
                if ps == s_ and want[s_] != q and parent.get(q) == s_:
                    parent[q] = None
                    nchild_now[s_] = nchild_now.get(s_, 1) - 1
                    touched.add(q)
        for s_, q in want.items():
            old = parent.get(q)
            if old == s_:
                continue
            if old is not None:
                nchild_now[old] = nchild_now.get(old, 1) - 1
            parent[q] = s_
            nchild_now[s_] = nchild_now.get(s_, 0) + 1
            touched.add(q)

    added, moved = [], []
    for q in sorted(touched):
        final, first = parent.get(q), parent0.get(q)
        if final == first:
            continue
        if final is None:
            # unreachable since the balance check above : a released target is
            # always taken. Kept as a RAISE, not a `continue`, because the
            # `continue` that used to be here is precisely what wrote a second
            # parent onto node 8095 -- a silent skip is how this defect lived.
            raise AssertionError("target %r was released and taken by nobody ; "
                                 "the balance check should have refused this "
                                 "local problem" % q)
        if first is None:
            added.append((final, q))
        else:
            moved.append((first, final, q))
    return added, moved, considered


def assert_graph_legal(nodes, edges0, added, moved):
    """The whole-graph assertion (ZEUS (c)). Run AFTER the transaction is computed
    and BEFORE the world is written: one parent per target, no source above two
    children, every initial fork intact, no source gaining a child."""
    parent0, nchild0 = {}, {}
    for s_, t_ in edges0:
        parent0[t_] = s_
        nchild0[s_] = nchild0.get(s_, 0) + 1
    parent = dict(parent0)
    for o, s_, q in moved:
        if parent.get(q) != o:
            raise AssertionError("move (%r to %r) on %r whose parent is %r"
                                 % (o, s_, q, parent.get(q)))
        parent[q] = s_
    for s_, q in added:
        if parent.get(q) is not None:
            raise AssertionError("add (%r to %r) on a target that already has %r"
                                 % (s_, q, parent[q]))
        parent[q] = s_
    seen = {}
    for q, s_ in parent.items():
        if s_ is not None:
            seen[s_] = seen.get(s_, 0) + 1
    for s_, k in seen.items():
        if k > 2:
            raise AssertionError("source %r ends with %d children" % (s_, k))
    for s_, k0 in nchild0.items():
        if k0 >= 2 and seen.get(s_, 0) < k0:
            raise AssertionError("initial fork on %r broken: %d to %d"
                                 % (s_, k0, seen.get(s_, 0)))
        if k0 >= 1 and seen.get(s_, 0) > k0:
            raise AssertionError("source %r gained a child: %d to %d"
                                 % (s_, k0, seen.get(s_, 0)))
    return {"targets": len(parent), "sources": len(seen),
            "max_children": max(seen.values()) if seen else 0,
            "initial_forks": sum(1 for v in nchild0.values() if v >= 2)}


def _rewrite(sub, added, moved):
    """Edges only. Node rows pass through untouched, by construction."""
    import polars as pl
    nodes = sub.filter(pl.col("row_type") == "node")
    edges = sub.filter(pl.col("row_type") == "edge")
    kill = {(o, q) for o, _s, q in moved}
    if kill:
        keep = [(int(a), int(b)) not in kill for a, b in
                zip(edges["source_id"].to_list(), edges["target_id"].to_list())]
        edges = edges.filter(pl.Series(keep))
    new = [(a, b) for a, b in added] + [(s_, q) for _o, s_, q in moved]
    if new:
        proto = edges.head(1) if edges.height else sub.head(1)
        base = {c: (proto[c][0] if proto.height else None) for c in sub.columns}
        rows = []
        for a, b in new:
            r = dict(base)
            r["row_type"] = "edge"
            r["source_id"] = a
            r["target_id"] = b
            for c in ("node_id", "t", "z", "y", "x"):
                if c in r:
                    r[c] = None
            rows.append(r)
        edges = pl.concat([edges, pl.DataFrame(rows, schema=sub.schema)],
                          how="vertical_relaxed")
    return pl.concat([nodes, edges], how="vertical_relaxed")


def assert_property(nodes, edges0, added, moved, fl, gate_um=GATE_UM):
    """THE PROPERTY TEST. Not "did it crash" -- "does every edge it wrote satisfy
    the rule's own stated contract".

    The three properties, and the third is the one that was silently false:
      1. every target single-parented                     (defects 1 and 3)
      2. no source ends with more children than it began  (defect 2)
      3. EVERY NEW EDGE IS WITHIN THE GATE OF *ITS OWN* SOURCE'S COMPENSATED
         POSITION -- not of the track end's. This is the contract I stated all
         evening ("within 7 um") and did not hold: on the shipped world 17 of
         1 359 edges violate it, up to 11,45 um.

    Returns the VIOLATION COUNTS. It does not raise on property 3 -- an arm may
    legitimately choose to write such edges, but it may never do so silently.
    """
    st = assert_graph_legal(nodes, edges0, added, moved)   # 1 and 2, these DO raise
    over, worst = [], 0.0
    for s_, q in list(added) + [(x, y) for _o, x, y in moved]:
        f = fl.get(s_, (0.0, 0.0, 0.0))
        aim = (nodes[s_][1] + f[0] / SCALE[0],
               nodes[s_][2] + f[1] / SCALE[1],
               nodes[s_][3] + f[2] / SCALE[2])
        d = float(_um(np.asarray(nodes[q][1:], dtype=np.float64)
                      - np.asarray(aim, dtype=np.float64)))
        worst = max(worst, d)
        if d > gate_um:
            over.append((s_, q, round(d, 4)))
    st["edges_written"] = len(added) + len(moved)
    st["beyond_own_gate"] = len(over)
    st["beyond_own_gate_pct"] = (100.0 * len(over) / st["edges_written"]
                                 if st["edges_written"] else 0.0)
    st["worst_edge_um"] = round(worst, 4)
    st["gate_um"] = gate_um
    st["_examples"] = sorted(over, key=lambda r: -r[2])[:5]
    return st


def selftest():
    """HADES n5's three cases, named, plus the whole-graph assertion.

    Each of these FAILED on the version this lane pushed as kernel version 22 at
    2026-09-12T22:17:02Z. They are here so that version can never come back.
    """
    ok = []

    def W(nodes, edges):
        return ({i: (t, z, y, x) for i, t, z, y, x in nodes}, list(edges))

    # --- CASE 1 : "P to A to B writes ONE parent, B" -------------------------
    # q is re-attributed twice across two local problems. The old code wrote both
    # (A,q) and (B,q) and the node ended with two parents.
    nodes = [(1, 0, 0, 0, 0),      # P, parent of q
             (2, 1, 0, 0, 0),      # q
             (3, 0, 0, 0, 2),      # A, a track end nearer than P
             (4, 0, 0, 0, 3)]      # B, a track end nearer than A
    n, e = W(nodes, [(1, 2)])
    fl = {k: (0.0, 0.0, 0.0) for k in n}
    added, moved, _c = resolve(n, e, fl, gate_um=7.0, margin_um=0.0)
    st = assert_graph_legal(n, e, added, moved)
    tgt = [q for _o, _s, q in moved] + [q for _s, q in added]
    assert len(tgt) == len(set(tgt)), (added, moved)
    assert st["max_children"] <= 1, st
    ok.append("P to A to B writes ONE parent for the target, never two")

    # --- CASE 2 : "a mother with one daughter outside Q keeps both" ----------
    # node 1 is a real fork: daughter 2 is inside the gate, daughter 5 is far
    # away. The old check counted only the children inside Q, saw one, and let
    # the local problem take daughter 2 -- destroying a true division from
    # outside the neighbourhood it was looking at.
    nodes = [(1, 0, 0, 0, 0), (2, 1, 0, 0, 0), (5, 1, 0, 0, 60),
             (3, 0, 0, 0, 1)]
    n, e = W(nodes, [(1, 2), (1, 5)])
    fl = {k: (0.0, 0.0, 0.0) for k in n}
    added, moved, _c = resolve(n, e, fl, gate_um=7.0, margin_um=0.0)
    assert added == [] and moved == [], (added, moved)
    st = assert_graph_legal(n, e, added, moved)
    assert st["initial_forks"] == 1
    ok.append("a mother with one daughter outside Q keeps BOTH daughters")

    # --- CASE 3 : "a one-child source refuses a second child" ---------------
    # node 1 already has a child OUTSIDE the gate. A free target sits inside.
    # A continuation rule must never turn it into a fork.
    nodes = [(1, 0, 0, 0, 0), (5, 1, 0, 0, 60), (2, 1, 0, 0, 1)]
    n, e = W(nodes, [(1, 5)])
    fl = {k: (0.0, 0.0, 0.0) for k in n}
    added, moved, _c = resolve(n, e, fl, gate_um=7.0, margin_um=0.0)
    for s_, _q in added:
        assert s_ != 1, (added, moved)
    for _o, s_, _q in moved:
        assert s_ != 1, (added, moved)
    assert_graph_legal(n, e, added, moved)
    ok.append("a source that already has a child refuses a second one")

    # --- CASE 4 : the rule still DOES something ------------------------------
    # A guard that only refuses proves nothing: one track end, one free target
    # one voxel away, and the edge must appear.
    nodes = [(1, 0, 5, 5, 5), (2, 1, 5, 5, 6)]
    n, e = W(nodes, [])
    fl = {k: (0.0, 0.0, 0.0) for k in n}
    added, moved, _c = resolve(n, e, fl, gate_um=7.0, margin_um=0.0)
    assert added == [(1, 2)] and moved == [], (added, moved)
    assert_graph_legal(n, e, added, moved)
    ok.append("the passing path: a free target one voxel away is taken")

    # --- CASE 5 : a genuine re-attribution still happens ---------------------
    # the incumbent parent is two voxels away, the track end one: the edge moves,
    # exactly once, and the old edge is the one named in the move.
    nodes = [(1, 0, 5, 5, 5), (2, 1, 5, 5, 6), (3, 0, 5, 5, 8)]
    n, e = W(nodes, [(3, 2)])
    fl = {k: (0.0, 0.0, 0.0) for k in n}
    added, moved, _c = resolve(n, e, fl, gate_um=7.0, margin_um=0.0)
    assert moved == [(3, 1, 2)] and added == [], (added, moved)
    assert_graph_legal(n, e, added, moved)
    ok.append("the passing path: a cheaper source takes the target, once")

    # --- CASE 7 : "more sources than targets leaves nobody stranded" --------
    # THE SHAPE THAT MICROCASES MISSED and the assertion caught on film
    # 6bba_74686d6a, node 8095. Two sources with a child each, ONE target inside
    # the gate, plus a track end : the assignment cannot serve everyone, and the
    # old code released a child that nobody took while still writing the new
    # edge -- the source ended with two children. The local problem must be
    # refused whole.
    nodes = [(1, 0, 0, 0, 0),      # source A, child 10
             (2, 0, 0, 0, 1),      # source B, child 11
             (9, 0, 0, 0, 2),      # the track end
             (10, 1, 0, 0, 0),     # A's child, inside the gate
             (11, 1, 0, 0, 90)]    # B's child, far outside
    n, e = W(nodes, [(1, 10), (2, 11)])
    fl = {k: (0.0, 0.0, 0.0) for k in n}
    added, moved, _c = resolve(n, e, fl, gate_um=7.0, margin_um=0.0)
    st = assert_graph_legal(n, e, added, moved)
    assert st["max_children"] <= 1, (added, moved, st)
    for s_, _q in added:
        assert s_ not in (1, 2), (added, moved)
    ok.append("more sources than targets: nobody is left holding a released child")

    # --- CASE 8 : "with abstention, a forced source declines" ---------------
    # HADES n8's own shape. Track end at x=0 ; X at x=-1 is B's child, Y at x=+1
    # is free ; B sits at x=60. WITHOUT abstention the assignment must give B
    # something and it writes a 23,97 um edge. WITH abstention B declines.
    nodes = [(1, 0, 0, 0, 0), (2, 1, 0, 0, -1), (3, 1, 0, 0, 1), (4, 0, 0, 0, 60)]
    n, e = W(nodes, [(4, 2)])
    fl = {k: (0.0, 0.0, 0.0) for k in n}
    a_no, m_no, _ = resolve(n, e, fl, gate_um=7.0, margin_um=2.0, abstain=False)
    p_no = assert_property(n, e, a_no, m_no, fl, gate_um=7.0)
    a_ab, m_ab, _ = resolve(n, e, fl, gate_um=7.0, margin_um=2.0, abstain=True)
    p_ab = assert_property(n, e, a_ab, m_ab, fl, gate_um=7.0)
    assert p_no["beyond_own_gate"] >= 1, p_no
    assert p_ab["beyond_own_gate"] == 0, (p_ab, a_ab, m_ab)
    ok.append("abstain=True: the forced source declines, and the over-gate edge "
              "that abstain=False writes (%.2f um) is gone" % p_no["worst_edge_um"])

    # --- CASE 9 : the property test COUNTS rather than hides ----------------
    # It must report a violation, not raise on it -- an arm may choose to write
    # such an edge, but never silently.
    assert p_no["beyond_own_gate_pct"] > 0 and p_no["edges_written"] > 0
    assert "worst_edge_um" in p_no and p_no["_examples"]
    ok.append("the property test COUNTS over-gate edges instead of hiding them")

    # --- CASE 6 : the assertion itself refuses an illegal transaction --------
    nodes = [(1, 0, 0, 0, 0), (2, 1, 0, 0, 0), (3, 0, 0, 0, 1)]
    n, e = W(nodes, [(1, 2)])
    try:
        assert_graph_legal(n, e, [(3, 2)], [])      # 2 would have two parents
    except AssertionError:
        ok.append("assert_graph_legal refuses a target with two parents")
    else:
        raise AssertionError("the whole-graph assertion admitted two parents")

    for i, t in enumerate(ok, 1):
        print("  %d PASS  %s" % (i, t))
    print("[ker11] plugin selftest PASS : %d cases -- HADES n5's three defects, "
          "two passing paths, and the assertion refusing an illegal transaction."
          % len(ok))
    return 0



if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--world-csv", default="")
    ap.add_argument("--field", default="")
    ap.add_argument("--film", default="")
    ap.add_argument("--tol-um", type=float, default=1e-6)
    ap.add_argument("--receipt", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    rep = flow_identity_onefilm(a.world_csv, a.field, a.film, a.tol_um)
    rep["opposite_motion_test"] = opposite_motion_test()
    import pathlib
    pathlib.Path(a.receipt).write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in rep.items()
                      if k not in ("_join", "_definition")}, indent=1))
    sys.exit(0 if rep["IDENTITY"] == "PASS" else 1)
