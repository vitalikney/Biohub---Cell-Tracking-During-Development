**Skeptic re-check of the four lenses (exposure, relrank, model, adversary)**

Bottom line: the facts behind all four lenses hold, and every model number reproduces. The main problems are the claims about how safe the #37 partner is, and the categorical "keep #37 over exp75" advice. The files support that advice only if CI (coordinject) fails on the private embryo.

**The 5 decision-relevant numbers, re-checked**

1. **Leaderboard blocks and medal lines: CONFIRMED.**
   - Recomputed from lb.csv e10_20260929T1141Z: 1,006 rows. We are rank 141 (0.959, SubmissionCount 56, 17th of 22 in the 0.959 block). 124 teams are ≥0.960 and 53 are ≥0.965.
   - Blocks by rank: 0.959 is #125-146, 0.958 #147-167, 0.957 #168-234, 0.956 #235-384 (150 teams), 0.955 #385-484 (100), 0.954 #485-599 (115), 0.953 #600-1006 (407).
   - With 3,994 teams (CONTEXT l.4548), silver ~#199 falls in the 0.957 block and bronze ~#399 in the 0.955 block. The 475 teams at 0.954-0.959 and the submission-count medians (63.5 / 57 / 38) also check out.
   - Caveat: relrank's label "0.953 = точные копии x138" (all 407 teams at 0.953 are exact x138 copies) is unproven. It only means those teams were seen at 0.953.

