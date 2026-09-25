"""exp60 x138 train lab, laptop side (research/wf_ideas_v3/TASK_CLOUD_SESSION.md T5; s_merge.json C06 + E05).

    python tools/trainlab.py split                     # writes experiments/exp60_trainlab/split.json (BEFORE any run)
    K="--base x138 --patch divinsert --patch safetail --patch trainlab --lab --set REPAIR_DEADLINE_S=40000
       --set DIVINS_DEADLINE_S=40000 --set DIVINS_ENABLE=1 --set DIVINS_STEAL=1 --set DIVINS_CAP=4 --set DIVINS_FRAME_CAP=1
       --set DIVINS_ALPHA=1 --set DIVINS_THRESH=1.5 --set DIVINS_DUMP=1 --set VALIDATOR_ENABLE=0"
    python tools/build_probe_kernel.py exp60_x138_trainlab_a $K --set TRAINLAB_SHARD=A         --train-stems @experiments/exp60_trainlab/split.json:A --out-dir exp60_trainlab/kernel_a
    python tools/build_probe_kernel.py exp60_x138_trainlab_b $K --set TRAINLAB_SHARD=B         --train-stems @experiments/exp60_trainlab/split.json:B --out-dir exp60_trainlab/kernel_b   [--owner sasyami         --out-dir exp60_trainlab/kernel_b_sasyami for friend A's account]
    python tools/trainlab.py score --dumps <dir> [<dir> ...] --nb experiments/exp60_trainlab/kernel_a/<nb>.ipynb \
        --train-dir biohub-cell-tracking-during-development/train --out experiments/exp60_trainlab/results [--workers 3]

The lab kernels (tools/build_probe_kernel.py --base x138 --patch divinsert --patch safetail --patch trainlab --lab)
write per train video /kaggle/working/trainlab/<stem>.npz (tools/trainlab_io.py: graph before the safe divisions,
graph before the short-track filter, final graph, the DeepCenter score of every safe-division candidate) and
divins_dump/<stem>.npz (DaughterNet p of every insertion candidate; dump-only, nothing inserted), plus the lowdet npz
(edge_cache/<stem>.npz). `score` replays the tail arms on CPU through the lab notebook's OWN functions (the lines of
filter_output_graph between the hooks, exec'd with the notebook's config cell), scores every arm with the official
metric (tools/official, the rows of tools/score_geffs.py) and writes <out>.json + <out>.md (small, committable).

Arms (pre-registered, FINAL_REPORT.md section e / TASK T5):
  control          the kernel's final graph (x138 + safetail, insertion dump-only = x138's output on the video)
  forkmid45        C04 on control: a safe-division fork (added edge safe_division == 1, not div_inserted) with
                   |P - (c1 + c2)/2| >= 4.5 um loses its ILP-side edge if that edge has edge_prob == 0.0, else the added
                   edge; nodes untouched (tools/trainlab.forkmid; the kernel patch is T6's)
  ins35            DaughterNet insertion with #35's config (steal 1, cap 4, frame cap 1, alpha 1, threshold 0.4) on
                   control, node p from the kernel's divins dump (tools/div_insert.insert_divisions)
  ins35_nosteal0   the same, but edges with edge_prob == 0.0 are never stolen
  ins35_forkmid45  (extra, for K3 = K2 + forkmid) forkmid after the insertion
  linefit_w07_win2 replay from the pre-short-track graph with OUTPUT_LINEFIT_WEIGHT 0.7, window 2
  dc0.15 .. dc0.35 replay from the pre-safe-division graph with DEEPCENTER_SAFE_DIV_THRESHOLD t (0.25 = x138 = control)
Parity: replaying the presafe dump at the kernel's own threshold and the preshort dump must give the kernel's final
graph (writer rows byte-identical; float coordinates reported too) - the lab's control gate.
44b6: one clip per leak group (split.json), so every GT division is counted once; checked again here.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import io
import json
import math
import os
import sys
import time
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import div_insert as dvi  # noqa: E402
import trainlab_io as tio  # noqa: E402

SPLITS = ROOT / "experiments/l2_daughternet/splits.json"
HEAD_REPORT = ROOT / "experiments/coordhead_retrain/out_full_P/report.json"
SPLIT_OUT = ROOT / "experiments/exp60_trainlab/split.json"
DUMMY_TWINS = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
SPLIT_SEED = 20260925
SPLIT_TOTAL = 56
SCALE_UM = (1.625, 0.40625, 0.40625)
FORKMID_UM = 4.5
DC_CONTROL = 0.25
DC_THRESHOLDS = (0.15, 0.20, 0.25, 0.30, 0.35)
INS35 = {"enable": 1, "steal": 1, "cap_video": 4, "cap_frame": 1, "alpha": 1.0, "threshold": 0.4}
LINEFIT_ARM = (0.7, 2)
ARMS = ("control", "forkmid45", "ins35", "ins35_nosteal0", "ins35_forkmid45", "linefit_w07_win2",
        "dc0.15", "dc0.20", "dc0.30", "dc0.35")
GROUPS = ("SELECTION", "CONFIRMATION", "ALL")
EMBRYOS = ("44b6", "6bba")
_MISSING = object()


def _h(*parts) -> str:
    return hashlib.sha256(":".join(str(p) for p in parts).encode("utf-8")).hexdigest()


# ------------------------------------------------------------------------------------------------------------------
# split (written to git BEFORE any run)
# ------------------------------------------------------------------------------------------------------------------
def make_split(total: int = SPLIT_TOTAL, seed: int = SPLIT_SEED) -> dict:
    sp = json.loads(SPLITS.read_text(encoding="utf-8"))
    div = {k: int(v) for k, v in sp["divisions_per_video"].items()}
    stems = sorted(sp["folds"])
    probable = list(json.loads(HEAD_REPORT.read_text(encoding="utf-8"))["x138_probable_train"])
    excluded = set(probable) | set(DUMMY_TWINS)
    grouped = {s for g in sp["meta"]["leak_groups"] for s in g}
    groups44 = [list(g) for g in sp["meta"]["leak_groups"]] + [[s] for s in stems
                                                                if s.startswith("44b6") and s not in grouped]
    chosen44, skipped_groups, group_of = [], [], {}
    for gi, g in enumerate(groups44):
        avail = [s for s in g if s not in excluded]
        if not avail:
            skipped_groups.append(g)
            continue
        pick = min(avail, key=lambda s: (-div[s], _h(seed, "rep", s)))
        chosen44.append(pick)
        group_of[pick] = gi
    n6 = total - len(chosen44)
    pool6 = [s for s in stems if s.startswith("6bba") and s not in excluded]
    chosen6 = sorted(pool6, key=lambda s: (-div[s], _h(seed, "6bba", s)))[:n6]
    halves = {"SELECTION": [], "CONFIRMATION": []}
    for lst in (chosen44, chosen6):  # half within each embryo, pairs of similar division count split by a coin
        order = sorted(lst, key=lambda s: (-div[s], _h(seed, "half", s)))
        for i in range(0, len(order), 2):
            pair = order[i:i + 2]
            first_sel = int(_h(seed, "pair", pair[0]), 16) % 2 == 0
            if len(pair) == 1:
                halves["SELECTION" if first_sel else "CONFIRMATION"].append(pair[0])
                continue
            halves["SELECTION"].append(pair[0] if first_sel else pair[1])
            halves["CONFIRMATION"].append(pair[1] if first_sel else pair[0])
    shards = {"A": [], "B": []}
    k = 0
    for lst in (chosen6, chosen44):  # snake A B B A over (embryo, -divisions): both embryos, similar event counts
        for s in sorted(lst, key=lambda s: (-div[s], _h(seed, "shard", s))):
            shards["AB"[k % 4 in (1, 2)]].append(s)
            k += 1
    shards = {k2: sorted(v) for k2, v in shards.items()}
    chosen = sorted(chosen44 + chosen6)
    return {
        "generator": "tools/trainlab.py split", "seed": seed, "total": len(chosen),
        "rule": ("44b6: one clip per leak group of experiments/l2_daughternet/splits.json (singletons = own group), the "
                 "member with most GT divisions (tie: sha256(seed:rep:stem)); 6bba: most GT divisions first (tie: "
                 "sha256(seed:6bba:stem)) up to the total; excluded: the 20 probable x138 head-training stems "
                 "(tools/train_coordhead.py x138_probable_train, out_full_P/report.json) and the 4 dummy train twins. "
                 "SELECTION/CONFIRMATION: within each embryo, stems ordered by (-divisions, sha256(seed:half:stem)), "
                 "consecutive pairs split by the parity of sha256(seed:pair:first). Shards: snake A,B,B,A over "
                 "(embryo, -divisions, sha256(seed:shard:stem))."),
        "stems": chosen,
        "embryo": {s: s[:4] for s in chosen},
        "divisions": {s: div[s] for s in chosen},
        "leak_group_44b6": {s: group_of[s] for s in chosen44},
        "halves": {k2: sorted(v) for k2, v in halves.items()},
        "half_of": {s: h for h, lst in halves.items() for s in lst},
        "shards": shards,
        "excluded": {"x138_probable_train": probable, "dummy_twins": list(DUMMY_TWINS)},
        "skipped_44b6_groups": skipped_groups,
        "summary": {
            emb: {"clips": sum(s.startswith(emb) for s in chosen),
                  "divisions": sum(div[s] for s in chosen if s.startswith(emb)),
                  **{h: {"clips": sum(s.startswith(emb) for s in halves[h]),
                         "divisions": sum(div[s] for s in halves[h] if s.startswith(emb))} for h in halves},
                  **{f"shard_{k2}": sum(s.startswith(emb) for s in shards[k2]) for k2 in shards}}
            for emb in EMBRYOS},
    }


# ------------------------------------------------------------------------------------------------------------------
# the lab notebook's own tail on CPU
# ------------------------------------------------------------------------------------------------------------------
def notebook_code_cells(nb_path: Path) -> list[str]:
    nb = json.loads(Path(nb_path).read_text(encoding="utf-8"))
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def cell_env(src: str) -> dict[str, str]:
    """Literal os.environ["K"] = "V" assignments of a cell (the preset + the builder's override block)."""
    env = {}
    for node in ast.parse(src).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
            continue
        tgt = node.targets[0]
        if (isinstance(tgt, ast.Subscript) and ast.unparse(tgt.value) == "os.environ"
                and isinstance(tgt.slice, ast.Constant) and isinstance(node.value, ast.Constant)):
            env[str(tgt.slice.value)] = str(node.value.value)
    return env


@contextlib.contextmanager
def patched_environ(env: dict):
    saved = dict(os.environ)
    os.environ.update(env)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(saved)


_SKIP_CALLS = {"load_deepcenter_veto_detector", "write_test_submission"}


def _calls(node: ast.AST) -> set[str]:
    return {n.func.id for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def tail_segment(post: str, start: str) -> str:
    """filter_output_graph's lines between the `start` hook and the final hook, as a function of the locals used."""
    from build_probe_kernel import trainlab_hook_line
    lines = post.splitlines(keepends=True)
    first = [i for i, ln in enumerate(lines) if ln == trainlab_hook_line(start)]
    last = [i for i, ln in enumerate(lines) if ln == trainlab_hook_line("final")]
    if len(first) != 1 or len(last) != 1 or not first[0] < last[0]:
        raise RuntimeError(f"lab notebook: hook lines {start}/final not found exactly once ({first}, {last})")
    body = "".join(lines[first[0] + 1:last[0]])
    return (f"def _trainlab_tail_{start}(nodes_by_id, edges, stats, dataset, deepcenter_bundle, repair_frame_cache,"
            " deepcenter_heatmap_cache, _stage_t0):\n" + body + "    return nodes_by_id, edges\n")


def tail_namespace(nb_path: Path) -> dict:
    """Globals for the lab notebook's tail: config cell + the post-processing cell's imports, functions and simple
    assignments (no model load, no writer run), with the cell-0 environment; plus the two tail segments."""
    cells = notebook_code_cells(nb_path)
    config = [c for c in cells if "COMP_DIR_CANDIDATES" in c]
    post = [c for c in cells if "def filter_output_graph(" in c]
    if len(config) != 1 or len(post) != 1:
        raise RuntimeError("lab notebook: expected one config cell and one post-processing cell")
    env = cell_env(cells[0])
    if "IPython.display" not in sys.modules:
        try:
            import IPython.display  # noqa: F401
        except Exception:
            stub = types.ModuleType("IPython.display")
            stub.display = lambda *a, **k: None
            sys.modules.setdefault("IPython", types.ModuleType("IPython"))
            sys.modules["IPython.display"] = stub
    ns: dict = {"__name__": "trainlab_tail"}
    with patched_environ(env), contextlib.redirect_stdout(io.StringIO()):
        exec(compile(config[0], "lab_config_cell", "exec"), ns)
        for node in ast.parse(post[0]).body:
            code = compile(ast.Module(body=[node], type_ignores=[]), "lab_post_cell", "exec")
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                try:
                    exec(code, ns)
                except ImportError:
                    pass
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                exec(code, ns)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)) and not (_calls(node) & _SKIP_CALLS):
                try:
                    exec(code, ns)
                except Exception:
                    pass
        for start in ("presafe", "preshort"):
            exec(compile(tail_segment(post[0], start), f"lab_tail_{start}", "exec"), ns)
    for name in ("add_safe_divisions_postlink", "filter_short_track_components", "linefit_smooth_output_graph",
                 "deepcenter_accept_repair_point", "edge_distance_um", "_trainlab_tail_presafe",
                 "_trainlab_tail_preshort", "DEEPCENTER_SAFE_DIV_THRESHOLD", "OUTPUT_LINEFIT_WEIGHT"):
        if name not in ns:
            raise RuntimeError(f"lab notebook namespace lacks {name}")
    ns["trainlab_hook"] = lambda *a, **k: None  # replays record nothing
    ns["BIOHUB_DIVINS_ENABLE"] = "0"  # the insertion block inside the segment is skipped (arms insert themselves)
    ns["_trainlab_env"] = env
    return ns


