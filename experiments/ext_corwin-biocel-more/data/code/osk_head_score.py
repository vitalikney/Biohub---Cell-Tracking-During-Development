#!/usr/bin/env python3
"""Score the MITOSE v2 `sched` bag on EVERY candidate of a probmat, GT-free.

Offline the head table was a precomputed parquet built from a population that carries
GT-derived columns. A kernel has no GT and needs none: `pil_price_fork.read_head_table`
requires exactly the key columns (t, z, y, x) and the score column. This script writes
those, and nothing else.

It does NOT re-implement the head. `mh_net.py`, `mh_data.py`, `grille.py`,
`normalisation.py` and `cuisson.py` are imported VERBATIM from the MITOSE lane, so the
crop geometry, the per-frame p99 normalisation and the architecture cannot drift.

The bag arithmetic reproduces `mhv2_publish.py` l.95-109 in the same two stages and the
same dtype: mean of the 5 seeds within a fold in float64, then mean of the 2 folds. No
routing by embryo -- every candidate is scored by all ten models, which is the deployment
column `logit_mean` (LANE_RULES 0.1).

PRECISION. The published P1 table was computed under bf16 autocast on an A100. A T4 is
sm_75 and has no bf16 at all, so that arithmetic is unreachable there. `--precision`
selects fp32 (default, the most portable), fp16 or bf16, and the choice is written into
the output manifest so no reader can mistake one for another.

Usage:
  python osk_head_score.py --probmat-dir D --films F.json --bag-dir B --out-dir O
                           [--precision fp32|fp16|bf16] [--batch 256] [--device cuda]
                           [--mitose-impl DIR] [--witness-parquet P --witness-film NAME]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

SEEDS = (1, 2, 3, 4, 5)
EMBRYOS = ("44b6", "6bba")
GRID_DOWNSAMPLE = np.array([1, 4, 4], dtype=np.int64)   # pm_coords -> full-resolution voxels


def read_utc() -> str:
    try:
        return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "UNREAD"


def load_bag(bag_dir: Path, device, net_mod, data_mod):
    """Load the ten checkpoints, in a FIXED order, checking each one's declared identity."""
    import torch
    models = []
    for e in EMBRYOS:
        for s in SEEDS:
            path = bag_dir / f"h{e}_s{s}__best_held_{e}.pt"
            if not path.exists():
                raise SystemExit(f"REFUSED: missing bag member {path}")
            st = torch.load(str(path), map_location=device, weights_only=False)
            # the identity guard of mhv2_score.py l.75-89, kept: a file named for one
            # held embryo whose checkpoint declares another is a silent catastrophe.
            declared = st.get("held_embryo")
            if declared is not None and str(declared) != e:
                raise SystemExit(
                    f"REFUSED: {path.name} is named for held embryo {e!r} but its "
                    f"checkpoint declares {declared!r}")
            m = net_mod.MitosisHead(in_channels=st.get("in_channels", data_mod.N_CHANNELS),
                                    width=st.get("width", 32)).to(device)
            m.load_state_dict(st["model"])   # strict: a missing tensor raises
            m.eval()
            models.append((f"{e}_s{s}", e, m))
    return models


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probmat-dir", required=True, type=Path)
    ap.add_argument("--films", required=True, type=Path)
    ap.add_argument("--zarr-dir", required=True, type=Path)
    ap.add_argument("--bag-dir", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--mitose-impl", required=True, type=Path,
                    help="folder holding mh_net.py, mh_data.py, grille.py, normalisation.py")
    ap.add_argument("--precision", choices=("fp32", "fp16", "bf16"), default="fp32")
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--shard", default="0::1")
    ap.add_argument("--witness-parquet", type=Path, default=None,
                    help="if given, compare this film's logit_mean against the witness and "
                         "publish the divergence -- it never changes what is written")
    ap.add_argument("--witness-film", default=None)
    args = ap.parse_args()

    sys.path.insert(0, str(args.mitose_impl.resolve()))
    import torch
    import mh_data as D
    import mh_net as NET

    device = args.device
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"
    # determinism knobs: TF32 silently changes fp32 convolutions on Ampere and later,
    # and it does not exist on a T4 -- turning it OFF is what makes the two comparable.
    torch.backends.cudnn.benchmark = False
    if hasattr(torch.backends, "cuda"):
        torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False

    amp_dtype = {"fp32": None, "fp16": torch.float16, "bf16": torch.bfloat16}[args.precision]
    if amp_dtype is torch.bfloat16 and device == "cuda" and not torch.cuda.is_bf16_supported():
        raise SystemExit("REFUSED: bf16 asked for on a card that does not support it "
                         "(a T4 is sm_75). Choose fp32 or fp16 and say so in the receipt.")

    films = json.loads(args.films.read_text())
    if isinstance(films, dict):
        films = films["films"]
    i, n = (int(v) for v in args.shard.split("::"))
    films = films[i::n]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    models = load_bag(args.bag_dir, device, NET, D)
    print(f"bag: {len(models)} models loaded from {args.bag_dir}", flush=True)

    manifest = {
        "schema": "BIOCEL_HEAD_SCORE_V1",
        "date_u": read_utc(),
        "precision": args.precision,
        "device": device,
        "torch": torch.__version__,
        "cuda_device_name": (torch.cuda.get_device_name(0) if device == "cuda" else None),
        "batch": int(args.batch),
        "n_models": len(models),
        "bag_dir": str(args.bag_dir),
        "tf32_disabled": True,
        "cudnn_benchmark": False,
        "films": {},
    }

    for film in films:
        t0 = time.time()
        pm = np.load(args.probmat_dir / f"{film}.npz")
        # the key is `pm_coords`, not `coords` -- `pil_lier.load_probmat` renames it on
        # read and this script does not go through that function.
        coords = np.asarray(pm["pm_coords"])       # (n, 4) int16 : t, z, y/4, x/4
        n_cand = int(coords.shape[0])
        # full-resolution voxels -- the key pil_price_fork joins on
        kvox = coords[:, 1:].astype(np.int64) * GRID_DOWNSAMPLE[None, :]
        # the GRILLE frame crop_from_film reads: (z, (y-0.5)/2, (x-0.5)/2)
        grid = np.empty((n_cand, 3), dtype=np.float64)
        grid[:, 0] = kvox[:, 0]
        grid[:, 1] = (kvox[:, 1] - 0.5) / 2.0
        grid[:, 2] = (kvox[:, 2] - 0.5) / 2.0
        tt = coords[:, 0].astype(np.int64)

        reader = D.FilmReader(args.zarr_dir, film)
        logits = np.zeros((n_cand, len(models)), dtype=np.float64)

        order = np.argsort(tt, kind="stable")      # frame-major: the p99 cache stays small
        t_crop = 0.0
        t_fwd = 0.0
        buf: list[np.ndarray] = []
        rows: list[int] = []

        def flush():
            nonlocal t_fwd, buf, rows
            if not buf:
                return
            tf = time.time()
            x = torch.from_numpy(np.stack(buf)).to(device)
            with torch.no_grad():
                if amp_dtype is None:
                    out = [m(x).float().cpu().numpy() for _, _, m in models]
                else:
                    with torch.autocast(device, dtype=amp_dtype, enabled=(device == "cuda")):
                        out = [m(x).float().cpu().numpy() for _, _, m in models]
            for j, o in enumerate(out):
                logits[np.asarray(rows), j] = o.astype(np.float64)
            t_fwd += time.time() - tf
            buf, rows = [], []

        last_t = None
        for r in order:
            r = int(r)
            if last_t is not None and int(tt[r]) != last_t:
                flush()
                reader.keep_only(set(D.clamped_frames(int(tt[r]), reader.n_frames)))
            last_t = int(tt[r])
            tc = time.time()
            bank, _ = D.crop_from_film(reader, int(tt[r]), grid[r])
            fed = bank[:, D.Z_MARGIN:D.Z_MARGIN + D.Z_FED,
                       D.XY_MARGIN:D.XY_MARGIN + D.Y_FED,
                       D.XY_MARGIN:D.XY_MARGIN + D.X_FED]
            t_crop += time.time() - tc
            buf.append(fed)
            rows.append(r)
            if len(buf) >= args.batch:
                flush()
        flush()

        # the bag: mean of the 5 seeds inside a fold, then the mean of the 2 folds,
        # both in float64 and in that order (mhv2_publish.py l.95-109)
        per_fold = []
        for k, e in enumerate(EMBRYOS):
            cols = [j for j, (_, ee, _) in enumerate(models) if ee == e]
            per_fold.append(logits[:, cols].mean(axis=1))
        logit_mean = np.mean(np.stack(per_fold, axis=1), axis=1)

        import polars as pl
        df = pl.DataFrame({
            "dataset": [film] * n_cand,
            "t": coords[:, 0].astype(np.int32),
            "z": kvox[:, 0].astype(np.int32),
            "y": kvox[:, 1].astype(np.int32),
            "x": kvox[:, 2].astype(np.int32),
            "logit_mean": logit_mean,
            "logit_fold_held_44b6": per_fold[0],
            "logit_fold_held_6bba": per_fold[1],
        })
        out_path = args.out_dir / f"{film}.parquet"
        df.write_parquet(out_path)

        rec = {"n_candidates": n_cand, "seconds_total": round(time.time() - t0, 2),
               "seconds_crop": round(t_crop, 2), "seconds_forward": round(t_fwd, 2),
               "frames_read": int(reader.frames_read),
               "logit_mean_min": float(logit_mean.min()),
               "logit_mean_max": float(logit_mean.max())}

        if args.witness_parquet is not None and film == (args.witness_film or film):
            w = pl.read_parquet(args.witness_parquet)
            key = ["t", "z", "y", "x"]
            j = df.select(key + ["logit_mean"]).join(
                w.select(key + ["logit_mean"]), on=key, how="inner", suffix="_w")
            d = (j["logit_mean"] - j["logit_mean_w"]).to_numpy()
            a = np.abs(d)
            rec["witness"] = {
                "path": str(args.witness_parquet),
                "rows_witness": int(w.height), "rows_joined": int(j.height),
                "join_rate": (float(j.height) / float(w.height)) if w.height else None,
                "max_abs_delta": float(a.max()) if a.size else None,
                "mean_abs_delta": float(a.mean()) if a.size else None,
                "p50_abs_delta": float(np.percentile(a, 50)) if a.size else None,
                "p99_abs_delta": float(np.percentile(a, 99)) if a.size else None,
                "n_exact": int((d == 0).sum()),
                "spearman_note": "not computed here; the world is the acceptance test",
                "precision_of_this_run": args.precision,
                "precision_of_the_witness": "bf16 autocast on A100 (mhv2_score.py l.198-200)",
            }
        manifest["films"][film] = rec
        print(json.dumps({film: rec}), flush=True)

    with (args.out_dir / "HEAD_SCORE_MANIFEST.json").open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
