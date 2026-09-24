"""Build the MOTION_RELINK_TIGHT_UM = 5.5 variant of friend A's cache (the value the exp39 kernel ships).

WHY
    friend A's ckpt/<stem>.npz were produced by the exp29 notebook with its default MOTION_RELINK_TIGHT_UM = 6.0
    (edge_anatomy reproduces every ckpt with 6.0), while the exp39 kernel sets BIOHUB_MOTION_RELINK_TIGHT_UM=5.5
    (cell 0).  The rest of the post-processing is identical (the exp29 and exp39 notebooks differ only in that knob and
    the DivNet veto inside add_safe_divisions_postlink, which is downstream of the ckpt).

WHAT (per video, <= 4 worker processes)
    1. raw/<stem>.geff -> the notebook's OWN filter_output_graph (exp29 cells via tools/public_local.py, the namespace
       friend C's runner builds), with the switches pass1_extras.py used to write the ckpt: safe divisions,
       short-track filter, linefit and prune-isolated OFF; motion relink, gap closing, gap2 recovery ON.  Synthetic
       gap points are refined on the local train frames (TEST_DIR = train dir), exactly like the pass-1 kernel.
    2. DeepCenter gap veto (close_single_frame_gaps -> deepcenter_accept_repair_point) needs the DeepCenter heatmap
       at the synthetic gap point; dc/ only holds scores at raw nodes and the model is not local.  The veto answer is
       an ORACLE keyed by (t, refined point): first the 6.0 run is replayed with answers read from friend A's 6.0 ckpt
       (accepted <=> a gap_synthetic node exists at that point), and the 6.0 replay must reproduce the ckpt EXACTLY
       (node ids, float32 coordinates, edge list, probabilities, every stats counter) - that validates the oracle and
       the whole code path.  The 5.5 run reuses the 6.0 answer for every point the 6.0 run also queried (same end/start
       pair -> same refined point -> same DeepCenter score); a point the 6.0 run never queried is UNKNOWN and gets
       --dc-unknown (default accept = the notebook's own behaviour when the score is missing).  Unknown points are
       listed per video in build/<stem>.json.
    3. The 5.5 ckpt is written in friend A's format (node_id, tzyx_syn float32, src, dst, edge_prob float32, stats).
    dc/ and raw/ are copied unchanged (the relink does not touch raw nodes; dc/ keys raw node ids only, so the
    replay's gap2 flag = not raw and not gap_synthetic stays correct).
    4. divnet/: friend A scored every parent of pass2_rank_divisions.candidates(15 um, k=64, steal) on the 6.0 ckpt.
       On the 5.5 ckpt the same pool (plus the replay's divnet_rerank pool, 12 um radius add) is rebuilt; raw parents
       reuse friend A's score (same node id = same position), synthetic parents reuse it when a 6.0 synthetic node
       sits at the identical (t, z, y, x); the rest are scored here on CPU with tools/divnet_infer.py and the same
       checkpoint (external/giorgosi__biohub-divnet-v2/best_overall.pt).  A sample of old parents is re-scored on CPU
       to measure the CPU-vs-friend-A difference.

USAGE
    python experiments/l2_daughternet/relink55/build_t55_cache.py ckpt --workers 4
    python experiments/l2_daughternet/relink55/build_t55_cache.py divnet --workers 4
    python experiments/l2_daughternet/relink55/build_t55_cache.py summary
    (--stems A B for a smoke test; finished videos are skipped on relaunch)
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
import os
import shutil
import sys
import time
import warnings
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC_CACHE = ROOT / "data_external" / "friend_a_cache" / "friend_a_b20_exp29_friend_c" / "cache" / "friend_a_b20_exp29"
DST_ROOT = ROOT / "data_external" / "friend_a_cache_t55"
DST_CACHE = DST_ROOT / "cache" / "friend_a_b20_exp29_t55"
BUILD_DIR = DST_ROOT / "build"
EXP39_NOTEBOOK = ROOT / "experiments" / "exp39_sjlee947_tight55_divnetveto" / "exp39-sjlee947-tight55-divnetveto.ipynb"
DIVNET_CKPT = ROOT / "external" / "giorgosi__biohub-divnet-v2" / "best_overall.pt"
BUILD_VERSION = 1

for _p in (ROOT / "tools", ROOT / "experiments" / "local_friend_b_exp02_public_port"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# switches of pass1_extras.py (ckpt = input of the division stage) + the stages friend C's tail namespace disables
CKPT_SWITCHES = {
    "OUTPUT_SAFE_DIVISIONS": False, "OUTPUT_FILTER_SHORT_TRACKS": False, "OUTPUT_LINEFIT_SMOOTH": False,
    "OUTPUT_PRUNE_ISOLATED": False, "OUTPUT_MOTION_RELINK": True, "OUTPUT_GAP_CLOSE": True,
    "OUTPUT_GAP2_RECOVERY": True, "USE_DEEPCENTER_VETO": True, "REQUIRE_DEEPCENTER_VETO": False,
}
# constants that must equal the exp39 kernel's resolved values (checked in `ckpt` against the exp39 notebook cells)
CHECK_KEYS = (
    "OUTPUT_EDGE_MAX_UM", "OUTPUT_ENFORCE_NEXT_FRAME", "OUTPUT_SINGLE_PARENT_REPAIR", "OUTPUT_SINGLE_CHILD_REPAIR",
    "MOTION_RELINK_RELAXED_UM", "MOTION_RELINK_VELOCITY_WEIGHT", "MOTION_RELINK_LEARNED_BONUS",
    "MOTION_RELINK_MAX_FRAME_NODES", "OUTPUT_DIVISION_GEOMETRY_FILTER", "OUTPUT_GAP_CLOSE", "GAP_CLOSE_MAX_GAP",
    "GAP_CLOSE_UM", "GAP_DENSITY_ADAPTIVE", "GAP_DENSITY_REFERENCE_UM", "GAP_DENSITY_GAIN",
    "GAP_DENSITY_MAX_STEP_DELTA_UM", "GAP_DENSITY_NEIGHBORS", "GAP_CLOSE_REUSE_EXISTING", "GAP_CLOSE_REUSE_UM",
    "GAP_CLOSE_MAX_ADDED_FRAC", "GAP_CLOSE_MAX_ADDED_ABS", "GAP_REFINE_SYNTHETIC", "GAP_REFINE_WIN_Z",
    "GAP_REFINE_WIN_YX", "GAP_REFINE_MAX_SHIFT_UM", "OUTPUT_GAP2_RECOVERY", "GAP2_MAX_TOTAL_UM", "GAP2_MAX_STEP_UM",
    "GAP2_MAX_LINKS_FRAC", "GAP2_MAX_LINKS_ABS", "GAP2_REQUIRE_CONTEXT", "GAP2_FRAME_FRAC_CAP",
    "DEEPCENTER_GAP_VETO", "DEEPCENTER_GAP_THRESHOLD", "DEEPCENTER_GAP_CONFIRM_MIN_SPAN_UM",
)


def _atomic_replace(tmp: Path, dst: Path) -> None:
    for attempt in range(30):
        try:
            os.replace(tmp, dst)
            return
        except PermissionError:
            if attempt == 29:
                raise
            time.sleep(min(0.05 * (attempt + 1), 1.0))


def atomic_npz(path: Path, **arrays) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.stem}.{os.getpid()}.tmp.npz")
    np.savez_compressed(tmp, **arrays)
    _atomic_replace(tmp, path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    _atomic_replace(tmp, path)


# ------------------------------------------------------------------------------------------------ notebook namespace
_W: dict = {}


def worker_ns(data_dir: str) -> dict:
    """friend C's tail namespace (exp29 cells, unpatched), built once per process."""
    if _W.get("data_dir") == data_dir:
        return _W["ns"]
    os.environ["BIOHUB_DATA_DIR"] = data_dir
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "friend_c_b31_runner", ROOT / "experiments" / "local_friend_c_b31_cluster" / "runner.py")
    fc = importlib.util.module_from_spec(spec)
    sys.modules["friend_c_b31_runner"] = fc
    spec.loader.exec_module(fc)
    shim = type("Cfg", (), {"output_dir": BUILD_DIR / "ns" / str(os.getpid()), "data_dir": Path(data_dir)})
    with contextlib.redirect_stdout(io.StringIO()):
        ns = fc._tail_namespace(shim)
    ns.update(CKPT_SWITCHES)
    if Path(ns["TEST_DIR"]).resolve() != Path(data_dir).resolve():
        raise RuntimeError(f"TEST_DIR {ns['TEST_DIR']} != {data_dir}")
    _W.clear()
    _W.update(data_dir=data_dir, ns=ns, fc=fc, original_accept=ns["deepcenter_accept_repair_point"])
    return ns


