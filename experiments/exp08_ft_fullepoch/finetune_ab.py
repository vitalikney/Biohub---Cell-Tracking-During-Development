# --- exp03: fine-tune from pretrained weights and A/B the RAW model on the fixed holdout ---
# Raw model = predict_unet_transformer.py (+ILP), no notebook post-processing. Same holdout for A and B.
import json, os, subprocess, sys, time, shutil
from pathlib import Path

E = os.environ.get
FT_EPOCHS = int(E("BIOHUB_FT_EPOCHS", "3"))
FT_MAX_ITERS = E("BIOHUB_FT_MAX_ITERS", "")          # "" = full epoch
FT_BATCH = int(E("BIOHUB_FT_BATCH", "8"))
FT_LR = E("BIOHUB_FT_LR", "5e-5")
FT_DET_LOSS = E("BIOHUB_FT_DET_LOSS", "bce")         # bce | gauss_focal
FT_DET_SIGMA = E("BIOHUB_FT_DET_SIGMA_UM", "2.5")
FT_WINDOW = E("BIOHUB_FT_WINDOW", "2")
FT_DOWNSAMPLE = E("BIOHUB_FT_DOWNSAMPLE", "1,4,4")
FT_DET_NEG_W = E("BIOHUB_FT_DET_NEG_WEIGHT", "0.01")
FT_DET_LOSS_W = E("BIOHUB_FT_DET_LOSS_WEIGHT", "1.0")
FT_N_TRAIN = int(E("BIOHUB_FT_N_TRAIN", "0"))        # 0 = all 183 non-holdout videos
FT_INIT = E("BIOHUB_FT_INIT", "pretrained")           # pretrained | scratch
RUN_BASELINE_EVAL = E("BIOHUB_RUN_BASELINE_EVAL", "1") != "0"
DET_THRESHOLD = E("BIOHUB_DET_THRESHOLD", "0.965")
ILP_ARGS = ["--use-ilp", "--ilp-edge-weight", "-1.0", "--ilp-appearance-weight", E("BIOHUB_ILP_APPEARANCE_WEIGHT", "0.0"),
            "--ilp-disappearance-weight", E("BIOHUB_ILP_DISAPPEARANCE_WEIGHT", "2"),
            "--ilp-division-weight", E("BIOHUB_ILP_DIVISION_WEIGHT", "1.2")]
SEED = E("BIOHUB_FT_SEED", "42")

HOLDOUT = json.loads(E("BIOHUB_HOLDOUT_JSON"))  # dict with 'holdout' and 'train'

# ---- writable training repo -------------------------------------------------
TRAIN_REPO = WORKING_DIR / "train_repo"
shutil.rmtree(TRAIN_REPO, ignore_errors=True)
TRAIN_REPO.mkdir(parents=True)
for sub in ("scripts", "src"):
    shutil.copytree(REPO_DIR / sub, TRAIN_REPO / sub)
(TRAIN_REPO / "weights").mkdir()
shutil.copytree(REPO_DIR / "weights" / METHOD, TRAIN_REPO / "weights" / METHOD)
PRETRAINED = TRAIN_REPO / "weights" / METHOD / "split_0" / "edge_predictor_best.pth"
apply_train_patches(TRAIN_REPO / "scripts" / "train_unet_transformer.py")
(TRAIN_REPO / "scripts" / "score_holdout.py").write_text('''
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, "scripts")
import evaluate as ev
ap = argparse.ArgumentParser(); ap.add_argument("--method"); ap.add_argument("--out"); ap.add_argument("geffs", nargs="+")
a = ap.parse_args()
geffs = [Path(g) for g in a.geffs]
rows = ev.evaluate_run({"username": "x", "method": a.method, "split": "split_0", "dir": None, "geffs": geffs})
s = ev.summarise(rows)
summary = {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in s.items()}
Path(a.out).write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, default=str))
print("SCORE", a.method, json.dumps(summary))
''')

train_stems = HOLDOUT["train"] if FT_N_TRAIN <= 0 else HOLDOUT["train"][:FT_N_TRAIN]
val_stems = HOLDOUT["holdout"]
splits_path = TRAIN_REPO / "ft_splits.json"
splits_path.write_text(json.dumps([{"split": 0, "train": train_stems, "test": val_stems}], indent=1))
# evaluate.py looks for DATA_DIR/dataset_splits.json (read-only mount) -> it just skips the missing check.
print(f"train videos {len(train_stems)} | holdout {len(val_stems)}", flush=True)

ENV = {**os.environ, "PYTHONPATH": "src", "PYTHONUNBUFFERED": "1", "BIOHUB_DATA_DIR": str(TRAIN_DIR),
       "PYTORCH_ALLOC_CONF": "expandable_segments:True"}


def run(cmd, log_name, cwd=TRAIN_REPO, env=ENV):
    print("$", " ".join(map(str, cmd)), flush=True)
    t0 = time.time()
    with open(WORKING_DIR / log_name, "w") as log:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            if "FutureWarning" in line or "sk_imread" in line or "_gcd_import" in line:
                continue
            print(line, end="", flush=True)
            log.write(line)
        rc = proc.wait()
    print(f"[{log_name}] exit={rc} wall={(time.time()-t0)/60:.1f} min", flush=True)
    return rc


