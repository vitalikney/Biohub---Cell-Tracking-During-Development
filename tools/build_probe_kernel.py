"""Build an LB-probe kernel = exp29 realised config + env-knob overrides (+ optional DivNet veto), one command.

    python tools/build_probe_kernel.py exp40_relink_off --set MOTION_RELINK_TIGHT_UM=0 --set DEEPCENTER_GAP_THRESHOLD=0.35 \
        --divnet 0 --note "relink off" [--push]

Base = experiments/exp39_sjlee947_tight55_divnetveto (exp29 + DivNet veto cell). `--divnet 0` disables the veto through
BIOHUB_DIVNET_VERIFY=0 (the cell stays, the model is not loaded), so `--divnet 0` with no --set is exp29 bit-for-bit.
Knob names are given WITHOUT the BIOHUB_ prefix. Overrides are appended to the config cell AFTER the base values and the
configuration guard's expected values are patched for the keys it checks. Output folder:
experiments/<name>/ with the notebook, kernel-metadata.json and probe.json; `--push` runs `kaggle kernels push`.

`--base x138` (default exp39): base = experiments/exp56_x138_verbatim (anvithpothula/biohub-x138 byte-identical, public
0.953, sha256-checked; its kernel-metadata.json = x138's datasets, docker pin and machine shape). Only --patch divinsert
and --patch leafprune are supported there (same patch code, x138's cell indices: config 2, predict-patch 4,
post-processing 5; no DivNet cell, so divinsert also adds the DivNet helper definitions its DaughterNet builds on, taken
verbatim from the exp39 DivNet cell, without loading DivNet or installing the veto). x138's preset name is kept, the
override block is appended only when there are overrides, there is no BIOHUB_DIVNET_VERIFY (no --divnet), and the
notebook is written in x138's compact JSON: with no --patch and no --set the output is byte-identical to x138.

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
  stitch     plan L6 FN-anatomy stitch: cell 2 STITCH_PARAMS from BIOHUB_STITCH_{ENABLE,MIN_PROB,MAX_UM,MIN_UM,MIN_CHAIN}
             (ENABLE default 0 = exact no-op) + cell 7 stitch_final_graph, its own capture of the linker's edges before
             the motion relink, and a guarded call after linefit AND after the edgefilter call, before the divinsert
             call (any patch order). Re-adds the linker's own edges whose source is a track end and whose target is a
             track start. Replay: config keys st.<param>, same function text.
  swapfix    plan L6b motion 2x2 swap: cell 2 SWAPFIX_PARAMS from BIOHUB_SWAPFIX_{ENABLE,MIN_GAIN_UM,MIN_RATIO,MAX_PROB,
             SRC_UM,MAX_LEN_UM,MIN_TERMS} (ENABLE default 0 = exact no-op) + cell 7 swapfix_final_graph and a guarded
             call after linefit / edgefilter, before stitch / divinsert (any patch order). Replay: sw.<param>.
  coordhead  x138's V1284 coordinate-refinement head (anvithpothula/biohub-x138, public 0.953), x138's lines verbatim:
             cell 5 (predict-script patch cell) gets a block guarded by BIOHUB_COORDHEAD_ENABLE (default 0 = exact
             no-op, the predict script is not touched) that writes the head module, removes the int16 cast (float
             coordinates end to end), refines each peak (<= 2 um) and swaps in the trilinear feature gather; plus
             per-video shift stats (COORDHEAD_STATS log lines, coordhead_stats_*.jsonl) and a summary after
             prediction. COORDHEAD_MODE=candidate (default) | zero | capture. With ENABLE != 0 the CC0 dataset
             anvithpothula/biohub-v1284-head-s075 is attached. COORDHEAD_HEAD_PATH (default "" = the public head,
             exact no-op) loads our own head file instead (tools/train_coordhead.py output, same format), e.g.
             --set COORDHEAD_HEAD_PATH=biohub-coordhead-199/v1284_head.pt (that dataset is attached automatically).
  floatout   float output coordinates (wf_ideas_v2 "float-output-coords"): write_test_submission (cell 7) writes node
             z/y/x through floatout_zyx; knob BIOHUB_OUTPUT_FLOAT_COORDS = 0 (default: the base writer's integers,
             byte-identical submission.csv) | safe (w = max(0, r + min(max(round(v - r, 3), 0), 0.499)), r = round(v):
             floor(w) == r) | float (v); both clipped to [0, dim - 1] and written as f"{w:.3f}" on every node row; t, ids
             and the edge rows' -1 stay integers. A new last cell re-reads submission.csv like royerlab csv_to_geffs.py
             (polars, z/y/x as Float64) and asserts decimal points, floor(w) == round(v) (safe), ranges and node/edge
             counts. Replay: config key out.coords=round|safe|float.
  safetail   (x138 base only; ideas workflow v3 E1) runtime insurance, applied after every other patch: requires
             --set REPAIR_DEADLINE_S=34200 (any other value needs --lab); DaughterNet insertion runs only while the
             repair deadline has not fired and the kernel is younger than BIOHUB_DIVINS_DEADLINE_S (default 28800;
             'DIVINS SKIPPED (deadline)'), inside try/except (input edges kept, 'DIVINS FAILED'); BIOHUB_DEGRADE_KEEP_DIV
             (set to 1) keeps safe divisions + linefit after the deadline. --lab builds (dummy only, never submit) may
             set REPAIR_DEADLINE_S=1 (FD test), DIVINS_FORCE_FAIL=1 (FF test) and DIVINS_DUMP=1.
  lowrefine  (x138 base only; ideas workflow v3 E2 = C05) x138's low-detection pool (readmit / gapfill) gets the V1284
             head's coordinates for its rows with score >= BIOHUB_READMIT_MIN_SCORE (0.965: exactly the main peaks the
             head already refined before the ILP); 0.5-0.965 rows stay on the grid; the pool's int16 cast is dropped
             (float32). Edits only the 'lowdet' literals of the predict-patch cell (order lowdet -> V1284 unchanged).
             Knob BIOHUB_LOWREFINE_ENABLE (the patch sets 1; 0 = byte-identical CSV). A refine exception keeps that
             frame's grid coordinates and logs 'LOWREFINE FAILED'; per video 'LOWREFINE <name>: refined R of N ...'.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = ROOT / "experiments/exp39_sjlee947_tight55_divnetveto"
BASE_NB = BASE_DIR / "exp39-sjlee947-tight55-divnetveto.ipynb"
NL = chr(10)
# Bases: notebook, metadata folder and the CODE-cell indices the patches address (config constants, predict-script
# patch cell, DivNet cell or None, post-processing cell with filter_output_graph + the writer).
X138_DIR = ROOT / "experiments/exp56_x138_verbatim"
BASES = {
    "exp39": {"dir": BASE_DIR, "nb": BASE_NB, "sha256": None, "compact": False,
              "config": 2, "predict": 5, "divnet": 6, "post": 7, "patches": None},
    "x138": {"dir": X138_DIR, "nb": X138_DIR / "exp56-x138-verbatim.ipynb",
             # = experiments/ext_x138/biohub-x138.ipynb as pulled from anvithpothula/biohub-x138
             "sha256": "6b655e39bbfd2d3d6c762badea69847d3f00f5b548f385cb01b07ee2600fde6d", "compact": True,
             "config": 2, "predict": 4, "divnet": None, "post": 5,
             "patches": ("divinsert", "leafprune", "safetail")},
}
CELL = dict(BASES["exp39"])  # the active base's cell indices; main() sets it from --base before any patch runs


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


def _tail_anchor(c7: str, anchor: str, calls: tuple[str, ...]) -> str:
    """Extend `anchor` over the post-linefit calls already present, in the fixed tail order (names of module-level
    call-text constants, resolved lazily: linefit -> edgefilter -> swapfix -> stitch -> divinsert)."""
    for name in calls:
        text = globals()[name]
        if anchor + text in c7:
            anchor += text
    return anchor


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
    after = CELL["divnet"]
    if after is None:
        # base without the exp39 DivNet cell (x138): the helper definitions go first, both cells after the prediction
        # cell and before post-processing (the same slot as exp39's DivNet + divinsert cells)
        after = CELL["predict"]
        cells_src.setdefault(NEW_CELLS_KEY, []).append((after, divnet_helpers_cell()))
    cells_src.setdefault(NEW_CELLS_KEY, []).append((after, cell))
    post = CELL["post"]
    c7 = cells_src[post]
    c7 = _rep1(c7, '''                "x": refined_point[2],
            }
            inserted_ids.append(node_id)
''', '''                "x": refined_point[2],
                "gap2_synthetic": 1,  # divinsert: node flag (gap2 nodes had none); no downstream reader
            }
            inserted_ids.append(node_id)
''')
    anchor = '    nodes_by_id = linefit_smooth_output_graph(nodes_by_id, edges, stats)' + NL
    # patches applied before this one keep the replay's order: linefit -> edgefilter -> swapfix -> stitch -> insertion
    anchor = _tail_anchor(c7, anchor, ("EDGEFILTER_CALL", "SWAPFIX_CALL", "STITCH_CALL"))
    c7 = _rep1(c7, anchor, anchor + DIVINS_CALL)
    cells_src[post] = c7


def divnet_helpers_cell() -> str:
    """For a base without a DivNet cell (x138): tools/daughternet.py builds on _DivNetConvBlock and prepare_divnet_input
    (its import falls back to the notebook globals). The exp39 DivNet cell's module text up to the model loading is
    taken VERBATIM (the definitions exp48's DaughterNet ran with; tools/divnet_infer.py has since diverged: it drops
    frames from the shared cache); DIVNET_VERIFY / the model load / the veto helper are not included."""
    nb = json.load(open(BASE_NB, encoding="utf-8"))
    code = [c for c in nb["cells"] if c["cell_type"] == "code"]
    s = "".join(code[BASES["exp39"]["divnet"]]["source"])
    body = s[s.index('"""Inference for the public'):s.index(NL + "DIVNET_VERIFY = os.environ.get(")].rstrip(NL) + NL
    for need in ("from __future__ import annotations", "class _DivNetConvBlock(", "def prepare_divnet_input("):
        assert body.count(need) == 1, need
    assert "load_divnet_mitosis_model()" not in body
    return ("# ---- divinsert helpers (tools/build_probe_kernel.py --patch divinsert on a base without a DivNet cell): the" + NL
            + "# DivNet conv block and input preparation that the DaughterNet cell below builds on, verbatim from the exp39" + NL
            + "# DivNet cell (the code exp48 ran). Definitions only: no DivNet model is loaded and no veto is installed." + NL
            + body)


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
    cells_src[CELL["config"]] = leafprune_config_source(cells_src[CELL["config"]])
    cells_src[CELL["post"]] = leafprune_postproc_source(cells_src[CELL["post"]])


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


