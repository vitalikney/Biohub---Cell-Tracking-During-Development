"""Kaggle CPU replay lab: run experiments/l2_daughternet/replay/replay.py on free Kaggle CPU kernels (4 vCPU, 32 GB
RAM, no GPU quota) instead of the laptop, several jobs in parallel.

SUBCOMMANDS
    push-code [--force] [--skip-verify] [-m MSG]
        Bundle replay.py + its repo import closure (AST walk over imports, importlib.import_module("x") and
        ROOT / "a" / "b.py" path literals) + data files (splits.json, the exp29 notebook, tools/official/) into ONE zip
        stored as lab_code.bin (a non-archive extension: Kaggle neither unpacks it nor converts tabular files inside it)
        + lab_manifest.json (per-file sha256, bundle sha256, git HEAD, local package versions), and upload it as the
        PRIVATE dataset vitaliineibauer/biohub-lab-code (created the first time, new version afterwards; `-p .` from
        inside the stage folder, --keep-tabular). Before uploading, the bundle is extracted to a scratch dir and imported
        there (replay module + init_context: notebook namespace, scorer, div_insert) in a low-priority single process,
        so a missing module fails here and not on Kaggle. Waits until the new version is served (its manifest matches).
        Also makes sure the PRIVATE dataset vitaliineibauer/biohub-lab-wheels holds manylinux cp312 wheels of the
        locally installed versions of the result-relevant packages (PINNED_DISTS; uploaded only when the pins change).
    run NAME [--dataset OWNER/SLUG ...] [--map LOCAL=KAGGLE_PATH ...] [--workers 4] [--keep-tail] [--wait-slot]
             [--stale-ok] [--dry-run] -- <replay.py args exactly as for a local run>
        Builds and pushes the PRIVATE CPU kernel vitaliineibauer/biohub-lab-NAME (script kernel, enable_gpu false,
        enable_internet false; sources: competition data, sasyami/biohub-friend-a-b20-cache, biohub-lab-code,
        biohub-lab-wheels, pilkwang/biohub-tracking-support-pack-50ep-v1 (fallback wheels for unpinned dependencies)
        + every --dataset). Local paths in the replay args are rewritten at kernel run time:
            --cache/--node-p/--grid/--splits PATH  bundled repo file -> its extracted copy; small file (<= 4 MB, not
                                                   under data_external/) -> embedded in the kernel script; otherwise
                                                   looked up under the attached datasets by the longest matching
                                                   path suffix (e.g. .../friend_a_b20_exp29_friend_c/cache/
                                                   friend_a_b20_exp29 -> the sasyami dataset); ambiguity is an error
                                                   (fix with --map LOCAL=/kaggle/input/...)
            node_p=PATH inside --config            same rules
            --out                                  always /kaggle/working/out
            --export-coords PATH                   /kaggle/working/out/<basename>
            --data-dir                             always the competition train dir (GT .geff)
            --workers                              always --workers of this command (default 4)
        The kernel refuses to run on a stale code dataset (bundle sha256 recorded at `run` time must match the
        mounted one); `run` refuses when the local code differs from the last push-code (use --stale-ok to override).
        Heavy replay scratch (out/tail, out/work, out/node_p) is deleted at the end unless --keep-tail.
        Kaggle allows 5 concurrent batch CPU sessions per account (push error "Maximum batch CPU session count of 5
        reached", 2026-09-24); --wait-slot retries the push every --slot-poll s until a slot frees up.
    pull NAME [--no-wait] [--poll S] [--timeout S]
        Waits for the kernel, downloads its output (retries transient failures) into
        .public_local_cache/kaggle_lab/NAME/ and prints lab_run.json timings + the replay report.
    status
        Lists our lab kernels (registry + `kaggle kernels list --mine`) with their Kaggle states.

EXAMPLES
    nice -n 19 python tools/kaggle_lab.py push-code
    nice -n 19 python tools/kaggle_lab.py run exp39-all -- --cache data_external/friend_a_cache/\
friend_a_b20_exp29_friend_c/cache/friend_a_b20_exp29 --split all --configs exp39 --control exp39
    nice -n 19 python tools/kaggle_lab.py pull exp39-all
    nice -n 19 python tools/kaggle_lab.py status
"""

from __future__ import annotations

import argparse
import ast
import base64
import datetime as dt
import hashlib
import importlib.metadata
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER = "vitaliineibauer"
CODE_REF = f"{OWNER}/biohub-lab-code"
WHEELS_REF = f"{OWNER}/biohub-lab-wheels"
CACHE_REF = "sasyami/biohub-friend-a-b20-cache"
SUPPORT_REF = "pilkwang/biohub-tracking-support-pack-50ep-v1"  # its wheels/ = fallback for unpinned dependencies
COMPETITION = "biohub-cell-tracking-during-development"
KERNEL_PREFIX = "biohub-lab-"
REPLAY_REL = "experiments/l2_daughternet/replay/replay.py"
LAB_HOME = ROOT / ".public_local_cache" / "kaggle_lab"
CODE_STAGE = LAB_HOME / "_code_dataset"
WHEELS_STAGE = LAB_HOME / "_wheels_dataset"
KERNEL_STAGE = LAB_HOME / "_kernels"
REGISTRY = LAB_HOME / "registry.json"
BUNDLE_NAME = "lab_code.bin"
MANIFEST_NAME = "lab_manifest.json"
WHEELS_MANIFEST_NAME = "wheels_manifest.json"

# Code closure: seeds + files that are data, not imports + import search dirs (replay.py's own sys.path entries,
# score_geffs' tools/official paths).
SEED_FILES = [REPLAY_REL]
EXTRA_FILES = ["experiments/l2_daughternet/splits.json",
               "experiments/exp29_sjlee947_verbatim/exp29-sjlee947-verbatim.ipynb"]  # public_local.DEFAULT_NOTEBOOK
EXTRA_TREES = ["tools/official"]
SEARCH_DIRS = ["tools", "experiments/local_friend_b_exp02_public_port", "tools/official/src", "tools/official/scripts"]
PATH_LITERAL_SUFFIXES = (".py", ".json", ".ipynb")
PATH_LITERAL_MAX_BYTES = 5 * 1024 * 1024