class DCLookup:
    """deepcenter_score_point stand-in: the kernel's recorded score of the same (t, z, y, x); unseen point -> None
    (= 'missing' -> accepted, like a kernel without a DeepCenter score) and counted."""

    def __init__(self, table: dict):
        self.table, self.calls, self.miss = table, 0, 0

    def __call__(self, dataset, t, point, detector_bundle, frame_cache, heatmap_cache):
        self.calls += 1
        key = (int(t), float(point[0]), float(point[1]), float(point[2]))
        if key not in self.table:
            self.miss += 1
            return None
        return self.table[key]


def copy_graph(graph: tuple[dict, list]) -> tuple[dict, list]:
    nodes, edges = graph
    return {k: dict(v) for k, v in nodes.items()}, [dict(e) for e in edges]


def replay(ns: dict, dump: dict, start: str, dataset: str, dc_threshold: float | None = None,
           linefit: tuple[float, int] | None = None) -> tuple[dict, list, dict, dict]:
    nodes, edges = copy_graph(dump[start])
    stats = json.loads(json.dumps(dump["meta"][start + "_stats"]))
    lookup = DCLookup(dump["dc"])
    over: dict = {"deepcenter_score_point": lookup}
    if dc_threshold is not None:
        over["DEEPCENTER_SAFE_DIV_THRESHOLD"] = float(dc_threshold)
    if linefit is not None:
        over["OUTPUT_LINEFIT_WEIGHT"], over["OUTPUT_LINEFIT_WINDOW"] = float(linefit[0]), int(linefit[1])
    saved = {k: ns.get(k, _MISSING) for k in over}
    ns.update(over)
    try:
        bundle = object() if int(dump["meta"].get("dc_bundle", 0)) else None
        with contextlib.redirect_stdout(io.StringIO()):
            nodes, edges = ns["_trainlab_tail_" + start](nodes, edges, stats, dataset, bundle, {}, {}, time.time())
    finally:
        for k, v in saved.items():
            if v is _MISSING:
                ns.pop(k, None)
            else:
                ns[k] = v
    return nodes, edges, stats, {"dc_calls": lookup.calls, "dc_miss": lookup.miss}


