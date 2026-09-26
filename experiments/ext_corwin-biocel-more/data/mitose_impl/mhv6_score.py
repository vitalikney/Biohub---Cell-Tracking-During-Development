"""MITOSE / v6 -- the INFERENCE path, and the chrono that says whether it ships.

The red team's V7: nothing outside the bank writer read a pair crop, and the
deployment population had never been named. Both are settled here.

THE DECLARED SHORTLIST, which is what makes the feature affordable. FRONT A's
full poser is 128 587 rows per film = 1 192 s of crop alone, **11,8x** the
101,33 s/film of measured T4 headroom. The shortlist is the mother's **top-6
pairs by `sum_dist_asc`** (the sum of the two mother-daughter distances,
ascending) over the poser's own mothers -- 99,1 pct of true pairs are inside the
top 6 by nearest, 0,963 for the prefilter actually used -- which is about
1 186 rows per film.

This file scores exactly that list: it reads a shortlist table (bound by the
same roles as the bank), extracts the mother crop and the pair crop for every
row, forwards the bag of `PairHead` members, and writes one parquet per film
with the mean logit and every member's own column. `--chrono-only` runs the same
path and writes NO scores: it exists to answer "how many seconds per film" before
a model exists, and it says so in its receipt.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time

import numpy as np
import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mh_data as D            # noqa: E402
import mhv6_bank as BK         # noqa: E402
import mhv6_net as NET6        # noqa: E402
import mhv6_pair_crop as PC    # noqa: E402
import mhv6_train as T6        # noqa: E402


def date_u():
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                          capture_output=True, text=True,
                          check=True).stdout.strip()


def shortlist_of(df, bound, top_pairs, top_mothers, order_column):
    """The DECLARED deployment shortlist: the top-`top_pairs` pairs of each
    mother by the sum of her two mother-daughter distances (ascending), over the
    top-`top_mothers` mothers of the film by `order_column`."""
    d1 = df[bound.get("dist_m_d1_um", "dist_m_d1_um")].to_numpy()
    d2 = df[bound.get("dist_m_d2_um", "dist_m_d2_um")].to_numpy()
    ssum = d1 + d2
    m_key = np.stack([df[bound["m_z"]].to_numpy(), df[bound["m_y"]].to_numpy(),
                      df[bound["m_x"]].to_numpy()], axis=1)
    key = [tuple(v) for v in m_key]
    order_vals = (df[order_column].to_numpy().astype(np.float64)
                  if order_column in df.columns
                  else np.zeros(df.height, dtype=np.float64))
    by_mother = {}
    for i, k in enumerate(key):
        by_mother.setdefault(k, []).append(i)
    mothers = sorted(by_mother, key=lambda k: -float(order_vals[by_mother[k][0]]))
    if top_mothers > 0:
        mothers = mothers[:top_mothers]
    keep = []
    for k in mothers:
        idx = np.array(by_mother[k], dtype=np.int64)
        idx = idx[np.argsort(ssum[idx], kind="mergesort")][:top_pairs]
        keep.extend(int(v) for v in idx)
    return np.array(sorted(keep), dtype=np.int64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop-dir", required=True)
    ap.add_argument("--csv", action="store_true")
    ap.add_argument("--zarr-dir", required=True)
    ap.add_argument("--columns", default="")
    ap.add_argument("--model", action="append", default=[],
                    help="name=path.pt, repeatable; absent = a randomly "
                         "initialised head, chrono only")
    ap.add_argument("--top-pairs", type=int, default=6)
    ap.add_argument("--top-mothers", type=int, default=0)
    ap.add_argument("--order-column", default="mother_v2_logit")
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--n-films", type=int, default=0)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--width", type=int, default=32)
    ap.add_argument("--chrono-only", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    import polars as pl
    sub, files = BK._population_files(a.pop_dir, a.csv)
    if a.n_films > 0:
        files = files[:a.n_films]
    overrides = (json.loads(pathlib.Path(a.columns).read_text(encoding="utf-8"))
                 if a.columns else None)
    bound = BK.bind_columns(BK._read_table(files[0]).columns, overrides)

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    models = []
    for spec in a.model:
        name, path = spec.split("=", 1)
        st = torch.load(path, map_location="cpu", weights_only=False)
        m = NET6.PairHead(in_channels=D.N_CHANNELS,
                          width=int(st.get("width", a.width))).to(dev)
        m.load_state_dict(st["model"])
        m.eval()
        models.append((name, m))
    if not models:
        m = NET6.PairHead(in_channels=D.N_CHANNELS, width=a.width).to(dev)
        m.eval()
        models.append(("UNTRAINED_chrono_only", m))

    out_dir = pathlib.Path(a.out_dir) if a.out_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
    per_film = []
    t_all = time.time()
    for f in files:
        film = f.stem
        df = BK._read_table(f)
        idx = shortlist_of(df, bound, a.top_pairs, a.top_mothers, a.order_column)
        reader = D.FilmReader(a.zarr_dir, film)
        import grille as G
        t0 = time.time()
        crops = np.empty((len(idx),) + T6.V6_FED_SHAPE, dtype=np.float32)
        scal = np.zeros((len(idx), NET6.PairHead.N_SCALARS), dtype=np.float32)
        keep = []
        cols = {k: df[v].to_numpy() for k, v in bound.items() if k != "film"}
        n_ref = 0
        for j, i in enumerate(idx):
            i = int(i)
            g = G.natif_vers_grille(np.array(
                [[cols["m_z"][i], cols["m_y"][i], cols["m_x"][i]],
                 [cols["d1_z"][i], cols["d1_y"][i], cols["d1_x"][i]],
                 [cols["d2_z"][i], cols["d2_y"][i], cols["d2_x"][i]]],
                dtype=np.float64))
            try:
                mc, _l1 = D.crop_from_film(reader, int(cols["t"][i]), g[0])
                pc, _l2 = PC.pair_crop_from_film(reader, int(cols["t"][i]),
                                                 g[1], g[2])
            except (PC.PairCropError, D.MitosisDataError):
                n_ref += 1
                continue
            row = np.stack([mc, pc])[None, ...]
            crops[len(keep)] = T6.plain_view(row)[0]
            scal[len(keep)] = NET6.symmetric_scalars(
                {k: (float(cols[k][i]) if k in cols else None)
                 for k in BK.SCALAR_ROLES})
            keep.append(i)
        t_crop = time.time() - t0
        n = len(keep)
        t0 = time.time()
        outs = {}
        with torch.no_grad():
            for name, m in models:
                s = np.empty(n, dtype=np.float32)
                for b in range(0, n, a.batch):
                    xb = torch.from_numpy(crops[b:min(b + a.batch, n)]).to(dev)
                    sb = torch.from_numpy(scal[b:min(b + a.batch, n)]).to(dev)
                    s[b:b + xb.shape[0]] = m(xb, sb).float().cpu().numpy()
                outs[name] = s
        t_fwd = time.time() - t0
        if out_dir and not a.chrono_only:
            cols_out = {"row": np.array(keep, dtype=np.int64)}
            for name, s in outs.items():
                cols_out["logit__" + name] = s
            cols_out["logit_mean"] = np.mean(list(outs.values()), axis=0)
            pl.DataFrame(cols_out).write_parquet(str(out_dir / (film + ".parquet")))
        per_film.append({"film": film, "rows_in_population": int(df.height),
                         "rows_in_shortlist": int(len(idx)),
                         "rows_scored": n, "rows_refused": n_ref,
                         "seconds_crop": round(t_crop, 3),
                         "seconds_forward": round(t_fwd, 3)})
        del reader

    n_films = len(per_film)
    tot_rows = sum(p["rows_scored"] for p in per_film)
    tot_crop = sum(p["seconds_crop"] for p in per_film)
    tot_fwd = sum(p["seconds_forward"] for p in per_film)
    rep = {"schema": "BIOCEL_RECU_V1", "date_u": date_u(), "lane": "MITOSE",
           "question": ("the v6 inference path on the DECLARED shortlist, and "
                        "its seconds per film"),
           "harnais": "mhv6_score.py on MIT_GPU_2", "assiette": str(sub),
           "shortlist_rule": ("top-%d pairs of each mother by the sum of her two "
                              "mother-daughter distances, ascending%s"
                              % (a.top_pairs,
                                 (", over the top-%d mothers by %s"
                                  % (a.top_mothers, a.order_column))
                                 if a.top_mothers > 0 else "")),
           "models": [n for n, _m in models],
           "device": dev, "n_films": n_films,
           "rows_scored_per_film": (round(tot_rows / max(n_films, 1), 1)),
           "seconds_crop_per_film": round(tot_crop / max(n_films, 1), 3),
           "seconds_forward_per_film_per_member":
               round(tot_fwd / max(n_films, 1) / max(len(models), 1), 3),
           "seconds_total_per_film_one_member":
               round((tot_crop + tot_fwd / max(len(models), 1))
                     / max(n_films, 1), 3),
           "t4_headroom_seconds_per_film": 101.33,
           "per_film": per_film,
           "wall_seconds": round(time.time() - t_all, 2),
           "what_this_does_not_establish": (
               "nothing about a Kaggle T4 notebook: this is an A100 pod's CPU "
               "and GPU, and the crop half is CPU-bound; and with no --model "
               "the weights are random, which times the arithmetic and not a "
               "trained head")}
    D.write_json(a.out, rep)
    print(json.dumps({k: rep[k] for k in
                      ("n_films", "rows_scored_per_film",
                       "seconds_crop_per_film",
                       "seconds_forward_per_film_per_member",
                       "seconds_total_per_film_one_member",
                       "t4_headroom_seconds_per_film")}, indent=1))


if __name__ == "__main__":
    main()
