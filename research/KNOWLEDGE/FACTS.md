# FACTS - verified facts with sources (curator: facts; curation v4)

State as of **2026-09-25 18:25 UTC**. First build (no earlier FACTS.md existed). IDs are stable: later curations
edit a line in place or append; never renumber. "CONTEXT l.N" = line in `CONTEXT.md` at this date (lines shift as the
file grows - search the quoted date/heading if a line moved). Newer sources win; disagreements go to CONTRADICTIONS.

## 1. Metric and scoring quirks

| ID | Fact | Source (date) |
|---|---|---|
| F-MET-01 | score = adjusted edge Jaccard + 0.1 x division Jaccard; official code github.com/royerlab/kaggle-cell-tracking-competition | CONTEXT §1 l.10, §4 (06 Sep); `research/wf_ideas_v3/FINAL_REPORT.md` §b (25 Sep) |
| F-MET-02 | Node matching: optimal one-to-one bipartite assignment on scaled centroid distance, max 7.0 um | CONTEXT §4 l.43; `research/wf_ideas_v3/browser_intel.md` §5 (Overview, read 25 Sep 11:20 UTC) |
| F-MET-03 | Edge TP needs both endpoints matched to GT nodes linked in GT; edge FP only if an endpoint matches a GT node linked elsewhere -> edges/forks among UNANNOTATED cells are free | CONTEXT §4 l.43-44 |
| F-MET-04 | Node multiplier adj = J x (1 - 0.1 (N_pred - N_est)/N_est): linear, no kink, no upper clamp -> fewer nodes than N_est is a bonus; scores can exceed 1.0 | CONTEXT §4 l.45; `research/wf_ideas_v3/FINAL_REPORT.md` §j.1; browser_intel §5; `experiments/ext_biohub-exp003-two-embryos/NOTES.md` #4 |
| F-MET-05 | Adjusted edge J is averaged over videos weighted by the video's TP+FP+FN (not by GT edge count, see C-01) | `research/wf_ideas_v3/FINAL_REPORT.md` §j.1 (25 Sep); browser_intel §5 ("weight-averaged by (TP+FP+FN)") |
| F-MET-06 | Division J = TP/(TP+FP+FN), micro-averaged. Official rule (metrics.md): local parent anchor, two GT daughter lineages matched to two DISTINCT predicted child branches, directed local topology; "Merely sharing a weakly connected component is not sufficient" | CONTEXT §4 l.47-52 (verified 11 Sep) |
| F-MET-07 | The public notebooks' built-in validator (and our old `tools/repo`) scores divisions with the OLD weakly-connected rule; it reversed a local ranking once | CONTEXT 23 Sep 20:30 entry l.1250; `experiments/RESULTS.md` row "local division sweep (OFFICIAL metric)" l.71 |
| F-MET-08 | Public division J ~0.36 (+-0.04): probe 26 (all forks off) 0.911 vs 0.947; this is an UPPER bound because forks-off also removed the second-daughter edges | `experiments/RESULTS.md` probe 26 l.59; CONTEXT 24 Sep 02:00 l.1319; `research/wf_ideas_v3/FINAL_REPORT.md` §j.7 |
| F-MET-09 | Break-even precision for an added fork = J/(1+J) ~0.265 at J_pub 0.36; team floor P_min 0.31 | CONTEXT 24 Sep 00:40 and 02:00 (l.1298-1321) |
| F-MET-10 | Coordinates: spec says integer voxel centroids; float output (safe encoding) was accepted and scored identically at 3 decimals (probes 32/33 ties) | browser_intel §5; `experiments/RESULTS.md` probes 32/33 l.65-66 |
| F-MET-11 | Public LB shows 3 decimals; within one displayed score teams are ordered by the unrounded score; submission time decides only among byte-identical copies (Rules 3.7.b) | `research/wf_ideas_v4/FINAL_REPORT_v4.md` §2 (18:08 UTC 25 Sep); CONTEXT 25 Sep 13:58 l.1737 |

## 2. Data and splits

