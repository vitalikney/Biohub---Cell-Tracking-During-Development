"""MITOSE / v6 -- the PAIR bank: index, fill, verify. Ready to run the minute
FRONT A's loosened proposals land, and refusing to run on anything else.

A v6 row is TWO crops, not one: the mother's four-offset stack around t and the
pair's four-offset stack around t+1, oriented by `mhv6_pair_crop.py`. The bank is
therefore laid out as

    row r  ->  [ mother (4, 15, 48, 48) | pair (4, 15, 48, 48) ]  float16

which is 552 960 bytes per row, twice the node bank's 276 480.

THE THREE COMMANDS, and the discipline is the node bank's, which was proven twice
today (once by catching twelve stale shard files, once by catching a half-written
blob):

  index   draws the training rows from a trio table under a NAMED sampling rule
          and allocates the blob. It REFUSES a directory that already holds
          `shard_*.done` files -- the exact trap that cost this lane a fill at
          11:28Z.
  fill    one shard, `--shard i --n-shards n`, skipping nothing silently: a
          shard whose `.done` exists is reported as such and the caller decides.
  verify  rows claimed against the index, an all-zero-row sample, and a REFUSING
          path that must fire on a forged zero row before its PASS means
          anything.

THE SAMPLING RULE, written here so it cannot drift:
  every POSITIVE of the table (the trios the judge credits if posed);
  every `mother_is_true` negative (a real mother, the wrong pair -- 1 411 in the
  present table), because that is the class the scorer exists to separate;
  and at most `--per-film` other rows per film, STRATIFIED by the product
  `pm_prob_d1 * pm_prob_d2` in `--strata` equal-count bins, so the hard ones are
  in the bank and not only the easy background.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mh_data as D            # noqa: E402
import mhv6_pair_crop as PC    # noqa: E402

ROW_ELEMS = int(np.prod(D.BANK_SHAPE)) * 2
ROW_BYTES = ROW_ELEMS * 2
V6_ROW_SHAPE = (2,) + tuple(D.BANK_SHAPE)


class V6BankError(ValueError):
    """A named refusal of this module."""


# ---------------------------------------------------------------- the schema
#
# FRONT A's `TRIO_DUMP_A199` is the population from 2026-09-08T14:1xZ: every
# positive plus the 2 000 highest-scored negatives per film, crop-ready
# coordinates, judge-frame labels, a MANIFEST. It is written by another lane, so
# this file BINDS ITS COLUMNS BY ROLE and REFUSES a table it cannot bind rather
# than guessing: a silently missing `ranker_score` would turn the stratified
# sample into a random one and nobody would see it in a receipt.
ROLES = {
    "film": ("film", "dataset"),
    "t": ("t", "t_mother", "frame"),
    "label": ("label", "judge_label", "is_true_trio", "credited"),
    "m_z": ("m_z", "mz", "mother_z"), "m_y": ("m_y", "my", "mother_y"),
    "m_x": ("m_x", "mx", "mother_x"),
    "d1_z": ("d1_z", "d1z", "daughter1_z"),
    "d1_y": ("d1_y", "d1y", "daughter1_y"),
    "d1_x": ("d1_x", "d1x", "daughter1_x"),
    "d2_z": ("d2_z", "d2z", "daughter2_z"),
    "d2_y": ("d2_y", "d2y", "daughter2_y"),
    "d2_x": ("d2_x", "d2x", "daughter2_x"),
    "strata": ("ranker_score", "score", "arbiter_score", "lgbm_score"),
}
"""The second name of each coordinate role is FRONT A's own, read off
`TRIO_DUMP_A199/<film>.csv` at 15:2xZ (`mz,my,mx,d1z,...`): the binder learns the
dump's spelling once, here, instead of a hand-written override file that would
have to be kept in step with it."""
"""role -> the column names accepted for it, most specific first. The `strata`
role is FRONT A's RANKER SCORE: ZEUS 14:1xZ replaced the `pm_prob` product with
it, because the hardest negatives are the ones ITS ranker scores highest, and a
sample that misses those teaches the pair scorer nothing it does not know."""

OPTIONAL_ROLES = ("mother_is_true", "pm_prob_d1", "pm_prob_d2",
                  "dist_m_d1_um", "dist_m_d2_um", "sister_sep_um",
                  "symmetry", "cos_angle_at_mother", "dz_m_d1", "dz_m_d2",
                  "mother_v2_logit")

SCALAR_ROLES = ("dist_m_d1_um", "dist_m_d2_um", "pm_prob_d1", "pm_prob_d2",
                "dz_m_d1", "dz_m_d2", "sister_sep_um", "symmetry",
                "cos_angle_at_mother", "mother_v2_logit", "divergence")

SCALAR_NAMES = {
    "dist_m_d1_um": ("dist_m_d1_um", "d_m_d1"),
    "dist_m_d2_um": ("dist_m_d2_um", "d_m_d2"),
    "pm_prob_d1": ("pm_prob_d1", "prob_m_d1"),
    "pm_prob_d2": ("pm_prob_d2", "prob_m_d2"),
    "sister_sep_um": ("sister_sep_um", "sister"),
    "symmetry": ("symmetry",),
    "cos_angle_at_mother": ("cos_angle_at_mother", "cos_at_m"),
    "mother_v2_logit": ("mother_v2_logit", "head_logit"),
    "divergence": ("divergence",),
}
"""Each scalar bound by NAME across the two spellings this project has. `dz_m_d1`
and `dz_m_d2` are absent from FRONT A's dump and are COMPUTED from the
coordinates instead of silently zeroed -- the one thing a scalar block must never
do is arrive full of zeros that look like measurements."""
"""What travels into the index as the row's `scalars` block, so the trainer
never re-reads the population. Every d1/d2 pair is symmetrised INSIDE the
network (`mhv6_net.symmetric_scalars`), because the table's d1/d2 ordering is
an arbitrary candidate row index -- the red team's V13 (b)."""

