# check_corwin_secondary - skeptic check of exp74_k2_secw_corwin (K2 + secswap to Corwin's CC0 secondary)

- 2026-09-27 11:30-11:50 UTC. Nothing pushed, uploaded, submitted or committed.

## Build
- Rebuilt with the exact build_command into experiments/_scratch_skep74 (--out-dir; deleted afterwards): ipynb sha256
  17835c019b550e28707fc69f3c5c19973a93c072ab8f79f6fb91cd5775106d9a = staged; kernel-metadata.json and probe.json
  byte-identical (cmp). Third identical build (builder currently being edited by another session: secswap unaffected).
- Diff vs K2 exp58 (1f1ddb6d, verified unchanged): 14/14 cells, notebook metadata equal; cell 0 = preset header comment +
  2 os.environ lines (SECONDARY_EXPECTED_SHA256, SECONDARY_ARTIFACT_MANIFEST); cell 3 = the one pinned-sha line -> env
  lookup with the pilkwang default. Nothing else. kernel-metadata = K2's + dataset vitaliineibauer/biohub-secw-corwin-v1
  (same docker pin, T4, private, internet off).
- pytest -q tests: 440 passed (count grew from 416 because other sessions added tests). Tracked *.ipynb /
  kernel-metadata.json: no modifications (finals #37 = K2 exp58, #38 = exp58n untouched).

## Runtime risk (cell 3)
- Finder selects by model.weight_sha256 == expected: explicit path first, then pilkwang paths, then rglob. The pilkwang
  manifest has a different sha -> skipped. So a wrong mount path costs ~210 s of rglob but still finds our manifest; the
  dataset missing = FileNotFoundError (loud). A silent K2 rerun is impossible. Copied weights re-hashed -> RuntimeError on
  mismatch.
- Repack: pth sha 1168...27d, config sha e9b4e396... (match Corwin's manifest). ARTIFACT_MANIFEST.json has
  model.weight_sha256. kaggle CLI --dir-mode zip = shutil.make_archive(root_dir=weights/) -> weights.zip holds
  unet_transformer/split_0/... = what copy_or_extract_tree extracts. Both modes are OK.
- Checkpoint format (static pickletools disassembly of data.pkl, nothing unpickled/executed): bare OrderedDict
  state_dict, globals only torch FloatStorage/LongStorage/_rebuild_tensor_v2 + OrderedDict, 136 keys
  (unet.* + transformer.*), key list IDENTICAL to our own exp08 fine-tune weights (already loaded fine by our kernels);
  config.json identical to exp08's. Storage location 'cpu' (ours 'cuda:0'; irrelevant with map_location). Load risk: low.
- Runtime = K2's (same architecture). Dataset does NOT exist yet (datasets files -> 403).
- GPU 11:36Z: exp71-secft-all RUNNING + exp70n-k2-thr03 QUEUED = 2 sessions -> no dummy push allowed.

## Can it move the public display (needs >= 0.955)?
- CORRECTION to the prep note: the swing is NOT small. Cell 4 mixes detection as (1-0.80)*primary + 0.80*secondary, so
  the secondary is the DOMINANT detector (80% of detection logits) plus 0.15 edge weight + low-margin link consensus.
  Swapping it is the biggest single-model lever in K2, not a bounded nudge.
- Direction prior is negative: Corwin's k10_subvox.py (ZEUS 14:4xZ) measured pilkwang's ("the vendor's") secondary vs
  theirs: placement hit rate at 3 um 0.68 vs 0.61, d_p90 4.2 vs 5.1, "+0.006 public". With the linker linking by
  distance and 80% of detection coming from the secondary, worse placement goes straight into edge loss. Corwin's 0.965
  most likely did NOT serve this model. Caveat: the uploaded file is SERVED_A_ep025_034_swa10 (a SWA export, maybe newer
  than the 14:4x comparison) -> some chance it is better.
- The fusion knobs (0.80 / 0.15 / 0.35 / 0.48) were tuned for pilkwang's seed -> extra negative drift.
- Estimate: public 0.938-0.957, centre ~0.948; P(>= 0.955) ~10%. The downside is free for the display (the best score is
  kept); the only cost is a slot + ~7.3 h of scoring.
- Overlap with exp72 (00:05Z, K2 + OUR retrained secondary): same lever class (secondary swap). exp72's result is the
  better-informed test; exp74 is the more-varied second draw. It is reasonable as a risk probe, not as a top pick.

## Fixes / to-do before submitting
1. Correct expected_public to 0.938-0.957 (centre ~0.948) and drop the "swing is bounded" claim (0.80 detection weight).
2. Upload needs a go: `PYTHONIOENCODING=utf-8 python -m kaggle datasets create -p experiments/ds_secw_corwin_v1 --dir-mode zip`;
   then `datasets status` = ready and `datasets files` shows ARTIFACT_MANIFEST.json + weights(.zip) at the root.
3. Dummy only when < 2 sessions are active; gates: 'Secondary artifact: .../biohub-secw-corwin-v1', 'Secondary SHA256:
   1168...27d', 'Dual-seed ensemble: requested=True weights_found=True', COMPLETE, Traceback 0; node/fork counts vs K2
   (122,252 nodes / 75 forks); nodes moving > ~10% or forks < ~50 = look closer before spending a slot.
4. Order: after exp72 is scored, or earlier only if a free slot would otherwise go unused. If exp72 (our secondary) lands
   >= 0.955, exp74 adds little; if exp72 drops, exp74 is still an independent draw.
5. Optional stronger-variance follow-up (new patch, not built): make the hard-set BIOHUB_SECONDARY_DETECTION_WEIGHT
   patchable (e.g. 0.5) so a swapped secondary does not own 80% of detection.
