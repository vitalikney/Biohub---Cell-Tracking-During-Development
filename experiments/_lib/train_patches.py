# --- Patches for scripts/train_unet_transformer.py (applied at runtime inside the Kaggle notebook) ---
# Adds:
#   --init-weights PATH        : initialise the full UNet+transformer from a checkpoint (fine-tuning)
#   --det-loss {bce,gauss_focal}: detection loss variant. gauss_focal = anisotropic Gaussian heatmap
#                                targets + CenterNet-style penalty-reduced focal loss (PAC-MAP / nnLandmark ideas)
#   --det-sigma-um FLOAT       : Gaussian sigma in microns for gauss_focal (default 2.5)
#   --max-detections INT       : keep only the strongest local maxima per frame before the
#                                quadratic transformer (prevents scratch-start OOMs)
#   --lr-schedule {constant,cosine}, --min-lr FLOAT: optional epoch-level LR decay
#   --checkpoint-every INT     : additionally save numbered model weights every N epochs
#   --seed INT                 : torch/numpy seed
# Usage in notebook:  apply_train_patches(TRAIN_REPO / "scripts" / "train_unet_transformer.py")
from pathlib import Path


def _replace_once(src: str, old: str, new: str, label: str) -> str:
    n = src.count(old)
    if n != 1:
        raise RuntimeError(f"patch '{label}': expected exactly 1 occurrence, found {n}")
    return src.replace(old, new)


GAUSS_LOSS_CODE = '''
# ---- exp patches: detection loss variants -----------------------------------
DET_LOSS_MODE = "bce"
DET_SIGMA_UM = 2.5


def _gaussian_1d(sigma_vox: float, device) -> torch.Tensor:
    sigma_vox = max(float(sigma_vox), 1e-3)
    r = max(1, int(round(3.0 * sigma_vox)))
    x = torch.arange(-r, r + 1, device=device, dtype=torch.float32)
    k = torch.exp(-0.5 * (x / sigma_vox) ** 2)
    return k / k.max()  # peak = 1 so a lone point keeps target 1 at its centre


def _gaussian_heatmap(points: torch.Tensor, voxel_size, sigma_um: float) -> torch.Tensor:
    """points: (B, Z, Y, X) binary. Returns soft target in [0, 1] with anisotropic Gaussian blobs."""
    B = points.shape[0]
    h = points[:, None].float()  # (B,1,Z,Y,X)
    for axis, vs in enumerate(voxel_size):
        k = _gaussian_1d(sigma_um / float(vs), points.device)
        r = k.numel() // 2
        shape = [1, 1, 1, 1, 1]
        shape[2 + axis] = k.numel()
        pad = [0, 0, 0, 0, 0, 0]
        pad[2 * (2 - axis)] = r
        pad[2 * (2 - axis) + 1] = r
        h = F.conv3d(F.pad(h, pad), k.reshape(shape))
    return h[:, 0].clamp(max=1.0)


def compute_detection_loss_gauss_focal(
    det_logits: torch.Tensor,
    coords: torch.Tensor,
    mask: torch.Tensor,
    neg_weight: float,
    voxel_size,
    sigma_um: float,
    alpha: float = 2.0,
    beta: float = 4.0,
) -> torch.Tensor:
    """CenterNet-style loss on Gaussian heatmap targets, per-sample normalised like the BCE variant.

    pos (target == 1):   (1-p)^alpha * -log(p)                  / n_pos
    neg (target  < 1):   (1-t)^beta * p^alpha * -log(1-p)       * neg_weight / n_neg
    The neg_weight keeps the positive-unlabeled down-weighting of unannotated nuclei.
    """
    B = det_logits.shape[0]
    spatial = det_logits.shape[2:]
    logits = det_logits[:, 0]
    points = torch.zeros_like(logits)
    nt = mask.sum(dim=1).long()
    for b in range(B):
        n_gt = int(nt[b])
        if n_gt <= 0:
            continue
        gt = coords[b, :n_gt]
        zi = gt[:, 0].long().clamp(0, spatial[0] - 1)
        yi = gt[:, 1].long().clamp(0, spatial[1] - 1)
        xi = gt[:, 2].long().clamp(0, spatial[2] - 1)
        points[b, zi, yi, xi] = 1.0
    with torch.no_grad():
        target = _gaussian_heatmap(points, voxel_size, sigma_um)
    p = torch.sigmoid(logits.float()).clamp(1e-6, 1 - 1e-6)
    pos = points > 0.5
    pos_term = ((1 - p) ** alpha) * (-torch.log(p))
    neg_term = ((1 - target) ** beta) * (p ** alpha) * (-torch.log(1 - p))
    n_pos = pos.reshape(B, -1).sum(dim=1).clamp(min=1).float()
    n_neg = (pos.numel() // B - n_pos).clamp(min=1)
    pos_loss = (pos_term * pos).reshape(B, -1).sum(dim=1) / n_pos
    neg_loss = (neg_term * (~pos)).reshape(B, -1).sum(dim=1) / n_neg * neg_weight
    return (pos_loss + neg_loss).mean()


'''

