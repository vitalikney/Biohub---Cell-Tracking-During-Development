"""exp77 end-to-end CPU check with the REAL pieces. It runs locally and is never uploaded.

The real pieces:
  - the pinned support-pack trainer (sha c4f63177), patched by c01's own patch code;
  - the real pilkwang teacher 9bac2fa0 and the real exp71 student ed8c616b, with the notebook's real sha constants;
  - 4 real train videos (2 x 44b6, 2 x 6bba), linked through directory junctions.
Cells c03, c04, the worker, c06, c07 and c08 run unchanged, except that /kaggle/working and /kaggle/input point to a
scratch dir. Both workers run the real SecondaryFineTune and loss for a few iterations on the CPU. torch.cuda.synchronize
is a no-op in the children, via sitecustomize, because the trainer calls it every step.
"""
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import run_smoke as rs  # noqa: E402

TEACHER_W = REPO_ROOT / "_dl/exp60_a/secondary_seed_weights/unet_transformer/split_0"
TRACKING_REPO = REPO_ROOT / "_dl/exp60_a/tracking_repo"
SECFT_DS = REPO_ROOT / "_dl/secft_all_ds"
TRAIN = REPO_ROOT / "biohub-cell-tracking-during-development/train"
VIDEOS = ["44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b"]


def junction(link, target):
    subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True, capture_output=True)


