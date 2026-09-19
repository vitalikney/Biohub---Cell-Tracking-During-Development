# Friend A B20 cached follow-up

All results below use the official metric on all 199 train videos. No detector/linker inference, model training, or
leaderboard submission was performed: the experiment reuses the completed `friend_a_b20_exp29` cache.

## DivNet parent diagnostic

- Scored parents: 3,821,426.
- GT division parents: 151; matched to a scored parent in the same frame within 7 microns: 142 (94.0%).
- AUC: **0.8340**.
- hits@1/2/3: **0.2676 / 0.3521 / 0.3944**, ranked within each dataset/frame.
- Published reference: AUC 0.887, hits@1/2/3 0.28/0.40/0.46.

The AUC is in the expected high-signal range and the hit rates are close to the published reference. The cached input
construction is therefore working; the failed first B20 pass was an integration/design problem rather than a random
DivNet output. Full distributions and per-video coverage are in `b20_followup_diagnostic.json`; the dependency-free
histogram is `b20_followup_diagnostic.svg`.

## Pure public-candidate re-ranking

Candidate pool: public orphans only, no steals, exact parent radius <= 12 microns, sister separation >= 5 microns,
public hard gates, frame/global caps and DeepCenter veto. The matched geometry control verifies this implementation
against the original public control before changing the order.

Gate: score >= original control + 0.005, division TP increases, and adjusted-edge delta >= -0.001.

| variant | score | delta | adjusted edge | edge delta | div J | TP/FP/FN | gate |
|---|---:|---:|---:|---:|---:|---:|:---:|
| original public control | 0.912028 | +0.000000 | 0.902311 | +0.000000 | 0.097166 | 24/96/127 | reference |
| matched geometry control | 0.912054 | +0.000026 | 0.902172 | -0.000139 | 0.098814 | 25/102/126 | no |
| DivNet, no threshold | 0.911610 | -0.000417 | 0.902124 | -0.000187 | 0.094862 | 24/102/127 | no |
| DivNet, p >= 0.5 | **0.914300** | **+0.002273** | **0.902445** | **+0.000134** | **0.118557** | 23/43/128 | no |
| hybrid p / (1 + public geometry cost) | 0.911919 | -0.000108 | 0.902154 | -0.000157 | 0.097656 | 25/105/126 | no |

The `p >= 0.5` filter removes 59 division false positives and improves score by 0.00227, but also loses one true
division and remains below the required +0.005. The hybrid restores one extra true division but also restores false
positives and gives no score gain. No variant passes the registered gate, so B20 is closed and no LB probe is justified.

## Reproduction

Run from the repository root with the project Python. Every pass-2 command is resumable per video.

```powershell
$b20Cache = "C:\Projects\CellTracker\outputs\local_friend_a_b20_divnet\cache"
$b20Data = "C:\Projects\CellTracker\train"
$b20Scores = "$b20Cache\friend_a_b20_exp29\divnet"

python experiments/local_friend_a_b20_divnet/diagnose_divnet.py `
  --tag friend_a_b20_exp29 `
  --cache-dir $b20Cache --data-dir $b20Data `
  --out C:\Projects\CellTracker\outputs\local_friend_a_b20_divnet\followup\divnet_diagnostic.json

python experiments/local_friend_a_b20_divnet/pass2_public_rerank.py `
  --tag friend_a_b20_exp29 --ranker geometry --parent-um 12 --sister-min-um 5 `
  --cache-dir $b20Cache --data-dir $b20Data `
  --label followup_geometry_public12_sister5 --resume

python experiments/local_friend_a_b20_divnet/pass2_public_rerank.py `
  --tag friend_a_b20_exp29 --ranker divnet --parent-um 12 --sister-min-um 5 `
  --cache-dir $b20Cache --data-dir $b20Data --scores-file $b20Scores `
  --min-score -1 --label followup_divnet_public12_sister5_all --resume

python experiments/local_friend_a_b20_divnet/pass2_public_rerank.py `
  --tag friend_a_b20_exp29 --ranker divnet --parent-um 12 --sister-min-um 5 `
  --cache-dir $b20Cache --data-dir $b20Data --scores-file $b20Scores `
  --min-score 0.5 --label followup_divnet_public12_sister5_p05 --resume

python experiments/local_friend_a_b20_divnet/pass2_public_rerank.py `
  --tag friend_a_b20_exp29 --ranker hybrid --parent-um 12 --sister-min-um 5 `
  --cache-dir $b20Cache --data-dir $b20Data --scores-file $b20Scores `
  --min-score -1 --label followup_hybrid_public12_sister5_all --resume
```
