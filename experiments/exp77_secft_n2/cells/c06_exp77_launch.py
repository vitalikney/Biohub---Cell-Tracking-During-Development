# [exp77] LAUNCHER. It runs the two recipes as two subprocesses of the worker written by the cell above:
#   n2a: GPU0 (CUDA_VISIBLE_DEVICES=0), init = the exp71 student ed8c616b, lr 1e-5, loader seed 271828. This is epoch 2.
#   n2b: GPU1 (CUDA_VISIBLE_DEVICES=1), init = the pilkwang parent 9bac2fa0, lr 3e-5 (3x), loader seed 314159 (as exp71).
# Both runs use the exp71 loss against the frozen ORIGINAL teacher 9bac2fa0, frozen BN, the same trainable modules,
# num_workers 2 each (the box has 4 vCPUs) and at most one pass over the loader.
# Time caps:
#   - each worker stops training at min(its start + 4.5 h, the deadline set here) and saves the student;
#   - the launcher touches a stop file 5 min after that deadline, then kills the process group 20 min after it;
#   - all training must end by EXP77_T0 + 5.75 h, so the notebook finishes well under 7 h.
# If the session shows only ONE GPU, the two runs go one after the other on GPU0, and each gets half of the
# remaining window.
# The EXP77_* environment overrides exist only for the local CPU smoke test (as in exp71). On Kaggle the defaults apply.
import datetime
import math
import os
import signal

PROBE_ITERS = int(os.environ.get("EXP77_PROBE_ITERS", "40"))
PROBE_WARMUP_SKIP = int(os.environ.get("EXP77_PROBE_WARMUP_SKIP", "10"))
TRAIN_BUDGET_S = float(os.environ.get("EXP77_TRAIN_BUDGET_H", "4.25")) * 3600.0
HARD_STOP_S = float(os.environ.get("EXP77_HARD_STOP_H", "4.5")) * 3600.0
NUM_WORKERS = int(os.environ.get("EXP77_NUM_WORKERS", "2"))
DATALOADER_TIMEOUT_S = float(os.environ.get("EXP77_DATALOADER_TIMEOUT_S", "300"))
PROGRESS_EVERY = int(os.environ.get("EXP77_PROGRESS_EVERY", "500"))
EXPECTED_TRAIN_VIDEOS = int(os.environ.get("EXP77_EXPECTED_TRAIN_VIDEOS", "199"))
TRAIN_WINDOW_S = float(os.environ.get("EXP77_TRAIN_WINDOW_H", "5.75")) * 3600.0
STOP_GRACE_S = float(os.environ.get("EXP77_STOP_GRACE_S", "300"))
KILL_GRACE_S = float(os.environ.get("EXP77_KILL_GRACE_S", "1200"))
POLL_S = float(os.environ.get("EXP77_POLL_S", "60"))
MIN_RUN_WINDOW_S = float(os.environ.get("EXP77_MIN_RUN_WINDOW_S", "1800"))
TAIL_MAX_LINES = int(os.environ.get("EXP77_TAIL_MAX_LINES", "40"))
GPU_SLOTS = int(os.environ.get("EXP77_GPU_SLOTS", str(torch.cuda.device_count())))
assert GPU_SLOTS >= 1, "no GPU visible"
TRAIN_END_UNIX = EXP77_T0 + TRAIN_WINDOW_S

WORKER_SRC = WORKING_ROOT / "exp77_worker.py"  # written by the %%writefile cell
assert WORKER_SRC.is_file(), WORKER_SRC
EXP77_LOGS = WORKING_ROOT / "exp77_logs"
EXP77_LOGS.mkdir(parents=True, exist_ok=True)

RECIPE = ("y3uanm notebook0afc5663f6 (v1) teacher-distilled fine-tune of the pilkwang seed314159 secondary; "
          "teacher = frozen pilkwang parent 9bac2fa0")
RUN_SPECS = [
    {
        "label": "n2a",
        "lr": 1e-5,
        "seed": 271828,
        "init_weights": str(secft_all_weights),
        "init_sha256": SECFT_ALL_SHA256,
        "init_desc": "vitaliineibauer/biohub-secft-all-v1 (exp71 student: 1 epoch, lr 1e-5, seed 314159)",
        "export_dir": "secft_n2a",
        "artifact_name": "biohub-secft-n2a-v1",
    },
    {
        "label": "n2b",
        "lr": 3e-5,
        "seed": 314159,
        "init_weights": str(initial_weights),
        "init_sha256": expected_initial_sha256,
        "init_desc": "pilkwang/biohub-temporal-unet3d-seed314159-v1 (the parent = the teacher)",
        "export_dir": "secft_n2b",
        "artifact_name": "biohub-secft-n2b-v1",
    },
]
SPEC_BY_LABEL = {spec["label"]: spec for spec in RUN_SPECS}
SLOTS = [str(i) for i in range(min(GPU_SLOTS, len(RUN_SPECS)))]