# ------------------------------------------------------------------------------------------------------------------
# arms that edit the final graph
# ------------------------------------------------------------------------------------------------------------------
def _flag(rec: dict, key: str) -> bool:
    try:
        return int(rec.get(key, 0) or 0) == 1
    except (TypeError, ValueError):
        return False


def _pos_um(node: dict) -> np.ndarray:
    return np.array([float(node["z"]), float(node["y"]), float(node["x"])], dtype=np.float64) * np.asarray(SCALE_UM)


def fork_mid_um(nodes: dict, parent: int, children: list[int]) -> float:
    c = np.mean([_pos_um(nodes[k]) for k in children], axis=0)
    return float(np.linalg.norm(_pos_um(nodes[parent]) - c))


def forkmid(nodes: dict, edges: list, thresh_um: float = FORKMID_UM) -> tuple[list, list[dict]]:
    """C04 (s_merge.json): only 2-child forks with exactly one safe_division, non-inserted child edge; |P - mid| >=
    thresh -> drop the ILP-side edge when its edge_prob == 0.0, else the added edge. Nodes are never touched.
    Returns (edges in the input order minus the dropped ones, audit rows for every eligible fork)."""
    by_src: dict[int, list[int]] = {}
    for i, e in enumerate(edges):
        by_src.setdefault(int(e["source_id"]), []).append(i)
    drop: set[int] = set()
    audit = []
    for u in sorted(by_src):
        idx = by_src[u]
        if len(idx) != 2:
            continue
        added = [i for i in idx if _flag(edges[i], "safe_division") and not _flag(edges[i], "div_inserted")]
        if len(added) != 1 or any(_flag(edges[i], "div_inserted") for i in idx):
            continue
        a = added[0]
        o = idx[0] if idx[1] == a else idx[1]
        kids = [int(edges[a]["target_id"]), int(edges[o]["target_id"])]
        mid = fork_mid_um(nodes, u, kids)
        p = edges[o].get("edge_prob")
        ilp_zero = p is not None and not (isinstance(p, float) and math.isnan(p)) and float(p) == 0.0
        remove = None
        if mid >= thresh_um:
            remove = o if ilp_zero else a
            drop.add(remove)
        audit.append({"parent": u, "added_child": kids[0], "ilp_child": kids[1], "mid_um": round(mid, 4),
                      "ilp_edge_prob": None if p is None else float(p),
                      "removed": None if remove is None else ("ilp" if remove == o else "added")})
    return [e for i, e in enumerate(edges) if i not in drop], audit