# ---- stitch: plan L6 (FN anatomy, experiments/l2_daughternet/edge_anatomy/fn_anatomy.py). Restore the linker's own
# edges between a track END and a track START of the final graph (both ends left free by the motion relink, whose gates
# drop the ILP's long displacements, and by everything after it). Applied at the END of the tail: after linefit and
# after the edgefilter call, before the divinsert call (any patch order). The replay lab (config keys st.<param>)
# applies the same source text to its notebook cells and calls the same function on the post-tail(+ef) graph.
STITCH_KNOB_LINE = 'OUTPUT_LINEFIT_SMOOTH = os.environ.get("BIOHUB_OUTPUT_LINEFIT_SMOOTH", "1") != "0"' + NL
STITCH_DISPLAY_LINE = '    "output_linefit_smooth": OUTPUT_LINEFIT_SMOOTH,' + NL
# replay param -> kernel knob (without BIOHUB_), with the kernel default; the function reads a dict with these keys
STITCH_KNOBS = {"enable": ("STITCH_ENABLE", "0"), "min_prob": ("STITCH_MIN_PROB", "0.0"),
                "max_um": ("STITCH_MAX_UM", "0.0"), "min_um": ("STITCH_MIN_UM", "0.0"),
                "min_chain": ("STITCH_MIN_CHAIN", "0")}
STITCH_KNOB = (
    "# stitch (plan L6): re-add the linker's own end->start edges after linefit (+ edgefilter); ENABLE=0 = inert" + NL
    + 'STITCH_PARAMS = {' + NL
    + '    "enable": int(os.environ.get("BIOHUB_STITCH_ENABLE", "0")),' + NL
    + '    "min_prob": float(os.environ.get("BIOHUB_STITCH_MIN_PROB", "0.0")),' + NL
    + '    "max_um": float(os.environ.get("BIOHUB_STITCH_MAX_UM", "0.0")),' + NL
    + '    "min_um": float(os.environ.get("BIOHUB_STITCH_MIN_UM", "0.0")),' + NL
    + '    "min_chain": int(os.environ.get("BIOHUB_STITCH_MIN_CHAIN", "0")),' + NL
    + '}' + NL
)
STITCH_DISPLAY = '    "stitch_params": STITCH_PARAMS,' + NL
STITCH_FN = r'''def stitch_final_graph(
    nodes_by_id: dict[int, dict[str, object]],
    edges: list[dict[str, object]],
    stats: dict[str, int],
    params: dict[str, object],
    ilp_probs: dict[tuple[int, int], float] | None = None,
) -> tuple[dict[int, dict[str, object]], list[dict[str, object]]]:
    """Plan L6: re-add the linker's own edges between a track END and a track START of the FINAL graph.

    ilp_probs = the linker's own edges {(source, target): p} as filter_output_graph received them (after its next-frame
    / length filter). The motion relink replaces them; the ILP links it cannot place inside its gates (mostly
    displacements > 10 um) are lost even when both nodes stay free to the end of the tail. Candidate = an ILP edge whose
    two nodes are in the graph, target on the next frame, source without a successor (a track end), target without a
    predecessor (a track start), p >= params["min_prob"], current length (um) in [params["min_um"], params["max_um"]]
    (max_um 0 = no upper limit), and - with params["min_chain"] = k > 0 - at least k edges of linear chain above the
    source and below the target. Added in order of p descending, then (t, source, target), each node used once (the
    linker's solution is one-to-one already). No node is added or removed. Deterministic, independent of dict order.
    """
    if not int(params.get("enable", 0)) or not edges or not nodes_by_id or not ilp_probs:
        return nodes_by_id, edges
    min_prob = float(params.get("min_prob", 0.0))
    max_um = float(params.get("max_um", 0.0))
    min_um = float(params.get("min_um", 0.0))
    min_chain = int(params.get("min_chain", 0))
    successors: dict[int, list[int]] = {}
    predecessors: dict[int, list[int]] = {}
    for edge in edges:
        successors.setdefault(int(edge["source_id"]), []).append(int(edge["target_id"]))
        predecessors.setdefault(int(edge["target_id"]), []).append(int(edge["source_id"]))
    max_t = max(int(node["t"]) for node in nodes_by_id.values())

    def chain_up(node_id: int, need: int) -> int:
        steps = 0
        while steps < need:
            parents = predecessors.get(node_id, [])
            if len(parents) != 1 or len(successors.get(parents[0], [])) != 1:
                break
            node_id = parents[0]
            steps += 1
        return steps

    def chain_down(node_id: int, need: int) -> int:
        steps = 0
        while steps < need:
            children = successors.get(node_id, [])
            if len(children) != 1 or len(predecessors.get(children[0], [])) != 1:
                break
            node_id = children[0]
            steps += 1
        return steps

    candidates: list[tuple[float, int, int, int, float]] = []
    for (source_id, target_id), prob in sorted(ilp_probs.items()):
        source = nodes_by_id.get(int(source_id))
        target = nodes_by_id.get(int(target_id))
        if source is None or target is None:
            continue
        source_id, target_id, prob = int(source_id), int(target_id), float(prob)
        if not np.isfinite(prob) or prob < min_prob:
            continue
        if int(target["t"]) != int(source["t"]) + 1 or int(source["t"]) >= max_t:
            continue
        if successors.get(source_id) or predecessors.get(target_id):
            continue
        length = float(edge_distance_um(source, target))
        if length < min_um or (max_um > 0.0 and length > max_um):
            continue
        if min_chain > 0 and (chain_up(source_id, min_chain) < min_chain or chain_down(target_id, min_chain) < min_chain):
            continue
        candidates.append((-prob, int(source["t"]), source_id, target_id, length))
    stats["stitch_candidates"] = len(candidates)
    if not candidates:
        return nodes_by_id, edges
    candidates.sort()
    used_sources: set[int] = set()
    used_targets: set[int] = set()
    added: list[dict[str, object]] = []
    for neg_prob, _, source_id, target_id, length in candidates:
        if source_id in used_sources or target_id in used_targets:
            continue
        used_sources.add(source_id)
        used_targets.add(target_id)
        added.append({
            "source_id": source_id,
            "target_id": target_id,
            "edge_prob": -neg_prob,
            "distance_um": length,
            "stitched": 1,
        })
    stats["stitch_added"] = len(added)
    return nodes_by_id, edges + added
'''
STITCH_CAPTURE = r'''    # stitch: the linker's own edges (after the next-frame / length filter), for the post-linefit end->start stitch
    _st_ilp_probs: dict[tuple[int, int], float] = {}
    for _st_edge in edges:
        _st_p = _st_edge.get("edge_prob")
        if _st_p is None:
            continue
        try:
            _st_p = float(_st_p)
        except (TypeError, ValueError):
            continue
        if np.isfinite(_st_p):
            _st_key = (int(_st_edge["source_id"]), int(_st_edge["target_id"]))
            _st_ilp_probs[_st_key] = max(_st_ilp_probs.get(_st_key, float("-inf")), _st_p)
'''
STITCH_CALL = r'''    # ---- stitch (plan L6): re-add the linker's own end->start edges; STITCH_PARAMS["enable"] = 0 -> no-op ----
    if int(STITCH_PARAMS.get("enable", 0)):
        nodes_by_id, edges = stitch_final_graph(nodes_by_id, edges, stats, STITCH_PARAMS, _st_ilp_probs)
        print(f"  [{dataset}] stitch: candidates={stats.get('stitch_candidates', 0)}"
              f" added={stats.get('stitch_added', 0)}")
    # ---- /stitch ----
'''


def stitch_config_source(c2: str) -> str:
    """Config cell (base code cell 2): STITCH_PARAMS from the BIOHUB_STITCH_* knobs + its CONFIG_DISPLAY line (anchored
    on the linefit SMOOTH lines: composes with --patch leafprune (WINDOW) and --patch edgefilter (WEIGHT))."""
    c2 = _rep1(c2, STITCH_KNOB_LINE, STITCH_KNOB_LINE + NL + STITCH_KNOB)
    return _rep1(c2, STITCH_DISPLAY_LINE, STITCH_DISPLAY_LINE + STITCH_DISPLAY)


def stitch_postproc_source(c7: str) -> str:
    """Post-processing cell (base code cell 7): stitch_final_graph before filter_output_graph, the ILP capture before the
    motion relink, and the guarded call after linefit AND after the edgefilter call (if that patch is or will be
    applied: edgefilter always inserts its call directly after linefit) and before the divinsert call (divinsert
    anchors after this call when present). Counters are set by the function itself."""
    c7 = _rep1(c7, _EF_FILTER_DEF, NL + NL + NL + STITCH_FN + _EF_FILTER_DEF)
    c7 = _rep1(c7, _EF_RELINK_ANCHOR, STITCH_CAPTURE + _EF_RELINK_ANCHOR)
    anchor = _tail_anchor(c7, _LP_LINEFIT_CALL, ("EDGEFILTER_CALL", "SWAPFIX_CALL"))
    return _rep1(c7, anchor, anchor + STITCH_CALL)


def patch_stitch(cells_src: dict) -> None:
    """Plan L6 (2026-09-24): end->start stitch with the linker's own edges. Knobs via --set STITCH_ENABLE=1
    STITCH_MIN_PROB=... STITCH_MAX_UM=... STITCH_MIN_UM=... STITCH_MIN_CHAIN=...; default STITCH_ENABLE=0 = exact
    no-op (the capture only builds a dict nothing else reads)."""
    cells_src[2] = stitch_config_source(cells_src[2])
    cells_src[7] = stitch_postproc_source(cells_src[7])


# ---- swapfix: plan L6b (experiments/l2_daughternet/edge_anatomy/swap_anatomy.py). Local 2x2 re-assignment of the
# final graph's links between consecutive frames by a constant-velocity (second-difference) motion cost: a->b + c->d
# become a->d + c->b when that makes both trajectories markedly smoother. Applied after linefit and the edgefilter
# call, before the stitch and divinsert calls (any patch order). Replay: config keys sw.<param>, same function text.
SWAPFIX_KNOB_LINE = 'OUTPUT_PRUNE_ISOLATED = os.environ.get("BIOHUB_OUTPUT_PRUNE_ISOLATED", "1") != "0"' + NL
SWAPFIX_DISPLAY_LINE = '    "output_prune_isolated": OUTPUT_PRUNE_ISOLATED,' + NL
SWAPFIX_KNOBS = {"enable": ("SWAPFIX_ENABLE", "0"), "min_gain_um": ("SWAPFIX_MIN_GAIN_UM", "3.0"),
                 "min_ratio": ("SWAPFIX_MIN_RATIO", "0.0"), "max_prob": ("SWAPFIX_MAX_PROB", "1.01"),
                 "src_um": ("SWAPFIX_SRC_UM", "10.0"), "max_len_um": ("SWAPFIX_MAX_LEN_UM", "14.0"),
                 "min_terms": ("SWAPFIX_MIN_TERMS", "4")}
