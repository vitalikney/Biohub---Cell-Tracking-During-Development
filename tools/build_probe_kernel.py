"""Build an LB-probe kernel = exp29 realised config + env-knob overrides (+ optional DivNet veto), one command.

    python tools/build_probe_kernel.py exp40_relink_off --set MOTION_RELINK_TIGHT_UM=0 --set DEEPCENTER_GAP_THRESHOLD=0.35 \
        --divnet 0 --note "relink off" [--push]

Base = experiments/exp39_sjlee947_tight55_divnetveto (exp29 + DivNet veto cell). `--divnet 0` disables the veto through
BIOHUB_DIVNET_VERIFY=0 (the cell stays, the model is not loaded), so `--divnet 0` with no --set is exp29 bit-for-bit.
Knob names are given WITHOUT the BIOHUB_ prefix. Overrides are appended to the config cell AFTER the base values and the
configuration guard's expected values are patched for the keys it checks. Output folder:
experiments/<name>/ with the notebook, kernel-metadata.json and probe.json; `--push` runs `kaggle kernels push`.

Patches (`--patch NAME`, repeatable, any order; they always address the BASE code-cell indices):
  gshift     takaito's per-frame global-shift motion relink (cell 2 knobs + cell 7).
  divinsert  plan L2 DaughterNet division insertion after the post-processing tail: a new code cell after the DivNet
             cell with tools/daughternet.py + tools/div_insert.py embedded, and a guarded call in filter_output_graph.
             Knobs (via --set, without BIOHUB_): DIVINS_ENABLE (default 0 = exact no-op, no model load), DIVINS_STEAL,
             DIVINS_CAP, DIVINS_FRAME_CAP, DIVINS_ALPHA, DIVINS_THRESH, DIVINS_WEIGHTS (comma-separated globs, default
             /kaggle/input/**/vitalii_daughternet/*.pt), DIVINS_DUMP (1 -> /kaggle/working/divins_dump/<dataset>.npz),
             DIVINS_DUMP_DIR, DIVINS_BATCH. With DIVINS_ENABLE != 0 the weights dataset vitaliineibauer/biohub-ft-weights
             is ensured in dataset_sources; `--dataset owner/slug` attaches any other dataset.
  leafprune  plan L4 weak-leaf pruning, verbatim from seyitkaangunes/biohub-035-deconfounded-edge-stack: cell 2 knob
             BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB (default 0.0 = exact no-op) + prune_weak_leaf_nodes and its guarded call in
             filter_output_graph between short-track filtering and linefit (the 035 notebook's position). Set it with
             --set LEAF_PRUNE_MIN_EDGE_PROB=0.3 (the 035 notebook runs 0.30). Replay: config key leaf_prune=<p>.
  edgefilter plan L5 edge-anatomy filter: cell 2 EDGEFILTER_PARAMS from BIOHUB_EDGEFILTER_{ENABLE,MAX_PROB,ALT,
             MIN_LEN_UM,RELINK,PRUNE,SKIP_FORKS} (ENABLE default 0 = exact no-op) + cell 7 edgefilter_final_graph, a
             capture of the linker's own edges before the motion relink, and a guarded call right after linefit (before
             the divinsert call if both patches are applied). Drops (RELINK=1: re-links to the ILP's free alternative)
             relink edges with edge_prob < MAX_PROB (= the unscored 0.0 pairs). Replay: config keys ef.<param>
             (experiments/l2_daughternet/replay/replay.py), same function text.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = ROOT / "experiments/exp39_sjlee947_tight55_divnetveto"
BASE_NB = BASE_DIR / "exp39-sjlee947-tight55-divnetveto.ipynb"
NL = chr(10)


def _rep1(s: str, old: str, new: str) -> str:
    assert s.count(old) == 1, f"anchor count {s.count(old)} != 1: {old[:70]!r}"
    return s.replace(old, new)


def patch_gshift(cells_src: dict) -> None:
    """takaito/biohub-a951-gshift (2026-09-22): per-frame global displacement = median of mutual-nearest-neighbour
    shifts between consecutive frames (MNN radius BIOHUB_MOTION_RELINK_GLOBAL_SHIFT_MNN_UM, default 8; his run: 12),
    subtracted inside the motion relink cost (raw distance and velocity prediction). Ported line for line; the only
    difference is that our relink has no density-adaptive per-call velocity/bonus overrides (we use the constants)."""
    c2 = cells_src[2]
    c2 = _rep1(c2, 'MOTION_RELINK_LEARNED_BONUS = float(os.environ.get("BIOHUB_MOTION_RELINK_LEARNED_BONUS", "0.75"))' + NL,
               'MOTION_RELINK_LEARNED_BONUS = float(os.environ.get("BIOHUB_MOTION_RELINK_LEARNED_BONUS", "0.75"))' + NL
               + 'MOTION_RELINK_GLOBAL_SHIFT = os.environ.get("BIOHUB_MOTION_RELINK_GLOBAL_SHIFT", "0") != "0"' + NL
               + 'MOTION_RELINK_GLOBAL_SHIFT_MNN_UM = float(os.environ.get("BIOHUB_MOTION_RELINK_GLOBAL_SHIFT_MNN_UM", "8.0"))' + NL
               + 'MOTION_RELINK_GLOBAL_SHIFT_MIN_PAIRS = int(os.environ.get("BIOHUB_MOTION_RELINK_GLOBAL_SHIFT_MIN_PAIRS", "20"))' + NL
               + 'MOTION_RELINK_GLOBAL_SHIFT_MIN_UM = float(os.environ.get("BIOHUB_MOTION_RELINK_GLOBAL_SHIFT_MIN_UM", "0.0"))' + NL)
    cells_src[2] = c2
    c7 = cells_src[7]
    c7 = _rep1(c7, '''    position_um = {node_id: _position_um(node) for node_id, node in nodes_by_id.items()}
    predecessor_position_um: dict[int, np.ndarray] = {}
    selected_edges: list[dict[str, object]] = []

    def assign_pass(
        source_ids: list[int],
        target_ids: list[int],
        gate_um: float,
    ) -> list[tuple[int, int, float, float, float]]:
        if not source_ids or not target_ids:
            return []
''', '''    position_um = {node_id: _position_um(node) for node_id, node in nodes_by_id.items()}
    predecessor_position_um: dict[int, np.ndarray] = {}
    selected_edges: list[dict[str, object]] = []

    # --- gshift: per-frame global displacement (median of mutual-nearest-neighbour shifts) ---
    _zero_shift = np.zeros(3, dtype=np.float64)
    global_shift_um: dict[int, np.ndarray] = {}
    if MOTION_RELINK_GLOBAL_SHIFT:
        for _t in sorted(ids_by_t):
            if _t + 1 not in ids_by_t:
                continue
            _src = np.stack([position_um[i] for i in ids_by_t[_t]])
            _tgt = np.stack([position_um[i] for i in ids_by_t[_t + 1]])
            if len(_src) < MOTION_RELINK_GLOBAL_SHIFT_MIN_PAIRS or len(_tgt) < MOTION_RELINK_GLOBAL_SHIFT_MIN_PAIRS:
                continue
            _d1, _j = cKDTree(_tgt).query(_src, distance_upper_bound=MOTION_RELINK_GLOBAL_SHIFT_MNN_UM)
            _d2, _i = cKDTree(_src).query(_tgt, distance_upper_bound=MOTION_RELINK_GLOBAL_SHIFT_MNN_UM)
            _pairs = [(a, int(_j[a])) for a in range(len(_src)) if np.isfinite(_d1[a]) and _i[int(_j[a])] == a]
            if len(_pairs) < MOTION_RELINK_GLOBAL_SHIFT_MIN_PAIRS:
                continue
            _shift = np.median(np.stack([_tgt[b] - _src[a] for a, b in _pairs]), axis=0)
            if float(np.linalg.norm(_shift)) < MOTION_RELINK_GLOBAL_SHIFT_MIN_UM:
                continue
            global_shift_um[_t] = _shift
        stats["motion_relink_global_shift_frames"] = len(global_shift_um)
        stats["motion_relink_global_shift_sum_um"] = float(
            sum(float(np.linalg.norm(v)) for v in global_shift_um.values())
        )

    def assign_pass(
        source_ids: list[int],
        target_ids: list[int],
        gate_um: float,
        shift_um: np.ndarray = _zero_shift,
        prev_shift_um: np.ndarray = _zero_shift,
    ) -> list[tuple[int, int, float, float, float]]:
        if not source_ids or not target_ids:
            return []
''')
    c7 = _rep1(c7, '''            prev_pos = predecessor_position_um.get(source_id)
            if prev_pos is None:
                predicted = source_pos
            else:
                predicted = source_pos + MOTION_RELINK_VELOCITY_WEIGHT * (source_pos - prev_pos)
            for j, target_id in enumerate(target_ids):
                target_pos = position_um[target_id]
                raw = float(np.linalg.norm(target_pos - source_pos))
                if raw > gate_um:
                    continue
                motion = float(np.linalg.norm(target_pos - predicted))
                prob = learned_prob(source_id, target_id)
                raw_dist[i, j] = raw
''', '''            prev_pos = predecessor_position_um.get(source_id)
            shifted_pos = source_pos + shift_um
            if prev_pos is None:
                predicted = shifted_pos
            else:
                predicted = shifted_pos + MOTION_RELINK_VELOCITY_WEIGHT * (source_pos - prev_pos - prev_shift_um)
            for j, target_id in enumerate(target_ids):
                target_pos = position_um[target_id]
                raw_true = float(np.linalg.norm(target_pos - source_pos))
                raw = float(np.linalg.norm(target_pos - shifted_pos))
                if raw > gate_um:
                    continue
                motion = float(np.linalg.norm(target_pos - predicted))
                prob = learned_prob(source_id, target_id)
                raw_dist[i, j] = raw_true
''')
    c7 = _rep1(c7, '            matches = assign_pass(pass_sources, pass_targets, gate_um)' + NL,
               '            matches = assign_pass(' + NL
               + '                pass_sources,' + NL
               + '                pass_targets,' + NL
               + '                gate_um,' + NL
               + '                global_shift_um.get(t, _zero_shift),' + NL
               + '                global_shift_um.get(t - 1, _zero_shift),' + NL
               + '            )' + NL)
    cells_src[7] = c7


NEW_CELLS_KEY = "_new_cells"  # cells_src[NEW_CELLS_KEY] = [(after_code_index, source), ...], inserted after all patches
WEIGHTS_DATASET = "vitaliineibauer/biohub-ft-weights"


def _embed_module(path: Path) -> str:
    """Module source for a notebook cell: the one `from __future__ import annotations` line goes to the cell top."""
    s = path.read_text(encoding="utf-8")
    line = "from __future__ import annotations" + NL
    assert s.count(line) == 1, f"{path.name}: expected one __future__ import"
    return s.replace(line, "")


DIVINS_GLUE = r'''
# ======== kernel glue (tools/build_probe_kernel.py patch_divinsert) ========
import glob as _divins_glob

BIOHUB_DIVINS_ENABLE = os.environ.get("BIOHUB_DIVINS_ENABLE", "0").strip() or "0"
DIVINS_WEIGHTS = os.environ.get("BIOHUB_DIVINS_WEIGHTS", "/kaggle/input/**/vitalii_daughternet/*.pt")
DIVINS_DUMP = os.environ.get("BIOHUB_DIVINS_DUMP", "0") != "0"
DIVINS_DUMP_DIR = Path(os.environ.get("BIOHUB_DIVINS_DUMP_DIR", "/kaggle/working/divins_dump"))
DIVINS_BATCH = int(os.environ.get("BIOHUB_DIVINS_BATCH", "256"))
DIVINS_PARAMS = divins_params({
    "enable": 1 if BIOHUB_DIVINS_ENABLE != "0" else 0,
    "steal": 1 if os.environ.get("BIOHUB_DIVINS_STEAL", "0") != "0" else 0,
    "cap_video": int(os.environ.get("BIOHUB_DIVINS_CAP", "3")),
    "cap_frame": int(os.environ.get("BIOHUB_DIVINS_FRAME_CAP", "1")),
    "alpha": float(os.environ.get("BIOHUB_DIVINS_ALPHA", "1.0")),
    "threshold": float(os.environ.get("BIOHUB_DIVINS_THRESH", "0.5")),
})


def divins_find_weights(spec: str) -> list[str]:
    """Comma-separated glob patterns -> sorted .pt files. '**' is expanded by a pruned os.walk (skips *.zarr / *.geff
    trees and hidden dirs, depth <= 6): a plain recursive glob over /kaggle/input walks the competition zarr chunks."""
    found: set[str] = set()
    for pattern in [item.strip() for item in str(spec).split(",") if item.strip()]:
        if "**" not in pattern:
            found.update(_divins_glob.glob(pattern))
            continue
        head, _, tail = pattern.partition("**")
        head = os.path.normpath(head.rstrip("/\\") or "/")
        tail = tail.lstrip("/\\")
        if not os.path.isdir(head):
            continue
        base_depth = head.count(os.sep)
        for dirpath, dirnames, _files in os.walk(head, followlinks=True):
            if os.path.normpath(dirpath).count(os.sep) - base_depth >= 6:
                dirnames[:] = []
            else:
                dirnames[:] = sorted(d for d in dirnames if not d.endswith((".zarr", ".geff")) and not d.startswith("."))
            found.update(_divins_glob.glob(os.path.join(dirpath, tail)))
    return sorted(p for p in found if os.path.isfile(p))


def divins_frame_reader(dataset: str):
    """The notebook's read_test_frame with t clamped to [0, T-1] (the DivNet recipe asks for t+1 and t+2, which do not
    exist for nodes near the last frame; friend A's B20 reader clamps the same way). Frames it loads itself are not
    kept in the shared cache (prepared frames are cached in the bundle), frames already there are reused."""
    meta = json.loads((TEST_DIR / f"{dataset}.zarr" / "0" / "zarr.json").read_text())
    n_frames = int(meta["shape"][0])

    def _read(ds: str, t: int, frame_cache: dict) -> np.ndarray:
        tt = max(0, min(int(t), n_frames - 1))
        had = tt in frame_cache
        frame = read_test_frame(ds, tt, frame_cache)
        if not had:
            frame_cache.pop(tt, None)
        return frame

    return _read


def divins_dump(dataset: str, nodes_by_id: dict, edges: list, node_p: dict, triples: list, result_edges: list) -> None:
    """BIOHUB_DIVINS_DUMP=1: pre-insertion graph + node p + triples + result -> <DUMP_DIR>/<dataset>.npz
    (tools/div_insert.replay_dump reproduces the insertion from it on the laptop)."""
    DIVINS_DUMP_DIR.mkdir(parents=True, exist_ok=True)
    arrays = dump_arrays(nodes_by_id, edges, node_p, DIVINS_PARAMS, triples, result_edges)
    np.savez_compressed(DIVINS_DUMP_DIR / f"{dataset}.npz", **arrays)


DIVINS_BUNDLE = None
if BIOHUB_DIVINS_ENABLE != "0":
    _divins_t0 = time.time()
    _divins_paths = divins_find_weights(DIVINS_WEIGHTS)
    if not _divins_paths:
        raise FileNotFoundError(f"BIOHUB_DIVINS_ENABLE={BIOHUB_DIVINS_ENABLE} but no DaughterNet weights match {DIVINS_WEIGHTS!r}")
    DIVINS_BUNDLE = load_daughternet(_divins_paths)
    print(f"DIVINS ENABLED: {len(_divins_paths)} DaughterNet model(s) {_divins_paths} on {DIVINS_BUNDLE['device']}"
          f" params {DIVINS_PARAMS} batch {DIVINS_BATCH} dump {DIVINS_DUMP} ({time.time() - _divins_t0:.1f} s)")
else:
    print("DIVINS disabled (BIOHUB_DIVINS_ENABLE=0): no model loaded, filter_output_graph unchanged")
'''

DIVINS_CALL = r'''    # ---- divinsert: post-tail DaughterNet division insertion (tools/div_insert.py); BIOHUB_DIVINS_ENABLE=0 -> no-op ----
    if BIOHUB_DIVINS_ENABLE != "0" and dataset is not None and edges and nodes_by_id:
        _dv_t0 = time.time()
        _dv_triples = candidate_triples(nodes_by_id, edges, DIVINS_PARAMS)
        _dv_ids = sorted({int(_i) for _tr in _dv_triples for _i in _tr})
        _dv_t1 = time.time()
        if _dv_ids:
            _dv_probs = score_nodes(str(dataset), [nodes_by_id[_i] for _i in _dv_ids], DIVINS_BUNDLE, repair_frame_cache,
                                    divins_frame_reader(str(dataset)), batch=DIVINS_BATCH)
        else:
            _dv_probs = np.zeros((0, 3), dtype=np.float32)
        DIVINS_BUNDLE["prepared_frames"].clear()
        _dv_node_p = {_i: tuple(float(_x) for _x in _dv_probs[_k]) for _k, _i in enumerate(_dv_ids)}
        _dv_t2 = time.time()
        _dv_edges, _dv_stats = insert_divisions(nodes_by_id, edges, _dv_node_p, DIVINS_PARAMS)
        _dv_t3 = time.time()
        if DIVINS_DUMP:
            divins_dump(str(dataset), nodes_by_id, edges, _dv_node_p, _dv_triples, _dv_edges)
        stats.update(_dv_stats)
        stats["divins_nodes_scored"] = len(_dv_ids)
        stats["divins_sec_candidates"] = round(_dv_t1 - _dv_t0, 3)
        stats["divins_sec_score"] = round(_dv_t2 - _dv_t1, 3)
        stats["divins_sec_insert"] = round(_dv_t3 - _dv_t2, 3)
        print(f"  [{dataset}] divinsert: triples={_dv_stats['divins_triples']}"
              f" (orphan={_dv_stats['divins_triples_orphan']}, steal={_dv_stats['divins_triples_steal']})"
              f" nodes_scored={len(_dv_ids)} eligible={_dv_stats['divins_eligible']}"
              f" added={_dv_stats['divins_added']} (orphan={_dv_stats['divins_added_orphan']},"
              f" steal={_dv_stats['divins_added_steal']}) sec cand/score/insert="
              f"{_dv_t1 - _dv_t0:.1f}/{_dv_t2 - _dv_t1:.1f}/{_dv_t3 - _dv_t2:.1f}")
        edges = _dv_edges
    # ---- /divinsert ----
'''


def patch_divinsert(cells_src: dict) -> None:
    """Plan L2 (2026-09-23): DaughterNet-scored division insertion AFTER the whole post-processing tail.
    New cell after the DivNet cell (code index 6): tools/daughternet.py + tools/div_insert.py verbatim + BIOHUB_DIVINS_*
    knobs + weight loading (only when BIOHUB_DIVINS_ENABLE != 0). Cell 7: (a) recover_strict_gap2 tags its inserted
    nodes gap2_synthetic = 1 (a node key nothing downstream reads; lets div_insert skip them as v), (b) a guarded call
    after linefit_smooth_output_graph and before the FINAL print: candidate_triples -> score_nodes on the involved nodes
    only (frame reader = read_test_frame over filter_output_graph's repair_frame_cache) -> insert_divisions, with
    per-stage seconds and counts in stats, and BIOHUB_DIVINS_DUMP=1 writes /kaggle/working/divins_dump/<dataset>.npz."""
    tools_dir = Path(__file__).resolve().parent
    cell = ("# ---- divinsert (tools/build_probe_kernel.py --patch divinsert): plan L2 post-tail division insertion."
            + NL + "# Embedded verbatim: tools/daughternet.py (3-class DaughterNet on the DivNet input contract; its divnet_infer"
            + NL + "# import falls back to the DivNet cell's globals) and tools/div_insert.py (the same code the laptop replay runs)."
            + NL + "# BIOHUB_DIVINS_ENABLE=0 (default): nothing is loaded and filter_output_graph behaves exactly as before."
            + NL + "from __future__ import annotations" + NL + NL
            + "# ======== tools/daughternet.py ========" + NL + _embed_module(tools_dir / "daughternet.py") + NL
            + "# ======== tools/div_insert.py ========" + NL + _embed_module(tools_dir / "div_insert.py")
            + DIVINS_GLUE)
    cells_src.setdefault(NEW_CELLS_KEY, []).append((6, cell))
    c7 = cells_src[7]
    c7 = _rep1(c7, '''                "x": refined_point[2],
            }
            inserted_ids.append(node_id)
''', '''                "x": refined_point[2],
                "gap2_synthetic": 1,  # divinsert: node flag (gap2 nodes had none); no downstream reader
            }
            inserted_ids.append(node_id)
''')
    anchor = '    nodes_by_id = linefit_smooth_output_graph(nodes_by_id, edges, stats)' + NL
    if anchor + EDGEFILTER_CALL in c7:  # --patch edgefilter applied first: keep filter -> insertion (the replay's order)
        anchor += EDGEFILTER_CALL
    c7 = _rep1(c7, anchor, anchor + DIVINS_CALL)
    cells_src[7] = c7


def meta_divinsert(meta: dict, overrides: dict) -> None:
    """Attach the DaughterNet weights dataset when the stage is switched on."""
    if overrides.get("BIOHUB_DIVINS_ENABLE", "0") != "0" and WEIGHTS_DATASET not in meta["dataset_sources"]:
        meta["dataset_sources"].append(WEIGHTS_DATASET)


# ---- leafprune: weak-leaf pruning, ported VERBATIM from the public notebook
# seyitkaangunes/biohub-035-deconfounded-edge-stack (pulled 2026-09-24; its cell 0 runs
# BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB=0.30, its cell 2 default is 0.0 = inert). The knob line, function, counters and call
# are that notebook's text; the replay lab (experiments/l2_daughternet/replay/replay.py, config key leaf_prune=<p>)
# applies the same two source functions to its notebook cells, so a replay number and a kernel built with
# --patch leafprune run one code path.
LEAFPRUNE_KNOB = (
    "# leafprune (035 notebook v4): weak-leaf pruning threshold, 0.0 = inert" + NL
    + 'LEAF_PRUNE_MIN_EDGE_PROB = float(os.environ.get("BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB", "0.0"))' + NL
)
LEAFPRUNE_DISPLAY = '    "leaf_prune_min_edge_prob": LEAF_PRUNE_MIN_EDGE_PROB,' + NL
LEAFPRUNE_FN = r'''def prune_weak_leaf_nodes(
    nodes_by_id: dict[int, dict[str, object]],
    edges: list[dict[str, object]],
    stats: dict[str, int],
) -> tuple[dict[int, dict[str, object]], list[dict[str, object]]]:
    """v4: remove terminal leaf nodes attached by a low-probability edge.

    A node is pruned only when ALL of the following hold:
      * it has no successor (out-degree 0) -- i.e. the tracker could not continue it;
      * it has exactly one incoming edge (never a division daughter ambiguity);
      * it does not sit on the final frame (terminal cells there are legitimate);
      * its single incoming edge HAS a learned probability and it is below
        LEAF_PRUNE_MIN_EDGE_PROB.
    Edges without a probability (edge_prob is None, e.g. safe-division additions)
    are exempt by construction, so division daughters added by add_safe_divisions_postlink
    can never be pruned here. Single pass, no cascade: conservative by design.
    """
    if LEAF_PRUNE_MIN_EDGE_PROB <= 0.0 or not nodes_by_id or not edges:
        return nodes_by_id, edges
    max_t = max(int(node["t"]) for node in nodes_by_id.values())
    out_degree: dict[int, int] = {}
    incoming: dict[int, list[dict[str, object]]] = {}
    for edge in edges:
        source_id = int(edge["source_id"])
        target_id = int(edge["target_id"])
        out_degree[source_id] = out_degree.get(source_id, 0) + 1
        incoming.setdefault(target_id, []).append(edge)
    drop: set[int] = set()
    for node_id, node in nodes_by_id.items():
        if out_degree.get(node_id, 0) != 0:
            continue
        if int(node["t"]) >= max_t:
            continue
        incoming_edges = incoming.get(node_id, [])
        if len(incoming_edges) != 1:
            continue
        prob = incoming_edges[0].get("edge_prob")
        if prob is None:
            continue
        try:
            prob = float(prob)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(prob):
            continue
        if prob < LEAF_PRUNE_MIN_EDGE_PROB:
            drop.add(node_id)
    if not drop:
        return nodes_by_id, edges
    kept_nodes = {node_id: node for node_id, node in nodes_by_id.items() if node_id not in drop}
    kept_edges = [
        edge for edge in edges
        if int(edge["source_id"]) not in drop and int(edge["target_id"]) not in drop
    ]
    stats["leaf_prune_nodes"] = len(drop)
    stats["leaf_prune_edges"] = len(edges) - len(kept_edges)
    return kept_nodes, kept_edges
'''
LEAFPRUNE_STATS = '        "leaf_prune_nodes": 0,' + NL + '        "leaf_prune_edges": 0,' + NL
LEAFPRUNE_CALL = r'''    if LEAF_PRUNE_MIN_EDGE_PROB > 0.0:
        nodes_by_id, edges = prune_weak_leaf_nodes(nodes_by_id, edges, stats)
        if stats.get("leaf_prune_nodes"):
            print(f"  [{dataset}] after weak-leaf pruning: {len(nodes_by_id)} nodes, {len(edges)} edges"
                  f" (leaf_pruned={stats['leaf_prune_nodes']})")
'''
# anchors (each must occur exactly once): the 035 notebook places the call after short-track filtering and before
# linefit_smooth_output_graph, the function right before filter_output_graph, the two counters at the end of the
# stats dict, the knob after OUTPUT_LINEFIT_WINDOW and its display entry after "output_linefit_window".
_LP_SHORT_TRACK_PRINT = ('''          f" (components_removed={stats['short_track_components_removed']})")''' + NL)
_LP_LINEFIT_CALL = "    nodes_by_id = linefit_smooth_output_graph(nodes_by_id, edges, stats)" + NL


def leafprune_config_source(c2: str) -> str:
    """Config cell (base code cell 2): the BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB knob (default 0.0) + its CONFIG_DISPLAY line.
    The 035 notebook's PPSWEEP_EXTENDED / PPSWEEP_PREFIX_GUARD switches next to it are not ported (they only extend its
    validator-gated PP sweep, which our base runs with the validator off)."""
    line = 'OUTPUT_LINEFIT_WINDOW = int(os.environ.get("BIOHUB_OUTPUT_LINEFIT_WINDOW", "2"))' + NL
    c2 = _rep1(c2, line, line + NL + LEAFPRUNE_KNOB)
    line = '    "output_linefit_window": OUTPUT_LINEFIT_WINDOW,' + NL
    return _rep1(c2, line, line + LEAFPRUNE_DISPLAY)


def leafprune_postproc_source(c7: str) -> str:
    """Post-processing cell (base code cell 7): prune_weak_leaf_nodes before filter_output_graph, its two counters in
    the stats dict, and the guarded call between short-track filtering and linefit (LEAF_PRUNE_MIN_EDGE_PROB <= 0 ->
    the call is skipped: the graph is exactly the base's)."""
    c7 = _rep1(c7, NL + NL + NL + "def filter_output_graph(" + NL,
               NL + NL + NL + LEAFPRUNE_FN + NL + NL + "def filter_output_graph(" + NL)
    c7 = _rep1(c7, '        "linefit_skipped_nodes": 0,' + NL + "    }" + NL,
               '        "linefit_skipped_nodes": 0,' + NL + LEAFPRUNE_STATS + "    }" + NL)
    return _rep1(c7, _LP_SHORT_TRACK_PRINT + _LP_LINEFIT_CALL,
                 _LP_SHORT_TRACK_PRINT + LEAFPRUNE_CALL + _LP_LINEFIT_CALL)


def patch_leafprune(cells_src: dict) -> None:
    """Plan L4 (2026-09-24): weak-leaf pruning from seyitkaangunes/biohub-035-deconfounded-edge-stack. A leaf (no
    successor, exactly one incoming edge, not on the last frame) whose incoming edge has a finite learned edge_prob
    below BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB is removed (single pass, no cascade); edges without a probability
    (safe-division / gap edges) are exempt. Knob via --set LEAF_PRUNE_MIN_EDGE_PROB=<p>; default 0.0 = exact no-op."""
    cells_src[2] = leafprune_config_source(cells_src[2])
    cells_src[7] = leafprune_postproc_source(cells_src[7])


# ---- edgefilter: plan L5 (edge anatomy, experiments/l2_daughternet/edge_anatomy). Drop - and optionally re-link to
# the ILP's own choice - the motion-relink edges the network never scored (edge_prob 0.0; every scored edge has
# p >= 0.4, gap / safe-division edges carry None and are exempt) at the END of the tail (after linefit, before the
# divinsert call when both patches are applied). The replay lab (experiments/l2_daughternet/replay/replay.py, config
# keys ef.<param>) applies the same source text to its notebook cells and calls the same function on the post-tail
# graph, so a replay number and a kernel built with --patch edgefilter run one code path.
EDGEFILTER_KNOB_LINE = 'OUTPUT_LINEFIT_WEIGHT = float(os.environ.get("BIOHUB_OUTPUT_LINEFIT_WEIGHT", "0.8"))' + NL
EDGEFILTER_DISPLAY_LINE = '    "output_linefit_weight": OUTPUT_LINEFIT_WEIGHT,' + NL
# replay param -> kernel knob (without BIOHUB_), with the kernel default; the function reads a dict with these keys
EDGEFILTER_KNOBS = {"enable": ("EDGEFILTER_ENABLE", "0"), "max_prob": ("EDGEFILTER_MAX_PROB", "0.3"),
                    "alt": ("EDGEFILTER_ALT", "0"), "min_len_um": ("EDGEFILTER_MIN_LEN_UM", "0.0"),
                    "relink": ("EDGEFILTER_RELINK", "0"), "prune": ("EDGEFILTER_PRUNE", "0"),
                    "skip_forks": ("EDGEFILTER_SKIP_FORKS", "1")}
EDGEFILTER_KNOB = (
    "# edgefilter (plan L5): drop / re-link unscored motion-relink edges after linefit; ENABLE=0 = inert" + NL
    + 'EDGEFILTER_PARAMS = {' + NL
    + '    "enable": int(os.environ.get("BIOHUB_EDGEFILTER_ENABLE", "0")),' + NL
    + '    "max_prob": float(os.environ.get("BIOHUB_EDGEFILTER_MAX_PROB", "0.3")),' + NL
    + '    "alt": int(os.environ.get("BIOHUB_EDGEFILTER_ALT", "0")),' + NL
    + '    "min_len_um": float(os.environ.get("BIOHUB_EDGEFILTER_MIN_LEN_UM", "0.0")),' + NL
    + '    "relink": int(os.environ.get("BIOHUB_EDGEFILTER_RELINK", "0")),' + NL
    + '    "prune": int(os.environ.get("BIOHUB_EDGEFILTER_PRUNE", "0")),' + NL
    + '    "skip_forks": int(os.environ.get("BIOHUB_EDGEFILTER_SKIP_FORKS", "1")),' + NL
    + '}' + NL
)
EDGEFILTER_DISPLAY = '    "edgefilter_params": EDGEFILTER_PARAMS,' + NL
EDGEFILTER_FN = r'''def edgefilter_final_graph(
    nodes_by_id: dict[int, dict[str, object]],
    edges: list[dict[str, object]],
    stats: dict[str, int],
    params: dict[str, object],
    ilp_probs: dict[tuple[int, int], float] | None = None,
) -> tuple[dict[int, dict[str, object]], list[dict[str, object]]]:
    """Plan L5: drop (optionally re-link) weak motion-relink edges of the FINAL graph (after linefit).

    Candidate = an edge with a finite edge_prob below params["max_prob"] (the motion relink stores 0.0 for pairs the
    network never scored; scored pairs have p >= 0.4; gap and safe-division edges carry None and are never touched),
    whose target is on the next frame, whose current length (um) is >= params["min_len_um"], whose source is not a
    fork when params["skip_forks"], and which has the ILP evidence params["alt"] asks for (ilp_probs = the linker's
    own edges {(source, target): p} as filter_output_graph received them, after its next-frame / length filter):
      0 none; 1 the source had another ILP successor; 2 the target had another ILP predecessor; 3 either;
      4 a FREE ILP alternative: an ILP successor of the source on the next frame without a predecessor in the graph,
        or an ILP predecessor of the target on the previous frame without a successor.
    Candidates are handled in (t, source, target) order. relink=1 replaces a dropped edge by source -> free ILP
    successor (best p), else free ILP predecessor -> target; an end point is claimed once. prune=1 removes nodes left
    without any edge. Deterministic, independent of dict order.
    """
    if not int(params.get("enable", 0)) or not edges or not nodes_by_id:
        return nodes_by_id, edges
    max_prob = float(params.get("max_prob", 0.3))
    min_len = float(params.get("min_len_um", 0.0))
    alt_mode = int(params.get("alt", 0))
    relink = bool(int(params.get("relink", 0)))
    skip_forks = bool(int(params.get("skip_forks", 1)))
    ilp_probs = ilp_probs or {}
    ilp_succ: dict[int, list[tuple[int, float]]] = {}
    ilp_pred: dict[int, list[tuple[int, float]]] = {}
    for (a, b), p in sorted(ilp_probs.items()):
        ilp_succ.setdefault(int(a), []).append((int(b), float(p)))
        ilp_pred.setdefault(int(b), []).append((int(a), float(p)))
    out_degree: dict[int, int] = {}
    in_degree: dict[int, int] = {}
    for edge in edges:
        out_degree[int(edge["source_id"])] = out_degree.get(int(edge["source_id"]), 0) + 1
        in_degree[int(edge["target_id"])] = in_degree.get(int(edge["target_id"]), 0) + 1

    def free_successor(source_id: int, target_id: int) -> tuple[int, float] | None:
        t_next = int(nodes_by_id[source_id]["t"]) + 1
        free = [(c, p) for c, p in ilp_succ.get(source_id, []) if c != target_id and c in nodes_by_id
                and in_degree.get(c, 0) == 0 and int(nodes_by_id[c]["t"]) == t_next]
        return max(free, key=lambda item: (item[1], -item[0])) if free else None

    def free_predecessor(source_id: int, target_id: int) -> tuple[int, float] | None:
        t_prev = int(nodes_by_id[target_id]["t"]) - 1
        free = [(c, p) for c, p in ilp_pred.get(target_id, []) if c != source_id and c in nodes_by_id
                and out_degree.get(c, 0) == 0 and int(nodes_by_id[c]["t"]) == t_prev]
        return max(free, key=lambda item: (item[1], -item[0])) if free else None

    candidates: list[tuple[int, int, int, int]] = []
    for index, edge in enumerate(edges):
        prob = edge.get("edge_prob")
        if prob is None:
            continue
        try:
            prob = float(prob)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(prob) or prob >= max_prob:
            continue
        source_id = int(edge["source_id"])
        target_id = int(edge["target_id"])
        source = nodes_by_id.get(source_id)
        target = nodes_by_id.get(target_id)
        if source is None or target is None or int(target["t"]) != int(source["t"]) + 1:
            continue
        if skip_forks and out_degree.get(source_id, 0) >= 2:
            continue
        if min_len > 0.0 and edge_distance_um(source, target) < min_len:
            continue
        if alt_mode:
            other_succ = any(c != target_id for c, _ in ilp_succ.get(source_id, []))
            other_pred = any(c != source_id for c, _ in ilp_pred.get(target_id, []))
            if alt_mode == 1 and not other_succ:
                continue
            if alt_mode == 2 and not other_pred:
                continue
            if alt_mode == 3 and not (other_succ or other_pred):
                continue
            if alt_mode == 4 and free_successor(source_id, target_id) is None \
                    and free_predecessor(source_id, target_id) is None:
                continue
        candidates.append((int(source["t"]), source_id, target_id, index))
    stats["edgefilter_candidates"] = len(candidates)
    if not candidates:
        return nodes_by_id, edges
    candidates.sort()
    drop: set[int] = set()
    added: list[dict[str, object]] = []
    relinked_fwd = relinked_bwd = 0
    for _, source_id, target_id, index in candidates:
        drop.add(index)
        out_degree[source_id] -= 1
        in_degree[target_id] -= 1
        if not relink:
            continue
        choice = free_successor(source_id, target_id)
        if choice is not None:
            new_source, new_target = source_id, choice[0]
            relinked_fwd += 1
        else:
            choice = free_predecessor(source_id, target_id)
            if choice is None:
                continue
            new_source, new_target = choice[0], target_id
            relinked_bwd += 1
        out_degree[new_source] = out_degree.get(new_source, 0) + 1
        in_degree[new_target] = in_degree.get(new_target, 0) + 1
        added.append({
            "source_id": new_source,
            "target_id": new_target,
            "edge_prob": float(choice[1]),
            "distance_um": edge_distance_um(nodes_by_id[new_source], nodes_by_id[new_target]),
            "edgefilter_relinked": 1,
        })
    edges = [edge for index, edge in enumerate(edges) if index not in drop] + added
    stats["edgefilter_dropped"] = len(drop)
    stats["edgefilter_relinked_fwd"] = relinked_fwd
    stats["edgefilter_relinked_bwd"] = relinked_bwd
    if int(params.get("prune", 0)):
        incident = {int(edge["source_id"]) for edge in edges} | {int(edge["target_id"]) for edge in edges}
        kept = {node_id: node for node_id, node in nodes_by_id.items() if node_id in incident}
        stats["edgefilter_pruned_nodes"] = len(nodes_by_id) - len(kept)
        nodes_by_id = kept
    return nodes_by_id, edges
'''
# ILP pairs as filter_output_graph holds them after its own next-frame / max-length filter, before the motion relink
# replaces them (the relink's learned_edge_probs are built from the same list).
EDGEFILTER_CAPTURE = r'''    # edgefilter: the linker's own edges (after the next-frame / length filter), for the post-linefit re-link
    _ef_ilp_probs: dict[tuple[int, int], float] = {}
    for _ef_edge in edges:
        _ef_p = _ef_edge.get("edge_prob")
        if _ef_p is None:
            continue
        try:
            _ef_p = float(_ef_p)
        except (TypeError, ValueError):
            continue
        if np.isfinite(_ef_p):
            _ef_key = (int(_ef_edge["source_id"]), int(_ef_edge["target_id"]))
            _ef_ilp_probs[_ef_key] = max(_ef_ilp_probs.get(_ef_key, float("-inf")), _ef_p)
'''
EDGEFILTER_CALL = r'''    # ---- edgefilter (plan L5): drop / re-link unscored relink edges; EDGEFILTER_PARAMS["enable"] = 0 -> no-op ----
    if int(EDGEFILTER_PARAMS.get("enable", 0)):
        nodes_by_id, edges = edgefilter_final_graph(nodes_by_id, edges, stats, EDGEFILTER_PARAMS, _ef_ilp_probs)
        print(f"  [{dataset}] edgefilter: candidates={stats.get('edgefilter_candidates', 0)}"
              f" dropped={stats.get('edgefilter_dropped', 0)} relinked={stats.get('edgefilter_relinked_fwd', 0)}"
              f"+{stats.get('edgefilter_relinked_bwd', 0)} pruned={stats.get('edgefilter_pruned_nodes', 0)}")
    # ---- /edgefilter ----
'''
_EF_RELINK_ANCHOR = ("    if OUTPUT_MOTION_RELINK:" + NL
                     + "        learned_edge_probs: dict[tuple[int, int], float] = {}" + NL)
_EF_FILTER_DEF = NL + NL + NL + "def filter_output_graph(" + NL


def edgefilter_config_source(c2: str) -> str:
    """Config cell (base code cell 2): EDGEFILTER_PARAMS from the BIOHUB_EDGEFILTER_* knobs + its CONFIG_DISPLAY line
    (anchored on the linefit WEIGHT lines, so it composes with --patch leafprune, which anchors on the WINDOW lines)."""
    c2 = _rep1(c2, EDGEFILTER_KNOB_LINE, EDGEFILTER_KNOB_LINE + NL + EDGEFILTER_KNOB)
    return _rep1(c2, EDGEFILTER_DISPLAY_LINE, EDGEFILTER_DISPLAY_LINE + EDGEFILTER_DISPLAY)


def edgefilter_postproc_source(c7: str) -> str:
    """Post-processing cell (base code cell 7): edgefilter_final_graph before filter_output_graph, the ILP capture
    before the motion relink, and the guarded call right after linefit_smooth_output_graph (and before the divinsert
    call when that patch is applied too, in either order: the replay runs the filter on the post-tail graph and the
    insertion after it). Counters are set by the function itself (no stats-dict anchor: composes with leafprune)."""
    c7 = _rep1(c7, _EF_FILTER_DEF, NL + NL + NL + EDGEFILTER_FN + _EF_FILTER_DEF)
    c7 = _rep1(c7, _EF_RELINK_ANCHOR, EDGEFILTER_CAPTURE + _EF_RELINK_ANCHOR)
    return _rep1(c7, _LP_LINEFIT_CALL, _LP_LINEFIT_CALL + EDGEFILTER_CALL)


def patch_edgefilter(cells_src: dict) -> None:
    """Plan L5 (2026-09-24): edge anatomy filter. Knobs via --set EDGEFILTER_ENABLE=1 EDGEFILTER_MAX_PROB=...
    EDGEFILTER_ALT=... EDGEFILTER_MIN_LEN_UM=... EDGEFILTER_RELINK=... EDGEFILTER_PRUNE=... EDGEFILTER_SKIP_FORKS=...;
    default EDGEFILTER_ENABLE=0 = exact no-op (the capture only builds a dict nothing else reads)."""
    cells_src[2] = edgefilter_config_source(cells_src[2])
    cells_src[7] = edgefilter_postproc_source(cells_src[7])


PATCHES = {"gshift": patch_gshift, "divinsert": patch_divinsert, "leafprune": patch_leafprune,
           "edgefilter": patch_edgefilter}
META_PATCHES = {"divinsert": meta_divinsert}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="folder/kernel name, e.g. exp40_relink_off (lowercase, digits, _ or -)")
    ap.add_argument("--set", action="append", default=[], help="KNOB=value (without BIOHUB_), repeatable")
    ap.add_argument("--divnet", choices=["0", "1"], default="1", help="DivNet veto on (1, exp39) or off (0, exp29)")
    ap.add_argument("--note", default="", help="one line for probe.json")
    ap.add_argument("--patch", action="append", default=[], choices=sorted(PATCHES), help="code surgery to apply, repeatable")
    ap.add_argument("--dataset", action="append", default=[], help="extra Kaggle dataset source owner/slug, repeatable")
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]+", a.name):
        sys.exit("name must be lowercase letters/digits/_/-")
    overrides = {}
    for item in a.set:
        k, _, v = item.partition("=")
        if not k or not _:
            sys.exit(f"bad --set {item!r}")
        overrides["BIOHUB_" + k.strip().removeprefix("BIOHUB_")] = v.strip()
    if any(k.startswith("BIOHUB_DIVINS_") for k in overrides) and "divinsert" not in a.patch:
        # without the patch no code reads these knobs: the probe would silently be exp39
        sys.exit("DIVINS_* knobs need --patch divinsert")
    if "divinsert" in a.patch and overrides.get("BIOHUB_DIVINS_ENABLE", "0") == "0":
        print("NOTE: --patch divinsert with DIVINS_ENABLE=0 (default) builds an exact no-op of the base")
    if "BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB" in overrides:
        if "leafprune" not in a.patch:
            # the base notebook has no prune_weak_leaf_nodes: the knob would be read by nothing
            sys.exit("LEAF_PRUNE_MIN_EDGE_PROB needs --patch leafprune")
        try:
            _lp = float(overrides["BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB"])
        except ValueError:
            sys.exit(f"LEAF_PRUNE_MIN_EDGE_PROB must be a number, got {overrides['BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB']!r}")
        if _lp != _lp or _lp in (float("inf"), float("-inf")):
            # nan would silently skip the call, inf would prune every leaf with a finite edge_prob; the replay refuses both
            sys.exit(f"LEAF_PRUNE_MIN_EDGE_PROB must be finite, got {overrides['BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB']!r}")
    if "leafprune" in a.patch and float(overrides.get("BIOHUB_LEAF_PRUNE_MIN_EDGE_PROB", "0")) <= 0.0:
        print("NOTE: --patch leafprune with LEAF_PRUNE_MIN_EDGE_PROB<=0 (default 0.0) builds an exact no-op of the "
              "base")
    ef_knobs = {"BIOHUB_" + knob: default for knob, default in EDGEFILTER_KNOBS.values()}
    if any(k.startswith("BIOHUB_EDGEFILTER_") for k in overrides):
        if "edgefilter" not in a.patch:
            sys.exit("EDGEFILTER_* knobs need --patch edgefilter")
        unknown = sorted(k for k in overrides if k.startswith("BIOHUB_EDGEFILTER_") and k not in ef_knobs)
        if unknown:
            sys.exit(f"unknown edgefilter knobs {unknown}; known: {sorted(ef_knobs)}")
        for k in overrides:
            if k in ef_knobs:
                try:
                    value = float(overrides[k])
                except ValueError:
                    sys.exit(f"{k} must be a number, got {overrides[k]!r}")
                if value != value or value in (float("inf"), float("-inf")):
                    sys.exit(f"{k} must be finite, got {overrides[k]!r}")
                if ef_knobs[k].isdigit() and not re.fullmatch(r"-?\d+", overrides[k]):  # the config cell calls int()
                    sys.exit(f"{k} must be an integer literal, got {overrides[k]!r}")
    if "edgefilter" in a.patch and overrides.get("BIOHUB_EDGEFILTER_ENABLE", "0") in ("0", "0.0"):
        print("NOTE: --patch edgefilter with EDGEFILTER_ENABLE=0 (default) builds an exact no-op of the base")
    overrides["BIOHUB_DIVNET_VERIFY"] = a.divnet

    nb = json.load(open(BASE_NB, encoding="utf-8"))
    cells = nb["cells"]
    code = [i for i, c in enumerate(cells) if c["cell_type"] == "code"]

    def src(i):
        return "".join(cells[i]["source"])

    def set_src(i, s):
        cells[i]["source"] = s.splitlines(keepends=True)
        cells[i]["outputs"] = []
        cells[i]["execution_count"] = None

    c0 = src(code[0])
    assert "BIOHUB_PRESET = 'exp39_sjlee947_tight55_divnetveto'" in c0
    c0 = c0.replace("BIOHUB_PRESET = 'exp39_sjlee947_tight55_divnetveto'", f"BIOHUB_PRESET = '{a.name}'")
    block = NL + f"# ---- {a.name}: probe overrides (tools/build_probe_kernel.py) ----" + NL
    block += NL.join(f'os.environ["{k}"] = "{v}"' for k, v in overrides.items()) + NL
    c0 = c0.rstrip(NL) + NL + block
    set_src(code[0], c0)

    c1 = src(code[1])
    for k, v in overrides.items():
        m = re.search(r'^(\s*"%s": )([^,\n]+),' % re.escape(k), c1, re.M)
        if m:
            c1 = c1[:m.start(2)] + (v if re.fullmatch(r"-?\d+(\.\d+)?", v) else json.dumps(v)) + c1[m.end(2):]
    set_src(code[1], c1)

    if a.patch:
        # patches always see the BASE code-cell indices (cell 7 = post-processing); new cells go in afterwards
        cells_src = {k: src(code[k]) for k in range(len(code))}
        for name in a.patch:
            PATCHES[name](cells_src)
        new_cells = cells_src.pop(NEW_CELLS_KEY, [])
        for k, s in cells_src.items():
            if s != src(code[k]):
                set_src(code[k], s)
        for after in sorted({k for k, _ in new_cells}, reverse=True):
            for s in reversed([s for k, s in new_cells if k == after]):
                cells.insert(code[after] + 1, {"cell_type": "code", "execution_count": None, "metadata": {},
                                               "outputs": [], "source": s.splitlines(keepends=True)})
        code = [i for i, c in enumerate(cells) if c["cell_type"] == "code"]
        overrides["PATCHES"] = "+".join(a.patch)

    for i in code:
        compile(src(i), f"cell{i}", "exec")
    out_dir = ROOT / "experiments" / a.name
    out_dir.mkdir(exist_ok=True)
    nb_name = a.name.replace("_", "-") + ".ipynb"
    json.dump(nb, open(out_dir / nb_name, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    meta = json.load(open(BASE_DIR / "kernel-metadata.json"))
    slug = "biohub-" + a.name.replace("_", "-")
    meta["id"] = "vitaliineibauer/" + slug
    meta["title"] = slug
    meta["code_file"] = nb_name
    for name in a.patch:
        if name in META_PATCHES:
            META_PATCHES[name](meta, overrides)
    for ds in a.dataset:
        if ds not in meta["dataset_sources"]:
            meta["dataset_sources"].append(ds)
    json.dump(meta, open(out_dir / "kernel-metadata.json", "w", encoding="utf-8"), indent=1)
    probe = {
        "base": "exp29 realised config (tight55, pilkwang primary, validator off) = LB 0.947; built by tools/build_probe_kernel.py from the exp39 notebook",
        "change": {k.removeprefix("BIOHUB_"): v for k, v in overrides.items()},
        "note": a.note,
        "rule": "compare with exp29 0.947; >= 0.950 adopt; ties recorded; <= 0.944 drop",
    }
    json.dump(probe, open(out_dir / "probe.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("built", out_dir.relative_to(ROOT), "overrides", overrides)
    if a.push:
        r = subprocess.run([sys.executable, "-m", "kaggle", "kernels", "push", "-p", str(out_dir)])
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
