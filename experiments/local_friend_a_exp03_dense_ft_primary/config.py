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
from datetime import datetime
from pathlib import Path


EXPERIMENT = "local_friend_a_exp03_dense_ft_primary"
LEGACY_STEP1C_EXPERIMENT = "local_friend_a_exp03_loeo_dense_20ep"
EXPECTED_BRANCH = "detector-baseline-v2"
WEIGHTS_DATASET = "vitaliineibauer/biohub-ft-weights"
TEACHER_DATASET_FOLDER = "teacher_geff"
DENSE_DATASET_FOLDER = "train_dense_geff"
WINNER_WEIGHTS_FOLDER = "friend_a_ft_dense_primary"

BATCH_SIZE = 4
NUM_WORKERS = 0 if os.name == "nt" else 4
FT_EPOCHS = 1
FT_LEARNING_RATE = 5e-5
SEED = 42
WINDOW_SIZE = 2
DOWNSAMPLE = "1,4,4"
POOL_KERNEL_UM = 5.0
DET_LOSS_WEIGHT = 1.0
MAX_DETECTIONS = 0
DET_THRESHOLD = 0.965
ILP_APPEARANCE = 0.0
ILP_DISAPPEARANCE = 2.0
ILP_DIVISION = 1.2
TEACHER_CHUNK_SIZE = 6
TEACHER_DEDUP_RADIUS_UM = 5.0
WINNING_DELTA = 0.005

VARIANTS = [
    {"name": "sparse_1200", "data": "sparse", "max_iters": 1200, "det_neg_weight": 0.01, "aug_intensity": False},
    {"name": "dense_1200", "data": "dense", "max_iters": 1200, "det_neg_weight": 0.01, "aug_intensity": False},
    {"name": "dense_2400", "data": "dense", "max_iters": 2400, "det_neg_weight": 0.01, "aug_intensity": False},
    {"name": "dense_1200_neg0p1", "data": "dense", "max_iters": 1200, "det_neg_weight": 0.1, "aug_intensity": False},
    {"name": "dense_1200_aug", "data": "dense", "max_iters": 1200, "det_neg_weight": 0.01, "aug_intensity": True},
]

RUN_PIPELINE = os.environ.get("BIOHUB_DENSE_FT_RUN_PIPELINE", "1") != "0"
AUTO_UPLOAD = os.environ.get("BIOHUB_DENSE_FT_AUTO_UPLOAD", "1") != "0"
AUTO_GIT = os.environ.get("BIOHUB_DENSE_FT_AUTO_GIT", "1") != "0"
RUN_STEP3 = os.environ.get("BIOHUB_DENSE_FT_RUN_STEP3", "1") != "0"
RUN_ID = os.environ.get("BIOHUB_DENSE_FT_RUN_ID", "active").strip() or "active"


def find_project_root(start: Path) -> Path:
    for candidate in [start.resolve(), *start.resolve().parents]:
        for repo_candidate in (candidate, candidate / ".github-push-worktree"):
            if (repo_candidate / "TEAM.md").exists() and (repo_candidate / "tools" / "repo" / "scripts").exists():
                return repo_candidate
    raise FileNotFoundError("Repository root not found. Start Jupyter inside C:\\Projects\\CellTracker.")


PROJECT_ROOT = find_project_root(Path.cwd())
WORKSPACE_ROOT = PROJECT_ROOT.parent if PROJECT_ROOT.name == ".github-push-worktree" else PROJECT_ROOT
GIT = ["git", "-c", f"safe.directory={PROJECT_ROOT.as_posix()}"]
DATA_DIR = Path(os.environ.get("BIOHUB_DATA_DIR", WORKSPACE_ROOT / "train")).expanduser().resolve()
DENSE_DATA_DIR = Path(os.environ.get("BIOHUB_DENSE_DATA_DIR", WORKSPACE_ROOT / "train_dense")).expanduser().resolve()
OUTPUT_ROOT = Path(os.environ.get("BIOHUB_OUTPUT_DIR", WORKSPACE_ROOT / "outputs")).expanduser().resolve()
RUN_DIR = OUTPUT_ROOT / EXPERIMENT / RUN_ID
LEGACY_STEP1C_RUN_DIR = OUTPUT_ROOT / LEGACY_STEP1C_EXPERIMENT / "active"
PIPELINE_STATE_PATH = RUN_DIR / "pipeline_state.json"
REPO_DIR = RUN_DIR / "repo"
PREDICTIONS_ROOT = RUN_DIR / "predictions"
EVALUATION_ROOT = RUN_DIR / "evaluation"
TEACHER_DIR = (
    LEGACY_STEP1C_RUN_DIR / TEACHER_DATASET_FOLDER
    if (LEGACY_STEP1C_RUN_DIR / TEACHER_DATASET_FOLDER).exists()
    else RUN_DIR / TEACHER_DATASET_FOLDER
)
MANIFEST_PATH = PROJECT_ROOT / "experiments" / "_lib" / "loeo_train6bba_val44b6.json"
EXP03_CONFIG_PATH = PROJECT_ROOT / "experiments" / "exp03_finetune_ab" / "config.py"
TRAIN_PATCH_PATH = PROJECT_ROOT / "experiments" / "_lib" / "train_patches.py"
PREDICT_PATCH_PATH = PROJECT_ROOT / "experiments" / "_lib" / "predict_patches.py"
BUILDER_PATH = PROJECT_ROOT / "tools" / "build_dense_gt.py"
EXPERIMENT_DIR = PROJECT_ROOT / "experiments" / EXPERIMENT
REFERENCE_ROOT = OUTPUT_ROOT / "_dense_ft_reference_weights"
PRIMARY_WEIGHTS_DIR = REFERENCE_ROOT / "pilkwang_primary"
PRIMARY_WEIGHTS = PRIMARY_WEIGHTS_DIR / "edge_predictor_best.pth"
PRIMARY_EXPECTED_SHA256 = "12f6881ee3620a831697ca098ff8f48e687a24225f4e048b538deec3562fe771"
PRIMARY_DATASET = "pilkwang/biohub-tracking-support-pack-50ep-v1"
PRIMARY_REMOTE_FOLDER = "weights/unet_transformer/split_0"
TEACHER_PRIMARY_DIR = REFERENCE_ROOT / "teacher_exp03B"
TEACHER_PRIMARY_WEIGHTS = TEACHER_PRIMARY_DIR / "edge_predictor_best.pth"
TEACHER_PRIMARY_EXPECTED_SHA256 = "f3bb1932efe8fbb6893f7707eebb0355814d53f86081e0d8c48d90140e98b305"
TEACHER_SECONDARY_DIR = REFERENCE_ROOT / "teacher_seed314159"
TEACHER_SECONDARY_WEIGHTS = TEACHER_SECONDARY_DIR / "edge_predictor_best.pth"
TEACHER_SECONDARY_EXPECTED_SHA256 = "9bac2fa0dadc4a6fc1899e0caf187f4b553e0a7cd90ba1261a68b35ffe9e305f"
SECONDARY_DATASET = "pilkwang/biohub-temporal-unet3d-seed314159-v1"
SECONDARY_REMOTE_FOLDER = "weights/unet_transformer/split_0"
ALL_MANIFEST_PATH = RUN_DIR / "all199.json"
LOEO_TRAIN_SPLIT_PATH = RUN_DIR / "loeo_train.json"
LOEO_EVAL_SPLIT_PATH = RUN_DIR / "loeo_eval.json"
EXP03_TRAIN_SPLIT_PATH = RUN_DIR / "exp03_train.json"
EXP03_EVAL_SPLIT_PATH = RUN_DIR / "exp03_eval.json"


def atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_state() -> dict:
    if not PIPELINE_STATE_PATH.is_file():
        return {"experiment": EXPERIMENT, "run_id": RUN_ID, "status": "new", "variants": {}}
    return json.loads(PIPELINE_STATE_PATH.read_text(encoding="utf-8"))


def save_state(**updates) -> dict:
    state = load_state()
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


def stream_command(command: list[str], *, cwd: Path, env: dict, log_path: Path, label: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"\n[{label}] {subprocess.list2cmdline(command)}", flush=True)
    with log_path.open("a", encoding="utf-8") as log_handle:
        log_handle.write(f"\n===== {datetime.now().astimezone().isoformat()} | {label} =====\n")
        log_handle.flush()
        process = subprocess.Popen(
            command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
        )
        try:
            assert process.stdout is not None
            for line in process.stdout:
                log_handle.write(line)
                log_handle.flush()
                encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
                print(line.encode(encoding, errors="replace").decode(encoding, errors="replace"), end="", flush=True)
            return_code = process.wait()
        except KeyboardInterrupt:
            terminate_process(process)
            save_state(status=f"interrupted_during_{label}")
            print("\nStopped safely. Run All again; completed variants will be skipped.", flush=True)
            raise
        except BaseException:
            terminate_process(process)
            save_state(status=f"notebook_error_during_{label}")
            raise
    if return_code != 0:
        save_state(status=f"failed_during_{label}", failed_log=str(log_path), return_code=return_code)
        raise RuntimeError(f"{label} failed with exit code {return_code}; see {log_path}")


def checked(command: list[str], *, cwd: Path, env: dict | None = None) -> str:
    result = subprocess.run(
        command, cwd=cwd, env=env, text=True, encoding="utf-8", errors="replace", capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {subprocess.list2cmdline(command)}\n"
            + (result.stdout + result.stderr)[-6000:]
        )
    return result.stdout


def import_file(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def common_env(data_dir: Path) -> dict[str, str]:
    env = {
        **os.environ,
        "BIOHUB_DATA_DIR": str(data_dir),
        "BIOHUB_PREDICTIONS_DIR": str(PREDICTIONS_ROOT),
        "PYTHONPATH": str(REPO_DIR / "src"),
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTORCH_ALLOC_CONF": "expandable_segments:True",
    }
    env.pop("BIOHUB_ENSEMBLE_WEIGHTS", None)
    return env


def guarded_remove_tree(path: Path, parent: Path) -> None:
    if not path.resolve().is_relative_to(parent.resolve()):
        raise RuntimeError(f"Refusing to remove path outside {parent}: {path}")
    if path.exists():
        shutil.rmtree(path)


def update_marked_block(path: Path, marker: str, line: str, heading_prefix: str) -> None:
    text_value = path.read_text(encoding="utf-8")
    block = marker + "\n" + line
    pattern = re.compile(re.escape(marker) + r"\n[^\n]*")
    if pattern.search(text_value):
        text_value = pattern.sub(block, text_value, count=1)
    else:
        heading = next((item for item in text_value.splitlines() if item.startswith(heading_prefix)), None)
        if heading is None:
            raise RuntimeError(f"Heading not found in {path}: {heading_prefix}")
        text_value = text_value.replace(heading, heading + "\n" + block, 1)
    atomic_write_text(path, text_value.rstrip() + "\n")


print(f"project:      {PROJECT_ROOT}")
print(f"sparse data:  {DATA_DIR}")
print(f"dense data:   {DENSE_DATA_DIR}")
print(f"teacher data: {TEACHER_DIR}")
print(f"run:          {RUN_DIR}")