# Packages pinned on Kaggle to the LOCAL versions (the lab's numbers must not depend on the image). The Kaggle CPU image
# (2026-09-24: py 3.12.13, numpy 2.0.2, scipy 1.16.3, pandas 2.3.3, polars 1.35.2) lacks tracksdata/geff/zarr/rustworkx
# and has different numerics stacks; unpinned transitive dependencies come from the image or the support pack wheels.
PINNED_DISTS = ["numpy", "scipy", "pandas", "polars", "polars-runtime-32", "networkx", "rustworkx", "tracksdata",
                "geff", "geff-spec", "zarr", "numcodecs", "rstar-python"]
WHEEL_PLATFORM_ARGS = ["--only-binary=:all:", "--python-version", "3.12", "--implementation", "cp",
                       "--abi", "cp312", "--abi", "abi3", "--abi", "none",
                       "--platform", "manylinux_2_28_x86_64", "--platform", "manylinux_2_27_x86_64",
                       "--platform", "manylinux_2_17_x86_64", "--platform", "manylinux2014_x86_64",
                       "--platform", "any"]

# replay.py options that carry paths
INPUT_PATH_OPTS = ("--cache", "--node-p", "--grid", "--splits")
OUTPUT_FILE_OPTS = ("--export-coords",)
DROPPED_OPTS = ("--out", "--data-dir", "--workers")
UNSUPPORTED_OPTS = ("--make-synthetic-cache",)
EMBED_MAX_BYTES = 4 * 1024 * 1024
TERMINAL_STATES = ("complete", "error", "cancelacknowledged", "cancelrequested", "cancelled")


# ------------------------------------------------------------------------------------------------ small helpers
def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(Path(path).read_bytes())


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _kaggle(args: list[str], cwd: Path | None = None, retries: int = 1, check: bool = True,
            timeout: int = 1800) -> subprocess.CompletedProcess:
    """Run the Kaggle CLI (python -m kaggle ...); retry transient failures."""
    cmd = [sys.executable, "-m", "kaggle", *args]
    last = None
    for attempt in range(retries):
        try:
            last = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                  timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            last = subprocess.CompletedProcess(cmd, 124, "", f"timeout after {timeout} s: {exc}")
        text = (last.stdout or "") + (last.stderr or "")
        transient = any(k in text.lower() for k in ("timed out", "timeout", "connection", "temporarily", "502", "503",
                                                    "504", "remote end closed", "reset by peer"))
        if last.returncode == 0 and not (transient and "error" in text.lower()):
            return last
        if re.search(r"\b(403|404) Client Error", text):
            break  # permanent (missing / not ours): no retry
        if attempt + 1 < retries:
            wait = min(10 * (attempt + 1), 60)
            print(f"  kaggle {' '.join(args[:2])}: attempt {attempt + 1} failed ({text.strip()[-200:]!r}); "
                  f"retry in {wait} s", flush=True)
            time.sleep(wait)
    if check:
        raise SystemExit(f"kaggle {' '.join(args)} failed (rc {last.returncode}):\n{last.stdout}\n{last.stderr}")
    return last


def _low_priority_kwargs() -> dict:
    """Subprocess kwargs for idle CPU priority (the laptop is in use)."""
    if os.name == "nt":
        return {"creationflags": 0x00000040}  # IDLE_PRIORITY_CLASS
    return {"preexec_fn": lambda: os.nice(19)}


def _load_json(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=60).stdout.rstrip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


# ------------------------------------------------------------------------------------------------ code closure
def _callee(node: ast.Call) -> str:
    f = node.func
    return f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")


def _module_files(name: str, dirs: list[Path]) -> list[Path]:
    """Repo files for top-level module `name` searched in `dirs` (a package -> all its .py files)."""
    for d in dirs:
        single = d / f"{name}.py"
        if single.is_file():
            return [single]
        pkg = d / name
        if (pkg / "__init__.py").is_file():
            return sorted(p for p in pkg.rglob("*.py") if "__pycache__" not in p.parts)
    return []


def code_closure() -> list[str]:
    """Repo-relative posix paths of every file the lab needs (see module docstring)."""
    search = [ROOT / d for d in SEARCH_DIRS]
    files: set[str] = set()
    todo = [ROOT / s for s in SEED_FILES]
    while todo:
        path = todo.pop()
        rel = _rel(path)
        if rel in files:
            continue
        files.add(rel)
        if path.suffix != ".py":
            continue
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(path))
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    names.add(node.module.split(".")[0])
                elif node.level > 0:  # relative import inside a package: take the whole package
                    pkg = path.parent
                    for _ in range(node.level - 1):
                        pkg = pkg.parent
                    todo.extend(p for p in pkg.rglob("*.py") if "__pycache__" not in p.parts)
            elif (isinstance(node, ast.Call) and _callee(node) == "import_module" and node.args
                  and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                names.add(node.args[0].value.split(".")[0])
        for name in sorted(names):
            todo.extend(_module_files(name, [path.parent, *search]))
        # path literals: ROOT / "experiments" / "x" / "y.py", PROJECT_ROOT / "experiments/a/b.ipynb", TOOLS / "z.py"
        for match in re.finditer(r'\b[A-Za-z_]+((?:\s*/\s*"[^"\n]+")+)', src):
            parts = re.findall(r'"([^"\n]+)"', match.group(1))
            for base in (ROOT, ROOT / "tools", path.parent):
                cand = base.joinpath(*parts)
                try:
                    ok = (cand.is_file() and cand.suffix in PATH_LITERAL_SUFFIXES
                          and cand.stat().st_size <= PATH_LITERAL_MAX_BYTES and ROOT in cand.resolve().parents)
                except OSError:
                    ok = False
                if ok:
                    todo.append(cand)
                    break
    for rel in EXTRA_FILES:
        if not (ROOT / rel).is_file():
            raise SystemExit(f"missing lab data file {rel}")
        files.add(rel)
    for tree_rel in EXTRA_TREES:
        for p in (ROOT / tree_rel).rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                files.add(_rel(p))
    return sorted(files)


def build_bundle(files: list[str]) -> tuple[bytes, dict[str, str]]:
    """Deterministic zip (sorted names, fixed timestamps): unchanged code -> identical sha256."""
    hashes: dict[str, str] = {}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in files:
            data = (ROOT / rel).read_bytes()
            hashes[rel] = _sha256_bytes(data)
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)
    return buf.getvalue(), hashes


