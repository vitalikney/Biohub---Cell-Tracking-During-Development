# h_external-data-training notes
- 2026-09-25 ~11:05 UTC: started; BRIEF read; no prior json.
- 11:15 read CONTEXT.md (L3 dorado lines 1281-1293, resume 1500+), experiments/ext_x138/DIFF.md, tools/dorado_crops.py header,
  tools/register_44b6_dorado.py header, research/discussions_summary.md. Dorado = 522 T x 505x2217x2170 at Kaggle scale;
  tracks bundle 458,519 tracks, 38,068 slots/frame (tools/dorado_crops.py). 44b6 GT = Ultrack dorado points (84% within 2.5 um).
  Only prior external-data use = dorado DaughterNet (closed: val AUC parent 0.62). Nobody trained a DETECTOR/coord head on dorado.
- public.czbiohub.org: curl from this container -> proxy 403 (blocked here; was reachable from Colab/friend A per CONTEXT).
- 11:40 ultrack_supplementary (raw.githubusercontent OK): configuration/sparse_zebrafish = DS_LENGTH 521 (= dorado 522 frames),
  segment -cl edge -fl detection, UNet weights unet-simview.pt (SimView = multi-view Tomer-2012 design = Kaggle instrument per hosts);
  large_zebrafish = DaXi + unet-daxi.pt. config.toml sparse: min_area 300, max_area 25000, threshold 0.4, max_distance 10.
  => the public dorado tracks were produced with unet-simview.pt; never tested by the team (only mentioned CONTEXT B24).
- v2 dorado-oos-lab JSONs: N_est ~0.91 x Ultrack count in clip (IQR 0.82-0.95); Ultrack vs GT median 1.29 um, 97% <7 um;
  snapping to Ultrack loses <4um share (r2_critic.notes.md:20); streaming 2-10 MB/s, chunk (1,1,128,2217,2170) ~400MB;
  Stage-1 OOS boxes: 24 boxes per 40 GB. 44b6 a_never mostly under-segmentation but 91% of a_never FN are in 6bba.
- coordhead_retrain/out_full_P.log: 44b6->6bba head: new 1.5699 vs public 1.5668 um (19,248 pairs); none 1.7199. => more
  same-embryo (dorado) pairs unlikely to beat the public head on another embryo (convention differs by embryo).
- training loss (tools/repo/scripts/train_unet_transformer.py:535): single-voxel positives at GT, all other voxels neg weight 0.01.
- 12:20 x138 notebook (experiments/exp56_x138_verbatim): BIOHUB_SECONDARY_DETECTION_WEIGHT=0.80 -> detection logits =
  0.2*primary + 0.8*secondary(aligned), retention guard 0.90; SECONDARY_EDGE_WEIGHT 0.15; head reads PRIMARY features only.
  => a dense-trained SECONDARY moves 80% of detection while head/primary edge net stay valid. History: secondary swaps on LB
  -0.016 (probe 7), -0.025 (probe 10), -0.007 (probe 13) (experiments/RESULTS.md lines 39,42,46): lever is strong both ways.
- lab CSV l5_per_video_confirmation_vs_exp39.csv (exp39): node ratio (Np-Ne)/Ne GT-edge-weighted 44b6 -0.164, 6bba -0.021;
  weighted J 44b6 0.8906 adj 0.9052; 6bba J 0.9181 adj 0.9201. Dense detection that pushes Np to ~Ultrack (~1.1 Ne) costs
  ~2.6% (44b6-type) / ~1.2% (6bba-type) of adj via the multiplier -> threshold must be recalibrated to hold N_pred.
- ultrack repo examples/zebrahub: Ultrack runs on CPU with sqlite, classical detect_foreground + robust_invert boundaries;
  pip-installable -> can pseudo-track the 199 Kaggle clips (both embryos) in Kaggle CPU kernels with internet.
- dense fine-tune line (CONTEXT 473-495, 766-780, 930-1005): planned with SELF-teacher labels, never executed (cancelled 18 Sep).
  Le Quang Canh: encoder move with frozen linker -0.0377; joint fine-tune needs teacher EDGES -> dorado Ultrack tracks have edges.
- blocked: public.czbiohub.org, zebrahub.sf.czbiohub.org (proxy 403); GitHub API tree listing not enabled; raw.githubusercontent OK.
- 12:50 final JSON written (4 hypotheses: dense-dorado-secondary, dense-primary-headrefit, ultrack-dense-6bba, simview-readmit-pool).
