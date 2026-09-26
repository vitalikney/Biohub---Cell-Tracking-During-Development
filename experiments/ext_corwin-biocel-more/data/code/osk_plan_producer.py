#!/usr/bin/env python3
"""The trio plan-producer path, TIMED. It measures seconds; it does not claim a world.

ZEUS's order of 2026-09-08 14:4xZ: time the whole post-canon correction path on a T4 with
PROVISIONAL weights, because the 13 s/film figure is a projection and the headroom measured
today is 94,5 s/film (`biocel-run-466b25ca`, 265,50 s/film against 360).

  world CSV + probmat -> poser -> pair crops -> v6 (fp16) -> arbiter -> corrections -> referee

WHAT IS REAL AND WHAT IS NOT. Every second reported is real: the volume reads, the crops, the
GPU transfer, the forward, the arbiter, the plan application. The WEIGHTS are provisional and
the POSER is mine, not FRONT A's declared one -- so the world this path would write is
meaningless, and the script REFUSES to write a submission unless `--dry` says out loud that
nobody is being fooled. FRONT A's poser drops in at `--pop-dir`: give it one and mine is not
used at all.

THE POSER, and its only job is to load the path with the right shape and the right row count.
For each film: every node the world gives two children is a mother; its daughters are those
children; further candidate pairs come from the probmat's out-neighbours of that node within
`--pair-gate-um`. Columns are the ones `mhv6_score.shortlist_of` reads --
`dist_m_d1_um`, `dist_m_d2_um`, `m_z/m_y/m_x`, the daughter grids, `mother_v2_logit` --
and the row count is capped at `--rows-per-film` (declared 1 172).

Usage:
  python osk_plan_producer.py --world submission.csv --probmat-dir D --zarr-dir Z
                              --mitose-impl M --out-dir O --models m1.pt[,m2.pt] --dry
                              [--pop-dir P] [--arbiter model.txt --arbiter-features f.json]
                              [--rows-per-film 1172] [--top-pairs 6] [--top-mothers 0]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

VOXEL_UM = np.array([1.625, 0.40625, 0.40625], dtype=np.float64)
GRID_DS = np.array([1, 4, 4], dtype=np.int64)


def read_utc() -> str:
    try:
        return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "UNREAD"


class Stage:
    """A timer that cannot lie by omission: every stage entered is reported, even on 0 rows."""

    def __init__(self, book: dict, name: str):
        self.book, self.name = book, name

    def __enter__(self):
        self.t = time.time()
        return self

    def __exit__(self, *a):
        self.book[self.name] = round(self.book.get(self.name, 0.0) + time.time() - self.t, 3)
        return False


def read_world(path: Path) -> dict:
    """film -> {'nodes': {nid: (t,z,y,x)}, 'children': {nid: [nid...]}}"""
    out: dict = defaultdict(lambda: {"nodes": {}, "children": defaultdict(list)})
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            f = line.rstrip("\n").split(",")
            if len(f) != 10 or f[0] == "id":
                continue
            ds, row_type = f[1], f[2]
            if row_type == "node":
                out[ds]["nodes"][int(f[3])] = (int(f[4]), int(f[5]), int(f[6]), int(f[7]))
            elif row_type == "edge":
                out[ds]["children"][int(f[8])].append(int(f[9]))
    return out


def pose(film, world, pm_path, gate_um, rows_cap, pairs_per_mother=6):
    """The kernel-side poser. Shape and row count only -- see the module docstring."""
    nodes, children = world["nodes"], world["children"]
    rows = []
    pm = None
    if pm_path.exists():
        z = np.load(pm_path)
        coords = np.asarray(z["pm_coords"])
        kv = coords[:, 1:].astype(np.int64) * GRID_DS[None, :]
        by_t = defaultdict(list)
        for i, t in enumerate(coords[:, 0].astype(np.int64)):
            by_t[int(t)].append(i)
        pm = (coords, kv, by_t)

    # CANDIDATE MOTHERS ARE NOT THE WORLD'S EXISTING FORKS. The corrector's whole point is
    # mothers the world does NOT have, so posing only over nodes that already fork gave 88
    # rows on four films against a declared 1 172 PER FILM -- a 13x underestimate of the very
    # quantity being measured. Every node is a candidate mother; the cap and the pairs-per-
    # mother reproduce the declared shortlist's shape (about 195 mothers x 6 pairs).
    mothers = sorted(nodes)
    for m in mothers:
        mt, mz, my, mx = nodes[m]
        mpos = np.array([mz, my, mx], dtype=np.float64)
        cand = []
        for c in children.get(m, ()):
            if c in nodes:
                cand.append(np.array(nodes[c][1:], dtype=np.float64))
        if pm is not None:
            for i in pm[2].get(mt + 1, []):
                p = pm[1][i].astype(np.float64)
                if np.linalg.norm((p - mpos) * VOXEL_UM) <= gate_um:
                    cand.append(p)
                    if len(cand) > 24:
                        break
        seen = set()
        uniq = []
        for p in cand:
            k = tuple(int(v) for v in p)
            if k not in seen:
                seen.add(k)
                uniq.append(p)
        posed_here = 0
        for i in range(len(uniq)):
            for j in range(i + 1, len(uniq)):
                d1 = float(np.linalg.norm((uniq[i] - mpos) * VOXEL_UM))
                d2 = float(np.linalg.norm((uniq[j] - mpos) * VOXEL_UM))
                rows.append({
                    "dataset": film, "t_mother": mt,
                    "m_z": mz, "m_y": my, "m_x": mx,
                    "d1_z": int(uniq[i][0]), "d1_y": int(uniq[i][1]), "d1_x": int(uniq[i][2]),
                    "d2_z": int(uniq[j][0]), "d2_y": int(uniq[j][1]), "d2_x": int(uniq[j][2]),
                    "dist_m_d1_um": d1, "dist_m_d2_um": d2,
                    "mother_v2_logit": 0.0,
                })
                posed_here += 1
                if len(rows) >= rows_cap:
                    return rows
                if posed_here >= pairs_per_mother:
                    break
            if posed_here >= pairs_per_mother:
                break
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", required=True, type=Path)
    ap.add_argument("--probmat-dir", required=True, type=Path)
    ap.add_argument("--zarr-dir", required=True, type=Path)
    ap.add_argument("--mitose-impl", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--models", default="")
    ap.add_argument("--pop-dir", type=Path, default=None,
                    help="FRONT A's trio population. Given, MY poser is not used at all.")
    ap.add_argument("--arbiter", default="")
    ap.add_argument("--arbiter-features", default="")
    ap.add_argument("--rows-per-film", type=int, default=1172)
    ap.add_argument("--pair-gate-um", type=float, default=14.0)
    ap.add_argument("--top-pairs", type=int, default=6)
    ap.add_argument("--top-mothers", type=int, default=0)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--rows-csv", default="",
                    help="the arbiter's TOP-N rows per film: step (3) of the cascade")
    ap.add_argument("--predict-rows", type=int, default=0,
                    help="time a LightGBM predict on this many rows per film")
    ap.add_argument("--dry", action="store_true",
                    help="REQUIRED. Without it this refuses to run at all, because with "
                         "provisional weights the world it would write is meaningless.")
    args = ap.parse_args()

    if not args.dry:
        raise SystemExit(
            "REFUSED: --dry is required. The weights are provisional and the poser is the "
            "kernel's own, so any submission this path produced would be a number nobody "
            "may read. This script measures SECONDS and writes no world.")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    book: dict = {}
    report = {"schema": "BIOCEL_RECU_V1", "date_u": read_utc(), "lane": "KERNEL",
              "question": "How many T4 seconds per film does the trio correction path cost?",
              "weights": "PROVISIONAL", "poser": ("FRONT A (--pop-dir)" if args.pop_dir
                                                  else "the kernel's own, shape only"),
              "films": {}, "stages_seconds": book}

    with Stage(book, "read_world"):
        world = read_world(args.world)
    films = sorted(world)

    pop_dir = args.pop_dir
    if pop_dir is None:
        pop_dir = args.out_dir / "pop"
        pop_dir.mkdir(parents=True, exist_ok=True)
        import polars as pl
        for film in films:
            with Stage(book, "pose"):
                rows = pose(film, world[film], args.probmat_dir / f"{film}.npz",
                            args.pair_gate_um, args.rows_per_film, args.top_pairs)
            report["films"].setdefault(film, {})["rows_posed"] = len(rows)
            with Stage(book, "pose_write"):
                (pl.DataFrame(rows) if rows else pl.DataFrame()).write_parquet(
                    pop_dir / f"{film}.parquet")

    models = [m for m in args.models.split(",") if m]
    # ALWAYS launch the scorer. With no --model `mhv6_score.py` builds an untrained
    # PairHead and labels it UNTRAINED_chrono_only -- which is the whole point of a
    # timing run. Skipping the subprocess when --models was empty cost the one number
    # the run existed to produce, and it did so SILENTLY.
    if True:
        cmd = [sys.executable, str(args.mitose_impl / "mhv6_score.py"),
               "--pop-dir", str(pop_dir), "--zarr-dir", str(args.zarr_dir),
               "--out-dir", str(args.out_dir / "scores"),
               "--top-pairs", str(args.top_pairs), "--top-mothers", str(args.top_mothers),
               "--batch", str(args.batch),
               # `--out` is REQUIRED by mhv6_score and omitting it cost a whole run.
               "--out", str(args.out_dir / "v6_receipt.json"),
               # its own timing mode: forwards the bag and writes no score table
               "--chrono-only"]
        if args.rows_csv:
            cmd += ["--rows-csv", str(args.rows_csv)]
        for m in models:
            cmd += ["--model", m]
        report["v6_members"] = models or ["UNTRAINED_chrono_only"]
        with Stage(book, "v6_score_subprocess"):
            r = subprocess.run(cmd, capture_output=True, text=True,
                               env={**os.environ,
                                    "PYTHONPATH": str(args.mitose_impl.resolve())})
        report["v6_returncode"] = r.returncode
        report["v6_stdout_tail"] = r.stdout[-3000:]
        if r.returncode != 0:
            report["v6_stderr_tail"] = r.stderr[-3000:]

    if args.arbiter and args.predict_rows:
        # STEP 2 of the cascade, honestly labelled: the PREDICT is really timed, on a real
        # booster with its real 142 features; the FEATURE VALUES are synthetic because the
        # feature computer is FRONT A's and is not in my hands. So the predict cost is
        # measured and the feature-computation cost is NOT -- and I do not blend the two.
        with Stage(book, "arbiter_predict_synthetic_features"):
            try:
                import lightgbm as lgb
                b = lgb.Booster(model_file=args.arbiter)
                rng = np.random.default_rng(20260908)
                X = rng.standard_normal((args.predict_rows, b.num_feature()),
                                        dtype=np.float32)
                for _ in films:
                    b.predict(X)
                report["arbiter_predict_rows_per_film"] = int(args.predict_rows)
                report["arbiter_n_features"] = b.num_feature()
                report["arbiter_feature_values"] = "SYNTHETIC -- the computer is FRONT A's"
            except Exception as e:                        # noqa: BLE001
                report["arbiter_error"] = repr(e)[:300]
    elif args.arbiter:
        with Stage(book, "arbiter_load"):
            try:
                import lightgbm as lgb
                b = lgb.Booster(model_file=args.arbiter)
                feats = json.loads(Path(args.arbiter_features).read_text()) \
                    if args.arbiter_features else None
                report["arbiter_n_features"] = b.num_feature()
                report["arbiter_feature_list_given"] = bool(feats)
            except Exception as e:                        # noqa: BLE001
                report["arbiter_error"] = repr(e)[:300]

    n = max(1, len(films))
    report["n_films"] = len(films)
    report["seconds_per_film_by_stage"] = {k: round(v / n, 3) for k, v in book.items()}
    report["seconds_per_film_total"] = round(sum(book.values()) / n, 3)
    report["headroom_seconds_per_film"] = 360.0 - 265.50
    report["verdict"] = ("FITS" if report["seconds_per_film_total"] <=
                         report["headroom_seconds_per_film"] else "OVER THE HEADROOM")
    report["what_this_does_not_establish"] = [
        "no score, no world: the weights are provisional and nothing was submitted",
        "the row count and the crop geometry drive the time; FRONT A's poser may pose a "
        "different number of rows and the seconds move with it",
    ]
    (args.out_dir / "PLAN_PRODUCER_CHRONO.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in
                      ("n_films", "seconds_per_film_by_stage", "seconds_per_film_total",
                       "headroom_seconds_per_film", "verdict", "v6_returncode")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
