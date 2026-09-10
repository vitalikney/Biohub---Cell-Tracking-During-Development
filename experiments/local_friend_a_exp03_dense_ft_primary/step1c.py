# STEP 1c: finish/reuse the 138-video teacher and dense labels before any fine-tuning.

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

    ensure_teacher(step1c_ids, smoke_key="step1c_teacher_smoke")
    tracked_stats = EXPERIMENT_DIR / "dense_stats_138.csv"
    build_dense(
        "step1c_138",
        MANIFEST_PATH,
        "train,holdout",
        step1c_ids,
        tracked_stats,
        smoke=True,
    )

    if AUTO_UPLOAD and not (remote_teacher and remote_dense):
        upload_geff_folders(step1c_ids)
    elif not AUTO_UPLOAD:
        print("BIOHUB_DENSE_FT_AUTO_UPLOAD=0: teacher/dense upload skipped by request.")

    with tracked_stats.open(newline="", encoding="utf-8") as handle:
        dense_rows = list(csv.DictReader(handle))
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
        f"{result['teacher_recall_of_gt_5um_mean']:.4f}, dense/N_est mean "
        f"{result['n_dense_over_estimated_mean']:.3f}; dataset folders `{TEACHER_DATASET_FOLDER}/` and "
        f"`{DENSE_DATASET_FOLDER}/`; 44b6 pseudo-points are not used for training.",
        heading_prefix="## 14. Operational state",
    )
    save_state(status="step1c_complete", step1c_complete=True)
    if AUTO_GIT:
        commit_and_push(
            [tracked_stats, step1c_result_path, results_md, context_path],
            "Complete Friend A STEP 1c dense labels",
        )
    print("STEP 1c complete. No leaderboard submission was made.")
elif RUN_PIPELINE:
    print("Skipping completed STEP 1c.")
else:
    print("Dry preflight: STEP 1c was not started.")
