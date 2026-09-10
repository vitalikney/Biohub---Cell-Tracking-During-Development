"""Add atomic full-state epoch resume to the patched joint trainer.

Call this after ``experiments._lib.train_patches.apply_train_patches``. The
resulting ``--resume-state`` checkpoint includes model, AdamW, scheduler, AMP
scaler and deterministic RNG state. It is intentionally kept as an experiment
patch instead of changing the vendored support-pack script.
"""

from pathlib import Path


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"full-state patch {label!r}: expected one occurrence, found {count}")
    return source.replace(old, new, 1)


def apply_full_state_resume_patch(
    script_path: Path,
    *,
    state_format: str = "biohub_full_training_state_v1",
) -> None:
    script_path = Path(script_path)
    source = script_path.read_text(encoding="utf-8")
    legacy_import = "from biohub_tracking.models import SimpleNodeTransformer, TemporalUNet3D"
    if legacy_import in source:
        source = source.replace(
            legacy_import,
            "from biohub_tracking.models.simple_node_transformer import SimpleNodeTransformer\n"
            "from biohub_tracking.models.temporal_unet import TemporalUNet3D",
            1,
        )
    source = _replace_once(
        source,
        "    init_weights: Path | None = None,\n) -> UNetNodeTransformer:\n",
        "    init_weights: Path | None = None,\n    resume_state: Path | None = None,\n) -> UNetNodeTransformer:\n",
        "train signature",
    )
    source = _replace_once(
        source,
        '    parser.add_argument("--init-weights", type=str, default=None, help="Full model checkpoint to fine-tune from.")\n',
        '    parser.add_argument("--init-weights", type=str, default=None, help="Full model checkpoint to fine-tune from.")\n'
        '    parser.add_argument("--resume-state", type=str, default=None, help="Resume full model/optimizer/scheduler state.")\n',
        "resume CLI",
    )
    source = _replace_once(
        source,
        "    args = parser.parse_args()\n",
        "    args = parser.parse_args()\n"
        "    if args.init_weights and args.resume_state:\n"
        "        raise ValueError(\"--init-weights and --resume-state are mutually exclusive\")\n",
        "resume CLI guard",
    )
    source = _replace_once(
        source,
        "        train(\n            init_weights=Path(args.init_weights) if args.init_weights else None,\n            seed=args.seed,\n",
        "        train(\n            init_weights=Path(args.init_weights) if args.init_weights else None,\n"
        "            resume_state=Path(args.resume_state) if args.resume_state else None,\n            seed=args.seed,\n",
        "pass resume state",
    )
    source = _replace_once(
        source,
        "    if init_weights is not None:\n",
        "    resume_payload = None\n"
        "    start_epoch = 0\n"
        "    resume_best_score = 0.0\n"
        "    if resume_state is not None:\n"
        "        resume_payload = torch.load(resume_state, map_location=\"cpu\", weights_only=False)\n"
        f"        if resume_payload.get(\"format\") != {state_format!r}:\n"
        "            raise RuntimeError(f\"Unsupported resume-state format: {resume_payload.get('format')}\")\n"
        "        if resume_payload.get(\"model_config\") != model_config:\n"
        "            raise RuntimeError(\"Resume-state model config differs from the requested architecture\")\n"
        "        if int(resume_payload.get(\"target_epochs\", -1)) != n_epochs:\n"
        "            raise RuntimeError(\"Resume-state target epoch count differs from --epochs\")\n"
        "        start_epoch = int(resume_payload[\"completed_epochs\"])\n"
        "        if not 0 <= start_epoch <= n_epochs:\n"
        "            raise RuntimeError(f\"Invalid completed epoch count in resume state: {start_epoch}\")\n"
        "        resume_best_score = float(resume_payload[\"best_score\"])\n"
        "        missing, unexpected = model.load_state_dict(resume_payload[\"model_state\"], strict=True)\n"
        "        if missing or unexpected:\n"
        "            raise RuntimeError(\"Resume-state model keys do not match\")\n"
        "        print(f\"  loaded full resume state after epoch {start_epoch}/{n_epochs}\", flush=True)\n"
        "    if init_weights is not None:\n",
        "load resume model",
    )
    source = _replace_once(
        source,
        "    print(\n        f\"Starting training for {n_epochs} epochs (batch_size={batch_size}, \"\n",
        "    if resume_payload is not None:\n"
        "        optimizer.load_state_dict(resume_payload[\"optimizer_state\"])\n"
        "        if scheduler is not None and resume_payload.get(\"scheduler_state\") is not None:\n"
        "            scheduler.load_state_dict(resume_payload[\"scheduler_state\"])\n"
        "        if resume_payload.get(\"scaler_state\") is not None:\n"
        "            SCALER.load_state_dict(resume_payload[\"scaler_state\"])\n"
        "        if g is not None and resume_payload.get(\"dataloader_generator_state\") is not None:\n"
        "            g.set_state(resume_payload[\"dataloader_generator_state\"])\n"
        "        if resume_payload.get(\"torch_rng_state\") is not None:\n"
        "            torch.set_rng_state(resume_payload[\"torch_rng_state\"])\n"
        "        if device.type == \"cuda\" and resume_payload.get(\"cuda_rng_state_all\") is not None:\n"
        "            torch.cuda.set_rng_state_all(resume_payload[\"cuda_rng_state_all\"])\n"
        "        if resume_payload.get(\"numpy_rng_state\") is not None:\n"
        "            np.random.set_state(resume_payload[\"numpy_rng_state\"])\n"
        "        del resume_payload\n"
        "    print(\n        f\"Starting training for {n_epochs} epochs (batch_size={batch_size}, \"\n",
        "restore optimiser and RNG",
    )
    source = _replace_once(source, "    best_score = 0.0\n", "    best_score = resume_best_score\n", "best score")
    source = _replace_once(
        source,
        '    pbar = tqdm(range(n_epochs), desc="Training", disable=False)\n',
        '    pbar = tqdm(range(start_epoch, n_epochs), total=n_epochs, initial=start_epoch, desc="Training", disable=False)\n',
        "epoch range",
    )
    source = _replace_once(
        source,
        "            rng = np.random.default_rng()\n",
        "            rng = np.random.default_rng(int(np.random.randint(0, 2**32, dtype=np.uint64)))\n",
        "augmentation RNG",
    )
    source = _replace_once(
        source,
        '            f"  Epoch {epoch:3d}/{n_epochs} | lr={current_lr:.2e} | edge={edge_loss:.4f} | det={det_loss:.4f} | "\n',
        '            f"  Epoch {epoch + 1:3d}/{n_epochs} | lr={current_lr:.2e} | edge={edge_loss:.4f} | det={det_loss:.4f} | "\n',
        "one-based epoch display",
    )
    source = _replace_once(
        source,
        "        if scheduler is not None:\n            scheduler.step()\n        marker = \"*\" if is_best else \" \"\n",
        "        if scheduler is not None:\n"
        "            scheduler.step()\n"
        "        resume_payload_to_save = {\n"
        f"            \"format\": {state_format!r},\n"
        "            \"completed_epochs\": epoch + 1,\n"
        "            \"target_epochs\": n_epochs,\n"
        "            \"best_score\": best_score,\n"
        "            \"model_config\": model_config,\n"
        "            \"model_state\": {k.replace(\"unet.module.\", \"unet.\", 1): v for k, v in model.state_dict().items()},\n"
        "            \"optimizer_state\": optimizer.state_dict(),\n"
        "            \"scheduler_state\": scheduler.state_dict() if scheduler is not None else None,\n"
        "            \"scaler_state\": SCALER.state_dict(),\n"
        "            \"torch_rng_state\": torch.get_rng_state(),\n"
        "            \"cuda_rng_state_all\": torch.cuda.get_rng_state_all() if device.type == \"cuda\" else None,\n"
        "            \"numpy_rng_state\": np.random.get_state(),\n"
        "            \"dataloader_generator_state\": g.get_state() if g is not None else None,\n"
        "        }\n"
        "        resume_tmp = output_dir / \"training_state_latest.tmp\"\n"
        "        torch.save(resume_payload_to_save, resume_tmp)\n"
        "        resume_tmp.replace(output_dir / \"training_state_latest.pt\")\n"
        "        print(f\"  Resume state saved after epoch {epoch + 1}/{n_epochs}\", flush=True)\n"
        "        marker = \"*\" if is_best else \" \"\n",
        "atomic epoch state",
    )
    script_path.write_text(source, encoding="utf-8")
    print(f"applied full-state resume patch to {script_path}")