# Accelerated motion_relink_edges: the notebook's OWN source text (extracted from the exp29 post-processing cell) with
# one surgical change - the inner target loop of assign_pass only visits targets a KD-tree finds within gate + 1e-3 um.
# Every visited pair is computed by the unchanged notebook lines (same np.linalg.norm, same `raw > gate_um` test, same
# cost formula), every skipped pair has raw > gate_um and would have hit `continue`, so the cost / raw / motion / prob
# matrices and the linear_sum_assignment call are bit-identical.  Validated: (a) every video's 6.0 run with it must
# reproduce friend A's ckpt exactly (check60), (b) `verify55` re-runs the 5.5 videos that were built with the
# unmodified notebook function and requires identical ckpt arrays.
_RELINK_LOOP_OLD = "            for j, target_id in enumerate(target_ids):\n"
_RELINK_LOOP_NEW = ("            for j in sorted(_kd_tree.query_ball_point(source_pos, gate_um + 1e-3)):\n"
                    "                target_id = target_ids[j]\n")
_RELINK_TREE_ANCHOR = "        prob_matrix = np.zeros_like(cost)\n"
_RELINK_TREE_CODE = ("        prob_matrix = np.zeros_like(cost)\n"
                     "        _kd_tree = cKDTree(np.stack([position_um[_t] for _t in target_ids]))\n")


def fast_relink_source() -> str:
    import public_local as pl

    cells = pl.notebook_cells(pl.DEFAULT_NOTEBOOK)
    post = cells[pl.find_cell(cells, "def filter_output_graph", "def add_safe_divisions_postlink")]
    start = post.index("def motion_relink_edges(")
    stop = post.index("def close_single_frame_gaps(")
    src = post[start:stop]
    for old, new in ((_RELINK_LOOP_OLD, _RELINK_LOOP_NEW), (_RELINK_TREE_ANCHOR, _RELINK_TREE_CODE)):
        if src.count(old) != 1:
            raise RuntimeError(f"relink anchor not unique: {old!r}")
        src = src.replace(old, new)
    return src


def install_relink(ns: dict, fast: bool) -> None:
    if "notebook_motion_relink_edges" not in _W:
        _W["notebook_motion_relink_edges"] = ns["motion_relink_edges"]
        exec(compile(fast_relink_source(), "<notebook:motion_relink_edges+kdtree>", "exec"), ns)
        _W["fast_motion_relink_edges"] = ns["motion_relink_edges"]
    ns["motion_relink_edges"] = _W["fast_motion_relink_edges" if fast else "notebook_motion_relink_edges"]


def exp39_constants(data_dir: str) -> dict:
    """Resolved constants of the exp39 kernel notebook (env cell + constants cell), in a clean child process."""
    import public_local as pl

    for key in [k for k in os.environ if k.startswith("BIOHUB_") and k != "BIOHUB_DATA_DIR"]:
        os.environ.pop(key)
    cells = pl.notebook_cells(EXP39_NOTEBOOK)
    with contextlib.redirect_stdout(io.StringIO()):
        ns = pl.build_namespace(cells, ROOT / "tools" / "repo", BUILD_DIR / "ns" / "exp39", Path(data_dir))
    return {k: ns[k] for k in (*CHECK_KEYS, "MOTION_RELINK_TIGHT_UM")}


