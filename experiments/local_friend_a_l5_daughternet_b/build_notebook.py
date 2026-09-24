"""Build the Friend A L5 root notebook in the checkout and its launch copy one directory above it."""
from __future__ import annotations

import json
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NAME = "friend-a-l5-daughternet-b.ipynb"


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


cells = [
    md(
        """# Friend A — L5 DaughterNet-B (full resolution, resumable)\n
This is the current L5 task from the top block of `PROMPT_FRIEND_A.md`. It trains five models from random
initialisation on the registered leak-safe folds and returns honest held-out-fold probabilities for all 1,012,255
candidate nodes.\n
Fixed contract: full XY resolution, crop `16×64×64`, image lags `−2…+3`, classes `cont / parent / daughter`, RTX GPU.
The labels, candidate-pool hard examples, optimiser and per-source OOF readout use the current L2 v2 trainer.\n
Run the cells in order. The full run is resumable. The first build creates a roughly **25 GiB** cache outside Git.
Interrupting during the build keeps completed videos; interrupting during training keeps the last completed epoch;
scoring keeps completed videos. Rerun the same long cell to continue. Do not delete the `active_v2_pool` output directory.\n
The final hand-off is `experiments/local_friend_a_l5_daughternet_b/oof_nodes.parquet` with exactly
`stem,node_id,fold,p_cont,p_par,p_dau`. No leaderboard submission is made here.

Conservative local RTX 5070 Ti estimate for the current v2 sample set: **14–22 hours total** (cache 1–2 h, training
12–18 h, final million-node scoring 1–2 h). Early stopping may shorten training; actual epoch timings are written.
"""
    ),
    code(
        """from pathlib import Path
import sys

def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    candidates = [start, *start.parents, start / ".github-push-worktree"]
    for candidate in candidates:
        if (candidate / "PROMPT_FRIEND_A.md").is_file() and (
            candidate / "experiments" / "local_friend_a_l5_daughternet_b" / "runner.py"
        ).is_file():
            return candidate
    raise FileNotFoundError("Repository checkout not found. Start Jupyter from C:\\\\Projects\\\\CellTracker.")

PROJECT_ROOT = find_repo_root(Path.cwd())
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.local_friend_a_l5_daughternet_b.runner import (
    L5Config, clear_scoring_stop, clear_training_stop, compact_scoring_status,
    compact_training_status, preflight, request_scoring_stop, request_training_stop,
    run_node_scoring, run_smoke, run_training,
)

cfg = L5Config.from_environment(PROJECT_ROOT)
print("Repository:", PROJECT_ROOT)
print("Data:", cfg.data_dir)
print("Working outputs:", cfg.work_dir)
print("Final OOF:", cfg.final_oof_path)
cfg
"""
    ),
    md("## 1. Mandatory preflight\n\nChecks registered inputs, all 199 videos, CUDA, model shape, and immutable hashes."),
    code("preflight_report = preflight(cfg)\npreflight_report"),
    md("## 2. End-to-end smoke\n\nSix division-rich videos, two temporary folds, one epoch. Full training must not start if this fails."),
    code("clear_training_stop(cfg, smoke=True)\nsmoke_status = run_smoke(cfg)\nsmoke_status"),
    md(
        """## 3. Full five-fold training

This is the first long cell. On the first run it builds the ~25 GiB v2 crop cache, then trains one fold at a time on the
RTX 5070 Ti. Rerunning it reuses the cache, skips finished folds, and resumes an unfinished fold from `last.pt`.

To stop immediately, interrupt the kernel; the current in-memory part is lost, but completed cache videos / the last
completed epoch remain. For a clean stop after the current epoch, create the displayed `STOP_REQUESTED` file from a
second PowerShell or a second notebook kernel. Do not execute the helper below before starting unless you intend to stop.
"""
    ),
    code("clear_training_stop(cfg)\ntraining_status = run_training(cfg)\ntraining_status"),
    md("### Training status (safe to run after an interrupt)"),
    code("compact_training_status(cfg)"),
    md(
        """### Optional graceful-stop helper

Run this from a **second kernel** while training is active. It asks the worker to finish the current epoch, save
`last.pt`, and stop before another fold. The normal training cell clears this marker when you deliberately resume.
"""
    ),
    code("# request_training_stop(cfg)  # uncomment only when you want to stop\n# compact_training_status(cfg)"),
    md(
        """## 4. Score all exported candidate nodes with the held-out model

Run only after all five fold summaries exist. Each video uses the model of its registered fold (the model that did not
see that video). Results are checkpointed per video, so rerunning continues where it stopped.
"""
    ),
    code("clear_scoring_stop(cfg)\nscoring_report = run_node_scoring(cfg)\nscoring_report"),
    md("### Scoring status / optional graceful stop\n\nUse `request_scoring_stop(cfg)` from a second kernel to stop after the current video."),
    code("# request_scoring_stop(cfg)  # uncomment only when you want to stop\ncompact_scoring_status(cfg)"),
    md(
        """## Hand-off

When scoring reports `status: complete`, commit only the final
`experiments/local_friend_a_l5_daughternet_b/oof_nodes.parquet` plus a short results note. Never commit the 25 GiB cache,
fold checkpoints, per-video parquet files, or raw data. Send Vitalii the commit hash and confirm the exact row count,
schema, and SHA-256 printed by the scoring report.
"""
    ),
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

tracked = ROOT / NAME
tracked.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
launch_copy = ROOT.parent / NAME
if launch_copy.resolve() != tracked.resolve():
    shutil.copy2(tracked, launch_copy)
print(tracked)
print(launch_copy)
