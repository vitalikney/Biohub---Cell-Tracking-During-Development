"""Add per-video metric rows to calibration results produced before `public_local.py` started saving them.

Re-scoring reads the post-processed `.geff` graphs that are already on disk, so this costs seconds and does
not re-run inference or post-processing.

    python experiments/local_friend_b_exp02_public_port/rescore.py [--suffix _4vid]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE = ROOT / ".public_local_cache"
sys.path.insert(0, str(ROOT / "tools"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suffix", default="")
    ap.add_argument("--data-dir", default=str(ROOT / "biohub-cell-tracking-during-development" / "train"))
    args = ap.parse_args()

    os.environ["BIOHUB_DATA_DIR"] = args.data_dir
    import score_geffs

    for result_path in sorted(CACHE.glob(f"*{args.suffix}/pp/*.json")):
        result = json.loads(result_path.read_text())
        if result.get("metric_rows"):
            print(f"{result_path}: already has rows")
            continue
        geff_dir = result_path.parent / result_path.stem
        geffs = sorted(geff_dir.glob("*.geff"))
        if not geffs:
            print(f"{result_path}: no graphs under {geff_dir}, skipping")
            continue
        summary, rows = score_geffs.score(geffs, quiet=True)
        result["summary"], result["metric_rows"] = summary, rows
        result_path.write_text(json.dumps(result, indent=2))
        print(f"{result_path}: re-scored {len(rows)} videos, score={summary['score']:.4f}")


if __name__ == "__main__":
    main()
