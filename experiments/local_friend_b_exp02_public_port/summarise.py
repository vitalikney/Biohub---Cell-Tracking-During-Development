"""Collect the calibration runs of `tools/public_local.py` and test the ranking against the leaderboard.

The calibration question is not "does the local score match the LB score" - it cannot, the LB is a different
embryo and 29% of a hidden test set. It is "does the local port ORDER the four configurations the way the
leaderboard ordered them". Spearman rank correlation over the four points plus the observed spread answers it.

LEAKAGE, and why this script reports three video sets instead of one
-------------------------------------------------------------------
Three of the four calibration configurations (exp30, exp31, exp32) swap in a checkpoint we fine-tuned
ourselves: exp03B as primary and exp23 as secondary. Both were fine-tuned on the 183 videos of
`experiments/_lib/holdout_split.json`, and that set contains SIX of the twelve LOEO 44b6 videos this
calibration runs on:

    seen by exp03B/exp23 : 44b6_12dfb391, 44b6_2a2eff9f, 44b6_a21120c2,
                           44b6_c50204e0, 44b6_d2f34f90, 44b6_d5e7d891
    never fine-tuned on  : 44b6_1d530831, 44b6_74d0c52e, 44b6_7a302da0,
                           44b6_87bba6c4, 44b6_9be80b04, 44b6_e28840c6

So on half the calibration set exp30/31/32 are scored on their own training data while exp29 is not, which
biases the comparison towards exactly the configurations the leaderboard placed LAST. The ranking test is only
meaningful on the six videos no fine-tune ever saw. (The pilkwang base weights saw all 199 videos, so nothing
here is absolutely clean - but that leak is identical across all four configurations, which is what a RANKING
comparison needs.)

The metric is weighted by ground-truth edge count, so subsets are re-summarised from the per-video rows rather
than averaged from the totals.
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE = ROOT / ".public_local_cache"
sys.path.insert(0, str(ROOT / "tools" / "official" / "src"))

# Leaderboard results of probes 11-14, scored 2026-09-11 (CONTEXT.md §14 / RESULTS.md).
LB = {"exp29": 0.947, "exp30": 0.944, "exp31": 0.941, "exp32": 0.937}
WHAT = {
    "exp29": "public stack verbatim",
    "exp30": "+ PRIMARY := exp03B",
    "exp31": "+ PRIMARY := exp03B + Z-flip TTA",
    "exp32": "+ PRIMARY := exp03B + SECONDARY := exp23",
}
# Videos of the LOEO 44b6 holdout that exp03B / exp23 were fine-tuned on (holdout_split.json "train").
LEAKY_FOR_FT = {"44b6_12dfb391", "44b6_2a2eff9f", "44b6_a21120c2",
                "44b6_c50204e0", "44b6_d2f34f90", "44b6_d5e7d891"}


def load(suffix: str) -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = {}
    for tag in LB:
        for path in sorted((CACHE / f"{tag}{suffix}" / "pp").glob("*.json")):
            out.setdefault(tag, {})[path.stem] = json.loads(path.read_text())
    return out


def subset_summary(run: dict, keep) -> dict | None:
    from tracking_cellmot.metrics import summarise

    rows = run.get("metric_rows")
    if not rows:
        return None
    rows = [r for r in rows if keep(r["dataset"])]
    return summarise(rows) if rows else None


def spearman(a: list[float], b: list[float]) -> float:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(order):
            r[i] = float(pos)
        return r

    ra, rb = ranks(a), ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else float("nan")


def report(data: dict, label: str, name: str, keep) -> dict[str, float]:
    scores: dict[str, float] = {}
    rows_out = []
    for tag in LB:
        run = data.get(tag, {}).get(label)
        if run is None:
            continue
        s = subset_summary(run, keep) or (run["summary"] if keep("") else None)
        if s is None:
            continue
        scores[tag] = s["score"]
        rows_out.append((tag, s))

    if not rows_out:
        return scores
    n_vid = len([r for r in data[rows_out[0][0]][label]["metric_rows"] if keep(r["dataset"])])
    print(f"\n### {name}  ({n_vid} videos, post-processing '{label}')")
    print(f"{'tag':6s} {'LB':>6s} {'local':>8s} {'edge':>8s} {'div_J':>7s} {'TP/FP/FN':>12s}  what")
    for tag, s in rows_out:
        print(f"{tag:6s} {LB[tag]:6.3f} {s['score']:8.4f} {s['edge_jaccard']:8.4f} "
              f"{s['division_jaccard']:7.4f} {int(s['division_tp']):3d}/{int(s['division_fp']):3d}/"
              f"{int(s['division_fn']):3d}  {WHAT[tag]}")
    if len(scores) >= 3:
        tags = list(scores)
        rho = spearman([scores[t] for t in tags], [LB[t] for t in tags])
        inv = [f"{a}<{b}" for a, b in combinations(tags, 2)
               if (LB[a] - LB[b]) * (scores[a] - scores[b]) < 0]
        print(f"  local order: {' > '.join(sorted(tags, key=lambda t: -scores[t]))}")
        print(f"  spearman vs LB = {rho:+.2f} | spread {max(scores.values()) - min(scores.values()):.4f} "
              f"(LB spread {max(LB[t] for t in tags) - min(LB[t] for t in tags):.3f})")
        print(f"  inversions vs LB: {', '.join(inv) if inv else 'none'}")
    return scores


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suffix", default="")
    ap.add_argument("--label", default="base")
    args = ap.parse_args()

    data = load(args.suffix)
    if not data:
        raise SystemExit(f"no calibration results found under {CACHE} with suffix {args.suffix!r}")
    if not any("metric_rows" in run for runs in data.values() for run in runs.values()):
        raise SystemExit("results predate per-video metric rows; re-score with "
                         "experiments/local_friend_b_exp02_public_port/rescore.py")

    print("LOCAL CALIBRATION of the public-pipeline port vs the leaderboard")
    print("LB ranking to reproduce: exp29 0.947 > exp30 0.944 > exp31 0.941 > exp32 0.937")

    report(data, args.label, "ALL calibration videos", lambda d: True)
    report(data, args.label, "CLEAN: never fine-tuned on by exp03B/exp23", lambda d: d not in LEAKY_FOR_FT)
    report(data, args.label, "LEAKY: inside exp03B/exp23 training data", lambda d: d in LEAKY_FOR_FT)

    print("\nRead the CLEAN block for the calibration verdict. A port that reproduces the LB order there is "
          "calibrated;\nan inversion that appears only in the LEAKY block is the fine-tune scoring on its own "
          "training data, not a port defect.")


if __name__ == "__main__":
    main()
