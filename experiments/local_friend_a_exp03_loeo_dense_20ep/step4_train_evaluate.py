# STEP 4: scratch dense-label LOEO training, official milestone evaluation, upload, and report.


def save_training_curves(log_path: Path, experiment_dir: Path, epochs: int) -> tuple[Path, Path | None]:
    pattern = re.compile(
        r"Epoch\s+(?P<epoch>\d+)/(?P<epochs>\d+).*?lr=(?P<lr>[0-9.eE+-]+).*?"
        r"edge=(?P<edge>[0-9.eE+-]+).*?det=(?P<det>[0-9.eE+-]+).*?"
        r"test_loss=(?P<test_loss>[0-9.eE+-]+).*?acc=(?P<acc>[0-9.eE+-]+).*?"
        r"recall=(?P<recall>[0-9.eE+-]+).*?best=(?P<best>[0-9.eE+-]+)"
    )
    by_epoch = {}
    for match in pattern.finditer(log_path.read_text(encoding="utf-8", errors="replace")):
        number = int(match.group("epoch"))
        by_epoch[number] = {
            "epoch": number,
            **{name: float(match.group(name)) for name in ("lr", "edge", "det", "test_loss", "acc", "recall", "best")},
        }
    rows = [by_epoch[number] for number in sorted(by_epoch)]
    if [row["epoch"] for row in rows] != list(range(1, epochs + 1)):
        raise RuntimeError(f"Could not reconstruct complete 1..{epochs} history from {log_path}")
    csv_path = experiment_dir / "training_history.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    plot_path = experiment_dir / "learning_curves.png"
    try:
        import matplotlib.pyplot as plt

        figure, axes = plt.subplots(1, 2, figsize=(11, 4))
        axes[0].plot([row["epoch"] for row in rows], [row["edge"] for row in rows], label="edge loss")
        axes[0].plot([row["epoch"] for row in rows], [row["det"] for row in rows], label="detection loss")
        axes[0].plot([row["epoch"] for row in rows], [row["test_loss"] for row in rows], label="internal val loss")
        axes[0].set(xlabel="epoch", title="Losses")
        axes[0].legend()
        axes[1].plot([row["epoch"] for row in rows], [row["acc"] for row in rows], label="internal edge accuracy")
        axes[1].plot([row["epoch"] for row in rows], [row["recall"] for row in rows], label="internal node recall")
        axes[1].set(xlabel="epoch", ylim=(0, 1.02), title="Internal diagnostics")
        axes[1].legend()
        figure.tight_layout()
        figure.savefig(plot_path, dpi=140)
        plt.close(figure)
    except ImportError:
        plot_path = None
    return csv_path, plot_path