| ID | Fact | Source (date) |
|---|---|---|
| F-DAT-01 | Train: 199 videos (.zarr v3, T=100, Z=64, 256x256 uint16; voxel 1.625 x 0.40625 x 0.40625 um), sparse GT .geff; two embryos 44b6 (71 videos, dense, ~1% annotated, 26 divisions) and 6bba (128 videos, ~9% annotated, 125 divisions); 151 division events in 87 videos | CONTEXT §2 l.18-20; `experiments/l2_daughternet/splits.json` summary |
| F-DAT-02 | Unique GT divisions = 149 (2 counted twice in overlapping 44b6 crops) | CONTEXT 23 Sep 21:30 UTC l.1263 |
| F-DAT-03 | 44b6 clips are overlapping space-time crops of ONE recording (global GT node ids): 62 video pairs share 2,429 GT nodes and 2 divisions. Leak groups: 11 multi-clip groups covering 64 of 71 clips (sizes 24/11/6/4/3/3/3/3/3/2/2) + 7 singletons; folds keep groups whole (0 of 62 links cross folds) | CONTEXT 23 Sep 21:30 l.1260-1262; `experiments/l2_daughternet/splits.json` meta.leak_groups (tools/make_splits.py, seed 20260923) |
| F-DAT-04 | 6bba crops share only 1-frame boundary overlaps (independently annotated) | CONTEXT 23 Sep 21:30 l.1262 |
| F-DAT-05 | 44b6 train clips are crops of the PUBLIC Ultrack "dorado" movie (2024_03_22_dorado): 654/777 GT nodes of 44b6_12dfb391 coincide with dorado track points; 63/71 clips placed; 84% of GT within 2.5 um -> dorado-pretrained models are not leak-free on 44b6 (see C-05) | CONTEXT 23 Sep 23:30 l.1276-1283; `research/wf_ideas_v3/FINAL_REPORT.md` §j.20 (tools/register_44b6_dorado.py) |
| F-DAT-06 | Train/test are embryo-disjoint; public LB ~29% of test (one embryo), private ~71%; hidden test names follow `<embryo>_<fov>`; `test/` holds 4 dummy copies of train videos | browser_intel §5 (Data tab, Leaderboard, 25 Sep); CONTEXT §2 l.21 |
| F-DAT-07 | Data tab: hidden test "approximately the same size as the training dataset"; exact N not stated (see F-RUN-06, C-02) | browser_intel §5 |
| F-DAT-08 | Low-contrast 6bba videos (57b7cc1e ratio 1.7, 786893ac 4.5 vs median 24) hold 43% of detection losses on divset36 | CONTEXT §10 l.117-119 |
| F-DAT-09 | Lab splits: SELECTION = 64 6bba odd-index stems; CONFIRMATION = 6bba even + all 44b6 (135) | `experiments/l2_daughternet/splits.json` meta |
| F-DAT-10 | exp60 lab split: 56 clips (44b6 17 = one per leak group, 11 GT div; 6bba 39, 88 div), SELECTION/CONFIRMATION 28/28, shards A/B; excludes 20 probable x138 head-training stems + 4 dummy twins; written before any run | `experiments/exp60_trainlab/split.json`; CONTEXT 25 Sep 14:29 l.1759-1767 |
| F-DAT-11 | GT quirks: frozen/duplicated frames, boundary cells split into two tracks, a few wrong edges, very dim annotated nuclei | CONTEXT §2 l.22-23 |
| F-DAT-12 | DeepCenter (safe-division veto) was trained only on the 71 44b6 clips (validated on 6bba) -> 6bba is an honest bed for its threshold | `research/wf_ideas_v3/FINAL_REPORT.md` §j.12 (browser_intel §6.1) |

## 3. LB state and history

