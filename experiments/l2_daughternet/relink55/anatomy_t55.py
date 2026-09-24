"""Edge anatomy (experiments/l2_daughternet/edge_anatomy/anatomy.py, unchanged) on the tight-5.5 lab.

anatomy.py re-runs the notebook relink per video to attach pass / residual features and validates it against the
cache's ckpt; its namespace takes MOTION_RELINK_TIGHT_UM from BIOHUB_MOTION_RELINK_TIGHT_UM (the exp29 env cell does
not set it), so this wrapper exports 5.5.  To avoid the slow O(N^2) notebook loop, the relink cache <out>/relink/ is
pre-filled with anatomy.relink_rerun itself, run with the notebook relink source + KD-tree prefilter (bit-identical,
see build_t55_cache.py verify55); anatomy.relink_rerun validates every video against the 5.5 ckpt as usual.
Labels / origins / FP rates do not depend on the relink features.

    python experiments/l2_daughternet/relink55/anatomy_t55.py --workers 4
"""

from __future__ import annotations

import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "5.5"  # before anything builds a notebook namespace (children inherit)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "l2_daughternet" / "edge_anatomy"))
sys.path.insert(0, str(HERE))

CACHE = ROOT / "data_external" / "friend_a_cache_t55" / "cache" / "friend_a_b20_exp29_t55"
REPLAY_OUT = ROOT / ".public_local_cache" / "l2_replay_t55"
OUT = ROOT / ".public_local_cache" / "l2_edge_anatomy_t55"
DATA = ROOT / "biohub-cell-tracking-during-development" / "train"


def prefill(stem: str) -> dict:
    import anatomy
    import build_t55_cache as B

    anatomy.init_worker({"cache": str(CACHE), "data_dir": str(DATA), "ns_out": str(OUT / "ns")})
    ns = anatomy._W["ns"]
    if float(ns["MOTION_RELINK_TIGHT_UM"]) != 5.5:
        raise RuntimeError(f"namespace tight gate {ns['MOTION_RELINK_TIGHT_UM']} != 5.5")
    if "fast_relink" not in anatomy._W:
        exec(compile(B.fast_relink_source(), "<notebook:motion_relink_edges+kdtree>", "exec"), ns)
        anatomy._W["fast_relink"] = True
    arrays = anatomy.relink_rerun(stem, CACHE, OUT)
    return {"stem": stem, "valid": int(arrays["valid"]), "check": str(arrays["check"])}


def main() -> None:
    import argparse
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--stems", nargs="*", default=[])
    a, rest = ap.parse_known_args()
    if a.workers > 4:
        raise SystemExit("at most 4 workers")
    stems = list(a.stems) or sorted(p.stem for p in (CACHE / "ckpt").glob("*.npz"))
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        res = list(pool.map(prefill, stems, chunksize=4))
    bad = [r for r in res if not r["valid"]]
    print(f"relink prefill: {len(res)} videos, invalid vs 5.5 ckpt: {len(bad)}", flush=True)
    if bad:
        print(json.dumps(bad[:3], indent=1))
        raise SystemExit("relink rerun does not reproduce the 5.5 ckpt")
    import anatomy

    sys.argv = [sys.argv[0], "--cache", str(CACHE), "--replay-out", str(REPLAY_OUT), "--out", str(OUT),
                "--tag", "exp39_t55", "--report-dir", str(HERE), "--data-dir", str(DATA), "--workers", str(a.workers),
                *(["--stems", *a.stems] if a.stems else []), *rest]
    anatomy.main()


if __name__ == "__main__":
    main()
