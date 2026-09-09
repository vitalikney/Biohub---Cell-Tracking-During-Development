# Validate the honest split, create/reuse a persistent run directory, and prepare a resumable trainer.

required_modules = [
    "torch", "tracksdata", "geff", "polars", "rustworkx", "zarr", "tqdm",
    "scipy", "skimage", "dask", "networkx", "pandas", "pyscipopt", "ilpy", "blosc2",
]
missing_modules = [name for name in required_modules if importlib.util.find_spec(name) is None]
if missing_modules:
    raise ImportError("Missing STEP-1 packages: " + ", ".join(missing_modules))

import torch

if sys.version_info[:2] != (3, 12):
    raise RuntimeError(f"Python 3.12 is required; current interpreter: {sys.version.split()[0]}")
if not torch.cuda.is_available():
    raise RuntimeError("CUDA is unavailable. Select the Python 3.12 project kernel and restart Jupyter.")
probe = torch.zeros(1, device="cuda")
del probe
torch.cuda.empty_cache()
device_name = torch.cuda.get_device_name(0)
print(f"CUDA OK: torch={torch.__version__}, CUDA={torch.version.cuda}, device={device_name}")

split_manifest = json.loads(SPLIT_SOURCE.read_text(encoding="utf-8"))
train_ids = list(split_manifest["train"])
holdout_ids = list(split_manifest["holdout"])
if len(train_ids) != 126 or len(holdout_ids) != 12:
    raise RuntimeError(f"Unexpected manifest size: train={len(train_ids)}, holdout={len(holdout_ids)}")
if len(train_ids) != len(set(train_ids)) or len(holdout_ids) != len(set(holdout_ids)):
    raise RuntimeError("Duplicate IDs in the LOEO manifest")
if set(train_ids) & set(holdout_ids):
    raise RuntimeError("Leakage: train and holdout IDs overlap")
if any(not name.startswith("6bba_") for name in train_ids):
    raise RuntimeError("Leakage: every train video must be 6bba")
if any(not name.startswith("44b6_") for name in holdout_ids):
    raise RuntimeError("Leakage: every holdout video must be 44b6")
missing_paths = [
    str(DATA_DIR / f"{name}{suffix}")
    for name in train_ids + holdout_ids
    for suffix in (".zarr", ".geff")
    if not (DATA_DIR / f"{name}{suffix}").exists()
]
if missing_paths:
    raise FileNotFoundError(f"Missing {len(missing_paths)} data paths. First entries:\n" + "\n".join(missing_paths[:20]))
print(f"Leak-free split OK: {len(train_ids)} train 6bba | {len(holdout_ids)} holdout 44b6")

branch = run_checked([*GIT, "branch", "--show-current"], cwd=PROJECT_ROOT).strip()
if AUTO_GIT and branch != EXPECTED_BRANCH:
    raise RuntimeError(f"Auto-publish requires branch {EXPECTED_BRANCH!r}; current branch is {branch!r}")
dirty_before = run_checked([*GIT, "status", "--porcelain"], cwd=PROJECT_ROOT).strip()
if dirty_before:
    print("WARNING: working tree is not clean. Auto-commit will refuse unrelated paths at publication time:\n" + dirty_before)

RUN_DIR.mkdir(parents=True, exist_ok=True)
EVALUATION_ROOT.mkdir(parents=True, exist_ok=True)
PREDICTIONS_ROOT.mkdir(parents=True, exist_ok=True)
EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_SPLIT = RUN_DIR / "loeo_train6bba_val44b6_for_trainer.json"
EVAL_SPLIT = RUN_DIR / "loeo_44b6_for_prediction.json"
atomic_write_text(TRAIN_SPLIT, json.dumps([{"split": 0, "train": train_ids, "test": holdout_ids}], indent=2))
atomic_write_text(EVAL_SPLIT, json.dumps([{"split": 0, "train": [], "test": holdout_ids}], indent=2))


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"STEP-1 resume patch {label!r}: expected one occurrence, found {count}")
    return source.replace(old, new, 1)


