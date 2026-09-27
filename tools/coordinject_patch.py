"""--patch coordinject (x138 base): yuki0731/biohub-coord-inject as a final post-step on the written submission.csv.

research/wf_ideas_v4/bigger_levers/prep_coord_refiner.notes.md. The CC0 dataset yuki0731/biohub-coord-inject (team LMM,
public 0.961) ships coord_inject_runtime.py + 4 Dense2 detector seeds (UNet3D base 24 + offset head, xy pooled 4x, 4 flip
views each) + a z refiner and an xy refiner. Its rule (inject_one): every predicted node moves to the nearest refined
detection of the same frame if that detection lies within max_um (3.0 um), new = (1 - alpha) * old + alpha * target
(alpha 1.0). Node set, ids and edges are unchanged.

Here it runs AFTER write_test_submission (a new code cell right after x138's post-processing cell, before the submission
guard / validator cells), so the whole K2 tail (deadlines, insertion, forkmid ...) is untouched:
  1. find the dataset (COORD_INJECT_MANIFEST.json under /kaggle/input, or BIOHUB_COORDINJECT_DIR), sha256-check the
     runtime module and the 6 checkpoints it loads;
  2. one worker subprocess per GPU (<= BIOHUB_COORDINJECT_WORKERS, default 2), test stems interleaved, each imports the
     dataset's coord_inject_runtime.py VERBATIM and runs detector_cache_for_video + apply_axis_refiners per video, writing
     /kaggle/working/coordinject/<stem>.npz atomically; a worker starts no new video once
     now + 1.25 x (its slowest video so far, first video 300 s) passes the deadline
     KERNEL_START_TS + BIOHUB_COORDINJECT_DEADLINE_S (default 37800 = 10.5 h); the main process kills workers still alive
     at deadline + 900 s;
  3. stream-rewrite submission.csv: node rows of every video with an npz get the injected z/y/x (integers like the x138
     writer, max(0, round(v)) clipped to the volume; a float cell stays float with 3 decimals); every other byte is
     copied; the tmp file must have the same line count, then os.replace. Videos without an npz keep their rows.
Fail-soft: any exception -> 'COORDINJECT FAILED', submission.csv is left exactly as K2 wrote it (the replace is the last
step). BIOHUB_COORDINJECT_ENABLE=0 (default) -> the cell prints one line and does nothing (byte-identical CSV).
Knobs (--set, without BIOHUB_): COORDINJECT_ENABLE 0|1, COORDINJECT_MAX_UM (3.0, (0, 7]), COORDINJECT_ALPHA (1.0,
(0, 1]), COORDINJECT_DEADLINE_S (37800; non-lab builds 3600..39600), COORDINJECT_WORKERS (2; 1..2), COORDINJECT_AMP
(0: refiners in fp32; 1 = the runtime's bf16 autocast), COORDINJECT_DIR (''), COORDINJECT_FORCE_FAIL (--lab only).
Log: 'COORDINJECT_WORKER <stem> ...' per video, 'COORDINJECT <stem>: replaced R/N ...', 'COORDINJECT SUMMARY: ...'.
"""
from __future__ import annotations

