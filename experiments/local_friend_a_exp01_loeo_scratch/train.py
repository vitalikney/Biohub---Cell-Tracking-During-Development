# Stream the long-running process to the notebook and to train.log.

import csv
import math
import re


def write_results(payload: dict) -> None:
    (RUN_DIR / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def terminate_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=30)


def print_subprocess_line(line: str) -> None:
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    safe_line = line.encode(encoding, errors="replace").decode(encoding, errors="replace")
    print(safe_line, end="", flush=True)


def write_training_history(epoch_rows: list[dict], output_dir: Path) -> tuple[Path, Path | None]:
    """Save per-epoch CSV and a dependency-free SVG diagnostic plot."""
    history_csv = output_dir / "history.csv"
    fields = ["epoch", "edge", "det", "test_loss", "acc", "recall", "best"]
    with history_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{**row, "epoch": row["epoch"] + 1} for row in epoch_rows])
    if not epoch_rows:
        return history_csv, None

    width, height = 960, 680
    left, right = 95.0, 900.0
    loss_top, loss_bottom = 105.0, 325.0
    metric_top, metric_bottom = 420.0, 620.0
    epochs = [row["epoch"] + 1 for row in epoch_rows]

    def x_pos(index: int) -> float:
        return (left + right) / 2 if len(epoch_rows) == 1 else left + index * (right - left) / (len(epoch_rows) - 1)

    positive_losses = [
        float(row[key]) for row in epoch_rows for key in ("edge", "det", "test_loss") if float(row[key]) > 0
    ]
    log_low = math.floor(math.log10(min(positive_losses)))
    log_high = math.ceil(math.log10(max(positive_losses)))
    if log_low == log_high:
        log_low -= 1

    def loss_y(value: float) -> float:
        value = max(float(value), 10 ** log_low)
        ratio = (log_high - math.log10(value)) / (log_high - log_low)
        return loss_top + ratio * (loss_bottom - loss_top)

    metric_values = [float(row[key]) for row in epoch_rows for key in ("recall", "best")]
    metric_low = max(0.0, min(metric_values) - 0.01)
    metric_high = min(1.0, max(metric_values) + 0.01)
    if metric_high - metric_low < 0.02:
        metric_low = max(0.0, metric_low - 0.01)
        metric_high = min(1.0, metric_high + 0.01)

    def metric_y(value: float) -> float:
        ratio = (metric_high - float(value)) / (metric_high - metric_low)
        return metric_top + ratio * (metric_bottom - metric_top)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Segoe UI,Arial,sans-serif;fill:#202124}.axis{stroke:#5f6368;stroke-width:1}.grid{stroke:#dfe3e8;stroke-width:1}.series{fill:none;stroke-width:3}.dot{stroke:#fff;stroke-width:1.5}</style>',
        '<text x="480" y="34" text-anchor="middle" font-size="21" font-weight="600">Friend A scratch LOEO training</text>',
        '<text x="480" y="58" text-anchor="middle" font-size="14" fill="#5f6368">Internal sparse-GT diagnostics — not the official competition metric</text>',
        '<text x="95" y="88" font-size="16" font-weight="600">Losses (log scale)</text>',
        '<text x="95" y="403" font-size="16" font-weight="600">Validation metrics</text>',
    ]

    for exponent in range(log_high, log_low - 1, -1):
        y = loss_y(10 ** exponent)
        svg.extend([
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="12">1e{exponent}</text>',
        ])
    for tick_index in range(5):
        value = metric_low + tick_index * (metric_high - metric_low) / 4
        y = metric_y(value)
        svg.extend([
            f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}"/>',
            f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="12">{value:.3f}</text>',
        ])
    svg.extend([
        f'<line class="axis" x1="{left}" y1="{loss_top}" x2="{left}" y2="{loss_bottom}"/>',
        f'<line class="axis" x1="{left}" y1="{loss_bottom}" x2="{right}" y2="{loss_bottom}"/>',
        f'<line class="axis" x1="{left}" y1="{metric_top}" x2="{left}" y2="{metric_bottom}"/>',
        f'<line class="axis" x1="{left}" y1="{metric_bottom}" x2="{right}" y2="{metric_bottom}"/>',
    ])

    loss_series = [("det", "Detection loss", "#d97706"), ("edge", "Edge loss", "#2563eb"), ("test_loss", "Validation loss", "#7c3aed")]
    for key, label, colour in loss_series:
        points = " ".join(f"{x_pos(i):.1f},{loss_y(row[key]):.1f}" for i, row in enumerate(epoch_rows))
        svg.append(f'<polyline class="series" points="{points}" stroke="{colour}"/>')
        for i, row in enumerate(epoch_rows):
            svg.append(f'<circle class="dot" cx="{x_pos(i):.1f}" cy="{loss_y(row[key]):.1f}" r="4" fill="{colour}"/>')

    metric_series = [("recall", "Validation recall", "#059669"), ("best", "Best internal score", "#dc2626")]
    for key, label, colour in metric_series:
        points = " ".join(f"{x_pos(i):.1f},{metric_y(row[key]):.1f}" for i, row in enumerate(epoch_rows))
        svg.append(f'<polyline class="series" points="{points}" stroke="{colour}"/>')
        for i, row in enumerate(epoch_rows):
            svg.append(f'<circle class="dot" cx="{x_pos(i):.1f}" cy="{metric_y(row[key]):.1f}" r="4" fill="{colour}"/>')

    best_index = max(range(len(epoch_rows)), key=lambda index: epoch_rows[index]["best"])
    best_x = x_pos(best_index)
    svg.extend([
        f'<line x1="{best_x:.1f}" y1="{metric_top}" x2="{best_x:.1f}" y2="{metric_bottom}" stroke="#111827" stroke-dasharray="5 5"/>',
        f'<text x="{best_x + 7:.1f}" y="{metric_top + 18:.1f}" font-size="12">saved checkpoint</text>',
    ])
    for i, epoch in enumerate(epochs):
        x = x_pos(i)
        svg.append(f'<text x="{x:.1f}" y="{metric_bottom + 25}" text-anchor="middle" font-size="12">{epoch}</text>')
    svg.append(f'<text x="{(left + right) / 2:.1f}" y="{metric_bottom + 52}" text-anchor="middle" font-size="14">Epoch</text>')

    legend_items = [*loss_series, *metric_series]
    for i, (_, label, colour) in enumerate(legend_items):
        x = 105 + (i % 3) * 260
        y = 348 + (i // 3) * 24
        svg.extend([
            f'<line x1="{x}" y1="{y}" x2="{x + 28}" y2="{y}" stroke="{colour}" stroke-width="3"/>',
            f'<text x="{x + 36}" y="{y + 5}" font-size="13">{label}</text>',
        ])
    svg.append('</svg>')
    curve_svg = output_dir / "training_curves.svg"
    curve_svg.write_text("\n".join(svg), encoding="utf-8")
    return history_csv, curve_svg


if RUN_TRAINING:
    started_at = datetime.now().astimezone()
    train_log = RUN_DIR / "train.log"
    trainer_env = {
        **os.environ,
        "BIOHUB_DATA_DIR": str(DATA_DIR),
        "PYTHONPATH": str(TRAIN_REPO / "src"),
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTORCH_ALLOC_CONF": "expandable_segments:True",
    }
    print(f"Training started at {started_at.isoformat()}", flush=True)
    with train_log.open("w", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            TRAIN_CMD,
            cwd=TRAIN_REPO,
            env=trainer_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        try:
            assert process.stdout is not None
            for line in process.stdout:
                log_handle.write(line)
                log_handle.flush()
                print_subprocess_line(line)
            return_code = process.wait()
        except KeyboardInterrupt:
            terminate_process(process)
            write_results(
                {
                    "experiment": EXPERIMENT,
                    "run_id": RUN_ID,
                    "status": "interrupted",
                    "official_metric": None,
                    "log": str(train_log),
                }
            )
            raise
        except BaseException:
            terminate_process(process)
            write_results(
                {
                    "experiment": EXPERIMENT,
                    "run_id": RUN_ID,
                    "status": "notebook_stream_failed",
                    "official_metric": None,
                    "log": str(train_log),
                }
            )
            raise

    finished_at = datetime.now().astimezone()
    wall_seconds = (finished_at - started_at).total_seconds()
    if return_code != 0:
        write_results(
            {
                "experiment": EXPERIMENT,
                "run_id": RUN_ID,
                "status": "failed",
                "return_code": return_code,
                "official_metric": None,
                "wall_seconds": wall_seconds,
                "log": str(train_log),
            }
        )
        raise RuntimeError(f"Training failed with exit code {return_code}; see {train_log}")

    checkpoint_source = TRAIN_REPO / "weights" / METHOD / "split_0" / "edge_predictor_best.pth"
    model_config_source = checkpoint_source.parent / "config.json"
    if not checkpoint_source.exists() or not model_config_source.exists():
        raise FileNotFoundError("Training ended successfully but the expected checkpoint/config pair is missing")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=False)
    checkpoint_target = ARTIFACT_DIR / "edge_predictor_best.pth"
    model_config_target = ARTIFACT_DIR / "config.json"
    shutil.copy2(checkpoint_source, checkpoint_target)
    shutil.copy2(model_config_source, model_config_target)
    shutil.copy2(RUN_DIR / "run_config.json", ARTIFACT_DIR / "run_config.json")

    log_text = train_log.read_text(encoding="utf-8", errors="replace")
    epoch_pattern = re.compile(
        r"Epoch\s+(?P<epoch>\d+)/(?P<epochs>\d+).*?edge=(?P<edge>[0-9.eE+-]+).*?"
        r"det=(?P<det>[0-9.eE+-]+).*?test_loss=(?P<test_loss>[0-9.eE+-]+).*?"
        r"acc=(?P<acc>[0-9.eE+-]+).*?recall=(?P<recall>[0-9.eE+-]+).*?best=(?P<best>[0-9.eE+-]+)"
    )
    epoch_rows = []
    for match in epoch_pattern.finditer(log_text):
        row = {"epoch": int(match.group("epoch"))}
        row.update({key: float(match.group(key)) for key in ("edge", "det", "test_loss", "acc", "recall", "best")})
        epoch_rows.append(row)

    checkpoint_sha256 = hashlib.sha256(checkpoint_target.read_bytes()).hexdigest()
    history_csv, curve_svg = write_training_history(epoch_rows, ARTIFACT_DIR)
    results = {
        "experiment": EXPERIMENT,
        "run_id": RUN_ID,
        "status": "trained_not_officially_scored",
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "wall_seconds": wall_seconds,
        "train_videos": len(train_ids),
        "validation_videos": len(holdout_ids),
        "validation_set": "LOEO-44b6",
        "initialization": "scratch",
        "checkpoint": str(checkpoint_target),
        "checkpoint_sha256": checkpoint_sha256,
        "model_config": str(model_config_target),
        "history_csv": str(history_csv),
        "training_curve_svg": str(curve_svg) if curve_svg is not None else None,
        "internal_sparse_validation": epoch_rows,
        "official_metric": None,
        "note": "Internal acc/recall is diagnostic only; Friend B must run prediction and the official metric.",
    }
    write_results(results)
    shutil.copy2(RUN_DIR / "results.json", ARTIFACT_DIR / "results.json")
    print(f"Training complete in {wall_seconds / 3600:.2f} h")
    print(f"Hand-off artifact: {ARTIFACT_DIR}")
else:
    print("BIOHUB_RUN_TRAINING=0: preflight passed; training was intentionally skipped.")
