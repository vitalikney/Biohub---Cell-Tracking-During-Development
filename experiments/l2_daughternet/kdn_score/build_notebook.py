"""Build the self-contained K-DS Kaggle kernel: kdn-score.ipynb + kernel-metadata.json in this folder.

    python experiments/l2_daughternet/kdn_score/build_notebook.py                    # OOF over all 1,012,255 rows
    python experiments/l2_daughternet/kdn_score/build_notebook.py --ensemble 1       # 5-fold ensemble -> node_p_ens
    python experiments/l2_daughternet/kdn_score/build_notebook.py --ensemble both    # OOF + ensemble from one joint pass
    python experiments/l2_daughternet/kdn_score/build_notebook.py --smoke            # KDS_SMOKE=1: 3 videos x 300 rows

The notebook embeds, verbatim, tools/divnet_infer.py, tools/daughternet.py, kdn_train/kdn_core.py (FrameReader, splits
loader, log), kds_core.py and experiments/l2_daughternet/splits.json as %%writefile cells (materialised under
/kaggle/working/kds_src so the worker subprocesses can import them); a guard cell checks their sha256 against the values
recorded at build time. Re-run this script after any change to those five files. Nothing is pushed.

Inputs of the kernel: the competition data, dataset vitaliineibauer/biohub-l2-coords (coords_exp39.parquet) and the
output of kernel vitaliineibauer/biohub-l2-kdn-train (folds/fold_k/best.pt, splits_used.json).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KERNEL_ID = "vitaliineibauer/biohub-l2-kdn-score"
NOTEBOOK = "kdn-score.ipynb"
SRC_ROOT = "/kaggle/working/kds_src"
DATASETS = ["vitaliineibauer/biohub-l2-coords"]
KERNEL_SOURCES = ["vitaliineibauer/biohub-l2-kdn-train"]

SOURCES = [  # (path in kds_src, repo file)
    ("tools/divnet_infer.py", ROOT / "tools" / "divnet_infer.py"),
    ("tools/daughternet.py", ROOT / "tools" / "daughternet.py"),
    ("kdn_core.py", ROOT / "experiments" / "l2_daughternet" / "kdn_train" / "kdn_core.py"),
    ("kds_core.py", HERE / "kds_core.py"),
    ("splits.json", ROOT / "experiments" / "l2_daughternet" / "splits.json"),
]


def _sha(text: str) -> str:
    return hashlib.sha256(text.rstrip().encode("utf-8")).hexdigest()


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text}


def code(text: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text}


def build(smoke: bool, ensemble: str) -> tuple[Path, dict]:
    files = []
    for rel, path in SOURCES:
        if not path.is_file():
            raise FileNotFoundError(path)
        files.append((rel, path.read_text(encoding="utf-8")))
    hashes = {rel: _sha(text) for rel, text in files}
    cells = [md(f"""# Biohub L2 K-DS: DaughterNet scores for every exported candidate node

Scores all rows of `coords_exp39.parquet` (dataset `vitaliineibauer/biohub-l2-coords`: 1,012,255 candidate nodes of the
exp39 base over the 199 train videos; float voxel coordinates of the full-resolution frame) with the K-DN fold models
from the attached output of `vitaliineibauer/biohub-l2-kdn-train`.

* **OOF** (`KDS_ENSEMBLE=0`, default): each row is scored by the model of its video's fold (the fold model that never
  trained on that video; folds from the trainer's `splits_used.json`, else the embedded `splits.json`)
  -> `node_p_oof.parquet`. A routing audit (summary `oof_routing_audit`) leaves a video NaN if its fold model trained
  on it or on a video of its leak group (`splits.json` meta.leak_groups, 44b6 crops that share GT).
