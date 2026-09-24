"""Laptop (CPU) runner for the K-DN kernel: the SAME kdn_core code the notebook embeds, with a DATA_DIR override.

    python experiments/l2_daughternet/kdn_train/run_local.py                 # smoke: 3 division-rich videos, 1 epoch, 2 folds
    python experiments/l2_daughternet/kdn_train/run_local.py --videos 5 --out C:/tmp/kdn
    python experiments/l2_daughternet/kdn_train/run_local.py --stems 6bba_xxx,44b6_yyy
    python experiments/l2_daughternet/kdn_train/run_local.py --extra-samples experiments/l2_daughternet/pool_samples.parquet

Every KDN_* environment knob of the notebook works here too (KDN_EPOCHS, KDN_EPOCH_SAMPLES, KDN_FOLDS, ...); the
defaults below only switch on smoke mode, point the data/work/cache directories at local paths and force CPU.
Outputs (oof.csv, oof_readout.json, folds/fold_k/{best,last}.pt, labels_summary.csv, contract_check.json) land in
--out (default: <system temp>/kdn_local), never inside the repository.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in (str(ROOT), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default=str(ROOT / "biohub-cell-tracking-during-development" / "train"))
    ap.add_argument("--out", default=str(Path(tempfile.gettempdir()) / "kdn_local"))
    ap.add_argument("--videos", type=int, default=3, help="smoke-mode video count (division-rich, both embryos)")
    ap.add_argument("--stems", default="", help="comma-separated stems (overrides --videos)")
    ap.add_argument("--full", action="store_true", help="no smoke mode: 5 folds / 30 epochs unless KDN_* say otherwise")
    ap.add_argument("--gpu", action="store_true", help="allow CUDA if present (default: CPU only)")
    ap.add_argument("--extra-samples", default="", help="KDN_EXTRA_SAMPLES: pool rows (tools/make_pool_samples.py)")
    ap.add_argument("--pool-weight", default="", help="KDN_POOL_WEIGHT (default 1.0)")
    args = ap.parse_args()

    os.environ.setdefault("KDN_SMOKE", "0" if args.full else "1")
    os.environ.setdefault("KDN_SMOKE_VIDEOS", str(args.videos))
    if args.stems:
        os.environ["KDN_STEMS"] = args.stems
    os.environ["KDN_DATA_DIR"] = args.data_dir
    os.environ["KDN_WORK_DIR"] = args.out
    os.environ.setdefault("KDN_CACHE_DIR", str(Path(args.out) / "cache"))
    if not args.gpu:
        os.environ.setdefault("KDN_GPUS", "0")
    if args.extra_samples:
        os.environ["KDN_EXTRA_SAMPLES"] = str(Path(args.extra_samples).resolve())
    if args.pool_weight:
        os.environ["KDN_POOL_WEIGHT"] = args.pool_weight

    import kdn_core

    cfg = kdn_core.config_from_env()
    kdn_core.log("[local] config:", {k: v for k, v in cfg.items() if k != "gate"})
    t0 = time.time()
    state = kdn_core.run_all(cfg)
    out = Path(args.out)
    import pandas as pd

    oof = pd.read_csv(out / "oof.csv")
    missing = [c for c in kdn_core.OOF_COLUMNS if c not in oof.columns]
    kdn_core.log(f"[local] oof.csv rows {len(oof)}, with predictions {int(oof['p_par'].notna().sum())}, "
                 f"missing columns {missing}; contract check {'PASS' if state['verify']['pass'] else 'FAIL'}; "
                 f"timing {state['timing']}; wall {time.time() - t0:.0f} s")
    if "source" in oof.columns:
        kdn_core.log("[local] oof rows by source x label:\n"
                     + oof.groupby(["source", "label"]).size().unstack(fill_value=0).to_string())
    ok = not missing and len(oof) > 0 and oof["p_par"].notna().all() and state["verify"]["pass"]
    if cfg.get("extra_samples"):
        ok = (ok and "source" in oof.columns and bool((oof["source"] == "pool").any())
              and "pool" in state["readout"].get("by_source", {}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
