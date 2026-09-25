# notes: schedule skeptic, dense-proposal-detector-copy (2026-09-25T11:00:34Z)
- started; read BRIEF.md; no prior json
- read: sibling v_detector-retrain_coordhead-v2-embryo-robust_schedule.json (refuted on gate P, same logic applies)
- CHECKED numbers: exp03B 1200 it = 27 min train on 2xT4 (experiments/RESULTS.md l.14) OK; 1,337 readmitted on 4 dummy clips
  (CONTEXT l.1515) OK; 0.43 um z offset = fractional shift_vox mean (wf_ideas_v2/r2_research_dorado-oos-lab.notes.md l.10) OK;
  "63 reliable" placed clips (CONTEXT l.1283) OK (r2_critic used 25 of them).
- trainer: compute_detection_loss (tools/repo/scripts/train_unet_transformer.py l.535-593) single-voxel pos, neg_weight default
  1e-2 (argparse l.1227); `mask` = node padding mask, NOT a voxel ignore mask -> 6bba PU masking (neg >7 um from GT) needs a
  NEW loss patch in experiments/_lib/train_patches.py (not "as described").
- dense-geff path: tools/build_dense_gt.py exists (teacher nodes w/o edges, GT meta copied) but the friend-A dense fine-tune line
  was cancelled 18 Sep and never executed end-to-end (CONTEXT l.1005; h_external-data-training.notes) -> untested glue.
- x138 pool: cell 5 load_low_detections/readmit read low_coords/low_score from $BIOHUB_CACHE_DIR/<ds>.npz; one score array,
  one READMIT_MIN_SCORE -> needs a source tag array + per-source threshold (small patch). build_probe_kernel --base x138
  currently allows only divinsert|leafprune (CONTEXT l.1509) -> new patch infra needed.
- runtime: REPAIR_DEADLINE_S 27000 (x138 cell 0 l.73): after 7.5 h remaining movies lose relink/readmit/gapfill. Hidden-test
  runtime unknown; scoring latency ~7.5 h (h_ensembles-and-private.notes l.4) -> little headroom for a 3rd detector pass.
- data location: register_44b6_dorado.py needs train GT geffs + data_external/dorado/tracks.npz; L3 line was Vitalii's
  session -> files likely on Vitalii's machine, NOT confirmed on friend A's (idea assumes friend A holds them).
- friend A: no commits since 24 Sep 04:12 MSK; queued for x138 lab cache after #34 (PROMPT_FRIEND_A.md top block) -> GPU conflict.
- verdict: clock OK (~2 days slack) but P(scored) = P(base)0.85 x P(glue)0.75-0.8 x P(gate)0.35 x P(dummy/runtime)0.9 ~ 0.2 (Kaggle path),
  ~0.1 (friend A path). REFUTED under schedule lens.
- 2026-09-25T11:03:46Z final JSON written
