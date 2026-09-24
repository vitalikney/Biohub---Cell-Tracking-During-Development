# arithmetic verify notes (anisotropic-forkaware-rts-smoother)
- 2026-09-24 start; no prior json
- Sources read: fn_anatomy_exp39_ef.md (a_linefit 353 = 28 44b6/325 6bba; FN total 6099; b_swap 1528, u_div 593, v_taken 556), l6 report, l5 selection (ef_a3: 21,510 dropped / 10,293+4,837 relinked on 64 sel vids), RESULTS B28 (w0.8/win2 0.9001, off 0.8856 on 12 vids), research notes (a_linefit median move 1.33um; 22% have p=0 edge in window vs 13.3% base)
- Arithmetic: 1 FN->TP ~ 1/D, D=TP+FP+FN ~ 128.9k GT edges (+FP) -> ~7.2e-6. a_linefit ceiling 353*7.2e-6 = +0.0025. Attributable to unscored-edge smoothing: excess (22-13.3)%=8.7% .. 22% of 353 -> 31..78 FN -> +0.0002..+0.0006 (gross, before symmetric losses).
- Plan: exact rs0/rs1/rs2 on a few videos with official match (scratchpad script, output to scratchpad only).
- EXACT check (scratchpad rs/rs_check.py, official match, ef_a3_rl_pr graph): 6bba_05db0fb1 (heavy ef video: 1603 dropped, 1206 relinked): control reproduced exactly (TP1113 FP82 FN70); linefit(ckpt raw, tail topology) == tail pos (err 0).
  rs0 (linefit on final topology): TP +2, FP -9, FN -2, edge J 0.87984 -> 0.88774 (+0.0079 this video); N_pred identical. rs1 (fork split) identical to rs0; rs2 (cut unscored) same counts. nodes moved >0.5um: 8.7% (rs0), 13.6% (rs2). 7 match flips.
  NOTE FP reduction dominates (not a_linefit FN rescue) -> mechanism = FP edges whose endpoints were dragged INTO match by smoothing along later-dropped edges.
- batch2 (random sel 6bba_48816121/8b7818bf/df673a83/d2b9fc0c): rs0 dTP/dFP = 0/0 on all 4 (gm nodes moved>0.5um 0-1%); rs2: -1TP +2FP on 48816121, else 0.
- batch3: 6bba_c73a1d11 (FP99): rs0 +5TP -12FP (rs2 +1/-14); 6bba_12665c0e 0/0; 44b6_81c256f0 0/0; 44b6_3a861e03 (FP21): rs0 -2TP +2FP (rs2 0/-2); 44b6_deabac95 0/0. Gains concentrate in high-FP (dense) videos.
- per-video FP (ef graph): 199 vids FP 5242 (44b6 1074 / 6bba 4168); FP>=40 in 33 vids = 3154 FP; FP>=10 in 119 vids = 4943.
- session 2 (resume): no json yet. GT totals (ef csv): 44b6 GT 19,826 FP 1074; 6bba GT 109,057 FP 4168; ef dropped 44b6 17.5k / 6bba 40.9k. GT-weighted unit (1 FP removed or FN->TP) ~ 1/sumGT ~ 7.8e-6 all-199.
  GT-weighted gains so far rs0: 05db0fb1 +9.3 units, c73a1d11 +11.8, 3a861e03 -3.8; 7 others 0. Next: run top-dropped videos 767a1e17, 78a7bd97, 32db13fc, 57b7cc1e, 786893ac, 44b6_87bba6c4.
- batch4 rs0 (dTP/dFP, GT-weighted units = dJ*GT): 767a1e17 +9/-16 (+19.3); 57b7cc1e -2/-4 (+0.6; rs2 +1/-13 = +8.1); 44b6_87bba6c4 -5/+6 (-6.9; rs2 -4/+4 = -5.2). 44b6 negative on both changed videos so far -> per-embryo gate risk (need +19.8 units on 44b6 for +0.001).
- batch5 44b6 rs0: 2f31fc2f -2/+3 (-2.9 u), 267148e4 -3/+4 (-6.1 u), e57ff5c6 0/0, cf8fed6b 0/0. 44b6 changed videos 4/4 NEGATIVE; 8 44b6 vids (incl top-dropped) sum -19.7 u = -0.0010 on 44b6 (sumGT 19.8k). rs2 same sign.
- batch6 6bba (selection) rs0: 78a7bd97 -6/+8 (-11.2 u), 32db13fc -2/-5 (+1.6 u), 3abfe10a 0/-1 (+0.7 u). rs2: -14.1 / -4.5 / -2.0.
- splits.json: confirmation = 71 44b6 (GT 19,826) + 64 6bba (GT 53,228) = 73,054 GT. Gate +0.002 = 146 u; 44b6 +0.001 = 19.8 u; 6bba +0.001 = 53 u.
- Heavy videos (ef dropped >= 700): 44b6 8 (9.7% GT), 6bba 19 (13.9% GT, 37.8% FP). Measured 5/8 heavy 44b6 -> net -19.7 u (rs0), -14.2 u (rs2): 44b6 conf ~ -0.001 -> per-embryo gate FAIL, win rate 0/4 changed.
- 6bba: 7 heavy measured sum rs0 +32.1 u (sd ~10 u/video), rs2 ~ +18 u; 5 light random = 0. Extrapolated 6bba confirmation ~ +20..45 u = +0.0004..0.0008; pooled confirmation ~ (+30 - 25)/73k ~ +0.0001 (range -0.0003..+0.0006). Selection (GT 55.8k) ~ +0.0002..0.0004. Far below +0.002.
- rs1 (fork split) == rs0 on 05db0fb1; forks 0.14% of nodes -> division term effect ~0.
- VERDICT: refuted (arithmetic). JSON written.