| ID | Fact | Source (date) |
|---|---|---|
| F-LB-01 | Our best public = **0.954** (#35 exp57b = x138 + DaughterNet insertion); x138 verbatim on our account = 0.953 (#34) | `experiments/lb_poll/poll.log` 18:18:57Z; CONTEXT 25 Sep 14:37 / 16:20 l.1797-1810 |
| F-LB-02 | Rank history: 46/3174 after probe 2 (06 Sep); #834 at 0.947 (23 Sep); ~#456-460 at 0.950 (25 Sep 11:00-11:27); **#151 of 3,905 at 0.954 (25 Sep 18:08 UTC), 37 submissions** | CONTEXT §1 l.11, 23 Sep 18:40 l.1233, 25 Sep 11:40 l.1551; `research/wf_ideas_v4/FINAL_REPORT_v4.md` §2 |
| F-LB-03 | LB blocks 18:08 UTC 25 Sep: 0.957 = ranks 66-77, 0.956 = 78-98, 0.955 = 99-133, 0.954 = 134-195, 0.953 = 196-456 (261 teams); silver ~rank 195, bronze ~390 (inside 0.953), gold ~rank 17 = 0.966; top 0.975 | FINAL_REPORT_v4 §2; CONTEXT 25 Sep 18:20 l.1846-1849; browser_intel (top 0.975) |
| F-LB-04 | No public notebook above 0.953 (checked 25 Sep 11:40 and ~17:20 UTC); x138 copies: kunaldesale2408 (whitespace-only diff), raunakdey07 | CONTEXT 25 Sep 11:40 l.1549; FINAL_REPORT_v4 §2; `experiments/ext_biohub-cell-tracking/NOTES.md` |
| F-LB-05 | x138 (anvithpothula/biohub-x138, 0.953) = thtennant frontier947-readmit (0.946) + ONE change: V1284 coordinate-refinement head (MLP 224->32->3, shift <= 2 um, float coords, trilinear gather) | CONTEXT 24 Sep 12:30 l.1380-1385; `experiments/ext_x138/DIFF.md` §1 |
| F-LB-06 | x138 author privately 0.956 (#83, 25 Sep 18:08); Corwin #17 0.965; team y3uanm 0.949 -> 0.956 via secondary-detector distillation fine-tune | FINAL_REPORT_v4 §2; `experiments/ext_corwin-biocel-aux/NOTES.md`; `experiments/ext_y3uanm-secondary-ft/NOTES.md` |
| F-LB-07 | Full probe chronology with decisions: `research/KNOWLEDGE/DECISIONS.md` §1 | `experiments/RESULTS.md`; CONTEXT §11, §14 |

## 4. Runtime and hidden-test size N

| ID | Fact | Source (date) |
|---|---|---|
| F-RUN-01 | Kaggle limit: CPU/GPU notebook "<= 12 hours run-time", internet off (NOT 9 h; see C-03) | browser_intel §5; CONTEXT 25 Sep 13:58 l.1740 |
| F-RUN-02 | One hidden rerun covers public AND private in one run; latencies already include private | `experiments/runtime_step0/step0.md`; `research/wf_ideas_v3/h_ensembles-and-private.notes.md` l.9 |
| F-RUN-03 | Measured latencies (submit -> COMPLETE, 10-min poll): L34 (x138) in (6.29, 6.46] h; L35 (exp57b) in (6.72, 7.73] h (five empty CLI polls 15:26-16:06Z); #31 exp51 17:09 -> 00:39 = ~7.5 h; #32/#33 00:02 -> <= 07:50 (<= 7.8 h) | CONTEXT 25 Sep 14:37, 16:20 l.1797-1803; CONTEXT 24 Sep 17:09 / 25 Sep 00:39, 07:50 l.1446-1498 |
| F-RUN-04 | Dummy timing (4 clips): x138 GPU phase ~318 s/clip/shard on 2 shards, repair 56.6 s/clip; exp57b repair 122.9 s/clip (insertion +~66 s/clip); model T(N) ~ 300 + (N/2)x318 + N x r | `experiments/runtime_step0/step0.md`; `experiments/runtime_step0/*_timing.txt` |
| F-RUN-05 | x138 REPAIR_DEADLINE_S = 27,000 s (7.5 h): after it relink, gap close, safe divisions and linefit are switched off for remaining (alphabetical) clips | `experiments/ext_x138/DIFF.md` §2 cell 0; browser_intel runtime projection l.270-273 |
| F-RUN-06 | Step-0 bound: hidden N <= ~106 (from L34) / <= ~97 (from L35) at dummy speed; K2 forecast <= ~7.8 h | `experiments/runtime_step0/step0.md` (25 Sep 16:40) |
| F-RUN-07 | safetail (C01): REPAIR_DEADLINE_S 34,200 (9.5 h), insertion gate DIVINS_DEADLINE_S 28,800 (8.0 h), fail-soft 'DIVINS FAILED', DEGRADE_KEEP_DIV=1 keeps safe divisions + linefit after the deadline | CONTEXT §9 T1 entry l.1898-1905; `experiments/exp58_x138_safe_lowref/probe.json` |
| F-RUN-08 | Binding runtime constraint for K2 is its own insertion gate (8.0 h, worst-case margin ~0.2 h), not the 12 h limit | `research/wf_ideas_v4/lens_literature.notes.md` l.14; `research/wf_ideas_v4/v_intel_pair-gbm-relink-prior_feasibility.notes.md` l.6 |
| F-RUN-09 | Whole-kernel dummy time is not informative (exp51 29 min vs exp52 43 min for identical compute); only per-dataset lines are | `research/wf_ideas_v3/FINAL_REPORT.md` §j.19 |

## 5. Kaggle rules: ties, limits, errors, quota

| ID | Fact | Source (date) |
|---|---|---|
| F-RUL-01 | 5 submissions/day per TEAM, reset 00:00 UTC; up to 2 final submissions, selected manually (auto-pick would take two near-copies) | CONTEXT §11a l.321-341; browser_intel §5 (Rules 2); `research/wf_ideas_v3/FINAL_REPORT.md` §f |
| F-RUL-02 | Final deadline 29 Sep 2026 23:59 UTC; team merger deadline 22 Sep passed; team = vitaliineibauer (leader), sasyami, gsfatakhov; team plan: finals ticked by 29 Sep 20:00 UTC | browser_intel §5; CONTEXT 23 Sep team clarification l.1236-1239; CONTEXT 25 Sep 13:38 l.1584 |
| F-RUL-03 | Ties: Rules 3.7.b "the Submission that was entered first ... will be the winner" (byte copies); display order within a rounded score follows the unrounded score | CONTEXT 25 Sep 13:58 l.1737-1739 (https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/rules); FINAL_REPORT_v4 §2 |
| F-RUL-04 | Error classes: Notebook Timeout, Notebook Threw Exception, Submission CSV Not Found, Submission Scoring / Format Error, Notebook Exceeded Allowed Compute, Kaggle Error; errored submissions count toward the daily limit | CONTEXT 25 Sep 13:58 l.1741-1743 (https://www.kaggle.com/code-competition-debugging) |
| F-RUL-05 | GPU quota 30 h/week, max 2 concurrent GPU sessions; reset expected Sat 26 Sep 00:00 UTC (2020 staff post, unconfirmed); 18:56/30 used at 13:58 UTC, ~21:13/30 at ~18:10 UTC 25 Sep; hidden reruns reportedly do not count (unverified) | CONTEXT §1 l.12, 25 Sep 13:58 l.1744-1746; FINAL_REPORT_v4 §2 |
| F-RUL-06 | Proxy submissions via other accounts and private code sharing outside the team = disqualification | CONTEXT §11a l.335-341 |
| F-RUL-07 | External data allowed if public and equally accessible (incl. pretrained models); Zebrahub confirmed allowed | browser_intel §5; `research/discussions_summary.md` 741386 |
| F-RUL-08 | Team policy: no matching of hidden test clips to public recordings, no transductive overlap consensus on test crops | CONTEXT 23 Sep 23:30 l.1280-1283; CONTEXT 25 Sep 13:38 R9 l.1673 |
| F-RUL-09 | Every submission needs the user's explicit OK (night pre-approval allowed); K2 pre-approved for 00:01 UTC 26 Sep | CONTEXT §1 l.15; CONTEXT 25 Sep 13:38 l.1579, 17:55 l.1834; memory `project-lb-probe-approval` |

## 6. Models and weights

| ID | Fact | Source (date) |
|---|---|---|
| F-MOD-01 | Base models: pilkwang support pack (TemporalUNet3D, XY ds 4x, window 2 + node transformer + ILP), primary + seed314159 secondary (detection weight 0.8, edge weight 0.15) | CONTEXT §5 l.55; `experiments/runtime_step0/exp56-x138-verbatim_timing.txt` (Secondary model line) |
| F-MOD-02 | x138 datasets: pilkwang deepcenter prior v1, temporal-unet3d seed314159 v1, tracking support pack 50ep v1, anvithpothula/biohub-v1284-head-s075 (CC0) | `experiments/ext_biohub-cell-tracking/NOTES.md` #2 |
| F-MOD-03 | Our weights: private dataset vitaliineibauer/biohub-ft-weights (exp03B, exp08, exp23, soup03B_50, vitalii_daughternet fold_0..4, friend A checkpoints) | TEAM.md onboarding; `experiments/runtime_step0/exp48-leafprune-divins_timing.txt` (DIVINS ENABLED line) |
| F-MOD-04 | DaughterNet v1: 17,143 GT samples, 5 folds with 44b6 leak groups; OOF parent AUC 0.848, daughter AUC 0.767; v2 better pool AUC but worse insertion | CONTEXT 23 Sep 21:40 l.1270-1275, 24 Sep 02:10 l.1322 |
| F-MOD-05 | V1284 head retrain on 199 = kill test FAIL (6bba->44b6 +12% worse; learns 6bba z-offset) -> keep public head | CONTEXT 24 Sep ~23:00 l.1488-1493 |
| F-MOD-06 | Dorado-only DaughterNet: val AUC parent 0.62 / daughter 0.53 -> closed (Ultrack auto-divisions too noisy) | CONTEXT 23 Sep 23:45 l.1284-1286 |
| F-MOD-07 | Pipelines are bit-deterministic run to run: exp46 parity sha256 == exp39; exp54 CSV == exp48; exp56 reproduced every x138 counter | CONTEXT 24 Sep 00:30 l.1307-1310, 24 Sep 22:00 l.1483; `research/wf_ideas_v3/FINAL_REPORT.md` §j.2 |
| F-MOD-08 | In x138 every final edge comes from a flow-prior Hungarian; ILP gives 0 forks -> safe divisions are the only fork source; READMIT returns discarded peaks >= 0.965 as unrefined int16 copies (fixed by lowrefine C05) | `research/wf_ideas_v3/FINAL_REPORT.md` §j.9, §j.14 |
| F-MOD-09 | Leaf prune on x138 undoes READMIT (>= 479 of 513 pruned leaves are readmitted nodes) | CONTEXT 25 Sep 08:40 l.1514-1516 |
| F-MOD-10 | K2 dummy gates 18/18 PASS (K2/K1/FD 16/16 + FF 2/2); K1 sha256 == exp57b dummy; FF CSV == exp56 dummy | CONTEXT 25 Sep 17:20, 17:45 l.1817-1829 |

## 7. What transfers from lab to LB and what does not

| ID | Fact | Source (date) |
|---|---|---|
| F-TRN-01 | Leaky validation: hold12 0.9902 -> LB 0.899 (probe 1); pilkwang weights saw all 199 videos | CONTEXT §11 l.233-240; `experiments/RESULTS.md` probe 1 |
| F-TRN-02 | Rules that override relink with the in-sample ILP/edge net look +0.01..+0.016 in lab and give 0 on LB (probes 21, 29, 30) | CONTEXT 24 Sep 16:40/16:55 l.1435-1445; memory `project-edge-filter-finding` |
| F-TRN-03 | Division insertion is the one lab line that transferred: lab CONFIRMATION +0.0019 -> LB +0.001 (probe 28), again +0.001 on x138 (probe 35) | CONTEXT 25 Sep 10:20 l.1538; `experiments/RESULTS.md` probes 28, 35 |
| F-TRN-04 | Geometry-only change (float output) lab +0.0019..+0.0025 -> LB tie twice (probes 32/33) | `research/wf_ideas_v3/FINAL_REPORT.md` §j.16; RESULTS probes 32/33 |
| F-TRN-05 | TTA-group changes: local gains (Z-flip +0.017, axis-flip +0.021) -> LB -0.009 / -0.001; 81-87% of local gain survives on a scratch primary, so the LB failure is embryo difference, not memorisation | `experiments/RESULTS.md` probes 16, 19 and Friend B rows l.87-107 |
| F-TRN-06 | Weight swaps (fine-tuned primary, secondaries, soup) never beat pilkwang on the TTA stack (probes 7, 10, 11, 13, 15, 17) | CONTEXT §11 VERDICT 12 Sep l.299-303 |
| F-TRN-07 | Friend B port reproduces LB ORDER (Spearman +0.80) but not magnitude; +0.001-class local gains do not earn probes | `experiments/RESULTS.md` Friend B calibration l.99, probe-18 prediction l.103 |
| F-TRN-08 | x138 head: +0.007 on its own base but only +0.002 on ours (probe 31); ~+0.0022-0.0027 of x138's +0.007 is the 2.4-2.9% node drop via the multiplier | CONTEXT 25 Sep 07:50 l.1500-1504; `research/wf_ideas_v3/FINAL_REPORT.md` §j.6 |
| F-TRN-09 | Post-processing gains of the public stack DO transfer to unseen embryos (+0.046 public heuristics vs clean pipeline) | CONTEXT §13 l.354-355 |
| F-TRN-10 | exp60 lab arms that use DaughterNet are an in-sample upper bound (4/5 folds saw the clips); FD dummy local 0.9249 vs K1 0.9180 is an in-sample artefact - never act on it | CONTEXT 25 Sep 18:20 ADDENDUM L5, L7 l.1875-1886 |

## CONTRADICTIONS (statements that disagree between files)

| ID | Topic | Statement A | Statement B | Current reading |
|---|---|---|---|---|
| C-01 | Edge-J weighting | CONTEXT §4 l.45: adj_edge "weighted by GT edge count" | `research/wf_ideas_v3/FINAL_REPORT.md` §j.1 + browser_intel §5: weighted by TP+FP+FN | B (Overview text); CONTEXT §4 is stale |
| C-02 | Hidden test size N | CONTEXT §1 l.14 (06 Sep): ~100-130 videos from 6 h latency; Data tab (browser_intel §5): ~199 "approximately the same size as train"; v3 FINAL_REPORT §g.1/§j.4: N ~110-160, plan for 200 | `experiments/runtime_step0/step0.md` (25 Sep 16:40): N <= ~97-106 at dummy speed | step0 bound is newest and measured; unresolved whether hidden hardware is faster |
| C-03 | Runtime limit | `experiments/ext_optimized-biohub-max-score/NOTES.md` #3: governor for a "9 h hidden rerun"; `research/discussions_summary.md` l.278: HOCT 10 h deadline | CONTEXT 25 Sep 13:58 l.1740 + browser_intel §5: 12 h (Overview) | 12 h official; 9/10 h are other notebooks' own guards |
| C-04 | 0.97 feasibility | CONTEXT l.1185 (headed "23 Sep NIGHT", written 22 Sep per C-18) and TEAM.md (friend A row): user target 0.97 (later 0.99 in v3 BRIEF); 24 Sep 10:50: target 0.97 +- 0.005 | v2 FINAL_REPORT (CONTEXT 24 Sep 18:00 l.1459): ~0.955, ceiling ~0.962; v3 §b: P(0.97 public) < 0.005; user accepted "public ~0.954" (CONTEXT 13:38 l.1583) | 0.97 out of reach by 29 Sep (retraining refused by R9); TEAM.md still shows the old target |
| C-05 | Dorado vs train embryo | `research/discussions_summary.md` l.326 (Sergio, rank 1): dorado is a DIFFERENT embryo | CONTEXT 23 Sep 23:30 l.1276: 44b6 train clips are crops of dorado (654/777 nodes coincide) | measurement kept (v3 §j.20) |
| C-06 | LB noise | CONTEXT §11a l.325-330 (08 Sep): run-to-run noise +-0.003, deltas < 0.005 not decisions | v3 §j.2 + F-MOD-07: our kernels are deterministic; 0.946/0.942 pair came from notebooks with an in-kernel PP sweep | deterministic; a 0.001 step is a real effect on one embryo, transfer is the uncertainty |
| C-07 | Tie order | CONTEXT 25 Sep 13:58 l.1738: a late byte-copy of x138 ranks at the END of the 0.953 block (read as general tie order) | FINAL_REPORT_v4 §2: within a displayed score order follows the unrounded score; time only among byte copies | B refines A |
| C-08 | Scoring latency | CONTEXT §11a l.323 "3-5 h"; RESULTS "~6 h"; CONTEXT 25 Sep 10:20 l.1526 "7-10 h" | measured L34 6.29-6.46 h, L35 6.72-7.73 h (F-RUN-03) | use measured bounds |
| C-09 | Division rule wording | browser_intel §5 (Overview Evaluation): "a connected component that covers the pre-split stage and touches both daughter lineages" | CONTEXT §4 (metrics.md): weakly connected component "not sufficient"; distinct child branches | metrics.md (code) governs |
| C-10 | Swap FN | CONTEXT 24 Sep 13:45 l.1415-1417: ~2,700 swap FN are a NODE-POSITION problem, oracle +0.03-0.046 | v3 §j.10: refuted - GT node 4.4/4.7 um from two tracks 9.4 um apart, beyond the 2 um head; annotation convention / missed node | B |
| C-11 | a_never share | v2 / CONTEXT 24 Sep 11:20 l.1368: never-detected-link ~31% of FN | v3 §j.8: 28.3% (`experiments/l2_daughternet/edge_anatomy/fn_anatomy_exp39.md`) | B |
| C-12 | Which lab gains transfer | CONTEXT 24 Sep 16:55 l.1444: lab gains trustworthy for changes that do not lean on network confidence (e.g. float output) | probes 32/33 float output tied twice; v3 §j.16 "incomplete" | only division insertion has a transfer pair (F-TRN-03) |
| C-13 | Axis-flip memorisation | RESULTS Friend B 4-video row l.91: ~97% memorised, variant CLOSED | RESULTS 12-video row l.107: memorised share only 13-19% (retraction) | B; LB closed it anyway (probe 19) |
| C-14 | Public "0.948" notebooks | CONTEXT 23 Sep 18:40 l.1229: same notebook lands 0.004 apart -> public scores are draws from ~0.945 +- 0.003 | CONTEXT 24 Sep 00:30 l.1309: pipeline is deterministic, so takaito 0.948 vs our 0.944 = different code/version | B |
| C-15 | ILP division weight closure | §10a A2 / probe 3: ILP div 0.9 neutral, closed | v3 §j.18: test invalid (ILP gives no output forks) but no need to reopen (ILP fork precision 0.19 < 0.265) | closed for a different reason |
| C-16 | R7 vs F2 default | R7 (CONTEXT 13:38 l.1667): "DIVINS_DUMP=1 is never in a submission" | exp52 (§f default F2 / fallback 5) and exp51/exp48/exp57b were built with DIVINS_DUMP=1 (`experiments/exp52_coordhead_floatout/probe.json`) | R7 written for new builds; exp52 already scored without error - needs an explicit note |
| C-17 | RESULTS vs CONTEXT | `experiments/RESULTS.md` probe 25 (exp44 v2) row: PENDING | CONTEXT 23 Sep 18:40 l.1230: exp44 bundle = 0.946 | CONTEXT; RESULTS row stale |
| C-18 | Dates of 23/24-Sep entries | CONTEXT entries headed 2026-09-23/24 above l.1218 (probes 21-23) | CONTEXT 22 Sep 20:10 DATE CORRECTION l.1218: they were written on 22 Sep UTC | probes 21-23 happened 22 Sep |