VERIFY_SCRIPT = r'''
import importlib, importlib.util, json, sys
from pathlib import Path
lab, scratch, repo = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]).resolve()
path = lab / "__REPLAY_REL__"
spec = importlib.util.spec_from_file_location("lab_replay", path)
mod = importlib.util.module_from_spec(spec)
sys.modules["lab_replay"] = mod
spec.loader.exec_module(mod)
(scratch / "data").mkdir(parents=True, exist_ok=True)
mod.init_context({"cache": str(scratch), "data_dir": str(scratch / "data"), "out": str(scratch / "out"),
                  "need_insert": True})
importlib.import_module("tracking_cellmot.metrics")
loaded, outside = [], []
for m in list(sys.modules.values()):
    f = getattr(m, "__file__", None)
    if not f:
        continue
    p = Path(f).resolve()
    if p == Path(__file__).resolve():
        continue  # this check script itself
    if lab.resolve() in p.parents:
        loaded.append(p.relative_to(lab.resolve()).as_posix())
    elif repo in p.parents:
        outside.append(str(p))
print(json.dumps({"loaded_from_bundle": sorted(loaded), "loaded_from_repo": sorted(outside)}))
'''


def verify_bundle(bundle: bytes) -> dict:
    """Extract the bundle and import it there (one low-priority process, no replay work)."""
    scratch = LAB_HOME / "_verify"
    shutil.rmtree(scratch, ignore_errors=True)
    lab = scratch / "lab"
    with zipfile.ZipFile(io.BytesIO(bundle)) as zf:
        zf.extractall(lab)
    script = scratch / "verify.py"
    script.write_text(VERIFY_SCRIPT.replace("__REPLAY_REL__", REPLAY_REL), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "BIOHUB_DATA_DIR")}
    started = time.time()
    proc = subprocess.run([sys.executable, str(script), str(lab), str(scratch / "work"), str(ROOT)], cwd=lab, env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900,
                          **_low_priority_kwargs())
    if proc.returncode != 0:
        raise SystemExit(f"bundle import check FAILED (the bundle misses a module?):\n{proc.stdout[-3000:]}\n"
                         f"{proc.stderr[-5000:]}")
    result = json.loads(proc.stdout.strip().splitlines()[-1])
    if result["loaded_from_repo"]:
        raise SystemExit(f"bundle import check: modules were imported from the repo, not the bundle: "
                         f"{result['loaded_from_repo']}")
    result["seconds"] = round(time.time() - started, 1)
    shutil.rmtree(scratch, ignore_errors=True)
    return result


# ------------------------------------------------------------------------------------------------ datasets
def dataset_exists(ref: str) -> bool:
    proc = _kaggle(["datasets", "status", ref], retries=3, check=False, timeout=120)
    text = (proc.stdout + proc.stderr).lower()
    if proc.returncode == 0 and "ready" in text:
        return True
    # a dataset of ours that does not exist answers 403 Forbidden (2026-09-24), older API versions 404
    if any(k in text for k in ("403", "forbidden", "404", "not found", "does not exist")):
        return False
    if proc.returncode == 0:
        return True  # exists but e.g. still processing
    raise SystemExit(f"kaggle datasets status {ref}: {proc.stdout}{proc.stderr}")


def upload_dataset(stage: Path, ref: str, message: str) -> None:
    """Create (first time) or version the PRIVATE dataset from inside its stage folder (`-p .`, keep tabular files)."""
    if dataset_exists(ref):
        print(f"  uploading new version of {ref} ...", flush=True)
        _kaggle(["datasets", "version", "-p", ".", "-t", "-m", message], cwd=stage, retries=2, timeout=3600)
    else:
        print(f"  creating PRIVATE dataset {ref} ...", flush=True)
        _kaggle(["datasets", "create", "-p", ".", "-t"], cwd=stage, retries=2, timeout=3600)


def remote_json(ref: str, filename: str, dest: Path) -> dict | None:
    """Download one small JSON file of the dataset's current version."""
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)
    proc = _kaggle(["datasets", "download", ref, "-f", filename, "-p", str(dest), "--force"], retries=2, check=False,
                   timeout=300)
    if proc.returncode != 0:
        return None
    target = dest / filename
    if not target.is_file():
        for z in dest.glob("*.zip"):
            with zipfile.ZipFile(z) as zf:
                zf.extractall(dest)
    return _load_json(target)


def wait_for_remote(ref: str, filename: str, key: str, want: str, timeout: int = 1200) -> None:
    started = time.time()
    while True:
        got = remote_json(ref, filename, LAB_HOME / "_remote" / ref.replace("/", "__"))
        if got and got.get(key) == want:
            print(f"  {ref}: new version is served ({key} {want[:12]}), {time.time() - started:.0f} s", flush=True)
            return
        if time.time() - started > timeout:
            raise SystemExit(f"{ref}: the uploaded version is not served after {timeout} s "
                             f"(remote {key} = {(got or {}).get(key)}); re-check later with push-code")
        time.sleep(20)


def local_pins() -> dict[str, str]:
    pins = {}
    for dist in PINNED_DISTS:
        try:
            pins[dist] = importlib.metadata.version(dist)
        except importlib.metadata.PackageNotFoundError:
            raise SystemExit(f"{dist} is not installed locally; cannot pin it") from None
    return pins