def main():
    root = Path(os.environ.get("EXP77_SMOKE_ROOT", tempfile.gettempdir())) / "exp77_realcpu"
    if root.exists():
        for p in (root / "competition" / "train").glob("*"):
            os.rmdir(p) if p.is_dir() else p.unlink()  # remove junctions without touching their targets
        shutil.rmtree(root)
    root.mkdir(parents=True)
    six = sorted(n.name[:-5] for n in TRAIN.glob("6bba_*.zarr"))[1]
    videos = VIDEOS + [six]
    comp = root / "competition" / "train"
    comp.mkdir(parents=True)
    for v in videos:
        junction(comp / f"{v}.zarr", TRAIN / f"{v}.zarr")
        junction(comp / f"{v}.geff", TRAIN / f"{v}.geff")

    input_root = root / "input"
    teacher_dir = input_root / "datasets" / "pilkwang" / "biohub-temporal-unet3d-seed314159-v1"
    tw = teacher_dir / "weights" / "unet_transformer" / "split_0"
    tw.mkdir(parents=True)
    for f in ("edge_predictor_best.pth", "config.json"):
        shutil.copyfile(TEACHER_W / f, tw / f)
    secft_manifest = json.loads((SECFT_DS / "ARTIFACT_MANIFEST.json").read_text())
    (teacher_dir / "ARTIFACT_MANIFEST.json").write_text(json.dumps({
        "model": {"weight_sha256": rs.REAL_TEACHER_SHA},
        "compatibility": {**secft_manifest["compatibility"], "gate_diagnostics": {"x": 1}},
    }))
    shutil.copytree(SECFT_DS, input_root / "datasets" / "vitaliineibauer" / "biohub-secft-all-v1")

    working = root / "working"
    working.mkdir()
    run_dir = Path(tempfile.mkdtemp(prefix="secondary_ft_", dir=working))
    repo_dir = run_dir / "repo"
    shutil.copytree(TRACKING_REPO / "scripts", repo_dir / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(TRACKING_REPO / "src", repo_dir / "src", ignore=shutil.ignore_patterns("__pycache__"))
    initial_weights_root = run_dir / "initial_weights"
    shutil.copytree(teacher_dir / "weights", initial_weights_root)
    secondary_weights = initial_weights_root / "unet_transformer" / "split_0" / "edge_predictor_best.pth"

    # c01's own patch code: from the trainer sha pin down to write_text (it includes the pinned-sha assert)
    c01 = rs.cell("c01_setup_v1.py")
    start = c01.index('train_script = repo_dir / "scripts" / "train_unet_transformer.py"')
    end = c01.index('train_script.write_text(train_source, encoding="utf-8")') + len('train_script.write_text(train_source, encoding="utf-8")')
    choose_existing_dir, replace_once = rs.c01_functions()
    ns = {"__name__": "__main__", "Path": Path, "hashlib": hashlib, "repo_dir": repo_dir, "replace_once": replace_once}
    exec(compile(c01[start:end], "c01_patch", "exec"), ns)
    train_script = ns["train_script"]

    # children: sitecustomize makes torch.cuda.synchronize a no-op on this CPU-only torch
    site_dir = root / "site"
    site_dir.mkdir()
    (site_dir / "sitecustomize.py").write_text(
        "import os\nif os.environ.get('EXP77_ALLOW_CPU') == '1':\n    import torch\n"
        "    torch.cuda.synchronize = lambda *a, **k: None\n")
    env = {**rs.BASE_ENV, "EXP77_GPU_SLOTS": "2", "EXP77_PROBE_ITERS": "3", "EXP77_PROGRESS_EVERY": "2",
           "EXP77_TRAIN_BUDGET_H": str(25.0 / 3600), "EXP77_POLL_S": "5", "EXP77_TAIL_MAX_LINES": "60",
           "PYTHONPATH": str(site_dir)}
    os.environ.update(env)
    sys.path[:0] = [str(repo_dir / "scripts"), str(repo_dir / "src")]
    import train_unet_transformer as trainer
    import torch.nn.functional as functional
    import copy
    assert Path(trainer.__file__).resolve() == train_script.resolve()
    ns.update({
        "copy": copy, "json": json, "shutil": shutil, "subprocess": subprocess, "sys": sys, "tempfile": tempfile,
        "torch": torch, "functional": functional, "time": time, "input_root": input_root, "secondary": teacher_dir,
        "competition": root / "competition", "run_dir": run_dir, "initial_weights_root": initial_weights_root,
        "secondary_weights": secondary_weights, "secondary_config": secondary_weights.with_name("config.json"),
        "trainer": trainer, "choose_existing_dir": choose_existing_dir,
    })
    subs = [('Path("/kaggle/working")', f'Path("{working.as_posix()}")')]

    def ex(name):
        src = rs.cell(name)
        for a, b in subs:
            src = src.replace(a, b)
        exec(compile(src, name, "exec"), ns)

    t0 = time.time()
    ex("c03_splits_v1.py")
    ex("c04_exp77_inputs.py")
    (working / "exp77_worker.py").write_text(rs.cell("w05_exp77_worker.py"), encoding="utf-8")
    ex("c06_exp77_launch.py")
    ex("c07_exp77_sanity.py")
    ex("c08_exp77_export.py")
    log = json.loads((working / "exp77_train_log.json").read_text())
    info = {"working": working, "teacher_sha": rs.REAL_TEACHER_SHA, "t_state": ns["initial_state"]}
    rs.PREFIXES = ("unet.decoder_blocks.1.", "unet.head.", "detect_head.")
    rs.CONFIG = ns["config"]
    ma = rs.check_export("n2a", info, rs.REAL_SECFT_SHA, ns["secft_all_state"])
    mb = rs.check_export("n2b", info, rs.REAL_TEACHER_SHA, ns["initial_state"])
    for lab, m in (("n2a", ma), ("n2b", mb)):
        tr = m["model"]["training"]
        print(f"{lab}: sha {m['model']['weight_sha256'][:12]} parent {m['model']['parent_sha256'][:8]} "
              f"root {m['model']['root_parent_sha256'][:8]} lr {tr['learning_rate']} seed {tr['seed']} "
              f"n_iters {tr['n_iters']}/{tr['loader_len']} s/it {tr['seconds_per_iter_mean']}")
        assert tr["n_iters"] >= 1
        totals = log["runs"][lab]["detection_proxy"]["totals"]
        print(f"  proxy: {totals}")
        assert "error" not in log["runs"][lab]["detection_proxy"]
    assert "init_p0.5_det" in log["runs"]["n2a"]["detection_proxy"]["totals"]
    print(f"REAL CPU E2E PASS in {time.time() - t0:.0f} s")
    for p in (root / "competition" / "train").glob("*"):
        os.rmdir(p)


if __name__ == "__main__":
    main()
