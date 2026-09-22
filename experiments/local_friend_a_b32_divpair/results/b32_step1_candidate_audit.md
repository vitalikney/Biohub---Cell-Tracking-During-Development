# B32 Step 1 — candidate reach audit

Date: 2026-09-22. Scope: all 199 training videos, B20 `friend_a_b20_exp29`
checkpoints, official 7 um one-to-one node matching. No training and no
leaderboard submission were performed.

## Registered result

| group | videos | candidates | covered GT divisions | GT divisions | coverage |
|---|---:|---:|---:|---:|---:|
| all | 199 | 338,285 | 58 | 151 | **38.4%** |
| 44b6 | 71 | 196,180 | 6 | 26 | **23.1%** |
| 6bba | 128 | 142,105 | 52 | 125 | **41.6%** |

The registered gate is greater than 90%, so the pipeline stopped before crop
caching or GPU training.

## Where reach is lost

The cumulative audit follows each GT division through the source graph and the
registered candidate rules:

| stage | count | fraction of 151 |
|---|---:|---:|
| GT divisions | 151 | 100.0% |
| parent detected | 149 | 98.7% |
| parent and both daughters detected | 121 | **80.1%** |
| parent has exactly one child | 120 | 79.5% |
| existing child is a valid next-frame link within 10 um | 120 | 79.5% |
| existing child matches a GT daughter | 117 | 77.5% |
| other daughter is a valid predicted node | 117 | 77.5% |
| other daughter within 15 um of parent | 116 | 76.8% |
| sister separation 5–20 um | 116 | 76.8% |
| DeepCenter candidate score at least 0.20 | 97 | 64.2% |
| candidate is an orphan | 58 | **38.4%** |

Thus the first hard ceiling is detection: only 80.1% have all three required
nodes, already below the 90% target. The largest later loss is the orphan-only
rule: 39 otherwise reachable second daughters are already linked to another
parent.

## Falsification sweeps

| pool | candidates | positives / covered | coverage |
|---|---:|---:|---:|
| registered: parent 15 um, sister 5–20 um, DC >= 0.20, orphan only | 338,285 | 58 | 38.4% |
| parent radius 30 um, other registered rules unchanged | 736,825 | 59 | 39.1% |
| relaxed orphan ceiling: radius 30 um, sister 0–40 um, no DC veto | 4,854,901 | 63 | 41.7% |
| registered geometry/DC but allow stealing linked nodes | 16,317,552 | 97 | 64.2% |

The radius expansion requested by the plan adds only one division. Stealing
raises reach but still misses the 90% gate and expands the pool to 16.3 million
triples. It is not silently substituted for the registered recipe.

## Decision

**B32 is stopped at Step 1 under the current plan.** Training 25 epochs on 58
positive events cannot validate the stated pair-model hypothesis, and a radius
change cannot repair the missing detections. The nearest viable redesign must
change an upstream assumption: recover missing daughter detections and/or allow
claimed daughters with a learned edge-replacement decision. That is a new
experiment and must be registered explicitly; it is not a safe parameter tweak
inside B32.