DATASET = "yuki0731/biohub-coord-inject"
# sha256 of the files the post-step imports / loads (dataset version of 25 Aug 2026, pulled 27 Sep 2026)
SHA256 = {
    "coord_inject_runtime.py": "af3d8537f4f8d57a7c44ba6a237b25f82e4178751b4b10b571e77bd04816cbed",
    "D_mix_offpeak_mix_s0_ep0.pt": "2ff7dd30b9e685c59fb414af6583b42561405885272c8045782d9ccca4d5bd65",
    "M_seed1_offpeak_mix_s1_ep0.pt": "f9ecfe7de2e1099f96f3f97af0529f80cdbfdd2848cb8dc3c253e6e66319c0e1",
    "M_seed2_offpeak_mix_s2_ep0.pt": "2537b6bfe7187aacd4565cdef67014464f357613735b268e4dec7eeaa913b176",
    "M_seed3_offpeak_mix_s3_ep0.pt": "b16072a007069090af8d84ed7a05c27c37684be99589a435d00153737d20e335",
    "R_ens4off_tr171_z_s0_ep6.pt": "e0919797da9ccf523b55bde8a720ee335b5f96e8df8ca94d49dad06907bd4461",
    "RprojQ_ens4off_tr171_xy_s0_ep1.pt": "f9d25c6a0d956d48e478255dd106ff1529ad1018e3889e854a5e3b40965bfdc4",
}
KNOBS = ("BIOHUB_COORDINJECT_ENABLE", "BIOHUB_COORDINJECT_MAX_UM", "BIOHUB_COORDINJECT_ALPHA",
         "BIOHUB_COORDINJECT_DEADLINE_S", "BIOHUB_COORDINJECT_WORKERS", "BIOHUB_COORDINJECT_AMP",
         "BIOHUB_COORDINJECT_DIR", "BIOHUB_COORDINJECT_FORCE_FAIL")
SUBMIT_DEADLINE_RANGE = (3600.0, 39600.0)

# The worker: one process per GPU, the dataset's runtime module verbatim (run_coord_injection's device setup, detector
# list and refiner files), one npz per video. argv[1] = json args.
WORKER_SRC = r'''"""coordinject worker (tools/coordinject_patch.py): yuki0731 coord_inject_runtime.py verbatim, one npz per video."""
import json
import os
import sys
import time
import traceback
from pathlib import Path

import numpy as np

args = json.loads(sys.argv[1])
sys.path.insert(0, args["weights_dir"])  # the dataset's coord_inject_runtime.py (sha256-checked by the caller)
import torch  # noqa: E402

import coord_inject_runtime as R  # noqa: E402

torch.set_num_threads(int(args.get("threads", 2)))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
if device.type == "cuda":
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
W = Path(args["weights_dir"])
t_load = time.time()
models = [R.load_detector(W / name, device) for name in args["detectors"]]
z_spec = R.load_refiner(W / args["z_refiner"], device)
xy_spec = R.load_refiner(W / args["xy_refiner"], device)
print(f"COORDINJECT_WORKER start shard={args['shard']} device={device} "
      f"gpu={torch.cuda.get_device_name(0) if device.type == 'cuda' else '-'} stems={len(args['stems'])} "
      f"load={time.time() - t_load:.1f}s", flush=True)
out_dir = Path(args["out_dir"])
seconds = []
for stem in args["stems"]:
    est = 1.25 * max(seconds) if seconds else float(args["first_est_s"])
    if time.time() + est > float(args["deadline_ts"]):
        print(f"COORDINJECT_WORKER SKIP (deadline) {stem} and the rest of shard {args['shard']}: est {est:.0f}s", flush=True)
        break
    t0 = time.time()
    try:
        zarr_path = Path(args["test_dir"]) / f"{stem}.zarr"
        meta = R.read_array_meta(zarr_path)
        cache = R.detector_cache_for_video(stem, zarr_path, models, device)
        refined = R.apply_axis_refiners(cache, z_spec, xy_spec, device, amp=bool(int(args["amp"])))
        tmp = out_dir / f"{stem}.tmp.npz"
        np.savez(tmp, raw_ref=refined["raw_ref"], scores=refined["scores"], offsets=refined["offsets"],
                 T=refined["T"], shape=np.asarray(meta["shape"], dtype=np.int64))
        os.replace(tmp, out_dir / f"{stem}.npz")
    except Exception as exc:
        traceback.print_exc()
        print(f"COORDINJECT_WORKER FAILED {stem} ({type(exc).__name__}: {exc})", flush=True)
        continue
    seconds.append(time.time() - t0)
    print(f"COORDINJECT_WORKER {stem}: T={int(refined['T'])} dets={len(refined['scores'])} "
          f"dz={refined['median_abs_dz']:.3f} dxy={refined['median_abs_dxy']:.3f} {seconds[-1]:.1f}s", flush=True)
print(f"COORDINJECT_WORKER done shard={args['shard']} videos={len(seconds)} "
      f"sec_total={sum(seconds):.0f} sec_max={max(seconds) if seconds else 0:.0f}", flush=True)
'''

