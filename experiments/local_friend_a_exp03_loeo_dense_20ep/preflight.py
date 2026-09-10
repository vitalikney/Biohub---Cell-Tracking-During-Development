# Validate the fixed split, prepare a patched working copy, and define reusable helpers.

required_modules = [
    "torch", "tracksdata", "geff", "polars", "rustworkx", "zarr", "tqdm",
    "scipy", "skimage", "dask", "networkx", "pandas", "pyscipopt", "ilpy", "blosc2", "kaggle",
]
missing_modules = [name for name in required_modules if importlib.util.find_spec(name) is None]
if missing_modules:
    raise ImportError("Missing pipeline packages: " + ", ".join(missing_modules))

import torch

if sys.version_info[:2] != (3, 12):
    raise RuntimeError(f"Python 3.12 is required; current interpreter: {sys.version.split()[0]}")
if not DATA_DIR.is_dir():
    raise FileNotFoundError(f"Training directory is missing: {DATA_DIR}")

manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
train_ids = list(manifest["train"])
holdout_ids = list(manifest["holdout"])
if len(train_ids) != 126 or len(holdout_ids) != 12:
    raise RuntimeError(f"Unexpected LOEO manifest size: {len(train_ids)} train, {len(holdout_ids)} holdout")
if set(train_ids) & set(holdout_ids):
    raise RuntimeError("Leakage: train and holdout IDs overlap")
if any(not value.startswith("6bba_") for value in train_ids):
    raise RuntimeError("Leakage: STEP 4 train side must contain only 6bba")
if any(not value.startswith("44b6_") for value in holdout_ids):
    raise RuntimeError("Leakage: STEP 4 holdout must contain only 44b6")

all_ids = sorted(path.stem for path in DATA_DIR.glob("*.geff"))
if len(all_ids) != 199 or len(set(all_ids)) != 199:
    raise RuntimeError(f"Expected 199 source GEFF datasets, found {len(all_ids)}")
missing_pairs = [
    str(DATA_DIR / f"{dataset_id}{suffix}")
    for dataset_id in all_ids
    for suffix in (".geff", ".zarr")
    if not (DATA_DIR / f"{dataset_id}{suffix}").exists()
]
if missing_pairs:
    raise FileNotFoundError("Source data are incomplete:\n" + "\n".join(missing_pairs[:20]))

RUN_DIR.mkdir(parents=True, exist_ok=True)
PREDICTIONS_ROOT.mkdir(parents=True, exist_ok=True)
EVALUATION_ROOT.mkdir(parents=True, exist_ok=True)
EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
atomic_write_text(TRAIN_SPLIT_PATH, json.dumps([{"split": 0, "train": train_ids, "test": holdout_ids}], indent=2))
atomic_write_text(EVAL_SPLIT_PATH, json.dumps([{"split": 0, "train": [], "test": holdout_ids}], indent=2))
atomic_write_text(ALL_MANIFEST_PATH, json.dumps({"all": all_ids}, indent=2))

branch = checked([*GIT, "branch", "--show-current"], cwd=PROJECT_ROOT).strip()
if AUTO_GIT and branch != EXPECTED_BRANCH:
    raise RuntimeError(f"Auto-publish needs branch {EXPECTED_BRANCH!r}; current branch is {branch!r}")

if RUN_PIPELINE:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable. Select the project Python 3.12 kernel and restart Jupyter.")
    cuda_probe = torch.zeros(1, device="cuda")
    del cuda_probe
    torch.cuda.empty_cache()
    cuda_device = torch.cuda.get_device_name(0)
    print(f"CUDA OK: torch={torch.__version__}, runtime={torch.version.cuda}, device={cuda_device}")
else:
    cuda_device = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "dry-run (CUDA not required)"


def prepare_repo_copy() -> None:
    marker = REPO_DIR / ".friend_a_dense_pipeline_patch_v1"
    if marker.is_file():
        return
    if REPO_DIR.exists():
        guarded_remove_tree(REPO_DIR, RUN_DIR)
    REPO_DIR.mkdir(parents=True)
    for subdir in ("scripts", "src"):
        shutil.copytree(PROJECT_ROOT / "tools" / "repo" / subdir, REPO_DIR / subdir)
    train_patch = import_file("friend_a_dense_train_patches", TRAIN_PATCH_PATH)
    predict_patch = import_file("friend_a_dense_predict_patches", PREDICT_PATCH_PATH)
    resume_patch = import_file("friend_a_dense_resume_patch", RESUME_PATCH_PATH)
    train_script = REPO_DIR / "scripts" / "train_unet_transformer.py"
    predict_script = REPO_DIR / "scripts" / "predict_unet_transformer.py"
    train_patch.apply_train_patches(train_script)
    resume_patch.apply_full_state_resume_patch(train_script)
    predict_patch.apply_predict_patches(predict_script)
    compile(train_script.read_text(encoding="utf-8"), str(train_script), "exec")
    compile(predict_script.read_text(encoding="utf-8"), str(predict_script), "exec")
    help_env = common_env(DATA_DIR)
    help_text = checked([sys.executable, str(train_script), "--help"], cwd=REPO_DIR, env=help_env)
    for flag in (
        "--resume-state", "--amp", "--no-grad-ckpt", "--seed", "--max-detections",
        "--lr-schedule", "--min-lr", "--checkpoint-every",
    ):
        if flag not in help_text:
            raise RuntimeError(f"Patched trainer is missing {flag}")
    atomic_write_text(marker, "friend_a_dense_pipeline_patch_v1\n")


