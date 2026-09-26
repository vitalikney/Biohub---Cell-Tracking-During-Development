#!/usr/bin/env python3
"""Compare a produced world to a witness world by node and edge SETS.

The `id` column is a GLOBAL renumbering left to the caller by `pil_lier.world_rows`, and the
witness renumbers from 0 over its single film. Comparing ids would pass or fail for the wrong
reason. This compares:

  nodes : the set of (node_id, t, z, y, x)   -- node_id is the probmat row index on both sides
  edges : the set of (source_id, target_id)

and, as a second and independent criterion that does NOT use node_id at all, the MULTISET of
node positions (t, z, y, x) -- so a pure renumbering of node_id could not hide a real difference.

Both files may or may not carry the leading `id` column and a header; both shapes are accepted
and the shape actually seen is reported.

Usage:
  python osk_compare_worlds.py --produced <csv> --witness <csv> --film <name> --out <json>
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import subprocess
import sys

HEADER = "id,dataset,row_type,node_id,t,z,y,x,source_id,target_id"


def read_utc() -> str:
    try:
        return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "UNREAD"


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse(path: str, film: str) -> dict:
    """Return nodes, edges and the shape actually seen. Tolerates the leading id column."""
    nodes: set[tuple[int, int, int, int, int]] = set()
    positions: collections.Counter = collections.Counter()
    edges: set[tuple[int, int]] = set()
    n_lines = 0
    had_header = False
    had_id_column = None
    other_films = set()
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith("id,dataset") or line.startswith("dataset,row_type"):
                had_header = True
                continue
            n_lines += 1
            f = line.split(",")
            # 10 fields = with the leading id ; 9 fields = world_rows' own output
            if len(f) == 10:
                shape = True
                f = f[1:]
            elif len(f) == 9:
                shape = False
            else:
                raise SystemExit(f"REFUSED: {path} line has {len(f)} fields, expected 9 or 10: {line[:120]}")
            if had_id_column is None:
                had_id_column = shape
            elif had_id_column != shape:
                raise SystemExit(f"REFUSED: {path} mixes 9-field and 10-field lines")
            ds, row_type, node_id, t, z, y, x, src, tgt = f
            if ds != film:
                other_films.add(ds)
                continue
            if row_type == "node":
                key = (int(node_id), int(t), int(z), int(y), int(x))
                nodes.add(key)
                positions[(int(t), int(z), int(y), int(x))] += 1
            elif row_type == "edge":
                edges.add((int(src), int(tgt)))
            else:
                raise SystemExit(f"REFUSED: {path} unknown row_type {row_type!r}")
    return {"nodes": nodes, "positions": positions, "edges": edges,
            "n_lines": n_lines, "had_header": had_header,
            "had_id_column": bool(had_id_column), "other_films": sorted(other_films)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--produced", required=True)
    ap.add_argument("--witness", required=True)
    ap.add_argument("--film", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    p = parse(args.produced, args.film)
    w = parse(args.witness, args.film)

    nodes_only_p = sorted(p["nodes"] - w["nodes"])
    nodes_only_w = sorted(w["nodes"] - p["nodes"])
    edges_only_p = sorted(p["edges"] - w["edges"])
    edges_only_w = sorted(w["edges"] - p["edges"])
    pos_only_p = sorted((p["positions"] - w["positions"]).elements())
    pos_only_w = sorted((w["positions"] - p["positions"]).elements())

    node_set_equal = not nodes_only_p and not nodes_only_w
    edge_set_equal = not edges_only_p and not edges_only_w
    pos_multiset_equal = not pos_only_p and not pos_only_w

    verdict = ("PARITY AT THE SET LEVEL" if (node_set_equal and edge_set_equal and pos_multiset_equal)
               else "DIFFERENT")

    out = {
        "schema": "BIOCEL_RECU_V1",
        "date_u": read_utc(),
        "lane": "KERNEL",
        "question": "Does the produced world equal the witness world on node and edge SETS?",
        "film": args.film,
        "verdict": verdict,
        "criteria": {
            "node_set_equal_on_id_and_position": node_set_equal,
            "edge_set_equal": edge_set_equal,
            "position_multiset_equal_independent_of_node_id": pos_multiset_equal,
        },
        "produced": {
            "path": args.produced, "sha256": sha256_of(args.produced),
            "bytes": os.path.getsize(args.produced),
            "n_lines": p["n_lines"], "n_nodes": len(p["nodes"]), "n_edges": len(p["edges"]),
            "had_header": p["had_header"], "had_id_column": p["had_id_column"],
            "other_films_present": p["other_films"],
        },
        "witness": {
            "path": args.witness, "sha256": sha256_of(args.witness),
            "bytes": os.path.getsize(args.witness),
            "n_lines": w["n_lines"], "n_nodes": len(w["nodes"]), "n_edges": len(w["edges"]),
            "had_header": w["had_header"], "had_id_column": w["had_id_column"],
            "other_films_present": w["other_films"],
        },
        "differences": {
            "n_nodes_only_in_produced": len(nodes_only_p),
            "n_nodes_only_in_witness": len(nodes_only_w),
            "n_edges_only_in_produced": len(edges_only_p),
            "n_edges_only_in_witness": len(edges_only_w),
            "n_positions_only_in_produced": len(pos_only_p),
            "n_positions_only_in_witness": len(pos_only_w),
            "first_20_nodes_only_in_produced": nodes_only_p[:20],
            "first_20_nodes_only_in_witness": nodes_only_w[:20],
            "first_20_edges_only_in_produced": edges_only_p[:20],
            "first_20_edges_only_in_witness": edges_only_w[:20],
        },
        "what_this_does_not_establish": [
            "nothing about the SCORE of either world -- no judge was run and no GT was read",
            "nothing about the other 198 films: one film is one film",
            "the `id` column is deliberately NOT compared: it is a global renumbering and the "
            "witness renumbers from 0 over this single film",
        ],
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps({k: out[k] for k in ("verdict", "criteria", "differences")}, indent=1)[:2000])
    print(f"-> {args.out}")
    return 0 if verdict.startswith("PARITY") else 5


if __name__ == "__main__":
    sys.exit(main())
