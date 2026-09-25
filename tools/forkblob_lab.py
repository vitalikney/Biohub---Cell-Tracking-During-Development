"""forkblob lab arm (ideas workflow v4 L1; rule and harm gate frozen in CONTEXT.md PRE-REGISTRATION v3 ADDENDUM L4,
25 Sep 18:20 UTC, before any exp60 output was on disk). CPU only; reads the exp60 trainlab dumps + the local train zarrs.

    python tools/forkblob_lab.py score --dumps <exp60 output dir> [<dir> ...] [--workers 3]
        [--split experiments/exp60_trainlab/split.json] [--train-dir biohub-cell-tracking-during-development/train]
        [--out experiments/exp60_trainlab/forkblob]           -> <out>.json + <out>.md
    python tools/forkblob_lab.py dummy --csv _dl/biohub-exp56-x138-verbatim/submission.csv
        [--zarr-dir biohub-cell-tracking-during-development/test]   (how many dummy forks the rule flags)

The rule is the kernel's own code: FORKBLOB_FN of tools/build_probe_kernel.py (--patch forkblob) is exec'd here and
forkblob_edges() runs with a zarr frame reader instead of the notebook's read_test_frame. Scoring uses the helpers of
tools/trainlab.py (official_eval = the official metric rows, summarise_rows, the lab's forkmid copy); that file is
imported, never edited.

Arms (on the kernel's final graph = trainlab 'control'):
  forkblob            forkblob on control (the gated arm)
  forkmid45_forkblob  info only: forkblob after trainlab's forkmid 4.5 um (the K3 order forkmid -> forkblob)
Harm gate (L4, pooled over the 56 lab clips): vetoed evaluable TP <= 1 and (TP == 0 or FP >= 3 TP) (division labels
of the control graph); pooled div_J(arm) >= control; dose = vetoed / control safe-division forks >= 10%; pooled
adj_edge delta >= -0.0002; nodes unchanged. Log per vetoed fork: dropped edge, its edge label, the fork's label.
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import io
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_probe_kernel as bpk  # noqa: E402
import trainlab as tl  # noqa: E402
import trainlab_io as tio  # noqa: E402

TRAIN_DIR = ROOT / "biohub-cell-tracking-during-development/train"
TEST_DIR = ROOT / "biohub-cell-tracking-during-development/test"
OUT = ROOT / "experiments/exp60_trainlab/forkblob"
ARMS = ("control", "forkblob", "forkmid45_forkblob")
GATED = "forkblob"
DOSE_MIN = 0.10
ADJ_EDGE_MIN_DELTA = -0.0002


def forkblob_namespace() -> dict:
    """FORKBLOB_FN exec'd as the kernel does (its knob line printed nowhere); the pure functions are what we need."""
    ns: dict = {"os": os, "np": np, "VOXEL_SCALE_UM": tuple(tl.SCALE_UM)}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(bpk.FORKBLOB_FN, "FORKBLOB_FN", "exec"), ns)
    return ns


class ZarrFrames:
    """read_frame(t) over <stem>.zarr/0 with a small LRU (forkblob asks for t+1 of each close fork)."""

    def __init__(self, zarr_path: Path, keep: int = 4):
        import zarr
        self.arr = zarr.open(str(Path(zarr_path) / "0"), mode="r")
        self.keep, self.cache, self.reads = keep, collections.OrderedDict(), 0

    def __call__(self, t: int) -> np.ndarray:
        t = int(t)
        if t in self.cache:
            self.cache.move_to_end(t)
            return self.cache[t]
        frame = np.asarray(self.arr[t])
        self.reads += 1
        self.cache[t] = frame
        while len(self.cache) > self.keep:
            self.cache.popitem(last=False)
        return frame