SWAPFIX_KNOB = (
    "# swapfix (plan L6b): motion-smoothness 2x2 re-assignment of final links; ENABLE=0 = inert" + NL
    + 'SWAPFIX_PARAMS = {' + NL
    + '    "enable": int(os.environ.get("BIOHUB_SWAPFIX_ENABLE", "0")),' + NL
    + '    "min_gain_um": float(os.environ.get("BIOHUB_SWAPFIX_MIN_GAIN_UM", "3.0")),' + NL
    + '    "min_ratio": float(os.environ.get("BIOHUB_SWAPFIX_MIN_RATIO", "0.0")),' + NL
    + '    "max_prob": float(os.environ.get("BIOHUB_SWAPFIX_MAX_PROB", "1.01")),' + NL
    + '    "src_um": float(os.environ.get("BIOHUB_SWAPFIX_SRC_UM", "10.0")),' + NL
    + '    "max_len_um": float(os.environ.get("BIOHUB_SWAPFIX_MAX_LEN_UM", "14.0")),' + NL
    + '    "min_terms": int(os.environ.get("BIOHUB_SWAPFIX_MIN_TERMS", "4")),' + NL
    + '}' + NL
)
SWAPFIX_DISPLAY = '    "swapfix_params": SWAPFIX_PARAMS,' + NL
SWAPFIX_FN = r'''def swapfix_final_graph(
    nodes_by_id: dict[int, dict[str, object]],
    edges: list[dict[str, object]],
    stats: dict[str, int],
    params: dict[str, object],
    ilp_probs: dict[tuple[int, int], float] | None = None,
) -> tuple[dict[int, dict[str, object]], list[dict[str, object]]]:
    """Plan L6b: swap two links between consecutive frames when a constant-velocity model strongly prefers it.

    Simple link = an edge a->b with a finite edge_prob (gap / safe-division edges, None, are never touched), target on
    the next frame, a with exactly one successor and b with exactly one predecessor. For two simple links a->b, c->d of
    the same frame pair whose sources lie within params["src_um"] of each other, the move is a->d + c->b (both new
    lengths <= params["max_len_um"]). Motion cost = sum of the second differences |x(t+1) - 2 x(t) + x(t-1)| (um, final
    float coordinates) at a, c (with their unique predecessors) and at b, d (with their unique successors), counted only
    for terms that exist before and after the move; at least params["min_terms"] such terms (4 = full context). A move
    is a candidate when cost_before - cost_after >= params["min_gain_um"], cost_after <= (1 - params["min_ratio"]) *
    cost_before, and both current edge_prob < params["max_prob"]. Candidates are applied by decreasing gain, each node
    in at most one move (so moves never interact). New links carry edge_prob 0.0 (a pair the linker did not choose).
    No node is added or removed. Deterministic, independent of dict order.
    """
    if not int(params.get("enable", 0)) or not edges or not nodes_by_id:
        return nodes_by_id, edges
    from scipy.spatial import cKDTree as _SwKDTree

    min_gain = float(params.get("min_gain_um", 3.0))
    min_ratio = float(params.get("min_ratio", 0.0))
    max_prob = float(params.get("max_prob", 1.01))
    src_um = float(params.get("src_um", 10.0))
    max_len = float(params.get("max_len_um", 14.0))
    min_terms = int(params.get("min_terms", 4))
    scale = np.asarray([1.625, 0.40625, 0.40625], dtype=np.float64)
    pos = {int(i): np.asarray([float(n["z"]), float(n["y"]), float(n["x"])], dtype=np.float64) * scale
           for i, n in nodes_by_id.items()}
    successors: dict[int, list[int]] = {}
    predecessors: dict[int, list[int]] = {}
    for edge in edges:
        successors.setdefault(int(edge["source_id"]), []).append(int(edge["target_id"]))
        predecessors.setdefault(int(edge["target_id"]), []).append(int(edge["source_id"]))
    simple_by_t: dict[int, list[tuple[int, int, int]]] = {}
    for index, edge in enumerate(edges):
        source_id, target_id = int(edge["source_id"]), int(edge["target_id"])
        prob = edge.get("edge_prob")
        if prob is None:
            continue
        try:
            prob = float(prob)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(prob) or prob >= max_prob:
            continue
        if source_id not in nodes_by_id or target_id not in nodes_by_id:
            continue
        t_source = int(nodes_by_id[source_id]["t"])
        if int(nodes_by_id[target_id]["t"]) != t_source + 1:
            continue
        if len(successors.get(source_id, [])) != 1 or len(predecessors.get(target_id, [])) != 1:
            continue
        simple_by_t.setdefault(t_source, []).append((source_id, target_id, index))

    def unique(items: list[int]) -> int | None:
        return items[0] if len(items) == 1 else None

    def second_diff(p0: int, p1: int, p2: int) -> float:
        return float(np.linalg.norm(pos[p2] - 2.0 * pos[p1] + pos[p0]))

    candidates: list[tuple[float, int, int, int, int, int, int, int]] = []
    for t in sorted(simple_by_t):
        links = sorted(simple_by_t[t])
        if len(links) < 2:
            continue
        tree = _SwKDTree(np.stack([pos[a] for a, _, _ in links]))
        for i, j in sorted(tree.query_pairs(src_um)):
            a, b, index_ab = links[i]
            c, d, index_cd = links[j]
            if float(np.linalg.norm(pos[d] - pos[a])) > max_len or float(np.linalg.norm(pos[b] - pos[c])) > max_len:
                continue
            before = after = 0.0
            terms = 0
            pa, pc = unique(predecessors.get(a, [])), unique(predecessors.get(c, []))
            sb, sd = unique(successors.get(b, [])), unique(successors.get(d, []))
            if pa is not None:
                before += second_diff(pa, a, b); after += second_diff(pa, a, d); terms += 1
            if pc is not None:
                before += second_diff(pc, c, d); after += second_diff(pc, c, b); terms += 1
            if sb is not None:
                before += second_diff(a, b, sb); after += second_diff(c, b, sb); terms += 1
            if sd is not None:
                before += second_diff(c, d, sd); after += second_diff(a, d, sd); terms += 1
            if terms < min_terms:
                continue
            gain = before - after
            if gain < min_gain or after > (1.0 - min_ratio) * before:
                continue
            candidates.append((-gain, t, a, b, c, d, index_ab, index_cd))
    stats["swapfix_candidates"] = len(candidates)
    if not candidates:
        return nodes_by_id, edges
    candidates.sort()
    used: set[int] = set()
    replace: dict[int, int] = {}
    for _neg_gain, _t, a, b, c, d, index_ab, index_cd in candidates:
        if a in used or b in used or c in used or d in used:
            continue
        used.update((a, b, c, d))
        replace[index_ab] = d
        replace[index_cd] = b
    new_edges: list[dict[str, object]] = []
    for index, edge in enumerate(edges):
        if index not in replace:
            new_edges.append(edge)
            continue
        source_id, target_id = int(edge["source_id"]), replace[index]
        new_edges.append({
            "source_id": source_id,
            "target_id": target_id,
            "edge_prob": 0.0,
            "distance_um": edge_distance_um(nodes_by_id[source_id], nodes_by_id[target_id]),
            "swapfix": 1,
        })
    stats["swapfix_swaps"] = len(replace) // 2
    return nodes_by_id, new_edges
'''
SWAPFIX_CALL = r'''    # ---- swapfix (plan L6b): motion 2x2 re-assignment; SWAPFIX_PARAMS["enable"] = 0 -> no-op ----
    if int(SWAPFIX_PARAMS.get("enable", 0)):
        nodes_by_id, edges = swapfix_final_graph(nodes_by_id, edges, stats, SWAPFIX_PARAMS)
        print(f"  [{dataset}] swapfix: candidates={stats.get('swapfix_candidates', 0)}"
              f" swaps={stats.get('swapfix_swaps', 0)}")
    # ---- /swapfix ----
'''


def swapfix_config_source(c2: str) -> str:
    """Config cell (base code cell 2): SWAPFIX_PARAMS from the BIOHUB_SWAPFIX_* knobs + its CONFIG_DISPLAY line
    (anchored on the OUTPUT_PRUNE_ISOLATED lines: composes with leafprune / edgefilter / stitch)."""
    c2 = _rep1(c2, SWAPFIX_KNOB_LINE, SWAPFIX_KNOB_LINE + NL + SWAPFIX_KNOB)
    return _rep1(c2, SWAPFIX_DISPLAY_LINE, SWAPFIX_DISPLAY_LINE + SWAPFIX_DISPLAY)


def swapfix_postproc_source(c7: str) -> str:
    """Post-processing cell (base code cell 7): swapfix_final_graph before filter_output_graph and the guarded call after
    linefit and the edgefilter call, before the stitch / divinsert calls (whichever patches come later anchor after it:
    edgefilter always goes directly after linefit, stitch and divinsert extend their anchors over this call)."""
    c7 = _rep1(c7, _EF_FILTER_DEF, NL + NL + NL + SWAPFIX_FN + _EF_FILTER_DEF)
    anchor = _tail_anchor(c7, _LP_LINEFIT_CALL, ("EDGEFILTER_CALL",))
    return _rep1(c7, anchor, anchor + SWAPFIX_CALL)


def patch_swapfix(cells_src: dict) -> None:
    """Plan L6b (2026-09-24): motion-smoothness 2x2 link swaps. Knobs via --set SWAPFIX_ENABLE=1 SWAPFIX_MIN_GAIN_UM=...
    SWAPFIX_MIN_RATIO=... SWAPFIX_MAX_PROB=... SWAPFIX_SRC_UM=... SWAPFIX_MAX_LEN_UM=... SWAPFIX_MIN_TERMS=...;
    default SWAPFIX_ENABLE=0 = exact no-op."""
    cells_src[2] = swapfix_config_source(cells_src[2])
    cells_src[7] = swapfix_postproc_source(cells_src[7])


