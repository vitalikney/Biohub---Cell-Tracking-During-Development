"""B20 pass 1: stream all 199 train videos through the local port in ~10-video bundles (CONTEXT_FRIEND_B.md §38).

Per bundle: rewrite the private bundling kernel's stem list -> push -> poll -> download its single zip -> unzip into
the data dir -> exp29 inference with --keep-peak-prob into the shared tag `exp29pp` -> delete the .zarr videos
(GT .geff files stay, they are small). Raw prediction graphs accumulate in .public_local_cache/exp29pp/raw/.
Videos already present locally are inferred without downloading. Resumable: stems whose raw graph exists are skipped.

    python stream_bundles.py --bundle-size 10 [--max-bundles N] [--dry-run]
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA = ROOT / "biohub-cell-tracking-during-development"
TRAIN = DATA / "train"
KDIR = Path(__file__).resolve().parent / "kernel_fetch_missing"
KID = "gsfatakhov/biohub-loeo44b6-missing-videos"
PY = sys.executable
TAG = "exp29pp"
RAW = ROOT / ".public_local_cache" / TAG / "raw"
LOG = Path(__file__).resolve().parent / "results" / "stream_bundles.log"


def log(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as fh:
        fh.write(line + "\n")


def run(cmd, **kw):
    log("$ " + " ".join(map(str, cmd)))
    return subprocess.run(cmd, cwd=ROOT, **kw)


def run_retry(cmd, ok, tries=6, wait=60, **kw):
    """Run a network command until `ok(result)` is true; the Kaggle endpoints time out transiently."""
    for k in range(tries):
        r = run(cmd, capture_output=True, text=True, **kw)
        if ok(r):
            return r
        log(f"attempt {k + 1}/{tries} failed: {(r.stdout + r.stderr).strip()[-300:]}")
        time.sleep(wait * (k + 1))
    raise RuntimeError(f"gave up after {tries} attempts: {' '.join(map(str, cmd))}")


def all_stems() -> list[str]:
    idx = json.loads((DATA / "_file_index.json").read_text())
    return sorted({f["name"].split("/")[1].rsplit(".", 1)[0] for f in idx if f["name"].startswith("train/")})


def complete_locally(stem: str, idx_sizes: dict) -> bool:
    want = [n for n in idx_sizes if n.startswith(f"train/{stem}.")]
    return all((DATA / n).is_file() and (DATA / n).stat().st_size == idx_sizes[n] for n in want)


def fetch_bundle(stems: list[str], out: Path) -> Path:
    script = KDIR / "fetch_missing.py"
    src = script.read_text()
    import re
    src = re.sub(r'STEMS = "[^"]*"\.split\(\)', f'STEMS = "{" ".join(stems)}".split()', src, count=1)
    script.write_text(src)
    run_retry(["kaggle", "kernels", "push", "-p", str(KDIR)], lambda r: r.returncode == 0 and "pushed" in r.stdout.lower())
    t0 = time.time()
    while True:
        st = run_retry(["kaggle", "kernels", "status", KID], lambda r: "KernelWorkerStatus" in r.stdout, tries=10, wait=30).stdout
        if "COMPLETE" in st:
            break
        if "ERROR" in st or "CANCEL" in st:
            raise RuntimeError(f"kernel failed: {st}")
        if time.time() - t0 > 3600:
            raise RuntimeError("kernel timeout")
        time.sleep(45)
    log(f"kernel complete in {(time.time() - t0) / 60:.1f} min")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    def got_zip(r):
        zs = list(out.glob("*.zip"))
        return bool(zs) and zs[0].stat().st_size > 1e8
    run_retry(["kaggle", "kernels", "output", KID, "-p", str(out)], got_zip, tries=8, wait=90)
    z = list(out.glob("*.zip"))[0]
    log(f"downloaded {z.name} {z.stat().st_size / 1e9:.2f} GB")
    return z


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle-size", type=int, default=10)
    ap.add_argument("--max-bundles", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    idx_sizes = {f["name"]: f["size"] for f in json.loads((DATA / "_file_index.json").read_text())}
    stems = all_stems()
    CK = RAW.parent / "ckpt"; DC = RAW.parent / "dc"
    done = {p.stem for p in RAW.glob("*.geff") if (CK / f"{p.stem}.npz").is_file() and (DC / f"{p.stem}.npz").is_file()} if RAW.is_dir() else set()
    todo = [s for s in stems if s not in done]
    local = [s for s in todo if complete_locally(s, idx_sizes)]
    remote = [s for s in todo if s not in local]
    log(f"{len(stems)} stems | done {len(done)} | todo {len(todo)} (local {len(local)}, to fetch {len(remote)})")
    if a.dry_run:
        return

    bundles = ([local] if local else []) + [remote[i:i + a.bundle_size] for i in range(0, len(remote), a.bundle_size)]
    if a.max_bundles:
        bundles = bundles[: a.max_bundles]
    for bi, stems_b in enumerate(bundles, 1):
        is_local = stems_b is local
        log(f"=== bundle {bi}/{len(bundles)}: {len(stems_b)} videos {'(local)' if is_local else ''}: {' '.join(stems_b)}")
        if not is_local:
            z = fetch_bundle(stems_b, ROOT / ".public_local_cache" / "_bundle")
            with zipfile.ZipFile(z) as zf:
                zf.extractall(DATA)
            z.unlink()
            missing = [s for s in stems_b if not complete_locally(s, idx_sizes)]
            if missing:
                raise RuntimeError(f"bundle incomplete after unzip: {missing}")
            log(f"bundle unpacked ({len(stems_b)} videos)")
        r = run([PY, str(ROOT / "tools" / "public_local.py"), "--tag", TAG, "--label", "base", "--stage", "infer",
                 "--keep-peak-prob", "--stems", *stems_b], capture_output=True, text=True)
        tail = "\n".join(r.stdout.splitlines()[-3:])
        log(f"inference exit={r.returncode}: {tail}")
        if r.returncode != 0:
            log(r.stderr[-2000:])
            raise RuntimeError("inference failed")
        got = [s for s in stems_b if (RAW / f"{s}.geff").is_dir()]
        if len(got) != len(stems_b):
            raise RuntimeError(f"raw graphs missing after inference: {set(stems_b) - set(got)}")
        # pass-1 extras while the frames are on disk: post-gap checkpoint + DeepCenter score per raw node (§38.6)
        r = run([PY, str(Path(__file__).resolve().parent / "pass1_extras.py"), "--tag", TAG, "--stems", *stems_b], capture_output=True, text=True)
        log(f"extras exit={r.returncode}: " + "\n".join(l for l in r.stdout.splitlines() if l.startswith("44b6") or l.startswith("6bba"))[-600:])
        if r.returncode != 0:
            log(r.stderr[-2000:]); raise RuntimeError("pass1 extras failed")
        miss = [s for s in stems_b if not ((CK / f"{s}.npz").is_file() and (DC / f"{s}.npz").is_file())]
        if miss:
            raise RuntimeError(f"extras missing: {miss}")
        if not is_local:
            for s in stems_b:
                shutil.rmtree(TRAIN / f"{s}.zarr", ignore_errors=True)
            log("bundle videos deleted (GT geffs kept)")
    log("=== STREAM DONE")


if __name__ == "__main__":
    main()