def edge_labels(nodes: dict, edges: list, gt_geff: Path) -> dict:
    """(source, target) -> 'TP' (matched GT edge) / 'FP' (valid, unmatched) / 'ignored' (not counted by the metric),
    from the official matching of the writer's rounded graph (the same construction as trainlab.official_eval)."""
    import polars as pl
    import score_geffs as sg  # puts tools/official on sys.path
    import tracksdata as td
    from tracking_cellmot import metrics as M

    gt, scale = sg._load_gt_and_scale(Path(gt_geff))
    g = td.graph.IndexedRXGraph()
    for key in ("z", "y", "x"):
        g.add_node_attr_key(key, pl.Float64, 0.0)
    ids = sorted(int(i) for i in nodes)
    if ids:
        g.bulk_add_nodes([{"t": int(nodes[i]["t"]), "z": float(max(0, int(round(float(nodes[i]["z"]))))),
                           "y": float(max(0, int(round(float(nodes[i]["y"]))))),
                           "x": float(max(0, int(round(float(nodes[i]["x"])))))} for i in ids], indices=ids)
    if edges:
        g.bulk_add_edges([{"source_id": int(e["source_id"]), "target_id": int(e["target_id"])} for e in edges])
    M._evaluate(g, gt, "jaccard", scale, 7.0)
    out = {}
    if g.num_edges() == 0:
        return out
    ea = M._evaluate_matched_graph(g, gt)
    k = td.DEFAULT_ATTR_KEYS
    for row in ea.select(k.EDGE_SOURCE, k.EDGE_TARGET, k.MATCHED_EDGE_MASK, "pred_valid").iter_rows():
        out[(int(row[0]), int(row[1]))] = "TP" if row[2] else ("FP" if row[3] else "ignored")
    return out


def lab_clip(task: dict) -> dict:
    """task: stem, dump (trainlab npz), zarr (train <stem>.zarr), gt (.geff or None), half."""
    t0 = time.time()
    stem = task["stem"]
    ns = forkblob_namespace()
    dump = tio.trainlab_load(task["dump"])
    control = tl.copy_graph(dump["final"])
    nodes = control[0]
    before = tl.float_digest(nodes, [])
    frames = ZarrFrames(Path(task["zarr"]))
    fb_edges, counters, vetoed = ns["forkblob_edges"](nodes, control[1], frames)
    fm_edges, _ = tl.forkmid(nodes, control[1])
    fb2_edges, counters2, vetoed2 = ns["forkblob_edges"](nodes, fm_edges, frames)
    graphs = {"control": control, "forkblob": (nodes, fb_edges), "forkmid45_forkblob": (nodes, fb2_edges)}
    out: dict = {"stem": stem, "embryo": stem[:4], "half": task.get("half"), "counters": counters,
                 "counters_after_forkmid": counters2, "frames_read": frames.reads,
                 "nodes_unchanged": tl.float_digest(nodes, []) == before and len(nodes) == len(dump["final"][0]),
                 "vetoed": vetoed, "vetoed_after_forkmid": vetoed2}
    arms: dict = {}
    if task.get("gt"):
        scored: dict = {}
        for arm, (n, e) in graphs.items():
            dig = tl.writer_digest(n, e)
            if dig not in scored:
                scored[dig] = tl.official_eval(n, e, Path(task["gt"]))
            row, tpf, fpf = scored[dig]
            arms[arm] = {"row": row, "nodes": len(n), "edges": len(e), "forks": len(tl.forks_of(e)),
                         "tp_forks_n": len(tpf), "fp_forks_n": len(fpf)}
            if arm == "control":
                ctp, cfp = set(tpf), set(fpf)
        labels = edge_labels(nodes, control[1], Path(task["gt"])) if vetoed or vetoed2 else {}
        for v in vetoed + vetoed2:
            v["div_label"] = "TP" if v["parent"] in ctp else ("FP" if v["parent"] in cfp else "ignored")
            v["edge_label"] = labels.get(tuple(v["dropped"]), "ignored")
    else:
        for arm, (n, e) in graphs.items():
            arms[arm] = {"nodes": len(n), "edges": len(e), "forks": len(tl.forks_of(e))}
    out["arms"] = arms
    out["seconds"] = round(time.time() - t0, 1)
    return out


