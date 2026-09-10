# Shared resumable helpers for STEP 1c, five fine-tune comparisons, and the winning 183-video run.

from geff import GeffMetadata

TRAIN_SCRIPT = REPO_DIR / "scripts" / "train_unet_transformer.py"
PREDICT_SCRIPT = REPO_DIR / "scripts" / "predict_unet_transformer.py"


def kaggle_files(dataset: str = WEIGHTS_DATASET) -> str:
    return checked(
        [sys.executable, "-m", "kaggle", "datasets", "files", dataset, "--page-size", "1000"],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
    )


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


def restore_geff_folder(snapshot: Path, folder: str, destination: Path, expected_ids: list[str]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for index, dataset_id in enumerate(expected_ids, start=1):
        target = destination / f"{dataset_id}.geff"
        if target.is_dir():
            continue
        unpacked = [
            path for path in snapshot.rglob(f"{dataset_id}.geff")
            if path.is_dir() and folder in path.parts
        ]
        if unpacked:
            shutil.copytree(unpacked[0], target)
        else:
            archives = [
                path for path in snapshot.rglob(f"{dataset_id}.geff.zip")
                if folder in path.parts
            ]
            if not archives:
                raise FileNotFoundError(f"Remote folder {folder} has no {dataset_id}.geff(.zip)")
            temporary = RUN_DIR / "restore_tmp" / folder / dataset_id
            if temporary.exists():
                guarded_remove_tree(temporary, RUN_DIR)
            temporary.mkdir(parents=True)
            shutil.unpack_archive(str(archives[0]), str(temporary))
            nested = [path for path in temporary.rglob(f"{dataset_id}.geff") if path.is_dir()]
            shutil.copytree(nested[0] if nested else temporary, target)
        if index % 20 == 0 or index == len(expected_ids):
            print(f"restored {folder}: {index}/{len(expected_ids)}", flush=True)


def upsert_results_row(key: str, line: str) -> None:
    path = PROJECT_ROOT / "experiments" / "RESULTS.md"
    lines = [value for value in path.read_text(encoding="utf-8").splitlines() if not value.startswith(key)]
    insert_at = next((index for index, value in enumerate(lines) if value.startswith("## Per-video")), len(lines))
    lines.insert(insert_at, line)
    atomic_write_text(path, "\n".join(lines).rstrip() + "\n")


def commit_and_push(paths: list[Path], message: str) -> None:
    relative = [str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/") for path in paths]
    staged_before = checked([*GIT, "diff", "--cached", "--name-only"], cwd=PROJECT_ROOT).splitlines()
    unrelated = set(staged_before) - set(relative)
    if unrelated:
        raise RuntimeError("Refusing to include unrelated staged files: " + ", ".join(sorted(unrelated)))
    checked([*GIT, "add", "--", *relative], cwd=PROJECT_ROOT)
    staged = subprocess.run([*GIT, "diff", "--cached", "--quiet"], cwd=PROJECT_ROOT)
    if staged.returncode == 1:
        print(checked([*GIT, "commit", "-m", message], cwd=PROJECT_ROOT).strip())
    elif staged.returncode != 0:
        raise RuntimeError("git diff --cached failed")
    print(checked([*GIT, "push", "origin", EXPECTED_BRANCH], cwd=PROJECT_ROOT).strip())


def stage_current_dataset(name: str) -> Path:
    stage = RUN_DIR / name
    if stage.exists():
        guarded_remove_tree(stage, RUN_DIR)
    stage.mkdir(parents=True)
    stream_command(
        [sys.executable, "-m", "kaggle", "datasets", "download", WEIGHTS_DATASET,
         "-p", str(stage), "--unzip", "-o"],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        log_path=RUN_DIR / f"{name}.log",
        label=f"stage_{name}",
    )
    atomic_write_text(
        stage / "dataset-metadata.json",
        json.dumps({"id": WEIGHTS_DATASET, "title": "biohub-ft-weights"}, indent=2) + "\n",
    )
    return stage


def publish_stage(stage: Path, message: str, expected: list[str]) -> None:
    stream_command(
        [sys.executable, "-m", "kaggle", "datasets", "version", "-p", str(stage),
         "--dir-mode", "zip", "-m", message],
        cwd=PROJECT_ROOT,
        env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        log_path=RUN_DIR / "dataset_upload.log",
        label="upload_dataset_version",
    )
    for attempt in range(12):
        listing = kaggle_files()
        if all(value in listing for value in expected):
            return
        if attempt < 11:
            print("Kaggle is processing the version; retrying in 10 seconds...")
            time.sleep(10)
    raise RuntimeError("Uploaded dataset version is not yet visible with the expected files")


def upload_geff_folders(ids: list[str]) -> None:
    stage = stage_current_dataset("geff_upload_stage")
    for folder, source in ((TEACHER_DATASET_FOLDER, TEACHER_DIR), (DENSE_DATASET_FOLDER, DENSE_DATA_DIR)):
        destination = stage / folder
        if destination.exists():
            guarded_remove_tree(destination, stage)
        destination.mkdir(parents=True)
        for dataset_id in ids:
            geff = source / f"{dataset_id}.geff"
            if not geff.is_dir():
                raise FileNotFoundError(geff)
            shutil.copytree(geff, destination / geff.name)
    publish_stage(
        stage,
        f"Friend A dense teacher/labels: {len(ids)} videos",
        [f"{TEACHER_DATASET_FOLDER}/", f"{DENSE_DATASET_FOLDER}/"],
    )


def upload_weight_pair(weights: Path, folder: str, message: str) -> None:
    config = weights.with_name("config.json")
    if not weights.is_file() or not config.is_file():
        raise FileNotFoundError(f"Incomplete checkpoint pair: {weights}")
    digest = sha256_file(weights)
    if load_state().get(f"uploaded_{folder}") == digest:
        return
    stage = stage_current_dataset("winner_upload_stage")
    destination = stage / folder
    if destination.exists():
        guarded_remove_tree(destination, stage)
    destination.mkdir(parents=True)
    shutil.copy2(weights, destination / "edge_predictor_best.pth")
    shutil.copy2(config, destination / "config.json")
    publish_stage(stage, message, [f"{folder}/edge_predictor_best.pth", f"{folder}/config.json"])
    save_state(**{f"uploaded_{folder}": digest})


def prediction_output(user: str, method: str) -> Path:
    return PREDICTIONS_ROOT / user / method / "split_0"


def predict_teacher_chunk(ids: list[str], label: str) -> list[Path]:
    primary, secondary = ensure_teacher_models()
    split = RUN_DIR / "teacher_splits" / f"{label}.json"
    atomic_write_text(split, json.dumps([{"split": 0, "train": [], "test": ids}], indent=2))
    user = "friend_a_dense_teacher"
    env = common_env(DATA_DIR)
    env["USER"] = user
    env["BIOHUB_ENSEMBLE_WEIGHTS"] = str(secondary)
    stream_command(
        [sys.executable, str(PREDICT_SCRIPT), "--method", label, "--data-dir", str(DATA_DIR),
         "--splits", str(split), "--split", "0", "--weights", str(primary),
         "--unet-batch-size", "4", "--det-threshold", str(DET_THRESHOLD)],
        cwd=REPO_DIR,
        env=env,
        log_path=RUN_DIR / "teacher_logs" / f"{label}.log",
        label=label,
    )
    output = prediction_output(user, label)
    geffs = sorted(output.glob("*.geff"))
    if {path.stem for path in geffs} != set(ids):
        raise RuntimeError(f"Teacher coverage mismatch for {label}")
    return geffs


def ensure_teacher(ids: list[str], *, smoke_key: str) -> None:
    TEACHER_DIR.mkdir(parents=True, exist_ok=True)
    missing = [dataset_id for dataset_id in ids if not (TEACHER_DIR / f"{dataset_id}.geff").is_dir()]
    if missing and not load_state().get(smoke_key):
        smoke = predict_teacher_chunk(missing[:2], f"{smoke_key}_2")
        if len(smoke) != min(2, len(missing)):
            raise RuntimeError("Teacher smoke failed")
        guarded_remove_tree(prediction_output("friend_a_dense_teacher", f"{smoke_key}_2"), PREDICTIONS_ROOT)
        save_state(**{smoke_key: True})
    missing = [dataset_id for dataset_id in ids if not (TEACHER_DIR / f"{dataset_id}.geff").is_dir()]
    for offset in range(0, len(missing), TEACHER_CHUNK_SIZE):
        chunk = missing[offset: offset + TEACHER_CHUNK_SIZE]
        label = f"teacher_{smoke_key}_{offset // TEACHER_CHUNK_SIZE:03d}"
        geffs = predict_teacher_chunk(chunk, label)
        for source in geffs:
            destination = TEACHER_DIR / source.name
            if destination.exists():
                guarded_remove_tree(destination, TEACHER_DIR)
            shutil.move(str(source), str(destination))
        output = prediction_output("friend_a_dense_teacher", label)
        if output.exists():
            guarded_remove_tree(output, PREDICTIONS_ROOT)
        save_state(status="teacher_in_progress", teacher_complete_count=sum((TEACHER_DIR / f"{x}.geff").is_dir() for x in ids))
    if any(not (TEACHER_DIR / f"{dataset_id}.geff").is_dir() for dataset_id in ids):
        raise RuntimeError("Teacher generation ended with missing GEFFs")


def build_dense(
    state_label: str,
    manifest_path: Path,
    manifest_keys: str,
    ids: list[str],
    stats_path: Path,
    *,
    smoke: bool,
) -> None:
    if smoke and not load_state().get(f"{state_label}_builder_smoke"):
        smoke_dir = RUN_DIR / f"{state_label}_builder_smoke"
        stream_command(
            [sys.executable, str(BUILDER_PATH), "--data-dir", str(DATA_DIR), "--teacher-dir", str(TEACHER_DIR),
             "--output-dir", str(smoke_dir), "--manifest", str(manifest_path), "--manifest-keys", manifest_keys,
             "--dedup-radius-um", str(TEACHER_DEDUP_RADIUS_UM), "--stats-out", str(smoke_dir / "dense_stats.csv"),
             "--limit", "2"],
            cwd=PROJECT_ROOT,
            env=common_env(DATA_DIR),
            log_path=RUN_DIR / f"{state_label}_builder_smoke.log",
            label=f"{state_label}_builder_smoke",
        )
        save_state(**{f"{state_label}_builder_smoke": True})
    stream_command(
        [sys.executable, str(BUILDER_PATH), "--data-dir", str(DATA_DIR), "--teacher-dir", str(TEACHER_DIR),
         "--output-dir", str(DENSE_DATA_DIR), "--manifest", str(manifest_path), "--manifest-keys", manifest_keys,
         "--dedup-radius-um", str(TEACHER_DEDUP_RADIUS_UM), "--stats-out", str(stats_path)],
        cwd=PROJECT_ROOT,
        env=common_env(DATA_DIR),
        log_path=RUN_DIR / f"build_dense_{state_label}.log",
        label=f"build_dense_{state_label}",
    )
    with stats_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != len(ids) or any(float(row["gt_node_recall_in_dense"]) != 1.0 for row in rows):
        raise RuntimeError(f"Dense stats validation failed for {state_label}")


def finetune_command(
    *, method: str, data_dir: Path, split_path: Path, max_iters: int,
    det_neg_weight: float, aug_intensity: bool,
) -> list[str]:
    primary = ensure_primary_model()
    command = [
        sys.executable, str(TRAIN_SCRIPT), "--method", method, "--data-dir", str(data_dir),
        "--splits", str(split_path), "--split", "0", "--epochs", str(FT_EPOCHS),
        "--max-iters", str(max_iters), "--batch-size", str(BATCH_SIZE), "--num-workers", str(NUM_WORKERS),
        "--lr", str(FT_LEARNING_RATE), "--lr-schedule", "constant", "--det-loss", "bce",
        "--det-loss-weight", str(DET_LOSS_WEIGHT), "--det-neg-weight", str(det_neg_weight),
        "--window-size", str(WINDOW_SIZE), "--downsample", DOWNSAMPLE,
        "--pool-kernel-um", str(POOL_KERNEL_UM), "--max-detections", str(MAX_DETECTIONS),
        "--seed", str(SEED), "--amp", "--no-grad-ckpt", "--single-gpu",
        "--init-weights", str(primary),
    ]
    if aug_intensity:
        command.append("--aug-intensity")
    if command.count("--init-weights") != 1 or "--unet-weights" in command:
        raise RuntimeError("Every revised-plan training command must fine-tune exactly one full primary checkpoint")
    return command


def training_output(method: str) -> Path:
    return REPO_DIR / "weights" / method / "split_0"


def smoke_finetune(label: str, data_dir: Path, det_neg_weight: float, aug_intensity: bool) -> None:
    key = f"smoke_{label}"
    if load_state().get(key):
        return
    split = RUN_DIR / "smoke_splits" / f"{label}.json"
    atomic_write_text(split, json.dumps([{"split": 0, "train": train_ids[:2], "test": train_ids[:2]}], indent=2))
    method = f"smoke_{label}"
    output = training_output(method)
    if output.exists():
        guarded_remove_tree(output, REPO_DIR / "weights")
    command = finetune_command(
        method=method, data_dir=data_dir, split_path=split, max_iters=2,
        det_neg_weight=det_neg_weight, aug_intensity=aug_intensity,
    )
    stream_command(command, cwd=REPO_DIR, env=common_env(data_dir), log_path=RUN_DIR / f"smoke_{label}.log", label=f"smoke_{label}")
    if not (output / "edge_predictor_best.pth").is_file():
        raise RuntimeError(f"Fine-tune smoke produced no weights: {label}")
    save_state(**{key: True})


def run_finetune(
    *, label: str, data_dir: Path, split_path: Path, max_iters: int,
    det_neg_weight: float, aug_intensity: bool,
) -> Path:
    state = load_state()
    completed = state.get("completed_trainings", {})
    recorded = completed.get(label)
    if recorded and Path(recorded["weights"]).is_file():
        print(f"Skipping completed fine-tune: {label}")
        return Path(recorded["weights"]).parent
    smoke_finetune(label, data_dir, det_neg_weight, aug_intensity)
    method = f"friend_a_{label}"
    output = training_output(method)
    if output.exists():
        guarded_remove_tree(output, REPO_DIR / "weights")
    command = finetune_command(
        method=method, data_dir=data_dir, split_path=split_path, max_iters=max_iters,
        det_neg_weight=det_neg_weight, aug_intensity=aug_intensity,
    )
    atomic_write_text(RUN_DIR / f"{label}_command.txt", subprocess.list2cmdline(command) + "\n")
    save_state(status=f"training_{label}", active_training=label)
    stream_command(command, cwd=REPO_DIR, env=common_env(data_dir), log_path=RUN_DIR / f"train_{label}.log", label=f"train_{label}")
    weights = output / "edge_predictor_best.pth"
    if not weights.is_file() or not weights.with_name("config.json").is_file():
        raise FileNotFoundError(f"Fine-tune did not produce a complete checkpoint: {output}")
    completed = dict(load_state().get("completed_trainings", {}))
    completed[label] = {"weights": str(weights), "sha256": sha256_file(weights), "max_iters": max_iters}
    save_state(status=f"training_{label}_complete", active_training=None, completed_trainings=completed)
    return output


def metric_node_counts(rows: list[dict]) -> tuple[int, float, float]:
    predicted = 0
    estimated = 0.0
    for row in rows:
        predicted += int(row["num_pred_nodes"])
        metadata = GeffMetadata.read(DATA_DIR / f"{row['dataset']}.geff")
        value = float((metadata.extra or {}).get("estimated_number_of_nodes", float("nan")))
        if not math.isfinite(value) or value <= 0:
            raise RuntimeError(f"Missing estimated_number_of_nodes for {row['dataset']}")
        estimated += value
    return predicted, estimated, predicted / estimated


def evaluate_weights(label: str, weights: Path, eval_split: Path, expected_ids: list[str]) -> dict:
    evaluation = EVALUATION_ROOT / label
    metrics_path = evaluation / "official_metrics.json"
    if metrics_path.is_file():
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
        archive = payload.get("prediction_zip")
        if int(payload.get("summary", {}).get("n", -1)) == len(expected_ids) and archive and Path(archive).is_file():
            print(f"Skipping completed official evaluation: {label}")
            return payload
    evaluation.mkdir(parents=True, exist_ok=True)
    user = "friend_a_dense_ft_eval"
    env = common_env(DATA_DIR)
    env["USER"] = user
    prediction_dir = prediction_output(user, label)
    if prediction_dir.exists():
        guarded_remove_tree(prediction_dir, PREDICTIONS_ROOT)
    stream_command(
        [sys.executable, str(PREDICT_SCRIPT), "--method", label, "--data-dir", str(DATA_DIR),
         "--splits", str(eval_split), "--split", "0", "--weights", str(weights),
         "--unet-batch-size", "4", "--det-threshold", str(DET_THRESHOLD), "--use-ilp",
         "--ilp-appearance-weight", str(ILP_APPEARANCE), "--ilp-disappearance-weight", str(ILP_DISAPPEARANCE),
         "--ilp-division-weight", str(ILP_DIVISION)],
        cwd=REPO_DIR,
        env=env,
        log_path=evaluation / "predict.log",
        label=f"predict_{label}",
    )
    geffs = sorted(prediction_dir.glob("*.geff"))
    if {path.stem for path in geffs} != set(expected_ids):
        raise RuntimeError(f"Prediction coverage mismatch for {label}")
    stream_command(
        [sys.executable, str(PROJECT_ROOT / "tools" / "score_geffs.py"), str(prediction_dir), "--out", str(metrics_path)],
        cwd=PROJECT_ROOT,
        env={**os.environ, "BIOHUB_DATA_DIR": str(DATA_DIR), "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
        log_path=evaluation / "score.log",
        label=f"score_{label}",
    )
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    if int(payload.get("summary", {}).get("n", -1)) != len(expected_ids):
        raise RuntimeError(f"Official scorer skipped videos for {label}")
    n_pred, n_est, ratio = metric_node_counts(payload["rows"])
    zip_dir = RUN_DIR / "prediction_zips"
    zip_dir.mkdir(parents=True, exist_ok=True)
    temporary = Path(shutil.make_archive(str(zip_dir / f".{label}.building"), "zip", root_dir=prediction_dir))
    archive = zip_dir / f"{label}.zip"
    temporary.replace(archive)
    guarded_remove_tree(prediction_dir, PREDICTIONS_ROOT)
    payload["checkpoint"] = {"weights": str(weights), "weights_sha256": sha256_file(weights)}
    payload["aggregate_node_counts"] = {"n_pred": n_pred, "n_est": n_est, "n_pred_over_n_est": ratio}
    payload["prediction_zip"] = str(archive)
    atomic_write_text(metrics_path, json.dumps(payload, ensure_ascii=False, indent=2))
    print(
        f"{label}: score={payload['summary']['score']:.4f}, edge={payload['summary']['edge_jaccard']:.4f}, "
        f"recall={payload['summary']['node_recall']:.4f}, Npred/Nest={ratio:.3f}"
    )
    return payload


def compact_metric(payload: dict) -> dict:
    summary = payload["summary"]
    counts = payload["aggregate_node_counts"]
    return {
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


def record_variant(variant: dict, metric: dict) -> dict:
    results_path = EXPERIMENT_DIR / "results.json"
    result = json.loads(results_path.read_text(encoding="utf-8")) if results_path.is_file() else {
        "experiment": EXPERIMENT,
        "plan_revision": "2026-09-10 20:00",
        "split": "126x6bba fine-tune -> 12x44b6 raw official validation",
        "initialization": "pilkwang primary",
        "primary_sha256": PRIMARY_EXPECTED_SHA256,
        "variants": {},
        "winning_delta": WINNING_DELTA,
        "leaderboard_submission": False,
    }
    result["variants"][variant["name"]] = {**variant, "metric": metric, "completed_at": datetime.now().astimezone().isoformat()}
    baseline = result["variants"].get("sparse_1200", {}).get("metric", {}).get("score")
    if baseline is not None:
        for name, value in result["variants"].items():
            value["delta_vs_sparse"] = value["metric"]["score"] - baseline
    result["updated_at"] = datetime.now().astimezone().isoformat()
    atomic_write_text(results_path, json.dumps(result, ensure_ascii=False, indent=2))
    label = variant["name"]
    upsert_results_row(
        f"| local Friend A exp03 {label} |",
        f"| local Friend A exp03 {label} | primary FT; {variant['data']} labels; {variant['max_iters']} it; "
        f"lr 5e-5 constant; neg {variant['det_neg_weight']}; aug={variant['aug_intensity']} | - | "
        f"**{metric['score']:.4f}** (edge {metric['edge_jaccard']:.4f}, recall {metric['node_recall']:.4f}, "
        f"Npred/Nest {metric['n_pred_over_n_est']:.3f}) LOEO-44b6 | GPU | init pilkwang primary; no LB |",
    )
    completed_summary = ", ".join(
        f"{name}={value['metric']['score']:.4f}" for name, value in result["variants"].items()
    )
    context_path = PROJECT_ROOT / "CONTEXT.md"
    update_marked_block(
        context_path,
        "<!-- friend-a-exp03-dense-ft-primary-progress -->",
        f"- {datetime.now().date().isoformat()} Friend A primary fine-tune comparison in progress/completed: "
        f"{completed_summary}; raw official LOEO-44b6, gate dense >= sparse +0.005; no LB.",
        "## 14. Operational state",
    )
    if AUTO_GIT:
        commit_and_push(
            [results_path, PROJECT_ROOT / "experiments" / "RESULTS.md", context_path],
            f"Record Friend A primary FT {label}",
        )
    return result
