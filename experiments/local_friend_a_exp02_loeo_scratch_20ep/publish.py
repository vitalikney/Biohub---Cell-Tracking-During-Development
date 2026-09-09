# Select by the official metric, package the artifact, upload weights, update reports, commit, and push.


def compact_metric(label: str, payload: dict) -> dict:
    summary = payload["summary"]
    nodes = payload["aggregate_node_counts"]
    checkpoint = payload["checkpoint"]
    return {
        "label": label,
        "candidate": bool(checkpoint["candidate"]),
        "epoch": checkpoint["epoch"],
        "weights_sha256": checkpoint["weights_sha256"],
        "score": float(summary["score"]),
        "adj_edge_jaccard": float(summary["adj_edge_jaccard"]),
        "edge_jaccard": float(summary["edge_jaccard"]),
        "division_jaccard": float(summary["division_jaccard"]),
        "division_tp": int(summary["division_tp"]),
        "division_fp": int(summary["division_fp"]),
        "division_fn": int(summary["division_fn"]),
        "node_recall": float(summary["node_recall"]),
        "n_pred": int(nodes["n_pred"]),
        "n_est": float(nodes["n_est"]),
        "n_pred_over_n_est": float(nodes["n_pred_over_n_est"]),
        "videos": int(summary["n"]),
        "wall_seconds": float(payload.get("wall_seconds", 0.0)),
    }


def upload_best_weights(weights_path: Path, config_path: Path, result_summary: dict) -> None:
    current_state = load_pipeline_state()
    if current_state.get("weights_uploaded"):
        print(f"Weights already uploaded as {WEIGHTS_DATASET_SUBFOLDER}/; skipping")
        return
    stage = RUN_DIR / "weights_dataset_stage"
    if stage.exists():
        if not stage.resolve().is_relative_to(RUN_DIR.resolve()):
            raise RuntimeError(f"Refusing to replace unexpected staging path: {stage}")
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    upload_env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    run_streamed(
        [
            sys.executable, "-m", "kaggle", "datasets", "download", WEIGHTS_DATASET,
            "-p", str(stage), "--unzip", "-o",
        ],
        cwd=PROJECT_ROOT,
        env=upload_env,
        log_path=RUN_DIR / "weights_upload.log",
        label="download_current_weights_dataset",
    )
    destination = stage / WEIGHTS_DATASET_SUBFOLDER
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(weights_path, destination / "edge_predictor_best.pth")
    shutil.copy2(config_path, destination / "config.json")
    if sha256_file(destination / "edge_predictor_best.pth") != sha256_file(weights_path):
        raise RuntimeError("Staged checkpoint hash mismatch")
    atomic_write_text(
        stage / "dataset-metadata.json",
        json.dumps({"id": WEIGHTS_DATASET, "title": "biohub-ft-weights"}, indent=2) + "\n",
    )
    readme = stage / "README.md"
    readme_text = readme.read_text(encoding="utf-8") if readme.exists() else "Biohub team weights.\n"
    marker = f"`{WEIGHTS_DATASET_SUBFOLDER}/`"
    if marker not in readme_text:
        readme_text = readme_text.rstrip() + (
            f"\n\n{marker} is Friend A STEP 1's official-best scratch checkpoint trained on 126 6bba videos "
            f"and selected on 12 unseen 44b6 videos: score {result_summary['score']:.6f}, "
            f"edge Jaccard {result_summary['edge_jaccard']:.6f}, node recall {result_summary['node_recall']:.6f}, "
            f"N_pred/N_est {result_summary['n_pred_over_n_est']:.6f}. No leaderboard submission was made.\n"
        )
        atomic_write_text(readme, readme_text)
    run_streamed(
        [
            sys.executable, "-m", "kaggle", "datasets", "version", "-p", str(stage),
            "--dir-mode", "zip", "-m", f"{EXPERIMENT}: official-best LOEO checkpoint",
        ],
        cwd=PROJECT_ROOT,
        env=upload_env,
        log_path=RUN_DIR / "weights_upload.log",
        label="upload_best_weights",
    )
    required_remote_files = [
        f"{WEIGHTS_DATASET_SUBFOLDER}/edge_predictor_best.pth",
        f"{WEIGHTS_DATASET_SUBFOLDER}/config.json",
    ]
    listing = ""
    for attempt in range(6):
        listing = run_checked(
            [sys.executable, "-m", "kaggle", "datasets", "files", WEIGHTS_DATASET, "--page-size", "200"],
            cwd=PROJECT_ROOT,
            env=upload_env,
        )
        if all(name in listing for name in required_remote_files):
            break
        if attempt < 5:
            print("Kaggle version is still processing; checking again in 10 seconds...")
            time.sleep(10)
    else:
        raise RuntimeError("Kaggle accepted the version, but the expected STEP-1 files are not visible after 60 seconds")
    save_pipeline_state(
        status="weights_uploaded",
        weights_uploaded=True,
        weights_dataset=WEIGHTS_DATASET,
        weights_dataset_subfolder=WEIGHTS_DATASET_SUBFOLDER,
        uploaded_checkpoint_sha256=sha256_file(weights_path),
    )
    print(f"Uploaded and verified: {WEIGHTS_DATASET}/{WEIGHTS_DATASET_SUBFOLDER}")