EXP77_LOG = {
    "kernel": "vitaliineibauer/biohub-exp77-secft-n2",
    "recipe": RECIPE,
    "started_utc": datetime.datetime.fromtimestamp(EXP77_T0, datetime.timezone.utc).isoformat(timespec="seconds"),
    "torch": torch.__version__,
    "n_visible_gpus_notebook": torch.cuda.device_count(),
    "gpu_slots": SLOTS,
    "mode": "parallel" if len(SLOTS) >= len(RUN_SPECS) else "sequential",
    "train_videos": len(names),
    "teacher_sha256": expected_initial_sha256,
    "patched_train_script_sha256": PATCHED_TRAIN_SCRIPT_SHA256,
    "knobs": {
        "probe_iters": PROBE_ITERS,
        "probe_warmup_skip": PROBE_WARMUP_SKIP,
        "train_budget_s": TRAIN_BUDGET_S,
        "hard_stop_s": HARD_STOP_S,
        "num_workers": NUM_WORKERS,
        "dataloader_timeout_s": DATALOADER_TIMEOUT_S,
        "train_window_s": TRAIN_WINDOW_S,
        "stop_grace_s": STOP_GRACE_S,
        "kill_grace_s": KILL_GRACE_S,
    },
    "run_specs": RUN_SPECS,
    "launch": {},
}


def _run_cfg(spec, slot, deadline_unix):
    out_dir = run_dir / spec["label"]
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg = {
        "label": spec["label"],
        "recipe": RECIPE,
        "out_dir": str(out_dir),
        "log_path": str(EXP77_LOGS / f"{spec['label']}_log.json"),
        "stop_file": str(out_dir / "STOP"),
        "deadline_unix": deadline_unix,
        "repo_scripts": str(repo_dir / "scripts"),
        "repo_src": str(repo_dir / "src"),
        "train_script": str(train_script),
        "patched_train_script_sha256": PATCHED_TRAIN_SCRIPT_SHA256,
        "config": config,
        "data_dir": str(data_dir),
        "splits_path": str(splits_path),
        "names": names,
        "teacher_weights": str(initial_weights),
        "teacher_sha256": expected_initial_sha256,
        "init_weights": spec["init_weights"],
        "init_sha256": spec["init_sha256"],
        "init_desc": spec["init_desc"],
        "lr": spec["lr"],
        "seed": spec["seed"],
        "knobs": {
            "probe_iters": PROBE_ITERS,
            "probe_warmup_skip": PROBE_WARMUP_SKIP,
            "train_budget_s": TRAIN_BUDGET_S,
            "hard_stop_s": HARD_STOP_S,
            "num_workers": NUM_WORKERS,
            "dataloader_timeout_s": DATALOADER_TIMEOUT_S,
            "progress_every": PROGRESS_EVERY,
            "expected_train_videos": EXPECTED_TRAIN_VIDEOS,
        },
    }
    cfg_path = out_dir / "run_cfg.json"
    cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return cfg_path, cfg


def _launch(spec, slot, deadline_unix):
    cfg_path, cfg = _run_cfg(spec, slot, deadline_unix)
    env = dict(os.environ)
    env["CUDA_VISIBLE_DEVICES"] = slot
    env["PYTHONPATH"] = os.pathsep.join(
        p for p in (cfg["repo_scripts"], cfg["repo_src"], os.environ.get("PYTHONPATH", "")) if p
    )
    env["PYTHONUNBUFFERED"] = "1"
    env["OMP_NUM_THREADS"] = "2"  # 2 trainers + 4 loader workers share 4 vCPUs
    env["MKL_NUM_THREADS"] = "2"
    log_path = EXP77_LOGS / f"worker_{spec['label']}.log"
    log_file = open(log_path, "ab")
    proc = subprocess.Popen(
        [sys.executable, "-u", str(WORKER_SRC), str(cfg_path)],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        cwd=str(WORKING_ROOT),
        env=env,
        start_new_session=True,  # own process group: the watchdog can kill the loader workers too
    )
    state = {
        "spec": spec,
        "slot": slot,
        "proc": proc,
        "log_path": log_path,
        "log_file": log_file,
        "log_pos": 0,
        "stop_file": Path(cfg["stop_file"]),
        "deadline_unix": deadline_unix,
        "launched_unix": time.time(),
        "stop_touched": False,
        "killed": False,
    }
    EXP77_LOG["launch"][spec["label"]] = {
        "slot_cuda_visible_devices": slot,
        "pid": proc.pid,
        "launched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "deadline_utc": datetime.datetime.fromtimestamp(deadline_unix, datetime.timezone.utc).isoformat(timespec="seconds"),
        "lr": spec["lr"],
        "seed": spec["seed"],
        "init_sha256": spec["init_sha256"],
    }
    print(f"[exp77] launched {spec['label']} on CUDA_VISIBLE_DEVICES={slot} (pid {proc.pid}); lr {spec['lr']:g}, "
          f"seed {spec['seed']}, init {spec['init_sha256'][:8]}; training deadline in "
          f"{(deadline_unix - time.time()) / 3600:.2f} h", flush=True)
    return state