def apply_step1_resume_patch(script_path: Path) -> None:
    source = script_path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        "    init_weights: Path | None = None,\n) -> UNetNodeTransformer:\n",
        "    init_weights: Path | None = None,\n    resume_state: Path | None = None,\n) -> UNetNodeTransformer:\n",
        "train signature",
    )
    source = replace_once(
        source,
        '    parser.add_argument("--init-weights", type=str, default=None, help="Full model checkpoint to fine-tune from.")\n',
        '    parser.add_argument("--init-weights", type=str, default=None, help="Full model checkpoint to fine-tune from.")\n'
        '    parser.add_argument("--resume-state", type=str, default=None, help="Resume full model/optimizer/scheduler state.")\n',
        "resume CLI",
    )
    source = replace_once(
        source,
        "    args = parser.parse_args()\n",
        "    args = parser.parse_args()\n"
        "    if args.init_weights and args.resume_state:\n"
        "        raise ValueError(\"--init-weights and --resume-state are mutually exclusive\")\n",
        "resume CLI guard",
    )
    source = replace_once(
        source,
        "        train(\n            init_weights=Path(args.init_weights) if args.init_weights else None,\n            seed=args.seed,\n",
        "        train(\n            init_weights=Path(args.init_weights) if args.init_weights else None,\n"
        "            resume_state=Path(args.resume_state) if args.resume_state else None,\n            seed=args.seed,\n",
        "pass resume state",
    )
    source = replace_once(
        source,
        "    if init_weights is not None:\n",
        "    resume_payload = None\n"
        "    start_epoch = 0\n"
        "    resume_best_score = 0.0\n"
        "    if resume_state is not None:\n"
        "        resume_payload = torch.load(resume_state, map_location=\"cpu\", weights_only=False)\n"
        "        if resume_payload.get(\"format\") != \"friend_a_step1_state_v1\":\n"
        "            raise RuntimeError(f\"Unsupported resume-state format: {resume_payload.get('format')}\")\n"
        "        if resume_payload.get(\"model_config\") != model_config:\n"
        "            raise RuntimeError(\"Resume-state model config differs from the requested architecture\")\n"
        "        if int(resume_payload.get(\"target_epochs\", -1)) != n_epochs:\n"
        "            raise RuntimeError(\"Resume-state target epoch count differs from --epochs\")\n"
        "        start_epoch = int(resume_payload[\"completed_epochs\"])\n"
        "        if not 0 <= start_epoch <= n_epochs:\n"
        "            raise RuntimeError(f\"Invalid completed epoch count in resume state: {start_epoch}\")\n"
        "        resume_best_score = float(resume_payload[\"best_score\"])\n"
        "        _resume_missing, _resume_unexpected = model.load_state_dict(resume_payload[\"model_state\"], strict=True)\n"
        "        if _resume_missing or _resume_unexpected:\n"
        "            raise RuntimeError(\"Resume-state model keys do not match\")\n"
        "        print(f\"  loaded full resume state after epoch {start_epoch}/{n_epochs}\", flush=True)\n"
        "    if init_weights is not None:\n",
        "load resume model",
    )
    source = replace_once(
        source,
        "    print(\n        f\"Starting training for {n_epochs} epochs (batch_size={batch_size}, \"\n",
        "    if resume_payload is not None:\n"
        "        optimizer.load_state_dict(resume_payload[\"optimizer_state\"])\n"
        "        if scheduler is not None and resume_payload.get(\"scheduler_state\") is not None:\n"
        "            scheduler.load_state_dict(resume_payload[\"scheduler_state\"])\n"
        "        if resume_payload.get(\"scaler_state\") is not None:\n"
        "            SCALER.load_state_dict(resume_payload[\"scaler_state\"])\n"
        "        if g is not None and resume_payload.get(\"dataloader_generator_state\") is not None:\n"
        "            g.set_state(resume_payload[\"dataloader_generator_state\"])\n"
        "        if resume_payload.get(\"torch_rng_state\") is not None:\n"
        "            torch.set_rng_state(resume_payload[\"torch_rng_state\"])\n"
        "        if device.type == \"cuda\" and resume_payload.get(\"cuda_rng_state_all\") is not None:\n"
        "            torch.cuda.set_rng_state_all(resume_payload[\"cuda_rng_state_all\"])\n"
        "        if resume_payload.get(\"numpy_rng_state\") is not None:\n"
        "            np.random.set_state(resume_payload[\"numpy_rng_state\"])\n"
        "        del resume_payload\n"
        "    print(\n        f\"Starting training for {n_epochs} epochs (batch_size={batch_size}, \"\n",
        "restore optimiser and RNG",
    )
    source = replace_once(
        source,
        "    best_score = 0.0\n",
        "    best_score = resume_best_score\n",
        "resume best score",
    )
    source = replace_once(
        source,
        '    pbar = tqdm(range(n_epochs), desc="Training", disable=False)\n',
        '    pbar = tqdm(range(start_epoch, n_epochs), total=n_epochs, initial=start_epoch, desc="Training", disable=False)\n',
        "resume epoch range",
    )
    source = replace_once(
        source,
        "            rng = np.random.default_rng()\n",
        "            rng = np.random.default_rng(int(np.random.randint(0, 2**32, dtype=np.uint64)))\n",
        "reproducible augmentation RNG",
    )
    source = replace_once(
        source,
        '            f"  Epoch {epoch:3d}/{n_epochs} | lr={current_lr:.2e} | edge={edge_loss:.4f} | det={det_loss:.4f} | "\n',
        '            f"  Epoch {epoch + 1:3d}/{n_epochs} | lr={current_lr:.2e} | edge={edge_loss:.4f} | det={det_loss:.4f} | "\n',
        "one-based epoch display",
    )
    source = replace_once(
        source,
        "        if scheduler is not None:\n            scheduler.step()\n        marker = \"*\" if is_best else \" \"\n",
        "        if scheduler is not None:\n"
        "            scheduler.step()\n"
        "        _resume_model_state = {k.replace(\"unet.module.\", \"unet.\", 1): v for k, v in model.state_dict().items()}\n"
        "        _resume_payload = {\n"
        "            \"format\": \"friend_a_step1_state_v1\",\n"
        "            \"completed_epochs\": epoch + 1,\n"
        "            \"target_epochs\": n_epochs,\n"
        "            \"best_score\": best_score,\n"
        "            \"model_config\": model_config,\n"
        "            \"model_state\": _resume_model_state,\n"
        "            \"optimizer_state\": optimizer.state_dict(),\n"
        "            \"scheduler_state\": scheduler.state_dict() if scheduler is not None else None,\n"
        "            \"scaler_state\": SCALER.state_dict(),\n"
        "            \"torch_rng_state\": torch.get_rng_state(),\n"
        "            \"cuda_rng_state_all\": torch.cuda.get_rng_state_all() if device.type == \"cuda\" else None,\n"
        "            \"numpy_rng_state\": np.random.get_state(),\n"
        "            \"dataloader_generator_state\": g.get_state() if g is not None else None,\n"
        "        }\n"
        "        _resume_tmp = output_dir / \"training_state_latest.tmp\"\n"
        "        torch.save(_resume_payload, _resume_tmp)\n"
        "        _resume_tmp.replace(output_dir / \"training_state_latest.pt\")\n"
        "        print(f\"  Resume state saved after epoch {epoch + 1}/{n_epochs}\", flush=True)\n"
        "        marker = \"*\" if is_best else \" \"\n",
        "atomic full-state checkpoint",
    )
    script_path.write_text(source, encoding="utf-8")
    print(f"Applied STEP-1 full-state resume patch to {script_path}")


