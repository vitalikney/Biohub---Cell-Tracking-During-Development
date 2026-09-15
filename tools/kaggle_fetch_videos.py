"""Download a SUBSET of competition videos (zarr + geff) with the Kaggle API, keeping the directory layout.

The competition zip is ~88 GB; `kaggle competitions download -f <file>` fetches one file but flattens its path.
This script lists every competition file once (cached JSON, ~200 API pages), filters by video stem and
downloads the matching files in parallel into `<out>/train/<stem>.zarr/...` and `<out>/train/<stem>.geff/...`,
skipping files that already exist with the right size. Safe to re-run (resumes).

Usage:
    python tools/kaggle_fetch_videos.py --split experiments/_lib/loeo_train6bba_val44b6.json --key holdout
    python tools/kaggle_fetch_videos.py --stems 44b6_12dfb391 6bba_062c8d37 [--out biohub-cell-tracking-during-development]
    python tools/kaggle_fetch_videos.py --list-only          # only (re)build the file index

Needs ~/.kaggle/kaggle.json. One video = ~100 zarr chunks (~4.5 MB each) + a few dozen small geff files.
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

COMP = "biohub-cell-tracking-during-development"
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "biohub-cell-tracking-during-development"
INDEX = ROOT / "biohub-cell-tracking-during-development" / "_file_index.json"


def build_index(api, index_path: Path) -> list[dict]:
    files, token, page = [], None, 0
    while True:
        for attempt in range(5):
            try:
                r = api.competition_list_files(COMP, page_token=token, page_size=200)
                break
            except Exception as e:  # noqa: BLE001
                print(f"list page {page} failed ({e}); retry {attempt + 1}", file=sys.stderr)
                time.sleep(2 * (attempt + 1))
        else:
            raise RuntimeError("file listing failed")
        files.extend({"name": f.name, "size": int(getattr(f, "total_bytes", 0) or 0)} for f in r.files)
        page += 1
        token = r.next_page_token
        if page % 20 == 0:
            print(f"  listed {len(files)} files ({page} pages)")
        if not token:
            break
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(files))
    print(f"index: {len(files)} files -> {index_path}")
    return files


def fetch_one(api, name: str, size: int, out: Path) -> tuple[str, str]:
    dst = out / name
    if dst.is_file() and (size == 0 or dst.stat().st_size == size):
        return name, "skip"
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = dst.parent / f".tmp_{os.getpid()}_{abs(hash(name)) % 10**8}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    try:
        for attempt in range(6):
            try:
                api.competition_download_file(COMP, name, path=str(tmp_dir), force=True, quiet=True)
                got = tmp_dir / Path(name).name
                if not got.is_file():
                    cands = list(tmp_dir.iterdir())
                    if len(cands) != 1:
                        raise RuntimeError(f"unexpected download result {cands}")
                    got = cands[0]
                if size and got.stat().st_size != size:
                    raise RuntimeError(f"size mismatch {got.stat().st_size} != {size}")
                os.replace(got, dst)
                return name, "ok"
            except Exception as e:  # noqa: BLE001
                if attempt == 5:
                    return name, f"FAIL {e}"
                time.sleep(3 * (attempt + 1))
    finally:
        for p in tmp_dir.glob("*"):
            p.unlink(missing_ok=True)
        tmp_dir.rmdir()
    return name, "FAIL"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", help="JSON with lists of stems")
    ap.add_argument("--key", default="holdout", help="key inside --split JSON")
    ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--refresh-index", action="store_true")
    ap.add_argument("--list-only", action="store_true")
    ap.add_argument("--zarr-only", action="store_true", help="skip the .geff ground-truth files")
    args = ap.parse_args()

    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()

    out = Path(args.out)
    index_path = out / "_file_index.json"
    if args.refresh_index or not index_path.is_file():
        files = build_index(api, index_path)
    else:
        files = json.loads(index_path.read_text())
        print(f"index: {len(files)} files (cached {index_path})")
    if args.list_only:
        return

    stems = list(args.stems)
    if args.split:
        stems += list(json.load(open(args.split))[args.key])
    stems = sorted(set(stems))
    if not stems:
        ap.error("no stems given")
    prefixes = tuple(f"train/{s}." for s in stems)
    todo = [f for f in files if f["name"].startswith(prefixes)]
    if args.zarr_only:
        todo = [f for f in todo if ".geff/" not in f["name"]]
    total_mb = sum(f["size"] for f in todo) / 1e6
    print(f"{len(stems)} videos -> {len(todo)} files, {total_mb:.0f} MB -> {out}")
    found = {s for s in stems if any(f["name"].startswith(f"train/{s}.") for f in todo)}
    missing = sorted(set(stems) - found)
    if missing:
        print("WARNING: no files in the competition index for:", missing)

    t0 = time.time()
    n_ok = n_skip = n_fail = 0
    done_mb = 0.0
    fails = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch_one, api, f["name"], f["size"], out): f for f in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            f = futs[fut]
            name, status = fut.result()
            if status == "ok":
                n_ok += 1
                done_mb += f["size"] / 1e6
            elif status == "skip":
                n_skip += 1
            else:
                n_fail += 1
                fails.append((name, status))
            if i % 50 == 0 or i == len(todo):
                el = time.time() - t0
                print(f"  {i}/{len(todo)} ok={n_ok} skip={n_skip} fail={n_fail} {done_mb:.0f} MB "
                      f"{done_mb / max(el, 1e-9):.1f} MB/s elapsed {el / 60:.1f} min", flush=True)
    if fails:
        print("FAILED files:")
        for name, st in fails:
            print("  ", name, st)
        sys.exit(1)
    print("done")


if __name__ == "__main__":
    main()
