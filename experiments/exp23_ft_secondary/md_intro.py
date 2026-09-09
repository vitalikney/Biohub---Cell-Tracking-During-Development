# exp23 — fine-tune the public pipeline's SECONDARY model (pilkwang seed314159) with the exp03B recipe

A = raw seed314159 model on the fixed 12-video holdout (leaky, sanity only). B = the same model fine-tuned 1200 it
(batch 8, lr 5e-5, BCE, window 2, seed 42) on the 183 non-holdout videos. Output `ft_weights/` goes to the Kaggle dataset
`vitaliineibauer/biohub-ft-weights/exp23` for friend B's honest check as SECONDARY in the full public pipeline (CONTEXT §10a B2).
