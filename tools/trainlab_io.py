"""exp60 x138 train lab (research/wf_ideas_v3/TASK_CLOUD_SESSION.md T5): graph snapshots for the CPU tail replay.

Embedded VERBATIM in the lab kernel (tools/build_probe_kernel.py --patch trainlab, its own cell before the
post-processing cell) and imported by tools/trainlab.py on the laptop, so the kernel's dump and the laptop's reader
share one serialiser. Pure python + numpy; nothing here touches images or models.

Kernel side (BIOHUB_TRAINLAB_DUMP=1; 0 = every hook returns at once, nothing is recorded or written):
  trainlab_hook("presafe", ...)   in filter_output_graph right before add_safe_divisions_postlink: snapshot of the
                                  graph + stats, starts recording DeepCenter scores (trainlab_record_dc)
  trainlab_hook("preshort", ...)  right before filter_short_track_components: stops the recording, second snapshot
  trainlab_hook("final", ...)     right before the FINAL print (after linefit and the divinsert call): third snapshot,
                                  writes <BIOHUB_TRAINLAB_DIR>/<dataset>.npz and a TRAINLAB_TIMING log line
Any exception inside a hook is caught: 'TRAINLAB FAILED' in the log, TRAINLAB_STATE["failed"] += 1, the pipeline
continues untouched (the hooks never modify their inputs).

Graph arrays (prefix = stage name + "_"): nodes in dict iteration order and edges in list order (the tail iterates
both), every attribute key present in any record as <prefix>n.<key> / <prefix>e.<key> (float64 value) plus
<prefix>nt.<key> / <prefix>et.<key> (int8 type code: 0 absent, 1 int, 2 None, 3 bool, 4 float, 5 other = lost).
trainlab_graph_from_arrays inverts it exactly for codes 0-4 (ints up to 2**53).
"""
from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path

import numpy as np

TRAINLAB_DUMP = os.environ.get("BIOHUB_TRAINLAB_DUMP", "0") != "0"
TRAINLAB_DIR = Path(os.environ.get("BIOHUB_TRAINLAB_DIR", "/kaggle/working/trainlab"))
TRAINLAB_STAGES = ("presafe", "preshort", "final")
TRAINLAB_STATE: dict = {"pending": {}, "dc": None, "failed": 0, "written": [], "t0": time.time()}
_TL_ABSENT, _TL_INT, _TL_NONE, _TL_BOOL, _TL_FLOAT, _TL_OTHER = 0, 1, 2, 3, 4, 5


def _trainlab_encode(records: list) -> dict:
    keys = sorted({str(k) for r in records for k in r})
    out = {}
    for key in keys:
        vals = np.full(len(records), np.nan, dtype=np.float64)
        kinds = np.zeros(len(records), dtype=np.int8)
        for i, r in enumerate(records):
            if key not in r:
                continue
            v = r[key]
            if v is None:
                kinds[i] = _TL_NONE
            elif isinstance(v, (bool, np.bool_)):
                kinds[i], vals[i] = _TL_BOOL, float(bool(v))
            elif isinstance(v, (int, np.integer)):
                kinds[i], vals[i] = _TL_INT, float(int(v))
            elif isinstance(v, (float, np.floating)):
                kinds[i], vals[i] = _TL_FLOAT, float(v)
            else:
                kinds[i] = _TL_OTHER
        out[key] = (vals, kinds)
    return out


def trainlab_graph_arrays(prefix: str, nodes_by_id: dict, edges: list) -> dict:
    """Snapshot one graph as plain arrays (copies: later in-place edits of the node dicts do not leak in)."""
    arrays = {prefix + "node_order": np.asarray([int(k) for k in nodes_by_id], dtype=np.int64).reshape(-1)}
    for tag, records in (("n", list(nodes_by_id.values())), ("e", list(edges))):
        for key, (vals, kinds) in _trainlab_encode(records).items():
            arrays[f"{prefix}{tag}.{key}"] = vals
            arrays[f"{prefix}{tag}t.{key}"] = kinds
    arrays[prefix + "n_edges"] = np.asarray(len(edges), dtype=np.int64)
    return arrays


def _trainlab_decode(arrays, prefix: str, tag: str, n: int) -> list:
    records = [dict() for _ in range(n)]
    head = f"{prefix}{tag}."
    for name in sorted(k for k in arrays if k.startswith(head)):
        key = name[len(head):]
        vals = np.asarray(arrays[name], dtype=np.float64)
        kinds = np.asarray(arrays[f"{prefix}{tag}t.{key}"])
        for i in range(n):
            kind = int(kinds[i])
            if kind == _TL_ABSENT or kind == _TL_OTHER:
                continue
            if kind == _TL_NONE:
                records[i][key] = None
            elif kind == _TL_BOOL:
                records[i][key] = bool(vals[i])
            elif kind == _TL_INT:
                records[i][key] = int(vals[i])
            else:
                records[i][key] = float(vals[i])
    return records