# ---- coordhead: the x138 "V1284" coordinate-refinement head (anvithpothula/biohub-x138, public LB 0.953 = the public
# 0.946 kernel thtennant/biohub-frontier947-readmit-v1 + this block ONLY; pulled 2026-09-24 to experiments/ext_x138, full
# diff in experiments/ext_x138/DIFF.md). A frozen-feature MLP (Linear 224->32, SiLU, Linear 32->3; input = the primary
# UNet's 32-channel feature at the peak voxel + its 6 face-neighbour differences, standardised by a stored mean/scale)
# shifts every detected peak by a bounded 2*d/(1+|d|) <= 2 um right after peak extraction (before coord_offset[t]); the
# int16 cast at the end of predict_video is removed, so the refined sub-voxel coordinates reach the graph, the ILP and
# the whole post-processing tail as floats (the tail is float-native: nodes are read as float, linefit already moves
# nodes off the grid; the CSV writer rounds to full-resolution voxels, exactly as in x138); and
# UNetNodeTransformer._index_features is replaced CLASS-WIDE (primary and secondary model) by a trilinear gather that
# reproduces the native integer gather at integer coordinates. The x138 lines are kept VERBATIM (COORDHEAD_X138_MODULE:
# the module it writes next to the script; COORDHEAD_X138_PATCH: its four anchored replacements); ours around them:
# the BIOHUB_COORDHEAD_ENABLE guard (0 = the predict script is not touched at all), a head lookup that tries the two
# mount paths before x138's full /kaggle/input rglob (~3-4 min on this competition's mount), and a stats wrapper that
# calls x138's refine and returns its array unchanged (COORDHEAD_STATS lines in the log, /kaggle/working/
# coordhead_stats_<shard>.jsonl, a summary after prediction that fails the run if the head never ran).
COORDHEAD_DATASET = "anvithpothula/biohub-v1284-head-s075"
COORDHEAD_KNOBS = {"BIOHUB_COORDHEAD_ENABLE": "0", "BIOHUB_COORDHEAD_MODE": "candidate", "BIOHUB_COORDHEAD_HEAD_PATH": ""}
# COORDHEAD_HEAD_PATH (default "" = the public x138 head, exact no-op): our own head file in the public head's format
# (tools/train_coordhead.py), given as a path under /kaggle/input that is resolved in both mount layouts
# (/kaggle/input/<path> and /kaggle/input/datasets/<owner>/<path>), e.g. biohub-coordhead-199/v1284_head.pt; an
# absolute existing path is taken as is. Datasets of known head slugs are attached automatically, others need --dataset.
COORDHEAD_HEAD_DATASETS = {"biohub-coordhead-199": "vitaliineibauer/biohub-coordhead-199"}
COORDHEAD_X138_MODULE = r'''(_ps.parent/'v1284_coordinate_refinement.py').write_text('"""Frozen-feature coordinate regression at first-seen fused detector centers."""\nimport os\nfrom pathlib import Path\nimport numpy as np\nimport torch\n\nSPACING = np.array([1.625, 1.625, 1.625], dtype=np.float32)\nOFFSETS = ((0,0,0), (-1,0,0), (1,0,0), (0,-1,0), (0,1,0), (0,0,-1), (0,0,1))\n_CACHE = None\n\n\ndef make_head():\n    head = torch.nn.Sequential(torch.nn.Linear(224, 32), torch.nn.SiLU(), torch.nn.Linear(32, 3))\n    torch.nn.init.zeros_(head[-1].weight)\n    torch.nn.init.zeros_(head[-1].bias)\n    return head\n\n\ndef bounded(head, x):\n    delta = head(x)\n    return 2.0 * delta / (1.0 + torch.linalg.vector_norm(delta, dim=-1, keepdim=True))\n\n\ndef sample_features(feature, arr):\n    xyz = torch.as_tensor(arr[:, 1:], device=feature.device, dtype=torch.long)\n    blocks = []\n    for offset in OFFSETS:\n        loc = xyz + torch.tensor(offset, device=feature.device)\n        for axis, size in enumerate(feature.shape[-3:]):\n            loc[:, axis].clamp_(0, size-1)\n        blocks.append(feature[0, :, loc[:,0], loc[:,1], loc[:,2]].T)\n    # Directional differences plus the central representation.\n    return torch.cat([blocks[0]] + [b - blocks[0] for b in blocks[1:]], dim=1)\n\n\ndef index_features(self, maps, coords, mask):\n    """Trilinear lookup; integer coordinates reproduce native gather exactly."""\n    out = torch.zeros((*coords.shape[:2], maps.shape[1]), device=maps.device, dtype=maps.dtype)\n    for batch in range(len(maps)):\n        n = int(mask[batch].sum())\n        if not n:\n            continue\n        q = coords[batch, :n].clone()\n        for axis, size in enumerate(maps.shape[-3:]):\n            q[:,axis].clamp_(0, size-1)\n        low = q.floor().long()\n        frac = q-low\n        for z in (0,1):\n            for y in (0,1):\n                for x in (0,1):\n                    shift = torch.tensor([z,y,x], device=maps.device)\n                    loc = low+shift\n                    for axis, size in enumerate(maps.shape[-3:]):\n                        loc[:,axis].clamp_(0,size-1)\n                    weight = torch.where(shift.bool(), frac, 1-frac).prod(dim=1)\n                    out[batch,:n] += maps[batch,:,loc[:,0],loc[:,1],loc[:,2]].T * weight[:,None]\n    return out\n\n\ndef refine(ds_path, t, arr, feature):\n    global _CACHE\n    mode = os.environ[\'V1284_MODE\']\n    if not len(arr):\n        return arr\n    if mode == \'zero\':\n        return arr.astype(np.float32)\n    x = sample_features(feature, arr).float()\n    if mode == \'capture\':\n        folder = Path(os.environ[\'V1284_CAPTURE\']) / ds_path.stem\n        folder.mkdir(parents=True, exist_ok=True)\n        np.savez_compressed(folder/f\'{int(t):04d}.npz\', coords=arr, features=x.cpu().numpy())\n        return arr\n    if _CACHE is None:\n        saved = torch.load(os.environ[\'V1284_HEAD\'], map_location=\'cpu\', weights_only=True)\n        head = make_head().to(feature.device)\n        head.load_state_dict(saved[\'state_dict\']); head.eval()\n        _CACHE = (head, saved[\'mean\'].to(feature.device), saved[\'scale\'].to(feature.device))\n    head, mean, scale = _CACHE\n    shift = bounded(head, (x-mean)/scale).cpu().numpy() / SPACING\n    result = arr.astype(np.float32).copy()\n    result[:,1:] += shift\n    result[:,1:] = np.clip(result[:,1:], 0, np.asarray(feature.shape[-3:])-1)\n    if not np.isfinite(result).all() or np.max(np.linalg.norm((result[:,1:]-arr[:,1:])*SPACING,axis=1)) > 2.00001:\n        raise RuntimeError(\'invalid V1284 displacement\')\n    return result\n')
'''
COORDHEAD_X138_PATCH = r'''_trial_source = _ps.read_text()
if _trial_source.count('import tracksdata as td\n') != 1: raise RuntimeError("V1284 patch anchor mismatch")
_trial_source = _trial_source.replace('import tracksdata as td\n', 'import tracksdata as td\nfrom v1284_coordinate_refinement import refine as _v1284_refine, index_features as _v1284_index\n')
if _trial_source.count('                coord_offset[t] = (global_node_count, global_node_count + len(arr))') != 1: raise RuntimeError("V1284 patch anchor mismatch")
_trial_source = _trial_source.replace('                coord_offset[t] = (global_node_count, global_node_count + len(arr))', '                arr = _v1284_refine(ds_path, t, arr, unet_out[:, f_idx])\n                coord_offset[t] = (global_node_count, global_node_count + len(arr))')
if _trial_source.count('    coords = coords.astype(np.int16)\n') != 1: raise RuntimeError("V1284 patch anchor mismatch")
_trial_source = _trial_source.replace('    coords = coords.astype(np.int16)\n', '    # Preserve refined geometry through association and graph output.\n')
if _trial_source.count('    model, window_size, downsample = load_model(weights_path, device)') != 1: raise RuntimeError("V1284 patch anchor mismatch")
_trial_source = _trial_source.replace('    model, window_size, downsample = load_model(weights_path, device)', '    model, window_size, downsample = load_model(weights_path, device)\n    UNetNodeTransformer._index_features = _v1284_index')
'''
COORDHEAD_HEAD_LOOKUP = r'''_myhead = [_p for _p in (Path('/kaggle/input/biohub-v1284-head-s075/v1284_head.pt'),
                         Path('/kaggle/input/datasets/anvithpothula/biohub-v1284-head-s075/v1284_head.pt')) if _p.is_file()][:1]
if not _myhead:
    # x138's own lookup (walks the whole /kaggle/input tree, competition zarrs included)
    _myhead = sorted(Path('/kaggle/input').rglob('biohub-v1284-head-s075/v1284_head.pt'))
if len(_myhead) != 1:
    raise RuntimeError(('my V1284 head mount mismatch', [str(p) for p in _myhead]))
_ch_head_path = os.environ.get('BIOHUB_COORDHEAD_HEAD_PATH', '').strip()
if _ch_head_path:
    # COORDHEAD_HEAD_PATH (tools/build_probe_kernel.py): our retrained head (same file format) replaces the public one
    _ch_head_hits = [Path(_ch_head_path)] if Path(_ch_head_path).is_file() else sorted({_p for _pat in (_ch_head_path, 'datasets/*/' + _ch_head_path) for _p in Path('/kaggle/input').glob(_pat) if _p.is_file()})
    if len(_ch_head_hits) != 1:
        raise RuntimeError(('COORDHEAD_HEAD_PATH must resolve to exactly one file', _ch_head_path, [str(p) for p in _ch_head_hits]))
    _myhead = _ch_head_hits
    print('coordhead: COORDHEAD_HEAD_PATH override ->', _myhead[0])
# My own head, same architecture the module loads. Trained on x107's 20-movie TRAIN capture
# (4,136 detection<->GT pairs). Held-out BY MOVIE it moves centres CLOSER to truth:
#   ridge -10.8%   mlp -10.4%   POOLED, 16 of 20 movies improve.
# The 4-movie version of this head was +14.9% WORSE, so the null there was volume, not concept.
import hashlib as _coordhead_hashlib
print('coordhead: V1284 head', _myhead[0], 'sha256', _coordhead_hashlib.sha256(_myhead[0].read_bytes()).hexdigest()[:16])
# x138: V1284_MODE='candidate' (head inference); BIOHUB_COORDHEAD_MODE=zero (float path, no shift) or capture (dump
# coords + 224-d features per frame to V1284_CAPTURE, coordinates unchanged) are the module's own other modes
os.environ['V1284_MODE']=os.environ.get('BIOHUB_COORDHEAD_MODE', 'candidate').strip() or 'candidate'
os.environ.setdefault('V1284_CAPTURE', '/kaggle/working/v1284_capture')
os.environ['V1284_HEAD']=str(_myhead[0])
for _coordhead_old_log in Path('/kaggle/working').glob('coordhead_stats_*.jsonl'):
    _coordhead_old_log.unlink()
'''
# predict-script source added after x138's import line: a wrapper named like x138's refine (the name predict_video
# calls), so the head's array is what predict_video gets; it only counts. _v1284_log(ds_path) runs before build_graph.
COORDHEAD_STATS_SRC = '''from v1284_coordinate_refinement import SPACING as _V1284_SPACING
_v1284_refine_head = _v1284_refine
_V1284_STATS = {}


def _v1284_refine(ds_path, t, arr, feature):
    """coordhead stats (tools/build_probe_kernel.py): x138's refine, its array returned unchanged."""
    out = _v1284_refine_head(ds_path, t, arr, feature)
    st = _V1284_STATS.setdefault(str(ds_path), {"frames": 0, "peaks": 0, "moved": 0, "ge1um": 0, "sum_um": 0.0,
                                                "max_um": 0.0, "sum_dzyx_um": [0.0, 0.0, 0.0]})
    st["frames"] += 1
    if len(arr):
        d = (np.asarray(out, dtype=np.float64)[:, 1:] - np.asarray(arr, dtype=np.float64)[:, 1:]) * _V1284_SPACING
        n = np.linalg.norm(d, axis=1)
        st["peaks"] += int(len(arr))
        st["moved"] += int((n > 0).sum())
        st["ge1um"] += int((n >= 1.0).sum())
        st["sum_um"] += float(n.sum())
        st["max_um"] = max(st["max_um"], float(n.max()))
        for k in range(3):
            st["sum_dzyx_um"][k] += float(d[:, k].sum())
    return out


def _v1284_log(ds_path):
    st = _V1284_STATS.pop(str(ds_path), None)
    if st is None:
        return
    k = max(st["peaks"], 1)
    rec = {"dataset": Path(str(ds_path)).name, "mode": os.environ.get("V1284_MODE", ""), "frames": st["frames"],
           "peaks": st["peaks"], "moved": st["moved"], "ge1um": st["ge1um"], "mean_um": round(st["sum_um"] / k, 5),
           "max_um": round(st["max_um"], 5), "sum_um": st["sum_um"],
           "mean_dz_um": round(st["sum_dzyx_um"][0] / k, 5), "mean_dy_um": round(st["sum_dzyx_um"][1] / k, 5),
           "mean_dx_um": round(st["sum_dzyx_um"][2] / k, 5)}
    print("COORDHEAD_STATS " + json.dumps(rec, sort_keys=True), flush=True)
    shard = os.environ.get("BIOHUB_GPU_SHARD", "single").replace("/", "_")
    with (Path("/kaggle/working") / ("coordhead_stats_" + shard + ".jsonl")).open("a") as handle:
        handle.write(json.dumps(rec, sort_keys=True) + "\\n")
'''
COORDHEAD_STATS_PATCH = (
    "_coordhead_import = 'from v1284_coordinate_refinement import refine as _v1284_refine, index_features as _v1284_index\\n'" + NL
    + "_coordhead_build = '        graph = build_graph(coords, edges)\\n'" + NL
    + "if _trial_source.count(_coordhead_import) != 1 or _trial_source.count(_coordhead_build) != 1:" + NL
    + "    raise RuntimeError('coordhead stats anchor mismatch')" + NL
    + "_trial_source = _trial_source.replace(_coordhead_import, _coordhead_import + " + repr(COORDHEAD_STATS_SRC) + ")" + NL
    + "_trial_source = _trial_source.replace(_coordhead_build, '        _v1284_log(ds_path)\\n' + _coordhead_build)" + NL
    + "compile(_trial_source, str(_ps), 'exec')" + NL
    + "_ps.write_text(_trial_source)" + NL
    + "print('coordhead: V1284 head patched (x138 verbatim + stats wrapper); mode =', os.environ['V1284_MODE'])" + NL
)
COORDHEAD_SUMMARY = r'''
# ---- coordhead summary (tools/build_probe_kernel.py --patch coordhead) ----
if os.environ.get("BIOHUB_COORDHEAD_ENABLE", "0").strip() not in ("", "0"):
    _ch_rows = [json.loads(_line) for _p in sorted(Path("/kaggle/working").glob("coordhead_stats_*.jsonl"))
                for _line in _p.read_text().splitlines() if _line.strip()]
    _ch_peaks = sum(int(_r["peaks"]) for _r in _ch_rows)
    _ch_moved = sum(int(_r["moved"]) for _r in _ch_rows)
    _ch_ge1 = sum(int(_r["ge1um"]) for _r in _ch_rows)
    _ch_mean = sum(float(_r["sum_um"]) for _r in _ch_rows) / max(_ch_peaks, 1)
    _ch_max = max([float(_r["max_um"]) for _r in _ch_rows] or [0.0])
    print(f"COORDHEAD SUMMARY: videos={len(_ch_rows)}/{len(test_stems)} peaks={_ch_peaks} moved={_ch_moved}"
          f" (>=1um: {_ch_ge1}) mean_shift_um={_ch_mean:.4f} max_shift_um={_ch_max:.4f}"
          f" mode={os.environ.get('V1284_MODE')}", flush=True)
    if os.environ.get("V1284_MODE") == "candidate" and (len(_ch_rows) != len(test_stems) or _ch_peaks == 0):
        raise RuntimeError(f"coordhead enabled but the head did not run on every video: {len(_ch_rows)} stats rows")
'''
_CH_PRED_ANCHOR = "start_time = time.time()" + NL + "available_gpu_count = _torch.cuda.device_count()" + NL
_CH_DONE_ANCHOR = 'print(f"Prediction completed in {predict_seconds / 60:.2f} minutes")'


