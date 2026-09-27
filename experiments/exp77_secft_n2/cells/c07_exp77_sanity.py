# [exp77] Sanity, the exp71 c08 hard asserts, run per student in the notebook process (CPU tensors). A student is exported
# only if every check passes:
#   - only parameters under the v1-trainable prefixes moved, against every reference: n2b vs the parent 9bac2fa0;
#     n2a vs its init ed8c616b AND vs the root parent 9bac2fa0;
#   - every tensor is finite;
#   - the sha differs from every reference;
#   - config.json equals the parent config;
#   - the file strict-loads the way predict_unet_transformer.load_model loads BIOHUB_SECONDARY_WEIGHTS in x138.
# A failing student is recorded and skipped, and the other one is still exported. The detection proxy ran in each worker
# and is in <label>_log.json.
import traceback

BaseModel = trainer.UNetNodeTransformer


def _build_base_model():
    return BaseModel(
        unet=trainer.TemporalUNet3D(
            in_channels=1,
            out_channels=config["unet_out_channels"],
            layers=config["unet_layers"],
        ),
        unet_out_channels=config["unet_out_channels"],
        pos_feat_dim=4 * trainer._POS_EMBED_DIM,
    )


_probe_model = _build_base_model()
_last_block = len(_probe_model.unet.decoder_blocks) - 1
del _probe_model
TRAINABLE_PREFIXES = (f"unet.decoder_blocks.{_last_block}.", "unet.head.", "detect_head.")
REFERENCES = {
    "n2a": {"init_ed8c616b": (secft_all_state, SECFT_ALL_SHA256), "root_parent_9bac2fa0": (initial_state, expected_initial_sha256)},
    "n2b": {"parent_9bac2fa0": (initial_state, expected_initial_sha256)},
}


def _compare(new_state, ref_state):
    changed, unchanged_trainable, param_deltas = [], [], {}
    for key, old in ref_state.items():
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
    return changed, unchanged_trainable, unexpected_frozen, param_deltas


def _sanity(label, student):
    candidate = student["candidate"]
    new_state = torch.load(candidate, map_location="cpu", weights_only=True)
    assert list(new_state) == list(initial_state), "state-dict keys differ from the teacher"
    candidate_sha256 = hashlib.sha256(candidate.read_bytes()).hexdigest()
    assert candidate_sha256 == student["sha256"], "candidate changed since TRAIN_DONE.json"
    out = {"candidate_sha256": candidate_sha256, "trainable_prefixes": list(TRAINABLE_PREFIXES), "vs": {}}
    for ref_name, (ref_state, ref_sha) in REFERENCES[label].items():
        assert candidate_sha256 != ref_sha, f"new weights are byte-identical to {ref_name}"
        changed, unchanged_trainable, unexpected_frozen, param_deltas = _compare(new_state, ref_state)
        if unexpected_frozen:
            print(f"WARNING [{label} vs {ref_name}]: trainable weights that did not move:", unexpected_frozen, flush=True)
        out["vs"][ref_name] = {
            "ref_sha256": ref_sha,
            "changed_keys": changed,
            "unchanged_trainable_keys": unchanged_trainable,
            "param_deltas": param_deltas,
        }
        print(f"[{label}] sanity vs {ref_name}: {len(changed)} tensors changed, all under {TRAINABLE_PREFIXES}")
        for key in changed:
            print(f"  {key:45s} max|d|={param_deltas[key]['max_abs']:.3e}  rel_l2={param_deltas[key]['rel_l2']:.3e}")
    _candidate_config = json.loads(candidate.with_name("config.json").read_text(encoding="utf-8"))
    assert _candidate_config == config, (_candidate_config, config)
    _strict_check = _build_base_model()
    _strict_check.load_state_dict(new_state)  # strict=True, same construction as load_model()
    del _strict_check
    out["all_finite"] = True
    out["strict_load"] = True
    print(f"[{label}] sanity OK: all finite; strict load OK; new SHA256 {candidate_sha256}", flush=True)
    return out


SANITY = {}
SANITY_FAIL = {}
for _label, _student in STUDENTS.items():
    try:
        SANITY[_label] = _sanity(_label, _student)
    except Exception as exc:
        traceback.print_exc()
        SANITY_FAIL[_label] = repr(exc)
        print(f"[exp77] {_label}: SANITY FAILED -> not exported: {exc!r}", flush=True)
EXP77_LOG["sanity"] = SANITY
EXP77_LOG["sanity_failures"] = SANITY_FAIL
if "n2a" in SANITY and "n2b" in SANITY and STUDENTS["n2a"]["sha256"] == STUDENTS["n2b"]["sha256"]:
    print("WARNING: n2a and n2b are byte-identical", flush=True)  # cannot happen with different inits; logged, not fatal
print(f"[exp77] sanity passed: {sorted(SANITY)}; failed: {SANITY_FAIL or 'none'}", flush=True)
for _label in sorted(SANITY):
    _proxy = (WORKER_RESULTS[_label].get("worker_log") or {}).get("detection_proxy", {})
    print(f"[{_label}] detection proxy totals: {_proxy.get('totals', _proxy)}", flush=True)
