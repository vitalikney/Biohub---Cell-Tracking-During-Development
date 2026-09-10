# STEP 1c: obtain/create the 138-video teacher, build dense labels, publish and record the step.

step1c_ids = train_ids + holdout_ids

if RUN_PIPELINE and not load_state().get("step1c_complete"):
    listing = kaggle_files()
    remote_teacher = f"{TEACHER_DATASET_FOLDER}/" in listing
    remote_dense = f"{DENSE_DATASET_FOLDER}/" in listing
    print(f"Kaggle dataset: teacher={remote_teacher}, dense={remote_dense}")

    if remote_teacher or remote_dense:
        snapshot = download_dataset_snapshot()
        if remote_teacher:
            restore_geff_folder(snapshot, TEACHER_DATASET_FOLDER, TEACHER_DIR, step1c_ids)
        if remote_dense:
            restore_geff_folder(snapshot, DENSE_DATASET_FOLDER, DENSE_DATA_DIR, step1c_ids)

    if not remote_teacher:
        ensure_teacher(step1c_ids, smoke_first=True)

    # A two-video builder smoke precedes the full CPU build. Finished dense GEFFs are validated and reused.
    smoke_output = RUN_DIR / "dense_builder_smoke"
    smoke_stats = smoke_output / "dense_stats.csv"
    if not load_state().get("dense_builder_smoke_complete"):
        stream_command(
            [
                sys.executable, str(BUILDER_PATH), "--data-dir", str(DATA_DIR),
                "--teacher-dir", str(TEACHER_DIR), "--output-dir", str(smoke_output),
                "--manifest", str(MANIFEST_PATH), "--manifest-keys", "train,holdout",
                "--dedup-radius-um", str(TEACHER_DEDUP_RADIUS_UM),
                "--stats-out", str(smoke_stats), "--limit", "2",
            ],
            cwd=PROJECT_ROOT,
            env=common_env(DATA_DIR),
            log_path=RUN_DIR / "dense_builder_smoke.log",
            label="dense_builder_smoke2",
        )
        save_state(dense_builder_smoke_complete=True)

    tracked_stats = EXPERIMENT_DIR / "dense_stats.csv"
    stream_command(
        [
            sys.executable, str(BUILDER_PATH), "--data-dir", str(DATA_DIR),
            "--teacher-dir", str(TEACHER_DIR), "--output-dir", str(DENSE_DATA_DIR),
            "--manifest", str(MANIFEST_PATH), "--manifest-keys", "train,holdout",
            "--dedup-radius-um", str(TEACHER_DEDUP_RADIUS_UM), "--stats-out", str(tracked_stats),
        ],
        cwd=PROJECT_ROOT,
        env=common_env(DATA_DIR),
        log_path=RUN_DIR / "dense_builder.log",
        label="build_dense_138",
    )
    with tracked_stats.open(newline="", encoding="utf-8") as handle:
        dense_rows = list(csv.DictReader(handle))
    if len(dense_rows) != len(step1c_ids):
        raise RuntimeError(f"Dense stats coverage is {len(dense_rows)}/{len(step1c_ids)}")
    if any(float(row["gt_node_recall_in_dense"]) != 1.0 for row in dense_rows):
        raise RuntimeError("Dense GT recall is not exactly 1.0")

    if AUTO_UPLOAD and not (remote_teacher and remote_dense):
        upload_geff_folders(
            {TEACHER_DATASET_FOLDER: TEACHER_DIR, DENSE_DATASET_FOLDER: DENSE_DATA_DIR},
            step1c_ids,
            f"Friend A STEP 1c: teacher and dense GEFF labels for {len(step1c_ids)} LOEO videos",
        )
    elif not AUTO_UPLOAD:
        print("BIOHUB_DENSE_AUTO_UPLOAD=0: teacher/dense upload skipped by request.")

    ratios = [float(row["n_dense_over_estimated"]) for row in dense_rows]
    recalls = [float(row["teacher_recall_of_gt_5um"]) for row in dense_rows]
    result = {
        "experiment": EXPERIMENT,
        "step": "1c",
        "status": "complete",
        "completed_at": datetime.now().astimezone().isoformat(),
        "videos": len(step1c_ids),
        "train_6bba": len(train_ids),
        "diagnostic_44b6": len(holdout_ids),
        "teacher": "exp03B + pilkwang seed314159 logits ensemble",
        "teacher_det_threshold": DET_THRESHOLD,
        "teacher_use_ilp": False,
        "dense_rule": "teacher union GT; GT wins within 5 um; GT edges only",
        "teacher_recall_of_gt_5um_mean": sum(recalls) / len(recalls),
        "n_dense_over_estimated_mean": sum(ratios) / len(ratios),
        "n_dense_over_estimated_min": min(ratios),
        "n_dense_over_estimated_max": max(ratios),
        "ratio_outliers": sum(str(row["ratio_outside_0.9_1.1"]).lower() == "true" for row in dense_rows),
        "stats_csv": str(tracked_stats.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "dataset": WEIGHTS_DATASET,
        "dataset_folders": [TEACHER_DATASET_FOLDER, DENSE_DATASET_FOLDER],
        "uploaded": bool(AUTO_UPLOAD or (remote_teacher and remote_dense)),
        "leaderboard_submission": False,
    }
    step1c_result_path = EXPERIMENT_DIR / "step1c_results.json"
    atomic_write_text(step1c_result_path, json.dumps(result, ensure_ascii=False, indent=2))
    upsert_results_row(
        "| local Friend A exp03 STEP 1c |",
        f"| local Friend A exp03 STEP 1c | exp03B+seed314159 teacher (det {DET_THRESHOLD}, no ILP) -> dense GT union | - | "
        f"138 videos; teacher recall@5um mean {result['teacher_recall_of_gt_5um_mean']:.4f}; "
        f"dense/Nest mean {result['n_dense_over_estimated_mean']:.3f} | teacher GPU + CPU build | "
        f"GT recall 1.0; folders `{TEACHER_DATASET_FOLDER}/`, `{DENSE_DATASET_FOLDER}/`; no LB |",
    )
    results_md = PROJECT_ROOT / "experiments" / "RESULTS.md"
    context_path = PROJECT_ROOT / "CONTEXT.md"
    update_marked_block(
        context_path,
        "<!-- friend-a-step1c-dense-result -->",
        f"- {datetime.now().date().isoformat()} Friend A STEP 1c complete: exp03B+seed314159 teacher and dense labels "
        f"for 126 train 6bba + 12 diagnostic 44b6; teacher recall@5um mean "
        f"{result['teacher_recall_of_gt_5um_mean']:.4f}, dense/N_est mean {result['n_dense_over_estimated_mean']:.3f}; "
        f"dataset folders `{TEACHER_DATASET_FOLDER}/` and `{DENSE_DATASET_FOLDER}/`; 44b6 pseudo-points are not used for training.",
        heading_prefix="## 14. Operational state",
    )
    save_state(status="step1c_reports_written", step1c_complete=True)
    if AUTO_GIT:
        commit_and_push(
            [BUILDER_PATH, tracked_stats, step1c_result_path, results_md, context_path],
            "Complete Friend A STEP 1c dense labels",
        )
    print("STEP 1c complete. No leaderboard submission was made.")
elif RUN_PIPELINE:
    print("Skipping completed STEP 1c.")
else:
    print("Dry preflight: STEP 1c was not started.")