def _tail(state, final=False):
    """Print the new part of a worker log (tqdm \\r refreshes become lines), at most TAIL_MAX_LINES per poll."""
    with open(state["log_path"], "rb") as fh:
        fh.seek(state["log_pos"])
        data = fh.read()
        state["log_pos"] = fh.tell()
    if not data:
        return
    lines = [ln for ln in data.decode("utf-8", errors="replace").replace("\r", "\n").split("\n") if ln.strip()]
    limit = 10 * TAIL_MAX_LINES if final else TAIL_MAX_LINES
    if len(lines) > limit:
        print(f"[{state['spec']['label']}] ... {len(lines) - limit} lines skipped (full log: {state['log_path']})")
        lines = lines[-limit:]
    for ln in lines:
        print(f"[{state['spec']['label']}] {ln[:400]}")
    sys.stdout.flush()


def _kill(state):
    proc = state["proc"]
    try:
        if hasattr(os, "killpg"):
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
    except (ProcessLookupError, PermissionError, OSError) as exc:
        print(f"[exp77] kill {state['spec']['label']}: {exc!r}", flush=True)
    try:
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
    state["killed"] = True


pending = list(RUN_SPECS)
active = {}
WORKER_RESULTS = {}
while pending or active:
    for slot in SLOTS:
        while slot not in active and pending:
            spec = pending.pop(0)
            now = time.time()
            # Parallel: 1 run per slot, it gets the whole window. Sequential fallback (1 GPU): the runs still to go
            # share the remaining window evenly.
            runs_to_go = math.ceil((1 + len(pending)) / len(SLOTS))
            share = (TRAIN_END_UNIX - now) / runs_to_go
            if share < MIN_RUN_WINDOW_S:
                print(f"[exp77] SKIP {spec['label']}: only {share / 60:.0f} min of training window left", flush=True)
                WORKER_RESULTS[spec["label"]] = {"returncode": None, "killed": False, "skipped": "no_time"}
                continue
            active[slot] = _launch(spec, slot, now + share)
    if not active:
        break
    time.sleep(POLL_S)
    for slot, state in list(active.items()):
        _tail(state)
        label = state["spec"]["label"]
        rc = state["proc"].poll()
        now = time.time()
        if rc is None and not state["stop_touched"] and now > state["deadline_unix"] + STOP_GRACE_S:
            state["stop_file"].touch()
            state["stop_touched"] = True
            print(f"[exp77] WATCHDOG: {label} still running {STOP_GRACE_S:.0f} s after its deadline; stop file touched",
                  flush=True)
        if rc is None and now > state["deadline_unix"] + KILL_GRACE_S:
            print(f"[exp77] WATCHDOG: killing {label} ({KILL_GRACE_S:.0f} s after its deadline)", flush=True)
            _kill(state)
            rc = state["proc"].poll()
        if rc is None:
            continue
        _tail(state, final=True)
        state["log_file"].close()
        WORKER_RESULTS[label] = {
            "returncode": rc,
            "killed": state["killed"],
            "stop_file_touched": state["stop_touched"],
            "wall_s": round(now - state["launched_unix"], 1),
        }
        print(f"[exp77] {label} exited with code {rc} after {(now - state['launched_unix']) / 3600:.2f} h"
              f"{' (KILLED by the watchdog)' if state['killed'] else ''}", flush=True)
        del active[slot]

# Collect the students: a run counts only if TRAIN_DONE.json exists and its sha matches the weights file.
STUDENTS = {}
for spec in RUN_SPECS:
    label = spec["label"]
    res = WORKER_RESULTS.setdefault(label, {"returncode": None, "killed": False})
    log_json = EXP77_LOGS / f"{label}_log.json"
    res["worker_log"] = json.loads(log_json.read_text(encoding="utf-8")) if log_json.is_file() else None
    done_path = run_dir / label / "TRAIN_DONE.json"
    if not done_path.is_file():
        res["status"] = "no_student"
        print(f"[exp77] {label}: NO STUDENT (TRAIN_DONE.json missing; returncode {res['returncode']})", flush=True)
        continue
    done = json.loads(done_path.read_text(encoding="utf-8"))
    cand = Path(done["candidate"])
    if not cand.is_file() or hashlib.sha256(cand.read_bytes()).hexdigest() != done["sha256"]:
        res["status"] = "bad_student_file"
        print(f"[exp77] {label}: candidate missing or sha mismatch vs TRAIN_DONE.json", flush=True)
        continue
    res["status"] = "trained"
    if res["returncode"] not in (0, None) or res["killed"]:
        print(f"[exp77] {label}: the student was saved, but the worker then failed or was killed "
              f"(returncode {res['returncode']}); exporting it anyway (the proxy may be missing)", flush=True)
    STUDENTS[label] = {"candidate": cand, "sha256": done["sha256"], "done": done}
EXP77_LOG["worker_results"] = {k: {kk: vv for kk, vv in v.items() if kk != "worker_log"} for k, v in WORKER_RESULTS.items()}
print(f"[exp77] students ready for sanity/export: {sorted(STUDENTS)}; "
      f"notebook elapsed {(time.time() - EXP77_T0) / 3600:.2f} h", flush=True)
