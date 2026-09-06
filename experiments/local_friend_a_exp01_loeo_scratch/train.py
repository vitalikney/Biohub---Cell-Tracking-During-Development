# Stream the long-running process to the notebook and to train.log.

import re


def write_results(payload: dict) -> None:
    (RUN_DIR / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


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
    safe_line = line.encode(encoding, errors="replace").decode(encoding, errors="replace")
    print(safe_line, end="", flush=True)


if RUN_TRAINING:
    started_at = datetime.now().astimezone()
    train_log = RUN_DIR / "train.log"
    trainer_env = {
        **os.environ,
        "BIOHUB_DATA_DIR": str(DATA_DIR),
        "PYTHONPATH": str(TRAIN_REPO / "src"),
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTORCH_ALLOC_CONF": "expandable_segments:True",
    }
    print(f"Training started at {started_at.isoformat()}", flush=True)
    with train_log.open("w", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            TRAIN_CMD,
            cwd=TRAIN_REPO,
            env=trainer_env,
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
            write_results(
                {
                    "experiment": EXPERIMENT,
                    "run_id": RUN_ID,
                    "status": "interrupted",
                    "official_metric": None,
                    "log": str(train_log),
                }
            )
            raise
        except BaseException:
            terminate_process(process)
            write_results(
                {
                    "experiment": EXPERIMENT,
                    "run_id": RUN_ID,
                    "status": "notebook_stream_failed",
                    "official_metric": None,
                    "log": str(train_log),
                }
            )
            raise

    finished_at = datetime.now().astimezone()
    wall_seconds = (finished_at - started_at).total_seconds()
    if return_code != 0:
        write_results(
            {
                "experiment": EXPERIMENT,
                "run_id": RUN_ID,
                "status": "failed",
                "return_code": return_code,
                "official_metric": None,
                "wall_seconds": wall_seconds,
                "log": str(train_log),
            }
        )
        raise RuntimeError(f"Training failed with exit code {return_code}; see {train_log}")

    checkpoint_source = TRAIN_REPO / "weights" / METHOD / "split_0" / "edge_predictor_best.pth"
    model_config_source = checkpoint_source.parent / "config.json"
    if not checkpoint_source.exists() or not model_config_source.exists():
        raise FileNotFoundError("Training ended successfully but the expected checkpoint/config pair is missing")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=False)
    checkpoint_target = ARTIFACT_DIR / "edge_predictor_best.pth"
    model_config_target = ARTIFACT_DIR / "config.json"
    shutil.copy2(checkpoint_source, checkpoint_target)
    shutil.copy2(model_config_source, model_config_target)
    shutil.copy2(RUN_DIR / "run_config.json", ARTIFACT_DIR / "run_config.json")

    log_text = train_log.read_text(encoding="utf-8", errors="replace")
    epoch_pattern = re.compile(
        r"Epoch\s+(?P<epoch>\d+)/(?P<epochs>\d+).*?edge=(?P<edge>[0-9.eE+-]+).*?"
        r"det=(?P<det>[0-9.eE+-]+).*?test_loss=(?P<test_loss>[0-9.eE+-]+).*?"
        r"acc=(?P<acc>[0-9.eE+-]+).*?recall=(?P<recall>[0-9.eE+-]+).*?best=(?P<best>[0-9.eE+-]+)"
    )
    epoch_rows = []
    for match in epoch_pattern.finditer(log_text):
        row = {"epoch": int(match.group("epoch"))}
        row.update({key: float(match.group(key)) for key in ("edge", "det", "test_loss", "acc", "recall", "best")})
        epoch_rows.append(row)

    checkpoint_sha256 = hashlib.sha256(checkpoint_target.read_bytes()).hexdigest()
    results = {
        "experiment": EXPERIMENT,
        "run_id": RUN_ID,
        "status": "trained_not_officially_scored",
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "wall_seconds": wall_seconds,
        "train_videos": len(train_ids),
        "validation_videos": len(holdout_ids),
        "validation_set": "LOEO-44b6",
        "initialization": "scratch",
        "checkpoint": str(checkpoint_target),
        "checkpoint_sha256": checkpoint_sha256,
        "model_config": str(model_config_target),
        "internal_sparse_validation": epoch_rows,
        "official_metric": None,
        "note": "Internal acc/recall is diagnostic only; Friend B must run prediction and the official metric.",
    }
    write_results(results)
    shutil.copy2(RUN_DIR / "results.json", ARTIFACT_DIR / "results.json")
    print(f"Training complete in {wall_seconds / 3600:.2f} h")
    print(f"Hand-off artifact: {ARTIFACT_DIR}")
else:
    print("BIOHUB_RUN_TRAINING=0: preflight passed; training was intentionally skipped.")
