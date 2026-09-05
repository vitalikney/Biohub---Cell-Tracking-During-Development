# --- exp10: clean pipeline submission: fine-tuned weights -> predict (ILP) -> postproc -> submission.csv ---
import csv, json, os, subprocess, sys, time, shutil
from pathlib import Path
E = os.environ.get
WEIGHTS_SUB = E("BIOHUB_WEIGHTS_SUB", "exp03B")
DET_THRESHOLD = E("BIOHUB_DET_THRESHOLD", "0.965")
ILP_ARGS = ["--use-ilp", "--ilp-edge-weight", "-1.0", "--ilp-appearance-weight", E("BIOHUB_ILP_APPEARANCE_WEIGHT", "0.0"),
            "--ilp-disappearance-weight", E("BIOHUB_ILP_DISAPPEARANCE_WEIGHT", "2"),
            "--ilp-division-weight", E("BIOHUB_ILP_DIVISION_WEIGHT", "1.2")]
PP = dict(gap_um=float(E("BIOHUB_PP_GAP_UM", "5.0")), max_gap=int(E("BIOHUB_PP_MAX_GAP", "1")),
          div_parent_um=float(E("BIOHUB_PP_DIV_PARENT_UM", "5.0")), div_sister_um=float(E("BIOHUB_PP_DIV_SISTER_UM", "12.0")),
          div_max_frac=float(E("BIOHUB_PP_DIV_MAX_FRAC", "0.01")), min_len=int(E("BIOHUB_PP_MIN_LEN", "0")))
VALIDATE = E("BIOHUB_SUBMIT_VALIDATE", "0") != "0"
HOLDOUT = json.loads(E("BIOHUB_HOLDOUT_JSON", "{}")).get("holdout", [])
N_GPU = int(E("BIOHUB_N_GPU", "2"))
SUBMISSION_PATH = WORKING_DIR / "submission.csv"

# ---- writable repo + weights ----
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
print("weights:", wsrc, (WDIR / "config.json").read_text(), flush=True)
ENV = {**os.environ, "PYTHONPATH": "src", "PYTHONUNBUFFERED": "1"}
SCORE_SCRIPT = '''
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
'''
(TRAIN_REPO / "scripts" / "score_holdout.py").write_text(SCORE_SCRIPT)


def predict(data_dir: Path, stems: list, method: str) -> list:
    splits_path = TRAIN_REPO / f"splits_{method}.json"
    splits_path.write_text(json.dumps([{"split": 0, "train": [], "test": stems}]))
    procs = []
    for g in range(N_GPU):
        cmd = [sys.executable, "scripts/predict_unet_transformer.py", "--data-dir", str(data_dir), "--splits", str(splits_path),
               "--split", "0", "--weights", str(WEIGHTS), "--method", f"{method}_gpu{g}", "--slice", f"{g}::{N_GPU}",
               "--det-threshold", DET_THRESHOLD, "--unet-batch-size", "4", *ILP_ARGS]
        procs.append(subprocess.Popen(cmd, cwd=TRAIN_REPO, env={**ENV, "CUDA_VISIBLE_DEVICES": str(g), "BIOHUB_DATA_DIR": str(data_dir)},
                                      stdout=open(WORKING_DIR / f"predict_{method}_gpu{g}.log", "w"), stderr=subprocess.STDOUT))
    t0 = time.time()
    for g, p in enumerate(procs):
        if p.wait() != 0:
            print((WORKING_DIR / f"predict_{method}_gpu{g}.log").read_text()[-3000:])
            raise RuntimeError(f"predict shard {g} failed for {method}")
    geffs = sorted((TRAIN_REPO / "predictions").rglob(f"{method}_gpu*/split_0/*.geff"))
    print(f"{method}: {len(geffs)} graphs in {(time.time()-t0)/60:.1f} min", flush=True)
    assert {g.stem for g in geffs} == set(stems), "missing predictions"
    return geffs


def postprocess(geffs: list, out_dir: Path) -> list:
    out_dir.mkdir(parents=True, exist_ok=True)
    outs = []
    t0 = time.time()
    for p in geffs:
        g = load(p)
        st = process(g, **PP)
        o = out_dir / p.name
        save(g, o); outs.append(o)
        print(f"  pp {p.stem}: {st}", flush=True)
    print(f"post-processing {len(outs)} graphs in {(time.time()-t0)/60:.1f} min", flush=True)
    return outs


# ---- optional self-check on holdout (train videos) ----
if VALIDATE and HOLDOUT:
    raw = predict(TRAIN_DIR, HOLDOUT, "val_raw")
    pp = postprocess(raw, WORKING_DIR / "val_pp")
    for name, gl in (("val_raw", raw), ("val_pp", pp)):
        out = WORKING_DIR / f"score_{name}.json"
        r = subprocess.run([sys.executable, "scripts/score_holdout.py", "--method", name, "--out", str(out), *map(str, gl)],
                           cwd=TRAIN_REPO, env={**ENV, "BIOHUB_DATA_DIR": str(TRAIN_DIR)}, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-1500:], r.stderr[-1500:])
        s = json.loads(out.read_text())["summary"]
        print(f"== {name}: score={s['score']:.4f} edge={s['edge_jaccard']:.4f} div={int(s['division_tp'])}/{int(s['division_fp'])}/{int(s['division_fn'])}", flush=True)
    shutil.rmtree(WORKING_DIR / "val_pp", ignore_errors=True)

# ---- test prediction + submission ----
test_stems = sorted(p.name[:-5] for p in TEST_DIR.iterdir() if p.name.endswith(".zarr"))
print("test videos:", len(test_stems), flush=True)
raw = predict(TEST_DIR, test_stems, "test")
pp = postprocess(raw, WORKING_DIR / "test_pp")

COLUMNS = ["id", "dataset", "row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"]
row_id = 0; n_nodes = 0; n_edges = 0
with open(SUBMISSION_PATH, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLUMNS); w.writeheader()
    for p in pp:
        g = load(p)
        ds = p.stem
        for n, d in sorted(g.nodes(data=True), key=lambda kv: (int(kv[1]["t"]), int(kv[0]))):
            w.writerow({"id": row_id, "dataset": ds, "row_type": "node", "node_id": int(n), "t": int(d["t"]),
                        "z": max(0, int(round(float(d["z"])))), "y": max(0, int(round(float(d["y"])))), "x": max(0, int(round(float(d["x"])))),
                        "source_id": -1, "target_id": -1}); row_id += 1; n_nodes += 1
        for u, v in g.edges():
            assert int(g.nodes[v]["t"]) == int(g.nodes[u]["t"]) + 1
            w.writerow({"id": row_id, "dataset": ds, "row_type": "edge", "node_id": -1, "t": -1, "z": -1, "y": -1, "x": -1,
                        "source_id": int(u), "target_id": int(v)}); row_id += 1; n_edges += 1
print(f"wrote {SUBMISSION_PATH}: {n_nodes} nodes, {n_edges} edges, {row_id} rows", flush=True)
import pandas as pd
df = pd.read_csv(SUBMISSION_PATH)
assert list(df.columns) == COLUMNS and df["id"].tolist() == list(range(len(df)))
assert set(df["dataset"].unique()) == set(test_stems)
print(df.head(6).to_string())
for d in (TRAIN_REPO, REPO_DIR, WORKING_DIR / "test_pp"):
    shutil.rmtree(d, ignore_errors=True)
print("done; kept:", sorted(p.name for p in WORKING_DIR.iterdir()))
