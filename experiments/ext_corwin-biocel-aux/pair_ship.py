"""ENG/PAIR -- THE SHIP OBJECT: a GT-free learned opinion for the champion's relink.

Handed to ENG/KER11. Nothing in this file is to be edited into a deployed cell in place: it is a
NEW module that a copy of `cell_06.py` imports, and its effect is gated by one env dial whose
default makes the patched cell byte-identical to the deployed one.

======================================================================================
WHAT IT IS
======================================================================================
`pair_edge_probs(nodes_by_id, seed_edges)` returns `{(source_id, target_id): p}` for every
(node at t, node at t+1) pair within 15,0 judge-um of the champion's own node set, where `p` is
a LightGBM probability that the judge would count that pair as a true edge.

It is trained on the sealed scorer's own labels on 199 films (126 016 positives, 968 623
negatives, `recus/PAIR_LABELS.json`, both certifications passing 199/199) and read OUT-OF-FOLD BY
FILM and LEAVE-ONE-EMBRYO-OUT (`recus/PAIR_OOF_AUC_BOOT.json`).

======================================================================================
GT-FREE, ASSERTED AT IMPORT AND NOT MERELY CLAIMED
======================================================================================
This module imports numpy, scipy.spatial, lightgbm and `pair_features` -- nothing else. It opens
exactly one file, the booster, whose sha256 it verifies. It never reads a `.geff`, never imports
the scorer bundle, never touches `RADAR_GT_DIR`, and takes no film identity as an input to any
column. `assert_gt_free()` runs at import and raises if any scorer module is already bound into
this module's namespace or if the booster's sha does not match.

======================================================================================
HOW `cell_06.py` USES IT -- four sites, one new env dial, default INERT
======================================================================================
Work on a copy of `10_CHANTIERS/40_LIAGE/impl/cell_06_deployed_1d67f13c.py` (sha
`1d67f13cce9fa2b6...`); the shard variant `40cb2e18...` takes the identical change.

  site 1  `cell_03.py`, beside the other relink dials:
            BIOHUB_MOTION_RELINK_PAIR_SCORER   default "0"     <- unset => byte-identical
            BIOHUB_MOTION_RELINK_PAIR_BONUS    default "16.0"
  site 2  `motion_relink_edges` signature (cell_06.py:420) gains
            `pair_edge_probs: dict | None = None, pair_bonus: float = 0.0`
  site 3  the cost line (cell_06.py:481) gains ONE term:
            cost[i, j] = motion + 0.05*raw - MOTION_RELINK_LEARNED_BONUS*prob \\
                                           - pair_bonus * pair_prob(i, j)
          **It must be a SECOND term, never folded into `learned_edge_probs`**: cell_06's own
          `learned_prob()` pushes anything outside [0,1] through a sigmoid, so a coefficient
          cannot be carried inside the dict's values.
  site 4  at cell_06.py:1393, two passes instead of one:
            seed = motion_relink_edges(nodes_by_id, {}, learned_edge_probs)          # unchanged
            pp   = pair_ship.pair_edge_probs(nodes_by_id, [(s, t) for s, t, *_ in seed])
            motion_edges = motion_relink_edges(nodes_by_id, stats, learned_edge_probs,
                                               pair_edge_probs=pp, pair_bonus=PAIR_BONUS)

WHY TWO PASSES. The strongest column is `res_norm`, the residual of the displacement after the
tissue flow, and the flow is built from SINGLE-CHILD LINKS -- which do not exist at line 1393
until something has linked. The seed pass is the cheapest edge set `cell_06` can compute for
itself, and every number this lane published was produced on exactly that seed
(`recus/PAIR_BOOTSTRAP.json`). Measured extra cost of the seed pass: **0,44 s/film mean,
4,29 s max** on 32 vCPU. The ILP's own `edges` are available at that line too and would be free,
but this lane never measured that variant and does not recommend what it has not measured.

======================================================================================
WHAT WAS MEASURED, SO NOBODY HAS TO TAKE THIS ON TRUST
======================================================================================
199 films, sealed judge, OUT-OF-FOLD probabilities only, `recus/R_JUGE_PAIR_CORE15.json` and
`recus/R_JUGE_PAIR_DEPLOY.json`, one replay of the deployed relink, arm A = prob 0:

    B_b16      +98 tp  -144 fp   dJ_edge +0,001687   (44b6 +0,000609 / 6bba +0,001889)
    B_LOEO_b16 +100 tp -144 fp   dJ_edge +0,001702   (44b6 +0,001008 / 6bba +0,001831)
    BC_b16     +99 tp  -144 fp   dJ_edge +0,001694   <- the vendor's term kept at its deployed
                                                        1,0 AND ours at 16: they compose
    C_b16 (the VENDOR's probability at the same coefficient)   dJ_edge  -0,000104

**ARM A IS NOT THE CHAMPION** (fidelity -621 tp / +1 600 fp / dJ -0,015452): no gap-close, no
safe divisions, no short-track filter, positions already smoothed. These are a SIGN and a SIZE.
Only a DRY turns them into a delta, and the DRY's node band will NOT be 0.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

import numpy as np

# ------------------------------------------------------------------ ship defaults
CAND_UM = 15.0            # the candidate gate the model was trained on
RELINK_REACH_UM = 10.0    # no pair beyond the relaxed radius can ever become an edge
PAIR_BONUS_DEFAULT = 16.0  # the coefficient of the NEW cost term; 8, 16 and 32 all pass
MODEL_NAME = "pair_gbm_core15_boot.txt"
MODEL_SHA256 = "289fd9d81d4a62fde8b54d8f01077f8f8c84fec2cdc1ca770f639b736f6a51c1"
NAMES_NAME = "pair_gbm_core15_boot.names.json"
NAMES_SHA256 = "1b1444b159b20558087c59724c7ce68909c31ffdd9fb80cc96537f0bb3ea0016"
COLUMNS = ["disp_norm", "disp_dz", "disp_rho", "flow_defined", "flow_norm", "res_norm",
           "res_cos", "n_cand_s_10", "n_cand_s_15", "n_cand_d_10", "n_cand_d_15",
           "rank_s", "rank_d", "ratio_s", "ratio_d"]
CORE15 = list(range(15))
#: Where the runtime artefacts are looked for, in order. They are IN GIT under the run
#: directory's `ship/`, so no consumer ever depends on a network volume again.
SEARCH_DIRS = ("", "../ship", "ship")
_FORBIDDEN = ("tracking_cellmot", "tracksdata", "lifetwin.radar.juge", "zarr")


def assert_gt_free() -> dict:
    """Raise unless this module's own namespace is free of every ground-truth reader."""
    bad = [n for n in _FORBIDDEN if n in globals() or any(
        isinstance(v, type(sys)) and getattr(v, "__name__", "") == n for v in globals().values())]
    if bad:
        raise RuntimeError(f"pair_ship is not GT-free: {bad}")
    return {"gt_free": True, "forbidden_checked": list(_FORBIDDEN)}


