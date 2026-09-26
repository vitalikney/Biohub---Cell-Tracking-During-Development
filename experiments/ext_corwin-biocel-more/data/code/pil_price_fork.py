"""LIAGE / one-solver -- THE PRICED PATH: a per-node division cost inside the ILP.

One script, three cost SOURCES, and nothing else differs between them:

  * ``--fork-source constant``  every candidate carries ``ilp_division_weight``.
    This is the PLAIN world expressed as a cost vector, and it is the
    pre-registered fixed point of the head price at ``--scale 0``.
  * ``--fork-source oracle-gt`` a GT-matched true mother carries ``--oracle-cost``
    and every other candidate carries ``ilp_division_weight``. This is an AUDIT
    world -- it knows every mother by name, it can never be a submission -- and
    it exists here to prove, at the bit, that this file's solve is the pilot's
    solve (its world must hash to the pilot's ``oracle_tau0.30`` arm).
  * ``--fork-source head``      the real price:

        fork_cost(candidate) = ilp_division_weight - scale x (logit_mean - base)
                               for a candidate MATCHED to a head row by position
        fork_cost(candidate) = ilp_division_weight
                               for an unmatched candidate, which is COUNTED

    The mandate writes the price as ``-s x (logit_mean - b)``. Adding the
    deployed constant is not a different family: for s != 0,
    ``D - s(l - b) = -s(l - (b + D/s))``, so form and form-with-D span exactly
    the same two-parameter set of cost vectors and differ only in how ``b`` is
    labelled. The difference is at s = 0, where the shifted form gives every
    node the deployed ``ilp_division_weight`` and therefore reproduces the plain
    world AT THE BIT -- the fixed point the mandate itself names -- while the
    unshifted form would give every node a cost of 0 and make every fork free.
    The shifted form is the one that carries the named fixed point, so it is the
    one used, and this paragraph is the declaration of it.

THE JOIN IS BY POSITION, NEVER BY INDEX. Candidate identities are not stable
across inference runs (ZEUS ruling 2026-09-07T22:37:49Z). The key is the integer
tuple ``(t, z, y, x)`` in FULL-RESOLUTION voxels -- ``pm_coords`` multiplied by
the deployed downsample (1, 4, 4), which is exactly what the exported world
carries. Because "full resolution" and "the pm_coords convention" have been used
for two different grids in two different mailboxes, BOTH joins are computed on
every film and both counts are published; the run refuses if the join it was
told to use falls below ``--min-match-rate`` while the other one is better, and
names the two rates in the refusal.

Nothing runs after the selection but the format canon. No relink, no gap-close,
no graft, no DROP, no post-filter.
"""

from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pil_lier import (  # noqa: E402
    DEPLOYED_DOWNSAMPLE,
    DEPLOYED_PARAMS,
    GRID_DOWNSAMPLE,
    VOXEL_SCALE_UM,
    load_probmat,
    solve_with_fork_cost_vector,
    world_rows,
)

JUDGE_MATCH_UM = 7.0
KEY_COLUMNS = ("t", "z", "y", "x")


def coords_native_of(pm: dict) -> np.ndarray:
    """The exported world's own integer coordinates: pm_coords x (1, 4, 4)."""
    c = pm["coords"].astype(np.float32).copy()
    c[:, 1:] *= DEPLOYED_DOWNSAMPLE
    return c.astype(np.int64)


def read_head_table(path: Path, score_column: str) -> "object":
    import polars as pl

    df = pl.read_parquet(path)
    missing = [c for c in KEY_COLUMNS if c not in df.columns]
    if missing:
        raise SystemExit(
            f"REFUSED: head table {path} has no column(s) {missing}; columns are "
            f"{sorted(df.columns)}"
        )
    if score_column not in df.columns:
        raise SystemExit(
            f"REFUSED: head table {path} has no score column {score_column!r}; columns are "
            f"{sorted(df.columns)}"
        )
    return df


