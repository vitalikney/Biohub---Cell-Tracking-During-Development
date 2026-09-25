# Step 0 (T7): runtime arithmetic on the hidden test — 2026-09-25 ~16:40 UTC

Inputs (dummy logs, `*_timing.txt`; latencies from `experiments/lb_poll/poll.log`):
- x138 dummy (exp56): shards launched at 257.7 s, "Prediction completed in 10.59 min" at 892.8 s (4 clips, 2 GPU shards
  -> ~318 s per clip per shard), repair 46.8 + 59.3 + 11.1 + 109.3 = 226.5 s (56.6 s/clip), kernel end 1111.7 s.
- exp57b dummy: same GPU phase; repair 79.9 + 116.2 + 19.4 + 275.9 = 491.4 s (122.9 s/clip; the insertion adds ~66 s/clip).
- Latencies: L34 (x138) in (6.29, 6.46] h; L35 (exp57b) in (6.72, 7.73] h (five empty CLI polls 15:26-16:06Z).

Model (x138 repairs after the whole GPU phase, one clip after another, alphabetical):
T(N) ~= 300 s + (N/2) * 318 s + N * r,   r = 56.6 s (x138), 122.9 s (exp57b).

Upper bounds on the number of hidden clips N (runtime <= latency, dummy per-clip speed):
- from L34 <= 23,256 s: N <= 106;
- from L35 <= 27,828 s: N <= 97.
- (L35 - L34) / 66 s gives N in (14, 78) if both queues were similar — wide, only a sanity check.
Clip sizes differ from the 4 dummies, so these are approximate. The Data tab's "about the size of train" (~199) is
inconsistent with these latencies at dummy speed: either N is ~100 or the hidden hardware is faster.

IMPORTANT: the hidden rerun processes public AND private clips in ONE run; L34/L35 already cover the private part.
There is no separate "denser private run".

Forecasts (N <= 97-106):
- x138 (#34): <= 6.46 h measured; below its 7.5 h REPAIR_DEADLINE -> not degraded (R1).
- exp57b (#35): <= 7.73 h measured. x138's REPAIR_DEADLINE_S = 27,000 s (7.5 h) may have degraded the LAST few clips
  if the true runtime was above ~7.5 h (unprovable with the empty polls) -> #35 is not a finals candidate (R5).
- K2 (exp58 = #35 + safetail + lowrefine): ~= #35 runtime + lowrefine (a few s/clip) -> ~7.8 h at most. Its repair
  deadline is 34,200 s (9.5 h, not reached) and the insertion gate 28,800 s (8.0 h): the last clip's insertion starts
  before ~7.8 h, margin >= ~0.2 h in the worst case, several hours in the likely case.

Verdicts:
- R5 (admission): K2 is admissible once its own latency is observed <= 9.5 h (poll every 10 min).
- R6 (N1 parrepair): L34 <= 8.0 h, #35 no error, L35 <= 8.5 h, F1 forecast ~7.8 h < 9.0 h -> NOT triggered.