* **Ensemble** (`KDS_ENSEMBLE=1`): softmax averaged over all fold models, what the submission kernel does
  -> `node_p_ens.parquet`. `KDS_ENSEMBLE=both` produces both from ONE pass (every fold model runs once per sample;
  OOF = the video's fold model, ensemble = the mean), so the frames are read and prepared once.
* Output columns `stem, node_id, fold, p_cont, p_par, p_dau` (softmax in `tools.daughternet.CLASSES` order), one row per
  input row in input order, plus `node_p_<mode>_summary.json` (rows per fold, NaN count, timing, contract checks,
  `score_nodes` re-verification).
* Input = the DivNet contract of `tools/daughternet.prepare_sample` (lags -1..+2, XY pool 4, 16x32x32 crop, percentile
  50/99.5 clipped to [-0.5, 6], gaussian marker). Frames are read once per video (kdn_core.FrameReader) by a prefetch
  thread pool; samples are cropped with the contract's own functions and checked against `prepare_sample` in every
  video (1 sample from raw frames + 2 from the shared frames; any difference aborts).
* Two worker processes, one per T4 (`CUDA_VISIBLE_DEVICES` 0 / 1), videos split greedily by rows + frames; fp32 unless
  `KDS_AMP=1`. Per-video parts in `/kaggle/working/parts/<mode>/` make a rerun resume.
* Embedded sources ({", ".join(rel for rel, _ in files)}) are sha256-guarded.
"""),
             code(f"""import os, sys, platform, importlib
from pathlib import Path

KDS_SRC = Path("{SRC_ROOT}")
(KDS_SRC / "tools").mkdir(parents=True, exist_ok=True)
print("python", sys.version.split()[0], platform.platform(), "cpus", os.cpu_count())
import torch
print("torch", torch.__version__, "cuda", torch.cuda.is_available(), torch.cuda.device_count(),
      [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])
for _name in ("numpy", "pandas", "pyarrow", "blosc2", "numcodecs", "zstandard", "zarr"):
    try:
        _mod = importlib.import_module(_name)
        print(f"  {{_name:12s}} {{getattr(_mod, '__version__', '?')}}")
    except Exception as _exc:
        print(f"  {{_name:12s}} MISSING ({{type(_exc).__name__}})")
_root = Path("/kaggle/input")
if _root.exists():  # two levels, never into the competition *.zarr / *.geff trees
    for _p in sorted(_root.glob("*")):
        print("input:", _p)
        if _p.is_dir() and not _p.name.endswith((".zarr", ".geff")):
            for _q in sorted(_p.glob("*"))[:12]:
                print("   ", _q)
"""),
             code(f"%%writefile {SRC_ROOT}/tools/__init__.py\n"
                  "# tools package materialised by the K-DS kernel (divnet_infer + daughternet, verbatim repo copies)\n")]
    for rel, text in files:
        cells.append(code(f"%%writefile {SRC_ROOT}/{rel}\n{text}"))
    cells.append(code(f"""import hashlib
EXPECTED_SHA256 = {json.dumps(hashes, indent=1)}
_bad = {{}}
for _rel, _want in EXPECTED_SHA256.items():
    _got = hashlib.sha256((KDS_SRC / _rel).read_text(encoding="utf-8").rstrip().encode("utf-8")).hexdigest()
    if _got != _want:
        _bad[_rel] = _got
if _bad:
    raise RuntimeError(f"embedded source drift: {{_bad}}")
print("embedded sources OK:", ", ".join(EXPECTED_SHA256))
"""))
    cells.append(code(f"""# ---- configuration (every knob is an env var read by kds_core.config_from_env) ----
os.environ.setdefault("KDS_SMOKE", "{1 if smoke else 0}")          # 1 = 3 videos x 300 rows
os.environ.setdefault("KDS_ENSEMBLE", "{ensemble}")        # 0 = OOF, 1 = 5-fold ensemble, both
os.environ.setdefault("KDS_BATCH", "512")
os.environ.setdefault("KDS_AMP", "0")               # 1 = fp16 autocast (faster, |dp| ~1e-3 vs score_nodes)
os.environ.setdefault("KDS_FRAME_THREADS", "2")     # frame-prefetch threads per worker
os.environ.setdefault("KDS_WORKERS", "0")           # 0 = one worker per GPU (max 2)
os.environ.setdefault("KDS_EXPECT_FOLDS", "5")
os.environ.setdefault("KDS_VERIFY_PER_FOLD", "3")   # rows per fold re-scored via tools.daughternet.score_nodes on CPU

if str(KDS_SRC) not in sys.path:
    sys.path.insert(0, str(KDS_SRC))
import kds_core
cfg = kds_core.config_from_env()
if Path("/kaggle/working").exists() and not torch.cuda.is_available() and not cfg["smoke"]:
    raise RuntimeError("K-DS full run needs the GPU accelerator (2x T4)")
for _k, _v in cfg.items():
    print(f"  {{_k:18s}} {{_v}}")
"""))
    cells.append(code("state = kds_core.run(cfg)\n"))
    cells.append(code("""import json
_fail = []
for _mode, _s in state["summaries"].items():
    print(f"== {_mode}: {_s['output']}")
    print("   rows out", _s["rows_out"], "of input", _s["rows_input_parquet"], "| NaN rows", _s["nan_rows"],
          "| rows per fold", _s["rows_per_fold"])
    print("   videos", json.dumps({k: v for k, v in _s["videos"].items() if k not in ("no_model", "leak_excluded")}),
          "no model:", _s["videos"]["no_model"][:10], "leak-excluded:", _s["videos"].get("leak_excluded", [])[:10])
    _aud = _s.get("oof_routing_audit")
    if _aud:
        print("   OOF routing audit", json.dumps({k: (len(v) if k == "excluded" else v) for k, v in _aud.items()}))
        if _aud["excluded"]:
            print(f"   WARNING {len(_aud['excluded'])} videos have NaN OOF p: their fold model trained on them or on "
                  f"a leak-group sibling: {list(_aud['excluded'])[:10]}")
    print("   timing", json.dumps({k: v for k, v in _s["timing"].items() if k != "workers"}))
    for _w in _s["timing"]["workers"]:
        print("   worker", json.dumps({k: v for k, v in _w.items() if k != "failed"}), "failed", len(_w["failed"]))
    print("   prob", json.dumps(_s["prob"]))
    print("   verify", json.dumps({k: v for k, v in _s["verify"].items() if k != "rows"}))
    if not _s["verify"].get("pass"):
        _fail.append(f"{_mode}: score_nodes re-verification failed")
    if _s["nan_rows"]:
        print(f"   WARNING {_s['nan_rows']} rows without a prediction")
for _p in sorted(Path(state["work_dir"]).glob("*")):
    if _p.is_file():
        print(f"{_p.stat().st_size / 2**20:9.2f} MiB  {_p}")
if _fail:
    raise RuntimeError("; ".join(_fail))
"""))
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    out = HERE / NOTEBOOK
    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    return out, hashes


def write_metadata() -> Path:
    base = json.loads((ROOT / "experiments" / "exp39_sjlee947_tight55_divnetveto" / "kernel-metadata.json")
                      .read_text(encoding="utf-8"))
    meta = {
        "id": KERNEL_ID,
        "title": KERNEL_ID.split("/", 1)[1],
        "code_file": NOTEBOOK,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": False,
        "dataset_sources": DATASETS,
        "competition_sources": ["biohub-cell-tracking-during-development"],
        "kernel_sources": KERNEL_SOURCES,
        "model_sources": [],
        "docker_image": base["docker_image"],
        "machine_shape": "NvidiaTeslaT4",
    }
    path = HERE / "kernel-metadata.json"
    path.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="make KDS_SMOKE=1 the notebook default")
    ap.add_argument("--ensemble", default="0", choices=["0", "1", "both"], help="notebook default of KDS_ENSEMBLE")
    args = ap.parse_args()
    out, hashes = build(args.smoke, args.ensemble)
    meta = write_metadata()
    print("wrote", out, "and", meta)
    for rel, h in hashes.items():
        print(f"  {rel:24s} sha256(rstrip) {h[:16]}")


if __name__ == "__main__":
    main()
