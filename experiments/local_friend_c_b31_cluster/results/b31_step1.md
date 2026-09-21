# Friend C B31 — Step 1 result

The nearest-neighbour audit completed on all 199 cached raw graphs.

| graph | nodes | nearest <1 um | nearest <2 um | nearest <3 um |
|---|---:|---:|---:|---:|
| raw predictions | 4,211,780 | 0 (0%) | 0 (0%) | 0 (0%) |
| sparse GT | 133,318 | 0 (0%) | 0 (0%) | 2 (0.0015%) |

## Decision

**B31 is closed at Step 1.** The registered stop rule was to stop if fewer than 1% of raw peaks had a same-frame
neighbour below 2 um. The observed fraction is exactly zero. The public detector already applies 3 um physical NMS,
so none of the proposed clustering radii (`0.5`, `1.0`, `1.5`, `2.0` um) can merge a raw pair. Running the four-radius
sweep would produce identical graphs and is intentionally skipped. Nothing is submitted to the leaderboard.

The CPU implementation was nevertheless validated by rebuilding the radius-zero path on all 199 videos: score
`0.9120275024`, adjusted edge `0.9023109032`, divisions `24/96/127`, exactly matching Friend A's saved control. It took
521 seconds on the Windows development machine and touched no images, weights, or CUDA. The runner retains a diagnostic
`--force-sweep` option, but it is not part of the registered result after this stop gate.
