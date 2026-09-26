# [exp71] LAST CELL. Writes the dataset payload in the layout of pilkwang/biohub-temporal-unet3d-seed314159-v1
# that x138 code cell 3 reads (_find_secondary_artifact_root -> manifest["model"]["weight_sha256"];
# copy_or_extract_tree(<manifest dir>/weights) -> unet_transformer/split_0/{edge_predictor_best.pth, config.json};
# sha256 check of the copied weights), then removes every scratch dir from /kaggle/working.
#   /kaggle/working/secft/ARTIFACT_MANIFEST.json
#   /kaggle/working/secft/weights/unet_transformer/split_0/edge_predictor_best.pth
#   /kaggle/working/secft/weights/unet_transformer/split_0/config.json
#   /kaggle/working/exp71_train_log.json          (small log, outside the dataset folder)
working_root = Path("/kaggle/working")
secft_dir = working_root / "secft"
if secft_dir.exists():
    shutil.rmtree(secft_dir)
secft_weights = secft_dir / "weights" / "unet_transformer" / "split_0" / "edge_predictor_best.pth"
secft_weights.parent.mkdir(parents=True)
shutil.copyfile(candidate, secft_weights)
# Architecture is unchanged: ship the teacher's own config.json bytes (same 5 keys load_model reads).
shutil.copyfile(secondary_config, secft_weights.with_name("config.json"))
assert json.loads(secft_weights.with_name("config.json").read_text(encoding="utf-8")) == config

secft_sha256 = hashlib.sha256(secft_weights.read_bytes()).hexdigest()
assert secft_sha256 == candidate_sha256, (secft_sha256, candidate_sha256)
assert secft_sha256 != expected_initial_sha256

teacher_manifest = json.loads((secondary / "ARTIFACT_MANIFEST.json").read_text(encoding="utf-8"))
assert teacher_manifest["model"]["weight_sha256"] == expected_initial_sha256
compatibility = copy.deepcopy(teacher_manifest.get("compatibility", {}))
compatibility.pop("gate_diagnostics", None)  # refers to full_frame_center files this artifact does not ship
compatibility.get("models", {}).pop("full_frame_center", None)

train_stats = EXP71_LOG["runs"]["train"]
n_iters = int(train_stats["n_iters"])
model_block = {
    "config": config,
    "method": "unet_transformer",
    "weight_path": "weights/unet_transformer/split_0/edge_predictor_best.pth",
    "weight_bytes": secft_weights.stat().st_size,
    "weight_sha256": secft_sha256,
    "parent_sha256": expected_initial_sha256,
    "training": {
        "method": "secondary_teacher_distill_ft_y3uanm_v1",
        "init": "pilkwang/biohub-temporal-unet3d-seed314159-v1 weights/unet_transformer/split_0/edge_predictor_best.pth",
        "trainable": ["unet.decoder_blocks[-1]", "unet.head", "detect_head"],
        "batchnorm": "frozen (train() forced to eval mode)",
        "det_loss": "softplus(-logit) at GT centres + 0.5*BCE(student, teacher sigmoid) on non-GT voxels "
                    "+ 0.1*normalised feature MSE to the teacher",
        "edge_loss": "unchanged trainer edge loss through the frozen transformer",
        "det_loss_weight": 1.0,
        "optimizer": "AdamW (torch defaults besides lr)",
        "learning_rate": 1e-5,
        "batch_size": 1,
        "precision": "fp32",
        "seed": 314159,
        "augmentations": [],
        "validation": None,
        "train_datasets": len(names),
        "loader_len": train_stats.get("loader_len"),
        "max_iters": MAX_ITERS,
        "n_iters": n_iters,
        "epoch_fraction": round(n_iters / max(int(train_stats.get("loader_len") or 0), 1), 4),
        "hard_stopped": bool(train_stats.get("hard_stopped")),
        "stop_reason": train_stats.get("stop_reason"),
        "num_workers": NUM_WORKERS,
        "seconds_per_iter_probe": EXP71_LOG["max_iters_rule"]["seconds_per_iter"],
        "seconds_per_iter_mean": train_stats.get("seconds_per_iter_mean"),
        "train_wall_s": train_stats.get("wall_s_incl_data_loading"),
    },
}
manifest = {
    "artifact_name": "biohub-secft-all-v1",
    "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "source": "private training kernel vitaliineibauer/biohub-exp71-secft-all (y3uanm notebook0afc5663f6 recipe)",
    "parent_artifact": "pilkwang/biohub-temporal-unet3d-seed314159-v1",
    "compatibility": compatibility,
    "contents": {
        "weights": {"files": 2, "bytes": sum(p.stat().st_size for p in secft_weights.parent.iterdir())},
        "repo_included": False,
        "wheels_included": False,
    },
    "model": model_block,
    "models": {"unet_transformer": model_block},
    "n_iters": n_iters,
    "notes": [
        "Drop-in secondary for x138-style notebooks: same architecture/config as the parent, only the weights differ.",
        "x138 hard-codes the parent sha (code cell 3 _secondary_expected_sha256); set it to model.weight_sha256 and "
        "point BIOHUB_SECONDARY_ARTIFACT_MANIFEST at this file.",
    ],
}
(secft_dir / "ARTIFACT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

# Emulate x138 code cell 3 on the written folder.
_info = json.loads((secft_dir / "ARTIFACT_MANIFEST.json").read_text())
assert str(_info.get("model", {}).get("weight_sha256", "")) == secft_sha256
with tempfile.TemporaryDirectory() as _tmp:
    _copied = Path(_tmp) / "secondary_seed_weights"
    shutil.copytree(secft_dir / "weights", _copied)
    _w = _copied / "unet_transformer" / "split_0" / "edge_predictor_best.pth"
    assert _w.is_file() and _w.with_name("config.json").is_file()
    assert hashlib.sha256(_w.read_bytes()).hexdigest() == secft_sha256
print("x138 loader emulation OK", flush=True)

EXP71_LOG["artifact"] = {
    "dir": str(secft_dir),
    "weight_sha256": secft_sha256,
    "parent_sha256": expected_initial_sha256,
    "n_iters": n_iters,
    "max_iters": MAX_ITERS,
}
EXP71_LOG["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
(working_root / "exp71_train_log.json").write_text(json.dumps(EXP71_LOG, indent=2) + "\n", encoding="utf-8")

# Cleanup: repo copy, teacher copy, trained-weights scratch, splits (all under run_dir).
shutil.rmtree(run_dir)
_total = 0
print("final /kaggle/working:")
for _p in sorted(working_root.rglob("*")):
    if _p.is_file():
        _total += _p.stat().st_size
        print(f"  {_p.relative_to(working_root)}  {_p.stat().st_size:,} B")
print(f"  total {_total / 2**20:.1f} MiB")
if _total > 64 * 2**20:
    print("WARNING: /kaggle/working is larger than expected", flush=True)
print("NEW SECONDARY SHA256 (for the x138 sha anchor / --patch secswap):", secft_sha256)
print(
    "n_iters:", n_iters, "| max_iters:", MAX_ITERS, "| loader_len:", train_stats.get("loader_len"),
    "| hard_stopped:", train_stats.get("hard_stopped"), "| stop_reason:", train_stats.get("stop_reason"),
)
