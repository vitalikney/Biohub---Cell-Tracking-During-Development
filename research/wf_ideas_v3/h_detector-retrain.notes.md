# h_detector-retrain notes (lens: model retraining before 29 Sep)
- 2026-09-25 ~11:05 UTC: started; read BRIEF.md; no prior JSON.

- 11:15 read experiments/coordhead_retrain/out_full_P.log, out_full_Q.log (P=no debias, Q=--debias embryo; both Huber 0.5, 120 ep, 125,700 pairs, 30 s CPU fit).
  Embryo-held-out mean dist (um): 6bba->44b6 none 1.499 / public 1.296 / P 1.452 / Q 1.378; 44b6->6bba none 1.720 / public 1.567 / P 1.570 / Q 1.588.
  7 um re-match counts differ by <=5 of 20k (44b6) and <=50 of 112k (6bba): the head barely changes metric matching directly.
- KILL-TEST CRITIQUE: 'public' reference is embryo-IN-sample (x138 validator trained on 10 stems per embryo; 44b6 clips are overlapping crops of one recording,
  so 'without x138 train videos' does not remove leakage). Kill test compares out-of-embryo new head vs in-embryo public head -> biased against retrains.
- Detector target in tools/repo/scripts/train_unet_transformer.py l.560-580: single positive voxel at gt/ds .long() (floor), BCE; no Gaussian, no offset head.
  v2 notes: GT coords are integer voxels on both embryos; 'none' bias z +0.18 (44b6) / +0.82 (6bba) um -> embryo-specific convention (train_coordhead tables).
- RESULTS.md: every detector fine-tune/retrain so far <= public on LB (exp33 0.944, exp27 scratch secondary 0.920, soup 0.943); scratch 6bba 20 ep = 0.68 on 44b6 (pilkwang 0.88), 0.833 on own train.
- Forum (discussions_summary l.216): dense fine-tune head-only -0.0033, head+encoder under frozen linker -0.0377 (Le Quang Canh).
