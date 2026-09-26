"""MITOSE / mitosis head -- the network.

The mandate allows two designs: "the J0 two-trunk design if it runs, else a
compact 3D ResNet over the three frames stacked as channels". The J0 design is
a DENSE HEATMAP decoder (`reseau.py` + `cibles.py` + `decodeur.py` + a loss
interface that couples H_m, O and S under one mask) -- it answers "where are the
mothers in this image", not "does THIS candidate divide". The deliverable of
this run is a per-candidate probability for the LIAGE solver, so this file takes
the second option and says so: a compact anisotropic 3D ResNet whose input is
the four frames {t-2, t-1, t, t+1} stacked as channels.

WHY ANISOTROPIC. A grid voxel is 1,625 um in z and 0,8125 um in xy, so a
kernel that is symmetric in voxels is twice as wide in xy as in z in MICRONS.
The stem therefore strides only in xy; z is reduced later, once the physical
extents match.

The output is ONE logit. `P(division)` is its sigmoid. Nothing in this file
reads a path, a film or a label.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class ResBlock3d(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.a = nn.Conv3d(channels, channels, 3, padding=1, bias=False)
        self.na = nn.InstanceNorm3d(channels, affine=True)
        self.b = nn.Conv3d(channels, channels, 3, padding=1, bias=False)
        self.nb = nn.InstanceNorm3d(channels, affine=True)
        self.act = nn.SiLU(inplace=True)

    def forward(self, x):
        h = self.act(self.na(self.a(x)))
        h = self.nb(self.b(h))
        return self.act(x + h)


class MitosisHead(nn.Module):
    """Input (B, C_in, 11, 40, 40) -> (B,) logit."""

    def __init__(self, in_channels=4, width=32, dropout=0.1):
        super().__init__()
        w = int(width)
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
        self.head = nn.Sequential(
            nn.Dropout(dropout), nn.Linear(8 * w, 4 * w),
            nn.SiLU(inplace=True), nn.Dropout(dropout), nn.Linear(4 * w, 1))

    def forward(self, x):
        h = self.stage3(self.down2(self.stage2(self.down1(self.stage1(
            self.stem(x))))))
        avg = h.mean(dim=(2, 3, 4))
        mx = h.amax(dim=(2, 3, 4))
        return self.head(torch.cat([avg, mx], dim=1)).squeeze(1)


def count_parameters(model):
    return int(sum(p.numel() for p in model.parameters() if p.requires_grad))
