# STEP 3: only a winning dense recipe is extended to the fixed exp03 183-video training split.

if RUN_PIPELINE and RUN_STEP3:
    state = load_state()
    if not state.get("step2_complete"):
        raise RuntimeError("STEP 2 is incomplete; refusing to choose a recipe early.")
    winner_name = state.get("winning_variant")
    if winner_name is None:
        print("STEP 3 correctly skipped: no dense variant cleared the +0.005 gate.")
    elif state.get("step3_complete"):
        print("Skipping completed STEP 3.")
    else:
        winner = next(variant for variant in VARIANTS if variant["name"] == winner_name)
        print(f"STEP 3 winner: {winner_name}. Extending teacher/dense labels to all 199 videos.")
        ensure_teacher(all_ids, smoke_key="all199_teacher_smoke")
        tracked_stats = EXPERIMENT_DIR / "dense_stats_199.csv"
        build_dense(
            "all199",
            ALL_MANIFEST_PATH,
            "all",
            all_ids,
            tracked_stats,
            smoke=True,
        )
        if AUTO_UPLOAD:
            upload_geff_folders(all_ids)
        else:
            print("BIOHUB_DENSE_FT_AUTO_UPLOAD=0: updated 199-video GEFF upload skipped by request.")

        step3_label = f"step3_183_{winner_name}"
        output = run_finetune(
            label=step3_label,
            data_dir=DENSE_DATA_DIR,
            split_path=EXP03_TRAIN_SPLIT_PATH,
            max_iters=winner["max_iters"],
            det_neg_weight=winner["det_neg_weight"],
            aug_intensity=winner["aug_intensity"],
        )
        weights = output / "edge_predictor_best.pth"
        loeo_payload = evaluate_weights(
            f"{step3_label}_loeo44b6_mixed_overlap",
            weights,
            LOEO_EVAL_SPLIT_PATH,
            holdout_ids,
        )
        exp03_payload = evaluate_weights(
            f"{step3_label}_exp03_hold12",
            weights,
            EXP03_EVAL_SPLIT_PATH,
            exp03_holdout_ids,
        )
        loeo_metric = compact_metric(loeo_payload)
        exp03_metric = compact_metric(exp03_payload)
        if AUTO_UPLOAD:
            upload_weight_pair(
                weights,
                WINNER_WEIGHTS_FOLDER,
                f"Friend A primary dense fine-tune on exp03 183: {winner_name}",
            )
        else:
            print("BIOHUB_DENSE_FT_AUTO_UPLOAD=0: final weights upload skipped by request.")

        result = {
            "experiment": EXPERIMENT,
            "step": 3,
            "status": "complete",
            "completed_at": datetime.now().astimezone().isoformat(),
            "winning_recipe": winner,
            "train_split": "exp03 fixed 183 non-holdout videos",
            "initialization": "pilkwang primary",
            "weights": str(weights),
            "weights_sha256": sha256_file(weights),
            "dataset": WEIGHTS_DATASET,
            "dataset_folder": WINNER_WEIGHTS_FOLDER,
            "uploaded": AUTO_UPLOAD,
            "loeo_44b6_mixed_overlap_diagnostic": loeo_metric,
            "exp03_hold12_official": exp03_metric,
            "leaderboard_submission": False,
        }
        step3_result_path = EXPERIMENT_DIR / "step3_results.json"
        atomic_write_text(step3_result_path, json.dumps(result, ensure_ascii=False, indent=2))
        upsert_results_row(
            "| local Friend A exp03 STEP 3 |",
            f"| local Friend A exp03 STEP 3 | primary dense FT `{winner_name}` on fixed 183 | - | "
            f"hold12 **{exp03_metric['score']:.4f}** (edge {exp03_metric['edge_jaccard']:.4f}, "
            f"recall {exp03_metric['node_recall']:.4f}, Npred/Nest {exp03_metric['n_pred_over_n_est']:.3f}); "
            f"LOEO-44b6 mixed-overlap diagnostic {loeo_metric['score']:.4f} | GPU | "
            f"`{WINNER_WEIGHTS_FOLDER}/`; no LB |",
        )
        results_md = PROJECT_ROOT / "experiments" / "RESULTS.md"
        context_path = PROJECT_ROOT / "CONTEXT.md"
        update_marked_block(
            context_path,
            "<!-- friend-a-exp03-dense-ft-primary-step3 -->",
            f"- {datetime.now().date().isoformat()} Friend A STEP 3 complete: primary dense FT `{winner_name}` on fixed "
            f"183 videos; raw official exp03 hold12 {exp03_metric['score']:.4f}, LOEO-44b6 mixed-overlap diagnostic "
            f"{loeo_metric['score']:.4f}; weights `{WINNER_WEIGHTS_FOLDER}/`; no LB.",
            heading_prefix="## 14. Operational state",
        )
        save_state(status="step3_complete", step3_complete=True, step3_weights_sha256=sha256_file(weights))
        if AUTO_GIT:
            commit_and_push(
                [tracked_stats, step3_result_path, results_md, context_path],
                "Complete Friend A primary dense fine-tune",
            )
        print("\nMESSAGE FOR VITALII:")
        print(
            f"Friend A STEP 3 готов: `{winner_name}` дообучен от pilkwang primary на fixed exp03 183. "
            f"Raw official hold12={exp03_metric['score']:.4f}; веса и config.json: "
            f"{WEIGHTS_DATASET}/{WINNER_WEIGHTS_FOLDER}/. Можно пробовать как PRIMARY на TTA-base. "
            "На leaderboard я ничего не отправлял."
        )
elif RUN_PIPELINE:
    print("BIOHUB_DENSE_FT_RUN_STEP3=0: STEP 3 skipped by request.")
else:
    print("Dry preflight: STEP 3 was not started.")
