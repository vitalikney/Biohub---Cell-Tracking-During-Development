# v_recheck R43-RC-B notes (2026-09-29T16:25:01Z)
- no prior json; RESULTS.md l.26-27 exp11/exp11+pp, l.30 exp10 v2 hold12 0.9902, l.33 probe1 LB 0.899; l.107 exp29 LOEO full stack pp +0.0261
- verified numbers (RESULTS.md l.25-33): B 0.8825->0.9059 = +0.0234 (gap5 +0.0109, direct8 +0.0080, div5/12 +0.0045); A 0.8798->0.8963 = +0.0165; in-embryo exp10 0.9575->0.9728 = +0.0153; probe 1 LB 0.899 vs hold12 0.9902. Detector = exp03B / pilkwang pretrained, pre-x138.
- nuance: LOEO pp 0.906 was closer to probe-1 LB 0.899 than hold12 0.990 -> exp11 was the better predictor of LB level; it does not undermine the verdict (structural stages, not 0.001 knobs).
- nuance: arm A 'pretrained' may have seen 44b6 in pretraining; arm B is the clean unseen-embryo arm. No effect on verdict.
- R41-RC-B (round41/scan_recheck.json) = K out-of-embryo argument; finding cites it correctly. Action None; nothing to build/dummy/submit. NOT refuted.
- 2026-09-29T16:25:38Z final JSON written (refuted=false)
