# Validate both fixed splits, prepare the patched repo, and resolve verified checkpoints.

import ast

required_modules = [
    "torch", "tracksdata", "geff", "polars", "rustworkx", "zarr", "tqdm", "scipy",
    "skimage", "dask", "networkx", "pandas", "pyscipopt", "ilpy", "blosc2", "kaggle",
]
missing_modules = [name for name in required_modules if importlib.util.find_spec(name) is None]
if missing_modules:
    raise ImportError("Missing pipeline packages: " + ", ".join(missing_modules))

import torch

if sys.version_info[:2] != (3, 12):
    raise RuntimeError(f"Python 3.12 is required; current interpreter: {sys.version.split()[0]}")
if not DATA_DIR.is_dir():
    raise FileNotFoundError(DATA_DIR)

loeo_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
train_ids = list(loeo_manifest["train"])
holdout_ids = list(loeo_manifest["holdout"])
if len(train_ids) != 126 or len(holdout_ids) != 12 or set(train_ids) & set(holdout_ids):
    raise RuntimeError("Unexpected or leaking LOEO manifest")
if any(not value.startswith("6bba_") for value in train_ids):
    raise RuntimeError("LOEO train side must contain only 6bba")
if any(not value.startswith("44b6_") for value in holdout_ids):
    raise RuntimeError("LOEO validation side must contain only 44b6")