def _ch_indent(text: str) -> str:
    """Indent a block of single-line statements by 4 spaces (no multi-line string literals in these blocks)."""
    return "".join(("    " + line) if line.strip() else line for line in text.splitlines(keepends=True))


def coordhead_block() -> str:
    """The guarded cell-5 block: x138's module write + head lookup + x138's four replacements + the stats wrapper."""
    return (
        "# ---- coordhead (tools/build_probe_kernel.py --patch coordhead): x138 V1284 coordinate-refinement head." + NL
        + "# x138 lines verbatim inside the guard; BIOHUB_COORDHEAD_ENABLE=0 -> predict_unet_transformer.py is not touched." + NL
        + 'if os.environ.get("BIOHUB_COORDHEAD_ENABLE", "0").strip() not in ("", "0"):' + NL
        + _ch_indent(COORDHEAD_X138_MODULE + COORDHEAD_HEAD_LOOKUP + NL + COORDHEAD_X138_PATCH + COORDHEAD_STATS_PATCH)
        + "else:" + NL
        + '    print("coordhead disabled (BIOHUB_COORDHEAD_ENABLE=0): predict_unet_transformer.py unchanged")' + NL + NL
    )


def patch_coordhead(cells_src: dict) -> None:
    """x138's V1284 head (see the section comment). Base code cell 5 (the predict-script patch cell): the guarded block
    right before the prediction launch (after every other predict-script patch of the cell, so its anchors are the
    patched text, as in x138) and a guarded summary after 'Prediction completed'. Knobs: --set COORDHEAD_ENABLE=1
    [COORDHEAD_MODE=candidate|zero|capture]; default ENABLE=0 = exact no-op (the predict script is not modified)."""
    c5 = cells_src[5]
    c5 = _rep1(c5, _CH_PRED_ANCHOR, coordhead_block() + _CH_PRED_ANCHOR)
    c5 = _rep1(c5, _CH_DONE_ANCHOR, _CH_DONE_ANCHOR + NL + COORDHEAD_SUMMARY)
    cells_src[5] = c5


def meta_coordhead(meta: dict, overrides: dict) -> None:
    """Attach the head's CC0 dataset when the stage is switched on."""
    if overrides.get("BIOHUB_COORDHEAD_ENABLE", "0").strip() not in ("", "0") and COORDHEAD_DATASET not in meta["dataset_sources"]:
        meta["dataset_sources"].append(COORDHEAD_DATASET)
    head_path = overrides.get("BIOHUB_COORDHEAD_HEAD_PATH", "").strip()
    head_ds = COORDHEAD_HEAD_DATASETS.get(head_path.lstrip("/").split("/")[0]) if head_path else None
    if head_ds and head_ds not in meta["dataset_sources"]:
        meta["dataset_sources"].append(head_ds)
    elif head_path and not head_ds:
        print(f"NOTE: COORDHEAD_HEAD_PATH={head_path!r} is not a known head dataset: attach it with --dataset owner/slug")


# ---- floatout: sub-voxel output coordinates (research/wf_ideas_v2/final.json "float-output-coords"; lab on the exp39
# tail, all 199 videos, official scorer reproduced: plain float +0.00178, truncation-safe +0.00190, division counts
# identical). write_test_submission (base code cell 7) writes max(0, int(round(v))) for z/y/x; the tail (linefit, and the
# coordhead's refined peaks) is float-native, so the rounding throws away sub-voxel positions. Knob
# BIOHUB_OUTPUT_FLOAT_COORDS = 0 (default: the base writer's integers, byte-identical submission.csv) | safe | float.
# safe: r = round(v), w = max(0, r + min(max(round(v - r, 3), 0), 0.499)) -> floor(w) == r, so a server that truncates
# floats still reads the integer writer's value; float: v. Both clipped to [0, dim - 1] (volume 64 x 256 x 256) and written
# as f"{w:.3f}" on EVERY node row (polars infers the column dtype from the first rows -> Float64); t, node_id, source_id,
# target_id and the edge rows' -1 stay integers. A last cell re-reads submission.csv like royerlab
# scripts/csv_to_geffs.py (pl.read_csv, z/y/x cast to Float64) and asserts decimal points, floor(w) == round(v) (safe),
# ranges and node/edge counts against the integer writer's values. Replay: config key out.coords=round|safe|float
# (experiments/l2_daughternet/replay/replay.py write_geff calls floatout_text from this text).
FLOATOUT_MODES = ("0", "safe", "float")
FLOATOUT_TEXT_FN = r'''def floatout_text(value: float, hi: int, mode: str) -> str:
    """One node coordinate cell in safe / float mode (the replay lab runs this same function: out.coords)."""
    v = float(value)
    if mode == "safe":
        r = round(v)
        w = max(0, r + min(max(round(v - r, 3), 0.0), 0.499))
    elif mode == "float":
        w = v
    else:
        raise ValueError(f"floatout mode must be safe or float, got {mode!r}")
    return f"{min(max(float(w), 0.0), float(hi)) + 0.0:.3f}"
'''
FLOATOUT_FN = (
    "# ---- floatout (tools/build_probe_kernel.py --patch floatout): sub-voxel output coordinates. The base writer rounds" + NL
    + "# z/y/x to max(0, int(round(v))); BIOHUB_OUTPUT_FLOAT_COORDS = 0 (default: exactly that, byte-identical CSV) | safe |" + NL
    + "# float. safe: w = max(0, r + min(max(round(v - r, 3), 0), 0.499)) with r = round(v) -> floor(w) == r (a truncating" + NL
    + "# parser still reads the integer writer's value); float: v. Both clipped to [0, dim - 1], written with 3 decimals on" + NL
    + "# EVERY node row (polars infers Float64 from the first rows); t, ids and the edge rows' -1 stay integers." + NL
    + 'OUTPUT_FLOAT_COORDS = os.environ.get("BIOHUB_OUTPUT_FLOAT_COORDS", "0").strip() or "0"' + NL
    + 'if OUTPUT_FLOAT_COORDS not in ("0", "safe", "float"):' + NL
    + '    raise ValueError(f"BIOHUB_OUTPUT_FLOAT_COORDS must be 0, safe or float, got {OUTPUT_FLOAT_COORDS!r}")' + NL
    + 'FLOATOUT_MAX = {"z": 63, "y": 255, "x": 255}  # volume (64, 256, 256) on every train and test video' + NL
    + '# the integer writer\'s z/y/x of every node row (flat, row order) and its counts: read by the floatout check cell' + NL
    + 'FLOATOUT_REF: dict[str, object] = {"int": [], "nodes": 0, "edges": 0}' + NL + NL + NL
    + FLOATOUT_TEXT_FN + NL + NL
    + '''def floatout_zyx(node: dict) -> dict:
    """z/y/x cells of one node row; OUTPUT_FLOAT_COORDS=0 returns the base writer's integers unchanged."""
    ints = {axis: max(0, int(round(float(node[axis])))) for axis in ("z", "y", "x")}
    if OUTPUT_FLOAT_COORDS == "0":
        return ints
    FLOATOUT_REF["int"].extend((ints["z"], ints["y"], ints["x"]))
    return {axis: floatout_text(node[axis], FLOATOUT_MAX[axis], OUTPUT_FLOAT_COORDS) for axis in ("z", "y", "x")}
''' + NL + NL)
_FO_WRITER_DEF = 'def write_test_submission(tag: str = "base") -> None:' + NL
_FO_WRITER_INIT = "    seen_datasets: set[str] = set()" + NL + "    row_id = 0" + NL
_FO_WRITER_RESET = '    FLOATOUT_REF.update({"int": [], "nodes": 0, "edges": 0})  # floatout: fresh integer reference per write' + NL
_FO_WRITER_COORDS = ('                    "z": max(0, int(round(float(node["z"])))),' + NL
                     + '                    "y": max(0, int(round(float(node["y"])))),' + NL
                     + '                    "x": max(0, int(round(float(node["x"])))),' + NL)