def trainlab_graph_from_arrays(arrays, prefix: str) -> tuple[dict, list]:
    """Inverse of trainlab_graph_arrays -> (nodes_by_id in the recorded order, edges in the recorded order)."""
    order = [int(i) for i in np.asarray(arrays[prefix + "node_order"]).reshape(-1)]
    nodes = _trainlab_decode(arrays, prefix, "n", len(order))
    edges = _trainlab_decode(arrays, prefix, "e", int(np.asarray(arrays[prefix + "n_edges"])))
    return dict(zip(order, nodes)), edges


def _trainlab_json(obj) -> np.ndarray:
    return np.asarray(json.dumps(obj, sort_keys=True, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


def trainlab_record_dc(t, point, score) -> None:
    """Called by the kernel's deepcenter_score_point wrapper: one row per scored point while recording is on
    (between the presafe and preshort hooks = the safe-division DeepCenter veto only)."""
    rec = TRAINLAB_STATE.get("dc")
    if rec is None:
        return
    s = float("nan") if score is None else float(score)
    rec.append((int(t), float(point[0]), float(point[1]), float(point[2]), s))


def trainlab_hook(stage: str, dataset, nodes_by_id: dict, edges: list, stats: dict, deepcenter_bundle=None,
                  stage_t0=None) -> None:
    if not TRAINLAB_DUMP or dataset is None:
        return
    try:
        now = time.time()
        pend = TRAINLAB_STATE["pending"]
        if stage == "presafe":
            TRAINLAB_STATE["dc"] = []
            pend[str(dataset)] = {"arrays": trainlab_graph_arrays("presafe_", nodes_by_id, edges),
                                  "presafe_stats": json.loads(str(_trainlab_json(stats))),
                                  "dc_bundle": int(deepcenter_bundle is not None),
                                  "t": {"presafe": now - (stage_t0 or now)}}
            return
        rec = pend.get(str(dataset))
        if rec is None:
            raise RuntimeError(f"stage {stage} without a presafe snapshot")
        if stage == "preshort":
            dc = TRAINLAB_STATE["dc"] or []
            TRAINLAB_STATE["dc"] = None
            dca = np.asarray(dc, dtype=np.float64).reshape(-1, 5)
            rec["arrays"]["dc_tzyx"] = dca[:, :4].copy()
            rec["arrays"]["dc_score"] = dca[:, 4].copy()
            rec["arrays"].update(trainlab_graph_arrays("preshort_", nodes_by_id, edges))
            rec["preshort_stats"] = json.loads(str(_trainlab_json(stats)))
            rec["t"]["preshort"] = now - (stage_t0 or now)
            return
        if stage != "final":
            raise ValueError(f"unknown trainlab stage {stage!r}")
        if "dc_score" not in rec["arrays"]:
            raise RuntimeError("final stage without a preshort snapshot")
        rec["arrays"].update(trainlab_graph_arrays("final_", nodes_by_id, edges))
        rec["t"]["final"] = now - (stage_t0 or now)
        meta = {"dataset": str(dataset), "dc_bundle": rec["dc_bundle"], "presafe_stats": rec["presafe_stats"],
                "preshort_stats": rec["preshort_stats"], "final_stats": json.loads(str(_trainlab_json(stats))),
                "stage_seconds": rec["t"], "kernel_elapsed_s": now - float(os.environ.get("BIOHUB_KERNEL_START_TS",
                                                                                          TRAINLAB_STATE["t0"])),
                "n_dc": int(len(rec["arrays"]["dc_score"])), "format": 1}
        TRAINLAB_DIR.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(TRAINLAB_DIR / f"{dataset}.npz", meta_json=_trainlab_json(meta), **rec["arrays"])
        pend.pop(str(dataset), None)
        TRAINLAB_STATE["written"].append(str(dataset))
        timing = {"dataset": str(dataset), "presafe_s": round(rec["t"]["presafe"], 2),
                  "preshort_s": round(rec["t"]["preshort"], 2), "final_s": round(rec["t"]["final"], 2),
                  "kernel_elapsed_s": round(meta["kernel_elapsed_s"], 1), "n_dc": meta["n_dc"],
                  "nodes": len(nodes_by_id), "edges": len(edges)}
        print("TRAINLAB_TIMING " + json.dumps(timing, sort_keys=True), flush=True)
    except Exception as exc:  # fail-soft: the lab never breaks the pipeline
        TRAINLAB_STATE["failed"] += 1
        TRAINLAB_STATE["dc"] = None
        print(f"  [{dataset}] TRAINLAB FAILED at {stage} ({type(exc).__name__}: {exc})", flush=True)


def trainlab_load(path) -> dict:
    """Laptop side: one dataset's dump -> {'meta', 'presafe', 'preshort', 'final' (nodes, edges), 'dc' {(t,z,y,x): s}}."""
    with np.load(path, allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    out = {"meta": json.loads(str(arrays["meta_json"]))}
    for stage in TRAINLAB_STAGES:
        out[stage] = trainlab_graph_from_arrays(arrays, stage + "_")
    tzyx = np.asarray(arrays["dc_tzyx"], dtype=np.float64).reshape(-1, 4)
    score = np.asarray(arrays["dc_score"], dtype=np.float64).reshape(-1)
    dc: dict = {}
    for (t, z, y, x), s in zip(tzyx.tolist(), score.tolist()):
        dc[(int(t), float(z), float(y), float(x))] = None if math.isnan(s) else float(s)
    out["dc"] = dc
    return out
