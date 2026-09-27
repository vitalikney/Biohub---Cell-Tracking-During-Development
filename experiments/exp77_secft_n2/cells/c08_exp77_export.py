# [exp77] LAST CELL: exp71 c09, run once per student that passed sanity. It writes the dataset payload in the layout of
# pilkwang/biohub-temporal-unet3d-seed314159-v1, which x138 code cell 3 reads:
#   - _find_secondary_artifact_root -> manifest["model"]["weight_sha256"];
#   - copy_or_extract_tree(<manifest dir>/weights) -> unet_transformer/split_0/{edge_predictor_best.pth, config.json};
#   - a sha256 check of the copied weights.
# It then removes every scratch dir from /kaggle/working.
#   /kaggle/working/secft_n2a/ARTIFACT_MANIFEST.json + weights/unet_transformer/split_0/{edge_predictor_best.pth, config.json}
#   /kaggle/working/secft_n2b/ (same layout)
#   /kaggle/working/exp77_train_log.json    (small combined log, outside the dataset folders)
#   /kaggle/working/exp77_logs/             (worker stdout logs, per-run JSON logs, the worker source)
teacher_manifest = json.loads((secondary / "ARTIFACT_MANIFEST.json").read_text(encoding="utf-8"))
assert teacher_manifest["model"]["weight_sha256"] == expected_initial_sha256
compatibility = copy.deepcopy(teacher_manifest.get("compatibility", {}))
compatibility.pop("gate_diagnostics", None)  # refers to full_frame_center files this artifact does not ship
compatibility.get("models", {}).pop("full_frame_center", None)

PARENT_ARTIFACT = "pilkwang/biohub-temporal-unet3d-seed314159-v1"
EXPORTED = {}
EXPORT_FAIL = {}


