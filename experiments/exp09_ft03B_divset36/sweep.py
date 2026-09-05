# --- exp07: predict hold12 with fine-tuned weights at several detection thresholds; zip all geffs ---
import json, os, subprocess, sys, time, shutil
from pathlib import Path
E = os.environ.get
HOLDOUT = json.loads(E("BIOHUB_HOLDOUT_JSON"))
THRESHOLDS = E("BIOHUB_SWEEP_THRESHOLDS", "0.93,0.965,0.985").split(",")
WEIGHTS_SUB = E("BIOHUB_WEIGHTS_SUB", "exp03B")
ILP_ARGS = ["--use-ilp", "--ilp-edge-weight", "-1.0", "--ilp-appearance-weight", E("BIOHUB_ILP_APPEARANCE_WEIGHT", "0.0"),
            "--ilp-disappearance-weight", E("BIOHUB_ILP_DISAPPEARANCE_WEIGHT", "2"),
            "--ilp-division-weight", E("BIOHUB_ILP_DIVISION_WEIGHT", "1.2")]

TRAIN_REPO = WORKING_DIR / "train_repo"
shutil.rmtree(TRAIN_REPO, ignore_errors=True); TRAIN_REPO.mkdir(parents=True)
for sub in ("scripts", "src"):
    shutil.copytree(REPO_DIR / sub, TRAIN_REPO / sub)
wsrc = next(p for p in [Path("/kaggle/input/datasets/vitaliineibauer/biohub-ft-weights") / WEIGHTS_SUB,
                        Path("/kaggle/input/biohub-ft-weights") / WEIGHTS_SUB] if p.exists())
WDIR = TRAIN_REPO / "weights" / "ft" / "split_0"; WDIR.mkdir(parents=True)
for f in ("edge_predictor_best.pth", "config.json"):
    shutil.copy(wsrc / f, WDIR / f)
WEIGHTS = WDIR / "edge_predictor_best.pth"
print("weights:", wsrc, (WDIR / "config.json").read_text())
val_stems = HOLDOUT["divset36"]
splits_path = TRAIN_REPO / "splits.json"
splits_path.write_text(json.dumps([{"split": 0, "train": [], "test": val_stems}]))
ENV = {**os.environ, "PYTHONPATH": "src", "PYTHONUNBUFFERED": "1", "BIOHUB_DATA_DIR": str(TRAIN_DIR)}
(TRAIN_REPO / "scripts" / "score_holdout.py").write_text('''
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, "scripts")
import evaluate as ev
ap = argparse.ArgumentParser(); ap.add_argument("--method"); ap.add_argument("--out"); ap.add_argument("geffs", nargs="+")
a = ap.parse_args()
rows = ev.evaluate_run({"username": "x", "method": a.method, "split": "split_0", "dir": None, "geffs": [Path(g) for g in a.geffs]})
s = ev.summarise(rows)
summary = {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in s.items()}
Path(a.out).write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, default=str))
print("SCORE", a.method, json.dumps(summary))
''')

def predict(method, thr):
    procs = []
    for g in range(2):
        cmd = [sys.executable, "scripts/predict_unet_transformer.py", "--data-dir", str(TRAIN_DIR), "--splits", str(splits_path),
               "--split", "0", "--weights", str(WEIGHTS), "--method", f"{method}_gpu{g}", "--slice", f"{g}::2",
               "--det-threshold", thr, "--unet-batch-size", "4", *ILP_ARGS]
        procs.append(subprocess.Popen(cmd, cwd=TRAIN_REPO, env={**ENV, "CUDA_VISIBLE_DEVICES": str(g)},
                                      stdout=open(WORKING_DIR / f"predict_{method}_gpu{g}.log", "w"), stderr=subprocess.STDOUT))
    t0 = time.time()
    for p in procs:
        if p.wait() != 0:
            raise RuntimeError(f"predict failed for {method}")
    print(f"{method}: prediction {(time.time()-t0)/60:.1f} min", flush=True)
    geffs = sorted((TRAIN_REPO / "predictions").rglob(f"{method}_gpu*/split_0/*.geff"))
    assert len(geffs) == len(val_stems), len(geffs)
    out = WORKING_DIR / f"score_{method}.json"
    r = subprocess.run([sys.executable, "scripts/score_holdout.py", "--method", method, "--out", str(out), *map(str, geffs)],
                       cwd=TRAIN_REPO, env=ENV, capture_output=True, text=True)
    print(r.stdout[-600:], r.stderr[-800:] if r.returncode else "", flush=True)
    s = json.loads(out.read_text())["summary"]
    print(f"== {method}: score={s['score']:.4f} edge={s['edge_jaccard']:.4f} recall={s['node_recall']:.4f} div={s['division_tp']}/{s['division_fp']}/{s['division_fn']}", flush=True)
    return s

results = {}
for thr in THRESHOLDS:
    m = f"thr{thr.replace('.', '')}"
    results[m] = predict(m, thr)
(WORKING_DIR / "sweep_summary.json").write_text(json.dumps(results, indent=1))
print(json.dumps({k: round(v["score"], 4) for k, v in results.items()}))
shutil.make_archive(str(WORKING_DIR / "predictions"), "zip", root_dir=str(TRAIN_REPO / "predictions"))
print("predictions.zip KB:", (WORKING_DIR / "predictions.zip").stat().st_size // 1024)
for d in (TRAIN_REPO, REPO_DIR):
    shutil.rmtree(d, ignore_errors=True)
print("kept:", sorted(p.name for p in WORKING_DIR.iterdir()))