# The injection rule of coord_inject_runtime.inject_one on the CSV's node rows (no tracksdata / geff round trip).
INJECT_FN = r'''def coordinject_positions(old_zyx, times, refined, max_um=3.0, alpha=1.0):
    """inject_one's rule: each node -> nearest refined detection of its frame (distance in um, SCALE) if <= max_um,
    new = (1 - alpha) * old + alpha * target. Returns (new_zyx float64, replaced bool mask, nn distance um or nan)."""
    from scipy.spatial import cKDTree

    scale = np.array([1.625, 0.40625, 0.40625], dtype=np.float64)
    old = np.asarray(old_zyx, dtype=np.float64).reshape(-1, 3)
    times = np.asarray(times, dtype=np.int64).reshape(-1)
    new = old.copy()
    replaced = np.zeros(len(old), dtype=bool)
    dist = np.full(len(old), np.nan)
    coords = np.asarray(refined["raw_ref"], dtype=np.float64).reshape(-1, 3)
    offsets = np.asarray(refined["offsets"], dtype=np.int64).reshape(-1)
    for t in np.unique(times):
        if t < 0 or t + 1 >= len(offsets):
            continue
        cand = coords[int(offsets[t]):int(offsets[t + 1])]
        if not len(cand):
            continue
        idx_nodes = np.flatnonzero(times == t)
        d, j = cKDTree(cand * scale).query(old[idx_nodes] * scale, k=1)
        dist[idx_nodes] = d
        ok = d <= max_um
        sel = idx_nodes[ok]
        new[sel] = (1.0 - alpha) * old[sel] + alpha * cand[j[ok]]
        replaced[sel] = True
    return new, replaced, dist


def coordinject_cell(value, hi, is_float):
    """One CSV coordinate cell: the x138 writer's integer max(0, round(v)) clipped to hi, or 3 decimals (floatout)."""
    v = min(max(float(value), 0.0), float(hi))
    return f"{v + 0.0:.3f}" if is_float else str(max(0, min(int(round(v)), int(hi))))


def coordinject_rewrite_csv(path, refined_by_stem, max_um=3.0, alpha=1.0):
    """Two streaming passes over submission.csv: collect the node rows of the refined videos, then copy every line,
    replacing only the z/y/x cells of those rows. Writes <path>.coordinject.tmp and returns (tmp, stats); the caller
    replaces the CSV. Columns: id,dataset,row_type,node_id,t,z,y,x,source_id,target_id."""
    path = Path(path)
    rows = {}
    with path.open("r", newline="") as f:
        header = f.readline().rstrip("\r\n").split(",")
        col = {c: i for i, c in enumerate(header)}
        for key in ("dataset", "row_type", "t", "z", "y", "x"):
            assert key in col, f"coordinject: submission.csv has no {key} column"
        for ln, line in enumerate(f, start=1):
            parts = line.rstrip("\r\n").split(",")
            if len(parts) != len(header):
                raise ValueError(f"coordinject: line {ln} has {len(parts)} fields")
            if parts[col["row_type"]] == "node" and parts[col["dataset"]] in refined_by_stem:
                rows.setdefault(parts[col["dataset"]], []).append(
                    (ln, int(parts[col["t"]]), float(parts[col["z"]]), float(parts[col["y"]]), float(parts[col["x"]]),
                     "." in parts[col["z"]] + parts[col["y"]] + parts[col["x"]]))
    new_cells = {}
    stats = {}
    for stem, recs in rows.items():
        ref = refined_by_stem[stem]
        arr = np.asarray([r[1:5] for r in recs], dtype=np.float64)
        new, replaced, dist = coordinject_positions(arr[:, 1:4], arr[:, 0].astype(np.int64), ref, max_um, alpha)
        shape = np.asarray(ref["shape"], dtype=np.int64).reshape(-1)[-3:]
        hi = shape - 1
        moved = 0
        for k, r in enumerate(recs):
            if not replaced[k]:
                continue
            cells = [coordinject_cell(new[k, a], hi[a], r[5]) for a in range(3)]
            olds = [coordinject_cell(arr[k, 1 + a], hi[a], r[5]) for a in range(3)]
            if cells != olds:
                moved += 1
            new_cells[r[0]] = cells
        shift = np.linalg.norm((new[replaced] - arr[replaced, 1:4]) * np.array([1.625, 0.40625, 0.40625]), axis=1)
        finite = dist[np.isfinite(dist)]
        stats[stem] = {"nodes": len(recs), "replaced": int(replaced.sum()), "moved_cells": moved,
                       "replace_frac": float(replaced.mean()) if len(recs) else 0.0,
                       "median_shift_um": float(np.median(shift)) if len(shift) else 0.0,
                       "p95_shift_um": float(np.percentile(shift, 95)) if len(shift) else 0.0,
                       "median_nn_um": float(np.median(finite)) if len(finite) else float("nan")}
    tmp = path.with_name(path.name + ".coordinject.tmp")
    n_in = 0
    with path.open("r", newline="") as f, tmp.open("w", newline="") as g:
        g.write(f.readline())
        zi, yi, xi = col["z"], col["y"], col["x"]
        for ln, line in enumerate(f, start=1):
            n_in += 1
            cells = new_cells.get(ln)
            if cells is None:
                g.write(line)
                continue
            end = line[len(line.rstrip("\r\n")):]
            parts = line.rstrip("\r\n").split(",")
            parts[zi], parts[yi], parts[xi] = cells
            g.write(",".join(parts) + end)
    with tmp.open("r", newline="") as g:
        n_out = sum(1 for _ in g) - 1
    if n_out != n_in:
        raise RuntimeError(f"coordinject: tmp has {n_out} data lines, submission.csv {n_in}")
    return tmp, stats
'''

