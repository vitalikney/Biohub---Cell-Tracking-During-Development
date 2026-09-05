# --- Setup header: constants expected by the dependency/repo helpers (from baseline cell 8) ---
from __future__ import annotations
import csv, importlib.util, json, math, os, shutil, subprocess, tempfile, zipfile, sys, time
from pathlib import Path

COMPETITION = "biohub-cell-tracking-during-development"
COMP_DIR_CANDIDATES = [Path(f"/kaggle/input/competitions/{COMPETITION}"), Path(f"/kaggle/input/{COMPETITION}")]
COMP_DIR = next((p for p in COMP_DIR_CANDIDATES if p.exists()), COMP_DIR_CANDIDATES[0])
TRAIN_DIR = COMP_DIR / "train"
TEST_DIR = COMP_DIR / "test"
WORKING_DIR = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path(".")
REPO_DIR = WORKING_DIR / "tracking_repo"
METHOD = "unet_transformer"
WEIGHTS_RELATIVE = f"weights/{METHOD}/split_0/edge_predictor_best.pth"
TARGET_ARTIFACT_SLUG = os.environ.get("BIOHUB_TARGET_ARTIFACT_SLUG", "biohub-tracking-support-pack-50ep-v1")
PRIMARY_ARTIFACT_MANIFEST = Path(os.environ.get(
    "BIOHUB_PRIMARY_ARTIFACT_MANIFEST",
    "/kaggle/input/datasets/pilkwang/biohub-tracking-support-pack-50ep-v1/ARTIFACT_MANIFEST.json"))
ALLOW_ARTIFACT_FALLBACK = os.environ.get("BIOHUB_ALLOW_ARTIFACT_FALLBACK", "0") != "0"
