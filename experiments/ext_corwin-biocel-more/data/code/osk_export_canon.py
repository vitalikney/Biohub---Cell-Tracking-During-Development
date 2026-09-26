#!/usr/bin/env python3
"""Turn the solver's per-film row files into the competition's submission.csv.

This is the FORMAT canon and nothing else. It adds the global `id`, writes the header the
downstream validator demands, and checks the invariants. It never reorders a solver
decision, never drops a node, never adds an edge -- « nothing runs after the selection but
the format canon ».

Contract, read off the deployed chain (notebook cell 3 HEADER, cell 11 `_EF_ENTETE`,
cell 9 schema validation) and off `pil_lier.world_rows`:
  header  : id,dataset,row_type,node_id,t,z,y,x,source_id,target_id   -- UNQUOTED
  newline : LF
  id      : 0-based running counter, GLOBAL across every film, in write order
  node_id : per film, as the solver emitted it (a probmat row index)
  rows    : nodes then edges, per film
  films   : at least one row for EVERY film named in --films

Usage:
  python osk_export_canon.py --rows-glob "out/rows_*.csv" --films films.json
                             --out /kaggle/working/submission.csv [--shape-tzyx 100,64,256,256]
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HEADER = "id,dataset,row_type,node_id,t,z,y,x,source_id,target_id"


def read_utc() -> str:
    try:
        return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "UNREAD"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows-glob", required=True)
    ap.add_argument("--films", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--shape-tzyx", default="100,64,256,256",
                    help="the dataset shape used to CHECK coordinate bounds; a row outside "
                         "it is a refusal, never a silent clamp")
    ap.add_argument("--receipt", type=Path, default=None)
    args = ap.parse_args()

    films = json.loads(args.films.read_text())
    if isinstance(films, dict):
        films = films["films"]
    films = list(films)
    tmax, zmax, ymax, xmax = (int(v) for v in args.shape_tzyx.split(","))

    paths = sorted(glob.glob(args.rows_glob))
    if not paths:
        raise SystemExit(f"REFUSED: --rows-glob {args.rows_glob!r} matched no file")

    per_film_nodes: dict[str, int] = {f: 0 for f in films}
    per_film_edges: dict[str, int] = {f: 0 for f in films}
    unknown_films: set[str] = set()
    non_integer = 0
    out_of_bounds: list[str] = []
    rid = 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="\n") as fo:
        fo.write(HEADER + "\n")
        for p in paths:
            with open(p, "r", encoding="utf-8") as fi:
                for line in fi:
                    line = line.strip()
                    if not line or line.startswith("id,dataset") or line.startswith("dataset,row_type"):
                        continue
                    f = line.split(",")
                    if len(f) != 9:
                        raise SystemExit(
                            f"REFUSED: {p} line has {len(f)} fields, world_rows emits 9: {line[:120]}")
                    ds, row_type, node_id, t, z, y, x, src, tgt = f
                    if ds not in per_film_nodes:
                        unknown_films.add(ds)
                    for v in (node_id, t, z, y, x, src, tgt):
                        # integer coordinates only -- floats did not transport (05/09)
                        if v.lstrip("-").isdigit() is False:
                            non_integer += 1
                            raise SystemExit(
                                f"REFUSED: non-integer field {v!r} in {p}: {line[:120]}")
                    if row_type == "node":
                        ti, zi, yi, xi = int(t), int(z), int(y), int(x)
                        if not (0 <= ti < tmax and 0 <= zi < zmax
                                and 0 <= yi < ymax and 0 <= xi < xmax):
                            out_of_bounds.append(line[:120])
                        per_film_nodes[ds] = per_film_nodes.get(ds, 0) + 1
                    elif row_type == "edge":
                        per_film_edges[ds] = per_film_edges.get(ds, 0) + 1
                    else:
                        raise SystemExit(f"REFUSED: unknown row_type {row_type!r} in {p}")
                    fo.write(f"{rid},{line}\n")
                    rid += 1

    missing = [f for f in films if per_film_nodes.get(f, 0) == 0]
    verdict = "CANON OK"
    if unknown_films:
        verdict = "REFUSED: rows for films not in --films"
    elif missing:
        verdict = "REFUSED: films with no node row"
    elif out_of_bounds:
        verdict = "REFUSED: coordinates outside the dataset shape"

    h = hashlib.sha256(args.out.read_bytes()).hexdigest()
    rec = {
        "schema": "BIOCEL_RECU_V1", "date_u": read_utc(), "lane": "KERNEL",
        "question": "Does the exported submission.csv satisfy the format canon?",
        "verdict": verdict,
        "out": str(args.out), "sha256": h, "bytes": args.out.stat().st_size,
        "n_rows_without_header": rid,
        "n_films_expected": len(films),
        "n_films_with_nodes": sum(1 for f in films if per_film_nodes.get(f, 0)),
        "films_missing": missing[:20],
        "unknown_films": sorted(unknown_films)[:20],
        "n_nodes_total": sum(per_film_nodes.values()),
        "n_edges_total": sum(per_film_edges.values()),
        "n_non_integer_fields": non_integer,
        "n_out_of_bounds_nodes": len(out_of_bounds),
        "first_out_of_bounds": out_of_bounds[:5],
        "header": HEADER,
        "source_files": paths,
        "what_this_does_not_establish": [
            "nothing about the SCORE: this checks a format, not a world",
            "the id column is created HERE and is a global running counter; the per-film "
            "witness worlds renumber from 0, so ids never compare across the two",
        ],
    }
    if args.receipt is not None:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        with args.receipt.open("w", encoding="utf-8", newline="\n") as fh:
            json.dump(rec, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    print(json.dumps({k: rec[k] for k in
                      ("verdict", "n_rows_without_header", "n_films_expected",
                       "n_films_with_nodes", "n_nodes_total", "n_edges_total",
                       "n_out_of_bounds_nodes", "sha256", "bytes")}, indent=1))
    return 0 if verdict == "CANON OK" else 7


if __name__ == "__main__":
    sys.exit(main())
