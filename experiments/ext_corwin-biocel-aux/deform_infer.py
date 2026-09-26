"""ENG/DEFORM -- the SHIPPABLE object, self-contained, for a Kaggle kernel cell.

One file, no import from this lane's other modules, no network, no ground truth. It takes a film's
zarr and a list of node positions in FULL-RES integer indices and returns, for each node, the
predicted displacement in judge-microns; optionally the local divergence of the field beside it.

  from deform_infer import DeformField
  F = DeformField("/kaggle/input/<ds>/deform_S4_060000_fp16.pt", device="cuda", iters=3)
  u_um, div = F.film("/kaggle/input/.../<film>.zarr", t_array, zyx_array)

UNITS, ONCE. The network runs on the 2x laterally MEAN-POOLED volume (64, 128, 128), voxel
(1,625 ; 0,8125 ; 0,8125) um. A full-res index y maps to lattice coordinate (y - 0,5)/2; z is
unchanged. u is returned in MICRONS on (z, y, x).

DIRECTION, ONCE. u(p) is the displacement of the material at p in frame t towards frame t+1:
a node n at t with child m at t+1 should have u(n) ~ (m - n) * (1,625 ; 0,40625 ; 0,40625).

CASCADE. `iters=k` re-runs the same weights on the already-warped pair and composes exactly,
u_new(p) = du(p) + u_old(p + du(p)). It is GT-free -- the weights applied to their own output --
and it is what recovers the displacement MAGNITUDE (0,4624 of the truth at k=1, 0,6593 at k=3).
`iters=1` is byte-identical to the uncascaded path (gate: max_abs_diff = 0.0 um).
"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

VOX_UM = (1.625, 0.8125, 0.8125)          # the POOLED lattice
FULL_UM = (1.625, 0.40625, 0.40625)       # the raw array and the GT indices
CLAMP_HIGH = 4.0


def _blk(cin, cout, stride=1):
    return nn.Sequential(nn.Conv3d(cin, cout, 3, stride=stride, padding=1),
                         nn.LeakyReLU(0.2, inplace=True))


class DeformNet(nn.Module):
    ENC = (16, 32, 32, 32)
    DEC = (32, 32, 32, 16)

    def __init__(self, in_ch=2):
        super().__init__()
        self.inc = _blk(in_ch, self.ENC[0])
        self.down = nn.ModuleList()
        c = self.ENC[0]
        for co in self.ENC:
            self.down.append(nn.Sequential(_blk(c, co, stride=2), _blk(co, co)))
            c = co
        self.up = nn.ModuleList()
        skips = [self.ENC[0]] + list(self.ENC[:-1])
        for co, sk in zip(self.DEC, reversed(skips)):
            self.up.append(nn.Sequential(_blk(c + sk, co), _blk(co, co)))
            c = co
        self.tail = _blk(c, 16)
        self.flow = nn.Conv3d(16, 3, 3, padding=1)

    def forward(self, x):
        h = self.inc(x)
        skips = [h]
        for d in self.down:
            h = d(h)
            skips.append(h)
        skips.pop()
        for u_, s in zip(self.up, reversed(skips)):
            h = F.interpolate(h, size=s.shape[2:], mode="trilinear", align_corners=False)
            h = u_(torch.cat([h, s], dim=1))
        return self.flow(self.tail(h))


def _identity_grid(shape, device, dtype):
    d, h, w = shape
    g = torch.stack(torch.meshgrid(torch.arange(d, device=device, dtype=dtype),
                                   torch.arange(h, device=device, dtype=dtype),
                                   torch.arange(w, device=device, dtype=dtype),
                                   indexing="ij"), dim=0)
    return g.unsqueeze(0)


def _sample(vol, pts_or_field, grid=None):
    """grid_sample's last grid axis is (x, y, z), the REVERSE of the tensor's spatial order.
    That reversal happens here and nowhere else."""
    n, _, d, h, w = vol.shape
    size = torch.tensor([d - 1, h - 1, w - 1], device=vol.device, dtype=vol.dtype)
    p = pts_or_field if grid is None else grid + pts_or_field
    if p.dim() == 5:                                    # a field: (N,3,D,H,W)
        p = 2.0 * p / size.view(1, 3, 1, 1, 1) - 1.0
        p = torch.flip(p.permute(0, 2, 3, 4, 1), dims=[-1])
    else:                                               # points: (P,3)
        p = 2.0 * p.to(vol.dtype) / size.view(1, 3) - 1.0
        p = torch.flip(p, dims=[-1]).view(1, -1, 1, 1, 3)
    return F.grid_sample(vol, p, mode="bilinear", padding_mode="border", align_corners=True)


class DeformField:
    def __init__(self, weights_path, device="cuda", iters=3, batch=8):
        self.dev = torch.device(device)
        self.net = DeformNet(2).to(self.dev).eval()
        sd = torch.load(weights_path, map_location=self.dev)
        sd = sd.get("model", sd)
        self.net.load_state_dict({k: v.float() for k, v in sd.items()})
        self.iters = int(iters)
        self.batch = int(batch)
        self.vox = np.array(VOX_UM)

    @staticmethod
    def _frame(arr, t, q_low, q_high):
        a = np.asarray(arr[t]).astype(np.float32)
        d, h, w = a.shape
        a = a.reshape(d, h // 2, 2, w // 2, 2).mean(axis=(2, 4))
        return np.clip((a - q_low) / (q_high - q_low + 1e-6), 0.0, CLAMP_HIGH)

    def _field(self, x):
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16,
                                             enabled=self.dev.type == "cuda"):
            u = self.net(x)
        u = u.float()
        if self.iters > 1:
            fixed, moving = x[:, 0:1].float(), x[:, 1:2].float()
            grid = _identity_grid(tuple(u.shape[2:]), self.dev, torch.float32)
            for _ in range(self.iters - 1):
                warped = _sample(moving, u, grid)
                with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16,
                                                     enabled=self.dev.type == "cuda"):
                    du = self.net(torch.cat([fixed, warped], dim=1))
                du = du.float()
                u = du + _sample(u, du, grid)          # u_new(p) = du(p) + u_old(p + du(p))
        return u

    def film(self, zarr_path, t_of_node, zyx_of_node, want_divergence=False):
        """-> u_um (N,3) in judge-microns on (z,y,x); div (N,) or None. NaN where t has no t+1."""
        import zarr
        g = zarr.open_group(str(zarr_path), mode="r")
        q = g.attrs["image_statistics"]["quantiles"]
        q_low, q_high = float(q["0.001"]), float(q["0.999"])
        arr = g["0"]
        nt = int(arr.shape[0])
        t_of_node = np.asarray(t_of_node, np.int64)
        lat = np.asarray(zyx_of_node, np.float64).copy()
        lat[:, 1] = (lat[:, 1] - 0.5) / 2.0
        lat[:, 2] = (lat[:, 2] - 0.5) / 2.0
        u_um = np.full((len(lat), 3), np.nan, np.float64)
        div = np.full(len(lat), np.nan, np.float64) if want_divergence else None
        frames = [self._frame(arr, t, q_low, q_high) for t in range(nt)]
        for s in range(0, nt - 1, self.batch):
            ts = list(range(s, min(s + self.batch, nt - 1)))
            x = torch.from_numpy(np.stack([np.stack([frames[t], frames[t + 1]])
                                           for t in ts])).to(self.dev)
            u = self._field(x)
            if want_divergence:
                p = F.pad(u, (1, 1, 1, 1, 1, 1), mode="replicate")
                dv = ((p[:, 0:1, 2:, 1:-1, 1:-1] - p[:, 0:1, :-2, 1:-1, 1:-1])
                      + (p[:, 1:2, 1:-1, 2:, 1:-1] - p[:, 1:2, 1:-1, :-2, 1:-1])
                      + (p[:, 2:3, 1:-1, 1:-1, 2:] - p[:, 2:3, 1:-1, 1:-1, :-2])) * 0.5
            for bi, t in enumerate(ts):
                m = t_of_node == t
                if not m.any():
                    continue
                pts = torch.from_numpy(lat[m]).to(self.dev)
                u_um[m] = _sample(u[bi:bi + 1], pts).view(3, -1).t().cpu().numpy() * self.vox
                if want_divergence:
                    div[m] = _sample(dv[bi:bi + 1].repeat(1, 3, 1, 1, 1),
                                     pts).view(3, -1)[0].cpu().numpy()
        return u_um, div


def hybrid(u_model_um, u_flow_um, threshold_um=2.0):
    """The pre-registered combination: the K = 12 tissue flow takes the edge wherever it says the
    tissue is moving more than `threshold_um`, the image field takes it everywhere else.
    Both inputs are in judge-microns on (z, y, x). NaN rows of the model fall back to the flow."""
    u_model_um = np.asarray(u_model_um, np.float64)
    u_flow_um = np.asarray(u_flow_um, np.float64)
    big = np.linalg.norm(u_flow_um, axis=1, keepdims=True) > threshold_um
    bad = ~np.isfinite(u_model_um).all(axis=1, keepdims=True)
    return np.where(big | bad, u_flow_um, u_model_um)
