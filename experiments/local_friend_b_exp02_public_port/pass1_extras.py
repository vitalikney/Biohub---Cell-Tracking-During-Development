"""B20 pass-1 extras, run while a bundle's videos are still on disk (CONTEXT_FRIEND_B.md §38.6).

For each video with a raw graph in .public_local_cache/exp29pp/raw/:
  ckpt/<stem>.npz   the graph after edge filter + motion relink + gap closing (+ gap2), i.e. the notebook's
                    post-processing with safe-divisions, short-track filter and linefit switched OFF - the exact
                    input the division stage sees; nodes (id,t,z,y,x, gap_synthetic) and edges (src,dst,edge_prob)
  dc/<stem>.npz     DeepCenter score (8-view TTA, as in the notebook) at every RAW node, keyed by node_id, so the
                    safe-division veto can be applied in pass 2 without frames
Everything is done through the notebook's own functions loaded by tools/public_local.py, so the checkpoint is
byte-for-byte what the shipped pipeline would hand to the division stage.

    python pass1_extras.py --stems A B C  [--tag exp29pp]
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stems", nargs="+", required=True); ap.add_argument("--tag", default="exp29pp")
    a = ap.parse_args()
    import public_local as pl
    cache = pl.DEFAULT_CACHE / a.tag; raw = cache / "raw"; work = cache / "work"; work.mkdir(parents=True, exist_ok=True)
    (cache / "ckpt").mkdir(exist_ok=True); (cache / "dc").mkdir(exist_ok=True)
    data_dir = pl.DEFAULT_DATA
    # division stage, short-track and linefit OFF -> checkpoint after gap closing (same switches as run_stage_table.sh)
    # prune-isolated also OFF: in the shipped order it runs AFTER the division stage, and an isolated node at t+1 is a
    # legitimate candidate daughter, so the checkpoint must keep it; pass 2 applies prune-isolated after divisions.
    for k, v in {"BIOHUB_OUTPUT_SAFE_DIVISIONS": "0", "BIOHUB_OUTPUT_FILTER_SHORT_TRACKS": "0", "BIOHUB_OUTPUT_LINEFIT_SMOOTH": "0",
                 "BIOHUB_OUTPUT_PRUNE_ISOLATED": "0"}.items():
        os.environ[k] = v
    cells = pl.notebook_cells(pl.DEFAULT_NOTEBOOK)
    repo, _ = pl.materialise_repo(Path(pl.DEFAULT_WEIGHTS_ROOT), work, None, None, materialise_code=False)
    ns = pl.build_namespace(cells, repo, work, data_dir)
    pl.load_postproc(cells, ns)
    if ns.get("DEEPCENTER_VETO_DETECTOR") is None:
        ns["DEEPCENTER_VETO_DETECTOR"] = ns["load_deepcenter_veto_detector"]()
    bundle = ns["DEEPCENTER_VETO_DETECTOR"]
    graph_from_geff = ns["graph_from_geff"]; filter_output_graph = ns["filter_output_graph"]
    heatmap_for_frame = ns["deepcenter_heatmap_for_frame"]
    WZ, WYX = ns["DEEPCENTER_SCORE_WIN_Z"], ns["DEEPCENTER_SCORE_WIN_YX"]
    pool = int(getattr(bundle["cfg"], "pool_factor", 4))

    for stem in a.stems:
        g = graph_from_geff(raw / f"{stem}.geff")
        nodes = {}
        for r in g.node_attrs().iter_rows(named=True):
            nodes[int(r["node_id"])] = {"node_id": int(r["node_id"]), "t": int(r["t"]), "z": float(r["z"]), "y": float(r["y"]), "x": float(r["x"])}
        edges = [{"source_id": int(r["source_id"]), "target_id": int(r["target_id"]),
                  "edge_prob": None if r.get("edge_prob") is None else float(r["edge_prob"])} for r in g.edge_attrs().iter_rows(named=True)]
        # --- DeepCenter score at every raw node (before the graph is mutated) ---
        by_t = {}
        for nid, n in nodes.items(): by_t.setdefault(n["t"], []).append(nid)
        frame_cache, hm_cache = {}, {}
        dc_ids, dc_vals = [], []
        for t in sorted(by_t):
            hm = heatmap_for_frame(stem, int(t), bundle, frame_cache, hm_cache)
            for nid in by_t[t]:
                n = nodes[nid]
                z = int(round(n["z"])); y = int(round(n["y"] / pool)); x = int(round(n["x"] / pool))
                patch = hm[max(0, z - WZ):z + WZ + 1, max(0, y - WYX):y + WYX + 1, max(0, x - WYX):x + WYX + 1]
                dc_ids.append(nid); dc_vals.append(float(patch.max()) if patch.size else -1.0)
            frame_cache.clear(); hm_cache.clear()
        np.savez_compressed(cache / "dc" / f"{stem}.npz", node_id=np.array(dc_ids), dc=np.array(dc_vals, np.float32))
        # --- checkpoint after gap closing ---
        nb, eb, stats = filter_output_graph(nodes, edges, dataset=stem, deepcenter_bundle=bundle)
        ids = np.array(sorted(nb)); arr = np.array([[nb[i]["t"], nb[i]["z"], nb[i]["y"], nb[i]["x"], int(nb[i].get("gap_synthetic", 0))] for i in ids], np.float32)
        src = np.array([e["source_id"] for e in eb]); dst = np.array([e["target_id"] for e in eb])
        prob = np.array([np.nan if e.get("edge_prob") is None else float(e["edge_prob"]) for e in eb], np.float32)
        np.savez_compressed(cache / "ckpt" / f"{stem}.npz", node_id=ids, tzyx_syn=arr, src=src, dst=dst, edge_prob=prob,
                            stats=json.dumps({k: int(v) for k, v in stats.items()}))
        print(f"{stem}: raw {len(nodes)} nodes -> ckpt {len(nb)} nodes / {len(eb)} edges; dc scores {len(dc_ids)}", flush=True)


if __name__ == "__main__":
    main()
