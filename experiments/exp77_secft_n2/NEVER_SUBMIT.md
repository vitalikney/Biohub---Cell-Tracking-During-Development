# NEVER SUBMIT

`vitaliineibauer/biohub-exp77-secft-n2` is a training notebook. It is never a competition submission.

- It writes no `submission.csv`. Internet is on, which a code-competition submission would reject anyway.
- User OK: "да, N2" (CONTEXT, 27 Sep 18:19 UTC), for a second, stronger fine-tune of about 3 GPU-hours. The push itself is done by the main session, not by the builder.
- It produces two fine-tuned secondary detectors, trained in parallel in one T4 x2 session. Each is a subprocess on its own GPU.

| run | GPU | init | lr | loader seed | length | output dir |
|---|---|---|---|---|---|---|
| n2a | CUDA_VISIBLE_DEVICES=0 | exp71 student `ed8c616b` (`vitaliineibauer/biohub-secft-all-v1`) | 1e-5 | 271828 | +1 epoch (epoch 2) | `/kaggle/working/secft_n2a/` |
| n2b | CUDA_VISIBLE_DEVICES=1 | pilkwang parent `9bac2fa0` | 3e-5 | 314159 | 1 epoch | `/kaggle/working/secft_n2b/` |

- Each output dir holds `ARTIFACT_MANIFEST.json` and `weights/unet_transformer/split_0/{edge_predictor_best.pth, config.json}`.
  - The manifest has `model.weight_sha256`, `model.parent_sha256` (n2a: `ed8c616b`, n2b: `9bac2fa0`), `model.root_parent_sha256` (`9bac2fa0`) and `model.lineage`.
  - This is the x138 secondary layout, the same as `biohub-secft-all-v1`. Each dir becomes its own private dataset, `biohub-secft-n2a-v1` / `biohub-secft-n2b-v1`. The exp70b + `--patch secswap` rungs then point at the new sha.
- `/kaggle/working/exp77_train_log.json` is the combined log. It holds the launcher, the sanity results, the artifacts and both workers' run logs, including each worker's in-sample detection proxy.
- `/kaggle/working/exp77_logs/` holds the worker stdout logs, the per-run JSON logs and the worker source.
- Both runs use the exp71 recipe (y3uanm v1):
  - the teacher is the frozen ORIGINAL pilkwang `9bac2fa0`, for n2a too;
  - the same loss and the same trainable modules; BN is frozen;
  - AdamW with a fresh optimizer state.
- Time caps:
  - each run's training hard-stops at 4.5 h and saves the student;
  - all training ends within 5.75 h of cell c04;
  - the launcher watchdog touches a stop file 5 min after a run's deadline, then kills the process group 20 min after it;
  - expected wall time is about 2.5-3 h (one epoch at about 0.40-0.50 s/it on each GPU); the hard bound is under 6.5 h.
- If only one GPU is visible, the runs go one after the other (n2a first) and share the window evenly.

Rebuild the notebook from the cell files (run from the repo root):

```
python experiments/exp77_secft_n2/build.py
```

`build.py` turns `cells/w05_exp77_worker.py` into a `%%writefile /kaggle/working/exp77_worker.py` cell. The other cells are
assembled as in `_lib/build_nb.py`. `c01`-`c03` are exp71's cells, byte for byte.

Local checks (CPU, no GPU):

```
python experiments/exp77_secft_n2/smoke/run_smoke.py      # fake trainer: 4 scenarios
python experiments/exp77_secft_n2/smoke/run_real_cpu.py   # real trainer, real teacher and exp71 student, 4 real videos
```

The 4 fake-trainer scenarios:
- parallel;
- 1-GPU sequential, with a loader-failure fallback and a hard stop;
- the watchdog stop file plus a kill;
- all runs failing, so the export cell raises.
