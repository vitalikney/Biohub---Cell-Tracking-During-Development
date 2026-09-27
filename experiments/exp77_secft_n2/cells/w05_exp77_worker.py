# [exp77] WORKER: runs ONE recipe of exp77 on ONE GPU.
# The notebook writes this file to /kaggle/working/exp77_worker.py (build.py prepends %%writefile). The launcher cell
# then starts it once per recipe as `python -u exp77_worker.py <run_cfg.json>`, with CUDA_VISIBLE_DEVICES set to one GPU.
# The recipe code is exp71's cells c04-c07 (the y3uanm v1 recipe plus exp71's run control), kept verbatim where
# possible. Every change against exp71 is marked [exp77]:
#   - the teacher is always the ORIGINAL pilkwang parent (initial_state); the student starts from RUN_CFG["init_weights"];
#   - lr and the loader seed come from RUN_CFG;
#   - the knobs come from RUN_CFG; the hard stop also honours the launcher's absolute deadline and a stop file;
#   - .cuda() is .to(_DEVICE). This is identical on Kaggle; CPU is allowed only for the local smoke test;
#   - the student is written to <out_dir>/weights, then TRAIN_DONE.json, then a diagnostic detection proxy runs.
import copy
import datetime
import functools
import gc
import hashlib
import inspect
import json
import math
import multiprocessing
import os
import shutil
import statistics
import sys
import time
import traceback
from pathlib import Path

RUN_CFG = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
LABEL = RUN_CFG["label"]
OUT_DIR = Path(RUN_CFG["out_dir"])
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = Path(RUN_CFG["log_path"])
DONE_PATH = OUT_DIR / "TRAIN_DONE.json"
TAG = f"[exp77 {LABEL}]"

if sys.platform.startswith("linux"):
    # exp71 ran the trainer's DataLoader workers under fork, the Linux default before Python 3.14. Pin fork here:
    # the trainer's worker_init_fn is a local function, which cannot be pickled under spawn or forkserver.
    multiprocessing.set_start_method("fork", force=True)

sys.path[:0] = [RUN_CFG["repo_scripts"], RUN_CFG["repo_src"]]

import torch
import torch.nn.functional as functional

import train_unet_transformer as trainer


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


assert Path(trainer.__file__).resolve() == Path(RUN_CFG["train_script"]).resolve(), f"Loaded wrong trainer: {trainer.__file__}"
assert _sha256(trainer.__file__) == RUN_CFG["patched_train_script_sha256"], "trainer differs from the notebook's patched copy"
assert "validate" in inspect.signature(trainer.train).parameters, "Loaded trainer has no validate parameter"
ALLOW_CPU = os.environ.get("EXP77_ALLOW_CPU") == "1"  # local CPU smoke test only; never set on Kaggle
if not ALLOW_CPU:
    assert torch.cuda.is_available(), "CUDA GPU is required"
    assert torch.cuda.device_count() == 1, (
        f"expected exactly one visible GPU, got {torch.cuda.device_count()} "
        f"(CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')!r})"
    )
_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"{TAG} device {_DEVICE} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}), "
      f"CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')!r}", flush=True)

# ---- inputs (exp71 c03, with the teacher and the student init split apart) ----
config = RUN_CFG["config"]
data_dir = Path(RUN_CFG["data_dir"])
splits_path = Path(RUN_CFG["splits_path"])
names = list(RUN_CFG["names"])
split = json.loads(splits_path.read_text(encoding="utf-8"))[0]
initial_weights = Path(RUN_CFG["teacher_weights"])  # the frozen teacher = pilkwang parent 9bac2fa0 (exp71 name kept)
expected_initial_sha256 = RUN_CFG["teacher_sha256"]
assert _sha256(initial_weights) == expected_initial_sha256, "Teacher weight SHA256 mismatch"
initial_state = torch.load(initial_weights, map_location="cpu", weights_only=True)
student_init_weights = Path(RUN_CFG["init_weights"])
student_init_sha256 = RUN_CFG["init_sha256"]
assert _sha256(student_init_weights) == student_init_sha256, "Student init weight SHA256 mismatch"
student_init_state = torch.load(student_init_weights, map_location="cpu", weights_only=True)
assert list(student_init_state) == list(initial_state), "student init keys differ from the teacher"
LR = float(RUN_CFG["lr"])
SEED = int(RUN_CFG["seed"])