def read_exp03_split(path: Path) -> dict[str, list[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        call = node.value
        if (
            isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "json"
            and call.func.attr == "dumps"
            and call.args
        ):
            value = ast.literal_eval(call.args[0])
            if isinstance(value, dict) and set(value) == {"train", "holdout"}:
                return {key: list(items) for key, items in value.items()}
    raise RuntimeError(f"Could not find exp03 split in {path}")


exp03_split = read_exp03_split(EXP03_CONFIG_PATH)
exp03_train_ids = exp03_split["train"]
exp03_holdout_ids = exp03_split["holdout"]
if len(exp03_train_ids) != 183 or len(exp03_holdout_ids) != 12:
    raise RuntimeError("Unexpected exp03 183/12 split")
if set(exp03_train_ids) & set(exp03_holdout_ids):
    raise RuntimeError("exp03 train and holdout overlap")

all_ids = sorted(path.stem for path in DATA_DIR.glob("*.geff"))
if len(all_ids) != 199 or len(set(all_ids)) != 199:
    raise RuntimeError(f"Expected 199 source videos, found {len(all_ids)}")
missing_exp03_ids = sorted(set(exp03_train_ids + exp03_holdout_ids) - set(all_ids))
if missing_exp03_ids:
    raise RuntimeError(f"exp03 split contains unknown videos: {missing_exp03_ids}")
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
atomic_write_text(LOEO_TRAIN_SPLIT_PATH, json.dumps([{"split": 0, "train": train_ids, "test": holdout_ids}], indent=2))
atomic_write_text(LOEO_EVAL_SPLIT_PATH, json.dumps([{"split": 0, "train": [], "test": holdout_ids}], indent=2))
atomic_write_text(EXP03_TRAIN_SPLIT_PATH, json.dumps([{"split": 0, "train": exp03_train_ids, "test": exp03_holdout_ids}], indent=2))
atomic_write_text(EXP03_EVAL_SPLIT_PATH, json.dumps([{"split": 0, "train": [], "test": exp03_holdout_ids}], indent=2))
atomic_write_text(ALL_MANIFEST_PATH, json.dumps({"all": all_ids}, indent=2))

branch = checked([*GIT, "branch", "--show-current"], cwd=PROJECT_ROOT).strip()
if AUTO_GIT and branch != EXPECTED_BRANCH:
    raise RuntimeError(f"Auto-publish needs branch {EXPECTED_BRANCH!r}; current branch is {branch!r}")
if RUN_PIPELINE:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable. Select the project Python 3.12 kernel and restart Jupyter.")
    probe = torch.zeros(1, device="cuda")
    del probe
    torch.cuda.empty_cache()
    cuda_device = torch.cuda.get_device_name(0)
    print(f"CUDA OK: torch={torch.__version__}, runtime={torch.version.cuda}, device={cuda_device}")
else:
    cuda_device = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "dry preflight"


def prepare_repo_copy() -> None:
    marker = REPO_DIR / ".friend_a_dense_ft_patch_v1"
    if marker.is_file():
        return
    if REPO_DIR.exists():
        guarded_remove_tree(REPO_DIR, RUN_DIR)
    REPO_DIR.mkdir(parents=True)
    for subdir in ("scripts", "src"):
        shutil.copytree(PROJECT_ROOT / "tools" / "repo" / subdir, REPO_DIR / subdir)
    train_patch = import_file("friend_a_dense_ft_train_patches", TRAIN_PATCH_PATH)
    predict_patch = import_file("friend_a_dense_ft_predict_patches", PREDICT_PATCH_PATH)
    train_script = REPO_DIR / "scripts" / "train_unet_transformer.py"
    predict_script = REPO_DIR / "scripts" / "predict_unet_transformer.py"
    train_patch.apply_train_patches(train_script)
    predict_patch.apply_predict_patches(predict_script)
    legacy_import = "from biohub_tracking.models import SimpleNodeTransformer, TemporalUNet3D"
    trainer_source = train_script.read_text(encoding="utf-8")
    if legacy_import in trainer_source:
        trainer_source = trainer_source.replace(
            legacy_import,
            "from biohub_tracking.models.simple_node_transformer import SimpleNodeTransformer\n"
            "from biohub_tracking.models.temporal_unet import TemporalUNet3D",
            1,
        )
        train_script.write_text(trainer_source, encoding="utf-8")
    compile(train_script.read_text(encoding="utf-8"), str(train_script), "exec")
    compile(predict_script.read_text(encoding="utf-8"), str(predict_script), "exec")
    help_text = checked([sys.executable, str(train_script), "--help"], cwd=REPO_DIR, env=common_env(DATA_DIR))
    for flag in ("--init-weights", "--max-iters", "--amp", "--no-grad-ckpt", "--max-detections", "--aug-intensity"):
        if flag not in help_text:
            raise RuntimeError(f"Patched trainer is missing {flag}")
    atomic_write_text(marker, "friend_a_dense_ft_patch_v1\n")


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


def copy_verified_pair(source_dir: Path, target_dir: Path, expected_hash: str) -> Path:
    source_weights = source_dir / "edge_predictor_best.pth"
    source_config = source_dir / "config.json"
    if not source_weights.is_file() or not source_config.is_file():
        raise FileNotFoundError(f"Incomplete checkpoint pair in {source_dir}")
    if sha256_file(source_weights).lower() != expected_hash.lower():
        raise RuntimeError(f"Checkpoint hash mismatch in {source_dir}: {sha256_file(source_weights)}")
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_weights, target_dir / source_weights.name)
    shutil.copy2(source_config, target_dir / source_config.name)
    return target_dir / source_weights.name


def ensure_pair(target_dir: Path, expected_hash: str, local_candidates: list[Path], dataset: str, remote_folder: str) -> Path:
    target = target_dir / "edge_predictor_best.pth"
    config = target_dir / "config.json"
    if target.is_file() and config.is_file() and sha256_file(target).lower() == expected_hash.lower():
        return target
    source = next((path for path in local_candidates if (path / "edge_predictor_best.pth").is_file()), None)
    if source is not None:
        return copy_verified_pair(source, target_dir, expected_hash)
    for name in ("edge_predictor_best.pth", "config.json"):
        download_model_file(dataset, f"{remote_folder}/{name}", target_dir / name)
    if sha256_file(target).lower() != expected_hash.lower():
        raise RuntimeError(f"Downloaded checkpoint hash mismatch: {target}")
    return target


def ensure_primary_model() -> Path:
    return ensure_pair(
        PRIMARY_WEIGHTS_DIR,
        PRIMARY_EXPECTED_SHA256,
        [OUTPUT_ROOT / "_reference_weights" / "reference_pilkwang_primary"],
        PRIMARY_DATASET,
        PRIMARY_REMOTE_FOLDER,
    )


def ensure_teacher_models() -> tuple[Path, Path]:
    primary = ensure_pair(
        TEACHER_PRIMARY_DIR,
        TEACHER_PRIMARY_EXPECTED_SHA256,
        [
            OUTPUT_ROOT / "_dense_pipeline_weights" / "exp03B",
            OUTPUT_ROOT / "kaggle_weights_upload_20260907_2215" / "exp03B",
        ],
        WEIGHTS_DATASET,
        "exp03B",
    )
    secondary = ensure_pair(
        TEACHER_SECONDARY_DIR,
        TEACHER_SECONDARY_EXPECTED_SHA256,
        [
            OUTPUT_ROOT / "_dense_pipeline_weights" / "seed314159",
            OUTPUT_ROOT / "_reference_weights" / "reference_pilkwang_secondary_seed314159",
        ],
        SECONDARY_DATASET,
        SECONDARY_REMOTE_FOLDER,
    )
    return primary, secondary


prepare_repo_copy()
run_config = {
    "experiment": EXPERIMENT,
    "plan_revision": "2026-09-10 20:00",
    "branch": branch,
    "python": sys.version,
    "platform": platform.platform(),
    "cuda_device": cuda_device,
    "loeo_manifest_sha256": sha256_file(MANIFEST_PATH),
    "initialization": "verified pilkwang primary",
    "primary_sha256": PRIMARY_EXPECTED_SHA256,
    "variants": VARIANTS,
    "batch_size": BATCH_SIZE,
    "epochs": FT_EPOCHS,
    "learning_rate": FT_LEARNING_RATE,
    "learning_rate_schedule": "constant",
    "max_detections": MAX_DETECTIONS,
    "seed": SEED,
    "winning_delta": WINNING_DELTA,
    "scratch_training": False,
    "leaderboard_submission": False,
}
fingerprint = hashlib.sha256(json.dumps(run_config, sort_keys=True).encode()).hexdigest()
run_config["fingerprint"] = fingerprint
run_config_path = RUN_DIR / "run_config.json"
if run_config_path.is_file():
    previous = json.loads(run_config_path.read_text(encoding="utf-8"))
    if previous.get("fingerprint") != fingerprint:
        raise RuntimeError("The active dense-FT run uses another recipe. Set BIOHUB_DENSE_FT_RUN_ID to a new value.")
else:
    atomic_write_text(run_config_path, json.dumps(run_config, ensure_ascii=False, indent=2))
save_state(status="prepared", config_fingerprint=fingerprint)
print(f"Preflight OK: LOEO {len(train_ids)}/{len(holdout_ids)}; exp03 {len(exp03_train_ids)}/{len(exp03_holdout_ids)}")
print(f"Reusable teacher files: {sum((TEACHER_DIR / f'{value}.geff').is_dir() for value in train_ids + holdout_ids)}/138")
if not RUN_PIPELINE:
    print("Dry preflight only: no teacher, training, upload, or git operation was started.")