patch_marker = TRAIN_REPO / ".friend_a_step1_patch_complete"
if TRAIN_REPO.exists() and not patch_marker.exists():
    if not TRAIN_REPO.resolve().is_relative_to(RUN_DIR.resolve()):
        raise RuntimeError(f"Refusing to replace unexpected training repository: {TRAIN_REPO}")
    shutil.rmtree(TRAIN_REPO)

if not patch_marker.exists():
    TRAIN_REPO.mkdir(parents=True)
    for subdir in ("scripts", "src"):
        shutil.copytree(PROJECT_ROOT / "tools" / "repo" / subdir, TRAIN_REPO / subdir)
    patch_spec = importlib.util.spec_from_file_location("friend_a_train_patches", TRAIN_PATCH_SOURCE)
    if patch_spec is None or patch_spec.loader is None:
        raise RuntimeError(f"Cannot import {TRAIN_PATCH_SOURCE}")
    patch_module = importlib.util.module_from_spec(patch_spec)
    patch_spec.loader.exec_module(patch_module)
    train_script = TRAIN_REPO / "scripts" / "train_unet_transformer.py"
    patch_module.apply_train_patches(train_script)
    trainer_source = train_script.read_text(encoding="utf-8")
    legacy_import = "from biohub_tracking.models import SimpleNodeTransformer, TemporalUNet3D"
    if legacy_import in trainer_source:
        trainer_source = trainer_source.replace(
            legacy_import,
            "from biohub_tracking.models.simple_node_transformer import SimpleNodeTransformer\n"
            "from biohub_tracking.models.temporal_unet import TemporalUNet3D",
            1,
        )
        train_script.write_text(trainer_source, encoding="utf-8")
    apply_step1_resume_patch(train_script)
    atomic_write_text(patch_marker, "friend_a_step1_state_v1\n")

