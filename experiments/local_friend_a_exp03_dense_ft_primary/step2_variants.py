# STEP 2: same-machine sparse reference plus four dense primary fine-tunes.

if RUN_PIPELINE:
    if not load_state().get("step1c_complete"):
        raise RuntimeError("STEP 1c is incomplete; refusing to train before dense labels are verified.")

    ensure_primary_model()
    experiment_result = None
    for variant in VARIANTS:
        data_dir = DATA_DIR if variant["data"] == "sparse" else DENSE_DATA_DIR
        output = run_finetune(
            label=variant["name"],
            data_dir=data_dir,
            split_path=LOEO_TRAIN_SPLIT_PATH,
            max_iters=variant["max_iters"],
            det_neg_weight=variant["det_neg_weight"],
            aug_intensity=variant["aug_intensity"],
        )
        payload = evaluate_weights(
            variant["name"],
            output / "edge_predictor_best.pth",
            LOEO_EVAL_SPLIT_PATH,
            holdout_ids,
        )
        experiment_result = record_variant(variant, compact_metric(payload))

    assert experiment_result is not None
    sparse_score = experiment_result["variants"]["sparse_1200"]["metric"]["score"]
    dense_names = [variant["name"] for variant in VARIANTS if variant["data"] == "dense"]
    best_dense_name = max(dense_names, key=lambda name: experiment_result["variants"][name]["metric"]["score"])
    best_dense_score = experiment_result["variants"][best_dense_name]["metric"]["score"]
    delta = best_dense_score - sparse_score
    winner = best_dense_name if delta >= WINNING_DELTA else None
    experiment_result.update(
        {
            "status": "step2_complete",
            "sparse_reference_score": sparse_score,
            "best_dense_variant": best_dense_name,
            "best_dense_score": best_dense_score,
            "best_dense_delta_vs_sparse": delta,
            "winning_variant": winner,
            "step3_allowed": winner is not None,
            "completed_at": datetime.now().astimezone().isoformat(),
        }
    )
    results_path = EXPERIMENT_DIR / "results.json"
    atomic_write_text(results_path, json.dumps(experiment_result, ensure_ascii=False, indent=2))
    decision = (
        f"winner {winner}: {best_dense_score:.4f} vs sparse {sparse_score:.4f} ({delta:+.4f})"
        if winner
        else f"no dense winner: best {best_dense_name} {best_dense_score:.4f} vs sparse {sparse_score:.4f} ({delta:+.4f})"
    )
    context_path = PROJECT_ROOT / "CONTEXT.md"
    update_marked_block(
        context_path,
        "<!-- friend-a-exp03-dense-ft-primary-decision -->",
        f"- {datetime.now().date().isoformat()} Friend A primary dense-FT decision on raw LOEO-44b6: {decision}; "
        f"required delta +{WINNING_DELTA:.3f}; no LB.",
        heading_prefix="## 14. Operational state",
    )
    save_state(
        status="step2_complete",
        step2_complete=True,
        sparse_reference_score=sparse_score,
        best_dense_variant=best_dense_name,
        best_dense_score=best_dense_score,
        best_dense_delta_vs_sparse=delta,
        winning_variant=winner,
    )
    if AUTO_GIT:
        commit_and_push([results_path, context_path], "Record Friend A primary dense FT decision")
    print(f"STEP 2 complete: {decision}")
else:
    print("Dry preflight: STEP 2 fine-tunes were not started.")
