# Predict and officially score milestones, training-best, and the two pilkwang references.


def load_valid_metrics(path: Path) -> dict | None:
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    summary = payload.get("summary", {})
    if int(summary.get("n", -1)) != len(holdout_ids):
        return None
    if {row.get("dataset") for row in rows} != set(holdout_ids):
        return None
    return payload


def evaluation_is_complete(payload: dict | None) -> bool:
    prediction_zip = payload.get("prediction_zip") if payload is not None else None
    return bool(
        payload is not None
        and "checkpoint" in payload
        and "aggregate_node_counts" in payload
        and prediction_zip
        and Path(prediction_zip).is_file()
    )


def n_pred_over_n_est(rows: list[dict]) -> tuple[int, float, float]:
    from geff import GeffMetadata

    predicted = 0
    estimated = 0.0
    for row in rows:
        n_pred = int(row["num_pred_nodes"])
        metadata = GeffMetadata.read(DATA_DIR / f"{row['dataset']}.geff")
        n_est = float((metadata.extra or {}).get("estimated_number_of_nodes", float("nan")))
        if not math.isfinite(n_est) or n_est <= 0:
            raise RuntimeError(f"Missing estimated_number_of_nodes for {row['dataset']}")
        expected_ratio = (n_pred - n_est) / n_est
        reported_ratio = float(row["total_node_ratio"])
        if not math.isclose(expected_ratio, reported_ratio, rel_tol=1e-9, abs_tol=1e-9):
            raise RuntimeError(f"Official scorer node ratio mismatch for {row['dataset']}")
        predicted += n_pred
        estimated += n_est
    return predicted, estimated, predicted / estimated


def zip_and_remove_predictions(prediction_dir: Path, label: str) -> Path:
    if not prediction_dir.resolve().is_relative_to(PREDICTIONS_ROOT.resolve()):
        raise RuntimeError(f"Refusing to archive unexpected prediction path: {prediction_dir}")
    zip_dir = RUN_DIR / "prediction_zips"
    zip_dir.mkdir(parents=True, exist_ok=True)
    zip_path = zip_dir / f"{label}.zip"
    temporary_base = zip_dir / f".{label}.building"
    temporary_zip = Path(shutil.make_archive(str(temporary_base), "zip", root_dir=prediction_dir))
    temporary_zip.replace(zip_path)
    shutil.rmtree(prediction_dir)
    return zip_path


