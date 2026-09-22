# Friend A — B34 appearance-aware linker audit

Status: **blocked as a leak-free LOEO experiment; training was not started**.

The source requested by the 2026-09-23 Friend A plan was inspected from
[`giorgosin/notebook447aed80b2`](https://www.kaggle.com/code/giorgosin/notebook447aed80b2).
The downloaded notebook had SHA-256
`bf3b58785020ca4761c9d8a11d94182c7a032278ebe22f029ded0fc08cdf92de`.
It is kept under the git-ignored `external/giorgosin_trainer/` directory and is
not vendored by this commit.

## Why it cannot be called honest LOEO yet

1. The trainer requires the shipped public `edge_predictor_best.pth` and aborts
   when that checkpoint is absent. It loads the whole UNet, detection head and
   transformer. That checkpoint was trained on all 199 public videos, including
   both embryos. Starting either embryo fold from it leaks the validation embryo.
2. Its validation split is not embryo LOEO. The competition adapter hard-codes
   one `6bba` and one `44b6` video as validation, while its original path uses a
   random `VAL_FRAC=0.15` split.
3. The training schedule mixes external ZSNS/relay pairs unless the data path is
   redesigned. This does not implement the plan's two folds over the local 199
   videos.
4. It trains on GT-node pair features, whereas the requested inference path uses
   nodes from the public detector. The train/inference candidate distributions
   therefore differ.
5. It is not safely resumable: only a new best model is written. Optimizer,
   scaler, RNG state, epoch and the latest checkpoint are not saved every epoch.
6. The notebook is Kaggle/Linux-specific (`/kaggle/input`, `/kaggle/working`,
   cgroup and `libc.so.6` helpers). A Windows port needs explicit replacement and
   a smoke test before a long run.

## Decision needed before implementation

Choose one interpretation and record it in the plan:

- **Leak-free B34:** initialise each fold from weights that never saw its held-out
  embryo (or train from scratch), build true `6bba -> 44b6` and `44b6 -> 6bba`
  manifests, train on public-detector candidates, and save a complete checkpoint
  after every epoch. This is the only variant that may use the `+0.003 per
  embryo` LOEO gate, but it is a materially different and longer experiment.
- **Public-checkpoint regression:** keep the author's initialisation and measure
  whether appearance features improve the already-trained public stack. This can
  be useful engineering evidence, but it must be labelled in-sample/leaky and
  must not be reported as honest LOEO.

Until that choice is made, B34 remains unstarted. B33 can run independently.
