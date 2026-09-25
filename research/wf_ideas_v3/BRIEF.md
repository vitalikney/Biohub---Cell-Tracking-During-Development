# Ideas workflow v3 — brief (written 2026-09-25 ~11:00 UTC)

Target set by the user: **0.99 by 29 Sep**. Every research agent in `research/wf_ideas_v3/` reads this file first.

## 1. Where we are
- Kaggle "Biohub - Cell Tracking During Development": detect zebrafish nuclei in 3D+t light-sheet videos (~100 frames,
  64x256x256 voxels, scale z,y,x = 1.625, 0.40625, 0.40625 um; median true step ~1.8 um/frame; sister separation
  ~9-10 um), link them across frames, find divisions. Code competition: notebook <= 12 h, no internet, output
  `submission.csv`. Public LB ~29% of test (one embryo); private ~71% (other embryos, unseen). Hidden test embryos
  differ from the two train embryos (44b6: 71 clips, dense, 0.2-1.3% annotated; 6bba: 128 clips, 13-15% annotated).
- Metric (official code: `tools/official/`, rules in `tools/official/metrics.md`): score = adjusted edge Jaccard +
  0.1 x division Jaccard. adj_edge per video = J_edge x (1 - 0.1*(N_pred - N_est)/N_est), weighted by GT edge count
  (fewer nodes than N_est is a bonus). GT is SPARSE: edges among unannotated cells are free; an edge is FP only if an
  endpoint matches a GT node linked differently. Matching: 7 um, per-timepoint optimal assignment. Division J needs a
  local fork with two distinct daughter branches ("merely sharing a weakly connected component is not sufficient").
- PUBLIC LB (ours): best **0.950** = exp51 (our exp48 stack + the x138 V1284 coordinate head; probe 31) and exp52
  (+ float output coords, tie). exp48 = 0.948. Our public division J ~0.36 (removing every fork: 0.947 -> 0.911), so
  our public adjusted edge term is ~0.91. LB top on 24 Sep: 0.969-0.975; 41 teams at 0.953 (public notebook
  `anvithpothula/biohub-x138`).
- PENDING (submitted 25 Sep, results expected ~17:00-20:00 UTC): #34 = exp56 = x138 VERBATIM on our account (expect
  0.953) and #35 = exp57b = x138 + our DaughterNet division insertion (+12 forks, nodes identical). Rules: #34 = 0.953
  -> x138 is the new base; #35 > #34 -> x138 + insertion is F1.
- x138 stack (`experiments/ext_x138/DIFF.md`, kernel `experiments/exp56_x138_verbatim/`): TemporalUNet3D detector
  (2 seeds, 8-view TTA, threshold 0.965, 3 um NMS) + V1284 coordinate head (224->32->3 MLP on frozen UNet features,
  shift <= 2 um, float coords, trilinear gather) -> SimpleNodeTransformer edge scorer -> ILP -> thtennant chain
  (flow-prior relink with a 7 um tight gate, READMIT of discarded peaks, sub-threshold gap filler, DeepCenter 0.25,
  ILP timeout) -> safe divisions -> short-track filter -> linefit. The head adds +0.007 on x138's base but only +0.002
  on ours: the post-ILP stages consume node POSITIONS.
