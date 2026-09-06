# --- Patches for scripts/predict_unet_transformer.py: model ensembling at inference ---
# Env BIOHUB_ENSEMBLE_WEIGHTS = comma-separated extra checkpoint paths (each with config.json next to it).
# The wrapped model averages detection logits (before TTA/NMS) and edge logits across models.
from pathlib import Path


def _replace_once(src: str, old: str, new: str, label: str) -> str:
    n = src.count(old)
    if n != 1:
        raise RuntimeError(f"patch '{label}': expected exactly 1 occurrence, found {n}")
    return src.replace(old, new)


ENSEMBLE_CODE = '''
# ---- exp patch: inference-time ensemble ------------------------------------
class _MultiOut:
    """Holds per-model UNet feature maps; supports the `unet_out[:, f]` indexing used in predict_video."""
    def __init__(self, outs):
        self.outs = outs

    def __getitem__(self, key):
        return [o[key] for o in self.outs]


class EnsembleModel:
    def __init__(self, models):
        self.models = models

    def encode(self, imgs):
        outs, dets = [], None
        for m in self.models:
            u, d = m.encode(imgs)
            outs.append(u)
            dets = d if dets is None else [a + b for a, b in zip(dets, d)]
        dets = [d / len(self.models) for d in dets]
        return _MultiOut(outs), dets

    def _index_features(self, feat_maps, coords, mask):
        return [m._index_features(fm, coords, mask) for m, fm in zip(self.models, feat_maps)]

    def predict_edges(self, fs, ft, *args):
        logits = None
        for m, a, b in zip(self.models, fs, ft):
            l = m.predict_edges(a, b, *args)
            logits = l if logits is None else logits + l
        return logits / len(self.models)

    def eval(self):
        for m in self.models:
            m.eval()
        return self


def _maybe_ensemble(model, device):
    import os as _os
    extra = [p for p in _os.environ.get("BIOHUB_ENSEMBLE_WEIGHTS", "").split(",") if p.strip()]
    if not extra:
        return model
    models = [model]
    for p in extra:
        m, _, _ = load_model(Path(p), device)
        models.append(m)
    print(f"ENSEMBLE: {len(models)} models (averaging detection + edge logits): {extra}", flush=True)
    return EnsembleModel(models)


'''

PATCHES = [
    (
        "def predict(\n",
        ENSEMBLE_CODE + "def predict(\n",
        "ensemble class",
    ),
    (
        "    model, window_size, downsample = load_model(weights_path, device)\n",
        "    model, window_size, downsample = load_model(weights_path, device)\n    model = _maybe_ensemble(model, device)\n",
        "ensemble wrap",
    ),
]


def apply_predict_patches(script_path: Path) -> None:
    script_path = Path(script_path)
    src = script_path.read_text(encoding="utf-8")
    for old, new, label in PATCHES:
        src = _replace_once(src, old, new, label)
    script_path.write_text(src, encoding="utf-8")
    print(f"applied {len(PATCHES)} predict patches to {script_path}")