TRAIN_SCRIPT = TRAIN_REPO / "scripts" / "train_unet_transformer.py"
PREDICT_SCRIPT = TRAIN_REPO / "scripts" / "predict_unet_transformer.py"
compile(TRAIN_SCRIPT.read_text(encoding="utf-8"), str(TRAIN_SCRIPT), "exec")
compile(PREDICT_SCRIPT.read_text(encoding="utf-8"), str(PREDICT_SCRIPT), "exec")
help_env = {
    **os.environ,
    "PYTHONPATH": str(TRAIN_REPO / "src"),
    "BIOHUB_DATA_DIR": str(DATA_DIR),
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
}
help_text = run_checked([sys.executable, str(TRAIN_SCRIPT), "--help"], cwd=TRAIN_REPO, env=help_env)
for flag in (
    "--resume-state", "--amp", "--no-grad-ckpt", "--seed", "--det-loss", "--max-detections",
    "--lr-schedule", "--min-lr", "--checkpoint-every",
):
    if flag not in help_text:
        raise RuntimeError(f"Prepared trainer is missing required flag: {flag}")

run_config = {
    "experiment": EXPERIMENT,
    "step": 1,
    "run_id": RUN_ID,
    "project_root": str(PROJECT_ROOT),
    "data_dir": str(DATA_DIR),
    "branch": branch,
    "python": sys.version,
    "platform": platform.platform(),
    "torch": torch.__version__,
    "cuda_runtime": torch.version.cuda,
    "cuda_device": device_name,
    "split": str(SPLIT_SOURCE.relative_to(PROJECT_ROOT)),
    "split_sha256": sha256_file(SPLIT_SOURCE),
    "train_videos": train_ids,
    "validation_videos": holdout_ids,
    "initialization": "scratch",
    "epochs": EPOCHS,
    "milestone_epochs": list(MILESTONE_EPOCHS),
    "batch_size": BATCH_SIZE,
    "num_workers": NUM_WORKERS,
    "learning_rate": LEARNING_RATE,
    "learning_rate_schedule": LR_SCHEDULE,
    "minimum_learning_rate": MIN_LEARNING_RATE,
    "seed": SEED,
    "window_size": WINDOW_SIZE,
    "det_loss": DET_LOSS,
    "det_neg_weight": DET_NEG_WEIGHT,
    "det_loss_weight": DET_LOSS_WEIGHT,
    "downsample": [int(value) for value in DOWNSAMPLE.split(",")],
    "pool_kernel_um": POOL_KERNEL_UM,
    "max_detections": MAX_DETECTIONS,
    "checkpoint_every": CHECKPOINT_EVERY,
    "amp": True,
    "gradient_checkpointing": False,
    "prediction": {
        "det_threshold": DET_THRESHOLD,
        "use_ilp": True,
        "ilp_appearance_weight": ILP_APPEARANCE,
        "ilp_disappearance_weight": ILP_DISAPPEARANCE,
        "ilp_division_weight": ILP_DIVISION,
        "post_processing": None,
    },
    "references": [
        "pilkwang/biohub-tracking-support-pack-50ep-v1",
        "pilkwang/biohub-temporal-unet3d-seed314159-v1",
    ],
    "weights_dataset_subfolder": WEIGHTS_DATASET_SUBFOLDER,
}
config_fingerprint = hashlib.sha256(json.dumps(run_config, sort_keys=True).encode("utf-8")).hexdigest()
run_config["config_fingerprint"] = config_fingerprint
if RUN_CONFIG_PATH.exists():
    previous_config = json.loads(RUN_CONFIG_PATH.read_text(encoding="utf-8"))
    if previous_config.get("config_fingerprint") != config_fingerprint:
        raise RuntimeError(
            f"Existing run {RUN_DIR} uses a different configuration. Set BIOHUB_STEP1_RUN_ID to a new value."
        )