- Local lab (friend A's cache of the public exp39 stack on all 199 train videos, official metric): exp39 0.9143; edge
  TP 122,151 / FP 6,846 / FN 6,732; annotated node recall 0.983; divisions TP 23 / FP 43 / FN 128. FN anatomy: ~2,700
  "swap"-type FN are NODE POSITION errors (annotated nucleus sits between two of our tracks; matches 4.4 um vs 1.8 um
  for correct edges; oracle +0.03-0.046); ~31% of FN involve a node the detector never produced; the loss is a DENSITY
  problem (densest 6bba quartile = 52% of the loss, Spearman(J, nodes/frame) = -0.66); 44b6 misses are mostly
  under-segmentation. Files: `experiments/l2_daughternet/edge_anatomy/*.md`.
- LAB CAVEAT (quantified twice on the LB): the public detector AND edge network were trained on all 199 train videos,
  so any rule trusting their confidence looks +0.01..+0.016 locally and gives 0 on the LB (edge filter #29 0.947, #30
  0.946). Changes that do not lean on network confidence transfer better (division insertion: lab +0.0019 -> LB +0.001).
  44b6 clips are overlapping space-time crops of ONE public recording (the Ultrack "dorado" movie). LB noise ~0.003
  (two byte-identical public notebooks scored 0.946 / 0.942).
- Retraining so far: our all-199 scratch detector = 0.920 as secondary; fine-tuned primaries 0.944/0.943 vs 0.947;
  head retrain on 199 failed its embryo-held-out kill test (learns 6bba's annotation z offset). Forum: a top-3 team says
  detector retraining gave most of its gain; top teams at 0.969-0.975 retrained models.
- Previous idea workflow (v2, `research/wf_ideas_v2/FINAL_REPORT.md`) concluded: expected ~0.955, ceiling ~0.962,
  0.97 unreachable by post-processing alone. You may disagree - but with evidence.
- CLOSED lines (re-open only with a NEW mechanism or a clear error in the old test; list the error): detector
  fine-tunes on the pilkwang stack, weight soups, TTA variants (Z-flip, axis-flip), relink knobs, global-shift relink,
  AdaBN, DivNet veto, HOCT, Trackastra, synthetic data, dorado-only DaughterNet, division pair model, duplicate
  clustering (3 um NMS already), edge filter / stitch, float output (tie), head retrain on 199 (kill test), leaf prune
  on x138 (removes readmitted nodes). NOTE: flow-prior relink / readmit / gap filler were "neutral" on our base but are
  exactly what makes the head work on x138 - a closure on one base does not always hold on another.

## 2. Time and resources (plan backwards from the deadline)
- Now: Fri 25 Sep ~11:00 UTC. Kaggle final deadline 29 Sep 23:59 UTC; the user ticks the 2 finals by **29 Sep 20:00
  UTC**. Scoring latency 7-10 h => the LAST submission that can inform the finals goes in ~**29 Sep 10:00 UTC**.
- LB slots: 1 left on 25 Sep UTC, then 5 per day on 26, 27, 28, 29 Sep (reset 00:00 UTC) = 21 slots, shared by the
  team; each submission needs the user's explicit OK. A probe needs: kernel build (0.5-2 h agent work for a new patch
  incl. tests; `tools/build_probe_kernel.py`) + a private Kaggle run on the 4 dummy test videos (15-40 min GPU) + the
  submission's own scoring run (the x138-type notebook takes several hours on the hidden test; the 12 h limit is hard).
- GPU: Kaggle vitaliineibauer ~0 GPU-h left until the reset on 26 Sep 00:00 UTC, then 30 GPU-h/week (2xT4 or P100,
  max 2 concurrent sessions, 12 h per session, no internet in kernels; Kaggle CPU kernels 4 vCPU/30 GB are free).
  Kaggle sasyami (friend A's account) ~30 GPU-h/week. Kaggle gsfatakhov (friend B) is inactive - do not plan on him.
  Colab: one free T4 in the user's browser (session limits; the 82 GB competition data must be fetched per session -
  subsets only). Friend A: RTX 5070 Ti 16 GB (Windows 11, PyTorch 2.9.1/cu128), full competition data (82 GB) and lab
  caches locally; availability uncertain (PC rebooted 24 Sep; waiting for #34). Known speeds: detector retrain from
  scratch on all 199 ~23 h on the 5070 Ti; 1200-iteration fine-tune ~1 h; V1284 head capture on 199 videos 7.2 Kaggle
  GPU-h. Friend C = friend A's MacBook Air M4 16 GB, CPU only (image-free lab grids from caches).
- THIS CONTAINER (where you run): 4 CPU, 15 GB RAM, no GPU, NO competition data, NO Kaggle access. Network: WebSearch
  works; WebFetch works for github.com; curl works for raw.githubusercontent.com and PyPI (you may `pip install`).
  BLOCKED by policy: kaggle.com, arxiv.org, biorxiv.org, forum.image.sc, semanticscholar, openreview, huggingface -
  try at most once, then use search snippets or GitHub mirrors (READMEs, code, papers' repos). The user may connect a
  browser later: when you need a Kaggle page, write it into your `browser_todo` list instead of guessing its content.
- You may run light python here (<= 10 min, no training), e.g. the official metric in `tools/official` on SYNTHETIC
  graphs to check metric arithmetic.

## 3. Policy
- Legitimate gains only: public external data for TRAINING is allowed (Zebrahub / Ultrack dorado etc.). We do NOT
  match hidden test clips against public recordings or use public tracks as test labels (team policy + hosts'
  statement). Transductive test-time tricks (e.g. consensus across overlapping test crops) go to a separate
  "needs user decision" list, never into the default plan.
- Nobody but Vitalii submits. Agents never submit, push kernels, or contact anyone.
- Honesty: cite a file path or URL for every number; mark guesses as guesses. Saying "0.99 is unreachable, here is the
  best reachable plan and what 0.99 would take" is a valid outcome; inflating gains is not.
