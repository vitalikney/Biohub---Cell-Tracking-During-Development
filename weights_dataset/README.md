Fine-tuned UNet+node-transformer weights for the Biohub cell tracking pipeline (private experiments).
Each subfolder = one experiment: edge_predictor_best.pth + config.json (same format as pilkwang support pack).

- `soup03B_50/`: weight-space average (0.5/0.5) of the pilkwang primary (support pack 50ep, split_0) and exp03B
  (its 1200-it fine-tune). Same init/architecture -> linear interpolation is valid. Built 2026-09-11 for LB probe exp35
  (node-count mechanism: exp03B is more confident, +3.2% nodes at det 0.965; the soup sits half-way).
