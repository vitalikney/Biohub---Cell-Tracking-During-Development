# [exp71] Run control + instrumentation. NOT part of y3uanm v1: the recipe cells above are v1 verbatim
# (plus the trainer-sha guard in the setup cell). Nothing here changes the loss, the optimiser or the data.
import datetime
import functools
import gc
import math
import os
import statistics
import traceback

# Defaults = the Kaggle run. The EXP71_* environment overrides exist only for the local CPU smoke test.
PROBE_ITERS = int(os.environ.get("EXP71_PROBE_ITERS", "40"))
PROBE_WARMUP_SKIP = int(os.environ.get("EXP71_PROBE_WARMUP_SKIP", "10"))
TRAIN_BUDGET_S = float(os.environ.get("EXP71_TRAIN_BUDGET_H", "4.0")) * 3600.0
HARD_STOP_S = float(os.environ.get("EXP71_HARD_STOP_H", "6.0")) * 3600.0
NUM_WORKERS = int(os.environ.get("EXP71_NUM_WORKERS", "4"))
DATALOADER_TIMEOUT_S = float(os.environ.get("EXP71_DATALOADER_TIMEOUT_S", "300"))
PROGRESS_EVERY = int(os.environ.get("EXP71_PROGRESS_EVERY", "500"))
EXPECTED_TRAIN_VIDEOS = int(os.environ.get("EXP71_EXPECTED_TRAIN_VIDEOS", "199"))
# Spec cap: 199 videos x 99 windows (T=100, W=2). The trainer skips windows with an empty GT frame, so the real
# loader is shorter (18,707 counted locally: 44b6 6,315 + 6bba 12,392); the probe cell also caps at one pass.
EPOCH_ITERS = 19701

assert len(names) == EXPECTED_TRAIN_VIDEOS, (len(names), EXPECTED_TRAIN_VIDEOS)
assert split["train"] == names and split["test"] == [], "exp71 trains on ALL annotated videos"

EXP71_LOG = {
    "kernel": "vitaliineibauer/biohub-exp71-secft-all",
    "recipe": "y3uanm notebook0afc5663f6 (v1): teacher-distilled fine-tune of the pilkwang seed314159 secondary",
    "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "torch": torch.__version__,
    "cuda_device": torch.cuda.get_device_name(0),
    "n_visible_gpus": torch.cuda.device_count(),
    "train_videos": len(names),
    "parent_sha256": expected_initial_sha256,
    "knobs": {
        "probe_iters": PROBE_ITERS,
        "probe_warmup_skip": PROBE_WARMUP_SKIP,
        "train_budget_s": TRAIN_BUDGET_S,
        "hard_stop_s": HARD_STOP_S,
        "num_workers": NUM_WORKERS,
        "dataloader_timeout_s": DATALOADER_TIMEOUT_S,
        "epoch_iters": EPOCH_ITERS,
        "lr": 1e-5,
        "batch_size": 1,
        "seed": 314159,
    },
    "runs": {},
}
_current_run = {}


class _WallClockStop(RuntimeError):
    """Raised from the batch iterator when the hard wall-clock stop of a run is reached."""


def _nocache_cycle(loader):
    """Drop-in for trainer._cycle.

    trainer._cycle is itertools.cycle, which keeps a reference to EVERY batch it yields (~0.55 MB per
    window -> ~10 GB of host RAM over 19,701 windows when max_iters is set). This version re-iterates
    the loader instead (same order on the first pass: same seeded sampler), and stamps each yielded
    batch for the timing probe, the progress lines and the hard wall-clock stop.
    """
    run = _current_run
    run["loader_len"] = len(loader)
    stamps = run["stamps"]
    while True:
        for batch in loader:
            now = time.monotonic()
            stop_at = run.get("hard_stop_at")
            if stop_at is not None and now > stop_at:
                EXP71_LOG["runs"][run["label"]].update(hard_stopped=True, stop_reason="hard_wall_clock")
                raise _WallClockStop(
                    f"{run['label']}: hard wall-clock stop after {len(stamps)} iterations"
                )
            stamps.append(now)
            k = len(stamps)
            if PROGRESS_EVERY > 0 and k % PROGRESS_EVERY == 0:
                elapsed = now - stamps[0]
                spi = elapsed / max(k - 1, 1)
                target = run.get("max_iters") or k
                print(
                    f"[exp71] {run['label']}: it {k}/{target} | {elapsed / 60:.1f} min | "
                    f"{spi:.3f} s/it | eta {(target - k) * spi / 60:.1f} min",
                    flush=True,
                )
            yield batch


