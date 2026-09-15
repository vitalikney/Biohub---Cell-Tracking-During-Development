"""Collect the calibration runs of `tools/public_local.py` into one table and test the ranking against the LB.

The calibration question is not "does the local score match the LB score" - it cannot, the LB is a different
embryo and 29% of a hidden test set. It is "does the local port ORDER the four configurations the way the
leaderboard ordered them, with a comparable spread". Spearman rank correlation over four points plus the
observed spread answers that.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE = Path(__file__).resolve().parent.parent.parent / ".public_local_cache"

# Leaderboard results of probes 11-14, scored 2026-09-11 (CONTEXT.md §14 / RESULTS.md).
LB = {"exp29": 0.947, "exp30": 0.944, "exp31": 0.941, "exp32": 0.937}
WHAT = {
    "exp29": "public stack verbatim",
    "exp30": "+ PRIMARY := exp03B",
    "exp31": "+ PRIMARY := exp03B + Z-flip TTA",
    "exp32": "+ PRIMARY := exp03B + SECONDARY := exp23",
}


def load(suffix: str) -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = {}
    for tag in LB:
        for label in ("base", "tight55"):
            path = CACHE / f"{tag}{suffix}" / "pp" / f"{label}.json"
            if path.is_file():
                out.setdefault(tag, {})[label] = json.loads(path.read_text())
    return out


def spearman(a: list[float], b: list[float]) -> float:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(order):
            r[i] = float(pos)
        return r

    ra, rb = ranks(a), ranks(b)
    n = len(a)
    mean_a, mean_b = sum(ra) / n, sum(rb) / n
    num = sum((x - mean_a) * (y - mean_b) for x, y in zip(ra, rb))
    den = (sum((x - mean_a) ** 2 for x in ra) * sum((y - mean_b) ** 2 for y in rb)) ** 0.5
    return num / den if den else float("nan")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suffix", default="")
    args = ap.parse_args()

    data = load(args.suffix)
    if not data:
        raise SystemExit(f"no calibration results found under {CACHE} with suffix {args.suffix!r}")

    n_videos = len(next(iter(next(iter(data.values())).values()))["videos"])
    print(f"\nLocal calibration on {n_videos} videos (official metric) vs the leaderboard\n")
    header = f"{'tag':6s} {'LB':>6s} {'local base':>11s} {'local 5.5':>10s} {'edge':>7s} {'div_J':>7s} "\
             f"{'div TP/FP/FN':>13s}  what"
    print(header)
    print("-" * len(header))
    for tag in LB:
        runs = data.get(tag, {})
        base = runs.get("base", {}).get("summary")
        tight = runs.get("tight55", {}).get("summary")
        s = base or tight
        if s is None:
            print(f"{tag:6s} {LB[tag]:6.3f} {'-':>11s} {'-':>10s}")
            continue
        print(f"{tag:6s} {LB[tag]:6.3f} "
              f"{(base['score'] if base else float('nan')):11.4f} "
              f"{(tight['score'] if tight else float('nan')):10.4f} "
              f"{s['edge_jaccard']:7.4f} {s['division_jaccard']:7.4f} "
              f"{int(s['division_tp']):4d}/{int(s['division_fp']):4d}/{int(s['division_fn']):4d}  {WHAT[tag]}")

    for label in ("base", "tight55"):
        tags = [t for t in LB if label in data.get(t, {})]
        if len(tags) < 3:
            continue
        local = [data[t][label]["summary"]["score"] for t in tags]
        lb = [LB[t] for t in tags]
        rho = spearman(local, lb)
        inversions = [(a, b) for a, b in combinations(tags, 2)
                      if (LB[a] - LB[b]) * (data[a][label]["summary"]["score"]
                                            - data[b][label]["summary"]["score"]) < 0]
        print(f"\npost-processing '{label}': n={len(tags)} "
              f"spearman(local, LB)={rho:+.2f} "
              f"local spread={max(local) - min(local):.4f} (LB spread={max(lb) - min(lb):.3f})")
        print(f"  ranking inversions vs LB: {inversions if inversions else 'none'}")

    # The submitted configurations were not all post-processed the same way.
    as_submitted = {}
    if "tight55" in data.get("exp29", {}):
        as_submitted["exp29"] = data["exp29"]["tight55"]["summary"]["score"]
    for tag in ("exp30", "exp31", "exp32"):
        if "base" in data.get(tag, {}):
            as_submitted[tag] = data[tag]["base"]["summary"]["score"]
    if len(as_submitted) == 4:
        tags = list(as_submitted)
        rho = spearman([as_submitted[t] for t in tags], [LB[t] for t in tags])
        order = " > ".join(sorted(tags, key=lambda t: -as_submitted[t]))
        print(f"\nAS SUBMITTED (exp29 at tight 5.5, the rest at 6.0): spearman={rho:+.2f}")
        print(f"  local order: {order}")
        print(f"  LB order:    {' > '.join(sorted(LB, key=lambda t: -LB[t]))}")


if __name__ == "__main__":
    main()
