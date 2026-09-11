"""Reproduce the division base rates on OUR full training set, from GT geffs only."""
import os, sys, warnings, glob
warnings.filterwarnings("ignore")
ROOT = "tools/official"
sys.path.insert(0, ROOT + "/src"); sys.path.insert(0, ROOT + "/scripts")
from pathlib import Path
import numpy as np, tracksdata as td
DATA = Path("biohub-cell-tracking-during-development/train")
SCALE = np.array([1.625, 0.40625, 0.40625])

cont, divstep, sister, par_to_each = [], [], [], []
nvid = ndiv = 0
for g in sorted(DATA.glob("*.geff")):
    try:
        pr = td.graph.IndexedRXGraph.from_geff(g)
        gr = pr[0] if isinstance(pr, tuple) else pr
    except Exception:
        continue
    nvid += 1
    na = gr.node_attrs().to_pandas().set_index("node_id")
    pos = {int(i): np.array([r.z, r.y, r.x]) * SCALE for i, r in na.iterrows()}
    tt = {int(i): int(r.t) for i, r in na.iterrows()}
    out = {}
    for s, d in gr.edge_list():
        out.setdefault(int(s), []).append(int(d))
    for s, ch in out.items():
        if len(ch) == 1:
            cont.append(float(np.linalg.norm(pos[s] - pos[ch[0]])))
        elif len(ch) == 2:
            ndiv += 1
            d0, d1 = ch
            a = float(np.linalg.norm(pos[s] - pos[d0])); b = float(np.linalg.norm(pos[s] - pos[d1]))
            divstep += [a, b]; par_to_each.append((min(a, b), max(a, b)))
            sister.append(float(np.linalg.norm(pos[d0] - pos[d1])))

def q(v, name):
    v = np.array(v)
    print(f"{name:22} n={len(v):6d} median={np.median(v):6.3f} p25={np.percentile(v,25):6.3f} "
          f"p75={np.percentile(v,75):6.3f} p90={np.percentile(v,90):6.3f} p99={np.percentile(v,99):6.3f} max={v.max():6.3f}")

print(f"videos={nvid} divisions={ndiv}")
q(cont, "continuation step"); q(divstep, "division step"); q(sister, "sister separation")
pe = np.array(par_to_each)
if len(pe):
    sym = np.abs(pe[:,1]-pe[:,0]) / np.maximum((pe[:,0]+pe[:,1])/2, 1e-6)
    q(sym, "GT symmetry ratio")
    print(f"   fraction of GT divisions REJECTED by the public symmetry gate (tau=0.6): {(sym>0.6).mean():.3f}")
    print(f"   fraction with max parent-daughter dist > 9.0 um (public SAFE_DIV_MAX_UM): {(pe[:,1]>9.0).mean():.3f}")
s = np.array(sister); c = np.array(cont)
print("\nMINIMUM sister separation: what a lower bound would cost and save")
print(f"{'min_sister':>10} {'GT div kept':>12} {'continuations above it':>24}")
for thr in [0, 4, 5, 6, 7, 8, 9]:
    print(f"{thr:>10} {(s>=thr).mean():>12.3f} {(c>=thr).mean():>24.5f}")