def join_by_position(df, pm: dict, score_column: str) -> dict:
    """Join a head table to the probmat candidates on the integer position key.

    Returns the per-candidate score vector (NaN where no head row matched) and
    every count the receipts need, each MEASURED here and never derived.
    """
    coords_native = coords_native_of(pm)
    coords_grid = pm["coords"].astype(np.int64)

    key_native = {(int(t), int(z), int(y), int(x)): i
                  for i, (t, z, y, x) in enumerate(coords_native)}
    key_grid = {(int(t), int(z), int(y), int(x)): i
                for i, (t, z, y, x) in enumerate(coords_grid)}

    tt = np.asarray(df["t"].to_list(), dtype=np.int64)
    zz = np.rint(np.asarray(df["z"].to_list(), dtype=np.float64)).astype(np.int64)
    yy = np.rint(np.asarray(df["y"].to_list(), dtype=np.float64)).astype(np.int64)
    xx = np.rint(np.asarray(df["x"].to_list(), dtype=np.float64)).astype(np.int64)
    sc = np.asarray(df[score_column].to_list(), dtype=np.float64)

    idx_native = np.full(tt.shape[0], -1, dtype=np.int64)
    idx_grid = np.full(tt.shape[0], -1, dtype=np.int64)
    for r in range(tt.shape[0]):
        k = (int(tt[r]), int(zz[r]), int(yy[r]), int(xx[r]))
        idx_native[r] = key_native.get(k, -1)
        idx_grid[r] = key_grid.get(k, -1)

    n_rows = int(tt.shape[0])
    hit_native = int((idx_native >= 0).sum())
    hit_grid = int((idx_grid >= 0).sum())

    n_cand = int(pm["coords"].shape[0])
    vals = np.full(n_cand, np.nan, dtype=np.float64)
    ok = idx_native >= 0
    vals[idx_native[ok]] = sc[ok]
    cand_matched = int(np.isfinite(vals).sum())

    return {
        "score_column": score_column,
        "head_rows": n_rows,
        "head_rows_joined_full_resolution": hit_native,
        "head_rows_joined_decimated_grid": hit_grid,
        "head_row_join_rate_full_resolution": (hit_native / n_rows) if n_rows else 0.0,
        "head_row_join_rate_decimated_grid": (hit_grid / n_rows) if n_rows else 0.0,
        "candidates": n_cand,
        "candidates_matched_by_position": cand_matched,
        "candidates_unmatched_by_position": n_cand - cand_matched,
        "candidate_match_rate": (cand_matched / n_cand) if n_cand else 0.0,
        "score_values": vals,
        "score_min_matched": float(np.nanmin(vals)) if cand_matched else None,
        "score_max_matched": float(np.nanmax(vals)) if cand_matched else None,
    }


def read_gt(geff: Path) -> dict:
    import zarr

    def arr(rel: str):
        for cand in (rel + "/values", rel):
            p = geff / cand
            if p.exists():
                return np.asarray(zarr.open_array(str(p), mode="r")[:])
        return None

    e = arr("edges/ids")
    return {
        "ids": np.asarray(arr("nodes/ids"), dtype=np.int64),
        "t": np.asarray(arr("nodes/props/t"), dtype=np.float64),
        "z": np.asarray(arr("nodes/props/z"), dtype=np.float64),
        "y": np.asarray(arr("nodes/props/y"), dtype=np.float64),
        "x": np.asarray(arr("nodes/props/x"), dtype=np.float64),
        "edges": np.empty((0, 2), np.int64) if e is None else np.asarray(e, np.int64).reshape(-1, 2),
    }


def true_mothers(gt: dict) -> np.ndarray:
    if gt["edges"].size == 0:
        return np.empty((0,), dtype=np.int64)
    src, cnt = np.unique(gt["edges"][:, 0], return_counts=True)
    return src[cnt >= 2]


