"""exp77 local CPU smoke test (no GPU, never uploaded).

It runs the notebook's own cells c03, c04, the worker, c06, c07 and c08 against a fake trainer and dummy tensors.
The inputs are a fake pilkwang teacher, a fake exp71 student, 4 fake videos and a fake /kaggle/working. The two worker
subprocesses are real. Only the sha constants and the /kaggle/working path in the cell sources are replaced; the
knobs come in through the EXP77_* environment overrides.

Usage: python run_smoke.py [scenario ...]   (default: all)
"""
import ast
import copy
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

import torch
import torch.nn.functional as functional

HERE = Path(__file__).resolve().parent
CELLS = HERE.parent / "cells"
FAKE_REPO = HERE / "fake_repo"
REAL_TEACHER_SHA = "9bac2fa0dadc4a6fc1899e0caf187f4b553e0a7cd90ba1261a68b35ffe9e305f"
REAL_SECFT_SHA = "ed8c616bcc5990d3cccfe728d0e00469feb40ca8a0590137045f7ef225903f2e"
NAMES = ["44b6_aaaa0001", "44b6_aaaa0002", "6bba_bbbb0001", "6bba_bbbb0002"]
CONFIG = {"unet_out_channels": 4, "unet_layers": [4, 8], "downsample": [1, 4, 4], "window_size": 2, "pool_kernel_um": 5.0}
PREFIXES = ("unet.decoder_blocks.1.", "unet.head.", "detect_head.")

BASE_ENV = {
    "EXP77_ALLOW_CPU": "1",
    "EXP77_PROBE_ITERS": "4",
    "EXP77_PROBE_WARMUP_SKIP": "1",
    "EXP77_NUM_WORKERS": "0",
    "EXP77_PROGRESS_EVERY": "5",
    "EXP77_EXPECTED_TRAIN_VIDEOS": str(len(NAMES)),
    "EXP77_POLL_S": "0.5",
    "EXP77_MIN_RUN_WINDOW_S": "5",
    "EXP77_TAIL_MAX_LINES": "15",
}
SCENARIOS = {
    # both runs in parallel, full pass over the (24-window) loader, both exported
    "parallel_ok": {"EXP77_GPU_SLOTS": "2"},
    # 1 GPU -> sequential; n2a's probe loader fails with num_workers=2 -> retried with 0; tiny hard stop -> both saved early
    "sequential_loaderfail_hardstop": {
        "EXP77_GPU_SLOTS": "1", "EXP77_NUM_WORKERS": "2", "FAKE_FAIL_WORKERS_IN": "n2a",
        "EXP77_HARD_STOP_H": str(6.0 / 3600), "FAKE_ITER_SLEEP": "0.5", "EXP77_DATALOADER_TIMEOUT_S": "10",
    },
    # watchdog: stop file touched ~20 s after T0 (n2a stops mid-run, saved, exported, proxy crash tolerated);
    # n2b hangs in its real-run data load -> killed at ~T0+60 s -> not exported, notebook still succeeds
    "watchdog_stopfile_kill": {
        "EXP77_GPU_SLOTS": "2", "EXP77_TRAIN_WINDOW_H": str(120.0 / 3600), "EXP77_STOP_GRACE_S": "-100",
        "EXP77_KILL_GRACE_S": "-60", "FAKE_ITER_SLEEP": "1.0", "FAKE_HANG_IN": "n2b", "FAKE_CRASH_PROXY_IN": "n2a",
    },
    # both hang -> both killed -> the export cell raises "no student exported"
    "all_fail_raises": {
        "EXP77_GPU_SLOTS": "2", "EXP77_TRAIN_WINDOW_H": str(40.0 / 3600), "EXP77_STOP_GRACE_S": "-30",
        "EXP77_KILL_GRACE_S": "-20", "FAKE_HANG_IN": "secondary_ft_",
    },
}
FAKE_KEYS = ("FAKE_ITER_SLEEP", "FAKE_FAIL_WORKERS_IN", "FAKE_HANG_IN", "FAKE_CRASH_PROXY_IN")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def cell(name):
    return (CELLS / name).read_text(encoding="utf-8")


