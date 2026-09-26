import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path

import copy
import torch
import torch.nn.functional as functional

import time

input_root = Path("/kaggle/input")

# 新模型包上传到 Kaggle 后，修改这一处即可。
# 第一次使用原始模型时改成：
# SECONDARY_SLUG = "biohub-temporal-unet3d-seed314159-v1"
SECONDARY_SLUG = "biohub-temporal-unet3d-seed314159-v1"


def choose_existing_dir(name, candidates):
    for path in candidates:
        if path.is_dir():
            print(f"{name}: {path}", flush=True)
            return path
    checked = "\n".join(str(path) for path in candidates)
    raise FileNotFoundError(
        f"{name} not found. Checked:\n{checked}"
    )


path_t0 = time.perf_counter()

support = choose_existing_dir(
    "support",
    [
        input_root / "datasets" / "pilkwang"
        / "biohub-tracking-support-pack-50ep-v1",
        input_root / "datasets" / "hftams"
        / "biohub-tracking-support-pack-50ep-v1",
        input_root / "biohub-tracking-support-pack-50ep-v1",
    ],
)

secondary = choose_existing_dir(
    "secondary",
    [
        input_root / "datasets" / "pilkwang" / SECONDARY_SLUG,
        input_root / "datasets" / "hftams" / SECONDARY_SLUG,
        input_root / SECONDARY_SLUG,
    ],
)

competition = choose_existing_dir(
    "competition",
    [
        input_root / "competitions"
        / "biohub-cell-tracking-during-development",
        input_root / "biohub-cell-tracking-during-development",
    ],
)

assert (competition / "train").is_dir(), (
    f"train directory not found: {competition / 'train'}"
)

print(
    f"Path initialization: {time.perf_counter() - path_t0:.2f}s",
    flush=True,
)

run_dir = Path(tempfile.mkdtemp(prefix="secondary_ft_", dir="/kaggle/working"))
repo_dir = run_dir / "repo"
initial_weights_root = run_dir / "initial_weights"

print("support:", support)
print("secondary:", secondary)
print("competition:", competition)
print("run_dir:", run_dir)

# 只安装训练脚本实际需要的顶层包。
# --no-deps 是关键：避免 tracksdata 自动拉取 imagecodecs==2026.6.26。
runtime_packages = [
    "tracksdata",
    "polars==1.42.0",
    "polars-runtime-32==1.42.0",
    "zarr==3.2.1",
    "geff==1.2.0.1.1",
    "geff-spec==1.1.1",
    "numcodecs==0.15.1",
    "donfig==0.8.1.post1",
    "bidict==0.23.1",
    "ilpy==0.6.0",
    "pyscipopt==6.2.1",
    "dask",
    "blosc2",
    "pyarrow",
    "rustworkx",
    "sqlalchemy",
]

wheels_dir = support / "wheels"
assert wheels_dir.is_dir(), f"wheels directory not found: {wheels_dir}"

install_command = [
    sys.executable,
    "-m",
    "pip",
    "install",
    "--no-index",
    "--no-deps",
    "--force-reinstall",
    "--find-links",
    str(wheels_dir),
    *runtime_packages,
]

print("Installing runtime packages with --no-deps...")
print(" ".join(install_command))
subprocess.run(install_command, check=True)

# 复制推理仓库源码。
repo_source = support / "repo"
repo_archive = support / "repo.zip"

if repo_source.is_dir():
    shutil.copytree(repo_source, repo_dir)
elif repo_archive.is_file():
    shutil.unpack_archive(str(repo_archive), str(run_dir))
    if not repo_dir.exists():
        extracted = next(
            path for path in run_dir.iterdir()
            if path.is_dir() and path.name not in {"initial_weights"}
        )
        extracted.rename(repo_dir)
else:
    raise FileNotFoundError("Support pack contains neither repo/ nor repo.zip")

# 复制副模型权重。
secondary_weights_source = secondary / "weights"
secondary_weights_archive = secondary / "weights.zip"

if secondary_weights_source.is_dir():
    shutil.copytree(secondary_weights_source, initial_weights_root)
elif secondary_weights_archive.is_file():
    shutil.unpack_archive(str(secondary_weights_archive), str(initial_weights_root))
else:
    raise FileNotFoundError("Secondary artifact contains neither weights/ nor weights.zip")

secondary_weights = (
    initial_weights_root
    / "unet_transformer"
    / "split_0"
    / "edge_predictor_best.pth"
)
secondary_config = secondary_weights.with_name("config.json")

assert secondary_weights.is_file(), secondary_weights
assert secondary_config.is_file(), secondary_config

sys.path[:0] = [
    str(repo_dir / "scripts"),
    str(repo_dir / "src"),
]

train_script = repo_dir / "scripts" / "train_unet_transformer.py"
# [exp71] guard (not in y3uanm v1): patch only the exact support-pack trainer that x138 pins.
assert hashlib.sha256(train_script.read_bytes()).hexdigest() == (
    "c4f6317736bb3bb1ec8f3f6e9a6d935a463e3f0f1f685481b2d13218d35dc9ea"
), "support-pack train_unet_transformer.py is not the pinned version"
train_source = train_script.read_text(encoding="utf-8")