if RUN_PIPELINE and not load_state().get("step4_complete"):
    if not load_state().get("step1c_complete"):
        raise RuntimeError("STEP 1c is not complete; STEP 4 cannot start")
    missing_dense = [dataset_id for dataset_id in train_ids + holdout_ids if not (DENSE_DATA_DIR / f"{dataset_id}.geff").is_dir()]
    if missing_dense:
        raise FileNotFoundError(f"Dense dataset is missing {len(missing_dense)} GEFFs")

    smoke_training("step4_dense", DENSE_DATA_DIR, train_ids, DENSE_NEG_WEIGHT, 0)
    step4_output = run_training(
        "step4_dense", STEP4_METHOD, DENSE_DATA_DIR, train_ids, holdout_ids,
        STEP4_EPOCHS, DENSE_NEG_WEIGHT, 0,
    )
    checkpoint_paths = [step4_output / f"edge_predictor_epoch_{epoch:03d}.pth" for epoch in MILESTONE_EPOCHS]
    missing_checkpoints = [str(path) for path in checkpoint_paths if not path.is_file()]
    if missing_checkpoints:
        raise FileNotFoundError("STEP 4 checkpoints are missing:\n" + "\n".join(missing_checkpoints))
    raw_metrics = evaluate_milestones("step4_dense", step4_output, MILESTONE_EPOCHS)
    metrics = {label: compact_metric(label, payload) for label, payload in raw_metrics.items()}
    best_label = max(metrics, key=lambda label: (metrics[label]["score"], metrics[label]["epoch"] or -1))
    best = metrics[best_label]
    best_weights = Path(best["weights"])

    if AUTO_UPLOAD:
        upload_weight_pair(
            best_weights,
            STEP4_WEIGHTS_FOLDER,
            f"Friend A STEP 4: official-best dense LOEO checkpoint, score {best['score']:.6f}",
        )
    else:
        print("BIOHUB_DENSE_AUTO_UPLOAD=0: STEP 4 weight upload skipped.")

    history_path, curve_path = save_training_curves(RUN_DIR / "step4_dense_train.log", EXPERIMENT_DIR, STEP4_EPOCHS)
    result = {
        "experiment": EXPERIMENT,
        "step": 4,
        "status": "complete_official_loeo",
        "completed_at": datetime.now().astimezone().isoformat(),
        "split": "126x6bba dense train -> original sparse-GT 12x44b6 official validation",
        "initialization": "scratch",
        "recipe": {
            "epochs": STEP4_EPOCHS,
            "team_md_epochs": 30,
            "epoch_override": "explicit user request on 2026-09-10",
            "batch_size": BATCH_SIZE,
            "lr": LEARNING_RATE,
            "lr_schedule": "cosine",
            "min_lr": MIN_LEARNING_RATE,
            "det_neg_weight": DENSE_NEG_WEIGHT,
            "window_size": WINDOW_SIZE,
            "downsample": [1, 4, 4],
            "max_detections": 0,
            "checkpoint_every": CHECKPOINT_EVERY,
            "seed": SEED,
            "amp": True,
            "gradient_checkpointing": False,
        },
        "checkpoint_table": [metrics[label] for label in sorted(metrics)],
        "official_best": best,
        "sparse_step1_best": 0.6803,
        "improvement_over_sparse": best["score"] - 0.6803,
        "decision_gate": 0.70,
        "decision": "STEP_5_full199_dense" if best["score"] >= 0.70 else "fallback_sparse_neg_weight_0.001",
        "weights_dataset": WEIGHTS_DATASET,
        "weights_folder": STEP4_WEIGHTS_FOLDER,
        "weights_uploaded": AUTO_UPLOAD,
        "training_history": str(history_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "learning_curve": str(curve_path.relative_to(PROJECT_ROOT)).replace("\\", "/") if curve_path else None,
        "leaderboard_submission": False,
    }
    step4_result_path = EXPERIMENT_DIR / "results.json"
    atomic_write_text(step4_result_path, json.dumps(result, ensure_ascii=False, indent=2))
    upsert_results_row(
        "| local Friend A exp03 STEP 4 |",
        f"| local Friend A exp03 STEP 4 | scratch dense LOEO, 126x6bba, {STEP4_EPOCHS}ep (user override from TEAM 30), "
        f"BCE w2 ds1,4,4 cosine 1e-4->1e-5 | - | best **{best['score']:.4f}** ({best_label}; edge "
        f"{best['edge_jaccard']:.4f}, recall {best['node_recall']:.4f}, Npred/Nest {best['n_pred_over_n_est']:.3f}) | GPU | "
        f"12/12 original 44b6; decision `{result['decision']}`; weights `{STEP4_WEIGHTS_FOLDER}/`; no LB |",
    )
    results_md = PROJECT_ROOT / "experiments" / "RESULTS.md"
    context_path = PROJECT_ROOT / "CONTEXT.md"
    update_marked_block(
        context_path,
        "<!-- friend-a-step4-dense-result -->",
        f"- {datetime.now().date().isoformat()} Friend A STEP 4 complete: dense scratch {STEP4_EPOCHS}ep "
        f"(explicit user override from TEAM 30), best official LOEO-44b6 {best['score']:.4f} "
        f"({best_label}, edge {best['edge_jaccard']:.4f}, recall {best['node_recall']:.4f}, "
        f"N_pred/N_est {best['n_pred_over_n_est']:.3f}); next `{result['decision']}`; weights `{STEP4_WEIGHTS_FOLDER}/`; no LB.",
        heading_prefix="## 14. Operational state",
    )
    save_state(
        status="step4_reports_written",
        step4_complete=True,
        step4_best_label=best_label,
        step4_best_score=best["score"],
        step4_best_weights=str(best_weights),
        step4_decision=result["decision"],
    )
    if AUTO_GIT:
        commit_paths = [step4_result_path, history_path, results_md, context_path]
        if curve_path:
            commit_paths.append(curve_path)
        commit_and_push(commit_paths, "Complete Friend A STEP 4 dense LOEO")
    print(f"STEP 4 complete: {best_label} score={best['score']:.6f}; next={result['decision']}")
elif RUN_PIPELINE:
    print(f"Skipping completed STEP 4: score={load_state().get('step4_best_score')}")
else:
    print("Dry preflight: STEP 4 was not started.")
