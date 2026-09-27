# scan_recheck notes (round 14, 2026-09-27)

2026-09-27T01:48Z start. scan_recheck.json did not exist -> fresh run. Chrome not used; no Kaggle API calls (quiet window 04:10-06:45Z respected anyway).
- Read: CONTEXT.md tail (l.2451-2770: R12-A3/A4/A9, RESUME POINT 22:46Z, probe 42, round-13 record, L5v2, exp71/exp72 governance), round13/REPORT.md,
  v3 FINAL_REPORT section i, s_merge.json dropped/candidates, experiments/RESULTS.md, research/KNOWLEDGE/IDEAS.md (refuted/tested rows).
- Excluded as already rechecked in rounds 2-13 (36 items): I-146, I-097/107, I-209, P6, I-049, I-020, I-034, I-147, I-148, I-108, I-202/231, I-075,
  I-028, I-077/078/066/067 (R2-RC-B), I-158, I-165, I-145, I-151, I-035, I-043, I-135, I-168, I-054, I-157, I-164, I-161/162, I-184, I-186/141,
  I-042, headroom family, I-041/029, I-058, I-079, I-276, I-177/179/180/181, I-222. Plus the closed list in the task.
- 01:55Z PICK A = I-106 (exp23 secondary with PILKWANG primary; 'never run; family closed after 4 negatives').
  CONTEXT l.316-318 (11 Sep): exp32 'was tested with exp03B as primary (both fine-tuned with the same recipe on the same 183 videos ->
  correlated errors). exp23 as secondary with the PILKWANG primary is untested'. CONTEXT l.175 A26 'untested with the pilkwang primary'.
  RESULTS l.37-47: every secondary swap ran on an exp03B-primary base (probe 5 exp20, 7 exp22, 10 exp27 = exp06 base; 13 exp32 = exp30 base).
  v_retrain.json (reach0955) '0 of 5': exp08 sec -0.016 (shares init with exp03B, 'no diversity' per RESULTS l.39), friendA ep21 sec -0.025
  (weaker scratch model), exp23 sec -0.007, exp03B primary -0.003, soup primary -0.004 -> 2 of 5 are primary swaps, 3 of 3 secondary swaps sit
  on the exp03B primary. x138 primary = pilkwang/biohub-tracking-support-pack-50ep-v1 (exp56 notebook, PRIMARY_ARTIFACT_MANIFEST default),
  secondary = pilkwang seed314159 (sha 9bac...), SECONDARY_DETECTION_WEIGHT 0.80. So exp72 (K2 + distilled FT secondary) = the I-106 class,
  never tested. CONTEXT 21:21Z line 'our model-swap record on the LB is 0/5' is the framing the 07:30Z Q1-Q3 push will quote.
- 02:05Z PICK B = I-063 DaughterNet v2 / v1+v2 average. CONTEXT l.1314-1327: v2 pool OOF parent-vs-cont AUC 0.875 vs v1 0.825 on the same
  rows (44b6 0.950 / 6bba 0.859); daughter 0.743 vs 0.718; SELECTION insertion v2 orphan +0.0010 vs v1 +0.0044, steal v2 cap6 +0.0032 vs v1
  cap4 +0.0058; the same entry says 'All L2 deltas on 64 videos are 1-4 division events, i.e. inside noise'. v1 itself shrank SELECTION +0.0058
  -> CONFIRMATION +0.0019 (l.1304-1307). v2 never ran on CONFIRMATION, x138 or LB. Ledger I-063 reason 'insertion worse than v1' overstates.
  Kernel weights: v1 5 flat folds vitalii_daughternet/fold_k.pt; kdn-train latest output likely v2 (v_divisions-x138_d1 feasibility).
- 02:15Z PICK C = I-069 D1 OOF insertion rescore. exp60 results.md l.13-30: ins35 in-sample 44b6/ALL +0.0058 (1/8/10 -> 2/8/9),
  6bba/ALL +0.0065 (15/17/73 -> 23/23/65: +8 TP/+6 FP, added precision 0.57). Honest v1 OOF on the old exp39 base, CONFIRMATION 135 videos
  (CONTEXT l.1304-1307): +0.0019, 44b6 +0.0015, 6bba +0.0021, TP 16->20 / FP 28->39 (added precision 4/15 = 0.27; Wilson 80% [0.149, 0.431],
  90% [0.126, 0.479]). 6bba lab control J 0.143 -> break-even J/(1+J) 0.125; private break-even 0.11-0.20 (s_merge C03). Public: P27->P28,
  P34->P35, P38->P37 all +0.001 = one embryo, one mechanism. R12-A3 (CONTEXT 21:31Z) cites 'insertion (lab +0.006, P(<0 on private) 0.10-0.15)'
  without the in-sample label. R12-A9(e) E set = {P27->P28, P34->P35, P38->P37, P28->P31}: 3 of 4 are the insertion.
- 02:25Z scan_recheck.json written (3 findings: R14-RC-A today, R14-RC-B info, R14-RC-C info). Done.
