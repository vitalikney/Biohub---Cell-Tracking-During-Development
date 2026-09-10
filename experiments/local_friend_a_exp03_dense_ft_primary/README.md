# Friend A dense primary fine-tunes

The root-level `friend-a-dense-pipeline.ipynb` is the only entry point. It implements the revised 2026-09-10 Friend A
plan: STEP 1c followed by same-machine sparse/dense fine-tune comparisons of the pilkwang primary, then an optional
183-video fine-tune of the winning dense recipe.

Data, teacher graphs, predictions, and weights stay outside Git. The notebook writes compact results here.

Completed teacher chunks, dense graphs, fine-tune variants, and evaluations resume independently. Interrupting an active
fine-tune restarts only that variant (about 1 hour for 1200 iterations; about 2 hours for 2400 iterations).
