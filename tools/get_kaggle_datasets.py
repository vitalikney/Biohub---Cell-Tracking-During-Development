"""Fetch the Kaggle datasets our kernels depend on into external/<owner>__<name>/ (git-ignored).

Pointer-in-git, bytes-fetched-once: the slugs below are the manifest, the bytes live on Kaggle
and in each teammate's local cache. This is what DVC would do with a remote; we have no remote,
and Kaggle already serves these files, so the manifest is the whole mechanism.

Usage:
    python tools/get_kaggle_datasets.py            # fetch everything missing
    python tools/get_kaggle_datasets.py --only support   # substring filter on the slug
    python tools/get_kaggle_datasets.py --force    # re-download even if the folder exists

Needs the Kaggle API configured (KAGGLE_USERNAME/KAGGLE_KEY or ~/.kaggle/kaggle.json).
Version pinning: Kaggle downloads the latest version; the version we validated is noted per entry.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "external"

# slug, note (what it is, which of our kernels use it, version validated)
DATASETS = [
    ("pilkwang/biohub-tracking-support-pack-50ep-v1",
     "pilkwang support pack: primary TemporalUNet3D weights (split_0), tracking_repo code, DeepCenter manifest; every probe kernel; v1"),
    ("pilkwang/biohub-temporal-unet3d-seed314159-v1",
     "secondary detector seed314159 (the dual-seed blend); every probe kernel; v1"),
    ("pilkwang/biohub-deepcenter-unet3d-center-prior-v1",
     "DeepCenter full_frame_center/best.pt veto model; every probe kernel since exp29; v1"),
    ("giorgosi/biohub-divnet-v2",
     "public DivNet 3D mitosis classifier (best_overall.pt 5.6 MB + ARTIFACT_MANIFEST.json): per-node division-event detector trained on all 199 videos, OOF AUC 0.887; loader/scorer code in tools/divnet_infer.py; for B20"),
    ("vitaliineibauer/biohub-ft-weights",
     "team weights (exp03B, exp08, exp23, soup03B_50, friend_a_*); ALSO fully in git under weights_dataset/, fetch only if you want the Kaggle copy"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="substring filter on the dataset slug")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    DEST.mkdir(exist_ok=True)
    for slug, note in DATASETS:
        if a.only and a.only not in slug:
            continue
        out = DEST / slug.replace("/", "__")
        if out.exists() and any(out.iterdir()) and not a.force:
            print("present  ", slug, "->", out.relative_to(ROOT))
            continue
        print("fetching ", slug, "|", note, flush=True)
        out.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, "-m", "kaggle", "datasets", "download", "-d", slug, "-p", str(out), "--unzip"]
        r = subprocess.run(cmd)
        if r.returncode != 0:
            print("FAILED   ", slug, "(exit", r.returncode, ")")
            continue
        for z in out.glob("*.zip"):
            z.unlink()
        n = sum(1 for p in out.rglob("*") if p.is_file())
        mb = sum(p.stat().st_size for p in out.rglob("*") if p.is_file()) / 1e6
        print("done     ", slug, "%d files, %.0f MB" % (n, mb))


if __name__ == "__main__":
    main()
