# r1 research clip-boundary-frames notes (started)
## Code facts (tools/repo/scripts/predict_unet_transformer.py, temporal_unet.py)
- window_size=2 (all weights config.json). Windows [ws, ws+1], stride 1, NO padding. seen_frames dedup: frame 0 detected in slot0 of [0,1]; frames 1..T-1 in slot1 of [t-1,t].
- TemporalUNet3D temporal mixing = _TemporalAttention (per-voxel MHA over T), NO positional encoding -> permutation-equivariant; slot0/slot1 identical function. Frame 0 sees frame 1 (future), others see past. No padded frames at any clip edge.
- => detector-padding part (a) of hypothesis REFUTED by code; last frames are detected exactly like interior frames.
- (resume 2) re-verified predict loop in tools/repo/scripts/predict_unet_transformer.py L348-403: stride=W-1=1, window_starts 0..T-2, no padding. exp39 notebook patches this script (dual-seed blend + retention guard) but keeps loop.
- next: check linefit ends, gap-close at t=0/T-1, parquet boundary breakdown.
