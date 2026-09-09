import sys, pandas as pd, networkx as nx
from pathlib import Path
sys.path.insert(0, "tools"); import postproc
csv, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
d = pd.read_csv(csv)
for ds, sub in d.groupby("dataset"):
    g = nx.DiGraph()
    nodes = sub[sub.row_type == "node"]
    for r in nodes.itertuples():
        g.add_node(int(r.node_id), t=int(r.t), z=float(r.z), y=float(r.y), x=float(r.x))
    edges = sub[sub.row_type == "edge"]
    g.add_edges_from(zip(edges.source_id.astype(int), edges.target_id.astype(int)))
    postproc.save(g, out / f"{ds}.geff")
    print(ds, g.number_of_nodes(), g.number_of_edges())