# ------------------------------------------------------------------------------------------------ graph I/O
def load_raw(stem: str) -> tuple[dict, list]:
    ns = _W["ns"]
    graph = ns["graph_from_geff"](SRC_CACHE / "raw" / f"{stem}.geff")
    nodes = {}
    for row in graph.node_attrs().iter_rows(named=True):
        i = int(row["node_id"])
        nodes[i] = {"node_id": i, "t": int(row["t"]), "z": float(row["z"]), "y": float(row["y"]), "x": float(row["x"])}
    edges = []
    for row in graph.edge_attrs().iter_rows(named=True):
        p = row.get("edge_prob") if hasattr(row, "get") else None
        edges.append({"source_id": int(row["source_id"]), "target_id": int(row["target_id"]),
                      "edge_prob": None if p is None else float(p)})
    return nodes, edges


def ckpt_arrays(nodes: dict, edges: list, stats: dict) -> dict:
    """Exactly pass1_extras.py's serialisation."""
    ids = np.array(sorted(nodes))
    arr = np.array([[nodes[i]["t"], nodes[i]["z"], nodes[i]["y"], nodes[i]["x"], int(nodes[i].get("gap_synthetic", 0))]
                    for i in ids], np.float32)
    src = np.array([e["source_id"] for e in edges])
    dst = np.array([e["target_id"] for e in edges])
    prob = np.array([np.nan if e.get("edge_prob") is None else float(e["edge_prob"]) for e in edges], np.float32)
    return {"node_id": ids, "tzyx_syn": arr, "src": src, "dst": dst, "edge_prob": prob,
            "stats": json.dumps({k: int(v) for k, v in stats.items()})}


def compare_ckpt(ours: dict, ref_path: Path) -> dict:
    with np.load(ref_path, allow_pickle=False) as ck:
        ref = {k: ck[k] for k in ck.files}
    out = {"node_ids_equal": bool(np.array_equal(ours["node_id"].astype(np.int64), ref["node_id"].astype(np.int64)))}
    out["tzyx_equal"] = bool(out["node_ids_equal"] and np.array_equal(ours["tzyx_syn"], ref["tzyx_syn"]))
    if out["node_ids_equal"] and not out["tzyx_equal"]:
        out["tzyx_max_abs"] = float(np.nanmax(np.abs(ours["tzyx_syn"] - ref["tzyx_syn"])))
    out["edges_equal"] = bool(len(ours["src"]) == len(ref["src"]) and np.array_equal(ours["src"], ref["src"])
                              and np.array_equal(ours["dst"], ref["dst"]))
    out["edge_set_equal"] = (set(zip(ours["src"].tolist(), ours["dst"].tolist()))
                             == set(zip(ref["src"].tolist(), ref["dst"].tolist())))
    out["prob_equal"] = bool(out["edges_equal"] and np.array_equal(ours["edge_prob"], ref["edge_prob"], equal_nan=True))
    so, sr = json.loads(ours["stats"]), json.loads(str(ref["stats"]))
    out["stats_diff"] = {k: (so.get(k), sr.get(k)) for k in sorted(set(so) | set(sr)) if so.get(k) != sr.get(k)}
    out["exact"] = bool(out["node_ids_equal"] and out["tzyx_equal"] and out["edges_equal"] and out["prob_equal"]
                        and not out["stats_diff"])
    out["ref_nodes"], out["ref_edges"] = int(len(ref["node_id"])), int(len(ref["src"]))
    return out


# ------------------------------------------------------------------------------------------------ DeepCenter oracle
DC_CKPT = ROOT / "external" / "pilkwang__biohub-deepcenter-unet3d-center-prior-v1" / "weights" / "full_frame_center" / "best.pt"


def load_dc_model(stem: str) -> dict:
    """DeepCenter decisions computed by the `dcmodel` phase for points the 6.0 run never queried."""
    path = BUILD_DIR / "dc_model" / f"{stem}.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {(int(p["t"]), float(p["z"]), float(p["y"]), float(p["x"])): bool(p["accepted"]) for p in data["points"]}