def predict_and_score(weights: Path, method: str) -> dict:
    """2-GPU sharded prediction on the holdout, then micro-averaged score over all holdout videos."""
    n_gpu = int(os.environ.get("BIOHUB_N_GPU", "2"))
    procs = []
    for g in range(max(1, n_gpu)):
        cmd = [sys.executable, "scripts/predict_unet_transformer.py", "--data-dir", str(TRAIN_DIR),
               "--splits", str(splits_path), "--split", "0", "--weights", str(weights),
               "--method", f"{method}_gpu{g}", "--slice", f"{g}::{max(1, n_gpu)}",
               "--det-threshold", DET_THRESHOLD, "--unet-batch-size", "4", *ILP_ARGS]
        env = {**ENV, "CUDA_VISIBLE_DEVICES": str(g)}
        print("$", " ".join(cmd), flush=True)
        procs.append((g, subprocess.Popen(cmd, cwd=TRAIN_REPO, env=env, stdout=open(WORKING_DIR / f"predict_{method}_gpu{g}.log", "w"), stderr=subprocess.STDOUT)))
    t0 = time.time()
    for g, p in procs:
        rc = p.wait()
        print(f"  shard {g} exit={rc}", flush=True)
        if rc != 0:
            print(Path(WORKING_DIR / f"predict_{method}_gpu{g}.log").read_text()[-3000:])
            raise RuntimeError(f"prediction shard {g} failed")
    print(f"  prediction wall {(time.time()-t0)/60:.1f} min", flush=True)
    # score with the repo's evaluator (same metric code as the competition) -- in a SUBPROCESS so the
    # notebook process never holds GPU memory (open_dataset normalises on GPU) that would OOM training.
    geffs = sorted(p for g in range(max(1, n_gpu)) for p in (TRAIN_REPO / "predictions").rglob(f"{method}_gpu{g}/split_0/*.geff"))
    assert len(geffs) == len(val_stems), (len(geffs), len(val_stems))
    out_json = WORKING_DIR / f"score_{method}.json"
    rc = run([sys.executable, "scripts/score_holdout.py", "--method", method, "--out", str(out_json), *map(str, geffs)],
             f"score_{method}.log")
    if rc != 0:
        raise RuntimeError("scoring failed")
    out = json.loads(out_json.read_text())["summary"]
    print(f"== {method}: score={out['score']:.4f} adj_edge={out['adj_edge_jaccard']:.4f} edge={out['edge_jaccard']:.4f} "
          f"div={out['division_jaccard']:.4f} (TP={out['division_tp']} FP={out['division_fp']} FN={out['division_fn']}) node_recall={out['node_recall']:.4f}", flush=True)
    return out


results = {}
# ---- A: pretrained raw model on holdout ---------------------------------------
if RUN_BASELINE_EVAL:
    results["A_pretrained"] = predict_and_score(PRETRAINED, "A_pretrained")

# ---- B: fine-tune ----------------------------------------------------------------
cmd = [sys.executable, "scripts/train_unet_transformer.py", "--method", "ft",
       "--data-dir", str(TRAIN_DIR), "--splits", str(splits_path), "--split", "0",
       "--epochs", str(FT_EPOCHS), "--batch-size", str(FT_BATCH), "--num-workers", E("BIOHUB_FT_NUM_WORKERS", "4"), "--lr", FT_LR,
       "--det-loss-weight", FT_DET_LOSS_W, "--det-neg-weight", FT_DET_NEG_W,
       "--window-size", FT_WINDOW, "--downsample", FT_DOWNSAMPLE, "--pool-kernel-um", "5.0",
       "--det-loss", FT_DET_LOSS, "--det-sigma-um", FT_DET_SIGMA, "--seed", SEED]
if FT_MAX_ITERS:
    cmd += ["--max-iters", FT_MAX_ITERS]
cmd += E("BIOHUB_FT_EXTRA_FLAGS", "").split()
if FT_INIT == "pretrained":
    cmd += ["--init-weights", str(PRETRAINED)]
rc = run(cmd, "train_ft.log")
if rc != 0:
    raise SystemExit(rc)
FT_WEIGHTS = TRAIN_REPO / "weights" / "ft" / "split_0" / "edge_predictor_best.pth"
dst = WORKING_DIR / "ft_weights" / "unet_transformer" / "split_0"
shutil.rmtree(WORKING_DIR / "ft_weights", ignore_errors=True)
shutil.copytree(FT_WEIGHTS.parent, dst)
print("saved fine-tuned weights to", dst, [p.name for p in dst.iterdir()], flush=True)

results["B_finetuned"] = predict_and_score(FT_WEIGHTS, "B_finetuned")

cfg = {k: v for k, v in os.environ.items() if k.startswith("BIOHUB_FT") or k in ("BIOHUB_DET_THRESHOLD",)}
(WORKING_DIR / "exp_summary.json").write_text(json.dumps({"config": cfg, "results": results}, indent=1))
print(json.dumps({"config": cfg, "results": {k: {m: v[m] for m in ("score", "adj_edge_jaccard", "division_jaccard", "node_recall")} for k, v in results.items()}}, indent=1))

# ---- keep prediction graphs as ONE zip (reliable to download), then cleanup
shutil.make_archive(str(WORKING_DIR / "predictions"), "zip", root_dir=str(TRAIN_REPO / "predictions"))
print("predictions.zip:", (WORKING_DIR / "predictions.zip").stat().st_size // 1024, "KB", flush=True)
# ---- cleanup: drop bulky prediction graphs and repo copies so `kaggle kernels output` stays small ----
for _d in (TRAIN_REPO / "predictions", REPO_DIR, TRAIN_REPO / "src", TRAIN_REPO / "scripts", TRAIN_REPO / "weights"):
    shutil.rmtree(_d, ignore_errors=True)
print("cleanup done; kept:", sorted(p.name for p in WORKING_DIR.iterdir()))
