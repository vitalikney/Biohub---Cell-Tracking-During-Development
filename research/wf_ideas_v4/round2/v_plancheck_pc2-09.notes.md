# PC2-09 plancheck notes (2026-09-25T20:22:57Z)
- 20:25Z GT geff divisions (outdeg>=2, tools/score_geffs._load_gt_and_scale): 44b6_0113de3b 0 (52 nodes), 44b6_0b24845f 0 (51), 6bba_05b6850b 0 (861), 6bba_05db0fb1 **3** (1229 nodes, 1183 edges). Finding claim 'no matchable GT divisions' was only shown on 05b6850b.
- tl.official_eval per dummy clip (exp56 / K2 / exp57b dummy CSVs in _dl/ vs train/<stem>.geff):
  - 44b6_0113de3b: forks 35/39/39, div TP/FP/FN 0/0/0
  - 44b6_0b24845f: forks 6/6/6, 0/0/0
  - 6bba_05b6850b: forks 5/9/9, 0/0/0 (edge_J 0.980)
  - 6bba_05db0fb1: forks 16/21/20, **div 0/0/3** (edge_J 0.8724 / 0.8767 / 0.8724)
  Fork totals 62 (exp56) / 75 (K2) match the finding; tp_forks and fp_forks are empty everywhere, so every existing fork is ignored. BUT the claims "no matchable GT divisions" and "0/0/0" are false on 05db0fb1: its 3 GT divisions are all FN.
- Consequence: removal riders (forkmid/forkblob) cannot move division counts on dummies (no TP/FP fork to remove), so for them the finding holds. Additive riders (K3b DeepCenter threshold, insertion) CAN turn FN->TP or add FP forks on 05db0fb1, so "can never show benefit" is wrong. 05db0fb1 is also in split.json excluded.x138_probable_train, so any such signal is in-sample and not evidence about private anyway.
- Prior art: FINAL_REPORT §e gates 3-5 are plumbing gates (node equality, edge diffs), not harm gates; CONTEXT L7 already calls dummy-local deltas in-sample artefacts. The novelty of the action is small.
- 20:30Z verdict written: refuted=true (partly false fact; corrected wording in fix)
