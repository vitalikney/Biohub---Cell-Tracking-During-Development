# GENERE PAR scripts/frontier/cells/_build_matrice_variant.py
# NE PAS EDITER A LA MAIN.
# Source : cell_05.py
# Variante de MESURE : emet EN PASSE la matrice de probabilites que
# le probdump recalcule dans une seconde passe GPU (77,4 s/film).
# N'affecte jamais le chassis de soumission, qui reference cell_05.py.

# Fail fast instead of silently running volumetric inference on CPU.
import torch as _torch

if not _torch.cuda.is_available():
    raise RuntimeError(
        "CUDA GPU is required for this notebook. Enable a Kaggle GPU accelerator and commit again."
    )
print("CUDA device:", _torch.cuda.get_device_name(0))
print("CUDA capability:", ".".join(map(str, _torch.cuda.get_device_capability(0))))
if _torch.cuda.get_device_capability(0)[0] < 7:
    raise RuntimeError(
        "This notebook requires a T4-or-newer CUDA device; generic P100 assignment is incompatible with the current Kaggle PyTorch CUDA build."
    )

# Apply eight-view planar detection TTA before graph prediction.
_ps = REPO_DIR / "scripts" / "predict_unet_transformer.py"
_s = _ps.read_text()
_old = """        if cfg.det_tta:
            tta_flips = [(-1,), (-2,), (-2, -1)]
            for dims in tta_flips:
                imgs_flip = imgs.flip(dims)
                _, det_flip = model.encode(imgs_flip)
                for f in range(W):
                    det_logits[f] = det_logits[f] + det_flip[f].flip(dims)
                del imgs_flip, det_flip
            for f in range(W):
                det_logits[f] = det_logits[f] / 4"""
_new = """        if cfg.det_tta:
            _nv = 1
            for dims in [(-1,), (-2,), (-2, -1)]:
                imgs_flip = imgs.flip(dims)
                _, det_flip = model.encode(imgs_flip)
                for f in range(W):
                    det_logits[f] = det_logits[f] + det_flip[f].flip(dims)
                del imgs_flip, det_flip
                _nv += 1
            for _k in (1, 3):
                imgs_rot = torch.rot90(imgs, _k, dims=(-2, -1))
                _, det_rot = model.encode(imgs_rot)
                for f in range(W):
                    det_logits[f] = det_logits[f] + torch.rot90(det_rot[f], -_k, dims=(-2, -1))
                del imgs_rot, det_rot
                _nv += 1
            imgs_t = imgs.transpose(-1, -2)
            _, det_t = model.encode(imgs_t)
            for f in range(W):
                det_logits[f] = det_logits[f] + det_t[f].transpose(-1, -2)
            del imgs_t, det_t
            _nv += 1
            imgs_at = torch.rot90(imgs, 1, dims=(-2, -1)).transpose(-1, -2)
            _, det_at = model.encode(imgs_at)
            for f in range(W):
                det_logits[f] = det_logits[f] + torch.rot90(det_at[f].transpose(-1, -2), -1, dims=(-2, -1))
            del imgs_at, det_at
            _nv += 1
            for f in range(W):
                det_logits[f] = det_logits[f] / _nv"""
if _old in _s:
    _ps.write_text(_s.replace(_old, _new))
    print("TTA patch applied (400ep spatial D4-style)")
else:
    print("TTA WARNING: block not found - using default 4-way")

