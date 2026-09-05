# --- Patches for scripts/train_unet_transformer.py (applied at runtime inside the Kaggle notebook) ---
# Adds:
#   --init-weights PATH        : initialise the full UNet+transformer from a checkpoint (fine-tuning)
#   --det-loss {bce,gauss_focal}: detection loss variant. gauss_focal = anisotropic Gaussian heatmap
#                                targets + CenterNet-style penalty-reduced focal loss (PAC-MAP / nnLandmark ideas)
#   --det-sigma-um FLOAT       : Gaussian sigma in microns for gauss_focal (default 2.5)
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
        "    parser.add_argument(\"--seed\", type=int, default=None)\n",
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
        "DET_LOSS_MODE = \"bce\"\nDET_SIGMA_UM = 2.5\nUSE_AMP = False\nNO_GRAD_CKPT = False\nSCALER = torch.amp.GradScaler(\"cuda\", enabled=False)\n",
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
        "    global DET_LOSS_MODE, DET_SIGMA_UM, USE_AMP, NO_GRAD_CKPT, SCALER\n"
        "    USE_AMP = bool(args.amp); NO_GRAD_CKPT = bool(args.no_grad_ckpt)\n"
        "    SCALER = torch.amp.GradScaler(\"cuda\", enabled=USE_AMP)\n"
        "    print(f\"amp={USE_AMP} no_grad_ckpt={NO_GRAD_CKPT}\", flush=True)\n",
        "amp apply",
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
]


def apply_train_patches(script_path: Path) -> None:
    script_path = Path(script_path)
    src = script_path.read_text(encoding="utf-8")
    for old, new, label in PATCHES:
        src = _replace_once(src, old, new, label)
    script_path.write_text(src, encoding="utf-8")
    print(f"applied {len(PATCHES)} train patches to {script_path}")