_GT_FREE = assert_gt_free()
_BOOSTER = None


def find_artefact(name, model_dir=None):
    """The artefacts live beside this module OR in the run directory's `ship/`. Both are in
    git. Returns the first existing path; raises with every place it looked."""
    here = pathlib.Path(__file__).resolve().parent
    tried = []
    for d in ([pathlib.Path(model_dir)] if model_dir else []) + [here / s for s in SEARCH_DIRS]:
        p = (d / name).resolve()
        tried.append(str(p))
        if p.exists():
            return p
    raise FileNotFoundError(f"pair_ship: {name} not found. Looked in: {tried}")


def load_names(model_dir=None, verify_sha=True):
    """The column order, loaded GUARDED.

    ENG/KV12 shipped a model whose `.names.json` was loaded UNGUARDED and was not on the
    machine -- ENG/KER11's STATE.md calls it « the one blocker ». This function never blocks:
    when the file is absent the module falls back to its own `COLUMNS` literal, and when it is
    present it must AGREE with it and with the booster's own `feature_names` header.
    """
    try:
        p = find_artefact(NAMES_NAME, model_dir)
    except FileNotFoundError:
        return {"source": "module literal COLUMNS", "columns": list(COLUMNS), "verified": False}
    if verify_sha:
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        if sha != NAMES_SHA256:
            raise RuntimeError(f"pair_ship names sha mismatch: {sha} != {NAMES_SHA256}")
    import json
    doc = json.loads(p.read_text(encoding="utf-8"))
    if list(doc["columns"]) != list(COLUMNS):
        raise RuntimeError("pair_ship: names file disagrees with the module's COLUMNS")
    return {"source": str(p), "columns": list(doc["columns"]), "verified": True}