# Evaluate and calibrate two temporal models on one candidate graph.
_s = _ps.read_text()
_ensemble_replacements = [
    ('    downsample: tuple[int, ...] = (1, 4, 4),\n) -> tuple[np.ndarray, list[tuple[int, int, float, float]]]:', '    downsample: tuple[int, ...] = (1, 4, 4),\n    secondary_model: UNetNodeTransformer | None = None,\n    secondary_edge_weight: float = 0.0,\n    secondary_detection_weight: float = 0.0,\n    secondary_link_mode: str = "raw",\n    secondary_mix_temperature: float = 1.0,\n    secondary_low_margin_max: float = 0.2,\n) -> tuple[np.ndarray, list[tuple[int, int, float, float]]]:'),
    ('            for f in range(W):\n                det_logits[f] = det_logits[f] / _nv\n\n        del imgs', '            for f in range(W):\n                det_logits[f] = det_logits[f] / _nv\n\n        secondary_unet_out = None\n        if secondary_model is not None:\n            secondary_unet_out, secondary_det_logits = secondary_model.encode(imgs)\n\n            if secondary_detection_weight > 0.0:\n                if cfg.det_tta:\n                    _secondary_nv = 1\n                    for dims in [(-1,), (-2,), (-2, -1)]:\n                        secondary_imgs_flip = imgs.flip(dims)\n                        _, secondary_det_flip = secondary_model.encode(secondary_imgs_flip)\n                        for f in range(W):\n                            secondary_det_logits[f] = (\n                                secondary_det_logits[f] + secondary_det_flip[f].flip(dims)\n                            )\n                        del secondary_imgs_flip, secondary_det_flip\n                        _secondary_nv += 1\n                    for _k in (1, 3):\n                        secondary_imgs_rot = torch.rot90(imgs, _k, dims=(-2, -1))\n                        _, secondary_det_rot = secondary_model.encode(secondary_imgs_rot)\n                        for f in range(W):\n                            secondary_det_logits[f] = secondary_det_logits[f] + torch.rot90(\n                                secondary_det_rot[f], -_k, dims=(-2, -1)\n                            )\n                        del secondary_imgs_rot, secondary_det_rot\n                        _secondary_nv += 1\n                    secondary_imgs_t = imgs.transpose(-1, -2)\n                    _, secondary_det_t = secondary_model.encode(secondary_imgs_t)\n                    for f in range(W):\n                        secondary_det_logits[f] = (\n                            secondary_det_logits[f] + secondary_det_t[f].transpose(-1, -2)\n                        )\n                    del secondary_imgs_t, secondary_det_t\n                    _secondary_nv += 1\n                    secondary_imgs_at = torch.rot90(\n                        imgs, 1, dims=(-2, -1)\n                    ).transpose(-1, -2)\n                    _, secondary_det_at = secondary_model.encode(secondary_imgs_at)\n                    for f in range(W):\n                        secondary_det_logits[f] = secondary_det_logits[f] + torch.rot90(\n                            secondary_det_at[f].transpose(-1, -2),\n                            -1,\n                            dims=(-2, -1),\n                        )\n                    del secondary_imgs_at, secondary_det_at\n                    _secondary_nv += 1\n                    for f in range(W):\n                        secondary_det_logits[f] = secondary_det_logits[f] / _secondary_nv\n\n                for f in range(W):\n                    primary_det = det_logits[f]\n                    secondary_det = secondary_det_logits[f]\n                    primary_mean = primary_det.mean()\n                    secondary_mean = secondary_det.mean()\n                    primary_scale = primary_det.float().std(unbiased=False).clamp_min(1e-4)\n                    secondary_scale = secondary_det.float().std(unbiased=False).clamp_min(1e-4)\n                    scale_ratio = (primary_scale / secondary_scale).clamp(0.5, 2.0)\n                    secondary_det_aligned = (\n                        (secondary_det - secondary_mean) * scale_ratio + primary_mean\n                    )\n                    det_logits[f] = (\n                        (1.0 - secondary_detection_weight) * primary_det\n                        + secondary_detection_weight * secondary_det_aligned\n                    )\n\n            del secondary_det_logits\n\n        del imgs'),
    ('            edge_logits_pair = model.predict_edges(\n                unet_feat_src, unet_feat_tgt,\n                p_coords_src * ds_arr_t, p_coords_tgt * ds_arr_t,\n                p_pos_src, p_pos_tgt,\n                p_mask_src, p_mask_tgt,\n            )  # (1, n_src, n_tgt)\n\n            raw = edge_logits_pair[0]', '            edge_logits_pair = model.predict_edges(\n                unet_feat_src, unet_feat_tgt,\n                p_coords_src * ds_arr_t, p_coords_tgt * ds_arr_t,\n                p_pos_src, p_pos_tgt,\n                p_mask_src, p_mask_tgt,\n            )  # (1, n_src, n_tgt)\n\n            if secondary_model is not None:\n                if secondary_unet_out is None:\n                    raise RuntimeError("Secondary model is loaded but its feature map is missing")\n                secondary_feat_src = secondary_model._index_features(\n                    secondary_unet_out[:, f_idx], p_coords_src, p_mask_src,\n                )\n                secondary_feat_tgt = secondary_model._index_features(\n                    secondary_unet_out[:, f_idx + 1], p_coords_tgt, p_mask_tgt,\n                )\n                secondary_logits_pair = secondary_model.predict_edges(\n                    secondary_feat_src, secondary_feat_tgt,\n                    p_coords_src * ds_arr_t, p_coords_tgt * ds_arr_t,\n                    p_pos_src, p_pos_tgt,\n                    p_mask_src, p_mask_tgt,\n                )\n\n                if secondary_link_mode == "raw":\n                    secondary_for_mix = secondary_logits_pair\n                    blend_weight = secondary_edge_weight\n                elif secondary_link_mode in {\n                    "calibrated", "adaptive", "low_margin_consensus"\n                }:\n                    primary_center = edge_logits_pair.mean(dim=1, keepdim=True)\n                    primary_scale = edge_logits_pair.float().std(\n                        dim=1, keepdim=True, unbiased=False\n                    ).clamp_min(1e-4)\n                    secondary_center = secondary_logits_pair.mean(dim=1, keepdim=True)\n                    secondary_scale = secondary_logits_pair.float().std(\n                        dim=1, keepdim=True, unbiased=False\n                    ).clamp_min(1e-4)\n                    secondary_scale_ratio = (primary_scale / secondary_scale).clamp(0.5, 2.0)\n                    secondary_for_mix = (\n                        (secondary_logits_pair - secondary_center) * secondary_scale_ratio\n                        + primary_center\n                    )\n                    if secondary_link_mode == "calibrated":\n                        blend_weight = secondary_edge_weight\n                    elif secondary_link_mode == "adaptive":\n                        if n_src >= 2:\n                            primary_probs = torch.softmax(edge_logits_pair[0], dim=0)\n                            secondary_probs = torch.softmax(secondary_for_mix[0], dim=0)\n                            primary_top2 = torch.topk(primary_probs, k=2, dim=0)\n                            secondary_top2 = torch.topk(secondary_probs, k=2, dim=0)\n                            primary_margin = primary_top2.values[0] - primary_top2.values[1]\n                            secondary_margin = secondary_top2.values[0] - secondary_top2.values[1]\n                            local_weight = (\n                                secondary_edge_weight + secondary_margin - primary_margin\n                            ).clamp(0.15, 0.75)\n                            same_parent = primary_top2.indices[0].eq(\n                                secondary_top2.indices[0]\n                            )\n                            local_weight = torch.where(\n                                same_parent,\n                                torch.maximum(\n                                    local_weight,\n                                    torch.full_like(local_weight, secondary_edge_weight),\n                                ),\n                                local_weight,\n                            )\n                            blend_weight = local_weight.view(1, 1, -1)\n                        else:\n                            blend_weight = secondary_edge_weight\n                    else:\n                        if n_src >= 2:\n                            primary_probs = torch.softmax(edge_logits_pair[0], dim=0)\n                            secondary_probs = torch.softmax(secondary_for_mix[0], dim=0)\n                            primary_top2 = torch.topk(primary_probs, k=2, dim=0)\n                            secondary_top2 = torch.topk(secondary_probs, k=2, dim=0)\n                            primary_margin = primary_top2.values[0] - primary_top2.values[1]\n                            same_parent = primary_top2.indices[0].eq(\n                                secondary_top2.indices[0]\n                            )\n                            uncertainty = (\n                                (secondary_low_margin_max - primary_margin)\n                                / secondary_low_margin_max\n                            ).clamp(0.0, 1.0)\n                            local_weight = secondary_edge_weight * uncertainty\n                            local_weight = torch.where(\n                                same_parent,\n                                local_weight,\n                                torch.zeros_like(local_weight),\n                            )\n                            blend_weight = local_weight.view(1, 1, -1)\n                        else:\n                            blend_weight = 0.0\n                else:\n                    raise ValueError(f"Unsupported secondary link mode: {secondary_link_mode}")\n\n                edge_logits_pair = (\n                    (1.0 - blend_weight) * edge_logits_pair\n                    + blend_weight * secondary_for_mix\n                )\n                if secondary_mix_temperature != 1.0:\n                    mixed_center = edge_logits_pair.mean(dim=1, keepdim=True)\n                    edge_logits_pair = mixed_center + (\n                        edge_logits_pair - mixed_center\n                    ) / secondary_mix_temperature\n\n            raw = edge_logits_pair[0]'),
    ('        del unet_out\n', '        del unet_out\n        if secondary_unet_out is not None:\n            del secondary_unet_out\n'),
    ('    model, window_size, downsample = load_model(weights_path, device)\n    print(', '    model, window_size, downsample = load_model(weights_path, device)\n\n    secondary_model = None\n    secondary_weights_text = os.environ.get("BIOHUB_SECONDARY_WEIGHTS", "").strip()\n    secondary_edge_weight = float(os.environ.get("BIOHUB_SECONDARY_EDGE_WEIGHT", "0"))\n    secondary_detection_weight = float(\n        os.environ.get("BIOHUB_SECONDARY_DETECTION_WEIGHT", "0")\n    )\n    secondary_link_mode = os.environ.get("BIOHUB_SECONDARY_LINK_MODE", "raw").strip()\n    secondary_mix_temperature = float(\n        os.environ.get("BIOHUB_SECONDARY_MIX_TEMPERATURE", "1")\n    )\n    secondary_low_margin_max = float(\n        os.environ.get("BIOHUB_SECONDARY_LOW_MARGIN_MAX", "0.2")\n    )\n    edge_candidate_threshold = float(\n        os.environ.get("BIOHUB_DUAL_SEED_EDGE_THRESHOLD", str(cfg.threshold))\n    )\n    if secondary_weights_text:\n        if not 0.0 < secondary_edge_weight < 1.0:\n            raise ValueError("BIOHUB_SECONDARY_EDGE_WEIGHT must be strictly between 0 and 1")\n        if not 0.0 <= secondary_detection_weight < 1.0:\n            raise ValueError(\n                "BIOHUB_SECONDARY_DETECTION_WEIGHT must be in the half-open interval [0, 1)"\n            )\n        if secondary_link_mode not in {\n            "raw", "calibrated", "adaptive", "low_margin_consensus"\n        }:\n            raise ValueError(\n                "BIOHUB_SECONDARY_LINK_MODE must be raw, calibrated, adaptive, "\n                "or low_margin_consensus"\n            )\n        if not 0.5 <= secondary_mix_temperature <= 2.0:\n            raise ValueError("BIOHUB_SECONDARY_MIX_TEMPERATURE must be in [0.5, 2.0]")\n        if not 0.0 < edge_candidate_threshold < 1.0:\n            raise ValueError("BIOHUB_DUAL_SEED_EDGE_THRESHOLD must be strictly between 0 and 1")\n        if not 0.0 < secondary_low_margin_max <= 1.0:\n            raise ValueError("BIOHUB_SECONDARY_LOW_MARGIN_MAX must be in (0, 1]")\n        secondary_model, secondary_window_size, secondary_downsample = load_model(\n            Path(secondary_weights_text), device,\n        )\n        if secondary_window_size != window_size or secondary_downsample != downsample:\n            raise ValueError(\n                "Primary and secondary models have incompatible inference grids: "\n                f"primary=(window={window_size}, downsample={downsample}), "\n                f"secondary=(window={secondary_window_size}, downsample={secondary_downsample})"\n            )\n        cfg.threshold = edge_candidate_threshold\n        print(\n            f"Secondary model: {secondary_weights_text} | "\n            f"edge weight={secondary_edge_weight:.3f} | "\n            f"detection weight={secondary_detection_weight:.3f} | "\n            f"link mode={secondary_link_mode} | "\n            f"temperature={secondary_mix_temperature:.3f} | "\n            f"low-margin max={secondary_low_margin_max:.3f} | "\n            f"edge threshold={cfg.threshold:.3f}",\n            flush=True,\n        )\n\n    print('),
    ('                unet_batch_size=unet_batch_size,\n                downsample=downsample,\n            )', '                unet_batch_size=unet_batch_size,\n                downsample=downsample,\n                secondary_model=secondary_model,\n                secondary_edge_weight=secondary_edge_weight,\n                secondary_detection_weight=secondary_detection_weight,\n                secondary_link_mode=secondary_link_mode,\n                secondary_mix_temperature=secondary_mix_temperature,\n                secondary_low_margin_max=secondary_low_margin_max,\n            )'),
]
for _patch_index, (_ensemble_old, _ensemble_new) in enumerate(
    _ensemble_replacements, start=1
):
    _ensemble_count = _s.count(_ensemble_old)
    if _ensemble_count != 1:
        raise RuntimeError(
            f'Calibrated dual-seed patch {_patch_index} expected one match, '
            f'found {_ensemble_count}'
        )
    _s = _s.replace(_ensemble_old, _ensemble_new, 1)
