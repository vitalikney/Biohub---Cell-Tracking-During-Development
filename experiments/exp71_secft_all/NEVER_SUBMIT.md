# NEVER SUBMIT

`vitaliineibauer/biohub-exp71-secft-all` is a training notebook. It is never a competition submission.

- It writes no `submission.csv`. Internet is on, which a code-competition submission would reject anyway.
- Its only product is a fine-tuned secondary detector:
  - `/kaggle/working/secft/` holds `ARTIFACT_MANIFEST.json` and `weights/unet_transformer/split_0/{edge_predictor_best.pth, config.json}`.
  - `/kaggle/working/exp71_train_log.json` is the run log.
  - These become the private dataset `biohub-secft-all-v1`. An x138-based inference notebook (exp72) then consumes that dataset.
- Recipe: y3uanm `notebook0afc5663f6` (v1), kept verbatim where possible (see `cells/md_00_intro.py`).
- Pushing this kernel spends about 4.5 GPU-hours on a T4. It needs the user's explicit OK (plan R9: retraining).

Rebuild the notebook from the cell files (run from the repo root):

```
python experiments/_lib/build_nb.py experiments/exp71_secft_all/exp71-secft-all.ipynb \
  experiments/exp71_secft_all/cells/md_00_intro.py \
  experiments/exp71_secft_all/cells/c01_setup_v1.py \
  experiments/exp71_secft_all/cells/c02_sanity_read_v1.py \
  experiments/exp71_secft_all/cells/c03_splits_v1.py \
  experiments/exp71_secft_all/cells/c04_model_loss_v1.py \
  experiments/exp71_secft_all/cells/c05_exp71_control.py \
  experiments/exp71_secft_all/cells/c06_exp71_probe.py \
  experiments/exp71_secft_all/cells/c07_train_v1.py \
  experiments/exp71_secft_all/cells/c08_exp71_sanity.py \
  experiments/exp71_secft_all/cells/c09_exp71_export.py
```