def c01_functions():
    """choose_existing_dir and replace_once, taken verbatim from c01 (the rest of c01 is Kaggle-only)."""
    tree = ast.parse(cell("c01_setup_v1.py"))
    keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("choose_existing_dir", "replace_once")]
    assert len(keep) == 2
    ns = {"Path": Path}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "c01_functions", "exec"), ns)
    return ns["choose_existing_dir"], ns["replace_once"]


def write_artifact(root, state, manifest_model, compat=True):
    w = root / "weights" / "unet_transformer" / "split_0" / "edge_predictor_best.pth"
    w.parent.mkdir(parents=True, exist_ok=True)
    torch.save(state, w)
    w.with_name("config.json").write_text(json.dumps(CONFIG, indent=2))
    manifest = {"model": {"weight_sha256": sha(w), **manifest_model}}
    if compat:
        manifest["compatibility"] = {"schema_version": 1, "models": {"unet_transformer": {}, "full_frame_center": {}},
                                     "gate_diagnostics": {"x": 1}}
    (root / "ARTIFACT_MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    return w, sha(w)


def setup(root):
    sys.path.insert(0, str(FAKE_REPO / "scripts"))
    fake = importlib.import_module("train_unet_transformer")
    sys.path.pop(0)
    torch.manual_seed(0)
    teacher = fake.UNetNodeTransformer(fake.TemporalUNet3D(1, CONFIG["unet_out_channels"], CONFIG["unet_layers"]),
                                       CONFIG["unet_out_channels"], 4 * fake._POS_EMBED_DIM)
    t_state = teacher.state_dict()
    input_root = root / "input"
    teacher_dir = input_root / "datasets" / "pilkwang" / "biohub-temporal-unet3d-seed314159-v1"
    t_w, t_sha = write_artifact(teacher_dir, t_state, {})
    s_state = {k: (v + 1e-3 if k.startswith(PREFIXES) and v.is_floating_point() and "running" not in k else v.clone())
               for k, v in t_state.items()}
    s_dir = input_root / "datasets" / "vitaliineibauer" / "biohub-secft-all-v1"
    s_w, s_sha = write_artifact(s_dir, s_state, {"parent_sha256": t_sha}, compat=False)
    competition = root / "competition"
    for n in NAMES:
        (competition / "train" / f"{n}.zarr").mkdir(parents=True)
        (competition / "train" / f"{n}.geff").mkdir()
    working = root / "working"
    working.mkdir()
    run_dir = Path(tempfile.mkdtemp(prefix="secondary_ft_", dir=working))
    repo_dir = run_dir / "repo"
    shutil.copytree(FAKE_REPO, repo_dir)
    initial_weights_root = run_dir / "initial_weights"
    shutil.copytree(teacher_dir / "weights", initial_weights_root)
    secondary_weights = initial_weights_root / "unet_transformer" / "split_0" / "edge_predictor_best.pth"
    train_script = repo_dir / "scripts" / "train_unet_transformer.py"
    sys.modules.pop("train_unet_transformer", None)
    sys.path[:0] = [str(repo_dir / "scripts"), str(repo_dir / "src")]
    trainer = importlib.import_module("train_unet_transformer")
    choose_existing_dir, replace_once = c01_functions()
    ns = {
        "__name__": "__main__",
        "copy": copy, "hashlib": hashlib, "json": json, "shutil": shutil, "subprocess": subprocess, "sys": sys,
        "tempfile": tempfile, "Path": Path, "torch": torch, "functional": functional, "time": time,
        "input_root": input_root, "secondary": teacher_dir, "competition": competition, "run_dir": run_dir,
        "repo_dir": repo_dir, "initial_weights_root": initial_weights_root, "secondary_weights": secondary_weights,
        "secondary_config": secondary_weights.with_name("config.json"), "train_script": train_script,
        "trainer": trainer, "choose_existing_dir": choose_existing_dir, "replace_once": replace_once,
    }
    return ns, {"teacher_sha": t_sha, "student_sha": s_sha, "t_state": t_state, "s_state": s_state,
                "working": working, "run_dir": run_dir}


def run_cells(ns, info):
    subs = [(REAL_TEACHER_SHA, info["teacher_sha"]), (REAL_SECFT_SHA, info["student_sha"]),
            ('Path("/kaggle/working")', f'Path("{info["working"].as_posix()}")')]

    def ex(name, src=None):
        src = src if src is not None else cell(name)
        for a, b in subs:
            src = src.replace(a, b)
        exec(compile(src, name, "exec"), ns)

    ex("c03_splits_v1.py")
    ex("c04_exp77_inputs.py")
    # the %%writefile cell
    (info["working"] / "exp77_worker.py").write_text(cell("w05_exp77_worker.py"), encoding="utf-8")
    ex("c06_exp77_launch.py")
    ex("c07_exp77_sanity.py")
    ex("c08_exp77_export.py")


def check_export(label, info, parent_sha, parent_state):
    d = info["working"] / f"secft_{label}"
    files = sorted(str(p.relative_to(d)).replace("\\", "/") for p in d.rglob("*") if p.is_file())
    assert files == ["ARTIFACT_MANIFEST.json", "weights/unet_transformer/split_0/config.json",
                     "weights/unet_transformer/split_0/edge_predictor_best.pth"], files
    m = json.loads((d / "ARTIFACT_MANIFEST.json").read_text())
    w = d / "weights/unet_transformer/split_0/edge_predictor_best.pth"
    assert m["model"]["weight_sha256"] == sha(w)
    assert m["models"]["unet_transformer"]["weight_sha256"] == sha(w)
    assert m["model"]["parent_sha256"] == parent_sha, (m["model"]["parent_sha256"], parent_sha)
    assert m["model"]["root_parent_sha256"] == info["teacher_sha"]
    assert m["model"]["teacher_sha256"] == info["teacher_sha"]
    assert m["artifact_name"] == f"biohub-secft-{label}-v1"
    assert "full_frame_center" not in m["compatibility"]["models"] and "gate_diagnostics" not in m["compatibility"]
    assert json.loads(w.with_name("config.json").read_text()) == CONFIG
    new = torch.load(w, map_location="cpu", weights_only=True)
    for ref in (parent_state, info["t_state"]):
        changed = [k for k in ref if not torch.equal(ref[k], new[k])]
        assert changed and all(k.startswith(PREFIXES) for k in changed), changed
    return m


def main(selected):
    results = {}
    scratch = Path(os.environ.get("EXP77_SMOKE_ROOT", tempfile.gettempdir())) / "exp77_smoke"
    for name in selected:
        env_over = {**BASE_ENV, **SCENARIOS[name]}
        saved = {k: os.environ.get(k) for k in set(env_over) | set(FAKE_KEYS)}
        for k in FAKE_KEYS:
            os.environ.pop(k, None)
        os.environ.update(env_over)
        root = scratch / name
        shutil.rmtree(root, ignore_errors=True)
        root.mkdir(parents=True)
        cwd = os.getcwd()
        sys_path = list(sys.path)
        t0 = time.time()
        print(f"\n==================== scenario {name} ====================", flush=True)
        try:
            ns, info = setup(root)
            raised = None
            try:
                run_cells(ns, info)
            except RuntimeError as exc:
                raised = exc
            working = info["working"]
            log = json.loads((working / "exp77_train_log.json").read_text())
            assert not info["run_dir"].exists(), "run_dir not cleaned up"
            assert (working / "exp77_logs" / "exp77_worker.py").is_file() and not (working / "exp77_worker.py").exists()
            top = sorted(p.name for p in working.iterdir())
            wr = log["worker_results"]
            if name == "parallel_ok":
                assert raised is None, raised
                assert top == ["exp77_logs", "exp77_train_log.json", "secft_n2a", "secft_n2b"], top
                ma = check_export("n2a", info, info["student_sha"], info["s_state"])
                mb = check_export("n2b", info, info["teacher_sha"], info["t_state"])
                for m, lr, seed in ((ma, 1e-5, 271828), (mb, 3e-5, 314159)):
                    tr = m["model"]["training"]
                    assert tr["learning_rate"] == lr and tr["seed"] == seed, tr
                    assert tr["n_iters"] == 24 and tr["loader_len"] == 24 and not tr["hard_stopped"], tr
                assert ma["model"]["training"]["total_epochs_incl_parent_ft"] == 2.0
                assert ma["parent_artifact"] == "vitaliineibauer/biohub-secft-all-v1"
                la, lb = log["launch"]["n2a"], log["launch"]["n2b"]
                assert la["slot_cuda_visible_devices"] == "0" and lb["slot_cuda_visible_devices"] == "1"
                assert log["runs"]["n2a"]["cuda_visible_devices"] == "0" and log["runs"]["n2b"]["cuda_visible_devices"] == "1"
                assert "init_p0.5_det" in log["runs"]["n2a"]["detection_proxy"]["totals"]
                assert "init_p0.5_det" not in log["runs"]["n2b"]["detection_proxy"]["totals"]
                assert "student_over_teacher_p0.965_det" in log["runs"]["n2b"]["detection_proxy"]["totals"]
                assert log["mode"] == "parallel"
                # both launched before either finished = parallel
                assert abs(wr["n2a"]["wall_s"] - wr["n2b"]["wall_s"]) < 30
            elif name == "sequential_loaderfail_hardstop":
                assert raised is None, raised
                assert log["mode"] == "sequential"
                for lab in ("n2a", "n2b"):
                    tr = check_export(lab, info, info["student_sha"] if lab == "n2a" else info["teacher_sha"],
                                      info["s_state"] if lab == "n2a" else info["t_state"])["model"]["training"]
                    assert tr["hard_stopped"] and tr["stop_reason"] == "hard_wall_clock", tr
                    assert 0 < tr["n_iters"] < 24, tr
                assert "probe_worker_failure" in log["runs"]["n2a"] and log["runs"]["n2a"]["knobs"]["num_workers"] == 0
                if sys.platform.startswith("linux"):  # fork: n2b's real 2-worker loader runs fine
                    assert "probe_worker_failure" not in log["runs"]["n2b"] and log["runs"]["n2b"]["knobs"]["num_workers"] == 2
                else:  # Windows spawn cannot run the (fake or real) trainer's loader workers -> the real fallback path
                    assert "probe_worker_failure" in log["runs"]["n2b"] and log["runs"]["n2b"]["knobs"]["num_workers"] == 0
                la, lb = log["launch"]["n2a"], log["launch"]["n2b"]
                assert la["slot_cuda_visible_devices"] == lb["slot_cuda_visible_devices"] == "0"
                assert lb["launched_utc"] >= la["launched_utc"]
                assert lb["deadline_utc"] > la["deadline_utc"]
            elif name == "watchdog_stopfile_kill":
                assert raised is None, raised
                assert top == ["exp77_logs", "exp77_train_log.json", "secft_n2a"], top
                tr = check_export("n2a", info, info["student_sha"], info["s_state"])["model"]["training"]
                assert tr["hard_stopped"] and tr["stop_reason"] == "stop_file" and 0 < tr["n_iters"] < 24, tr
                assert "error" in log["runs"]["n2a"]["detection_proxy"]
                assert wr["n2b"]["killed"] and wr["n2b"]["status"] == "no_student", wr["n2b"]
                assert wr["n2a"]["returncode"] == 0
            elif name == "all_fail_raises":
                assert raised is not None and "no student exported" in str(raised), raised
                assert top == ["exp77_logs", "exp77_train_log.json"], top
                assert wr["n2a"]["killed"] and wr["n2b"]["killed"]
            results[name] = f"PASS ({time.time() - t0:.0f} s)"
        except Exception:
            traceback.print_exc()
            results[name] = "FAIL"
        finally:
            os.chdir(cwd)
            sys.path[:] = sys_path
            sys.modules.pop("train_unet_transformer", None)
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
    print("\n==================== SUMMARY ====================")
    for k, v in results.items():
        print(f"  {k:35s} {v}")
    return all(v.startswith("PASS") for v in results.values())


if __name__ == "__main__":
    sel = sys.argv[1:] or list(SCENARIOS)
    sys.exit(0 if main(sel) else 1)
