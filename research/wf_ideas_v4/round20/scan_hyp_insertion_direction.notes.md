# scan_hyp_insertion_direction notes (round 20, started 2026-09-27T20:02Z)
- 20:03Z read: CONTEXT l.2599-3216 (RESUME 26 Sep 22:46Z .. 20:02Z 27 Sep). KEY NEW FACT: probe 45 exp70g (K2 + cap 6) = 0.956 (#162, 113 passed; ledger L (7.49, 7.67] h, insertion gate did NOT fire), while the exp60 lab said cap 6 = -0.00057 (0 TP / 4 FP / 81 unannotated among 85 extras) -> lab sign wrong again (2nd time after dc0.30).
- Probe 46 exp70q (cap6 + thr0.3 + fm45) 56611472 PENDING, expected ~22:00-22:40Z.
- Dummies (4 clips, forks): K2 75; exp70g cap6 81; exp78a cap8 86; exp76e fm+cap6 80; exp70q fm+cap6+thr0.3 82; exp70b fm 74. Dummy runtimes: K2 1,512 s; exp78a 1,486; exp76e 1,279; exp70b ~1,740; exp70q 1,874 -> noise band ~1,280-1,880 s among configs with identical insertion work.
- Scale (R15DS-1, round15/scan_hyp_div_sensitivity.json): public D ~44 GT divisions (19-72), J ~0.28-0.38; one public TP ~+0.0023, one FP ~-0.0007; break-even evaluable precision J/(1+J) ~0.22-0.27.
- ins_cap6.json: cap binding lab: cap4 45/56 clips at cap; cap6 39/56; cap8 25/56; uncapped 525 insertions vs 201 (cap4) / 286 (cap6) / 345 (cap8). steal_cap = floor(0.5*cap).
- div_insert.py: DaughterNet p computed for all candidate triples BEFORE cap/threshold -> cap/thr/frame-cap change no GPU work; only steal on/off changes the candidate set (e.g. 44b6_0db75fae 2340 triples, 1064 steal).
- 20:15Z LAB SWEEP (scratchpad/r20ins/sweep2.py + an2.py -> sweep2_raw.json, an2.json; 564 s, 6 workers; tools/ untouched; params = trainlab.INS35 + overrides; cap4 row reproduces ins_cap6 exactly: 0.939878, div 25/31/74). IN-SAMPLE DaughterNet, sign unreliable (cap6 lab -0.00057 vs public +0.002). Pooled delta vs cap6 (ALL | 44b6 | 6bba), div TP/FP/FN, added, extras vs cap6 (TP/FP/ign, med score):
  cap8 +0.00061 | 0 | +0.00070 | 26/36/73 | 345 | 60 (1/1/58, 0.496)
  cap10 +0.00068 | 0 | +0.00071 | 27/41/72 | 389 | 104 (2/6/96)
  cap12 +0.00126 | 0 | +0.00137 | 28/42/71 | 423 | 138 (3/7/128, 0.492); clips at cap 15/56
  cap12_fc2 +0.00123 | 0 | +0.00135 | 28/42/71 | 462 | 176 (3/7/166)
  cap6_fc2 +0.00021 | 0 | +0.00025 | 25/34/74 | 289 | 30 (0/1/29)
  cap8_fc2 +0.00092 | 0 | +0.00102 | 27/39/72 | 364 | 83 (2/4/77)
  cap6_t03 0.00000 (digest-identical scores; 28 extra all unannotated) | 25/35/74 | 314
  cap6_t02 +0.00044 | -0.00074 | +0.00070 | 26/37/73 | 334 | 48 (1/2/45, 0.316)
  cap8_t03 +0.00120 | 0 | +0.00138 | 27/37/72 | 402 | 117 (2/2/113)
  cap12_fc2_t03 (I3) +0.00166 | 0 | +0.00181 | 29/44/70 | 581 | 295 (4/9/282)
  cap16_fc2_t02 (I4) +0.00233 | -0.00152 | +0.00303 | 32/53/67 | 843 | 557 (7/18/532)
  unc (fc1) +0.00138 | 0 | +0.00146 | 29/46/70 | 525 | 240 (4/11/225)
  unc_fc2 +0.00129 | 0 | +0.00131 | 30/51/69 | 691
  unc_fcU (no frame cap) -0.00022 | 0 | -0.00048 | 30/59/69 | 1097, 519 steals; adj edge -0.00055 (steal edge damage)
  cap6_nosteal -0.00202 | -0.00503 | -0.00158 | 22/32/77  (steal OFF clearly bad, as in I-068)
  cap8_nosteal -0.00093; cap6 steal_frac 1.0 -0.00009; cap8 sf1 +0.00051 (< cap8 +0.00061)
  cap6_t05 -0.00013 | +0.00079 | -0.00031 | 24/31/75 | 216
- Clips are 100 frames. Uncapped (fc1) per-clip insertions: median 7, IQR 5-12, max 30; with no frame cap up to 133 (dense clips).
- Lab precision by DaughterNet score band (unc_fcU pool, evaluable only): 0.6-0.8 6TP/7FP (0.46); 0.5-0.6 6/11 (0.35); 0.45-0.5 1/5 (0.17); 0.4-0.45 1/11 (0.08). Lab break-even q* = J/(1+J) ~0.16 (lab J 0.19); public ~0.22-0.27.
- Evaluable fraction of insertions (lab): 5-7% (cap4 set 15/201, cap6 extras 4/85, cap12 extras 10/138).
- 20:25Z SWEEP 3 (scratchpad/r20ins/sweep3.py -> sweep3_raw.json, an3.json; 230 s). vs cap6 (ALL | 44b6 | 6bba), div, added, extras vs cap6:
  cap16_fc2 +0.00133 | 0 | +0.00141 | 29/46/70 | 528 | 242 (4/11/227)
  cap24_fc2 +0.00188 | 0 | +0.00204 | 30/47/69 | 606 | 320 (5/12/303); clips at cap 6/56; adj edge -8e-6
  cap24_fc2_t03 +0.00282 | 0 | +0.00308 | 32/50/67 | 915 | 629 (7/15/607)
  cap16_fc2_t03 +0.00240 | 0 | +0.00263 | 31/48/68 | 721
  cap12_fc3 +0.00107; cap24_fc1 +0.00142 (517, ~= unc fc1 525); cap40_fc3 +0.00088 (743; FP 29, adj -7e-5) -> frame cap 3 worse than 2.
  vs K2 (cap4) pooled: cap12_fc2 +0.00066, cap24_fc2 +0.00131, cap24_fc2_t03 +0.00225; 44b6 stays -0.00079 vs K2 for every cap >= 6 (one FP fork in 44b6_e29f0176), 6bba cap24_fc2 +0.0015 vs K2.
  READING: in-sample lab is non-monotone: dip at cap 6 (4 FP events), recovery from cap 8, monotone rise to cap 24 fc2; fc3 and no-frame-cap lose (FP and steal edge damage). Lab and public now AGREE in sign for cap >= 12 fc2 (lab small-n, in-sample).
- 20:35Z MC (scratchpad/r20ins/mc2.py -> mc2.json, 60k draws, 5,194 accepted by conditioning on K2 0.954 -> cap6 0.956). Model: every lab insertion stands for Poisson(N_pub/56 * m_vol) public ones, N_pub U(29,38) clips (hidden ~100-130 videos x 0.29), m_vol LogU(0.6,1.6); evaluable frac lab 3.8% x LogU(0.5,2); P(TP|evaluable, score) = lab logistic (b0 -1.00, b1 5.01 around 0.5: q(0.6) 0.38, q(0.45) 0.22, q(0.3) 0.12) + public logit shift N(0,1.2); TP value LogN(median 0.0023, sd 0.5), FP value 0.25-0.4 x TP (R15DS-1); lab adj-edge delta added; rounding to 3 dp. MODEL ESTIMATES (unconditional on 46): 
  rung: E[delta vs exp70g] / P(display >= 0.957) / P(<= 0.955) / P(<= 0.954)
  cap8 +0.0007 / 0.40 / 0.28 / 0.09;  cap10 +0.0012 / 0.51 / 0.29 / 0.13;  cap12 fc1 +0.0016 / 0.55 / 0.29 / 0.16
  cap12 fc2 (exp78b) +0.0021 / 0.60 / 0.28 / 0.17;  cap16 fc2 +0.0027 / 0.63 / 0.28 / 0.19;  cap24 fc2 +0.0036 / 0.645 / 0.27 / 0.21
  cap24 fc1 (~uncapped fc1) +0.0024 / 0.60 / 0.29 / 0.19;  uncapped fc2 +0.0041 / 0.65 / 0.29 / 0.22;  no frame cap +0.0071 / 0.665 / 0.30 / 0.26 (heavy tails)
  cap12 fc2 thr0.3 (I3) +0.0021 / 0.56 / 0.34 / 0.25;  cap16 fc2 thr0.2 (I4) +0.0020 / 0.53 / 0.41 / 0.35;  cap6 thr0.2 -0.0001 / 0.20 / 0.39
  cap6 fc2 -0.0001 / 0.28 / 0.35;  cap6 steal off -0.0013 / 0.24 / 0.60;  size-scaled cap 6x(n/median) in [4,12] +0.0003 / 0.37 / 0.39.
  P(probe 46 display): 0.955 0.19, 0.956 0.57, 0.957 0.08, >=0.958 0.11, <=0.954 0.05.
  Caveat: one public read drives everything; E is dominated by the right tail; the ordering among cap12fc2 / cap16fc2 / cap24fc2 is within model noise; what the model does separate is (a) fc<=2 and thr 0.4 have less downside than thr<0.4, (b) steal off and size-scaling lose, (c) cap 8 is the weakest volume rung.
- (clock note: the '20:15Z/20:25Z/20:35Z' stamps above are approximate; date -u at the end of the MC was 20:24Z.)
- 20:26Z dummy clips = 44b6_0113de3b, 44b6_0b24845f, 6bba_05b6850b, 6bba_05db0fb1 (train copies, not in the exp60 56-clip split). Dummy fork steps so far: cap4->6 +6 (1.5/clip; lab 1.52), cap6->8 +5 (1.25/clip; lab 1.07). Predicted dummy forks from lab extras/clip: cap12 fc2 ~94 (88-100), cap24 fc2 ~104 (95-115); nodes must equal 121,252 (insertion adds edges only).
- 20:26Z runtime: kernel DIVINS_CALL scores candidate_triples(...) nodes with DaughterNet BEFORE cap/threshold/frame cap (tools/build_probe_kernel.py l.355-362; div_insert.insert_divisions only selects) -> cap/fc/thr add no GPU work; only DIVINS_STEAL changes the candidate set. Hidden ledger: exp70g (7.49, 7.67] h vs K2 (7.36, 7.54] h vs 43/44 (7.56, 7.74] h (no insertion change) -> within latency noise.
- 20:26Z name check: no experiments/exp80* folder exists; exp78b probe.json = K2 knobs + DIVINS_CAP 12 + DIVINS_FRAME_CAP 2 (thr 0.4, steal 1, alpha 1).
- Did not use web search: this is a knob-direction question on our own code; no external source changes the answer.
- 20:26Z final JSON written (8 findings R20ID-1..8).