# Independent C retention guard: preserve primary candidates when the
# aligned dual-seed blend loses more than 10% of a frame's primary candidates.
_retention_old = """                    det_logits[f] = (
                        (1.0 - secondary_detection_weight) * primary_det
                        + secondary_detection_weight * secondary_det_aligned
                    )"""
_retention_new = """                    blended_det = (
                        (1.0 - secondary_detection_weight) * primary_det
                        + secondary_detection_weight * secondary_det_aligned
                    )
                    if frame_indices[f] not in seen_frames:
                        primary_candidates = _detect_cells_pooled(
                            primary_det[0], frame_indices[f], cfg.det_threshold, pool_k,
                        )
                        blended_candidates = _detect_cells_pooled(
                            blended_det[0], frame_indices[f], cfg.det_threshold, pool_k,
                        )
                        primary_count = int(primary_candidates.shape[0])
                        blended_count = int(blended_candidates.shape[0])
                        retention_min = float(os.environ.get(
                            "BIOHUB_RETENTION_MIN_RATIO", "0.90"
                        ))
                        if not 0.0 < retention_min <= 1.0:
                            raise ValueError("BIOHUB_RETENTION_MIN_RATIO must be in (0, 1]")
                        retention_ratio = (
                            blended_count / primary_count if primary_count else 1.0
                        )
                        if primary_count and retention_ratio < retention_min:
                            det_logits[f] = primary_det
                            print(
                                f"RETENTION_FALLBACK t={frame_indices[f]} "
                                f"primary={primary_count} blended={blended_count} "
                                f"ratio={retention_ratio:.6f} threshold={retention_min:.6f}",
                                flush=True,
                            )
                        else:
                            det_logits[f] = blended_det
                            print(
                                f"RETENTION_KEEP t={frame_indices[f]} "
                                f"primary={primary_count} blended={blended_count} "
                                f"ratio={retention_ratio:.6f} threshold={retention_min:.6f}",
                                flush=True,
                            )
                    else:
                        det_logits[f] = blended_det"""