def node_p_from_divins(path: Path | None) -> tuple[dict | None, list | None]:
    """(node p, the dump's pre-insertion edge pairs) from a divins_dump npz (tools/div_insert.dump_arrays)."""
    if path is None or not Path(path).is_file():
        return None, None
    with np.load(path, allow_pickle=False) as z:
        ids = np.asarray(z["p_id"]).reshape(-1).tolist()
        p = np.asarray(z["p"], dtype=np.float32).reshape(-1, 3)
        st = [tuple(int(v) for v in r) for r in np.asarray(z["edge_st"]).reshape(-1, 2)]
    return {int(i): tuple(float(x) for x in p[k]) for k, i in enumerate(ids)}, st


def insert35(nodes: dict, edges: list, node_p: dict, nosteal0: bool = False) -> tuple[list, dict]:
    """#35's insertion on the final graph; nosteal0: edges with edge_prob == 0.0 are presented to div_insert with
    edge_prob None (= never stolen), then mapped back to the original dicts."""
    if not nosteal0:
        return dvi.insert_divisions(nodes, edges, node_p, INS35)
    masked, back = [], {}
    for e in edges:
        p = e.get("edge_prob")
        if p is not None and not (isinstance(p, float) and math.isnan(p)) and float(p) == 0.0:
            m = dict(e)
            m["edge_prob"] = None
            back[id(m)] = e
            masked.append(m)
        else:
            masked.append(e)
    out, stats = dvi.insert_divisions(nodes, masked, node_p, INS35)
    if out is masked:
        return edges, stats
    return [back.get(id(e), e) for e in out], stats


# ------------------------------------------------------------------------------------------------------------------
# digests and scoring
# ------------------------------------------------------------------------------------------------------------------
def writer_rows(nodes: dict, edges: list) -> bytes:
    """The rows write_test_submission produces for one dataset (nodes by id with rounded coords, edges in order)."""
    out = io.StringIO()
    for nid in sorted(nodes):
        n = nodes[nid]
        out.write("n,%d,%d,%d,%d,%d\n" % (int(nid), int(n["t"]), max(0, int(round(float(n["z"])))),
                                          max(0, int(round(float(n["y"])))), max(0, int(round(float(n["x"]))))))
    for e in edges:
        out.write("e,%d,%d\n" % (int(e["source_id"]), int(e["target_id"])))
    return out.getvalue().encode("ascii")


def writer_digest(nodes: dict, edges: list) -> str:
    return hashlib.sha256(writer_rows(nodes, edges)).hexdigest()


def float_digest(nodes: dict, edges: list) -> str:
    h = hashlib.sha256()
    ids = list(nodes)
    h.update(np.asarray(ids, dtype=np.int64).tobytes())
    h.update(np.asarray([[float(nodes[i][k]) for k in ("t", "z", "y", "x")] for i in ids], dtype=np.float64).tobytes())
    h.update(np.asarray([[int(e["source_id"]), int(e["target_id"])] for e in edges], dtype=np.int64).tobytes())
    return h.hexdigest()


def graph_diff(a: tuple[dict, list], b: tuple[dict, list]) -> dict:
    (na, ea), (nb, eb) = a, b
    common = [i for i in na if i in nb]
    dz = [max(abs(float(na[i][k]) - float(nb[i][k])) for k in ("z", "y", "x")) for i in common]
    return {"writer_equal": writer_digest(na, ea) == writer_digest(nb, eb),
            "float_equal": float_digest(na, ea) == float_digest(nb, eb),
            "nodes": [len(na), len(nb)], "edges": [len(ea), len(eb)],
            "node_ids_equal": list(na) == list(nb),
            "edge_pairs_equal": [(e["source_id"], e["target_id"]) for e in ea] == [(e["source_id"], e["target_id"]) for e in eb],
            "max_abs_coord_diff": max(dz) if dz else 0.0}


def forks_of(edges: list) -> dict[int, tuple[int, ...]]:
    kids: dict[int, list[int]] = {}
    for e in edges:
        kids.setdefault(int(e["source_id"]), []).append(int(e["target_id"]))
    return {u: tuple(sorted(v)) for u, v in kids.items() if len(v) >= 2}


