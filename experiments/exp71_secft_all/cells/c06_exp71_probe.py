# [exp71] Timing probe: the v1 training call with max_iters=PROBE_ITERS (same model, loss, data order),
# written to a throw-away weights root. Its steady-state seconds/iteration sets the real run length:
#     MAX_ITERS = min(19701, int(4.0 * 3600 / seconds_per_iter)), and never more than one pass over the loader
#     (18,707 windows on the full train set), i.e. at most v1's single epoch.
probe_weights_root = run_dir / "probe_weights"


def _run_probe(num_workers):
    _begin_run("probe", PROBE_ITERS)
    EXP71_LOG["runs"]["probe"]["num_workers"] = num_workers
    trainer.UNetNodeTransformer = SecondaryFineTune
    trainer.compute_detection_loss = sparse_detection_loss
    trainer.WEIGHTS_PATH = probe_weights_root
    t0 = time.monotonic()
    probe = trainer.train(
        data_dir=data_dir,
        fold=0,
        splits_file=splits_path,
        method="unet_transformer",
        n_epochs=1,
        lr=1e-5,
        batch_size=1,
        num_workers=num_workers,
        seed=314159,
        unet_out_channels=config["unet_out_channels"],
        unet_layers=config["unet_layers"],
        downsample=tuple(config["downsample"]),
        window_size=config["window_size"],
        det_loss_weight=1.0,
        max_iters=PROBE_ITERS,
        validate=False,
        augmentations=None,
        data_parallel=False,
        pool_kernel_um=float(config.get("pool_kernel_um", 5.0)),
    )
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
    EXP71_LOG["probe_worker_failure"] = _probe_failure
    print(f"WARNING: DataLoader failure with num_workers={NUM_WORKERS}; retrying the probe with num_workers=0", flush=True)
    NUM_WORKERS = 0
    reference.clear()
    _current_run.clear()
    gc.collect()
    torch.cuda.empty_cache()
    probe_model, probe_diffs = _run_probe(NUM_WORKERS)
EXP71_LOG["knobs"]["num_workers"] = NUM_WORKERS
assert len(probe_diffs) >= 2, f"timing probe produced too few iterations: {probe_diffs}"

probe_skip = min(PROBE_WARMUP_SKIP, len(probe_diffs) // 2)
probe_steady = probe_diffs[probe_skip:]
seconds_per_iter = statistics.fmean(probe_steady)
n_windows = int(_current_run["loader_len"])
budget_iters = int(TRAIN_BUDGET_S / seconds_per_iter)
MAX_ITERS = min(EPOCH_ITERS, budget_iters)
if n_windows != EPOCH_ITERS:
    # Expected: 18,707 on the full train set (windows with an empty GT frame are skipped). Never exceed one
    # pass over the loader (= v1's single epoch).
    print(f"NOTE: the loader has {n_windows} windows (cap {EPOCH_ITERS}); capping MAX_ITERS at one pass", flush=True)
    MAX_ITERS = min(MAX_ITERS, n_windows)
MAX_ITERS = max(1, MAX_ITERS)

EXP71_LOG["runs"]["probe"].update(
    warmup_skipped=probe_skip,
    seconds_per_iter_steady=round(seconds_per_iter, 4),
    seconds_per_iter_steady_median=round(statistics.median(probe_steady), 4),
    seconds_per_iter_steady_max=round(max(probe_steady), 4),
    warmup_diffs_s=[round(d, 3) for d in probe_diffs[:probe_skip]],
)
EXP71_LOG["max_iters_rule"] = {
    "formula": "min(19701, int(TRAIN_BUDGET_S / seconds_per_iter)), capped at the loader length",
    "train_budget_s": TRAIN_BUDGET_S,
    "seconds_per_iter": round(seconds_per_iter, 4),
    "budget_iters": budget_iters,
    "epoch_iters": EPOCH_ITERS,
    "loader_len": n_windows,
    "max_iters": MAX_ITERS,
    "epoch_fraction": round(MAX_ITERS / n_windows, 4),
    "projected_train_s": round(MAX_ITERS * seconds_per_iter, 1),
}
print(
    f"timing probe: {len(probe_diffs) + 1} it; steady {seconds_per_iter:.4f} s/it "
    f"(median {statistics.median(probe_steady):.4f}, max {max(probe_steady):.4f}, first {probe_skip} skipped); "
    f"probe wall incl. data loading {EXP71_LOG['runs']['probe']['wall_s_incl_data_loading'] / 60:.1f} min",
    flush=True,
)
print(
    f"MAX_ITERS = {MAX_ITERS}  (= min({EPOCH_ITERS}, int({TRAIN_BUDGET_S:.0f} / {seconds_per_iter:.4f}) = "
    f"{budget_iters}); {MAX_ITERS / n_windows:.1%} of one epoch; projected training "
    f"{MAX_ITERS * seconds_per_iter / 3600:.2f} h",
    flush=True,
)

# Free the probe completely: student, teacher copy, last autograd graph, loader workers, weights on disk.
del probe_model
reference.clear()
_current_run.clear()
gc.collect()
torch.cuda.empty_cache()
shutil.rmtree(probe_weights_root, ignore_errors=True)
print(f"after probe cleanup: CUDA memory allocated {torch.cuda.memory_allocated() / 2**20:.0f} MiB", flush=True)