def dc_model_video(stem: str, settings: dict) -> dict:
    """Score the 5.5-only DeepCenter gap queries with the notebook's own loader / heatmap / point score (8-view TTA,
    BIOHUB_DEEPCENTER_TTA=1 as in the exp29/exp39 env cell), on CPU.  Validation in the same frames: the score at every
    raw node vs friend A's dc/ value (same heatmap, same patch max), the 6.0 queries' accept/reject decisions (when the
    side file carries the 6.0 log), and the accepted 6.0 synthetic points (score >= threshold)."""
    ns = worker_ns(settings["data_dir"])
    side = json.loads((BUILD_DIR / "videos" / f"{stem}.json").read_text(encoding="utf-8"))
    points = side.get("dc_new_points") or side.get("dc_unknown_points") or []
    if not points:
        return {"stem": stem, "points": 0}
    if "dc_bundle" not in _W:
        import torch

        torch.set_num_threads(int(settings.get("torch_threads", 4)))
        os.environ["BIOHUB_DEEPCENTER_CHECKPOINT"] = str(DC_CKPT)
        os.environ["BIOHUB_DEEPCENTER_TTA"] = "1"
        ns["USE_DEEPCENTER_VETO"] = True
        with contextlib.redirect_stdout(io.StringIO()):
            bundle = ns["load_deepcenter_veto_detector"]()
        if bundle is None or Path(bundle["path"]).resolve() != DC_CKPT.resolve():
            raise RuntimeError(f"DeepCenter checkpoint not loaded from {DC_CKPT}")
        _W["dc_bundle"] = bundle
    bundle = _W["dc_bundle"]
    thr = float(ns["DEEPCENTER_GAP_THRESHOLD"])
    wz, wyx = int(ns["DEEPCENTER_SCORE_WIN_Z"]), int(ns["DEEPCENTER_SCORE_WIN_YX"])
    pool = int(getattr(bundle["cfg"], "pool_factor", 4))
    raw_nodes, _ = load_raw(stem)
    with np.load(SRC_CACHE / "dc" / f"{stem}.npz", allow_pickle=False) as dc:
        dc_ref = {int(i): float(v) for i, v in zip(dc["node_id"], dc["dc"])}
    # accepted 6.0 synthetic points that were DeepCenter-checked (span >= confirm span)
    with np.load(SRC_CACHE / "ckpt" / f"{stem}.npz", allow_pickle=False) as ck:
        ids, rows, src, dst = ck["node_id"].tolist(), ck["tzyx_syn"], ck["src"].tolist(), ck["dst"].tolist()
    pos = {i: r for i, r in zip(ids, rows)}
    pred = {d: s for s, d in zip(src, dst)}
    succ = {s: d for s, d in zip(src, dst)}
    span_min = float(ns["DEEPCENTER_GAP_CONFIRM_MIN_SPAN_UM"])
    scale = np.asarray([1.625, 0.40625, 0.40625])
    acc60 = []
    for i, r in pos.items():
        if r[4] == 1 and i in pred and i in succ:
            a, b = pos[pred[i]], pos[succ[i]]
            if float(np.linalg.norm((np.asarray(a[1:4], float) - np.asarray(b[1:4], float)) * scale)) >= span_min:
                acc60.append((int(r[0]), (float(r[1]), float(r[2]), float(r[3]))))
    log60 = [(int(q[0]), (q[1], q[2], q[3]), bool(q[4])) for q in side.get("dc_log60", [])]
    frames = sorted({int(p["t"]) for p in points})
    out_points, raw_diff, raw_flip, v60 = [], [], 0, {"n": 0, "agree": 0}
    acc_check = {"n": 0, "ge_thr": 0}
    by_t: dict[int, list[int]] = {}
    for i, n in raw_nodes.items():
        by_t.setdefault(int(n["t"]), []).append(i)
    frame_cache: dict = {}
    heat_cache: dict = {}
    for t in frames:
        heat = ns["deepcenter_heatmap_for_frame"](stem, t, bundle, frame_cache, heat_cache)
        for p in points:
            if int(p["t"]) == t:
                s = ns["deepcenter_score_point"](stem, t, (p["z"], p["y"], p["x"]), bundle, frame_cache, heat_cache)
                out_points.append({"t": t, "z": p["z"], "y": p["y"], "x": p["x"], "score": s,
                                   "accepted": bool(s is None or s >= thr), "fallback_used": p.get("accepted")})
        for i in by_t.get(t, []):
            n = raw_nodes[i]
            z, y, x = int(round(n["z"])), int(round(n["y"] / pool)), int(round(n["x"] / pool))
            patch = heat[max(0, z - wz):z + wz + 1, max(0, y - wyx):y + wyx + 1, max(0, x - wyx):x + wyx + 1]
            v = float(patch.max()) if patch.size else -1.0
            if i in dc_ref:
                raw_diff.append(abs(v - dc_ref[i]))
                raw_flip += int((v >= thr) != (dc_ref[i] >= thr))
        for tt, pt, acc in log60:
            if tt == t:
                s = ns["deepcenter_score_point"](stem, t, pt, bundle, frame_cache, heat_cache)
                v60["n"] += 1
                v60["agree"] += int((s is not None and s >= thr) == acc)
        for tt, pt in acc60:
            if tt == t:
                s = ns["deepcenter_score_point"](stem, t, pt, bundle, frame_cache, heat_cache)
                acc_check["n"] += 1
                acc_check["ge_thr"] += int(s is not None and s >= thr)
        frame_cache.clear()
        heat_cache.clear()
    raw_diff = np.asarray(raw_diff)
    result = {"stem": stem, "threshold": thr, "points": out_points, "frames": len(frames),
              "validation": {"raw_nodes": int(len(raw_diff)),
                             "raw_max_abs": float(raw_diff.max()) if len(raw_diff) else None,
                             "raw_mean_abs": float(raw_diff.mean()) if len(raw_diff) else None,
                             "raw_threshold_flips": raw_flip, "log60": v60, "accepted60_points": acc_check}}
    atomic_text(BUILD_DIR / "dc_model" / f"{stem}.json", json.dumps(result, indent=1))
    return {"stem": stem, "points": len(out_points), "accepted": sum(p["accepted"] for p in out_points),
            "fallback_disagree": sum(p["accepted"] != p["fallback_used"] for p in out_points
                                     if p["fallback_used"] is not None),
            **result["validation"]}


def make_oracle(answer, log: list):
    """Drop-in for the notebook's deepcenter_accept_repair_point: same counters, answer from `answer(key)`."""
    def oracle(dataset, t, point, detector_bundle, frame_cache, heatmap_cache, stats, prefix, threshold):
        if prefix != "gap":
            raise RuntimeError(f"unexpected DeepCenter check {prefix!r} before the ckpt")
        key = (int(t), float(point[0]), float(point[1]), float(point[2]))
        stats[f"deepcenter_{prefix}_checked"] += 1
        accepted, source = answer(key)
        log.append((key, bool(accepted), source))
        stats[f"deepcenter_{prefix}_{'accepted' if accepted else 'rejected'}"] += 1
        return bool(accepted)
    return oracle


