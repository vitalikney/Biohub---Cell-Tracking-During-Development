"""LIAGE / one-solver-pilot -- `pil_lier` : ONE solver, costs in, integer world out.

What this file is
-----------------
It rebuilds, from a probmat `.npz`, the exact graph the deployed chain hands to
`tracksdata.solvers.ILPSolver` inside `predict_unet_transformer.py` l.943-951,
runs that solver with the frozen deployed vector, and (a) compares its output to
the deployed solver's own `.geff` output when one is given -- that is the parity
witness -- and (b) exports an integer world.

The deployed facts this file reproduces, each read from a source, never recalled
  * graph construction  : `build_graph()` of the deployed
    `sortie_public_S015/tracking_repo/scripts/predict_unet_transformer.py`
    l.114-147 -- node attrs z/y/x Float64 with default -999999.0, nodes added in
    the order of `coords`, edges carrying `edge_prob` and `edge_dist` Float64.
  * candidate edges     : same file l.781-809 -- `probs[i, j] > cfg.threshold`,
    `sorted(..., reverse=True)` on the tuple `(prob, i, j)`, and NO greedy cap:
    with `use_ilp=True`, `PredictConfig.__post_init__` (l.83-90) leaves
    `max_parents_per_node` and `max_children_per_node` at None.
  * coordinates         : same file l.817-820 -- the downsampled grid coords are
    multiplied by `downsample` = (1, 4, 4) and cast back to int16. The ILP
    objective does not read coordinates, so this affects the exported world only.
  * solver call         : same file l.943-951 -- FOUR kwargs and no more:
    `edge_weight = ilp_edge_weight * EdgeAttr("edge_prob")`, `appearance_weight`,
    `disappearance_weight`, `division_weight`. Everything else is a tracksdata
    default, read in the installed package
    (`tracksdata/solvers/_ilp_solver.py` l.140-149 at 0.1.0rc6.dev3+g980c2d30a):
    node_weight 0.0, merge_weight None (merges disabled), num_threads 1,
    reset True, return_solution True, gap 0.0, timeout None.

Two traps this file refuses to fall into
----------------------------------------
  * `ILPSolver` accumulates its model across `solve()` calls (`reset_model()` is
    called only in `__init__`): ONE INSTANCE PER FILM, always.
  * `solve()` never returns its status -- it only emits `LOG.warning`. This file
    installs a handler on the `tracksdata` logger, reads the warnings back, and
    fails the film loudly on any non-optimal solve. It never uses
    `suppress_output()`.

Nothing here relinks, grafts, drops or post-filters. Canon of FORMAT only.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

import numpy as np

# The deployed downsample of the champion weights (config read from the run log:
# unet_out_channels 32, layers 32/64/128, downsample 1/4/4).
DEPLOYED_DOWNSAMPLE = np.array([1.0, 4.0, 4.0], dtype=np.float32)
# dump_edge_candidates.py:41-42, quoted verbatim by the probmat emitter
# (predict_unet_transformer.py l.267-268).
VOXEL_SCALE_UM = np.array([1.625, 0.40625, 0.40625], dtype=np.float32)
GRID_DOWNSAMPLE = np.array([1.0, 4.0, 4.0], dtype=np.float32)

# The frozen deployed scalar vector (KERNEL receipt
# 50_KERNEL/runs/20260907T2116Z__KER__deployed-sources-by-sha/recus/
# R_20260907T2127Z__deployed-solver-config.json, section B).
# `edge_threshold` 0,48 is MEASURED, not declared: see the parity receipt
# recus/R_20260907T222100Z__pilot-parity.json (two independent criteria).
DEPLOYED_PARAMS = {
    "ilp_edge_weight": -1.0,
    "ilp_appearance_weight": 0.0,
    "ilp_disappearance_weight": 1.5,
    "ilp_division_weight": 1.0,
    "ilp_node_weight": 0.0,
    "edge_threshold": 0.48,
    "max_dist_um": 0.0,   # 0 = no distance gate beyond the probmat's own 15 um
    "r_excl_um": 0.0,     # 0 = no exclusion; native overlaps, armed mode only
}


class SolverWarningCatcher(logging.Handler):
    """Reads back what `ILPSolver._solve()` only ever writes to the logger."""

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())

    @property
    def non_optimal(self) -> bool:
        """A GENUINE failure: the solver did not reach the optimum.

        `Trivial solution found with all variables set to 0!` is NOT one of
        these. It is the correct optimum of a problem whose costs make keeping
        anything more expensive than keeping nothing -- exactly what happens at
        `node_weight = +1,0`. Counting it as a failure made a legitimate
        sensitivity point look like a crash and, worse, handed an EMPTY world to
        the judge, which then stalled (measured 22:48Z: 0 CPU ticks on all
        workers for 5 minutes on a world with only a header line).
        """
        return any(
            ("did not converge" in m) or ("Failed to solve" in m)
            for m in self.messages
        )

    @property
    def trivial_solution(self) -> bool:
        return any("Trivial solution" in m for m in self.messages)


def load_probmat(path: Path) -> dict:
    z = np.load(path)
    return {
        "coords": z["pm_coords"],
        "src": z["pm_src"],
        "tgt": z["pm_tgt"],
        "prob": z["pm_prob"],
        "gate_um": float(z["pm_gate_um"]),
        "schema": str(z["pm_schema"]),
    }


def candidate_edges(
    pm: dict, edge_threshold: float, max_dist_um: float = 0.0,
    local_threshold: float | None = None, local_src: np.ndarray | None = None,
    prob_bonus: np.ndarray | None = None,
) -> list[tuple[int, int, float, float]]:
    """The deployed candidate set, in the deployed ORDER.

    Deployed loop (predict_unet_transformer.py l.781-809): per frame pair, the
    surviving pairs are `sorted([(prob, i, j) ...], reverse=True)` -- descending
    on prob, then on the LOCAL source index, then on the LOCAL target index --
    and appended in that order, with no cap when the ILP is on. Since the local
    offsets are constant within a frame pair, ordering on the global indices is
    the same ordering. Frame pairs come in increasing t.

    Edge INSERTION ORDER matters: it fixes the ilpy variable indices, hence how
    ties in the objective are broken. This function reproduces it.
    """
    coords = pm["coords"]
    src = pm["src"]
    tgt = pm["tgt"]
    prob = pm["prob"]
    keep = prob > edge_threshold
    if local_threshold is not None and local_src is not None:
        # HEAD-GATED LOCAL THRESHOLD (ZEUS order 2026-09-08T05:2xZ). The global
        # gate stays where it is; only the OUT-EDGES of the shortlisted
        # candidates are admitted down to `local_threshold`. Those edges are
        # already in the probmat -- nothing is invented, the gate is lifted for
        # a named, published set of sources. The graph grows by about
        # K x (out-degree) edges per film, not by the whole plate, and the count
        # is measured and published per film, never assumed.
        keep = keep | ((prob > float(local_threshold)) & local_src[src])
    s = src[keep]
    t = tgt[keep]
    p = prob[keep].astype(np.float64)
    if s.size == 0:
        return []

    t_src = coords[s, 0].astype(np.int64)  # the frame pair is keyed by t of the source
    # descending on (prob, i, j) inside a frame pair, frame pairs in increasing t
    order = np.lexsort((-t.astype(np.int64), -s.astype(np.int64), -p, t_src))

    pos = coords[:, 1:].astype(np.float32) * GRID_DOWNSAMPLE * VOXEL_SCALE_UM
    d = np.linalg.norm(pos[s[order]] - pos[t[order]], axis=1)

    if max_dist_um and max_dist_um > 0.0:
        # a TIGHTER gate than the probmat's own 15 um; it can only remove
        # candidates, never add any (the probmat cannot be widened here)
        keep_d = d <= float(max_dist_um)
        order = order[keep_d]
        d = d[keep_d]

    p_out = p[order]
    if prob_bonus is not None:
        # ARM D (Guillaume's 22nd order). The deployed objective term is
        # `ilp_edge_weight x EdgeAttr("edge_prob")` with ilp_edge_weight = -1,0,
        # so an edge contributes -prob. Adding a REWARD -beta x sigmoid(score) to
        # that edge is arithmetically the same as handing the solver
        # `edge_prob + beta x sigmoid(score)`. It is done that way on purpose:
        # the deployed kwarg stays LITERALLY the deployed one, and the bonus is
        # added AFTER the lexsort, so the edge INSERTION ORDER -- which fixes the
        # ilpy variable indices and hence every tie-break -- is untouched. At
        # beta = 0 the world is therefore bit-identical, and that is the arm's
        # own refusing test.
        b = np.asarray(prob_bonus, dtype=np.float64)
        if b.shape[0] != prob.shape[0]:
            raise SystemExit(
                f"REFUSED: prob_bonus has {b.shape[0]} entries for {prob.shape[0]} probmat edges")
        p_out = p_out + b[keep][order]
    return [
        (int(a), int(b_), float(c), float(dist))
        for a, b_, c, dist in zip(s[order], t[order], p_out, d, strict=True)
    ]


def logit_cost(p: np.ndarray, floor: float = 1e-6) -> np.ndarray:
    """-logit(p), clipped so a probability of 0 or 1 does not become an infinite
    cost. A pinned candidate is expressed as an +-inf pin on the weight
    expression, never as a large finite cost (design note, A4)."""
    q = np.clip(np.asarray(p, dtype=np.float64), floor, 1.0 - floor)
    return -np.log(q / (1.0 - q))


def load_scores(path: Path | None, coords_native: np.ndarray,
                min_match_rate: float = 0.95) -> dict:
    """ARMED MODE. Read the learned score table of one film and join it to the
    probmat rows BY POSITION.

    Schema, read on the delivered file (not declared):
      long format, one row per object, `kind` in {node, edge, fork};
      keys `k_i` / `k_src` / `k_tgt` / `k_a` / `k_b`, `k_t`;
      **coordinates `k_z_vox` / `k_y_vox` / `k_x_vox` in FULL-RESOLUTION voxels**
      (the world convention, not the decimated grid);
      node rows carry `score_birth`, `score_death`, `score_loeo`,
      `score_node_near`, `score_world`.

    The join is by POSITION -- the integer key (t, z, y, x) in full-resolution
    voxels, which is what `coords_native` holds -- and never by candidate index:
    candidate identities are not stable across inference runs (a one-bit logit
    change relocates 22 pct of candidates by ~1,6 um; ZEUS ruling 22:37:49Z).
    `k_i` IS also present, so the two joins are compared and their AGREEMENT is
    published: a position join that disagrees with the index join on tables built
    from these very probmats would mean one of the two is wrong.

    WHICH TERMS ARE ARMED IS A MEASUREMENT, NOT A PREFERENCE. The scorers lane's
    own pre-registered figures (22:50:08Z) fired on node (AUC 0,572 / 0,620
    against a 0,90 bar), on edge (AP 0,0641 / 0,0134 BELOW `pm_prob` alone at
    0,1084 / 0,0140) and on fork (AP 7,9e-05 / 6,6e-05). Only birth and death
    beat their base rate by 10x to 38x. So this loader exposes every column, and
    the caller arms birth and death; arming the edge term with a scorer measured
    to be worse than the network would be a choice against the measurement.
    """
    out: dict = {"armed": False, "path": None if path is None else str(path)}
    if path is None or not path.exists():
        return out
    import polars as pl

    df = pl.read_parquet(path).filter(pl.col("kind") == "node")
    n = coords_native.shape[0]
    key = {(int(t), int(z), int(y), int(x)): i
           for i, (t, z, y, x) in enumerate(coords_native)}

    # CODE REVIEW #11 -- `armed` used to be set to True HERE, on nothing but a
    # readable parquet, before any row had joined and before any term had armed.
    # A table joining zero rows then produced `armed: true, armed_terms: []` and
    # a solve bit-identical to the disarmed one, and no receipt could tell
    # "the learned costs did nothing" from "the learned costs were never
    # applied". `armed` is now a READING of the join, set after it, below.
    out["columns"] = sorted(df.columns)
    out["rows_node"] = int(df.height)

    idx = np.full(df.height, -1, dtype=np.int64)
    for r, (t, z, y, x) in enumerate(zip(df["k_t"], df["k_z_vox"], df["k_y_vox"], df["k_x_vox"],
                                         strict=True)):
        idx[r] = key.get((int(t), int(round(float(z))), int(round(float(y))), int(round(float(x)))), -1)
    matched = int((idx >= 0).sum())
    out["matched_by_position"] = matched
    out["unmatched_by_position"] = int(df.height - matched)
    out["match_rate"] = (matched / df.height) if df.height else 0.0
    # CODE REVIEW #11, the reading and the refusal. These tables are built from
    # these very probmats, so anything under `min_match_rate` is a bug and not a
    # fact; the refusal names the two counts.
    out["armed"] = matched > 0
    out["min_match_rate"] = float(min_match_rate)
    if df.height and out["match_rate"] < float(min_match_rate):
        raise SystemExit(
            f"REFUSED: score table {path} joins {matched} of {df.height} rows by position "
            f"({out['match_rate']:.4f} < {float(min_match_rate):.4f}); a table built from this "
            f"probmat must join almost everything, so this is a key mismatch, not a fact"
        )

    if "k_i" in df.columns:
        ki = np.asarray(df["k_i"].to_list(), dtype=np.int64)
        agree = int(((idx >= 0) & (idx == ki)).sum())
        out["index_join_agrees_with_position_join"] = agree
        out["index_join_disagrees"] = int(matched - agree)

    for term, col in (("node", "score_loeo"), ("birth", "score_birth"),
                      ("death", "score_death"), ("near", "score_node_near"),
                      ("world", "score_world")):
        if col not in df.columns:
            continue
        vals = np.full(n, np.nan, dtype=np.float64)
        src = np.asarray(df[col].to_list(), dtype=np.float64)
        ok = idx >= 0
        vals[idx[ok]] = src[ok]
        out[f"p_{term}"] = vals
        out[f"nodes_without_{term}"] = int(np.isnan(vals).sum())
    return out


def node_ids_are_row_indices(node_ids) -> bool:
    """CODE REVIEW #12 -- the READING behind the claim `node_ids[k] == k`.

    That identity is load-bearing twice: the parity verdict compares the
    solver's node ids against the deployed geff's ids as if they were the same
    numbering, and `world_rows` indexes `coords[nid]` by solution node id to
    write the exported coordinates. It was asserted in a docstring
    ("That is checked here, not assumed") and checked nowhere. The failure mode
    of a tracksdata version bump is not an exception: it is a world whose every
    coordinate is shifted, still judged, still scored, only lower.

    This function is the measurement; `build_graph` raises on it, and the
    callers record its value per film so the receipt carries a reading and not
    a claim.
    """
    ids = list(int(v) for v in node_ids)
    return ids == list(range(len(ids)))


def exclusion_groups(pairs: list[tuple[int, int]]) -> tuple[list[list[int]], int]:
    """CODE REVIEW #14 -- turn overlap PAIRS into connected GROUPS (union-find).

    `largest_exclusion_group` was initialised to 0 and never assigned, so the
    receipt field was a constant zero that reads as a measurement. Design note
    A4 requires the group size to be capped and both the largest group and the
    total pair count to be published before native exclusion is used: exclusion
    expands pairwise, so one un-capped cluster of k mutually-overlapping
    candidates adds k(k-1)/2 constraints to a single film's model and arrives
    as a silent slowdown rather than an error.

    Returns (groups, largest_group_size).
    """
    parent: dict[int, int] = {}

    def find(a: int) -> int:
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in pairs:
        ra, rb = find(int(a)), find(int(b))
        if ra != rb:
            parent[ra] = rb
    groups: dict[int, list[int]] = {}
    for node in list(parent):
        groups.setdefault(find(node), []).append(node)
    out = [sorted(g) for g in groups.values()]
    largest = max((len(g) for g in out), default=0)
    return out, largest


def build_graph(coords: np.ndarray, edges: list[tuple[int, int, float, float]]):
    """VERBATIM semantics of the deployed `build_graph`
    (predict_unet_transformer.py l.114-147). Kept as its own function so a
    reader can diff it against the deployed text line by line."""
    import polars as pl
    import tracksdata as td

    graph = td.graph.InMemoryGraph()

    for key in ["z", "y", "x"]:
        graph.add_node_attr_key(key, pl.Float64, -999999.0)

    node_ids = graph.bulk_add_nodes([
        {"t": int(t), "z": float(z), "y": float(y), "x": float(x)}
        for t, z, y, x in coords
    ])
    # CODE REVIEW #12 -- checked here for real, not in a docstring.
    if not node_ids_are_row_indices(node_ids):
        raise RuntimeError(
            "InMemoryGraph did not number nodes 0..n-1: the parity verdict and every "
            "exported coordinate index `coords[nid]` depend on that identity"
        )

    if edges:
        graph.add_edge_attr_key("edge_prob", pl.Float64, 0.0)
        graph.add_edge_attr_key("edge_dist", pl.Float64, 0.0)
        graph.bulk_add_edges([
            {
                "source_id": node_ids[src],
                "target_id": node_ids[tgt],
                "edge_prob": prob,
                "edge_dist": dist,
            }
            for src, tgt, prob, dist in edges
        ])

    return graph, node_ids


def solve_one(
    pm: dict,
    params: dict,
    exclusion_pairs: list[tuple[int, int]] | None = None,
    timeout_s: float | None = None,
    scores: dict | None = None,
) -> dict:
    """Build the graph, solve it once with a FRESH ILPSolver, read the status back."""
    import tracksdata as td
    from tracksdata.solvers import ILPSolver

    edges = candidate_edges(
        pm, float(params["edge_threshold"]), float(params.get("max_dist_um", 0.0))
    )
    coords_native = pm["coords"].astype(np.float32).copy()
    coords_native[:, 1:] *= DEPLOYED_DOWNSAMPLE
    coords_native = coords_native.astype(np.int16)

    t0 = time.perf_counter()
    graph, node_ids = build_graph(coords_native, edges)
    t_build = time.perf_counter() - t0

    # ARMED MODE: learned costs replace the constants, term by term. A term with
    # no learned score keeps its deployed constant, and the receipt says which.
    armed = scores if scores is not None else {"armed": False}
    armed_terms: list[str] = []
    if armed.get("armed"):
        import polars as pl

        # cost = scale x (-logit(p)) + offset. At scale = 0 the term is exactly
        # the deployed constant carried by `offset`, so the disarmed vector is a
        # point of this space and the loop has a fixed point inside it.
        for term, deployed_default in (
            ("node", float(params.get("ilp_node_weight", 0.0))),
            ("fork", float(params["ilp_division_weight"])),
            ("birth", float(params["ilp_appearance_weight"])),
            ("death", float(params["ilp_disappearance_weight"])),
        ):
            vals = armed.get(f"p_{term}")
            if vals is None or not float(params.get(f"scale_{term}", 0.0)):
                continue
            scale = float(params[f"scale_{term}"])
            offset = float(params.get(f"offset_{term}", deployed_default))
            cost = scale * logit_cost(np.where(np.isnan(vals), 0.5, vals)) + offset
            cost = np.where(np.isnan(vals), deployed_default, cost)
            attr = f"{term}_cost"
            graph.add_node_attr_key(attr, pl.Float64, 0.0)
            graph.update_node_attrs(
                node_ids=[int(node_ids[i]) for i in range(len(cost))],
                attrs={attr: [float(v) for v in cost]},
            )
            armed_terms.append(term)

    # CODE REVIEW #14 -- groups measured and capped before the overlaps are added.
    n_excl = 0
    largest_group = 0
    n_groups = 0
    if exclusion_pairs:
        groups, largest_group = exclusion_groups(exclusion_pairs)
        n_groups = len(groups)
        cap = int(params.get("max_exclusion_group", 8))
        if cap > 0 and largest_group > cap:
            raise SystemExit(
                f"REFUSED: largest exclusion group {largest_group} > max_exclusion_group {cap} "
                f"({n_groups} groups over {len(exclusion_pairs)} pairs); pairwise expansion of "
                f"one cluster of k candidates costs k(k-1)/2 constraints"
            )
        graph.bulk_add_overlaps([[int(node_ids[a]), int(node_ids[b])] for a, b in exclusion_pairs])
        n_excl = len(exclusion_pairs)

    catcher = SolverWarningCatcher()
    logger = logging.getLogger("tracksdata")
    logger.addHandler(catcher)
    prev_level = logger.level
    logger.setLevel(logging.WARNING)

    t0 = time.perf_counter()
    if graph.num_edges() > 0:
        kw = {
            "edge_weight": float(params["ilp_edge_weight"]) * td.EdgeAttr("edge_prob"),
            "node_weight": float(params.get("ilp_node_weight", 0.0)),
            "appearance_weight": float(params["ilp_appearance_weight"]),
            "disappearance_weight": float(params["ilp_disappearance_weight"]),
            "division_weight": float(params["ilp_division_weight"]),
        }
        if "node" in armed_terms:
            kw["node_weight"] = td.NodeAttr("node_cost")
        if "fork" in armed_terms:
            kw["division_weight"] = td.NodeAttr("fork_cost")
        if "birth" in armed_terms:
            kw["appearance_weight"] = td.NodeAttr("birth_cost")
        if "death" in armed_terms:
            kw["disappearance_weight"] = td.NodeAttr("death_cost")
        solver = ILPSolver(timeout=timeout_s, **kw)  # ONE instance for THIS film
        solution = solver.solve(graph)
    else:
        solution = None
    t_solve = time.perf_counter() - t0

    logger.removeHandler(catcher)
    logger.setLevel(prev_level)

    if solution is None:
        sel_nodes = np.empty((0,), dtype=np.int64)
        sel_edges = np.empty((0, 2), dtype=np.int64)
    else:
        nd = solution.node_attrs(attr_keys=["node_id", "t", "z", "y", "x"])
        sel_nodes = np.asarray(nd["node_id"].to_list(), dtype=np.int64)
        ed = solution.edge_attrs(attr_keys=["source_id", "target_id"])
        if ed.height:
            sel_edges = np.stack(
                [
                    np.asarray(ed["source_id"].to_list(), dtype=np.int64),
                    np.asarray(ed["target_id"].to_list(), dtype=np.int64),
                ],
                axis=1,
            )
        else:
            sel_edges = np.empty((0, 2), dtype=np.int64)

    return {
        "n_nodes_graph": int(pm["coords"].shape[0]),
        "n_edges_graph": len(edges),
        "n_nodes_selected": int(sel_nodes.size),
        "n_edges_selected": int(sel_edges.shape[0]),
        "selected_nodes": sel_nodes,
        "selected_edges": sel_edges,
        "coords_native": coords_native,
        "seconds_build": t_build,
        "seconds_solve": t_solve,
        "solver_warnings": catcher.messages,
        "non_optimal": catcher.non_optimal,
        "trivial_solution": catcher.trivial_solution,
        "n_exclusion_pairs": n_excl,
        "n_exclusion_groups": n_groups,
        "largest_exclusion_group": largest_group,
        "armed_terms": armed_terms,
        # CODE REVIEW #11 -- `armed` is now the join's reading, and the join
        # counts travel with it into every receipt.
        "armed": bool(armed.get("armed")) and bool(armed_terms),
        "matched_by_position": armed.get("matched_by_position"),
        "index_join_disagrees": armed.get("index_join_disagrees"),
        "node_ids_are_row_indices": node_ids_are_row_indices(node_ids),
    }


def solve_with_fork_cost_vector(
    pm: dict,
    params: dict,
    fork_cost: np.ndarray,
    timeout_s: float | None = None,
    exclusion_pairs: list[tuple[int, int]] | None = None,
    local_threshold: float | None = None,
    local_src: np.ndarray | None = None,
    prob_bonus: np.ndarray | None = None,
) -> dict:
    """THE PRICED PATH: one solve per film with a PER-NODE division cost.

    This is the one function every priced arm goes through -- the GT oracle
    (audit only) and the mitosis head alike -- so that "oracle" and "real price"
    differ by the cost VECTOR and by nothing else in the code.

    It reproduces, deliberately and at the bit, the kwargs the pilot's
    `pil_oracle_fork_ceiling.solve_one_with_direct_fork_cost` passed:
    `edge_weight = ilp_edge_weight x EdgeAttr("edge_prob")`,
    `appearance_weight`, `disappearance_weight`,
    `division_weight = NodeAttr("fork_cost")`, `timeout` -- and no
    `node_weight` kwarg, because that path passed none and the library default
    is 0,0. That equality is not asserted, it is MEASURED: the fixed-point
    receipt of this run re-solves the pilot's oracle arm through this function
    and compares the exported world's sha256 against the pilot's own.

    What it adds over that path, and only that:
      * the #12 node-id identity, raised in `build_graph` and read back here;
      * the #14 exclusion groups, measured and capped;
      * the fork-cost vector's own descriptive counters, so no figure about
        "how many nodes were priced" is ever derived from something else.
    """
    import polars as pl
    import tracksdata as td
    from tracksdata.solvers import ILPSolver

    edges = candidate_edges(
        pm, float(params["edge_threshold"]), float(params.get("max_dist_um", 0.0)),
        local_threshold=local_threshold, local_src=local_src, prob_bonus=prob_bonus,
    )
    n_edges_global_only = len(candidate_edges(
        pm, float(params["edge_threshold"]), float(params.get("max_dist_um", 0.0))
    )) if local_threshold is not None else len(edges)
    coords_native = pm["coords"].astype(np.float32).copy()
    coords_native[:, 1:] *= DEPLOYED_DOWNSAMPLE
    coords_native = coords_native.astype(np.int16)

    t0 = time.perf_counter()
    graph, node_ids = build_graph(coords_native, edges)
    t_build = time.perf_counter() - t0

    cost = np.asarray(fork_cost, dtype=np.float64)
    if cost.shape[0] != pm["coords"].shape[0]:
        raise SystemExit(
            f"REFUSED: fork cost vector has {cost.shape[0]} entries for "
            f"{pm['coords'].shape[0]} candidates"
        )
    if not np.all(np.isfinite(cost)):
        raise SystemExit(
            f"REFUSED: {int((~np.isfinite(cost)).sum())} non-finite entries in the fork cost "
            f"vector; a pin is an +-inf on the weight expression, never a cost"
        )
    graph.add_node_attr_key("fork_cost", pl.Float64, 0.0)
    graph.update_node_attrs(
        node_ids=[int(node_ids[k]) for k in range(cost.shape[0])],
        attrs={"fork_cost": [float(v) for v in cost]},
    )

    n_excl = 0
    n_groups = 0
    largest_group = 0
    if exclusion_pairs:
        groups, largest_group = exclusion_groups(exclusion_pairs)
        n_groups = len(groups)
        cap = int(params.get("max_exclusion_group", 8))
        if cap > 0 and largest_group > cap:
            raise SystemExit(
                f"REFUSED: largest exclusion group {largest_group} > max_exclusion_group {cap} "
                f"({n_groups} groups over {len(exclusion_pairs)} pairs)"
            )
        graph.bulk_add_overlaps([[int(node_ids[a]), int(node_ids[b])] for a, b in exclusion_pairs])
        n_excl = len(exclusion_pairs)

    catcher = SolverWarningCatcher()
    logger = logging.getLogger("tracksdata")
    logger.addHandler(catcher)
    prev_level = logger.level
    logger.setLevel(logging.WARNING)

    t0 = time.perf_counter()
    if graph.num_edges() > 0:
        solver = ILPSolver(
            edge_weight=float(params["ilp_edge_weight"]) * td.EdgeAttr("edge_prob"),
            appearance_weight=float(params["ilp_appearance_weight"]),
            disappearance_weight=float(params["ilp_disappearance_weight"]),
            division_weight=td.NodeAttr("fork_cost"),
            timeout=timeout_s,
        )
        solution = solver.solve(graph)
    else:
        solution = None
    t_solve = time.perf_counter() - t0

    logger.removeHandler(catcher)
    logger.setLevel(prev_level)

    if solution is None:
        sel_nodes = np.empty((0,), dtype=np.int64)
        sel_edges = np.empty((0, 2), dtype=np.int64)
    else:
        nd = solution.node_attrs(attr_keys=["node_id"])
        sel_nodes = np.asarray(nd["node_id"].to_list(), dtype=np.int64)
        ed = solution.edge_attrs(attr_keys=["source_id", "target_id"])
        if ed.height:
            sel_edges = np.stack(
                [np.asarray(ed["source_id"].to_list(), dtype=np.int64),
                 np.asarray(ed["target_id"].to_list(), dtype=np.int64)],
                axis=1,
            )
        else:
            sel_edges = np.empty((0, 2), dtype=np.int64)

    # posed forks: a SELECTED node with two or more selected out-edges. Measured
    # on the solution, never derived from the cost vector.
    forks: list[int] = []
    if sel_edges.size:
        u, c = np.unique(sel_edges[:, 0], return_counts=True)
        forks = [int(v) for v in u[c >= 2]]

    return {
        "n_nodes_graph": int(pm["coords"].shape[0]),
        "n_edges_graph": len(edges),
        "n_edges_graph_global_gate_only": n_edges_global_only,
        "n_edges_added_by_local_gate": len(edges) - n_edges_global_only,
        "n_nodes_selected": int(sel_nodes.size),
        "n_edges_selected": int(sel_edges.shape[0]),
        "selected_nodes": sel_nodes,
        "selected_edges": sel_edges,
        "coords_native": coords_native,
        "forks": len(forks),
        "fork_nodes": forks,
        "seconds_build": t_build,
        "seconds_solve": t_solve,
        "solver_warnings": catcher.messages,
        "non_optimal": catcher.non_optimal,
        "trivial_solution": catcher.trivial_solution,
        "n_exclusion_pairs": n_excl,
        "n_exclusion_groups": n_groups,
        "largest_exclusion_group": largest_group,
        "node_ids_are_row_indices": node_ids_are_row_indices(node_ids),
    }


def read_geff_witness(geff: Path) -> dict:
    """The deployed solver's OWN output: selected nodes and selected EDGES."""
    import zarr

    def arr(rel: str):
        p = geff / rel
        if not p.exists():
            return None
        return np.asarray(zarr.open_array(str(p), mode="r")[:])

    nodes = arr("nodes/ids")
    edges = arr("edges/ids")
    return {
        "nodes": None if nodes is None else np.asarray(nodes, dtype=np.int64),
        "edges": (
            np.empty((0, 2), dtype=np.int64)
            if edges is None
            else np.asarray(edges, dtype=np.int64).reshape(-1, 2)
        ),
    }