def official_eval(nodes: dict, edges: list, gt_geff: Path) -> tuple[dict, list[int], list[int]]:
    """tracking_cellmot.metrics.evaluate, spelled out so the fork labels come back: same _evaluate call, same edge
    counts, score_divisions (= evaluate_divisions' only input); the pred graph is the writer's rounded nodes."""
    import polars as pl
    import score_geffs as sg  # puts tools/official on sys.path
    import tracksdata as td
    from tracking_cellmot import division_metrics as D
    from tracking_cellmot import metrics as M

    gt, scale = sg._load_gt_and_scale(Path(gt_geff))
    n_total = sg._estimated_n_total(Path(gt_geff))
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
    if g.num_edges() == 0:
        tp, fp, fn = 0, 0, gt.num_edges()
    else:
        ea = M._evaluate_matched_graph(g, gt)
        tp = int(ea[td.DEFAULT_ATTR_KEYS.MATCHED_EDGE_MASK].sum())
        fp = int(ea["pred_valid"].sum()) - tp
        fn = gt.num_edges() - tp
    div = D.score_divisions(g, gt, scale=scale, max_distance=7.0)
    dtp = sum(div.scores.values())
    er = M.EvaluationResult(edge_tp=tp, edge_fp=fp, edge_fn=fn, division_tp=dtp, division_fn=len(div.scores) - dtp,
                            division_fp=len(div.fp_forks), num_pred_nodes=g.num_nodes())
    rec = M.node_recall(g, gt) if g.num_edges() > 0 and g.num_nodes() > 0 else 0.0
    return M.per_sample_metrics(er, n_total, rec), sorted(int(x) for x in div.tp_forks), sorted(int(x) for x in div.fp_forks)


def summarise_rows(rows: list[dict]) -> dict:
    import score_geffs  # noqa: F401  (sys.path)
    from tracking_cellmot.metrics import summarise
    return summarise(rows)


# ------------------------------------------------------------------------------------------------------------------
# one dataset
# ------------------------------------------------------------------------------------------------------------------
_NS_CACHE: dict = {}


def lab_dataset(task: dict) -> dict:
    """task: stem, dump, nb, gt (GT .geff or None = no scoring), divins (npz or None)."""
    stem = task["stem"]
    t0 = time.time()
    ns = _NS_CACHE.get(task["nb"]) or _NS_CACHE.setdefault(task["nb"], tail_namespace(Path(task["nb"])))
    dump = tio.trainlab_load(task["dump"])
    control = copy_graph(dump["final"])
    out: dict = {"stem": stem, "embryo": stem[:4], "meta": {k: dump["meta"][k] for k in
                                                           ("stage_seconds", "kernel_elapsed_s", "n_dc", "dc_bundle")}}
    graphs: dict[str, tuple[dict, list]] = {"control": control}
    info: dict[str, dict] = {"control": {}}
    # parity: the replays must rebuild the kernel's final graph
    rp = replay(ns, dump, "presafe", stem)
    rs = replay(ns, dump, "preshort", stem)
    out["parity"] = {"presafe": {**graph_diff(control, rp[:2]), **rp[3]}, "preshort": graph_diff(control, rs[:2])}
    # forkmid on control
    fm_edges, fm_audit = forkmid(control[0], control[1])
    graphs["forkmid45"] = (control[0], fm_edges)
    info["forkmid45"] = {"removed": sum(1 for r in fm_audit if r["removed"]), "eligible": len(fm_audit)}
    # insertion (node p from the kernel's dump-only divinsert)
    node_p, divins_st = node_p_from_divins(task.get("divins"))
    out["divins_dump"] = node_p is not None
    # the dump-only insertion saw exactly the final graph (it inserts nothing; the final hook follows it)
    out["divins_graph_match"] = None if divins_st is None else divins_st == [
        (int(e["source_id"]), int(e["target_id"])) for e in control[1]]
    if node_p is not None:
        for arm, nosteal in (("ins35", False), ("ins35_nosteal0", True)):
            e2, st = insert35(control[0], control[1], node_p, nosteal0=nosteal)
            graphs[arm] = (control[0], e2)
            info[arm] = {k: st[k] for k in ("divins_added", "divins_added_steal", "divins_triples", "divins_missing_p")}
        e3, fm2 = forkmid(control[0], graphs["ins35"][1])
        graphs["ins35_forkmid45"] = (control[0], e3)
        n_ins = [sum(1 for e in es if _flag(e, "div_inserted")) for es in (graphs["ins35"][1], e3)]
        info["ins35_forkmid45"] = {"removed": sum(1 for r in fm2 if r["removed"]), "inserted_kept": n_ins[0] == n_ins[1]}
    # linefit and DeepCenter threshold replays
    lf = replay(ns, dump, "preshort", stem, linefit=LINEFIT_ARM)
    graphs["linefit_w07_win2"] = lf[:2]
    for t in DC_THRESHOLDS:
        if t == DC_CONTROL:
            continue
        r = replay(ns, dump, "presafe", stem, dc_threshold=t)
        graphs[f"dc{t:.2f}"] = r[:2]
        info[f"dc{t:.2f}"] = {"dc_miss": r[3]["dc_miss"], "safe_divisions_added": r[2].get("safe_divisions_added", 0)}
    # scoring (writer-row digests: identical graphs are scored once)
    scored: dict[str, tuple] = {}
    arms: dict[str, dict] = {}
    control_forks = forks_of(control[1])
    for arm, (nodes, edges) in graphs.items():
        dig = writer_digest(nodes, edges)
        rec = {"digest": dig[:16], "nodes": len(nodes), "edges": len(edges), "forks": len(forks_of(edges)),
               **info.get(arm, {})}
        if task.get("gt"):
            if dig not in scored:
                scored[dig] = official_eval(nodes, edges, Path(task["gt"]))
            row, tpf, fpf = scored[dig]
            f = forks_of(edges)
            new = [u for u, k in f.items() if control_forks.get(u) != k]
            gone = [u for u, k in control_forks.items() if f.get(u) != k]
            rec.update({"row": row, "tp_forks": tpf, "fp_forks": fpf, "new_forks": sorted(new),
                        "gone_forks": sorted(gone)})
        arms[arm] = rec
    out["arms"] = arms
    # forkmid audit with the control's fork labels
    ctp = set(arms["control"].get("tp_forks", []))
    cfp = set(arms["control"].get("fp_forks", []))
    for r in fm_audit:
        r["label"] = "TP" if r["parent"] in ctp else ("FP" if r["parent"] in cfp else "ignored")
    out["forkmid_audit"] = fm_audit
    out["seconds"] = round(time.time() - t0, 1)
    return out


