# v_hyp_insertion_direction R20ID-1 notes (2026-09-27)
- 20:28Z verified an2/an3.json numbers match finding (cap24_fc2 +0.001883 ALL, 44b6 0, 6bba +0.002037; extras vs cap6 5TP/12FP/303ign). NOTE unc_fc2 (691 ins) = +0.001293 < cap24_fc2 +0.001883 -> cap24fc2 is a lab PEAK, not a monotone top; 44b6 d_cap6 = 0 for EVERY arm >= cap6 except t02/nosteal -> entire signal from 6bba.
- CLIP BOOTSTRAP + LOO (scratchpad/r20ins/boot_v.py, 400 clip resamples of 56, trainlab.summarise_rows on sweep2_raw/sweep3_raw):
  arm vs cap6: d / P(boot>0) / CI90 / d after dropping the top-2 contributing clips
  cap8 +0.00060 / 0.64 / [-0.00030,+0.00208] / -0.00016
  cap12_fc2 +0.00123 / 0.79 / [-0.00100,+0.00385] / -0.00027
  cap16_fc2 +0.00133 / 0.73 / [-0.00124,+0.00437] / -0.00087
  cap24_fc2 +0.00188 / 0.90 / [-0.00045,+0.00491] / -0.00028
  unc_fc2 +0.00129 / 0.77 / [-0.00141,+0.00420] / -0.00069
  vs K2 (cap4): cap12_fc2 +0.00066 P 0.65; cap24_fc2 +0.00131 P 0.71 (CI90 [-0.00164,+0.00495]); minus top-2 clips -0.00088..-0.00089.
  Top contributors every arm: 6bba_9a41d029, 6bba_337b1b3a, 6bba_3fda6b25 (all 6bba). 44b6 = 0 for all caps >= 6.
  -> 'lab agrees in sign for cap>=12 fc2' rests on 2-3 clips / ~3-5 TP events; no arm's CI90 excludes 0.
- Shape: cap24_fc2 +0.00188 > unc_fc2 +0.00129 (lab falls again above cap 24) -> cap24fc2 is the max of 29 noisy arms (winner's curse), not 'top of a monotone curve'.
- fc2 vs fc3 at cap12: +0.00123 vs +0.00107 (diff 1.6e-4 ~ one FP event). thr: lab PREFERS 0.3 (cap24_fc2_t03 +0.00282) -> 'thr 0.4' is not from this fact. steal off -0.002 = 44b6 loses 1 TP (div 1/8/10 vs 2/9/9) -> one event, but consistent with earlier I-068.
- Robust-ish part only: no frame cap -> adj edge -0.00055 (519 steals, a many-event edge effect, not a division count).
- Feasibility: logging only; knob rungs are under user aggressive-mode lift (CONTEXT l.2940/2946, 27 Sep 11:14/11:16Z). No R8 issue, no runtime (cap/fc/thr post-scoring).
