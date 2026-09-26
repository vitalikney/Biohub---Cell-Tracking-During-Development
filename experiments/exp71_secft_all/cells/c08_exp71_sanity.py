# [exp71] Sanity (hard asserts): only parameters of the v1-trainable modules moved vs the teacher, every
# tensor is finite, the new sha differs from the parent, and the file strict-loads the way
# predict_unet_transformer.load_model loads BIOHUB_SECONDARY_WEIGHTS in x138.
new_state = torch.load(candidate, map_location="cpu", weights_only=True)
assert list(new_state) == list(initial_state), "state-dict keys differ from the teacher"
_last_block = len(model.unet.decoder_blocks) - 1
TRAINABLE_PREFIXES = (f"unet.decoder_blocks.{_last_block}.", "unet.head.", "detect_head.")
changed, unchanged_trainable, param_deltas = [], [], {}
for key, old in initial_state.items():
    new = new_state[key]
    assert new.shape == old.shape and new.dtype == old.dtype, f"shape/dtype changed: {key}"
    if new.is_floating_point():
        assert torch.isfinite(new).all(), f"non-finite values in {key}"
    if torch.equal(new, old):
        if key.startswith(TRAINABLE_PREFIXES):
            unchanged_trainable.append(key)
        continue
    changed.append(key)
    delta = new.double() - old.double()
    param_deltas[key] = {
        "max_abs": float(delta.abs().max()),
        "rel_l2": float(delta.norm() / old.double().norm().clamp_min(1e-12)),
    }
outside = [key for key in changed if not key.startswith(TRAINABLE_PREFIXES)]
assert not outside, f"parameters outside {TRAINABLE_PREFIXES} changed: {outside}"
assert changed, "no parameter changed: the fine-tune did not update the model"
unexpected_frozen = [
    key for key in unchanged_trainable
    if not key.endswith(("running_mean", "running_var", "num_batches_tracked"))
]
if unexpected_frozen:
    print("WARNING: trainable weights that did not move:", unexpected_frozen, flush=True)

candidate_sha256 = hashlib.sha256(candidate.read_bytes()).hexdigest()
assert candidate_sha256 != expected_initial_sha256, "new weights are byte-identical to the parent"

_candidate_config = json.loads(candidate.with_name("config.json").read_text(encoding="utf-8"))
assert _candidate_config == config, (_candidate_config, config)
_strict_check = BaseModel(
    unet=trainer.TemporalUNet3D(
        in_channels=1,
        out_channels=_candidate_config["unet_out_channels"],
        layers=_candidate_config["unet_layers"],
    ),
    unet_out_channels=_candidate_config["unet_out_channels"],
    pos_feat_dim=4 * trainer._POS_EMBED_DIM,
)
_strict_check.load_state_dict(new_state)  # strict=True, same construction as load_model()
del _strict_check

EXP71_LOG["sanity"] = {
    "candidate_sha256": candidate_sha256,
    "parent_sha256": expected_initial_sha256,
    "trainable_prefixes": list(TRAINABLE_PREFIXES),
    "changed_keys": changed,
    "unchanged_trainable_keys": unchanged_trainable,
    "param_deltas": param_deltas,
    "all_finite": True,
}
print(f"sanity OK: {len(changed)} tensors changed, all under {TRAINABLE_PREFIXES}; all finite; strict load OK")
for key in changed:
    print(f"  {key:45s} max|d|={param_deltas[key]['max_abs']:.3e}  rel_l2={param_deltas[key]['rel_l2']:.3e}")
print("new SHA256:", candidate_sha256, "\nparent   :", expected_initial_sha256, flush=True)


# [exp71] Diagnostic only (never blocks the export): teacher vs student peak counts on 8 fixed TRAIN windows
# (in-sample), with the trainer's own peak finder (detect_and_match) at p >= 0.5 and p >= 0.965.
def _exp71_detection_proxy(n_per_prefix=4):
    device = next(model.parameters()).device
    teacher = reference["teacher"]
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
        imgs = item["imgs"].to(device, dtype=torch.float32)[None]
        coords = item["coords"].to(device)[None]
        masks = item["masks"].to(device)[None]
        image_shape = tuple(int(v) for v in item["image_shape"].tolist())
        voxel_size = tuple(float(v) for v in item["voxel_size"].tolist())
        with torch.no_grad():
            _, student_logits = model.encode(imgs)
            _, teacher_logits = teacher.encode(imgs)
        row = {"video": name, "t_start": int(item["t_start"]), "gt": int(masks.sum())}
        totals["gt"] += row["gt"]
        for who, logits in (("teacher", teacher_logits), ("student", student_logits)):
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
        t_det, s_det = totals[f"teacher_{tname}_det"], totals[f"student_{tname}_det"]
        totals[f"student_over_teacher_{tname}_det"] = round(s_det / max(t_det, 1), 4)
        print(
            f"  {tname}: peaks teacher {t_det} -> student {s_det} (x{s_det / max(t_det, 1):.3f}); "
            f"GT hit teacher {totals[f'teacher_{tname}_gt_hit']}/{totals['gt']} -> "
            f"student {totals[f'student_{tname}_gt_hit']}/{totals['gt']}",
            flush=True,
        )
    return {"note": "in-sample train windows; trainer peak finder, not the x138 pipeline", "totals": totals, "rows": rows}


try:
    print("detection proxy (teacher vs student, 8 train windows):", flush=True)
    EXP71_LOG["detection_proxy"] = _exp71_detection_proxy()
except Exception as exc:  # diagnostic only
    traceback.print_exc()
    EXP71_LOG["detection_proxy"] = {"error": repr(exc)}
