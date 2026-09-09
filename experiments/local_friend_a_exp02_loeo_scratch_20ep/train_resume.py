# Train from scratch, or resume the full state from the last completed epoch.


def read_training_progress() -> tuple[int, dict | None]:
    if not TRAIN_STATE.exists():
        return 0, None
    payload = torch.load(TRAIN_STATE, map_location="cpu", weights_only=False)
    if payload.get("format") != "friend_a_step1_state_v1":
        raise RuntimeError(f"Unexpected training-state format in {TRAIN_STATE}")
    if int(payload.get("target_epochs", -1)) != EPOCHS:
        raise RuntimeError(f"Training-state target does not equal {EPOCHS} epochs")
    if payload.get("model_config") != {
        "unet_out_channels": 32,
        "unet_layers": [32, 64, 128],
        "downsample": [1, 4, 4],
        "window_size": WINDOW_SIZE,
        "pool_kernel_um": POOL_KERNEL_UM,
    }:
        raise RuntimeError("Training-state architecture differs from the fixed STEP-1 recipe")
    completed = int(payload["completed_epochs"])
    if not 0 <= completed <= EPOCHS:
        raise RuntimeError(f"Invalid completed epoch count: {completed}")
    return completed, payload


TRAIN_CMD_BASE = [
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
    "--lr-schedule", LR_SCHEDULE,
    "--min-lr", str(MIN_LEARNING_RATE),
    "--det-loss-weight", str(DET_LOSS_WEIGHT),
    "--det-neg-weight", str(DET_NEG_WEIGHT),
    "--window-size", str(WINDOW_SIZE),
    "--downsample", DOWNSAMPLE,
    "--pool-kernel-um", str(POOL_KERNEL_UM),
    "--max-detections", str(MAX_DETECTIONS),
    "--checkpoint-every", str(CHECKPOINT_EVERY),
    "--det-loss", DET_LOSS,
    "--seed", str(SEED),
    "--amp",
    "--no-grad-ckpt",
    "--single-gpu",
]
if "--init-weights" in TRAIN_CMD_BASE or "--unet-weights" in TRAIN_CMD_BASE:
    raise RuntimeError("Leakage guard: STEP 1 must start from scratch")

if RUN_PIPELINE:
    completed_epochs, training_payload = read_training_progress()
    if training_payload is not None:
        del training_payload
    if completed_epochs < EPOCHS:
        train_command = [*TRAIN_CMD_BASE]
        if completed_epochs:
            train_command.extend(["--resume-state", str(TRAIN_STATE)])
            print(f"Resuming the exact full state after epoch {completed_epochs}/{EPOCHS}")
        else:
            print("Starting the honest Friend A model from scratch")
        atomic_write_text(RUN_DIR / "train_command.txt", subprocess.list2cmdline(train_command) + "\n")
        trainer_env = {
            **os.environ,
            "BIOHUB_DATA_DIR": str(DATA_DIR),
            "PYTHONPATH": str(TRAIN_REPO / "src"),
            "PYTHONUNBUFFERED": "1",
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
            "PYTORCH_ALLOC_CONF": "expandable_segments:True",
        }
        save_pipeline_state(status="training", completed_epochs_before_launch=completed_epochs)
        run_streamed(
            train_command,
            cwd=TRAIN_REPO,
            env=trainer_env,
            log_path=RUN_DIR / "train.log",
            label="training",
        )
    completed_epochs, training_payload = read_training_progress()
    if completed_epochs != EPOCHS:
        raise RuntimeError(f"Trainer returned without reaching {EPOCHS} epochs: completed={completed_epochs}")
    del training_payload

    required_model_files = [
        TRAIN_OUTPUT / "edge_predictor_best.pth",
        TRAIN_OUTPUT / "config.json",
        *[TRAIN_OUTPUT / f"edge_predictor_epoch_{epoch:03d}.pth" for epoch in MILESTONE_EPOCHS],
    ]
    missing_model_files = [str(path) for path in required_model_files if not path.is_file()]
    if missing_model_files:
        raise FileNotFoundError("Training finished but checkpoint files are missing:\n" + "\n".join(missing_model_files))

    epoch_pattern = re.compile(
        r"Epoch\s+(?P<epoch>\d+)/(?P<epochs>\d+).*?lr=(?P<lr>[0-9.eE+-]+).*?"
        r"edge=(?P<edge>[0-9.eE+-]+).*?det=(?P<det>[0-9.eE+-]+).*?"
        r"test_loss=(?P<test_loss>[0-9.eE+-]+).*?acc=(?P<acc>[0-9.eE+-]+).*?"
        r"recall=(?P<recall>[0-9.eE+-]+).*?best=(?P<best>[0-9.eE+-]+)(?:\s+(?P<marker>\*))?\s+\|\s*"
        r"train=(?P<train_seconds>[0-9.eE+-]+)s\s+test=(?P<validation_seconds>[0-9.eE+-]+)s"
    )
    epoch_by_number = {}
    for match in epoch_pattern.finditer((RUN_DIR / "train.log").read_text(encoding="utf-8", errors="replace")):
        epoch_number = int(match.group("epoch"))
        epoch_by_number[epoch_number] = {
            "epoch": epoch_number,
            **{
                key: float(match.group(key))
                for key in (
                    "lr", "edge", "det", "test_loss", "acc", "recall", "best",
                    "train_seconds", "validation_seconds",
                )
            },
            "checkpoint_saved_as_internal_best": match.group("marker") == "*",
        }
    training_history = [epoch_by_number[number] for number in sorted(epoch_by_number)]
    if [row["epoch"] for row in training_history] != list(range(1, EPOCHS + 1)):
        raise RuntimeError("Could not reconstruct a complete 1..20 training history from train.log")
    atomic_write_text(RUN_DIR / "training_history.json", json.dumps(training_history, indent=2))
    history_fields = list(training_history[0])
    with (RUN_DIR / "training_history.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=history_fields)
        writer.writeheader()
        writer.writerows(training_history)
    internal_best_rows = [row for row in training_history if row["checkpoint_saved_as_internal_best"]]
    internal_best_epoch = internal_best_rows[-1]["epoch"] if internal_best_rows else None
    save_pipeline_state(
        status="training_complete",
        completed_epochs=EPOCHS,
        internal_best_epoch=internal_best_epoch,
        internal_best_score=max(row["best"] for row in training_history),
    )
    print(f"Training complete: {EPOCHS}/{EPOCHS} epochs; internal best epoch={internal_best_epoch}")
else:
    print("BIOHUB_STEP1_RUN_PIPELINE=0: training intentionally skipped after preflight.")