PATCHES = [
    # --- DataLoader workers: avoid /dev/shm exhaustion on Kaggle (window>=3 batches are large)
    (
        "from itertools import cycle as _cycle\n",
        "from itertools import cycle as _cycle\nimport torch.multiprocessing as _tmp\n_tmp.set_sharing_strategy(\"file_system\")\n",
        "shm sharing strategy",
    ),
    # --- gauss focal loss: definitions inserted before the original compute_detection_loss
    (
        "def compute_detection_loss(\n    det_logits: torch.Tensor,\n    coords: torch.Tensor,\n    mask: torch.Tensor,\n    neg_weight: float = 0.1,\n) -> torch.Tensor:\n",
        GAUSS_LOSS_CODE
        + "def compute_detection_loss(\n    det_logits: torch.Tensor,\n    coords: torch.Tensor,\n    mask: torch.Tensor,\n    neg_weight: float = 0.1,\n    voxel_size=None,\n) -> torch.Tensor:\n"
        + "    if DET_LOSS_MODE == \"gauss_focal\" and voxel_size is not None:\n"
        + "        return compute_detection_loss_gauss_focal(det_logits, coords, mask, neg_weight, voxel_size, DET_SIGMA_UM)\n",
        "det-loss dispatch",
    ),
    # --- pass voxel_size from train_epoch
    (
        "            compute_detection_loss(\n                det_logits[i], coords[:, i], masks[:, i],\n                det_neg_weight,\n            )\n            for i in range(W)\n",
        "            compute_detection_loss(\n                det_logits[i], coords[:, i], masks[:, i],\n                det_neg_weight, voxel_size=voxel_size,\n            )\n            for i in range(W)\n",
        "det-loss voxel_size",
    ),
    # --- bound the quadratic transformer input.  A scratch detector can emit
    # thousands of random local maxima before the detection head has learned;
    # the linker attention/edge tensors then scale as O(N^2) and exhaust 16 GB.
    (
        "        peak_idx = torch.nonzero(is_peak[:, 0])\n",
        "        peak_idx = torch.nonzero(is_peak[:, 0])\n"
        "        if MAX_DETECTIONS is not None and peak_idx.numel():\n"
        "            capped_idx = []\n"
        "            for b in range(B):\n"
        "                sample_idx = torch.nonzero(peak_idx[:, 0] == b, as_tuple=False).flatten()\n"
        "                if sample_idx.numel() > MAX_DETECTIONS:\n"
        "                    sample_peaks = peak_idx[sample_idx]\n"
        "                    sample_scores = det_logits[\n"
        "                        sample_peaks[:, 0], 0, sample_peaks[:, 1],\n"
        "                        sample_peaks[:, 2], sample_peaks[:, 3]\n"
        "                    ].float()\n"
        "                    # Sparse labelled cells must survive the memory cap even before\n"
        "                    # the scratch detector has learned to rank them above random peaks.\n"
        "                    nt = int(mask[b].sum().item())\n"
        "                    if nt > 0:\n"
        "                        det_xyz = sample_peaks[:, 1:].float()\n"
        "                        gt_xyz = gt_coords[b, :nt]\n"
        "                        cap_dists = torch.cdist(\n"
        "                            det_xyz * vs if vs is not None else det_xyz,\n"
        "                            gt_xyz * vs if vs is not None else gt_xyz,\n"
        "                        )\n"
        "                        protected = cap_dists.min(dim=1).values <= max_match_distance\n"
        "                        sample_scores = sample_scores.clone()\n"
        "                        sample_scores[protected] = torch.inf\n"
        "                    keep = torch.topk(sample_scores, MAX_DETECTIONS, sorted=False).indices\n"
        "                    sample_idx = sample_idx[keep]\n"
        "                capped_idx.append(sample_idx)\n"
        "            peak_idx = peak_idx[torch.cat(capped_idx)] if capped_idx else peak_idx[:0]\n",
        "max detections per frame",
    ),
    # --- init weights: train() signature
    (
        "    pool_kernel_um: float = 5.0,\n    data_parallel: bool = True,\n) -> UNetNodeTransformer:\n",
        "    pool_kernel_um: float = 5.0,\n    data_parallel: bool = True,\n    init_weights: Path | None = None,\n) -> UNetNodeTransformer:\n",
        "init-weights signature",
    ),
    # --- init weights: load after model creation (before DataParallel wrap)
    (
        "    model = UNetNodeTransformer(\n        unet=unet,\n        unet_out_channels=unet_out_channels,\n        pos_feat_dim=pos_feat_dim,\n    ).to(device)\n",
        "    model = UNetNodeTransformer(\n        unet=unet,\n        unet_out_channels=unet_out_channels,\n        pos_feat_dim=pos_feat_dim,\n    ).to(device)\n"
        "    if init_weights is not None:\n"
        "        _state = torch.load(init_weights, map_location=\"cpu\", weights_only=True)\n"
        "        _state = {k.replace(\"unet.module.\", \"unet.\", 1): v for k, v in _state.items()}\n"
        "        _missing, _unexpected = model.load_state_dict(_state, strict=False)\n"
        "        print(f\"  init weights {init_weights}: {len(_missing)} missing, {len(_unexpected)} unexpected\", flush=True)\n",
        "init-weights load",
    ),
    # --- CLI args
    (
        "    parser.add_argument(\"--single-gpu\", dest=\"data_parallel\", action=\"store_false\",\n                        help=\"Disable multi-GPU; train on cuda:0 only.\")\n",
        "    parser.add_argument(\"--single-gpu\", dest=\"data_parallel\", action=\"store_false\",\n                        help=\"Disable multi-GPU; train on cuda:0 only.\")\n"
        "    parser.add_argument(\"--init-weights\", type=str, default=None, help=\"Full model checkpoint to fine-tune from.\")\n"
        "    parser.add_argument(\"--det-loss\", type=str, default=\"bce\", choices=[\"bce\", \"gauss_focal\"])\n"
        "    parser.add_argument(\"--det-sigma-um\", type=float, default=2.5)\n"
        "    parser.add_argument(\"--seed\", type=int, default=None)\n"
        "    parser.add_argument(\"--max-detections\", type=int, default=0,\n"
        "                        help=\"Keep the strongest local maxima per frame before transformer linking.\")\n"
        "    parser.add_argument(\"--lr-schedule\", choices=[\"constant\", \"cosine\"], default=\"constant\")\n"
        "    parser.add_argument(\"--min-lr\", type=float, default=1e-5,\n"
        "                        help=\"Final learning rate for the cosine schedule.\")\n"
        "    parser.add_argument(\"--checkpoint-every\", type=int, default=0,\n"
        "                        help=\"Save edge_predictor_epoch_NNN.pth every N epochs; 0 disables.\")\n",
        "cli args",
    ),
    # --- apply CLI args in main
    (
        "    args = parser.parse_args()\n\n    from dataspec import DATASET_PATH\n",
        "    args = parser.parse_args()\n"
        "    global DET_LOSS_MODE, DET_SIGMA_UM\n"
        "    DET_LOSS_MODE = args.det_loss\n"
        "    DET_SIGMA_UM = args.det_sigma_um\n"
        "    print(f\"det loss mode={DET_LOSS_MODE} sigma_um={DET_SIGMA_UM} init_weights={args.init_weights} seed={args.seed}\", flush=True)\n"
        "    if args.seed is not None:\n"
        "        torch.manual_seed(args.seed); np.random.seed(args.seed)\n\n"
        "    from dataspec import DATASET_PATH\n",
        "main apply args",
    ),
    # --- pass init_weights + seed into train()
    (
        "        train(\n            data_dir=data_dir,\n            fold=fold,\n",
        "        train(\n            init_weights=Path(args.init_weights) if args.init_weights else None,\n            seed=args.seed,\n            data_dir=data_dir,\n            fold=fold,\n",
        "train() call",
    ),
    # ================= speed: AMP (fp16 autocast + GradScaler) and optional no-grad-checkpointing =================
    (
        "DET_LOSS_MODE = \"bce\"\nDET_SIGMA_UM = 2.5\n",
        "DET_LOSS_MODE = \"bce\"\nDET_SIGMA_UM = 2.5\nMAX_DETECTIONS = None\nLR_SCHEDULE = \"constant\"\nMIN_LR = 1e-5\nCHECKPOINT_EVERY = 0\nUSE_AMP = False\nNO_GRAD_CKPT = False\nSCALER = torch.amp.GradScaler(\"cuda\", enabled=False)\n",
        "amp globals",
    ),
    (
        "    parser.add_argument(\"--seed\", type=int, default=None)\n",
        "    parser.add_argument(\"--seed\", type=int, default=None)\n"
        "    parser.add_argument(\"--amp\", action=\"store_true\", help=\"fp16 autocast for UNet/transformer forward + GradScaler\")\n"
        "    parser.add_argument(\"--no-grad-ckpt\", action=\"store_true\", help=\"disable UNet gradient checkpointing (faster, more memory)\")\n",
        "amp cli",
    ),
    (
        "    global DET_LOSS_MODE, DET_SIGMA_UM\n",
        "    global DET_LOSS_MODE, DET_SIGMA_UM, MAX_DETECTIONS, LR_SCHEDULE, MIN_LR, CHECKPOINT_EVERY, USE_AMP, NO_GRAD_CKPT, SCALER\n"
        "    USE_AMP = bool(args.amp); NO_GRAD_CKPT = bool(args.no_grad_ckpt)\n"
        "    MAX_DETECTIONS = int(args.max_detections) if args.max_detections > 0 else None\n"
        "    LR_SCHEDULE = args.lr_schedule; MIN_LR = float(args.min_lr)\n"
        "    CHECKPOINT_EVERY = int(args.checkpoint_every)\n"
        "    if CHECKPOINT_EVERY < 0:\n"
        "        raise ValueError(f\"--checkpoint-every must be non-negative, got {CHECKPOINT_EVERY}\")\n"
        "    if LR_SCHEDULE == \"cosine\" and (MIN_LR < 0 or MIN_LR > args.lr):\n"
        "        raise ValueError(f\"--min-lr must be between 0 and --lr ({args.lr}), got {MIN_LR}\")\n"
        "    SCALER = torch.amp.GradScaler(\"cuda\", enabled=USE_AMP)\n"
        "    print(f\"amp={USE_AMP} no_grad_ckpt={NO_GRAD_CKPT} max_detections={MAX_DETECTIONS} lr_schedule={LR_SCHEDULE} min_lr={MIN_LR:g} checkpoint_every={CHECKPOINT_EVERY}\", flush=True)\n",
        "amp apply",
    ),
    # --- optional epoch-level learning-rate decay; constant remains the default
    (
        "    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)\n"
        "    print(f\"Starting training for {n_epochs} epochs (batch_size={batch_size})...\", flush=True)\n",
        "    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)\n"
        "    scheduler = (\n"
        "        torch.optim.lr_scheduler.CosineAnnealingLR(\n"
        "            optimizer, T_max=max(n_epochs, 1), eta_min=MIN_LR\n"
        "        )\n"
        "        if LR_SCHEDULE == \"cosine\" else None\n"
        "    )\n"
        "    print(\n"
        "        f\"Starting training for {n_epochs} epochs (batch_size={batch_size}, \"\n"
        "        f\"lr={lr:g}, schedule={LR_SCHEDULE}, min_lr={MIN_LR:g})...\",\n"
        "        flush=True,\n"
        "    )\n",
        "learning-rate scheduler setup",
    ),
    (
        "    for epoch in pbar:\n        t0 = time.monotonic()\n",
        "    for epoch in pbar:\n"
        "        current_lr = optimizer.param_groups[0][\"lr\"]\n"
        "        t0 = time.monotonic()\n",
        "capture epoch learning rate",
    ),
    (
        "        marker = \"*\" if is_best else \" \"\n"
        "        pbar.set_postfix(edge=f\"{edge_loss:.4f}\", det=f\"{det_loss:.4f}\", acc=f\"{test_acc:.4f}\")\n",
        "        if CHECKPOINT_EVERY and (epoch + 1) % CHECKPOINT_EVERY == 0:\n"
        "            periodic_path = output_dir / f\"edge_predictor_epoch_{epoch + 1:03d}.pth\"\n"
        "            torch.save(\n"
        "                {k.replace(\"unet.module.\", \"unet.\", 1): v for k, v in model.state_dict().items()},\n"
        "                periodic_path,\n"
        "            )\n"
        "            print(f\"  Periodic checkpoint saved: {periodic_path}\", flush=True)\n"
        "        if scheduler is not None:\n"
        "            scheduler.step()\n"
        "        marker = \"*\" if is_best else \" \"\n"
        "        pbar.set_postfix(edge=f\"{edge_loss:.4f}\", det=f\"{det_loss:.4f}\", acc=f\"{test_acc:.4f}\", lr=f\"{current_lr:.2e}\")\n",
        "periodic checkpoints and learning-rate scheduler",
    ),
    (
        "            f\"  Epoch {epoch:3d}/{n_epochs} | edge={edge_loss:.4f} | det={det_loss:.4f} | \"\n",
        "            f\"  Epoch {epoch:3d}/{n_epochs} | lr={current_lr:.2e} | edge={edge_loss:.4f} | det={det_loss:.4f} | \"\n",
        "log epoch learning rate",
    ),
    # wrap encode/predict_edges in autocast; disable checkpointing; placed right after init-weights loading
    (
        "        print(f\"  init weights {init_weights}: {len(_missing)} missing, {len(_unexpected)} unexpected\", flush=True)\n",
        "        print(f\"  init weights {init_weights}: {len(_missing)} missing, {len(_unexpected)} unexpected\", flush=True)\n"
        "    if NO_GRAD_CKPT:\n"
        "        model.unet.gradient_checkpointing = False\n"
        "        print(\"  UNet gradient checkpointing disabled\", flush=True)\n"
        "    if USE_AMP:\n"
        "        _enc_orig, _pe_orig = model.encode, model.predict_edges\n"
        "        def _enc_amp(*a, **k):\n"
        "            with torch.autocast(\"cuda\", dtype=torch.float16):\n"
        "                return _enc_orig(*a, **k)\n"
        "        def _pe_amp(*a, **k):\n"
        "            with torch.autocast(\"cuda\", dtype=torch.float16):\n"
        "                return _pe_orig(*a, **k)\n"
        "        model.encode, model.predict_edges = _enc_amp, _pe_amp\n"
        "        print(\"  AMP autocast enabled for encode/predict_edges\", flush=True)\n",
        "amp wrap",
    ),
    # losses in fp32
    (
        "    probs = torch.softmax(logits, dim=0)  # dim=0 intentional: divisions allowed, merges aren't\n",
        "    probs = torch.softmax(logits.float(), dim=0)  # dim=0 intentional: divisions allowed, merges aren't\n",
        "edge loss fp32",
    ),
    (
        "    logits = det_logits[:, 0]  # (B, Z, Y, X)\n    target = torch.zeros_like(logits)\n",
        "    logits = det_logits[:, 0].float()  # (B, Z, Y, X)\n    target = torch.zeros_like(logits)\n",
        "det loss fp32",
    ),
    # scaler-aware backward
    (
        "        optimizer.zero_grad()\n        loss.backward()\n        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)\n        optimizer.step()\n",
        "        optimizer.zero_grad()\n        SCALER.scale(loss).backward()\n        SCALER.unscale_(optimizer)\n        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)\n        SCALER.step(optimizer)\n        SCALER.update()\n",
        "scaler backward",
    ),
    # --- intensity augmentation (gain / background offset / gamma) for robustness to low-contrast, high-background videos
    (
        "DEFAULT_AUGMENTATIONS = [brightness_augment, flip_augment]\n",
        "DEFAULT_AUGMENTATIONS = [brightness_augment, flip_augment]\n"
        "AUG_INTENSITY = False\n\n"
        "def intensity_augment(imgs, coords, masks, *, rng):\n"
        "    # imgs: (W, *spatial) normalised to ~[0, 1]; simulate gain, additive haze and gamma changes\n"
        "    gain = float(rng.uniform(0.5, 1.6)); offset = float(rng.uniform(-0.15, 0.45)); gamma = float(rng.uniform(0.6, 1.5))\n"
        "    x = imgs.clamp(min=0.0)\n"
        "    x = torch.pow(x + 1e-6, gamma) * gain + offset\n"
        "    if rng.random() < 0.3:  # haze: add a smooth positive background\n"
        "        x = x + float(rng.uniform(0.2, 0.8))\n"
        "    return x, coords, masks\n",
        "intensity aug def",
    ),
    (
        "    parser.add_argument(\"--seed\", type=int, default=None)\n",
        "    parser.add_argument(\"--seed\", type=int, default=None)\n"
        "    parser.add_argument(\"--aug-intensity\", action=\"store_true\", help=\"add gain/offset/gamma intensity augmentation\")\n",
        "intensity aug cli",
    ),
    (
        "    USE_AMP = bool(args.amp); NO_GRAD_CKPT = bool(args.no_grad_ckpt)\n",
        "    USE_AMP = bool(args.amp); NO_GRAD_CKPT = bool(args.no_grad_ckpt)\n"
        "    if args.aug_intensity:\n"
        "        DEFAULT_AUGMENTATIONS.append(intensity_augment); print(\"intensity augmentation ON\", flush=True)\n",
        "intensity aug apply",
    ),
]


def apply_train_patches(script_path: Path) -> None:
    script_path = Path(script_path)
    src = script_path.read_text(encoding="utf-8")
    for old, new, label in PATCHES:
        src = _replace_once(src, old, new, label)
    script_path.write_text(src, encoding="utf-8")
    print(f"applied {len(PATCHES)} train patches to {script_path}")