def compare_with_witness(result: dict, witness: dict) -> dict:
    """Parity on the SOLVER'S OWN OUTPUT, by node id -- no geometric join needed.

    The node ids of the deployed geff ARE the row indices of the probmat:
    `build_graph` adds the nodes of `coords` in order into a fresh
    `InMemoryGraph`, so `node_ids[k] == k`. That is checked here, not assumed.
    """
    a_n = set(int(x) for x in result["selected_nodes"])
    b_n = set(int(x) for x in witness["nodes"])
    a_e = set((int(u), int(v)) for u, v in result["selected_edges"])
    b_e = set((int(u), int(v)) for u, v in witness["edges"])
    return {
        "nodes_pilot": len(a_n),
        "nodes_witness": len(b_n),
        "nodes_only_pilot": len(a_n - b_n),
        "nodes_only_witness": len(b_n - a_n),
        "nodes_identical": a_n == b_n,
        "edges_pilot": len(a_e),
        "edges_witness": len(b_e),
        "edges_only_pilot": len(a_e - b_e),
        "edges_only_witness": len(b_e - a_e),
        "edges_identical": a_e == b_e,
        "sample_only_witness": sorted(b_e - a_e)[:10],
        "sample_only_pilot": sorted(a_e - b_e)[:10],
    }


