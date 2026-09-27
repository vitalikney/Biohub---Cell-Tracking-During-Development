initial_weights = secondary_weights
actual_initial_sha256 = hashlib.sha256(initial_weights.read_bytes()).hexdigest()
expected_initial_sha256 = "9bac2fa0dadc4a6fc1899e0caf187f4b553e0a7cd90ba1261a68b35ffe9e305f"
assert actual_initial_sha256 == expected_initial_sha256, "Initial weight SHA256 mismatch"
config = json.loads(initial_weights.with_name("config.json").read_text(encoding="utf-8"))
initial_state = torch.load(initial_weights, map_location="cpu", weights_only=True)
data_dir = competition / "train"
names = sorted(
    path.stem for path in data_dir.glob("*.zarr")
    if path.with_suffix(".geff").exists()
)
assert names, f"No annotated training datasets found in {data_dir}"
split = {"split": 0, "train": names, "test": []}
splits_path = run_dir / "splits.json"
splits_path.write_text(json.dumps([split], indent=2), encoding="utf-8")
print(f"Train: {len(names)}; local validation disabled", flush=True)
