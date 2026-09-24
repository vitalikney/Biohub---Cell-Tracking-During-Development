"""Build PRIVATE Kaggle GPU kernels that capture x138/V1284 coordinate-head training data on TRAIN videos.

The kernel is exp51's notebook (experiments/exp51_coordhead, = exp48 + --patch coordhead, probe 31) with
BIOHUB_COORDHEAD_MODE=capture, cut after the prediction cell. Everything that decides peaks and features is exp51's
code verbatim: cell 0 knobs (det 0.965, ...), cell 3 setup (primary + secondary seed314159, secondary detection
weight 0.80, retention guard 0.90), cell 5 predict-script patches (D4 detection TTA, dual-seed blend, edge-feature TTA
= the 8-view averaged primary UNet map the head reads, secondary edge TTA 0.75, x138's V1284 block). Changes, none of
which touches a peak or a feature:
  cell 0  + BIOHUB_COORDHEAD_MODE=capture and the capture knobs (V1284_CAPTURE*, below);
  cell 3  the secondary-manifest lookup tries the three explicit mount paths before the full /kaggle/input rglob
          (x138's order; ~3.5 min less setup; same result: the original returns the first sha256 match, and the
          explicit paths come first in its candidate list too);
  cell 5  TEST_DIR -> <competition>/train and test_stems -> this shard's stems; a capture-only patch of the predict
          script (the edge-transformer loop runs zero pairs, predict() skips build_graph / ILP / save_graph and instead
          compacts the video's per-frame x138 capture files); no geff merge; a capture summary; cleanup of the repo
          copy so only the capture is in the output;
  cells 6-14 (DivNet, divinsert, post-processing tail, writer) are dropped; DivNet / ft-weights datasets detached.

Per video the kernel writes /kaggle/working/capture/<stem>.npz (np.savez_compressed):
  coords (M,4) int16       x138's arr = [t, z, y, x] integer peaks in the (1,4,4)-downsampled grid (1.625 um isotropic)
  features (M,224) float32 x138's sample_features(unet_out[:, f_idx], arr), bit-exact
  near_gt (M,) bool        peak within KEEP_UM (default 10 um) of a GT node of the same frame
  sampled (M,) bool        uniform random SAMPLE share (default 1 %) of ALL peaks (rng seeded by crc32(stem))
  nearest_gt_um (M,) f32   distance to the nearest same-frame GT node (inf: frame without GT)
  frame_t, frame_peaks     peaks per frame (all peaks)
  feat_sum, feat_sumsq (224,) float64, n_all   exact all-peak feature moments (for standardisation)
plus a line in capture/manifest_<gpu shard>.jsonl and capture/capture_summary_<kernel shard>.json (timings, sizes).
M ~ 3-4 peaks per GT node (+1 % of all peaks): ~1-3 MB per video instead of ~30-70 MB for x138's raw per-frame dump.

Usage (from the repo root):
  python experiments/coordhead_retrain/build_capture_kernel.py pilot --stems 44b6_a,44b6_b,44b6_c,6bba_a,6bba_b,6bba_c
  python experiments/coordhead_retrain/build_capture_kernel.py full --shards 4          # builds s0of4 .. s3of4
  ... add --push to push (one `kaggle kernels push` per built folder; Kaggle allows 2 concurrent GPU sessions).
Output: experiments/coordhead_retrain/kernels/chcap-<name>/ (notebook + kernel-metadata.json) and
experiments/coordhead_retrain/capture_plan.json (shard -> stems).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BASE_NB = ROOT / "experiments/exp51_coordhead/exp51-coordhead.ipynb"
BASE_META = ROOT / "experiments/exp51_coordhead/kernel-metadata.json"
TRAIN_DIR = ROOT / "biohub-cell-tracking-during-development/train"
SPLITS = ROOT / "experiments/l2_daughternet/splits.json"
NL = chr(10)
DROP_DATASETS = ("giorgosi/biohub-divnet-v2", "vitaliineibauer/biohub-ft-weights")
CAPTURE_KNOBS = {
    "BIOHUB_COORDHEAD_MODE": "capture",
    "V1284_CAPTURE": "/tmp/v1284_raw",            # x138's per-frame files (deleted after each video's compaction)
    "V1284_CAPTURE_ONLY": "1",                     # stop after detection + capture (no edges / graph / ILP)
    "V1284_CAPTURE_OUT": "/kaggle/working/capture",
    "V1284_CAPTURE_KEEP_UM": "10.0",               # keep peaks within 10 um of a same-frame GT node (4 um match + 2 um
                                                   # head cap + 7 um count margin)
    "V1284_CAPTURE_SAMPLE": "0.01",                # + 1 % of all peaks (all-peak shift / feature distribution)
}


def _rep1(s: str, old: str, new: str) -> str:
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"anchor matched {n} times: {old[:80]!r}")
    return s.replace(old, new)


# ---- predict-script source inserted after the coordhead stats wrapper (anchor '_V1284_STATS = {}\n') ----
CAPTURE_SRC = '''import time as _v1284_time
import shutil as _v1284_shutil
import zlib as _v1284_zlib
_V1284_CAPTURE_ONLY = os.environ.get("V1284_CAPTURE_ONLY", "0") == "1"
_V1284_VIDEO_T0 = [0.0]
_V1284_GT_SCALE_UM = np.array([1.625, 0.40625, 0.40625], dtype=np.float64)


def _v1284_read_gt(ds_path):
    """GT nodes of <stem>.geff next to the zarr: t and (z, y, x) in um (geff axes: full-resolution voxels)."""
    stem = Path(str(ds_path)).stem
    props = Path(str(ds_path)).parent / (stem + ".geff") / "nodes" / "props"
    cols = [np.asarray(zarr.open_array(str(props / k / "values"), mode="r")[...]) for k in ("t", "z", "y", "x")]
    return cols[0].astype(np.int64), np.stack(cols[1:], axis=1).astype(np.float64) * _V1284_GT_SCALE_UM


def _v1284_capture_finalize(ds_path):
    """coordhead capture (experiments/coordhead_retrain): compact x138's per-frame capture files of one video."""
    t_start = _v1284_time.time()
    stem = Path(str(ds_path)).stem
    raw_dir = Path(os.environ["V1284_CAPTURE"]) / stem
    out_dir = Path(os.environ.get("V1284_CAPTURE_OUT", "/kaggle/working/capture"))
    out_dir.mkdir(parents=True, exist_ok=True)
    keep_um = float(os.environ.get("V1284_CAPTURE_KEEP_UM", "10.0"))
    sample_rate = float(os.environ.get("V1284_CAPTURE_SAMPLE", "0.01"))
    gt_t, gt_um = _v1284_read_gt(ds_path)
    rng = np.random.default_rng(_v1284_zlib.crc32(stem.encode("utf-8")))
    spacing = np.asarray(_V1284_SPACING, dtype=np.float64)
    parts = {"coords": [], "features": [], "near_gt": [], "sampled": [], "nearest_gt_um": []}
    feat_sum = np.zeros(224, dtype=np.float64)
    feat_sumsq = np.zeros(224, dtype=np.float64)
    n_all = 0
    frame_t, frame_peaks = [], []
    for path in sorted(raw_dir.glob("*.npz")):
        t = int(path.stem)
        with np.load(path) as z:
            coords = np.asarray(z["coords"])
            feats = np.asarray(z["features"])
        if coords.ndim != 2 or coords.shape[1] != 4 or feats.shape != (len(coords), 224) or feats.dtype != np.float32:
            raise RuntimeError(f"capture file {path}: coords {coords.shape} {coords.dtype}, features {feats.shape} {feats.dtype}")
        if len(coords) and not (coords[:, 0] == t).all():
            raise RuntimeError(f"capture file {path}: frame column != {t}")
        frame_t.append(t)
        frame_peaks.append(len(coords))
        n_all += len(coords)
        f64 = feats.astype(np.float64)
        feat_sum += f64.sum(axis=0)
        feat_sumsq += (f64 * f64).sum(axis=0)
        det_um = coords[:, 1:].astype(np.float64) * spacing
        g = gt_um[gt_t == t]
        if len(g) and len(coords):
            dist = np.sqrt(((det_um[:, None, :] - g[None, :, :]) ** 2).sum(axis=-1)).min(axis=1)
        else:
            dist = np.full(len(coords), np.inf)
        near = dist <= keep_um
        samp = rng.random(len(coords)) < sample_rate
        keep = near | samp
        parts["coords"].append(coords[keep].astype(np.int16))
        parts["features"].append(feats[keep])
        parts["near_gt"].append(near[keep])
        parts["sampled"].append(samp[keep])
        parts["nearest_gt_um"].append(dist[keep].astype(np.float32))
    if not frame_t:
        raise RuntimeError(f"no capture files for {stem} in {raw_dir}")
    arrays = {k: (np.concatenate(v) if v else None) for k, v in parts.items()}
    out_path = out_dir / (stem + ".npz")
    np.savez_compressed(out_path, **arrays, frame_t=np.asarray(frame_t, dtype=np.int16),
                        frame_peaks=np.asarray(frame_peaks, dtype=np.int32), feat_sum=feat_sum, feat_sumsq=feat_sumsq,
                        n_all=np.int64(n_all), keep_um=np.float64(keep_um), sample_rate=np.float64(sample_rate))
    _v1284_shutil.rmtree(raw_dir, ignore_errors=True)
    rec = {"stem": stem, "frames": len(frame_t), "peaks_all": int(n_all), "kept": int(len(arrays["coords"])),
           "near_gt": int(arrays["near_gt"].sum()), "sampled": int(arrays["sampled"].sum()),
           "gt_nodes": int(len(gt_t)), "gt_frames": int(len(np.unique(gt_t))), "bytes": out_path.stat().st_size,
           "video_seconds": round(t_start - _V1284_VIDEO_T0[0], 2),
           "finalize_seconds": round(_v1284_time.time() - t_start, 2),
           "gpu_shard": os.environ.get("BIOHUB_GPU_SHARD", "single"),
           "kernel_shard": os.environ.get("BIOHUB_CAPTURE_SHARD", "")}
    print("COORDHEAD_CAPTURE " + json.dumps(rec, sort_keys=True), flush=True)
    shard = os.environ.get("BIOHUB_GPU_SHARD", "single").replace("/", "_")
    with (out_dir / ("manifest_" + shard + ".jsonl")).open("a") as handle:
        handle.write(json.dumps(rec, sort_keys=True) + "\\n")