if _s.count(_retention_old) != 1:
    raise RuntimeError(
        f"Candidate-retention patch expected one insertion point, found {_s.count(_retention_old)}"
    )
_s = _s.replace(_retention_old, _retention_new, 1)


# --- MATRICE EN PASSE : patches additifs (lane MATRICE-EN-PASSE) ---
_pm_patches = [
    ('module', 'def _detect_cells_pooled(\n', 'import time as _pm_time\n\n# --- MATRICE EN PASSE : emetteur probmat-1.0 (lane MATRICE-EN-PASSE) --------\n# Strictement additif. Inerte sans BIOCEL_PROBMAT_DIR.\n# Contrat de format : scripts/matrice/probmat_io.py\n_PM_DIR_TEXT = os.environ.get("BIOCEL_PROBMAT_DIR", "").strip()\n_PM_DIR = Path(_PM_DIR_TEXT) if _PM_DIR_TEXT else None\nif _PM_DIR is not None:\n    _PM_DIR.mkdir(parents=True, exist_ok=True)\n_PM_GATE_UM = float(os.environ.get("BIOCEL_PROBMAT_GATE_UM", "15.0"))\n_PM_COMPRESS = os.environ.get("BIOCEL_PROBMAT_COMPRESS", "1").strip() != "0"\n_PM_SCHEMA = "probmat-1.0"\n# Constantes REPRISES TELLES QUELLES de dump_edge_candidates.py:41-42.\n_PM_SCALE = np.array([1.625, 0.40625, 0.40625], dtype=np.float32)\n_PM_DS = np.array([1.0, 4.0, 4.0], dtype=np.float32)\n_PM_BUF = {"pm_src": [], "pm_tgt": [], "pm_prob": []}\n_PM_T = [0.0, 0.0]          # [emission, ecriture] en secondes, par film\n\n\ndef _pm_reset():\n    for _k in _PM_BUF:\n        _PM_BUF[_k] = []\n    _PM_T[0] = 0.0\n    _PM_T[1] = 0.0\n\n\ndef _pm_emit(probs_np, c_src, c_tgt, off_src, off_tgt):\n    """Une paire de frames. PORTE VERBATIM du bloc de porte de\n    dump_edge_candidates.dump_video:133-141 -- memes constantes, meme ordre des\n    operations flottantes, meme ordre d\'enumeration ligne-majeur."""\n    pos_src_um = (c_src[:, 1:].astype(np.float32) * _PM_DS) * _PM_SCALE\n    pos_tgt_um = (c_tgt[:, 1:].astype(np.float32) * _PM_DS) * _PM_SCALE\n    dmat = np.linalg.norm(pos_src_um[:, None, :] - pos_tgt_um[None, :, :], axis=2)\n    ii, jj = np.where(dmat <= _PM_GATE_UM)\n    _PM_BUF["pm_src"].append(ii + off_src)\n    _PM_BUF["pm_tgt"].append(jj + off_tgt)\n    _PM_BUF["pm_prob"].append(probs_np[ii, jj])\n\n\ndef _pm_save(stem, coords_ds):\n    """Ecrit le .npz du film. coords_ds : (N,4) grille SOUS-ECHANTILLONNEE,\n    les noeuds de la passe, memes index que src_idx/tgt_idx."""\n    if _PM_DIR is None:\n        return\n    _pm_t0 = _pm_time.perf_counter()\n    _pm_out = {"pm_coords": np.asarray(coords_ds, dtype=np.int16)}\n    for _k, _dt in (("pm_src", np.int32), ("pm_tgt", np.int32),\n                    ("pm_prob", np.float32)):\n        _parts = _PM_BUF[_k]\n        _pm_out[_k] = (np.concatenate(_parts).astype(_dt) if _parts\n                       else np.empty((0,), dtype=_dt))\n    if len(_pm_out["pm_src"]):\n        _mx = max(int(_pm_out["pm_src"].max()), int(_pm_out["pm_tgt"].max()))\n        if _mx >= len(_pm_out["pm_coords"]):\n            raise RuntimeError(\n                "PROBMAT: index " + str(_mx) + " hors des "\n                + str(len(_pm_out["pm_coords"])) + " noeuds sur " + stem\n                + " -- la matrice ne pointe pas les noeuds de la passe")\n    _pm_out["pm_gate_um"] = np.float32(_PM_GATE_UM)\n    _pm_out["pm_schema"] = np.array(_PM_SCHEMA)\n    _pm_path = _PM_DIR / (stem + ".npz")\n    if _PM_COMPRESS:\n        np.savez_compressed(str(_pm_path), **_pm_out)\n    else:\n        np.savez(str(_pm_path), **_pm_out)\n    _PM_T[1] += _pm_time.perf_counter() - _pm_t0\n    print(\n        "PROBMAT_EXPORT film=" + stem\n        + " nodes=" + str(len(_pm_out["pm_coords"]))\n        + " pairs=" + str(len(_pm_out["pm_src"]))\n        + " gate_um=" + str(_PM_GATE_UM)\n        + " emit_s=" + format(_PM_T[0], ".3f")\n        + " write_s=" + format(_PM_T[1], ".3f")\n        + " bytes=" + str(_pm_path.stat().st_size),\n        flush=True,\n    )\n\n\ndef _detect_cells_pooled(\n'),
    ('reset', '    seen_frames: set[int] = set()\n    seen_pairs: set[tuple[int, int]] = set()\n', '    _pm_reset()\n    if _PM_DIR is not None:\n        if cfg.edge_activation != "softmax":\n            raise RuntimeError(\n                "PROBMAT: edge_activation=" + str(cfg.edge_activation) +\n                " -- le probdump est defini sur le SOFTMAX par cible")\n        _pm_vox = np.asarray(voxel_size, dtype=np.float32)\n        if not np.array_equal(_pm_vox, _PM_DS * _PM_SCALE):\n            raise RuntimeError(\n                "PROBMAT: voxel_size " + str(tuple(_pm_vox)) + " != " +\n                str(tuple(_PM_DS * _PM_SCALE)) +\n                " -- l echelle du probdump ne vaut pas pour ce film")\n    seen_frames: set[int] = set()\n    seen_pairs: set[tuple[int, int]] = set()\n'),
    ('export', '            raw = edge_logits_pair[0]\n            if cfg.edge_activation == "softmax":\n                probs = torch.softmax(raw, dim=0).cpu().numpy()\n            else:\n                probs = torch.sigmoid(raw).cpu().numpy()\n', '            raw = edge_logits_pair[0]\n            if cfg.edge_activation == "softmax":\n                probs = torch.softmax(raw, dim=0).cpu().numpy()\n            else:\n                probs = torch.sigmoid(raw).cpu().numpy()\n\n            if _PM_DIR is not None:\n                _pm_t2 = _pm_time.perf_counter()\n                _pm_emit(probs, c_src, c_tgt,\n                         int(idx_src[0]), int(idx_tgt[0]))\n                _PM_T[0] += _pm_time.perf_counter() - _pm_t2\n'),
    ('save', '    coords = np.concatenate(coord_lists) if coord_lists else np.empty((0, 4), dtype=np.int16)\n    # Scale spatial coords back to original resolution.\n    coords = coords.astype(np.float32)\n', "    coords = np.concatenate(coord_lists) if coord_lists else np.empty((0, 4), dtype=np.int16)\n    _pm_save(Path(ds_path).name.replace('.zarr', ''), coords)\n    # Scale spatial coords back to original resolution.\n    coords = coords.astype(np.float32)\n"),
]
for _pm_name, _pm_old, _pm_new in _pm_patches:
    if _s.count(_pm_old) != 1:
        raise RuntimeError(
            f'PROBMAT patch {_pm_name} expected one match, found {_s.count(_pm_old)}'
        )
    _s = _s.replace(_pm_old, _pm_new, 1)
