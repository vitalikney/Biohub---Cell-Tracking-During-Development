"""Bundle the LOEO-44b6 videos that the per-file competition endpoint would not deliver.

Kaggle throttles the per-file competition download (HTTP 429 with an escalating Retry-After, 0.1 MB/s by the
end), so instead this private CPU kernel copies the still-missing videos from the competition mount and writes
ONE zip to its output, which downloads through the kernel-output endpoint in a single request.
Private kernel, own account, data stays inside the team - allowed per TEAM.md.
"""
import shutil, zipfile, os, time
from pathlib import Path

STEMS = "44b6_9be80b04 44b6_a21120c2 44b6_c50204e0 44b6_d2f34f90 44b6_d5e7d891 44b6_e28840c6".split()
CANDIDATES = [Path("/kaggle/input/competitions/biohub-cell-tracking-during-development/train"),
              Path("/kaggle/input/biohub-cell-tracking-during-development/train")]
train = next((p for p in CANDIDATES if p.exists()), None)
if train is None:
    raise SystemExit("competition train dir not found: " + str(CANDIDATES))
out = Path("/kaggle/working/loeo44b6_missing.zip")
t0 = time.time(); n_files = 0; n_bytes = 0
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as zf:  # chunks are already blosc-compressed
    for stem in STEMS:
        for suffix in (".zarr", ".geff"):
            src = train / (stem + suffix)
            if not src.exists():
                raise SystemExit("missing on the mount: " + str(src))
            for p in sorted(src.rglob("*")):
                if p.is_file():
                    zf.write(p, arcname=str(Path("train") / p.relative_to(train)))
                    n_files += 1; n_bytes += p.stat().st_size
        print(stem, "done", flush=True)
print(f"{len(STEMS)} videos, {n_files} files, {n_bytes/1e9:.2f} GB -> {out} ({out.stat().st_size/1e9:.2f} GB) in {time.time()-t0:.0f}s")
