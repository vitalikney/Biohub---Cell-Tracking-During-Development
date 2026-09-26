"""MITOSE / v6 -- the PAIR network: two crops in, one logit out, and the pair
branch cannot tell its two daughters apart.

The red team's V1 is the reason this file exists: there was no v6 network, and
the v4 trainer would have opened a 552 960-byte row as two 276 480-byte rows --
the mother crop of trio r/2 and the pair crop of the odd rows, against the label
of trio r, silently. Nothing here is shared with `mh_net.py` by import: v4's
weights are frozen and deployed, and a change to its file would touch a shipped
model.

THE DESIGN, declared before it trains:

  trunk       ONE `MitosisTrunk`, the v4 encoder without its head, applied to
              BOTH crops with SHARED weights. The mother crop and the pair crop
              are the same kind of object (four frames of normalised voxels
              around a place), so one trunk learns one vocabulary and the pair
              branch does not have to relearn what a nucleus looks like.
  pooling     mean and max over the volume, as in v4 -> 8w features per crop.
  merge       plain CONCATENATION of (mother, pair), in that order and nothing
              else. ZEUS 14:4xZ, on HADES: the two representations stay
              IDENTIFIED -- the invariance this arm needs is the swap of the two
              DAUGHTERS, never the swap of mother and pair. The symmetric
              interaction terms |m - p| and m * p that this file carried until
              then are REMOVED: they are functions invariant under exchanging
              the two branches, and a head that reads them can build a feature
              that no longer knows which crop is the mother.
  scalars     the geometry travels through a small MLP, and every scalar that
              refers to "d1" or "d2" is fed as a SYMMETRIC pair (min, max) --
              never as (d1, d2), whose ordering the red team showed is an
              arbitrary candidate row index (V13 b). Feeding `pm_prob_d1` and
              `pm_prob_d2` in that order would teach the net a row index.
  output      one logit. Its sigmoid is P(this trio is the division the judge
              credits when posed).

THE INVARIANCE IS A PROPERTY OF THE FILE, not a hope: `selftest` swaps the two
daughters in BOTH the crop and the scalars and requires the logit to be equal to
the last bit.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from mh_net import ResBlock3d


class MitosisTrunk(nn.Module):
    """v4's encoder, without the head: (B, C, Z, Y, X) -> (B, 8w)."""

    def __init__(self, in_channels=4, width=32):
        super().__init__()
        w = int(width)
        self.width = w
        self.stem = nn.Sequential(
            nn.Conv3d(in_channels, w, (3, 5, 5), stride=(1, 2, 2),
                      padding=(1, 2, 2), bias=False),
            nn.InstanceNorm3d(w, affine=True), nn.SiLU(inplace=True))
        self.stage1 = nn.Sequential(ResBlock3d(w), ResBlock3d(w))
        self.down1 = nn.Sequential(
            nn.Conv3d(w, 2 * w, 3, stride=2, padding=1, bias=False),
            nn.InstanceNorm3d(2 * w, affine=True), nn.SiLU(inplace=True))
        self.stage2 = nn.Sequential(ResBlock3d(2 * w), ResBlock3d(2 * w))
        self.down2 = nn.Sequential(
            nn.Conv3d(2 * w, 4 * w, 3, stride=2, padding=1, bias=False),
            nn.InstanceNorm3d(4 * w, affine=True), nn.SiLU(inplace=True))
        self.stage3 = nn.Sequential(ResBlock3d(4 * w), ResBlock3d(4 * w))

    def forward(self, x):
        h = self.stage3(self.down2(self.stage2(self.down1(self.stage1(
            self.stem(x))))))
        return torch.cat([h.mean(dim=(2, 3, 4)), h.amax(dim=(2, 3, 4))], dim=1)


class PairHead(nn.Module):
    """(B, 2, C, Z, Y, X) crops + (B, S) scalars -> (B,) logit."""

    N_SCALARS = 11
    """(min, max) of the two mother-daughter distances; (min, max) of the two
    probmat edge probabilities; (min, max) of |dz| to the two daughters; the
    sister separation; the symmetry; the cosine at the mother; the mother's own
    head logit; and the DIVERGENCE, which is the deployed graft's own gate
    quantity and arrives with FRONT A's dump. Every d1/d2 pair enters as a
    SYMMETRIC (min, max), never in the table's arbitrary order."""

    def __init__(self, in_channels=4, width=32, n_scalars=None, dropout=0.1):
        super().__init__()
        w = int(width)
        self.trunk = MitosisTrunk(in_channels=in_channels, width=width)
        s = int(self.N_SCALARS if n_scalars is None else n_scalars)
        self.n_scalars = s
        self.scalars = (nn.Sequential(
            nn.Linear(s, 4 * w), nn.SiLU(inplace=True),
            nn.Linear(4 * w, 2 * w), nn.SiLU(inplace=True)) if s > 0 else None)
        merged = 8 * w * 2 + (2 * w if s > 0 else 0)
        self.head = nn.Sequential(
            nn.Dropout(dropout), nn.Linear(merged, 4 * w),
            nn.SiLU(inplace=True), nn.Dropout(dropout), nn.Linear(4 * w, 1))

    def forward(self, crops, scalars=None):
        m = self.trunk(crops[:, 0])
        p = self.trunk(crops[:, 1])
        feats = [m, p]
        if self.scalars is not None:
            if scalars is None:
                raise ValueError("this head was built with %d scalars and got "
                                 "none" % self.n_scalars)
            feats.append(self.scalars(scalars))
        return self.head(torch.cat(feats, dim=1)).squeeze(1)


def symmetric_scalars(row):
    """The scalar vector, built so that swapping d1 and d2 cannot change it.

    `row` is a mapping with the trio table's own names. Missing keys are 0,0 and
    the caller publishes which were missing -- a silent zero is a measurement
    this file refuses to hide."""
    def g(k):
        v = row.get(k)
        return 0.0 if v is None else float(v)
    d1, d2 = g("dist_m_d1_um"), g("dist_m_d2_um")
    p1, p2 = g("pm_prob_d1"), g("pm_prob_d2")
    z1, z2 = abs(g("dz_m_d1")), abs(g("dz_m_d2"))
    return [min(d1, d2), max(d1, d2), min(p1, p2), max(p1, p2),
            min(z1, z2), max(z1, z2), g("sister_sep_um"), g("symmetry"),
            g("cos_angle_at_mother"), g("mother_v2_logit"), g("divergence")]


def count_parameters(model):
    return int(sum(p.numel() for p in model.parameters() if p.requires_grad))