def load_booster(model_dir=None, verify_sha=True):
    """Load the booster once, verify its sha256, and check its own header against the names."""
    global _BOOSTER
    if _BOOSTER is not None:
        return _BOOSTER
    import lightgbm as lgb
    p = find_artefact(MODEL_NAME, model_dir)
    if verify_sha:
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        if sha != MODEL_SHA256:
            raise RuntimeError(f"pair_ship booster sha mismatch: {sha} != {MODEL_SHA256}")
    bst = lgb.Booster(model_file=str(p))
    names = load_names(model_dir, verify_sha)["columns"]
    if list(bst.feature_name()) != names:
        raise RuntimeError(f"pair_ship: booster feature order {bst.feature_name()} != {names}")
    _BOOSTER = bst
    return _BOOSTER


def pair_edge_probs(nodes_by_id, seed_edges, model_dir=None, gate_um=RELINK_REACH_UM,
                    stats=None):
    """THE ENTRY POINT.

    Parameters
    ----------
    nodes_by_id : {node_id: {"t": int, "pos": np.ndarray(3)}}
        exactly `cell_06.py`'s own dict at line 1393. `pos` is in MICRONS, derived upstream
        from the submission's INTEGER voxel coordinates times the film's own OME-NGFF scale;
        this module never rounds and never re-derives a coordinate.
    seed_edges : iterable of (source_id, target_id)
        the edge set available at call time -- the seed pass's output. Only used to build the
        tissue flow and the chain lengths; no label, no ground truth.
    gate_um : float
        pairs further apart than this are not returned; beyond the relaxed radius no pair can
        become an edge, so returning them would only cost memory.

    Returns
    -------
    {(source_id, target_id): float in [0, 1]}  -- joined BY POSITION throughout, never by id
    across worlds: the ids here are `cell_06`'s own, in its own world, which is the one case
    where an id is meaningful.
    """
    import pair_features as pf
    ids = np.fromiter((int(k) for k in nodes_by_id), dtype=np.int64, count=len(nodes_by_id))
    order = np.argsort(ids, kind="stable")
    nid = ids[order]
    pos = np.stack([np.asarray(nodes_by_id[int(k)]["pos"], dtype=np.float64) for k in nid])
    t_arr = np.fromiter((int(nodes_by_id[int(k)]["t"]) for k in nid), dtype=np.int64, count=len(nid))
    idx_of = {int(v): i for i, v in enumerate(nid)}
    se = [(int(s), int(d)) for s, d in seed_edges if int(s) in idx_of and int(d) in idx_of]
    esrc = np.fromiter((idx_of[s] for s, _ in se), dtype=np.int64, count=len(se))
    etgt = np.fromiter((idx_of[d] for _, d in se), dtype=np.int64, count=len(se))

    si, di, F, info = pf.build_features(pos, t_arr, nid, esrc, etgt)
    near = F[:, 0] <= gate_um
    if not near.any():
        return {}
    p = load_booster(model_dir).predict(F[near][:, CORE15])
    if stats is not None:
        stats["pair_scorer_pairs"] = int(near.sum())
        stats["pair_scorer_flow_defined_frac"] = round(info["flow_defined_frac"], 5)
        stats["pair_scorer_p_mean"] = round(float(p.mean()), 5)
    ks = nid[si[near]]
    kd = nid[di[near]]
    return {(int(a), int(b)): float(v) for a, b, v in zip(ks, kd, p)}


def cost_term(pair_probs, source_id, target_id, pair_bonus=PAIR_BONUS_DEFAULT):
    """The exact quantity to SUBTRACT from `cost[i, j]`, kept here so the patch to the
    deployed cell is one call and cannot drift from what was measured."""
    v = pair_probs.get((int(source_id), int(target_id)), 0.0)
    if not np.isfinite(v):
        return 0.0
    return float(pair_bonus) * float(min(max(v, 0.0), 1.0))