def _export(label):
    spec = SPEC_BY_LABEL[label]
    candidate = STUDENTS[label]["candidate"]
    candidate_sha256 = SANITY[label]["candidate_sha256"]
    wlog = WORKER_RESULTS[label].get("worker_log") or {}
    train_stats = wlog.get("runs", {}).get("train", {})
    rule = wlog.get("max_iters_rule", {})
    out_dir = WORKING_ROOT / spec["export_dir"]
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_weights = out_dir / "weights" / "unet_transformer" / "split_0" / "edge_predictor_best.pth"
    out_weights.parent.mkdir(parents=True)
    shutil.copyfile(candidate, out_weights)
    # Architecture is unchanged: ship the teacher's own config.json bytes (same 5 keys load_model reads).
    shutil.copyfile(secondary_config, out_weights.with_name("config.json"))
    assert json.loads(out_weights.with_name("config.json").read_text(encoding="utf-8")) == config

    out_sha256 = hashlib.sha256(out_weights.read_bytes()).hexdigest()
    assert out_sha256 == candidate_sha256, (out_sha256, candidate_sha256)
    assert out_sha256 not in (expected_initial_sha256, SECFT_ALL_SHA256)

    n_iters = int(train_stats.get("n_iters") or STUDENTS[label]["done"].get("n_iters") or 0)
    is_continuation = spec["init_sha256"] != expected_initial_sha256
    lineage = (
        [
            {"artifact": "vitaliineibauer/biohub-secft-all-v1", "sha256": SECFT_ALL_SHA256,
             "training": "exp71: 1 epoch (18,707 it), lr 1e-5, seed 314159, same recipe"},
            {"artifact": PARENT_ARTIFACT, "sha256": expected_initial_sha256, "training": "pilkwang original"},
        ]
        if is_continuation
        else [{"artifact": PARENT_ARTIFACT, "sha256": expected_initial_sha256, "training": "pilkwang original"}]
    )
    model_block = {
        "config": config,
        "method": "unet_transformer",
        "weight_path": "weights/unet_transformer/split_0/edge_predictor_best.pth",
        "weight_bytes": out_weights.stat().st_size,
        "weight_sha256": out_sha256,
        "parent_sha256": spec["init_sha256"],
        "root_parent_sha256": expected_initial_sha256,
        "teacher_sha256": expected_initial_sha256,
        "lineage": lineage,
        "training": {
            "method": "secondary_teacher_distill_ft_y3uanm_v1",
            "exp77_run": label,
            "init": spec["init_desc"],
            "teacher": f"{PARENT_ARTIFACT} (frozen, sha {expected_initial_sha256[:8]})",
            "trainable": ["unet.decoder_blocks[-1]", "unet.head", "detect_head"],
            "batchnorm": "frozen (train() forced to eval mode)",
            "det_loss": "softplus(-logit) at GT centres + 0.5*BCE(student, teacher sigmoid) on non-GT voxels "
                        "+ 0.1*normalised feature MSE to the teacher",
            "edge_loss": "unchanged trainer edge loss through the frozen transformer",
            "det_loss_weight": 1.0,
            "optimizer": "AdamW (torch defaults besides lr; fresh optimizer state)",
            "learning_rate": spec["lr"],
            "batch_size": 1,
            "precision": "fp32",
            "seed": spec["seed"],
            "augmentations": [],
            "validation": None,
            "train_datasets": len(names),
            "loader_len": train_stats.get("loader_len"),
            "max_iters": train_stats.get("max_iters"),
            "n_iters": n_iters,
            "epoch_fraction": round(n_iters / max(int(train_stats.get("loader_len") or 0), 1), 4),
            "total_epochs_incl_parent_ft": (1.0 if is_continuation else 0.0)
                + round(n_iters / max(int(train_stats.get("loader_len") or 0), 1), 4),
            "hard_stopped": bool(train_stats.get("hard_stopped")),
            "stop_reason": train_stats.get("stop_reason"),
            "num_workers": (wlog.get("knobs") or {}).get("num_workers"),
            "cuda_visible_devices": wlog.get("cuda_visible_devices"),
            "seconds_per_iter_probe": rule.get("seconds_per_iter"),
            "seconds_per_iter_mean": train_stats.get("seconds_per_iter_mean"),
            "train_wall_s": train_stats.get("wall_s_incl_data_loading"),
        },
    }
    manifest = {
        "artifact_name": spec["artifact_name"],
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": f"private training kernel vitaliineibauer/biohub-exp77-secft-n2, run {label} "
                  "(y3uanm notebook0afc5663f6 recipe)",
        "parent_artifact": "vitaliineibauer/biohub-secft-all-v1" if is_continuation else PARENT_ARTIFACT,
        "root_parent_artifact": PARENT_ARTIFACT,
        "compatibility": compatibility,
        "contents": {
            "weights": {"files": 2, "bytes": sum(p.stat().st_size for p in out_weights.parent.iterdir())},
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
    (out_dir / "ARTIFACT_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # Emulate x138 code cell 3 on the written folder.
    _info = json.loads((out_dir / "ARTIFACT_MANIFEST.json").read_text())
    assert str(_info.get("model", {}).get("weight_sha256", "")) == out_sha256
    with tempfile.TemporaryDirectory() as _tmp:
        _copied = Path(_tmp) / "secondary_seed_weights"
        shutil.copytree(out_dir / "weights", _copied)
        _w = _copied / "unet_transformer" / "split_0" / "edge_predictor_best.pth"
        assert _w.is_file() and _w.with_name("config.json").is_file()
        assert hashlib.sha256(_w.read_bytes()).hexdigest() == out_sha256
        assert sorted(p.name for p in _w.parent.iterdir()) == ["config.json", "edge_predictor_best.pth"]
    print(f"[{label}] x138 loader emulation OK -> {out_dir}", flush=True)
    return {
        "dir": str(out_dir),
        "artifact_name": spec["artifact_name"],
        "weight_sha256": out_sha256,
        "parent_sha256": spec["init_sha256"],
        "root_parent_sha256": expected_initial_sha256,
        "n_iters": n_iters,
        "max_iters": train_stats.get("max_iters"),
        "hard_stopped": bool(train_stats.get("hard_stopped")),
        "stop_reason": train_stats.get("stop_reason"),
    }


for _label in [spec["label"] for spec in RUN_SPECS]:
    if _label not in SANITY:
        continue
    try:
        EXPORTED[_label] = _export(_label)
    except Exception as exc:
        traceback.print_exc()
        EXPORT_FAIL[_label] = repr(exc)
        shutil.rmtree(WORKING_ROOT / SPEC_BY_LABEL[_label]["export_dir"], ignore_errors=True)
        print(f"[exp77] {_label}: EXPORT FAILED: {exc!r}", flush=True)

EXP77_LOG["artifacts"] = EXPORTED
EXP77_LOG["export_failures"] = EXPORT_FAIL
EXP77_LOG["runs"] = {label: res.get("worker_log") for label, res in WORKER_RESULTS.items()}
EXP77_LOG["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
EXP77_LOG["notebook_wall_s"] = round(time.time() - EXP77_T0, 1)
(WORKING_ROOT / "exp77_train_log.json").write_text(json.dumps(EXP77_LOG, indent=2) + "\n", encoding="utf-8")

# Cleanup. run_dir holds the repo copy, the teacher copy, both students' scratch weights, splits.json and the run configs.
# The worker source moves next to its logs.
shutil.rmtree(run_dir)
if WORKER_SRC.exists():
    shutil.move(str(WORKER_SRC), str(EXP77_LOGS / WORKER_SRC.name))
_total = 0
print("final /kaggle/working:")
for _p in sorted(WORKING_ROOT.rglob("*")):
    if _p.is_file():
        _total += _p.stat().st_size
        print(f"  {_p.relative_to(WORKING_ROOT)}  {_p.stat().st_size:,} B")
print(f"  total {_total / 2**20:.1f} MiB")
if _total > 64 * 2**20:
    print("WARNING: /kaggle/working is larger than expected", flush=True)
for _label in [spec["label"] for spec in RUN_SPECS]:
    if _label in EXPORTED:
        _e = EXPORTED[_label]
        print(f"NEW SECONDARY {_label} ({_e['artifact_name']}): SHA256 {_e['weight_sha256']} | n_iters {_e['n_iters']} | "
              f"max_iters {_e['max_iters']} | hard_stopped {_e['hard_stopped']} | stop_reason {_e['stop_reason']}")
    else:
        _why = EXPORT_FAIL.get(_label) or SANITY_FAIL.get(_label) or WORKER_RESULTS.get(_label, {}).get("status")
        print(f"!!! {_label}: NOT EXPORTED ({_why}); see exp77_logs/worker_{_label}.log", flush=True)
if not EXPORTED:
    raise RuntimeError("exp77: no student exported")