def replace_once(source, old, new, label):
    count = source.count(old)
    assert count == 1, (
        f"{label}: expected exactly one match, found {count}"
    )
    return source.replace(old, new, 1)


# 1. 给 train() 增加 validate 参数。
train_source = replace_once(
    train_source,
    """    pool_kernel_um: float = 5.0,
    data_parallel: bool = True,
) -> UNetNodeTransformer:""",
    """    pool_kernel_um: float = 5.0,
    data_parallel: bool = True,
    validate: bool = True,
) -> UNetNodeTransformer:""",
    "train signature",
)

# 3. validate=False 时不加载验证数据。
train_source = replace_once(
    train_source,
    """    train_video_data = _load(train_files, "train")
    test_video_data = _load(test_files, "test")
""",
    """    train_video_data = _load(train_files, "train")
    test_video_data = _load(test_files, "test") if validate else []
""",
    "validation data loading",
)


# 4. 不创建验证 Dataset。
train_source = replace_once(
    train_source,
    "    test_ds = FrameWindowDataset(test_video_data, max_nodes=max_nodes)\n",
    "    test_ds = FrameWindowDataset(test_video_data, max_nodes=max_nodes) if validate else None\n",
    "validation dataset",
)


# 5. 不创建验证 DataLoader。
train_source = replace_once(
    train_source,
    """    test_loader = DataLoader(
        test_ds, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, prefetch_factor=2 if num_workers > 0 else None,
        persistent_workers=num_workers > 0, pin_memory=False,
        generator=g, worker_init_fn=worker_init_fn,
    )
""",
    """    test_loader = (
        DataLoader(
            test_ds,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            prefetch_factor=2 if num_workers > 0 else None,
            persistent_workers=num_workers > 0,
            pin_memory=False,
            generator=g,
            worker_init_fn=worker_init_fn,
        )
        if validate
        else None
    )
""",
    "validation dataloader",
)


# 6. validate=False 时跳过完整 evaluate()。
train_source = replace_once(
    train_source,
    """        t0 = time.monotonic()
        test_loss, test_acc, test_recall = evaluate(model, test_loader, device, pool_kernel_um=pool_kernel_um)
        test_time = time.monotonic() - t0

        score = test_acc * test_recall
        is_best = score >= best_score

        if is_best:
            best_score = score
            # Normalise any DataParallel "unet.module." prefix to "unet." so the
            # checkpoint loads on a single GPU (e.g. in the prediction script).
            torch.save(
                {k.replace("unet.module.", "unet.", 1): v for k, v in model.state_dict().items()},
                save_path,
            )
""",
    """        if validate:
            t0 = time.monotonic()
            test_loss, test_acc, test_recall = evaluate(
                model,
                test_loader,
                device,
                pool_kernel_um=pool_kernel_um,
            )
            test_time = time.monotonic() - t0

            score = test_acc * test_recall
            is_best = score >= best_score
        else:
            test_loss = float("nan")
            test_acc = float("nan")
            test_recall = float("nan")
            test_time = 0.0
            score = 0.0
            is_best = True

        if is_best:
            best_score = score
            # Normalize any DataParallel prefix before saving.
            torch.save(
                {
                    k.replace("unet.module.", "unet.", 1): v
                    for k, v in model.state_dict().items()
                },
                save_path,
            )
""",
    "evaluation block",
)


# 7. 训练结束时输出正确的模式说明。
train_source = replace_once(
    train_source,
    """    print(f"\\nBest score (acc*recall): {best_score:.4f}, saved to {save_path}", flush=True)
""",
    """    if validate:
        print(
            f"\\nBest score (acc*recall): {best_score:.4f}, "
            f"saved to {save_path}",
            flush=True,
        )
    else:
        print(
            f"\\nTrain-only mode: latest model saved to {save_path}",
            flush=True,
        )
""",
    "training summary",
)


compile(train_source, str(train_script), "exec")
train_script.write_text(train_source, encoding="utf-8")

import inspect
import train_unet_transformer as trainer

assert Path(trainer.__file__).resolve() == train_script.resolve(), (
    f"Loaded wrong trainer: {trainer.__file__}"
)
assert "validate" in inspect.signature(trainer.train).parameters, (
    "Loaded trainer has no validate parameter. Restart the kernel."
)
assert torch.cuda.is_available(), "CUDA GPU is required"

print("Training script patched and imported.", flush=True)
print("trainer:", trainer.__file__, flush=True)
print("train signature:", inspect.signature(trainer.train), flush=True)
print("torch:", torch.__version__, flush=True)
print("CUDA:", torch.cuda.get_device_name(0), flush=True)
print("secondary weights:", secondary_weights, flush=True)
print("secondary config:", secondary_config, flush=True)
