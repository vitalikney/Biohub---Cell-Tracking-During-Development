# value skeptic notes: M2 exp60 6bba extension (2026-09-25T17:49:25Z)
- no prior JSON answer found; starting
- 2026-09-25 (UTC) clip accounting (experiments/l2_daughternet/splits.json divisions_per_video + experiments/exp60_trainlab/split.json):
  6bba 128 clips / 125 GT div = bed 39 clips/88 + clean 78 clips/17 (61 clips with 0 div, 17 with exactly 1) + 10 x138 head stems/20
  (INCLUDES 6bba_05db0fb1 = 3 div) + twin 6bba_05b6850b/0. The idea's "+ dummy twin 05db0fb1 (3)" double counts: max bed = 125 div
  (+42%), not 128 (+45%); honest (head-free) bed = 105 div (+19%) -> SE of a TP-count arc shrinks by only ~1-sqrt(88/105) = 8%.
- DeepCenter split_manifest: train = 71 44b6, VAL = 128 6bba (research/wf_ideas_v3/browser_intel.md s6.1 item 2) -> 6bba was the
  checkpoint-selection set (history.csv 500 rows), honest for weights-fit, mildly selection-biased.
- Detector/edge net/seed314159 all trained on 199 (discussion 742064; memory edge-filter finding): fork candidate geometry on ANY train
  clip is in-sample -> the bias that killed the edge filter (+0.016 lab, 0 LB) is not reduced by more 6bba clips.
- PRIOR LB EVIDENCE on the same knob (CONTEXT.md l.698-704, 2026-09-11): sjlee101's own forks of the 0.947 stack, DeepCenter safe-div
  threshold 0.15 -> 0.946, 0.20 -> 0.947, 0.25 -> 0.947 (public). The public arc over 0.15-0.25 is flat to within 0.001 -> a K3b
  t* in that range is very unlikely to show the R4 +0.002 on LB; the lab arc only decides whether a slot is spent.
- Metric ceiling (score = adj_edge + 0.1*div_J, micro-averaged): on the 39-clip bed, div_J ~ TP/(TP+FP+FN) with ~88 GT; one net TP
  flip ~ +0.008 div_J -> +0.0008 score, so the E5 lab gate +0.002 = ~3 net flips. Nodes identical under K3b -> no node-multiplier
  term; each fork adds one edge (tiny edge-J term, FP only when both endpoints are annotated).
- Real merit found: exp60's bed was picked "most GT divisions first" -> 30% of 6bba clips carry 70% of its divisions, so the
  bed over-weights TP opportunities vs FP-fork opportunities (~2.3x) and biases t* permissive. The 61 zero-division clean clips
  are the only way to see population-density FP forks. But it only acts as a VETO.
- VOI: P(39-bed passes E5) ~0.3 (plan) x P(ext flips it) ~0.2-0.3 x residual loss that R4's LB gate would not catch
  (~0.15 x 0.0015) ~ 1-2e-5; and K3b's intended role is F2-variance where final = max(F1,F2), so a false pass costs little and a
  false veto removes an upside option -> VOI ~0, maybe slightly negative. Claimed +0.0001..+0.0003 not supported.
- Timing: exp60 shards A/B already running tonight on this week's leftover quota (CONTEXT 17:20/17:55 UTC); extension would need
  new agent code (split_ext + trainlab EXT group) during the unattended night.
- VERDICT: refuted on value. Fix: lazy/conditional - run only the 78 clean clips (2 shards) and only if the 39-bed passes E5;
  fix the accounting (105 honest div, not 128); treat 10 head stems as excluded, not "reported separately".
- 2026-09-25T17:52:04Z final JSON written
