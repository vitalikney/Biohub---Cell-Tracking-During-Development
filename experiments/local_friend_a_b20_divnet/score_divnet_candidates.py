"""Resumable DivNet scoring for B20 candidate forks.

One probability is evaluated per candidate parent (DivNet is a parent-event
classifier); that probability is then attached to every admissible second-child
candidate for the parent. Per-video and within-video checkpoints make Ctrl-C or
``STOP_REQUESTED`` safe.
"""

from __future__ import annotations

import argparse
import gc
import os
import sys
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent.parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "experiments" / "local_friend_b_exp02_public_port"))

import divnet_infer as divnet  # noqa: E402
import pass2_rank_divisions as p2  # noqa: E402
import public_local as pl  # noqa: E402


def atomic_npz(path: Path, **arrays: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.stem + ".tmp.npz")
    np.savez_compressed(temporary, **arrays)
    # On Windows, antivirus/indexing can briefly hold the previous NPZ open.
    # Retrying keeps resumable checkpoints from turning a transient file lock
    # into a multi-hour pipeline failure.
    for attempt in range(20):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 19:
                raise
            gc.collect()
            time.sleep(min(0.05 * (attempt + 1), 1.0))


def stop_requested() -> bool:
    value = os.environ.get("BIOHUB_B20_STOP_FILE", "").strip()
    return bool(value) and Path(value).exists()


class FrameReader:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.arrays: dict[str, object] = {}

    def __call__(self, dataset: str, t: int, frame_cache: dict) -> np.ndarray:
        import zarr

        if dataset not in self.arrays:
            self.arrays[dataset] = zarr.open(str(self.data_dir / f"{dataset}.zarr" / "0"), mode="r")
        array = self.arrays[dataset]
        index = max(0, min(int(t), int(array.shape[0]) - 1))
        if index not in frame_cache:
            frame_cache[index] = np.asarray(array[index])
        return frame_cache[index]


def load_partial(path: Path) -> dict[int, float]:
    if not path.is_file():
        return {}
    # NpzFile owns an open file handle.  Closing it explicitly is required on
    # Windows before the same checkpoint path can be atomically replaced.
    with np.load(path) as payload:
        parents = np.asarray(payload["p"]).copy()
        values = np.asarray(payload["score"]).copy()
    return {int(parent): float(score) for parent, score in zip(parents, values)}


def save_partial(path: Path, scores: dict[int, float]) -> None:
    parents = np.array(sorted(scores), dtype=np.int64)
    values = np.array([scores[int(parent)] for parent in parents], dtype=np.float32)
    atomic_npz(path, p=parents, score=values)


def score_video(
    stem: str,
    cache: Path,
    output_dir: Path,
    bundle: dict[str, object],
    reader: FrameReader,
    parent_um: float,
    candidate_k: int,
    batch_size: int,
    checkpoint_every: int,
) -> Path:
    import torch

    output = output_dir / f"{stem}.npz"
    if output.is_file():
        with np.load(output) as existing:
            if {"p", "score"} <= set(existing.files):
                print(f"{stem}: DivNet cache present ({len(existing['score'])} parents)", flush=True)
                return output

    nodes, edges, dcs, peak = p2.load_video(cache, stem)
    candidates, _, _ = p2.candidates(nodes, edges, dcs, peak, parent_um, candidate_k, "steal")
    representatives: dict[int, tuple[int, int, int]] = {}
    for parent, child, candidate, t, _ in candidates:
        representatives.setdefault(int(parent), (int(child), int(candidate), int(t)))

    partial = output_dir / f"{stem}.partial.npz"
    scores = load_partial(partial)
    pending = [parent for parent in sorted(representatives) if parent not in scores]
    frame_cache: dict[object, np.ndarray] = {}
    bundle["prepared_frames"] = {}
    print(
        f"{stem}: {len(candidates)} candidate forks, {len(representatives)} parents, "
        f"{len(scores)} resumed",
        flush=True,
    )
    try:
        for start in range(0, len(pending), batch_size):
            if stop_requested():
                save_partial(partial, scores)
                raise SystemExit(75)
            batch_parents = pending[start : start + batch_size]
            samples = []
            for parent in batch_parents:
                child, candidate, t = representatives[parent]
                samples.append(
                    divnet.prepare_divnet_input(
                        stem,
                        t,
                        nodes[parent],
                        bundle,
                        frame_cache,
                        reader,
                    )
                )
            tensor = torch.from_numpy(np.stack(samples)).to(
                device=bundle["device"], dtype=torch.float32
            )
            with torch.inference_mode(), torch.autocast(
                device_type="cuda",
                dtype=torch.float16,
                enabled=bundle["device"].type == "cuda",
            ):
                probability = torch.sigmoid(bundle["model"](tensor)).flatten().float().cpu().numpy()
            for parent, value in zip(batch_parents, probability):
                scores[int(parent)] = float(value)
            if len(scores) % checkpoint_every < len(batch_parents):
                save_partial(partial, scores)
                print(f"  {stem}: {len(scores)}/{len(representatives)} parents", flush=True)
    except KeyboardInterrupt:
        save_partial(partial, scores)
        raise

    if len(scores) != len(representatives):
        save_partial(partial, scores)
        raise RuntimeError(f"{stem}: scored {len(scores)} of {len(representatives)} parents")
    parents = np.array(sorted(scores), dtype=np.int64)
    atomic_npz(
        output,
        p=parents,
        score=np.array([scores[int(parent)] for parent in parents], dtype=np.float32),
    )
    partial.unlink(missing_ok=True)
    bundle["prepared_frames"] = {}
    if bundle["device"].type == "cuda":
        torch.cuda.empty_cache()
    print(f"{stem}: DivNet complete", flush=True)
    return output


def combine(files: list[Path], output: Path) -> None:
    columns: dict[str, list[np.ndarray]] = {key: [] for key in ("stem", "p", "score")}
    for path in files:
        with np.load(path) as payload:
            columns["stem"].append(np.array([path.stem] * len(payload["p"])))
            columns["p"].append(np.asarray(payload["p"]))
            columns["score"].append(np.asarray(payload["score"]))
    atomic_npz(output, **{key: np.concatenate(values) for key, values in columns.items()})
    print(f"combined {len(files)} videos -> {output}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="friend_a_b20_exp29")
    parser.add_argument("--stems", nargs="*", default=[])
    parser.add_argument("--data-dir", default=str(pl.DEFAULT_DATA))
    parser.add_argument("--parent-um", type=float, default=15.0)
    parser.add_argument("--candidate-k", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--checkpoint-every", type=int, default=256)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    cache = pl.DEFAULT_CACHE / args.tag
    stems = args.stems or sorted(path.stem for path in (cache / "ckpt").glob("*.npz"))
    output_dir = cache / "divnet"
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = ROOT / "external" / "giorgosi__biohub-divnet-v2" / "best_overall.pt"
    bundle = divnet.load_divnet_mitosis_model(checkpoint)
    reader = FrameReader(Path(args.data_dir))
    completed: list[Path] = []
    for stem in stems:
        completed.append(
            score_video(
                stem,
                cache,
                output_dir,
                bundle,
                reader,
                args.parent_um,
                args.candidate_k,
                args.batch_size,
                args.checkpoint_every,
            )
        )
        if stop_requested():
            raise SystemExit(75)
    if args.output:
        combine(completed, Path(args.output))
    else:
        print(f"per-video DivNet scores are complete in {output_dir}", flush=True)


if __name__ == "__main__":
    main()
