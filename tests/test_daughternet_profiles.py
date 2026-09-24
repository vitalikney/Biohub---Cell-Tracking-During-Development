from __future__ import annotations

import numpy as np
import torch

from experiments.l2_daughternet.kdn_train import kdn_core
from tools.daughternet import build_model, fullres_config
from tools.divnet_infer import prepare_divnet_input


def _reader(_dataset: str, t: int, cache: dict) -> np.ndarray:
    value = np.arange(20 * 80 * 80, dtype=np.float32).reshape(20, 80, 80)
    return value + float(t)


def test_fullres_input_contract_and_model_shape() -> None:
    cfg = fullres_config()
    bundle = {"config": cfg, "prepared_frames": {}}
    node = {"t": 4, "z": 10, "y": 40, "x": 40}
    sample = prepare_divnet_input("dummy", 4, node, bundle, {}, _reader)
    assert sample.shape == (7, 16, 64, 64)
    assert np.isfinite(sample).all()
    model = build_model(cfg).eval()
    with torch.inference_mode():
        prediction = model(torch.from_numpy(sample[None]))
    assert tuple(prediction.shape) == (1, 3)


def test_kdn_profile_can_switch_without_drifting_l2() -> None:
    kdn_core.configure_profile({"profile": "friend_a_l5_fullres"})
    assert kdn_core.CROP == (16, 64, 64)
    assert kdn_core.IMAGE_CHANNELS == 6
    assert kdn_core.DEFAULT_CFG["input"]["image_lags"] == [-2, -1, 0, 1, 2, 3]

    kdn_core.configure_profile({"profile": "l2_divnet_contract"})
    assert kdn_core.CROP == (16, 32, 32)
    assert kdn_core.IMAGE_CHANNELS == 4
    assert kdn_core.DEFAULT_CFG["input"]["image_lags"] == [-1, 0, 1, 2]
