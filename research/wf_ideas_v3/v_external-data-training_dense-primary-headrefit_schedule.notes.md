# notes Fri Sep 25 11:14:44 UTC 2026 schedule skeptic dense-primary-headrefit
- read BRIEF; value sibling json REFUTED (central -0.002, feasible=false). Idea-1 schedule notes: only a start line (no verdict yet).
- 11:25 UTC checks (all internal, no web needed):
  * tools/dorado_clips.py (idea 1's dense clip writer) DOES NOT EXIST; data_external/ absent in container; existing dorado dataset vitaliineibauer/biohub-dorado-crops = 5x16x32x32 DaughterNet crops, NOT full-volume clips+geff usable by train_unet_transformer.py (single --data-dir, l.1207-1248 -> needs symlink farm + 1:1 sampler patch).
  * build_probe_kernel.py --base x138: only divinsert|leafprune (docstring l.12-14; CONTEXT resume block). PRIMARY_OVERRIDE exists only in exp39/exp48-lineage notebooks (popped in x138 comparison, ext_x138/DIFF.md l.74,92) -> new primary+head patch for x138 cells 3/4/5 needed (~2-3 h + byte-identity tests).
  * capture builder = exp51-based (exp48 stack), not x138; asserts anvithpothula/biohub-v1284-head-s075; local_capture.py hardcodes PRIMARY_SHA 12f6881e (l.56) -> --primary knob needed (~1 h).
  * train_coordhead.py has no --stems flag; 20-movie restriction = pass a folder with 20 npz (OK). x138 head's 20 movies are x107's capture (DIFF.md l.24); our "same 20" = heuristic x138_probable_train (l.197).
  * capture cost: 7.2 GPU-h/199 (CONTEXT l.1488) -> 20 videos ~0.7 GPU-h + setup; idea's number OK.
  * scoring latency proxy ~7.5 h (#31 17:09->00:39); x138 hidden runtime not in repo.
  * Probability chain: P(dataset by 26 Sep 07:00) ~0.6 x P(idea-1 gate) ~0.33 x P(own OOS gate a) ~0.5 x P(head kill test b) ~0.5 x P(no slip) 0.8 x P(x138 base) 0.85 ~= 0.034. Execution-only (no gates) ~0.6x0.8x0.85 ~= 0.41. Both < 0.70 -> REFUTE.
