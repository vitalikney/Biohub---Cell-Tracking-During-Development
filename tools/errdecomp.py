"""Error decomposition of prediction graphs vs GT: detection misses, fragmentation, wrong association (per video)."""
import sys, os
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import postproc, divranker

def decompose(geff_dir: Path, gt_dir: Path):
    rows = []
    for p in sorted(Path(geff_dir).glob("*.geff")):
        g = postproc.load(p); gt = divranker._load_gt(gt_dir / p.name)
        m = divranker._match_pred_to_gt(g, gt); inv = {v: k for k, v in m.items()}
        gt_edges = list(gt.edges()); pred_edges = set(g.edges())
        missed_nodes = sum(1 for n in gt.nodes if n not in inv)
        lost_det = frag = rec = 0
        for a, b in gt_edges:
            pa, pb = inv.get(a), inv.get(b)
            if pa is None or pb is None: lost_det += 1
            elif (pa, pb) in pred_edges: rec += 1
            else: frag += 1
        # wrong association: predicted edge whose endpoints both match GT nodes but is not a GT edge
        gt_edge_set = set(gt_edges); wrong = 0
        for u, v in pred_edges:
            gu, gv = m.get(u), m.get(v)
            if gu is not None and gv is not None and (gu, gv) not in gt_edge_set: wrong += 1
        # fragmentation detail: for fragmented edges, does pa have any successor / pb any predecessor?
        frag_pa_no_succ = frag_pb_no_pred = frag_both_linked_elsewhere = 0
        for a, b in gt_edges:
            pa, pb = inv.get(a), inv.get(b)
            if pa is None or pb is None or (pa, pb) in pred_edges: continue
            s = g.out_degree(pa) == 0; t = g.in_degree(pb) == 0
            if s and t: frag_pa_no_succ += 0  # counted below
            if s: frag_pa_no_succ += 1
            if t: frag_pb_no_pred += 1
            if not s and not t: frag_both_linked_elsewhere += 1
        rows.append(dict(video=p.stem, gt_nodes=gt.number_of_nodes(), missed_nodes=missed_nodes, gt_edges=len(gt_edges),
                         recovered=rec, lost_to_detection=lost_det, fragmented=frag, wrong_assoc=wrong,
                         frag_src_no_succ=frag_pa_no_succ, frag_tgt_no_pred=frag_pb_no_pred, frag_both_linked_elsewhere=frag_both_linked_elsewhere))
    return rows

if __name__ == "__main__":
    import pandas as pd
    rows = decompose(Path(sys.argv[1]), Path(sys.argv[2]))
    df = pd.DataFrame(rows); pd.set_option("display.width", 250)
    print(df.to_string(index=False))
    tot = df.drop(columns="video").sum(); ge = tot.gt_edges
    print(f"\nTOTAL gt_edges={ge} recovered={tot.recovered/ge:.3f} lost_to_detection={tot.lost_to_detection/ge:.3f} fragmented={tot.fragmented/ge:.3f} wrong_assoc={tot.wrong_assoc} | missed_nodes={tot.missed_nodes/tot.gt_nodes:.3f}")
    print(f"fragmented split: src_no_succ={tot.frag_src_no_succ} tgt_no_pred={tot.frag_tgt_no_pred} both_linked_elsewhere={tot.frag_both_linked_elsewhere}")
