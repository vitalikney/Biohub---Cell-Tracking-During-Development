# [exp77] Inputs beyond exp71. Cells c01-c03 above are exp71's, byte for byte. They install the wheels, copy the repo,
# patch the trainer and pin the pilkwang parent/teacher 9bac2fa0. They also write splits.json with all 199 videos and no test.
# This cell adds three things:
#   1. the exp71 student (ed8c616b, private dataset vitaliineibauer/biohub-secft-all-v1), the init of run A (n2a);
#   2. the sha of the PATCHED trainer file, so each worker subprocess can check it imports the same code;
#   3. the notebook clock that the launcher budgets against.
EXP77_T0 = time.time()
WORKING_ROOT = Path("/kaggle/working")
SECFT_ALL_SHA256 = "ed8c616bcc5990d3cccfe728d0e00469feb40ca8a0590137045f7ef225903f2e"

secft_all = choose_existing_dir(
    "secft_all (exp71 student)",
    [
        input_root / "datasets" / "vitaliineibauer" / "biohub-secft-all-v1",
        input_root / "biohub-secft-all-v1",
    ],
)
secft_all_manifest = json.loads((secft_all / "ARTIFACT_MANIFEST.json").read_text(encoding="utf-8"))
assert secft_all_manifest["model"]["weight_sha256"] == SECFT_ALL_SHA256, secft_all_manifest["model"]["weight_sha256"]
assert secft_all_manifest["model"]["parent_sha256"] == expected_initial_sha256, secft_all_manifest["model"]["parent_sha256"]
secft_all_weights = secft_all / "weights" / "unet_transformer" / "split_0" / "edge_predictor_best.pth"
assert hashlib.sha256(secft_all_weights.read_bytes()).hexdigest() == SECFT_ALL_SHA256, "exp71 student SHA256 mismatch"
assert json.loads(secft_all_weights.with_name("config.json").read_text(encoding="utf-8")) == config, (
    "exp71 student config differs from the parent config"
)
secft_all_state = torch.load(secft_all_weights, map_location="cpu", weights_only=True)
assert list(secft_all_state) == list(initial_state), "exp71 student keys differ from the parent"
_moved = [k for k in initial_state if not torch.equal(secft_all_state[k], initial_state[k])]
assert _moved, "the exp71 student equals the parent"
print(f"exp71 student: {secft_all_weights} | sha {SECFT_ALL_SHA256[:8]} | {len(_moved)} tensors differ from the parent",
      flush=True)

PATCHED_TRAIN_SCRIPT_SHA256 = hashlib.sha256(train_script.read_bytes()).hexdigest()
print("patched trainer sha256:", PATCHED_TRAIN_SCRIPT_SHA256, flush=True)
print("visible GPUs in the notebook process:", torch.cuda.device_count(), flush=True)