_FO_WRITER_FLOAT = '                    **floatout_zyx(node),  # floatout: z/y/x (OUTPUT_FLOAT_COORDS=0: the integers above)' + NL
_FO_WRITER_COUNT = '    assert row_id == total_nodes + total_edges, "Internal row counter mismatch"' + NL
_FO_WRITER_RECORD = '    FLOATOUT_REF.update(nodes=total_nodes, edges=total_edges)  # floatout: the writer\'s counts, for the check' + NL
FLOATOUT_CHECK = r'''# ---- floatout check (tools/build_probe_kernel.py --patch floatout): re-read submission.csv the way royerlab
# scripts/csv_to_geffs.py does (pl.read_csv with its columns, node rows, t cast to Int64, z/y/x cast to Float64) and check
# the written coordinates against the integer writer's values recorded by write_test_submission (FLOATOUT_REF).
if OUTPUT_FLOAT_COORDS != "0":
    import polars as _fo_pl

    _fo_cols = ["dataset", "row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"]
    _fo_df = _fo_pl.read_csv(SUBMISSION_PATH, columns=_fo_cols)
    for _fo_c in ("z", "y", "x"):
        assert _fo_df.schema[_fo_c] == _fo_pl.Float64, f"floatout: polars inferred {_fo_df.schema[_fo_c]} for {_fo_c}"
    for _fo_c in ("node_id", "t", "source_id", "target_id"):
        assert _fo_df.schema[_fo_c] == _fo_pl.Int64, f"floatout: polars inferred {_fo_df.schema[_fo_c]} for {_fo_c}"
    _fo_nodes = _fo_df.filter(_fo_pl.col("row_type") == "node").with_columns(
        _fo_pl.col("t").cast(_fo_pl.Int64), _fo_pl.col("z").cast(_fo_pl.Float64),
        _fo_pl.col("y").cast(_fo_pl.Float64), _fo_pl.col("x").cast(_fo_pl.Float64))
    _fo_edges = _fo_df.filter(_fo_pl.col("row_type") == "edge")
    _fo_text = _fo_pl.read_csv(SUBMISSION_PATH, columns=_fo_cols, infer_schema_length=0)  # every cell as written
    _fo_text_nodes = _fo_text.filter(_fo_pl.col("row_type") == "node")
    _fo_text_edges = _fo_text.filter(_fo_pl.col("row_type") == "edge")
    for _fo_c in ("z", "y", "x"):
        assert _fo_text_nodes[_fo_c].str.contains(".", literal=True).all(), f"floatout: a node {_fo_c} has no decimal point"
        assert (_fo_text_edges[_fo_c] == "-1").all(), f"floatout: edge rows must keep {_fo_c} = -1"
    for _fo_c in ("node_id", "t", "source_id", "target_id"):
        assert not _fo_text[_fo_c].str.contains(".", literal=True).any(), f"floatout: {_fo_c} must stay integer"
    _fo_int = np.asarray(FLOATOUT_REF["int"], dtype=np.int64).reshape(-1, 3)
    _fo_hi = np.asarray([FLOATOUT_MAX[_fo_c] for _fo_c in ("z", "y", "x")], dtype=np.int64)
    _fo_w = _fo_nodes.select(["z", "y", "x"]).to_numpy().astype(np.float64)
    assert len(_fo_nodes) == FLOATOUT_REF["nodes"] == len(_fo_int), ("floatout: node rows", len(_fo_nodes),
                                                                     FLOATOUT_REF["nodes"], len(_fo_int))
    assert len(_fo_edges) == FLOATOUT_REF["edges"], ("floatout: edge rows", len(_fo_edges), FLOATOUT_REF["edges"])
    assert np.isfinite(_fo_w).all() and (_fo_w >= 0.0).all() and (_fo_w <= _fo_hi).all(), "floatout: coordinate out of range"
    _fo_ref = np.minimum(_fo_int, _fo_hi)  # the integer writer's value (it has no upper clip) inside the volume
    _fo_floor = np.floor(_fo_w).astype(np.int64)
    if OUTPUT_FLOAT_COORDS == "safe":
        assert (_fo_floor == _fo_ref).all(), f"floatout: floor(w) != round(v) on {int((_fo_floor != _fo_ref).sum())} coords"
    else:
        assert (np.abs(_fo_w - _fo_ref) <= 0.5 + 1e-6).all(), "floatout: |w - round(v)| > 0.5"
    _fo_forks = int((_fo_edges.group_by(["dataset", "source_id"]).len()["len"] >= 2).sum())
    _fo_changed = _fo_w != _fo_int
    print(f"FLOATOUT CHECK PASSED: mode={OUTPUT_FLOAT_COORDS} nodes={len(_fo_nodes)} edges={len(_fo_edges)} "
          f"forks={_fo_forks} coords_changed={_fo_changed.mean():.4f} "
          f"(z/y/x {[round(float(_v), 4) for _v in _fo_changed.mean(axis=0)]}) "
          f"mean_abs_shift_vox={np.abs(_fo_w - _fo_int).mean():.4f} "
          f"int_beyond_volume={int((_fo_int > _fo_hi).sum())} floor_ne_int_unclipped={int((_fo_floor != _fo_int).sum())}",
          flush=True)
else:
    print("floatout: OUTPUT_FLOAT_COORDS=0 -> integer coordinates (the base writer), nothing to check")
'''


def floatout_postproc_source(c7: str) -> str:
    """Post-processing cell (base code cell 7): the knob + floatout_text / floatout_zyx right before
    write_test_submission, and three edits inside it (reset the integer reference, node rows' z/y/x through
    floatout_zyx, record the writer's counts). No other patch touches these lines: any patch order."""
    c7 = _rep1(c7, NL + NL + _FO_WRITER_DEF, NL + NL + FLOATOUT_FN + _FO_WRITER_DEF)
    c7 = _rep1(c7, _FO_WRITER_INIT, _FO_WRITER_INIT + _FO_WRITER_RESET)
    c7 = _rep1(c7, _FO_WRITER_COORDS, _FO_WRITER_FLOAT)
    return _rep1(c7, _FO_WRITER_COUNT, _FO_WRITER_COUNT + _FO_WRITER_RECORD)


def patch_floatout(cells_src: dict) -> None:
    """Float output coordinates (see the section comment). Knob via --set OUTPUT_FLOAT_COORDS=safe|float; default 0 =
    the base writer's integers (byte-identical submission.csv). A new last code cell (after the manifest, base code
    index 13) runs the csv_to_geffs-style parse check when the knob is on."""
    cells_src[7] = floatout_postproc_source(cells_src[7])
    cells_src.setdefault(NEW_CELLS_KEY, []).append((max(k for k in cells_src if isinstance(k, int)), FLOATOUT_CHECK))


# ---- safetail (ideas workflow v3, E1 = C01 + fail-soft; research/wf_ideas_v3/FINAL_REPORT.md): x138 base only ----
SAFETAIL_GATE = r"""

# ---- safetail (tools/build_probe_kernel.py --patch safetail): runtime insurance for the hidden rerun ----
# DaughterNet insertion runs only while the repair deadline has not fired and the kernel is younger than
# BIOHUB_DIVINS_DEADLINE_S; BIOHUB_DIVINS_FORCE_FAIL=1 (dummy test only) makes the insertion raise to exercise the
# fail-soft path; BIOHUB_DEGRADE_KEEP_DIV=1 keeps safe divisions + linefit after the deadline.
SAFETAIL_DIVINS_DEADLINE_S = float(os.environ.get("BIOHUB_DIVINS_DEADLINE_S", "28800"))
SAFETAIL_DIVINS_FORCE_FAIL = os.environ.get("BIOHUB_DIVINS_FORCE_FAIL", "0") != "0"
print(f"SAFETAIL: repair deadline {REPAIR_DEADLINE_S:.0f}s, divins deadline {SAFETAIL_DIVINS_DEADLINE_S:.0f}s,"
      f" keep_div_after_deadline={os.environ.get('BIOHUB_DEGRADE_KEEP_DIV', '0')},"
      f" divins_force_fail={int(SAFETAIL_DIVINS_FORCE_FAIL)}", flush=True)


def safetail_divins_allowed(dataset, stats) -> bool:
    elapsed = _time.time() - KERNEL_START_TS
    if _deadline_degraded or elapsed >= SAFETAIL_DIVINS_DEADLINE_S:
        stats["divins_skipped_deadline"] = 1
        print(f"  [{dataset}] DIVINS SKIPPED (deadline): elapsed {elapsed:.0f}s, degraded={int(_deadline_degraded)}",
              flush=True)
        return False
    return True
"""

SAFETAIL_DEGRADE_OLD = """    OUTPUT_SAFE_DIVISIONS = False
    OUTPUT_LINEFIT_SMOOTH = False
    print(
        f"DEADLINE: {_time.time() - KERNEL_START_TS:.0f}s since kernel start exceeds"
        f" {REPAIR_DEADLINE_S:.0f}s; remaining datasets get edge filtering and"
        " short-track filtering only",
        flush=True,
    )
"""
SAFETAIL_DEGRADE_NEW = """    _keep_div = os.environ.get("BIOHUB_DEGRADE_KEEP_DIV", "0") != "0"  # safetail
    if not _keep_div:
        OUTPUT_SAFE_DIVISIONS = False
        OUTPUT_LINEFIT_SMOOTH = False
    print(
        f"DEADLINE: {_time.time() - KERNEL_START_TS:.0f}s since kernel start exceeds"
        f" {REPAIR_DEADLINE_S:.0f}s; remaining datasets get edge filtering and"
        " short-track filtering only"
        + ("; safetail keeps safe divisions + linefit" if _keep_div else ""),
        flush=True,
    )
"""
_DIVINS_IF = '    if BIOHUB_DIVINS_ENABLE != "0" and dataset is not None and edges and nodes_by_id:' + NL
_DIVINS_END = '    # ---- /divinsert ----' + NL


def safetail_divins_call() -> str:
    """DIVINS_CALL with the deadline gate and a try/except that keeps the pre-insertion edges on any exception."""
    head, rest = DIVINS_CALL.split(_DIVINS_IF)
    body, tail = rest.split(_DIVINS_END)
    assert tail == "", tail
    body = "".join("    " + ln if ln.strip() else ln for ln in body.splitlines(keepends=True))
    return (head
            + '    if BIOHUB_DIVINS_ENABLE != "0" and dataset is not None and edges and nodes_by_id'
            + ' and safetail_divins_allowed(dataset, stats):' + NL
            + '        _dv_edges_in = edges' + NL
            + '        try:' + NL
            + '            if SAFETAIL_DIVINS_FORCE_FAIL:' + NL
            + '                raise RuntimeError("BIOHUB_DIVINS_FORCE_FAIL=1 (dummy test of the fail-soft path)")' + NL
            + body
            + '        except Exception as _dv_exc:' + NL
            + '            edges = _dv_edges_in' + NL
            + '            if DIVINS_BUNDLE is not None:' + NL
            + '                DIVINS_BUNDLE["prepared_frames"].clear()' + NL
            + '            stats["divins_failed"] = 1' + NL
            + '            print(f"  [{dataset}] DIVINS FAILED ({type(_dv_exc).__name__}: {_dv_exc});"' + NL
            + '                  " keeping the pre-insertion edges", flush=True)' + NL
            + _DIVINS_END)