2. **Public lift decomposition 0.953 → 0.954 → 0.956 → 0.958 → 0.959: CONFIRMED.**
   - Sources: RESULTS l.67 (P34), l.70 (#37), l.78 (P45; exp70g = K2 + cap 6 only, CONTEXT l.2473), CONTEXT l.3856 (P50), l.4153 (P51).
   - The lenses count the public-only share differently: exposure says 4 of 6 thousandths, adversary says 5 of 6. The difference is only whether CI is counted as "mixed" or "public-only".

3. **Cap-6 lab −0.00057 (bootstrap 90% −0.00125..−0.00011, 85 extra insertions = 0 TP / 4 FP / 81 unannotated): CONFIRMED** at CONTEXT l.2545-2547 and FACTS F-TRN-42.
   - Overstated as evidence against cap 6: it rests on only 4 annotated insertions out of 85. CONTEXT C-133 calls it an "in-sample, near-blind estimate". F-TRN-68 says the dummy lab "MISSED cap 4 → 6 (lab 0.0000, LB +0.002; the lab has 0 division TP)".
   - So cap 6 has no usable lab evidence in either direction, not "clear negative lab evidence".

4. **Insertion "honest CV" +0.0019, 90% CI [−0.0007, +0.0050], 27% precision: the number is CONFIRMED (CONTEXT l.1305-1307), but it is overstated as backing for the shipped lever.**
   - The same line says the run "Fails the gate narrowly (... 4/15 = 27% < 31%)". l.1308 says "even a perfect transfer would move the public score by ~0".
   - The confirmed setup was the v1 steal sub-test at threshold 0.5, on the pre-x138 exp39 line. The shipped #35/#37 config uses "ens threshold 0.4" (l.1331, l.1770), and l.1305 says the threshold "must be re-calibrated for the ensemble".
   - The folds held out videos, not an embryo. Adversary's "no lever has honest out-of-embryo validation" is the accurate wording.
   - Exposure's "CV-backed" should read: "held-out-video OOF for an earlier config on an earlier base; failed its gate; public +0.001 twice".

5. **Monte Carlo numbers: all REPRODUCED from scratchpad cyrus/grid.txt and my rerun of mc_cyrus.py.**
   - Model lens:
     - Default: {exp87a, #37} 0.789-0.790 bronze / 0.577-0.587 silver.
     - Harsh (cap 6 and K centred at −0.001): 0.556-0.561 / 0.191-0.197. With CI also 0: 0.530-0.536 / 0.159-0.167.
     - exp87a alone, harsh: 0.13-0.25 bronze. Field "central": 0.376-0.378 / 0.078-0.085. FIELD=now and KCLONE rows match.
   - Adversary: my seed-39 rerun gives 0.667/0.336 (they quote 0.673/0.343) and 0.556/0.193 (they quote 0.568/0.200). Within seed noise.
   - Relrank (reran rr/scen.py): #141 in scenario (b), #217 with cap 6 = 0, #287 with cap 6 at its lab value, #162 with CI = 0, #346 with cap 6 + CI = 0, #541 in a-worst, #309 with K2 at +0.003. Scenario (c) P(silver) 0.81 / 0.63; scenario (d) pair P(silver) 0.59, P(bronze+) 0.85. 769 proven forks. All match.

**Wrong or unsupported claims**

- **The "floor" claims in exposure and adversary are wrong as worded.**
  - Exposure: "falls back to about #37/exp75 level ... around the bronze boundary, not a collapse". Adversary: "worst realistic outcome = x138 + insertion ... costs silver much more than bronze".
  - #37 alone at 0.954 ranks about #489 on today's board (scen.py prints "#37 as best would be ~489"). That is below the bronze line (#399). FACTS F-TRN-63 says the same: "#37 (0.954) sits below the public bronze line". exp75 at 0.955 straddles the line.
  - Falling back to #37 keeps bronze only if the rival forks also lose their public gains. Evidence:
    - relrank a-worst: #541, no medal.
    - #37 alone P(bronze+): scenario (c) 0.29-0.32; model 0.48 in general, 0.31 when the field keeps its gains ("central").
- **"#37 is the better partner than exp75 in both adversarial worlds" (adversary) is true only for bronze.**
  - Levers-at-0 world: exp75 wins silver (0.355-0.360 vs 0.336-0.343).
  - At the model's default settings with the standing CI prior (CI_SD 0.0008, my rerun), exp75 wins both: 0.821/0.616 vs 0.784/0.576. F-TRN-66 records the same (.824/.622 vs .791/.580) and marks "P3 slightly ahead" as refuted.
  - Exposure's "Do not swap #37 for exp75" is therefore a bet that CI fails on the private embryo, not something the model shows. The earlier chat answer (CONTEXT l.4581: "the choice is the sign of CI on the private") is the correct framing.
- **"CI was adopted even though our lab pointed the other way" (adversary) is wrong on timing.**
  - At selection time (27 Sep 12:49Z, l.2985) the refiner lab was +0.0032 at ALPHA 0.5.
  - The −0.0055 dummy-lab read came later (round 28). F-TRN-60(b) says it is one event and "never a sign read for coordinate-only changes".
  - Only cap 6 was submitted against its own pre-registered rule.
- **"The teams above 0.960 mostly bring their own retrained models" (exposure) is only partly supported.**
  - Relrank's own trajectory run: of the 71 teams at 0.960-0.964, 18 were seen at 0.953/0.954 and only 24 were already ≥0.960 on 26 Sep 16:20Z.
  - Only the 53 teams at ≥0.965 look mostly independent (43 were already ≥0.960 by then).
- **Relrank's verdict "без медали только в одном случае (~#541)" (no medal in only one case, ~#541) omits a line its own script prints.**
  - "cap6+K+CI = 0 (K own-only) → rank 570" is also outside the medals.
  - Scenario (b) (#141 for any shared loss L) holds by construction: it assumes we lose exactly what every fork loses. That is the opposite of Cyrus's premise that the more over-fitted files lose more.
- **Minor.**
  - Exposure quotes the finals-card model П3 0.68-0.85 / 0.39-0.63. Those are the exp85a numbers, now stale (C-263). The round-31 exp87a re-run gives 0.61-0.83 / 0.39-0.64.
  - The grid's "{#37,#38} ticked" row label is also stale (the current tick is {exp87a, #37}), but the numbers themselves are fine.

**Contradictions between the lenses**

- **Risk grade.** Relrank rates it "moderate, medal likely". Its (c) and (d) scenarios give P(bronze+) 0.85-1.0 because the independent teams hold and the forks only jitter. The model lens under Cyrus-harsh assumptions gives 0.53-0.56, and 0.38 if the field keeps its gains.
  - The difference comes entirely from the field assumption: do rival forks lose their public-tuned gains as well?
  - Nobody can measure that. The honest range for the ticked pair is about 0.4-0.85 bronze and 0.1-0.6 silver.
- **What honest validation supports insertion.** Exposure says an honest CV check; adversary says none out-of-embryo; relrank says it is based on the training embryos. Per item 4, the adversary's wording is the most accurate.
- **CI classification.** Exposure calls it neutral/mixed; relrank and adversary call it public-only. The refiner lab was in-sample positive, the dummy lab has the wrong sign (0 of 2), and there are three +0.001 public reads, all on one embryo. "Mixed, leaning public" is fair.

**What holds across all four lenses**
- We are in Cyrus's category.
- The #37 hedge is what keeps the bronze probability up. Without it, exp87a alone drops to 0.13-0.25 bronze under the harsh assumptions.
- The reserve slot has no safe use now. An x138-family file had to be submitted by about 14:30-15:00Z (CONTEXT l.4586).
- The {exp87a, exp85a} pair is the worst option (0.17-0.27 bronze under harsh assumptions).

**Evidence that does not exist**
- Any private or out-of-embryo read of cap 6, K or CI.
- The rival field's actual composition. Fork versus independent is a proxy built from snapshots taken since 26 Sep 16:20Z.
- The adversary's MC outputs were not saved to files; I reproduced them approximately.

Files I read or ran (no repo writes, no Kaggle calls):
- C:\Users\vital\Documents\kAGGLE\Biohub - Cell Tracking During Development\CONTEXT.md
- C:\Users\vital\Documents\kAGGLE\Biohub - Cell Tracking During Development\experiments\RESULTS.md
- C:\Users\vital\Documents\kAGGLE\Biohub - Cell Tracking During Development\research\KNOWLEDGE\FACTS.md
- C:\Users\vital\Documents\kAGGLE\Biohub - Cell Tracking During Development\experiments\lb_poll\_lb\e10_20260929T1141Z\lb.csv
- C:\Users\vital\AppData\Local\Temp\claude\c--Users-vital-Documents-kAGGLE-Biohub---Cell-Tracking-During-Development\acabaea6-42c1-4115-a146-2ddc5bb7e8c8\scratchpad\cyrus\grid.txt, cyrus\mc_cyrus.py, r26\mc26.py, rr\scen.py, rr\traj.py