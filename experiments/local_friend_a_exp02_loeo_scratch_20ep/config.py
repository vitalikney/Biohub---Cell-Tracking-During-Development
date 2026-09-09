from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path


EXPERIMENT = "local_friend_a_exp02_loeo_scratch_20ep"
METHOD = "friend_a_exp02_loeo20_scratch_bce_w2"
WEIGHTS_DATASET = "vitaliineibauer/biohub-ft-weights"
WEIGHTS_DATASET_SUBFOLDER = "friend_a_exp02_loeo20"
EXPECTED_BRANCH = "detector-baseline-v2"

EPOCHS = 20
MILESTONE_EPOCHS = (5, 10, 15, 20)
BATCH_SIZE = 4
NUM_WORKERS = 0 if os.name == "nt" else 4
LEARNING_RATE = 1e-4
MIN_LEARNING_RATE = 1e-5
LR_SCHEDULE = "cosine"
SEED = 42
WINDOW_SIZE = 2
DET_LOSS = "bce"
DET_NEG_WEIGHT = 0.01
DET_LOSS_WEIGHT = 1.0
DOWNSAMPLE = "1,4,4"
POOL_KERNEL_UM = 5.0
MAX_DETECTIONS = 1024
CHECKPOINT_EVERY = 5
DET_THRESHOLD = 0.965
ILP_APPEARANCE = 0.0
ILP_DISAPPEARANCE = 2.0
ILP_DIVISION = 1.2

RUN_PIPELINE = os.environ.get("BIOHUB_STEP1_RUN_PIPELINE", "1") != "0"
AUTO_UPLOAD = os.environ.get("BIOHUB_STEP1_AUTO_UPLOAD", "1") != "0"
AUTO_GIT = os.environ.get("BIOHUB_STEP1_AUTO_GIT", "1") != "0"
RUN_ID = os.environ.get("BIOHUB_STEP1_RUN_ID", "active").strip() or "active"


def find_project_root(start: Path) -> Path:
    for candidate in [start.resolve(), *start.resolve().parents]:
        for repo_candidate in (candidate, candidate / ".github-push-worktree"):
            if (repo_candidate / "TEAM.md").exists() and (repo_candidate / "tools" / "repo" / "scripts").exists():
                return repo_candidate
    raise FileNotFoundError("Repository root not found. Start Jupyter inside C:\\Projects\\CellTracker.")


PROJECT_ROOT = find_project_root(Path.cwd())
WORKSPACE_ROOT = PROJECT_ROOT.parent if PROJECT_ROOT.name == ".github-push-worktree" else PROJECT_ROOT
GIT = ["git", "-c", f"safe.directory={PROJECT_ROOT.as_posix()}"]
explicit_data = os.environ.get("BIOHUB_DATA_DIR", "").strip()
data_candidates = [
    Path(explicit_data).expanduser() if explicit_data else None,
    WORKSPACE_ROOT / "train",
    PROJECT_ROOT / "biohub-cell-tracking-during-development" / "train",
    PROJECT_ROOT / "train",
]
DATA_DIR = next((path.resolve() for path in data_candidates if path is not None and path.exists()), None)
if DATA_DIR is None:
    checked = "\n".join(str(path) for path in data_candidates if path is not None)
    raise FileNotFoundError(f"Training data not found. Set BIOHUB_DATA_DIR. Checked:\n{checked}")

default_output_root = WORKSPACE_ROOT / "outputs"
OUTPUT_ROOT = Path(os.environ.get("BIOHUB_OUTPUT_DIR", default_output_root)).expanduser().resolve()
RUN_DIR = OUTPUT_ROOT / EXPERIMENT / RUN_ID
TRAIN_REPO = RUN_DIR / "train_repo"
TRAIN_OUTPUT = TRAIN_REPO / "weights" / METHOD / "split_0"
TRAIN_STATE = TRAIN_OUTPUT / "training_state_latest.pt"
ARTIFACT_DIR = RUN_DIR / "artifact"
PREDICTIONS_ROOT = RUN_DIR / "predictions"
EVALUATION_ROOT = RUN_DIR / "evaluation"
REFERENCE_ROOT = OUTPUT_ROOT / "_reference_weights"
PIPELINE_STATE_PATH = RUN_DIR / "pipeline_state.json"
RUN_CONFIG_PATH = RUN_DIR / "run_config.json"
EXPERIMENT_DIR = PROJECT_ROOT / "experiments" / EXPERIMENT
SPLIT_SOURCE = PROJECT_ROOT / "experiments" / "_lib" / "loeo_train6bba_val44b6.json"
TRAIN_PATCH_SOURCE = PROJECT_ROOT / "experiments" / "_lib" / "train_patches.py"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def load_pipeline_state() -> dict:
    if not PIPELINE_STATE_PATH.exists():
        return {"experiment": EXPERIMENT, "run_id": RUN_ID, "status": "new", "evaluations": {}}
    return json.loads(PIPELINE_STATE_PATH.read_text(encoding="utf-8"))


def save_pipeline_state(**updates) -> dict:
    state = load_pipeline_state()
    state.update(updates)
    state["updated_at"] = datetime.now().astimezone().isoformat()
    atomic_write_text(PIPELINE_STATE_PATH, json.dumps(state, ensure_ascii=False, indent=2))
    return state


def terminate_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=30)


def print_subprocess_line(line: str) -> None:
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    print(line.encode(encoding, errors="replace").decode(encoding, errors="replace"), end="", flush=True)


def run_streamed(command: list[str], *, cwd: Path, env: dict, log_path: Path, label: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"\n[{label}] {subprocess.list2cmdline(command)}", flush=True)
    with log_path.open("a", encoding="utf-8") as log_handle:
        log_handle.write(f"\n===== {datetime.now().astimezone().isoformat()} | {label} =====\n")
        log_handle.flush()
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        try:
            assert process.stdout is not None
            for line in process.stdout:
                log_handle.write(line)
                log_handle.flush()
                print_subprocess_line(line)
            return_code = process.wait()
        except KeyboardInterrupt:
            terminate_process(process)
            save_pipeline_state(status=f"interrupted_during_{label}")
            print("\nStopped safely. Run all cells again to continue from the last completed unit.", flush=True)
            raise
        except BaseException:
            terminate_process(process)
            save_pipeline_state(status=f"notebook_error_during_{label}")
            raise
    if return_code != 0:
        save_pipeline_state(status=f"failed_during_{label}", return_code=return_code, failed_log=str(log_path))
        raise RuntimeError(f"{label} failed with exit code {return_code}; see {log_path}")


def run_checked(command: list[str], *, cwd: Path, env: dict | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {subprocess.list2cmdline(command)}\n"
            + (result.stdout + result.stderr)[-6000:]
        )
    return result.stdout


print(f"project: {PROJECT_ROOT}")
print(f"data:    {DATA_DIR}")
print(f"run:     {RUN_DIR}")
print(
    f"STEP 1: scratch 6bba->44b6 | epochs={EPOCHS} batch={BATCH_SIZE} workers={NUM_WORKERS} "
    f"lr={LEARNING_RATE:g}->{MIN_LEARNING_RATE:g} ({LR_SCHEDULE}) checkpoints={MILESTONE_EPOCHS}"
)
