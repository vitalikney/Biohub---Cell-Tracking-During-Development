# Conditional continuation: STEP 5 on a winning dense recipe, otherwise the requested sparse-side fallback.


def write_followup_report(
    *, experiment_dir: Path, result: dict, results_key: str, results_line: str,
    context_marker: str, context_line: str, commit_message: str, extra_paths: list[Path],
) -> None:
    experiment_dir.mkdir(parents=True, exist_ok=True)
    result_path = experiment_dir / "results.json"
    atomic_write_text(result_path, json.dumps(result, ensure_ascii=False, indent=2))
    upsert_results_row(results_key, results_line)
    results_md = PROJECT_ROOT / "experiments" / "RESULTS.md"
    context_path = PROJECT_ROOT / "CONTEXT.md"
    update_marked_block(context_path, context_marker, context_line, heading_prefix="## 14. Operational state")
    if AUTO_GIT:
        commit_and_push([result_path, results_md, context_path, *extra_paths], commit_message)


if RUN_PIPELINE and load_state().get("step4_complete") and CONTINUE_AFTER_STEP4:
    step4_score = float(load_state()["step4_best_score"])
    if step4_score >= 0.70 and not load_state().get("step5_complete"):
        STEP5_EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
        remaining_ids = [dataset_id for dataset_id in all_ids if not (TEACHER_DIR / f"{dataset_id}.geff").is_dir()]
        if remaining_ids and not load_state().get("teacher_extension_smoke_complete"):
            smoke_geffs = predict_teacher_chunk(remaining_ids[:2], "teacher_extension_smoke2")
            if len(smoke_geffs) != min(2, len(remaining_ids)):
                raise RuntimeError("Full-199 teacher extension smoke has incomplete coverage")
            guarded_remove_tree(prediction_output("friend_a_dense_teacher", "teacher_extension_smoke2"), PREDICTIONS_ROOT)
            save_state(teacher_extension_smoke_complete=True)
            print("Full-199 teacher extension smoke passed.")
        ensure_teacher(all_ids, smoke_first=False)

        full_stats = STEP5_EXPERIMENT_DIR / "dense_stats_full199.csv"
        stream_command(
            [
                sys.executable, str(BUILDER_PATH), "--data-dir", str(DATA_DIR),
                "--teacher-dir", str(TEACHER_DIR), "--output-dir", str(DENSE_DATA_DIR),
                "--manifest", str(ALL_MANIFEST_PATH), "--manifest-keys", "all",
                "--dedup-radius-um", str(TEACHER_DEDUP_RADIUS_UM), "--stats-out", str(full_stats),
            ],
            cwd=PROJECT_ROOT,
            env=common_env(DATA_DIR),
            log_path=RUN_DIR / "dense_builder_full199.log",
            label="build_dense_full199",
        )
        with full_stats.open(newline="", encoding="utf-8") as handle:
            full_rows = list(csv.DictReader(handle))
        if len(full_rows) != 199:
            raise RuntimeError(f"Full dense stats contain {len(full_rows)}/199 videos")
        if AUTO_UPLOAD and not load_state().get("full199_geff_uploaded"):
            upload_geff_folders(
                {TEACHER_DATASET_FOLDER: TEACHER_DIR, DENSE_DATASET_FOLDER: DENSE_DATA_DIR},
                all_ids,
                "Friend A STEP 5 preparation: extend teacher and dense GEFF labels to all 199 videos",
            )
            save_state(full199_geff_uploaded=True)

        smoke_training("step5_full199_dense", DENSE_DATA_DIR, all_ids, DENSE_NEG_WEIGHT, 0)
        step5_output = run_training(
            "step5_full199_dense", STEP5_METHOD, DENSE_DATA_DIR, all_ids, holdout_ids,
            STEP5_EPOCHS, DENSE_NEG_WEIGHT, 0,
        )
        final_weights = step5_output / f"edge_predictor_epoch_{STEP5_EPOCHS:03d}.pth"
        if not final_weights.is_file():
            raise FileNotFoundError(final_weights)
        if AUTO_UPLOAD:
            upload_weight_pair(
                final_weights,
                STEP5_WEIGHTS_FOLDER,
                f"Friend A STEP 5: dense scratch model on all 199 videos, epoch {STEP5_EPOCHS}",
            )
        history_path, curve_path = save_training_curves(
            RUN_DIR / "step5_full199_dense_train.log", STEP5_EXPERIMENT_DIR, STEP5_EPOCHS
        )
        handoff = (
            f"Friend A STEP 5 готов: dense-модель с нуля обучена на всех 199 видео, {STEP5_EPOCHS} эпох, "
            f"финальный checkpoint загружен в `{WEIGHTS_DATASET}/{STEP5_WEIGHTS_FOLDER}/`. "
            "Честной LOEO-оценки у full199 модели нет. По плану TEAM.md можно сделать один LB probe как secondary "
            "с первым blend weight 0.5; сам ноутбук ничего на leaderboard не отправлял."
        )
        handoff_path = STEP5_EXPERIMENT_DIR / "handoff_to_vitalii.txt"
        atomic_write_text(handoff_path, handoff + "\n")
        result = {
            "experiment": STEP5_EXPERIMENT,
            "step": 5,
            "status": "complete",
            "completed_at": datetime.now().astimezone().isoformat(),
            "trigger_step4_score": step4_score,
            "train_videos": 199,
            "initialization": "scratch",
            "epochs": STEP5_EPOCHS,
            "recipe": "same dense recipe as STEP 4",
            "selected_checkpoint": f"epoch_{STEP5_EPOCHS:03d}",
            "selection_note": "final prescribed epoch; no leaky internal-best claim",
            "weights_sha256": sha256_file(final_weights),
            "weights_dataset": WEIGHTS_DATASET,
            "weights_folder": STEP5_WEIGHTS_FOLDER,
            "weights_uploaded": AUTO_UPLOAD,
            "official_validation": None,
            "leaderboard_submission": False,
            "handoff_message": handoff,
        }
        extras = [full_stats, history_path, handoff_path]
        if curve_path:
            extras.append(curve_path)
        write_followup_report(
            experiment_dir=STEP5_EXPERIMENT_DIR,
            result=result,
            results_key="| local Friend A exp04 STEP 5 |",
            results_line=(
                f"| local Friend A exp04 STEP 5 | dense scratch all199, {STEP5_EPOCHS}ep, same winning STEP 4 recipe | - | - | GPU | "
                f"final epoch {STEP5_EPOCHS}; dataset `{STEP5_WEIGHTS_FOLDER}/`; no honest LOEO after all199; no LB |"
            ),
            context_marker="<!-- friend-a-step5-full199-dense-result -->",
            context_line=(
                f"- {datetime.now().date().isoformat()} Friend A STEP 5 complete: dense scratch on all 199 videos, "
                f"{STEP5_EPOCHS} epochs; final weights `{STEP5_WEIGHTS_FOLDER}/`; no honest LOEO claim and no LB submission."
            ),
            commit_message="Complete Friend A STEP 5 full199 dense training",
            extra_paths=extras,
        )
        save_state(status="complete", step5_complete=True, handoff_message=handoff)
        print("\nMESSAGE FOR VITALII:\n" + handoff)
    elif step4_score < 0.70 and not load_state().get("fallback_complete"):
        FALLBACK_EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
        fallback_milestones = (5, 10)
        smoke_training("fallback_sparse_neg0001", DATA_DIR, train_ids, FALLBACK_NEG_WEIGHT, 1024)
        fallback_output = run_training(
            "fallback_sparse_neg0001", FALLBACK_METHOD, DATA_DIR, train_ids, holdout_ids,
            FALLBACK_EPOCHS, FALLBACK_NEG_WEIGHT, 1024,
        )
        raw_metrics = evaluate_milestones("fallback_sparse_neg0001", fallback_output, fallback_milestones)
        metrics = {label: compact_metric(label, payload) for label, payload in raw_metrics.items()}
        best_label = max(metrics, key=lambda label: (metrics[label]["score"], metrics[label]["epoch"] or -1))
        best = metrics[best_label]
        best_weights = Path(best["weights"])
        if AUTO_UPLOAD:
            upload_weight_pair(
                best_weights,
                FALLBACK_WEIGHTS_FOLDER,
                f"Friend A fallback: sparse neg-weight 0.001 official-best, score {best['score']:.6f}",
            )
        history_path, curve_path = save_training_curves(
            RUN_DIR / "fallback_sparse_neg0001_train.log", FALLBACK_EXPERIMENT_DIR, FALLBACK_EPOCHS
        )
        result = {
            "experiment": FALLBACK_EXPERIMENT,
            "step": "STEP 4 fallback",
            "status": "complete_official_loeo",
            "completed_at": datetime.now().astimezone().isoformat(),
            "trigger_step4_score": step4_score,
            "split": "126x6bba sparse train -> 12x44b6 official validation",
            "initialization": "scratch",
            "epochs": FALLBACK_EPOCHS,
            "det_neg_weight": FALLBACK_NEG_WEIGHT,
            "checkpoint_table": [metrics[label] for label in sorted(metrics)],
            "official_best": best,
            "weights_dataset": WEIGHTS_DATASET,
            "weights_folder": FALLBACK_WEIGHTS_FOLDER,
            "folder_note": "TEAM.md did not prescribe a fallback folder name; the notebook uses this explicit unique name",
            "leaderboard_submission": False,
        }
        extras = [history_path]
        if curve_path:
            extras.append(curve_path)
        write_followup_report(
            experiment_dir=FALLBACK_EXPERIMENT_DIR,
            result=result,
            results_key="| local Friend A exp04 fallback |",
            results_line=(
                f"| local Friend A exp04 fallback | sparse scratch neg-weight 0.001, 126x6bba, 10ep | - | "
                f"best **{best['score']:.4f}** ({best_label}; edge {best['edge_jaccard']:.4f}, recall "
                f"{best['node_recall']:.4f}, Npred/Nest {best['n_pred_over_n_est']:.3f}) | GPU | "
                f"trigger dense STEP4 {step4_score:.4f}<0.70; weights `{FALLBACK_WEIGHTS_FOLDER}/`; no LB |"
            ),
            context_marker="<!-- friend-a-step4-fallback-result -->",
            context_line=(
                f"- {datetime.now().date().isoformat()} Friend A sparse fallback complete: det-neg-weight 0.001, "
                f"10 epochs, best LOEO-44b6 {best['score']:.4f} ({best_label}, recall {best['node_recall']:.4f}, "
                f"N_pred/N_est {best['n_pred_over_n_est']:.3f}); weights `{FALLBACK_WEIGHTS_FOLDER}/`; no LB."
            ),
            commit_message="Complete Friend A sparse neg-weight fallback",
            extra_paths=extras,
        )
        save_state(status="complete", fallback_complete=True)
        print(f"Fallback complete: {best_label}, score={best['score']:.6f}")
    else:
        print("The conditional follow-up is already complete.")
elif RUN_PIPELINE and not CONTINUE_AFTER_STEP4:
    print("STEP 4 finished. Conditional follow-up is paused by BIOHUB_DENSE_CONTINUE_AFTER_STEP4=0.")
elif RUN_PIPELINE:
    raise RuntimeError("STEP 4 is not complete; conditional continuation cannot start")
else:
    print("Dry preflight: conditional follow-up was not started.")
