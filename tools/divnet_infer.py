"""DivNet 3D mitosis classifier - inference code lifted VERBATIM from the public notebook
haideptry/biohub-sota-0-948-density-adaptive-2xt4-22m (2026-09-17), which loads the public dataset
giorgosi/biohub-divnet-v2 (ARTIFACT_MANIFEST.json + best_overall.pt, 5.6 MB).

What the model is (from the manifest): per-node division-event detector, 3D UNet-GAP, 5 input channels =
image at lags -1,0,+1,+2 around the split frame + a gaussian centre marker, crop 16 x 32 x 32 after the
official xy pooling by 4, normalisation lo/hi percentile 50/99.5 clipped to [-0.5, 6], voxel scale
(1.625, 0.40625, 0.40625), 4 folds by movie over all 199 videos and the 151 GT divisions; ensemble = mean
sigmoid over folds (only best_overall.pt ships in v2). Reported OOF: AUC 0.887 (single 0.845), AUC vs
confuser forks 0.921, hits@k 0.28/0.40/0.46/0.57/0.66 for k=1/2/3/5/10, simulated official div_J 0.214 at
top-1 and 0.226 at top-2 (ours: 0.11), calibration at p=0.5: TPR 0.72, FPR vs confusers 0.03.

The notebook uses it only as a soft VETO on safe-division candidates (p < 0.5 rejected). The manifest's own
simulation says the value is in RANKING candidates by p (top-k per parent), i.e. exactly B20.

Nothing here is executed by our pipeline yet; it is vendored so friend B can score his B20 candidates with
it (needs the 4 frames around each candidate: read_test_frame(dataset, t, frame_cache) in the notebook).
"""
import numpy as np
import torch
import torch.nn as nn
from pathlib import Path

class _DivNetConvBlock(torch.nn.Module):
    def __init__(self, in_c: int, out_c: int):
        super().__init__()
        self.conv = torch.nn.Sequential(
            torch.nn.Conv3d(in_c, out_c, kernel_size=3, padding=1),
            torch.nn.BatchNorm3d(out_c),
            torch.nn.ReLU(inplace=True),
            torch.nn.Conv3d(out_c, out_c, kernel_size=3, padding=1),
            torch.nn.BatchNorm3d(out_c),
            torch.nn.ReLU(inplace=True),
        )
    def forward(self, x):
        return self.conv(x)

class DivNetMitosisClassifier(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.b1 = _DivNetConvBlock(1, 16)
        self.p1 = torch.nn.MaxPool3d((1, 2, 2))
        self.b2 = _DivNetConvBlock(16, 32)
        self.p2 = torch.nn.MaxPool3d((2, 2, 2))
        self.b3 = _DivNetConvBlock(32, 64)
        self.gap = torch.nn.AdaptiveAvgPool3d((1, 1, 1))
        self.fc = torch.nn.Sequential(
            torch.nn.Linear(64, 32),
            torch.nn.ReLU(inplace=True),
            torch.nn.Linear(32, 1),
        )
    def forward(self, x):
        x = self.p1(self.b1(x))
        x = self.p2(self.b2(x))
        x = self.gap(self.b3(x))
        x = torch.flatten(x, 1)
        return self.fc(x)


def load_divnet_mitosis_model() -> dict[str, object] | None:
    if not globals().get("DIVNET_VERIFY", True):
        print("DivNet mitosis gate disabled by configuration.")
        return None
    if torch is None:
        print("DivNet mitosis gate skipped: torch is unavailable.")
        return None
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Direct I/O check first (avoid expensive FUSE glob)
    candidates = [
        Path("/kaggle/input/biohub-divnet-v2/best_overall.pt"),
        Path("/kaggle/input/datasets/giorgosi/biohub-divnet-v2/best_overall.pt"),
        Path("/kaggle/input/biohub-divnet-v2/model.pt"),
        Path("/kaggle/input/biohub-divnet-v2/best.pt"),
    ]
    for ckpt_path in candidates:
        if ckpt_path.exists():
            try:
                print(f"Loading DivNet checkpoint from direct path: {ckpt_path}")
                ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
                state = ckpt.get("model_state", ckpt) if isinstance(ckpt, dict) else ckpt
                model = DivNetMitosisClassifier()
                model.load_state_dict(state, strict=False)
                model.to(device)
                model.eval()
                print(f"[OK] DivNet loaded successfully from {ckpt_path}")
                return {"model": model, "device": device, "torch": torch}
            except Exception as exc:
                print(f"Failed loading DivNet checkpoint {ckpt_path}: {exc}")
    print("DivNet mitosis checkpoint not found. Operating in geometric baseline mode.")
    return None

DIVNET_BUNDLE = load_divnet_mitosis_model()


def divnet_score_division(
    dataset: str,
    t: int,
    parent_node: dict[str, object],
    daughter1: dict[str, object],
    daughter2: dict[str, object],
    divnet_bundle: dict[str, object] | None,
    frame_cache: dict[int, np.ndarray],
    z_pad: int = 8,
    xy_pad: int = 16,
) -> float | None:
    if divnet_bundle is None or dataset is None:
        return None
    model = divnet_bundle["model"]
    device = divnet_bundle["device"]
    t_mod = divnet_bundle["torch"]
    cz = int(round(float(parent_node["z"])))
    cy = int(round(float(parent_node["y"])))
    cx = int(round(float(parent_node["x"])))
    try:
        frames = [read_test_frame(dataset, max(0, t + dt), frame_cache) for dt in range(4)]
        vol = np.stack(frames, axis=0) # (4, Z, Y, X)
        Z, Y, X = vol.shape[1], vol.shape[2], vol.shape[3]
        z0, z1 = max(0, cz - z_pad), min(Z, cz + z_pad)
        y0, y1 = max(0, cy - xy_pad), min(Y, cy + xy_pad)
        x0, x1 = max(0, cx - xy_pad), min(X, cx + xy_pad)
        crop = vol[:, z0:z1, y0:y1, x0:x1]
        padded = np.zeros((4, 2 * z_pad, 2 * xy_pad, 2 * xy_pad), dtype=np.float32)
        dz0 = z_pad - (cz - z0)
        dy0 = xy_pad - (cy - y0)
        dx0 = xy_pad - (cx - x0)
        padded[:, dz0:dz0 + (z1 - z0), dy0:dy0 + (y1 - y0), dx0:dx0 + (x1 - x0)] = crop
        mean_val = float(np.mean(padded))
        std_val = float(np.std(padded)) + 1e-6
        padded = (padded - mean_val) / std_val
        tensor = t_mod.from_numpy(padded).unsqueeze(0).unsqueeze(0).to(device=device, dtype=t_mod.float32)
        with t_mod.inference_mode():
            logit = model(tensor)
            prob = float(t_mod.sigmoid(logit).squeeze().cpu().item())
        return prob
    except Exception as e:
        return None