def patch_safetail(cells_src: dict) -> None:
    """Ideas workflow v3 E1 (research/wf_ideas_v3/FINAL_REPORT.md, TASK_CLOUD_SESSION.md T1), x138 base only, applied
    after every other patch. Post-processing cell: (a) SAFETAIL knobs + safetail_divins_allowed() after the x138
    runtime-guard block; (b) _deadline_degrade() keeps OUTPUT_SAFE_DIVISIONS / OUTPUT_LINEFIT_SMOOTH when
    BIOHUB_DEGRADE_KEEP_DIV=1 (main() sets it to 1 for safetail builds); (c) with --patch divinsert: the insertion call
    is gated by the deadline and wrapped in try/except (on failure: input edges kept, 'DIVINS FAILED' in the log).
    The repair deadline itself is REPAIR_DEADLINE_S from --set (main() requires it)."""
    post = CELL["post"]
    c = cells_src[post]
    c = _rep1(c, NL + NL + NL + "def fallback_output_graph(", SAFETAIL_GATE + NL + NL + "def fallback_output_graph(")
    c = _rep1(c, SAFETAIL_DEGRADE_OLD, SAFETAIL_DEGRADE_NEW)
    if DIVINS_CALL in c:
        c = _rep1(c, DIVINS_CALL, safetail_divins_call())
    cells_src[post] = c


PATCHES = {"gshift": patch_gshift, "divinsert": patch_divinsert, "leafprune": patch_leafprune,
           "edgefilter": patch_edgefilter, "stitch": patch_stitch, "swapfix": patch_swapfix,
           "coordhead": patch_coordhead, "floatout": patch_floatout, "safetail": patch_safetail}
META_PATCHES = {"divinsert": meta_divinsert, "coordhead": meta_coordhead}


# ---- lowrefine (ideas workflow v3 E2 = s_merge.json C05, reduced variant): x138 base only. x138's predict-patch cell
# writes the low-detection pool (readmit >= 0.965, gapfill >= 0.5) through the 'lowdet globals' / 'lowdet peaks' /
# 'lowdet write' replacements of one string-literal list, on the INTEGER pooled grid, cast to int16; the V1284 head
# (patched into the predict script AFTER that list: swapping the order made x122's 'LOW-DETECTION DUMP SKIPPED') refines
# only the main peaks. lowrefine edits four spots inside those literals (runtime text below, escaped into the literal):
# the pool rows with score >= READMIT_MIN_SCORE go through _v1284_refine AFTER the integer score lookup, with the same
# unet_out[:, f_idx] feature map as the main peaks (same peaks, same features: in distribution); the int16 cast is
# skipped (cell 5 load_low_detections reads low_coords as float64; readmit / gapfill use float(vox)). Runtime knob
# BIOHUB_LOWREFINE_ENABLE: "0" runs the original statements (byte-identical pool, dump and CSV). Fail-soft: an exception
# keeps that frame's grid coordinates and prints 'LOWREFINE FAILED' (first failing frame per video) + a failed-frame
# counter in the per-video 'LOWREFINE <name>: refined R of N lowdet peaks' line.
LOWREFINE_GLOBALS_ANCHOR = r"_LOWDET: list = []\n"  # 'lowdet globals' new text (a double-quoted literal)
LOWREFINE_GLOBALS = (
    "_LOWREFINE_ENABLE = os.environ.get('BIOHUB_LOWREFINE_ENABLE', '0').strip() not in ('', '0')\n"
    "_LOWREFINE_MIN_SCORE = float(os.environ.get('BIOHUB_READMIT_MIN_SCORE', '0.965'))\n"
    "_LOWREFINE_COUNTS = [0, 0, 0]  # lowrefine, per video: refined peaks, lowdet peaks, failed frames\n"
)
# 'lowdet peaks' new text (a single-quoted literal): the statement at 24 spaces inside `if len(_low):`
LOWREFINE_PEAKS_ANCHOR = "_LOWDET.append((_low.astype(np.float32), _lsc.astype(np.float32)))"
LOWREFINE_PEAKS = (
    "if _LOWREFINE_ENABLE:\n"
    "    _lowf = _low.astype(np.float32)\n"
    "    _LOWREFINE_COUNTS[1] += len(_low)\n"
    "    try:\n"
    "        _lhi = np.asarray(_lsc, dtype=np.float64) >= _LOWREFINE_MIN_SCORE\n"
    "        if bool(_lhi.any()):\n"
    "            _lref = np.asarray(_v1284_refine(ds_path, t, _low[_lhi], unet_out[:, f_idx]), dtype=np.float32)\n"
    "            if _lref.shape != _lowf[_lhi].shape or not np.array_equal(_lref[:, 0], _lowf[_lhi, 0]):\n"
    "                raise RuntimeError(f\"refine returned shape {_lref.shape} for {int(_lhi.sum())} peaks\")\n"
    "            _lowf[_lhi] = _lref\n"
    "            _LOWREFINE_COUNTS[0] += int(_lhi.sum())\n"
    "    except Exception as _lr_exc:\n"
    "        _lowf = _low.astype(np.float32)\n"
    "        if not _LOWREFINE_COUNTS[2]:\n"
    "            print(f\"LOWREFINE FAILED (t={t}, {type(_lr_exc).__name__}: {_lr_exc}); grid coordinates kept\", flush=True)\n"
    "        _LOWREFINE_COUNTS[2] += 1\n"
    "    _LOWDET.append((_lowf, _lsc.astype(np.float32)))\n"
    "else:\n"
    "    " + LOWREFINE_PEAKS_ANCHOR
)
# 'lowdet write' new text (a double-quoted literal): the cast at 16 spaces, the per-video print at 12 spaces
LOWREFINE_CAST_ANCHOR = r"                _lc = _lc.astype(np.int16)\n"
LOWREFINE_CAST = (
    "                if not _LOWREFINE_ENABLE:\n"
    "                    _lc = _lc.astype(np.int16)\n"
)
LOWREFINE_PRINT_ANCHOR = r"            print(f'LOWDET {name}: {len(_lc)} peaks above {_LOWDET_THRESHOLD}', flush=True)\n"
LOWREFINE_PRINT = (
    "            if _LOWREFINE_ENABLE:\n"
    "                print(f'LOWREFINE {name}: refined {_LOWREFINE_COUNTS[0]} of {_LOWREFINE_COUNTS[1]} lowdet peaks'\n"
    "                      f' (score >= {_LOWREFINE_MIN_SCORE}), failed frames {_LOWREFINE_COUNTS[2]}', flush=True)\n"
    "                _LOWREFINE_COUNTS[:] = [0, 0, 0]\n"
)
_LR_V1284_MARK = "(_ps.parent/'v1284_coordinate_refinement.py').write_text("


def _lr_literal(text: str, quote: str, indent: int = 0) -> str:
    """Runtime text -> its spelling inside an x138 cell-4 string literal delimited by `quote` (newlines as \\n;
    continuation lines indented by `indent` spaces)."""
    assert "\\" not in text and quote not in text, text[:60]
    lines = text.split("\n")
    return "\\n".join([lines[0]] + [(" " * indent + ln) if ln else ln for ln in lines[1:]])


def lowrefine_predict_source(c4: str) -> str:
    """x138 predict-patch cell (code cell 4): the four exact-once edits inside the 'lowdet' literals, all before the
    V1284 block (the patch order lowdet -> V1284 is left as it is)."""
    assert "_LOWREFINE_ENABLE" not in c4, "lowrefine already applied"
    v1284_at = c4.index(_LR_V1284_MARK)
    for anchor in (LOWREFINE_GLOBALS_ANCHOR, LOWREFINE_PEAKS_ANCHOR, LOWREFINE_CAST_ANCHOR, LOWREFINE_PRINT_ANCHOR):
        assert c4.count(anchor) == 1, f"lowrefine anchor count {c4.count(anchor)} != 1: {anchor[:70]!r}"
        assert c4.index(anchor) < v1284_at, f"lowrefine anchor after the V1284 block: {anchor[:70]!r}"
    c4 = _rep1(c4, LOWREFINE_GLOBALS_ANCHOR, LOWREFINE_GLOBALS_ANCHOR + _lr_literal(LOWREFINE_GLOBALS, '"'))
    c4 = _rep1(c4, LOWREFINE_PEAKS_ANCHOR, _lr_literal(LOWREFINE_PEAKS, "'", indent=24))
    c4 = _rep1(c4, LOWREFINE_CAST_ANCHOR, _lr_literal(LOWREFINE_CAST, '"'))
    return _rep1(c4, LOWREFINE_PRINT_ANCHOR, LOWREFINE_PRINT_ANCHOR + _lr_literal(LOWREFINE_PRINT, '"'))


def patch_lowrefine(cells_src: dict) -> None:
    """Ideas workflow v3 E2 (research/wf_ideas_v3/TASK_CLOUD_SESSION.md T2): V1284-refined coordinates for the
    readmit-eligible (>= 0.965) rows of x138's low-detection pool. Knob BIOHUB_LOWREFINE_ENABLE (main() sets 1)."""
    cells_src[CELL["predict"]] = lowrefine_predict_source(cells_src[CELL["predict"]])