'''

# (old, new) replacements applied to the ALREADY coordhead-patched predict script inside the kernel
CAPTURE_PATCHES = [
    ("_V1284_STATS = {}\n", "_V1284_STATS = {}\n" + CAPTURE_SRC),
    ("        # --- Edge prediction for each consecutive pair in the window ---\n        for f_idx in range(W - 1):\n",
     "        # --- Edge prediction for each consecutive pair in the window ---\n"
     "        for f_idx in (range(0) if _V1284_CAPTURE_ONLY else range(W - 1)):\n"),
    ("        ds_path = data_dir / name\n        coords, edges = predict_video(\n",
     "        ds_path = data_dir / name\n        _V1284_VIDEO_T0[0] = _v1284_time.time()\n"
     "        coords, edges = predict_video(\n"),
    ("        _v1284_log(ds_path)\n",
     "        _v1284_log(ds_path)\n        if _V1284_CAPTURE_ONLY:\n            _v1284_capture_finalize(ds_path)\n"
     "            continue\n"),
]


def capture_patch_block() -> str:
    """Cell-5 code (top level, after the coordhead block) that applies CAPTURE_PATCHES to the predict script."""
    lines = [
        "# ---- coordhead capture-only (experiments/coordhead_retrain/build_capture_kernel.py): the predict script stops",
        "# after peak detection + x138's capture (no edge transformer, no graph / ILP / geff); per video the x138 per-frame",
        "# files are compacted into V1284_CAPTURE_OUT/<stem>.npz (peaks near GT + a random share + all-peak moments).",
        'if os.environ.get("V1284_MODE") != "capture" or os.environ.get("V1284_CAPTURE_ONLY") != "1":',
        '    raise RuntimeError("capture kernel needs COORDHEAD_ENABLE=1, COORDHEAD_MODE=capture, V1284_CAPTURE_ONLY=1")',
        "_cap_source = _ps.read_text()",
        "_cap_patches = " + repr(CAPTURE_PATCHES),
        "for _cap_old, _cap_new in _cap_patches:",
        "    if _cap_source.count(_cap_old) != 1:",
        "        raise RuntimeError(('capture patch anchor mismatch', _cap_old[:80], _cap_source.count(_cap_old)))",
        "    _cap_source = _cap_source.replace(_cap_old, _cap_new)",
        "compile(_cap_source, str(_ps), 'exec')",
        "_ps.write_text(_cap_source)",
        "import shutil as _cap_shutil",
        "_cap_shutil.rmtree(os.environ['V1284_CAPTURE'], ignore_errors=True)",
        "for _cap_old_file in Path(os.environ['V1284_CAPTURE_OUT']).glob('*'):",
        "    _cap_old_file.unlink()",
        "print('coordhead capture-only patch applied: train stems', len(test_stems), '| out', os.environ['V1284_CAPTURE_OUT'],",
        "      '| keep_um', os.environ['V1284_CAPTURE_KEEP_UM'], '| sample', os.environ['V1284_CAPTURE_SAMPLE'], flush=True)",
        "",
    ]
    return NL.join(lines) + NL


CAPTURE_SUMMARY = r'''
# ---- coordhead capture summary (experiments/coordhead_retrain/build_capture_kernel.py) ----
_cap_out = Path(os.environ["V1284_CAPTURE_OUT"])
_cap_rows = [json.loads(_line) for _p in sorted(_cap_out.glob("manifest_*.jsonl"))
             for _line in _p.read_text().splitlines() if _line.strip()]
