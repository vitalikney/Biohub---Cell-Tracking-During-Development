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
- 11:30 web: WebSearch ok. github.com/JunhaoLiXD/Biohub_Cell_Tracking (reproduced public 0.941/0.944, nothing >0.953), github.com/Kai-Gowers/biohub-cell-tracking-v2 (400-ep DDP retrain LB 0.927 vs shipped 0.942), royerlab baseline README (3 epochs, 'not trained to convergence'). kaggle.com not tried (policy).
- sibling notes read: h_github-intel (Kai-Gowers det recall 96.7 vs 98.3 %; naveenlx retrains never >0.947), h_redteam-past (same kill-test critique), h_linking-on-x138 (low-det pool UNREFINED int16; 1,337 readmitted nodes on dummy clips), h_external-data-training (dorado = Ultrack unet-simview tracks).
- v2 evidence that bounds my lens: de-quantisation ceiling +0.001-0.002 edge recall (r1_research_polyphase...json jitter dose-response); tail offsets unlearnable from raw patches |r|<=0.09 (r1_research_gate-aware-refine-head.json); 44b6 a_never = under-segmentation of 2 Ultrack objects ~7 um apart, Ultrack has +44 % interior points vs our final nodes (r2_critic.notes.md); node-drop break-even P(annotated)<0.3 % (wf_ideas/hyp_nodes-metric.notes.md) -> node-budget pruning dead.
- x138 head effect: exp51 nodes -2.9 % vs exp48 => up to ~0.003 of x138's +0.007 may be node multiplier (DIFF.md sec.4).
- Verdict forming: no retrain in 4 days has evidence for >= +0.005; propose H1 head-v2 (CPU, finishes), H2 dense proposal-only detector copy feeding x138 low-det pool, H3 Ultrack-convention localiser test (no training), H4 joint fine-tune long shot with kill gates.
- 10:53 UTC: wrote final JSON research/wf_ideas_v3/h_detector-retrain.json (4 hypotheses).
