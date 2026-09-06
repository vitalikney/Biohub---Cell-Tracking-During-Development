# Verify and describe the exact hand-off to Friend B/Vitalii. This cell never uploads or submits anything.

results_path = RUN_DIR / "results.json"
results = json.loads(results_path.read_text(encoding="utf-8"))

if results["status"] == "trained_not_officially_scored":
    required_artifacts = [
        ARTIFACT_DIR / "edge_predictor_best.pth",
        ARTIFACT_DIR / "config.json",
        ARTIFACT_DIR / "run_config.json",
        ARTIFACT_DIR / "results.json",
    ]
    missing_artifacts = [str(path) for path in required_artifacts if not path.exists()]
    if missing_artifacts:
        raise FileNotFoundError("Incomplete hand-off artifact:\n" + "\n".join(missing_artifacts))

    handoff = {
        "experiment": EXPERIMENT,
        "status": "ready_for_friend_b_evaluation",
        "weights_dataset_subfolder": EXPERIMENT,
        "files_for_weights_dataset": [
            str(ARTIFACT_DIR / "edge_predictor_best.pth"),
            str(ARTIFACT_DIR / "config.json"),
        ],
        "supporting_files": [
            str(ARTIFACT_DIR / "run_config.json"),
            str(ARTIFACT_DIR / "results.json"),
            str(RUN_DIR / "train.log"),
        ],
        "evaluation_request": {
            "sets": ["LOEO-44b6", "48 (hold12 + divset36)"],
            "metric": "official competition metric",
            "leaderboard_submission": False,
        },
    }
    handoff_path = RUN_DIR / "handoff.json"
    handoff_path.write_text(json.dumps(handoff, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(handoff_path, ARTIFACT_DIR / "handoff.json")
    print("READY FOR HAND-OFF")
    print(f"Send this directory to Friend B/Vitalii: {ARTIFACT_DIR}")
    print(f"Then copy the measured result into experiments/{EXPERIMENT}/results.json and RESULTS.md.")
else:
    print(f"Current run status: {results['status']}. No checkpoint hand-off was created.")