CELL_SRC = (r'''# ---- coordinject (tools/build_probe_kernel.py --patch coordinject; tools/coordinject_patch.py) ----
# yuki0731/biohub-coord-inject (CC0, team LMM 0.961) as a final post-step on submission.csv: each node moves to the
# nearest refined detection of its frame within BIOHUB_COORDINJECT_MAX_UM (inject_one's rule); nodes / ids / edges are
# unchanged. BIOHUB_COORDINJECT_ENABLE=0 (default) -> nothing runs, submission.csv byte-identical. Fail-soft: any
# exception leaves submission.csv exactly as the writer produced it ('COORDINJECT FAILED').
import hashlib as _ci_hashlib
import json as _ci_json
import subprocess as _ci_subprocess
import sys as _ci_sys
import time as _ci_time
import traceback as _ci_traceback
from pathlib import Path

import numpy as np

COORDINJECT_ENABLE = os.environ.get("BIOHUB_COORDINJECT_ENABLE", "0").strip() not in ("", "0")
COORDINJECT_SHA256 = ''' + repr(SHA256) + r'''
COORDINJECT_DETECTORS = ["D_mix_offpeak_mix_s0_ep0.pt", "M_seed1_offpeak_mix_s1_ep0.pt", "M_seed2_offpeak_mix_s2_ep0.pt",
                         "M_seed3_offpeak_mix_s3_ep0.pt"]
COORDINJECT_WORKER_SRC = ''' + repr(WORKER_SRC) + r'''
COORDINJECT_WORK = Path(os.environ.get("BIOHUB_COORDINJECT_WORK", "/kaggle/working"))  # tests only; not a --set knob
COORDINJECT_OUT = COORDINJECT_WORK / "coordinject"
COORDINJECT_STATE = {"status": "disabled", "videos": 0, "replaced": 0, "nodes": 0}


''' + INJECT_FN + r'''

def coordinject_find_dir():
    env = os.environ.get("BIOHUB_COORDINJECT_DIR", "").strip()
    cands = [Path(env)] if env else []
    for pat in ("*", "*/*", "*/*/*", "*/*/*/*"):
        cands += sorted(p.parent for p in Path("/kaggle/input").glob(pat + "/COORD_INJECT_MANIFEST.json"))
    for d in cands:
        if all((d / name).is_file() for name in COORDINJECT_SHA256):
            return d
    raise FileNotFoundError(f"coordinject: no dataset folder with {sorted(COORDINJECT_SHA256)} (checked {len(cands)})")


def coordinject_check_sha(d):
    for name, want in COORDINJECT_SHA256.items():
        h = _ci_hashlib.sha256()
        with (d / name).open("rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                h.update(block)
        if h.hexdigest() != want:
            raise RuntimeError(f"coordinject: sha256 mismatch for {name}: {h.hexdigest()} != {want}")


def coordinject_run():
    t_start = _ci_time.time()
    max_um = float(os.environ.get("BIOHUB_COORDINJECT_MAX_UM", "3.0"))
    alpha = float(os.environ.get("BIOHUB_COORDINJECT_ALPHA", "1.0"))
    deadline_s = float(os.environ.get("BIOHUB_COORDINJECT_DEADLINE_S", "37800"))
    n_workers = int(os.environ.get("BIOHUB_COORDINJECT_WORKERS", "2"))
    amp = os.environ.get("BIOHUB_COORDINJECT_AMP", "0").strip() or "0"
    if not (0.0 < max_um <= 7.0 and 0.0 < alpha <= 1.0 and n_workers >= 1):
        raise ValueError(f"coordinject knobs out of range: max_um={max_um} alpha={alpha} workers={n_workers}")
    if os.environ.get("BIOHUB_COORDINJECT_FORCE_FAIL", "0") != "0":
        raise RuntimeError("BIOHUB_COORDINJECT_FORCE_FAIL=1 (dummy test of the fail-soft path)")
    kernel_start = float(globals().get("KERNEL_START_TS", t_start))
    deadline_ts = kernel_start + deadline_s
    if t_start > deadline_ts - 600:
        COORDINJECT_STATE["status"] = "skipped_deadline"
        print(f"COORDINJECT SKIPPED (deadline): kernel elapsed {t_start - kernel_start:.0f}s, deadline {deadline_s:.0f}s",
              flush=True)
        return
    import torch as _ci_torch

    n_gpu = _ci_torch.cuda.device_count()
    if n_gpu == 0:
        COORDINJECT_STATE["status"] = "skipped_no_gpu"
        print("COORDINJECT SKIPPED (no GPU)", flush=True)
        return
    wdir = coordinject_find_dir()
    coordinject_check_sha(wdir)
    stems = list(test_stems)
    n_workers = max(1, min(n_workers, n_gpu, len(stems)))
    COORDINJECT_OUT.mkdir(parents=True, exist_ok=True)
    for old in COORDINJECT_OUT.glob("*.npz"):
        old.unlink()
    worker = COORDINJECT_OUT / "coordinject_worker.py"
    worker.write_text(COORDINJECT_WORKER_SRC)
    procs = []
    for i in range(n_workers):
        wargs = {"weights_dir": str(wdir), "detectors": COORDINJECT_DETECTORS, "z_refiner": "R_ens4off_tr171_z_s0_ep6.pt",
                 "xy_refiner": "RprojQ_ens4off_tr171_xy_s0_ep1.pt", "stems": stems[i::n_workers], "shard": i,
                 "test_dir": str(TEST_DIR), "out_dir": str(COORDINJECT_OUT), "deadline_ts": deadline_ts,
                 "first_est_s": 300.0, "amp": amp, "threads": 2}
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(i), OMP_NUM_THREADS="2", PYTHONUNBUFFERED="1")
        log = (COORDINJECT_OUT / f"worker_{i}.log").open("w")
        procs.append((_ci_subprocess.Popen([_ci_sys.executable, str(worker), _ci_json.dumps(wargs)], env=env,
                                           stdout=log, stderr=_ci_subprocess.STDOUT), log))
    print(f"COORDINJECT: {n_workers} worker(s) on {n_gpu} GPU(s), {len(stems)} videos, dataset {wdir}, "
          f"max_um={max_um} alpha={alpha} amp={amp}, kernel elapsed {t_start - kernel_start:.0f}s, "
          f"deadline {deadline_s:.0f}s", flush=True)
    try:
        while any(p.poll() is None for p, _ in procs) and _ci_time.time() < deadline_ts + 900:
            _ci_time.sleep(10)
    finally:
        for p, log in procs:
            if p.poll() is None:
                p.kill()
                print(f"COORDINJECT: worker pid {p.pid} killed at the deadline", flush=True)
            p.wait()
            log.close()
    for i in range(n_workers):
        print((COORDINJECT_OUT / f"worker_{i}.log").read_text()[-20000:], flush=True)
    t_workers = _ci_time.time() - t_start
    refined = {}
    for stem in stems:
        p = COORDINJECT_OUT / f"{stem}.npz"
        if p.is_file():
            with np.load(p) as z:
                refined[stem] = {k: z[k] for k in z.files}
    if not refined:
        COORDINJECT_STATE["status"] = "no_videos"
        print("COORDINJECT: no video was refined; submission.csv unchanged", flush=True)
        return
    tmp, stats = coordinject_rewrite_csv(SUBMISSION_PATH, refined, max_um=max_um, alpha=alpha)
    os.replace(tmp, SUBMISSION_PATH)
    for stem in sorted(stats):
        s = stats[stem]
        print(f"COORDINJECT {stem}: replaced {s['replaced']}/{s['nodes']} ({s['replace_frac']:.3f}) moved_cells "
              f"{s['moved_cells']} shift_med={s['median_shift_um']:.3f}um p95={s['p95_shift_um']:.3f}um "
              f"nn_med={s['median_nn_um']:.3f}um", flush=True)
    n_nodes = sum(s["nodes"] for s in stats.values())
    n_rep = sum(s["replaced"] for s in stats.values())
    n_mov = sum(s["moved_cells"] for s in stats.values())
    COORDINJECT_STATE.update(status="applied", videos=len(refined), replaced=n_rep, nodes=n_nodes)
    (COORDINJECT_WORK / "coordinject_summary.json").write_text(_ci_json.dumps(
        {"videos": len(refined), "of": len(stems), "nodes": n_nodes, "replaced": n_rep, "moved_cells": n_mov,
         "max_um": max_um, "alpha": alpha, "worker_seconds": t_workers, "seconds": _ci_time.time() - t_start,
         "per_video": stats}, indent=1, sort_keys=True))
    print(f"COORDINJECT SUMMARY: videos={len(refined)}/{len(stems)} nodes={n_nodes} replaced={n_rep} "
          f"({n_rep / max(n_nodes, 1):.3f}) moved_cells={n_mov} workers {t_workers:.0f}s total "
          f"{_ci_time.time() - t_start:.0f}s | kernel elapsed {_ci_time.time() - kernel_start:.0f}s", flush=True)


if COORDINJECT_ENABLE:
    try:
        coordinject_run()
    except Exception as _ci_exc:
        _ci_traceback.print_exc()
        COORDINJECT_STATE["status"] = "failed"
        _ci_tmp = Path(str(SUBMISSION_PATH) + ".coordinject.tmp")
        if _ci_tmp.exists():
            _ci_tmp.unlink()
        print(f"COORDINJECT FAILED ({type(_ci_exc).__name__}: {_ci_exc}); submission.csv unchanged", flush=True)
else:
    print("coordinject disabled (BIOHUB_COORDINJECT_ENABLE=0): submission.csv unchanged")
''')