def update_results_markdown(result: dict) -> None:
    path = PROJECT_ROOT / "experiments" / "RESULTS.md"
    text = path.read_text(encoding="utf-8")
    best = result["official_best"]
    refs = result["references"]
    train_hours = result["timing"]["training_gpu_seconds"] / 3600
    eval_hours = result["timing"]["evaluation_wall_seconds"] / 3600
    line = (
        f"| local Friend A exp02 | scratch 20ep, 126x6bba -> LOEO-44b6; BCE, w2, ds1,4,4, cosine 1e-4->1e-5, seed42 | - | "
        f"best **{best['score']:.4f}** at {best['label']} (edge {best['edge_jaccard']:.4f}, recall {best['node_recall']:.4f}, "
        f"Npred/Nest {best['n_pred_over_n_est']:.3f}); primary ref {refs['reference_pilkwang_primary']['score']:.4f}, "
        f"secondary ref {refs['reference_pilkwang_secondary_seed314159']['score']:.4f} | "
        f"{train_hours:.1f} h train + {eval_hours:.1f} h eval | 12/12 honest videos; milestones 5/10/15/20 + training-best; "
        f"dataset `{WEIGHTS_DATASET_SUBFOLDER}/`; stop delta20-15={result['decision']['score20_minus_score15']:+.4f}; no LB submission |"
    )
    lines = [existing for existing in text.splitlines() if not existing.startswith("| local Friend A exp02 |")]
    insert_at = next((index for index, existing in enumerate(lines) if existing.startswith("## Per-video")), len(lines))
    lines.insert(insert_at, line)
    atomic_write_text(path, "\n".join(lines).rstrip() + "\n")


def update_context(result: dict) -> None:
    path = PROJECT_ROOT / "CONTEXT.md"
    text = path.read_text(encoding="utf-8")
    marker = "<!-- friend-a-exp02-loeo20-result -->"
    best = result["official_best"]
    decision = result["decision"]
    note = (
        f"{marker}\n- {datetime.now().date().isoformat()} Friend A STEP 1 complete: 20-epoch scratch 6bba->44b6 official best "
        f"{best['score']:.4f} ({best['label']}, edge {best['edge_jaccard']:.4f}, recall {best['node_recall']:.4f}, "
        f"N_pred/N_est {best['n_pred_over_n_est']:.3f}); delta20-15 {decision['score20_minus_score15']:+.4f}; "
        f"decision `{decision['next_step']}`; weights `{WEIGHTS_DATASET_SUBFOLDER}/`, no LB submission."
    )
    pattern = re.compile(re.escape(marker) + r"\n- [^\n]*")
    if pattern.search(text):
        text = pattern.sub(note, text, count=1)
    else:
        heading = next(
            (line for line in text.splitlines() if line.startswith("## 14. Operational state")),
            None,
        )
        if heading is None:
            raise RuntimeError("CONTEXT.md §14 heading not found")
        text = text.replace(heading, heading + "\n" + note, 1)
    atomic_write_text(path, text.rstrip() + "\n")


def commit_and_push_reports() -> None:
    expected_paths = {
        "CONTEXT.md",
        "experiments/RESULTS.md",
        f"experiments/{EXPERIMENT}/results.json",
    }
    status_text = run_checked([*GIT, "status", "--porcelain"], cwd=PROJECT_ROOT)
    changed_paths = set()
    for line in status_text.splitlines():
        path_text = line[3:].strip()
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        changed_paths.add(path_text.replace("\\", "/"))
    unexpected = changed_paths - expected_paths
    if unexpected:
        raise RuntimeError("Refusing auto-commit because unrelated paths are modified: " + ", ".join(sorted(unexpected)))
    run_checked([*GIT, "add", "--", *sorted(expected_paths)], cwd=PROJECT_ROOT)
    staged = subprocess.run([*GIT, "diff", "--cached", "--quiet"], cwd=PROJECT_ROOT)
    if staged.returncode == 1:
        message = f"Record Friend A STEP 1 honest LOEO result"
        output = run_checked([*GIT, "commit", "-m", message], cwd=PROJECT_ROOT)
        if output.strip():
            print(output.strip())
    elif staged.returncode != 0:
        raise RuntimeError("git diff --cached --quiet failed")
    output = run_checked([*GIT, "push", "origin", EXPECTED_BRANCH], cwd=PROJECT_ROOT)
    if output.strip():
        print(output.strip())
    save_pipeline_state(status="complete", git_pushed=True)