STRATUM_QUOTA = (120, 60, 40, 30, 20, 10, 8, 6, 4, 2)
"""V11. An equal-count split of ten bins with an equal share each is a
UNIFORM sample wearing the word "stratified": every bin holds n/10 and gives
up 300/10, so the drawn rows reproduce the population's deciles exactly. This
quota is DECLARED and weighted to the top of the ranker's order -- 120 of the
300 from the hardest tenth, 2 from the easiest -- and it sums to 300."""


def bind_columns(cols, overrides=None):
    """{role: column} or a REFUSAL naming the role that cannot be bound and the
    columns actually present."""
    have = list(cols)
    over = dict(overrides or {})
    out = {}
    missing = []
    for role, names in ROLES.items():
        if role in over:
            if over[role] not in have:
                missing.append("%s (forced to %r)" % (role, over[role]))
            else:
                out[role] = over[role]
            continue
        hit = next((n for n in names if n in have), None)
        if hit is None:
            missing.append("%s (tried %s)" % (role, ", ".join(names)))
        else:
            out[role] = hit
    if missing:
        raise V6BankError(
            "REFUSED: cannot bind %d role(s) of FRONT A's dump: %s. Columns "
            "present: %s" % (len(missing), " ; ".join(missing), ", ".join(have)))
    for role in OPTIONAL_ROLES:
        if role in have:
            out[role] = role
    return out


def date_u():
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                          capture_output=True, text=True,
                          check=True).stdout.strip()


def _scalars_of_row(df, sc_cols, cols, i):
    """The scalar block with the NET's own key names, every value either read
    from a bound column or COMPUTED. `dz_m_d1` and `dz_m_d2` are the z gaps in
    native voxels, computed here because FRONT A's dump does not carry them."""
    out = {}
    for role in SCALAR_ROLES:
        if role in sc_cols:
            out[role] = float(sc_cols[role][i])
    out["dz_m_d1"] = float(cols["m_z"][i]) - float(cols["d1_z"][i])
    out["dz_m_d2"] = float(cols["m_z"][i]) - float(cols["d2_z"][i])
    for role in SCALAR_ROLES:
        out.setdefault(role, None)
    return out