def world_rows(film: str, result: dict) -> tuple[list[str], int, int]:
    """The competition's ten columns, integer coordinates, nodes then edges.

    Header read from the judged world /workspace/MITOSE/variantes/
    TEM_S0.15_K100000_CANON.csv : id,dataset,row_type,node_id,t,z,y,x,source_id,target_id
    `id` is left to the caller's global renumbering (canon of FORMAT).
    """
    coords = result["coords_native"]
    rows: list[str] = []
    kept = sorted(int(x) for x in result["selected_nodes"])
    for nid in kept:
        t, z, y, x = (int(v) for v in coords[nid])
        rows.append(f"{film},node,{nid},{t},{z},{y},{x},-1,-1")
    n_nodes = len(rows)
    n_edges = 0
    for u, v in sorted((int(a), int(b)) for a, b in result["selected_edges"]):
        rows.append(f"{film},edge,-1,-1,-1,-1,-1,{u},{v}")
        n_edges += 1
    return rows, n_nodes, n_edges


def main() -> int:
    ap = argparse.ArgumentParser(description="one-solver pilot: probmat -> ILP -> integer world")
    ap.add_argument("--probmat-dir", required=True, type=Path)
    ap.add_argument("--films", required=True, type=Path, help="JSON list of film stems")
    ap.add_argument("--shard", default="0::1", help="i::n slice of the film list")
    ap.add_argument("--params", type=Path, default=None, help="JSON of the <=8 scalars")
    ap.add_argument("--witness-dir", type=Path, default=None, help="deployed geff dir (parity)")
    ap.add_argument("--scores-dir", type=Path, default=None,
                    help="ARMED MODE: directory of <film>.parquet learned score tables")
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--timeout", type=float, default=600.0)
    ap.add_argument("--tag", default="run")
    args = ap.parse_args()

    params = dict(DEPLOYED_PARAMS)
    if args.params is not None:
        params.update(json.loads(args.params.read_text()))

    films = json.loads(args.films.read_text())
    if isinstance(films, dict):
        films = films["films"]
    i, n = (int(v) for v in args.shard.split("::"))
    films = films[i::n]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = args.out_dir / f"rows_{args.tag}_{i}.csv"
    stats_path = args.out_dir / f"stats_{args.tag}_{i}.jsonl"

    with rows_path.open("w", encoding="utf-8", newline="\n") as fr, \
         stats_path.open("w", encoding="utf-8", newline="\n") as fs:
        for film in films:
            pm = load_probmat(args.probmat_dir / f"{film}.npz")
            sc = None
            if args.scores_dir is not None:
                coords_native = pm["coords"].astype(np.float32).copy()
                coords_native[:, 1:] *= DEPLOYED_DOWNSAMPLE
                sc = load_scores(args.scores_dir / f"{film}.parquet",
                                 coords_native.astype(np.int64))
            res = solve_one(pm, params, timeout_s=args.timeout, scores=sc)
            rec = {
                "film": film,
                "n_nodes_graph": res["n_nodes_graph"],
                "n_edges_graph": res["n_edges_graph"],
                "n_nodes_selected": res["n_nodes_selected"],
                "n_edges_selected": res["n_edges_selected"],
                "seconds_build": round(res["seconds_build"], 3),
                "seconds_solve": round(res["seconds_solve"], 3),
                "non_optimal": res["non_optimal"],
                "trivial_solution": res["trivial_solution"],
                "solver_warnings": res["solver_warnings"],
                "edge_threshold": params["edge_threshold"],
                "armed": res["armed"],
                "armed_terms": res["armed_terms"],
                # CODE REVIEW #11 / #12 / #14 -- the readings travel with the score.
                "matched_by_position": res["matched_by_position"],
                "index_join_disagrees": res["index_join_disagrees"],
                "node_ids_are_row_indices": res["node_ids_are_row_indices"],
                "n_exclusion_pairs": res["n_exclusion_pairs"],
                "n_exclusion_groups": res["n_exclusion_groups"],
                "largest_exclusion_group": res["largest_exclusion_group"],
                "score_join": None if sc is None else {
                    k: v for k, v in sc.items()
                    if k.startswith(("matched_", "unmatched_", "nodes_without_",
                                     "index_join_", "rows_", "match_rate", "min_match_rate"))
                },
            }
            if args.witness_dir is not None:
                w = read_geff_witness(args.witness_dir / f"{film}.geff")
                rec["parity"] = compare_with_witness(res, w)
            rows, nn, ne = world_rows(film, res)
            fr.write("\n".join(rows) + "\n")
            fs.write(json.dumps(rec) + "\n")
            fs.flush()
            print(json.dumps({k: rec[k] for k in rec if k != "solver_warnings"}), flush=True)
            if res["non_optimal"]:
                print(f"FILM FAILED LOUDLY (non-optimal solve): {film}", file=sys.stderr, flush=True)
                return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