def match_mothers_to_candidates(gt: dict, mothers: np.ndarray,
                                coords: np.ndarray) -> tuple[list[int], int]:
    """Nearest candidate at the same t within the judge's own 7 um.

    Byte-for-byte the pilot's `pil_oracle_fork_ceiling.match_to_candidates`
    (same order of operations, same tie-break by argmin), so the oracle arm of
    this file is the pilot's oracle arm.
    """
    pos_c = coords[:, 1:].astype(np.float64) * GRID_DOWNSAMPLE * VOXEL_SCALE_UM
    t_c = coords[:, 0].astype(np.int64)
    by_t: dict[int, np.ndarray] = {}
    for t in np.unique(t_c):
        by_t[int(t)] = np.flatnonzero(t_c == t)
    id_to_row = {int(v): i for i, v in enumerate(gt["ids"])}
    hits: list[int] = []
    misses = 0
    for m in mothers:
        r = id_to_row.get(int(m))
        if r is None:
            misses += 1
            continue
        t = int(round(gt["t"][r]))
        rows = by_t.get(t)
        if rows is None or rows.size == 0:
            misses += 1
            continue
        p = np.array([gt["z"][r], gt["y"][r], gt["x"][r]], dtype=np.float64) * VOXEL_SCALE_UM
        d = np.linalg.norm(pos_c[rows] - p[None, :], axis=1)
        k = int(np.argmin(d))
        if d[k] <= JUDGE_MATCH_UM:
            hits.append(int(rows[k]))
        else:
            misses += 1
    return hits, misses