# ---- exp71 c04 (y3uanm v1 model + loss), verbatim except the lines marked [exp77] ----
BaseModel = trainer.UNetNodeTransformer
reference = {}
class SecondaryFineTune(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_state_dict(initial_state, strict=True)
        reference["teacher"] = copy.deepcopy(self).to(_DEVICE).eval().requires_grad_(False)  # [exp77] .cuda() -> .to(_DEVICE)
        self.load_state_dict(student_init_state, strict=True)  # [exp77] student init: n2a = exp71 student, n2b = the parent itself
        self.requires_grad_(False)
        for module in (self.unet.decoder_blocks[-1], self.unet.head, self.detect_head): module.requires_grad_(True)
    def train(self, mode=True):
        return super().train(False)
    def encode(self, imgs):
        features, logits = super().encode(imgs)
        if torch.is_grad_enabled():
            with torch.no_grad(): teacher_features, teacher_logits = reference["teacher"].encode(imgs)
            reference["logits"] = iter(teacher_logits)
            reference["feature_loss"] = functional.mse_loss(features.float(), teacher_features.float()) / teacher_features.float().square().mean().clamp_min(1e-6)
        return features, logits
def sparse_detection_loss(logits, coords, mask, neg_weight=0.01):
    """结合标注中心监督、未标注区域蒸馏与共享特征约束。"""
    teacher_prob = next(reference["logits"]).float().sigmoid()
    points = coords[mask].long().clamp_min(0).minimum(torch.tensor(logits.shape[2:], device=logits.device) - 1)
    positive = torch.zeros_like(logits, dtype=torch.bool)
    positive[mask.nonzero()[:, 0], 0, points[:, 0], points[:, 1], points[:, 2]] = True
    positive_loss = functional.softplus(-logits.float())[positive].sum() / positive.sum().clamp_min(1)
    distillation = functional.binary_cross_entropy_with_logits(logits.float(), teacher_prob, reduction="none")
    return positive_loss + 0.5 * distillation[~positive].sum() / (~positive).sum().clamp_min(1) + 0.1 * reference["feature_loss"]

# ---- exp71 c05 (run control + instrumentation); the knobs come from RUN_CFG [exp77] ----
_K = RUN_CFG["knobs"]
PROBE_ITERS = int(_K["probe_iters"])
PROBE_WARMUP_SKIP = int(_K["probe_warmup_skip"])
TRAIN_BUDGET_S = float(_K["train_budget_s"])
HARD_STOP_S = float(_K["hard_stop_s"])
NUM_WORKERS = int(_K["num_workers"])
DATALOADER_TIMEOUT_S = float(_K["dataloader_timeout_s"])
PROGRESS_EVERY = int(_K["progress_every"])
EXPECTED_TRAIN_VIDEOS = int(_K["expected_train_videos"])
DEADLINE_UNIX = float(RUN_CFG["deadline_unix"])  # [exp77] absolute end of training set by the launcher
STOP_FILE = RUN_CFG["stop_file"]  # [exp77] the launcher touches this to stop training at the next batch
# Spec cap: 199 videos x 99 windows (T=100, W=2). The trainer skips windows with an empty GT frame, so the real
# loader is shorter (18,707 on Kaggle in exp71); the probe cell also caps at one pass.
EPOCH_ITERS = 19701

assert len(names) == EXPECTED_TRAIN_VIDEOS, (len(names), EXPECTED_TRAIN_VIDEOS)
assert split["train"] == names and split["test"] == [], "exp77 trains on ALL annotated videos"

RUN_LOG = {
    "kernel": "vitaliineibauer/biohub-exp77-secft-n2",
    "label": LABEL,
    "recipe": RUN_CFG["recipe"],
    "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "torch": torch.__version__,
    "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
    "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    "n_visible_gpus": torch.cuda.device_count(),
    "train_videos": len(names),
    "teacher_sha256": expected_initial_sha256,
    "init_sha256": student_init_sha256,
    "init_desc": RUN_CFG["init_desc"],
    "knobs": {
        "probe_iters": PROBE_ITERS,
        "probe_warmup_skip": PROBE_WARMUP_SKIP,
        "train_budget_s": TRAIN_BUDGET_S,
        "hard_stop_s": HARD_STOP_S,
        "deadline_unix": DEADLINE_UNIX,
        "num_workers": NUM_WORKERS,
        "dataloader_timeout_s": DATALOADER_TIMEOUT_S,
        "epoch_iters": EPOCH_ITERS,
        "lr": LR,
        "batch_size": 1,
        "seed": SEED,
    },
    "runs": {},
}
_current_run = {}


def _write_log():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(RUN_LOG, indent=2) + "\n", encoding="utf-8")