def _pooled(results: list[dict], arm: str, emb: str | None = None) -> dict | None:
    rows = [r["arms"][arm]["row"] for r in results if "row" in r["arms"].get(arm, {})
            and (emb is None or r["embryo"] == emb)]
    if not rows:
        return None
    s = tl.summarise_rows(rows)
    s["clips"] = len(rows)
    s["nodes"] = sum(r["arms"][arm]["nodes"] for r in results if emb is None or r["embryo"] == emb)
    return s


def harm_gate(results: list[dict], n_expected: int, missing: list) -> dict:
    """ADDENDUM L4 harm gate on the pooled lab clips (all embryos together)."""
    c, a = _pooled(results, "control"), _pooled(results, GATED)
    vet = [v for r in results for v in r["vetoed"]]
    tp = sum(1 for v in vet if v.get("div_label") == "TP")
    fp = sum(1 for v in vet if v.get("div_label") == "FP")
    seen = sum(r["counters"]["forkblob_forks_seen"] for r in results)
    dose = len(vet) / seen if seen else 0.0
    d_adj = None if c is None or a is None else a["adj_edge_jaccard"] - c["adj_edge_jaccard"]
    checks = {
        "clips_complete": not missing and len(results) == n_expected,
        "vetoed_evaluable_tp_le_1": tp <= 1,
        "tp0_or_fp_ge_3tp": tp == 0 or fp >= 3 * tp,
        "div_J_arm_ge_control": c is not None and a is not None and a["division_jaccard"] >= c["division_jaccard"],
        "dose_ge_10pct": dose >= DOSE_MIN,
        "adj_edge_delta_ge_-0.0002": d_adj is not None and d_adj >= ADJ_EDGE_MIN_DELTA,
        "nodes_unchanged": all(r["nodes_unchanged"] for r in results)
                           and all(r["arms"][GATED]["nodes"] == r["arms"]["control"]["nodes"] for r in results),
    }
    return {"pass": all(checks.values()), "checks": checks,
            "vetoed": len(vet), "vetoed_tp": tp, "vetoed_fp": fp,
            "vetoed_ignored": sum(1 for v in vet if v.get("div_label") == "ignored"),
            "dropped_edge_labels": dict(collections.Counter(v.get("edge_label") for v in vet)),
            "control_safe_division_forks": seen, "dose": dose,
            "div_J": {"control": None if c is None else c["division_jaccard"],
                      "arm": None if a is None else a["division_jaccard"]},
            "adj_edge": {"control": None if c is None else c["adj_edge_jaccard"],
                         "arm": None if a is None else a["adj_edge_jaccard"], "delta": d_adj},
            "score_delta": None if c is None or a is None else a["score"] - c["score"],
            "rule": ("ADDENDUM L4, pooled lab clips: vetoed evaluable TP <= 1 and (TP == 0 or FP >= 3 TP); pooled div_J(arm)"
                     " >= control; dose >= 10% of control safe-division forks; pooled adj_edge delta >= -0.0002; "
                     "nodes unchanged")}


def aggregate(results: list[dict]) -> dict:
    agg: dict = {}
    for arm in ARMS:
        agg[arm] = {}
        for emb in (None, *tl.EMBRYOS):
            s = _pooled(results, arm, emb)
            if s is None:
                continue
            c = _pooled(results, "control", emb)
            s["delta"] = s["score"] - c["score"]
            s["delta_adj_edge"] = s["adj_edge_jaccard"] - c["adj_edge_jaccard"]
            s["delta_div_J"] = s["division_jaccard"] - c["division_jaccard"]
            agg[arm][emb or "POOLED"] = s
    return agg


def _f(x, nd=4, sign=False):
    if x is None or (isinstance(x, float) and x != x):
        return "-"
    return (f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}") if isinstance(x, float) else str(x)