def ensure_wheels(force: bool = False) -> dict:
    """biohub-lab-wheels = manylinux cp312 wheels of the local versions of PINNED_DISTS (uploaded on pin change)."""
    pins = local_pins()
    manifest_path = WHEELS_STAGE / WHEELS_MANIFEST_NAME
    manifest = _load_json(manifest_path, {}) or {}
    remote = remote_json(WHEELS_REF, WHEELS_MANIFEST_NAME, LAB_HOME / "_remote" / "wheels")
    if not force and remote and remote.get("pins") == pins and manifest.get("pins") == pins:
        print(f"wheels: {WHEELS_REF} up to date ({len(pins)} pins)", flush=True)
        return manifest
    print(f"wheels: building {WHEELS_REF} for pins {pins}", flush=True)
    shutil.rmtree(WHEELS_STAGE, ignore_errors=True)
    WHEELS_STAGE.mkdir(parents=True)
    cache = LAB_HOME / "_wheel_cache"
    cache.mkdir(parents=True, exist_ok=True)
    for dist, version in pins.items():
        norm = re.sub(r"[-_.]+", "_", dist).lower()
        have = [p for p in cache.glob("*.whl")
                if re.sub(r"[-_.]+", "_", p.name.split("-")[0]).lower() == norm and p.name.split("-")[1] == version]
        if not have:
            proc = subprocess.run([sys.executable, "-m", "pip", "download", "--no-deps", "--disable-pip-version-check",
                                   *WHEEL_PLATFORM_ARGS, "-d", str(cache), f"{dist}=={version}"],
                                  capture_output=True, text=True, timeout=1800, **_low_priority_kwargs())
            if proc.returncode != 0:
                raise SystemExit(f"pip download {dist}=={version} failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
            have = [p for p in cache.glob("*.whl")
                    if re.sub(r"[-_.]+", "_", p.name.split("-")[0]).lower() == norm and p.name.split("-")[1] == version]
        if not have:
            raise SystemExit(f"no wheel for {dist}=={version} in {cache}")
        shutil.copy2(have[0], WHEELS_STAGE / have[0].name)
    manifest = {"pins": pins, "wheels": {p.name: _sha256_file(p) for p in sorted(WHEELS_STAGE.glob("*.whl"))},
                "created_utc": _now(), "target": "manylinux x86_64 cp312 (Kaggle CPU image, python 3.12)"}
    _write_json(manifest_path, manifest)
    _write_json(WHEELS_STAGE / "dataset-metadata.json",
                {"title": WHEELS_REF.split("/")[1], "id": WHEELS_REF, "licenses": [{"name": "other"}]})
    upload_dataset(WHEELS_STAGE, WHEELS_REF, f"pins {json.dumps(pins, sort_keys=True)}"[:250])
    wait_for_remote(WHEELS_REF, WHEELS_MANIFEST_NAME, "created_utc", manifest["created_utc"])
    return manifest


def cmd_push_code(args) -> None:
    started = time.time()
    LAB_HOME.mkdir(parents=True, exist_ok=True)
    files = code_closure()
    bundle, hashes = build_bundle(files)
    bundle_sha = _sha256_bytes(bundle)
    total = sum((ROOT / f).stat().st_size for f in files)
    print(f"closure: {len(files)} files, {total / 1e6:.2f} MB raw, bundle {len(bundle) / 1e6:.2f} MB, "
          f"sha256 {bundle_sha[:16]}", flush=True)
    for f in files:
        print(f"    {f}", flush=True)
    wheels = ensure_wheels(force=args.force_wheels)
    pushed = _load_json(CODE_STAGE / "pushed.json", {}) or {}
    if not args.force and pushed.get("bundle_sha256") == bundle_sha:
        remote = remote_json(CODE_REF, MANIFEST_NAME, LAB_HOME / "_remote" / "code")
        if remote and remote.get("bundle_sha256") == bundle_sha:
            print(f"code: {CODE_REF} already serves this bundle ({bundle_sha[:16]}); nothing to push "
                  f"({time.time() - started:.0f} s)", flush=True)
            return
    verify = {"skipped": True}
    if not args.skip_verify:
        print("verifying the bundle (extract + import replay/init_context, idle priority) ...", flush=True)
        verify = verify_bundle(bundle)
        print(f"  OK in {verify['seconds']} s: {len(verify['loaded_from_bundle'])} bundle modules imported, "
              f"none from the repo", flush=True)
        unused = sorted(f for f in files if f.endswith(".py") and f not in verify["loaded_from_bundle"])
        if unused:
            print(f"  (bundled but not imported by the check - lazy imports or unused: {len(unused)} files)",
                  flush=True)
    dirty_files = sorted(line[3:].strip().strip('"') for line in _git("status", "--porcelain").splitlines() if line)
    manifest = {
        "bundle_sha256": bundle_sha, "bundle": BUNDLE_NAME, "replay": REPLAY_REL, "files": hashes,
        "created_utc": _now(), "git_head": _git("rev-parse", "HEAD"),
        "git_dirty_bundled": sorted(f for f in files if any(f == d or f.startswith(d.rstrip("/") + "/")
                                                            for d in dirty_files)),
        "local_python": sys.version.split()[0], "pins": wheels.get("pins"), "verify": verify,
    }
    shutil.rmtree(CODE_STAGE, ignore_errors=True)
    CODE_STAGE.mkdir(parents=True)
    (CODE_STAGE / BUNDLE_NAME).write_bytes(bundle)
    _write_json(CODE_STAGE / MANIFEST_NAME, manifest)
    _write_json(CODE_STAGE / "dataset-metadata.json",
                {"title": CODE_REF.split("/")[1], "id": CODE_REF, "licenses": [{"name": "other"}]})
    message = args.message or f"bundle {bundle_sha[:12]} git {manifest['git_head'][:8]}" + (
        f" +{len(manifest['git_dirty_bundled'])} dirty" if manifest["git_dirty_bundled"] else "")
    upload_dataset(CODE_STAGE, CODE_REF, message)
    wait_for_remote(CODE_REF, MANIFEST_NAME, "bundle_sha256", bundle_sha)
    _write_json(CODE_STAGE / "pushed.json", {"bundle_sha256": bundle_sha, "pushed_utc": _now(),
                                             "files": len(files), "message": message})
    print(f"push-code done in {time.time() - started:.0f} s: {CODE_REF} bundle {bundle_sha[:16]} "
          f"({len(manifest['git_dirty_bundled'])} bundled files with uncommitted changes)", flush=True)


# ------------------------------------------------------------------------------------------------ kernel launcher
KERNEL_TEMPLATE = r'''# Generated by tools/kaggle_lab.py (biohub CPU replay lab). Do not edit: re-run `kaggle_lab.py run` instead.
import base64, hashlib, json, os, shutil, subprocess, sys, threading, time, zipfile, zlib
from pathlib import Path

CFG = json.loads(__CFG_JSON__)
T0 = time.time()
INPUT = Path("/kaggle/input")
OUT = Path("/kaggle/working/out")
LAB = Path("/tmp/biohub_lab/code")
INPUTS = Path("/tmp/biohub_lab/inputs")
TIMES = {}
MEM = {"min_available_kb": None}


def log(msg):
    print(f"[lab {time.time() - T0:7.1f} s] {msg}", flush=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def dataset_root(ref):
    owner, slug = ref.split("/", 1)
    for cand in (INPUT / "datasets" / owner / slug, INPUT / slug):
        if cand.is_dir():
            return cand
    raise SystemExit(f"dataset {ref} is not mounted (no /kaggle/input/datasets/{owner}/{slug} or /kaggle/input/{slug})")


def competition_train():
    for cand in (INPUT / "competitions" / CFG["competition"] / "train", INPUT / CFG["competition"] / "train"):
        if cand.is_dir() and any(cand.glob("*.geff")):
            return cand
    raise SystemExit("competition train dir with GT .geff not found under /kaggle/input")


_INDEX = []


def index():
    if not _INDEX:
        for ref in CFG["search_datasets"]:
            for dirpath, dirnames, filenames in os.walk(dataset_root(ref)):
                keep = []
                for d in dirnames:
                    _INDEX.append((Path(dirpath) / d, True))
                    if not d.endswith((".geff", ".zarr")):
                        keep.append(d)
                dirnames[:] = keep
                _INDEX.extend((Path(dirpath) / f, False) for f in filenames)
    return _INDEX


def search(locator, want_dir):
    parts = [p for p in locator.split("/") if p]
    best, hits = 0, []
    for path, is_dir in index():
        if is_dir != want_dir:
            continue
        n, cp = 0, path.parts
        while n < len(parts) and n < len(cp) and cp[-1 - n] == parts[-1 - n]:
            n += 1
        if n == 0:
            continue
        if n > best:
            best, hits = n, [path]
        elif n == best:
            hits.append(path)
    if not hits:
        raise SystemExit(f"input {locator!r} not found in the attached datasets {CFG['search_datasets']} "
                         "(attach its dataset with run --dataset, or give --map)")
    if len(hits) > 1:
        raise SystemExit(f"input {locator!r} is ambiguous ({best} matching trailing components): "
                         f"{[str(h) for h in hits[:6]]}; use run --map LOCAL=/kaggle/input/...")
    return hits[0]


def resolve(spec, resolved):
    if isinstance(spec, str):
        return spec
    kind = spec["kind"]
    if kind == "join":
        return "".join(resolve(s, resolved) for s in spec["parts"])
    if kind == "bundle":
        value = str(LAB / spec["rel"])
    elif kind == "embed":
        target = INPUTS / spec["name"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(zlib.decompress(base64.b64decode(spec["data"])))
        if sha256(target) != spec["sha256"]:
            raise SystemExit(f"embedded input {spec['name']} is corrupt")
        value = str(target)
    elif kind == "search":
        value = str(search(spec["locator"], spec["dir"]))
    elif kind == "kaggle":
        value = spec["path"]
        if not Path(value).exists():
            raise SystemExit(f"mapped input {value} does not exist")
    elif kind == "out":
        value = str(OUT / spec["name"]) if spec.get("name") else str(OUT)
    elif kind == "data":
        value = str(competition_train())
    else:
        raise SystemExit(f"unknown arg spec {spec}")
    if kind not in ("out", "data"):
        resolved[spec.get("local", kind)] = value
    return value


def mem_sampler(stop):
    while not stop.is_set():
        try:
            for line in open("/proc/meminfo"):
                if line.startswith("MemAvailable:"):
                    kb = int(line.split()[1])
                    if MEM["min_available_kb"] is None or kb < MEM["min_available_kb"]:
                        MEM["min_available_kb"] = kb
        except OSError:
            pass
        stop.wait(5.0)


def versions():
    code = ("import importlib.metadata as m, json, sys; out={}\n"
            "for d in sys.argv[1:]:\n"
            "    try: out[d]=m.version(d)\n"
            "    except Exception: out[d]=None\n"
            "print(json.dumps(out))")
    names = sorted(set(CFG["pins"]) | {"torch", "pyarrow", "blosc2", "dask", "scikit-image", "numba", "pydantic"})
    proc = subprocess.run([sys.executable, "-c", code, *names], capture_output=True, text=True)
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stop = threading.Event()
    threading.Thread(target=mem_sampler, args=(stop,), daemon=True).start()
    run = {"name": CFG["name"], "kernel": CFG["kernel"], "pushed_utc": CFG["pushed_utc"],
           "started_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), "argv_local": CFG["argv_local"],
           "python": sys.version.split()[0], "nproc": os.cpu_count(), "bundle_sha256": CFG["bundle_sha256"]}
    try:
        run["cpu_model"] = next(l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name"))
        run["mem_total_gb"] = round(int(next(l.split()[1] for l in open("/proc/meminfo")
                                              if l.startswith("MemTotal:"))) / 1048576, 1)
    except Exception:
        pass
    rc = 1
    try:
        # 1. code bundle (refuse a stale dataset version)
        code_root = dataset_root(CFG["code_ref"])
        bundle = code_root / CFG["bundle_name"]
        got = sha256(bundle)
        if got != CFG["bundle_sha256"]:
            raise SystemExit(f"STALE CODE DATASET: mounted {CFG['code_ref']} bundle {got[:16]} != expected "
                             f"{CFG['bundle_sha256'][:16]} (run was built for a newer push-code; re-run it)")
        shutil.rmtree(LAB, ignore_errors=True)
        with zipfile.ZipFile(bundle) as zf:
            zf.extractall(LAB)
        log(f"code bundle {got[:16]} extracted to {LAB}")
        # 2. pinned packages (local versions) from our wheels dataset, unpinned deps from the image / support pack
        t = time.time()
        links = []
        for ref in CFG["wheel_datasets"]:
            root = dataset_root(ref)
            links += ["--find-links", str(root / "wheels" if (root / "wheels").is_dir() else root)]
        before = versions()
        need = {d: v for d, v in CFG["pins"].items() if before.get(d) != v}
        if need:
            cmd = [sys.executable, "-m", "pip", "install", "--no-index", "--disable-pip-version-check",
                   "--no-warn-conflicts", "-q", *links, *[f"{d}=={v}" for d, v in sorted(CFG["pins"].items())]]
            log("pip install " + " ".join(f"{d}=={v}" for d, v in sorted(need.items())))
            proc = subprocess.run(cmd, capture_output=True, text=True)
            print(proc.stdout[-4000:], proc.stderr[-4000:], flush=True)
            if proc.returncode != 0:
                raise SystemExit(f"pip install failed (rc {proc.returncode})")
        after = versions()
        run["versions_before"], run["versions"] = before, after
        bad = {d: (after.get(d), v) for d, v in CFG["pins"].items() if after.get(d) != v}
        if bad:
            raise SystemExit(f"pinned versions not installed: {bad}")
        TIMES["install"] = round(time.time() - t, 1)
        log(f"packages pinned to the local versions ({len(CFG['pins'])}) in {TIMES['install']} s")
        # 3. arguments
        resolved = {}
        argv = [resolve(a, resolved) for a in CFG["argv"]]
        run["argv_kaggle"], run["inputs"] = argv, resolved
        for k, v in resolved.items():
            log(f"input {k} -> {v}")
        TIMES["setup"] = round(time.time() - T0, 1)
        # 4. replay
        env = dict(os.environ, BIOHUB_DATA_DIR=str(competition_train()), PYTHONUNBUFFERED="1")
        env.pop("PYTHONPATH", None)
        cmd = [sys.executable, "-u", str(LAB / CFG["replay_rel"]), *argv]
        log("replay: " + " ".join(cmd))
        t = time.time()
        with open(OUT / "replay.log", "w", encoding="utf-8") as fh:
            proc = subprocess.Popen(cmd, cwd=LAB, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, bufsize=1)
            for line in proc.stdout:
                print(line, end="", flush=True)
                fh.write(line)
            rc = proc.wait()
        TIMES["replay"] = round(time.time() - t, 1)
        log(f"replay exit code {rc} after {TIMES['replay']} s")
    except SystemExit as exc:
        run["error"] = str(exc)
        log(f"ERROR: {exc}")
    except Exception as exc:  # noqa: BLE001
        run["error"] = repr(exc)
        log(f"ERROR: {exc!r}")
    finally:
        stop.set()
        if not CFG["keep_tail"]:
            for sub in ("tail", "work", "node_p"):
                shutil.rmtree(OUT / sub, ignore_errors=True)
        TIMES["total"] = round(time.time() - T0, 1)
        total_kb = None
        try:
            total_kb = int(next(l.split()[1] for l in open("/proc/meminfo") if l.startswith("MemTotal:")))
        except Exception:
            pass
        if total_kb and MEM["min_available_kb"] is not None:
            run["peak_mem_used_gb"] = round((total_kb - MEM["min_available_kb"]) / 1048576, 2)
        run.update(rc=rc, seconds=TIMES, finished_utc=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                   outputs=sorted(str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file())[:500])
        (OUT / "lab_run.json").write_text(json.dumps(run, indent=2), encoding="utf-8")
        log(f"lab_run.json written: rc {rc}, seconds {TIMES}, peak mem {run.get('peak_mem_used_gb')} GB")
    if rc != 0 or run.get("error"):
        sys.exit(rc or 1)


main()
'''


def _split_opt(token: str, names: tuple[str, ...]) -> tuple[str | None, str | None]:
    for name in names:
        if token == name:
            return name, None
        if token.startswith(name + "="):
            return name, token[len(name) + 1:]
    return None, None


def _bundle_files() -> dict[str, str]:
    manifest = _load_json(CODE_STAGE / MANIFEST_NAME, {}) or {}
    return manifest.get("files", {})


def classify_path(value: str, maps: list[tuple[str, str]], bundle_files: dict[str, str], embeds: list) -> dict | str:
    """Local path -> kernel arg spec (see module docstring)."""
    if value.startswith("/kaggle/"):
        return value
    local = Path(value)
    local = local if local.is_absolute() else (ROOT / local if (ROOT / local).exists() else Path.cwd() / local)
    for src, dst in maps:
        s = Path(src)
        s = s if s.is_absolute() else ROOT / s
        try:
            rest = local.resolve().relative_to(s.resolve())
        except ValueError:
            continue
        path = dst.rstrip("/") + ("/" + rest.as_posix() if rest.as_posix() != "." else "")
        return {"kind": "kaggle", "path": path, "local": value}
    if not local.exists():
        raise SystemExit(f"path {value!r} does not exist locally (give an existing path, a /kaggle/... path or --map)")
    resolved = local.resolve()
    rel = resolved.relative_to(ROOT).as_posix() if ROOT in resolved.parents else None
    if rel and rel in bundle_files and resolved.is_file():
        if _sha256_file(resolved) != bundle_files[rel]:
            raise SystemExit(f"{rel} changed since push-code; run push-code first")
        return {"kind": "bundle", "rel": rel, "local": value}
    if resolved.is_file() and resolved.stat().st_size <= EMBED_MAX_BYTES and not (rel or "").startswith("data_external/"):
        data = resolved.read_bytes()
        name = f"{len(embeds)}_{resolved.name}"
        embeds.append(name)
        return {"kind": "embed", "name": name, "sha256": _sha256_bytes(data),
                "data": base64.b64encode(zlib.compress(data, 9)).decode("ascii"), "local": value}
    locator = rel if rel else "/".join(resolved.parts[-4:])
    return {"kind": "search", "locator": locator, "dir": resolved.is_dir(), "local": value}


def rewrite_args(replay_args: list[str], maps, workers: int) -> tuple[list, list[str]]:
    bundle_files = _bundle_files()
    embeds: list[str] = []
    out: list = []
    notes: list[str] = []
    i = 0
    while i < len(replay_args):
        tok = replay_args[i]
        name, value = _split_opt(tok, UNSUPPORTED_OPTS)
        if name:
            raise SystemExit(f"{name} is not supported on the Kaggle lab")
        name, value = _split_opt(tok, DROPPED_OPTS)
        if name:
            if value is None:
                i += 1
                value = replay_args[i] if i < len(replay_args) else ""
            notes.append(f"{name} {value} -> forced on Kaggle")
            i += 1
            continue
        name, value = _split_opt(tok, INPUT_PATH_OPTS + OUTPUT_FILE_OPTS)
        if name:
            if value is None:
                i += 1
                if i >= len(replay_args):
                    raise SystemExit(f"{name} needs a value")
                value = replay_args[i]
            if name in OUTPUT_FILE_OPTS:
                out += [name, {"kind": "out", "name": Path(value).name}]
            else:
                if name == "--grid" and "node_p" in Path(value).read_text(encoding="utf-8", errors="replace"):
                    notes.append("WARNING: --grid file mentions node_p; paths inside a grid JSON are NOT rewritten")
                out += [name, classify_path(value, maps, bundle_files, embeds)]
            i += 1
            continue
        name, value = _split_opt(tok, ("--config",))
        if name:
            if value is None:
                i += 1
                value = replay_args[i]
            parts: list = []
            for k, item in enumerate(value.split(",")):
                sep = "," if k else ""
                if item.strip().startswith("node_p="):
                    parts += [sep + item.split("=", 1)[0] + "=",
                              classify_path(item.split("=", 1)[1].strip(), maps, bundle_files, embeds)]
                else:
                    parts.append(sep + item)
            out += ["--config", parts[0] if len(parts) == 1 and isinstance(parts[0], str)
                    else {"kind": "join", "parts": parts}]
            i += 1
            continue
        out.append(tok)
        i += 1
    out += ["--out", {"kind": "out"}, "--data-dir", {"kind": "data"}, "--workers", str(workers)]
    return out, notes


def _slug(name: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,38}[a-z0-9]", name):
        raise SystemExit(f"NAME {name!r}: use 3-40 chars of [a-z0-9-] (it becomes the kernel slug {KERNEL_PREFIX}NAME)")
    return KERNEL_PREFIX + name


def _registry() -> dict:
    return _load_json(REGISTRY, {}) or {}


def _parse_status(text: str) -> str:
    m = re.search(r'status "(?:KernelWorkerStatus\.)?([A-Za-z_]+)"', text)
    return m.group(1).lower() if m else "unknown"


def kernel_status(ref: str) -> tuple[str, str]:
    proc = _kaggle(["kernels", "status", ref], retries=3, check=False, timeout=120)
    text = (proc.stdout + proc.stderr).strip()
    return _parse_status(text), text


def cmd_run(args) -> None:
    slug = _slug(args.name)
    ref = f"{OWNER}/{slug}"
    replay_args = list(args.replay_args)
    if not replay_args:
        raise SystemExit("give the replay arguments after --")
    manifest = _load_json(CODE_STAGE / MANIFEST_NAME)
    pushed = _load_json(CODE_STAGE / "pushed.json")
    if not manifest or not pushed or pushed.get("bundle_sha256") != manifest.get("bundle_sha256"):
        raise SystemExit("no pushed code bundle; run `kaggle_lab.py push-code` first")
    # freshness: same closure, same bytes as the pushed bundle
    files = code_closure()
    changed = sorted(f for f in files if manifest["files"].get(f) != _sha256_file(ROOT / f))
    changed += sorted(set(manifest["files"]) - set(files))
    if changed and not args.stale_ok:
        raise SystemExit(f"local code differs from the pushed bundle ({len(changed)} files, e.g. {changed[:5]}); "
                         "run push-code first (or --stale-ok to run the pushed code anyway)")
    wheels = _load_json(WHEELS_STAGE / WHEELS_MANIFEST_NAME, {}) or {}
    if not wheels.get("pins"):
        raise SystemExit("no wheels manifest; run push-code first")
    maps = []
    for item in args.map:
        src, sep, dst = item.partition("=")
        if not sep or not dst.startswith("/kaggle/"):
            raise SystemExit(f"--map {item!r}: expected LOCAL=/kaggle/input/...")
        maps.append((src, dst))
    argv, notes = rewrite_args(replay_args, maps, args.workers)
    datasets = [CODE_REF, WHEELS_REF, SUPPORT_REF, CACHE_REF, *[d for d in args.dataset if d]]
    datasets = list(dict.fromkeys(datasets))
    cfg = {"name": args.name, "kernel": ref, "pushed_utc": _now(), "competition": COMPETITION,
           "code_ref": CODE_REF, "bundle_name": BUNDLE_NAME, "bundle_sha256": manifest["bundle_sha256"],
           "replay_rel": REPLAY_REL, "pins": wheels["pins"], "wheel_datasets": [WHEELS_REF, SUPPORT_REF],
           "search_datasets": [d for d in datasets if d not in (CODE_REF, WHEELS_REF, SUPPORT_REF)],
           "argv": argv, "argv_local": replay_args, "keep_tail": bool(args.keep_tail)}
    stage = KERNEL_STAGE / args.name
    shutil.rmtree(stage, ignore_errors=True)
    stage.mkdir(parents=True)
    script = KERNEL_TEMPLATE.replace("__CFG_JSON__", repr(json.dumps(cfg)))
    compile(script, "lab_run.py", "exec")
    (stage / "lab_run.py").write_text(script, encoding="utf-8")
    meta = {"id": ref, "title": slug, "code_file": "lab_run.py", "language": "python", "kernel_type": "script",
            "is_private": True, "enable_gpu": False, "enable_tpu": False, "enable_internet": False,
            "dataset_sources": datasets, "competition_sources": [COMPETITION], "kernel_sources": [],
            "model_sources": []}
    _write_json(stage / "kernel-metadata.json", meta)
    for note in notes:
        print(f"  {note}", flush=True)
    shown = [a if isinstance(a, str) else f"<{a['kind']}:{a.get('locator') or a.get('rel') or a.get('name') or a.get('path') or ''}>"
             for a in argv]
    print(f"kernel {ref}\n  datasets {datasets}\n  replay args {' '.join(shown)}", flush=True)
    if args.dry_run:
        print(f"dry run: kernel folder {stage}", flush=True)
        return
    waited = time.time()
    while True:
        proc = _kaggle(["kernels", "push", "-p", "."], cwd=stage, retries=2, check=False, timeout=600)
        text = (proc.stdout + proc.stderr).strip()
        full = "session count" in text.lower()  # "Maximum batch CPU session count of 5 reached." (2026-09-24)
        if not (full and args.wait_slot) or time.time() - waited > args.slot_timeout:
            break
        print(f"  [{_now()}] all Kaggle CPU session slots busy ({text[-80:]}); retry in {args.slot_poll} s", flush=True)
        time.sleep(args.slot_poll)
    print(f"  {text}", flush=True)
    if proc.returncode != 0 or "successfully pushed" not in text.lower():
        hint = " (Kaggle allows 5 concurrent batch CPU sessions; use --wait-slot to queue)" if full else ""
        raise SystemExit(f"kernel push failed: {text}{hint}")
    version = re.search(r"version (\d+)", text)
    reg = _registry()
    reg[args.name] = {"ref": ref, "pushed_utc": cfg["pushed_utc"], "pushed_unix": time.time(),
                      "version": int(version.group(1)) if version else None, "argv_local": replay_args,
                      "datasets": datasets, "bundle_sha256": manifest["bundle_sha256"]}
    _write_json(REGISTRY, reg)
    print(f"pushed {ref} (https://www.kaggle.com/code/{ref}); `kaggle_lab.py pull {args.name}` fetches the result",
          flush=True)


def cmd_pull(args) -> None:
    reg = _registry()
    ref = (reg.get(args.name) or {}).get("ref") or f"{OWNER}/{_slug(args.name)}"
    started = time.time()
    last = None
    while True:
        state, text = kernel_status(ref)
        if state != last:
            print(f"[{_now()}] {ref}: {state}", flush=True)
            last = state
        if state in TERMINAL_STATES:
            break
        if not args.wait:
            print("not finished; pull again later (or without --no-wait)", flush=True)
            return
        if time.time() - started > args.timeout:
            raise SystemExit(f"timeout after {args.timeout} s, state {state}")
        time.sleep(args.poll)
    dest = LAB_HOME / args.name
    shutil.rmtree(dest, ignore_errors=True)  # never mix files of two kernel versions
    dest.mkdir(parents=True, exist_ok=True)
    proc = None
    for attempt in range(8):
        proc = _kaggle(["kernels", "output", ref, "-p", str(dest), "-o"], check=False, timeout=1800)
        text = proc.stdout + proc.stderr
        if proc.returncode == 0 and "error" not in text.lower():
            break
        wait = min(15 * (attempt + 1), 120)
        print(f"  output download attempt {attempt + 1} failed ({text.strip()[-200:]!r}); retry in {wait} s", flush=True)
        time.sleep(wait)
    else:
        raise SystemExit(f"could not download the output of {ref}: {proc.stdout}{proc.stderr}")
    run = _load_json(dest / "out" / "lab_run.json") or _load_json(dest / "lab_run.json") or {}
    if args.name in reg:
        reg[args.name].update(state=state, pulled_utc=_now(), rc=run.get("rc"), seconds=run.get("seconds"),
                              peak_mem_used_gb=run.get("peak_mem_used_gb"))
        _write_json(REGISTRY, reg)
    print(f"{ref}: state {state}; output in {dest}", flush=True)
    if run:
        print(f"  rc {run.get('rc')}  seconds {run.get('seconds')}  peak mem {run.get('peak_mem_used_gb')} GB  "
              f"cpu {run.get('cpu_model')} x{run.get('nproc')}  error {run.get('error')}", flush=True)
    reports = sorted((dest / "out").glob("report_*.md"))
    for rep in reports:
        print(f"\n--- {rep.relative_to(dest)}\n{rep.read_text(encoding='utf-8')}", flush=True)
    if not reports:
        logs = sorted(dest.glob("*.log"))
        if logs:
            try:
                entries = json.loads(logs[0].read_text(encoding="utf-8"))
                tail = "".join(e.get("data", "") for e in entries)[-4000:]
            except ValueError:
                tail = logs[0].read_text(encoding="utf-8", errors="replace")[-4000:]
            print(f"\n--- no report; kernel log tail ({logs[0].name}):\n{tail}", flush=True)
    if state != "complete" or run.get("rc"):
        sys.exit(1)


def cmd_status(args) -> None:
    reg = _registry()
    refs = {name: entry["ref"] for name, entry in reg.items()}
    proc = _kaggle(["kernels", "list", "--mine", "-s", KERNEL_PREFIX, "--page-size", "100", "--csv"], retries=2,
                   check=False, timeout=180)
    for line in (proc.stdout or "").splitlines()[1:]:
        ref = line.split(",", 1)[0].strip()
        if ref.startswith(f"{OWNER}/{KERNEL_PREFIX}") and ref not in refs.values():
            refs[ref.split("/", 1)[1][len(KERNEL_PREFIX):]] = ref
    if not refs:
        print("no lab kernels yet", flush=True)
        return
    counts: dict[str, int] = {}
    rows = []
    for name, ref in sorted(refs.items(), key=lambda kv: (reg.get(kv[0], {}).get("pushed_unix", 0), kv[0])):
        state, _ = kernel_status(ref)
        counts[state] = counts.get(state, 0) + 1
        entry = reg.get(name, {})
        secs = (entry.get("seconds") or {}).get("total")
        rows.append((name, state, entry.get("pushed_utc", "-"), f"{secs:.0f}" if secs else "-",
                     "yes" if entry.get("pulled_utc") else "no",
                     " ".join(entry.get("argv_local", []))[:90]))
    width = max(len(r[0]) for r in rows)
    print(f"{'name':<{width}}  {'state':<10}  {'pushed':<23}  {'sec':>6}  pulled  replay args", flush=True)
    for r in rows:
        print(f"{r[0]:<{width}}  {r[1]:<10}  {r[2]:<23}  {r[3]:>6}  {r[4]:<6}  {r[5]}", flush=True)
    print("states: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("push-code", help="bundle the lab code into the private dataset " + CODE_REF)
    p.add_argument("--force", action="store_true", help="upload even if the served bundle is identical")
    p.add_argument("--force-wheels", action="store_true", help="rebuild and upload " + WHEELS_REF)
    p.add_argument("--skip-verify", action="store_true", help="skip the local import check of the bundle")
    p.add_argument("-m", "--message", default="")
    p.set_defaults(func=cmd_push_code)
    p = sub.add_parser("run", help="push a private CPU kernel running replay.py; replay args after --")
    p.add_argument("name")
    p.add_argument("--dataset", action="append", default=[], help="extra dataset OWNER/SLUG to attach (repeatable)")
    p.add_argument("--map", action="append", default=[], metavar="LOCAL=/kaggle/input/...",
                   help="explicit path mapping for an input (repeatable)")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--keep-tail", action="store_true", help="keep out/tail, out/work, out/node_p in the output")
    p.add_argument("--stale-ok", action="store_true", help="run even if local code differs from the pushed bundle")
    p.add_argument("--dry-run", action="store_true", help="build the kernel folder but do not push")
    p.add_argument("--wait-slot", action="store_true",
                   help="if all 5 Kaggle batch CPU sessions are busy, retry until a slot frees up")
    p.add_argument("--slot-poll", type=int, default=60)
    p.add_argument("--slot-timeout", type=int, default=6 * 3600)
    p.set_defaults(func=cmd_run)  # replay args: everything after the first standalone "--" (split in main)
    p = sub.add_parser("pull", help="wait for a lab kernel and download its output")
    p.add_argument("name")
    p.add_argument("--no-wait", dest="wait", action="store_false")
    p.add_argument("--poll", type=int, default=30)
    p.add_argument("--timeout", type=int, default=12 * 3600)
    p.set_defaults(func=cmd_pull)
    p = sub.add_parser("status", help="list lab kernels and their states")
    p.set_defaults(func=cmd_status)
    argv = sys.argv[1:]
    replay_args: list[str] = []
    if "--" in argv:  # lab options before, replay.py options after (argparse REMAINDER would swallow lab options)
        cut = argv.index("--")
        argv, replay_args = argv[:cut], argv[cut + 1:]
    args = ap.parse_args(argv)
    if replay_args and args.cmd != "run":
        ap.error("arguments after -- are only accepted by `run`")
    args.replay_args = replay_args
    args.func(args)


if __name__ == "__main__":
    main()
