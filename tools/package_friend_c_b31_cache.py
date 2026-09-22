"""Build the compact, image-free B31/B33/B35 cache package for Friend C.

The archive contains only raw GEFFs, DeepCenter node scores, post-gap
checkpoints, DivNet parent scores, and GT GEFFs. Competition image Zarrs,
weights, and prediction outputs are never included.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import zipfile
from pathlib import Path


def geff_stems(path: Path) -> set[str]:
    return {item.stem for item in path.glob("*.geff") if item.is_dir()}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def add_tree(archive: zipfile.ZipFile, source: Path, destination: Path) -> int:
    count = 0
    for path in sorted(source.rglob("*")):
        if path.is_file():
            archive.write(path, (destination / path.relative_to(source)).as_posix())
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-root", required=True, help="directory containing <tag>/{raw,dc,ckpt,divnet}")
    parser.add_argument("--tag", default="friend_a_b20_exp29")
    parser.add_argument("--data-dir", required=True, help="train directory containing <stem>.geff")
    parser.add_argument("--output", required=True, help="destination .zip")
    parser.add_argument("--expected-videos", type=int, default=199)
    args = parser.parse_args()

    cache_root = Path(args.cache_root).resolve()
    cache = cache_root if (cache_root / "ckpt").is_dir() else cache_root / args.tag
    data_dir = Path(args.data_dir).resolve()
    output = Path(args.output).resolve()
    sets = {
        "raw": geff_stems(cache / "raw"),
        "dc": {path.stem for path in (cache / "dc").glob("*.npz")},
        "ckpt": {path.stem for path in (cache / "ckpt").glob("*.npz")},
        "divnet": {path.stem for path in (cache / "divnet").glob("*.npz")},
        "gt": geff_stems(data_dir),
    }
    stems = sets["ckpt"]
    if args.expected_videos and len(stems) != args.expected_videos:
        raise RuntimeError(f"Expected {args.expected_videos} checkpoints, found {len(stems)}")
    for name, values in sets.items():
        missing = stems - values
        if missing:
            raise RuntimeError(f"{name} misses {len(missing)} stems: {sorted(missing)[:5]}")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    manifest = {
        "format": "biohub-friend-c-b31-cache-v1",
        "created_unix": time.time(),
        "tag": args.tag,
        "videos": len(stems),
        "stems": sorted(stems),
        "contents": {
            "raw": "raw detector/linker GEFFs with peak_prob",
            "dc": "DeepCenter score per raw node_id",
            "ckpt": "post-gap checkpoint before divisions/final tail",
            "divnet": "DivNet probability per eligible parent node_id",
            "train": "GT GEFF only; no image Zarrs",
        },
    }
    file_count = 0
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
        file_count += 1
        for name in ("raw", "dc", "ckpt", "divnet"):
            file_count += add_tree(archive, cache / name, Path("cache") / args.tag / name)
        for stem in sorted(stems):
            file_count += add_tree(archive, data_dir / f"{stem}.geff", Path("train") / f"{stem}.geff")
    temporary.replace(output)
    digest = sha256(output)
    sidecar = output.with_suffix(output.suffix + ".sha256")
    sidecar.write_text(f"{digest}  {output.name}\n", encoding="ascii")
    print(json.dumps({
        "archive": str(output), "sha256": digest, "bytes": output.stat().st_size,
        "files": file_count, "videos": len(stems), "tag": args.tag,
    }, indent=2))


if __name__ == "__main__":
    main()
