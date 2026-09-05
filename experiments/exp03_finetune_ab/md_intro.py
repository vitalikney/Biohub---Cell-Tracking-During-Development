# exp03 — fine-tune A/B on the fixed 12-video holdout

A = pretrained support-pack weights, raw model (UNet+transformer+ILP, no notebook post-processing).
B = same model fine-tuned on the 183 non-holdout videos with the settings in the config cell.
Both scored on the same holdout with the repo evaluator (competition metric code). No submission produced.
