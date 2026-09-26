# indarkarhana/biohub-dual-seed-frame-retention-guard-v1 (team Bio-Pirates, now 0.960; notebook last run 28 Jul 13:32 UTC; its own markdown: "Public score: 0.913 | Exact public-backbone reproduction: 0.912") - pulled 26 Sep 21:00 UTC
1. Pilkwang "Two Seeds Logit Blend" backbone (4 pilkwang datasets: deepcenter prior v1, temporal-unet3d seed314159 v1, tracking support pack 50ep v1, figures) + a label-free "frame retention guard": keeps the two-seed ensemble where the seeds agree and stops one weak seed from erasing a coherent group of candidates in an unusual frame (BIOHUB_RETENTION_GUARD, BIOHUB_DUAL_SEED_MIN_CANDIDATE_RETENTION).
2. ILP costs in the markdown: appearance 0, disappearance 1.5, division 1.0; DeepCenter confirms only marginal synthetic one-frame gap nodes; density-adaptive gap gate r = 2(5.8 + clip(0.04(s-6.5), +-0.125)) um.
3. Differs from x138: an old (July, 0.913-era) ancestor of the same family; x138 has since superseded every stage.
4. +0.001 over its reproduced backbone (0.913 vs 0.912) by the author's own numbers.
5. Verdict: nothing to take. Source: https://www.kaggle.com/code/indarkarhana/biohub-dual-seed-frame-retention-guard-v1