# ------------------------------------------------------------------------------------------------------------------
# aggregation, gates, report
# ------------------------------------------------------------------------------------------------------------------
def aggregate(results: list[dict], half_of: dict) -> dict:
    agg: dict = {}
    for arm in ARMS:
        agg[arm] = {}
        for emb in EMBRYOS:
            for grp in GROUPS:
                res = [r for r in results if r["embryo"] == emb and arm in r["arms"] and "row" in r["arms"][arm]
                       and (grp == "ALL" or half_of.get(r["stem"]) == grp)]
                if not res:
                    continue
                s = summarise_rows([r["arms"][arm]["row"] for r in res])
                s["clips"] = len(res)
                s["nodes"] = sum(r["arms"][arm]["nodes"] for r in res)
                s["forks"] = sum(r["arms"][arm]["forks"] for r in res)
                agg[arm][f"{emb}/{grp}"] = s
    for arm in ARMS:
        for key, s in agg[arm].items():
            c = agg["control"].get(key)
            if c and s.get("score") == s.get("score") and c.get("score") == c.get("score"):
                s["delta"] = s["score"] - c["score"]
                s["delta_nodes"] = s["nodes"] - c["nodes"]
                s["delta_forks"] = s["forks"] - c["forks"]
    return agg


def _fork_precision(results: list[dict], arm: str, emb: str, stems: set | None = None) -> dict:
    new_tp = new_n = gone_tp = gone_n = 0
    for r in results:
        if r["embryo"] != emb or (stems is not None and r["stem"] not in stems):
            continue
        a, c = r["arms"].get(arm, {}), r["arms"]["control"]
        if "new_forks" not in a:
            continue
        new_n += len(a["new_forks"])
        new_tp += len(set(a["new_forks"]) & set(a["tp_forks"]))
        gone_n += len(a["gone_forks"])
        gone_tp += len(set(a["gone_forks"]) & set(c.get("tp_forks", [])))
    return {"new_forks": new_n, "new_tp": new_tp, "new_precision": new_tp / new_n if new_n else None,
            "gone_forks": gone_n, "gone_tp": gone_tp}


