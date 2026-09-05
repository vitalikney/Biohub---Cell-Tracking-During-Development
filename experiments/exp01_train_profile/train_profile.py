# --- Profiling run of the training recipe ---
import json, os, subprocess, sys, time, shutil
from pathlib import Path

EPOCHS = int(os.environ.get("BIOHUB_PROF_EPOCHS", "1"))
MAX_ITERS = int(os.environ.get("BIOHUB_PROF_MAX_ITERS", "150"))
BATCH = int(os.environ.get("BIOHUB_PROF_BATCH", "8"))
N_TRAIN = int(os.environ.get("BIOHUB_PROF_N_TRAIN", "20"))
N_VAL = int(os.environ.get("BIOHUB_PROF_N_VAL", "2"))
WINDOW = int(os.environ.get("BIOHUB_PROF_WINDOW", "2"))
DOWNSAMPLE = os.environ.get("BIOHUB_PROF_DOWNSAMPLE", "1,4,4")

# Writable training copy of the repo: REPO_DIR/weights is a symlink into read-only /kaggle/input.
TRAIN_REPO = WORKING_DIR / "train_repo"
shutil.rmtree(TRAIN_REPO, ignore_errors=True)
TRAIN_REPO.mkdir(parents=True)
for sub in ("scripts", "src"):
    shutil.copytree(REPO_DIR / sub, TRAIN_REPO / sub)
(TRAIN_REPO / "weights").mkdir()
shutil.copytree(REPO_DIR / "weights" / METHOD, TRAIN_REPO / "weights" / METHOD)  # pretrained init, if needed
print("train repo:", TRAIN_REPO, sorted(p.name for p in TRAIN_REPO.iterdir()))
apply_train_patches(TRAIN_REPO / "scripts" / "train_unet_transformer.py")

stems = sorted(p.name[:-5] for p in TRAIN_DIR.iterdir() if p.name.endswith(".zarr"))
test_stems = {p.name[:-5] for p in TEST_DIR.iterdir() if p.name.endswith(".zarr")}
stems = [s for s in stems if s not in test_stems]
a = [s for s in stems if s.startswith("44b6")]
b = [s for s in stems if s.startswith("6bba")]
train = a[: N_TRAIN // 2] + b[: N_TRAIN // 2]
val = a[-N_VAL:] + b[-N_VAL:]
splits = [{"split": 0, "train": train, "test": val}]
splits_path = TRAIN_REPO / "prof_splits.json"
splits_path.write_text(json.dumps(splits, indent=1))
print("train", len(train), "val", len(val))

cmd = [sys.executable, "scripts/train_unet_transformer.py",
       "--method", "prof",
       "--data-dir", str(TRAIN_DIR),
       "--splits", str(splits_path),
       "--split", "0",
       "--epochs", str(EPOCHS),
       "--max-iters", str(MAX_ITERS),
       "--batch-size", str(BATCH),
       "--num-workers", "4",
       "--det-loss-weight", "1.0",
       "--det-neg-weight", "0.01",
       "--window-size", str(WINDOW),
       "--downsample", DOWNSAMPLE,
       "--pool-kernel-um", "5.0"]
for flag in os.environ.get("BIOHUB_PROF_EXTRA_FLAGS", "").split():
    cmd.append(flag)
print(" ".join(cmd), flush=True)
env = {**os.environ, "PYTHONPATH": "src", "PYTHONUNBUFFERED": "1"}
t0 = time.time()
log_path = WORKING_DIR / "train_profile.log"
with open(log_path, "w") as log:
    proc = subprocess.Popen(cmd, cwd=TRAIN_REPO, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        print(line, end="", flush=True)
        log.write(line)
    rc = proc.wait()
elapsed = time.time() - t0
print(f"\nexit code {rc}; wall {elapsed/60:.1f} min", flush=True)

# GPU memory snapshot after run
try:
    print(subprocess.run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total", "--format=csv"],
                         capture_output=True, text=True).stdout)
except Exception as e:
    print("nvidia-smi failed", e)

out_w = TRAIN_REPO / "weights" / "prof" / "split_0"
if out_w.exists():
    dst = WORKING_DIR / "prof_weights"
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(out_w, dst)
    print("saved weights:", [p.name for p in dst.iterdir()])

summary = {"extra_flags": os.environ.get("BIOHUB_PROF_EXTRA_FLAGS", ""), "epochs": EPOCHS, "max_iters": MAX_ITERS, "batch": BATCH, "n_train": len(train), "n_val": len(val),
           "window": WINDOW, "downsample": DOWNSAMPLE, "wall_min": elapsed / 60, "exit_code": rc}
(WORKING_DIR / "profile_summary.json").write_text(json.dumps(summary, indent=1))
print(summary)
if rc != 0:
    raise SystemExit(rc)
