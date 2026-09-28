# inventory notes (28 Sep)

## Code map (exp70g-k2-cap6.ipynb)
- cell0 = env defaults (x138) + probe override block (DIVINS_*, REPAIR_DEADLINE_S 34200, DIVINS_DEADLINE_S 28800, LOWREFINE_ENABLE 1, DEGRADE_KEEP_DIV 1)
- cell1 = CONFIG GUARD: raises if DET_THRESHOLD/ILP_APPEARANCE/ILP_DISAPPEARANCE/GAP_CLOSE_UM/OUTPUT_MIN_TRACK_LEN/BIDIRECTIONAL_EDGE_WEIGHT/FUSION_MODE/DUAL_SEED_RETENTION drift (builder patches cell-1 guard for --set keys)
- cell2 = module-level reads (notebook globals) for post-proc; DET/ILP passed as CLI args to predict subprocess (c04 predict_cmd)
- cell3 = HARD-SETS SECONDARY_EDGE_WEIGHT 0.15, SECONDARY_DETECTION_WEIGHT 0.80, LINK_MODE low_margin_consensus, MIX_TEMPERATURE 1, LOW_MARGIN_MAX 0.35, DUAL_SEED_EDGE_THRESHOLD 0.48, DEEPCENTER_CHECKPOINT (resolved path)
- cell4 = predict-script patches; HARD-SETS DUAL_SEED_MIN_CANDIDATE_RETENTION 0.90, EDGE_FEATURE_TTA 1, SECONDARY_EDGE_FEATURE_TTA 1 / _WEIGHT 0.75; SECOND guard: BIDIRECTIONAL_EDGE_WEIGHT must == 0.15 (ValueError) -> builder only patches cell1 guard
- cell4 lowdet patch: LOWREFINE uses READMIT_MIN_SCORE as its refine threshold (_LOWREFINE_MIN_SCORE) -> READMIT_MIN_SCORE couples readmit AND lowrefine
- CACHE_EDGE_THRESHOLD=1.0 -> `probs > 1.0` never true -> edge cache dead
- GAP_CLOSE_MAX_GAP=2 but c07:854 `effective_gap_max = min(GAP_CLOSE_MAX_GAP, 1)` -> 2 == 1
- VALIDATOR_ENABLE=0 -> VALIDATOR_*/PPSWEEP_* dead
- filter_output_graph order (c07 ~1938-2130): edge max/next-frame -> motion relink (flow) -> readmit + relink -> single parent -> gap close (DC gap veto) -> gap2 -> gapfill -> safe div (DC veto) -> div geometry filter(off) -> prune isolated -> short-track filter + rescue -> linefit -> divinsert

## Couplings / inert ranges found (08:xx UTC)
- readmit pool = load_low_detections (c07 l.1203-1270): returns None if GAPFILL_MAX_GAP < 1 or CACHE_DIR unset; filters score >= GAPFILL_MIN_SCORE and drops peaks within GAPFILL_EXCLUDE_UM of a node -> GAPFILL_MAX_GAP/MIN_SCORE/EXCLUDE_UM also move READMIT.
- LOWDET_THRESHOLD 0.3 < GAPFILL_MIN_SCORE 0.5 -> LOWDET in [0, 0.5] is output-inert (only dump size); lowrefine refines only peaks >= READMIT_MIN_SCORE.
- GAP2: `dist > GAP2_MAX_TOTAL_UM or dist / 3.0 > GAP2_MAX_STEP_UM` with TOTAL 10.2 -> step <= 3.4 always, so GAP2_MAX_STEP_UM >= 3.4 is inert (x138 ppsweep 'gap2step40' = 4.0 inert).
- GAP_CLOSE_MAX_GAP 2 -> effective 1 (c07 l.854).
- flow relink: in flow frames the tight gate is MOTION_RELINK_FLOW_TIGHT_UM 7.0 and the relaxed gate falls back to MOTION_RELINK_RELAXED_UM 10.0 (unset); MOTION_RELINK_TIGHT_UM 5.5 = seed gate (FLOW_SEED_GATE_UM 0) + tight gate only where no flow field.
- relink cost `motion + RAW_COST*raw - LEARNED_BONUS*prob`; prob = ILP edge prob (0 for non-ILP pairs) -> LEARNED_BONUS is the only channel from ILP edges to output edges.
- ILP_DIVISION_WEIGHT is NOT in the cell-1 guard; DET/APPEAR/DISAPPEAR/GAP_CLOSE_UM/MIN_TRACK_LEN are (builder patches cell-1 guard).
- BIDIRECTIONAL_EDGE_WEIGHT has a second guard in cell 4 (ValueError unless 0.15) the builder does not patch -> --set crashes. FUSION_MODE is read only by guards/prints.
- ADAPTIVE_SHORT_TRACK_RESCUE dormant: trigger removed_frac >= 0.10 never met (F-MOD-23) -> rescue params inert unless TRIGGER lowered.
- MOTION_RELINK_MAX_FRAME_NODES 2600: any frame above -> relink skipped for the whole clip (0 in lab/public run_stats).
- VALIDATOR_ENABLE 0 -> VALIDATOR_*, PPSWEEP_* dead; RUN_OUTPUT_DIAGNOSTICS never read; CACHE_EDGE_THRESHOLD 1.0 -> `probs > 1.0` never -> edge cache empty.
- Not env knobs in exp70g (need a --patch): LEAF_PRUNE, FORKMID, COORDINJECT, EDGEFILTER, STITCH, SWAPFIX.

## Disclosures
- 743929 JT (x138 fork): ILP_DIVISION_WEIGHT 1.2->0.4 (+0.001), READMIT_MIN_SCORE 0.965->0.94 (+0.001), both node-neutral (<1%).
- 743222 imissher (0.947 stack): DET 0.960 0.946 / 0.970 0.945 vs 0.946/0.948; relink off 0.946; SECONDARY_DETECTION_WEIGHT 0.65 0.945; ILP candidate threshold (DUAL_SEED_EDGE_THRESHOLD) 0.48->0.30 0.000.
- 741242 Hammad: validator picks tight55 every rerun.
- amanatar V6 (x138 fork, public 0.901 per curation 17): DET 0.960, GAP 5.8, SAFE_DIV_MAX 10.5, SISTER 15, DIVERGE 1.50, FRAC caps 0.012/0.006, rescue 3/0.85, retention 0.75, FLOW_K 16, FLOW_RADIUS 48, FLOW_Z_WEIGHT 0.40 + new code.
- anhadmahajan track-your-cells (older stack, score unknown): GAP 5.8, DIVERGE 4.0, LEARNED_BONUS 1.25, SECONDARY_LINK_MODE adaptive.
- seyitkaangunes 035: MOTION_RELINK_VELOCITY_WEIGHT 0.25 (+ leaf prune 0.30).
- indarkarhana retention-guard v1 (July, 0.913): DET 0.96875, DISAPPEAR 1.5, GAP 5.8, SAFE_DIV_MAX 4.66, SISTER 8.5, EXISTING_CHILD 7.65, SEC_DET_W 0.475, GAP2 off, rescue off.
- sjlee single-knob forks (0.947 stack): SECONDARY_EDGE_FEATURE_TTA_WEIGHT 1.0 0.947 tie; DC safe-div 0.25 0.947 tie, 0.15 0.946; sister 16 0.947 tie. lineage-forge + mtoshidesu: DC safe-div 0.20.
- x138 PP_CANDIDATES (in-notebook, validator off): gap45, tight55, relaxed9, bonus125, gap2step40, reuse28, dcgap035.
- 08:08Z inventory.json written (gen script in scratchpad gen.py)