def report_md(res: dict) -> str:
    g = res.get("gate", {})
    L = ["# forkblob lab arm (ADDENDUM L4) on the exp60 dumps", "",
         f"Generated by `tools/forkblob_lab.py score` at {res['generated_utc']} UTC from {res['n_clips']} clips "
         f"(expected {res['n_expected']}); missing dumps: {res['missing'] or 'none'}; missing zarrs: "
         f"{res['missing_zarr'] or 'none'}.", ""]
    if g:
        L += [f"## Harm gate: pass = **{g['pass']}**", "", g["rule"], "",
              "| check | ok |", "|---|---|"] + [f"| {k} | {v} |" for k, v in g["checks"].items()]
        L += ["", f"vetoed {g['vetoed']} (TP {g['vetoed_tp']}, FP {g['vetoed_fp']}, ignored {g['vetoed_ignored']}); "
                  f"control safe-division forks {g['control_safe_division_forks']}; dose {_f(g['dose'], 3)}; "
                  f"dropped edges {g['dropped_edge_labels']}; div_J {g['div_J']}; adj_edge delta "
                  f"{_f(g['adj_edge']['delta'], 5, True)}; score delta {_f(g['score_delta'], 5, True)}", ""]
        L += ["## Arms (score = adj edge J + 0.1 div J; delta vs control)", "",
              "| arm | group | clips | score | delta | adj edge d | div J | div J d | div TP/FP/FN |", "|---|---|---|---|---|---|---|---|---|"]
        for arm, groups in res["aggregate"].items():
            for key, s in groups.items():
                L.append(f"| {arm} | {key} | {s['clips']} | {_f(s['score'])} | {_f(s['delta'], 4, True)} | "
                         f"{_f(s['delta_adj_edge'], 5, True)} | {_f(s['division_jaccard'])} | {_f(s['delta_div_J'], 4, True)} | "
                         f"{s['division_tp']}/{s['division_fp']}/{s['division_fn']} |")
    L += ["", "## Vetoed forks (forkblob on control)", "",
          "| clip | parent | t | dropped edge | side | sister um | valley | edge label | fork label |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in res["clips"]:
        for v in r["vetoed"]:
            L.append(f"| {r['stem']} | {v['parent']} | {v['t']} | {v['dropped'][0]}->{v['dropped'][1]} | {v['side']} | "
                     f"{v['sister_um']} | {v['valley']} | {v.get('edge_label', '-')} | {v.get('div_label', '-')} |")
    return "\n".join(L) + "\n"


def cmd_score(a) -> None:
    split = json.loads(Path(a.split).read_text(encoding="utf-8"))
    stems = [s for s in split["stems"] if not a.only or s in set(a.only.split(","))]
    roots = [Path(p) for p in a.dumps]
    tasks, missing, missing_zarr = [], [], []
    for s in stems:
        dump = tl.find_files(roots, "trainlab", s)
        zp = Path(a.train_dir) / f"{s}.zarr"
        if dump is None:
            missing.append(s)
            continue
        if not zp.is_dir():
            missing_zarr.append(s)
            continue
        tasks.append({"stem": s, "dump": str(dump), "zarr": str(zp), "half": split["half_of"].get(s),
                      "gt": None if a.no_score else str(Path(a.train_dir) / f"{s}.geff")})
    print(f"{len(tasks)} clips with dumps + zarrs; missing dumps {missing}; missing zarrs {missing_zarr}", flush=True)
    if a.workers > 1:
        from multiprocessing import Pool
        with Pool(a.workers) as pool:
            results = pool.map(lab_clip, tasks, chunksize=1)
    else:
        results = []
        for t in tasks:
            results.append(lab_clip(t))
            r = results[-1]
            print(f"  {r['stem']}: forks {r['counters']['forkblob_forks_seen']} close {r['counters']['forkblob_close']}"
                  f" vetoed {len(r['vetoed'])} {r['seconds']}s", flush=True)
    res = {"generated_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), "n_clips": len(results),
           "n_expected": len(stems), "missing": missing, "missing_zarr": missing_zarr,
           "rule": {"max_um": 5.0, "min_valley": 0.95, "sigma_zyx": [0.6, 1.5, 1.5], "samples": 41,
                    "source": "tools/build_probe_kernel.py FORKBLOB_FN (exec'd)"}}
    if not a.no_score:
        res["aggregate"] = aggregate(results)
        res["gate"] = harm_gate(results, len(stems), missing + missing_zarr)
    res["clips"] = results
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    out.with_suffix(".md").write_text(report_md(res), encoding="utf-8")
    if "gate" in res:
        print("GATE", json.dumps({k: res["gate"][k] for k in ("pass", "checks", "vetoed", "vetoed_tp", "vetoed_fp",
                                                              "dose")}, default=str), flush=True)
    print("wrote", out.with_suffix(".json"), flush=True)


def csv_graphs(csv_path: Path) -> dict:
    """submission.csv -> {dataset: (nodes_by_id, edges)}. The CSV carries no edge flags: every 2-child fork is taken as
    a safe-division fork (x138: every fork comes from add_safe_divisions_postlink; a K2 CSV also holds DaughterNet
    forks, which it cannot tell apart), its second edge in file order marked safe_division = 1."""
    import pandas as pd
    df = pd.read_csv(csv_path)
    out = {}
    for ds, d in df.groupby("dataset", sort=True):
        nd = d[d.row_type == "node"]
        nodes = {int(r.node_id): {"t": int(r.t), "z": float(r.z), "y": float(r.y), "x": float(r.x)}
                 for r in nd.itertuples()}
        edges = [{"source_id": int(r.source_id), "target_id": int(r.target_id), "edge_prob": None}
                 for r in d[d.row_type == "edge"].itertuples()]
        seen: dict = {}
        for e in edges:
            seen[e["source_id"]] = seen.get(e["source_id"], 0) + 1
            if seen[e["source_id"]] == 2:
                e["safe_division"] = 1
        out[str(ds)] = (nodes, edges)
    return out


def cmd_dummy(a) -> None:
    ns = forkblob_namespace()
    total = {"forks": 0, "close": 0, "flagged": 0}
    rows = []
    for ds, (nodes, edges) in csv_graphs(Path(a.csv)).items():
        kept, c, vetoed = ns["forkblob_edges"](nodes, edges, ZarrFrames(Path(a.zarr_dir) / f"{ds}.zarr"))
        total["forks"] += c["forkblob_forks_seen"]
        total["close"] += c["forkblob_close"]
        total["flagged"] += c["forkblob_removed"]
        print(f"{ds}: forks {c['forkblob_forks_seen']} close(<=5um) {c['forkblob_close']} flagged {c['forkblob_removed']}"
              f" skipped {c['forkblob_skipped']}")
        rows += [dict(v, dataset=ds) for v in vetoed]
    for v in rows:
        print(f"  {v['dataset']} parent {v['parent']} t {v['t']} sister_um {v['sister_um']} valley {v['valley']}")
    print("TOTAL", json.dumps(total))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("score")
    c.add_argument("--dumps", nargs="+", required=True, help="downloaded exp60 kernel output folder(s)")
    c.add_argument("--split", default=str(tl.SPLIT_OUT))
    c.add_argument("--train-dir", default=str(TRAIN_DIR))
    c.add_argument("--out", default=str(OUT))
    c.add_argument("--workers", type=int, default=1)
    c.add_argument("--only", default="", help="comma-separated stems")
    c.add_argument("--no-score", action="store_true", help="counts and vetoed forks only (no GT)")
    d = sub.add_parser("dummy")
    d.add_argument("--csv", default=str(ROOT / "_dl/biohub-exp56-x138-verbatim/submission.csv"))
    d.add_argument("--zarr-dir", default=str(TEST_DIR))
    a = ap.parse_args()
    cmd_score(a) if a.cmd == "score" else cmd_dummy(a)


if __name__ == "__main__":
    main()
