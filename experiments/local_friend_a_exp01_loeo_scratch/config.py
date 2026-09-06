from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


EXPERIMENT = "local_friend_a_exp01_loeo_scratch"
METHOD = "friend_a_scratch_bce_w2"

# Friend A defaults from TEAM.md. Environment variables make the notebook reusable
# for the later controlled variants without editing generated cells.
RUN_TRAINING = os.environ.get("BIOHUB_RUN_TRAINING", "1") != "0"
EPOCHS = int(os.environ.get("BIOHUB_FRIEND_A_EPOCHS", "5"))
BATCH_SIZE = int(os.environ.get("BIOHUB_FRIEND_A_BATCH", "4"))
# Windows spawn makes every worker import the CUDA runtime and can exhaust the pagefile.
# Local timing showed data loading was only ~8% of a batch, so zero workers is the safe default.
default_workers = "0" if os.name == "nt" else "4"
NUM_WORKERS = int(os.environ.get("BIOHUB_FRIEND_A_WORKERS", default_workers))
LEARNING_RATE = float(os.environ.get("BIOHUB_FRIEND_A_LR", "1e-4"))
SEED = int(os.environ.get("BIOHUB_FRIEND_A_SEED", "42"))
WINDOW_SIZE = int(os.environ.get("BIOHUB_FRIEND_A_WINDOW", "2"))
DET_LOSS = os.environ.get("BIOHUB_FRIEND_A_DET_LOSS", "bce")
DET_NEG_WEIGHT = float(os.environ.get("BIOHUB_FRIEND_A_DET_NEG_WEIGHT", "0.01"))
DET_LOSS_WEIGHT = float(os.environ.get("BIOHUB_FRIEND_A_DET_LOSS_WEIGHT", "1.0"))
DOWNSAMPLE = os.environ.get("BIOHUB_FRIEND_A_DOWNSAMPLE", "1,4,4")
POOL_KERNEL_UM = float(os.environ.get("BIOHUB_FRIEND_A_POOL_KERNEL_UM", "5.0"))
AUG_INTENSITY = os.environ.get("BIOHUB_FRIEND_A_AUG_INTENSITY", "0") == "1"
MAX_ITERS_TEXT = os.environ.get("BIOHUB_FRIEND_A_MAX_ITERS", "").strip()
MAX_ITERS = int(MAX_ITERS_TEXT) if MAX_ITERS_TEXT else None

if not 5 <= EPOCHS <= 10:
    raise ValueError("TEAM.md requires 5–10 epochs for the leak-free validator")
if BATCH_SIZE not in (4, 5, 6, 8):
    raise ValueError("Use batch 4–6 without gradient checkpointing, or explicitly choose 8 after enabling it")
if BATCH_SIZE == 8:
    raise ValueError("This notebook disables gradient checkpointing; use batch 4–6 on a 16 GB GPU")
if DET_LOSS not in {"bce", "gauss_focal"}:
    raise ValueError("BIOHUB_FRIEND_A_DET_LOSS must be bce or gauss_focal")


def find_project_root(start: Path) -> Path:
    candidates = [start.resolve(), *start.resolve().parents]
    for candidate in candidates:
        repo_candidates = [candidate, candidate / ".github-push-worktree"]
        for repo_candidate in repo_candidates:
            if (repo_candidate / "TEAM.md").exists() and (repo_candidate / "tools" / "repo" / "scripts").exists():
                return repo_candidate
    raise FileNotFoundError("Repository root not found. Start Jupyter inside the cloned project.")


PROJECT_ROOT = find_project_root(Path.cwd())

explicit_data = os.environ.get("BIOHUB_DATA_DIR", "").strip()
data_candidates = [
    Path(explicit_data).expanduser() if explicit_data else None,
    PROJECT_ROOT / "biohub-cell-tracking-during-development" / "train",
    PROJECT_ROOT / "train",
    PROJECT_ROOT.parent / "train",  # convenient for a worktree next to the local dataset
]
DATA_DIR = next((path.resolve() for path in data_candidates if path is not None and path.exists()), None)
if DATA_DIR is None:
    checked = "\n".join(str(path) for path in data_candidates if path is not None)
    raise FileNotFoundError(
        "Training data were not found. Set BIOHUB_DATA_DIR to the directory containing *.zarr and *.geff.\n"
        f"Checked:\n{checked}"
    )

RUN_ID = os.environ.get("BIOHUB_RUN_ID", datetime.now().strftime("%Y%m%d_%H%M%S"))
default_output_root = (
    PROJECT_ROOT.parent / "outputs" if PROJECT_ROOT.name == ".github-push-worktree" else PROJECT_ROOT / "outputs"
)
OUTPUT_ROOT = Path(os.environ.get("BIOHUB_OUTPUT_DIR", default_output_root)).expanduser().resolve()
RUN_DIR = OUTPUT_ROOT / EXPERIMENT / RUN_ID
TRAIN_REPO = RUN_DIR / "train_repo"
ARTIFACT_DIR = RUN_DIR / "artifact"
SPLIT_SOURCE = PROJECT_ROOT / "experiments" / "_lib" / "loeo_train6bba_val44b6.json"
PATCH_SOURCE = PROJECT_ROOT / "experiments" / "_lib" / "train_patches.py"

print(f"project: {PROJECT_ROOT}")
print(f"data:    {DATA_DIR}")
print(f"run:     {RUN_DIR}")
print(
    f"recipe: scratch | epochs={EPOCHS} batch={BATCH_SIZE} workers={NUM_WORKERS} "
    f"lr={LEARNING_RATE:g} window={WINDOW_SIZE} det_loss={DET_LOSS} seed={SEED}"
)