def kaggle_files(dataset: str = WEIGHTS_DATASET) -> str:
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    return checked(
        [sys.executable, "-m", "kaggle", "datasets", "files", dataset, "--page-size", "1000"],
        cwd=PROJECT_ROOT,
        env=env,
    )


def copy_model_pair(source_dir: Path, target_dir: Path, expected_sha256: str) -> Path:
    source_weights = source_dir / "edge_predictor_best.pth"
    source_config = source_dir / "config.json"
    if not source_weights.is_file() or not source_config.is_file():
        raise FileNotFoundError(f"Incomplete checkpoint pair in {source_dir}")
    actual = sha256_file(source_weights).lower()
    if actual != expected_sha256.lower():
        raise RuntimeError(f"Checkpoint hash mismatch in {source_dir}: {actual}")
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_weights, target_dir / source_weights.name)
    shutil.copy2(source_config, target_dir / source_config.name)
    return target_dir / source_weights.name


def download_model_file(dataset: str, remote: str, destination: Path) -> None:
    download_dir = destination.parent / "download"
    download_dir.mkdir(parents=True, exist_ok=True)
    output = checked(
        [sys.executable, "-m", "kaggle", "datasets", "download", dataset, "-f", remote,
         "-p", str(download_dir), "--unzip", "-o"],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
    )
    if output.strip():
        print(output.strip())
    matches = [path for path in download_dir.rglob(Path(remote).name) if path.is_file()]
    if not matches:
        raise FileNotFoundError(f"Kaggle download did not produce {remote}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[0], destination)


def ensure_teacher_models() -> tuple[Path, Path]:
    if not (PRIMARY_WEIGHTS.is_file() and PRIMARY_WEIGHTS.with_name("config.json").is_file()):
        local_primary = [
            OUTPUT_ROOT / "kaggle_weights_upload_20260907_2215" / "exp03B",
            OUTPUT_ROOT / "_reference_weights" / "exp03B",
        ]
        source = next((path for path in local_primary if (path / "edge_predictor_best.pth").is_file()), None)
        if source is not None:
            copy_model_pair(source, PRIMARY_WEIGHTS_DIR, PRIMARY_EXPECTED_SHA256)
        else:
            for name in ("edge_predictor_best.pth", "config.json"):
                download_model_file(WEIGHTS_DATASET, f"{PRIMARY_DATASET_FOLDER}/{name}", PRIMARY_WEIGHTS_DIR / name)
    if not (SECONDARY_WEIGHTS.is_file() and SECONDARY_WEIGHTS.with_name("config.json").is_file()):
        local_secondary = OUTPUT_ROOT / "_reference_weights" / "reference_pilkwang_secondary_seed314159"
        if (local_secondary / "edge_predictor_best.pth").is_file():
            copy_model_pair(local_secondary, SECONDARY_WEIGHTS_DIR, SECONDARY_EXPECTED_SHA256)
        else:
            for name in ("edge_predictor_best.pth", "config.json"):
                download_model_file(SECONDARY_DATASET, f"{SECONDARY_REMOTE_FOLDER}/{name}", SECONDARY_WEIGHTS_DIR / name)
    for path, expected in ((PRIMARY_WEIGHTS, PRIMARY_EXPECTED_SHA256), (SECONDARY_WEIGHTS, SECONDARY_EXPECTED_SHA256)):
        if sha256_file(path).lower() != expected.lower():
            raise RuntimeError(f"Teacher model hash mismatch: {path}")
    return PRIMARY_WEIGHTS, SECONDARY_WEIGHTS


prepare_repo_copy()
run_config = {
    "experiment": EXPERIMENT,
    "branch": branch,
    "project_root": str(PROJECT_ROOT),
    "data_dir": str(DATA_DIR),
    "dense_data_dir": str(DENSE_DATA_DIR),
    "python": sys.version,
    "platform": platform.platform(),
    "cuda_device": cuda_device,
    "manifest_sha256": sha256_file(MANIFEST_PATH),
    "train_videos": train_ids,
    "holdout_videos": holdout_ids,
    "all_videos": all_ids,
    "step4_epochs": STEP4_EPOCHS,
    "team_step4_epochs": 30,
    "epoch_override": "explicit user request on 2026-09-10",
    "batch_size": BATCH_SIZE,
    "lr": LEARNING_RATE,
    "lr_schedule": "cosine",
    "min_lr": MIN_LEARNING_RATE,
    "seed": SEED,
    "window_size": WINDOW_SIZE,
    "downsample": [1, 4, 4],
    "step4_max_detections": 0,
    "checkpoint_every": CHECKPOINT_EVERY,
    "leaderboard_submission": False,
}
fingerprint = hashlib.sha256(json.dumps(run_config, sort_keys=True).encode()).hexdigest()
run_config["fingerprint"] = fingerprint
run_config_path = RUN_DIR / "run_config.json"
if run_config_path.is_file():
    previous = json.loads(run_config_path.read_text(encoding="utf-8"))
    if previous.get("fingerprint") != fingerprint:
        raise RuntimeError("The active run has a different recipe. Set BIOHUB_DENSE_RUN_ID to a new value.")
else:
    atomic_write_text(run_config_path, json.dumps(run_config, ensure_ascii=False, indent=2))
save_state(status="prepared", config_fingerprint=fingerprint)
print(f"Preflight OK: 126 train 6bba | 12 holdout 44b6 | {len(all_ids)} total")
if not RUN_PIPELINE:
    print("Dry preflight only: BIOHUB_DENSE_RUN_PIPELINE=0, no teacher/training/upload was started.")
