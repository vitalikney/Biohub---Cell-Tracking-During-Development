# arms_1 notes (28 Sep) - group: detection + readmit/lowrefine

Task: two-direction arms (743929 style) for detection/readmit knobs not closed and not LB-tested by us.
arms_1.json did not exist at start -> fresh work.

## Code facts (exp70g-k2-cap6.ipynb split into cells)
- NMS = pool_kernel_um from weights config.json = 5.0 (not an env knob; only `--pool-kernel-um` CLI of predict script,
  not in predict_cmd) -> needs a --patch, not --set. pool_kernel_from_um: k = round(um/voxel), forced odd.
- lowdet peaks come from the SAME fused map and the SAME pool_k as candidates (`_detect_cells_pooled(det_logits[f_idx][0], t, 0.3, pool_k)`),
  so lowdet peaks with score > 0.965 are exactly the ILP candidate set; those the ILP kept are removed from the pool by
  GAPFILL_EXCLUDE_UM 2.0 -> readmit at 0.965 = "ILP-dropped candidates next to an open end"; 0.94 adds sub-threshold peaks.
- readmit keeps every free peak with d(anchor) <= 4 um and score >= READMIT_MIN_SCORE; second relink places them or they
  are pruned as isolated (OUTPUT_PRUNE_ISOLATED) -> surviving readmits = new edges re-wiring open ends.
- DET_THRESHOLD also drives the dual-seed retention guard (primary vs blended map per frame) -> nonlinear.

## CPU checks on exp60 lab dumps (_dl/exp60_*/edge_cache + trainlab, 56 clips, in-sample, ~6 min total)
Scripts in scratchpad (lowstats.py, rdscore.py, nms.py).
- candidates 1,341,252; lowdet bands: [0.94,0.955) 20,758; [0.955,0.965) 18,596; [0.965,0.975) 26,450; [0.975,0.99) 80,172; >=0.99 1,234,630.
- presafe nodes 1,150,839; readmitted 14,525 (1.26%); final 1,124,511 nodes / 1,082,114 edges; final readmitted 13,284 (1.18%),
  16,677 final edges (1.54%) touch a readmitted node.
- score of the 14,525 readmits (matched exactly to lowdet peaks): [0.965,0.97) 450, [0.97,0.975) 549, [0.975,0.98) 654,
  [0.98,0.985) 827, [0.985,0.99) 1,148, [0.99,0.995) 2,075, >=0.995 8,822.
  -> READMIT 0.98 drops 1,653 readmits (-0.14% nodes); 0.99 drops 3,628 (-0.32% nodes, ~-0.4% edges); 0.995 drops 5,703 (-0.50%).
- after readmit, free peaks within 4 um of an open end: [0.94,0.965) 6,303 (+0.55%, = F-TRN-55 6,696 +0.60%); >=0.965 only 188 left.
- GAPFILL_EXCLUDE_UM: readmit-eligible peaks near open ends with nearest-node distance in (1.5,2] = 2, (2,3] = 5 (all bands)
  -> EXCLUDE in [1.5,3] is INERT for readmit (NMS kernel already separates peaks); gapfill pool (>=0.5) changes 743 / 3,006
  of 409,910 free peaks, and gapfill nodes are only 1,053 (0.09% of nodes) -> useless knob. GAPFILL_PEAK_RADIUS likewise tiny.
- NMS pool_kernel_um 5.0 on a (1.625 um)^3 downsampled grid -> kernel (3,3,3) for um in [2.44, 5.69): plateau. Only moves:
  kernel 1 (every voxel above threshold is a peak -> node explosion) or kernel 5 (>= 44,075 of 1,341,252 candidates = 3.3%
  suppressed, peak-peak lower bound) -> both > 1.5% node change; not an env knob either. REJECT.
- DET_THRESHOLD 0.96 adds ~half of [0.955,0.965) = ~9.3k candidates (+0.7%); 0.97 removes ~half of [0.965,0.975) = ~13k
  (-1.0%), partly returned by readmit (0.965 < 0.97). imissher 743222: both directions lost on the 0.947 stack.
- DeepCenter safe-div scores (lab, TTA on): 6,617 checks, 1,763 accept; 804 (12%) within +-0.025 of 0.25 -> TTA off would
  flip a few hundred checks at random on a closed/tuned veto; one-arm only (binary); saves some runtime.
- LOWDET_THRESHOLD in [0,0.5] inert; LOWREFINE_ENABLE LB-tested (P38); UNET_BATCH_SIZE runtime only.

## Ranking
1 READMIT_MIN_SCORE up 0.99 / down 0.94 (down = exp85c, built, dummy PASS +0.84%). JT disclosed down +0.001 on x138.
2 DET_THRESHOLD 0.97 / 0.96 (low; imissher both-lose).
3 DEEPCENTER_TTA 0 (low, one arm).
- 11:xxZ arms_1.json written (3 candidates)
