"""Build the self-contained K-DN Kaggle kernel: kdn-train.ipynb + kernel-metadata.json in this folder.

    python experiments/l2_daughternet/kdn_train/build_notebook.py            # v2 full run (5 folds, 30 epochs max)
    python experiments/l2_daughternet/kdn_train/build_notebook.py --smoke    # KDN_SMOKE=1 default (5 videos, 1 epoch)
    python experiments/l2_daughternet/kdn_train/build_notebook.py --no-extra # v1 notebook (GT samples only)

The notebook embeds, verbatim, tools/divnet_infer.py, tools/daughternet.py, kdn_core.py and
experiments/l2_daughternet/splits.json as %%writefile cells (materialised under /kaggle/working/kdn_src so the fold
subprocesses can import them); a guard cell checks their sha256 against the values recorded at build time.
v2: experiments/l2_daughternet/pool_samples.parquet (tools/make_pool_samples.py) is embedded the same way, as a CSV
text copy (pool_samples.csv; the builder checks that kdn_core.load_extra_samples reads it back bit-identical to the
parquet), its sha256 is in the guard, and KDN_EXTRA_SAMPLES points to it. Re-run this script after any change to those
files. Nothing is pushed.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KERNEL_ID = "vitaliineibauer/biohub-l2-kdn-train"
NOTEBOOK = "kdn-train.ipynb"
SRC_ROOT = "/kaggle/working/kdn_src"

SOURCES = [  # (path in kdn_src, repo file)
    ("tools/divnet_infer.py", ROOT / "tools" / "divnet_infer.py"),
    ("tools/daughternet.py", ROOT / "tools" / "daughternet.py"),
    ("kdn_core.py", HERE / "kdn_core.py"),
]
SPLITS = ROOT / "experiments" / "l2_daughternet" / "splits.json"
EXTRA = ROOT / "experiments" / "l2_daughternet" / "pool_samples.parquet"
EXTRA_REL = "pool_samples.csv"


def _sha(text: str) -> str:
    return hashlib.sha256(text.rstrip().encode("utf-8")).hexdigest()


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text}


def code(text: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text}


def extra_csv_text(path: Path) -> tuple[str, dict]:
    """Parquet -> CSV text for a %%writefile cell; asserts that the text reads back exactly, through the same loader
    the kernel uses (kdn_core.load_extra_samples, float_precision='round_trip')."""
    import numpy as np
    import pandas as pd

    for p in (str(ROOT), str(HERE)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import kdn_core

    df = pd.read_parquet(path)
    text = df.to_csv(index=False, lineterminator="\n")
    back = pd.read_csv(io.StringIO(text), dtype={"stem": str, "label": str}, float_precision="round_trip")
    if list(back.columns) != list(df.columns) or len(back) != len(df):
        raise RuntimeError("pool CSV round trip changed the columns or the row count")
    for col in df.columns:
        a, b = df[col].to_numpy(), back[col].to_numpy()
        if np.issubdtype(np.asarray(a).dtype, np.number):
            same = np.array_equal(a.astype(np.float64), b.astype(np.float64), equal_nan=True)
        else:
            same = bool((a.astype(str) == b.astype(str)).all())
        if not same:
            raise RuntimeError(f"pool CSV round trip changed column {col}")
    tmp = HERE / "_pool_roundtrip_check.csv"
    try:  # the exact loader the kernel runs on the embedded file
        tmp.write_text(text.rstrip() + "\n", encoding="utf-8")
        loaded = kdn_core.load_extra_samples(tmp)
    finally:
        tmp.unlink(missing_ok=True)
    ref = kdn_core.load_extra_samples(path)
    if list(loaded.columns) != list(ref.columns) or len(loaded) != len(ref):
        raise RuntimeError("load_extra_samples(csv) != load_extra_samples(parquet): columns / rows")
    for col in ref.columns:
        a, b = ref[col].to_numpy(), loaded[col].to_numpy()
        ok = (np.array_equal(a.astype(np.float64), b.astype(np.float64), equal_nan=True)
              if np.issubdtype(np.asarray(a).dtype, np.number) else bool((a.astype(str) == b.astype(str)).all()))
        if not ok:
            raise RuntimeError(f"load_extra_samples(csv) != load_extra_samples(parquet) in column {col}")
    info = {"parquet": path.relative_to(ROOT).as_posix(), "parquet_sha256": kdn_core.sha256_file(path),
            "rows": int(len(df)), "videos": int(df["stem"].nunique()),
            "by_label": {k: int(v) for k, v in df["label"].value_counts().items()},
            "csv_bytes": len(text.encode("utf-8"))}
    return text, info


def build(smoke: bool, extra: Path | None = EXTRA) -> tuple[Path, dict, dict | None]:
    files = [(rel, path.read_text(encoding="utf-8")) for rel, path in SOURCES]
    splits_text = SPLITS.read_text(encoding="utf-8") if SPLITS.is_file() else None
    if splits_text is not None:
        files.append(("splits.json", splits_text))
    extra_info = None
    if extra is not None:
        extra_text, extra_info = extra_csv_text(Path(extra))
        files.append((EXTRA_REL, extra_text))
    hashes = {rel: _sha(text) for rel, text in files}
    splits_note = ("`experiments/l2_daughternet/splits.json` (tools/make_splits.py, 5 folds) embedded verbatim"
                   if splits_text is not None else
                   "no splits.json at build time: kdn_core.make_splits_inline (5 folds by video, stratified by embryo "
                   "and division count, seed 0)")
    if extra_info is not None:
        extra_note = f"""* **v2 pool rows** (KDN_EXTRA_SAMPLES = the embedded `{EXTRA_REL}`, a bit-exact CSV copy of
  `{extra_info['parquet']}` (sha256 {extra_info['parquet_sha256'][:16]}, {extra_info['rows']} rows in
  {extra_info['videos']} videos, {extra_info['by_label']}, tools/make_pool_samples.py): nodes of OUR predicted graphs
  (exp39 candidate triples) labelled by the nearest annotated GT node within 7 um, cropped at their PREDICTED
  coordinates exactly like GT samples; source=pool, fold = the video's fold; a pool row within 1 voxel of a GT sample
  (same t) is dropped (GT label kept). The class-balanced sampler is unchanged; KDN_POOL_WEIGHT scales the loss of pool
  rows. The readout has a separate source=pool block (`by_source.pool` in oof_readout.json, `[readout pool]` lines):
  the block that matters for insertion precision. `oof.csv` carries `source` (gt / pool).
"""
        extra_env = (f'os.environ.setdefault("KDN_EXTRA_SAMPLES", str(KDN_SRC / "{EXTRA_REL}"))  '
                     '# v2 pool rows ("" = v1)\n'
                     'os.environ.setdefault("KDN_POOL_WEIGHT", "1.0")   # loss weight of pool rows\n'
                     'os.environ.setdefault("KDN_ES_SOURCE", "all")     # early-stop loss over all / gt / pool rows\n')
    else:
        extra_note = "* No pool rows (v1: GT samples only).\n"
        extra_env = ""
    cells = [md(f"""# Biohub L2 K-DN: DaughterNet training with honest folds + OOF predictions

Trains `tools/daughternet.py` (DivNet UNet-GAP body, 3-logit head, classes cont / parent / daughter) **from random init**
on the 199 train videos with folds grouped by video, and predicts every labelled sample with the fold model that never
saw its video.

* Folds: {splits_note}.
* Labels (annotated GT nodes only): parent = >= 2 GT children; daughter = child of a parent at its first frame;
  cont = in/out-degree 1 and >= 2 frames (lineage) from any parent/daughter node, <= 60 per video; hard negatives =
  cont nodes inside the L2 insertion gate of an annotated one-child node (as u or v), <= 40 per video.
{extra_note}* Input = the DivNet contract (`prepare_sample`): lags -1..+2, XY mean-pool 4, 16x32x32 crop, percentile 50/99.5
  clipped to [-0.5, 6], gaussian marker -> (5, 16, 32, 32). An 18x34x34 crop is cached so the +-1 voxel jitter has a
  margin; its inner crop equals the contract sample exactly (asserted per video and per source).
* Training: AdamW 1e-3 + cosine, <= 30 epochs, early stopping on the fold's val loss (class-macro CE), batch 64,
  class-balanced sampler, flips z/y/x + rot90 yx (all 5 channels), +-1 voxel jitter, gain 0.8-1.2. Two folds run
  concurrently, one per T4 (one subprocess per fold).
* Outputs in /kaggle/working: `oof.csv`, `oof_readout.json`, `folds/fold_k/{{best,last}}.pt`
  ({{'model_state','config','fold','epoch','val_loss'}}), `folds/fold_k/{{history,summary}}.json`,
  `labels_summary.csv`, `splits_used.json`, `contract_check.json`.
* Knobs (env, set in the config cell): KDN_SMOKE=1 (5 videos, 1 epoch, 2 folds), KDN_MAX_VIDEOS, KDN_EPOCHS,
  KDN_EPOCH_SAMPLES, KDN_PATIENCE, KDN_INNER_VAL, KDN_CACHE_DTYPE, KDN_EXTRA_SAMPLES, KDN_POOL_WEIGHT, KDN_ES_SOURCE, ...
"""),
             code(f"""import os, sys, platform, importlib
from pathlib import Path

KDN_SRC = Path("{SRC_ROOT}")
(KDN_SRC / "tools").mkdir(parents=True, exist_ok=True)
print("python", sys.version.split()[0], platform.platform(), "cpus", os.cpu_count())
import torch
print("torch", torch.__version__, "cuda", torch.cuda.is_available(), torch.cuda.device_count(),
      [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])
for _name in ("numpy", "pandas", "blosc2", "numcodecs", "zstandard", "pyarrow", "imagecodecs", "zarr"):
    try:
        _mod = importlib.import_module(_name)
        print(f"  {{_name:12s}} {{getattr(_mod, '__version__', '?')}}")
    except Exception as _exc:
        print(f"  {{_name:12s}} MISSING ({{type(_exc).__name__}})")
for _p in sorted(Path("/kaggle/input").glob("*")) if Path("/kaggle/input").exists() else []:
    print("input:", _p)
"""),
             code(f"%%writefile {SRC_ROOT}/tools/__init__.py\n"
                  "# tools package materialised by the K-DN kernel (divnet_infer + daughternet, verbatim repo copies)\n")]
    for rel, text in files:
        cells.append(code(f"%%writefile {SRC_ROOT}/{rel}\n{text}"))
    cells.append(code(f"""import hashlib
EXPECTED_SHA256 = {json.dumps(hashes, indent=1)}
_bad = {{}}
for _rel, _want in EXPECTED_SHA256.items():
    _got = hashlib.sha256((KDN_SRC / _rel).read_text(encoding="utf-8").rstrip().encode("utf-8")).hexdigest()
    if _got != _want:
        _bad[_rel] = _got
if _bad:
    raise RuntimeError(f"embedded source drift: {{_bad}}")
print("embedded sources OK:", ", ".join(EXPECTED_SHA256))
"""))
    cells.append(code(f"""# ---- configuration (every knob is an env var read by kdn_core.config_from_env) ----
os.environ.setdefault("KDN_SMOKE", "{1 if smoke else 0}")        # 1 = 5 division-rich videos, 1 epoch, 2 folds
os.environ.setdefault("KDN_MAX_VIDEOS", "0")   # 0 = all videos
os.environ.setdefault("KDN_EPOCHS", "1" if os.environ["KDN_SMOKE"] != "0" else "30")
os.environ.setdefault("KDN_PATIENCE", "6")
os.environ.setdefault("KDN_BATCH", "64")
os.environ.setdefault("KDN_LR", "1e-3")
os.environ.setdefault("KDN_EPOCH_SAMPLES", "0")  # 0 = one pass worth of training samples per epoch
os.environ.setdefault("KDN_CONT_PER_VIDEO", "60")
os.environ.setdefault("KDN_HARDNEG_PER_VIDEO", "40")
os.environ.setdefault("KDN_INNER_VAL", "0")    # 1 = early-stop on fold k+1 and train on the other K-2 folds
os.environ.setdefault("KDN_CACHE_DTYPE", "float32")
os.environ.setdefault("KDN_DIVNET", "1")        # in-sample DivNet comparison (giorgosi/biohub-divnet-v2)
{extra_env}
if str(KDN_SRC) not in sys.path:
    sys.path.insert(0, str(KDN_SRC))
import kdn_core
cfg = kdn_core.config_from_env()
if Path("/kaggle/working").exists() and not torch.cuda.is_available() and not cfg["smoke"]:
    raise RuntimeError("K-DN full run needs the GPU accelerator (2x T4)")
for _k, _v in cfg.items():
    print(f"  {{_k:20s}} {{_v}}")
"""))
    cells.append(code("state = kdn_core.step_prepare(cfg)\n"))
    cells.append(code("state = kdn_core.step_build_cache(cfg, state)\n"))
    cells.append(code("state = kdn_core.step_train(cfg, state)\n"))
    cells.append(code("state = kdn_core.step_oof(cfg, state)\n"))
    cells.append(code("""state = kdn_core.step_verify(cfg, state)
import json
print(json.dumps(state["timing"], indent=1))
for _p in sorted(Path(state["work_dir"]).rglob("*")):
    if _p.is_file() and "kdn_src" not in _p.parts:
        print(f"{_p.stat().st_size / 2**20:9.2f} MiB  {_p}")
if not state["verify"]["pass"]:
    raise RuntimeError("contract check failed: see contract_check.json")
"""))
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    out = HERE / NOTEBOOK
    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    return out, hashes, extra_info


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
        "dataset_sources": ["giorgosi/biohub-divnet-v2"],
        "competition_sources": ["biohub-cell-tracking-during-development"],
        "kernel_sources": [],
        "model_sources": [],
        "docker_image": base["docker_image"],
        "machine_shape": "NvidiaTeslaT4",
    }
    path = HERE / "kernel-metadata.json"
    path.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="make KDN_SMOKE=1 the notebook default")
    ap.add_argument("--no-extra", action="store_true", help="v1 notebook: no embedded pool rows")
    ap.add_argument("--extra", default=str(EXTRA), help="pool rows parquet to embed (tools/make_pool_samples.py)")
    args = ap.parse_args()
    extra = None if args.no_extra else Path(args.extra)
    if extra is not None and not extra.is_file():
        raise SystemExit(f"{extra} not found (run tools/make_pool_samples.py, or pass --no-extra)")
    out, hashes, extra_info = build(args.smoke, extra)
    meta = write_metadata()
    print("wrote", out, f"({out.stat().st_size / 2**20:.2f} MiB) and", meta)
    for rel, h in hashes.items():
        print(f"  {rel:24s} sha256(rstrip) {h[:16]}")
    if extra_info:
        print(f"  pool rows: {extra_info['rows']} ({extra_info['by_label']}) from {extra_info['parquet']} "
              f"sha256 {extra_info['parquet_sha256'][:16]}, CSV {extra_info['csv_bytes'] / 2**20:.2f} MiB, round trip OK")


if __name__ == "__main__":
    main()
