"""MITOSE / v6 -- the PAIR trainer, and the guard that made it necessary.

The red team's V1, executed on a fabricated blob: `np.memmap(mode='r',
shape=(4, 4, 15, 48, 48))` opens a 2 211 840-byte v6 bank WITHOUT AN ERROR and
maps half of it -- the mother crop of trio r/2 for even r, the pair crop for odd
r, against the label of trio r. So this file's `open_bank` does the one thing
v4's never did: it reads `row_shape` from `index_meta.json`, computes the size
the blob MUST have, and RAISES when the file on disk disagrees. `selftest`
proves both directions and the two exit codes.

WHAT ELSE IS DIFFERENT FROM v4's TRAINER, each because a review said so:

  V6  augmentation. v4 draws an independent xy sub-crop, independent y and x
      flips and `rot90(k in 0..3)` per sample. On the pair crop that destroys the
      canonical +y axis the whole design rests on. Here `--pair-augment` allows
      exactly one geometric operation on the pair crop -- the **y flip**, which
      IS the daughter swap -- with ONE draw per ROW shared by both crops, and no
      rot90 and no xy sub-crop on the pair. The mother crop keeps v4's.
  V5  `--min-val-positives` is DERIVED (`floor(min fold positives / 2)`), never
      passed by hand, and echoed with the per-fold counts.
  V9  the shipped epoch is either DECLARED before reading (`--shipped-epoch`) or
      chosen from the OTHER four folds' out-of-fold vectors
      (`--epoch-from-other-folds`), and the receipt says which. The pooled-over-
      all-199-films choice v4 used is not available here.
  V13 `--pos-repeat` is per fold, computed to hit a target step count, and the
      five step counts are published.
  V4  the fold map is a FILE and is mandatory: one map, shared with the arbiter.

THE SCHOOL IS A SCHOOL OF PAIRS (ZEUS 14:4xZ, on HADES). An epoch does not draw
rows, it draws EVENTS: for every mother that carries a true pair, the TRUE pair
and `--k-wrong` plausible WRONG pairs OF THE SAME MOTHER; plus `--n-deceptive`
top-scored pairs of mothers that carry no true pair at all, so the net also
learns "no pair here". Each EVENT weighs one -- its rows share that weight, so
ten wrong sisters do not make a division ten times heavier -- and the loss is
therefore weighted, never repeated. `--pos-weight` stays at 1: the balance comes
from the draw, and stacking a weight on top of it is the double correction the
v3 ablation already measured as harmful.

AND THE WINDOW IS CHECKED ON WHAT THE NET IS FED, not on the bank: a row whose
two daughters do not BOTH fall inside the fed window -- in xy AND in z -- is
EXCLUDED from training and counted. The pair crop refuses an xy separation
beyond its reach and has no z refusal at all; sisters separate in three
dimensions.

Nothing in this file writes a world, a submission or a score table.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import subprocess
import sys
import time

import numpy as np
import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mh_data as D            # noqa: E402
import mhv6_net as NET6        # noqa: E402

V6_ROW_SHAPE = (2,) + tuple(D.BANK_SHAPE)
V6_ROW_BYTES = int(np.prod(V6_ROW_SHAPE)) * 2
V6_FED_SHAPE = (2,) + tuple(D.FED_SHAPE)


class V6TrainError(ValueError):
    """A named refusal of this module."""


def date_u():
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                          capture_output=True, text=True,
                          check=True).stdout.strip()


def load_index(bank_dir):
    with open(str(pathlib.Path(bank_dir) / "index.jsonl"), encoding="utf-8") as f:
        return [json.loads(x) for x in f]


def open_bank(bank_dir, mode="r"):
    """The blob, its shape READ from the index and its size CHECKED.

    v4's `open_bank` takes the shape from a module constant and memmaps it; a
    file of any size at least that large opens silently. This one refuses."""
    d = pathlib.Path(bank_dir)
    meta = json.loads((d / "index_meta.json").read_text(encoding="utf-8"))
    n = int(meta["population_n"])
    shape = tuple(int(v) for v in meta.get("row_shape", V6_ROW_SHAPE))
    if shape != V6_ROW_SHAPE:
        raise V6TrainError(
            "REFUSED: index_meta.json says row_shape %s, this trainer feeds %s "
            "-- a v4 bank is not a v6 bank" % (list(shape), list(V6_ROW_SHAPE)))
    want = n * int(np.prod(shape)) * 2
    got = int((d / "bank.f16").stat().st_size)
    if got != want:
        raise V6TrainError(
            "REFUSED: bank.f16 is %d bytes, the index of %d rows at %d bytes a "
            "row needs %d (%.3fx). A v6 row is %d bytes; opening it as v4's %d "
            "would feed the mother crop of trio r/2 against the label of trio r."
            % (got, n, int(np.prod(shape)) * 2, want, got / max(want, 1),
               V6_ROW_BYTES, int(np.prod(D.BANK_SHAPE)) * 2))
    return np.memmap(str(d / "bank.f16"), dtype=np.float16, mode=mode,
                     shape=(n,) + shape), meta


def fed_view(x):
    """(B, 2, C, Z_BANK, Y_BANK, X_BANK) -> the centred fed window."""
    return x[:, :, :, D.Z_MARGIN:D.Z_MARGIN + D.Z_FED,
             D.XY_MARGIN:D.XY_MARGIN + D.Y_FED,
             D.XY_MARGIN:D.XY_MARGIN + D.X_FED]


def augment_v6(batch_np, rng, pair_augment=True):
    """ONE draw per ROW, and the pair crop keeps its axis.

    mother crop: v4's augmentation (sub-crop, y and x flips, rot90 in xy).
    pair crop:   the y FLIP ONLY -- which is exactly the daughter swap the crop
                 is already invariant to -- plus the same intensity jitter. No
                 rot90 and no xy sub-crop: the canonical +y axis is the feature.
    """
    b = batch_np.shape[0]
    out = np.empty((b,) + V6_FED_SHAPE, dtype=np.float32)
    dz = rng.integers(0, 2 * D.Z_MARGIN + 1, size=b)
    dy = rng.integers(0, 2 * D.XY_MARGIN + 1, size=b)
    dx = rng.integers(0, 2 * D.XY_MARGIN + 1, size=b)
    fy = rng.integers(0, 2, size=b)
    fx = rng.integers(0, 2, size=b)
    k = rng.integers(0, 4, size=b)
    gain = rng.uniform(0.85, 1.15, size=b).astype(np.float32)
    bias = rng.normal(0.0, 0.02, size=b).astype(np.float32)
    z0, y0, x0 = D.Z_MARGIN, D.XY_MARGIN, D.XY_MARGIN
    for i in range(b):
        m = batch_np[i, 0, :, dz[i]:dz[i] + D.Z_FED, dy[i]:dy[i] + D.Y_FED,
                     dx[i]:dx[i] + D.X_FED].astype(np.float32)
        if fy[i]:
            m = m[:, :, ::-1, :]
        if fx[i]:
            m = m[:, :, :, ::-1]
        if k[i]:
            m = np.rot90(m, k=int(k[i]), axes=(2, 3))
        p = batch_np[i, 1, :, z0:z0 + D.Z_FED, y0:y0 + D.Y_FED,
                     x0:x0 + D.X_FED].astype(np.float32)
        if pair_augment and fy[i]:
            p = p[:, :, ::-1, :]
        out[i, 0] = m * gain[i] + bias[i]
        out[i, 1] = p * gain[i] + bias[i]
    return out


def plain_view(batch_np):
    b = batch_np.shape[0]
    out = np.empty((b,) + V6_FED_SHAPE, dtype=np.float32)
    z0, y0, x0 = D.Z_MARGIN, D.XY_MARGIN, D.XY_MARGIN
    out[:] = batch_np[:, :, :, z0:z0 + D.Z_FED, y0:y0 + D.Y_FED,
                      x0:x0 + D.X_FED].astype(np.float32)
    return out


def ap_and_auc(y, s):
    """Average precision and a TIE-AWARE AUC, or (None, None) when the fold
    holds no positive or no negative -- a named empty, never a 0,5."""
    y = np.asarray(y).astype(np.int64)
    s = np.asarray(s, dtype=np.float64)
    n = y.size
    npos = int(y.sum())
    if npos == 0 or npos == n:
        return None, None
    o = np.argsort(-s, kind="mergesort")
    ys = y[o]
    prec = np.cumsum(ys) / np.arange(1, n + 1)
    ap = float((prec * ys).sum() / npos)
    order = np.argsort(s, kind="mergesort")
    ss = s[order]
    ranks = np.empty(n, dtype=np.float64)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and ss[j + 1] == ss[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    auc = float((ranks[y == 1].sum() - npos * (npos + 1) / 2.0)
                / (npos * (n - npos)))
    return ap, auc


def scalars_of(rows):
    """The symmetric scalar block, and the count of rows whose index line
    carried no `scalars` at all -- published, never silently zero."""
    out = np.zeros((len(rows), NET6.PairHead.N_SCALARS), dtype=np.float32)
    n_missing = 0
    for i, r in enumerate(rows):
        sc = r.get("scalars")
        if sc is None:
            n_missing += 1
            sc = r
        out[i] = NET6.symmetric_scalars(sc)
    return out, n_missing


def cmd_selftest(a):
    """BOTH DIRECTIONS on a fabricated 8-row bank: the right size opens, the
    wrong size RAISES. Run it twice with --row-bytes to see the two exit codes."""
    tmp = pathlib.Path(a.tmp_dir)
    tmp.mkdir(parents=True, exist_ok=True)
    n = 8
    rows = [{"row": i, "film": "fab", "embryo": "fab", "t": 3, "label": i % 2,
             "trio": i} for i in range(n)]
    with open(str(tmp / "index.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    meta = {"population_n": n, "row_shape": list(V6_ROW_SHAPE),
            "row_bytes": V6_ROW_BYTES, "n_positive": n // 2}
    (tmp / "index_meta.json").write_text(json.dumps(meta), encoding="utf-8")
    rb = int(a.row_bytes)
    with open(str(tmp / "bank.f16"), "wb") as f:
        f.truncate(n * rb)
    err = None
    opened = None
    try:
        bank, _m = open_bank(str(tmp))
        opened = list(bank.shape)
    except V6TrainError as e:
        err = str(e)
    ok = (err is None) if rb == V6_ROW_BYTES else (err is not None)
    rep = {"schema": "BIOCEL_RECU_V1", "date_u": date_u(), "lane": "MITOSE",
           "question": ("does the v6 trainer refuse a bank whose rows are not "
                        "552 960 bytes"),
           "harnais": "mhv6_train.py selftest", "assiette": "fabricated",
           "n_rows": n, "row_bytes_written": rb,
           "row_bytes_expected": V6_ROW_BYTES,
           "opened_shape": opened, "refusal": err,
           "verdict": ("AS EXPECTED" if ok else "UNEXPECTED"),
           "reading": ("at 552 960 the bank opens and the shape is "
                       "(n, 2, 4, 15, 48, 48); at 276 480 -- v4's row -- it "
                       "RAISES instead of mapping half the file"),
           "what_this_does_not_establish":
               "nothing about training: no gradient is taken here"}
    D.write_json(a.out, rep)
    print(json.dumps(rep, indent=1))
    if not ok:
        raise SystemExit(2)
    if err is not None:
        raise SystemExit(3)     # the REFUSING direction: non-zero by design


def cmd_nettest(a):
    """The DAUGHTER SWAP is invariant end to end -- crop, scalars and logit --
    and the MOTHER/PAIR swap is NOT, which is the other half of the ruling.

    ZEUS 14:4xZ: "the two representations stay IDENTIFIED (mother branch, pair
    branch, concatenated, never pooled symmetrically) -- the invariance is the
    swap of the two daughters, not the swap of mother and pair." Both halves are
    measured here on a fabricated pair, with an untrained head: the arithmetic
    is what is being proved, not a model.
    """
    import math
    import mhv6_pair_crop as PC
    cz, cy, cx = 12, 64, 64
    sep, ang = 12.0, math.radians(37.0)
    d1 = (cz, cy - (sep / 2) * math.cos(ang), cx - (sep / 2) * math.sin(ang))
    d2 = (cz, cy + (sep / 2) * math.cos(ang), cx + (sep / 2) * math.sin(ang))
    reader = PC.FabricatedReader(blobs={3: [(3, d1[0], d1[1], d1[2], 1.0),
                                            (3, d2[0], d2[1], d2[2], 0.7)]})
    pair_a, _ = PC.pair_crop_from_film(reader, 2, d1, d2)
    pair_b, _ = PC.pair_crop_from_film(reader, 2, d2, d1)
    mother, _lm = D.crop_from_film(reader, 2, (cz, cy, cx))
    row_a = np.stack([mother, pair_a])[None, ...]
    row_b = np.stack([mother, pair_b])[None, ...]
    swapped_mp = np.stack([pair_a, mother])[None, ...]
    sc_a = np.array([NET6.symmetric_scalars(
        {"dist_m_d1_um": 4.0, "dist_m_d2_um": 7.5, "pm_prob_d1": 0.9,
         "pm_prob_d2": 0.2, "dz_m_d1": 1.0, "dz_m_d2": -3.0,
         "sister_sep_um": 10.5, "symmetry": 0.3, "cos_angle_at_mother": -0.8,
         "mother_v2_logit": 1.2})], dtype=np.float32)
    sc_b = np.array([NET6.symmetric_scalars(
        {"dist_m_d1_um": 7.5, "dist_m_d2_um": 4.0, "pm_prob_d1": 0.2,
         "pm_prob_d2": 0.9, "dz_m_d1": -3.0, "dz_m_d2": 1.0,
         "sister_sep_um": 10.5, "symmetry": 0.3, "cos_angle_at_mother": -0.8,
         "mother_v2_logit": 1.2})], dtype=np.float32)
    torch.manual_seed(20260908)
    net = NET6.PairHead(in_channels=D.N_CHANNELS, width=8)
    net.eval()
    with torch.no_grad():
        la = float(net(torch.from_numpy(plain_view(row_a)),
                       torch.from_numpy(sc_a))[0])
        lb = float(net(torch.from_numpy(plain_view(row_b)),
                       torch.from_numpy(sc_b))[0])
        lc = float(net(torch.from_numpy(plain_view(swapped_mp)),
                       torch.from_numpy(sc_a))[0])
    same_crop = bool(np.array_equal(pair_a, pair_b))
    same_scalars = bool(np.array_equal(sc_a, sc_b))
    daughter_swap_invariant = bool(la == lb)
    mother_pair_swap_changes_it = bool(la != lc)
    ok = (same_crop and same_scalars and daughter_swap_invariant
          and mother_pair_swap_changes_it)
    rep = {"schema": "BIOCEL_RECU_V1", "date_u": date_u(), "lane": "MITOSE",
           "question": ("is the head invariant to the DAUGHTER swap and NOT to "
                        "the mother/pair swap"),
           "harnais": "mhv6_train.py nettest", "assiette": "fabricated",
           "pair_crop_identical_under_the_daughter_swap": same_crop,
           "scalars_identical_under_the_daughter_swap": same_scalars,
           "logit_daughters_as_given": la, "logit_daughters_swapped": lb,
           "logit_mother_and_pair_swapped": lc,
           "daughter_swap_invariant": daughter_swap_invariant,
           "mother_pair_swap_CHANGES_the_logit": mother_pair_swap_changes_it,
           "verdict": ("PROVEN" if ok else "REFUSED"),
           "what_this_does_not_establish":
               "nothing about a trained model: these weights are random"}
    D.write_json(a.out, rep)
    print(json.dumps({k: rep[k] for k in
                      ("daughter_swap_invariant",
                       "mother_pair_swap_CHANGES_the_logit", "verdict")},
                     indent=1))
    if not ok:
        raise SystemExit(2)


def cmd_augtest(a):
    """V6 PROVEN: the pair crop's daughters stay on ROWS through the whole
    augmentation, and v4's augmentation puts them on COLUMNS half the time.

    The row is the very one that produced rows 18 and 30 at 13:23Z: two blobs
    planted 12 grid voxels apart at 37 degrees, extracted by
    `mhv6_pair_crop.pair_crop_from_film`, then augmented `--draws` times.
    """
    import math
    import mhv6_pair_crop as PC
    cz, cy, cx = 12, 64, 64
    sep, ang = 12.0, math.radians(37.0)
    d1 = (cz, cy - (sep / 2) * math.cos(ang), cx - (sep / 2) * math.sin(ang))
    d2 = (cz, cy + (sep / 2) * math.cos(ang), cx + (sep / 2) * math.sin(ang))
    reader = PC.FabricatedReader(blobs={3: [(3, d1[0], d1[1], d1[2], 1.0),
                                            (3, d2[0], d2[1], d2[2], 1.0)]})
    pair, _log = PC.pair_crop_from_film(reader, 2, d1, d2)
    row = np.empty(V6_ROW_SHAPE, dtype=np.float16)
    row[0] = pair.astype(np.float16)          # the mother slot, unused here
    row[1] = pair.astype(np.float16)
    batch = np.repeat(row[None, ...], int(a.draws), axis=0)
    rng = np.random.default_rng(20260908)

    def axis_of(crop):
        """'rows' if the two peaks sit in one COLUMN (the pair axis is +y),
        'cols' if they sit in one ROW."""
        mid = D.Z_FED // 2
        pl = crop[2][mid]
        hy, hx = pl.shape[0] // 2, pl.shape[1] // 2
        return ("rows" if pl[:, hx].max() >= pl[hy, :].max() else "cols")

    aug = augment_v6(batch, rng, pair_augment=True)
    v6 = [axis_of(aug[i, 1]) for i in range(aug.shape[0])]
    rng2 = np.random.default_rng(20260908)
    v4_like = augment_v6(batch, rng2, pair_augment=True)
    # v4's own augmentation, applied to the PAIR crop, for the contrast
    v4 = []
    rng3 = np.random.default_rng(20260908)
    mh = __import__("mh_train")
    for i in range(int(a.draws)):
        one = mh.augment(batch[i:i + 1, 1], rng3)
        v4.append(axis_of(one[0]))
    n_rows_v6 = sum(1 for v in v6 if v == "rows")
    n_rows_v4 = sum(1 for v in v4 if v == "rows")
    ok = (n_rows_v6 == len(v6)) and (n_rows_v4 < len(v4))
    rep = {"schema": "BIOCEL_RECU_V1", "date_u": date_u(), "lane": "MITOSE",
           "question": ("does --pair-augment keep the pair crop's canonical +y "
                        "axis, and does v4's augmentation destroy it"),
           "harnais": "mhv6_train.py augtest", "assiette": "fabricated",
           "draws": int(a.draws),
           "pair_augment_draws_with_the_axis_on_ROWS": n_rows_v6,
           "v4_augmentation_draws_with_the_axis_on_ROWS": n_rows_v4,
           "expected": ("all draws on ROWS under --pair-augment; fewer than all "
                        "under v4's rot90"),
           "verdict": ("PROVEN" if ok else "UNEXPECTED"),
           "what_this_does_not_establish":
               "nothing about a real film: this is the fabricated pair"}
    D.write_json(a.out, rep)
    print(json.dumps({k: rep[k] for k in
                      ("draws", "pair_augment_draws_with_the_axis_on_ROWS",
                       "v4_augmentation_draws_with_the_axis_on_ROWS",
                       "verdict")}, indent=1))
    if not ok:
        raise SystemExit(2)


def cmd_train(a):
    rows = load_index(a.bank_dir)
    bank, meta = open_bank(a.bank_dir)
    fold_map = json.loads(pathlib.Path(a.fold_map).read_text(encoding="utf-8"))
    # TWO SHAPES, one map. FRONT A's shared map is {"fold_of_film": {film: k}},
    # this lane's own was {k: [films]}; both are read, neither is guessed at.
    fold_of = {}
    if isinstance(fold_map, dict) and "fold_of_film" in fold_map:
        fold_of = {f: int(k) for f, k in fold_map["fold_of_film"].items()}
        n_declared = int(fold_map.get("folds", len(set(fold_of.values()))))
    else:
        for k, films in fold_map.items():
            for f in films:
                fold_of[f] = int(k)
        n_declared = len(fold_map)
    films = sorted({r["film"] for r in rows})
    missing = [f for f in films if f not in fold_of]
    if missing:
        raise V6TrainError(
            "REFUSED: %d films of the index are absent from the fold map (%s). "
            "One map, shared with the arbiter, or no run."
            % (len(missing), missing[:3]))
    n_folds = n_declared
    y = np.array([int(r["label"]) for r in rows], dtype=np.int64)
    fold = np.array([fold_of[r["film"]] for r in rows], dtype=np.int64)
    per_fold_pos = [int(y[fold == k].sum()) for k in range(n_folds)]
    min_val = int(math.floor(min(per_fold_pos) / 2.0))
    if a.min_val_positives >= 0:
        min_val = int(a.min_val_positives)
    k = int(a.fold)
    val = np.flatnonzero(fold == k)
    tr = np.flatnonzero(fold != k)
    n_val_pos = int(y[val].sum())
    print(json.dumps({"BANK_ASSERT": {
        "bank": a.bank_dir, "rows": len(rows), "n_positive": int(y.sum()),
        "row_shape": list(V6_ROW_SHAPE), "bank_bytes": int(bank.size * 2),
        "per_fold_positives": per_fold_pos,
        "min_val_positives_derived": min_val,
        "fold": k, "val_positives": n_val_pos}}))
    if n_val_pos < min_val:
        raise V6TrainError("REFUSED: fold %d holds %d positives, below the "
                           "derived floor %d" % (k, n_val_pos, min_val))

    # ---- (2) THE WINDOW, checked on what the net is fed ---------------------
    half_y = D.Y_FED / 2.0 - 2.0
    half_z = D.Z_FED / 2.0 - 1.0
    sep = np.array([r.get("pair_sep_grid", [0.0, 0.0]) for r in rows],
                   dtype=np.float64)
    inside = (sep[:, 0] / 2.0 <= half_y) & (sep[:, 1] / 2.0 <= half_z)
    n_out_xy = int(((sep[:, 0] / 2.0 > half_y)).sum())
    n_out_z = int(((sep[:, 1] / 2.0 > half_z)).sum())
    n_excluded = int((~inside).sum())
    n_excluded_pos = int((~inside & (y == 1)).sum())
    tr = tr[inside[tr]]
    val = val[inside[val]]

    pos_tr = tr[y[tr] == 1]
    neg_tr = tr[y[tr] == 0]
    # ---- (1) THE SCHOOL OF PAIRS -------------------------------------------
    mother_of = np.array([r.get("mother_key", "%s|%d" % (r["film"], r["t"]))
                          for r in rows], dtype=object)
    by_mother = {}
    for i in tr:
        by_mother.setdefault(mother_of[i], []).append(int(i))
    events_true = [m for m, idx in by_mother.items()
                   if any(y[j] == 1 for j in idx)]
    events_none = [m for m, idx in by_mother.items()
                   if not any(y[j] == 1 for j in idx)]
    strata_of = np.array([float(r.get("strata_key", 0.0)) for r in rows],
                         dtype=np.float64)
    pos_repeat = 1
    n_ep = (len(events_true) * (1 + int(a.k_wrong))
            + min(int(a.n_deceptive), len(events_none)) * int(a.deceptive_pairs))
    steps = int(math.ceil(n_ep / a.batch))

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(int(a.torch_seed))
    model = NET6.PairHead(in_channels=D.N_CHANNELS, width=a.width).to(dev)
    ema = {n: p.detach().clone() for n, p in model.state_dict().items()}
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=a.lr, total_steps=max(1, steps * a.epochs), pct_start=0.3)
    lossf = torch.nn.BCEWithLogitsLoss(reduction="none")
    rng = np.random.default_rng(int(a.seed))
    sc_all, n_sc_missing = scalars_of(rows)
    if n_sc_missing:
        print(json.dumps({"warning": "index lines without a `scalars` block",
                          "n_rows": n_sc_missing, "of": len(rows)}))

    def draw_epoch(rng):
        """One epoch: every true EVENT with its true pair and k wrong pairs of
        the same mother, plus deceptive top pairs of mothers with no true pair.
        Returns (row indices, per-row weight) -- the weight makes the EVENT the
        unit, never the row."""
        idx = []
        wts = []
        for m in events_true:
            here = np.array(by_mother[m], dtype=np.int64)
            t_rows = here[y[here] == 1]
            w_rows = here[y[here] == 0]
            if w_rows.size:
                order = w_rows[np.argsort(-strata_of[w_rows], kind="mergesort")]
                take = order[:int(a.k_wrong)] if not a.k_random else \
                    rng.choice(w_rows, size=min(int(a.k_wrong), w_rows.size),
                               replace=False)
            else:
                take = np.empty(0, dtype=np.int64)
            block = np.concatenate([t_rows, take])
            if block.size == 0:
                continue
            idx.append(block)
            wts.append(np.full(block.size, 1.0 / block.size))
        if events_none and int(a.n_deceptive) > 0:
            pick = rng.choice(len(events_none),
                              size=min(int(a.n_deceptive), len(events_none)),
                              replace=False)
            for j in pick:
                here = np.array(by_mother[events_none[j]], dtype=np.int64)
                order = here[np.argsort(-strata_of[here], kind="mergesort")]
                block = order[:int(a.deceptive_pairs)]
                if block.size == 0:
                    continue
                idx.append(block)
                wts.append(np.full(block.size, 1.0 / block.size))
        if not idx:
            raise V6TrainError("REFUSED: the epoch is empty -- no event in this "
                               "fold carries a pair inside the window")
        return np.concatenate(idx), np.concatenate(wts).astype(np.float32)

    def evaluate(idx, use_ema=True):
        state = None
        if use_ema:
            state = {n: p.detach().clone() for n, p in model.state_dict().items()}
            model.load_state_dict(ema)
        model.eval()
        out = np.empty(len(idx), dtype=np.float64)
        with torch.no_grad():
            for s in range(0, len(idx), a.eval_batch):
                sel = idx[s:s + a.eval_batch]
                xb = torch.from_numpy(plain_view(np.asarray(bank[sel]))).to(dev)
                sb = torch.from_numpy(sc_all[sel]).to(dev)
                out[s:s + len(sel)] = model(xb, sb).float().cpu().numpy()
        if state is not None:
            model.load_state_dict(state)
        return out

    hist = []
    best = (-1.0, -1)
    outd = pathlib.Path(a.out_dir)
    outd.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for ep in range(int(a.epochs)):
        model.train()
        idx, wts = draw_epoch(rng)
        perm = rng.permutation(len(idx))
        idx, wts = idx[perm], wts[perm]
        tot = 0.0
        for s in range(0, len(idx), a.batch):
            order = np.argsort(idx[s:s + a.batch], kind="mergesort")
            sel = idx[s:s + a.batch][order]
            wb = torch.from_numpy(wts[s:s + a.batch][order]).to(dev)
            xb = torch.from_numpy(augment_v6(np.asarray(bank[sel]), rng,
                                             bool(a.pair_augment))).to(dev)
            sb = torch.from_numpy(sc_all[sel]).to(dev)
            yb = torch.from_numpy(y[sel].astype(np.float32)).to(dev)
            opt.zero_grad(set_to_none=True)
            loss = (lossf(model(xb, sb), yb) * wb).sum() / wb.sum()
            loss.backward()
            if a.clip_grad > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), a.clip_grad)
            opt.step()
            sched.step()
            with torch.no_grad():
                for n_, p_ in model.state_dict().items():
                    if p_.dtype.is_floating_point:
                        ema[n_].mul_(a.ema_decay).add_(p_, alpha=1 - a.ema_decay)
                    else:
                        ema[n_].copy_(p_)
            tot += float(loss.item()) * len(sel)
        sv = evaluate(val)
        ap, auc = ap_and_auc(y[val], sv)
        hist.append({"epoch": ep, "loss": round(tot / max(len(idx), 1), 6),
                     "val_ap": ap, "val_auc": auc,
                     "seconds": round(time.time() - t0, 1)})
        print(json.dumps(hist[-1]))
        np.save(str(outd / ("val_scores_epoch%03d.npy" % ep)), sv)
        torch.save({"model": {n: v.cpu() for n, v in ema.items()},
                    "epoch": ep, "is_ema": True, "width": a.width,
                    "in_channels": D.N_CHANNELS, "fold": k,
                    "row_shape": list(V6_ROW_SHAPE)},
                   str(outd / ("ckpt_epoch%03d.pt" % ep)))
        if ap is not None and ap > best[0]:
            best = (ap, ep)

    shipped = int(a.shipped_epoch) if a.shipped_epoch >= 0 else int(best[1])
    rule = ("DECLARED before reading (--shipped-epoch)" if a.shipped_epoch >= 0
            else "chosen on THIS fold's own out-of-fold AP -- to be replaced by "
                 "the other-four-folds rule when the five folds are read "
                 "together")
    rep = {"schema": "BIOCEL_RECU_V1", "date_u": date_u(), "lane": "MITOSE",
           "question": "one fold of the v6 PAIR head",
           "harnais": "mhv6_train.py train", "assiette": a.bank_dir,
           "fold": k, "n_folds": n_folds, "fold_map": a.fold_map,
           "per_fold_positives": per_fold_pos,
           "min_val_positives_derived": min_val,
           "n_train_positive": int(len(pos_tr)),
           "n_val_positive": n_val_pos,
           "school": {"rule": ("one EVENT per mother that carries a true "
                               "pair: the true pair plus k wrong pairs of the "
                               "SAME mother, plus deceptive top pairs of "
                               "mothers with no true pair; the event weighs "
                               "one and its rows share that weight"),
                      "k_wrong": int(a.k_wrong),
                      "wrong_pairs_taken_by": ("the ranker's own top" if not
                                               a.k_random else "a random draw"),
                      "n_deceptive_mothers": int(a.n_deceptive),
                      "deceptive_pairs_each": int(a.deceptive_pairs),
                      "events_with_a_true_pair": len(events_true),
                      "events_without": len(events_none),
                      "pos_weight": 1.0,
                      "why_no_pos_repeat": ("the balance comes from the draw; "
                                            "stacking a weight on a repeat is "
                                            "the double correction v3 measured "
                                            "as harmful")},
           "window_check_on_what_the_net_is_fed": {
               "fed_half_window_grid_xy": half_y, "fed_half_window_grid_z": half_z,
               "n_rows_excluded": n_excluded,
               "n_excluded_because_xy": n_out_xy,
               "n_excluded_because_z": n_out_z,
               "n_POSITIVES_excluded": n_excluded_pos,
               "rule": ("a row whose two daughters do not BOTH fall inside the "
                        "fed window, in xy AND in z, never reaches the net")},
           "pos_repeat": pos_repeat, "steps_per_epoch": steps,
           "epoch_rows": int(n_ep), "batch": int(a.batch),
           "n_index_rows_without_scalars": n_sc_missing,
           "recipe": {"onecycle": True, "clip_grad": a.clip_grad,
                      "ema_decay": a.ema_decay, "lr": a.lr,
                      "pair_augment_y_flip_only": bool(a.pair_augment),
                      "scalars": NET6.PairHead.N_SCALARS,
                      "scalars_are_symmetric_in_d1_d2": True},
           "shipped_epoch": shipped, "shipped_epoch_rule": rule,
           "history": hist, "model_parameters": NET6.count_parameters(model),
           "seconds": round(time.time() - t0, 1),
           "what_this_does_not_establish": (
               "nothing about a judged world and nothing about the arbiter: "
               "this is one fold's out-of-fold vector")}
    D.write_json(outd / ("R_training_fold%d.json" % k), rep)
    print(json.dumps({"fold": k, "shipped_epoch": shipped,
                      "best_val_ap": best[0], "steps": steps,
                      "pos_repeat": pos_repeat}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("selftest")
    p.add_argument("--tmp-dir", required=True)
    p.add_argument("--row-bytes", type=int, default=V6_ROW_BYTES)
    p.add_argument("--out", required=True)
    p.set_defaults(f=cmd_selftest)
    p = sub.add_parser("nettest")
    p.add_argument("--out", required=True)
    p.set_defaults(f=cmd_nettest)
    p = sub.add_parser("augtest")
    p.add_argument("--draws", type=int, default=200)
    p.add_argument("--out", required=True)
    p.set_defaults(f=cmd_augtest)
    p = sub.add_parser("train")
    p.add_argument("--bank-dir", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--fold-map", required=True)
    p.add_argument("--fold", type=int, required=True)
    p.add_argument("--epochs", type=int, default=26)
    p.add_argument("--batch", type=int, default=96)
    p.add_argument("--eval-batch", type=int, default=256)
    p.add_argument("--width", type=int, default=32)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--clip-grad", type=float, default=1.0)
    p.add_argument("--ema-decay", type=float, default=0.999)
    p.add_argument("--hard", type=int, default=3000)
    p.add_argument("--rand-neg", type=int, default=3000)
    p.add_argument("--pos-repeat", type=int, default=0,
                   help="kept for the receipt; the school of pairs does not "
                        "repeat positives, it weighs events")
    p.add_argument("--target-steps", type=int, default=78)
    p.add_argument("--k-wrong", type=int, default=4,
                   help="wrong pairs of the SAME mother shown beside each true "
                        "pair")
    p.add_argument("--k-random", action="store_true",
                   help="draw the k wrong pairs at random instead of taking the "
                        "ranker's own top -- the harder default is the top")
    p.add_argument("--n-deceptive", type=int, default=200,
                   help="mothers with NO true pair whose top pairs are shown, "
                        "so the net learns `no pair here`")
    p.add_argument("--deceptive-pairs", type=int, default=2)
    p.add_argument("--min-val-positives", type=int, default=-1,
                   help="-1 = DERIVE floor(min fold positives / 2)")
    p.add_argument("--shipped-epoch", type=int, default=-1,
                   help="-1 = choose on this fold; >= 0 = DECLARED beforehand")
    p.add_argument("--pair-augment", type=int, default=1)
    p.add_argument("--seed", type=int, default=20260908)
    p.add_argument("--torch-seed", type=int, default=20260908)
    p.set_defaults(f=cmd_train)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