def patch(cells_src: dict, post_index: int, new_cells_key: str) -> None:
    """New code cell right after the base post-processing cell (x138 base code cell 5: write_test_submission('base')),
    i.e. before the submission guard, validator and manifest cells."""
    cells_src.setdefault(new_cells_key, []).append((post_index, CELL_SRC))


def meta(meta_json: dict, overrides: dict) -> None:
    """Attach the CC0 dataset when the step is switched on."""
    if overrides.get("BIOHUB_COORDINJECT_ENABLE", "0").strip() not in ("", "0") and DATASET not in meta_json["dataset_sources"]:
        meta_json["dataset_sources"].append(DATASET)


def check(base: str, patches: list, overrides: dict, lab: bool) -> str | None:
    """Builder-side refusals; returns an error message or None."""
    ci = {k: v for k, v in overrides.items() if k.startswith("BIOHUB_COORDINJECT_")}
    if ci and "coordinject" not in patches:
        return "COORDINJECT_* knobs need --patch coordinject"
    if "coordinject" not in patches:
        return None
    if base != "x138":
        return "--patch coordinject needs --base x138"
    unknown = sorted(k for k in ci if k not in KNOBS)
    if unknown:
        return f"unknown coordinject knobs {unknown}; known: {list(KNOBS)}"
    for k in ("BIOHUB_COORDINJECT_ENABLE", "BIOHUB_COORDINJECT_AMP", "BIOHUB_COORDINJECT_FORCE_FAIL"):
        if ci.get(k, "0") not in ("0", "1"):
            return f"{k.removeprefix('BIOHUB_')} must be 0 or 1, got {ci[k]!r}"
    if ci.get("BIOHUB_COORDINJECT_FORCE_FAIL", "0") != "0" and not lab:
        return "COORDINJECT_FORCE_FAIL is a dummy test knob: needs --lab"
    try:
        max_um = float(ci.get("BIOHUB_COORDINJECT_MAX_UM", "3.0"))
        alpha = float(ci.get("BIOHUB_COORDINJECT_ALPHA", "1.0"))
        dl = float(ci.get("BIOHUB_COORDINJECT_DEADLINE_S", "37800"))
        workers = int(ci.get("BIOHUB_COORDINJECT_WORKERS", "2"))
    except ValueError as exc:
        return f"coordinject knob is not a number: {exc}"
    if not 0.0 < max_um <= 7.0:
        return f"COORDINJECT_MAX_UM must be in (0, 7], got {max_um}"
    if not 0.0 < alpha <= 1.0:
        return f"COORDINJECT_ALPHA must be in (0, 1], got {alpha}"
    if workers not in (1, 2):
        return f"COORDINJECT_WORKERS must be 1 or 2, got {workers}"
    lo, hi = SUBMIT_DEADLINE_RANGE
    if not lab and not lo <= dl <= hi:
        return f"COORDINJECT_DEADLINE_S must be in [{lo:.0f}, {hi:.0f}] for a submission build (got {dl:.0f}); --lab for others"
    if lab and not 0.0 <= dl < float("inf"):
        return f"COORDINJECT_DEADLINE_S must be finite and >= 0, got {dl}"
    if ci.get("BIOHUB_COORDINJECT_ENABLE", "0") == "0":
        print("NOTE: --patch coordinject with COORDINJECT_ENABLE=0 (default) writes a byte-identical submission.csv")
    return None