def _excepthook(exc_type, exc, tb):  # [exp77] an uncaught error still leaves a log behind
    RUN_LOG["error"] = "".join(traceback.format_exception(exc_type, exc, tb))[-4000:]
    try:
        _write_log()
    finally:
        sys.__excepthook__(exc_type, exc, tb)


sys.excepthook = _excepthook


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
                RUN_LOG["runs"][run["label"]].update(hard_stopped=True, stop_reason="hard_wall_clock")
                raise _WallClockStop(
                    f"{run['label']}: hard wall-clock stop after {len(stamps)} iterations"
                )
            if run.get("stop_file") and os.path.exists(run["stop_file"]):  # [exp77] launcher watchdog
                RUN_LOG["runs"][run["label"]].update(hard_stopped=True, stop_reason="stop_file")
                raise _WallClockStop(
                    f"{run['label']}: stop file after {len(stamps)} iterations"
                )
            stamps.append(now)
            k = len(stamps)
            if PROGRESS_EVERY > 0 and k % PROGRESS_EVERY == 0:
                elapsed = now - stamps[0]
                spi = elapsed / max(k - 1, 1)
                target = run.get("max_iters") or k
                print(
                    f"{TAG} {run['label']}: it {k}/{target} | {elapsed / 60:.1f} min | "
                    f"{spi:.3f} s/it | eta {(target - k) * spi / 60:.1f} min",
                    flush=True,
                )
            yield batch


_orig_train_epoch = trainer.train_epoch
_orig_tqdm = trainer.tqdm
_orig_DataLoader = trainer.DataLoader


def _dataloader_with_timeout(*args, **kwargs):
    """trainer.DataLoader with a per-batch timeout when workers are used (the trainer passes timeout=0 = wait
    forever): a stuck worker then raises instead of silently burning the session up to the 12 h limit."""
    if kwargs.get("num_workers", 0) > 0 and DATALOADER_TIMEOUT_S > 0:
        kwargs.setdefault("timeout", DATALOADER_TIMEOUT_S)
    return _orig_DataLoader(*args, **kwargs)


def _is_loader_failure(exc):
    """DataLoader timeouts / dead workers surface as RuntimeError at next(batch_iter), before any compute."""
    return isinstance(exc, RuntimeError) and "DataLoader" in str(exc)


def _timed_train_epoch(model, *args, **kwargs):
    """Wraps trainer.train_epoch: keeps a handle on the student (for the hard stop) and logs the epoch."""
    _current_run["model"] = model
    t0 = time.monotonic()
    out = _orig_train_epoch(model, *args, **kwargs)
    stats = RUN_LOG["runs"][_current_run["label"]]
    stats["train_epoch_wall_s"] = round(time.monotonic() - t0, 1)
    stats["avg_edge_loss"] = float(out[0])
    stats["avg_det_loss"] = float(out[1])
    return out


trainer._cycle = _nocache_cycle
trainer.train_epoch = _timed_train_epoch
trainer.DataLoader = _dataloader_with_timeout
# The trainer's tqdm bars refresh every 0.1 s on stderr (~140k updates in a 4 h run); 60 s keeps the log small.
trainer.tqdm = functools.partial(_orig_tqdm, mininterval=60.0)


def _begin_run(label, max_iters, hard_stop_s=None, stop_file=None):
    _current_run.clear()
    _current_run.update(
        label=label,
        max_iters=max_iters,
        stamps=[],
        hard_stop_at=None if hard_stop_s is None else time.monotonic() + hard_stop_s,
        stop_file=stop_file,
    )
    RUN_LOG["runs"][label] = {"max_iters": max_iters, "hard_stopped": False, "stop_reason": None}


def _end_run(wall_s):
    """Summarise the per-iteration stamps of the current run; returns the per-iteration durations."""
    stamps = _current_run["stamps"]
    diffs = [b - a for a, b in zip(stamps, stamps[1:])]
    stats = RUN_LOG["runs"][_current_run["label"]]
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
    f"{TAG} control: lr {LR:g}, seed {SEED}, init {student_init_sha256[:8]}, teacher {expected_initial_sha256[:8]}; "
    f"probe {PROBE_ITERS} it (skip {PROBE_WARMUP_SKIP}), budget {TRAIN_BUDGET_S / 3600:.2f} h, "
    f"hard stop {HARD_STOP_S / 3600:.2f} h (deadline in {(DEADLINE_UNIX - time.time()) / 3600:.2f} h), "
    f"num_workers {NUM_WORKERS} (loader timeout {DATALOADER_TIMEOUT_S:.0f} s), {len(names)} train videos",
    flush=True,
)
_write_log()