def run_ckpt(stem: str, nodes: dict, edges: list, tight_um: float, oracle) -> tuple[dict, list, dict]:
    ns = _W["ns"]
    ns.update(CKPT_SWITCHES)
    ns["MOTION_RELINK_TIGHT_UM"] = float(tight_um)
    ns["deepcenter_accept_repair_point"] = oracle
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            out_nodes, out_edges, stats = ns["filter_output_graph"](
                copy.deepcopy(nodes), copy.deepcopy(edges), dataset=stem, deepcenter_bundle={"oracle": True})
    finally:
        ns["deepcenter_accept_repair_point"] = _W["original_accept"]
    return out_nodes, out_edges, stats


def build_video(stem: str, settings: dict) -> dict:
    install_relink(worker_ns(settings["data_dir"]), bool(settings.get("fast_relink")))
    started = time.time()
    side_path = BUILD_DIR / "videos" / f"{stem}.json"
    out_path = DST_CACHE / "ckpt" / f"{stem}.npz"
    model_table = load_dc_model(stem)
    if side_path.is_file() and out_path.is_file() and not settings.get("verify"):
        side = json.loads(side_path.read_text(encoding="utf-8"))
        if (side.get("version") == BUILD_VERSION and side.get("dc_unknown") == settings["dc_unknown"]
                and int(side.get("dc_model_n", 0)) == len(model_table)):
            return side
    nodes, edges = load_raw(stem)

    # ---- 6.0 replay: DeepCenter answers read from friend A's ckpt; must reproduce it exactly
    with np.load(SRC_CACHE / "ckpt" / f"{stem}.npz", allow_pickle=False) as ck:
        ids, rows = ck["node_id"], ck["tzyx_syn"]
    syn60 = {(int(r[0]), float(r[1]), float(r[2]), float(r[3])) for i, r in zip(ids.tolist(), rows) if r[4] == 1}

    def answer60(key):
        k32 = (key[0], *(float(np.float32(v)) for v in key[1:]))
        return (k32 in syn60), "ckpt60"

    log60: list = []
    n60, e60, s60 = run_ckpt(stem, nodes, edges, 6.0, make_oracle(answer60, log60))
    a60 = ckpt_arrays(n60, e60, s60)
    check60 = compare_ckpt(a60, SRC_CACHE / "ckpt" / f"{stem}.npz")
    table = {}
    for key, acc, _src in log60:
        if key in table and table[key] != acc:
            raise RuntimeError(f"{stem}: DeepCenter oracle conflict at {key}")
        table[key] = acc

    # ---- 5.5 run: reuse every 6.0 answer; unknown points get the --dc-unknown policy
    policy = settings["dc_unknown"]

    def answer55(key):
        if key in table:
            return table[key], "reused60"
        if key in model_table:
            return model_table[key], "model"
        return (policy == "accept"), f"unknown_{policy}"

    log55: list = []
    n55, e55, s55 = run_ckpt(stem, nodes, edges, 5.5, make_oracle(answer55, log55))
    a55 = ckpt_arrays(n55, e55, s55)
    if settings.get("verify"):  # compare with the stored ckpt (built by the unmodified notebook relink); no writes
        with np.load(out_path, allow_pickle=False) as ck:
            same = {k: bool(np.array_equal(np.asarray(a55[k]), ck[k], equal_nan=(k == "edge_prob")))
                    for k in ("node_id", "tzyx_syn", "src", "dst", "edge_prob")}
            same["stats"] = json.loads(a55["stats"]) == json.loads(str(ck["stats"]))
        return {"stem": stem, "check60_exact": check60["exact"], "same55": same, "identical55": all(same.values()),
                "seconds": round(time.time() - started, 1)}
    atomic_npz(out_path, **a55)

    raw_ids = set(nodes)
    syn55 = sum(1 for n in n55.values() if n.get("gap_synthetic"))
    gap2_55 = sum(1 for i, n in n55.items() if i not in raw_ids and not n.get("gap_synthetic"))
    e60_set = set(zip(a60["src"].tolist(), a60["dst"].tolist()))
    e55_set = set(zip(a55["src"].tolist(), a55["dst"].tolist()))
    unknown = [{"t": k[0], "z": k[1], "y": k[2], "x": k[3], "accepted": acc} for k, acc, s in log55
               if s.startswith("unknown")]
    new_points = [{"t": k[0], "z": k[1], "y": k[2], "x": k[3], "accepted": acc, "source": s} for k, acc, s in log55
                  if s != "reused60"]
    side = {
        "version": BUILD_VERSION, "stem": stem, "dc_unknown": policy, "dc_model_n": len(model_table),
        "relink_impl": "notebook+kdtree_prefilter" if settings.get("fast_relink") else "notebook",
        "dc_new55": len(new_points), "dc_new_points": new_points,
        "dc_model_used55": sum(1 for _k, _a, s in log55 if s == "model"),
        "dc_log60": [[k[0], k[1], k[2], k[3], int(acc)] for k, acc, _s in log60],
        "check60": check60,
        "stats60": json.loads(a60["stats"]), "stats55": json.loads(a55["stats"]),
        "nodes60": int(len(a60["node_id"])), "nodes55": int(len(a55["node_id"])),
        "edges60": int(len(a60["src"])), "edges55": int(len(a55["src"])),
        "edges_common": len(e60_set & e55_set), "edges_only60": len(e60_set - e55_set),
        "edges_only55": len(e55_set - e60_set),
        "raw_nodes": len(raw_ids), "syn55": syn55, "gap2_55": gap2_55,
        "dc_queries60": len(log60), "dc_queries55": len(log55),
        "dc_reused55": sum(1 for _k, _a, s in log55 if s == "reused60"),
        "dc_unknown55": len(unknown), "dc_unknown_points": unknown,
        "seconds": round(time.time() - started, 1),
    }
    atomic_text(side_path, json.dumps(side, indent=1))
    return side