def _pair_sep_grid(cols, i):
    """(xy, |z|) separation of the two daughters in GRID voxels.

    The trainer needs it to answer the only question that matters about the
    window: are BOTH daughters actually inside the crop the net is fed -- in xy
    AND in z. `mhv6_pair_crop` refuses an xy separation beyond its reach and has
    no z refusal at all, and sisters separate in three dimensions."""
    import grille as G
    import numpy as _np
    g = G.natif_vers_grille(_np.array(
        [[cols["d1_z"][i], cols["d1_y"][i], cols["d1_x"][i]],
         [cols["d2_z"][i], cols["d2_y"][i], cols["d2_x"][i]]],
        dtype=_np.float64))
    dz = abs(float(g[0][0] - g[1][0]))
    dy = float(g[0][1] - g[1][1])
    dx = float(g[0][2] - g[1][2])
    return [round(float((dy * dy + dx * dx) ** 0.5), 4), round(dz, 4)]


def _read_table(path):
    """One film of the population, parquet or CSV. FRONT A's dump is CSV
    (`/root/LIA/out/TRIO_DUMP_A199/<film>.csv`) and this file globbed parquet
    only -- the red team's V2."""
    import polars as pl
    p = pathlib.Path(path)
    if p.suffix == ".csv":
        return pl.read_csv(str(p), infer_schema_length=None)
    return pl.read_parquet(str(p))


def _population_files(trio_dir, csv_mode):
    root = pathlib.Path(trio_dir)
    sub = root / "films" if (root / "films").is_dir() else root
    pat = "*.csv" if csv_mode else "*.parquet"
    files = sorted(sub.glob(pat))
    if not files:
        raise V6BankError("no %s under %s" % (pat, sub))
    return sub, files


