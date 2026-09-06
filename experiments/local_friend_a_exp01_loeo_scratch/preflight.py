# Preflight, immutable split conversion, and a writable copy of the training code.

required_modules = ["torch", "tracksdata", "geff", "polars", "rustworkx", "zarr", "tqdm"]
evaluation_modules = ["scipy", "skimage", "dask", "networkx", "pandas", "sklearn", "pyscipopt", "ilpy", "blosc2"]
missing_modules = [name for name in required_modules if importlib.util.find_spec(name) is None]
if missing_modules:
    raise ImportError(
        "Missing packages: " + ", ".join(missing_modules) + "\n"
        "Install the dependencies listed in TEAM.md into the selected Python 3.12 environment."
    )
missing_evaluation_modules = [name for name in evaluation_modules if importlib.util.find_spec(name) is None]
if missing_evaluation_modules:
    print(
        "Warning: optional inference/evaluation packages are missing: "
        + ", ".join(missing_evaluation_modules)
        + ". They do not block training, but TEAM.md requires them before official evaluation."
    )

import torch

if sys.version_info[:2] != (3, 12):
    raise RuntimeError(f"Python 3.12 is required by TEAM.md; current interpreter: {sys.version.split()[0]}")
if not torch.cuda.is_available():
    raise RuntimeError("CUDA is unavailable. Install a CUDA 12.8+ PyTorch build and restart the notebook kernel.")

# A real allocation catches driver/build mismatches that nvidia-smi alone cannot detect.
probe = torch.zeros(1, device="cuda")
del probe
torch.cuda.empty_cache()
device_name = torch.cuda.get_device_name(0)
device_capability = torch.cuda.get_device_capability(0)
print(
    f"CUDA OK: torch={torch.__version__}, runtime={torch.version.cuda}, "
    f"device={device_name}, capability={device_capability}"
)

split_manifest = json.loads(SPLIT_SOURCE.read_text(encoding="utf-8"))
train_ids = list(split_manifest["train"])
holdout_ids = list(split_manifest["holdout"])

if len(train_ids) != 126 or len(holdout_ids) != 12:
    raise RuntimeError(f"Unexpected LOEO manifest size: train={len(train_ids)}, holdout={len(holdout_ids)}")
if len(train_ids) != len(set(train_ids)) or len(holdout_ids) != len(set(holdout_ids)):
    raise RuntimeError("Duplicate dataset IDs in the LOEO manifest")
if set(train_ids) & set(holdout_ids):
    raise RuntimeError("Leakage: train and holdout IDs overlap")
if any(not dataset_id.startswith("6bba_") for dataset_id in train_ids):
    raise RuntimeError("Leakage: every training ID must belong to embryo 6bba")
if any(not dataset_id.startswith("44b6_") for dataset_id in holdout_ids):
    raise RuntimeError("Leakage: every holdout ID must belong to embryo 44b6")

missing_data = []
for dataset_id in train_ids + holdout_ids:
    for suffix in (".zarr", ".geff"):
        expected = DATA_DIR / f"{dataset_id}{suffix}"
        if not expected.exists():
            missing_data.append(str(expected))
if missing_data:
    preview = "\n".join(missing_data[:20])
    raise FileNotFoundError(f"Missing {len(missing_data)} dataset paths. First entries:\n{preview}")

all_6bba = {path.name.removesuffix(".zarr") for path in DATA_DIR.glob("6bba_*.zarr")}
excluded_6bba = sorted(all_6bba - set(train_ids))
print(f"LOEO split OK: {len(train_ids)} train 6bba | {len(holdout_ids)} validation 44b6")
if excluded_6bba:
    print("6bba videos outside the fixed manifest:", excluded_6bba)

RUN_DIR.mkdir(parents=True, exist_ok=False)
TRAIN_REPO.mkdir(parents=True)
for subdir in ("scripts", "src"):
    shutil.copytree(PROJECT_ROOT / "tools" / "repo" / subdir, TRAIN_REPO / subdir)

patch_spec = importlib.util.spec_from_file_location("friend_a_train_patches", PATCH_SOURCE)
if patch_spec is None or patch_spec.loader is None:
    raise RuntimeError(f"Cannot import training patches from {PATCH_SOURCE}")
patch_module = importlib.util.module_from_spec(patch_spec)
patch_spec.loader.exec_module(patch_module)
TRAIN_SCRIPT = TRAIN_REPO / "scripts" / "train_unet_transformer.py"
patch_module.apply_train_patches(TRAIN_SCRIPT)
trainer_source = TRAIN_SCRIPT.read_text(encoding="utf-8")
legacy_models_import = "from biohub_tracking.models import SimpleNodeTransformer, TemporalUNet3D"
if legacy_models_import in trainer_source:
    trainer_source = trainer_source.replace(
        legacy_models_import,
        "from biohub_tracking.models.simple_node_transformer import SimpleNodeTransformer\n"
        "from biohub_tracking.models.temporal_unet import TemporalUNet3D",
        1,
    )
    TRAIN_SCRIPT.write_text(trainer_source, encoding="utf-8")
    print("patched local namespace-package model imports")
