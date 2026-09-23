"""Adversarial CPU tests of the K-DS scorer: fold routing / leak audit / Kaggle mount layouts / stale parts.

    python experiments/l2_daughternet/kdn_score/test_adversarial.py [--out DIR]     # ~2-3 min on CPU

The fold models are random-init DaughterNets with the head weight zeroed and a fold-specific head bias, so each model
outputs ONE constant softmax that identifies it: the model that scored a row is read back from p, independently of
kds_core's routing code, and compared with experiments/l2_daughternet/splits.json read directly.

T1 routing   5 fold checkpoints in the new Kaggle layout /kaggle/input/notebooks/<owner>/<slug>/folds/fold_k/best.pt, the
             same files again under the legacy /kaggle/input/<slug>/ mount (must not abort discovery), the coords parquet
             under /kaggle/input/datasets/<owner>/biohub-l2-coords/. One 44b6 leak-group video per fold + one 6bba video;
             rows of different videos interleaved in random order; a node_id shared by every video; synthetic rows on .5
             rounding boundaries of the pooled crop centre, negative z, t = 0 and t = T-1. EVERY row's fast-path sample is
             contract-checked against tools.daughternet.prepare_sample. OOF p must be the softmax of the model of the
             video's splits.json fold and that model must not have trained on any video of the row's leak group; ens p =
             mean of the 5; output order = input order. Discovery must refuse two different trainer runs.
T2 partial   a trainer splits_used.json listing a subset and moving one leak-group sibling to another fold: the other
             sibling (routed by the embedded splits to a model that trained on the moved one) must be NaN in OOF and
             listed as leak_excluded, finite in ens; a fold without a checkpoint gives NaN; checkpoints/splits n_folds
             mismatch aborts; a rerun resumes; replacing one checkpoint clears the parts and rescores (no stale parts).
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

import kds_core  # noqa: E402  (bootstraps tools/ and kdn_core onto sys.path)
import kdn_core  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
from tools.daughternet import CLASSES, DEFAULT_CFG, build_model  # noqa: E402

DATA = ROOT / "biohub-cell-tracking-during-development" / "train"
COORDS = ROOT / "experiments" / "l2_daughternet" / "coords_exp39.parquet"
SPLITS = ROOT / "experiments" / "l2_daughternet" / "splits.json"
SLUG = "biohub-l2-kdn-train"
FAILURES: list[str] = []


def check(ok: bool, what: str) -> None:
    print(("  ok   " if ok else "  FAIL ") + what, flush=True)
    if not ok:
        FAILURES.append(what)


def fold_bias(fold: int, variant: int = 0) -> list[float]:
    return [0.0, 0.35 * (fold + 1) + 0.9 * variant, -0.25 * (fold + 1) + 0.5 * variant]


def expected_p(bias: list[float]) -> np.ndarray:
    return torch.softmax(torch.tensor(bias, dtype=torch.float32), dim=0).numpy().astype(np.float64)


def make_ckpt(path: Path, fold: int, n_folds: int = 5, variant: int = 0) -> Path:
    """Trainer payload format; constant output softmax(fold_bias(fold, variant)) whatever the input."""
    torch.manual_seed(1000 + fold)
    cfg = copy.deepcopy(DEFAULT_CFG)
    cfg["classes"] = list(CLASSES)
    cfg["train"] = {"fold": fold, "early_stop_fold": fold, "n_folds": n_folds, "inner_val": False,
                    "kernel": "kds-adversarial-test"}
    model = build_model(cfg)
    with torch.no_grad():
        model.head.weight.zero_()
        model.head.bias.copy_(torch.tensor(fold_bias(fold, variant)))
    payload = {"model_state": {k: v.detach().cpu() for k, v in model.state_dict().items()}, "config": cfg,
               "fold": int(fold), "epoch": 0, "val_loss": 0.0}
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(payload, path)
    return path


def identify(p: np.ndarray, experts: dict[int, np.ndarray]) -> tuple[int, float, float]:
    """(fold k whose constant softmax p is, |p - expect_k|, gap to the next best)."""
    d = {k: float(np.abs(p - e).max()) for k, e in experts.items()}
    order = sorted(d, key=d.get)
    return order[0], d[order[0]], d[order[1]] - d[order[0]]


def base_cfg(tmp: Path, work: str, inp: Path, **kw) -> dict:
    cfg = kds_core.config_from_env({
        "work_dir": str(tmp / work), "input_root": str(inp), "ckpt_root": "", "coords": "", "splits": "",
        "data_dir": str(DATA), "stems": [], "max_videos": 0, "rows_per_video": 0, "seed": 0, "modes": ["oof", "ens"],
        "gpus": 0, "workers": 2, "frame_threads": 2, "batch": 16, "checks_fresh": 1, "checks_cached": 10 ** 6,
        "verify_per_fold": 2, "verify_tol": 1e-5, "expect_folds": 5, "retries": 0, "resume": True})
    cfg.update(kw)
    return cfg


def sample_rows(coords: pd.DataFrame, stems: list[str], per_video: int, rng) -> pd.DataFrame:
    parts = []
    counts = coords.loc[coords.stem.isin(stems)].groupby("node_id")["stem"].nunique()
    nid = int(counts.sort_values(ascending=False, kind="stable").index[0]) if len(counts) and counts.max() >= 2 else None
    for s in stems:
        g = coords[coords.stem == s]
        pick = set(rng.choice(len(g), size=min(per_video, len(g)), replace=False).tolist())
        pick |= {int(np.argmin(g.t.to_numpy())), int(np.argmax(g.t.to_numpy())), int(np.argmin(g.z.to_numpy()))}
        if nid is not None and (g.node_id.to_numpy() == nid).any():
            pick.add(int(np.flatnonzero(g.node_id.to_numpy() == nid)[0]))
        parts.append(g.iloc[sorted(pick)])
    return pd.concat(parts), nid


def test_routing(tmp: Path, coords: pd.DataFrame, splits: dict[str, int], groups: list[list[str]]) -> None:
    print("\n[T1] fold routing on 5 identifiable fold models, duplicate Kaggle mounts, interleaved input")
    rng = np.random.default_rng(7)
    fold_groups = {}
    for g in groups:
        fold_groups.setdefault(splits[g[0]], sorted(g))
    stems = [fold_groups[k][0] for k in range(5)]
    stems.append(sorted(s for s in splits if s.startswith("6bba") and splits[s] == 2)[0])
    rows, nid = sample_rows(coords, stems, 8, rng)
    T = json.loads((DATA / f"{stems[-1]}.zarr" / "0" / "zarr.json").read_text())["shape"][0]
    synth = pd.DataFrame({  # pooled-centre rounding boundaries (y/4, x/4 = k + .5, z = k + .5), padding, t clamps
        "stem": stems[-1], "node_id": np.arange(10 ** 9, 10 ** 9 + 6, dtype=np.int64),
        "t": np.array([0, T - 1, 50, 50, T - 2, 1], dtype=np.int64),
        "z": [10.5, -0.5, 63.5, 11.5, 0.49999, -0.6666667],
        "y": [42.0, -2.0, 254.0, 46.0, 2.0, 257.9],
        "x": [6.0, 1021.9, 2.0, 10.0, 253.99, -2.1]})
    rows = pd.concat([rows, synth], ignore_index=True)
    rows = rows.iloc[rng.permutation(len(rows))].reset_index(drop=True)  # interleave the videos
    inp = tmp / "t1_input"
    new = inp / "notebooks" / "vitaliineibauer" / SLUG
    legacy = inp / SLUG
    for k in range(5):
        make_ckpt(new / "folds" / f"fold_{k}" / "best.pt", k)
        make_ckpt(new / "folds" / f"fold_{k}" / "last.pt", k, variant=3)  # decoy: never best.pt
    (new / "splits_used.json").write_text(json.dumps({"source": "test", "n_folds": 5, "folds": splits}, indent=1))
    shutil.copytree(new, legacy)  # the same trainer output visible under the legacy mount too
    ds = inp / "datasets" / "vitaliineibauer" / "biohub-l2-coords"
    ds.mkdir(parents=True)
    rows[["stem", "node_id", "t", "z", "y", "x"]].to_parquet(ds / "coords_exp39.parquet", index=False)

    found = kds_core.discover_checkpoints(inp, "best.pt", SLUG)
    check(sorted(found) == [0, 1, 2, 3, 4] and len({p.parent.parent for p in found.values()}) == 1,
          f"duplicate mounts: 5 folds from one mount {sorted({str(p.parent.parent.relative_to(inp)) for p in found.values()})}")
    # two genuinely different trainer runs must not be mixed
    bad = tmp / "t1_bad_input"
    make_ckpt(bad / "notebooks" / "u" / SLUG / "folds" / "fold_0" / "best.pt", 0)
    make_ckpt(bad / "notebooks" / "u" / "other-run" / "folds" / "fold_1" / "best.pt", 1)
    try:
        kds_core.discover_checkpoints(bad, "best.pt", SLUG)
        check(False, "fold_0 and fold_1 from two different trainer outputs must be refused")
    except RuntimeError as exc:
        check("different trainer outputs" in str(exc), "fold models from two trainer outputs refused")
    make_ckpt(bad / "notebooks" / "u" / f"{SLUG}-v2" / "folds" / "fold_0" / "best.pt", 0, variant=1)
    try:
        kds_core.discover_checkpoints(bad, "best.pt", SLUG)
        check(False, "two different fold_0/best.pt matching the slug must be refused")
    except RuntimeError as exc:
        check("different checkpoints" in str(exc), "two different fold_0 checkpoints refused (set KDS_CKPT_ROOT)")

    cfg = base_cfg(tmp, "t1_work", inp)
    t0 = time.time()
    state = kds_core.run(cfg)
    print(f"  run: {time.time() - t0:.1f} s")
    experts = {k: expected_p(fold_bias(k)) for k in range(5)}
    ens_expect = np.mean([experts[k] for k in range(5)], axis=0)
    sib = {s: set(g) for g in groups for s in g}
    s_oof, s_ens = state["summaries"]["oof"], state["summaries"]["ens"]
    oof = pd.read_parquet(tmp / "t1_work" / "node_p_oof.parquet")
    ens = pd.read_parquet(tmp / "t1_work" / "node_p_ens.parquet")
    for name, out in (("oof", oof), ("ens", ens)):
        check(len(out) == len(rows) and np.array_equal(out.stem.to_numpy(), rows.stem.to_numpy())
              and np.array_equal(out.node_id.to_numpy(), rows.node_id.to_numpy()),
              f"{name}: {len(out)} rows in the interleaved input order (stem, node_id)")
        check(bool((out.fold.to_numpy() == rows.stem.map(splits).to_numpy()).all()),
              f"{name}: fold column = splits.json fold")
    p = oof[kds_core.P_COLUMNS].to_numpy(np.float64)
    bad_rows, leak_rows, worst = [], [], 0.0
    for i, stem in enumerate(oof.stem):
        k, d, gap = identify(p[i], experts)
        worst = max(worst, d)
        if k != splits[stem] or d > 1e-6 or gap < 1e-3:
            bad_rows.append((stem, k, d))
        # model k trained on every splits.json video whose fold != k: none may be in the row's leak group
        if any(splits[s] != k for s in sib.get(stem, set()) | {stem}):
            leak_rows.append(stem)
    check(not bad_rows, f"oof: every row scored by its video's splits.json fold model (max |p - expect| {worst:.1e}) "
                        f"{bad_rows[:3]}")
    check(not leak_rows and s_oof["oof_routing_audit"]["excluded"] == {}
          and s_oof["oof_routing_audit"]["videos_in_leak_groups"] == 5,
          f"oof: no row scored by a model that trained on its video or a leak-group sibling "
          f"({sum(len(sib.get(s, ())) for s in stems)} leak-group members around the 5 44b6 videos)")
    shared = oof[oof.node_id == nid] if nid is not None else oof.iloc[:0]
    n_vid = int(coords.loc[coords.stem.isin(stems) & (coords.node_id == nid)].stem.nunique()) if nid is not None else 0
    n_fold = int(shared.stem.map(splits).nunique())
    check(n_vid >= 2 and len(shared) == n_vid and n_fold >= 2 and shared.p_par.nunique() == n_fold
          and all(identify(r, experts)[0] == splits[st] for st, r in
                  zip(shared.stem, shared[kds_core.P_COLUMNS].to_numpy(np.float64))),
          f"node_id {nid} shared by {n_vid} videos ({n_fold} folds): each row keeps its own video's fold model p")
    d_ens = float(np.abs(ens[kds_core.P_COLUMNS].to_numpy(np.float64) - ens_expect).max())
    check(d_ens < 1e-6, f"ens: every row = mean of the 5 fold softmaxes (max |dp| {d_ens:.1e})")
    n_checked = sum(w["sum_checks_fresh"] + w["sum_checks_cached"] for w in s_oof["timing"]["workers"])
    check(n_checked == len(rows), f"every row's sample contract-checked against prepare_sample ({n_checked}/{len(rows)}, "
                                  "incl. .5 rounding boundaries, negative z, t = 0 and T-1)")
    check(s_oof["verify"]["pass"] and s_ens["verify"]["pass"] and s_oof["nan_rows"] == 0 and s_ens["nan_rows"] == 0,
          f"verify via score_nodes pass (oof {s_oof['verify']['max_abs_diff']:.1e}, ens "
          f"{s_ens['verify']['max_abs_diff']:.1e}), no NaN")
    ck_paths = {Path(v["path"]).parent.parent.parent for v in s_oof["checkpoints"].values()}
    check(len(ck_paths) == 1 and s_oof["splits"]["primary"] is not None
          and Path(s_oof["splits"]["primary"]).parent in ck_paths,
          f"checkpoints and splits_used.json from the same mount {sorted(str(p.relative_to(inp)) for p in ck_paths)}")


def test_partial(tmp: Path, coords: pd.DataFrame, splits: dict[str, int], groups: list[list[str]]) -> None:
    print("\n[T2] partial trainer splits: leak audit, fold without a model, n_folds guard, stale parts")
    rng = np.random.default_rng(11)
    grp = next(sorted(g) for g in groups if splits[g[0]] == 0 and len(g) == 2)
    L1, L2 = grp                      # a fold-0 leak group of two videos
    V1 = sorted(s for s in splits if s.startswith("6bba") and splits[s] == 1)[0]
    V3 = sorted(s for s in splits if s.startswith("6bba") and splits[s] == 3)[0]
    rows, _ = sample_rows(coords, [L1, L2, V1, V3], 6, rng)
    rows = rows.iloc[rng.permutation(len(rows))].reset_index(drop=True)
    inp = tmp / "t2_input"
    run_dir = inp / SLUG
    make_ckpt(run_dir / "folds" / "fold_0" / "best.pt", 0)
    make_ckpt(run_dir / "folds" / "fold_1" / "best.pt", 1)
    # the trainer moved L2 to fold 1 (so model 0 trained on L2); L1 is not listed -> embedded fold 0 -> model 0
    primary = {"source": "test", "n_folds": 5, "folds": {L2: 1, V1: splits[V1], V3: splits[V3]}}
    (run_dir / "splits_used.json").write_text(json.dumps(primary, indent=1))
    ds = inp / "biohub-l2-coords"
    ds.mkdir(parents=True)
    rows[["stem", "node_id", "t", "z", "y", "x"]].to_parquet(ds / "coords_exp39.parquet", index=False)
    cfg = base_cfg(tmp, "t2_work", inp, checks_cached=2)
    state = kds_core.run(cfg)
    s = state["summaries"]["oof"]
    oof = pd.read_parquet(tmp / "t2_work" / "node_p_oof.parquet")
    ens = pd.read_parquet(tmp / "t2_work" / "node_p_ens.parquet")
    e = {k: expected_p(fold_bias(k)) for k in (0, 1)}
    fin = np.isfinite(oof[kds_core.P_COLUMNS].to_numpy()).all(axis=1)
    by = dict(zip(oof.stem, fin))
    check(s["videos"]["leak_excluded"] == [L1] and list(s["oof_routing_audit"]["excluded"]) == [L1]
          and s["oof_routing_audit"]["excluded"][L1]["model_trained_on"] == [L2],
          f"leak audit excludes {L1} (fold 0 model trained on its sibling {L2})")
    check(not fin[(oof.stem == L1).to_numpy()].any() and not fin[(oof.stem == V3).to_numpy()].any()
          and fin[oof.stem.isin([L2, V1]).to_numpy()].all(),
          f"oof NaN exactly for {L1} (leak) and {V3} (fold 3 has no model): {by}")
    ok_rows = oof[oof.stem.isin([L2, V1])]
    d1 = float(np.abs(ok_rows[kds_core.P_COLUMNS].to_numpy(np.float64) - e[1]).max())
    check(d1 < 1e-6 and bool((oof.loc[oof.stem == L2, "fold"] == 1).all()),
          f"{L2} routed by the trainer's splits_used.json to fold 1 (model 1), |dp| {d1:.1e}")
    d_ens = float(np.abs(ens[kds_core.P_COLUMNS].to_numpy(np.float64) - (e[0] + e[1]) / 2).max())
    check(d_ens < 1e-6 and s["videos"]["no_model"] == [V3],
          f"ens finite for every video incl. {L1} and {V3} (mean of the 2 models, |dp| {d_ens:.1e})")

    # resume: nothing changed -> no rescoring
    state = kds_core.run(cfg)
    s = state["summaries"]["oof"]
    check(s["videos"]["scored_this_run"] == 0 and s["videos"]["resumed"] == 2 and s["parts_status"] == "resume",
          f"rerun resumes ({s['videos']['resumed']} videos, status {s['parts_status']})")
    # a replaced fold checkpoint must never reuse the old parts
    make_ckpt(run_dir / "folds" / "fold_1" / "best.pt", 1, variant=1)
    state = kds_core.run(cfg)
    s = state["summaries"]["oof"]
    oof2 = pd.read_parquet(tmp / "t2_work" / "node_p_oof.parquet")
    e1b = expected_p(fold_bias(1, variant=1))
    d1b = float(np.abs(oof2.loc[oof2.stem.isin([L2, V1]), kds_core.P_COLUMNS].to_numpy(np.float64) - e1b).max())
    check(s["parts_status"] == "cleared (signature changed)" and s["videos"]["scored_this_run"] == 2 and d1b < 1e-6,
          f"new fold_1 checkpoint: parts cleared and rescored with the new model (|dp| {d1b:.1e})")

    # checkpoints trained with 5 folds, routing splits with 2 folds -> refuse
    (run_dir / "splits_used.json").write_text(json.dumps(
        {"source": "test", "n_folds": 2, "folds": {L2: 1, V1: 1, L1: 0}}, indent=1))
    try:
        kds_core.run(cfg)
        check(False, "n_folds mismatch between checkpoints and splits must abort")
    except RuntimeError as exc:
        check("n_folds" in str(exc), "n_folds mismatch (checkpoints 5, splits_used.json 2) aborts before scoring")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="", help="scratch dir (default: a new temp dir, removed at the end)")
    args = ap.parse_args()
    t_all = time.time()
    tmp = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="kds_adv_"))
    if tmp.exists() and args.out:
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    coords = kds_core.read_coords(COORDS)
    splits = kdn_core.load_splits(SPLITS)
    groups = kds_core.leak_groups(SPLITS)
    print(f"scratch {tmp}; {len(groups)} leak groups; torch {torch.__version__}")
    test_routing(tmp, coords, splits, groups)
    test_partial(tmp, coords, splits, groups)
    print(f"\n{'PASS' if not FAILURES else 'FAIL'}: {len(FAILURES)} failures in {time.time() - t_all:.0f} s")
    for f in FAILURES:
        print("  -", f)
    if not args.out:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
