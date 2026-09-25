# notes: schedule/feasibility skeptic, mirror-daughter-lowdet (2026-09-25T11:02:08Z)
- read BRIEF.md; sibling value verdict (lowdet-daughter-recovery, metric-math) refuted, ~0 gain
- 11:2x read sibling schedule verdicts: edge-evidence (refuted, P~0.15-0.3), divins-x138-lab-retune (x138 train cache 13-16 GPU-h, P~0.2 with gate)
- CONTEXT l.1259-1262 B35 step A: 0.90 full-frame pass 136->151/151 at +23.9% nodes (b35_step_a.md: 44b6 26/26, 6bba 125/125, max 73%); reach is 'within 20 um of an eligible one-child parent, >=3 um from nodes', NOT mirror-specific; graph = exp39, detector = public primary (in-sample)
- r1_hyp_divisions.json: 15 unreachable = 151-136 (exp39 graph); 30 TP / 2,537 FP geometry-only orphan pool: confirmed; r1 notes AUDIT3b: mirror 7.2 vs 7.1 um TP vs FP (no separation)
- x138 cell 0: BIOHUB_CACHE_DIR=/kaggle/working/edge_cache, LOWDET_THRESHOLD 0.3, READMIT 4um/0.965, GAPFILL >=0.5 3.5um exclude 2um, REPAIR_DEADLINE_S 27000. Lowdet peaks from _detect_cells_pooled on det_logits (downsample 1,4,4 grid => ~1.6 um quantisation). Dump exists ONLY at runtime on test; no train lowdet dump exists anywhere (repo, friend A B35 cache is exp39 primary at 0.90 on his PC)
- tools/div_insert.py docstring: 'nodes are never added or removed', 'nothing reads files' -> mirror branch breaks both invariants; candidate_triples only yields u with an admissible v, so the extra parents are never scored by DaughterNet today -> glue change + more score_nodes calls
- build_probe_kernel.py: DIVINS glue in filter_output_graph post-tail; DIVINS_DUMP writes pre-insertion graph+node_p; replay.py = exp39 tail only; no x138-on-train harness
- friend A: no commits since 24 Sep 04:12 MSK; told to wait for #34 then build x138 lab cache (format raw/ckpt/dc/divnet, lowdet npz not requested)
- v2: mirror-peak-daughter was merged into a dedupe cluster and not chosen in FINAL_REPORT