print('PROBMAT export patch applied (' + str(len(_pm_patches))
      + ' insertions, strictement additif)')

compile(_s, str(_ps), 'exec')
_ps.write_text(_s)
print('Calibrated dual-seed runtime patch applied')

def list_test_stems() -> list[str]:
    if not TEST_DIR.exists():
        raise FileNotFoundError(f"Test directory does not exist: {TEST_DIR}")
    stems = sorted(path.name[:-5] for path in TEST_DIR.iterdir() if path.name.endswith(".zarr"))
    if not stems:
        raise FileNotFoundError(f"No test .zarr files found in {TEST_DIR}")
    return stems


test_stems = list_test_stems()
print(f"Found {len(test_stems)} test videos")
print(test_stems[:10])

splits_path = REPO_DIR / "kaggle_test_splits_50ep.json"
splits_path.parent.mkdir(parents=True, exist_ok=True)
splits_path.write_text(json.dumps([{"split": 0, "train": [], "test": test_stems}], indent=2))

predict_cmd = [
    sys.executable,
    "scripts/predict_unet_transformer.py",
    "--data-dir",
    str(TEST_DIR),
    "--splits",
    str(splits_path.name),
    "--split",
    "0",
    "--weights",
    WEIGHTS_RELATIVE,
    "--unet-batch-size",
    str(UNET_BATCH_SIZE),
    "--det-threshold",
    str(DET_THRESHOLD),
    "--ilp-edge-weight",
    str(ILP_EDGE_WEIGHT),
    "--ilp-appearance-weight",
    str(ILP_APPEARANCE_WEIGHT),
    "--ilp-disappearance-weight",
    str(ILP_DISAPPEARANCE_WEIGHT),
    "--ilp-division-weight",
    str(ILP_DIVISION_WEIGHT),
]
if USE_ILP:
    predict_cmd.append("--use-ilp")