# ------------------------------------------------------------------------------------------------ DivNet
class FrameReader:
    """friend A's score_divnet_candidates.FrameReader (zarr, frame index clamped to the video)."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.arrays: dict = {}

    def __call__(self, dataset: str, t: int, frame_cache: dict) -> np.ndarray:
        import zarr

        if dataset not in self.arrays:
            self.arrays[dataset] = zarr.open(str(self.data_dir / f"{dataset}.zarr" / "0"), mode="r")
        array = self.arrays[dataset]
        index = max(0, min(int(t), int(array.shape[0]) - 1))
        if index not in frame_cache:
            frame_cache[index] = np.asarray(array[index])
        return frame_cache[index]


def divnet_video(stem: str, settings: dict) -> dict:
    import pass2_rank_divisions as p2

    started = time.time()
    side_path = BUILD_DIR / "divnet" / f"{stem}.json"
    out_path = DST_CACHE / "divnet" / f"{stem}.npz"
    if side_path.is_file() and out_path.is_file():
        side = json.loads(side_path.read_text(encoding="utf-8"))
        if side.get("version") == BUILD_VERSION and side.get("ckpt_mtime") == (DST_CACHE / "ckpt" / f"{stem}.npz").stat().st_mtime:
            return side
    nodes, edges, dcs, peak = p2.load_video(DST_CACHE, stem)
    parents: dict[int, int] = {}
    eligible: set[int] = set()  # parents the replay's divnet_rerank can rank (12 um add pool, sister >= 5 um, public gates)
    for mode, um, k in (("steal", 15.0, 64), ("add", 12.0, 0)):
        cands, _, _ = p2.candidates(nodes, edges, dcs, peak, um, k, mode)
        for parent, _c, _q, t, f in cands:
            parents.setdefault(int(parent), int(t))
            if mode == "add" and float(f[2]) >= 5.0 and p2.public_key(f) is not None:
                eligible.add(int(parent))
    # DivNet input = f(stem, t, parent coordinates): reuse friend A's score of any 6.0 parent at the identical
    # (t, z, y, x) (float32 ckpt coordinates; raw nodes keep id and position, synthetic ones may be renumbered)
    with np.load(SRC_CACHE / "divnet" / f"{stem}.npz", allow_pickle=False) as dv:
        old = {int(p): float(s) for p, s in zip(dv["p"], dv["score"])}
    with np.load(SRC_CACHE / "ckpt" / f"{stem}.npz", allow_pickle=False) as ck:
        old_by_pos = {(int(r[0]), float(r[1]), float(r[2]), float(r[3])): old[int(i)]
                      for i, r in zip(ck["node_id"].tolist(), ck["tzyx_syn"]) if int(i) in old}
    scores: dict[int, float] = {}
    source = {"reused_raw": 0, "reused_synthetic_by_position": 0, "cpu": 0}
    todo = []
    for parent, t in sorted(parents.items()):
        n = nodes[parent]
        key = (int(n["t"]), float(np.float32(n["z"])), float(np.float32(n["y"])), float(np.float32(n["x"])))
        if key in old_by_pos and int(n["t"]) == int(t):
            scores[parent] = old_by_pos[key]
            source["reused_raw" if parent in dcs else "reused_synthetic_by_position"] += 1
            continue
        todo.append((parent, t))
    if settings.get("dry_run"):
        frames = sorted({max(0, t + lag) for _p, t in todo for lag in (-1, 0, 1, 2)})
        return {"stem": stem, "parents": len(parents), "old_parents": len(old), **source, "todo": len(todo),
                "todo_raw": sum(1 for p, _t in todo if p in dcs), "todo_eligible": sum(1 for p, _t in todo if p in eligible),
                "eligible": len(eligible), "todo_frames": len(frames), "todo_eligible_ids": sorted(p for p, _t in todo if p in eligible),
                "seconds": round(time.time() - started, 1)}
    # CPU check sample: re-score up to N old raw parents to measure the CPU vs friend A (CUDA fp16 autocast) delta
    rng = np.random.default_rng(0)
    reused = [p for p in scores if p in dcs and p in old]
    sample = [(int(p), parents[int(p)]) for p in rng.choice(reused, size=min(settings["check_n"], len(reused)),
                                                            replace=False)] if reused else []
    cpu_scores = {}
    if todo or sample:
        import torch
        import divnet_infer as divnet

        torch.set_num_threads(max(1, int(settings.get("torch_threads", 1))))
        if "divnet_bundle" not in _W:
            _W["divnet_bundle"] = divnet.load_divnet_mitosis_model(DIVNET_CKPT)
            _W["reader"] = FrameReader(Path(settings["data_dir"]))
        bundle, reader = _W["divnet_bundle"], _W["reader"]
        bundle["prepared_frames"] = {}
        frame_cache: dict = {}
        jobs = todo + sample
        for start in range(0, len(jobs), 64):
            batch = jobs[start:start + 64]
            samples = [divnet.prepare_divnet_input(stem, t, nodes[p], bundle, frame_cache, reader) for p, t in batch]
            with torch.inference_mode():
                prob = torch.sigmoid(bundle["model"](torch.from_numpy(np.stack(samples)).float())).flatten().numpy()
            for (p, _t), v in zip(batch, prob.tolist()):
                cpu_scores[(p, _t)] = float(v)
        bundle["prepared_frames"] = {}
    for p, t in todo:
        scores[p] = cpu_scores[(p, t)]
        source["cpu"] += 1
    diffs = np.asarray([cpu_scores[(p, t)] - old[p] for p, t in sample], dtype=np.float64)
    flips = int(sum((cpu_scores[(p, t)] >= 0.5) != (old[p] >= 0.5) for p, t in sample))
    ids = np.array(sorted(scores), dtype=np.int64)
    atomic_npz(out_path, p=ids, score=np.array([scores[int(i)] for i in ids], dtype=np.float32))
    side = {"version": BUILD_VERSION, "stem": stem, "ckpt_mtime": (DST_CACHE / "ckpt" / f"{stem}.npz").stat().st_mtime,
            "parents": len(parents), "old_parents": len(old), **source,
            "cpu_ge_05": int(sum(scores[p] >= 0.5 for p, _t in todo)),
            "check_n": len(sample), "check_max_abs": float(np.abs(diffs).max()) if len(diffs) else None,
            "check_mean_abs": float(np.abs(diffs).mean()) if len(diffs) else None, "check_flips_05": flips,
            "seconds": round(time.time() - started, 1)}
    atomic_text(side_path, json.dumps(side, indent=1))
    return side


# ------------------------------------------------------------------------------------------------ driver
def _task(kind: str, stem: str, settings: dict) -> dict:
    if kind == "ckpt":
        return build_video(stem, settings)
    if kind == "dcmodel":
        return dc_model_video(stem, settings)
    return divnet_video(stem, settings)


def run_pool(kind: str, stems: list[str], settings: dict, workers: int) -> list[dict]:
    results = []
    started = time.time()
    if workers <= 1:
        for s in stems:
            results.append(_task(kind, s, settings))
            print(f"  {s} {results[-1].get('seconds')} s", flush=True)
        return results
    with ProcessPoolExecutor(max_workers=workers) as pool:
        pending = list(reversed(stems))
        running = set()
        while pending or running:
            while pending and len(running) < 2 * workers:
                running.add(pool.submit(_task, kind, pending.pop(), settings))
            done, running = wait(running, return_when=FIRST_COMPLETED)
            for fut in done:
                results.append(fut.result())
                n = len(results)
                if n % 10 == 0 or n == len(stems):
                    el = time.time() - started
                    print(f"  [{kind}] {n}/{len(stems)}  {el / 60:.1f} min  eta {el / n * (len(stems) - n) / 60:.1f} min",
                          flush=True)
    return results


def copy_static(stems: list[str]) -> None:
    for sub in ("dc", "raw"):
        (DST_CACHE / sub).mkdir(parents=True, exist_ok=True)
    for s in stems:
        dc_src, dc_dst = SRC_CACHE / "dc" / f"{s}.npz", DST_CACHE / "dc" / f"{s}.npz"
        if not dc_dst.is_file():
            shutil.copy2(dc_src, dc_dst)
        raw_src, raw_dst = SRC_CACHE / "raw" / f"{s}.geff", DST_CACHE / "raw" / f"{s}.geff"
        if not raw_dst.exists():
            shutil.copytree(raw_src, raw_dst)


def summary() -> dict:
    vids = sorted(BUILD_DIR.glob("videos/*.json"))
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in vids]
    dv = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(BUILD_DIR.glob("divnet/*.json"))]
    tot = lambda key, src=rows: int(sum(int(r.get(key) or 0) for r in src))  # noqa: E731
    stat_keys = ("motion_relink_edges", "motion_relink_tight_edges", "motion_relink_relaxed_edges", "gap_candidates",
                 "gap_pairs_selected", "gap_reused_existing", "gap_added_nodes", "gap_refined_synthetic",
                 "deepcenter_gap_checked", "deepcenter_gap_accepted", "deepcenter_gap_rejected",
                 "deepcenter_gap_bypassed_strong_motion", "gap2_candidates", "gap2_pairs_selected", "gap2_added_nodes")
    out = {
        "videos": len(rows),
        "check60_exact": sum(r["check60"]["exact"] for r in rows),
        "check60_failures": {r["stem"]: {k: v for k, v in r["check60"].items() if k != "exact"}
                             for r in rows if not r["check60"]["exact"]},
        "nodes60": tot("nodes60"), "nodes55": tot("nodes55"), "edges60": tot("edges60"), "edges55": tot("edges55"),
        "edges_common": tot("edges_common"), "edges_only60": tot("edges_only60"), "edges_only55": tot("edges_only55"),
        "stats60": {k: int(sum(r["stats60"].get(k, 0) for r in rows)) for k in stat_keys},
        "stats55": {k: int(sum(r["stats55"].get(k, 0) for r in rows)) for k in stat_keys},
        "dc_queries60": tot("dc_queries60"), "dc_queries55": tot("dc_queries55"), "dc_reused55": tot("dc_reused55"),
        "dc_new55": int(sum(int(r.get("dc_new55", r["dc_unknown55"])) for r in rows)),
        "dc_new_videos": sum(1 for r in rows if int(r.get("dc_new55", r["dc_unknown55"]))),
        "dc_model_used55": tot("dc_model_used55"),
        "dc_unknown55": tot("dc_unknown55"), "dc_unknown_videos": sum(1 for r in rows if r["dc_unknown55"]),
        "dc_unknown_policy": sorted({r["dc_unknown"] for r in rows}),
    }
    if dv:
        out["divnet"] = {"videos": len(dv), "parents": tot("parents", dv), "old_parents": tot("old_parents", dv),
                         "reused_raw": tot("reused_raw", dv),
                         "reused_synthetic_by_position": tot("reused_synthetic_by_position", dv),
                         "cpu_scored": tot("cpu", dv), "cpu_scored_ge_05": tot("cpu_ge_05", dv),
                         "check_n": tot("check_n", dv),
                         "check_max_abs": max((r["check_max_abs"] or 0.0) for r in dv),
                         "check_mean_abs": float(np.mean([r["check_mean_abs"] for r in dv if r["check_mean_abs"] is not None])),
                         "check_flips_05": tot("check_flips_05", dv)}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phase", choices=["ckpt", "verify55", "dcmodel", "divnet", "summary"])
    ap.add_argument("--fast-relink", action="store_true",
                    help="notebook relink source + KD-tree prefilter of the inner loop (bit-identical; see verify55)")
    ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dc-unknown", choices=["accept", "reject"], default="accept")
    ap.add_argument("--check-n", type=int, default=40, help="old DivNet parents re-scored on CPU per video")
    ap.add_argument("--dry-run", action="store_true", help="divnet: only count the parents that need a new score")
    ap.add_argument("--data-dir", default=str(ROOT / "biohub-cell-tracking-during-development" / "train"))
    a = ap.parse_args()
    if a.workers > 4:
        raise SystemExit("at most 4 workers")
    stems = list(a.stems) or sorted(p.stem for p in (SRC_CACHE / "ckpt").glob("*.npz"))
    settings = {"data_dir": str(Path(a.data_dir).resolve()), "dc_unknown": a.dc_unknown, "check_n": a.check_n,
                "torch_threads": 1 if a.workers > 1 else 4, "fast_relink": a.fast_relink,
                "dry_run": a.dry_run}
    if a.phase == "ckpt":
        # constants: our namespace (exp29 cells + ckpt switches + tight 5.5) vs the exp39 kernel's resolved values
        with ProcessPoolExecutor(max_workers=1) as pool:
            want = pool.submit(exp39_constants, settings["data_dir"]).result()
        ns = worker_ns(settings["data_dir"])
        ns["MOTION_RELINK_TIGHT_UM"] = 5.5
        diff = {k: (repr(ns[k]), repr(want[k])) for k in want if ns[k] != want[k]}
        print("exp39 constants:", {k: want[k] for k in ("MOTION_RELINK_TIGHT_UM", "GAP_CLOSE_UM",
                                                        "DEEPCENTER_GAP_THRESHOLD", "MOTION_RELINK_LEARNED_BONUS")},
              "| differences vs our namespace:", diff or "none", flush=True)
        if diff:
            raise SystemExit("namespace constants differ from the exp39 kernel")
        copy_static(stems)
        t0 = time.time()
        res = run_pool("ckpt", stems, settings, a.workers)
        bad = [r["stem"] for r in res if not r["check60"]["exact"]]
        print(f"ckpt: {len(res)} videos in {(time.time() - t0) / 60:.1f} min; 6.0 replay exact in "
              f"{len(res) - len(bad)}/{len(res)} (failures {bad[:5]}); DeepCenter unknown at 5.5: "
              f"{sum(r['dc_unknown55'] for r in res)} points in {sum(1 for r in res if r['dc_unknown55'])} videos",
              flush=True)
    elif a.phase == "verify55":
        # videos whose stored 5.5 ckpt was built with the UNMODIFIED notebook relink: rerun with --fast-relink in memory
        todo = [s for s in stems if (BUILD_DIR / "videos" / f"{s}.json").is_file() and json.loads(
            (BUILD_DIR / "videos" / f"{s}.json").read_text(encoding="utf-8")).get("relink_impl", "notebook") == "notebook"]
        res = run_pool("ckpt", todo, dict(settings, fast_relink=True, verify=True), a.workers)
        atomic_text(DST_ROOT / "verify55.json", json.dumps(res, indent=1))
        print(f"verify55: {len(res)} notebook-built videos re-run with the KD-tree relink: 6.0 exact "
              f"{sum(r['check60_exact'] for r in res)}/{len(res)}, 5.5 ckpt identical "
              f"{sum(r['identical55'] for r in res)}/{len(res)}", flush=True)
        return
    elif a.phase == "dcmodel":
        todo = []
        for s in stems:
            side = json.loads((BUILD_DIR / "videos" / f"{s}.json").read_text(encoding="utf-8"))
            if side.get("dc_new_points") or side.get("dc_unknown_points"):
                todo.append(s)
        print(f"dcmodel: {len(todo)} videos with 5.5-only DeepCenter queries", flush=True)
        res = run_pool("dcmodel", todo, settings, a.workers)
        atomic_text(DST_ROOT / "dc_model_summary.json", json.dumps(res, indent=1))
        tot = lambda k: sum(int(r.get(k) or 0) for r in res)  # noqa: E731
        print(json.dumps({"videos": len(res), "points": tot("points"), "accepted": tot("accepted"),
                          "fallback_disagree": tot("fallback_disagree"), "raw_nodes": tot("raw_nodes"),
                          "raw_max_abs": max((r.get("raw_max_abs") or 0) for r in res) if res else None,
                          "raw_threshold_flips": tot("raw_threshold_flips"),
                          "log60_n": sum(r["log60"]["n"] for r in res if "log60" in r),
                          "log60_agree": sum(r["log60"]["agree"] for r in res if "log60" in r),
                          "accepted60_n": sum(r["accepted60_points"]["n"] for r in res if "accepted60_points" in r),
                          "accepted60_ge_thr": sum(r["accepted60_points"]["ge_thr"] for r in res
                                                   if "accepted60_points" in r)}, indent=1), flush=True)
    elif a.phase == "divnet":
        missing = [s for s in stems if not (DST_CACHE / "ckpt" / f"{s}.npz").is_file()]
        if missing:
            raise SystemExit(f"{len(missing)} ckpt missing (run the ckpt phase first), e.g. {missing[:3]}")
        t0 = time.time()
        res = run_pool("divnet", stems, settings, a.workers)
        if a.dry_run:
            atomic_text(DST_ROOT / "divnet_dryrun.json", json.dumps(res, indent=1))
            keys = ("parents", "old_parents", "reused_raw", "reused_synthetic_by_position", "todo", "todo_raw",
                    "todo_eligible", "eligible", "todo_frames")
            print(json.dumps({k: int(sum(r[k] for r in res)) for k in keys} |
                             {"videos_with_todo": sum(1 for r in res if r["todo"]),
                              "videos_with_todo_eligible": sum(1 for r in res if r["todo_eligible"])}, indent=1))
            return
        print(f"divnet: {len(res)} videos in {(time.time() - t0) / 60:.1f} min; cpu-scored "
              f"{sum(r['cpu'] for r in res)} parents", flush=True)
    s = summary()
    atomic_text(DST_ROOT / "build_summary.json", json.dumps(s, indent=1))
    print(json.dumps({k: v for k, v in s.items() if k != "check60_failures"}, indent=1))
    if s["check60_failures"]:
        print("check60 failures (first 3):", json.dumps(dict(list(s["check60_failures"].items())[:3]), indent=1))


if __name__ == "__main__":
    main()