if RUN_PIPELINE:
    metric_payloads = {}
    for path in sorted(EVALUATION_ROOT.glob("*/official_metrics.json")):
        payload = load_valid_metrics(path)
        if payload is not None and "checkpoint" in payload and "aggregate_node_counts" in payload:
            metric_payloads[path.parent.name] = payload
    required_labels = {
        *[f"epoch_{epoch:03d}" for epoch in MILESTONE_EPOCHS],
        "training_best",
        *REFERENCE_SPECS.keys(),
    }
    missing_labels = required_labels - set(metric_payloads)
    if missing_labels:
        raise RuntimeError("Cannot publish; evaluations are missing: " + ", ".join(sorted(missing_labels)))
    compact = {label: compact_metric(label, payload) for label, payload in metric_payloads.items()}
    candidate_labels = [f"epoch_{epoch:03d}" for epoch in MILESTONE_EPOCHS] + ["training_best"]
    official_best_label = max(
        candidate_labels,
        key=lambda label: (compact[label]["score"], -(compact[label]["epoch"] or 10**9)),
    )
    official_best = compact[official_best_label]
    selected_source = Path(metric_payloads[official_best_label]["checkpoint"]["weights"])
    config_source = selected_source.with_name("config.json")
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    selected_target = ARTIFACT_DIR / "edge_predictor_best.pth"
    config_target = ARTIFACT_DIR / "config.json"
    shutil.copy2(selected_source, selected_target)
    shutil.copy2(config_source, config_target)
    shutil.copy2(RUN_CONFIG_PATH, ARTIFACT_DIR / "run_config.json")
    shutil.copy2(RUN_DIR / "training_history.csv", ARTIFACT_DIR / "training_history.csv")
    shutil.copy2(RUN_DIR / "training_history.json", ARTIFACT_DIR / "training_history.json")
    if sha256_file(selected_source) != sha256_file(selected_target):
        raise RuntimeError("Packaged official-best checkpoint hash mismatch")

    score15 = compact["epoch_015"]["score"]
    score20 = compact["epoch_020"]["score"]
    delta20_15 = score20 - score15
    if official_best["score"] >= 0.85:
        next_step = "STEP_3_validator_usable"
    elif official_best["score"] < 0.80:
        next_step = "STEP_4_dense_labels_sparse_limit"
    else:
        next_step = "STEP_2_borderline_review_0.80_to_0.85"
    training_history = json.loads((RUN_DIR / "training_history.json").read_text(encoding="utf-8"))
    result = {
        "experiment": EXPERIMENT,
        "step": 1,
        "status": "complete_official_loeo",
        "completed_at": datetime.now().astimezone().isoformat(),
        "split": "126x6bba train -> 12x44b6 validation",
        "initialization": "scratch",
        "recipe": json.loads(RUN_CONFIG_PATH.read_text(encoding="utf-8")),
        "checkpoint_table": [compact[label] for label in candidate_labels],
        "references": {label: compact[label] for label in REFERENCE_SPECS},
        "official_best": official_best,
        "official_best_checkpoint_sha256": sha256_file(selected_target),
        "artifact_dir": str(ARTIFACT_DIR),
        "weights_dataset": WEIGHTS_DATASET,
        "weights_dataset_subfolder": WEIGHTS_DATASET_SUBFOLDER,
        "decision": {
            "score20_minus_score15": delta20_15,
            "twenty_epochs_enough_by_stop_rule": delta20_15 < 0.005,
            "best_score_gate": official_best["score"],
            "next_step": next_step,
        },
        "timing": {
            "training_gpu_seconds": sum(row["train_seconds"] + row["validation_seconds"] for row in training_history),
            "evaluation_wall_seconds": sum(row["wall_seconds"] for row in compact.values()),
        },
        "official_metric": "adjusted_edge_jaccard + 0.1 * division_jaccard",
        "leaderboard_submission": False,
    }
    atomic_write_text(RUN_DIR / "results.json", json.dumps(result, ensure_ascii=False, indent=2))
    atomic_write_text(ARTIFACT_DIR / "results.json", json.dumps(result, ensure_ascii=False, indent=2))

    if AUTO_UPLOAD:
        upload_best_weights(selected_target, config_target, official_best)
    else:
        print("BIOHUB_STEP1_AUTO_UPLOAD=0: Kaggle upload intentionally skipped")
    result["weights_uploaded"] = bool(load_pipeline_state().get("weights_uploaded"))
    atomic_write_text(RUN_DIR / "results.json", json.dumps(result, ensure_ascii=False, indent=2))
    atomic_write_text(ARTIFACT_DIR / "results.json", json.dumps(result, ensure_ascii=False, indent=2))
    tracked_results = EXPERIMENT_DIR / "results.json"
    atomic_write_text(tracked_results, json.dumps(result, ensure_ascii=False, indent=2))
    update_results_markdown(result)
    update_context(result)
    save_pipeline_state(status="reports_written", official_best_label=official_best_label)

    if AUTO_GIT:
        if AUTO_UPLOAD and not result["weights_uploaded"]:
            raise RuntimeError("Refusing to commit the final report before the requested weights upload succeeds")
        commit_and_push_reports()
    else:
        print("BIOHUB_STEP1_AUTO_GIT=0: report files were written but not committed")
    print(
        f"STEP 1 COMPLETE: best={official_best_label} score={official_best['score']:.6f}; "
        f"next={next_step}; no leaderboard submission."
    )
else:
    print("BIOHUB_STEP1_RUN_PIPELINE=0: packaging/publication intentionally skipped.")