if SLICE:
    predict_cmd.extend(["--slice", SLICE])

def _visible_cuda_tokens(count: int) -> list[str]:
    raw = os.environ.get("CUDA_VISIBLE_DEVICES", "").strip()
    if raw and raw != "-1":
        tokens = [token.strip() for token in raw.split(",") if token.strip()]
        if len(tokens) < count:
            raise RuntimeError(
                f"torch reports {count} CUDA devices but CUDA_VISIBLE_DEVICES={raw!r}"
            )
        return tokens[:count]
    return [str(index) for index in range(count)]


def _prediction_dir_for_method(method: str) -> Path:
    matches = sorted((REPO_DIR / "predictions").glob(f"*/{method}/split_0"))
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one prediction directory for {method!r}, found {matches}"
        )
    return matches[0]


def _wait_for_prediction_shards(
    processes: dict[int, subprocess.Popen],
    commands: dict[int, list[str]],
) -> None:
    while processes:
        failed: tuple[int, int] | None = None
        for shard_index, process in list(processes.items()):
            return_code = process.poll()
            if return_code is None:
                continue
            del processes[shard_index]
            if return_code != 0:
                failed = (shard_index, return_code)
                break
        if failed is None:
            if processes:
                time.sleep(1.0)
            continue

        failed_index, failed_code = failed
        for process in processes.values():
            if process.poll() is None:
                process.terminate()
        for process in processes.values():
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        raise subprocess.CalledProcessError(failed_code, commands[failed_index])


