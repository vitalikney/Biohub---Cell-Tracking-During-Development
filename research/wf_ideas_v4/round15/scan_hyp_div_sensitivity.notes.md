# scan_hyp_div_sensitivity notes (round 15, started 2026-09-27T05:31:02Z)
- 05:45Z read: CONTEXT l.2790-2814 (D1 read 04:58Z: dc0.30 = 0.949 vs K2 0.954; exp70j/k built 04:59Z; submitted 05:28Z as probes 43/44, class C).
- exp60 lab dc rows (experiments/exp60_trainlab/results.md l.49-72): control div TP/FP/FN 44b6 1/8/10, 6bba 15/17/73.
  dc0.30: 44b6 1/6/10, 6bba 15/11/73 (0 TP lost, 8 FP removed, forks -128). dc0.20: 6bba 15/23/73 (+6 FP, 0 TP; forks +138).
  dc0.15: 6bba 15/30/73 (+13 FP). dc0.35: 44b6 0/1/11, 6bba 10/6/78 -> 6 TP lost -> lab TP cluster sits in [0.30,0.35).
- Metric: tools/official/src/tracking_cellmot/metrics.py l.474-531: division J MICRO-averaged (pooled TP/FP/FN over all public clips);
  score = adj_edge + 0.1*divJ. FACTS F-MET-08: public div J ~0.36 (upper bound; probe 26 forks-off 0.911 vs 0.947).
- Mechanism (exp70j notebook l.4087-4210): DeepCenter safe-div veto scores the CANDIDATE second daughter v (center-prior heatmap
  of the 44b6-trained UNet3D, win z1/yx2) and rejects if < threshold; then ranker parent_dist+0.15*sister_dist, frame cap
  0.8% of sources, global cap 0.4% of edges. Safe divisions run BEFORE the DaughterNet insertion (l.4607 vs l.4693); insertion
  uses orphans only (+steal), cap 4/video, frame cap 1, no DeepCenter in the insertion gate.
- Dummy fork bands (4 clips; CONTEXT 21:38Z, 05:28Z): [0.25,0.30) 20 forks, [0.225,0.25) 13, [0.20,0.225) 8 (75 total at 0.25).
- 06:05Z PRIOR PUBLIC EVIDENCE on the same embryo (CONTEXT 11 Sep 14:20 MSK l.698-710; IDEAS I-018): sjlee stack (same DeepCenter
  checkpoint + DC TTA=1 + sister 14 safe-div lineage as x138 cell 0 l.26-66) public forks: DC 0.20 = 0.947, DC 0.25 (+sectta1) = 0.947
  (sectta1 alone 0.947), DC 0.15 = 0.946. => on public, band [0.20,0.25) net |d| < 0.001; band [0.15,0.20) net ~ -0.001.
- SHIFT(-0.05) hypothesis explains all 3 public facts: public dc0.30 (-0.005) ~ lab dc0.35 cliff (6bba -0.0036, 44b6 -0.0074; 6 TP
  lost in lab [0.30,0.35)); public 0.20-vs-0.25 tie ~ lab 0.25-vs-0.30 (+0.001/-0.0006); public 0.15-vs-0.20 (-0.001) ~ lab 0.20-vs-0.25
  (-0.0008). r_ladder L2 already foresaw 'on a shifted embryo 0.30 acts like 0.35 (-0.004..-0.007)'.
- MC (scratchpad dcmc.py/dcmc2.py/dcmc3.py; priors G U(10,45), J U(0.28,0.38), recall U(0.35,0.6), evaluable forks in [0.25,0.30)
  Poisson(U(2,10)), precision U(0,1); conditioned on K2 in [0.9535,0.9545) and dc0.30 display 0.949):
  D=TP+FP+FN 5/50/95% = 19/44/72; one public div TP = +0.0014/0.0023/0.0052; one FP = -0.0004/0.0007/0.0018;
  TP forks lost at dc0.30 k0 = 1/3/4 (P(k0=1) 0.09, 2 0.33, 3 0.37, 4 0.17); FP removed f0 = 0/2/6; removed-band evaluable precision
  0.33/0.60/1.0 (break-even J/(1+J) ~0.26).
  Predicted displays (bins <=952/953/954/955/>=956): H-FLAT 44 [.11,.08,.12,.09,.61] 43 [.11,.05,.07,.06,.71];
  H-DECAY 44 [.27,.16,.17,.12,.28] 43 [.39,.14,.13,.10,.24]; H-LAB q=0.05 44 [.60,.22,.13,.03,.03] 43 [.76,.13,.06,.02,.02];
  SHIFT(FP-only, lamF U(0.5,4)) 44: 0.954 .46 / 0.953 .32 / <=0.952 .21; 43: 0.954 .23 / 0.953 .29 / <=0.952 .40.
- Insertion: K2 - twin display +0.001 => unrounded (0, 0.002) => ~1 public TP + 1-2 FP. Lab cap6 extra 85 ins: 0 TP/4 FP (CONTEXT 21:56Z).
  Cap 4 binds nearly everywhere (I-220) => DIVINS_THRESH 0.4 -> 0.3 nearly inert; I-308 tighter refuted; I-326 cap6 refuted.
- Build template (research/wf_ideas_v4/reach0955/r_ladder.json L2 exp70d): python tools/build_probe_kernel.py <name> --base x138
  --patch divinsert --patch safetail --patch lowrefine $K --set DEEPCENTER_SAFE_DIV_THRESHOLD=<t> --note "..."
- 06:25Z final JSON written (11 findings, R15DS-1..11).
