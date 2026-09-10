# Resumable teacher, training, evaluation, reporting, and Kaggle-dataset helpers.

from geff import GeffMetadata

TRAIN_SCRIPT = REPO_DIR / "scripts" / "train_unet_transformer.py"
PREDICT_SCRIPT = REPO_DIR / "scripts" / "predict_unet_transformer.py"


def upsert_results_row(key: str, line: str) -> None:
    path = PROJECT_ROOT / "experiments" / "RESULTS.md"
    lines = [value for value in path.read_text(encoding="utf-8").splitlines() if not value.startswith(key)]
    insert_at = next((index for index, value in enumerate(lines) if value.startswith("## Per-video")), len(lines))
    lines.insert(insert_at, line)
    atomic_write_text(path, "\n".join(lines).rstrip() + "\n")


def commit_and_push(paths: list[Path], message: str) -> None:
    relative = [str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/") for path in paths]
    already_staged = checked([*GIT, "diff", "--cached", "--name-only"], cwd=PROJECT_ROOT).splitlines()
    unexpected_staged = set(already_staged) - set(relative)
    if unexpected_staged:
        raise RuntimeError("Refusing to include already-staged unrelated files: " + ", ".join(sorted(unexpected_staged)))
    checked([*GIT, "add", "--", *relative], cwd=PROJECT_ROOT)
    staged = subprocess.run([*GIT, "diff", "--cached", "--quiet"], cwd=PROJECT_ROOT)
    if staged.returncode == 1:
        print(checked([*GIT, "commit", "-m", message], cwd=PROJECT_ROOT).strip())
    elif staged.returncode != 0:
        raise RuntimeError("git diff --cached failed")
    print(checked([*GIT, "push", "origin", EXPECTED_BRANCH], cwd=PROJECT_ROOT).strip())


def restore_geff_folder(snapshot: Path, folder: str, destination: Path, expected_ids: list[str]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for index, dataset_id in enumerate(expected_ids, start=1):
        target = destination / f"{dataset_id}.geff"
        if target.exists():
            continue
        candidates = [path for path in snapshot.rglob(f"{dataset_id}.geff") if path.is_dir() and folder in path.parts]
        if candidates:
            shutil.copytree(candidates[0], target)
        else:
            archives = [path for path in snapshot.rglob(f"{dataset_id}.geff.zip") if folder in path.parts]
            if not archives:
                raise FileNotFoundError(f"Remote folder {folder} has no {dataset_id}.geff(.zip)")
            unpack = RUN_DIR / "restore_tmp" / folder / dataset_id
            if unpack.exists():
                guarded_remove_tree(unpack, RUN_DIR)
            unpack.mkdir(parents=True)
            shutil.unpack_archive(str(archives[0]), str(unpack))
            nested = [path for path in unpack.rglob(f"{dataset_id}.geff") if path.is_dir()]
            source = nested[0] if nested else unpack
            shutil.copytree(source, target)
        if index % 20 == 0 or index == len(expected_ids):
            print(f"restored {folder}: {index}/{len(expected_ids)}", flush=True)


def download_dataset_snapshot() -> Path:
    snapshot = RUN_DIR / "weights_dataset_snapshot"
    marker = snapshot / ".download_complete"
    if marker.is_file():
        return snapshot
    if snapshot.exists():
        guarded_remove_tree(snapshot, RUN_DIR)
    snapshot.mkdir(parents=True)
    stream_command(
        [sys.executable, "-m", "kaggle", "datasets", "download", WEIGHTS_DATASET,
         "-p", str(snapshot), "--unzip", "-o"],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        log_path=RUN_DIR / "dataset_download.log",
        label="download_weights_dataset",
    )
    atomic_write_text(marker, "complete\n")
    return snapshot


def stage_current_weights_dataset(stage_name: str) -> Path:
    stage = RUN_DIR / stage_name
    if stage.exists():
        guarded_remove_tree(stage, RUN_DIR)
    stage.mkdir(parents=True)
    stream_command(
        [sys.executable, "-m", "kaggle", "datasets", "download", WEIGHTS_DATASET,
         "-p", str(stage), "--unzip", "-o"],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        log_path=RUN_DIR / f"{stage_name}.log",
        label=f"stage_{stage_name}",
    )
    atomic_write_text(
        stage / "dataset-metadata.json",
        json.dumps({"id": WEIGHTS_DATASET, "title": "biohub-ft-weights"}, indent=2) + "\n",
    )
    return stage


def publish_dataset_stage(stage: Path, message: str, expected_prefixes: list[str]) -> None:
    stream_command(
        [sys.executable, "-m", "kaggle", "datasets", "version", "-p", str(stage),
         "--dir-mode", "zip", "-m", message],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        log_path=RUN_DIR / "dataset_upload.log",
        label="upload_weights_dataset_version",
    )
    for attempt in range(12):
        listing = kaggle_files()
        if all(prefix in listing for prefix in expected_prefixes):
            print("Kaggle dataset version is visible and contains all requested folders.")
            return
        if attempt < 11:
            print("Kaggle is still processing the dataset version; retrying in 10 seconds...")
            time.sleep(10)
    raise RuntimeError("Kaggle accepted the version but expected folders are not visible")


def upload_geff_folders(folder_sources: dict[str, Path], expected_ids: list[str], message: str) -> None:
    stage = stage_current_weights_dataset("geff_upload_stage")
    for folder, source in folder_sources.items():
        target = stage / folder
        if target.exists():
            guarded_remove_tree(target, stage)
        target.mkdir(parents=True)
        for dataset_id in expected_ids:
            source_geff = source / f"{dataset_id}.geff"
            if not source_geff.is_dir():
                raise FileNotFoundError(source_geff)
            shutil.copytree(source_geff, target / source_geff.name)
    publish_dataset_stage(stage, message, [f"{folder}/" for folder in folder_sources])


def upload_weight_pair(weights: Path, folder: str, message: str) -> None:
    state = load_state()
    state_key = f"uploaded_{folder}"
    if state.get(state_key) == sha256_file(weights):
        print(f"Already uploaded and recorded: {folder}/")
        return
    config_path = weights.with_name("config.json")
    if not weights.is_file() or not config_path.is_file():
        raise FileNotFoundError(f"Incomplete weight/config pair: {weights}")
    stage = stage_current_weights_dataset("weights_upload_stage")
    target = stage / folder
    if target.exists():
        guarded_remove_tree(target, stage)
    target.mkdir(parents=True)
    shutil.copy2(weights, target / "edge_predictor_best.pth")
    shutil.copy2(config_path, target / "config.json")
    publish_dataset_stage(stage, message, [f"{folder}/edge_predictor_best.pth", f"{folder}/config.json"])
    save_state(**{state_key: sha256_file(weights)})


def prediction_output(user: str, method: str) -> Path:
    return PREDICTIONS_ROOT / user / method / "split_0"


def predict_teacher_chunk(dataset_ids: list[str], label: str) -> list[Path]:
    primary, secondary = ensure_teacher_models()
    split_path = RUN_DIR / "teacher_splits" / f"{label}.json"
    atomic_write_text(split_path, json.dumps([{"split": 0, "train": [], "test": dataset_ids}], indent=2))
    user = "friend_a_dense_teacher"
    method = label
    env = common_env(DATA_DIR)
    env["USER"] = user
    env["BIOHUB_ENSEMBLE_WEIGHTS"] = str(secondary)
    stream_command(
        [
            sys.executable, str(PREDICT_SCRIPT), "--method", method, "--data-dir", str(DATA_DIR),
            "--splits", str(split_path), "--split", "0", "--weights", str(primary),
            "--unet-batch-size", "4", "--det-threshold", str(DET_THRESHOLD),
        ],
        cwd=REPO_DIR,
        env=env,
        log_path=RUN_DIR / "teacher_logs" / f"{label}.log",
        label=label,
    )
    output = prediction_output(user, method)
    geffs = sorted(output.glob("*.geff"))
    if {path.stem for path in geffs} != set(dataset_ids):
        raise RuntimeError(f"Teacher chunk {label} did not produce exact requested coverage")
    return geffs


def ensure_teacher(ids: list[str], *, smoke_first: bool) -> None:
    TEACHER_DIR.mkdir(parents=True, exist_ok=True)
    if smoke_first and not load_state().get("teacher_smoke_complete"):
        smoke_geffs = predict_teacher_chunk(ids[:2], "teacher_smoke2")
        for path in smoke_geffs:
            loaded = __import__("tracksdata").graph.IndexedRXGraph.from_geff(path)
            graph = loaded[0] if isinstance(loaded, tuple) else loaded
            if graph.num_nodes() <= 0:
                raise RuntimeError(f"Teacher smoke output is empty: {path}")
        guarded_remove_tree(prediction_output("friend_a_dense_teacher", "teacher_smoke2"), PREDICTIONS_ROOT)
        save_state(teacher_smoke_complete=True)
        print("Teacher smoke passed on 2 videos.")
    missing = [dataset_id for dataset_id in ids if not (TEACHER_DIR / f"{dataset_id}.geff").is_dir()]
    for offset in range(0, len(missing), TEACHER_CHUNK_SIZE):
        chunk = missing[offset: offset + TEACHER_CHUNK_SIZE]
        label = f"teacher_chunk_{offset // TEACHER_CHUNK_SIZE:03d}"
        geffs = predict_teacher_chunk(chunk, label)
        for source in geffs:
            target = TEACHER_DIR / source.name
            if target.exists():
                guarded_remove_tree(target, TEACHER_DIR)
            shutil.move(str(source), str(target))
        output_parent = prediction_output("friend_a_dense_teacher", label)
        if output_parent.exists():
            guarded_remove_tree(output_parent, PREDICTIONS_ROOT)
        save_state(status="teacher_in_progress", teacher_complete_count=sum((TEACHER_DIR / f"{x}.geff").is_dir() for x in ids))
    if any(not (TEACHER_DIR / f"{dataset_id}.geff").is_dir() for dataset_id in ids):
        raise RuntimeError("Teacher generation ended with missing datasets")


def training_output(method: str) -> Path:
    return REPO_DIR / "weights" / method / "split_0"


def fixed_train_command(
    *, method: str, data_dir: Path, split_path: Path, epochs: int, neg_weight: float,
    max_detections: int, max_iters: int | None = None,
) -> list[str]:
    command = [
        sys.executable, str(TRAIN_SCRIPT), "--method", method, "--data-dir", str(data_dir),
        "--splits", str(split_path), "--split", "0", "--epochs", str(epochs),
        "--batch-size", str(BATCH_SIZE), "--num-workers", str(NUM_WORKERS),
        "--lr", str(LEARNING_RATE), "--lr-schedule", "cosine", "--min-lr", str(MIN_LEARNING_RATE),
        "--det-loss", "bce", "--det-loss-weight", str(DET_LOSS_WEIGHT),
        "--det-neg-weight", str(neg_weight), "--window-size", str(WINDOW_SIZE),
        "--downsample", DOWNSAMPLE, "--pool-kernel-um", str(POOL_KERNEL_UM),
        "--max-detections", str(max_detections), "--checkpoint-every", str(CHECKPOINT_EVERY),
        "--seed", str(SEED), "--amp", "--no-grad-ckpt", "--single-gpu",
    ]
    if max_iters is not None:
        command.extend(["--max-iters", str(max_iters)])
    if "--init-weights" in command or "--unet-weights" in command:
        raise RuntimeError("Scratch-training leakage guard failed")
    return command


def smoke_training(label: str, data_dir: Path, ids: list[str], neg_weight: float, max_detections: int) -> None:
    key = f"{label}_smoke_complete"
    if load_state().get(key):
        print(f"Skipping completed smoke: {label}")
        return
    split = RUN_DIR / "smoke_splits" / f"{label}.json"
    atomic_write_text(split, json.dumps([{"split": 0, "train": ids[:2], "test": ids[:2]}], indent=2))
    command = fixed_train_command(
        method=f"{label}_smoke", data_dir=data_dir, split_path=split, epochs=1,
        neg_weight=neg_weight, max_detections=max_detections, max_iters=2,
    )
    stream_command(command, cwd=REPO_DIR, env=common_env(data_dir), log_path=RUN_DIR / f"{label}_smoke.log", label=f"{label}_smoke")
    output = training_output(f"{label}_smoke")
    if not (output / "edge_predictor_best.pth").is_file():
        raise RuntimeError(f"Smoke test produced no checkpoint: {label}")
    save_state(**{key: True})
    print(f"Smoke passed: {label}")


def run_training(
    label: str, method: str, data_dir: Path, train_set: list[str], test_set: list[str],
    epochs: int, neg_weight: float, max_detections: int,
) -> Path:
    split = RUN_DIR / "training_splits" / f"{label}.json"
    atomic_write_text(split, json.dumps([{"split": 0, "train": train_set, "test": test_set}], indent=2))
    output = training_output(method)
    state_path = output / "training_state_latest.pt"
    completed = 0
    if state_path.is_file():
        payload = torch.load(state_path, map_location="cpu", weights_only=False)
        if payload.get("format") != "biohub_full_training_state_v1":
            raise RuntimeError(f"Unknown resume state format: {state_path}")
        if int(payload.get("target_epochs", -1)) != epochs:
            raise RuntimeError(f"Resume state target differs from requested {epochs} epochs")
        completed = int(payload["completed_epochs"])
        del payload
    if completed < epochs:
        command = fixed_train_command(
            method=method, data_dir=data_dir, split_path=split, epochs=epochs,
            neg_weight=neg_weight, max_detections=max_detections,
        )
        if completed:
            command.extend(["--resume-state", str(state_path)])
            print(f"Resuming {label} after epoch {completed}/{epochs}")
        else:
            print(f"Starting {label} from scratch")
        atomic_write_text(RUN_DIR / f"{label}_command.txt", subprocess.list2cmdline(command) + "\n")
        save_state(status=f"training_{label}", active_training=label, completed_epochs_before_launch=completed)
        stream_command(command, cwd=REPO_DIR, env=common_env(data_dir), log_path=RUN_DIR / f"{label}_train.log", label=f"train_{label}")
    payload = torch.load(state_path, map_location="cpu", weights_only=False)
    if int(payload.get("completed_epochs", -1)) != epochs:
        raise RuntimeError(f"{label} returned before completing {epochs} epochs")
    del payload
    save_state(status=f"training_{label}_complete", active_training=None)
    return output


def metric_node_counts(rows: list[dict]) -> tuple[int, float, float]:
    predicted = 0
    estimated = 0.0
    for row in rows:
        predicted += int(row["num_pred_nodes"])
        metadata = GeffMetadata.read(DATA_DIR / f"{row['dataset']}.geff")
        value = float((metadata.extra or {}).get("estimated_number_of_nodes", float("nan")))
        if not math.isfinite(value) or value <= 0:
            raise RuntimeError(f"No estimated_number_of_nodes for {row['dataset']}")
        estimated += value
    return predicted, estimated, predicted / estimated


def evaluate_checkpoint(label: str, weights: Path, expected_ids: list[str]) -> dict:
    evaluation = EVALUATION_ROOT / label
    metrics_path = evaluation / "official_metrics.json"
    if metrics_path.is_file():
        existing = json.loads(metrics_path.read_text(encoding="utf-8"))
        if int(existing.get("summary", {}).get("n", -1)) == len(expected_ids) and existing.get("prediction_zip"):
            if Path(existing["prediction_zip"]).is_file():
                print(f"Skipping completed official evaluation: {label}")
                return existing
    evaluation.mkdir(parents=True, exist_ok=True)
    if not weights.is_file() or not weights.with_name("config.json").is_file():
        raise FileNotFoundError(f"Checkpoint/config missing: {weights}")
    user = "friend_a_dense_eval"
    method = label
    env = common_env(DATA_DIR)
    env["USER"] = user
    stream_command(
        [
            sys.executable, str(PREDICT_SCRIPT), "--method", method, "--data-dir", str(DATA_DIR),
            "--splits", str(EVAL_SPLIT_PATH), "--split", "0", "--weights", str(weights),
            "--unet-batch-size", "4", "--det-threshold", str(DET_THRESHOLD), "--use-ilp",
            "--ilp-appearance-weight", str(ILP_APPEARANCE),
            "--ilp-disappearance-weight", str(ILP_DISAPPEARANCE),
            "--ilp-division-weight", str(ILP_DIVISION),
        ],
        cwd=REPO_DIR,
        env=env,
        log_path=evaluation / "predict.log",
        label=f"predict_{label}",
    )
    prediction_dir = prediction_output(user, method)
    geffs = sorted(prediction_dir.glob("*.geff"))
    if {path.stem for path in geffs} != set(expected_ids):
        raise RuntimeError(f"Official evaluation coverage mismatch for {label}")
    stream_command(
        [sys.executable, str(PROJECT_ROOT / "tools" / "score_geffs.py"), str(prediction_dir), "--out", str(metrics_path)],
        cwd=PROJECT_ROOT,
        env={**os.environ, "BIOHUB_DATA_DIR": str(DATA_DIR), "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        log_path=evaluation / "score.log",
        label=f"score_{label}",
    )
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    if int(payload.get("summary", {}).get("n", -1)) != len(expected_ids):
        raise RuntimeError(f"Official scorer skipped one or more videos for {label}")
    n_pred, n_est, ratio = metric_node_counts(payload["rows"])
    zip_dir = RUN_DIR / "prediction_zips"
    zip_dir.mkdir(parents=True, exist_ok=True)
    temp_base = zip_dir / f".{label}.building"
    archive = Path(shutil.make_archive(str(temp_base), "zip", root_dir=prediction_dir))
    zip_path = zip_dir / f"{label}.zip"
    archive.replace(zip_path)
    guarded_remove_tree(prediction_dir, PREDICTIONS_ROOT)
    payload["checkpoint"] = {"label": label, "weights": str(weights), "weights_sha256": sha256_file(weights)}
    payload["aggregate_node_counts"] = {"n_pred": n_pred, "n_est": n_est, "n_pred_over_n_est": ratio}
    payload["prediction_zip"] = str(zip_path)
    atomic_write_text(metrics_path, json.dumps(payload, ensure_ascii=False, indent=2))
    print(
        f"{label}: score={payload['summary']['score']:.4f}, edge={payload['summary']['edge_jaccard']:.4f}, "
        f"recall={payload['summary']['node_recall']:.4f}, Npred/Nest={ratio:.3f}"
    )
    return payload


def evaluate_milestones(label_prefix: str, output: Path, epochs: tuple[int, ...]) -> dict[str, dict]:
    specs = [(f"epoch_{epoch:03d}", output / f"edge_predictor_epoch_{epoch:03d}.pth") for epoch in epochs]
    specs.append(("training_best", output / "edge_predictor_best.pth"))
    results = {}
    for checkpoint_label, weights in specs:
        results[checkpoint_label] = evaluate_checkpoint(f"{label_prefix}_{checkpoint_label}", weights, holdout_ids)
    return results


def compact_metric(checkpoint_label: str, payload: dict) -> dict:
    summary = payload["summary"]
    counts = payload["aggregate_node_counts"]
    epoch_match = re.search(r"epoch_(\d+)$", checkpoint_label)
    return {
        "label": checkpoint_label,
        "epoch": int(epoch_match.group(1)) if epoch_match else None,
        "score": float(summary["score"]),
        "adj_edge_jaccard": float(summary["adj_edge_jaccard"]),
        "edge_jaccard": float(summary["edge_jaccard"]),
        "division_jaccard": float(summary["division_jaccard"]),
        "division_tp": int(summary["division_tp"]),
        "division_fp": int(summary["division_fp"]),
        "division_fn": int(summary["division_fn"]),
        "node_recall": float(summary["node_recall"]),
        "n_pred": int(counts["n_pred"]),
        "n_est": float(counts["n_est"]),
        "n_pred_over_n_est": float(counts["n_pred_over_n_est"]),
        "weights": payload["checkpoint"]["weights"],
        "weights_sha256": payload["checkpoint"]["weights_sha256"],
    }