def _merge_prediction_shards(worker_count: int) -> Path:
    shard_dirs: list[Path] = []
    seen: set[str] = set()
    expected_all = set(test_stems)

    for shard_index in range(worker_count):
        shard_method = f"{METHOD}_gpu{shard_index}"
        shard_dir = _prediction_dir_for_method(shard_method)
        expected = set(test_stems[shard_index::worker_count])
        shard_paths = sorted(shard_dir.glob("*.geff"))
        found = {path.stem for path in shard_paths}
        if found != expected:
            raise RuntimeError(
                f"GPU shard {shard_index} output mismatch: "
                f"missing={sorted(expected - found)}, extra={sorted(found - expected)}"
            )
        overlap = seen & found
        if overlap:
            raise RuntimeError(f"Duplicate datasets across GPU shards: {sorted(overlap)}")
        seen.update(found)
        shard_dirs.append(shard_dir)

    if seen != expected_all:
        raise RuntimeError(
            f"Merged GPU shards do not cover the test set: "
            f"missing={sorted(expected_all - seen)}, extra={sorted(seen - expected_all)}"
        )

    username_roots = {shard_dir.parents[1] for shard_dir in shard_dirs}
    if len(username_roots) != 1:
        raise RuntimeError(f"GPU shards used inconsistent prediction roots: {username_roots}")
    import shutil as _shutil

    final_root = next(iter(username_roots)) / METHOD
    final_dir = final_root / "split_0"
    staging_dir = final_root / "split_0_dual_gpu_staging"
    if staging_dir.exists():
        if staging_dir.is_dir():
            _shutil.rmtree(staging_dir)
        else:
            staging_dir.unlink()
    staging_dir.mkdir(parents=True, exist_ok=False)

    for shard_dir in shard_dirs:
        for source in sorted(shard_dir.glob("*.geff")):
            destination = staging_dir / source.name
            if destination.exists():
                raise RuntimeError(f"Refusing to overwrite duplicate merged output: {destination}")
            _shutil.move(str(source), str(destination))

    merged = {path.stem for path in staging_dir.glob("*.geff")}
    if merged != expected_all:
        raise RuntimeError(
            f"Staged prediction directory failed verification: "
            f"missing={sorted(expected_all - merged)}, extra={sorted(merged - expected_all)}"
        )

    if final_dir.exists():
        if final_dir.is_dir():
            _shutil.rmtree(final_dir)
        else:
            final_dir.unlink()
    staging_dir.rename(final_dir)
    for shard_dir in shard_dirs:
        _shutil.rmtree(shard_dir.parent)
    print(f"Merged {len(merged)} prediction graphs into {final_dir}")
    return final_dir


