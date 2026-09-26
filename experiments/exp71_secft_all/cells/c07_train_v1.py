# y3uanm v1 cell 6 (the real run). [exp71] changes: num_workers=NUM_WORKERS (v1: 0; same sample order,
# no augmentations), max_iters=MAX_ITERS from the timing probe (v1: None = one full epoch), and a hard
# wall-clock stop / DataLoader-failure path that saves the current student exactly like train() would
# (both flagged in the log and the manifest). Everything else is verbatim.
_begin_run("train", MAX_ITERS, hard_stop_s=HARD_STOP_S)
_t0 = time.monotonic()
trainer.UNetNodeTransformer = SecondaryFineTune
trainer.compute_detection_loss = sparse_detection_loss
trainer.WEIGHTS_PATH = run_dir / "weights"
try:
    model = trainer.train(
        data_dir=data_dir,
        fold=0,
        splits_file=splits_path,
        method="unet_transformer",
        n_epochs=1,
        lr=1e-5,
        batch_size=1,
        num_workers=NUM_WORKERS,
        seed=314159,
        unet_out_channels=config["unet_out_channels"],
        unet_layers=config["unet_layers"],
        downsample=tuple(config["downsample"]),
        window_size=config["window_size"],
        det_loss_weight=1.0,
        max_iters=MAX_ITERS,
        validate=False,
        augmentations=None,
        data_parallel=False,
        pool_kernel_um=float(config.get("pool_kernel_um", 5.0)),
    )
except (_WallClockStop, RuntimeError) as stop:
    if not isinstance(stop, _WallClockStop):
        if not _is_loader_failure(stop) or "model" not in _current_run:
            raise
        traceback.print_exc()
        EXP71_LOG["runs"]["train"].update(hard_stopped=True, stop_reason=f"dataloader_failure: {stop!r}")
    print(f"WARNING: {stop!r}; saving the current student state the way train() does", flush=True)
    model = _current_run["model"]
    torch.save(
        {k.replace("unet.module.", "unet.", 1): v for k, v in model.state_dict().items()},
        trainer.WEIGHTS_PATH / "unet_transformer/split_0/edge_predictor_best.pth",
    )
_end_run(time.monotonic() - _t0)
_current_run.pop("model", None)
print(f"[exp71] real run: {EXP71_LOG['runs']['train']}", flush=True)
candidate = trainer.WEIGHTS_PATH / "unet_transformer/split_0/edge_predictor_best.pth"
model.load_state_dict(torch.load(candidate, map_location="cpu", weights_only=True), strict=True)
candidate.with_name("config.json").write_text(json.dumps(config, indent=2))
print("Candidate:", candidate, "\nSHA256:", hashlib.sha256(candidate.read_bytes()).hexdigest())
