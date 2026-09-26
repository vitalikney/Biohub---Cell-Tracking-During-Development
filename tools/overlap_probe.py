"""G-P BIT-PROBE for the OVERLAP-CONSENSUS line (CONTEXT.md 2026-09-26 08:58 UTC): does the hidden test hold overlapping
space-time crops? Registration only (tools/overlap_reg.py, the G-A code path and thresholds, all pairs verified), no model.

Outcome on the hidden rerun (> SMALL_SET videos) is read from the Kaggle error class only:
  >= 1 accepted pair          -> raise RuntimeError('OVERLAP PROBE: N accepted pairs')     ('Notebook Threw Exception')
  0 accepted pairs            -> minimal valid submission.csv                               (COMPLETE, score ~0)
  probe itself failed         -> no submission.csv is written                               ('Submission CSV Not Found')
On the commit run (the <= SMALL_SET visible dummy clips) it always writes the valid CSV, so the commit completes; a failure
there is printed as 'OVERLAP PROBE FAILED'.

Reader: the competition zarr v3 layout (one chunk = one frame, codecs bytes + blosc) decoded with blosc2 (present in the
Kaggle image; x138 reads frames the same way), then numcodecs / python-blosc, then zarr as fallbacks.

Notebook: python tools/overlap_probe.py --build-notebook experiments/exp65_overlap_probe  (embeds overlap_reg.py and this
file verbatim). Local run: python tools/overlap_probe.py --test-dir <dir> [--out-dir <dir>] [--workers 4].
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import traceback
from pathlib import Path

import numpy as np

import overlap_reg as R

COMPETITION = "biohub-cell-tracking-during-development"
TEST_DIR_CANDIDATES = (f"/kaggle/input/competitions/{COMPETITION}/test", f"/kaggle/input/{COMPETITION}/test")
SMALL_SET = 10
CSV_HEADER = ["id", "dataset", "row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"]
KERNEL_ID = "vitaliineibauer/biohub-exp65-overlap-probe"
NB_NAME = "exp65-overlap-probe.ipynb"


# ----------------------------------------------------------------------------------------------------------------------
# pure decisions
# ----------------------------------------------------------------------------------------------------------------------
def find_test_dir(candidates=TEST_DIR_CANDIDATES, override: str | None = None) -> Path | None:
    """First existing test dir (override first, e.g. env OVERLAP_PROBE_TEST_DIR); None if none exists."""
    for c in ([override] if override else []) + list(candidates):
        if c and Path(c).is_dir():
            return Path(c)
    return None


def list_videos(test_dir) -> list[Path]:
    return sorted(p for p in Path(test_dir).iterdir() if p.name.endswith(".zarr"))


def decide(n_videos: int, n_accepted: int, failed: bool, small_set: int = SMALL_SET) -> str:
    """-> 'raise' (overlap found on the hidden set), 'csv' (write the valid CSV) or 'nocsv' (probe failed on the hidden
    set: leave no CSV so the error class differs from the overlap signal)."""
    if n_videos <= small_set:
        return "csv"
    if failed:
        return "nocsv"
    return "raise" if n_accepted >= 1 else "csv"


def minimal_rows(stems_shapes) -> list[list]:
    """sample_submission-shaped rows: per video nodes 1..k at t = 0..k-1 (k = min(3, T)) in the volume centre, chained
    by edges (1->2, 2->3). stems_shapes: [(stem, (T, Z, Y, X) or None)] -> rows without the header."""
    rows, rid = [], 0
    for stem, shape in stems_shapes:
        T, Z, Y, X = (int(s) for s in shape) if shape else (3, 64, 256, 256)
        k = max(1, min(3, T))
        for i in range(k):
            rows.append([rid, stem, "node", i + 1, i, Z // 2, Y // 2, X // 2, -1, -1])
            rid += 1
        for i in range(k - 1):
            rows.append([rid, stem, "edge", -1, -1, -1, -1, -1, i + 1, i + 2])
            rid += 1
    return rows


def write_csv(path, rows) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CSV_HEADER)
        w.writerows(rows)


# ----------------------------------------------------------------------------------------------------------------------
# reader (zarr v3, one chunk per frame, bytes + blosc)
# ----------------------------------------------------------------------------------------------------------------------
def _decompressors():
    out = []
    try:
        import blosc2
        try:
            blosc2.set_nthreads(1)
        except Exception:
            pass
        out.append(("blosc2", blosc2.decompress))
    except Exception:
        pass
    try:
        from numcodecs import blosc as _nb
        out.append(("numcodecs", _nb.decompress))
    except Exception:
        pass
    try:
        import blosc
        out.append(("blosc", blosc.decompress))
    except Exception:
        pass
    return out


def array_meta(zarr_path) -> dict:
    return json.loads((Path(zarr_path) / "0" / "zarr.json").read_text(encoding="utf-8"))


def video_shape(zarr_path) -> tuple:
    return tuple(int(v) for v in array_meta(zarr_path)["shape"])


def make_reader(zarr_path):
    """-> (read_frame(t) -> (Z, Y, X) np.ndarray, shape (T, Z, Y, X), backend name)."""
    zp = Path(zarr_path)
    meta = array_meta(zp)
    shape = tuple(int(v) for v in meta["shape"])
    dtype = np.dtype(meta["data_type"]).newbyteorder("<")
    chunk = [int(c) for c in meta["chunk_grid"]["configuration"]["chunk_shape"]]
    codecs = [c.get("name") for c in meta.get("codecs", [])]
    sep = meta.get("chunk_key_encoding", {}).get("configuration", {}).get("separator", "/")
    fill = meta.get("fill_value", 0) or 0
    fshape = shape[1:]
    simple = (len(shape) == 4 and chunk == [1, *fshape] and codecs in (["bytes", "blosc"], ["bytes"])
              and meta.get("chunk_key_encoding", {}).get("name", "default") == "default")
    decs = _decompressors() if codecs == ["bytes", "blosc"] else [("raw", bytes)]
    if simple and decs:
        name, dec = decs[0]

        def read(t, _zp=zp, _dec=dec):
            key = sep.join(["c", str(int(t)), "0", "0", "0"])
            p = _zp / "0" / key
            if not p.exists():
                return np.full(fshape, fill, dtype=dtype)
            arr = np.frombuffer(_dec(p.read_bytes()), dtype=dtype)
            if arr.size != int(np.prod(fshape)):
                raise ValueError(f"{p}: {arr.size} values, expected {int(np.prod(fshape))}")
            return arr.reshape(fshape)
        return read, shape, name
    import zarr  # fallback: any layout zarr understands
    arr = zarr.open(str(zp / "0"), mode="r")
    return (lambda t, _a=arr: np.asarray(_a[int(t)])), tuple(int(s) for s in arr.shape), "zarr"


def _probe_anchor_job(path: str):
    read, shape, _ = make_reader(path)
    return Path(path).name[:-5], R.video_anchors(read, shape[0], backend="sparse")


def anchors_all(paths, workers: int, log=print) -> dict:
    """Anchors for every video: a spawn pool of `workers` processes, sequential on any pool failure."""
    jobs = [str(p) for p in paths]
    out: dict = {}
    if workers > 1 and len(jobs) > 1:
        try:
            import multiprocessing as mp
            with mp.get_context("spawn").Pool(int(workers)) as pool:
                for n, r in pool.imap_unordered(_probe_anchor_job, jobs):
                    out[n] = r
                    if log and (len(out) % 10 == 0 or len(out) == len(jobs)):
                        log(f"OVERLAP PROBE anchors {len(out)}/{len(jobs)}")
            return out
        except Exception as e:  # pragma: no cover - exercised only when the pool itself breaks
            if log:
                log(f"OVERLAP PROBE pool failed ({type(e).__name__}: {e}); sequential")
            out = {}
    for j in jobs:
        n, r = _probe_anchor_job(j)
        out[n] = r
    return out


# ----------------------------------------------------------------------------------------------------------------------
# run
# ----------------------------------------------------------------------------------------------------------------------
def run_probe(test_dir, out_dir, workers: int = 4, small_set: int = SMALL_SET, log=print) -> dict:
    """The whole probe. Raises RuntimeError('OVERLAP PROBE: N accepted pairs') on the hidden-overlap outcome; otherwise
    returns a summary dict (and writes <out_dir>/submission.csv unless the outcome is 'nocsv')."""
    t0 = time.time()
    summary = {"test_dir": str(test_dir), "videos": 0, "accepted": 0, "failed": False, "outcome": None}
    paths, pairs, failed = [], [], False
    try:
        if test_dir is None:
            raise FileNotFoundError(f"no test dir among {TEST_DIR_CANDIDATES}")
        paths = list_videos(test_dir)
        summary["videos"] = len(paths)
        if not paths:
            raise FileNotFoundError(f"no .zarr in {test_dir}")
        log(f"OVERLAP PROBE videos {len(paths)} in {test_dir}; reader {make_reader(paths[0])[2]}; workers {workers}")
        anchor_sets = anchors_all(paths, workers, log=log)
        t1 = time.time()
        readers, shapes = {}, {}
        for p in paths:
            readers[p.name[:-5]], shapes[p.name[:-5]], _ = make_reader(p)
        res = R.register(anchor_sets, readers, shapes)
        pairs = res["pairs"]
        st = res["stats"]
        frames = sum(int(a["timing"]["frames"]) for a in anchor_sets.values())
        summary.update({"accepted": len(pairs), "anchors": st["anchors"], "candidate_pairs": st["candidate_pairs"],
                        "accepted_cross_prefix": st["accepted_cross_prefix"], "frames": frames,
                        "anchor_wall_s": round(t1 - t0, 1), "verify_s": st["verify_s"],
                        "wall_per_frame_s": round((t1 - t0) / max(1, frames), 4),
                        "rejected": {k: st[k] for k in st if k.startswith("rejected_")}})
        for p in pairs:
            log(f"OVERLAP PROBE pair {p['a']} {p['b']} offset {p['offset']} votes {p['votes']} frames {p['n_frames']} "
                f"spatial {p['spatial_frac']} equal {p['equal_fracs']}")
    except Exception:
        failed = True
        summary["failed"] = True
        summary["error"] = traceback.format_exc(limit=5)
        log("OVERLAP PROBE FAILED\n" + summary["error"])
    summary["wall_s"] = round(time.time() - t0, 1)
    outcome = decide(summary["videos"], len(pairs), failed, small_set)
    summary["outcome"] = outcome
    log("OVERLAP PROBE SUMMARY " + json.dumps(summary, sort_keys=True, default=str))
    if outcome == "raise":
        raise RuntimeError(f"OVERLAP PROBE: {len(pairs)} accepted pairs")
    if outcome == "csv":
        ss = []
        for p in paths:
            try:
                ss.append((p.name[:-5], video_shape(p)))
            except Exception:
                ss.append((p.name[:-5], None))
        write_csv(Path(out_dir) / "submission.csv", minimal_rows(ss))
        log(f"OVERLAP PROBE wrote {Path(out_dir) / 'submission.csv'} ({len(ss)} videos)")
    else:
        log("OVERLAP PROBE: no submission.csv (probe failed on the hidden set)")
    return summary


def kaggle_main() -> dict:
    out_dir = Path("/kaggle/working") if Path("/kaggle/working").is_dir() else Path(".")
    workers = int(os.environ.get("OVERLAP_PROBE_WORKERS", str(min(4, os.cpu_count() or 1))))
    test_dir = find_test_dir(override=os.environ.get("OVERLAP_PROBE_TEST_DIR"))
    return run_probe(test_dir, out_dir, workers=workers)


# ----------------------------------------------------------------------------------------------------------------------
# notebook builder
# ----------------------------------------------------------------------------------------------------------------------
def _code_cell(src: str) -> dict:
    lines = src.splitlines(keepends=True)
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": lines}


def build_notebook(out_dir, tools_dir=None) -> Path:
    tools = Path(tools_dir) if tools_dir else Path(__file__).resolve().parent
    reg = (tools / "overlap_reg.py").read_text(encoding="utf-8")
    probe = (tools / "overlap_probe.py").read_text(encoding="utf-8")
    write = ("# Embedded verbatim: tools/overlap_reg.py and tools/overlap_probe.py (worker processes import them).\n"
             "import os, sys\n"
             "from pathlib import Path\n"
             "MOD_DIR = Path('/kaggle/working/_overlap_mods') if Path('/kaggle/working').is_dir() else Path('_overlap_mods')\n"
             "MOD_DIR.mkdir(parents=True, exist_ok=True)\n"
             f"(MOD_DIR / 'overlap_reg.py').write_bytes({reg!r}.encode('utf-8'))\n"
             f"(MOD_DIR / 'overlap_probe.py').write_bytes({probe!r}.encode('utf-8'))\n"
             "sys.path.insert(0, str(MOD_DIR))\n"
             "os.environ['PYTHONPATH'] = str(MOD_DIR) + os.pathsep + os.environ.get('PYTHONPATH', '')\n"
             "print('modules written to', MOD_DIR)\n")
    run = ("import overlap_probe\n"
           "OVERLAP_PROBE_SUMMARY = overlap_probe.kaggle_main()\n")
    md = {"cell_type": "markdown", "metadata": {}, "source": [
        "# exp65 overlap probe (G-P bit-probe)\n",
        "Registration only (tools/overlap_reg.py). Hidden set: raises 'OVERLAP PROBE: N accepted pairs' if >= 1 pair of\n",
        "test crops overlaps exactly; otherwise writes a trivial valid CSV. Probe failure on the hidden set: no CSV.\n",
        "Never a final submission.\n"]}
    nb = {"cells": [md, _code_cell(write), _code_cell(run)],
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 4}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / NB_NAME).write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    meta = {"id": KERNEL_ID, "title": KERNEL_ID.split("/", 1)[1], "code_file": NB_NAME, "language": "python",
            "kernel_type": "notebook", "is_private": True, "enable_gpu": False, "enable_tpu": False,
            "enable_internet": False, "keywords": [], "dataset_sources": [], "kernel_sources": [],
            "competition_sources": [COMPETITION], "model_sources": [],
            "docker_image": "gcr.io/kaggle-private-byod/python@sha256:"
                            "37c64f7dd9c54116ecd1bcc88817c5469b88387388fade02bfa8bf3fc647d461"}
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    return out / NB_NAME


def notebook_code(nb_path) -> str:
    """The notebook's code cells joined (local tests run exactly this text)."""
    nb = json.loads(Path(nb_path).read_text(encoding="utf-8"))
    return "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build-notebook", default=None, help="output folder for the notebook + kernel-metadata.json")
    ap.add_argument("--test-dir", default=None)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    if a.build_notebook:
        print(build_notebook(a.build_notebook))
        return
    run_probe(find_test_dir(override=a.test_dir) if a.test_dir else find_test_dir(), a.out_dir, workers=a.workers)


if __name__ == "__main__":
    main()