start_time = time.time()
available_gpu_count = _torch.cuda.device_count()
worker_count = min(2, available_gpu_count, len(test_stems))

if worker_count >= 2 and not SLICE:
    cuda_tokens = _visible_cuda_tokens(worker_count)
    processes: dict[int, subprocess.Popen] = {}
    commands: dict[int, list[str]] = {}
    print(f"Launching {worker_count} independent video shards on CUDA devices {cuda_tokens}")
    for shard_index in range(worker_count):
        shard_method = f"{METHOD}_gpu{shard_index}"
        shard_cmd = [
            *predict_cmd,
            "--method",
            shard_method,
            "--slice",
            f"{shard_index}::{worker_count}",
        ]
        shard_env = {**os.environ, "PYTHONPATH": "src"}
        shard_env["CUDA_VISIBLE_DEVICES"] = cuda_tokens[shard_index]
        shard_env["BIOHUB_GPU_SHARD"] = f"{shard_index}/{worker_count}"
        print(
            f"GPU shard {shard_index}: CUDA_VISIBLE_DEVICES={cuda_tokens[shard_index]} | "
            + " ".join(shard_cmd),
            flush=True,
        )
        commands[shard_index] = shard_cmd
        processes[shard_index] = subprocess.Popen(
            shard_cmd,
            cwd=REPO_DIR,
            env=shard_env,
        )
    _wait_for_prediction_shards(processes, commands)
    _merge_prediction_shards(worker_count)
else:
    reason = "SLICE is active" if SLICE else f"only {available_gpu_count} CUDA device(s) available"
    print(f"Using single-process prediction because {reason}.")
    print(" ".join(predict_cmd))
    subprocess.run(
        predict_cmd,
        cwd=REPO_DIR,
        env={**os.environ, "PYTHONPATH": "src"},
        check=True,
    )

predict_seconds = time.time() - start_time
print(f"Prediction completed in {predict_seconds / 60:.2f} minutes")