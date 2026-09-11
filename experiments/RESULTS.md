# Experiment log

Metric: adjusted edge Jaccard + 0.1 * division Jaccard (micro-averaged). "val4" = baseline notebook's 4-video validator
(44b6_12dfb391, 44b6_267148e4, 6bba_062c8d37, 6bba_07e24132). "hold12" = fixed 12-video holdout (`_lib/holdout_split.json`).
Caveat: the pretrained pilkwang weights saw ALL train videos, so val4/hold12 are optimistic for them.

| exp | what | val4 | hold12 | GPU time | notes |
|---|---|---|---|---|---|
| exp00 | user's baseline (public 0.933) re-run as private kernel via API | 0.9360 (adj_edge 0.9194, div 0.1667) | - | 37 min | reproduced exactly; test predict 9.5 min, validator predict 8 min (4 videos, 2xT4) |
| exp01 | training-speed profile, 150 it, batch 8, window 2, ds 1,4,4 | - | - | 9.5 min | 3.4 s/it (backward 73%, grad ckpt); full epoch on 183 videos ~2.1 h -> training from scratch infeasible, fine-tune instead |
| exp01b | same + `--amp --no-grad-ckpt` | - | - | 6 min | 2.05 s/it (1.65x faster), losses on par (edge 0.0083, acc 0.998); full epoch ~1.3 h |
| exp02 | public 0.941 notebook (analyticaobscura), full pipeline + post-proc, on hold12 | - | **0.9632** (edge 0.9256, div 1/7/13) | ~60 min | notebook's own validator code; adj includes node-count BONUS (t_pred 232k vs t_true 360k); per-video 44b6_87bba6c4 collapses to 0.53 (54 FP) where raw model gets 0.85 |
| exp03 A | pretrained raw model (predict+ILP, det 0.965, no notebook post-proc) on hold12 | - | **0.9527** (edge 0.9417, node recall 0.984, div 0/14) | 12 min | v1 crashed in training (OOM: notebook process held 6.4 GB from GPU-side scoring); scoring moved to subprocess |
| exp03 B | +1200 it fine-tune from pretrained (bce, lr 5e-5, amp, no ckpt), 27 min train | - | **0.9575** (edge 0.9468, recall 0.986, div 0/14) | 45 min | +0.0048 vs A; note B never saw the holdout while A did => real gain. Per-video: 44b6_1d530831 +0.058, 87bba6c4 +0.035, f20478e9 +0.019; worse on 9be80b04 -0.030, e28840c6 -0.035 (dense, more FP) |
| exp04 | as exp03 B but `--det-loss gauss_focal` (sigma 2.5 um) | - | 0.9094 (edge 0.8826, recall 0.940) | 45 min | WORSE at det 0.965: node ratio drops (-0.5..-0.9) => heatmap calibration changed; would need threshold re-sweep; parked |
| exp07 | det-threshold sweep of exp03B raw model on hold12 (0.93/0.965/0.985) | - | 0.9559 / 0.9575 / 0.9582 | 30 min | flat: model robust to threshold; predictions zipped -> local post-proc (tools/postproc.py, tools/score_geffs.py) |
| exp07+pp | local post-proc on thr0.965 graphs: gap closing 5um/1 frame, mutual-NN midpoint | - | **0.9619** (edge 0.9516) | CPU | +0.0044; gap 2 frames 0.9583, gap 8um 0.9586, min-len 3 = 0.9575 (neutral), min-len 6 0.9610 (hurts recall) |
| exp07+pp+div | + post-hoc divisions (parent<=5um to an orphan track start at t+1, mutual NN, sisters<=10-12um) | - | **0.9728** (adj 0.9606, div 6/35/8) | CPU | +0.011 from the division term: most added forks sit on unannotated cells (free), 6/14 GT divisions recovered. Sweep: parent 3um 0.9658, 4um 0.9708, 6um 0.9661; sisters 6um 0.9639, 8um 0.9693. Only 14 GT divisions => noisy, do not over-tune |
| exp07+pp+vel | gap closing with EMA-velocity projection (0.5 / 1.0) | - | 0.9619 / 0.9621 | CPU | neutral; gap 4um+vel 0.9601, 2-frame 0.9602 |
| exp07+pp+steal | divisions may 'steal' a weakly linked daughter (edge_prob < 0.6/0.7/0.8) | - | 0.9710 / 0.9717 / 0.9693 | CPU | no new TP, more edge damage -> keep steal off (base 0.9728) |
| pp direct link | residual end(t)->start(t+1) linking, mutual NN, radius 4/6/8 um (after gap5) | - | hold12 0.9634/0.9645/0.9654; divset36 0.9041/0.9051/0.9056 | CPU | consistent gain on both sets (fragmentation fix); radius sweep continues |
| pp v2 | gap5 + direct link 8um + divisions 5/12 | - | hold12 **0.9780** (adj 0.9646, div 6/31/8); divset36 **0.9117** (17/141/75) | CPU | direct 10 um: 0.9757/0.9109; 12 um worse. New default in exp10 |
| exp08 | fine-tune FULL epoch (~2265 it) from pretrained, workers=0 | - | 0.9539 (edge 0.9398, recall 0.981) | 95 min | WORSE than exp03B 0.9575: more training => fewer nodes (ratio -0.09..-0.72) and fewer TP edges; per-video swings ±0.03 (e28840c6 +0.041, 1d530831 -0.033). Sweet spot <= 1200 it. Weights kept for a possible 2-model ensemble |
| exp09 | exp03B raw predictions on 36 division-rich videos (92 GT divisions; 32 are 6bba) | - | raw 0.8997 (edge 0.8987, recall 0.977, div 0/92) on divset36 | 30 min | division-rich videos are much harder than hold12 (0.9575); predictions in $TEMP/exp09pred/all; sweep running |
| exp10 | submission notebook (exp03B -> ILP -> postproc gap5 + div 5/12) with hold12 self-check | - | raw 0.9575 / pp **0.9728** (exact match with local) | 20 min | valid submission.csv (4 dummy videos: 125k nodes, 119k edges); 12 videos predicted in 8.1 min => ~200 hidden videos ≈ 2.5 h. Ready for an LB probe |
| exp11 | LOEO: fine-tune on 6bba only (126 videos, 1200 it), raw eval on 12 44b6 videos (15 div) | - | A pretrained 0.8798 (edge 0.8585) / B 0.8825 (edge 0.8570, recall 0.987) | 60 min | cross-embryo fine-tune OK; 44b6 videos much harder than hold12 average |
| exp11+pp | post-proc on LOEO predictions (12 unseen-embryo 44b6 videos) | - | B: raw 0.8825 / gap5 0.8934 / +direct8 0.9014 / v2 0.9059; A: 0.8798 / 0.8850 / 0.8944 / 0.8963 | CPU | every post-proc stage helps on the unseen embryo |
| exp12 | ILP division weight 0.3 / 0.6 (vs 1.2) on 48 videos (hold12+divset36) | - | raw 0.9204 (div 36/205/70) / 0.9210 (24/104/82) | 45 min | local comparison with v2 post-proc running |
| exp12+pp | ILP div weight x post-proc on 48 videos | - | div1.2: raw 0.9096 / v2 0.9229 / gap+direct only 0.9158; div0.6: 0.9210 / 0.9249 / **0.9271**; div0.3: 0.9204 / 0.9248 / 0.9266 | CPU | v2.1 = ILP div 0.6 + gap5 + direct8, no post-hoc divisions |
| exp10 v2 | submission notebook, config v2.1 (ILP div 0.6, gap5, direct8, no post-hoc div), hold12 self-check | - | raw **0.9820** (div 8/19/6) / pp **0.9902** (adj 0.9660, edge 0.9554) | 20 min | LB-probe candidate; 4 dummy test videos: 124.9k nodes / 119.4k edges |
| exp14 | fine-tune 1200 it + intensity augmentation (gain 0.5-1.6, offset -0.15..0.45, gamma 0.6-1.5, haze p=0.3) | - | 0.9345 (edge 0.9358, recall 0.982) | 65 min | WORSE than exp03B; det loss 0.017 vs 0.0022; rejected |
| exp13+pp | ILP disappearance/appearance costs x v2.1 post-proc, 48 videos (div weight 1.2) | - | d1/a0 0.9149, d3/a0 0.9110, d2/a0.5 0.9216 | 100 min | reference d2/a0 0.9158; a0.5 gain comes from divisions (12 TP) that div 0.6 captures better; keep d2/a0 |
| LB probe 1 | kernel exp10 v2 (config v2.1) submitted 2026-09-06 04:30, id 56044199 | - | **LB 0.899** | - | vs user's 0.933 / public 0.941; hold12 0.9902 did not transfer (leaky validation); see CONTEXT §11 |
| LB probe 2 | exp06 = public 0.941 pipeline + primary := exp03B (id 56049333) | - | **LB 0.945** | ~6 h scoring | +0.004 vs public; adopted as new base |
| LB probe 3 | exp18 = public pipeline, ILP division weight 0.9 (id 56049863) | - | LB 0.941 | ~6 h | neutral; dropped |
| LB probe 4 | exp19 = public pipeline, det threshold 0.95 (id 56056939) | - | **LB 0.940** | ~5.5 h scoring | vs 0.941: neutral (noise), dropped; det stays 0.965 |
| LB probe 5 | exp20 = exp06 base, SECONDARY_DETECTION_WEIGHT 0.8->0.5 (id 56057989) | - | **LB 0.943** | ~6 h scoring | vs exp06 0.945: -0.002, negative, dropped; secondary weight stays 0.8 |
| LB probe 6 | exp21 = exp06 base, OUTPUT_MIN_TRACK_LEN 6->4 (id 56065251) | - | **LB 0.943** | ~7 h scoring | -0.002 vs 0.945: shorter tracks add nodes without edge gain; try 8 next (exp25) |
| LB probe 7 | exp22 = exp06 base, secondary weights := exp08 fine-tune (id 56065255) | - | **LB 0.929** | ~6 h scoring | -0.016 vs exp06 0.945: strongly negative; exp08 shares init with exp03B (no diversity) and the public post-proc is tuned for the seed314159 secondary; dropped |
| LB probe 8 | exp24 = exp06 base, GAP_CLOSE_UM 5.0->6.5 (id 56071497) | - | **LB 0.944** | ~6 h scoring | -0.001 vs 0.945: noise; gap-closing radius stays 5.0 |
| LB probe 9 | exp25 = exp06 base, OUTPUT_MIN_TRACK_LEN 6->8 (id 56072510) | - | **LB 0.944** | ~6.5 h scoring | -0.001 vs 0.945: noise; min track len stays 6; post-proc probes closed |
| LB probe 10 | exp27 = exp06 base, SECONDARY := friend_a_full199_ep21 (from scratch, all 199 videos, 21 epochs) (id 56084358) | - | **LB 0.920** | ~5.5 h scoring | -0.025 vs 0.945: the 21-epoch scratch model is weaker than pilkwang's secondary; on the 4 dummy test videos exp06 0.8961 vs exp27 0.8889 (edge FP/FN up, recall down); blend at weight 0.8 amplifies it. Next: honest raw comparison on 6bba->44b6 before any further probe |
| LB probe 14 / exp29 | sjlee101/biohub-lf-dctta-v020 verbatim (public 0.947: DeepCenter TTA + secondary edge-feature TTA 0.75 + DC div thr 0.20 on Harmonic Fusion), validator+sweep on (id 56146538) | - | **LB 0.947** | ~2 h kernel | submitted 2026-09-10 17:49; reproduces the public 0.947 | scored 2026-09-11 ~02:00 MSK: REPRODUCES the public 0.947 (sweep picked tight55 = MOTION_RELINK_TIGHT_UM 5.5); new base for final candidate 1 |
| LB probe 11 / exp30 | sjlee101 0.947 TTA stack + PRIMARY := exp03B, validator off (id 56145113) | - | **LB 0.944** | ~30 min kernel | submitted 2026-09-10 16:28; our candidate base | -0.003 vs exp29: the fine-tuned primary does NOT add on the TTA stack (confounded by tight55 -> exp33 deconfounds) |
| LB probe 12 / exp31 | exp30 + Z-flip views in the primary/secondary edge-feature TTA loops (training aug flipped Z; public TTA was XY-only) (id 56145851) | - | **LB 0.941** | ~35 min kernel | submitted 2026-09-10 17:08 | -0.003 vs exp30 = tie (noise floor), not a negative; leaky local +0.010; re-tested on the clean exp29 base as probe 16 (exp34) |
| LB probe 13 / exp32 | exp30 + SECONDARY := exp23 (fine-tuned seed314159) (id 56146281) | - | **LB 0.937** | ~30 min kernel | submitted 2026-09-10 17:34; second step of the fine-tune stack on the TTA base | -0.007 vs exp30: fine-tuned secondary hurts on the TTA stack too (3rd negative secondary swap); dropped |
| LB probe 15 / exp33 | exp29 realised config (sjlee stack + MOTION_RELINK_TIGHT_UM 5.5) + PRIMARY := exp03B, validator off | - | pending | ~30 min kernel | submitted 2026-09-11 09:35 MSK (id 56160334); deconfounds probe 11 (one change vs the submitted exp29) |
| LB probe 16 / exp34 | exp29 realised config (sjlee stack + MOTION_RELINK_TIGHT_UM 5.5, pilkwang primary) + Z-flip views in both edge-feature TTA loops (12 views) | - | pending | ~35 min kernel | pushed 2026-09-11 09:40 MSK; re-test of exp31 on the clean base (leaky 4-video local: exp29 0.8932, exp30 0.8936, exp31 0.9034, exp32 0.8969) |
| LB probe 17 (candidate) / exp35 | exp29 realised config (sjlee stack + tight55) + PRIMARY := soup03B_50 (weight-space average 0.5 pilkwang primary + 0.5 exp03B; dataset folder `soup03B_50/`) | - | pending | ~30 min kernel | pushed 2026-09-11 09:55 MSK; submit after exp33 scores (node-count mechanism: the soup halves exp03B's +3.2% node shift) |
| local division sweep | `tools/sim_safediv.py` on 12 hold-out videos (exp23 A_pretrained geffs, 14 GT divisions): safe-division gate OFF 0.9469 -> ON (public tau 0.6) **0.9567**; tau 0.3/0.45/0.8/1.0/1.4/2.0 = 0.9515/0.9550/0.9550/0.9591/0.9554/0.9545; parent radius 7.5/10.5 = 0.9573/0.9567; divergence 1.0/3.0 = 0.9577/0.9547 | - | **gate worth +0.010; all thresholds inside single-event noise** | ~25 min CPU | 14 GT divisions => 1 division = +-0.004 score; response is jagged, not unimodal; no LB probe. Ceiling = 4:1 FP:TP => needs a classifier (B20). Re-run on all 199 videos to resolve any knob |
| exp23 | fine-tune the pilkwang seed314159 SECONDARY, exp03B recipe (1200 it, batch 8, lr 5e-5, bce, seed 42) | - | hold12 raw A 0.9469 (edge 0.9346, recall 0.982) -> B **0.9551** (edge 0.9409, recall 0.982); leaky sanity only | 50 min | weights in dataset `vitaliineibauer/biohub-ft-weights/exp23`; NOT probed on LB until friend B checks it as secondary in the full public pipeline on LOEO-44b6 (probe 7 lesson) |
| exp15 | inference ensemble exp03B+exp08 (avg det logits + edge logits), hold12, ILP div 0.6 | - | raw 0.9708 (edge 0.9454, recall 0.984, div 5/24/9) | 20 min | worse than single exp03B raw 0.9820; rejected |
| exp17 | fine-tune 600 it (exp03B recipe) | - | 0.9556 (edge 0.9418, recall 0.986) | 40 min | within noise of exp03B (1200 it, 0.9575); per-video deltas -0.08..+0.06 |
| exp16 | fine-tune 1200 it, seed 7 | - | 0.9502 (edge 0.9346, recall 0.972) | 50 min | worse than seed 42 (exp03B 0.9575); seed variance ±0.005 |
| exp06 | full 0.941 pipeline with PRIMARY weights := exp03B (dataset vitaliineibauer/biohub-ft-weights) on hold12 | - | 0.9615 (edge 0.9279, div 1/10/13, t_pred 245k) | ~60 min | vs exp02 0.9632: neutral. edge +0.002 but t_pred +13k (smaller node bonus) and +3 div FP. Fine-tuned primary is diluted: SECONDARY_DETECTION_WEIGHT 0.8 blends in pilkwang seed model; post-proc thresholds tuned for those weights. Per-video +0.059 on 1d530831, +0.054 on 87bba6c4, -0.033 on 9be80b04 |
| exp05 | as exp03 B but `--window-size 3` (workers=0) | - | 0.9526 (edge 0.9409, recall 0.983) | 75 min | WORSE than exp03B 0.9575; train 60 min (3 s/it). Per-video mixed: +0.058 on 9be80b04, -0.03..-0.04 on 4 other 44b6. v1/v2 died of /dev/shm leak in DataLoader workers |
| local Friend A exp01 | from-scratch validator, fixed 6bba manifest -> LOEO-44b6, 5 epochs, BCE, window 2, seed 42 | - | raw **0.6706** (edge 0.6688, div 0/0/15, recall 0.8600); fixed pp v2 **0.6891** (adj edge 0.6869, raw edge 0.6856, div 1/31/14, recall 0.8649); internal sparse recall best 0.8944 at epoch 4 | 2 h 33 min train + ~8 min predict | no pretrained weights; 12/12 LOEO; det 0.965, TTA, NMS5, ILP app 0 / disapp 2 / div 1.2; validator-aligned diagnostic 0.6603; no LB submission |

| local Friend A exp02 | scratch 20ep, 126x6bba -> LOEO-44b6; BCE, w2, ds1,4,4, cosine 1e-4->1e-5, seed42 | - | best **0.6803** at epoch_020 (edge 0.6809, recall 0.8531, Npred/Nest 0.998); primary ref 0.8807, secondary ref 0.8691 | 9.7 h train + 0.7 h eval | 12/12 honest videos; milestones 5/10/15/20 + training-best; dataset `friend_a_exp02_loeo20/`; stop delta20-15=+0.0031; no LB submission |
| local Friend A exp02 / STEP 1b | epoch-20 scratch model scored on a fixed seed-42 sample of 12 of its own 6bba training videos; same raw predictor/ILP recipe | - | own-train12 **0.8332** (edge 0.8455, recall 0.9361, Npred/Nest 1.169; div 0/0/17) | ~3 min predict + score | smoke 2/2 passed; +0.1528 score and +0.0830 recall vs LOEO-44b6: substantial embryo shift plus residual sparse-label/calibration limit; continue fixed dense STEP 4; no LB submission |
## Per-video observations (exp00 validator)
- 44b6_267148e4: adj_edge 0.81 because t_pred 20957 > t_true 19130 (over-count penalty) and edge_jaccard 0.82 (33 FP / 23 FN / 254 TP).
- 44b6_12dfb391: edge_jaccard 0.913, t_pred 42555 < t_true 58672 (no penalty).
- Division jaccard on val4 = 1/6 (1 TP, 1 FP, ...) - division term is basically untouched upside (max +0.1).

## Per-video (exp03 A, raw pretrained model on hold12)
44b6 videos are the weak spot: edge_jaccard 0.79-0.92 (1d530831 0.786, 87bba6c4 0.853, 9be80b04 0.862, e28840c6 0.874),
6bba videos 0.93-0.99. Node ratio on dense 44b6 is strongly negative (-0.33..-0.69 => far fewer nodes predicted than
estimated), yet GT node recall is 0.94-1.0 => annotated nuclei are found; the losses are linking/fragmentation in dense
regions and under-detection of unannotated cells. Divisions: raw ILP gives 0 TP / 14 (division_weight 1.2).

## Key finding (2026-09-05 evening)
The adjusted-Jaccard penalty is signed: predicting FEWER nodes than `estimated_number_of_nodes` gives a bonus
(factor 1 + 0.1*(T_true-T_pred)/T_true). On hold12 the full public pipeline has a lower raw edge Jaccard than the
raw fine-tuned model (0.9256 vs 0.9468) but wins on the adjusted score (0.9632 vs 0.9575) because its post-processing
(short-track filter etc.) cuts t_pred to 232k vs 360k estimated (+3.5% bonus). => Combine: fine-tuned weights
(better edges) inside the pipeline (node reduction) - tested in exp06. Per-video the pipeline is bad on
44b6_87bba6c4 (0.53, 54 FP edges) where raw gets 0.85; worth inspecting which post-proc stage adds those FPs.
Caveat: hold12 = same embryos as train; LB test is split by embryo.

## Decision (2026-09-05 23:00)
Swapping weights inside the public pipeline gives noise-level changes; the raw-model gains (+0.005 edge J) are measurable.
=> Build our own clean pipeline: fine-tuned model + ILP + light node-reduction post-processing (short-track filter,
isolated-node prune, gap closing), scored with the OFFICIAL repo metric on hold12; keep prediction geffs (zipped)
so post-processing sweeps run locally on CPU. Then one LB probe to calibrate against the public pipeline.

## Clean pipeline v1 (2026-09-05 23:50)
exp03B weights -> predict (det 0.965, ILP app 0 / disapp 2 / div 1.2) -> tools/postproc.py gap_um=5 max_gap=1,
div_parent_um=5 div_sister_um=12 -> hold12 official score 0.9728 (raw 0.9575). Next: better weights (exp05 window 3,
exp08 full epoch), then a Kaggle inference notebook producing submission.csv with this pipeline (for one LB probe).