compile(TRAIN_SCRIPT.read_text(encoding="utf-8"), str(TRAIN_SCRIPT), "exec")

help_env = {
    **os.environ,
    "PYTHONPATH": str(TRAIN_REPO / "src"),
    "BIOHUB_DATA_DIR": str(DATA_DIR),
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
}
help_check = subprocess.run(
    [sys.executable, str(TRAIN_SCRIPT), "--help"],
    cwd=TRAIN_REPO,
    env=help_env,
    text=True,
    encoding="utf-8",
    errors="replace",
    capture_output=True,
)
if help_check.returncode != 0:
    raise RuntimeError("Patched trainer import/CLI check failed:\n" + (help_check.stdout + help_check.stderr)[-4000:])
for required_flag in ("--amp", "--no-grad-ckpt", "--seed", "--det-loss"):
    if required_flag not in help_check.stdout:
        raise RuntimeError(f"Patched trainer is missing required flag: {required_flag}")

split_for_trainer = [{"split": 0, "train": train_ids, "test": holdout_ids}]
TRAIN_SPLIT = RUN_DIR / "loeo_train6bba_val44b6_for_trainer.json"
TRAIN_SPLIT.write_text(json.dumps(split_for_trainer, ensure_ascii=False, indent=2), encoding="utf-8")

TRAIN_CMD = [
    sys.executable,
    str(TRAIN_SCRIPT),
    "--method", METHOD,
    "--data-dir", str(DATA_DIR),
    "--splits", str(TRAIN_SPLIT),
    "--split", "0",
    "--epochs", str(EPOCHS),
    "--batch-size", str(BATCH_SIZE),
    "--num-workers", str(NUM_WORKERS),
    "--lr", str(LEARNING_RATE),
    "--det-loss-weight", str(DET_LOSS_WEIGHT),
    "--det-neg-weight", str(DET_NEG_WEIGHT),
    "--window-size", str(WINDOW_SIZE),
    "--downsample", DOWNSAMPLE,
    "--pool-kernel-um", str(POOL_KERNEL_UM),
    "--det-loss", DET_LOSS,
    "--seed", str(SEED),
    "--amp",
    "--no-grad-ckpt",
    "--single-gpu",
]
if MAX_ITERS is not None:
    TRAIN_CMD.extend(["--max-iters", str(MAX_ITERS)])
if AUG_INTENSITY:
    TRAIN_CMD.append("--aug-intensity")

for forbidden_flag in ("--init-weights", "--unet-weights"):
    if forbidden_flag in TRAIN_CMD:
        raise RuntimeError(f"Leakage guard: forbidden scratch-training flag found: {forbidden_flag}")

try:
    git_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()
except Exception:
    git_commit = None

RUN_CONFIG = {
    "experiment": EXPERIMENT,
    "run_id": RUN_ID,
    "status": "prepared",
    "created_at": datetime.now().astimezone().isoformat(),
    "project_root": str(PROJECT_ROOT),
    "data_dir": str(DATA_DIR),
    "git_commit": git_commit,
    "python": sys.version,
    "platform": platform.platform(),
    "torch": torch.__version__,
    "cuda_runtime": torch.version.cuda,
    "cuda_device": device_name,
    "train_embryo": "6bba",
    "validation_embryo": "44b6",
    "train_videos": train_ids,
    "validation_videos": holdout_ids,
    "split_sha256": hashlib.sha256(SPLIT_SOURCE.read_bytes()).hexdigest(),
    "initialization": "scratch",
    "epochs": EPOCHS,
    "batch_size": BATCH_SIZE,
    "num_workers": NUM_WORKERS,
    "learning_rate": LEARNING_RATE,
    "seed": SEED,
    "window_size": WINDOW_SIZE,
    "det_loss": DET_LOSS,
    "det_neg_weight": DET_NEG_WEIGHT,
    "det_loss_weight": DET_LOSS_WEIGHT,
    "downsample": DOWNSAMPLE,
    "pool_kernel_um": POOL_KERNEL_UM,
    "aug_intensity": AUG_INTENSITY,
    "max_iters_per_epoch": MAX_ITERS,
    "amp": True,
    "gradient_checkpointing": False,
    "command": TRAIN_CMD,
}
(RUN_DIR / "run_config.json").write_text(json.dumps(RUN_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
(RUN_DIR / "command.txt").write_text(subprocess.list2cmdline(TRAIN_CMD) + "\n", encoding="utf-8")
(RUN_DIR / "results.json").write_text(
    json.dumps(
        {
            "experiment": EXPERIMENT,
            "run_id": RUN_ID,
            "status": "prepared",
            "official_metric": None,
            "note": "Official prediction/evaluation is Friend B's follow-up task.",
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
print("scratch command prepared (no pretrained weights):")
print(subprocess.list2cmdline(TRAIN_CMD))