_cap_done = {_r["stem"] for _r in _cap_rows}
_cap_missing = sorted(set(CAPTURE_STEMS) - _cap_done)
_cap_extra = sorted(_cap_done - set(CAPTURE_STEMS))
_cap_npz = {_p.stem: _p.stat().st_size for _p in _cap_out.glob("*.npz")}
_cap_video_s = [float(_r["video_seconds"]) for _r in _cap_rows]
_cap_summary = {
    "kernel_shard": os.environ.get("BIOHUB_CAPTURE_SHARD", ""),
    "stems": list(CAPTURE_STEMS), "done": len(_cap_done), "missing": _cap_missing, "extra": _cap_extra,
    "gpu_workers": int(worker_count), "predict_wall_seconds": round(float(predict_seconds), 1),
    "setup_seconds_before_predict": round(float(start_time - KERNEL_T0), 1) if "KERNEL_T0" in globals() else None,
    "video_seconds_mean": round(sum(_cap_video_s) / max(len(_cap_video_s), 1), 1),
    "video_seconds_max": round(max(_cap_video_s or [0.0]), 1),
    "gpu_seconds_total": round(sum(_cap_video_s), 1),
    "peaks_all": sum(int(_r["peaks_all"]) for _r in _cap_rows), "kept": sum(int(_r["kept"]) for _r in _cap_rows),
    "near_gt": sum(int(_r["near_gt"]) for _r in _cap_rows), "gt_nodes": sum(int(_r["gt_nodes"]) for _r in _cap_rows),
    "npz_bytes_total": sum(_cap_npz.values()), "npz_bytes_mean": round(sum(_cap_npz.values()) / max(len(_cap_npz), 1)),
    "knobs": {_k: os.environ.get(_k) for _k in ("V1284_CAPTURE_KEEP_UM", "V1284_CAPTURE_SAMPLE", "V1284_MODE")},
}
(_cap_out / ("capture_summary_" + _cap_summary["kernel_shard"] + ".json")).write_text(json.dumps(_cap_summary, indent=1))
print("COORDHEAD CAPTURE SUMMARY " + json.dumps({k: v for k, v in _cap_summary.items() if k != "stems"}), flush=True)
for _r in sorted(_cap_rows, key=lambda r: r["stem"]):
    print(f"  {_r['stem']}  peaks={_r['peaks_all']:6d} kept={_r['kept']:5d} near={_r['near_gt']:5d} gt={_r['gt_nodes']:5d}"
          f"  {_r['bytes'] / 1e6:6.2f} MB  video={_r['video_seconds']:7.1f}s  finalize={_r['finalize_seconds']:5.1f}s")
