# prep_corwin_secondary - exp74 = K2 + Corwin's CC0 secondary (secswap)

- 2026-09-27 11:20 UTC. Live file listing of corwin1979/biocel-secw-3f1c84ad (CC0-1.0, 30 downloads): FLAT layout,
  3 files at the root: MANIFEST_SHA256.json (809 B), config.json (165 B), edge_predictor_best.pth (8,356,270 B).
  Downloaded to the scratchpad; sha256 edge_predictor_best.pth = 1168050414f7286d1b66692a2b57cc6a9e1d6068451627bfd6313ec459dde27d,
  config.json = e9b4e396... (both equal Corwin's manifest).
- LAYOUT DOES NOT MATCH x138's finder (code cell 3, _find_secondary_artifact_root + copy_or_extract_tree). Missing:
  1. no file named ARTIFACT_MANIFEST.json (Corwin's is MANIFEST_SHA256.json; the finder opens only the explicit path, two
     pilkwang paths and rglob('ARTIFACT_MANIFEST.json'));
  2. no key model.weight_sha256 (Corwin's manifest has files."edge_predictor_best.pth" instead);
  3. no weights/ folder or weights.zip: the pth and config.json sit at the dataset root, while x138 copies
     <manifest dir>/weights[.zip] and expects unet_transformer/split_0/{edge_predictor_best.pth, config.json} inside.
  So a manifest path /kaggle/input/datasets/corwin1979/biocel-secw-3f1c84ad/... cannot work (the builder also refuses any
  file name other than .../ARTIFACT_MANIFEST.json). Attached raw with the new sha, the finder skips every manifest, rglob
  finds only pilkwang's (sha != new expected) -> FileNotFoundError in cell 3 = loud crash, never a silent K2 rerun.
- FIX (prepared, NOT uploaded): repack as our private dataset vitaliineibauer/biohub-secw-corwin-v1 (slug free, checked
  11:28Z) in experiments/ds_secw_corwin_v1/: ARTIFACT_MANIFEST.json {model.weight_sha256 = 1168...27d, provenance},
  weights/unet_transformer/split_0/{edge_predictor_best.pth, config.json} byte-identical to Corwin's, Corwin's manifest
  kept verbatim as CORWIN_MANIFEST_SHA256.json, dataset-metadata.json (CC0-1.0). The pth is git-ignored (experiments/**/*.pth).
  secondary_manifest_info is only assigned in x138 (no field read), so the minimal manifest suffices.
  Local simulation of finder + copy_or_extract_tree: dir mode OK, zip mode (shutil.make_archive of weights/, what
  `--dir-mode zip` uploads) OK, sha matches in both.
- Upload command (needs a go from the orchestrator/user; not in this task's allowed actions):
  PYTHONIOENCODING=utf-8 python -m kaggle datasets create -p experiments/ds_secw_corwin_v1 --dir-mode zip
  then `python -m kaggle datasets files vitaliineibauer/biohub-secw-corwin-v1` must show ARTIFACT_MANIFEST.json + weights
  (dir or weights.zip) at the root; wait until the dataset is ready before pushing the dummy.
- 11:24 UTC BUILT experiments/exp74_k2_secw_corwin (kernel vitaliineibauer/biohub-exp74-k2-secw-corwin, private, T4,
  internet off, K2's docker; dataset_sources = K2's + vitaliineibauer/biohub-secw-corwin-v1). Command (Git Bash):

      export MSYS_NO_PATHCONV=1
      K="--set DIVINS_ENABLE=1 --set DIVINS_STEAL=1 --set DIVINS_CAP=4 --set DIVINS_FRAME_CAP=1 --set DIVINS_ALPHA=1 --set DIVINS_THRESH=0.4 --set DIVINS_DUMP=0"
      python tools/build_probe_kernel.py exp74_k2_secw_corwin --base x138 --patch divinsert --patch safetail --patch lowrefine --patch secswap $K --set REPAIR_DEADLINE_S=34200 --set DIVINS_DEADLINE_S=28800 --set LOWREFINE_ENABLE=1 --set SECONDARY_EXPECTED_SHA256=1168050414f7286d1b66692a2b57cc6a9e1d6068451627bfd6313ec459dde27d --set SECONDARY_ARTIFACT_MANIFEST=/kaggle/input/datasets/vitaliineibauer/biohub-secw-corwin-v1/ARTIFACT_MANIFEST.json --dataset vitaliineibauer/biohub-secw-corwin-v1 --note "exp74: K2 + secswap to Corwin's CC0 secondary (corwin1979/biocel-secw-3f1c84ad repacked as vitaliineibauer/biohub-secw-corwin-v1)"

  ipynb sha256 17835c019b550e28707fc69f3c5c19973a93c072ab8f79f6fb91cd5775106d9a (rebuilt twice, identical; another session
  was editing tools/build_probe_kernel.py at the time - its diff does not touch secswap).
  Diff vs K2 exp58 (1f1ddb6d, unchanged): cell 0 = preset comment + 2 knob lines; cell 3 = the one sha line. Nothing else.
- Tests: the first pytest run hit 6 collection errors while the other session was mid-edit of the builder; rerun 416 passed.
  Nothing committed, nothing submitted.
- GPU at 11:28Z: exp71 RUNNING + exp70n dummy QUEUED = 2 sessions -> no dummy push (and the dataset does not exist yet).
- Dummy gates to read: 'Secondary artifact: /kaggle/input/datasets/vitaliineibauer/biohub-secw-corwin-v1',
  'Secondary SHA256: 1168050414...27d', 'Dual-seed ensemble: requested=True weights_found=True', COMPLETE, node/fork counts
  vs K2 (a different secondary changes the edge/detection fusion, so counts WILL move; > ~10% node change = look closer).
- Risks: (a) Corwin's own note (k10_subvox.py, 19 Sep): pilkwang's secondary beat theirs by +0.006 public on placement ->
  EV plausibly <= 0; (b) checkpoint wrapping/key format not re-verified here (local unpickling of the external pth was
  blocked by the permission classifier; the 26 Sep note says 136 keys, same arch, identical config) - a mismatch crashes
  load_model loudly in the dummy, it cannot pass silently; (c) the fusion knobs (edge 0.15, det 0.80, low-margin 0.35,
  thr 0.48) were tuned for pilkwang's seed and stay hard-set; (d) runtime = K2's (same architecture).