def gates(results: list[dict], agg: dict, half_of: dict) -> dict:
    g: dict = {}
    # parity (control gate)
    bad = [r["stem"] for r in results
           if not (r["parity"]["presafe"]["writer_equal"] and r["parity"]["preshort"]["writer_equal"])]
    g["parity"] = {"pass": not bad, "writer_mismatch": bad,
                   "float_mismatch": [r["stem"] for r in results if not (r["parity"]["presafe"]["float_equal"]
                                                                          and r["parity"]["preshort"]["float_equal"])],
                   "dc_miss_total": sum(r["parity"]["presafe"]["dc_miss"] for r in results),
                   "divins_graph_mismatch": [r["stem"] for r in results if r.get("divins_graph_match") is False],
                   "no_divins_dump": [r["stem"] for r in results if r.get("divins_dump") is False]}
    # forkmid (C04 audit, all lab clips)
    fm = {}
    rows = [dict(a, embryo=r["embryo"]) for r in results for a in r["forkmid_audit"]]
    for emb in EMBRYOS:
        rr = [a for a in rows if a["embryo"] == emb]
        tp_mid = [a["mid_um"] for a in rr if a["label"] == "TP"]
        fm[emb] = {"eligible": len(rr), "removed": sum(1 for a in rr if a["removed"]),
                   "removed_tp": sum(1 for a in rr if a["removed"] and a["label"] == "TP"),
                   "removed_fp": sum(1 for a in rr if a["removed"] and a["label"] == "FP"),
                   "tp_forks": len(tp_mid), "tp_mid_max_um": max(tp_mid) if tp_mid else None}
    tp_max = [fm[e]["tp_mid_max_um"] for e in EMBRYOS if fm[e]["tp_mid_max_um"] is not None]
    nodes_same = all(agg["forkmid45"].get(f"{e}/ALL", {}).get("delta_nodes", 0) == 0 for e in EMBRYOS)
    ins_same = all(r["arms"].get("ins35_forkmid45", {}).get("inserted_kept", True) for r in results)
    fm["pass"] = (all(fm[e]["removed_tp"] == 0 for e in EMBRYOS)
                  and sum(fm[e]["removed_fp"] for e in EMBRYOS) >= 3 and fm["44b6"]["removed_fp"] >= 1
                  and (not tp_max or FORKMID_UM - max(tp_max) >= 0.7) and nodes_same and ins_same)
    fm["rule"] = ("0 TP safe-division forks removed on each embryo; >= 3 FP removed with >= 1 on 44b6; TP midpoint "
                  "margin >= 0.7 um below 4.5; node count unchanged (FINAL_REPORT.md section e, T9)")
    g["forkmid"] = fm
    # DeepCenter threshold (M1), judged ONLY on 6bba: t* from SELECTION, verdict on CONFIRMATION
    arms_dc = [f"dc{t:.2f}" for t in DC_THRESHOLDS if t != DC_CONTROL]
    sel = {a: agg[a].get("6bba/SELECTION", {}).get("delta") for a in arms_dc}
    conf = {a: agg[a].get("6bba/CONFIRMATION", {}).get("delta") for a in arms_dc}
    cands = [a for a in arms_dc if sel[a] is not None]
    dc: dict = {"selection_delta": sel, "confirmation_delta": conf,
                "44b6_all_delta": {a: agg[a].get("44b6/ALL", {}).get("delta") for a in arms_dc}}
    if cands:
        best = max(cands, key=lambda a: sel[a])
        tstar = float(best[2:])
        grid = list(DC_THRESHOLDS)
        k = grid.index(tstar)
        neigh = [grid[j] for j in (k - 1, k + 1) if 0 <= j < len(grid)]
        conf_of = {t: (0.0 if t == DC_CONTROL else conf.get(f"dc{t:.2f}")) for t in grid}
        conf_stems = {s for s, h in half_of.items() if h == "CONFIRMATION"}
        prec = _fork_precision(results, best, "6bba", conf_stems)
        cf = agg["control"].get("6bba/CONFIRMATION", {}).get("forks") or 0
        af = agg[best].get("6bba/CONFIRMATION", {}).get("forks") or 0
        d44 = agg[best].get("44b6/ALL", {}).get("delta")
        checks = {
            "conf_ge_+0.002": conf_of[tstar] is not None and conf_of[tstar] >= 0.002,
            "plateau_strict_grid_neighbours_ge_+0.001": all(conf_of[t] is not None and conf_of[t] >= 0.001 for t in neigh),
            "plateau_noncontrol_neighbours_ge_+0.001": all(conf_of[t] is not None and conf_of[t] >= 0.001
                                                           for t in neigh if t != DC_CONTROL),
            "44b6_ge_-0.0005": d44 is not None and d44 >= -0.0005,
            "new_fork_precision_ge_0.35": prec["new_precision"] is None or prec["new_precision"] >= 0.35,
            "fork_change_le_+50%": cf == 0 or (af - cf) / cf <= 0.5,
        }
        dc.update({"t_star": tstar, "neighbours": neigh, "confirmation_at_t_star": conf_of[tstar],
                   "new_fork_precision_conf": prec, "checks": checks,
                   "pass_strict": all(v for k2, v in checks.items() if k2 != "plateau_noncontrol_neighbours_ge_+0.001"),
                   "pass_noncontrol_plateau": all(v for k2, v in checks.items()
                                                 if k2 != "plateau_strict_grid_neighbours_ge_+0.001"),
                   "note": ("The pre-registered plateau rule asks >= +0.001 at both neighbouring thresholds; read "
                            "literally, a neighbour equal to the control (0.25) has delta 0 by definition, so any t* "
                            "next to 0.25 fails. Both readings are reported; the main session decides (no build if "
                            "t* = 0.25; network-confidence arms are discounted to 0)."),
                   "no_build_if_t_star_is_control": True})
    g["deepcenter_m1"] = dc
    # insertion: CONFIRMATION >= 0 on each embryo (else a warning in CONTEXT; R2 unchanged, LB decides)
    g["insertion"] = {a: {emb: agg[a].get(f"{emb}/CONFIRMATION", {}).get("delta") for emb in EMBRYOS}
                      for a in ("ins35", "ins35_nosteal0")}
    g["insertion"]["ok_each_embryo_ge_0"] = {
        a: all((agg[a].get(f"{emb}/CONFIRMATION", {}).get("delta") or 0.0) >= 0.0 for emb in EMBRYOS)
        for a in ("ins35", "ins35_nosteal0")}
    g["linefit_record_only"] = {f"{emb}/{grp}": agg["linefit_w07_win2"].get(f"{emb}/{grp}", {}).get("delta")
                                for emb in EMBRYOS for grp in GROUPS}
    return g


def check_leak(stems: list[str]) -> list:
    sp = json.loads(SPLITS.read_text(encoding="utf-8"))
    clash = []
    for grp in sp["meta"]["leak_groups"]:
        inside = sorted(set(grp) & set(stems))
        if len(inside) > 1:
            clash.append(inside)
    return clash


def _fmt(x, nd=4, sign=False):
    if x is None or (isinstance(x, float) and x != x):
        return "-"
    return (f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}") if isinstance(x, float) else str(x)