if not hasattr(trainer, "_exp71_orig_train_epoch"):
    trainer._exp71_orig_train_epoch = trainer.train_epoch
    trainer._exp71_orig_tqdm = trainer.tqdm
    trainer._exp71_orig_DataLoader = trainer.DataLoader


def _dataloader_with_timeout(*args, **kwargs):
    """trainer.DataLoader with a per-batch timeout when workers are used (the trainer passes timeout=0 = wait
    forever): a stuck worker then raises instead of silently burning the session up to the 12 h limit."""
    if kwargs.get("num_workers", 0) > 0 and DATALOADER_TIMEOUT_S > 0:
        kwargs.setdefault("timeout", DATALOADER_TIMEOUT_S)
    return trainer._exp71_orig_DataLoader(*args, **kwargs)


def _is_loader_failure(exc):
    """DataLoader timeouts / dead workers surface as RuntimeError at next(batch_iter), before any compute."""
    return isinstance(exc, RuntimeError) and "DataLoader" in str(exc)


def _timed_train_epoch(model, *args, **kwargs):
    """Wraps trainer.train_epoch: keeps a handle on the student (for the hard stop) and logs the epoch."""
    _current_run["model"] = model
    t0 = time.monotonic()
    out = trainer._exp71_orig_train_epoch(model, *args, **kwargs)
    stats = EXP71_LOG["runs"][_current_run["label"]]
    stats["train_epoch_wall_s"] = round(time.monotonic() - t0, 1)
    stats["avg_edge_loss"] = float(out[0])
    stats["avg_det_loss"] = float(out[1])
    return out


trainer._cycle = _nocache_cycle
trainer.train_epoch = _timed_train_epoch
trainer.DataLoader = _dataloader_with_timeout
# The trainer's tqdm bars refresh every 0.1 s on stderr (~140k updates in a 4 h run); 60 s keeps the log small.
trainer.tqdm = functools.partial(trainer._exp71_orig_tqdm, mininterval=60.0)


def _begin_run(label, max_iters, hard_stop_s=None):
    _current_run.clear()
    _current_run.update(
        label=label,
        max_iters=max_iters,
        stamps=[],
        hard_stop_at=None if hard_stop_s is None else time.monotonic() + hard_stop_s,
    )
    EXP71_LOG["runs"][label] = {"max_iters": max_iters, "hard_stopped": False, "stop_reason": None}


def _end_run(wall_s):
    """Summarise the per-iteration stamps of the current run; returns the per-iteration durations."""
    stamps = _current_run["stamps"]
    diffs = [b - a for a, b in zip(stamps, stamps[1:])]
    stats = EXP71_LOG["runs"][_current_run["label"]]
    stats["n_iters"] = len(stamps)
    stats["wall_s_incl_data_loading"] = round(wall_s, 1)
    stats["loader_len"] = _current_run.get("loader_len")
    if diffs:
        stats["seconds_per_iter_mean"] = round(statistics.fmean(diffs), 4)
        stats["seconds_per_iter_by_1000"] = [
            round(statistics.fmean(diffs[i:i + 1000]), 4) for i in range(0, len(diffs), 1000)
        ]
    return diffs


print(
    f"exp71 control: probe {PROBE_ITERS} it (skip {PROBE_WARMUP_SKIP}), budget {TRAIN_BUDGET_S / 3600:.2f} h, "
    f"hard stop {HARD_STOP_S / 3600:.2f} h, num_workers {NUM_WORKERS} (loader timeout {DATALOADER_TIMEOUT_S:.0f} s), "
    f"{len(names)} train videos",
    flush=True,
)