# only the capture goes to the output: drop the repo copy (weights = symlink into /kaggle/input, not followed) and the
# secondary weights copy
import shutil as _cap_shutil
_cap_shutil.rmtree(REPO_DIR, ignore_errors=True)
_cap_shutil.rmtree(WORKING_DIR / "secondary_seed_weights", ignore_errors=True)
if _cap_missing or _cap_extra or set(_cap_npz) != _cap_done:
    raise RuntimeError(("capture incomplete", _cap_missing, _cap_extra, sorted(set(_cap_done) ^ set(_cap_npz))))
'''

SECONDARY_OLD = "SECONDARY_ARTIFACTS, secondary_manifest_info = _find_secondary_artifact_root()\n"
SECONDARY_NEW = '''def _find_secondary_artifact_root_fast() -> tuple[Path, dict]:
    """capture kernel: x138's order - the three explicit mount paths first, the /kaggle/input rglob only if they miss.
    Same result as _find_secondary_artifact_root (its candidate list starts with the same three paths)."""
    for manifest_path in (
        _secondary_manifest_explicit,
        Path(f"/kaggle/input/{_secondary_slug}/ARTIFACT_MANIFEST.json"),
        Path(f"/kaggle/input/datasets/pilkwang/{_secondary_slug}/ARTIFACT_MANIFEST.json"),
    ):
        if not manifest_path.is_file():
            continue
        try:
            info = json.loads(manifest_path.read_text())
        except Exception:
            continue
        if str(info.get("model", {}).get("weight_sha256", "")) == _secondary_expected_sha256:
            return manifest_path.parent, info
    return _find_secondary_artifact_root()


