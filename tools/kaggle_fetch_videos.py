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

RATE LIMITS: Kaggle throttles aggressively. A 16-worker burst earned HTTP 429 with `Retry-After: 4455`
(74 minutes), and the Kaggle client does not surface that - it builds connections with no timeout and simply
wedges, so every worker sits at zero bytes while the site is up. Downloads therefore go through the REST
endpoint directly, with a deadline per request and a process-wide pause that honours Retry-After. Keep
--workers small (default 4).
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


DOWNLOAD_URL = "https://www.kaggle.com/api/v1/competitions/data/download/{comp}/{file}"
# Set when the server answers 429: no worker starts a new request before this wall-clock time.
_RATE_LIMIT_UNTIL = 0.0
_RATE_LOCK = None


def _credentials() -> tuple[str, str]:
    cfg = json.loads((Path.home() / ".kaggle" / "kaggle.json").read_text())
    return cfg["username"], cfg["key"]


def _respect_rate_limit() -> None:
    while True:
        with _RATE_LOCK:
            wait = _RATE_LIMIT_UNTIL - time.time()
        if wait <= 0:
            return
        time.sleep(min(wait, 30.0))


def _note_rate_limit(retry_after: float) -> None:
    global _RATE_LIMIT_UNTIL
    with _RATE_LOCK:
        until = time.time() + retry_after
        if until > _RATE_LIMIT_UNTIL:
            _RATE_LIMIT_UNTIL = until
            print(f"  RATE LIMITED: pausing all workers for {retry_after / 60:.1f} min", flush=True)


def fetch_one(session, name: str, size: int, out: Path, timeout: float) -> tuple[str, str]:
    """Download one competition file.

    Uses the REST endpoint directly rather than `api.competition_download_file`: the Kaggle client builds its
    connections without a timeout and, when the server answers 429, it wedges instead of raising - observed as
    every worker stalled with zero bytes moving while the site was up. Here a 429 is surfaced, its Retry-After
    is honoured process-wide, and every request has a deadline.
    """
    import urllib.parse

    dst = out / name
    if dst.is_file() and (size == 0 or dst.stat().st_size == size):
        return name, "skip"
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + f".part{os.getpid()}")
    url = DOWNLOAD_URL.format(comp=COMP, file=urllib.parse.quote(name, safe=""))

    for attempt in range(6):
        _respect_rate_limit()
        try:
            with session.get(url, stream=True, timeout=timeout, allow_redirects=True) as r:
                if r.status_code == 429:
                    _note_rate_limit(float(r.headers.get("retry-after", 300)) + 5.0)
                    continue
                r.raise_for_status()
                written = 0
                with tmp.open("wb") as fh:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        fh.write(chunk)
                        written += len(chunk)
            if size and written != size:
                raise RuntimeError(f"size mismatch {written} != {size}")
            os.replace(tmp, dst)
            return name, "ok"
        except Exception as e:  # noqa: BLE001
            tmp.unlink(missing_ok=True)
            if attempt == 5:
                return name, f"FAIL {e}"
            time.sleep(3 * (attempt + 1))
    return name, "FAIL"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", help="JSON with lists of stems")
    ap.add_argument("--key", default="holdout", help="key inside --split JSON")
    ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    # Kaggle rate-limits hard: a 16-worker burst earned a 429 with Retry-After of 74 minutes. Keep this low.
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=120.0, help="per-request deadline in seconds")
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

    global _RATE_LOCK
    import threading

    import requests

    _RATE_LOCK = threading.Lock()
    session = requests.Session()
    session.auth = _credentials()

    t0 = time.time()
    n_ok = n_skip = n_fail = 0
    done_mb = 0.0
    fails = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch_one, session, f["name"], f["size"], out, args.timeout): f for f in todo}
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
