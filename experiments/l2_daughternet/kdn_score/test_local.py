"""Laptop (CPU) test of the K-DS scorer with random-init fold checkpoints (no trained model needed).

    python experiments/l2_daughternet/kdn_score/test_local.py                  # ~2-4 min on CPU
    python experiments/l2_daughternet/kdn_score/test_local.py --rows 800 --out C:/tmp/kds_test

1. Two random-init DaughterNet checkpoints in the trainer's format ({'model_state','config','fold','epoch','val_loss'}),
   head scaled so the softmax actually varies between nodes (a near-uniform output would make the 1e-5 checks vacuous).
2. Core function kds_core.score_video on 2 local videos (fold 0 and fold 1 in splits.json, one per embryo), a seeded
   subsample of their coords_exp39.parquet rows in SHUFFLED order: shape, finiteness, sum to 1, row alignment
   (stem, node_id preserved), fold column = splits fold, and re-scoring rows through tools.daughternet.score_nodes
   directly (its own frame reading and sample building) within 1e-5. Sensitivity controls: the other fold's model and a
   2-pooled-voxel shift must move p by far more than the tolerance. Prefetch-thread path == inline path. Ensemble path
   == score_nodes with both models.
3. End-to-end kds_core.run on a fake /kaggle/input tree (trainer output with decoys: last.pt, a best.pt inside a *.zarr
   and one without a fold_k dir; coords parquet under a dataset dir; splits_used.json): 2 CPU worker processes, oof +
   ens, merged parquet aligned to the selection, summary verify within 1e-5, then a rerun that resumes every part and
   reproduces the outputs bit for bit.
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
from tools.daughternet import CLASSES, DEFAULT_CFG, build_model, load_daughternet, score_nodes  # noqa: E402

DATA = ROOT / "biohub-cell-tracking-during-development" / "train"
COORDS = ROOT / "experiments" / "l2_daughternet" / "coords_exp39.parquet"
SPLITS = ROOT / "experiments" / "l2_daughternet" / "splits.json"
TOL = 1e-5
FAILURES: list[str] = []


def check(ok: bool, what: str) -> None:
    print(("  ok   " if ok else "  FAIL ") + what, flush=True)
    if not ok:
        FAILURES.append(what)


def make_ckpt(path: Path, fold: int, seed: int, head_scale: float = 40.0) -> Path:
    torch.manual_seed(seed)
    cfg = copy.deepcopy(DEFAULT_CFG)
    cfg["classes"] = list(CLASSES)
    cfg["train"] = {"fold": fold, "early_stop_fold": fold, "kernel": "kds-test-random-init"}
    model = build_model(cfg)
    with torch.no_grad():
        model.head.weight.mul_(head_scale)
        model.head.bias.normal_(0.0, 0.5)
    payload = {"model_state": {k: v.detach().cpu() for k, v in model.state_dict().items()}, "config": cfg,
               "fold": int(fold), "epoch": 0, "val_loss": float("nan")}
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(payload, path)
    return path


def pick_videos(coords: pd.DataFrame, splits: dict[str, int]) -> list[str]:
    sizes = coords.groupby("stem").size()
    out = []
    for fold, emb in ((0, "44b6"), (1, "6bba")):
        cands = sorted(s for s, n in sizes.items() if splits.get(s) == fold and s.startswith(emb) and 3000 <= n <= 7000
                       and (DATA / f"{s}.zarr").exists())
        if not cands:
            raise SystemExit(f"no local video of fold {fold} / embryo {emb} with 3000-7000 rows")
        out.append(cands[0])
    return out


def rescore(stem: str, rows: pd.DataFrame, bundle: dict, reader, batch: int = 1) -> np.ndarray:
    bundle["prepared_frames"] = {}
    nodes = [{"t": int(r.t), "z": float(r.z), "y": float(r.y), "x": float(r.x)} for r in rows.itertuples()]
    return score_nodes(stem, nodes, bundle, {}, reader, batch=batch)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", type=int, default=1500, help="rows per video for the core-function test")
    ap.add_argument("--e2e-rows", type=int, default=250, help="rows per video for the end-to-end run")
    ap.add_argument("--out", default="", help="scratch dir (default: a new temp dir, removed at the end)")
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()
    t_all = time.time()
    tmp = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="kds_test_"))
    if tmp.exists() and args.out:
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    print(f"scratch {tmp}; torch {torch.__version__} threads {torch.get_num_threads()}")

    coords = kds_core.read_coords(COORDS)
    splits = kdn_core.load_splits(SPLITS)
    A, B = pick_videos(coords, splits)
    print(f"videos {A} (fold {splits[A]}, {int((coords.stem == A).sum())} rows) and {B} (fold {splits[B]}, "
          f"{int((coords.stem == B).sum())} rows)")

    # ---- checkpoints: a fake trainer output + decoys the discovery must ignore
    inp = tmp / "input"
    trainer = inp / "biohub-l2-kdn-train"
    ck = {0: make_ckpt(trainer / "folds" / "fold_0" / "best.pt", 0, seed=100),
          1: make_ckpt(trainer / "folds" / "fold_1" / "best.pt", 1, seed=101)}
    make_ckpt(trainer / "folds" / "fold_0" / "last.pt", 0, seed=900)                         # not best.pt
    make_ckpt(inp / "competitions" / "x" / "train" / "decoy.zarr" / "fold_2" / "best.pt", 2, seed=901)  # inside .zarr
    make_ckpt(inp / "some-dataset" / "best.pt", 3, seed=902)                                  # no fold_k dir
    (trainer / "splits_used.json").write_text(json.dumps(
        {"source": "kds test", "n_folds": 2, "folds": {A: splits[A], B: splits[B]}}, indent=1))
    (inp / "biohub-l2-coords").mkdir(parents=True, exist_ok=True)
    shutil.copy2(COORDS, inp / "biohub-l2-coords" / COORDS.name)

    print("\n[1] discovery")
    found = kds_core.discover_checkpoints(inp, "best.pt", "biohub-l2-kdn-train")
    check(found == ck, f"discover_checkpoints -> {{{', '.join(f'{k}: {v.relative_to(inp)}' for k, v in found.items())}}}")
    info = kds_core.inspect_checkpoints(found)
    check(sorted(info) == [0, 1] and all(v["fold"] == k for k, v in info.items()), "inspect_checkpoints fold ids")
    folds, sinfo = kds_core.resolve_splits({"splits": "", "train_slug": "biohub-l2-kdn-train"}, list(found.values()), inp)
    check(sinfo["primary"] == str(trainer / "splits_used.json") and folds[A] == splits[A] and folds[B] == splits[B]
          and len(folds) == len(splits), f"splits: primary splits_used.json, fallback embedded ({len(folds)} videos)")
    check(kds_core.find_coords({"coords": "", "coords_name": COORDS.name, "coords_slug": "biohub-l2-coords"}, inp)
          == inp / "biohub-l2-coords" / COORDS.name, "find_coords under the dataset dir")
    full = kds_core.select_rows(coords, kds_core.config_from_env({"stems": [], "max_videos": 0, "rows_per_video": 0}))
    check(len(full) == len(coords) == 1012255 and full.index.equals(coords.index),
          f"default selection = every input row in input order ({len(full)})")

    # ---- core function on CPU
    print("\n[2] core function kds_core.score_video (CPU)")
    bundle = load_daughternet([ck[0], ck[1]], device="cpu")
    single = {f: load_daughternet([ck[f]], device="cpu") for f in (0, 1)}
    reader = kdn_core.FrameReader(DATA)
    rng = np.random.default_rng(0)
    results = {}
    for stem in (A, B):
        g = coords[coords.stem == stem]
        g = g.iloc[rng.choice(len(g), size=min(args.rows, len(g)), replace=False)]  # random subset, shuffled order
        fold = splits[stem]
        t0 = time.time()
        p, st = kds_core.score_video(stem, g.t.to_numpy(), g.z.to_numpy(), g.y.to_numpy(), g.x.to_numpy(), bundle,
                                     reader, [fold], batch=128, frames=None, checks_fresh=2, checks_cached=3)
        secs = time.time() - t0
        df = pd.DataFrame({"stem": stem, "node_id": g.node_id.to_numpy(), "fold": np.int16(fold),
                           "p_cont": p[:, 0], "p_par": p[:, 1], "p_dau": p[:, 2]}, index=g.index)
        results[stem] = (g, df)
        print(f"  {stem}: {len(g)} rows in {secs:.1f} s ({len(g) / secs:.0f} rows/s CPU), frames {st['frames']}, "
              f"build {st['build_s']:.1f} s, frame prep {st['frame_wait_s']:.1f} s, model {st['model_s']:.1f} s; "
              f"p_par mean {p[:, 1].mean():.3f} std {p[:, 1].std():.3f} range [{p[:, 1].min():.3f}, {p[:, 1].max():.3f}]")
        check(p.shape == (len(g), 3) and p.dtype == np.float32, f"{stem} shape {p.shape} {p.dtype}")
        check(bool(np.isfinite(p).all()), f"{stem} all finite")
        check(float(np.abs(p.sum(1) - 1).max()) < TOL, f"{stem} rows sum to 1 (max |sum-1| {np.abs(p.sum(1) - 1).max():.1e})")
        check(st["checks_fresh"] == 2 and st["checks_cached"] == 3, f"{stem} contract checks 2 fresh + 3 cached passed")
        check(df.stem.eq(stem).all() and np.array_equal(df.node_id.to_numpy(), g.node_id.to_numpy())
              and df.index.equals(g.index), f"{stem} row alignment (stem, node_id, input order) preserved")
        check(bool((df.fold == splits[stem]).all()), f"{stem} fold column = splits fold {splits[stem]}")
        check(float(p[:, 1].std()) > 1e-3, f"{stem} p varies between nodes (p_par std {p[:, 1].std():.3f})")
        # re-score through tools.daughternet.score_nodes directly
        pick = list(dict.fromkeys([int(np.argmax(p[:, 1])), int(np.argmin(p[:, 1])), int(np.argmax(p[:, 2])),
                                   int(np.argmax(g.t.to_numpy())), int(np.argmin(g.z.to_numpy())),
                                   int(np.argmax(g.x.to_numpy())), *rng.choice(len(g), 6, replace=False).tolist()]))
        sub = g.iloc[pick]
        ref1 = rescore(stem, sub, single[fold], reader, batch=1)
        ref64 = rescore(stem, sub, single[fold], reader, batch=64)
        d1 = float(np.abs(ref1 - p[pick]).max())
        d64 = float(np.abs(ref64 - p[pick]).max())
        check(d1 < TOL and d64 < TOL, f"{stem} {len(pick)} rows (incl. t max, z min, x max) re-scored by score_nodes: "
                                      f"max |dp| {d1:.1e} (batch 1), {d64:.1e} (batch 64) < {TOL}")
        other = rescore(stem, sub, single[1 - fold], reader)
        shifted = sub.assign(x=sub.x + 8.0)
        d_other = float(np.abs(other - p[pick]).max())
        d_shift = float(np.abs(rescore(stem, shifted, single[fold], reader) - p[pick]).max())
        check(d_other > 100 * TOL and d_shift > 100 * TOL,
              f"{stem} controls: other fold's model |dp| {d_other:.3f}, x+8 voxel shift |dp| {d_shift:.3f} (>> tol)")

    g, df = results[A]
    sub = g.iloc[:300]
    fold = splits[A]
    prefetch = kds_core.FramePrefetcher(reader, kds_core.contract_params(bundle["config"]), threads=2)
    p_pre, _ = kds_core.score_video(A, sub.t, sub.z, sub.y, sub.x, bundle, reader, [fold], batch=128, frames=prefetch)
    prefetch.close()
    p_inl, _ = kds_core.score_video(A, sub.t, sub.z, sub.y, sub.x, bundle, reader, [fold], batch=128, frames=None)
    check(float(np.abs(p_pre - p_inl).max()) <= 1e-6, f"prefetch-thread path == inline path (max |dp| "
                                                       f"{np.abs(p_pre - p_inl).max():.1e})")
    check(float(np.abs(p_inl - df[kds_core.P_COLUMNS].to_numpy()[:300]).max()) < TOL,
          "subset re-run (different batch composition) matches the full-video run")

    g, _ = results[B]
    sub = g.iloc[:200]
    p_ens, _ = kds_core.score_video(B, sub.t, sub.z, sub.y, sub.x, bundle, reader, None, batch=64)
    ref = rescore(B, sub.iloc[:6], bundle, reader, batch=64)
    check(float(np.abs(ref - p_ens[:6]).max()) < TOL and float(np.abs(p_ens.sum(1) - 1).max()) < TOL,
          f"ensemble (mean of 2 fold models) == score_nodes with both models (max |dp| {np.abs(ref - p_ens[:6]).max():.1e})")

    # ---- end to end, 2 CPU worker processes
    print("\n[3] end-to-end kds_core.run (2 CPU worker processes, oof + ens)")
    cfg = kds_core.config_from_env({
        "work_dir": str(tmp / "work"), "input_root": str(inp), "ckpt_root": "", "coords": "", "splits": "",
        "data_dir": str(DATA), "stems": [A, B], "max_videos": 0, "rows_per_video": args.e2e_rows, "seed": 0,
        "modes": ["oof", "ens"], "gpus": 0, "workers": 2, "frame_threads": 2, "batch": 64, "verify_per_fold": 3,
        "verify_tol": TOL, "expect_folds": 2, "retries": 1, "resume": True})
    t0 = time.time()
    state = kds_core.run(cfg)
    print(f"  run 1: {time.time() - t0:.1f} s")
    sel = kds_core.select_rows(coords, cfg)
    outs = {}
    for mode in ("oof", "ens"):
        out = pd.read_parquet(tmp / "work" / kds_core.OUTPUTS[mode])
        summ = json.loads((tmp / "work" / f"node_p_{mode}_summary.json").read_text())
        outs[mode] = out
        pv = out[kds_core.P_COLUMNS].to_numpy(np.float64)
        check(list(out.columns) == kds_core.OUT_COLUMNS, f"{mode}: columns {list(out.columns)}")
        check(len(out) == len(sel) == 2 * args.e2e_rows and np.array_equal(out.stem.to_numpy(), sel.stem.to_numpy())
              and np.array_equal(out.node_id.to_numpy(), sel.node_id.to_numpy()),
              f"{mode}: {len(out)} rows aligned to the selection (stem, node_id, input order)")
        check(bool((out.fold.to_numpy() == sel.stem.map(splits).to_numpy()).all()), f"{mode}: fold column = splits fold")
        check(summ["nan_rows"] == 0 and bool(np.isfinite(pv).all()) and float(np.abs(pv.sum(1) - 1).max()) < TOL,
              f"{mode}: no NaN, rows sum to 1")
        check(summ["verify"]["pass"] and summ["verify"]["checked"] >= 4,
              f"{mode}: summary verify {summ['verify']['checked']} rows via score_nodes max |dp| "
              f"{summ['verify']['max_abs_diff']:.1e} <= {TOL}")
        check(sorted(summ["checkpoints"]) == ["0", "1"] and all(summ["checkpoints"][str(k)]["path"] == str(v)
                                                                for k, v in ck.items()),
              f"{mode}: summary checkpoints are the fold_k/best.pt files only")
        check(summ["rows_per_fold"] == {str(splits[A]): args.e2e_rows, str(splits[B]): args.e2e_rows}
              and summ["videos"]["scored_this_run"] == 2 and len(summ["timing"]["workers"]) == 2,
              f"{mode}: rows per fold {summ['rows_per_fold']}, 2 videos on 2 workers "
              f"{[w['rows'] for w in summ['timing']['workers']]}")
    # OOF rows that are also in the core-test subsample must agree with the core function
    core = pd.concat([results[A][1], results[B][1]])
    both = outs["oof"].merge(core, on=["stem", "node_id"], suffixes=("", "_core"))
    dmax = float(np.abs(both[kds_core.P_COLUMNS].to_numpy() -
                        both[[c + "_core" for c in kds_core.P_COLUMNS]].to_numpy()).max()) if len(both) else float("nan")
    check(len(both) > 20 and dmax < TOL, f"e2e OOF vs core function on {len(both)} shared rows: max |dp| {dmax:.1e}")
    check(float(np.abs(outs["oof"][kds_core.P_COLUMNS].to_numpy() - outs["ens"][kds_core.P_COLUMNS].to_numpy()).max())
          > 100 * TOL, "ens differs from oof")

    t0 = time.time()
    kds_core.run(cfg)
    print(f"  run 2 (resume): {time.time() - t0:.1f} s")
    for mode in ("oof", "ens"):
        summ = json.loads((tmp / "work" / f"node_p_{mode}_summary.json").read_text())
        again = pd.read_parquet(tmp / "work" / kds_core.OUTPUTS[mode])
        check(summ["videos"]["resumed"] == 2 and summ["videos"]["scored_this_run"] == 0 and again.equals(outs[mode]),
              f"{mode}: rerun resumed both videos from parts/ and reproduced the output exactly")

    # partial resume: only A's OOF part is missing -> A is rescored with its single fold model (not the joint pass)
    (tmp / "work" / "parts" / "oof" / f"{A}.parquet").unlink()
    t0 = time.time()
    kds_core.run(cfg)
    print(f"  run 3 (A's oof part deleted): {time.time() - t0:.1f} s")
    s_oof = json.loads((tmp / "work" / "node_p_oof_summary.json").read_text())
    s_ens = json.loads((tmp / "work" / "node_p_ens_summary.json").read_text())
    rec = [r for w in s_oof["timing"]["workers"] for r in json.loads(
        (tmp / "work" / "parts" / "_run" / f"_worker_{w['worker']}_attempt0.json").read_text())["records"]]
    again = pd.read_parquet(tmp / "work" / kds_core.OUTPUTS["oof"])
    d3 = float(np.abs(again[kds_core.P_COLUMNS].to_numpy() - outs["oof"][kds_core.P_COLUMNS].to_numpy()).max())
    check(s_oof["videos"]["resumed"] == 1 and s_oof["videos"]["scored_this_run"] == 1
          and s_ens["videos"]["resumed"] == 2 and s_ens["videos"]["scored_this_run"] == 0
          and len(rec) == 1 and rec[0]["stem"] == A and rec[0]["modes"] == ["oof"] and rec[0]["models"] == 1,
          f"partial rerun scored only {[(r['stem'], r['modes'], r['models']) for r in rec]}")
    check(d3 < TOL and pd.read_parquet(tmp / "work" / kds_core.OUTPUTS["ens"]).equals(outs["ens"]),
          f"single-model OOF path == joint-pass OOF (max |dp| {d3:.1e}); ens output unchanged")

    print(f"\n{'PASS' if not FAILURES else 'FAIL'}: {len(FAILURES)} failures in {time.time() - t_all:.0f} s")
    for f in FAILURES:
        print("  -", f)
    if not args.keep and not args.out:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