SECONDARY_ARTIFACTS, secondary_manifest_info = _find_secondary_artifact_root_fast()
'''


def build(name: str, stems: list[str], push: bool) -> Path:
    nb, meta = make_notebook(name, stems)
    out_dir = HERE / "kernels" / f"chcap-{name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / meta["code_file"]).write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    (out_dir / "kernel-metadata.json").write_text(json.dumps(meta, indent=1))
    print(f"built {out_dir.relative_to(ROOT)}  ({len(stems)} train videos) -> {meta['id']}")
    if push:
        r = subprocess.run([sys.executable, "-m", "kaggle", "kernels", "push", "-p", str(out_dir)])
        if r.returncode != 0:
            raise SystemExit(r.returncode)
    return out_dir


def make_notebook(name: str, stems: list[str]) -> tuple[dict, dict]:
    """The capture notebook (exp51 cells 0-5, transformed) and its kernel metadata, in memory."""
    nb = json.loads(BASE_NB.read_text(encoding="utf-8"))
    cells = nb["cells"]
    code = [i for i, c in enumerate(cells) if c["cell_type"] == "code"]
    src = {k: "".join(cells[i]["source"]) for k, i in enumerate(code)}
    assert len(code) == 15, len(code)

    c0 = src[0]
    for must in ('os.environ["BIOHUB_COORDHEAD_ENABLE"] = "1"', 'os.environ["BIOHUB_DIVINS_ENABLE"] = "1"',
                 "BIOHUB_PRESET = 'exp51_coordhead'"):
        assert must in c0, must
    assert "BIOHUB_COORDHEAD_MODE" not in c0
    c0 = c0.replace("BIOHUB_PRESET = 'exp51_coordhead'", f"BIOHUB_PRESET = 'chcap_{name}'")
    block = [NL + f"# ---- chcap_{name}: coordhead TRAIN capture (experiments/coordhead_retrain/build_capture_kernel.py) ----"]
    block += [f'os.environ["{k}"] = "{v}"' for k, v in CAPTURE_KNOBS.items()]
    block += [f'os.environ["BIOHUB_CAPTURE_SHARD"] = "{name}"', "import time as _cap_time", "KERNEL_T0 = _cap_time.time()"]
    c0 = c0.rstrip(NL) + NL + NL.join(block) + NL

    c3 = _rep1(src[3], SECONDARY_OLD, SECONDARY_NEW)

    c5 = src[5]
    assert "# ---- coordhead (tools/build_probe_kernel.py --patch coordhead)" in c5
    stems_lines = NL.join(f"    {s!r}," for s in stems)
    c5 = _rep1(c5, "test_stems = list_test_stems()\n",
               "# capture kernel (experiments/coordhead_retrain/build_capture_kernel.py): TRAIN videos of this shard\n"
               'TEST_DIR = COMP_DIR / "train"\n'
               "CAPTURE_STEMS = [\n" + stems_lines + "\n]\n"
               "_cap_absent = [s for s in CAPTURE_STEMS if not (TEST_DIR / f'{s}.zarr').is_dir() or not (TEST_DIR / f'{s}.geff').is_dir()]\n"
               "if _cap_absent or len(set(CAPTURE_STEMS)) != len(CAPTURE_STEMS):\n"
               "    raise FileNotFoundError(('capture stems missing in train/ or duplicated', _cap_absent))\n"
               "test_stems = list(CAPTURE_STEMS)\n")
    anchor = "start_time = time.time()" + NL + "available_gpu_count = _torch.cuda.device_count()" + NL
    c5 = _rep1(c5, anchor, capture_patch_block() + NL + anchor)
    c5 = _rep1(c5, "    _wait_for_prediction_shards(processes, commands)\n    _merge_prediction_shards(worker_count)\n",
               "    _wait_for_prediction_shards(processes, commands)\n"
               "    print('capture: GPU subprocesses done (capture mode: no geff merge)', flush=True)\n")
    c5 = c5.rstrip(NL) + NL + CAPTURE_SUMMARY

    new_src = {0: c0, 1: src[1], 2: src[2], 3: c3, 4: src[4], 5: c5}
    keep = []
    for k in range(6):
        cell = cells[code[k]]
        cell["source"] = new_src[k].splitlines(keepends=True)
        cell["outputs"] = []
        cell["execution_count"] = None
        keep.append(cell)
    for k, s in new_src.items():
        compile(s, f"cell{k}", "exec")
    nb["cells"] = keep

    slug = f"biohub-chcap-{name}"
    nb_name = f"chcap-{name}.ipynb"
    meta = json.loads(BASE_META.read_text())
    meta["id"] = "vitaliineibauer/" + slug
    meta["title"] = slug
    meta["code_file"] = nb_name
    meta["is_private"] = True
    meta["enable_gpu"] = True
    meta["enable_internet"] = False
    meta["dataset_sources"] = [d for d in meta["dataset_sources"] if d not in DROP_DATASETS]
    assert "anvithpothula/biohub-v1284-head-s075" in meta["dataset_sources"]
    return nb, meta


def all_train_stems() -> list[str]:
    stems = sorted(p.name[:-5] for p in TRAIN_DIR.glob("*.zarr"))
    if len(stems) != 199:
        folds = json.loads(SPLITS.read_text())["folds"]
        print(f"NOTE: {len(stems)} local train zarrs; using the 199 stems of splits.json")
        stems = sorted(folds)
    return stems


def gt_counts(stems: list[str]) -> dict[str, int]:
    """GT node count per video (local geff); falls back to 0 when the local data is absent."""
    out = {}
    for s in stems:
        meta = TRAIN_DIR / f"{s}.geff" / "nodes" / "props" / "t" / "values" / "zarr.json"
        out[s] = int(json.loads(meta.read_text())["shape"][0]) if meta.is_file() else 0
    return out


def plan_shards(stems: list[str], n: int) -> list[list[str]]:
    """Round-robin over stems sorted by (embryo, -GT nodes): every shard gets both embryos and a similar GT volume;
    within a shard the order alternates between the two GPU workers (slice i::2) the same way."""
    counts = gt_counts(stems)
    shards: list[list[str]] = [[] for _ in range(n)]
    k = 0
    for emb in ("6bba", "44b6"):  # each embryo round-robin (by GT count), continuing the shard counter
        for s in sorted([s for s in stems if s.startswith(emb)], key=lambda s: (-counts[s], s)):
            shards[k % n].append(s)
            k += 1
    out = []
    for sh in shards:  # interleave the embryos inside a shard so both GPU workers (slice i::2) get both
        a = [s for s in sh if s.startswith("6bba")]
        b = [s for s in sh if s.startswith("44b6")]
        order, ia, ib = [], 0, 0
        while ia < len(a) or ib < len(b):
            if ib >= len(b) or (ia < len(a) and ia * len(b) <= ib * len(a)):
                order.append(a[ia]); ia += 1
            else:
                order.append(b[ib]); ib += 1
        out.append(order)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["pilot", "full"])
    ap.add_argument("--stems", default="", help="pilot: comma-separated train stems")
    ap.add_argument("--shards", type=int, default=4, help="full: number of kernel shards")
    ap.add_argument("--only", default="", help="full: comma-separated shard indices to build (default all)")
    ap.add_argument("--embryo", default="", choices=["", "44b6", "6bba"],
                    help="full: Kaggle shards over this embryo only (names <embryo>-s<i>of<n>); the other embryo's "
                         "stems go to the plan entry friend_a_<other> for local_capture.py --plan (GT-rich first)")
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    plan_path = HERE / "capture_plan.json"
    plan = json.loads(plan_path.read_text()) if plan_path.is_file() else {}
    if a.mode == "pilot":
        stems = [s.strip() for s in a.stems.split(",") if s.strip()]
        if not stems:
            raise SystemExit("--stems needed for the pilot")
        unknown = sorted(set(stems) - set(all_train_stems()))
        if unknown:
            raise SystemExit(f"not train stems: {unknown}")
        build("pilot", stems, a.push)
        plan["pilot"] = stems
    else:
        pool = all_train_stems()
        counts = gt_counts(pool)
        prefix = ""
        if a.embryo:
            other = "6bba" if a.embryo == "44b6" else "44b6"
            plan[f"friend_a_{other}"] = sorted([s for s in pool if s.startswith(other)], key=lambda s: (-counts[s], s))
            print(f"friend_a_{other}: {len(plan[f'friend_a_{other}'])} videos (local_capture.py --plan friend_a_{other})")
            pool = [s for s in pool if s.startswith(a.embryo)]
            prefix = a.embryo + "-"
        shards = plan_shards(pool, a.shards)
        only = {int(x) for x in a.only.split(",") if x.strip()} or set(range(a.shards))
        for i, stems in enumerate(shards):
            name = f"{prefix}s{i}of{a.shards}"
            plan[name] = stems
            print(f"{name}: {len(stems)} videos, GT nodes {sum(counts[s] for s in stems)}, "
                  f"44b6 {sum(s.startswith('44b6') for s in stems)} / 6bba {sum(s.startswith('6bba') for s in stems)}")
            if i in only:
                build(name, stems, a.push)
    plan_path.write_text(json.dumps(plan, indent=1))


if __name__ == "__main__":
    main()