else:
    atomic_write_text(RUN_CONFIG_PATH, json.dumps(run_config, ensure_ascii=False, indent=2))
save_pipeline_state(status="prepared", config_fingerprint=config_fingerprint)

REFERENCE_SPECS = {
    "reference_pilkwang_primary": "pilkwang/biohub-tracking-support-pack-50ep-v1",
    "reference_pilkwang_secondary_seed314159": "pilkwang/biohub-temporal-unet3d-seed314159-v1",
}
REFERENCE_REMOTE_DIR = "weights/unet_transformer/split_0"


def ensure_reference_model(label: str, dataset: str) -> Path:
    target_dir = REFERENCE_ROOT / label
    target_weights = target_dir / "edge_predictor_best.pth"
    target_config = target_dir / "config.json"
    if target_weights.exists() and target_config.exists():
        return target_weights
    target_dir.mkdir(parents=True, exist_ok=True)
    download_dir = target_dir / "download"
    download_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("edge_predictor_best.pth", "config.json"):
        remote_file = f"{REFERENCE_REMOTE_DIR}/{filename}"
        output = run_checked(
            [
                sys.executable, "-m", "kaggle", "datasets", "download", dataset,
                "-f", remote_file, "-p", str(download_dir), "--unzip", "-o",
            ],
            cwd=PROJECT_ROOT,
        )
        if output.strip():
            print(output.strip())
        candidates = [path for path in download_dir.rglob(filename) if path.is_file()]
        if not candidates:
            raise FileNotFoundError(f"Kaggle download did not produce {remote_file} for {dataset}")
        shutil.copy2(candidates[0], target_dir / filename)
    state = torch.load(target_weights, map_location="cpu", weights_only=True)
    if not isinstance(state, dict) or not state:
        raise RuntimeError(f"Invalid reference checkpoint: {target_weights}")
    del state
    print(f"Reference ready: {label} | {sha256_file(target_weights)}")
    return target_weights

print("STEP-1 preflight passed. The notebook is safe to resume in the same RUN_DIR.")
