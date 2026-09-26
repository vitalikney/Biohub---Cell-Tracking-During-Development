"""ENG/KER10 -- SUBVOX : sub-voxel refinement of a detected peak.

ZEUS 14:4xZ. The vendor's secondary earns +0,006 public on PLACEMENT (3 um
0,68 against our 0,61 ; d_p90 4,2 against 5,1) and the linker links by
distance, so half a lattice step of placement is worth more edges than any
knob. The decoder currently returns the INTEGER index of the local maximum in
the downsampled grid: laterally that grid is 4 full-resolution units, i.e.
1,625 judge-um, and the true centre of a nucleus almost never sits on it.

THE OPERATOR. For each peak, the intensity-weighted centroid of the heatmap
over the (2r+1)^3 neighbourhood of the peak:

    c = sum_k w_k * p_k / sum_k w_k          w = the heatmap, p = the index

with r = 1 (3x3x3) or r = 2 (5x5x5). The offset c - peak is returned in
DOWNSAMPLED voxels; the caller multiplies by the downsample (1, 4, 4) and
rounds, so the submission stays integer and the judge keeps scaling integers.

THREE THINGS THAT ARE NOT DECORATION.

  * THE WEIGHT IS THE PROBABILITY, NOT THE LOGIT. A centroid needs a
    non-negative weight; logits are signed and a single negative neighbour
    would throw the centroid outside the neighbourhood, or divide by a
    near-zero sum. `sigmoid` is applied by the caller and asserted here.

  * OUT-OF-BOUNDS NEIGHBOURS ARE MASKED, NOT CLAMPED. Clamping an index at the
    volume edge duplicates the border voxel into the sum and pulls every edge
    peak outward. The mask makes the centroid of a border peak the centroid of
    the neighbours it actually has.

  * THE OFFSET IS BOUNDED BY r BY CONSTRUCTION -- a weighted mean of indices
    within +-r of the peak cannot leave that box -- so the node COUNT cannot
    change and no peak can jump into another's cell. The caller still asserts
    the count per film rather than trusting this paragraph.
"""
from __future__ import annotations

import torch


def offsets(prob_volume: torch.Tensor, peaks: torch.Tensor, r: int = 1) -> torch.Tensor:
    """(N, 3) sub-voxel offsets in DOWNSAMPLED voxels, one per peak.

    prob_volume : (Z, Y, X) heatmap in [0, 1] -- the caller's sigmoid.
    peaks       : (N, 3) int64 indices into that volume.
    """
    if peaks.numel() == 0:
        return peaks.new_zeros((0, 3), dtype=torch.float32)
    if prob_volume.dim() != 3:
        raise ValueError("SUBVOX: the volume must be (Z, Y, X), got %r"
                         % (tuple(prob_volume.shape),))
    v = prob_volume.float()
    if bool((v < 0).any()) or bool((v > 1).any()):
        raise ValueError("SUBVOX: the weight must be a probability in [0, 1]; "
                         "the caller passed a volume ranging %.4f..%.4f"
                         % (float(v.min()), float(v.max())))
    dev = v.device
    S = v.shape
    d = torch.arange(-r, r + 1, device=dev, dtype=torch.long)
    DZ, DY, DX = torch.meshgrid(d, d, d, indexing="ij")
    DZ, DY, DX = DZ.reshape(-1), DY.reshape(-1), DX.reshape(-1)

    p = peaks.to(dev).long()
    Z = p[:, 0:1] + DZ[None, :]
    Y = p[:, 1:2] + DY[None, :]
    X = p[:, 2:3] + DX[None, :]
    ok = ((Z >= 0) & (Z < S[0]) & (Y >= 0) & (Y < S[1]) & (X >= 0) & (X < S[2]))
    w = v[Z.clamp(0, S[0] - 1), Y.clamp(0, S[1] - 1), X.clamp(0, S[2] - 1)]
    w = w * ok.to(w.dtype)
    den = w.sum(1).clamp_min(1e-8)
    cz = (w * Z.float()).sum(1) / den
    cy = (w * Y.float()).sum(1) / den
    cx = (w * X.float()).sum(1) / den
    off = torch.stack([cz, cy, cx], dim=1) - p.float()
    return off.clamp(-float(r), float(r))