def _train_call(num_workers, max_iters, weights_root):
    """The v1 training call (exp71 c06/c07); only lr and seed come from RUN_CFG [exp77]."""
    trainer.UNetNodeTransformer = SecondaryFineTune
    trainer.compute_detection_loss = sparse_detection_loss
    trainer.WEIGHTS_PATH = weights_root
    return trainer.train(
        data_dir=data_dir,
        fold=0,
        splits_file=splits_path,
        method="unet_transformer",
        n_epochs=1,
        lr=LR,
        batch_size=1,
        num_workers=num_workers,
        seed=SEED,
        unet_out_channels=config["unet_out_channels"],
        unet_layers=config["unet_layers"],
        downsample=tuple(config["downsample"]),
        window_size=config["window_size"],
        det_loss_weight=1.0,
        max_iters=max_iters,
        validate=False,
        augmentations=None,
        data_parallel=False,
        pool_kernel_um=float(config.get("pool_kernel_um", 5.0)),
    )


def _free_cuda():
    reference.clear()
    _current_run.clear()
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


# ---- exp71 c06: timing probe (throw-away weights root) ----
probe_weights_root = OUT_DIR / "probe_weights"


def _run_probe(num_workers):
    _begin_run("probe", PROBE_ITERS)
    RUN_LOG["runs"]["probe"]["num_workers"] = num_workers
    t0 = time.monotonic()
    probe = _train_call(num_workers, PROBE_ITERS, probe_weights_root)
    return probe, _end_run(time.monotonic() - t0)


_probe_failure = None
try:
    probe_model, probe_diffs = _run_probe(NUM_WORKERS)
except RuntimeError as exc:
    if NUM_WORKERS == 0 or not _is_loader_failure(exc):
        raise
    traceback.print_exc()
    _probe_failure = repr(exc)
if _probe_failure is not None:  # retried outside the except block so the failed loader/workers are released
    RUN_LOG["probe_worker_failure"] = _probe_failure
    print(f"{TAG} WARNING: DataLoader failure with num_workers={NUM_WORKERS}; retrying the probe with num_workers=0", flush=True)
    NUM_WORKERS = 0
    _free_cuda()
    probe_model, probe_diffs = _run_probe(NUM_WORKERS)
RUN_LOG["knobs"]["num_workers"] = NUM_WORKERS
assert len(probe_diffs) >= 2, f"timing probe produced too few iterations: {probe_diffs}"