def report_md(res: dict) -> str:
    L = ["# exp60 x138 train lab: tail arms (official metric)", "",
         f"Generated by `tools/trainlab.py score` at {res['generated_utc']} UTC from {res['n_clips']} clips "
         f"({', '.join(f'{k} {v}' for k, v in res['clips_per_embryo'].items())}); 44b6 leak-group clashes: "
         f"{res['leak_clashes'] or 'none'}. Missing dumps: {res['missing'] or 'none'}.", "",
         "## Parity (control gate)", "",
         f"pass = **{res['gates']['parity']['pass']}**; writer-row mismatches {res['gates']['parity']['writer_mismatch']};"
         f" float mismatches {res['gates']['parity']['float_mismatch']}; DeepCenter lookups missed "
         f"{res['gates']['parity']['dc_miss_total']}.", "",
         "## Arms (score = adj edge J + 0.1 div J; delta vs control)", "",
         "| arm | group | clips | score | delta | adj edge | div J | div TP/FP/FN | nodes d | forks d |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for arm in ARMS:
        for key, s in res["aggregate"].get(arm, {}).items():
            L.append(f"| {arm} | {key} | {s['clips']} | {_fmt(s.get('score'))} | {_fmt(s.get('delta'), 4, True)} | "
                     f"{_fmt(s.get('adj_edge_jaccard'))} | {_fmt(s.get('division_jaccard'))} | "
                     f"{s.get('division_tp')}/{s.get('division_fp')}/{s.get('division_fn')} | "
                     f"{s.get('delta_nodes', 0)} | {s.get('delta_forks', 0)} |")
    fm = res["gates"]["forkmid"]
    L += ["", "## forkmid 4.5 um audit (C04)", "", f"pass = **{fm['pass']}** ({fm['rule']})", ""]
    for emb in EMBRYOS:
        L.append(f"- {emb}: {fm[emb]}")
    dc = res["gates"]["deepcenter_m1"]
    L += ["", "## DeepCenter safe-division threshold (M1, 6bba only)", "", f"```\n{json.dumps(dc, indent=1)}\n```"]
    L += ["", "## Insertion (#35 config) and linefit (record only)", "",
          f"```\n{json.dumps(res['gates']['insertion'], indent=1)}\n{json.dumps(res['gates']['linefit_record_only'], indent=1)}\n```",
          "", "## Timing per clip (kernel)", "", "| clip | presafe s | preshort s | final s | kernel elapsed s |",
          "|---|---|---|---|---|"]
    for r in res["clips"]:
        st = r["meta"]["stage_seconds"]
        L.append(f"| {r['stem']} | {_fmt(st.get('presafe'), 1)} | {_fmt(st.get('preshort'), 1)} | "
                 f"{_fmt(st.get('final'), 1)} | {_fmt(r['meta']['kernel_elapsed_s'], 0)} |")
    return "\n".join(L) + "\n"


def find_files(roots: list[Path], sub: str, stem: str) -> Path | None:
    """<root>/<sub>/<stem>.npz, <root>/<stem>.npz when root itself is the <sub> folder, else any <sub>/<stem>.npz below."""
    for root in roots:
        for cand in (root / sub / f"{stem}.npz", root / f"{stem}.npz" if root.name == sub else None):
            if cand is not None and cand.is_file():
                return cand
        hits = sorted(p for p in root.rglob(f"{stem}.npz") if p.parent.name == sub)
        if hits:
            return hits[0]
    return None


def cmd_score(a) -> None:
    split = json.loads(Path(a.split).read_text(encoding="utf-8"))
    stems = [s for s in split["stems"] if not a.only or s in set(a.only.split(","))]
    roots = [Path(p) for p in a.dumps]
    tasks, missing = [], []
    for s in stems:
        dump = find_files(roots, "trainlab", s)
        if dump is None:
            missing.append(s)
            continue
        gt = None if a.no_score else Path(a.train_dir) / f"{s}.geff"
        tasks.append({"stem": s, "dump": str(dump), "nb": str(Path(a.nb).resolve()), "gt": None if gt is None else str(gt),
                      "divins": find_files(roots, "divins_dump", s)})
    print(f"{len(tasks)} clips with dumps, {len(missing)} missing: {missing}", flush=True)
    if a.workers > 1:
        from multiprocessing import Pool
        with Pool(a.workers) as pool:
            results = pool.map(lab_dataset, tasks, chunksize=1)
    else:
        results = []
        for t in tasks:
            results.append(lab_dataset(t))
            print(f"  {t['stem']}: parity {results[-1]['parity']['presafe']['writer_equal']}/"
                  f"{results[-1]['parity']['preshort']['writer_equal']} {results[-1]['seconds']}s", flush=True)
    half_of = split["half_of"]
    res = {"generated_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), "n_clips": len(results),
           "clips_per_embryo": {e: sum(r["embryo"] == e for r in results) for e in EMBRYOS},
           "missing": missing, "leak_clashes": check_leak([r["stem"] for r in results]),
           "arms_spec": {"forkmid_um": FORKMID_UM, "ins35": INS35, "linefit": LINEFIT_ARM, "dc": DC_THRESHOLDS}}
    if not a.no_score:
        res["aggregate"] = aggregate(results, half_of)
        res["gates"] = gates(results, res["aggregate"], half_of)
    for r in results:  # keep the JSON small: fork id lists -> counts
        for arm in r["arms"].values():
            for k in ("tp_forks", "fp_forks", "new_forks", "gone_forks"):
                if k in arm:
                    arm[k + "_n"] = len(arm.pop(k))
    res["clips"] = results
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    if not a.no_score:
        out.with_suffix(".md").write_text(report_md(res), encoding="utf-8")
    print("wrote", out.with_suffix(".json"), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("split")
    s.add_argument("--total", type=int, default=SPLIT_TOTAL)
    s.add_argument("--out", default=str(SPLIT_OUT))
    s.add_argument("--force", action="store_true", help="overwrite an existing split (never after a run)")
    c = sub.add_parser("score")
    c.add_argument("--dumps", nargs="+", required=True, help="downloaded kernel output folder(s)")
    c.add_argument("--nb", required=True, help="the lab notebook the dumps came from (its tail code is replayed)")
    c.add_argument("--split", default=str(SPLIT_OUT))
    c.add_argument("--train-dir", default=str(ROOT / "biohub-cell-tracking-during-development/train"))
    c.add_argument("--out", default=str(ROOT / "experiments/exp60_trainlab/results"))
    c.add_argument("--workers", type=int, default=1)
    c.add_argument("--only", default="", help="comma-separated stems")
    c.add_argument("--no-score", action="store_true", help="parity + arm graphs only (no GT needed)")
    a = ap.parse_args()
    if a.cmd == "split":
        out = Path(a.out)
        if out.exists() and not a.force:
            raise SystemExit(f"{out} exists: the split is fixed before any run (use --force only before the push)")
        sp = make_split(a.total)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(sp, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(sp["summary"], indent=1))
        print("wrote", out)
    else:
        cmd_score(a)


if __name__ == "__main__":
    main()