# registration on separate lines (parallel patch branches add their own lines)
BASES["x138"]["patches"] += ("lowrefine",)
PATCHES["lowrefine"] = patch_lowrefine


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="folder/kernel name, e.g. exp40_relink_off (lowercase, digits, _ or -)")
    ap.add_argument("--set", action="append", default=[], help="KNOB=value (without BIOHUB_), repeatable")
    ap.add_argument("--base", choices=sorted(BASES), default="exp39",
                    help="base notebook: exp39 (default) or x138 (= exp56, anvithpothula/biohub-x138 verbatim)")
    ap.add_argument("--divnet", choices=["0", "1"], default=None,
                    help="DivNet veto on (1, exp39, the default) or off (0, exp29); exp39 base only")
    ap.add_argument("--note", default="", help="one line for probe.json")
    ap.add_argument("--patch", action="append", default=[], choices=sorted(PATCHES), help="code surgery to apply, repeatable")
    ap.add_argument("--dataset", action="append", default=[], help="extra Kaggle dataset source owner/slug, repeatable")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--lab", action="store_true",
                    help="dummy/lab build, never a submission: allows DIVINS_DUMP=1, DIVINS_FORCE_FAIL and any REPAIR_DEADLINE_S")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]+", a.name):
        sys.exit("name must be lowercase letters/digits/_/-")
    base = BASES[a.base]
    CELL.clear()
    CELL.update(base)
    if base["patches"] is not None:
        unsupported = sorted(set(a.patch) - set(base["patches"]))
        if unsupported:
            sys.exit(f"--base {a.base} supports only --patch {', '.join(base['patches'])}; got {unsupported}")
        if a.divnet is not None:
            sys.exit(f"--divnet: the {a.base} base has no DivNet veto cell")
        if len(set(a.patch)) != len(a.patch):
            sys.exit("each --patch once")
    overrides = {}
    for item in a.set:
        k, _, v = item.partition("=")
        if not k or not _:
            sys.exit(f"bad --set {item!r}")
        overrides["BIOHUB_" + k.strip().removeprefix("BIOHUB_")] = v.strip()
    if "safetail" in a.patch:
        if a.base != "x138":
            sys.exit("--patch safetail needs --base x138")
        if "BIOHUB_REPAIR_DEADLINE_S" not in overrides:
            sys.exit("--patch safetail needs --set REPAIR_DEADLINE_S=34200 (x138 default 27000 is the runtime cliff)")
        if not a.lab and overrides["BIOHUB_REPAIR_DEADLINE_S"] != "34200":
            sys.exit("submission builds with safetail use REPAIR_DEADLINE_S=34200; other values need --lab")
        if not a.lab and overrides.get("BIOHUB_DIVINS_DUMP", "0") != "0":
            sys.exit("DIVINS_DUMP=1 is for --lab builds only")
        overrides.setdefault("BIOHUB_DEGRADE_KEEP_DIV", "1")
        a.patch = [p for p in a.patch if p != "safetail"] + ["safetail"]  # wraps what the other patches inserted
    for _k in ("BIOHUB_DIVINS_DEADLINE_S", "BIOHUB_DIVINS_FORCE_FAIL", "BIOHUB_DEGRADE_KEEP_DIV"):
        if _k in overrides and "safetail" not in a.patch:
            sys.exit(f"{_k.removeprefix('BIOHUB_')} needs --patch safetail")
    if "lowrefine" in a.patch:
        if a.base != "x138":
            sys.exit("--patch lowrefine needs --base x138")
        overrides.setdefault("BIOHUB_LOWREFINE_ENABLE", "1")
    if "BIOHUB_LOWREFINE_ENABLE" in overrides:
        if "lowrefine" not in a.patch:
            sys.exit("LOWREFINE_ENABLE needs --patch lowrefine")
        if overrides["BIOHUB_LOWREFINE_ENABLE"] not in ("0", "1"):
            sys.exit(f"LOWREFINE_ENABLE must be 0 or 1, got {overrides['BIOHUB_LOWREFINE_ENABLE']!r}")
    if overrides.get("BIOHUB_DIVINS_FORCE_FAIL", "0") != "0" and not a.lab:
        sys.exit("DIVINS_FORCE_FAIL is a dummy test knob: needs --lab")
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
    st_knobs = {"BIOHUB_" + knob: default for knob, default in STITCH_KNOBS.values()}
    if any(k.startswith("BIOHUB_STITCH_") for k in overrides):
        if "stitch" not in a.patch:
            sys.exit("STITCH_* knobs need --patch stitch")
        unknown = sorted(k for k in overrides if k.startswith("BIOHUB_STITCH_") and k not in st_knobs)
        if unknown:
            sys.exit(f"unknown stitch knobs {unknown}; known: {sorted(st_knobs)}")
        for k in overrides:
            if k in st_knobs:
                try:
                    value = float(overrides[k])
                except ValueError:
                    sys.exit(f"{k} must be a number, got {overrides[k]!r}")
                if value != value or value in (float("inf"), float("-inf")):
                    sys.exit(f"{k} must be finite, got {overrides[k]!r}")
                if st_knobs[k].isdigit() and not re.fullmatch(r"-?\d+", overrides[k]):  # the config cell calls int()
                    sys.exit(f"{k} must be an integer literal, got {overrides[k]!r}")
    if "stitch" in a.patch and overrides.get("BIOHUB_STITCH_ENABLE", "0") in ("0", "0.0"):
        print("NOTE: --patch stitch with STITCH_ENABLE=0 (default) builds an exact no-op of the base")
    sw_knobs = {"BIOHUB_" + knob: default for knob, default in SWAPFIX_KNOBS.values()}
    if any(k.startswith("BIOHUB_SWAPFIX_") for k in overrides):
        if "swapfix" not in a.patch:
            sys.exit("SWAPFIX_* knobs need --patch swapfix")
        unknown = sorted(k for k in overrides if k.startswith("BIOHUB_SWAPFIX_") and k not in sw_knobs)
        if unknown:
            sys.exit(f"unknown swapfix knobs {unknown}; known: {sorted(sw_knobs)}")
        for k in overrides:
            if k in sw_knobs:
                try:
                    value = float(overrides[k])
                except ValueError:
                    sys.exit(f"{k} must be a number, got {overrides[k]!r}")
                if value != value or value in (float("inf"), float("-inf")):
                    sys.exit(f"{k} must be finite, got {overrides[k]!r}")
                if sw_knobs[k].isdigit() and not re.fullmatch(r"-?\d+", overrides[k]):  # the config cell calls int()
                    sys.exit(f"{k} must be an integer literal, got {overrides[k]!r}")
    if "swapfix" in a.patch and overrides.get("BIOHUB_SWAPFIX_ENABLE", "0") in ("0", "0.0"):
        print("NOTE: --patch swapfix with SWAPFIX_ENABLE=0 (default) builds an exact no-op of the base")
    if any(k.startswith("BIOHUB_COORDHEAD_") for k in overrides):
        if "coordhead" not in a.patch:
            sys.exit("COORDHEAD_* knobs need --patch coordhead")
        unknown = sorted(k for k in overrides if k.startswith("BIOHUB_COORDHEAD_") and k not in COORDHEAD_KNOBS)
        if unknown:
            sys.exit(f"unknown coordhead knobs {unknown}; known: {sorted(COORDHEAD_KNOBS)}")
        if not re.fullmatch(r"\d+", overrides.get("BIOHUB_COORDHEAD_ENABLE", "0")):
            sys.exit(f"COORDHEAD_ENABLE must be an integer literal, got {overrides['BIOHUB_COORDHEAD_ENABLE']!r}")
        if overrides.get("BIOHUB_COORDHEAD_MODE", "candidate") not in ("candidate", "zero", "capture"):
            sys.exit(f"COORDHEAD_MODE must be candidate, zero or capture, got {overrides['BIOHUB_COORDHEAD_MODE']!r}")
        if not re.fullmatch(r"[A-Za-z0-9_./*-]*", overrides.get("BIOHUB_COORDHEAD_HEAD_PATH", "")):
            sys.exit(f"COORDHEAD_HEAD_PATH must be a plain path, got {overrides['BIOHUB_COORDHEAD_HEAD_PATH']!r}")
        if overrides.get("BIOHUB_COORDHEAD_HEAD_PATH", "") and overrides.get("BIOHUB_COORDHEAD_ENABLE", "0") in ("", "0"):
            sys.exit("COORDHEAD_HEAD_PATH needs COORDHEAD_ENABLE=1")
    if "coordhead" in a.patch and overrides.get("BIOHUB_COORDHEAD_ENABLE", "0").strip() in ("", "0"):
        print("NOTE: --patch coordhead with COORDHEAD_ENABLE=0 (default) builds an exact no-op of the base")
    if "BIOHUB_OUTPUT_FLOAT_COORDS" in overrides:
        if "floatout" not in a.patch:
            # the base writer never reads the knob: the probe would silently write integers
            sys.exit("OUTPUT_FLOAT_COORDS needs --patch floatout")
        if overrides["BIOHUB_OUTPUT_FLOAT_COORDS"] not in FLOATOUT_MODES:
            sys.exit(f"OUTPUT_FLOAT_COORDS must be one of {FLOATOUT_MODES}, got {overrides['BIOHUB_OUTPUT_FLOAT_COORDS']!r}")
    if "floatout" in a.patch and overrides.get("BIOHUB_OUTPUT_FLOAT_COORDS", "0") == "0":
        print("NOTE: --patch floatout with OUTPUT_FLOAT_COORDS=0 (default) writes a byte-identical submission.csv")
    if a.base == "exp39":
        overrides["BIOHUB_DIVNET_VERIFY"] = a.divnet or "1"

    raw_nb = base["nb"].read_bytes()
    if base["sha256"] and hashlib.sha256(raw_nb).hexdigest() != base["sha256"]:
        sys.exit(f"{base['nb']} is not the expected {a.base} notebook (sha256 mismatch)")
    nb = json.loads(raw_nb.decode("utf-8"))
    cells = nb["cells"]
    code = [i for i, c in enumerate(cells) if c["cell_type"] == "code"]

    def src(i):
        return "".join(cells[i]["source"])

    def set_src(i, s):
        # exp39 builds store source as a list of lines (as before); x138 (Kaggle export) keeps one string per cell
        cells[i]["source"] = s if base["compact"] else s.splitlines(keepends=True)
        cells[i]["outputs"] = []
        cells[i]["execution_count"] = None

    c0 = src(code[0])
    if a.base == "exp39":
        assert "BIOHUB_PRESET = 'exp39_sjlee947_tight55_divnetveto'" in c0
        c0 = c0.replace("BIOHUB_PRESET = 'exp39_sjlee947_tight55_divnetveto'", f"BIOHUB_PRESET = '{a.name}'")
    if overrides or a.base == "exp39":  # x138: its preset name stays; no overrides -> cell 0 untouched
        tag = "tools/build_probe_kernel.py" + ("" if a.base == "exp39" else f" --base {a.base}")
        block = NL + f"# ---- {a.name}: probe overrides ({tag}) ----" + NL
        block += NL.join(f'os.environ["{k}"] = "{v}"' for k, v in overrides.items()) + NL
        c0 = c0.rstrip(NL) + NL + block
        set_src(code[0], c0)

    c1 = src(code[1])
    for k, v in overrides.items():
        m = re.search(r'^(\s*"%s": )([^,\n]+),' % re.escape(k), c1, re.M)
        if m:
            c1 = c1[:m.start(2)] + (v if re.fullmatch(r"-?\d+(\.\d+)?", v) else json.dumps(v)) + c1[m.end(2):]
    if c1 != src(code[1]) or a.base == "exp39":
        set_src(code[1], c1)

    if a.patch:
        # patches always see the BASE code-cell indices (CELL: exp39 post-processing = 7, x138 = 5); new cells go in
        # afterwards
        cells_src = {k: src(code[k]) for k in range(len(code))}
        for name in a.patch:
            PATCHES[name](cells_src)
        new_cells = cells_src.pop(NEW_CELLS_KEY, [])
        for k, s in cells_src.items():
            if s != src(code[k]):
                set_src(code[k], s)
        cell_ids = {c.get("id") for c in cells}
        for after in sorted({k for k, _ in new_cells}, reverse=True):
            for s in reversed([s for k, s in new_cells if k == after]):
                if base["compact"]:  # Kaggle-export base (x138): cell ids, source as one string
                    cid = hashlib.sha256(s.encode("utf-8")).hexdigest()[:8]
                    assert cid not in cell_ids, cid
                    cell_ids.add(cid)
                    new = {"id": cid, "cell_type": "code", "source": s, "metadata": {}, "outputs": [],
                           "execution_count": None}
                else:
                    new = {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                           "source": s.splitlines(keepends=True)}
                cells.insert(code[after] + 1, new)
        code = [i for i, c in enumerate(cells) if c["cell_type"] == "code"]
        overrides["PATCHES"] = "+".join(a.patch)

    for i in code:
        compile(src(i), f"cell{i}", "exec")
    out_dir = ROOT / "experiments" / a.name
    out_dir.mkdir(exist_ok=True)
    nb_name = a.name.replace("_", "-") + ".ipynb"
    if base["compact"]:
        # x138's own serialisation (Kaggle export): compact separators; json.loads -> dumps reproduces it byte for byte
        (out_dir / nb_name).write_bytes(json.dumps(nb, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    else:
        json.dump(nb, open(out_dir / nb_name, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    meta = json.load(open(base["dir"] / "kernel-metadata.json"))
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
    if a.lab:
        probe["lab"] = "LAB/DUMMY BUILD (--lab): never submit"
    if a.base == "x138":
        probe["base"] = ("x138 verbatim = exp56 (anvithpothula/biohub-x138, author public 0.953; x138 datasets, docker pin "
                         "and machine shape); built by tools/build_probe_kernel.py --base x138")
        probe["rule"] = "compare with exp56 (x138 verbatim on our account); above exp56 adopt, ties recorded"
    json.dump(probe, open(out_dir / "probe.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("built", out_dir.relative_to(ROOT), "overrides", overrides)
    if a.push:
        r = subprocess.run([sys.executable, "-m", "kaggle", "kernels", "push", "-p", str(out_dir)])
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