probe_skip = min(PROBE_WARMUP_SKIP, len(probe_diffs) // 2)
probe_steady = probe_diffs[probe_skip:]
seconds_per_iter = statistics.fmean(probe_steady)
n_windows = int(_current_run["loader_len"])
# [exp77] the budget also respects the launcher's absolute deadline, minus a margin for the second data load and the
# save (it matters only for the 1-GPU sequential fallback; in parallel mode TRAIN_BUDGET_S binds)
_remaining_s = DEADLINE_UNIX - time.time()
_budget_s = min(TRAIN_BUDGET_S, _remaining_s - min(900.0, 0.1 * _remaining_s))
budget_iters = max(0, int(_budget_s / seconds_per_iter))
MAX_ITERS = min(EPOCH_ITERS, budget_iters)
if n_windows != EPOCH_ITERS:
    # Expected: 18,707 on the full train set (windows with an empty GT frame are skipped). Never exceed one
    # pass over the loader (= v1's single epoch).
    print(f"{TAG} NOTE: the loader has {n_windows} windows (cap {EPOCH_ITERS}); capping MAX_ITERS at one pass", flush=True)
    MAX_ITERS = min(MAX_ITERS, n_windows)
MAX_ITERS = max(1, MAX_ITERS)

RUN_LOG["runs"]["probe"].update(
    warmup_skipped=probe_skip,
    seconds_per_iter_steady=round(seconds_per_iter, 4),
    seconds_per_iter_steady_median=round(statistics.median(probe_steady), 4),
    seconds_per_iter_steady_max=round(max(probe_steady), 4),
    warmup_diffs_s=[round(d, 3) for d in probe_diffs[:probe_skip]],
)
RUN_LOG["max_iters_rule"] = {
    "formula": "min(19701, int(min(TRAIN_BUDGET_S, rem - min(900, 0.1*rem)) / seconds_per_iter)), rem = deadline - now; capped at the loader length",
    "train_budget_s": TRAIN_BUDGET_S,
    "budget_s_used": round(_budget_s, 1),
    "seconds_per_iter": round(seconds_per_iter, 4),
    "budget_iters": budget_iters,
    "epoch_iters": EPOCH_ITERS,
    "loader_len": n_windows,
    "max_iters": MAX_ITERS,
    "epoch_fraction": round(MAX_ITERS / n_windows, 4),
    "projected_train_s": round(MAX_ITERS * seconds_per_iter, 1),
}
print(
    f"{TAG} timing probe: {len(probe_diffs) + 1} it; steady {seconds_per_iter:.4f} s/it "
    f"(median {statistics.median(probe_steady):.4f}, max {max(probe_steady):.4f}, first {probe_skip} skipped); "
    f"probe wall incl. data loading {RUN_LOG['runs']['probe']['wall_s_incl_data_loading'] / 60:.1f} min",
    flush=True,
)
print(
    f"{TAG} MAX_ITERS = {MAX_ITERS}  (budget {_budget_s:.0f} s / {seconds_per_iter:.4f} = {budget_iters}); "
    f"{MAX_ITERS / n_windows:.1%} of one epoch; projected training {MAX_ITERS * seconds_per_iter / 3600:.2f} h",
    flush=True,
)

# Free the probe completely: student, teacher copy, last autograd graph, loader workers, weights on disk.
del probe_model
_free_cuda()
shutil.rmtree(probe_weights_root, ignore_errors=True)
if torch.cuda.is_available():
    print(f"{TAG} after probe cleanup: CUDA memory allocated {torch.cuda.memory_allocated() / 2**20:.0f} MiB", flush=True)
_write_log()

# ---- exp71 c07: the real run ----
# exp71 changes kept: num_workers=NUM_WORKERS; max_iters=MAX_ITERS from the probe; a hard wall-clock stop and a
# DataLoader-failure path that save the current student exactly like train() would.
# [exp77] The hard stop is min(HARD_STOP_S, the launcher's deadline) and it also honours the stop file.
_hard_stop_s = min(HARD_STOP_S, max(60.0, DEADLINE_UNIX - time.time()))
_begin_run("train", MAX_ITERS, hard_stop_s=_hard_stop_s, stop_file=STOP_FILE)
RUN_LOG["runs"]["train"]["hard_stop_s"] = round(_hard_stop_s, 1)
_t0 = time.monotonic()
weights_root = OUT_DIR / "weights"
try:
    model = _train_call(NUM_WORKERS, MAX_ITERS, weights_root)
except (_WallClockStop, RuntimeError) as stop:
    if not isinstance(stop, _WallClockStop):
        if not _is_loader_failure(stop) or "model" not in _current_run:
            raise
        traceback.print_exc()
        RUN_LOG["runs"]["train"].update(hard_stopped=True, stop_reason=f"dataloader_failure: {stop!r}")
    print(f"{TAG} WARNING: {stop!r}; saving the current student state the way train() does", flush=True)
    model = _current_run["model"]
    torch.save(
        {k.replace("unet.module.", "unet.", 1): v for k, v in model.state_dict().items()},
        trainer.WEIGHTS_PATH / "unet_transformer/split_0/edge_predictor_best.pth",
    )
_end_run(time.monotonic() - _t0)
_current_run.pop("model", None)
print(f"{TAG} real run: {RUN_LOG['runs']['train']}", flush=True)
candidate = trainer.WEIGHTS_PATH / "unet_transformer/split_0/edge_predictor_best.pth"
model.load_state_dict(torch.load(candidate, map_location="cpu", weights_only=True), strict=True)
candidate.with_name("config.json").write_text(json.dumps(config, indent=2))
candidate_sha256 = _sha256(candidate)
print(f"{TAG} Candidate: {candidate}\n{TAG} SHA256: {candidate_sha256}", flush=True)
RUN_LOG["candidate"] = {"path": str(candidate), "sha256": candidate_sha256}
_write_log()
# The launcher exports a student only if this marker exists and its sha matches the file.
DONE_PATH.write_text(json.dumps({
    "label": LABEL,
    "candidate": str(candidate),
    "sha256": candidate_sha256,
    "n_iters": RUN_LOG["runs"]["train"].get("n_iters"),
    "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
}, indent=2), encoding="utf-8")


# ---- exp71 c08 (diagnostic part only). The hard-assert sanity runs in the notebook process. ----
# Diagnostic only; it never blocks the export. It counts peaks of the teacher, the student init (n2a only) and the
# student on 8 fixed TRAIN windows (in-sample), with the trainer's own peak finder (detect_and_match) at p >= 0.5 and
# p >= 0.965.
def _exp77_detection_proxy(models, n_per_prefix=4):
    thresholds = {"p0.5": 0.0, "p0.965": math.log(0.965 / 0.035)}
    picks = []
    for prefix in ("44b6", "6bba"):
        group = [n for n in names if n.startswith(prefix)]
        picks += group[:: max(1, len(group) // n_per_prefix)][:n_per_prefix]
    totals = {"gt": 0}
    rows = []
    for name in picks:
        video_meta, windows = trainer.load_dataset_windows(
            data_dir / name,
            window_size=config["window_size"],
            downsample=tuple(config["downsample"]),
        )
        item = trainer.FrameWindowDataset([(video_meta, windows)])[len(windows) // 2]
        imgs = item["imgs"].to(_DEVICE, dtype=torch.float32)[None]
        coords = item["coords"].to(_DEVICE)[None]
        masks = item["masks"].to(_DEVICE)[None]
        image_shape = tuple(int(v) for v in item["image_shape"].tolist())
        voxel_size = tuple(float(v) for v in item["voxel_size"].tolist())
        with torch.no_grad():
            logits_by = {who: m.encode(imgs)[1] for who, m in models.items()}
        row = {"video": name, "t_start": int(item["t_start"]), "gt": int(masks.sum())}
        totals["gt"] += row["gt"]
        for who, logits in logits_by.items():
            for tname, tlogit in thresholds.items():
                n_det = n_hit = 0
                for i in range(imgs.shape[1]):
                    _, _, det_mask, matches = trainer.detect_and_match(
                        logits[i], coords[:, i], masks[:, i], image_shape,
                        det_threshold=tlogit,
                        pool_kernel_um=float(config.get("pool_kernel_um", 5.0)),
                        voxel_size=voxel_size,
                        frame_index=i,
                        window_size=imgs.shape[1],
                    )
                    n_det += int(det_mask.sum())
                    n_hit += int((matches[0] >= 0).sum())
                row[f"{who}_{tname}_det"] = n_det
                row[f"{who}_{tname}_gt_hit"] = n_hit
                totals[f"{who}_{tname}_det"] = totals.get(f"{who}_{tname}_det", 0) + n_det
                totals[f"{who}_{tname}_gt_hit"] = totals.get(f"{who}_{tname}_gt_hit", 0) + n_hit
        rows.append(row)
    for tname in thresholds:
        t_det = totals[f"teacher_{tname}_det"]
        parts = []
        for who in models:
            if who == "teacher":
                continue
            w_det = totals[f"{who}_{tname}_det"]
            totals[f"{who}_over_teacher_{tname}_det"] = round(w_det / max(t_det, 1), 4)
            parts.append(f"{who} {w_det} (x{w_det / max(t_det, 1):.3f}, GT hit {totals[f'{who}_{tname}_gt_hit']}/{totals['gt']})")
        print(f"{TAG}   {tname}: teacher {t_det} (GT hit {totals[f'teacher_{tname}_gt_hit']}/{totals['gt']}) -> "
              + "; ".join(parts), flush=True)
    return {"note": "in-sample train windows; trainer peak finder, not the x138 pipeline", "totals": totals, "rows": rows}


try:
    _proxy_models = {"teacher": reference["teacher"]}
    if student_init_sha256 != expected_initial_sha256:  # n2a: also show where the student started (exp71)
        _init_model = BaseModel(
            unet=trainer.TemporalUNet3D(
                in_channels=1,
                out_channels=config["unet_out_channels"],
                layers=config["unet_layers"],
            ),
            unet_out_channels=config["unet_out_channels"],
            pos_feat_dim=4 * trainer._POS_EMBED_DIM,
        )
        _init_model.load_state_dict(student_init_state)
        _proxy_models["init"] = _init_model.to(_DEVICE).eval()
    _proxy_models["student"] = model.eval()
    print(f"{TAG} detection proxy ({' vs '.join(_proxy_models)}, 8 train windows):", flush=True)
    RUN_LOG["detection_proxy"] = _exp77_detection_proxy(_proxy_models)
except Exception as exc:  # diagnostic only
    traceback.print_exc()
    RUN_LOG["detection_proxy"] = {"error": repr(exc)}

RUN_LOG["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
_write_log()
print(f"{TAG} worker done", flush=True)