def cmd_index(a):
    import polars as pl
    out = pathlib.Path(a.bank_dir)
    stale = sorted(out.glob("shard_*.done")) if out.exists() else []
    if stale and not a.force:
        raise V6BankError(
            "REFUSED: %d shard_*.done already in %s -- a fill here would skip "
            "those shards and leave the blob half written. Delete the directory "
            "or pass --force." % (len(stale), out))
    sub, files = _population_files(a.trio_dir, a.csv)
    overrides = (json.loads(pathlib.Path(a.columns).read_text(encoding="utf-8"))
                 if a.columns else None)
    _first = _read_table(files[0])
    _first_columns = list(_first.columns)
    bound = bind_columns(_first_columns, overrides)
    films = [f.stem for f in files]
    rng = np.random.default_rng(a.seed)
    rows = []
    per_film = {}
    n_hard_on_films_without_a_positive = 0
    for film, path in zip(films, files):
        df = _read_table(path)
        if df.height == 0:
            continue
        b2 = bind_columns(df.columns, overrides)
        if b2 != bound:
            raise V6BankError(
                "REFUSED: %s binds its columns differently from the first file "
                "(%s against %s) -- one dump, one schema" % (film, b2, bound))
        lab = df[bound["label"]].to_numpy()
        if lab.dtype.kind in "SU" or lab.dtype == object:
            lab = np.array([1 if str(v).upper() in ("1", "TRUE", "PAIRED",
                                                    "CREDITED") else 0
                            for v in lab], dtype=np.int64)
        mt = ((df[bound["mother_is_true"]].to_numpy() == 1) & (lab == 0)
              if "mother_is_true" in bound
              else np.zeros(df.height, dtype=bool))
        pos = np.flatnonzero(lab == 1)
        hard = np.flatnonzero(mt)
        taken = set(int(i) for i in pos) | set(int(i) for i in hard)
        rest = np.array([i for i in range(df.height) if i not in taken],
                        dtype=np.int64)
        picked = np.empty(0, dtype=np.int64)
        if rest.size and a.per_film > 0:
            key = df[bound["strata"]].to_numpy().astype(np.float64)[rest]
            order = np.argsort(-key, kind="mergesort")
            bins = np.array_split(order, int(a.strata))
            want = int(a.per_film)
            quota = list(STRATUM_QUOTA[:len(bins)])
            if len(quota) < len(bins):
                quota += [0] * (len(bins) - len(quota))
            scale = want / max(sum(quota), 1)
            got = []
            short = 0
            for q, b in zip(quota, bins):
                k = int(round(q * scale))
                if b.size == 0 or k <= 0:
                    short += k
                    continue
                take = min(k, b.size)
                short += k - take
                got.append(rng.choice(b, size=take, replace=False))
            picked = rest[np.concatenate(got)] if got else picked
            if picked.size > want:
                picked = picked[:want]
        keep = np.concatenate([pos, hard, picked]).astype(np.int64)
        keep = np.unique(keep)
        cols = {k: df[v].to_numpy() for k, v in bound.items()
                if k not in ("film", "label")}
        sc_cols = {}
        for role, names in SCALAR_NAMES.items():
            hit = next((n for n in names if n in df.columns), None)
            if hit is not None:
                sc_cols[role] = df[hit].to_numpy()
        for i in keep:
            i = int(i)
            rows.append({
                "film": film, "embryo": film.split("_")[0], "trio": i,
                "t": int(cols["t"][i]), "label": int(lab[i]),
                "mother_is_true": int(bool(mt[i])),
                "m": [float(cols["m_z"][i]), float(cols["m_y"][i]),
                      float(cols["m_x"][i])],
                "d1": [float(cols["d1_z"][i]), float(cols["d1_y"][i]),
                       float(cols["d1_x"][i])],
                "d2": [float(cols["d2_z"][i]), float(cols["d2_y"][i]),
                       float(cols["d2_x"][i])],
                "strata_key": float(cols["strata"][i]),
                # THE EVENT, so an epoch can weigh a division once and not once
                # per wrong pair (ZEUS 14:4xZ): every trio of the same MOTHER is
                # the same event, true pair and wrong pairs together.
                "mother_key": "%s|%d|%d|%d|%d" % (
                    film, int(cols["t"][i]), int(round(float(cols["m_z"][i]))),
                    int(round(float(cols["m_y"][i]))),
                    int(round(float(cols["m_x"][i])))),
                "pair_sep_grid": _pair_sep_grid(cols, i),
                "scalars": _scalars_of_row(df, sc_cols, cols, i)})
        if pos.size == 0:
            n_hard_on_films_without_a_positive += int(hard.size)
        per_film[film] = {"n_trios": int(df.height), "n_positive": int(pos.size),
                          "n_mother_is_true": int(hard.size),
                          "n_sampled": int(picked.size), "n_kept": int(keep.size)}
    for i, r in enumerate(rows):
        r["row"] = i
    n_pos_check = int(sum(r["label"] for r in rows))
    if n_pos_check == 0:
        raise V6BankError(
            "REFUSED: the index holds %d rows and ZERO positives. A bank with "
            "no positive trains nothing and its receipt would still look "
            "plausible." % len(rows))
    out.mkdir(parents=True, exist_ok=True)
    with open(str(out / "index.jsonl"), "w", encoding="utf-8",
              newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
    n_pos = int(sum(r["label"] for r in rows))
    meta = {"schema": "BIOCEL_RECU_V1", "date_u": date_u(), "lane": "MITOSE",
            "question": "the v6 PAIR training index",
            "harnais": "mhv6_bank.py index", "assiette": a.trio_dir,
            "sampling_rule": ("every positive; every mother_is_true negative; "
                              "at most %d other rows per film, stratified by "
                              "the column bound to the `strata` role in %d "
                              "equal-count bins" % (a.per_film, a.strata)),
            "columns_bound_by_role": bound,
            "scalar_columns_bound": {k: next(
                (n for n in v if n in _first_columns) for k in [k] for v in
                [SCALAR_NAMES[k]] if any(n in _first_columns for n in v))
                for k in SCALAR_NAMES
                if any(n in _first_columns for n in SCALAR_NAMES[k])},
            "scalars_computed_here": ["dz_m_d1", "dz_m_d2"],
            "seed": a.seed, "n_films": len(per_film), "population_n": len(rows),
            "n_positive": n_pos,
            "base_rate": (n_pos / len(rows)) if rows else None,
            "row_shape": list(V6_ROW_SHAPE), "row_bytes": ROW_BYTES,
            "bank_bytes": len(rows) * ROW_BYTES,
            "stratum_quota_declared": list(STRATUM_QUOTA),
            "n_hard_negatives_on_films_without_a_positive":
                n_hard_on_films_without_a_positive,
            "per_embryo": {}, "per_film": per_film,
            "what_this_does_not_establish":
                "nothing about a model: this is a list of rows"}
    for e in sorted({r["embryo"] for r in rows}):
        sub = [r for r in rows if r["embryo"] == e]
        meta["per_embryo"][e] = {"n_rows": len(sub),
                                 "n_positive": int(sum(r["label"] for r in sub))}
    D.write_json(out / "index_meta.json", meta)
    path = out / "bank.f16"
    need = len(rows) * ROW_BYTES
    if not path.exists() or path.stat().st_size != need:
        with open(str(path), "wb") as fh:
            fh.truncate(need)
    print(json.dumps({"n_rows": len(rows), "n_positive": n_pos,
                      "bank_bytes": need, "gib": round(need / 2**30, 2),
                      "per_embryo": meta["per_embryo"]}, indent=1))


def cmd_schema(a):
    """Bind FRONT A's dump BEFORE anything is drawn from it, and say in one
    receipt what was bound, what was refused, and what the file actually holds.
    This is the command that runs the minute the dump lands."""
    sub, files = _population_files(a.trio_dir, a.csv)
    df = _read_table(files[0])
    overrides = (json.loads(pathlib.Path(a.columns).read_text(encoding="utf-8"))
                 if a.columns else None)
    err = None
    bound = None
    try:
        bound = bind_columns(df.columns, overrides)
    except V6BankError as e:
        err = str(e)
    rep = {"schema": "BIOCEL_RECU_V1", "date_u": date_u(), "lane": "MITOSE",
           "question": "can this lane bind FRONT A's trio dump by role",
           "harnais": "mhv6_bank.py schema", "assiette": str(sub),
           "n_files": len(files), "first_file": files[0].name,
           "columns_present": list(df.columns),
           "dtypes": {c: str(t) for c, t in zip(df.columns, df.dtypes)},
           "rows_in_first_file": int(df.height),
           "columns_bound_by_role": bound, "refusal": err,
           "verdict": ("BOUND" if bound else "REFUSED"),
           "what_this_does_not_establish":
               "nothing about the dump's content: this reads its header"}
    D.write_json(a.out, rep)
    print(json.dumps({"verdict": rep["verdict"], "bound": bound,
                      "refusal": err, "n_files": len(files)}, indent=1))
    if err:
        raise SystemExit(4)


def _read_index(bank_dir):
    rows = [json.loads(x) for x in
            open(str(pathlib.Path(bank_dir) / "index.jsonl"), encoding="utf-8")]
    return rows


def cmd_fill(a):
    import grille as G
    bank = pathlib.Path(a.bank_dir)
    done = bank / ("shard_%d.done" % a.shard)
    if done.exists() and not a.force:
        print(json.dumps({"shard": a.shard, "state": "already_done"}))
        return
    rows = _read_index(bank)
    films = sorted({r["film"] for r in rows})
    mine = [f for i, f in enumerate(films) if i % a.n_shards == a.shard]
    mm = np.memmap(str(bank / "bank.f16"), dtype=np.float16, mode="r+",
                   shape=(len(rows),) + V6_ROW_SHAPE)
    t0 = time.time()
    written = 0
    refused = {"pair_too_wide": 0, "crop_error": 0}
    refused_rows = []
    for film in mine:
        sub = [r for r in rows if r["film"] == film]
        sub.sort(key=lambda r: r["t"])
        reader = D.FilmReader(a.zarr_dir, film)
        for r in sub:
            g = G.natif_vers_grille(np.array([r["m"], r["d1"], r["d2"]],
                                             dtype=np.float64))
            try:
                m, _lm = D.crop_from_film(reader, r["t"], g[0])
                p, _lp = PC.pair_crop_from_film(reader, r["t"], g[1], g[2])
            except PC.PairCropError as e:
                refused["pair_too_wide"] += 1
                refused_rows.append({"row": int(r["row"]), "film": film,
                                     "why": "pair_too_wide",
                                     "detail": str(e)[:200]})
                continue
            except D.MitosisDataError as e:
                refused["crop_error"] += 1
                refused_rows.append({"row": int(r["row"]), "film": film,
                                     "why": "crop_error",
                                     "detail": str(e)[:200]})
                continue
            mm[r["row"], 0] = m.astype(np.float16)
            mm[r["row"], 1] = p.astype(np.float16)
            written += 1
        del reader
    mm.flush()
    # V12: a row the fill REFUSED is named on disk, so `verify` can require
    # claimed + refused == rows instead of failing the whole 31 GiB bank on
    # one legitimately unreachable crop.
    with open(str(bank / ("refused_%d.jsonl" % a.shard)), "w",
              encoding="utf-8", newline="\n") as fh:
        for r in refused_rows:
            fh.write(json.dumps(r) + "\n")
    h = hashlib.sha256()
    for f in mine:
        for r in [x for x in rows if x["film"] == f][:8]:
            h.update(np.ascontiguousarray(mm[r["row"]]).tobytes())
    rep = {"schema": "BIOCEL_RECU_V1", "date_u": date_u(), "lane": "MITOSE",
           "n_refused_rows_named_on_disk": len(refused_rows),
           "question": "one shard of the v6 PAIR bank",
           "harnais": "mhv6_bank.py fill", "assiette": a.bank_dir,
           "shard": a.shard, "n_shards": a.n_shards, "n_films": len(mine),
           "population_n": sum(1 for r in rows if r["film"] in set(mine)),
           "written": written, "refused": refused,
           "slice_sha16": h.hexdigest()[:16],
           "seconds": round(time.time() - t0, 2),
           "what_this_does_not_establish":
               "nothing about the other shards"}
    D.write_json(done, rep)
    print(json.dumps({"shard": a.shard, "written": written, "refused": refused,
                      "seconds": rep["seconds"]}))


def cmd_verify(a):
    bank = pathlib.Path(a.bank_dir)
    rows = _read_index(bank)
    dones = sorted(bank.glob("shard_*.done"))
    claimed = 0
    for d in dones:
        claimed += int(json.loads(d.read_text(encoding="utf-8"))["written"])
    refused_ids = set()
    for f in sorted(bank.glob("refused_*.jsonl")):
        for line in open(str(f), encoding="utf-8"):
            refused_ids.add(int(json.loads(line)["row"]))
    mm = np.memmap(str(bank / "bank.f16"), dtype=np.float16, mode="r",
                   shape=(len(rows),) + V6_ROW_SHAPE)
    rng = np.random.default_rng(20260908)
    live = [i for i in range(len(rows)) if i not in refused_ids]
    take = rng.choice(live, size=min(a.sample, len(live)), replace=False)
    zero_m = 0
    zero_p = 0
    finite = True

    def sample_is_clean(idx):
        zm = zp = 0
        for i in idx:
            r = np.asarray(mm[int(i)])
            if not r[0].any():
                zm += 1
            if not r[1].any():
                zp += 1
        return zm, zp

    for i in take:
        r = np.asarray(mm[int(i)])
        if not np.all(np.isfinite(r)):
            finite = False
    zero_m, zero_p = sample_is_clean(take)
    # V12, THE REFUSING PATH FOR REAL: zero a row that IS in the sample, run
    # the same test, require it to fire, then put the row back. Testing that
    # a zero array is zero -- which is what this file did at 13:28Z -- proves
    # nothing about the blob.
    fired = False
    if take.size and mm.flags.writeable is not None:
        victim = int(take[0])
        mmw = np.memmap(str(bank / "bank.f16"), dtype=np.float16, mode="r+",
                        shape=(len(rows),) + V6_ROW_SHAPE)
        keep = np.array(mmw[victim], copy=True)
        mmw[victim] = 0
        mmw.flush()
        zm2, zp2 = sample_is_clean(take)
        fired = bool(zm2 > zero_m and zp2 > zero_p)
        mmw[victim] = keep
        mmw.flush()
        del mmw
        zm3, zp3 = sample_is_clean(take)
        fired = fired and (zm3, zp3) == (zero_m, zero_p)
    ok = (claimed + len(refused_ids) == len(rows) and zero_m == 0
          and zero_p == 0 and finite and fired)
    rep = {"schema": "BIOCEL_RECU_V1", "date_u": date_u(), "lane": "MITOSE",
           "question": "is the v6 pair bank actually filled, in both directions",
           "harnais": "mhv6_bank.py verify", "assiette": a.bank_dir,
           "rows_index": len(rows), "rows_claimed": claimed,
           "rows_refused_and_named": len(refused_ids),
           "rule": "claimed + refused must equal the index",
           "n_shards_done": len(dones), "sample_n": int(take.size),
           "n_sample_all_zero_mother_crops": zero_m,
           "n_sample_all_zero_pair_crops": zero_p,
           "sample_all_finite": bool(finite),
           "refusing_path_zeroes_a_REAL_row_and_the_test_fires": fired,
           "bank_bytes_on_disk": int((bank / "bank.f16").stat().st_size),
           "bank_bytes_expected": len(rows) * ROW_BYTES,
           "verdict": "COMPLETE" if ok else "INCOMPLETE",
           "what_this_does_not_establish":
               "nothing about the crops' content beyond being non-zero"}
    D.write_json(a.out, rep)
    print(json.dumps({k: rep[k] for k in
                      ("verdict", "rows_index", "rows_claimed",
                       "rows_refused_and_named", "n_shards_done",
                       "n_sample_all_zero_mother_crops",
                       "n_sample_all_zero_pair_crops",
                       "refusing_path_zeroes_a_REAL_row_and_the_test_fires")},
                     indent=1))
    if not ok:
        raise SystemExit(3)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("index")
    p.add_argument("--trio-dir", required=True)
    p.add_argument("--bank-dir", required=True)
    p.add_argument("--per-film", type=int, default=300)
    p.add_argument("--strata", type=int, default=10)
    p.add_argument("--columns", default="",
                   help="json {role: column} forcing part of the binding; "
                        "absent = bind by the accepted names of each role")
    p.add_argument("--csv", action="store_true",
                   help="the population is <film>.csv, not <film>.parquet -- "
                        "FRONT A's TRIO_DUMP_A199 is CSV")
    p.add_argument("--seed", type=int, default=20260908)
    p.add_argument("--force", action="store_true")
    p.set_defaults(f=cmd_index)
    p = sub.add_parser("schema")
    p.add_argument("--trio-dir", required=True)
    p.add_argument("--csv", action="store_true")
    p.add_argument("--columns", default="")
    p.add_argument("--out", required=True)
    p.set_defaults(f=cmd_schema)
    p = sub.add_parser("fill")
    p.add_argument("--bank-dir", required=True)
    p.add_argument("--zarr-dir", required=True)
    p.add_argument("--shard", type=int, required=True)
    p.add_argument("--n-shards", type=int, required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(f=cmd_fill)
    p = sub.add_parser("verify")
    p.add_argument("--bank-dir", required=True)
    p.add_argument("--sample", type=int, default=4000)
    p.add_argument("--out", required=True)
    p.set_defaults(f=cmd_verify)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