def main() -> int:
    ap = argparse.ArgumentParser(description="one solver, a per-node division cost")
    ap.add_argument("--probmat-dir", required=True, type=Path)
    ap.add_argument("--films", required=True, type=Path)
    ap.add_argument("--shard", default="0::1")
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--tag", default="price")
    ap.add_argument("--timeout", type=float, default=1800.0)
    ap.add_argument("--edge-threshold", type=float, default=None,
                    help="overrides the deployed edge_candidate_threshold 0,48. This is NOT "
                         "det_threshold (0,96875): two gates, two names.")
    ap.add_argument("--max-exclusion-group", type=int, default=8)
    ap.add_argument("--fork-source", choices=("constant", "oracle-gt", "head"), required=True)
    ap.add_argument("--gt-dir", type=Path, default=None,
                    help="AUDIT ONLY: required by --fork-source oracle-gt, and optional "
                         "elsewhere to LABEL the posed forks true/false at 7 um")
    ap.add_argument("--oracle-cost", type=float, default=-5.0)
    ap.add_argument("--decoys-per-mother", type=float, default=0.0,
                    help="AUDIT ONLY, and the whole point of it: give the SAME attractive cost to "
                         "R x (kept true mothers) candidates drawn uniformly among the non-mothers, "
                         "so the priced set has precision 1/(1+R). This degrades the oracle into a "
                         "head of known precision and lets the judge say what precision is worth. "
                         "Uniform decoys are the PESSIMISTIC model: a real head's false positives "
                         "are mitosis-like and sit where a fork is plausible, so a uniform decoy "
                         "poses fewer forks than a real one would.")
    ap.add_argument("--mother-keep-fraction", type=float, default=1.0,
                    help="AUDIT ONLY: price only this fraction of the matched true mothers, so the "
                         "priced set has a known RECALL. 1,0 = the pilot's oracle.")
    ap.add_argument("--decoy-seed", type=int, default=20260908)
    ap.add_argument("--head-dir", type=Path, default=None)
    ap.add_argument("--score-column", default="logit_mean")
    ap.add_argument("--score-column-mode", choices=("fixed", "honest-fold"), default="fixed",
                    help="ZEUS ruling 2026-09-08T04:5xZ. `fixed` uses --score-column for every film: "
                         "on a TRAIN film `logit_mean` is partly SELF-SCORED, because the fold held "
                         "on 6bba was trained on 44b6's ground truth, so half of the mean has seen "
                         "the mothers of a 44b6 film. `honest-fold` prices each film with "
                         "`logit_fold_held_<embryo of that film>` -- the fold that never saw it. "
                         "That is LOEO AT MEASUREMENT TIME, not a routing at deployment: the "
                         "shippable world uses `logit_mean` with the same per-film base rule, and "
                         "both are published side by side, the honest one deciding the gates. The "
                         "per-film K-th-largest base neutralises the scale difference between folds, "
                         "because a rank inside a film does not care about an additive offset.")
    ap.add_argument("--honest-fold-prefix", default="logit_fold_held_")
    ap.add_argument("--scale", type=float, default=0.0, help="s in D - s x (logit - b)")
    ap.add_argument("--base", type=float, default=0.0, help="b in D - s x (logit - b)")
    ap.add_argument("--base-mode", choices=("fixed", "per-film-topk"), default="fixed",
                    help="`fixed` uses --base for every film -- a POOLED operating point. "
                         "`per-film-topk` sets b to the --base-k-th largest score among the "
                         "candidates of THAT film, which is GT-free, computed at inference from "
                         "the film's own predicted scores, and is NOT a routing by embryo: it "
                         "uses the film being tracked, never a label about which embryo it is. "
                         "Measured reason (receipt HEAD_RECALL_AT_K_P1_C60.json): pooled recall@380 "
                         "is 10 of 38 C60 mothers while per-film top-380 is 38 of 38 -- film-level "
                         "offset dominates the pooled ranking.")
    ap.add_argument("--base-k", type=int, default=100,
                    help="K of --base-mode per-film-topk, and the shortlist size of "
                         "--price-mode flat and of --local-tau")
    ap.add_argument("--price-mode", choices=("graded", "flat"), default="graded",
                    help="ZEUS order 05:2xZ. `graded` is D - s x (logit - b_film): a candidate near "
                         "the bottom of the shortlist gets a discount too shallow to pay for a fork "
                         "(measured: the honest K=200 shortlist HELD 16 of the 22 posable mothers "
                         "and the graded price converted only 9). `flat` is the deployable shape of "
                         "the ladder's 10 pct arm: EVERY candidate in the honest per-film top-K "
                         "carries `ilp_division_weight - --flat-discount`, everyone else carries the "
                         "scalar. No score enters the cost beyond membership of the shortlist.")
    ap.add_argument("--flat-discount", type=float, default=6.0,
                    help="D of --price-mode flat; D = 6,0 reproduces the oracle's own -5,0 cost")
    ap.add_argument("--edge-bonus-beta", type=float, default=0.0,
                    help="ARM D (Guillaume's 22nd order): for every candidate of the honest per-film "
                         "top --base-k, its TWO BEST OUT-EDGES by pm_prob (among those the tau gate "
                         "keeps) receive an extra reward -beta x sigmoid(head score of the MOTHER) on "
                         "the edge weight, beside the node fork cost. The daughters are then reserved "
                         "by the price itself instead of being left to whichever fork the solver finds "
                         "cheapest -- which is what arms B and C could not prevent. beta = 0 is the "
                         "arm's own REFUSING test: it must reproduce the graded arm AT THE BIT.")
    ap.add_argument("--local-tau", type=float, default=None,
                    help="HEAD-GATED LOCAL THRESHOLD (ZEUS order 05:2xZ): keep the global "
                         "--edge-threshold everywhere EXCEPT the OUT-EDGES of the shortlisted "
                         "candidates (the honest per-film top --base-k), which are admitted down to "
                         "this value. Those edges are already in the probmat; the graph grows by "
                         "about K x out-degree per film and the added count is published per film.")
    ap.add_argument("--min-match-rate", type=float, default=0.95,
                    help="on the HEAD ROWS: below this the run refuses rather than pricing "
                         "a fraction of the candidates it was told it would price")
    ap.add_argument("--write-posed-forks", action="store_true",
                    help="emit forks_<tag>_<shard>.csv: one line per posed fork, positions "
                         "in native voxels, labelled by the GT at 7 um when --gt-dir is given")
    args = ap.parse_args()

    if args.fork_source == "oracle-gt" and args.gt_dir is None:
        ap.error("--fork-source oracle-gt requires --gt-dir")
    if args.fork_source == "head" and args.head_dir is None:
        ap.error("--fork-source head requires --head-dir")

    params = dict(DEPLOYED_PARAMS)
    if args.edge_threshold is not None:
        params["edge_threshold"] = float(args.edge_threshold)
    params["max_exclusion_group"] = int(args.max_exclusion_group)
    deployed_division = float(params["ilp_division_weight"])

    films = json.loads(args.films.read_text())
    if isinstance(films, dict):
        films = films["films"]
    i, n = (int(v) for v in args.shard.split("::"))
    films = films[i::n]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = args.out_dir / f"rows_{args.tag}_{i}.csv"
    stats_path = args.out_dir / f"stats_{args.tag}_{i}.jsonl"
    forks_path = args.out_dir / f"forks_{args.tag}_{i}.csv"

    ff = forks_path.open("w", encoding="utf-8", newline="\n") if args.write_posed_forks else None
    with rows_path.open("w", encoding="utf-8", newline="\n") as fr, \
         stats_path.open("w", encoding="utf-8", newline="\n") as fs:
        for film in films:
            pm = load_probmat(args.probmat_dir / f"{film}.npz")
            n_cand = int(pm["coords"].shape[0])
            cost = np.full(n_cand, deployed_division, dtype=np.float64)
            join: dict = {}
            gt = None
            gt_mother_rows: list[int] = []

            if args.gt_dir is not None:
                gt = read_gt(args.gt_dir / f"{film}.geff")
                mothers = true_mothers(gt)
                gt_mother_rows, gt_misses = match_mothers_to_candidates(gt, mothers, pm["coords"])
                join["gt_mothers"] = int(mothers.size)
                join["gt_mothers_matched_7um"] = len(gt_mother_rows)
                join["gt_mothers_with_no_candidate"] = gt_misses

            if args.fork_source == "oracle-gt":
                # deterministic per film and per seed: zlib.crc32, never `hash`,
                # which is salted per interpreter run (PYTHONHASHSEED)
                rng = np.random.default_rng(
                    (int(args.decoy_seed) * 1_000_003 + zlib.crc32(film.encode("utf-8")))
                    % (2 ** 63))
                kept = sorted(int(v) for v in gt_mother_rows)
                if float(args.mother_keep_fraction) < 1.0 and kept:
                    k = int(round(len(kept) * float(args.mother_keep_fraction)))
                    kept = sorted(int(v) for v in
                                  rng.choice(np.asarray(kept), size=k, replace=False)) if k else []
                decoys: list[int] = []
                if float(args.decoys_per_mother) > 0.0 and kept:
                    n_dec = int(round(len(kept) * float(args.decoys_per_mother)))
                    pool = np.setdiff1d(np.arange(n_cand, dtype=np.int64),
                                        np.asarray(sorted(int(v) for v in gt_mother_rows),
                                                   dtype=np.int64))
                    n_dec = min(n_dec, int(pool.size))
                    if n_dec > 0:
                        decoys = sorted(int(v) for v in
                                        rng.choice(pool, size=n_dec, replace=False))
                for h in kept + decoys:
                    cost[h] = float(args.oracle_cost)
                join["priced_true_mothers"] = len(kept)
                join["priced_decoys"] = len(decoys)
                join["priced_set_precision"] = (
                    len(kept) / (len(kept) + len(decoys))) if (kept or decoys) else None
                join["mother_keep_fraction"] = float(args.mother_keep_fraction)
                join["decoys_per_mother"] = float(args.decoys_per_mother)
                join["decoy_seed"] = int(args.decoy_seed)
                join["priced_nodes"] = len(kept) + len(decoys)

            elif args.fork_source == "head":
                score_column = args.score_column
                if args.score_column_mode == "honest-fold":
                    score_column = f"{args.honest_fold_prefix}{film.split('_')[0]}"
                df = read_head_table(args.head_dir / f"{film}.parquet", score_column)
                j = join_by_position(df, pm, score_column)
                join["score_column_used"] = score_column
                join["score_column_mode"] = args.score_column_mode
                vals = j.pop("score_values")
                join.update(j)
                if (j["head_rows"] and
                        j["head_row_join_rate_full_resolution"] < float(args.min_match_rate)):
                    raise SystemExit(
                        f"REFUSED on {film}: the head table joins "
                        f"{j['head_rows_joined_full_resolution']} of {j['head_rows']} rows on the "
                        f"FULL-RESOLUTION key ({j['head_row_join_rate_full_resolution']:.4f} < "
                        f"{float(args.min_match_rate):.4f}); on the DECIMATED grid key it joins "
                        f"{j['head_rows_joined_decimated_grid']} "
                        f"({j['head_row_join_rate_decimated_grid']:.4f}). Two grids, one of them "
                        f"is the table's; this is a key mismatch, not a fact."
                    )
                ok = np.isfinite(vals)
                # the SHORTLIST: the top --base-k scored candidates of this film.
                # It is the object both `flat` and `--local-tau` act on, and its
                # size is measured here, never assumed.
                shortlist = np.zeros(n_cand, dtype=bool)
                if int(ok.sum()):
                    idx_sorted = np.argsort(-np.where(ok, vals, -np.inf), kind="stable")
                    kk = min(int(args.base_k), int(ok.sum()))
                    shortlist[idx_sorted[:kk]] = True
                join["shortlist_size"] = int(shortlist.sum())
                base = float(args.base)
                if args.base_mode == "per-film-topk":
                    scored = np.sort(vals[ok])[::-1]
                    if scored.size == 0:
                        base = 0.0   # nothing scored: `ok` is empty, nothing is priced
                    else:
                        k = min(int(args.base_k), int(scored.size))
                        base = float(scored[k - 1])
                    join["base_mode"] = "per-film-topk"
                    join["base_k"] = int(args.base_k)
                if args.price_mode == "flat":
                    cost[shortlist] = deployed_division - float(args.flat_discount)
                    join["price_mode"] = "flat"
                    join["flat_discount"] = float(args.flat_discount)
                else:
                    cost[ok] = deployed_division - float(args.scale) * (vals[ok] - base)
                    join["price_mode"] = "graded"
                join["base_used"] = base
                join["priced_nodes"] = int(ok.sum())
                join["unpriced_nodes_keep_scalar"] = int((~ok).sum())
                join["scale"] = float(args.scale)
                join["base"] = float(args.base)
                join["candidates_cheaper_than_scalar"] = int(
                    (cost < deployed_division).sum())
            else:
                join["priced_nodes"] = 0

            join["cost_min"] = float(cost.min())
            join["cost_max"] = float(cost.max())
            join["cost_below_deployed_division"] = int((cost < deployed_division).sum())

            # ARM D: the per-probmat-edge bonus, built from the shortlist.
            prob_bonus = None
            if float(args.edge_bonus_beta) != 0.0 and args.fork_source == "head":
                sc_all = np.full(n_cand, np.nan, dtype=np.float64)
                sc_all[np.isfinite(vals)] = vals[np.isfinite(vals)]
                tau_g = float(params["edge_threshold"])
                kept_e = pm["prob"] > tau_g
                if args.local_tau is not None:
                    kept_e = kept_e | ((pm["prob"] > float(args.local_tau)) & shortlist[pm["src"]])
                e_idx = np.flatnonzero(kept_e)
                e_src = pm["src"][e_idx].astype(np.int64)
                e_p = pm["prob"][e_idx].astype(np.float64)
                # two best out-edges per shortlisted source: sort by (src, -prob)
                sel = shortlist[e_src]
                e_idx, e_src, e_p = e_idx[sel], e_src[sel], e_p[sel]
                order_e = np.lexsort((-e_p, e_src))
                e_idx, e_src = e_idx[order_e], e_src[order_e]
                rank = np.zeros(e_src.shape[0], dtype=np.int64)
                if e_src.shape[0]:
                    newgrp = np.ones(e_src.shape[0], dtype=bool)
                    newgrp[1:] = e_src[1:] != e_src[:-1]
                    starts = np.flatnonzero(newgrp)
                    rank = np.arange(e_src.shape[0]) - np.repeat(
                        starts, np.diff(np.append(starts, e_src.shape[0])))
                take = e_idx[rank < 2]
                take_src = e_src[rank < 2]
                prob_bonus = np.zeros(pm["prob"].shape[0], dtype=np.float64)
                sig = 1.0 / (1.0 + np.exp(-sc_all[take_src]))
                prob_bonus[take] = float(args.edge_bonus_beta) * np.nan_to_num(sig, nan=0.0)
                join["edge_bonus_beta"] = float(args.edge_bonus_beta)
                join["edges_given_a_bonus"] = int(take.shape[0])
                join["bonus_max"] = float(prob_bonus.max()) if take.shape[0] else 0.0
                join["shortlist_sources_with_two_out_edges"] = int(
                    np.unique(take_src[rank[rank < 2] == 1]).shape[0])
            local_src = None
            if args.local_tau is not None:
                local_src = shortlist if args.fork_source == "head" else None
            res = solve_with_fork_cost_vector(
                pm, params, cost, timeout_s=args.timeout,
                local_threshold=(args.local_tau if local_src is not None else None),
                local_src=local_src, prob_bonus=prob_bonus)
            if local_src is not None:
                join["local_tau"] = float(args.local_tau)
                join["local_sources"] = int(local_src.sum())

            rec = {
                "film": film,
                "fork_source": args.fork_source,
                "edge_candidate_threshold": params["edge_threshold"],
                "det_threshold": 0.96875,
                "ilp_division_weight": deployed_division,
                "n_nodes_graph": res["n_nodes_graph"],
                "n_edges_graph": res["n_edges_graph"],
                "n_edges_graph_global_gate_only": res["n_edges_graph_global_gate_only"],
                "n_edges_added_by_local_gate": res["n_edges_added_by_local_gate"],
                "n_nodes_selected": res["n_nodes_selected"],
                "n_edges_selected": res["n_edges_selected"],
                "posed_forks": res["forks"],
                "seconds_build": round(res["seconds_build"], 3),
                "seconds_solve": round(res["seconds_solve"], 3),
                "non_optimal": res["non_optimal"],
                "trivial_solution": res["trivial_solution"],
                "solver_warnings": res["solver_warnings"],
                "n_exclusion_pairs": res["n_exclusion_pairs"],
                "n_exclusion_groups": res["n_exclusion_groups"],
                "largest_exclusion_group": res["largest_exclusion_group"],
                "node_ids_are_row_indices": res["node_ids_are_row_indices"],
                "join": join,
            }

            if ff is not None:
                coords = res["coords_native"]
                sel = res["selected_edges"]
                children: dict[int, list[int]] = {}
                for u, v in sel:
                    children.setdefault(int(u), []).append(int(v))
                # the GT mothers of this film, at the CANDIDATE they matched, in
                # native voxels: the label below is "did the solver pose its fork
                # on a candidate the GT calls a mother", read at the judge's 7 um.
                mother_xyz = np.empty((0, 4), dtype=np.float64)
                if gt is not None and gt_mother_rows:
                    mother_xyz = np.array(
                        [coords[r] for r in sorted(set(int(r) for r in gt_mother_rows))],
                        dtype=np.float64,
                    )
                for m in sorted(res["fork_nodes"]):
                    kids = sorted(children.get(int(m), []))[:2]
                    if len(kids) < 2:
                        continue
                    mt, mz, my, mx = (int(v) for v in coords[int(m)])
                    a = [int(v) for v in coords[kids[0]]]
                    b = [int(v) for v in coords[kids[1]]]
                    label = ""
                    if gt is not None:
                        # true = this posed mother sits within 7 um of a GT mother
                        if mother_xyz.size:
                            d = np.linalg.norm(
                                (mother_xyz[:, 1:] - np.array([mz, my, mx], dtype=np.float64))
                                * VOXEL_SCALE_UM, axis=1)
                            same_t = mother_xyz[:, 0] == mt
                            label = "true" if (same_t & (d <= JUDGE_MATCH_UM)).any() else "false"
                        else:
                            label = "false"
                    ff.write(f"{film},{mt},{mz},{my},{mx},"
                             f"{a[1]},{a[2]},{a[3]},{b[1]},{b[2]},{b[3]},{label}\n")

            rows, _, _ = world_rows(film, res)
            fr.write("\n".join(rows) + "\n")
            fs.write(json.dumps(rec) + "\n")
            fs.flush()
            print(json.dumps({k: rec[k] for k in rec if k != "solver_warnings"}), flush=True)
            if res["non_optimal"]:
                print(f"FILM FAILED LOUDLY (non-optimal solve): {film}", file=sys.stderr, flush=True)
                if ff is not None:
                    ff.close()
                return 3
    if ff is not None:
        ff.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