def evaluate_weights(label: str, weights_path: Path, *, candidate: bool, epoch: int | None) -> dict:
    evaluation_dir = EVALUATION_ROOT / label
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = evaluation_dir / "official_metrics.json"
    existing = load_valid_metrics(metrics_path)
    if evaluation_is_complete(existing):
        print(f"Skipping completed evaluation: {label} | score={existing['summary']['score']:.4f}")
        return existing

    if not weights_path.is_file() or not weights_path.with_name("config.json").is_file():
        raise FileNotFoundError(f"Checkpoint/config pair missing for {label}: {weights_path}")
    method = f"step1_{label}"
    prediction_dir = PREDICTIONS_ROOT / "friend_a_step1" / method / "split_0"
    predictor_env = {
        **os.environ,
        "USER": "friend_a_step1",
        "BIOHUB_DATA_DIR": str(DATA_DIR),
        "BIOHUB_PREDICTIONS_DIR": str(PREDICTIONS_ROOT),
        "PYTHONPATH": str(TRAIN_REPO / "src"),
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTORCH_ALLOC_CONF": "expandable_segments:True",
    }
    predict_command = [
        sys.executable,
        str(PREDICT_SCRIPT),
        "--method", method,
        "--data-dir", str(DATA_DIR),
        "--splits", str(EVAL_SPLIT),
        "--split", "0",
        "--weights", str(weights_path),
        "--unet-batch-size", "4",
        "--det-threshold", str(DET_THRESHOLD),
        "--use-ilp",
        "--ilp-appearance-weight", str(ILP_APPEARANCE),
        "--ilp-disappearance-weight", str(ILP_DISAPPEARANCE),
        "--ilp-division-weight", str(ILP_DIVISION),
    ]
    started = time.monotonic()
    save_pipeline_state(status=f"evaluating_{label}", active_evaluation=label)
    run_streamed(
        predict_command,
        cwd=TRAIN_REPO,
        env=predictor_env,
        log_path=evaluation_dir / "predict.log",
        label=f"predict_{label}",
    )
    geffs = sorted(prediction_dir.glob("*.geff"))
    if len(geffs) != len(holdout_ids) or {path.stem for path in geffs} != set(holdout_ids):
        raise RuntimeError(f"Prediction coverage for {label} is not exactly the 12 LOEO videos")

    score_env = {
        **os.environ,
        "BIOHUB_DATA_DIR": str(DATA_DIR),
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
    }
    score_command = [
        sys.executable,
        str(PROJECT_ROOT / "tools" / "score_geffs.py"),
        str(prediction_dir),
        "--out", str(metrics_path),
    ]
    run_streamed(
        score_command,
        cwd=PROJECT_ROOT,
        env=score_env,
        log_path=evaluation_dir / "score.log",
        label=f"score_{label}",
    )
    metrics = load_valid_metrics(metrics_path)
    if metrics is None:
        raise RuntimeError(f"Official scorer did not create a complete metrics file for {label}")
    n_pred, n_est, node_ratio = n_pred_over_n_est(metrics["rows"])
    zip_path = zip_and_remove_predictions(prediction_dir, label)
    metrics["checkpoint"] = {
        "label": label,
        "candidate": candidate,
        "epoch": epoch,
        "weights": str(weights_path),
        "weights_sha256": sha256_file(weights_path),
    }
    metrics["aggregate_node_counts"] = {
        "n_pred": n_pred,
        "n_est": n_est,
        "n_pred_over_n_est": node_ratio,
    }
    metrics["prediction_zip"] = str(zip_path)
    metrics["wall_seconds"] = time.monotonic() - started
    atomic_write_text(metrics_path, json.dumps(metrics, ensure_ascii=False, indent=2))
    state = load_pipeline_state()
    evaluations = dict(state.get("evaluations", {}))
    evaluations[label] = {
        "status": "complete",
        "metrics": str(metrics_path),
        "score": metrics["summary"]["score"],
    }
    save_pipeline_state(status="evaluation_in_progress", active_evaluation=None, evaluations=evaluations)
    print(
        f"{label}: score={metrics['summary']['score']:.4f} edge={metrics['summary']['edge_jaccard']:.4f} "
        f"recall={metrics['summary']['node_recall']:.4f} N_pred/N_est={node_ratio:.4f}"
    )
    return metrics


if RUN_PIPELINE:
    completed_epochs, completed_payload = read_training_progress()
    if completed_epochs != EPOCHS:
        raise RuntimeError("Evaluation cannot start before all 20 training epochs are complete")
    del completed_payload
    internal_best_epoch = load_pipeline_state().get("internal_best_epoch")
    evaluation_specs = [
        *[
            {
                "label": f"epoch_{epoch:03d}",
                "weights": TRAIN_OUTPUT / f"edge_predictor_epoch_{epoch:03d}.pth",
                "candidate": True,
                "epoch": epoch,
            }
            for epoch in MILESTONE_EPOCHS
        ],
        {
            "label": "training_best",
            "weights": TRAIN_OUTPUT / "edge_predictor_best.pth",
            "candidate": True,
            "epoch": internal_best_epoch,
        },
    ]
    for reference_label, dataset in REFERENCE_SPECS.items():
        reference_metrics = load_valid_metrics(EVALUATION_ROOT / reference_label / "official_metrics.json")
        reference_weights = (
            REFERENCE_ROOT / reference_label / "edge_predictor_best.pth"
            if evaluation_is_complete(reference_metrics)
            else ensure_reference_model(reference_label, dataset)
        )
        evaluation_specs.append(
            {"label": reference_label, "weights": reference_weights, "candidate": False, "epoch": None}
        )

    all_metrics = {}
    for spec in evaluation_specs:
        all_metrics[spec["label"]] = evaluate_weights(
            spec["label"], spec["weights"], candidate=spec["candidate"], epoch=spec["epoch"]
        )
    save_pipeline_state(status="evaluation_complete", active_evaluation=None)
    print("All five candidate entries and both pilkwang references have official 12/12 LOEO metrics.")
else:
    print("BIOHUB_STEP1_RUN_PIPELINE=0: checkpoint evaluation intentionally skipped.")
